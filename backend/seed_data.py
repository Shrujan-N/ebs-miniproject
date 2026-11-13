"""
Seed script for VoltEdge Energy Systems Pvt. Ltd. (Part A - ERP Database)
Course: UE24CS343AB8 Enterprise Business Systems
Owner: Srujan (Database, Backend & Dashboard)

Populates:
- 6 Master Data tables (employee, payment_term, customer, supplier, item, warehouse)
- 2 Transaction tables with 12 records each (sales_order + items, purchase_order + items)
- Stock ledger table for warehouse valuation reports
"""

import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "voltedge_ebs.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "schema.sql")

# ============================================================================
# TEAM CONFIGURATION (Update SRNs here if needed; embedded across all tables)
# ============================================================================
TEAM_MEMBERS = [
    {
        "emp_id": "HR-EMP-0001",
        "name": "Srujan",
        "srn": "PES1UG24CS001",
        "role": "Head of Database, Backend & Analytics",
        "dept": "IT & ERP Systems",
        "email": "srujan@voltedge-energy.in",
    },
    {
        "emp_id": "HR-EMP-0002",
        "name": "Eshaan",
        "srn": "PES1UG24CS002",
        "role": "Operations & Sales Director",
        "dept": "Sales & Order Management",
        "email": "eshaan@voltedge-energy.in",
    },
    {
        "emp_id": "HR-EMP-0003",
        "name": "Abhay",
        "srn": "PES1UG24CS003",
        "role": "Supply Chain & Procurement Lead",
        "dept": "Procurement & Logistics",
        "email": "abhay@voltedge-energy.in",
    },
    {
        "emp_id": "HR-EMP-0004",
        "name": "Siri",
        "srn": "PES1UG24CS004",
        "role": "Product Quality & Financial Controller",
        "dept": "Finance & Quality Control",
        "email": "siri@voltedge-energy.in",
    },
]


def init_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        cursor.executescript(f.read())

    # 1. Insert Employees (Team Members with SRNs)
    for m in TEAM_MEMBERS:
        cursor.execute(
            """
            INSERT INTO employee (employee_id, employee_name, srn, designation, department, email, status)
            VALUES (?, ?, ?, ?, ?, ?, 'Active')
            """,
            (m["emp_id"], f"{m['name']} ({m['srn']})", m["srn"], m["role"], m["dept"], m["email"]),
        )

    # 2. Insert Payment Terms
    payment_terms = [
        ("TERM-NET15", "Net 15 Days", 15, 0.0, "Full invoice settlement within 15 days of delivery"),
        ("TERM-NET30", "Net 30 Days", 30, 0.0, "Standard B2B 30-day credit cycle after invoice generation"),
        ("TERM-ADV50", "50% Advance Payment", 15, 50.0, "50% advance on order confirmation, balance on dispatch"),
        ("TERM-IMMED", "Immediate on Delivery", 0, 100.0, "100% RTGS/NEFT payment upon goods receipt inspection"),
    ]
    cursor.executemany(
        "INSERT INTO payment_term VALUES (?, ?, ?, ?, ?)",
        payment_terms,
    )

    # 3. Insert Customers (8 Realistic B2B Energy/Electrical Clients)
    customers = [
        ("CUST-2026-01", "Bengaluru Solar Solutions Pvt. Ltd.", "Commercial EPC", "Bengaluru Urban", "29AABCB1421B1Z5", "procurement@blrsolar.in", "HR-EMP-0002", "Managed by Eshaan [PES1UG24CS002]"),
        ("CUST-2026-02", "GreenGrid Energy Systems India", "Utility Scale", "Karnataka South", "29AAECG5519G1Z2", "orders@greengrid.co.in", "HR-EMP-0001", "Managed by Srujan [PES1UG24CS001]"),
        ("CUST-2026-03", "Deccan Power Infrastructure Ltd.", "Industrial Grid", "Hyderabad / South", "36AABCD8821D1Z8", "supply@deccanpower.in", "HR-EMP-0004", "Managed by Siri [PES1UG24CS004]"),
        ("CUST-2026-04", "Karnataka MicroGrid Corporation", "Government PSU", "Bengaluru Rural", "29AAACK9012M1Z1", "tenders@kmgrid.kar.nic.in", "HR-EMP-0003", "Managed by Abhay [PES1UG24CS003]"),
        ("CUST-2026-05", "Kaveri Industrial Renewables", "Manufacturing", "Mysuru Industrial", "29AABCK3340K1Z9", "purchase@kaverirenew.in", "HR-EMP-0002", "Managed by Eshaan [PES1UG24CS002]"),
        ("CUST-2026-06", "SunPeak Rooftop Engineering", "Commercial EPC", "Chennai / TN", "33AADCS7712P1Z4", "ops@sunpeaksolar.in", "HR-EMP-0001", "Managed by Srujan [PES1UG24CS001]"),
        ("CUST-2026-07", "Mysuru CleanTech Park Pvt. Ltd.", "Tech Park Infra", "Mysuru", "29AAFCM4109C1Z7", "facilities@mysurucleantech.in", "HR-EMP-0004", "Managed by Siri [PES1UG24CS004]"),
        ("CUST-2026-08", "Apex Substation Projects LLP", "Industrial Grid", "Hubballi-Dharwad", "29AAJFA2298A1Z3", "projects@apexsubstation.in", "HR-EMP-0003", "Managed by Abhay [PES1UG24CS003]"),
    ]
    cursor.executemany(
        "INSERT INTO customer VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        customers,
    )

    # 4. Insert Suppliers (6 Realistic Component & Raw Material Vendors)
    suppliers = [
        ("SUP-2026-01", "Texas Instruments India Distributor", "Semiconductors", "Bengaluru (Bagmane)", "29AAACT4011T1Z6", 5, "HR-EMP-0003", "Verified by Abhay [PES1UG24CS003]"),
        ("SUP-2026-02", "ElectroParts Peenya Pvt. Ltd.", "Passive Components", "Bengaluru (Peenya)", "29AABCE7812E1Z1", 3, "HR-EMP-0001", "Verified by Srujan [PES1UG24CS001]"),
        ("SUP-2026-03", "Bharat Power Semiconductors Ltd.", "Power Modules", "Pune / Bengaluru", "27AAACB9921B1Z4", 7, "HR-EMP-0002", "Verified by Eshaan [PES1UG24CS002]"),
        ("SUP-2026-04", "Delta Magnetics & Toroid Coils", "Transformers & Coils", "Chennai", "33AABCD5102M1Z8", 6, "HR-EMP-0004", "Verified by Siri [PES1UG24CS004]"),
        ("SUP-2026-05", "Hosur Precision SheetMetal Works", "IP65 Enclosures", "Hosur Industrial", "33AAACH6634H1Z2", 4, "HR-EMP-0003", "Verified by Abhay [PES1UG24CS003]"),
        ("SUP-2026-06", "LFP CellTech Solutions India", "Battery Subsystems", "Hyderabad", "36AADCL8190C1Z5", 8, "HR-EMP-0001", "Verified by Srujan [PES1UG24CS001]"),
    ]
    cursor.executemany(
        "INSERT INTO supplier VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        suppliers,
    )

    # 5. Insert Products / Items (Finished Goods + Raw Materials)
    items = [
        ("ITM-INV-5KW", "5kW Hybrid Solar Inverter (IP65)", "Finished Goods", "Nos", 68000.0, 49500.0, 15, "Srujan [PES1UG24CS001]"),
        ("ITM-INV-10KW", "10kW Three-Phase String Inverter", "Finished Goods", "Nos", 118000.0, 86000.0, 10, "Eshaan [PES1UG24CS002]"),
        ("ITM-BMS-48V", "48V 100A Smart LiFePO4 BMS Controller", "Finished Goods", "Nos", 14500.0, 9800.0, 30, "Siri [PES1UG24CS004]"),
        ("ITM-CNV-25KVA", "25kVA Industrial AC-DC Power Converter", "Finished Goods", "Nos", 165000.0, 122000.0, 8, "Abhay [PES1UG24CS003]"),
        ("ITM-SPD-1000V", "1000V DC Surge Protection Device Box", "Finished Goods", "Nos", 8500.0, 5400.0, 40, "Srujan [PES1UG24CS001]"),
        ("ITM-PNL-LT400", "400V LT Distribution & Synchronization Panel", "Finished Goods", "Nos", 210000.0, 154000.0, 5, "Eshaan [PES1UG24CS002]"),
        ("ITM-RAW-MOSFET", "1200V SiC MOSFET Half-Bridge Module", "Raw Material", "Nos", 4200.0, 3400.0, 100, "Abhay [PES1UG24CS003]"),
        ("ITM-RAW-COIL", "High-Frequency Toroidal Copper Inductor", "Raw Material", "Nos", 2600.0, 1950.0, 80, "Siri [PES1UG24CS004]"),
        ("ITM-RAW-CHAS", "Powder-Coated Aluminum Inverter Chassis", "Raw Material", "Nos", 3800.0, 2900.0, 50, "Srujan [PES1UG24CS001]"),
    ]
    cursor.executemany(
        "INSERT INTO item VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        items,
    )

    # 6. Insert Warehouses
    warehouses = [
        ("WH-PEENYA-RAW", "Peenya Raw Material Store - BLR", "Raw Material", "Peenya Phase II, Bengaluru", 2500, "HR-EMP-0003"),
        ("WH-WHITEFIELD-FG", "Whitefield Finished Goods Hub - BLR", "Finished Goods", "Whitefield EPIP, Bengaluru", 1200, "HR-EMP-0001"),
        ("WH-ECITY-ASSY", "Electronic City Work-in-Progress Floor", "WIP Store", "Electronic City Ph I, Bengaluru", 800, "HR-EMP-0002"),
        ("WH-BOMMA-QA", "Bommasandra Quality Inspection Store", "QA & Quarantine", "Bommasandra Ind. Area, Bengaluru", 600, "HR-EMP-0004"),
    ]
    cursor.executemany(
        "INSERT INTO warehouse VALUES (?, ?, ?, ?, ?, ?)",
        warehouses,
    )

    # ========================================================================
    # 7. Populate 12 Realistic Sales Orders (Order-to-Cash Workflow)
    # ========================================================================
    # Format: (so_id, customer_id, emp_id, term_id, order_date, delivery_date, stage, status, srn_ref, [(item_code, wh, qty, rate)])
    sales_orders_data = [
        (
            "SAL-ORD-2026-0001", "CUST-2026-01", "HR-EMP-0002", "TERM-NET30",
            "2026-05-12", "2026-05-22", "Payment Received", "Completed",
            "Processed by Eshaan (PES1UG24CS002)",
            [("ITM-INV-5KW", "WH-WHITEFIELD-FG", 6, 68000.0), ("ITM-SPD-1000V", "WH-WHITEFIELD-FG", 10, 8500.0)]
        ),
        (
            "SAL-ORD-2026-0002", "CUST-2026-02", "HR-EMP-0001", "TERM-ADV50",
            "2026-06-08", "2026-06-19", "Payment Received", "Completed",
            "Processed by Srujan (PES1UG24CS001)",
            [("ITM-INV-10KW", "WH-WHITEFIELD-FG", 5, 118000.0), ("ITM-BMS-48V", "WH-WHITEFIELD-FG", 8, 14500.0)]
        ),
        (
            "SAL-ORD-2026-0003", "CUST-2026-03", "HR-EMP-0004", "TERM-NET30",
            "2026-06-24", "2026-07-05", "Payment Received", "Completed",
            "Processed by Siri (PES1UG24CS004)",
            [("ITM-CNV-25KVA", "WH-WHITEFIELD-FG", 3, 165000.0)]
        ),
        (
            "SAL-ORD-2026-0004", "CUST-2026-04", "HR-EMP-0003", "TERM-NET15",
            "2026-07-11", "2026-07-24", "Payment Received", "Completed",
            "Processed by Abhay (PES1UG24CS003)",
            [("ITM-PNL-LT400", "WH-WHITEFIELD-FG", 2, 210000.0), ("ITM-SPD-1000V", "WH-WHITEFIELD-FG", 12, 8500.0)]
        ),
        (
            "SAL-ORD-2026-0005", "CUST-2026-05", "HR-EMP-0002", "TERM-NET15",
            "2026-07-28", "2026-08-08", "Payment Received", "Completed",
            "Processed by Eshaan (PES1UG24CS002)",
            [("ITM-INV-5KW", "WH-WHITEFIELD-FG", 8, 68000.0)]
        ),
        (
            "SAL-ORD-2026-0006", "CUST-2026-06", "HR-EMP-0001", "TERM-IMMED",
            "2026-08-14", "2026-08-23", "Payment Received", "Completed",
            "Processed by Srujan (PES1UG24CS001)",
            [("ITM-BMS-48V", "WH-WHITEFIELD-FG", 20, 14500.0), ("ITM-INV-5KW", "WH-WHITEFIELD-FG", 4, 68000.0)]
        ),
        (
            "SAL-ORD-2026-0007", "CUST-2026-07", "HR-EMP-0004", "TERM-NET30",
            "2026-08-29", "2026-09-10", "Payment Received", "Completed",
            "Processed by Siri (PES1UG24CS004)",
            [("ITM-INV-10KW", "WH-WHITEFIELD-FG", 4, 118000.0), ("ITM-SPD-1000V", "WH-WHITEFIELD-FG", 8, 8500.0)]
        ),
        (
            "SAL-ORD-2026-0008", "CUST-2026-08", "HR-EMP-0003", "TERM-ADV50",
            "2026-09-09", "2026-09-21", "Payment Received", "Completed",
            "Processed by Abhay (PES1UG24CS003)",
            [("ITM-PNL-LT400", "WH-WHITEFIELD-FG", 3, 210000.0)]
        ),
        (
            "SAL-ORD-2026-0009", "CUST-2026-01", "HR-EMP-0001", "TERM-NET15",
            "2026-09-25", "2026-10-06", "Sales Invoice", "To Receive Payment",
            "Processed by Srujan (PES1UG24CS001)",
            [("ITM-INV-10KW", "WH-WHITEFIELD-FG", 5, 118000.0), ("ITM-BMS-48V", "WH-WHITEFIELD-FG", 10, 14500.0)]
        ),
        (
            "SAL-ORD-2026-0010", "CUST-2026-02", "HR-EMP-0002", "TERM-NET30",
            "2026-10-07", "2026-10-18", "Delivery Note", "To Bill",
            "Processed by Eshaan (PES1UG24CS002)",
            [("ITM-CNV-25KVA", "WH-WHITEFIELD-FG", 4, 165000.0)]
        ),
        (
            "SAL-ORD-2026-0011", "CUST-2026-03", "HR-EMP-0004", "TERM-ADV50",
            "2026-10-21", "2026-11-04", "Sales Order", "To Deliver and Bill",
            "Processed by Siri (PES1UG24CS004)",
            [("ITM-INV-5KW", "WH-WHITEFIELD-FG", 7, 68000.0), ("ITM-SPD-1000V", "WH-WHITEFIELD-FG", 14, 8500.0)]
        ),
        (
            "SAL-ORD-2026-0012", "CUST-2026-05", "HR-EMP-0003", "TERM-NET15",
            "2026-11-03", "2026-11-15", "Quotation", "Draft / Quoted",
            "Processed by Abhay (PES1UG24CS003)",
            [("ITM-PNL-LT400", "WH-WHITEFIELD-FG", 2, 210000.0), ("ITM-BMS-48V", "WH-WHITEFIELD-FG", 6, 14500.0)]
        ),
    ]

    for so_id, cust_id, emp_id, term_id, o_date, d_date, stage, status, srn_ref, line_items in sales_orders_data:
        total_amt = sum(q * r for _, _, q, r in line_items)
        cursor.execute(
            """
            INSERT INTO sales_order (so_id, customer_id, employee_id, term_id, order_date, delivery_date, workflow_stage, status, total_amount, srn_reference)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (so_id, cust_id, emp_id, term_id, o_date, d_date, stage, status, total_amt, srn_ref),
        )
        for item_code, wh_id, qty, rate in line_items:
            cursor.execute(
                """
                INSERT INTO sales_order_item (so_id, item_code, warehouse_id, qty, rate, amount)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (so_id, item_code, wh_id, qty, rate, qty * rate),
            )

    # ========================================================================
    # 8. Populate 12 Realistic Purchase Orders (Procure-to-Pay Workflow)
    # ========================================================================
    purchase_orders_data = [
        (
            "PUR-ORD-2026-0001", "SUP-2026-01", "HR-EMP-0003", "TERM-NET30",
            "2026-05-05", "2026-05-12", "Payment Sent", "Completed",
            "Approved by Abhay (PES1UG24CS003)",
            [("ITM-RAW-MOSFET", "WH-PEENYA-RAW", 120, 3400.0)]
        ),
        (
            "PUR-ORD-2026-0002", "SUP-2026-02", "HR-EMP-0001", "TERM-NET15",
            "2026-05-20", "2026-05-25", "Payment Sent", "Completed",
            "Approved by Srujan (PES1UG24CS001)",
            [("ITM-RAW-COIL", "WH-PEENYA-RAW", 140, 1950.0)]
        ),
        (
            "PUR-ORD-2026-0003", "SUP-2026-05", "HR-EMP-0002", "TERM-NET30",
            "2026-06-10", "2026-06-16", "Payment Sent", "Completed",
            "Approved by Eshaan (PES1UG24CS002)",
            [("ITM-RAW-CHAS", "WH-PEENYA-RAW", 90, 2900.0)]
        ),
        (
            "PUR-ORD-2026-0004", "SUP-2026-03", "HR-EMP-0004", "TERM-ADV50",
            "2026-06-27", "2026-07-04", "Payment Sent", "Completed",
            "Approved by Siri (PES1UG24CS004)",
            [("ITM-RAW-MOSFET", "WH-PEENYA-RAW", 150, 3400.0)]
        ),
        (
            "PUR-ORD-2026-0005", "SUP-2026-04", "HR-EMP-0003", "TERM-NET15",
            "2026-07-15", "2026-07-22", "Payment Sent", "Completed",
            "Approved by Abhay (PES1UG24CS003)",
            [("ITM-RAW-COIL", "WH-PEENYA-RAW", 180, 1950.0)]
        ),
        (
            "PUR-ORD-2026-0006", "SUP-2026-06", "HR-EMP-0001", "TERM-NET30",
            "2026-08-03", "2026-08-11", "Payment Sent", "Completed",
            "Approved by Srujan (PES1UG24CS001)",
            [("ITM-BMS-48V", "WH-BOMMA-QA", 35, 9800.0)]
        ),
        (
            "PUR-ORD-2026-0007", "SUP-2026-01", "HR-EMP-0002", "TERM-NET30",
            "2026-08-21", "2026-08-28", "Payment Sent", "Completed",
            "Approved by Eshaan (PES1UG24CS002)",
            [("ITM-RAW-MOSFET", "WH-PEENYA-RAW", 130, 3400.0)]
        ),
        (
            "PUR-ORD-2026-0008", "SUP-2026-05", "HR-EMP-0004", "TERM-IMMED",
            "2026-09-08", "2026-09-13", "Payment Sent", "Completed",
            "Approved by Siri (PES1UG24CS004)",
            [("ITM-RAW-CHAS", "WH-PEENYA-RAW", 110, 2900.0)]
        ),
        (
            "PUR-ORD-2026-0009", "SUP-2026-02", "HR-EMP-0001", "TERM-NET15",
            "2026-09-26", "2026-10-01", "Supplier Invoice", "To Pay",
            "Approved by Srujan (PES1UG24CS001)",
            [("ITM-SPD-1000V", "WH-BOMMA-QA", 50, 5400.0)]
        ),
        (
            "PUR-ORD-2026-0010", "SUP-2026-03", "HR-EMP-0003", "TERM-NET30",
            "2026-10-12", "2026-10-19", "Goods Receipt", "To Bill",
            "Approved by Abhay (PES1UG24CS003)",
            [("ITM-RAW-MOSFET", "WH-PEENYA-RAW", 110, 3400.0)]
        ),
        (
            "PUR-ORD-2026-0011", "SUP-2026-04", "HR-EMP-0002", "TERM-ADV50",
            "2026-10-25", "2026-11-02", "Purchase Order", "To Receive and Bill",
            "Approved by Eshaan (PES1UG24CS002)",
            [("ITM-RAW-COIL", "WH-PEENYA-RAW", 150, 1950.0)]
        ),
        (
            "PUR-ORD-2026-0012", "SUP-2026-06", "HR-EMP-0004", "TERM-NET30",
            "2026-11-05", "2026-11-14", "Material Request", "Requisition Approved",
            "Approved by Siri (PES1UG24CS004)",
            [("ITM-BMS-48V", "WH-BOMMA-QA", 30, 9800.0)]
        ),
    ]

    for po_id, sup_id, emp_id, term_id, o_date, e_date, stage, status, srn_ref, line_items in purchase_orders_data:
        total_amt = sum(q * r for _, _, q, r in line_items)
        cursor.execute(
            """
            INSERT INTO purchase_order (po_id, supplier_id, employee_id, term_id, order_date, expected_date, workflow_stage, status, total_amount, srn_reference)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (po_id, sup_id, emp_id, term_id, o_date, e_date, stage, status, total_amt, srn_ref),
        )
        for item_code, wh_id, qty, rate in line_items:
            cursor.execute(
                """
                INSERT INTO purchase_order_item (po_id, item_code, warehouse_id, qty, rate, amount)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (po_id, item_code, wh_id, qty, rate, qty * rate),
            )

    # ========================================================================
    # 9. Populate Stock Ledger for Warehouse Valuation Report
    # ========================================================================
    stock_entries = [
        ("ITM-INV-5KW", "WH-WHITEFIELD-FG", 18, 49500.0, 18 * 49500.0, "2026-11-10"),
        ("ITM-INV-10KW", "WH-WHITEFIELD-FG", 11, 86000.0, 11 * 86000.0, "2026-11-10"),
        ("ITM-BMS-48V", "WH-WHITEFIELD-FG", 42, 9800.0, 42 * 9800.0, "2026-11-10"),
        ("ITM-CNV-25KVA", "WH-WHITEFIELD-FG", 6, 122000.0, 6 * 122000.0, "2026-11-10"),
        ("ITM-SPD-1000V", "WH-BOMMA-QA", 55, 5400.0, 55 * 5400.0, "2026-11-10"),
        ("ITM-PNL-LT400", "WH-ECITY-ASSY", 4, 154000.0, 4 * 154000.0, "2026-11-10"),
        ("ITM-RAW-MOSFET", "WH-PEENYA-RAW", 240, 3400.0, 240 * 3400.0, "2026-11-10"),
        ("ITM-RAW-COIL", "WH-PEENYA-RAW", 190, 1950.0, 190 * 1950.0, "2026-11-10"),
        ("ITM-RAW-CHAS", "WH-PEENYA-RAW", 85, 2900.0, 85 * 2900.0, "2026-11-10"),
    ]
    cursor.executemany(
        """
        INSERT INTO stock_ledger (item_code, warehouse_id, available_qty, valuation_rate, stock_value, last_updated)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        stock_entries,
    )

    conn.commit()
    conn.close()
    print(f"[OK] VoltEdge database initialized at: {DB_PATH}")


if __name__ == "__main__":
    init_database()
