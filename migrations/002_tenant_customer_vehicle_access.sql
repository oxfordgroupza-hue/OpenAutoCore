-- OpenAutoCore tenant-scoped customer/vehicle access maps
-- STATUS: NOT APPLIED. Apply only after 001_tenant_auth.sql on a disposable
-- backed-up database. Existing records are intentionally not auto-assigned.
-- Provision each legacy record to its correct workshop explicitly before use.

CREATE TABLE workshop_customer_access (
    shop_id INT NOT NULL,
    customer_id INT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (shop_id, customer_id),
    UNIQUE KEY uq_customer_single_workshop (customer_id),
    CONSTRAINT fk_customer_access_shop
        FOREIGN KEY (shop_id) REFERENCES shop_info(id) ON DELETE CASCADE,
    CONSTRAINT fk_customer_access_customer
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE workshop_vehicle_access (
    shop_id INT NOT NULL,
    vehicle_id INT UNSIGNED NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (shop_id, vehicle_id),
    UNIQUE KEY uq_vehicle_single_workshop (vehicle_id),
    CONSTRAINT fk_vehicle_access_shop
        FOREIGN KEY (shop_id) REFERENCES shop_info(id) ON DELETE CASCADE,
    CONSTRAINT fk_vehicle_access_vehicle
        FOREIGN KEY (vehicle_id) REFERENCES vehicles(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Provisioning checklist:
-- 1. Confirm every existing customer/vehicle belongs to a specific shop.
-- 2. Insert only explicitly verified mappings; never assign all records to shop 1.
-- 3. Ensure every vehicle's customer mapping has the same shop_id as its vehicle mapping.
-- 4. Run cross-shop negative tests before setting OAC_ENABLE_TENANT_DATA=true.
-- 5. No public endpoints may infer ownership from an ID supplied by a desktop client.
