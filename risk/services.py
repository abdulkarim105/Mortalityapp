import joblib
import numpy as np
from django.conf import settings
from observations.models import ObservationSet

_model = None

def get_model():
    global _model
    if _model is None:
        _model = joblib.load(settings.ML_MODEL_PATH)
    return _model


def predict_180d_mortality(obs: ObservationSet) -> float:
    """
    Returns probability (0..1) of 180-day mortality for a given ObservationSet.
    """
    model = get_model()

    cols = ObservationSet.feature_columns()
    row = [getattr(obs, c) for c in cols]
    X = np.array([row], dtype=float)

    # supports sklearn pipelines or xgb models that expose predict_proba
    proba = model.predict_proba(X)[0][1]
    return float(proba)


def risk_band_for_probability(p: float) -> str:
    """
    Convert probability (0..1) into LOW / MEDIUM / HIGH using settings thresholds.
    """
    thr_low = settings.RISK_BAND_THRESHOLDS.get("LOW", 0.10)
    thr_med = settings.RISK_BAND_THRESHOLDS.get("MEDIUM", 0.30)

    if p >= thr_med:
        return "HIGH"
    if p >= thr_low:
        return "MEDIUM"
    return "LOW"
