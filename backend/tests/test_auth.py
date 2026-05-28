"""
Auth critical path: register, login, and token-protected access.
"""


def test_register_success(client):
    resp = client.post("/api/auth/register", json={"email": "new@example.com", "password": "password123"})
    assert resp.status_code == 201
    assert resp.json()["email"] == "new@example.com"
    assert "password" not in resp.json()


def test_register_duplicate_email(client):
    client.post("/api/auth/register", json={"email": "dup@example.com", "password": "password123"})
    resp = client.post("/api/auth/register", json={"email": "dup@example.com", "password": "password123"})
    assert resp.status_code == 400


def test_register_invalid_email(client):
    resp = client.post("/api/auth/register", json={"email": "not-an-email", "password": "password123"})
    assert resp.status_code == 422


def test_register_password_too_short(client):
    resp = client.post("/api/auth/register", json={"email": "short@example.com", "password": "abc"})
    assert resp.status_code == 422


def test_login_success(client):
    client.post("/api/auth/register", json={"email": "user@example.com", "password": "password123"})
    resp = client.post("/api/auth/login", json={"email": "user@example.com", "password": "password123"})
    assert resp.status_code == 200
    assert "access_token" in resp.json()
    assert resp.json()["token_type"] == "bearer"


def test_login_wrong_password(client):
    client.post("/api/auth/register", json={"email": "user@example.com", "password": "password123"})
    resp = client.post("/api/auth/login", json={"email": "user@example.com", "password": "wrongpassword"})
    assert resp.status_code == 401


def test_login_unknown_email(client):
    resp = client.post("/api/auth/login", json={"email": "ghost@example.com", "password": "password123"})
    assert resp.status_code == 401


def test_protected_route_without_token(client):
    # FastAPI's HTTPBearer returns 401 (not 403) when the Authorization header is absent
    resp = client.get("/api/todos")
    assert resp.status_code == 401


def test_protected_route_with_invalid_token(client):
    resp = client.get("/api/todos", headers={"Authorization": "Bearer garbage"})
    assert resp.status_code == 401
