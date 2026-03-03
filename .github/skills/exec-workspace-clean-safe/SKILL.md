---
name: exec-workspace-clean-safe
description: Executor: limpar workspace com segurança (sem comandos destrutivos) antes de passar ao Testador; garante tracked-unstaged vazio.
target: vscode
---

# Skill — EXECUTOR: Workspace Clean (Seguro)

Objetivo
- Garantir que o verify não vai falhar por `E_VERIFY_DIRTY_WORKSPACE`.
- Fazer limpeza segura SEM comandos destrutivos.

Definição de "workspace sujo" (para verify)
- `git diff --name-only` NÃO vazio (tracked-unstaged)

Comandos proibidos (hard fail)
- `git restore` (qualquer forma)
- `git reset --hard`
- `git checkout -- .`
- `git clean -fd*`
- `git stash -u`

Procedimento seguro (copiar e rodar)
1) Snapshot (prova do estado):
- `cd "C:\HB TRACK"`
- `git diff --cached --name-only > _tmp_staged_before.txt`
- `git diff --name-only > _tmp_unstaged_before.txt`

2) Remover apenas temporários NÃO rastreados (manual/Explorer ou comando específico do seu ambiente).
Se for usar comando, use apenas remoção explícita de diretórios de cache conhecidos (sem glob agressivo).
Exemplos típicos (faça manualmente se tiver dúvida):
- `__pycache__/`
- `.pytest_cache/`
- `.mypy_cache/`
- `.ruff_cache/`
- `_tmp/`
- `_scratch/`

3) Resolver tracked-unstaged um a um (sem restore global):
- Verificar quais arquivos estão em `git diff --name-only`.
Para cada arquivo:
  a) Se pertence ao trabalho e deve ser commitado -> `git add "<path_exato>"`
  b) Se NÃO pertence ao trabalho -> `git checkout -- "<path_exato>"`
  c) Se houver dúvida -> STOP e escalar (não arriscar)

4) Prova final:
- `git diff --name-only`
DEVE estar vazio.

5) Prova de não-regressão do staged:
- `git diff --cached --name-only`
Comparar com `_tmp_staged_before.txt` (não deve ter "perdido" staged do trabalho).

Regra de passagem para Testador
- Se `Workspace Clean: False` aparecer em `executor_main.log` (como no seu exemplo AR_177), NÃO passar para Testador.
Rodar esta skill e repetir `hb report` se necessário.