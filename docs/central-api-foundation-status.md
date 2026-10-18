# Central API foundation status

## Implemented on `multi-shop-foundation`

- `api/main.py` defines a separate FastAPI application with a single `GET /health` endpoint.
- `tests/test_api_foundation.py` checks the health response and verifies that common business-data routes are not exposed accidentally.
- The API does not connect to MySQL and does not read or mutate application data.
- The original Windows desktop client and database repositories remain unchanged.
- Interactive API documentation and the OpenAPI schema are disabled by default.

## Local checks

In a disposable virtual environment, install only the API test dependencies (the full desktop application's PyQt and integration dependencies are not needed for these isolated tests):

```powershell
python -m pip install -r requirements-dev.txt
python -m pytest -q tests/test_api_foundation.py
```

Run a local server with the repository's normal requirements installed:

```powershell
python -m uvicorn api.main:app --host 127.0.0.1 --port 8000
```

Then request `http://127.0.0.1:8000/health`. Stop the server with Ctrl+C. This is a local process check, not a production deployment or a multi-workshop readiness test.

## Why authentication and business routes are not enabled yet

The existing schema has a `users` table and persistent sessions, but no authoritative user-to-workshop membership model. Most core records also lack a workshop ownership column. Adding login alone would not protect customer data: every business-data route must resolve workshop membership server-side and validate ownership of linked records.

Before adding authenticated business endpoints:

1. Design a reviewed, reversible migration for workshop membership and ownership across customers, vehicles, appointments, estimates, estimate jobs/items, repair orders, invoices, payments, inspections/findings, parts orders/sessions, integrations, and settings.
2. Decide how existing rows are assigned to a named legacy/demo workshop; never silently map live records.
3. Implement server-side sessions, logout/revocation, expiry, login throttling, and secret handling.
4. Enforce workshop membership and role checks in every query and mutation. Verify linked IDs belong to the same workshop.
5. Replace global and destructive settings save operations (including table-wide truncate/rewrite patterns) before multi-shop use.
6. Add cross-workshop denial tests, migration rollback tests, backup/restore checks, and concurrency tests.
7. Migrate the Windows client away from direct MySQL access only after the central API supports the specific workflows enabled in the client.

No schema migration, database connection, cloud deployment, or production data change has been performed.
