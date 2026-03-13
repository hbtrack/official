---
module: "training"
system_scope_ref: "../../../_canon/SYSTEM_SCOPE.md"
handball_rules_ref: "../../../_canon/HANDBALL_RULES_DOMAIN.md"
handball_semantic_applicability: true
contract_path_ref: "../../../../contracts/openapi/paths/training.yaml"
schemas_ref: "../../../../contracts/schemas/training/"
type: "test-matrix"
---

# TEST_MATRIX_TRAINING.md

## Objetivo
Mapear a cobertura mínima de testes do módulo `training`.

## Princípio
Toda superfície contratual e toda regra crítica do módulo deve ter prova correspondente.

## Matriz
| ID | Área | Artefato-fonte | Tipo de teste | Ferramenta | Obrigatório | Evidência |
|---|---|---|---|---|---|---|
| TM-001 | API | `contracts/openapi/paths/training.yaml` | Contract test | Schemathesis | Sim | `_reports/contract_gates/latest.json` |
| TM-002 | Schema | `contracts/schemas/training/*.schema.json` | Schema validation | JSON Schema validator | Sim | `_reports/contract_gates/latest.json` |
| TM-003 | Regras de domínio | `DOMAIN_RULES_TRAINING.md` (DR-TRAIN-001 a DR-TRAIN-007) | Business rule test | pytest | Sim | `tests/training/test_domain_rules.py` |
| TM-004 | Invariantes | `INVARIANTS_TRAINING.md` (INV-TRAIN-001 a INV-TRAIN-006) | Invariant test | pytest | Sim | `tests/training/test_invariants.py` |
| TM-005 | Regras derivadas do handebol | `DOMAIN_RULES_TRAINING.md` (DR-TRAIN-H01 a DR-TRAIN-H04) | Business rule test | pytest | Sim | `tests/training/test_handball_rules.py` |
| TM-006 | Wellness temporal | INV-TRAIN-002, INV-TRAIN-003 | Temporal validation test | pytest | Sim | `tests/training/test_wellness_temporal.py` |
| TM-007 | Janela de edição por papel | INV-TRAIN-004 | Authorization + temporal test | pytest | Sim | `tests/training/test_edit_windows.py` |
| TM-008 | Readonly histórico | INV-TRAIN-005 | Temporal validation test | pytest | Sim | `tests/training/test_readonly_sessions.py` |

## Casos mínimos obrigatórios
- Payload válido (sessão com todos os campos)
- Payload inválido (soma de foco > 120)
- Erro esperado (submissão fora da janela temporal)
- Violação de regra de domínio (DR-TRAIN-002: soma de foco)
- Violação de invariante (INV-TRAIN-002: wellness pré-treino tardio)
- Validação de RBAC (treinador vs coordenador)
- Validação temporal (edição fora da janela)
- Readonly histórico (sessão > 60 dias)

## Regra
Nenhuma feature do módulo pode ser considerada pronta sem evidência mínima nesta matriz.
