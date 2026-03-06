# AR_BACKLOG_TEAMS.md

Status: DRAFT  
Versão: v0.1.0  
Tipo de Documento: AR Materialization Backlog (Normativo Operacional / SSOT)  
Módulo: TEAMS  
Fase: FASE_0  
Autoridade: NORMATIVO_OPERACIONAL  
Owners:
- Arquitetura (Arquiteto): Codex (Arquiteto v2.2.0)
- Execução (Executor): (a definir)
- Auditoria/Testes: (a definir)

Última revisão: 2026-03-03  
Próxima revisão recomendada: 2026-03-10  

Dependências:
- INVARIANTS_TEAMS.md
- TEAMS_USER_FLOWS.md
- TEAMS_SCREENS_SPEC.md
- TEAMS_FRONT_BACK_CONTRACT.md
- TEST_MATRIX_TEAMS.md

---

## REGRA SSOT (obrigatória)

**DB/schema.sql > services/domain rules > OpenAPI > frontend > PRD.**

---

## 1) Objetivo (Normativo)

Decompor a materialização do módulo TEAMS em ARs pequenas e auditáveis, com:
- AC binário por AR
- dependências explícitas
- estratégia de validação (inclui tentativas de violação para invariantes BLOQUEANTES)
- caminho até §10 (TEST_MATRIX como SSOT do DONE)

---

## 2) Classes de AR (fatiamento)

- **A** — Banco/Persistência (migrations, constraints, models)
- **B** — Regras de Domínio/Services
- **D** — Frontend/UX
- **E** — Contrato Front-Back / OpenAPI / wiring de router
- **T** — Testes + evidências `_reports/*`
- **G** — Governança: sync de matrizes/§10 (Done Gate)

---

## 3) Auditoria AS-IS (Resumo)

### 3.1 Evidenciado (alto nível)
- `teams` com constraints de gênero/soft delete/datas + trigger anti-delete físico.  
  Evidência: `docs/ssot/schema.sql` âncora `CREATE TABLE public.teams`.
- Endpoints TEAMS expostos em OpenAPI para CRUD/settings/coach/staff e rotas `/members/*` de convite.  
  Evidência: `docs/ssot/openapi.json` âncora `operationId: create_team_api_v1_teams_post`.
- Frontend Teams V2 com rotas `/teams/*` e consumo de `/teams` paginado.  
  Evidência: `Hb Track - Frontend/src/components/teams-v2/DashboardV2.tsx` âncora `teamsService.list({ page, limit })`.

### 3.2 Divergências/GAPS (bloqueantes)

| GAP ID | Severidade | Descrição | Evidência mínima |
|---|---|---|---|
| GAP-TEAMS-001 | BLOQUEANTE | `GET /teams` OpenAPI=lista; FE/service=paginação (`items/total`) | `docs/ssot/openapi.json` âncora `"/api/v1/teams": { "get": ... }` |
| GAP-TEAMS-002 | BLOQUEANTE | Convites RESTful `/teams/{id}/invites` usados no FE/E2E, mas não existem no OpenAPI SSOT atual | `Hb Track - Frontend/src/lib/api/teams.ts` âncora `createTeamInvite` |
| GAP-TEAMS-003 | BLOQUEANTE | `DELETE /teams/{id}` motivo: FE manda body; BE lê query | `Hb Track - Backend/app/api/v1/routers/teams.py` âncora `delete_team` |
| GAP-TEAMS-004 | BLOQUEANTE | Shape staff: FE usa `role_id`; BE retorna `role` string | `Hb Track - Frontend/src/components/teams-v2/MembersTab.tsx` âncora `staffRoleIds.includes(member.role_id)` |
| GAP-TEAMS-005 | BLOQUEANTE | `TeamGender` FE inclui `misto` mas DB bloqueia | `Hb Track - Frontend/src/lib/api/teams.ts` âncora `TeamGender` |
| GAP-TEAMS-006 | BLOQUEANTE | PRD RDB10 (temporada) vs DB `team_registrations` sem season_id | `docs/hbtrack/PRD Hb Track.md` âncora `RDB10` |

---

## 4) Tabela Resumo do Backlog de ARs

| AR ID | Classe | Prioridade | Objetivo | Alvos SSOT | Dependências | Status |
|---|---|---|---|---|---|---|
| AR-TEAMS-001 | E | CRITICA | Normalizar contrato `GET /teams` (paginação) + remover drift OpenAPI | CONTRACT-TEAMS-001, INV-TEAMS-017 | — | PENDENTE |
| AR-TEAMS-002 | E | CRITICA | Expor rotas RESTful `/invites` e sincronizar OpenAPI | FLOW-TEAMS-007, CONTRACT-TEAMS-020..023, INV-TEAMS-006/007/013/014 | AR-TEAMS-001 | PENDENTE |
| AR-TEAMS-003 | E | ALTA | Alinhar contrato de `DELETE /teams/{id}` (reason query vs body) | CONTRACT-TEAMS-005, INV-TEAMS-019 | AR-TEAMS-001 | PENDENTE |
| AR-TEAMS-004 | E | ALTA | Definir shape canônico de staff (role vs role_id) + OpenAPI sync | CONTRACT-TEAMS-009, INV-TEAMS-018 | AR-TEAMS-001 | PENDENTE |
| AR-TEAMS-004D | D | ALTA | Ajustar MembersTab para shape canônico de staff | SCREEN-TEAMS-004, FLOW-TEAMS-003 | AR-TEAMS-004 | PENDENTE |
| AR-TEAMS-005 | A | ALTA | Decidir e alinhar domínio `gender` (inclui/exclui `misto`) | INV-TEAMS-001, INV-TEAMS-021 | DEC-TEAMS-001 | PENDENTE |
| AR-TEAMS-006A | A | CRITICA | Materializar RDB10 em DB (season_id + constraints/indexes) OU formalizar decisão alternativa | INV-TEAMS-020 | DEC-TEAMS-002 | PENDENTE |
| AR-TEAMS-006B | B | CRITICA | Ajustar services/routers `team_registrations` para o modelo decidido | CONTRACT-TEAMS-013..016 | AR-TEAMS-006A | PENDENTE |
| AR-TEAMS-007 | T | CRITICA | Contract tests TEAMS P0 + evidências `_reports/*` | TEST-TEAMS-CONTRACT-* | AR-TEAMS-001,002,003,004,005,006B | PENDENTE |
| AR-TEAMS-008 | T | ALTA | E2E/MANUAL_GUIADO flows P0 + evidências | TEST-TEAMS-FLOW-* / TEST-TEAMS-SCREEN-* | AR-TEAMS-001,002,003,004D,005,006B | PENDENTE |
| AR-TEAMS-009 | G | CRITICA | Done Gate §10: sync TEST_MATRIX_TEAMS + evidências | §10 (TEST_MATRIX_TEAMS.md) | AR-TEAMS-007..008 | PENDENTE |

---

## 5) Decisões pendentes (validação humana)

### DEC-TEAMS-001 — Domínio de gênero inclui `misto`?

- **Contexto:** FE tipa `misto`, DB bloqueia por `ck_teams_gender`.
- **Impacto:** migration + contratos + validações + filtros.
- **SSOT atual:** DB.

### DEC-TEAMS-002 — Como materializar RDB10 (temporada) em `team_registrations`?

- **Contexto:** PRD exige temporada; DB atual (SSOT) não tem `season_id` na tabela `team_registrations`.
- **Opções (alto nível):**
  - (A) adicionar `season_id` + constraints/indexes e ajustar serviços/rotas;
  - (B) reinterpretar RDB10 para o modelo atual e atualizar PRD (governança).

### DEC-TEAMS-003 — Quem pode “Criar equipe” (Treinador ou não)?

- **Contexto:** PRD (RACI) sugere Treinador como Consulted; repo (FE/BE) permite Treinador criar.
