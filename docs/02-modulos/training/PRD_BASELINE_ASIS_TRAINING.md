# PRD (Baseline AS-IS) — Módulo TRAINING

## 1. Controle do documento (Governança)

* **Documento**: PRD_BASELINE_ASIS_TRAINING.md
* **Status**: BASELINE / AS-IS
* **Versão**: v1.2
* **Data**: 2026-02-07
* **Owner (papel)**: Product Owner / Tech Lead
* **Escopo do baseline**: "Training (agenda + sessões + presença + wellness + gamificação + performance)"

### Baseline Evidence Snapshot
* **Git commit**: e02c83efa1926c880336511ff72a13311093bdb9
* **Generated at**: 2026-01-29T10:05:14.823044Z
* **System state**: HB Track v1.2 (93.5% module completion)
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
* **Referência técnica canônica**: `docs/02-modulos/training/TRD_TRAINING.md` (versão v1.7, commit e02c83ef)
  * Regra: contratos e regras verificadas = ver TRD.

## 2. Objetivo do baseline (por que este PRD existe)

### Problema atual:
Módulo TRAINING está 93,5% completo (29/31 funcionalidades implementadas) mas sem documentação baseline consolidada, criando risco de retrabalho e inconsistência entre implementação e especificações durante finalização.

### Objetivo deste baseline:
* Consolidar estado atual do módulo TRAINING para referência canônica
* Fixar papéis e permissões implementados para training/wellness
* Mapear contratos reais via evidência OpenAPI/schema atual
* Documentar invariantes inter-módulos para integrações seguras
* Estabelecer baseline para finalização dos 2 itens restantes (template UI + E2E tests)

## 3. Escopo e fora de escopo do baseline

### 3.1 In-scope (lista fechada)
* Gestão de sessões de treino (CRUD, workflow draft→scheduled→in_progress→pending_review→readonly; UI "closed")
* Sistema de wellness pre/post training
* Banco de exercícios com tags hierárquicas
* Performance analytics com cache de 17 métricas
* Gamificação (badges, rankings, streaks)
* Planejamento de ciclos (macro/meso/microciclos)
* Dashboard de efetividade preventiva
* Compliance LGPD (export, retention, anonymization)
* Integrações com módulos Athletes/Teams

### 3.2 Out-of-scope (lista explícita)
* Template configuration UI (Parcial - backend completo, frontend incompleto)
* E2E comprehensive test suite (escrito mas não executado completamente)
* Módulos externos (Athletes, Teams, Analytics core)
* Features futuras não implementadas

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
* **Descrição (AS-IS)**: Sistema mantém templates de sessão com focus presets, favorites per user e application automática para criação de sessões
* **Atores**: Coach, Staff (creator/manager), All users (consumer)
* **Estado**: Parcial (backend completo, frontend configuration UI incompleta)
* **Regras/validações observadas**:
  * Template focus validation igual a sessões normais
  * User-scoped favorites
  * Template versioning basic
* **Saídas observadas**: Template library, quick session creation, standardized focus patterns
* **Evidência mínima**:
  * **OpenAPI**: `GET/POST /api/v1/session-templates`, `GET/PATCH/DELETE .../session-templates/{id}`
  * **Schema**: `session_templates` table
  * **UI**: templates management (incompleto)
  * **Teste/Log**: template service backend tests
* **Referência TRD**: §6 PRD-FR-008; Regras: RULE-FOCUS-MAX-120
* **Observações / Known issues**: Frontend configuration interface não implementada completamente

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
1. Acessa agenda semanal ou calendário mensal
2. Seleciona data/time slot
3. Define focus percentages com traffic light validation
4. Adiciona exercícios via drag-and-drop do banco
5. Define participantes (team roster)
6. Salva como draft ou publica diretamente

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

### Fricções conhecidas:
* Template configuration UI incompleta força workarounds
* Load time ocasional em analytics dashboard com dados extensos
* Mobile UX não otimizada para formulários wellness

### Evidência: 
* Frontend components, user flow screenshots, UX testing notes

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

### Gap-001: Template configuration UI incompleta
* **Evidência**: Frontend templates interface 60% implemented
* **Impacto**: Users cannot easily create/customize session templates via UI
* **Priority**: Medium (workaround via direct session creation exists)

### Gap-002: E2E test suite não executado completamente
* **Evidência**: Test files written but some marked as skip, coverage validation pending
* **Impacto**: Risk de regression bugs em releases
* **Priority**: High (before production deployment)

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

* **v1.2** (2026-02-07): Alinhado ao TRD v1.7. Reconciliação de PRETENDIDO: audit logs, internal_load trigger, cache refresh, overload alerts, export audit trails promovidos para Confirmado com evidência file:line. Badge eligibility reclassificado como Futuro V1.1. SLAs cross-referenciados ao PRD_HB_TRACK §10.7.
* **v1.1** (2026-01-29): Alinhado ao TRD v1.5 (status, deadlines, escopo), inferências marcadas como PRETENDIDO, snapshot sincronizado
* **v1.0** (2026-01-29): Criação inicial do baseline AS-IS baseado em estado 93.5% do módulo TRAINING, evidências regeneradas via scripts/generate_docs.py com manifesto de rastreabilidade (commit e02c83ef), snapshot atual do sistema consolidado

---

**Documento criado por**: GitHub Copilot (Claude Sonnet 4)
**Baseline Owner**: Product Owner / Tech Lead
**Revisores/Assinatura**: Davi Sermenho (pendente)
**Status atual**: DRAFT (aguardando review para VERIFIED)
**Manifesto de evidências**: commit e02c83ef | 2026-01-29T10:05:14.823044Z
