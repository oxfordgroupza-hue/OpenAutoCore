from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_health_is_available_without_database():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "openautocore-api",
        "stage": "foundation",
    }


def test_no_business_data_routes_are_exposed_yet():
    for path in ("/customers", "/vehicles", "/appointments", "/estimates", "/invoices"):
        response = client.get(path)
        assert response.status_code == 404


def test_api_documentation_is_disabled_by_default():
    assert client.get("/docs").status_code == 404
    assert client.get("/openapi.json").status_code == 404
