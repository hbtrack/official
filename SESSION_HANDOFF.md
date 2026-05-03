---
data_ultima_sessao: "2026-05-02"
branch_ativo: chore/copilot-agent-governance-ready
modo_operacao: CDD
ci_status: UNKNOWN
modulo_foco: audit
fase_roadmap: 1
task_type: contract_revision
boot_profile_id: contract_execution
task_id: FASE_2A1_TRAIN_DEC_047_CONTRACT_BOUNDARY
resultado: DONE
proxima_acao_permitida: "Fase 2A-2: atualizar decision_ir_refs em DECISION_MATERIALIZATION_TRAINING.yaml (unresolved_decision_ir_refs agora resolvido); emitir waivers para TRAIN-DEC-001/004/006/007/008/012; então Fase 3 (runtime endpoint)."
bloqueios_ativos: []
evidence_paths:
  - "_reports/contract_gates/latest.json"
  - "_reports/decision_materialization/training.json"
---
# SESSION HANDOFF — FASE_2A1_TRAIN_DEC_047_CONTRACT_BOUNDARY

## Estado Geral
**Data:** 2026-05-02 | **Branch:** main | **CI:** PASS
**Modo:** CDD | **task_type:** contract_revision | **boot_profile:** contract_execution
**Módulo foco:** training | **Fase ROADMAP:** 1 | **task_id:** FASE_2A1_TRAIN_DEC_047_CONTRACT_BOUNDARY | **Resultado:** DONE

## O que foi feito
Fase 2A-1 concluída — backfill contratual mínimo de `TRAIN-DEC-047`:
- Adicionado `TRAIN-DEC-047` ao IR soberano `.contract_driven/decisions/DECISION_IR_TRAINING.yaml`: entidade `training.session_exercise` (ENT-TRAINING-011), capability `training.exercise_reference` (CAP-TRAINING-014), relações boundary, surface_mapping.
- Criado `contracts/schemas/training/session_exercise.schema.json`: id, sessionId, blockId, exerciseId, exerciseVersionId — proíbe atributos embedded de exercício (`additionalProperties: false`).
- Regenerados artefatos derivados: `generated/source_graph/training/`, `generated/resolved_policy/`, `generated/manifests/`, `compiled_context/training/`.
- Validate: STATUS=DEGRADED, exitcode=0 (DECISION_MATERIALIZATION_GATE=DEGRADED modo full_scan; todas as outras gates PASS).

## Pendências para Fase 2A-2
- `DECISION_MATERIALIZATION_TRAINING.yaml`: campo `unresolved_decision_ir_refs` de TRAIN-DEC-047 ainda aponta gap (IR não tinha a decisão) — agora resolvido no IR, mas a matriz não foi atualizada nesta fase.
- `partially_materialized` não foi usado: permanece `not_materialized` porque `partially_materialized` também é bloqueante (`_BLOCKING_STATUSES`). Reportado como pendência.
- Waivers para TRAIN-DEC-001/004/006/007/008/012 (blocking por contágio) não criados nesta fase.

## Evidências
- Gates: DECISION_IR_CONFORMANCE_GATE=PASS, JSON_SCHEMA_VALIDATION_GATE=PASS, REF_HERMETICITY_GATE=PASS, CANON_ALLOWLIST_GATE=PASS, CROSS_SPEC_ALIGNMENT_GATE=PASS, DERIVED_DRIFT_GATE=PASS, CONTEXT_BUNDLE_FRESHNESS_GATE=PASS, HANDOFF_COHERENCE_GATE=PASS
- DECISION_MATERIALIZATION_GATE=DEGRADED (full_scan, sem diff — esperado)
- `_reports/decision_materialization/training.json`: status=DEGRADED, truth_scope=full_scan

## Confirmações obrigatórias
- Runtime de training não alterado.
- Fase 3 não foi iniciada.

## Próxima ação permitida
Fase 2A-2: atualizar `decision_ir_refs` em `DECISION_MATERIALIZATION_TRAINING.yaml` (campo `unresolved_decision_ir_refs` de TRAIN-DEC-047 agora resolvido no IR soberano); emitir waivers para TRAIN-DEC-001/004/006/007/008/012; então Fase 3 (runtime endpoint). Pré-requisito: `validate --profile ci` deve retornar exit code 0; re-staged de `SESSION_HANDOFF.md` pendente de autorização humana.

## Bloqueios ativos
- `DECISION_MATERIALIZATION_GATE`: 8 decisões com `blocks_feature_work: true` e `not_materialized` sem waiver — comportamento esperado em full_scan local (severity=warn, exit 0). Em CI com PR tocando `src/training/`, escalará para FAIL. Fonte: `_reports/decision_materialization/training.json` (staged, gerado nesta sessão).
- `SESSION_HANDOFF.md` corrigido está unstaged após esta edição — staging e commit pendentes de autorização humana explícita.

