---
target: vscode
name: test-preconditions-guard
description: Testador: valida pré-condições (AR/validation/evidence staged/workspace limpo/fase) e bloqueia com mensagem objetiva antes do hb verify.
---

# Skill — TESTADOR: Pré-condições (Guard)

Objetivo
- Impedir verify com evidência falsa, workspace sujo ou fase errada.
- Evitar `E_VERIFY_DIRTY_WORKSPACE`.

Pré-condições obrigatórias (todas verdade)
1) AR existe:
- `docs/hbtrack/ars/**/AR_<id>_*.md`

2) AR contém "Validation Command" não vazio.

3) Evidence do Executor existe:
- `docs/hbtrack/evidence/AR_<id>/executor_main.log`

4) Evidence do Executor está STAGED:
- `git diff --cached --name-only` deve conter `docs/hbtrack/evidence/AR_<id>/executor_main.log`

5) Workspace limpo (tracked-unstaged vazio):
- `git diff --name-only` deve retornar vazio
Se não estiver vazio -> BLOQUEAR.
(Seu hb verify já faz isso e retorna `E_VERIFY_DIRTY_WORKSPACE`.)

6) Fase/ordem (anti-alucinação):
- Kanban usado apenas para confirmar fase compatível (não autoriza commit).

Comandos (copiar e rodar)
- `cd "C:\HB TRACK"`
- `git diff --name-only`
- `git diff --cached --name-only`
- (opcional) abrir `docs/hbtrack/evidence/AR_<id>/executor_main.log` e confirmar `Exit Code: 0`

Se qualquer pré-condição falhar
- NÃO rodar verify.
- Preencher `_reports/TESTADOR.md` com:
  - RESULT=BLOCKED
  - Motivo objetivo (ex.: "EVIDENCE_NOT_STAGED", "DIRTY_WORKSPACE: unstaged_modified=N", "MISSING_EVIDENCE_FILE")
  - NEXT_ACTION: Executor (limpar workspace / stagear evidence) ou Arquiteto (divergência de plano)