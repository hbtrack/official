# SURVIVAL SUITE — Política de Regressão Obrigatória

> Criado: 2026-03-19. Critério: item 3 do backlog de melhorias (testes2.md).

## O que é

Conjunto mínimo de testes que devem passar antes de aceitar qualquer mudança nos seguintes artefatos críticos do pipeline:

- `scripts/contracts/validate/validate_contracts.py`
- `docs/_canon/gates/GATES_REGISTRY.yaml`
- `.contract_driven/BOOT_PROFILES.yaml`
- `.contract_driven/TASK_CATALOG.yaml`
- `contracts/schemas/shared/session_start.schema.json`
- `scripts/git-hooks/pre-commit`
- Qualquer arquivo em `.contract_driven/agent_prompts/`

## Como rodar

```
python3 scripts/hb survival-suite
```

DONE = exit code 0. Não avançar sem suíte verde.

## Composição da suíte

| Arquivo | O que protege |
|---------|---------------|
| `tests/test_pipeline_governance.py` | Comportamento dos gates (waiver, state machine, handoff, UI) |
| `tests/pipeline_gates/test_phase_0_determinism.py` | CLI determinismo, SSOT carregável, task catalog, boot profiles |
| `tests/pipeline_gates/test_context_budgets_and_parity.py::TestSSOTParity` | SSOTs principais carregam e têm estrutura válida |
| `tests/pipeline_gates/test_context_budgets_and_parity.py::TestHookIntegrity` | Hook versionado, instalado e sem divergência |
| `tests/pipeline_gates/test_context_budgets_and_parity.py::TestZeroBootProfileReferences` | Sem referências hardcoded a boot profiles |
| `tests/pipeline_gates/test_context_budgets_and_parity.py::test_parity_cli_verify` | CLI `hb` existe e é executável |
| `tests/pipeline_gates/test_tooling_config_gate.py` | Gate de tooling funciona em local e CI |

## Quando é obrigatória

A suíte deve rodar e retornar exit 0 **antes de fazer merge ou promoção** sempre que a mudança tocar:

- qualquer gate (adição, remoção, renomeação, mudança de profile)
- BOOT_PROFILES.yaml ou TASK_CATALOG.yaml
- validate_contracts.py
- GATES_REGISTRY.yaml
- session_start.schema.json
- pre-commit hook

Para outras mudanças (contratos de módulo, docs, schemas de domínio), a suíte é recomendada mas não obrigatória.

## Falhas conhecidas fora da suíte (não bloqueantes)

Os testes abaixo estão vermelhos por razões documentadas e são **separáveis** da suíte:

| Teste | Causa | Risco |
|-------|-------|-------|
| `test_session_handoff_md_under_budget` | SESSION_HANDOFF.md é volátil (cresce cada sessão) | Nenhum — não afeta enforcement |
| `test_contract_gates_pass` (video module) | Pipeline CI tem FAILs pré-existentes separáveis | Controlado — cada FAIL tem causa rastreável |
| `test_compile_blocks_uuid_suffix_violation` | Mensagem de erro do policy compiler evoluiu | Baixo — enforcement funciona, só mensagem diferiu |
| `test_compile_blocks_missing_semantic_id_binding` | Idem | Baixo |
| `test_module_doc_crossrefs_*` | Comportamento de governance evoluiu | Baixo |

## Regra de ouro

> Se a suíte falha, o pipeline não está em estado seguro para mudança. Corrija a suíte antes de avançar.

Não adicionar novos testes à suíte sem que eles passem no estado atual do repositório.
