"""
CRUD critical path: create, read, update, delete todos with auth enforcement.
"""


def test_create_todo(auth_client):
    resp = auth_client.post("/api/todos", json={"title": "Buy milk"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Buy milk"
    assert data["completed"] is False
    assert data["due_date"] is None


def test_create_todo_with_due_date(auth_client):
    resp = auth_client.post("/api/todos", json={"title": "File taxes", "due_date": "2026-06-01T00:00:00Z"})
    assert resp.status_code == 201
    assert resp.json()["due_date"] is not None


def test_create_todo_empty_title(auth_client):
    resp = auth_client.post("/api/todos", json={"title": "   "})
    assert resp.status_code == 422


def test_create_todo_missing_title(auth_client):
    resp = auth_client.post("/api/todos", json={"description": "no title"})
    assert resp.status_code == 422


def test_list_todos_empty(auth_client):
    resp = auth_client.get("/api/todos")
    assert resp.status_code == 200
    assert resp.json() == []


def test_list_todos_returns_own_only(client):
    """Two users — each should only see their own todos."""
    client.post("/api/auth/register", json={"email": "alice@example.com", "password": "password123"})
    r = client.post("/api/auth/login", json={"email": "alice@example.com", "password": "password123"})
    alice_token = r.json()["access_token"]

    client.post("/api/auth/register", json={"email": "bob@example.com", "password": "password123"})
    r = client.post("/api/auth/login", json={"email": "bob@example.com", "password": "password123"})
    bob_token = r.json()["access_token"]

    client.post("/api/todos", json={"title": "Alice's todo"}, headers={"Authorization": f"Bearer {alice_token}"})
    client.post("/api/todos", json={"title": "Bob's todo"}, headers={"Authorization": f"Bearer {bob_token}"})

    alice_todos = client.get("/api/todos", headers={"Authorization": f"Bearer {alice_token}"}).json()
    bob_todos = client.get("/api/todos", headers={"Authorization": f"Bearer {bob_token}"}).json()

    assert len(alice_todos) == 1 and alice_todos[0]["title"] == "Alice's todo"
    assert len(bob_todos) == 1 and bob_todos[0]["title"] == "Bob's todo"


def test_update_todo_title(auth_client):
    todo_id = auth_client.post("/api/todos", json={"title": "Original"}).json()["id"]
    resp = auth_client.put(f"/api/todos/{todo_id}", json={"title": "Updated"})
    assert resp.status_code == 200
    assert resp.json()["title"] == "Updated"


def test_update_todo_mark_complete(auth_client):
    todo_id = auth_client.post("/api/todos", json={"title": "Do laundry"}).json()["id"]
    resp = auth_client.put(f"/api/todos/{todo_id}", json={"completed": True})
    assert resp.status_code == 200
    assert resp.json()["completed"] is True


def test_update_todo_clear_due_date(auth_client):
    todo_id = auth_client.post(
        "/api/todos", json={"title": "Task", "due_date": "2026-06-01T00:00:00Z"}
    ).json()["id"]
    resp = auth_client.put(f"/api/todos/{todo_id}", json={"due_date": None})
    assert resp.status_code == 200
    assert resp.json()["due_date"] is None


def test_omitting_due_date_does_not_clear_it(auth_client):
    """
    Sending a PUT without due_date should leave the existing due date untouched.
    This is the model_fields_set behaviour: an omitted field is not the same as
    an explicit null. Without this distinction, updating the title would silently
    clear the due date and cancel the scheduled reminder.
    """
    created = auth_client.post(
        "/api/todos", json={"title": "Task", "due_date": "2026-06-01T00:00:00Z"}
    ).json()
    resp = auth_client.put(f"/api/todos/{created['id']}", json={"title": "Renamed"})
    assert resp.status_code == 200
    assert resp.json()["due_date"] == created["due_date"]
    assert resp.json()["title"] == "Renamed"


def test_update_nonexistent_todo(auth_client):
    resp = auth_client.put("/api/todos/9999", json={"title": "Ghost"})
    assert resp.status_code == 404


def test_update_another_users_todo(client):
    client.post("/api/auth/register", json={"email": "alice@example.com", "password": "password123"})
    r = client.post("/api/auth/login", json={"email": "alice@example.com", "password": "password123"})
    alice_headers = {"Authorization": f"Bearer {r.json()['access_token']}"}

    client.post("/api/auth/register", json={"email": "bob@example.com", "password": "password123"})
    r = client.post("/api/auth/login", json={"email": "bob@example.com", "password": "password123"})
    bob_headers = {"Authorization": f"Bearer {r.json()['access_token']}"}

    todo_id = client.post("/api/todos", json={"title": "Alice's"}, headers=alice_headers).json()["id"]
    resp = client.put(f"/api/todos/{todo_id}", json={"title": "Hijacked"}, headers=bob_headers)
    assert resp.status_code == 404


def test_delete_todo(auth_client):
    todo_id = auth_client.post("/api/todos", json={"title": "Temporary"}).json()["id"]
    resp = auth_client.delete(f"/api/todos/{todo_id}")
    assert resp.status_code == 204
    assert auth_client.get("/api/todos").json() == []


def test_delete_nonexistent_todo(auth_client):
    resp = auth_client.delete("/api/todos/9999")
    assert resp.status_code == 404


def test_delete_another_users_todo(client):
    client.post("/api/auth/register", json={"email": "alice@example.com", "password": "password123"})
    r = client.post("/api/auth/login", json={"email": "alice@example.com", "password": "password123"})
    alice_headers = {"Authorization": f"Bearer {r.json()['access_token']}"}

    client.post("/api/auth/register", json={"email": "bob@example.com", "password": "password123"})
    r = client.post("/api/auth/login", json={"email": "bob@example.com", "password": "password123"})
    bob_headers = {"Authorization": f"Bearer {r.json()['access_token']}"}

    todo_id = client.post("/api/todos", json={"title": "Alice's"}, headers=alice_headers).json()["id"]
    resp = client.delete(f"/api/todos/{todo_id}", headers=bob_headers)
    assert resp.status_code == 404
