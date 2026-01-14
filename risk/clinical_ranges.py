# risk/clinical_ranges.py
# column_name: (low, high, unit, label)
NORMAL_RANGES = {
    "HR_MEAN": (60, 100, "bpm", "Mean heart rate"),
    "HR_MAX": (60, 140, "bpm", "Max heart rate"),
    "RR_MEAN": (12, 20, "breaths/min", "Mean respiratory rate"),
    "TEMP_MIN": (36.5, 37.5, "°C", "Minimum temperature"),
    "SYSBP_MEAN": (90, 140, "mmHg", "Mean systolic BP"),
    "DIASBP_MEAN": (60, 90, "mmHg", "Mean diastolic BP"),
    "MEANBP_MEAN": (65, 105, "mmHg", "Mean arterial pressure (MAP)"),
    "Lactate_mean": (0.5, 2.0, "mmol/L", "Mean lactate"),
    "BUN_mean": (7, 20, "mg/dL", "Mean BUN"),
    "Bilirubin_mean": (0.2, 1.2, "mg/dL", "Mean bilirubin"),
    "GCS_mean": (13, 15, "", "Mean GCS"),
    "RDW_mean": (11.5, 14.5, "%", "Mean RDW"),
    "AG_MEAN": (8, 16, "mEq/L", "Mean anion gap"),
}

# Keep this short and clinically focused
DRIVER_FEATURES = [
    "HR_MEAN",
    "TEMP_MIN",
    "RR_MEAN",
    "SYSBP_MEAN",
    "MEANBP_MEAN",
    "Lactate_mean",
    "BUN_mean",
    "Bilirubin_mean",
    "GCS_mean",
    "AG_MEAN",
    "RDW_mean",
]
