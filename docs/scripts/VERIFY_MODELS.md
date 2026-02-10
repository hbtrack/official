# Guia Canônico: Scripts de Validação de Models SQLAlchemy

**Versão:** 1.0  
**Data:** 2026-02-09  
**Autor:** HB Track Engineering Team  
**Escopo:** Pipeline completo de criação, validação e verificação de conformidade de models SQLAlchemy no backend HB Track.

---

## 1. Visão Geral

### 1.1 O que Este Pipeline Resolve

O pipeline de validação de models garante **conformidade 100%** entre:
- **Database schema** (PostgreSQL DDL, fonte de verdade via migrations Alembic)
- **Models SQLAlchemy** (`app/models/*.py`)
- **Regras de negócio** (foreign keys, constraints, nullable, tipos)

**Quando usar:**
- Criar novo model a partir de tabela existente no DB
- Modificar model existente (colunas, constraints, FKs)
- Validar que model está sincronizado com schema.sql (SSOT)
- Garantir que mudanças em código respeitam baseline de arquivos protegidos

**Artefatos principais:**
- `schema.sql` (SSOT gerado via `pg_dump` ou migrations)
- `.hb_guard/baseline.json` (baseline de arquivos protegidos)
- `docs/_generated/parity_report.json` (relatório de diffs estruturais)

---

### 1.2 Scripts do Pipeline

| Script | Linguagem | Responsabilidade | Exit Codes |
|--------|-----------|------------------|------------|
| **models_autogen_gate.ps1** | PowerShell | Orquestra pipeline completo (guard → parity → autogen → parity → requirements) | 0, 1, 2, 3, 4 |
| **parity_gate.ps1** | PowerShell | Verifica alinhamento Model ↔ DB (pre-check e post-check) | 0, 1, 2 |
| **parity_scan.ps1** | PowerShell | Scan detalhado de mudanças pendentes (diagnóstico) | 0, 1, 2 |
| **autogen_model_from_db.py** | Python | Gera/atualiza model SQLAlchemy a partir do DB | 0, 1 |
| **agent_guard.py** | Python | Gerencia baseline (snapshot/check) de arquivos protegidos | 0, 1, 3 |
| **model_requirements.py** | Python | Valida integridade do model contra schema.sql (FKs, constraints, RDB) | 0, 1, 4 |

---

## 2. SSOT e Dependências

### 2.1 Fontes de Verdade (SSOT)

1. **Database Schema (PostgreSQL)**
   - Arquivo: `docs/_generated/schema.sql` (gerado via `pg_dump` ou `inv.ps1 refresh`)
   - Geração: `powershell -NoProfile -ExecutionPolicy Bypass -File "C:\HB TRACK\scripts\inv.ps1" refresh`
   - Conteúdo: DDL completo (CREATE TABLE, FK, CHECK, INDEX, COMMENT ON COLUMN)

2. **Baseline de Arquivos Protegidos**
   - Arquivo: `.hb_guard/baseline.json`
   - Geração: `python scripts/agent_guard.py snapshot --root . --out .hb_guard/baseline.json --exclude "venv,.venv,__pycache__,.pytest_cache,docs\_generated"`
   - Conteúdo: SHA256 + size de todos os arquivos rastreados (exceto excludes)

3. **Regras de Integridade (RDB)**
   - Documento: `docs/00_product/PRD_HB_TRACK.md` (Seção 8.3)
   - Regras: FK obrigatórios, CHECK constraints, nullable explícito, validações de negócio

### 2.2 Dependências Externas

- **Python 3.11+** (venv obrigatório: `Hb Track - Backend/venv/Scripts/python.exe`)
- **PostgreSQL 14+** (DATABASE_URL_SYNC env var)
- **Alembic** (migrations)
- **SQLAlchemy 2.x**
- **psycopg2** (driver sync para parity scan)

### 2.3 Dependências Internas

```
models_autogen_gate.ps1
  ├── parity_gate.ps1
  │   ├── parity_scan.ps1
  │   └── agent_guard.py (check)
  ├── autogen_model_from_db.py
  ├── agent_guard.py (snapshot, opcional se -Create)
  └── model_requirements.py
```

---

## 3. Pré-requisitos

### 3.1 Checklist Obrigatório

Execute este checklist **antes de rodar qualquer script do pipeline**:

```powershell
# CHECK 1: PowerShell 5.1
$PSVersionTable.PSVersion.Major  # Deve ser 5

# CHECK 2: Backend root como working directory
Set-Location "C:\HB TRACK\Hb Track - Backend"
Get-Location  # Deve retornar backend root

# CHECK 3: Venv válido
Test-Path "venv\Scripts\python.exe"  # Deve retornar True
& "venv\Scripts\python.exe" --version  # Python 3.11+

# CHECK 4: DATABASE_URL_SYNC env var
$env:DATABASE_URL_SYNC  # Deve retornar postgresql+psycopg2://...
# OU: arquivo .env existe com DATABASE_URL ou DATABASE_URL_SYNC

# CHECK 5: Baseline existe
Test-Path ".hb_guard\baseline.json"  # Deve retornar True
# Se False: rodar snapshot (ver Seção 8.2)

# CHECK 6: Schema.sql atualizado (< 24h ou commit recente)
(Get-Item "docs\_generated\schema.sql").LastWriteTime
# Se desatualizado: rodar inv.ps1 refresh (ver Seção 3.2)

# CHECK 7: Repo limpo (nenhum arquivo pendente)
git status --porcelain  # Deve retornar vazio
# Se houver arquivos: commit ou revert antes de prosseguir
```

**Política de falha:** Se QUALQUER check falhar, ABORTAR e corrigir o problema antes de continuar.

### 3.2 Refresh do SSOT (schema.sql)

```powershell
# Atualiza schema.sql a partir do DB (via pg_dump)
Set-Location "C:\HB TRACK"
powershell -NoProfile -ExecutionPolicy Bypass -File "scripts\inv.ps1" refresh

# Verifica resultado
Test-Path "Hb Track - Backend\docs\_generated\schema.sql"
```

### 3.3 Snapshot do Baseline (primeira vez ou após mudanças autorizadas)

```powershell
Set-Location "C:\HB TRACK\Hb Track - Backend"
& "venv\Scripts\python.exe" scripts\agent_guard.py snapshot `
  --root "." `
  --out ".hb_guard\baseline.json" `
  --exclude "venv,.venv,__pycache__,.pytest_cache,docs\_generated"

# Commit baseline
git add .hb_guard\baseline.json
git commit -m "chore(guard): update baseline after authorized changes"
```

---

## 4. Interface dos Scripts

### 4.1 models_autogen_gate.ps1 (Orquestrador)

**Path:** `Hb Track - Backend/scripts/models_autogen_gate.ps1`

**Objetivo:** Executar pipeline completo de validação de model (guard → parity → autogen → parity → requirements).

**Sintaxe:**
```powershell
.\scripts\models_autogen_gate.ps1 `
  -Table "<table_name>" `
  [-Create] `
  [-Profile <fk|strict|lenient>] `
  [-AllowCycleWarning] `
  [-Allow "<path1>,<path2>,..."] `
  [-ModelFile "<relative_path>"] `
  [-ClassName "<class_name>"] `
  [-DbUrl "<connection_string>"]
```

**Parâmetros:**

| Nome | Tipo | Obrigatório | Default | Descrição | Exemplo |
|------|------|-------------|---------|-----------|---------|
| `-Table` | string | ✅ | — | Nome da tabela no DB (fonte de verdade) | `"attendance"` |
| `-Create` | switch | ❌ | `$false` | Se presente, cria novo model e atualiza baseline via snapshot | `-Create` |
| `-Profile` | string | ❌ | `"strict"` | Perfil de validação: `fk` (FK-only), `strict` (todas regras), `lenient` (relaxado) | `-Profile strict` |
| `-AllowCycleWarning` | switch | ❌ | `$false` | Permite cycle warnings para tabelas `teams`/`seasons` (requer `use_alter=True`) | `-AllowCycleWarning` |
| `-Allow` | string[] | ❌ | `@()` | Lista de paths adicionais autorizados a modificar (CSV ou array) | `-Allow "app/routes/attendance.py"` |
| `-ModelFile` | string | ❌ | auto | Path relativo do model (auto-detectado via `__tablename__`) | `-ModelFile "app/models/custom_attendance.py"` |
| `-ClassName` | string | ❌ | auto | Nome da classe do model (auto-gerado como CamelCase) | `-ClassName "AttendanceRecord"` |
| `-DbUrl` | string | ❌ | env var | Override de DATABASE_URL_SYNC para casos especiais | `-DbUrl "postgresql+psycopg2://..."` |

**Exit Codes:**
- `0`: Pipeline completo, model 100% conforme
- `1`: Erro interno (crash, arquivo não encontrado, exceção não tratada)
- `2`: Parity structural diffs (model difere do DB)
- `3`: Guard violations (arquivo protegido modificado sem autorização)
- `4`: Requirements violations (model viola regras de integridade/RDB)

---

### 4.2 parity_gate.ps1

**Path:** `Hb Track - Backend/scripts/parity_gate.ps1`

**Objetivo:** Verificar alinhamento estrutural Model ↔ Database (pre-check e post-check).

**Sintaxe:**
```powershell
.\scripts\parity_gate.ps1 `
  -Table "<table_name>" `
  [-Allow "<path1>,<path2>,..."] `
  [-AllowEnvPy] `
  [-AllowCycleWarning] `
  [-ParityReportPath "<path>"]
```

**Parâmetros:**

| Nome | Tipo | Obrigatório | Default | Descrição |
|------|------|-------------|---------|-----------|
| `-Table` | string | ✅ | — | Nome da tabela a validar |
| `-Allow` | string[] | ❌ | `@()` | Paths autorizados (além do model) |
| `-AllowEnvPy` | switch | ❌ | `$false` | Permite modificação de `db/alembic/env.py` |
| `-AllowCycleWarning` | switch | ❌ | `$false` | Permite cycle warnings (teams/seasons) |
| `-ParityReportPath` | string | ❌ | auto | Path customizado do parity_report.json |

**Exit Codes:**
- `0`: Model alinhado com DB
- `1`: Erro interno
- `2`: Diffs estruturais detectados (ver `docs/_generated/parity_report.json`)
- `3`: Guard violations

---

### 4.3 agent_guard.py

**Path:** `Hb Track - Backend/scripts/agent_guard.py`

**Objetivo:** Gerenciar baseline de arquivos protegidos (snapshot/check).

**Sintaxe:**
```powershell
# Snapshot (criar/atualizar baseline)
& "venv\Scripts\python.exe" scripts\agent_guard.py snapshot `
  --root "." `
  --out ".hb_guard\baseline.json" `
  --exclude "venv,.venv,__pycache__,.pytest_cache,docs\_generated"

# Check (validar contra baseline)
& "venv\Scripts\python.exe" scripts\agent_guard.py check `
  --root "." `
  --baseline ".hb_guard\baseline.json" `
  --allow "app/models/attendance.py,scripts/parity_gate.ps1" `
  --forbid-new `
  --forbid-delete `
  --assert-skip-model-only-empty "db\alembic\env.py"
```

**Exit Codes:**
- `0`: Nenhum arquivo protegido modificado
- `1`: Erro interno
- `3`: Violations detectadas (SHA mismatch, arquivo novo não autorizado, arquivo deletado)

---

### 4.4 model_requirements.py

**Path:** `Hb Track - Backend/scripts/model_requirements.py`

**Objetivo:** Validar integridade do model contra schema.sql (FKs, constraints, nullable, regras de negócio).

**Sintaxe:**
```powershell
& "venv\Scripts\python.exe" scripts\model_requirements.py `
  --table "<table_name>" `
  --profile <fk|strict|lenient>
```

**Parâmetros:**

| Nome | Tipo | Obrigatório | Default | Descrição |
|------|------|-------------|---------|-----------|
| `--table` | string | ✅ | — | Nome da tabela a validar |
| `--profile` | string | ❌ | `"strict"` | Perfil de validação: `fk` (FK-only), `strict` (todas regras), `lenient` (relaxado) |

**Exit Codes:**
- `0`: Model atende todas as requirements
- `1`: Erro interno
- `4`: Requirements violations (FK ausente, nullable incorreto, tipo incompatível, etc.)

---

## 5. Fluxo de Execução

### 5.1 Pipeline Completo (models_autogen_gate.ps1)

```
┌─────────────────────────────────────────────────────┐
│ PASSO 0: Preparação                                 │
├─────────────────────────────────────────────────────┤
│ • Set CWD = backend root                            │
│ • Resolve model file path (auto-detect)            │
│ • Build allowlist = [modelPath, ...custom Allow]   │
│ • Set PYTHONDONTWRITEBYTECODE=1                     │
│ • Validate DATABASE_URL_SYNC env var               │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│ PASSO 1: PRE-CHECK (Parity)                         │
├─────────────────────────────────────────────────────┤
│ Script: parity_gate.ps1 -Table <T> -Allow <...>    │
│ Objetivo: Verificar estado inicial (pode falhar)   │
│ Exit: 0 (ok) ou 2 (diffs) → WARNING, não aborta    │
│ Lógica: Se falhar, autogen tentará corrigir        │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│ PASSO 2: AUTOGEN (Aplicar Model)                    │
├─────────────────────────────────────────────────────┤
│ Script: autogen_model_from_db.py apply             │
│ Objetivo: Gerar/atualizar model a partir do DB     │
│ Exit: 0 (ok) ou 1 (crash) → ABORT                  │
│ Output: app/models/<table>.py (modificado/criado)  │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│ PASSO 2b: SNAPSHOT (se -Create)                     │
├─────────────────────────────────────────────────────┤
│ Script: agent_guard.py snapshot                     │
│ Objetivo: Atualizar baseline com novo model        │
│ Exit: 0 (ok) ou 1 (crash) → ABORT                  │
│ Output: .hb_guard/baseline.json (atualizado)       │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│ PASSO 3: POST-CHECK (Parity)                        │
├─────────────────────────────────────────────────────┤
│ Script: parity_gate.ps1 -Table <T> -Allow <...>    │
│ Objetivo: Validar que model agora está alinhado    │
│ Exit: 0 (ok) ou 2 (diffs) → ABORT                  │
│ Observability: [POST] parity_exit=<n>              │
│ Lógica: Se exit!=0, pipeline FALHA (exit 2)        │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│ PASSO 4: REQUIREMENTS (Validação)                   │
├─────────────────────────────────────────────────────┤
│ Script: model_requirements.py --table <T>          │
│ Objetivo: Validar FKs, constraints, nullable, RDB  │
│ Exit: 0 (ok) ou 4 (violations) → ABORT             │
│ Lógica: Se exit!=0, pipeline FALHA (exit 4)        │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│ RESULTADO FINAL                                      │
├─────────────────────────────────────────────────────┤
│ ✅ Exit 0: ALL GATES PASSED — Model 100% conforme  │
│ ❌ Exit 2: Parity diffs (ver parity_report.json)   │
│ ❌ Exit 3: Guard violations (ver allowlist)        │
│ ❌ Exit 4: Requirements violations (ver output)     │
│ ❌ Exit 1: Internal error (ver stack trace)        │
└─────────────────────────────────────────────────────┘
```

### 5.2 Guard Check (agent_guard.py)

Executado internamente por `parity_gate.ps1` (ANTES do parity scan):

```
┌─────────────────────────────────────────────────────┐
│ 1. Load baseline (.hb_guard/baseline.json)         │
├─────────────────────────────────────────────────────┤
│ 2. Scan current files (excluindo venv, __pycache__,│
│    docs/_generated)                                 │
├─────────────────────────────────────────────────────┤
│ 3. Compare SHA256 de cada arquivo                   │
├─────────────────────────────────────────────────────┤
│ 4. Violations:                                       │
│    • MODIFIED: SHA diferente (não em allowlist)    │
│    • NEW: arquivo novo (--forbid-new ativo)        │
│    • DELETED: arquivo deletado (--forbid-delete)   │
├─────────────────────────────────────────────────────┤
│ 5. Assert SKIP_MODEL_ONLY_TABLES = set()           │
│    (db/alembic/env.py, anti-masking)               │
├─────────────────────────────────────────────────────┤
│ 6. Exit 0 (ok) ou 3 (violations)                   │
└─────────────────────────────────────────────────────┘
```

### 5.3 Parity Scan (parity_scan.ps1)

Executado por `parity_gate.ps1` (APÓS guard check):

```
┌─────────────────────────────────────────────────────┐
│ 1. Execute alembic compare (SCAN_ONLY mode)        │
├─────────────────────────────────────────────────────┤
│ 2. Capture output (structural diffs, warnings)     │
├─────────────────────────────────────────────────────┤
│ 3. Parse output e gerar JSON report:                │
│    • diffs: lista de ops (add_column, modify, etc) │
│    • warnings: SQLAlchemy warnings (cycle, etc)    │
├─────────────────────────────────────────────────────┤
│ 4. Filter by -TableFilter (se especificado)        │
├─────────────────────────────────────────────────────┤
│ 5. Write docs/_generated/parity_report.json        │
├─────────────────────────────────────────────────────┤
│ 6. Exit codes:                                       │
│    • 0: nenhum diff estrutural                     │
│    • 2: diffs encontrados (FailOnStructuralDiffs)  │
│    • 1: crash/erro interno                         │
└─────────────────────────────────────────────────────┘
```

---

## 6. Artefatos Gerados/Modificados

### 6.1 Arquivos Gerados (docs/_generated/)

| Arquivo | Script Origem | Descrição | Commit? |
|---------|---------------|-----------|---------|
| `schema.sql` | `inv.ps1 refresh` (pg_dump) | DDL completo do DB (SSOT) | ✅ Sim |
| `parity_report.json` | `parity_scan.ps1` | Relatório de diffs estruturais | ❌ Não (git restore) |
| `alembic_state.txt` | `parity_scan.ps1` | Estado de migrations (heads) | ❌ Não (git restore) |
| `manifest.json` | `parity_scan.ps1` | Manifest de models/tables | ❌ Não (git restore) |

### 6.2 Arquivos Modificados (app/models/)

| Arquivo | Script Origem | Descrição | Commit? |
|---------|---------------|-----------|---------|
| `app/models/<table>.py` | `autogen_model_from_db.py` | Model SQLAlchemy gerado/atualizado | ✅ Sim (após validação) |

### 6.3 Baseline (.hb_guard/)

| Arquivo | Script Origem | Descrição | Commit? |
|---------|---------------|-----------|---------|
| `.hb_guard/baseline.json` | `agent_guard.py snapshot` | Baseline de arquivos protegidos (SHA256 + size) | ✅ Sim (após snapshot) |

### 6.4 Limpeza de Artefatos Gerados

**Regra:** Após rodar gates, **sempre limpar** `docs/_generated/*` para evitar sujar o repo.

```powershell
# No backend root
git restore -- `
  "docs\_generated\alembic_state.txt" `
  "docs\_generated\manifest.json" `
  "docs\_generated\parity_report.json" `
  "docs\_generated\schema.sql"

# No repo root (se necessário)
git restore -- `
  "C:/HB TRACK/Hb Track - Backend/docs/_generated/alembic_state.txt" `
  "C:/HB TRACK/Hb Track - Backend/docs/_generated/manifest.json" `
  "C:/HB TRACK/Hb Track - Backend/docs/_generated/schema.sql" `
  "C:/HB TRACK/Hb Track - Backend/docs/_generated/trd_training_permissions_report.txt"
```

---

## 7. Exit Codes

### 7.1 Semântica Completa

| Exit Code | Nome | Origem | Significado | Resolução |
|-----------|------|--------|-------------|-----------|
| **0** | SUCCESS | Todos | Pipeline completo, nenhum erro | Continuar (commit se aprovado) |
| **1** | INTERNAL_ERROR | Todos | Crash, exceção não tratada, arquivo não encontrado | Ver stack trace, corrigir pré-requisitos |
| **2** | PARITY_DIFFS | parity_gate.ps1, parity_scan.ps1 | Estrutura Model ↔ DB desalinhada | Ver parity_report.json, criar migration ou corrigir model |
| **3** | GUARD_VIOLATIONS | agent_guard.py | Arquivo protegido modificado sem autorização | Adicionar path ao `-Allow`, ou reverter mudança |
| **4** | REQUIREMENTS_VIOLATIONS | model_requirements.py | Model viola regras de integridade (FK, nullable, constraints) | Corrigir model conforme output do script |

### 7.2 Diagnóstico por Exit Code

#### Exit 0: Success ✅

**Sintoma:** Script retorna 0, nenhuma mensagem de erro.

**Significado:** Operação completada com sucesso.

**Ação:** Continuar para próximo passo ou commit.

---

#### Exit 1: Internal Error ❌

**Sintoma:**
```
[FAIL] models_autogen_gate failed: <exception_message>
$LASTEXITCODE = 1
```

**Causas comuns:**
- Arquivo não encontrado (schema.sql, model.py)
- Erro de sintaxe Python
- Venv não configurado
- DATABASE_URL_SYNC não definido

**Diagnóstico:**
1. Verificar stack trace completo no output
2. Confirmar pré-requisitos (Seção 3.1)
3. Verificar paths de arquivos
4. Validar permissões de leitura/escrita

**Exemplos de mensagens:**
- `RuntimeError: CREATE TABLE for '<table>' not found in schema.sql`
- `FileNotFoundError: [Errno 2] No such file or directory: 'app/models/<table>.py'`
- `env var not set: DATABASE_URL_SYNC`

---

#### Exit 2: Parity Structural Diffs ❌

**Sintoma:**
```
[FAIL] [parity_gate] exited with code 2
[POST] parity_exit=2
```

**Causas comuns:**
- Coluna adicionada/removida no model sem migration
- Tipo de coluna alterado
- Constraint (FK, CHECK, UNIQUE) modificada
- Nullable alterado
- Migration pendente não aplicada

**Diagnóstico:**
1. Abrir `docs/_generated/parity_report.json`
2. Revisar seção `"diffs"` para identificar operações pendentes
3. Verificar se migration existe e foi aplicada (`alembic current`)

**Exemplo de parity_report.json:**
```json
{
  "diffs": [
    {
      "op": "modify_nullable",
      "table": "attendance",
      "column": "athlete_id",
      "existing_type": "INTEGER",
      "existing_nullable": false,
      "nullable": true
    }
  ],
  "warnings": []
}
```

**Resolução:**

**Opção A: Migration necessária**
```powershell
alembic revision --autogenerate -m "fix attendance.athlete_id nullable"
alembic upgrade head
# Re-rodar gate
.\scripts\models_autogen_gate.ps1 -Table "attendance"
```

**Opção B: Model incorreto (reverter)**
```powershell
git restore -- app\models\attendance.py
# Ou re-gerar via autogen
.\scripts\models_autogen_gate.ps1 -Table "attendance"
```

---

#### Exit 3: Guard Violations ❌

**Sintoma:**
```
[FAIL] guard violations detected:
MODIFIED: app/routes/attendance.py (SHA mismatch)
$LASTEXITCODE = 3
```

**Causas comuns:**
- Arquivo de test modificado (`tests/**`)
- Arquivo de API modificado (`app/routes/**`)
- Arquivo de ML/Celery modificado (`app/tasks/**`)
- Script auxiliar modificado sem estar na allowlist

**Diagnóstico:**
1. Identificar qual arquivo foi modificado (output do guard)
2. Verificar se modificação é intencional
3. Verificar SHA atual vs baseline:
   ```powershell
   $file = "app\routes\attendance.py"
   Get-FileHash $file -Algorithm SHA256
   # Comparar com .hb_guard/baseline.json
   ```

**Resolução:**

**Opção A: Autorizar modificação (adicionar ao allowlist)**
```powershell
.\scripts\models_autogen_gate.ps1 -Table "attendance" -Allow "app/routes/attendance.py"
```

**Opção B: Reverter modificação não intencional**
```powershell
git restore -- app\routes\attendance.py
```

**Opção C: Atualizar baseline (após mudança legítima e commitada)**
```powershell
& "venv\Scripts\python.exe" scripts\agent_guard.py snapshot `
  --root "." `
  --out ".hb_guard\baseline.json" `
  --exclude "venv,.venv,__pycache__,.pytest_cache,docs\_generated"
git add .hb_guard\baseline.json
git commit -m "chore(guard): update baseline after authorized changes"
```

---

#### Exit 4: Requirements Violations ❌

**Sintoma:**
```
[FAIL] [model_requirements] exited with code 4
Requirements violations:
• FK 'fk_attendance_athlete' ondelete: expected CASCADE, got None
• Column 'date': nullable expected False, got True
```

**Causas comuns:**
- FK sem `ondelete` declarado
- Nullable incorreto ou não-explícito
- Tipo incompatível com schema.sql
- CHECK constraint ausente no model
- Index ausente

**Diagnóstico:**
1. Ler output completo do `model_requirements.py`
2. Comparar model com schema.sql (SSOT)
3. Verificar regras de integridade (PRD Seção 8.3)

**Resolução:**

**Editar model manualmente:**
```python
# Antes (violação)
athlete_id: Mapped[int] = mapped_column(ForeignKey("athletes.id"), nullable=False)

# Depois (conforme)
athlete_id: Mapped[int] = mapped_column(
    ForeignKey("athletes.id", name="fk_attendance_athlete", ondelete="CASCADE"),
    nullable=False
)
```

**Re-validar:**
```powershell
.\scripts\models_autogen_gate.ps1 -Table "attendance" -Profile strict
# Deve retornar exit 0
```

---

## 8. Exemplos Completos

### 8.1 Criar Novo Model (Tabela Existente no DB)

```powershell
# PASSO 0: Preparação
Set-Location "C:\HB TRACK\Hb Track - Backend"
git status --porcelain  # Deve estar vazio

# PASSO 1: Rodar gate com -Create (primeira vez)
.\scripts\models_autogen_gate.ps1 -Table "attendance" -Create -Profile strict

# Output esperado:
# [CWD] C:\HB TRACK\Hb Track - Backend
# [ROOT] C:\HB TRACK\Hb Track - Backend
# [TABLE] attendance
# [INFO] using DATABASE_URL_SYNC from .env
# [WARN] pre parity_gate failed (exit=2); continuing to autogen to attempt fix.
# [INFO] autogen_model_from_db: apply --table attendance
# [OK] Model written: app\models\attendance.py
# [OK] baseline written: .hb_guard\baseline.json
# [POST] parity_exit=0
# [OK] model_requirements: all checks passed
# Exit 0

# PASSO 2: Verificar modelo gerado
cat app\models\attendance.py

# PASSO 3: Limpar artefatos gerados
git restore -- docs\_generated\*

# PASSO 4: Commit
git status --porcelain  # Deve mostrar apenas app\models\attendance.py e .hb_guard\baseline.json
git add app\models\attendance.py .hb_guard\baseline.json
git commit -m "feat(models): add attendance model (100% SSOT conformant)"
```

---

### 8.2 Modificar Model Existente

```powershell
# PASSO 0: Preparação
Set-Location "C:\HB TRACK\Hb Track - Backend"
git status --porcelain  # Deve estar vazio

# PASSO 1: Editar model manualmente (ex: adicionar coluna 'notes')
# app\models\attendance.py:
#   notes: Mapped[str | None] = mapped_column(Text, nullable=True)

# PASSO 2: Rodar gate (SEM -Create, apenas validação)
.\scripts\models_autogen_gate.ps1 -Table "attendance" -Profile strict

# PASSO 2a: Se exit=2 (parity diffs), criar migration
alembic revision --autogenerate -m "add attendance.notes column"
alembic upgrade head

# PASSO 3: Re-rodar gate (deve passar)
.\scripts\models_autogen_gate.ps1 -Table "attendance" -Profile strict
# Exit 0

# PASSO 4: Limpar artefatos
git restore -- docs\_generated\*

# PASSO 5: Commit
git add app\models\attendance.py db\alembic\versions\0042_*.py
git commit -m "feat(models): add notes column to attendance"
```

---

### 8.3 Validar Todos os Models (Múltiplas Tabelas)

```powershell
# Lista de tabelas (exemplo)
$tables = @("attendance", "athletes", "teams", "seasons", "matches")

foreach ($table in $tables) {
  Write-Host "`n===== Validating $table =====" -ForegroundColor Cyan
  .\scripts\models_autogen_gate.ps1 -Table $table -Profile strict
  $exitCode = $LASTEXITCODE
  
  if ($exitCode -ne 0) {
    Write-Host "[FAIL] $table validation failed (exit=$exitCode)" -ForegroundColor Red
    break  # Parar no primeiro erro
  }
  
  Write-Host "[OK] $table validation passed" -ForegroundColor Green
}

# Limpar artefatos ao final
git restore -- docs\_generated\*
```

---

### 8.4 Validar com Cycle Warning (teams/seasons)

```powershell
# Tabelas com cycle: teams <-> seasons (FK bidirecional)
.\scripts\models_autogen_gate.ps1 `
  -Table "teams" `
  -Profile strict `
  -AllowCycleWarning

# Pré-requisito: models devem ter use_alter=True nas FKs
# app/models/team.py:
#   season_id: Mapped[int | None] = mapped_column(
#       ForeignKey("seasons.id", name="fk_teams_season_id", use_alter=True),
#       nullable=True
#   )
# app/models/season.py:
#   team_id: Mapped[int | None] = mapped_column(
#       ForeignKey("teams.id", name="fk_seasons_team_id", use_alter=True),
#       nullable=True
#   )
```

---

### 8.5 Capturar Exit Code Corretamente (Anti-Pattern)

```powershell
# ❌ ERRADO: pipeline mascara exit code
.\scripts\models_autogen_gate.ps1 -Table "attendance" | Out-File log.txt
if ($LASTEXITCODE -ne 0) { exit 1 }  # $LASTEXITCODE foi mascarado por Out-File

# ✅ CORRETO: capturar imediatamente
.\scripts\models_autogen_gate.ps1 -Table "attendance"
$exitCode = $LASTEXITCODE
Write-Host "Exit code: $exitCode"

# Ou com redirecionamento (mas capturar antes de qualquer pipeline)
.\scripts\models_autogen_gate.ps1 -Table "attendance" *>&1 | Tee-Object log.txt
$exitCode = $LASTEXITCODE  # Corrompido por Tee-Object

# Alternativa (rodar, capturar, depois redirecionar se necessário)
.\scripts\models_autogen_gate.ps1 -Table "attendance"
$exitCode = $LASTEXITCODE
Write-Host "Exit: $exitCode" | Out-File -Append log.txt
```

---

## 9. Troubleshooting

### 9.1 Por Sintoma

#### "env var not set: DATABASE_URL_SYNC"

**Causa:** Variável de ambiente não definida.

**Resolução:**
```powershell
# Opção A: Definir manualmente
$env:DATABASE_URL_SYNC = "postgresql+psycopg2://user:pass@localhost:5432/hb_track_db"

# Opção B: Verificar .env existe e contém DATABASE_URL_SYNC ou DATABASE_URL
Test-Path ".env"
Select-String -Path ".env" -Pattern "DATABASE_URL"

# Opção C: Usar -DbUrl override
.\scripts\models_autogen_gate.ps1 -Table "attendance" -DbUrl "postgresql+psycopg2://..."
```

---

#### "Missing .hb_guard\baseline.json"

**Causa:** Baseline nunca foi criado.

**Resolução:**
```powershell
& "venv\Scripts\python.exe" scripts\agent_guard.py snapshot `
  --root "." `
  --out ".hb_guard\baseline.json" `
  --exclude "venv,.venv,__pycache__,.pytest_cache,docs\_generated"

git add .hb_guard\baseline.json
git commit -m "chore(guard): create baseline"
```

---

#### "CREATE TABLE for '<table>' not found in schema.sql"

**Causa:** schema.sql desatualizado ou tabela não existe no DB.

**Resolução:**
```powershell
# Atualizar schema.sql
Set-Location "C:\HB TRACK"
powershell -NoProfile -ExecutionPolicy Bypass -File "scripts\inv.ps1" refresh

# Verificar se tabela existe
Select-String -Path "Hb Track - Backend\docs\_generated\schema.sql" -Pattern "CREATE TABLE.*<table>"

# Se tabela não existe: criar migration
cd "Hb Track - Backend"
alembic revision -m "create <table> table"
# Editar migration, definir DDL
alembic upgrade head
# Re-gerar schema.sql
cd ..
powershell -NoProfile -ExecutionPolicy Bypass -File "scripts\inv.ps1" refresh
```

---

#### Working tree sujo após rodar gate (docs/_generated/*)

**Causa:** Artefatos gerados não foram limpos.

**Resolução:**
```powershell
# No backend root
Set-Location "C:\HB TRACK\Hb Track - Backend"
git restore -- docs\_generated\*

# Verificar
git status --porcelain  # Deve mostrar apenas mudanças intencionais (app/models/*)
```

---

#### Cycle warning sem -AllowCycleWarning (teams/seasons)

**Sintoma:**
```
[FAIL] cycle warning detected (teams<->seasons). Use -AllowCycleWarning with mitigation evidence.
Exit 2
```

**Resolução:**
```powershell
# Validar que mitigações estão presentes (use_alter=True em ambos FKs)
Select-String -Path "app\models\team.py" -Pattern "use_alter\s*=\s*True"
Select-String -Path "app\models\season.py" -Pattern "use_alter\s*=\s*True"

# Se mitigações presentes, usar flag
.\scripts\models_autogen_gate.ps1 -Table "teams" -AllowCycleWarning

# Se mitigações ausentes, adicionar ao model:
# ForeignKey("...", name="fk_...", use_alter=True)
```

---

### 9.2 Performance e Observabilidade

#### Output verboso (debug)

```powershell
$VerbosePreference = "Continue"
.\scripts\models_autogen_gate.ps1 -Table "attendance" -Profile strict
```

#### Rastrear comandos executados

```powershell
# Habilitar command tracing
Set-PSDebug -Trace 1
.\scripts\models_autogen_gate.ps1 -Table "attendance"
Set-PSDebug -Trace 0
```

#### Tempo de execução

```powershell
Measure-Command {
  .\scripts\models_autogen_gate.ps1 -Table "attendance"
}
```

---

## 10. FAQ

### Q1: Quando usar `-Create` vs sem `-Create`?

**A:** Use `-Create` APENAS na primeira vez, ao criar um novo model. Isso atualiza o baseline automaticamente. Para modificações subsequentes, **não use** `-Create` (baseline deve ser atualizado manualmente após commit).

---

### Q2: Qual a diferença entre `-Profile fk`, `strict`, e `lenient`?

**A:**
- **`fk`**: Valida apenas foreign keys (nome, referência, ondelete)
- **`strict`**: Valida FKs + nullable explícito + tipos exatos + constraints + indexes (recomendado)
- **`lenient`**: Valida FKs + permite equivalências de tipos (ex: varchar|None ↔ text)

---

### Q3: Preciso commitar `docs/_generated/*` após rodar gate?

**A:** **NÃO.** Sempre limpe com `git restore -- docs\_generated\*` após validação. Esses arquivos são artefatos descartáveis gerados a cada run.

---

### Q4: O que fazer se baseline está "órfão" (SHA mismatch em scripts que não foram modificados)?

**A:** 
1. Verificar se há mudanças pendentes: `git status --porcelain`
2. Se repo limpo, baseline está desatualizado: criar backup branch e atualizar baseline via snapshot
3. Nunca fazer snapshot automaticamente sem revisar mudanças

---

### Q5: Posso rodar gates em CI/CD?

**A:** Sim, mas:
- Garantir DATABASE_URL_SYNC disponível (via secrets)
- Baseline deve estar commitado no repo
- Rodar sempre em modo validation (sem `-Create`)
- Exit code != 0 deve falhar o job

---

### Q6: Como validar todos os models de uma vez?

**A:** Criar script wrapper (ver Seção 8.3), ou usar `parity_scan.ps1` sem `-TableFilter`:

```powershell
.\scripts\parity_scan.ps1 -FailOnStructuralDiffs
# Exit 0: todos models alinhados
# Exit 2: diffs em algum model (ver parity_report.json)
```

---

### Q7: Exit code 2 mas parity_report.json vazio ou sem diffs estruturais?

**A:** Possível cause: cycle warning (teams/seasons). Verificar seção `"warnings"` do report:

```powershell
$report = Get-Content "docs\_generated\parity_report.json" -Raw | ConvertFrom-Json
$report.warnings | Where-Object { $_.category -eq "sa_warning" }
```

Se cycle warning presente, usar `-AllowCycleWarning`.

---

## 11. Referências

### 11.1 Documentos Relacionados

- **ADR-MODELS-001**: [docs/ADR/_INDEX_ADR.md](C:/HB TRACK/docs/ADR/_INDEX_ADR.md)
- **CHECKLIST-CANONICA-MODELS**: [docs/execution_tasks/CHECKLIST-CANONICA-MODELS.md](C:/HB TRACK/docs/execution_tasks/CHECKLIST-CANONICA-MODELS.md)
- **Exit Codes Reference**: [docs/references/exit_codes.md](C:/HB TRACK/docs/references/exit_codes.md)
- **PRD (Seção 8.3 - RDB)**: [docs/00_product/PRD_HB_TRACK.md](C:/HB TRACK/docs/00_product/PRD_HB_TRACK.md)
- **Canonical Sources**: [docs/_canon/00_START_HERE.md](C:/HB TRACK/docs/_canon/00_START_HERE.md)

### 11.2 Scripts Relacionados

- **models_autogen_gate.ps1**: [Hb Track - Backend/scripts/models_autogen_gate.ps1](C:/HB TRACK/Hb Track - Backend/scripts/models_autogen_gate.ps1)
- **parity_gate.ps1**: [Hb Track - Backend/scripts/parity_gate.ps1](C:/HB TRACK/Hb Track - Backend/scripts/parity_gate.ps1)
- **parity_scan.ps1**: [Hb Track - Backend/scripts/parity_scan.ps1](C:/HB TRACK/Hb Track - Backend/scripts/parity_scan.ps1)
- **autogen_model_from_db.py**: [Hb Track - Backend/scripts/autogen_model_from_db.py](C:/HB TRACK/Hb Track - Backend/scripts/autogen_model_from_db.py)
- **agent_guard.py**: [Hb Track - Backend/scripts/agent_guard.py](C:/HB TRACK/Hb Track - Backend/scripts/agent_guard.py)
- **model_requirements.py**: [Hb Track - Backend/scripts/model_requirements.py](C:/HB TRACK/Hb Track - Backend/scripts/model_requirements.py)

---

## 12. Changelog do Documento

| Versão | Data | Autor | Mudanças |
|--------|------|-------|----------|
| 1.0 | 2026-02-09 | HB Track Engineering Team | Criação inicial: documentação completa dos 6 scripts de validação de models |

---

## 13. Notas Finais

### 13.1 Do's and Don'ts

#### ✅ DO:
- Sempre rodar `git status --porcelain` antes e depois de gates
- Sempre limpar `docs/_generated/*` após validação
- Capturar `$LASTEXITCODE` imediatamente após comando
- Usar venv do backend (`venv\Scripts\python.exe`)
- Commitar baseline após snapshot manual
- Usar `-Allow` para autorizar modificações legítimas

#### ❌ DON'T:
- Não criar arquivos temporários dentro do repo (use `C:\Temp\`)
- Não fazer snapshot automático sem revisar mudanças
- Não usar Invoke-Expression (quebra quoting em PowerShell 5.1)
- Não usar comandos POSIX (ls, cat, grep) — usar PowerShell equivalents
- Não commitar `docs/_generated/*`
- Não encadear comandos com `&&` ou `||` (usar PowerShell `;` ou blocos try/catch)

### 13.2 Responsabilidades

- **Humano/Agent:** Revisar output, diagnosticar failures, aprovar snapshots, commitar mudanças
- **Scripts:** Executar validações deterministicamente, reportar exit codes específicos, gerar logs padronizados
- **CI/CD (futuro):** Rodar gates automaticamente em PRs, bloquear merge se exit != 0

---

**Última atualização:** 2026-02-09  
**Próxima revisão:** Após implementação de CI jobs ou mudanças maiores no pipeline
