# EXEC_TASK: Implementação do Gate de Validação Estrutural Model↔DB

**Derivado de:** ADR-MODELS-001  
**Status:** ✅ COMPLETED  
**Prioridade:** P0 (CRÍTICO)  
**Estimativa:** 3.5 dias  
**Assignee:** Davi + Claude (AI Assistant)
**Data de Conclusão:** 2026-02-11

---

## 🎯 OBJETIVO EXECUTÁVEL

Implementar o sistema de validação em 3 camadas (guardrails → parity → requirements) com gate binário (PASS/FAIL) e SSOT canônico em `docs/_generated/schema.sql`, garantindo 100% de conformidade estrutural entre SQLAlchemy models e PostgreSQL.

---

## 📋 PRÉ-REQUISITOS

### Verificações Obrigatórias (ANTES DE INICIAR)

```powershell
# ✅ CHECK 1: Baseline existente
Test-Path ".hb_guard/baseline.json"
# Esperado: True

# ✅ CHECK 2: Parity gate funcional
.\scripts\parity_gate.ps1 -Table "attendance"
# Esperado: exit=0 ou exit=2 (não 3)

# ✅ CHECK 3: Schema.sql atualizado
Get-Content "docs\_generated\schema.sql" | Select-String "CREATE TABLE attendance"
# Esperado: encontrar definição completa

# ✅ CHECK 4: Ambiente Python
python --version
# Esperado: Python 3.11+

# ✅ CHECK 5: Dependências instaladas
pip list | Select-String "sqlalchemy|alembic"
# Esperado: SQLAlchemy 2.x, Alembic 1.x
```

**ABORTAR SE:** qualquer check falhar. Resolver dependências antes de prosseguir.

---

## 🔄 FASES DE EXECUÇÃO

### FASE 1: Implementar model_requirements.py (1.5 dias)

#### Entregável 1.1: Parser DDL (schema.sql → expectativas)

**Arquivo:** `Hb Track - Backend/scripts/model_requirements.py`

**Funcionalidade:**
```python
def parse_ddl(table_name: str, schema_sql_path: str) -> TableExpectation:
    """
    Extrai expectativas estruturais de schema.sql.
    
    Returns:
        TableExpectation(
            columns=[
                ColumnExpectation(name="id", pg_type="integer", nullable=False, default="..."),
                ColumnExpectation(name="name", pg_type="character varying(200)", nullable=False),
                ...
            ],
            foreign_keys=[
                FKExpectation(name="fk_attendance_team", local_cols=["team_id"], 
                             ref_table="teams", ref_cols=["id"], ondelete="CASCADE"),
                ...
            ],
            check_constraints=["ck_attendance_status_valid"],
            unique_constraints=[("season_id", "team_id", "athlete_id", "date")],
            indexes=[
                IndexExpectation(name="idx_attendance_team_date", columns=["team_id", "date"], unique=False),
                ...
            ]
        )
    """
    # Implementação:
    # 1. Ler schema.sql
    # 2. Encontrar CREATE TABLE {table_name} block
    # 3. Parsear colunas (regex: nome tipo nullable default)
    # 4. Parsear FKs (CONSTRAINT ... FOREIGN KEY)
    # 5. Parsear CHECKs (CONSTRAINT ... CHECK)
    # 6. Parsear UNIQUE (CONSTRAINT ... UNIQUE)
    # 7. Parsear INDEXes (CREATE INDEX ... ON {table_name})
    # 8. Retornar estrutura tipada
```

**Testes de aceitação:**
```python
# TEST 1.1.1: Extração de colunas
expectation = parse_ddl("attendance", "docs/_generated/schema.sql")
assert len(expectation.columns) == 10  # Número esperado de colunas
assert expectation.columns[0].name == "id"
assert expectation.columns[0].pg_type == "integer"
assert expectation.columns[0].nullable == False

# TEST 1.1.2: Extração de FKs
fk_names = [fk.name for fk in expectation.foreign_keys]
assert "fk_attendance_team" in fk_names
assert "fk_attendance_athlete" in fk_names

# TEST 1.1.3: Extração de CHECKs
assert "ck_attendance_status_valid" in expectation.check_constraints

# TEST 1.1.4: Extração de UNIQUE
assert ("season_id", "team_id", "athlete_id", "date") in expectation.unique_constraints
```

**Critério de DONE:**
- ✅ Parser extrai 100% das estruturas de `attendance` (validado manualmente)
- ✅ Testes passam com `pytest tests/test_model_requirements.py::test_parse_ddl`
- ✅ Suporta edge cases: tipos compostos (`character varying(200)`), defaults literais

---

#### Entregável 1.2: Parser AST (model.py → declarações)

**Funcionalidade:**
```python
def parse_model_ast(model_path: str) -> ModelDeclaration:
    """
    Extrai declarações estruturais de um model Python via AST.
    
    Suporta padrões:
    - Mapped[T] + mapped_column(...)
    - Column(...) direto
    - sa.Column(...) aliased
    
    Returns:
        ModelDeclaration(
            columns=[
                ColumnDeclaration(name="id", sa_type="Integer", nullable=False, line=25),
                ColumnDeclaration(name="name", sa_type="String(200)", nullable=False, line=27),
                ...
            ],
            table_args={
                "foreign_keys": [...],
                "check_constraints": [...],
                "unique_constraints": [...],
                "indexes": [...]
            }
        )
    """
    # Implementação:
    # 1. Parsear arquivo Python com ast.parse()
    # 2. Visitar ast.ClassDef da classe do model
    # 3. Extrair colunas de:
    #    - ast.AnnAssign (Mapped[...] = mapped_column(...))
    #    - ast.Assign (Column(...))
    # 4. Extrair __table_args__ (ast.Assign → tuple/dict)
    # 5. Mapear tipos SA → string normalizada
    # 6. Retornar estrutura tipada com line numbers
```

**Testes de aceitação:**
```python
# TEST 1.2.1: Detecção de Mapped + mapped_column
declaration = parse_model_ast("app/models/attendance.py")
col = next(c for c in declaration.columns if c.name == "date")
assert col.sa_type == "Date"
assert col.nullable == False
assert col.line > 0  # Line number extraído

# TEST 1.2.2: Detecção de Column direto
col = next(c for c in declaration.columns if c.name == "created_at")
assert col.sa_type == "DateTime"
assert col.nullable == False

# TEST 1.2.3: Extração de __table_args__
fks = declaration.table_args["foreign_keys"]
assert len(fks) >= 4  # FK para team, athlete, season, training_session
```

**Critério de DONE:**
- ✅ Parser detecta 100% das colunas de `app/models/attendance.py`
- ✅ Suporta 3 padrões de declaração (Mapped, Column, sa.Column)
- ✅ Extrai line numbers para relatórios
- ✅ Testes passam com `pytest tests/test_model_requirements.py::test_parse_ast`

---

#### Entregável 1.3: Validador (comparação + relatório)

**Funcionalidade:**
```python
def validate_model(table_name: str, profile: str = "strict") -> ValidationReport:
    """
    Compara expectativa (DDL) vs declaração (AST) e retorna violations.
    
    Perfis:
    - "strict": todas as validações A-H (padrão)
    - "fk": apenas validações A-D (para ciclos FK documentados)
    - "lenient": apenas A-C (metaprogramming permitido)
    
    Returns:
        ValidationReport(
            violations=[
                Violation(
                    rule="A1_EXTRA_COLUMN",
                    severity="ERROR",
                    location="app/models/attendance.py:42",
                    message="Column 'extra_field' exists in model but not in schema.sql",
                    fix_suggestion="Remove column or run migration"
                ),
                ...
            ],
            summary={
                "total_violations": 3,
                "errors": 2,
                "warnings": 1,
                "conformity": "FAIL"
            }
        )
    """
    # Implementação:
    # 1. Chamar parse_ddl() e parse_model_ast()
    # 2. Aplicar validações por perfil:
    #    - A: Colunas exatas (extras, faltantes)
    #    - B: Tipos corretos (mapeamento PG→SA)
    #    - C: Nullable correto (NOT NULL ↔ nullable=False)
    #    - D: FKs corretas (nome, ref, ondelete, use_alter)
    #    - E: CHECKs (nomes exatos)
    #    - F: Indexes explícitos (prefixos idx_, ix_)
    #    - G: UNIQUE constraints (não duplicar com Index)
    #    - H: Server defaults (literais, não funções)
    # 3. Acumular violations com line numbers
    # 4. Gerar relatório JSON + summary
```

**Mapeamento PG→SA (Critério B):**
```python
PG_TO_SA_TYPES = {
    "integer": ["Integer"],
    "bigint": ["BigInteger"],
    "character varying": ["String"],  # Aceita com/sem length
    "character varying(N)": ["String(N)", "String"],  # Length é opcional no SA
    "text": ["Text", "String"],  # Text pode ser String sem length
    "boolean": ["Boolean"],
    "date": ["Date"],
    "timestamp without time zone": ["DateTime"],
    "timestamp with time zone": ["DateTime"],  # Timezone ignorada no SA
    "numeric": ["Numeric"],
    "numeric(P,S)": ["Numeric(P,S)", "Numeric"],
    "uuid": ["Uuid"],
    # ... (adicionar conforme necessário)
}
```

**Testes de aceitação:**
```python
# TEST 1.3.1: Detecção de coluna extra
# Modificar app/models/attendance.py para adicionar coluna fictícia
report = validate_model("attendance", profile="strict")
assert any(v.rule == "A1_EXTRA_COLUMN" for v in report.violations)

# TEST 1.3.2: Tipo incorreto
# Modificar 'date' para String no model
report = validate_model("attendance", profile="strict")
assert any(v.rule == "B1_TYPE_MISMATCH" for v in report.violations)

# TEST 1.3.3: Nullable incorreto
# Remover nullable=False de coluna NOT NULL
report = validate_model("attendance", profile="strict")
assert any(v.rule == "C1_NULLABLE_MISMATCH" for v in report.violations)

# TEST 1.3.4: FK faltando use_alter
# Remover use_alter=True de FK de ciclo
report = validate_model("teams", profile="strict")
assert any(v.rule == "D4_MISSING_USE_ALTER" for v in report.violations)

# TEST 1.3.5: Conformidade total
# Model correto (attendance após autogen)
report = validate_model("attendance", profile="strict")
assert report.summary["conformity"] == "PASS"
assert report.summary["total_violations"] == 0
```

**Critério de DONE:**
- ✅ Todas as validações A-H implementadas
- ✅ Mapeamento PG→SA cobre 95%+ dos tipos do projeto
- ✅ Relatório JSON com line numbers e fix suggestions
- ✅ Testes passam com `pytest tests/test_model_requirements.py::test_validate`
- ✅ Exit code 0 (PASS) vs 4 (FAIL) correto

---

#### Entregável 1.4: CLI wrapper

**Funcionalidade:**
```python
# Hb Track - Backend/scripts/model_requirements.py (executável)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate SQLAlchemy model against schema.sql")
    parser.add_argument("--table", required=True, help="Table name (e.g., attendance)")
    parser.add_argument("--profile", default="strict", choices=["strict", "fk", "lenient"],
                        help="Validation profile")
    parser.add_argument("--report", default="docs/_generated/requirements_report.json",
                        help="Output JSON report path")
    
    args = parser.parse_args()
    
    try:
        report = validate_model(args.table, profile=args.profile)
        
        # Salvar relatório
        with open(args.report, "w") as f:
            json.dump(report, f, indent=2)
        
        # Output console
        if report.summary["conformity"] == "PASS":
            print(f"✅ [{args.table}] PASS — {report.summary['total_violations']} violations")
            sys.exit(0)
        else:
            print(f"❌ [{args.table}] FAIL — {report.summary['total_violations']} violations")
            for v in report.violations:
                print(f"  {v.severity} {v.rule} @ {v.location}")
                print(f"    {v.message}")
                print(f"    Fix: {v.fix_suggestion}")
            sys.exit(4)
    
    except Exception as e:
        print(f"❌ INTERNAL ERROR: {e}")
        sys.exit(1)
```

**Testes de aceitação:**
```powershell
# TEST 1.4.1: Exit code 0 (PASS)
python "Hb Track - Backend/scripts/model_requirements.py" --table attendance --profile strict
$LASTEXITCODE -eq 0  # True

# TEST 1.4.2: Exit code 4 (FAIL)
# Modificar model para introduzir erro
python "Hb Track - Backend/scripts/model_requirements.py" --table attendance --profile strict
$LASTEXITCODE -eq 4  # True

# TEST 1.4.3: Relatório JSON gerado
Test-Path "docs\_generated\requirements_report.json"  # True
Get-Content "docs\_generated\requirements_report.json" | ConvertFrom-Json | Select-Object -ExpandProperty summary
# Esperado: { total_violations, errors, warnings, conformity }
```

**Critério de DONE:**
- ✅ CLI aceita `--table`, `--profile`, `--report`
- ✅ Exit codes corretos (0/4/1)
- ✅ Output console legível (violations com line numbers)
- ✅ Relatório JSON salvo em `docs/_generated/requirements_report.json`

---

### FASE 2: Integrar STEP 4 ao models_autogen_gate.ps1 (0.5 dias)

#### Entregável 2.1: Modificação do orquestrador

**Arquivo:** `scripts/models_autogen_gate.ps1`

**Modificação (inserir após STEP 3):**
```powershell
# ==================== STEP 4: Requirements Validation ====================
Write-Host "`n[STEP 4] Running requirements validation..." -ForegroundColor Cyan

# Determinar perfil baseado em flags e tabela
$profile = if ($Profile) { $Profile } else { "strict" }

# Executar model_requirements.py (usar call operator, NÃO Invoke-Expression)
$requirementsArgs = @(
    "scripts\model_requirements.py",
    "--table", $Table,
    "--profile", $profile
)
Write-Host "  CMD: python $($requirementsArgs -join ' ')" -ForegroundColor Gray

$requirementsOutput = & $venvPy $requirementsArgs 2>&1
$requirementsExit = $LASTEXITCODE

Write-Host $requirementsOutput

if ($requirementsExit -eq 4) {
    Write-Host "[FAIL] Requirements validation failed (exit=4)" -ForegroundColor Red
    Write-Host "  Review violations in docs\_generated\requirements_report.json" -ForegroundColor Yellow
    exit 4
}
elseif ($requirementsExit -ne 0) {
    Write-Host "[ERROR] Requirements validator crashed (exit=$requirementsExit)" -ForegroundColor Red
    exit 1
}

Write-Host "[PASS] Requirements validation succeeded" -ForegroundColor Green
```

**Modificação (adicionar parâmetro):**
```powershell
param(
    [Parameter(Mandatory=$true)]
    [string]$Table,
    
    [switch]$Create,
    
    [string[]]$Allow,
    
    [ValidateSet("fk", "strict", "lenient")]
    [string]$Profile = "strict",  # <--- NOVO
    
    [switch]$AllowCycleWarning
)
```

**Testes de aceitação:**
```powershell
# TEST 2.1.1: STEP 4 executado
.\scripts\models_autogen_gate.ps1 -Table "attendance" -Profile "strict"
# Esperado: ver output "[STEP 4] Running requirements validation..."

# TEST 2.1.2: Exit code 4 propagado
# Modificar model para introduzir erro
.\scripts\models_autogen_gate.ps1 -Table "attendance"
$LASTEXITCODE -eq 4  # True (não 1)

# TEST 2.1.3: Perfil "fk" aplicado
.\scripts\models_autogen_gate.ps1 -Table "teams" -Profile "fk" -AllowCycleWarning
# Esperado: validações A-D apenas, sem E-H
```

**Critério de DONE:**
- ✅ STEP 4 inserido entre STEP 3 e STEP 5
- ✅ Flag `-Profile` funcional (`strict`, `fk`, `lenient`)
- ✅ Exit code 4 propagado corretamente
- ✅ Compatibilidade retroativa mantida (flags anteriores funcionam)

---

### FASE 3: Corrigir propagação de exit codes (0.5 dias)

#### Entregável 3.1: Validação de exit codes específicos

**Problema atual:**
```powershell
# BUG: gate achata todos os erros para exit=1
if ($parityExit -ne 0) {
    exit 1  # ❌ Perde informação de exit=2 vs exit=3
}
```

**Correção:**
```powershell
# ==================== STEP 6: Exit Code Propagation ====================
# Mantém exit codes específicos (0/2/3/4) para debugging

if ($guardExit -ne 0) {
    exit $guardExit  # Propaga 3 (guard violation)
}

if ($parityExit -ne 0) {
    exit $parityExit  # Propaga 2 (structural diffs)
}

if ($requirementsExit -ne 0) {
    exit $requirementsExit  # Propaga 4 (requirements violation)
}

# Se chegou aqui, sucesso total
Write-Host "`n✅ ALL GATES PASSED — Model is 100% conformant" -ForegroundColor Green
exit 0
```

**Testes de aceitação:**
```powershell
# TEST 3.1.1: Exit 3 (guard)
# Modificar baseline.json manualmente
.\scripts\models_autogen_gate.ps1 -Table "attendance"
$LASTEXITCODE -eq 3  # True (não 1)

# TEST 3.1.2: Exit 2 (parity)
# Modificar model sem aplicar migration
.\scripts\models_autogen_gate.ps1 -Table "attendance"
$LASTEXITCODE -eq 2  # True (não 1)

# TEST 3.1.3: Exit 4 (requirements)
# Modificar model para violar requirements
.\scripts\models_autogen_gate.ps1 -Table "attendance"
$LASTEXITCODE -eq 4  # True (não 1)

# TEST 3.1.4: Exit 0 (success)
# Model totalmente correto
.\scripts\models_autogen_gate.ps1 -Table "attendance"
$LASTEXITCODE -eq 0  # True
```

**Critério de DONE:**
- ✅ Exit codes específicos propagados (0/2/3/4)
- ✅ Nenhum exit=1 genérico (exceto crashes)
- ✅ Testes passam com todos os exit codes

---

### FASE 4: Smoke test completo em attendance (1 dia)

#### Entregável 4.1: Validação de ciclo completo

**Cenário 1: Model correto (baseline)**
```powershell
# SETUP: Model attendance já existe e está conforme
.\scripts\models_autogen_gate.ps1 -Table "attendance" -Profile "strict"

# Esperado:
# - STEP 1: PASS (parity pré-check)
# - STEP 2: SKIP (model já existe)
# - STEP 3: PASS (parity pós-check)
# - STEP 4: PASS (requirements)
# - STEP 5: SKIP (baseline já existe)
# - EXIT: 0
```

**Cenário 2: Coluna extra (alucinação)**
```powershell
# SETUP: Adicionar coluna fictícia ao model
# app/models/attendance.py:
#   extra_field: Mapped[str] = mapped_column(String(100))

.\scripts\models_autogen_gate.ps1 -Table "attendance" -Profile "strict"

# Esperado:
# - STEP 1: PASS (DB não tem extra_field, mas parity não detecta)
# - STEP 3: PASS (parity não detecta extras)
# - STEP 4: FAIL (requirements detecta A1_EXTRA_COLUMN)
# - EXIT: 4
# - Relatório: docs/_generated/requirements_report.json
```

**Cenário 3: Tipo incorreto**
```powershell
# SETUP: Mudar tipo de 'date' para String
# app/models/attendance.py:
#   date: Mapped[str] = mapped_column(String(20))

.\scripts\models_autogen_gate.ps1 -Table "attendance" -Profile "strict"

# Esperado:
# - STEP 3: FAIL (parity detecta type_changed)
# - EXIT: 2
# - Relatório: docs/_generated/parity_report.json
```

**Cenário 4: Nullable incorreto**
```powershell
# SETUP: Remover nullable=False de coluna NOT NULL
# app/models/attendance.py:
#   athlete_id: Mapped[int] = mapped_column(Integer, ForeignKey(...))  # ❌ sem nullable

.\scripts\models_autogen_gate.ps1 -Table "attendance" -Profile "strict"

# Esperado:
# - STEP 3: FAIL (parity detecta modify_nullable)
# - EXIT: 2
```

**Cenário 5: FK sem use_alter (ciclo)**
```powershell
# SETUP: Remover use_alter=True de FK de teams
# app/models/teams.py:
#   season_id: Mapped[int] = mapped_column(Integer, ForeignKey("seasons.id"))  # ❌ sem use_alter

.\scripts\models_autogen_gate.ps1 -Table "teams" -Profile "strict"

# Esperado:
# - STEP 4: FAIL (requirements detecta D4_MISSING_USE_ALTER)
# - EXIT: 4
```

**Critério de DONE:**
- ✅ 5 cenários executados com sucesso
- ✅ Exit codes corretos para cada caso (0/2/4)
- ✅ Relatórios JSON gerados corretamente
- ✅ Mensagens de erro legíveis e acionáveis

---

### FASE 5: Documentação executável (0.5 dias)

#### Entregável 5.1: Atualizar docs/references/exit_codes.md

**Adicionar seção:**
```markdown
### Exit Code 4: Requirements Violation

**Origem:** `Hb Track - Backend/scripts/model_requirements.py`

**Significado:** O model SQLAlchemy viola expectativas estruturais de `schema.sql`.

**Causas comuns:**
- Coluna extra/faltante no model
- Tipo PG↔SA incompatível
- Nullable incorreto (NOT NULL vs nullable=True)
- FK sem use_alter em ciclos
- CHECK/UNIQUE/INDEX faltando

**Resolução:**
1. Revisar `docs/_generated/requirements_report.json`
2. Corrigir violations listadas (com line numbers)
3. Reexecutar gate: `.\scripts\models_autogen_gate.ps1 -Table <nome>`

**Exemplo:**
```powershell
❌ [attendance] FAIL — 2 violations
  ERROR A1_EXTRA_COLUMN @ app/models/attendance.py:42
    Column 'extra_field' exists in model but not in schema.sql
    Fix: Remove column or run migration
  ERROR B1_TYPE_MISMATCH @ app/models/attendance.py:35
    Column 'date' has type 'String' but schema.sql expects 'Date'
    Fix: Change to Date type
```
```

#### Entregável 5.2: Atualizar docs/architecture/CHECKLIST-CANONICA-MODELS.md

**Adicionar item:**
```markdown
### ✅ STEP 4: Validação de Requirements

**Objetivo:** Garantir conformidade estrutural independente de Alembic.

**Comando:**
```powershell
python "Hb Track - Backend/scripts/model_requirements.py" --table <nome> --profile strict
```

**Critério de sucesso:**
- ✅ Exit code = 0
- ✅ Relatório JSON: `conformity = "PASS"`
- ✅ Total de violations = 0

**Se falhar:**
1. Revisar `docs/_generated/requirements_report.json`
2. Corrigir violations (usar line numbers)
3. Revalidar

**Perfis disponíveis:**
- `strict`: Todas as validações A-H (padrão)
- `fk`: Apenas A-D (ciclos FK documentados)
- `lenient`: Apenas A-C (metaprogramming permitido)
```

#### Entregável 5.3: Criar docs/workflows/model_requirements_guide.md

**Conteúdo:**
```markdown
# Guia de Uso: Model Requirements Validator

## Visão Geral

O `model_requirements.py` valida conformidade estrutural entre SQLAlchemy models e `schema.sql`, complementando o Alembic compare.

## Quando usar

- ✅ Após gerar/modificar models
- ✅ Antes de commit (via pre-commit hook)
- ✅ Em CI/CD (automático em PRs)
- ✅ Para detectar alucinações de IA

## Uso básico

```powershell
# Validação padrão (strict)
python "Hb Track - Backend/scripts/model_requirements.py" --table attendance

# Validação com perfil específico
python "Hb Track - Backend/scripts/model_requirements.py" --table teams --profile fk

# Salvar relatório customizado
python "Hb Track - Backend/scripts/model_requirements.py" --table seasons --report custom_report.json
```

## Perfis de validação

### strict (padrão)
Todas as validações A-H. Use para models novos/estáveis.

### fk
Apenas A-D (sem CHECKs/Indexes/UNIQUE). Use para ciclos FK documentados.

### lenient
Apenas A-C (sem constraints). Use para models com metaprogramming.

## Interpretando violations

### A1_EXTRA_COLUMN
**Causa:** Coluna no model que não existe em schema.sql.
**Fix:** Remover coluna OU criar migration.

### B1_TYPE_MISMATCH
**Causa:** Tipo PG vs SA incompatível.
**Fix:** Corrigir tipo no model (ver mapeamento PG→SA).

### C1_NULLABLE_MISMATCH
**Causa:** NOT NULL no DB mas nullable=True no model.
**Fix:** Adicionar `nullable=False` no model.

### D4_MISSING_USE_ALTER
**Causa:** FK de ciclo sem `use_alter=True`.
**Fix:** Adicionar `use_alter=True` na ForeignKey.

## Exit codes

- `0`: PASS (conformidade total)
- `4`: FAIL (violations detectadas)
- `1`: ERROR (crash interno)

## Troubleshooting

**Q: Validator reporta false positive?**
A: Verificar mapeamento PG→SA em `Hb Track - Backend/scripts/model_requirements.py`. Adicionar equivalência se necessário.

**Q: Metaprogramming não suportado?**
A: Usar perfil `lenient` OU mover lógica para `app/models/extensions/*.py`.

**Q: Relatório JSON vazio?**
A: Verificar se schema.sql foi atualizado após migrations (`pg_dump`).
```

**Critério de DONE:**
- ✅ `exit_codes.md` com seção completa sobre exit=4
- ✅ `CHECKLIST-CANONICA-MODELS.md` com STEP 4 integrado
- ✅ `model_requirements_guide.md` criado com exemplos práticos
- ✅ Documentos sincronizados com código real

---

## 🧪 TESTES DE ACEITAÇÃO GLOBAL

### Smoke Test Final (executar APÓS todas as fases)

```powershell
# ==================== CENÁRIO 1: Conformidade total ====================
Write-Host "`n[TEST 1] Validando model correto (attendance)..." -ForegroundColor Cyan
.\scripts\models_autogen_gate.ps1 -Table "attendance" -Profile "strict"
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ FAIL: Esperado exit=0 para model correto" -ForegroundColor Red
    exit 1
}
Write-Host "✅ PASS" -ForegroundColor Green

# ==================== CENÁRIO 2: Detecção de alucinação ====================
Write-Host "`n[TEST 2] Detectando coluna extra (alucinação)..." -ForegroundColor Cyan

# SETUP: Adicionar coluna fictícia
$backupPath = "app/models/attendance.py.bak"
Copy-Item "app/models/attendance.py" $backupPath
Add-Content "app/models/attendance.py" "`n    extra_field: Mapped[str] = mapped_column(String(100))"

# VALIDAR
.\scripts\models_autogen_gate.ps1 -Table "attendance" -Profile "strict"
$exitCode = $LASTEXITCODE

# CLEANUP
Move-Item $backupPath "app/models/attendance.py" -Force

if ($exitCode -ne 4) {
    Write-Host "❌ FAIL: Esperado exit=4 para coluna extra" -ForegroundColor Red
    exit 1
}

# Verificar relatório
$report = Get-Content "docs\_generated\requirements_report.json" | ConvertFrom-Json
if ($report.violations.Count -eq 0) {
    Write-Host "❌ FAIL: Relatório deveria ter violations" -ForegroundColor Red
    exit 1
}
Write-Host "✅ PASS" -ForegroundColor Green

# ==================== CENÁRIO 3: Exit code propagation ====================
Write-Host "`n[TEST 3] Validando propagação de exit codes..." -ForegroundColor Cyan

# Modificar baseline para forçar guard fail
$guardBackup = ".hb_guard/baseline.json.bak"
Copy-Item ".hb_guard/baseline.json" $guardBackup
Set-Content ".hb_guard/baseline.json" "{}"

.\scripts\models_autogen_gate.ps1 -Table "attendance"
$guardExit = $LASTEXITCODE

Move-Item $guardBackup ".hb_guard/baseline.json" -Force

if ($guardExit -ne 3) {
    Write-Host "❌ FAIL: Esperado exit=3 para guard violation" -ForegroundColor Red
    exit 1
}
Write-Host "✅ PASS" -ForegroundColor Green

# ==================== CENÁRIO 4: Perfis de validação ====================
Write-Host "`n[TEST 4] Testando perfis (strict vs fk)..." -ForegroundColor Cyan

# Executar com perfil "fk" (deve passar se apenas FKs estão ok)
.\scripts\models_autogen_gate.ps1 -Table "teams" -Profile "fk" -AllowCycleWarning
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ FAIL: Perfil 'fk' deveria passar para teams" -ForegroundColor Red
    exit 1
}
Write-Host "✅ PASS" -ForegroundColor Green

Write-Host "`n✅✅✅ TODOS OS TESTES PASSARAM ✅✅✅" -ForegroundColor Green
Write-Host "Sistema de validação está 100% funcional" -ForegroundColor Cyan
```

**Critério de DONE GLOBAL:**
- ✅ 4 cenários de smoke test passam
- ✅ Exit codes corretos em todos os casos (0/2/3/4)
- ✅ Relatórios JSON gerados e validados
- ✅ Nenhum falso positivo/negativo

---

## 📊 CHECKLIST DE ENTREGA

### Código

- [ ] `Hb Track - Backend/scripts/model_requirements.py` implementado (parsers + validator + CLI)
- [ ] `Hb Track - Backend/scripts/models_autogen_gate.ps1` modificado (STEP 4 + propagação exit codes)
- [ ] `Hb Track - Backend/tests/unit/test_model_requirements_*.py` criado (11+ casos de teste)
- [ ] Mapeamento PG→SA completo (15+ tipos)

### Documentação

- [ ] `docs/references/exit_codes.md` atualizado (exit=4)
- [ ] `docs/architecture/CHECKLIST-CANONICA-MODELS.md` atualizado (STEP 4)
- [ ] `docs/workflows/model_requirements_guide.md` criado
- [ ] Comentários inline no código (docstrings)

### Validação

- [ ] 11 testes unitários passam (`pytest tests/test_model_requirements.py`)
- [ ] 4 cenários de smoke test passam (script acima)
- [ ] Validação manual de `attendance` com exit=0
- [ ] Validação de alucinação forçada com exit=4

### Infra

- [ ] `docs/_generated/requirements_report.json` template criado
- [ ] Exit codes documentados em `docs/references/exit_codes.md`
- [ ] Baseline `.hb_guard/baseline.json` atualizado (se necessário)

---

## 🚨 CONDIÇÕES DE ABORT

### ABORTAR IMEDIATAMENTE SE:

1. **Pré-requisitos falharem:**
   - `parity_gate.ps1` não existir ou retornar exit != 0/2
   - `schema.sql` desatualizado (sem `CREATE TABLE attendance`)
   - Python < 3.11 ou SQLAlchemy < 2.0

2. **Testes unitários falharem >10%:**
   - Indica problemas fundamentais no parser/validator
   - Revisar implementação antes de prosseguir

3. **Smoke test global falhar:**
   - Sistema não está funcional
   - Não seguir para CI/CD integration

4. **Exit code propagation não funcionar:**
   - Crítico para debugging
   - Deve retornar 0/2/3/4 específicos (não 1 genérico)

---

## 📅 CRONOGRAMA DETALHADO

| Dia | Fase | Horas | Entregáveis |
|-----|------|-------|-------------|
| **D1** | FASE 1.1-1.2 | 8h | Parsers DDL + AST |
| **D2** | FASE 1.3-1.4 | 8h | Validator + CLI |
| **D3** | FASE 2-3 | 4h | Integração gate + exit codes |
| **D3** | FASE 4 | 4h | Smoke tests |
| **D4** | FASE 5 | 4h | Documentação |

**Total:** 28 horas (~3.5 dias úteis)

---

## 🎯 CRITÉRIO DE SUCESSO FINAL

### Definição de DONE:

**O sistema está pronto quando:**

1. ✅ `model_requirements.py` detecta 100% das violações nos testes
2. ✅ `models_autogen_gate.ps1` executa todas as 3 camadas (guard → parity → requirements)
3. ✅ Exit codes específicos (0/2/3/4) propagados corretamente
4. ✅ Smoke test global passa (4 cenários)
5. ✅ Documentação sincronizada com código (exit_codes, checklist, guia)
6. ✅ Validação de `attendance` retorna exit=0 (conformidade total)

**Assinatura de aceite:**
- [ ] Davi (Tech Lead) — Validação técnica
- [ ] Claude (AI Assistant) — Revisão de código + documentação

---

## 📎 ANEXOS

### A. Estrutura de arquivos esperada

```
handball_master/
├── scripts/
│   ├── model_requirements.py        # NOVO (FASE 1)
│   ├── models_autogen_gate.ps1      # MODIFICADO (FASE 2)
│   ├── parity_gate.ps1              # Existente
│   └── agent_guard.py               # Existente
├── tests/
│   └── test_model_requirements.py   # NOVO (FASE 1)
├── docs/
│   ├── references/
│   │   └── exit_codes.md            # MODIFICADO (FASE 5)
│   ├── architecture/
│   │   └── CHECKLIST-CANONICA-MODELS.md  # MODIFICADO (FASE 5)
│   ├── workflows/
│   │   └── model_requirements_guide.md   # NOVO (FASE 5)
│   └── _generated/
│       ├── schema.sql               # Existente (SSOT)
│       ├── requirements_report.json # NOVO (gerado)
│       └── parity_report.json       # Existente
└── app/
    └── models/
        └── attendance.py            # Model de teste
```

### B. Exemplo de requirements_report.json

```json
{
  "table": "attendance",
  "profile": "strict",
  "timestamp": "2024-02-08T14:32:15Z",
  "violations": [
    {
      "rule": "A1_EXTRA_COLUMN",
      "severity": "ERROR",
      "location": "app/models/attendance.py:42",
      "message": "Column 'extra_field' exists in model but not in schema.sql",
      "fix_suggestion": "Remove column definition or create migration to add it to DB"
    },
    {
      "rule": "B1_TYPE_MISMATCH",
      "severity": "ERROR",
      "location": "app/models/attendance.py:35",
      "message": "Column 'date' has type 'String' but schema.sql expects 'Date'",
      "fix_suggestion": "Change type to: date: Mapped[datetime.date] = mapped_column(Date, nullable=False)"
    }
  ],
  "summary": {
    "total_violations": 2,
    "errors": 2,
    "warnings": 0,
    "conformity": "FAIL"
  }
}
```

### C. Comandos de referência rápida

```powershell
# Validação isolada (requirements only)
python "Hb Track - Backend/scripts/model_requirements.py" --table attendance --profile strict

# Gate completo (3 camadas)
."\Hb Track - Backend\scripts\models_autogen_gate.ps1" -Table "attendance" -Profile "strict"

# Gate com allowlist (modificações permitidas)
.\scripts\models_autogen_gate.ps1 -Table "attendance" -Allow "app/models/attendance.py"

# Gate para ciclos FK (perfil relaxado)
.\scripts\models_autogen_gate.ps1 -Table "teams" -Profile "fk" -AllowCycleWarning

# Forçar recreação (skeleton + autogen)
.\scripts\models_autogen_gate.ps1 -Table "new_table" -Create

# Atualizar baseline após mudanças aprovadas
python scripts/agent_guard.py snapshot
```

---

**FIM DA EXEC_TASK**

**Status:** ✅ PRONTO PARA EXECUÇÃO  
**Próximo passo:** Iniciar FASE 1 (implementação de `model_requirements.py`)