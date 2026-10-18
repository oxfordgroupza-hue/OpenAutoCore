# Multi-workshop implementation plan

## Goal

Prepare OpenAutoCore for independent automotive repair businesses using the Windows desktop client while connecting to one centrally hosted service. Workshop data must remain isolated, and the original upstream repository must remain untouched.

## Current assessment

The existing application is a Python/PyQt6 desktop client with MySQL repositories. The desktop code calls `connect_db()` directly using environment-based database credentials. FastAPI/Uvicorn is currently used for local integration callbacks; this is not yet a complete remote business API.

The roadmap identifies multi-shop support as future work.

Observed risks that must be addressed before a multi-workshop pilot:

- Customer and vehicle repository methods perform global queries or filter only by record ID.
- Appointment methods read, update, and delete records without a workshop ownership condition.
- Estimates, estimate jobs/items, repair orders, invoices, and inspection records form a linked data graph and must be protected consistently.
- Shop settings and pricing-matrix save methods truncate and rewrite tables, which is incompatible with multiple independent workshops.
- User authentication is not sufficient by itself; the server must resolve the user's workshop membership and permissions.
- Integration credentials and callback handling must use explicit workshop ownership rather than a global/default shop.
- A client-installed database credential must not grant access to the central production database.

## Target architecture

1. **Windows desktop client:** presentation and user interaction; no production database credentials.
2. **HTTPS API:** authentication, authorization, input validation, business operations, and audit events.
3. **Central relational database:** accessible only to the API service through a least-privilege database account.
4. **Workshop identity and membership:** every authenticated user is linked to one or more workshops with a role. Each request resolves an authorized workshop context on the server.
5. **Backups and observability:** automated backups, restore verification, health checks, and structured logs without secrets or unnecessary customer data.

## Data model direction

Use a normalized workshop table and workshop membership relationship. Every business record must have a verifiable workshop owner. For core records such as customers, vehicles, appointments, repair orders, estimates, invoices, and inspections, prefer explicit ownership columns where they materially simplify authorization and indexing. For dependent rows such as estimate line items and inspection findings, enforce ownership through validated parent relationships and/or explicit ownership columns where needed for safe queries.

Add foreign keys and indexes after reviewing the full schema and existing data. Existing data must be assigned to a clearly identified legacy/default workshop during a controlled migration. Never infer a real workshop identity from arbitrary IDs or silently assign production data to a demo tenant.

Workshop-specific configuration includes shop profile, labour rates, pricing rules, tax rates, user preferences, and integration credentials. Global defaults may exist only as explicit defaults; writes must be scoped to a workshop. Replace destructive table-wide `TRUNCATE` save patterns with scoped upserts/transactions.

## Implementation phases

### Phase 0 — Safe workspace and baseline

- Work only on a user-controlled development branch/repository.
- Preserve the upstream project and the current main branch.
- Record the current schema and key workflows.
- Use a disposable development database with synthetic data.
- Confirm dependency installation and existing application startup before refactoring.

### Phase 1 — Identity and API foundation

- Add workshop and membership schema with appropriate constraints.
- Implement server-side authentication and authorization.
- Add a versioned HTTPS API with validated request/response schemas.
- Keep database credentials exclusively on the server.
- Add health checks and safe error handling; do not expose stack traces or secrets to clients.

### Phase 2 — Data isolation

- Migrate customers, vehicles, appointments, repair orders, estimates, estimate jobs/items, invoices, payments, inspections/findings, and associated assets/integrations.
- Scope every repository operation to the authenticated workshop.
- Validate all cross-table references against that same workshop.
- Replace global settings mutations with workshop-scoped operations.
- Remove any fallback that selects a global/default integration credential.

### Phase 3 — Desktop integration

- Introduce a typed API client and secure session handling.
- Replace direct production MySQL calls incrementally, workflow by workflow.
- Keep the UI responsive, handle network failures, and avoid logging tokens or customer-sensitive information.
- Provide a simple server URL/configuration mechanism suitable for demo deployments.

### Phase 4 — Verification

- Unit-test authorization and input validation.
- Run tenant-isolation tests: workshop A must not read or mutate workshop B's records, including by changing IDs or linked IDs.
- Test employee roles, login expiry, logout, failed requests, and integration callbacks.
- Test concurrent normal workflows with at least 20 simulated active users; measure latency and database connection usage.
- Test backup restoration and migration rollback on disposable data.
- Do not use real customer data for early demos.

### Phase 5 — Demo deployment

- Only after isolation tests pass, select hosting and deploy the API/database.
- Keep database ports private; expose only the HTTPS API and required administration endpoints.
- Use TLS, managed secrets/environment variables, least-privilege accounts, backups, monitoring, and rate limits.
- Review actual provider cost, free-tier expiry, and billing status before creating resources.

## Release gates

Do not call the system multi-tenant-ready until:

- Cross-workshop read/write tests pass for every business entity.
- No desktop client contains central production database credentials.
- Settings and integration credentials are isolated.
- Migration and rollback have been tested on a copy.
- The 20-user concurrency test completes without data leakage or unacceptable failures.
- Backup restoration has been verified.

## Licensing note

The upstream project is GPL-3.0. Preserve required notices and review GPL obligations before distributing modified desktop builds or offering a hosted/commercial derivative. This plan does not assert ownership of upstream code.

## Current status

This document records the initial audit and implementation sequence. It does not claim that the application has already been modified, migrated, deployed, or tested. No cloud resources are created by this plan.
