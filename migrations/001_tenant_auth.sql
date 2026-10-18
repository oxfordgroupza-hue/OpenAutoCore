-- OpenAutoCore tenant authentication schema foundation
-- STATUS: NOT APPLIED. Review docs/tenant-authentication-migration.md first.
-- Run only against a backed-up disposable test database until all release gates pass.
-- This migration is additive and intentionally does not assign existing users
-- to a workshop. Without explicit active membership rows, API login must fail closed.

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

-- Required manual post-migration actions before enabling OAC_ENABLE_TENANT_AUTH:
-- 1. Revoke all legacy sessions (they store raw tokens, unlike API token digests).
-- 2. Explicitly create an active workshop_memberships row for each authorized user.
-- 3. Verify the chosen shop_id exists and matches the intended legacy/demo shop.
-- 4. Test login, workshop selection, session expiry, revocation, and membership suspension.
-- 5. Do not enable business-data endpoints; they are not implemented yet.
