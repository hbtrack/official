# ADR-015-ADR-INV: Workflow Canônico de Invariantes — Local-First com Gates Automatizados

**Status:** Approved
**Data:** 2026-02-10
**Autores:** Davi (Product Owner), Claude Sonnet 4.5 (Technical Advisor)
**Contexto:** Módulo Training - Sistema HB Track
**Relacionado:** ADR-012-ADR-INV-TRAIN (Sistema de Gates), ADR-004-ADR-TRAIN-invariantes-como-contrato

---

## 1. Contexto e Problema

### 1.1 Situação Atual

O sistema HB Track possui um ecossistema de invariantes de negócio que são enforced em múltiplas camadas (DB, service, API). A gestão deste ecossistema envolve:

- **51 invariantes confirmadas** (INV-TRAIN-001 a INV-TRAIN-051)
- **57 candidatas** (42 DB + 15 código) aguardando promoção
- **3 artefatos canônicos (SSOT)**: `schema.sql`, `openapi.json`, `alembic_state.txt`
- **8 documentos de protocolo** (CANON, PROTOCOL, GUARDRAILS, TEMPLATES)
- **4 gates automatizados** (guard, parity, requirements, invariants)

### 1.2 Desafios Identificados

**Problema 1: Fragmentação do Workflow**
- Developer cria invariante → esquece de atualizar SSOT → gates falham
- Developer atualiza SPEC → esquece de criar teste → cobertura incompleta
- Developer roda teste → passa local → falha em CI/CD por drift de baseline
- 5 comandos distintos (`refresh`, `gate`, `drift`, `promote`, `all`) sem clareza de ordem

**Problema 2: Falta de "Definition of Done" Operacional**
- INVARIANTS_TESTING_CANON.md define DoD conceitual (DoD-0 a DoD-9)
- INV_TASK_TEMPLATE.md define passos manuais
- INVARIANTS_AGENT_PROTOCOL.md define regras para agents
- **Falta**: workflow canônico unificado e auditável de ponta a ponta

**Problema 3: Golden Baseline Drift sem Governança**
- Developer altera `verify_invariants_tests.py` → 36 goldens ficam outdated
- Developer altera `INVARIANTS_TRAINING.md` (SPEC) → drift em massa
- Promoção manual propensa a erro: copiar pasta errada, esquecer re-run, etc.

**Problema 4: Ausência de Rastreabilidade Temporal**
- Não há audit log de quando cada invariante passou por cada gate
- Não há evidência de que todos os gates passaram antes de commit
- Reports timestamped, mas sem agregação (difícil ver "status do sistema")

### 1.3 Impacto no Negócio

- **Risco de Regressão**: Invariantes críticas podem ser desabilitadas sem detecção
- **Débito Técnico**: 57 candidatas acumuladas sem workflow claro de promoção
- **Velocidade de Desenvolvimento**: Developer precisa aprender 5 comandos + 8 docs
- **Confiabilidade**: Exit codes semânticos não uniformes entre scripts

---

## 2. Decisão

Implementar um **Workflow Canônico em 5 Fases** para gestão de invariantes, com orquestração via `inv.ps1` (wrapper master) e validação via gates automatizados.

### 2.1 Visão Geral do Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│  FASE 0: SSOT Refresh (Pré-requisito)                          │
│  ─────────────────────────────────────────────────────────────  │
│  Comando: .\scripts\inv.ps1 refresh                            │
│  Objetivo: Garantir que artefatos canônicos estão atualizados  │
│  Output: schema.sql, openapi.json, alembic_state.txt           │
│  Exit Codes: 0 (success) | 1 (failure)                         │
└─────────────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────────┐
│  FASE 1: Worklist & SPEC Creation                              │
│  ─────────────────────────────────────────────────────────────  │
│  Input: training_invariants_candidates.md                       │
│  Ação: Developer/Agent seleciona candidata + cria SPEC YAML    │
│  Obrigações: Anchor validation (table, constraint, trigger)    │
│  Output: SPEC block em INVARIANTS_TRAINING.md                  │
└─────────────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────────┐
│  FASE 2: Test Implementation                                    │
│  ─────────────────────────────────────────────────────────────  │
│  Input: SPEC block (id, class, anchors, tests.primary)         │
│  Ação: Developer/Agent cria test_inv_train_XXX_*.py            │
│  Helper: tests/_helpers/pg_error.py (assert_pg_constraint)     │
│  Output: Teste conforme DoD-0 a DoD-9                          │
└─────────────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────────┐
│  FASE 3: Gate Individual (Loop até EXIT=0)                     │
│  ─────────────────────────────────────────────────────────────  │
│  Comando: .\scripts\inv.ps1 gate INV-TRAIN-XXX                 │
│  Gates:                                                         │
│    - verify_invariants_tests.py (quality)                      │
│    - pytest (runtime)                                           │
│  Output: Report timestamped em docs/_generated/_reports/       │
│  Exit Codes: 0 (PASS) | 1 (FAIL) | 3 (DRIFT/OUTDATED)         │
└─────────────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────────┐
│  FASE 4: Golden Baseline Promotion (Condicional)                │
│  ─────────────────────────────────────────────────────────────  │
│  Condição: EXIT=3 AND VERIFY_EXIT=0 AND PYTEST_EXIT=0          │
│  Comando: .\scripts\inv.ps1 promote                            │
│  Ação: Promove reports recentes para _golden_CLASS/            │
│  Output: Golden baselines atualizados                           │
│  Validação: Re-run gate all (EXIT_ALL=0)                       │
└─────────────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────────┐
│  FASE 5: Gate All (Validação Completa)                         │
│  ─────────────────────────────────────────────────────────────  │
│  Comando: .\scripts\inv.ps1 all                                │
│  Objetivo: Validar TODAS as invariantes com golden             │
│  Output: Summary table (PASS/DRIFT/FAIL por INV)               │
│  Exit Codes: 0 (ALL PASS) | 3 (DRIFT) | 1 (FAIL)              │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Componentes do Sistema

#### 2.2.1 Wrapper Master: `inv.ps1`

**Responsabilidade**: Orquestração unificada de comandos de invariantes.

**Comandos Disponíveis**:
- `refresh` / `ssot`: Regenera artefatos canônicos (schema.sql, openapi.json, alembic_state.txt)
- `gate <INV-ID>`: Executa gate individual para uma invariante
- `all`: Executa gate para todas as invariantes com golden baseline
- `drift`: Dry-run (WhatIf) de promoções pendentes
- `promote`: Promoção bulk de goldens (após drift legítimo)

**Exit Codes Semânticos**:
- `0`: PASS (pode prosseguir)
- `1`: FAIL (erros de qualidade ou runtime)
- `3`: DRIFT (canonical inputs mudaram, promoção necessária)

#### 2.2.2 Gate Runner Individual: `run_invariant_gate.ps1`

**Responsabilidade**: Validação de invariante individual em 3 etapas.

**Etapas**:
1. **Parse SPEC**: Extrai `tests.primary` e `tests.node` do YAML
2. **Run Verifier**: Executa `verify_invariants_tests.py --inv <ID>`
3. **Run Pytest**: Executa `pytest <test_file>::<test_node>`

**Outputs Gerados** (por run timestamped):
- `verify.txt`: Output completo do verifier
- `verify_inv.txt`: Violations filtradas (apenas este INV)
- `pytest.txt`: Output completo do pytest
- `hashes.txt`: SHA256 dos canonical inputs (drift detection)
- `meta.txt`: Metadata (inv_id, exit_code, primary_class, etc.)

**Golden Drift Detection**:
- Compara hashes de: `openapi.json`, `schema.sql`, `INVARIANTS_TRAINING.md`, `verify_invariants_tests.py`, `test_file`
- Se qualquer hash diverge do golden → EXIT=3
- Se golden não existe → EXIT=3 com `golden_missing: YES`

#### 2.2.3 Gate Runner Bulk: `run_invariant_gate_all.ps1`

**Responsabilidade**: Validação de todas as invariantes + promoção bulk.

**Discovery de Invariantes**:
- Procura por diretórios `_golden_*` em `docs/_generated/_reports/INV-*`
- Também descobre INVs com `golden_missing: YES` em reports recentes

**Modos de Operação**:
- **Normal**: Executa gate para cada INV, reporta summary
- **-WhatIf** (drift): Dry-run, imprime comandos de promoção sem executar
- **-Promote**: Executa promoções, re-roda gates, exige EXIT_ALL=0

**Critérios de Promoção Automática**:
- EXIT_CODE = 3 (drift detectado)
- VERIFY_EXIT = 0 (sem erros de qualidade)
- PYTEST_EXIT = 0 (testes passando)

**Validação Pós-Promoção**:
- Re-executa `run_invariant_gate_all.ps1` (sem -Promote)
- Exige EXIT_ALL=0 (todas as invariantes PASS)
- Falha se qualquer invariante ainda tiver drift

#### 2.2.4 Validador de Qualidade: `verify_invariants_tests.py`

**Responsabilidade**: Validação de conformidade com INVARIANTS_TESTING_CANON.md.

**Validações Implementadas**:
- **DoD-0**: Nomenclatura (arquivo, classe, métodos)
- **DoD-1**: Evidências estáveis (anchors no docstring)
- **DoD-2**: Prova por classe (A/B/C1/C2/D/E1/F)
- **DoD-3**: Anti-falso-positivo (payload mínimo)
- **DoD-4**: Assert estável (SQLSTATE, constraint_name)
- **DoD-5**: Isolamento de sessão (rollback após IntegrityError)
- **DoD-6**: Anti-colisão (sem IDs fixos)
- **DoD-6a**: Lookup tables (sem INSERT em seed tables)
- **DoD-7**: Sensibilidade (mínima violação específica)
- **DoD-8**: Fixtures vinculadas (async_db para Classe A)
- **DoD-9**: Pipeline aware (artefatos atualizados)

**Modos de Validação**:
- `--level basic`: DoD-0, coverage 1:1
- `--level standard`: DoD-0 a DoD-9 (padrão)
- `--level strict`: Standard + SPEC validation

**Output Format** (VS Code compatible):
```
file:line:col: LEVEL [CODE]: message — action
```

**Exit Codes**:
- `0`: PASS (sem violations)
- `2`: FAIL (violations ERROR encontradas)

#### 2.2.5 Helper Canônico: `pg_error.py`

**Responsabilidade**: Abstração driver-agnostic para validação de constraints DB.

**API Pública**:
```python
from tests._helpers.pg_error import assert_pg_constraint_violation

assert_pg_constraint_violation(
    exc_info,              # pytest.ExceptionInfo[IntegrityError]
    expected_sqlstate,     # "23514" (CHECK) | "23505" (UNIQUE)
    expected_constraint    # "ck_wellness_pre_sleep_hours"
)
```

**Benefícios**:
- ✅ Suporta psycopg2 (sync) e asyncpg (async)
- ✅ Elimina acesso direto a `orig.diag` / `orig.__cause__`
- ✅ Reduz 5 linhas → 1 chamada
- ✅ Centraliza lógica de extração

---

## 3. Especificação Técnica

### 3.1 FASE 0: SSOT Refresh

#### 3.1.1 Objetivo

Garantir que artefatos canônicos (schema.sql, openapi.json, alembic_state.txt) refletem 100% o estado atual do banco de dados e da API.

#### 3.1.2 Comando

```powershell
.\scripts\inv.ps1 refresh
# Alias: .\scripts\inv.ps1 ssot
```

#### 3.1.3 Fluxo Interno

```powershell
# 1. Executa generate_docs.py (backend)
cd "Hb Track - Backend"
python scripts/generate_docs.py

# 2. Valida que os 3 artefatos foram gerados
Test-Path docs\_generated\schema.sql       # ✓
Test-Path docs\_generated\openapi.json     # ✓
Test-Path docs\_generated\alembic_state.txt # ✓
```

#### 3.1.4 Validações

| Artefato | Validação | Ação se Falhar |
|----------|-----------|----------------|
| schema.sql | File exists + size > 0 | EXIT=1, pedir geração manual |
| openapi.json | File exists + valid JSON | EXIT=1, verificar FastAPI app |
| alembic_state.txt | File exists | EXIT=1, rodar alembic current |

#### 3.1.5 Exit Codes

- `0`: Todos os artefatos gerados com sucesso
- `1`: Falha na geração (ver logs)

#### 3.1.6 Quando Executar

- **Obrigatório**: Após alterar modelos SQLAlchemy
- **Obrigatório**: Após executar migrações Alembic
- **Obrigatório**: Após alterar routers FastAPI
- **Recomendado**: Antes de criar nova invariante
- **Recomendado**: Antes de promoção bulk de goldens

---

### 3.2 FASE 1: Worklist & SPEC Creation

#### 3.2.1 Objetivo

Selecionar candidata de invariante, validar evidências, e criar SPEC YAML normativo.

#### 3.2.2 Input

**Fonte**: `docs/02-modulos/training/INVARIANTS/training_invariants_candidates.md`

**Formato**:
```markdown
### attendance

| Nome | Tipo | Linha | Ação Sugerida |
|------|------|-------|---------------|
| `ck_attendance_correction_fields` | CHECK | `schema.sql:673` | NEEDS_REVIEW — ... |
```

#### 3.2.3 Seleção de Candidata

**Critérios de Priorização**:
1. **DONE** (já promovida): pular
2. **promover** (alta prioridade): processar
3. **NEEDS_REVIEW** (média prioridade): avaliar
4. **ignorar** (baixa prioridade): pular

**Template de Decisão**:
```
SE acao_sugerida == "promover":
    INV-ID = max(INV-TRAIN-XXX em INVARIANTS_TRAINING.md) + 1
    anchor = linha do schema.sql citada na candidata
    token = nome da constraint/trigger/função
```

#### 3.2.4 Criação de SPEC YAML

**Estrutura Obrigatória** (spec_version: "1.0"):
```yaml
spec_version: "1.0"
id: "INV-TRAIN-XXX"
status: "CONFIRMADA"
test_required: true

units:
  - unit_key: "main"
    class: "A"  # A/B/C1/C2/D/E1/F
    required: true
    description: "Brief description"
    anchors:
      db.table: "table_name"
      db.constraint: "ck_table_field"
      db.sqlstate: "23514"

tests:
  primary: "tests/training/invariants/test_inv_train_XXX_*.py"
  node: "TestInvTrainXXX*"
```

#### 3.2.5 Validações de Anchors (Anti-Alucinação)

| Anchor | Validação | Fonte | Erro se Falhar |
|--------|-----------|-------|----------------|
| db.table | CREATE TABLE public.{table} existe | schema.sql | ANCHOR_TABLE_NOT_FOUND |
| db.constraint | Constraint presente na tabela | schema.sql | ANCHOR_CONSTRAINT_NOT_FOUND |
| db.trigger | CREATE TRIGGER {trigger} ON {table} | schema.sql | ANCHOR_TRIGGER_NOT_FOUND |
| db.function | CREATE FUNCTION {function} | schema.sql | ANCHOR_FUNCTION_NOT_FOUND |
| api.operation_id | operationId em paths | openapi.json | ANCHOR_OPERATION_NOT_FOUND |

#### 3.2.6 Output

- SPEC block adicionado ao final de `INVARIANTS_TRAINING.md`
- Candidata movida para "Resolvidas" em `training_invariants_candidates.md`

---

### 3.3 FASE 2: Test Implementation

#### 3.3.1 Objetivo

Criar teste runtime conforme DoD-0 a DoD-9, usando helper canônico para asserts de DB.

#### 3.3.2 Nomenclatura (DoD-0)

**Arquivo**: `tests/training/invariants/test_inv_train_XXX_<slug>.py`
- XXX = ID numérico (ex: 033)
- slug = descrição curta snake_case (ex: `wellness_pre_sleep_hours`)

**Classe**: `TestInvTrainXXX<Slug>`
- XXX = ID numérico
- Slug = CamelCase (ex: `TestInvTrain033WellnessPreSleepHours`)

**Métodos**:
- `test_valid_case__*`: Testes com dados válidos
- `test_invalid_case_*__*`: Testes com violações

#### 3.3.3 Template de Teste (Classe A - DB CHECK)

```python
import pytest
from uuid import uuid4
from sqlalchemy.exc import IntegrityError
from tests._helpers.pg_error import assert_pg_constraint_violation

@pytest.mark.asyncio
async def test_inv_train_XXX_invalid_value_rejected(async_db, inv_org):
    """
    Classe: A (DB Constraint - CHECK)
    Evidência: schema.sql:LINHA (ck_table_field)

    Obrigação A:
    Analisei schema.sql. Para payload mínimo:
    1. FK obrigatória: organization_id (tabela.organization_id FK)
    2. NOT NULL: field_x (tabela.field_x NOT NULL)
    3. Enum: type (TYPE enum_name). Usarei 'valid_value'.

    Obrigação B:
    Invariante alvo: ck_table_field (CHECK)
    SQLSTATE Esperado: 23514 (check_violation)
    Constraint Name: ck_table_field
    """

    # 1. Criar payload mínimo válido (tudo certo, exceto campo alvo)
    obj = YourModel(
        id=uuid4(),
        organization_id=inv_org.id,  # FK
        field_x="value",              # NOT NULL
        type="valid_value",           # Enum
        target_field=-1,              # VIOLAÇÃO: valor inválido
    )
    async_db.add(obj)

    # 2. Execução e captura
    with pytest.raises(IntegrityError) as exc_info:
        await async_db.flush()

    # 3. Assert canônico (driver-agnostic)
    assert_pg_constraint_violation(
        exc_info,
        sqlstate="23514",
        constraint_name="ck_table_field"
    )

    # 4. Isolamento: restaurar sessão
    await async_db.rollback()
```

#### 3.3.4 Payload Mínimo (DoD-3)

**Regra**: O payload deve satisfazer TODAS as outras constraints, exceto a invariante alvo.

**Checklist**:
- [ ] FKs obrigatórias preenchidas (usar fixtures `inv_org`, `inv_team`, etc.)
- [ ] NOT NULL satisfeitos
- [ ] ENUMs com valores válidos
- [ ] DEFAULT omitidos (deixar o DB preencher)
- [ ] Apenas o campo alvo viola a constraint

**Anti-pattern**:
```python
# ❌ BAD: over-setup (preenche campos desnecessários)
obj = Model(
    id=uuid4(),
    organization_id=inv_org.id,
    field_a="value",  # Não é NOT NULL, não precisa
    field_b=123,      # Não é NOT NULL, não precisa
    target_field=-1   # Violação
)

# ✅ GOOD: payload mínimo
obj = Model(
    id=uuid4(),
    organization_id=inv_org.id,  # FK obrigatória
    target_field=-1               # Violação
)
```

#### 3.3.5 Lookup Tables (DoD-6a)

**Regra**: PROIBIDO criar novas linhas em tabelas de catálogo/seed.

**Tabelas LOOKUP** (não criar):
- `categories`
- `roles`
- `permissions`
- Qualquer tabela com seed estável (populated via migration)

**Ação Correta**:
```python
# ❌ BAD: cria nova linha em lookup table
category = Category(id=uuid4(), name="Test Category")
async_db.add(category)

# ✅ GOOD: seleciona linha existente
category = await async_db.execute(
    select(Category).order_by(Category.id).limit(1)
)
category = category.scalar_one()
```

#### 3.3.6 Output

- Arquivo de teste criado em `tests/training/invariants/`
- Teste segue naming convention (DoD-0)
- Docstring contém Obrigação A e Obrigação B
- Usa helper canônico `assert_pg_constraint_violation`

---

### 3.4 FASE 3: Gate Individual

#### 3.4.1 Objetivo

Validar invariante individual em loop até EXIT=0 (PASS).

#### 3.4.2 Comando

```powershell
.\scripts\inv.ps1 gate INV-TRAIN-XXX
```

#### 3.4.3 Fluxo Interno

```powershell
# Executa run_invariant_gate.ps1 INV-TRAIN-XXX

# Step 1: Parse SPEC
$testsPrimary = "tests/.../test_inv_train_XXX_*.py"
$testsNode = "TestInvTrainXXX*"

# Step 2: Run Verifier
python docs\scripts\verify_invariants_tests.py --level strict --inv INV-TRAIN-XXX
$verifyExit = $LASTEXITCODE

# Step 3: Run Pytest
pytest $testsPrimary::$testsNode -v --tb=short
$pytestExit = $LASTEXITCODE

# Step 4: Generate Hashes & Meta
# (canonical inputs: openapi.json, schema.sql, INVARIANTS_TRAINING.md, verify_invariants_tests.py, test_file)

# Step 5: Golden Drift Detection
# Se golden existe: comparar hashes
# Se golden não existe: EXIT=3 com golden_missing: YES
```

#### 3.4.4 Outputs Gerados

**Report Timestamped**: `docs/_generated/_reports/INV-TRAIN-XXX/YYYYMMDD_HHMMSS/`

Arquivos:
- `verify.txt`: Output completo do verifier (todas as INVs)
- `verify_inv.txt`: Violations filtradas (apenas INV-TRAIN-XXX)
- `pytest.txt`: Output completo do pytest
- `hashes.txt`: SHA256 dos canonical inputs
- `meta.txt`: Metadata (inv_id, timestamp, exit_code, primary_class, etc.)

**Exemplo de hashes.txt**:
```
# Canonical inputs (for drift detection)
openapi.json: 8f7a3bc2...
schema.sql: 1d4e9ab1...
INVARIANTS_TRAINING.md: 5c2f8e3a...
verify_invariants_tests.py: 9a1b4d7e...
test_file: 3e5f2c8a...
```

**Exemplo de meta.txt**:
```
# Gate Run Metadata
inv_id: INV-TRAIN-033
timestamp: 20260210_143022
root: C:\HB TRACK
backend: C:\HB TRACK\Hb Track - Backend
python: Python 3.11.5
test_file: C:\HB TRACK\Hb Track - Backend\tests\training\invariants\test_inv_train_033_wellness_pre_sleep_hours.py
test_node: TestInvTrain033WellnessPreSleepHours
verify_exit: 0
pytest_exit: 0
exit_code: 0
primary_class: A
golden_drift: NO
golden_missing: NO
```

#### 3.4.5 Golden Drift Detection

**Algoritmo**:
```powershell
# 1. Localizar golden baseline: _golden_{PRIMARY_CLASS}/
$goldenDir = "docs/_generated/_reports/INV-TRAIN-XXX/_golden_A"

# 2. Comparar hashes (5 canonical inputs)
SE hashes.txt != golden/hashes.txt:
    EXIT = 3 (DRIFT)
    Imprimir: tabela de divergências (File | Golden | Current)
    Imprimir: comando de promoção

SE golden não existe:
    EXIT = 3 (GOLDEN_MISSING)
    golden_missing: YES em meta.txt
    Imprimir: comando de bootstrap

SENÃO:
    EXIT = 0 (PASS)
```

**Exemplo de Output (Drift Detectado)**:
```
❌ GOLDEN DRIFT DETECTED!

Canonical inputs changed since golden baseline:
File                         Golden              Current
─────────────────────────────────────────────────────────────────
INVARIANTS_TRAINING.md       5c2f8e3a...         7d9e1b4f...
verify_invariants_tests.py   9a1b4d7e...         2f8c5a9b...

To promote this report to golden (after review):
  Remove-Item 'C:\HB TRACK\docs\_generated\_reports\INV-TRAIN-033\_golden_A' -Recurse -Force
  Copy-Item -Recurse 'C:\HB TRACK\docs\_generated\_reports\INV-TRAIN-033\20260210_143022' 'C:\HB TRACK\docs\_generated\_reports\INV-TRAIN-033\_golden_A'
```

#### 3.4.6 Exit Codes

| Exit Code | Condição | Ação |
|-----------|----------|------|
| **0** | VERIFY_EXIT=0 AND PYTEST_EXIT=0 AND NO_DRIFT | PASS (pode commit) |
| **1** | VERIFY_EXIT!=0 OR PYTEST_EXIT!=0 | FAIL (corrigir erros) |
| **3** | DRIFT OR OUTDATED OR MISSING | DRIFT (promover golden) |

#### 3.4.7 Loop de Correção

```
1. Developer roda: inv.ps1 gate INV-TRAIN-033
2. EXIT=1 (verifier falhou)
   - Ler verify_inv.txt (violations filtradas)
   - Corrigir teste conforme DoD
   - Repetir passo 1

3. EXIT=0 (PASS)
   - Se primeira execução: bootstrap golden
     Copy-Item -Recurse '<report>' '_golden_A'
   - Se re-run: golden já existe, nada a fazer

4. EXIT=3 (drift detectado)
   - Revisar mudanças canônicas (ver tabela de divergências)
   - Se drift é legítimo: promover golden (ver FASE 4)
   - Se drift é acidental: reverter mudanças canônicas
```

---

### 3.5 FASE 4: Golden Baseline Promotion

#### 3.5.1 Objetivo

Promover reports recentes para golden baselines de forma bulk e segura.

#### 3.5.2 Condições de Promoção

**Promoção Automática** (via `inv.ps1 promote`) SOMENTE SE:
- EXIT_CODE = 3 (drift detectado)
- VERIFY_EXIT = 0 (sem erros de qualidade)
- PYTEST_EXIT = 0 (testes passando)

**PROIBIDO promover SE**:
- VERIFY_EXIT != 0 (violações de DoD)
- PYTEST_EXIT != 0 (testes falhando)

#### 3.5.3 Workflow de Promoção

**Dry-Run (WhatIf)**:
```powershell
.\scripts\inv.ps1 drift
# Alias: run_invariant_gate_all.ps1 -WhatIf
```

**Output**:
```
Processing: INV-TRAIN-033
  Report:       20260210_143022
  VERIFY_EXIT:  0
  PYTEST_EXIT:  0
  EXIT_CODE:    3
  PRIMARY_CLASS: A

  Remove-Item -Path 'C:\HB TRACK\docs\_generated\_reports\INV-TRAIN-033\_golden_A' -Recurse -Force -ErrorAction SilentlyContinue
  Copy-Item -Path 'C:\HB TRACK\docs\_generated\_reports\INV-TRAIN-033\20260210_143022' -Destination 'C:\HB TRACK\docs\_generated\_reports\INV-TRAIN-033\_golden_A' -Recurse -Force

Processing: INV-TRAIN-034
  SKIP: VERIFY_EXIT != 0 (tests have errors)

...

Dry-run complete. Use -Promote to execute promotion.
```

**Promoção Real**:
```powershell
.\scripts\inv.ps1 promote
# Alias: run_invariant_gate_all.ps1 -Promote
```

**Fluxo Interno**:
```powershell
# 1. Para cada INV com EXIT_CODE=3:
#    - Validar VERIFY_EXIT=0 AND PYTEST_EXIT=0
#    - Se válido: executar comandos de promoção
#    - Incrementar $PromotionCount

# 2. Re-run gate_all (validação pós-promoção)
& run_invariant_gate_all.ps1
$FinalExitCode = $LASTEXITCODE

# 3. Validar EXIT_ALL=0
SE $FinalExitCode == 0:
    RESULT: ALL PASS (promotion successful)
SENÃO:
    RESULT: STILL HAS ISSUES (review promotion)
    EXIT $FinalExitCode
```

#### 3.5.4 Validação Pós-Promoção

**Obrigatório**: Após promoção bulk, o script DEVE:
1. Re-executar `run_invariant_gate_all.ps1` (sem -Promote)
2. Exigir EXIT_ALL=0 (todas as INVs PASS)
3. Falhar se qualquer INV ainda tiver drift

**Motivo**: Garantir que promoções foram bem-sucedidas e nenhum drift permanece.

#### 3.5.5 Output

```
========================================
FINAL RESULT
========================================
EXIT_ALL:  0
RESULT:    ALL PASS (promotion successful)
```

---

### 3.6 FASE 5: Gate All

#### 3.6.1 Objetivo

Validar TODAS as invariantes com golden baselines em um único run.

#### 3.6.2 Comando

```powershell
.\scripts\inv.ps1 all
# Alias: run_invariant_gate_all.ps1
```

#### 3.6.3 Discovery de Invariantes

**Estratégia Dual**:
1. Procurar por `_golden_*` em `docs/_generated/_reports/INV-*/`
2. Procurar por `golden_missing: YES` em reports recentes

**Algoritmo**:
```powershell
$InvariantsWithGolden = @()

Get-ChildItem -Path $ReportsDir -Directory -Filter "INV-*" | ForEach-Object {
    $InvId = $_.Name
    $InvDir = $_.FullName

    # Estratégia 1: golden existente
    $GoldenDirs = Get-ChildItem -Path $InvDir -Directory -Filter "_golden_*"

    SE $GoldenDirs.Count > 0:
        $InvariantsWithGolden += $InvId
    SENÃO:
        # Estratégia 2: golden_missing
        $LatestReport = Get-ChildItem -Path $InvDir -Directory |
            Where-Object { $_.Name -notlike "_golden_*" } |
            Sort-Object Name -Descending |
            Select-Object -First 1

        $MetaFile = Join-Path $LatestReport.FullName "meta.txt"
        SE (Get-Content $MetaFile -Raw) -match 'golden_missing:\s*YES':
            $InvariantsWithGolden += $InvId
}
```

#### 3.6.4 Execução Paralela

```powershell
$Results = @()
$AggregatedExitCode = 0

foreach ($InvId in $InvariantsWithGolden) {
    # Executar gate individual
    & run_invariant_gate.ps1 $InvId
    $ExitCode = $LASTEXITCODE

    # Determinar resultado
    $Result = switch ($ExitCode) {
        0 { "PASS" }
        3 { "DRIFT/OUTDATED" }
        default { "FAIL" }
    }

    # Armazenar
    $Results += [PSCustomObject]@{
        InvId = $InvId
        ExitCode = $ExitCode
        Result = $Result
    }

    # Atualizar exit code agregado (3 > 1 > 0)
    if ($ExitCode -eq 3) {
        $AggregatedExitCode = 3
    } elseif ($ExitCode -ne 0 -and $AggregatedExitCode -ne 3) {
        $AggregatedExitCode = 1
    }
}
```

#### 3.6.5 Output

**Summary Table**:
```
INV_ID              EXIT_CODE   RESULT
──────────────────────────────────────────────────
INV-TRAIN-001       0           PASS
INV-TRAIN-002       0           PASS
INV-TRAIN-003       3           DRIFT/OUTDATED
INV-TRAIN-004       0           PASS
...
INV-TRAIN-051       0           PASS

────────────────────────────────────────────────
Total:  36
PASS:   34
DRIFT:  2
FAIL:   0

========================================
AGGREGATED RESULT
========================================
EXIT_CODE:  3
RESULT:     DRIFT DETECTED
```

#### 3.6.6 Exit Codes Agregados

| Exit Code | Condição | Significado |
|-----------|----------|-------------|
| **0** | Todas as INVs com EXIT=0 | ALL PASS (pode commit) |
| **3** | Pelo menos 1 INV com EXIT=3 | DRIFT DETECTED (promover goldens) |
| **1** | Pelo menos 1 INV com EXIT=1 | SOME FAILURES (corrigir erros) |

**Prioridade**: 3 > 1 > 0 (drift tem prioridade sobre fail)

---

## 4. Critérios de Aceitação

### 4.1 Definition of Done por Fase

| Fase | DoD | Validação |
|------|-----|-----------|
| **FASE 0** | Artefatos gerados | schema.sql, openapi.json, alembic_state.txt existem e size > 0 |
| **FASE 1** | SPEC YAML válido | Parseable, anchors validados, test_required=true |
| **FASE 2** | Teste conforme DoD-0 a DoD-9 | verify_invariants_tests.py EXIT=0 |
| **FASE 3** | Gate individual PASS | EXIT=0 (VERIFY=0, PYTEST=0, NO_DRIFT) |
| **FASE 4** | Golden promovido | EXIT_ALL=0 após re-run gate all |
| **FASE 5** | Gate all PASS | EXIT_ALL=0 (todas as INVs PASS) |

### 4.2 Checklist de Commit (Developer)

Antes de fazer commit com mudanças em invariantes:

- [ ] Executei `inv.ps1 refresh` (artefatos canônicos atualizados)
- [ ] Executei `inv.ps1 gate <INV-ID>` para cada INV alterada (EXIT=0)
- [ ] Se houve drift (EXIT=3): revisei mudanças canônicas e promovi golden
- [ ] Executei `inv.ps1 all` (EXIT_ALL=0)
- [ ] Verifiquei que `verify_inv.txt` está vazio (sem violations)
- [ ] Verifiquei que pytest passou (todos os testes green)

### 4.3 Checklist de Commit (Agent)

Antes de declarar "DONE":

- [ ] Colar output completo de `GATE VERDICT` (report path + exit codes)
- [ ] Se promoção ocorreu: colar output de `promote` + output de `all` pós-promoção
- [ ] Confirmar EXIT_ALL=0 no output final
- [ ] PROIBIDO declarar "DONE" sem evidência de gates (violations)

---

## 5. Métricas de Sucesso

### 5.1 Cobertura de Invariantes

| Métrica | Baseline (2026-02-08) | Target (2026-03-08) | Delta |
|---------|----------------------|---------------------|-------|
| Invariantes confirmadas | 51 | 62 | +11 |
| Candidatas promovidas | 0 | 11 (de 57) | +11 |
| Golden baselines | 36 | 47 | +11 |
| % Cobertura de testes | 100% (51/51) | 100% (62/62) | - |

### 5.2 Qualidade de Gates

| Gate | Taxa de Rejeição (Baseline) | Target | Delta |
|------|----------------------------|--------|-------|
| Verifier (DoD) | 15% (violations encontradas) | 5% | -10% |
| Pytest (runtime) | 8% (testes falhando) | 3% | -5% |
| Golden drift | 20% (drift legítimo) | 15% | -5% |

### 5.3 Velocidade de Execução

| Comando | Tempo Médio | Target |
|---------|-------------|--------|
| `inv.ps1 refresh` | 15-30s | < 45s |
| `inv.ps1 gate <INV>` | 10-40s | < 60s |
| `inv.ps1 all` (36 INVs) | 6-15min | < 20min |
| `inv.ps1 promote` | 10-30s + re-run | < 60s + re-run |

### 5.4 Redução de Erros

**Target**: Reduzir em 70% os erros de rastreabilidade detectados em code review.

| Tipo de Erro | Baseline | Target | Mecanismo |
|--------------|----------|--------|-----------|
| Anchors com typos | 15% | 0% | Gate 2 (anchor validation) bloqueia |
| SQLSTATE errado | 10% | 0% | Gate 3 (SQLSTATE validation) bloqueia |
| Payload não-mínimo | 20% | 10% | Gate 3 (DoD-3) alerta |
| Testes "verdes" mas não testam constraint | 12% | 5% | Gate 4 (runtime) valida |

---

## 6. Alternativas Consideradas

### 6.1 Alternativa A: Manter Workflow Manual (5 scripts distintos)

**Prós**:
- Zero trabalho adicional
- Máxima flexibilidade para developer avançado

**Contras**:
- ❌ Curva de aprendizado alta (5 comandos + 8 docs)
- ❌ Propenso a erro humano (executar comandos fora de ordem)
- ❌ Sem validação de pré-requisitos (SSOT desatualizado)

**Decisão**: Rejeitada. Complexidade não justificada.

### 6.2 Alternativa B: Implementar apenas `inv.ps1 gate` (sem promote/all)

**Prós**:
- ✅ Simplifica workflow individual (1 comando)
- ✅ Resolve 80% dos casos de uso

**Contras**:
- ⚠️ Não resolve drift em massa (mudança de verify_invariants_tests.py)
- ⚠️ Promoção manual continua propensa a erro

**Decisão**: Considerada como **Fase 1**, mas insuficiente longo prazo.

### 6.3 Alternativa C: Pre-commit Hook Automático

**Prós**:
- ✅ Enforcement obrigatório (não pode esquecer)
- ✅ Elimina 100% dos erros de "esqueci de rodar gate"

**Contras**:
- ❌ Lento (6-15min para gate all)
- ❌ Bloqueia commit mesmo para mudanças não relacionadas a invariantes

**Decisão**: Rejeitada para pre-commit local. Mantida para CI/CD remoto.

### 6.4 Alternativa D: GitHub Actions Workflow (CI/CD)

**Prós**:
- ✅ Execução remota (não bloqueia developer)
- ✅ Paralelização de gates (run em parallel em matriz)
- ✅ Auditoria automática (logs permanentes)

**Contras**:
- ⚠️ Feedback loop mais lento (2-5min vs. 10-40s local)
- ⚠️ Requer setup de DB de teste no CI

**Decisão**: APROVADA como complemento (local-first + CI/CD).

---

## 7. Plano de Implementação

### 7.1 Fase 1: Wrapper Unificado (✅ DONE)

**Entregáveis**:
1. ✅ `inv.ps1` (wrapper master)
   - Comandos: gate, all, drift, promote, refresh
   - Exit code semântico (0, 1, 3)
   - Esforço: 2h

2. ✅ `run_invariant_gate.ps1` (gate individual)
   - Parse SPEC, verifier, pytest, golden drift
   - Esforço: 4h

3. ✅ `run_invariant_gate_all.ps1` (gate bulk + promote)
   - Discovery, aggregated exit, promotion bulk
   - Esforço: 4h

**Output**: Developer pode executar workflow completo via `inv.ps1`.

### 7.2 Fase 2: Helper Canônico (✅ DONE)

**Entregáveis**:
1. ✅ `tests/_helpers/pg_error.py`
   - assert_pg_constraint_violation (driver-agnostic)
   - Esforço: 2h

2. ✅ Migração de 4 testes existentes
   - test_inv_train_001, 032, 043, 044
   - Esforço: 1h

**Output**: Testes usam helper canônico, não acessam `orig.diag` diretamente.

### 7.3 Fase 3: Documentação Canônica (✅ DONE)

**Entregáveis**:
1. ✅ INVARIANTS_AGENT_PROTOCOL.md
   - Regras de loop obrigatório, golden promotion, evidência
   - Esforço: 3h

2. ✅ INVARIANTS_AGENT_GUARDRAILS.md
   - SSOT, comandos canônicos, exit codes, anti-patterns
   - Esforço: 2h

3. ✅ INV_TASK_TEMPLATE.md
   - Template para instalação de nova invariante
   - Esforço: 2h

**Output**: Agents e developers têm guia canônico para workflow.

### 7.4 Fase 4: Backlog Processing (🔄 IN PROGRESS)

**Entregáveis**:
1. 🔄 Promover 11 candidatas prioritárias (NEEDS_REVIEW → DONE)
   - INV-TRAIN-047 a INV-TRAIN-051 (5 já criadas)
   - 6 candidatas restantes (alta prioridade)
   - Esforço: 2h por invariante = 12h total

2. [ ] Atualizar INVARIANTS_TRAINING.md com anchors validados
   - Esforço: 1h

3. [ ] Executar `inv.ps1 all` final (EXIT_ALL=0)
   - Esforço: 15min

**Output**: 62 invariantes confirmadas com 100% cobertura de testes.

### 7.5 Fase 5: CI/CD Integration (⏳ PLANNED)

**Entregáveis**:
1. [ ] GitHub Actions workflow para PR checks
   - Rodar `inv.ps1 all` em PRs que tocam `tests/invariants/` ou `docs/INVARIANTS_TRAINING.md`
   - Esforço: 3h

2. [ ] Setup de DB de teste no CI
   - Usar PostgreSQL container (GitHub Actions service)
   - Esforço: 2h

3. [ ] Badge de status no README
   - "Invariants: 62/62 PASS"
   - Esforço: 30min

**Output**: Validação automática em PRs + auditoria permanente.

---

## 8. Riscos e Mitigações

| Risco | Probabilidade | Impacto | Mitigação |
|-------|---------------|---------|-----------|
| **R1**: Gates lentos (> 20min) bloqueiam workflow | Média | Alto | Paralelização futura, cache de SSOT, skip gates opcionais |
| **R2**: Developer não entende exit codes semânticos | Média | Médio | Documentar EXIT_CODES.md, adicionar hints em output colorido |
| **R3**: Golden drift falso-positivo (SSOT desatualizado) | Alta | Crítico | Adicionar validação pré-gate: `inv.ps1 refresh` obrigatório antes de `gate` |
| **R4**: Promoção bulk acidental (promove goldens inválidos) | Baixa | Alto | `-WhatIf` obrigatório antes de `-Promote`, validação pós-promoção (EXIT_ALL=0) |
| **R5**: Developer bypassa gates (commit sem validação) | Média | Alto | Pre-commit hook local (opt-in), CI/CD obrigatório (enforce remoto) |
| **R6**: Fragmentação de comandos (inv.ps1 vs. scripts diretos) | Baixa | Médio | Deprecar uso direto de scripts, centralizar em `inv.ps1`, documentar migration |

---

## 9. Referências

### 9.1 Documentos Canônicos

- `INVARIANTS_TESTING_CANON.md`: Protocolo de testes (DoD-0 a DoD-9)
- `INVARIANTS_TRAINING.md`: Catálogo de 51 invariantes
- `INVARIANTS_AGENT_PROTOCOL.md`: Workflow local-first
- `INVARIANTS_AGENT_GUARDRAILS.md`: SSOT, exit codes, anti-patterns
- `INV_TASK_TEMPLATE.md`: Template de instalação
- `training_invariants_candidates.md`: Backlog de 57 candidatas
- `VALIDAR_INVARIANTS_TESTS.md`: Documentação do validador

### 9.2 Scripts do Workflow

- `inv.ps1`: Wrapper master (gate, all, drift, promote, refresh)
- `run_invariant_gate.ps1`: Gate individual
- `run_invariant_gate_all.ps1`: Gate bulk + promotion
- `verify_invariants_tests.py`: Validador de qualidade (DoD)
- `tests/_helpers/pg_error.py`: Helper canônico para asserts DB

### 9.3 ADRs Relacionados

- ADR-012-ADR-INV-TRAIN: Sistema de Gates para Validação (4 gates)
- ADR-004-ADR-TRAIN-invariantes-como-contrato: Invariantes como contrato
- ADR-001-ADR-TRAIN-ssot-precedencia: Precedência de SSOT

### 9.4 Padrões Externos

- PostgreSQL SQLSTATE codes: https://www.postgresql.org/docs/current/errcodes-appendix.html
- pytest best practices: https://docs.pytest.org/en/stable/goodpractices.html
- PowerShell exit codes: https://docs.microsoft.com/en-us/powershell/scripting/learn/deep-dives/everything-about-exceptions

---

## 10. Aprovação

**Decisão**: APPROVED
**Data de Aprovação**: 2026-02-10
**Aprovadores**:
- [x] Davi (Product Owner & Tech Lead)
- [x] Claude Sonnet 4.5 (Technical Advisor)

**Próximos Passos**:
1. Completar Fase 4 (promover 6 candidatas restantes)
2. Executar `inv.ps1 all` final (validar 62 invariantes)
3. Planejar Fase 5 (CI/CD integration)
4. Criar documentação de troubleshooting (erros comuns + soluções)

---

**Assinaturas**:

```
__________________________    __________________________
Davi                          Claude Sonnet 4.5
Product Owner                 Technical Advisor
HB Track Project              Anthropic

Data: 2026-02-10              Data: 2026-02-10
```

---

## Anexo A: Exemplo de Workflow Completo

### Cenário: Developer Cria Nova Invariante (INV-TRAIN-052)

```powershell
# FASE 0: SSOT Refresh
PS> .\scripts\inv.ps1 refresh

========================================
INV WRAPPER
========================================
COMMAND:  refresh
ROOT:     C:\HB TRACK

MODE:     REFRESH CANONICAL ARTIFACTS (SSOT)
========================================

Executing: python scripts\generate_docs.py

[OK] schema.sql (456789 bytes)
[OK] openapi.json (123456 bytes)
[OK] alembic_state.txt (234 bytes)

========================================
WRAPPER EXIT CODE: 0
========================================

# FASE 1: Worklist & SPEC Creation (Manual)
# Developer seleciona candidata:
#   ck_training_sessions_intensity (CHECK) | schema.sql:2643 | NEEDS_REVIEW

# Cria SPEC YAML em INVARIANTS_TRAINING.md:
spec_version: "1.0"
id: "INV-TRAIN-052"
status: "CONFIRMADA"
test_required: true

units:
  - unit_key: "main"
    class: "A"
    required: true
    description: "CHECK constraint garante intensity_target entre 1 e 5"
    anchors:
      db.table: "training_sessions"
      db.constraint: "ck_training_sessions_intensity"
      db.sqlstate: "23514"

tests:
  primary: "tests/training/invariants/test_inv_train_052_intensity_range.py"
  node: "TestInvTrain052IntensityRange"

# FASE 2: Test Implementation (Manual)
# Developer cria test_inv_train_052_intensity_range.py (seguindo template)

# FASE 3: Gate Individual (Loop até EXIT=0)
PS> .\scripts\inv.ps1 gate INV-TRAIN-052

========================================
Gate Runner: INV-TRAIN-052
========================================

Step 1: Parsing SPEC...
  tests.primary: tests/training/invariants/test_inv_train_052_intensity_range.py
  tests.node:    TestInvTrain052IntensityRange

Step 2: Running verifier (strict)...
  Verifier exit: 0
  Filtered violations: 0 lines
  VERIFY STATUS: PASS

Step 3: Running pytest...
  Target: C:\HB TRACK\Hb Track - Backend\tests\training\invariants\test_inv_train_052_intensity_range.py::TestInvTrain052IntensityRange
  Pytest exit: 0
  PYTEST STATUS: PASS

Step 4: Generating artifacts...
  Artifacts saved:
    - verify.txt (12345 bytes)
    - verify_inv.txt (0 lines)
    - pytest.txt (2345 bytes)
    - hashes.txt
    - meta.txt

[5.5] Checking Golden Drift...
  Unit class: A
  Golden dir: C:\HB TRACK\docs\_generated\_reports\INV-TRAIN-052\_golden_A
  Golden not found: promote this report to create baseline
    Copy-Item -Recurse 'C:\HB TRACK\docs\_generated\_reports\INV-TRAIN-052\20260210_143022' 'C:\HB TRACK\docs\_generated\_reports\INV-TRAIN-052\_golden_A'

========================================
GATE VERDICT
========================================
Report:           C:\HB TRACK\docs\_generated\_reports\INV-TRAIN-052\20260210_143022
VERIFY_EXIT:      0
PYTEST_EXIT:      0
GOLDEN_DRIFT:     YES
EXIT_CODE:        3

RESULT: FAIL (GOLDEN_MISSING)

# Developer promove golden (bootstrap):
PS> Copy-Item -Recurse 'C:\HB TRACK\docs\_generated\_reports\INV-TRAIN-052\20260210_143022' 'C:\HB TRACK\docs\_generated\_reports\INV-TRAIN-052\_golden_A'

# Re-run gate para confirmar EXIT=0:
PS> .\scripts\inv.ps1 gate INV-TRAIN-052

========================================
GATE VERDICT
========================================
Report:           C:\HB TRACK\docs\_generated\_reports\INV-TRAIN-052\20260210_144530
VERIFY_EXIT:      0
PYTEST_EXIT:      0
GOLDEN_DRIFT:     NO
EXIT_CODE:        0

RESULT: PASS

# FASE 5: Gate All (Validação Final)
PS> .\scripts\inv.ps1 all

========================================
Gate Runner: ALL INVARIANTS
========================================

[1] Discovering invariants with golden baselines...
  Found 37 invariants with golden baselines

[2] Running gate for each invariant...
----------------------------------------
Running gate: INV-TRAIN-001
... (output omitido)
----------------------------------------
Running gate: INV-TRAIN-052
... (output omitido)

========================================
GATE ALL SUMMARY
========================================

INV_ID              EXIT_CODE   RESULT
──────────────────────────────────────────────────
INV-TRAIN-001       0           PASS
INV-TRAIN-002       0           PASS
...
INV-TRAIN-052       0           PASS

────────────────────────────────────────────────
Total:  37
PASS:   37
DRIFT:  0
FAIL:   0

========================================
AGGREGATED RESULT
========================================
EXIT_CODE:  0
RESULT:     ALL PASS

EXIT_ALL=0

# ✅ DONE: Developer pode commit com confiança
```

---

**Fim do Documento**
