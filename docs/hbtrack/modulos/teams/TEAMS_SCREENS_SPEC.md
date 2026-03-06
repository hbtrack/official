# TEAMS_SCREENS_SPEC.md

Status: DRAFT  
Versão: v0.1.0  
Tipo de Documento: Screens Specification (Normativo Operacional / SSOT)  
Módulo: TEAMS  
Fase: FASE_0  
Autoridade: NORMATIVO_OPERACIONAL  
Owners:
- Arquitetura (Arquiteto): Codex (Arquiteto v2.2.0)
- Frontend: (a definir)
- Auditoria: (a definir)

Última revisão: 2026-03-03  
Próxima revisão recomendada: 2026-03-17  

Dependências:
- INVARIANTS_TEAMS.md
- TEAMS_USER_FLOWS.md
- TEAMS_FRONT_BACK_CONTRACT.md
- AR_BACKLOG_TEAMS.md

---

## REGRA SSOT (obrigatória)

**DB/schema.sql > services/domain rules > OpenAPI > frontend > PRD.**

---

## 1) Objetivo (Normativo)

Especificar os estados funcionais mínimos das telas do módulo TEAMS (loading/error/empty/data/blocked) para implementação e para smoke/E2E.

---

## 2) Escopo (ETAPA 0)

### 2.1 Dentro do escopo
- Dashboard de equipes
- Detalhe de equipe com tabs (overview/members/settings)
- Estados mínimos de erro/empty/sucesso

### 2.2 Fora do escopo
- Pixel-perfect, animações e refinamentos visuais
- Conteúdo e regras detalhadas de Treinos/Jogos/Analytics (apenas integração)

---

## 3) Convenções de Estado

| Estado | Símbolo | Descrição |
|--------|---------|-----------|
| loading | ⏳ | Requisição em andamento |
| error | 🔴 | Erro de API/contrato |
| empty | ⬜ | Sem dados |
| data | ✅ | Dados disponíveis |
| blocked | ❌ | Bloqueado por invariante/perm |

---

## 4) Telas

---

### SCREEN-TEAMS-001 — Dashboard de Equipes

**Rota**: `/teams`  
**Prioridade**: P0  
**Flows**: FLOW-TEAMS-001, FLOW-TEAMS-002, FLOW-TEAMS-006  
**Contratos**: CONTRACT-TEAMS-001, CONTRACT-TEAMS-002, CONTRACT-TEAMS-005

#### Estados mínimos

| Estado | Conteúdo mínimo | CTA |
|--------|-----------------|-----|
| ⏳ loading | Skeleton de cards | — |
| 🔴 error | Mensagem + retry | Retry |
| ⬜ empty | “Você ainda não participa...” | “Criar minha primeira equipe” |
| ✅ data | Grid/lista de equipes + paginação | “Criar equipe”, “Ver equipe”, “Arquivar” |

#### Evidência (EVIDENCIADO)

- `Hb Track - Frontend/src/components/teams-v2/DashboardV2.tsx`
  - Âncora: `if (isLoading) { ... }` / `if (isError) { ... }` / `if ... teams.length === 0`
  - Trecho:
    ```ts
    if (isLoading) { return (...) }
    if (isError) { return (...) }
    if (!isLoading && teams.length === 0) { return (...) }
    ```

---

### SCREEN-TEAMS-002 — Modal Criar Equipe

**Rota**: (modal) dentro de `/teams`  
**Prioridade**: P0  
**Flows**: FLOW-TEAMS-002  
**Contratos**: CONTRACT-TEAMS-002  
**Invariantes**: INV-TEAMS-001, INV-TEAMS-016

#### Campos obrigatórios (mínimo)
- `name` (min 3 chars no FE; min 1 no OpenAPI — GAP de paridade)
- `category_id`
- `gender`

#### Estados mínimos

| Estado | Comportamento |
|--------|---------------|
| ⏳ submitting | Botão desabilitado |
| 🔴 error 409/400 | Mensagem de “já existe” / validação |
| 🔴 error 422 | Campos inválidos destacados |
| ✅ success | Redireciona para Members |

#### Evidência (EVIDENCIADO)

- `Hb Track - Frontend/tests/e2e/teams/teams.crud.spec.ts`
  - Âncora: `CREATE TEAM`
  - Trecho:
    ```ts
    // Endpoint: POST /teams
    // Payload: { name (min 3 chars), category_id (1-7), gender, ... }
    ```

---

### SCREEN-TEAMS-003 — Detalhe da Equipe (Layout com Tabs)

**Rota**: `/teams/{teamId}/*`  
**Prioridade**: P0  
**Flows**: FLOW-TEAMS-003  
**Contratos**: CONTRACT-TEAMS-003

#### Tabs mínimas
- Overview (`/overview`)
- Members (`/members`)
- Settings (`/settings`) — se `canManageTeam`

#### Evidência (EVIDENCIADO)

- `Hb Track - Frontend/src/app/(admin)/teams/[teamId]/layout.tsx`
  - Âncora: `Tabs:`
  - Trecho:
    ```ts
    // - Configurações→ /teams/[teamId]/settings (se canManageTeam)
    ```

---

### SCREEN-TEAMS-004 — Members (Staff + Atletas)

**Rota**: `/teams/{teamId}/members`  
**Prioridade**: P0  
**Flows**: FLOW-TEAMS-003, FLOW-TEAMS-007, FLOW-TEAMS-008  
**Contratos**: CONTRACT-TEAMS-009, CONTRACT-TEAMS-013..016, CONTRACT-TEAMS-020..023 (GAP)

#### Estados mínimos (staff)

| Estado | Conteúdo mínimo |
|--------|-----------------|
| ⏳ loading | Skeleton tabela |
| 🔴 error | Toast + fallback vazio |
| ⬜ empty | “Nenhum membro na comissão” + CTA convidar (se perm) |
| ✅ data | Lista staff + pendentes + ações (editar/remover/reenviar) |

#### Evidência (EVIDENCIADO)

- `Hb Track - Frontend/src/components/teams-v2/MembersTab.tsx`
  - Âncora: `Promise.all([ teamsService.getStaff, teamsService.getPendingMembers ])`
  - Trecho:
    ```ts
    const [staffResponse, pendingResponse] = await Promise.all([
      teamsService.getStaff(teamId, true),
      teamsService.getPendingMembers(teamId),
    ]);
    ```

---

### SCREEN-TEAMS-005 — Settings (nome + alert threshold)

**Rota**: `/teams/{teamId}/settings`  
**Prioridade**: P0  
**Flows**: FLOW-TEAMS-004  
**Contratos**: CONTRACT-TEAMS-004, CONTRACT-TEAMS-006  
**Invariantes**: INV-TEAMS-004

#### Estados mínimos

| Estado | Conteúdo mínimo |
|--------|-----------------|
| ⏳ loading | Nome/descrição placeholders |
| 🔴 error | Toast de falha |
| ✅ data | Editar nome e threshold; salvar |

#### Evidência (EVIDENCIADO)

- `Hb Track - Frontend/src/components/teams-v2/SettingsTab.tsx`
  - Âncora: `handleThresholdSave`
  - Trecho:
    ```ts
    body: JSON.stringify({ alert_threshold_multiplier: value }),
    ```

---

### SCREEN-TEAMS-006 — Stats (Integração)

**Rota**: `/teams/{teamId}/stats`  
**Prioridade**: P1  
**Status**: EVIDENCIADO (UI) / INTEGRAÇÃO (dados)  

Nota: contratos e invariantes de analytics/training são tratados em `TEAMS_INTEGRATION.md`.

#### Evidência (EVIDENCIADO)

- `Hb Track - Frontend/src/app/(admin)/teams/[teamId]/stats/page.tsx`
  - Âncora: `Rota: /teams/[teamId]/stats`
  - Trecho:
    ```ts
    /**
     * Rota: /teams/[teamId]/stats
     */
    ```

---

### SCREEN-TEAMS-007 — Trainings (Integração)

**Rota**: `/teams/{teamId}/trainings`  
**Prioridade**: P1  
**Status**: EVIDENCIADO (UI) / INTEGRAÇÃO (dados)  

Nota: contratos e invariantes do módulo TRAINING são tratados no MCP de TRAINING.

#### Evidência (EVIDENCIADO)

- `Hb Track - Frontend/src/app/(admin)/teams/[teamId]/trainings/page.tsx`
  - Âncora: `Rota: /teams/[teamId]/trainings`
  - Trecho:
    ```ts
    /**
     * Rota: /teams/[teamId]/trainings
     */
    ```
