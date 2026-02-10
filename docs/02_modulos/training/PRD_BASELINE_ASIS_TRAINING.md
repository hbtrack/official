# PRD (Baseline AS-IS) — Módulo TRAINING

## 1. Controle do documento (Governança)

* **Documento**: PRD_BASELINE_ASIS_TRAINING.md
* **Status**: BASELINE / AS-IS
* **Versão**: v1.3
* **Data**: 2026-02-08
* **Owner (papel)**: Product Owner / Tech Lead
* **Escopo do baseline**: "Training (agenda + sessões + presença + wellness + gamificação + performance + alertas/sugestões + attendance + analytics insights + templates)"

### Baseline Evidence Snapshot
* **Git commit**: e02c83efa1926c880336511ff72a13311093bdb9
* **Generated at**: 2026-01-29T10:05:14.823044Z
* **System state**: HB Track v1.3 (97% module completion — 31/32 features; badge monthly job inativo)
* **Evidence files**:
  * OpenAPI: `Hb Track - Backend/docs/_generated/openapi.json` (checksum: 7b435e0e...)
  * Schema: `Hb Track - Backend/docs/_generated/schema.sql` (checksum: 068a32e1...)
  * Migrations state: `Hb Track - Backend/docs/_generated/alembic_state.txt` (checksum: 9fc66059...)
  * Manifest: `Hb Track - Backend/docs/_generated/manifest.json`

### Fontes de verdade (obrigatórias):
* **OpenAPI**: `Hb Track - Backend/docs/_generated/openapi.json` (tags: training-sessions, wellness, analytics, session-templates)
* **Schema**: `Hb Track - Backend/docs/_generated/schema.sql` (tabelas do módulo Training — ver TRD)
* **Migrations state**: `Hb Track - Backend/docs/_generated/alembic_state.txt`
* **Manifest**: `Hb Track - Backend/docs/_generated/manifest.json` (rastreabilidade commit + checksums)
* **UI/Fluxos**: `Hb Track - Fronted/src/app/(admin)/training/` (agenda, calendar, wellness forms)

### Documentos relacionados:
* **Planos**: `docs/_PLANO_TRAINING.md` (implementação), `docs/_ANALISE_FLUXO_ATIVIDADES.md` (workflow)
* **Guidelines/Security/RBAC**: `docs/_PERMISSIONS.md`
* **Referência técnica canônica**: `docs/02-modulos/training/TRD_TRAINING.md` (versão v1.8, commit e02c83ef)
  * Regra: contratos e regras verificadas = ver TRD.

## 2. Objetivo do baseline (por que este PRD existe)

### Problema atual:
Módulo TRAINING está 97% completo (31/32 funcionalidades implementadas — badge monthly job inativo) com documentação que precisava de alinhamento entre PRD_BASELINE, TRD e INVARIANTS.

### Objetivo deste baseline:
* Consolidar estado atual do módulo TRAINING para referência canônica (12 FRs, 80 endpoints, 46+ invariantes)
* Fixar papéis e permissões implementados para training/wellness
* Mapear contratos reais via evidência OpenAPI/schema atual
* Documentar invariantes inter-módulos para integrações seguras
* Registrar features de frontend (UX flows) implementadas

## 3. Escopo e fora de escopo do baseline

### 3.1 In-scope (lista fechada)
* Gestão de sessões de treino (CRUD, workflow draft→scheduled→in_progress→pending_review→readonly; UI "closed")
* Sistema de wellness pre/post training
* Banco de exercícios com tags hierárquicas
* Performance analytics com cache de 17 métricas
* Gamificação (badges, rankings, streaks)
* Planejamento de ciclos (macro/meso/microciclos)
* Templates de sessão (CRUD, favorites, focus presets)
* Alertas automáticos e sugestões de carga
* Gestão de presenças (attendance) com correções administrativas
* Training analytics insights (sumário, carga semanal, desvios, eficácia preventiva)
* Dashboard de efetividade preventiva
* Compliance LGPD (export, retention, anonymization)
* Integrações com módulos Athletes/Teams

### 3.2 Out-of-scope (lista explícita)
* Cálculo mensal de badges (job Celery comentado — `celery_app.py:136-139`)
* Módulos externos (Athletes, Teams, Analytics core)
* Features futuras não implementadas (IA, competições, scout)

### 3.3 Suposições do baseline
* Ambiente backend em estado funcional com migrations até 0046
* Frontend em desenvolvimento ativo com componentes principais funcionais
* Integrações com PostgreSQL, Redis, Celery operacionais

## 4. Visão geral do produto/módulo hoje (AS-IS)

### Descrição curta:
O módulo TRAINING do HB Track é um sistema completo de gestão de treinamentos para handebol que permite criar/gerenciar sessões com foco percentual em 7 áreas (ataque posicional, defesa posicional, transições, técnico, físico, pré-jogo, mental), monitorar wellness pré/pós treino dos atletas, gerenciar banco de exercícios com tags, analisar performance através de 17 métricas cached, gamificar participação através de badges/rankings e planejar periodização via macro/meso/microciclos.

### Limites e integrações existentes:
* **Integra com Athletes**: para seleção de participantes e registro de presence/wellness
* **Integra com Teams**: para contexto organizacional e permissões
* **Integra com Organizations**: para isolamento multi-tenant
* **Integra com Seasons**: para contexto temporal e relatórios
* **Depende de Redis**: para cache de performance e sessions — **Confirmado**: `app/core/celery_app.py` (broker/backend), libs instaladas
* **Depende de Celery**: para jobs async (alerts, exports, cleanup) — **Confirmado**: `app/core/celery_app.py`, `celery_tasks.py`, scripts `start-celery-*.ps1`
* **O que não existe**: integração direta com competições, integração com IoT devices, sincronização com wearables

## 5. Papéis, perfis e permissões (alto nível)

### 5.1 Papéis existentes
* **Coach/Staff**: Criação/edição de sessões, monitoramento de wellness, acesso a analytics, gestão de templates
* **Athlete**: Submissão de wellness próprio, visualização de histórico próprio, acesso a badges próprios
* **Admin**: Todas permissões de coach + gestão de dados organizacionais + exports LGPD

### 5.2 Regras de autorização (resumo canônico)
* Requisitos por endpoint: ver `docs/_generated/trd_training_permissions_report.txt` (gerado a partir de routers + permissions_map)
* Autorização baseada em RBAC + escopo de organização/time
* Export e analytics seguem rate limiting e escopo organizacional (ver TRD)

### 5.3 Evidência
* **Doc RBAC/Security**: `docs/_PERMISSIONS.md`
* **Endpoints protegidos**: todos endpoints training-sessions/* requerem auth middleware

## 6. Estados do domínio e invariantes atuais

### 6.1 Estados por entidade
**Training Session**:
* `draft` → `scheduled` → `in_progress` → `pending_review` → `readonly`
* Nota: UI usa rótulo "closed" para status `readonly` (ver TRD)
* Transições: staff pode avançar, apenas admin pode reverter `readonly`

**Wellness Submission**:
* `pending` → `submitted` → `processed`
* Cálculos pós-submissão — **Confirmado**: trigger `tr_calculate_internal_load` calcula `internal_load = minutes_effective × session_rpe` (ver `wellness_post_service.py:286`, `wellness_post.py:173-174`)

**Exercise Assignment**:
* `active` → `removed`
* Soft delete para preservar histórico

### 6.2 Invariantes (regras confirmadas e gaps)
* Regras confirmadas: ver TRD §5 (Evidence Ledger).
* Regras pretendidas (não localizadas): manter aqui como backlog/Gap-005.

### 6.3 Evidência
* **Schema**: training_sessions.status, wellness_*.status columns
* **OpenAPI/Services**: ver TRD (operationIds e evidências de transição)
* **Business logic**: `training_session_service.py` validation rules

## 7. Requisitos funcionais AS-IS (catálogo)

**PRD-FR-001** — Gestão de sessões de treino
* **Descrição (AS-IS)**: Sistema permite criar, editar, visualizar e deletar sessões de treino com 7 focos percentuais, validação de limites, workflow de status e gestão de participantes
* **Atores**: Coach, Staff, Admin
* **Estado**: Ativo
* **Regras/validações observadas**: 
  * Focus percentages limitado a 120% total (traffic light: verde ≤100%, amarelo 101-120%, vermelho >120%)
  * Lifecycle e transições confirmadas: ver TRD (status `draft`→`scheduled`→`in_progress`→`pending_review`→`readonly`)
  * Requires team/season context válido
* **Saídas observadas**: Sessão persistida. Logs de auditoria — **Confirmado** (INV-TRAIN-019, append-only audit_logs). Notificações de mudança de status — **Futuro V1.1** (não implementado)
* **Evidência mínima**:
  * **OpenAPI**: `GET/POST /api/v1/training-sessions`, `POST .../publish`, `POST .../close`, `POST .../duplicate`
  * **Schema**: `training_sessions` table com focus_*_pct columns
  * **UI**: `AgendaClient.tsx`, `CalendarioClient.tsx`
  * **Teste/Log**: service tests em `training_session_service.py`
* **Referência TRD**: §6 PRD-FR-001; Regras: RULE-FOCUS-MAX-120, RULE-SESSION-EDIT-AUTHOR-10M, RULE-SESSION-EDIT-SUPERIOR-24H, RULE-SESSION-IMMUTABLE-60D, RULE-SESSION-LIFECYCLE, RULE-DEVIATION-THRESHOLD-20PTS, RULE-DEVIATION-AGGREGATE-30PCT, RULE-JUSTIFICATION-MIN-50CHARS

**PRD-FR-002** — Monitoramento wellness pré-treino
* **Descrição (AS-IS)**: Atletas submetem wellness pré-treino (sono, fadiga, stress, dor muscular, prontidão) via formulário self-service com validação; reminder notifications — **Parcial** (service `wellness_notification_service.py:35` cria registros em `wellness_reminders`, mas Celery scheduled tasks desabilitadas em `celery_app.py:127-134`)
* **Atores**: Athlete (submissão), Coach/Staff (monitoramento)
* **Estado**: Ativo
* **Regras/validações observadas**:
  * Scales 1-5 para cada dimensão wellness
  * Submissão até `session_at - 2h` (ver TRD RULE-WPRE-DEADLINE-2H)
  * Reminder 24h é UX (não bloqueia) — **Parcial** (service existe, scheduled task desabilitada)
* **Saídas observadas**: Wellness data persistido. Dashboard — **Confirmado** (analytics cache, PRD-FR-005). Badge eligibility — **Futuro V1.1** (sem implementação)
* **Evidência mínima**:
  * **OpenAPI**: `GET/POST /api/v1/wellness-pre/training_sessions/{id}/wellness_pre`, `GET .../status`
  * **Schema**: `wellness_pre` table
  * **UI**: `WellnessPreClient.tsx`
  * **Teste/Log**: wellness service validations
* **Referência TRD**: §6 PRD-FR-002; Regras: RULE-WPRE-DEADLINE-2H, RULE-UNIQUE-WPRE-ATHLETE-SESSION, RULE-LGPD-RETENTION-3Y

**PRD-FR-003** — Monitoramento wellness pós-treino
* **Descrição (AS-IS)**: Atletas submetem RPE e internal load pós-treino com calculation automático e integration com performance analytics
* **Atores**: Athlete (submissão), Coach/Staff (analysis)
* **Estado**: Ativo
* **Regras/validações observadas**:
  * RPE scale 1-10
  * Internal load = RPE × duration — **Confirmado**: trigger `tr_calculate_internal_load` (`wellness_post.py:173-174`)
  * Submissão até 24h pós criação (`wellness_post_service.py:88`)
* **Saídas observadas**: Load metrics e training analytics cache — **Confirmado** (INV-TRAIN-015, INV-TRAIN-022). Overload alerts — **Confirmado**: `check_weekly_overload_task` (`celery_tasks.py:57-58`, `training_analytics_service.py:191`)
* **Evidência mínima**:
  * **OpenAPI**: `GET/POST /api/v1/wellness-post/training_sessions/{id}/wellness_post`, `GET .../status`
  * **Schema**: `wellness_post` table
  * **UI**: post-wellness forms
  * **Teste/Log**: load calculation tests
* **Referência TRD**: §6 PRD-FR-003; Regras: RULE-WPOST-DEADLINE-24H, RULE-UNIQUE-WPOST-ATHLETE-SESSION, RULE-LGPD-RETENTION-3Y

**PRD-FR-004** — Banco de exercícios
* **Descrição (AS-IS)**: Sistema mantém biblioteca de exercícios com tags hierárquicas, favorites per user, media URLs e assignment a sessões via drag-and-drop
* **Atores**: Coach, Staff (gestão), All users (consumption)
* **Estado**: Ativo
* **Regras/validações observadas**:
  * Tags hierarchical com parent/child relationships
  * Media URL validation para videos
  * Soft delete para preservar histórico
* **Saídas observadas**: Exercise library, session exercise assignments, user favorites
* **Evidência mínima**:
  * **OpenAPI**: `GET/POST /api/v1/exercises`, `GET/POST /api/v1/exercise-tags`, `GET/POST .../exercise-favorites`
  * **Schema**: `exercises`, `exercise_tags`, `training_session_exercises` tables
  * **UI**: exercise management pages
  * **Teste/Log**: exercise service CRUD tests
* **Referência TRD**: §6 PRD-FR-004; Regras: ver TRD §5 (nenhuma RULE específica confirmada para FR-004)

**PRD-FR-005** — Performance analytics
* **Descrição (AS-IS)**: Sistema calcula e cacheia 17 métricas de performance incluindo load analysis, deviation alerts, attendance rates e wellness response tracking
* **Atores**: Coach, Staff, Admin
* **Estado**: Ativo
* **Regras/validações observadas**:
  * Threshold-based alerting (ver TRD RULE-OVERLOAD-THRESHOLD-1.5X)
  * Team-scoped metrics isolation
  * Cache refresh daily/on-demand — **Confirmado** (INV-TRAIN-027, TRD v1.6)
* **Saídas observadas**: Performance dashboard — **Confirmado** (analytics cache + endpoints). Deviation alerts — **Confirmado** (`check_weekly_overload_task`). Trend reports — **Parcial** (analytics data disponível, UI de trends não confirmada)
* **Evidência mínima**:
  * **OpenAPI**: `GET /api/v1/analytics/wellness-rankings`, `GET .../team/{id}/athletes-90plus`
  * **Schema**: `training_analytics_cache` table
  * **UI**: analytics dashboard components
  * **Teste/Log**: cache calculation algorithms
* **Referência TRD**: §6 PRD-FR-005; Regras: RULE-OVERLOAD-THRESHOLD-1.5X (cache refresh daily **Confirmado** TRD v1.6, INV-TRAIN-027)

**PRD-FR-006** — Sistema de gamificação
* **Descrição (AS-IS)**: Sistema awards badges para athletes baseado em wellness response rate (≥90% monthly), mantém rankings de team e tracks streaks de participação
* **Atores**: Athlete (recipient), System (calculation), Coach/Staff (monitoring)
* **Estado**: Ativo
* **Regras/validações observadas**:
  * Badge calculation monthly (1st day) — **Inativo**: job comentado em `celery_app.py:136-139`
  * Response rate threshold 90% para wellness champion
  * Streak tracking multi-month
* **Saídas observadas**: Badge awards, team rankings, leaderboards
* **Evidência mínima**:
  * **OpenAPI**: `POST /api/v1/analytics/wellness-rankings/calculate` (cálculo sob demanda)
  * **Schema**: `athlete_badges`, `team_wellness_rankings` tables
  * **UI**: badge showcase components
  * **Teste/Log**: `wellness_gamification_service.py` tests
* **Referência TRD**: §6 PRD-FR-006; Regras: RULE-BADGE-MONTHLY-90PCT, RULE-BADGE-STREAK-3M

**PRD-FR-007** — Planejamento de ciclos
* **Descrição (AS-IS)**: Sistema suporta hierarchical planning via macrocycles (season-long), mesocycles (4-6 weeks), microcycles (weekly) com dependencies e date validation
* **Atores**: Coach, Staff, Admin
* **Estado**: Ativo
* **Regras/validações observadas**:
  * Date overlap validation
  * Hierarchy enforcement (macro → meso → micro)
  * Season scope compliance
* **Saídas observadas**: Periodization structure, cycle calendars, planning reports
* **Evidência mínima**:
  * **OpenAPI**: `GET/POST /api/v1/training-cycles`, `GET/POST /api/v1/training-microcycles`, `GET .../teams/{id}/active`
  * **Schema**: `training_cycles`, `training_microcycles` tables
  * **UI**: cycle management interface
  * **Teste/Log**: cycle validation logic
* **Referência TRD**: §6 PRD-FR-007; Regras: RULE-FOCUS-MAX-120, RULE-MICROCYCLE-SESSION-DEFAULT — **Confirmado** (`training_session_service.py:237-239`)

**PRD-FR-008** — Templates de sessão
* **Descrição (AS-IS)**: Sistema mantém templates de sessão reutilizáveis com focus presets (7 áreas), icons customizáveis (target/activity/bar-chart/shield/zap/flame), favorites per user, limite de 50 templates por organização e application automática para criação de sessões
* **Atores**: Coach, Staff (creator/manager — roles: treinador, coordenador, dirigente, preparador_fisico), All users (consumer)
* **Estado**: Ativo
* **Regras/validações observadas**:
  * Template focus validation ≤120% total (igual a sessões) — **Confirmado**: `ck_session_templates_focus_sum`
  * Template name unique per org — **Confirmado** (INV-TRAIN-035)
  * Limite 50 templates por organização — **Confirmado**: service validation
  * User-scoped favorites via toggle endpoint
  * Hard delete (não soft delete) para liberar espaço
* **Saídas observadas**: Template library, quick session creation, standardized focus patterns, favorite management
* **Evidência mínima**:
  * **OpenAPI**: 6 endpoints — `GET/POST /api/v1/session-templates`, `GET/PATCH/DELETE .../session-templates/{id}`, `PATCH .../session-templates/{id}/favorite`
  * **Schema**: `session_templates` table com `idx_session_templates_org_favorite`
  * **UI**: `ConfiguracoesClient.tsx` — **Completo**: create, edit, delete, duplicate, favorite toggle com permission gating (`can_view_training`, `can_create_training`, `can_edit_training`, `can_delete_training`)
  * **Teste/Log**: template service backend tests
* **Referência TRD**: §6 PRD-FR-008; Regras: RULE-FOCUS-MAX-120

**PRD-FR-009** — Export LGPD e compliance
* **Descrição (AS-IS)**: Sistema define export de dados e retenção LGPD; interface de export é interna (ExportService) e não está no OpenAPI
* **Atores**: Athlete (self-export), Admin (full export), System (retention)
* **Estado**: Parcial (interface interna; endpoints públicos não expostos)
* **Regras/validações observadas**:
  * Rate limiting 5 exports/day per user (ver TRD RULE-EXPORT-RATE-PDF-5D)
  * Scope validation (own data apenas para athletes) — **Confirmado**: RBAC middleware em endpoints de export
  * Audit logging para todos exports — **Confirmado**: `athlete_data_export_service.py:389-398` (`_log_export`)
* **Saídas observadas**: Exported data files e audit logs — **Confirmado** (`_log_export` registra em audit_logs); anonymization após 3 anos — **Confirmado** (ver TRD RULE-LGPD-RETENTION-3Y)
* **Evidência mínima**:
  * **TRD**: Export LGPD (interface interna, regras verificadas)
  * **Schema**: `export_jobs` table
  * **UI**: export functionality integrated — **Parcial** (backend completo, UI pendente de confirmação)
  * **Teste/Log**: LGPD compliance tests — **Confirmado** (INV-TRAIN-025: `tests/unit/test_inv_train_025_export_lgpd_endpoints.py`)
* **Referência TRD**: §6 PRD-FR-009; Regras: RULE-EXPORT-RATE-PDF-5D, RULE-EXPORT-RATE-ATHLETE-3D, RULE-LGPD-RETENTION-3Y

**PRD-FR-010** — Alertas e sugestões de carga
* **Descrição (AS-IS)**: Sistema gera alertas automáticos de sobrecarga (weekly_overload quando carga semanal >1.5× threshold, low_wellness_response quando response rate <70% por 2+ semanas) e sugestões de ajuste de carga (compensation: redistribuir foco alto; reduce_next_week: reduzir intensidade) baseadas em análise dos últimos 90 dias de histórico
* **Atores**: System (trigger automático via Celery), Coach/Coordenador (gestão de alertas e sugestões)
* **Estado**: Ativo
* **Regras/validações observadas**:
  * Threshold dinâmico via `team.alert_threshold_multiplier` (default 1.5×) — **Confirmado**: `training_alerts_service.py:82`
  * Severidade: warning (100-110% do threshold), critical (>110%)
  * Sugestões requerem mínimo 3 microciclos similares, desvio ≥10pts, consistência ≥70%
  * Tipos de sugestão: `compensation`, `reduce_next_week`
  * Confiança: high (≥70%), medium (50-70%), low (<50%)
* **Saídas observadas**: Alertas persistidos com histórico e stats. Sugestões com status (pending/applied/dismissed). WebSocket broadcast para alertas críticos — **Confirmado** (INV-TRAIN-024)
* **Evidência mínima**:
  * **OpenAPI**: 9 endpoints em `/api/v1/training/alerts-suggestions/*` (active, history, stats, dismiss para alerts; pending, history, stats, apply, dismiss para suggestions)
  * **Schema**: `training_alerts` (type, severity, metadata JSONB), `training_suggestions` (type, target_session_ids, recommended_adjustment_pct, status)
  * **UI**: Frontend de alertas integrado ao dashboard de analytics
  * **Teste/Log**: `tests/unit/test_inv_train_024_websocket_broadcast.py` (INV-TRAIN-024)
* **Referência TRD**: §6 PRD-FR-010; Regras: RULE-OVERLOAD-THRESHOLD-1.5X

**PRD-FR-011** — Gestão de presenças (Attendance)
* **Descrição (AS-IS)**: Sistema registra presença individual e em batch por sessão de treino, com status de presença (present/absent), tipo de participação (full/partial/adapted/did_not_train), fonte (manual/import/correction) e correções administrativas com audit trail
* **Atores**: Coach (registro individual e batch), Admin (correção administrativa)
* **Estado**: Ativo
* **Regras/validações observadas**:
  * Soft delete com pair `deleted_at`/`deleted_reason` — **Confirmado**: `ck_attendance_deleted_reason` (`schema.sql:674`)
  * Correção administrativa requer `correction_by_user_id` e `correction_at` — **Confirmado** (INV-TRAIN-030)
  * Rota scoped `/api/v1/teams/{team_id}/trainings/{id}/attendance` **não exposta** no agregador — retorna 404 — **Confirmado** (INV-TRAIN-016)
* **Saídas observadas**: Registros de presença, estatísticas por sessão, audit trail de correções
* **Evidência mínima**:
  * **OpenAPI**: 6 endpoints (list, add, batch, update, statistics, correct) em `/api/v1/training_sessions/{id}/attendance/*` e `/api/v1/attendance/{id}/*`
  * **Schema**: `attendance` table com constraints `ck_attendance_presence_status`, `ck_attendance_participation_type`, `ck_attendance_source`
  * **UI**: `/training/presencas` (AttendanceTab component)
  * **Teste/Log**: `tests/api/test_training.py::TestAttendanceAPI`
* **Referência TRD**: §6 PRD-FR-011; Regras: RULE-SOFTDELETE-REASON-PAIR

**PRD-FR-012** — Training Analytics Insights
* **Descrição (AS-IS)**: Sistema fornece sumários agregados de 17 métricas por equipe, análise de carga semanal (últimas N semanas), análise de desvios planejado vs executado e dashboard de eficácia preventiva (correlação load × lesões)
* **Atores**: Coach, Staff, Admin
* **Estado**: Ativo
* **Regras/validações observadas**:
  * Cache híbrido: weekly (mês corrente, por microcycle_id), monthly (histórico)
  * Invalidação automática via trigger `tr_invalidate_analytics_cache` — **Confirmado** (INV-TRAIN-020)
  * Threshold dinâmico via `team.alert_threshold_multiplier` — **Confirmado**: `training_analytics_service.py:190-191`
* **Saídas observadas**: Team summary (17 métricas), weekly load history, deviation analysis, prevention effectiveness dashboard
* **Evidência mínima**:
  * **OpenAPI**: 4 endpoints em `/api/v1/analytics/team/{team_id}/*` (summary, weekly-load, deviation-analysis, prevention-effectiveness)
  * **Schema**: Dependências em 8 tabelas (training_analytics_cache, training_sessions, training_microcycles, attendance, wellness_pre, wellness_post, training_alerts, training_suggestions) + tabelas externas (teams, athletes, medical_cases)
  * **UI**: `/training/analytics` (AnalyticsClient), `/training/eficacia-preventiva` (PreventionDashboardClient)
  * **Teste/Log**: analytics service calculations, cache invalidation tests
* **Referência TRD**: §6 PRD-FR-012; Regras: threshold dinâmico

## 8. Requisitos não funcionais (NFR) AS-IS

> **Referência completa de SLAs**: ver PRD_HB_TRACK.md §10 (RNF-001 a RNF-009, SLAs §10.7)

### 8.1 Performance
* **Métrica/limite atual**: Training analytics cache refresh sub-5s para team data, dashboard load <3s typical
* **SLAs formais**: p95 < 200ms (CRUD), < 2s (analytics) — ver PRD_HB_TRACK.md §10.7
* **Estado**: Estimado (based on development testing)
* **Evidência**: Caching implementation, Redis performance configs

### 8.2 Confiabilidade/Disponibilidade
* **Backup strategy**: PostgreSQL automated backups, Redis persistence enabled
* **SLAs formais**: 99.5% uptime, MTTR < 4h — ver PRD_HB_TRACK.md §10.7
* **Estado**: Confirmado
* **Evidência**: Database configuration, backup scripts

### 8.3 Segurança/Privacidade (AS-IS)
* **AuthN/AuthZ existentes**: JWT-based authentication, RBAC middleware em todos endpoints training
* **Logs/audit**: Audit trail — **Confirmado**: `athlete_data_export_service.py:389-398` (`_log_export`), INV-TRAIN-019 (audit_logs append-only)
* **Retenção/mascaramento**: 3-year retention com anonymization automática, LGPD compliance
* **Evidência**: Security middleware, LGPD scripts, audit logging confirmado

## 9. Dados (alto nível) e sensibilidade

### Entidades principais:
* **training_sessions**: dados de treino, não-sensível (PII básico: timestamps)
* **wellness_pre/post**: dados pessoais de saúde/performance - SENSÍVEL (LGPD)
* **exercises**: não-sensível, dados públicos
* **training_session_exercises**: vínculo sessão-exercício (histórico)
* **athlete_badges**: gamification data, não-sensível
* **training_analytics_cache**: analytics aggregated, não-sensível
* **export_jobs**: dados de export LGPD (jobs)

### Campos sensíveis por entidade:
* **wellness_***: sleep_quality, fatigue_level, stress_level, muscle_soreness, readiness, rpe (dados de saúde)
* **training_sessions**: participant lists (via foreign keys)

### Políticas existentes:
* **Retenção**: 3 anos active, anonymization posterior
* **Consentimento**: implicit via platform usage terms
* **Exportação**: self-service limitada, admin full export — **Confirmado** (backend: `athlete_data_export_service.py`, rate limiting: RULE-EXPORT-RATE-PDF-5D)

### Evidência: 
* Schema comments, LGPD compliance services, data classification docs

## 10. UX e fluxos reais (alto nível)

### Fluxo 1 - Criação de sessão de treino (Coach):
1. Acessa agenda semanal (`/training/agenda`) ou calendário mensal (`/training/calendario`)
2. Seleciona data/time slot ou clica "+"
3. Opcionalmente seleciona template de sessão para pré-carregar focos
4. Define focus percentages com sistema semáforo (traffic light):
   - **Verde** (≤100%): válido, prossegue normalmente
   - **Amarelo** (101-120%): válido mas requer atenção visual
   - **Vermelho** (>120%): bloqueado pela constraint `ck_session_templates_focus_sum`
5. Adiciona exercícios via drag-and-drop do banco de exercícios (`@dnd-kit/core`)
6. Define participantes (team roster), localização, tipo (quadra/fisico/video/reuniao/teste)
7. Salva como draft ou publica diretamente
* **Evidência**: `CreateSessionModal/`, `SessionEditorModal.tsx`, `FocusDistributionEditor.tsx`

### Fluxo 2 - Wellness pre-treino (Athlete):
1. Recebe reminder (24h antes, UX; não bloqueia)
2. Acessa wellness form via app/web
3. Preenche 5 dimensões (scales 1-5)
4. Submete com validation feedback
5. Recebe confirmação e badge progress update

### Fluxo 3 - Monitoramento staff (Coach):
1. Acessa dashboard wellness
2. Visualiza response rates e alerts
3. Drilla down em atletas específicos
4. Gera relatórios de trends
5. Toma ações baseadas em deviations

### Fluxo 4 - Agenda semanal (Coach):
1. Visualiza semana (Seg–Dom) com sessões organizadas por dia em cards
2. Drag-and-drop de sessões entre dias para reagendar (`@dnd-kit`, pointer sensor 6px)
3. Filtros: equipe (dropdown), busca por texto (debounce 300ms)
4. Contadores de status: badges com drafts e pending review
5. URL-based state: `?view=week`, `?date=YYYY-MM-DD`, `?teamId=UUID`, `?q=search`
6. Auto-scroll para primeiro draft da semana
* **Evidência**: `AgendaClient.tsx`, `WeeklyAgenda.tsx`, `AgendaHeader.tsx`

### Fluxo 5 - Copiar semana (Coach):
1. Na agenda semanal, clica "Copiar Semana"
2. Seleciona semana fonte e semana destino
3. Sistema duplica todas sessões da semana como `draft`
4. Coach ajusta focos/exercícios conforme necessário
* **Evidência**: `CopyWeekModal.tsx`, `POST /api/v1/training-sessions/copy-week`

### Fluxo 6 - Agenda mensal (Coach):
1. Calendário grid (mês completo) com indicadores de densidade por dia
2. Session pills compactos (máx 2 por dia, "+N" para excedentes)
3. Clique em dia abre drawer lateral com detalhes completos
4. Filtros: All, Pending Review, Scheduled, Draft
5. Navegação: mês anterior/próximo, botão "Hoje"
* **Evidência**: `MonthlyAgenda.tsx`, `/training/calendario`

### Fluxo 7 - Planejamento de ciclos (Coach):
1. Acessa `/training/planejamento` com hierarquia colapsável:
   - **Macrociclo** (trimestre/temporada) → **Mesociclo** (4-6 semanas) → **Microciclo** (semanal)
2. Criação via wizard modal (`CreateCycleWizard.tsx`)
3. Barras de progresso de carga planejada por microciclo
4. Status visual por ciclo (active/completed/cancelled)
5. Copy week entre microciclos
* **Evidência**: `PlanejamentoClient.tsx`, `CreateCycleWizard.tsx`

### Fluxo 8 - Banco de exercícios (Coach):
1. Acessa `/training/exercise-bank` com grid virtualizado para 100+ exercícios
2. Filtros avançados:
   - Texto (debounce 500ms) no nome/descrição
   - Categoria: aquecimento, técnico, tático, físico, jogo
   - Tags hierárquicas (AND/OR) via `TagFilter.tsx`
   - Toggle "Apenas favoritos"
3. Paginação customizável: 12, 20 ou 40 por página
4. Drag-and-drop de exercício para sessão ativa (`DraggableExerciseCard.tsx` → `SessionExerciseDropZone.tsx`)
5. Criação/edição via modais (staff-only: treinador, coordenador, dirigente, superadmin)
6. Favoritar exercícios (user-scoped)
* **Evidência**: `exercise-bank/page.tsx`, `VirtualizedExerciseGrid.tsx`, `ExerciseCard.tsx`

### Fluxo 9 - Configuração de templates (Coach/Staff):
1. Acessa `/training/configuracoes`
2. Lista de templates (máx 50/org) ordenados por favoritos
3. Criação com: nome, descrição, ícone (target/activity/bar-chart/shield/zap/flame), 7 focos (%)
4. Duplicar template existente como base
5. Toggle favorito (estrela)
6. Hard delete (sem soft delete)
* **Evidência**: `ConfiguracoesClient.tsx`, `CreateTemplateModal.tsx`, `EditTemplateModal.tsx`

### Fluxo 10 - Relatório de sessão (Coach):
1. Acessa `/training/relatorio/{sessionId}` após fechar sessão
2. Visualiza análise de desvios: planejado vs executado por foco
3. Outcome da execução (on_time, delayed, canceled, shortened, extended)
4. Notas e observações
* **Evidência**: `RelatorioClient.tsx`

### Rotas de frontend (mapa completo):

| Rota | Componente | Feature |
|------|------------|---------|
| `/training/agenda` | `AgendaClient.tsx` | Agenda semanal + mensal |
| `/training/calendario` | `page.tsx` | Calendário mensal |
| `/training/planejamento` | `PlanejamentoClient.tsx` | Planejamento de ciclos |
| `/training/exercise-bank` | `page.tsx` | Banco de exercícios |
| `/training/analytics` | `AnalyticsClient.tsx` | Analytics & insights |
| `/training/rankings` | `RankingsClient.tsx` | Rankings dashboard |
| `/training/eficacia-preventiva` | `PreventionDashboardClient.tsx` | Eficácia preventiva |
| `/training/configuracoes` | `ConfiguracoesClient.tsx` | Templates & configurações |
| `/training/presencas` | `page.tsx` | Presenças (attendance) |
| `/training/relatorio/[sessionId]` | `RelatorioClient.tsx` | Relatório de sessão |

### Fricções conhecidas:
* Load time ocasional em analytics dashboard com dados extensos
* Mobile UX não otimizada para formulários wellness
* Rankings dashboard com dados limitados quando histórico < 3 meses

### Evidência:
* Frontend components em `Hb Track - Fronted/src/app/(admin)/training/` e `Hb Track - Fronted/src/components/training/`

## 11. Telemetria e métricas (AS-IS)

### O que é medido hoje:
* **Performance metrics**: 17 cached calculations incluindo load analysis, deviation tracking
* **Usage analytics**: wellness response rates, badge achievement rates, session creation frequency
* **System metrics**: cache hit rates, API response times básicos

### O que não é medido:
* **User experience metrics**: task completion rates, user satisfaction, abandonment points
* **Advanced performance**: detailed query performance, frontend load times
* **Business metrics**: feature adoption rates, user engagement depth

### Evidência: 
* Analytics implementation, training_analytics_cache service, basic logging configs

## 12. Riscos e mitigação (no estado atual)

### Risco: Data loss em wellness submissions
* **Impacto**: Alto (dados sensíveis LGPD)
* **Probabilidade**: Baixa
* **Mitigação atual**: Database transactions, backup automático
* **Gap**: Validação de integridade referencial necessária

### Risco: Performance degradation em analytics
* **Impacto**: Médio (UX impact)
* **Probabilidade**: Média (com scale)
* **Mitigação atual**: Redis caching, calculation optimization
* **Gap**: Monitoring e alerting proativo

### Risco: LGPD non-compliance
* **Impacto**: Alto (legal/regulatório)
* **Probabilidade**: Baixa
* **Mitigação atual**: Retention policies confirmadas; export/audit trails — **Confirmado** (`athlete_data_export_service.py:389-398`, INV-TRAIN-019)
* **Gap**: Regular compliance auditing process

### Risco: Unauthorized access cross-tenant
* **Impacato**: Alto (data breach)
* **Probabilidade**: Baixa
* **Mitigação atual**: Organization-scoped queries, RBAC middleware
* **Gap**: Penetration testing, access reviews

## 13. Lacunas conhecidas (backlog de correção, sem virar futuro no PRD)

### ~~Gap-001: Template configuration UI incompleta~~ — **FECHADO**
* **Resolução**: Backend com `ctx.requires` em todos endpoints (`session_templates.py:54,100,179,222,323,374`). Frontend com gating por `permission_keys` (`ConfiguracoesClient.tsx:56,69,75`). UI completa: create, edit, delete, duplicate, favorite.
* **Evidência de fechamento**: TRD v1.6 §1.1 GAP-001 CLOSED/VERIFIED
* **Data**: 2026-02-08

### ~~Gap-002: E2E test suite não executado completamente~~ — **FECHADO**
* **Resolução**: E2E executado com sucesso: `pytest tests/e2e/test_training_flow_e2e.py -q` → 1 passed in 5.29s
* **Evidência de fechamento**: TRD v1.6 §1.1 GAP-002 CLOSED/VERIFIED
* **Data**: 2026-02-08

### Gap-003: Mobile UX não otimizada
* **Evidência**: Wellness forms not responsive-optimized
* **Impacto**: Athlete experience degraded em mobile devices
* **Priority**: Medium (affects user adoption)

### Gap-004: Advanced performance monitoring
* **Evidência**: Basic logging only, no APM integration
* **Impacto**: Difficult to troubleshoot performance issues
* **Priority**: Low (system currently performing adequately)

### Gap-005: Regras/efeitos não verificados no código
* **Evidência**: Regras/efeitos como audit trails, notificações de status, cache refresh daily e interface de export sem validação localizada (ver TRD)
* **Impacto**: Comportamento pode diferir da documentação; regras podem não estar sendo aplicadas
* **Priority**: Medium (definir se são regras de negócio a implementar ou specs incorretas)

## 14. Critérios de verificação do baseline ("gates")

Para marcar este PRD como **VERIFIED**:

* ✅ Todo PRD-FR possui Evidência mínima preenchida (OpenAPI/Schema/TRD + UI + Test)
* ✅ Papéis e invariantes referenciam docs RBAC/Security e evidências _generated
* ✅ NFRs não comprovados marcados como "Estimado" ou "Desconhecido"
* ✅ _generated atualizado em 2026-01-29T10:05:14.823044Z (commit e02c83ef)
* ✅ Manifest.json confirma integridade dos arquivos gerados
* ⏳ Revisão concluída por Davi Sermenho (Product Owner)
* ⏳ Validação technical review por Tech Lead
* ⏳ Confirmation que manifest.json e PRD estão alinhados ao mesmo commit

## 15. Histórico de mudanças do documento

* **v1.3** (2026-02-08): Eliminação de dívida técnica de documentação. Adicionados PRD-FR-010 (Alertas e Sugestões), PRD-FR-011 (Attendance), PRD-FR-012 (Training Analytics Insights). FR-008 atualizado de Parcial para Ativo. Gap-001 e Gap-002 fechados (evidência TRD v1.8). Escopo expandido para 12 FRs. Completude atualizada de 93.5% para 97%. UX flows expandidos com 8 novos fluxos de frontend (10 rotas documentadas). Referência TRD atualizada para v1.8.
* **v1.2** (2026-02-07): Alinhado ao TRD v1.6. Reconciliação de PRETENDIDO: audit logs, internal_load trigger, cache refresh, overload alerts, export audit trails promovidos para Confirmado com evidência file:line. Badge eligibility reclassificado como Futuro V1.1. SLAs cross-referenciados ao PRD_HB_TRACK §10.7.
* **v1.1** (2026-01-29): Alinhado ao TRD v1.5 (status, deadlines, escopo), inferências marcadas como PRETENDIDO, snapshot sincronizado
* **v1.0** (2026-01-29): Criação inicial do baseline AS-IS baseado em estado 93.5% do módulo TRAINING, evidências regeneradas via scripts/generate_docs.py com manifesto de rastreabilidade (commit e02c83ef), snapshot atual do sistema consolidado

---

**Documento criado por**: GitHub Copilot (Claude Sonnet 4)
**Baseline Owner**: Product Owner / Tech Lead
**Revisores/Assinatura**: Davi Sermenho (pendente)
**Status atual**: DRAFT (aguardando review para VERIFIED)
**Manifesto de evidências**: commit e02c83ef | 2026-01-29T10:05:14.823044Z
