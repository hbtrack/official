---
task_type: implementation_execution
version: "1.0.0"
status: active
---

# hb_implementer — Worker de Execução de Implementação

## Pré-requisitos obrigatórios

1. `hb verify --task-type implementation_execution --module <module> --approved-plan-path <path>` executado com sucesso.
2. O plano aprovado existe no path informado.
3. O worktree está limpo antes de qualquer edição.
4. Os arquivos permitidos/proibidos já foram carregados da sessão/estado.

## Input esperado

- `module`
- `approved_plan_path`
- `allowed_files`
- `forbidden_files`
- `decision_ids_affected`
- `pr_sequence_step`

## Saídas obrigatórias

- `_reports/implementation_flow/current_state.json`
- `_reports/implementation_flow/plan_to_diff_trace.json`
- `_reports/implementation_flow/implementation_evidence_pack.json`

## Regras operacionais

- Ler o plano aprovado antes de alterar qualquer arquivo.
- Trabalhar apenas dentro de `allowed_files`.
- Não tocar arquivos listados em `forbidden_files`.
- Não alterar canon para “fazer passar”.
- Não declarar PASS sem `pr_url` remoto presente no evidence pack.
