# TEAMS_INTEGRATION.md

Status: DRAFT  
Versão: v0.1.0  
Tipo de Documento: Integrações do Módulo (Normativo Operacional / SSOT)  
Módulo: TEAMS  
Fase: FASE_0  
Autoridade: NORMATIVO_OPERACIONAL  

Última revisão: 2026-03-03  
Próxima revisão recomendada: 2026-03-17  

Dependências:
- INVARIANTS_TEAMS.md
- TEAMS_FRONT_BACK_CONTRACT.md
- AR_BACKLOG_TEAMS.md

---

## REGRA SSOT (obrigatória)

**DB/schema.sql > services/domain rules > OpenAPI > frontend > PRD.**

---

## 1) Objetivo

Catalogar integrações EVIDENCIADAS do módulo TEAMS com outros domínios, e declarar o que é núcleo vs integração.

---

## 2) Integrações EVIDENCIADAS

### INT-TEAMS-001 — Auth/RBAC (ExecutionContext + permission_dep)

- **Uso:** enforcement de papéis e escopo (org/team) nas rotas TEAMS.
- **Risco:** sem RBAC correto, exfiltração entre equipes.

**Evidência:**
- `Hb Track - Backend/app/api/v1/routers/teams.py`
  - Âncora: `permission_dep(... require_org/require_team ...)`
  - Trecho:
    ```py
    ctx: ExecutionContext = Depends(permission_dep(roles=[...], require_team=True))
    ```

---

### INT-TEAMS-002 — Organizations/OrgMemberships/Roles

- **Uso:** coach é `OrgMembership` com `role_id=3`; staff lista por joins com Role.

**Evidência:**
- `docs/ssot/openapi.json`
  - Âncora: `operationId: reassign_team_coach_api_v1_teams__team_id__coach_patch`
  - Trecho:
    ```json
    "description": "4. Valida novo coach (role_id=3, ativo, mesma org)"
    ```

---

### INT-TEAMS-003 — PasswordReset (welcome token) + EmailService

- **Uso:** convite/reenvio/cancelamento interage com token `welcome` e envio de email.

**Evidência:**
- `Hb Track - Backend/app/api/v1/routers/teams.py`
  - Âncora: `resend_team_member_invite`
  - Trecho:
    ```py
    PasswordReset.token_type == "welcome"
    ```

---

### INT-TEAMS-004 — Notifications (WebSocket) em mudanças de coach

- **Uso:** reassign/remove coach dispara notification + broadcast.

**Evidência:**
- `Hb Track - Backend/app/api/v1/routers/teams.py`
  - Âncora: `remove_staff_member`
  - Trecho:
    ```py
    await notification_service.broadcast_to_user(user.id, notification)
    ```

---

### INT-TEAMS-005 — Athletes/Persons (team_registrations + staff person_id)

- **Uso:** `team_registrations` referencia `athletes` e `teams`; `team_memberships` referencia `persons`.

**Evidência:**
- `docs/ssot/schema.sql`
  - Âncora: `CREATE TABLE public.team_registrations`
  - Trecho:
    ```sql
    athlete_id uuid NOT NULL,
    team_id uuid NOT NULL,
    ```

---

### INT-TEAMS-006 — TRAINING/Analytics (integração via team_id e settings)

- **Uso:** `teams.alert_threshold_multiplier` é descrito como “Step 3” (alertas wellness).

**Evidência:**
- `docs/ssot/schema.sql`
  - Âncora: `COMMENT ON COLUMN public.teams.alert_threshold_multiplier`
  - Trecho:
    ```sql
    COMMENT ON COLUMN public.teams.alert_threshold_multiplier IS 'Step 3: Multiplicador ...'
    ```

---

## 3) GAPS de integração (impactam TEAMS)

### GAP-INT-TEAMS-001 — Convites RESTful `/invites` não aparecem no OpenAPI SSOT atual

**Impacto:** flows P0 de membros pendentes/reenviar/cancelar no FE ficam bloqueados.  
**Roteiro:** AR-TEAMS-002 (wiring + OpenAPI sync + testes).

**Evidência:**
- `Hb Track - Backend/app/api/v1/api.py`
  - Âncora: `LOOKUP include_router(lookup.router, ...)`
  - Trecho:
    ```py
    api_router.include_router(lookup.router, tags=["lookup"])
    ```

> Nota: ausência de `team_invites.router` no agregador v1 é o núcleo do GAP (ver AR_BACKLOG_TEAMS.md).
