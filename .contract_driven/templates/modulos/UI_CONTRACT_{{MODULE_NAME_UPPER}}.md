---
# TEMPLATE: module-doc-template
# DEST: docs/hbtrack/modulos/<module>/UI_CONTRACT_{{MODULE_NAME_UPPER}}.md
# SOURCE: .contract_driven/templates/modulos/UI_CONTRACT_{{MODULE_NAME_UPPER}}.md
module: "{{MODULE_NAME}}"
system_scope_ref: "../../../_canon/SYSTEM_SCOPE.md"
handball_rules_ref: "../../../_canon/HANDBALL_RULES_DOMAIN.md"
type: "ui-contract"
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
