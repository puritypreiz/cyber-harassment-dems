"""Composite indexes beyond the single-column indexes declared inline on models.

Imported once during init_db() so they're created alongside the tables.
"""
from sqlalchemy import Index

from backend.database.models.audit_log import AuditLog
from backend.database.models.case import Case
from backend.database.models.evidence import Evidence

Index("ix_cases_status_severity", Case.status, Case.severity)
Index("ix_evidence_case_uploaded", Evidence.case_id, Evidence.uploaded_at)
Index("ix_audit_actor_created", AuditLog.actor_id, AuditLog.created_at)
