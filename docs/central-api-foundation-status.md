# Central API foundation status

This branch contains an early central API foundation for the multi-workshop demo.

## Implemented

- Health-only FastAPI endpoint at `GET /health`.
- Interactive API docs and OpenAPI schema disabled by default.
- Tenant-aware authentication service primitives with random bearer tokens,
  SHA-256 token digests in storage, short session lifetime, membership checks,
  and revocation.
- Opt-in `/auth/login`, `/auth/me`, and `/auth/logout` routes. These routes
  are not mounted unless `OAC_ENABLE_TENANT_AUTH=true`.
- A Windows-side HTTP transport foundation with HTTPS enforcement for non-loopback hosts and in-memory bearer-token handling. It is not yet wired into legacy login/repositories.
- Unit tests for authentication contracts, client transport behavior, and API route gating.
- Migration design and preflight requirements in
  `docs/tenant-authentication-migration.md`.

## Not production-ready

- The authentication migration is a design draft and has **not** been applied
  to any database.
- The API does not yet expose business data routes.
- The legacy desktop repositories still connect directly to MySQL. They have
  not been converted to use the central API.
- Business tables are not yet fully workshop-scoped; existing data must not be
  exposed through a multi-workshop service.
- Login throttling, operational monitoring, secret management, backups, TLS
  deployment, and full integration tests remain release requirements.
- GitHub Actions currently reports a failed job before any steps are visible;
  the test suite has not been confirmed passing in CI.

## Local contract tests

From a clean Python environment:

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q tests/test_api_foundation.py tests/test_tenant_auth_contract.py tests/test_api_auth_routes.py tests/test_central_api_client.py
```

The tests use fakes and do not connect to a real database. Passing unit tests
would not prove that the migration works against the target MySQL version.

## Required release gates

1. Restore a backup into a disposable MySQL test database.
2. Apply and verify the reviewed migration there.
3. Test account creation, membership changes, login, expiry, revocation, and
   multi-workshop selection.
4. Convert all business-data repository access to authenticated central API
   requests and remove database credentials from Windows clients.
5. Add tenant ownership to all business records and child relationships.
6. Test every read/write/list/export/integration path against two isolated
   workshops, including attempts to substitute foreign record IDs.
7. Build and test a Windows installer against a test API.
8. Deploy only after all release gates pass. No paid cloud resources or
   production database changes are authorized by this branch work.
