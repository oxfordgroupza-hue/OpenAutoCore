"""Unit tests for tenant context and explicit role allowlists."""
import pytest
from fastapi import HTTPException

from api.tenant_context import require_roles, tenant_context


def test_tenant_context_normalizes_authenticated_session():
    context = tenant_context({
        "user_id": 12,
        "shop_id": 4,
        "workshop_role": "Manager",
        "username": "manager",
    })
    assert context == {"user_id": 12, "shop_id": 4, "role": "manager"}


@pytest.mark.parametrize("session", [
    {},
    {"user_id": 1, "shop_id": 1},
    {"user_id": "bad", "shop_id": 1, "workshop_role": "owner"},
    {"user_id": 1, "shop_id": 0, "workshop_role": "owner"},
    {"user_id": 1, "shop_id": 1, "workshop_role": " "},
])
def test_tenant_context_rejects_incomplete_or_invalid_session(session):
    with pytest.raises(HTTPException) as error:
        tenant_context(session)
    assert error.value.status_code == 401


def test_role_dependency_accepts_only_explicit_allowed_role():
    dependency = require_roles("owner", "manager")
    assert dependency({"user_id": 1, "shop_id": 8, "role": "manager"})["shop_id"] == 8

    with pytest.raises(HTTPException) as error:
        dependency({"user_id": 1, "shop_id": 8, "role": "technician"})
    assert error.value.status_code == 403


def test_role_dependency_requires_nonempty_allowlist():
    with pytest.raises(ValueError):
        require_roles()
