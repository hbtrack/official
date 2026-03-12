---
# TEMPLATE: module-doc-template
# DEST: docs/hbtrack/modulos/<module>/README.md
# SOURCE: .contract_driven/templates/modulos/README.md
module: "{{MODULE_NAME}}"
system_scope_ref: "../../../_canon/SYSTEM_SCOPE.md"
handball_rules_ref: "../../../_canon/HANDBALL_RULES_DOMAIN.md"
module_scope_ref: "./MODULE_SCOPE_{{MODULE_NAME_UPPER}}.md"
domain_rules_ref: "./DOMAIN_RULES_{{MODULE_NAME_UPPER}}.md"
invariants_ref: "./INVARIANTS_{{MODULE_NAME_UPPER}}.md"
# Condicional - somente quando módulo tem lifecycle (RULES 11.1)
# state_model_ref: "./STATE_MODEL_{{MODULE_NAME_UPPER}}.md"
test_matrix_ref: "./TEST_MATRIX_{{MODULE_NAME_UPPER}}.md"
openapi_ref: "../../../../contracts/openapi/paths/{{MODULE_NAME}}.yaml"
schemas_ref: "../../../../contracts/schemas/{{MODULE_NAME}}/"
---

# {{MODULE_NAME}}

## Objetivo
{{MODULE_NAME}} é o módulo responsável por `{{MODULE_PURPOSE}}`.

## Responsabilidades
{{RESPONSIBILITIES_MD_LIST}}

## Fora do escopo
{{OUT_OF_SCOPE_MD_LIST}}

## Artefatos do módulo
- `MODULE_SCOPE_{{MODULE_NAME_UPPER}}.md`
- `DOMAIN_RULES_{{MODULE_NAME_UPPER}}.md`
- `INVARIANTS_{{MODULE_NAME_UPPER}}.md`
- `TEST_MATRIX_{{MODULE_NAME_UPPER}}.md`
- `contracts/openapi/paths/{{MODULE_NAME}}.yaml`
- `contracts/schemas/{{MODULE_NAME}}/*.schema.json`

### Artefatos condicionais (quando aplicável)
<!-- STATE_MODEL só quando módulo tem lifecycle: ver RULES seção 11.1 -->
- `STATE_MODEL_{{MODULE_NAME_UPPER}}.md` (quando houver lifecycle/estados)

## Dependências
- Sistema: `SYSTEM_SCOPE.md`
- Domínio esportivo: `HANDBALL_RULES_DOMAIN.md`
- Contrato HTTP: `contracts/openapi/paths/{{MODULE_NAME}}.yaml`
- Schemas: `contracts/schemas/{{MODULE_NAME}}/`

## Regras
1. Nenhuma interface pública do módulo existe fora do contrato OpenAPI.
2. Nenhuma entidade pública estável do módulo existe fora de schema.
3. Toda regra derivada do handebol deve apontar para `HANDBALL_RULES_DOMAIN.md`.
4. Se houver lifecycle, toda transição relevante deve estar em `STATE_MODEL_{{MODULE_NAME_UPPER}}.md` (ver RULES seção 11.1).

## Navegação rápida
1. Leia `MODULE_SCOPE_{{MODULE_NAME_UPPER}}.md`
2. Leia `DOMAIN_RULES_{{MODULE_NAME_UPPER}}.md`
3. Leia `INVARIANTS_{{MODULE_NAME_UPPER}}.md`
4. Se houver lifecycle: leia `STATE_MODEL_{{MODULE_NAME_UPPER}}.md`
5. Leia `TEST_MATRIX_{{MODULE_NAME_UPPER}}.md`
6. Leia os contratos do módulo
