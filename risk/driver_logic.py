from observations.models import ObservationSet
from .clinical_ranges import NORMAL_RANGES, DRIVER_FEATURES


def _severity_icon(severity: str) -> str:
    # Red for extreme values, Yellow for abnormal-but-not-extreme values
    return "🔴" if severity in ("TOO HIGH", "TOO LOW") else "🟡"


# Default threshold if a feature is not listed below
DEFAULT_TOO_THRESHOLD = 0.40

# Per-feature thresholds (tune as needed)
TOO_THRESHOLDS = {
    # Neuro
    "GCS_mean": 0.25,
    "GCS_max": 0.25,

    # Shock / perfusion
    "SYSBP_mean": 0.35,
    "SYSBP_min": 0.35,
    "MEANBP_mean": 0.35,
    "MEANBP_min": 0.35,

    # Lactate
    "Lactate_mean": 0.50,
    "Lactate_max": 0.50,
    "Lactate_min": 0.50,

    # Renal
    "BUN_mean": 0.55,
    "BUN_min": 0.55,
    "BUN_max": 0.55,

    # Liver
    "Bilirubin_mean": 0.55,
    "Bilirubin_max": 0.55,

    # Resp
    "RR_mean": 0.50,
    "RR_min": 0.50,
    "RR_max": 0.50,

    # Temp
    "TEMP_min": 0.60,
    "TEMP_std": 0.60,

    # HR
    "HR_mean": 0.55,
    "HR_max": 0.55,
    "HR_std": 0.60,

    # Anion gap
    "AG_mean": 0.55,
    "AG_min": 0.55,
    "AG_max": 0.55,
    "AG_std": 0.60,

    # RDW (often chronic marker; make less sensitive)
    "RDW_mean": 0.75,
    "RDW_min": 0.75,
    "RDW_max": 0.75,
    "RDW_std": 0.75,

    # Demographics / score (usually not “too” clinically in same way)
    "age": 0.90,
    "age_adj_comorbidity_score": 0.90,

    # Optional extras if you add them to DRIVER_FEATURES later
    "SYSBP_std": 0.60,
    "DIASBP_mean": 0.60,
    "DIASBP_min": 0.60,
}


def _get_too_threshold(feature_name: str) -> float:
    # Exact match
    if feature_name in TOO_THRESHOLDS:
        return TOO_THRESHOLDS[feature_name]

    # Case-insensitive fallback (handles SYSBP_mean vs SYSBP_MEAN etc.)
    fn = feature_name.lower()
    for k, v in TOO_THRESHOLDS.items():
        if k.lower() == fn:
            return v

    return DEFAULT_TOO_THRESHOLD


def build_clinical_drivers(obs: ObservationSet, show_all: bool = False):
    """
    Severity rules:
    - LOW       → slightly below normal  (yellow)
    - HIGH      → slightly above normal  (yellow)
    - TOO LOW   → far below normal       (red)
    - TOO HIGH  → far above normal       (red)

    If show_all=False:
      - if >3 TOO severity drivers -> return top 5
      - else -> return top 3

    If show_all=True:
      - return all abnormal drivers

    Returns: (drivers, shown_count, high_count, total_abnormal)
    """
    items = []

    for col in DRIVER_FEATURES:
        rng = NORMAL_RANGES.get(col)
        if not rng:
            continue

        low, high, unit, label = rng

        # IMPORTANT: use hasattr/getattr safely
        val = getattr(obs, col, None)
        if val is None:
            continue

        try:
            v = float(val)
        except (TypeError, ValueError):
            continue

        # Only abnormal values
        if low <= v <= high:
            continue

        width = (high - low) if (high - low) != 0 else 1.0
        too_thr = _get_too_threshold(col)

        if v < low:
            score = (low - v) / width
            arrow = "↓"
            severity = "TOO LOW" if score >= too_thr else "LOW"
        else:
            score = (v - high) / width
            arrow = "↑"
            severity = "TOO HIGH" if score >= too_thr else "HIGH"

        icon = _severity_icon(severity)

        v_str = f"{v:.2f}".rstrip("0").rstrip(".")
        unit_str = f" {unit}" if unit else ""
        text = f"{label}: {v_str}{unit_str} (normal {low}–{high}) {arrow}"

        items.append(
            {
                "col": col,
                "text": text,
                "severity": severity,
                "icon": icon,
                "score": float(score),
                "threshold": float(too_thr),  # optional debugging
            }
        )

    # Sort most abnormal first
    items.sort(key=lambda x: x["score"], reverse=True)

    # Count only extreme ones
    high_count = sum(1 for x in items if x["severity"] in ("TOO HIGH", "TOO LOW"))
    total_abnormal = len(items)

    if show_all:
        shown = items
    else:
        max_items = 5 if high_count > 3 else 3
        shown = items[:max_items]

    return shown, len(shown), high_count, total_abnormal
