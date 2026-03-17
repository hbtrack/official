---
module: "matches"
system_scope_ref: "../../../_canon/SYSTEM_SCOPE.md"
handball_rules_ref: "../../../_canon/HANDBALL_RULES_DOMAIN.md"
handball_semantic_applicability: true
contract_path_ref: "../../../../contracts/openapi/paths/matches.yaml"
schemas_ref: "../../../../contracts/schemas/matches/"
type: "invariants"
updated: "2026-03-16"
---

# INVARIANTS_MATCHES.md

## Objetivo
Registrar invariantes do módulo `matches`.

## Definição
Invariantes são condições que devem permanecer verdadeiras independentemente do fluxo, endpoint ou interface.

## Invariantes globais vinculantes
- `.contract_driven/DOMAIN_AXIOMS.json`
- `docs/_canon/GLOBAL_INVARIANTS.md`

## Tabela de invariantes
| ID | Invariante | Entidades | Fonte | Como verificar |
|---|---|---|---|---|
| INV-MATCH-001 | `id`, `competitionId`, `homeTeamId`, `awayTeamId` e `scheduledAt` são obrigatórios. | `Match` | `match.schema.json` | JSON Schema validation |
| INV-MATCH-002 | `homeTeamId` deve ser diferente de `awayTeamId`. | `Match` | Regra estrutural do módulo | Teste de contrato |
| INV-MATCH-003 | `homeScore` e `awayScore`, quando presentes, são inteiros maiores ou iguais a zero. | `Match` | Schema local | Range validation |
| INV-MATCH-004 | Se `startedAt` e `endedAt` estiverem presentes, então `startedAt <= endedAt`. | `Match` | Regra temporal do módulo | Teste de contrato |
| INV-MATCH-005 | `lineupUserIds`, `officialIncidentIds` e `refereeNames` são coleções sem duplicidade. | `Match` | Schema local | `uniqueItems` + auditoria de payload |

## Relação com outros documentos
- `docs/hbtrack/modulos/matches/DOMAIN_RULES_MATCHES.md`
- `contracts/schemas/matches/match.schema.json`
