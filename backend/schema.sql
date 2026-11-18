-- =============================================================================
-- VoltEdge Power Systems Pvt. Ltd. — Local SQLite Schema (Offline Prototype Mirror)
-- Models ERPNext v16 MariaDB entities locally for zero-dependency execution.
-- Authentic MariaDB `tab*` DDL is provided in `backend/erpnext_mariadb_schema.sql`.
-- =============================================================================

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS employee (
    employee_id TEXT PRIMARY KEY,
    employee_name TEXT NOT NULL,
    srn TEXT NOT NULL UNIQUE,
    designation TEXT NOT NULL,
    department TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    status TEXT NOT NULL DEFAULT 'Active'
);

CREATE TABLE IF NOT EXISTS payment_term (
    payment_term_id TEXT PRIMARY KEY,
    term_name TEXT NOT NULL,
    credit_days INTEGER NOT NULL,
    description TEXT
);

CREATE TABLE IF NOT EXISTS customer (
    customer_id TEXT PRIMARY KEY,
    customer_name TEXT NOT NULL,
    customer_group TEXT NOT NULL,
    territory TEXT NOT NULL,
    gstin TEXT NOT NULL,
    credit_limit REAL NOT NULL DEFAULT 0,
    default_payment_term TEXT,
    account_manager_id TEXT,
    FOREIGN KEY (default_payment_term) REFERENCES payment_term(payment_term_id),
    FOREIGN KEY (account_manager_id) REFERENCES employee(employee_id)
);

CREATE TABLE IF NOT EXISTS supplier (
    supplier_id TEXT PRIMARY KEY,
    supplier_name TEXT NOT NULL,
    supplier_group TEXT NOT NULL,
    country TEXT NOT NULL DEFAULT 'India',
    gstin TEXT NOT NULL,
    default_payment_term TEXT,
    buyer_id TEXT,
    FOREIGN KEY (default_payment_term) REFERENCES payment_term(payment_term_id),
    FOREIGN KEY (buyer_id) REFERENCES employee(employee_id)
);

CREATE TABLE IF NOT EXISTS item (
    item_code TEXT PRIMARY KEY,
    item_name TEXT NOT NULL,
    item_group TEXT NOT NULL,
    uom TEXT NOT NULL DEFAULT 'Nos',
    valuation_rate REAL NOT NULL,
    selling_rate REAL NOT NULL,
    reorder_level INTEGER NOT NULL DEFAULT 5
);

CREATE TABLE IF NOT EXISTS warehouse (
    warehouse_id TEXT PRIMARY KEY,
    warehouse_name TEXT NOT NULL,
    warehouse_type TEXT NOT NULL,
    city TEXT NOT NULL,
    manager_id TEXT,
    FOREIGN KEY (manager_id) REFERENCES employee(employee_id)
);

-- Linked Order-to-Cash (O2C) chain: Quotation -> Sales Order -> Delivery Note -> Sales Invoice -> Payment Entry
CREATE TABLE IF NOT EXISTS sales_order (
    so_id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL,
    order_date TEXT NOT NULL,
    delivery_date TEXT NOT NULL,
    workflow_stage TEXT NOT NULL,
    status TEXT NOT NULL,
    quotation_id TEXT,
    delivery_note_id TEXT,
    sales_invoice_id TEXT,
    payment_entry_id TEXT,
    net_total REAL NOT NULL DEFAULT 0,
    gst_amount REAL NOT NULL DEFAULT 0,
    total_amount REAL NOT NULL,
    owner_emp_id TEXT NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customer(customer_id),
    FOREIGN KEY (owner_emp_id) REFERENCES employee(employee_id)
);

CREATE TABLE IF NOT EXISTS sales_order_item (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    so_id TEXT NOT NULL,
    item_code TEXT NOT NULL,
    qty INTEGER NOT NULL,
    rate REAL NOT NULL,
    amount REAL NOT NULL,
    FOREIGN KEY (so_id) REFERENCES sales_order(so_id) ON DELETE CASCADE,
    FOREIGN KEY (item_code) REFERENCES item(item_code)
);

-- Linked Procure-to-Pay (P2P) chain: Material Request -> Purchase Order -> Purchase Receipt -> Purchase Invoice -> Payment Entry
CREATE TABLE IF NOT EXISTS purchase_order (
    po_id TEXT PRIMARY KEY,
    supplier_id TEXT NOT NULL,
    order_date TEXT NOT NULL,
    schedule_date TEXT NOT NULL,
    workflow_stage TEXT NOT NULL,
    status TEXT NOT NULL,
    material_request_id TEXT,
    purchase_receipt_id TEXT,
    purchase_invoice_id TEXT,
    payment_entry_id TEXT,
    net_total REAL NOT NULL DEFAULT 0,
    gst_amount REAL NOT NULL DEFAULT 0,
    total_amount REAL NOT NULL,
    buyer_emp_id TEXT NOT NULL,
    FOREIGN KEY (supplier_id) REFERENCES supplier(supplier_id),
    FOREIGN KEY (buyer_emp_id) REFERENCES employee(employee_id)
);

CREATE TABLE IF NOT EXISTS purchase_order_item (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    po_id TEXT NOT NULL,
    item_code TEXT NOT NULL,
    qty INTEGER NOT NULL,
    rate REAL NOT NULL,
    amount REAL NOT NULL,
    FOREIGN KEY (po_id) REFERENCES purchase_order(po_id) ON DELETE CASCADE,
    FOREIGN KEY (item_code) REFERENCES item(item_code)
);

-- Manufacturing / Opening Stock Entries (Feeds Stock Ledger Calculation)
CREATE TABLE IF NOT EXISTS stock_entry (
    stock_entry_id TEXT PRIMARY KEY,
    posting_date TEXT NOT NULL,
    purpose TEXT NOT NULL,
    item_code TEXT NOT NULL,
    warehouse_id TEXT NOT NULL,
    qty INTEGER NOT NULL,
    valuation_rate REAL NOT NULL,
    remarks TEXT,
    owner_emp_id TEXT NOT NULL,
    FOREIGN KEY (item_code) REFERENCES item(item_code),
    FOREIGN KEY (warehouse_id) REFERENCES warehouse(warehouse_id),
    FOREIGN KEY (owner_emp_id) REFERENCES employee(employee_id)
);

-- Immutable Event Log generated mathematically from Stock Entry, Purchase Receipt, and Delivery Note
CREATE TABLE IF NOT EXISTS stock_ledger_entry (
    sle_id TEXT PRIMARY KEY,
    item_code TEXT NOT NULL,
    warehouse_id TEXT NOT NULL,
    posting_date TEXT NOT NULL,
    voucher_type TEXT NOT NULL,
    voucher_no TEXT NOT NULL,
    actual_qty INTEGER NOT NULL,
    qty_after_transaction INTEGER NOT NULL,
    valuation_rate REAL NOT NULL,
    stock_value REAL NOT NULL,
    FOREIGN KEY (item_code) REFERENCES item(item_code),
    FOREIGN KEY (warehouse_id) REFERENCES warehouse(warehouse_id)
);

-- Summary Bin View Table (Computed via recalculate_stock_ledger, never hand-typed)
CREATE TABLE IF NOT EXISTS stock_ledger (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_code TEXT NOT NULL,
    warehouse_id TEXT NOT NULL,
    actual_qty INTEGER NOT NULL,
    reserved_qty INTEGER NOT NULL DEFAULT 0,
    available_qty INTEGER NOT NULL,
    stock_value REAL NOT NULL,
    last_updated TEXT NOT NULL,
    UNIQUE(item_code, warehouse_id),
    FOREIGN KEY (item_code) REFERENCES item(item_code),
    FOREIGN KEY (warehouse_id) REFERENCES warehouse(warehouse_id)
);
