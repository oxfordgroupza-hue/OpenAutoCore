# Central API authentication and tenant-isolation readiness review

Branch reviewed: `multi-shop-foundation`

This is a source-code review only. No database connection, migration, production action, or deployment was performed.

## Verified current state

- The central API in `api/main.py` exposes only `GET /health`; it has no business-data routes and no authentication dependency.
- The desktop login flow in `openauto/managers/login_manager.py` calls `UsersRepository.verify_credentials` directly. That repository connects to MySQL through `connect_db()`.
- `openauto/repositories/users_repository.py` hashes passwords with bcrypt (cost 12) and has methods to create, look up, and verify users. It also has persistent-session helpers backed by `user_sessions`.
- The schema defines `user_sessions(token CHAR(64), user_id, created_at, expires_at)`; the token is the primary key and the user ID references `users.id`.
- The schema's `users` table has global unique constraints on username and email and a single global `user_type` enum (`writer`, `technician`, `manager`). It has no workshop-membership relationship.
- The desktop login implementation is not a substitute for central API authentication. Its current credential verification relies on the desktop client reaching MySQL.
- `shop_info` is the closest existing workshop-profile table, but it is not sufficient on its own to represent membership, role, active/suspended status, or authorization.
- The schema dump contains 29 tables and does not contain `app_settings`, although code refers to that table. The deployed database may differ from the dump; this must be resolved before migration design can be finalized.
- `SettingsManager` currently uses table-wide `TRUNCATE` operations for shop profile, pricing matrix, labor rates, and tax rates. These operations are incompatible with shared multi-workshop data.

## Security blockers

1. There is no implemented central API login, bearer/session validation, logout route, or request-level authorization.
2. There is no explicit user-to-workshop membership table or active membership status.
3. Most business records have no workshop ownership column or verified tenant-boundary constraint.
4. Linked record IDs (customer, vehicle, appointment, estimate, repair order, assigned staff, inspections, invoices, and integration sessions) are not yet protected by a central API authorization layer.
5. Legacy desktop code can connect directly to MySQL. For a remotely hosted demo, the database must not be publicly exposed; client access must be moved behind the HTTPS API and database credentials must remain server-side.
6. Persistent sessions must be revocable, expiry-enforced, rate-limited at login, and stored/handled as secrets. A session token must never be accepted without resolving both the user and an active workshop membership.

## Recommended implementation sequence

1. Reconcile the schema dump against the actual intended database schema, especially `app_settings`, and review every foreign key and repository query.
2. Define a canonical workshop ID, user-to-workshop membership table, membership status, and per-workshop role policy. Decide explicitly whether users can belong to multiple workshops.
3. Prepare a migration proposal with preflight checks, explicit mapping of existing data to a chosen legacy/demo workshop, backup/restore verification, validation queries, and rollback limits. Do not execute it as part of this review.
4. Implement API authentication against the existing password hashes, using a high-entropy random session token, a fixed server-enforced expiry, secure transport, and revocation. Return only minimal user and membership data; never return password hashes.
5. Implement a single authorization dependency that resolves the token, verifies expiry and active membership, and derives workshop identity server-side. Never trust a client-supplied workshop ID as proof of access.
6. Add tenant-aware repositories and constraints, including checks that every linked record and assigned user belongs to the same workshop. Review global uniqueness rules such as VIN and repair-order number before changing them.
7. Replace table-wide settings truncation with workshop-scoped, transactional writes. Avoid destructive DDL in application request paths.
8. Add automated tests for expired/revoked/invalid tokens, inactive memberships, role enforcement, and cross-workshop reads/writes/deletes, including nested IDs and integration callbacks.
9. Only after those gates pass, adapt the Windows client to call the central HTTPS API and remove direct database connectivity from the client package.

## Release gate

The API remains health-only until the schema, authentication, tenant ownership, authorization, and cross-workshop tests are implemented and verified. Do not expose business data, run migrations, or claim multi-workshop readiness based on the current foundation alone.
