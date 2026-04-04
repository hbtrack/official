---
module: "matches"
system_scope_ref: "../../../_canon/SYSTEM_SCOPE.md"
handball_rules_ref: "../../../_canon/HANDBALL_RULES_DOMAIN.md"
handball_semantic_applicability: true
contract_path_ref: "../../../../contracts/openapi/paths/matches.yaml"
schemas_ref: "../../../../contracts/schemas/matches/"
---

# TEST_MATRIX_MATCHES.md

## Objetivo
Definir a matriz mínima de testes e evidências que sustentam os contratos do módulo.

## Matriz (mínimo)
| ID | Artefato | Tipo de verificação | Obrigatório | Evidência |
|---|---|---|:---:|---|
| TM-001 | `contracts/openapi/paths/matches.yaml` | Lint OpenAPI (Redocly/Spectral) | Sim | `_reports/contract_gates/latest.json` |
| TM-002 | `contracts/schemas/matches/` | Validação JSON Schema | Sim | `_reports/contract_gates/latest.json` |
| TM-003 | `DOMAIN_RULES_MATCHES.md` | Revisão normativa + testes de regra (quando existir) | Condicional | `_reports/contract_gates/latest.json` |
| TM-004 | `INVARIANTS_MATCHES.md` | Teste de invariantes (quando existir) | Condicional | `_reports/contract_gates/latest.json` |
| TM-005 | `graph/test_obligations.yaml` | Source graph — obrigações de teste MATCH-TO-001..004 | Sim | `tests/pipeline_gates/test_matches_source_graph_integrity.py` |

## Obrigações
- Obrigações: [graph/test_obligations.yaml](graph/test_obligations.yaml)
