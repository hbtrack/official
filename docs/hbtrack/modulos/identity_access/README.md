---
module: "identity_access"
system_scope_ref: "../../../_canon/SYSTEM_SCOPE.md"
handball_rules_ref: "../../../_canon/HANDBALL_RULES_DOMAIN.md"
handball_semantic_applicability: false
type: "readme"
module_scope_ref: "./MODULE_SCOPE_IDENTITY_ACCESS.md"
domain_rules_ref: "./DOMAIN_RULES_IDENTITY_ACCESS.md"
invariants_ref: "./INVARIANTS_IDENTITY_ACCESS.md"
test_matrix_ref: "./TEST_MATRIX_IDENTITY_ACCESS.md"
contract_path_ref: "../../../../contracts/openapi/paths/identity_access.yaml"
schemas_ref: "../../../../contracts/schemas/identity_access/"
---

# identity_access

## Objetivo
Documentar o escopo normativo do módulo `identity_access` e suas superfícies soberanas.

## Superfícies soberanas (referências)
- HTTP (OpenAPI paths): `contracts/openapi/paths/identity_access.yaml`
- Schemas de domínio: `contracts/schemas/identity_access/`
- Workflows (Arazzo): `contracts/workflows/identity_access/` (quando aplicável)
- Eventos (AsyncAPI): `contracts/asyncapi/` (quando aplicável)

## Source graph estruturado
- Manifesto do módulo: `docs/hbtrack/modulos/identity_access/graph/module_manifest.yaml`
- Entidades: `docs/hbtrack/modulos/identity_access/graph/entity_graph.yaml`
- Endpoints: `docs/hbtrack/modulos/identity_access/graph/endpoints.yaml`
- Erros: `docs/hbtrack/modulos/identity_access/graph/errors.yaml`
- Obrigações de teste: `docs/hbtrack/modulos/identity_access/graph/test_obligations.yaml`

Este conjunto ativa `identity_access` na trilha soberana de source graph. Ele deve permanecer alinhado com `contracts/`, `src/identity_access/` e os documentos normativos do módulo.

## Fontes globais vinculantes
- `docs/_canon/SYSTEM_SCOPE.md`
- `docs/_canon/HANDBALL_RULES_DOMAIN.md` (quando o gatilho de handebol aplicar)
- SSOT de convenções/templates de API HTTP: `.contract_driven/templates/api/api_rules.yaml`
