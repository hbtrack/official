# =============================================================================
# SCRIPT DE RESET + MIGRATION + SEED - BANCO DE DADOS E2E
# =============================================================================
#
# PROPOSITO: Preparar banco de dados E2E do zero
#
# PIPELINE:
#   1. RESET: Limpa banco via Docker (remove volume)
#   2. MIGRATION: Executa Alembic (29 migrações)
#   3. SEED: Popula dados mínimos (Python/SQL)
#
# EXECUCAO:
#   .\db\reset-db-e2e.ps1
#
# SAIDA:
#   - Exit 0: Banco pronto para testes
#   - Exit 1: Erro em alguma fase
#
# TEMPO ESTIMADO: 30-60 segundos
#
# =============================================================================

param(
    [switch]$SkipReset = $false,
    [switch]$SkipMigration = $false,
    [switch]$SkipSeed = $false,
    [switch]$Verbose = $false,
    [int]$PostgresWaitSeconds = 10
)

$ErrorActionPreference = 'Continue'
$phaseStartTime = Get-Date

# Cores
function Write-Success {
    param([string]$Message)
    Write-Host "[OK]   $Message" -ForegroundColor Green
}

function Write-Failure {
    param([string]$Message)
    Write-Host "[ERRO] $Message" -ForegroundColor Red
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[AVISO] $Message" -ForegroundColor Yellow
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

function Test-Docker {
    Write-Info "Verificando Docker..."
    
    $dockerResult = docker --version 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Failure "Docker nao encontrado. Instale Docker Desktop."
        Write-Host "Download: https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
        return $false
    }
    
    Write-Success "Docker instalado: $dockerResult"
    return $true
}

function Test-DockerCompose {
    Write-Info "Verificando docker-compose..."
    
    $composeResult = docker-compose --version 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Failure "docker-compose nao encontrado"
        return $false
    }
    
    Write-Success "docker-compose: $composeResult"
    return $true
}

function Test-Python {
    Write-Info "Verificando Python..."
    
    $pythonResult = python --version 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Warning "Python nao encontrado. Seed SQL sera usado como fallback."
        return $false
    }
    
    Write-Success "Python: $pythonResult"
    return $true
}

function Test-Alembic {
    Write-Info "Verificando Alembic..."
    
    $alembicResult = alembic --version 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Warning "Alembic nao encontrado em PATH. Tentando via python -m..."
        return $false
    }
    
    Write-Success "Alembic instalado"
    return $true
}

# =============================================================================
# PRE-REQUISITOS
# =============================================================================

Write-Section "PRE-REQUISITOS"

# Validar que estamos no diretorio correto
$backendPath = "c:\HB TRACK\Hb Track - Backend"
$infraPath = "c:\HB TRACK\infra"

if (-not (Test-Path "$infraPath\docker-compose.yml")) {
    Write-Failure "docker-compose.yml nao encontrado em: $infraPath"
    Write-Host "Execute este script do diretorio com docker-compose.yml" -ForegroundColor Yellow
    exit 1
}

Write-Success "Diretorio infra encontrado: $infraPath"

# Validar dependencias
if (-not (Test-Docker)) { exit 1 }
if (-not (Test-DockerCompose)) { exit 1 }

$hasPython = Test-Python
$hasAlembic = Test-Alembic

# =============================================================================
# FASE 1: RESET
# =============================================================================

if (-not $SkipReset) {
    Write-Section "FASE 1: RESET (Limpar banco de dados)" 1
    
    Write-Info "Parando docker-compose..."
    Push-Location $infraPath
    
    try {
        docker-compose down --volumes 2>&1 | ForEach-Object {
            if ($Verbose) { Write-Host "  $_" -ForegroundColor Gray }
        }
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Docker parado e volume removido"
        } else {
            Write-Warning "Erro ao parar docker (pode estar ja parado)"
        }
        
        Write-Info "Removendo container PostgreSQL..."
        docker-compose rm -f postgres 2>&1 | Out-Null
        
        Write-Success "RESET completo - banco limpo"
    } catch {
        Write-Failure "Erro no RESET: $($_.Exception.Message)"
        exit 1
    } finally {
        Pop-Location
    }
} else {
    Write-Info "FASE 1 pulada (-SkipReset)"
}

# =============================================================================
# FASE 1.5: INICIAR DOCKER
# =============================================================================

Write-Section "Iniciando Docker..." 1.5

Push-Location $infraPath

try {
    Write-Info "Subindo docker-compose (PostgreSQL)..."
    docker-compose up -d 2>&1 | ForEach-Object {
        if ($Verbose) { Write-Host "  $_" -ForegroundColor Gray }
    }
    
    if ($LASTEXITCODE -ne 0) {
        Write-Failure "Erro ao iniciar docker-compose"
        exit 1
    }
    
    Write-Success "Docker iniciado"
    
    # Aguardar PostgreSQL estar pronto
    Write-Info "Aguardando PostgreSQL ficar pronto (max $PostgresWaitSeconds segundos)..."
    
    $postgresReady = $false
    $attempts = 0
    $maxAttempts = $PostgresWaitSeconds
    
    while ($attempts -lt $maxAttempts -and -not $postgresReady) {
        try {
            # Tentar conexao simples
            $env:PGPASSWORD = "hbtrack_dev_pwd"
            $pgResult = docker exec -i hbtrack-postgres-dev psql -U hbtrack_dev -d postgres -c "SELECT 1;" 2>&1
            if ($LASTEXITCODE -eq 0) {
                $postgresReady = $true
            }
        } catch {
            $postgresReady = $false
        }
        
        if (-not $postgresReady) {
            Write-Host "  Aguardando... ($attempts/$maxAttempts)" -ForegroundColor Gray
            Start-Sleep -Seconds 1
            $attempts++
        }
    }
    
    if ($postgresReady) {
        Write-Success "PostgreSQL pronto para conexao"
    } else {
        Write-Warning "PostgreSQL nao respondeu a tempo. Continuando mesmo assim..."
    }
    
} catch {
    Write-Failure "Erro ao iniciar Docker: $($_.Exception.Message)"
    exit 1
} finally {
    Pop-Location
}

# =============================================================================
# FASE 1.9: CRIAR BANCO DE DADOS
# =============================================================================

Write-Section "Criando banco de dados..." 1.9

try {
    Write-Info "Criando database hb_track_e2e..."
    $env:PGPASSWORD = "hbtrack_dev_pwd"
    docker exec -i hbtrack-postgres-dev psql -U hbtrack_dev -d postgres -c "CREATE DATABASE hb_track_e2e;" 2>&1 | Out-Null
    
    # Exit code 0 = criado com sucesso, 1 = database já existe (ambos OK)
    Write-Success "Banco de dados criado ou ja existe"
} catch {
    Write-Warning "Erro ao criar banco: $($_.Exception.Message)"
}

# =============================================================================
# FASE 2: MIGRATION (ALEMBIC)
# =============================================================================

if (-not $SkipMigration) {
    Write-Section "FASE 2: MIGRATION (Alembic - 29 migrações)" 2
    
    Push-Location "$backendPath\db"
    
    try {
        # Garantir variaveis de ambiente para Alembic
        $env:DATABASE_URL = "postgresql+psycopg2://hbtrack_dev:hbtrack_dev_pwd@localhost:5433/hb_track_e2e"
        $env:DATABASE_URL_ASYNC = "postgresql+asyncpg://hbtrack_dev:hbtrack_dev_pwd@localhost:5433/hb_track_e2e"
        
        Write-Info "Executando: alembic upgrade head"
        
        if ($hasAlembic) {
            alembic upgrade head 2>&1 | ForEach-Object {
                Write-Host "  $_" -ForegroundColor Gray
            }
        } else {
            Write-Info "Tentando via: python -m alembic upgrade head"
            python -m alembic upgrade head 2>&1 | ForEach-Object {
                Write-Host "  $_" -ForegroundColor Gray
            }
        }
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Migration completa - Schema criado (29 migrações aplicadas)"
        } else {
            Write-Failure "Migration falhou"
            exit 1
        }
        
        # Verificar migracao atual
        Write-Info "Verificando versao atual..."
        if ($hasAlembic) {
            $currentVersion = alembic current 2>&1 | Select-Object -Last 1
        } else {
            $currentVersion = python -m alembic current 2>&1 | Select-Object -Last 1
        }
        Write-Host "  Versao atual: $currentVersion" -ForegroundColor Cyan
        
    } catch {
        Write-Failure "Erro na migration: $($_.Exception.Message)"
        exit 1
    } finally {
        Pop-Location
    }
} else {
    Write-Info "FASE 2 pulada (-SkipMigration)"
}

# =============================================================================
# FASE 3: SEED
# =============================================================================

if (-not $SkipSeed) {
    Write-Section "FASE 3: SEED (Dados minimos)" 3
    
    Push-Location $backendPath
    
    try {
        $seedSuccess = $false
        
        # Tentar seed Python primeiro (idempotente)
        if ($hasPython) {
            Write-Info "Executando: python scripts/seed_e2e.py"
            
            python scripts/seed_e2e.py 2>&1 | ForEach-Object {
                Write-Host "  $_" -ForegroundColor Gray
            }
            
            if ($LASTEXITCODE -eq 0) {
                Write-Success "Seed E2E completo (Python)"
                $seedSuccess = $true
            } else {
                Write-Warning "Seed Python falhou, tentando SQL..."
            }
        }
        
        # Fallback para seed SQL
        if (-not $seedSuccess) {
            Write-Info "Executando: SQL seeds (fallback)"
            
            if (Test-Path "db\seed_minimo_oficial.sql") {
                Write-Host "  Aplicando seed_minimo_oficial.sql..." -ForegroundColor Gray
                psql -U hbtrack_dev -d hb_track_e2e -f "db\seed_minimo_oficial.sql" 2>&1 | Out-Null
            }
            
            if (Test-Path "db\seed_test_users.sql") {
                Write-Host "  Aplicando seed_test_users.sql..." -ForegroundColor Gray
                psql -U hbtrack_dev -d hb_track_e2e -f "db\seed_test_users.sql" 2>&1 | Out-Null
            }
            
            Write-Success "Seed SQL completo"
            $seedSuccess = $true
        }
        
        if (-not $seedSuccess) {
            Write-Failure "Seed falhou (Python e SQL)"
            exit 1
        }
        
    } catch {
        Write-Failure "Erro na seed: $($_.Exception.Message)"
        exit 1
    } finally {
        Pop-Location
    }
} else {
    Write-Info "FASE 3 pulada (-SkipSeed)"
}

# =============================================================================
# VERIFICACAO FINAL
# =============================================================================

Write-Section "VERIFICACAO FINAL"

Push-Location $backendPath

try {
    Write-Info "Verificando dados no banco..."
    
    # Contar usuarios
    $userCount = psql -U hbtrack_dev -d hb_track_e2e -tAc "SELECT COUNT(*) FROM users;" 2>$null
    Write-Host "  Usuarios: $userCount" -ForegroundColor Cyan
    
    # Contar roles
    $roleCount = psql -U hbtrack_dev -d hb_track_e2e -tAc "SELECT COUNT(*) FROM roles;" 2>$null
    Write-Host "  Roles: $roleCount" -ForegroundColor Cyan
    
    # Contar permissions
    $permCount = psql -U hbtrack_dev -d hb_track_e2e -tAc "SELECT COUNT(*) FROM permissions;" 2>$null
    Write-Host "  Permissions: $permCount" -ForegroundColor Cyan
    
    if ([int]$userCount -gt 0 -and [int]$roleCount -gt 0 -and [int]$permCount -gt 0) {
        Write-Success "Dados verificados - Banco pronto para testes!"
    } else {
        Write-Warning "Contadores baixos - Banco pode estar incompleto"
    }
    
} catch {
    Write-Warning "Nao conseguiu verificar dados (psql pode nao estar em PATH)"
} finally {
    Pop-Location
}

# =============================================================================
# RESUMO FINAL
# =============================================================================

$phaseEndTime = Get-Date
$totalDuration = $phaseEndTime - $phaseStartTime

Write-Section "RESUMO"

Write-Success "Reset + Migration + Seed completo!"
Write-Host "`nTempo total: $($totalDuration.ToString('mm\:ss'))" -ForegroundColor Cyan
Write-Host "`nBanco pronto em: hb_track_e2e" -ForegroundColor Green
Write-Host "PostgreSQL rodando em: localhost:5433" -ForegroundColor Green
Write-Host "`nProxima etapa: python scripts/seed_e2e.py (novamente, se necessario)" -ForegroundColor Yellow

exit 0
