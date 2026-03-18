---
doc_type: canon
version: "1.1.0"
last_reviewed: "2026-03-16"
status: active
---

# CONTRACT_PIPELINE.md

## 0. Objetivo
Consolidar os estágios oficiais do fluxo contract-driven, com autoridade, evidência e enforcement por estágio.

## 1. Princípios Canônicos
- 3 níveis de canonização: regra substantiva (RULES) → registro operacional (PIPELINE) → enforcement técnico (gates + validators)
- Boot canônico: `docs/_canon/AGENT_INSTRUCTIONS.md` carregado automaticamente
- Cada fase tem critério binário: FAIL = exitcode !=0, não avançar

## 2. Estágios Oficiais

| Estágio | Autoridade obrigatória | Evidência obrigatória | Enforcement técnico | Condição de avanço |
| --- | --- | --- | --- | --- |
| Pre-contract | `RULES`, `LAYOUT`, `MODULE_REGISTRY`, `.contract_driven/BOOT_PROFILES.yaml` | `_reports/session_start.json`, `SESSION_HANDOFF.md` (quando existir) | pre-contract orchestrator, `PRE_CONTRACT_EVIDENCE_GATE`, `MODULE_REGISTRY_GATE` | worker destino resolvido, boot classificado e foundation pronta |
| Decision Discovery | `DECISION_POLICY`, backlog arquitetural, ADRs aceitas, DSS apenas como apoio | ADR criada/atualizada ou bloqueio explícito | `.contract_driven/agent_prompts/decision_discovery.prompt.md`, backlog/ADR workflow | nenhuma decisão obrigatória em aberto |
| Authoring | templates SSOT, docs de módulo, contratos soberanos, `MODULE_REGISTRY.expected_surfaces` | artefatos soberanos nos paths canônicos + derivados em `generated/` | workers especializados, generators, validações locais | artefato escrito no path correto, sem inferência fora do canon |
| Validation | `CI_CONTRACT_GATES.md`, `GATES_REGISTRY`, `TOOLCHAIN_HEALTH_POLICY` | `_reports/contract_gates/latest.json` | `validate_contracts.py`, gates oficiais, CI | nenhum gate bloqueante em `FAIL` |
| Readiness | `MODULE_REGISTRY`, DoD por superfície em `RULES`, `MODULE_DECISION_IR` quando aplicável | `_reports/evidence/module_readiness_scorecard.json` | `READINESS_SUMMARY_GATE`, `DECISION_IR_CONFORMANCE_GATE` | módulo elegível para `validated_contract` ou `implementation_ready` |
| Implementation handoff | scorecard final, evidência pré-contrato, contratos aprovados | handoff explícito e rastreável | gates de readiness + processo de implementação | contrato materializável sem inferência adicional |

## 3. Regras de Transição
- Sem pular estágios; nenhuma implementação antes de Validation + Readiness
- Output derivado vive em `generated/` ou `_reports/`
- Mudança em input global exige `python3 scripts/contracts/validate/api/compile_api_policy.py --all` antes de re-validar

## 4. Registro de Melhoria
Alteração no fluxo: registrar em RULES + PIPELINE + `.contract_driven/BOOT_PROFILES.yaml` + GATES_REGISTRY (quando houver gate) — só então atualizar código/prompt.

## 5. Enforcement Técnico
Prompts operacionalizam; não substituem o canon. Conflito prompt ↔ canon deve bloquear.
