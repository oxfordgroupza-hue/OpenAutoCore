# Central API foundation status

## Included

- A separate FastAPI application entry point at `api/main.py`.
- A minimal `GET /health` endpoint for process-level health checks.
- OpenAPI documentation at `/docs` for local development.

## Deliberate limitations

This is **not a production-ready API**. It does not connect to MySQL or expose customer, vehicle, appointment, estimate, repair-order, invoice, or inspection data. It does not implement login, tokens, workshop membership, role checks, tenant isolation, rate limiting, or production CORS/TLS configuration.

Do not expose this service publicly or connect the desktop application to it for real customer data yet.

## Local smoke test

In a disposable virtual environment with the project's requirements installed, run:

```powershell
python -m uvicorn api.main:app --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000/health`. Expected response:

```json
{"status":"ok","service":"openautocore-api","stage":"foundation"}
```

Stop the process with Ctrl+C. This test does not connect to or change any database.

## Required engineering gates

1. Confirm the complete schema and authentication/user model.
2. Design a reversible, reviewed tenant migration and explicit legacy-data mapping.
3. Implement server-side authentication and user-to-workshop membership.
4. Implement tenant-scoped repositories and enforce ownership for every linked record.
5. Add cross-workshop authorization tests before adding business routes.
6. Only then adapt the Windows client to call the API and evaluate deployment.
