from sqlalchemy import func

from backend.database.database import db
from backend.database.models.case import Case
from backend.database.models.user import User
from backend.utils.constants import CaseStatus, Roles


def find_least_loaded_counselor() -> User | None:
    """Auto-assignment picks the active counselor with the fewest open cases,
    so no single counselor is overloaded while others sit idle."""
    open_case_counts = (
        db.session.query(Case.assigned_counselor_id, func.count(Case.id))
        .filter(Case.status.in_((CaseStatus.OPEN, CaseStatus.UNDER_REVIEW, CaseStatus.ESCALATED)))
        .group_by(Case.assigned_counselor_id)
        .all()
    )
    load_by_counselor = {counselor_id: count for counselor_id, count in open_case_counts if counselor_id}

    counselors = User.query.filter_by(role=Roles.COUNSELOR, is_active=True).all()
    if not counselors:
        return None

    return min(counselors, key=lambda c: load_by_counselor.get(c.id, 0))
