---
module: "competitions"
system_scope_ref: "../../../_canon/SYSTEM_SCOPE.md"
handball_rules_ref: "../../../_canon/HANDBALL_RULES_DOMAIN.md"
handball_semantic_applicability: true
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
- SSOT de convenções/templates de API HTTP: `.contract_driven/templates/API_RULES/API_RULES.yaml`
