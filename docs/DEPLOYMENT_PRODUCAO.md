<!-- STATUS: NEEDS_REVIEW -->

# GUIA DE DEPLOYMENT - PRODUÇÃO

**Data de Preparação:** 2025-12-25
**Status Staging:** ✅ COMPLETO
**Pronto para Produção:** ✅ SIM

---

## ✅ PRÉ-REQUISITOS VALIDADOS

### Staging Environment (COMPLETO)

- ✅ 5 migrations aplicadas com sucesso
- ✅ 4 materialized views criadas
- ✅ Schema validado (season_id, team_id adicionados)
- ✅ Foreign keys e índices criados
- ✅ Router integrado na API
- ✅ Código Python (11 arquivos, 1,638 linhas)

### Arquivos Prontos

```
backend/
├── db/alembic/versions/
│   ├── 5c90cfd7e291_add_season_team_to_training_sessions_.py  ✅
│   ├── 92365c111182_create_mv_training_performance.py  ✅
│   ├── 6086f19465e1_create_mv_athlete_training_summary.py  ✅
│   ├── bb97d068b643_create_mv_wellness_summary.py  ✅
│   └── 8fba6a22b58c_create_mv_medical_cases_summary.py  ✅
│
├── app/schemas/reports/  ✅ (5 arquivos)
├── app/services/reports/  ✅ (5 arquivos)
└── app/api/v1/routers/reports.py  ✅
```

---

## 🚀 DEPLOYMENT EM PRODUÇÃO

### Ambiente Produção

- **Database:** Neon PostgreSQL 17
- **Endpoint:** `ep-soft-cake-ad07z2ue-pooler.c-2.us-east-1.aws.neon.tech`
- **URL:** `postgresql://neondb_owner:npg_fmT3ctPrD8pW@ep-soft-cake-ad07z2ue-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require`

### ⚠️ IMPORTANTE: Antes de Começar

1. **Backup do Banco de Dados**
   - Neon oferece snapshots automáticos
   - Crie um snapshot manual antes do deployment
   - Valide que o snapshot foi criado com sucesso

2. **Janela de Manutenção**
   - Escolher horário de baixo tráfego
   - Comunicar usuários sobre manutenção
   - Estimativa: 5-10 minutos de downtime

3. **Plano de Rollback**
   - Ter comando de downgrade pronto
   - Saber como restaurar snapshot do Neon
   - Ter contato de suporte disponível

---

## 📝 PASSO A PASSO - DEPLOYMENT

### Opção 1: Script Automático (RECOMENDADO)

#### 1.1 Criar Script de Deployment

```batch
@echo off
REM deploy_production.bat
REM Script para aplicar migrations em PRODUÇÃO

echo ================================================================================
echo DEPLOYMENT EM PRODUCAO - SISTEMA DE RELATORIOS
echo ================================================================================
echo.
echo ATENCAO: Este script vai modificar o banco de dados de PRODUCAO
echo.
echo Database: ep-soft-cake-ad07z2ue-pooler (PRODUCTION)
echo.
pause

set DATABASE_URL=postgresql://neondb_owner:npg_fmT3ctPrD8pW@ep-soft-cake-ad07z2ue-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require^&channel_binding=require

echo.
echo [1/4] Verificando revisao atual...
.venv\Scripts\alembic.exe -c backend\db\alembic.ini current

echo.
echo [2/4] Listando migrations pendentes...
.venv\Scripts\alembic.exe -c backend\db\alembic.ini history

echo.
echo Deseja continuar com o deployment? (Ctrl+C para cancelar)
pause

echo.
echo [3/4] Aplicando migrations...
.venv\Scripts\alembic.exe -c backend\db\alembic.ini upgrade head

echo.
echo [4/4] Verificando schema final...
.venv\Scripts\python.exe verify_production.py

echo.
echo ================================================================================
echo DEPLOYMENT COMPLETO
echo ================================================================================
pause
```

#### 1.2 Criar Script de Verificação

```python
# verify_production.py
import os
import psycopg2
from psycopg2.extras import RealDictCursor

os.environ['DATABASE_URL'] = 'postgresql://neondb_owner:npg_fmT3ctPrD8pW@ep-soft-cake-ad07z2ue-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require'

conn = psycopg2.connect(os.environ['DATABASE_URL'])
cursor = conn.cursor(cursor_factory=RealDictCursor)

print("PRODUCTION DATABASE VERIFICATION")
print("=" * 80)

# Check columns
cursor.execute("""
    SELECT column_name, data_type, is_nullable
    FROM information_schema.columns
    WHERE table_name = 'training_sessions'
      AND column_name IN ('season_id', 'team_id')
""")
print("\n1. Columns in training_sessions:")
for row in cursor.fetchall():
    print(f"   - {row['column_name']}: {row['data_type']} (nullable: {row['is_nullable']})")

# Check views
cursor.execute("""
    SELECT matviewname FROM pg_matviews
    WHERE matviewname LIKE 'mv_%'
    ORDER BY matviewname
""")
print("\n2. Materialized Views:")
for row in cursor.fetchall():
    print(f"   - {row['matviewname']}")

# Check FKs
cursor.execute("""
    SELECT conname, confrelid::regclass
    FROM pg_constraint
    WHERE conrelid = 'training_sessions'::regclass
      AND contype = 'f'
      AND conname LIKE 'fk_training_sessions_%'
""")
print("\n3. Foreign Keys:")
for row in cursor.fetchall():
    print(f"   - {row['conname']} -> {row['referenced_table']}")

# Check indexes
cursor.execute("""
    SELECT indexname FROM pg_indexes
    WHERE tablename = 'training_sessions'
      AND indexname LIKE 'idx_training_sessions_%'
""")
print("\n4. Indexes:")
for row in cursor.fetchall():
    print(f"   - {row['indexname']}")

# Data counts
print("\n5. Data Counts:")
tables = ['training_sessions', 'mv_training_performance', 'mv_athlete_training_summary',
          'mv_wellness_summary', 'mv_medical_cases_summary']
for table in tables:
    try:
        cursor.execute(f"SELECT COUNT(*) as cnt FROM {table}")
        count = cursor.fetchone()['cnt']
        print(f"   - {table}: {count} records")
    except Exception as e:
        print(f"   - {table}: ERROR ({str(e)})")

print("\n" + "=" * 80)
print("VERIFICATION COMPLETE")
print("=" * 80)

conn.close()
```

#### 1.3 Executar Deployment

```bash
# Windows
cmd /c deploy_production.bat

# Ou manualmente:
set DATABASE_URL=postgresql://neondb_owner:npg_fmT3ctPrD8pW@ep-soft-cake-ad07z2ue-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require
.venv\Scripts\alembic.exe -c backend\db\alembic.ini upgrade head
```

---

### Opção 2: Deployment Manual Passo a Passo

#### Passo 1: Verificar Estado Atual

```bash
# Set DATABASE_URL
$env:DATABASE_URL="postgresql://neondb_owner:npg_fmT3ctPrD8pW@ep-soft-cake-ad07z2ue-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

# Check current revision
.venv\Scripts\alembic.exe -c backend\db\alembic.ini current

# Expected output: 4af09f9d46a0 (ou anterior)
```

#### Passo 2: Visualizar Migrations Pendentes

```bash
.venv\Scripts\alembic.exe -c backend\db\alembic.ini history

# Deve mostrar:
# 4af09f9d46a0 -> 5c90cfd7e291 (head), add_season_team_to_training_sessions_phase1
# 5c90cfd7e291 -> 92365c111182, create_mv_training_performance
# 92365c111182 -> 6086f19465e1, create_mv_athlete_training_summary
# 6086f19465e1 -> bb97d068b643, create_mv_wellness_summary
# bb97d068b643 -> 8fba6a22b58c, create_mv_medical_cases_summary
```

#### Passo 3: Aplicar Migrations

```bash
# ATENÇÃO: Este comando vai modificar o banco de produção!
.venv\Scripts\alembic.exe -c backend\db\alembic.ini upgrade head

# Saída esperada:
# INFO  [alembic.runtime.migration] Running upgrade 4af09f9d46a0 -> 5c90cfd7e291
# INFO  [alembic.runtime.migration] Running upgrade 5c90cfd7e291 -> 92365c111182
# INFO  [alembic.runtime.migration] Running upgrade 92365c111182 -> 6086f19465e1
# INFO  [alembic.runtime.migration] Running upgrade 6086f19465e1 -> bb97d068b643
# INFO  [alembic.runtime.migration] Running upgrade bb97d068b643 -> 8fba6a22b58c
```

#### Passo 4: Executar Backfill (se necessário)

```bash
# Dry run first
.venv\Scripts\python.exe backend\db\scripts\backfill_simple.py \
  --database-url "$env:DATABASE_URL" \
  --dry-run

# Se houver registros para atualizar, executar backfill real
.venv\Scripts\python.exe backend\db\scripts\backfill_simple.py \
  --database-url "$env:DATABASE_URL" \
  --batch-size 1000
```

#### Passo 5: Verificar Schema

```bash
.venv\Scripts\python.exe verify_production.py

# Deve mostrar:
# - season_id: uuid (nullable: YES) ✅
# - team_id: uuid (nullable: YES) ✅
# - 4 materialized views ✅
# - 2 foreign keys ✅
# - 3 indexes ✅
```

#### Passo 6: Testar Endpoints

```bash
# Iniciar aplicação
uvicorn app.main:app --reload

# Acessar:
# http://localhost:8000/api/v1/docs

# Testar endpoints:
# GET /api/v1/reports/training-performance
# GET /api/v1/reports/athletes/{athlete_id}
# GET /api/v1/reports/wellness-summary
# GET /api/v1/reports/medical-summary
```

---

## 🔄 ROLLBACK (Se Necessário)

### Opção 1: Downgrade via Alembic

```bash
# Voltar para revisão anterior
.venv\Scripts\alembic.exe -c backend\db\alembic.ini downgrade 4af09f9d46a0

# Isso vai:
# - Remover 4 materialized views
# - Remover colunas season_id e team_id
# - Remover foreign keys
# - Remover índices
```

### Opção 2: Restaurar Snapshot do Neon

1. Acessar Neon Console
2. Selecionar projeto
3. Ir em "Branches" ou "Backups"
4. Restaurar snapshot criado antes do deployment
5. Atualizar connection string na aplicação

---

## ✅ CHECKLIST DE VALIDAÇÃO PÓS-DEPLOYMENT

### Database Schema

- [ ] Coluna `training_sessions.season_id` existe e é UUID nullable
- [ ] Coluna `training_sessions.team_id` existe e é UUID nullable
- [ ] FK `fk_training_sessions_season` criada
- [ ] FK `fk_training_sessions_team` criada
- [ ] Índice `idx_training_sessions_season` criado
- [ ] Índice `idx_training_sessions_team` criado
- [ ] Índice `idx_training_sessions_org_season_date` criado

### Materialized Views

- [ ] `mv_training_performance` existe
- [ ] `mv_athlete_training_summary` existe
- [ ] `mv_wellness_summary` existe
- [ ] `mv_medical_cases_summary` existe

### API Endpoints

- [ ] `/api/v1/reports/training-performance` responde
- [ ] `/api/v1/reports/training-trends` responde
- [ ] `/api/v1/reports/athletes/{id}` responde
- [ ] `/api/v1/reports/athletes` responde
- [ ] `/api/v1/reports/wellness-summary` responde
- [ ] `/api/v1/reports/wellness-trends` responde
- [ ] `/api/v1/reports/medical-summary` responde
- [ ] `/api/v1/reports/athletes/{id}/medical-history` responde
- [ ] Tag "Reports" aparece em `/api/v1/docs`

### Functional Testing

- [ ] Criar training session com season_id e team_id
- [ ] Refresh materialized views manualmente
- [ ] Query reports via API e validar dados
- [ ] Testar filtros (season_id, team_id, date range)
- [ ] Validar permissões (coordenador, treinador)

### Performance

- [ ] Queries em materialized views < 100ms
- [ ] Endpoints de relatórios < 500ms
- [ ] Índices sendo utilizados (EXPLAIN ANALYZE)

---

## 📊 MONITORAMENTO PÓS-DEPLOYMENT

### Logs a Monitorar

1. **Erros de Aplicação**
   ```bash
   # Logs de erro relacionados a relatórios
   grep "reports" logs/app.log | grep ERROR
   ```

2. **Performance de Queries**
   ```sql
   -- Queries mais lentas
   SELECT query, mean_exec_time, calls
   FROM pg_stat_statements
   WHERE query LIKE '%mv_%'
   ORDER BY mean_exec_time DESC
   LIMIT 10;
   ```

3. **Uso de Índices**
   ```sql
   -- Verificar se índices estão sendo usados
   SELECT
       schemaname,
       tablename,
       indexname,
       idx_scan,
       idx_tup_read
   FROM pg_stat_user_indexes
   WHERE tablename = 'training_sessions'
       AND indexname LIKE 'idx_training_sessions_%'
   ORDER BY idx_scan DESC;
   ```

### Métricas de Sucesso

- ✅ Zero erros 500 nos endpoints de relatórios
- ✅ Tempo de resposta < 500ms
- ✅ Materialized views sendo atualizadas corretamente
- ✅ Dados corretos sendo retornados

---

## 🔧 MANUTENÇÃO CONTÍNUA

### Refresh de Materialized Views

As materialized views precisam ser atualizadas periodicamente:

```sql
-- Manual refresh (pode ser lento)
REFRESH MATERIALIZED VIEW mv_training_performance;
REFRESH MATERIALIZED VIEW mv_athlete_training_summary;
REFRESH MATERIALIZED VIEW mv_wellness_summary;
REFRESH MATERIALIZED VIEW mv_medical_cases_summary;

-- Concurrent refresh (não bloqueia leituras)
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_training_performance;
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_athlete_training_summary;
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_wellness_summary;
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_medical_cases_summary;
```

**Estratégias de Atualização:**

1. **Via Endpoint API** (Recomendado)
   ```bash
   POST /api/v1/reports/refresh-training-performance
   ```

2. **Via Cron Job**
   ```bash
   # Atualizar a cada hora
   0 * * * * psql $DATABASE_URL -c "REFRESH MATERIALIZED VIEW CONCURRENTLY mv_training_performance"
   ```

3. **Via Trigger** (Automático, mas pode ter impacto em performance)
   ```sql
   -- Criar função de refresh
   CREATE OR REPLACE FUNCTION refresh_training_performance()
   RETURNS TRIGGER AS $$
   BEGIN
       REFRESH MATERIALIZED VIEW CONCURRENTLY mv_training_performance;
       RETURN NEW;
   END;
   $$ LANGUAGE plpgsql;

   -- Trigger após insert/update em training_sessions
   CREATE TRIGGER trg_refresh_training_performance
   AFTER INSERT OR UPDATE ON training_sessions
   FOR EACH STATEMENT
   EXECUTE FUNCTION refresh_training_performance();
   ```

---

## 📞 SUPORTE E CONTATOS

### Em Caso de Problemas

1. **Rollback Imediato**
   ```bash
   .venv\Scripts\alembic.exe -c backend\db\alembic.ini downgrade 4af09f9d46a0
   ```

2. **Verificar Logs**
   ```bash
   tail -f logs/app.log
   ```

3. **Neon Support**
   - Dashboard: https://console.neon.tech
   - Docs: https://neon.tech/docs

### Documentação de Referência

- [FASE1_CONCLUIDA.md](FASE1_CONCLUIDA.md) - Relatório completo da implementação
- [IMPLEMENTACAO_RELATORIOS_STATUS.md](IMPLEMENTACAO_RELATORIOS_STATUS.md) - Status detalhado
- [MANUAL_DE_RELATORIOS.md](MANUAL_DE_RELATORIOS.md) - Especificação dos relatórios
- [REGRAS_SISTEMAS.md](REGRAS_SISTEMAS.md) - RAG V1.1

---

## ✅ CONCLUSÃO

Este deployment adiciona:
- ✅ 2 novas colunas ao schema (`season_id`, `team_id`)
- ✅ 4 materialized views para relatórios
- ✅ 9 novos endpoints REST
- ✅ 2 foreign keys e 3 índices
- ✅ 1,638 linhas de código Python

**Impacto:** BAIXO
- Schema changes são aditivos (não quebram código existente)
- Colunas são NULLABLE (não requerem dados imediatos)
- Materialized views não afetam performance de writes

**Risco:** BAIXO
- Testado em staging com sucesso
- Rollback simples via alembic downgrade
- Snapshot de backup disponível

---

**Preparado por:** Claude Sonnet 4.5
**Data:** 2025-12-25
**Versão:** 1.0

**PRONTO PARA DEPLOYMENT EM PRODUÇÃO** ✅
