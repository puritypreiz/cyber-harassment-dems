from flask import Blueprint, g, jsonify, request

from backend.database.database import db
from backend.database.models.case import Case
from backend.database.models.user import User
from backend.harassment.case_service import CaseError, assign_counselor, assign_legal, create_case, update_status
from backend.harassment.timeline import build_case_timeline
from backend.security.access_control import can_access_case, can_modify_case
from backend.security.csrf_protection import csrf_exempt
from backend.security.input_validation import ValidationError, require_fields, sanitize_choice, sanitize_text
from backend.security.rate_limiter import limiter
from backend.auth.roles import login_required, roles_required
from backend.utils.constants import CaseStatus, HarassmentCategory, Roles
from backend.utils.helpers import client_ip, paginate_query
from backend.victim_support.counselor_assignment import find_least_loaded_counselor
from backend.victim_support.support_plan import build_support_plan

harassment_bp = Blueprint("harassment", __name__, url_prefix="/api/cases")


@harassment_bp.route("", methods=["POST"])
@csrf_exempt
@login_required
@limiter.limit("20 per hour")
def create_case_route():
    data = request.get_json(silent=True) or {}
    try:
        require_fields(data, ["title", "description"])
        title = sanitize_text(data["title"], "title", max_length=200)
        description = sanitize_text(data["description"], "description", max_length=5000)
        category = data.get("category") if data.get("category") in HarassmentCategory.ALL else None
    except ValidationError as exc:
        return jsonify({"errors": exc.errors}), 400

    case = create_case(
        g.current_user, title, description, category,
        is_anonymous=bool(data.get("is_anonymous")), ip_address=client_ip(),
    )

    counselor = find_least_loaded_counselor()
    if counselor:
        assign_counselor(case, counselor, g.current_user, ip_address=client_ip())

    return jsonify({"case": case.to_dict(), "support_plan": build_support_plan(case)}), 201


@harassment_bp.route("", methods=["GET"])
@login_required
def list_cases_route():
    query = Case.query
    if g.current_user.role == Roles.STUDENT:
        query = query.filter_by(reporter_id=g.current_user.id)
    elif g.current_user.role == Roles.COUNSELOR:
        query = query.filter_by(assigned_counselor_id=g.current_user.id)
    elif g.current_user.role == Roles.LEGAL:
        query = query.filter_by(assigned_legal_id=g.current_user.id)
    # admin sees all

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    items, meta = paginate_query(query.order_by(Case.created_at.desc()), page, per_page)
    return jsonify({"cases": [c.to_dict() for c in items], "meta": meta})


@harassment_bp.route("/<case_id>", methods=["GET"])
@login_required
def get_case_route(case_id):
    case = db.session.get(Case, case_id)
    if case is None or not can_access_case(g.current_user, case):
        return jsonify({"error": "Case not found."}), 404
    return jsonify({"case": case.to_dict()})


@harassment_bp.route("/<case_id>/status", methods=["PATCH"])
@csrf_exempt
@login_required
def update_case_status_route(case_id):
    case = db.session.get(Case, case_id)
    if case is None or not can_access_case(g.current_user, case):
        return jsonify({"error": "Case not found."}), 404
    if not can_modify_case(g.current_user, case):
        return jsonify({"error": "You do not have permission to modify this case."}), 403

    data = request.get_json(silent=True) or {}
    try:
        new_status = sanitize_choice(data.get("status"), "status", CaseStatus.ALL)
    except ValidationError as exc:
        return jsonify({"errors": exc.errors}), 400

    try:
        case = update_status(case, new_status, g.current_user, ip_address=client_ip())
    except CaseError as exc:
        return jsonify({"error": exc.message}), exc.status_code
    return jsonify({"case": case.to_dict()})


@harassment_bp.route("/<case_id>/assign-counselor", methods=["POST"])
@csrf_exempt
@roles_required(Roles.ADMIN, Roles.COUNSELOR)
def assign_counselor_route(case_id):
    case = db.session.get(Case, case_id)
    if case is None:
        return jsonify({"error": "Case not found."}), 404

    data = request.get_json(silent=True) or {}
    counselor = db.session.get(User, data.get("counselor_id", ""))
    if counselor is None:
        return jsonify({"error": "Counselor not found."}), 404

    try:
        case = assign_counselor(case, counselor, g.current_user, ip_address=client_ip())
    except CaseError as exc:
        return jsonify({"error": exc.message}), exc.status_code
    return jsonify({"case": case.to_dict()})


@harassment_bp.route("/<case_id>/assign-legal", methods=["POST"])
@csrf_exempt
@roles_required(Roles.ADMIN, Roles.LEGAL)
def assign_legal_route(case_id):
    case = db.session.get(Case, case_id)
    if case is None:
        return jsonify({"error": "Case not found."}), 404

    data = request.get_json(silent=True) or {}
    legal_user = db.session.get(User, data.get("legal_id", ""))
    if legal_user is None:
        return jsonify({"error": "Legal-team user not found."}), 404

    try:
        case = assign_legal(case, legal_user, g.current_user, ip_address=client_ip())
    except CaseError as exc:
        return jsonify({"error": exc.message}), exc.status_code
    return jsonify({"case": case.to_dict()})


@harassment_bp.route("/<case_id>/timeline", methods=["GET"])
@login_required
def case_timeline_route(case_id):
    case = db.session.get(Case, case_id)
    if case is None or not can_access_case(g.current_user, case):
        return jsonify({"error": "Case not found."}), 404
    return jsonify({"timeline": build_case_timeline(case)})


@harassment_bp.route("/<case_id>/support-plan", methods=["GET"])
@login_required
def case_support_plan_route(case_id):
    case = db.session.get(Case, case_id)
    if case is None or not can_access_case(g.current_user, case):
        return jsonify({"error": "Case not found."}), 404
    return jsonify({"support_plan": build_support_plan(case)})
