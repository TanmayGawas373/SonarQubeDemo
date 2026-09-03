# utils/role.py

from functools import wraps
from flask import abort
from flask_login import current_user

def role_required(role):
    """Decorator to ensure the current_user has the given role.
    Returns 403 if role does not match, 401 if not authenticated.
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            if getattr(current_user, 'role', None) != role:
                abort(403)
            return f(*args, **kwargs)
        return wrapper
    return decorator
