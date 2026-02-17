#Requires -Version 5.1
<#
# HB_SCRIPT_KIND=CHECK
# HB_SCRIPT_SIDE_EFFECTS=FS_READ,PROCESS_SPAWN
# HB_SCRIPT_SCOPE=policy,governance,ci
# HB_SCRIPT_IDEMPOTENT=YES
# HB_SCRIPT_ENTRYPOINT=powershell -File scripts/checks/check_ci_gates_local.ps1
# HB_SCRIPT_OUTPUTS=exit_code,console

.SYNOPSIS
    HB Track — Validação Local de Todos os Gates de CI/CD

.DESCRIPTION
    Executa localmente todos os gates de validação que rodam no CI/CD do GitHub Actions.
    
    Gates incluídos:
    1. Scripts Policy (HB001-HB009)
    2. Governance Language Linter (promotional/conversational)
    3. Policy Manifest Hashes
    4. Policy Markdown Drift
    5. Path Constants Consistency
    6. Schema Drift (schema.sql vs live DB)
    7. Contract Drift (openapi.json vs live app)
    
    Use antes de push para evitar falhas no CI.

.PARAMETER SkipScriptsPolicy
    Pula validação de Scripts Policy

.PARAMETER SkipLanguageLinter
    Pula validação de linguagem em docs

.PARAMETER SkipManifest
    Pula validação de manifest hashes

.PARAMETER SkipDrift
    Pula validação de drift no SCRIPTS_classification.md

.PARAMETER SkipPathConstants
    Pula validação de constantes de path

.PARAMETER SkipSchemaDrift
    Pula validação de schema drift (requer DATABASE_URL)

.PARAMETER SkipContractDrift
    Pula validação de contract drift (requer FastAPI importável)

.PARAMETER FailFast
    Para na primeira falha (padrão: continua até o fim)

.OUTPUTS
    Exit codes:
      0 = OK (todos os gates passaram)
      1 = FAILURE (um ou mais gates falharam)
      3 = ERROR (erro de execução)

.EXAMPLE
    # Rodar todos os gates
    .\scripts\checks\check_ci_gates_local.ps1
    
    # Rodar só policy + language
    .\scripts\checks\check_ci_gates_local.ps1 -SkipManifest -SkipDrift -SkipPathConstants
    
    # Fail-fast (parar no primeiro erro)
    .\scripts\checks\check_ci_gates_local.ps1 -FailFast

.NOTES
    Version: 1.0.0
    Author: HB Track Team
    Simula: .github/workflows/scripts-policy.yml, governance-protocol-validation.yml
#>

[CmdletBinding()]
param(
    [switch]$SkipScriptsPolicy,
    [switch]$SkipLanguageLinter,
    [switch]$SkipManifest,
    [switch]$SkipDrift,
    [switch]$SkipPathConstants,
    [switch]$SkipSchemaDrift,
    [switch]$SkipContractDrift,
    [switch]$SkipDocsIndex,
    [switch]$FailFast
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

# Exit codes
$EXIT_OK = 0
$EXIT_FAILURE = 1
$EXIT_ERROR = 3

# Repo root
$RepoRoot = (Get-Item $PSScriptRoot).Parent.Parent.FullName
Set-Location $RepoRoot

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  HB TRACK — LOCAL CI/CD GATES" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Repo root: $RepoRoot" -ForegroundColor Gray
Write-Host ""

# Results tracker
$Results = @()
$HasFailure = $false

function Invoke-Gate {
    param(
        [string]$Name,
        [string]$Description,
        [scriptblock]$Command,
        [switch]$Skip
    )
    
    if ($Skip) {
        Write-Host "[$Name] SKIPPED" -ForegroundColor DarkGray
        $Results += [pscustomobject]@{
            Gate = $Name
            Status = "SKIP"
            ExitCode = "-"
        }
        return
    }
    
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Yellow
    Write-Host "Gate: $Name" -ForegroundColor Yellow
    Write-Host "========================================" -ForegroundColor Yellow
    Write-Host "$Description" -ForegroundColor Gray
    Write-Host ""
    
    try {
        & $Command
        $ExitCode = $LASTEXITCODE
        
        if ($ExitCode -eq 0) {
            Write-Host "[$Name] PASS ✅" -ForegroundColor Green
            $Results += [pscustomobject]@{
                Gate = $Name
                Status = "PASS"
                ExitCode = $ExitCode
            }
        } else {
            Write-Host "[$Name] FAIL ❌ (exit=$ExitCode)" -ForegroundColor Red
            $script:HasFailure = $true
            $Results += [pscustomobject]@{
                Gate = $Name
                Status = "FAIL"
                ExitCode = $ExitCode
            }
            
            if ($FailFast) {
                Write-Host ""
                Write-Host "[FAIL-FAST] Parando na primeira falha." -ForegroundColor Red
                throw "Gate $Name falhou com exit code $ExitCode"
            }
        }
    } catch {
        Write-Host "[$Name] ERROR ⚠️ : $_" -ForegroundColor Magenta
        $script:HasFailure = $true
        $Results += [pscustomobject]@{
            Gate = $Name
            Status = "ERROR"
            ExitCode = "!"
        }
        
        if ($FailFast) {
            throw
        }
    }
}

# ========================================
# GATE 1: Scripts Policy
# ========================================
Invoke-Gate -Name "Scripts Policy" `
    -Description "Valida HB_SCRIPT headers, prefixos, side-effects (HB001-HB009)" `
    -Command {
        & 'scripts\_policy\check_scripts_policy.ps1'
    } `
    -Skip:$SkipScriptsPolicy

# ========================================
# GATE 2: Governance Language Linter
# ========================================
Invoke-Gate -Name "Language Protocol" `
    -Description "Detecta linguagem promocional/conversacional em docs canônicos" `
    -Command {
        # Encontrar Python (venv ou system)
        $PythonExe = $null
        $VenvPython = Join-Path $RepoRoot "Hb Track - Backend\venv\Scripts\python.exe"
        if (Test-Path $VenvPython) {
            $PythonExe = $VenvPython
        } else {
            $PythonExe = (Get-Command python -ErrorAction SilentlyContinue).Source
        }
        
        if (-not $PythonExe) {
            Write-Host "[ERROR] Python não encontrado" -ForegroundColor Red
            exit 3
        }
        
        & $PythonExe "docs\scripts\_ia\ai_governance_linter.py"
    } `
    -Skip:$SkipLanguageLinter

# ========================================
# GATE 3: Policy Manifest Hashes
# ========================================
Invoke-Gate -Name "Manifest Integrity" `
    -Description "Valida integridade de hashes no policy.manifest.json" `
    -Command {
        & 'scripts\_policy\check_policy_manifest.ps1'
    } `
    -Skip:$SkipManifest

# ========================================
# GATE 4: Policy Markdown Drift
# ========================================
Invoke-Gate -Name "Policy MD Sync" `
    -Description "Valida SCRIPTS_classification.md está sincronizado com YAML" `
    -Command {
        & 'scripts\_policy\check_policy_md_is_derived.ps1'
    } `
    -Skip:$SkipDrift

# ========================================
# GATE 5: Path Constants Consistency
# ========================================
Invoke-Gate -Name "Path Constants" `
    -Description "Valida constantes Python/PowerShell idênticas" `
    -Command {
        # Encontrar Python
        $PythonExe = $null
        $VenvPython = Join-Path $RepoRoot "Hb Track - Backend\venv\Scripts\python.exe"
        if (Test-Path $VenvPython) {
            $PythonExe = $VenvPython
        } else {
            $PythonExe = (Get-Command python -ErrorAction SilentlyContinue).Source
        }
        
        if (-not $PythonExe) {
            Write-Host "[ERROR] Python não encontrado" -ForegroundColor Red
            exit 3
        }
        
        $Output = & $PythonExe "scripts\_policy\check_path_constants.py" | ConvertFrom-Json
        if ($Output) {
            Write-Host "Path constants valid" -ForegroundColor Green
            exit 0
        } else {
            Write-Host "[ERROR] Invalid output from check_path_constants.py" -ForegroundColor Red
            exit 3
        }
    } `
    -Skip:$SkipPathConstants

# ========================================
# GATE 6: Schema Drift
# ========================================
Invoke-Gate -Name "Schema Drift" `
    -Description "Compara schema.sql (SSOT) com o schema live do banco de dados" `
    -Command {
        $PythonExe = $null
        $VenvPython = Join-Path $RepoRoot "Hb Track - Backend\venv\Scripts\python.exe"
        if (Test-Path $VenvPython) {
            $PythonExe = $VenvPython
        } else {
            $PythonExe = (Get-Command python -ErrorAction SilentlyContinue).Source
        }
        
        if (-not $PythonExe) {
            Write-Host "[ERROR] Python não encontrado" -ForegroundColor Red
            exit 3
        }
        
        & $PythonExe "scripts\checks\db\check_schema_drift.py"
    } `
    -Skip:$SkipSchemaDrift

# ========================================
# GATE 7: Contract Drift
# ========================================
Invoke-Gate -Name "Contract Drift" `
    -Description "Compara openapi.json (SSOT) com o contrato live da FastAPI app" `
    -Command {
        $PythonExe = $null
        $VenvPython = Join-Path $RepoRoot "Hb Track - Backend\venv\Scripts\python.exe"
        if (Test-Path $VenvPython) {
            $PythonExe = $VenvPython
        } else {
            $PythonExe = (Get-Command python -ErrorAction SilentlyContinue).Source
        }
        
        if (-not $PythonExe) {
            Write-Host "[ERROR] Python não encontrado" -ForegroundColor Red
            exit 3
        }
        
        & $PythonExe "scripts\checks\openapi\check_contract_drift.py"
    } `
    -Skip:$SkipContractDrift

# ========================================
# GATE 8: Docs Index
# ========================================
Invoke-Gate -Name "Docs Index" `
    -Description "Valida docs/_INDEX.yaml (schema, IDs únicos, paths existentes)" `
    -Command {
        & 'scripts\checks\docs\check_docs_index.ps1'
    } `
    -Skip:$SkipDocsIndex

# ========================================
# SUMMARY
# ========================================
Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  SUMMARY" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

$Results | Format-Table -AutoSize

$PassCount = ($Results | Where-Object { $_.Status -eq "PASS" }).Count
$FailCount = ($Results | Where-Object { $_.Status -eq "FAIL" -or $_.Status -eq "ERROR" }).Count
$SkipCount = ($Results | Where-Object { $_.Status -eq "SKIP" }).Count
$TotalCount = $Results.Count

Write-Host ""
Write-Host "Total gates: $TotalCount" -ForegroundColor Gray
Write-Host "  PASS: $PassCount" -ForegroundColor Green
Write-Host "  FAIL: $FailCount" -ForegroundColor $(if ($FailCount -gt 0) { "Red" } else { "Gray" })
Write-Host "  SKIP: $SkipCount" -ForegroundColor DarkGray
Write-Host ""

if ($HasFailure) {
    Write-Host "❌ LOCAL GATES FAILED - Corrija os erros antes de push" -ForegroundColor Red
    Write-Host ""
    Write-Host "Próximos passos:" -ForegroundColor Yellow
    Write-Host "  1. Revise os erros acima" -ForegroundColor White
    Write-Host "  2. Corrija os arquivos violando policy/protocolo" -ForegroundColor White
    Write-Host "  3. Re-execute: .\scripts\checks\check_ci_gates_local.ps1" -ForegroundColor White
    Write-Host ""
    exit $EXIT_FAILURE
} else {
    Write-Host "✅ ALL GATES PASS - Safe to push!" -ForegroundColor Green
    Write-Host ""
    exit $EXIT_OK
}
