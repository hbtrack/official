---
module: "analytics"
system_scope_ref: "../../../_canon/SYSTEM_SCOPE.md"
handball_rules_ref: "../../../_canon/HANDBALL_RULES_DOMAIN.md"
handball_semantic_applicability: false
type: "readme"
module_scope_ref: "./MODULE_SCOPE_ANALYTICS.md"
domain_rules_ref: "./DOMAIN_RULES_ANALYTICS.md"
invariants_ref: "./INVARIANTS_ANALYTICS.md"
test_matrix_ref: "./TEST_MATRIX_ANALYTICS.md"
permissions_ref: "./PERMISSIONS_ANALYTICS.md"
errors_ref: "./ERRORS_ANALYTICS.md"
contract_path_ref: "../../../../contracts/openapi/paths/analytics.yaml"
schemas_ref: "../../../../contracts/schemas/analytics/"
---

# analytics

## Objetivo
Documentar o escopo normativo do módulo `analytics` e suas superfícies soberanas.

## Superfícies soberanas (referências)
- HTTP (OpenAPI paths): `contracts/openapi/paths/analytics.yaml`
- Schemas de domínio: `contracts/schemas/analytics/`
- Workflows (Arazzo): `contracts/workflows/analytics/` (quando aplicável)
- Eventos (AsyncAPI): `contracts/asyncapi/` (quando aplicável)

## Source graph estruturado
- Manifesto do módulo: `docs/hbtrack/modulos/analytics/graph/module_manifest.yaml`
- Entidades: `docs/hbtrack/modulos/analytics/graph/entities.yaml`
- Endpoints: `docs/hbtrack/modulos/analytics/graph/endpoints.yaml`
- Erros: `docs/hbtrack/modulos/analytics/graph/errors.yaml`
- Obrigações de teste: `docs/hbtrack/modulos/analytics/graph/test_obligations.yaml`

Este conjunto é a segunda ativação do source graph soberano fora do piloto de `reports`. Ele deve permanecer alinhado com `contracts/`, `src/analytics/` e os documentos normativos do módulo.

## Fontes globais vinculantes
- `docs/_canon/SYSTEM_SCOPE.md`
- `docs/_canon/HANDBALL_RULES_DOMAIN.md` (quando o gatilho de handebol aplicar)
- SSOT de convenções/templates de API HTTP: `.contract_driven/templates/api/api_rules.yaml`
