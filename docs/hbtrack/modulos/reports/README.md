---
module: "reports"
system_scope_ref: "../../../_canon/SYSTEM_SCOPE.md"
handball_rules_ref: "../../../_canon/HANDBALL_RULES_DOMAIN.md"
handball_semantic_applicability: false
type: "readme"
module_scope_ref: "./MODULE_SCOPE_REPORTS.md"
domain_rules_ref: "./DOMAIN_RULES_REPORTS.md"
invariants_ref: "./INVARIANTS_REPORTS.md"
test_matrix_ref: "./TEST_MATRIX_REPORTS.md"
contract_path_ref: "../../../../contracts/openapi/paths/reports.yaml"
schemas_ref: "../../../../contracts/schemas/reports/"
---

# reports

## Objetivo
Documentar o escopo normativo do módulo `reports` e suas superfícies soberanas.

## Superfícies soberanas (referências)
- HTTP (OpenAPI paths): `contracts/openapi/paths/reports.yaml`
- Schemas de domínio: `contracts/schemas/reports/`
- Workflows (Arazzo): `contracts/workflows/reports/` (quando aplicável)
- Eventos (AsyncAPI): `contracts/asyncapi/` (quando aplicável)

## Source graph estruturado
- Manifesto do módulo: `docs/hbtrack/modulos/reports/graph/module_manifest.yaml`
- Entidades: `docs/hbtrack/modulos/reports/graph/entity_graph.yaml`
- Endpoints: `docs/hbtrack/modulos/reports/graph/endpoints.yaml`
- Erros: `docs/hbtrack/modulos/reports/graph/errors.yaml`
- Obrigações de teste: `docs/hbtrack/modulos/reports/graph/test_obligations.yaml`

Este conjunto é o IR estruturado piloto do módulo `reports`. Até o compiler entrar, ele deve permanecer alinhado com `contracts/`, `src/reports/` e os documentos normativos do módulo.

## Fontes globais vinculantes
- `docs/_canon/SYSTEM_SCOPE.md`
- `docs/_canon/HANDBALL_RULES_DOMAIN.md` (quando o gatilho de handebol aplicar)
- SSOT de convenções/templates de API HTTP: `.contract_driven/templates/api/api_rules.yaml`
