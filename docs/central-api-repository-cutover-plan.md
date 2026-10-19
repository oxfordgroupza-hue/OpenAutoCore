# Central API and Desktop Repository Cutover Plan

## Purpose

Move the Windows/PyQt desktop client from direct MySQL access to a central HTTPS API without weakening existing OpenAutoCore features. This is a staged engineering plan, not a declaration that multi-workshop operation is ready.

## Non-negotiable safety rule

Do not deploy the existing desktop client against a shared multi-workshop database. The current repository layer issues direct SQL without a consistently enforced workshop context. Adding a login token alone does not isolate data.

## Confirmed repository surface

The following active repository modules were reviewed on `multi-shop-foundation`:

| Module | Observed data surface | Cutover concern |
|---|---|---|
| `customer_repository.py` | `customers` | Every read/update/delete and related customer identifier must be scoped to the authenticated workshop. |
| `vehicle_repository.py` | `vehicles`, `customers` | Vehicle ownership joins must validate both vehicle and customer belong to the same workshop. |
| `appointment_repository.py` | `appointments`, `customers`, `vehicles` | Calendar/list/detail/update/delete paths must all enforce tenant scope. |
| `repair_orders_repository.py` | `repair_orders`, `users`, `customers`, `vehicles`, `estimate_jobs`, `estimate_items`, `items`, `pt_sessions`, `estimates` | High-risk aggregate with cascading deletes, status changes, staff assignment, locks, approvals, and derived totals. |
| `estimates_repository.py` | `estimates`, `repair_orders` | Estimate and repair-order parent relationship must be validated server-side. |
| `estimate_jobs_repository.py` | `estimate_jobs`, `estimate_items`, `estimates` | Job and line-item operations must verify ownership through the estimate/repair-order chain. |
| `estimate_items_repository.py` | `estimate_items`, `estimate_jobs` | Item operations must not trust caller-supplied estimate/job IDs. |
| `mpi_repository.py` | `mpi_inspections`, `mpi_findings`, `repair_orders`, `vehicles` | Inspection/finding ownership and any related media/sign-off records require parent-chain validation. |
| `parts_tree_repository.py` | `pt_sessions`, `pt_orders`, `pt_order_items`, estimate links | Supplier/session/order records must be scoped and validated together. |
| `ro_c3_repository.py` | `ro_c3_lines` | Every line operation must verify its repair-order parent is in the active workshop. |
| `settings_repository.py` | `pricing_matrix`, `labor_rates`, `app_settings`, `tax_rates`, `user_settings` | Shop settings must be isolated; `app_settings` is referenced by code but absent from the reviewed schema dump. |
| `users_repository.py` | `users`, `user_settings`, `user_sessions` | Existing global user identity and legacy role model need a compatibility plan for workshop memberships. |
| `settings_manager.py` | `shop_info`, `pricing_matrix`, `labor_rates`, `tax_rates` | Settings writes must be transactional and scoped; existing table-replacement behavior must not overwrite other shops' settings. |

The schema dump currently contains 29 tables. Most operational tables do not consistently carry a `shop_id`. A subset of integration tables already has shop identifiers, which is not sufficient to guarantee tenant isolation.

## Required target architecture

1. **Desktop client:** UI and business workflows remain in the Windows app; repositories call the central API rather than opening database connections.
2. **Central API:** authenticates users, resolves one active workshop membership per session, derives workshop scope from the authenticated session, validates roles and parent-child ownership, and performs all database operations.
3. **Database:** only the API service account can connect from the application infrastructure. Demo workstations receive no database credentials or network route to MySQL.
4. **Workshop membership:** a user may belong to one or more workshops; the login flow requires an explicit selection when more than one active membership exists.
5. **Auditability:** write operations that change financial, customer, repair-order, approval, or settings data are logged with actor, workshop, action, and timestamp, excluding passwords and bearer tokens.

## Implementation sequence

### Gate 0 — preserve current behavior
- Keep original `main` unchanged.
- Keep the API auth routes disabled by default.
- Do not apply `migrations/001_tenant_auth.sql` to a live database.
- Keep direct-MySQL legacy behavior available only for isolated single-workshop development until feature parity and cutover tests are complete.

### Gate 1 — schema and relationship inventory
- Confirm actual deployed schema versus `openauto_schema.sql`.
- Map primary keys, foreign keys, cascade behavior, status transitions, and all SQL call sites for every repository.
- Decide whether tenant isolation uses direct `shop_id` columns, enforced parent ownership, or both. High-value operational entities should have an explicit and indexable tenant key where feasible.
- Design a repeatable migration and rollback procedure; do not backfill every existing record to an arbitrary workshop.

### Gate 2 — API primitives
- Finish auth hardening: login throttling, generic failure responses, session revocation, expiry handling, and membership deactivation tests.
- Add authenticated request context and central authorization helpers.
- Add request/response schemas and consistent validation/error handling.
- Add health/readiness distinction without exposing database details.

### Gate 3 — vertical-slice migration
Implement and test one complete workflow at a time, beginning with customers and vehicles:
- list/search, details, create, update, delete;
- validate customer/vehicle ownership on every operation;
- verify that a user from workshop B cannot read or mutate workshop A's records, including by guessing numeric IDs.
Then migrate appointments, repair orders, estimates/jobs/items, MPI, parts ordering, settings, and integrations in dependency order.

### Gate 4 — desktop adapter and login
- Replace direct SQL in a repository only after the corresponding API endpoints and contract tests are ready.
- Preserve method contracts used by UI code through adapter classes where practical.
- Store only the session token in process memory or a supported OS credential store; never store central database credentials on workstations.
- Handle expiry, logout, offline/network failure, and workshop selection explicitly.
- Remove/disable account creation from the public login screen unless it is backed by a safe workshop-provisioning/invitation flow.

### Gate 5 — release validation
- Automated unit and API tests.
- Disposable MySQL integration tests using the real schema and migrations.
- Cross-tenant negative tests for every endpoint and every parent-child relationship.
- Concurrent-use tests for at least 20 workshops.
- Windows packaging/install/upgrade tests on clean Windows 11 machines.
- TLS, secret management, backup/restore, monitoring, rate limits, and incident recovery checks.
- Confirm no workstation can reach MySQL and no business-data endpoint works without authentication and tenant scope.

## Current state

- The API health foundation, opt-in authentication routes, tenant-aware session primitives, and Windows HTTP transport foundation exist.
- The HTTP transport is not yet wired into legacy repositories.
- Business-data endpoints and end-to-end tenant isolation are not implemented.
- The tenant-auth migration is a draft and has not been applied.
- GitHub Actions currently cannot start jobs because GitHub reports that the account is locked due to a billing issue. This is an account-level CI blocker, not evidence that test assertions failed. Local/stubbed test checks are not a substitute for a full CI and database integration run.

**Release decision:** not production-ready and not safe for shared multi-workshop customer data until the gates above pass.
