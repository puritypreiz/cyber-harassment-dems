import uuid
from datetime import datetime, timedelta, timezone

import jwt
from flask import current_app

from backend.security.session_manager import is_token_revoked


class TokenError(Exception):
    pass


def _encode(payload: dict, expires_delta: timedelta, token_type: str) -> tuple[str, str, datetime]:
    now = datetime.now(timezone.utc)
    expires_at = now + expires_delta
    jti = str(uuid.uuid4())
    full_payload = {
        **payload,
        "type": token_type,
        "jti": jti,
        "iat": now,
        "exp": expires_at,
    }
    token = jwt.encode(full_payload, current_app.config["JWT_SECRET_KEY"], algorithm="HS256")
    return token, jti, expires_at


def create_access_token(user_id: str, role: str) -> str:
    minutes = current_app.config["JWT_ACCESS_TOKEN_MINUTES"]
    token, _, _ = _encode({"sub": user_id, "role": role}, timedelta(minutes=minutes), "access")
    return token


def create_refresh_token(user_id: str, role: str) -> tuple[str, str, datetime]:
    days = current_app.config["JWT_REFRESH_TOKEN_DAYS"]
    return _encode({"sub": user_id, "role": role}, timedelta(days=days), "refresh")


def decode_token(token: str, expected_type: str = "access") -> dict:
    try:
        payload = jwt.decode(token, current_app.config["JWT_SECRET_KEY"], algorithms=["HS256"])
    except jwt.ExpiredSignatureError as exc:
        raise TokenError("Token has expired.") from exc
    except jwt.InvalidTokenError as exc:
        raise TokenError("Token is invalid.") from exc

    if payload.get("type") != expected_type:
        raise TokenError(f"Expected a {expected_type} token.")

    if is_token_revoked(payload.get("jti", "")):
        raise TokenError("Token has been revoked.")

    return payload
