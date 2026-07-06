"""Seeds a fresh database with demo accounts for local development.

Never run against a production database - passwords here are well-known and
meant only for exercising the app locally. Usage: `python -m backend.database.seed`.
"""
from app import create_app
from backend.auth.password_manager import hash_password
from backend.database.database import db
from backend.database.models.user import User
from backend.utils.constants import Roles

DEMO_ACCOUNTS = [
    ("demo_student", "student@example.org", Roles.STUDENT),
    ("demo_counselor", "counselor@example.org", Roles.COUNSELOR),
    ("demo_legal", "legal@example.org", Roles.LEGAL),
    ("demo_admin", "admin@example.org", Roles.ADMIN),
]
DEMO_PASSWORD = "ChangeMe123!"


def seed() -> None:
    app = create_app()
    with app.app_context():
        for username, email, role in DEMO_ACCOUNTS:
            if User.query.filter_by(username=username).first():
                continue
            user = User(username=username, email=email, role=role, password_hash=hash_password(DEMO_PASSWORD))
            db.session.add(user)
        db.session.commit()
        print(f"Seeded {len(DEMO_ACCOUNTS)} demo accounts (password: {DEMO_PASSWORD}).")


if __name__ == "__main__":
    seed()
