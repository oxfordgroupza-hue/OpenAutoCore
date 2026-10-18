# Multi-workshop schema review

This is a planning document only. It does not modify or migrate a database.

## Confirmed gaps in the current schema

- `users` has identity and role fields, but no workshop membership relation.
- `customers` has no workshop identifier.
- `vehicles` references a customer, but has no workshop identifier of its own.
- `appointments` references customer and vehicle records without a workshop identifier.
- `estimates`, `estimate_items`, and `estimate_jobs` are linked records but do not have a consistent workshop ownership boundary.
- `repair_orders`, `invoices`, and `payments` link to other records without a workshop ownership boundary.
- Inspection records, parts/integration session data, and callback payloads must be traced through their parent records and external identifiers before they are exposed through an API.
- `shop_info` exists, and some integration tables already carry a `shop_id`, but this partial support does not prove end-to-end tenant isolation.
- `pricing_matrix`, `labor_rates`, `tax_rates`, and `app_settings` are currently read as global settings in the legacy repositories.
- `openauto/managers/settings_manager.py` contains table-wide `TRUNCATE` then rewrite flows for `shop_info`, `pricing_matrix`, `labor_rates`, and `tax_rates`. Those operations would erase other workshops' settings and must be replaced before multi-shop use.
- The legacy database schema includes existing rows. A migration must explicitly map those rows to an approved legacy/demo workshop and must not assume that numeric ID 1 is always the correct tenant.

## Required migration design before implementation

1. Inventory every table, foreign key, integration callback, uploaded asset, report, and query that reads or writes workshop-owned data.
2. Define a canonical workshop identity and a user-to-workshop membership table with explicit roles and membership status.
3. Choose a safe tenant-key strategy for parent and child tables. Use database constraints where possible to prevent cross-workshop relationships, not only application-level checks.
4. Plan staged migration: preflight checks, backup, additive schema changes, explicit legacy mapping, validation queries, application cutover, rollback procedure.
5. Make migrations idempotent where practical and document the exact rollback limitations for any destructive operation.
6. Add tests proving workshop A cannot read, mutate, delete, or infer workshop B data by changing record IDs, nested IDs, query filters, or integration callback values.
7. Review every settings and integration workflow for explicit workshop selection. Remove default-tenant assumptions and global writes.
8. Only then implement API business routes and adapt the Windows desktop client.

## Safety boundary

Do not run this migration against any database yet. Do not expose customer data from the API until the schema design, ownership mapping, authorization model, and cross-workshop tests are reviewed.
