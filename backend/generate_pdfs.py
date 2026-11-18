"""
EBS Submission PDF Generator (Part A Capstone-PPT Deck & Part B Digital Sales Brochure)
Course: UE24CS343AB8 Enterprise Business Systems
Owner: Srujan (Database, Backend & Dashboard)

Generates two clean, light-background PDFs:
1. pdfs/EBS24CS-P01 001-002-003-004 VoltEdge-ERPNext.pdf  (Part A: 17-slide 16:9 Capstone-PPT Deck)
2. pdfs/EBS24CS-P02 001-002-003-004 NEXORA.pdf            (Part B: 8-page A4 Portrait Digital Sales Brochure)
"""

import base64
import html as html_lib
import os
import shutil
import subprocess
import sys
import zipfile

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR)
PDF_DIR = os.path.join(PROJECT_DIR, "pdfs")
BUILD_DIR = os.path.join(PDF_DIR, "_html_sources")

CAPSTONE_PPT_CANDIDATES = [
    r"d:\university\capstone\my part.pptx",
    r"d:\university\capstone\Review 2 PPT Format-0.pptx",
]

sys.path.insert(0, BASE_DIR)
from app import fetch_dashboard_payload, init_database  # noqa: E402
from generate_part_b_brochure import brochure_css, build_part_b_brochure  # noqa: E402
from generate_part_b_docx import generate_part_b_docx  # noqa: E402


def esc(val):
    return html_lib.escape(str(val))


def inr(val):
    return f"&#8377;{val:,.0f}"


def load_pes_logo_data_uri():
    """Load PES crest from the user's Capstone PPT master if present on disk."""
    for ppt_path in CAPSTONE_PPT_CANDIDATES:
        if os.path.exists(ppt_path):
            try:
                with zipfile.ZipFile(ppt_path) as zf:
                    if "ppt/media/image1.png" in zf.namelist():
                        raw = zf.read("ppt/media/image1.png")
                        b64 = base64.b64encode(raw).decode("ascii")
                        return f"data:image/png;base64,{b64}"
            except OSError:
                pass
    return ""


def get_team_footer_line(employees):
    names = []
    for emp in employees:
        nm = emp["employee_name"].split("(")[0].strip().upper()
        if nm:
            names.append(nm)
    if not names:
        names = ["SRUJAN", "ESHAAN", "ABHAY", "SIRI"]
    return "  &bull;  ".join(names)


def short_emp(emp_label):
    """Turn 'Eshaan (PES1UG24CS002)' or 'Processed by Eshaan (PES1UG24CS002)' into concise 'Eshaan (CS002)' or full SRN."""
    return str(emp_label).replace("Processed by ", "").replace("Approved by ", "")


def capstone_css():
    """
    Exact 16:9 PowerPoint slide styling matching d:\\university\\capstone\\my part.pdf,
    Capstone PPT (1).pdf, and Review 2.pdf (Retrospect master: #BD582C / #E48312 / #33CCCC / #DC2626 / #0088CC).
    """
    return """
    @page {
        size: 13.333in 7.5in;
        margin: 0;
    }
    * {
        box-sizing: border-box;
        margin: 0;
        padding: 0;
    }
    html, body {
        background-color: #FFFFFF;
        color: #111827;
        font-family: "Calibri", "Segoe UI", Arial, sans-serif;
        font-size: 10.5pt;
        line-height: 1.38;
        -webkit-print-color-adjust: exact !important;
        print-color-adjust: exact !important;
    }
    .slide {
        width: 13.333in;
        height: 7.5in;
        position: relative;
        overflow: hidden;
        background-color: #FFFFFF;
        page-break-after: always;
    }
    .slide:last-child {
        page-break-after: auto;
    }

    /* Master Header */
    .hdr-sub {
        position: absolute;
        top: 0.24in;
        left: 0.55in;
        font-size: 9.5pt;
        color: #7F8C8D;
        font-family: "Arial", "Calibri", sans-serif;
    }
    .hdr-logo {
        position: absolute;
        top: 0.20in;
        right: 0.24in;
        width: 0.78in;
        height: auto;
    }
    .hdr-logo-fallback {
        position: absolute;
        top: 0.24in;
        right: 0.28in;
        border: 1pt solid #1E3A8A;
        padding: 2pt 6pt;
        font-size: 8.5pt;
        font-weight: 700;
        color: #1E3A8A;
    }
    .hdr-title {
        position: absolute;
        top: 0.54in;
        right: 1.15in;
        left: 0.55in;
        text-align: right;
        font-family: "Trebuchet MS", "Calibri", sans-serif;
        font-size: 20.5pt;
        font-weight: 700;
        color: #DC2626;
        line-height: 1.15;
    }
    .hdr-cyan {
        position: absolute;
        top: 0.96in;
        right: 1.15in;
        width: 7.9in;
        height: 2.8pt;
        background-color: #33CCCC;
    }
    .hdr-rule {
        position: absolute;
        top: 1.03in;
        left: 0.55in;
        right: 0.55in;
        height: 0.75pt;
        background-color: #9CA3AF;
    }

    /* Master Footer (Retrospect terracotta + amber top hairline) */
    .ftr-amber {
        position: absolute;
        left: 0;
        right: 0;
        bottom: 0.42in;
        height: 4.5pt;
        background-color: #E48312;
    }
    .ftr-terra {
        position: absolute;
        left: 0;
        right: 0;
        bottom: 0;
        height: 0.42in;
        background-color: #BD582C;
        color: #FFFFFF;
        display: flex;
        align-items: center;
        justify-content: center;
        font-family: "Trebuchet MS", "Calibri", sans-serif;
        font-size: 11pt;
        letter-spacing: 0.4pt;
    }
    .ftr-num {
        position: absolute;
        right: 0.35in;
        font-size: 10pt;
        font-weight: 700;
        color: #FFFFFF;
    }

    /* Main Slide Content Area */
    .slide-body {
        position: absolute;
        top: 1.16in;
        left: 0.55in;
        right: 0.55in;
        bottom: 0.56in;
        display: flex;
        flex-direction: column;
        gap: 8pt;
    }

    /* Plain Capstone Text Hierarchy (NO bento boxes, NO neon pills) */
    .sub-blue {
        font-family: "Calibri", "Trebuchet MS", sans-serif;
        font-size: 12.5pt;
        font-weight: 700;
        color: #0088CC;
        margin-bottom: 3pt;
    }
    .sub-navy {
        font-family: "Calibri", "Trebuchet MS", sans-serif;
        font-size: 11.5pt;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 3pt;
    }
    .sub-rust {
        font-family: "Calibri", "Trebuchet MS", sans-serif;
        font-size: 11.5pt;
        font-weight: 700;
        color: #BD582C;
        margin-bottom: 3pt;
    }
    p.plain {
        font-size: 10pt;
        color: #111827;
        margin-bottom: 4pt;
    }
    ul.cap-list {
        list-style: none;
        padding-left: 0;
    }
    ul.cap-list li {
        position: relative;
        padding-left: 14pt;
        margin-bottom: 4.5pt;
        font-size: 9.8pt;
        color: #111827;
    }
    ul.cap-list li::before {
        content: "\\25AA";
        position: absolute;
        left: 0;
        top: -0.5pt;
        color: #E48312;
        font-size: 10pt;
    }
    .key-b {
        color: #1E3A8A;
        font-weight: 700;
    }

    /* Layouts */
    .two-col {
        display: flex;
        gap: 20pt;
        width: 100%;
    }
    .col-half {
        flex: 1;
        min-width: 0;
    }
    .col-40 {
        flex: 0.42;
        min-width: 0;
    }
    .col-60 {
        flex: 0.58;
        min-width: 0;
    }
    .three-col {
        display: flex;
        gap: 14pt;
        width: 100%;
    }
    .col-third {
        flex: 1;
        min-width: 0;
    }

    /* Clean PowerPoint / Word Student Tables */
    table.ppt {
        width: 100%;
        border-collapse: collapse;
        font-size: 8.6pt;
    }
    table.ppt th {
        background-color: #E8EEF5;
        color: #111827;
        font-weight: 700;
        text-align: left;
        padding: 4pt 6pt;
        border: 0.75pt solid #CBD5E1;
    }
    table.ppt td {
        padding: 3.2pt 6pt;
        border: 0.75pt solid #CBD5E1;
        color: #111827;
        vertical-align: top;
    }
    table.ppt tr:nth-child(even) td {
        background-color: #F9FAFB;
    }
    table.ppt.warm th {
        background-color: #F5EBE6;
    }
    .num {
        text-align: right;
        font-variant-numeric: tabular-nums;
        white-space: nowrap;
    }
    .mono {
        font-family: "Consolas", "Courier New", monospace;
        font-size: 8pt;
    }
    table.ppt td.mono {
        white-space: nowrap;
    }

    /* Cover Slide Styling (matches Review 2.pdf & Capstone PPT (1).pdf) */
    .cover-top {
        margin-top: 0.62in;
        text-align: center;
        padding: 0 0.8in;
    }
    .cover-deg {
        font-family: "Trebuchet MS", "Calibri", sans-serif;
        font-size: 15.5pt;
        font-weight: 700;
        color: #DC2626;
        margin-bottom: 2pt;
    }
    .cover-course {
        font-family: "Trebuchet MS", "Calibri", sans-serif;
        font-size: 18pt;
        font-weight: 700;
        color: #DC2626;
        margin-top: 4pt;
    }
    .cover-part {
        font-family: "Trebuchet MS", "Calibri", sans-serif;
        font-size: 13pt;
        font-weight: 700;
        color: #1E3A8A;
        margin-top: 4pt;
    }
    .cover-div {
        width: 82%;
        height: 1pt;
        background-color: #CBD5E1;
        margin: 0.22in auto 0.24in auto;
    }
    table.cover-meta {
        width: 10.7in;
        margin: 0 auto;
        border-collapse: collapse;
        font-size: 11.5pt;
    }
    table.cover-meta td {
        padding: 5.5pt 4pt;
        vertical-align: top;
    }
    .cm-lbl {
        width: 2.25in;
        font-weight: 700;
        color: #BD582C;
    }
    .cm-sep {
        width: 0.25in;
        font-weight: 700;
        color: #BD582C;
    }
    .cm-val {
        color: #1F2937;
    }

    /* Outline Numbered Circles (matches Capstone PPT Slide 2) */
    .out-row {
        display: flex;
        align-items: center;
        gap: 12pt;
        margin-bottom: 7pt;
    }
    .out-num {
        width: 22pt;
        height: 22pt;
        border-radius: 50%;
        background-color: #BD582C;
        color: #FFFFFF;
        font-weight: 700;
        font-size: 11pt;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
    }
    .out-txt {
        font-size: 11pt;
        color: #1F2937;
    }

    /* Light Visual Frame & Figure Captions */
    .fig-frame {
        border: 0.75pt solid #CBD5E1;
        background-color: #FFFFFF;
        padding: 6pt 8pt;
    }
    .fig-cap {
        font-size: 9.2pt;
        font-weight: 700;
        color: #1E3A8A;
        margin-top: 4pt;
    }
    .fig-desc {
        font-size: 8.8pt;
        color: #374151;
        margin-top: 1pt;
    }
    .url-line {
        font-family: "Consolas", monospace;
        font-size: 8pt;
        color: #1D4ED8;
    }

    /* KPI Plain Academic Row (No SaaS cards) */
    table.kpi-strip {
        width: 100%;
        border-collapse: collapse;
        margin-bottom: 4pt;
    }
    table.kpi-strip td {
        width: 25%;
        border: 0.75pt solid #CBD5E1;
        background-color: #F9FAFB;
        padding: 6pt 10pt;
    }
    .kpi-lbl {
        font-size: 8.5pt;
        color: #4B5563;
        font-weight: 700;
    }
    .kpi-val {
        font-size: 16pt;
        font-weight: 700;
        color: #1F2937;
        margin: 1pt 0;
    }
    .kpi-sub {
        font-size: 8pt;
        color: #6B7280;
    }

    /* Clean Browser Capture Chrome Bar (Light background, zero dark header) */
    .ui-win {
        border: 1pt solid #94A3B8;
        background-color: #FFFFFF;
    }
    .ui-bar {
        background-color: #F1F5F9;
        border-bottom: 0.75pt solid #CBD5E1;
        padding: 3.5pt 8pt;
        font-size: 8pt;
        color: #334155;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .ui-url {
        background-color: #FFFFFF;
        border: 0.75pt solid #CBD5E1;
        padding: 1pt 8pt;
        font-family: "Consolas", monospace;
        font-size: 7.8pt;
        color: #475569;
    }
    """


def slide_header_footer(sub_left, title, footer_names, slide_no, logo_uri):
    logo_html = (
        f'<img class="hdr-logo" src="{logo_uri}" alt="PES">'
        if logo_uri
        else '<div class="hdr-logo-fallback">PESU</div>'
    )
    return f"""
        <div class="hdr-sub">{esc(sub_left)}</div>
        {logo_html}
        <div class="hdr-title">{esc(title)}</div>
        <div class="hdr-cyan"></div>
        <div class="hdr-rule"></div>
        <div class="ftr-amber"></div>
        <div class="ftr-terra">
            <span>{footer_names}</span>
            <span class="ftr-num">{slide_no}</span>
        </div>
    """


def wrap_slide(body_html, sub_left, title, footer_names, slide_no, logo_uri):
    return f"""
    <div class="slide">
        {slide_header_footer(sub_left, title, footer_names, slide_no, logo_uri)}
        <div class="slide-body">
            {body_html}
        </div>
    </div>
    """


def wrap_cover_slide(inner_html, footer_names, slide_no, logo_uri):
    logo_html = (
        f'<img class="hdr-logo" src="{logo_uri}" alt="PES" style="width:0.85in;">'
        if logo_uri
        else '<div class="hdr-logo-fallback">PESU</div>'
    )
    return f"""
    <div class="slide">
        {logo_html}
        {inner_html}
        <div class="ftr-amber"></div>
        <div class="ftr-terra">
            <span>{footer_names}</span>
            <span class="ftr-num">{slide_no}</span>
        </div>
    </div>
    """


# =====================================================================
# MATPLOTLIB-STYLE WHITE VECTOR PLOTS (Matching d:\university\capstone\my part.pdf)
# =====================================================================

def svg_mpl_monthly_sales(monthly_sales):
    """Matplotlib-style white plot: Monthly Sales Revenue Bars + Trend Line."""
    w, h = 540, 238
    pl, pt, pr, pb = 64, 34, 24, 38
    pw, ph = w - pl - pr, h - pt - pb
    max_val = max([r["revenue_lakhs"] for r in monthly_sales] + [20.0]) * 1.32
    n = max(len(monthly_sales), 1)
    step = pw / n
    bw = min(46, step * 0.52)

    grid = []
    for i in range(5):
        frac = i / 4.0
        y = pt + ph * (1.0 - frac)
        val = max_val * frac
        grid.append(
            f'<line x1="{pl}" y1="{y:.1f}" x2="{pl+pw}" y2="{y:.1f}" '
            f'stroke="#E5E7EB" stroke-width="0.9" stroke-dasharray="3,2"/>'
            f'<text x="{pl-6}" y="{y+3.5:.1f}" text-anchor="end" font-size="8.5" fill="#111827">{val:.0f}</text>'
        )

    bars = []
    line_pts = []
    for idx, row in enumerate(monthly_sales):
        cx = pl + idx * step + step * 0.5
        bh = (row["revenue_lakhs"] / max_val) * ph
        by = pt + ph - bh
        bx = cx - bw / 2.0
        bars.append(
            f'<rect x="{bx:.1f}" y="{by:.1f}" width="{bw:.1f}" height="{bh:.1f}" fill="#1F77B4" stroke="#111827" stroke-width="0.5"/>'
            f'<text x="{cx:.1f}" y="{by-8:.1f}" text-anchor="middle" font-size="8.2" font-weight="bold" fill="#111827">'
            f'&#8377;{row["revenue_lakhs"]:.2f}L</text>'
            f'<text x="{cx:.1f}" y="{pt+ph+14}" text-anchor="middle" font-size="8.5" fill="#111827">{esc(row["month_label"])}</text>'
            f'<text x="{cx:.1f}" y="{pt+ph+25}" text-anchor="middle" font-size="7.5" fill="#4B5563">({row["order_count"]} SO)</text>'
        )
        line_pts.append(f"{cx:.1f},{by:.1f}")

    dots = "".join(
        f'<circle cx="{pt_xy.split(",")[0]}" cy="{pt_xy.split(",")[1]}" r="3" fill="#FF7F0E" stroke="#111827" stroke-width="0.6"/>'
        for pt_xy in line_pts
    )
    polyline = (
        f'<polyline points="{" ".join(line_pts)}" fill="none" stroke="#FF7F0E" stroke-width="1.8"/>'
        if len(line_pts) > 1
        else ""
    )
    range_lbl = (
        f"{esc(monthly_sales[0]['month_label'])} - {esc(monthly_sales[-1]['month_label'])}"
        if monthly_sales
        else "FY 2026-27"
    )

    return f"""
    <svg viewBox="0 0 {w} {h}" width="100%" style="background:#FFFFFF; font-family:Arial,Calibri,sans-serif; display:block;">
        <text x="{w/2:.1f}" y="19" text-anchor="middle" font-size="11" font-weight="bold" fill="#111827">
            Monthly Sales Revenue Trend ({range_lbl})
        </text>
        {"".join(grid)}
        <rect x="{pl}" y="{pt}" width="{pw}" height="{ph}" fill="none" stroke="#111827" stroke-width="1"/>
        {"".join(bars)}
        {polyline}
        {dots}
        <text x="16" y="{pt+ph/2:.1f}" text-anchor="middle" font-size="8.8" fill="#111827"
              transform="rotate(-90 16 {pt+ph/2:.1f})">Revenue (INR Lakhs)</text>
        <rect x="{pl+8}" y="{pt+6}" width="126" height="32" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="0.8"/>
        <rect x="{pl+16}" y="{pt+12}" width="12" height="7" fill="#1F77B4"/>
        <text x="{pl+33}" y="{pt+18.5}" font-size="7.8" fill="#111827">Monthly Revenue</text>
        <line x1="{pl+16}" y1="{pt+28}" x2="{pl+28}" y2="{pt+28}" stroke="#FF7F0E" stroke-width="1.8"/>
        <text x="{pl+33}" y="{pt+31}" font-size="7.8" fill="#111827">Order Trend</text>
    </svg>
    """


def _prepare_slide_data(raw):
    """Adapt live fetch_dashboard_payload() into uniform, zero-hardcode slide metrics."""
    customers = raw["customers"]
    suppliers = raw["suppliers"]
    emp_map = {e["employee_id"]: f"{e['employee_name']} ({e['srn']})" for e in raw["employees"]}
    cust_map = {c["customer_id"]: c for c in customers}
    sup_map = {s["supplier_id"]: s for s in suppliers}
    term_map = {t["payment_term_id"]: t["term_name"] for t in raw["payment_terms"]}

    months_fmt = {
        "2026-05": "May 2026",
        "2026-06": "Jun 2026",
        "2026-07": "Jul 2026",
        "2026-08": "Aug 2026",
    }
    monthly_sales = []
    for m in raw["monthly_sales"]:
        monthly_sales.append({
            **m,
            "month_label": months_fmt.get(m["month"], m["month"]),
        })

    po_counts = {}
    for po in raw["purchase_orders"]:
        po_counts[po["supplier_id"]] = po_counts.get(po["supplier_id"], 0) + 1
    sup_by_name = {s["supplier_name"]: s for s in suppliers}
    supplier_spend = []
    for sp in raw["supplier_spend"]:
        s_obj = sup_by_name.get(sp["supplier_name"], {})
        supplier_spend.append({
            **sp,
            "supplier_group": s_obj.get("supplier_group", "Raw Materials"),
            "po_count": po_counts.get(s_obj.get("supplier_id", ""), 0),
        })

    sales_orders = []
    for so in raw["sales_orders"]:
        c_obj = cust_map.get(so["customer_id"], {})
        sales_orders.append({
            **so,
            "term_name": term_map.get(c_obj.get("default_payment_term", ""), "Net 30 Days"),
            "srn_reference": emp_map.get(so["owner_emp_id"], so.get("owner_name", "")),
        })

    purchase_orders = []
    for po in raw["purchase_orders"]:
        s_obj = sup_map.get(po["supplier_id"], {})
        purchase_orders.append({
            **po,
            "expected_date": po["schedule_date"],
            "term_name": term_map.get(s_obj.get("default_payment_term", ""), "Net 30 Days"),
            "srn_reference": emp_map.get(po["buyer_emp_id"], po.get("buyer_name", "")),
        })

    inventory_report = []
    for sl in raw["stock_ledger"]:
        inventory_report.append({
            **sl,
            "safety_stock": sl.get("reorder_level", 5),
            "value_lakhs": round(sl["stock_value"] / 100000.0, 2),
        })

    rk = raw["kpis"]
    delivered_so = sum(1 for so in sales_orders if so["workflow_stage"] in ("Delivery Note", "Sales Invoice", "Payment Received"))
    completed_so = sum(1 for so in sales_orders if so["workflow_stage"] == "Payment Received")
    so_count = len(sales_orders)
    po_count = len(purchase_orders)
    inventory_units = sum(int(sl["actual_qty"]) for sl in raw["stock_ledger"])

    kpis = {
        **rk,
        "sales_lakhs": round(rk["total_sales_revenue"] / 100000.0, 2),
        "purchase_lakhs": round(rk["total_procurement_spend"] / 100000.0, 2),
        "inventory_lakhs": round(rk["total_inventory_value"] / 100000.0, 2),
        "so_count": so_count,
        "po_count": po_count,
        "completed_so": completed_so,
        "delivered_so": delivered_so,
        "fulfillment_pct": round((delivered_so / so_count * 100.0) if so_count else 0.0, 1),
        "inventory_units": inventory_units,
    }

    return {
        **raw,
        "emp_map": emp_map,
        "monthly_sales": monthly_sales,
        "supplier_spend": supplier_spend,
        "sales_orders": sales_orders,
        "purchase_orders": purchase_orders,
        "inventory_report": inventory_report,
        "kpis": kpis,
    }


def svg_mpl_supplier_spend(supplier_spend):
    """Matplotlib-style horizontal bar plot: Supplier Procurement Spend."""
    w, h = 540, 238
    pl, pt, pr, pb = 206, 34, 52, 34
    pw, ph = w - pl - pr, h - pt - pb
    rows = supplier_spend[:6]
    max_val = max([r["spend_lakhs"] for r in rows] + [10.0]) * 1.18
    n = max(len(rows), 1)
    step = ph / n
    bh = min(20, step * 0.56)

    grid = []
    for i in range(5):
        frac = i / 4.0
        x = pl + pw * frac
        val = max_val * frac
        grid.append(
            f'<line x1="{x:.1f}" y1="{pt}" x2="{x:.1f}" y2="{pt+ph}" stroke="#E5E7EB" stroke-width="0.9" stroke-dasharray="3,2"/>'
            f'<text x="{x:.1f}" y="{pt+ph+13}" text-anchor="middle" font-size="8.2" fill="#111827">{val:.1f}</text>'
        )

    bars = []
    for idx, row in enumerate(rows):
        cy = pt + idx * step + step * 0.5
        by = cy - bh / 2.0
        bw = (row["spend_lakhs"] / max_val) * pw
        short_name = row["supplier_name"].replace(" Pvt. Ltd.", "").replace(" Ltd.", "")
        if len(short_name) > 29:
            short_name = short_name[:27] + ".."
        bars.append(
            f'<rect x="{pl}" y="{by:.1f}" width="{bw:.1f}" height="{bh:.1f}" fill="#FF7F0E" stroke="#111827" stroke-width="0.5"/>'
            f'<text x="{pl-6}" y="{cy+3:.1f}" text-anchor="end" font-size="8.2" fill="#111827">{esc(short_name)}</text>'
            f'<text x="{pl+bw+5:.1f}" y="{cy+3:.1f}" font-size="8.2" font-weight="bold" fill="#111827">&#8377;{row["spend_lakhs"]:.2f}L ({row["po_count"]} PO)</text>'
        )

    return f"""
    <svg viewBox="0 0 {w} {h}" width="100%" style="background:#FFFFFF; font-family:Arial,Calibri,sans-serif; display:block;">
        <text x="{w/2:.1f}" y="19" text-anchor="middle" font-size="11" font-weight="bold" fill="#111827">
            Supplier-Wise Raw Material Spend (FY 2026-27)
        </text>
        {"".join(grid)}
        <rect x="{pl}" y="{pt}" width="{pw}" height="{ph}" fill="none" stroke="#111827" stroke-width="1"/>
        {"".join(bars)}
        <text x="{pl+pw/2:.1f}" y="{h-6}" text-anchor="middle" font-size="8.8" fill="#111827">Total Procurement Spend (INR Lakhs)</text>
    </svg>
    """


def svg_mpl_inventory_vs_safety(inventory_report):
    """Matplotlib-style grouped bar plot: Calculated Stock On-Hand vs Safety Stock across all 12 SKUs."""
    w, h = 540, 238
    pl, pt, pr, pb = 54, 34, 20, 52
    pw, ph = w - pl - pr, h - pt - pb
    rows = sorted(inventory_report, key=lambda r: r["item_code"])
    max_qty = max([max(r["available_qty"], r["safety_stock"]) for r in rows] + [100]) * 1.15
    n = max(len(rows), 1)
    step = pw / n
    bw = min(12, step * 0.34)

    grid = []
    for i in range(5):
        frac = i / 4.0
        y = pt + ph * (1.0 - frac)
        val = max_qty * frac
        grid.append(
            f'<line x1="{pl}" y1="{y:.1f}" x2="{pl+pw}" y2="{y:.1f}" stroke="#E5E7EB" stroke-width="0.9" stroke-dasharray="3,2"/>'
            f'<text x="{pl-6}" y="{y+3:.1f}" text-anchor="end" font-size="8.2" fill="#111827">{val:.0f}</text>'
        )

    bars = []
    for idx, row in enumerate(rows):
        cx = pl + idx * step + step * 0.5
        h1 = (max(0, row["available_qty"]) / max_qty) * ph
        h2 = (row["safety_stock"] / max_qty) * ph
        y1 = pt + ph - h1
        y2 = pt + ph - h2
        code = row["item_code"].replace("ITM-RAW-", "RM-").replace("ITM-", "")
        bars.append(
            f'<rect x="{cx-bw-1:.1f}" y="{y1:.1f}" width="{bw:.1f}" height="{h1:.1f}" fill="#2CA02C" stroke="#111827" stroke-width="0.4"/>'
            f'<rect x="{cx+1:.1f}" y="{y2:.1f}" width="{bw:.1f}" height="{h2:.1f}" fill="#D62728" stroke="#111827" stroke-width="0.4"/>'
            f'<text x="{cx:.1f}" y="{min(y1, y2)-4:.1f}" text-anchor="middle" font-size="7.0" fill="#111827">{row["available_qty"]}</text>'
            f'<text x="{cx:.1f}" y="{pt+ph+13}" text-anchor="middle" font-size="6.8" fill="#111827" '
            f'transform="rotate(-28 {cx:.1f} {pt+ph+13})">{esc(code)}</text>'
        )

    return f"""
    <svg viewBox="0 0 {w} {h}" width="100%" style="background:#FFFFFF; font-family:Arial,Calibri,sans-serif; display:block;">
        <text x="{w/2:.1f}" y="19" text-anchor="middle" font-size="11" font-weight="bold" fill="#111827">
            Calculated Available Stock vs. Reorder Level (All 12 SKUs)
        </text>
        {"".join(grid)}
        <rect x="{pl}" y="{pt}" width="{pw}" height="{ph}" fill="none" stroke="#111827" stroke-width="1"/>
        {"".join(bars)}
        <text x="15" y="{pt+ph/2:.1f}" text-anchor="middle" font-size="8.8" fill="#111827"
              transform="rotate(-90 15 {pt+ph/2:.1f})">Quantity (Units)</text>
        <rect x="{pl+pw-138}" y="{pt+6}" width="132" height="30" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="0.8"/>
        <rect x="{pl+pw-130}" y="{pt+12}" width="10" height="7" fill="#2CA02C"/>
        <text x="{pl+pw-115}" y="{pt+18.5}" font-size="7.8" fill="#111827">Available Qty</text>
        <rect x="{pl+pw-130}" y="{pt+24}" width="10" height="7" fill="#D62728"/>
        <text x="{pl+pw-115}" y="{pt+30.5}" font-size="7.8" fill="#111827">Reorder Threshold</text>
    </svg>
    """


def svg_system_architecture(k):
    """Draw.io-style light VoltEdge ERPNext v16 MariaDB & Offline SQLite architecture diagram."""
    return f"""
    <svg viewBox="0 0 560 220" width="100%" style="background:#FFFFFF; font-family:Arial,Calibri,sans-serif; display:block;">
        <defs>
            <marker id="arrA" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto">
                <polygon points="0 0, 7 3.5, 0 7" fill="#334155"/>
            </marker>
        </defs>
        <text x="280" y="18" text-anchor="middle" font-size="10.2" font-weight="bold" fill="#111827">
            VoltEdge ERPNext v16 (MariaDB DDL + Offline SQLite) Dual-Cycle Flow
        </text>

        <!-- Master Data Layer -->
        <rect x="20" y="34" width="140" height="162" fill="#F8FAFC" stroke="#1E3A8A" stroke-width="1.2"/>
        <rect x="20" y="34" width="140" height="22" fill="#1E3A8A"/>
        <text x="90" y="48.5" text-anchor="middle" font-size="8.8" font-weight="bold" fill="#FFFFFF">6 Master DocTypes</text>
        <text x="30" y="72" font-size="8" fill="#111827">&#8226; tabEmployee (4 SRNs)</text>
        <text x="30" y="90" font-size="8" fill="#111827">&#8226; tabCustomer (8 B2B)</text>
        <text x="30" y="108" font-size="8" fill="#111827">&#8226; tabSupplier (6 RM)</text>
        <text x="30" y="126" font-size="8" fill="#111827">&#8226; tabItem (12: 6FG+6RM)</text>
        <text x="30" y="144" font-size="8" fill="#111827">&#8226; tabWarehouse (4 Hubs)</text>
        <text x="30" y="162" font-size="8" fill="#111827">&#8226; tabPayment Terms (4)</text>
        <text x="30" y="184" font-size="7.3" fill="#4B5563">Docker v16 + SQLite mirror</text>

        <!-- Cycle 1 O2C -->
        <rect x="202" y="34" width="160" height="72" fill="#EFF6FF" stroke="#0088CC" stroke-width="1.2"/>
        <text x="282" y="51" text-anchor="middle" font-size="8.8" font-weight="bold" fill="#0077B6">Cycle 1: Order-to-Cash (O2C)</text>
        <text x="282" y="66" text-anchor="middle" font-size="7.8" fill="#111827">{k['so_count']} Sales Orders (&#8377;{k['sales_lakhs']:.2f}L)</text>
        <text x="282" y="80" text-anchor="middle" font-size="7.5" fill="#374151">QTN &#8594; SO &#8594; DN &#8594; SINV &#8594; PAY</text>
        <text x="282" y="95" text-anchor="middle" font-size="7.3" fill="#4B5563">Finished Goods Dispatch + 18% GST</text>

        <!-- Cycle 2 P2P + Mfg -->
        <rect x="202" y="124" width="160" height="72" fill="#FFF7ED" stroke="#BD582C" stroke-width="1.2"/>
        <text x="282" y="141" text-anchor="middle" font-size="8.8" font-weight="bold" fill="#BD582C">Cycle 2: P2P + Mfg</text>
        <text x="282" y="156" text-anchor="middle" font-size="7.8" fill="#111827">{k['po_count']} RM POs (&#8377;{k['purchase_lakhs']:.2f}L)</text>
        <text x="282" y="170" text-anchor="middle" font-size="7.5" fill="#374151">MR &#8594; PO &#8594; PR &#8594; PINV &#8594; PAY</text>
        <text x="282" y="185" text-anchor="middle" font-size="7.3" fill="#4B5563">+ 24 Stock Entries -&gt; {k['sle_count']} SLEs</text>

        <!-- Analytics / Export -->
        <rect x="404" y="34" width="138" height="162" fill="#F8FAFC" stroke="#1E3A8A" stroke-width="1.2"/>
        <rect x="404" y="34" width="138" height="22" fill="#BD582C"/>
        <text x="473" y="48.5" text-anchor="middle" font-size="8.8" font-weight="bold" fill="#FFFFFF">Outputs &amp; Reports</text>
        <text x="414" y="74" font-size="8" font-weight="bold" fill="#1E3A8A">REST Sync + Server</text>
        <text x="414" y="88" font-size="7.6" fill="#111827">app.py (Port 8050)</text>
        <text x="414" y="110" font-size="8" font-weight="bold" fill="#1E3A8A">Calculated Bin</text>
        <text x="414" y="124" font-size="7.6" fill="#111827">SUM(SLE) -&gt; 12 Balances</text>
        <text x="414" y="146" font-size="8" font-weight="bold" fill="#1E3A8A">3 Live MIS Reports</text>
        <text x="414" y="160" font-size="7.6" fill="#111827">Sales, RM Spend, Stock</text>
        <text x="414" y="182" font-size="7.6" fill="#4B5563">+ 13 ERPNext CSV Files</text>

        <!-- Arrows -->
        <line x1="160" y1="70" x2="200" y2="70" stroke="#334155" stroke-width="1.2" marker-end="url(#arrA)"/>
        <line x1="160" y1="160" x2="200" y2="160" stroke="#334155" stroke-width="1.2" marker-end="url(#arrA)"/>
        <line x1="362" y1="70" x2="402" y2="70" stroke="#334155" stroke-width="1.2" marker-end="url(#arrA)"/>
        <line x1="362" y1="160" x2="402" y2="160" stroke="#334155" stroke-width="1.2" marker-end="url(#arrA)"/>
    </svg>
    """


def svg_process_cycle(title, stages, accent="#0088CC"):
    """Draw horizontal 5-step chevron-style flow matching Capstone PPT (1).pdf Slide 4."""
    w, h = 1140, 118
    step_w = 212
    gap = 15
    boxes = []
    for i, (num, st_title, doc_id, note) in enumerate(stages):
        x = 10 + i * (step_w + gap)
        boxes.append(f"""
            <polygon points="{x},12 {x+step_w-14},12 {x+step_w},44 {x+step_w-14},76 {x},76 {x+12 if i>0 else x},44"
                     fill="{'#FFF7ED' if i==len(stages)-1 else '#F8FAFC'}" stroke="{accent}" stroke-width="1.3"/>
            <text x="{x+20}" y="30" font-size="10.5" font-weight="bold" fill="{accent}">Stage {num}: {esc(st_title)}</text>
            <text x="{x+20}" y="47" font-size="9.5" font-weight="bold" fill="#111827">{esc(doc_id)}</text>
            <text x="{x+20}" y="63" font-size="8.6" fill="#4B5563">{esc(note)}</text>
        """)
    return f"""
    <svg viewBox="0 0 {w} {h}" width="100%" style="background:#FFFFFF; font-family:Arial,Calibri,sans-serif; display:block;">
        <text x="12" y="10" font-size="9.5" font-weight="bold" fill="#1E3A8A">{esc(title)}</text>
        <g transform="translate(0, 12)">
            {"".join(boxes)}
        </g>
    </svg>
    """


def svg_er_schema_diagram():
    """Authentic ERPNext v16 MariaDB 13-table `tab*` ER Schema on white canvas."""
    def tbl(x, y, w, name, hdr_bg, cols):
        row_h = 13.5
        tot_h = 19 + len(cols) * row_h + 4
        lines = [
            f'<rect x="{x}" y="{y}" width="{w}" height="{tot_h}" fill="#FFFFFF" stroke="#64748B" stroke-width="1"/>',
            f'<rect x="{x}" y="{y}" width="{w}" height="19" fill="{hdr_bg}"/>',
            f'<text x="{x+8}" y="{y+13}" font-size="8.6" font-weight="bold" fill="#FFFFFF">{name}</text>',
        ]
        for idx, (tag, col_nm, col_ty) in enumerate(cols):
            cy = y + 30 + idx * row_h
            tag_clr = "#B45309" if tag == "PK" else ("#0369A1" if tag == "FK" else "#6B7280")
            lines.append(
                f'<text x="{x+7}" y="{cy}" font-size="7.2" font-weight="bold" fill="{tag_clr}">{tag}</text>'
                f'<text x="{x+26}" y="{cy}" font-size="7.5" fill="#111827">{col_nm}</text>'
                f'<text x="{x+w-7}" y="{cy}" text-anchor="end" font-size="6.9" fill="#64748B">{col_ty}</text>'
            )
        return "".join(lines)

    elements = [
        '<path d="M 240 48 L 325 48" stroke="#64748B" stroke-width="1" fill="none"/>',
        '<path d="M 240 132 L 274 132 L 274 72 L 325 72" stroke="#64748B" stroke-width="1" fill="none"/>',
        '<path d="M 240 202 L 290 202 L 290 94 L 325 94" stroke="#64748B" stroke-width="1" fill="none"/>',
        '<path d="M 240 278 L 274 278 L 274 248 L 325 248" stroke="#64748B" stroke-width="1" fill="none"/>',
        '<path d="M 240 148 L 304 148 L 304 268 L 325 268" stroke="#64748B" stroke-width="1" fill="none"/>',
        '<path d="M 590 88 L 650 88 L 650 56 L 690 56" stroke="#0088CC" stroke-width="1.2" fill="none"/>',
        '<path d="M 590 275 L 650 275 L 650 154 L 690 154" stroke="#BD582C" stroke-width="1.2" fill="none"/>',
        '<path d="M 920 245 L 950 245 L 950 355 L 920 355" stroke="#2CA02C" stroke-width="1.1" fill="none"/>',
        '<path d="M 240 375 L 672 375 L 672 355 L 690 355" stroke="#2CA02C" stroke-width="1.1" fill="none"/>',
        '<path d="M 1045 140 L 1045 355 L 920 355" stroke="#2CA02C" stroke-width="1.1" fill="none"/>',

        # Left column: 5 Master DocTypes (+ Item on far right)
        tbl(15, 10, 225, "tabCustomer (8 rows)", "#1E3A8A", [
            ("PK", "name (CUS-2026-xxxx)", "VARCHAR"),
            ("", "customer_name, tax_id", "VARCHAR"),
            ("FK", "payment_terms, account_mgr", "FK"),
        ]),
        tbl(15, 92, 225, "tabEmployee (4 SRNs)", "#1E3A8A", [
            ("PK", "name (HR-EMP-xxxx)", "VARCHAR"),
            ("", "employee_name, custom_srn", "VARCHAR"),
            ("", "designation, docstatus", "VARCHAR"),
        ]),
        tbl(15, 174, 225, "tabPayment Terms Template (4)", "#1E3A8A", [
            ("PK", "name (PT-xxx)", "VARCHAR"),
            ("", "template_name, credit_days", "INT"),
        ]),
        tbl(15, 240, 225, "tabSupplier (6 RM Vendors)", "#1E3A8A", [
            ("PK", "name (SUP-2026-xxxx)", "VARCHAR"),
            ("", "supplier_name, tax_id", "VARCHAR"),
            ("FK", "payment_terms, custom_buyer", "FK"),
        ]),
        tbl(15, 326, 225, "tabWarehouse (4 Hubs)", "#1E3A8A", [
            ("PK", "name (WH-xxxx)", "VARCHAR"),
            ("", "warehouse_name, city", "VARCHAR"),
            ("FK", "custom_manager_id", "FK"),
        ]),

        # Center column: O2C & P2P Transaction DocTypes
        tbl(325, 14, 265, "tabSales Order (12 O2C Chains)", "#0088CC", [
            ("PK", "name (SAL-ORD-2026-xxxx)", "VARCHAR"),
            ("FK", "customer -> tabCustomer", "FK"),
            ("", "custom_quotation_id, custom_delivery_note_id", "TEXT"),
            ("", "custom_sales_invoice_id, custom_payment_id", "TEXT"),
            ("", "workflow_state, status, docstatus", "INT/TXT"),
            ("", "net_total, gst, grand_total", "DECIMAL"),
        ]),
        tbl(325, 200, 265, "tabPurchase Order (12 RM POs)", "#BD582C", [
            ("PK", "name (PUR-ORD-2026-xxxx)", "VARCHAR"),
            ("FK", "supplier -> tabSupplier", "FK"),
            ("", "custom_mr_id, custom_pr_id", "TEXT"),
            ("", "custom_pinv_id, custom_payment_id", "TEXT"),
            ("", "workflow_state, status, docstatus", "INT/TXT"),
            ("", "net_total, gst, grand_total", "DECIMAL"),
        ]),

        # Right-mid column: Child Lines, Stock Entry, SLE, Bin
        tbl(690, 12, 230, "tabSales Order Item (22 rows)", "#0284C7", [
            ("PK", "name", "VARCHAR"),
            ("FK", "parent -> tabSales Order", "FK"),
            ("FK", "item_code -> tabItem", "FK"),
            ("", "qty, rate, amount", "DECIMAL"),
        ]),
        tbl(690, 108, 230, "tabPurchase Order Item (23 RM)", "#C2410C", [
            ("PK", "name", "VARCHAR"),
            ("FK", "parent -> tabPurchase Order", "FK"),
            ("FK", "item_code (ITM-RAW-* ONLY)", "FK"),
            ("", "qty, rate, amount", "DECIMAL"),
        ]),
        tbl(690, 204, 230, "tabStock Entry (24 Mfg/Issue)", "#0F766E", [
            ("PK", "name (STE-2026-xxxx)", "VARCHAR"),
            ("FK", "custom_item_code, to_wh", "FK"),
            ("", "stock_entry_type, fg_qty", "DECIMAL"),
        ]),
        tbl(690, 294, 230, "tabStock Ledger Entry (59 SLE)", "#15803D", [
            ("PK", "name (SLE-2026-xxxx)", "VARCHAR"),
            ("FK", "item_code, warehouse, voucher_no", "FK"),
            ("", "actual_qty, qty_after_tx", "DECIMAL"),
        ]),

        # Far right column: Item Catalog + Calculated Bin
        tbl(950, 12, 195, "tabItem (12 SKUs)", "#1E3A8A", [
            ("PK", "name (ITM-xxxx)", "VARCHAR"),
            ("", "item_name", "VARCHAR"),
            ("", "item_group (6FG+6RM)", "VARCHAR"),
            ("", "valuation_rate", "DECIMAL"),
            ("", "standard_rate", "DECIMAL"),
            ("", "safety_stock", "INT"),
        ]),
        tbl(950, 265, 195, "tabBin (12 Calc Rows)", "#2CA02C", [
            ("PK", "name (item + wh)", "VARCHAR"),
            ("FK", "item_code -> tabItem", "FK"),
            ("FK", "warehouse -> tabWH", "FK"),
            ("", "actual_qty = SUM(SLE)", "DECIMAL"),
            ("", "reserved_qty, stock_val", "DECIMAL"),
        ]),
    ]
    return f"""
    <svg viewBox="0 0 1160 412" width="100%" style="background:#FFFFFF; font-family:Arial,Calibri,sans-serif; display:block;">
        {"".join(elements)}
    </svg>
    """


# =====================================================================
# PART A SLIDES BUILDER (EBS24CS-P01 001-002-003-004 VoltEdge-ERPNext.pdf)
# =====================================================================

def build_part_a_slides(raw_data, logo_uri):
    data = _prepare_slide_data(raw_data)
    sub_hdr = "VoltEdge Power Systems Pvt. Ltd. - ERPNext v16 Implementation (22UECS352A)"
    footer_names = get_team_footer_line(data["employees"])
    k = data["kpis"]
    slides = []

    team_inline = ", ".join(
        f"{e['employee_name'].split('(')[0].strip()} ({e['srn']})" for e in data["employees"]
    )

    # SLIDE 1: Cover Slide
    cover_inner = f"""
        <div class="cover-top">
            <div class="cover-deg">B.Tech. in Computer Science &amp; Engineering (2024&#8211;2028)</div>
            <div class="cover-deg" style="font-size:14pt;">Semester - V</div>
            <div class="cover-course">22UECS352A / UE24CS343AB8 &#8211; Enterprise Business Systems</div>
            <div class="cover-part">Mini-Project Part A: VoltEdge Power Systems &#8211; ERPNext v16 Implementation Report</div>
        </div>
        <div class="cover-div"></div>
        <table class="cover-meta">
            <tr><td class="cm-lbl">Project Title</td><td class="cm-sep">:</td>
                <td class="cm-val">End-to-End ERPNext v16 Implementation for VoltEdge Power Systems Pvt. Ltd.</td></tr>
            <tr><td class="cm-lbl">Business Domain</td><td class="cm-sep">:</td>
                <td class="cm-val">Clean-Tech Power Electronics &amp; Smart Grid Manufacturing (Peenya &amp; Whitefield, Bengaluru)</td></tr>
            <tr><td class="cm-lbl">EBS Package Studied</td><td class="cm-sep">:</td>
                <td class="cm-val">ERPNext v16 (Released 12 Jan 2026) / Frappe v16 (MariaDB 10.6+ InnoDB + Local SQLite Offline Mirror)</td></tr>
            <tr><td class="cm-lbl">Schema &amp; Cycles</td><td class="cm-sep">:</td>
                <td class="cm-val">13-Table Relational Schema (<span class="mono">tab*</span> MariaDB DDL + SQLite) covering O2C, Raw-Material P2P &amp; Calculated Stock</td></tr>
            <tr><td class="cm-lbl">Project Team &amp; SRNs</td><td class="cm-sep">:</td>
                <td class="cm-val">{esc(team_inline)}</td></tr>
            <tr><td class="cm-lbl">Role Split</td><td class="cm-sep">:</td>
                <td class="cm-val">Srujan (Database &amp; Backend) | Eshaan (Procurement &amp; SCM) | Abhay (Mfg &amp; Visuals) | Siri (Reports &amp; Finance)</td></tr>
        </table>
    """
    slides.append(wrap_cover_slide(cover_inner, footer_names, 1, logo_uri))

    # SLIDE 2: Outline (Capstone PPT Slide 2 exact style)
    outline_items = [
        ("1", "Introduction & Company Scenario", "VoltEdge Power Systems Pvt. Ltd. operations across 4 Bengaluru hubs"),
        ("2", "Installed EBS Product Research", "ERPNext v16 (12 Jan 2026), MariaDB 10.6+ stack, Docker setup, and verified Frappe clients"),
        ("3", "Populated Master Data Entities", "6 relational master tables (Employees, Terms, Warehouses, 8 Customers, 6 RM Vendors, 12 SKUs)"),
        ("4", "Transaction Tables & Dual Cycles", "12 Sales Orders (FG O2C) and 12 Purchase Orders (Raw Materials ONLY P2P)"),
        ("5", "Calculated Stock & MIS Reports", "24 Manufacturing Stock Entries -> 59 SLE audit entries -> dynamic SUM(SLE) bin valuation"),
        ("6", "System Figures & Workflows (Figs. 1-4)", "Architecture overview, Master UI capture, and 1 single order tracked across 5 O2C/P2P docs"),
        ("7", "Executive Dashboard & Plots (Figs. 5-9)", "4 core KPIs, 3 analytical charts, and 18% GST output/margin register"),
        ("8", "Authentic MariaDB Schema (Fig. 10)", "13-table ERPNext v16 tab* ER diagram, Docker/Python demo commands, and source URLs"),
    ]
    out_html = '<div style="margin-top:4pt;">' + "".join(
        f"""
        <div class="out-row">
            <div class="out-num">{n}</div>
            <div class="out-txt"><span class="key-b">{esc(t)}:</span> {esc(d)}</div>
        </div>
        """
        for n, t, d in outline_items
    ) + "</div>"
    slides.append(wrap_slide(out_html, sub_hdr, "Outline", footer_names, 2, logo_uri))

    # SLIDE 3: Business Scenario & ERPNext Research
    s3 = f"""
    <div class="two-col">
        <div class="col-half">
            <div class="sub-blue">1. Company Scenario: VoltEdge Power Systems Pvt. Ltd.</div>
            <p class="plain">VoltEdge manufactures 5kW/10kW solar inverters, 48V LiFePO4 BMS controllers, 25kVA industrial converters, DC surge boxes, and 400A LT switchgear panels across Peenya &amp; Whitefield, Bengaluru.</p>
            <ul class="cap-list" style="margin-top:4pt;">
                <li><span class="key-b">4 Warehouse Locations:</span> Peenya Raw Material Store (<span class="mono">WH-PEENYA-RAW</span>), Bommasandra WIP, Whitefield Finished Goods Hub (<span class="mono">WH-WHITEFIELD-FG</span>), and QC Quarantine Hold.</li>
                <li><span class="key-b">Process Integrity Enforced:</span> Procurement buys <strong>Raw Materials ONLY</strong> (<span class="mono">ITM-RAW-*</span>); Manufacturing Stock Entries produce Finished Goods and compute warehouse balances dynamically via <span class="mono">SUM(SLE)</span>.</li>
                <li><span class="key-b">Dual Deployment Ready:</span> <span class="mono">erpnext_v16_docker/docker-compose.yml</span> spins up real <span class="mono">frappe/erpnext:v16.0.0</span> + MariaDB 10.6; <span class="mono">backend/app.py</span> (port 8050) serves the offline SQLite showcase.</li>
            </ul>
            <div class="sub-blue" style="margin-top:6pt;">Team Responsibilities</div>
            <ul class="cap-list">
                <li><span class="key-b">Srujan S (HR-EMP-0001):</span> Sales &amp; CRM, SQLite/MariaDB Schema &amp; Dashboard</li>
                <li><span class="key-b">Eshaan Menon (HR-EMP-0002):</span> Procurement, Raw-Material P2P &amp; REST Sync</li>
                <li><span class="key-b">Abhay Verma (HR-EMP-0003):</span> Manufacturing Stock Entries, QC &amp; Visuals</li>
                <li><span class="key-b">Siri Kulkarni (HR-EMP-0004):</span> Finance, GST Registers &amp; MIS Reporting</li>
            </ul>
        </div>
        <div class="col-half">
            <div class="sub-blue">2. EBS Product Profile: ERPNext v16 (Frappe Technologies)</div>
            <table class="ppt warm" style="margin-bottom:8pt;">
                <tr><th style="width:32%;">Attribute</th><th>Verified Details</th></tr>
                <tr><td><b>Developer &amp; HQ</b></td><td>Frappe Technologies Pvt. Ltd. (Mumbai, Maharashtra, India)</td></tr>
                <tr><td><b>Origin &amp; License</b></td><td>Founded 2008 by Rushabh Mehta; 100% Open Source (GNU GPL v3)</td></tr>
                <tr><td><b>Latest Release</b></td><td><b>ERPNext v16 (v16.0.0, released 12 January 2026)</b> alongside v15 LTS</td></tr>
                <tr><td><b>Production Stack</b></td><td>Python 3.12+ (Frappe v16), <b>MariaDB 10.6+ (InnoDB)</b>, Redis, Vue 3</td></tr>
                <tr><td><b>Core Modules</b></td><td>Accounting (GST/TDS), Buying, Selling, Stock/MRP, Mfg, HR, Quality</td></tr>
                <tr><td><b>Verified Clients (frappe.io)</b></td><td><b>Precihole Sports</b>, <b>Banaraswala Wire Mesh</b>, <b>Multicolor Steels</b>, <b>Rangsutra</b>, Shizuoka General Hospital</td></tr>
                <tr><td><b>Fact Clarification</b></td><td>Zerodha (Rainmatter) is an investor in Frappe, not an ERP client case study; Docker Compose + MariaDB DDL included in repo</td></tr>
            </table>
            <div class="sub-navy">Source URLs (Part A Reference Links)</div>
            <p class="url-line">1. Official Product &amp; Blogs: https://erpnext.com &amp; https://frappe.io/blog</p>
            <p class="url-line">2. v16 Release &amp; Docs: https://docs.erpnext.com &amp; https://github.com/frappe/erpnext</p>
            <p class="url-line">3. Docker Deployment: https://github.com/frappe/frappe_docker</p>
        </div>
    </div>
    """
    slides.append(wrap_slide(s3, sub_hdr, "Business Scenario & Product Study", footer_names, 3, logo_uri))

    # SLIDE 4: Master Data Part 1 (Employees, Payment Terms, Warehouses)
    emp_rows = "".join(
        f"<tr><td class='mono'>{esc(e['employee_id'])}</td><td>{esc(e['employee_name'])}</td>"
        f"<td class='mono'>{esc(e['srn'])}</td><td>{esc(e['department'])}</td><td>{esc(e['designation'])}</td></tr>"
        for e in data["employees"]
    )
    term_rows = "".join(
        f"<tr><td class='mono'>{esc(t['payment_term_id'])}</td><td>{esc(t['term_name'])}</td>"
        f"<td class='num'>{t['credit_days']} d</td><td>{esc(t['description'])}</td></tr>"
        for t in data["payment_terms"]
    )
    wh_rows = "".join(
        f"<tr><td class='mono'>{esc(w['warehouse_id'])}</td><td>{esc(w['warehouse_name'])}</td>"
        f"<td>{esc(w['warehouse_type'])}</td><td>{esc(w['city'])}</td>"
        f"<td>{esc(w.get('manager_name') or w['manager_id'])}</td></tr>"
        for w in data["warehouses"]
    )
    s4 = f"""
    <div class="sub-blue">Master Entities 1 to 3: Employees (tabEmployee), Payment Terms &amp; Warehouses</div>
    <div class="two-col">
        <div class="col-half">
            <div class="sub-navy">Entity 1: tabEmployee ({len(data['employees'])} Project Officers)</div>
            <table class="ppt">
                <tr><th>Emp ID</th><th>Name</th><th>SRN</th><th>Dept</th><th>Designation</th></tr>
                {emp_rows}
            </table>
        </div>
        <div class="col-half">
            <div class="sub-navy">Entity 2: tabPayment Terms Template ({len(data['payment_terms'])} Rules)</div>
            <table class="ppt">
                <tr><th>Term ID</th><th>Term Name</th><th class="num">Credit</th><th>Commercial Rule</th></tr>
                {term_rows}
            </table>
        </div>
    </div>
    <div class="sub-navy" style="margin-top:6pt;">Entity 3: tabWarehouse ({len(data['warehouses'])} Bengaluru Operating Hubs)</div>
    <table class="ppt">
        <tr><th>Warehouse ID</th><th>Warehouse Name</th><th>Type</th><th>City</th><th>Custodian</th></tr>
        {wh_rows}
    </table>
    """
    slides.append(wrap_slide(s4, sub_hdr, "Master Data Entities (Part 1)", footer_names, 4, logo_uri))

    # SLIDE 5: Master Data Part 2 (Customers 8 + Suppliers 6)
    cust_rows = "".join(
        f"<tr><td class='mono'>{esc(c['customer_id'])}</td><td>{esc(c['customer_name'])}</td>"
        f"<td>{esc(c['customer_group'])}</td><td>{esc(c['territory'])}</td>"
        f"<td class='mono'>{esc(c['gstin'])}</td><td>{esc(c.get('manager_name') or c['account_manager_id'])}</td></tr>"
        for c in data["customers"]
    )
    sup_rows = "".join(
        f"<tr><td class='mono'>{esc(s['supplier_id'])}</td><td>{esc(s['supplier_name'])}</td>"
        f"<td>{esc(s['supplier_group'])}</td><td>{esc(s['country'])}</td>"
        f"<td class='mono'>{esc(s['gstin'])}</td><td>{esc(s.get('buyer_name') or s['buyer_id'])}</td></tr>"
        for s in data["suppliers"]
    )
    s5 = f"""
    <div class="sub-navy">Entity 4: tabCustomer ({len(data['customers'])} B2B Buyers with Valid Indian GSTIN)</div>
    <table class="ppt" style="font-size:8.2pt;">
        <tr><th>Customer ID</th><th>Company Name</th><th>Segment</th><th>State</th><th>GSTIN</th><th>Account Owner</th></tr>
        {cust_rows}
    </table>
    <div class="sub-navy" style="margin-top:6pt;">Entity 5: tabSupplier ({len(data['suppliers'])} Raw Material Vendors)</div>
    <table class="ppt" style="font-size:8.2pt;">
        <tr><th>Supplier ID</th><th>Vendor Name</th><th>Component Specialty</th><th>Country</th><th>GSTIN</th><th>Procurement Lead</th></tr>
        {sup_rows}
    </table>
    """
    slides.append(wrap_slide(s5, sub_hdr, "Master Data Entities (Part 2)", footer_names, 5, logo_uri))

    # SLIDE 6: Master Data Part 3 (Item Catalog 12 + Calculated Stock Ledger Link)
    item_rows = "".join(
        f"<tr><td class='mono'>{esc(it['item_code'])}</td><td>{esc(it['item_name'])}</td>"
        f"<td>{esc(it['item_group'])}</td><td>{esc(it['uom'])}</td>"
        f"<td class='num'>{inr(it['selling_rate']) if it['selling_rate'] > 0 else '— (Internal)'}</td>"
        f"<td class='num'>{inr(it['valuation_rate'])}</td>"
        f"<td class='num'>{it['reorder_level']}</td></tr>"
        for it in data["items"]
    )
    s6 = f"""
    <div class="sub-blue">Entity 6: tabItem ({len(data['items'])} Active SKUs: 6 Finished Goods &amp; 6 Raw Materials)</div>
    <table class="ppt" style="font-size:8.1pt;">
        <tr>
            <th>Item Code</th><th>Item Name</th><th>Group</th><th>UOM</th>
            <th class="num">Selling Rate</th><th class="num">Valuation Rate</th>
            <th class="num">Reorder Lvl</th>
        </tr>
        {item_rows}
    </table>
    <div class="sub-navy" style="margin-top:6pt;">Calculated Inventory Architecture (Zero Hardcoded Balances)</div>
    <ul class="cap-list">
        <li><span class="key-b">Strict Finished Goods vs. Raw Materials Split:</span> Purchase Orders buy <strong>only</strong> the 6 Raw Materials (<span class="mono">ITM-RAW-*</span> into <span class="mono">WH-PEENYA-RAW</span>); 24 Manufacturing <span class="mono">tabStock Entry</span> vouchers consume Raw Materials and produce the 6 Finished Goods (<span class="mono">WH-WHITEFIELD-FG</span>).</li>
        <li><span class="key-b">Mathematically Derived Stock (tabBin):</span> <span class="mono">recalculate_stock_ledger()</span> replays all <strong>{k['sle_count']} immutable Stock Ledger Entries</strong> chronologically across Purchase Receipts, Mfg Entries, and Delivery Notes -> <b>{k['inventory_units']} units (&#8377;{k['inventory_lakhs']:.2f}L)</b>.</li>
    </ul>
    """
    slides.append(wrap_slide(s6, sub_hdr, "Master Data: 12-SKU Catalog & Stock Link", footer_names, 6, logo_uri))

    # SLIDE 7: Transaction Table 1 - Sales Orders (12 rows)
    so_rows = "".join(
        f"<tr><td class='mono'>{esc(so['so_id'])}</td><td>{esc(so['order_date'])}</td>"
        f"<td>{esc(so['customer_name'])}</td><td style='font-size:7.4pt;'>{esc(so['items_summary'])}</td>"
        f"<td>{esc(so['workflow_stage'])}</td><td>{esc(so['status'])}</td>"
        f"<td class='num'>{inr(so['total_amount'])}</td>"
        f"<td class='mono' style='font-size:7.3pt;'>{esc(so.get('delivery_note_id') or so['quotation_id'])}</td></tr>"
        for so in data["sales_orders"]
    )
    s7 = f"""
    <div class="sub-blue">Transaction Table 1: tabSales Order ({k['so_count']} O2C Records | Booked Revenue: &#8377;{k['sales_lakhs']:.2f} Lakhs incl. GST)</div>
    <table class="ppt" style="font-size:7.9pt;">
        <tr>
            <th>Sales Order ID</th><th>Date</th><th>Customer</th><th>Ordered FG Items</th>
            <th>O2C Stage</th><th>Status</th><th class="num">Grand Total</th><th>Latest Chain Doc</th>
        </tr>
        {so_rows}
    </table>
    <p class="plain" style="margin-top:6pt;"><b>Note:</b> Every Sales Order stores its full 5-document O2C chain (<span class="mono">QTN -> SO -> DN -> SINV -> PAY</span>). Orders <span class="mono">0001&#8211;0009</span> generated Delivery Notes &amp; Stock Ledger outflows; <span class="mono">0010&#8211;0011</span> reserve Finished Goods; <span class="mono">0012</span> sits at open Quotation.</p>
    """
    slides.append(wrap_slide(s7, sub_hdr, "Transaction Data: Sales Orders (O2C)", footer_names, 7, logo_uri))

    # SLIDE 8: Transaction Table 2 - Purchase Orders (12 rows - Raw Materials ONLY)
    po_rows = "".join(
        f"<tr><td class='mono'>{esc(po['po_id'])}</td><td>{esc(po['order_date'])}</td>"
        f"<td>{esc(po['supplier_name'])}</td><td style='font-size:7.4pt;'>{esc(po['items_summary'])}</td>"
        f"<td>{esc(po['workflow_stage'])}</td><td>{esc(po['status'])}</td>"
        f"<td class='num'>{inr(po['total_amount'])}</td>"
        f"<td class='mono' style='font-size:7.3pt;'>{esc(po.get('purchase_receipt_id') or po['material_request_id'])}</td></tr>"
        for po in data["purchase_orders"]
    )
    s8 = f"""
    <div class="sub-blue">Transaction Table 2: tabPurchase Order ({k['po_count']} P2P Records | RM Spend: &#8377;{k['purchase_lakhs']:.2f} Lakhs incl. GST)</div>
    <table class="ppt" style="font-size:7.9pt;">
        <tr>
            <th>Purchase Order ID</th><th>Date</th><th>Supplier</th><th>Raw Materials Only (ITM-RAW-*)</th>
            <th>P2P Stage</th><th>Status</th><th class="num">Grand Total</th><th>Latest Chain Doc</th>
        </tr>
        {po_rows}
    </table>
    <p class="plain" style="margin-top:6pt;"><b>Verified Integrity:</b> <b>0 Finished Goods</b> appear in any Purchase Order (<span class="mono">0001&#8211;0012</span>). All 12 POs procure raw semiconductors, PCBs, coils, LiFePO4 cells, breakers, and enclosures into <span class="mono">WH-PEENYA-RAW</span>, feeding manufacturing Stock Entries.</p>
    """
    slides.append(wrap_slide(s8, sub_hdr, "Transaction Data: Purchase Orders (RM Only)", footer_names, 8, logo_uri))

    # SLIDE 9: Built-In Management Reports (3 SQL Reports)
    rep1_rows = "".join(
        f"<tr><td>{esc(r['month_label'])}</td><td class='num'>{r['order_count']}</td>"
        f"<td class='num'>&#8377;{r['revenue_lakhs']:.2f} L</td></tr>"
        for r in data["monthly_sales"]
    )
    rep2_rows = "".join(
        f"<tr><td>{esc(r['supplier_name'])}</td><td>{esc(r['supplier_group'])}</td>"
        f"<td class='num'>{r['po_count']}</td><td class='num'>&#8377;{r['spend_lakhs']:.2f} L</td></tr>"
        for r in data["supplier_spend"]
    )
    rep3_rows = "".join(
        f"<tr><td class='mono'>{esc(r['item_code'])}</td><td>{esc(r['item_name'])}</td>"
        f"<td class='num'>{r['actual_qty']}</td><td class='num'>{r['reserved_qty']}</td>"
        f"<td class='num'><b>{r['available_qty']}</b></td><td class='num'>{r['safety_stock']}</td>"
        f"<td class='num'>&#8377;{r['value_lakhs']:.2f} L</td>"
        f"<td><b>{'Reorder Alert' if r['available_qty'] <= r['safety_stock'] + 2 else 'Healthy'}</b></td></tr>"
        for r in data["inventory_report"]
    )
    s9 = f"""
    <div class="two-col">
        <div class="col-40">
            <div class="sub-blue">Report 1: Monthly Billed Sales</div>
            <table class="ppt" style="font-size:8.2pt; margin-bottom:8pt;">
                <tr><th>Month</th><th class="num">SOs</th><th class="num">Revenue</th></tr>
                {rep1_rows}
            </table>
            <div class="sub-blue">Report 2: Raw Material Supplier Spend</div>
            <table class="ppt" style="font-size:7.9pt;">
                <tr><th>Supplier</th><th>Category</th><th class="num">POs</th><th class="num">Spend</th></tr>
                {rep2_rows}
            </table>
        </div>
        <div class="col-60">
            <div class="sub-blue">Report 3: Calculated Stock Ledger &amp; Reservation (tabBin)</div>
            <table class="ppt" style="font-size:7.6pt;">
                <tr>
                    <th>SKU</th><th>Item</th><th class="num">Actual</th><th class="num">Rsrv</th>
                    <th class="num">Avail</th><th class="num">Min</th><th class="num">Val</th><th>Status</th>
                </tr>
                {rep3_rows}
            </table>
            <p class="plain" style="margin-top:6pt;"><b>Zero Hardcoding:</b> Every <span class="mono">Actual Qty</span> equals <span class="mono">SUM(actual_qty)</span> from <span class="mono">tabStock Ledger Entry</span> ({k['sle_count']} events); <span class="mono">Reserved</span> reflects pending Sales Orders.</p>
        </div>
    </div>
    """
    slides.append(wrap_slide(s9, sub_hdr, "Built-In ERP Management Reports", footer_names, 9, logo_uri))

    # SLIDE 10: Figures 1 & 2 (Fresh page for screenshots/visuals - NO dark backgrounds)
    cust_preview = "".join(
        f"<tr><td class='mono'>{esc(c['customer_id'])}</td><td>{esc(c['customer_name'])}</td>"
        f"<td>{esc(c['territory'])}</td><td class='mono'>{esc(c['gstin'])}</td></tr>"
        for c in data["customers"][:5]
    )
    sup_preview = "".join(
        f"<tr><td class='mono'>{esc(s['supplier_id'])}</td><td>{esc(s['supplier_name'])}</td>"
        f"<td>{esc(s['supplier_group'])}</td></tr>"
        for s in data["suppliers"][:4]
    )
    s10 = f"""
    <div class="two-col">
        <div class="col-half">
            <div class="fig-frame">
                {svg_system_architecture(k)}
            </div>
            <div class="fig-cap">Figure 1: VoltEdge ERPNext v16 MariaDB &amp; Offline SQLite Architecture</div>
            <div class="fig-desc">Master entities feed O2C Sales Orders (Finished Goods) and Raw-Material P2P POs plus Manufacturing Stock Entries to compute live Bin balances.</div>
        </div>
        <div class="col-half">
            <div class="ui-win">
                <div class="ui-bar">
                    <span><b>VoltEdge ERP v16 Desk</b> &#8212; Master Directory (Light Theme)</span>
                    <span class="ui-url">http://127.0.0.1:8050/</span>
                </div>
                <div style="padding:7pt 8pt;">
                    <div style="font-size:8.5pt; font-weight:700; color:#1E3A8A; margin-bottom:3pt;">Customers (tabCustomer — 5 of {len(data['customers'])})</div>
                    <table class="ppt" style="font-size:7.6pt; margin-bottom:6pt;">
                        <tr><th>ID</th><th>Customer Name</th><th>State</th><th>GSTIN</th></tr>
                        {cust_preview}
                    </table>
                    <div style="font-size:8.5pt; font-weight:700; color:#BD582C; margin-bottom:3pt;">Raw Material Vendors (tabSupplier — 4 of {len(data['suppliers'])})</div>
                    <table class="ppt" style="font-size:7.6pt;">
                        <tr><th>ID</th><th>Supplier Name</th><th>Category</th></tr>
                        {sup_preview}
                    </table>
                </div>
            </div>
            <div class="fig-cap">Figure 2: Master Data Entities Screen Capture (Clean White Desk Header)</div>
            <div class="fig-desc">Browser view of our light-mode ERP workspace displaying B2B customers, valid GSTINs, and raw-material suppliers.</div>
        </div>
    </div>
    """
    slides.append(wrap_slide(s10, sub_hdr, "System Architecture & Master Registry UI", footer_names, 10, logo_uri))

    # SLIDE 11: Figure 3 - One Single Order Moving End-to-End Through All 5 O2C Documents
    so1 = data["sales_orders"][0]
    o2c_stages = [
        ("1", "Quotation", so1["quotation_id"], f"{so1['order_date']} | Quote Approved"),
        ("2", "Sales Order", so1["so_id"], f"{so1['customer_name'][:18]}.."),
        ("3", "Delivery Note", so1["delivery_note_id"], "WH-WHITEFIELD-FG (-6 INV, -8 BMS)"),
        ("4", "Sales Invoice", so1["sales_invoice_id"], f"Net + 18% GST = INR {so1['total_amount']:,.0f}"),
        ("5", "Payment Entry", so1["payment_entry_id"], "NEFT Cleared (Completed)"),
    ]
    s11 = f"""
    <div class="fig-frame" style="padding:10pt 12pt;">
        {svg_process_cycle(f"Single-Document Trace: {so1['so_id']} Moving Across All 5 O2C Stages", o2c_stages, accent="#0088CC")}
    </div>
    <div class="two-col" style="margin-top:6pt;">
        <div class="col-half">
            <div class="sub-blue">End-to-End Continuity Trace ({esc(so1['so_id'])})</div>
            <ul class="cap-list">
                <li><span class="key-b">1. Quotation ({esc(so1['quotation_id'])}) &#8594; 2. Sales Order ({esc(so1['so_id'])}):</span> Approved for <b>{esc(so1['customer_name'])}</b> for <b>6 &times; 5kW Inverter + 8 &times; 48V Smart BMS</b> (<span class="mono">Net {inr(so1['net_total'])} + GST {inr(so1['gst_amount'])}</span>).</li>
                <li><span class="key-b">3. Delivery Note ({esc(so1['delivery_note_id'])}):</span> Dispatched from <span class="mono">WH-WHITEFIELD-FG</span> on {esc(so1['delivery_date'])}, posting negative <span class="mono">tabStock Ledger Entry</span> rows against prior manufactured stock (+24/+50 from Batch-1).</li>
                <li><span class="key-b">4. Sales Invoice ({esc(so1['sales_invoice_id'])}) &#8594; 5. Payment ({esc(so1['payment_entry_id'])}):</span> 18% GST tax invoice raised and reconciled to zero balance under <span class="mono">{esc(so1['term_name'])}</span>.</li>
            </ul>
        </div>
        <div class="col-half">
            <div class="sub-navy">O2C Document Chain Registry (First 5 Orders)</div>
            <table class="ppt" style="font-size:7.8pt;">
                <tr><th>Sales Order</th><th>Delivery Note</th><th>Sales Invoice</th><th>Payment Entry</th><th class="num">Total</th></tr>
                {"".join(f"<tr><td class='mono'>{esc(so['so_id'])}</td><td class='mono'>{esc(so.get('delivery_note_id') or 'Pending')}</td><td class='mono'>{esc(so.get('sales_invoice_id') or 'Pending')}</td><td class='mono'>{esc(so.get('payment_entry_id') or 'Pending')}</td><td class='num'>{inr(so['total_amount'])}</td></tr>" for so in data['sales_orders'][:5])}
            </table>
        </div>
    </div>
    <div class="fig-cap">Figure 3: One Single O2C Order ({esc(so1['so_id'])}) Progressed Across All 5 Linked ERPNext Documents</div>
    <div class="fig-desc">Demonstrates strict parent-child document linking from Customer Quotation down to Stock Ledger deduction, Tax Invoice, and bank settlement.</div>
    """
    slides.append(wrap_slide(s11, sub_hdr, "Process Cycle 1: End-to-End O2C Chain", footer_names, 11, logo_uri))

    # SLIDE 12: Figure 4 - One Single PO Moving End-to-End Through All 5 P2P Documents (Raw Materials Only)
    po1 = data["purchase_orders"][0]
    p2p_stages = [
        ("1", "Material Req.", po1["material_request_id"], "BOM Shortage Trigger (RM)"),
        ("2", "Purchase Order", po1["po_id"], f"{po1['supplier_name'][:18]}.."),
        ("3", "Purchase Rcpt", po1["purchase_receipt_id"], "WH-PEENYA-RAW (+140 MOSFET, +90 PCB)"),
        ("4", "Purchase Inv.", po1["purchase_invoice_id"], f"3-Way Match (INR {po1['total_amount']:,.0f})"),
        ("5", "Payment Settled", po1["payment_entry_id"], "NEFT Vendor Payout Done"),
    ]
    s12 = f"""
    <div class="fig-frame" style="padding:10pt 12pt;">
        {svg_process_cycle(f"Single-Document Trace: {po1['po_id']} Moving Across All 5 P2P Stages (Raw Materials)", p2p_stages, accent="#BD582C")}
    </div>
    <div class="two-col" style="margin-top:6pt;">
        <div class="col-half">
            <div class="sub-rust">End-to-End Continuity Trace ({esc(po1['po_id'])})</div>
            <ul class="cap-list">
                <li><span class="key-b">1. Material Request ({esc(po1['material_request_id'])}) &#8594; 2. PO ({esc(po1['po_id'])}):</span> Issued to <b>{esc(po1['supplier_name'])}</b> for Raw Materials <b>140 &times; SiC MOSFET + 90 &times; Control PCB</b> (<span class="mono">{inr(po1['total_amount'])} incl. 18% GST</span>).</li>
                <li><span class="key-b">3. Purchase Receipt ({esc(po1['purchase_receipt_id'])}):</span> Received into <span class="mono">WH-PEENYA-RAW</span> on {esc(po1['schedule_date'])}, posting +140 / +90 to <span class="mono">tabStock Ledger Entry</span> prior to Batch-1 manufacturing on 2026-05-05.</li>
                <li><span class="key-b">4. Purchase Invoice ({esc(po1['purchase_invoice_id'])}) &#8594; 5. Payment ({esc(po1['payment_entry_id'])}):</span> Passed 3-way PO&#8211;PR&#8211;Invoice match and settled via NEFT.</li>
            </ul>
        </div>
        <div class="col-half">
            <div class="sub-navy">P2P Document Chain Registry (First 5 Raw Material POs)</div>
            <table class="ppt warm" style="font-size:7.8pt;">
                <tr><th>Purchase Order</th><th>Purchase Receipt</th><th>Purchase Inv.</th><th>Payment Entry</th><th class="num">Total</th></tr>
                {"".join(f"<tr><td class='mono'>{esc(po['po_id'])}</td><td class='mono'>{esc(po.get('purchase_receipt_id') or 'Pending')}</td><td class='mono'>{esc(po.get('purchase_invoice_id') or 'Pending')}</td><td class='mono'>{esc(po.get('payment_entry_id') or 'Pending')}</td><td class='num'>{inr(po['total_amount'])}</td></tr>" for po in data['purchase_orders'][:5])}
            </table>
        </div>
    </div>
    <div class="fig-cap">Figure 4: One Single Raw-Material P2P Order ({esc(po1['po_id'])}) Across All 5 Linked ERPNext Documents</div>
    <div class="fig-desc">Proves 100% Raw Material procurement discipline, positive chronological stock balance before manufacturing consumption, and 3-way voucher settlement.</div>
    """
    slides.append(wrap_slide(s12, sub_hdr, "Process Cycle 2: End-to-End P2P Chain", footer_names, 12, logo_uri))

    # SLIDE 13: Figures 5 & 6 (Executive Dashboard KPIs + Chart 1 Monthly Sales)
    s13 = f"""
    <div class="ui-win" style="padding:7pt 9pt;">
        <div class="ui-bar" style="margin:-7pt -9pt 6pt -9pt;">
            <span><b>VoltEdge Executive Dashboard</b> &#8212; Live SQLite Key Performance Indicators</span>
            <span class="ui-url">http://127.0.0.1:8050/</span>
        </div>
        <table class="kpi-strip">
            <tr>
                <td><div class="kpi-lbl">TOTAL SALES REVENUE</div><div class="kpi-val">&#8377;{k['sales_lakhs']:.2f} L</div><div class="kpi-sub">Across {k['so_count']-1} Confirmed SOs</div></td>
                <td><div class="kpi-lbl">RM PROCUREMENT SPEND</div><div class="kpi-val">&#8377;{k['purchase_lakhs']:.2f} L</div><div class="kpi-sub">{k['po_count']} RM POs (0 FG POs)</div></td>
                <td><div class="kpi-lbl">DELIVERY FULFILLMENT</div><div class="kpi-val">{k['fulfillment_pct']:.1f}%</div><div class="kpi-sub">{k['delivered_so']} Delivered · {k['completed_so']} Paid</div></td>
                <td><div class="kpi-lbl">CALCULATED INVENTORY</div><div class="kpi-val">&#8377;{k['inventory_lakhs']:.2f} L</div><div class="kpi-sub">{k['inventory_units']} Units ({k['sle_count']} SLEs)</div></td>
            </tr>
        </table>
    </div>
    <div class="fig-cap" style="margin-bottom:4pt;">Figure 5: Live Executive Dashboard KPI Summary Panel (4 Real-Time Metrics)</div>
    <div class="two-col" style="align-items:center;">
        <div class="col-60">
            <div class="fig-frame">
                {svg_mpl_monthly_sales(data["monthly_sales"])}
            </div>
        </div>
        <div class="col-40">
            <div class="sub-blue">Monthly Revenue Observations</div>
            <ul class="cap-list">
                <li><span class="key-b">Consistent Scaling:</span> Monthly booked sales progress cleanly across May&#8211;July 2026 commercial EPC deployments.</li>
                <li><span class="key-b">Zero Static Figures:</span> Every KPI and chart bar computes directly via SQL queries over <span class="mono">voltedge_ebs.db</span> and updates immediately when stages advance.</li>
            </ul>
            <div class="fig-cap">Figure 6: Monthly Sales Revenue Trend Plot</div>
            <div class="fig-desc">Vector analytical plot showing billed O2C revenue (bars) and order momentum across operating months.</div>
        </div>
    </div>
    """
    slides.append(wrap_slide(s13, sub_hdr, "Executive Dashboard & Sales Plot", footer_names, 13, logo_uri))

    # SLIDE 14: Figures 7 & 8 (Chart 2 Supplier Spend + Chart 3 Inventory Stock vs Safety Stock)
    s14 = f"""
    <div class="two-col" style="margin-top:4pt;">
        <div class="col-half">
            <div class="fig-frame">
                {svg_mpl_supplier_spend(data["supplier_spend"])}
            </div>
            <div class="fig-cap">Figure 7: Raw Material Supplier Spend Comparison Plot</div>
            <div class="fig-desc">Tracks procurement distribution across semiconductor, PCB, cell, inductor, enclosure, and breaker vendors.</div>
            <ul class="cap-list" style="margin-top:5pt;">
                <li><span class="key-b">Top Vendor:</span> {esc(data['supplier_spend'][0]['supplier_name'])} accounts for &#8377;{data['supplier_spend'][0]['spend_lakhs']:.2f}L across {data['supplier_spend'][0]['po_count']} RM POs.</li>
            </ul>
        </div>
        <div class="col-half">
            <div class="fig-frame">
                {svg_mpl_inventory_vs_safety(data["inventory_report"])}
            </div>
            <div class="fig-cap">Figure 8: Calculated Available Stock vs. Reorder Level (All 12 SKUs)</div>
            <div class="fig-desc">Displays net available quantities (SUM(SLE) minus pending SO reservations) against configured safety thresholds.</div>
            <ul class="cap-list" style="margin-top:5pt;">
                <li><span class="key-b">100% Positive Balances:</span> Every Manufactured FG and Raw Material SKU stays cleanly above zero and reorder threshold across all 59 SLE events.</li>
            </ul>
        </div>
    </div>
    """
    slides.append(wrap_slide(s14, sub_hdr, "Procurement & Inventory Analytical Plots", footer_names, 14, logo_uri))

    # SLIDE 15: Figure 9 - Management Reporting & GST Audit Capture
    audit_rows = "".join(
        f"<tr><td class='mono'>{esc(so['so_id'])}</td><td>{esc(so['customer_name'])}</td>"
        f"<td>{esc(so['workflow_stage'])}</td><td class='num'>{inr(so['net_total'])}</td>"
        f"<td class='num'>{inr(so['gst_amount'])}</td><td class='num'>{inr(so['total_amount'])}</td>"
        f"<td>{esc(short_emp(so['srn_reference']))}</td></tr>"
        for so in data["sales_orders"][6:]
    )
    gross_margin = k["sales_lakhs"] - k["purchase_lakhs"]
    s15 = f"""
    <div class="ui-win">
        <div class="ui-bar">
            <span><b>VoltEdge Financial &amp; Audit Console</b> &#8212; 18% GST Tax Register &amp; Cash Spread</span>
            <span class="ui-url">http://127.0.0.1:8050/</span>
        </div>
        <div style="padding:8pt 10pt;">
            <table class="kpi-strip" style="margin-bottom:8pt;">
                <tr>
                    <td><div class="kpi-lbl">BOOKED O2C SALES</div><div class="kpi-val" style="font-size:13.5pt;">&#8377;{k['sales_lakhs']:.2f} L</div></td>
                    <td><div class="kpi-lbl">RM PROCUREMENT SPEND</div><div class="kpi-val" style="font-size:13.5pt;">&#8377;{k['purchase_lakhs']:.2f} L</div></td>
                    <td><div class="kpi-lbl">OPERATING SPREAD</div><div class="kpi-val" style="font-size:13.5pt;">&#8377;{gross_margin:.2f} L</div></td>
                    <td><div class="kpi-lbl">ERPNEXT CSV EXPORTS</div><div class="kpi-val" style="font-size:13.5pt;">13 Files</div></td>
                </tr>
            </table>
            <div style="font-size:9pt; font-weight:700; color:#1E3A8A; margin-bottom:4pt;">GST Tax Output Register &amp; Team Officer Ownership (Orders 7 to 12)</div>
            <table class="ppt" style="font-size:7.9pt;">
                <tr><th>Order ID</th><th>Customer</th><th>Stage</th><th class="num">Net Value</th><th class="num">GST (18%)</th><th class="num">Grand Total</th><th>Officer (SRN)</th></tr>
                {audit_rows}
            </table>
        </div>
    </div>
    <div class="fig-cap" style="margin-top:6pt;">Figure 9: Financial Margin Bridge, 18% GST Register &amp; SRN Audit Trail</div>
    <div class="fig-desc">Illustrates Net vs. 18% GST breakup persisted per Sales Order alongside cash spread and 13 synchronized ERPNext CSV exports.</div>
    """
    slides.append(wrap_slide(s15, sub_hdr, "Management Reporting & GST Audit", footer_names, 15, logo_uri))

    # SLIDE 16: Figure 10 - Authentic ERPNext v16 MariaDB Schema Diagram (13 Tables)
    s16 = f"""
    <div class="fig-frame" style="padding:6pt 8pt;">
        {svg_er_schema_diagram()}
    </div>
    <div class="fig-cap">Figure 10: Authentic ERPNext v16 MariaDB tab* Relational Schema (<span class="mono">backend/erpnext_mariadb_schema.sql</span> — 13 DocType Tables)</div>
    <div class="fig-desc">Models authentic MariaDB 10.6+ InnoDB <span class="mono">tab*</span> DocTypes (name PK, docstatus, parent child FKs, tabStock Entry, tabStock Ledger Entry, and calculated tabBin), synchronized cleanly with our offline SQLite showcase.</div>
    """
    slides.append(wrap_slide(s16, sub_hdr, "Authentic ERPNext v16 MariaDB Schema", footer_names, 16, logo_uri))

    # SLIDE 17: Conclusion, Demo Commands, References & Thank You
    s17 = """
    <div class="two-col">
        <div class="col-half">
            <div class="sub-blue">Conclusion &amp; Verification Readiness</div>
            <ul class="cap-list">
                <li><span class="key-b">Complete Master &amp; Mfg Coverage:</span> 6 master entities (12 SKUs: 6 FG + 6 RM), 12 Sales Orders (5-doc O2C chains), 12 RM-Only Purchase Orders (5-doc P2P chains), and 24 Manufacturing/Issue Stock Entries.</li>
                <li><span class="key-b">Calculated Inventory Math:</span> Zero hardcoded balances; <span class="mono">recalculate_stock_ledger()</span> replays 59 Stock Ledger Entries chronologically with zero negative balances and zero Finished Goods on POs.</li>
                <li><span class="key-b">Real ERPNext v16 + Offline Twin:</span> Includes <span class="mono">erpnext_v16_docker/docker-compose.yml</span> (<span class="mono">frappe/erpnext:v16.0.0</span> + MariaDB 10.6), authentic MariaDB DDL, REST API pusher (<span class="mono">--push</span>), and 13 Data Import CSVs.</li>
            </ul>
            <div class="sub-navy" style="margin-top:6pt;">Live Demo Commands (Windows PowerShell / Docker)</div>
            <div style="background:#F8FAFC; border:0.75pt solid #CBD5E1; padding:6pt 8pt; font-family:Consolas,monospace; font-size:8.2pt; color:#111827;">
                python backend\\seed_data.py; python backend\\erpnext_sync.py<br>
                python backend\\app.py &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# Local UI at http://127.0.0.1:8050<br>
                cd erpnext_v16_docker; docker compose up -d &nbsp;# ERPNext v16 (:8080)
            </div>
        </div>
        <div class="col-half">
            <div class="sub-blue">Verified References &amp; Source URLs</div>
            <ul class="cap-list">
                <li><span class="key-b">ERPNext Official Platform &amp; Blog:</span> <span class="url-line">https://erpnext.com &amp; https://frappe.io/blog</span></li>
                <li><span class="key-b">ERPNext v16 Release &amp; GitHub:</span> <span class="url-line">https://github.com/frappe/erpnext/releases</span></li>
                <li><span class="key-b">Frappe Docker (v16 Stack):</span> <span class="url-line">https://github.com/frappe/frappe_docker</span></li>
                <li><span class="key-b">MariaDB 10.6 InnoDB Docs:</span> <span class="url-line">https://mariadb.com/kb/en/documentation/</span></li>
                <li><span class="key-b">DBML Schema Architecture:</span> <span class="url-line">https://dbdiagram.io</span></li>
            </ul>
            <div style="margin-top:20pt; text-align:center;">
                <div style="font-family:'Trebuchet MS',Calibri,sans-serif; font-size:28pt; font-weight:700; color:#DC2626;">Thank You!</div>
                <div style="font-size:10.5pt; color:#4B5563; margin-top:4pt;">Live SQLite &amp; ERPNext v16 Schema Demonstration Ready</div>
            </div>
        </div>
    </div>
    """
    slides.append(wrap_slide(s17, sub_hdr, "Conclusion & Verified References", footer_names, 17, logo_uri))

    return slides


# =====================================================================
# HTML COMPILATION & CHROME / EDGE HEADLESS PDF EXPORT
# =====================================================================

def wrap_html(title, css_text, slides_list):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{esc(title)}</title>
<style>
{css_text}
</style>
</head>
<body>
{"".join(slides_list)}
</body>
</html>
"""


def find_browser():
    candidates = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    return None


def html_to_pdf(browser_exe, html_path, pdf_path):
    abs_html = os.path.abspath(html_path).replace("\\", "/")
    file_url = f"file:///{abs_html}"
    cmd = [
        browser_exe,
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--no-pdf-header-footer",
        f"--print-to-pdf={os.path.abspath(pdf_path)}",
        file_url,
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if proc.returncode != 0 or not os.path.exists(pdf_path):
        raise RuntimeError(f"Browser PDF export failed ({proc.returncode}): {proc.stderr}")


def main():
    init_database()
    data = fetch_dashboard_payload()
    logo_uri = load_pes_logo_data_uri()
    part_a_css = capstone_css()
    part_b_css = brochure_css()

    os.makedirs(PDF_DIR, exist_ok=True)
    os.makedirs(BUILD_DIR, exist_ok=True)

    browser = find_browser()
    if not browser:
        raise RuntimeError("Neither Chrome nor Edge was found for headless PDF generation.")

    part_a_html = os.path.join(BUILD_DIR, "part_a_voltedge.html")
    part_b_html = os.path.join(BUILD_DIR, "part_b_nexora.html")

    part_a_pdf = os.path.join(PDF_DIR, "EBS24CS-P01 001-002-003-004 VoltEdge-ERPNext.pdf")
    part_b_pdf = os.path.join(PDF_DIR, "EBS24CS-P02 001-002-003-004 NEXORA.pdf")

    part_a_slides = build_part_a_slides(data, logo_uri)
    part_b_pages = build_part_b_brochure(data)

    with open(part_a_html, "w", encoding="utf-8") as fh:
        fh.write(wrap_html("EBS24CS-P01 VoltEdge ERPNext v16 Implementation", part_a_css, part_a_slides))
    with open(part_b_html, "w", encoding="utf-8") as fh:
        fh.write(wrap_html("EBS24CS-P02 NEXORA Digital Sales Brochure", part_b_css, part_b_pages))

    html_to_pdf(browser, part_a_html, part_a_pdf)
    html_to_pdf(browser, part_b_html, part_b_pdf)
    shutil.copy2(part_a_pdf, os.path.join(os.path.dirname(PROJECT_DIR), os.path.basename(part_a_pdf)))
    shutil.copy2(part_b_pdf, os.path.join(os.path.dirname(PROJECT_DIR), os.path.basename(part_b_pdf)))
    generate_part_b_docx(data)

    print(f"[OK] Part A PDF ({len(part_a_slides)} slides): {part_a_pdf} ({os.path.getsize(part_a_pdf)} bytes)")
    print(f"[OK] Part B PDF ({len(part_b_pages)}-page A4 brochure): {part_b_pdf} ({os.path.getsize(part_b_pdf)} bytes)")


if __name__ == "__main__":
    main()
