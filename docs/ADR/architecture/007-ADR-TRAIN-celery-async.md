# 007-ADR-TRAIN — Automação Assíncrona via Celery

**Status:** Aceita
**Data:** 2026-02-08
**Autor:** Equipe HB Track
**Fase:** F2
**Módulos Afetados:** backend | infra

---

## Contexto

Algumas operações do módulo Training não devem ocorrer inline (sincronamente no request/response cycle) por impacto de performance, acoplamento ou complexidade de processamento.

Exemplos: atualização automática de status após conclusão de treino, cálculo de analytics/agregações semanais, pós-processamento de wellness data e geração de alertas de sobrecarga.

**Componentes Relacionados:**
- Modelo de dados: `training_analytics_cache`, `training_alerts`, `training_suggestions`
- Constraints: `ck_training_alerts_type`, `ck_training_alerts_severity`, `ck_training_suggestions_status`
- Infraestrutura: Celery workers + Redis broker
- Invariantes: classes E1 (fire-and-forget) e E2 (com efeito colateral em DB)

---

## Decisão

Processos como:
- Atualização automática de status (lifecycle transitions)
- Agregações de analytics (cache semanal/mensal)
- Pós-processamento de wellness e geração de alertas
- Sugestões automáticas de ajuste de carga

**devem** ser executados via **Celery + Redis**, fora do ciclo HTTP.

### Detalhes Técnicos

```
Arquitetura:

  HTTP Request → FastAPI → Response (sync, rápido)
                    ↓
              Celery Task (async, via Redis broker)
                    ↓
              Worker processa → DB update (analytics_cache, alerts, suggestions)
```

```sql
-- Tabelas alimentadas por tarefas assíncronas:

-- training_analytics_cache (schema.sql:2371)
CONSTRAINT ck_training_analytics_cache_granularity CHECK (
  (granularity)::text = ANY (ARRAY['weekly', 'monthly']::text[])
)

-- training_alerts (schema.sql:2329-2330)
CONSTRAINT ck_training_alerts_severity CHECK (
  (severity)::text = ANY (ARRAY['warning', 'critical']::text[])
)
CONSTRAINT ck_training_alerts_type CHECK (
  (alert_type)::text = ANY (ARRAY['weekly_overload', 'low_wellness_response']::text[])
)

-- training_suggestions (schema.sql:2763-2764)
CONSTRAINT ck_training_suggestions_status CHECK (
  (status)::text = ANY (ARRAY['pending', 'applied', 'dismissed']::text[])
)
```

**Stack envolvida:**
- Backend: Celery (task queue) + Redis (broker/result backend)
- Database: PostgreSQL — tabelas de cache e alertas
- Deploy: Render — workers separados do web server

---

## Alternativas Consideradas

### Alternativa 1: Processamento inline (síncrono no request)

**Prós:**
- Implementação mais simples
- Sem infraestrutura adicional (sem Redis, sem workers)

**Contras:**
- Timeout em requests longos (agregações pesadas)
- Acoplamento: falha no analytics bloqueia resposta do treino
- Escalabilidade limitada

**Razão da rejeição:** Agregações e alertas podem levar segundos; bloquear o request é inaceitável para UX.

### Alternativa 2: Cron jobs / scheduled tasks

**Prós:**
- Mais simples que Celery (sem broker)
- Suficiente para processamento batch

**Contras:**
- Sem processamento event-driven (apenas time-based)
- Sem retry/backoff nativo
- Sem visibilidade de status de tasks

**Razão da rejeição:** O sistema precisa de processamento tanto event-driven (ao salvar treino) quanto scheduled (agregações semanais). Celery suporta ambos.

---

## Consequências

### Positivas
- ✅ Melhor performance no ciclo HTTP (response rápido, processamento em background)
- ✅ Menor acoplamento entre funcionalidades core e analytics
- ✅ Retry automático com backoff para tasks que falham
- ✅ Escalabilidade horizontal (mais workers conforme necessário)

### Negativas
- ⚠️ Complexidade de infraestrutura: Redis como dependência adicional
- ⚠️ Necessidade de testes assíncronos dedicados (classes E1/E2 do testing canon)
- ⚠️ Eventual consistency: analytics pode estar defasado até o worker processar

### Neutras
- ℹ️ Invariantes E1 (fire-and-forget) e E2 (com efeito em DB) refletem os dois padrões de tasks

---

## Validação

### Critérios de Conformidade
- [x] Tabelas de analytics/alertas/sugestões alimentadas por workers
- [x] Constraints de tipo e status nas tabelas assíncronas presentes no schema
- [x] Invariantes classes E1/E2 definidas no testing canon

---

## Referências

- `Hb Track - Backend/docs/_generated/schema.sql:2371`: `ck_training_analytics_cache_granularity`
- `Hb Track - Backend/docs/_generated/schema.sql:2329-2330`: `ck_training_alerts_severity`, `ck_training_alerts_type`
- `Hb Track - Backend/docs/_generated/schema.sql:2763-2764`: `ck_training_suggestions_status`, `ck_training_suggestions_type`
- `docs/TRD_TRAINING.md`: dependência explícita de Celery
- `docs/PRD_BASELINE_ASIS_TRAINING.md`: infraestrutura declarada
- ADRs relacionados: ADR-TRAIN-004 (invariantes — classes E1/E2)

---

## Revisões

| Data | Autor | Mudança | Versão |
|------|-------|---------|--------|
| 2026-02-08 | Equipe HB Track | Criação inicial | 1.0 |
| 2026-02-08 | Equipe HB Track | Adequação ao template padrão ADR com evidências de schema | 1.1 |
