"""Object-level access control: can this specific user act on this specific
case/evidence record? Complements the coarse role checks in backend.auth.roles.
"""
from backend.utils.constants import Roles


class AccessDenied(Exception):
    pass


def can_access_case(user, case) -> bool:
    if user.role == Roles.ADMIN:
        return True
    if user.id == case.reporter_id:
        return True
    if user.role == Roles.COUNSELOR and user.id == case.assigned_counselor_id:
        return True
    if user.role == Roles.LEGAL and user.id == case.assigned_legal_id:
        return True
    return False


def can_access_evidence(user, case) -> bool:
    return can_access_case(user, case)


def can_modify_case(user, case) -> bool:
    if user.role == Roles.ADMIN:
        return True
    if user.role == Roles.COUNSELOR and user.id == case.assigned_counselor_id:
        return True
    if user.role == Roles.LEGAL and user.id == case.assigned_legal_id:
        return True
    return False


def enforce(condition: bool, message: str = "You do not have permission to perform this action.") -> None:
    if not condition:
        raise AccessDenied(message)
