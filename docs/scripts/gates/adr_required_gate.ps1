param(
  [string]$BaseRef = "origin/main",
  [string]$HeadRef = "HEAD"
)

$ErrorActionPreference = "Stop"

function Get-ChangedFiles([string]$base, [string]$head) {
  $cmd = "git diff --name-only $base...$head"
  $out = & git diff --name-only "$base...$head"
  return @($out | Where-Object { $_ -and $_.Trim().Length -gt 0 })
}

function Match-AnyPattern([string]$path, [string[]]$patterns) {
  foreach ($p in $patterns) {
    if ($path -like $p) { return $true }
  }
  return $false
}

# 1) Defina os arquivos/pastas sensíveis (SSOT / domínio / invariantes / gerados / governança)
# Ajuste para refletir exatamente sua estrutura.
$sensitivePatterns = @(
  "Hb Track - Backend/docs/_generated/*",
  "Hb Track - Backend/docs/_generated/**",
  "Hb Track - Backend/app/**",
  "Hb Track - Backend/src/**",
  "Hb Track - Backend/models/**",
  "Hb Track - Backend/alembic/**",
  "Hb Track - Backend/tests/training/**",
  "docs/02-modulos/training/**",
  "docs/_ai/**",
  "INVARIANTS_TRAINING.md",
  "TRD_TRAINING.md",
  "PRD_BASELINE_ASIS_TRAINING.md",
  "PRD_HB_TRACK.md",
  "_MAPA_DE_CONTEXTO.md"
)

# 2) Defina onde ADRs vivem (o gate exige um ADR quando sensíveis mudam)
$adrPatterns = @(
  "docs/adr/training/ADR-TRAIN-*.md"
)

$adrIndexPath = "docs/adr/training/ADR_INDEX.md"

# 3) Liste mudanças
$changed = Get-ChangedFiles $BaseRef $HeadRef

if ($changed.Count -eq 0) {
  Write-Host "[OK] No changes detected."
  exit 0
}

# 4) Detecte se houve mudança sensível
$sensitiveChanged = @()
foreach ($f in $changed) {
  if (Match-AnyPattern $f $sensitivePatterns) {
    $sensitiveChanged += $f
  }
}

if ($sensitiveChanged.Count -eq 0) {
  Write-Host "[OK] No sensitive files changed. ADR not required."
  exit 0
}

# 5) Se houve mudança sensível, exija ADR(s) e índice atualizado
$adrTouched = @()
foreach ($f in $changed) {
  if (Match-AnyPattern $f $adrPatterns) {
    $adrTouched += $f
  }
}

$indexTouched = $changed -contains $adrIndexPath

# Regra mínima: pelo menos 1 ADR tocado + ADR_INDEX tocado
if ($adrTouched.Count -lt 1 -or -not $indexTouched) {
  Write-Host ""
  Write-Host "[FAIL] Sensitive change detected ⇒ ADR is mandatory."
  Write-Host "Sensitive files changed:"
  $sensitiveChanged | ForEach-Object { Write-Host "  - $_" }

  Write-Host ""
  if ($adrTouched.Count -lt 1) {
    Write-Host "Missing: at least one ADR file in docs/adr/training/ADR-TRAIN-*.md"
  } else {
    Write-Host "ADR touched:"
    $adrTouched | ForEach-Object { Write-Host "  - $_" }
  }

  if (-not $indexTouched) {
    Write-Host "Missing: update index file $adrIndexPath"
  }

  Write-Host ""
  Write-Host "Fix:"
  Write-Host "  1) Create/update an ADR using docs/adr/ADR_TEMPLATE.md"
  Write-Host "  2) Add it under docs/adr/training/"
  Write-Host "  3) Update docs/adr/training/ADR_INDEX.md"
  exit 2
}

Write-Host "[OK] Sensitive change detected and ADR + index updated."
Write-Host "Sensitive files changed:"
$sensitiveChanged | ForEach-Object { Write-Host "  - $_" }
Write-Host "ADR files touched:"
$adrTouched | ForEach-Object { Write-Host "  - $_" }
Write-Host "Index touched: $adrIndexPath"
exit 0
