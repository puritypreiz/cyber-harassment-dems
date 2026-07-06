import uuid
from backend.utils.helpers import utcnow

from backend.database.database import db


def _uuid() -> str:
    return str(uuid.uuid4())


class QRCode(db.Model):
    __tablename__ = "qr_codes"

    id = db.Column(db.String(36), primary_key=True, default=_uuid)
    evidence_id = db.Column(db.String(36), db.ForeignKey("evidence.id"), nullable=False, unique=True)

    token = db.Column(db.String(512), nullable=False, unique=True, index=True)
    image_filename = db.Column(db.String(255), nullable=False)

    scan_count = db.Column(db.Integer, default=0, nullable=False)
    last_scanned_at = db.Column(db.DateTime, nullable=True)

    created_at = db.Column(db.DateTime, default=lambda: utcnow(), nullable=False)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "evidence_id": self.evidence_id,
            "image_filename": self.image_filename,
            "scan_count": self.scan_count,
            "last_scanned_at": self.last_scanned_at.isoformat() if self.last_scanned_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
