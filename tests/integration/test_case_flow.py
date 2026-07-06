from backend.database.database import db
from backend.database.models.user import User
from backend.auth.password_manager import hash_password
from backend.utils.constants import Roles


def _create_staff_user(app, username, role):
    with app.app_context():
        user = User(username=username, email=f"{username}@example.org", role=role,
                    password_hash=hash_password("Str0ngPass!word"))
        db.session.add(user)
        db.session.commit()


def _login(client, username):
    r = client.post("/api/auth/login", json={"username_or_email": username, "password": "Str0ngPass!word"})
    return r.get_json()["access_token"]


def test_case_creation_assigns_counselor_automatically(client, app, register_and_login):
    _create_staff_user(app, "counselor1", Roles.COUNSELOR)

    _, access_token, _ = register_and_login()
    headers = {"Authorization": f"Bearer {access_token}"}

    r = client.post("/api/cases", json={
        "title": "Doxxing incident",
        "description": "Someone posted my home address on a public forum.",
    }, headers=headers)
    assert r.status_code == 201
    case = r.get_json()["case"]
    assert case["assigned_counselor_id"] is not None
    assert case["category"] == "doxxing"


def test_counselor_can_update_assigned_case_status(client, app, register_and_login):
    _create_staff_user(app, "counselor1", Roles.COUNSELOR)
    _, student_token, _ = register_and_login()
    student_headers = {"Authorization": f"Bearer {student_token}"}

    r = client.post("/api/cases", json={"title": "t", "description": "d"}, headers=student_headers)
    case_id = r.get_json()["case"]["id"]

    counselor_token = _login(client, "counselor1")
    counselor_headers = {"Authorization": f"Bearer {counselor_token}"}

    r = client.patch(f"/api/cases/{case_id}/status", json={"status": "under_review"}, headers=counselor_headers)
    assert r.status_code == 200
    assert r.get_json()["case"]["status"] == "under_review"


def test_student_cannot_change_case_status(client, register_and_login):
    _, access_token, _ = register_and_login()
    headers = {"Authorization": f"Bearer {access_token}"}

    r = client.post("/api/cases", json={"title": "t", "description": "d"}, headers=headers)
    case_id = r.get_json()["case"]["id"]

    r = client.patch(f"/api/cases/{case_id}/status", json={"status": "closed"}, headers=headers)
    assert r.status_code == 403


def test_critical_severity_signal_detected(client, register_and_login):
    _, access_token, _ = register_and_login()
    headers = {"Authorization": f"Bearer {access_token}"}

    r = client.post("/api/cases", json={
        "title": "Threats",
        "description": "They messaged saying they will kill me if I don't stop posting.",
    }, headers=headers)
    assert r.get_json()["case"]["severity"] == "critical"
