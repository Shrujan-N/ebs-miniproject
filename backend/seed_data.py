"""
VoltEdge Power Systems Pvt. Ltd. — Database Seeder & Stock Ledger Calculator
==========================================================================
Populates 13 SQLite tables modeling ERPNext v16 entities (authentically
mirrored to MariaDB `tab*` DDL in `backend/erpnext_mariadb_schema.sql`):
- 4 PES University Project Officers (placeholder SRNs kept in TEAM_MEMBERS)
- 12 Items (6 Finished Goods + 6 Raw Materials)
- 12 Sales Orders with full 5-document linked O2C chains (QTN -> SO -> DN -> SINV -> PAY)
- 12 Purchase Orders (Raw Materials ONLY) with full 5-document P2P chains (MR -> PO -> PR -> PINV -> PAY)
- 24 Manufacturing & Material Issue Stock Entries generating FG & consuming RM
- Mathematically calculated `stock_ledger_entry` and `stock_ledger` (`recalculate_stock_ledger`)
"""

import os
import sqlite3
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "voltedge_ebs.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "backend", "schema.sql")

# Project Team Members & Official PES University SRNs
TEAM_MEMBERS = [
    {
        "employee_id": "HR-EMP-0001",
        "employee_name": "SHRUJAN N",
        "srn": "PES1UG24CS624",
        "designation": "Sales & CRM Manager",
        "department": "Sales & Operations",
        "email": "shrujan@voltedge-power.in",
        "status": "Active",
    },
    {
        "employee_id": "HR-EMP-0002",
        "employee_name": "ESHAAN K",
        "srn": "PES1UG24EE012",
        "designation": "Procurement & SCM Lead",
        "department": "Procurement & Logistics",
        "email": "eshaan@voltedge-power.in",
        "status": "Active",
    },
    {
        "employee_id": "HR-EMP-0003",
        "employee_name": "ABHAY A KATTI",
        "srn": "PES1UG22EE001",
        "designation": "Manufacturing & Quality Lead",
        "department": "Production & QC",
        "email": "abhay@voltedge-power.in",
        "status": "Active",
    },
    {
        "employee_id": "HR-EMP-0004",
        "employee_name": "SIRI S S",
        "srn": "PES1UG24CS627",
        "designation": "Finance & ERP Systems Admin",
        "department": "Finance & IT",
        "email": "siri@voltedge-power.in",
        "status": "Active",
    },
]

RECEIVED_PO_STAGES = ("Purchase Receipt", "Purchase Invoice", "Payment Settled")
DELIVERED_SO_STAGES = ("Delivery Note", "Sales Invoice", "Payment Received")


def recalculate_stock_ledger(conn: sqlite3.Connection) -> None:
    """Mathematically compute `stock_ledger_entry` and `stock_ledger` from transactions.

    Zero balances are hardcoded: every SKU quantity is derived chronologically from
    Material Receipts (Purchase Receipts), Manufacturing Stock Entries, and Delivery Notes.
    """
    cur = conn.cursor()
    cur.execute("DELETE FROM stock_ledger_entry")
    cur.execute("DELETE FROM stock_ledger")

    events = []

    # 1. Purchase Receipts (inflows into WH-PEENYA-RAW)
    po_rows = cur.execute(
        """
        SELECT po.schedule_date AS posting_date,
               'Purchase Receipt' AS voucher_type,
               COALESCE(po.purchase_receipt_id, po.po_id) AS voucher_no,
               poi.item_code,
               'WH-PEENYA-RAW' AS warehouse_id,
               poi.qty AS actual_qty,
               i.valuation_rate
        FROM purchase_order po
        JOIN purchase_order_item poi ON po.po_id = poi.po_id
        JOIN item i ON poi.item_code = i.item_code
        WHERE po.workflow_stage IN ('Purchase Receipt', 'Purchase Invoice', 'Payment Settled')
        """
    ).fetchall()
    for row in po_rows:
        events.append({
            "posting_date": row[0],
            "priority": 0,
            "voucher_type": row[1],
            "voucher_no": row[2],
            "item_code": row[3],
            "warehouse_id": row[4],
            "actual_qty": int(row[5]),
            "valuation_rate": float(row[6]),
        })

    # 2. Stock Entries (Raw Material issues -qty and Manufacturing FG completions +qty)
    ste_rows = cur.execute(
        """
        SELECT posting_date, purpose, stock_entry_id, item_code, warehouse_id, qty, valuation_rate
        FROM stock_entry
        """
    ).fetchall()
    for row in ste_rows:
        prio = 1 if int(row[5]) < 0 else 2
        events.append({
            "posting_date": row[0],
            "priority": prio,
            "voucher_type": row[1],
            "voucher_no": row[2],
            "item_code": row[3],
            "warehouse_id": row[4],
            "actual_qty": int(row[5]),
            "valuation_rate": float(row[6]),
        })

    # 3. Delivery Notes (outflows from WH-WHITEFIELD-FG)
    so_rows = cur.execute(
        """
        SELECT so.delivery_date AS posting_date,
               'Delivery Note' AS voucher_type,
               COALESCE(so.delivery_note_id, so.so_id) AS voucher_no,
               soi.item_code,
               'WH-WHITEFIELD-FG' AS warehouse_id,
               -soi.qty AS actual_qty,
               i.valuation_rate
        FROM sales_order so
        JOIN sales_order_item soi ON so.so_id = soi.so_id
        JOIN item i ON soi.item_code = i.item_code
        WHERE so.workflow_stage IN ('Delivery Note', 'Sales Invoice', 'Payment Received')
        """
    ).fetchall()
    for row in so_rows:
        events.append({
            "posting_date": row[0],
            "priority": 3,
            "voucher_type": row[1],
            "voucher_no": row[2],
            "item_code": row[3],
            "warehouse_id": row[4],
            "actual_qty": int(row[5]),
            "valuation_rate": float(row[6]),
        })

    events.sort(key=lambda e: (e["posting_date"], e["priority"], e["voucher_no"], e["item_code"]))

    running_qty = {}
    sle_records = []
    for idx, ev in enumerate(events, start=1):
        key = (ev["item_code"], ev["warehouse_id"])
        new_qty = running_qty.get(key, 0) + ev["actual_qty"]
        running_qty[key] = new_qty
        stock_val = round(new_qty * ev["valuation_rate"], 2)
        sle_records.append((
            f"SLE-2026-{idx:04d}",
            ev["item_code"],
            ev["warehouse_id"],
            ev["posting_date"],
            ev["voucher_type"],
            ev["voucher_no"],
            ev["actual_qty"],
            new_qty,
            ev["valuation_rate"],
            stock_val,
        ))

    cur.executemany(
        """
        INSERT INTO stock_ledger_entry (
            sle_id, item_code, warehouse_id, posting_date, voucher_type,
            voucher_no, actual_qty, qty_after_transaction, valuation_rate, stock_value
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        sle_records,
    )

    # Calculate reserved quantities for submitted Sales Orders awaiting Delivery Note
    reserved_rows = cur.execute(
        """
        SELECT soi.item_code, SUM(soi.qty)
        FROM sales_order so
        JOIN sales_order_item soi ON so.so_id = soi.so_id
        WHERE so.workflow_stage = 'Sales Order'
        GROUP BY soi.item_code
        """
    ).fetchall()
    reserved_map = {r[0]: int(r[1]) for r in reserved_rows}

    # Aggregate final warehouse balances from immutable stock_ledger_entry log
    bin_rows = cur.execute(
        """
        SELECT sle.item_code,
               sle.warehouse_id,
               SUM(sle.actual_qty) AS actual_qty,
               i.valuation_rate,
               MAX(sle.posting_date) AS last_updated
        FROM stock_ledger_entry sle
        JOIN item i ON sle.item_code = i.item_code
        GROUP BY sle.item_code, sle.warehouse_id
        ORDER BY i.item_group, sle.item_code
        """
    ).fetchall()

    ledger_rows = []
    for item_code, wh_id, actual_qty, val_rate, last_dt in bin_rows:
        actual = int(actual_qty)
        reserved = reserved_map.get(item_code, 0) if wh_id == "WH-WHITEFIELD-FG" else 0
        available = actual - reserved
        stock_val = round(actual * float(val_rate), 2)
        ledger_rows.append((
            item_code,
            wh_id,
            actual,
            reserved,
            available,
            stock_val,
            f"{last_dt} {datetime.now().strftime('%H:%M:%S')}",
        ))

    cur.executemany(
        """
        INSERT INTO stock_ledger (
            item_code, warehouse_id, actual_qty, reserved_qty,
            available_qty, stock_value, last_updated
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        ledger_rows,
    )
    conn.commit()


def seed_all():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")

    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        conn.executescript(f.read())

    cur = conn.cursor()

    # 1. Employees
    cur.executemany(
        "INSERT INTO employee VALUES (:employee_id, :employee_name, :srn, :designation, :department, :email, :status)",
        TEAM_MEMBERS,
    )

    # 2. Payment Terms
    payment_terms = [
        ("PT-ADV", "100% Advance", 0, "Full payment prior to warehouse dispatch"),
        ("PT-NET15", "Net 15 Days", 15, "Due 15 days from Tax Invoice date"),
        ("PT-NET30", "Net 30 Days", 30, "Standard B2B industrial 30-day credit"),
        ("PT-NET45", "Net 45 Days", 45, "Utility and Tier-1 EPC contractor terms"),
    ]
    cur.executemany("INSERT INTO payment_term VALUES (?, ?, ?, ?)", payment_terms)

    # 3. Customers (8 B2B Accounts across India)
    customers = [
        ("CUS-2026-0001", "Apex Industrial Drives Pvt Ltd", "Industrial Manufacturing", "Karnataka", "29AABCA4812K1Z5", 2500000, "PT-NET30", "HR-EMP-0001"),
        ("CUS-2026-0002", "Deccan Solar Grid Corp", "Utility & Solar EPC", "Telangana", "36AABCD9012M1Z2", 3500000, "PT-NET45", "HR-EMP-0001"),
        ("CUS-2026-0003", "Kaveri Precision Robotics", "Industrial Manufacturing", "Tamil Nadu", "33AABCK3319P1Z8", 1800000, "PT-NET30", "HR-EMP-0001"),
        ("CUS-2026-0004", "Sahyadri Green Microgrids", "Utility & Solar EPC", "Maharashtra", "27AABCS7741L1Z1", 2800000, "PT-NET45", "HR-EMP-0001"),
        ("CUS-2026-0005", "Nandi Metro Rail Contracting", "Infrastructure", "Karnataka", "29AABCN1122R1Z9", 4000000, "PT-NET30", "HR-EMP-0004"),
        ("CUS-2026-0006", "Bharat ColdChain Logistics", "Commercial Cold Storage", "Gujarat", "24AABCB6620E1Z4", 2000000, "PT-NET15", "HR-EMP-0001"),
        ("CUS-2026-0007", "Vindhya Telecom Towers Ltd", "Telecom Infrastructure", "Madhya Pradesh", "23AABCV8832F1Z7", 2200000, "PT-NET30", "HR-EMP-0004"),
        ("CUS-2026-0008", "Malabar Agro Processing Co", "Commercial Manufacturing", "Kerala", "32AABCM5518G1Z3", 1200000, "PT-ADV", "HR-EMP-0001"),
    ]
    cur.executemany("INSERT INTO customer VALUES (?, ?, ?, ?, ?, ?, ?, ?)", customers)

    # 4. Suppliers (6 Raw Material & Semiconductor Vendors)
    suppliers = [
        ("SUP-2026-0001", "SemiCore Components India", "Power Semiconductors", "India", "29AABCS1001A1Z1", "PT-NET30", "HR-EMP-0002"),
        ("SUP-2026-0002", "Vayu Magnetics & Coils", "Inductive Components", "India", "27AABCV2002B1Z2", "PT-NET30", "HR-EMP-0002"),
        ("SUP-2026-0003", "CellVolt Energy Cells LLP", "Battery Cells", "India", "33AABCC3003C1Z3", "PT-NET15", "HR-EMP-0002"),
        ("SUP-2026-0004", "CircuitCraft EMS Pvt Ltd", "Control PCBs", "India", "29AABCC4004D1Z4", "PT-NET30", "HR-EMP-0003"),
        ("SUP-2026-0005", "AluCast Enclosures Ltd", "Sheet Metal & Chassis", "India", "24AABCA5005E1Z5", "PT-NET45", "HR-EMP-0002"),
        ("SUP-2026-0006", "SwitchGear Controls India", "Electrical Breakers", "India", "27AABCS6006F1Z6", "PT-NET30", "HR-EMP-0003"),
    ]
    cur.executemany("INSERT INTO supplier VALUES (?, ?, ?, ?, ?, ?, ?)", suppliers)

    # 5. Items (6 Finished Goods + 6 Raw Materials = 12 SKUs)
    items = [
        ("ITM-INV-5KW", "5kW Hybrid Solar Inverter", "Finished Goods", "Nos", 52000, 78000, 8),
        ("ITM-INV-10KW", "10kW Three-Phase Grid Inverter", "Finished Goods", "Nos", 88000, 128000, 5),
        ("ITM-BMS-48V", "48V 200A Smart LiFePO4 BMS", "Finished Goods", "Nos", 16500, 25500, 15),
        ("ITM-CNV-25KVA", "25kVA Industrial Power Converter", "Finished Goods", "Nos", 140000, 198000, 4),
        ("ITM-SPD-1000V", "1000V DC Surge Protection Box", "Finished Goods", "Nos", 6800, 11200, 20),
        ("ITM-PNL-LT400", "400A Three-Phase LT Switchgear Panel", "Finished Goods", "Nos", 92000, 138000, 3),
        ("ITM-RAW-MOSFET", "SiC MOSFET Power Module", "Raw Materials", "Nos", 4200, 0, 40),
        ("ITM-RAW-COIL", "Toroidal Copper Inductor Coil", "Raw Materials", "Nos", 3100, 0, 35),
        ("ITM-RAW-CHAS", "IP65 Anodized Aluminium Chassis", "Raw Materials", "Nos", 5500, 0, 25),
        ("ITM-RAW-CELL", "3.2V 280Ah Prismatic LiFePO4 Cell", "Raw Materials", "Nos", 3800, 0, 50),
        ("ITM-RAW-PCB", "4-Layer Immersion Gold Control PCB", "Raw Materials", "Nos", 2400, 0, 40),
        ("ITM-RAW-BREAKER", "400A MCCB Industrial Breaker Unit", "Raw Materials", "Nos", 14500, 0, 12),
    ]
    cur.executemany("INSERT INTO item VALUES (?, ?, ?, ?, ?, ?, ?)", items)

    # 6. Warehouses (4 Locations in Bengaluru)
    warehouses = [
        ("WH-PEENYA-RAW", "Peenya Raw Material Store", "Raw Material", "Bengaluru", "HR-EMP-0002"),
        ("WH-ELECTRONIC-WIP", "Bommasandra Assembly WIP", "Work In Progress", "Bengaluru", "HR-EMP-0003"),
        ("WH-WHITEFIELD-FG", "Whitefield Finished Goods Hub", "Finished Goods", "Bengaluru", "HR-EMP-0001"),
        ("WH-QA-QUARANTINE", "QC Hold & Inspection Store", "Inspection", "Bengaluru", "HR-EMP-0003"),
    ]
    cur.executemany("INSERT INTO warehouse VALUES (?, ?, ?, ?, ?)", warehouses)

    # 7. Sales Orders (12 O2C Transactions with full 5-doc chain IDs)
    # Chain: Quotation -> Sales Order -> Delivery Note -> Sales Invoice -> Payment Entry
    item_selling_rate = {row[0]: row[5] for row in items}
    item_val_rate = {row[0]: row[4] for row in items}

    sales_orders_data = [
        ("SAL-ORD-2026-0001", "CUS-2026-0001", "2026-05-06", "2026-05-14", "Payment Received", "Completed", "QTN-2026-0001", "MAT-DN-2026-0001", "ACC-SINV-2026-0001", "ACC-PAY-2026-0001", "HR-EMP-0001", [("ITM-INV-5KW", 6), ("ITM-BMS-48V", 8)]),
        ("SAL-ORD-2026-0002", "CUS-2026-0002", "2026-05-10", "2026-05-18", "Payment Received", "Completed", "QTN-2026-0002", "MAT-DN-2026-0002", "ACC-SINV-2026-0002", "ACC-PAY-2026-0002", "HR-EMP-0001", [("ITM-INV-10KW", 5), ("ITM-SPD-1000V", 10)]),
        ("SAL-ORD-2026-0003", "CUS-2026-0003", "2026-05-15", "2026-05-24", "Payment Received", "Completed", "QTN-2026-0003", "MAT-DN-2026-0003", "ACC-SINV-2026-0003", "ACC-PAY-2026-0003", "HR-EMP-0001", [("ITM-CNV-25KVA", 3), ("ITM-PNL-LT400", 2)]),
        ("SAL-ORD-2026-0004", "CUS-2026-0004", "2026-06-02", "2026-06-11", "Payment Received", "Completed", "QTN-2026-0004", "MAT-DN-2026-0004", "ACC-SINV-2026-0004", "ACC-PAY-2026-0004", "HR-EMP-0001", [("ITM-INV-5KW", 8), ("ITM-SPD-1000V", 12)]),
        ("SAL-ORD-2026-0005", "CUS-2026-0005", "2026-06-09", "2026-06-19", "Payment Received", "Completed", "QTN-2026-0005", "MAT-DN-2026-0005", "ACC-SINV-2026-0005", "ACC-PAY-2026-0005", "HR-EMP-0004", [("ITM-BMS-48V", 20)]),
        ("SAL-ORD-2026-0006", "CUS-2026-0006", "2026-06-16", "2026-06-26", "Payment Received", "Completed", "QTN-2026-0006", "MAT-DN-2026-0006", "ACC-SINV-2026-0006", "ACC-PAY-2026-0006", "HR-EMP-0001", [("ITM-INV-10KW", 4), ("ITM-PNL-LT400", 3)]),
        ("SAL-ORD-2026-0007", "CUS-2026-0007", "2026-07-04", "2026-07-14", "Sales Invoice", "To Bill", "QTN-2026-0007", "MAT-DN-2026-0007", "ACC-SINV-2026-0007", None, "HR-EMP-0004", [("ITM-CNV-25KVA", 4), ("ITM-SPD-1000V", 8)]),
        ("SAL-ORD-2026-0008", "CUS-2026-0008", "2026-07-12", "2026-07-22", "Sales Invoice", "To Bill", "QTN-2026-0008", "MAT-DN-2026-0008", "ACC-SINV-2026-0008", None, "HR-EMP-0001", [("ITM-INV-5KW", 4), ("ITM-BMS-48V", 10)]),
        ("SAL-ORD-2026-0009", "CUS-2026-0001", "2026-07-18", "2026-07-28", "Delivery Note", "To Bill", "QTN-2026-0009", "MAT-DN-2026-0009", None, None, "HR-EMP-0001", [("ITM-INV-10KW", 5)]),
        ("SAL-ORD-2026-0010", "CUS-2026-0002", "2026-07-24", "2026-08-03", "Sales Order", "To Deliver & Bill", "QTN-2026-0010", None, None, None, "HR-EMP-0001", [("ITM-INV-5KW", 7), ("ITM-SPD-1000V", 14)]),
        ("SAL-ORD-2026-0011", "CUS-2026-0004", "2026-07-29", "2026-08-08", "Sales Order", "To Deliver & Bill", "QTN-2026-0011", None, None, None, "HR-EMP-0001", [("ITM-BMS-48V", 6), ("ITM-PNL-LT400", 2)]),
        ("SAL-ORD-2026-0012", "CUS-2026-0006", "2026-08-02", "2026-08-12", "Quotation", "Open Quotation", "QTN-2026-0012", None, None, None, "HR-EMP-0001", [("ITM-CNV-25KVA", 2), ("ITM-INV-10KW", 3)]),
    ]

    for so_id, cust_id, o_dt, d_dt, stage, status, qtn_id, dn_id, sinv_id, pay_id, emp_id, lines in sales_orders_data:
        net_total = sum(qty * item_selling_rate[code] for code, qty in lines)
        gst_amt = round(net_total * 0.18, 2)
        grand_total = round(net_total + gst_amt, 2)
        cur.execute(
            """
            INSERT INTO sales_order (
                so_id, customer_id, order_date, delivery_date, workflow_stage, status,
                quotation_id, delivery_note_id, sales_invoice_id, payment_entry_id,
                net_total, gst_amount, total_amount, owner_emp_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (so_id, cust_id, o_dt, d_dt, stage, status, qtn_id, dn_id, sinv_id, pay_id, net_total, gst_amt, grand_total, emp_id),
        )
        for code, qty in lines:
            rate = item_selling_rate[code]
            cur.execute(
                "INSERT INTO sales_order_item (so_id, item_code, qty, rate, amount) VALUES (?, ?, ?, ?, ?)",
                (so_id, code, qty, rate, qty * rate),
            )

    # 8. Purchase Orders (12 P2P Transactions — Raw Materials ONLY)
    # Chain: Material Request -> Purchase Order -> Purchase Receipt -> Purchase Invoice -> Payment Entry
    purchase_orders_data = [
        ("PUR-ORD-2026-0001", "SUP-2026-0001", "2026-05-01", "2026-05-03", "Payment Settled", "Completed", "MAT-MR-2026-0001", "MAT-PR-2026-0001", "ACC-PINV-2026-0001", "ACC-PAY-2026-0101", "HR-EMP-0002", [("ITM-RAW-MOSFET", 140), ("ITM-RAW-PCB", 90)]),
        ("PUR-ORD-2026-0002", "SUP-2026-0002", "2026-05-02", "2026-05-04", "Payment Settled", "Completed", "MAT-MR-2026-0002", "MAT-PR-2026-0002", "ACC-PINV-2026-0002", "ACC-PAY-2026-0102", "HR-EMP-0002", [("ITM-RAW-COIL", 110), ("ITM-RAW-CHAS", 80)]),
        ("PUR-ORD-2026-0003", "SUP-2026-0003", "2026-05-03", "2026-05-05", "Payment Settled", "Completed", "MAT-MR-2026-0003", "MAT-PR-2026-0003", "ACC-PINV-2026-0003", "ACC-PAY-2026-0103", "HR-EMP-0002", [("ITM-RAW-CELL", 160), ("ITM-RAW-BREAKER", 24)]),
        ("PUR-ORD-2026-0004", "SUP-2026-0004", "2026-05-18", "2026-05-24", "Payment Settled", "Completed", "MAT-MR-2026-0004", "MAT-PR-2026-0004", "ACC-PINV-2026-0004", "ACC-PAY-2026-0104", "HR-EMP-0002", [("ITM-RAW-COIL", 60), ("ITM-RAW-MOSFET", 80)]),
        ("PUR-ORD-2026-0005", "SUP-2026-0005", "2026-06-04", "2026-06-10", "Payment Settled", "Completed", "MAT-MR-2026-0005", "MAT-PR-2026-0005", "ACC-PINV-2026-0005", "ACC-PAY-2026-0105", "HR-EMP-0002", [("ITM-RAW-CHAS", 50), ("ITM-RAW-PCB", 70)]),
        ("PUR-ORD-2026-0006", "SUP-2026-0006", "2026-06-12", "2026-06-18", "Payment Settled", "Completed", "MAT-MR-2026-0006", "MAT-PR-2026-0006", "ACC-PINV-2026-0006", "ACC-PAY-2026-0106", "HR-EMP-0003", [("ITM-RAW-BREAKER", 18), ("ITM-RAW-CELL", 80)]),
        ("PUR-ORD-2026-0007", "SUP-2026-0001", "2026-06-22", "2026-06-29", "Purchase Invoice", "To Pay", "MAT-MR-2026-0007", "MAT-PR-2026-0007", "ACC-PINV-2026-0007", None, "HR-EMP-0002", [("ITM-RAW-MOSFET", 60), ("ITM-RAW-PCB", 50)]),
        ("PUR-ORD-2026-0008", "SUP-2026-0002", "2026-07-05", "2026-07-11", "Purchase Invoice", "To Pay", "MAT-MR-2026-0008", "MAT-PR-2026-0008", "ACC-PINV-2026-0008", None, "HR-EMP-0002", [("ITM-RAW-COIL", 50), ("ITM-RAW-CHAS", 40)]),
        ("PUR-ORD-2026-0009", "SUP-2026-0004", "2026-07-14", "2026-07-20", "Purchase Receipt", "To Bill", "MAT-MR-2026-0009", "MAT-PR-2026-0009", None, None, "HR-EMP-0003", [("ITM-RAW-PCB", 60), ("ITM-RAW-BREAKER", 10)]),
        ("PUR-ORD-2026-0010", "SUP-2026-0005", "2026-07-21", "2026-07-28", "Purchase Receipt", "To Bill", "MAT-MR-2026-0010", "MAT-PR-2026-0010", None, None, "HR-EMP-0002", [("ITM-RAW-CELL", 100)]),
        ("PUR-ORD-2026-0011", "SUP-2026-0003", "2026-07-27", "2026-08-04", "Purchase Order", "To Receive & Bill", "MAT-MR-2026-0011", None, None, None, "HR-EMP-0002", [("ITM-RAW-COIL", 45), ("ITM-RAW-MOSFET", 50)]),
        ("PUR-ORD-2026-0012", "SUP-2026-0006", "2026-08-01", "2026-08-10", "Material Request", "Draft", "MAT-MR-2026-0012", None, None, None, "HR-EMP-0003", [("ITM-RAW-CHAS", 30), ("ITM-RAW-BREAKER", 12)]),
    ]

    for po_id, sup_id, o_dt, s_dt, stage, status, mr_id, pr_id, pinv_id, pay_id, emp_id, lines in purchase_orders_data:
        for code, _ in lines:
            if not code.startswith("ITM-RAW-"):
                raise ValueError(f"Business rule violation: PO {po_id} attempted to buy non-raw-material {code}")
        net_total = sum(qty * item_val_rate[code] for code, qty in lines)
        gst_amt = round(net_total * 0.18, 2)
        grand_total = round(net_total + gst_amt, 2)
        cur.execute(
            """
            INSERT INTO purchase_order (
                po_id, supplier_id, order_date, schedule_date, workflow_stage, status,
                material_request_id, purchase_receipt_id, purchase_invoice_id, payment_entry_id,
                net_total, gst_amount, total_amount, buyer_emp_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (po_id, sup_id, o_dt, s_dt, stage, status, mr_id, pr_id, pinv_id, pay_id, net_total, gst_amt, grand_total, emp_id),
        )
        for code, qty in lines:
            rate = item_val_rate[code]
            cur.execute(
                "INSERT INTO purchase_order_item (po_id, item_code, qty, rate, amount) VALUES (?, ?, ?, ?, ?)",
                (po_id, code, qty, rate, qty * rate),
            )

    # 9. Manufacturing & Raw Material Issue Stock Entries (24 entries: 2 production batches)
    # Batch 1 (2026-05-05): Consume initial RM receipts, produce FG for May/June O2C orders
    # Batch 2 (2026-06-20): Consume May/June RM receipts, replenish FG for June/July O2C orders
    stock_entries = [
        # Batch 1 Raw Material Issues (WH-PEENYA-RAW)
        ("STE-2026-0001", "2026-05-05", "Material Issue for Manufacture", "ITM-RAW-MOSFET", "WH-PEENYA-RAW", -90, item_val_rate["ITM-RAW-MOSFET"], "Batch-1 BOM issue for Inverter & Converter lines", "HR-EMP-0003"),
        ("STE-2026-0002", "2026-05-05", "Material Issue for Manufacture", "ITM-RAW-PCB", "WH-PEENYA-RAW", -60, item_val_rate["ITM-RAW-PCB"], "Batch-1 BOM issue for BMS & Inverter control boards", "HR-EMP-0003"),
        ("STE-2026-0003", "2026-05-05", "Material Issue for Manufacture", "ITM-RAW-COIL", "WH-PEENYA-RAW", -75, item_val_rate["ITM-RAW-COIL"], "Batch-1 BOM issue for choke & transformer assembly", "HR-EMP-0003"),
        ("STE-2026-0004", "2026-05-05", "Material Issue for Manufacture", "ITM-RAW-CHAS", "WH-PEENYA-RAW", -55, item_val_rate["ITM-RAW-CHAS"], "Batch-1 BOM issue for IP65 enclosures & SPD boxes", "HR-EMP-0003"),
        ("STE-2026-0005", "2026-05-05", "Material Issue for Manufacture", "ITM-RAW-CELL", "WH-PEENYA-RAW", -100, item_val_rate["ITM-RAW-CELL"], "Batch-1 BOM issue for BMS test & pack validation", "HR-EMP-0003"),
        ("STE-2026-0006", "2026-05-05", "Material Issue for Manufacture", "ITM-RAW-BREAKER", "WH-PEENYA-RAW", -14, item_val_rate["ITM-RAW-BREAKER"], "Batch-1 BOM issue for LT panels & converters", "HR-EMP-0003"),
        # Batch 1 Finished Goods Production Receipts (WH-WHITEFIELD-FG)
        ("STE-2026-0007", "2026-05-05", "Manufacture", "ITM-INV-5KW", "WH-WHITEFIELD-FG", 24, item_val_rate["ITM-INV-5KW"], "WO-2026-0001 Batch-1 5kW Inverter assembly complete", "HR-EMP-0003"),
        ("STE-2026-0008", "2026-05-05", "Manufacture", "ITM-INV-10KW", "WH-WHITEFIELD-FG", 15, item_val_rate["ITM-INV-10KW"], "WO-2026-0002 Batch-1 10kW Inverter assembly complete", "HR-EMP-0003"),
        ("STE-2026-0009", "2026-05-05", "Manufacture", "ITM-BMS-48V", "WH-WHITEFIELD-FG", 50, item_val_rate["ITM-BMS-48V"], "WO-2026-0003 Batch-1 Smart BMS SMT & burn-in complete", "HR-EMP-0003"),
        ("STE-2026-0010", "2026-05-05", "Manufacture", "ITM-CNV-25KVA", "WH-WHITEFIELD-FG", 8, item_val_rate["ITM-CNV-25KVA"], "WO-2026-0004 Batch-1 25kVA Converter QC passed", "HR-EMP-0003"),
        ("STE-2026-0011", "2026-05-05", "Manufacture", "ITM-SPD-1000V", "WH-WHITEFIELD-FG", 55, item_val_rate["ITM-SPD-1000V"], "WO-2026-0005 Batch-1 DC Surge Box batch complete", "HR-EMP-0003"),
        ("STE-2026-0012", "2026-05-05", "Manufacture", "ITM-PNL-LT400", "WH-WHITEFIELD-FG", 6, item_val_rate["ITM-PNL-LT400"], "WO-2026-0006 Batch-1 LT Switchgear tested", "HR-EMP-0003"),
        # Batch 2 Raw Material Issues (WH-PEENYA-RAW)
        ("STE-2026-0013", "2026-06-20", "Material Issue for Manufacture", "ITM-RAW-MOSFET", "WH-PEENYA-RAW", -70, item_val_rate["ITM-RAW-MOSFET"], "Batch-2 BOM issue for Q2 replenishment", "HR-EMP-0003"),
        ("STE-2026-0014", "2026-06-20", "Material Issue for Manufacture", "ITM-RAW-PCB", "WH-PEENYA-RAW", -60, item_val_rate["ITM-RAW-PCB"], "Batch-2 BOM issue for control logic boards", "HR-EMP-0003"),
        ("STE-2026-0015", "2026-06-20", "Material Issue for Manufacture", "ITM-RAW-COIL", "WH-PEENYA-RAW", -50, item_val_rate["ITM-RAW-COIL"], "Batch-2 BOM issue for magnetic cores", "HR-EMP-0003"),
        ("STE-2026-0016", "2026-06-20", "Material Issue for Manufacture", "ITM-RAW-CHAS", "WH-PEENYA-RAW", -40, item_val_rate["ITM-RAW-CHAS"], "Batch-2 BOM issue for housings", "HR-EMP-0003"),
        ("STE-2026-0017", "2026-06-20", "Material Issue for Manufacture", "ITM-RAW-CELL", "WH-PEENYA-RAW", -80, item_val_rate["ITM-RAW-CELL"], "Batch-2 BOM issue for BMS harness assembly", "HR-EMP-0003"),
        ("STE-2026-0018", "2026-06-20", "Material Issue for Manufacture", "ITM-RAW-BREAKER", "WH-PEENYA-RAW", -12, item_val_rate["ITM-RAW-BREAKER"], "Batch-2 BOM issue for switchgear replenishment", "HR-EMP-0003"),
        # Batch 2 Finished Goods Production Receipts (WH-WHITEFIELD-FG)
        ("STE-2026-0019", "2026-06-20", "Manufacture", "ITM-INV-5KW", "WH-WHITEFIELD-FG", 12, item_val_rate["ITM-INV-5KW"], "WO-2026-0007 Batch-2 5kW Inverter replenishment", "HR-EMP-0003"),
        ("STE-2026-0020", "2026-06-20", "Manufacture", "ITM-INV-10KW", "WH-WHITEFIELD-FG", 10, item_val_rate["ITM-INV-10KW"], "WO-2026-0008 Batch-2 10kW Inverter replenishment", "HR-EMP-0003"),
        ("STE-2026-0021", "2026-06-20", "Manufacture", "ITM-BMS-48V", "WH-WHITEFIELD-FG", 30, item_val_rate["ITM-BMS-48V"], "WO-2026-0009 Batch-2 Smart BMS replenishment", "HR-EMP-0003"),
        ("STE-2026-0022", "2026-06-20", "Manufacture", "ITM-CNV-25KVA", "WH-WHITEFIELD-FG", 5, item_val_rate["ITM-CNV-25KVA"], "WO-2026-0010 Batch-2 25kVA Converter replenishment", "HR-EMP-0003"),
        ("STE-2026-0023", "2026-06-20", "Manufacture", "ITM-SPD-1000V", "WH-WHITEFIELD-FG", 30, item_val_rate["ITM-SPD-1000V"], "WO-2026-0011 Batch-2 DC Surge Box replenishment", "HR-EMP-0003"),
        ("STE-2026-0024", "2026-06-20", "Manufacture", "ITM-PNL-LT400", "WH-WHITEFIELD-FG", 5, item_val_rate["ITM-PNL-LT400"], "WO-2026-0012 Batch-2 LT Switchgear replenishment", "HR-EMP-0003"),
    ]
    cur.executemany(
        "INSERT INTO stock_entry VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        stock_entries,
    )

    conn.commit()
    recalculate_stock_ledger(conn)
    conn.close()
    print(f"[VoltEdge EBS] Seeded database with calculated Stock Ledger at: {DB_PATH}")


def init_database():
    """Compatibility helper to seed DB if missing."""
    if not os.path.exists(DB_PATH):
        seed_all()


if __name__ == "__main__":
    seed_all()
