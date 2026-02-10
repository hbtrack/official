<#
models_batch.ps1 (SSOT-AUTO)
Batch runner determinístico: refresh SSOT (1x) -> tabelas do schema.sql -> requirements scan -> gate nas FAIL (1 por vez) -> stop-on-first-failure.

Uso:
  # automático via SSOT (default, fail-fast ON)
  .\scripts\models_batch.ps1

  # automático via SSOT, excluindo algumas tabelas
  .\scripts\models_batch.ps1 -ExcludeTables "alembic_version","audit_logs"

  # usar lista explícita (manual)
  .\scripts\models_batch.ps1 -AutoTables None -TablesFile .\scripts\tables.txt

  # só varredura (requirements), sem gate
  .\scripts\models_batch.ps1 -SkipGate

  # desabilitar fail-fast (continuar mesmo com erro)
  .\scripts\models_batch.ps1 -NoFailFast

  # autorizar snapshot baseline (não commita)
  .\scripts\models_batch.ps1 -AllowBaselineSnapshot
#>

[CmdletBinding()]
param(
  [ValidateSet("FromSSOT","None")]
  [string]$AutoTables = "FromSSOT",

  [string[]]$ExcludeTables = @(
    "alembic_version"
  ),

  [string[]]$Tables,
  [string]$TablesFile,

  [ValidateSet("strict","fk","lenient")]
  [string]$DefaultProfile = "strict",

  [switch]$SkipRefresh,
  [switch]$SkipGate,
  [switch]$NoFailFast,
  [switch]$AllowBaselineSnapshot = $false
)

$FailFast = -not $NoFailFast

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Abort([string]$Message, [int]$ExitCode = 1) {
  Write-Host "`n[ABORT] $Message" -ForegroundColor Red
  exit $ExitCode
}

function Ensure-BackendRoot {
  if (-not (Test-Path ".\scripts")) {
    Abort "CWD não é o backend root. Rode: Set-Location 'C:\HB TRACK\Hb Track - Backend'." 1
  }
  if (-not (Test-Path ".\venv\Scripts\python.exe")) {
    Abort "venv não encontrada em .\venv\Scripts\python.exe" 1
  }
  if (-not (Test-Path ".\scripts\model_requirements.py")) {
    Abort "scripts\model_requirements.py não encontrado." 1
  }
  if (-not (Test-Path ".\scripts\models_autogen_gate.ps1")) {
    Abort "scripts\models_autogen_gate.ps1 não encontrado." 1
  }
}

function Ensure-CleanRepo {
  $porcelain = (git status --porcelain)
  if ($porcelain -and $porcelain.Trim().Length -gt 0) {
    Write-Host $porcelain
    Abort "Repo não está limpo (git status --porcelain não vazio). Limpe/reverta/commite antes de rodar batch." 3
  }
}

function Run-RefreshSSOT {
  if ($SkipRefresh) {
    Write-Host "[SKIP] inv.ps1 refresh" -ForegroundColor Yellow
    return
  }

  $inv = "C:\HB TRACK\scripts\inv.ps1"
  if (-not (Test-Path $inv)) { Abort "inv.ps1 não encontrado em $inv" 1 }

  Write-Host "`n[STEP] SSOT refresh (inv.ps1 refresh)" -ForegroundColor Cyan
  & powershell -NoProfile -ExecutionPolicy Bypass -File $inv refresh
  $ec = $LASTEXITCODE
  if ($ec -ne 0) { Abort "inv.ps1 refresh falhou (exit=$ec)" $ec }
}

function Load-TablesManual {
  $list = @()
  if ($Tables -and $Tables.Count -gt 0) {
    $list += $Tables
  }
  elseif ($TablesFile) {
    if (-not (Test-Path $TablesFile)) { Abort "TablesFile não existe: $TablesFile" 1 }
    $raw = Get-Content $TablesFile -ErrorAction Stop
    foreach ($line in $raw) {
      $t = $line.Trim()
      if ($t -and -not $t.StartsWith("#")) { $list += $t }
    }
  }
  else {
    Abort "AutoTables=None exige -Tables ou -TablesFile." 1
  }

  $norm = @()
  foreach ($t in $list) {
    $x = $t.Trim()
    if ($x) { $norm += $x }
  }
  $norm = $norm | Select-Object -Unique
  if ($norm.Count -eq 0) { Abort "Lista de tabelas vazia." 1 }
  return ,$norm
}

function Load-TablesFromSSOT([string[]]$Exclude) {
  $schemaPath = "docs/_generated/schema.sql"
  if (-not (Test-Path $schemaPath)) {
    Abort "SSOT não encontrado: $schemaPath. Rode inv.ps1 refresh (ou remova -SkipRefresh)." 1
  }

  $content = Get-Content $schemaPath -Raw -ErrorAction Stop

  # captura: CREATE TABLE [schema.]table (
  $rx = [regex] 'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?(?:"?[\w]+"?\.)?"?([\w]+)"?\s*\('
  $matches = $rx.Matches($content)

  $tables = @()
  foreach ($m in $matches) {
    $t = $m.Groups[1].Value
    if (-not $t) { continue }
    if ($Exclude -and ($Exclude -contains $t)) { continue }
    $tables += $t
  }

  $tables = $tables | Select-Object -Unique
  if ($tables.Count -eq 0) { Abort "Nenhuma tabela extraída do SSOT." 1 }
  return ,$tables
}

function Get-ProfileForTable([string]$TableName) {
  # Ajuste aqui se houver outras tabelas com ciclo FK/edge-case.
  $fkTables = @("teams","seasons")
  if ($fkTables -contains $TableName) { return "fk" }
  return $DefaultProfile
}

function Find-ModelFile([string]$TableName) {
  # Procura dinamicamente por arquivo que contenha __tablename__ = '<table>'
  # Retorna o caminho ou $null se não encontado
  $modelsDir = "app/models"
  if (-not (Test-Path $modelsDir)) { return $null }
  
  $tableName = [regex]::Escape($TableName)
  foreach ($modelFile in Get-ChildItem "$modelsDir/*.py" -ErrorAction SilentlyContinue) {
    $content = Get-Content $modelFile -Raw -ErrorAction SilentlyContinue
    $pattern = "__tablename__\s*=\s*['\"]$tableName['\"]"
    if ($content -match $pattern) {
      return $modelFile.FullName
    }
  }
  return $null
}

function Restore-GeneratedArtifacts {
  # Backend docs/_generated
  try {
    git restore -- `
      "docs/_generated/alembic_state.txt" `
      "docs/_generated/manifest.json" `
      "docs/_generated/parity_report.json" `
      "docs/_generated/schema.sql" 2>$null | Out-Null
  } catch {}

  # Root docs/_generated (um nível acima do backend)
  try {
    git restore -- `
      "..\docs/_generated/alembic_state.txt" `
      "..\docs/_generated/manifest.json" `
      "..\docs/_generated/schema.sql" `
      "..\docs/_generated/trd_training_permissions_report.txt" 2>$null | Out-Null
  } catch {}
}

function Run-Requirements([string]$TableName, [string]$Profile, [string]$LogPath) {
  Write-Host "`n[REQ] $TableName (profile=$Profile)" -ForegroundColor Cyan
  Add-Content -Path $LogPath -Value "`n[REQ] $TableName (profile=$Profile)`n"

  # Detectar SKIP_NO_MODEL via Find-ModelFile (busca dinâmica)
  $modelPath = Find-ModelFile $TableName
  if (-not $modelPath) {
    Write-Host "  [SKIP] $TableName - modelo não encontrado" -ForegroundColor Yellow
    Add-Content -Path $LogPath -Value "[SKIP] $TableName - modelo não encontrado`n"
    return 100  # Código interno para SKIP_NO_MODEL
  }

  # Executar Python sem parar em erro (mesmo que falhe)
  $ErrorActionPreference = "Continue"
  $output = & ".\venv\Scripts\python.exe" scripts\model_requirements.py --table $TableName --profile $Profile 2>&1
  $ec = $LASTEXITCODE
  $ErrorActionPreference = "Stop"
  
  # Log output
  $output | Add-Content -Path $LogPath
  
  return $ec
}

function Run-Gate([string]$TableName, [string]$Profile, [string]$LogPath) {
  $gate = ".\scripts\models_autogen_gate.ps1"

  Write-Host "`n[GATE] $TableName (profile=$Profile)" -ForegroundColor Cyan
  Add-Content -Path $LogPath -Value "`n[GATE] $TableName (profile=$Profile)`n"

  if ($Profile -eq "fk") {
    & $gate -Table $TableName -Profile $Profile -AllowCycleWarning 2>&1 | Tee-Object -Append -FilePath $LogPath | Out-Null
  } else {
    & $gate -Table $TableName -Profile $Profile 2>&1 | Tee-Object -Append -FilePath $LogPath | Out-Null
  }

  return $LASTEXITCODE
}

function Maybe-SnapshotBaseline([string]$LogPath) {
  if (-not $AllowBaselineSnapshot) {
    Write-Host "[INFO] Baseline snapshot DESABILITADO (padrão)." -ForegroundColor Yellow
    Add-Content -Path $LogPath -Value "`n[INFO] Baseline snapshot DESABILITADO (padrão).`n"
    return
  }

  Write-Host "`n[STEP] Baseline snapshot (AUTORIZADO)" -ForegroundColor Cyan
  Add-Content -Path $LogPath -Value "`n[STEP] Baseline snapshot (AUTORIZADO)`n"

  & ".\venv\Scripts\python.exe" scripts\agent_guard.py snapshot `
    --root "." `
    --out ".hb_guard/baseline.json" `
    --exclude "venv,.venv,__pycache__,.pytest_cache,docs\_generated" 2>&1 | Tee-Object -Append -FilePath $LogPath | Out-Null

  $ec = $LASTEXITCODE
  if ($ec -ne 0) { Abort "snapshot baseline falhou (exit=$ec)" $ec }

  Write-Host "[OK] baseline.json atualizado (não commitado automaticamente)" -ForegroundColor Green
  Add-Content -Path $LogPath -Value "[OK] baseline.json atualizado (não commitado automaticamente)`n"
}

# -------------------- MAIN --------------------
Ensure-BackendRoot
Ensure-CleanRepo

$runId = (Get-Date -Format "yyyyMMdd_HHmmss")
$logPath = Join-Path $env:TEMP "hb_models_batch_$runId.log"
$csvPath = Join-Path $env:TEMP "hb_models_batch_$runId.csv"

Write-Host "LOG: $logPath" -ForegroundColor Gray
Write-Host "CSV: $csvPath" -ForegroundColor Gray

"table,profile,step,exit,status" | Set-Content -Path $csvPath -Encoding UTF8

Run-RefreshSSOT

$tables =
  if ($AutoTables -eq "FromSSOT") { Load-TablesFromSSOT $ExcludeTables }
  else { Load-TablesManual }

Write-Host "`n[INFO] Tabelas selecionadas: $($tables.Count)" -ForegroundColor Yellow
Add-Content -Path $logPath -Value "[INFO] Tabelas selecionadas: $($tables.Count)`n"

# 1) Requirements scan em lote
$failReq = New-Object System.Collections.Generic.List[string]
foreach ($t in $tables) {
  $profile = Get-ProfileForTable $t
  $ec = Run-Requirements $t $profile $logPath

  if ($ec -eq 0) {
    "$t,$profile,requirements,0,PASS" | Add-Content -Path $csvPath
  }
  elseif ($ec -eq 100) {
    "$t,$profile,requirements,100,SKIP_NO_MODEL" | Add-Content -Path $csvPath
    Write-Host "  [SKIP] $t - modelo não encontrado" -ForegroundColor Yellow
  }
  elseif ($ec -eq 4) {
    "$t,$profile,requirements,4,FAIL" | Add-Content -Path $csvPath
    $failReq.Add($t) | Out-Null
  }
  elseif ($ec -eq 1) {
    "$t,$profile,requirements,1,CRASH" | Add-Content -Path $csvPath
    if ($FailFast) { Abort "Requirements crash em $t (exit=1). Veja log: $logPath" 1 }
  }
  else {
    "$t,$profile,requirements,$ec,ERROR" | Add-Content -Path $csvPath
    if ($FailFast) { Abort "Requirements erro inesperado em $t (exit=$ec). Veja log: $logPath" $ec }
  }

  Restore-GeneratedArtifacts
}

if ($SkipGate) {
  Write-Host "`n[DONE] SkipGate ativo. Varredura concluída." -ForegroundColor Green
  Write-Host "FAIL (requirements exit=4): $($failReq -join ', ')" -ForegroundColor Yellow
  exit 0
}

# 2) Corrigir somente as FAIL (1 por 1)
if ($failReq.Count -eq 0) {
  Write-Host "`n[OK] Nenhuma tabela com FAIL em requirements." -ForegroundColor Green
  Maybe-SnapshotBaseline $logPath
  exit 0
}

Write-Host "`n[INFO] Tabelas FAIL (requirements): $($failReq -join ', ')" -ForegroundColor Yellow
Add-Content -Path $logPath -Value "`n[INFO] FAIL (requirements): $($failReq -join ', ')`n"

foreach ($t in $failReq) {
  Ensure-CleanRepo
  $profile = Get-ProfileForTable $t

  $ec = Run-Gate $t $profile $logPath
  Restore-GeneratedArtifacts

  if ($ec -eq 0) {
    "$t,$profile,gate,0,PASS" | Add-Content -Path $csvPath
    Write-Host "[OK] Gate PASS para $t" -ForegroundColor Green
  }
  else {
    "$t,$profile,gate,$ec,FAIL" | Add-Content -Path $csvPath
    Write-Host "[FAIL] Gate falhou para $t (exit=$ec). Veja log: $logPath" -ForegroundColor Red
    if ($FailFast) { exit $ec }
  }
}

Maybe-SnapshotBaseline $logPath

Write-Host "`n[COMPLETE] Batch finalizado." -ForegroundColor Green
Write-Host "LOG: $logPath"
Write-Host "CSV: $csvPath"
exit 0
