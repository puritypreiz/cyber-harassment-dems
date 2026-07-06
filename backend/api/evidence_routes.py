from flask import Blueprint, Response, g, jsonify, request

from backend.chain_of_custody.audit_log import record as record_audit
from backend.database.database import db
from backend.database.models.case import Case
from backend.database.models.evidence import Evidence
from backend.evidence.evidence_service import EvidenceError, decrypt_evidence_bytes, upload_evidence, verify_integrity
from backend.security.access_control import can_access_case
from backend.security.csrf_protection import csrf_exempt
from backend.security.rate_limiter import limiter
from backend.auth.roles import login_required
from backend.utils.constants import AuditAction
from backend.utils.helpers import client_ip

evidence_bp = Blueprint("evidence", __name__, url_prefix="/api/cases/<case_id>/evidence")


def _load_case_or_404(case_id):
    case = db.session.get(Case, case_id)
    if case is None or not can_access_case(g.current_user, case):
        return None
    return case


@evidence_bp.route("", methods=["POST"])
@csrf_exempt
@login_required
@limiter.limit("30 per hour")
def upload_evidence_route(case_id):
    case = _load_case_or_404(case_id)
    if case is None:
        return jsonify({"error": "Case not found."}), 404

    uploaded_file = request.files.get("file")
    if uploaded_file is None:
        return jsonify({"error": "No file provided."}), 400

    file_bytes = uploaded_file.read()
    try:
        evidence = upload_evidence(
            case, g.current_user, uploaded_file.filename, file_bytes,
            request.form.get("description"), ip_address=client_ip(),
        )
    except EvidenceError as exc:
        return jsonify({"error": exc.message}), exc.status_code

    return jsonify({"evidence": evidence.to_dict()}), 201


@evidence_bp.route("", methods=["GET"])
@login_required
def list_evidence_route(case_id):
    case = _load_case_or_404(case_id)
    if case is None:
        return jsonify({"error": "Case not found."}), 404

    items = Evidence.query.filter_by(case_id=case.id).order_by(Evidence.uploaded_at.desc()).all()
    return jsonify({"evidence": [item.to_dict() for item in items]})


@evidence_bp.route("/<evidence_id>", methods=["GET"])
@login_required
def get_evidence_route(case_id, evidence_id):
    case = _load_case_or_404(case_id)
    if case is None:
        return jsonify({"error": "Case not found."}), 404

    evidence = Evidence.query.filter_by(id=evidence_id, case_id=case.id).first()
    if evidence is None:
        return jsonify({"error": "Evidence not found."}), 404

    record_audit(AuditAction.EVIDENCE_VIEWED, actor_id=g.current_user.id, entity_type="evidence",
                 entity_id=evidence.id, ip_address=client_ip())
    return jsonify({"evidence": evidence.to_dict()})


@evidence_bp.route("/<evidence_id>/download", methods=["GET"])
@login_required
@limiter.limit("60 per hour")
def download_evidence_route(case_id, evidence_id):
    case = _load_case_or_404(case_id)
    if case is None:
        return jsonify({"error": "Case not found."}), 404

    evidence = Evidence.query.filter_by(id=evidence_id, case_id=case.id).first()
    if evidence is None:
        return jsonify({"error": "Evidence not found."}), 404

    try:
        plaintext = decrypt_evidence_bytes(evidence)
    except Exception:
        return jsonify({"error": "Evidence could not be decrypted; integrity check required."}), 500

    record_audit(AuditAction.EVIDENCE_DOWNLOADED, actor_id=g.current_user.id, entity_type="evidence",
                 entity_id=evidence.id, ip_address=client_ip())

    return Response(
        plaintext,
        mimetype=evidence.mime_type,
        headers={"Content-Disposition": f'attachment; filename="{evidence.original_filename}"'},
    )


@evidence_bp.route("/<evidence_id>/verify", methods=["POST"])
@csrf_exempt
@login_required
def verify_evidence_route(case_id, evidence_id):
    case = _load_case_or_404(case_id)
    if case is None:
        return jsonify({"error": "Case not found."}), 404

    evidence = Evidence.query.filter_by(id=evidence_id, case_id=case.id).first()
    if evidence is None:
        return jsonify({"error": "Evidence not found."}), 404

    is_valid = verify_integrity(evidence, actor_id=g.current_user.id)
    return jsonify({"is_verified": is_valid, "evidence": evidence.to_dict()})
