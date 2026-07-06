from datetime import datetime, timezone

from backend.auth.jwt_handler import create_access_token, create_refresh_token, decode_token
from backend.auth.mfa import decrypt_secret, verify_totp_code
from backend.auth.password_manager import hash_password, verify_password
from backend.database.database import db
from backend.database.models.user import User
from backend.security.session_manager import lockout_expiry, revoke_token
from backend.utils.constants import Roles
from backend.utils.helpers import utcnow
from backend.utils.validators import is_strong_password, is_valid_email, is_valid_username

MAX_FAILED_ATTEMPTS = 5


class AuthError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class MFARequired(Exception):
    def __init__(self, user_id: str):
        self.user_id = user_id


def register_user(username: str, email: str, password: str, role: str = Roles.STUDENT) -> User:
    if not is_valid_username(username):
        raise AuthError("Username must be 3-32 characters (letters, digits, ., _, -).")
    if not is_valid_email(email):
        raise AuthError("A valid email address is required.")
    if not is_strong_password(password):
        raise AuthError(
            "Password must be at least 10 characters and include upper, lower, "
            "digit, and special characters."
        )
    if role not in Roles.ALL:
        role = Roles.STUDENT

    if User.query.filter((User.username == username) | (User.email == email)).first():
        raise AuthError("An account with that username or email already exists.", status_code=409)

    user = User(
        username=username,
        email=email,
        password_hash=hash_password(password),
        role=role,
    )
    db.session.add(user)
    db.session.commit()
    return user


def _is_locked(user: User) -> bool:
    return bool(user.locked_until and user.locked_until > utcnow())


def authenticate(username_or_email: str, password: str, totp_code: str | None = None) -> tuple[User, str, str]:
    user = User.query.filter(
        (User.username == username_or_email) | (User.email == username_or_email)
    ).first()

    if user is None:
        raise AuthError("Invalid credentials.", status_code=401)

    if _is_locked(user):
        raise AuthError("Account temporarily locked due to repeated failed login attempts.", status_code=423)

    if not user.is_active or not verify_password(password, user.password_hash):
        user.failed_login_attempts += 1
        if user.failed_login_attempts >= MAX_FAILED_ATTEMPTS:
            user.locked_until = lockout_expiry(minutes=15)
        db.session.commit()
        raise AuthError("Invalid credentials.", status_code=401)

    if user.mfa_enabled:
        if not totp_code:
            raise MFARequired(user.id)
        secret = decrypt_secret(user.mfa_secret_encrypted)
        if not verify_totp_code(secret, totp_code):
            user.failed_login_attempts += 1
            db.session.commit()
            raise AuthError("Invalid multi-factor authentication code.", status_code=401)

    user.failed_login_attempts = 0
    user.locked_until = None
    user.last_login_at = utcnow()
    db.session.commit()

    access_token = create_access_token(user.id, user.role)
    refresh_token, _, _ = create_refresh_token(user.id, user.role)
    return user, access_token, refresh_token


def refresh_access_token(refresh_token: str) -> str:
    from backend.auth.jwt_handler import TokenError

    try:
        payload = decode_token(refresh_token, expected_type="refresh")
    except TokenError as exc:
        raise AuthError(str(exc), status_code=401) from exc

    user = db.session.get(User, payload["sub"])
    if user is None or not user.is_active:
        raise AuthError("Account is not available.", status_code=401)

    return create_access_token(user.id, user.role)


def logout(access_payload: dict, refresh_payload: dict | None = None) -> None:
    exp = datetime.fromtimestamp(access_payload["exp"], tz=timezone.utc)
    revoke_token(access_payload["jti"], exp)
    if refresh_payload:
        exp = datetime.fromtimestamp(refresh_payload["exp"], tz=timezone.utc)
        revoke_token(refresh_payload["jti"], exp)
