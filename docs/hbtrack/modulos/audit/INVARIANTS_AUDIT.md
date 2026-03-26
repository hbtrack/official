---
module: "audit"
system_scope_ref: "../../../_canon/SYSTEM_SCOPE.md"
handball_rules_ref: "../../../_canon/HANDBALL_RULES_DOMAIN.md"
handball_semantic_applicability: false
contract_path_ref: "../../../../contracts/openapi/paths/audit.yaml"
schemas_ref: "../../../../contracts/schemas/audit/"
type: "invariants"
updated: "2026-03-16"
---

# INVARIANTS_AUDIT.md

## Objetivo
Registrar invariantes do módulo `audit`.

## Definição
Invariantes são condições que devem permanecer verdadeiras independentemente do fluxo, endpoint ou interface.

## Invariantes globais vinculantes
- `.contract_driven/DOMAIN_AXIOMS.json`
- `docs/_canon/GLOBAL_INVARIANTS.md`

## Tabela de invariantes
| ID | Invariante | Entidades | Fonte | Como verificar |
|---|---|---|---|---|
| INV-AUD-001 | `id`, `actorUserId`, `action` e `occurredAt` são obrigatórios em toda entrada de auditoria. | `AuditEntry` | `audit_entry.schema.json` | JSON Schema validation |
| INV-AUD-002 | `audit` é append-only; entradas não podem ser sobrescritas destrutivamente após registradas. | `AuditEntry` | Regra estrutural do módulo | Teste de persistência/auditoria |
| INV-AUD-003 | Se `targetResourceId` estiver presente, `targetResourceType` deve estar explicitado. | `AuditEntry` | Regra de coerência do módulo | Teste de contrato |
| INV-AUD-004 | `beforeSummary` e `afterSummary`, quando presentes, devem ser resumos saneados e não cópia integral de payload sensível. | `AuditEntry` | Authority matrix `must_not_infer` | Revisão de compliance |
| INV-AUD-005 | `correlationId`, quando presente, deve permanecer estável entre os eventos da mesma operação correlacionada. | `AuditEntry` | Authority matrix `correlation_id` | Testes integrados de rastreabilidade |

## Relação com outros documentos
- `docs/hbtrack/modulos/audit/DOMAIN_RULES_AUDIT.md`
- `contracts/schemas/audit/audit_entry.schema.json`
