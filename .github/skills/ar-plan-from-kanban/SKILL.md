---
name: ar-plan-from-kanban
description: Gera Plan JSON(s) somente para AR-TRAIN existentes e liberadas pelo Kanban, respeitando Batch Plan + dependências do Backlog, e prepara o dry-run.
target: vscode
---

# Skill — Arquiteto: Planos a partir de Kanban/Backlog/Batch

Objetivo
- Converter estado operacional (Kanban) + dependências (AR_BACKLOG) + marcos/ordem macro (ROADMAP, quando aplicável) em Plan JSON(s) válidos e prontos para `hb plan --dry-run`.

Autoridade (SSOT)
- `docs/hbtrack/Hb Track Kanban.md` (ordem/estado operacional)
- `docs/hbtrack/modulos/treinos/AR_BACKLOG_TRAINING.md` (dependências + AR-TRAIN permitidas)
- `docs/hbtrack/modulos/treinos/TRAINING_ROADMAP.md` (marcos/ordem macro; quando aplicável)
- `docs/_canon/contratos/ar_contract.schema.json` (validação do plan JSON)
- `docs/_canon/specs/GATES_REGISTRY.yaml` (gates referenciáveis)

Entradas mínimas exigidas (fail-fast)
- Qual batch alvo (ex.: “Batch 2”) OU lista de ARs READY no Kanban.
Se não houver -> RESULT=BLOCKED_INPUT (exit 4).

Regras binárias (anti-alucinação)
1) EXECUÇÃO (permitido)
- Somente criar planos para AR-TRAIN-* que EXISTEM no `AR_BACKLOG_TRAINING.md`.
- Somente se o Kanban liberar como executável (ex.: `READY`).
2) GOVERNANÇA (bloquear)
- Se a necessidade não tiver AR-TRAIN/IDs catalogados em SSOT/backlog -> BLOCKED_INPUT (exit 4).
- Não inventar task no plan.

Procedimento (checklist determinístico)
1) Rodar SSOT refresh:
- `python scripts/ssot/gen_docs_ssot.py`
2) Ler Kanban e selecionar apenas ARs `READY` do batch alvo.
3) Validar dependências declaradas no Kanban/backlog:
- Se AR depende de outra que não está ✅ VERIFICADO -> BLOQUEAR (exit 4).
4) Para cada AR selecionada:
- Criar `docs/_canon/planos/<nome>.json` com `plan.version` = schema_version.
- Garantir tasks[].id único `^[0-9]{3}$`.
- Incluir `write_scope` em tarefas que tocam produto.
- Incluir `validation_command` não-trivial (comportamental).
5) Dry-run obrigatório (um por plano):
- `python scripts/run/hb_cli.py plan <plan_json_path> --dry-run`

Saídas obrigatórias
- `docs/_canon/planos/<nome>.json` (um por AR ou por conjunto, conforme seu padrão)
- `_reports/ARQUITETO.yaml` (preenchido via skill `ar-handoff-writer`)

Gates a mencionar quando relevantes (não inventar)
- `PLANS_AR_SYNC`
- `RETRY_LIMIT_GATE`
- `DOC_SCHEMA_ROLLBACK_SAFE`
