---
module: "training"
system_scope_ref: "../../../_canon/SYSTEM_SCOPE.md"
handball_rules_ref: "../../../_canon/HANDBALL_RULES_DOMAIN.md"
handball_semantic_applicability: true
type: "errors"
error_model_ref: "../../../../docs/_canon/ERROR_MODEL.md"
problem_schema_ref: "../../../../contracts/openapi/components/schemas/shared/problem.yaml"
updated_at: "2026-03-16"
---

# ERRORS_TRAINING.md

> Media type canônico de erro: `application/problem+json` (RFC 7807).
> Shape: `contracts/openapi/components/schemas/shared/problem.yaml`.
> Erros genéricos (400, 401, 404, 500) seguem o modelo global — este arquivo registra apenas os códigos específicos do domínio `training`.

---

## Erros de Transição de Estado (FSM — ADR-017)

| Código (type) | Situação | HTTP | Invariante/DR | Observação |
|---|---|---|---|---|
| `TRAINING_INVALID_STATE_TRANSITION` | Transição de estado inválida conforme FSM fechada (ex.: DRAFT→COMPLETED, COMPLETED→IN_PROGRESS) | 422 | INV-TRAIN-017, INV-TRAIN-006 | Detalhe no campo `detail` com transição tentada e estados válidos |
| `TRAINING_SESSION_IMMUTABLE` | Sessão em estado imutável (IN_PROGRESS, COMPLETED, ARCHIVED, CANCELLED) — edição destrutiva rejeitada | 422 | INV-TRAIN-006, DR-TRAIN-017 | Inclui `status` atual da sessão no `detail` |
| `TRAINING_SESSION_READONLY` | Sessão com `session_at` > 60 dias — somente leitura | 422 | INV-TRAIN-005 | Inclui `session_at` e limiar de 60 dias no `detail` |
| `TRAINING_MISSING_PUBLISH_REQUIREMENTS` | Sessão não possui pré-requisitos para PUBLISHED/SCHEDULED (falta objective, scope, bloco mínimo ou coach_assignment) | 422 | DR-TRAIN-014, INV-TRAIN-086 | Lista campos ausentes no `detail` |

---

## Erros de Validação de Domínio

| Código (type) | Situação | HTTP | Invariante/DR | Observação |
|---|---|---|---|---|
| `TRAINING_FOCUS_SUM_EXCEEDED` | Soma dos `focus_*_pct` excede 120 (INV-TRAIN-001) | 422 | INV-TRAIN-001, DR-TRAIN-002 | Inclui soma calculada e limite no `detail` |
| `TRAINING_WELLNESS_PRE_WINDOW_CLOSED` | Submissão ou edição de `wellness_pre` bloqueada (NOW >= session_at - 2h) | 400 | INV-TRAIN-002 | Inclui `session_at` e horário atual no `detail` |
| `TRAINING_WELLNESS_POST_WINDOW_CLOSED` | Edição de `wellness_post` bloqueada (NOW >= created_at + 24h) | 400 | INV-TRAIN-003 | Inclui `created_at` e limiar no `detail` |
| `TRAINING_EDIT_WINDOW_EXPIRED` | Janela de edição expirada para o papel do solicitante | 422 | INV-TRAIN-004 | Inclui papel, `session_at`/`ended_at` e janela permitida no `detail` |
| `TRAINING_OBJECTIVE_ORIGIN_REQUIRED` | `SessionObjective` sem `origin` válido | 422 | DR-TRAIN-012 | Lista valores válidos do enum `objective_origin` no `detail` |
| `TRAINING_MANUAL_RATIONALE_REQUIRED` | origin = MANUAL_COACH_RATIONALE sem `originNotes` (mínimo 10 chars) | 422 | DR-TRAIN-013 | — |
| `TRAINING_FEEDBACK_CONTEXT_REQUIRED` | `FeedbackThread` sem contexto operacional vinculado | 422 | DR-TRAIN-019, INV-TRAIN-010 | Lista campos de contexto esperados no `detail` |
| `TRAINING_OUTCOME_REQUIRED` | `FeedbackThread` sem `conversationOutcome` | 422 | INV-TRAIN-091, DR-TRAIN-020 | — |
| `TRAINING_FOLLOWUP_DATE_REQUIRED` | `conversationOutcome = FOLLOWUP_SCHEDULED` sem `followUpAt` | 422 | DR-TRAIN-021 | — |
| `TRAINING_COMMITMENT_TEXT_REQUIRED` | `conversationOutcome = COMMITMENT_MADE` sem `commitmentText` | 422 | DR-TRAIN-022 | — |
| `TRAINING_ELASTIC_SUM_VIOLATION` | Elastic Sum Rule (INV-TRAIN-083): excesso fora da tolerância de ±10% | 422 | INV-TRAIN-083, DR-TRAIN-053 | Inclui excesso em minutos no `detail`; violação dentro da tolerância retorna 200 com `Warning` header |
| `TRAINING_BLOCK_IDS_MISMATCH` | `blockIds` no reorder não batem com blocos da sessão | 422 | — | — |
| `TRAINING_MICROCYCLE_DATES_OUTSIDE_MESOCYCLE` | Datas do microciclo fora do intervalo do mesociclo pai | 422 | INV-TRAIN-056 | Inclui intervalos pai e filho no `detail` |
| `TRAINING_CYCLE_PARENT_INVALID` | Micro/Meso sem parent_cycle_id válido do tipo correto | 422 | INV-TRAIN-054 | — |

---

## Erros de Integridade Referencial

| Código (type) | Situação | HTTP | Invariante/DR | Observação |
|---|---|---|---|---|
| `TRAINING_EXECUTION_RECORD_CONTEXT_MISSING` | `ExecutionRecord` sem vínculo a sessão, bloco ou prescrição | 422 | INV-TRAIN-008, INV-TRAIN-009, DR-TRAIN-015 | — |
| `TRAINING_EXERCISE_VERSION_REQUIRED` | `exerciseId` presente sem `exerciseVersionId` | 422 | DR-TRAIN-048, TRAIN-DEC-048 | — |
| `TRAINING_WELLNESS_DUPLICATE` | Segundo registro de wellness pré ou pós para mesmo atleta na mesma sessão | 409 | DR-TRAIN-005, DR-TRAIN-007 | BOLA: idempotência via `PUT` se já existe |
| `TRAINING_ATTENTION_QUEUE_INVALID_ITEM` | Item de `AttentionQueueItem` sem `severity`, `reasonCode`, `targetEntityType` ou `targetEntityId` | 422 | INV-TRAIN-094, DR-TRAIN-038 | Lista campos ausentes no `detail` |

---

## Erros de Autorização

| Código (type) | Situação | HTTP | Invariante/DR | Observação |
|---|---|---|---|---|
| `TRAINING_FORBIDDEN` | Role insuficiente para a operação | 403 | PERMISSIONS_TRAINING.md | Segue OWASP BOLA: 403 retornado mesmo quando recurso não existe (não revelar existência) |
| `TRAINING_EXERCISE_ACL_FORBIDDEN` | Exercício ORG `restricted` sem ACL para o solicitante | 403 | INV-TRAIN-EXB-ACL-007, INV-TRAIN-065 | — |
| `TRAINING_ACL_ORG_MISMATCH` | Usuário adicionado à ACL de exercício de outra organização | 422 | INV-TRAIN-EXB-ACL-003 | — |
| `TRAINING_ACL_REDUNDANT` | Tentativa de adicionar ACL a exercício com `visibility_mode = org_wide` | 422 | INV-TRAIN-EXB-ACL-002 | — |
| `TRAINING_RESTRICTION_OVERRIDE_UNAUTHORIZED` | Tentativa de atribuir atleta com restrição crítica sem permissão de `OVERRIDE_RESTRICTION` | 403 | INV-TRAIN-092, DR-TRAIN-025 | Override legal exige registro via módulo `audit` |

---

## Erros de Constraint de Negócio

| Código (type) | Situação | HTTP | Invariante/DR | Observação |
|---|---|---|---|---|
| `TRAINING_PLANNED_SNAPSHOT_IMMUTABLE` | Tentativa de alterar `plannedContentSnapshot` após PUBLISHED | 422 | INV-TRAIN-007, TRAIN-DEC-045 | Campo write-once na transição para PUBLISHED |
| `TRAINING_SESSION_BLOCK_MISSING` | PUBLISHED requer pelo menos 1 `session_block` | 422 | INV-TRAIN-086, DR-TRAIN-049 | — |
| `TRAINING_SYSTEM_EXERCISE_READONLY` | Tentativa de editar exercício SYSTEM por usuário de org | 403 | INV-TRAIN-EXB-ACL-004, INV-TRAIN-069 | Use `copy-to-org` para adaptar |
| `TRAINING_ACL_DUPLICATE_USER` | Usuário já presente na ACL do exercício | 422 | INV-TRAIN-EXB-ACL-006 | Constraint de unicidade (exercise_id, user_id) |
