from datetime import datetime, timedelta, timezone

from backend.utils.helpers import utcnow

# In-memory refresh-token blocklist (revoked on logout / rotation).
# For multi-process deployments, back this with Redis instead.
_revoked_tokens: dict[str, datetime] = {}


def revoke_token(jti: str, expires_at: datetime) -> None:
    _revoked_tokens[jti] = expires_at
    _purge_expired()


def is_token_revoked(jti: str) -> bool:
    _purge_expired()
    return jti in _revoked_tokens


def _purge_expired() -> None:
    now = datetime.now(timezone.utc)
    expired = [jti for jti, exp in _revoked_tokens.items() if exp < now]
    for jti in expired:
        _revoked_tokens.pop(jti, None)


def lockout_expiry(minutes: int = 15) -> datetime:
    """Returned as naive UTC - this value is stored in User.locked_until (a DB
    column), unlike the revoked-token expiries above which stay in memory."""
    return utcnow() + timedelta(minutes=minutes)
