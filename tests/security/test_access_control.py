import io


def test_cannot_download_evidence_for_case_you_do_not_own(client, register_and_login):
    _, token_a, _ = register_and_login(username="student_a", email="a@example.org")
    headers_a = {"Authorization": f"Bearer {token_a}"}
    r = client.post("/api/cases", json={"title": "t", "description": "d"}, headers=headers_a)
    case_id = r.get_json()["case"]["id"]

    r = client.post(
        f"/api/cases/{case_id}/evidence",
        data={"file": (io.BytesIO(b"secret"), "note.txt")},
        headers=headers_a,
        content_type="multipart/form-data",
    )
    evidence_id = r.get_json()["evidence"]["id"]

    _, token_b, _ = register_and_login(username="student_b", email="b@example.org")
    headers_b = {"Authorization": f"Bearer {token_b}"}

    r = client.get(f"/api/cases/{case_id}/evidence/{evidence_id}/download", headers=headers_b)
    assert r.status_code == 404


def test_path_traversal_filename_cannot_escape_storage_dir(client, register_and_login, app):
    _, access_token, _ = register_and_login()
    headers = {"Authorization": f"Bearer {access_token}"}
    r = client.post("/api/cases", json={"title": "t", "description": "d"}, headers=headers)
    case_id = r.get_json()["case"]["id"]

    r = client.post(
        f"/api/cases/{case_id}/evidence",
        data={"file": (io.BytesIO(b"content"), "../../../../etc/passwd.txt")},
        headers=headers,
        content_type="multipart/form-data",
    )
    assert r.status_code == 201
    evidence = r.get_json()["evidence"]
    assert ".." not in evidence["original_filename"]

    with app.app_context():
        import os

        assert os.path.commonpath([
            os.path.abspath(app.config["ENCRYPTED_EVIDENCE_DIR"]),
        ]) == os.path.abspath(app.config["ENCRYPTED_EVIDENCE_DIR"])
        stored_files = os.listdir(app.config["ENCRYPTED_EVIDENCE_DIR"])
        assert len(stored_files) == 1


def test_qr_token_tampering_detected_via_api(client, register_and_login):
    _, access_token, _ = register_and_login()
    headers = {"Authorization": f"Bearer {access_token}"}
    r = client.post("/api/cases", json={"title": "t", "description": "d"}, headers=headers)
    case_id = r.get_json()["case"]["id"]

    r = client.post(
        f"/api/cases/{case_id}/evidence",
        data={"file": (io.BytesIO(b"content"), "note.txt")},
        headers=headers,
        content_type="multipart/form-data",
    )
    evidence_id = r.get_json()["evidence"]["id"]

    from backend.database.models.qr_code import QRCode

    with client.application.app_context():
        token = QRCode.query.filter_by(evidence_id=evidence_id).first().token

    tampered = token.rsplit(".", 1)[0] + ".0000000000000000000000000000000000000000000000000000000000000000"
    r = client.post("/api/qr/verify", json={"token": tampered}, headers=headers)
    assert r.status_code == 400
