---
module: "ai_ingestion"
system_scope_ref: "../../../_canon/SYSTEM_SCOPE.md"
handball_rules_ref: "../../../_canon/HANDBALL_RULES_DOMAIN.md"
handball_semantic_applicability: false
contract_path_ref: "../../../../contracts/openapi/paths/ai_ingestion.yaml"
schemas_ref: "../../../../contracts/schemas/ai_ingestion/"
---

# ai_ingestion

## Objetivo
Documentar o escopo normativo do módulo `ai_ingestion` e suas superfícies soberanas.

## Superfícies soberanas (referências)
- HTTP (OpenAPI paths): `contracts/openapi/paths/ai_ingestion.yaml`
- Schemas de domínio: `contracts/schemas/ai_ingestion/`
- Workflows (Arazzo): `contracts/workflows/ai_ingestion/` (quando aplicável)
- Eventos (AsyncAPI): `contracts/asyncapi/` (quando aplicável)

## Fontes globais vinculantes
- `docs/_canon/SYSTEM_SCOPE.md`
- `docs/_canon/HANDBALL_RULES_DOMAIN.md` (quando o gatilho de handebol aplicar)
- SSOT de convenções/templates de API HTTP: `.contract_driven/templates/API_RULES/API_RULES.yaml`
