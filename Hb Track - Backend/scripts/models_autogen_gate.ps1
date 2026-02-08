param(
  [Parameter(Mandatory=$true)][string]$Table,
  [switch]$Create,
  [ValidateSet("fk", "strict", "lenient")][string]$Profile = "strict",
  [string]$ModelFile = "",
  [string]$ClassName = "",
  [string[]]$Allow = @(),
  [string]$DbUrl = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Invoke-External {
  param(
    [Parameter(Mandatory=$true)][string]$Command,
    [Parameter()][string[]]$Arguments = @(),
    [Parameter(Mandatory=$true)][string]$Step
  )

  & $Command @Arguments
  $exitCode = $LASTEXITCODE

  if (-not $?) {
    throw "[$Step] failed to execute command: $Command"
  }

  if ($exitCode -ne 0) {
    Write-Host "[FAIL] [$Step] exited with code $exitCode" -ForegroundColor Red
    exit $exitCode
  }
}

function Resolve-ModelFileForTable {
  param(
    [Parameter(Mandatory=$true)][string]$Table,
    [Parameter(Mandatory=$true)][string]$RootPath
  )

  $escapedTable = [regex]::Escape($Table)
  $pattern = "__tablename__\s*=\s*['`"]$escapedTable['`"]"
  $hit = Select-String -Path "app\models\*.py" -Pattern $pattern -ErrorAction SilentlyContinue | Select-Object -First 1

  if ($hit) {
    $resolvedPath = $hit.Path
    if ($resolvedPath.StartsWith($RootPath, [System.StringComparison]::OrdinalIgnoreCase)) {
      $resolvedPath = $resolvedPath.Substring($RootPath.Length).TrimStart('\', '/')
    }
    return ($resolvedPath -replace '\\', '/')
  }

  return ((Join-Path "app/models" "$Table.py") -replace '\\', '/')
}

try {
  $SCRIPT_ROOT = $PSScriptRoot
  $ROOT = (Resolve-Path (Join-Path $SCRIPT_ROOT "..")).Path
  Write-Host "[CWD] $((Resolve-Path ".").Path)"
  Write-Host "[ROOT] $ROOT"
  Write-Host "[TABLE] $Table"

  # evita geração de __pycache__/.pyc em execuções python deste gate
  $env:PYTHONDONTWRITEBYTECODE = "1"
  $env:PYTHONPYCACHEPREFIX = Join-Path $ROOT ".hb_guard\pycache"
  New-Item -ItemType Directory -Force -Path $env:PYTHONPYCACHEPREFIX | Out-Null

  $dbEnvName = "DATABASE_URL_SYNC"

  if (-not [string]::IsNullOrWhiteSpace($DbUrl)) {
    [System.Environment]::SetEnvironmentVariable($dbEnvName, $DbUrl, "Process")
    Write-Host "[INFO] using -DbUrl override for $dbEnvName"
  } else {
    $dbSync = [System.Environment]::GetEnvironmentVariable($dbEnvName, "Process")
    if ([string]::IsNullOrWhiteSpace($dbSync)) {
      $loadEnv = Join-Path $SCRIPT_ROOT "_load_env.ps1"
      if (Test-Path $loadEnv) {
        . $loadEnv -EnvPath (Join-Path $ROOT ".env")
        $dbSync = [System.Environment]::GetEnvironmentVariable($dbEnvName, "Process")
      }
    }

    if ([string]::IsNullOrWhiteSpace($dbSync)) {
      $dbUrl = [System.Environment]::GetEnvironmentVariable("DATABASE_URL", "Process")
      if (-not [string]::IsNullOrWhiteSpace($dbUrl)) {
        # fallback: converte URL async para sync quando necessário
        if ($dbUrl.StartsWith("postgresql+asyncpg://")) {
          $dbSync = $dbUrl -replace "^postgresql\+asyncpg://", "postgresql+psycopg2://"
        } else {
          $dbSync = $dbUrl
        }
        [System.Environment]::SetEnvironmentVariable($dbEnvName, $dbSync, "Process")
        Write-Host "[INFO] fallback DATABASE_URL -> $dbEnvName"
      }
    }
  }

  if ([string]::IsNullOrWhiteSpace([System.Environment]::GetEnvironmentVariable($dbEnvName, "Process"))) {
    throw "env var not set: $dbEnvName (nem -DbUrl, nem .env/DATABASE_URL disponíveis)"
  }

  $venvPy = Join-Path $ROOT "venv\Scripts\python.exe"
  if (Test-Path $venvPy) { $py = $venvPy } else { $py = "python" }

  $autogenScript = Join-Path $SCRIPT_ROOT "autogen_model_from_db.py"
  $agentGuardScript = Join-Path $SCRIPT_ROOT "agent_guard.py"
  $parityGateScript = Join-Path $SCRIPT_ROOT "parity_gate.ps1"
  $modelRequirementsScript = Join-Path $SCRIPT_ROOT "model_requirements.py"

  Push-Location $ROOT
  try {
    $resolvedModelFile = $ModelFile
    if ([string]::IsNullOrWhiteSpace($resolvedModelFile)) {
      $resolvedModelFile = Resolve-ModelFileForTable -Table $Table -RootPath $ROOT
    }

    $modelPath = $resolvedModelFile
    if ([string]::IsNullOrWhiteSpace($modelPath)) { $modelPath = "app/models/$Table.py" }
    $allowFinal = @($Allow + @($modelPath) | Select-Object -Unique)

    # pre-check: parity can fail before autogen; do not abort here
    & $parityGateScript -Table $Table -Allow $allowFinal
    $preExit = $LASTEXITCODE
    if (-not $?) {
      Write-Host "[WARN] pre parity_gate execution had errors; continuing to autogen." -ForegroundColor Yellow
    }
    if ($preExit -ne 0) {
      Write-Host "[WARN] pre parity_gate failed (exit=$preExit); continuing to autogen to attempt fix." -ForegroundColor Yellow
    }

    $autogenArgs = @($autogenScript, "apply", "--table", $Table, "--db-env", $dbEnvName)
    if ($Create) { $autogenArgs += "--create" }
    if (-not [string]::IsNullOrWhiteSpace($resolvedModelFile)) { $autogenArgs += @("--model-file", $resolvedModelFile) }
    if ($ClassName) { $autogenArgs += @("--class-name", $ClassName) }

    Invoke-External -Command $py -Arguments $autogenArgs -Step "autogen_model_from_db"

    if ($Create) {
      $snapshotArgs = @($agentGuardScript, "snapshot", "--root", ".", "--out", ".hb_guard\baseline.json", "--exclude", "venv,.venv,__pycache__,.pytest_cache,docs\_generated")
      Invoke-External -Command $py -Arguments $snapshotArgs -Step "agent_guard snapshot"
    }

    # post-check: this one defines final gate result
    & $parityGateScript -Table $Table -Allow $allowFinal
    $parityExit = $LASTEXITCODE
    if (-not $?) {
      throw "[parity_gate] failed to execute parity gate"
    }
    if ($parityExit -ne 0) {
      Write-Host "[FAIL] [parity_gate] exited with code $parityExit" -ForegroundColor Red
      exit $parityExit
    }

    # STEP 4: model requirements validation (must propagate exact exit code)
    $requirementsArgs = @($modelRequirementsScript, "--table", $Table, "--profile", $Profile)
    & $py @requirementsArgs
    $requirementsExit = $LASTEXITCODE
    if (-not $?) {
      throw "[model_requirements] failed to execute requirements validator"
    }
    if ($requirementsExit -ne 0) {
      Write-Host "[FAIL] [model_requirements] exited with code $requirementsExit" -ForegroundColor Red
      exit $requirementsExit
    }
  }
  finally {
    Pop-Location
  }

  exit 0
}
catch {
  Write-Host "[FAIL] models_autogen_gate failed: $($_.Exception.Message)" -ForegroundColor Red
  exit 1
}