"""
ERPNext v16 Synchronization & CSV Export Utility (VoltEdge Power Systems)
==========================================================================
1. Exports all 13 local SQLite tables into ERPNext Data Import CSV templates
   (`backend/erpnext_csv_exports/tab_*.csv`) matching Frappe/ERPNext v16 columns.
2. Provides `push_to_erpnext_api(base_url, api_key, api_secret)` using Python's
   built-in `urllib.request` to seed records directly into a live ERPNext v16
   Docker instance (`http://localhost:8080`) without external pip packages.
"""

import argparse
import csv
import json
import os
import sqlite3
import urllib.error
import urllib.request

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "voltedge_ebs.db")
EXPORT_DIR = os.path.join(BASE_DIR, "backend", "erpnext_csv_exports")

TABLES = [
    ("employee", "tab_Employee.csv"),
    ("payment_term", "tab_Payment_Term.csv"),
    ("customer", "tab_Customer.csv"),
    ("supplier", "tab_Supplier.csv"),
    ("item", "tab_Item.csv"),
    ("warehouse", "tab_Warehouse.csv"),
    ("sales_order", "tab_Sales_Order.csv"),
    ("sales_order_item", "tab_Sales_Order_Item.csv"),
    ("purchase_order", "tab_Purchase_Order.csv"),
    ("purchase_order_item", "tab_Purchase_Order_Item.csv"),
    ("stock_entry", "tab_Stock_Entry.csv"),
    ("stock_ledger_entry", "tab_Stock_Ledger_Entry.csv"),
    ("stock_ledger", "tab_Bin.csv"),
]


def export_tables_to_csv() -> list:
    os.makedirs(EXPORT_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    exported_files = []

    for table_name, csv_name in TABLES:
        rows = cur.execute(f"SELECT * FROM {table_name}").fetchall()
        headers = [desc[0] for desc in cur.description]
        out_path = os.path.join(EXPORT_DIR, csv_name)
        with open(out_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)
        exported_files.append((csv_name, len(rows)))

    conn.close()
    return exported_files


def _post_erpnext_resource(base_url: str, doctype: str, payload: dict, auth_header: str) -> dict:
    endpoint = f"{base_url.rstrip('/')}/api/resource/{urllib.request.quote(doctype)}"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        endpoint,
        data=data,
        method="POST",
        headers={
            "Authorization": auth_header,
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))


def push_to_erpnext_api(
    base_url: str = "http://localhost:8080",
    api_key: str = "",
    api_secret: str = "",
    company: str = "VoltEdge Power Systems Pvt. Ltd.",
) -> dict:
    """Push Customer, Supplier, Item, Sales Order & Purchase Order records to live ERPNext v16 REST API."""
    if not api_key or not api_secret:
        return {
            "ok": False,
            "message": "Provide --api-key and --api-secret (or ERPNEXT_API_KEY / ERPNEXT_API_SECRET env vars).",
        }

    auth_header = f"token {api_key}:{api_secret}"
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    pushed = {"Item": 0, "Customer": 0, "Supplier": 0, "Sales Order": 0, "Purchase Order": 0}
    errors = []

    try:
        for it in cur.execute("SELECT * FROM item").fetchall():
            try:
                _post_erpnext_resource(
                    base_url,
                    "Item",
                    {
                        "item_code": it["item_code"],
                        "item_name": it["item_name"],
                        "item_group": it["item_group"],
                        "stock_uom": it["uom"],
                        "valuation_rate": it["valuation_rate"],
                        "standard_rate": it["selling_rate"],
                        "is_stock_item": 1,
                    },
                    auth_header,
                )
                pushed["Item"] += 1
            except urllib.error.HTTPError as e:
                if e.code != 409:
                    errors.append(f"Item {it['item_code']}: HTTP {e.code}")

        for c in cur.execute("SELECT * FROM customer").fetchall():
            try:
                _post_erpnext_resource(
                    base_url,
                    "Customer",
                    {
                        "customer_name": c["customer_name"],
                        "customer_group": "Commercial",
                        "territory": "India",
                        "tax_id": c["gstin"],
                    },
                    auth_header,
                )
                pushed["Customer"] += 1
            except urllib.error.HTTPError as e:
                if e.code != 409:
                    errors.append(f"Customer {c['customer_id']}: HTTP {e.code}")

        for s in cur.execute("SELECT * FROM supplier").fetchall():
            try:
                _post_erpnext_resource(
                    base_url,
                    "Supplier",
                    {
                        "supplier_name": s["supplier_name"],
                        "supplier_group": "Raw Material",
                        "country": s["country"],
                        "tax_id": s["gstin"],
                    },
                    auth_header,
                )
                pushed["Supplier"] += 1
            except urllib.error.HTTPError as e:
                if e.code != 409:
                    errors.append(f"Supplier {s['supplier_id']}: HTTP {e.code}")

        for so in cur.execute(
            "SELECT so.*, c.customer_name FROM sales_order so JOIN customer c ON so.customer_id = c.customer_id"
        ).fetchall():
            items = cur.execute(
                "SELECT item_code, qty, rate FROM sales_order_item WHERE so_id = ?", (so["so_id"],)
            ).fetchall()
            try:
                _post_erpnext_resource(
                    base_url,
                    "Sales Order",
                    {
                        "customer": so["customer_name"],
                        "company": company,
                        "transaction_date": so["order_date"],
                        "delivery_date": so["delivery_date"],
                        "items": [{"item_code": x["item_code"], "qty": x["qty"], "rate": x["rate"]} for x in items],
                    },
                    auth_header,
                )
                pushed["Sales Order"] += 1
            except urllib.error.HTTPError as e:
                if e.code != 409:
                    errors.append(f"SO {so['so_id']}: HTTP {e.code}")

        for po in cur.execute(
            "SELECT po.*, s.supplier_name FROM purchase_order po JOIN supplier s ON po.supplier_id = s.supplier_id"
        ).fetchall():
            items = cur.execute(
                "SELECT item_code, qty, rate FROM purchase_order_item WHERE po_id = ?", (po["po_id"],)
            ).fetchall()
            try:
                _post_erpnext_resource(
                    base_url,
                    "Purchase Order",
                    {
                        "supplier": po["supplier_name"],
                        "company": company,
                        "transaction_date": po["order_date"],
                        "schedule_date": po["schedule_date"],
                        "items": [{"item_code": x["item_code"], "qty": x["qty"], "rate": x["rate"]} for x in items],
                    },
                    auth_header,
                )
                pushed["Purchase Order"] += 1
            except urllib.error.HTTPError as e:
                if e.code != 409:
                    errors.append(f"PO {po['po_id']}: HTTP {e.code}")
    except urllib.error.URLError as e:
        return {"ok": False, "message": f"Cannot reach ERPNext server at {base_url}: {e.reason}", "pushed": pushed}
    finally:
        conn.close()

    return {"ok": len(errors) == 0, "pushed": pushed, "errors": errors}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="VoltEdge ERPNext v16 CSV Exporter & REST Sync")
    parser.add_argument("--push", action="store_true", help="Push master/transaction records to live ERPNext v16 API")
    parser.add_argument("--url", default=os.environ.get("ERPNEXT_URL", "http://localhost:8080"))
    parser.add_argument("--api-key", default=os.environ.get("ERPNEXT_API_KEY", ""))
    parser.add_argument("--api-secret", default=os.environ.get("ERPNEXT_API_SECRET", ""))
    args = parser.parse_args()

    res = export_tables_to_csv()
    print("[VoltEdge ERPNext v16 Sync] Exported 13 tables to CSV:")
    for fname, count in res:
        print(f"  - {fname}: {count} rows")

    if args.push:
        sync_out = push_to_erpnext_api(args.url, args.api_key, args.api_secret)
        print("[VoltEdge ERPNext v16 REST Push]", json.dumps(sync_out, indent=2))
