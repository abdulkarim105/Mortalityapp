from django.contrib import admin
from .models import ObservationSet

@admin.register(ObservationSet)
class ObservationSetAdmin(admin.ModelAdmin):
    list_display = ("id","encounter","recorded_at","recorded_by")
    list_filter = ("recorded_at",)
    search_fields = ("encounter__patient__mrn","encounter__patient__full_name")
