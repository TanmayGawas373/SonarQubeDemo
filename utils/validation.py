# utils/validation.py
"""Centralized input‑validation helpers used across the app.
These functions raise ``ValueError`` with a clear message when validation fails.
The service layer catches ``ValueError`` and returns a 400 response.
"""

import re
from typing import Iterable

def require_fields(data: dict, fields: Iterable[str]):
    """Ensure ``data`` contains all ``fields``; raise ``ValueError`` otherwise.
    ``fields`` may be a list of required keys.
    """
    missing = [f for f in fields if f not in data or data[f] is None]
    if missing:
        raise ValueError(f"Missing required field(s): {', '.join(missing)}")
    return True

def validate_email(email: str):
    email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    if not re.match(email_regex, email):
        raise ValueError("Invalid email format")
    return True

def validate_password(password: str, min_length: int = 8):
    if len(password) < min_length:
        raise ValueError(f"Password must be at least {min_length} characters")
    return True

def validate_role(role: str, allowed: set = {"student", "instructor", "admin"}):
    if role not in allowed:
        raise ValueError(f"Role must be one of {', '.join(allowed)}")
    return True
