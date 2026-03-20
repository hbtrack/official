---
module: "notifications"
system_scope_ref: "../../../_canon/SYSTEM_SCOPE.md"
handball_rules_ref: "../../../_canon/HANDBALL_RULES_DOMAIN.md"
handball_semantic_applicability: false
type: "permissions"
adr_refs:
  - "ADR-008: authz-strategy (RBAC flat, 5 roles)"
  - "ADR-007: auth-strategy (JWT Bearer)"
domain_rules_ref: "./DOMAIN_RULES_NOTIFICATIONS.md"
invariants_ref: "./INVARIANTS_NOTIFICATIONS.md"
updated_at: "2026-03-19"
---

# PERMISSIONS_NOTIFICATIONS.md

> **Nota canônica:** O módulo `identity_access` é a fonte soberana de autorização.
> Este artefato **documenta** como `notifications` aplica a policy — não a redefine.
> Roles canônicos: `admin`, `coordinator`, `coach`, `athlete`, `member` (ADR-008).
> Enforcement por operação, via guards no Router (BFLA) e Service (BOLA, BOPLA).

---

## Tabela de Permissões por Operação

| Operação (operationId) | admin | coordinator | coach | athlete | member | Observação |
|---|---|---|---|---|---|---|
| `createNotificationIntent` | ✅ | ✅ | ✅ | ❌ | ❌ | Envio de notificação por staff; athlete não pode iniciar notificações para outros |
| `listDeliveries` | ✅ | ✅ | ✅ (próprias) | ✅ (próprias) | ❌ | BOLA: cada usuário vê apenas suas próprias entregas |
| `getDelivery` | ✅ | ✅ | ✅ (própria) | ✅ (própria) | ❌ | BOLA por delivery — acesso somente ao destinatário |
| `getUserNotificationPreferences` | ✅ | ✅ | ✅ (próprias) | ✅ (próprias) | ❌ | Preferências são dados pessoais — somente o próprio usuário e gestores |
| `updateUserNotificationPreferences` | ✅ | ✅ | ✅ (próprias) | ✅ (próprias) | ❌ | Usuário controla suas próprias preferências de notificação |

---

## Regras de contexto cross-operação

| ID | Regra | Ref |
|---|---|---|
| PERM-NOT-001 | Athlete não pode criar intents de notificação para outros usuários (anti-spam) | ADR-008, DOMAIN_RULES_NOTIFICATIONS |
| PERM-NOT-002 | Preferências de notificação são dados pessoais; só o próprio usuário ou admin pode alterar | ADR-010 |
| PERM-NOT-003 | Admin pode visualizar entregas de qualquer usuário para auditoria; deve ser logado | DOMAIN_RULES_NOTIFICATIONS |
