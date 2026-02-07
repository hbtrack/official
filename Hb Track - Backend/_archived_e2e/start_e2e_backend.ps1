# Script para iniciar backend E2E
# Uso: .\start_e2e_backend.ps1

$env:DATABASE_URL = "postgresql+psycopg2://hbtrack_dev:hbtrack_dev_pwd@localhost:5433/hb_track_e2e"
$env:E2E = "1"
$env:ENV = "test"
$env:JWT_SECRET = "teste-jwt-secret-super-seguro-123456"

Set-Location "c:\HB TRACK\Hb Track - Backend"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "HB TRACK E2E Backend" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "DATABASE_URL: $env:DATABASE_URL"
Write-Host "E2E: $env:E2E"
Write-Host "ENV: $env:ENV"
Write-Host "========================================" -ForegroundColor Cyan

python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
