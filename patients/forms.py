from django import forms
from .models import Patient, Encounter

class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ["mrn", "full_name", "date_of_birth", "sex"]
        widgets = {
            "date_of_birth": forms.DateInput(attrs={"type": "date"}),
        }

class EncounterForm(forms.ModelForm):
    class Meta:
        model = Encounter
        fields = ["patient", "admitted_at", "unit", "status"]
        widgets = {
            "admitted_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }
