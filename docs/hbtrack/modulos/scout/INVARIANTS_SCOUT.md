---
module: "scout"
system_scope_ref: "../../../_canon/SYSTEM_SCOPE.md"
handball_rules_ref: "../../../_canon/HANDBALL_RULES_DOMAIN.md"
handball_semantic_applicability: true
contract_path_ref: "../../../../contracts/openapi/paths/scout.yaml"
schemas_ref: "../../../../contracts/schemas/scout/"
type: "invariants"
updated: "2026-03-16"
---

# INVARIANTS_SCOUT.md

## Objetivo
Registrar invariantes do módulo `scout`.

## Definição
Invariantes são condições que devem permanecer verdadeiras independentemente do fluxo, endpoint ou interface.

## Invariantes globais vinculantes
- `.contract_driven/DOMAIN_AXIOMS.json`
- `docs/_canon/GLOBAL_INVARIANTS.md`

## Tabela de invariantes
| ID | Invariante | Entidades | Fonte | Como verificar |
|---|---|---|---|---|
| INV-SCOUT-001 | `id`, `matchId`, `eventLabel` e `recordedAt` são obrigatórios. | `ScoutEvent` | `scout_event.schema.json` | JSON Schema validation |
| INV-SCOUT-002 | `tagLabels` e `clipAssetRefs`, quando presentes, são coleções sem duplicidade. | `ScoutEvent` | Schema local | `uniqueItems` + auditoria de payload |
| INV-SCOUT-003 | Campos de taxonomia observacional (`eventLabel`, `tagLabels`, `codingSchemaLabel`) devem ser verificáveis contra `CANONICAL_EVENT_TAXONOMY_SCOUT.yaml`. | `ScoutEvent` | `SCOUT_TAXONOMY_GATE` | Gate de taxonomia |
| INV-SCOUT-004 | `scout` não pode redefinir placar oficial, regra IHF ou estatística oficial de competição sem mapeamento explícito. | `ScoutEvent` | Authority matrix `must_not_infer` | Revisão de contrato |

## Relação com outros documentos
- `docs/hbtrack/modulos/scout/DOMAIN_RULES_SCOUT.md`
- `contracts/schemas/scout/scout_event.schema.json`
