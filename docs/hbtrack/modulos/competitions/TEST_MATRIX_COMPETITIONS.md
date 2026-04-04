---
module: "competitions"
system_scope_ref: "../../../_canon/SYSTEM_SCOPE.md"
handball_rules_ref: "../../../_canon/HANDBALL_RULES_DOMAIN.md"
handball_semantic_applicability: true
contract_path_ref: "../../../../contracts/openapi/paths/competitions.yaml"
schemas_ref: "../../../../contracts/schemas/competitions/"
---

# TEST_MATRIX_COMPETITIONS.md

## Objetivo
Definir a matriz mínima de testes e evidências que sustentam os contratos do módulo.

## Matriz (mínimo)
| ID | Artefato | Tipo de verificação | Obrigatório | Evidência |
|---|---|---|:---:|---|
| TM-001 | `contracts/openapi/paths/competitions.yaml` | Lint OpenAPI (Redocly/Spectral) | Sim | `_reports/contract_gates/latest.json` |
| TM-002 | `contracts/schemas/competitions/` | Validação JSON Schema | Sim | `_reports/contract_gates/latest.json` |
| TM-003 | `DOMAIN_RULES_COMPETITIONS.md` | Revisão normativa + testes de regra (quando existir) | Condicional | `_reports/contract_gates/latest.json` |
| TM-004 | `INVARIANTS_COMPETITIONS.md` | Teste de invariantes (quando existir) | Condicional | `_reports/contract_gates/latest.json` |
| TM-005 | `graph/test_obligations.yaml` | Source graph — obrigações de teste COMP-TO-001..004 | Sim | `tests/pipeline_gates/test_competitions_source_graph_integrity.py` |

## Obrigações
- Obrigações: [graph/test_obligations.yaml](graph/test_obligations.yaml)
