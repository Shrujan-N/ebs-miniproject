-- ============================================================================
-- UE24CS343AB8 - Enterprise Business Systems (EBS) Mini Project
-- Company: VoltEdge Energy Systems Pvt. Ltd. (Bengaluru)
-- Module: Relational Database Schema (ERPNext-compatible structure)
-- Owner: Srujan (Database, Backend & Dashboard)
-- ============================================================================

PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS stock_ledger;
DROP TABLE IF EXISTS purchase_order_item;
DROP TABLE IF EXISTS purchase_order;
DROP TABLE IF EXISTS sales_order_item;
DROP TABLE IF EXISTS sales_order;
DROP TABLE IF EXISTS warehouse;
DROP TABLE IF EXISTS item;
DROP TABLE IF EXISTS supplier;
DROP TABLE IF EXISTS customer;
DROP TABLE IF EXISTS payment_term;
DROP TABLE IF EXISTS employee;

-- 1. MASTER ENTITY: Employee (Includes Team Members & SRNs)
CREATE TABLE employee (
    employee_id VARCHAR(20) PRIMARY KEY,
    employee_name VARCHAR(100) NOT NULL,
    srn VARCHAR(20) NOT NULL UNIQUE,
    designation VARCHAR(80) NOT NULL,
    department VARCHAR(60) NOT NULL,
    email VARCHAR(100) NOT NULL,
    status VARCHAR(20) DEFAULT 'Active'
);

-- 2. MASTER ENTITY: Payment Terms Template
CREATE TABLE payment_term (
    term_id VARCHAR(20) PRIMARY KEY,
    term_name VARCHAR(60) NOT NULL UNIQUE,
    credit_days INTEGER NOT NULL DEFAULT 0,
    advance_pct REAL NOT NULL DEFAULT 0.0,
    description VARCHAR(200)
);

-- 3. MASTER ENTITY: Customer
CREATE TABLE customer (
    customer_id VARCHAR(20) PRIMARY KEY,
    customer_name VARCHAR(120) NOT NULL,
    customer_group VARCHAR(60) NOT NULL,
    territory VARCHAR(60) NOT NULL,
    gstin VARCHAR(20) NOT NULL,
    contact_email VARCHAR(100),
    account_manager_id VARCHAR(20) NOT NULL,
    srn_tag VARCHAR(60) NOT NULL,
    FOREIGN KEY (account_manager_id) REFERENCES employee(employee_id)
);

-- 4. MASTER ENTITY: Supplier
CREATE TABLE supplier (
    supplier_id VARCHAR(20) PRIMARY KEY,
    supplier_name VARCHAR(120) NOT NULL,
    supplier_group VARCHAR(60) NOT NULL,
    city VARCHAR(60) NOT NULL,
    gstin VARCHAR(20) NOT NULL,
    lead_time_days INTEGER NOT NULL DEFAULT 7,
    procurement_officer_id VARCHAR(20) NOT NULL,
    srn_tag VARCHAR(60) NOT NULL,
    FOREIGN KEY (procurement_officer_id) REFERENCES employee(employee_id)
);

-- 5. MASTER ENTITY: Item / Product
CREATE TABLE item (
    item_code VARCHAR(25) PRIMARY KEY,
    item_name VARCHAR(120) NOT NULL,
    item_group VARCHAR(60) NOT NULL,
    uom VARCHAR(20) NOT NULL DEFAULT 'Nos',
    standard_selling_rate REAL NOT NULL,
    valuation_rate REAL NOT NULL,
    safety_stock INTEGER NOT NULL DEFAULT 10,
    created_by_srn VARCHAR(60) NOT NULL
);

-- 6. MASTER ENTITY: Warehouse
CREATE TABLE warehouse (
    warehouse_id VARCHAR(25) PRIMARY KEY,
    warehouse_name VARCHAR(100) NOT NULL,
    warehouse_type VARCHAR(50) NOT NULL,
    location VARCHAR(80) NOT NULL,
    capacity_units INTEGER NOT NULL,
    incharge_id VARCHAR(20) NOT NULL,
    FOREIGN KEY (incharge_id) REFERENCES employee(employee_id)
);

-- ============================================================================
-- TRANSACTION TABLES (Order-to-Cash & Procure-to-Pay Cycles)
-- ============================================================================

-- Transaction Table 1: Sales Order (Order-to-Cash Header)
CREATE TABLE sales_order (
    so_id VARCHAR(25) PRIMARY KEY,
    customer_id VARCHAR(20) NOT NULL,
    employee_id VARCHAR(20) NOT NULL,
    term_id VARCHAR(20) NOT NULL,
    order_date DATE NOT NULL,
    delivery_date DATE NOT NULL,
    workflow_stage VARCHAR(40) NOT NULL, -- Quotation, Sales Order, Delivery Note, Sales Invoice, Payment Received
    status VARCHAR(30) NOT NULL,         -- Completed, To Bill, To Deliver, Draft
    total_amount REAL NOT NULL,
    srn_reference VARCHAR(80) NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customer(customer_id),
    FOREIGN KEY (employee_id) REFERENCES employee(employee_id),
    FOREIGN KEY (term_id) REFERENCES payment_term(term_id)
);

-- Sales Order Line Items
CREATE TABLE sales_order_item (
    so_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    so_id VARCHAR(25) NOT NULL,
    item_code VARCHAR(25) NOT NULL,
    warehouse_id VARCHAR(25) NOT NULL,
    qty INTEGER NOT NULL,
    rate REAL NOT NULL,
    amount REAL NOT NULL,
    FOREIGN KEY (so_id) REFERENCES sales_order(so_id) ON DELETE CASCADE,
    FOREIGN KEY (item_code) REFERENCES item(item_code),
    FOREIGN KEY (warehouse_id) REFERENCES warehouse(warehouse_id)
);

-- Transaction Table 2: Purchase Order (Procure-to-Pay Header)
CREATE TABLE purchase_order (
    po_id VARCHAR(25) PRIMARY KEY,
    supplier_id VARCHAR(20) NOT NULL,
    employee_id VARCHAR(20) NOT NULL,
    term_id VARCHAR(20) NOT NULL,
    order_date DATE NOT NULL,
    expected_date DATE NOT NULL,
    workflow_stage VARCHAR(40) NOT NULL, -- Material Request, Purchase Order, Goods Receipt, Supplier Invoice, Payment Sent
    status VARCHAR(30) NOT NULL,         -- Completed, To Receive, To Bill, Submitted
    total_amount REAL NOT NULL,
    srn_reference VARCHAR(80) NOT NULL,
    FOREIGN KEY (supplier_id) REFERENCES supplier(supplier_id),
    FOREIGN KEY (employee_id) REFERENCES employee(employee_id),
    FOREIGN KEY (term_id) REFERENCES payment_term(term_id)
);

-- Purchase Order Line Items
CREATE TABLE purchase_order_item (
    po_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    po_id VARCHAR(25) NOT NULL,
    item_code VARCHAR(25) NOT NULL,
    warehouse_id VARCHAR(25) NOT NULL,
    qty INTEGER NOT NULL,
    rate REAL NOT NULL,
    amount REAL NOT NULL,
    FOREIGN KEY (po_id) REFERENCES purchase_order(po_id) ON DELETE CASCADE,
    FOREIGN KEY (item_code) REFERENCES item(item_code),
    FOREIGN KEY (warehouse_id) REFERENCES warehouse(warehouse_id)
);

-- Warehouse Stock Ledger (For Inventory Valuation Report & KPI)
CREATE TABLE stock_ledger (
    entry_id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_code VARCHAR(25) NOT NULL,
    warehouse_id VARCHAR(25) NOT NULL,
    available_qty INTEGER NOT NULL,
    valuation_rate REAL NOT NULL,
    stock_value REAL NOT NULL,
    last_updated DATE NOT NULL,
    FOREIGN KEY (item_code) REFERENCES item(item_code),
    FOREIGN KEY (warehouse_id) REFERENCES warehouse(warehouse_id)
);
