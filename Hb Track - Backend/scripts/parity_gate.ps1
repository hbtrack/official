param(
  [Parameter(Mandatory=$true)][string]$Table,
  [string[]]$Allow = @(),
  [switch]$AllowEnvPy
)

$ErrorActionPreference = "Stop"

$ROOT = (Resolve-Path ".").Path
Write-Host "[CWD] $ROOT"
Write-Host "[TABLE] $Table"

if (Test-Path ".\venv\Scripts\python.exe") { $py = ".\venv\Scripts\python.exe" } else { $py = "python" }

# Ensure baseline exists
if (-not (Test-Path ".hb_guard\baseline.json")) {
  throw "Missing .hb_guard\baseline.json. Run: $py scripts/agent_guard.py snapshot --root . --out .hb_guard/baseline.json"
}

# Build allowlist (relative paths)
$allowList = @("scripts/agent_guard.py", "scripts/parity_gate.ps1")
$allowList += $Allow
if ($AllowEnvPy) { $allowList += "db/alembic/env.py" }

$allowCsv = ($allowList -join ",")

Write-Host "[GUARD] allow=$allowCsv"
& $py scripts/agent_guard.py check --root "." --baseline ".hb_guard\baseline.json" --allow $allowCsv --forbid-new --forbid-delete --assert-skip-model-only-empty "db\alembic\env.py"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "[PARITY] running parity_scan.ps1 -FailOnStructuralDiffs"
.\scripts\parity_scan.ps1 -TableFilter $Table -FailOnStructuralDiffs
$parityExit = $LASTEXITCODE
if ($parityExit -ne 0) {
  exit $parityExit
}

$reportPath = "docs\_generated\parity_report.json"
if (-not (Test-Path $reportPath)) {
  throw "Missing $reportPath after parity scan"
}

$report = Get-Content $reportPath -Raw | ConvertFrom-Json
$warnings = @($report.warnings)
$cycleWarn = @($warnings | Where-Object {
  ([string]$_.category) -eq "sa_warning" -and (
    ([string]$_.message) -match "unresolvable cycles" -or
    ([string]$_.message) -match "Cannot correctly sort tables"
  )
})

if ($cycleWarn.Count -gt 0) {
  $cycleTables = @("teams", "seasons")
  if ([string]::IsNullOrWhiteSpace($Table) -or ($cycleTables -contains $Table)) {
    Write-Host "[FAIL] cycle warning detected (tooling health risk)." -ForegroundColor Red
    exit 2
  } else {
    Write-Host "[WARN] cycle warning detected but out of scope for Table=$Table; continuing." -ForegroundColor Yellow
  }
}

exit 0