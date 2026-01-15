import joblib
import numpy as np
import pandas as pd
from django.conf import settings
from observations.models import ObservationSet

_model_bundle = None  # can be a pipeline OR a dict with {"pipeline":..., "features":[...]}

def get_model_bundle():
    global _model_bundle
    if _model_bundle is None:
        _model_bundle = joblib.load(settings.ML_MODEL_PATH)
    return _model_bundle


def _bundle_to_pipeline_and_features(bundle):
    """
    Supports either:
      - bundle = sklearn pipeline/model
      - bundle = {"pipeline": pipeline, "features": [col1, col2, ...]}
    """
    if isinstance(bundle, dict) and "pipeline" in bundle:
        pipeline = bundle["pipeline"]
        features = bundle.get("features")
        return pipeline, features
    return bundle, None


def predict_180d_mortality(obs: ObservationSet) -> float:
    """
    Returns probability (0..1) of 180-day mortality for a given ObservationSet.
    """
    bundle = get_model_bundle()
    pipeline, trained_features = _bundle_to_pipeline_and_features(bundle)

    # Prefer the feature list saved during training (prevents mismatch).
    # Fallback to ObservationSet.feature_columns().
    cols = trained_features or ObservationSet.feature_columns()

    # Convert None -> np.nan so the pipeline imputer can handle it
    row = {c: (getattr(obs, c) if getattr(obs, c) is not None else np.nan) for c in cols}

    # Use DataFrame to preserve column names/order
    X = pd.DataFrame([row], columns=cols)

    proba = pipeline.predict_proba(X)[0][1]
    return float(proba)


def risk_band_for_probability(p: float) -> str:
    thr_low = settings.RISK_BAND_THRESHOLDS.get("LOW", 0.30)
    thr_med = settings.RISK_BAND_THRESHOLDS.get("MEDIUM", 0.70)

    if p >= thr_med:
        return "HIGH"
    if p >= thr_low:
        return "MEDIUM"
    return "LOW"
