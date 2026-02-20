# HB_SCRIPT_KIND=OPS
# HB_SCRIPT_SCOPE=infra
# HB_SCRIPT_SIDE_EFFECTS=PROC_START_STOP
# HB_SCRIPT_IDEMPOTENT=YES
# HB_SCRIPT_ENTRYPOINT=powershell -File scripts/ops/inv.ps1
# HB_SCRIPT_OUTPUTS=stdout
#!/usr/bin/env pwsh
#
# inv.ps1
# Wrapper unificado para comandos de invariantes (reduz erro humano/agent)
#
# Usage:
#   .\scripts\inv.ps1 gate INV-TRAIN-015    # Executa gate individual
#   .\scripts\inv.ps1 all                   # Executa gate all
#   .\scripts\inv.ps1 drift                 # Executa gate all -WhatIf (dry-run)
#   .\scripts\inv.ps1 promote               # Executa gate all -Promote (bulk)
#   .\scripts\inv.ps1 refresh               # Regenera artefatos canônicos (SSOT)
#

param(
    [Parameter(Position=0, Mandatory=$true)]
    [ValidateSet('gate', 'all', 'drift', 'promote', 'refresh', 'ssot')]
    [string]$Command,
    
    [Parameter(Position=1)]
    [string]$InvId = ""
)

$ErrorActionPreference = "Stop"

# Paths
$ScriptRoot = $PSScriptRoot
$RootDir = Split-Path -Parent (Split-Path -Parent $ScriptRoot)   # scripts/ops → scripts → repo root
$GateScript = Join-Path $RootDir "scripts\run\run_invariant_gate.ps1"
$GateAllScript = Join-Path $RootDir "scripts\run\run_invariant_gate_all.ps1"

# Guardrail: validate repo root
if (-not (Test-Path (Join-Path $RootDir "AGENTS.md"))) {
    Write-Host "FATAL: repo root not found at $RootDir (missing AGENTS.md)" -ForegroundColor Red
    exit 1
}

# Header
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "INV WRAPPER" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "COMMAND:  $Command" -ForegroundColor White
Write-Host "ROOT:     $RootDir" -ForegroundColor White

# Dispatch
switch ($Command) {
    'gate' {
        if ([string]::IsNullOrWhiteSpace($InvId)) {
            Write-Host "ERROR: INV-ID required for 'gate' command" -ForegroundColor Red
            Write-Host "Usage: .\scripts\inv.ps1 gate INV-TRAIN-XXX" -ForegroundColor Yellow
            exit 1
        }
        
        Write-Host "MODE:     GATE INDIVIDUAL ($InvId)" -ForegroundColor White
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host ""
        
        # Executar gate individual
        & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $GateScript $InvId
        $ExitCode = $LASTEXITCODE
        
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host "WRAPPER EXIT CODE: $ExitCode" -ForegroundColor $(if ($ExitCode -eq 0) { "Green" } elseif ($ExitCode -eq 3) { "Yellow" } else { "Red" })
        Write-Host "========================================" -ForegroundColor Cyan
        
        exit $ExitCode
    }
    
    'all' {
        Write-Host "MODE:     GATE ALL" -ForegroundColor White
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host ""
        
        # Executar gate all
        & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $GateAllScript
        $ExitCode = $LASTEXITCODE
        
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host "WRAPPER EXIT CODE: $ExitCode" -ForegroundColor $(if ($ExitCode -eq 0) { "Green" } elseif ($ExitCode -eq 3) { "Yellow" } else { "Red" })
        Write-Host "========================================" -ForegroundColor Cyan
        
        exit $ExitCode
    }
    
    'drift' {
        Write-Host "MODE:     DRIFT CHECK (WhatIf)" -ForegroundColor White
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host ""
        
        # Executar gate all com -WhatIf
        & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $GateAllScript -WhatIf
        $ExitCode = $LASTEXITCODE
        
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host "WRAPPER EXIT CODE: $ExitCode" -ForegroundColor $(if ($ExitCode -eq 0) { "Green" } elseif ($ExitCode -eq 3) { "Yellow" } else { "Red" })
        Write-Host "========================================" -ForegroundColor Cyan
        
        exit $ExitCode
    }
    
    'promote' {
        Write-Host "MODE:     PROMOTE (Bulk)" -ForegroundColor White
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host ""
        
        # Executar gate all com -Promote
        & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $GateAllScript -Promote
        $ExitCode = $LASTEXITCODE
        
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host "WRAPPER EXIT CODE: $ExitCode" -ForegroundColor $(if ($ExitCode -eq 0) { "Green" } elseif ($ExitCode -eq 3) { "Yellow" } else { "Red" })
        Write-Host "========================================" -ForegroundColor Cyan
        
        exit $ExitCode
    }
    
    { $_ -in 'refresh', 'ssot' } {
        Write-Host "MODE:     REFRESH CANONICAL ARTIFACTS (SSOT)" -ForegroundColor White
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host ""
        
        # Paths dos artefatos canônicos
        $BackendDir = Join-Path $RootDir "Hb Track - Backend"
        $SchemaFile = Join-Path $BackendDir "docs\_generated\schema.sql"
        $OpenApiFile = Join-Path $BackendDir "docs\_generated\openapi.json"
        $AlembicFile = Join-Path $BackendDir "docs\_generated\alembic_state.txt"
        $GenerateScript = Join-Path $RootDir "scripts\generate\docs\gen_docs_soot.py"

        # Repo root mirror (SSOT canônico consumido pelas docs/agentes)
        $RepoGeneratedDir = Join-Path $RootDir "docs\_generated"
        $RepoSchemaFile = Join-Path $RepoGeneratedDir "schema.sql"
        $RepoOpenApiFile = Join-Path $RepoGeneratedDir "openapi.json"
        $RepoAlembicFile = Join-Path $RepoGeneratedDir "alembic_state.txt"
        
        # Validar que gen_docs_soot.py existe
        if (-not (Test-Path $GenerateScript)) {
            Write-Host "ERROR: gen_docs_soot.py not found at $GenerateScript" -ForegroundColor Red
            exit 1
        }
        
        Write-Host "Executing: python $GenerateScript --all" -ForegroundColor Yellow
        Write-Host ""
        
        # Executar gen_docs_soot.py --all
        Push-Location $BackendDir
        try {
            & python $GenerateScript --all
            $ExitCode = $LASTEXITCODE
            
            if ($ExitCode -ne 0) {
                Write-Host ""
                Write-Host "ERROR: gen_docs_soot.py failed with exit code $ExitCode" -ForegroundColor Red
                exit $ExitCode
            }
        } finally {
            Pop-Location
        }
        
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host "VALIDATING CANONICAL ARTIFACTS" -ForegroundColor Cyan
        Write-Host "========================================" -ForegroundColor Cyan
        
        # Validar que os 3 artefatos foram gerados
        $AllArtifactsExist = $true
        
        if (Test-Path $SchemaFile) {
            $SchemaSize = (Get-Item $SchemaFile).Length
            Write-Host "[OK] schema.sql ($SchemaSize bytes)" -ForegroundColor Green
        } else {
            Write-Host "[FAIL] schema.sql NOT FOUND" -ForegroundColor Red
            $AllArtifactsExist = $false
        }
        
        if (Test-Path $OpenApiFile) {
            $OpenApiSize = (Get-Item $OpenApiFile).Length
            Write-Host "[OK] openapi.json ($OpenApiSize bytes)" -ForegroundColor Green
        } else {
            Write-Host "[FAIL] openapi.json NOT FOUND" -ForegroundColor Red
            $AllArtifactsExist = $false
        }
        
        if (Test-Path $AlembicFile) {
            $AlembicSize = (Get-Item $AlembicFile).Length
            Write-Host "[OK] alembic_state.txt ($AlembicSize bytes)" -ForegroundColor Green
        } else {
            Write-Host "[FAIL] alembic_state.txt NOT FOUND" -ForegroundColor Red
            $AllArtifactsExist = $false
        }

        Write-Host ""

        # Validar mirror em docs/ssot (repo root). SSOT canônico para docs/agentes.
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host "VALIDATING REPO ROOT MIRROR (docs/ssot)" -ForegroundColor Cyan
        Write-Host "========================================" -ForegroundColor Cyan

        if (Test-Path $RepoSchemaFile) {
            $RepoSchemaSize = (Get-Item $RepoSchemaFile).Length
            if ((Test-Path $SchemaFile) -and $RepoSchemaSize -ne (Get-Item $SchemaFile).Length) {
                Write-Host "[FAIL] docs/ssot/schema.sql size mismatch vs backend copy" -ForegroundColor Red
                $AllArtifactsExist = $false
            } else {
                Write-Host "[OK] docs/ssot/schema.sql ($RepoSchemaSize bytes)" -ForegroundColor Green
            }
        } else {
            Write-Host "[FAIL] docs/ssot/schema.sql NOT FOUND" -ForegroundColor Red
            $AllArtifactsExist = $false
        }

        if (Test-Path $RepoOpenApiFile) {
            $RepoOpenApiSize = (Get-Item $RepoOpenApiFile).Length
            if ((Test-Path $OpenApiFile) -and $RepoOpenApiSize -ne (Get-Item $OpenApiFile).Length) {
                Write-Host "[FAIL] docs/ssot/openapi.json size mismatch vs backend copy" -ForegroundColor Red
                $AllArtifactsExist = $false
            } else {
                Write-Host "[OK] docs/ssot/openapi.json ($RepoOpenApiSize bytes)" -ForegroundColor Green
            }
        } else {
            Write-Host "[FAIL] docs/ssot/openapi.json NOT FOUND" -ForegroundColor Red
            $AllArtifactsExist = $false
        }

        if (Test-Path $RepoAlembicFile) {
            $RepoAlembicSize = (Get-Item $RepoAlembicFile).Length
            if ((Test-Path $AlembicFile) -and $RepoAlembicSize -ne (Get-Item $AlembicFile).Length) {
                Write-Host "[FAIL] docs/ssot/alembic_state.txt size mismatch vs backend copy" -ForegroundColor Red
                $AllArtifactsExist = $false
            } else {
                Write-Host "[OK] docs/ssot/alembic_state.txt ($RepoAlembicSize bytes)" -ForegroundColor Green
            }
        } else {
            Write-Host "[FAIL] docs/ssot/alembic_state.txt NOT FOUND" -ForegroundColor Red
            $AllArtifactsExist = $false
        }

        Write-Host ""
        
        if (-not $AllArtifactsExist) {
            Write-Host "========================================" -ForegroundColor Cyan
            Write-Host "WRAPPER EXIT CODE: 1" -ForegroundColor Red
            Write-Host "========================================" -ForegroundColor Cyan
            exit 1
        }
        
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host "WRAPPER EXIT CODE: 0" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Cyan
        exit 0
    }
}
