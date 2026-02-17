#Requires -Version 5.1
# HB_SCRIPT_KIND: CHECK
# HB_SCRIPT_SCOPE: docs
# HB_SCRIPT_SIDE_EFFECTS: NONE
# HB_SCRIPT_IDEMPOTENT: YES
# HB_SCRIPT_ENTRYPOINT: .\scripts\checks\docs\check_docs_index.ps1
# HB_SCRIPT_DESCRIPTION: Validates docs/_INDEX.yaml against index.schema.json

<#
.SYNOPSIS
    Validates documentation index against JSON Schema

.DESCRIPTION
    Validates docs/_INDEX.yaml against docs/_canon/SCHEMAS/index.schema.json
    Checks:
      - Schema conformance
      - ID uniqueness
      - Path existence
      - Category validity

.EXAMPLE
    .\scripts\checks\docs\check_docs_index.ps1

.NOTES
    Exit Codes:
      0 - OK (all validations pass)
      2 - VIOLATION (schema mismatch, duplicate ID, path not found, missing category)
      3 - ERROR (YAML parse error, schema file not found, missing dependencies)
#>

[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"

# Exit codes (contract)
$EXIT_OK = 0
$EXIT_VIOLATION = 2
$EXIT_ERROR = 3

# Resolve paths
$RepoRoot = (Get-Item $PSScriptRoot).Parent.Parent.Parent.FullName
$Engine = Join-Path $RepoRoot "scripts\_lib\docs_index_lib.py"

# Verify engine exists
if (-not (Test-Path $Engine)) {
    Write-Error "[ERROR] Validation engine not found: $Engine"
    exit $EXIT_ERROR
}

# Execute Python engine
try {
    & python $Engine
    $exitCode = $LASTEXITCODE
    
    # Propagate exit code
    switch ($exitCode) {
        0 { exit $EXIT_OK }
        2 { exit $EXIT_VIOLATION }
        3 { exit $EXIT_ERROR }
        default { 
            Write-Warning "[WARN] Unexpected exit code from engine: $exitCode"
            exit $EXIT_ERROR 
        }
    }
}
catch {
    Write-Error "[ERROR] Failed to execute validation engine: $_"
    exit $EXIT_ERROR
}
