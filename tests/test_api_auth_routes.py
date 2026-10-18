"""Tests that authentication endpoints fail closed by default."""
import importlib

from fastapi.testclient import TestClient


def test_auth_routes_are_not_mounted_by_default(monkeypatch):
    monkeypatch.delenv("OAC_ENABLE_TENANT_AUTH", raising=False)
    import api.main as api_main
    importlib.reload(api_main)
    client = TestClient(api_main.app)
    assert client.get("/health").status_code == 200
    assert client.post("/auth/login", json={
        "username_or_email": "demo", "password": "demo"
    }).status_code == 404


def test_auth_routes_require_explicit_opt_in(monkeypatch):
    monkeypatch.setenv("OAC_ENABLE_TENANT_AUTH", "false")
    import api.main as api_main
    importlib.reload(api_main)
    assert all(not route.path.startswith("/auth") for route in api_main.app.routes)

    monkeypatch.setenv("OAC_ENABLE_TENANT_AUTH", "true")
    importlib.reload(api_main)
    assert {"/auth/login", "/auth/me", "/auth/logout"}.issubset(
        {route.path for route in api_main.app.routes}
    )
    monkeypatch.delenv("OAC_ENABLE_TENANT_AUTH", raising=False)
    importlib.reload(api_main)


def test_login_route_supports_explicit_workshop_selection(monkeypatch):
    monkeypatch.setenv("OAC_ENABLE_TENANT_AUTH", "true")
    import api.main as api_main
    import api.auth_routes as auth_routes
    importlib.reload(api_main)

    class FakeService:
        def login(self, identity, password, workshop_id=None):
            assert identity == "owner"
            assert password == "password"
            if workshop_id is None:
                return {"selection_required": True, "workshops": [{"id": 7, "role": "owner"}]}
            return {"access_token": "opaque-token", "workshop": {"id": workshop_id}}

    monkeypatch.setattr(auth_routes, "service", FakeService())
    client = TestClient(api_main.app)
    selection = client.post("/auth/login", json={"username_or_email": "owner", "password": "password"})
    assert selection.status_code == 200
    assert selection.json()["selection_required"] is True

    chosen = client.post("/auth/login", json={
        "username_or_email": "owner", "password": "password", "workshop_id": 7
    })
    assert chosen.status_code == 200
    assert chosen.json()["workshop"]["id"] == 7

    monkeypatch.delenv("OAC_ENABLE_TENANT_AUTH", raising=False)
    importlib.reload(api_main)
