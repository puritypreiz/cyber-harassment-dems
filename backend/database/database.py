import os

from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
migrate = Migrate()


def init_db(app):
    db.init_app(app)
    migrate.init_app(app, db, directory=os.path.join(os.path.dirname(__file__), "migrations"))
    with app.app_context():
        # Import models so they are registered on the metadata before create_all.
        from backend.database.models import (  # noqa: F401
            audit_log,
            case,
            consent,
            evidence,
            notification,
            qr_code,
            user,
        )
        from backend.database import indexes  # noqa: F401

        db.create_all()
