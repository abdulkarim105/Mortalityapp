from __future__ import annotations
from typing import Any, Dict
from .models import AuditEvent

def log_event(*, user, action: str, obj, details: Dict[str, Any] | None = None):
    AuditEvent.objects.create(
        user=user if getattr(user, "is_authenticated", False) else None,
        action=action,
        object_type=obj.__class__.__name__,
        object_id=str(getattr(obj, "id", "")),
        details=details or {},
    )
