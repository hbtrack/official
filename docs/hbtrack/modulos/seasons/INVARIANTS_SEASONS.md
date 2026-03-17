---
module: "seasons"
system_scope_ref: "../../../_canon/SYSTEM_SCOPE.md"
handball_rules_ref: "../../../_canon/HANDBALL_RULES_DOMAIN.md"
handball_semantic_applicability: false
contract_path_ref: "../../../../contracts/openapi/paths/seasons.yaml"
schemas_ref: "../../../../contracts/schemas/seasons/"
type: "invariants"
updated: "2026-03-16"
---

# INVARIANTS_SEASONS.md

## Objetivo
Registrar invariantes do módulo `seasons`.

## Definição
Invariantes são condições que devem permanecer verdadeiras independentemente do fluxo, endpoint ou interface.

## Invariantes globais vinculantes
- `.contract_driven/DOMAIN_AXIOMS.json`
- `docs/_canon/GLOBAL_INVARIANTS.md`

## Tabela de invariantes
| ID | Invariante | Entidades | Fonte | Como verificar |
|---|---|---|---|---|
| INV-SEAS-001 | `id`, `name`, `startDate` e `endDate` são obrigatórios para toda temporada publicada como shape estável. | `Season` | `season.schema.json` | JSON Schema validation |
| INV-SEAS-002 | `startDate` deve ser menor ou igual a `endDate`. | `Season` | Regra temporal do módulo | Teste de contrato e validação de domínio |
| INV-SEAS-003 | `phaseLabels`, `competitionIds` e `teamIds` são listas sem duplicidade. | `Season` | Schema local | `uniqueItems` + auditoria de payload |
| INV-SEAS-004 | `seasons` não pode carregar scorekeeping, taxonomia de scout, semântica médica nem política de autenticação. | `Season` | Authority matrix `must_not_infer` | Revisão de contrato + gates de boundary |

## Relação com outros documentos
- `docs/hbtrack/modulos/seasons/DOMAIN_RULES_SEASONS.md`
- `contracts/schemas/seasons/season.schema.json`
