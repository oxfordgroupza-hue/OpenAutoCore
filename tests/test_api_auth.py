from fastapi.testclient import TestClient

from api import database
from api.main import app

client = TestClient(app)

USER = {
    "id": 17,
    "username": "demo-writer",
    "email": "writer@example.invalid",
    "user_type": "writer",
    "first_name": "Demo",
    "last_name": "Writer",
}


def test_health_is_available_without_database():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_login_returns_bearer_token_without_password_hash(monkeypatch):
    monkeypatch.setattr(database, "authenticate_user", lambda username, password: USER.copy())
    monkeypatch.setattr(database, "create_session", lambda user_id: "a" * 64)
    response = client.post(
        "/auth/login",
        json={"username_or_email": "demo-writer", "password": "example-password"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["access_token"] == "a" * 64
    assert body["token_type"] == "bearer"
    assert body["user"]["id"] == 17
    assert "password_hash" not in body["user"]


def test_invalid_credentials_are_rejected(monkeypatch):
    monkeypatch.setattr(database, "authenticate_user", lambda username, password: None)
    response = client.post(
        "/auth/login",
        json={"username_or_email": "unknown", "password": "wrong"},
    )
    assert response.status_code == 401


def test_me_requires_authentication():
    response = client.get("/auth/me")
    assert response.status_code == 401


def test_me_returns_only_public_user_fields(monkeypatch):
    monkeypatch.setattr(database, "get_user_for_token", lambda token: USER.copy())
    response = client.get("/auth/me", headers={"Authorization": "Bearer " + "b" * 64})
    assert response.status_code == 200
    assert response.json()["username"] == USER["username"]
    assert "password_hash" not in response.json()


def test_expired_or_unknown_token_is_rejected(monkeypatch):
    monkeypatch.setattr(database, "get_user_for_token", lambda token: None)
    response = client.get("/auth/me", headers={"Authorization": "Bearer " + "c" * 64})
    assert response.status_code == 401


def test_logout_revokes_current_token(monkeypatch):
    seen = []
    monkeypatch.setattr(database, "get_user_for_token", lambda token: USER.copy())
    monkeypatch.setattr(database, "delete_session", lambda token: seen.append(token))
    response = client.post("/auth/logout", headers={"Authorization": "Bearer " + "d" * 64})
    assert response.status_code == 204
    assert seen == ["d" * 64]


def test_database_unavailable_does_not_leak_details(monkeypatch):
    def unavailable(username, password):
        raise database.DatabaseUnavailable("secret database detail")

    monkeypatch.setattr(database, "authenticate_user", unavailable)
    response = client.post(
        "/auth/login",
        json={"username_or_email": "demo-writer", "password": "example-password"},
    )
    assert response.status_code == 503
    assert "secret database detail" not in response.text
