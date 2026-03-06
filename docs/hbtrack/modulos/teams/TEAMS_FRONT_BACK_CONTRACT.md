# TEAMS_FRONT_BACK_CONTRACT.md

Status: DRAFT  
Versão: v0.1.0  
Tipo de Documento: Front-Back Contract (Normativo Operacional / SSOT)  
Módulo: TEAMS  
Fase: FASE_0  
Autoridade: NORMATIVO_OPERACIONAL  
Owners:
- Arquitetura (Arquiteto): Codex (Arquiteto v2.2.0)
- Backend: (a definir)
- Frontend: (a definir)
- Auditoria: (a definir)

Última revisão: 2026-03-03  
Próxima revisão recomendada: 2026-03-17  

Dependências:
- INVARIANTS_TEAMS.md
- TEAMS_USER_FLOWS.md
- TEAMS_SCREENS_SPEC.md
- AR_BACKLOG_TEAMS.md
- TEST_MATRIX_TEAMS.md

---

## REGRA SSOT (obrigatória)

**DB/schema.sql > services/domain rules > OpenAPI > frontend > PRD.**

---

## 1) Objetivo (Normativo)

Formalizar os contratos mínimos FE↔BE do módulo TEAMS, com:
- request/response mínimos
- erros funcionais mínimos
- rastreabilidade (INV/FLOW/SCREEN/TEST/AR)

---

## 2) Escopo (ETAPA 0)

### 2.1 Dentro do escopo
- `/teams` e subrotas do domínio de equipes
- staff (`team_memberships`) e coach (Step 18/19/35)
- configurações (Step 15)
- `team_registrations` (listagem e update de vínculo)

### 2.2 Fora do escopo
- contratos de treinos/jogos/analytics (apenas integração)

---

## 3) Convenções

- Base path (FastAPI v1): `/api/v1`
- `BLOQUEANTE_VALIDACAO`: violação deve resultar em 4xx (422/409/400).
- `EVIDENCIADO`: exige evidência `path+anchor+excerpt`.

---

## 4) Contratos (TEAMS)

### CONTRACT-TEAMS-001 — Listar equipes (paginado)

**Endpoint**: `GET /api/v1/teams?page=&limit=&season_id=`  
**Prioridade**: P0  
**Flows/Telas**: FLOW-TEAMS-001 / SCREEN-TEAMS-001  
**Invariantes**: INV-TEAMS-017

#### Response 200 (mínimo)

```json
{
  "items": [{ "id": "uuid", "name": "string" }],
  "page": 1,
  "limit": 50,
  "total": 0
}
```

#### GAPS conhecidos

- OpenAPI SSOT para `GET /api/v1/teams` atualmente descreve response como `array[TeamResponse]` (não paginado).

**Evidência (GAP de paridade OpenAPI↔FE/Service)**:
- `docs/ssot/openapi.json`
  - Âncora: `"/api/v1/teams": { "get": ... "items": { "$ref": "#/components/schemas/TeamResponse" } }`
  - Trecho:
    ```json
    "schema": { "type": "array", "items": { "$ref": "#/components/schemas/TeamResponse" } }
    ```
- `Hb Track - Frontend/src/lib/api/teams.ts`
  - Âncora: `teamsService.list`
  - Trecho:
    ```ts
    const response = await apiClient.get<PaginatedResponse<Team>>("/teams", { params });
    ```

---

### CONTRACT-TEAMS-002 — Criar equipe

**operationId**: `create_team_api_v1_teams_post`  
**Endpoint**: `POST /api/v1/teams`  
**Prioridade**: P0  
**Flows/Telas**: FLOW-TEAMS-002 / SCREEN-TEAMS-002  
**Invariantes**: INV-TEAMS-001, INV-TEAMS-016

#### Request body (mínimo)

```json
{
  "name": "string",
  "category_id": 1,
  "gender": "masculino|feminino",
  "is_our_team": true
}
```

#### Response 201 (mínimo)

```json
{ "id": "uuid", "organization_id": "uuid", "name": "string" }
```

#### Evidência (EVIDENCIADO)

- `docs/ssot/openapi.json`
  - Âncora: `operationId: create_team_api_v1_teams_post`
  - Trecho:
    ```json
    "operationId": "create_team_api_v1_teams_post"
    ```

---

### CONTRACT-TEAMS-003 — Obter equipe por ID

**operationId**: `get_team_api_v1_teams__team_id__get`  
**Endpoint**: `GET /api/v1/teams/{team_id}`  
**Prioridade**: P0  
**Flows/Telas**: FLOW-TEAMS-003 / SCREEN-TEAMS-003

#### Evidência (EVIDENCIADO)

- `docs/ssot/openapi.json`
  - Âncora: `operationId: get_team_api_v1_teams__team_id__get`
  - Trecho:
    ```json
    "operationId": "get_team_api_v1_teams__team_id__get"
    ```

---

### CONTRACT-TEAMS-004 — Atualizar equipe

**operationId**: `update_team_api_v1_teams__team_id__patch`  
**Endpoint**: `PATCH /api/v1/teams/{team_id}`  
**Prioridade**: P0  
**Flows/Telas**: (Settings) / SCREEN-TEAMS-005

#### Nota de paridade (GAP)

Frontend tenta atualizar `description`, mas DB/schema não contém `teams.description` (inexistente em `docs/ssot/schema.sql`).

**Evidência (GAP)**:
- `docs/ssot/schema.sql`
  - Âncora: `CREATE TABLE public.teams`
  - Trecho:
    ```sql
    CREATE TABLE public.teams (
        ... name character varying(120) NOT NULL,
        ... deleted_reason text,
        season_id uuid,
    ```

---

### CONTRACT-TEAMS-005 — Arquivar equipe (soft delete)

**Endpoint**: `DELETE /api/v1/teams/{team_id}?reason=`  
**Prioridade**: P1  
**Flows/Telas**: FLOW-TEAMS-006 / SCREEN-TEAMS-001  
**Invariantes**: INV-TEAMS-003, INV-TEAMS-019

#### Response
- `204 No Content`

#### GAP de contrato FE↔BE

FE envia `reason` no body; BE lê `reason` por query param.

**Evidência (GAP)**:
- `Hb Track - Frontend/src/lib/api/teams.ts`
  - Âncora: `teamsService.delete`
  - Trecho:
    ```ts
    await apiClient.delete(`/teams/${id}`, { data: reason ? { reason } : undefined });
    ```
- `Hb Track - Backend/app/api/v1/routers/teams.py`
  - Âncora: `delete_team`
  - Trecho:
    ```py
    reason: str = Query("Exclusão manual", description="Motivo da exclusão")
    ```

---

### CONTRACT-TEAMS-006 — Atualizar settings (Step 15)

**operationId**: `update_team_settings_api_v1_teams__team_id__settings_patch`  
**Endpoint**: `PATCH /api/v1/teams/{team_id}/settings`  
**Prioridade**: P0  
**Flows/Telas**: FLOW-TEAMS-004 / SCREEN-TEAMS-005  
**Invariantes**: INV-TEAMS-004

---

### CONTRACT-TEAMS-007 — Reatribuir coach (Step 18/21)

**operationId**: `reassign_team_coach_api_v1_teams__team_id__coach_patch`  
**Endpoint**: `PATCH /api/v1/teams/{team_id}/coach`  
**Prioridade**: P0  
**Invariantes**: INV-TEAMS-012

---

### CONTRACT-TEAMS-008 — Histórico de coaches (Step 19)

**operationId**: `get_team_coaches_history_api_v1_teams__team_id__coaches_history_get`  
**Endpoint**: `GET /api/v1/teams/{team_id}/coaches/history`  
**Prioridade**: P1

---

### CONTRACT-TEAMS-009 — Listar staff

**operationId**: `get_team_staff_api_v1_teams__team_id__staff_get`  
**Endpoint**: `GET /api/v1/teams/{team_id}/staff?active_only=true`  
**Prioridade**: P0  
**Invariantes**: INV-TEAMS-018

#### GAP de shape no FE

FE filtra por `role_id`, mas response atual (`TeamStaffMember`) expõe `role` string.

**Evidência (GAP)**:
- `Hb Track - Frontend/src/components/teams-v2/MembersTab.tsx`
  - Âncora: `staffRoleIds.includes(member.role_id)`
  - Trecho:
    ```ts
    .filter((member: any) => staffRoleIds.includes(member.role_id))
    ```

---

### CONTRACT-TEAMS-010 — Remover staff (Step 35)

**operationId**: `remove_staff_member_api_v1_teams__team_id__staff__membership_id__delete`  
**Endpoint**: `DELETE /api/v1/teams/{team_id}/staff/{membership_id}`  
**Prioridade**: P1  
**Invariantes**: INV-TEAMS-015

---

### CONTRACT-TEAMS-011 — Reenviar convite (rota `/members/*`)

**operationId**: `resend_team_member_invite_api_v1_teams__team_id__members__membership_id__resend_invite_post`  
**Endpoint**: `POST /api/v1/teams/{team_id}/members/{membership_id}/resend-invite`  
**Prioridade**: P1  
**Invariantes**: INV-TEAMS-013

---

### CONTRACT-TEAMS-012 — Cancelar convite (rota `/members/*`)

**operationId**: `cancel_team_member_invite_api_v1_teams__team_id__members__membership_id__cancel_invite_delete`  
**Endpoint**: `DELETE /api/v1/teams/{team_id}/members/{membership_id}/cancel-invite`  
**Prioridade**: P1  
**Invariantes**: INV-TEAMS-014

---

## 5) Contratos (Team Registrations)

### CONTRACT-TEAMS-013 — Listar inscrições da equipe

**Endpoint**: `GET /api/v1/teams/{team_id}/registrations?active_only=&page=&limit=`  
**Prioridade**: P0  
**Status**: EVIDENCIADO  

**Evidência**:
- `Hb Track - Backend/app/api/v1/routers/team_registrations.py`
  - Âncora: `list_team_registrations`
  - Trecho:
    ```py
    @router.get("/teams/{team_id}/registrations", ... response_model=TeamRegistrationPaginatedResponse)
    ```

---

### CONTRACT-TEAMS-014 — Criar inscrição atleta–equipe

**Endpoint**: `POST /api/v1/teams/{team_id}/registrations/{athlete_id}`  
**Prioridade**: P1  
**Status**: EVIDENCIADO

---

### CONTRACT-TEAMS-015 — Atualizar inscrição (encerrar vínculo)

**Endpoint**: `PATCH /api/v1/teams/{team_id}/registrations/{registration_id}`  
**Prioridade**: P0  
**Status**: EVIDENCIADO

---

### CONTRACT-TEAMS-016 — Obter inscrição por ID

**Endpoint**: `GET /api/v1/teams/{team_id}/registrations/{registration_id}`  
**Prioridade**: P1  
**Status**: EVIDENCIADO

---

## 6) Proposta fora do PRD — não normativa

Nenhuma nesta versão (todas as lacunas aqui são derivadas de drift interno repo: BE/FE/OpenAPI/DB).

---

## 7) Contratos RESTful de convites `/invites` (GAP)

> Frontend e testes E2E assumem `/teams/{teamId}/invites`, mas o OpenAPI SSOT atual não contém esses endpoints.

### CONTRACT-TEAMS-020 — Listar convites pendentes (GAP)

**Endpoint**: `GET /api/v1/teams/{team_id}/invites`  
**Status**: GAP  
**decision_required**: true  

**Evidência (GAP)**:
- `Hb Track - Frontend/tests/e2e/teams/teams.invites.spec.ts`
  - Âncora: `CONTRATO`
  - Trecho:
    ```ts
    // GET  /teams/{teamId}/invites → Listar pendentes
    ```

---

### CONTRACT-TEAMS-021 — Criar convite (GAP)

**Endpoint**: `POST /api/v1/teams/{team_id}/invites`  
**Status**: GAP  
**decision_required**: true  

**Evidência (GAP)**:
- `Hb Track - Frontend/src/lib/api/teams.ts`
  - Âncora: `createTeamInvite`
  - Trecho:
    ```ts
    return apiClient.post<TeamInviteActionResponse>(`/teams/${teamId}/invites`, { ... });
    ```

---

### CONTRACT-TEAMS-022 — Reenviar convite (GAP)

**Endpoint**: `POST /api/v1/teams/{team_id}/invites/{invite_id}/resend`  
**Status**: GAP  
**decision_required**: true  

**Evidência (GAP)**:
- `Hb Track - Frontend/src/lib/api/teams.ts`
  - Âncora: `resendInvite`
  - Trecho:
    ```ts
    return apiClient.post<TeamInviteActionResponse>(`/teams/${teamId}/invites/${inviteId}/resend`);
    ```

---

### CONTRACT-TEAMS-023 — Cancelar convite (GAP)

**Endpoint**: `DELETE /api/v1/teams/{team_id}/invites/{invite_id}`  
**Status**: GAP  
**decision_required**: true  

**Evidência (GAP)**:
- `Hb Track - Frontend/src/lib/api/teams.ts`
  - Âncora: `cancelInvite`
  - Trecho:
    ```ts
    return apiClient.delete<TeamInviteActionResponse>(`/teams/${teamId}/invites/${inviteId}`);
    ```
