# UE24CS343AB8 — EBS Mini Project (`ebs_project`)

## Team Responsibilities
- **Srujan**: Relational Database (`schema.sql`, `voltedge_ebs.db`, `schema.dbml`), Python Backend (`app.py`, `seed_data.py`, `erpnext_sync.py`), Executive Dashboard & 3 Management Reports (`templates/dashboard.html`).
- **Eshaan**: Main Structure of Part A & Design of AI Agentic Models (LSTM, MQTT+CNN, VLM+GNN).
- **Abhay**: Design & Visuals for Companies (`templates/nexora.html` & colour systems).
- **Siri**: Product Modules, Report Analysis & Financial Governance.

---

## Quick Start (Windows PowerShell — Zero `pip` Installs Required)

```powershell
cd "d:\university\sem 5\EBS\miniproject\ebs_project"
.\run.ps1
```

Or run directly:
```powershell
python "d:\university\sem 5\EBS\miniproject\ebs_project\backend\app.py"
```

### Option A: Live Server URLs
1. **Part A — VoltEdge Energy Systems ERP Workspace (Light Theme for Report Screenshots)**:
   - `http://127.0.0.1:5000/dashboard`
2. **Part B — NEXORA AI-Native EBS Website & 8-Page Digital Brochure (`#290044` & `#F5F5DC` Theme)**:
   - `http://127.0.0.1:5000/nexora`

### Option B: Standalone HTML Files (Open Directly in Browser)
- [voltedge_dashboard_standalone.html](file:///d:/university/sem%205/EBS/miniproject/ebs_project/voltedge_dashboard_standalone.html) — Part A Dashboard, 3 Reports, 2 Business Cycles, 6 Master Tables, and Relational Schema.
- [nexora_brochure_standalone.html](file:///d:/university/sem%205/EBS/miniproject/ebs_project/nexora_brochure_standalone.html) — Part B NEXORA Single-Page Website & Print-Ready Brochure.

---

## Updating Team SRNs
Open `backend/seed_data.py` (lines 19–48) and `templates/nexora.html` (Footer section) to replace `PES1UG24CS001`–`004` with your exact SRNs, then run `python backend\app.py` to regenerate the database, CSV exports, and standalone HTML files automatically.
