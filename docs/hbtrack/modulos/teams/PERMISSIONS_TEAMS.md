---
module: "teams"
system_scope_ref: "../../../_canon/SYSTEM_SCOPE.md"
handball_rules_ref: "../../../_canon/HANDBALL_RULES_DOMAIN.md"
handball_semantic_applicability: true
type: "permissions"
adr_refs:
  - "ADR-008: authz-strategy (RBAC flat, 5 roles)"
  - "ADR-007: auth-strategy (JWT Bearer)"
domain_rules_ref: "./DOMAIN_RULES_TEAMS.md"
updated_at: "2026-03-19"
---

# PERMISSIONS_TEAMS.md

> **Nota canônica:** O módulo `identity_access` é a fonte soberana de autorização.
> Este artefato **documenta** como `teams` aplica a policy — não a redefine.
> Roles canônicos: `admin`, `coordinator`, `coach`, `athlete`, `member` (ADR-008).
> Enforcement por operação, via guards no Router (BFLA) e Service (BOLA, BOPLA).

---

## Tabela de Permissões por Operação

| Operação (operationId) | admin | coordinator | coach | athlete | member | Observação |
|---|---|---|---|---|---|---|
| `listTeams` | ✅ | ✅ | ✅ | ✅ | ✅ | Times são entidades públicas do contexto esportivo |
| `createTeam` | ✅ | ✅ | ❌ | ❌ | ❌ | Criação de time requer gestão |
| `getTeam` | ✅ | ✅ | ✅ | ✅ | ✅ | Detalhes básicos de time são dados públicos |
| `patchTeam` | ✅ | ✅ | ✅ (próprio time) | ❌ | ❌ | coach pode editar dados operacionais do time que lidera |
| `addAthleteToTeam` | ✅ | ✅ | ✅ (próprio time) | ❌ | ❌ | Gestão de roster — coach do time pode adicionar atletas |
| `removeAthleteFromTeam` | ✅ | ✅ | ✅ (próprio time) | ❌ | ❌ | Remoção de atleta — mesmo escopo de adição |
| `addStaffToTeam` | ✅ | ✅ | ❌ | ❌ | ❌ | Adição de staff (coaches) requer gestão |
| `removeStaffFromTeam` | ✅ | ✅ | ❌ | ❌ | ❌ | Remoção de staff requer gestão |

---

## Regras de contexto cross-operação

| ID | Regra | Ref |
|---|---|---|
| PERM-TEAM-001 | coach só pode gerenciar atletas e dados operacionais do time ao qual está vinculado | ADR-008, DOMAIN_RULES_TEAMS |
| PERM-TEAM-002 | Adição de um segundo coach ao mesmo time requer aprovação de coordinator | DOMAIN_RULES_TEAMS |
| PERM-TEAM-003 | Athlete não pode ver informações de composição de roster de outros times (dados táticos) | ADR-010 |
| PERM-TEAM-004 | Remoção de staff (removeStaffFromTeam) com sessões ativas vinculadas bloqueia até resolução | DOMAIN_RULES_TEAMS |
