import uuid
from backend.utils.helpers import utcnow

from backend.database.database import db


def _uuid() -> str:
    return str(uuid.uuid4())


class AuditLog(db.Model):
    """Append-only chain-of-custody / security audit trail.

    Each entry is signed (see chain_of_custody.digital_signature) and chained to the
    previous entry's hash so tampering with historical rows is detectable.
    """

    __tablename__ = "audit_logs"

    id = db.Column(db.String(36), primary_key=True, default=_uuid)
    actor_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=True)
    action = db.Column(db.String(60), nullable=False, index=True)

    entity_type = db.Column(db.String(40), nullable=True)
    entity_id = db.Column(db.String(36), nullable=True, index=True)

    ip_address = db.Column(db.String(45), nullable=True)
    details = db.Column(db.JSON, nullable=True)

    previous_entry_hash = db.Column(db.String(64), nullable=True)
    entry_hash = db.Column(db.String(64), nullable=False)
    signature = db.Column(db.Text, nullable=False)

    created_at = db.Column(db.DateTime, default=lambda: utcnow(), nullable=False)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "actor_id": self.actor_id,
            "action": self.action,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "details": self.details,
            "entry_hash": self.entry_hash,
            "previous_entry_hash": self.previous_entry_hash,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
