---
module: "medical"
system_scope_ref: "../../../_canon/SYSTEM_SCOPE.md"
handball_rules_ref: "../../../_canon/HANDBALL_RULES_DOMAIN.md"
handball_semantic_applicability: false
contract_path_ref: "../../../../contracts/openapi/paths/medical.yaml"
schemas_ref: "../../../../contracts/schemas/medical/"
type: "domain-rules"
updated: "2026-03-16"
---

# DOMAIN_RULES_MEDICAL.md

## Objetivo
Registrar as regras de negócio do módulo `medical`.

## Fonte do domínio
- `docs/_canon/MODULE_SOURCE_AUTHORITY_MATRIX.yaml`
- `contracts/schemas/medical/medical_record.schema.json`
- `docs/hbtrack/modulos/medical/INVARIANTS_MEDICAL.md`
- Fontes técnico-científicas permitidas via authority matrix (`ASPETAR`, `ACSM`, `IHF` quando aplicável)
- `docs/hbtrack/modulos/medical/graph/entity_graph.yaml`
- `docs/hbtrack/modulos/medical/graph/errors.yaml`
- `docs/hbtrack/modulos/medical/graph/endpoints.yaml`

## Regras de negócio
| ID | Regra | Entidades afetadas | Fonte | Observações |
|---|---|---|---|---|
| DR-MED-001 | `medical` é soberano de avaliação clínica, restrição, autorização de retorno ao treino e retorno ao jogo. | `MedicalRecord` | Authority matrix `medical` | Fonte clínica formal |
| DR-MED-002 | Dados de `wellness` não viram prontuário médico sem avaliação clínica explícita registrada em `medical`. | `MedicalRecord`, `WellnessEntry` | Boundary `wellness`/`medical` | Impede medicalização implícita |
| DR-MED-003 | `returnToTrainingAuthorized` e `returnToPlayAuthorized` são decisões distintas; liberação para jogo pressupõe raciocínio clínico documentado além da rotina de treino. | `MedicalRecord` | Semântica clínica do módulo | Não colapsar autorizações |
| DR-MED-004 | `assessmentSummary`, `restrictionSummary` e `clinicalNotes` são dados sensíveis sob governança de privacidade e auditoria; outros módulos consomem apenas abstrações contratadas. | `MedicalRecord` | Authority matrix + privacy bindings | Leitura controlada |
| DR-MED-005 | Nenhuma hipótese diagnóstica ou autorização clínica pode existir fora de um registro médico explícito. | `MedicalRecord` | Authority matrix `must_not_infer` | Bloqueia inferência solta |

## Limites de inferência
- Não tratar `wellness` como prontuário clínico.
- Não mover autenticação, sessão ou política de autorização para `medical`.
- Não aceitar diagnóstico, tratamento ou clearance sem contrato explícito do módulo.

## Âncoras estruturadas
- As entidades soberanas e seus campos mapeados para runtime estão em `docs/hbtrack/modulos/medical/graph/entity_graph.yaml`.
- O mapa mínimo de operações e permissões publicadas está em `docs/hbtrack/modulos/medical/graph/endpoints.yaml`.
- O mapa mínimo de erros transport/domain do módulo está em `docs/hbtrack/modulos/medical/graph/errors.yaml`.
