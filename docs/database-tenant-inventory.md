# Database table inventory for multi-workshop planning

Source reviewed: `openauto_schema.sql` on `multi-shop-foundation` (29 `CREATE TABLE` definitions). This is a static schema review; no database was connected to or changed.

## Tenant ownership inventory

| Table | Current linkage in schema | Required tenant treatment |
|---|---|---|
| `shop_info` | Shop profile, primary key `id` | Canonical workshop entity candidate; review uniqueness, lifecycle, and ownership rules. |
| `users` | User identity and role; no shop key | Add explicit membership and role mapping. A global role alone is insufficient. |
| `user_sessions` | Links to `users.id` | Tie each active session to a valid user; resolve workshop membership for each request. |
| `user_settings` | Links to user | Decide which preferences are per-user and which business settings belong to a workshop. |
| `customers` | Primary key `customer_id`; no shop key | Workshop-owned; scope every lookup, list, edit, archive, and delete. |
| `vehicles` | `customer_id` foreign key | Workshop-owned; validate vehicle and customer share the same workshop. VIN uniqueness may need to become tenant-scoped. |
| `appointments` | Links to customer and vehicle | Workshop-owned; validate both linked records belong to the authorized workshop. |
| `estimates` | Links to customer, repair order, and assigned users | Workshop-owned; verify all referenced records and assigned users are in the same workshop. |
| `estimate_jobs` | Links to estimate | Child of estimate; ownership must follow and be constrained to the parent estimate. |
| `estimate_items` | Links to estimate and estimate job | Child of estimate/job; prevent cross-workshop parent/child references. |
| `repair_orders` | Links to customer, vehicle, appointment, estimate, and users | Workshop-owned; validate every linked record and user. Review globally unique `ro_number`. |
| `ro_c3_lines` | Links to repair order, estimate item, and user | Child of repair order; enforce parent and linked item ownership. |
| `invoices` | Links to estimate | Workshop-owned child; invoice access must be scoped through the estimate/workshop. |
| `payments` | Links to repair order and optional estimate | Financial child; validate both parents, restrict processor metadata, and audit mutations. |
| `mpi_inspections` | Stores RO, estimate, customer, vehicle, and creator IDs without declared foreign keys in this dump | Workshop-owned; verify each reference and add appropriate constraints after reviewing existing data. |
| `mpi_findings` | Links to inspection | Child of inspection; enforce parent ownership. |
| `mpi_photos` | Links to inspection and optional finding; contains binary data | Child of inspection; authorize image reads/writes and apply file-size/type controls. |
| `mpi_signoffs` | Links to inspection; stores signatures | Child of inspection; treat signatures as sensitive evidence and audit access. |
| `labor_rates` | No workshop key | Make workshop-specific unless an explicitly shared platform default is required. |
| `pricing_matrix` | No workshop key | Make workshop-specific; remove table-wide truncate/rewrite save paths. |
| `tax_rates` | No workshop key | Make workshop-specific or jurisdiction-scoped with explicit configuration. |
| `integration_tokens` | Has `shop_id` referencing `shop_info` | Existing partial tenancy; encrypt/rotate secrets and enforce shop scope for every operation. |
| `square_connections` | Has `shop_id`, merchant and tokens | Add/verify FK and tenant authorization; protect secrets and callbacks. |
| `square_devices` | Has `shop_id` and device identifiers | Add/verify FK; validate shop ownership on device pairing and status changes. |
| `pt_sessions` | Links to estimate and repair order IDs without declared foreign keys in this dump | Add explicit tenant ownership or derive through validated parents; prevent session ID guessing and cross-shop use. |
| `pt_orders` | Links to PartsTech session | Child of session; derive and enforce workshop from the authorized parent session. |
| `pt_order_items` | Links to session, order, and estimate job | Child data; verify all linked records share a workshop. |
| `parts_tree_items` | Contains estimate/session/job IDs without declared foreign keys in this dump | Child of estimate/session; validate all links and scope all CRUD operations. |
| `partstech_payloads` | Stores raw integration payload JSON and external session IDs | Treat as sensitive tenant data; validate callback identity before storing or serving payloads. |
| `app_settings` | Not present as a table in this schema dump, though legacy repository code references it | Reconcile schema/code drift before migration; do not assume deployment schema matches this dump. |

## High-risk design findings

- Tenant isolation must not rely solely on filtering a top-level customer list. Child tables, nested IDs, joins, integration callbacks, and exports can all leak data.
- Some logical relationships are not declared as database foreign keys in this schema dump. The migration must validate existing rows before adding constraints.
- Some uniqueness rules may be global today (for example VIN and repair-order number) and need deliberate tenant-specific decisions rather than mechanical changes.
- `app_settings` appears in repository code but not in this schema dump; reconcile the exact target database schema and migration history first.
- `integration_tokens`, `square_connections`, and `square_devices` have partial `shop_id` support, but this alone does not establish complete tenant isolation.
- Do not add a `shop_id` column to every table mechanically. For child tables, a validated tenant key on parent tables plus composite constraints may be safer; choose after inspecting all repository queries and writes.

## Migration gate checklist

- [ ] Compare this dump with the actual target database schema and migration history.
- [ ] Trace all repository methods and direct SQL for every table above.
- [ ] Define membership, role, suspension, and workshop-switch behavior.
- [ ] Decide tenant-aware uniqueness and foreign-key strategy.
- [ ] Produce preflight queries for orphaned and cross-linked records.
- [ ] Take and verify a restorable backup before any schema change.
- [ ] Write an additive migration with an explicit legacy-workshop mapping and documented rollback.
- [ ] Test tenant A/B isolation across read, create, update, delete, exports, reports, and integrations.
- [ ] Keep business API routes disabled until these gates pass.
