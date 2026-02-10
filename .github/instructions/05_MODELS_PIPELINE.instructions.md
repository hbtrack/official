---
description: Carregar quando eu pedir para varrer, criar, corrigir ou validar SQLAlchemy models a partir do SSOT (docs/_generated/schema.sql) usando o gate (guard → parity → requirements) e/ou models_batch.ps1. Objetivo: execução determinística, fail-fast, repo limpo, sem arquivos temporários, e sem travar o guard.
applyTo: "**/scripts/models_batch.ps1,**/scripts/models_autogen_gate.ps1,**/scripts/parity_gate.ps1,**/scripts/agent_guard.py,**/scripts/model_requirements.py,**/app/models/**/*.py,**/.hb_guard/baseline.json,**/docs/_generated/**,**/docs/_canon/**"
---
# 05 — Models Pipeline (SSOT → Gate) — FAIL-FAST + Guard-Safe

Contexto: HB Track (handebol). Este documento governa SOMENTE o fluxo de integridade estrutural Model↔DB.

## Regras inegociáveis
1) FAIL-FAST: no primeiro erro (exit != 0), PARE e reporte:
   - comando executado
   - últimas ~60 linhas do output
   - $LASTEXITCODE
   - git status --porcelain
   Não fazer tentativa-e-erro.

2) Repo limpo: antes de qualquer execução, git status --porcelain DEVE estar vazio.
   Se não estiver: ABORTAR.

3) Proibido criar arquivos temporários no repo:
   - .tmp_*.ps1, temp.txt, backup.sql, test_output.json, etc.
   Se precisar de script auxiliar: use um diretório fora do repo (ex: C:\Temp) OU apenas comandos no terminal.

4) SSOT e Gate:
   - SSOT: docs/_generated/schema.sql (gerado por C:\HB TRACK\scripts\inv.ps1 refresh)
   - Gate: scripts/models_autogen_gate.ps1
   - Exit codes canônicos:
     0 sucesso | 1 crash | 2 parity | 3 guard | 4 requirements

5) Artefatos gerados NÃO entram em PR (a menos que explicitamente solicitado):
   - docs/_generated/* (backend e repo root)
   Se forem modificados, devem ser revertidos no final.

## Pipeline canônico: 1 tabela por vez (modo fix)
Sempre seguir EXATAMENTE esta ordem para a tabela <T>.

### STEP 0 — Entrar no backend root e validar repo limpo
```powershell
Set-Location "C:\HB TRACK\Hb Track - Backend"
git status --porcelain
````

Se houver saída: ABORT.

### STEP 1 — (Opcional) SSOT refresh (somente se solicitado)

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "C:\HB TRACK\scripts\inv.ps1" refresh
$LASTEXITCODE
```

Se exit != 0: ABORT.

### STEP 2 — Rodar gate para <T>

```powershell
.\scripts\models_autogen_gate.ps1 -Table "<T>" -Profile strict
$LASTEXITCODE
```

* Exit 0: OK (passou)
* Exit 2/3/4: ABORTAR e reportar (sem “tentar consertar” automaticamente)

### STEP 3 — Commit do model (somente se gate=0 e houver mudança real)

```powershell
git status --porcelain
git diff --name-only
```

Se houver mudança em app/models relacionada a <T>:

```powershell
git add app/models
git commit -m "fix(models): autogen + strict pass for <T>"
```

Se não houver mudança no model: não commitar model.

### STEP 4 — Limpar artefatos gerados (sempre)

Reverter alterações de docs/_generated (backend e repo root):

```powershell
git restore -- `
  "docs/_generated/alembic_state.txt" `
  "docs/_generated/manifest.json" `
  "docs/_generated/parity_report.json" `
  "docs/_generated/schema.sql"

git restore -- `
  "..\docs/_generated/alembic_state.txt" `
  "..\docs/_generated/manifest.json" `
  "..\docs/_generated/schema.sql" `
  "..\docs/_generated/trd_training_permissions_report.txt"

git status --porcelain
```

Se ainda houver sujeira: ABORT.

### STEP 5 — Snapshot baseline (para não travar o guard no próximo passo)

Quando: após commit do model (se houve mudança).
Comando:

```powershell
& ".\venv\Scripts\python.exe" scripts\agent_guard.py snapshot `
  --root "." `
  --out ".hb_guard/baseline.json" `
  --exclude "venv,.venv,__pycache__,.pytest_cache,docs\_generated"
```

Commit baseline:

```powershell
git add -f .hb_guard/baseline.json
git commit -m "chore(guard): refresh baseline after model change (<T>)"
```

### STEP 6 — Confirmar repo limpo e só então avançar

```powershell
git status --porcelain
```

Se vazio: pode ir para a próxima tabela.

## Varredura (modo scan)

Objetivo: descobrir PASS/FAIL/SKIP_NO_MODEL sem corrigir nada.

Comando:

```powershell
Set-Location "C:\HB TRACK\Hb Track - Backend"
git status --porcelain
.\scripts\models_batch.ps1 -SkipGate -SkipRefresh
$LASTEXITCODE
```

Saída esperada:

* EXIT 0
* CSV/LOG gerados no %TEMP%
* SKIP_NO_MODEL deve usar código 100 (tabelas sem model)

IMPORTANTE: varredura não deve disparar commits. Apenas reportar.

## Execução em lote (modo fix por lista)

Quando autorizado, corrigir apenas as FAIL.
Regras:

* executar 1 tabela por vez com o pipeline canônico
* parar no primeiro erro (fail-fast)

## Política de commits / PR / merge

* 1 tabela corrigida = 1 commit de model (+ 1 commit de baseline)
* push + PR em lotes pequenos (5–10 tabelas), ou quando solicitado
* sempre manter repo limpo antes de iniciar a próxima tabela

````

## Agora: criar + commit (pra não sujar a repo)

Execute exatamente:

```powershell
Set-Location "C:\HB TRACK\Hb Track - Backend"

# 1) Criar o arquivo (cole o conteúdo acima)
# (use seu editor, depois volte aqui)

# 2) Verificar alterações
git status --porcelain

# 3) Commitar
git add ".github/instructions/05_MODELS_PIPELINE.instructions.md"
git commit -m "docs(copilot): add models pipeline instructions (fail-fast + guard-safe)"

# 4) Push (na branch atual)
git push
````

## PR / Merge

* Se você estiver em branch de trabalho: `gh pr create ...` (agora você tem gh instalado)
* Se preferir browser: abrir compare e criar PR (ok também)


- `gh pr create` pronto (PowerShell), com título e corpo bons, apontando para `main`.

````powershell
Set-Location "C:\HB TRACK\Hb Track - Backend"

# (opcional) confirmar auth
gh auth status

# criar PR (base=main, head=branch atual)
gh pr create `
  --base main `
  --head (git branch --show-current) `
  --title "docs(copilot): add models pipeline instructions (fail-fast + guard-safe)" `
  --body @"
## O que mudou
- Adiciona `.github/instructions/05_MODELS_PIPELINE.instructions.md` com o fluxo canônico para:
  - varredura (scan) via `models_batch.ps1 -SkipGate`
  - correção 1-tabela-por-vez via `models_autogen_gate.ps1`
  - regras de fail-fast, repo limpo e proibição de arquivos temporários
  - rotina explícita de snapshot/commit do baseline quando houver mudança intencional

## Por quê
- Evitar “tentativa-e-erro” do agent e reduzir drift.
- Garantir execução determinística: guard → parity → requirements, com exit codes canônicos (0/1/2/3/4).
- Evitar repo suja por artefatos gerados em `docs/_generated/*`.

## Como validar
```powershell
Set-Location "C:\HB TRACK\Hb Track - Backend"
git show --name-only --stat HEAD
````
