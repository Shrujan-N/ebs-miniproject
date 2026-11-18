"""
Part B Digital Sales Brochure DOCX Generator (Pure Black & White MS Word Student Document)
Course: UE24CS343AB8 Enterprise Business Systems
Outputs:
  1. d:\\university\\sem 5\\EBS\\miniproject\\ebs miniproject\\pdfs\\EBS24CS-P02 001-002-003-004 NEXORA.docx
  2. d:\\university\\sem 5\\EBS\\miniproject\\EBS24CS-P02 001-002-003-004 NEXORA.docx

Strict Monochrome / Grayscale Only (#000000, #333333, #808080, #E6E6E6, #F2F2F2, #FFFFFF).
Uses stdlib zipfile + Chrome headless SVG->PNG + strict ECMA-376 OpenXML.
"""

import os
import shutil
import struct
import subprocess
import sys
import zipfile
from xml.sax.saxutils import escape as xml_esc

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR)
ROOT_SUBMISSION_DIR = os.path.dirname(PROJECT_DIR)
PDF_DIR = os.path.join(PROJECT_DIR, "pdfs")
ASSET_DIR = os.path.join(PDF_DIR, "_html_sources", "docx_assets")

sys.path.insert(0, BASE_DIR)
from app import fetch_dashboard_payload  # noqa: E402
from generate_part_b_brochure import (  # noqa: E402
    svg_brochure_benchmark_plot,
    svg_brochure_ecosystem,
    svg_brochure_gnn_match,
    svg_brochure_lstm_forecast,
    svg_brochure_mqtt_cnn,
    svg_brochure_p2p_flowchart,
    svg_nexora_brand_mark,
)
from seed_data import init_database  # noqa: E402


def find_browser():
    for path in (
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    ):
        if os.path.exists(path):
            return path
    return None


def render_svg_to_png(browser_exe, svg_html, view_w, view_h, scale, out_png):
    px_w = int(round(view_w * scale))
    px_h = int(round(view_h * scale))
    styled_svg = svg_html.replace('width="100%"', f'width="{px_w}" height="{px_h}"')
    styled_svg = styled_svg.replace(
        f'width="{view_w}" height="{view_h}"',
        f'width="{px_w}" height="{px_h}"',
    )
    html_p = os.path.splitext(out_png)[0] + ".html"
    with open(html_p, "w", encoding="utf-8") as fh:
        fh.write(
            f'<!DOCTYPE html><html><body style="margin:0;padding:0;overflow:hidden;background:#FFFFFF;">'
            f"{styled_svg}</body></html>"
        )
    file_url = "file:///" + os.path.abspath(html_p).replace("\\", "/")
    cmd = [
        browser_exe,
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--hide-scrollbars",
        f"--window-size={px_w},{px_h}",
        f"--screenshot={os.path.abspath(out_png)}",
        file_url,
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=45)
    if proc.returncode != 0 or not os.path.exists(out_png):
        raise RuntimeError(f"Failed rendering {out_png}: {proc.stderr}")
    raw = open(out_png, "rb").read()
    w, h = struct.unpack(">II", raw[16:24])
    return w, h


def render_all_brochure_assets(browser_exe):
    os.makedirs(ASSET_DIR, exist_ok=True)
    specs = [
        ("rId10", "logo.png", svg_nexora_brand_mark(64), 64, 64, 2.5),
        ("rId11", "fig1_ecosystem.png", svg_brochure_ecosystem(), 540, 218, 2.4),
        ("rId12", "fig2_benchmark.png", svg_brochure_benchmark_plot(), 520, 178, 2.4),
        ("rId13", "fig3_lstm.png", svg_brochure_lstm_forecast(), 530, 162, 2.4),
        ("rId14", "fig4_mqtt_cnn.png", svg_brochure_mqtt_cnn(), 530, 154, 2.4),
        ("rId15", "fig5_gnn_match.png", svg_brochure_gnn_match(), 530, 165, 2.4),
        ("rId16", "fig6_p2p_flow.png", svg_brochure_p2p_flowchart(), 530, 278, 2.4),
    ]
    assets = {}
    for rid, fname, svg_src, vw, vh, scale in specs:
        out_png = os.path.join(ASSET_DIR, fname)
        pw, ph = render_svg_to_png(browser_exe, svg_src, vw, vh, scale, out_png)
        assets[fname] = {
            "rid": rid,
            "fname": fname,
            "path": out_png,
            "px_w": pw,
            "px_h": ph,
        }
    return assets


# =====================================================================
# OOXML HELPERS (Black & White Student Word Format)
# =====================================================================

def run_xml(text, font="Calibri", sz_pt=10.0, bold=False, italic=False, color="000000", underline=False):
    sz = int(round(sz_pt * 2))
    b_tag = "<w:b/>" if bold else ""
    i_tag = "<w:i/>" if italic else ""
    u_tag = '<w:u w:val="single"/>' if underline else ""
    chunks = str(text).split("\n")
    inner = "".join(
        (f'<w:t xml:space="preserve">{xml_esc(chunk)}</w:t>' + ("<w:br/>" if idx < len(chunks) - 1 else ""))
        for idx, chunk in enumerate(chunks)
    )
    return (
        f'<w:r><w:rPr><w:rFonts w:ascii="{font}" w:hAnsi="{font}" w:cs="{font}"/>'
        f'{b_tag}{i_tag}<w:color w:val="{color}"/><w:sz w:val="{sz}"/><w:szCs w:val="{sz}"/>{u_tag}'
        f'</w:rPr>{inner}</w:r>'
    )


def p_xml(runs_xml, before=0, after=75, line=255, align="left", left_indent=0,
          left_border_color=None, left_border_sz=18, bg_fill=None, bottom_border_color=None,
          bottom_border_sz=6):
    # ECMA-376 CT_PPrBase element order: pBdr -> shd -> spacing -> ind -> jc
    ppr = ['<w:pPr>']
    if left_border_color or bottom_border_color:
        ppr.append("<w:pBdr>")
        if left_border_color:
            ppr.append(f'<w:left w:val="single" w:sz="{left_border_sz}" w:space="8" w:color="{left_border_color}"/>')
        if bottom_border_color:
            ppr.append(f'<w:bottom w:val="single" w:sz="{bottom_border_sz}" w:space="3" w:color="{bottom_border_color}"/>')
        ppr.append("</w:pBdr>")
    if bg_fill:
        ppr.append(f'<w:shd w:val="clear" w:color="auto" w:fill="{bg_fill}"/>')
    ppr.append(f'<w:spacing w:before="{before}" w:after="{after}" w:line="{line}" w:lineRule="auto"/>')
    if left_indent:
        ppr.append(f'<w:ind w:left="{left_indent}"/>')
    if align != "left":
        ppr.append(f'<w:jc w:val="{align}"/>')
    ppr.append("</w:pPr>")
    return f'<w:p>{"".join(ppr)}{runs_xml}</w:p>'


def sec_heading(title_text, before=80, after=65):
    return p_xml(
        run_xml(title_text, font="Calibri", sz_pt=13.5, bold=True, color="000000"),
        before=before,
        after=after,
        line=255,
        bottom_border_color="000000",
        bottom_border_sz=8,
    )


def sub_heading(title_text, before=80, after=45):
    return p_xml(
        run_xml(title_text, font="Calibri", sz_pt=11.0, bold=True, color="000000"),
        before=before,
        after=after,
        line=245,
    )


def bullet_p(lead_bold, body_text, sz_pt=9.4, after=40):
    runs = (
        run_xml("\u2022  ", font="Calibri", sz_pt=sz_pt, bold=True, color="000000")
        + (run_xml(lead_bold + " ", font="Calibri", sz_pt=sz_pt, bold=True, color="000000") if lead_bold else "")
        + run_xml(body_text, font="Calibri", sz_pt=sz_pt, color="000000")
    )
    return p_xml(runs, before=0, after=after, line=245, left_indent=180)


def page_break_p():
    return '<w:p><w:r><w:br w:type="page"/></w:r></w:p>'


_DOC_IMG_SEQ = 1


def drawing_p(asset_info, width_inches, align="center", after=35, before=20):
    global _DOC_IMG_SEQ
    img_id = _DOC_IMG_SEQ
    _DOC_IMG_SEQ += 1
    cx = int(round(width_inches * 914400))
    cy = int(round(cx * (asset_info["px_h"] / float(asset_info["px_w"]))))
    rid = asset_info["rid"]
    fname = xml_esc(asset_info["fname"])
    drawing = (
        f'<w:r><w:drawing>'
        f'<wp:inline distT="0" distB="0" distL="0" distR="0">'
        f'<wp:extent cx="{cx}" cy="{cy}"/>'
        f'<wp:effectExtent l="0" t="0" r="0" b="0"/>'
        f'<wp:docPr id="{img_id}" name="{fname}"/>'
        f'<wp:cNvGraphicFramePr><a:graphicFrameLocks xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" noChangeAspect="1"/></wp:cNvGraphicFramePr>'
        f'<a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">'
        f'<a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">'
        f'<pic:pic xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture">'
        f'<pic:nvPicPr><pic:cNvPr id="{img_id}" name="{fname}"/><pic:cNvPicPr/></pic:nvPicPr>'
        f'<pic:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>'
        f'<pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm>'
        f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr>'
        f'</pic:pic></a:graphicData></a:graphic>'
        f'</wp:inline></w:drawing></w:r>'
    )
    return p_xml(drawing, before=before, after=after, align=align)


def make_cell(content_xml, width_dxa, fill=None, borders=None, pad_v=75, pad_h=105, valign="top"):
    if borders is None:
        borders = {
            "top": ("single", 6, "000000"),
            "bottom": ("single", 6, "000000"),
            "left": ("single", 6, "000000"),
            "right": ("single", 6, "000000"),
        }
    bdr_tags = []
    for side in ("top", "left", "bottom", "right"):
        if side in borders and borders[side] is not None:
            val, sz, clr = borders[side]
            bdr_tags.append(f'<w:{side} w:val="{val}" w:sz="{sz}" w:space="0" w:color="{clr}"/>')
        else:
            bdr_tags.append(f'<w:{side} w:val="none"/>')
    shd = f'<w:shd w:val="clear" w:color="auto" w:fill="{fill}"/>' if fill else ""
    tcpr = (
        f'<w:tcPr><w:tcW w:w="{width_dxa}" w:type="dxa"/>'
        f'<w:tcBorders>{"".join(bdr_tags)}</w:tcBorders>'
        f'{shd}'
        f'<w:tcMar><w:top w:w="{pad_v}" w:type="dxa"/><w:left w:w="{pad_h}" w:type="dxa"/>'
        f'<w:bottom w:w="{pad_v}" w:type="dxa"/><w:right w:w="{pad_h}" w:type="dxa"/></w:tcMar>'
        f'<w:vAlign w:val="{valign}"/></w:tcPr>'
    )
    return f"<w:tc>{tcpr}{content_xml}</w:tc>"


def make_table(col_widths, rows_xml, outer_border_color="000000", cell_spacing=0):
    tot_w = sum(col_widths)
    grid = "".join(f'<w:gridCol w:w="{w}"/>' for w in col_widths)
    bdr = (
        f'<w:tblBorders>'
        f'<w:top w:val="single" w:sz="6" w:space="0" w:color="{outer_border_color}"/>'
        f'<w:left w:val="single" w:sz="6" w:space="0" w:color="{outer_border_color}"/>'
        f'<w:bottom w:val="single" w:sz="6" w:space="0" w:color="{outer_border_color}"/>'
        f'<w:right w:val="single" w:sz="6" w:space="0" w:color="{outer_border_color}"/>'
        f'<w:insideH w:val="single" w:sz="4" w:space="0" w:color="{outer_border_color}"/>'
        f'<w:insideV w:val="single" w:sz="4" w:space="0" w:color="{outer_border_color}"/>'
        f'</w:tblBorders>'
    ) if outer_border_color else '<w:tblBorders><w:top w:val="none"/><w:left w:val="none"/><w:bottom w:val="none"/><w:right w:val="none"/><w:insideH w:val="none"/><w:insideV w:val="none"/></w:tblBorders>'
    spacing = f'<w:tblCellSpacing w:w="{cell_spacing}" w:type="dxa"/>' if cell_spacing else ""
    tblpr = (
        f'<w:tblPr><w:tblW w:w="{tot_w}" w:type="dxa"/>'
        f'{spacing}{bdr}<w:tblLayout w:type="fixed"/></w:tblPr>'
    )
    rows_joined = "".join(f"<w:tr>{r}</w:tr>" for r in rows_xml)
    return f"<w:tbl>{tblpr}<w:tblGrid>{grid}</w:tblGrid>{rows_joined}</w:tbl>"


def fig_caption_and_blurb(caption_text, blurb_text, after_blurb=75):
    return (
        p_xml(run_xml(caption_text, sz_pt=9.2, bold=True, color="000000"), before=45, after=20, line=240)
        + p_xml(run_xml(blurb_text, sz_pt=8.8, italic=True, color="333333"), before=0, after=after_blurb, line=240)
    )


def human_gate_box(text_prefix, bold_role, text_suffix, width_dxa=10206):
    inner = p_xml(
        run_xml("Where Humans Review & Approve: ", sz_pt=8.9, bold=True, color="000000")
        + run_xml(text_prefix + " ", sz_pt=8.9, color="000000")
        + run_xml(bold_role + " ", sz_pt=8.9, bold=True, color="000000")
        + run_xml(text_suffix, sz_pt=8.9, color="000000"),
        before=0,
        after=0,
        line=245,
    )
    bdrs = {"top": ("single", 4, "808080"), "bottom": ("single", 4, "808080"), "right": ("single", 4, "808080"), "left": ("single", 18, "000000")}
    return make_table([width_dxa], [make_cell(inner, width_dxa, fill="F2F2F2", borders=bdrs, pad_v=65, pad_h=110)], outer_border_color=None)


# =====================================================================
# 8-PAGE PURE BLACK & WHITE STUDENT WORD DOCUMENT
# =====================================================================

def build_document_xml(data, assets):
    emp_by_name = {}
    for emp in data["employees"]:
        nm = emp["employee_name"].split("(")[0].strip().lower()
        emp_by_name[nm] = emp["srn"]

    W_TOT = 10206
    parts = []

    # PAGE 1: COVER PAGE (Pure White + Crisp Black Rules + Greyscale Diagram)
    c_left = drawing_p(assets["logo.png"], 0.60, align="left", before=0, after=0)
    c_mid = (
        p_xml(run_xml("NEXORA", sz_pt=20.0, bold=True, color="000000"), before=0, after=10, line=240)
        + p_xml(run_xml("AI-NATIVE ENTERPRISE BUSINESS SYSTEM", sz_pt=8.8, bold=True, color="333333"), before=0, after=0, line=220)
    )
    c_right = (
        p_xml(run_xml("Product Sales Brochure", sz_pt=9.2, bold=True, color="000000"), align="right", before=0, after=10, line=230)
        + p_xml(run_xml("UE24CS343AB8 (Part B)", sz_pt=8.6, color="333333"), align="right", before=0, after=0, line=220)
    )
    band_bdrs = {
        "top": ("single", 16, "000000"),
        "bottom": ("single", 16, "000000"),
        "left": None,
        "right": None,
    }
    cover_banner = make_table(
        [1050, 6200, 2956],
        [
            make_cell(c_left, 1050, fill="FFFFFF", borders=band_bdrs, pad_v=110, pad_h=40, valign="center")
            + make_cell(c_mid, 6200, fill="FFFFFF", borders=band_bdrs, pad_v=110, pad_h=60, valign="center")
            + make_cell(c_right, 2956, fill="FFFFFF", borders=band_bdrs, pad_v=110, pad_h=40, valign="center")
        ],
        outer_border_color=None,
    )
    parts.append(cover_banner)

    parts.append(p_xml(run_xml("INTELLIGENCE THAT RUNS YOUR ENTERPRISE.", sz_pt=9.5, bold=True, color="333333"), before=200, after=35))
    parts.append(p_xml(run_xml("Your Enterprise.\nReimagined with Intelligence.", sz_pt=22.5, bold=True, color="000000"), before=0, after=105, line=275))
    parts.append(
        p_xml(
            run_xml(
                "Most business software only records transactions after problems have already occurred. ", sz_pt=10.2
            )
            + run_xml("NEXORA", sz_pt=10.2, bold=True)
            + run_xml(
                " is an AI-native Enterprise Business System designed for growing manufacturers and B2B distributors. "
                "Specialized AI agents monitor stock depletion, watch assembly quality, and audit supplier invoices, "
                "while human managers keep final approval authority over every financial commitment.",
                sz_pt=10.2,
            ),
            before=0,
            after=115,
            line=270,
        )
    )

    fig1_cell = make_cell(drawing_p(assets["fig1_ecosystem.png"], 6.75, align="center", before=15, after=15), W_TOT, fill="FFFFFF", pad_v=70, pad_h=85)
    parts.append(make_table([W_TOT], [fig1_cell], outer_border_color="000000"))
    parts.append(
        fig_caption_and_blurb(
            "Figure 1: Connected NEXORA Enterprise Architecture with Human Governance",
            '"Every department shares one live operational ledger: autonomous agents prepare routine procurement, production, and invoice work, while role-based approvals ensure complete management control."',
            after_blurb=110,
        )
    )

    cov_rows = [
        make_cell(p_xml(run_xml("8 Core Modules", sz_pt=9.5, bold=True), after=0), 3402, fill="E6E6E6", pad_v=65, pad_h=100)
        + make_cell(p_xml(run_xml("3 Agentic AI Engines", sz_pt=9.5, bold=True), after=0), 3402, fill="E6E6E6", pad_v=65, pad_h=100)
        + make_cell(p_xml(run_xml("Human-First Guardrails", sz_pt=9.5, bold=True), after=0), 3402, fill="E6E6E6", pad_v=65, pad_h=100),
        make_cell(p_xml(run_xml("Sales, Procurement, Inventory, Warehouse (WH), Production, Quality, Finance, and HR.", sz_pt=8.9), after=0, line=240), 3402, fill="FFFFFF", pad_v=85, pad_h=100)
        + make_cell(p_xml(run_xml("LSTM demand planning, MQTT + CNN visual QC, and VLM + GNN 3-way invoice auditing.", sz_pt=8.9), after=0, line=240), 3402, fill="FFFFFF", pad_v=85, pad_h=100)
        + make_cell(p_xml(run_xml("Strict spend thresholds, RBAC security, audit logs, and instant override gates.", sz_pt=8.9), after=0, line=240), 3402, fill="FFFFFF", pad_v=85, pad_h=100),
    ]
    parts.append(make_table([3402, 3402, 3402], cov_rows))
    parts.append(p_xml("", before=130, after=0))
    cov_ftr_bdr = {"top": ("single", 8, "000000"), "bottom": None, "left": None, "right": None}
    parts.append(
        make_table(
            [6206, 4000],
            [
                make_cell(p_xml(run_xml("NEXORA Enterprise Systems Pvt. Ltd.  \u2022  Bengaluru, India", sz_pt=8.8, bold=True), after=0), 6206, fill="F2F2F2", borders=cov_ftr_bdr, pad_v=75, pad_h=100)
                + make_cell(p_xml(run_xml("Digital Sales Brochure  \u2022  Page 1 of 8", sz_pt=8.8, bold=True), align="right", after=0), 4000, fill="F2F2F2", borders=cov_ftr_bdr, pad_v=75, pad_h=100)
            ],
            outer_border_color=None,
        )
    )
    parts.append(page_break_p())

    # PAGE 2: ABOUT NEXORA & VALUE IMPACT
    parts.append(sec_heading("1. Why Move Beyond Rule-Based ERP Software?"))
    parts.append(
        p_xml(
            run_xml(
                "Traditional ERP platforms depend on static IF-THEN rules, sending an alert only after warehouse stock falls below a fixed number. "
                "When supplier lead times slip or customer orders spike unexpectedly, rigid scripts react too late and leave staff clearing exceptions in spreadsheets.",
                sz_pt=9.7,
            ),
            after=65,
        )
    )
    parts.append(
        p_xml(
            run_xml("NEXORA replaces brittle scripts with ", sz_pt=9.7)
            + run_xml("Agentic AI", sz_pt=9.7, bold=True)
            + run_xml(": software agents that continuously ", sz_pt=9.7)
            + run_xml("Perceive", sz_pt=9.7, bold=True)
            + run_xml(" live ERP data, ", sz_pt=9.7)
            + run_xml("Reason", sz_pt=9.7, bold=True)
            + run_xml(" with forecasting and graph checks, ", sz_pt=9.7)
            + run_xml("Plan", sz_pt=9.7, bold=True)
            + run_xml(" concrete draft actions, and ", sz_pt=9.7)
            + run_xml("Route for Human Sign-Off", sz_pt=9.7, bold=True)
            + run_xml(" before money leaves the business.", sz_pt=9.7),
            after=85,
        )
    )

    parts.append(sub_heading("Side-by-Side Operational Comparison", before=30, after=45))
    comp_rows = [
        ("Business Area", "Traditional Rule-Based ERP", "NEXORA AI-Native Approach"),
        ("Inventory Reordering", "Triggers an alert only after stock drops past a static fixed number.", "LSTM agent forecasts 14-day runout curves from open orders and prepares draft POs early."),
        ("Vendor Selection", "Defaults blindly to the first vendor listed on the master item card.", "Scores suppliers dynamically by on-time delivery, unit pricing, and defect history."),
        ("Production Quality", "Defects recorded hours later during end-of-shift manual batch logs.", "Edge MQTT + CNN vision flags assembly flaws on-line in real time for supervisor review."),
        ("Supplier Billing (AP)", "Accounts staff manually type PDF invoice lines into ERP voucher screens.", "VLM + GNN agent parses PDF bills and cross-checks PO, Goods Receipt, and GST amounts."),
        ("Governance Control", "All-or-nothing automation or completely manual data entry.", "Autonomous drafting paired with configurable human spend caps and audit trails."),
    ]
    comp_xml_rows = []
    for r_i, (a, b, c) in enumerate(comp_rows):
        hdr = r_i == 0
        fill = "E6E6E6" if hdr else ("F7F7F7" if r_i % 2 == 0 else "FFFFFF")
        comp_xml_rows.append(
            make_cell(p_xml(run_xml(a, sz_pt=8.9, bold=True), after=0), 2200, fill=fill, pad_v=60, pad_h=90)
            + make_cell(p_xml(run_xml(b, sz_pt=8.9, bold=hdr), after=0), 3800, fill=fill, pad_v=60, pad_h=90)
            + make_cell(p_xml(run_xml(c, sz_pt=8.9, bold=hdr), after=0), 4206, fill=fill, pad_v=60, pad_h=90)
        )
    parts.append(make_table([2200, 3800, 4206], comp_xml_rows))

    parts.append(sub_heading("2. Measured Time & Exception Reduction in Pilot Workflows", before=115, after=50))
    fig2_cell = make_cell(drawing_p(assets["fig2_benchmark.png"], 6.6, align="center", before=10, after=10), W_TOT, fill="FFFFFF", pad_v=60, pad_h=80)
    parts.append(make_table([W_TOT], [fig2_cell], outer_border_color="000000"))
    parts.append(
        fig_caption_and_blurb(
            "Figure 2: Pilot Workflow Turnaround Benchmark (Rule-Based ERP vs. NEXORA)",
            '"By letting AI agents assemble draft purchase orders, pre-scan invoices, and watch assembly cameras continuously, operations teams shift from repetitive typing to fast exception approvals." (*Illustrative prototype model benchmarks.)',
            after_blurb=0,
        )
    )
    parts.append(page_break_p())

    # PAGE 3: 8 CORE BUSINESS MODULES & ENTERPRISE SERVICES (Clean MS Word tables!)
    parts.append(sec_heading("3. Product Offerings: 8 Unified Business Modules"))
    parts.append(
        p_xml(
            run_xml("NEXORA delivers a single-database ERP backbone across manufacturing, distribution, warehousing, and corporate finance, eliminating fragile connectors between departments.", sz_pt=9.7),
            after=80,
        )
    )

    modules = [
        ("Sales Management", "Quotes, tiered customer pricing, credit-limit checks, GST tax invoicing, and order delivery tracking."),
        ("Procurement Management", "Automated RFQ comparison, blanket supplier contracts, dynamic lead-time tracking, and smart PO drafting."),
        ("Inventory Management", "Multi-level BOM sync, FIFO/moving-average valuation, serial/lot traceability, and safety stock control."),
        ("Warehouse Management (WH)", "Rack & bin put-away mapping, inter-warehouse stock transfers, pick-pack-ship workflows, and barcoding."),
        ("Production Management", "Shop-floor work orders, machine capacity planning, WIP tracking, raw-material issue, and scrap logging."),
        ("Quality Management (QA/QC)", "Incoming vendor quarantine inspection, inline tolerance checks, defect imaging logs, and CAPA closure."),
        ("Finance & Accounting", "General ledger, GST/TDS compliance registers, 3-way AP invoice matching, and cash-flow forecasting."),
        ("Human Resources (HR)", "Department roles, shift attendance scheduling, approval hierarchy mapping, and employee expense claims."),
    ]
    mod_tbl_rows = [
        make_cell(p_xml(run_xml("#", sz_pt=9.0, bold=True), align="center", after=0), 600, fill="E6E6E6", pad_v=60, pad_h=60)
        + make_cell(p_xml(run_xml("Core Business Module", sz_pt=9.0, bold=True), after=0), 2800, fill="E6E6E6", pad_v=60, pad_h=90)
        + make_cell(p_xml(run_xml("Functional Capabilities Included", sz_pt=9.0, bold=True), after=0), 6806, fill="E6E6E6", pad_v=60, pad_h=90)
    ]
    for idx, (m_title, m_desc) in enumerate(modules):
        f_row = "F7F7F7" if idx % 2 == 1 else "FFFFFF"
        mod_tbl_rows.append(
            make_cell(p_xml(run_xml(str(idx + 1), sz_pt=9.0, bold=True), align="center", after=0), 600, fill=f_row, pad_v=65, pad_h=60)
            + make_cell(p_xml(run_xml(m_title, sz_pt=9.0, bold=True), after=0), 2800, fill=f_row, pad_v=65, pad_h=90)
            + make_cell(p_xml(run_xml(m_desc, sz_pt=9.0), after=0, line=240), 6806, fill=f_row, pad_v=65, pad_h=90)
        )
    parts.append(make_table([600, 2800, 6806], mod_tbl_rows))

    parts.append(sec_heading("4. Implementation, Migration, Training & Support Services", before=150, after=55))
    parts.append(
        p_xml(
            run_xml("Technology succeeds only when people trust it. Every NEXORA subscription can be paired with structured rollout services delivered by our solutions engineering team:", sz_pt=9.7),
            after=80,
        )
    )
    svc_rows = [
        make_cell(p_xml(run_xml("Guided Implementation", sz_pt=9.5, bold=True), after=0), 3402, fill="E6E6E6", pad_v=65, pad_h=100)
        + make_cell(p_xml(run_xml("Legacy Data Migration", sz_pt=9.5, bold=True), after=0), 3402, fill="E6E6E6", pad_v=65, pad_h=100)
        + make_cell(p_xml(run_xml("Training & 24/7 Support", sz_pt=9.5, bold=True), after=0), 3402, fill="E6E6E6", pad_v=65, pad_h=100),
        make_cell(
            bullet_p("", "Workflow discovery workshops (Week 1-2)", sz_pt=8.9)
            + bullet_p("", "Approval threshold & RBAC setup", sz_pt=8.9)
            + bullet_p("", "Sandbox parallel run before go-live", sz_pt=8.9, after=0),
            3402, fill="FFFFFF", pad_v=90, pad_h=90,
        )
        + make_cell(
            bullet_p("", "Automated cleanup of duplicate SKUs", sz_pt=8.9)
            + bullet_p("", "Import from Tally, SAP B1, ERPNext & Excel", sz_pt=8.9)
            + bullet_p("", "Opening stock & ledger balance validation", sz_pt=8.9, after=0),
            3402, fill="FFFFFF", pad_v=90, pad_h=90,
        )
        + make_cell(
            bullet_p("", "Role-based operator & controller training", sz_pt=8.9)
            + bullet_p("", "Quarterly AI forecast accuracy tuning", sz_pt=8.9)
            + bullet_p("", "Dedicated SLA ticket & phone desk", sz_pt=8.9, after=0),
            3402, fill="FFFFFF", pad_v=90, pad_h=90,
        ),
    ]
    parts.append(make_table([3402, 3402, 3402], svc_rows))
    parts.append(page_break_p())

    # PAGE 4: AGENTIC FEATURES (MODULES A & B)
    parts.append(sec_heading("5. Agentic AI Features: Smart Modules with Human Review"))
    parts.append(p_xml(run_xml("Below are two of NEXORA's core intelligent modules, showing exact AI/ML models paired with mandatory human decision gates.", sz_pt=9.6), after=70))

    mod_a_inner = (
        sub_heading("Agent Module A: Procurement & Warehouse \u2014 Procurement Intelligence Agent", before=0, after=35)
        + p_xml(
            run_xml("Uses ", sz_pt=9.1)
            + run_xml("Long Short-Term Memory (LSTM)", sz_pt=9.1, bold=True)
            + run_xml(" neural networks trained on rolling consumption history, seasonal demand spikes, and supplier lead-time drift to compute dynamic depletion rates and stage replenishment orders before bins run dry.", sz_pt=9.1),
            after=50, line=240,
        )
        + drawing_p(assets["fig3_lstm.png"], 6.6, align="center", before=10, after=20)
        + fig_caption_and_blurb(
            "Figure 3: Dynamic Stock Depletion Forecast & Queued PO Approval Card",
            '"Detects an upcoming Day-11 shortage for Servo Actuator #AC-40 and stages Draft PO #NX-PO-408 automatically."',
            after_blurb=45,
        )
        + human_gate_box(
            "Any draft PO exceeding the department spend ceiling (e.g., \u20b92,50,000) or switching to a backup supplier stays paused until the",
            "Procurement Manager",
            "reviews the LSTM rationale and clicks Approve & Send or edits quantity.",
            width_dxa=9880,
        )
        + p_xml("", before=0, after=0, line=20)
    )
    parts.append(make_table([W_TOT], [make_cell(mod_a_inner, W_TOT, fill="FFFFFF", pad_v=80, pad_h=115)]))
    parts.append(p_xml("", before=0, after=70))

    mod_b_inner = (
        sub_heading("Agent Module B: Production & Quality \u2014 Production Optimization Agent", before=0, after=35)
        + p_xml(
            run_xml("Combines ", sz_pt=9.1)
            + run_xml("IoT Edge Processing (MQTT protocols)", sz_pt=9.1, bold=True)
            + run_xml(" on assembly machinery with ", sz_pt=9.1)
            + run_xml("Convolutional Neural Networks (CNNs)", sz_pt=9.1, bold=True)
            + run_xml(" at optical camera stations to catch micro-cracks, missing fasteners, or thermal drift within milliseconds.", sz_pt=9.1),
            after=50, line=240,
        )
        + drawing_p(assets["fig4_mqtt_cnn.png"], 6.6, align="center", before=10, after=20)
        + fig_caption_and_blurb(
            "Figure 4: Shop-Floor Edge MQTT Telemetry & CNN Optical Defect Detection Frame",
            '"Isolates a surface micro-crack on Station B2 with 96% CNN confidence and tags the lot for quick inspection."',
            after_blurb=45,
        )
        + human_gate_box(
            "The agent never shuts down an assembly conveyor unilaterally. The",
            "Production Line Supervisor",
            "views the bounding-box camera snapshot to confirm lot diversion or dismiss a false positive.",
            width_dxa=9880,
        )
        + p_xml("", before=0, after=0, line=20)
    )
    parts.append(make_table([W_TOT], [make_cell(mod_b_inner, W_TOT, fill="FFFFFF", pad_v=80, pad_h=115)]))
    parts.append(page_break_p())

    # PAGE 5: AGENT MODULE C (FINANCE) + SUMMARY TABLE
    parts.append(sec_heading("Agent Module C: Finance & Audit \u2014 Financial Guardian Agent"))
    parts.append(
        p_xml(
            run_xml("Accounts Payable teams spend days reconciling supplier PDF bills that vary across formats. NEXORA pairs ", sz_pt=9.6)
            + run_xml("Vision-Language Models (VLMs)", sz_pt=9.6, bold=True)
            + run_xml(", which parse unstructured PDF or scanned invoices without rigid templates, with ", sz_pt=9.6)
            + run_xml("Graph Neural Networks (GNNs)", sz_pt=9.6, bold=True)
            + run_xml(" linking Vendor, PO, Goods Receipt Note (GRN), Bank Account, and Tax IDs to block duplicate billing and unapproved fees.", sz_pt=9.6),
            after=80,
        )
    )
    fig5_cell = make_cell(drawing_p(assets["fig5_gnn_match.png"], 6.7, align="center", before=15, after=15), W_TOT, fill="FFFFFF", pad_v=65, pad_h=80)
    parts.append(make_table([W_TOT], [fig5_cell], outer_border_color="000000"))
    parts.append(
        fig_caption_and_blurb(
            "Figure 5: Financial Guardian VLM + GNN 3-Way Match Exception Screen",
            '"In this example, the vendor billed for 100 Valve Bodies plus a \u20b99,500 rush fee when QA accepted only 92 units on the warehouse GRN, freezing payout automatically."',
            after_blurb=60,
        )
    )
    parts.append(
        human_gate_box(
            "Whenever a quantity mismatch, price variance, or vendor bank change triggers a GNN flag, payout waits for the",
            "Finance Controller",
            "to authorize partial payment (\u20b91,65,600 for 92 accepted units) or trigger a vendor debit note.",
        )
    )

    parts.append(sub_heading("Cross-Module Agentic Summary & Human Checkpoints", before=125, after=50))
    sum_rows = [
        ("ERP Module", "Agent & Models Used", "Autonomous Smart Action", "Human Approval Checkpoint"),
        ("Procurement & WH", "Procurement Agent\n(LSTM Time-Series)", "Predicts runout curves and drafts optimal multi-vendor POs.", "Procurement Manager approves orders over budget cap or new suppliers."),
        ("Production & QA", "Production Agent\n(MQTT Edge + CNN)", "Detects assembly anomalies and isolates suspect batch lots.", "Shift Supervisor confirms conveyor stops, scrap tags, or lot release."),
        ("Finance & AP", "Financial Guardian\n(VLM + GNN Graph)", "Reads invoice PDFs and performs 3-way PO-GRN-Bill verification.", "Finance Controller resolves variance holds and releases bank transfers."),
        ("Sales & Credit", "Deal Margin Guard\n(Gradient Risk Scoring)", "Flags overdue customer accounts and low-margin discount quotes.", "Sales Head reviews credit-limit overrides before releasing dispatch."),
    ]
    sum_xml = []
    for r_i, (c1t, c2t, c3t, c4t) in enumerate(sum_rows):
        hdr = r_i == 0
        fill = "E6E6E6" if hdr else ("F7F7F7" if r_i % 2 == 0 else "FFFFFF")
        sum_xml.append(
            make_cell(p_xml(run_xml(c1t, sz_pt=8.8, bold=True), after=0), 1900, fill=fill, pad_v=65, pad_h=80)
            + make_cell(p_xml(run_xml(c2t, sz_pt=8.7, bold=hdr), after=0, line=235), 2400, fill=fill, pad_v=65, pad_h=80)
            + make_cell(p_xml(run_xml(c3t, sz_pt=8.7, bold=hdr), after=0, line=235), 3000, fill=fill, pad_v=65, pad_h=80)
            + make_cell(p_xml(run_xml(c4t, sz_pt=8.7, bold=hdr), after=0, line=235), 2906, fill=fill, pad_v=65, pad_h=80)
        )
    parts.append(make_table([1900, 2400, 3000, 2906], sum_xml))
    parts.append(page_break_p())

    # PAGE 6: HOW IT WORKS
    parts.append(sec_heading("6. How It Works: AI Speed Paired with Human Control"))
    parts.append(
        p_xml(
            run_xml(
                "NEXORA structures every operational lifecycle, such as Procure-to-Pay (P2P), into clear handoffs between software agents and authorized employees. "
                "Agents handle continuous monitoring, calculation, and paperwork preparation; people approve capital spend, inspect physical goods, and authorize bank payouts.",
                sz_pt=9.7,
            ),
            after=80,
        )
    )
    fig6_cell = make_cell(drawing_p(assets["fig6_p2p_flow.png"], 6.75, align="center", before=20, after=20), W_TOT, fill="FFFFFF", pad_v=75, pad_h=85)
    parts.append(make_table([W_TOT], [fig6_cell], outer_border_color="000000"))
    parts.append(
        fig_caption_and_blurb(
            "Figure 6: End-to-End Intelligent Procure-to-Pay Process \u2014 Steps by AI vs. People",
            '"Notice the continuous learning loop: whenever a Procurement Manager adjusts or rejects an AI-drafted order at Step 4, NEXORA logs the reason and refines future LSTM recommendations."',
            after_blurb=90,
        )
    )

    flow_rows = [
        make_cell(p_xml(run_xml("Steps Handled by AI Agents", sz_pt=9.8, bold=True), after=0), 5103, fill="E6E6E6", pad_v=65, pad_h=110)
        + make_cell(p_xml(run_xml("Steps Handled by People", sz_pt=9.8, bold=True), after=0), 5103, fill="E6E6E6", pad_v=65, pad_h=110),
        make_cell(
            bullet_p("Continuous Monitoring:", "Watches warehouse stock levels and open customer demand 24/7.", sz_pt=9.0)
            + bullet_p("Demand & Supplier Reasoning:", "Runs LSTM forecasts and ranks vendors by cost and lead time.", sz_pt=9.0)
            + bullet_p("Draft Document Prep:", "Populates line items, tax codes, and rationale notes in draft POs.", sz_pt=9.0)
            + bullet_p("3-Way Bill Verification:", "Parses vendor PDFs via VLM and spots billing mismatches via GNN.", sz_pt=9.0, after=0),
            5103, fill="FFFFFF", pad_v=90, pad_h=110,
        )
        + make_cell(
            bullet_p("Budget & Policy Approval:", "Reviews and approves draft orders above configured spend caps.", sz_pt=9.0)
            + bullet_p("Override & Feedback:", "Rejects or edits quantities when real-world business context changes.", sz_pt=9.0)
            + bullet_p("Physical QA Inspection:", "Warehouse staff verify delivered goods and log damaged items in GRN.", sz_pt=9.0)
            + bullet_p("Final Treasury Release:", "Finance Controller authorizes vendor NEFT/RTGS bank settlement.", sz_pt=9.0, after=0),
            5103, fill="FFFFFF", pad_v=90, pad_h=110,
        ),
    ]
    parts.append(make_table([5103, 5103], flow_rows))
    parts.append(page_break_p())

    # PAGE 7: TRUST & SECURITY + PRICING PLANS
    parts.append(sec_heading("7. Trust, Security & Governance"))
    trust_bdr = {"top": ("single", 4, "808080"), "right": ("single", 4, "808080"), "bottom": ("single", 4, "808080"), "left": ("single", 20, "000000")}
    trust_quote = (
        p_xml(run_xml("Autonomous Intelligence. Accountable Decisions.", sz_pt=10.8, bold=True), after=30)
        + p_xml(
            run_xml('"NEXORA combines autonomous intelligence with human accountability." ', sz_pt=9.4, italic=True)
            + run_xml("Operational data stays strictly isolated per tenant, and every AI action operates within hard policy rules defined by your finance and IT leadership.", sz_pt=9.4),
            after=0,
        )
    )
    parts.append(make_table([W_TOT], [make_cell(trust_quote, W_TOT, fill="F2F2F2", borders=trust_bdr, pad_v=75, pad_h=115)], outer_border_color=None))
    parts.append(p_xml("", before=0, after=55))

    sec_rows = [
        make_cell(p_xml(run_xml("Security Control Pillar", sz_pt=9.0, bold=True), after=0), 3000, fill="E6E6E6", pad_v=60, pad_h=90)
        + make_cell(p_xml(run_xml("How Data & AI Actions Stay Controlled", sz_pt=9.0, bold=True), after=0), 7206, fill="E6E6E6", pad_v=60, pad_h=90),
        make_cell(p_xml(run_xml("1. Data Encryption & Isolation", sz_pt=8.9, bold=True), after=0), 3000, fill="FFFFFF", pad_v=65, pad_h=90)
        + make_cell(p_xml(run_xml("AES-256 encryption at rest for relational records and invoice PDFs; TLS 1.3 in transit across web portals and edge MQTT brokers. Optional private VPC / on-premise hosting prevents external model training on company data.", sz_pt=8.9), after=0, line=240), 7206, fill="FFFFFF", pad_v=65, pad_h=90),
        make_cell(p_xml(run_xml("2. Role-Based Access Control (RBAC)", sz_pt=8.9, bold=True), after=0), 3000, fill="F7F7F7", pad_v=65, pad_h=90)
        + make_cell(p_xml(run_xml("Granular document and field permissions enforce separation of duties: warehouse operators cannot approve purchase budgets, and procurement buyers cannot alter vendor bank master details.", sz_pt=8.9), after=0, line=240), 7206, fill="F7F7F7", pad_v=65, pad_h=90),
        make_cell(p_xml(run_xml("3. Hard Financial Spend Caps", sz_pt=8.9, bold=True), after=0), 3000, fill="FFFFFF", pad_v=65, pad_h=90)
        + make_cell(p_xml(run_xml("Administrators set clear monetary limits (e.g., max \u20b950,000 auto-PO per week). Any higher commitment automatically locks execution and escalates to designated managers.", sz_pt=8.9), after=0, line=240), 7206, fill="FFFFFF", pad_v=65, pad_h=90),
        make_cell(p_xml(run_xml("4. Audit Trails & Kill-Switch", sz_pt=8.9, bold=True), after=0), 3000, fill="F7F7F7", pad_v=65, pad_h=90)
        + make_cell(p_xml(run_xml("Every agent recommendation stores its input snapshot, confidence score, and human approver timestamp. A one-click pause switch reverts any module back to manual workflow instantly.", sz_pt=8.9), after=0, line=240), 7206, fill="F7F7F7", pad_v=65, pad_h=90),
    ]
    parts.append(make_table([3000, 7206], sec_rows))

    parts.append(sec_heading("8. Software Pricing Plans & Packages", before=130, after=55))
    parts.append(p_xml(run_xml("Transparent annual or monthly per-company licensing, inclusive of software updates, security patches, and full SQL export ownership.", sz_pt=9.5), after=70))
    pricing_rows = [
        ("Package Comparison", "Starter\nSmall Businesses", "Growth (Recommended)\nMid-Market Factories", "Enterprise\nMulti-Plant Groups"),
        ("Monthly Licensing", "\u20b945,000 / month", "\u20b91,25,000 / month", "Custom Annual Quote"),
        ("Included User Seats", "Up to 25 Active Users", "Up to 150 Active Users", "Unlimited Users & Plants"),
        ("ERP Modules Included", "Sales, Procurement, Inventory, Finance (4 Core)", "All 8 Modules (Full Suite + WH, Production, QA, HR)", "All 8 Modules + Multi-Company Consolidation"),
        ("Agentic AI Suite", "Financial Guardian (VLM Invoice Match, 10k runs/mo)", "All 3 AI Agents (1,00,000 agent runs/mo)", "Unlimited Inference + Custom Edge CNN Tuning"),
        ("Implementation & Support", "CSV Migration Tool + Email Helpdesk", "Dedicated Onboarding Engineer + 99.9% SLA", "Private VPC / On-Prem Setup + 24/7 Architect SLA"),
    ]
    p_xml_rows = []
    for r_i, (p0, p1, p2, p3) in enumerate(pricing_rows):
        hdr = r_i == 0
        bdr_growth = {"top": ("single", 16, "000000") if hdr else ("single", 6, "000000"), "bottom": ("single", 6, "000000"), "left": ("single", 6, "000000"), "right": ("single", 6, "000000")}
        f0 = "E6E6E6" if hdr else ("F7F7F7" if r_i % 2 == 0 else "FFFFFF")
        f2 = "D9D9D9" if hdr else ("F2F2F2" if r_i % 2 == 0 else "FFFFFF")
        p_xml_rows.append(
            make_cell(p_xml(run_xml(p0, sz_pt=8.7, bold=True), after=0), 2300, fill=f0, pad_v=65, pad_h=85)
            + make_cell(p_xml(run_xml(p1, sz_pt=8.7, bold=(r_i in (0, 1))), after=0, line=235), 2450, fill=f0, pad_v=65, pad_h=85)
            + make_cell(p_xml(run_xml(p2, sz_pt=8.7, bold=(r_i in (0, 1))), after=0, line=235), 2856, fill=f2, borders=bdr_growth, pad_v=65, pad_h=85)
            + make_cell(p_xml(run_xml(p3, sz_pt=8.7, bold=(r_i in (0, 1))), after=0, line=235), 2600, fill=f0, pad_v=65, pad_h=85)
        )
    parts.append(make_table([2300, 2450, 2856, 2600], p_xml_rows))
    parts.append(page_break_p())

    # PAGE 8: BACK COVER (STUDENT OFFICERS, CONTACTS & REFERENCE URLS)
    parts.append(sec_heading("9. Executive Leadership Team (Student Officers)"))
    parts.append(p_xml(run_xml("NEXORA is led by its four founding student officers overseeing product engineering, agentic AI research, enterprise database systems, and operational delivery:", sz_pt=9.6), after=75))

    officers = [
        ("Eshaan", "Founder & Chief Executive Officer (CEO)", "Product strategy, customer partnerships & executive governance."),
        ("Srujan", "Chief Technology Officer (CTO)", "Distributed ERP core, SQL databases, API security & telemetry pipelines."),
        ("Abhay", "Chief AI Officer (CAIO)", "LSTM demand modeling, edge MQTT + CNN vision & VLM/GNN guardrails."),
        ("Siri", "Chief Operating Officer (COO)", "Module architecture, client onboarding, QA compliance & finance workflows."),
    ]
    off_rows = [
        make_cell(p_xml(run_xml("Student Name", sz_pt=9.0, bold=True), after=0), 1500, fill="E6E6E6", pad_v=60, pad_h=85)
        + make_cell(p_xml(run_xml("SRN", sz_pt=9.0, bold=True), after=0), 1900, fill="E6E6E6", pad_v=60, pad_h=85)
        + make_cell(p_xml(run_xml("Executive Title", sz_pt=9.0, bold=True), after=0), 2900, fill="E6E6E6", pad_v=60, pad_h=85)
        + make_cell(p_xml(run_xml("Primary Focus", sz_pt=9.0, bold=True), after=0), 3906, fill="E6E6E6", pad_v=60, pad_h=85)
    ]
    for idx, (nm, role, bio) in enumerate(officers):
        srn = emp_by_name.get(nm.lower(), "PES1UG24CS000")
        f_r = "F7F7F7" if idx % 2 == 1 else "FFFFFF"
        off_rows.append(
            make_cell(p_xml(run_xml(nm, sz_pt=9.2, bold=True), after=0), 1500, fill=f_r, pad_v=65, pad_h=85)
            + make_cell(p_xml(run_xml(srn, font="Consolas", sz_pt=8.7), after=0), 1900, fill=f_r, pad_v=65, pad_h=85)
            + make_cell(p_xml(run_xml(role, sz_pt=8.9), after=0), 2900, fill=f_r, pad_v=65, pad_h=85)
            + make_cell(p_xml(run_xml(bio, sz_pt=8.7), after=0, line=235), 3906, fill=f_r, pad_v=65, pad_h=85)
        )
    parts.append(make_table([1500, 1900, 2900, 3906], off_rows))

    parts.append(sec_heading("10. Contact Us & Request a Live Product Demo", before=140, after=60))
    contact_left = make_cell(
        p_xml(run_xml("NEXORA Enterprise Systems Pvt. Ltd.", sz_pt=9.8, bold=True), after=35)
        + p_xml(run_xml("Suite 402, Bellandur Innovation Hub, Outer Ring Road,\nBengaluru - 560103, Karnataka, India", sz_pt=9.0), after=0, line=245),
        5200, fill="FFFFFF", pad_v=90, pad_h=110,
    )
    contact_right = make_cell(
        p_xml(run_xml("Sales Inquiries: ", sz_pt=8.9, bold=True) + run_xml("sales@nexora-ebs.example.com", font="Consolas", sz_pt=8.5), after=25)
        + p_xml(run_xml("Support Desk: ", sz_pt=8.9, bold=True) + run_xml("support@nexora-ebs.example.com", font="Consolas", sz_pt=8.5), after=25)
        + p_xml(run_xml("Web Portal: ", sz_pt=8.9, bold=True) + run_xml("https://nexora-ebs.example.com", font="Consolas", sz_pt=8.5, underline=True), after=25)
        + p_xml(run_xml("Local HTML Brochure: ", sz_pt=8.9, bold=True) + run_xml("nexora_brochure_standalone.html", font="Consolas", sz_pt=8.5), after=0),
        5006, fill="FFFFFF", pad_v=90, pad_h=110,
    )
    parts.append(make_table([5200, 5006], [contact_left + contact_right]))

    parts.append(sec_heading("11. Information Sources & Reference URLs", before=140, after=60))
    refs_inner = (
        p_xml(run_xml("Per project documentation guidelines, technical concepts, ERP module structures, neural architectures, and AI guardrail standards referenced in this brochure were sourced from:", sz_pt=8.9), after=50)
        + bullet_p("Open-Source ERP Module Structures:", "https://docs.erpnext.com and https://erpnext.com", sz_pt=8.7)
        + bullet_p("Deep Learning Models (LSTM & CNN Vision):", "https://pytorch.org/docs/stable/", sz_pt=8.7)
        + bullet_p("Graph Neural Networks (3-Way Match & Anomalies):", "https://pytorch-geometric.readthedocs.io", sz_pt=8.7)
        + bullet_p("Industrial IoT Edge Telemetry Standard (MQTT):", "https://mqtt.org", sz_pt=8.7)
        + bullet_p("AI Risk Management & Human-in-the-Loop Governance:", "https://www.nist.gov/itl/ai-risk-management-framework", sz_pt=8.7)
        + bullet_p("Enterprise Application & RBAC Security Guidelines:", "https://owasp.org/www-project-top-ten/", sz_pt=8.7, after=0)
    )
    parts.append(make_table([W_TOT], [make_cell(refs_inner, W_TOT, fill="FFFFFF", pad_v=90, pad_h=115)]))

    parts.append(p_xml("", before=180, after=0))
    back_bdrs = {"top": ("single", 12, "000000"), "bottom": ("single", 12, "000000"), "left": None, "right": None}
    parts.append(
        make_table(
            [5606, 4600],
            [
                make_cell(p_xml(run_xml("NEXORA \u2014 Intelligence That Runs Your Enterprise.", sz_pt=9.0, bold=True), after=0), 5606, fill="F2F2F2", borders=back_bdrs, pad_v=80, pad_h=100)
                + make_cell(p_xml(run_xml("UE24CS343AB8 (Part B) \u2022 Independent Concept Brochure", sz_pt=8.6), align="right", after=0), 4600, fill="F2F2F2", borders=back_bdrs, pad_v=80, pad_h=100)
            ],
            outer_border_color=None,
        )
    )

    sect_pr = (
        '<w:sectPr>'
        '<w:headerReference w:type="default" r:id="rId2"/>'
        '<w:footerReference w:type="default" r:id="rId3"/>'
        '<w:pgSz w:w="11906" w:h="16838"/>'
        '<w:pgMar w:top="700" w:right="850" w:bottom="660" w:left="850" w:header="360" w:footer="360" w:gutter="0"/>'
        '<w:cols w:space="720"/>'
        '<w:titlePg/>'
        '</w:sectPr>'
    )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document '
        'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
        'xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" '
        'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
        'xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture">'
        f'<w:body>{"".join(parts)}{sect_pr}</w:body>'
        '</w:document>'
    )


def build_styles_xml():
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:docDefaults>
    <w:rPrDefault>
      <w:rPr>
        <w:rFonts w:ascii="Calibri" w:hAnsi="Calibri" w:cs="Calibri"/>
        <w:color w:val="000000"/>
        <w:sz w:val="20"/>
        <w:szCs w:val="20"/>
      </w:rPr>
    </w:rPrDefault>
    <w:pPrDefault>
      <w:pPr>
        <w:spacing w:after="60" w:line="255" w:lineRule="auto"/>
      </w:pPr>
    </w:pPrDefault>
  </w:docDefaults>
  <w:style w:type="paragraph" w:default="1" w:styleId="Normal">
    <w:name w:val="Normal"/>
  </w:style>
</w:styles>
"""


def build_header_xml():
    c1 = make_cell(p_xml(run_xml("NEXORA \u2014 AI-Native Enterprise Business System", sz_pt=8.4, bold=True, color="000000"), after=0), 6206, borders={"top": None, "left": None, "right": None, "bottom": ("single", 8, "000000")}, pad_v=40, pad_h=0)
    c2 = make_cell(p_xml(run_xml("Digital Sales Brochure (Part B)", sz_pt=8.4, color="333333"), align="right", after=0), 4000, borders={"top": None, "left": None, "right": None, "bottom": ("single", 8, "000000")}, pad_v=40, pad_h=0)
    tbl = make_table([6206, 4000], [c1 + c2], outer_border_color=None)
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:hdr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        f'{tbl}{p_xml("", before=0, after=0, line=20)}</w:hdr>'
    )


def build_footer_xml():
    def fld(name):
        return (
            f'<w:r><w:rPr><w:color w:val="4D4D4D"/><w:sz w:val="17"/></w:rPr><w:fldChar w:fldCharType="begin"/></w:r>'
            f'<w:r><w:instrText xml:space="preserve"> {name} </w:instrText></w:r>'
            f'<w:r><w:fldChar w:fldCharType="separate"/></w:r>'
            f'<w:r><w:rPr><w:color w:val="4D4D4D"/><w:sz w:val="17"/></w:rPr><w:t>1</w:t></w:r>'
            f'<w:r><w:fldChar w:fldCharType="end"/></w:r>'
        )

    c1 = make_cell(
        p_xml(run_xml("UE24CS343AB8 Digital Sales Brochure", sz_pt=8.4, color="4D4D4D"), after=0),
        7406,
        borders={"top": ("single", 6, "808080"), "left": None, "right": None, "bottom": None},
        pad_v=45,
        pad_h=0,
    )
    c2 = make_cell(
        p_xml(
            run_xml("Page ", sz_pt=8.4, color="4D4D4D") + fld("PAGE") + run_xml(" of ", sz_pt=8.4, color="4D4D4D") + fld("NUMPAGES"),
            align="right",
            after=0,
        ),
        2800,
        borders={"top": ("single", 6, "808080"), "left": None, "right": None, "bottom": None},
        pad_v=45,
        pad_h=0,
    )
    tbl = make_table([7406, 2800], [c1 + c2], outer_border_color=None)
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:ftr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        f'{tbl}{p_xml("", before=0, after=0, line=20)}</w:ftr>'
    )


def build_content_types_xml():
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Default Extension="png" ContentType="image/png"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  <Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
  <Override PartName="/word/header1.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.header+xml"/>
  <Override PartName="/word/footer1.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml"/>
</Types>
"""


def build_root_rels_xml():
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>
"""


def build_doc_rels_xml(assets):
    img_rels = "".join(
        f'<Relationship Id="{info["rid"]}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/{info["fname"]}"/>'
        for info in assets.values()
    )
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/header" Target="header1.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/footer" Target="footer1.xml"/>
  {img_rels}
</Relationships>
"""


def generate_part_b_docx(data=None):
    global _DOC_IMG_SEQ
    _DOC_IMG_SEQ = 1
    if data is None:
        init_database()
        data = fetch_dashboard_payload()

    browser = find_browser()
    if not browser:
        raise RuntimeError("Chrome or Edge headless binary not found for rendering diagram PNGs.")

    os.makedirs(PDF_DIR, exist_ok=True)
    assets = render_all_brochure_assets(browser)

    docx_name = "EBS24CS-P02 001-002-003-004 NEXORA.docx"
    out_pdfs_docx = os.path.join(PDF_DIR, docx_name)
    out_root_docx = os.path.join(ROOT_SUBMISSION_DIR, docx_name)

    with zipfile.ZipFile(out_pdfs_docx, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", build_content_types_xml())
        zf.writestr("_rels/.rels", build_root_rels_xml())
        zf.writestr("word/_rels/document.xml.rels", build_doc_rels_xml(assets))
        zf.writestr("word/styles.xml", build_styles_xml())
        zf.writestr("word/header1.xml", build_header_xml())
        zf.writestr("word/footer1.xml", build_footer_xml())
        zf.writestr("word/document.xml", build_document_xml(data, assets))
        for info in assets.values():
            zf.write(info["path"], f"word/media/{info['fname']}")

    shutil.copy2(out_pdfs_docx, out_root_docx)
    print(f"[OK] Part B B&W DOCX: {out_pdfs_docx} ({os.path.getsize(out_pdfs_docx)} bytes)")
    print(f"[OK] Part B B&W DOCX copy: {out_root_docx}")
    return out_pdfs_docx


if __name__ == "__main__":
    generate_part_b_docx()
