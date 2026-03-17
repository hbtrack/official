---
doc_type: canon
version: "1.1.0"
last_reviewed: "2026-03-16"
status: active
---

# CONTRACT_PIPELINE.md

## 0. Objetivo

Consolidar os estágios oficiais do fluxo contract-driven do HB Track, com autoridade por estágio,
evidência obrigatória e enforcement técnico correspondente.

## 1. Regra de canonização operacional do pipeline

Toda melhoria que altera comportamento esperado do agente só entra no pipeline oficial quando existe em 3 níveis:

| Nível | Pergunta respondida | Artefatos autorizados |
| --- | --- | --- |
| Regra normativa | o que é obrigatório? | `.contract_driven/CONTRACT_SYSTEM_RULES.md`, `.contract_driven/CONTRACT_SYSTEM_LAYOUT.md`, canon global aplicável |
| Registro operacional | quando ler, aplicar ou bloquear? | `docs/_canon/CONTRACT_PIPELINE.md`, `docs/_canon/BOOT_PROFILES.md`, `docs/_canon/gates/GATES_REGISTRY.yaml`, `docs/_canon/MODULE_REGISTRY.yaml` |
| Enforcement técnico | como a regra vira comportamento executável? | generators, validators, gates, CI e prompts operacionais |

**Artefato de boot canônico:** `CLAUDE.md` (raiz do projeto) é carregado automaticamente pelo agente no início de cada sessão. Ele substitui a leitura sequencial de todos os artefatos de contexto e remete às fontes canônicas on-demand. Qualquer alteração em `CLAUDE.md` requer aprovação de ADR.

Regra:
- melhoria que exista só em código, prompt ou `_reports/` ainda não faz parte do pipeline oficial;
- prompt operacionaliza, mas não substitui a regra substantiva;
- conflito entre prompt e canon deve bloquear o fluxo.

## 2. Estágios oficiais

| Estágio | Autoridade obrigatória | Evidência obrigatória | Enforcement técnico | Condição de avanço |
| --- | --- | --- | --- | --- |
| Pre-contract | `RULES`, `LAYOUT`, `MODULE_REGISTRY`, `BOOT_PROFILES` | `_reports/agent_execution/*.json`, `_reports/evidence/boot_resolution_report.json`, `SESSION_HANDOFF.md` (quando existir) | pre-contract orchestrator, `PRE_CONTRACT_EVIDENCE_GATE`, `MODULE_REGISTRY_GATE` | worker destino resolvido, boot classificado e foundation pronta |
| Decision Discovery | `DECISION_POLICY`, backlog arquitetural, ADRs aceitas, DSS apenas como apoio | ADR criada/atualizada ou bloqueio explícito | `.contract_driven/agent_prompts/decision_discovery.prompt.md`, backlog/ADR workflow | nenhuma decisão obrigatória em aberto |
| Authoring | templates SSOT, docs de módulo, contratos soberanos, `MODULE_REGISTRY.expected_surfaces` | artefatos soberanos nos paths canônicos + derivados em `generated/` | workers especializados, generators, validações locais | artefato escrito no path correto, sem inferência fora do canon |
| Validation | `CI_CONTRACT_GATES.md`, `GATES_REGISTRY`, `TOOLCHAIN_HEALTH_POLICY` | `_reports/contract_gates/latest.json` | `validate_contracts.py`, gates oficiais, CI | nenhum gate bloqueante em `FAIL` |
| Readiness | `MODULE_REGISTRY`, DoD por superfície em `RULES`, `MODULE_DECISION_IR` quando aplicável | `_reports/evidence/module_readiness_scorecard.json` | `READINESS_SUMMARY_GATE`, `DECISION_IR_CONFORMANCE_GATE` | módulo elegível para `validated_contract` ou `implementation_ready` |
| Implementation handoff | scorecard final, evidência pré-contrato, contratos aprovados | handoff explícito e rastreável | gates de readiness + processo de implementação | contrato materializável sem inferência adicional |

## 3. Regras de transição

- nenhum estágio pode pular o anterior;
- todo output derivado vive em `generated/` ou `_reports/`;
- nenhuma implementação pode começar antes de `Validation` + `Readiness`;
- mudança em input global de policy exige `python3 scripts/contracts/validate/api/compile_api_policy.py --all` antes de retomar `Validation`;
- módulo com status insuficiente em `MODULE_REGISTRY.yaml` não pode ser tratado como pronto por conveniência.

## 4. Registro mínimo por melhoria

Quando uma melhoria altera o fluxo:
1. registrar a obrigação substantiva em `RULES` e/ou `LAYOUT`;
2. registrar o estágio e a ordem em `CONTRACT_PIPELINE.md`;
3. classificar a leitura em `BOOT_PROFILES.md`;
4. registrar o bloqueio em `GATES_REGISTRY.yaml`, quando houver gate oficial;
5. só então atualizar prompt, validator, generator ou CI.

## 5. Papel do prompt

Prompts do diretório `.contract_driven/agent_prompts/` são entrypoints operacionais.

Eles:
- executam o pipeline já canonizado;
- não criam regra substantiva sozinhos;
- devem carregar os artefatos exigidos por `BOOT_PROFILES.md`;
- devem bloquear quando o canon não sustentar uma instrução operacional.
