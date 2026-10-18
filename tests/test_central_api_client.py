"""Unit tests for the Windows central API transport."""
import pytest

from openauto.services.central_api_client import CentralApiClient, CentralApiError


class FakeResponse:
    def __init__(self, status_code=200, body=None):
        self.status_code = status_code
        self._body = body or {}

    def json(self):
        return self._body


class FakeSession:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def request(self, method, url, **kwargs):
        self.calls.append((method, url, kwargs))
        return self.responses.pop(0)


def test_requires_https_for_non_loopback_hosts():
    with pytest.raises(ValueError, match="HTTPS"):
        CentralApiClient("http://example.com")


def test_rejects_credentials_in_base_url():
    with pytest.raises(ValueError, match="must not contain credentials"):
        CentralApiClient("https://user:pass@example.com")


def test_login_stores_token_in_memory_and_me_uses_bearer_header():
    session = FakeSession([
        FakeResponse(body={"access_token": "test-token", "token_type": "bearer"}),
        FakeResponse(body={"user": {"id": 2}, "workshop": {"id": 7}}),
    ])
    client = CentralApiClient("https://api.example.test", session=session)
    client.login("user", "password", workshop_id=7)
    result = client.me()
    assert result["workshop"]["id"] == 7
    assert session.calls[0][2]["json"]["workshop_id"] == 7
    assert session.calls[1][2]["headers"]["Authorization"] == "Bearer test-token"


def test_workshop_selection_does_not_create_local_session():
    session = FakeSession([FakeResponse(body={
        "selection_required": True,
        "workshops": [{"id": 7, "role": "owner"}],
    })])
    client = CentralApiClient("https://api.example.test", session=session)
    result = client.login("user", "password")
    assert result["selection_required"] is True
    assert not client.is_authenticated


def test_logout_clears_token_even_when_request_fails():
    class BrokenSession:
        def request(self, *args, **kwargs):
            import requests
            raise requests.ConnectionError("secret network detail")

    client = CentralApiClient("https://api.example.test", session=BrokenSession())
    client._access_token = "test-token"
    with pytest.raises(CentralApiError):
        client.logout()
    assert not client.is_authenticated
