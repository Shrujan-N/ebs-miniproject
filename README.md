# UE24CS343AB8 / 22UECS352A — EBS Mini Project (`ebs miniproject`)

## Team Responsibilities
- **SHRUJAN N (`PES1UG24CS624`)**: Relational Database (`schema.sql`, `voltedge_ebs.db`, `schema.dbml`), Python Backend (`app.py`, `seed_data.py`, `erpnext_sync.py`), Executive Dashboard & 3 Management Reports (`templates/dashboard.html`).
- **ESHAAN K (`PES1UG24EE012`)**: Main Structure of Part A, Procurement & SCM, and Design of AI Agentic Models (LSTM, MQTT+CNN, VLM+GNN).
- **ABHAY A KATTI (`PES1UG22EE001`)**: Manufacturing Stock Entries, Quality Assurance & Brochure Visuals (`templates/nexora.html`).
- **SIRI S S (`PES1UG24CS627`)**: Product Modules, Report Analysis & Financial Governance.

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

### Option A: Live Server URLs (Local SQLite Showcase — Zero Dependencies)
1. **Part A — VoltEdge Power Systems ERPNext v16 Showcase (Light Desk UI)**:
   - `http://127.0.0.1:8050/dashboard`
2. **Part B — NEXORA ERP Cloud Digital Sales Brochure (Pure Black & White, Student Style)**:
   - `http://127.0.0.1:8050/nexora`

### Option B: Official ERPNext v16 Docker + MariaDB 10.6 Stack
```powershell
cd "d:\university\sem 5\EBS\miniproject\ebs miniproject\erpnext_v16_docker"
docker compose up -d
# Once created (~2-3 mins), open http://localhost:8080 and optionally sync records:
python ..\backend\erpnext_sync.py --push --api-key <KEY> --api-secret <SECRET>
```
Authentic MariaDB `tab*` DDL lives in `backend/erpnext_mariadb_schema.sql`.

### Option C: Standalone HTML Files (Open Directly in Browser)
- `dashboard_standalone.html` / `voltedge_dashboard_standalone.html` — Part A Dashboard, 5-Doc O2C/P2P Chain Tracer, Calculated Stock Ledger, 3 Reports, 6 Master Tables, and MariaDB Schema.
- `nexora_brochure_standalone.html` / `nexora_standalone.html` — Part B NEXORA B&W Digital Sales Brochure (strictly unrelated to Part A).

### Option D: Student-Style PDF & DOCX Deliverables (`pdfs/` & Submission Root)
Regenerate directly from `voltedge_ebs.db` (e.g., after updating SRNs in `backend/seed_data.py`) via:
```powershell
python "d:\university\sem 5\EBS\miniproject\ebs miniproject\backend\generate_pdfs.py"
```
Outputs:
- `pdfs/EBS24CS-P01 624-012-001-627 VoltEdge-ERPNext.pdf` & root copy (17-slide Part A Presentation & Visual Documentation Deck)
- `pdfs/EBS24CS-P02 624-012-001-627 NEXORA.pdf` & root copy (8-page A4 Portrait Pure B&W Digital Sales Brochure)
- `pdfs/EBS24CS-P02 624-012-001-627 NEXORA.docx` & root copy (Editable 8-page Microsoft Word version of Part B Brochure)

