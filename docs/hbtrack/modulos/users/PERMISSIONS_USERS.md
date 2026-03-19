---
module: "users"
system_scope_ref: "../../../_canon/SYSTEM_SCOPE.md"
handball_rules_ref: "../../../_canon/HANDBALL_RULES_DOMAIN.md"
handball_semantic_applicability: false
type: "permissions"
adr_refs:
  - "ADR-008: authz-strategy (RBAC flat, 5 roles)"
  - "ADR-007: auth-strategy (JWT Bearer)"
domain_rules_ref: "./DOMAIN_RULES_USERS.md"
invariants_ref: "./INVARIANTS_USERS.md"
decisions_ref: "../../../.contract_driven/decisions/DECISION_IR_USERS.yaml"
updated_at: "2026-03-19"
---

# PERMISSIONS_USERS.md

> **Nota canônica:** O módulo `identity_access` é a fonte soberana de autorização.
> Este artefato **documenta** como `users` aplica a policy — não a redefine.
> Roles canônicos: `admin`, `coordinator`, `coach`, `athlete`, `member` (ADR-008).
> Enforcement por operação, via guards no Router (BFLA) e Service (BOLA, BOPLA).
>
> **Boundary crítico:** `roleLabel` em `UserProfile` é **informativo** — representa
> o papel funcional/esportivo do usuário nos registros. A autorização técnica real
> (RBAC enforcement) é responsabilidade de `identity_access` via JWT `roles` claim
> (ADR-008, INV-USR-004). Alterações de `roleLabel` geram evento `user.role_changed`
> para rastreamento por `audit` (DEC-USERS-001).

---

## Tabela de Permissões por Operação

| Operação (operationId) | admin | coordinator | coach | athlete | member | Observação |
|---|---|---|---|---|---|---|
| `listUsers` | ✅ | ✅ | ✅ | ✅ | ❌ | Todos autenticados com role operacional; `member` (espectador) não lista usuários. Resultado filtrado por organizationId do JWT |
| `createUser` | ✅ | ✅ | ❌ | ❌ | ❌ | Admin e coordinator criam perfis (BFLA). Perfil criado com `statusLabel = pending_activation` no fluxo de convite (DEC-USERS-002) |
| `getUser` | ✅ | ✅ | ✅ (membros do seu time) | ✅ (próprio perfil) | ❌ | BOLA: owner sempre pode; coach vê membros do seu time; member não tem acesso |
| `patchUser` (próprio perfil) | ✅ | ✅ | ✅ | ✅ | ❌ | Owner pode editar seu próprio perfil (exceto roleLabel — ver abaixo) |
| `patchUser` (outro perfil) | ✅ | ✅ | ❌ | ❌ | ❌ | Admin e coordinator editam outros perfis |
| `patchUser.roleLabel` | ✅ | ✅ | ❌ | ❌ | ❌ | **Apenas admin e coordinator** alteram roleLabel (DEC-USERS-003). Gera evento `user.role_changed` |
| `patchUser.statusLabel` | ✅ (qualquer) | ✅ (active/pending) | ❌ | ✅ (próprio → active) | ❌ | Dono ativa seu próprio perfil (`pending_activation` → `active`). Admin/coordinator podem suspender (`suspended`) |

---

## Regras de contexto cross-operação

| ID | Regra | Ref |
|---|---|---|
| PERM-USR-001 | Roles são atribuídos em `identity_access`; `users` não altera atribuição de JWT roles | ADR-008 |
| PERM-USR-002 | Apenas `admin` e `coordinator` criam perfis de usuário (POST /users) | DEC-USERS-003, OWASP API5:2023 (BFLA) |
| PERM-USR-003 | BOLA: owner (`userId = token.sub`) sempre pode ler e editar seu próprio perfil | ADR-007, OWASP API1:2023 (BOLA) |
| PERM-USR-004 | `roleLabel` só pode ser alterado por `admin` ou `coordinator`; owner não pode promover/rebaixar seu próprio roleLabel | DEC-USERS-003, ADR-008 |
| PERM-USR-005 | `member` (espectador/familiar) não tem acesso a leitura ou criação de perfis de outros usuários | ADR-008, DR-USR-002 |
| PERM-USR-006 | Coach vê perfis de membros do seu time (GET /users?teamId=); não vê perfis de outras equipes | DR-USR-003, OWASP API1:2023 (BOLA) |
| PERM-USR-007 | BOPLA: allowlist de campos editáveis em PATCH — `firstName`, `lastName`, `displayName`, `positionLabel`, `preferredLanguage`, `preferenceTags`, `teamIds`, `seasonIds`; campos de authn proibidos (INV-USR-003) | OWASP API3:2023 (BOPLA), INV-USR-003 |
| PERM-USR-008 | `teamIds` e `seasonIds` = vínculos explícitos; nenhum role pode inferir vínculos a partir de presença, analytics ou sessão | DR-USR-003, INV-USR-002 |
| PERM-USR-009 | Alteração de `roleLabel` publica evento `user.role_changed` para audit trail (DEC-USERS-001) | DEC-USERS-001, DEC-USERS-003 |
| PERM-USR-010 | Payload de qualquer operação NUNCA inclui `password_hash`, `refresh_token`, `mfa_secret`, `jwt`, `access_token` | INV-USR-003, OWASP API8:2023 |
