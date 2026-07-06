class Roles:
    STUDENT = "student"
    COUNSELOR = "counselor"
    LEGAL = "legal"
    ADMIN = "admin"

    ALL = (STUDENT, COUNSELOR, LEGAL, ADMIN)
    STAFF = (COUNSELOR, LEGAL, ADMIN)


class CaseStatus:
    OPEN = "open"
    UNDER_REVIEW = "under_review"
    ESCALATED = "escalated"
    RESOLVED = "resolved"
    CLOSED = "closed"

    ALL = (OPEN, UNDER_REVIEW, ESCALATED, RESOLVED, CLOSED)


class SeverityLevel:
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

    ALL = (LOW, MEDIUM, HIGH, CRITICAL)


class HarassmentCategory:
    CYBERSTALKING = "cyberstalking"
    NON_CONSENSUAL_IMAGERY = "non_consensual_imagery"
    DOXXING = "doxxing"
    IMPERSONATION = "impersonation"
    THREATS = "threats"
    SEXUAL_HARASSMENT = "sexual_harassment"
    HATE_SPEECH = "hate_speech"
    DEFAMATION = "defamation"
    OTHER = "other"

    ALL = (
        CYBERSTALKING, NON_CONSENSUAL_IMAGERY, DOXXING, IMPERSONATION,
        THREATS, SEXUAL_HARASSMENT, HATE_SPEECH, DEFAMATION, OTHER,
    )


class AuditAction:
    EVIDENCE_UPLOADED = "evidence_uploaded"
    EVIDENCE_VIEWED = "evidence_viewed"
    EVIDENCE_DOWNLOADED = "evidence_downloaded"
    EVIDENCE_VERIFIED = "evidence_verified"
    EVIDENCE_INTEGRITY_FAILED = "evidence_integrity_failed"
    CASE_CREATED = "case_created"
    CASE_UPDATED = "case_updated"
    CASE_STATUS_CHANGED = "case_status_changed"
    USER_LOGIN = "user_login"
    USER_LOGIN_FAILED = "user_login_failed"
    USER_REGISTERED = "user_registered"
    REPORT_EXPORTED = "report_exported"
    QR_GENERATED = "qr_generated"
    QR_SCANNED = "qr_scanned"


NATIONAL_CRISIS_RESOURCES = [
    {
        "name": "National Sexual Assault Hotline",
        "contact": "1-800-656-4673",
        "available": "24/7",
    },
    {
        "name": "Crisis Text Line",
        "contact": "Text HOME to 741741",
        "available": "24/7",
    },
    {
        "name": "Cyber Civil Rights Initiative",
        "contact": "https://cybercivilrights.org",
        "available": "Online resources & helpline",
    },
]
