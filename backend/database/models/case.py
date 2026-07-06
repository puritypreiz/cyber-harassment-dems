import uuid
from backend.utils.helpers import utcnow

from backend.database.database import db
from backend.utils.constants import CaseStatus, HarassmentCategory, SeverityLevel


def _uuid() -> str:
    return str(uuid.uuid4())


class Case(db.Model):
    __tablename__ = "cases"

    id = db.Column(db.String(36), primary_key=True, default=_uuid)
    case_number = db.Column(db.String(20), unique=True, nullable=False, index=True)

    reporter_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False)
    assigned_counselor_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=True)
    assigned_legal_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=True)

    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(40), nullable=False, default=HarassmentCategory.OTHER)
    severity = db.Column(db.String(20), nullable=False, default=SeverityLevel.LOW)
    status = db.Column(db.String(20), nullable=False, default=CaseStatus.OPEN)

    is_anonymous = db.Column(db.Boolean, default=False, nullable=False)

    created_at = db.Column(db.DateTime, default=lambda: utcnow(), nullable=False)
    updated_at = db.Column(
        db.DateTime, default=lambda: utcnow(),
        onupdate=lambda: utcnow(), nullable=False,
    )
    closed_at = db.Column(db.DateTime, nullable=True)

    evidence_items = db.relationship("Evidence", backref="case", lazy="dynamic")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "case_number": self.case_number,
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "severity": self.severity,
            "status": self.status,
            "is_anonymous": self.is_anonymous,
            "assigned_counselor_id": self.assigned_counselor_id,
            "assigned_legal_id": self.assigned_legal_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
