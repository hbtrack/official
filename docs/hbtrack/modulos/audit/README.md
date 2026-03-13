---
module: "audit"
system_scope_ref: "../../../_canon/SYSTEM_SCOPE.md"
handball_rules_ref: "../../../_canon/HANDBALL_RULES_DOMAIN.md"
handball_semantic_applicability: false
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
