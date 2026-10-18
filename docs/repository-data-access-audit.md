# Repository data-access audit

This audit was performed against the `multi-shop-foundation` source branch and the checked-in schema dump. It is static inspection only; no application or database was run.

## Confirmed direct-database access

The desktop application is not yet an API client. Core repository modules call `connect_db()` directly, including:

- `openauto/repositories/customer_repository.py`
- `openauto/repositories/vehicle_repository.py`
- `openauto/repositories/appointment_repository.py`
- `openauto/repositories/estimates_repository.py`
- `openauto/repositories/estimate_items_repository.py`
- `openauto/repositories/estimate_jobs_repository.py`
- `openauto/repositories/repair_orders_repository.py`
- `openauto/repositories/ro_c3_repository.py`
- `openauto/repositories/parts_tree_repository.py`
- `openauto/repositories/users_repository.py`
- `openauto/repositories/settings_repository.py`

The API health check does not call these repositories. Keep this direct-database desktop path as legacy behavior until API coverage exists for each workflow; do not expose a production database port to workshop PCs.

## Highest-risk confirmed patterns

1. **Global customer and vehicle access.** Customer/vehicle repositories contain list and mutation queries keyed by record ID or global table scans. These must not be exposed to a multi-workshop API without explicit ownership checks.
2. **Appointments and repair orders.** Appointment and repair-order repository methods perform record operations without a verified workshop context. Their nested references to customers, vehicles, estimates, and staff need same-workshop validation.
3. **Settings data loss risk.** `openauto/managers/settings_manager.py` explicitly truncates and rewrites:
   - `shop_info` in `save_shop_settings()`
   - `pricing_matrix` in `save_pricing_matrix()`
   - `labor_rates` in `save_labor_rates()`
   - `tax_rates` in `save_tax_rates()`

   These operations are destructive across all rows and cannot support multiple workshops. Replace them with transactionally scoped updates/upserts after the schema defines workshop ownership.
4. **Inspection and media records.** `mpi_repository.py` operates on inspections, findings, photos, and signoffs; inspection records contain several linked IDs. Verify all ownership relationships before exposing inspection, image, or signature APIs.
5. **Parts/integration data.** PartsTech sessions, orders, items, and raw payloads must be tied to a validated workshop context. Do not trust caller-supplied session IDs or callback parameters as proof of ownership.
6. **Users and permissions.** Existing user roles are `writer`, `technician`, and `manager`; this is not a substitute for workshop membership or API authorization. User-list queries also need workshop scoping.

## Recommended implementation order

1. Finish the schema/membership design and decide the explicit legacy workshop mapping.
2. Implement API authentication and server-resolved workshop membership before any business-data routes.
3. Migrate one low-risk workflow (for example, workshop profile read) behind tests, then customers/vehicles, then appointments, estimates, repair orders, payments, inspections, and integrations.
4. Replace direct desktop database calls workflow-by-workflow only after the matching API endpoints are implemented and verified.
5. Run automated cross-workshop denial tests before the first real shop demo.

## Release status

The current branch has a health-only API, no database connection in the API entry point, and no workshop business routes. It is **not ready for real customer data or remote workshop demos**. No migration or deployment has been performed.
