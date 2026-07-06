import io


def _create_case(client, headers):
    r = client.post("/api/cases", json={
        "title": "Harassment on Instagram",
        "description": "Someone created a fake account and is sending unwanted messages.",
    }, headers=headers)
    return r.get_json()["case"]


def test_upload_and_download_evidence(client, register_and_login):
    _, access_token, _ = register_and_login()
    headers = {"Authorization": f"Bearer {access_token}"}
    case = _create_case(client, headers)

    r = client.post(
        f"/api/cases/{case['id']}/evidence",
        data={"file": (io.BytesIO(b"screenshot content"), "screenshot.txt")},
        headers=headers,
        content_type="multipart/form-data",
    )
    assert r.status_code == 201
    evidence = r.get_json()["evidence"]
    assert evidence["sha256_hash"]
    assert evidence["is_verified"] is True

    r = client.get(f"/api/cases/{case['id']}/evidence/{evidence['id']}/download", headers=headers)
    assert r.status_code == 200
    assert r.data == b"screenshot content"


def test_evidence_encrypted_at_rest(client, register_and_login, app):
    _, access_token, _ = register_and_login()
    headers = {"Authorization": f"Bearer {access_token}"}
    case = _create_case(client, headers)

    r = client.post(
        f"/api/cases/{case['id']}/evidence",
        data={"file": (io.BytesIO(b"super secret evidence text"), "note.txt")},
        headers=headers,
        content_type="multipart/form-data",
    )
    evidence = r.get_json()["evidence"]

    with app.app_context():
        from backend.database.database import db
        from backend.database.models.evidence import Evidence
        import os

        record = db.session.get(Evidence, evidence["id"])
        path = os.path.join(app.config["ENCRYPTED_EVIDENCE_DIR"], record.stored_filename)
        with open(path, "rb") as f:
            on_disk = f.read()
        assert b"super secret evidence text" not in on_disk


def test_integrity_verification_endpoint(client, register_and_login):
    _, access_token, _ = register_and_login()
    headers = {"Authorization": f"Bearer {access_token}"}
    case = _create_case(client, headers)

    r = client.post(
        f"/api/cases/{case['id']}/evidence",
        data={"file": (io.BytesIO(b"content"), "note.txt")},
        headers=headers,
        content_type="multipart/form-data",
    )
    evidence = r.get_json()["evidence"]

    r = client.post(f"/api/cases/{case['id']}/evidence/{evidence['id']}/verify", headers=headers)
    assert r.status_code == 200
    assert r.get_json()["is_verified"] is True


def test_detects_corrupted_evidence(client, register_and_login, app):
    _, access_token, _ = register_and_login()
    headers = {"Authorization": f"Bearer {access_token}"}
    case = _create_case(client, headers)

    r = client.post(
        f"/api/cases/{case['id']}/evidence",
        data={"file": (io.BytesIO(b"content"), "note.txt")},
        headers=headers,
        content_type="multipart/form-data",
    )
    evidence = r.get_json()["evidence"]

    with app.app_context():
        from backend.database.database import db
        from backend.database.models.evidence import Evidence
        import os

        record = db.session.get(Evidence, evidence["id"])
        path = os.path.join(app.config["ENCRYPTED_EVIDENCE_DIR"], record.stored_filename)
        with open(path, "r+b") as f:
            f.seek(0)
            f.write(b"\x00")

    r = client.post(f"/api/cases/{case['id']}/evidence/{evidence['id']}/verify", headers=headers)
    assert r.status_code == 200
    assert r.get_json()["is_verified"] is False


def test_another_students_case_is_not_accessible(client, register_and_login):
    _, token_a, _ = register_and_login(username="student_a", email="a@example.org")
    headers_a = {"Authorization": f"Bearer {token_a}"}
    case = _create_case(client, headers_a)

    _, token_b, _ = register_and_login(username="student_b", email="b@example.org")
    headers_b = {"Authorization": f"Bearer {token_b}"}

    r = client.get(f"/api/cases/{case['id']}", headers=headers_b)
    assert r.status_code == 404


def test_qr_generated_and_verifiable(client, register_and_login):
    _, access_token, _ = register_and_login()
    headers = {"Authorization": f"Bearer {access_token}"}
    case = _create_case(client, headers)

    r = client.post(
        f"/api/cases/{case['id']}/evidence",
        data={"file": (io.BytesIO(b"content"), "note.txt")},
        headers=headers,
        content_type="multipart/form-data",
    )
    evidence_id = r.get_json()["evidence"]["id"]

    r = client.get(f"/api/qr/evidence/{evidence_id}/image", headers=headers)
    assert r.status_code == 200
    assert r.content_type == "image/png"
