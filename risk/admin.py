from django.contrib import admin
from .models import RiskAssessment

@admin.register(RiskAssessment)
class RiskAssessmentAdmin(admin.ModelAdmin):
    list_display = ("id","encounter","risk_180d","risk_band","model_version","created_at","created_by")
    list_filter = ("risk_band","model_version")
