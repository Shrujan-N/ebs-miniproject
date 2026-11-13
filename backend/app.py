"""
VoltEdge ERP Backend & NEXORA Brochure Server (Zero-Dependency Python + SQLite)
Course: UE24CS343AB8 Enterprise Business Systems
Owner: Srujan (Database, Backend & Dashboard)

Uses Python's built-in http.server + sqlite3 + json so it runs on any Windows
Python installation without needing pip or external packages.
"""

import json
import os
import sqlite3
from http.server import BaseHTTPRequestHandler, HTTPServer
from seed_data import DB_PATH, init_database
from erpnext_sync import export_tables_to_csv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR)
TEMPLATE_DIR = os.path.join(PROJECT_DIR, "templates")


def get_db():
    if not os.path.exists(DB_PATH):
        init_database()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def fetch_dashboard_payload():
    """Executes all SQL queries for KPIs, Charts, 3 Reports, 6 Master Tables & 24 Transactions."""
    conn = get_db()
    cur = conn.cursor()

    # 1. KPI Queries
    cur.execute("SELECT COALESCE(SUM(total_amount), 0) AS total_sales, COUNT(*) AS so_count FROM sales_order")
    so_summary = dict(cur.fetchone())

    cur.execute("SELECT COUNT(*) AS completed_so FROM sales_order WHERE status = 'Completed'")
    completed_so = cur.fetchone()["completed_so"]

    cur.execute("SELECT COALESCE(SUM(total_amount), 0) AS total_purchases, COUNT(*) AS po_count FROM purchase_order")
    po_summary = dict(cur.fetchone())

    cur.execute("SELECT COALESCE(SUM(stock_value), 0) AS inventory_val, COALESCE(SUM(available_qty), 0) AS total_units FROM stock_ledger")
    inv_summary = dict(cur.fetchone())

    fulfillment_pct = round((completed_so / so_summary["so_count"]) * 100, 1) if so_summary["so_count"] else 0.0

    kpis = {
        "sales_lakhs": round(so_summary["total_sales"] / 100000.0, 2),
        "sales_raw": so_summary["total_sales"],
        "so_count": so_summary["so_count"],
        "completed_so": completed_so,
        "purchase_lakhs": round(po_summary["total_purchases"] / 100000.0, 2),
        "purchase_raw": po_summary["total_purchases"],
        "po_count": po_summary["po_count"],
        "fulfillment_pct": fulfillment_pct,
        "inventory_lakhs": round(inv_summary["inventory_val"] / 100000.0, 2),
        "inventory_units": inv_summary["total_units"],
    }

    # 2. Chart 1 & Report 1: Monthly Sales Analysis
    cur.execute(
        """
        SELECT
             strftime('%Y-%m', order_date) AS month_key,
             CASE strftime('%m', order_date)
                 WHEN '05' THEN 'May 2026'
                 WHEN '06' THEN 'Jun 2026'
                 WHEN '07' THEN 'Jul 2026'
                 WHEN '08' THEN 'Aug 2026'
                 WHEN '09' THEN 'Sep 2026'
                 WHEN '10' THEN 'Oct 2026'
                 WHEN '11' THEN 'Nov 2026'
                 ELSE strftime('%Y-%m', order_date)
             END AS month_label,
             COUNT(so_id) AS order_count,
             SUM(total_amount) AS monthly_revenue,
             ROUND(SUM(total_amount) / 100000.0, 2) AS revenue_lakhs
        FROM sales_order
        GROUP BY month_key
        ORDER BY month_key ASC
        """
    )
    monthly_sales = [dict(r) for r in cur.fetchall()]

    # 3. Chart 2 & Report 2: Purchase Distribution by Supplier
    cur.execute(
        """
        SELECT
            s.supplier_id,
            s.supplier_name,
            s.supplier_group,
            s.city,
            COUNT(p.po_id) AS po_count,
            SUM(p.total_amount) AS total_spend,
            ROUND(SUM(p.total_amount) / 100000.0, 2) AS spend_lakhs,
            s.srn_tag
        FROM purchase_order p
        JOIN supplier s ON p.supplier_id = s.supplier_id
        GROUP BY s.supplier_id
        ORDER BY total_spend DESC
        """
    )
    supplier_spend = [dict(r) for r in cur.fetchall()]

    # 4. Report 3: Inventory Stock & Valuation Analysis
    cur.execute(
        """
        SELECT
            sl.entry_id,
            i.item_code,
            i.item_name,
            i.item_group,
            w.warehouse_name,
            w.warehouse_type,
            sl.available_qty,
            i.safety_stock,
            sl.valuation_rate,
            sl.stock_value,
            ROUND(sl.stock_value / 100000.0, 2) AS value_lakhs,
            i.created_by_srn
        FROM stock_ledger sl
        JOIN item i ON sl.item_code = i.item_code
        JOIN warehouse w ON sl.warehouse_id = w.warehouse_id
        ORDER BY sl.stock_value DESC
        """
    )
    inventory_report = [dict(r) for r in cur.fetchall()]

    # 5. Master Data Entities (All 6 tables)
    cur.execute("SELECT * FROM employee ORDER BY employee_id")
    employees = [dict(r) for r in cur.fetchall()]

    cur.execute("SELECT * FROM customer ORDER BY customer_id")
    customers = [dict(r) for r in cur.fetchall()]

    cur.execute("SELECT * FROM supplier ORDER BY supplier_id")
    suppliers = [dict(r) for r in cur.fetchall()]

    cur.execute("SELECT * FROM item ORDER BY item_code")
    items = [dict(r) for r in cur.fetchall()]

    cur.execute(
        """
        SELECT w.*, e.employee_name AS incharge_name
        FROM warehouse w
        JOIN employee e ON w.incharge_id = e.employee_id
        ORDER BY w.warehouse_id
        """
    )
    warehouses = [dict(r) for r in cur.fetchall()]

    cur.execute("SELECT * FROM payment_term ORDER BY term_id")
    payment_terms = [dict(r) for r in cur.fetchall()]

    # 6. Transaction Tables (12 Sales Orders & 12 Purchase Orders)
    cur.execute(
        """
        SELECT
            so.*,
            c.customer_name,
            e.employee_name,
            pt.term_name
        FROM sales_order so
        JOIN customer c ON so.customer_id = c.customer_id
        JOIN employee e ON so.employee_id = e.employee_id
        JOIN payment_term pt ON so.term_id = pt.term_id
        ORDER BY so.so_id ASC
        """
    )
    sales_orders = [dict(r) for r in cur.fetchall()]

    cur.execute(
        """
        SELECT
            po.*,
            s.supplier_name,
            e.employee_name,
            pt.term_name
        FROM purchase_order po
        JOIN supplier s ON po.supplier_id = s.supplier_id
        JOIN employee e ON po.employee_id = e.employee_id
        JOIN payment_term pt ON po.term_id = pt.term_id
        ORDER BY po.po_id ASC
        """
    )
    purchase_orders = [dict(r) for r in cur.fetchall()]

    conn.close()

    return {
        "kpis": kpis,
        "monthly_sales": monthly_sales,
        "supplier_spend": supplier_spend,
        "inventory_report": inventory_report,
        "employees": employees,
        "customers": customers,
        "suppliers": suppliers,
        "items": items,
        "warehouses": warehouses,
        "payment_terms": payment_terms,
        "sales_orders": sales_orders,
        "purchase_orders": purchase_orders,
    }


def render_dashboard_html():
    """Injects the live SQLite JSON payload into templates/dashboard.html."""
    template_path = os.path.join(TEMPLATE_DIR, "dashboard.html")
    with open(template_path, "r", encoding="utf-8") as f:
        html = f.read()
    payload_json = json.dumps(fetch_dashboard_payload(), indent=2)
    return html.replace("/*__INITIAL_SQL_DATA__*/", f"window.__EBS_DATA__ = {payload_json};")


def build_standalone_snapshots():
    """Writes standalone HTML snapshots so the user can also open files directly."""
    dash_html = render_dashboard_html()
    standalone_dash = os.path.join(PROJECT_DIR, "voltedge_dashboard_standalone.html")
    with open(standalone_dash, "w", encoding="utf-8") as f:
        f.write(dash_html)

    nexora_src = os.path.join(TEMPLATE_DIR, "nexora.html")
    nexora_dst = os.path.join(PROJECT_DIR, "nexora_brochure_standalone.html")
    with open(nexora_src, "r", encoding="utf-8") as f:
        nex_html = f.read()
    with open(nexora_dst, "w", encoding="utf-8") as f:
        f.write(nex_html)


class EBSRequestHandler(BaseHTTPRequestHandler):
    def _send_html(self, content, status=200):
        encoded = content.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def _send_json(self, data, status=200):
        encoded = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def do_GET(self):
        path = self.path.split("?")[0]
        if path in ("/", "/dashboard"):
            self._send_html(render_dashboard_html())
        elif path == "/nexora":
            nexora_path = os.path.join(TEMPLATE_DIR, "nexora.html")
            with open(nexora_path, "r", encoding="utf-8") as f:
                self._send_html(f.read())
        elif path == "/api/data":
            self._send_json(fetch_dashboard_payload())
        else:
            self._send_html("<h3>404 Not Found</h3><p><a href='/dashboard'>Go to Dashboard</a></p>", 404)

    def do_POST(self):
        path = self.path.split("?")[0]
        length = int(self.headers.get("Content-Length", 0))
        raw_body = self.rfile.read(length).decode("utf-8") if length > 0 else "{}"
        data = json.loads(raw_body or "{}")

        if path == "/api/update_record":
            record_type = data.get("type")
            record_id = data.get("id")
            new_stage = data.get("workflow_stage")
            new_status = data.get("status")
            new_amount = float(data.get("total_amount", 0))

            conn = get_db()
            cur = conn.cursor()
            if record_type == "SO":
                cur.execute(
                    "UPDATE sales_order SET workflow_stage = ?, status = ?, total_amount = ? WHERE so_id = ?",
                    (new_stage, new_status, new_amount, record_id),
                )
            elif record_type == "PO":
                cur.execute(
                    "UPDATE purchase_order SET workflow_stage = ?, status = ?, total_amount = ? WHERE po_id = ?",
                    (new_stage, new_status, new_amount, record_id),
                )
            conn.commit()
            conn.close()
            build_standalone_snapshots()
            self._send_json({"ok": True, "id": record_id})

        elif path == "/api/reset_db":
            init_database()
            export_tables_to_csv()
            build_standalone_snapshots()
            self._send_json({"ok": True})
        else:
            self._send_json({"error": "Not found"}, 404)

    def log_message(self, fmt, *args):
        print(f"[EBS-SERVER] {self.address_string()} - {fmt % args}")


if __name__ == "__main__":
    init_database()
    export_tables_to_csv()
    build_standalone_snapshots()
    port = 5000
    server = HTTPServer(("127.0.0.1", port), EBSRequestHandler)
    print("=========================================================================")
    print(" VoltEdge ERP & NEXORA Server Running (Python + SQLite)")
    print(f" -> Part A (VoltEdge Dashboard & Reports): http://127.0.0.1:{port}/dashboard")
    print(f" -> Part B (NEXORA Website & Brochure):    http://127.0.0.1:{port}/nexora")
    print("=========================================================================")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server.")
        server.server_close()
