# ARCH_DECISIONS_TRAINING.md

**Módulo:** training  
**Status:** information_artifact (reference, auto-generated)  
**Last Updated:** 2026-03-17  
**Compilation Source:** docs/_canon/gates/TRAINING_MODULE_DECISION_IR.yaml  
**Related Contract:** See SESSION_HANDOFF.md for context

---

## Overview

Compilação de decisões arquiteturais (TRAIN-DEC-*) e regras de negócio (RUL-TRAINING-*) do módulo **training**.

Direcionado a: implementadores de backend, QA, e stakeholders técnicos que precisam entender motivações de design.

**Nota:** Este é um documento de referência gerado de SSOT (DECISION_IR.yaml). Alterações arquiteturas devem ser via ADR formal, atualizando DECISION_IR.yaml como SSOT.

---

## Seção 1: Decisões Arquiteturais Macroestruturais

### TRAIN-DEC-001: Finite State Machine para training_session

**Motivação:**  
Treinos têm ciclo de vida bem definido: planejamento → execução → revisão → arquivo.
Transições de estado devem ser explícitas e auditáveis.

**Decision:**
```
DRAFT
  ↓ [publish]
SCHEDULED (PUBLISHED)
  ↓ [start]
IN_PROGRESS
  ├─ [complete]
  │  ↓
  │ COMPLETED (terminal, revisão coach)
  │
  └─ [cancel]
     ↓
   CANCELLED (terminal, cancelado com razão)

COMPLETED, CANCELLED
  ↓ [archive, após 60+ dias]
ARCHIVED (terminal, somente leitura eternamente)
```

**Implementação:**
- enum `training_session_status`: DRAFT, SCHEDULED, IN_PROGRESS, COMPLETED, CANCELLED, ARCHIVED
- Migration v1: coluna `status` com constraint CHECK
- API: validar transições de estado em POST/PATCH `/sessions/{id}/status`

**Related Rules:**
- RUL-TRAINING-001: Apenas coach pode mudar estado
- RUL-TRAINING-002: Transições devem ser sequenciais (não pode DRAFT → COMPLETED)

---

### TRAIN-DEC-002: Role-Based Access Control (RBAC) para training

**Motivação:**  
Diferentes atores (coach, athlete, analyst, medical, admin) têm diferentes permissões.
Segurança e responsabilidade.

**Decision:**

| Role | Pode ver | Pode criar | Pode editar | Pode deletar |
|------|----------|-----------|-----------|-------------|
| head_coach | all sessions | ✓ | ✓ | soft-delete |
| assistant_coach | team sessions | ✓ | ✓ (own) | soft-delete |
| athlete | own sessions, own wellness | — | — | — |
| analyst | all (read-only) | — | — | — |
| medical_staff | wellness/readiness (own team) | — | ✓ notes | — |
| admin | all | all | all | soft-delete |

**Implementação:**
- Policies: training_sessions@view, training_sessions@create, training_sessions@update, training_sessions@delete
- API middleware: check_permission(role, resource, action)
- Database: soft_delete flag (never hard-delete training data, only flag deleted_at)

**Related Rules:**
- RUL-TRAINING-003: Athletes não podem ver outros athletes' wellness data
- RUL-TRAINING-004: Coaches não podem hidden delete sessions (audit trail obrigatória)

---

### TRAIN-DEC-003: Soft-Delete Everywhere

**Motivação:**  
Compliance (8 anos de retenção de dados de esporte). Auditoria.
Incidentes (um delete acidental → revert via backup, não via DB).

**Decision:**
- Nunca executar `DELETE FROM training_sessions`. Sempre `UPDATE training_sessions SET deleted_at = NOW()`
- Todas queries obrigatoriamente filtram `deleted_at IS NULL` (soft-delete policy no DB)
- Soft-deleted records permancem no DB eternamente (no purge)
- Hard-delete apenas via DBA + change control

**Implementação:**
- Todas tables training.*: coluna `deleted_at TIMESTAMP NULL DEFAULT NULL`
- Trigger de soft-delete: atualiza deleted_at + audit log
- ORM (SQLAlchemy): configure query filter `~Training.deleted_at.isnot(None)` on all queries

**Related Rules:**
- RUL-TRAINING-005: Soft-deleted sessions devem ser invisíveis para coach/athlete (except admin read-only view)
- RUL-TRAINING-006: Soft-delete triggers async event: `training_session_archived` (se estado era COMPLETED)

---

### TRAIN-DEC-004: Append-Only Execution Records

**Motivação:**  
Fatos de execução são imutáveis. Modificações de treino são histórico, não sobreposição.
Rastreabilidade completa: quem mudou quê, quando.

**Decision:**
- Tabela `execution_records` é append-only (nunca UPDATE/DELETE)
- Tipos de registros: SESSION_EXECUTION, BLOCK_EXECUTION, LIVE_ADJUSTMENT, CONSTRAINT_OVERRIDE, ALTERNATE_EXERCISE, LOAD_RECALCULATION
- Cada mudança durante treino gera novo registro (não sobrescreve anterior)
- Só read via SELECT, nunca UPDATE

**Implementação:**
- Table: `execution_records (id, session_id, execution_type, context_id, created_at, created_by, metadata_json)`
- Trigger: desabilitar UPDATE/DELETE
- API: POST `/sessions/{id}/execution` (append only)
- Histórico completo visível em session review (coach vê timeline de toda atividade)

**Related Rules:**
- RUL-TRAINING-007: Não pode override coach decisions (execution_records apenas log)
- RUL-TRAINING-008: Athletes não podem ver execution_records (privacidade coach)

---

## Seção 2: Decisões de Modelo de Dados

### TRAIN-DEC-005: Entidades Core (training_session, session_block, session_objective)

**Motivação:**  
Estruturação clara de hierarquia treino (session → blocks → exercises).
Cada nível tem responsabilidades distintas.

**Decision:**

**training_session:**
- ID único, soft-delete, state FSM, timestamps
- Metadados: team_id, coach_id, scheduled_at, actual_start, actual_end
- Focus distribution (7 dimensões: technical, tactical, physical, mental, recovery, team, individual)
- Flags: is_published, analytics_recommendations_pending, attention_queue_count

**session_block:**
- Filho de training_session
- Campos: phase (ACTIVATION, CONDITIONING, SKILL_WORK, STRENGTH, RECOVERY), exercises[], duration_actual
- Nível de granularidade: coach planeja blocos, executa by block

**session_objective:**
- Filho de training_session
- Origem rastreável: origin_enum (need_detected, competitive_focus, development_goal, coach_rationale)
- Estado: OPEN, ACHIEVED, ABANDONED
- Linked com need_detected (FK optional)

**Implementação:**
- 3 migration tables (training_sessions, session_blocks, session_objectives)
- Indexes: session_id (foreign keys), team_id, coach_id, created_at para queries rápidas
- Constraints: cascade delete do session → blocks, objectives

---

### TRAIN-DEC-006: Configuration & Customization per Team

**Motivação:**  
Diferentes times podem ter diferentes politicas (min athletes to attend, focus distribution rules, etc).

**Decision:**
- Cada team tem `training_config` (JSON) com overrides globais
- Config keys: min_athletes_to_schedule, max_focus_single_dimension (%), focus_dimensions_enabled[], readiness_threshold

**Implementação:**
- Table: `training_config (team_id, config_json, updated_at, updated_by)`
- API: GET/PUT `/teams/{team_id}/training-config` (admin only)
- Defaults: codificados em config schema (JSON Schema draft-07)

---

## Seção 3: Decisões de Workflows (Async Events & States)

### TRAIN-DEC-010: training_session Lifecycle Events

**Motivação:**  
Upstream modules (wellness, analytics, notifications, audit) precisam reagir a mudanças de sessão.
Event-driven architecture permite desacoplamento.

**Decision:**

Eventos emitidos em transições de estado:

| De | Para | Evento | Downstream Subscribers |
|----|------|--------|------------------------|
| — | DRAFT | `training_session_created` | notifications (silent), analytics |
| DRAFT | SCHEDULED | `training_session_published` | notifications (enviar alert atl), wellness (check-in window aberto), analytics (coleta sinais) |
| SCHEDULED | IN_PROGRESS | `training_session_started` | wellness (coleta live), audit |
| IN_PROGRESS | COMPLETED | `training_session_completed` | wellness (close check-in), analytics (calcular carga), audit |
| * | CANCELLED | `training_session_cancelled` | notifications, wellness (close check-in), audit |
| COMPLETED, CANCELLED | ARCHIVED | `training_session_archived` | analytics (finaliza sinais), audit (mark read-only) |

**Implementação:**
- 6 novo AsyncAPI events (+ training_attendance_marked existente = 7 sessão-level eventos)
- Event payloads: session_id, team_id, timestamp, transition_reason (optional)
- Publishing: FastAPI background task após state UPDATE (transactional guarantees via Outbox pattern)

---

### TRAIN-DEC-011: wellness Workflow Integration

**Motivação:**  
Athletes precisam fazer self-assessment pré/pós treino.
Coach precisa de readiness data pré-treino para recomendações.

**Decision:**
- Athlete submete wellness_assessment quando check-in pré-treino
- Readiness score (0–100) calculado: (sleep_quality + mood + resting_hr + fatigue_inverse) / 4
- Readiness category: low (<40), moderate (40–70), high (>70)
- Se readiness < config_threshold, coach recebe alerta (atenção_queue item)

**Implementação:**
- POST `/sessions/{id}/check-in` (athlete) → cria wellness_assessment + readiness_assessment eventos
- Background job: cálculo readiness score (async) → POST /analytics/readiness
- Trigger: se readiness < threshold, POST /training/attention-queue/create (item_type: wellness_alert)

---

### TRAIN-DEC-012: Analytics Recommendations Loop (Coach-in-Loop)

**Motivação:**  
Analytics pode gerar recomendações (exercise swaps, load adjustments) PERO coach sempre decide.
Previne blind automation, mantém coach autoridade.

**Decision:**
- Analytics module pode chamar POST `/training/recommendations/{session_id}/create`
- Status inicial: PENDING_COACH_REVIEW
- Coach vê recomendações no UI e clica Aceitar/Rejeitar
- Aceitar → `recommendation_accepted` evento → analytics atualiza
- Rejeitar → `recommendation_dismissed` evento + coach rationale field

**Implementação:**
- Table: `recommendations (id, session_id, type, status, analytics_reasoning_json, coach_decision, dismissal_reason, created_at)`
- FSM: PENDING_COACH_REVIEW → ACCEPTED | DISMISSED
- Events: recommendation_generated, recommendation_accepted, recommendation_dismissed

---

## Seção 4: Decisões de Intervention & Feedback

### TRAIN-DEC-020: Feedback Threads para Coach-Athlete Conversations

**Motivação:**  
Conversas devem ser contextualizadas e rastreáveis (audit, continuity).
Sistema de tickets/threads (não como DMs, mas como conversas com contexto).

**Decision:**
- Cada thread linkado a um contexto: session, block, objective, ou evidence item
- Participants: coach (n), athlete (primary), possible observers (analyst read-only)
- Thread states: OPEN, CLOSED
- Closure outcomes: reflection, commitment, pending_action, followup, decision

**Implementação:**
- Table: `feedback_threads (id, session_id, block_id, objective_id, evidence_id, athlete_id, coach_ids[], status, conversation_outcome, created_at, closed_at)`
- Table: `feedback_messages (id, thread_id, sender_role, message_text, created_at)` (append-only)
- Events: feedback_thread_created, feedback_thread_closed

---

### TRAIN-DEC-021: Attention Queue (Alerts Operacionais)

**Motivação:**  
Alertas devem ser fila processável, não ruído. Coach prioriza por tipo/severidade.

**Decision:**
- Queue items têm tipo: wellness_alert, medical_flag, recovery_concern, individual_performance, group_dynamics
- Estados: ACTIVE, RESOLVED, DISMISSED, ESCALATED
- Cada item requer resolução explícita + evidence
- Oldest items aparecem primeiro (FIFO com severidade customizável)

**Implementação:**
- Table: `attention_queue_items (id, session_id, item_type, athlete_id, severity_score, status, resolution_evidence, resolved_by, created_at, resolved_at)`
- API: GET `/attention-queue?status=ACTIVE&sort=created_at` (coach view)
- Events: attention_queue_item_created, attention_queue_item_resolved

---

## Seção 5: Decisões de Readiness & Eligibility

### TRAIN-DEC-022: Training Readiness Assessment

**Motivação:**  
Dados pré-treino (sleep, mood, HR, fatigue) → readiness score → prescrição adaptativa.

**Decision:**
- Athlete completa wellness_assessment (likert scales + numeric inputs)
- Readiness score calculado por algorithm: (sleep + mood + hr + fatigue_inverse) / 4
- Score usado para:
  1. Coach visualiza se atl está pronto
  2. Analytics pode desrecomendação (descale) se score < threshold
  3. Acionou prescrição adjustment (se habilitado em team config)

**Implementação:**
- Table: `readiness_assessments (id, session_id, athlete_id, sleep_quality, mood, resting_hr, yesterdays_fatigue, computed_score, computed_category, created_at)`
- Function: `compute_readiness_score(s,m,h,f) → (0-100)`
- Event: training_readiness_assessed (publicado pós-cálculo)

---

### TRAIN-DEC-023: Athlete Ineligibility & Prescription Adjustment

**Motivação:**  
Athletes podem declarar-se inelegiveis (médico, testagem, recuperação). Prescrição deve ajustar.

**Decision:**
- Athlete declara ineligibility no check-in (checkboxes + open reason)
- Razões: medical_contra, excessive_fatigue, recovery_window, testing_window, sabbatical
- Se ineligível:
  1. Session prescription descala (se config habilitada)
  2. Coach recebe alert (attention_queue)
  3. Evento: athlete_ineligible_for_prescription emitido

**Implementação:**
- Table: `athlete_ineligibility_declarations (id, athlete_id, ineligibility_reason, ineligibility_start, ineligibility_end, notes, created_at)`
- Coluna: training_sessions.ineligible_athlete_ids (JSON array)
- Event: athlete_ineligible_for_prescription, prescription_adjusted

---

## Seção 6: Decisões de Continuity

### TRAIN-DEC-026: Continuity Snapshots para Periodização

**Motivação:**  
Transições entre períodos (seasonal, pre-competition) devem preservar estado anterior.
Snapshots comprimem histórico para futuros periodos.

**Decision:**
- Ao final de período, criar snapshot: histórico agregado de atleta (volumes, intensidades, readiness patterns)
- Snapshot linkado ao próximo período para baseline
- Usado para progressão adaptativa

**Implementação:**
- Table: `continuity_snapshots (id, athlete_id, snapshot_type, snapshot_period_end, compressed_data_json, created_at)`
- Trigger: manual via coach ou automático em data-limite
- Event: continuity_snapshot_created

---

## Seção 7: Governance Rules (RUL-TRAINING-*)

### RUL-TRAINING-001: State Transition Validation
**Rule:** Coach só pode transicionar de estado atual para próximo estado permitido per FSM.
**Constraint:** API validates antes de UPDATE.
**Enforcement:** DB CHECK constraint + app-level validation.

### RUL-TRAINING-002: Role-Based Permissions
**Rule:** Action permissions baseadas em role (head_coach, assistant_coach, athlete, etc).
**Constraint:** Middleware checks permission before action.

### RUL-TRAINING-003: Athlete Privacy
**Rule:** Athlete não vê wellness data de outros athletes.
**Constraint:** API filters by `athlete_id == current_user_id`.

### RUL-TRAINING-004: Audit Trail Immutability
**Rule:** Todos changes são logged em audit_events (append-only).
**Constraint:** Trigger on every UPDATE to training.* tables.

### RUL-TRAINING-005: Soft-Delete Invisibility
**Rule:** Soft-deleted sessions invisíveis para coach/athlete (except admin).
**Constraint:** Query middleware adds `AND deleted_at IS NULL` filter.

### RUL-TRAINING-006: Focus Distribution Balance
**Rule:** Sum of focus percentages ≤ 100%.
**Constraint:** API validation + DB CHECK constraint.

### RUL-TRAINING-007: Execution Records Immutability
**Rule:** execution_records never updated/deleted (append-only).
**Constraint:** DB trigger BEFORE UPDATE/DELETE raises error.

### RUL-TRAINING-008: Coach Intervention Documentation
**Rule:** Toda mudança em tempo real (live adjustment) requer coach decision + nota.
**Constraint:** API POST /execution requires decision_id field.

---

## Seção 8: Integration Points (Async)

### Outbound Events (training → upstream modules)

1. **training.session.created** → analytics (inicia coleta sinais)
2. **training.session.published** → wellness (abre check-in window), notifications (alerta atletas)
3. **training.session.started** → wellness (coleta live)
4. **training.session.completed** → analytics (finaliza sinais, calcula carga)
5. **training_readiness_assessed** → analytics (input para recomendação)
6. **coach_intervention_required** → audit (log de ação coach)
7. **attention_queue_item_created** → notifications (alerta coach de item na fila)

### Inbound Events (upstream modules → training)

1. **analytics.recommendation_generated** → POST `/training/recommendations` (coach review)
2. **wellness.alert_threshold_exceeded** → POST `/training/attention-queue` (attention item)
3. **medical.contra_detected** → POST `/training/athlete-ineligibility` (flag athlete)

---

## Seção 9: Performance & Scaling Considerations

### TRAIN-DEC-030: Indexing Strategy
- Index: `(team_id, status, created_at)` for session listing
- Index: `(athlete_id, created_at)` for athlete history
- Index: `(session_id, execution_type)` for execution record filtering

### TRAIN-DEC-031: Query Optimization
- Use pagination: max 100 sessions per request
- Cache training_config per team (refresh every 5 min)
- Lazy load feedback threads (fetch only if coach clicks)

### TRAIN-DEC-032: Event Publishing Guarantees
- Use Outbox pattern: INSERT audit_event + training_session in same transaction
- Background job polls outbox every 5sec, publishes to AMQP
- Retry logic: exponential backoff (1s, 2s, 4s, 8s, stop after 60min)

---

## Seção 10: Testing & Validation

### TRAIN-DEC-040: FSM State Transition Tests
- [x] DRAFT → SCHEDULED (valid)
- [x] DRAFT → COMPLETED (invalid, raise error)
- [x] SCHEDULED → DRAFT (invalid, raise error)
- [x] COMPLETED → ARCHIVED (valid)
- [x] *  → CANCELLED (valid from any non-terminal)

### TRAIN-DEC-041: RBAC Permission Tests
Per role × action × resource matrix

### TRAIN-DEC-042: Soft-Delete Tests
Verify `deleted_at IS NULL` filter applied to all queries

---

## Seção 11: Deployment & Rollout

### TRAIN-DEC-050: Blue-Green Deployment Strategy
- Deploy migration v1 (6 tables)
- Deploy API endpoints (read-only first)
- Run compatibility tests vs existing data
- Switch feature flags: training.enabled=true

### TRAIN-DEC-051: Rollback Plan
- Revert migration: `alembic downgrade -1` (destroys tables, not recommended)
- Recommended: keep feature flag off, keep tables live (graceful degradation)

---

## Related Documents

- **SSOT:** `docs/_canon/gates/TRAINING_MODULE_DECISION_IR.yaml`
- **Database Schema:** `migrations/training/versions/20260317_001_create_training_tables.py`
- **AsyncAPI Contract:** `contracts/asyncapi/asyncapi.yaml` (27 events)
- **OpenAPI Contract:** `contracts/openapi/paths/training.yaml`
- **UI Contract:** `docs/hbtrack/modulos/training/UI_CONTRACT_TRAINING.md` (3 flows)
- **JSON Schemas:** `contracts/schemas/training/**`

---

## Approval

Generated: 2026-03-17 by HB Track CDD Pipeline  
Source: SSOT (TRAINING_MODULE_DECISION_IR.yaml)  
Status: **REFERENCE DOCUMENT** (Auto-generated, not a formal ADR)

**For ADR modifications:** Submit PR updating TRAINING_MODULE_DECISION_IR.yaml + formal ADR-*.md

