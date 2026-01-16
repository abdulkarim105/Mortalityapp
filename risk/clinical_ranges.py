# risk/clinical_ranges.py
# column_name: (low, high, unit, label)

NORMAL_RANGES = {
    # -------------------------
    # Neuro
    # -------------------------
    "GCS_max": (15, 15, "", "Maximum Glasgow Coma Scale"),
    "GCS_mean": (13, 15, "", "Mean Glasgow Coma Scale"),

    # -------------------------
    # Lactate (mmol/L)
    # -------------------------
    "Lactate_min": (0.5, 2.0, "mmol/L", "Minimum lactate"),
    "Lactate_mean": (0.5, 2.0, "mmol/L", "Mean lactate"),
    "Lactate_max": (0.5, 4.0, "mmol/L", "Maximum lactate"),

    # -------------------------
    # Renal: BUN (mg/dL)
    # -------------------------
    "BUN_min": (7, 20, "mg/dL", "Minimum BUN"),
    "BUN_mean": (7, 20, "mg/dL", "Mean BUN"),
    "BUN_max": (7, 25, "mg/dL", "Maximum BUN"),

    # -------------------------
    # Liver: Bilirubin (mg/dL)
    # -------------------------
    "Bilirubin_mean": (0.2, 1.2, "mg/dL", "Mean bilirubin"),
    "Bilirubin_max": (0.2, 1.2, "mg/dL", "Maximum bilirubin"),

    # Albumin (g/dL)
    "Albumin_min": (3.5, 5.0, "g/dL", "Minimum albumin"),
    "Albumin_mean": (3.5, 5.0, "g/dL", "Mean albumin"),
    "Albumin_max": (3.5, 5.0, "g/dL", "Maximum albumin"),

    # Alkaline Phosphatase (U/L) - broad normal range
    "AlkPhos_min": (40, 130, "U/L", "Minimum alkaline phosphatase"),
    "AlkPhos_mean": (40, 130, "U/L", "Mean alkaline phosphatase"),
    "AlkPhos_max": (40, 130, "U/L", "Maximum alkaline phosphatase"),

    # -------------------------
    # Coagulation
    # -------------------------
    # PT (seconds)
    "PT_min": (11, 14, "s", "Minimum prothrombin time (PT)"),
    "PT_mean": (11, 14, "s", "Mean prothrombin time (PT)"),

    # INR
    "INR_min": (0.8, 1.2, "", "Minimum INR"),
    "INR_mean": (0.8, 1.2, "", "Mean INR"),

    # aPTT (seconds)
    "aPTT_min": (25, 35, "s", "Minimum activated PTT (aPTT)"),
    "aPTT_mean": (25, 35, "s", "Mean activated PTT (aPTT)"),

    # -------------------------
    # Electrolytes / metabolism
    # -------------------------
    # Phosphate (mg/dL)
    "Phosphate_mean": (2.5, 4.5, "mg/dL", "Mean phosphate"),
    "Phosphate_max": (2.5, 4.5, "mg/dL", "Maximum phosphate"),

    # Anion Gap (mEq/L)
    "AG_mean": (8, 16, "mEq/L", "Mean anion gap"),
    "AG_min": (8, 16, "mEq/L", "Minimum anion gap"),
    "AG_max": (8, 16, "mEq/L", "Maximum anion gap"),
    "AG_std": (0, 6, "mEq/L", "Anion gap variability"),

    # -------------------------
    # Respiratory / oxygenation
    # -------------------------
    # PaO2 (mmHg) - wide range; low PaO2 is the main concern
    "PaO2_mean": (80, 120, "mmHg", "Mean PaO₂"),
    "PaO2_max": (80, 200, "mmHg", "Maximum PaO₂"),

    # Respiratory Rate (breaths/min)
    "RR_min": (8, 12, "breaths/min", "Minimum respiratory rate"),
    "RR_mean": (12, 20, "breaths/min", "Mean respiratory rate"),
    "RR_max": (12, 30, "breaths/min", "Maximum respiratory rate"),

    # -------------------------
    # Temperature (°C)
    # -------------------------
    "TEMP_min": (36.0, 37.5, "°C", "Minimum temperature"),
    "TEMP_std": (0.0, 1.0, "°C", "Temperature variability"),

    # -------------------------
    # Heart Rate (bpm)
    # -------------------------
    "HR_mean": (60, 100, "bpm", "Mean heart rate"),
    "HR_max": (60, 140, "bpm", "Maximum heart rate"),
    "HR_std": (0, 20, "bpm", "Heart rate variability"),

    # -------------------------
    # Blood pressure (mmHg)
    # -------------------------
    "SYSBP_min": (90, 120, "mmHg", "Minimum systolic BP"),
    "SYSBP_mean": (90, 140, "mmHg", "Mean systolic BP"),
    "SYSBP_std": (0, 25, "mmHg", "Systolic BP variability"),

    "DIASBP_min": (60, 80, "mmHg", "Minimum diastolic BP"),
    "DIASBP_mean": (60, 90, "mmHg", "Mean diastolic BP"),

    # Mean Arterial Pressure (MAP)
    "MEANBP_min": (65, 105, "mmHg", "Minimum MAP"),
    "MEANBP_mean": (65, 105, "mmHg", "Mean arterial pressure (MAP)"),

    # -------------------------
    # Hematology
    # -------------------------
    # RDW (%)
    "RDW_min": (11.0, 14.5, "%", "Minimum RDW"),
    "RDW_mean": (11.5, 14.5, "%", "Mean RDW"),
    "RDW_max": (11.5, 14.5, "%", "Maximum RDW"),
    "RDW_std": (0, 3, "%", "RDW variability"),

    # -------------------------
    # Demographics / score
    # -------------------------
    "age": (18, 90, "years", "Patient age"),
    "age_adj_comorbidity_score": (0, 20, "", "Age-adjusted comorbidity score"),
}


# Which features should appear as "Clinical drivers"
# (You can include all features, but usually it's better to keep it clinically readable.)
DRIVER_FEATURES = [
    # Neuro
    "GCS_max",
    "GCS_mean",

    # Lactate
    "Lactate_min",
    "Lactate_mean",
    "Lactate_max",

    # Renal
    "BUN_min",
    "BUN_mean",
    "BUN_max",

    # Liver / nutrition
    "Bilirubin_mean",
    "Bilirubin_max",
    "Albumin_min",
    "Albumin_mean",

    # Coagulation
    "PT_mean",
    "INR_mean",
    "aPTT_mean",

    # Metabolic
    "AG_mean",
    "AG_max",
    "AG_min",

    "Phosphate_mean",

    # Resp / O2
    "PaO2_mean",
    "RR_mean",
    "RR_max",
    "RR_min",

    # Temp
    "TEMP_min",

    # HR
    "HR_mean",
    "HR_max",

    # BP / perfusion
    "SYSBP_min",
    "SYSBP_mean",
    "MEANBP_min",
    "MEANBP_mean",

    "DIASBP_min",
    "DIASBP_mean",

    # Hematology
    "RDW_mean",
    "RDW_max",

    # Scores / demo
    "age",
    "age_adj_comorbidity_score",
]
