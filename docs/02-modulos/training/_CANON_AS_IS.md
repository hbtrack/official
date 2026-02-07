<!-- STATUS: VERIFIED | evidencia: _generated/openapi.json, _generated/schema.sql, _generated/alembic_state.txt -->

# Training Module - Canon AS-IS

## Fontes Canonicas

| Artefato | Localizacao | Evidencia |
|---|---|---|
| API Endpoints | `docs/_generated/openapi.json` | `paths["/api/v1/analytics/wellness-rankings"]`, `paths["/api/v1/reports/training-performance"]`, `paths["/api/v1/session-templates"]`, `paths["/api/v1/training-sessions"]`, `paths["/api/v1/wellness-pre/wellness_pre/{wellness_pre_id}/request-unlock"]` |
| Schemas/DTOs | `docs/_generated/openapi.json` | `components.schemas["TrainingSession"]`, `components.schemas["SessionTemplateResponse"]`, `components.schemas["WellnessSummaryReport"]` |
| DB Schema | `docs/_generated/schema.sql` | `CREATE TABLE public.training_sessions`, `CREATE TABLE public.training_cycles`, `CREATE TABLE public.wellness_reminders` |
| Alembic State | `docs/_generated/alembic_state.txt` | `=== ALEMBIC HEADS ===`, `=== ALEMBIC CURRENT ===` |

---

## Endpoints Verificados (openapi.json)

| Grupo | Path (literal) | Métodos |
|---|---|---|
| Analytics | `/api/v1/analytics/wellness-rankings` | GET |
| Analytics | `/api/v1/analytics/wellness-rankings/calculate` | POST |
| Analytics | `/api/v1/analytics/wellness-rankings/{team_id}/athletes-90plus` | GET |
| Reports | `/api/v1/reports/refresh-training-performance` | POST |
| Reports | `/api/v1/reports/team-training-game-correlation` | GET |
| Reports | `/api/v1/reports/training-performance` | GET |
| Reports | `/api/v1/reports/training-trends` | GET |
| Reports | `/api/v1/reports/wellness-summary` | GET |
| Reports | `/api/v1/reports/wellness-trends` | GET |
| Session Templates | `/api/v1/session-templates` | GET, POST |
| Session Templates | `/api/v1/session-templates/{template_id}` | GET, PATCH, DELETE |
| Session Templates | `/api/v1/session-templates/{template_id}/favorite` | PATCH |
| Training Sessions (team-scoped) | `/api/v1/teams/{team_id}/trainings` | GET, POST |
| Training Sessions (team-scoped) | `/api/v1/teams/{team_id}/trainings/{training_id}` | GET, PATCH, DELETE |
| Training Sessions (team-scoped) | `/api/v1/teams/{team_id}/trainings/{training_id}/restore` | POST |
| Wellness (team-scoped) | `/api/v1/teams/{team_id}/wellness-top-performers` | GET |
| Training Cycles | `/api/v1/training-cycles` | GET, POST |
| Training Cycles | `/api/v1/training-cycles/teams/{team_id}/active` | GET |
| Training Cycles | `/api/v1/training-cycles/{cycle_id}` | GET, PATCH, DELETE |
| Training Microcycles | `/api/v1/training-microcycles` | GET, POST |
| Training Microcycles | `/api/v1/training-microcycles/teams/{team_id}/current` | GET |
| Training Microcycles | `/api/v1/training-microcycles/{microcycle_id}` | GET, PATCH, DELETE |
| Training Microcycles | `/api/v1/training-microcycles/{microcycle_id}/summary` | GET |
| Training Sessions (global) | `/api/v1/training-sessions` | GET, POST |
| Training Sessions (global) | `/api/v1/training-sessions/copy-week` | POST |
| Session Exercises | `/api/v1/training-sessions/exercises/{session_exercise_id}` | PATCH, DELETE |
| Session Exercises | `/api/v1/training-sessions/{session_id}/exercises` | GET, POST |
| Session Exercises | `/api/v1/training-sessions/{session_id}/exercises/bulk` | POST |
| Session Exercises | `/api/v1/training-sessions/{session_id}/exercises/reorder` | PATCH |
| Training Sessions (global) | `/api/v1/training-sessions/{training_session_id}` | GET, PATCH, DELETE |
| Training Sessions (global) | `/api/v1/training-sessions/{training_session_id}/close` | POST |
| Training Sessions (global) | `/api/v1/training-sessions/{training_session_id}/deviation` | GET |
| Training Sessions (global) | `/api/v1/training-sessions/{training_session_id}/duplicate` | POST |
| Training Sessions (global) | `/api/v1/training-sessions/{training_session_id}/publish` | POST |
| Training Sessions (global) | `/api/v1/training-sessions/{training_session_id}/restore` | POST |
| Training Sessions (global) | `/api/v1/training-sessions/{training_session_id}/wellness-status` | GET |
| Alerts & Suggestions | `/api/v1/training/alerts-suggestions/alerts/team/{team_id}/active` | GET |
| Alerts & Suggestions | `/api/v1/training/alerts-suggestions/alerts/team/{team_id}/history` | GET |
| Alerts & Suggestions | `/api/v1/training/alerts-suggestions/alerts/team/{team_id}/stats` | GET |
| Alerts & Suggestions | `/api/v1/training/alerts-suggestions/alerts/{alert_id}/dismiss` | POST |
| Alerts & Suggestions | `/api/v1/training/alerts-suggestions/suggestions/team/{team_id}/history` | GET |
| Alerts & Suggestions | `/api/v1/training/alerts-suggestions/suggestions/team/{team_id}/pending` | GET |
| Alerts & Suggestions | `/api/v1/training/alerts-suggestions/suggestions/team/{team_id}/stats` | GET |
| Alerts & Suggestions | `/api/v1/training/alerts-suggestions/suggestions/{suggestion_id}/apply` | POST |
| Alerts & Suggestions | `/api/v1/training/alerts-suggestions/suggestions/{suggestion_id}/dismiss` | POST |
| Attendance | `/api/v1/training_sessions/{training_session_id}/attendance` | GET, POST |
| Attendance | `/api/v1/training_sessions/{training_session_id}/attendance/batch` | POST |
| Attendance | `/api/v1/training_sessions/{training_session_id}/attendance/statistics` | GET |
| Wellness Post | `/api/v1/wellness-post/training_sessions/{training_session_id}/wellness_post` | GET, POST |
| Wellness Post | `/api/v1/wellness-post/training_sessions/{training_session_id}/wellness_post/status` | GET |
| Wellness Post | `/api/v1/wellness-post/wellness_post/{wellness_post_id}` | GET, PATCH |
| Wellness Pre | `/api/v1/wellness-pre/training_sessions/{training_session_id}/wellness_pre` | GET, POST |
| Wellness Pre | `/api/v1/wellness-pre/training_sessions/{training_session_id}/wellness_pre/status` | GET |
| Wellness Pre | `/api/v1/wellness-pre/wellness_pre/{wellness_pre_id}` | GET, PATCH |
| Wellness Pre | `/api/v1/wellness-pre/wellness_pre/{wellness_pre_id}/request-unlock` | POST |

---

## Schemas/DTOs Verificados (components.schemas)

components.schemas["AlertListResponse"]
components.schemas["AlertResponse"]
components.schemas["AlertStatsResponse"]
components.schemas["AthleteAttendanceMetrics"]
components.schemas["AthleteAttendanceRecord"]
components.schemas["AthleteIndividualReport"]
components.schemas["AthleteTrainingLoadMetrics"]
components.schemas["AthleteWellnessMetrics"]
components.schemas["Attendance"]
components.schemas["AttendanceCorrection"]
components.schemas["AttendanceCreate"]
components.schemas["AttendanceReportResponse"]
components.schemas["AttendanceUpdate"]
components.schemas["DashboardAlert"]
components.schemas["DashboardNextTraining"]
components.schemas["DashboardTrainingSession"]
components.schemas["DashboardTrainingStats"]
components.schemas["DashboardTrainingTrend"]
components.schemas["DashboardWellnessStats"]
components.schemas["LoadReportResponse"]
components.schemas["MedicalCasesReport"]
components.schemas["MinutesReportResponse"]
components.schemas["ScopedTrainingSessionCreate"]
components.schemas["SessionClosureFieldErrors"]
components.schemas["SessionClosureResponse"]
components.schemas["SessionClosureValidationResult"]
components.schemas["SessionExerciseBulkCreate"]
components.schemas["SessionExerciseCreate"]
components.schemas["SessionExerciseListResponse"]
components.schemas["SessionExerciseReorder"]
components.schemas["SessionExerciseReorderItem"]
components.schemas["SessionExerciseResponse"]
components.schemas["SessionExerciseUpdate"]
components.schemas["SessionTemplateCreate"]
components.schemas["SessionTemplateListResponse"]
components.schemas["SessionTemplateResponse"]
components.schemas["SessionTemplateUpdate"]
components.schemas["SessionTypeEnum"]
components.schemas["SuggestionApply"]
components.schemas["SuggestionDismiss"]
components.schemas["SuggestionListResponse"]
components.schemas["SuggestionResponse"]
components.schemas["SuggestionStatsResponse"]
components.schemas["TeamTrainingGameCorrelationResponse"]
components.schemas["TrainingCycleCreate"]
components.schemas["TrainingCycleResponse"]
components.schemas["TrainingCycleUpdate"]
components.schemas["TrainingCycleWithMicrocycles"]
components.schemas["TrainingExecutionOutcome"]
components.schemas["TrainingFocusDistribution"]
components.schemas["TrainingMicrocycleCreate"]
components.schemas["TrainingMicrocycleResponse"]
components.schemas["TrainingMicrocycleUpdate"]
components.schemas["TrainingMicrocycleWithSessions"]
components.schemas["TrainingPerformanceMetrics"]
components.schemas["TrainingPerformanceReport"]
components.schemas["TrainingPerformanceTrend"]
components.schemas["TrainingSession"]
components.schemas["TrainingSessionCreate"]
components.schemas["TrainingSessionPaginatedResponse"]
components.schemas["TrainingSessionResponse"]
components.schemas["TrainingSessionUpdate"]
components.schemas["WellnessAthleteData"]
components.schemas["WellnessPost"]
components.schemas["WellnessPostCreate"]
components.schemas["WellnessPostData"]
components.schemas["WellnessPostUpdate"]
components.schemas["WellnessPre"]
components.schemas["WellnessPreCreate"]
components.schemas["WellnessPreData"]
components.schemas["WellnessPreUpdate"]
components.schemas["WellnessSessionStats"]
components.schemas["WellnessStatusResponse"]
components.schemas["WellnessSummaryMetrics"]
components.schemas["WellnessSummaryReport"]

---

## Tabelas/Entidades Relacionadas (schema.sql)

CREATE TABLE public.attendance
CREATE TABLE public.session_templates
CREATE TABLE public.training_alerts
CREATE TABLE public.training_analytics_cache
CREATE TABLE public.training_cycles
CREATE TABLE public.training_microcycles
CREATE TABLE public.training_session_exercises
CREATE TABLE public.training_sessions
CREATE TABLE public.training_suggestions
CREATE TABLE public.wellness_post
CREATE TABLE public.wellness_pre
CREATE TABLE public.wellness_reminders

---

## Checklist minimo para revalidar

- Regenerar _generated (generate_docs.py --all).
- Re-checar endpoints/schemas/tabelas listadas em `docs/_generated/openapi.json` e `docs/_generated/schema.sql`.

---

## Alembic heads/current (alembic_state.txt)

```
=== ALEMBIC HEADS ===
0052 (head)

=== ALEMBIC CURRENT ===
(no output)
```
