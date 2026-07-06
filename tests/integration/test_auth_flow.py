def test_register_login_me(client):
    r = client.post("/api/auth/register", json={
        "username": "jane_doe", "email": "jane@example.org", "password": "Str0ngPass!word",
    })
    assert r.status_code == 201

    r = client.post("/api/auth/login", json={
        "username_or_email": "jane_doe", "password": "Str0ngPass!word",
    })
    assert r.status_code == 200
    data = r.get_json()
    assert "access_token" in data and "refresh_token" in data

    r = client.get("/api/auth/me", headers={"Authorization": f"Bearer {data['access_token']}"})
    assert r.status_code == 200
    assert r.get_json()["user"]["username"] == "jane_doe"


def test_login_wrong_password_rejected(client):
    client.post("/api/auth/register", json={
        "username": "jane_doe", "email": "jane@example.org", "password": "Str0ngPass!word",
    })
    r = client.post("/api/auth/login", json={"username_or_email": "jane_doe", "password": "WrongPassword!1"})
    assert r.status_code == 401


def test_weak_password_rejected_on_register(client):
    r = client.post("/api/auth/register", json={
        "username": "weakuser", "email": "weak@example.org", "password": "weak",
    })
    assert r.status_code == 400


def test_duplicate_registration_rejected(client):
    payload = {"username": "jane_doe", "email": "jane@example.org", "password": "Str0ngPass!word"}
    client.post("/api/auth/register", json=payload)
    r = client.post("/api/auth/register", json=payload)
    assert r.status_code == 409


def test_account_lockout_after_repeated_failures(client):
    client.post("/api/auth/register", json={
        "username": "jane_doe", "email": "jane@example.org", "password": "Str0ngPass!word",
    })
    for _ in range(5):
        client.post("/api/auth/login", json={"username_or_email": "jane_doe", "password": "wrong"})
    r = client.post("/api/auth/login", json={"username_or_email": "jane_doe", "password": "Str0ngPass!word"})
    assert r.status_code == 423


def test_protected_route_requires_token(client):
    r = client.get("/api/auth/me")
    assert r.status_code == 401


def test_logout_revokes_access_token(client, register_and_login):
    _, access_token, refresh_token = register_and_login()
    headers = {"Authorization": f"Bearer {access_token}"}

    r = client.post("/api/auth/logout", json={"refresh_token": refresh_token}, headers=headers)
    assert r.status_code == 200

    r = client.get("/api/auth/me", headers=headers)
    assert r.status_code == 401
