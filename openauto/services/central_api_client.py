"""HTTP client for the central OpenAutoCore API.

This transport is not yet wired into the legacy repositories. It intentionally
has no MySQL connection settings and keeps bearer tokens in memory only. TLS
certificate verification remains enabled by requests' default behavior.
"""
from __future__ import annotations

import os
from urllib.parse import urlparse

import requests


class CentralApiError(RuntimeError):
    """Safe, user-facing central API failure."""


class CentralApiClient:
    def __init__(self, base_url: str | None = None, *, session=None, timeout: float = 10.0):
        candidate = (base_url or os.getenv("OAC_API_BASE_URL") or "").strip().rstrip("/")
        parsed = urlparse(candidate)
        if parsed.scheme not in {"https", "http"} or not parsed.netloc:
            raise ValueError("Set OAC_API_BASE_URL to the central API URL")
        if parsed.username or parsed.password or parsed.query or parsed.fragment:
            raise ValueError("The central API URL must not contain credentials, query, or fragment")
        if parsed.scheme != "https" and parsed.hostname not in {"localhost", "127.0.0.1", "::1"}:
            raise ValueError("HTTPS is required except for loopback development")
        if timeout <= 0 or timeout > 60:
            raise ValueError("timeout must be greater than 0 and at most 60 seconds")
        self.base_url = candidate
        self.timeout = timeout
        self._session = session or requests.Session()
        self._access_token: str | None = None

    @property
    def is_authenticated(self) -> bool:
        return bool(self._access_token)

    def _request(self, method: str, path: str, **kwargs):
        headers = dict(kwargs.pop("headers", {}) or {})
        if self._access_token:
            headers["Authorization"] = f"Bearer {self._access_token}"
        try:
            response = self._session.request(
                method,
                f"{self.base_url}/{path.lstrip('/')}",
                headers=headers,
                timeout=self.timeout,
                **kwargs,
            )
        except requests.RequestException as exc:
            raise CentralApiError("Could not connect to the central service") from exc
        if response.status_code >= 400:
            if response.status_code == 401:
                raise CentralApiError("Login expired or access was denied")
            if response.status_code == 503:
                raise CentralApiError("Central service is temporarily unavailable")
            raise CentralApiError(f"Central service request failed (HTTP {response.status_code})")
        return response

    def login(self, username_or_email: str, password: str, workshop_id: int | None = None) -> dict:
        payload = {"username_or_email": username_or_email, "password": password}
        if workshop_id is not None:
            payload["workshop_id"] = int(workshop_id)
        response = self._request("POST", "/auth/login", json=payload)
        try:
            data = response.json()
        except ValueError as exc:
            raise CentralApiError("Central service returned an invalid response") from exc
        if data.get("selection_required"):
            return {"selection_required": True, "workshops": data.get("workshops", [])}
        token = data.get("access_token")
        if not isinstance(token, str) or not token:
            raise CentralApiError("Central service did not return a valid session")
        self._access_token = token
        return data

    def me(self) -> dict:
        if not self._access_token:
            raise CentralApiError("Login is required")
        try:
            return self._request("GET", "/auth/me").json()
        except ValueError as exc:
            raise CentralApiError("Central service returned an invalid response") from exc

    def logout(self) -> None:
        if not self._access_token:
            return
        try:
            self._request("POST", "/auth/logout")
        finally:
            self._access_token = None

    def clear_session(self) -> None:
        """Clear the in-memory token without making a network request."""
        self._access_token = None
