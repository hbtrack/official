---
module: "analytics"
system_scope_ref: "../../../_canon/SYSTEM_SCOPE.md"
handball_rules_ref: "../../../_canon/HANDBALL_RULES_DOMAIN.md"
handball_semantic_applicability: false
contract_path_ref: "../../../../contracts/openapi/paths/analytics.yaml"
schemas_ref: "../../../../contracts/schemas/analytics/"
---

# TEST_MATRIX_ANALYTICS.md

## Objetivo
Definir a matriz mínima de testes e evidências que sustentam os contratos do módulo.

## Matriz (mínimo)
| ID | Artefato | Tipo de verificação | Obrigatório | Evidência |
|---|---|---|:---:|---|
| TM-001 | `contracts/openapi/paths/analytics.yaml` | Lint OpenAPI (Redocly/Spectral) | Sim | `_reports/contract_gates/latest.json` |
| TM-002 | `contracts/schemas/analytics/` | Validação JSON Schema | Sim | `_reports/contract_gates/latest.json` |
| TM-003 | `DOMAIN_RULES_ANALYTICS.md` | Revisão normativa + testes de regra (quando existir) | Condicional | `_reports/contract_gates/latest.json` |
| TM-004 | `INVARIANTS_ANALYTICS.md` | Teste de invariantes (quando existir) | Condicional | `_reports/contract_gates/latest.json` |
| TM-005 | `ERRORS_ANALYTICS.md` | Revisão da matriz mínima de exceções por operação crítica | Sim | `_reports/contract_gates/latest.json` |
| TM-006 | `analytics_query_request.schema.json` + `analytics_query_response.schema.json` | Validação de query estruturada sem DSL livre nem row shape aberto | Sim | `_reports/contract_gates/latest.json` |

## Obrigações estruturadas
- O conjunto mínimo compilável do módulo está em `docs/hbtrack/modulos/analytics/graph/test_obligations.yaml`.
- O pipeline deve manter `test_obligations.yaml` coerente com `contracts/`, `src/analytics/tests/` e `_reports/contract_gates/latest.json`.
