import os
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
# ✅ FIXED SHAP BACKGROUND (stable across PyCharm + Render)
# -------------------------------------------------------------------

def _get_fixed_background_X(cols) -> pd.DataFrame:
    """
    Loads a FIXED background dataset from disk so SHAP is consistent.
    Expected location (recommended):
        risk/ml_models/shap_background.joblib

    settings.py should contain:
        SHAP_BACKGROUND_PATH = BASE_DIR / "risk" / "ml_models" / "shap_background.joblib"

    The joblib may store:
      - a pandas DataFrame (best), or
      - a numpy array shaped (n_rows, n_features)
    """
    global _cached_bg

    if not hasattr(settings, "SHAP_BACKGROUND_PATH"):
        raise RuntimeError(
            "Missing settings.SHAP_BACKGROUND_PATH. "
            "Add SHAP_BACKGROUND_PATH to settings.py."
        )

    path = str(settings.SHAP_BACKGROUND_PATH)
    if not os.path.exists(path):
        raise RuntimeError(
            f"SHAP background file not found: {path}. "
            "Create and deploy shap_background.joblib (same file in local + Render)."
        )

    if _cached_bg is None:
        bg_loaded = joblib.load(path)

        if isinstance(bg_loaded, pd.DataFrame):
            bg = bg_loaded.copy()
        else:
            arr = np.asarray(bg_loaded, dtype=float)
            if arr.ndim == 1:
                arr = arr.reshape(1, -1)
            bg = pd.DataFrame(arr)

        _cached_bg = bg

    # ensure exact columns + order
    bg = _cached_bg.copy()
    if isinstance(bg, pd.DataFrame):
        # If DF has named columns, align by name; otherwise force by position
        if list(bg.columns) != list(cols):
            # try name-align
            try:
                bg = bg.reindex(columns=cols)
            except Exception:
                # fallback: overwrite columns by position
                bg = bg.iloc[:, : len(cols)]
                bg.columns = cols
        else:
            bg = bg[cols]

    # ensure float dtype
    for c in cols:
        if c in bg.columns:
            bg[c] = pd.to_numeric(bg[c], errors="coerce")

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
    """
    Build a simple signature so we don't reuse an explainer with a different background.
    """
    try:
        arr = np.asarray(X_bg_t)
        return f"{arr.shape}-{float(np.nanmean(arr)):.8f}-{float(np.nanstd(arr)):.8f}"
    except Exception:
        return "unknown"


def _get_tree_explainer(pipeline, X_bg_transformed):
    """
    Cache TreeExplainer on the model using FIXED background.
    Cache is invalidated if background signature changes.
    """
    global _tree_explainer, _tree_explainer_bg_sig

    sig = _background_signature(X_bg_transformed)
    if _tree_explainer is not None and _tree_explainer_bg_sig == sig:
        return _tree_explainer

    model = _get_xgb_model(pipeline)
    _tree_explainer = shap.TreeExplainer(model, data=X_bg_transformed)
    _tree_explainer_bg_sig = sig
    return _tree_explainer


def _get_transformed_feature_names(preprocessor, raw_cols):
    """
    If preprocessor supports get_feature_names_out, use it.
    Otherwise fallback to raw column names.
    """
    if preprocessor is None:
        return list(raw_cols)

    # sklearn >= 1.0 usually supports this for ColumnTransformer/OneHotEncoder pipelines
    if hasattr(preprocessor, "get_feature_names_out"):
        try:
            names = preprocessor.get_feature_names_out(raw_cols)
            return [str(n) for n in names]
        except Exception:
            pass

    # fallback
    return list(raw_cols)


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

    IMPORTANT:
      - If your preprocessor expands columns (one-hot), SHAP values will be returned
        in transformed-feature space. We label them using get_feature_names_out().
      - If your preprocessor does NOT expand columns (imputer/scaler only),
        then transformed features match raw cols and you’ll see the original names.
    """
    bundle = get_model_bundle()
    pipeline, trained_features = _bundle_to_pipeline_and_features(bundle)
    raw_cols = trained_features or ObservationSet.feature_columns()

    X, row = _build_X(obs, raw_cols)

    # probability (pipeline handles preprocessing)
    proba = float(pipeline.predict_proba(X)[0][1])

    pre = _get_preprocessor(pipeline)

    # ✅ fixed background from disk
    X_bg = _get_fixed_background_X(raw_cols)

    if pre is not None:
        X_t = pre.transform(X)
        X_bg_t = pre.transform(X_bg)
        feat_names = _get_transformed_feature_names(pre, raw_cols)
    else:
        X_t = X.values
        X_bg_t = X_bg.values
        feat_names = list(raw_cols)

    explainer = _get_tree_explainer(pipeline, X_bg_transformed=X_bg_t)

    shap_vals = explainer.shap_values(X_t)

    # binary classifier sometimes returns list [class0, class1]
    if isinstance(shap_vals, list):
        shap_row = shap_vals[1][0]
    else:
        shap_row = shap_vals[0]

    # Build items in transformed space
    shap_items = []
    for i, feat in enumerate(feat_names):
        sv = float(shap_row[i])
        shap_items.append({
            "feature": feat,
            "value": None,  # transformed feature value not always meaningful/available
            "shap_value": sv,
            "direction": "up" if sv > 0 else "down" if sv < 0 else "flat",
        })

    # If preprocessor does NOT expand columns, map raw values too
    if pre is None or len(feat_names) == len(raw_cols):
        for i, feat in enumerate(raw_cols):
            shap_items[i]["value"] = row.get(feat)

        # Hide missing user inputs (NaN) only when we have raw values
        shap_items = [d for d in shap_items if d["value"] is None or not pd.isna(d["value"])]

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
