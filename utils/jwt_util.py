import datetime
from typing import Any, Dict

import jwt
from flask import g, abort, request

from config.jwt_config import JWT_SECRET, JWT_ALGORITHM, ACCESS_TOKEN_EXPIRES


def create_access_token(user_id: int, role: str, email:str) -> str:
    """Create a JWT for the given user ID and role."""

    now = datetime.datetime.now(datetime.timezone.utc)

    payload = {
        "sub": str(user_id),
        "role": role,
        "email":email,
        "iat": now,
        "exp": now + datetime.timedelta(seconds=ACCESS_TOKEN_EXPIRES),
    }

    token = jwt.encode(
        payload,
        JWT_SECRET,
        algorithm=JWT_ALGORITHM
    )

    if isinstance(token, bytes):
        token = token.decode("utf-8")

    return token


def decode_token(token: str) -> Dict[str, Any]:
    """Decode and validate a JWT."""

    try:
        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM]
        )

        return payload

    except jwt.ExpiredSignatureError:
        abort(401, description="Token has expired")

    except jwt.InvalidTokenError:
        abort(401, description="Invalid token")


def jwt_required(fn):
    """Require a valid JWT from Authorization header or access_token cookie."""

    from functools import wraps

    @wraps(fn)
    def wrapper(*args, **kwargs):

        auth_header = request.headers.get("Authorization", "")

        if auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1].strip()

        else:
            token = request.cookies.get("access_token")

        if not token:
            abort(401, description="Missing authentication token")

        payload = decode_token(token)

        g.current_user = payload

        return fn(*args, **kwargs)

    return wrapper