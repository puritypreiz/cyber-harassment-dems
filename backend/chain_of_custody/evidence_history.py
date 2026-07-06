from backend.database.models.audit_log import AuditLog


def get_entity_history(entity_type: str, entity_id: str) -> list[AuditLog]:
    return (
        AuditLog.query.filter_by(entity_type=entity_type, entity_id=entity_id)
        .order_by(AuditLog.created_at.asc())
        .all()
    )


def get_case_history(case_id: str) -> list[AuditLog]:
    """All custody events touching a case or any evidence filed under it."""
    from backend.database.models.evidence import Evidence

    evidence_ids = [row.id for row in Evidence.query.filter_by(case_id=case_id).all()]
    relevant_entity_ids = [case_id, *evidence_ids]
    return (
        AuditLog.query.filter(AuditLog.entity_id.in_(relevant_entity_ids))
        .order_by(AuditLog.created_at.asc())
        .all()
    )
