---
module: "wellness"
system_scope_ref: "../../../_canon/SYSTEM_SCOPE.md"
handball_rules_ref: "../../../_canon/HANDBALL_RULES_DOMAIN.md"
handball_semantic_applicability: false
contract_path_ref: "../../../../contracts/openapi/paths/wellness.yaml"
schemas_ref: "../../../../contracts/schemas/wellness/"
type: "invariants"
updated: "2026-03-16"
---

# INVARIANTS_WELLNESS.md

## Objetivo
Registrar invariantes do módulo `wellness`.

## Definição
Invariantes são condições que devem permanecer verdadeiras independentemente do fluxo, endpoint ou interface.

## Invariantes globais vinculantes
- `.contract_driven/DOMAIN_AXIOMS.json`
- `docs/_canon/GLOBAL_INVARIANTS.md`

## Tabela de invariantes
| ID | Invariante | Entidades | Fonte | Como verificar |
|---|---|---|---|---|
| INV-WELL-001 | `id`, `athleteUserId`, `questionnaireDate` e `readinessScore` são obrigatórios. | `WellnessEntry` | `wellness_entry.schema.json` | JSON Schema validation |
| INV-WELL-002 | `readinessScore`, `fatigueScore`, `painScore` e `recoveryScore`, quando presentes, permanecem no intervalo `[0..10]`. | `WellnessEntry` | Schema local | Range validation |
| INV-WELL-003 | `sleepHours`, quando presente, permanece no intervalo `[0..24]`. | `WellnessEntry` | Schema local | Range validation |
| INV-WELL-004 | `wellness` não pode conter `diagnosis`, `treatment`, `prescription`, `procedure`, `medical_record` ou `clinical_note`. | `WellnessEntry` | `WELLNESS_MEDICAL_BOUNDARY_GATE` | Gate de boundary |
| INV-WELL-005 | `trainingSessionId`, quando presente, contextualiza a resposta de wellness, mas não pode substituir presença, execução ou autorização de treino. | `WellnessEntry` | Boundary com `training` | Revisão de contrato |

## Relação com outros documentos
- `docs/hbtrack/modulos/wellness/DOMAIN_RULES_WELLNESS.md`
- `contracts/schemas/wellness/wellness_entry.schema.json`
