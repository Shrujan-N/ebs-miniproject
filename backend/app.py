"""
VoltEdge Power Systems Pvt. Ltd. — Local ERPNext v16 Prototype & Web Server
==========================================================================
Zero external dependencies (uses Python built-in http.server + sqlite3).
Serves:
  - `/` & `/dashboard` : VoltEdge Power Systems ERPNext v16 Showcase (Part A)
  - `/nexora`          : NEXORA Industrial Automation Digital Sales Brochure (Part B)
  - `/api/data`        : Live SQLite JSON feed for KPIs, O2C/P2P chains & Stock Ledger
  - `/api/update_record` : Live workflow stage editor (triggers recalculate_stock_ledger)
  - `/api/create_order`  : Create new Sales Order (O2C) or Raw-Material Purchase Order (P2P)
  - `/api/reset_db`    : Reset DB back to clean seeded state
"""

import http.server
import json
import os
import socketserver
import sqlite3
import sys
from datetime import datetime
from urllib.parse import urlparse

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
DB_PATH = os.path.join(BASE_DIR, "voltedge_ebs.db")

if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from erpnext_sync import export_tables_to_csv  # noqa: E402
from seed_data import TEAM_MEMBERS, recalculate_stock_ledger, seed_all  # noqa: E402

SO_STAGE_MAP = {
    "Quotation": (True, False, False, False, "Open Quotation"),
    "Sales Order": (True, False, False, False, "To Deliver & Bill"),
    "Delivery Note": (True, True, False, False, "To Bill"),
    "Sales Invoice": (True, True, True, False, "To Bill"),
    "Payment Received": (True, True, True, True, "Completed"),
}

PO_STAGE_MAP = {
    "Material Request": (True, False, False, False, "Draft"),
    "Purchase Order": (True, False, False, False, "To Receive & Bill"),
    "Purchase Receipt": (True, True, False, False, "To Bill"),
    "Purchase Invoice": (True, True, True, False, "To Pay"),
    "Payment Settled": (True, True, True, True, "Completed"),
}


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_database():
    if not os.path.exists(DB_PATH):
        seed_all()
        export_tables_to_csv()


def _rows_to_dicts(rows):
    return [dict(r) for r in rows]


def fetch_dashboard_payload():
    init_database()
    conn = get_db_connection()
    cur = conn.cursor()

    employees = _rows_to_dicts(cur.execute("SELECT * FROM employee ORDER BY employee_id").fetchall())
    payment_terms = _rows_to_dicts(cur.execute("SELECT * FROM payment_term ORDER BY credit_days").fetchall())
    customers = _rows_to_dicts(
        cur.execute(
            """
            SELECT c.*, pt.term_name, e.employee_name AS manager_name
            FROM customer c
            LEFT JOIN payment_term pt ON c.default_payment_term = pt.payment_term_id
            LEFT JOIN employee e ON c.account_manager_id = e.employee_id
            ORDER BY c.customer_id
            """
        ).fetchall()
    )
    suppliers = _rows_to_dicts(
        cur.execute(
            """
            SELECT s.*, pt.term_name, e.employee_name AS buyer_name
            FROM supplier s
            LEFT JOIN payment_term pt ON s.default_payment_term = pt.payment_term_id
            LEFT JOIN employee e ON s.buyer_id = e.employee_id
            ORDER BY s.supplier_id
            """
        ).fetchall()
    )
    items = _rows_to_dicts(cur.execute("SELECT * FROM item ORDER BY item_group, item_code").fetchall())
    warehouses = _rows_to_dicts(
        cur.execute(
            """
            SELECT w.*, e.employee_name AS manager_name
            FROM warehouse w
            LEFT JOIN employee e ON w.manager_id = e.employee_id
            ORDER BY w.warehouse_id
            """
        ).fetchall()
    )

    so_item_map = {}
    for line in cur.execute(
        """
        SELECT soi.so_id, soi.item_code, i.item_name, soi.qty, soi.rate, soi.amount
        FROM sales_order_item soi
        JOIN item i ON soi.item_code = i.item_code
        ORDER BY soi.id
        """
    ).fetchall():
        d = dict(line)
        so_item_map.setdefault(d["so_id"], []).append(d)

    sales_orders = _rows_to_dicts(
        cur.execute(
            """
            SELECT so.*, c.customer_name, e.employee_name AS owner_name,
                   GROUP_CONCAT(i.item_name || ' (x' || soi.qty || ')', ', ') AS items_summary
            FROM sales_order so
            JOIN customer c ON so.customer_id = c.customer_id
            JOIN employee e ON so.owner_emp_id = e.employee_id
            LEFT JOIN sales_order_item soi ON so.so_id = soi.so_id
            LEFT JOIN item i ON soi.item_code = i.item_code
            GROUP BY so.so_id
            ORDER BY so.so_id
            """
        ).fetchall()
    )
    for so in sales_orders:
        so["line_items"] = so_item_map.get(so["so_id"], [])

    po_item_map = {}
    for line in cur.execute(
        """
        SELECT poi.po_id, poi.item_code, i.item_name, i.item_group, poi.qty, poi.rate, poi.amount
        FROM purchase_order_item poi
        JOIN item i ON poi.item_code = i.item_code
        ORDER BY poi.id
        """
    ).fetchall():
        d = dict(line)
        po_item_map.setdefault(d["po_id"], []).append(d)

    purchase_orders = _rows_to_dicts(
        cur.execute(
            """
            SELECT po.*, s.supplier_name, e.employee_name AS buyer_name,
                   GROUP_CONCAT(i.item_name || ' (x' || poi.qty || ')', ', ') AS items_summary
            FROM purchase_order po
            JOIN supplier s ON po.supplier_id = s.supplier_id
            JOIN employee e ON po.buyer_emp_id = e.employee_id
            LEFT JOIN purchase_order_item poi ON po.po_id = poi.po_id
            LEFT JOIN item i ON poi.item_code = i.item_code
            GROUP BY po.po_id
            ORDER BY po.po_id
            """
        ).fetchall()
    )
    for po in purchase_orders:
        po["line_items"] = po_item_map.get(po["po_id"], [])

    stock_entries = _rows_to_dicts(
        cur.execute(
            """
            SELECT se.*, i.item_name, w.warehouse_name, e.employee_name AS owner_name
            FROM stock_entry se
            JOIN item i ON se.item_code = i.item_code
            JOIN warehouse w ON se.warehouse_id = w.warehouse_id
            JOIN employee e ON se.owner_emp_id = e.employee_id
            ORDER BY se.posting_date DESC, se.stock_entry_id DESC
            """
        ).fetchall()
    )

    stock_ledger_entries = _rows_to_dicts(
        cur.execute(
            """
            SELECT sle.*, i.item_name, i.item_group, w.warehouse_name
            FROM stock_ledger_entry sle
            JOIN item i ON sle.item_code = i.item_code
            JOIN warehouse w ON sle.warehouse_id = w.warehouse_id
            ORDER BY sle.sle_id DESC
            """
        ).fetchall()
    )

    stock_ledger = _rows_to_dicts(
        cur.execute(
            """
            SELECT sl.*, i.item_name, i.item_group, i.valuation_rate, i.selling_rate, i.reorder_level,
                   w.warehouse_name, w.warehouse_type
            FROM stock_ledger sl
            JOIN item i ON sl.item_code = i.item_code
            JOIN warehouse w ON sl.warehouse_id = w.warehouse_id
            ORDER BY i.item_group, sl.stock_value DESC
            """
        ).fetchall()
    )

    # Monthly Sales Revenue Aggregation
    monthly_sales = _rows_to_dicts(
        cur.execute(
            """
            SELECT substr(order_date, 1, 7) AS month,
                   COUNT(*) AS order_count,
                   ROUND(SUM(total_amount)/100000.0, 2) AS revenue_lakhs
            FROM sales_order
            WHERE status != 'Open Quotation'
            GROUP BY substr(order_date, 1, 7)
            ORDER BY month
            """
        ).fetchall()
    )

    # Supplier Spend Aggregation
    supplier_spend = _rows_to_dicts(
        cur.execute(
            """
            SELECT s.supplier_name,
                   ROUND(SUM(po.total_amount)/100000.0, 2) AS spend_lakhs
            FROM purchase_order po
            JOIN supplier s ON po.supplier_id = s.supplier_id
            GROUP BY s.supplier_id
            ORDER BY spend_lakhs DESC
            """
        ).fetchall()
    )

    # KPI Rollups
    total_revenue = cur.execute("SELECT COALESCE(SUM(total_amount), 0) FROM sales_order WHERE status != 'Open Quotation'").fetchone()[0]
    total_procurement = cur.execute("SELECT COALESCE(SUM(total_amount), 0) FROM purchase_order").fetchone()[0]
    total_inv_value = cur.execute("SELECT COALESCE(SUM(stock_value), 0) FROM stock_ledger").fetchone()[0]
    collected_revenue = cur.execute("SELECT COALESCE(SUM(total_amount), 0) FROM sales_order WHERE workflow_stage = 'Payment Received'").fetchone()[0]
    pending_receivables = total_revenue - collected_revenue
    po_paid = cur.execute("SELECT COALESCE(SUM(total_amount), 0) FROM purchase_order WHERE workflow_stage = 'Payment Settled'").fetchone()[0]
    raw_only_violations = cur.execute(
        "SELECT COUNT(*) FROM purchase_order_item poi JOIN item i ON poi.item_code = i.item_code WHERE i.item_group != 'Raw Materials'"
    ).fetchone()[0]

    conn.close()

    return {
        "team": TEAM_MEMBERS,
        "employees": employees,
        "payment_terms": payment_terms,
        "customers": customers,
        "suppliers": suppliers,
        "items": items,
        "warehouses": warehouses,
        "sales_orders": sales_orders,
        "purchase_orders": purchase_orders,
        "stock_entries": stock_entries,
        "stock_ledger_entries": stock_ledger_entries,
        "stock_ledger": stock_ledger,
        "kpis": {
            "total_sales_revenue": total_revenue,
            "collected_revenue": collected_revenue,
            "pending_receivables": pending_receivables,
            "total_procurement_spend": total_procurement,
            "po_paid": po_paid,
            "total_inventory_value": total_inv_value,
            "active_so_count": len(sales_orders),
            "active_po_count": len(purchase_orders),
            "stock_entry_count": len(stock_entries),
            "sle_count": len(stock_ledger_entries),
            "po_raw_only_valid": raw_only_violations == 0,
            "customer_count": len(customers),
            "supplier_count": len(suppliers),
            "sku_count": len(items),
        },
        "monthly_sales": monthly_sales,
        "supplier_spend": supplier_spend,
        "db_path": DB_PATH,
    }


def render_dashboard_html():
    payload = fetch_dashboard_payload()
    tpl_path = os.path.join(TEMPLATE_DIR, "dashboard.html")
    with open(tpl_path, "r", encoding="utf-8") as f:
        html = f.read()
    injected_json = json.dumps(payload, ensure_ascii=False)
    return html.replace("__INITIAL_PAYLOAD__", injected_json)


def build_standalone_snapshots():
    """Exports self-contained HTML snapshots for instant browser viewing without starting Python."""
    dash_html = render_dashboard_html()
    for out_name in ("dashboard_standalone.html", "voltedge_dashboard_standalone.html"):
        with open(os.path.join(BASE_DIR, out_name), "w", encoding="utf-8") as f:
            f.write(dash_html)

    nexora_path = os.path.join(TEMPLATE_DIR, "nexora.html")
    with open(nexora_path, "r", encoding="utf-8") as f:
        nexora_html = f.read()

    for out_name in ("nexora_standalone.html", "nexora_brochure_standalone.html"):
        with open(os.path.join(BASE_DIR, out_name), "w", encoding="utf-8") as f:
            f.write(nexora_html)


def _suffix_num(record_id: str) -> str:
    return record_id.split("-")[-1]


class ERPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        print(f"[HTTP] {self.address_string()} - {format % args}")

    def _send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_html(self, html_str, status=200):
        body = html_str.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path in ("/", "/dashboard"):
            self._send_html(render_dashboard_html())
        elif parsed.path == "/nexora":
            with open(os.path.join(TEMPLATE_DIR, "nexora.html"), "r", encoding="utf-8") as f:
                self._send_html(f.read())
        elif parsed.path == "/api/data":
            self._send_json(fetch_dashboard_payload())
        else:
            self.send_error(404, "Endpoint not found")

    def do_POST(self):
        parsed = urlparse(self.path)
        content_len = int(self.headers.get("Content-Length", 0))
        raw_body = self.rfile.read(content_len) if content_len > 0 else b"{}"
        try:
            body = json.loads(raw_body.decode("utf-8"))
        except json.JSONDecodeError:
            self._send_json({"ok": False, "error": "Invalid JSON body"}, status=400)
            return

        if parsed.path == "/api/update_record":
            record_type = body.get("record_type")
            record_id = body.get("record_id")
            new_stage = body.get("workflow_stage")
            new_status = body.get("status")
            new_amount = body.get("total_amount")

            conn = get_db_connection()
            cur = conn.cursor()
            num = _suffix_num(record_id or "0001")

            if record_type == "SO":
                _, has_dn, has_sinv, has_pay, default_status = SO_STAGE_MAP.get(
                    new_stage, (True, False, False, False, new_status or "To Deliver & Bill")
                )
                dn_id = f"MAT-DN-2026-{num}" if has_dn else None
                sinv_id = f"ACC-SINV-2026-{num}" if has_sinv else None
                pay_id = f"ACC-PAY-2026-{num}" if has_pay else None
                cur.execute(
                    """
                    UPDATE sales_order
                    SET workflow_stage = ?, status = ?, total_amount = ?,
                        delivery_note_id = ?, sales_invoice_id = ?, payment_entry_id = ?
                    WHERE so_id = ?
                    """,
                    (new_stage, new_status or default_status, float(new_amount), dn_id, sinv_id, pay_id, record_id),
                )
            elif record_type == "PO":
                _, has_pr, has_pinv, has_pay, default_status = PO_STAGE_MAP.get(
                    new_stage, (True, False, False, False, new_status or "To Receive & Bill")
                )
                pr_id = f"MAT-PR-2026-{num}" if has_pr else None
                pinv_id = f"ACC-PINV-2026-{num}" if has_pinv else None
                pay_id = f"ACC-PAY-2026-01{num[-2:]}" if has_pay else None
                cur.execute(
                    """
                    UPDATE purchase_order
                    SET workflow_stage = ?, status = ?, total_amount = ?,
                        purchase_receipt_id = ?, purchase_invoice_id = ?, payment_entry_id = ?
                    WHERE po_id = ?
                    """,
                    (new_stage, new_status or default_status, float(new_amount), pr_id, pinv_id, pay_id, record_id),
                )
            else:
                conn.close()
                self._send_json({"ok": False, "error": "Unsupported record_type"}, status=400)
                return

            conn.commit()
            recalculate_stock_ledger(conn)
            conn.close()

            export_tables_to_csv()
            build_standalone_snapshots()
            self._send_json({"ok": True, "payload": fetch_dashboard_payload()})

        elif parsed.path == "/api/create_order":
            record_type = body.get("record_type")
            party_id = body.get("party_id")
            item_code = body.get("item_code")
            qty = int(body.get("qty", 1))
            stage = body.get("workflow_stage")
            today = datetime.now().strftime("%Y-%m-%d")

            if qty <= 0:
                self._send_json({"ok": False, "error": "Quantity must be >= 1"}, status=400)
                return

            conn = get_db_connection()
            cur = conn.cursor()
            item_row = cur.execute("SELECT * FROM item WHERE item_code = ?", (item_code,)).fetchone()
            if not item_row:
                conn.close()
                self._send_json({"ok": False, "error": f"Unknown item_code: {item_code}"}, status=400)
                return

            if record_type == "PO" and item_row["item_group"] != "Raw Materials":
                conn.close()
                self._send_json(
                    {
                        "ok": False,
                        "error": f"Business rule error: Purchase Orders may ONLY buy Raw Materials ({item_code} is {item_row['item_group']}).",
                    },
                    status=400,
                )
                return

            if record_type == "SO":
                count = cur.execute("SELECT COUNT(*) FROM sales_order").fetchone()[0] + 1
                num = f"{count:04d}"
                so_id = f"SAL-ORD-2026-{num}"
                rate = float(item_row["selling_rate"] or item_row["valuation_rate"])
                net = round(rate * qty, 2)
                gst = round(net * 0.18, 2)
                grand = round(net + gst, 2)
                st = stage or "Sales Order"
                _, has_dn, has_sinv, has_pay, status = SO_STAGE_MAP.get(st, (True, False, False, False, "To Deliver & Bill"))
                cur.execute(
                    """
                    INSERT INTO sales_order (
                        so_id, customer_id, order_date, delivery_date, workflow_stage, status,
                        quotation_id, delivery_note_id, sales_invoice_id, payment_entry_id,
                        net_total, gst_amount, total_amount, owner_emp_id
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        so_id,
                        party_id,
                        today,
                        today,
                        st,
                        status,
                        f"QTN-2026-{num}",
                        f"MAT-DN-2026-{num}" if has_dn else None,
                        f"ACC-SINV-2026-{num}" if has_sinv else None,
                        f"ACC-PAY-2026-{num}" if has_pay else None,
                        net,
                        gst,
                        grand,
                        "HR-EMP-0001",
                    ),
                )
                cur.execute(
                    "INSERT INTO sales_order_item (so_id, item_code, qty, rate, amount) VALUES (?, ?, ?, ?, ?)",
                    (so_id, item_code, qty, rate, net),
                )
            elif record_type == "PO":
                count = cur.execute("SELECT COUNT(*) FROM purchase_order").fetchone()[0] + 1
                num = f"{count:04d}"
                po_id = f"PUR-ORD-2026-{num}"
                rate = float(item_row["valuation_rate"])
                net = round(rate * qty, 2)
                gst = round(net * 0.18, 2)
                grand = round(net + gst, 2)
                st = stage or "Purchase Order"
                _, has_pr, has_pinv, has_pay, status = PO_STAGE_MAP.get(st, (True, False, False, False, "To Receive & Bill"))
                cur.execute(
                    """
                    INSERT INTO purchase_order (
                        po_id, supplier_id, order_date, schedule_date, workflow_stage, status,
                        material_request_id, purchase_receipt_id, purchase_invoice_id, payment_entry_id,
                        net_total, gst_amount, total_amount, buyer_emp_id
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        po_id,
                        party_id,
                        today,
                        today,
                        st,
                        status,
                        f"MAT-MR-2026-{num}",
                        f"MAT-PR-2026-{num}" if has_pr else None,
                        f"ACC-PINV-2026-{num}" if has_pinv else None,
                        f"ACC-PAY-2026-01{num[-2:]}" if has_pay else None,
                        net,
                        gst,
                        grand,
                        "HR-EMP-0002",
                    ),
                )
                cur.execute(
                    "INSERT INTO purchase_order_item (po_id, item_code, qty, rate, amount) VALUES (?, ?, ?, ?, ?)",
                    (po_id, item_code, qty, rate, net),
                )
            else:
                conn.close()
                self._send_json({"ok": False, "error": "Unsupported record_type"}, status=400)
                return

            conn.commit()
            recalculate_stock_ledger(conn)
            conn.close()
            export_tables_to_csv()
            build_standalone_snapshots()
            self._send_json({"ok": True, "payload": fetch_dashboard_payload()})

        elif parsed.path == "/api/reset_db":
            seed_all()
            export_tables_to_csv()
            build_standalone_snapshots()
            self._send_json({"ok": True, "payload": fetch_dashboard_payload()})
        else:
            self._send_json({"ok": False, "error": "Unknown POST endpoint"}, status=404)


def run_server(port=8050):
    init_database()
    export_tables_to_csv()
    build_standalone_snapshots()
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("127.0.0.1", port), ERPRequestHandler) as httpd:
        print("=" * 70)
        print("  VoltEdge Power Systems Pvt. Ltd. — ERPNext v16 Prototype & Showcase")
        print(f"  Part A (ERP Dashboard) : http://127.0.0.1:{port}/")
        print(f"  Part B (NEXORA Brochure): http://127.0.0.1:{port}/nexora")
        print(f"  SQLite DB Location     : {DB_PATH}")
        print("=" * 70)
        httpd.serve_forever()


if __name__ == "__main__":
    run_server()
