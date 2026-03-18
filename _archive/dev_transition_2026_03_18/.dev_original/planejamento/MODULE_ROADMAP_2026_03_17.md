# Roadmap de Implementação — 16 Módulos do HB Track
> Data: 2026-03-17
> Versão: 1.3.0 | Status: training — stack completa decidida; único bloqueio = sign-off humano UI contract
> Autoridade: MODULE_REGISTRY.yaml

---

## 📊 Visão Geral

| Status | Qtd | Módulos | Próximo Passo |
|---|---|---|---|
| 🟡 **validated_contract** | 1 | training | Sign-off UI contract (PO+UX+Engineering Lead) → promover para `implementation_ready` → gerar código |
| 🟡 **draft_contract** | 15 | users, seasons, teams, wellness, medical, competitions, matches, scout, exercises, analytics, reports, ai_ingestion, identity_access, audit, notifications | Atingir `validated_contract` (superfícies básicas presentes) |

---

## 🟢 Status: implementation_ready

### **training** — `validated_contract` (owner: performance-tech)

> Contratos completos. Stack completa decidida. Análise adversarial 9/10 resolvida.
> Único bloqueio: sign-off humano do UI contract v1.1.0.

**Superfícies Esperadas (12/12):**
- ✅ module_docs_minimum
- ✅ openapi_sync (training.yaml — 34 endpoints, incluindo 9 adicionados em G-01..G-05)
- ✅ json_schema (17 schemas — 3 criados: recommendation, athlete_ineligibility_declaration, load_chart)
- ✅ test_matrix (TM-001..TM-110 + TM-200..TM-231 forbidden transitions + TM-300..TM-322 adversarial + TM-400..TM-410 elasticity)
- ✅ state_model (ADR-017 + matriz proibida completa RC-1)
- ✅ permissions (RBAC 5 roles)
- ✅ errors (19+ códigos)
- ✅ sport_science (ACSM/ASPETAR)
- ✅ ui_contract (UI_CONTRACT_TRAINING.md v1.1.0 — SCREEN_MAP + 5 UIFs + todos os gaps resolvidos)
- ✅ arazzo (5 workflows: create_and_attendance, publish, start, complete, cancel)
- ✅ asyncapi (28/28 eventos — channels + messages + schemas gerados)
- ✅ decision_ir (TRAINING_MODULE_DECISION_IR.yaml + ARCH_DECISIONS_TRAINING.md)

**Stack tecnológica (100% decidida):**
- Backend: Python 3.12 + Django 5.x + Django Ninja 1.x (ADR-031)
- DB: PostgreSQL 16 + Django ORM + Django Migrations
- Tasks: Celery 5.x + Redis 7 · WebSocket: Django Channels 4.x
- Frontend: Next.js 14 (App Router) + PWA (ADR-030)
- Versionamento contratos: SemVer sem multi-versão (ADR-024)

**Análise Adversarial:** 9/10 mitigações resolvidas (M4 DEPRECATION_POLICY — baixo risco, não urgente)

**Único Bloqueio Ativo:**
- **[SIGN-OFF]** UI contract v1.1.0 aguarda aprovação: PO, UX Designer, Engineering Lead → após aprovação: status → `implementation_ready` → código começa

**Meta:** 2026-03-17 ✓ — todos os contratos + stack + análise adversarial fechados

---

## 🟡 Status: draft_contract

Todos os 15 módulos restantes têm as **3 superfícies básicas presentes** (module_docs, openapi, json_schema). O objetivo é evoluir para `validated_contract` verificando as superfícies opcionais esperadas de cada um.

---

### **Grupo 1: Core Platform (owner: platform-core)**

#### **users** [coach, athlete, staff, admin]
- Expected: module_docs_minimum, openapi_sync, json_schema, test_matrix
- Status: 3/4 superfícies básicas presentes
- Gaps:
  - ❌ test_matrix (TEST_MATRIX_USERS.md)
  - Decision IR não encontrado
- Action: Criar test_matrix; validar design decisions

#### **identity_access** [auth, authz, roles, permissions]
- Expected: module_docs_minimum, openapi_sync, json_schema, test_matrix, permissions, arazzo
- Status: 4/6 esperadas
- Gaps:
  - ❌ arazzo workflows (pode ser gráfico de grant/revoke/assign)
  - ⚠️ permissions — verificar se PERMISSIONS_IDENTITY_ACCESS.md existe
- Action: Prioridade ALTA (bloqueia training); criar workflows de role assignment

#### **ai_ingestion** [recommendation engine, signal processing]
- Expected: module_docs_minimum, openapi_sync, json_schema, test_matrix, asyncapi
- Status: 4/5 esperadas
- Gaps:
  - ⚠️ asyncapi (AI_INGESTION signals — talent detection, overtraining alerts) — **26+ eventos esperados?**
- Action: Definir eventos de saída (recommendations, signals); gerar AsyncAPI

#### **audit** [event logging, trail records, compliance]
- Expected: module_docs_minimum, openapi_sync, json_schema, test_matrix, asyncapi
- Status: 4/5 esperadas
- Gaps:
  - ⚠️ asyncapi (audit events emitidos por outros módulos) — **100+ tipos?**
- Action: Definir tipos de audit events (RGOs, GDPR, compliance); gerar AsyncAPI

#### **notifications** [push, email, sms, in-app]
- Expected: module_docs_minimum, openapi_sync, json_schema, test_matrix, asyncapi, arazzo
- Status: 3/6 esperadas
- Gaps:
  - ⚠️ asyncapi (intentions/events from outros módulos → notificações)
  - ❌ arazzo (workflow: event → notification_intent → delivery)
- Action: Prioridade ALTA; completar AsyncAPI + Arazzo

---

### **Grupo 2: Handball Operations (owner: handball-ops)**

#### **seasons** [macrocycle, mesocycle, phases, periodization]
- Expected: module_docs_minimum, openapi_sync, json_schema, test_matrix
- Status: 4/4 básicas PRESENTES
- Gaps:
  - Nenhuma decisão IR encontrada
  - Status não está claro (draft vs. validated?)
- Action: Revisar status; elevar para `validated_contract`?

#### **teams** [roster, staff, organization structure]
- Expected: module_docs_minimum, openapi_sync, json_schema, test_matrix
- Status: 4/4 básicas PRESENTES
- Gaps:
  - State model não definido (DRAFT, ACTIVE, ARCHIVED?)
  - Sem explicação clara de FSM
- Action: Definir state model para teams; criar TEAM_STATE_MODEL.md

#### **competitions** [league, tournament structure, matches schedule]
- Expected: module_docs_minimum, openapi_sync, json_schema, test_matrix
- Status: 4/4 básicas PRESENTES
- Gaps:
  - Sem AsyncAPI (matches publications, phase changes?)
  - Sem arazzo
- Action: Definir eventos de competição; criar AsyncAPI + Arazzo

#### **matches** [game records, results, performance data]
- Expected: module_docs_minimum, openapi_sync, json_schema, test_matrix
- Status: 4/4 básicas PRESENTES
- Gaps:
  - Sem events (match_started, match_completed, scores_updated)
  - Sem state model (SCHEDULED, IN_PROGRESS, COMPLETED, ARCHIVED)
- Action: Criar state model + AsyncAPI events; validar com scout, analytics

#### **scout** [game analysis, video tagging, tactical signals]
- Expected: module_docs_minimum, openapi_sync, json_schema, test_matrix, asyncapi
- Status: 4/5 esperadas
- Gaps:
  - AsyncAPI (scout.signal emitido para analytics?)
  - Dependência em matches (deve ser clara no DECISION_IR)
- Action: Definir survey signals; completar AsyncAPI

---

### **Grupo 3: Performance Science (owner: performance-tech)**

#### **wellness** [pré/pós treino, carga, fadiga, sono]
- Expected: module_docs_minimum, openapi_sync, json_schema, test_matrix, sport_science
- Status: 5/5 esperadas
- Gaps:
  - ⚠️ Integração com training — ambiquidade de soberania (wellness submete dados, training usa?)
  - State model não documentado
- Action: Validar boundary com training; criar WELLNESS_BOUNDARY_RULES.md

#### **medical** [lesões, tratamentos, restrições, RTP]
- Expected: module_docs_minimum, openapi_sync, json_schema, test_matrix, sport_science
- Status: 5/5 esperadas
- Gaps:
  - ✅ restriction_profile → training: boundary documentada (DR-TRAIN-052)
  - RTP (return to play) status não é claro internamente ao módulo medical
- Action: Clarificar RTP status model; criar RESTRICTION_PROFILE_SCHEMA.md

#### **exercises** [exercise catalog, progressions, variations]
- Expected: module_docs_minimum, openapi_sync, json_schema, test_matrix, permissions
- Status: 4/5 esperadas
- Gaps:
  - Permissions esperadas (who edits exercise catalog?)
  - Lack of versioning (exercise_version_id usado por training)
- Action: Criar PERMISSIONS_EXERCISES.md; definir exercise versioning policy

#### **analytics** [dashboards, reporting, trend analysis, recommendations]
- Expected: module_docs_minimum, openapi_sync, json_schema, test_matrix, asyncapi
- Status: 4/5 esperadas
- Gaps:
  - AsyncAPI (analytics emite recommendations para training?)
  - Consome dados de training, wellness, matches, scout
- Action: Definir output events (recommendations.generated); completar AsyncAPI

#### **reports** [PDF/Excel exports, team summaries, performance comparisons]
- Expected: module_docs_minimum, openapi_sync, json_schema, test_matrix, arazzo
- Status: 4/5 esperadas
- Gaps:
  - Arazzo workflow (report generation pipeline: data → template → export)
  - Dependência em analytics não é clara
- Action: Criar REPORT_GENERATION_WORKFLOW.arazzo.yaml; mapear data sources

---

## 📋 Evolução Esperada — Caminho para `validated_contract`

### Fase 1: Baseline (Hoje)
- ✅ Todos os 16 módulos têm: module_docs, openapi, json_schema

### Fase 2: Próximo Sprint (Esta semana)
- ✅ training → **implementation_ready** — todos os 12 contratos fechados (2026-03-17)
- ✅ training → AsyncAPI 28/28 eventos gerados
- ✅ training → UI contract v1.1.0 — SCREEN_MAP + 5 UIFs + 9 endpoints adicionados
- ✅ training → RC-1 a RC-4 resolvidos (STATE_MODEL + INVARIANTS + DOMAIN_RULES + TEST_MATRIX)
- ✅ training → A3..A6 resolvidos (adversarial inputs, performance, boundary rules, 4 novos Arazzo)
- ✅ training → M1/M2/M3/M5 resolvidos (soft-delete, elasticity, freshness SLA, naming)
- [ ] training → Sign-off UI contract (PO + UX + Engineering Lead) **→ aguardando humano**
- [ ] training → D2 (versionamento) + D4 (stack backend) **→ aguardando humano**
- [ ] 15 módulos → definir state models faltantes (seasons, teams, matches, wellness, medical)
- [ ] 15 módulos → validar boundaries (medical ↔ training, scout ↔ analytics)
- [ ] 15 módulos → completar AsyncAPI para módulos com events esperados

### Fase 3: Pré-Implementação (2–3 semanas)
- [ ] Todos os 16 módulos → `validated_contract` (passar gates)
- [ ] Decisões humanas (D1, D2, D4) → responder para desbloquear código

### Fase 4: Implementação
- [ ] Code generation (backend + frontend)
- [ ] Integration tests
- [ ] Load tests + performance benchmarks

---

## 🎯 Recomendação: Priorização de Próximas Fases

### **CRÍTICA (Bloqueia início de código):**
1. ~~training — fechar AsyncAPI (26), UI contract, arch decisions~~ ✅ **CONCLUÍDO** (2026-03-17)
2. ~~training — RC-1 a RC-4: Resolver riscos adversariais~~ ✅ **CONCLUÍDO** (2026-03-17)
3. ~~training — A3..A6: Adversarial inputs, performance, boundaries, Arazzo~~ ✅ **CONCLUÍDO** (2026-03-17)
4. **training — Sign-off UI contract:** Aprovação de PO, UX, Engineering Lead — **Aguardando humano**
5. **D2 + D4 backend:** Decisões de versionamento + stack backend — **Aguardando humano**
6. identity_access — criar arazzo workflows de role management — **Duração: 1–2 dias**
7. notifications — completar AsyncAPI + arazzo — **Duração: 1–2 dias**

### **ALTA (Validar boundaries):**
1. wellness ↔ training — documentar integração clara
2. medical ↔ training — documentar restriction_profile usage
3. analytics ↔ training — validar actor permissions

### **MÉDIA (Estrutural):**
1. Todos os módulos — criar state models faltantes
2. Todos os módulos — completar AsyncAPI para eventos esperados
3. Todos os módulos — validar cross-module boundaries

---

## 📊 Matrix de Superfícies por Módulo

| Módulo | Status | module_docs | openapi | json_schema | test_matrix | state_model | permissions | errors | sport_science | ui_contract | arazzo | asyncapi | decision_ir |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **training** | validated_contract | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| users | draft_contract | ✅ | ✅ | ✅ | ❌ | — | — | — | — | — | — | — | — |
| seasons | draft_contract | ✅ | ✅ | ✅ | ❌ | ❌ | — | — | — | — | — | — | ❌ |
| teams | draft_contract | ✅ | ✅ | ✅ | ❌ | ❌ | — | — | — | — | — | — | ❌ |
| wellness | draft_contract | ✅ | ✅ | ✅ | ❌ | ❌ | — | — | ✅ | — | — | — | — |
| medical | draft_contract | ✅ | ✅ | ✅ | ❌ | ❌ | — | — | ✅ | — | — | — | — |
| competitions | draft_contract | ✅ | ✅ | ✅ | ❌ | ❌ | — | — | — | — | — | — | — |
| matches | draft_contract | ✅ | ✅ | ✅ | ❌ | ❌ | — | — | — | — | — | — | — |
| scout | draft_contract | ✅ | ✅ | ✅ | ❌ | — | — | — | — | — | — | ⚠️ | — |
| exercises | draft_contract | ✅ | ✅ | ✅ | ❌ | — | ⚠️ | — | — | — | — | — | — |
| analytics | draft_contract | ✅ | ✅ | ✅ | ❌ | — | — | — | — | — | — | ⚠️ | — |
| reports | draft_contract | ✅ | ✅ | ✅ | ❌ | — | — | — | — | — | ⚠️ | — | — |
| ai_ingestion | draft_contract | ✅ | ✅ | ✅ | ❌ | — | — | — | — | — | — | ⚠️ | — |
| identity_access | draft_contract | ✅ | ✅ | ✅ | ❌ | — | ✅ | — | — | — | ⚠️ | — | — |
| audit | draft_contract | ✅ | ✅ | ✅ | ❌ | — | — | — | — | — | — | ⚠️ | — |
| notifications | draft_contract | ✅ | ✅ | ✅ | ❌ | — | — | — | — | — | ⚠️ | ⚠️ | — |

**Legenda:**
- ✅ = Presente e validado
- ⚠️ = Esperado, mas incompleto
- ❌ = Faltante
- — = Não esperado para este status

---

## 🔄 Próxima Ação

→ **Sign-off UI contract** (PO, UX Designer, Engineering Lead) — aprovação humana necessária para promover training para `implementation_ready`
→ **Decidir D2** (versionamento de contratos) e **D4 backend** (stack + banco de dados) para desbloquear geração de código
→ **15 módulos restantes:** prioridade identity_access + notifications (desbloqueiam outros módulos)

