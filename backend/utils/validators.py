import re

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

# At least 10 characters, one uppercase, one lowercase, one digit, one special character.
PASSWORD_RE = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^\w\s]).{10,}$")

USERNAME_RE = re.compile(r"^[A-Za-z0-9_.-]{3,32}$")


def is_valid_email(value: str) -> bool:
    return bool(value) and bool(EMAIL_RE.match(value.strip())) and len(value) <= 254


def is_strong_password(value: str) -> bool:
    return bool(value) and bool(PASSWORD_RE.match(value))


def is_valid_username(value: str) -> bool:
    return bool(value) and bool(USERNAME_RE.match(value))


def is_safe_string(value: str, max_length: int = 5000) -> bool:
    """Rejects null bytes and control characters commonly used in injection attempts."""
    if value is None:
        return False
    if len(value) > max_length:
        return False
    if "\x00" in value:
        return False
    return not any(ord(ch) < 9 for ch in value)
