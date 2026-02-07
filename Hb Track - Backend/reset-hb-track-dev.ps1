# =============================================================================
# RESET DO BANCO hb_track_dev (DBeaver)
# =============================================================================
#
# PROPOSITO: Resetar o banco de desenvolvimento visivel no DBeaver
#
# PIPELINE:
#   1. DROP + CREATE schema public (limpa todas as tabelas)
#   2. Aplicar migrations via Alembic
#   3. Aplicar migracao SQL (db/migrations)
#   4. Executar seeds (dados iniciais)
#
# EXECUCAO:
#   .\reset-hb-track-dev.ps1
#
# SAIDA:
#   - Exit 0: Banco pronto para uso
#   - Exit 1: Erro em alguma fase
#
# TEMPO ESTIMADO: 15-30 segundos
#
# =============================================================================

$ErrorActionPreference = 'Continue'

# Cores
function Write-Success {
    param([string]$Message)
    Write-Host "[OK]   $Message" -ForegroundColor Green
}

function Write-Failure {
    param([string]$Message)
    Write-Host "[ERRO] $Message" -ForegroundColor Red
}

function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Cyan
}

function Write-Section {
    param([string]$Message, [int]$Number = 0)
    if ($Number -gt 0) {
        Write-Host "`n========================================" -ForegroundColor Cyan
        Write-Host "[$Number] $Message" -ForegroundColor Cyan
        Write-Host "========================================`n" -ForegroundColor Cyan
    } else {
        Write-Host "`n========================================" -ForegroundColor Cyan
        Write-Host "$Message" -ForegroundColor Cyan
        Write-Host "========================================`n" -ForegroundColor Cyan
    }
}

Write-Section "RESET: hb_track_dev (DBeaver)"

# Verificar se estamos na pasta correta
$backendPath = "c:\HB TRACK\Hb Track - Backend"
if (-not (Test-Path $backendPath)) {
    Write-Failure "Pasta backend nao encontrada: $backendPath"
    exit 1
}

Push-Location $backendPath

try {
    # Carregar variaveis do .env
    Write-Info "Carregando variaveis do .env..."
    
    if (-not (Test-Path ".env")) {
        Write-Failure "Arquivo .env nao encontrado em: $backendPath"
        exit 1
    }
    
    $envContent = Get-Content .env
    $DATABASE_URL_SYNC = ($envContent | Select-String "^DATABASE_URL_SYNC=").ToString().Split('=', 2)[1].Trim()
    
    if (-not $DATABASE_URL_SYNC) {
        Write-Failure "DATABASE_URL_SYNC nao encontrado no .env"
        exit 1
    }
    
    Write-Info "Banco: $DATABASE_URL_SYNC"
    
    # =============================================================================
    # FASE 1: RESET DO SCHEMA
    # =============================================================================
    
    Write-Section "Resetando schema public..." 1
    
    $env:PGPASSWORD = "hbtrack_dev_pwd"
    
    Write-Info "Terminando conexoes ativas no banco..."
    psql -h localhost -p 5433 -U hbtrack_dev -d hb_track_dev -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'hb_track_dev' AND pid <> pg_backend_pid();" 2>&1 | Out-Null
    
    Start-Sleep -Seconds 1
    
    Write-Info "Dropando e recriando schema public..."
    $output = psql -h localhost -p 5433 -U hbtrack_dev -d hb_track_dev -c "DROP SCHEMA IF EXISTS public CASCADE; CREATE SCHEMA public; GRANT ALL ON SCHEMA public TO hbtrack_dev; GRANT ALL ON SCHEMA public TO PUBLIC;" 2>&1
    
    # Verificar se contem "CREATE SCHEMA" no output (sucesso)
    if ($output -match "CREATE SCHEMA" -or $LASTEXITCODE -eq 0) {
        Write-Success "Schema resetado com permissoes"
    } else {
        Write-Failure "Erro ao resetar schema: $output"
        exit 1
    }
    
    # =============================================================================
    # FASE 2: APLICAR MIGRATIONS
    # =============================================================================
    
    Write-Section "Aplicando migrations via Alembic..." 2
    
    # Garantir que DATABASE_URL_SYNC esta no ambiente
    $env:DATABASE_URL_SYNC = $DATABASE_URL_SYNC
    
    # Rodar alembic da raiz do backend (onde esta alembic.ini)
    Write-Info "Executando: python -m alembic upgrade head"
    $alembicOutput = python -m alembic upgrade head 2>&1
    
    $alembicOutput | ForEach-Object {
        Write-Host "  $_" -ForegroundColor Gray
    }
    
    if ($LASTEXITCODE -ne 0 -and ($alembicOutput -match "Multiple head revisions")) {
        Write-Info "Detectado multiplos heads. Executando: python -m alembic upgrade heads"
        $alembicOutput = python -m alembic upgrade heads 2>&1
        
        $alembicOutput | ForEach-Object {
            Write-Host "  $_" -ForegroundColor Gray
        }
    }
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Migrations aplicadas"
    } else {
        Write-Failure "Erro ao aplicar migrations"
        exit 1
    }
    
    # =============================================================================
    # FASE 3: APLICAR MIGRACAO SQL 0053 (db/migrations)
    # =============================================================================
    
    Write-Section "Aplicando migration SQL 0053..." 3
    
    $sqlMigration = ".\db\migrations\0053_training_sessions_review_flow.sql"
    
    if (-not (Test-Path $sqlMigration)) {
        Write-Failure "Migration SQL nao encontrada: $sqlMigration"
        exit 1
    }
    
    Write-Info "Executando: psql -f $sqlMigration"
    $sqlOutput = psql -h localhost -p 5433 -U hbtrack_dev -d hb_track_dev -f $sqlMigration 2>&1
    
    $sqlOutput | ForEach-Object {
        Write-Host "  $_" -ForegroundColor Gray
    }
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Migration SQL 0053 aplicada"
    } else {
        Write-Failure "Erro ao aplicar migration SQL 0053"
        exit 1
    }
    
    # =============================================================================
    # FASE 4: EXECUTAR SEEDS DE TESTE
    # =============================================================================
    
    Write-Section "Executando seed canonico E2E..." 4
    
    $seedScript = ".\scripts\seed_e2e_canonical.py"
    
    if (-not (Test-Path $seedScript)) {
        Write-Failure "Script de seed nao encontrado: $seedScript"
        exit 1
    }
    
    Write-Info "NOTA: Seed canonico com UUIDs determinísticos"
    Write-Info "      32 users, 16 teams, 240 athletes, 60 sessions, 60 wellness"
    
    # Verificar se python esta disponivel
    $pythonPath = ".\.venv\Scripts\python.exe"
    
    if (Test-Path $pythonPath) {
        Write-Info "Executando seed canônico via venv..."
        & $pythonPath $seedScript --deterministic 2>&1 | ForEach-Object {
            Write-Host "  $_" -ForegroundColor Gray
        }
    } else {
        Write-Info "Executando seed canônico via python global..."
        & python $seedScript --deterministic 2>&1 | ForEach-Object {
            Write-Host "  $_" -ForegroundColor Gray
        }
    }
    
    if ($LASTEXITCODE -ne 0) {
        Write-Failure "Erro ao executar seeds"
        exit 1
    }
    
    Write-Success "Seeds de teste executados"
    
    # =============================================================================
    # RESULTADO FINAL
    # =============================================================================
    
    Write-Host "`n" -NoNewline
    Write-Section "BANCO RESETADO COM SUCESSO!"
    
    Write-Host "Verifique no DBeaver:" -ForegroundColor Yellow
    Write-Host "   Host: localhost" -ForegroundColor White
    Write-Host "   Porta: 5433" -ForegroundColor White
    Write-Host "   Database: hb_track_dev" -ForegroundColor White
    Write-Host "   User: hbtrack_dev" -ForegroundColor White
    Write-Host ""
    Write-Host "Sistema configurado com:" -ForegroundColor Green
    Write-Host "   ✅ Schema canonico (migrations)" -ForegroundColor White
    Write-Host "   ✅ RBAC completo (5 roles, 65 permissions)" -ForegroundColor White
    Write-Host "   ✅ Super admin (adm@handballtrack.app)" -ForegroundColor White
    Write-Host "   ✅ Seed canônico (32 users, 16 teams, 240 athletes, team_memberships)" -ForegroundColor White
    Write-Host ""
    Write-Host "Proximos passos:" -ForegroundColor Green
    Write-Host "   1. Inicie o backend: .\reset-and-start.ps1" -ForegroundColor White
    Write-Host "   2. Rode os testes: pytest tests/ -v" -ForegroundColor White
    Write-Host ""
    
} catch {
    Write-Failure "Erro ao executar reset"
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
} finally {
    Pop-Location
}
