from django import forms


# Form used BEFORE prediction (doctor name + confirmation)
class GenerateRiskForm(forms.Form):
    doctor_name = forms.CharField(
        required=True,
        label="Doctor name",
        widget=forms.TextInput(attrs={
            "class": "form-control",
        })
    )

    confirm = forms.BooleanField(
        required=True,
        label="Confirm",
        help_text="I confirm that the vitals/labs snapshot is correct for prediction."
    )


# Form used AFTER prediction (doctor comment)
class RiskCommentForm(forms.Form):
    doctor_comment = forms.CharField(
        required=False,
        label="Doctor comment",
        widget=forms.Textarea(attrs={
            "class": "form-control",
            "rows": 4,
            "placeholder": "Write doctor note after seeing the risk..."
        })
    )
