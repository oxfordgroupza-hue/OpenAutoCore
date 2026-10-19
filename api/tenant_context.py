"""Authorization helpers for tenant-scoped business API routes.

These helpers intentionally derive workshop scope from the authenticated session,
never from a request body or query parameter. They are not business endpoints;
each endpoint must still validate ownership of every referenced parent/child row.
"""
from __future__ import annotations

from collections.abc import Callable
from typing import Any

from fastapi import Depends, HTTPException

from api.auth_routes import _current_session


def tenant_context(
    session: dict[str, Any] = Depends(_current_session),
) -> dict[str, Any]:
    """Return the authenticated tenant context or fail closed if it is incomplete."""
    try:
        user_id = int(session["user_id"])
        shop_id = int(session["shop_id"])
        role = str(session["workshop_role"]).strip().lower()
    except (KeyError, TypeError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    if user_id < 1 or shop_id < 1 or not role:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    return {"user_id": user_id, "shop_id": shop_id, "role": role}


def require_roles(*allowed_roles: str) -> Callable[..., dict[str, Any]]:
    """Build a dependency that enforces explicit workshop-role allowlists."""
    allowed = frozenset(str(role).strip().lower() for role in allowed_roles if str(role).strip())
    if not allowed:
        raise ValueError("At least one allowed role is required")

    def role_dependency(
        context: dict[str, Any] = Depends(tenant_context),
    ) -> dict[str, Any]:
        if context["role"] not in allowed:
            raise HTTPException(status_code=403, detail="Insufficient workshop permissions")
        return context

    return role_dependency
