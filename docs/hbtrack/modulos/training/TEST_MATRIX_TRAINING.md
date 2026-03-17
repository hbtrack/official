---
module: "training"
system_scope_ref: "../../../_canon/SYSTEM_SCOPE.md"
handball_rules_ref: "../../../_canon/HANDBALL_RULES_DOMAIN.md"
handball_semantic_applicability: true
contract_path_ref: "../../../../contracts/openapi/paths/training.yaml"
schemas_ref: "../../../../contracts/schemas/training/"
type: "test-matrix"
updated_at: "2026-03-16"
coverage_baseline: "DR-TRAIN-001..049 + DR-TRAIN-H01..H04 | INV-TRAIN-001..099 + EXB-ACL-001..007 | 21 endpoints | 7 schemas"
---

# TEST_MATRIX_TRAINING.md

## Objetivo
Mapear a cobertura mínima de testes do módulo `training`.

## Princípio
Toda superfície contratual e toda regra crítica do módulo deve ter prova correspondente.

---

## Matriz — Cobertura de Superfície Contratual

| ID | Área | Artefato-fonte | Tipo de teste | Ferramenta | Obrigatório | Evidência |
|---|---|---|---|---|---|---|
| TM-001 | API — superfície completa | `contracts/openapi/paths/training.yaml` (21 endpoints) | Contract test | Schemathesis | Sim | `_reports/contract_gates/latest.json` |
| TM-002 | Schemas JSON | `contracts/schemas/training/*.schema.json` (7 schemas) | Schema validation | JSON Schema validator | Sim | `_reports/contract_gates/latest.json` |
| TM-003 | Spectral OpenAPI | `contracts/openapi/openapi.yaml` + `.spectral.yaml` | Lint / ruleset | Spectral CLI | Sim | `_reports/contract_gates/latest.json` |
| TM-004 | FSM training_session | `STATE_MODEL_TRAINING.md` + ADR-017 | Transition test | pytest | Sim | `tests/training/test_state_machine.py` |

---

## Matriz — Regras de Domínio (DR-TRAIN-001 a DR-TRAIN-049 + H01–H04)

| ID | Área | Artefato-fonte | Tipo de teste | Ferramenta | Obrigatório | Evidência |
|---|---|---|---|---|---|---|
| TM-010 | RBAC: criação de sessão | DR-TRAIN-001 | Authorization test | pytest | Sim | `tests/training/test_domain_rules.py` |
| TM-011 | Soma de foco ≤ 120 | DR-TRAIN-002 | Business rule test | pytest | Sim | `tests/training/test_domain_rules.py` |
| TM-012 | Categorias válidas | DR-TRAIN-003 | Business rule test | pytest | Sim | `tests/training/test_domain_rules.py` |
| TM-013 | Wellness pré vinculado a sessão | DR-TRAIN-004 | Business rule test | pytest | Sim | `tests/training/test_domain_rules.py` |
| TM-014 | Um wellness pré por atleta por sessão | DR-TRAIN-005 | Uniqueness test | pytest | Sim | `tests/training/test_domain_rules.py` |
| TM-015 | Wellness pós só depois de sessão iniciada | DR-TRAIN-006 | Temporal test | pytest | Sim | `tests/training/test_domain_rules.py` |
| TM-016 | Um wellness pós por atleta por sessão | DR-TRAIN-007 | Uniqueness test | pytest | Sim | `tests/training/test_domain_rules.py` |
| TM-017 | Regras handball: posições-alvo | DR-TRAIN-H01 | Domain rule test | pytest | Sim | `tests/training/test_handball_rules.py` |
| TM-018 | Regras handball: carga periodização | DR-TRAIN-H02 | Domain rule test | pytest | Sim | `tests/training/test_handball_rules.py` |
| TM-019 | Regras handball: HBR-007 posições | DR-TRAIN-H03 | Domain rule test | pytest | Sim | `tests/training/test_handball_rules.py` |
| TM-020 | Regras handball: fases do jogo | DR-TRAIN-H04 | Domain rule test | pytest | Sim | `tests/training/test_handball_rules.py` |
| TM-021 | Unidade soberana = ciclo intervenção | DR-TRAIN-008 | Structural test | pytest | Sim | `tests/training/test_domain_rules.py` |
| TM-022 | Sessão nasce de need/goal/focus | DR-TRAIN-009 | Business rule test | pytest | Sim | `tests/training/test_domain_rules.py` |
| TM-023 | Analytics/IA apenas recomenda | DR-TRAIN-010 | Boundary test | pytest | Sim | `tests/training/test_domain_rules.py` |
| TM-024 | SessionObjective obrigatório | DR-TRAIN-011 | Presence test | pytest | Sim | `tests/training/test_objectives.py` |
| TM-025 | Origem de objetivo obrigatória | DR-TRAIN-012 | Enum validation test | pytest | Sim | `tests/training/test_objectives.py` |
| TM-026 | MANUAL_COACH_RATIONALE exige originNotes | DR-TRAIN-013 | Conditional field test | pytest | Sim | `tests/training/test_objectives.py` |
| TM-027 | Pré-requisitos para PUBLISHED/SCHEDULED | DR-TRAIN-014 | State precondition test | pytest | Sim | `tests/training/test_state_machine.py` |
| TM-028 | execution_record contexto de prescrição | DR-TRAIN-015 | Business rule test | pytest | Sim | `tests/training/test_execution_records.py` |
| TM-029 | planned_content_snapshot imutável pós-publish | DR-TRAIN-016 | Immutability test | pytest | Sim | `tests/training/test_execution_records.py` |
| TM-030 | COMPLETED imutável por edição destrutiva | DR-TRAIN-017 | Immutability test | pytest | Sim | `tests/training/test_state_machine.py` |
| TM-031 | Ajuste ao vivo exige motivo estruturado | DR-TRAIN-018 | Business rule test | pytest | Condicional (Fase 2) | `tests/training/test_live_adjustments.py` |
| TM-032 | Feedback vinculado a contexto | DR-TRAIN-019 | Business rule test | pytest | Sim | `tests/training/test_feedback_threads.py` |
| TM-033 | Feedback com conversation_outcome | DR-TRAIN-020 | Business rule test | pytest | Sim | `tests/training/test_feedback_threads.py` |
| TM-034 | FOLLOWUP_SCHEDULED exige followUpAt | DR-TRAIN-021 | Conditional field test | pytest | Sim | `tests/training/test_feedback_threads.py` |
| TM-035 | COMMITMENT_MADE exige commitmentText | DR-TRAIN-022 | Conditional field test | pytest | Sim | `tests/training/test_feedback_threads.py` |
| TM-036 | Revisão exige evidência de execução | DR-TRAIN-023 | Evidence chain test | pytest | Sim | `tests/training/test_reviews.py` |
| TM-037 | Restrição crítica bloqueia prescrição | DR-TRAIN-024 | Eligibility test | pytest | Sim | `tests/training/test_restrictions.py` |
| TM-038 | Override de restrição auditado | DR-TRAIN-025 | Audit trail test | pytest | Sim | `tests/training/test_restrictions.py` |
| TM-039 | FSM fechada training_session | DR-TRAIN-026 | State machine test | pytest | Sim | `tests/training/test_state_machine.py` |
| TM-040 | AttentionQueue: severity/reason/target obrigatórios | DR-TRAIN-027 | Presence test | pytest | Sim | `tests/training/test_attention_queue.py` |
| TM-041 | Dois loops: coletivo e individual | DR-TRAIN-028 | Structural test | pytest | Sim | `tests/training/test_domain_rules.py` |
| TM-042 | Persistência HYBRID | DR-TRAIN-029, DR-TRAIN-030 | Architecture test | pytest | Sim | `tests/training/test_persistence.py` |
| TM-043 | session_templates CRUD puro | DR-TRAIN-031 | Architecture test | pytest | Sim | `tests/training/test_persistence.py` |
| TM-044 | Separação camadas: Domain ≠ DTO ≠ ViewModel | DR-TRAIN-032, DR-TRAIN-033, DR-TRAIN-034, DR-TRAIN-035 | Layer separation test | pytest | Sim | `tests/training/test_layer_separation.py` |
| TM-045 | Dados externos via camada de ingestão | DR-TRAIN-036 | Boundary test | pytest | Sim | `tests/training/test_ingestion.py` |
| TM-046 | observed_at ≠ ingestedAt | DR-TRAIN-037 | Temporal field test | pytest | Sim | `tests/training/test_ingestion.py` |
| TM-047 | Idempotência de fatos ingeridos | DR-TRAIN-038 | Idempotency test | pytest | Sim | `tests/training/test_ingestion.py` |
| TM-048 | Wellness sensível: data_access_log | DR-TRAIN-039 | Audit test | pytest | Sim | `tests/training/test_sensitive_data.py` |
| TM-049 | Wellness sensível não exposto em genéricos | DR-TRAIN-040 | Security test | pytest | Sim | `tests/training/test_sensitive_data.py` |
| TM-050 | IA inferências sempre consultivas | DR-TRAIN-041 | Boundary test | pytest | Sim | `tests/training/test_domain_rules.py` |
| TM-051 | dropout_risk_signal nunca fonte primária | DR-TRAIN-042 | Derived field test | pytest | Sim | `tests/training/test_domain_rules.py` |
| TM-052 | AttentionQueue: itens sem campos rejeitados | DR-TRAIN-043 | Validation test | pytest | Sim | `tests/training/test_attention_queue.py` |
| TM-053 | Elastic Sum Rule + attention queue severity | DR-TRAIN-044 | Business rule test | pytest | Sim | `tests/training/test_attention_queue.py` |
| TM-054 | Notificação via notification_intent | DR-TRAIN-045 | Boundary test | pytest | Sim | `tests/training/test_boundaries.py` |
| TM-055 | Auditoria via módulo audit | DR-TRAIN-046 | Audit boundary test | pytest | Sim | `tests/training/test_boundaries.py` |
| TM-056 | medical read-only em training | DR-TRAIN-047 | Boundary test | pytest | Sim | `tests/training/test_boundaries.py` |
| TM-057 | identity_access governa; training aplica | DR-TRAIN-048 | RBAC boundary test | pytest | Sim | `tests/training/test_boundaries.py` |
| TM-058 | analytics soberano de derived_signal | DR-TRAIN-049 | Boundary test | pytest | Sim | `tests/training/test_boundaries.py` |
| TM-059 | exercises referenciado por ID+versão | DR-TRAIN-045 | Reference integrity test | pytest | Sim | `tests/training/test_boundaries.py` |
| TM-060 | HYBRID persistence coexistência | DR-TRAIN-046, DR-TRAIN-047 | Architecture test | pytest | Sim | `tests/training/test_persistence.py` |
| TM-061 | session_block DSL obrigatório na PUBLISHED | DR-TRAIN-049 | Presence test | pytest | Sim | `tests/training/test_session_blocks.py` |
| TM-062 | individualizationMode obrigatório e enum fechado | DR-TRAIN-030 | Enum validation test | pytest | Sim | `tests/training/test_domain_rules.py` |

---

## Matriz — Invariantes Críticas

| ID | Área | Artefato-fonte | Tipo de teste | Ferramenta | Obrigatório | Evidência |
|---|---|---|---|---|---|---|
| TM-100 | Soma de foco ≤ 120 | INV-TRAIN-001 | Invariant test | pytest | Sim | `tests/training/test_invariants.py` |
| TM-101 | Wellness pré bloqueado >= session_at - 2h | INV-TRAIN-002 | Temporal invariant | pytest | Sim | `tests/training/test_wellness_temporal.py` |
| TM-102 | Wellness pós bloqueado >= created_at + 24h | INV-TRAIN-003 | Temporal invariant | pytest | Sim | `tests/training/test_wellness_temporal.py` |
| TM-103 | Janela de edição por papel | INV-TRAIN-004 | Auth + temporal invariant | pytest | Sim | `tests/training/test_edit_windows.py` |
| TM-104 | Sessão > 60 dias somente leitura | INV-TRAIN-005 | Read-only invariant | pytest | Sim | `tests/training/test_readonly_sessions.py` |
| TM-105 | FSM 7 estados canônicos (ADR-017) | INV-TRAIN-006 | State machine invariant | pytest | Sim | `tests/training/test_state_machine.py` |
| TM-106 | planned_content_snapshot imutável após PUBLISHED | INV-TRAIN-007 | Immutability invariant | pytest | Sim | `tests/training/test_execution_records.py` |
| TM-107 | execution_record context chain | INV-TRAIN-008, INV-TRAIN-009 | Structural invariant | pytest | Sim | `tests/training/test_execution_records.py` |
| TM-108 | Feedback sem contexto rejeitado | INV-TRAIN-010 | Structural invariant | pytest | Sim | `tests/training/test_feedback_threads.py` |
| TM-109 | conversationOutcome obrigatório em FeedbackThread | INV-TRAIN-091 | Presence invariant | pytest | Sim | `tests/training/test_feedback_threads.py` |
| TM-110 | Transições inválidas de FSM retornam 422 | INV-TRAIN-017 | FSM transition invariant | pytest | Sim | `tests/training/test_state_machine.py` |
| TM-111 | Restrição crítica bloqueia prescrição sem override | INV-TRAIN-092 | Eligibility invariant | pytest | Sim | `tests/training/test_restrictions.py` |
| TM-112 | Derivados são view-only | INV-TRAIN-093 | Derived field invariant | pytest | Sim | `tests/training/test_invariants.py` |
| TM-113 | AttentionQueueItem: campos obrigatórios | INV-TRAIN-094 | Presence invariant | pytest | Sim | `tests/training/test_attention_queue.py` |
| TM-114 | training não entrega notificação diretamente | INV-TRAIN-095 | Boundary invariant | pytest | Sim | `tests/training/test_boundaries.py` |
| TM-115 | training envia eventos ao módulo audit | INV-TRAIN-096 | Audit invariant | pytest | Sim | `tests/training/test_boundaries.py` |
| TM-116 | training consome medical read-only | INV-TRAIN-097 | Boundary invariant | pytest | Sim | `tests/training/test_boundaries.py` |
| TM-117 | training aplica policy de identity_access | INV-TRAIN-098 | RBAC invariant | pytest | Sim | `tests/training/test_boundaries.py` |
| TM-118 | training referencia exercise_id + exercise_version_id | INV-TRAIN-099 | Reference invariant | pytest | Sim | `tests/training/test_boundaries.py` |
| TM-119 | Elastic Sum Rule (INV-TRAIN-083): Low/reject | INV-TRAIN-083 | Business rule invariant | pytest | Sim | `tests/training/test_attention_queue.py` |
| TM-120 | Sessão PUBLISHED exige >= 1 session_block | INV-TRAIN-086 | Presence invariant | pytest | Sim | `tests/training/test_session_blocks.py` |
| TM-121 | ACL extended bounds (EXB-ACL-001..007) | INV-TRAIN-EXB-ACL-001 a 007 | ACL invariant | pytest | Sim | `tests/training/test_acl.py` |

---

## Casos mínimos obrigatórios

- Payload válido: sessão com todos os campos obrigatórios (training_session + session_block + session_objective)
- Payload inválido: soma de foco > 120 (INV-TRAIN-001)
- Payload inválido: individualizationMode ausente (DR-TRAIN-030)
- Erro esperado: submissão de wellness_pre fora da janela temporal (INV-TRAIN-002)
- Violação de FSM: transição DRAFT => COMPLETED retorna 422 (INV-TRAIN-017)
- Violação de FSM: transição COMPLETED => IN_PROGRESS retorna 422 (INV-TRAIN-017)
- PUBLISHED sem session_block: rejeitado (INV-TRAIN-086, DR-TRAIN-049)
- Readonly histórico: sessão > 60 dias — edição bloqueada (INV-TRAIN-005)
- RBAC: criação por ator não autorizado rejeitada (DR-TRAIN-001)
- Validação temporal: edição fora da janela (INV-TRAIN-004)
- Override de restrição: sem auditoria rejeitado (INV-TRAIN-092, DR-TRAIN-025)
- Boundary: training não cria entidade medical nem exercise (INV-TRAIN-097, INV-TRAIN-099)
- Imutabilidade: planned_content_snapshot não alterável após PUBLISHED (INV-TRAIN-007)
- Feedback: sem conversationOutcome rejeitado (INV-TRAIN-091)
- SessionObjective: sem origin rejeitado (DR-TRAIN-012)
- MANUAL_COACH_RATIONALE sem originNotes rejeitado (DR-TRAIN-013)

---

## Regra
Nenhuma feature do módulo pode ser considerada pronta sem evidência mínima nesta matriz.
