---
name: test-verify-triple-run
description: Testador: executa hb verify, aplica regra triple-run/hashes, escreve TESTADOR.yaml e stageia apenas context.json/result.json.
target: vscode
---

# Skill — TESTADOR: hb verify (Triple-run determinístico)

Objetivo
- Rodar `hb verify <id>`.
- Aceitar PASS apenas com 3/3 exit=0 e hash idêntico.
- Produzir e stagear APENAS evidências commitáveis do Testador.

Comando único (copiar e rodar)
- `cd "C:\HB TRACK"`
- `python scripts/run/hb_cli.py verify <AR_ID>`

Interpretação (baseado no stdout real)
PASS:
- Run 1/3 exit=0 hash=H
- Run 2/3 exit=0 hash=H
- Run 3/3 exit=0 hash=H
- `✅ SUCESSO | Consistency: OK`

FAIL — dirty workspace:
- `E_VERIFY_DIRTY_WORKSPACE` + `unstaged_modified=N`
-> RESULT=BLOCKED e parar (não insistir).

FAIL — não determinístico:
- Qualquer run exit != 0 -> REJEITADO
- exit 0 mas hashes diferentes -> REJEITADO (FLAKY_OUTPUT)

Artefatos gerados (commitáveis)
Após verify, deve existir:
- `_reports/testador/AR_<id>_<git7>/context.json`
- `_reports/testador/AR_<id>_<git7>/result.json`

Staging (rígido, exato)
PERMITIDO:
- `git add "_reports/testador/AR_<id>_<git7>/context.json"`
- `git add "_reports/testador/AR_<id>_<git7>/result.json"`

PROIBIDO:
- `git add .`
- `git add _reports/` (amplo)
- stagear ARs, Kanban, _INDEX, evidence do executor (isso é do Executor)

Output (disco, não chat)
- Sobrescrever `_reports/TESTADOR.yaml` no seu template real (cabecalho + tabela + detalhes + evidências staged + NEXT_ACTION).
- NEXT_ACTION (conforme seu padrão):
  - PASS -> humano: `hb seal <id>`
  - FAIL por consistência -> Arquiteto (AH_DIVERGENCE se aplicável)
  - FAIL técnico -> Executor
  - BLOCKED (workspace) -> Executor (workspace clean)