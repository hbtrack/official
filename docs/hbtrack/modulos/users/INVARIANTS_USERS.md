---
module: "users"
system_scope_ref: "../../../_canon/SYSTEM_SCOPE.md"
handball_rules_ref: "../../../_canon/HANDBALL_RULES_DOMAIN.md"
handball_semantic_applicability: false
contract_path_ref: "../../../../contracts/openapi/paths/users.yaml"
schemas_ref: "../../../../contracts/schemas/users/"
type: "invariants"
updated: "2026-03-16"
---

# INVARIANTS_USERS.md

## Objetivo
Registrar invariantes do módulo `users`.

## Definição
Invariantes são condições que devem permanecer verdadeiras independentemente do fluxo, endpoint ou interface.

## Invariantes globais vinculantes
- `.contract_driven/DOMAIN_AXIOMS.json`
- `docs/_canon/GLOBAL_INVARIANTS.md`

## Tabela de invariantes
| ID | Invariante | Entidades | Fonte | Como verificar |
|---|---|---|---|---|
| INV-USR-001 | `id`, `displayName` e `roleLabel` são obrigatórios em todo `UserProfile` estável. | `UserProfile` | `user_profile.schema.json` | JSON Schema validation |
| INV-USR-002 | `teamIds`, `seasonIds` e `preferenceTags` são conjuntos sem duplicidade. | `UserProfile` | Schema local | `uniqueItems` + testes de contrato |
| INV-USR-003 | O módulo `users` não pode expor `password_hash`, `refresh_token`, `mfa_secret`, `jwt`, `access_token` ou artefatos equivalentes de autenticação. | `UserProfile` | `BOUNDARY_USERS_IDENTITY_ACCESS_GATE` | Gate de boundary + revisão contratual |
| INV-USR-004 | Atributos esportivos e de perfil pessoal pertencem a `users`; artefatos técnicos de authn/authz pertencem a `identity_access`. Nenhuma interface pública pode colapsar essa fronteira. | `UserProfile`, `AuthSession` | Authority matrix P-004 | Cross-spec alignment + gate de boundary |
| INV-USR-005 | `avatarUrl`, quando presente, deve ser apenas URL processada de exibição e não pode carregar credencial, segredo ou estado de authn/authz. | `UserProfile` | `user_profile.schema.json` + ADR-021 | Schema validation + revisão de boundary |

## Relação com outros documentos
- `docs/hbtrack/modulos/users/DOMAIN_RULES_USERS.md`
- `contracts/schemas/users/user_profile.schema.json`
