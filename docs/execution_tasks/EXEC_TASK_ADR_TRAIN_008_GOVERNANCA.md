# EXEC_TASK: Automação da Governança por Artefatos Gerados

**Derivado de:** 008-ADR-TRAIN-governanca-por-artefatos
**Status:** READY TO EXECUTE
**Prioridade:** P1 (ALTA — Enforcement de política "artifacts-first")
**Estimativa:** 3-4 dias
**Assignee:** Davi + Claude (AI Assistant)

---

## 🎯 OBJETIVO EXECUTÁVEL

Automatizar o enforcement da política **"artifacts-first"** via CI/CD gates + pre-commit hooks, garantindo que documentação só seja atualizada após geração de artefatos canônicos (`schema.sql`, `openapi.json`, `alembic_state.txt`, `manifest.json`).

---

## 📋 PRÉ-REQUISITOS

### Verificações Obrigatórias (ANTES DE INICIAR)

```powershell
# ✅ CHECK 1: Scripts de gate existentes
Test-Path "Hb Track - Backend\scripts\parity_gate.ps1"
Test-Path "Hb Track - Backend\scripts\agent_guard.py"
Test-Path "Hb Track - Backend\scripts\models_autogen_gate.ps1"
# Esperado: True para todos

# ✅ CHECK 2: Artefatos gerados existem
Test-Path "Hb Track - Backend\docs\_generated\schema.sql"
Test-Path "Hb Track - Backend\docs\_generated\openapi.json"
Test-Path "docs\_generated\alembic_state.txt"
Test-Path "docs\_generated\manifest.json"
# Esperado: True para todos

# ✅ CHECK 3: GitHub Actions funcional
Test-Path ".github\workflows"
# Esperado: True

# ✅ CHECK 4: Python 3.11+
python --version
# Esperado: Python 3.11+

# ✅ CHECK 5: PowerShell 5.1+ ou 7+
$PSVersionTable.PSVersion.Major -ge 5
# Esperado: True
```

**ABORTAR SE:** qualquer check falhar. Resolver dependências antes de prosseguir.

---

## 🔄 FASES DE EXECUÇÃO

### FASE 1: Artifact Freshness Validator (1 dia)

#### Entregável 1.1: Script de validação de timestamps

**Arquivo:** `scripts/validate_artifact_freshness.py`

```python
#!/usr/bin/env python3
"""
Valida que artefatos _generated/ são mais recentes que documentação derivada.

Regra: Se doc foi modificado após artifacts, FAIL (drift).
Exit codes:
- 0: Artifacts frescos (doc <= artifacts timestamp)
- 4: Artifacts stale (doc > artifacts timestamp)
- 1: Erro interno (arquivo não encontrado, etc.)
"""
import sys
from pathlib import Path
from datetime import datetime

# Mapeamento: documento → artefatos que devem estar frescos
DOC_TO_ARTIFACTS = {
    'docs/02_modulos/training/INVARIANTS/INVARIANTS_TRAINING.md': [
        'Hb Track - Backend/docs/_generated/schema.sql',
        'Hb Track - Backend/docs/_generated/openapi.json',
    ],
    'docs/02_modulos/training/TRD_TRAINING.md': [
        'Hb Track - Backend/docs/_generated/openapi.json',
        'Hb Track - Backend/docs/_generated/schema.sql',
    ],
    'docs/02_modulos/training/PRD_BASELINE_ASIS_TRAINING.md': [
        'Hb Track - Backend/docs/_generated/manifest.json',
    ],
}

def get_mtime(path: Path) -> datetime:
    """Retorna timestamp de modificação do arquivo."""
    if not path.exists():
        print(f"❌ Arquivo não encontrado: {path}")
        sys.exit(1)
    return datetime.fromtimestamp(path.stat().st_mtime)

def validate_freshness() -> bool:
    """
    Valida que todos os artefatos são mais recentes que docs derivadas.
    Retorna True se frescos, False se stale.
    """
    all_fresh = True

    for doc_path, artifact_paths in DOC_TO_ARTIFACTS.items():
        doc = Path(doc_path)
        if not doc.exists():
            continue  # Doc não existe, skip

        doc_mtime = get_mtime(doc)

        for artifact_path in artifact_paths:
            artifact = Path(artifact_path)
            artifact_mtime = get_mtime(artifact)

            # Regra: artifact deve ser >= doc (tolerância de 1 segundo por arredondamento)
            if artifact_mtime < doc_mtime:
                print(f"❌ STALE: {doc.name} modificado após {artifact.name}")
                print(f"   Doc mtime:      {doc_mtime}")
                print(f"   Artifact mtime: {artifact_mtime}")
                print(f"   Δt: {(doc_mtime - artifact_mtime).total_seconds():.1f}s")
                all_fresh = False
            else:
                print(f"✅ FRESH: {doc.name} ← {artifact.name}")

    return all_fresh

def main():
    print("🔍 Validando freshness de artefatos...\n")

    if validate_freshness():
        print("\n✅ Todos os artefatos estão frescos (docs ≤ artifacts)")
        sys.exit(0)
    else:
        print("\n❌ Artefatos stale detectados!")
        print("   Ação: Rodar parity_scan.ps1 ou regenerar artifacts antes de commitar docs")
        sys.exit(4)

if __name__ == '__main__':
    main()
```

**Testes de aceitação:**
```powershell
# TEST 1.1.1: Artifacts frescos (docs não modificadas)
python scripts/validate_artifact_freshness.py
$LASTEXITCODE -eq 0  # Sucesso

# TEST 1.1.2: Artifacts stale (simular doc modificada após artifact)
# Tocar doc para torná-la mais recente
(Get-Item "docs\02_modulos\training\INVARIANTS\INVARIANTS_TRAINING.md").LastWriteTime = Get-Date
python scripts/validate_artifact_freshness.py
$LASTEXITCODE -eq 4  # Stale detectado

# Restaurar timestamp original (git checkout)
git checkout "docs\02_modulos\training\INVARIANTS\INVARIANTS_TRAINING.md"
```

**Critério de DONE:**
- ✅ Script valida timestamps de docs vs artifacts
- ✅ Exit code 0 (fresh) vs 4 (stale) correto
- ✅ Output legível com Δt em segundos
- ✅ Mapeamento DOC_TO_ARTIFACTS completo (TRD, PRD, INVARIANTS)

---

### FASE 2: Pre-commit Hook (0.5 dias)

#### Entregável 2.1: Git pre-commit hook

**Arquivo:** `scripts/pre-commit-artifacts.sh`

```bash
#!/bin/bash
# Pre-commit hook: bloqueia commit de docs se artifacts stale

set -e

echo "🔍 [PRE-COMMIT] Validando freshness de artefatos..."

# Detectar docs staged para commit
STAGED_DOCS=$(git diff --cached --name-only | grep -E '^docs/.*\.(md|json)$' || true)

if [ -z "$STAGED_DOCS" ]; then
    echo "✅ Nenhuma doc staged, skipping artifact validation"
    exit 0
fi

echo "📄 Docs staged para commit:"
echo "$STAGED_DOCS" | sed 's/^/   - /'

# Executar validator
python scripts/validate_artifact_freshness.py

if [ $? -eq 4 ]; then
    echo ""
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║ ❌ COMMIT BLOQUEADO: Artifacts stale                       ║"
    echo "╠════════════════════════════════════════════════════════════╣"
    echo "║ Você está tentando commitar documentação que foi          ║"
    echo "║ modificada APÓS os artifacts gerados.                      ║"
    echo "║                                                            ║"
    echo "║ Ações requeridas:                                          ║"
    echo "║ 1. Rodar: powershell scripts/parity_scan.ps1              ║"
    echo "║ 2. Stage artifacts: git add docs/_generated/              ║"
    echo "║ 3. Retentar commit                                         ║"
    echo "║                                                            ║"
    echo "║ Ou bypass (NÃO recomendado): git commit --no-verify      ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    exit 1
fi

echo "✅ Artifacts frescos, commit permitido"
exit 0
```

**Instalação:**
```powershell
# Copiar hook para .git/hooks/
Copy-Item "scripts\pre-commit-artifacts.sh" ".git\hooks\pre-commit"

# Tornar executável (Linux/macOS)
chmod +x .git/hooks/pre-commit

# Windows: garantir que Git Bash execute (não requer chmod)
```

**Testes de aceitação:**
```powershell
# TEST 2.1.1: Commit sem docs staged → hook passa
git add "Hb Track - Backend\app\services\*.py"
git commit -m "Update service"
# Esperado: "Nenhuma doc staged, skipping" + commit sucede

# TEST 2.1.2: Commit com doc stale → hook bloqueia
(Get-Item "docs\02_modulos\training\INVARIANTS\INVARIANTS_TRAINING.md").LastWriteTime = Get-Date
git add "docs\02_modulos\training\INVARIANTS\INVARIANTS_TRAINING.md"
git commit -m "Update invariants"
# Esperado: "COMMIT BLOQUEADO" + exit 1

# TEST 2.1.3: Bypass com --no-verify
git commit -m "Update invariants" --no-verify
# Esperado: commit sucede (bypass)

# Cleanup
git reset HEAD~1  # Desfazer commit de teste
git checkout "docs\02_modulos\training\INVARIANTS\INVARIANTS_TRAINING.md"
```

**Critério de DONE:**
- ✅ Hook instalado em `.git/hooks/pre-commit`
- ✅ Detecta docs staged via `git diff --cached`
- ✅ Chama `validate_artifact_freshness.py`
- ✅ Exit 1 bloqueia commit (com mensagem de ajuda)
- ✅ Bypass via `--no-verify` funciona

---

### FASE 3: CI/CD GitHub Actions Workflow (1 dia)

#### Entregável 3.1: Workflow de validação de artifacts

**Arquivo:** `.github/workflows/validate-artifacts.yml`

```yaml
name: Validate Artifacts Freshness

on:
  pull_request:
    paths:
      - 'docs/**/*.md'
      - 'docs/**/*.json'
      - 'Hb Track - Backend/docs/_generated/**'

jobs:
  validate-artifacts:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v3
        with:
          fetch-depth: 0  # Necessário para comparar commits

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Validate artifact freshness
        id: validate
        run: |
          python scripts/validate_artifact_freshness.py
        continue-on-error: true

      - name: Report results
        if: steps.validate.outcome == 'failure'
        run: |
          echo "::error::❌ Artifacts stale detectados!"
          echo "::error::Documentação foi modificada após artifacts gerados."
          echo "::error::Ação: Rodar parity_scan.ps1 e commitar artifacts atualizados."
          exit 1

      - name: Success message
        if: steps.validate.outcome == 'success'
        run: |
          echo "✅ Artifacts frescos — documentação está sincronizada"

  validate-parity:
    runs-on: ubuntu-latest
    if: contains(github.event.pull_request.changed_files, 'app/models/')

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r "Hb Track - Backend/requirements.txt"

      - name: Run parity gate
        run: |
          cd "Hb Track - Backend"
          python scripts/parity_classify.py --check-only
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_db

      - name: Report parity violations
        if: failure()
        run: |
          echo "::error::❌ Parity gate falhou!"
          echo "::error::Divergências estruturais detectadas entre models e DB."
          echo "::error::Ver docs/_generated/parity_report.json para detalhes."
          exit 1
```

**Testes de aceitação:**
```powershell
# TEST 3.1.1: PR com doc stale → workflow falha
# (Criar PR de teste no GitHub com doc modificada após artifact)
# Esperado: workflow "Validate Artifacts Freshness" falha com exit 1

# TEST 3.1.2: PR com artifacts frescos → workflow passa
# (Criar PR com doc + artifacts atualizados no mesmo commit)
# Esperado: workflow passa com exit 0

# TEST 3.1.3: PR com models modificados → parity gate roda
# (Criar PR modificando app/models/*.py)
# Esperado: job "validate-parity" dispara e roda parity_classify.py
```

**Critério de DONE:**
- ✅ Workflow dispara em PRs que tocam docs/ ou _generated/
- ✅ Job `validate-artifacts` chama `validate_artifact_freshness.py`
- ✅ Job `validate-parity` roda quando models/ modificados
- ✅ Falhas geram mensagens de erro explicativas (`::error::`)
- ✅ Workflow passa apenas se artifacts frescos + parity OK

---

### FASE 4: Documentação do Fluxo de Governança (0.5 dias)

#### Entregável 4.1: Workflow guide

**Arquivo:** `docs/workflows/artifact_governance_workflow.md`

```markdown
# Workflow de Governança por Artefatos

## Visão Geral

Este documento descreve o fluxo obrigatório para atualização de documentação no HB Track, garantindo alinhamento entre código, artefatos gerados e documentação derivada.

## Princípio: Artifacts-First

**Regra de Ouro:** Documentação só é atualizada APÓS geração de artefatos canônicos.

```
┌─────────────────────────────────────────────────────────────────┐
│                   FLUXO DE GOVERNANÇA                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. Desenvolvedor altera CÓDIGO                                │
│     ├─ app/models/*.py (SQLAlchemy models)                     │
│     ├─ app/routers/*.py (FastAPI endpoints)                    │
│     └─ db/alembic/versions/*.py (migrations)                   │
│                                                                 │
│  2. Roda GERAÇÃO DE ARTEFATOS                                  │
│     ├─ powershell scripts/parity_scan.ps1                      │
│     ├─ Artefatos atualizados em docs/_generated/              │
│     └─ Exit code 0 (sem diffs estruturais)                     │
│                                                                 │
│  3. Valida ALINHAMENTO (gates)                                 │
│     ├─ scripts/parity_gate.ps1 (structural diffs = 0)         │
│     ├─ scripts/agent_guard.py (baseline check)                │
│     └─ python scripts/validate_artifact_freshness.py          │
│                                                                 │
│  4. Atualiza DOCUMENTAÇÃO (derivada)                           │
│     ├─ docs/02_modulos/training/TRD_TRAINING.md               │
│     ├─ docs/02_modulos/training/INVARIANTS_TRAINING.md        │
│     └─ docs/02_modulos/training/PRD_BASELINE_ASIS_TRAINING.md │
│                                                                 │
│  5. Abre PULL REQUEST                                          │
│     ├─ GitHub Actions valida artifacts freshness              │
│     ├─ CI/CD roda parity gate                                  │
│     └─ PR só é mergeável se gates passarem                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Artefatos Canônicos

| Artefato | Comando de Geração | Conteúdo | Autoridade |
|----------|-------------------|----------|------------|
| `schema.sql` | `pg_dump --schema-only` | DDL completo do banco | **DB real** (SSOT) |
| `openapi.json` | FastAPI auto-generated | Contrato de API | **FastAPI app** |
| `alembic_state.txt` | `alembic heads` + `alembic history` | Estado das migrations | **Alembic** |
| `manifest.json` | `scripts/generate_manifest.py` | Checksums + metadata | **Git state** |

## Comandos Essenciais

### 1. Gerar Artefatos

```powershell
# Backend: schema.sql + openapi.json + alembic_state.txt + manifest.json
cd "Hb Track - Backend"
powershell scripts/parity_scan.ps1

# Verificar saída
Test-Path "docs\_generated\schema.sql"
Test-Path "docs\_generated\openapi.json"
Test-Path "docs\_generated\alembic_state.txt"
Test-Path "docs\_generated\manifest.json"
```

### 2. Validar Alinhamento

```powershell
# Parity gate (structural diffs)
cd "Hb Track - Backend"
powershell scripts/parity_gate.ps1 -Table "training_sessions"
# Esperado: exit=0 (sem diffs estruturais)

# Agent guard (baseline check)
python scripts/agent_guard.py check --forbid-new
# Esperado: exit=0 (nenhuma violação)

# Artifact freshness
python scripts/validate_artifact_freshness.py
# Esperado: exit=0 (artifacts frescos)
```

### 3. Atualizar Documentação

**REGRA:** Só editar docs APÓS gates passarem (exit=0).

```markdown
# Exemplo: atualizar TRD após adicionar constraint
# 1. Rodar parity_scan.ps1 (gera schema.sql atualizado)
# 2. Validar: schema.sql contém novo constraint
# 3. Editar TRD: adicionar referência via constraint_name
# 4. Commitar: docs + artifacts no mesmo commit
```

### 4. Commit e PR

```powershell
# Stage artifacts + docs juntos
git add "Hb Track - Backend\docs\_generated\*.sql"
git add "Hb Track - Backend\docs\_generated\*.json"
git add "docs\02_modulos\training\*.md"

# Commit (pre-commit hook valida artifacts)
git commit -m "feat(training): adicionar constraint de X

- schema.sql: novo constraint ck_training_X
- TRD_TRAINING.md: documentar regra via constraint_name
- INVARIANTS_TRAINING.md: adicionar INV-TRAIN-XXX

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"

# Push e abrir PR
git push origin feature/add-constraint-x
```

## Gates Automáticos

### Pre-commit Hook (Local)

**Arquivo:** `.git/hooks/pre-commit`

**Comportamento:**
- Detecta docs staged para commit
- Valida freshness via `validate_artifact_freshness.py`
- **Bloqueia commit se artifacts stale** (exit 1)
- Bypass: `git commit --no-verify` (não recomendado)

**Instalação:**
```powershell
Copy-Item "scripts\pre-commit-artifacts.sh" ".git\hooks\pre-commit"
```

### CI/CD (GitHub Actions)

**Workflow:** `.github/workflows/validate-artifacts.yml`

**Triggers:**
- PRs que modificam `docs/**/*.md`
- PRs que modificam `docs/_generated/**`
- PRs que modificam `app/models/**`

**Jobs:**
1. **validate-artifacts:** Valida freshness (exit 0/4)
2. **validate-parity:** Roda parity gate para models modificados

**Resultado:**
- ✅ PR mergeável se gates passarem
- ❌ PR bloqueado se artifacts stale ou parity falhar

## Troubleshooting

### Problema: Pre-commit hook bloqueia commit

**Sintoma:**
```
❌ COMMIT BLOQUEADO: Artifacts stale
```

**Solução:**
```powershell
# 1. Regenerar artifacts
cd "Hb Track - Backend"
powershell scripts/parity_scan.ps1

# 2. Stage artifacts
git add "docs\_generated\*.sql"
git add "docs\_generated\*.json"

# 3. Retentar commit
git commit -m "..."
```

### Problema: CI/CD falha com "artifacts stale"

**Sintoma:** GitHub Actions job `validate-artifacts` falha

**Solução:**
```powershell
# 1. Fazer checkout da branch do PR
git checkout feature/minha-branch

# 2. Regenerar artifacts localmente
powershell scripts/parity_scan.ps1

# 3. Commitar artifacts
git add "docs\_generated\*"
git commit -m "chore: refresh artifacts"
git push
```

### Problema: Parity gate falha em CI/CD

**Sintoma:** Job `validate-parity` falha com diffs estruturais

**Solução:**
```powershell
# 1. Rodar parity gate localmente
cd "Hb Track - Backend"
powershell scripts/parity_gate.ps1 -Table "training_sessions"

# 2. Revisar parity_report.json
Get-Content "docs\_generated\parity_report.json" | ConvertFrom-Json

# 3. Corrigir model ou migration conforme diffs
# 4. Re-rodar gate até exit=0
# 5. Commitar correções + artifacts
```

## Referências

- **ADR-TRAIN-001:** SSOT e Precedência (DB > Service > OpenAPI > Docs)
- **ADR-TRAIN-002:** TRD por Referência (não duplicar schemas)
- **ADR-TRAIN-008:** Governança por Artefatos (esta ADR)
- **parity_scan.ps1:** Script de geração de artifacts
- **parity_gate.ps1:** Gate de validação estrutural
- **agent_guard.py:** Guard para agentes IA
```

**Critério de DONE:**
- ✅ Workflow guide completo com diagramas ASCII
- ✅ Comandos executáveis (copy-pasteable)
- ✅ Troubleshooting com soluções passo-a-passo
- ✅ Referências cruzadas a ADRs e scripts

---

#### Entregável 4.2: README.md em docs/_generated/

**Arquivo:** `docs/_generated/README.md`

```markdown
# Artefatos Gerados (_generated)

Este diretório contém **artefatos canônicos** gerados automaticamente de código/DB, servindo como **Single Source of Truth (SSOT)** para documentação derivada.

## ⚠️ IMPORTANTE: NÃO EDITAR MANUALMENTE

Arquivos neste diretório são **gerados automaticamente**. Edições manuais serão **sobrescritas** na próxima geração.

**Para modificar conteúdo:**
1. Alterar código/DB (models, routers, migrations)
2. Rodar script de geração (`parity_scan.ps1`)
3. Commitar artifacts atualizados

## Artefatos

### schema.sql

**Fonte:** `pg_dump --schema-only` do banco de dados real
**Conteúdo:** DDL completo (CREATE TABLE, constraints, triggers, indexes)
**Geração:** `powershell scripts/parity_scan.ps1` (chama pg_dump internamente)
**Autoridade:** **DB real** (PostgreSQL) — SSOT absoluto

**Uso:**
- Documentação referencia via `constraint_name` (ex: `ck_training_sessions_focus_total_sum`)
- Testes de invariantes extraem requisitos de setup (FKs, NOT NULL, enums)
- Parity gate compara com SQLAlchemy metadata

### openapi.json

**Fonte:** FastAPI auto-generated (`/openapi.json` endpoint)
**Conteúdo:** Contrato OpenAPI 3.0 (endpoints, schemas, operationIds)
**Geração:** `powershell scripts/parity_scan.ps1` (faz request HTTP ao app)
**Autoridade:** **FastAPI app** — SSOT de contratos de API

**Uso:**
- Documentação referencia via `operationId` (ex: `createTrainingSession`)
- Testes de contrato (Classe F) validam JSON Pointers
- Frontend consume para type generation

### alembic_state.txt

**Fonte:** `alembic heads` + `alembic history`
**Conteúdo:** Estado atual das migrations (head revision, histórico)
**Geração:** `powershell scripts/parity_scan.ps1`
**Autoridade:** **Alembic** — SSOT de versionamento de schema

**Uso:**
- Debugging de migration conflicts
- Audit trail de mudanças estruturais
- CI/CD valida que HEAD está aplicado

### manifest.json

**Fonte:** Script customizado (`scripts/generate_manifest.py`)
**Conteúdo:** Checksums SHA256 de artifacts + metadata Git
**Geração:** `powershell scripts/parity_scan.ps1` (chama generate_manifest.py)
**Autoridade:** **Git state** — SSOT de integridade

**Uso:**
- Agent guard valida checksums antes de operações
- Detecta tampering de artifacts
- Audit trail de quando artifacts foram gerados

## Comandos

```powershell
# Regenerar todos os artefatos
cd "Hb Track - Backend"
powershell scripts/parity_scan.ps1

# Validar freshness
python scripts/validate_artifact_freshness.py

# Ver diff de schema.sql
git diff "docs\_generated\schema.sql"
```

## Governança

Ver `docs/workflows/artifact_governance_workflow.md` para fluxo completo.

**Regra:** Documentação só é atualizada APÓS artifacts serem gerados.
```

**Critério de DONE:**
- ✅ README.md explica cada artifact (fonte, conteúdo, autoridade, uso)
- ✅ Aviso claro de não editar manualmente
- ✅ Comandos essenciais listados
- ✅ Link para workflow guide

---

## 🧪 TESTES DE ACEITAÇÃO GLOBAL

### Smoke Test Final (executar APÓS todas as fases)

```powershell
# ==================== CENÁRIO 1: Artifact freshness validator ====================
Write-Host "`n[TEST 1] Validando artifact freshness validator..." -ForegroundColor Cyan

# Setup: garantir artifacts frescos
cd "Hb Track - Backend"
powershell scripts/parity_scan.ps1
cd ..

# Teste: validar freshness
python scripts/validate_artifact_freshness.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ FAIL: Validator reportou artifacts stale (mas acabamos de gerar)" -ForegroundColor Red
    exit 1
}
Write-Host "✅ PASS: Artifacts frescos" -ForegroundColor Green

# ==================== CENÁRIO 2: Pre-commit hook bloqueia commit ====================
Write-Host "`n[TEST 2] Testando pre-commit hook..." -ForegroundColor Cyan

# Setup: criar commit de teste
$testBranch = "test-governance-$(Get-Random)"
git checkout -b $testBranch

# Modificar doc para torná-la mais recente que artifacts
Start-Sleep -Seconds 2
Add-Content "docs\02_modulos\training\TRD_TRAINING.md" "`n<!-- test -->"
git add "docs\02_modulos\training\TRD_TRAINING.md"

# Tentar commit (hook deve bloquear)
git commit -m "test: should be blocked" 2>&1 | Out-Null
$hookExitCode = $LASTEXITCODE

# Cleanup
git checkout main
git branch -D $testBranch

if ($hookExitCode -eq 0) {
    Write-Host "❌ FAIL: Hook não bloqueou commit com artifact stale" -ForegroundColor Red
    exit 1
}
Write-Host "✅ PASS: Hook bloqueou commit corretamente" -ForegroundColor Green

# ==================== CENÁRIO 3: CI/CD workflow existe ====================
Write-Host "`n[TEST 3] Validando CI/CD workflow..." -ForegroundColor Cyan

if (-not (Test-Path ".github\workflows\validate-artifacts.yml")) {
    Write-Host "❌ FAIL: Workflow validate-artifacts.yml não existe" -ForegroundColor Red
    exit 1
}

# Validar sintaxe YAML (requer yq ou python)
python -c "import yaml; yaml.safe_load(open('.github/workflows/validate-artifacts.yml'))" 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ FAIL: Workflow YAML inválido" -ForegroundColor Red
    exit 1
}
Write-Host "✅ PASS: Workflow válido" -ForegroundColor Green

# ==================== CENÁRIO 4: Documentação completa ====================
Write-Host "`n[TEST 4] Validando documentação..." -ForegroundColor Cyan

$docs = @(
    "docs\workflows\artifact_governance_workflow.md",
    "docs\_generated\README.md"
)

foreach ($doc in $docs) {
    if (-not (Test-Path $doc)) {
        Write-Host "❌ FAIL: Documento faltando: $doc" -ForegroundColor Red
        exit 1
    }
}
Write-Host "✅ PASS: Documentação completa" -ForegroundColor Green

Write-Host "`n✅✅✅ TODOS OS TESTES PASSARAM ✅✅✅" -ForegroundColor Green
```

**Critério de DONE GLOBAL:**
- ✅ 4 cenários de smoke test passam
- ✅ Validator funciona (exit 0/4)
- ✅ Pre-commit hook bloqueia commits (exit 1)
- ✅ CI/CD workflow válido (YAML sem erros)
- ✅ Documentação completa (workflow guide + README)

---

## 📊 CHECKLIST DE ENTREGA

### Código

- [ ] `scripts/validate_artifact_freshness.py` implementado
- [ ] `scripts/pre-commit-artifacts.sh` implementado
- [ ] `.git/hooks/pre-commit` instalado (hook ativo)
- [ ] `.github/workflows/validate-artifacts.yml` criado
- [ ] Mapeamento `DOC_TO_ARTIFACTS` completo (TRD, PRD, INVARIANTS)

### Documentação

- [ ] `docs/workflows/artifact_governance_workflow.md` criado
- [ ] `docs/_generated/README.md` criado
- [ ] Diagramas de fluxo (ASCII art) presentes
- [ ] Troubleshooting com soluções executáveis

### Validação

- [ ] Smoke test: 4 cenários passam
- [ ] Validator: exit 0 (fresh) e exit 4 (stale) funcionam
- [ ] Pre-commit hook: bloqueia commits (exit 1)
- [ ] CI/CD workflow: sintaxe YAML válida
- [ ] Documentação: links e comandos testados

### Infra

- [ ] Hook instalado em `.git/hooks/` (manual ou via setup script)
- [ ] CI/CD workflow merge em branch main
- [ ] Branch protection rules configuradas (require workflow pass)

---

## 🚨 CONDIÇÕES DE ABORT

### ABORTAR IMEDIATAMENTE SE:

1. **Pré-requisitos falharem:**
   - Scripts de gate (`parity_gate.ps1`, `agent_guard.py`) não existem
   - Artefatos `_generated/` não existem ou estão vazios
   - GitHub Actions não disponível (repo privado sem acesso)

2. **Pre-commit hook não funciona:**
   - Hook não dispara (instalação falhou)
   - Hook dispara mas não valida corretamente (lógica errada)
   - Bypass via `--no-verify` não funciona

3. **CI/CD workflow com erros:**
   - Sintaxe YAML inválida (falha no parse)
   - Jobs não disparam (triggers incorretos)
   - Falsos positivos/negativos > 10%

4. **Documentação incompleta:**
   - Workflow guide sem comandos executáveis
   - Troubleshooting sem soluções passo-a-passo
   - README sem avisos claros de não editar manualmente

---

## 📅 CRONOGRAMA DETALHADO

| Dia | Fase | Horas | Entregáveis |
|-----|------|-------|-------------|
| **D1** | FASE 1 | 8h | Artifact freshness validator |
| **D2** | FASE 2 | 4h | Pre-commit hook |
| **D2-D3** | FASE 3 | 8h | CI/CD workflow |
| **D3** | FASE 4 | 4h | Documentação |

**Total:** 24 horas (~3 dias úteis)

---

## 🎯 CRITÉRIO DE SUCESSO FINAL

### Definição de DONE:

**O sistema está pronto quando:**

1. ✅ `validate_artifact_freshness.py` funciona (exit 0/4)
2. ✅ Pre-commit hook bloqueia commits com artifacts stale
3. ✅ CI/CD workflow funcional (GitHub Actions passa)
4. ✅ Smoke test completo passa (4 cenários)
5. ✅ Documentação completa (workflow guide + README)
6. ✅ Branch protection rules ativadas (require workflow)

**Assinatura de aceite:**
- [ ] Davi (Tech Lead) — Validação técnica
- [ ] Claude (AI Assistant) — Revisão de código + documentação

---

## 📎 ANEXOS

### A. Estrutura de arquivos esperada

```
HB TRACK/
├── .github/
│   └── workflows/
│       └── validate-artifacts.yml         # NOVO
├── .git/
│   └── hooks/
│       └── pre-commit                     # NOVO (instalado)
├── scripts/
│   ├── validate_artifact_freshness.py     # NOVO
│   ├── pre-commit-artifacts.sh            # NOVO
│   ├── parity_scan.ps1                    # Existente
│   ├── parity_gate.ps1                    # Existente
│   └── agent_guard.py                     # Existente
├── docs/
│   ├── workflows/
│   │   └── artifact_governance_workflow.md  # NOVO
│   └── _generated/
│       ├── README.md                      # NOVO
│       ├── schema.sql                     # Existente
│       ├── openapi.json                   # Existente
│       ├── alembic_state.txt              # Existente
│       └── manifest.json                  # Existente
```

### B. Exemplo de saída do validator

```
🔍 Validando freshness de artefatos...

✅ FRESH: INVARIANTS_TRAINING.md ← schema.sql
✅ FRESH: INVARIANTS_TRAINING.md ← openapi.json
✅ FRESH: TRD_TRAINING.md ← openapi.json
✅ FRESH: TRD_TRAINING.md ← schema.sql
✅ FRESH: PRD_BASELINE_ASIS_TRAINING.md ← manifest.json

✅ Todos os artefatos estão frescos (docs ≤ artifacts)
```

### C. Comandos de referência rápida

```powershell
# Validar freshness
python scripts/validate_artifact_freshness.py

# Instalar pre-commit hook
Copy-Item "scripts\pre-commit-artifacts.sh" ".git\hooks\pre-commit"

# Regenerar artifacts
cd "Hb Track - Backend"
powershell scripts/parity_scan.ps1

# Smoke test completo
.\scripts\smoke_test_governance.ps1
```

---

**FIM DA EXEC_TASK**

**Status:** ✅ PRONTO PARA EXECUÇÃO
**Próximo passo:** Iniciar FASE 1 (artifact freshness validator)
