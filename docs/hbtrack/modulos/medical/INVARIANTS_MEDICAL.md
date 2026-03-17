---
module: "medical"
system_scope_ref: "../../../_canon/SYSTEM_SCOPE.md"
handball_rules_ref: "../../../_canon/HANDBALL_RULES_DOMAIN.md"
handball_semantic_applicability: false
contract_path_ref: "../../../../contracts/openapi/paths/medical.yaml"
schemas_ref: "../../../../contracts/schemas/medical/"
type: "invariants"
updated: "2026-03-16"
---

# INVARIANTS_MEDICAL.md

## Objetivo
Registrar invariantes do módulo `medical`.

## Definição
Invariantes são condições que devem permanecer verdadeiras independentemente do fluxo, endpoint ou interface.

## Invariantes globais vinculantes
- `.contract_driven/DOMAIN_AXIOMS.json`
- `docs/_canon/GLOBAL_INVARIANTS.md`

## Tabela de invariantes
| ID | Invariante | Entidades | Fonte | Como verificar |
|---|---|---|---|---|
| INV-MED-001 | `id`, `athleteUserId`, `recordDate` e `recordLabel` são obrigatórios em todo registro médico. | `MedicalRecord` | `medical_record.schema.json` | JSON Schema validation |
| INV-MED-002 | `returnToPlayAuthorized = true` implica `returnToTrainingAuthorized = true`. | `MedicalRecord` | Semântica clínica do módulo | Regra de domínio + teste de contrato |
| INV-MED-003 | `medical` não pode absorver autenticação, sessão ou política de autorização técnica. | `MedicalRecord` | Authority matrix `must_not_infer` | Revisão de contrato |
| INV-MED-004 | Dados clínicos sensíveis permanecem sob binding de privacidade e auditoria; outros módulos só consomem abstrações contratadas. | `MedicalRecord` | Authority matrix `AUDIT_BINDINGS`, `PRIVACY_RULES_LOCAL` | Revisão de access control + auditoria |

## Relação com outros documentos
- `docs/hbtrack/modulos/medical/DOMAIN_RULES_MEDICAL.md`
- `contracts/schemas/medical/medical_record.schema.json`
