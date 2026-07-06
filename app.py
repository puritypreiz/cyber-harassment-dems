import os

from flask import Flask, jsonify, render_template
from flask_cors import CORS
from werkzeug.exceptions import HTTPException

from backend.api.admin_routes import admin_bp, public_bp
from backend.api.auth_routes import auth_bp
from backend.api.evidence_routes import evidence_bp
from backend.api.harassment_routes import harassment_bp
from backend.api.qr_routes import qr_bp
from backend.api.reports_routes import reports_bp
from backend.database.database import init_db
from backend.security.csrf_protection import init_csrf
from backend.security.rate_limiter import init_rate_limiter
from backend.security.secure_headers import apply_secure_headers
from backend.utils.logger import get_app_logger, get_security_logger
from config import get_config


def _ensure_storage_dirs(config) -> None:
    for key in (
        "STORAGE_DIR", "ENCRYPTED_EVIDENCE_DIR", "DECRYPTED_TEMP_DIR",
        "QR_CODE_DIR", "REPORTS_DIR", "BACKUPS_DIR",
    ):
        os.makedirs(config[key], exist_ok=True)


def create_app(config_object=None):
    app = Flask(
        __name__,
        template_folder="frontend/templates",
        static_folder="frontend/static",
    )
    app.config.from_object(config_object or get_config())

    _ensure_storage_dirs(app.config)

    init_db(app)
    init_csrf(app)
    init_rate_limiter(app)
    CORS(app, resources={r"/api/*": {"origins": app.config["ALLOWED_ORIGINS"]}}, supports_credentials=False)

    app.register_blueprint(auth_bp)
    app.register_blueprint(evidence_bp)
    app.register_blueprint(harassment_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(qr_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(public_bp)

    app_logger = get_app_logger()
    security_logger = get_security_logger()

    @app.after_request
    def add_security_headers(response):
        return apply_secure_headers(response)

    @app.errorhandler(413)
    def too_large(_exc):
        return jsonify({"error": "Uploaded file exceeds the maximum allowed size."}), 413

    @app.errorhandler(HTTPException)
    def handle_http_exception(exc):
        if exc.code and exc.code >= 500:
            app_logger.error("Unhandled HTTP exception: %s", exc)
        return jsonify({"error": exc.description}), exc.code

    @app.errorhandler(Exception)
    def handle_unexpected_exception(exc):
        app_logger.exception("Unhandled exception")
        security_logger.warning("Unhandled exception surfaced to client: %s", type(exc).__name__)
        return jsonify({"error": "An unexpected error occurred."}), 500

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/login")
    def login_page():
        return render_template("login.html")

    @app.route("/register")
    def register_page():
        return render_template("register.html")

    @app.route("/dashboard")
    def dashboard_page():
        return render_template("dashboard.html")

    @app.route("/upload-evidence")
    def upload_evidence_page():
        return render_template("upload_evidence.html")

    @app.route("/evidence/<evidence_id>")
    def evidence_details_page(evidence_id):
        return render_template("evidence_details.html", evidence_id=evidence_id)

    @app.route("/admin")
    def admin_dashboard_page():
        return render_template("admin_dashboard.html")

    @app.route("/counselor")
    def counselor_dashboard_page():
        return render_template("counselor_dashboard.html")

    @app.route("/legal")
    def legal_dashboard_page():
        return render_template("legal_dashboard.html")

    @app.route("/reports")
    def reports_page():
        return render_template("reports.html")

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", 5000)), debug=app.config["DEBUG"])
