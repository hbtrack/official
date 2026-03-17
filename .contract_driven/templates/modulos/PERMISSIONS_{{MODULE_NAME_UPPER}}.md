---
# TEMPLATE: module-doc-template
# DEST: docs/hbtrack/modulos/<module>/PERMISSIONS_{{MODULE_NAME_UPPER}}.md
# SOURCE: .contract_driven/templates/modulos/PERMISSIONS_{{MODULE_NAME_UPPER}}.md
module: "{{MODULE_NAME}}"
system_scope_ref: "../../../_canon/SYSTEM_SCOPE.md"
handball_rules_ref: "../../../_canon/HANDBALL_RULES_DOMAIN.md"
handball_semantic_applicability: {{HANDBALL_SEMANTIC_APPLICABILITY}}
type: "permissions"
domain_rules_ref: "./DOMAIN_RULES_{{MODULE_NAME_UPPER}}.md"
invariants_ref: "./INVARIANTS_{{MODULE_NAME_UPPER}}.md"
---
# PERMISSIONS_{{MODULE_NAME_UPPER}}.md

| Ação | Papel | Permitido | Observação |
|---|---|---|---|
| {{ACTION}} | {{ROLE}} | {{YES_NO}} | {{NOTE}} |
