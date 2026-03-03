---
name: exec-run-report-evidence
description: Executor: executa hb report (com validation_command), valida executor_main.log e carimbo na AR, e faz staging estritamente isolado por AR.
target: vscode
---

# Skill — EXECUTOR: Report + Evidência (isolado)

Objetivo
- Executar a AR exatamente como planejada.
- Rodar `hb report` com o validation_command da AR.
- Validar que a evidência canônica foi gerada com campos obrigatórios.
- Stagear SOMENTE o conjunto mínimo permitido para a AR atual.

Inputs obrigatórios (fail-fast)
- AR_ID (ex.: 175)
- Caminho da AR: docs/hbtrack/ars/**/AR_<id>_*.md
- validation_command (texto exato na seção "Validation Command (Contrato)")

Se faltar qualquer item -> RESULT=BLOCKED_INPUT (exit 4) e parar.

Comandos (copiar e rodar)
1) (Opcional) confirmar status atual:
- `cd "C:\HB TRACK"`
- `git status --porcelain`

2) Rodar report (com o command EXATO da AR):
- `cd "C:\HB TRACK"`
- `python scripts/run/hb_cli.py report <AR_ID> "<validation_command_exato>"`

DoD (Definition of Done) — Evidência canônica
Após o report, DEVE existir:
- `docs/hbtrack/evidence/AR_<id>/executor_main.log`

E esse arquivo DEVE conter (mínimo):
- `AR_ID: <id>`
- `Command: <...>`
- `Exit Code: 0`
- `Timestamp UTC: ...+00:00`
- `Behavior Hash (exit+stdout+stderr): <hash>`
- `Git HEAD: <sha>`
- `Python Version: ...`
- `Protocol Version: ...`
- `Workspace Clean: True`  (se False -> NÃO passar para Testador; ver skill exec-workspace-clean-safe)
- `--- STDOUT ---` contendo `PASS AR_<id>`

DoD — Carimbo na AR (gerado por hb report)
A AR DEVE ter o bloco final:
- `## Carimbo de Execução (Gerado por hb report)`
Com:
- Status Executor, Comando, Exit Code, Timestamp UTC, Behavior Hash, Evidence File, Python Version

Staging (rígido) — isolado por AR atual
PROIBIDO:
- `git add .`
- `git add docs/` (amplo)
- `git add _reports/` (amplo)
- stagear `.claude/**`, `.github/agents/**`, `docs/_canon/planos/**` (não pertence à execução de 1 AR)
- stagear evidências de OUTRAS ARs

PERMITIDO (exato — apenas AR atual):
- `git add "docs/hbtrack/evidence/AR_<id>/executor_main.log"`
- `git add "docs/hbtrack/ars/**/AR_<id>_*.md"`

Opcional (somente se hb index/kanban foi atualizado e isso for parte do seu fluxo):
- `git add "docs/hbtrack/_INDEX.md"` (se mudou por comando oficial)
- `git add "docs/hbtrack/Hb Track Kanban.md"` (somente se a mudança for necessária e autorizada no seu processo)

Checklist de prova (antes de handoff)
- `git diff --cached --name-only`
Regra: a lista staged deve conter APENAS os arquivos permitidos acima.
Se aparecer qualquer coisa fora -> `git restore --staged <path_exato>` e repetir o checklist.

Output (disco, não commit)
- Escrever `_reports/EXECUTOR.md` com: AR_ID, exit code, evidence_path, patch_summary, next action.