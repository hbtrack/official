---
module: "scout"
system_scope_ref: "../../../_canon/SYSTEM_SCOPE.md"
handball_rules_ref: "../../../_canon/HANDBALL_RULES_DOMAIN.md"
handball_semantic_applicability: true
type: "readme"
module_scope_ref: "./MODULE_SCOPE_SCOUT.md"
domain_rules_ref: "./DOMAIN_RULES_SCOUT.md"
invariants_ref: "./INVARIANTS_SCOUT.md"
test_matrix_ref: "./TEST_MATRIX_SCOUT.md"
contract_path_ref: "../../../../contracts/openapi/paths/scout.yaml"
schemas_ref: "../../../../contracts/schemas/scout/"
---

# scout

## Objetivo
Documentar o escopo normativo do módulo `scout` e suas superfícies soberanas.

## Superfícies soberanas (referências)
- HTTP (OpenAPI paths): `contracts/openapi/paths/scout.yaml`
- Schemas de domínio: `contracts/schemas/scout/`
- Workflows (Arazzo): `contracts/workflows/scout/` (quando aplicável)
- Eventos (AsyncAPI): `contracts/asyncapi/` (quando aplicável)

## Source graph estruturado
- `graph/module_manifest.yaml` — manifesto soberano do módulo
- `graph/entity_graph.yaml` — entidades e campos soberanos
- `graph/endpoints.yaml` — operações HTTP e use cases
- `graph/errors.yaml` — mapeamento de exceções e códigos HTTP
- `graph/test_obligations.yaml` — obrigações de teste e cobertura

## Fontes globais vinculantes
- `docs/_canon/SYSTEM_SCOPE.md`
- `docs/_canon/HANDBALL_RULES_DOMAIN.md` (quando o gatilho de handebol aplicar)
- SSOT de convenções/templates de API HTTP: `.contract_driven/templates/api/api_rules.yaml`
