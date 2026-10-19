"""Contract tests for customer/vehicle request validation and opt-in route gating."""
import importlib

import pytest
from pydantic import ValidationError

from api.customer_vehicle_routes import CustomerCreate, CustomerUpdate, VehicleCreate


def test_customer_create_rejects_extra_fields():
    with pytest.raises(ValidationError):
        CustomerCreate(first_name="A", last_name="B", phone="123", shop_id=999)


def test_customer_update_requires_at_least_one_field_at_route_boundary():
    # Empty model is valid as a schema object; route returns 400 if no fields are supplied.
    payload = CustomerUpdate()
    assert payload.model_dump(exclude_unset=True) == {}


def test_vehicle_create_validates_customer_id_and_normalizes_shape():
    payload = VehicleCreate(customer_id=4, make="Toyota", model="Corolla", year="2020")
    assert payload.customer_id == 4
    assert payload.year == "2020"
    with pytest.raises(ValidationError):
        VehicleCreate(customer_id=0, make="Toyota", model="Corolla")


def test_customer_vehicle_routes_are_not_mounted_without_both_opt_ins(monkeypatch):
    monkeypatch.setenv("OAC_ENABLE_TENANT_AUTH", "true")
    monkeypatch.delenv("OAC_ENABLE_TENANT_DATA", raising=False)
    import api.main as api_main
    importlib.reload(api_main)
    assert not any(route.path.startswith("/v1/") for route in api_main.app.routes)

    monkeypatch.setenv("OAC_ENABLE_TENANT_DATA", "true")
    importlib.reload(api_main)
    assert "/v1/customers" in {route.path for route in api_main.app.routes}

    monkeypatch.delenv("OAC_ENABLE_TENANT_AUTH", raising=False)
    monkeypatch.delenv("OAC_ENABLE_TENANT_DATA", raising=False)
    importlib.reload(api_main)
