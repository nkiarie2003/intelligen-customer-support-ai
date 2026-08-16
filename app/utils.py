from functools import wraps
from flask import abort
from flask_login import current_user

from .extensions import db
from .models import AuditLog


def staff_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(401)
        if not current_user.is_staff:
            abort(403)
        return view(*args, **kwargs)
    return wrapped


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(401)
        if current_user.role != "admin":
            abort(403)
        return view(*args, **kwargs)
    return wrapped


def audit(action: str, entity_type: str, entity_id=None, detail=None):
    actor_id = current_user.id if current_user.is_authenticated else None
    db.session.add(
        AuditLog(
            actor_id=actor_id,
            action=action,
            entity_type=entity_type,
            entity_id=str(entity_id) if entity_id is not None else None,
            detail=detail or {},
        )
    )
