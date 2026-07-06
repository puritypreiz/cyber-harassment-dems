import random
import string
from datetime import datetime, timezone

from backend.chain_of_custody.audit_log import record as record_audit
from backend.database.database import db
from backend.database.models.case import Case
from backend.database.models.user import User
from backend.harassment.classification import suggest_category
from backend.harassment.notifications import notify_case_status_change, notify_counselor_assigned
from backend.harassment.severity_assessment import assess_severity
from backend.utils.constants import AuditAction, CaseStatus, HarassmentCategory, Roles
from backend.utils.helpers import utcnow


class CaseError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


def _generate_case_number() -> str:
    year = datetime.now(timezone.utc).year
    suffix = "".join(random.choices(string.digits, k=6))
    candidate = f"CHD-{year}-{suffix}"
    if Case.query.filter_by(case_number=candidate).first():
        return _generate_case_number()
    return candidate


def create_case(reporter, title: str, description: str, category: str | None, is_anonymous: bool,
                 ip_address: str | None = None) -> Case:
    resolved_category = category if category in HarassmentCategory.ALL else suggest_category(description)
    severity = assess_severity(resolved_category, description)

    case = Case(
        case_number=_generate_case_number(),
        reporter_id=reporter.id,
        title=title,
        description=description,
        category=resolved_category,
        severity=severity,
        status=CaseStatus.OPEN,
        is_anonymous=is_anonymous,
    )
    db.session.add(case)
    db.session.commit()

    record_audit(
        action=AuditAction.CASE_CREATED,
        actor_id=reporter.id,
        entity_type="case",
        entity_id=case.id,
        details={"category": resolved_category, "severity": severity},
        ip_address=ip_address,
    )
    return case


def update_status(case: Case, new_status: str, actor, ip_address: str | None = None) -> Case:
    if new_status not in CaseStatus.ALL:
        raise CaseError("Invalid case status.")

    old_status = case.status
    case.status = new_status
    if new_status in (CaseStatus.RESOLVED, CaseStatus.CLOSED):
        case.closed_at = utcnow()
    db.session.commit()

    record_audit(
        action=AuditAction.CASE_STATUS_CHANGED,
        actor_id=actor.id,
        entity_type="case",
        entity_id=case.id,
        details={"old_status": old_status, "new_status": new_status},
        ip_address=ip_address,
    )

    reporter = db.session.get(User, case.reporter_id)
    if reporter:
        notify_case_status_change(reporter, case)
    return case


def assign_counselor(case: Case, counselor: User, actor, ip_address: str | None = None) -> Case:
    if counselor.role != Roles.COUNSELOR:
        raise CaseError("Target user is not a counselor.")

    case.assigned_counselor_id = counselor.id
    db.session.commit()

    record_audit(
        action=AuditAction.CASE_UPDATED,
        actor_id=actor.id,
        entity_type="case",
        entity_id=case.id,
        details={"assigned_counselor_id": counselor.id},
        ip_address=ip_address,
    )
    notify_counselor_assigned(counselor, case)
    return case


def assign_legal(case: Case, legal_user: User, actor, ip_address: str | None = None) -> Case:
    if legal_user.role != Roles.LEGAL:
        raise CaseError("Target user is not a legal-team member.")

    case.assigned_legal_id = legal_user.id
    db.session.commit()

    record_audit(
        action=AuditAction.CASE_UPDATED,
        actor_id=actor.id,
        entity_type="case",
        entity_id=case.id,
        details={"assigned_legal_id": legal_user.id},
        ip_address=ip_address,
    )
    return case
