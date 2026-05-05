---
doc_type: canon
version: "1.2.0"
last_reviewed: "2026-03-23"
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
| Decision Discovery | `DECISION_POLICY`, backlog arquitetural, ADRs aceitas, DSS apenas como apoio | ADR criada/atualizada ou bloqueio explícito | `decision_discovery.prompt.md`, backlog/ADR workflow | nenhuma decisão obrigatória em aberto |
| Authoring | templates SSOT, docs de módulo, contratos soberanos, `MODULE_REGISTRY.expected_surfaces` | artefatos soberanos no path canônico + derivados em `generated/` | workers especializados, generators, validações locais | artefato escrito no path correto, sem inferência fora do canon |
| Validation | `CI_CONTRACT_GATES.md`, `GATES_REGISTRY`, `TOOLCHAIN_HEALTH_POLICY` | `_reports/contract_gates/latest.json` | `validate_contracts.py`, gates oficiais, CI | nenhum gate bloqueante em `FAIL` |
| Readiness | `MODULE_REGISTRY`, DoD por superfície em `RULES`, `MODULE_DECISION_IR` quando aplicável | `_reports/evidence/module_readiness_scorecard.json` | `READINESS_SUMMARY_GATE`, `DECISION_IR_CONFORMANCE_GATE` | módulo elegível para `validated_contract` ou `implementation_ready` |
| Implementation | `MODULE_REGISTRY`, `FEATURE_REGISTRY`, `CODE_ARCHITECTURE.md` | `src/<module>/`, testes do módulo, `_reports/adversarial/*.json` | `generate_code`, `CODE_ARCHITECTURE_GATE`, hooks de backend | módulo elegível para `implemented` |
| Staging validation | `DEPLOY_PIPELINE.md`, contratos vigentes, smoke checks | evidência de staging, health check, rollback ref | workflow de deploy + gates/runtime checks aplicáveis | módulo elegível para `staging_validated` |
| Release | `DEPLOY_PIPELINE.md`, aprovação humana, artefatos de operação | evidência de produção, health check, aprovação rastreável | deploy manual/aprovado, monitoramento runtime | módulo elegível para `released` |

## 3. Regras de Transição
- Sem pular estágios; nenhuma implementação antes de Validation + Readiness
- Output derivado vive em `generated/` ou `_reports/`
- `_reports/contract_gates/latest.json` e os dashboards globais só podem ser atualizados por execução completa do pipeline (`profile=ci`, sem `--stage`); execuções parciais devem escrever relatórios escopados sem sobrescrever o baseline canônico.
- Logs de pré-contrato legados só podem ser aceitos como `baseline_backfill` quando declararem explicitamente `reconstructed_from`; sem isso, o módulo continua sem continuidade comprovada.
- Mudança em input global exige `python3 scripts/contracts/validate/api/compile_api_policy.py --all` antes de re-validar
- Lifecycle normativo de módulo:
  - `draft_contract` → `validated_contract`: superfícies esperadas presentes + gates verdes
  - `validated_contract` → `implementation_ready`: scorecard de readiness + adversarial PASS + Decision IR quando aplicável
  - `implementation_ready` → `implemented`: código em `src/<module>/`, runtime/testes reais, feature(s) em `implemented` quando o módulo estiver no `FEATURE_REGISTRY`
  - `implemented` → `staging_validated`: deploy de staging e health check comprovados
  - `staging_validated` → `released`: aprovação humana registrada + produção saudável + rollback referenciado

## 4. Registro de Melhoria
Alteração no fluxo: registrar em RULES + PIPELINE + `.contract_driven/BOOT_PROFILES.yaml` + GATES_REGISTRY (quando houver gate) — só então atualizar código/prompt.

## 5. Enforcement Técnico
Prompts operacionalizam; não substituem o canon. Conflito prompt ↔ canon deve bloquear.

## 6. Paridade Registry × Executor

Regra: todo gate inline em `validate_contracts.py` deve constar em `GATES_REGISTRY.yaml`.
Gates com `integrated_in_validate_contracts: false` são passos externos por design.
Teste obrigatório em CI: `tests/pipeline_gates/test_gate_registry_parity.py`.

## 7. Compilador Canônico de IR

**Compilador único**: `scripts/compile/compile_source_graph.py` é o único ponto de entrada autorizado para produzir a IR (Intermediate Representation) consumida pelos geradores downstream. Nenhum outro script deve ler `contracts/` para emitir IR.

**Inputs declarados** (por módulo):
- `contracts/openapi/paths/<module>.yaml` (derivado soberano do source master em `docs/hbtrack/modulos/<module>/graph/openapi_paths.yaml`)
- `contracts/schemas/<module>/*.schema.json`
- `docs/_canon/MODULE_REGISTRY.yaml` (fonte de taxonomia)
- `docs/hbtrack/modulos/<module>/graph/module_manifest.yaml`

**Outputs canônicos** em `generated/source_graph/<module>/`:
- `<module>.bundle.yaml` — manifest com inputs + compiler version + SHA-256 por input
- `<module>.openapi_contract_view.yaml` — operações com operation_id, method, path, runtime_handler_ref, use_case_ref, roles_allowed
- `<module>.schema_contract_view.yaml` — visão normalizada dos schemas
- `impact_report.json` — diff de cobertura e mudanças relativas à última compilação

**Determinismo**: mesmo conjunto de inputs (verificado via SHA-256) deve produzir outputs byte-identicos. Re-execução sem alteração de inputs é vacuous-true.

**Consumo downstream**: os geradores de código (`scripts/generate/backend_codegen.py`, e futuramente `frontend_contract_codegen.py`, `db_projection_codegen.py`, `test_codegen.py`) consomem **exclusivamente** a IR em `generated/source_graph/`. Ler contratos brutos (`contracts/openapi/`, `contracts/schemas/`) fora do compilador é violação arquitetural.

**Ordem canônica de geração**:
```
contracts/ (SSOT)
    ↓ compile_source_graph.py
generated/source_graph/ (IR)
    ↓ consumida por
backend_codegen.py · frontend_contract_codegen.py · db_projection_codegen.py · test_codegen.py
    ↓ produzem
src/<module>/generated/ · frontend/src/generated/ · generated/db_candidates/ · tests/generated/
    ↓ revisão humana para domínio/UX/banco
    ↓ materialização final
```

**Regeneração manual autorizada**: `python3 scripts/compile/compile_source_graph.py --all` ou `--module <mod>`. Após rodar, validar via `hb artifact generated/source_graph/<module>/<module>.bundle.yaml`.

Estado apurado 2026-03-23 (FASE 1):

| Gate | Decisão |
|------|---------|
| `SPECTRAL_LINTING_GATE` | Adicionado ao registry (order 13B) |
| `SURFACE_PROMOTION_COHERENCE_GATE` | Adicionado ao registry (order 20B1) |
| `SCOPE_BOUNDARY_GATE` | `integrated_in_validate_contracts: false` — passo pré-contrato externo |
| `ARCH_DECISION_PRESENCE_GATE` | `status: deferred` — implementar quando priorizado |
| `FRONTEND_CONTRACT_GATE` | `status: active` — valida frontend real contra stack, branding, shell, auth e navegação |

## 8. Protocolos Pós-Merge (§26)

**P2**: path é soberano; grep é auxiliar.
**P3**: `main` protegido; handoff via `chore/<task>` + PR.
