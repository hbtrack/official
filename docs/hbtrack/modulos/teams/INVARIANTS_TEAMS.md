# INVARIANTS_TEAMS.md — Invariantes do Módulo TEAMS

Status: DRAFT  
Versão: v0.1.0  
Tipo de Documento: Invariants (Normativo Operacional / SSOT)  
Módulo: TEAMS  
Fase: FASE_0  
Autoridade: NORMATIVO_OPERACIONAL  
Owners:
- Arquitetura (Arquiteto): Codex (Arquiteto v2.2.0)
- Backend/Frontend: (a definir)
- Auditoria/Testes: (a definir)

Última revisão: 2026-03-03  
Próxima revisão recomendada: 2026-03-17  

---

## REGRA SSOT (obrigatória)

**DB/schema.sql > services/domain rules > OpenAPI > frontend > PRD.**

---

## REGRA DE EVIDÊNCIA (anti-alucinação)

- Qualquer item com `status: EVIDENCIADO` DEVE conter **1 evidência verificável**: `path` + `anchor` + `excerpt`.
- Sem evidência ⇒ `status: HIPOTESE` ou `status: GAP`.

---

## 0) Escopo do módulo (ETAPA 0)

### 0.1 Dentro do escopo (TEAMS)
- Entidade `teams` (CRUD + soft delete).
- `team_memberships` (staff por equipe) incluindo coach, histórico, e remoção de staff.
- `team_registrations` (vínculo atleta↔equipe) — listagem e gestão do vínculo (fim do vínculo).
- Configuração da equipe: `alert_threshold_multiplier` (Step 15).

### 0.2 Fora do escopo (TEAMS)
- Treinos em si (`/teams/{team_id}/trainings`) — módulo TRAINING (apenas integração).
- Jogos/partidas (`/teams/{team_id}/matches/*`) — módulo MATCHES/SCOUT (apenas integração).
- Auth/JWT/RBAC como implementação detalhada (apenas integração).

---

## Âncoras de evidência (SSOT)

- DB: `docs/ssot/schema.sql`
- OpenAPI SSOT: `docs/ssot/openapi.json`
- Services/Routers (BE):
  - `Hb Track - Backend/app/services/team_service.py`
  - `Hb Track - Backend/app/services/team_registration_service.py`
  - `Hb Track - Backend/app/api/v1/routers/teams.py`
  - `Hb Track - Backend/app/api/v1/routers/team_registrations.py`
- Frontend (consumo/UX):
  - `Hb Track - Frontend/src/lib/api/teams.ts`
  - `Hb Track - Frontend/src/app/(admin)/teams/[teamId]/layout.tsx`

---

## Sumário (IDs estáveis)

| ID | Severidade | Camada | Status |
|---|---|---|---|
| INV-TEAMS-001 | BLOQUEANTE_VALIDACAO | db | EVIDENCIADO |
| INV-TEAMS-002 | BLOQUEANTE_VALIDACAO | db | EVIDENCIADO |
| INV-TEAMS-003 | BLOQUEANTE_VALIDACAO | db | EVIDENCIADO |
| INV-TEAMS-004 | BLOQUEANTE_VALIDACAO | db+api | EVIDENCIADO |
| INV-TEAMS-005 | BLOQUEANTE_VALIDACAO | db | EVIDENCIADO |
| INV-TEAMS-006 | BLOQUEANTE_VALIDACAO | db | EVIDENCIADO |
| INV-TEAMS-007 | BLOQUEANTE_VALIDACAO | db | EVIDENCIADO |
| INV-TEAMS-008 | BLOQUEANTE_VALIDACAO | db | EVIDENCIADO |
| INV-TEAMS-009 | BLOQUEANTE_VALIDACAO | db | EVIDENCIADO |
| INV-TEAMS-010 | BLOQUEANTE_VALIDACAO | db | EVIDENCIADO |
| INV-TEAMS-011 | NÃO_BLOQUEANTE | db | EVIDENCIADO |
| INV-TEAMS-012 | BLOQUEANTE_VALIDACAO | service+api | EVIDENCIADO |
| INV-TEAMS-013 | BLOQUEANTE_VALIDACAO | service+api | EVIDENCIADO |
| INV-TEAMS-014 | BLOQUEANTE_VALIDACAO | service+api | EVIDENCIADO |
| INV-TEAMS-015 | BLOQUEANTE_VALIDACAO | service+api | EVIDENCIADO |
| INV-TEAMS-016 | BLOQUEANTE_VALIDACAO | service | EVIDENCIADO |
| INV-TEAMS-017 | BLOQUEANTE_VALIDACAO | service | EVIDENCIADO |
| INV-TEAMS-018 | BLOQUEANTE_VALIDACAO | api | EVIDENCIADO |
| INV-TEAMS-019 | BLOQUEANTE_VALIDACAO | service+db | EVIDENCIADO |
| INV-TEAMS-020 | BLOQUEANTE_VALIDACAO | db+service | GAP |
| INV-TEAMS-021 | BLOQUEANTE_VALIDACAO | db+fe | GAP |

---

## INV-TEAMS-001 — Domínio de `teams.gender`

```yaml
id: INV-TEAMS-001
class: A
severity: BLOQUEANTE_VALIDACAO
layer: db
name: ck_teams_gender
rule: "teams.gender ∈ {'masculino','feminino'}"
status: EVIDENCIADO
evidence:
  - path: docs/ssot/schema.sql
    anchor: "CONSTRAINT ck_teams_gender"
    excerpt: "CONSTRAINT ck_teams_gender CHECK (((gender)::text = ANY ((ARRAY['masculino', 'feminino'])::text[])))"
rationale: "Bloqueia valores inválidos no dado-base que direciona elegibilidade e filtros em staff/atletas."
```

---

## INV-TEAMS-002 — Datas ativas coerentes (`active_from` ≤ `active_until`)

```yaml
id: INV-TEAMS-002
class: A
severity: BLOQUEANTE_VALIDACAO
layer: db
name: ck_teams_active_dates
rule: "(active_from IS NULL) OR (active_until IS NULL) OR (active_from <= active_until)"
status: EVIDENCIADO
evidence:
  - path: docs/ssot/schema.sql
    anchor: "CONSTRAINT ck_teams_active_dates"
    excerpt: "CONSTRAINT ck_teams_active_dates CHECK (((active_from IS NULL) OR (active_until IS NULL) OR (active_from <= active_until)))"
rationale: "Evita janela ativa invertida, reduzindo bugs de listagem/visibilidade."
```

---

## INV-TEAMS-003 — Soft delete atômico (pares `deleted_at`/`deleted_reason`)

```yaml
id: INV-TEAMS-003
class: A
severity: BLOQUEANTE_VALIDACAO
layer: db
name: ck_teams_deleted_reason
rule: "(deleted_at IS NULL AND deleted_reason IS NULL) OR (deleted_at IS NOT NULL AND deleted_reason IS NOT NULL)"
status: EVIDENCIADO
evidence:
  - path: docs/ssot/schema.sql
    anchor: "CONSTRAINT ck_teams_deleted_reason"
    excerpt: "CONSTRAINT ck_teams_deleted_reason CHECK ((((deleted_at IS NULL) AND (deleted_reason IS NULL)) OR ((deleted_at IS NOT NULL) AND (deleted_reason IS NOT NULL))))"
rationale: "Garante auditabilidade mínima em arquivamento/exclusão lógica."
```

---

## INV-TEAMS-004 — Faixa do `alert_threshold_multiplier` (Step 15)

```yaml
id: INV-TEAMS-004
class: A+B
severity: BLOQUEANTE_VALIDACAO
layer: db+api
name: teams_alert_threshold_multiplier_check
rule: "1.0 <= teams.alert_threshold_multiplier <= 3.0"
status: EVIDENCIADO
evidence:
  - path: docs/ssot/schema.sql
    anchor: "CONSTRAINT teams_alert_threshold_multiplier_check"
    excerpt: "CONSTRAINT teams_alert_threshold_multiplier_check CHECK (((alert_threshold_multiplier >= 1.0) AND (alert_threshold_multiplier <= 3.0)))"
rationale: "Configuração de sensibilidade de alertas deve permanecer em domínio controlado."
```

---

## INV-TEAMS-005 — Delete físico bloqueado em `teams`

```yaml
id: INV-TEAMS-005
class: A
severity: BLOQUEANTE_VALIDACAO
layer: db
name: trg_teams_block_delete
rule: "DELETE físico em teams é proibido; usar soft delete"
status: EVIDENCIADO
evidence:
  - path: docs/ssot/schema.sql
    anchor: "CREATE TRIGGER trg_teams_block_delete"
    excerpt: "CREATE TRIGGER trg_teams_block_delete BEFORE DELETE ON public.teams ... trg_block_physical_delete()"
rationale: "Evita perda irrecuperável de dados e preserva histórico."
```

---

## INV-TEAMS-006 — Domínio de `team_memberships.status`

```yaml
id: INV-TEAMS-006
class: A
severity: BLOQUEANTE_VALIDACAO
layer: db
name: check_team_memberships_status
rule: "team_memberships.status ∈ {'pendente','ativo','inativo'}"
status: EVIDENCIADO
evidence:
  - path: docs/ssot/schema.sql
    anchor: "CONSTRAINT check_team_memberships_status"
    excerpt: "CONSTRAINT check_team_memberships_status CHECK ((status = ANY (ARRAY['pendente','ativo','inativo'])))"
rationale: "Estado finito do vínculo de staff; necessário para convites e histórico."
```

---

## INV-TEAMS-007 — Unicidade de vínculo ativo/pendente (staff) por pessoa+equipe

```yaml
id: INV-TEAMS-007
class: A
severity: BLOQUEANTE_VALIDACAO
layer: db
name: idx_team_memberships_person_team_active
rule: "No máximo 1 team_membership (ativo|pendente) com end_at=NULL e deleted_at=NULL por (person_id, team_id)"
status: EVIDENCIADO
evidence:
  - path: docs/ssot/schema.sql
    anchor: "CREATE UNIQUE INDEX idx_team_memberships_person_team_active"
    excerpt: "CREATE UNIQUE INDEX idx_team_memberships_person_team_active ... (person_id, team_id) WHERE ((deleted_at IS NULL) AND (end_at IS NULL) AND (status = ANY ...))"
rationale: "Evita convites duplicados e múltiplos vínculos simultâneos conflitantes."
```

---

## INV-TEAMS-008 — Soft delete atômico em `team_registrations`

```yaml
id: INV-TEAMS-008
class: A
severity: BLOQUEANTE_VALIDACAO
layer: db
name: ck_team_registrations_deleted_reason
rule: "(deleted_at IS NULL AND deleted_reason IS NULL) OR (deleted_at IS NOT NULL AND deleted_reason IS NOT NULL)"
status: EVIDENCIADO
evidence:
  - path: docs/ssot/schema.sql
    anchor: "CONSTRAINT ck_team_registrations_deleted_reason"
    excerpt: "CONSTRAINT ck_team_registrations_deleted_reason CHECK ((((deleted_at IS NULL) AND (deleted_reason IS NULL)) OR ((deleted_at IS NOT NULL) AND (deleted_reason IS NOT NULL))))"
rationale: "Mantém auditabilidade mínima do elenco ao encerrar/arquivar vínculos."
```

---

## INV-TEAMS-009 — Unicidade de vínculo ativo atleta↔equipe (mesma equipe)

```yaml
id: INV-TEAMS-009
class: A
severity: BLOQUEANTE_VALIDACAO
layer: db
name: ux_team_registrations_active
rule: "No máximo 1 team_registration ativo (end_at NULL, deleted_at NULL) por (athlete_id, team_id)"
status: EVIDENCIADO
evidence:
  - path: docs/ssot/schema.sql
    anchor: "CREATE UNIQUE INDEX ux_team_registrations_active"
    excerpt: "CREATE UNIQUE INDEX ux_team_registrations_active ON public.team_registrations ... (athlete_id, team_id) WHERE ((end_at IS NULL) AND (deleted_at IS NULL))"
rationale: "Evita duplicidade do mesmo atleta dentro da mesma equipe."
```

---

## INV-TEAMS-010 — Delete físico bloqueado em `team_registrations`

```yaml
id: INV-TEAMS-010
class: A
severity: BLOQUEANTE_VALIDACAO
layer: db
name: trg_team_registrations_block_delete
rule: "DELETE físico em team_registrations é proibido; usar update end_at/soft delete"
status: EVIDENCIADO
evidence:
  - path: docs/ssot/schema.sql
    anchor: "CREATE TRIGGER trg_team_registrations_block_delete"
    excerpt: "CREATE TRIGGER trg_team_registrations_block_delete BEFORE DELETE ON public.team_registrations ... trg_block_physical_delete()"
rationale: "Preserva histórico de movimentações de elenco."
```

---

## INV-TEAMS-011 — Auto-encerrar vínculos ao atleta virar `dispensada`

```yaml
id: INV-TEAMS-011
class: A
severity: NÃO_BLOQUEANTE
layer: db
name: trg_auto_end_team_registrations_on_dispensada
rule: "Se athletes.state muda para 'dispensada', encerra team_registrations ativos (end_at=now())"
status: EVIDENCIADO
evidence:
  - path: docs/ssot/schema.sql
    anchor: "CREATE FUNCTION public.trg_auto_end_team_registrations_on_dispensada()"
    excerpt: "IF OLD.state != 'dispensada' AND NEW.state = 'dispensada' THEN ... UPDATE team_registrations SET end_at = now() ..."
rationale: "Automação de integridade: atleta dispensada não deve permanecer com vínculo ativo."
```

---

## INV-TEAMS-012 — Reatribuição de coach encerra vínculo antigo antes do novo

```yaml
id: INV-TEAMS-012
class: B
severity: BLOQUEANTE_VALIDACAO
layer: service+api
name: reassign_team_coach_order
rule: "Na reatribuição de coach, encerrar TeamMembership antigo (end_at,status=inativo) antes de criar novo e atualizar team.coach_membership_id"
status: EVIDENCIADO
evidence:
  - path: Hb Track - Backend/app/api/v1/routers/teams.py
    anchor: "reassign_team_coach"
    excerpt: "3. PRIMEIRO - Encerrar vínculo antigo ... 5. DEPOIS: Cria novo TeamMembership ... 6. Atualiza team.coach_membership_id"
rationale: "Evita dois coaches ativos simultâneos e mantém histórico coerente."
```

---

## INV-TEAMS-013 — Reenvio de convite: status pendente + cooldown + limite + refresh de token

```yaml
id: INV-TEAMS-013
class: B
severity: BLOQUEANTE_VALIDACAO
layer: service+api
name: invite_resend_rules
rule: "Somente status='pendente'; cooldown (default 48h); resend_count < max; refresh do PasswordReset(welcome) e reenvio de email"
status: EVIDENCIADO
evidence:
  - path: Hb Track - Backend/app/api/v1/routers/teams.py
    anchor: "resend_team_member_invite"
    excerpt: "if tm.status != 'pendente' ... if tm.resend_count >= settings.INVITE_MAX_RESEND_COUNT ... cooldown ... password_reset.created_at = now"
rationale: "Evita spam e garante token de welcome válido e auditável."
```

---

## INV-TEAMS-014 — Cancelamento de convite revoga token e faz soft delete do vínculo

```yaml
id: INV-TEAMS-014
class: B
severity: BLOQUEANTE_VALIDACAO
layer: service+api
name: invite_cancel_rules
rule: "Cancelar convite marca token como usado e soft-deleta TeamMembership pendente"
status: EVIDENCIADO
evidence:
  - path: docs/ssot/openapi.json
    anchor: "operationId: cancel_team_member_invite_api_v1_teams__team_id__members__membership_id__cancel_invite_delete"
    excerpt: "Marca token como usado (used_at = now) para desativar\\n- Soft delete do TeamMembership\\n- **NÃO envia email ao convidado** (cancelamento silencioso)"
rationale: "Cancelamento silencioso e revogação imediata do token."
```

---

## INV-TEAMS-015 — Remoção de staff é condicional (coach vs outros)

```yaml
id: INV-TEAMS-015
class: B
severity: BLOQUEANTE_VALIDACAO
layer: service+api
name: remove_staff_member_conditional
rule: "Se role_id=3: encerra vínculo e limpa team.coach_membership_id; caso contrário soft delete"
status: EVIDENCIADO
evidence:
  - path: Hb Track - Backend/app/api/v1/routers/teams.py
    anchor: "remove_staff_member"
    excerpt: "is_coach = role.id == 3 ... if is_coach: ... team.coach_membership_id = None ... else: team_membership.deleted_at = now"
rationale: "Treinador principal tem semântica especial; demais vínculos são removidos logicamente."
```

---

## INV-TEAMS-016 — Não permitir duplicidade de equipe ativa (service-level)

```yaml
id: INV-TEAMS-016
class: B
severity: BLOQUEANTE_VALIDACAO
layer: service
name: team_duplicate_guard
rule: "Proibir duplicidade ativa por (organization_id, category_id, gender, name) — service check"
status: EVIDENCIADO
evidence:
  - path: Hb Track - Backend/app/services/team_service.py
    anchor: "TeamService.create (existing duplicate check)"
    excerpt: "select(Team).where(Team.organization_id == organization_id, Team.category_id == category_id, Team.gender == gender, Team.name == name, Team.deleted_at.is_(None))"
rationale: "Garante UX coerente; sem UNIQUE no DB, permanece sujeito a race condition (GAP separado)."
```

---

## INV-TEAMS-017 — Listagem de equipes respeita vínculo (não-superadmin)

```yaml
id: INV-TEAMS-017
class: B
severity: BLOQUEANTE_VALIDACAO
layer: service
name: list_teams_scope_by_membership
rule: "Se não-superadmin: listar apenas teams com TeamMembership status ('ativo'|'pendente') da person_id"
status: EVIDENCIADO
evidence:
  - path: Hb Track - Backend/app/services/team_service.py
    anchor: "TeamService.list_teams (join TeamMembership)"
    excerpt: "query = query.join(TeamMembership, ...).where(TeamMembership.status.in_(['ativo','pendente']))"
rationale: "Evita exfiltração de dados entre equipes não vinculadas."
```

---

## INV-TEAMS-018 — Staff list deve suportar `active_only`

```yaml
id: INV-TEAMS-018
class: B
severity: BLOQUEANTE_VALIDACAO
layer: api
name: get_team_staff_active_only
rule: "GET /teams/{team_id}/staff?active_only=true retorna apenas status='ativo' e end_at=NULL"
status: EVIDENCIADO
evidence:
  - path: Hb Track - Backend/app/api/v1/routers/teams.py
    anchor: "get_team_staff (active_only filter)"
    excerpt: "if active_only: ... TeamMembership.status == 'ativo', TeamMembership.end_at.is_(None)"
rationale: "Base para tela Members/Staff e para filtros de gestão."
```

---

## INV-TEAMS-019 — Exclusão de equipe é soft delete com `reason` (compatível com ck_teams_deleted_reason)

```yaml
id: INV-TEAMS-019
class: A+B
severity: BLOQUEANTE_VALIDACAO
layer: service+db
name: team_soft_delete_reason_required
rule: "Ao marcar deleted_at, deve existir deleted_reason (não pode ser NULL)"
status: EVIDENCIADO
evidence:
  - path: Hb Track - Backend/app/api/v1/routers/teams.py
    anchor: "delete_team (reason Query)"
    excerpt: "reason: str = Query('Exclusão manual', ...); await service.soft_delete(team, reason=reason)"
rationale: "Sem `reason`, o DB bloqueia pelo ck_teams_deleted_reason."
```

---

## INV-TEAMS-020 — (PRD) TeamRegistrations não sobrepostas por pessoa+equipe+temporada

```yaml
id: INV-TEAMS-020
class: A+B
severity: BLOQUEANTE_VALIDACAO
layer: db+service
name: RDB10_non_overlapping_team_registrations
rule: "Não permitir sobreposição temporal para mesma pessoa+equipe+temporada"
status: GAP
decision_required: true
evidence:
  - path: docs/hbtrack/PRD Hb Track.md
    anchor: "RDB10"
    excerpt: "RDB10: TeamRegistrations não sobrepostas para mesma pessoa+equipe+temporada"
rationale: "SSOT DB atual não contém season_id em team_registrations; exige decisão de modelo/normalização."
```

---

## INV-TEAMS-021 — (Drift) FE aceita `gender='misto'` mas DB bloqueia

```yaml
id: INV-TEAMS-021
class: D
severity: BLOQUEANTE_VALIDACAO
layer: db+fe
name: gender_misto_drift
rule: "Alinhar domínio de gênero entre FE e DB (permitir 'misto' OU remover do FE)"
status: GAP
decision_required: true
evidence:
  - path: Hb Track - Frontend/src/lib/api/teams.ts
    anchor: "export type TeamGender"
    excerpt: "export type TeamGender = \"feminino\" | \"masculino\" | \"misto\";"
rationale: "Hoje, payload com 'misto' deve falhar no DB (INV-TEAMS-001)."
```
