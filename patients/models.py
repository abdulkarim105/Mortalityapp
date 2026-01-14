from django.db import models
from django.utils import timezone

class Patient(models.Model):
    mrn = models.CharField("MRN", max_length=64, unique=True)
    full_name = models.CharField(max_length=255)
    date_of_birth = models.DateField(null=True, blank=True)
    sex = models.CharField(max_length=16, blank=True)

    def __str__(self):
        return f"{self.full_name} ({self.mrn})"

class Encounter(models.Model):
    STATUS_CHOICES = [
        ("ACTIVE", "Active"),
        ("DISCHARGED", "Discharged"),
    ]
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="encounters")
    admitted_at = models.DateTimeField(default=timezone.now)
    unit = models.CharField(max_length=64, blank=True, help_text="e.g., ICU-A, ICU-B, Ward 3")
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="ACTIVE")

    def __str__(self):
        return f"Encounter #{self.id} - {self.patient}"
