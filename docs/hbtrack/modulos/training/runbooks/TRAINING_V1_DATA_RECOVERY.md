# Runbook: Recuperação de Dados V1 — Campos de Execução em TrainingSession

## Contexto

A migration `0007_training_session_execution_fields` adicionou 12 campos de execução
à tabela `training_sessions`. Antes desta migration ser aplicada, qualquer use case
que gravasse esses campos (ex: `started_at` ao iniciar uma sessão via
`TransitionTrainingSessionUseCase` com target `IN_PROGRESS`) perdia os dados
silenciosamente — o ORM não tinha a coluna, o repositório desconhecia o campo,
e o request retornava HTTP 200 sem erro (bug de perda silenciosa — V1).

Este runbook documenta como identificar e recuperar dados afetados.

---

## Campos afetados

| Campo | Preenchido quando | Transition que grava |
|---|---|---|
| `started_at` | Sessão inicia | `IN_PROGRESS` |
| `ended_at` | Sessão é encerrada | `COMPLETED` ou `CANCELLED` |
| `closed_at` | Sessão é fechada administrativamente | `ARCHIVED` |
| `closed_by_user_id` | Idem | `ARCHIVED` |
| `deviation_justification` | Desvio do planejado registrado | qualquer (opcional) |
| `planning_deviation_flag` | Idem | qualquer (opcional) |
| `duration_actual_minutes` | Encerramento da sessão | `COMPLETED` |
| `execution_outcome` | Idem | `COMPLETED` |
| `delay_minutes` | Idem | `COMPLETED` |
| `cancellation_reason` | Cancelamento | `CANCELLED` |
| `actual_load_recorded` | Registro de carga pós-sessão | `COMPLETED` |
| `post_review_completed_at` | Revisão pós-sessão | `COMPLETED` (workflow de revisão) |

---

## Identificar sessões afetadas

Execute no banco de produção (substitua `hb_track_production` pelo nome real):

```sql
-- Sessões que provavelmente foram iniciadas (IN_PROGRESS ou além)
-- mas têm started_at NULL — candidatas a recuperação
SELECT
    id,
    status,
    session_at,
    organization_id,
    team_id,
    created_at,
    updated_at
FROM training_sessions
WHERE
    status IN ('IN_PROGRESS', 'COMPLETED', 'CANCELLED', 'ARCHIVED')
    AND started_at IS NULL
ORDER BY updated_at DESC;
```

```sql
-- Contagem por status para dimensionar o impacto
SELECT status, count(*) AS total_afetadas
FROM training_sessions
WHERE
    status IN ('IN_PROGRESS', 'COMPLETED', 'CANCELLED', 'ARCHIVED')
    AND started_at IS NULL
GROUP BY status
ORDER BY total_afetadas DESC;
```

---

## Estratégia de recuperação

### Caso 1 — `started_at` ausente (janela de impacto pequena)

**Contexto**: A migration 0007 foi aplicada no deploy do PR `refactor/training-decomposition`.
Sessões transitadas para `IN_PROGRESS` ANTES deste deploy não têm `started_at`.

**Recuperação**: `started_at` pode ser aproximado por `updated_at` da transição —
se o log de aplicação (stdout do container) registrar a transição, use o timestamp do log.
Caso contrário, use `updated_at` como aproximação conservadora.

```sql
-- Aproximação: started_at = updated_at (conservadora)
-- Executar SOMENTE após confirmar impacto com DBA e stakeholder
UPDATE training_sessions
SET started_at = updated_at
WHERE
    status IN ('IN_PROGRESS', 'COMPLETED', 'CANCELLED', 'ARCHIVED')
    AND started_at IS NULL;
```

> ⚠️ **ATENÇÃO**: Executar esta query em transação com `BEGIN`/`ROLLBACK` primeiro
> para verificar o número de linhas afetadas antes de confirmar com `COMMIT`.

### Caso 2 — `ended_at` / `duration_actual_minutes` ausentes

Para sessões `COMPLETED` ou `CANCELLED` sem `ended_at`:

```sql
-- Verificar sessões completadas sem ended_at
SELECT id, status, updated_at
FROM training_sessions
WHERE status IN ('COMPLETED', 'CANCELLED')
  AND ended_at IS NULL;
```

Sem fonte de dados alternativa (logs, eventos), esses campos não podem ser
recuperados com precisão. Opções:
1. Deixar `NULL` (aceitar perda — campo optional no domínio)
2. Usar `updated_at` como aproximação, com flag `planning_deviation_flag = TRUE`
   para sinalizar que o dado foi reconstruído

### Caso 3 — `cancellation_reason` ausente

Não recuperável automaticamente — requer consulta ao usuário que cancelou.
Deixar `NULL` e registrar no changelog do time.

---

## Procedimento seguro de execução

```bash
# 1. Criar backup da tabela antes de qualquer UPDATE
pg_dump -h <host> -U <user> -d hb_track_production \
  -t training_sessions --data-only \
  -f /tmp/training_sessions_backup_$(date +%Y%m%d_%H%M%S).sql

# 2. Conectar ao banco em modo de transação
psql -h <host> -U <user> -d hb_track_production

# 3. Dentro do psql — executar em transação
BEGIN;

-- Identificar linhas afetadas
SELECT count(*) FROM training_sessions
WHERE status IN ('IN_PROGRESS', 'COMPLETED', 'CANCELLED', 'ARCHIVED')
  AND started_at IS NULL;

-- Se count for aceitável, aplicar aproximação
UPDATE training_sessions
SET started_at = updated_at
WHERE status IN ('IN_PROGRESS', 'COMPLETED', 'CANCELLED', 'ARCHIVED')
  AND started_at IS NULL;

-- Verificar resultado
SELECT count(*) FROM training_sessions
WHERE status IN ('IN_PROGRESS', 'COMPLETED', 'CANCELLED', 'ARCHIVED')
  AND started_at IS NULL;
-- deve retornar 0

-- Confirmar OU reverter
COMMIT;   -- confirma
-- ROLLBACK;  -- reverte

# 4. Verificar integridade pós-update
python manage.py check --database default
```

---

## Verificação pós-recuperação

```bash
# Rodar suite de testes de round-trip (escritos na Fase Tier 1)
export PYTHONPATH="src:.:scripts" DJANGO_SETTINGS_MODULE=config.settings TRAINING_CURSOR_SECRET=x
python3 -m pytest src/training/tests/unit/test_session_execution_fields_round_trip.py -v
```

---

## Janela de impacto estimada

| Evento | Data (estimada) |
|---|---|
| Refactor `training-decomposition` iniciado (Fase 0) | início 2026-04 |
| Bug V1 introduzido (25 campos sem migration) | Fases 0–3 (pré-Tier 1) |
| Migration `0007` aplicada (Tier 1, fix V1) | 21/04/2026 |
| **Janela de impacto** | Entre deploy do PR de Fase 4 e deploy do Tier 1 |

Se o ambiente de produção ainda estava em `origin/main` (pré-merge do PR), o impacto
em produção pode ser ZERO — o bug existia apenas na branch de refactor, não em main.

**Verificação definitiva**: checar o `git log --oneline origin/main | head -5` para
confirmar se o commit `1422d446` (Fase 4 — onde TrainingSession ganhou os campos novos)
chegou a entrar em main antes da migration 0007.

---

## Owner e cronograma

- **Owner**: DBA + tech lead de training
- **Urgência**: Executar antes do próximo sprint de relatórios de desempenho
  (qualquer relatório que use `started_at`/`duration_actual_minutes` retornará `NULL`
  para sessões afetadas)
- **Referência**: `.dev/decisões/rafatora_training.md` §7 V1 + §7.3 P2 + §8 N3.4
