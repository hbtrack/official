---
# TEMPLATE: module-doc-template
# DEST: docs/hbtrack/modulos/<module>/MODULE_SCOPE_{{MODULE_NAME_UPPER}}.md
# SOURCE: .contract_driven/templates/modulos/MODULE_SCOPE_{{MODULE_NAME_UPPER}}.md
module: "{{MODULE_NAME}}"
system_scope_ref: "../../../_canon/SYSTEM_SCOPE.md"
handball_rules_ref: "../../../_canon/HANDBALL_RULES_DOMAIN.md"
type: "module-scope"
---

# MODULE_SCOPE_{{MODULE_NAME_UPPER}}.md

## Objetivo
Definir claramente o que o módulo `{{MODULE_NAME}}` faz e o que não faz.

## Missão do módulo
{{MODULE_NAME}} existe para `{{MODULE_MISSION}}`.

## Responsabilidades
{{RESPONSIBILITIES_MD_LIST}}

## Atores
{{ACTORS_MD_LIST}}

## Entidades principais
{{DOMAIN_ENTITIES_MD_LIST}}

## Entradas
- Requests HTTP definidos em `contracts/openapi/paths/{{MODULE_NAME}}.yaml`
- Dados persistidos/consultados definidos em schemas
- Eventos, quando aplicável

## Saídas
- Responses HTTP
- Mudanças de estado do domínio
- Eventos, quando aplicável
- Dados derivados consumidos por outros módulos, quando aplicável

## Dentro do escopo
{{IN_SCOPE_MD_LIST}}

## Fora do escopo
{{OUT_OF_SCOPE_MD_LIST}}

## Dependências
- Módulos upstream: {{UPSTREAM_MODULES}}
- Módulos downstream: {{DOWNSTREAM_MODULES}}
- Artefatos globais:
  - `SYSTEM_SCOPE.md`
  - `HANDBALL_RULES_DOMAIN.md`

## Regras de fronteira
1. O módulo não deve assumir responsabilidades de outro módulo sem decisão explícita.
2. O módulo não deve expor comportamento fora do seu contrato.
3. Toda exceção de escopo deve ser registrada formalmente.
