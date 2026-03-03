---
name: ar-plan-dryrun-collision-policy
description: Aplica a política determinística para E_AR_COLLISION e DRY-FORCE no hb plan; define quando usar --force vs --skip-existing vs bloquear.
target: vscode
---

# Skill — Arquiteto: Dry-run e colisões (E_AR_COLLISION)

Objetivo
- Padronizar o que fazer quando `hb plan --dry-run` colide com AR existente.
- Evitar replanejamento errado e reduzir tempo perdido repetindo runs.

Evidência operacional (comportamento real do CLI)
- Sucesso com `--dry-run --force` mostra: "DRY-FORCE: AR existente seria sobrescrito" e "Todas as validações passaram."
- Falha sem `--force` mostra: `E_AR_COLLISION` e opções: `--force`, `--skip-existing`, `--dry-run`.

Regra determinística
1) Default (preferido): `--dry-run` sem side effects.
2) Se ocorrer `E_AR_COLLISION`:
- Se a intenção for REGERAR a AR a partir do plano (ex.: correção do plano/SSOT) -> usar `--dry-run --force`.
- Se a intenção for respeitar a AR já materializada (não alterar) -> usar `--dry-run --skip-existing`.
- Se houver dúvida sobre qual AR é a canônica (ex.: divergência entre Kanban/Backlog/Batch/AR em disco) -> BLOQUEAR (exit 4) e pedir intervenção humana.

Checklist (execução)
- Rodar: `python scripts/run/hb_cli.py plan <plan_json_path> --dry-run`
- Se `E_AR_COLLISION`:
  - Decidir `--force` vs `--skip-existing` conforme regra acima
  - Repetir o dry-run com o flag escolhido
- Registrar no handoff:
  - `dry_run_exit_code`
  - `collision_policy: FORCE|SKIP|BLOCKED`
  - AR id(s) impactadas

Saída obrigatória
- Nota em `_reports/ARQUITETO.md` explicando a escolha (FORCE/SKIP/BLOCKED) e citando o erro/saída observada.