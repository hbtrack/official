---
# TEMPLATE: module-doc-template
# DEST: docs/hbtrack/modulos/<module>/DOMAIN_RULES_{{MODULE_NAME_UPPER}}.md
# SOURCE: .contract_driven/templates/modulos/DOMAIN_RULES_{{MODULE_NAME_UPPER}}.md
module: "{{MODULE_NAME}}"
system_scope_ref: "../../../_canon/SYSTEM_SCOPE.md"
handball_rules_ref: "../../../_canon/HANDBALL_RULES_DOMAIN.md"
type: "domain-rules"
---

# DOMAIN_RULES_{{MODULE_NAME_UPPER}}.md

## Objetivo
Registrar as regras de negócio do módulo `{{MODULE_NAME}}`.

## Fonte do domínio
- `SYSTEM_SCOPE.md`
- `HANDBALL_RULES_DOMAIN.md` (quando aplicável)
- OpenAPI e schemas do módulo
- decisões arquiteturais e regulatórias pertinentes

## Regras de negócio
| ID | Regra | Entidades afetadas | Fonte | Observações |
|---|---|---|---|---|
{{BUSINESS_RULES_TABLE_ROWS}}

## Regras derivadas da modalidade
| ID | Regra derivada do handebol | Regra de produto | Referência em HANDBALL_RULES_DOMAIN.md |
|---|---|---|---|
{{HANDBALL_DERIVED_RULES_TABLE_ROWS}}

## Prioridade de verdade
1. Regra oficial do esporte, quando aplicável
2. Regra global do sistema
3. Regra do módulo
4. Comportamento da implementação

## Regras proibidas
- Não inferir regra de negócio a partir de UI isolada
- Não inferir regra de negócio a partir de dado histórico sem contrato
- Não inferir comportamento público sem respaldo em documentação do módulo
