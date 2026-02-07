<!-- STATUS: NEEDS_REVIEW -->

# CHECKLIST GO-LIVE - CONFORMIDADE RAG 100%

**Projeto:** HB Tracking Backend - Sistema de Relatórios
**RAG:** REGRAS_SISTEMAS.md V1.1
**Data Preparação:** 2025-12-25
**Status:** ⏳ AGUARDANDO EXECUÇÃO

---

## 📋 PRÉ-REQUISITOS

### ✅ COMPLETADO (FASE 1)

- [x] 5 migrations criadas e testadas em staging
- [x] 4 materialized views funcionais
- [x] 11 arquivos Python (schemas, services, router)
- [x] 9 endpoints REST implementados
- [x] 3 endpoints de manutenção (refresh)
- [x] Documentação completa (5 documentos)
- [x] Scripts de deployment e verificação

### ⏳ PENDENTE (FASE 2)

- [ ] Migration FASE 2 criada (`b4b136a1af44_finalize_training_sessions_not_null_phase2.py`)
- [ ] Validação de conformidade RAG executada
- [ ] Backup de produção criado

---

## 🎯 CHECKLIST EXECUÇÃO - FASE 2

### ETAPA 1: Validação Pré-Deployment

#### 1.1 Verificar Staging
```bash
# Validar que staging está 100% funcional
python backend/verify_production_rag.py \
  --database-url "postgresql://...@ep-misty-pine-ad12ggz1-pooler..."

# Resultado esperado: CONFORMIDADE RAG: APROVADO (com warnings sobre NULLABLE)
```

**Critérios de Aceitação:**
- [ ] Todas as 4 materialized views existem
- [ ] Todos os índices criados
- [ ] FKs validadas
- [ ] Soft delete ativo (deleted_at)
- [ ] Audit logs ativo

---

### ETAPA 2: Backup de Produção

#### 2.1 Criar Snapshot (Neon)
```bash
# Via Neon Console
1. Acessar https://console.neon.tech
2. Selecionar projeto de produção
3. Ir em "Branches" ou "Backups"
4. Criar snapshot manual com nome: "pre-fase2-relatorios-2025-12-25"
5. Aguardar conclusão
```

**Critérios de Aceitação:**
- [ ] Snapshot criado com sucesso
- [ ] Snapshot validado (pode ser restaurado)
- [ ] Tamanho do backup verificado

#### 2.2 Documentar Rollback
```bash
# Comando de downgrade (se necessário)
alembic downgrade 8fba6a22b58c  # Volta para antes da FASE 2
```

**Critérios de Aceitação:**
- [ ] Comando de rollback testado em staging
- [ ] Tempo de rollback medido (< 5 min)

---

### ETAPA 3: Deployment FASE 2 em Produção

#### 3.1 Aplicar Migration NOT NULL

**IMPORTANTE:** Só executar após validar que NÃO há NULLs em produção!

```bash
# Set DATABASE_URL
export DATABASE_URL="postgresql://neondb_owner:npg_fmT3ctPrD8pW@ep-soft-cake-ad07z2ue-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

# Verificar estado atual
.venv/Scripts/alembic.exe -c backend/db/alembic.ini current
# Esperado: 8fba6a22b58c (head)

# Aplicar FASE 2
.venv/Scripts/alembic.exe -c backend/db/alembic.ini upgrade head

# Verificar sucesso
.venv/Scripts/alembic.exe -c backend/db/alembic.ini current
# Esperado: b4b136a1af44 (head)
```

**Critérios de Aceitação:**
- [ ] Migration executada sem erros
- [ ] Log mostra "Validação OK: Nenhum NULL encontrado"
- [ ] Log mostra "Consistência validada: Todas FKs são válidas"
- [ ] Revision atual é `b4b136a1af44`

**⚠️ SE HOUVER ERRO:**
```bash
# A migration aborta automaticamente se houver NULLs
# Nesse caso:
1. Executar backfill:
   python backend/db/scripts/backfill_simple.py --database-url "$DATABASE_URL"

2. Re-executar migration:
   .venv/Scripts/alembic.exe -c backend/db/alembic.ini upgrade head
```

---

### ETAPA 4: Validação Pós-Deployment

#### 4.1 Executar Verificação RAG Completa
```bash
python backend/verify_production_rag.py \
  --database-url "$DATABASE_URL"
```

**Resultado Esperado:**
```
================================================================================
RELATÓRIO DE CONFORMIDADE RAG
================================================================================

Checks executados: 14
✓ Sucessos: 14
✗ Falhas: 0
Taxa de sucesso: 100.0%

================================================================================
✓ CONFORMIDADE RAG: APROVADO
Sistema está 100% conforme REGRAS_SISTEMAS.md V1.1
================================================================================
```

**Critérios de Aceitação:**
- [ ] ✓ R8/R39: season_id e team_id são NOT NULL
- [ ] ✓ RF29/RD85: 4 materialized views existem
- [ ] ✓ RF29/RD85: 3 índices criados
- [ ] ✓ RDB4: deleted_at column existe
- [ ] ✓ RDB5: audit_logs table existe
- [ ] ✓ R33: Todas FKs válidas
- [ ] ✓ R33: Sem registros órfãos
- [ ] Taxa de sucesso: 100%

#### 4.2 Verificar Schema
```bash
# Verificar colunas
psql $DATABASE_URL -c "
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'training_sessions'
  AND column_name IN ('season_id', 'team_id');
"

# Resultado esperado:
#  column_name | data_type | is_nullable
# -------------+-----------+-------------
#  season_id   | uuid      | NO          ✓
#  team_id     | uuid      | NO          ✓
```

**Critérios de Aceitação:**
- [ ] season_id is_nullable = NO
- [ ] team_id is_nullable = NO
- [ ] Ambas são uuid
- [ ] FKs existem e estão válidas

#### 4.3 Testar Endpoints de Relatórios
```bash
# Iniciar aplicação
uvicorn app.main:app --reload

# Testar via browser
# http://localhost:8000/api/v1/docs
```

**Endpoints a Testar:**

Relatórios:
- [ ] GET `/api/v1/reports/training-performance` → 200 OK
- [ ] GET `/api/v1/reports/training-trends` → 200 OK
- [ ] GET `/api/v1/reports/athletes/{id}` → 200 OK
- [ ] GET `/api/v1/reports/athletes` → 200 OK
- [ ] GET `/api/v1/reports/wellness-summary` → 200 OK
- [ ] GET `/api/v1/reports/wellness-trends` → 200 OK
- [ ] GET `/api/v1/reports/medical-summary` → 200 OK
- [ ] GET `/api/v1/reports/athletes/{id}/medical-history` → 200 OK

Manutenção:
- [ ] POST `/api/v1/reports/refresh/{view_name}` → 200 OK
- [ ] POST `/api/v1/reports/refresh-all` → 200 OK
- [ ] GET `/api/v1/reports/stats` → 200 OK

**Critérios de Aceitação:**
- [ ] Todos os endpoints retornam 200 OK
- [ ] Dados retornados estão corretos
- [ ] Filtros funcionam (season_id, team_id)
- [ ] Permissões validadas (coordenador, treinador)

#### 4.4 Refresh de Materialized Views
```bash
# Via SQL
psql $DATABASE_URL -f backend/db/scripts/refresh_all_materialized_views.sql

# Via API (preferido)
curl -X POST "http://localhost:8000/api/v1/reports/refresh-all" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Critérios de Aceitação:**
- [ ] Todas as 4 views refreshed sem erros
- [ ] Contagens de dados atualizadas
- [ ] Tempo de refresh < 30s (cada view)

---

### ETAPA 5: Testes Funcionais

#### 5.1 Criar Training Session com season_id/team_id
```bash
# Via API
curl -X POST "http://localhost:8000/api/v1/training-sessions" \
  -H "Authorization: Bearer JWT" \
  -H "Content-Type: application/json" \
  -d '{
    "season_id": "uuid-da-temporada",
    "team_id": "uuid-da-equipe",
    "session_at": "2025-12-26T10:00:00Z",
    "planned_load": 500
  }'
```

**Critérios de Aceitação:**
- [ ] Training session criada com sucesso
- [ ] season_id e team_id salvos corretamente
- [ ] FKs validadas (não permite season/team inválidos)
- [ ] Erro se tentar criar sem season_id ou team_id

#### 5.2 Validar Relatórios com Dados Reais
```bash
# Query training performance
curl -X GET "http://localhost:8000/api/v1/reports/training-performance?season_id=XXX"
```

**Critérios de Aceitação:**
- [ ] Relatórios retornam dados da nova session
- [ ] Métricas calculadas corretamente
- [ ] Filtros por season_id funcionam
- [ ] Filtros por team_id funcionam

#### 5.3 Testar Regras de Validação (R33)
```bash
# Tentar criar training session com season_id inválido
curl -X POST "http://localhost:8000/api/v1/training-sessions" \
  -H "Authorization: Bearer JWT" \
  -d '{
    "season_id": "00000000-0000-0000-0000-000000000000",
    "team_id": "uuid-valido",
    ...
  }'

# Resultado esperado: 400 Bad Request ou 422 Validation Error
```

**Critérios de Aceitação:**
- [ ] FK constraint impede season_id inválido
- [ ] FK constraint impede team_id inválido
- [ ] Mensagem de erro clara
- [ ] Banco mantém consistência

---

### ETAPA 6: Performance e Monitoramento

#### 6.1 Validar Performance de Queries
```sql
-- Verificar uso de índices
EXPLAIN ANALYZE
SELECT * FROM mv_training_performance
WHERE season_id = 'uuid-exemplo'
  AND team_id = 'uuid-exemplo'
  AND session_at >= '2025-01-01'
ORDER BY session_at DESC;

-- Resultado esperado: Index Scan usando idx_training_sessions_org_season_date
```

**Critérios de Aceitação:**
- [ ] Queries usam índices (não Seq Scan)
- [ ] Tempo de resposta < 100ms
- [ ] Plano de execução otimizado

#### 6.2 Monitorar Logs
```bash
# Application logs
tail -f logs/app.log | grep "reports"

# Database logs (se disponível)
# Verificar slow queries, deadlocks, etc.
```

**Critérios de Aceitação:**
- [ ] Sem erros 500 nos endpoints
- [ ] Sem queries lentas (> 1s)
- [ ] Sem deadlocks

---

### ETAPA 7: Documentação e Comunicação

#### 7.1 Atualizar Documentação
- [ ] Marcar FASE 2 como COMPLETA em [FASE1_CONCLUIDA.md](FASE1_CONCLUIDA.md)
- [ ] Atualizar status em [IMPLEMENTACAO_RELATORIOS_STATUS.md](IMPLEMENTACAO_RELATORIOS_STATUS.md)
- [ ] Documentar data de Go-Live em [README_RELATORIOS.md](README_RELATORIOS.md)

#### 7.2 Comunicar Time
- [ ] Notificar coordenadores sobre novos relatórios
- [ ] Compartilhar link da documentação da API (`/api/v1/docs`)
- [ ] Agendar treinamento (se necessário)

---

## ✅ CRITÉRIOS DE GO/NO-GO

### GO (Pode ir para produção)

**Todos os itens abaixo devem ser TRUE:**

- [x] FASE 1 completa em staging
- [ ] Backup de produção criado e validado
- [ ] Migration FASE 2 aplicada sem erros
- [ ] `verify_production_rag.py` retorna "APROVADO"
- [ ] season_id e team_id são NOT NULL
- [ ] Todas as 4 materialized views existem e têm dados
- [ ] Todos os índices criados
- [ ] FKs validadas sem registros órfãos
- [ ] Todos os 12 endpoints retornam 200 OK
- [ ] Testes funcionais passaram
- [ ] Performance validada (queries < 100ms)
- [ ] Sem erros em logs

**Taxa mínima de conformidade:** 100%

### NO-GO (NÃO pode ir para produção)

**Se QUALQUER item abaixo for TRUE:**

- [ ] `verify_production_rag.py` retorna "REPROVADO"
- [ ] Existem NULLs em season_id ou team_id
- [ ] Alguma materialized view não existe
- [ ] FKs inválidas ou registros órfãos
- [ ] Endpoints retornam erros 500
- [ ] Performance insatisfatória (> 500ms)
- [ ] Erros críticos em logs

**Ação:** Executar rollback e investigar

---

## 🔄 PLANO DE ROLLBACK

### Cenário 1: Migration FASE 2 Falhou

```bash
# A migration aborta automaticamente se houver NULLs
# Nenhuma ação necessária - estado permanece em 8fba6a22b58c

# Se necessário, verificar:
.venv/Scripts/alembic.exe -c backend/db/alembic.ini current
```

### Cenário 2: Migration Aplicada mas Sistema Instável

```bash
# Downgrade para FASE 1
.venv/Scripts/alembic.exe -c backend/db/alembic.ini downgrade 8fba6a22b58c

# Validar downgrade
python backend/verify_production_rag.py --database-url "$DATABASE_URL"
# Resultado: APROVADO (com warnings sobre NULLABLE)
```

### Cenário 3: Corrupção de Dados

```bash
# Restaurar snapshot do Neon
1. Acessar Neon Console
2. Selecionar snapshot "pre-fase2-relatorios-2025-12-25"
3. Restaurar
4. Atualizar connection string se necessário
5. Validar com verify_production_rag.py
```

---

## 📊 MÉTRICAS DE SUCESSO

### Deployment
- **Tempo Total:** < 15 minutos
- **Downtime:** 0 minutos (migrations são online)
- **Taxa de Sucesso:** 100%

### Performance
- **Endpoints:** < 500ms (p95)
- **Materialized Views:** < 100ms (query direta)
- **Refresh:** < 30s por view

### Qualidade
- **Conformidade RAG:** 100%
- **Cobertura de Testes:** 100% dos endpoints
- **Erros em Produção:** 0

---

## 📝 LOG DE EXECUÇÃO

### Registro de Deployment

**Data:** _____________________
**Executado por:** _____________________
**Ambiente:** PRODUÇÃO

**Checklist:**
- [ ] ETAPA 1: Validação Pré-Deployment → OK
- [ ] ETAPA 2: Backup de Produção → OK
- [ ] ETAPA 3: Deployment FASE 2 → OK
- [ ] ETAPA 4: Validação Pós-Deployment → OK
- [ ] ETAPA 5: Testes Funcionais → OK
- [ ] ETAPA 6: Performance e Monitoramento → OK
- [ ] ETAPA 7: Documentação e Comunicação → OK

**Resultado:** ⬜ GO-LIVE APROVADO  /  ⬜ ROLLBACK EXECUTADO

**Observações:**
```
_______________________________________________________
_______________________________________________________
_______________________________________________________
```

**Assinatura:** _____________________

---

## 🎯 PRÓXIMOS PASSOS PÓS GO-LIVE

### Imediato (Dia 1)
- [ ] Monitorar logs por 24h
- [ ] Validar métricas de performance
- [ ] Coletar feedback de usuários iniciais

### Curto Prazo (Semana 1)
- [ ] Configurar refresh automático (cron job)
- [ ] Ajustar índices se necessário
- [ ] Otimizar queries lentas

### Médio Prazo (Mês 1)
- [ ] Analisar padrões de uso
- [ ] Implementar melhorias baseadas em feedback
- [ ] Planejar GRUPO 2 (relatórios avançados)

---

**Preparado por:** Claude Sonnet 4.5
**Data:** 2025-12-25
**Versão:** 1.0
**Status:** ⏳ **PRONTO PARA EXECUÇÃO**
