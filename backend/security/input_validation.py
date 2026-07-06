"""Defensive input validation helpers used at API boundaries.

These guard against injection and oversized-payload attacks before data reaches
business logic. SQLAlchemy's ORM already parameterizes queries, but we still
validate shape/type/length of everything coming from the network.
"""
from backend.utils.validators import is_safe_string


class ValidationError(Exception):
    def __init__(self, errors: dict):
        self.errors = errors
        super().__init__(str(errors))


def require_fields(payload: dict, fields: list[str]) -> dict:
    if not isinstance(payload, dict):
        raise ValidationError({"_": "Request body must be a JSON object."})
    errors = {}
    for field in fields:
        if field not in payload or payload[field] in (None, ""):
            errors[field] = "This field is required."
    if errors:
        raise ValidationError(errors)
    return payload


def sanitize_text(value, field_name: str, max_length: int = 5000, required: bool = True) -> str:
    if value is None:
        if required:
            raise ValidationError({field_name: "This field is required."})
        return ""
    if not isinstance(value, str):
        raise ValidationError({field_name: "Must be a string."})
    value = value.strip()
    if required and not value:
        raise ValidationError({field_name: "This field is required."})
    if not is_safe_string(value, max_length=max_length):
        raise ValidationError({field_name: f"Invalid characters or exceeds {max_length} characters."})
    return value


def sanitize_choice(value, field_name: str, allowed: tuple) -> str:
    if value not in allowed:
        raise ValidationError({field_name: f"Must be one of: {', '.join(allowed)}."})
    return value
