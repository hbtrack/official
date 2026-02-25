# TRAINING_FRONT_BACK_CONTRACT.md — Contratos Front-Back do Módulo TRAINING

Status: DRAFT  
Versão: v1.0.0  
Tipo de Documento: SSOT Normativo — Front-Back Contract  
Módulo: TRAINING  
Fase: PRD v2.2 (2026-02-20) + AS-IS repo (2026-02-25)  
Autoridade: NORMATIVO_TECNICO  
Última revisão: 2026-02-25  

Dependências (leitura):
- `docs/hbtrack/modulos/treinos/INVARIANTS_TRAINING.md`
- `docs/hbtrack/modulos/treinos/TRAINING_USER_FLOWS.md`
- `docs/hbtrack/modulos/treinos/TRAINING_SCREENS_SPEC.md`
- `Hb Track - Backend/docs/ssot/openapi.json`
- `Hb Track - Backend/docs/ssot/schema.sql`
- `Hb Track - Backend/app/api/v1/api.py`
- `Hb Track - Backend/app/api/v1/routers/*` (training, attendance, wellness, analytics, exports)
- `Hb Track - Frontend/src/lib/api/*` (trainings, attendance, wellness, analytics, rankings)

---

## 1) Objetivo (Normativo)

Definir o **contrato determinístico** entre Frontend e Backend do módulo **TRAINING**:
- endpoints e operationIds,
- shapes mínimos de request/response (quando OpenAPI não tipa),
- tipos canônicos (UUID vs int, datetime),
- erros e regras (mapeadas para invariantes),
- gaps de paridade FE↔BE e contrato↔schema.

Este documento é **TO-BE**: quando houver divergência, a regra é **registrar como `DIVERGENTE_DO_SSOT`** e criar ARs para convergir.

---

## 2) SSOT e precedência (normativo)

Ordem de precedência para decisões de contrato:
1. **DB schema/constraints/triggers**: `Hb Track - Backend/docs/ssot/schema.sql`
2. **Models/Services** (regras de domínio)
3. **OpenAPI SSOT**: `Hb Track - Backend/docs/ssot/openapi.json`
4. **Frontend** (UX e integrações)
5. **PRD/TRD** (referência)

Quando **OpenAPI** estiver incompleto (schema `{}`) ou divergente do DB, este contrato define o **shape mínimo normativo** e registra o gap.

---

## 3) Convenções gerais do contrato

### 3.1 Base URL
- Base: `/api/v1`
- As rotas abaixo são relativas a este prefixo.

### 3.2 Tipos canônicos
- IDs primários e FKs: **UUID string** (`format: uuid`) para `team_id`, `athlete_id`, `training_session_id`, `cycle_id`, `microcycle_id`, `template_id`, `exercise_id`, etc.
- Datas (sem hora): `YYYY-MM-DD`
- Datetimes: ISO 8601 com timezone (idealmente UTC), ex.: `2026-02-25T10:00:00Z`
- Percentuais de foco: `number` (persistência em `numeric/decimal` no DB)

### 3.3 Soft delete (sessões, ciclos, microciclos)
Regra normativa:
- Operações de delete devem exigir `reason` (query param) e registrar `deleted_at` + `deleted_reason`.  
Ref.: `INV-TRAIN-008`.

### 3.4 Enums relevantes (SSOT)
- `training_sessions.status`: `draft|scheduled|in_progress|pending_review|readonly` (INV-TRAIN-006)
- `attendance.presence_status`: `present|absent|justified`
- `attendance.participation_type`: `full|partial|adapted|did_not_train`
- `attendance.reason_absence`: `medico|escola|familiar|opcional|outro`
- `wellness_pre.menstrual_cycle_phase` (opcional): `folicular|lutea|menstruacao|nao_informa`
- `training_alerts.alert_type`: `weekly_overload|low_wellness_response`
- `training_alerts.severity`: `warning|critical`
- `training_suggestions.type`: `compensation|reduce_next_week`
- `training_suggestions.status`: `pending|applied|dismissed`

---

## 4) Shapes canônicos mínimos (quando usados pelo FE)

> Nota: quando o OpenAPI já define schema tipado, ele permanece a referência.  
> Quando o OpenAPI não tipa (schema `{}`), os shapes abaixo são **normativos mínimos**.

### 4.1 Attendance (Presenças)

Regra de consistência DB (SSOT):
- `presence_status='absent'` ⇒ `reason_absence MUST be NULL`
- Ausência com motivo ⇒ usar `presence_status='justified'` (ver `ck_attendance_absent_reason_null` no model)

Shape mínimo:
```yaml
Attendance:
  id: uuid
  training_session_id: uuid
  athlete_id: uuid
  team_registration_id: uuid
  presence_status: present|absent|justified
  participation_type?: full|partial|adapted|did_not_train
  reason_absence?: medico|escola|familiar|opcional|outro
  minutes_effective?: int
  comment?: string
  source: manual|import|correction
  correction_by_user_id?: uuid
  correction_at?: datetime
```

### 4.2 Wellness Pre (Pré-treino)

Campos exigidos pelo DB:
```yaml
WellnessPreCreate:
  athlete_id: uuid
  sleep_hours: number  # 0..24, 1 casa decimal (numeric(4,1))
  sleep_quality: int   # 1..5
  fatigue_pre: int     # 0..10
  stress_level: int    # 0..10
  muscle_soreness: int # 0..10
  notes?: string
  readiness_score?: int # 0..10 (opcional SSOT)
  menstrual_cycle_phase?: folicular|lutea|menstruacao|nao_informa
```

### 4.3 Wellness Post (Pós-treino)

Campos exigidos pelo DB:
```yaml
WellnessPostCreate:
  athlete_id: uuid
  session_rpe: int        # 0..10
  fatigue_after: int      # 0..10
  mood_after: int         # 0..10
  muscle_soreness_after?: int # 0..10
  minutes_effective?: int
  notes?: string
```

Campo derivado:
- `internal_load` é calculado por trigger: `minutes_effective × session_rpe` (INV-TRAIN-021).

---

## 5) Contratos por área (CONTRACT-TRAIN-###)

### 5.1 Training Sessions — CRUD + workflow

| ID | Método | Path | operationId | Request | Response | Status | Invariantes-chave |
|---|---|---|---|---|---|---|---|
| CONTRACT-TRAIN-001 | GET | `/training-sessions` | `list_training_sessions_api_v1_training_sessions_get` | query filters + paginação | `TrainingSessionPaginatedResponse` | EVIDENCIADO | INV-TRAIN-006 |
| CONTRACT-TRAIN-002 | POST | `/training-sessions` | `create_training_session_api_v1_training_sessions_post` | `TrainingSessionCreate` | `TrainingSession` | EVIDENCIADO | INV-TRAIN-001, INV-TRAIN-006 |
| CONTRACT-TRAIN-003 | GET | `/training-sessions/{training_session_id}` | `get_training_session_by_id_api_v1_training_sessions__training_session_id__get` | — | `TrainingSession` | EVIDENCIADO | INV-TRAIN-006 |
| CONTRACT-TRAIN-004 | PATCH | `/training-sessions/{training_session_id}` | `update_training_session_api_v1_training_sessions__training_session_id__patch` | `TrainingSessionUpdate` | `TrainingSession` | EVIDENCIADO | INV-TRAIN-004, INV-TRAIN-005, INV-TRAIN-001 |
| CONTRACT-TRAIN-005 | DELETE | `/training-sessions/{training_session_id}?reason=` | `delete_training_session_api_v1_training_sessions__training_session_id__delete` | query `reason` | 204 | EVIDENCIADO | INV-TRAIN-008 |
| CONTRACT-TRAIN-006 | POST | `/training-sessions/{training_session_id}/publish` | `publish_training_session_api_v1_training_sessions__training_session_id__publish_post` | `{}` | `TrainingSession` | EVIDENCIADO | INV-TRAIN-006 |
| CONTRACT-TRAIN-007 | POST | `/training-sessions/{training_session_id}/close` | `close_training_session_api_v1_training_sessions__training_session_id__close_post` | `{}` | `SessionClosureResponse` | EVIDENCIADO | INV-TRAIN-006 |
| CONTRACT-TRAIN-008 | POST | `/training-sessions/{training_session_id}/duplicate` | `duplicate_training_session_api_v1_training_sessions__training_session_id__duplicate_post` | `{}` | `TrainingSession` | EVIDENCIADO | INV-TRAIN-006 |
| CONTRACT-TRAIN-009 | POST | `/training-sessions/{training_session_id}/restore` | `restore_training_session_api_v1_training_sessions__training_session_id__restore_post` | `{}` | `TrainingSession` | EVIDENCIADO | INV-TRAIN-008 |
| CONTRACT-TRAIN-010 | POST | `/training-sessions/copy-week` | `copy_week_sessions_api_v1_training_sessions_copy_week_post` | query: `team_id`, `source_week_start`, `target_week_start`, `validate_focus` | `TrainingSession[]` | EVIDENCIADO | INV-TRAIN-005, INV-TRAIN-001 |
| CONTRACT-TRAIN-011 | GET | `/training-sessions/{training_session_id}/deviation` | `get_session_deviation_api_v1_training_sessions__training_session_id__deviation_get` | — | `DeviationAnalysis` | EVIDENCIADO | INV-TRAIN-011 |
| CONTRACT-TRAIN-012 | GET | `/training-sessions/{training_session_id}/wellness-status` | `get_wellness_status_api_v1_training_sessions__training_session_id__wellness_status_get` | — | `WellnessStatusResponse` | EVIDENCIADO | INV-TRAIN-026 |

Notas:
- O endpoint `copy-week` tem regra extra de validação opcional `validate_focus=True` exigindo soma de focos = 100% (diferente de `INV-TRAIN-001` que permite até 120%). Isso deve ser refletido no FE como validação explicita no fluxo.

---

### 5.2 Training Sessions — Rotas Scoped por Team

| ID | Método | Path | operationId | Request | Response | Status | Observações |
|---|---|---|---|---|---|---|---|
| CONTRACT-TRAIN-013 | GET | `/teams/{team_id}/trainings` | `scoped_list_training_sessions_api_v1_teams__team_id__trainings_get` | query paginação | `TrainingSessionPaginatedResponse` | EVIDENCIADO | Alternativa scoped do list |
| CONTRACT-TRAIN-014 | POST | `/teams/{team_id}/trainings` | `scoped_create_training_session_api_v1_teams__team_id__trainings_post` | `ScopedTrainingSessionCreate` | `TrainingSession` | EVIDENCIADO | `organization_id` pode ser inferido |
| CONTRACT-TRAIN-015 | GET | `/teams/{team_id}/trainings/{training_id}` | `scoped_get_training_session_api_v1_teams__team_id__trainings__training_id__get` | — | `TrainingSession` | EVIDENCIADO | Enforce team scope |
| CONTRACT-TRAIN-016 | PATCH | `/teams/{team_id}/trainings/{training_id}` | `scoped_update_training_session_api_v1_teams__team_id__trainings__training_id__patch` | `TrainingSessionUpdate` | `TrainingSession` | EVIDENCIADO | Enforce team scope |
| CONTRACT-TRAIN-017 | DELETE | `/teams/{team_id}/trainings/{training_id}?reason=` | `scoped_delete_training_session_api_v1_teams__team_id__trainings__training_id__delete` | query `reason` | 204 | EVIDENCIADO | Soft delete |
| CONTRACT-TRAIN-018 | POST | `/teams/{team_id}/trainings/{training_id}/restore` | `scoped_restore_training_session_api_v1_teams__team_id__trainings__training_id__restore_post` | `{}` | `TrainingSession` | EVIDENCIADO | Restore de soft delete |

---

### 5.3 Session Exercises (drag-and-drop)

| ID | Método | Path | operationId | Request | Response | Status | Invariantes-chave |
|---|---|---|---|---|---|---|---|
| CONTRACT-TRAIN-019 | GET | `/training-sessions/{session_id}/exercises` | `get_session_exercises_api_v1_training_sessions__session_id__exercises_get` | — | `SessionExerciseListResponse` | EVIDENCIADO | INV-TRAIN-045 |
| CONTRACT-TRAIN-020 | POST | `/training-sessions/{session_id}/exercises` | `add_exercise_to_session_api_v1_training_sessions__session_id__exercises_post` | `SessionExerciseCreate` | `SessionExerciseResponse` | EVIDENCIADO | INV-TRAIN-045 |
| CONTRACT-TRAIN-021 | POST | `/training-sessions/{session_id}/exercises/bulk` | `bulk_add_exercises_to_session_api_v1_training_sessions__session_id__exercises_bulk_post` | `SessionExerciseBulkCreate` | `SessionExerciseResponse[]` | EVIDENCIADO | INV-TRAIN-045 |
| CONTRACT-TRAIN-022 | PATCH | `/training-sessions/exercises/{session_exercise_id}` | `update_session_exercise_api_v1_training_sessions_exercises__session_exercise_id__patch` | `SessionExerciseUpdate` | `SessionExerciseResponse` | EVIDENCIADO | INV-TRAIN-045 |
| CONTRACT-TRAIN-023 | PATCH | `/training-sessions/{session_id}/exercises/reorder` | `reorder_session_exercises_api_v1_training_sessions__session_id__exercises_reorder_patch` | `SessionExerciseReorder` | `{success, updated_count}` | EVIDENCIADO | INV-TRAIN-045 |
| CONTRACT-TRAIN-024 | DELETE | `/training-sessions/exercises/{session_exercise_id}` | `remove_exercise_from_session_api_v1_training_sessions_exercises__session_exercise_id__delete` | — | 204 | EVIDENCIADO | INV-TRAIN-045 |

---

### 5.4 Attendance (Presenças)

> Observação de naming: attendance usa prefixo `/training_sessions` (underscore) por herança histórica.

| ID | Método | Path | operationId | Request | Response | Status | Invariantes-chave |
|---|---|---|---|---|---|---|---|
| CONTRACT-TRAIN-025 | GET | `/training_sessions/{training_session_id}/attendance` | `list_attendance_by_session_api_v1_training_sessions__training_session_id__attendance_get` | query opcional `athlete_id`, `status` | `Attendance[]` | EVIDENCIADO | INV-TRAIN-016 |
| CONTRACT-TRAIN-026 | POST | `/training_sessions/{training_session_id}/attendance` | `add_attendance_to_session_api_v1_training_sessions__training_session_id__attendance_post` | `AttendanceCreate` | `Attendance` | EVIDENCIADO | INV-TRAIN-030 |
| CONTRACT-TRAIN-027 | POST | `/training_sessions/{training_session_id}/attendance/batch` | `add_attendance_batch_api_v1_training_sessions__training_session_id__attendance_batch_post` | `AttendanceCreate[]` | `Attendance[]` | EVIDENCIADO | INV-TRAIN-030 |
| CONTRACT-TRAIN-028 | GET | `/training_sessions/{training_session_id}/attendance/statistics` | `get_session_attendance_statistics_api_v1_training_sessions__training_session_id__attendance_statistics_get` | — | `{total_athletes, present_count, absent_count, attendance_rate}` | EVIDENCIADO | (derivado) |

Gap FE↔DB (crítico):
- O frontend precisa aceitar `presence_status='justified'` e não enviar `reason_absence` quando `presence_status='absent'` (DB bloqueia).

---

### 5.5 Wellness Pre/Post

> Observação de naming: prefixo de router é `/wellness-pre|/wellness-post` (hífen) mas subpaths mantêm `_` (`/wellness_pre`, `/training_sessions/...`).

#### Wellness Pre

| ID | Método | Path | operationId | Request | Response | Status | Invariantes-chave |
|---|---|---|---|---|---|---|---|
| CONTRACT-TRAIN-029 | GET | `/wellness-pre/training_sessions/{training_session_id}/wellness_pre` | `list_wellness_pre_by_session_api_v1_wellness_pre_training_sessions__training_session_id__wellness_pre_get` | query opcional `athlete_id` | `WellnessPre[]` | EVIDENCIADO | INV-TRAIN-026 |
| CONTRACT-TRAIN-030 | POST | `/wellness-pre/training_sessions/{training_session_id}/wellness_pre` | `add_wellness_pre_to_session_api_v1_wellness_pre_training_sessions__training_session_id__wellness_pre_post` | `WellnessPreCreate` | `WellnessPre` | EVIDENCIADO | INV-TRAIN-002, INV-TRAIN-009 |
| CONTRACT-TRAIN-031 | GET | `/wellness-pre/training_sessions/{training_session_id}/wellness_pre/status` | `get_wellness_pre_status_api_v1_wellness_pre_training_sessions__training_session_id__wellness_pre_status_get` | — | `{total_athletes, responded_pre, pending[], response_rate}` | EVIDENCIADO | (derivado) |
| CONTRACT-TRAIN-032 | GET | `/wellness-pre/wellness_pre/{wellness_pre_id}` | `get_wellness_pre_by_id_api_v1_wellness_pre_wellness_pre__wellness_pre_id__get` | — | `WellnessPre` | EVIDENCIADO | INV-TRAIN-026 |
| CONTRACT-TRAIN-033 | PATCH | `/wellness-pre/wellness_pre/{wellness_pre_id}` | `update_wellness_pre_api_v1_wellness_pre_wellness_pre__wellness_pre_id__patch` | `WellnessPreUpdate` | `WellnessPre` | EVIDENCIADO | INV-TRAIN-002 |
| CONTRACT-TRAIN-034 | POST | `/wellness-pre/wellness_pre/{wellness_pre_id}/request-unlock` | `request_wellness_unlock_api_v1_wellness_pre_wellness_pre__wellness_pre_id__request_unlock_post` | `{reason?}` | `{status}` | EVIDENCIADO | (workflow) |

#### Wellness Post

| ID | Método | Path | operationId | Request | Response | Status | Invariantes-chave |
|---|---|---|---|---|---|---|---|
| CONTRACT-TRAIN-035 | GET | `/wellness-post/training_sessions/{training_session_id}/wellness_post` | `list_wellness_post_by_session_api_v1_wellness_post_training_sessions__training_session_id__wellness_post_get` | query opcional `athlete_id` | `WellnessPost[]` | EVIDENCIADO | INV-TRAIN-026 |
| CONTRACT-TRAIN-036 | POST | `/wellness-post/training_sessions/{training_session_id}/wellness_post` | `add_wellness_post_to_session_api_v1_wellness_post_training_sessions__training_session_id__wellness_post_post` | `WellnessPostCreate` | `WellnessPost` | EVIDENCIADO | INV-TRAIN-003, INV-TRAIN-010, INV-TRAIN-021 |
| CONTRACT-TRAIN-037 | GET | `/wellness-post/training_sessions/{training_session_id}/wellness_post/status` | `get_wellness_post_status_api_v1_wellness_post_training_sessions__training_session_id__wellness_post_status_get` | — | `{total_athletes, responded_post, pending[], response_rate}` | EVIDENCIADO | (derivado) |
| CONTRACT-TRAIN-038 | GET | `/wellness-post/wellness_post/{wellness_post_id}` | `get_wellness_post_by_id_api_v1_wellness_post_wellness_post__wellness_post_id__get` | — | `WellnessPost` | EVIDENCIADO | INV-TRAIN-026 |
| CONTRACT-TRAIN-039 | PATCH | `/wellness-post/wellness_post/{wellness_post_id}` | `update_wellness_post_api_v1_wellness_post_wellness_post__wellness_post_id__patch` | `WellnessPostUpdate` | `WellnessPost` | EVIDENCIADO | INV-TRAIN-003 |

Gap FE↔BE (crítico):
- `Hb Track - Frontend/src/lib/api/wellness.ts` não usa os paths acima; o contrato FE deve convergir para estes endpoints.

---

### 5.6 Training Cycles / Microcycles

#### Cycles
| ID | Método | Path | operationId | Request | Response | Status | Invariantes-chave |
|---|---|---|---|---|---|---|---|
| CONTRACT-TRAIN-040 | GET | `/training-cycles` | `list_training_cycles_api_v1_training_cycles_get` | filtros `team_id`, `cycle_type`, `status` | `TrainingCycleResponse[]` | EVIDENCIADO | INV-TRAIN-037 |
| CONTRACT-TRAIN-041 | GET | `/training-cycles/{cycle_id}` | `get_training_cycle_api_v1_training_cycles__cycle_id__get` | — | `TrainingCycleWithMicrocycles` | EVIDENCIADO | INV-TRAIN-037 |
| CONTRACT-TRAIN-042 | POST | `/training-cycles` | `create_training_cycle_api_v1_training_cycles_post` | `TrainingCycleCreate` | `TrainingCycleResponse` | EVIDENCIADO | INV-TRAIN-037 |
| CONTRACT-TRAIN-043 | PATCH | `/training-cycles/{cycle_id}` | `update_training_cycle_api_v1_training_cycles__cycle_id__patch` | `TrainingCycleUpdate` | `TrainingCycleResponse` | EVIDENCIADO | INV-TRAIN-037 |
| CONTRACT-TRAIN-044 | DELETE | `/training-cycles/{cycle_id}?reason=` | `delete_training_cycle_api_v1_training_cycles__cycle_id__delete` | query `reason` | 204 | EVIDENCIADO | INV-TRAIN-008 |
| CONTRACT-TRAIN-045 | GET | `/training-cycles/teams/{team_id}/active` | `get_active_cycles_api_v1_training_cycles_teams__team_id__active_get` | — | `TrainingCycleResponse[]` | EVIDENCIADO | (derivado) |

#### Microcycles
| ID | Método | Path | operationId | Request | Response | Status | Invariantes-chave |
|---|---|---|---|---|---|---|---|
| CONTRACT-TRAIN-046 | GET | `/training-microcycles` | `list_training_microcycles_api_v1_training_microcycles_get` | `team_id` obrigatório + filtros | `TrainingMicrocycleResponse[]` | EVIDENCIADO | INV-TRAIN-043 |
| CONTRACT-TRAIN-047 | GET | `/training-microcycles/{microcycle_id}` | `get_training_microcycle_api_v1_training_microcycles__microcycle_id__get` | — | `TrainingMicrocycleWithSessions` | EVIDENCIADO | INV-TRAIN-043 |
| CONTRACT-TRAIN-048 | POST | `/training-microcycles` | `create_training_microcycle_api_v1_training_microcycles_post` | `TrainingMicrocycleCreate` | `TrainingMicrocycleResponse` | EVIDENCIADO | INV-TRAIN-001, INV-TRAIN-043 |
| CONTRACT-TRAIN-049 | PATCH | `/training-microcycles/{microcycle_id}` | `update_training_microcycle_api_v1_training_microcycles__microcycle_id__patch` | `TrainingMicrocycleUpdate` | `TrainingMicrocycleResponse` | EVIDENCIADO | INV-TRAIN-043 |
| CONTRACT-TRAIN-050 | DELETE | `/training-microcycles/{microcycle_id}?reason=` | `delete_training_microcycle_api_v1_training_microcycles__microcycle_id__delete` | query `reason` | 204 | EVIDENCIADO | INV-TRAIN-008 |
| CONTRACT-TRAIN-051 | GET | `/training-microcycles/teams/{team_id}/current` | `get_current_microcycle_api_v1_training_microcycles_teams__team_id__current_get` | query opcional `at_date` | `TrainingMicrocycleResponse` | EVIDENCIADO | (derivado) |
| CONTRACT-TRAIN-052 | GET | `/training-microcycles/{microcycle_id}/summary` | `get_microcycle_summary_api_v1_training_microcycles__microcycle_id__summary_get` | — | `dict` | EVIDENCIADO | INV-TRAIN-020 |

---

### 5.7 Banco de Exercícios + Tags + Favoritos

| ID | Método | Path | operationId | Request | Response | Status |
|---|---|---|---|---|---|---|
| CONTRACT-TRAIN-053 | GET | `/exercises` | `list_exercises_api_v1_exercises_get` | query filtros | `ExerciseListResponse` | EVIDENCIADO |
| CONTRACT-TRAIN-054 | POST | `/exercises` | `create_exercise_api_v1_exercises_post` | `ExerciseCreate` | `Exercise` | EVIDENCIADO |
| CONTRACT-TRAIN-055 | GET | `/exercises/{exercise_id}` | `get_exercise_api_v1_exercises__exercise_id__get` | — | `Exercise` | EVIDENCIADO |
| CONTRACT-TRAIN-056 | PATCH | `/exercises/{exercise_id}` | `update_exercise_api_v1_exercises__exercise_id__patch` | `ExerciseUpdate` | `Exercise` | EVIDENCIADO |
| CONTRACT-TRAIN-057 | GET | `/exercise-tags` | `list_tags_api_v1_exercise_tags_get` | — | `ExerciseTag[]` | EVIDENCIADO |
| CONTRACT-TRAIN-058 | POST | `/exercise-tags` | `create_tag_api_v1_exercise_tags_post` | `ExerciseTagCreate` | `ExerciseTag` | EVIDENCIADO |
| CONTRACT-TRAIN-059 | PATCH | `/exercise-tags/{tag_id}` | `update_tag_api_v1_exercise_tags__tag_id__patch` | `ExerciseTagUpdate` | `ExerciseTag` | EVIDENCIADO |
| CONTRACT-TRAIN-060 | GET | `/exercise-favorites` | `list_my_favorites_api_v1_exercise_favorites_get` | — | `ExerciseFavorite[]` | EVIDENCIADO |
| CONTRACT-TRAIN-061 | POST | `/exercise-favorites` | `favorite_exercise_api_v1_exercise_favorites_post` | `{exercise_id}` | `ExerciseFavorite` | EVIDENCIADO |
| CONTRACT-TRAIN-062 | DELETE | `/exercise-favorites/{exercise_id}` | `unfavorite_exercise_api_v1_exercise_favorites__exercise_id__delete` | — | 204 | EVIDENCIADO |

---

### 5.8 Session Templates

| ID | Método | Path | operationId | Request | Response | Status | Invariantes-chave |
|---|---|---|---|---|---|---|---|
| CONTRACT-TRAIN-063 | GET | `/session-templates` | `list_session_templates_api_v1_session_templates_get` | query `active_only` | `SessionTemplateListResponse` | EVIDENCIADO | INV-TRAIN-035 |
| CONTRACT-TRAIN-064 | POST | `/session-templates` | `create_session_template_api_v1_session_templates_post` | `SessionTemplateCreate` | `SessionTemplate` | EVIDENCIADO | INV-TRAIN-035, INV-TRAIN-001 |
| CONTRACT-TRAIN-065 | GET | `/session-templates/{template_id}` | `get_session_template_api_v1_session_templates__template_id__get` | — | `SessionTemplate` | EVIDENCIADO | — |
| CONTRACT-TRAIN-066 | PATCH | `/session-templates/{template_id}` | `update_session_template_api_v1_session_templates__template_id__patch` | `SessionTemplateUpdate` | `SessionTemplate` | EVIDENCIADO | INV-TRAIN-001 |
| CONTRACT-TRAIN-067 | DELETE | `/session-templates/{template_id}` | `delete_session_template_api_v1_session_templates__template_id__delete` | — | 204 | EVIDENCIADO | — |
| CONTRACT-TRAIN-068 | PATCH | `/session-templates/{template_id}/favorite` | `toggle_favorite_template_api_v1_session_templates__template_id__favorite_patch` | — | `SessionTemplate` | EVIDENCIADO | — |

---

### 5.9 Analytics (treino) + Rankings wellness + Top performers

#### Training analytics
| ID | Método | Path | operationId | Request | Response | Status |
|---|---|---|---|---|---|---|
| CONTRACT-TRAIN-069 | GET | `/analytics/team/{team_id}/summary` | `get_team_summary_api_v1_analytics_team__team_id__summary_get` | query `start_date`, `end_date` | `TeamSummaryResponse` | EVIDENCIADO |
| CONTRACT-TRAIN-070 | GET | `/analytics/team/{team_id}/weekly-load` | `get_weekly_load_api_v1_analytics_team__team_id__weekly_load_get` | query `weeks` | `WeeklyLoadResponse` | EVIDENCIADO |
| CONTRACT-TRAIN-071 | GET | `/analytics/team/{team_id}/deviation-analysis` | `get_deviation_analysis_api_v1_analytics_team__team_id__deviation_analysis_get` | query `start_date`, `end_date` | `DeviationAnalysisResponse` | EVIDENCIADO |
| CONTRACT-TRAIN-072 | GET | `/analytics/team/{team_id}/prevention-effectiveness` | `get_prevention_effectiveness_api_v1_analytics_team__team_id__prevention_effectiveness_get` | query `start_date`, `end_date`, `category` | `PreventionEffectivenessResponse` | EVIDENCIADO |

#### Wellness rankings (SSOT OpenAPI incompleto)
Status: **PARCIAL** (OpenAPI sem schema e service divergente do SSOT em partes).

Shape normativo mínimo (list):
```yaml
TeamWellnessRankingItem:
  team_id: uuid
  team_name: string
  response_rate_pre: number # 0..100
  response_rate_post: number # 0..100
  avg_rate: number # 0..100
  rank: int
  athletes_90plus: int
  calculated_at: datetime
```

| ID | Método | Path | operationId | Response (mínimo) | Status | Observações |
|---|---|---|---|---|---|---|
| CONTRACT-TRAIN-073 | GET | `/analytics/wellness-rankings` | `get_wellness_rankings_api_v1_analytics_wellness_rankings_get` | `TeamWellnessRankingItem[]` | PARCIAL | response_model ausente no router |
| CONTRACT-TRAIN-074 | POST | `/analytics/wellness-rankings/calculate` | `calculate_rankings_manually_api_v1_analytics_wellness_rankings_calculate_post` | `{month_reference, teams_processed, ...}` | PARCIAL | cálculo mensal evidenciado, mas service tem trechos inconsistentes |
| CONTRACT-TRAIN-075 | GET | `/analytics/wellness-rankings/{team_id}/athletes-90plus?month=` | `get_team_athletes_90plus_api_v1_analytics_wellness_rankings__team_id__athletes_90plus_get` | `{athletes:[...], total}` | PARCIAL | implementar via `team_registrations` (SSOT) |

#### Top performers (endpoint em `/teams`)
| ID | Método | Path | operationId | Response (mínimo) | Status |
|---|---|---|---|---|---|
| CONTRACT-TRAIN-076 | GET | `/teams/{team_id}/wellness-top-performers?month=` | `get_team_wellness_top_performers_api_v1_teams__team_id__wellness_top_performers_get` | `{month, team_id, team_name, top_performers:[...]}` | EVIDENCIADO |

---

### 5.10 Alertas e Sugestões (Step 18)

Status: **DIVERGENTE_DO_SSOT** (tipos de IDs em rotas não batem com DB).

SSOT DB:
- `training_alerts.id` é `uuid`, mas rota usa `alert_id: int`.
- `training_suggestions.id` é `uuid`, mas rota usa `suggestion_id: int`.
- `team_id` é `uuid`, mas rotas usam `team_id: int`.

Contratos (AS-IS expostos no OpenAPI; TO-BE deve convergir para UUIDs):

| ID | Método | Path | operationId | Status |
|---|---|---|---|---|
| CONTRACT-TRAIN-077 | GET | `/training/alerts-suggestions/alerts/team/{team_id}/active` | `get_active_alerts_api_v1_training_alerts_suggestions_alerts_team__team_id__active_get` | DIVERGENTE_DO_SSOT |
| CONTRACT-TRAIN-078 | GET | `/training/alerts-suggestions/alerts/team/{team_id}/history` | `get_alert_history_api_v1_training_alerts_suggestions_alerts_team__team_id__history_get` | DIVERGENTE_DO_SSOT |
| CONTRACT-TRAIN-079 | GET | `/training/alerts-suggestions/alerts/team/{team_id}/stats` | `get_alert_stats_api_v1_training_alerts_suggestions_alerts_team__team_id__stats_get` | DIVERGENTE_DO_SSOT |
| CONTRACT-TRAIN-080 | POST | `/training/alerts-suggestions/alerts/{alert_id}/dismiss` | `dismiss_alert_api_v1_training_alerts_suggestions_alerts__alert_id__dismiss_post` | DIVERGENTE_DO_SSOT |
| CONTRACT-TRAIN-081 | GET | `/training/alerts-suggestions/suggestions/team/{team_id}/pending` | `get_pending_suggestions_api_v1_training_alerts_suggestions_suggestions_team__team_id__pending_get` | DIVERGENTE_DO_SSOT |
| CONTRACT-TRAIN-082 | GET | `/training/alerts-suggestions/suggestions/team/{team_id}/history` | `get_suggestion_history_api_v1_training_alerts_suggestions_suggestions_team__team_id__history_get` | DIVERGENTE_DO_SSOT |
| CONTRACT-TRAIN-083 | GET | `/training/alerts-suggestions/suggestions/team/{team_id}/stats` | `get_suggestion_stats_api_v1_training_alerts_suggestions_suggestions_team__team_id__stats_get` | DIVERGENTE_DO_SSOT |
| CONTRACT-TRAIN-084 | POST | `/training/alerts-suggestions/suggestions/{suggestion_id}/apply` | `apply_suggestion_api_v1_training_alerts_suggestions_suggestions__suggestion_id__apply_post` | DIVERGENTE_DO_SSOT |
| CONTRACT-TRAIN-085 | POST | `/training/alerts-suggestions/suggestions/{suggestion_id}/dismiss` | `dismiss_suggestion_api_v1_training_alerts_suggestions_suggestions__suggestion_id__dismiss_post` | DIVERGENTE_DO_SSOT |

---

## 6) Contratos desabilitados no agregador (BLOQUEADO)

> Estes contratos existem como código, mas **não estão expostos** em `Hb Track - Backend/app/api/v1/api.py` e portanto **não aparecem** no `openapi.json` atual.

### 6.1 Exports (Step 23)

Fonte: `Hb Track - Backend/app/api/v1/routers/exports.py`

| ID | Método | Path | operationId | Status | Invariantes-chave |
|---|---|---|---|---|---|
| CONTRACT-TRAIN-086 | POST | `/analytics/export-pdf` | (não exposto no OpenAPI atual) | BLOQUEADO | INV-TRAIN-012 |
| CONTRACT-TRAIN-087 | GET | `/analytics/exports/{job_id}` | (não exposto no OpenAPI atual) | BLOQUEADO | INV-TRAIN-012 |
| CONTRACT-TRAIN-088 | GET | `/analytics/exports` | (não exposto no OpenAPI atual) | BLOQUEADO | INV-TRAIN-012 |
| CONTRACT-TRAIN-089 | GET | `/analytics/export-rate-limit` | (não exposto no OpenAPI atual) | BLOQUEADO | INV-TRAIN-012 |

### 6.2 LGPD — Export de dados do atleta (Step 24)

Fonte: `Hb Track - Backend/app/api/v1/routers/athlete_export.py`

| ID | Método | Path | operationId | Status | Invariantes-chave |
|---|---|---|---|---|---|
| CONTRACT-TRAIN-090 | GET | `/athletes/me/export-data?format=json|csv` | (não exposto no OpenAPI atual) | BLOQUEADO | INV-TRAIN-025 |

---

## 7) Divergências e Gaps (paridade)

### GAP-CONTRACT-1 — Wellness FE aponta para endpoints errados
- FE chama `/wellness_pre` e `/wellness_post` sem prefixo `/wellness-pre|/wellness-post`.
- Contrato normativo exige `CONTRACT-TRAIN-029..039`.

### GAP-CONTRACT-2 — Rankings wellness e TopPerformers usam tipos errados no FE
- FE trata `team_id` como `number` e usa `parseInt` em rotas.
- SSOT DB define `teams.id` como UUID.

### GAP-CONTRACT-3 — Alertas/Sugestões Step 18 com IDs `int` vs DB `uuid`
- Endpoint exposto, mas incompatível com schema (team_id/alert_id/suggestion_id).
- Deve ser tratado como **bloqueante** para qualquer UI que dependa dessas rotas.

### GAP-CONTRACT-4 — OpenAPI incompleto para rankings
- Endpoints de rankings (`/analytics/wellness-rankings*`) não têm response_model, gerando schema `{}`.
- Este documento define o shape mínimo normativo até o contrato ser tipado.

### GAP-CONTRACT-5 — Exports/LGPD routers existem mas estão desabilitados
- UI existe para export PDF, invariantes existem, mas as rotas não estão incluídas no agregador v1.

---

## 8) Proposta fora do PRD — não normativa

### “Training Suggestions” (planejamento inteligente)

Há um router em `Hb Track - Backend/app/api/v1/routers/training_suggestions.py`, e chamadas no FE (`/training-suggestions`), porém:
- não está exposto no agregador v1 (não aparece no OpenAPI SSOT),
- PRD marca recomendador de treinos como futuro.

Portanto, **não** entra como contrato normativo do MCP TRAINING nesta fase.
