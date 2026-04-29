---
task_type: adversarial_test_execution
version: "1.0.0"
status: active
---

# hb_adversarial_tester — Worker de Validação Adversarial Pós-PR

## Pré-requisitos obrigatórios

1. `hb verify --task-type adversarial_test_execution --module <module> --pr-url <url> --implementation-state-path <path>` executado com sucesso.
2. O PR remoto já existe.
3. O `implementation_evidence_pack.json` existe e referencia o mesmo `pr_url`.
4. O `current_state.json` está no mínimo em `IMPLEMENTATION_PR_OPENED`.

## Input esperado

- `module`
- `pr_url`
- `approved_plan_path`
- `implementation_state_path`
- `implementation_evidence_pack_path`
- `decision_ids_affected`

## Saídas obrigatórias

- `_reports/implementation_flow/adversarial_report.json`
- `_reports/implementation_flow/negative_test_manifest.json`

## Regras operacionais

- Operar apenas após PR remoto aberto.
- Não corrigir runtime.
- Não relaxar contrato, teste ou gate.
- Não aprovar o próprio output como prova suficiente.
