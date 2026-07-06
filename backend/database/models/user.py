import uuid
from backend.utils.helpers import utcnow

from backend.database.database import db
from backend.utils.constants import Roles


def _uuid() -> str:
    return str(uuid.uuid4())


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.String(36), primary_key=True, default=_uuid)
    username = db.Column(db.String(32), unique=True, nullable=False, index=True)
    email = db.Column(db.String(254), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False, default=Roles.STUDENT)

    display_name = db.Column(db.String(120), nullable=True)
    is_anonymous_profile = db.Column(db.Boolean, default=False, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    mfa_enabled = db.Column(db.Boolean, default=False, nullable=False)
    mfa_secret_encrypted = db.Column(db.LargeBinary, nullable=True)

    failed_login_attempts = db.Column(db.Integer, default=0, nullable=False)
    locked_until = db.Column(db.DateTime, nullable=True)
    last_login_at = db.Column(db.DateTime, nullable=True)

    created_at = db.Column(db.DateTime, default=lambda: utcnow(), nullable=False)
    updated_at = db.Column(
        db.DateTime, default=lambda: utcnow(),
        onupdate=lambda: utcnow(), nullable=False,
    )

    def to_public_dict(self) -> dict:
        return {
            "id": self.id,
            "username": self.username,
            "display_name": self.display_name if not self.is_anonymous_profile else "Anonymous",
            "role": self.role,
            "mfa_enabled": self.mfa_enabled,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
