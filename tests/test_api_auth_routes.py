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
