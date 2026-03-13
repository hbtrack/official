# OWASP API Security — Referências para HB Track

Este documento contém referências ao OWASP API Security Top 10, aplicáveis ao HB Track.

## Referências

- [OWASP API Security Project](https://owasp.org/www-project-api-security/)
- [OWASP API Security Top 10](https://owasp.org/API-Security/editions/2023/en/0x11-t10/)

## OWASP API Security Top 10 (2023)

### API1:2023 — Broken Object Level Authorization
- **Mitigação HB Track**: validação de ownership em todas as operações de recurso
- Verificar `userId` do token vs. `owner_id` do recurso

### API2:2023 — Broken Authentication
- **Mitigação HB Track**: JWT com expiração curta, refresh token rotation
- Autenticação centralizada via módulo `identity_access`

### API3:2023 — Broken Object Property Level Authorization
- **Mitigação HB Track**: schemas estritos, validação de campos permitidos por role
- Campos sensíveis filtrados por permissões

### API4:2023 — Unrestricted Resource Consumption
- **Mitigação HB Track**: rate limiting, paginação obrigatória, timeouts
- Limites de página: max 100 itens

### API5:2023 — Broken Function Level Authorization
- **Mitigação HB Track**: RBAC granular, verificação de permissões por operação
- Permissions matrix em `PERMISSIONS_{{MODULE}}.md`

### API6:2023 — Unrestricted Access to Sensitive Business Flows
- **Mitigação HB Track**: limitação de operações críticas (ex.: criação de partidas)
- Workflows governados via Arazzo

### API7:2023 — Server Side Request Forgery
- **Mitigação HB Track**: validação de URLs, whitelist de domínios externos
- Sem endpoints que aceitam URL arbitrária

### API8:2023 — Security Misconfiguration
- **Mitigação HB Track**: configuração via variáveis de ambiente, secrets management
 - Headers de segurança obrigatórios: HSTS, CSP, X-Content-Type-Options

### API9:2023 — Improper Inventory Management
- **Mitigação HB Track**: contrato-driven, OpenAPI como SSOT, versionamento explícito
- Endpoints deprecados documentados com sunset date

### API10:2023 — Unsafe Consumption of APIs
- **Mitigação HB Track**: validação de respostas de APIs externas, timeouts
- Schema validation de payloads recebidos

## Controles adicionais

- Input validation em todos os endpoints (via JSON Schema)
- Output encoding automático
- Logging de eventos de segurança
- Audit trail completo (módulo `audit`)

## Alinhamento canônico

Todas as diretrizes OWASP relevantes estão refletidas em:
- `docs/_canon/SECURITY_RULES.md`
- `.contract_driven/templates/api/api_rules.yaml`
- `docs/_canon/ERROR_MODEL.md`
