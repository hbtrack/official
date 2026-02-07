# scripts/sync_openapi.ps1
# Sincroniza contrato local de OpenAPI do backend
# Uso: powershell -ExecutionPolicy Bypass -File scripts/sync_openapi.ps1

param(
  [string]$BackendRepo = "C:\HB TRACK\Hb Track - Backend",
  [int]$WarningThresholdDays = 7,
  [int]$ErrorThresholdDays = 30
)

$src = Join-Path $BackendRepo "docs\_generated\openapi.json"
$dstDir = "docs\_generated"
$dst = Join-Path $dstDir "openapi.json"

# Validar existência da fonte
if (!(Test-Path $src)) {
  Write-Error "OpenAPI source not found: $src"
  Write-Error "Backend precisa gerar: python scripts/generate_docs.py --openapi"
  exit 1
}

# Criar diretório de destino se não existir
if (!(Test-Path $dstDir)) {
  New-Item -ItemType Directory -Force $dstDir | Out-Null
}

# Copiar arquivo
Copy-Item $src $dst -Force

# Validação de freshness
$srcFile = Get-Item $src
$age = (Get-Date) - $srcFile.LastWriteTime
$ageDays = [math]::Round($age.TotalDays, 1)

Write-Host "Synced OpenAPI: $src -> $dst"
Write-Host "Source age: $ageDays days"

if ($ageDays -gt $ErrorThresholdDays) {
  Write-Warning "OpenAPI é muito antigo (> $ErrorThresholdDays dias)"
  Write-Warning "Backend deve gerar: python scripts/generate_docs.py --openapi"
} elseif ($ageDays -gt $WarningThresholdDays) {
  Write-Host "OpenAPI tem $ageDays dias. Considere sincronizar novamente."
}