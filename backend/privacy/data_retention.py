from datetime import timedelta

from flask import current_app

from backend.chain_of_custody.audit_log import record as record_audit
from backend.database.models.case import Case
from backend.utils.constants import AuditAction, CaseStatus
from backend.utils.helpers import utcnow


def find_cases_due_for_purge_review(retention_days: int | None = None) -> list[Case]:
    """Closed/resolved cases whose retention window has elapsed.

    Returns candidates for review, not for automatic deletion - evidence in an
    active legal proceeding must never be auto-purged, so a human (admin/legal)
    always confirms before any data is removed. Never called on a schedule
    without that human-in-the-loop step.
    """
    days = retention_days or current_app.config["DATA_RETENTION_DAYS_DEFAULT"]
    cutoff = utcnow() - timedelta(days=days)

    return (
        Case.query.filter(
            Case.status.in_((CaseStatus.RESOLVED, CaseStatus.CLOSED)),
            Case.closed_at.isnot(None),
            Case.closed_at < cutoff,
        )
        .all()
    )


def mark_reviewed_for_retention(case: Case, actor, decision: str) -> None:
    """Records that an authorized staff member reviewed a retention candidate.
    `decision` should describe the outcome, e.g. 'retained_legal_hold' or 'purged'.
    """
    record_audit(
        action=AuditAction.CASE_UPDATED,
        actor_id=actor.id,
        entity_type="case",
        entity_id=case.id,
        details={"retention_review_decision": decision},
    )
