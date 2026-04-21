---
module: "identity_access"
system_scope_ref: "../../../_canon/SYSTEM_SCOPE.md"
handball_rules_ref: "../../../_canon/HANDBALL_RULES_DOMAIN.md"
handball_semantic_applicability: false
contract_path_ref: "../../../../contracts/openapi/paths/identity_access.yaml"
schemas_ref: "../../../../contracts/schemas/identity_access/"
type: "domain-rules"
updated: "2026-03-16"
---

# DOMAIN_RULES_IDENTITY_ACCESS.md

## Objetivo
Registrar as regras de negócio do módulo `identity_access`.

## Fonte do domínio
- `docs/_canon/SYSTEM_SCOPE.md`
- `docs/_canon/MODULE_SOURCE_AUTHORITY_MATRIX.yaml`
- `docs/_canon/AUTH_EXPERIENCE_CONTRACT.md`
- `contracts/schemas/identity_access/auth_session.schema.json`
- `docs/hbtrack/modulos/identity_access/INVARIANTS_IDENTITY_ACCESS.md`

## Regras de negócio
| ID | Regra | Entidades afetadas | Fonte | Observações |
|---|---|---|---|---|
| DR-IAM-001 | `identity_access` é soberano de login, logout, sessão, MFA, JWT, refresh e bindings técnicos de autorização. | `AuthSession` | Authority matrix `identity_access` | Fonte única de authn/authz |
| DR-IAM-002 | `principalUserId` liga a sessão ao usuário, mas `identity_access` não é dono do perfil esportivo nem de dados clínicos do usuário. | `AuthSession` | Boundary `users`/`identity_access` | Referência, não duplicação |
| DR-IAM-003 | `sessionScopeLabel`, `authMethodLabel` e `roleLabels` compõem o contexto técnico de autorização e não podem ser deduzidos de atributos esportivos como posição ou categoria. | `AuthSession` | `SYSTEM_SCOPE.md` + authority matrix | Técnica ≠ esporte |
| DR-IAM-004 | `mfaRequired`, `mfaSatisfied`, `issuedAt`, `expiresAt` e `revokedAt` descrevem explicitamente o ciclo de vida da sessão. | `AuthSession` | Schema local | Estado de sessão rastreável |
| DR-IAM-005 | Consentimentos, refresh e revogação devem ser governados aqui, nunca em `users`, `teams` ou módulos operacionais. | `AuthSession` | Authority matrix `must_not_infer` | Boundary obrigatório |
| DR-IAM-006 | Solicitação, validação, troca de senha e confirmação final do fluxo de recuperação pertencem exclusivamente a `identity_access`, incluindo política de token, não enumeração de contas e expiração. | `PasswordResetFlow` | `AUTH_EXPERIENCE_CONTRACT.md` | Boundary obrigatório |
| DR-IAM-007 | O link de recuperação enviado ao usuário deve ser construído a partir de `FRONTEND_URL`, e o envio transacional baseline do target-state usa `Resend`. | `PasswordResetFlow` | `AUTH_EXPERIENCE_CONTRACT.md` | Integração explícita, sem inferência |

## Limites de inferência
- Não modelar `birth_date`, `height`, `position`, `injury_history_summary` ou qualquer dado de perfil/saúde neste módulo.
- Não inferir papel técnico a partir de posição esportiva ou equipe.
- Não mover política de autenticação para módulos de negócio.

## Âncoras estruturadas
- As entidades soberanas e seus campos mapeados para runtime estão em `docs/hbtrack/modulos/identity_access/graph/entity_graph.yaml`.
- O mapa mínimo de operações e permissões publicadas está em `docs/hbtrack/modulos/identity_access/graph/endpoints.yaml`.
- O mapa mínimo de erros transport/domain do módulo está em `docs/hbtrack/modulos/identity_access/graph/errors.yaml`.
