---
module: "wellness"
system_scope_ref: "../../../_canon/SYSTEM_SCOPE.md"
handball_rules_ref: "../../../_canon/HANDBALL_RULES_DOMAIN.md"
handball_semantic_applicability: false
contract_path_ref: "../../../../contracts/openapi/paths/wellness.yaml"
schemas_ref: "../../../../contracts/schemas/wellness/"
---

# TEST_MATRIX_WELLNESS.md

## Objetivo
Definir a matriz mínima de testes e evidências que sustentam os contratos do módulo.

## Matriz (mínimo)
| ID | Artefato | Tipo de verificação | Obrigatório | Evidência |
|---|---|---|:---:|---|
| TM-001 | `contracts/openapi/paths/wellness.yaml` | Lint OpenAPI (Redocly/Spectral) | Sim | `_reports/contract_gates/latest.json` |
| TM-002 | `contracts/schemas/wellness/` | Validação JSON Schema | Sim | `_reports/contract_gates/latest.json` |
| TM-003 | `DOMAIN_RULES_WELLNESS.md` | Revisão normativa + testes de regra (quando existir) | Condicional | `_reports/contract_gates/latest.json` |
| TM-004 | `INVARIANTS_WELLNESS.md` | Teste de invariantes (quando existir) | Condicional | `_reports/contract_gates/latest.json` |

## Obrigações estruturadas
- O conjunto mínimo compilável do módulo está em `docs/hbtrack/modulos/wellness/graph/test_obligations.yaml`.
- O pipeline deve manter `test_obligations.yaml` coerente com `contracts/`, `src/wellness/tests/` e `_reports/contract_gates/latest.json`.
