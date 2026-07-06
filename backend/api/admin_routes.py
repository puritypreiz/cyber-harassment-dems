from flask import Blueprint, current_app, g, jsonify, request

from backend.chain_of_custody.audit_log import verify_chain
from backend.chain_of_custody.digital_signature import get_public_key_pem
from backend.database.database import db
from backend.database.models.audit_log import AuditLog
from backend.database.models.user import User
from backend.auth.roles import login_required, roles_required
from backend.privacy.consent_manager import grant_consent, has_consent, revoke_consent
from backend.privacy.data_retention import find_cases_due_for_purge_review
from backend.privacy.privacy_policy import get_policy
from backend.security.csrf_protection import csrf_exempt
from backend.utils.constants import Roles
from backend.utils.helpers import paginate_query
from backend.victim_support.hotline import get_hotline_info
from backend.victim_support.resources import get_resources_for_category

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")
public_bp = Blueprint("public", __name__, url_prefix="/api")


@admin_bp.route("/users", methods=["GET"])
@roles_required(Roles.ADMIN)
def list_users_route():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    items, meta = paginate_query(User.query.order_by(User.created_at.desc()), page, per_page)
    return jsonify({"users": [u.to_public_dict() for u in items], "meta": meta})


@admin_bp.route("/users/<user_id>/role", methods=["PATCH"])
@csrf_exempt
@roles_required(Roles.ADMIN)
def update_user_role_route(user_id):
    user = db.session.get(User, user_id)
    if user is None:
        return jsonify({"error": "User not found."}), 404

    data = request.get_json(silent=True) or {}
    role = data.get("role")
    if role not in Roles.ALL:
        return jsonify({"error": f"Role must be one of: {', '.join(Roles.ALL)}."}), 400

    user.role = role
    db.session.commit()
    return jsonify({"user": user.to_public_dict()})


@admin_bp.route("/users/<user_id>/deactivate", methods=["POST"])
@csrf_exempt
@roles_required(Roles.ADMIN)
def deactivate_user_route(user_id):
    user = db.session.get(User, user_id)
    if user is None:
        return jsonify({"error": "User not found."}), 404
    user.is_active = False
    db.session.commit()
    return jsonify({"user": user.to_public_dict()})


@admin_bp.route("/audit-log", methods=["GET"])
@roles_required(Roles.ADMIN, Roles.LEGAL)
def list_audit_log_route():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 50, type=int)
    items, meta = paginate_query(AuditLog.query.order_by(AuditLog.created_at.desc()), page, per_page)
    return jsonify({"entries": [e.to_dict() for e in items], "meta": meta})


@admin_bp.route("/audit-log/verify", methods=["GET"])
@roles_required(Roles.ADMIN, Roles.LEGAL)
def verify_audit_chain_route():
    entries = AuditLog.query.order_by(AuditLog.created_at.asc()).all()
    return jsonify({"results": verify_chain(entries)})


@admin_bp.route("/signing-public-key", methods=["GET"])
@login_required
def signing_public_key_route():
    return jsonify({"public_key_pem": get_public_key_pem(current_app.config["STORAGE_DIR"])})


@admin_bp.route("/retention/review-candidates", methods=["GET"])
@roles_required(Roles.ADMIN, Roles.LEGAL)
def retention_review_candidates_route():
    candidates = find_cases_due_for_purge_review()
    return jsonify({"cases": [c.to_dict() for c in candidates]})


@public_bp.route("/privacy-policy", methods=["GET"])
def privacy_policy_route():
    return jsonify(get_policy())


@public_bp.route("/support/hotline", methods=["GET"])
def hotline_route():
    return jsonify(get_hotline_info())


@public_bp.route("/support/resources", methods=["GET"])
def support_resources_route():
    category = request.args.get("category")
    return jsonify({"resources": get_resources_for_category(category)})


@public_bp.route("/consent", methods=["POST"])
@csrf_exempt
@login_required
def grant_consent_route():
    data = request.get_json(silent=True) or {}
    consent_type = data.get("consent_type")
    consent = grant_consent(g.current_user, consent_type)
    return jsonify({"consent": consent.to_dict()})


@public_bp.route("/consent/<consent_type>", methods=["DELETE"])
@csrf_exempt
@login_required
def revoke_consent_route(consent_type):
    consent = revoke_consent(g.current_user, consent_type)
    if consent is None:
        return jsonify({"error": "No such consent record."}), 404
    return jsonify({"consent": consent.to_dict()})


@public_bp.route("/consent/<consent_type>", methods=["GET"])
@login_required
def check_consent_route(consent_type):
    return jsonify({"granted": has_consent(g.current_user, consent_type)})
