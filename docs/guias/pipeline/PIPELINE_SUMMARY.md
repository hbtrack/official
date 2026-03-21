# HB TRACK — PIPELINE SUMMARY (current execution)
> Referência rápida do pipeline executável • Atualizado: 2026-03-20

---

## Verdade operacional

- **Entrypoint local:** `scripts/hb`
- **Entrypoint de CI:** `.github/workflows/contract-gates.yml`
- **Orquestração normativa:** `.contract_driven/agent_prompts/pre_contract_orchestrator.prompt.md`
- **Executor de enforcement:** `scripts/contracts/validate/validate_contracts.py`
- **Roteamento:** `.contract_driven/TASK_CATALOG.yaml`
- **Estado local:** `_reports/session_start.json`
- **Handoff operacional:** `SESSION_HANDOFF.md`
- **Workers:** prompts especializados executados pelo mesmo agente; não há runtime confirmado de subagentes autônomos

## Sequência operacional atual

```text
BOOT
  -> ler docs/_canon/AGENT_INSTRUCTIONS.md
  -> ler SESSION_HANDOFF.md se existir
  -> identificar task_type + module

FASE 0
  -> python3 scripts/hb verify --task-type <T> --module <M>
  -> grava/atualiza _reports/session_start.json
  -> roda validate_contracts.py --stage session-start

FASE 1
  -> python3 scripts/hb check --module <M>
  -> roda validate_contracts.py --stage pre-authoring
  -> bloqueia se faltar artefato obrigatório, boundary ou decisão aberta

FASE 2
  -> ler worker prompt indicado em TASK_CATALOG.yaml
  -> criar/editar artefato canônico
  -> python3 scripts/hb artifact <path>
  -> roda validate_contracts.py --stage artifact

FASE 2.5
  -> compile_api_policy.py quando contrato/policy global mudou

FASE 3
  -> python3 scripts/contracts/validate/validate_contracts.py

FASE 4+
  -> readiness/adversarial/generate_code somente quando o task_type ou pré-condições exigirem

FECHAMENTO
  -> atualizar SESSION_HANDOFF.md
  -> opcionalmente versionar via git commit; nesse ponto o pre-commit adiciona um checkpoint extra
```

## Gates e leitura correta do PASS

- O validador completo atualmente reporta **`gates_total=51`** em [`_reports/pipeline_health.json`](/home/davis/HB-TRACK/_reports/pipeline_health.json).
- O arquivo [`_reports/contract_gates/latest.json`](/home/davis/HB-TRACK/_reports/contract_gates/latest.json) reflete o **perfil/estágio executado por último**. Em runs locais ou por estágio, vários gates podem aparecer como `SKIP_NOT_APPLICABLE`.
- Portanto:
  - **PASS local != cobertura total de CI**
  - use `pipeline_health.json` para a foto global
  - use `latest.json` para o último run efetivo

## Handoff e evidência

- O handoff operacional que o agente lê e atualiza hoje é `SESSION_HANDOFF.md`.
- O enforcement protegido que toca handoff no fluxo atual é:
  - `HANDOFF_COHERENCE_GATE` no validator
  - regra do hook `pre-commit` exigindo `SESSION_HANDOFF.md` staged quando há mudança governada
- O arquivo `contracts/schemas/shared/session_handoff.schema.json` **não deve ser lido como o validador ativo do markdown operacional**. Ele descreve um payload estruturado auxiliar e não substitui o comportamento real do enforcement protegido.

## Roteamento rápido

```text
task_type + module
  -> TASK_CATALOG.yaml resolve worker_path + profile_id + allowed_stages
  -> MODULE_REGISTRY.yaml confirma módulo/status
  -> BOOT_PROFILES.yaml classifica o contexto
  -> worker prompt especializado executa a tarefa
```

Casos principais:

- `new_contract` / `contract_revision` -> `create_openapi_contract.prompt.md`
- `new_event` -> `create_asyncapi_contract.prompt.md`
- `new_workflow` -> `create_arazzo_workflow.prompt.md`
- `new_schema` -> `create_json_schema_contract.prompt.md`
- `new_state_model` -> `create_state_model.prompt.md`
- `new_ui_contract` -> `create_ui_contract.prompt.md`
- `new_module` -> `create_module_docs.prompt.md`
- `architecture_review` -> `decision_discovery.prompt.md`
- `adversarial_analysis` -> `adversarial_analysis.prompt.md`
- `readiness_promotion` -> `readiness_promotion.prompt.md`
- `generate_code` -> `generate_code.prompt.md`

Para status ativo/congelado e estágios permitidos, consultar sempre `TASK_CATALOG.yaml`; não confiar em contagens históricas resumidas.

## Não assumir

- Não assumir "21 gates". O número atual do executor completo é maior.
- Não assumir que `SESSION_HANDOFF.md` é validado por schema JSON no caminho principal.
- Não assumir runtime de subagentes com spawn autônomo.
- Não assumir que commit é o que faz os gates rodarem; os gates já rodam via `hb` e `validate_contracts.py`. O commit só adiciona o checkpoint do hook.

## Arquivos de verdade

- [`scripts/hb`](/home/davis/HB-TRACK/scripts/hb)
- [`scripts/contracts/validate/validate_contracts.py`](/home/davis/HB-TRACK/scripts/contracts/validate/validate_contracts.py)
- [`.contract_driven/TASK_CATALOG.yaml`](/home/davis/HB-TRACK/.contract_driven/TASK_CATALOG.yaml)
- [`.contract_driven/BOOT_PROFILES.yaml`](/home/davis/HB-TRACK/.contract_driven/BOOT_PROFILES.yaml)
- [`docs/_canon/MODULE_REGISTRY.yaml`](/home/davis/HB-TRACK/docs/_canon/MODULE_REGISTRY.yaml)
- [`docs/_canon/gates/GATES_REGISTRY.yaml`](/home/davis/HB-TRACK/docs/_canon/gates/GATES_REGISTRY.yaml)
- [`_reports/pipeline_health.json`](/home/davis/HB-TRACK/_reports/pipeline_health.json)
- [`_reports/contract_gates/latest.json`](/home/davis/HB-TRACK/_reports/contract_gates/latest.json)
