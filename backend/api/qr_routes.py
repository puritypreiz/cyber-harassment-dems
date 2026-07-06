import os

from flask import Blueprint, current_app, g, jsonify, request, send_file

from backend.chain_of_custody.audit_log import record as record_audit
from backend.database.database import db
from backend.database.models.case import Case
from backend.database.models.evidence import Evidence
from backend.evidence.evidence_service import decrypt_evidence_bytes
from backend.evidence.hash_verify import hashes_match, sha256_of_bytes
from backend.evidence.qr_verifier import QRVerificationError, parse_and_verify_token
from backend.security.access_control import can_access_case
from backend.security.csrf_protection import csrf_exempt
from backend.auth.roles import login_required
from backend.utils.constants import AuditAction
from backend.utils.helpers import client_ip, utcnow

qr_bp = Blueprint("qr", __name__, url_prefix="/api/qr")


@qr_bp.route("/evidence/<evidence_id>/image", methods=["GET"])
@login_required
def get_qr_image_route(evidence_id):
    evidence = db.session.get(Evidence, evidence_id)
    if evidence is None:
        return jsonify({"error": "Evidence not found."}), 404

    case = db.session.get(Case, evidence.case_id)
    if case is None or not can_access_case(g.current_user, case):
        return jsonify({"error": "Evidence not found."}), 404

    if evidence.qr_code is None:
        return jsonify({"error": "No QR code has been generated for this evidence item."}), 404

    path = os.path.join(current_app.config["QR_CODE_DIR"], evidence.qr_code.image_filename)
    return send_file(path, mimetype="image/png")


@qr_bp.route("/verify", methods=["POST"])
@csrf_exempt
@login_required
def verify_qr_route():
    """Verifies a scanned QR token against the current state of the evidence file.

    Confirms both (a) the QR code was genuinely issued by this system (signature
    check) and (b) the evidence file has not been altered since the QR was
    generated (hash check).
    """
    data = request.get_json(silent=True) or {}
    token = data.get("token", "")
    if not token:
        return jsonify({"error": "A QR token is required."}), 400

    try:
        payload = parse_and_verify_token(token)
    except QRVerificationError as exc:
        return jsonify({"error": str(exc)}), 400

    evidence = db.session.get(Evidence, payload["evidence_id"])
    if evidence is None:
        return jsonify({"error": "Referenced evidence no longer exists."}), 404

    case = db.session.get(Case, evidence.case_id)
    if case is None or not can_access_case(g.current_user, case):
        return jsonify({"error": "You do not have permission to verify this evidence."}), 403

    try:
        current_hash = sha256_of_bytes(decrypt_evidence_bytes(evidence))
        hash_matches = hashes_match(payload["sha256"], current_hash)
    except Exception:
        hash_matches = False

    if evidence.qr_code:
        evidence.qr_code.scan_count += 1
        evidence.qr_code.last_scanned_at = utcnow()
        db.session.commit()

    record_audit(AuditAction.QR_SCANNED, actor_id=g.current_user.id, entity_type="evidence",
                 entity_id=evidence.id, details={"hash_matches": hash_matches}, ip_address=client_ip())

    return jsonify({
        "evidence_id": evidence.id,
        "case_id": evidence.case_id,
        "issued_at": payload["issued_at"],
        "hash_matches_current_file": hash_matches,
    })
