"""Database access for the central API authentication foundation.

Credentials are read only by the server process. Never ship this module or database
credentials to the Windows desktop client.
"""
from __future__ import annotations

import os
from pathlib import Path

import bcrypt
import mysql.connector
from dotenv import load_dotenv

# Load the repository-level .env regardless of the process working directory.
load_dotenv(Path(__file__).resolve().parents[1] / ".env", override=False)

SESSION_TTL_SECONDS = 8 * 60 * 60


class DatabaseUnavailable(RuntimeError):
    """The central database could not be reached or queried."""


def _connect():
    required = ("MYSQL_HOST", "MYSQL_USER", "MYSQL_PASSWORD", "MYSQL_NAME")
    missing = [key for key in required if not os.getenv(key)]
    if missing:
        raise DatabaseUnavailable("Database configuration is incomplete.")
    try:
        return mysql.connector.connect(
            host=os.environ["MYSQL_HOST"],
            user=os.environ["MYSQL_USER"],
            password=os.environ["MYSQL_PASSWORD"],
            database=os.environ["MYSQL_NAME"],
            connection_timeout=8,
            autocommit=False,
        )
    except mysql.connector.Error as exc:
        raise DatabaseUnavailable("Database connection failed.") from exc


def authenticate_user(username_or_email: str, password: str) -> dict | None:
    conn = _connect()
    try:
        with conn.cursor(dictionary=True) as cur:
            cur.execute(
                """
                SELECT id, username, email, password_hash, user_type,
                       first_name, last_name
                FROM users
                WHERE username = %s OR email = %s
                LIMIT 1
                """,
                (username_or_email, username_or_email),
            )
            user = cur.fetchone()
        if not user:
            return None
        try:
            valid = bcrypt.checkpw(
                password.encode("utf-8"), user["password_hash"].encode("utf-8")
            )
        except (ValueError, TypeError, AttributeError):
            valid = False
        if not valid:
            return None
        user.pop("password_hash", None)
        return user
    except mysql.connector.Error as exc:
        raise DatabaseUnavailable("Authentication query failed.") from exc
    finally:
        conn.close()


def create_session(user_id: int) -> str:
    import secrets

    token = secrets.token_hex(32)
    conn = _connect()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO user_sessions (token, user_id, expires_at)
                VALUES (%s, %s, DATE_ADD(UTC_TIMESTAMP(), INTERVAL 8 HOUR))
                """,
                (token, user_id),
            )
        conn.commit()
        return token
    except mysql.connector.Error as exc:
        conn.rollback()
        raise DatabaseUnavailable("Could not create session.") from exc
    finally:
        conn.close()


def get_user_for_token(token: str) -> dict | None:
    conn = _connect()
    try:
        with conn.cursor(dictionary=True) as cur:
            cur.execute(
                """
                SELECT u.id, u.username, u.email, u.user_type,
                       u.first_name, u.last_name
                FROM user_sessions s
                JOIN users u ON u.id = s.user_id
                WHERE s.token = %s
                  AND s.expires_at IS NOT NULL
                  AND s.expires_at > UTC_TIMESTAMP()
                LIMIT 1
                """,
                (token,),
            )
            return cur.fetchone()
    except mysql.connector.Error as exc:
        raise DatabaseUnavailable("Session lookup failed.") from exc
    finally:
        conn.close()


def delete_session(token: str) -> None:
    conn = _connect()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM user_sessions WHERE token = %s", (token,))
        conn.commit()
    except mysql.connector.Error as exc:
        conn.rollback()
        raise DatabaseUnavailable("Could not revoke session.") from exc
    finally:
        conn.close()
