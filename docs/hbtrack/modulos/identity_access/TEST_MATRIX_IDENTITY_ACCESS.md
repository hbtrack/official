---
module: "identity_access"
system_scope_ref: "../../../_canon/SYSTEM_SCOPE.md"
handball_rules_ref: "../../../_canon/HANDBALL_RULES_DOMAIN.md"
handball_semantic_applicability: false
contract_path_ref: "../../../../contracts/openapi/paths/identity_access.yaml"
schemas_ref: "../../../../contracts/schemas/identity_access/"
---

# TEST_MATRIX_IDENTITY_ACCESS.md

## Objetivo
Definir a matriz mínima de testes e evidências que sustentam os contratos do módulo.

## Matriz (mínimo)
| ID | Artefato | Tipo de verificação | Obrigatório | Evidência |
|---|---|---|:---:|---|
| TM-001 | `contracts/openapi/paths/identity_access.yaml` | Lint OpenAPI (Redocly/Spectral) | Sim | `_reports/contract_gates/latest.json` |
| TM-002 | `contracts/schemas/identity_access/` | Validação JSON Schema | Sim | `_reports/contract_gates/latest.json` |
| TM-003 | `DOMAIN_RULES_IDENTITY_ACCESS.md` | Revisão normativa + testes de regra (quando existir) | Condicional | `_reports/contract_gates/latest.json` |
| TM-004 | `INVARIANTS_IDENTITY_ACCESS.md` | Teste de invariantes (quando existir) | Condicional | `_reports/contract_gates/latest.json` |
