# PIPELINE_QUICK_REFERENCE.md
> Consulta rápida do fluxo executável • Atualizado: 2026-03-20

---

## Contrato: sequência curta correta

```text
1. Ler docs/_canon/AGENT_INSTRUCTIONS.md
2. Ler SESSION_HANDOFF.md se existir
3. Resolver task_type + module
4. python3 scripts/hb verify --task-type <T> --module <M>
5. python3 scripts/hb check --module <M>
6. Ler worker prompt do TASK_CATALOG
7. Criar/editar artefato canônico
8. python3 scripts/hb artifact <path>   (para cada artefato)
9. compile_api_policy.py                 (somente quando contrato/policy mudou)
10. python3 scripts/contracts/validate/validate_contracts.py
11. readiness/adversarial/generate_code  (somente se task/precondições exigirem)
12. Atualizar SESSION_HANDOFF.md
13. Opcionalmente: git add/git commit    (pre-commit adiciona checkpoint extra)
```

## O que cada comando realmente faz

| Comando | Papel real | Saída principal |
|---|---|---|
| `hb verify` | abre/valida sessão e roda gates `session-start` | `_reports/session_start.json` |
| `hb check` | roda gates `pre-authoring` | status de prontidão para autoria |
| `hb artifact <path>` | registra hash e roda gates `artifact` | `stage2_artifacts[]` atualizado |
| `validate_contracts.py` | roda o validator principal por profile/stage | `latest.json`, `pipeline_health.json`, `pipeline_history.jsonl` |

## Roteamento rápido

| task_type | worker principal |
|---|---|
| `new_contract`, `contract_revision` | `create_openapi_contract.prompt.md` |
| `new_event` | `create_asyncapi_contract.prompt.md` |
| `new_workflow` | `create_arazzo_workflow.prompt.md` |
| `new_schema` | `create_json_schema_contract.prompt.md` |
| `new_state_model` | `create_state_model.prompt.md` |
| `new_ui_contract` | `create_ui_contract.prompt.md` |
| `new_module` | `create_module_docs.prompt.md` |
| `architecture_review` | `decision_discovery.prompt.md` |
| `adversarial_analysis` | `adversarial_analysis.prompt.md` |
| `readiness_promotion` | `readiness_promotion.prompt.md` |
| `generate_code` | `generate_code.prompt.md` |

Se houver dúvida de status ativo/congelado, consultar `TASK_CATALOG.yaml`; não confiar em listas antigas.

## Regras de leitura correta

- Worker = prompt especializado no mesmo agente.
- `PASS` em `latest.json` pode representar um subset de gates.
- O total atual do executor completo está em `_reports/pipeline_health.json` e hoje é `51`.
- `SESSION_HANDOFF.md` é o handoff operacional atual.
- O schema `session_handoff.schema.json` não substitui o validator real do markdown.
- Auditorias `audit_*` podem carregar o worker diretamente e pular o pre-contract de autoria.

## Checagens rápidas

```bash
# estado local da sessão
cat _reports/session_start.json

# último run efetivo
cat _reports/contract_gates/latest.json

# fotografia global do validator
cat _reports/pipeline_health.json
```

## Não fazer

- Não assumir "21 gates" ou "44 gates" como contagem fixa.
- Não assumir runtime de subagentes autônomos.
- Não assumir que commit faz o validator rodar.
- Não assumir que `PRE_CONTRACT_EVIDENCE_GATE` valida o markdown `SESSION_HANDOFF.md` por schema JSON.
