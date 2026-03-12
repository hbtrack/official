---
# TEMPLATE: module-doc-template
# DEST: docs/hbtrack/modulos/<module>/TEST_MATRIX_{{MODULE_NAME_UPPER}}.md
# SOURCE: .contract_driven/templates/modulos/TEST_MATRIX_{{MODULE_NAME_UPPER}}.md
module: "{{MODULE_NAME}}"
system_scope_ref: "../../../_canon/SYSTEM_SCOPE.md"
handball_rules_ref: "../../../_canon/HANDBALL_RULES_DOMAIN.md"
type: "test-matrix"
---

# TEST_MATRIX_{{MODULE_NAME_UPPER}}.md

## Objetivo
Mapear a cobertura mínima de testes do módulo `{{MODULE_NAME}}`.

## Princípio
Toda superfície contratual e toda regra crítica do módulo deve ter prova correspondente.

## Matriz
| ID | Área | Artefato-fonte | Tipo de teste | Ferramenta | Obrigatório | Evidência |
|---|---|---|---|---|---|---|
| TM-001 | API | `contracts/openapi/paths/{{MODULE_NAME}}.yaml` | Contract | {{CONTRACT_TEST_TOOL}} | Sim | {{EVIDENCE}} |
| TM-002 | Schema | `contracts/schemas/{{MODULE_NAME}}/*.schema.json` | Schema validation | {{SCHEMA_TEST_TOOL}} | Sim | {{EVIDENCE}} |
| TM-003 | Estado (condicional) | `STATE_MODEL_{{MODULE_NAME_UPPER}}.md` | Transition test | {{STATE_TEST_TOOL}} | Quando aplicável | {{EVIDENCE}} |
| TM-004 | Regra de domínio | `DOMAIN_RULES_{{MODULE_NAME_UPPER}}.md` | Business rule test | {{BUSINESS_RULE_TOOL}} | Sim | {{EVIDENCE}} |
| TM-005 | Invariantes | `INVARIANTS_{{MODULE_NAME_UPPER}}.md` | Invariant test | {{INVARIANT_TEST_TOOL}} | Sim | {{EVIDENCE}} |

## Casos mínimos obrigatórios
- payload válido
- payload inválido
- erro esperado
- transição válida (quando módulo tem lifecycle)
- transição inválida (quando módulo tem lifecycle)
- violação de regra de domínio
- violação de invariante

## Regra
Nenhuma feature do módulo pode ser considerada pronta sem evidência mínima nesta matriz.
