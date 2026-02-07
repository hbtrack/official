#!/usr/bin/env pwsh
# Proxy local para permitir uso de .\scripts\inv.ps1 a partir de "Hb Track - Backend"

$ErrorActionPreference = "Stop"

$proxyRoot = Split-Path -Parent $PSScriptRoot          # ...\Hb Track - Backend
$repoRoot = Split-Path -Parent $proxyRoot              # ...\HB TRACK
$target = Join-Path $repoRoot "scripts\inv.ps1"       # ...\HB TRACK\scripts\inv.ps1

if (-not (Test-Path $target)) {
    Write-Error "inv proxy target not found: $target"
    exit 1
}

& $target @args
exit $LASTEXITCODE
