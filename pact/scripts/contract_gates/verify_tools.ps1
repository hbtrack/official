$ErrorActionPreference = "Stop"

. (Join-Path $PSScriptRoot "env.ps1")

node -v
npm -v
redocly --version
spectral --version
ajv help

