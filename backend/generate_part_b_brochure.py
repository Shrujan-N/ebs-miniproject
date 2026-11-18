"""
Part B Digital Sales Brochure Generator (Black & White Student Booklet, 8 Pages A4)
Course: UE24CS343AB8 Enterprise Business Systems
Strictly follows: D:\\university\\sem 5\\EBS\\miniproject\\student handbook ebs.pdf (Part B)
- Pure Black & White / Grayscale aesthetic (no colors, classic student MS Word / Docs look)
- Independent of Part A (Note #1)
- Minimum 6 pages -> 8 balanced A4 pages
"""

import html as html_lib


def esc(val):
    return html_lib.escape(str(val))


def brochure_css():
    """Clean Black & White student booklet CSS (no colors, no decorative cards/gradients)."""
    return """
    @page {
        size: A4 portrait;
        margin: 0;
    }
    * {
        box-sizing: border-box;
        margin: 0;
        padding: 0;
    }
    html, body {
        background-color: #FFFFFF;
        color: #000000;
        font-family: "Calibri", "Times New Roman", Arial, sans-serif;
        font-size: 10pt;
        line-height: 1.42;
        -webkit-print-color-adjust: exact !important;
        print-color-adjust: exact !important;
    }
    .b-page {
        width: 210mm;
        height: 297mm;
        padding: 15mm 17mm 14mm 17mm;
        background-color: #FFFFFF;
        position: relative;
        overflow: hidden;
        page-break-after: always;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .b-page:last-child {
        page-break-after: auto;
    }

    /* Simple Black & White Running Header & Footer */
    .b-hdr {
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1pt solid #000000;
        padding-bottom: 4pt;
        margin-bottom: 10pt;
        font-size: 8.5pt;
        color: #333333;
        flex-shrink: 0;
    }
    .b-hdr-brand {
        font-weight: 700;
        color: #000000;
    }
    .b-body {
        flex: 1;
        display: flex;
        flex-direction: column;
        gap: 8pt;
        min-height: 0;
    }
    .b-ftr {
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-top: 0.75pt solid #808080;
        padding-top: 5pt;
        margin-top: 8pt;
        font-size: 8.5pt;
        color: #4D4D4D;
        flex-shrink: 0;
    }

    /* Classic Student Document Headings & Prose */
    h1.sec-head {
        font-family: "Calibri", "Times New Roman", serif;
        font-size: 14pt;
        font-weight: 700;
        color: #000000;
        border-bottom: 1pt solid #000000;
        padding-bottom: 2.5pt;
        margin-bottom: 3pt;
    }
    h2.sub-head {
        font-size: 11pt;
        font-weight: 700;
        color: #000000;
        margin-top: 4pt;
        margin-bottom: 2pt;
    }
    h3.mini-head {
        font-size: 10pt;
        font-weight: 700;
        color: #000000;
        margin-bottom: 2pt;
    }
    p.prose {
        font-size: 9.8pt;
        color: #000000;
    }
    ul.clean-list {
        list-style: disc;
        padding-left: 16pt;
    }
    ul.clean-list li {
        margin-bottom: 3.5pt;
        font-size: 9.5pt;
        color: #000000;
    }

    /* Plain White & Grayscale Academic Boxes */
    .grid-2 {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 10pt;
    }
    .grid-3 {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 9pt;
    }
    .box-bw {
        border: 0.75pt solid #000000;
        background-color: #FFFFFF;
        padding: 7pt 9pt;
    }
    .box-tint {
        border: 0.75pt solid #000000;
        background-color: #F2F2F2;
        padding: 7pt 9pt;
    }
    .human-note {
        margin-top: 4pt;
        padding: 5pt 8pt;
        background-color: #F2F2F2;
        border-left: 2.5pt solid #000000;
        font-size: 9pt;
        color: #000000;
    }

    /* Visual Frames & Figure Captions */
    .vis-box {
        border: 0.75pt solid #000000;
        background-color: #FFFFFF;
        padding: 6pt 8pt;
    }
    .vis-cap {
        font-size: 9.2pt;
        font-weight: 700;
        color: #000000;
        margin-top: 4pt;
    }
    .vis-blurb {
        font-size: 8.8pt;
        color: #333333;
        font-style: italic;
        margin-top: 1.5pt;
    }

    /* Standard MS Word Black & White Tables */
    table.bro {
        width: 100%;
        border-collapse: collapse;
        font-size: 9pt;
    }
    table.bro th {
        background-color: #E6E6E6;
        color: #000000;
        font-weight: 700;
        text-align: left;
        padding: 5pt 7pt;
        border: 0.75pt solid #000000;
    }
    table.bro td {
        padding: 4.5pt 7pt;
        border: 0.75pt solid #000000;
        color: #000000;
        vertical-align: top;
        background-color: #FFFFFF;
    }
    table.bro tr:nth-child(even) td {
        background-color: #F7F7F7;
    }
    .mono {
        font-family: "Consolas", "Courier New", monospace;
        font-size: 8.4pt;
    }
    .url-txt {
        font-family: "Consolas", monospace;
        font-size: 8.4pt;
        color: #000000;
        text-decoration: underline;
    }
    """


def brochure_page_wrap(body_html, section_label, page_no, total_pages):
    return f"""
    <div class="b-page">
        <div class="b-hdr">
            <span class="b-hdr-brand">NEXORA &#8212; AI-Native Enterprise Business System</span>
            <span>{esc(section_label)}</span>
        </div>
        <div class="b-body">
            {body_html}
        </div>
        <div class="b-ftr">
            <span>UE24CS343AB8 Digital Sales Brochure</span>
            <span>Page {page_no} of {total_pages}</span>
        </div>
    </div>
    """


# =====================================================================
# PURE BLACK & WHITE VECTOR ILLUSTRATIONS (Zero Color Hues)
# =====================================================================

def svg_nexora_brand_mark(size=54):
    """Crisp black-and-white geometric hexagon node logo."""
    return f"""
    <svg viewBox="0 0 64 64" width="{size}" height="{size}" style="display:block; background:#FFFFFF;">
        <polygon points="32,4 58,18 58,46 32,60 6,46 6,18" fill="#FFFFFF" stroke="#000000" stroke-width="3"/>
        <circle cx="32" cy="18" r="5" fill="#000000"/>
        <circle cx="19" cy="41" r="5" fill="#FFFFFF" stroke="#000000" stroke-width="2.5"/>
        <circle cx="45" cy="41" r="5" fill="#FFFFFF" stroke="#000000" stroke-width="2.5"/>
        <line x1="32" y1="22" x2="21" y2="37" stroke="#000000" stroke-width="2.2"/>
        <line x1="32" y1="22" x2="43" y2="37" stroke="#000000" stroke-width="2.2"/>
        <line x1="24" y1="41" x2="40" y2="41" stroke="#000000" stroke-width="2.2"/>
    </svg>
    """


def svg_brochure_ecosystem():
    """Page 1 B&W Cover Schematic: Connected Enterprise Modules + Human Control."""
    return """
    <svg viewBox="0 0 540 218" width="100%" style="background:#FFFFFF; font-family:Calibri,Arial,sans-serif; display:block;">
        <defs>
            <marker id="bwArr" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto">
                <polygon points="0 0, 6 3, 0 6" fill="#000000"/>
            </marker>
        </defs>
        <text x="270" y="16" text-anchor="middle" font-size="10.2" font-weight="bold" fill="#000000">
            NEXORA Connected Enterprise Hub: 8 Modules + 3 Agents + Human Control
        </text>

        <rect x="18" y="34" width="146" height="66" rx="2" fill="#FFFFFF" stroke="#000000" stroke-width="1.2"/>
        <text x="91" y="51" text-anchor="middle" font-size="9.2" font-weight="bold" fill="#000000">Sales &amp; Fulfillment</text>
        <text x="91" y="65" text-anchor="middle" font-size="7.8" fill="#333333">Smart Quotes, CRM Pipeline,</text>
        <text x="91" y="77" text-anchor="middle" font-size="7.8" fill="#333333">GST Billing &amp; Dispatch Plans</text>
        <text x="91" y="91" text-anchor="middle" font-size="7.4" font-weight="bold" fill="#000000">Live Demand Telemetry</text>

        <rect x="376" y="34" width="146" height="66" rx="2" fill="#FFFFFF" stroke="#000000" stroke-width="1.2"/>
        <text x="449" y="51" text-anchor="middle" font-size="9.2" font-weight="bold" fill="#000000">Procurement &amp; WH</text>
        <text x="449" y="65" text-anchor="middle" font-size="7.8" fill="#333333">LSTM Depletion Forecasting,</text>
        <text x="449" y="77" text-anchor="middle" font-size="7.8" fill="#333333">Vendor Ranking &amp; Bin Control</text>
        <text x="449" y="91" text-anchor="middle" font-size="7.4" font-weight="bold" fill="#000000">Auto-Drafts Pending Sign-Off</text>

        <rect x="18" y="136" width="146" height="66" rx="2" fill="#FFFFFF" stroke="#000000" stroke-width="1.2"/>
        <text x="91" y="153" text-anchor="middle" font-size="9.2" font-weight="bold" fill="#000000">Production &amp; Quality</text>
        <text x="91" y="167" text-anchor="middle" font-size="7.8" fill="#333333">IoT MQTT Edge Sensors &amp;</text>
        <text x="91" y="179" text-anchor="middle" font-size="7.8" fill="#333333">CNN Optical Defect Catch</text>
        <text x="91" y="193" text-anchor="middle" font-size="7.4" font-weight="bold" fill="#000000">Supervisor Line Control</text>

        <rect x="376" y="136" width="146" height="66" rx="2" fill="#FFFFFF" stroke="#000000" stroke-width="1.2"/>
        <text x="449" y="153" text-anchor="middle" font-size="9.2" font-weight="bold" fill="#000000">Finance, Audit &amp; HR</text>
        <text x="449" y="167" text-anchor="middle" font-size="7.8" fill="#333333">VLM PDF Invoice Reading &amp;</text>
        <text x="449" y="179" text-anchor="middle" font-size="7.8" fill="#333333">GNN 3-Way Anomaly Checks</text>
        <text x="449" y="193" text-anchor="middle" font-size="7.4" font-weight="bold" fill="#000000">Controller Payment Lock</text>

        <rect x="196" y="72" width="148" height="92" rx="3" fill="#E6E6E6" stroke="#000000" stroke-width="1.8"/>
        <text x="270" y="96" text-anchor="middle" font-size="11.5" font-weight="bold" fill="#000000">NEXORA CORE</text>
        <text x="270" y="111" text-anchor="middle" font-size="8" fill="#1A1A1A">Perceive &#8594; Reason &#8594; Plan</text>
        <rect x="210" y="120" width="120" height="32" rx="2" fill="#FFFFFF" stroke="#000000" stroke-width="1"/>
        <text x="270" y="134" text-anchor="middle" font-size="8.2" font-weight="bold" fill="#000000">Human Governance</text>
        <text x="270" y="145" text-anchor="middle" font-size="7.2" fill="#333333">RBAC + Spend Approval Gate</text>

        <line x1="164" y1="67" x2="196" y2="95" stroke="#000000" stroke-width="1.2" marker-end="url(#bwArr)"/>
        <line x1="376" y1="67" x2="344" y2="95" stroke="#000000" stroke-width="1.2" marker-end="url(#bwArr)"/>
        <line x1="164" y1="169" x2="196" y2="142" stroke="#000000" stroke-width="1.2" marker-end="url(#bwArr)"/>
        <line x1="376" y1="169" x2="344" y2="142" stroke="#000000" stroke-width="1.2" marker-end="url(#bwArr)"/>
    </svg>
    """


def svg_brochure_benchmark_plot():
    """Page 2 B&W Matplotlib-style benchmark bar chart (light grey vs solid black)."""
    w, h = 520, 178
    pl, pt, pr, pb = 160, 28, 30, 30
    pw, ph = w - pl - pr, h - pt - pb
    metrics = [
        ("PO Prep Time (mins)", 42, 4, "42m", "4m"),
        ("Invoice Check (mins)", 25, 2, "25m", "2m"),
        ("Stockout Alerts (/qtr)", 18, 2, "18", "2"),
        ("QC Review Delay (min)", 60, 1, "60m", "<1m"),
    ]
    max_v = 65.0
    step = ph / len(metrics)

    grid = []
    for xfrac in [0, 0.25, 0.5, 0.75, 1.0]:
        gx = pl + pw * xfrac
        grid.append(
            f'<line x1="{gx:.1f}" y1="{pt}" x2="{gx:.1f}" y2="{pt+ph}" stroke="#CCCCCC" stroke-width="0.9" stroke-dasharray="3,2"/>'
            f'<text x="{gx:.1f}" y="{pt+ph+13}" text-anchor="middle" font-size="8" fill="#000000">{int(max_v*xfrac)}</text>'
        )

    rows_svg = []
    for idx, (label, v_old, v_new, t_old, t_new) in enumerate(metrics):
        cy = pt + idx * step + step * 0.5
        w_old = (v_old / max_v) * pw
        w_new = max(4.0, (v_new / max_v) * pw)
        rows_svg.append(
            f'<text x="{pl-7}" y="{cy+3:.1f}" text-anchor="end" font-size="8.4" fill="#000000">{label}</text>'
            f'<rect x="{pl}" y="{cy-9:.1f}" width="{w_old:.1f}" height="8" fill="#B3B3B3" stroke="#000000" stroke-width="0.5"/>'
            f'<text x="{pl+w_old+4:.1f}" y="{cy-2:.1f}" font-size="7.5" fill="#333333">{t_old}</text>'
            f'<rect x="{pl}" y="{cy+1:.1f}" width="{w_new:.1f}" height="8" fill="#1A1A1A" stroke="#000000" stroke-width="0.5"/>'
            f'<text x="{pl+w_new+4:.1f}" y="{cy+8:.1f}" font-size="7.5" font-weight="bold" fill="#000000">{t_new}</text>'
        )

    return f"""
    <svg viewBox="0 0 {w} {h}" width="100%" style="background:#FFFFFF; font-family:Calibri,Arial,sans-serif; display:block;">
        <text x="{w/2:.1f}" y="17" text-anchor="middle" font-size="10" font-weight="bold" fill="#000000">
            Pilot Workflow Time &amp; Exception Reduction (Rule-Based ERP vs. NEXORA)
        </text>
        {"".join(grid)}
        <rect x="{pl}" y="{pt}" width="{pw}" height="{ph}" fill="none" stroke="#000000" stroke-width="1"/>
        {"".join(rows_svg)}
        <rect x="{pl+pw-138}" y="{pt+5}" width="132" height="28" fill="#FFFFFF" stroke="#000000" stroke-width="0.8"/>
        <rect x="{pl+pw-131}" y="{pt+10}" width="10" height="7" fill="#B3B3B3" stroke="#000000" stroke-width="0.5"/>
        <text x="{pl+pw-117}" y="{pt+16.5}" font-size="7.5" fill="#000000">Rule-Based ERP</text>
        <rect x="{pl+pw-131}" y="{pt+21}" width="10" height="7" fill="#1A1A1A" stroke="#000000" stroke-width="0.5"/>
        <text x="{pl+pw-117}" y="{pt+27.5}" font-size="7.5" fill="#000000">NEXORA (Supervised)</text>
    </svg>
    """


def svg_brochure_lstm_forecast():
    """Page 4 Visual 1 (B&W): LSTM Forecast Curve + Draft PO Approval Wireframe."""
    return """
    <svg viewBox="0 0 530 162" width="100%" style="background:#FFFFFF; font-family:Calibri,Arial,sans-serif; display:block;">
        <text x="158" y="15" text-anchor="middle" font-size="9.5" font-weight="bold" fill="#000000">
            LSTM 14-Day Stock Forecast: Actuator #AC-40
        </text>
        <line x1="42" y1="26" x2="288" y2="26" stroke="#E0E0E0" stroke-width="0.8"/>
        <line x1="42" y1="62" x2="288" y2="62" stroke="#E0E0E0" stroke-width="0.8"/>
        <line x1="42" y1="98" x2="288" y2="98" stroke="#E0E0E0" stroke-width="0.8"/>
        <rect x="42" y="24" width="246" height="106" fill="none" stroke="#000000" stroke-width="1"/>
        <line x1="42" y1="92" x2="288" y2="92" stroke="#4D4D4D" stroke-width="1.2" stroke-dasharray="4,3"/>
        <text x="48" y="88" font-size="7.2" font-weight="bold" fill="#000000">Safety Stock Min (60 units)</text>
        <polyline points="42,40 78,48 114,56 150,65 178,72" fill="none" stroke="#000000" stroke-width="2"/>
        <polyline points="178,72 208,85 236,99 266,114 288,123" fill="none" stroke="#000000" stroke-width="1.8" stroke-dasharray="4,2"/>
        <circle cx="222" cy="92" r="4" fill="#000000" stroke="#FFFFFF" stroke-width="1"/>
        <text x="222" y="81" text-anchor="middle" font-size="7.2" font-weight="bold" fill="#000000">Breach (Day 11)</text>
        <text x="42" y="142" font-size="7.5" fill="#333333">Day 1</text>
        <text x="172" y="142" font-size="7.5" fill="#333333">Today</text>
        <text x="262" y="142" font-size="7.5" fill="#333333">Day 14</text>
        <text x="14" y="78" text-anchor="middle" font-size="7.8" fill="#000000" transform="rotate(-90 14 78)">Units</text>

        <rect x="306" y="12" width="214" height="138" rx="2" fill="#FFFFFF" stroke="#000000" stroke-width="1.2"/>
        <rect x="306" y="12" width="214" height="22" fill="#E6E6E6" stroke="#000000" stroke-width="1"/>
        <text x="316" y="26.5" font-size="8.5" font-weight="bold" fill="#000000">Draft PO #NX-PO-408 (Queued)</text>
        <text x="316" y="50" font-size="8" fill="#000000"><tspan font-weight="bold">SKU:</tspan> Servo Actuator #AC-40</text>
        <text x="316" y="65" font-size="8" fill="#000000"><tspan font-weight="bold">Vendor:</tspan> Apex Precision Forgings</text>
        <text x="316" y="80" font-size="8" fill="#000000"><tspan font-weight="bold">Qty / Cost:</tspan> 250 units (&#8377;3,12,000)</text>
        <text x="316" y="95" font-size="8" fill="#000000" font-weight="bold">Rule: Exceeds &#8377;2.5L Auto-Cap</text>
        <rect x="316" y="110" width="90" height="22" rx="2" fill="#F2F2F2" stroke="#000000" stroke-width="1.2"/>
        <text x="361" y="124" text-anchor="middle" font-size="7.8" font-weight="bold" fill="#000000">Approve &amp; Send</text>
        <rect x="414" y="110" width="94" height="22" rx="2" fill="#FFFFFF" stroke="#4D4D4D" stroke-width="1"/>
        <text x="461" y="124" text-anchor="middle" font-size="7.8" font-weight="bold" fill="#333333">Edit / Reject</text>
    </svg>
    """


def svg_brochure_mqtt_cnn():
    """Page 4 Visual 2 (B&W): Edge MQTT Telemetry + CNN Camera Schematic."""
    return """
    <svg viewBox="0 0 530 154" width="100%" style="background:#FFFFFF; font-family:Calibri,Arial,sans-serif; display:block;">
        <rect x="10" y="10" width="236" height="134" rx="2" fill="#FFFFFF" stroke="#000000" stroke-width="1"/>
        <rect x="10" y="10" width="236" height="22" fill="#E6E6E6" stroke="#000000" stroke-width="1"/>
        <text x="20" y="24.5" font-size="8.4" font-weight="bold" fill="#000000">Edge Broker: mqtt://plant-line-b/telemetry</text>
        <text x="20" y="48" font-size="8.2" font-weight="bold" fill="#000000">Live Machine Readings (Last 60s)</text>
        <rect x="20" y="56" width="102" height="36" fill="#FFFFFF" stroke="#808080" stroke-width="0.8"/>
        <text x="28" y="70" font-size="7.2" fill="#4D4D4D">Spindle Temp</text>
        <text x="28" y="84" font-size="10.5" font-weight="bold" fill="#000000">62.4 &#176;C (OK)</text>
        <rect x="132" y="56" width="102" height="36" fill="#FFFFFF" stroke="#808080" stroke-width="0.8"/>
        <text x="140" y="70" font-size="7.2" fill="#4D4D4D">Cycle Vibration</text>
        <text x="140" y="84" font-size="10.5" font-weight="bold" fill="#000000">1.4 mm/s</text>
        <rect x="20" y="100" width="214" height="34" fill="#F2F2F2" stroke="#000000" stroke-width="0.9"/>
        <text x="28" y="114" font-size="7.8" font-weight="bold" fill="#000000">CNN Vision Event (Unit #LN-8824):</text>
        <text x="28" y="126" font-size="7.6" fill="#333333">Paused batch routing for Line Supervisor check.</text>

        <rect x="262" y="10" width="258" height="134" rx="2" fill="#FFFFFF" stroke="#000000" stroke-width="1.2"/>
        <rect x="262" y="10" width="258" height="22" fill="#E6E6E6" stroke="#000000" stroke-width="1"/>
        <text x="272" y="24.5" font-size="8.4" font-weight="bold" fill="#000000">CNN Surface Vision Feed &#8212; Station B2</text>
        <rect x="274" y="42" width="132" height="90" fill="#F7F7F7" stroke="#808080" stroke-width="0.9"/>
        <line x1="288" y1="62" x2="388" y2="62" stroke="#4D4D4D" stroke-width="1.5"/>
        <line x1="288" y1="88" x2="388" y2="88" stroke="#4D4D4D" stroke-width="1.5"/>
        <line x1="288" y1="112" x2="388" y2="112" stroke="#4D4D4D" stroke-width="1.5"/>
        <rect x="305" y="55" width="16" height="14" fill="#1A1A1A"/>
        <rect x="355" y="104" width="16" height="14" fill="#1A1A1A"/>
        <rect x="328" y="76" width="38" height="24" fill="#E6E6E6" fill-opacity="0.6" stroke="#000000" stroke-width="1.6" stroke-dasharray="3,2"/>
        <text x="347" y="72" text-anchor="middle" font-size="7.2" font-weight="bold" fill="#000000">Micro-Crack (96%)</text>
        <text x="416" y="54" font-size="8" font-weight="bold" fill="#000000">Recommended Action:</text>
        <text x="416" y="68" font-size="7.6" fill="#333333">Quarantine Lot #B2-19</text>
        <text x="416" y="80" font-size="7.6" fill="#333333">&amp; adjust feed torque.</text>
        <rect x="416" y="92" width="94" height="18" rx="2" fill="#F2F2F2" stroke="#000000" stroke-width="1"/>
        <text x="463" y="104" text-anchor="middle" font-size="7.3" font-weight="bold" fill="#000000">Supervisor: Divert Lot</text>
        <rect x="416" y="114" width="94" height="18" rx="2" fill="#FFFFFF" stroke="#4D4D4D" stroke-width="0.9"/>
        <text x="463" y="126" text-anchor="middle" font-size="7.3" font-weight="bold" fill="#333333">Mark False Positive</text>
    </svg>
    """


def svg_brochure_gnn_match():
    """Page 5 Visual (B&W): Financial Guardian VLM + GNN 3-Way Match Node Graph."""
    return """
    <svg viewBox="0 0 530 165" width="100%" style="background:#FFFFFF; font-family:Calibri,Arial,sans-serif; display:block;">
        <defs>
            <marker id="gnBw" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto">
                <polygon points="0 0, 6 3, 0 6" fill="#000000"/>
            </marker>
        </defs>
        <text x="265" y="16" text-anchor="middle" font-size="9.8" font-weight="bold" fill="#000000">
            Financial Guardian Agent: VLM Extraction &amp; GNN 3-Way Verification Graph
        </text>

        <rect x="16" y="34" width="144" height="58" rx="2" fill="#FFFFFF" stroke="#000000" stroke-width="1.2"/>
        <text x="88" y="50" text-anchor="middle" font-size="8.6" font-weight="bold" fill="#000000">1. Approved PO #884</text>
        <text x="88" y="64" text-anchor="middle" font-size="7.8" fill="#333333">100 Valve Bodies @ &#8377;1,800</text>
        <text x="88" y="77" text-anchor="middle" font-size="7.8" font-weight="bold" fill="#000000">Contracted Total: &#8377;1,80,000</text>

        <rect x="16" y="104" width="144" height="52" rx="2" fill="#FFFFFF" stroke="#000000" stroke-width="1.2"/>
        <text x="88" y="120" text-anchor="middle" font-size="8.6" font-weight="bold" fill="#000000">2. Warehouse GRN</text>
        <text x="88" y="133" text-anchor="middle" font-size="7.8" fill="#333333">92 Units Passed QA</text>
        <text x="88" y="146" text-anchor="middle" font-size="7.6" font-weight="bold" fill="#333333">8 Damaged on Delivery</text>

        <rect x="196" y="54" width="136" height="84" rx="2" fill="#F2F2F2" stroke="#000000" stroke-width="1.5"/>
        <text x="264" y="73" text-anchor="middle" font-size="9" font-weight="bold" fill="#000000">VLM + GNN Engine</text>
        <text x="264" y="88" text-anchor="middle" font-size="7.6" fill="#333333">Cross-checks Qty, Rate,</text>
        <text x="264" y="99" text-anchor="middle" font-size="7.6" fill="#333333">GSTIN &amp; Extra Charges</text>
        <rect x="208" y="108" width="112" height="20" rx="2" fill="#FFFFFF" stroke="#000000" stroke-width="1.2"/>
        <text x="264" y="121" text-anchor="middle" font-size="7.6" font-weight="bold" fill="#000000">ANOMALY: +&#8377;23,900</text>

        <rect x="368" y="34" width="146" height="58" rx="2" fill="#FFFFFF" stroke="#000000" stroke-width="1.2" stroke-dasharray="4,2"/>
        <text x="441" y="50" text-anchor="middle" font-size="8.6" font-weight="bold" fill="#000000">3. Supplier PDF (VLM Read)</text>
        <text x="441" y="64" text-anchor="middle" font-size="7.8" fill="#333333">Billed 100 pcs + &#8377;9,500 Fee</text>
        <text x="441" y="77" text-anchor="middle" font-size="7.8" font-weight="bold" fill="#000000">Invoiced: &#8377;1,89,500</text>

        <rect x="368" y="104" width="146" height="52" rx="2" fill="#F2F2F2" stroke="#000000" stroke-width="1.2"/>
        <text x="441" y="120" text-anchor="middle" font-size="8.4" font-weight="bold" fill="#000000">Finance Controller Hold</text>
        <text x="441" y="133" text-anchor="middle" font-size="7.5" fill="#333333">[Pay 92 Accepted (&#8377;1,65,600)]</text>
        <text x="441" y="145" text-anchor="middle" font-size="7.5" fill="#000000">[Dispute &amp; Issue Debit Note]</text>

        <line x1="160" y1="63" x2="195" y2="82" stroke="#000000" stroke-width="1.1" marker-end="url(#gnBw)"/>
        <line x1="160" y1="128" x2="195" y2="108" stroke="#000000" stroke-width="1.1" marker-end="url(#gnBw)"/>
        <line x1="368" y1="63" x2="333" y2="82" stroke="#000000" stroke-width="1.2" marker-end="url(#gnBw)"/>
        <line x1="332" y1="122" x2="366" y2="128" stroke="#000000" stroke-width="1.2" marker-end="url(#gnBw)"/>
    </svg>
    """


def svg_brochure_p2p_flowchart():
    """Page 6 Visual (B&W): Clean Swimlane Business Process Flowchart."""
    return """
    <svg viewBox="0 0 530 278" width="100%" style="background:#FFFFFF; font-family:Calibri,Arial,sans-serif; display:block;">
        <defs>
            <marker id="pfBw" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto">
                <polygon points="0 0, 6 3, 0 6" fill="#000000"/>
            </marker>
        </defs>

        <rect x="8" y="8" width="514" height="114" rx="2" fill="#FFFFFF" stroke="#000000" stroke-width="1"/>
        <text x="18" y="24" font-size="8.5" font-weight="bold" fill="#000000">STEPS HANDLED BY AI AGENTS (AUTONOMOUS SPEED)</text>

        <rect x="8" y="136" width="514" height="134" rx="2" fill="#F2F2F2" stroke="#000000" stroke-width="1"/>
        <text x="18" y="152" font-size="8.5" font-weight="bold" fill="#000000">STEPS HANDLED BY PEOPLE (HUMAN APPROVAL)</text>

        <rect x="18" y="36" width="110" height="68" rx="2" fill="#FFFFFF" stroke="#000000" stroke-width="1.2"/>
        <text x="73" y="53" text-anchor="middle" font-size="8.4" font-weight="bold" fill="#000000">1. Sense Stock</text>
        <text x="73" y="67" text-anchor="middle" font-size="7.4" fill="#333333">Tracks live bin balance</text>
        <text x="73" y="79" text-anchor="middle" font-size="7.4" fill="#333333">&amp; open sales pipeline</text>
        <text x="73" y="94" text-anchor="middle" font-size="7" font-weight="bold" fill="#000000">[AI Monitor]</text>

        <rect x="144" y="36" width="112" height="68" rx="2" fill="#FFFFFF" stroke="#000000" stroke-width="1.2"/>
        <text x="200" y="53" text-anchor="middle" font-size="8.4" font-weight="bold" fill="#000000">2. Forecast &amp; Rank</text>
        <text x="200" y="67" text-anchor="middle" font-size="7.4" fill="#333333">LSTM predicts runout;</text>
        <text x="200" y="79" text-anchor="middle" font-size="7.4" fill="#333333">scores trusted vendors</text>
        <text x="200" y="94" text-anchor="middle" font-size="7" font-weight="bold" fill="#000000">[AI Planning]</text>

        <rect x="272" y="36" width="112" height="68" rx="2" fill="#FFFFFF" stroke="#000000" stroke-width="1.2"/>
        <text x="328" y="53" text-anchor="middle" font-size="8.4" font-weight="bold" fill="#000000">3. Draft Order</text>
        <text x="328" y="67" text-anchor="middle" font-size="7.4" fill="#333333">Prepares PO + rationale</text>
        <text x="328" y="79" text-anchor="middle" font-size="7.4" fill="#333333">&amp; queues for approval</text>
        <text x="328" y="94" text-anchor="middle" font-size="7" font-weight="bold" fill="#000000">[AI Execution]</text>

        <rect x="400" y="36" width="112" height="68" rx="2" fill="#FFFFFF" stroke="#000000" stroke-width="1.2"/>
        <text x="456" y="53" text-anchor="middle" font-size="8.4" font-weight="bold" fill="#000000">6. 3-Way Match</text>
        <text x="456" y="67" text-anchor="middle" font-size="7.4" fill="#333333">VLM scans bill PDF;</text>
        <text x="456" y="79" text-anchor="middle" font-size="7.4" fill="#333333">GNN checks anomalies</text>
        <text x="456" y="94" text-anchor="middle" font-size="7" font-weight="bold" fill="#000000">[AI Audit]</text>

        <rect x="136" y="176" width="120" height="58" rx="2" fill="#FFFFFF" stroke="#000000" stroke-width="1.1" stroke-dasharray="3,2"/>
        <text x="196" y="195" text-anchor="middle" font-size="8.2" font-weight="bold" fill="#000000">Rejected / Adjusted</text>
        <text x="196" y="209" text-anchor="middle" font-size="7.3" fill="#333333">Logs manager note &amp;</text>
        <text x="196" y="221" text-anchor="middle" font-size="7.3" fill="#333333">retrains agent preferences</text>

        <polygon points="328,162 378,205 328,248 278,205" fill="#FFFFFF" stroke="#000000" stroke-width="1.5"/>
        <text x="328" y="199" text-anchor="middle" font-size="8.2" font-weight="bold" fill="#000000">4. Manager</text>
        <text x="328" y="211" text-anchor="middle" font-size="8.2" font-weight="bold" fill="#000000">Approval Gate</text>
        <text x="328" y="224" text-anchor="middle" font-size="7" fill="#333333">Verify Budget</text>

        <rect x="394" y="160" width="94" height="44" rx="2" fill="#FFFFFF" stroke="#000000" stroke-width="1.2"/>
        <text x="441" y="177" text-anchor="middle" font-size="7.9" font-weight="bold" fill="#000000">5. QA Receive (GRN)</text>
        <text x="441" y="191" text-anchor="middle" font-size="7.1" fill="#333333">Staff inspects goods</text>

        <rect x="394" y="216" width="94" height="44" rx="2" fill="#FFFFFF" stroke="#000000" stroke-width="1.2"/>
        <text x="441" y="233" text-anchor="middle" font-size="7.9" font-weight="bold" fill="#000000">7. Pay Release</text>
        <text x="441" y="247" text-anchor="middle" font-size="7.1" fill="#333333">Controller signs NEFT</text>

        <line x1="128" y1="70" x2="142" y2="70" stroke="#000000" stroke-width="1.2" marker-end="url(#pfBw)"/>
        <line x1="256" y1="70" x2="270" y2="70" stroke="#000000" stroke-width="1.2" marker-end="url(#pfBw)"/>
        <line x1="328" y1="104" x2="328" y2="160" stroke="#000000" stroke-width="1.3" marker-end="url(#pfBw)"/>
        <line x1="278" y1="205" x2="258" y2="205" stroke="#000000" stroke-width="1.2" marker-end="url(#pfBw)"/>
        <text x="268" y="198" text-anchor="middle" font-size="7" font-weight="bold" fill="#000000">No</text>
        <line x1="244" y1="176" x2="244" y2="106" stroke="#000000" stroke-width="1.1" stroke-dasharray="3,2" marker-end="url(#pfBw)"/>
        <line x1="378" y1="196" x2="392" y2="188" stroke="#000000" stroke-width="1.3" marker-end="url(#pfBw)"/>
        <text x="382" y="182" text-anchor="middle" font-size="7.2" font-weight="bold" fill="#000000">Yes</text>
        <path d="M 441 160 L 441 106" fill="none" stroke="#000000" stroke-width="1.2" marker-end="url(#pfBw)"/>
        <path d="M 502 104 L 502 238 L 490 238" fill="none" stroke="#000000" stroke-width="1.2" marker-end="url(#pfBw)"/>
    </svg>
    """


# =====================================================================
# 8-PAGE BLACK & WHITE STUDENT BROCHURE BUILDER
# =====================================================================

def build_part_b_brochure(data):
    """Build 8 clean Black & White A4 pages matching student Word style & Part B handbook."""
    total_pages = 8
    pages = []

    emp_by_name = {}
    for emp in data["employees"]:
        nm = emp["employee_name"].split("(")[0].strip().lower()
        emp_by_name[nm] = emp["srn"]

    # PAGE 1: Front Cover
    p1 = f"""
    <div class="b-page" style="background:#FFFFFF;">
        <div>
            <div style="border-top:2pt solid #000000; border-bottom:2pt solid #000000; padding:10pt 0; display:flex; justify-content:space-between; align-items:center;">
                <div style="display:flex; align-items:center; gap:12pt;">
                    {svg_nexora_brand_mark(46)}
                    <div>
                        <div style="font-size:20pt; font-weight:700; color:#000000; letter-spacing:1pt;">NEXORA</div>
                        <div style="font-size:8.8pt; color:#333333;">AI-NATIVE ENTERPRISE BUSINESS SYSTEM</div>
                    </div>
                </div>
                <div style="text-align:right; font-size:8.8pt; color:#000000;">
                    <div><b>Product Sales Brochure</b></div>
                    <div>UE24CS343AB8 (Part B)</div>
                </div>
            </div>

            <div style="margin-top:16pt;">
                <div style="font-size:9.5pt; font-weight:700; color:#333333; letter-spacing:0.5pt; margin-bottom:4pt;">
                    INTELLIGENCE THAT RUNS YOUR ENTERPRISE.
                </div>
                <div style="font-size:23pt; font-weight:700; color:#000000; line-height:1.18; margin-bottom:10pt;">
                    Your Enterprise.<br>Reimagined with Intelligence.
                </div>
                <p class="prose" style="font-size:10.3pt; margin-bottom:12pt;">
                    Most business software only records transactions after problems have already occurred.
                    <b>NEXORA</b> is an AI-native Enterprise Business System designed for growing manufacturers and B2B distributors.
                    Specialized AI agents monitor stock depletion, watch assembly quality, and audit supplier invoices, while human managers retain final approval authority over every financial commitment.
                </p>
            </div>

            <div class="vis-box" style="margin-top:4pt;">
                {svg_brochure_ecosystem()}
            </div>
            <div class="vis-cap">Figure 1: Connected NEXORA Enterprise Architecture with Human Governance</div>
            <div class="vis-blurb">
                "Every department shares one live operational ledger: autonomous agents prepare routine procurement, production, and invoice work, while role-based approvals ensure complete management control."
            </div>

            <table class="bro" style="margin-top:12pt;">
                <tr>
                    <th style="width:33.3%;">8 Core Modules</th>
                    <th style="width:33.3%;">3 Agentic AI Engines</th>
                    <th style="width:33.4%;">Human-First Guardrails</th>
                </tr>
                <tr>
                    <td>Sales, Procurement, Inventory, Warehouse (WH), Production, Quality, Finance, and HR.</td>
                    <td>LSTM demand planning, MQTT + CNN visual QC, and VLM + GNN 3-way invoice auditing.</td>
                    <td>Strict spend thresholds, RBAC security, audit logs, and instant override gates.</td>
                </tr>
            </table>
        </div>

        <div style="border-top:1pt solid #000000; padding-top:6pt; display:flex; justify-content:space-between; font-size:8.8pt; color:#000000;">
            <div><b>NEXORA Enterprise Systems Pvt. Ltd.</b> &#8226; Bengaluru, India</div>
            <div><b>Digital Sales Brochure</b> &#8226; Page 1 of {total_pages}</div>
        </div>
    </div>
    """
    pages.append(p1)

    # PAGE 2: About NEXORA & Value Impact
    p2_body = f"""
        <h1 class="sec-head">1. Why Move Beyond Rule-Based ERP Software?</h1>
        <p class="prose">
            Traditional ERP platforms depend on static <span class="mono">IF-THEN</span> rules, sending an alert only after warehouse stock falls below a hardcoded reorder number. When supplier lead times slip or customer demand spikes unexpectedly, rigid scripts react too late and leave staff clearing exceptions in spreadsheets.
        </p>
        <p class="prose">
            NEXORA replaces brittle scripts with <b>Agentic AI</b>: software agents that continuously <b>Perceive</b> live ERP records, <b>Reason</b> using neural forecasting and graph checks, <b>Plan</b> concrete draft actions, and <b>Route for Human Sign-Off</b> before money leaves the business.
        </p>

        <h2 class="sub-head">Side-by-Side Operational Comparison</h2>
        <table class="bro">
            <tr>
                <th style="width:22%;">Business Area</th>
                <th style="width:37%;">Traditional Rule-Based ERP</th>
                <th style="width:41%;">NEXORA AI-Native Approach</th>
            </tr>
            <tr>
                <td><b>Inventory Reordering</b></td>
                <td>Triggers an alert only after stock drops past a static fixed number.</td>
                <td><b>LSTM agent</b> forecasts 14-day runout curves from open orders and prepares draft POs early.</td>
            </tr>
            <tr>
                <td><b>Vendor Selection</b></td>
                <td>Defaults blindly to the first vendor listed on the master item card.</td>
                <td>Scores suppliers dynamically by actual on-time delivery, unit pricing, and defect history.</td>
            </tr>
            <tr>
                <td><b>Production Quality</b></td>
                <td>Defects recorded hours later during end-of-shift manual batch logs.</td>
                <td><b>Edge MQTT + CNN vision</b> flags assembly flaws on-line in real time for supervisor review.</td>
            </tr>
            <tr>
                <td><b>Supplier Billing (AP)</b></td>
                <td>Accounts staff manually type PDF invoice lines into ERP voucher screens.</td>
                <td><b>VLM + GNN agent</b> parses PDF bills and cross-checks PO, Goods Receipt, and GST amounts.</td>
            </tr>
            <tr>
                <td><b>Governance Control</b></td>
                <td>All-or-nothing automation or completely manual data entry.</td>
                <td>Autonomous drafting paired with configurable human spend caps and audit trails.</td>
            </tr>
        </table>

        <h2 class="sub-head">2. Measured Time &amp; Exception Reduction in Pilot Workflows</h2>
        <div class="vis-box">
            {svg_brochure_benchmark_plot()}
        </div>
        <div class="vis-cap">Figure 2: Pilot Workflow Turnaround Benchmark (Rule-Based ERP vs. NEXORA)</div>
        <div class="vis-blurb">
            "By letting AI agents assemble draft purchase orders, pre-scan invoices, and watch assembly cameras continuously, operations teams shift from repetitive typing to fast exception approvals." (*Illustrative prototype model benchmarks.)
        </div>
    """
    pages.append(brochure_page_wrap(p2_body, "About NEXORA & Agentic Advantage", 2, total_pages))

    # PAGE 3: Offerings (8 Modules + Services)
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
    mod_rows = "".join(
        f"<tr><td style='width:5%; text-align:center;'><b>{idx+1}</b></td><td style='width:27%;'><b>{esc(t)}</b></td><td>{esc(d)}</td></tr>"
        for idx, (t, d) in enumerate(modules)
    )
    p3_body = f"""
        <h1 class="sec-head">3. Product Offerings: 8 Unified Business Modules</h1>
        <p class="prose">
            NEXORA delivers a single-database ERP backbone across manufacturing, distribution, warehousing, and corporate finance, eliminating fragile connectors between departments.
        </p>
        <table class="bro">
            <tr><th style="width:5%;">#</th><th style="width:27%;">Core Module</th><th>Functional Capabilities Included</th></tr>
            {mod_rows}
        </table>

        <h1 class="sec-head" style="margin-top:8pt;">4. Implementation, Migration, Training &amp; Support Services</h1>
        <p class="prose">
            Technology succeeds only when people trust it. Every NEXORA subscription can be paired with structured rollout services delivered by our solutions engineering team:
        </p>
        <table class="bro">
            <tr>
                <th style="width:33.3%;">Guided Implementation</th>
                <th style="width:33.3%;">Legacy Data Migration</th>
                <th style="width:33.4%;">Training &amp; 24/7 Support</th>
            </tr>
            <tr>
                <td>
                    <ul class="clean-list" style="margin-top:2pt;">
                        <li>Workflow discovery workshops (Week 1&#8211;2)</li>
                        <li>Approval threshold &amp; RBAC setup</li>
                        <li>Sandbox parallel run before go-live</li>
                    </ul>
                </td>
                <td>
                    <ul class="clean-list" style="margin-top:2pt;">
                        <li>Automated cleanup of duplicate SKUs</li>
                        <li>Import from Tally, SAP B1, ERPNext &amp; Excel</li>
                        <li>Opening stock &amp; ledger balance validation</li>
                    </ul>
                </td>
                <td>
                    <ul class="clean-list" style="margin-top:2pt;">
                        <li>Role-based operator &amp; controller training</li>
                        <li>Quarterly AI forecast accuracy tuning</li>
                        <li>Dedicated SLA ticket &amp; phone desk</li>
                    </ul>
                </td>
            </tr>
        </table>
    """
    pages.append(brochure_page_wrap(p3_body, "Modules & Enterprise Services", 3, total_pages))

    # PAGE 4: AI Features (Modules A & B)
    p4_body = f"""
        <h1 class="sec-head">5. Agentic AI Features: Smart Modules with Human Review</h1>
        <p class="prose">
            Below are two of NEXORA's core intelligent modules, showing exact AI/ML models alongside mandatory human decision gates.
        </p>

        <div class="box-bw" style="padding:8pt 10pt;">
            <h2 class="sub-head" style="margin-top:0;">Agent Module A: Procurement &amp; Warehouse &#8212; Procurement Intelligence Agent</h2>
            <p class="prose" style="font-size:9.3pt;">
                Uses <b>Long Short-Term Memory (LSTM)</b> neural networks trained on rolling consumption history, seasonal order spikes, and supplier lead-time drift to compute dynamic depletion rates and stage replenishment orders before warehouse bins run dry.
            </p>
            <div class="vis-box" style="margin-top:5pt;">
                {svg_brochure_lstm_forecast()}
            </div>
            <div class="vis-cap">Figure 3: Dynamic Stock Depletion Forecast &amp; Queued PO Approval Card</div>
            <div class="vis-blurb">"Detects an upcoming Day-11 shortage for Servo Actuator #AC-40 and stages Draft PO #NX-PO-408 automatically."</div>
            <div class="human-note">
                <b>Where Humans Review &amp; Approve:</b> Any draft PO exceeding the department spend ceiling (e.g., &#8377;2,50,000) or switching to a backup supplier stays paused until the <b>Procurement Manager</b> reviews the LSTM rationale and clicks <i>Approve &amp; Send</i> or edits quantity.
            </div>
        </div>

        <div class="box-bw" style="padding:8pt 10pt; margin-top:2pt;">
            <h2 class="sub-head" style="margin-top:0;">Agent Module B: Production &amp; Quality &#8212; Production Optimization Agent</h2>
            <p class="prose" style="font-size:9.3pt;">
                Combines <b>IoT Edge Processing (MQTT protocols)</b> on CNC/assembly machinery with <b>Convolutional Neural Networks (CNNs)</b> at optical camera stations to catch micro-cracks, missing fasteners, or thermal drift within milliseconds.
            </p>
            <div class="vis-box" style="margin-top:5pt;">
                {svg_brochure_mqtt_cnn()}
            </div>
            <div class="vis-cap">Figure 4: Shop-Floor Edge MQTT Telemetry &amp; CNN Optical Defect Detection Frame</div>
            <div class="vis-blurb">"Isolates a surface micro-crack on Station B2 with 96% CNN confidence and tags the lot for quick inspection."</div>
            <div class="human-note">
                <b>Where Humans Review &amp; Approve:</b> The agent never shuts down an assembly conveyor unilaterally. The <b>Production Line Supervisor</b> views the bounding-box camera snapshot to confirm lot diversion or dismiss a false positive.
            </div>
        </div>
    """
    pages.append(brochure_page_wrap(p4_body, "Agentic Features (Procurement & Production)", 4, total_pages))

    # PAGE 5: Agent Module C (Finance) + Summary Table
    p5_body = f"""
        <h1 class="sec-head">Agent Module C: Finance &amp; Audit &#8212; Financial Guardian Agent</h1>
        <p class="prose">
            Accounts Payable teams lose days reconciling supplier PDF bills that vary across formats. NEXORA pairs <b>Vision-Language Models (VLMs)</b>, which parse unstructured scanned or PDF invoices without fixed coordinate templates, with <b>Graph Neural Networks (GNNs)</b> linking Vendor, PO, Goods Receipt Note (GRN), Bank Account, and Tax IDs to catch duplicate invoices, unapproved surcharges, or short-delivery billing.
        </p>

        <div class="vis-box" style="margin-top:2pt;">
            {svg_brochure_gnn_match()}
        </div>
        <div class="vis-cap">Figure 5: Financial Guardian VLM + GNN 3-Way Match Exception Screen</div>
        <div class="vis-blurb">
            "In this example, the vendor billed for 100 Valve Bodies plus a &#8377;9,500 rush fee when QA accepted only 92 units on the warehouse GRN, freezing payout automatically."
        </div>
        <div class="human-note">
            <b>Where Humans Review &amp; Approve:</b> Whenever a quantity mismatch, price variance, or new vendor bank change triggers a GNN risk flag, payout waits for the <b>Finance Controller</b> to authorize partial payment (&#8377;1,65,600 for 92 accepted units) or trigger a vendor debit note.
        </div>

        <h2 class="sub-head" style="margin-top:8pt;">Cross-Module Agentic Summary &amp; Human Checkpoints</h2>
        <table class="bro">
            <tr>
                <th style="width:19%;">ERP Module</th>
                <th style="width:24%;">Agent &amp; Models Used</th>
                <th style="width:29%;">Autonomous Smart Action</th>
                <th style="width:28%;">Human Approval Checkpoint</th>
            </tr>
            <tr>
                <td><b>Procurement &amp; WH</b></td>
                <td>Procurement Agent<br><span class="mono">(LSTM Time-Series)</span></td>
                <td>Predicts runout curves and drafts optimal multi-vendor POs.</td>
                <td><b>Procurement Manager</b> approves orders over budget cap or new suppliers.</td>
            </tr>
            <tr>
                <td><b>Production &amp; QA</b></td>
                <td>Production Agent<br><span class="mono">(MQTT Edge + CNN)</span></td>
                <td>Detects assembly anomalies and isolates suspect batch lots.</td>
                <td><b>Shift Supervisor</b> confirms conveyor stops, scrap tags, or lot release.</td>
            </tr>
            <tr>
                <td><b>Finance &amp; AP</b></td>
                <td>Financial Guardian<br><span class="mono">(VLM + GNN Graph)</span></td>
                <td>Reads invoice PDFs and performs 3-way PO&#8211;GRN&#8211;Bill verification.</td>
                <td><b>Finance Controller</b> resolves variance holds and releases bank transfers.</td>
            </tr>
            <tr>
                <td><b>Sales &amp; Credit</b></td>
                <td>Deal Margin Guard<br><span class="mono">(Gradient Risk Scoring)</span></td>
                <td>Flags overdue customer accounts and low-margin discount quotes.</td>
                <td><b>Sales Head</b> reviews credit-limit overrides before releasing dispatch.</td>
            </tr>
        </table>
    """
    pages.append(brochure_page_wrap(p5_body, "Agentic Features (Finance & Summary)", 5, total_pages))

    # PAGE 6: How It Works
    p6_body = f"""
        <h1 class="sec-head">6. How It Works: AI Speed Paired with Human Control</h1>
        <p class="prose">
            NEXORA structures every operational lifecycle, such as <b>Procure-to-Pay (P2P)</b>, into transparent handoffs between software agents and authorized employees. Agents do the continuous monitoring, calculation, and paperwork preparation; people approve capital expenditure, inspect physical goods, and sign off on bank payouts.
        </p>

        <div class="vis-box" style="padding:8pt;">
            {svg_brochure_p2p_flowchart()}
        </div>
        <div class="vis-cap">Figure 6: End-to-End Intelligent Procure-to-Pay Process &#8212; Steps by AI vs. People</div>
        <div class="vis-blurb">
            "Notice the continuous learning loop: whenever a Procurement Manager adjusts or rejects an AI-drafted order at Step 4, NEXORA logs the reason and refines future LSTM recommendations."
        </div>

        <table class="bro" style="margin-top:6pt;">
            <tr>
                <th style="width:50%;">Steps Handled by AI Agents</th>
                <th style="width:50%;">Steps Handled by People</th>
            </tr>
            <tr>
                <td>
                    <ul class="clean-list" style="margin-top:2pt;">
                        <li><b>Continuous Monitoring:</b> Watches warehouse stock levels and open customer demand 24/7.</li>
                        <li><b>Demand &amp; Supplier Reasoning:</b> Runs LSTM forecasts and ranks vendors by cost and lead time.</li>
                        <li><b>Draft Document Prep:</b> Populates line items, tax codes, and justification notes in draft POs.</li>
                        <li><b>3-Way Bill Verification:</b> Parses vendor PDFs via VLM and spots billing mismatches via GNN.</li>
                    </ul>
                </td>
                <td>
                    <ul class="clean-list" style="margin-top:2pt;">
                        <li><b>Budget &amp; Policy Approval:</b> Reviews and approves draft orders above configured spend caps.</li>
                        <li><b>Override &amp; Feedback:</b> Rejects or edits quantities when real-world business context changes.</li>
                        <li><b>Physical QA Inspection:</b> Warehouse staff verify delivered goods and log damaged items in GRN.</li>
                        <li><b>Final Treasury Release:</b> Finance Controller authorizes vendor NEFT/RTGS bank settlement.</li>
                    </ul>
                </td>
            </tr>
        </table>
    """
    pages.append(brochure_page_wrap(p6_body, "How It Works: AI-Human Process", 6, total_pages))

    # PAGE 7: Trust & Security + Pricing Plans
    p7_body = """
        <h1 class="sec-head">7. Trust, Security &amp; Governance</h1>
        <div class="human-note" style="margin-top:0; padding:6pt 9pt;">
            <div style="font-size:10.5pt; font-weight:700; color:#000000;">Autonomous Intelligence. Accountable Decisions.</div>
            <p class="prose" style="margin-top:2pt;">
                <i>"NEXORA combines autonomous intelligence with human accountability."</i> Operational data stays strictly isolated per tenant, and every AI action operates within hard policy rules defined by finance and IT leadership.
            </p>
        </div>

        <table class="bro">
            <tr><th style="width:30%;">Security Control Pillar</th><th>How Data &amp; AI Actions Stay Controlled</th></tr>
            <tr><td><b>1. Data Encryption &amp; Isolation</b></td><td>AES-256 encryption at rest for relational records and invoice PDFs; TLS 1.3 encryption in transit across web portals and edge MQTT brokers. Optional private VPC / on-premise hosting ensures company data is never used to train external public models.</td></tr>
            <tr><td><b>2. Role-Based Access Control (RBAC)</b></td><td>Granular document and field permissions enforce separation of duties: warehouse operators cannot approve purchase budgets, and procurement buyers cannot alter vendor bank master details.</td></tr>
            <tr><td><b>3. Hard Financial Spend Caps</b></td><td>Administrators set clear monetary limits (e.g., max &#8377;50,000 auto-PO per week). Any higher commitment automatically locks execution and escalates to designated managers.</td></tr>
            <tr><td><b>4. Audit Trails &amp; Instant Kill-Switch</b></td><td>Every agent recommendation stores its input snapshot, confidence score, and human approver timestamp. A one-click pause switch reverts any module back to manual workflow instantly.</td></tr>
        </table>

        <h1 class="sec-head" style="margin-top:8pt;">8. Software Pricing Plans &amp; Packages</h1>
        <p class="prose">
            Transparent annual or monthly per-company licensing, inclusive of software updates, security patches, and full SQL export ownership.
        </p>
        <table class="bro">
            <tr>
                <th style="width:23%;">Package Comparison</th>
                <th style="width:24%;">Starter<br><span style="font-weight:400; font-size:8pt;">Small Businesses</span></th>
                <th style="width:27%; background-color:#D9D9D9; border-top:2pt solid #000000;">Growth (Recommended)<br><span style="font-weight:400; font-size:8pt;">Mid-Market Factories</span></th>
                <th style="width:26%;">Enterprise<br><span style="font-weight:400; font-size:8pt;">Multi-Plant Groups</span></th>
            </tr>
            <tr>
                <td><b>Monthly Licensing</b></td>
                <td><b>&#8377;45,000 / month</b></td>
                <td><b>&#8377;1,25,000 / month</b></td>
                <td><b>Custom Annual Quote</b></td>
            </tr>
            <tr>
                <td><b>Included User Seats</b></td>
                <td>Up to 25 Active Users</td>
                <td>Up to 150 Active Users</td>
                <td>Unlimited Users &amp; Plants</td>
            </tr>
            <tr>
                <td><b>ERP Modules Included</b></td>
                <td>Sales, Procurement, Inventory, Finance (4 Core)</td>
                <td>All 8 Modules (Full Suite + WH, Production, QA, HR)</td>
                <td>All 8 Modules + Multi-Company Consolidation</td>
            </tr>
            <tr>
                <td><b>Agentic AI Suite</b></td>
                <td>Financial Guardian (VLM Invoice Match, 10k runs/mo)</td>
                <td>All 3 AI Agents (1,00,000 agent runs/mo)</td>
                <td>Unlimited Inference + Custom Edge CNN Tuning</td>
            </tr>
            <tr>
                <td><b>Implementation &amp; Support</b></td>
                <td>CSV Migration Tool + Email Helpdesk</td>
                <td>Dedicated Onboarding Engineer + 99.9% SLA</td>
                <td>Private VPC / On-Prem Setup + 24/7 Architect SLA</td>
            </tr>
        </table>
    """
    pages.append(brochure_page_wrap(p7_body, "Trust, Security & Pricing Packages", 7, total_pages))

    # PAGE 8: Student Officers, Contacts & References
    officers = [
        ("Eshaan", "Founder & Chief Executive Officer (CEO)", "Product strategy, customer partnerships & executive governance."),
        ("Srujan", "Chief Technology Officer (CTO)", "Distributed ERP core, SQL databases, API security & telemetry pipelines."),
        ("Abhay", "Chief AI Officer (CAIO)", "LSTM demand modeling, edge MQTT + CNN vision & VLM/GNN guardrails."),
        ("Siri", "Chief Operating Officer (COO)", "Module architecture, client onboarding, QA compliance & finance workflows."),
    ]
    officer_rows = "".join(
        f"<tr><td><b>{esc(nm)}</b></td><td class='mono'>{esc(emp_by_name.get(nm.lower(), 'PES1UG24CS000'))}</td>"
        f"<td>{esc(role)}</td><td>{esc(bio)}</td></tr>"
        for nm, role, bio in officers
    )

    p8_body = f"""
        <h1 class="sec-head">9. Executive Leadership Team (Student Officers)</h1>
        <p class="prose">
            NEXORA is led by its four founding student officers overseeing product engineering, agentic AI research, enterprise database systems, and operational delivery:
        </p>
        <table class="bro">
            <tr><th style="width:15%;">Student Name</th><th style="width:18%;">SRN</th><th style="width:28%;">Executive Title</th><th>Primary Focus</th></tr>
            {officer_rows}
        </table>

        <h1 class="sec-head" style="margin-top:8pt;">10. Contact Us &amp; Request a Live Product Demo</h1>
        <table class="bro">
            <tr>
                <td style="width:52%;">
                    <b>NEXORA Enterprise Systems Pvt. Ltd.</b><br>
                    Suite 402, Bellandur Innovation Hub, Outer Ring Road,<br>
                    Bengaluru &#8211; 560103, Karnataka, India
                </td>
                <td style="width:48%;">
                    <b>Sales Inquiries:</b> <span class="mono">sales@nexora-ebs.example.com</span><br>
                    <b>Support Desk:</b> <span class="mono">support@nexora-ebs.example.com</span><br>
                    <b>Web Portal:</b> <span class="url-txt">https://nexora-ebs.example.com</span><br>
                    <b>Local HTML Brochure:</b> <span class="mono">nexora_brochure_standalone.html</span>
                </td>
            </tr>
        </table>

        <h1 class="sec-head" style="margin-top:8pt;">11. Information Sources &amp; Reference URLs</h1>
        <div class="box-bw">
            <p class="prose" style="font-size:9pt; margin-bottom:4pt;">Per project documentation guidelines, technical concepts, ERP module structures, neural architectures, and AI guardrail standards referenced in this brochure were sourced from:</p>
            <ul class="clean-list">
                <li><b>Open-Source ERP Module Structures:</b> <span class="url-txt">https://docs.erpnext.com</span> and <span class="url-txt">https://erpnext.com</span></li>
                <li><b>Deep Learning Models (LSTM Forecasting &amp; CNN Vision):</b> <span class="url-txt">https://pytorch.org/docs/stable/</span></li>
                <li><b>Graph Neural Networks (Anomaly Detection &amp; 3-Way Match):</b> <span class="url-txt">https://pytorch-geometric.readthedocs.io</span></li>
                <li><b>Industrial IoT Edge Telemetry Standard (MQTT):</b> <span class="url-txt">https://mqtt.org</span></li>
                <li><b>AI Risk Management &amp; Human-in-the-Loop Governance:</b> <span class="url-txt">https://www.nist.gov/itl/ai-risk-management-framework</span></li>
                <li><b>Enterprise Application &amp; RBAC Security Guidelines:</b> <span class="url-txt">https://owasp.org/www-project-top-ten/</span></li>
            </ul>
        </div>

        <div style="border-top:1.5pt solid #000000; border-bottom:1.5pt solid #000000; padding:6pt 8pt; background:#F2F2F2; display:flex; justify-content:space-between; font-size:8.8pt; margin-top:auto;">
            <span><b>NEXORA</b> &#8212; Intelligence That Runs Your Enterprise.</span>
            <span>UE24CS343AB8 (Part B) &#8226; Independent Concept Brochure</span>
        </div>
    """
    pages.append(brochure_page_wrap(p8_body, "Leadership Team, Contact & References", 8, total_pages))

    return pages
