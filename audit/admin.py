from django.contrib import admin
from .models import AuditEvent

@admin.register(AuditEvent)
class AuditEventAdmin(admin.ModelAdmin):
    list_display = ("created_at","user","action","object_type","object_id")
    list_filter = ("action","object_type")
    search_fields = ("object_type","object_id","user__username")
    readonly_fields = ("created_at","user","action","object_type","object_id","details")
