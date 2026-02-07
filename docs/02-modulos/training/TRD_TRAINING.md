# TRD (Technical Reference Document) — Módulo TRAINING

## 1. Change Control

| Campo | Valor |
|-------|-------|
| **TRD válido para** | commit `e02c83ef` |
| **Manifest** | `Hb Track - Backend/docs/_generated/manifest.json` |
| **Generated at** | 2026-01-29T10:05:54Z |
| **Versão** | v1.6 |

---

## 1.1 Status de Gaps (GAP-001/GAP-002)

**GAP-001 — Template UI**: **CLOSED/VERIFIED**
- (a) Report de permissões: `docs/_generated/trd_training_permissions_report.txt:27-32`
- (b) Backend com `ctx.requires`: `Hb Track - Backend/app/api/v1/routers/session_templates.py:54`, `Hb Track - Backend/app/api/v1/routers/session_templates.py:100`, `Hb Track - Backend/app/api/v1/routers/session_templates.py:179`, `Hb Track - Backend/app/api/v1/routers/session_templates.py:222`, `Hb Track - Backend/app/api/v1/routers/session_templates.py:323`, `Hb Track - Backend/app/api/v1/routers/session_templates.py:374`
- (c) Frontend com gating por `permission_keys`: `Hb Track - Fronted/src/app/(admin)/training/configuracoes/ConfiguracoesClient.tsx:56`, `Hb Track - Fronted/src/app/(admin)/training/configuracoes/ConfiguracoesClient.tsx:69`, `Hb Track - Fronted/src/app/(admin)/training/configuracoes/ConfiguracoesClient.tsx:75`

**GAP-002 — E2E determinístico**: **CLOSED/VERIFIED**
- (d) Output do pytest (execução obrigatória):
```
./venv/Scripts/python.exe -m pytest tests/e2e/test_training_flow_e2e.py -q
.                                                                        [100%]
1 passed, 88 warnings in 5.29s
```

---

## 2. Escopo e Fontes de Verdade

### 2.1 Escopo
Este TRD cobre o módulo **Training** do HB Track.

**Training scope** = paths OpenAPI (inclui variantes hífen/underscore quando existirem):
```
/api/v1/training-sessions/*    /api/v1/training_sessions/*
/api/v1/wellness-pre/*         /api/v1/wellness_pre/*
/api/v1/wellness-post/*        /api/v1/wellness_post/*
/api/v1/exercises/*
/api/v1/exercise-tags/*        /api/v1/exercise_tags/*
/api/v1/exercise-favorites/*   /api/v1/exercise_favorites/*
/api/v1/training-cycles/*      /api/v1/training_cycles/*
/api/v1/training-microcycles/* /api/v1/training_microcycles/*
/api/v1/session-templates/*    /api/v1/session_templates/*
/api/v1/training/alerts-suggestions/*
/api/v1/attendance/*
/api/v1/analytics/wellness-rankings/*
/api/v1/analytics/team/*
```

Definições:
- Escopo do módulo (TRD): tudo que pertence ao módulo Training (API + serviços internos + tabelas).
- Escopo de verificação OpenAPI (Training scope): somente os paths acima, usados para contagem de operationIds e checagem de órfãos.
Nota: itens internos (ex.: FR-009 Export LGPD via ExportService) podem existir no TRD mesmo com Endpoints=0 no OpenAPI.

Nota: o OpenAPI contém endpoints com hífen e underscore; use **operationId** como âncora, não o path.

**Contagem de endpoints** (verificado via scripts):
| Métrica | Valor | Artefato |
|---------|-------|----------|
| OpenAPI (Training scope) | 80 | `trd_training_openapi_operationIds.txt` |
| Citados no TRD (operationIds únicos) | 80 | `trd_training_trd_operationIds.txt` |
| Órfãos (OpenAPI → TRD) | 0 | `trd_training_verification_report.txt` |
| Missing from OpenAPI (TRD → OpenAPI) | 0 | `trd_training_verification_report.txt` |

**Método de verificação**:
```bash
python3 docs/scripts/trd_extract_training_openapi_ids.py
python3 docs/scripts/trd_extract_trd_operationIds.py
python3 docs/scripts/trd_verify_training.py
```

**Funcionalidades cobertas**:
- Sessões de treino (CRUD, workflow, desvios)
- Wellness pré/pós treino
- Banco de exercícios
- Ciclos e microciclos
- Templates de sessão
- Gamificação (badges, rankings)
- Alertas e sugestões
- Presença (attendance)
- Analytics (wellness rankings + training analytics) e cache
- Export LGPD

### 2.2 Fontes de Verdade
| Fonte | Path | Descrição |
|-------|------|-----------|
| OpenAPI | `Hb Track - Backend/docs/_generated/openapi.json` | Contratos de API |
| Schema | `Hb Track - Backend/docs/_generated/schema.sql` | Estrutura de dados |
| Alembic | `Hb Track - Backend/docs/_generated/alembic_state.txt` | Estado de migrations |
| Manifest | `Hb Track - Backend/docs/_generated/manifest.json` | Checksums e rastreabilidade |

### 2.3 Precedência
```
DB constraints > service validations > OpenAPI > docs manuais
```

### 2.4 Regra de Não-Duplicação
TRD **não duplica** OpenAPI/schema. Ele **referencia** por `operationId` e nome de constraint.

---

## 3. Visão de Domínio

### 3.1 Entidades Principais
```
training_sessions          - Unidade de treino
training_session_exercises - Vínculo sessão-exercício
wellness_pre               - Bem-estar pré-treino
wellness_post              - Bem-estar pós-treino (RPE, internal_load)
attendance                 - Presença por treino
training_cycles            - Macro e mesociclos
training_microcycles       - Microciclos (planejamento semanal)
session_templates          - Templates reutilizáveis
exercises                  - Banco de exercícios
exercise_tags              - Tags hierárquicas
athlete_badges             - Gamificação
team_wellness_rankings     - Rankings mensais
training_alerts            - Alertas automáticos
training_suggestions       - Sugestões de ajuste
training_analytics_cache   - Cache de métricas
export_jobs                - Export LGPD (jobs)
```

### 3.2 Relacionamentos Principais
```
training_sessions
  ├─→ training_session_exercises ─→ exercises
  ├─→ training_microcycles ─→ training_cycles
  ├─→ wellness_pre (1:1 per athlete)
  ├─→ wellness_post (1:1 per athlete)
  └─→ attendance (N per session)

training_sessions.microcycle_id (nullable)
  - NULL: sessão criada avulsa
  - NOT NULL: sessão originada de microciclo
```

---

## 4. Lifecycle — Training Session

### 4.1 Status Enum
```
draft → scheduled → in_progress → pending_review → readonly
```
Nota: no front/UI o estado pode aparecer como **closed**; no DB o valor é `readonly`.

### 4.2 Semântica por Status
| Status | Descrição |
|--------|-----------|
| `draft` | Sessão criada, ainda editável e incompleta |
| `scheduled` | Sessão planejada/oficial para execução |
| `in_progress` | Sessão em execução |
| `pending_review` | Sessão finalizada aguardando revisão |
| `readonly` | Sessão fechada e bloqueada (salvo exceções) |

### 4.3 Transições Permitidas
| De | Para | Gatilho | Condição | Evidência |
|----|------|---------|----------|-----------|
| draft | scheduled | User action (publish) | Validação de campos completa | `publish_training_session_api_v1_training_sessions__training_session_id__publish_post` — `/api/v1/training-sessions/{training_session_id}/publish` |
| scheduled | in_progress | Celery task | `NOW >= session_at` | `celery_tasks.py:617` |
| in_progress | pending_review | Celery task | `NOW >= session_at + duration_planned_minutes` | `celery_tasks.py:645` |
| pending_review | readonly | User action (close) | User action | `close_training_session_api_v1_training_sessions__training_session_id__close_post` — `/api/v1/training-sessions/{training_session_id}/close` |

**Timezone**:
- `session_at`: `timestamp with time zone NOT NULL` (`schema.sql:2585`)
- Celery usa: `datetime.now(timezone.utc)` (`celery_tasks.py:610`)

### 4.4 Regras por Status
| Status | O que pode editar |
|--------|-------------------|
| `draft` | Todos os campos de planejamento e composição |
| `scheduled` | Apenas focos, notas, campos complementares (RULE-SESSION-EDIT-*) |
| `in_progress` | Apenas notas e ocorrências |
| `pending_review` | Apenas revisão pós-treino |
| `readonly` | Read-only (exceção: admin notes com RULE-SESSION-IMMUTABLE-60D) |

### 4.5 Evidência
- Constraint: `check_training_session_status` em `training_sessions` (`schema.sql:2627`)
- Service: `training_session_service.py` (validações de transição)
- Celery: `update_training_session_statuses_task` em `celery_tasks.py:581-676`

---

## 5. Evidence Ledger (Regras Confirmadas)

| ID | Regra | Escopo | Onde Imposto | Evidência | Severidade |
|----|-------|--------|--------------|-----------|------------|
| RULE-FOCUS-MAX-120 | Soma focus ≤120% | session/microcycle/template | DB + service | `ck_session_templates_focus_sum`, `training_microcycle_service.py:11` | bloqueia |
| RULE-WPRE-DEADLINE-2H | Wellness pré bloqueado se session_at - 2h < NOW | wellness_pre | service | `wellness_pre_service.py:86-95` | bloqueia |
| RULE-WPOST-DEADLINE-24H | Wellness pós bloqueado se created_at + 24h < NOW | wellness_post | service | `wellness_post_service.py:86-92` | bloqueia |
| RULE-SESSION-EDIT-AUTHOR-10M | Autor pode editar até 10min após criação | session | service | `training_session_service.py:52` | bloqueia |
| RULE-SESSION-EDIT-SUPERIOR-24H | Superior pode editar até 24h | session | service | `training_session_service.py:53` | bloqueia |
| RULE-SESSION-IMMUTABLE-60D | Sessão >60 dias é readonly | session | service | `training_session_service.py:57` | bloqueia |
| RULE-EXPORT-RATE-PDF-5D | Máx 5 exports PDF/dia | export | service | `export_service.py:30` | rate-limit |
| RULE-EXPORT-RATE-ATHLETE-3D | Máx 3 exports athlete/dia | export | service | `export_service.py:31` | rate-limit |
| RULE-LGPD-RETENTION-3Y | Retenção 3 anos, depois anonymiza | wellness/badges | service | `data_retention_service.py:64` | compliance |
| RULE-BADGE-MONTHLY-90PCT | Badge monthly se response_rate ≥90% | gamification | service | `wellness_gamification_service.py:128` | award |
| RULE-BADGE-STREAK-3M | Badge streak se 3 meses consecutivos | gamification | service | `wellness_gamification_service.py:147-154` | award |
| RULE-OVERLOAD-THRESHOLD-1.5X | Alerta se carga >1.5× threshold | alerts | service | `training_alerts_service.py:82` | alerta |
| RULE-SESSION-LIFECYCLE | Toda session segue draft→scheduled→in_progress→pending_review→readonly | session | service + Celery | `publish_training_session_api_v1_training_sessions__training_session_id__publish_post`, `close_training_session_api_v1_training_sessions__training_session_id__close_post`, `celery_tasks.py:617,645` | bloqueia |
| RULE-MICROCYCLE-SESSION-DEFAULT | Sessões via microciclo: draft se incompletas, scheduled se completas | microcycle | service | `training_session_service.py:237-239` | — |
| RULE-SOFTDELETE-REASON-PAIR | deleted_at e deleted_reason ambos NULL ou ambos preenchidos | tabelas com CHECK confirmada | DB constraint | `ck_training_sessions_deleted_reason`, `ck_wellness_pre_deleted_reason`, `ck_wellness_post_deleted_reason`, `ck_attendance_deleted_reason` | bloqueia |
| RULE-UNIQUE-WPRE-ATHLETE-SESSION | 1 wellness_pre por athlete×session | wellness_pre | DB | `ux_wellness_pre_session_athlete` | bloqueia |
| RULE-UNIQUE-WPOST-ATHLETE-SESSION | 1 wellness_post por athlete×session | wellness_post | DB | `ux_wellness_post_session_athlete` | bloqueia |
| RULE-DEVIATION-THRESHOLD-20PTS | Desvio ≥20pts em qualquer foco = significativo | session | service | `training_session_service.py:803` | alerta |
| RULE-DEVIATION-AGGREGATE-30PCT | Desvio agregado ≥30% = significativo | session | service | `training_session_service.py:815` | alerta |
| RULE-JUSTIFICATION-MIN-50CHARS | Justificativa de desvio mín 50 caracteres | session | service | `training_session_service.py:525` | bloqueia |

---

## 6. Mapa PRD-FR → Contratos

### PRD-FR-001 — Gestão de Sessões de Treino

**Objetivo**: CRUD de sessões com workflow de status, validação de focus e gestão de participantes.

**API Contracts**:
| operationId | Method | Path |
|-------------|--------|------|
| `list_training_sessions_api_v1_training_sessions_get` | GET | `/api/v1/training-sessions` |
| `create_training_session_api_v1_training_sessions_post` | POST | `/api/v1/training-sessions` |
| `get_training_session_by_id_api_v1_training_sessions__training_session_id__get` | GET | `/api/v1/training-sessions/{training_session_id}` |
| `update_training_session_api_v1_training_sessions__training_session_id__patch` | PATCH | `/api/v1/training-sessions/{training_session_id}` |
| `delete_training_session_api_v1_training_sessions__training_session_id__delete` | DELETE | `/api/v1/training-sessions/{training_session_id}` |
| `publish_training_session_api_v1_training_sessions__training_session_id__publish_post` | POST | `.../publish` |
| `close_training_session_api_v1_training_sessions__training_session_id__close_post` | POST | `.../close` |
| `duplicate_training_session_api_v1_training_sessions__training_session_id__duplicate_post` | POST | `.../duplicate` |
| `restore_training_session_api_v1_training_sessions__training_session_id__restore_post` | POST | `.../restore` |
| `copy_week_sessions_api_v1_training_sessions_copy_week_post` | POST | `/api/v1/training-sessions/copy-week` |
| `get_session_deviation_api_v1_training_sessions__training_session_id__deviation_get` | GET | `.../deviation` |
| `get_wellness_status_api_v1_training_sessions__training_session_id__wellness_status_get` | GET | `.../wellness-status` |

**Data Contracts**:
- Tabela: `training_sessions`
- Constraints: `check_training_session_status`, `ck_training_sessions_type`, `check_training_sessions_execution_outcome`
- FKs: `team_id`, `season_id`, `microcycle_id`, `organization_id`, `created_by_user_id`

**Regras Aplicáveis**: RULE-FOCUS-MAX-120, RULE-SESSION-EDIT-AUTHOR-10M, RULE-SESSION-EDIT-SUPERIOR-24H, RULE-SESSION-IMMUTABLE-60D, RULE-SESSION-LIFECYCLE, RULE-DEVIATION-THRESHOLD-20PTS, RULE-DEVIATION-AGGREGATE-30PCT, RULE-JUSTIFICATION-MIN-50CHARS

**Erros Relevantes**:
| Código | Condição |
|--------|----------|
| 422 | Validação falhou (focus >120%, campos obrigatórios) |
| 403 | Permissão insuficiente |
| 404 | Sessão não encontrada |
| 409 | Conflito de status (transição inválida) |

**Side Effects**:
- Auto-gera sugestão se focus >100% — **Confirmado**: `training_session_service.py:877`
- Audit log — **Confirmado** (INV-TRAIN-019): `training_session_service.py:246-255` (create), `:341-348` (update), `:393-399` (publish), `:764-770` (close). Teste: `tests/integration/test_training_session_audit_logs.py::test_audit_logs_for_create_update_publish_and_close`
- Cache invalidation — **Confirmado** (INV-TRAIN-020): trigger `tr_invalidate_analytics_cache` (`schema.sql:5208`). Teste: `tests/unit/test_inv_train_020_cache_invalidation_trigger.py::TestInvTrain020CacheInvalidationTrigger`

---

### PRD-FR-002 — Monitoramento Wellness Pré-Treino

**Objetivo**: Atleta submete wellness pré-treino com deadline de session_at - 2h.

**API Contracts**:
| operationId | Method | Path |
|-------------|--------|------|
| `list_wellness_pre_by_session_api_v1_wellness_pre_training_sessions__training_session_id__wellness_pre_get` | GET | `/api/v1/wellness-pre/training_sessions/{training_session_id}/wellness_pre` |
| `add_wellness_pre_to_session_api_v1_wellness_pre_training_sessions__training_session_id__wellness_pre_post` | POST | `/api/v1/wellness-pre/training_sessions/{training_session_id}/wellness_pre` |
| `get_wellness_pre_status_api_v1_wellness_pre_training_sessions__training_session_id__wellness_pre_status_get` | GET | `/api/v1/wellness-pre/training_sessions/{training_session_id}/wellness_pre/status` |
| `get_wellness_pre_by_id_api_v1_wellness_pre_wellness_pre__wellness_pre_id__get` | GET | `/api/v1/wellness-pre/wellness_pre/{wellness_pre_id}` |
| `update_wellness_pre_api_v1_wellness_pre_wellness_pre__wellness_pre_id__patch` | PATCH | `/api/v1/wellness-pre/wellness_pre/{wellness_pre_id}` |
| `request_wellness_unlock_api_v1_wellness_pre_wellness_pre__wellness_pre_id__request_unlock_post` | POST | `/api/v1/wellness-pre/wellness_pre/{wellness_pre_id}/request-unlock` |

**Data Contracts**:
- Tabela: `wellness_pre`
- Constraints:
  - `ux_wellness_pre_session_athlete` (UNIQUE: training_session_id, athlete_id)
  - `ck_wellness_pre_sleep_hours` (0-24)
  - `ck_wellness_pre_sleep_quality` (1-5)
  - Escalas 0-10 para fatigue, stress, soreness, readiness

**Regras Aplicáveis**: RULE-WPRE-DEADLINE-2H, RULE-UNIQUE-WPRE-ATHLETE-SESSION, RULE-LGPD-RETENTION-3Y

**Erros Relevantes**:
| Código | Condição |
|--------|----------|
| 422 | Validação falhou (escalas fora do range) |
| 403 | Atleta tentando acessar wellness de outro |
| 409 | Wellness já existe para esse athlete×session |
| 423 | Locked (deadline passou) |

**Side Effects**:
- LGPD: registra acesso quando staff lê dados de outros atletas — **Confirmado** (INV-TRAIN-026): `wellness_pre_service.py:69-173` (data_access_logs). Teste: `tests/unit/test_inv_train_026_lgpd_access_logging.py::TestInvTrain026LgpdAccessLogging`
- Badge eligibility atualizado — **PRETENDIDO** (sem evidência localizada no INVARIANTS)

---

### PRD-FR-003 — Monitoramento Wellness Pós-Treino

**Objetivo**: Atleta submete RPE e internal load com deadline de created_at + 24h.

**API Contracts**:
| operationId | Method | Path |
|-------------|--------|------|
| `list_wellness_post_by_session_api_v1_wellness_post_training_sessions__training_session_id__wellness_post_get` | GET | `/api/v1/wellness-post/training_sessions/{training_session_id}/wellness_post` |
| `add_wellness_post_to_session_api_v1_wellness_post_training_sessions__training_session_id__wellness_post_post` | POST | `/api/v1/wellness-post/training_sessions/{training_session_id}/wellness_post` |
| `get_wellness_post_status_api_v1_wellness_post_training_sessions__training_session_id__wellness_post_status_get` | GET | `/api/v1/wellness-post/training_sessions/{training_session_id}/wellness_post/status` |
| `get_wellness_post_by_id_api_v1_wellness_post_wellness_post__wellness_post_id__get` | GET | `/api/v1/wellness-post/wellness_post/{wellness_post_id}` |
| `update_wellness_post_api_v1_wellness_post_wellness_post__wellness_post_id__patch` | PATCH | `/api/v1/wellness-post/wellness_post/{wellness_post_id}` |

**Data Contracts**:
- Tabela: `wellness_post`
- Constraints:
  - `ux_wellness_post_session_athlete` (UNIQUE)
  - `ck_wellness_post_session_rpe` (0-10)
  - Escalas 0-10 para fatigue_after, mood_after, soreness_after
- Cálculo automático: `internal_load = session_rpe × minutes_effective`

**Regras Aplicáveis**: RULE-WPOST-DEADLINE-24H, RULE-UNIQUE-WPOST-ATHLETE-SESSION, RULE-LGPD-RETENTION-3Y

**Erros Relevantes**:
| Código | Condição |
|--------|----------|
| 422 | Validação falhou |
| 403 | Acesso cross-athlete |
| 409 | Duplicate |
| 423 | Locked |

**Side Effects**:
- Internal load calculado automaticamente (trigger DB) — **Confirmado** (INV-TRAIN-021): trigger `tr_calculate_internal_load` (`schema.sql:5194`). Teste: `tests/unit/test_inv_train_021_internal_load_trigger.py::TestInvTrain021InternalLoadTrigger`
- Performance cache atualizado — **Confirmado** (INV-TRAIN-022): `wellness_post_service.py:268-324`. Teste: `tests/unit/test_wellness_post_cache_invalidation.py::test_invalidate_training_analytics_cache_marks_weekly_and_monthly`
- Overload alerts podem ser triggered — **Confirmado** (INV-TRAIN-023): `wellness_post_service.py:330` (`_trigger_overload_alert_on_wellness_post`). Teste: `tests/unit/test_wellness_post_overload_alert_trigger.py::test_trigger_overload_alert_on_wellness_post_uses_session_week_and_team_multiplier`

---

### PRD-FR-004 — Banco de Exercícios

**Objetivo**: Biblioteca de exercícios com tags hierárquicas e favoritos.

**API Contracts**:
| operationId | Method | Path |
|-------------|--------|------|
| `list_exercises_api_v1_exercises_get` | GET | `/api/v1/exercises` |
| `create_exercise_api_v1_exercises_post` | POST | `/api/v1/exercises` |
| `get_exercise_api_v1_exercises__exercise_id__get` | GET | `/api/v1/exercises/{exercise_id}` |
| `update_exercise_api_v1_exercises__exercise_id__patch` | PATCH | `/api/v1/exercises/{exercise_id}` |
| `list_tags_api_v1_exercise_tags_get` | GET | `/api/v1/exercise-tags` |
| `create_tag_api_v1_exercise_tags_post` | POST | `/api/v1/exercise-tags` |
| `update_tag_api_v1_exercise_tags__tag_id__patch` | PATCH | `/api/v1/exercise-tags/{tag_id}` |
| `favorite_exercise_api_v1_exercise_favorites_post` | POST | `/api/v1/exercise-favorites` |
| `list_my_favorites_api_v1_exercise_favorites_get` | GET | `/api/v1/exercise-favorites` |
| `unfavorite_exercise_api_v1_exercise_favorites__exercise_id__delete` | DELETE | `/api/v1/exercise-favorites/{exercise_id}` |
| `add_exercise_to_session_api_v1_training_sessions__session_id__exercises_post` | POST | `/api/v1/training-sessions/{session_id}/exercises` |
| `get_session_exercises_api_v1_training_sessions__session_id__exercises_get` | GET | `/api/v1/training-sessions/{session_id}/exercises` |
| `bulk_add_exercises_to_session_api_v1_training_sessions__session_id__exercises_bulk_post` | POST | `/api/v1/training-sessions/{session_id}/exercises/bulk` |
| `update_session_exercise_api_v1_training_sessions_exercises__session_exercise_id__patch` | PATCH | `/api/v1/training-sessions/exercises/{session_exercise_id}` |
| `reorder_session_exercises_api_v1_training_sessions__session_id__exercises_reorder_patch` | PATCH | `/api/v1/training-sessions/{session_id}/exercises/reorder` |
| `remove_exercise_from_session_api_v1_training_sessions_exercises__session_exercise_id__delete` | DELETE | `/api/v1/training-sessions/exercises/{session_exercise_id}` |

**Data Contracts**:
- Tabelas: `exercises`, `exercise_tags`, `exercise_favorites`, `training_session_exercises`
- `exercise_tags.parent_tag_id` para hierarquia
- `training_session_exercises` permite duplicatas (circuitos)

**Regras Aplicáveis**: Soft delete em session_exercises

**Erros Relevantes**: 422, 404

---

### PRD-FR-005 — Performance Analytics

**Objetivo**: 17 métricas de performance com cache e threshold alerting.

**API Contracts**:
| operationId | Method | Path |
|-------------|--------|------|
| `get_wellness_rankings_api_v1_analytics_wellness_rankings_get` | GET | `/api/v1/analytics/wellness-rankings` |
| `get_team_athletes_90plus_api_v1_analytics_wellness_rankings__team_id__athletes_90plus_get` | GET | `/api/v1/analytics/wellness-rankings/{team_id}/athletes-90plus` |
| `calculate_rankings_manually_api_v1_analytics_wellness_rankings_calculate_post` | POST | `/api/v1/analytics/wellness-rankings/calculate` |

**Data Contracts**:
- Tabela: `training_analytics_cache`
- Granularidade: `weekly` (mês corrente), `monthly` (histórico)
- 17 métricas agregadas por equipe

**Regras Aplicáveis**: RULE-OVERLOAD-THRESHOLD-1.5X, Cache refresh daily — **Confirmado** (INV-TRAIN-027): Schedule `celery_app.py:117` (`refresh-analytics-cache`), Task `celery_tasks.py:768` (`refresh_training_rankings_task`). Teste: `tests/unit/test_refresh_training_rankings_task.py::test_refresh_training_rankings_task_recalculates_dirty_caches`

**Erros Relevantes**: 422

---

### PRD-FR-006 — Sistema de Gamificação

**Objetivo**: Badges para atletas e rankings de equipes.

**API Contracts**: Compartilha endpoints de FR-005 (`/api/v1/analytics/wellness-rankings/calculate`)

**Data Contracts**:
- Tabelas: `athlete_badges`, `team_wellness_rankings`
- Constraint: `ck_athlete_badges_type` ('wellness_champion_monthly', 'wellness_streak_3months')
- Index: `idx_badges_athlete_month`

**Regras Aplicáveis**: RULE-BADGE-MONTHLY-90PCT, RULE-BADGE-STREAK-3M

**Side Effects**:
- WebSocket broadcast para notificação de badge — **Confirmado** (INV-TRAIN-024): `wellness_gamification_service.py:328-387` (badges → NotificationService + broadcast). Teste: `tests/unit/test_inv_train_024_websocket_broadcast.py::TestInvTrain024WebsocketBroadcast`
- Relatório Top 5 performers — **PRETENDIDO** (sem evidência localizada no INVARIANTS)

---

### PRD-FR-007 — Planejamento de Ciclos

**Objetivo**: Macro, meso e microciclos com validação de datas.

**API Contracts**:
| operationId | Method | Path |
|-------------|--------|------|
| `list_training_cycles_api_v1_training_cycles_get` | GET | `/api/v1/training-cycles` |
| `create_training_cycle_api_v1_training_cycles_post` | POST | `/api/v1/training-cycles` |
| `get_training_cycle_api_v1_training_cycles__cycle_id__get` | GET | `/api/v1/training-cycles/{cycle_id}` |
| `update_training_cycle_api_v1_training_cycles__cycle_id__patch` | PATCH | `/api/v1/training-cycles/{cycle_id}` |
| `delete_training_cycle_api_v1_training_cycles__cycle_id__delete` | DELETE | `/api/v1/training-cycles/{cycle_id}` |
| `get_active_cycles_api_v1_training_cycles_teams__team_id__active_get` | GET | `/api/v1/training-cycles/teams/{team_id}/active` |
| `list_training_microcycles_api_v1_training_microcycles_get` | GET | `/api/v1/training-microcycles` |
| `create_training_microcycle_api_v1_training_microcycles_post` | POST | `/api/v1/training-microcycles` |
| `get_current_microcycle_api_v1_training_microcycles_teams__team_id__current_get` | GET | `/api/v1/training-microcycles/teams/{team_id}/current` |
| `get_training_microcycle_api_v1_training_microcycles__microcycle_id__get` | GET | `/api/v1/training-microcycles/{microcycle_id}` |
| `update_training_microcycle_api_v1_training_microcycles__microcycle_id__patch` | PATCH | `/api/v1/training-microcycles/{microcycle_id}` |
| `delete_training_microcycle_api_v1_training_microcycles__microcycle_id__delete` | DELETE | `/api/v1/training-microcycles/{microcycle_id}` |
| `get_microcycle_summary_api_v1_training_microcycles__microcycle_id__summary_get` | GET | `/api/v1/training-microcycles/{microcycle_id}/summary` |

**Data Contracts**:
- Tabelas: `training_cycles` (type: 'macro', 'meso'), `training_microcycles`
- Constraint: `check_cycle_type`
- Validação: `week_start < week_end`

**Regras Aplicáveis**: RULE-FOCUS-MAX-120, RULE-MICROCYCLE-SESSION-DEFAULT

**Erros Relevantes**: 422 (datas inválidas, overlap)

---

### PRD-FR-008 — Templates de Sessão

**Objetivo**: Templates reutilizáveis com focus presets.

**API Contracts**:
| operationId | Method | Path |
|-------------|--------|------|
| `list_session_templates_api_v1_session_templates_get` | GET | `/api/v1/session-templates` |
| `create_session_template_api_v1_session_templates_post` | POST | `/api/v1/session-templates` |
| `get_session_template_api_v1_session_templates__template_id__get` | GET | `/api/v1/session-templates/{template_id}` |
| `update_session_template_api_v1_session_templates__template_id__patch` | PATCH | `/api/v1/session-templates/{template_id}` |
| `delete_session_template_api_v1_session_templates__template_id__delete` | DELETE | `/api/v1/session-templates/{template_id}` |
| `toggle_favorite_template_api_v1_session_templates__template_id__favorite_patch` | PATCH | `/api/v1/session-templates/{template_id}/favorite` |

**Data Contracts**:
- Tabela: `session_templates`
- Constraint: soma focus ≤120% (7 campos focus_*_pct)
- Index: `idx_session_templates_org_favorite`

**Regras Aplicáveis**: RULE-FOCUS-MAX-120

**Erros Relevantes**: 422

---

### PRD-FR-009 — Export LGPD e Compliance

**Objetivo**: Export de dados com rate limiting e anonymização.

**API Contracts**: Via `ExportService` (endpoints internos)

**Data Contracts**:
- Tabela: `export_jobs` (status, params_hash, file_url, expires_at)
- Audit logs para todos exports — **PRETENDIDO** (sem evidência localizada no INVARIANTS)

**Regras Aplicáveis**: RULE-EXPORT-RATE-PDF-5D, RULE-EXPORT-RATE-ATHLETE-3D, RULE-LGPD-RETENTION-3Y

**Side Effects**:
- Celery task async para geração — **Confirmado** (INV-TRAIN-025): `celery_tasks.py:400-556` (`generate_analytics_pdf_task`). Teste: `tests/unit/test_inv_train_025_export_lgpd_endpoints.py::TestInvTrain025ExportLgpdEndpoints`
- Cleanup automático de jobs expirados — **Confirmado** (INV-TRAIN-025): `celery_tasks.py:400-556` (`cleanup_expired_export_jobs_task`). Teste: `tests/unit/test_inv_train_025_export_lgpd_endpoints.py::TestInvTrain025ExportLgpdEndpoints`
- Anonymização: `athlete_id = NULL` após 3 anos — **Confirmado**: RULE-LGPD-RETENTION-3Y

**Erros Relevantes**: 429 RateLimit

---

### PRD-FR-010 — Alerts & Suggestions (NOVO)

**Objetivo**: Alertas automáticos de sobrecarga e sugestões de ajuste de carga.

**API Contracts**:
| operationId | Method | Path |
|-------------|--------|------|
| `get_active_alerts_api_v1_training_alerts_suggestions_alerts_team__team_id__active_get` | GET | `/api/v1/training/alerts-suggestions/alerts/team/{id}/active` |
| `get_alert_history_api_v1_training_alerts_suggestions_alerts_team__team_id__history_get` | GET | `.../history` |
| `get_alert_stats_api_v1_training_alerts_suggestions_alerts_team__team_id__stats_get` | GET | `.../stats` |
| `dismiss_alert_api_v1_training_alerts_suggestions_alerts__alert_id__dismiss_post` | POST | `/api/v1/training/alerts-suggestions/alerts/{id}/dismiss` |
| `get_pending_suggestions_api_v1_training_alerts_suggestions_suggestions_team__team_id__pending_get` | GET | `/api/v1/training/alerts-suggestions/suggestions/team/{id}/pending` |
| `get_suggestion_history_api_v1_training_alerts_suggestions_suggestions_team__team_id__history_get` | GET | `.../history` |
| `get_suggestion_stats_api_v1_training_alerts_suggestions_suggestions_team__team_id__stats_get` | GET | `.../stats` |
| `apply_suggestion_api_v1_training_alerts_suggestions_suggestions__suggestion_id__apply_post` | POST | `/api/v1/training/alerts-suggestions/suggestions/{id}/apply` |
| `dismiss_suggestion_api_v1_training_alerts_suggestions_suggestions__suggestion_id__dismiss_post` | POST | `.../dismiss` |

**Data Contracts**:
- Tabelas: `training_alerts`, `training_suggestions`
- Constraints: `ck_alerts_type`, `ck_alerts_severity`, `ck_suggestions_type`, `ck_suggestions_status`

**Regras Aplicáveis**: RULE-OVERLOAD-THRESHOLD-1.5X

**Side Effects**:
- WebSocket broadcast para coordenadores — **Confirmado** (INV-TRAIN-024): `training_alerts_service.py:364-413` (alertas críticos → broadcast). Teste: `tests/unit/test_inv_train_024_websocket_broadcast.py::TestInvTrain024WebsocketBroadcast`
- Notificação via NotificationService — **Confirmado** (INV-TRAIN-024): `training_alerts_service.py:364-413` (alertas → NotificationService). Teste: `tests/unit/test_inv_train_024_websocket_broadcast.py::TestInvTrain024WebsocketBroadcast`

**Erros Relevantes**: 422, 404

---

### PRD-FR-011 — Attendance (NOVO)

**Objetivo**: Registro de presença por treino com correções administrativas.

**API Contracts**:
| operationId | Method | Path |
|-------------|--------|------|
| `list_attendance_by_session_api_v1_training_sessions__training_session_id__attendance_get` | GET | `/api/v1/training_sessions/{training_session_id}/attendance` |
| `add_attendance_to_session_api_v1_training_sessions__training_session_id__attendance_post` | POST | `/api/v1/training_sessions/{training_session_id}/attendance` |
| `add_attendance_batch_api_v1_training_sessions__training_session_id__attendance_batch_post` | POST | `/api/v1/training_sessions/{training_session_id}/attendance/batch` |
| `update_attendance_api_v1_attendance__attendance_id__patch` | PATCH | `/api/v1/attendance/{attendance_id}` |
| `get_session_attendance_statistics_api_v1_training_sessions__training_session_id__attendance_statistics_get` | GET | `/api/v1/training_sessions/{training_session_id}/attendance/statistics` |
| `correct_attendance_administrative_api_v1_attendance__attendance_id__correct_post` | POST | `/api/v1/attendance/{attendance_id}/correct` |

**Data Contracts**:
- Tabela: `attendance`
- Constraints:
  - `ck_attendance_presence_status` ('present', 'absent')
  - `ck_attendance_participation_type` ('full', 'partial', 'adapted', 'did_not_train')
  - `ck_attendance_source` ('manual', 'import', 'correction')
- Correction audit: `correction_by_user_id`, `correction_at`

**Regras Aplicáveis**: Soft delete, correction audit trail

**Erros Relevantes**: 422, 403, 404

**Nota de contrato (escopo atual)**:
- A rota scoped `/api/v1/teams/{team_id}/trainings/{training_id}/attendance` **não faz parte do contrato atual** (router não exposto no agregador).
- Comportamento observado/testado: retorna **404** quando chamada sem inclusão do router.
- Evidência de teste: `tests/api/test_training.py::TestAttendanceAPI::test_scoped_attendance_route_not_exposed_returns_404`

---

### PRD-FR-012 — Training Analytics (Insights)

**Objetivo**: Sumários agregados, carga semanal, análise de desvios e eficácia preventiva.

**API Contracts**:
| operationId | Method | Path |
|-------------|--------|------|
| `get_team_summary_api_v1_analytics_team__team_id__summary_get` | GET | `/api/v1/analytics/team/{team_id}/summary` |
| `get_weekly_load_api_v1_analytics_team__team_id__weekly_load_get` | GET | `/api/v1/analytics/team/{team_id}/weekly-load` |
| `get_deviation_analysis_api_v1_analytics_team__team_id__deviation_analysis_get` | GET | `/api/v1/analytics/team/{team_id}/deviation-analysis` |
| `get_prevention_effectiveness_api_v1_analytics_team__team_id__prevention_effectiveness_get` | GET | `/api/v1/analytics/team/{team_id}/prevention-effectiveness` |

**Evidência (router)**: `app/api/v1/routers/training_analytics.py:30-204`

**Data Contracts**:
- Tabelas (módulo Training): `training_analytics_cache`, `training_sessions`, `training_microcycles`, `attendance`, `wellness_pre`, `wellness_post`, `training_alerts`, `training_suggestions`
- Dependências externas: `teams`, `athletes`, `medical_cases`
**Evidência**: `app/services/training_analytics_service.py:29-38`, `app/services/prevention_effectiveness_service.py:17-20`

**Regras Aplicáveis**: Threshold dinâmico via `team.alert_threshold_multiplier` — **Evidência**: `app/services/training_analytics_service.py:190-191`

**Erros Relevantes**: 403, 422

---

## 7. Traceability Matrix

### 7.1 Cobertura PRD-FR
| PRD-FR | Descrição | Endpoints | Tabelas | Regras |
|--------|-----------|-----------|---------|--------|
| FR-001 | Sessões de Treino | 12 | 1 | 8 |
| FR-002 | Wellness Pré | 6 | 1 | 3 |
| FR-003 | Wellness Pós | 5 | 1 | 3 |
| FR-004 | Banco de Exercícios | 16 | 4 | 1 |
| FR-005 | Performance Analytics | 3 | 1 | 2 |
| FR-006 | Gamificação | 0* | 2 | 2 |
| FR-007 | Ciclos | 13 | 2 | 2 |
| FR-008 | Templates | 6 | 1 | 1 |
| FR-009 | Export LGPD | 0** | 1 | 3 |
| FR-010 | Alerts & Suggestions | 9 | 2 | 1 |
| FR-011 | Attendance | 6 | 1 | 2 |
| FR-012 | Training Analytics | 4 | 8 | 0 |
| **SOMA (não única)** | | **80** | **25** | **28** |

*FR-006: Endpoints = 0 (compartilhado com FR-005 via `/calculate`)
**FR-009: Endpoints = 0 (via ExportService interno, não exposto no OpenAPI)

Nota: a soma por FR pode divergir de contagens únicas (ver seção 2.1 e relatório de verificação).

### 7.2 Endpoints Órfãos
**Status**: VERIFICADO — ver `docs/_generated/trd_training_verification_report.txt`

**Método de verificação**:
```bash
python3 docs/scripts/trd_extract_training_openapi_ids.py
python3 docs/scripts/trd_extract_trd_operationIds.py
python3 docs/scripts/trd_verify_training.py
```

**Resultados (última execução)**:
- OpenAPI (Training scope): 80
- TRD cited (operationIds únicos): 80
- Órfãos (OpenAPI → TRD): 0
- Missing from OpenAPI (TRD → OpenAPI): 0

Status VERIFIED quando: 
1. `trd_verify_training.py` retorna 0 missing/órfãos 
2. `manifest checksum` corresponde aos artefatos 
_generated para o commit indicado.”

### 7.3 Tabelas Órfãs
**Status**: VERIFICADO — ver `docs/_generated/trd_training_verification_report.txt`

**Método de verificação**:
```bash
python3 docs/scripts/trd_extract_training_tables.py
python3 docs/scripts/trd_extract_trd_tables.py
python3 docs/scripts/trd_verify_training.py
```

**Resultados (última execução)**:
- Schema (Training scope): 17
- TRD cited tables: 17
- Órfãs (Schema → TRD): 0
- Missing from schema (TRD → Schema): 0

---

## 8. Contratos de API (Padrões Transversais)

### 8.1 Autenticação
- Método: `HTTPBearer` (JWT)
- Headers obrigatórios:
  - `Authorization: Bearer <token>`
  - `x-organization-id` (contexto multi-tenant)
- Header opcional: `X-Request-ID` (rastreabilidade)

### 8.2 Formato de Erro
```json
{
  "detail": [
    {
      "loc": ["body", "field_name"],
      "msg": "error message",
      "type": "error_type"
    }
  ]
}
```
Schema: `HTTPValidationError` (422)

### 8.3 Paginação
- Parâmetros: `offset`, `limit` (default 50, max 100)
- Response inclui: `total`, `items`

### 8.4 Rate Limits
| Recurso | Limite | Onde Imposto | Evidência |
|---------|--------|--------------|-----------|
| Export PDF | 5/dia | service | `export_service.py:30` |
| Export Athlete | 3/dia | service | `export_service.py:31` |

### 8.5 Autorização por Endpoint (gerado)
Requisitos de autorização por endpoint (roles + escopos via `permission_dep`, e chaves quando houver `ctx.requires/ctx.can`) estão em:
`docs/_generated/trd_training_permissions_report.txt`

**Gerador**: `python3 docs/scripts/trd_extract_training_permissions_report.py`

**Formato** (colunas):
`operationId`, `method`, `path`, `roles_required`, `require_org`, `require_team`,
`require_team_registration`, `permission_keys`, `evidence_router`, `evidence_permissions_map`

---

## 9. Contratos de Dados (DB)

### 9.1 Soft Delete Pattern

Campos (quando existirem):
- `deleted_at` (timestamp)
- `deleted_reason` (text)

**Garantia em nível de DB (CHECK: ambos NULL ou ambos preenchidos)** — CONFIRMADO:
| Constraint | Tabela | Evidência |
|------------|--------|-----------|
| `ck_training_sessions_deleted_reason` | training_sessions | `schema.sql:2634` |
| `ck_wellness_pre_deleted_reason` | wellness_pre | `schema.sql:2890` |
| `ck_wellness_post_deleted_reason` | wellness_post | `schema.sql:2829` |
| `ck_attendance_deleted_reason` | attendance | `schema.sql:674` |

**Demais tabelas do módulo**: podem possuir `deleted_at/deleted_reason`, mas a constraint não foi listada aqui. Fonte de verdade: `schema.sql` por tabela. (Não assumir garantia DB sem constraint nomeada.)

### 9.2 Audit Pattern

Campos comumente observados no schema (varia por tabela):
- `created_at` (timestamp, geralmente DEFAULT now())
- `updated_at` (timestamp, geralmente DEFAULT now())
- `created_by_user_id` (uuid)

Fonte de verdade por tabela: `schema.sql`.
(Não assumir universalidade destes campos sem checar a definição da tabela.)

### 9.3 Campos Sensíveis (LGPD)
| Tabela | Campos | Classificação |
|--------|--------|---------------|
| `wellness_pre` | sleep_hours, sleep_quality, fatigue_pre, stress_level, muscle_soreness, readiness_score, notes | Dados de saúde |
| `wellness_post` | session_rpe, fatigue_after, mood_after, internal_load, notes | Dados de saúde |

### 9.4 Constraints Importantes
| Constraint | Tabela | Tipo | Descrição |
|------------|--------|------|-----------|
| `check_training_session_status` | training_sessions | CHECK | draft, scheduled, in_progress, pending_review, readonly (`schema.sql:2627`) |
| `ck_training_sessions_type` | training_sessions | CHECK | quadra, fisico, video, reuniao, teste (`schema.sql:2644`) |
| `check_training_sessions_execution_outcome` | training_sessions | CHECK | on_time, delayed, canceled, shortened, extended (`schema.sql:2628`) |
| `ux_wellness_pre_session_athlete` | wellness_pre | UNIQUE | 1 per athlete×session |
| `ux_wellness_post_session_athlete` | wellness_post | UNIQUE | 1 per athlete×session |
| `check_cycle_type` | training_cycles | CHECK | macro, meso (`schema.sql:2404`) |
| `ck_athlete_badges_type` | athlete_badges | CHECK | wellness_champion_monthly, wellness_streak_3months |

---

## 10. Integrações e Dependências

### 10.1 IDs Externos
| ID | Origem | Validado em |
|----|--------|-------------|
| `athlete_id` | Módulo Athletes | FKs em wellness_*, attendance |
| `team_id` | Módulo Teams | FK em training_sessions, cycles |
| `season_id` | Módulo Seasons | FK em training_sessions |
| `organization_id` | Módulo Organizations | Todas as tabelas (multi-tenant) |

### 10.2 Celery Tasks
| Task | Schedule | Evidência |
|------|----------|-----------|
| `check_weekly_overload_task` | Domingo 23h | `celery_app.py:68-73` |
| `check_wellness_response_rates_task` | Diário 8h | `celery_app.py:75-81` |
| `cleanup_old_alerts_task` | Domingo 2h | `celery_app.py:83-89` |
| `update_training_session_statuses_task` | A cada minuto | `celery_app.py:99-105` |
| `anonymize_old_training_data_task` | Diário 4h | `celery_app.py:107-113` |
| `calculate_monthly_badges_task` | 1º dia mês 1h | `celery_app.py:136-139` **(COMENTADO)** |

### 10.3 Redis
- **Confirmado**: Broker/backend Celery em `celery_app.py:28-30`
- **Uso**: Cache de performance, sessions
- **Evidência**: `start-celery-*.ps1`, libs instaladas

---

## 11. Testes e Verificação

### 11.1 Mapa Invariante → Teste
| Regra | Teste | Status |
|-------|-------|--------|
| RULE-FOCUS-MAX-120 | `tests/integration/test_inv_train_001_focus_sum_constraint.py` | **Confirmado** (INV-TRAIN-001) |
| RULE-WPRE-DEADLINE-2H | `tests/unit/test_inv_train_002_wellness_pre_deadline.py` | **Confirmado** (INV-TRAIN-002) |
| RULE-WPOST-DEADLINE-24H | `tests/unit/test_inv_train_003_wellness_post_deadline.py` | **Confirmado** (INV-TRAIN-003) |
| RULE-SESSION-LIFECYCLE | `tests/unit/test_inv_train_006_lifecycle_status.py` | **Confirmado** (INV-TRAIN-006) |
| RULE-UNIQUE-WPRE-ATHLETE-SESSION | `tests/unit/test_inv_train_009_wellness_pre_uniqueness.py` | **Confirmado** (INV-TRAIN-009) |
| RULE-UNIQUE-WPOST-ATHLETE-SESSION | `tests/unit/test_inv_train_010_wellness_post_uniqueness.py` | **Confirmado** (INV-TRAIN-010) |

### 11.2 Paths dos Testes
```
Hb Track - Backend/tests/
├── unit/
│   ├── test_inv_train_002_wellness_pre_deadline.py
│   ├── test_inv_train_003_wellness_post_deadline.py
│   ├── test_inv_train_004_edit_window_time.py
│   ├── test_inv_train_005_immutability_60_days.py
│   ├── test_inv_train_006_lifecycle_status.py
│   ├── test_inv_train_007_celery_utc_timezone.py
│   ├── test_inv_train_008_soft_delete_reason_pair.py
│   ├── test_inv_train_009_wellness_pre_uniqueness.py
│   ├── test_inv_train_010_wellness_post_uniqueness.py
│   ├── test_inv_train_011_deviation_rules.py
│   ├── test_inv_train_012_export_rate_limit.py
│   ├── test_inv_train_013_gamification_badge_rules.py
│   ├── test_inv_train_014_overload_alert_threshold.py
│   ├── test_inv_train_020_cache_invalidation_trigger.py
│   ├── test_inv_train_021_internal_load_trigger.py
│   ├── test_inv_train_024_websocket_broadcast.py
│   ├── test_inv_train_025_export_lgpd_endpoints.py
│   ├── test_inv_train_026_lgpd_access_logging.py
│   ├── test_inv_train_028_focus_sum_constraint.py
│   ├── test_inv_train_029_edit_blocked_after_in_progress.py
│   ├── test_wellness_post_cache_invalidation.py
│   ├── test_wellness_post_overload_alert_trigger.py
│   └── test_refresh_training_rankings_task.py
├── integration/
│   ├── test_inv_train_001_focus_sum_constraint.py
│   ├── test_inv_train_015_training_analytics_exposure.py
│   ├── test_training_session_audit_logs.py
│   └── test_training_session_microcycle_status_route.py
├── api/
│   └── test_training.py (TestAttendanceAPI)
└── e2e/
    └── test_training_flow_e2e.py (Gap-002 CLOSED/VERIFIED)
```

---

## 12. Histórico de Mudanças

| Versão | Data | Autor | Descrição |
|--------|------|-------|-----------|
| v1.6 | 2026-01-31 | Claude Opus 4.5 | Side effects promovidos PRETENDIDO→Confirmado via INVARIANTS (audit log, cache invalidation, internal load trigger, websocket broadcast, export async/cleanup, LGPD access logging, overload alerts, cache refresh daily). Seção 11 atualizada com testes confirmados (INV-TRAIN-001 a INV-TRAIN-029) |
| v1.5 | 2026-01-29 | Codex | Routers sem duplicidade no grafo, OpenAPI regenerado sem warnings, pipeline gera relatório de permissões, status readonly padronizado |
| v1.4 | 2026-01-29 | Codex | Status readonly padronizado, OpenAPI regenerado (80/80), FR-012 com evidências file:line, relatório de autorização com formato/script |
| v1.3 | 2026-01-29 | Codex | FR-012 (Training Analytics), escopo OpenAPI vs módulo explicitado, soft delete/audit sem inferência, constraints alinhadas ao schema, relatório de autorização por endpoint |
| v1.2 | 2026-01-29 | Codex | Contagens factuais via artefatos, scripts de verificação atualizados (OpenAPI/TRD/tabelas), operationIds alinhados ao OpenAPI, FR-012 removido, side effects sem evidência marcados PRETENDIDO |
| v1.1 | 2026-01-29 | Claude Opus 4.5 | Hardening: Training scope explícito, lifecycle com condições temporais, constraints com nomes reais, FR-012 (Reports), side effects marcados PRETENDIDO onde sem evidência, RULE-SOFTDELETE-REASON-PAIR adicionada |
| v1.0 | 2026-01-29 | Claude Opus 4.5 | Criação inicial do TRD com 11 PRD-FR mapeados |

---

**Documento criado por**: Claude Opus 4.5
**TRD Owner**: Product Owner / Tech Lead
**Revisores/Assinatura**: Davi Sermenho (pendente)
**Status**: DRAFT
**Válido para commit**: e02c83ef | 2026-01-29T10:05:54Z
