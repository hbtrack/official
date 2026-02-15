# scripts/ops_gate.ps1
param(
  [ValidateSet("check","fix","batch")] [string] $Mode = "check",
  [ValidateSet("all","smart")]          [string] $Scope = "smart",
  [switch] $IncludeQuality = $false,
  [switch] $RefreshSSOT = $false
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# Repo root = um nível acima de /scripts
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path

function Invoke-Step([string]$Name, [scriptblock]$Cmd, [int]$DefaultFailCode) {
  Write-Host ""
  Write-Host "==> $Name"
  & $Cmd
  $code = $LASTEXITCODE
  if ($code -ne 0) {
    Write-Host "FAIL ($Name) exit=$code"
    exit $code
  }
  Write-Host "PASS ($Name)"
}

function Get-ChangedFiles([string]$root) {
  Push-Location $root
  try {
    $baseRef = $env:GITHUB_BASE_REF
    if ($baseRef) {
      git fetch origin $baseRef --depth=1 | Out-Null
      $base = "origin/$baseRef"
    } else {
      $base = "HEAD~1"
    }
    return @(git diff --name-only $base HEAD)
  } finally {
    Pop-Location
  }
}

function ShouldRunStructural([string[]]$changed) {
  if (-not $changed -or $changed.Count -eq 0) { return $true }
  foreach ($f in $changed) {
    if ($f -match '^docs/_generated/schema\.sql$') { return $true }
    if ($f -match '^app/models/')                { return $true }
    if ($f -match '^alembic/' -or $f -match '^migrations/') { return $true }
    if ($f -match '^ops_.*\.ps1$')               { return $true }
    if ($f -match '^gen_.*\.py$')                { return $true }
    if ($f -match '^check_models_requirements\.py$') { return $true }
  }
  return $false
}

$changed = @()
$runStructural = $true

if ($Scope -eq "smart") {
  $changed = Get-ChangedFiles $RepoRoot
  $runStructural = ShouldRunStructural $changed
}

# Helpers para paths
$ops_root                 = Join-Path $RepoRoot "scripts\ops"
$ops_infra                = Join-Path $ops_root "infra"

$ops_inv                  = Join-Path $ops_root "ops_inv.ps1"
$ops_parity_scan          = Join-Path $ops_root "ops_parity_scan.ps1"
$ops_parity_gate          = Join-Path $ops_infra "ops_parity_gate.ps1"
$ops_models_autogen_gate  = Join-Path $ops_infra "ops_models_autogen_gate.ps1"
$ops_models_batch         = Join-Path $ops_infra "ops_models_batch.ps1"
$check_requirements       = Join-Path $RepoRoot "scripts\checks\db\check_models_requirements.py"

# 0) Refresh SSOT (opcional)
if ($RefreshSSOT) {
  Invoke-Step "SSOT refresh (ops_inv.ps1 refresh)" {
    pwsh $ops_inv refresh
  } 5
}

# 1) Qualidade horizontal (opcional)
if ($IncludeQuality) {
  Invoke-Step "Ruff (lint)"          { Push-Location $RepoRoot; try { ruff check . } finally { Pop-Location } } 10
  Invoke-Step "Black (format check)" { Push-Location $RepoRoot; try { black --check . } finally { Pop-Location } } 11
  Invoke-Step "MyPy (typecheck)"     { Push-Location $RepoRoot; try { mypy app/ } finally { Pop-Location } } 12
  Invoke-Step "Bandit (security)"    { Push-Location $RepoRoot; try { bandit -r app/ -ll } finally { Pop-Location } } 13
  Invoke-Step "Radon (complexity)"   { Push-Location $RepoRoot; try { radon cc app/ -nc 6 } finally { Pop-Location } } 14
  Invoke-Step "Pytest"               { Push-Location $RepoRoot; try { pytest -q } finally { Pop-Location } } 15
  Invoke-Step "Coverage (>=75)"      { Push-Location $RepoRoot; try { coverage report --fail-under=75 } finally { Pop-Location } } 16
}

# 2) Gates estruturais DB-first
if ($runStructural) {

  if ($Mode -eq "check") {
    Invoke-Step "Parity scan" { pwsh $ops_parity_scan -FailOnStructuralDiffs } 2
    Invoke-Step "Parity gate" { pwsh $ops_parity_gate } 2

    Invoke-Step "Requirements (check_models_requirements.py)" {
      Push-Location $RepoRoot
      try { python $check_requirements } finally { Pop-Location }
    } 4
  }

  elseif ($Mode -eq "fix") {
    Invoke-Step "Models autogen gate (auto-fix)" { pwsh $ops_models_autogen_gate } 2

    Invoke-Step "Parity scan" { pwsh $ops_parity_scan -FailOnStructuralDiffs } 2
    Invoke-Step "Parity gate" { pwsh $ops_parity_gate } 2

    Invoke-Step "Requirements (check_models_requirements.py)" {
      Push-Location $RepoRoot
      try { python $check_requirements } finally { Pop-Location }
    } 4
  }

  elseif ($Mode -eq "batch") {
    Invoke-Step "Models batch (multi-table loop)" { pwsh $ops_models_batch } 2

        Invoke-Step "Parity gate" { pwsh $ops_parity_gate } 2

    Invoke-Step "Requirements (check_models_requirements.py)" {
      Push-Location $RepoRoot
      try { python $check_requirements } finally { Pop-Location }
    } 4
  }
}

Write-Host ""
Write-Host "ALL GATES PASSED"
exit 0
