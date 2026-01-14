# risk/models.py
from django.conf import settings
from django.db import models


class RiskAssessment(models.Model):
    encounter = models.ForeignKey(
        "patients.Encounter",
        on_delete=models.CASCADE,
        related_name="risk_assessments"
    )

    observation_set = models.ForeignKey(
        "observations.ObservationSet",
        on_delete=models.CASCADE,
        related_name="risk_assessments"
    )

    risk_180d = models.FloatField()
    risk_band = models.CharField(max_length=16)

    model_version = models.CharField(max_length=64, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="risk_assessments_created",
    )

    # ✅ ADD THIS (so DB NOT NULL column always gets a value, without changing UI)
    doctor_name = models.CharField(max_length=120, blank=True, default="")

    doctor_comment = models.TextField(blank=True, default="")

    def __str__(self):
        return f"Risk #{self.id} {self.risk_band} {self.risk_180d:.2f}%"
