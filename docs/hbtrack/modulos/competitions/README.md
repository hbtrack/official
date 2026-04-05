---
module: "competitions"
system_scope_ref: "../../../_canon/SYSTEM_SCOPE.md"
handball_rules_ref: "../../../_canon/HANDBALL_RULES_DOMAIN.md"
handball_semantic_applicability: true
type: "readme"
module_scope_ref: "./MODULE_SCOPE_COMPETITIONS.md"
domain_rules_ref: "./DOMAIN_RULES_COMPETITIONS.md"
invariants_ref: "./INVARIANTS_COMPETITIONS.md"
test_matrix_ref: "./TEST_MATRIX_COMPETITIONS.md"
contract_path_ref: "../../../../contracts/openapi/paths/competitions.yaml"
schemas_ref: "../../../../contracts/schemas/competitions/"
---

# competitions

## Objetivo
Documentar o escopo normativo do módulo `competitions` e suas superfícies soberanas.

## Superfícies soberanas (referências)
- HTTP (OpenAPI paths): `contracts/openapi/paths/competitions.yaml`
- Schemas de domínio: `contracts/schemas/competitions/`
- Workflows (Arazzo): `contracts/workflows/competitions/` (quando aplicável)
- Eventos (AsyncAPI): `contracts/asyncapi/` (quando aplicável)

## Fontes globais vinculantes
- `docs/_canon/SYSTEM_SCOPE.md`
- `docs/_canon/HANDBALL_RULES_DOMAIN.md` (quando o gatilho de handebol aplicar)
- SSOT de convenções/templates de API HTTP: `.contract_driven/templates/api/api_rules.yaml`

## Source Graph
- [graph/module_manifest.yaml](graph/module_manifest.yaml)
- [graph/entity_graph.yaml](graph/entity_graph.yaml)
- [graph/endpoints.yaml](graph/endpoints.yaml)
- [graph/errors.yaml](graph/errors.yaml)
- [graph/test_obligations.yaml](graph/test_obligations.yaml)
