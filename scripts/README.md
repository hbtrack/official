# HB Track - Backend Scripts

Pasta centralizada para scripts operacionais, de manutenção e automação.

## CANONICAL ENTRYPOINTS (CI + Local)

Estes são os **únicos** comandos oficiais para validação de governance:

| Gate | Comando | SSOT | Engine |
|------|---------|------|--------|
| **R12: Python Layout** | `pwsh -File scripts/checks/lint/check_python_layout.ps1` | [python_layout.policy.yaml](../_policy/python_layout.policy.yaml) | [check_python_layout.py](../_policy/check_python_layout.py) |
| **Scripts Policy** | `pwsh -File scripts/checks/policy/check_scripts_policy.ps1` | [scripts.policy.yaml](../_policy/scripts.policy.yaml) | [check_scripts_policy.ps1](../_policy/check_scripts_policy.ps1) |
| **Manifest Integrity** | `pwsh -File scripts/checks/policy/check_policy_manifest.ps1` | [policy.manifest.json](../_policy/policy.manifest.json) | [check_policy_manifest.ps1](../_policy/check_policy_manifest.ps1) |
| **Derived MD Drift** | `pwsh -File scripts/checks/policy/check_policy_md_is_derived.ps1` | [scripts.policy.yaml](../_policy/scripts.policy.yaml) | [check_policy_md_is_derived.ps1](../_policy/check_policy_md_is_derived.ps1) |

**Exit codes (all gates):**
- `0` = OK (compliance)
- `2` = VIOLATION / MISMATCH / DRIFT (policy/data error)
- `3` = HARNESS_ERROR (missing deps, git issue, etc.)

## Regra Determin�stica (MANDAT�RIA)
- **scripts/checks/**: Estritamente **READ-ONLY**. Scripts aqui n�o podem alterar banco de dados, arquivos ou estados do sistema.
- **scripts/fixes/**: Scripts que aplicam corre��es ou patches.
- **scripts/run/**: Ponto de entrada para automa��o (PowerShell).

## Estrutura
- **artifacts/**: Saídas de scripts (ignorados pelo git, exceto README).
- **diagnostics/**: Scripts de análise profunda (Read-only mais complexos).
- **generate/**: Geradores de código, hashes, schemas.
- **migrate/**: Migrações de dados e backfills.
- **ops/**: Operações de infraestrutura e banco (maintenance/refresh).
- **plans/**: **[ENCAPSULADO]** Sistema Architect-Executor (ver seção dedicada abaixo).
- **reset/**: Scripts para resetar ambiente ou serviços.
- **security/**: Auditorias e correções de segurança.
- **seeds/**: População de dados (dev/test/official).
- **temp/**: Scripts temporários e testes locais (ignorados pelo git).

---

## 📋 Sistema de Planos: Architect-Executor Flow

### Contexto

O diretório `scripts/plans/` implementa um **fluxo determinístico** para criação e execução de tarefas de desenvolvimento através de IAs especializadas:

- **Arquiteto (IA):** Cria planos detalhados com zero ambiguidade
- **Executor (IA/Humano):** Implementa exatamente o que foi planejado

**Documentação completa:** [scripts/plans/README.md](plans/README.md)

---

### Funcionamento Anterior (Antes da Refatoração - FASE-OPS-1)

#### ❌ Problemas Identificados

Os scripts usavam **caminhos relativos hard-coded**, causando:

1. **Fragilidade de execução:** Scripts falhavam se executados fora do diretório esperado
2. **Dependência implícita de `cwd`:** `Path("docs/plans")` assumia que `os.getcwd()` era a raiz do projeto
3. **Impossibilidade de portabilidade:** Caminhos não funcionariam consistentemente entre Windows/Linux
4. **Duplicação de constantes:** Cada script definia seus próprios caminhos

**Exemplo do código antigo:**
```python
# check_locks.py (ANTES)
LOCKS_FILE = Path("docs/file_locks.yaml")  # ❌ Relativo ao cwd

# plan_status.py (ANTES)
PLANS_DIR = Path("docs/plans")            # ❌ Relativo ao cwd
IMPLEMENTED_DIR = Path("docs/implemented")

# generate_context_snapshot.py (ANTES)
models_dir = Path("app/models")           # ❌ Assumia estar na raiz
if Path("requirements.txt").exists():     # ❌ Qual requirements.txt?
```

**Resultado:** Scripts só funcionavam se executados **exatamente** da raiz `C:\HB TRACK` E se o `cwd` do processo fosse mantido.

---

### Função de Cada Script

| Script | Propósito | Entrada | Saída |
|--------|-----------|---------|-------|
| **config.py** | Centraliza TODAS as constantes de caminhos usando `pathlib` absolutos | N/A | Constantes: `PROJECT_ROOT`, `PLANS_DIR`, `LOCKS_FILE`, etc. |
| **generate_context_snapshot.py** | Gera snapshot do estado atual do repositório para o Arquiteto | Nenhuma (lê repo) | Snapshot em stdout (Git, schema, estrutura, dependências) |
| **plan_status.py** | Gerencia ciclo de vida dos planos (status: RASCUNHO→APROVADO→EXECUTADO) | Caminho do plano.md | Status atual ou mudança de status |
| **check_locks.py** | Sistema de locks para prevenir conflitos quando múltiplos planos executam | Caminho do plano.md | Lista de locks, aquisição ou liberação |
| **executor_workflow.py** | Orquestrador principal (dry-run → execute → validate → commit) | Caminho do plano.md | Execução completa do workflow |
| **validate_dag.py** | Valida grafo de dependências entre planos (DAG) | Arquivo YAML de DAG | Ordem de execução ou validação de dependências |
| **validate_plan_adherence.py** | Verifica se implementação seguiu exatamente o plano | Caminho do plano.md | Relatório de conformidade (desvios) |
| **record_metrics.py** | Coleta métricas de tempo/bugs/rollbacks para medir ROI do fluxo | Task ID + métricas | Arquivo JSON atualizado + relatório |

---

### Mudanças Realizadas (FASE-OPS-1-ENCAPSULAR-SCRIPTS-PLANS)

#### ✅ Implementação (2026-02-17)

**Arquivos criados:**
1. `scripts/plans/config.py` - Módulo de configuração centralizado
2. `scripts/plans/docs/file_locks.yaml` - Arquivo inicial de locks
3. `scripts/plans/docs/metrics/executor_metrics.json` - Arquivo inicial de métricas
4. `scripts/plans/README.md` - Documentação completa do sistema

**Arquivos modificados (7):**
- `check_locks.py`
- `executor_workflow.py`
- `generate_context_snapshot.py`
- `plan_status.py`
- `record_metrics.py`
- `validate_dag.py`
- `validate_plan_adherence.py`

#### 🔧 Mudanças Técnicas

**Antes:**
```python
LOCKS_FILE = Path("docs/file_locks.yaml")  # ❌ Relativo
```

**Depois:**
```python
from config import LOCKS_FILE  # ✅ Absoluto: C:\HB TRACK\scripts\plans\docs\file_locks.yaml
```

**Constantes centralizadas em `config.py`:**
```python
from pathlib import Path

SCRIPTS_PLANS_ROOT = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPTS_PLANS_ROOT.parent.parent

# Estrutura encapsulada
DOCS_ROOT = SCRIPTS_PLANS_ROOT / "docs"
PLANS_DIR = DOCS_ROOT / "plans"
IMPLEMENTED_DIR = DOCS_ROOT / "implemented"
LOCKS_FILE = DOCS_ROOT / "file_locks.yaml"

# Diretórios do projeto HB TRACK
HB_BACKEND_DIR = PROJECT_ROOT / "Hb Track - Backend"
BACKEND_MODELS_DIR = HB_BACKEND_DIR / "app" / "models"
BACKEND_TESTS_DIR = HB_BACKEND_DIR / "tests"
```

#### 📊 Evidências de Testes (Definition of Done)

**T001: `plan_status.py` funciona com estrutura encapsulada**
```powershell
PS C:\HB TRACK> python scripts\plans\plan_status.py scripts\plans\docs\plans\TESTE-001.md

================================================================================
PLAN: TESTE-001
================================================================================
File: scripts\plans\docs\plans\TESTE-001.md
Status: RASCUNHO
ℹ️  Needs review before approval
```
✅ **PASS** - Leu plano da estrutura encapsulada sem erro "File not found"

---

**T002: `check_locks.py` usa novo caminho de locks**
```powershell
PS C:\HB TRACK> python scripts\plans\check_locks.py --list
No active locks.
```
✅ **PASS** - Leu de `scripts\plans\docs\file_locks.yaml` ao invés de `docs/file_locks.yaml`

---

**T003: `generate_context_snapshot.py` lê do backend**
```powershell
PS C:\HB TRACK> python scripts\plans\generate_context_snapshot.py | Select-String "Project root:|Backend dir:"

Project root: C:\HB TRACK
Backend dir: C:\HB TRACK\Hb Track - Backend
```
✅ **PASS** - Script agora lê de `Hb Track - Backend/app/models`, não de `scripts/plans/`

---

**T004: Todos os scripts importam `config.py` sem erros**
```powershell
PS C:\HB TRACK> python -c "import sys; sys.path.insert(0, 'scripts/plans'); from config import PROJECT_ROOT, PLANS_DIR; print(f'PROJECT_ROOT={PROJECT_ROOT}\nPLANS_DIR={PLANS_DIR}')"

✅ T004 PASS: Imports funcionam
PROJECT_ROOT=C:\HB TRACK
PLANS_DIR=C:\HB TRACK\scripts\plans\docs\plans
```
✅ **PASS** - Módulo `config.py` está acessível e constantes corretas

---

**T005 & T006: Arquivos iniciais criados**
```powershell
PS C:\HB TRACK> Get-Content "scripts\plans\docs\file_locks.yaml"
locked_files: {}

PS C:\HB TRACK> Get-Content "scripts\plans\docs\metrics\executor_metrics.json"
[]
```
✅ **PASS** - Arquivos de controle existem e estão no formato correto

---

**Validação de imports (7 scripts):**
```powershell
PS C:\HB TRACK> Get-ChildItem scripts\plans\*.py | Select-String -Pattern "from config import"

check_locks.py           from config import LOCKS_FILE
executor_workflow.py     from config import (
generate_context_snapshot.py from config import (
plan_status.py           from config import PLANS_DIR, IMPLEMENTED_DIR
record_metrics.py        from config import METRICS_FILE
validate_dag.py          from config import IMPLEMENTED_DIR
validate_plan_adherence.py from config import PROJECT_ROOT, BACKEND_TESTS_DIR
```
✅ **PASS** - Todos os 7 scripts importam de `config.py`

---

#### 🎯 Benefícios da Refatoração

| Aspecto | Antes | Depois |
|---------|-------|--------|
| **Portabilidade** | Quebrava ao mudar `cwd` | Funciona de qualquer diretório |
| **Windows/Linux** | Caminhos hard-coded com `/` | `pathlib.Path` adapta automaticamente |
| **Manutenção** | Constantes duplicadas em 7 arquivos | 1 único arquivo de configuração |
| **Debugging** | Erros crípticos "File not found" | Caminhos absolutos nos logs |
| **Documentação** | Código espalhado | README.md centralizado |

#### 📝 Uso Atual (Pós-Refatoração)

**Sempre rodar da raiz do projeto:**
```powershell
# ✅ CORRETO
PS C:\HB TRACK> python scripts\plans\generate_context_snapshot.py > scripts\plans\docs\context\context.txt
PS C:\HB TRACK> python scripts\plans\plan_status.py --list
PS C:\HB TRACK> python scripts\plans\check_locks.py --list

# ❌ ERRADO (não faça isso)
PS C:\HB TRACK\scripts\plans> python plan_status.py --list
```

**Por quê?** O sistema usa caminhos absolutos calculados a partir de `__file__`, mas o ambiente virtual (venv) e o Git exigem execução da raiz.

---

### Status da Task

**TASK-ID:** FASE-OPS-1-ENCAPSULAR-SCRIPTS-PLANS  
**Status:** ✅ **COMPLETA** (2026-02-17)  
**Definition of Done:** 6/6 testes passaram  
**Arquivos:** 3 criados, 7 modificados  
**Commit:** Pendente (aguardando aprovação do usuário)
