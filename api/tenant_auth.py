"""Tenant-aware authentication primitives for the central API.

This module deliberately does not connect to a database at import time. The
caller supplies a connection factory so unit tests can run without MySQL and
the legacy desktop app remains unaffected.

The SQL expects the additive migration described in
docs/tenant-authentication-migration.md. Do not expose business endpoints until
that migration is reviewed, applied to a disposable test database, and tenant
isolation tests pass.
"""
from __future__ import annotations

import hashlib
import secrets
from typing import Any, Callable

import bcrypt


class AuthenticationError(Exception):
    """Raised when credentials or workshop membership are invalid."""


class TenantAuthService:
    """Authenticate a user and resolve an explicit active workshop membership."""

    def __init__(self, connection_factory: Callable[[], Any], *, session_days: int = 1):
        if not 1 <= session_days <= 7:
            raise ValueError("session_days must be between 1 and 7")
        self._connect = connection_factory
        self._session_days = session_days

    @staticmethod
    def _verify_password(plain_password: str, password_hash: str) -> bool:
        try:
            return bcrypt.checkpw(
                plain_password.encode("utf-8"),
                password_hash.encode("utf-8"),
            )
        except (ValueError, TypeError, UnicodeError):
            return False

    def login(self, username_or_email: str, plain_password: str) -> dict[str, Any]:
        """Create a short-lived random session only for an active membership.

        A user with multiple workshop memberships must select a workshop through
        a separate explicit flow; this method intentionally refuses ambiguity.
        """
        identity = (username_or_email or "").strip()
        if not identity or not plain_password:
            raise AuthenticationError("Invalid credentials")

        conn = self._connect()
        try:
            with conn.cursor(dictionary=True) as cur:
                cur.execute(
                    """
                    SELECT u.id, u.username, u.email, u.password_hash,
                           u.first_name, u.last_name, u.user_type,
                           wm.shop_id, wm.role AS workshop_role
                    FROM users AS u
                    JOIN workshop_memberships AS wm ON wm.user_id = u.id
                    JOIN shop_info AS si ON si.id = wm.shop_id
                    WHERE (u.username = %s OR u.email = %s)
                      AND wm.status = 'active'
                    """,
                    (identity, identity),
                )
                rows = list(cur.fetchall() or [])

            # Avoid leaking whether the account exists or has a membership.
            if not rows:
                raise AuthenticationError("Invalid credentials")
            password_hash = rows[0].get("password_hash") or ""
            if not self._verify_password(plain_password, password_hash):
                raise AuthenticationError("Invalid credentials")

            # Multiple active memberships require a deliberate workshop chooser.
            memberships = {
                (int(row["shop_id"]), str(row["workshop_role"]))
                for row in rows
            }
            if len(memberships) != 1:
                raise AuthenticationError("Workshop selection is required")

            row = rows[0]
            token = secrets.token_urlsafe(32)
            token_digest = hashlib.sha256(token.encode("utf-8")).hexdigest()
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO user_sessions
                        (token, user_id, shop_id, created_at, expires_at)
                    VALUES (%s, %s, %s, UTC_TIMESTAMP(),
                            DATE_ADD(UTC_TIMESTAMP(), INTERVAL %s DAY))
                    """,
                    (token_digest, int(row["id"]), int(row["shop_id"]), self._session_days),
                )
            conn.commit()
            return {
                "access_token": token,
                "token_type": "bearer",
                "expires_in": self._session_days * 86400,
                "user": {
                    "id": int(row["id"]),
                    "username": row["username"],
                    "first_name": row.get("first_name"),
                    "last_name": row.get("last_name"),
                    "role": row["workshop_role"],
                },
                "workshop": {"id": int(row["shop_id"])},
            }
        except AuthenticationError:
            conn.rollback()
            raise
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def resolve_session(self, bearer_token: str) -> dict[str, Any] | None:
        """Resolve a live session and re-check active membership on every call."""
        token = (bearer_token or "").strip()
        if not token or len(token) > 256:
            return None
        digest = hashlib.sha256(token.encode("utf-8")).hexdigest()
        conn = self._connect()
        try:
            with conn.cursor(dictionary=True) as cur:
                cur.execute(
                    """
                    SELECT u.id AS user_id, u.username,
                           s.shop_id, wm.role AS workshop_role
                    FROM user_sessions AS s
                    JOIN users AS u ON u.id = s.user_id
                    JOIN workshop_memberships AS wm
                      ON wm.user_id = s.user_id AND wm.shop_id = s.shop_id
                    JOIN shop_info AS si ON si.id = s.shop_id
                    WHERE s.token = %s
                      AND s.expires_at > UTC_TIMESTAMP()
                      AND wm.status = 'active'
                    LIMIT 1
                    """,
                    (digest,),
                )
                row = cur.fetchone()
                return dict(row) if row else None
        finally:
            conn.close()

    def logout(self, bearer_token: str) -> None:
        """Revoke the current bearer session without storing raw bearer tokens."""
        token = (bearer_token or "").strip()
        if not token or len(token) > 256:
            return
        digest = hashlib.sha256(token.encode("utf-8")).hexdigest()
        conn = self._connect()
        try:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM user_sessions WHERE token = %s", (digest,))
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
