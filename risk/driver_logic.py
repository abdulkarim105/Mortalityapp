# risk/driver_logic.py
from observations.models import ObservationSet
from .clinical_ranges import NORMAL_RANGES, DRIVER_FEATURES

def _severity_icon(severity: str) -> str:
    return "🔴" if severity == "HIGH" else "🟡"

def build_clinical_drivers(obs: ObservationSet, show_all: bool = False):
    """
    If show_all=False:
      - if >3 HIGH severity drivers -> return top 5
      - else -> return top 3

    If show_all=True:
      - return all abnormal drivers

    Returns: (drivers, shown_count, high_count, total_abnormal)
    drivers: list of dicts with keys: text, severity, icon, score, col
    """
    items = []

    for col in DRIVER_FEATURES:
        if col not in NORMAL_RANGES:
            continue

        low, high, unit, label = NORMAL_RANGES[col]
        val = getattr(obs, col, None)
        if val is None:
            continue

        try:
            v = float(val)
        except (TypeError, ValueError):
            continue

        # abnormal only
        if low <= v <= high:
            continue

        width = (high - low) if (high - low) != 0 else 1.0

        if v < low:
            delta = low - v
            arrow = "↓"
        else:
            delta = v - high
            arrow = "↑"

        score = delta / width

        # severity cutoffs (tunable)
        severity = "HIGH" if score >= 0.50 else "MILD"
        icon = _severity_icon(severity)

        v_str = f"{v:.2f}".rstrip("0").rstrip(".")
        unit_str = f" {unit}" if unit else ""
        text = f"{label}: {v_str}{unit_str} (normal {low}–{high}) {arrow}"

        items.append({
            "col": col,
            "text": text,
            "severity": severity,
            "icon": icon,
            "score": score,
        })

    # Sort most abnormal first
    items.sort(key=lambda x: x["score"], reverse=True)

    high_count = sum(1 for x in items if x["severity"] == "HIGH")
    total_abnormal = len(items)

    if show_all:
        shown = items
    else:
        max_items = 5 if high_count > 3 else 3
        shown = items[:max_items]

    return shown, len(shown), high_count, total_abnormal
