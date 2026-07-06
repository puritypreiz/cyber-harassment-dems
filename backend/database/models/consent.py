import uuid
from backend.utils.helpers import utcnow

from backend.database.database import db


def _uuid() -> str:
    return str(uuid.uuid4())


class Consent(db.Model):
    __tablename__ = "consents"

    id = db.Column(db.String(36), primary_key=True, default=_uuid)
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False)

    consent_type = db.Column(db.String(60), nullable=False)  # e.g. data_processing, evidence_sharing, counselor_referral
    granted = db.Column(db.Boolean, nullable=False, default=False)

    granted_at = db.Column(db.DateTime, nullable=True)
    revoked_at = db.Column(db.DateTime, nullable=True)

    created_at = db.Column(db.DateTime, default=lambda: utcnow(), nullable=False)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "consent_type": self.consent_type,
            "granted": self.granted,
            "granted_at": self.granted_at.isoformat() if self.granted_at else None,
            "revoked_at": self.revoked_at.isoformat() if self.revoked_at else None,
        }
