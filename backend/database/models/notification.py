import uuid
from backend.utils.helpers import utcnow

from backend.database.database import db


def _uuid() -> str:
    return str(uuid.uuid4())


class Notification(db.Model):
    __tablename__ = "notifications"

    id = db.Column(db.String(36), primary_key=True, default=_uuid)
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False)
    case_id = db.Column(db.String(36), db.ForeignKey("cases.id"), nullable=True)

    channel = db.Column(db.String(20), nullable=False)  # email | sms | in_app
    subject = db.Column(db.String(200), nullable=True)
    body = db.Column(db.Text, nullable=False)

    status = db.Column(db.String(20), nullable=False, default="pending")  # pending | sent | failed | skipped
    sent_at = db.Column(db.DateTime, nullable=True)

    created_at = db.Column(db.DateTime, default=lambda: utcnow(), nullable=False)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "case_id": self.case_id,
            "channel": self.channel,
            "subject": self.subject,
            "status": self.status,
            "sent_at": self.sent_at.isoformat() if self.sent_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
