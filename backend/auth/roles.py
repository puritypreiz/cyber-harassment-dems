from functools import wraps

from flask import g, jsonify, request

from backend.auth.jwt_handler import TokenError, decode_token
from backend.database.database import db
from backend.database.models.user import User


def _extract_bearer_token() -> str | None:
    header = request.headers.get("Authorization", "")
    if header.startswith("Bearer "):
        return header[len("Bearer "):].strip()
    return None


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        token = _extract_bearer_token()
        if not token:
            return jsonify({"error": "Authentication required."}), 401
        try:
            payload = decode_token(token, expected_type="access")
        except TokenError as exc:
            return jsonify({"error": str(exc)}), 401

        user = db.session.get(User, payload["sub"])
        if user is None or not user.is_active:
            return jsonify({"error": "Account is not available."}), 401

        g.current_user = user
        return view(*args, **kwargs)

    return wrapped


def roles_required(*allowed_roles):
    def decorator(view):
        @wraps(view)
        @login_required
        def wrapped(*args, **kwargs):
            if g.current_user.role not in allowed_roles:
                return jsonify({"error": "You do not have permission to perform this action."}), 403
            return view(*args, **kwargs)

        return wrapped

    return decorator
