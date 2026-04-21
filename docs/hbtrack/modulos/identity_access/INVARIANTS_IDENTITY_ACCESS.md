---
module: "identity_access"
system_scope_ref: "../../../_canon/SYSTEM_SCOPE.md"
handball_rules_ref: "../../../_canon/HANDBALL_RULES_DOMAIN.md"
handball_semantic_applicability: false
contract_path_ref: "../../../../contracts/openapi/paths/identity_access.yaml"
schemas_ref: "../../../../contracts/schemas/identity_access/"
type: "invariants"
updated: "2026-03-16"
---

# INVARIANTS_IDENTITY_ACCESS.md

## Objetivo
Registrar invariantes do módulo `identity_access`.

## Definição
Invariantes são condições que devem permanecer verdadeiras independentemente do fluxo, endpoint ou interface.

## Invariantes globais vinculantes
- `.contract_driven/DOMAIN_AXIOMS.json`
- `docs/_canon/GLOBAL_INVARIANTS.md`

## Tabela de invariantes
| ID | Invariante | Entidades | Fonte | Como verificar |
|---|---|---|---|---|
| INV-IAM-001 | `id`, `principalUserId` e `sessionScopeLabel` são obrigatórios em toda sessão autenticada estável. | `AuthSession` | `auth_session.schema.json` | JSON Schema validation |
| INV-IAM-002 | `roleLabels` é coleção sem duplicidade. | `AuthSession` | Schema local | `uniqueItems` + auditoria de payload |
| INV-IAM-003 | `issuedAt < expiresAt`, e `revokedAt`, quando presente, deve ser maior ou igual a `issuedAt`. | `AuthSession` | Regra temporal do módulo | Teste de contrato |
| INV-IAM-004 | `identity_access` não pode conter `birth_date`, `height`, `dominant_hand`, `position` ou `injury_history_summary`. | `AuthSession` | `BOUNDARY_USERS_IDENTITY_ACCESS_GATE` | Gate de boundary |
| INV-IAM-005 | O fluxo de recuperação de senha não pode vazar existência de conta via resposta síncrona; links de reset devem ser de uso único e vinculados ao frontend oficial. | `PasswordResetFlow` | `AUTH_EXPERIENCE_CONTRACT.md` | Revisão contratual + testes de integração |

## Relação com outros documentos
- `docs/hbtrack/modulos/identity_access/DOMAIN_RULES_IDENTITY_ACCESS.md`
- `contracts/schemas/identity_access/auth_session.schema.json`
