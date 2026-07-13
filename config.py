import base64
import os

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


def _require_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(
            f"Required environment variable '{name}' is not set. "
            "Copy .env.example to .env and configure it."
        )
    return value


def _load_evidence_key() -> bytes:
    raw = os.environ.get("EVIDENCE_ENCRYPTION_KEY")
    if not raw:
        raise RuntimeError(
            "EVIDENCE_ENCRYPTION_KEY is not set. Generate one with: "
            "python -c \"import base64,os;print(base64.b64encode(os.urandom(32)).decode())\""
        )
    key = base64.b64decode(raw)
    if len(key) != 32:
        raise RuntimeError("EVIDENCE_ENCRYPTION_KEY must decode to exactly 32 bytes (AES-256).")
    return key


class Config:
    ENV = os.environ.get("FLASK_ENV", "production")
    DEBUG = ENV == "development"
    TESTING = os.environ.get("TESTING", "false").lower() == "true"

    SECRET_KEY = os.environ.get("SECRET_KEY") or ("test-secret-key" if TESTING else _require_env("SECRET_KEY"))
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY") or (
        "test-jwt-secret" if TESTING else _require_env("JWT_SECRET_KEY")
    )
    JWT_ACCESS_TOKEN_MINUTES = int(os.environ.get("JWT_ACCESS_TOKEN_MINUTES", "15"))
    JWT_REFRESH_TOKEN_DAYS = int(os.environ.get("JWT_REFRESH_TOKEN_DAYS", "7"))

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'cyber_harassment_dems.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    EVIDENCE_ENCRYPTION_KEY = (
        os.urandom(32) if TESTING and not os.environ.get("EVIDENCE_ENCRYPTION_KEY") else _load_evidence_key()
    )
    QR_SIGNING_KEY = os.environ.get("QR_SIGNING_KEY") or ("test-qr-signing-key" if TESTING else _require_env("QR_SIGNING_KEY"))

    MAX_UPLOAD_MB = int(os.environ.get("MAX_UPLOAD_MB", "50"))
    MAX_CONTENT_LENGTH = MAX_UPLOAD_MB * 1024 * 1024

    STORAGE_DIR = os.path.join(BASE_DIR, "storage")
    ENCRYPTED_EVIDENCE_DIR = os.path.join(STORAGE_DIR, "encrypted_evidence")
    DECRYPTED_TEMP_DIR = os.path.join(STORAGE_DIR, "decrypted_temp")
    QR_CODE_DIR = os.path.join(STORAGE_DIR, "qr_codes")
    REPORTS_DIR = os.path.join(STORAGE_DIR, "reports")
    BACKUPS_DIR = os.path.join(STORAGE_DIR, "backups")

    ALLOWED_EVIDENCE_EXTENSIONS = {
        "png", "jpg", "jpeg", "gif", "webp", "pdf", "txt", "mp4", "mov", "mp3", "wav", "eml", "msg",
    }

    ALLOWED_MIME_TYPES = {
        "image/png", "image/jpeg", "image/gif", "image/webp",
        "application/pdf", "text/plain",
        "video/mp4", "video/quicktime",
        "audio/mpeg", "audio/wav", "audio/x-wav",
        "message/rfc822",
    }

    RATE_LIMIT_STORAGE_URI = os.environ.get("RATE_LIMIT_STORAGE_URI", "memory://")

    ALLOWED_ORIGINS = [o.strip() for o in os.environ.get("ALLOWED_ORIGINS", "").split(",") if o.strip()]

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = ENV != "development"

    DATA_RETENTION_DAYS_DEFAULT = int(os.environ.get("DATA_RETENTION_DAYS_DEFAULT", "1825"))  # 5 years

    NATIONAL_HOTLINE_NUMBER = os.environ.get("NATIONAL_HOTLINE_NUMBER", "WARIF 24 Hr Helpline: +234 809 210 0009")

    SMTP_HOST = os.environ.get("SMTP_HOST")
    SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
    SMTP_USERNAME = os.environ.get("SMTP_USERNAME")
    SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD")
    SMTP_SENDER = os.environ.get("SMTP_SENDER", "noreply@example.org")
    SMS_PROVIDER_API_KEY = os.environ.get("SMS_PROVIDER_API_KEY")


def get_config() -> type[Config]:
    return Config
