"""Opt-in authentication routes; require the gated tenant migration first."""
from __future__ import annotations

import os
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field

from api.database import connect_db
from api.tenant_auth import AuthenticationError, TenantAuthService

router = APIRouter(prefix="/auth", tags=["authentication"])
bearer = HTTPBearer(auto_error=False)
service = TenantAuthService(connect_db, session_days=1)


class LoginRequest(BaseModel):
    username_or_email: str = Field(min_length=1, max_length=254)
    password: str = Field(min_length=1, max_length=1024)
    workshop_id: int | None = Field(default=None, ge=1)


def _current_session(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
) -> dict:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Authentication required")
    try:
        session = service.resolve_session(credentials.credentials)
    except Exception:
        raise HTTPException(status_code=503, detail="Authentication service unavailable")
    if session is None:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    return session


@router.post("/login")
def login(payload: LoginRequest) -> dict:
    try:
        return service.login(payload.username_or_email, payload.password, payload.workshop_id)
    except AuthenticationError as exc:
        raise HTTPException(status_code=401, detail=str(exc))
    except Exception:
        raise HTTPException(status_code=503, detail="Authentication service unavailable")


@router.get("/me")
def me(session: Annotated[dict, Depends(_current_session)]) -> dict:
    return {
        "user": {
            "id": session["user_id"],
            "username": session["username"],
            "role": session["workshop_role"],
        },
        "workshop": {"id": session["shop_id"]},
    }


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
    _session: Annotated[dict, Depends(_current_session)],
) -> None:
    try:
        service.logout(credentials.credentials if credentials else "")
    except Exception:
        raise HTTPException(status_code=503, detail="Authentication service unavailable")
    return None


def enabled_by_environment() -> bool:
    """Require a deliberate opt-in; fail closed for every other value."""
    return os.getenv("OAC_ENABLE_TENANT_AUTH", "").strip().lower() in {"1", "true", "yes"}
