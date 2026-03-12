---
module: "audit"
system_scope_ref: "../../../_canon/SYSTEM_SCOPE.md"
handball_rules_ref: "../../../_canon/HANDBALL_RULES_DOMAIN.md"
handball_semantic_applicability: false
contract_path_ref: "../../../../contracts/openapi/paths/audit.yaml"
schemas_ref: "../../../../contracts/schemas/audit/"
---

# TEST_MATRIX_AUDIT.md

## Objetivo
Definir a matriz mínima de testes e evidências que sustentam os contratos do módulo.

## Matriz (mínimo)
| ID | Artefato | Tipo de verificação | Obrigatório | Evidência |
|---|---|---|:---:|---|
| TM-001 | `contracts/openapi/paths/audit.yaml` | Lint OpenAPI (Redocly/Spectral) | Sim | `_reports/contract_gates/latest.json` |
| TM-002 | `contracts/schemas/audit/` | Validação JSON Schema | Sim | `_reports/contract_gates/latest.json` |
| TM-003 | `DOMAIN_RULES_AUDIT.md` | Revisão normativa + testes de regra (quando existir) | Condicional | `_reports/contract_gates/latest.json` |
| TM-004 | `INVARIANTS_AUDIT.md` | Teste de invariantes (quando existir) | Condicional | `_reports/contract_gates/latest.json` |
