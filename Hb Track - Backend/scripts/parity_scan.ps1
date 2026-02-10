param(
  [string]$RepoRoot = "C:\HB TRACK\Hb Track - Backend",
  [string]$Message = "parity-scan",
  [string]$TableFilter = "",
  [switch]$FailOnStructuralDiffs
)

$ErrorActionPreference = "Stop" # Mudado para Stop para o Agent detectar falhas imediatamente

# Garante que o RepoRoot seja tratado como caminho absoluto
$RepoRoot = (Resolve-Path $RepoRoot).Path
Push-Location $RepoRoot

# evita geração de __pycache__/.pyc fora da área ignorada pelo guard
$env:PYTHONDONTWRITEBYTECODE = "1"
$env:PYTHONPYCACHEPREFIX = Join-Path $RepoRoot ".hb_guard\pycache"
New-Item -ItemType Directory -Force -Path $env:PYTHONPYCACHEPREFIX | Out-Null

# 1. Localização Robusta do Python do Venv
$pythonExe = Join-Path $RepoRoot "venv\Scripts\python.exe"
if (-not (Test-Path $pythonExe)) {
    $pythonExe = Join-Path $RepoRoot ".venv\Scripts\python.exe"
}

# Se ainda não achar, tenta o PATH (fallback), mas avisa
if (-not (Test-Path $pythonExe)) {
    Write-Warning "Venv nao encontrado em $RepoRoot. Tentando usar python do sistema..."
    $pythonExe = "python"
}

# Carrega variáveis de ambiente
$loadEnv = Join-Path $RepoRoot "scripts\_load_env.ps1"
if (Test-Path $loadEnv) {
    . $loadEnv -EnvPath "$RepoRoot\.env"
}

try {
  Write-Host "--- [INICIANDO PARITY SCAN] ---" -ForegroundColor Cyan

  # 1) Build SSOT (schema.sql)
  # Usamos o operador & com aspas simples para caminhos com espaços
  $genDocs = Join-Path $RepoRoot "scripts\generate_docs.py"
  & $pythonExe $genDocs
  if ($LASTEXITCODE -ne 0) { throw "generate_docs.py falhou (exit $LASTEXITCODE)" }

  # 2) Scan-only (Alembic)
  Write-Host "--- [ALEMBIC SCAN] ---" -ForegroundColor Cyan
  $env:ALEMBIC_SCAN_ONLY = "1"
  if ($TableFilter) { $env:ALEMBIC_COMPARE_TABLES = $TableFilter }

  # Configuração de Paths (use env vars if set, else default)
  $generatedDirName = if ($env:HB_DOCS_GENERATED_DIR) { $env:HB_DOCS_GENERATED_DIR } else { "_generated" }
  $backendOut = Join-Path $RepoRoot "docs" $generatedDirName
  $logPathBackend = Join-Path $backendOut "parity-scan.log"
  $reportPathBackend = Join-Path $backendOut "parity_report.json"

  # Garante diretórios
  if (-not (Test-Path $backendOut)) { New-Item -ItemType Directory -Path $backendOut -Force | Out-Null }

  # Executa Alembic via módulo python para evitar erros de PATH do binário alembic
  # Importante: Alembic pode escrever INFO/WARN no stderr.
  # Usamos Start-Process com redirecionamento para evitar NativeCommandError espúrio.
  Write-Host "Executando Alembic..." -ForegroundColor Yellow

  $alembicArgs = @("-m", "alembic", "revision", "--autogenerate", "-m", $Message)
  $logPathBackendErr = Join-Path $backendOut "parity-scan.stderr.log"
  if (Test-Path $logPathBackend) { Remove-Item $logPathBackend -Force }
  if (Test-Path $logPathBackendErr) { Remove-Item $logPathBackendErr -Force }

  $proc = Start-Process -FilePath $pythonExe -ArgumentList $alembicArgs -NoNewWindow -Wait -PassThru -RedirectStandardOutput $logPathBackend -RedirectStandardError $logPathBackendErr
  $alembicExit = $proc.ExitCode

  if (Test-Path $logPathBackendErr) {
    $stderrLines = Get-Content $logPathBackendErr
    if ($stderrLines) {
      Add-Content -Path $logPathBackend -Value $stderrLines
      $stderrLines | ForEach-Object { Write-Host $_ }
    }
  }

  if ($alembicExit -ne 0) { throw "alembic revision falhou (exit $alembicExit)" }

  # 3) Classifica log em JSON
  Write-Host "Classificando discrepancias..." -ForegroundColor Yellow
  $classifyScript = Join-Path $RepoRoot "scripts\parity_classify.py"
  & $pythonExe $classifyScript --log $logPathBackend --out $reportPathBackend
  
  if ($LASTEXITCODE -ne 0) { throw "parity_classify.py falhou (exit $LASTEXITCODE)" }

  # 4) Validação de Diffs Estruturais
  if ($FailOnStructuralDiffs -and (Test-Path $reportPathBackend)) {
    $json = Get-Content $reportPathBackend -Raw | ConvertFrom-Json
    $count = $json.summary.structural_count
    if ($count -gt 0) {
      Write-Host "----------------------------------------------------" -ForegroundColor Red
      Write-Host "ERRO: Parity scan encontrou $count diffs estruturais!" -ForegroundColor Red
      Write-Host "Verifique: $reportPathBackend" -ForegroundColor Gray
      Write-Host "----------------------------------------------------" -ForegroundColor Red
      exit 2
    }
  }

  Write-Host "SUCESSO: Paridade validada ou sem diffs impeditivos." -ForegroundColor Green
  exit 0
}
catch {
  Write-Host "ERRO CRITICO: $($_.Exception.Message)" -ForegroundColor Red
  exit 1
}
finally {
  Pop-Location
}