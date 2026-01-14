from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator
from .models import ObservationSet
from .feature_ranges import FEATURE_RANGES


class ObservationSetForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["recorded_by_name"].help_text = (
            "Type nurse/clinician name (this will be shown on the encounter)"
        )

    class Meta:
        model = ObservationSet
        #fields = ["recorded_at"] + ObservationSet.feature_columns()
        fields = ["recorded_at", "recorded_by_name"] + ObservationSet.feature_columns()
        #widgets = {
           # "recorded_at": forms.DateTimeInput(attrs={"type": "datetime-local"})
        #}
        widgets = {
             "recorded_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
             "recorded_by_name": forms.TextInput(attrs={"placeholder": "Enter nurse/clinician name"}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Apply feature ranges to all fields
        for field_name, (min_v, max_v) in FEATURE_RANGES.items():
            if field_name not in self.fields:
                continue

            field = self.fields[field_name]

            # 1) Backend validation (Django)
            field.validators.append(MinValueValidator(min_v))
            field.validators.append(MaxValueValidator(max_v))

            # 2) Frontend validation (HTML5 browser popup)
            field.widget.attrs["type"] = "number"
            field.widget.attrs["min"] = str(min_v)
            field.widget.attrs["max"] = str(max_v)
            field.widget.attrs["step"] = "any"

            # Optional helper text
           # field.help_text = f"Allowed range: {min_v} to {max_v}"

    def clean(self):
        cleaned = super().clean()

        # Extra safety: explicit error messages
        for field_name, (min_v, max_v) in FEATURE_RANGES.items():
            if field_name not in cleaned:
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
