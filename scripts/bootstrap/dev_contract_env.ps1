Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$VenvDir = if ($env:HB_CONTRACT_VENV_DIR) { $env:HB_CONTRACT_VENV_DIR } else { Join-Path $RepoRoot ".venv-contract" }
$VenvPy = Join-Path $VenvDir "Scripts\python.exe"
$NodeBin = Join-Path $RepoRoot "node_modules\.bin"
$ReqFile = Join-Path $RepoRoot "scripts\bootstrap\requirements-contract-dev.txt"

function Require-Command {
  param([string]$Name)
  if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
    throw "Comando obrigatório ausente: $Name"
  }
}

function New-ContractVenv {
  param([string]$TargetDir)
  try {
    python -m venv $TargetDir
    return
  } catch {
    if (python -m virtualenv --version *> $null) {
      Write-Host "python -m venv indisponível; tentando fallback com virtualenv ..."
      python -m virtualenv $TargetDir
      return
    }
    throw "Nao foi possivel criar o virtualenv local. Instale python3-venv/ensurepip ou execute: python -m pip install --user virtualenv"
  }
}

function Test-ContractVenvReady {
  param([string]$PythonExe)
  if (-not (Test-Path $PythonExe)) {
    return $false
  }
  & $PythonExe -m pip --version *> $null
  return $LASTEXITCODE -eq 0
}

Write-Host "══ HB Track Contract Dev Bootstrap ══"
Require-Command python
Require-Command node
Require-Command npm

if (-not (Test-Path $ReqFile)) {
  throw "Manifesto de bootstrap ausente: $ReqFile"
}

if (-not (Test-Path $VenvDir)) {
  Write-Host "Criando virtualenv local em $VenvDir ..."
  New-ContractVenv -TargetDir $VenvDir
} elseif (-not (Test-ContractVenvReady -PythonExe $VenvPy)) {
  if ($VenvDir -eq (Join-Path $RepoRoot ".venv-contract")) {
    Write-Host "Virtualenv local inconsistente; recriando $VenvDir ..."
    Remove-Item -Recurse -Force $VenvDir
    New-ContractVenv -TargetDir $VenvDir
  } else {
    throw "Virtualenv existente sem pip funcional: $VenvDir. Remova o diretório ou aponte HB_CONTRACT_VENV_DIR para outro local."
  }
}

Write-Host "Verificando pip no virtualenv local ..."
if (-not (Test-ContractVenvReady -PythonExe $VenvPy)) {
  throw "pip ausente no virtualenv local: $VenvPy"
}

Write-Host "Instalando dependências Python de governança ..."
$env:PIP_DISABLE_PIP_VERSION_CHECK = "1"
& $VenvPy -m pip install -r $ReqFile

Write-Host "Sincronizando dependências Node com npm ci ..."
Push-Location $RepoRoot
try {
  npm ci
} finally {
  Pop-Location
}

if (Test-Path $NodeBin) {
  $env:PATH = "$NodeBin;$env:PATH"
}

Write-Host "Verificando módulos Python mínimos ..."
$PyCheck = @'
import importlib.util
missing = [name for name in ["pytest", "schemathesis", "yaml", "jsonschema"] if importlib.util.find_spec(name) is None]
if missing:
    raise SystemExit("Módulos Python ausentes: " + ", ".join(missing))
'@
& $VenvPy -c $PyCheck

Write-Host "Verificando toolchain de contratos ..."
foreach ($tool in @("oasdiff", "redocly", "spectral", "asyncapi")) {
  Require-Command $tool
}

Write-Host "✅ PASS — ambiente local pronto."
Write-Host "Python de contratos: $VenvPy"
