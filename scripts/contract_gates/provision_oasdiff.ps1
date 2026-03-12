$ErrorActionPreference = "Stop"

. (Join-Path $PSScriptRoot "env.ps1")

if (-not (Get-Command go -ErrorAction SilentlyContinue)) {
  Write-Error "Go runtime não encontrado no PATH. Instale Go e reexecute este script."
}

Write-Host "Instalando oasdiff via 'go install'..."
go install github.com/oasdiff/oasdiff@latest

Write-Host "Verificando oasdiff..."
oasdiff --version
