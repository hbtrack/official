# HB_SCRIPT_KIND: GENERATE
# HB_SCRIPT_SIDE_EFFECTS: FS_READ, FS_WRITE
# HB_SCRIPT_SCOPE: docs
# HB_SCRIPT_IDEMPOTENT: YES
# HB_SCRIPT_ENTRYPOINT: .\scripts\ssot\gen_docs_ssot.ps1
# HB_SCRIPT_OUTPUTS: generated_docs

<#
.SYNOPSIS
    SSOT Documentation Generation Script for HB Track (PowerShell Version)

.DESCRIPTION
    Generates SSOT artifacts to: docs/ssot/ (repository root)
    - openapi.json: OpenAPI 3.x specification from FastAPI app
    - schema.sql: Database schema dump from PostgreSQL (pg_dump)
    - alembic_state.txt: Current migration state (heads + current)
    - manifest.json: Generation manifest with git commit, timestamp, and file checksums

.PARAMETER All
    Generate all docs (default)

.PARAMETER OpenAPI
    Generate openapi.json

.PARAMETER Schema
    Generate schema.sql

.PARAMETER Alembic
    Generate alembic_state.txt

.PARAMETER Output
    Custom output directory (overrides default docs/ssot/)
#>

param (
    [switch]$All,
    [switch]$OpenAPI,
    [switch]$Schema,
    [switch]$Alembic,
    [string]$Output
)

# =============================================================================
# CONFIGURATION
# =============================================================================

# Script lives at scripts/ssot/gen_docs_ssot.ps1
$RepoRoot = (Get-Item "$PSScriptRoot\..\..").FullName
$BackendRoot = Join-Path $RepoRoot "Hb Track - Backend"

if (-not (Test-Path $BackendRoot)) {
    Write-Error "[FATAL] Backend dir not found: $BackendRoot"
    exit 1
}

# Load .env if exists
$EnvPath = Join-Path $BackendRoot ".env"
if (Test-Path $EnvPath) {
    Get-Content $EnvPath | Where-Object { $_ -match '=' -and $_ -notmatch '^#' } | ForEach-Object {
        $name, $value = $_.Split('=', 2)
        $name = $name.Trim()
        $value = $value.Trim().Trim('"').Trim("'")
        if (-not [string]::IsNullOrWhiteSpace($name)) {
            [System.Environment]::SetEnvironmentVariable($name, $value)
        }
    }
}

# Output directory - single location: docs/ssot/ at repo root
$DefaultOutputDir = Join-Path (Join-Path $RepoRoot "docs") "ssot"
$FinalOutputDir = if ($Output) { $Output } else { $DefaultOutputDir }

if (-not (Test-Path $FinalOutputDir)) {
    New-Item -ItemType Directory -Path $FinalOutputDir -Force | Out-Null
}

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

function Get-GitCommit {
    try {
        $commit = git -C $BackendRoot rev-parse HEAD 2>$null
        if ($LASTEXITCODE -eq 0) { return $commit.Trim() }
    } catch {}
    return "unknown"
}

function Get-FileChecksum {
    param([string]$FilePath)
    if (Test-Path $FilePath) {
        return (Get-FileHash $FilePath -Algorithm SHA256).Hash.ToLower()
    }
    return ""
}

function New-Manifest {
    param(
        [string]$OutputDir,
        [string[]]$GeneratedFiles
    )
    $ManifestFile = Join-Path $OutputDir "manifest.json"
    
    try {
        $GitCommit = Get-GitCommit
        $GeneratedAt = [DateTime]::UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ")
        
        $FilesInfo = @()
        foreach ($File in $GeneratedFiles) {
            $Path = Join-Path $OutputDir $File
            if (Test-Path $Path) {
                $FileInfo = Get-Item $Path
                $FilesInfo += @{
                    filename   = $File
                    checksum   = Get-FileChecksum $Path
                    size_bytes = $FileInfo.Length
                }
            }
        }
        
        $Manifest = @{
            git_commit       = $GitCommit
            generated_at     = $GeneratedAt
            output_strategy  = "single_location"
            output_location  = "docs/ssot"
            generator_script = "scripts/ssot/gen_docs_ssot.ps1 (unified)"
            files            = $FilesInfo
        }
        
        $Manifest | ConvertTo-Json -Depth 10 | Set-Content $ManifestFile -Encoding UTF8
        Write-Host "[OK] Manifest written to $ManifestFile"
        return $true
    } catch {
        Write-Host "[ERROR] Failed to generate manifest: $_"
        return $false
    }
}

# =============================================================================
# OPENAPI GENERATION
# =============================================================================

function Generate-OpenAPI {
    param([string]$OutputDir)
    $OutputFile = Join-Path $OutputDir "openapi.json"
    
    # Attempt 1: Direct app.openapi() via Python snippet
    try {
        Write-Host "[INFO] Attempting direct OpenAPI generation via Python..."
        $PythonCode = @"
import sys
import os
import json
from pathlib import Path

backend_root = r'$BackendRoot'
sys.path.insert(0, backend_root)

if not os.getenv('JWT_SECRET'):
    os.environ['JWT_SECRET'] = 'dummy-secret-for-openapi-generation'

try:
    from app.main import app
    schema = app.openapi()
    print(json.dumps(schema, indent=2, ensure_ascii=False))
except Exception as e:
    sys.stderr.write(str(e))
    sys.exit(1)
"@
        $SchemaJson = $PythonCode | python - 2>$null
        if ($LASTEXITCODE -eq 0 -and $SchemaJson) {
            $SchemaJson | Set-Content $OutputFile -Encoding UTF8
            Write-Host "[OK] OpenAPI spec written to $OutputFile"
            return $true
        }
        Write-Host "[WARN] Direct Python generation failed, falling back to HTTP..."
    } catch {
        Write-Host "[WARN] Exception during direct generation: $_"
    }

    # Attempt 2: HTTP fallback
    $BaseUrl = if ($env:BASE_URL) { $env:BASE_URL } else { "http://localhost:8000" }
    $Url = "$BaseUrl/api/v1/openapi.json"
    
    try {
        Write-Host "[INFO] Trying HTTP fallback: $Url"
        # Disable SSL check for local dev
        [System.Net.ServicePointManager]::ServerCertificateValidationCallback = { $true }
        $Response = Invoke-RestMethod -Uri $Url -Method Get -TimeoutSec 10
        $Response | ConvertTo-Json -Depth 20 | Set-Content $OutputFile -Encoding UTF8
        Write-Host "[OK] OpenAPI spec written to $OutputFile (via HTTP fallback)"
        return $true
    } catch {
        Write-Host "[ERROR] HTTP fallback also failed: $_"
        Write-Host "        Ensure the backend is running at $BaseUrl or fix import errors"
        return $false
    }
}

# =============================================================================
# TRAINING PERMISSIONS REPORT
# =============================================================================

function Generate-TrainingPermissions {
    $ReportScript = Join-Path (Join-Path $RepoRoot "docs") "scripts\trd_extract_training_permissions_report.py"
    if (-not (Test-Path $ReportScript)) {
        Write-Host "[WARN] Permissions report script not found: $ReportScript"
        return $false
    }

    try {
        python $ReportScript
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[OK] Training permissions report generated"
            return $true
        }
    } catch {
        Write-Host "[ERROR] Failed to generate permissions report: $_"
    }
    return $false
}

# =============================================================================
# SCHEMA SQL GENERATION
# =============================================================================

function Generate-SchemaSql {
    param([string]$OutputDir)
    $DatabaseUrl = $env:DATABASE_URL
    if (-not $DatabaseUrl) {
        Write-Host "[ERROR] DATABASE_URL not set"
        return $false
    }

    # Simplified parsing for pg_dump (doesn't handle all edge cases but common ones)
    $CleanUrl = $DatabaseUrl -replace "postgresql\+(asyncpg|psycopg2|psycopg)://", "postgresql://"
    
    # Regex to parse postgresql://user:pass@host:port/db
    if ($CleanUrl -match "postgresql://([^:]+):([^@]+)@([^:/]+)(?::(\d+))?/(.+)") {
        $User = $Matches[1]
        $Pass = $Matches[2]
        $DbHost = $Matches[3]
        $Port = if ($Matches[4]) { $Matches[4] } else { "5432" }
        $DB   = $Matches[5].Split('?')[0] # Remove query params
        
        $env:PGPASSWORD = $Pass
        if ($DatabaseUrl -match "sslmode") { $env:PGSSLMODE = "require" }
        
        $OutputFile = Join-Path $OutputDir "schema.sql"
        Write-Host "[INFO] Running pg_dump for $DbHost..."
        
        $Header = "-- Schema dump generated: $([DateTime]::UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ"))`n-- Source: $DbHost`n`n"
        $Header | Set-Content $OutputFile -Encoding UTF8
        
        pg_dump --schema-only --no-owner --no-privileges -h $DbHost -p $Port -U $User -d $DB | Add-Content $OutputFile
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[OK] Schema written to $OutputFile"
            return $true
        } else {
            Write-Host "[ERROR] pg_dump failed with exit code $LASTEXITCODE"
        }
    } else {
        Write-Host "[ERROR] Invalid DATABASE_URL format for parsing"
    }
    return $false
}

# =============================================================================
# ALEMBIC STATE GENERATION
# =============================================================================

function Generate-Alembic {
    param([string]$OutputDir)
    $DbUrlSync = $env:DATABASE_URL_SYNC
    $DbUrl = $env:DATABASE_URL

    if (-not $DbUrlSync -and -not $DbUrl) {
        Write-Host "[ERROR] DATABASE_URL_SYNC or DATABASE_URL must be set"
        return $false
    }

    $AlembicIni = Join-Path $BackendRoot "alembic.ini"
    if (-not (Test-Path $AlembicIni)) {
        Write-Host "[ERROR] alembic.ini not found"
        return $false
    }

    if (-not $DbUrlSync -and $DbUrl) {
        $SyncUrl = $DbUrl -replace "postgresql\+asyncpg://", "postgresql+psycopg2://"
        if (-not ($SyncUrl -like "postgresql+psycopg2://*")) {
            $SyncUrl = $SyncUrl -replace "postgresql://", "postgresql+psycopg2://"
        }
        $env:DATABASE_URL_SYNC = $SyncUrl
    }

    $OutputFile = Join-Path $OutputDir "alembic_state.txt"
    $OutputLines = @()
    
    try {
        Write-Host "[INFO] Running alembic heads..."
        $Heads = Push-Location $BackendRoot; alembic heads; Pop-Location
        $OutputLines += "=== ALEMBIC HEADS ==="
        $OutputLines += $Heads
        $OutputLines += ""

        Write-Host "[INFO] Running alembic current..."
        $Current = Push-Location $BackendRoot; alembic current; Pop-Location
        $OutputLines += "=== ALEMBIC CURRENT ==="
        $OutputLines += $Current
        $OutputLines += ""
        
        $OutputLines += "Generated: $([DateTime]::UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ"))"
        $OutputLines | Set-Content $OutputFile -Encoding UTF8
        
        Write-Host "[OK] Alembic state written to $OutputFile"
        return $true
    } catch {
        Write-Host "[ERROR] Alembic check failed: $_"
        return $false
    }
}

# =============================================================================
# MAIN
# =============================================================================

Write-Host "`n$($('='*60))"
Write-Host "HB Track SSOT Generator (Single Output)"
Write-Host "$($("="*60))"
Write-Host "Output directory: $FinalOutputDir"
Write-Host "$($('='*60))`n"

$Results = @()
$GeneratedFiles = @()

if ($All -or $OpenAPI) {
    $Success = Generate-OpenAPI $FinalOutputDir
    $Results += @{ Name = "OpenAPI"; Success = $Success }
    if ($Success) {
        $GeneratedFiles += "openapi.json"
        $PermSuccess = Generate-TrainingPermissions
        $Results += @{ Name = "Training Permissions Report"; Success = $PermSuccess }
    }
}

if ($All -or $Schema) {
    $Success = Generate-SchemaSql $FinalOutputDir
    $Results += @{ Name = "Schema SQL"; Success = $Success }
    if ($Success) {
        $GeneratedFiles += "schema.sql"
    }
}

if ($All -or $Alembic) {
    $Success = Generate-Alembic $FinalOutputDir
    $Results += @{ Name = "Alembic State"; Success = $Success }
    if ($Success) {
        $GeneratedFiles += "alembic_state.txt"
    }
}

if ($GeneratedFiles.Count -gt 0) {
    $ManifestSuccess = New-Manifest $FinalOutputDir $GeneratedFiles
    $Results += @{ Name = "Manifest"; Success = $ManifestSuccess }
}

Write-Host "`n$($('='*60))"
Write-Host "SUMMARY"
Write-Host "$($('='*60))"
foreach ($Res in $Results) {
    $Status = if ($Res.Success) { "[OK]" } else { "[FAILED]" }
    Write-Host "  $Status $($Res.Name)"
}

Write-Host "`nAll SSOT artifacts in: $FinalOutputDir"

$AllSuccess = $true
foreach ($Res in $Results) { if (-not $Res.Success) { $AllSuccess = $false; break } }

if ($AllSuccess) { exit 0 } else { exit 1 }
