from backend.database.database import db
from backend.database.models.user import User
from backend.auth.password_manager import hash_password
from backend.utils.constants import Roles


def _create_and_login(client, app, username, role):
    with app.app_context():
        user = User(username=username, email=f"{username}@example.org", role=role,
                    password_hash=hash_password("Str0ngPass!word"))
        db.session.add(user)
        db.session.commit()
    r = client.post("/api/auth/login", json={"username_or_email": username, "password": "Str0ngPass!word"})
    return r.get_json()["access_token"]


def test_student_cannot_access_admin_routes(client, register_and_login):
    _, access_token, _ = register_and_login()
    r = client.get("/api/admin/users", headers={"Authorization": f"Bearer {access_token}"})
    assert r.status_code == 403


def test_admin_can_list_users(client, app):
    token = _create_and_login(client, app, "admin1", Roles.ADMIN)
    r = client.get("/api/admin/users", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert any(u["username"] == "admin1" for u in r.get_json()["users"])


def test_audit_chain_verification_passes_after_activity(client, app, register_and_login):
    _, access_token, _ = register_and_login()
    headers = {"Authorization": f"Bearer {access_token}"}
    client.post("/api/cases", json={"title": "t", "description": "d"}, headers=headers)

    admin_token = _create_and_login(client, app, "admin1", Roles.ADMIN)
    r = client.get("/api/admin/audit-log/verify", headers={"Authorization": f"Bearer {admin_token}"})
    assert r.status_code == 200
    results = r.get_json()["results"]
    assert len(results) > 0
    assert all(entry["signature_valid"] for entry in results)
    assert all(entry["chain_linkage_valid"] for entry in results)


def test_legal_can_export_case_report(client, app, register_and_login):
    _, access_token, _ = register_and_login()
    headers = {"Authorization": f"Bearer {access_token}"}
    r = client.post("/api/cases", json={"title": "t", "description": "d"}, headers=headers)
    case_id = r.get_json()["case"]["id"]

    legal_token = _create_and_login(client, app, "legal1", Roles.LEGAL)
    with app.app_context():
        legal_user = User.query.filter_by(username="legal1").first()
        legal_id = legal_user.id

    legal_headers = {"Authorization": f"Bearer {legal_token}"}
    r = client.post(f"/api/cases/{case_id}/assign-legal", json={"legal_id": legal_id}, headers=legal_headers)
    assert r.status_code == 200

    r = client.get(f"/api/cases/{case_id}/report", headers=legal_headers)
    assert r.status_code == 200
    assert r.content_type == "application/pdf"
