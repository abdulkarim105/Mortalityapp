from django.db import models
from django.conf import settings
from django.utils import timezone
from patients.models import Encounter

FEATURE_COLUMNS = [
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
    "MEANBP_MEAN"
]

class ObservationSet(models.Model):
    """A structured snapshot of vitals/labs used for ML prediction."""
    encounter = models.ForeignKey(Encounter, on_delete=models.CASCADE, related_name="observation_sets")
    recorded_at = models.DateTimeField(default=timezone.now)
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="recorded_observations"
    )
    recorded_by_name = models.CharField(max_length=120, null=True, blank=True)
    # ✅ ADD THIS (so DB NOT NULL column always gets a value, without changing UI)
    #recorded_by_name = models.CharField(max_length=120, blank=True, default="")

    GCS_max = models.FloatField(null=True, blank=True)
    GCS_mean = models.FloatField(null=True, blank=True)
    Lactate_min = models.FloatField(null=True, blank=True)
    Lactate_max = models.FloatField(null=True, blank=True)
    Lactate_mean = models.FloatField(null=True, blank=True)
    BUN_min = models.FloatField(null=True, blank=True)
    BUN_mean = models.FloatField(null=True, blank=True)
    Bilirubin_max = models.FloatField(null=True, blank=True)
    Bilirubin_mean = models.FloatField(null=True, blank=True)
    AG_MEAN = models.FloatField(null=True, blank=True)
    AG_MAX = models.FloatField(null=True, blank=True)
    AG_MIN = models.FloatField(null=True, blank=True)
    AG_STD = models.FloatField(null=True, blank=True)
    SYSBP_MIN = models.FloatField(null=True, blank=True)
    SYSBP_MEAN = models.FloatField(null=True, blank=True)
    SYSBP_STD = models.FloatField(null=True, blank=True)
    DIASBP_MIN = models.FloatField(null=True, blank=True)
    DIASBP_MEAN = models.FloatField(null=True, blank=True)
    AGE = models.FloatField(null=True, blank=True)
    RR_MEAN = models.FloatField(null=True, blank=True)
    RR_MAX = models.FloatField(null=True, blank=True)
    RR_MIN = models.FloatField(null=True, blank=True)
    TEMP_STD = models.FloatField(null=True, blank=True)
    TEMP_MIN = models.FloatField(null=True, blank=True)
    HR_MEAN = models.FloatField(null=True, blank=True)
    HR_MAX = models.FloatField(null=True, blank=True)
    HR_STD = models.FloatField(null=True, blank=True)
    RDW_max = models.FloatField(null=True, blank=True)
    RDW_mean = models.FloatField(null=True, blank=True)
    RDW_min = models.FloatField(null=True, blank=True)
    RDW_std = models.FloatField(null=True, blank=True)
    age_adj_comorbidity_score = models.FloatField(null=True, blank=True)
    MEANBP_MIN = models.FloatField(null=True, blank=True)
    MEANBP_MEAN = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"ObservationSet #{self.id} for Encounter #{self.encounter_id}"

    @staticmethod
    def feature_columns():
        return FEATURE_COLUMNS
