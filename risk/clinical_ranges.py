# risk/clinical_ranges.py
# column_name: (low, high, unit, label)

NORMAL_RANGES = {
    # GCS
    "GCS_max": (15, 15, "", "Maximum Glasgow Coma Scale"),
    "GCS_mean": (13, 15, "", "Mean Glasgow Coma Scale"),

    # Lactate (mmol/L)
    "Lactate_min": (0.5, 1.0, "mmol/L", "Minimum lactate"),
    "Lactate_max": (2.0, 4.0, "mmol/L", "Maximum lactate"),
    "Lactate_mean": (0.5, 2.0, "mmol/L", "Mean lactate"),

    # BUN (mg/dL)
    "BUN_min": (7, 10, "mg/dL", "Minimum BUN"),
    "BUN_mean": (7, 20, "mg/dL", "Mean BUN"),

    # Bilirubin (mg/dL)
    "Bilirubin_max": (1.2, 3.0, "mg/dL", "Maximum bilirubin"),
    "Bilirubin_mean": (0.2, 1.2, "mg/dL", "Mean bilirubin"),

    # Anion Gap (mEq/L)
    "AG_MEAN": (8, 16, "mEq/L", "Mean anion gap"),
    "AG_MAX": (16, 25, "mEq/L", "Maximum anion gap"),
    "AG_MIN": (6, 8, "mEq/L", "Minimum anion gap"),
    "AG_STD": (0, 6, "mEq/L", "Anion gap variability"),

    # Systolic BP (mmHg)
    "SYSBP_MIN": (90, 100, "mmHg", "Minimum systolic BP"),
    "SYSBP_MEAN": (90, 140, "mmHg", "Mean systolic BP"),
    "SYSBP_STD": (0, 25, "mmHg", "Systolic BP variability"),

    # Diastolic BP (mmHg)
    "DIASBP_MIN": (60, 70, "mmHg", "Minimum diastolic BP"),
    "DIASBP_MEAN": (60, 90, "mmHg", "Mean diastolic BP"),

    # Age
    "AGE": (18, 90, "years", "Patient age"),

    # Respiratory Rate (breaths/min)
    "RR_MEAN": (12, 20, "breaths/min", "Mean respiratory rate"),
    "RR_MAX": (20, 30, "breaths/min", "Maximum respiratory rate"),
    "RR_MIN": (8, 12, "breaths/min", "Minimum respiratory rate"),

    # Temperature (°C)
    "TEMP_STD": (0, 1.0, "°C", "Temperature variability"),
    "TEMP_MIN": (36.0, 36.5, "°C", "Minimum temperature"),

    # Heart Rate (bpm)
    "HR_MEAN": (60, 100, "bpm", "Mean heart rate"),
    "HR_MAX": (60, 140, "bpm", "Maximum heart rate"),
    "HR_STD": (0, 20, "bpm", "Heart rate variability"),

    # RDW (%)
    "RDW_max": (14.5, 18.0, "%", "Maximum RDW"),
    "RDW_mean": (11.5, 14.5, "%", "Mean RDW"),
    "RDW_min": (11.0, 11.5, "%", "Minimum RDW"),
    "RDW_std": (0, 3, "%", "RDW variability"),

    # Comorbidity score
    "age_adj_comorbidity_score": (0, 20, "", "Age-adjusted comorbidity score"),

    # Mean Arterial Pressure (mmHg)
    "MEANBP_MIN": (60, 65, "mmHg", "Minimum MAP"),
    "MEANBP_MEAN": (65, 105, "mmHg", "Mean arterial pressure (MAP)"),
}


DRIVER_FEATURES = [
    "GCS_max",
    "GCS_mean",
    "Lactate_min",
    "Lactate_max",
    "Lactate_mean",
    "BUN_min",
    "BUN_mean",
    "Bilirubin_max",
    "Bilirubin_mean",
    "AG_MEAN",
    "AG_MAX",
    "AG_MIN",
    "AG_STD",
    "SYSBP_MIN",
    "SYSBP_MEAN",
    "SYSBP_STD",
    "DIASBP_MIN",
    "DIASBP_MEAN",
    "AGE",
    "RR_MEAN",
    "RR_MAX",
    "RR_MIN",
    "TEMP_STD",
    "TEMP_MIN",
    "HR_MEAN",
    "HR_MAX",
    "HR_STD",
    "RDW_max",
    "RDW_mean",
    "RDW_min",
    "RDW_std",
    "age_adj_comorbidity_score",
    "MEANBP_MIN",
    "MEANBP_MEAN",
]
