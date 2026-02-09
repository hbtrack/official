param(
  [Parameter(Mandatory=$true)][string]$Table,
  [string[]]$Allow = @(),
  [switch]$AllowEnvPy,
  [switch]$AllowCycleWarning,
  [string]$ParityReportPath = ""
)

$ErrorActionPreference = "Stop"

# Calculate ROOT from script location (not CWD) to ensure backend scope
$SCRIPT_ROOT = $PSScriptRoot
$ROOT = (Resolve-Path (Join-Path $SCRIPT_ROOT "..")).Path
Write-Host "[CWD] $((Resolve-Path ".").Path)"
Write-Host "[ROOT] $ROOT"
Write-Host "[TABLE] $Table"

$venvPy = Join-Path $ROOT "venv\Scripts\python.exe"
if (Test-Path $venvPy) { $py = $venvPy } else { $py = "python" }

# Ensure baseline exists
$baselinePath = Join-Path $ROOT ".hb_guard\baseline.json"
if (-not (Test-Path $baselinePath)) {
  throw "Missing .hb_guard\baseline.json. Run: $py scripts/agent_guard.py snapshot --root . --out .hb_guard/baseline.json"
}

# Build allowlist (relative paths)
$allowList = @("scripts/agent_guard.py", "scripts/parity_gate.ps1")
$allowList += $Allow
if ($AllowEnvPy) { $allowList += "db/alembic/env.py" }

$allowCsv = ($allowList -join ",")

# Push to ROOT to ensure guard runs with backend scope
Push-Location $ROOT
try {
  Write-Host "[GUARD] allow=$allowCsv"
  & $py scripts/agent_guard.py check --root "." --baseline ".hb_guard\baseline.json" --allow $allowCsv --forbid-new --forbid-delete --assert-skip-model-only-empty "db\alembic\env.py"
  if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
} finally {
  Pop-Location
}

Push-Location $ROOT
try {
  Write-Host "[PARITY] running parity_scan.ps1 -FailOnStructuralDiffs"
  $useInjectedReport = (-not [string]::IsNullOrWhiteSpace($ParityReportPath)) -and (Test-Path $ParityReportPath)
  if ($useInjectedReport) {
    Write-Host "[PARITY] using injected report: $ParityReportPath"
  } else {
    .\scripts\parity_scan.ps1 -TableFilter $Table -FailOnStructuralDiffs
    $parityExit = $LASTEXITCODE
    if ($parityExit -ne 0) {
      exit $parityExit
    }
  }
} finally {
  Pop-Location
}

$reportPath = "docs\_generated\parity_report.json"
if (-not [string]::IsNullOrWhiteSpace($ParityReportPath)) {
  $reportPath = $ParityReportPath
}
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
  $isCycleScope = [string]::IsNullOrWhiteSpace($Table) -or ($cycleTables -contains $Table)
  if ($isCycleScope -and -not $AllowCycleWarning) {
    Write-Host "[FAIL] cycle warning detected (teams<->seasons). Use -AllowCycleWarning with mitigation evidence." -ForegroundColor Red
    exit 2
  }

  if ($isCycleScope -and $AllowCycleWarning) {
    $teamModel = "app\models\team.py"
    $seasonModel = "app\models\season.py"

    $teamHasUseAlter = (Select-String -Path $teamModel -Pattern "fk_teams_season_id.*use_alter\s*=\s*True" -Quiet)
    $seasonHasUseAlter = (Select-String -Path $seasonModel -Pattern "fk_seasons_team_id.*use_alter\s*=\s*True" -Quiet)

    if (-not $teamHasUseAlter -or -not $seasonHasUseAlter) {
      Write-Host "[FAIL] -AllowCycleWarning requires mitigations: use_alter=True on both fk_teams_season_id and fk_seasons_team_id." -ForegroundColor Red
      exit 2
    }

    Write-Host "[WARN] cycle warning allowed by override; mitigations validated (use_alter=True on both sides)." -ForegroundColor Yellow
  } else {
    Write-Host "[WARN] cycle warning detected but out of scope for Table=$Table; continuing." -ForegroundColor Yellow
  }
}

exit 0