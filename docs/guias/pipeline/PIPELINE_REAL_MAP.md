# HB TRACK — PIPELINE REAL MAP
> Mapa do fluxo executável atual • Atualizado: 2026-03-20

---

## 1. Arquitetura executada

O pipeline real é um sistema contract-driven de **orquestração por prompt + registries + gates**, não um runtime online de multiagentes autônomos.

```text
Usuário/CI
  -> scripts/hb ou workflow contract-gates.yml
  -> TASK_CATALOG + MODULE_REGISTRY + BOOT_PROFILES
  -> worker prompt especializado
  -> validate_contracts.py
  -> _reports/ + SESSION_HANDOFF.md
```

Papel de cada camada:

- `scripts/hb`: entrypoint local e controle de sessão
- `pre_contract_orchestrator.prompt.md`: orquestração normativa do pre-contract
- `TASK_CATALOG.yaml`: roteamento task -> worker/profile
- `validate_contracts.py`: enforcement por gates
- `_reports/`: estado, health, history e evidências

## 2. Etapas reais do fluxo

| Etapa | Executor real | O que entra | O que sai | Observação importante |
|---|---|---|---|---|
| Boot | agente + docs canônicos | `AGENT_INSTRUCTIONS.md`, `SESSION_HANDOFF.md` se existir | contexto base | boot real é leitura dirigida, não carregamento cego de tudo |
| Session start | `python3 scripts/hb verify --task-type <T> --module <M>` | task_type, module | `_reports/session_start.json` + gates `session-start` | valida catálogo, módulo, profile e worker |
| Pre-authoring | `python3 scripts/hb check --module <M>` | estado do módulo + repo | gates `pre-authoring` | bloqueia ausência de artefatos, adversarial pendente e boundary |
| Authoring | worker prompt do `TASK_CATALOG` | contexto filtrado do módulo | artefato canônico | worker = prompt especializado no mesmo agente |
| Artifact checkpoint | `python3 scripts/hb artifact <path>` | artefato criado | hash + stage2_artifacts + gates `artifact` | ponto real de rastreabilidade local |
| Compile | `compile_api_policy.py` quando aplicável | contrato/policy global alterado | derivados em `generated/` | condicional, não universal |
| Full validation | `python3 scripts/contracts/validate/validate_contracts.py` | repo state completo | `latest.json`, `pipeline_health.json`, `pipeline_history.jsonl` | CI usa cobertura maior que runs locais por estágio |
| Readiness/adversarial | worker específico | latest, scorecards, superfícies, backlog | promoção, relatório adversarial ou bloqueio | depende do task_type e de pré-condições |
| Handoff | agente + arquivo operacional | estado final da sessão | `SESSION_HANDOFF.md` atualizado | artefato operacional entre sessões |
| Commit | git + hook `pre-commit` | arquivos staged | commit ou bloqueio | checkpoint extra; não é o motor principal de gates |

## 3. Gates: como ler o estado atual

- O executor completo reporta `health_score` e `gates_total` atuais em `pipeline_health.json` (não usar número fixo — contagem muda com o registry).
- `latest.json` não é sinônimo de "todos os gates executaram"; ele reflete o **último profile/stage** rodado.
- Em local, isso implica:
  - `hb verify` -> subset `session-start`
  - `hb check` -> subset `pre-authoring`
  - `hb artifact` -> subset `artifact`
  - `validate_contracts.py` full -> cobertura bem maior

Em outras palavras, o pipeline é **stage-aware** e **profile-aware**. Qualquer mapa que descreva "sempre 21" ou "sempre 44" gates está fora do comportamento atual.

## 4. Handoff e estado sem ambiguidade

Estado persistente confirmado:

- `_reports/session_start.json` -> estado transacional local da sessão
- `SESSION_HANDOFF.md` -> handoff operacional lido entre sessões
- `_reports/agent_execution/latest.json` -> evidência observável das fases do agente
- `_reports/pipeline_history.jsonl` -> histórico append-only de runs

Leitura correta do handoff:

- O markdown `SESSION_HANDOFF.md` é o artefato operacional usado pelo boot, pelo hook e pelo gate de coerência.
- O schema `contracts/schemas/shared/session_handoff.schema.json` existe, mas **não deve ser interpretado como o validador ativo do markdown operacional**.
- Se você precisar saber o enforcement real de handoff hoje, olhe para:
  - `HANDOFF_COHERENCE_GATE`
  - `scripts/git-hooks/pre-commit`

## 5. Roteamento e workers

Roteamento real:

```text
task_type + module
  -> TASK_CATALOG.yaml
  -> worker_path + profile_id + allowed_stages
  -> BOOT_PROFILES.yaml classifica o contexto
  -> worker prompt executa
```

Workers importantes:

- `pre_contract_orchestrator.prompt.md`
- `decision_discovery.prompt.md`
- `create_openapi_contract.prompt.md`
- `create_asyncapi_contract.prompt.md`
- `create_json_schema_contract.prompt.md`
- `adversarial_analysis.prompt.md`
- `readiness_promotion.prompt.md`
- `generate_code.prompt.md`

O que **nao** foi confirmado:

- spawn automático de subagentes
- planner autônomo separado do catálogo
- fila, broker ou runtime distribuído de agentes
- retrieval externo ao repositório no caminho principal

## 6. Commit e close-out

O commit continua útil, mas a leitura correta é:

- `hb` + `validate_contracts.py` já executam os checkpoints principais
- o commit aciona o `pre-commit`, que adiciona verificação de staging, hashes e handoff
- logo, commit é **fechamento operacional e de versionamento**, não o mecanismo que faz o pipeline existir

## 7. Arquivos para consultar primeiro

- [`scripts/hb`](/home/davis/HB-TRACK/scripts/hb)
- [`scripts/contracts/validate/validate_contracts.py`](/home/davis/HB-TRACK/scripts/contracts/validate/validate_contracts.py)
- [`.contract_driven/TASK_CATALOG.yaml`](/home/davis/HB-TRACK/.contract_driven/TASK_CATALOG.yaml)
- [`.contract_driven/BOOT_PROFILES.yaml`](/home/davis/HB-TRACK/.contract_driven/BOOT_PROFILES.yaml)
- [`docs/_canon/MODULE_REGISTRY.yaml`](/home/davis/HB-TRACK/docs/_canon/MODULE_REGISTRY.yaml)
- [`docs/_canon/gates/GATES_REGISTRY.yaml`](/home/davis/HB-TRACK/docs/_canon/gates/GATES_REGISTRY.yaml)
- [`_reports/pipeline_health.json`](/home/davis/HB-TRACK/_reports/pipeline_health.json)
- [`_reports/contract_gates/latest.json`](/home/davis/HB-TRACK/_reports/contract_gates/latest.json)
