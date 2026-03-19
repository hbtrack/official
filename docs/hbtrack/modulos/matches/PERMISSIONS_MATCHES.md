---
module: "matches"
system_scope_ref: "../../../_canon/SYSTEM_SCOPE.md"
handball_rules_ref: "../../../_canon/HANDBALL_RULES_DOMAIN.md"
handball_semantic_applicability: true
type: "permissions"
adr_refs:
  - "ADR-008: authz-strategy (RBAC flat, 5 roles)"
  - "ADR-007: auth-strategy (JWT Bearer)"
domain_rules_ref: "./DOMAIN_RULES_MATCHES.md"
updated_at: "2026-03-19"
---

# PERMISSIONS_MATCHES.md

> **Nota canônica:** O módulo `identity_access` é a fonte soberana de autorização.
> Este artefato **documenta** como `matches` aplica a policy — não a redefine.
> Roles canônicos: `admin`, `coordinator`, `coach`, `athlete`, `member` (ADR-008).
> Enforcement por operação, via guards no Router (BFLA) e Service (BOLA, BOPLA).

---

## Tabela de Permissões por Operação

| Operação (operationId) | admin | coordinator | coach | athlete | member | Observação |
|---|---|---|---|---|---|---|
| `listMatches` | ✅ | ✅ | ✅ | ✅ | ✅ | Partidas são dados públicos esportivos |
| `createMatch` | ✅ | ✅ | ❌ | ❌ | ❌ | Criação de partida requer gestão (vinculada a competition/season) |
| `getMatch` | ✅ | ✅ | ✅ | ✅ | ✅ | Detalhes de partida são dados públicos esportivos |
| `patchMatch` | ✅ | ✅ | ✅ (operacional) | ❌ | ❌ | coach pode atualizar dados operacionais (lineup, score); coordinator/admin editam metadados |
| `addPlayerToLineup` | ✅ | ✅ | ✅ | ❌ | ❌ | Gestão de lineup é responsabilidade do coach |
| `removePlayerFromLineup` | ✅ | ✅ | ✅ | ❌ | ❌ | Remoção de lineup requer mesma autoridade de inclusão |

---

## Regras de contexto cross-operação

| ID | Regra | Ref |
|---|---|---|
| PERM-MATCH-001 | Partidas em status COMPLETED são read-only para todos os roles | DOMAIN_RULES_MATCHES |
| PERM-MATCH-002 | Edição de lineup somente permite durante status SCHEDULED ou antes de kickoff (DOMAIN_RULES_MATCHES) | DOMAIN_RULES_MATCHES |
| PERM-MATCH-003 | Athlete não acessa informações de lineup de adversários antes de publicação oficial | ADR-010 (sensitive data) |
