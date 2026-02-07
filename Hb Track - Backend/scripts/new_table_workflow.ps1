param(
  [Parameter(Mandatory=$true)][string]$Table,
  [string]$ModelFile = "",
  [string]$ClassName = "",
  [switch]$CreateModel,
  [switch]$RunParityGateOnly
)

$ErrorActionPreference = "Stop"
$ROOT = (Resolve-Path ".").Path
Write-Host "[CWD] $ROOT"
Write-Host "[TABLE] $Table"

if (Test-Path ".\venv\Scripts\python.exe") { $py = ".\venv\Scripts\python.exe" } else { $py = "python" }

if (-not $RunParityGateOnly) {
  Write-Host "`n[STEP 1] Alembic upgrade head" -ForegroundColor Yellow
  & $py -m alembic upgrade head
  if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

  Write-Host "`n[STEP 2] Refresh SSOT (schema.sql via parity_scan)" -ForegroundColor Yellow
  .\scripts\parity_scan.ps1
  if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

if ($CreateModel) {
  Write-Host "`n[STEP 3] Create+Autogen model + parity gate" -ForegroundColor Yellow
  .\scripts\models_autogen_gate.ps1 -Table $Table -Create -ModelFile $ModelFile -ClassName $ClassName -Allow $ModelFile
  exit $LASTEXITCODE
} else {
  Write-Host "`n[STEP 3] Autogen model + parity gate (no create)" -ForegroundColor Yellow
  .\scripts\models_autogen_gate.ps1 -Table $Table -ModelFile $ModelFile -ClassName $ClassName -Allow $ModelFile
  exit $LASTEXITCODE
}