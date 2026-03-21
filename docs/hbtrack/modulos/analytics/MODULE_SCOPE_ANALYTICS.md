---
module: "analytics"
system_scope_ref: "../../../_canon/SYSTEM_SCOPE.md"
handball_rules_ref: "../../../_canon/HANDBALL_RULES_DOMAIN.md"
handball_semantic_applicability: false
contract_path_ref: "../../../../contracts/openapi/paths/analytics.yaml"
schemas_ref: "../../../../contracts/schemas/analytics/"
---

# MODULE_SCOPE_ANALYTICS.md

## Responsabilidades
- Expor apenas métricas derivadas e sinais soberanos de `analytics`.
- Definir query, filtros estruturados, janelas temporais, granularidade, projeções e refresh sem reescrever o dado-fonte.
- Publicar apenas superfícies contratuais com catálogo fechado de métricas e sem DSL textual implícita.

## Fora do escopo
- Cálculo, escrita ou correção do dado-fonte bruto de módulos soberanos.
- KPI, filtro, projeção ou dimensão ad hoc sem canonização prévia.
- Query livre baseada em string (`filterExpression`) ou resposta com colunas abertas por métrica.

## Dependências e integrações
- `training` e `wellness` fornecem parte do dado-fonte consumido pelos sinais derivados canônicos atuais.
- `identity_access` permanece soberano de autenticação e autorização; `analytics` apenas aplica a policy por operação.
