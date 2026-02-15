#Requires -Version 5.1
# HB_SCRIPT_KIND: CHECK
# HB_SCRIPT_SCOPE: docs
# HB_SCRIPT_SIDE_EFFECTS: FS_WRITE
# HB_SCRIPT_IDEMPOTENT: true
# HB_SCRIPT_ENTRYPOINT: scripts/checks/docs/check_policy_determinism.ps1
# HB_SCRIPT_OUTPUTS: tests/policy_scripts/evidence/

<#
.SYNOPSIS
    Valida determinismo do gate de scripts policy
.DESCRIPTION
    Roda o gate 3x e compara outputs (devem ser idênticos).
    Salva evidências em tests/policy_scripts/evidence/.
    
    Exit codes:
      0 = DETERMINISMO PROVADO (3 runs idênticos)
      2 = FALHA (outputs divergem)
      3 = ERRO (gate não executou)
#>

[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$RepoRoot = "C:\HB TRACK"
$EvidenceDir = Join-Path $RepoRoot "tests\policy_scripts\evidence"
$Gate = Join-Path $RepoRoot "scripts\_policy\check_scripts_policy.ps1"

Write-Host "`n[check_policy_determinism] Validando determinismo do gate..." -ForegroundColor Cyan
Write-Host "[INFO] Gate: $Gate" -ForegroundColor Gray
Write-Host "[INFO] Evidence: $EvidenceDir" -ForegroundColor Gray

# Criar diretório de evidências
if (-not (Test-Path $EvidenceDir)) {
    New-Item -ItemType Directory -Path $EvidenceDir -Force | Out-Null
    Write-Host "[INFO] Criado diretório de evidências" -ForegroundColor Gray
}

# Capturar estado do ambiente
$EnvFile = Join-Path $EvidenceDir "env.txt"
@"
Python Version:
$(& python --version 2>&1)

Git Version:
$(& git --version)

PowerShell Version:
$($PSVersionTable.PSVersion)

Date (UTC):
$((Get-Date).ToUniversalTime().ToString("yyyy-MM-dd HH:mm:ss"))
"@ | Set-Content -Path $EnvFile -Encoding UTF8

Write-Host "[INFO] Ambiente capturado: $EnvFile" -ForegroundColor Gray

# Capturar estado do git
$GitStateFile = Join-Path $EvidenceDir "git_state.txt"
@"
Commit:
$(git -C $RepoRoot rev-parse HEAD)

Status:
$(git -C $RepoRoot status --porcelain)
"@ | Set-Content -Path $GitStateFile -Encoding UTF8

Write-Host "[INFO] Estado git capturado: $GitStateFile" -ForegroundColor Gray

# Capturar comando exato
$CommandFile = Join-Path $EvidenceDir "command.txt"
@"
Command executed:
& '$Gate'

Working directory:
$RepoRoot

Executed at (UTC):
$((Get-Date).ToUniversalTime().ToString("yyyy-MM-dd HH:mm:ss"))
"@ | Set-Content -Path $CommandFile -Encoding UTF8

Write-Host "[INFO] Comando capturado: $CommandFile`n" -ForegroundColor Gray

# Executar gate 3x
$Outputs = @()
$ExitCodes = @()

for ($i = 1; $i -le 3; $i++) {
    Write-Host "[Run $i/3] Executando gate..." -ForegroundColor Cyan
    
    $OutputFile = Join-Path $EvidenceDir "run_log_$i.txt"
    
    try {
        # Roda gate e captura output + exit code
        $Output = & $Gate 2>&1 | Out-String
        $ExitCode = $LASTEXITCODE
        
        # Salva output
        $Output | Set-Content -Path $OutputFile -Encoding UTF8
        
        $Outputs += $Output
        $ExitCodes += $ExitCode
        
        Write-Host "  Exit code: $ExitCode" -ForegroundColor Gray
        Write-Host "  Output salvo: $OutputFile" -ForegroundColor Gray
    }
    catch {
        Write-Error "[ERRO] Falha ao executar gate: $_"
        exit 3
    }
}

Write-Host "`n[ANÁLISE] Comparando outputs..." -ForegroundColor Cyan

# Comparar exit codes
$ExitCodesUnique = $ExitCodes | Sort-Object -Unique
$UniqueCount = @($ExitCodesUnique).Count
if ($UniqueCount -ne 1) {
    Write-Host "[FAIL] Exit codes divergem: $($ExitCodes -join ', ')" -ForegroundColor Red
    exit 2
}

Write-Host "[OK] Exit codes consistentes: $($ExitCodes[0])" -ForegroundColor Green

# Comparar outputs (normalizar line endings)
$Output1_Lines = $Outputs[0] -split "`r?`n"
$Output2_Lines = $Outputs[1] -split "`r?`n"
$Output3_Lines = $Outputs[2] -split "`r?`n"

# Diff 1 vs 2
$Diff12 = Compare-Object -ReferenceObject $Output1_Lines -DifferenceObject $Output2_Lines
$Diff12File = Join-Path $EvidenceDir "diff_1_vs_2.txt"
if ($Diff12) {
    $Diff12 | Format-Table | Out-String | Set-Content -Path $Diff12File -Encoding UTF8
    Write-Host "[FAIL] Outputs 1 e 2 divergem (ver diff_1_vs_2.txt)" -ForegroundColor Red
    $Diff12 | Format-Table -AutoSize
    exit 2
} else {
    "No differences" | Set-Content -Path $Diff12File -Encoding UTF8
    Write-Host "[OK] Outputs 1 e 2 idênticos" -ForegroundColor Green
}

# Diff 2 vs 3
$Diff23 = Compare-Object -ReferenceObject $Output2_Lines -DifferenceObject $Output3_Lines
$Diff23File = Join-Path $EvidenceDir "diff_2_vs_3.txt"
if ($Diff23) {
    $Diff23 | Format-Table | Out-String | Set-Content -Path $Diff23File -Encoding UTF8
    Write-Host "[FAIL] Outputs 2 e 3 divergem (ver diff_2_vs_3.txt)" -ForegroundColor Red
    $Diff23 | Format-Table -AutoSize
    exit 2
} else {
    "No differences" | Set-Content -Path $Diff23File -Encoding UTF8
    Write-Host "[OK] Outputs 2 e 3 idênticos" -ForegroundColor Green
}

# Sucesso: determinismo provado
Write-Host "`n[DETERMINISMO PROVADO] ✓" -ForegroundColor Green
Write-Host "  3 runs executados" -ForegroundColor Gray
Write-Host "  Outputs idênticos (diff = 0)" -ForegroundColor Gray
Write-Host "  Exit codes estáveis ($($ExitCodes[0]))" -ForegroundColor Gray
Write-Host "  Evidências salvas em: $EvidenceDir" -ForegroundColor Gray

exit 0
