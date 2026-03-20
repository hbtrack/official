---
module: "competitions"
system_scope_ref: "../../../_canon/SYSTEM_SCOPE.md"
handball_rules_ref: "../../../_canon/HANDBALL_RULES_DOMAIN.md"
handball_semantic_applicability: true
type: "permissions"
adr_refs:
  - "ADR-008: authz-strategy (RBAC flat, 5 roles)"
  - "ADR-007: auth-strategy (JWT Bearer)"
domain_rules_ref: "./DOMAIN_RULES_COMPETITIONS.md"
invariants_ref: "./INVARIANTS_COMPETITIONS.md"
updated_at: "2026-03-19"
---

# PERMISSIONS_COMPETITIONS.md

> **Nota canônica:** O módulo `identity_access` é a fonte soberana de autorização.
> Este artefato **documenta** como `competitions` aplica a policy — não a redefine.
> Roles canônicos: `admin`, `coordinator`, `coach`, `athlete`, `member` (ADR-008).
> Enforcement por operação, via guards no Router (BFLA) e Service (BOLA, BOPLA).

---

## Tabela de Permissões por Operação

| Operação (operationId) | admin | coordinator | coach | athlete | member | Observação |
|---|---|---|---|---|---|---|
| `listCompetitions` | ✅ | ✅ | ✅ | ✅ | ✅ | Competições são dados públicos do contexto esportivo |
| `createCompetition` | ✅ | ✅ | ❌ | ❌ | ❌ | Criação de competição requer role de gestão |
| `getCompetition` | ✅ | ✅ | ✅ | ✅ | ✅ | Detalhes de competição são públicos |
| `patchCompetition` | ✅ | ✅ | ❌ | ❌ | ❌ | Edição restrita a gestores |
| `registerTeamInCompetition` | ✅ | ✅ | ❌ | ❌ | ❌ | Inscrição de time requer aprovação formal |
| `unregisterTeamFromCompetition` | ✅ | ✅ | ❌ | ❌ | ❌ | Desincrição irreversível após deadline — somente gestores |

---

## Regras de contexto cross-operação

| ID | Regra | Ref |
|---|---|---|
| PERM-COMP-001 | Inscrição de time em competição gera evento contratual imutável após deadline | DOMAIN_RULES_COMPETITIONS |
| PERM-COMP-002 | Patchs em competições ativas (status IN_PROGRESS) exigem role admin | DOMAIN_RULES_COMPETITIONS |
| PERM-COMP-003 | Listagem e leitura de competições são operações abertas — sem restrição de role (dados públicos esportivos) | ADR-008 |
