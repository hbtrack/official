---
module: "notifications"
system_scope_ref: "../../../_canon/SYSTEM_SCOPE.md"
handball_rules_ref: "../../../_canon/HANDBALL_RULES_DOMAIN.md"
handball_semantic_applicability: false
type: "readme"
module_scope_ref: "./MODULE_SCOPE_NOTIFICATIONS.md"
domain_rules_ref: "./DOMAIN_RULES_NOTIFICATIONS.md"
invariants_ref: "./INVARIANTS_NOTIFICATIONS.md"
test_matrix_ref: "./TEST_MATRIX_NOTIFICATIONS.md"
permissions_ref: "./PERMISSIONS_NOTIFICATIONS.md"
contract_path_ref: "../../../../contracts/openapi/paths/notifications.yaml"
schemas_ref: "../../../../contracts/schemas/notifications/"
---

# notifications

## Objetivo
Documentar o escopo normativo do módulo `notifications` e suas superfícies soberanas.

## Superfícies soberanas (referências)
- HTTP (OpenAPI paths): `contracts/openapi/paths/notifications.yaml`
- Schemas de domínio: `contracts/schemas/notifications/`
- Workflows (Arazzo): `contracts/workflows/notifications/` (quando aplicável)
- Eventos (AsyncAPI): `contracts/asyncapi/` (quando aplicável)

## Source graph estruturado
- Manifesto do módulo: `docs/hbtrack/modulos/notifications/graph/module_manifest.yaml`
- Entidades: `docs/hbtrack/modulos/notifications/graph/entities.yaml`
- Endpoints: `docs/hbtrack/modulos/notifications/graph/endpoints.yaml`
- Erros: `docs/hbtrack/modulos/notifications/graph/errors.yaml`
- Obrigações de teste: `docs/hbtrack/modulos/notifications/graph/test_obligations.yaml`

Este conjunto ativa `notifications` na trilha soberana de source graph. Ele deve permanecer alinhado com `contracts/`, `src/notifications/` e os documentos normativos do módulo.

## Fontes globais vinculantes
- `docs/_canon/SYSTEM_SCOPE.md`
- `docs/_canon/HANDBALL_RULES_DOMAIN.md` (quando o gatilho de handebol aplicar)
- SSOT de convenções/templates de API HTTP: `.contract_driven/templates/api/api_rules.yaml`
