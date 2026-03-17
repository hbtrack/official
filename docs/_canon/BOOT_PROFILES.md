---
doc_type: canon
version: "1.1.0"
last_reviewed: "2026-03-16"
status: active
---

# BOOT_PROFILES.md

## 0. Objetivo

Definir o perfil de boot por `task_type`, a classe de leitura de cada artefato de governança
e o formato canônico do Boot Resolution Report.

## 1. Classes de leitura

| Classe | Significado | Efeito operacional |
| --- | --- | --- |
| `boot_minimo` | precisa ser lido antes de qualquer decisão do agente | ausência bloqueia a tarefa |
| `boot_condicional` | precisa ser lido quando um gatilho explícito ocorrer | ausência bloqueia apenas o fluxo aplicável |
| `gate_only` | não entra no contexto de autoria; serve para validação/bloqueio | pode ser consultado por gates ou pela fase final do orquestrador |

Regra:
- se um artefato de governança não estiver classificado aqui, o agente não pode presumir leitura;
- prompt nenhum pode promover `gate_only` a fonte substantiva;
- expansão de contexto fora do perfil deve ser justificada na evidência de boot.

## 2. Artefatos de governança do boot

| Artefato | Classe padrão | Quando carregar | Finalidade |
| --- | --- | --- | --- |
| `.contract_driven/CONTRACT_SYSTEM_LAYOUT.md` | `boot_minimo` | sempre | validar taxonomia, paths e soberania |
| `.contract_driven/CONTRACT_SYSTEM_RULES.md` | `boot_minimo` | sempre | validar precedência, bloqueios e DoD |
| `docs/_canon/CONTRACT_PIPELINE.md` | `boot_minimo` | sempre | resolver estágio atual e ordem do fluxo |
| `docs/_canon/BOOT_PROFILES.md` | `boot_minimo` | sempre | resolver o próprio perfil de boot |
| `docs/_canon/MODULE_REGISTRY.yaml` | `boot_minimo` | sempre | status, owner e superfícies esperadas do módulo |
| `docs/_canon/TOOLCHAIN_HEALTH_POLICY.md` | `boot_condicional` | tarefas que executam validação, readiness, handoff ou dependem de health-check | definir `DEGRADED`, timeout e fail-closed |
| `docs/_canon/HUMAN_INTERFACE_POLICY.md` | `boot_condicional` | sempre que o agente for comunicar algo ao humano (decisões, progresso, bloqueios) | garantir linguagem de produto, formato de decisão padronizado e vocabulário sem jargão |
| `docs/_canon/gates/GATES_REGISTRY.yaml` | `gate_only` | auditoria, validação, readiness ou handoff | registrar bloqueios oficiais e ordem dos gates |

## 3. Perfis por `task_type`

| task_type | `boot_minimo` | `boot_condicional` | `gate_only` |
| --- | --- | --- | --- |
| `new_module` | trilogia contract-driven, `CONTRACT_PIPELINE.md`, `BOOT_PROFILES.md`, `MODULE_REGISTRY.yaml`, `SYSTEM_SCOPE.md`, `MODULE_MAP.md` | ADRs do domínio, `HANDBALL_RULES_DOMAIN.md` quando houver gatilho esportivo | `GATES_REGISTRY.yaml` só se terminar em auditoria/readiness |
| `new_contract` | base mínima + `DATA_CONVENTIONS.md`, `ERROR_MODEL.md`, `SECURITY_RULES.md`, docs do módulo, contrato/surface atual | `TOOLCHAIN_HEALTH_POLICY.md`, ADRs da surface, `HANDBALL_RULES_DOMAIN.md` | `GATES_REGISTRY.yaml` |
| `contract_revision` | mesmo perfil de `new_contract` + baseline existente + `generated/resolved_policy/<module>.sync.resolved.yaml` | `TOOLCHAIN_HEALTH_POLICY.md`, manifests, ADRs específicas | `GATES_REGISTRY.yaml` |
| `new_event` | base mínima + docs do módulo + `contracts/asyncapi/asyncapi.yaml` | `HANDBALL_RULES_DOMAIN.md`, `TOOLCHAIN_HEALTH_POLICY.md` se houver validação no turno | `GATES_REGISTRY.yaml` |
| `new_workflow` | base mínima + docs do módulo + `contracts/openapi/openapi.yaml` + operationIds soberanos | ADRs de workflow, `TOOLCHAIN_HEALTH_POLICY.md` se houver validação | `GATES_REGISTRY.yaml` |
| `new_schema` | base mínima + `DATA_CONVENTIONS.md`, docs do módulo, `contracts/schemas/<module>/` | `ERROR_MODEL.md`, `TOOLCHAIN_HEALTH_POLICY.md` se houver validação | `GATES_REGISTRY.yaml` |
| `new_state_model` | base mínima + docs do módulo + `STATE_MODEL_<MODULE>.md` se existir | ADRs de lifecycle, `TOOLCHAIN_HEALTH_POLICY.md` se houver readiness | `GATES_REGISTRY.yaml` |
| `new_ui_contract` | base mínima + docs do módulo + `UI_FOUNDATIONS.md` + `DESIGN_SYSTEM.md` | `TOOLCHAIN_HEALTH_POLICY.md` se houver validação/handoff | `GATES_REGISTRY.yaml` |
| `architecture_review` | base mínima + `ARCHITECTURE_DECISION_BACKLOG.md`, `DECISION_POLICY.md`, ADRs relevantes | DSS da pasta `docs/hbtrack/decisoes/` como apoio, nunca como SSOT | `GATES_REGISTRY.yaml` quando a revisão terminar em validação |

## 4. Boot Resolution Report

O orquestrador pré-contrato deve emitir `_reports/evidence/boot_resolution_report.json` com:

```json
{
  "artifact_id": "HBTRACK_BOOT_RESOLUTION_REPORT",
  "module": "training",
  "task_type": "contract_revision",
  "profile": "contract_revision",
  "mandatory_reads": [],
  "conditional_reads": [],
  "gate_only_reads": [],
  "module_status": "implementation_ready",
  "skipped_reads": [],
  "worker_prompt": ".contract_driven/agent_prompts/create_openapi_contract.prompt.md",
  "timestamp_utc": "2026-03-16T00:00:00Z"
}
```

Regra:
- ausência de leitura obrigatória impede handoff;
- expansão de contexto deve ser justificada em `conditional_reads`.
- `gate_only_reads` não entram como contexto de autoria;
- `module_status` deve refletir `docs/_canon/MODULE_REGISTRY.yaml`.
