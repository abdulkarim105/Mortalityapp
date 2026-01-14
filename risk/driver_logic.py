from observations.models import ObservationSet
from .clinical_ranges import NORMAL_RANGES, DRIVER_FEATURES


def _severity_icon(severity: str) -> str:
    # Red for extreme values, Yellow for normal-abnormal values
    if severity in ("TOO HIGH", "TOO LOW"):
        return "🔴"
    return "🟡"


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

    TOO_THRESHOLD = 0.50  # how far from normal to become "TOO HIGH / TOO LOW"

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

        # Only abnormal values
        if low <= v <= high:
            continue

        width = (high - low) if (high - low) != 0 else 1.0

        if v < low:
            delta = low - v
            arrow = "↓"
            score = delta / width
            severity = "TOO LOW" if score >= TOO_THRESHOLD else "LOW"
        else:
            delta = v - high
            arrow = "↑"
            score = delta / width
            severity = "TOO HIGH" if score >= TOO_THRESHOLD else "HIGH"

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

    # Count only extreme ones
    high_count = sum(1 for x in items if x["severity"] in ("TOO HIGH", "TOO LOW"))
    total_abnormal = len(items)

    if show_all:
        shown = items
    else:
        max_items = 5 if high_count > 3 else 3
        shown = items[:max_items]

    return shown, len(shown), high_count, total_abnormal
