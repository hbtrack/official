---
# TEMPLATE: module-doc-template
# DEST: docs/hbtrack/modulos/<module>/UI_CONTRACT_{{MODULE_NAME_UPPER}}.md
# SOURCE: .contract_driven/templates/modulos/UI_CONTRACT_{{MODULE_NAME_UPPER}}.md
module: "{{MODULE_NAME}}"
system_scope_ref: "../../../_canon/SYSTEM_SCOPE.md"
handball_rules_ref: "../../../_canon/HANDBALL_RULES_DOMAIN.md"
handball_semantic_applicability: {{HANDBALL_SEMANTIC_APPLICABILITY}}
type: "ui-contract"
contract_path_ref: "../../../../contracts/openapi/paths/{{MODULE_NAME}}.yaml"
schemas_ref: "../../../../contracts/schemas/{{MODULE_NAME}}/"
module_scope_ref: "./MODULE_SCOPE_{{MODULE_NAME_UPPER}}.md"
---
# UI_CONTRACT_{{MODULE_NAME_UPPER}}.md

## Entradas
- {{INPUT}}

## Saídas
- {{OUTPUT}}

## Estados
- loading
- success
- empty
- error

## Ações
- {{ACTION}}

## Erros
- {{ERROR_CASE}}
