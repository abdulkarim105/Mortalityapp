import joblib
import numpy as np
import pandas as pd
import shap
from django.conf import settings

from observations.models import ObservationSet

_model_bundle = None
_tree_explainer = None  # cached TreeExplainer


def get_model_bundle():
    global _model_bundle
    if _model_bundle is None:
        _model_bundle = joblib.load(settings.ML_MODEL_PATH)
    return _model_bundle


def _bundle_to_pipeline_and_features(bundle):
    """
    Supports either:
      - bundle = sklearn pipeline/model
      - bundle = {"pipeline": pipeline, "features": [...]}
      - bundle = {"pipeline": pipeline, "feature_cols": [...]} (backward compatible)
    """
    if isinstance(bundle, dict) and "pipeline" in bundle:
        pipeline = bundle["pipeline"]
        features = bundle.get("features") or bundle.get("feature_cols")
        return pipeline, features
    return bundle, None


def _safe_get(obs: ObservationSet, col: str):
    """
    Read feature safely. If the field doesn't exist or is None -> np.nan
    """
    if hasattr(obs, col):
        v = getattr(obs, col)
        return v if v is not None else np.nan
    return np.nan


def _build_X(obs: ObservationSet, cols):
    row = {c: _safe_get(obs, c) for c in cols}
    X = pd.DataFrame([row], columns=cols)
    return X, row


def _get_background_X(cols, n_rows: int = 50) -> pd.DataFrame:
    """
    Build a small background dataset from recent ObservationSet rows.
    This stabilizes SHAP and prevents all-zero explanations.
    """
    qs = ObservationSet.objects.order_by("-recorded_at")[:n_rows]
    rows = []
    for o in qs:
        rows.append({c: _safe_get(o, c) for c in cols})

    if not rows:
        # if DB empty, fallback to one NaN row (still works, but less informative)
        rows = [{c: np.nan for c in cols}]

    return pd.DataFrame(rows, columns=cols)


def predict_180d_mortality(obs: ObservationSet) -> float:
    """
    Returns probability (0..1) of 180-day mortality for a given ObservationSet.
    """
    bundle = get_model_bundle()
    pipeline, trained_features = _bundle_to_pipeline_and_features(bundle)
    cols = trained_features or ObservationSet.feature_columns()

    X, _ = _build_X(obs, cols)
    proba = pipeline.predict_proba(X)[0][1]
    return float(proba)


def _get_xgb_model(pipeline):
    # sklearn Pipeline -> last step is the model
    if hasattr(pipeline, "steps"):
        return pipeline.steps[-1][1]
    return pipeline


def _get_preprocessor(pipeline):
    # everything before the model (imputer, scaler, etc.)
    if hasattr(pipeline, "steps") and len(pipeline.steps) > 1:
        return pipeline[:-1]
    return None


def _get_tree_explainer(pipeline, X_bg_transformed):
    """
    Cache TreeExplainer on the XGBoost model.
    Provide background in transformed feature space if possible.
    """
    global _tree_explainer
    if _tree_explainer is not None:
        return _tree_explainer

    model = _get_xgb_model(pipeline)

    # TreeExplainer is the right one for XGBoost
    _tree_explainer = shap.TreeExplainer(model, data=X_bg_transformed)
    return _tree_explainer


def predict_180d_mortality_with_shap(obs: ObservationSet, top_n: int = 10):
    """
    Returns:
      proba: float (0..1)
      shap_items: list[dict] sorted by |shap_value| desc (top contributors first)
      (Missing user inputs are HIDDEN from shap_items)
    """
    bundle = get_model_bundle()
    pipeline, trained_features = _bundle_to_pipeline_and_features(bundle)
    cols = trained_features or ObservationSet.feature_columns()

    X, row = _build_X(obs, cols)

    # probability (pipeline handles imputation etc.)
    proba = float(pipeline.predict_proba(X)[0][1])

    # Prepare transformed inputs for SHAP
    pre = _get_preprocessor(pipeline)
    if pre is not None:
        X_t = pre.transform(X)
        X_bg = _get_background_X(cols, n_rows=50)
        X_bg_t = pre.transform(X_bg)
    else:
        X_t = X.values
        X_bg_t = _get_background_X(cols, n_rows=50).values

    explainer = _get_tree_explainer(pipeline, X_bg_transformed=X_bg_t)

    # Compute SHAP for one row
    shap_vals = explainer.shap_values(X_t)

    # XGBoost binary classifier usually returns (n_rows, n_features)
    # Sometimes it returns list -> pick positive class [1]
    if isinstance(shap_vals, list):
        shap_row = shap_vals[1][0]
    else:
        shap_row = shap_vals[0]

    shap_items = []
    for i, feat in enumerate(cols):
        value = row.get(feat)
        sv = float(shap_row[i])
        shap_items.append({
            "feature": feat,
            "value": value,
            "shap_value": sv,
            "direction": "up" if sv > 0 else "down" if sv < 0 else "flat",
        })

    # ✅ Hide features the user did not enter (value is NaN)
    shap_items = [d for d in shap_items if not pd.isna(d["value"])]

    shap_items.sort(key=lambda d: abs(d["shap_value"]), reverse=True)
    if top_n is not None:
        shap_items = shap_items[:top_n]

    return proba, shap_items


def risk_band_for_probability(p: float) -> str:
    thr_low = settings.RISK_BAND_THRESHOLDS.get("LOW", 0.30)
    thr_med = settings.RISK_BAND_THRESHOLDS.get("MEDIUM", 0.70)

    if p >= thr_med:
        return "HIGH"
    if p >= thr_low:
        return "MEDIUM"
    return "LOW"
