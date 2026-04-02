---
module: "wellness"
system_scope_ref: "../../../_canon/SYSTEM_SCOPE.md"
handball_rules_ref: "../../../_canon/HANDBALL_RULES_DOMAIN.md"
handball_semantic_applicability: false
type: "readme"
module_scope_ref: "./MODULE_SCOPE_WELLNESS.md"
domain_rules_ref: "./DOMAIN_RULES_WELLNESS.md"
invariants_ref: "./INVARIANTS_WELLNESS.md"
test_matrix_ref: "./TEST_MATRIX_WELLNESS.md"
permissions_ref: "./PERMISSIONS_WELLNESS.md"
contract_path_ref: "../../../../contracts/openapi/paths/wellness.yaml"
schemas_ref: "../../../../contracts/schemas/wellness/"
---

# wellness

## Objetivo
Documentar o escopo normativo do módulo `wellness` e suas superfícies soberanas.

## Superfícies soberanas (referências)
- HTTP (OpenAPI paths): `contracts/openapi/paths/wellness.yaml`
- Schemas de domínio: `contracts/schemas/wellness/`
- Workflows (Arazzo): `contracts/workflows/wellness/` (quando aplicável)
- Eventos (AsyncAPI): `contracts/asyncapi/` (quando aplicável)

## Source graph estruturado
- Manifesto do módulo: `docs/hbtrack/modulos/wellness/graph/module_manifest.yaml`
- Entidades: `docs/hbtrack/modulos/wellness/graph/entities.yaml`
- Endpoints: `docs/hbtrack/modulos/wellness/graph/endpoints.yaml`
- Erros: `docs/hbtrack/modulos/wellness/graph/errors.yaml`
- Obrigações de teste: `docs/hbtrack/modulos/wellness/graph/test_obligations.yaml`

Este conjunto ativa `wellness` na trilha soberana de source graph. Ele deve permanecer alinhado com `contracts/`, `src/wellness/` e os documentos normativos do módulo.

## Fontes globais vinculantes
- `docs/_canon/SYSTEM_SCOPE.md`
- `docs/_canon/HANDBALL_RULES_DOMAIN.md` (quando o gatilho de handebol aplicar)
- SSOT de convenções/templates de API HTTP: `.contract_driven/templates/api/api_rules.yaml`
