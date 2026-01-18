import joblib
import numpy as np
import pandas as pd
import shap
from django.conf import settings

from observations.models import ObservationSet

_model_bundle = None

_tree_explainer = None          # cached TreeExplainer
_tree_explainer_bg_sig = None   # signature of background used for explainer
_cached_bg = None               # cached background in RAW feature space


def get_model_bundle():
    global _model_bundle
    if _model_bundle is None:
        _model_bundle = joblib.load(settings.ML_MODEL_PATH)
    return _model_bundle


def _bundle_to_pipeline_and_features(bundle):
    if isinstance(bundle, dict) and "pipeline" in bundle:
        pipeline = bundle["pipeline"]
        features = bundle.get("features") or bundle.get("feature_cols")
        return pipeline, features
    return bundle, None


def _safe_get(obs: ObservationSet, col: str):
    if hasattr(obs, col):
        v = getattr(obs, col)
        return v if v is not None else np.nan
    return np.nan


def _build_X(obs: ObservationSet, cols):
    row = {c: _safe_get(obs, c) for c in cols}
    X = pd.DataFrame([row], columns=cols)
    return X, row


# -------------------------------------------------------------------
# ✅ BACKGROUND LOADED FROM THE SAME MODEL FILE (single joblib)
# -------------------------------------------------------------------

def _get_background_from_bundle(cols) -> pd.DataFrame:
    """
    Loads SHAP background from the model bundle (settings.ML_MODEL_PATH),
    so you only deploy ONE file: XGBoost_mortality_180days.joblib

    The model joblib must contain:
        {
          "pipeline": ...,
          "feature_cols": [...],
          "shap_background": <DataFrame or ndarray>
        }
    """
    global _cached_bg

    if _cached_bg is not None:
        return _cached_bg.reindex(columns=cols)

    bundle = get_model_bundle()
    bg_loaded = None

    if isinstance(bundle, dict):
        bg_loaded = bundle.get("shap_background")

    if bg_loaded is None:
        raise RuntimeError(
            "This model file does not contain 'shap_background'. "
            "Retrain/export the model with shap_background embedded into the same joblib."
        )

    # Convert to DataFrame
    if isinstance(bg_loaded, pd.DataFrame):
        bg = bg_loaded.copy()
    else:
        arr = np.asarray(bg_loaded, dtype=float)
        if arr.ndim == 1:
            arr = arr.reshape(1, -1)
        bg = pd.DataFrame(arr, columns=cols if arr.shape[1] == len(cols) else None)

    # Align columns/order safely
    if isinstance(bg, pd.DataFrame):
        if bg.shape[1] != len(cols):
            # try best-effort alignment by truncation
            bg = bg.iloc[:, :len(cols)]
        bg.columns = cols
        bg = bg.reindex(columns=cols)

    # Ensure numeric
    for c in cols:
        bg[c] = pd.to_numeric(bg[c], errors="coerce")

    _cached_bg = bg
    return bg


def _get_xgb_model(pipeline):
    if hasattr(pipeline, "steps"):
        return pipeline.steps[-1][1]
    return pipeline


def _get_preprocessor(pipeline):
    if hasattr(pipeline, "steps") and len(pipeline.steps) > 1:
        return pipeline[:-1]
    return None


def _background_signature(X_bg_t) -> str:
    try:
        arr = np.asarray(X_bg_t)
        return f"{arr.shape}-{float(np.nanmean(arr)):.8f}-{float(np.nanstd(arr)):.8f}"
    except Exception:
        return "unknown"


def _get_tree_explainer(pipeline, X_bg_transformed):
    global _tree_explainer, _tree_explainer_bg_sig

    sig = _background_signature(X_bg_transformed)
    if _tree_explainer is not None and _tree_explainer_bg_sig == sig:
        return _tree_explainer

    model = _get_xgb_model(pipeline)
    _tree_explainer = shap.TreeExplainer(model, data=X_bg_transformed)
    _tree_explainer_bg_sig = sig
    return _tree_explainer


def predict_180d_mortality(obs: ObservationSet) -> float:
    bundle = get_model_bundle()
    pipeline, trained_features = _bundle_to_pipeline_and_features(bundle)
    cols = trained_features or ObservationSet.feature_columns()

    X, _ = _build_X(obs, cols)
    proba = pipeline.predict_proba(X)[0][1]
    return float(proba)


def predict_180d_mortality_with_shap(obs: ObservationSet, top_n: int = 10):
    """
    Returns:
      proba: float (0..1)
      shap_items: list[dict] sorted by |shap_value| desc

    Note: Your pipeline is (SimpleImputer + XGBoost), so transformed features
    match raw features (no one-hot expansion).
    """
    bundle = get_model_bundle()
    pipeline, trained_features = _bundle_to_pipeline_and_features(bundle)
    cols = trained_features or ObservationSet.feature_columns()

    X, row = _build_X(obs, cols)

    # probability (pipeline handles preprocessing)
    proba = float(pipeline.predict_proba(X)[0][1])

    pre = _get_preprocessor(pipeline)

    # ✅ Background from same model joblib
    X_bg = _get_background_from_bundle(cols)

    if pre is not None:
        X_t = pre.transform(X)
        X_bg_t = pre.transform(X_bg)
    else:
        X_t = X.values
        X_bg_t = X_bg.values

    explainer = _get_tree_explainer(pipeline, X_bg_transformed=X_bg_t)

    shap_vals = explainer.shap_values(X_t)

    # binary classifier sometimes returns list [class0, class1]
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

    # Hide missing user inputs (NaN)
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
