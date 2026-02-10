Sim — dá pra documentar isso de forma canônica e **segura** (sem o agente “sair fazendo merge” errado). Abaixo vai um arquivo pronto para você copiar/colar como:

`docs/_canon/10_GIT_PR_MERGE_WORKFLOW.md`

Ele assume que você já tem `gh` funcionando (você tem) e que o fluxo padrão é PR → review → merge.

````markdown
# docs/_canon/10_GIT_PR_MERGE_WORKFLOW.md

| Propriedade | Valor |
|---|---|
| ID | CANON-GIT-WORKFLOW-010 |
| Status | CANÔNICO |
| Última verificação | 2026-02-09 (America/Sao_Paulo) |
| Porta de entrada | docs/_canon/00_START_HERE.md |
| Objetivo | Commit → Push → PR → Merge pelo terminal (gh + git) com segurança |
| Requer | Git + GitHub CLI (`gh`) autenticado |

# Workflow Canônico: Commit → Push → PR → Merge (Terminal)

Este documento define o fluxo para o agent operar Git/GitHub **sem tentativa-e-erro** e com **travamento de risco** (stop-on-first-failure).

## 0) Regras de segurança (NÃO NEGOCIÁVEIS)

1) Sempre executar no repositório correto:
```powershell
Set-Location "C:\HB TRACK\Hb Track - Backend"
````

2. Nunca fazer commit se houver lixo (temporários, docs/_generated não intencional).

* Antes de commitar, `git status --porcelain` deve mostrar **apenas** arquivos intencionais.

3. Parar no primeiro erro (qualquer comando com exit != 0).

* Capturar `$LASTEXITCODE` imediatamente após cada comando.

4. **Merge em main só com autorização explícita** do usuário.

* O agent pode abrir PR automaticamente, mas só faz merge quando você disser “pode mergear”.

## 1) Checklist pré-commit

```powershell
git status -sb
git status --porcelain
```

Critério:

* Branch correto (não commitar direto em main, salvo hotfix autorizado).
* Arquivos modificados = somente o escopo do trabalho.

Se aparecerem artefatos gerados que não são parte do PR, limpar:

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
```

## 2) Criar branch (se necessário)

```powershell
git switch -c fix/<nome-curto>
```

## 3) Staging e commit

### 3.1 Ver diff antes de adicionar

```powershell
git --no-pager diff --stat
git --no-pager diff
```

### 3.2 Adicionar arquivos (preciso)

```powershell
git add <paths>
```

### 3.3 Commit

```powershell
git commit -m "<tipo(escopo): mensagem>" 
```

Se hooks estiverem quebrados e você precisar seguir (evitar loops), usar:

```powershell
git commit --no-verify -m "<mensagem>"
```

(Registre no corpo do PR que foi `--no-verify` e por quê.)

## 4) Push

```powershell
git push -u origin HEAD
```

## 5) Criar PR via gh

### 5.1 PR automático (recomendado)

Puxa título/corpo do commit:

```powershell
gh pr create --base main --head HEAD --fill
```

### 5.2 PR com título e corpo

```powershell
gh pr create `
  --base main `
  --head HEAD `
  --title "<titulo>" `
  --body @"
## O que mudou
- ...

## Como validar
- ...

## Evidência
- ...
"@
```

Ver PR:

```powershell
gh pr view --web
```

## 6) Validar checks e status do PR

```powershell
gh pr status
gh pr view --json number,state,mergeable,reviewDecision,statusCheckRollup
```

## 7) Merge (SOMENTE COM AUTORIZAÇÃO EXPLÍCITA)

Quando o usuário disser “pode mergear”, usar UM dos modos:

### 7.1 Squash merge (recomendado para feature branch)

```powershell
gh pr merge --squash --delete-branch
```

### 7.2 Merge commit (quando histórico importa)

```powershell
gh pr merge --merge --delete-branch
```

### 7.3 Rebase merge (quando exigido)

```powershell
gh pr merge --rebase --delete-branch
```

## 8) Pós-merge (sincronizar main)

```powershell
git switch main
git pull
git status -sb
```

## 9) Stop-on-first-failure (padrão de execução)

Após cada comando importante:

```powershell
$ec = $LASTEXITCODE
if ($ec -ne 0) { Write-Host "ABORT: exit=$ec"; exit $ec }
```

## 10) Política: commits e PRs

* Preferir commits pequenos por intenção:

  * `fix(models): ...`
  * `chore(guard): refresh baseline ...`
  * `docs: ...`
* Baseline em commit separado.
* Docs (CHANGELOG/EXECUTIONLOG) em commit separado.

```


