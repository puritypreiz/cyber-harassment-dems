import uuid
from backend.utils.helpers import utcnow

from backend.database.database import db


def _uuid() -> str:
    return str(uuid.uuid4())


class Evidence(db.Model):
    __tablename__ = "evidence"

    id = db.Column(db.String(36), primary_key=True, default=_uuid)
    case_id = db.Column(db.String(36), db.ForeignKey("cases.id"), nullable=False)
    uploaded_by_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False)

    original_filename = db.Column(db.String(255), nullable=False)
    stored_filename = db.Column(db.String(255), nullable=False, unique=True)
    mime_type = db.Column(db.String(100), nullable=False)
    size_bytes = db.Column(db.Integer, nullable=False)

    sha256_hash = db.Column(db.String(64), nullable=False, index=True)
    encryption_nonce = db.Column(db.String(32), nullable=False)

    description = db.Column(db.Text, nullable=True)
    captured_metadata = db.Column(db.JSON, nullable=True)

    is_verified = db.Column(db.Boolean, default=True, nullable=False)
    last_verified_at = db.Column(db.DateTime, nullable=True)

    uploaded_at = db.Column(db.DateTime, default=lambda: utcnow(), nullable=False)

    qr_code = db.relationship("QRCode", backref="evidence", uselist=False, lazy="joined")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "case_id": self.case_id,
            "original_filename": self.original_filename,
            "mime_type": self.mime_type,
            "size_bytes": self.size_bytes,
            "sha256_hash": self.sha256_hash,
            "description": self.description,
            "is_verified": self.is_verified,
            "last_verified_at": self.last_verified_at.isoformat() if self.last_verified_at else None,
            "uploaded_at": self.uploaded_at.isoformat() if self.uploaded_at else None,
        }
