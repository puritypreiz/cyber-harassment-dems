from flask import Blueprint, g, jsonify, request

from backend.auth.auth_service import AuthError, MFARequired, authenticate, logout, refresh_access_token, register_user
from backend.auth.jwt_handler import TokenError, decode_token
from backend.auth.mfa import build_provisioning_uri, encrypt_secret, generate_totp_secret, provisioning_qr_svg, verify_totp_code
from backend.auth.roles import login_required
from backend.chain_of_custody.audit_log import record as record_audit
from backend.database.database import db
from backend.security.csrf_protection import csrf_exempt
from backend.security.rate_limiter import limiter
from backend.utils.constants import AuditAction, Roles
from backend.utils.helpers import client_ip

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/register", methods=["POST"])
@csrf_exempt
@limiter.limit("10 per hour")
def register():
    data = request.get_json(silent=True) or {}
    role = data.get("role") if data.get("role") in (Roles.STUDENT,) else Roles.STUDENT
    try:
        user = register_user(data.get("username", ""), data.get("email", ""), data.get("password", ""), role=role)
    except AuthError as exc:
        return jsonify({"error": exc.message}), exc.status_code

    record_audit(AuditAction.USER_REGISTERED, actor_id=user.id, entity_type="user", entity_id=user.id,
                 ip_address=client_ip())
    return jsonify({"user": user.to_public_dict()}), 201


@auth_bp.route("/login", methods=["POST"])
@csrf_exempt
@limiter.limit("10 per 5 minutes")
def login():
    data = request.get_json(silent=True) or {}
    try:
        user, access_token, refresh_token = authenticate(
            data.get("username_or_email", ""), data.get("password", ""), data.get("totp_code")
        )
    except MFARequired:
        return jsonify({"error": "mfa_code_required", "mfa_required": True}), 401
    except AuthError as exc:
        record_audit(AuditAction.USER_LOGIN_FAILED, actor_id=None, entity_type="user",
                     details={"attempted_identifier": data.get("username_or_email", "")}, ip_address=client_ip())
        return jsonify({"error": exc.message}), exc.status_code

    record_audit(AuditAction.USER_LOGIN, actor_id=user.id, entity_type="user", entity_id=user.id,
                 ip_address=client_ip())
    return jsonify({
        "user": user.to_public_dict(),
        "access_token": access_token,
        "refresh_token": refresh_token,
    })


@auth_bp.route("/refresh", methods=["POST"])
@csrf_exempt
@limiter.limit("30 per hour")
def refresh():
    data = request.get_json(silent=True) or {}
    try:
        access_token = refresh_access_token(data.get("refresh_token", ""))
    except AuthError as exc:
        return jsonify({"error": exc.message}), exc.status_code
    return jsonify({"access_token": access_token})


@auth_bp.route("/logout", methods=["POST"])
@csrf_exempt
@login_required
def logout_route():
    data = request.get_json(silent=True) or {}
    access_token = request.headers.get("Authorization", "").removeprefix("Bearer ").strip()
    access_payload = decode_token(access_token, expected_type="access")

    refresh_payload = None
    if data.get("refresh_token"):
        try:
            refresh_payload = decode_token(data["refresh_token"], expected_type="refresh")
        except TokenError:
            refresh_payload = None

    logout(access_payload, refresh_payload)
    return jsonify({"message": "Logged out."})


@auth_bp.route("/mfa/setup", methods=["POST"])
@csrf_exempt
@login_required
def mfa_setup():
    secret = generate_totp_secret()
    uri = build_provisioning_uri(secret, g.current_user.email)
    svg = provisioning_qr_svg(uri)

    g.current_user.mfa_secret_encrypted = encrypt_secret(secret)
    db.session.commit()

    return jsonify({"provisioning_uri": uri, "qr_svg": svg})


@auth_bp.route("/mfa/enable", methods=["POST"])
@csrf_exempt
@login_required
def mfa_enable():
    from backend.auth.mfa import decrypt_secret

    data = request.get_json(silent=True) or {}
    if not g.current_user.mfa_secret_encrypted:
        return jsonify({"error": "Call /mfa/setup first."}), 400

    secret = decrypt_secret(g.current_user.mfa_secret_encrypted)
    if not verify_totp_code(secret, data.get("totp_code", "")):
        return jsonify({"error": "Invalid verification code."}), 400

    g.current_user.mfa_enabled = True
    db.session.commit()
    return jsonify({"message": "MFA enabled."})


@auth_bp.route("/mfa/disable", methods=["POST"])
@csrf_exempt
@login_required
def mfa_disable():
    g.current_user.mfa_enabled = False
    g.current_user.mfa_secret_encrypted = None
    db.session.commit()
    return jsonify({"message": "MFA disabled."})


@auth_bp.route("/me", methods=["GET"])
@login_required
def me():
    return jsonify({"user": g.current_user.to_public_dict()})
