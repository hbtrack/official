---
doc_type: canon
version: "1.2.1"
last_reviewed: "2026-03-31"
status: active
---

# CONTRACT_PIPELINE.md

## 0. Objetivo
Consolidar o fluxo contract-driven com autoridade, evidência e enforcement por estágio.

## 1. Princípios Canônicos
- 3 níveis de canonização: regra substantiva (RULES) → registro operacional (PIPELINE) → enforcement técnico (gates + validators)
- owner source por conceito é definido em `docs/_canon/SOURCE_AUTHORITY_GRAPH.yaml`
- IR global: `docs/_canon/graph/global_rules.yaml`, `docs/_canon/graph/global_policies.yaml`, `docs/_canon/graph/lifecycle.yaml`, `docs/_canon/graph/source_map.yaml`
- IR operacional: `docs/_canon/graph/ops/`
- Boot canônico: `docs/_canon/AGENT_INSTRUCTIONS.md` carregado automaticamente
- Roteamento operacional: `.contract_driven/TASK_CATALOG.yaml`
- Entrypoint local: `scripts/hb`
- Cada fase é binária: FAIL = exitcode !=0, não avançar

## 2. Estágios Oficiais

| Estágio | Autoridade obrigatória | Evidência obrigatória | Enforcement técnico | Condição de avanço |
| --- | --- | --- | --- | --- |
| Pre-contract | `RULES`, `LAYOUT`, `MODULE_REGISTRY`, `.contract_driven/BOOT_PROFILES.yaml` | `_reports/session_start.json`, `SESSION_HANDOFF.md` (quando existir) | pre-contract orchestrator, `PRE_CONTRACT_EVIDENCE_GATE`, `MODULE_REGISTRY_GATE` | worker destino resolvido, boot classificado e foundation pronta |
| Decision Discovery | `DECISION_POLICY`, backlog arquitetural, ADRs aceitas, DSS apenas como apoio | ADR criada/atualizada ou bloqueio explícito | `decision_discovery.prompt.md`, backlog/ADR workflow | nenhuma decisão obrigatória em aberto |
| Authoring | templates SSOT, docs de módulo, contratos soberanos, `MODULE_REGISTRY.expected_surfaces` | artefatos soberanos no path canônico + derivados em `generated/` | workers especializados, generators, validações locais | artefato escrito no path correto, sem inferência fora do canon |
| Validation | `CI_CONTRACT_GATES.md`, `GATES_REGISTRY`, `TOOLCHAIN_HEALTH_POLICY` | `_reports/contract_gates/latest.json` | `validate_contracts.py`, gates oficiais, CI | nenhum gate bloqueante em `FAIL` |
| Readiness | `MODULE_REGISTRY`, DoD por superfície em `RULES`, `MODULE_DECISION_IR` quando aplicável | `_reports/evidence/module_readiness_scorecard.json` | `READINESS_SUMMARY_GATE`, `DECISION_IR_CONFORMANCE_GATE` | módulo elegível para `implementation_ready` |
| Implementation | `MODULE_REGISTRY`, `FEATURE_REGISTRY`, `CODE_ARCHITECTURE.md` | `src/<module>/`, testes do módulo, `_reports/adversarial/*.json` | `generate_code`, `implementation_promotion`, `CODE_ARCHITECTURE_GATE`, hooks de backend | somente módulos em `implementation_ready+` avançam para `implemented` via promoção formal |
| Staging validation | `DEPLOY_PIPELINE.md`, `docs/_canon/graph/ops/`, contratos vigentes, smoke checks | evidência de staging, health check, rollback ref | `staging_promotion` + workflow/gates | módulo elegível para `staging_validated` |
| Release | `DEPLOY_PIPELINE.md`, `docs/_canon/graph/ops/`, aprovação humana, artefatos de operação | evidência de produção, health check, aprovação rastreável | `release_promotion` + deploy/monitoramento | módulo elegível para `released` |

## 3. Regras de Transição
- Sem pular estágios; nenhuma implementação antes de Validation + Readiness
- Output derivado vive em `generated/` ou `_reports/`
- `_reports/contract_gates/latest.json` e os dashboards globais só podem ser atualizados por execução completa do pipeline (`profile=ci`, sem `--stage`); execuções parciais devem escrever relatórios escopados sem sobrescrever o baseline canônico.
- Logs de pré-contrato legados só podem ser aceitos como `baseline_backfill` quando declararem explicitamente `reconstructed_from`; sem isso, o módulo continua sem continuidade comprovada.
- Mudança em input global exige `python3 scripts/contracts/validate/api/compile_api_policy.py --all` antes de re-validar
- Lifecycle normativo de módulo:
  - `draft_contract` → `validated_contract`: superfícies esperadas presentes + gates verdes
  - `validated_contract` → `implementation_ready`: scorecard de readiness + adversarial PASS + Decision IR quando aplicável
  - `implementation_ready` → `implemented`: somente via `implementation_promotion`, com código em `src/<module>/`, runtime/testes reais e feature(s) em `implemented` no `FEATURE_REGISTRY`
  - `implemented` → `staging_validated`: só via `staging_promotion`, com staging comprovado
  - `staging_validated` → `released`: só via `release_promotion`, com aprovação e produção saudável

## 4. Registro de Melhoria
Alteração no fluxo: registrar em RULES + PIPELINE + `docs/_canon/graph/*.yaml` + `SOURCE_AUTHORITY_GRAPH.yaml` + `.contract_driven/BOOT_PROFILES.yaml` + GATES_REGISTRY (quando houver gate) — só então atualizar código.

## 5. Enforcement Técnico
Prompts operacionalizam; não substituem o canon. Conflito prompt ↔ canon deve bloquear.

## 6. Paridade Registry × Executor

Regra: todo gate inline em `validate_contracts.py` deve constar em `GATES_REGISTRY.yaml`.
Gates com `integrated_in_validate_contracts: false` são passos externos por design.
Teste obrigatório em CI: `tests/pipeline_gates/test_gate_registry_parity.py`.

Estado apurado 2026-03-23 (FASE 1):

| Gate | Decisão |
|------|---------|
| `SPECTRAL_LINTING_GATE` | Adicionado ao registry (order 13B) |
| `SURFACE_PROMOTION_COHERENCE_GATE` | Adicionado ao registry (order 20B1) |
| `SCOPE_BOUNDARY_GATE` | `integrated_in_validate_contracts: false` — passo pré-contrato externo |
| `ARCH_DECISION_PRESENCE_GATE` | ativo — bloqueia backlog arquitetural obrigatório pendente para contrato/readiness/generate_code |
| `FRONTEND_CONTRACT_GATE` | `status: deferred` — implementar junto com Fase 5 (frontend/) |
