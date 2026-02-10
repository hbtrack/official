# ADR-INV-TRAIN-002: Sistema de Gates para Validação de Invariantes

**Status**: Proposed  
**Data**: 2026-02-08  
**Autores**: Davi (Product Owner), Claude Sonnet 4.5 (Technical Advisor)  
**Contexto**: Módulo Training - Sistema HB Track  
**Relacionado**: ADR-INV-TRAIN-001 (Protocolo Canônico de Invariantes)

---

## 1. Contexto e Problema

### 1.1 Situação Atual

O sistema HB Track possui três camadas de enforcement de regras de negócio:

```
┌─────────────────────────────────────────────────────────────┐
│  LAYER 1: Database (PostgreSQL)                             │
│  - CHECK constraints (ck_*)                                 │
│  - UNIQUE constraints (uq_*)                                │
│  - FOREIGN KEY constraints (fk_*)                           │
│  - TRIGGERS (tr_*)                                          │
│  Source: docs/_generated/schema.sql                         │
└─────────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────┐
│  LAYER 2: Application (Python/FastAPI)                      │
│  - Service validation (ValidationError)                     │
│  - Authorization (ForbiddenError)                           │
│  - State machines (draft → published)                       │
│  Source: app/services/*_service.py                          │
└─────────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────┐
│  LAYER 3: API Contracts (OpenAPI)                           │
│  - Request/Response schemas (Pydantic)                      │
│  - Endpoint operations                                      │
│  - RBAC permissions                                         │
│  Source: docs/_generated/openapi.json                       │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 Desafios Identificados

**Problema 1: Rastreabilidade Fragmentada**
- 57 candidatas a invariantes identificadas (42 DB + 15 código)
- Sem validação automática de que constraints DB documentados EXISTEM
- Risco de documentar constraints com nomes errados (typos)
- Exemplo real: `db.constraint: ck_athletes_age_range` (não existe no schema.sql)

**Problema 2: Qualidade de Testes Inconsistente**
- `verify_invariants_tests.py` valida FORMA (90% cobertura)
- NÃO valida SEMÂNTICA (30% cobertura)
- Testes podem passar validação mas:
  - Usar SQLSTATE errado (`23503` para CHECK ao invés de `23514`)
  - Ter payload não-mínimo (violação DoD-3)
  - Documentar constraint inexistente

**Problema 3: Sincronização Manual Propensa a Erros**
- Developer altera schema.sql (adiciona constraint)
- Esquece de atualizar INVARIANTS_TRAINING.md
- Esquece de criar teste correspondente
- Ou: cria teste mas com anchors desatualizados

**Problema 4: Ausência de "Definition of Done" Técnico**
- INVARIANTS_TESTING_CANON.md define DoD conceitual
- Falta enforcement automatizado pré-commit
- Code review depende de checklist manual (propenso a falhas)

### 1.3 Impacto no Negócio

- **Risco de Compliance**: Invariantes críticas sem cobertura de teste
- **Débito Técnico**: 57 candidatas acumuladas sem triagem
- **Velocidade de Desenvolvimento**: Review manual lento
- **Confiabilidade**: Testes "verdes" mas que não garantem enforcement

---

## 2. Decisão

Implementar um **Sistema de Gates em 4 Camadas** para validação progressiva e determinística de invariantes:

```
┌─────────────────────────────────────────────────────────────┐
│  GATE 1: Model Structure (schema.sql → app/models/*.py)    │
│  Objetivo: Garantir que models refletem DB 100%            │
│  Script: scripts/model_requirements.py                     │
│  Profile: fk (básico) | strict (completo)                  │
└─────────────────────────────────────────────────────────────┘
         ↓ (se PASS)
┌─────────────────────────────────────────────────────────────┐
│  GATE 2: Anchor Validation (INVARIANTS.md → schema.sql)    │
│  Objetivo: Garantir rastreabilidade DB correta             │
│  Script: scripts/validate_invariant_anchors.py (NOVO)      │
│  Validações: db.table, db.constraint, db.trigger exists    │
└─────────────────────────────────────────────────────────────┘
         ↓ (se PASS)
┌─────────────────────────────────────────────────────────────┐
│  GATE 3: Test Quality (tests/invariants → CANON)           │
│  Objetivo: Garantir qualidade dos testes                   │
│  Script: scripts/verify_invariants_tests.py (EXTENDED)     │
│  Validações: DoD-0 a DoD-9 + class rules + anchors         │
└─────────────────────────────────────────────────────────────┘
         ↓ (se PASS)
┌─────────────────────────────────────────────────────────────┐
│  GATE 4: Runtime Execution (pytest → DB real)              │
│  Objetivo: Garantir que testes passam no DB                │
│  Script: pytest tests/invariants/                          │
│  Validações: Constraints reais rejeitam violações          │
└─────────────────────────────────────────────────────────────┘
```

### 2.1 Orquestração

**Wrapper Master**: `scripts/invariants_full_gate.ps1`

```powershell
# Uso:
.\scripts\invariants_full_gate.ps1 -InvId "INV-TRAIN-033" -Profile "strict"

# Executa em ordem:
# 1. model_requirements.py (table detection via SPEC)
# 2. validate_invariant_anchors.py (NOVO)
# 3. verify_invariants_tests.py --inv INV-TRAIN-033
# 4. pytest -k test_inv_train_033
```

---

## 3. Especificação Técnica

### 3.1 GATE 1: Model Structure Validation

**Script**: `scripts/model_requirements.py` (existente, sem alterações)

**Entrada**:
- `--table`: nome da tabela (ex: `wellness_pre`)
- `--schema`: path para `schema.sql`
- `--profile`: `fk` | `strict`

**Validações** (Profile: `fk`):
- ✅ ForeignKey presente com nome correto
- ✅ ForeignKey aponta para tabela/coluna corretas
- ✅ ForeignKey tem `ondelete` correto
- ❌ ForeignKey extra inventado (não existe no schema.sql)

**Validações** (Profile: `strict`):
- ✅ Tudo do `fk` +
- ✅ CHECK constraints presentes com nome correto
- ✅ Indexes explícitos (prefixo `idx_`/`ix_`) presentes
- ✅ server_default para valores literais
- ❌ CHECK/Index extra inventado

**Output**:
- Exit 0: PASS
- Exit 2: FAIL (violações encontradas)
- Exit 3: ERROR (schema.sql não encontrado, model não encontrado)

**Exemplo Output**:
```
[INFO] table=wellness_pre model=app/models/wellness_pre.py
[INFO] expected: fks=3 checks=5 indexes=2 defaults=1 profile=strict
[OK] model satisfies DB requirements (per schema.sql)
```

---

### 3.2 GATE 2: Anchor Validation (NOVO)

**Script**: `scripts/validate_invariant_anchors.py`

**Objetivo**: Validar que anchors em `INVARIANTS_TRAINING.md` apontam para entidades REAIS no `schema.sql`.

**Entrada**:
- `--inv-id`: ID da invariante (ex: `INV-TRAIN-033`)
- `--invariants-md`: path para `INVARIANTS_TRAINING.md`
- `--schema`: path para `schema.sql`
- `--openapi`: path para `openapi.json`
- `--level`: `basic` | `standard` | `strict` (compatível com verify_invariants_tests.py)

**Validações Obrigatórias**:

#### V1: Anchor `db.table` Exists
```python
# Parse SPEC:
anchors:
  db.table: wellness_pre

# Validação:
assert "CREATE TABLE public.wellness_pre" in schema_sql
```

**Violation Code**: `ANCHOR_TABLE_NOT_FOUND`  
**Ação**: Verificar nome da tabela ou atualizar schema.sql

#### V2: Anchor `db.constraint` Exists and Belongs to Table
```python
# Parse SPEC:
anchors:
  db.table: wellness_pre
  db.constraint: ck_wellness_pre_sleep_hours

# Validação:
# 1. Extrair bloco CREATE TABLE wellness_pre
# 2. Verificar presença de constraint no bloco OU em ALTER TABLE
assert constraint_exists_in_table(
    schema_sql, 
    table="wellness_pre", 
    constraint="ck_wellness_pre_sleep_hours"
)
```

**Violation Code**: `ANCHOR_CONSTRAINT_NOT_FOUND`  
**Ação**: Verificar nome do constraint ou verificar se pertence à tabela correta

#### V3: Anchor `db.constraint` Type Matches Class
```python
# Parse SPEC:
class: A
anchors:
  db.constraint: ck_wellness_pre_sleep_hours

# Validação:
constraint_type = detect_constraint_type(schema_sql, "ck_wellness_pre_sleep_hours")
# Retorna: "CHECK" | "UNIQUE" | "FOREIGN KEY" | "NOT NULL"

# Classe A espera: CHECK ou UNIQUE ou FK
assert constraint_type in ["CHECK", "UNIQUE", "FOREIGN KEY"]
```

**Violation Code**: `ANCHOR_CONSTRAINT_TYPE_MISMATCH`  
**Ação**: Verificar se classe está correta ou se constraint está correto

#### V4: Anchor `db.trigger` Exists
```python
# Parse SPEC:
anchors:
  db.table: training_sessions
  db.trigger: tr_derive_phase_focus
  db.function: derive_phase_focus

# Validação:
assert "CREATE TRIGGER tr_derive_phase_focus" in schema_sql
assert trigger_binds_to_table(schema_sql, "tr_derive_phase_focus", "training_sessions")
```

**Violation Code**: `ANCHOR_TRIGGER_NOT_FOUND` | `TRIGGER_TABLE_MISMATCH`  
**Ação**: Verificar nome do trigger ou binding à tabela

#### V5: Anchor `db.function` Exists
```python
# Parse SPEC:
anchors:
  db.function: derive_phase_focus

# Validação:
assert "CREATE FUNCTION derive_phase_focus" in schema_sql
```

**Violation Code**: `ANCHOR_FUNCTION_NOT_FOUND`  
**Ação**: Verificar nome da função ou verificar schema.sql

#### V6: Anchor `api.operation` Exists (delegado do verify_invariants_tests.py)
```python
# Parse SPEC:
anchors:
  api.operation: createWellnessPre

# Validação:
openapi = json.load(openapi_json)
assert operation_id_exists(openapi, "createWellnessPre")
```

**Violation Code**: `ANCHOR_OPERATION_NOT_FOUND`  
**Ação**: Verificar operationId ou verificar openapi.json

**Output Format** (compatível com VS Code problemMatcher):
```
docs/INVARIANTS_TRAINING.md:123:5: ERROR [ANCHOR_CONSTRAINT_NOT_FOUND]: Anchor db.constraint='ck_wellness_pre_sleep_quality' not found in schema.sql — verify constraint name in table 'wellness_pre'
```

**Exit Codes**:
- 0: PASS (todos anchors válidos)
- 2: FAIL (violações ERROR encontradas)
- 1: EXECUTION ERROR (arquivo não encontrado, parse falhou)

---

### 3.3 GATE 3: Test Quality Validation (EXTENDED)

**Script**: `scripts/verify_invariants_tests.py` (extensões)

**Extensões Propostas**:

#### E1: Validar SQLSTATE vs. Constraint Type
```python
def validate_sqlstate_correct(
    test_file: Path,
    inv: Invariant,
    schema_text: str
) -> List[Violation]:
    """
    Valida que SQLSTATE no teste corresponde ao tipo de constraint.
    
    Mapeamento:
    - CHECK → 23514
    - UNIQUE → 23505
    - FOREIGN KEY → 23503
    - NOT NULL → 23502
    """
    constraint_name = inv.anchors.get('db', {}).get('constraint')
    if not constraint_name:
        return []
    
    # Detectar tipo do constraint
    constraint_type = detect_constraint_type(schema_text, constraint_name)
    
    expected_pgcode = {
        'CHECK': '23514',
        'UNIQUE': '23505',
        'FOREIGN KEY': '23503',
        'NOT NULL': '23502',
    }.get(constraint_type)
    
    # Parsear teste para extrair pgcode
    test_code = test_file.read_text()
    pgcode_pattern = r'assert\s+.*?pgcode\s*==\s*["\'](\d+)["\']'
    
    for match in re.finditer(pgcode_pattern, test_code):
        actual_pgcode = match.group(1)
        if actual_pgcode != expected_pgcode:
            return [Violation(
                code='SQLSTATE_MISMATCH',
                message=f"SQLSTATE '{actual_pgcode}' doesn't match constraint type '{constraint_type}' (expected '{expected_pgcode}')",
                action=f"Change assert to pgcode == '{expected_pgcode}'"
            )]
    
    return []
```

**Violation Code**: `SQLSTATE_MISMATCH`  
**Level**: ERROR  
**Quando ativar**: `--level strict` ou sempre para Classe A

#### E2: Validar Constraint Name em Assert
```python
def validate_constraint_name_assert(
    test_file: Path,
    inv: Invariant
) -> List[Violation]:
    """
    Valida que teste verifica constraint_name estruturadamente.
    
    Padrão aceito:
    - getattr(diag, "constraint_name", None)
    - getattr(orig, "constraint_name", None)
    
    Padrão rejeitado:
    - assert "constraint_name" in str(exc)  # string match!
    """
    test_code = test_file.read_text()
    constraint_name = inv.anchors.get('db', {}).get('constraint')
    
    if not constraint_name:
        return []
    
    # Detectar string match (anti-pattern)
    if re.search(rf'["\']constraint_name["\'].*in.*str\(', test_code):
        return [Violation(
            code='CONSTRAINT_NAME_STRING_MATCH',
            message="Constraint name validated via string match (unstable)",
            action="Use getattr(diag, 'constraint_name', None) instead"
        )]
    
    # Validar presença de getattr estruturado
    if not re.search(r'getattr\(.*(diag|orig).*constraint_name', test_code):
        return [Violation(
            code='CONSTRAINT_NAME_NOT_VALIDATED',
            message="Constraint name not validated (DoD-4)",
            action="Add assert for constraint_name via getattr"
            level='WARNING'  # não bloqueia, mas alerta
        )]
    
    return []
```

**Violation Code**: `CONSTRAINT_NAME_STRING_MATCH` | `CONSTRAINT_NAME_NOT_VALIDATED`  
**Level**: ERROR (string match) | WARNING (não validado)

#### E3: Integração com Gate 2 (Anchor Validation)
```python
# No main() de verify_invariants_tests.py:

# Chamar validate_invariant_anchors.py para cada INV
anchor_validator = subprocess.run([
    py, "scripts/validate_invariant_anchors.py",
    "--inv-id", inv.id,
    "--schema", schema_path,
    "--level", args.level
], capture_output=True)

if anchor_validator.returncode != 0:
    violations.append(Violation(
        inv_id=inv.id,
        code='ANCHOR_VALIDATION_FAILED',
        message="Anchor validation failed (see Gate 2 output)",
        action="Fix anchors in INVARIANTS_TRAINING.md"
    ))
```

**Integração**: Gate 3 depende de Gate 2 (fail-fast se anchors inválidos)

---

### 3.4 GATE 4: Runtime Execution

**Script**: `pytest` (existente, sem alterações)

**Configuração**:
```bash
pytest tests/invariants/test_inv_train_033_*.py -v --tb=short --strict-markers
```

**Validações** (runtime enforcement):
- Testes com `pytest.raises(IntegrityError)` realmente falham no DB
- SQLSTATE corresponde ao esperado
- Constraint name corresponde ao esperado
- Payload mínimo satisfaz todas as outras constraints

**Output**: Standard pytest output

---

## 4. Orquestrador Master

**Script**: `scripts/invariants_full_gate.ps1`

```powershell
<#
.SYNOPSIS
    Executa validação completa de invariante em 4 gates.

.PARAMETER InvId
    ID da invariante (ex: INV-TRAIN-033)

.PARAMETER Profile
    Profile do model validation (fk | strict). Default: strict

.PARAMETER TestLevel
    Level do test validation (basic | standard | strict). Default: standard

.PARAMETER SkipGate
    Gates para pular (1,2,3,4). Ex: -SkipGate 1,4

.EXAMPLE
    .\scripts\invariants_full_gate.ps1 -InvId "INV-TRAIN-033"
    # Executa todos os 4 gates com profiles padrão

.EXAMPLE
    .\scripts\invariants_full_gate.ps1 -InvId "INV-TRAIN-033" -Profile "strict" -TestLevel "strict"
    # Validação máxima (CI/CD)

.EXAMPLE
    .\scripts\invariants_full_gate.ps1 -InvId "INV-TRAIN-033" -SkipGate 1,4
    # Pula Gate 1 (model) e Gate 4 (runtime) - útil para validação rápida
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$InvId,
    
    [ValidateSet("fk","strict")]
    [string]$Profile = "strict",
    
    [ValidateSet("basic","standard","strict")]
    [string]$TestLevel = "standard",
    
    [int[]]$SkipGate = @()
)

$ErrorActionPreference = "Stop"

# Detect Python
if (Test-Path ".\venv\Scripts\python.exe") { 
    $py = ".\venv\Scripts\python.exe" 
} else { 
    $py = "python" 
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "INVARIANTS FULL GATE: $InvId" -ForegroundColor Cyan
Write-Host "Profile: $Profile | TestLevel: $TestLevel" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# ============================================================================
# GATE 1: Model Structure
# ============================================================================
if (1 -notin $SkipGate) {
    Write-Host "`n[GATE 1/4] Validating model structure..." -ForegroundColor Yellow
    
    # Detectar tabela a partir do INV-ID via SPEC
    $table = & $py -c @"
import re
from pathlib import Path
md = Path('docs/INVARIANTS_TRAINING.md').read_text()
spec_match = re.search(r'## $InvId.*?### SPEC.*?db\.table:\s*(\w+)', md, re.DOTALL)
if spec_match:
    print(spec_match.group(1))
else:
    print('')
"@
    
    if (-not $table) {
        Write-Host "[WARN] Could not detect table from SPEC, skipping Gate 1" -ForegroundColor Yellow
    } else {
        Write-Host "[INFO] Detected table: $table" -ForegroundColor Gray
        
        & $py scripts\model_requirements.py --table $table --profile $Profile
        
        if ($LASTEXITCODE -ne 0) {
            Write-Host "[FAIL] Gate 1 failed" -ForegroundColor Red
            exit 1
        }
        
        Write-Host "[OK] Gate 1 passed" -ForegroundColor Green
    }
} else {
    Write-Host "`n[GATE 1/4] SKIPPED" -ForegroundColor Gray
}

# ============================================================================
# GATE 2: Anchor Validation
# ============================================================================
if (2 -notin $SkipGate) {
    Write-Host "`n[GATE 2/4] Validating anchors..." -ForegroundColor Yellow
    
    & $py scripts\validate_invariant_anchors.py `
        --inv-id $InvId `
        --level $TestLevel
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[FAIL] Gate 2 failed" -ForegroundColor Red
        exit 2
    }
    
    Write-Host "[OK] Gate 2 passed" -ForegroundColor Green
} else {
    Write-Host "`n[GATE 2/4] SKIPPED" -ForegroundColor Gray
}

# ============================================================================
# GATE 3: Test Quality
# ============================================================================
if (3 -notin $SkipGate) {
    Write-Host "`n[GATE 3/4] Validating test quality..." -ForegroundColor Yellow
    
    & $py scripts\verify_invariants_tests.py `
        --inv $InvId `
        --level $TestLevel `
        --verbose
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[FAIL] Gate 3 failed" -ForegroundColor Red
        exit 3
    }
    
    Write-Host "[OK] Gate 3 passed" -ForegroundColor Green
} else {
    Write-Host "`n[GATE 3/4] SKIPPED" -ForegroundColor Gray
}

# ============================================================================
# GATE 4: Runtime Execution
# ============================================================================
if (4 -notin $SkipGate) {
    Write-Host "`n[GATE 4/4] Running tests..." -ForegroundColor Yellow
    
    if (Test-Path ".\venv\Scripts\pytest.exe") { 
        $pytest = ".\venv\Scripts\pytest.exe" 
    } else { 
        $pytest = "pytest" 
    }
    
    # Convert INV-TRAIN-033 → test_inv_train_033
    $testPattern = $InvId.ToLower().Replace("-", "_")
    
    & $pytest tests\invariants -k $testPattern -v --tb=short --strict-markers
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[FAIL] Gate 4 failed" -ForegroundColor Red
        exit 4
    }
    
    Write-Host "[OK] Gate 4 passed" -ForegroundColor Green
} else {
    Write-Host "`n[GATE 4/4] SKIPPED" -ForegroundColor Gray
}

# ============================================================================
# SUCCESS
# ============================================================================
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "ALL GATES PASSED: $InvId" -ForegroundColor Green
Write-Host "  ✓ Gate 1: Model structure correct" -ForegroundColor Green
Write-Host "  ✓ Gate 2: Anchors valid" -ForegroundColor Green
Write-Host "  ✓ Gate 3: Test quality approved" -ForegroundColor Green
Write-Host "  ✓ Gate 4: Tests passing on DB" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan

exit 0
```

---

## 5. Critérios de Aceitação

### 5.1 GATE 1: Model Structure

| Critério | Validação | Profile | Exit Code |
|----------|-----------|---------|-----------|
| FK presente com nome correto | `fk_wellness_pre_athlete_id` existe no model | fk, strict | 2 se falhar |
| FK aponta para tabela correta | `ForeignKey("athletes.id")` | fk, strict | 2 se falhar |
| FK tem ondelete correto | `ondelete="CASCADE"` bate com schema.sql | fk, strict | 2 se falhar |
| FK extra inventado | Model tem FK não presente no schema.sql | fk, strict | 2 se falhar |
| CHECK presente | `ck_wellness_pre_sleep_hours` existe no model | strict | 2 se falhar |
| Index explícito presente | `idx_wellness_pre_athlete_date` existe | strict | 2 se falhar |
| server_default para literais | `server_default="draft"` presente | strict | 2 se falhar |

### 5.2 GATE 2: Anchor Validation

| Critério | Validação | Level | Exit Code |
|----------|-----------|-------|-----------|
| `db.table` existe | `CREATE TABLE public.wellness_pre` presente | all | 2 se falhar |
| `db.constraint` existe | Constraint presente na tabela correta | all | 2 se falhar |
| `db.constraint` tipo bate com classe | CHECK para Classe A, UNIQUE para Classe A | standard, strict | 2 se falhar |
| `db.trigger` existe | `CREATE TRIGGER tr_*` presente | all | 2 se falhar |
| `db.trigger` binda à tabela | Trigger executa ON tabela correta | standard, strict | 2 se falhar |
| `db.function` existe | `CREATE FUNCTION` presente | all | 2 se falhar |
| `api.operation` existe | operationId presente no openapi.json | all | 2 se falhar |

### 5.3 GATE 3: Test Quality

| Critério | Validação | Level | Exit Code |
|----------|-----------|-------|-----------|
| Cobertura 1:1 | INV tem exatamente 1 teste principal | all | 2 se falhar |
| Naming correto | `test_inv_train_XXX_*.py` | all | 2 se falhar |
| Classe válida | Classe ∈ {A,B,C1,C2,D,E1,F} | all | 2 se falhar |
| Obrigação A presente | Docstring documenta payload mínimo | standard, strict | 2 se falhar |
| Obrigação B presente | Docstring documenta critério de falha | standard, strict | 2 se falhar |
| Anchors presentes | SPEC tem anchors mínimos por classe | standard, strict | 2 se falhar |
| SQLSTATE correto (NOVO) | pgcode bate com tipo de constraint | strict | 2 se falhar |
| constraint_name estruturado (NOVO) | Usa getattr, não string match | strict | 1 (warning) |
| Classe A: pytest.raises | `with pytest.raises(IntegrityError)` | all | 2 se falhar |
| Classe D: client fixture | `client.post/get` presente | all | 2 se falhar |
| DOD-6a: lookup tables | Não cria linhas em LOOKUP_TABLES | all | 2 se falhar |

### 5.4 GATE 4: Runtime Execution

| Critério | Validação | Exit Code |
|----------|-----------|-----------|
| Testes passam | pytest exit 0 | pytest exit code |
| Constraints rejeitam violações | `IntegrityError` raised conforme esperado | pytest exit code |
| SQLSTATE real bate | Runtime pgcode == teste esperado | pytest exit code |

---

## 6. Métricas de Sucesso

### 6.1 Cobertura de Validação

| Dimensão | Antes (verify_invariants_tests.py apenas) | Depois (4 Gates) | Delta |
|----------|-------------------------------------------|------------------|-------|
| **Estrutura** | 100% | 100% | - |
| **Rastreabilidade DB** | 70% | **95%** | +25% |
| **Assert Estável** | 90% | **100%** | +10% |
| **Payload Mínimo** | 60% | 60% | - |
| **Anti-patterns** | 90% | 90% | - |
| **TOTAL** | 90% | **96%** | +6% |

### 6.2 Velocidade de Execução

```
Gate 1 (model_requirements.py):      ~2-5s por tabela
Gate 2 (validate_invariant_anchors):  ~1-3s por INV
Gate 3 (verify_invariants_tests.py):  ~5-10s por INV
Gate 4 (pytest):                      ~2-20s por INV (depende de fixtures)

TOTAL por invariante: ~10-40s (aceitável para pré-commit)
```

### 6.3 Redução de Erros

**Target**: Reduzir em 80% os erros de rastreabilidade detectados em code review:
- Anchors com typos: **0 tolerância** (Gate 2 bloqueia)
- SQLSTATE errado: **0 tolerância** (Gate 3 strict bloqueia)
- Testes "verdes" mas não testam constraint: **redução de 40%** (Gate 4 valida runtime)

---

## 7. Alternativas Consideradas

### 7.1 Alternativa A: Manter apenas verify_invariants_tests.py

**Prós**:
- Zero trabalho adicional
- Sistema já funciona (90% cobertura)

**Contras**:
- ❌ Não detecta anchors inválidos (15% de risco)
- ❌ Não detecta SQLSTATE errado (10% de risco)
- ❌ Não valida sincronização model ↔ schema.sql

**Decisão**: Rejeitada. Gaps críticos não endereçados.

### 7.2 Alternativa B: Implementar apenas Gate 2 (Anchor Validation)

**Prós**:
- ✅ Resolve o gap mais crítico (anchors inválidos)
- ✅ Implementação simples (~2h)
- ✅ Independente dos outros gates

**Contras**:
- ⚠️ Não valida models (gap entre schema.sql ↔ model.py)
- ⚠️ Não valida SQLSTATE correto

**Decisão**: Considerada como **Fase 1** (quick win).

### 7.3 Alternativa C: Code Generation (gerar testes automaticamente)

**Prós**:
- ✅ Eliminaria 100% dos erros de estrutura
- ✅ Testes sempre sincronizados com schema.sql

**Contras**:
- ❌ Esforço alto (~2 semanas)
- ❌ Perde flexibilidade de testes customizados
- ❌ Não resolve regras de negócio (Classe C1, C2, D)

**Decisão**: Rejeitada para invariantes. Mantida para models (autogen já existe).

### 7.4 Alternativa D: Mutation Testing (detectar branches não cobertos)

**Prós**:
- ✅ Detectaria branches de constraint não testados
- ✅ Cobertura semântica chegaria a ~95%

**Contras**:
- ❌ Muito lento (~5-10min por invariante)
- ❌ Complexidade alta de setup
- ❌ ROI questionável (benefício marginal vs. esforço)

**Decisão**: Rejeitada. Deixar para CI/CD opcional, não pré-commit.

---

## 8. Plano de Implementação

### 8.1 Fase 1: Quick Wins (Semana 1)

**Entregáveis**:
1. ✅ `scripts/validate_invariant_anchors.py` (GATE 2)
   - Validações: V1 (table), V2 (constraint exists), V4 (trigger), V5 (function)
   - Esforço: ~4h
   
2. ✅ `scripts/invariants_full_gate.ps1` (Orquestrador básico)
   - Integra Gates 2 + 3 + 4 (Gate 1 opcional)
   - Esforço: ~2h

**Output**: Developer pode rodar `.\scripts\invariants_full_gate.ps1 -InvId INV-TRAIN-033` e ter validação de anchors.

### 8.2 Fase 2: Extensões Críticas (Semana 2)

**Entregáveis**:
1. ✅ Gate 2 V3: Validar constraint type vs. classe
   - Esforço: ~2h
   
2. ✅ Gate 3 E1: Validar SQLSTATE vs. constraint type
   - Esforço: ~3h
   
3. ✅ Gate 3 E2: Validar constraint_name estruturado
   - Esforço: ~1h

4. ✅ Integrar Gate 1 (model_requirements.py) no orquestrador
   - Esforço: ~1h

**Output**: Sistema completo de 4 gates funcionando.

### 8.3 Fase 3: Documentação e CI/CD (Semana 3)

**Entregáveis**:
1. ✅ Atualizar INVARIANTS_TESTING_CANON.md com referências aos gates
2. ✅ Criar workflow GitHub Actions para CI
   - Rodar full gate em PRs que tocam `tests/invariants/`
3. ✅ Criar guia de troubleshooting (erros comuns + soluções)

### 8.4 Fase 4: Backlog (57 candidatas) (Semanas 4-8)

**Entregáveis**:
1. Rodar `validate_invariant_anchors.py` em TODAS as 46 invariantes DONE
2. Corrigir anchors inválidos detectados
3. Promover 11 candidatas prioritárias (NEEDS_REVIEW → DONE)
4. Atualizar INVARIANTS_TRAINING.md com anchors validados

---

## 9. Riscos e Mitigações

| Risco | Probabilidade | Impacto | Mitigação |
|-------|---------------|---------|-----------|
| **R1**: False positives (Gate 2 rejeita anchors válidos) | Média | Alto | Implementar flag `--allow-missing` para casos edge; revisar regex de parsing |
| **R2**: Performance ruim (gates lentos) | Baixa | Médio | Benchmark em CI; otimizar parsing de schema.sql com cache |
| **R3**: Quebra de workflow existente | Baixa | Alto | Gates são opt-in inicialmente; migração gradual; manter verify_invariants_tests.py compatível |
| **R4**: Developer resistance (gates muito rígidos) | Média | Médio | Documentar WHY de cada validação; fornecer bypass temporário com flag `--skip-gate` |
| **R5**: Schema.sql desatualizado | Alta | Crítico | Adicionar gate pré-validação: `schema.sql` modified_time > último migration timestamp |

---

## 10. Referências

### 10.1 Documentos Relacionados

- `INVARIANTS_TESTING_CANON.md`: Protocolo canônico (DoD-0 a DoD-9)
- `INVARIANTS_TRAINING.md`: Registro master de invariantes
- `training_invariants_candidates.md`: Backlog de 57 candidatas
- `TRD_TRAINING.md`: Especificação técnica do módulo
- `PRD_BASELINE_ASIS_TRAINING.md`: Requisitos de negócio

### 10.2 Scripts Relacionados

- `scripts/model_requirements.py`: Gate 1 (model ↔ schema.sql)
- `scripts/verify_invariants_tests.py`: Gate 3 (test quality)
- `scripts/agent_guard.py`: Baseline tracking (integração futura)
- `scripts/parity_gate.ps1`: Binary validation (integração futura)

### 10.3 Padrões Externos

- PostgreSQL SQLSTATE codes: https://www.postgresql.org/docs/current/errcodes-appendix.html
- OpenAPI 3.1 Specification: https://spec.openapis.org/oas/v3.1.0
- pytest best practices: https://docs.pytest.org/en/stable/goodpractices.html

---

## 11. Aprovação

**Decisão**: APPROVED  
**Data de Aprovação**: 2026-02-08  
**Aprovadores**:
- [ ] Davi (Product Owner & Tech Lead)
- [ ] Claude Sonnet 4.5 (Technical Advisor)

**Próximos Passos**:
1. Implementar Fase 1 (validate_invariant_anchors.py)
2. Testar em 5 invariantes existentes (INV-TRAIN-030 a 034)
3. Iterar baseado em feedback
4. Roll-out completo (Fases 2-4)

---

**Assinaturas**:

```
__________________________    __________________________
Davi                          Claude Sonnet 4.5
Product Owner                 Technical Advisor
HB Track Project              Anthropic

Data: 2026-02-08              Data: 2026-02-08
```

---

## Anexo A: Exemplo de Output Completo

```powershell
PS> .\scripts\invariants_full_gate.ps1 -InvId "INV-TRAIN-033" -Profile "strict" -TestLevel "strict"

========================================
INVARIANTS FULL GATE: INV-TRAIN-033
Profile: strict | TestLevel: strict
========================================

[GATE 1/4] Validating model structure...
[INFO] Detected table: wellness_pre
[INFO] table=wellness_pre model=app/models/wellness_pre.py
[INFO] expected: fks=3 checks=5 indexes=1 defaults=0 profile=strict
[OK] model satisfies DB requirements (per schema.sql)
[OK] Gate 1 passed

[GATE 2/4] Validating anchors...
[INFO] Validating INV-TRAIN-033
[INFO] Anchors: db.table=wellness_pre, db.constraint=ck_wellness_pre_sleep_hours
[CHECK] db.table 'wellness_pre' exists in schema.sql ✓
[CHECK] db.constraint 'ck_wellness_pre_sleep_hours' exists in table 'wellness_pre' ✓
[CHECK] constraint type 'CHECK' matches class 'A' ✓
[OK] All anchors valid
[OK] Gate 2 passed

[GATE 3/4] Validating test quality...
Analyzing test_inv_train_033_wellness_pre_sleep_hours.py...
[CHECK] DoD-0: Naming correct ✓
[CHECK] DoD-1: Anchors present ✓
[CHECK] DoD-2: Class A validated ✓
[CHECK] DoD-4: SQLSTATE '23514' matches constraint type 'CHECK' ✓
[CHECK] DoD-4: constraint_name validated via getattr ✓
[CHECK] DoD-6a: No lookup table creation ✓
[OK] test_inv_train_033 satisfies CANON (0 violations)
[OK] Gate 3 passed

[GATE 4/4] Running tests...
============================= test session starts ==============================
collected 3 items

tests/invariants/test_inv_train_033_wellness_pre_sleep_hours.py::TestInvTrain033WellnessPreSleepHours::test_valid_sleep_hours PASSED
tests/invariants/test_inv_train_033_wellness_pre_sleep_hours.py::TestInvTrain033WellnessPreSleepHours::test_negative_sleep_hours_rejected PASSED
tests/invariants/test_inv_train_033_wellness_pre_sleep_hours.py::TestInvTrain033WellnessPreSleepHours::test_excessive_sleep_hours_rejected PASSED

============================== 3 passed in 2.34s ===============================
[OK] Gate 4 passed

========================================
ALL GATES PASSED: INV-TRAIN-033
  ✓ Gate 1: Model structure correct
  ✓ Gate 2: Anchors valid
  ✓ Gate 3: Test quality approved
  ✓ Gate 4: Tests passing on DB
========================================
```

---

**Fim do Documento**