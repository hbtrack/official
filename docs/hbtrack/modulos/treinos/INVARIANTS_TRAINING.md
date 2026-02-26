# INVARIANTS_TRAINING.md — Invariantes do Módulo TRAINING

Status: DRAFT  
Versão: v1.3.0  
Tipo de Documento: SSOT Normativo — Invariantes  
Módulo: TRAINING  
Fase: PRD v2.2 (2026-02-20) + AS-IS repo (2026-02-25) + DEC-TRAIN-EXB-* (2026-02-25) + FASE_3 (2026-02-27)  
Autoridade: NORMATIVO_TECNICO  
Última revisão: 2026-02-27  

> Changelog v1.3.0 (2026-02-27):  
> - Adicionadas INV-TRAIN-054..081 (28 invariantes — FASE_3: Ciclos/Sessão, Banco Exercícios, Presença/Pendências, Atleta/Pós-treino, IA/Educativo, Wellness Obrigatório, Gamificação, IA Treinador)  
> - INV-TRAIN-EXB-ACL-001 AMENDADA: default `org_wide` → `restricted` (decisão normativa do humano: "ORG default = restricted, só criador vê")  
> - INV-TRAIN-060 sobrepõe EXB-ACL-001 default; EXB-ACL-001 atualizada para consistência  
> - Nota: INV-TRAIN-058 coexiste com INV-TRAIN-004/029 (princípio geral; 004/029 são refinamentos por-papel/por-status)  

> Changelog v1.2.0 (2026-02-26):  
> - Adicionada Authority Matrix  
> - Adicionada convenção de Classification Tags (`[NORMATIVO]`/`[DESCRITIVO-AS-IS]`/`[HIPOTESE]`/`[GAP]`)  
> - Adicionado `decision_trace:` formal em INV-TRAIN-047..053, EXB-ACL-001..007  

> Changelog v1.1.0 (2026-02-25):  
> - Adicionadas INV-TRAIN-047..053 (Banco de Exercícios — base)  
> - Adicionadas INV-TRAIN-EXB-ACL-001..007 (ACL/Visibilidade ORG)  
> - Decisões aprovadas incorporadas: DEC-TRAIN-EXB-001, DEC-TRAIN-EXB-001B, DEC-TRAIN-EXB-002, DEC-TRAIN-EXB-RBAC-001  

> Nota importante (IDs): este documento **alinha a numeração `INV-TRAIN-###`** ao conjunto de testes em
> `Hb Track - Backend/tests/training/invariants/*` e às referências em `docs/hbtrack/TRD Traing.md`.

---

## Authority Matrix

| Aspecto | Regra |
|---|---|
| Fonte de verdade | DB constraints/triggers (`schema.sql`) + Domain services + Decisões humanas (DEC-*) |
| Escrita normativa | **Arquiteto** — criar, alterar, remover invariantes |
| Escrita operacional | N/A (invariantes não têm estado operacional) |
| Somente leitura | Executor, Testador, Designer UX |
| Proposta de alteração | Qualquer papel → via GAP ou DEC ao Arquiteto |
| Precedência em conflito | DB constraint > Service rule > DEC > PRD |

---

## Convenção de Tags (Classification)

Cada invariante (INV-*) neste documento é uma **unidade de afirmação testável** e recebe classificação:

| Tag | Significado |
|---|---|
| `[NORMATIVO]` | Regra que DEVE ser respeitada. Fonte: DB, Service, DEC ou PRD explícito. |
| `[DESCRITIVO-AS-IS]` | Observação do estado atual (evidenciado no repo). Pode mudar. |
| `[HIPOTESE]` | Expectativa derivada do PRD/fluxos, mas não evidenciada no repo. |
| `[GAP]` | Lacuna identificada entre o normativo e o estado atual. |

**Regra de ouro:** Se alguém puder perguntar "isso é normativo ou só observação?", o trecho precisa de tag própria.

**Aplicação neste documento:** Todas as invariantes são `[NORMATIVO]` por definição (expressam regras obrigatórias). O campo `status` indica o estado AS-IS:
- `status: IMPLEMENTADO` → regra normativa + implementação evidenciada (normativo + AS-IS).
- `status: GAP` → regra normativa sem implementação evidenciada (normativo + gap).
- `status: DEPRECATED` → mantida para referência, não normativa para novos ARs.

---

## Escopo

Dentro do escopo:
- `training_sessions`, `training_session_exercises`
- `wellness_pre`, `wellness_post`, `wellness_reminders`
- `attendance`
- `training_cycles`, `training_microcycles`
- `session_templates`
- `exercises`, `exercise_tags`, `exercise_favorites`, `exercise_media`, `exercise_acl`
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

---

## INV-TRAIN-047

```yaml
id: INV-TRAIN-047
class: A
name: exercise_scope_valid
rule: >
  Todo exercício DEVE pertencer a um escopo válido: SYSTEM ou ORG.
  Exercícios SYSTEM são instalados pela plataforma.
  Exercícios ORG são criados por usuários da organização.
table: exercises
constraints:
  - ck_exercises_scope (enum: SYSTEM, ORG)
evidence:
  - GAP: constraint não evidenciada no schema atual; a ser materializada por AR.
status: GAP
decision_ref: DEC-TRAIN-EXB-001
decision_trace: [DEC-TRAIN-EXB-001]
rationale: >
  Separar exercícios do sistema dos exercícios personalizados pela organização
  permite catálogo curado + customização sem comprometer integridade.
```

---

## INV-TRAIN-048

```yaml
id: INV-TRAIN-048
class: B
name: system_exercise_immutable_for_org_users
rule: >
  Usuários da organização NÃO PODEM editar ou excluir exercícios instalados (scope = SYSTEM).
  Qualquer tentativa de PATCH/DELETE por usuário não-plataforma DEVE retornar 403.
table: exercises
services:
  - app/services/exercise_service.py (guard de escopo)
evidence:
  - GAP: guard de escopo não evidenciado no service atual.
status: GAP
decision_ref: DEC-TRAIN-EXB-001
decision_trace: [DEC-TRAIN-EXB-001]
rationale: >
  Protege o catálogo base da plataforma contra alterações acidentais ou indevidas.
```

---

## INV-TRAIN-049

```yaml
id: INV-TRAIN-049
class: A
name: org_exercise_single_organization
rule: >
  Todo exercício criado pela organização (scope = ORG) DEVE estar vinculado
  a exatamente uma organização válida (organization_id NOT NULL, FK ativa).
table: exercises
constraints:
  - fk_exercises_organization_id (quando scope = ORG)
  - ck_exercises_org_requires_org_id
evidence:
  - GAP: constraint condicional não evidenciada no schema atual.
status: GAP
decision_ref: DEC-TRAIN-EXB-001
decision_trace: [DEC-TRAIN-EXB-001]
rationale: >
  Impede exercícios ORG "órfãos" e garante isolamento multi-tenant.
```

---

## INV-TRAIN-050

```yaml
id: INV-TRAIN-050
class: A
name: favorite_unique_per_user_exercise
rule: >
  Um usuário só PODE favoritar o mesmo exercício uma vez.
  Constraint de unicidade em (user_id, exercise_id).
table: exercise_favorites
constraints:
  - uq_exercise_favorites_user_exercise
evidence:
  - Hb Track - Backend/docs/ssot/schema.sql (verificar: ux_exercise_favorites_*)
  - GAP: verificar se constraint existe; se não, materializar via AR.
status: GAP
decision_ref: DEC-TRAIN-EXB-001
decision_trace: [DEC-TRAIN-EXB-001]
rationale: >
  Favoritos duplicados poluem a lista e geram inconsistência de contagem.
```

---

## INV-TRAIN-051

```yaml
id: INV-TRAIN-051
class: B
name: catalog_visibility_respects_organization
rule: >
  Usuário só PODE ver exercícios SYSTEM + exercícios ORG da própria organização,
  respeitando visibility_mode e ACL quando aplicável.
  Backend é a autoridade de enforcement (não apenas frontend).
table: exercises
services:
  - app/services/exercise_service.py (filtro de catálogo)
evidence:
  - GAP: filtro de visibilidade por org + visibility_mode não evidenciado no service.
status: GAP
decision_ref: DEC-TRAIN-EXB-001, DEC-TRAIN-EXB-001B
decision_trace: [DEC-TRAIN-EXB-001, DEC-TRAIN-EXB-001B]
rationale: >
  Multi-tenant + ACL: impede vazamento cross-org e respeita restrições de compartilhamento.
```

---

## INV-TRAIN-052

```yaml
id: INV-TRAIN-052
class: A
name: exercise_media_type_reference_valid
rule: >
  Todo item de mídia vinculado ao exercício DEVE informar tipo válido
  (ex.: image, video, youtube_link, external_link) e referência válida (URL ou asset_id).
table: exercise_media
constraints:
  - ck_exercise_media_type
  - ck_exercise_media_reference_not_empty
evidence:
  - GAP: tabela exercise_media e constraints não evidenciadas no schema atual.
status: GAP
decision_ref: DEC-TRAIN-EXB-001
decision_trace: [DEC-TRAIN-EXB-001]
rationale: >
  Evita mídias "vazias" e garante renderização confiável no frontend.
```

---

## INV-TRAIN-053

```yaml
id: INV-TRAIN-053
class: B
name: soft_delete_exercise_no_break_historic_session
rule: >
  Exercício referenciado por sessão histórica NÃO PODE ser removido de forma
  a invalidar leitura da sessão (soft-delete preserva referência).
  Se houver hard-delete, deve haver regra de tombstone ou fallback.
tables:
  - exercises
  - training_session_exercises
services:
  - app/services/exercise_service.py (guard de delete)
evidence:
  - GAP: guard de preservação histórica não evidenciado no service.
status: GAP
decision_ref: DEC-TRAIN-EXB-001
decision_trace: [DEC-TRAIN-EXB-001]
rationale: >
  Sessões históricas são artefatos de auditoria; remover exercícios referenciados
  degrada dados e compliance.
```

---

## INV-TRAIN-EXB-ACL-001

```yaml
id: INV-TRAIN-EXB-ACL-001
class: A
name: exercise_org_visibility_mode_valid
rule: >
  Todo exercício ORG DEVE possuir visibility_mode válido: org_wide ou restricted.
  Default para novos exercícios ORG: **restricted** (apenas criador vê; compartilhar exige ação explícita).
  AMENDADA v1.3.0: default alterado de org_wide para restricted por decisão normativa do humano
  e consistência com INV-TRAIN-060.
table: exercises
constraints:
  - ck_exercises_visibility_mode (enum: org_wide, restricted; aplicável quando scope = ORG)
evidence:
  - GAP: campo visibility_mode e constraint não evidenciados no schema atual.
status: GAP
decision_ref: DEC-TRAIN-EXB-001B, INV-TRAIN-060
decision_trace: [DEC-TRAIN-EXB-001B, INV-TRAIN-060]
rationale: >
  Controla quem visualiza exercícios ORG e abre caminho para ACL granular.
  Default restricted segue princípio de menor privilégio: apenas criador vê por padrão.
```

---

## INV-TRAIN-EXB-ACL-002

```yaml
id: INV-TRAIN-EXB-ACL-002
class: B
name: acl_only_for_org_restricted
rule: >
  ACL por usuário só PODE existir para exercício ORG com visibility_mode = restricted.
  Tentativa de adicionar ACL em exercício com visibility_mode = org_wide DEVE ser bloqueada (400/422).
table: exercise_acl
services:
  - app/services/exercise_acl_service.py (guard)
evidence:
  - GAP: tabela exercise_acl e guard de consistência não evidenciados.
status: GAP
decision_ref: DEC-TRAIN-EXB-001B
decision_trace: [DEC-TRAIN-EXB-001B]
rationale: >
  ACL em exercício org_wide é redundante e gera confusão operacional.
```

---

## INV-TRAIN-EXB-ACL-003

```yaml
id: INV-TRAIN-EXB-ACL-003
class: B
name: acl_anti_cross_org
rule: >
  Usuário incluído na ACL de um exercício DEVE pertencer à mesma organização do exercício.
  Backend DEVE validar membership da organização antes de inserir na ACL.
table: exercise_acl
services:
  - app/services/exercise_acl_service.py (validação cross-org)
evidence:
  - GAP: validação não evidenciada.
status: GAP
decision_ref: DEC-TRAIN-EXB-001B
decision_trace: [DEC-TRAIN-EXB-001B]
rationale: >
  Previne vazamento cross-org de exercícios proprietários.
```

---

## INV-TRAIN-EXB-ACL-004

```yaml
id: INV-TRAIN-EXB-ACL-004
class: B+D
name: acl_authority_creator_only
rule: >
  Apenas o treinador criador do exercício ORG PODE alterar visibility_mode e gerenciar ACL.
  Outro treinador da mesma org NÃO PODE modificar ACL/visibilidade de exercício alheio (403).
  O papel RBAC de "Treinador" é identificador explícito (não inferido de categoria genérica).
table: exercises, exercise_acl
services:
  - app/services/exercise_service.py (guard created_by + role check)
  - app/services/exercise_acl_service.py (guard)
evidence:
  - GAP: guard não evidenciado.
status: GAP
decision_ref: DEC-TRAIN-EXB-001B, DEC-TRAIN-EXB-002, DEC-TRAIN-EXB-RBAC-001
decision_trace: [DEC-TRAIN-EXB-001B, DEC-TRAIN-EXB-002, DEC-TRAIN-EXB-RBAC-001]
rationale: >
  Evita que treinadores sobreponham configurações de compartilhamento de colegas.
  RBAC explícito previne falsos positivos em guards baseados em inferência de papel.
```

---

## INV-TRAIN-EXB-ACL-005

```yaml
id: INV-TRAIN-EXB-ACL-005
class: B
name: creator_implicit_access
rule: >
  O treinador criador DEVE manter acesso ao próprio exercício ORG
  independentemente da ACL (restritiva ou não).
  Não é necessário o criador estar listado explicitamente na ACL.
table: exercises
services:
  - app/services/exercise_service.py (query de visibilidade)
evidence:
  - GAP: regra de bypass para criador não evidenciada.
status: GAP
decision_ref: DEC-TRAIN-EXB-001B
decision_trace: [DEC-TRAIN-EXB-001B]
rationale: >
  Impede que o criador perca acesso ao próprio conteúdo por configuração de ACL.
```

---

## INV-TRAIN-EXB-ACL-006

```yaml
id: INV-TRAIN-EXB-ACL-006
class: A
name: acl_unique_per_exercise_user
rule: >
  Um usuário NÃO PODE aparecer duplicado na ACL do mesmo exercício.
  Constraint de unicidade em (exercise_id, user_id).
table: exercise_acl
constraints:
  - uq_exercise_acl_exercise_user
evidence:
  - GAP: tabela e constraint não evidenciadas.
status: GAP
decision_ref: DEC-TRAIN-EXB-001B
decision_trace: [DEC-TRAIN-EXB-001B]
rationale: >
  Duplicidade na ACL gera inconsistência de remoção e riscos de query.
```

---

## INV-TRAIN-EXB-ACL-007

```yaml
id: INV-TRAIN-EXB-ACL-007
class: B
name: acl_change_no_retrobreak_historic_session
rule: >
  Mudanças de ACL/visibility_mode NÃO PODEM invalidar a leitura de sessões históricas
  que já referenciam o exercício. O backend DEVE permitir leitura de session_exercises
  independentemente do ACL/visibility atual do exercício referenciado.
tables:
  - training_session_exercises
  - exercises
  - exercise_acl
services:
  - app/services/training_session_service.py (leitura de sessão histórica)
evidence:
  - GAP: guard de leitura histórica não evidenciado.
status: GAP
decision_ref: DEC-TRAIN-EXB-001B
decision_trace: [DEC-TRAIN-EXB-001B]
rationale: >
  Sessões históricas são imutáveis (INV-TRAIN-005); ACL restritiva posterior
  não pode degradar auditoria ou leitura de dados consolidados.
```

---

# FASE_3 — Ciclos/Sessão + Atleta + IA + Wellness Obrigatório (v1.3.0, 2026-02-27)

> **Nota de coexistência (INV-TRAIN-058 vs 004/029):**
> INV-TRAIN-058 é o princípio geral ("mutável até encerrar"). INV-TRAIN-004 e INV-TRAIN-029
> são refinamentos por-papel e por-status que operam **dentro** desse princípio.
> Ou seja: 058 NÃO override as restrições de papel/janela temporal de 004/029.

## INV-TRAIN-054

```yaml
id: INV-TRAIN-054
class: A+B
name: cycle_hierarchy_mandatory
rule: >
  Um Microciclo DEVE pertencer a um Mesociclo válido, e um Mesociclo DEVE pertencer
  a um Macrociclo válido. Não pode existir micro/meso "solto" (sem parent_cycle_id
  apontando para ciclo existente do tipo correto).
tables:
  - training_cycles
  - training_microcycles
constraints:
  - FK training_microcycles.cycle_id → training_cycles.id
  - Service: validação de que parent_cycle_id aponta para cycle_type correto
evidence:
  - GAP: FK básica existe, mas validação de hierarquia (macro→meso→micro) não evidenciada em service.
status: GAP
extends: INV-TRAIN-037, INV-TRAIN-043
rationale: >
  Reforça a integridade hierárquica do planejamento. Ciclos "soltos" degradam
  rastreabilidade e analytics de periodização.
```

---

## INV-TRAIN-055

```yaml
id: INV-TRAIN-055
class: B
name: meso_overlap_allowed
rule: >
  Mesociclos da mesma equipe/macrociclo PODEM se sobrepor em datas.
  O sistema NÃO deve bloquear sobreposição nem forçar ajuste automático.
tables:
  - training_cycles
evidence:
  - GAP: política de sobreposição não explicitada em service/constraint.
status: GAP
rationale: >
  Periodização de handebol admite mesociclos simultâneos (ex.: preparatório físico
  e competitivo técnico-tático). Bloquear sobreposição impediria planejamento real.
```

---

## INV-TRAIN-056

```yaml
id: INV-TRAIN-056
class: A+B
name: micro_contained_in_meso
rule: >
  As datas (start_date, end_date) do Microciclo DEVEM estar 100% contidas no
  intervalo do Mesociclo pai. Microciclo que extrapola é inválido (422).
tables:
  - training_microcycles
  - training_cycles
constraints:
  - Service/DB: check micro.start >= meso.start AND micro.end <= meso.end
evidence:
  - GAP: validação de containment não evidenciada (INV-TRAIN-043 valida datas do micro, mas não containment no meso).
status: GAP
extends: INV-TRAIN-043
rationale: >
  Garante coerência temporal da hierarquia macro→meso→micro sem deixar semanas
  "vazando" fora do mesociclo planejado.
```

---

## INV-TRAIN-057

```yaml
id: INV-TRAIN-057
class: B
name: standalone_session_explicit_flag
rule: >
  Toda sessão DEVE estar vinculada a um Microciclo (via microcycle_id) OU
  estar marcada explicitamente como avulsa (microcycle_id IS NULL + flag standalone).
  Sessão sem vínculo e sem flag é inválida.
tables:
  - training_sessions
services:
  - app/services/training_session_service.py (validação create/update)
evidence:
  - GAP: campo standalone/flag de sessão avulsa não evidenciado no schema.
status: GAP
rationale: >
  Evita sessões "invisíveis" ao planejamento, permitindo ao treinador treinos
  fora da periodização (amistosos, reforço).
```

---

## INV-TRAIN-058

```yaml
id: INV-TRAIN-058
class: B
name: session_structure_mutable_until_close
rule: >
  O treinador PODE adicionar/remover/reordenar exercícios enquanto a sessão NÃO
  estiver encerrada (status != readonly). Após encerrar, a estrutura de exercícios
  é histórica e NÃO pode ser alterada.
  NOTA: Este é o princípio geral. INV-TRAIN-004 (janela por papel) e INV-TRAIN-029
  (regras por status) são refinamentos que operam DENTRO deste princípio.
tables:
  - training_sessions
  - training_session_exercises
services:
  - app/services/training_session_service.py
  - app/services/session_exercise_service.py
evidence:
  - PARCIAL: status lifecycle impede edição em readonly, mas guard explícito de exercícios por status
    não evidenciado como regra separada.
status: PARCIAL
coexists_with: INV-TRAIN-004, INV-TRAIN-029
rationale: >
  Permite ajustes de última hora no treino (realidade operacional) sem degradar
  o histórico consolidado.
```

---

## INV-TRAIN-059

```yaml
id: INV-TRAIN-059
class: A
name: exercise_order_contiguous_unique
rule: >
  Dentro de uma sessão, a ordem dos exercícios (order_index) DEVE ser:
  - Única por sessão (sem duplicidade),
  - Contígua (1..N sem gaps),
  - Determinística.
  Reorder DEVE normalizar gaps.
tables:
  - training_session_exercises
constraints:
  - uq_session_exercises_order (unique (training_session_id, order_index))
evidence:
  - INV-TRAIN-045 garante unicidade, mas contiguidade/normalização de gaps não evidenciada.
status: PARCIAL
extends: INV-TRAIN-045
rationale: >
  Ordem determinística garante reprodutibilidade do treino e UX consistente
  no drag-and-drop.
```

---

## INV-TRAIN-060

```yaml
id: INV-TRAIN-060
class: B
name: org_exercise_default_restricted
rule: >
  Ao criar exercício de scope ORG, o default de visibility_mode DEVE ser
  "restricted" (apenas o treinador criador vê). Compartilhar com outros
  treinadores exige ação explícita do criador (ACL ou mudança para org_wide).
tables:
  - exercises
services:
  - app/services/exercise_service.py (default na criação)
evidence:
  - GAP: default atual documentado como org_wide (INV-TRAIN-EXB-ACL-001 amendada para restricted em v1.3.0).
status: GAP
overrides: INV-TRAIN-EXB-ACL-001 (default)
decision_trace: [DECISÃO_HUMANA_2026-02-27]
rationale: >
  Princípio de menor privilégio. Evita exposição acidental de exercícios
  proprietários do treinador.
```

---

## INV-TRAIN-061

```yaml
id: INV-TRAIN-061
class: B
name: system_exercise_copy_not_edit
rule: >
  Exercícios SYSTEM NÃO podem ser editados por usuários de org. Ao "adaptar",
  o sistema DEVE criar uma cópia ORG (via copy-to-org) e o treinador edita a cópia.
  O exercício SYSTEM original permanece inalterado.
tables:
  - exercises
services:
  - app/services/exercise_service.py (guard SYSTEM + copy-to-org)
evidence:
  - INV-TRAIN-048 proíbe edição de SYSTEM. Copy-to-org está em CONTRACT-TRAIN-095 (GAP).
status: GAP
extends: INV-TRAIN-048
rationale: >
  Preserva o catálogo global. Adaptações locais são cópias ORG rastreáveis.
```

---

## INV-TRAIN-062

```yaml
id: INV-TRAIN-062
class: B
name: exercise_visibility_required_for_session_add
rule: >
  Um exercício só PODE ser adicionado a uma sessão se for visível ao treinador
  naquele momento: SYSTEM (global), ORG criado por ele, ou ORG compartilhado
  via ACL com ele. Exercício ORG restricted sem ACL para o treinador → 403.
tables:
  - training_session_exercises
  - exercises
  - exercise_acl
services:
  - app/services/session_exercise_service.py (guard de visibilidade)
evidence:
  - GAP: guard de visibilidade no add-exercise-to-session não evidenciado.
status: GAP
extends: INV-TRAIN-051
rationale: >
  Impede que treinador B monte sessão com exercício privado do treinador A.
```

---

## INV-TRAIN-063

```yaml
id: INV-TRAIN-063
class: B+D
name: athlete_preconfirm_not_official
rule: >
  O atleta PODE pré-confirmar presença no app (status = preconfirmed),
  mas isso NÃO constitui presença oficial. A presença oficial só é
  consolidada pelo treinador no encerramento da sessão (INV-TRAIN-064).
tables:
  - attendance
services:
  - app/services/attendance_service.py (fluxo de pré-confirmação)
evidence:
  - GAP: fluxo de pré-confirmação de atleta não evidenciado.
status: GAP
extends: INV-TRAIN-016
decision_trace: [DECISÃO_HUMANA_2026-02-27]
rationale: >
  Dá ao atleta engajamento antecipado sem retirar do treinador a
  autoridade sobre presença oficial.
```

---

## INV-TRAIN-064

```yaml
id: INV-TRAIN-064
class: B
name: official_attendance_at_closure
rule: >
  O sistema só PODE consolidar presença oficial (presente/ausente/justificado)
  no momento do encerramento da sessão pelo treinador. Antes do encerramento,
  registros de presença são provisórios/rascunho.
tables:
  - attendance
  - training_sessions
services:
  - app/services/attendance_service.py
  - app/services/training_session_service.py (fluxo de close)
evidence:
  - PARCIAL: close existe, mas fluxo de consolidação de presença no close não evidenciado como separado.
status: GAP
extends: INV-TRAIN-016
decision_trace: [DECISÃO_HUMANA_2026-02-27]
rationale: >
  Evita que presença parcial antes do treino vire dado oficial sem validação humana.
```

---

## INV-TRAIN-065

```yaml
id: INV-TRAIN-065
class: B
name: closure_allows_inconsistency_as_pending
rule: >
  Se no encerramento houver atleta não elegível ou dado não resolvido,
  o sistema DEVE permitir encerrar. Itens inconsistentes NÃO viram oficiais;
  viram "pendências" com motivo, rastreáveis em fila separada (INV-TRAIN-066).
tables:
  - training_sessions
  - attendance
services:
  - app/services/training_session_service.py (close com pendências)
evidence:
  - GAP: fluxo de encerramento com pendências não evidenciado.
status: GAP
decision_trace: [DECISÃO_HUMANA_2026-02-27]
rationale: >
  Prioriza o encerramento do treino (realidade operacional) sobre perfeição de dados.
  Pendências são tratadas posteriormente sem bloquear o fluxo.
```

---

## INV-TRAIN-066

```yaml
id: INV-TRAIN-066
class: B+D
name: pending_queue_separate
rule: >
  Pendências geradas no encerramento (presença inválida, atleta não resolvido etc.)
  DEVEM ir para fila/tela separada "Pendências do Treino". A sessão encerrada
  NÃO é alterada; pendências são entidades próprias vinculadas à sessão.
tables:
  - training_pending_items (nova tabela ou extensão)
  - training_sessions
services:
  - app/services/training_pending_service.py (novo)
evidence:
  - GAP: tabela e service de pendências não existem.
status: GAP
decision_trace: [DECISÃO_HUMANA_2026-02-27]
rationale: >
  Separar pendências da sessão concluída preserva integridade do histórico
  e dá ao treinador UX dedicada para resolução assíncrona.
```

---

## INV-TRAIN-067

```yaml
id: INV-TRAIN-067
class: B+D
name: athlete_pending_collaboration_no_validate
rule: >
  O atleta PODE ajudar a resolver pendências (ex.: confirmar identidade),
  mas NÃO PODE transformar pendência em dado oficial sozinho.
  A validação final de qualquer pendência é exclusiva do treinador.
tables:
  - training_pending_items
services:
  - app/services/training_pending_service.py (RBAC: atleta colabora, treinador valida)
evidence:
  - GAP: fluxo colaborativo não evidenciado.
status: GAP
decision_trace: [DECISÃO_HUMANA_2026-02-27]
rationale: >
  Engaja o atleta sem delegar autoridade de validação oficial.
```

---

## INV-TRAIN-068

```yaml
id: INV-TRAIN-068
class: D
name: athlete_sees_training_before
rule: >
  O atleta DEVE conseguir ver, antes do treino: horário, lista de exercícios
  e objetivo da sessão (quando existir), sem depender de preencher formulários.
  Esta é informação read-only na perspectiva do atleta.
tables:
  - training_sessions
  - training_session_exercises
services:
  - Endpoint de leitura para atleta (scoped pela equipe)
evidence:
  - GAP: endpoint/tela de atleta para ver treino antecipadamente não evidenciado.
status: GAP
decision_trace: [DECISÃO_HUMANA_2026-02-27]
rationale: >
  Permite ao atleta se preparar mentalmente e logisticamente para o treino.
```

---

## INV-TRAIN-069

```yaml
id: INV-TRAIN-069
class: D+B
name: exercise_media_accessible_to_athlete
rule: >
  Se um exercício está no treino do atleta, o atleta DEVE poder ver as
  mídias/instruções do exercício, independente da visibility_mode do exercício
  (SYSTEM ou ORG). A visibilidade por mídia segue a sessão, não o exercício.
tables:
  - training_session_exercises
  - exercise_media
services:
  - app/services/session_exercise_service.py (acesso via sessão)
evidence:
  - GAP: acesso do atleta a mídia via sessão não evidenciado.
status: GAP
decision_trace: [DECISÃO_HUMANA_2026-02-27]
rationale: >
  Atleta precisa das instruções/vídeos para executar corretamente,
  independente de quem criou o exercício.
```

---

## INV-TRAIN-070

```yaml
id: INV-TRAIN-070
class: B+D
name: post_training_conversational
rule: >
  O pós-treino do atleta (RPE, dificuldade, dores, feedback) DEVE poder
  ser registrado de forma conversacional (texto/voz), sem exigir formulário
  rígido como pré-requisito. Campos de formulário, se existirem, DEVEM ser opcionais.
tables:
  - wellness_post (extensão com campo conversational_feedback)
services:
  - app/services/wellness_post_service.py (aceitar input conversacional)
evidence:
  - GAP: input conversacional não evidenciado; wellness_post atual é formulário fixo.
status: GAP
decision_trace: [DECISÃO_HUMANA_2026-02-27]
rationale: >
  Reduz atrito para o atleta e aumenta taxa de resposta pós-treino.
  Formulário rígido é barreira para adolescentes.
```

---

## INV-TRAIN-071

```yaml
id: INV-TRAIN-071
class: B+D
name: wellness_missing_blocks_full_content
rule: >
  Se o atleta NÃO cumprir a política de wellness obrigatória (INV-TRAIN-076),
  o sistema DEVE:
  - Permitir ver o mínimo operacional (horário do treino, local).
  - Bloquear conteúdo completo (exercícios, vídeos, instruções e detalhes).
  O bloqueio de conteúdo é consequência da política, não regra independente.
tables:
  - wellness_pre
  - wellness_post
  - training_sessions
services:
  - app/services/athlete_content_gate_service.py (novo)
evidence:
  - GAP: gate de conteúdo por wellness não implementado.
status: GAP
extends: INV-TRAIN-002
depends_on: INV-TRAIN-076
decision_trace: [DECISÃO_HUMANA_2026-02-27]
rationale: >
  Incentivo positivo: compliance com wellness desbloqueia valor (conteúdo).
  Atleta nunca fica "no escuro" sobre horário/local.
```

---

## INV-TRAIN-072

```yaml
id: INV-TRAIN-072
class: B
name: ai_suggestion_not_order
rule: >
  A IA PODE enviar mensagens automáticas ao atleta, mas SEMPRE como
  sugestão/apoio (tom não-imperativo) e NÃO PODE criar/publicar treino
  oficial automaticamente. Toda geração de treino pela IA passa por
  "editar antes" do treinador (INV-TRAIN-075, INV-TRAIN-080).
services:
  - app/services/ai_coach_service.py (tone guard + publish guard)
evidence:
  - GAP: módulo de IA coach não existe.
status: GAP
decision_trace: [DECISÃO_HUMANA_2026-02-27]
rationale: >
  O treinador humano é a autoridade. IA é ferramenta de apoio,
  não tomador de decisão.
```

---

## INV-TRAIN-073

```yaml
id: INV-TRAIN-073
class: B
name: ai_privacy_no_intimate_content
rule: >
  O treinador NÃO PODE ver conteúdo íntimo das conversas do atleta com a IA.
  O treinador só recebe alertas/resumos de risco (safety), sem expor texto íntimo.
  O atleta é dono do conteúdo da conversa.
services:
  - app/services/ai_coach_service.py (privacy filter)
  - app/services/coach_alerts_service.py (summarizer)
evidence:
  - GAP: módulo de IA coach não existe.
status: GAP
decision_trace: [DECISÃO_HUMANA_2026-02-27]
rationale: >
  Confiança atleta ↔ IA depende de privacidade. Treinador recebe
  informação acionável sem violação de intimidade.
```

---

## INV-TRAIN-074

```yaml
id: INV-TRAIN-074
class: B
name: ai_educational_content_independent
rule: >
  A IA PODE explicar regras e situações de jogo (2 minutos, superioridade numérica,
  7m, princípios táticos) mesmo que o treino do dia não cite o tema.
  Conteúdo educativo NÃO altera treino/agendamento; é informativo.
services:
  - app/services/ai_coach_service.py (educational module)
evidence:
  - GAP: conteúdo educativo não implementado.
status: GAP
decision_trace: [DECISÃO_HUMANA_2026-02-27]
rationale: >
  Atleta tem curiosidade além do treino do dia. Conteúdo educativo aumenta
  literacia tática sem interferir no planejamento.
```

---

## INV-TRAIN-075

```yaml
id: INV-TRAIN-075
class: B
name: ai_extra_training_draft_only
rule: >
  Se o atleta pedir "treino extra", a IA PODE gerar um rascunho, mas o rascunho
  DEVE chegar ao treinador como "editar antes de aprovar". O sistema NÃO PODE
  publicar/agendar automaticamente. Publicação só após ação explícita do treinador.
tables:
  - training_sessions (status=draft, source=ai_athlete_request)
services:
  - app/services/ai_coach_service.py (draft generation)
  - app/services/training_session_service.py (source tracking)
evidence:
  - GAP: geração de rascunho por IA não implementada.
status: GAP
decision_trace: [DECISÃO_HUMANA_2026-02-27]
rationale: >
  Mantém o treinador humano como gatekeeper de tudo que vira treino oficial.
  Evita risco de IA sugerir treino inadequado.
```

---

## INV-TRAIN-076

```yaml
id: INV-TRAIN-076
class: B
name: mandatory_wellness_policy
rule: >
  Para o atleta acessar conteúdo completo do treino (exercícios, vídeos,
  instruções e detalhes), o sistema DEVE exigir:
  1) wellness pré DO DIA; e
  2) wellness pós DO ÚLTIMO TREINO realizado (quando existir).
  Se algum estiver faltando, o atleta vê apenas mínimo operacional
  (horário, local), sem conteúdo completo.
  "Último treino realizado" = último treino encerrado/concluído do atleta/equipe.
tables:
  - wellness_pre
  - wellness_post
  - training_sessions
services:
  - app/services/athlete_content_gate_service.py (policy check)
evidence:
  - GAP: política de bloqueio por wellness não implementada.
status: GAP
extends: INV-TRAIN-002, INV-TRAIN-003
decision_trace: [DECISÃO_HUMANA_2026-02-27]
rationale: >
  Incentiva compliance contínua do atleta com wellness, criando ciclo virtuoso:
  preencher wellness → desbloquear conteúdo → preparar-se melhor → desempenho.
```

---

## INV-TRAIN-077

```yaml
id: INV-TRAIN-077
class: B+D
name: immediate_virtual_coach_feedback
rule: >
  Quando o atleta concluir o pós-treino conversacional, o sistema DEVE gerar
  e entregar feedback curto do treinador virtual contendo:
  1) 1 reconhecimento (esforço/consistência), e
  2) 1 orientação prática (técnica/tática/recuperação) aplicável ao próximo treino.
  Se o atleta NÃO concluir o pós-treino, o sistema NÃO gera feedback.
services:
  - app/services/ai_coach_service.py (feedback gen)
  - app/services/wellness_post_service.py (trigger on complete)
evidence:
  - GAP: treinador virtual e feedback automático não implementados.
status: GAP
extends: INV-TRAIN-013
decision_trace: [DECISÃO_HUMANA_2026-02-27]
rationale: >
  Recompensa imediata por completar pós-treino. Orientação prática
  conecta feedback a ação futura.
```

---

## INV-TRAIN-078

```yaml
id: INV-TRAIN-078
class: B+D
name: progress_view_requires_compliance
rule: >
  O atleta só PODE visualizar a aba/visão de progresso pessoal
  (histórico e comparativos de evolução) quando estiver em conformidade
  com a política de check-ins obrigatórios (INV-TRAIN-076).
  Se não estiver em conformidade, vê apenas visão básica do dia.
services:
  - app/services/athlete_content_gate_service.py (progress gate)
evidence:
  - GAP: gate de progresso por compliance não implementado.
status: GAP
extends: INV-TRAIN-013
depends_on: INV-TRAIN-076
decision_trace: [DECISÃO_HUMANA_2026-02-27]
rationale: >
  Reforça incentivo de compliance: progressão pessoal é desbloqueada
  por participação contínua.
```

---

## INV-TRAIN-079

```yaml
id: INV-TRAIN-079
class: B
name: individual_recognition_no_intimate_leak
rule: >
  Qualquer reconhecimento/feedback gerado para valorizar o atleta
  (consistência, participação) DEVE ser individual e NÃO PODE expor
  conteúdo íntimo de conversa do atleta para terceiros.
  O treinador recebe apenas resumos/alertas conforme INV-TRAIN-073.
services:
  - app/services/ai_coach_service.py (privacy filter on recognition)
evidence:
  - GAP: módulo de reconhecimento não implementado.
status: GAP
extends: INV-TRAIN-073
decision_trace: [DECISÃO_HUMANA_2026-02-27]
rationale: >
  Proteção de dados sensíveis. Reconhecimento público usa apenas
  métricas agregadas (taxa de resposta, frequência), não conteúdo de conversa.
```

---

## INV-TRAIN-080

```yaml
id: INV-TRAIN-080
class: B
name: ai_coach_draft_only
rule: >
  A IA PODE ajudar o treinador sugerindo exercícios, montando sessões e propondo
  planejamento (microciclo/agenda), mas toda proposta DEVE ser criada como
  rascunho ("editar antes"). O sistema NÃO pode publicar/agendar automaticamente.
  Publicação/agendamento ocorre APENAS após ação explícita do treinador.
  (Generaliza INV-TRAIN-075 para o contexto do treinador.)
tables:
  - training_sessions (status=draft, source=ai_coach_suggestion)
services:
  - app/services/ai_coach_service.py (draft-only guard)
evidence:
  - GAP: módulo de IA para coach não implementado.
status: GAP
extends: INV-TRAIN-075
decision_trace: [DECISÃO_HUMANA_2026-02-27]
rationale: >
  O treinador DEVE revisar toda proposta antes de publicar. IA
  é copiloto, não autopiloto.
```

---

## INV-TRAIN-081

```yaml
id: INV-TRAIN-081
class: B
name: ai_suggestion_requires_justification
rule: >
  Toda sugestão da IA para o treinador (exercício/sessão/planejamento) DEVE
  incluir justificativa mínima (curta e objetiva) baseada em sinais do sistema
  (wellness, carga recente, consistência, objetivo do microciclo, dados de jogo/scout).
  Sugestões sem justificativa NÃO PODEM ser apresentadas como recomendação
  (apenas como "ideia genérica" com label distinto).
services:
  - app/services/ai_coach_service.py (justification enforcer)
evidence:
  - GAP: módulo de IA para coach não implementado.
status: GAP
decision_trace: [DECISÃO_HUMANA_2026-02-27]
rationale: >
  Justificativa rastreável permite ao treinador avaliar qualidade da sugestão
  e cria feedback loop para melhoria do modelo de IA.
```
