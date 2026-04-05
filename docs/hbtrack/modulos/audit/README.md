---
module: "audit"
system_scope_ref: "../../../_canon/SYSTEM_SCOPE.md"
handball_rules_ref: "../../../_canon/HANDBALL_RULES_DOMAIN.md"
handball_semantic_applicability: false
type: "readme"
module_scope_ref: "./MODULE_SCOPE_AUDIT.md"
domain_rules_ref: "./DOMAIN_RULES_AUDIT.md"
invariants_ref: "./INVARIANTS_AUDIT.md"
test_matrix_ref: "./TEST_MATRIX_AUDIT.md"
contract_path_ref: "../../../../contracts/openapi/paths/audit.yaml"
schemas_ref: "../../../../contracts/schemas/audit/"
---

# audit

## Objetivo
Documentar o escopo normativo do módulo `audit` e suas superfícies soberanas.

## Superfícies soberanas (referências)
- HTTP (OpenAPI paths): `contracts/openapi/paths/audit.yaml`
- Schemas de domínio: `contracts/schemas/audit/`
- Workflows (Arazzo): `contracts/workflows/audit/` (quando aplicável)
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
