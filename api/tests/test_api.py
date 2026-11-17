import uuid


def _register_and_login(client) -> dict[str, str]:
    creds = {"email": f"{uuid.uuid4().hex[:8]}@test.fr", "password": "motdepasse123"}
    assert client.post("/auth/register", json=creds).status_code == 201
    token = client.post("/auth/login", json=creds).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok", "database": "up"}


def test_notes_require_auth(client):
    assert client.get("/notes").status_code == 401


def test_full_flow(client):
    headers = _register_and_login(client)
    r = client.post("/notes", json={"title": "Test", "content": "Hello"}, headers=headers)
    assert r.status_code == 201
    note_id = r.json()["id"]

    notes = client.get("/notes", headers=headers).json()
    assert [n["title"] for n in notes] == ["Test"]

    assert client.delete(f"/notes/{note_id}", headers=headers).status_code == 204
    assert client.get("/notes", headers=headers).json() == []


def test_user_cannot_delete_other_users_note(client):
    alice, bob = _register_and_login(client), _register_and_login(client)
    note_id = client.post("/notes", json={"title": "Privé"}, headers=alice).json()["id"]
    assert client.delete(f"/notes/{note_id}", headers=bob).status_code == 404


def test_duplicate_email_rejected(client):
    creds = {"email": "doublon@test.fr", "password": "motdepasse123"}
    client.post("/auth/register", json=creds)
    assert client.post("/auth/register", json=creds).status_code == 409


def test_cors_allows_client_only(client):
    ok = client.options("/notes", headers={"Origin": "http://localhost:5173", "Access-Control-Request-Method": "GET"})
    assert ok.headers.get("access-control-allow-origin") == "http://localhost:5173"
    bad = client.options("/notes", headers={"Origin": "https://evil.example", "Access-Control-Request-Method": "GET"})
    assert "access-control-allow-origin" not in bad.headers
