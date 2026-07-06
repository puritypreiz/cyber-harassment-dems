import base64
import os
import shutil
import tempfile

import pytest


@pytest.fixture()
def app():
    storage_dir = tempfile.mkdtemp()
    os.environ["TESTING"] = "true"
    os.environ["FLASK_ENV"] = "development"
    os.environ["EVIDENCE_ENCRYPTION_KEY"] = base64.b64encode(os.urandom(32)).decode()

    from app import create_app
    from config import Config

    class TestConfig(Config):
        TESTING = True
        SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
        STORAGE_DIR = storage_dir
        ENCRYPTED_EVIDENCE_DIR = os.path.join(storage_dir, "encrypted_evidence")
        DECRYPTED_TEMP_DIR = os.path.join(storage_dir, "decrypted_temp")
        QR_CODE_DIR = os.path.join(storage_dir, "qr_codes")
        REPORTS_DIR = os.path.join(storage_dir, "reports")
        BACKUPS_DIR = os.path.join(storage_dir, "backups")
        RATELIMIT_ENABLED = False

    flask_app = create_app(TestConfig)
    yield flask_app
    shutil.rmtree(storage_dir, ignore_errors=True)


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def register_and_login(client):
    def _do(username="jane_doe", email="jane@example.org", password="Str0ngPass!word", role=None):
        client.post("/api/auth/register", json={"username": username, "email": email, "password": password})
        resp = client.post("/api/auth/login", json={"username_or_email": username, "password": password})
        data = resp.get_json()
        return data["user"], data["access_token"], data["refresh_token"]

    return _do
