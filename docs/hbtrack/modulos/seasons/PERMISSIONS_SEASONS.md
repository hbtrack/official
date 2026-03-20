---
module: "seasons"
system_scope_ref: "../../../_canon/SYSTEM_SCOPE.md"
handball_rules_ref: "../../../_canon/HANDBALL_RULES_DOMAIN.md"
handball_semantic_applicability: true
type: "permissions"
adr_refs:
  - "ADR-008: authz-strategy (RBAC flat, 5 roles)"
  - "ADR-007: auth-strategy (JWT Bearer)"
domain_rules_ref: "./DOMAIN_RULES_SEASONS.md"
invariants_ref: "./INVARIANTS_SEASONS.md"
updated_at: "2026-03-19"
---

# PERMISSIONS_SEASONS.md

> **Nota canônica:** O módulo `identity_access` é a fonte soberana de autorização.
> Este artefato **documenta** como `seasons` aplica a policy — não a redefine.
> Roles canônicos: `admin`, `coordinator`, `coach`, `athlete`, `member` (ADR-008).
> Enforcement por operação, via guards no Router (BFLA) e Service (BOLA, BOPLA).

---

## Tabela de Permissões por Operação

| Operação (operationId) | admin | coordinator | coach | athlete | member | Observação |
|---|---|---|---|---|---|---|
| `listSeasons` | ✅ | ✅ | ✅ | ✅ | ✅ | Temporadas são dados públicos do contexto esportivo |
| `createSeason` | ✅ | ✅ | ❌ | ❌ | ❌ | Criação de temporada requer role de gestão |
| `getSeason` | ✅ | ✅ | ✅ | ✅ | ✅ | Detalhes de temporada são dados públicos |
| `patchSeason` | ✅ | ✅ | ❌ | ❌ | ❌ | Edição de temporada restrita a gestores |
| `addTeamToSeason` | ✅ | ✅ | ❌ | ❌ | ❌ | Associação de time a temporada requer gestão |
| `removeTeamFromSeason` | ✅ | ✅ | ❌ | ❌ | ❌ | Desassociação requer gestão; irreversível após inicio da temporada |

---

## Regras de contexto cross-operação

| ID | Regra | Ref |
|---|---|---|
| PERM-SEA-001 | Temporadas em status ACTIVE não podem ter times removidos por coordinator (somente admin) | DOMAIN_RULES_SEASONS |
| PERM-SEA-002 | Patchs em temporadas COMPLETED são somente para admin (dados históricos) | DOMAIN_RULES_SEASONS |
| PERM-SEA-003 | Listagem e leitura de temporadas são operações abertas — dados públicos esportivos | ADR-008 |
