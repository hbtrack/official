---
# TEMPLATE: module-doc-template
# DEST: docs/hbtrack/modulos/<module>/SCREEN_MAP_{{MODULE_NAME_UPPER}}.md
# SOURCE: .contract_driven/templates/modulos/SCREEN_MAP_{{MODULE_NAME_UPPER}}.md
module: "{{MODULE_NAME}}"
system_scope_ref: "../../../_canon/SYSTEM_SCOPE.md"
handball_rules_ref: "../../../_canon/HANDBALL_RULES_DOMAIN.md"
handball_semantic_applicability: {{HANDBALL_SEMANTIC_APPLICABILITY}}
type: "screen-map"
module_scope_ref: "./MODULE_SCOPE_{{MODULE_NAME_UPPER}}.md"
ui_contract_ref: "./UI_CONTRACT_{{MODULE_NAME_UPPER}}.md"
diagram_format: "mermaid"
---
# SCREEN_MAP_{{MODULE_NAME_UPPER}}.md

```mermaid
flowchart TD
  A[{{SCREEN_A}}] --> B[{{SCREEN_B}}]
  B --> C[{{SCREEN_C}}]
```
