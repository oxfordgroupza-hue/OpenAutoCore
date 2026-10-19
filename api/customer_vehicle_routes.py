"""Customer and vehicle API routes with explicit workshop ownership checks.

These endpoints are opt-in only through the central API router. They use
workshop ownership mapping tables so legacy customer/vehicle tables do not
become globally readable merely because a user has authenticated.
"""
from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict, Field

from api.database import connect_db
from api.tenant_context import tenant_context

router = APIRouter(prefix="/v1", tags=["workshop data"])


class CustomerCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    first_name: str = Field(min_length=1, max_length=30)
    last_name: str = Field(min_length=1, max_length=30)
    phone: str = Field(min_length=1, max_length=15)
    address: str = Field(default="", max_length=255)
    city: str = Field(default="", max_length=100)
    state: str = Field(default="", max_length=100)
    zip: str = Field(default="", max_length=20)
    alt_phone: str | None = Field(default=None, max_length=15)
    email: str | None = Field(default=None, max_length=254)


class CustomerUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    first_name: str | None = Field(default=None, min_length=1, max_length=30)
    last_name: str | None = Field(default=None, min_length=1, max_length=30)
    phone: str | None = Field(default=None, min_length=1, max_length=15)
    address: str | None = Field(default=None, max_length=255)
    city: str | None = Field(default=None, max_length=100)
    state: str | None = Field(default=None, max_length=100)
    zip: str | None = Field(default=None, max_length=20)
    alt_phone: str | None = Field(default=None, max_length=15)
    email: str | None = Field(default=None, max_length=254)


class VehicleCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    customer_id: int = Field(ge=1)
    vin: str | None = Field(default=None, max_length=17)
    plate: str | None = Field(default=None, max_length=20)
    plate_state: str | None = Field(default=None, max_length=20)
    year: str | None = Field(default=None, max_length=30)
    make: str = Field(min_length=1, max_length=100)
    model: str = Field(min_length=1, max_length=100)
    engine_size: str | None = Field(default=None, max_length=100)
    trim: str | None = Field(default=None, max_length=100)


def _rows(sql: str, params: tuple[Any, ...]) -> list[dict[str, Any]]:
    conn = connect_db()
    try:
        with conn.cursor(dictionary=True) as cur:
            cur.execute(sql, params)
            return list(cur.fetchall() or [])
    finally:
        conn.close()


def _one(sql: str, params: tuple[Any, ...]) -> dict[str, Any] | None:
    rows = _rows(sql, params)
    return rows[0] if rows else None


def _owned_customer(shop_id: int, customer_id: int) -> bool:
    return _one(
        "SELECT customer_id FROM workshop_customer_access WHERE shop_id=%s AND customer_id=%s",
        (shop_id, customer_id),
    ) is not None


def _owned_vehicle(shop_id: int, vehicle_id: int) -> dict[str, Any] | None:
    return _one(
        """SELECT v.id, v.customer_id, v.vin, v.plate, v.plate_state, v.year,
                  v.make, v.model, v.engine_size, v.trim
           FROM vehicles v
           JOIN workshop_vehicle_access a ON a.vehicle_id=v.id AND a.shop_id=%s
           JOIN workshop_customer_access ca
             ON ca.customer_id=v.customer_id AND ca.shop_id=a.shop_id
           WHERE v.id=%s LIMIT 1""",
        (shop_id, vehicle_id),
    )


@router.get("/customers")
def list_customers(
    context: Annotated[dict, Depends(tenant_context)],
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
) -> list[dict[str, Any]]:
    return _rows(
        """SELECT c.customer_id, c.first_name, c.last_name, c.phone, c.address,
                  c.city, c.state, c.zip, c.alt_phone, c.email
           FROM customers c
           JOIN workshop_customer_access a ON a.customer_id=c.customer_id
           WHERE a.shop_id=%s
           ORDER BY c.last_name, c.first_name
           LIMIT %s OFFSET %s""",
        (context["shop_id"], limit, offset),
    )


@router.post("/customers", status_code=status.HTTP_201_CREATED)
def create_customer(
    payload: CustomerCreate,
    context: Annotated[dict, Depends(tenant_context)],
) -> dict[str, int]:
    shop_id = context["shop_id"]
    data = payload.model_dump()
    conn = connect_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO customers
                   (last_name, first_name, phone, address, city, state, zip, alt_phone, email)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                (data["last_name"], data["first_name"], data["phone"], data["address"],
                 data["city"], data["state"], data["zip"], data["alt_phone"], data["email"]),
            )
            customer_id = int(cur.lastrowid)
            cur.execute(
                "INSERT INTO workshop_customer_access (shop_id, customer_id) VALUES (%s,%s)",
                (shop_id, customer_id),
            )
        conn.commit()
        return {"customer_id": customer_id}
    except Exception:
        conn.rollback()
        raise HTTPException(status_code=503, detail="Customer service unavailable")
    finally:
        conn.close()


@router.get("/customers/{customer_id}")
def get_customer(
    customer_id: int,
    context: Annotated[dict, Depends(tenant_context)],
) -> dict[str, Any]:
    customer = _one(
        """SELECT c.customer_id, c.first_name, c.last_name, c.phone, c.address,
                  c.city, c.state, c.zip, c.alt_phone, c.email
           FROM customers c JOIN workshop_customer_access a ON a.customer_id=c.customer_id
           WHERE a.shop_id=%s AND c.customer_id=%s LIMIT 1""",
        (context["shop_id"], customer_id),
    )
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@router.patch("/customers/{customer_id}")
def update_customer(
    customer_id: int,
    payload: CustomerUpdate,
    context: Annotated[dict, Depends(tenant_context)],
) -> dict[str, bool]:
    data = payload.model_dump(exclude_unset=True)
    if not data:
        raise HTTPException(status_code=400, detail="No fields supplied")
    if any(value is None for value in data.values()):
        raise HTTPException(status_code=422, detail="Fields cannot be null")
    allowed = {"first_name", "last_name", "phone", "address", "city", "state", "zip", "alt_phone", "email"}
    if not set(data).issubset(allowed):
        raise HTTPException(status_code=422, detail="Invalid fields")
    conn = connect_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT customer_id FROM workshop_customer_access WHERE shop_id=%s AND customer_id=%s",
                (context["shop_id"], customer_id),
            )
            if not cur.fetchone():
                raise HTTPException(status_code=404, detail="Customer not found")
            assignments = ", ".join(f"{column}=%s" for column in data)
            cur.execute(
                f"UPDATE customers SET {assignments} WHERE customer_id=%s",
                (*data.values(), customer_id),
            )
        conn.commit()
        return {"updated": True}
    except HTTPException:
        conn.rollback()
        raise
    except Exception:
        conn.rollback()
        raise HTTPException(status_code=503, detail="Customer service unavailable")
    finally:
        conn.close()


@router.get("/customers/{customer_id}/vehicles")
def list_customer_vehicles(
    customer_id: int,
    context: Annotated[dict, Depends(tenant_context)],
) -> list[dict[str, Any]]:
    if not _owned_customer(context["shop_id"], customer_id):
        raise HTTPException(status_code=404, detail="Customer not found")
    return _rows(
        """SELECT v.id, v.customer_id, v.vin, v.plate, v.plate_state, v.year,
                  v.make, v.model, v.engine_size, v.trim
           FROM vehicles v
           JOIN workshop_vehicle_access a ON a.vehicle_id=v.id AND a.shop_id=%s
           JOIN workshop_customer_access ca
             ON ca.customer_id=v.customer_id AND ca.shop_id=a.shop_id
           WHERE v.customer_id=%s ORDER BY v.year DESC, v.make, v.model""",
        (context["shop_id"], customer_id),
    )


@router.post("/vehicles", status_code=status.HTTP_201_CREATED)
def create_vehicle(
    payload: VehicleCreate,
    context: Annotated[dict, Depends(tenant_context)],
) -> dict[str, int]:
    shop_id = context["shop_id"]
    data = payload.model_dump()
    if not _owned_customer(shop_id, data["customer_id"]):
        # Deliberately do not reveal whether the customer exists in another shop.
        raise HTTPException(status_code=404, detail="Customer not found")
    data["vin"] = data["vin"].strip().upper() if data["vin"] else None
    data["plate"] = data["plate"].strip().upper() if data["plate"] else None
    data["plate_state"] = data["plate_state"].strip().upper() if data["plate_state"] else None
    conn = connect_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO vehicles
                   (vin, plate, plate_state, year, make, model, engine_size, trim, customer_id)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                (data["vin"], data["plate"], data["plate_state"], data["year"], data["make"],
                 data["model"], data["engine_size"], data["trim"], data["customer_id"]),
            )
            vehicle_id = int(cur.lastrowid)
            cur.execute(
                "INSERT INTO workshop_vehicle_access (shop_id, vehicle_id) VALUES (%s,%s)",
                (shop_id, vehicle_id),
            )
        conn.commit()
        return {"vehicle_id": vehicle_id}
    except Exception:
        conn.rollback()
        raise HTTPException(status_code=503, detail="Vehicle service unavailable")
    finally:
        conn.close()


@router.get("/vehicles/{vehicle_id}")
def get_vehicle(
    vehicle_id: int,
    context: Annotated[dict, Depends(tenant_context)],
) -> dict[str, Any]:
    vehicle = _owned_vehicle(context["shop_id"], vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return vehicle
