---
module: "exercises"
system_scope_ref: "../../../_canon/SYSTEM_SCOPE.md"
handball_rules_ref: "../../../_canon/HANDBALL_RULES_DOMAIN.md"
handball_semantic_applicability: false
type: "readme"
module_scope_ref: "./MODULE_SCOPE_EXERCISES.md"
domain_rules_ref: "./DOMAIN_RULES_EXERCISES.md"
invariants_ref: "./INVARIANTS_EXERCISES.md"
test_matrix_ref: "./TEST_MATRIX_EXERCISES.md"
permissions_ref: "./PERMISSIONS_EXERCISES.md"
contract_path_ref: "../../../../contracts/openapi/paths/exercises.yaml"
schemas_ref: "../../../../contracts/schemas/exercises/"
---

# exercises

## Objetivo
Documentar o escopo normativo do módulo `exercises` e suas superfícies soberanas.

## Superfícies soberanas (referências)
- HTTP (OpenAPI paths): `contracts/openapi/paths/exercises.yaml`
- Schemas de domínio: `contracts/schemas/exercises/`
- Workflows (Arazzo): `contracts/workflows/exercises/` (quando aplicável)
- Eventos (AsyncAPI): `contracts/asyncapi/` (quando aplicável)

## Source graph estruturado
- Manifesto do módulo: `docs/hbtrack/modulos/exercises/graph/module_manifest.yaml`
- Entidades: `docs/hbtrack/modulos/exercises/graph/entities.yaml`
- Endpoints: `docs/hbtrack/modulos/exercises/graph/endpoints.yaml`
- Erros: `docs/hbtrack/modulos/exercises/graph/errors.yaml`
- Obrigações de teste: `docs/hbtrack/modulos/exercises/graph/test_obligations.yaml`

Este conjunto ativa `exercises` na trilha soberana de source graph. Ele deve permanecer alinhado com `contracts/`, `src/exercises/` e os documentos normativos do módulo.

## Fontes globais vinculantes
- `docs/_canon/SYSTEM_SCOPE.md`
- `docs/_canon/HANDBALL_RULES_DOMAIN.md` (quando o gatilho de handebol aplicar)
- SSOT de convenções/templates de API HTTP: `.contract_driven/templates/api/api_rules.yaml`
