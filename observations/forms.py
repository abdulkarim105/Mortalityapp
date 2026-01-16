from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator

from .models import ObservationSet
from .feature_ranges import FEATURE_RANGES


class ObservationSetForm(forms.ModelForm):
    class Meta:
        model = ObservationSet
        fields = ["recorded_at", "recorded_by_name"] + ObservationSet.feature_columns()
        widgets = {
            "recorded_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "recorded_by_name": forms.TextInput(attrs={"placeholder": "Enter nurse/clinician name"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Help text for recorded_by_name
        if "recorded_by_name" in self.fields:
            self.fields["recorded_by_name"].help_text = (
                "Type nurse/clinician name (this will be shown on the encounter)"
            )

        # Apply feature ranges to all fields (only if they exist in the form)
        for field_name, (min_v, max_v) in FEATURE_RANGES.items():
            if field_name not in self.fields:
                continue

            field = self.fields[field_name]

            # 1) Backend validation (Django)
            field.validators.append(MinValueValidator(min_v))
            field.validators.append(MaxValueValidator(max_v))

            # 2) Frontend validation (HTML5)
            field.widget.attrs["type"] = "number"
            field.widget.attrs["min"] = str(min_v)
            field.widget.attrs["max"] = str(max_v)
            field.widget.attrs["step"] = "any"

    def clean(self):
        cleaned = super().clean()

        # Extra safety: explicit error messages
        for field_name, (min_v, max_v) in FEATURE_RANGES.items():
            if field_name not in self.fields:
                continue

            value = cleaned.get(field_name)
            if value is None:
                continue

            try:
                value = float(value)
            except (TypeError, ValueError):
                continue

            if value < min_v or value > max_v:
                self.add_error(
                    field_name,
                    f"Value must be between {min_v} and {max_v}."
                )

        return cleaned
