from django.db import models
from django.conf import settings

class AuditEvent(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    action = models.CharField(max_length=64)
    object_type = models.CharField(max_length=128)
    object_id = models.CharField(max_length=64)
    details = models.JSONField(default=dict, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["created_at"]),
            models.Index(fields=["action"]),
            models.Index(fields=["object_type","object_id"]),
        ]

    def __str__(self):
        return f"{self.created_at} {self.action} {self.object_type}#{self.object_id}"
