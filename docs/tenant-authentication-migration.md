# Tenant authentication migration — gated implementation

Status: **design draft; not executed against any database**.

This migration is a prerequisite for central API authentication, not a complete
multi-workshop conversion. Do not expose customer, vehicle, estimate, repair
order, invoice, payment, inspection, or integration endpoints until all tenant
ownership work and cross-tenant tests are complete.

## Design decisions

- Keep `shop_info.id` as the existing workshop identifier for the first
  migration, pending a real-database schema comparison.
- Add an explicit `workshop_memberships` relation. Global `users.user_type`
  remains a legacy UI role and is not authorization for a workshop.
- Store only SHA-256 digests of random API bearer tokens in `user_sessions`.
  Raw tokens are returned once at login and are never stored in the database.
- Session resolution re-checks membership status on every request, allowing
  immediate revocation.
- A user with more than one active workshop membership receives the available
  memberships only after password verification, then must explicitly select one.
- Keep the API health-only until the migration and its integration tests are
  validated against an isolated disposable MySQL instance.

## Preflight required before running any DDL

1. Take and verify a restorable backup of the target database.
2. Confirm the exact MySQL version and compare `SHOW CREATE TABLE` output for
   `shop_info`, `users`, and `user_sessions` with the checked-in schema.
3. Verify `user_sessions.token` is wide enough for a 64-character SHA-256 hex
   digest (the current schema uses `CHAR(64)`).
4. Inventory existing sessions. Existing desktop sessions store raw 64-character
   hex tokens; they are not compatible with the new digest convention. Revoke
   all legacy sessions at cutover, rather than accepting both token formats.
5. Identify the actual legacy workshop and explicitly map existing users to it.
   Never assume `shop_info.id = 1` without checking the real database.
6. Run the migration against a disposable copy first and test rollback/restore.

## Proposed additive DDL

Review and adapt this DDL only after preflight. It is not an automatic migration.

```sql
CREATE TABLE workshop_memberships (
    user_id INT NOT NULL,
    shop_id INT NOT NULL,
    role ENUM('owner','manager','service_writer','technician','viewer') NOT NULL,
    status ENUM('active','invited','suspended','revoked') NOT NULL DEFAULT 'invited',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, shop_id),
    KEY idx_membership_shop_status (shop_id, status),
    CONSTRAINT fk_membership_user
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_membership_shop
        FOREIGN KEY (shop_id) REFERENCES shop_info(id) ON DELETE CASCADE
) ENGINE=InnoDB;

ALTER TABLE user_sessions
    ADD COLUMN shop_id INT NULL,
    ADD KEY idx_session_user_shop_expiry (user_id, shop_id, expires_at),
    ADD CONSTRAINT fk_session_shop
        FOREIGN KEY (shop_id) REFERENCES shop_info(id) ON DELETE CASCADE;
```

The `shop_id` on `user_sessions` is initially nullable to allow an additive
migration. Before enabling API login, all legacy sessions must be revoked and
new API sessions must have a non-null `shop_id`. A later migration may make it
NOT NULL after confirming there are no remaining legacy session rows.

## Mandatory verification

- User with no membership cannot log in.
- Suspended/revoked membership cannot log in or continue using an existing token.
- Invalid passwords and unknown users produce the same public error.
- Expired sessions fail; logout revokes the digest.
- Tokens are random, short-lived, and only their digest is stored.
- A user with multiple active memberships is never assigned a workshop implicitly.
- Workshop A cannot resolve a session or query a record in workshop B.
- Existing desktop login/session flows are tested before cutover.
- Migration is tested on a copy with existing data; restore is demonstrated.

## Remaining blockers

This change does not add workshop ownership to business tables or retrofit the
desktop client. The schema review in `docs/database-tenant-inventory.md` and
the repository audit in `docs/repository-data-access-audit.md` remain release
gates. Do not advertise this repository as multi-tenant-ready until all
business reads/writes, child relationships, integrations, reports, uploads,
and settings are tenant-scoped and tested.
