---
# TEMPLATE: module-doc-template
# DEST: docs/hbtrack/modulos/<module>/ERRORS_{{MODULE_NAME_UPPER}}.md
# SOURCE: .contract_driven/templates/modulos/ERRORS_{{MODULE_NAME_UPPER}}.md
module: "{{MODULE_NAME}}"
system_scope_ref: "../../../_canon/SYSTEM_SCOPE.md"
handball_rules_ref: "../../../_canon/HANDBALL_RULES_DOMAIN.md"
handball_semantic_applicability: {{HANDBALL_SEMANTIC_APPLICABILITY}}
type: "errors"
error_model_ref: "../../../../docs/_canon/ERROR_MODEL.md"
problem_schema_ref: "../../../../contracts/openapi/components/schemas/shared/problem.yaml"
---
# ERRORS_{{MODULE_NAME_UPPER}}.md

| Código | Situação | HTTP | Observação |
|---|---|---|---|
| {{ERROR_CODE}} | {{ERROR_CASE}} | {{HTTP_STATUS}} | {{NOTE}} |
