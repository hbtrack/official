---
module: "identity_access"
system_scope_ref: "../../../_canon/SYSTEM_SCOPE.md"
handball_rules_ref: "../../../_canon/HANDBALL_RULES_DOMAIN.md"
handball_semantic_applicability: false
type: "permissions"
adr_refs:
  - "ADR-008: authz-strategy (RBAC flat, 5 roles)"
  - "ADR-007: auth-strategy (JWT Bearer RS256)"
domain_rules_ref: "./DOMAIN_RULES_IDENTITY_ACCESS.md"
invariants_ref: "./INVARIANTS_IDENTITY_ACCESS.md"
---

# PERMISSIONS_IDENTITY_ACCESS.md

> **Nota canônica:** Este módulo É a fonte soberana de autenticação e autorização (ADR-007, ADR-008).
> Os roles canônicos do sistema são: `admin`, `coordinator`, `coach`, `athlete`, `member`.
> Enforcement: BFLA verificado por operação server-side.

---

## Tabela de Permissões por Operação

| Operação (operationId) | admin | coordinator | coach | athlete | member | Observação |
|---|---|---|---|---|---|---|
| `authLogin` | ✅ | ✅ | ✅ | ✅ | ✅ | Público — sem autenticação prévia (security: []) |
| `authForgotPassword` | ✅ | ✅ | ✅ | ✅ | ✅ | Público — inicia reset sem enumerar conta |
| `authResetPassword` | ✅ | ✅ | ✅ | ✅ | ✅ | Público — valida token de reset recebido |
| `authNewPassword` | ✅ | ✅ | ✅ | ✅ | ✅ | Público — define nova senha a partir do token |
| `authConfirmReset` | ✅ | ✅ | ✅ | ✅ | ✅ | Público — confirma etapa final do reset |
| `authLogout` | ✅ | ✅ | ✅ | ✅ | ✅ | Qualquer usuário autenticado encerra sua própria sessão |
| `authRefreshToken` | ✅ | ✅ | ✅ | ✅ | ✅ | Qualquer usuário com refresh token válido |
| `authGetCurrentSession` | ✅ | ✅ | ✅ | ✅ | ✅ | BOLA: cada usuário acessa apenas sua sessão ativa |
| `listActiveSessions` | ✅ | ❌ | ❌ | ❌ | ❌ | Apenas admin pode listar sessões de outros usuários |
| `revokeSession` | ✅ | ❌ | ❌ | ❌ | ❌ | Apenas admin pode revogar sessões alheias |
| `listUserRoles` | ✅ | ✅ | ❌ | ❌ | ❌ | admin e coordinator podem consultar roles de usuários |
| `assignRole` | ✅ | ❌ | ❌ | ❌ | ❌ | Apenas admin — DR-IAM-003 |
| `revokeRole` | ✅ | ❌ | ❌ | ❌ | ❌ | Apenas admin — DR-IAM-003 |
