import os

from flask import Blueprint, current_app, g, jsonify, send_file

from backend.chain_of_custody.audit_log import record as record_audit
from backend.chain_of_custody.evidence_history import get_case_history
from backend.chain_of_custody.export_report import write_case_report_pdf
from backend.database.database import db
from backend.database.models.case import Case
from backend.database.models.evidence import Evidence
from backend.security.access_control import can_access_case
from backend.auth.roles import login_required, roles_required
from backend.utils.constants import AuditAction, Roles
from backend.utils.helpers import client_ip

reports_bp = Blueprint("reports", __name__, url_prefix="/api/cases/<case_id>/report")


@reports_bp.route("", methods=["GET"])
@roles_required(Roles.ADMIN, Roles.LEGAL, Roles.COUNSELOR)
def export_case_report_route(case_id):
    case = db.session.get(Case, case_id)
    if case is None or not can_access_case(g.current_user, case):
        return jsonify({"error": "Case not found."}), 404

    evidence_items = Evidence.query.filter_by(case_id=case.id).order_by(Evidence.uploaded_at.asc()).all()
    audit_entries = get_case_history(case.id)

    output_path = os.path.join(current_app.config["REPORTS_DIR"], f"{case.case_number}_chain_of_custody.pdf")
    write_case_report_pdf(case, evidence_items, audit_entries, output_path, current_app.config["STORAGE_DIR"])

    record_audit(AuditAction.REPORT_EXPORTED, actor_id=g.current_user.id, entity_type="case",
                 entity_id=case.id, ip_address=client_ip())

    return send_file(output_path, mimetype="application/pdf", as_attachment=True,
                      download_name=os.path.basename(output_path))
