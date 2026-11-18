-- =============================================================================
-- VoltEdge Power Systems Pvt. Ltd. — Authentic ERPNext v16 MariaDB Schema
-- Target Engine: MariaDB 10.6+ / InnoDB (Frappe Framework v16, released 12 Jan 2026)
-- =============================================================================
-- Note: ERPNext uses MariaDB tables prefixed with `tab` (`tabSales Order`, `tabBin`, etc.),
-- string primary keys (`name VARCHAR(140)`), `docstatus` (0=Draft, 1=Submitted, 2=Cancelled),
-- and child table `parent` / `parenttype` / `parentfield` foreign keys.

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

CREATE DATABASE IF NOT EXISTS `_voltedge_erpnext_v16`
  DEFAULT CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;
USE `_voltedge_erpnext_v16`;

-- 1. Core Master: Employee (Project Officers)
CREATE TABLE IF NOT EXISTS `tabEmployee` (
  `name` VARCHAR(140) NOT NULL,
  `creation` DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6),
  `modified` DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
  `owner` VARCHAR(140) DEFAULT 'Administrator',
  `docstatus` INT(1) NOT NULL DEFAULT 0,
  `employee_name` VARCHAR(140) NOT NULL,
  `custom_srn` VARCHAR(32) NOT NULL UNIQUE,
  `designation` VARCHAR(140) NOT NULL,
  `department` VARCHAR(140) NOT NULL,
  `company_email` VARCHAR(140) NOT NULL UNIQUE,
  `status` VARCHAR(32) NOT NULL DEFAULT 'Active',
  PRIMARY KEY (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. Accounting Master: Payment Terms Template
CREATE TABLE IF NOT EXISTS `tabPayment Terms Template` (
  `name` VARCHAR(140) NOT NULL,
  `creation` DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6),
  `modified` DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
  `docstatus` INT(1) NOT NULL DEFAULT 0,
  `template_name` VARCHAR(140) NOT NULL,
  `credit_days` INT(11) NOT NULL DEFAULT 0,
  `description` TEXT,
  PRIMARY KEY (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. Selling Master: Customer
CREATE TABLE IF NOT EXISTS `tabCustomer` (
  `name` VARCHAR(140) NOT NULL,
  `creation` DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6),
  `modified` DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
  `docstatus` INT(1) NOT NULL DEFAULT 0,
  `customer_name` VARCHAR(140) NOT NULL,
  `customer_group` VARCHAR(140) NOT NULL,
  `territory` VARCHAR(140) NOT NULL,
  `tax_id` VARCHAR(24) NOT NULL,
  `credit_limit` DECIMAL(18,2) NOT NULL DEFAULT 0.00,
  `payment_terms` VARCHAR(140),
  `account_manager` VARCHAR(140),
  PRIMARY KEY (`name`),
  KEY `idx_customer_name` (`customer_name`),
  CONSTRAINT `fk_cust_terms` FOREIGN KEY (`payment_terms`) REFERENCES `tabPayment Terms Template` (`name`),
  CONSTRAINT `fk_cust_mgr` FOREIGN KEY (`account_manager`) REFERENCES `tabEmployee` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. Buying Master: Supplier
CREATE TABLE IF NOT EXISTS `tabSupplier` (
  `name` VARCHAR(140) NOT NULL,
  `creation` DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6),
  `modified` DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
  `docstatus` INT(1) NOT NULL DEFAULT 0,
  `supplier_name` VARCHAR(140) NOT NULL,
  `supplier_group` VARCHAR(140) NOT NULL,
  `country` VARCHAR(64) NOT NULL DEFAULT 'India',
  `tax_id` VARCHAR(24) NOT NULL,
  `payment_terms` VARCHAR(140),
  `custom_buyer_id` VARCHAR(140),
  PRIMARY KEY (`name`),
  KEY `idx_supplier_name` (`supplier_name`),
  CONSTRAINT `fk_sup_terms` FOREIGN KEY (`payment_terms`) REFERENCES `tabPayment Terms Template` (`name`),
  CONSTRAINT `fk_sup_buyer` FOREIGN KEY (`custom_buyer_id`) REFERENCES `tabEmployee` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 5. Stock Master: Item (Finished Goods & Raw Materials)
CREATE TABLE IF NOT EXISTS `tabItem` (
  `name` VARCHAR(140) NOT NULL,
  `creation` DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6),
  `modified` DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
  `docstatus` INT(1) NOT NULL DEFAULT 0,
  `item_code` VARCHAR(140) NOT NULL UNIQUE,
  `item_name` VARCHAR(140) NOT NULL,
  `item_group` VARCHAR(140) NOT NULL,
  `stock_uom` VARCHAR(32) NOT NULL DEFAULT 'Nos',
  `valuation_rate` DECIMAL(18,2) NOT NULL,
  `standard_rate` DECIMAL(18,2) NOT NULL,
  `safety_stock` INT(11) NOT NULL DEFAULT 5,
  `is_stock_item` INT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (`name`),
  KEY `idx_item_group` (`item_group`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 6. Stock Master: Warehouse
CREATE TABLE IF NOT EXISTS `tabWarehouse` (
  `name` VARCHAR(140) NOT NULL,
  `creation` DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6),
  `modified` DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
  `docstatus` INT(1) NOT NULL DEFAULT 0,
  `warehouse_name` VARCHAR(140) NOT NULL,
  `warehouse_type` VARCHAR(64) NOT NULL,
  `city` VARCHAR(64) NOT NULL,
  `company` VARCHAR(140) NOT NULL DEFAULT 'VoltEdge Power Systems Pvt. Ltd.',
  `custom_manager_id` VARCHAR(140),
  PRIMARY KEY (`name`),
  CONSTRAINT `fk_wh_mgr` FOREIGN KEY (`custom_manager_id`) REFERENCES `tabEmployee` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 7. Selling Transaction: Sales Order (Linked 5-Document O2C Chain)
CREATE TABLE IF NOT EXISTS `tabSales Order` (
  `name` VARCHAR(140) NOT NULL,
  `creation` DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6),
  `modified` DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
  `docstatus` INT(1) NOT NULL DEFAULT 1,
  `customer` VARCHAR(140) NOT NULL,
  `transaction_date` DATE NOT NULL,
  `delivery_date` DATE NOT NULL,
  `workflow_state` VARCHAR(64) NOT NULL,
  `status` VARCHAR(64) NOT NULL,
  `custom_quotation_id` VARCHAR(140),
  `custom_delivery_note_id` VARCHAR(140),
  `custom_sales_invoice_id` VARCHAR(140),
  `custom_payment_entry_id` VARCHAR(140),
  `net_total` DECIMAL(18,2) NOT NULL,
  `total_taxes_and_charges` DECIMAL(18,2) NOT NULL DEFAULT 0.00,
  `grand_total` DECIMAL(18,2) NOT NULL,
  `owner_employee` VARCHAR(140) NOT NULL,
  PRIMARY KEY (`name`),
  KEY `idx_so_customer` (`customer`),
  CONSTRAINT `fk_so_customer` FOREIGN KEY (`customer`) REFERENCES `tabCustomer` (`name`),
  CONSTRAINT `fk_so_owner` FOREIGN KEY (`owner_employee`) REFERENCES `tabEmployee` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 8. Selling Child Table: Sales Order Item
CREATE TABLE IF NOT EXISTS `tabSales Order Item` (
  `name` VARCHAR(140) NOT NULL,
  `parent` VARCHAR(140) NOT NULL,
  `parenttype` VARCHAR(140) NOT NULL DEFAULT 'Sales Order',
  `parentfield` VARCHAR(140) NOT NULL DEFAULT 'items',
  `idx` INT(11) NOT NULL DEFAULT 1,
  `item_code` VARCHAR(140) NOT NULL,
  `qty` DECIMAL(18,3) NOT NULL,
  `rate` DECIMAL(18,2) NOT NULL,
  `amount` DECIMAL(18,2) NOT NULL,
  PRIMARY KEY (`name`),
  KEY `idx_parent` (`parent`),
  CONSTRAINT `fk_soi_parent` FOREIGN KEY (`parent`) REFERENCES `tabSales Order` (`name`) ON DELETE CASCADE,
  CONSTRAINT `fk_soi_item` FOREIGN KEY (`item_code`) REFERENCES `tabItem` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 9. Buying Transaction: Purchase Order (Raw Materials Only + 5-Document P2P Chain)
CREATE TABLE IF NOT EXISTS `tabPurchase Order` (
  `name` VARCHAR(140) NOT NULL,
  `creation` DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6),
  `modified` DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
  `docstatus` INT(1) NOT NULL DEFAULT 1,
  `supplier` VARCHAR(140) NOT NULL,
  `transaction_date` DATE NOT NULL,
  `schedule_date` DATE NOT NULL,
  `workflow_state` VARCHAR(64) NOT NULL,
  `status` VARCHAR(64) NOT NULL,
  `custom_material_request_id` VARCHAR(140),
  `custom_purchase_receipt_id` VARCHAR(140),
  `custom_purchase_invoice_id` VARCHAR(140),
  `custom_payment_entry_id` VARCHAR(140),
  `net_total` DECIMAL(18,2) NOT NULL,
  `total_taxes_and_charges` DECIMAL(18,2) NOT NULL DEFAULT 0.00,
  `grand_total` DECIMAL(18,2) NOT NULL,
  `custom_buyer_id` VARCHAR(140) NOT NULL,
  PRIMARY KEY (`name`),
  KEY `idx_po_supplier` (`supplier`),
  CONSTRAINT `fk_po_supplier` FOREIGN KEY (`supplier`) REFERENCES `tabSupplier` (`name`),
  CONSTRAINT `fk_po_buyer` FOREIGN KEY (`custom_buyer_id`) REFERENCES `tabEmployee` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 10. Buying Child Table: Purchase Order Item
CREATE TABLE IF NOT EXISTS `tabPurchase Order Item` (
  `name` VARCHAR(140) NOT NULL,
  `parent` VARCHAR(140) NOT NULL,
  `parenttype` VARCHAR(140) NOT NULL DEFAULT 'Purchase Order',
  `parentfield` VARCHAR(140) NOT NULL DEFAULT 'items',
  `idx` INT(11) NOT NULL DEFAULT 1,
  `item_code` VARCHAR(140) NOT NULL,
  `qty` DECIMAL(18,3) NOT NULL,
  `rate` DECIMAL(18,2) NOT NULL,
  `amount` DECIMAL(18,2) NOT NULL,
  PRIMARY KEY (`name`),
  KEY `idx_parent` (`parent`),
  CONSTRAINT `fk_poi_parent` FOREIGN KEY (`parent`) REFERENCES `tabPurchase Order` (`name`) ON DELETE CASCADE,
  CONSTRAINT `fk_poi_item` FOREIGN KEY (`item_code`) REFERENCES `tabItem` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 11. Manufacturing / Inventory Transaction: Stock Entry
CREATE TABLE IF NOT EXISTS `tabStock Entry` (
  `name` VARCHAR(140) NOT NULL,
  `creation` DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6),
  `docstatus` INT(1) NOT NULL DEFAULT 1,
  `posting_date` DATE NOT NULL,
  `stock_entry_type` VARCHAR(64) NOT NULL,
  `custom_item_code` VARCHAR(140) NOT NULL,
  `to_warehouse` VARCHAR(140) NOT NULL,
  `fg_completed_qty` DECIMAL(18,3) NOT NULL,
  `valuation_rate` DECIMAL(18,2) NOT NULL,
  `remarks` TEXT,
  `owner` VARCHAR(140) NOT NULL,
  PRIMARY KEY (`name`),
  CONSTRAINT `fk_ste_item` FOREIGN KEY (`custom_item_code`) REFERENCES `tabItem` (`name`),
  CONSTRAINT `fk_ste_wh` FOREIGN KEY (`to_warehouse`) REFERENCES `tabWarehouse` (`name`),
  CONSTRAINT `fk_ste_owner` FOREIGN KEY (`owner`) REFERENCES `tabEmployee` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 12. Audit Log: Stock Ledger Entry (Immutable Event Log)
CREATE TABLE IF NOT EXISTS `tabStock Ledger Entry` (
  `name` VARCHAR(140) NOT NULL,
  `docstatus` INT(1) NOT NULL DEFAULT 1,
  `item_code` VARCHAR(140) NOT NULL,
  `warehouse` VARCHAR(140) NOT NULL,
  `posting_date` DATE NOT NULL,
  `voucher_type` VARCHAR(64) NOT NULL,
  `voucher_no` VARCHAR(140) NOT NULL,
  `actual_qty` DECIMAL(18,3) NOT NULL,
  `qty_after_transaction` DECIMAL(18,3) NOT NULL,
  `valuation_rate` DECIMAL(18,2) NOT NULL,
  `stock_value` DECIMAL(18,2) NOT NULL,
  `is_cancelled` INT(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (`name`),
  KEY `idx_sle_item_wh` (`item_code`, `warehouse`, `posting_date`),
  CONSTRAINT `fk_sle_item` FOREIGN KEY (`item_code`) REFERENCES `tabItem` (`name`),
  CONSTRAINT `fk_sle_wh` FOREIGN KEY (`warehouse`) REFERENCES `tabWarehouse` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 13. Live Calculated Stock Bin (`tabBin` in ERPNext)
CREATE TABLE IF NOT EXISTS `tabBin` (
  `name` VARCHAR(140) NOT NULL,
  `item_code` VARCHAR(140) NOT NULL,
  `warehouse` VARCHAR(140) NOT NULL,
  `actual_qty` DECIMAL(18,3) NOT NULL DEFAULT 0.000,
  `reserved_qty` DECIMAL(18,3) NOT NULL DEFAULT 0.000,
  `projected_qty` DECIMAL(18,3) NOT NULL DEFAULT 0.000,
  `valuation_rate` DECIMAL(18,2) NOT NULL DEFAULT 0.00,
  `stock_value` DECIMAL(18,2) NOT NULL DEFAULT 0.00,
  PRIMARY KEY (`name`),
  UNIQUE KEY `uq_bin_item_wh` (`item_code`, `warehouse`),
  CONSTRAINT `fk_bin_item` FOREIGN KEY (`item_code`) REFERENCES `tabItem` (`name`),
  CONSTRAINT `fk_bin_wh` FOREIGN KEY (`warehouse`) REFERENCES `tabWarehouse` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

SET FOREIGN_KEY_CHECKS = 1;
