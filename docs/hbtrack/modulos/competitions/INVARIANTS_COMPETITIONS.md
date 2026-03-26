---
module: "competitions"
system_scope_ref: "../../../_canon/SYSTEM_SCOPE.md"
handball_rules_ref: "../../../_canon/HANDBALL_RULES_DOMAIN.md"
handball_semantic_applicability: true
contract_path_ref: "../../../../contracts/openapi/paths/competitions.yaml"
schemas_ref: "../../../../contracts/schemas/competitions/"
type: "invariants"
updated: "2026-03-16"
---

# INVARIANTS_COMPETITIONS.md

## Objetivo
Registrar invariantes do módulo `competitions`.

## Definição
Invariantes são condições que devem permanecer verdadeiras independentemente do fluxo, endpoint ou interface.

## Invariantes globais vinculantes
- `.contract_driven/DOMAIN_AXIOMS.json`
- `docs/_canon/GLOBAL_INVARIANTS.md`

## Tabela de invariantes
| ID | Invariante | Entidades | Fonte | Como verificar |
|---|---|---|---|---|
| INV-COMP-001 | `id`, `seasonId`, `name` e `startDate` são obrigatórios em toda competição. | `Competition` | `competition.schema.json` | JSON Schema validation |
| INV-COMP-002 | `startDate` deve ser menor ou igual a `endDate` quando `endDate` estiver presente. | `Competition` | Regra temporal do módulo | Teste de contrato |
| INV-COMP-003 | `stageLabels`, `calendarEntryIds` e `registrationTeamIds` são listas sem duplicidade. | `Competition` | Schema local | `uniqueItems` + auditoria de payload |
| INV-COMP-004 | `competitions` não pode carregar taxonomia detalhada de scout, scorekeeping oficial de partida fora do contrato nem regras de autenticação. | `Competition` | Authority matrix `must_not_infer` | Revisão de contrato |

## Relação com outros documentos
- `docs/hbtrack/modulos/competitions/DOMAIN_RULES_COMPETITIONS.md`
- `contracts/schemas/competitions/competition.schema.json`
