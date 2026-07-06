from backend.database.database import db
from backend.database.models.consent import Consent
from backend.utils.helpers import utcnow


class ConsentType:
    DATA_PROCESSING = "data_processing"
    EVIDENCE_SHARING = "evidence_sharing"
    COUNSELOR_REFERRAL = "counselor_referral"

    ALL = (DATA_PROCESSING, EVIDENCE_SHARING, COUNSELOR_REFERRAL)


def grant_consent(user, consent_type: str) -> Consent:
    consent = Consent.query.filter_by(user_id=user.id, consent_type=consent_type).first()
    now = utcnow()
    if consent is None:
        consent = Consent(user_id=user.id, consent_type=consent_type)
        db.session.add(consent)
    consent.granted = True
    consent.granted_at = now
    consent.revoked_at = None
    db.session.commit()
    return consent


def revoke_consent(user, consent_type: str) -> Consent | None:
    consent = Consent.query.filter_by(user_id=user.id, consent_type=consent_type).first()
    if consent is None:
        return None
    consent.granted = False
    consent.revoked_at = utcnow()
    db.session.commit()
    return consent


def has_consent(user, consent_type: str) -> bool:
    consent = Consent.query.filter_by(user_id=user.id, consent_type=consent_type, granted=True).first()
    return consent is not None
