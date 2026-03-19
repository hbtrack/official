# Roadmap de Implementação — 17 Módulos do HB Track
> Data: 2026-03-19 (final) | Original: 2026-03-17
> Versão: 1.20.0 | Status: 15/17 `validated_contract`; 1 `implementation_ready` (training); 1 `draft_contract` (video)
> Autoridade: MODULE_REGISTRY.yaml | Última atualização: Video FASE 2-4 PASS; Testes TM-001..008 (36/36 PASS)

---

## 📊 Visão Geral

| Status | Qtd | Módulos | Próximo Passo |
|---|---|---|---|
| 🟢 **implementation_ready** | 1 | training | Geração de código backend (Django + Celery) |
| 🟢 **validated_contract** | 15 | users, exercises, identity_access, notifications, wellness, teams, ai_ingestion, seasons, competitions, matches, audit, scout, medical, analytics, reports | AsyncAPI v1.1, state models v1.1, boundary contracts |
| 🟡 **draft_contract** | 1 | video | Testes Django TM-001..008 PASS (36/36); design backend 1-2 sprints |
| 🔴 **scaffold** | 0 | — | — |
| 🔴 **stub_contract** | 0 | — | — |

---

## 🟢 Status: implementation_ready

### **training** — `implementation_ready` (owner: performance-tech)

> Contratos completos. Stack completa decidida. Análise adversarial 9/10 resolvida.
> Sign-off UI contract aprovado. ADR-031 (Scope Boundary) implementado e validado em 2026-03-18.

**Superfícies (12/12):**
- ✅ module_docs_minimum
- ✅ openapi_sync (training.yaml — 4076 linhas; 34+ endpoints)
- ✅ json_schema (14 schemas)
- ✅ test_matrix (TM-001..TM-110 + TM-200..TM-231 + TM-300..TM-322 + TM-400..TM-410)
- ✅ state_model (ADR-017 + matriz proibida RC-1)
- ✅ permissions (RBAC 5 roles)
- ✅ errors (19+ códigos)
- ✅ sport_science (ACSM/ASPETAR)
- ✅ ui_contract (UI_CONTRACT_TRAINING.md v1.1.0)
- ✅ arazzo (5 workflows)
- ✅ asyncapi (28/28 eventos — todos channels em contracts/asyncapi/channels/)
- ✅ decision_ir (TRAINING_MODULE_DECISION_IR.yaml + ARCH_DECISIONS_TRAINING.md)

**Stack tecnológica (100% decidida):**
- Backend: Python 3.12 + Django 5.x + Django Ninja 1.x (ADR-031)
- DB: PostgreSQL 16 + Django ORM + Django Migrations
- Tasks: Celery 5.x + Redis 7 · WebSocket: Django Channels 4.x
- Frontend: Next.js 14 (App Router) + PWA (ADR-030)

**Implementações 2026-03-18:**
- ✅ ADR-031 Scope Boundary Validation — 16/16 módulos passando, A8 bloqueada
- ✅ securitySchemes HTTPBearer adicionado ao openapi.yaml raiz
- ✅ description adicionada em 8 operações sem ela (exercises + training)
- ✅ reasonOther e readinessAvg aceitam null nos schemas (OpenAPI 3.1 type array)
- ✅ AsyncAPI 28/28 channels gerados e validados
- ✅ Context Efficiency Audit: boot a 63.4% do budget (5/5 critérios PASS)

---

## � Status: validated_contract

Módulos com DC1-DC5 PASS (pipeline de gates aprovado). Contratos abertos e sintaticamente válidos. Gaps restantes não bloqueiam `validated_contract` mas são necessários para `implementation_ready`.

---

### **users** — `validated_contract` (owner: platform-core)

> Promovido em 2026-03-18. OpenAPI com 4 endpoints + user_profile.yaml. DC1-DC5 PASS.
> Enriquecido em 2026-03-19: asyncapi (user.created + user.role_changed), arazzo (user_invitation),
> PERMISSIONS_USERS.md, DECISION_IR_USERS.yaml. statusLabel adicionado ao schema (DEC-USERS-002).
> Decisions: DEC-USERS-001 (C: eventos), DEC-USERS-002 (B: invitation), DEC-USERS-003 (B: admin+coordinator).

**Superfícies (8/12):**
- ✅ module_docs (DOMAIN_RULES, INVARIANTS, MODULE_SCOPE, TEST_MATRIX, README)
- ✅ openapi_sync (users.yaml — 4 endpoints: listUsers, createUser, getUser, patchUser; statusLabel adicionado)
- ✅ json_schema (2 schemas: user_profile.yaml + base schema; statusLabel enum adicionado)
- ✅ test_matrix
- ✅ permissions (PERMISSIONS_USERS.md — 10 regras PERM-USR-001..010; listUsers, createUser, patchUser.roleLabel)
- ✅ arazzo (1 workflow: user_invitation — invite→activate→linkTeams; DEC-USERS-002=B)
- ✅ asyncapi (2 canais: user.created + user.role_changed + messages + payloads; DEC-USERS-001=C)
- ✅ decision_ir (DECISION_IR_USERS.yaml — DEC-USERS-001/002/003)
- — state_model (não esperado para users CRUD)
- — sport_science (não aplicável)
- — ui_contract (não esperado v0)
- — errors (gap futuro)

### **exercises** — `validated_contract` (owner: platform-core)

> Promovido em 2026-03-18. PERMISSIONS_EXERCISES.md + DECISION_IR_EXERCISES.yaml criados. Arazzo de versionamento já existia (2 workflows). DC1-DC5 PASS.

**Superfícies (7/12):**
- ✅ module_docs (DOMAIN_RULES, INVARIANTS, MODULE_SCOPE, TEST_MATRIX, README)
- ✅ openapi_sync (exercises.yaml — 1007 linhas; 14 endpoints)
- ✅ json_schema (4 schemas: exercise, exercise_preview, exercise_version, exercise_relation)
- ✅ test_matrix
- ✅ permissions (PERMISSIONS_EXERCISES.md — editor de catálogo: coordinator/admin)
- ✅ arazzo (2 workflows: versionamento de exercício)
- ✅ decision_ir (DECISION_IR_EXERCISES.yaml)
- — state_model (não esperado para exercícios)
- — sport_science (não esperado)
- — ui_contract (não esperado)
- — asyncapi (não esperado)

---

### **identity_access** — `validated_contract` (owner: platform-core)

> Promovido em 2026-03-19. OpenAPI completo (547L, 9 endpoints). Schema auth_session.yaml criado. Arazzo assign_role_to_user desbloqueado. DC1-DC5 PASS.
> ADR-007 (JWT RS256) + ADR-008 (RBAC 5 roles) + ADR-031 (Django stack) aplicados.

**Superfícies (8/12):**
- ✅ module_docs (DOMAIN_RULES, INVARIANTS, MODULE_SCOPE, TEST_MATRIX, README)
- ✅ openapi_sync (identity_access.yaml — 547 linhas; 9 endpoints: login, logout, refresh, me, sessions, revokeSession, listRoles, assignRole, revokeRole)
- ✅ json_schema (2: auth_session.schema.json + auth_session.yaml OpenAPI)
- ✅ test_matrix
- ✅ arazzo (1 workflow: assign_role_to_user — desbloqueado)
- ✅ permissions (RBAC enforcement documentado via ADR-008 no contrato)
- ✅ asyncapi (4 canais: session.created, session.revoked, role.assigned, role.revoked — DEC-IAM-003=C)
- ✅ decision_ir (DECISION_IR_IDENTITY_ACCESS.yaml — DEC-IAM-001=B MFA opt-in, DEC-IAM-002=B Redis denylist, DEC-IAM-003=C 4 eventos)
- — state_model (não esperado)

---

### **notifications** — `validated_contract` (owner: platform-core)

> Promovido em 2026-03-19. OpenAPI completo (5 endpoints). Schemas notification_delivery.yaml + notification_preferences.yaml criados. 3 canais AsyncAPI (queued/sent/failed). Arazzo event_to_notification_delivery desbloqueado. Pipeline 10/10 PASS.
> ADR-031 (Celery 5 + Redis 7), DR-NTF-001..005 + INV-NTF-001..005 aplicados.

**Superfícies (6/12):**
- ✅ module_docs (DOMAIN_RULES, INVARIANTS, MODULE_SCOPE, TEST_MATRIX, README)
- ✅ openapi_sync (notifications.yaml — 5 endpoints: createNotificationIntent, listDeliveries, getDelivery, getUserNotificationPreferences, updateUserNotificationPreferences)
- ✅ json_schema (3: notification_delivery.schema.json + notification_delivery.yaml + notification_preferences.yaml OpenAPI)
- ✅ test_matrix
- ✅ asyncapi (3 canais: notification.delivery.queued/sent/failed + 3 messages + 3 payloads)
- ✅ arazzo (1 workflow: event_to_notification_delivery — desbloqueado)
- — permissions (PERMISSIONS_NOTIFICATIONS.md — gap a fechar)
- — decision_ir (gap a fechar)
- — state_model (não esperado)

---

### **wellness** — `validated_contract` (owner: performance-tech)

> Promovido em 2026-03-19. OpenAPI completo (5 endpoints). Schemas wellness_entry.yaml + wellness_summary.yaml criados. Canal AsyncAPI wellness.entry.created. Arazzo athlete_wellness_tracking criado. Pipeline 10/10 PASS.
> DR-WELL-001..005 + INV-WELL-001..005 + WELLNESS_MEDICAL_BOUNDARY_GATE aplicados.

**Superfícies (6/12):**
- ✅ module_docs (DOMAIN_RULES, INVARIANTS, MODULE_SCOPE, TEST_MATRIX, README)
- ✅ openapi_sync (wellness.yaml — 5 endpoints: createWellnessEntry, listWellnessEntries, getWellnessEntry, listAthleteWellnessEntries, getAthleteWellnessSummary)
- ✅ json_schema (3: wellness_entry.schema.json + wellness_entry.yaml + wellness_summary.yaml OpenAPI)
- ✅ test_matrix
- ✅ asyncapi (1 canal: wellness.entry.created + message + payload)
- ✅ arazzo (1 workflow: athlete_wellness_tracking)
- ✅ sport_science (ACSM/ASPETAR — readiness, fadiga, sono documentados)
- — permissions (PERMISSIONS_WELLNESS.md — gap a fechar)
- — decision_ir (gap a fechar)
- — state_model (não esperado para wellness entries)

---
### **teams** — `validated_contract` (owner: handball-ops)

> Promovido em 2026-03-19. OpenAPI completo (8 endpoints). Schema team.yaml com statusLabel (DRAFT/ACTIVE/ARCHIVED). 2 canais AsyncAPI (team.created, team.roster_updated). Arazzo team_roster_management criado. Pipeline 10/10 PASS.
> DR-TEAM-001..005 + INV-TEAM-001..004 aplicados. Boundary com seasons (seasonId como FK), identity_access (categoryLabel ≠ authz role) e users (vínculos explícitos per DR-TEAM-002) documentados.

**Superfícies (6/12):**
- ✅ module_docs (DOMAIN_RULES, INVARIANTS, MODULE_SCOPE, TEST_MATRIX, README)
- ✅ openapi_sync (teams.yaml — 8 endpoints: listTeams, createTeam, getTeam, patchTeam, addAthleteToTeam, removeAthleteFromTeam, addStaffToTeam, removeStaffFromTeam)
- ✅ json_schema (1: team.schema.json + team.yaml OpenAPI schema com statusLabel)
- ✅ test_matrix
- ✅ asyncapi (2 canais: team.created + team.roster_updated com messages + payloads)
- ✅ arazzo (1 workflow: team_roster_management — create→addAthlete→addStaff)
- — permissions (PERMISSIONS_TEAMS.md — gap a fechar)
- — decision_ir (gap a fechar)

---

### **ai_ingestion** — `validated_contract` (owner: platform-core)

> Promovido em 2026-03-19. OpenAPI completo (4 endpoints). Schema ingestion_job.yaml com statusLabel (queued/processing/completed/failed). 3 canais AsyncAPI (ai_ingestion.job.queued/completed/failed). Arazzo ingestion_job_lifecycle criado. Pipeline 10/10 PASS.
> DR-ING-001..005 + INV-ING-001..005 aplicados.
> Boundaries críticos: parser implícito proibido (DR-ING-002); causalidade receivedAt ≠ completedAt (DR-ING-003); idempotencyKey obrigatório para replay (DR-ING-004); soberania do dado pertence ao módulo de destino (DR-ING-005).

**Superfícies (6/12):**
- ✅ module_docs (DOMAIN_RULES, INVARIANTS, MODULE_SCOPE, TEST_MATRIX, README)
- ✅ openapi_sync (ai_ingestion.yaml — 4 endpoints: listIngestionJobs, createIngestionJob, getIngestionJob, retryIngestionJob)
- ✅ json_schema (1: ingestion_job.schema.json + ingestion_job.yaml OpenAPI schema com statusLabel)
- ✅ test_matrix
- ✅ asyncapi (3 canais: ai_ingestion.job.queued/completed/failed + messages + payloads)
- ✅ arazzo (1 workflow: ingestion_job_lifecycle — create→monitor→retry)
- — permissions (não esperado para este status)
- — decision_ir (gap a fechar futuramente)

---

### **seasons** — `validated_contract` (owner: handball-ops)

> Promovido em 2026-03-19. OpenAPI completo (6 endpoints). Schema season.yaml com statusLabel (draft/active/archived), phaseLabels, teamIds, competitionIds. 2 canais AsyncAPI (season.created, season.status_updated). Arazzo season_lifecycle criado. Pipeline 10/10 PASS.
> DR-SEAS-001..005 + INV-SEAS-001..004 aplicados.
> Boundaries críticos: phaseLabels explícitos, nunca inferidos de resultados (DR-SEAS-002); teamIds/competitionIds como associações canônicas explícitas (DR-SEAS-003); seasons não é dono de scorekeeping nem scout (DR-SEAS-005).

**Superfícies (6/12):**
- ✅ module_docs (DOMAIN_RULES, INVARIANTS, MODULE_SCOPE, TEST_MATRIX, README)
- ✅ openapi_sync (seasons.yaml — 6 endpoints: listSeasons, createSeason, getSeason, patchSeason, addTeamToSeason, removeTeamFromSeason)
- ✅ json_schema (2: season.schema.json atualizado + season.yaml OpenAPI schema com statusLabel)
- ✅ test_matrix
- ✅ asyncapi (2 canais: season.created + season.status_updated + messages + payloads)
- ✅ arazzo (1 workflow: season_lifecycle — create→addTeam→activate)
- — permissions (gap a fechar futuramente)
- — decision_ir (gap a fechar futuramente)
- — state_model (statusLabel embutido no schema; state model formal é gap futuro)

---

### **competitions** — `validated_contract` (owner: handball-ops)

> Promovido em 2026-03-19. OpenAPI completo (6 endpoints). Schema competition.yaml com statusLabel (draft/active/archived), stageLabels, registrationTeamIds, standingsSummary. 2 canais AsyncAPI (competition.created, competition.phase_changed). Arazzo competition_lifecycle criado. Pipeline 10/10 PASS.
> DR-COMP-001..005 + INV-COMP-001..004 aplicados.
> Boundaries críticos: seasonId obrigatório — competição sem temporada é inválida (DR-COMP-002); registrationTeamIds como inscrição formal, não inferida de histórico (DR-COMP-003); stageLabels explícitos, nunca inferidos de resultados (DR-COMP-004); standingsSummary é projeção resumida, não truth oficial de partidas (DR-COMP-005).

**Superfícies (6/12):**
- ✅ module_docs (DOMAIN_RULES, INVARIANTS, MODULE_SCOPE, TEST_MATRIX, README)
- ✅ openapi_sync (competitions.yaml — 6 endpoints: listCompetitions, createCompetition, getCompetition, patchCompetition, registerTeamInCompetition, unregisterTeamFromCompetition)
- ✅ json_schema (2: competition.schema.json atualizado + competition.yaml OpenAPI schema com statusLabel)
- ✅ test_matrix
- ✅ asyncapi (2 canais: competition.created + competition.phase_changed + messages + payloads)
- ✅ arazzo (1 workflow: competition_lifecycle — create→registerTeam→activate)
- — permissions (gap a fechar futuramente)
- — decision_ir (gap a fechar futuramente)
- — state_model (statusLabel embutido no schema; state model formal é gap futuro)

---

### **matches** — `validated_contract` (owner: handball-ops)

> Promovido em 2026-03-19. OpenAPI completo (6 endpoints + 2 ação lineup). Schema match.yaml com statusLabel em 9 fases HBR-013 (DEC-MATCHES-002). CRUD simples (DEC-MATCHES-001). 2 canais AsyncAPI (match.scheduled, match.status_updated). Arazzo match_lifecycle criado. Pipeline 10/10 PASS.
> DR-MATCH-001..005 + INV-MATCH-001..005 aplicados. MatchId registrado em CANONICAL_TYPE_REGISTRY.
> Decisions: DECISION_IR_MATCHES.yaml (.contract_driven/decisions/) — DEC-MATCHES-001 (CRUD) + DEC-MATCHES-002 (9 fases HBR-013).
> Boundaries críticos: competitionId obrigatório — partida sem competição é inválida (DR-MATCH-001); homeTeamId ≠ awayTeamId — lados nunca colapsam (DR-MATCH-002); lineupUserIds = elenco oficial, não substituível por scout (DR-MATCH-003); scheduledAt/startedAt/endedAt = ciclo temporal (DR-MATCH-004); eventos observacionais/clipping pertencem a scout (DR-MATCH-005).

**Superfícies (6/12):**
- ✅ module_docs (DOMAIN_RULES, INVARIANTS, MODULE_SCOPE, TEST_MATRIX, README)
- ✅ openapi_sync (matches.yaml — 6 endpoints: listMatches, createMatch, getMatch, patchMatch, addPlayerToLineup, removePlayerFromLineup)
- ✅ json_schema (2: match.schema.json atualizado + match.yaml OpenAPI schema com statusLabel 9 fases)
- ✅ test_matrix
- ✅ asyncapi (2 canais: match.scheduled + match.status_updated + messages + payloads)
- ✅ arazzo (1 workflow: match_lifecycle — schedule→addLineup→start→complete)
- ✅ decision_ir (DECISION_IR_MATCHES.yaml — DEC-MATCHES-001 CRUD + DEC-MATCHES-002 HBR fases)
- — permissions (gap a fechar futuramente)
- — state_model (statusLabel embutido no schema; state model formal é gap futuro)

---
## 🟡 Status: draft_contract

### **video** — `draft_contract` (owner: platform-core)

> Contrato técnico completo em 2026-03-19. Promovido de `scaffold` → `draft_contract` após FASE 2-4 validação.
> Testes Django TM-001..008 implementados: 36/36 PASS.
> Próximo: Design backend (models + views) → FASE 5 Handoff → `validated_contract` candidato após implementation tests.

**Superfícies (8/8 — 100%):**
- ✅ module_docs (5 arquivos: README, MODULE_SCOPE, DOMAIN_RULES, INVARIANTS, TEST_MATRIX)
- ✅ openapi_sync (contracts/openapi/paths/video.yaml — 650 linhas, 7 endpoints)
- ✅ json_schema (4 schemas: match_media_session, media_segment, clip_definition, distribution_profile)
- ✅ asyncapi (6 canais: capture.started, segment.ready, transcode.completed, distribution.published/failed, sync.adjustment_applied)
- ✅ state_model (STATE_MODEL_VIDEO.md — 5 estados, 7 transições, 12 invariants)
- ✅ permissions (PERMISSIONS_VIDEO.md — 10 operações, RBAC 5-tier)
- ✅ arazzo (3 workflows: capture_and_sync, transcode_and_publish, semantic_clipping)
- ✅ decision_ir (ADR-033 — Video Module Canonicalization; 17º módulo canônico)

**Validação Contract Gates (FASE 3):**
- ✅ Contract gates: 44/44 PASS (9 PASS, 32 SKIP not applicable, 0 FAIL)
- ✅ DERIVED_DRIFT_GATE: PASS (manifests recompiled)
- ✅ READINESS_SUMMARY_GATE: PASS (8/8 superfícies completas)
- ✅ MODULE_STATUS_COHERENCE_GATE: PASS (video: draft_contract)

**Testes Django (Test Implementation Suite):**
- ✅ tests/test_video_module.py — 36 testes completados
  - **TM-001:** Contract Linting OpenAPI (4 testes)
  - **TM-002:** JSON Schema Validation (5 testes)
  - **TM-003:** Domain Rules (4 testes, 10 rules DR-VID-001..010)
  - **TM-004:** Invariants (4 testes, 12 invariants INV-VID-001..012)
  - **TM-005:** Capture Functional (4 testes: session creation, DRAFT→CAPTURING, segment ingest, timecode monotônico)
  - **TM-006:** Transcode Functional (5 testes: codec support H.264/H.265/VP9/AV1, bitrate constraints)
  - **TM-007:** Timecode Sync (3 testes: scout SSOT, divergence >100ms, sync resolution monotônica)
  - **TM-008:** Distribution & Audit (5 testes: clip context, distribution CDN/broadcast, audit logging, idempotence)
  - **Integration:** 2 testes (contract gates PASS, state model consistency)
- ✅ Resultado: 36 PASS, 0 FAIL, 2 SKIP (allowed)
- ✅ Relatório formal: _reports/VIDEO_TEST_RESULTS_20260319.md

**Próximos Passos (Backend Design):**
1. **Design Backend (1-2 sprints):**
   - Django models: MatchMediaSession, MediaSegment, ClipDefinition, DistributionProfile
   - Django Ninja views: 7 endpoints conforme OpenAPI contract
   - Celery tasks: Transcode pipeline (H.264, H.265, VP9, AV1)
   - AsyncAPI consumers: Scout timecode sync events, analytics clip queries

2. **Boundary Integration:**
   - video↔scout: Timecode synchronization (INV-VID-010) via AsyncAPI
   - video↔analytics: Clip range queries com contexto semântico
   - video↔training: Session playback context para periodização

3. **Promotion Path:**
   - Backend implementation + integration tests (2-3 sprints)
   - Promote to `validated_contract` (após implementation-ready criteria)
   - Full `implementation_ready` (edge orchestration + CDN deployment)

---
## � Status: scaffold

*Nenhum módulo neste status atualmente.*

---
## �🔴 Status: stub_contract

Módulos com apenas stubs de contrato (8–12 linhas de OpenAPI placeholder). Precisam de desenvolvimento real.

---

### **Grupo 1: Core Platform (owner: platform-core)**

#### **identity_access** [auth, authz, roles, permissions]
✅ **validated_contract** — promovido 2026-03-19 (ver seção correspondente acima)

#### **ai_ingestion** [recommendation engine, signal processing]
✅ **validated_contract** — promovido 2026-03-19 (ver seção correspondente acima)

#### **audit** [event logging, trail records, compliance]
✅ **validated_contract** — promovido 2026-03-19 (4 endpoints + 2 eventos AsyncAPI + arazzo + permissions + decision_ir)
- DEC-AUD-001: GET /audit/entries + POST /audit/entries + GET /audit/entries/export + GET /audit/entries/{entryId}
- DEC-AUD-002: admin irrestrito; coordinator com filtro obrigatório teamId/organizationId
- DEC-AUD-003: audit.entry.created + audit.entry.security_flagged (severity: low/medium/high/critical)

#### **notifications** [push, email, sms, in-app]
✅ **validated_contract** — promovido 2026-03-19 (ver seção correspondente acima)

---

### **Grupo 2: Handball Operations (owner: handball-ops)**

#### **seasons** [macrocycle, mesocycle, phases, periodization]
✅ **validated_contract** — promovido 2026-03-19 (ver seção correspondente acima)

#### **teams** [roster, staff, organization structure]
✅ **validated_contract** — promovido 2026-03-19 (ver seção correspondente acima)

#### **competitions** [league, tournament structure, matches schedule]
✅ **validated_contract** — promovido 2026-03-19 (ver seção correspondente acima)

#### **matches** [game records, results, performance data]
✅ **validated_contract** — promovido 2026-03-19 (ver seção correspondente acima)

#### **scout** [game analysis, video tagging, tactical signals]
✅ **validated_contract** — promovido 2026-03-19 (5 endpoints + 2 eventos AsyncAPI + arazzo + permissions + decision_ir + taxonomia canônica)
- DEC-SCOUT-001=C: GET /scout/events + POST /scout/events + GET /scout/events/{eventId} + GET /scout/events/aggregations + POST /scout/sessions/{matchId}/complete
- DEC-SCOUT-002=B: admin irrestrito; coordinator/coach com teamId obrigatório; athlete read-only self
- DEC-SCOUT-003=C: scout.event.created + scout.session.completed

---

### **Grupo 3: Performance Science (owner: performance-tech)**

#### **wellness** [pré/pós treino, carga, fadiga, sono]
✅ **validated_contract** — promovido 2026-03-19 (ver seção correspondente acima)

#### **medical** [lesões, tratamentos, restrições, RTP]
✅ **validated_contract** — promovido em 2026-03-19 (5 endpoints + schema + soft-delete + DC1-DC5 PASS)
- OpenAPI: ✅ medical.yaml (400+ linhas, 5 endpoints: listMedicalRecords, createMedicalRecord, getMedicalRecord, updateMedicalRecord, deleteMedicalRecord)
- Schema: ✅ medical_record.schema.json com fields: id, athleteUserId, recordDate, recordLabel, assessmentSummary, restrictionSummary, returnToTrainingAuthorized, returnToPlayAuthorized, clinicalNotes
- Segurança: ✅ HTTPBearer, BOLA mitigation (team-level access), x-semantic-id binding em todos IDs
- Conformidade: ✅ DR-MED-001..004, INV-MED-001..004, soft-delete com audit trail, paginação (pageSize 1-100)
- Sport Science: ✅ RTP authorization invariante (play→training), clinical notes restricted
- Superfícies (6/12): module_docs ✅, openapi_sync ✅ (400L), json_schema ✅ (1), test_matrix ✅, sport_science ✅, gaps (asyncapi/arazzo/permissions/decision_ir → v1.1)

#### **analytics** [dashboards, reporting, trend analysis, recommendations]
✅ **validated_contract** — promovido em 2026-03-19 (5 endpoints + schema + read-only + DC1-DC5 PASS)
- OpenAPI: ✅ analytics.yaml (600+ linhas, 5 endpoints: listAnalyticsSnapshots, createAnalyticsSnapshot, getAnalyticsSnapshot, listAnalyticsDashboards, queryAnalyticsData)
- Schema: ✅ analytics_snapshot.schema.json com fields: id, metricName, computedAt, sourceModuleLabels, timeWindowLabel, granularityLabel, filterSummary, projectionKey, refreshModeLabel
- Segurança: ✅ HTTPBearer, read-only enforcement (GET/POST snapshot + query), x-semantic-id binding
- Conformidade: ✅ DR-ANL-001..005, INV-ANL-001..003, sourceModuleLabels obrigatório (provenance), nunca reescreve source-of-truth
- Sport Science: ✅ KPI derivado, query time-series, no self-referential recursive metrics
- Superfícies (6/12): module_docs ✅, openapi_sync ✅ (600L), json_schema ✅ (1), test_matrix ✅, gaps (asyncapi/arazzo/permissions/decision_ir → v1.1)

#### **reports** [PDF/Excel exports, team summaries, performance comparisons]
✅ **validated_contract** — promovido em 2026-03-19 (5 endpoints + schema + async lifecycle + DC1-DC5 PASS)
- OpenAPI: ✅ reports.yaml (530+ linhas, 5 endpoints: listReportJobs, createReportJob, getReportJob, updateReportJob, downloadReportArtifact)
- Schema: ✅ report_job.schema.json com fields: id, ownerUserId, reportType, formatLabel, parameterSummary, sourceMetricNames, generatedArtifactRef, retentionLabel, requestedAt
- Segurança: ✅ HTTPBearer, team-level access, x-semantic-id binding em jobId/ownerUserId
- Async Lifecycle: ✅ 5-state job status (queued, processing, completed, failed, cancelled), cancelable (queued/processing only)
- Conformidade: ✅ DR-RPT-001..005, INV-RPT-001..004, parameterSummary explícito (no silent UI params), generatedArtifactRef não transfere storage sovereignty
- Binary Downloads: ✅ multiformat (PDF: application/pdf, Excel: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, CSV: text/csv, JSON: application/json)
- Retenção: ✅ retentionLabel obrigatório quando artifact gerado, 410 Gone quando expirado
- Superfícies (6/12): module_docs ✅, openapi_sync ✅ (530L), json_schema ✅ (1), test_matrix ✅, gaps (asyncapi/arazzo/permissions/decision_ir → v1.1)

---

## 📋 Evolução Esperada — Caminho para `validated_contract`

### Fase 1: Baseline
- ✅ Todos os 16 módulos têm: module_docs, openapi, json_schema
- ✅ Todos os 16 módulos têm: TEST_MATRIX

### Fase 2: Sprint 2026-03-17 / 2026-03-18 / 2026-03-19 ✅ CONCLUÍDA
- ✅ training → **implementation_ready** — todos os 14 schemas + 4076 linhas de contrato (2026-03-17)
- ✅ training → AsyncAPI 28/28 canais gerados
- ✅ training → UI contract v1.1.0 — SCREEN_MAP + 5 UIFs + 9 endpoints adicionados
- ✅ training → RC-1 a RC-4 resolvidos (STATE_MODEL + INVARIANTS + DOMAIN_RULES + TEST_MATRIX)
- ✅ training → A3..A6 resolvidos (adversarial inputs, performance, boundary rules, 4 novos Arazzo)
- ✅ training → M1/M2/M3/M5 resolvidos (soft-delete, elasticity, freshness SLA, naming)
- ✅ ADR-031 — Scope Boundary Gate implementado e validado (16/16 módulos PASS, 2026-03-18)
- ✅ openapi.yaml — HTTPBearer securityScheme adicionado (2026-03-18)
- ✅ openapi.yaml — 8 operações com `description` ausente corrigidas (exercises + training)
- ✅ openapi.yaml — nullable fixes: reasonOther + readinessAvg (tipo: [string|number, "null"])
- ✅ Auditoria de Eficiência de Contexto — 63.4% budget utilizado (2026-03-18)
- ✅ training → Sign-off UI contract (PO + UX + Engineering Lead) — **SIGNED_OFF 2026-03-18**
- ✅ training → D2 (versionamento) + D4 (stack backend) — **ADR-024 + ADR-031 formalizados 2026-03-18**
- ✅ exercises → **validated_contract** — OpenAPI completo (368L, 4 endpoints) + user_profile.yaml + DC1-DC5 PASS (2026-03-18)
- ✅ exercises → **validated_contract** — PERMISSIONS+DECISION_IR criados + DC1-DC5 PASS (2026-03-18)
- ✅ identity_access → **validated_contract** — OpenAPI completo (547L, 9 endpoints) + auth_session.yaml + arazzo desbloqueado + DC1-DC5 PASS (2026-03-19)
- ✅ notifications → **validated_contract** — OpenAPI (5 endpoints) + schemas + 3 canais AsyncAPI + arazzo desbloqueado + pipeline 10/10 PASS (2026-03-19)
- ✅ wellness → **validated_contract** — OpenAPI (5 endpoints) + 2 schemas + 1 canal AsyncAPI + arazzo + pipeline 10/10 PASS (2026-03-19)
- ✅ teams → **validated_contract** — OpenAPI (8 endpoints) + OpenAPI schema (statusLabel DRAFT/ACTIVE/ARCHIVED) + 2 canais AsyncAPI + 2 payloads + arazzo (team_roster_management) + pipeline 10/10 PASS (2026-03-19)
- ✅ ai_ingestion → **validated_contract** — OpenAPI (4 endpoints: listIngestionJobs, createIngestionJob, getIngestionJob, retryIngestionJob) + ingestion_job.yaml schema + 3 canais AsyncAPI (job.queued/completed/failed) + arazzo (ingestion_job_lifecycle) + pipeline 10/10 PASS (2026-03-19)
- ✅ seasons → **validated_contract** — OpenAPI (6 endpoints: listSeasons, createSeason, getSeason, patchSeason, addTeamToSeason, removeTeamFromSeason) + season.yaml schema (statusLabel/phaseLabels/teamIds/competitionIds) + 2 canais AsyncAPI (season.created/status_updated) + arazzo (season_lifecycle) + pipeline 10/10 PASS (2026-03-19)
- ✅ competitions → **validated_contract** — OpenAPI (6 endpoints: listCompetitions, createCompetition, getCompetition, patchCompetition, registerTeamInCompetition, unregisterTeamFromCompetition) + competition.yaml schema (statusLabel/stageLabels/registrationTeamIds/standingsSummary) + 2 canais AsyncAPI (competition.created/phase_changed) + arazzo (competition_lifecycle) + pipeline 10/10 PASS (2026-03-19)
- ✅ matches → **validated_contract** — OpenAPI (6 endpoints: listMatches, createMatch, getMatch, patchMatch, addPlayerToLineup, removePlayerFromLineup) + match.yaml schema (statusLabel 9 fases HBR-013 / DEC-MATCHES-002, CRUD / DEC-MATCHES-001) + 2 canais AsyncAPI (match.scheduled/status_updated) + arazzo (match_lifecycle) + DECISION_IR_MATCHES.yaml + MatchId em CANONICAL_TYPE_REGISTRY + pipeline 10/10 PASS (2026-03-19)
- ✅ users → **8/12 superfícies** — asyncapi (user.created + user.role_changed), arazzo (user_invitation), PERMISSIONS_USERS.md (PERM-USR-001..010), DECISION_IR_USERS.yaml (DEC-USERS-001/002/003), statusLabel adicionado ao schema user_profile.yaml + pipeline 10/10 PASS (2026-03-19)
- ✅ medical → **validated_contract** — OpenAPI (400+ linhas, 5 endpoints: listMedicalRecords, createMedicalRecord, getMedicalRecord, updateMedicalRecord, deleteMedicalRecord) + medical_record.yaml schema + soft-delete + BOLA mitigation + sport_science rules + DR-MED-001..005 + INV-MED-001..004 + pipeline 10/10 PASS (2026-03-19)
- ✅ analytics → **validated_contract** — OpenAPI (600+ linhas, 5 endpoints: listAnalyticsSnapshots, createAnalyticsSnapshot, getAnalyticsSnapshot, listAnalyticsDashboards, queryAnalyticsData) + analytics_snapshot.yaml schema + read-only enforcement + sourceModuleLabels obrigatório + DR-ANL-001..005 + INV-ANL-001..003 + pipeline 10/10 PASS (2026-03-19)
- ✅ reports → **validated_contract** — OpenAPI (530+ linhas, 5 endpoints: listReportJobs, createReportJob, getReportJob, updateReportJob, downloadReportArtifact) + report_job.yaml schema + async job lifecycle (5-state) + binary downloads (PDF/Excel/CSV/JSON) + retenção com 410 Gone + DR-RPT-001..005 + INV-RPT-001..004 + pipeline 10/10 PASS (2026-03-19)
- ✅ **video** → **draft_contract** — FASE 2-4 completas. Contratos técnicos desenvolvidos (OpenAPI 650L + 4 schemas + 6 canais AsyncAPI + STATE_MODEL + PERMISSIONS + 3 workflows). CONTRACT_GATES: 44/44 PASS (2026-03-19). Testes Django TM-001..008 implementados: 36/36 PASS (2026-03-19). SESSION_HANDOFF_VIDEO_20260319_FINAL.md criado.

### Fase 3: Backend Implementation Planning (Próximas 2-3 sprints)
- ✅ training → Geração de código backend (Django Ninja + Celery) — roadmap design (ADR-031 stack decidido)
- ✅ video → Testes Django TM-001..008 implementados (36/36 PASS). Pronto para design de models/views
- [ ] video → Design backend: MatchMediaSession, MediaSegment, ClipDefinition models
- [ ] video → API views (7 endpoints per OpenAPI contract)
- [ ] video → Celery tasks: Transcode pipeline (H.264, H.265, VP9, AV1)
- [ ] video → AsyncAPI consumers: Scout timecode sync, analytics clip queries
- [ ] Remaining gaps: AsyncAPI v1.1 (medical/analytics/reports/wellness/teams), state models v1.1
- [ ] Cross-module boundary tests: medical↔training, scout↔analytics, video↔scout (timecode sync)

### Fase 4: Validação de Contratos (CONCLUÍDA)
- ✅ medical/analytics/reports/teams/audit/scout → **`validated_contract`** — todos gates PASS (2026-03-19)
- ✅ 15/17 módulos → `validated_contract` (2026-03-19)
- ✅ 1/17 módulo → `implementation_ready` (training, 2026-03-17)
- ✅ 1/17 módulo → `draft_contract` (video, 2026-03-19)
- ⏳ Remaining gaps: AsyncAPI v1.1, state models v1.1, decision_ir para alguns módulos
- ⏳ Cross-module boundary reviews: medical↔training, scout↔analytics, video↔scout (timecode sync)

### Fase 5: Implementação (Em andamento)
- ✅ Video: Testes Django TM-001..008 completados (36/36 PASS, contract tests)
- [ ] Backend code generation: Django models + API views + Celery tasks
- [ ] Integration tests: Contract-to-code alignment
- [ ] Load tests + performance benchmarks
- [ ] Promotion: video `draft_contract` → `validated_contract` (após implementation tests)

---

## 🎯 Recomendação: Priorização de Próximas Fases

### **CRÍTICA (Em andamento — Backend Design)**
1. ✅ ~~training — fechar AsyncAPI (28), UI contract, arch decisions~~ **CONCLUÍDO** (2026-03-17)
2. ✅ ~~training — RC-1 a RC-4: Resolver riscos adversariais~~ **CONCLUÍDO** (2026-03-17)
3. ✅ ~~training — A3..A6: Adversarial inputs, performance, boundaries, Arazzo~~ **CONCLUÍDO** (2026-03-17)
4. ✅ ~~ADR-031 — Scope Boundary Gate~~ **CONCLUÍDO** (2026-03-18)
5. ✅ ~~HTTPBearer securityScheme + operações sem description~~ **CONCLUÍDO** (2026-03-18)
6. ✅ ~~**training — Sign-off UI contract:**~~ **CONCLUÍDO** — SIGNED_OFF 2026-03-18 (PO + UX + Engineering Lead)
7. ✅ ~~**D2 + D4 backend:**~~ **CONCLUÍDO** — ADR-024 (versionamento) + ADR-031 (stack) formalizados 2026-03-18
8. ✅ ~~**exercises** — fechar contrato~~ **CONCLUÍDO** — PERMISSIONS + arazzo + decision_ir + DC1-DC5 PASS (2026-03-18)
9. ✅ ~~**identity_access** — desenvolver OpenAPI real~~ **CONCLUÍDO** — 547L, 9 endpoints, auth_session.yaml, arazzo desbloqueado, DC1-DC5 PASS (2026-03-19)
10. ✅ ~~**medical** — contratos clínicos (avaliações, RTP, restrições)~~ **CONCLUÍDO** — 400L, 5 endpoints, soft-delete, BOLA mitigation, pipeline 10/10 PASS (2026-03-19)
11. ✅ ~~**analytics** — snapshots de métricas derivadas~~ **CONCLUÍDO** — 600L, 5 endpoints, read-only, provenance, pipeline 10/10 PASS (2026-03-19)
12. ✅ ~~**reports** — geração assíncrona de relatórios~~ **CONCLUÍDO** — 530L, 5 endpoints, job lifecycle, binary downloads, pipeline 10/10 PASS (2026-03-19)
13. ✅ ~~**video** — FASE 0-4: Contract Development + Test Matrix~~ **CONCLUÍDO** (2026-03-19)
14. **→ video — Backend Design (models + views, 1-2 sprints)**
15. **→ training — Code Generation (Django + Celery, 2-3 sprints)**
5. ~~HTTPBearer securityScheme + operações sem description~~ ✅ **CONCLUÍDO** (2026-03-18)
6. ~~**training — Sign-off UI contract:**~~ ✅ **CONCLUÍDO** — SIGNED_OFF 2026-03-18 (PO + UX + Engineering Lead)
7. ~~**D2 + D4 backend:**~~ ✅ **CONCLUÍDO** — ADR-024 (versionamento) + ADR-031 (stack) formalizados 2026-03-18
8. ~~**exercises** — fechar contrato~~ ✅ **CONCLUÍDO** — PERMISSIONS + arazzo + decision_ir + DC1-DC5 PASS (2026-03-18)
9. ~~**identity_access** — desenvolver OpenAPI real~~ ✅ **CONCLUÍDO** — 547L, 9 endpoints, auth_session.yaml, arazzo desbloqueado, DC1-DC5 PASS (2026-03-19)
10. ~~**medical** — contratos clínicos (avaliações, RTP, restrições)~~ ✅ **CONCLUÍDO** — 400L, 5 endpoints, soft-delete, BOLA mitigation, pipeline 10/10 PASS (2026-03-19)
11. ~~**analytics** — snapshots de métricas derivadas~~ ✅ **CONCLUÍDO** — 600L, 5 endpoints, read-only, provenance, pipeline 10/10 PASS (2026-03-19)
12. ~~**reports** — geração assíncrona de relatórios~~ ✅ **CONCLUÍDO** — 530L, 5 endpoints, job lifecycle, binary downloads, pipeline 10/10 PASS (2026-03-19)

### **ALTA (Infraestrutura de contratos) — v1.1+:**
1. AsyncAPI para medical, analytics, reports (eventos: clinical_*, metric_*, job_*)
2. State models formais para medical (RTP workflow), analytics (recommendation lifecycle), reports (job persistence)
3. Workflows Arazzo em `contracts/workflows/` para remaining módulos
4. users — schemas adicionais (profile, invitation, role_membership)

### **IMEDIATA (validação de boundaries — v1.0):**
1. wellness ↔ training — integração clara documentada
2. medical ↔ training — RTP restriction_profile usage
3. medical ↔ wellness — recovery insights handoff
4. analytics ↔ training — actor permissions + metric refresh triggers
5. analytics ↔ scout — event-driven snapshot updates
6. reports ↔ analytics — metric source normalization

### **PRÓXIMA (Code generation v1.0):**
- medical: Django models + soft-delete + audit logging
- analytics: query engine + snapshot persistence + cache invalidation
- reports: Celery async jobs + S3 storage adapter + retention scheduler
- Todas UI: athlete medical history + dashboard + report tracker (Next.js)

---

## 📊 Matrix de Superfícies por Módulo

> Atualizada em 2026-03-18. openapi ⚠️ = stub (8–12 linhas). openapi ✅ = contrato substantivo.

| Módulo | Status | module_docs | openapi | json_schema | test_matrix | state_model | permissions | sport_science | ui_contract | arazzo | asyncapi | decision_ir |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **training** | **implementation_ready** | ✅ | ✅ | ✅ (14) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ (28) | ✅ |
| **exercises** | **validated_contract** | ✅ | ✅ (1007L) | ✅ (4) | ✅ | — | ✅ | — | — | ✅ (2) | — | ✅ |
| **users** | **validated_contract** | ✅ | ✅ (4 ep) | ✅ (2) | ✅ | — | ✅ | — | — | ✅ (1) | ✅ (2) | ✅ |
| **identity_access** | **validated_contract** | ✅ | ✅ (547L) | ✅ (2) | ✅ | — | ✅ | — | — | ✅ (1) | ✅ (4) | ✅ |
| **ai_ingestion** | **validated_contract** | ✅ | ✅ (4 ep) | ✅ (1) | ✅ | — | — | — | — | ✅ (1) | ✅ (3) | — |
| **audit** | **validated_contract** | ✅ | ✅ (4 ep) | ✅ (1) | ✅ | — | ✅ | — | — | ✅ (1) | ✅ (2) | ✅ |
| **notifications** | **validated_contract** | ✅ | ✅ (5 ep) | ✅ (3) | ✅ | — | — | — | — | ✅ (1) | ✅ (3) | — |
| **wellness** | **validated_contract** | ✅ | ✅ (5 ep) | ✅ (3) | ✅ | — | — | ✅ | — | ✅ (1) | ✅ (1) | — |
| **seasons** | **validated_contract** | ✅ | ✅ (6 ep) | ✅ (2) | ✅ | — | — | — | — | ✅ (1) | ✅ (2) | — |
| **teams** | **validated_contract** | ✅ | ✅ (8 ep) | ✅ (1) | ✅ | ✅ | — | — | — | ✅ (1) | ✅ (2) | — |
| **competitions** | **validated_contract** | ✅ | ✅ (6 ep) | ✅ (2) | ✅ | — | — | — | — | ✅ (1) | ✅ (2) | — |
| **matches** | **validated_contract** | ✅ | ✅ (6 ep) | ✅ (2) | ✅ | — | — | — | — | ✅ (1) | ✅ (2) | ✅ |
| **scout** | **validated_contract** | ✅ | ✅ (5 ep) | ✅ (1) | ✅ | — | ✅ | — | — | ✅ (1) | ✅ (2) | ✅ |
| **medical** | **validated_contract** | ✅ | ✅ (400L) | ✅ (1) | ✅ | — | — | ✅ | — | ⏳¹ | — | — |
| **analytics** | **validated_contract** | ✅ | ✅ (600L) | ✅ (1) | ✅ | — | — | — | — | ⏳¹ | — | — |
| **reports** | **validated_contract** | ✅ | ✅ (530L) | ✅ (1) | ✅ | — | — | — | — | ⏳¹ | — | — |
| **video** | **scaffold** | ✅ | ⏳ | ⏳ (4) | ✅ | — | — | — | — | — | — | — |

**Legenda:**
- ✅ = Presente e validado
- ⚠️ = Presente, mas incompleto / stub
- ⏳¹ = Arazzo intent/AsyncAPI deferido para v1.1+
- ❌ = Faltante (esperado para este status)
- — = Não esperado para este status
- (N) = quantidade de arquivos/canais
- (NL) = linhas de OpenAPI

---

## 🔄 Próxima Ação

→ ~~Sign-off UI contract~~ ✅ **CONCLUÍDO** — SIGNED_OFF 2026-03-18 (PO + UX + Engineering Lead)
→ ~~D2 + D4 decisões~~ ✅ **CONCLUÍDO** — ADR-024 + ADR-031 formalizados 2026-03-18
→ ~~**exercises** — fechar contrato~~ ✅ **CONCLUÍDO** — PERMISSIONS_EXERCISES + DECISION_IR + DC1-DC5 PASS (2026-03-18)
→ ~~**identity_access** — OpenAPI real (9 endpoints, 547L)~~ ✅ **CONCLUÍDO** — auth_session.yaml + arazzo + DC1-DC5 PASS (2026-03-19)
→ ~~**medical** — contratos clínicos (5 endpoints, 400L)~~ ✅ **CONCLUÍDO** — soft-delete + BOLA mitigation + DC1-DC5 PASS (2026-03-19)
→ ~~**analytics** — snapshots de métricas (5 endpoints, 600L)~~ ✅ **CONCLUÍDO** — read-only + provenance + DC1-DC5 PASS (2026-03-19)
→ ~~**reports** — geração assíncrona (5 endpoints, 530L)~~ ✅ **CONCLUÍDO** — job lifecycle + binary downloads + DC1-DC5 PASS (2026-03-19)
→ ~~**video** — Decision Discovery + canonicalização~~ ✅ **CONCLUÍDO** — ADR-033 aprovado, MODULE_REGISTRY atualizado, documento mínimo criado, scaffold PASS (2026-03-19)
→ **VIDEO CONTRACTS v1.0 (IMEDIATO)** — OpenAPI (capture/ingest/playback endpoints) + AsyncAPI (6+ canais) + JSON Schemas (4 tipos) para promover a `draft_contract`
→ **CODE GENERATION v1.0 (PRÓXIMA SEMANA)** — Django/FastAPI/Next.js para training + medical/analytics/reports
→ **Boundary validation** — video↔scout (timecode), medical↔training, analytics↔training, reports↔analytics
→ **v1.1 planning** — STATE_MODEL + PERMISSIONS + additional Arazzo workflows para video + medical/analytics/reports

