<!-- TEMPLATE: global-canon-template | DEST: docs/_canon/ERROR_MODEL.md | SOURCE: .contract_driven/templates/globais/ERROR_MODEL.md -->

# ERROR_MODEL.md

## Objetivo
Padronizar respostas de erro HTTP usando Problem Details for HTTP APIs.

## Media Type
- `application/problem+json`

## Campos Base
- `type`
- `title`
- `status`
- `detail`
- `instance`

## Extensões Permitidas
- `code`
- `traceId`
- `errors`
- `context`
- `timestamp`

## Exemplo Base
```json
{
  "type": "https://{{PROJECT_DOMAIN}}/problems/validation-error",
  "title": "Validation error",
  "status": 400,
  "detail": "One or more fields are invalid.",
  "instance": "/api/{{RESOURCE_PATH}}",
  "code": "VALIDATION_ERROR",
  "traceId": "{{TRACE_ID}}",
  "errors": [
    {
      "field": "{{FIELD_NAME}}",
      "message": "{{ERROR_MESSAGE}}"
    }
  ]
}
```

## Regras
1. `type` deve ser estável e documentável.
2. `title` deve ser curto e humano-legível.
3. `status` deve refletir o HTTP status real.
4. `detail` deve explicar a falha sem ambiguidade.
5. Campos extras devem ser consistentes em todo o sistema.

## Mapeamento Inicial
| HTTP Status | code | type |
|---|---|---|
| 400 | VALIDATION_ERROR | https://{{PROJECT_DOMAIN}}/problems/validation-error |
| 401 | UNAUTHORIZED | https://{{PROJECT_DOMAIN}}/problems/unauthorized |
| 403 | FORBIDDEN | https://{{PROJECT_DOMAIN}}/problems/forbidden |
| 404 | NOT_FOUND | https://{{PROJECT_DOMAIN}}/problems/not-found |
| 409 | CONFLICT | https://{{PROJECT_DOMAIN}}/problems/conflict |
| 422 | BUSINESS_RULE_VIOLATION | https://{{PROJECT_DOMAIN}}/problems/business-rule-violation |
| 500 | INTERNAL_ERROR | https://{{PROJECT_DOMAIN}}/problems/internal-error |
