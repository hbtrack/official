# INVARIANTS_TRAINING.md — Invariantes do Módulo TRAINING

Status: DRAFT  
Versão: v1.0.0  
Tipo de Documento: SSOT Normativo — Invariantes  
Módulo: TRAINING  
Fase: PRD v2.2 (2026-02-20) + AS-IS repo (2026-02-25)  
Autoridade: NORMATIVO_TECNICO  
Última revisão: 2026-02-25  

> Nota importante (IDs): este documento **alinha a numeração `INV-TRAIN-###`** ao conjunto de testes em
> `Hb Track - Backend/tests/training/invariants/*` e às referências em `docs/hbtrack/TRD Traing.md`.

---

## Escopo

Dentro do escopo:
- `training_sessions`, `training_session_exercises`
- `wellness_pre`, `wellness_post`, `wellness_reminders`
- `attendance`
- `training_cycles`, `training_microcycles`
- `session_templates`
- `exercises`, `exercise_tags`, `exercise_favorites`
- `training_analytics_cache`, `team_wellness_rankings`
- `training_alerts`, `training_suggestions`
- Export LGPD / jobs assíncronos (quando ancorados no módulo Training)

Fora do escopo (mas podem ser dependências):
- COMPETITIONS/SCOUT (partidas, eventos, standings)
- Auth/RBAC “core” (salvo invariantes explicitamente ancoradas por contrato OpenAPI)

---

## Fontes de verdade e precedência (normativo)

1. DB constraints/triggers (maior precedência): `Hb Track - Backend/docs/ssot/schema.sql`  
2. Services/Domain rules: `Hb Track - Backend/app/services/*`  
3. OpenAPI (contrato): `Hb Track - Backend/docs/ssot/openapi.json`  
4. Frontend (UX): `Hb Track - Frontend/src/*`  
5. PRD/TRD (referência): `docs/hbtrack/PRD Hb Track.md`, `docs/hbtrack/TRD Traing.md`  

---

## Convenções

- `class` (MP §5): `A` (DB), `B` (Service), `C` (Cálculo/Determinismo), `D` (UX), `E` (Contrato API), `T` (Testes/Gates).
- `status`:
  - `IMPLEMENTADO`: evidência objetiva no schema/código.
  - `PARCIAL`: regra existe mas falta paridade FE/BE ou há divergência menor.
  - `DIVERGENTE_DO_SSOT`: implementação contradiz schema/contrato e precisa correção.
  - `GAP`: exigido pelo PRD/fluxos mas não evidenciado no repo.
  - `DEPRECATED`: mantido apenas para compatibilidade histórica (não usar em novos ARs).

---

## INV-TRAIN-001

```yaml
id: INV-TRAIN-001
class: A
name: focus_total_max_120_pct
rule: >
  A soma dos percentuais de foco (7 campos focus_*_pct) deve ser <= 120.
  Valores individuais, quando presentes, devem estar em 0..100.
tables:
  - training_sessions
  - session_templates
constraints:
  - ck_training_sessions_focus_total_sum
  - chk_session_templates_total_focus
evidence:
  - Hb Track - Backend/docs/ssot/schema.sql (ck_training_sessions_focus_total_sum; chk_session_templates_total_focus)
  - Hb Track - Backend/tests/training/invariants/test_inv_train_001_focus_sum_constraint.py
status: IMPLEMENTADO
rationale: >
  Permite sessões híbridas (ex.: técnico + físico) sem ultrapassar um limite
  que preserve consistência das análises.
```

---

## INV-TRAIN-002

```yaml
id: INV-TRAIN-002
class: B
name: wellness_pre_deadline_2h_before_session
rule: >
  Submissão/edição de wellness_pre é bloqueada quando NOW >= session_at - 2h.
tables:
  - wellness_pre
services:
  - app/services/wellness_pre_service.py (submit_wellness_pre; _check_edit_window)
evidence:
  - Hb Track - Backend/app/services/wellness_pre_service.py (_check_edit_window)
  - Hb Track - Backend/docs/ssot/schema.sql (COMMENT wellness_pre.locked_at)
  - Hb Track - Backend/tests/training/invariants/test_inv_train_002_wellness_pre_deadline.py
status: IMPLEMENTADO
rationale: >
  Garante coleta “pré” com antecedência suficiente para ajuste de carga e evita
  edições tardias que distorcem o histórico.
```

---

## INV-TRAIN-003

```yaml
id: INV-TRAIN-003
class: B
name: wellness_post_edit_window_24h_after_created
rule: >
  Edição de wellness_post é bloqueada quando NOW >= created_at + 24h (limite não-inclusivo).
tables:
  - wellness_post
services:
  - app/services/wellness_post_service.py (_check_edit_window)
evidence:
  - Hb Track - Backend/app/services/wellness_post_service.py (_check_edit_window)
  - Hb Track - Backend/docs/ssot/schema.sql (COMMENT wellness_post.locked_at)
  - Hb Track - Backend/tests/training/invariants/test_inv_train_003_wellness_post_deadline.py
status: IMPLEMENTADO
rationale: >
  Permite correção breve pós-treino, mas impede edições retroativas que degradam
  a confiabilidade da carga interna e analytics.
```

---

## INV-TRAIN-004

```yaml
id: INV-TRAIN-004
class: B
name: session_edit_window_by_role
rule: >
  Janela de edição depende de papel e estado:
  - Autor (treinador): pode editar sessão "scheduled" até 10 min antes de session_at (limite não-inclusivo).
  - Superior (coordenador/dirigente): pode editar "pending_review" até 24h após ended_at (limite não-inclusivo).
tables:
  - training_sessions
services:
  - app/services/training_session_service.py (_validate_edit_permission; AUTHOR_EDIT_WINDOW_MINUTES=10; SUPERIOR_EDIT_WINDOW_HOURS=24)
evidence:
  - Hb Track - Backend/app/services/training_session_service.py (_validate_edit_permission)
  - Hb Track - Backend/tests/training/invariants/test_inv_train_004_edit_window_time.py
status: IMPLEMENTADO
rationale: >
  Reduz alterações próximas do horário do treino e formaliza a revisão operacional por hierarquia.
```

---

## INV-TRAIN-005

```yaml
id: INV-TRAIN-005
class: B
name: session_immutable_after_60_days
rule: >
  Sessões com session_at mais antigas que 60 dias são somente leitura; qualquer tentativa de edição é bloqueada.
tables:
  - training_sessions
services:
  - app/services/training_session_service.py (IMMUTABILITY_DAYS=60; _validate_edit_permission)
evidence:
  - Hb Track - Backend/app/services/training_session_service.py (IMMUTABILITY_DAYS; _validate_edit_permission)
  - Hb Track - Backend/tests/training/invariants/test_inv_train_005_immutability_60_days.py
status: IMPLEMENTADO
rationale: >
  Garante estabilidade histórica e reduz risco de manipulação tardia de métricas.
```

---

## INV-TRAIN-006

```yaml
id: INV-TRAIN-006
class: A+C
name: training_session_status_lifecycle
rule: >
  Status permitido em training_sessions: draft | scheduled | in_progress | pending_review | readonly.
  Workflow alvo: draft → scheduled → in_progress → pending_review → readonly.
table: training_sessions
constraints:
  - check_training_session_status
tasks:
  - app/core/celery_tasks.py (update_training_session_statuses_task)
evidence:
  - Hb Track - Backend/docs/ssot/schema.sql (check_training_session_status)
  - Hb Track - Backend/app/core/celery_tasks.py (update_training_session_statuses_task)
  - Hb Track - Backend/tests/training/invariants/test_inv_train_006_lifecycle_status.py
status: IMPLEMENTADO
rationale: >
  Controla o ciclo operacional do treino e determina permissões de edição e fechamento.
```

---

## INV-TRAIN-007

```yaml
id: INV-TRAIN-007
class: C
name: celery_uses_utc
rule: >
  Operações de datetime em tasks Celery devem usar timezone UTC (timezone.utc) para comparações e timestamps.
services:
  - app/core/celery_tasks.py
evidence:
  - Hb Track - Backend/app/core/celery_tasks.py
  - Hb Track - Backend/tests/training/invariants/test_inv_train_007_celery_utc_timezone.py
status: IMPLEMENTADO
rationale: >
  Evita drift por timezone local e garante determinismo em jobs de transição/cálculo.
```

---

## INV-TRAIN-008

```yaml
id: INV-TRAIN-008
class: A
name: soft_delete_reason_pair
rule: >
  (deleted_at IS NULL AND deleted_reason IS NULL) OR (deleted_at IS NOT NULL AND deleted_reason IS NOT NULL).
tables:
  - training_sessions
  - wellness_pre
  - wellness_post
  - attendance
constraints:
  - ck_training_sessions_deleted_reason
  - ck_wellness_pre_deleted_reason
  - ck_wellness_post_deleted_reason
  - ck_attendance_deleted_reason
evidence:
  - Hb Track - Backend/docs/ssot/schema.sql (ck_*_deleted_reason)
  - Hb Track - Backend/tests/training/invariants/test_inv_train_008_soft_delete_reason_pair.py
status: IMPLEMENTADO
rationale: >
  Soft delete auditável e reversível: não existe “exclusão sem motivo”.
```

---

## INV-TRAIN-009

```yaml
id: INV-TRAIN-009
class: A
name: unique_wellness_pre_per_athlete_session
rule: >
  No máximo 1 wellness_pre ativo por (training_session_id, athlete_id).
  Soft-delete aware (único quando deleted_at IS NULL).
table: wellness_pre
index: ux_wellness_pre_session_athlete
evidence:
  - Hb Track - Backend/docs/ssot/schema.sql (CREATE UNIQUE INDEX ux_wellness_pre_session_athlete ...)
  - Hb Track - Backend/tests/training/invariants/test_inv_train_009_wellness_pre_uniqueness.py
status: IMPLEMENTADO
rationale: >
  Impede duplicidade de respostas pré-treino por sessão, protegendo analytics e alertas.
```

---

## INV-TRAIN-010

```yaml
id: INV-TRAIN-010
class: A
name: unique_wellness_post_per_athlete_session
rule: >
  No máximo 1 wellness_post ativo por (training_session_id, athlete_id).
  Soft-delete aware (único quando deleted_at IS NULL).
table: wellness_post
index: ux_wellness_post_session_athlete
evidence:
  - Hb Track - Backend/docs/ssot/schema.sql (CREATE UNIQUE INDEX ux_wellness_post_session_athlete ...)
  - Hb Track - Backend/tests/training/invariants/test_inv_train_010_wellness_post_uniqueness.py
status: IMPLEMENTADO
rationale: >
  Evita duplicidade de RPE/carga interna por sessão.
```

---

## INV-TRAIN-011

```yaml
id: INV-TRAIN-011
class: B
name: deviation_rules_and_min_justification
rule: >
  - Desvio significativo: >= 20 pts em qualquer foco (absoluto).
  - Desvio agregado significativo: >= 30% (agregado).
  - Justificativa mínima para desvios: >= 50 caracteres.
table: training_sessions
services:
  - app/services/training_session_service.py (MIN_JUSTIFICATION_LENGTH=50; lógica de desvio)
evidence:
  - Hb Track - Backend/app/services/training_session_service.py (MIN_JUSTIFICATION_LENGTH; significant deviation)
  - Hb Track - Backend/tests/training/invariants/test_inv_train_011_deviation_rules.py
status: IMPLEMENTADO
rationale: >
  Desvios precisam ser rastreáveis e explicáveis para auditoria e para calibrar planejamento.
```

---

## INV-TRAIN-012

```yaml
id: INV-TRAIN-012
class: B
name: export_rate_limits_daily
rule: >
  Rate limiting diário:
  - Analytics PDF: máximo 5/dia por usuário.
  - Athlete export: máximo 3/dia por usuário.
services:
  - app/services/export_service.py (ANALYTICS_PDF_DAILY_LIMIT=5; ATHLETE_DATA_DAILY_LIMIT=3)
evidence:
  - Hb Track - Backend/app/services/export_service.py
  - Hb Track - Backend/tests/training/invariants/test_inv_train_012_export_rate_limit.py
status: IMPLEMENTADO
rationale: >
  Protege a plataforma contra abuso/custos de geração e reduz risco operacional.
```

---

## INV-TRAIN-013

```yaml
id: INV-TRAIN-013
class: B
name: gamification_badge_eligibility
rule: >
  Badges de wellness:
  - monthly: response_rate >= 90% no mês.
  - streak: 3 meses consecutivos cumprindo critério.
services:
  - app/services/wellness_gamification_service.py
evidence:
  - Hb Track - Backend/app/services/wellness_gamification_service.py
  - Hb Track - Backend/tests/training/invariants/test_inv_train_013_gamification_badge_rules.py
status: PARCIAL
note: >
  Backend evidencia regras; front-end de notificações/badges pode estar incompleto conforme PRD RF-013.
rationale: >
  Incentiva consistência de resposta wellness e melhora qualidade de dados.
```

---

## INV-TRAIN-014

```yaml
id: INV-TRAIN-014
class: B
name: overload_alert_threshold_multiplier
rule: >
  Alertas de sobrecarga semanal usam multiplicador por equipe:
  threshold_critical = threshold_base * teams.alert_threshold_multiplier.
  (Referência de produto: 1.5 juvenis, 2.0 padrão, 2.5 adultos.)
tables:
  - training_alerts
  - teams
services:
  - app/services/training_alerts_service.py (check_weekly_overload)
evidence:
  - Hb Track - Backend/docs/ssot/schema.sql (teams.alert_threshold_multiplier DEFAULT 2.0; COMMENT)
  - Hb Track - Backend/app/services/training_alerts_service.py
  - Hb Track - Backend/tests/training/invariants/test_inv_train_014_overload_alert_threshold.py
status: DIVERGENTE_DO_SSOT
note: >
  Há divergência/risco: vários endpoints/serviços de alerts usam team_id tipado como int,
  mas o SSOT do schema define UUID. Ver AR backlog (classe E/B) para correção.
rationale: >
  Threshold dinâmico é essencial para evitar falsos positivos em diferentes categorias/idades.
```

---

## INV-TRAIN-015

```yaml
id: INV-TRAIN-015
class: E+C
name: training_analytics_endpoints_exposed
rule: >
  O módulo Training Analytics expõe endpoints de summary/weekly-load/deviation-analysis/prevention-effectiveness
  via router + services, com threshold dinâmico baseado em team.alert_threshold_multiplier.
api:
  - /api/v1/analytics/team/{team_id}/summary
  - /api/v1/analytics/team/{team_id}/weekly-load
  - /api/v1/analytics/team/{team_id}/deviation-analysis
  - /api/v1/analytics/team/{team_id}/prevention-effectiveness
services:
  - app/services/training_analytics_service.py
  - app/services/prevention_effectiveness_service.py
evidence:
  - Hb Track - Backend/app/api/v1/routers/training_analytics.py
  - Hb Track - Backend/tests/training/invariants/test_inv_train_015_training_analytics_exposure.py
status: IMPLEMENTADO
rationale: >
  Analytics precisa ser acessível por staff para tomada de decisão e prevenção.
```

---

## INV-TRAIN-016

```yaml
id: INV-TRAIN-016
class: E
name: attendance_auth_and_scoped_route_not_exposed
rule: >
  Endpoints de attendance exigem autenticação; rota scoped alternativa (teams/{team_id}/trainings/{id}/attendance) não é exposta no agregador.
api:
  - /api/v1/training_sessions/{training_session_id}/attendance (auth required)
  - /api/v1/teams/{team_id}/trainings/{id}/attendance (MUST NOT exist / 404)
evidence:
  - Hb Track - Backend/app/api/v1/routers/attendance.py
  - Hb Track - Backend/app/api/v1/api.py (inclui attendance.router; não inclui attendance_scoped)
  - Hb Track - Backend/tests/training/invariants/test_inv_train_016_attendance_auth_scoped.py
status: IMPLEMENTADO
rationale: >
  Presença é dado sensível operacional; não deve haver rota “paralela” exposta sem governança.
```

---

## INV-TRAIN-018

```yaml
id: INV-TRAIN-018
class: B
name: microcycle_session_default_status
rule: >
  Ao criar training_session com microcycle_id:
  - Se payload estiver “completo” (ex.: duration_planned_minutes, location, main_objective), status inicial = scheduled.
  - Caso contrário, status inicial = draft.
table: training_sessions
services:
  - app/services/training_session_service.py (create)
evidence:
  - Hb Track - Backend/app/services/training_session_service.py (create)
  - Hb Track - Backend/tests/training/invariants/test_inv_train_018_training_session_microcycle_status.py
  - Hb Track - Backend/tests/training/invariants/test_inv_train_018_training_session_microcycle_status_route.py
status: IMPLEMENTADO
rationale: >
  Sessões originadas do planejamento podem nascer agendadas quando já têm dados mínimos.
```

---

## INV-TRAIN-019

```yaml
id: INV-TRAIN-019
class: B
name: audit_logs_for_training_session_actions
rule: >
  Ações create/update/publish/close em training_sessions registram audit_logs (append-only).
tables:
  - audit_logs
  - training_sessions
services:
  - app/services/training_session_service.py
evidence:
  - Hb Track - Backend/app/services/training_session_service.py (ações e logging)
  - Hb Track - Backend/tests/training/invariants/test_inv_train_019_training_session_audit_logs.py
status: IMPLEMENTADO
rationale: >
  Treinos impactam métricas, saúde e decisões; auditoria é requisito de compliance/operacional.
```

---

## INV-TRAIN-020

```yaml
id: INV-TRAIN-020
class: A
name: analytics_cache_invalidation_trigger
rule: >
  Trigger tr_invalidate_analytics_cache invalida training_analytics_cache quando training_sessions é inserido/alterado/removido.
table: training_sessions
trigger: tr_invalidate_analytics_cache
function: fn_invalidate_analytics_cache
evidence:
  - Hb Track - Backend/docs/ssot/schema.sql (tr_invalidate_analytics_cache; fn_invalidate_analytics_cache)
  - Hb Track - Backend/tests/training/invariants/test_inv_train_020_cache_invalidation_trigger.py
status: IMPLEMENTADO
rationale: >
  Evita analytics “stale” e mantém consistência de métricas weekly/monthly.
```

---

## INV-TRAIN-021

```yaml
id: INV-TRAIN-021
class: A
name: internal_load_trigger
rule: >
  Trigger tr_calculate_internal_load calcula wellness_post.internal_load automaticamente (minutes_effective × session_rpe).
table: wellness_post
trigger: tr_calculate_internal_load
function: fn_calculate_internal_load
evidence:
  - Hb Track - Backend/docs/ssot/schema.sql (tr_calculate_internal_load; fn_calculate_internal_load)
  - Hb Track - Backend/tests/training/invariants/test_inv_train_021_internal_load_trigger.py
status: IMPLEMENTADO
rationale: >
  Padroniza cálculo de carga interna e evita divergência entre clientes.
```

---

## INV-TRAIN-022

```yaml
id: INV-TRAIN-022
class: C
name: wellness_post_invalidates_training_analytics_cache
rule: >
  Ao submeter wellness_post, o sistema deve marcar caches weekly e monthly relacionados como dirty (cache_dirty=true; calculated_at=NULL).
tables:
  - training_analytics_cache
services:
  - app/services/wellness_post_service.py (_invalidate_training_analytics_cache)
evidence:
  - Hb Track - Backend/app/services/wellness_post_service.py (_invalidate_training_analytics_cache)
  - Hb Track - Backend/tests/training/invariants/test_inv_train_022_wellness_post_cache_invalidation.py
status: IMPLEMENTADO
rationale: >
  Wellness pós altera carga/RPE e precisa refletir rapidamente nos dashboards.
```

---

## INV-TRAIN-023

```yaml
id: INV-TRAIN-023
class: C+B
name: wellness_post_triggers_overload_alert_check
rule: >
  Ao submeter wellness_post, deve ser possível disparar verificação de sobrecarga semanal para a semana da sessão (week_start) usando multiplicador da equipe.
services:
  - app/services/wellness_post_service.py (_trigger_overload_alert_on_wellness_post)
  - app/services/training_alerts_service.py (check_weekly_overload)
evidence:
  - Hb Track - Backend/app/services/wellness_post_service.py (_trigger_overload_alert_on_wellness_post)
  - Hb Track - Backend/tests/training/invariants/test_inv_train_023_wellness_post_overload_alert_trigger.py
status: DIVERGENTE_DO_SSOT
note: >
  Mesmo com evidência de chamada, a cadeia alerts/suggestions tem risco de quebra por tipos (team_id UUID vs int) e por endpoints.
rationale: >
  Integra wellness/carga com prevenção de overtraining de forma automática.
```

---

## INV-TRAIN-024

```yaml
id: INV-TRAIN-024
class: B+D
name: websocket_broadcast_for_alerts_and_badges
rule: >
  Alertas críticos e badges relevantes geram NotificationService + broadcast via WebSocket (para usuários-alvo).
services:
  - app/services/training_alerts_service.py (broadcast em alertas)
  - app/services/wellness_gamification_service.py (broadcast em badges)
evidence:
  - Hb Track - Backend/app/services/training_alerts_service.py
  - Hb Track - Backend/app/services/wellness_gamification_service.py
  - Hb Track - Backend/tests/training/invariants/test_inv_train_024_websocket_broadcast.py
status: PARCIAL
note: >
  Backend evidencia integração; FE de notificações pode não estar materializado (PRD RF-013).
rationale: >
  Notificações reduzem latência operacional (coordenação e prevenção).
```

---

## INV-TRAIN-025

```yaml
id: INV-TRAIN-025
class: E+C
name: lgpd_export_async_jobs
rule: >
  Exports LGPD/relatórios PDF devem ser gerados de forma assíncrona via job (Celery),
  com cleanup de jobs expirados e auditabilidade.
tables:
  - export_jobs
services:
  - app/services/export_service.py
tasks:
  - app/core/celery_tasks.py (generate_analytics_pdf_task; cleanup_expired_export_jobs_task)
evidence:
  - Hb Track - Backend/app/core/celery_tasks.py
  - Hb Track - Backend/app/services/export_service.py
  - Hb Track - Backend/tests/training/invariants/test_inv_train_025_export_lgpd_endpoints.py
status: PARCIAL
rationale: >
  Evita bloquear UI, garante rastreabilidade e reduz risco de reprocessamentos.
```

---

## INV-TRAIN-026

```yaml
id: INV-TRAIN-026
class: B
name: lgpd_access_logging
rule: >
  Quando staff acessa dados de atletas (ex.: wellness) fora do “self-only”, deve registrar data_access_logs/audit logs conforme política LGPD.
services:
  - app/services/wellness_pre_service.py (data access logging)
evidence:
  - Hb Track - Backend/app/services/wellness_pre_service.py
  - Hb Track - Backend/tests/training/invariants/test_inv_train_026_lgpd_access_logging.py
status: IMPLEMENTADO
rationale: >
  Compliance LGPD: rastrear acesso a dados pessoais/saúde.
```

---

## INV-TRAIN-027

```yaml
id: INV-TRAIN-027
class: C
name: refresh_training_rankings_task
rule: >
  A task refresh_training_rankings_task recalcula caches dirty e marca cache_dirty=false, atualizando calculated_at em UTC.
tables:
  - training_analytics_cache
tasks:
  - app/core/celery_tasks.py (refresh_training_rankings_task)
evidence:
  - Hb Track - Backend/app/core/celery_tasks.py (refresh_training_rankings_task)
  - Hb Track - Backend/tests/training/invariants/test_inv_train_027_refresh_training_rankings_task.py
status: IMPLEMENTADO
rationale: >
  Mantém analytics consistentes sem depender apenas de eventos em tempo real.
```

---

## INV-TRAIN-028

```yaml
id: INV-TRAIN-028
class: T
name: deprecated_duplicate_focus_rule
rule: >
  DEPRECATED. ID histórico redundante para a mesma regra de INV-TRAIN-001.
superseded_by: INV-TRAIN-001
evidence:
  - Hb Track - Backend/tests/training/invariants/test_inv_train_028_focus_sum_constraint.py
status: DEPRECATED
rationale: >
  Mantido para compatibilidade com histórico de testes; não criar novos ARs referenciando INV-TRAIN-028.
```

---

## INV-TRAIN-029

```yaml
id: INV-TRAIN-029
class: B
name: editing_rules_by_session_status
rule: >
  Edição de training_sessions é controlada por estado:
  - readonly: bloqueia completamente
  - in_progress: bloqueia completamente
  - pending_review: permite apenas campos de revisão
  - scheduled: permite apenas subconjunto (notes, focus_*, intensity_target, etc.)
  - draft: edição livre
table: training_sessions
services:
  - app/services/training_session_service.py (_validate_edit_permission)
evidence:
  - Hb Track - Backend/app/services/training_session_service.py (_validate_edit_permission)
  - Hb Track - Backend/tests/training/invariants/test_inv_train_029_edit_blocked_after_in_progress.py
status: IMPLEMENTADO
rationale: >
  Evita inconsistência operacional durante execução e consolida revisão pós-treino.
```

---

## INV-TRAIN-030

```yaml
id: INV-TRAIN-030
class: A
name: attendance_correction_requires_audit_fields
rule: >
  Quando attendance.source = 'correction', os campos correction_by_user_id e correction_at são obrigatórios.
table: attendance
constraint: ck_attendance_correction_fields
evidence:
  - Hb Track - Backend/docs/ssot/schema.sql (ck_attendance_correction_fields)
  - Hb Track - Backend/tests/training/invariants/test_inv_train_030_attendance_correction_fields.py
status: IMPLEMENTADO
rationale: >
  Correções administrativas precisam de trilha de auditoria explícita.
```

---

## INV-TRAIN-031

```yaml
id: INV-TRAIN-031
class: A
name: derive_phase_focus_from_percentages
rule: >
  phase_focus_* é derivado automaticamente quando percentuais correspondentes >= 5%,
  via trigger BEFORE + constraints de consistência.
table: training_sessions
trigger: tr_derive_phase_focus
function: fn_derive_phase_focus
constraints:
  - ck_phase_focus_attack_consistency
  - ck_phase_focus_defense_consistency
  - ck_phase_focus_transition_offense_consistency
  - ck_phase_focus_transition_defense_consistency
evidence:
  - Hb Track - Backend/docs/ssot/schema.sql (fn_derive_phase_focus; tr_derive_phase_focus; ck_phase_focus_*_consistency)
  - Hb Track - Backend/tests/training/invariants/test_inv_train_031_derive_phase_focus.py
status: IMPLEMENTADO
rationale: >
  Normaliza flags por foco sem depender do cliente e garante consistência com percentuais.
```

---

## INV-TRAIN-032

```yaml
id: INV-TRAIN-032
class: A
name: wellness_post_rpe_range
rule: session_rpe deve estar entre 0 e 10 (inclusive).
table: wellness_post
constraint: ck_wellness_post_rpe
evidence:
  - Hb Track - Backend/docs/ssot/schema.sql (ck_wellness_post_rpe)
  - Hb Track - Backend/tests/training/invariants/test_inv_train_032_wellness_post_rpe.py
  - Hb Track - Backend/tests/training/invariants/test_inv_train_032_wellness_post_rpe_runtime.py
status: IMPLEMENTADO
rationale: >
  RPE fora do domínio invalida cálculos de carga interna.
```

---

## INV-TRAIN-033

```yaml
id: INV-TRAIN-033
class: A
name: wellness_pre_sleep_hours_range
rule: sleep_hours deve estar entre 0 e 24 (inclusive).
table: wellness_pre
constraint: ck_wellness_pre_sleep_hours
evidence:
  - Hb Track - Backend/docs/ssot/schema.sql (ck_wellness_pre_sleep_hours)
  - Hb Track - Backend/tests/training/invariants/test_inv_train_033_wellness_pre_sleep_hours.py
  - Hb Track - Backend/tests/training/invariants/test_inv_train_033_wellness_pre_sleep_hours_runtime.py
status: IMPLEMENTADO
rationale: >
  Evita valores inválidos e melhora qualidade do dado de sono.
```

---

## INV-TRAIN-034

```yaml
id: INV-TRAIN-034
class: A
name: wellness_pre_sleep_quality_range
rule: sleep_quality deve estar entre 1 e 5 (inclusive).
table: wellness_pre
constraint: ck_wellness_pre_sleep_quality
evidence:
  - Hb Track - Backend/docs/ssot/schema.sql (ck_wellness_pre_sleep_quality)
  - Hb Track - Backend/tests/training/invariants/test_inv_train_034_wellness_pre_sleep_quality.py
  - Hb Track - Backend/tests/training/invariants/test_inv_train_034_wellness_pre_sleep_quality_runtime.py
status: IMPLEMENTADO
rationale: >
  Mantém consistência com UI (escala 1–5) e com cálculos derivados (readiness).
```

---

## INV-TRAIN-035

```yaml
id: INV-TRAIN-035
class: A
name: session_template_unique_name_per_org
rule: >
  Nome do template é único por organização.
table: session_templates
constraint: uq_session_templates_org_name
evidence:
  - Hb Track - Backend/docs/ssot/schema.sql (uq_session_templates_org_name)
  - Hb Track - Backend/tests/training/invariants/test_inv_train_035_session_templates_unique_name.py
  - Hb Track - Backend/tests/training/invariants/test_inv_train_035_session_templates_unique_name_runtime.py
status: IMPLEMENTADO
rationale: >
  Evita ambiguidade na seleção e reutilização de templates.
```

---

## INV-TRAIN-036

```yaml
id: INV-TRAIN-036
class: A
name: wellness_rankings_unique_team_month
rule: Ranking mensal é único por (team_id, month_reference).
table: team_wellness_rankings
constraint: uq_team_wellness_rankings_team_month
evidence:
  - Hb Track - Backend/docs/ssot/schema.sql (uq_team_wellness_rankings_team_month)
  - Hb Track - Backend/tests/training/invariants/test_inv_train_036_wellness_rankings_unique.py
  - Hb Track - Backend/tests/training/invariants/test_inv_train_036_wellness_rankings_unique_runtime.py
status: IMPLEMENTADO
rationale: >
  Evita duplicidade de ranking e garante idempotência de recálculos mensais.
```

---

## INV-TRAIN-037

```yaml
id: INV-TRAIN-037
class: A
name: cycle_dates_valid
rule: start_date < end_date (estrito).
table: training_cycles
constraint: check_cycle_dates
evidence:
  - Hb Track - Backend/docs/ssot/schema.sql (check_cycle_dates)
  - Hb Track - Backend/tests/training/invariants/test_inv_train_037_cycle_dates.py
  - Hb Track - Backend/tests/training/invariants/test_inv_train_037_cycle_dates_runtime.py
status: IMPLEMENTADO
rationale: >
  Planejamento inválido (datas invertidas) quebra microciclos e relatórios.
```

---

## INV-TRAIN-040

```yaml
id: INV-TRAIN-040
class: E
name: openapi_contract_health_public
rule: >
  O OpenAPI deve declarar GET /api/v1/health (operationId health_api_v1_health_get), público (sem security) e com response 200.
api:
  operationId: health_api_v1_health_get
  method: GET
  path: /api/v1/health
evidence:
  - Hb Track - Backend/docs/ssot/openapi.json
  - Hb Track - Backend/tests/training/invariants/test_inv_train_040_health_contract.py
status: PARCIAL
note: >
  O teste atual aponta para docs/_generated/openapi.json; SSOT atual do repo está em Hb Track - Backend/docs/ssot/openapi.json.
rationale: >
  Gate de contrato: endpoint health é âncora de observabilidade e smoke tests.
```

---

## INV-TRAIN-041

```yaml
id: INV-TRAIN-041
class: E
name: openapi_contract_teams_auth
rule: >
  O OpenAPI deve declarar GET /api/v1/teams (operationId get_teams_api_v1_teams_get) com security HTTPBearer (ou equivalente) e responses 200/422.
api:
  operationId: get_teams_api_v1_teams_get
  method: GET
  path: /api/v1/teams
evidence:
  - Hb Track - Backend/docs/ssot/openapi.json
  - Hb Track - Backend/tests/training/invariants/test_inv_train_041_teams_contract.py
status: PARCIAL
note: >
  O teste atual aponta para docs/_generated/openapi.json; SSOT atual do repo está em Hb Track - Backend/docs/ssot/openapi.json.
rationale: >
  Gate de contrato: Training depende de teams; contrato precisa ser estável e autenticado.
```

---

## INV-TRAIN-043

```yaml
id: INV-TRAIN-043
class: A
name: microcycle_dates_valid
rule: week_start < week_end (estrito).
table: training_microcycles
constraint: check_microcycle_dates
evidence:
  - Hb Track - Backend/docs/ssot/schema.sql (check_microcycle_dates)
  - Hb Track - Backend/tests/training/invariants/test_inv_train_043_microcycle_dates_check.py
status: IMPLEMENTADO
rationale: >
  Microciclo deve representar um intervalo temporal válido para agregações semanais.
```

---

## INV-TRAIN-044

```yaml
id: INV-TRAIN-044
class: A
name: analytics_cache_unique_lookup
rule: >
  training_analytics_cache é único por (team_id, microcycle_id, month, granularity).
table: training_analytics_cache
constraint: uq_training_analytics_cache_lookup
evidence:
  - Hb Track - Backend/docs/ssot/schema.sql (uq_training_analytics_cache_lookup)
  - Hb Track - Backend/tests/training/invariants/test_inv_train_044_analytics_cache_unique.py
status: IMPLEMENTADO
rationale: >
  Evita duplicidade de cache e garante lookup determinístico para dashboards.
```

---

## INV-TRAIN-045

```yaml
id: INV-TRAIN-045
class: A
name: session_exercises_order_unique
rule: >
  order_index é único por sessão (session_id, order_index) quando deleted_at IS NULL.
table: training_session_exercises
index: idx_session_exercises_session_order_unique
evidence:
  - Hb Track - Backend/docs/ssot/schema.sql (idx_session_exercises_session_order_unique)
  - Hb Track - Backend/tests/training/invariants/test_inv_train_045_session_exercises_order_unique.py
status: IMPLEMENTADO
rationale: >
  Drag-and-drop e ordenação determinística dependem de order_index sem colisões.
```

---

## INV-TRAIN-046

```yaml
id: INV-TRAIN-046
class: A
name: wellness_response_trigger_updates_reminders
rule: >
  Ao inserir wellness_pre/wellness_post, o sistema atualiza wellness_reminders.responded_at quando houver reminder pendente.
tables:
  - wellness_pre
  - wellness_post
  - wellness_reminders
triggers:
  - tr_update_wellness_pre_response
  - tr_update_wellness_post_response
function: fn_update_wellness_response_timestamp
evidence:
  - Hb Track - Backend/docs/ssot/schema.sql (fn_update_wellness_response_timestamp; triggers tr_update_wellness_*_response)
  - Hb Track - Backend/tests/training/invariants/test_inv_train_046_wellness_post_response_trigger.py
status: IMPLEMENTADO
rationale: >
  Permite métricas de lembretes/resposta e auditoria de engajamento wellness.
```
