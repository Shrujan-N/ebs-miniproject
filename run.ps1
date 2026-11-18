# ============================================================================
# UE24CS343AB8 - EBS Mini Project PowerShell Launcher (Zero External Dependencies)
# Owner: SHRUJAN N (PES1UG24CS624 — Database, Backend & Dashboard)
# ============================================================================

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectRoot

Write-Host "[1/2] Initializing SQLite Relational Database & Exporting ERPNext CSVs..." -ForegroundColor Cyan
python "$ProjectRoot\backend\seed_data.py"
python "$ProjectRoot\backend\erpnext_sync.py"

Write-Host "[2/2] Starting VoltEdge ERP Dashboard & NEXORA Brochure Server..." -ForegroundColor Green
Write-Host " -> Part A (VoltEdge Dashboard): http://127.0.0.1:8050/dashboard" -ForegroundColor Yellow
Write-Host " -> Part B (NEXORA Brochure):    http://127.0.0.1:8050/nexora" -ForegroundColor Yellow
python "$ProjectRoot\backend\app.py"
