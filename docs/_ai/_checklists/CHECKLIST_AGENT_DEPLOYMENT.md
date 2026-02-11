# CHECKLIST_AGENT_DEPLOYMENT.md

## Descrição
Checklist pré-deployment: validar que agent e scripts estão prontos para operar em produção/staging.

---

## Pré-Execução (SEMPRE fazer antes de agent ir ao vivo)

### Environment Validation
- [ ] PowerShell 5.1 (ou superior)
  ```powershell
  $PSVersionTable.PSVersion.Major -eq 5
  ```
- [ ] Python 3.11+ (backend)
  ```powershell
  python --version  # expect "Python 3.11.x"
  ```
- [ ] Venv existe e é funcional
  ```powershell
  Test-Path "Hb Track - Backend\venv\Scripts\python.exe"
  ```
- [ ] Dependências instaladas (pip list)
  ```powershell
  pip list | sls "sqlalchemy|alembic|pydantic"
  ```

### Repository Validation
- [ ] Git repo limpo (no uncommitted changes exceto allowed)
  ```powershell
  git status --porcelain  # expect empty ou only expected files
  ```
- [ ] Remote origin configured
  ```powershell
  git remote -v | sls origin
  ```
- [ ] Branch é main/dev (não detached HEAD)
  ```powershell
  git rev-parse --abbrev-ref HEAD
  ```

### Scripts Validation
- [ ] Todos scripts approved estão presentes + executable
  ```powershell
  Test-Path "scripts\*.ps1"  # spot check alguns chave-scripts
  ```
- [ ] Schema.sql existe (gerado recentemente)
  ```powershell
  Test-Path "Hb Track - Backend\docs\_generated\schema.sql"
  $age = (Get-Date) - (Get-Item "...\schema.sql").LastWriteTime
  # age < 24 horas is good
  ```

### Baseline Validation
- [ ] Baseline.json NÃO é commitado (acidentalmente)
  ```powershell
  git ls-files | sls "baseline"  # expect nothing
  ```
- [ ] `.gitignore` inclui `.hb_guard/`
  ```powershell
  Select-String ".hb_guard" .gitignore
  ```

### Docs Validation
- [ ] Canon docs acessíveis (nenhum link quebrado)
  ```powershell
  Test-Path "docs\_canon\00_START_HERE.md"
  Test-Path "docs\_canon\08_APPROVED_COMMANDS.md"
  ```
- [ ] SSOT artifacts existem
  ```powershell
  Test-Path "docs\_generated\openapi.json"
  Test-Path "docs\_generated\schema.sql"
  ```

---

## Critério de Go/No-Go

### Go (Proceed)
- ✅ PowerShell 5.1
- ✅ Python 3.11+
- ✅ Venv funcional + deps installed
- ✅ Git repo limpo
- ✅ Scripts presentes + baseline not committed
- ✅ Canon docs accessible

### No-Go (Wait, Fix)
- ❌ PowerShell versão errada → upgrade/downgrade
- ❌ Python versão errada → criar novo venv
- ❌ Venv corrompido → deletar + recreate
- ❌ Git dirty → commit/stash before proceeding
- ❌ Baseline committed → read GUARDRAIL_POLICY_BASELINE.md

---

## TODO
- [ ] Criar script automatizado de pré-flight check
- [ ] Adicionar timeout para cada check (some can hang)
- [ ] Criar rollback automation se qualquer check falha
