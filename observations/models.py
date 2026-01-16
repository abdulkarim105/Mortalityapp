from django.db import models
from django.conf import settings
from django.utils import timezone
from patients.models import Encounter

# Must match the training CSV / model features EXACTLY (case-sensitive)
FEATURE_COLUMNS = [
    "GCS_max",
    "GCS_mean",
    "Lactate_min",
    "Lactate_max",
    "Lactate_mean",
    "BUN_min",
    "BUN_mean",
    "BUN_max",
    "Bilirubin_max",
    "Bilirubin_mean",
    "Albumin_mean",
    "Albumin_min",
    "Albumin_max",
    "AlkPhos_mean",
    "AlkPhos_max",
    "AlkPhos_min",
    "PT_mean",
    "PT_min",
    "INR_mean",
    "INR_min",
    "Phosphate_mean",
    "Phosphate_max",
    "PaO2_mean",
    "PaO2_max",
    "aPTT_mean",
    "aPTT_min",
    "AG_mean",
    "AG_max",
    "AG_min",
    "AG_std",
    "SYSBP_min",
    "SYSBP_mean",
    "SYSBP_std",
    "DIASBP_min",
    "DIASBP_mean",
    "age",
    "RR_mean",
    "RR_max",
    "RR_min",
    "TEMP_std",
    "TEMP_min",
    "HR_mean",
    "HR_max",
    "HR_std",
    "RDW_max",
    "RDW_mean",
    "RDW_min",
    "RDW_std",
    "age_adj_comorbidity_score",
    "MEANBP_min",
    "MEANBP_mean",
]


class ObservationSet(models.Model):
    """A structured snapshot of vitals/labs used for ML prediction."""
    encounter = models.ForeignKey(
        Encounter,
        on_delete=models.CASCADE,
        related_name="observation_sets"
    )
    recorded_at = models.DateTimeField(default=timezone.now)
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="recorded_observations"
    )
    recorded_by_name = models.CharField(max_length=120, null=True, blank=True)

    # ---- Features (match CSV exactly) ----
    GCS_max = models.FloatField(null=True, blank=True)
    GCS_mean = models.FloatField(null=True, blank=True)

    Lactate_min = models.FloatField(null=True, blank=True)
    Lactate_max = models.FloatField(null=True, blank=True)
    Lactate_mean = models.FloatField(null=True, blank=True)

    BUN_min = models.FloatField(null=True, blank=True)
    BUN_mean = models.FloatField(null=True, blank=True)
    BUN_max = models.FloatField(null=True, blank=True)

    Bilirubin_max = models.FloatField(null=True, blank=True)
    Bilirubin_mean = models.FloatField(null=True, blank=True)

    Albumin_mean = models.FloatField(null=True, blank=True)
    Albumin_min = models.FloatField(null=True, blank=True)
    Albumin_max = models.FloatField(null=True, blank=True)

    AlkPhos_mean = models.FloatField(null=True, blank=True)
    AlkPhos_max = models.FloatField(null=True, blank=True)
    AlkPhos_min = models.FloatField(null=True, blank=True)

    PT_mean = models.FloatField(null=True, blank=True)
    PT_min = models.FloatField(null=True, blank=True)

    INR_mean = models.FloatField(null=True, blank=True)
    INR_min = models.FloatField(null=True, blank=True)

    Phosphate_mean = models.FloatField(null=True, blank=True)
    Phosphate_max = models.FloatField(null=True, blank=True)

    PaO2_mean = models.FloatField(null=True, blank=True)
    PaO2_max = models.FloatField(null=True, blank=True)

    aPTT_mean = models.FloatField(null=True, blank=True)
    aPTT_min = models.FloatField(null=True, blank=True)

    AG_mean = models.FloatField(null=True, blank=True)
    AG_max = models.FloatField(null=True, blank=True)
    AG_min = models.FloatField(null=True, blank=True)
    AG_std = models.FloatField(null=True, blank=True)

    SYSBP_min = models.FloatField(null=True, blank=True)
    SYSBP_mean = models.FloatField(null=True, blank=True)
    SYSBP_std = models.FloatField(null=True, blank=True)

    DIASBP_min = models.FloatField(null=True, blank=True)
    DIASBP_mean = models.FloatField(null=True, blank=True)

    age = models.FloatField(null=True, blank=True)

    RR_mean = models.FloatField(null=True, blank=True)
    RR_max = models.FloatField(null=True, blank=True)
    RR_min = models.FloatField(null=True, blank=True)

    TEMP_std = models.FloatField(null=True, blank=True)
    TEMP_min = models.FloatField(null=True, blank=True)

    HR_mean = models.FloatField(null=True, blank=True)
    HR_max = models.FloatField(null=True, blank=True)
    HR_std = models.FloatField(null=True, blank=True)

    RDW_max = models.FloatField(null=True, blank=True)
    RDW_mean = models.FloatField(null=True, blank=True)
    RDW_min = models.FloatField(null=True, blank=True)
    RDW_std = models.FloatField(null=True, blank=True)

    age_adj_comorbidity_score = models.FloatField(null=True, blank=True)

    MEANBP_min = models.FloatField(null=True, blank=True)
    MEANBP_mean = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"ObservationSet #{self.id} for Encounter #{self.encounter_id}"

    @staticmethod
    def feature_columns():
        return FEATURE_COLUMNS
