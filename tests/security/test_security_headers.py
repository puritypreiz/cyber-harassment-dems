def test_security_headers_present(client):
    r = client.get("/")
    assert r.headers.get("X-Content-Type-Options") == "nosniff"
    assert r.headers.get("X-Frame-Options") == "DENY"
    assert "default-src 'self'" in r.headers.get("Content-Security-Policy", "")
    assert r.headers.get("Cache-Control") == "no-store"


def test_stack_traces_not_leaked_to_client(client, monkeypatch):
    # Force an unexpected exception inside a route and confirm the response body
    # contains only a generic message, never the exception details/traceback.
    import backend.api.auth_routes as auth_routes

    def boom(*args, **kwargs):
        raise RuntimeError("super secret internal detail")

    monkeypatch.setattr(auth_routes, "authenticate", boom)
    r = client.post("/api/auth/login", json={"username_or_email": "x", "password": "y"})
    assert r.status_code == 500
    assert "super secret internal detail" not in r.get_data(as_text=True)
