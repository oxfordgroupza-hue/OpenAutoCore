# Central API authentication foundation status

## Included on `multi-shop-foundation`

- `GET /health`: process health response; does not depend on MySQL.
- `POST /auth/login`: verifies the existing `users` bcrypt password hash and creates an eight-hour bearer session in the existing `user_sessions` table.
- `GET /auth/me`: returns the authenticated user's public profile.
- `POST /auth/logout`: revokes the current session.
- Database configuration is server-side only, loaded from repository-root `.env` or process environment. The Windows client must never receive MySQL credentials.
- API documentation and OpenAPI are disabled by default. Set `APP_ENV=development` only for local development to enable `/docs` and `/openapi.json`.
- Unit/API tests use mocked database functions and do not connect to, read, or change a real database.

## Local checks

Install the repository requirements and test dependencies in a disposable virtual environment, then run:

```powershell
python -m pip install -r requirements.txt -r requirements-dev.txt
python -m pytest -q tests/test_api_auth.py
```

For a local health check:

```powershell
python -m uvicorn api.main:app --host 127.0.0.1 --port 8000
```

Then request `http://127.0.0.1:8000/health`. Do not bind to a public interface until deployment has HTTPS, rate limiting, monitoring, and reviewed secrets handling.

## Explicitly not production-ready

This API is **not yet safe for a multi-workshop pilot**. The legacy schema has users but no authoritative user-to-workshop membership table, and most business tables do not have a workshop key. The current API deliberately exposes no customer, vehicle, appointment, estimate, repair-order, invoice, payment, inspection, parts, or settings routes.

Before any business-data endpoint is added:

1. Design a reviewed and reversible migration for workshop memberships and tenant ownership of every business record and child table.
2. Decide how legacy/demo rows are mapped to a specific workshop; do not silently assign live data.
3. Enforce membership and role authorization server-side, and validate ownership of linked IDs in every read and write.
4. Store bearer-token digests rather than raw tokens in a new session schema before production.
5. Add login throttling, audit logging, HTTPS/TLS deployment, security headers, secret rotation, backups, and cross-workshop isolation tests.
6. Migrate the Windows client away from direct MySQL access only after the API covers the workflows being enabled.

No schema migration, database connection, cloud deployment, or production data change is performed by these files.
