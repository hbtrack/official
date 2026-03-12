---
# TEMPLATE: module-doc-template
# DEST: docs/hbtrack/modulos/<module>/INVARIANTS_{{MODULE_NAME_UPPER}}.md
# SOURCE: .contract_driven/templates/modulos/INVARIANTS_{{MODULE_NAME_UPPER}}.md
module: "{{MODULE_NAME}}"
system_scope_ref: "../../../_canon/SYSTEM_SCOPE.md"
handball_rules_ref: "../../../_canon/HANDBALL_RULES_DOMAIN.md"
type: "invariants"
---

# INVARIANTS_{{MODULE_NAME_UPPER}}.md

## Objetivo
Registrar invariantes do módulo `{{MODULE_NAME}}`.

## Definição
Invariantes são condições que devem permanecer verdadeiras independentemente do fluxo, endpoint ou interface.

## Tabela de invariantes
| ID | Invariante | Entidades | Fonte | Como verificar |
|---|---|---|---|---|
{{INVARIANTS_TABLE_ROWS}}

## Regras de uso
1. Nenhum endpoint pode violar invariantes.
2. Nenhuma automação assíncrona pode violar invariantes.
3. Nenhuma UI pode assumir transição que quebre invariantes.
4. Toda violação deve bloquear merge ou exigir exceção formal.

## Relação com outros documentos
- `DOMAIN_RULES_{{MODULE_NAME_UPPER}}.md`
- `STATE_MODEL_{{MODULE_NAME_UPPER}}.md`
- `TEST_MATRIX_{{MODULE_NAME_UPPER}}.md`
