---
description: Feature modules documentation index
---

# Módulos por Feature

Documentação de funcionalidades principais, organizadas por módulo.

---

## 📑 Quick Find

Procurando documentação sobre um módulo?

| Módulo | Descrição | Status | Docs |
|--------|-----------|--------|------|
| **Athletes** | Atletas, badges, wellness tracking | 🟢 STABLE | `athletes/` |
| **Teams** | Times, memberships, registrations | 🟢 STABLE | `teams/` |
| **Training** | Ciclos, sessões, invariantes | 🟢 STABLE | `training/` |
| **Games** | Competições, matches, eventos | 🟡 PARTIAL | `games/` |
| **Statistics** | Analytics, dashboards, reports | 🟡 PARTIAL | `statistics/` |
| **Auth** | RBAC, permissões, access control | 🟢 STABLE | `auth/` |

---

## 🟢 Stable Modules

### Athletes (`athletes/`)
**Purpose:** Gerenciar perfis de atletas, badges, e wellness.

**Key Files:**
- `README.md` — Visão geral do módulo
- `MODELS.md` — Schema SQLAlchemy
- `API.md` — Endpoints REST
- `TESTS.md` — Cobertura de testes

**Status:** Produção, mudanças raras  
**Dependencies:** Teams, Training  
**Teste Coverage:** 85%+

**Quick Questions:**
- Qual é a estrutura de badges? → `MODELS.md: badges column`
- Como fitness score é calculado? → `API.md: GET /athletes/{id}/fitness`
- Integração com wellness? → `athletes/wellness/README.md`

---

### Teams (`teams/`)
**Purpose:** Gerenciar times, memberships, e registrações.

**Key Files:**
- `README.md` — Visão geral
- `MODELS.md` — Schema (note: ciclo FK com seasons)
- `ROTAS.md` — Routes & endpoints
- `MEMBERSHIPS.md` — Member lifecycle

**Status:** Produção, FK cycles mitigated (use_alter=True)  
**Dependencies:** Athletes, Training  
**Teste Coverage:** 80%+

**Quick Questions:**
- Por que teams↔seasons tem ciclo FK? → `MODELS.md: use_alter=True mitigation`
- Como adicionar membro? → `MEMBERSHIPS.md: POST /teams/{id}/members`
- Soft delete implementado? → `README.md: secciones lifecycle`

---

### Training (`training/`)
**Purpose:** Gerenciar ciclos de treinamento, sessões, invariantes.

**Key Files:**
- `README.md` — Visão geral
- `MODELS.md` — Schema (training_cycles, sessions, exercises)
- `INVARIANTS/` — Rules library (INVARIANTS_TRAINING.md)
- `PROTOCOLS/` — Operational guides
- `ADRs/` — Architecture decisions (001-012)

**Status:** Ativo, invariantes em desenvolvimento  
**Dependencies:** Athletes, Teams  
**Teste Coverage:** 70%+ (crescendo)

**Quick Questions:**
- Quais regras de validação existem? → `INVARIANTS/INVARIANTS_TRAINING.md`
- Como adicionar nova invariante? → `/install-invariant` no Copilot
- Schema treino? → `MODELS.md`
- Lifecycle de sessão? → `PROTOCOLS/SESSION_LIFECYCLE.md`

---

## 🟡 Partial Modules (Under Development)

### Games (`games/`)
**Purpose:** Competições, matches, eventos.

**Status:** Parcialmente implementado  
**Coverage:** API endpoints 60%, Models 70%  
**Next:** Implementar relatórios de jogos

**Docs:**
- `README.md` — Overview
- `ROADMAP.md` — Próximas features
- `MODELS.md` — Schema atual

---

### Statistics (`statistics/`)
**Purpose:** Analytics, dashboards, relatórios.

**Status:** Estrutura base pronta, regras em progress  
**Coverage:** 40%  
**Next:** Dashboard backend, realtime metrics

**Docs:**
- `README.md` — Overview
- `METRICS.md` — Definições de métricas
- `API.md` — Endpoints de analytics

---

## 🔐 Auth Module (`auth/`)
**Purpose:** RBAC, permissões, geração de sessões.

**Key Files:**
- `README.md` — Visão geral RBAC
- `ROLES.md` — Roles definidos (admin, coach, athlete, etc.)
- `PERMISSIONS.md` — Permission matrix
- `SESSION.md` — Token & session management

**Status:** Produção, todas as roles implementadas  
**Dependencies:** Users, Organizations  
**Teste Coverage:** 95%+

**Quick Questions:**
- Qual role tem acesso a relatórios? → `PERMISSIONS.md: reports_view`
- Como adicionar permissão nova? → `AUTH_ADR_*.md`
- Session token expiration? → `SESSION.md: token_ttl`

---

## 🗺️ How to Navigate

### 1. Quero entender arquitetura de X módulo
**Go to:** `docs/02_modulos/<module>/README.md`

### 2. Preciso ver schema de X tabela
**Go to:** `docs/02_modulos/<module>/MODELS.md` or via Copilot: `/models-gate <table>`

### 3. Quero adicionar endpoint novo
**Go to:** `docs/02_modulos/<module>/API.md` + `docs/_canon/03_WORKFLOWS.md`

### 4. Preciso colocar regra de validação em training
**Go to:** `/install-invariant` in Copilot, or `docs/02_modulos/training/INVARIANTS/`

### 5. Encontrei bug em X módulo
**Go to:** `docs/02_modulos/<module>/TESTS.md` (coverage map) + file issue

### 6. Integração entre módulos confusa
**Go to:** `docs/_canon/02_CONTEXT_MAP.md` (dependency graph)

---

## 📊 Module Health Dashboard

| Module | Docs | Tests | Status | Last Update |
|--------|------|-------|--------|-------------|
| Athletes | 95% | 85% | 🟢 STABLE | 2026-02-08 |
| Teams | 90% | 80% | 🟢 STABLE | 2026-02-08 |
| Training | 85% | 70% | 🟢 ACTIVE | 2026-02-10 |
| Games | 60% | 60% | 🟡 PARTIAL | 2026-01-20 |
| Statistics | 50% | 40% | 🟡 PARTIAL | 2026-01-15 |
| Auth | 100% | 95% | 🟢 STABLE | 2026-02-01 |

---

## 🚀 Getting Started

**New to codebase?**

1. Read `docs/_canon/00_START_HERE.md` (10 min)
2. Pick a module above
3. Read `<module>/README.md` (15 min)
4. Explore `<module>/MODELS.md` or `<module>/API.md` depending on your role
5. Ask Copilot: `/models-gate next` or `/parity-fix <table>`

**Want to contribute?**

1. Pick module you care about
2. Read its ROADMAP.md (if exists)
3. Check TESTS.md for coverage gaps
4. Open issue or draft PR
5. See `docs/_canon/10_GIT_PR_MERGE_WORKFLOW.md`

**Need architecture decision?**

See `docs/ADR/` for decisions on:
- Training module lifecycle (ADR-003)
- Invariants as contract (ADR-004)
- Soft delete strategy (ADR-005)
- RBAC design (ADR-011)
- Multi-tenancy (ADR-010)

---

## 📚 Reference

- **Authority:** `docs/_canon/01_AUTHORITY_SSOT.md`
- **Navigation:** `docs/_canon/02_CONTEXT_MAP.md`
- **Workflows:** `docs/_canon/03_WORKFLOWS.md`
- **ADRs:** `docs/ADR/` (architecture decisions)
- **Prompts:** `docs/_ai/06_AGENT-PROMPTS.md` (Copilot integration)
