"""
ERPNext Data Export & REST API Sync Utility
Course: UE24CS343AB8 Enterprise Business Systems
Owner: Srujan (Database, Backend & Dashboard)

Generates ERPNext Data Import CSV files from voltedge_ebs.db so the exact
master and transaction records can be bulk-imported into any ERPNext v15 instance.
"""

import csv
import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "voltedge_ebs.db")
EXPORT_DIR = os.path.join(BASE_DIR, "erpnext_csv_exports")


def export_tables_to_csv():
    os.makedirs(EXPORT_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    tables = [
        "employee",
        "payment_term",
        "customer",
        "supplier",
        "item",
        "warehouse",
        "sales_order",
        "sales_order_item",
        "purchase_order",
        "purchase_order_item",
        "stock_ledger",
    ]

    for tbl in tables:
        cursor.execute(f"SELECT * FROM {tbl}")
        rows = cursor.fetchall()
        headers = [desc[0] for desc in cursor.description]

        csv_path = os.path.join(EXPORT_DIR, f"tab_{tbl}.csv")
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)

    conn.close()
    print(f"[OK] Exported {len(tables)} ERPNext-compatible CSV files to: {EXPORT_DIR}")


if __name__ == "__main__":
    export_tables_to_csv()
