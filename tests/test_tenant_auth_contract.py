"""Unit tests for tenant authentication service primitives."""
import hashlib

import bcrypt
import pytest

from api.tenant_auth import AuthenticationError, TenantAuthService


class FakeCursor:
    def __init__(self, connection):
        self.connection = connection
        self.rows = []
        self.row = None
        self.last_query = ""

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def execute(self, query, params=None):
        self.last_query = query
        self.connection.queries.append((query, params))
        if "JOIN workshop_memberships" in query and "SELECT u.id, u.username" in query:
            self.rows = self.connection.login_rows
        elif "SELECT u.id AS user_id" in query:
            self.row = self.connection.session_row
        else:
            self.row = None

    def fetchall(self):
        return self.rows

    def fetchone(self):
        return self.row


class FakeConnection:
    def __init__(self, login_rows=None, session_row=None):
        self.login_rows = login_rows or []
        self.session_row = session_row
        self.queries = []
        self.committed = False
        self.rolled_back = False
        self.closed = False

    def cursor(self, dictionary=False, **kwargs):
        return FakeCursor(self)

    def commit(self):
        self.committed = True

    def rollback(self):
        self.rolled_back = True

    def close(self):
        self.closed = True


def _row(password, shop_id=10, role="owner"):
    return {
        "id": 3,
        "username": "shopowner",
        "email": "owner@example.test",
        "password_hash": bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode(),
        "first_name": "Shop",
        "last_name": "Owner",
        "user_type": "manager",
        "shop_id": shop_id,
        "workshop_role": role,
    }


def test_login_returns_token_but_stores_only_digest():
    conn = FakeConnection(login_rows=[_row("correct horse")])
    result = TenantAuthService(lambda: conn).login("shopowner", "correct horse")

    assert result["token_type"] == "bearer"
    assert len(result["access_token"]) >= 40
    assert result["workshop"]["id"] == 10
    assert conn.committed
    insert = next((q, p) for q, p in conn.queries if "INSERT INTO user_sessions" in q)
    assert insert[1][0] == hashlib.sha256(result["access_token"].encode()).hexdigest()
    assert insert[1][0] != result["access_token"]


def test_invalid_credentials_are_rejected():
    conn = FakeConnection(login_rows=[_row("right password")])
    with pytest.raises(AuthenticationError, match="Invalid credentials"):
        TenantAuthService(lambda: conn).login("shopowner", "wrong password")
    assert conn.rolled_back


def test_unknown_user_is_rejected():
    conn = FakeConnection()
    with pytest.raises(AuthenticationError, match="Invalid credentials"):
        TenantAuthService(lambda: conn).login("unknown", "password")


def test_multiple_active_memberships_require_explicit_selection():
    row = _row("password")
    second = dict(row, shop_id=11, workshop_role="technician")
    conn = FakeConnection(login_rows=[row, second])
    result = TenantAuthService(lambda: conn).login("shopowner", "password")
    assert result["selection_required"] is True
    assert result["workshops"] == [
        {"id": 10, "role": "owner"},
        {"id": 11, "role": "technician"},
    ]
    assert not conn.queries or all("INSERT INTO user_sessions" not in q for q, _ in conn.queries)


def test_login_can_select_one_of_multiple_workshops():
    row = _row("password")
    second = dict(row, shop_id=11, workshop_role="technician")
    conn = FakeConnection(login_rows=[row, second])
    result = TenantAuthService(lambda: conn).login("shopowner", "password", shop_id=11)
    assert result["workshop"]["id"] == 11
    assert result["user"]["role"] == "technician"


def test_session_resolution_hashes_bearer_and_rechecks_membership():
    conn = FakeConnection(session_row={
        "user_id": 3, "username": "shopowner", "shop_id": 10,
        "workshop_role": "owner",
    })
    service = TenantAuthService(lambda: conn)
    token = "raw-secret-token"
    assert service.resolve_session(token)["shop_id"] == 10
    query, params = conn.queries[-1]
    assert params[0] == hashlib.sha256(token.encode()).hexdigest()
    assert "wm.status = 'active'" in query
    assert "s.expires_at > UTC_TIMESTAMP()" in query


def test_logout_revokes_only_digest():
    conn = FakeConnection()
    token = "raw-secret-token"
    TenantAuthService(lambda: conn).logout(token)
    query, params = conn.queries[-1]
    assert "DELETE FROM user_sessions" in query
    assert params[0] == hashlib.sha256(token.encode()).hexdigest()
    assert params[0] != token
    assert conn.committed


def test_session_lifetime_is_bounded():
    with pytest.raises(ValueError):
        TenantAuthService(lambda: FakeConnection(), session_days=30)
