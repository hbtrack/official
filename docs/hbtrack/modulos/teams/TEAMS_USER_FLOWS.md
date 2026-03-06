# TEAMS_USER_FLOWS.md

Status: DRAFT  
Versão: v0.1.0  
Tipo de Documento: User Flows (Normativo Operacional / SSOT)  
Módulo: TEAMS  
Fase: FASE_0  
Autoridade: NORMATIVO_OPERACIONAL  
Owners:
- Arquitetura (Arquiteto): Codex (Arquiteto v2.2.0)
- Produto/UX: (a definir)
- Auditoria: (a definir)

Última revisão: 2026-03-03  
Próxima revisão recomendada: 2026-03-17  

Dependências:
- INVARIANTS_TEAMS.md
- TEAMS_SCREENS_SPEC.md
- TEAMS_FRONT_BACK_CONTRACT.md
- AR_BACKLOG_TEAMS.md
- TEST_MATRIX_TEAMS.md

---

## REGRA SSOT (obrigatória)

**DB/schema.sql > services/domain rules > OpenAPI > frontend > PRD.**

---

## 1) Objetivo (Normativo)

Definir os fluxos mínimos do módulo TEAMS, ancorando cada passo em telas (SCREEN-TEAMS-*) e contratos (CONTRACT-TEAMS-*), com rastreabilidade para invariantes (INV-TEAMS-*).

---

## 2) Escopo (ETAPA 0)

### 2.1 Dentro do escopo
- Criar/listar/editar/arquivar equipes
- Configurações de equipe (Step 15)
- Gestão de staff (coach + comissão) e convites (onde aplicável)
- Gestão de elenco via `team_registrations` (listagem/encerramento)

### 2.2 Fora do escopo
- CRUD de treinos e presença (TRAINING)
- CRUD de jogos/partidas (MATCHES/SCOUT)
- Implementação de Auth/RBAC (apenas pré-condição)

---

## 3) Convenções

- Ator principal: Dirigente / Coordenador / Treinador autenticado.
- Pré-condição global: usuário autenticado com organização selecionada.
- Estados: `EVIDENCIADO` exige evidência `path+anchor+excerpt`; senão `GAP`/`HIPOTESE`.

---

## 4) Fluxos

---

### FLOW-TEAMS-001 — Acessar Dashboard de Equipes

**Prioridade**: P0  
**Status**: EVIDENCIADO  
**Telas**: SCREEN-TEAMS-001  
**Contratos**: CONTRACT-TEAMS-001  
**Invariantes-chave**: INV-TEAMS-017

#### Passos

| # | Ator | Ação | Sistema | Tela/Contrato |
|---|------|------|---------|---------------|
| 1 | Usuário | Acessa `/teams` | Carrega lista paginada | SCREEN-TEAMS-001 / CONTRACT-TEAMS-001 |
| 2 | Usuário | Usa filtros/busca | Filtra client-side | SCREEN-TEAMS-001 |
| 3 | Usuário | Seleciona uma equipe | Redireciona para `/teams/{id}/overview` | SCREEN-TEAMS-003 |

#### Evidência (EVIDENCIADO)

- `Hb Track - Frontend/src/components/teams-v2/DashboardV2.tsx`
  - Âncora: `teamsService.list({ page, limit })`
  - Trecho:
    ```ts
    const response = await teamsService.list({ page: currentPage, limit: itemsPerPage });
    const mappedTeams = mapApiTeamsToV2(response.items);
    ```

---

### FLOW-TEAMS-002 — Criar Equipe

**Prioridade**: P0  
**Status**: EVIDENCIADO  
**Telas**: SCREEN-TEAMS-001, SCREEN-TEAMS-002  
**Contratos**: CONTRACT-TEAMS-002  
**Invariantes-chave**: INV-TEAMS-001, INV-TEAMS-016

#### Passos

| # | Ator | Ação | Sistema | Tela/Contrato |
|---|------|------|---------|---------------|
| 1 | Usuário | Clica “Criar equipe” | Abre modal | SCREEN-TEAMS-002 |
| 2 | Usuário | Informa `name`, `category_id`, `gender` | Valida campos | SCREEN-TEAMS-002 |
| 3 | Usuário | Submete | Cria equipe | CONTRACT-TEAMS-002 |
| 4 | Sistema | Retorna equipe criada | Redireciona para members (opcional) | SCREEN-TEAMS-004 |

#### Evidência (EVIDENCIADO)

- `docs/ssot/openapi.json`
  - Âncora: `operationId: create_team_api_v1_teams_post`
  - Trecho:
    ```json
    "operationId": "create_team_api_v1_teams_post"
    ```

---

### FLOW-TEAMS-003 — Acessar Detalhe da Equipe e Navegar por Tabs

**Prioridade**: P0  
**Status**: EVIDENCIADO  
**Telas**: SCREEN-TEAMS-003..007  
**Contratos**: CONTRACT-TEAMS-003, CONTRACT-TEAMS-009  
**Invariantes-chave**: INV-TEAMS-018

#### Passos

| # | Ator | Ação | Sistema | Tela/Contrato |
|---|------|------|---------|---------------|
| 1 | Usuário | Acessa `/teams/{teamId}` | Redireciona para overview | SCREEN-TEAMS-003 |
| 2 | Usuário | Alterna tabs (members/settings/...) | Mantém navegação | SCREEN-TEAMS-003..007 |
| 3 | Sistema | Carrega dados mínimos da equipe | GET `/teams/{teamId}` | CONTRACT-TEAMS-003 |
| 4 | Sistema | Carrega staff | GET `/teams/{teamId}/staff` | CONTRACT-TEAMS-009 |

#### Evidência (EVIDENCIADO)

- `Hb Track - Frontend/src/app/(admin)/teams/[teamId]/layout.tsx`
  - Âncora: `Tabs:`
  - Trecho:
    ```ts
    // Tabs:
    // - Visão Geral  → /teams/[teamId]/overview
    // - Membros      → /teams/[teamId]/members
    ```

---

### FLOW-TEAMS-004 — Atualizar Configurações de Alertas (Step 15)

**Prioridade**: P0  
**Status**: EVIDENCIADO  
**Telas**: SCREEN-TEAMS-005  
**Contratos**: CONTRACT-TEAMS-006  
**Invariantes-chave**: INV-TEAMS-004

#### Passos

| # | Ator | Ação | Sistema | Tela/Contrato |
|---|------|------|---------|---------------|
| 1 | Usuário | Acessa Settings | Exibe valor atual | SCREEN-TEAMS-005 |
| 2 | Usuário | Ajusta threshold | Valida faixa 1.0..3.0 | INV-TEAMS-004 |
| 3 | Usuário | Salva | PATCH `/teams/{id}/settings` | CONTRACT-TEAMS-006 |

#### Evidência (EVIDENCIADO)

- `docs/ssot/openapi.json`
  - Âncora: `operationId: update_team_settings_api_v1_teams__team_id__settings_patch`
  - Trecho:
    ```json
    "operationId": "update_team_settings_api_v1_teams__team_id__settings_patch"
    ```

---

### FLOW-TEAMS-005 — Reatribuir Treinador (Coach) e Consultar Histórico

**Prioridade**: P0  
**Status**: EVIDENCIADO  
**Telas**: SCREEN-TEAMS-004, SCREEN-TEAMS-005  
**Contratos**: CONTRACT-TEAMS-007, CONTRACT-TEAMS-008  
**Invariantes-chave**: INV-TEAMS-012

#### Passos

| # | Ator | Ação | Sistema | Tela/Contrato |
|---|------|------|---------|---------------|
| 1 | Usuário | Abre gestão de staff | Lista staff | CONTRACT-TEAMS-009 |
| 2 | Usuário | Seleciona novo coach | PATCH coach | CONTRACT-TEAMS-007 |
| 3 | Sistema | Atualiza vínculos e notifica | Ordem garantida | INV-TEAMS-012 |
| 4 | Usuário | Consulta histórico | GET coaches/history | CONTRACT-TEAMS-008 |

#### Evidência (EVIDENCIADO)

- `docs/ssot/openapi.json`
  - Âncora: `operationId: reassign_team_coach_api_v1_teams__team_id__coach_patch`
  - Trecho:
    ```json
    "operationId": "reassign_team_coach_api_v1_teams__team_id__coach_patch"
    ```

---

### FLOW-TEAMS-006 — Arquivar (Soft delete) uma Equipe

**Prioridade**: P1  
**Status**: EVIDENCIADO  
**Telas**: SCREEN-TEAMS-001  
**Contratos**: CONTRACT-TEAMS-005  
**Invariantes-chave**: INV-TEAMS-003, INV-TEAMS-019

#### Passos

| # | Ator | Ação | Sistema | Tela/Contrato |
|---|------|------|---------|---------------|
| 1 | Usuário | No card/menu da equipe, escolhe “Arquivar” | Confirma motivo | SCREEN-TEAMS-001 |
| 2 | Usuário | Confirma | DELETE soft delete | CONTRACT-TEAMS-005 |
| 3 | Sistema | Marca deleted_at+reason | DB bloqueia ausência de reason | INV-TEAMS-019 |

#### Evidência (EVIDENCIADO)

- `Hb Track - Backend/app/api/v1/routers/teams.py`
  - Âncora: `delete_team`
  - Trecho:
    ```py
    reason: str = Query("Exclusão manual", description="Motivo da exclusão")
    ```

---

### FLOW-TEAMS-007 — Convites RESTful `/invites` (criar/listar/reenviar/cancelar)

**Prioridade**: P0  
**Status**: GAP  
**decision_required**: true  
**Telas**: SCREEN-TEAMS-004  
**Contratos**: CONTRACT-TEAMS-020..023  
**Invariantes-chave**: INV-TEAMS-006, INV-TEAMS-007, INV-TEAMS-013..014

#### Contexto do GAP

- Frontend usa `/teams/{teamId}/invites` como contrato canônico.
- OpenAPI SSOT não contém `invites` (feature não exposta no agregador v1 atual).

#### Evidência (GAP)

- `Hb Track - Frontend/src/lib/api/teams.ts`
  - Âncora: `createTeamInvite`
  - Trecho:
    ```ts
    return apiClient.post(`/teams/${teamId}/invites`, { email, role });
    ```

---

### FLOW-TEAMS-008 — Gestão de Elenco via `team_registrations`

**Prioridade**: P0  
**Status**: EVIDENCIADO (parcial)  
**Telas**: SCREEN-TEAMS-004  
**Contratos**: CONTRACT-TEAMS-013..016  
**Invariantes-chave**: INV-TEAMS-008..011, INV-TEAMS-020 (GAP)

#### Passos (mínimo)

| # | Ator | Ação | Sistema | Tela/Contrato |
|---|------|------|---------|---------------|
| 1 | Usuário | Abre tab Members | Lista atletas vinculados | CONTRACT-TEAMS-013 |
| 2 | Usuário | Encerra vínculo (remove atleta) | PATCH registration end_at | CONTRACT-TEAMS-015 |

#### Evidência (EVIDENCIADO)

- `Hb Track - Backend/app/api/v1/routers/team_registrations.py`
  - Âncora: `@router.get("/teams/{team_id}/registrations")`
  - Trecho:
    ```py
    @router.get("/teams/{team_id}/registrations", ... response_model=TeamRegistrationPaginatedResponse)
    ```

