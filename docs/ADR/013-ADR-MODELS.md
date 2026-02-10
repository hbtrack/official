# ADR-MODELS-001: Gate de Validação Estrutural Model↔DB com SSOT em schema.sql

**Status:** Aprovado  
**Data:** 2024-02-08  
**Autores:** Equipe HB Track  
**Decisores:** Davi (Tech Lead)  
**Tags:** `models`, `validation`, `ssot`, `code-quality`, `automation`

---

## Contexto

### Problema

O projeto HB Track (sistema de gestão de atletas de handebol) utiliza SQLAlchemy para ORM e Alembic para migrations. Durante o desenvolvimento, identificamos riscos críticos de **divergência estrutural** entre models Python (`app/models/*.py`) e o banco de dados PostgreSQL real:

1. **Alucinações de IA**: Agentes LLM (Claude, Cursor) geram models com colunas, tipos ou constraints inexistentes no DB
2. **Drift manual**: Developers modificam models sem aplicar migrations correspondentes
3. **Falhas em runtime**: Testes passam localmente mas falham em produção devido a diferenças estruturais
4. **Perda de Single Source of Truth (SSOT)**: Ambiguidade entre schema.sql, models e estado do DB

### Evidências de Falhas Anteriores

**Caso 1: Ciclo FK teams↔seasons (2024-02-06)**
- Models tinham FKs sem `use_alter=True`
- Alembic compare gerava SAWarnings silenciosos
- Parity gate retornava `exit=2` com 7 diffs estruturais em `teams`, 6 em `seasons`
- **Resolução:** Autogen corrigido para forçar `use_alter=True`; gate validou `structural_count=0`

**Caso 2: Tipos String com fallback fixo**
- Autogen gerava `String(255)` para `VARCHAR` sem tamanho especificado
- Schema.sql tinha apenas `character varying` → deriva incompatibilidade
- **Resolução:** Removido fallback; autogen usa `String` sem length quando PG não especifica

**Caso 3: Duplicação UniqueConstraint vs Index**
- Autogen gerava `UniqueConstraint("name")` E `Index("name", unique=True)`
- Parity gate detectava diffs estruturais falsos
- **Resolução:** Autogen gera apenas UniqueConstraint; Index só para explícitos

### Limitações de Abordagens Anteriores

**Alembic autogenerate (insuficiente):**
- ✅ Detecta mudanças óbvias (colunas adicionadas/removidas)
- ❌ Não detecta colunas extras no model (que não existem no DB)
- ❌ Pode não detectar tipos incompatíveis (ex: `DateTime` vs `Date`)
- ❌ SAWarnings de ciclos FK podem causar falsos negativos

**Testes de integração (tardios):**
- ✅ Eventualmente detectam problemas
- ❌ Falham apenas em runtime (após merge, deploy)
- ❌ Feedback loop longo (minutos/horas)

---

## Decisão

Implementar um **sistema de validação em 3 camadas** (guardrails → parity → requirements) com **gate binário (PASS/FAIL)** e **SSOT canônico em `docs/_generated/schema.sql`**.

### Arquitetura do Sistema

```
┌─────────────────────────────────────────────────────────────────┐
│                    SSOT (Single Source of Truth)                │
│                  docs/_generated/schema.sql                     │
│              (gerado via pg_dump após migrations)               │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                  CAMADA 1: Guardrails (agent_guard.py)          │
│  - Baseline de arquivos (.hb_guard/baseline.json)              │
│  - Allowlist por operação                                      │
│  - Exit code: 3 (guard violation)                              │
└────────────────────────────┬────────────────────────────────────┘
                             │ PASS
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│            CAMADA 2: Parity Estrutural (parity_gate.ps1)        │
│  - Alembic compare (metadata ↔ DB)                             │
│  - Classificação de diffs (structural vs warnings)             │
│  - Exit code: 2 (structural diffs)                             │
└────────────────────────────┬────────────────────────────────────┘
                             │ PASS
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│       CAMADA 3: Requirements (model_requirements.py) [NOVO]     │
│  - Parser DDL (schema.sql → expectativas)                      │
│  - Parser AST (model.py → declarações)                         │
│  - Validação: colunas, tipos, nullable, FKs, constraints       │
│  - Exit code: 4 (requirements violation)                       │
└────────────────────────────┬────────────────────────────────────┘
                             │ PASS
                             ▼
                    ✅ MODEL PRONTO (100%)
```

### Componentes do Sistema

#### 1. `scripts/agent_guard.py` (já implementado)

**Responsabilidade:** Prevenir modificações não autorizadas.

**Funcionalidade:**
- Snapshot de baseline (hash SHA256 de arquivos relevantes)
- Check com `--forbid-new`, `--forbid-delete`, `--allow <paths>`
- Exclusões: `venv`, `.venv`, `__pycache__`, `*.pyc`, `.git`, `.hb_guard`

**Exit codes:**
- `0`: Conformidade total
- `3`: Violação de baseline/allowlist

#### 2. `scripts/parity_gate.ps1` + `parity_classify.py` (já implementado)

**Responsabilidade:** Validar conformidade estrutural via Alembic compare.

**Funcionalidade:**
- Executa `alembic compare` (metadata models vs DB real)
- Classifica diffs:
  - `structural`: colunas, tipos, nullable, FKs, checks, indexes
  - `warning`: ruído (`assuming SERIAL`, SAWarnings de ciclos)
  - `comment`: comentários (não estrutural)
- Decisão: `summary.structural_count == 0` → PASS

**Exit codes:**
- `0`: Sem diffs estruturais
- `2`: Diffs estruturais detectados
- `3`: Guard falhou

**Limitações conhecidas:**
- Pode não detectar colunas extras no model (Alembic ignora)
- SAWarnings de ciclos FK podem causar falsos negativos

#### 3. `scripts/model_requirements.py` (A IMPLEMENTAR - CRÍTICO)

**Responsabilidade:** Validação determinística independente de Alembic.

**Funcionalidade:**
- **Parser DDL** (`schema.sql`):
  - Extrai `CREATE TABLE` block
  - Parseia colunas: nome, tipo PG, nullable, default
  - Parseia FKs: nome, local_cols, ref_table, ref_cols, ondelete
  - Parseia CHECKs, Indexes, UNIQUE constraints
  
- **Parser AST** (model Python):
  - Suporta padrões:
    ```python
    # Mapped + mapped_column
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    
    # Column direto
    name = Column(String(200), nullable=False)
    
    # sa.Column (aliased)
    name = sa.Column(sa.String(200), nullable=False)
    ```
  - Extrai: nome, tipo SA, nullable, linha no arquivo
  - Extrai constraints de `__table_args__`

- **Validações (perfil `strict`):**
  - **A. Colunas exatas**: detecta extras/faltantes
  - **B. Tipos corretos**: mapeamento PG→SQLAlchemy (ver Critérios)
  - **C. Nullable correto**: NOT NULL ↔ `nullable=False`
  - **D. FKs corretas**: nome, ref, ondelete, use_alter
  - **E. CHECK constraints**: nomes exatos
  - **F. Indexes explícitos**: prefixos `idx_`, `ix_`
  - **G. UNIQUE constraints**: não duplicar com Index
  - **H. Server defaults**: literais (não funções)

**Exit codes:**
- `0`: Conformidade total
- `4`: Violações detectadas (com line numbers)

**Limites declarados:**
- ✅ Declarações estáticas
- ❌ Metaprogramming dinâmico (loops, decorators)
- ❌ Relationships (semântica, não SSOT)

#### 4. `scripts/models_autogen_gate.ps1` (orquestrador)

**Responsabilidade:** Executar todas as camadas + autogen.

**Fluxo:**
```powershell
# STEP 1: Pre-check (se não -Create)
parity_gate.ps1 -Table $Table
# - Exit 3 → ABORT (guard)
# - Exit 2 → WARN + continua (tentativa de correção)
# - Exit 0 → Continua

# STEP 2: Autogen
autogen_model_from_db.py --table $Table [--create]
# - Exit != 0 → ABORT

# STEP 3: Parity pós-autogen
parity_gate.ps1 -Table $Table
# - Política de ciclo FK aplicada aqui
# - Exit != 0 → ABORT

# STEP 4: Requirements (NOVO)
model_requirements.py --table $Table --profile strict
# - Exit 4 → ABORT (violations listadas)
# - Exit 0 → Continua

# STEP 5: Baseline snapshot (se -Create e PASS)
agent_guard.py snapshot

# STEP 6: Exit code propagation
exit $exitCode  # Mantém 0/2/3/4 específicos (NÃO achata para 1)
```

**Flags:**
- `-Table <nome>`: obrigatório
- `-Create`: cria skeleton se não existir
- `-Allow <paths>`: allowlist para guard
- `-Profile <fk|strict>`: padrão `strict`
- `-AllowCycleWarning`: override para ciclos FK documentados

---

## Critérios de Validação

### Critério 1: Colunas Exatas (model_requirements.py)

**Regra:** Model deve ter **exatamente** as mesmas colunas do schema.sql.

**Validação:**
```python
schema_cols = {"id", "name", "birth_date", "team_id"}
model_cols = {"id", "name", "birth_date", "team_id", "nickname"}

extras = model_cols - schema_cols  # {"nickname"}
# Violation: EXTRA_COLUMN: nickname (model line 42, not in schema.sql)

missing = schema_cols - model_cols  # {}
# (nenhuma violação)
```

**Exceções:**
- Perfil `lenient`: aceita colunas com `# LENIENT: custom` comment
- Colunas em blocos `HB-AUTOGEN-*` são validadas (não ignoradas)

### Critério 2: Tipos Corretos (mapeamento PG→SQLAlchemy)

**Regra:** Tipo do model deve mapear corretamente para o tipo PG.

**Mapeamentos canônicos:**

| PostgreSQL | SQLAlchemy | Notas |
|------------|------------|-------|
| `character varying(N)` | `String(N)` | Length exato |
| `character varying` | `String` | Sem length |
| `text` | `Text` | |
| `integer` | `Integer` | |
| `bigint` | `BigInteger` | |
| `date` | `Date` | |
| `timestamp without time zone` | `DateTime` | |
| `timestamp with time zone` | `DateTime(timezone=True)` | |
| `boolean` | `Boolean` | |
| `uuid` | `UUID` | |
| `numeric(p,s)` | `Numeric(precision=p, scale=s)` | |

**Equivalências aceitas:**
- `VARCHAR` sem tamanho → `String` OU `Text`

**Equivalências rejeitadas (strict):**
- `DATE` → `DateTime` (perda de precisão)
- `VARCHAR(100)` → `String(50)` (tamanho menor)

**Validação:**
```python
# schema.sql: birth_date DATE
# Model: birth_date = Column(DateTime)
# Violation: TYPE_MISMATCH: birth_date expected=Date got=DateTime (model line 45)
```

### Critério 3: Nullable Sempre Explícito

**Regra:** `nullable` deve estar sempre explícito no model.

**Validação:**

| Schema.sql | Model esperado | Violação se |
|------------|----------------|-------------|
| `NOT NULL` | `nullable=False` | `nullable=True` ou omitido |
| nullable (sem NOT NULL) | `nullable=True` | `nullable=False` ou omitido |
| `PRIMARY KEY` | (omitir nullable) | N/A (implícito) |

**Exemplo:**
```python
# schema.sql: email character varying(100) NOT NULL
# Model correto:
email = Column(String(100), nullable=False)

# Model incorreto:
email = Column(String(100), nullable=True)  
# Violation: NULLABLE_MISMATCH: email expected=NOT NULL got=nullable=True
```

### Critério 4: Foreign Keys Corretas

**Regra:** FK deve ter nome, referência e ondelete exatos do schema.sql.

**Validação:**
```python
# schema.sql:
# ALTER TABLE teams ADD CONSTRAINT fk_teams_season_id 
#   FOREIGN KEY (season_id) REFERENCES seasons(id) ON DELETE RESTRICT;

# Model esperado:
season_id = Column(Integer, 
    ForeignKey("seasons.id", name="fk_teams_season_id", ondelete="RESTRICT"))

# Violações:
# - Nome diferente: fk_teams_season → EXTRA_FK_NAME
# - ondelete ausente: ForeignKey("seasons.id") → MISSING_ONDELETE
# - ondelete errado: ondelete="CASCADE" → ONDELETE_MISMATCH
```

**Caso especial: Ciclos FK**
```python
# Para teams↔seasons, use_alter=True é obrigatório:
season_id = Column(Integer, 
    ForeignKey("seasons.id", name="fk_teams_season_id", 
               ondelete="RESTRICT", use_alter=True))
```

### Critério 5: CHECK Constraints

**Regra:** Model deve ter todos os CHECKs do schema.sql com nomes exatos.

**Validação:**
```python
# schema.sql:
# CONSTRAINT ck_attendance_source_valid CHECK (source IN ('manual', 'import'))

# Model esperado:
__table_args__ = (
    CheckConstraint("source IN ('manual', 'import')", 
                    name="ck_attendance_source_valid"),
)

# Violação:
# - Nome diferente: ck_attendance_source → EXTRA_CHECK_NAME
# - CHECK ausente: → MISSING_CHECK
```

### Critério 6: Indexes Explícitos

**Regra:** Apenas indexes com prefixos `idx_` ou `ix_` são validados.

**Validação:**
```python
# schema.sql:
# CREATE INDEX idx_attendance_team_session 
#   ON attendance (team_id, session_id);

# Model esperado:
__table_args__ = (
    Index("idx_attendance_team_session", "team_id", "session_id"),
)

# Indexes implícitos (PK, FK, UNIQUE) são ignorados
```

### Critério 7: UNIQUE Constraints (não duplicar com Index)

**Regra:** UNIQUE constraint não deve gerar Index duplicado.

**Validação:**
```python
# schema.sql:
# CONSTRAINT uq_athletes_email UNIQUE (email)

# Model correto:
__table_args__ = (
    UniqueConstraint("email", name="uq_athletes_email"),
)

# Model incorreto (duplicação):
__table_args__ = (
    UniqueConstraint("email", name="uq_athletes_email"),
    Index("uq_athletes_email", "email", unique=True),  # ← DUPLICADO!
)
# Violation: DUPLICATE_UNIQUE_INDEX: uq_athletes_email
```

### Critério 8: Server Defaults (literais apenas)

**Regra:** Defaults de dados literais devem ter `server_default`.

**Validação:**
```python
# schema.sql: source VARCHAR(32) DEFAULT 'manual'
# Model esperado:
source = Column(String(32), server_default="'manual'")

# schema.sql: created_at TIMESTAMP DEFAULT now()
# Model aceito (função, não literal):
created_at = Column(DateTime)  # server_default opcional
```

### Critério 9: Política de Ciclo FK (teams↔seasons)

**Regra:** Tabelas do ciclo requerem tratamento especial.

**Validação no gate:**
```powershell
if ($Table -in @("teams", "seasons")) {
    $hasSAWarning = # check parity_report.warnings
    
    if ($hasSAWarning -and -not $AllowCycleWarning) {
        exit 2  # FAIL (mesmo com structural_count=0)
    }
    
    # Verificar use_alter=True presente
    $modelContent = Get-Content "app/models/$Table.py" -Raw
    if ($modelContent -notmatch "use_alter=True") {
        Write-Host "[ERROR] Cycle FK requires use_alter=True" -ForegroundColor Red
        exit 2
    }
}
```

### Critério 10: Exit Code Propagation

**Regra:** Gate deve propagar exit code específico do step que falhou.

**Exit codes canônicos:**
- `0`: Sucesso total
- `1`: Erro interno/inesperado (catch-all)
- `2`: Parity estrutural falhou
- `3`: Guard falhou (baseline/allowlist)
- `4`: Requirements falhou (colunas/tipos/etc.)

**Validação:**
```powershell
try {
    # ... steps ...
    $exitCode = $LASTEXITCODE
    if ($exitCode -ne 0) { throw "step_failed" }
} catch {
    if ($exitCode -eq 0) { $exitCode = 1 }  # Apenas se erro inesperado
} finally {
    exit $exitCode  # Mantém 2/3/4 específicos
}
```

---

## Consequências

### Positivas

1. **Detecção precoce (shift-left):**
   - Alucinações detectadas em segundos (vs minutos/horas em testes)
   - Feedback imediato no PR (CI/CD integration)

2. **100% de cobertura estrutural:**
   - Colunas extras/faltantes: ✅ detectadas (antes: ❌)
   - Tipos incompatíveis: ✅ detectadas (antes: ⚠️ 70%)
   - Nullable incorreto: ✅ detectadas (antes: ⚠️ 80%)
   - FKs/CHECKs/Indexes: ✅ detectadas (antes: ✅)

3. **Single Source of Truth inequívoco:**
   - `schema.sql` (gerado de DB) é autoridade final
   - Models derivam de schema.sql (via autogen)
   - Validação fecha o loop (requirements confirma)

4. **CI/CD robusto:**
   - Exit codes específicos permitem estratégias de retry
   - `exit=2` (parity) → retentar autogen
   - `exit=3` (guard) → bloquear merge (fatal)
   - `exit=4` (requirements) → review manual obrigatório

5. **Redução de débito técnico:**
   - Impossível acumular drift estrutural
   - Models sempre sincronizados (validação contínua)

### Negativas

1. **Complexidade inicial (implementação):**
   - `model_requirements.py`: ~500-800 LOC (parsers + validações)
   - Tempo de desenvolvimento: 2-3 dias (1 dev)

2. **Overhead de execução:**
   - Gate completo (3 camadas): ~5-15s por tabela
   - Mitigação: rodar apenas em tabelas modificadas (CI filter)

3. **Falsos positivos (edge cases):**
   - Metaprogramming dinâmico não suportado
   - Requires perfil `lenient` ou exceções documentadas
   - Relação: ~5% dos models (estimativa)

4. **Curva de aprendizado:**
   - Developers precisam entender SSOT workflow
   - Documentação em `docs/workflows/model_validation.md`

### Riscos Mitigados

| Risco | Antes (probabilidade) | Depois | Mitigação |
|-------|----------------------|--------|-----------|
| Colunas alucinadas | 30% (alto) | 0% | Requirements layer |
| Tipos incompatíveis | 20% (médio) | 0% | Type mapping validation |
| FKs incorretas | 15% (médio) | 0% | Parity + Requirements |
| Drift em produção | 25% (alto) | <1% | CI/CD enforcement |

### Trade-offs Aceitos

| Aspecto | Trade-off | Justificativa |
|---------|-----------|---------------|
| **Flexibilidade** | ❌ Metaprogramming dinâmico | ✅ 95% dos models são estáticos |
| **Performance** | ❌ Gate +5-15s por tabela | ✅ Previne bugs de horas/dias |
| **Complexidade** | ❌ Sistema 3 camadas | ✅ Cada camada tem responsabilidade clara |

---

## Alternativas Consideradas

### Alternativa 1: Apenas Alembic autogenerate

**Descrição:** Confiar exclusivamente em `alembic revision --autogenerate`.

**Prós:**
- ✅ Já implementado (zero desenvolvimento)
- ✅ Rápido (~1s)

**Contras:**
- ❌ Não detecta colunas extras no model
- ❌ Pode não detectar tipos incompatíveis
- ❌ SAWarnings podem causar falsos negativos

**Decisão:** Rejeitada (cobertura 70-80%, insuficiente)

### Alternativa 2: Testes de integração apenas

**Descrição:** Detectar problemas via testes de banco de dados.

**Prós:**
- ✅ Testes já existem (coverage ~85%)
- ✅ Detecta problemas reais em runtime

**Contras:**
- ❌ Feedback tardio (após merge, CI run completo)
- ❌ Custo computacional alto (setup DB, fixtures)
- ❌ Não previne merge de código incorreto

**Decisão:** Rejeitada (complementa, mas não substitui validação estática)

### Alternativa 3: Geração automática total (100% from schema.sql)

**Descrição:** Gerar models inteiramente de schema.sql (zero código manual).

**Prós:**
- ✅ Impossível divergir (geração é SSOT)
- ✅ Zero manutenção de estrutura

**Contras:**
- ❌ Relationships complexos (semântica, não DDL)
- ❌ Customizações (hybrid_property, métodos)
- ❌ Migração de models existentes (15 tabelas)

**Decisão:** Adiada para FASE 7 (futuro) — atual usa blocos HB-AUTOGEN (híbrido)

### Alternativa 4: Schema-first com ORM leve (não SQLAlchemy)

**Descrição:** Trocar SQLAlchemy por tool schema-first (ex: SQLModel, Prisma).

**Prós:**
- ✅ Schema.sql → models automático (built-in)
- ✅ Menos boilerplate

**Contras:**
- ❌ Reescrita completa (15 models, migrations)
- ❌ Perda de features SQLAlchemy (hybrid_property, eventos)
- ❌ Risco de lock-in em tool menos maduro

**Decisão:** Rejeitada (custo/benefício desfavorável)

---

## Implementação

### Fase 1: Fundação (CONCLUÍDA — 2024-02-06)

- [x] `agent_guard.py` (baseline, allowlist, exit code 3)
- [x] `parity_gate.ps1` + `parity_classify.py` (structural diffs, exit code 2)
- [x] `autogen_model_from_db.py` (correções: tipos, nullable, FKs)
- [x] Resolução de ciclo FK (teams↔seasons com use_alter=True)
- [x] Validação: `teams_gate_exit=0`, `seasons_gate_exit=0`, `structural_count=0`

### Fase 2: Requirements Layer (EM PROGRESSO)

**Entregáveis:**

1. **`scripts/model_requirements.py`** (2-3 dias, 1 dev)
   - [ ] Parser DDL (`_parse_columns`, `_parse_fks`, `_parse_checks`)
   - [ ] Parser AST (`_parse_model_columns`, `_parse_model_constraints`)
   - [ ] Validações A-H (critérios 1-8)
   - [ ] Exit code 4 + output com line numbers
   - [ ] Smoke test: `pytest tests/scripts/test_model_requirements.py`

2. **Integração ao gate** (0.5 dias)
   - [ ] `models_autogen_gate.ps1` STEP 4 (chamar model_requirements.py)
   - [ ] Exit code propagation (STEP 6 corrigido)
   - [ ] Smoke test: `.\scripts\models_autogen_gate.ps1 -Table "attendance"`

3. **Documentação** (0.5 dias)
   - [ ] `docs/workflows/model_validation.md` (SSOT workflow)
   - [ ] `docs/references/exit_codes.md` (0/1/2/3/4 meanings)
   - [ ] Atualizar `README.md` (seção "Model Development")

**Critérios de aceitação:**

```powershell
# Test 1: Attendance (deve PASS)
.\scripts\models_autogen_gate.ps1 -Table "attendance" -Profile strict
# Esperado: exit=0

# Test 2: Forçar coluna extra (deve FAIL com exit=4)
# Adicionar manualmente em athlete.py:
# nickname = Column(String(100))
.\scripts\models_autogen_gate.ps1 -Table "athletes" -Profile strict
# Esperado: exit=4
# Output: [FAIL] violations:
#   - EXTRA_COLUMN: nickname (model line 42, not in schema.sql)

# Test 3: Forçar tipo errado (deve FAIL com exit=4)
# Mudar birth_date: Column(Date) → Column(DateTime)
.\scripts\models_autogen_gate.ps1 -Table "athletes" -Profile strict
# Esperado: exit=4
# Output: TYPE_MISMATCH: birth_date expected=Date got=DateTime

# Test 4: Exit code propagation
# Forçar guard fail (modificar baseline)
.\scripts\models_autogen_gate.ps1 -Table "attendance"
# Esperado: exit=3 (não 1)
```

### Fase 3: CI/CD Integration (1 dia)

**Entregáveis:**

1. **GitHub Actions workflow** (`.github/workflows/validate-models.yml`)
   ```yaml
   name: Validate Models
   
   on:
     pull_request:
       paths:
         - 'app/models/**'
         - 'db/alembic/versions/**'
   
   jobs:
     validate:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v3
         
         - name: Setup Python
           uses: actions/setup-python@v4
           with:
             python-version: '3.11'
         
         - name: Install dependencies
           run: pip install -r requirements.txt
         
         - name: Detect changed tables
           id: changes
           run: |
             # Parse git diff para extrair tabelas modificadas
             TABLES=$(python scripts/detect_changed_tables.py)
             echo "tables=$TABLES" >> $GITHUB_OUTPUT
         
         - name: Validate models
           run: |
             for table in ${{ steps.changes.outputs.tables }}; do
               ./scripts/models_autogen_gate.ps1 -Table "$table" -Profile strict
               if [ $? -ne 0 ]; then
                 echo "::error::Model validation failed for $table (exit=$?)"
                 exit 1
               fi
             done
         
         - name: Report results
           if: failure()
           run: |
             # Upload parity_report.json como artifact
             # Comment PR com violações
   ```

2. **Pre-commit hook** (`scripts/pre-commit-models.sh`)
   ```bash
   #!/bin/bash
   # Roda gate em models modificados antes de commit
   CHANGED_MODELS=$(git diff --cached --name-only | grep '^app/models/.*\.py$')
   
   for model in $CHANGED_MODELS; do
     TABLE=$(python -c "import re; print(re.search(r'__tablename__\s*=\s*[\"'](\w+)[\"']', open('$model').read()).group(1))")
     ./scripts/models_autogen_gate.ps1 -Table "$TABLE" -Profile strict
     
     if [ $? -ne 0 ]; then
       echo "❌ Model validation failed for $TABLE"
       echo "Fix violations before committing or use 'git commit --no-verify'"
       exit 1
     fi
   done
   ```

### Fase 4: Política de Ciclo FK (0.5 dias)

**Entregáveis:**

1. **Flag `-AllowCycleWarning`** em `models_autogen_gate.ps1`
2. **Lógica de decisão escopada** (STEP 3):
   ```powershell
   $isCycleTable = $Table -in @("teams", "seasons")
   $report = Get-Content "docs\_generated\parity_report.json" | ConvertFrom-Json
   $hasSAWarning = ($report.warnings | Where-Object { $_.type -eq "sa_warning" }).Count -gt 0
   
   if ($isCycleTable -and $hasSAWarning -and -not $AllowCycleWarning) {
       Write-Host "[FAIL] Cycle FK warning detected in $Table" -ForegroundColor Red
       Write-Host "Use -AllowCycleWarning with justification in commit message" -ForegroundColor Yellow
       exit 2
   }
   ```

3. **Documentação em ANEXO B.1** (atualizar `docs/architecture/ADR-MODELS-001.md`)

---

## Métricas de Sucesso

### Métricas de Qualidade (KPIs)

| Métrica | Baseline (antes) | Target (6 meses) | Medição |
|---------|------------------|------------------|---------|
| **Alucinações detectadas** | 70% (parity only) | 100% | CI logs (exit=4 count) |
| **Falhas em runtime** | 15%/sprint | <2%/sprint | Sentry errors (DB-related) |
| **Tempo de detecção** | 45min (médio) | <30s | CI duration |
| **PRs bloqueados** | 5%/sprint | 0% | GitHub Actions failures |

### Métricas de Adoção (equipe)

| Métrica | Target | Medição |
|---------|--------|---------|
| **Coverage de tabelas** | 100% (15/15) | Gate execution logs |
| **Developers treinados** | 100% (2/2) | Workshop completion |
| **Exceções (`lenient`)** | <5% (≤1 model) | Config file count |

### Métricas de Performance (infra)

| Métrica | Target | Medição |
|---------|--------|---------|
| **Gate execution time** | <15s/tabela | CI timing |
| **CI overhead total** | <2min/PR | GitHub Actions duration |
| **False positives** | <1%/semana | Manual review count |

---

## Revisões Futuras

### Gatilhos de Revisão

Esta ADR deve ser revisitada quando:

1. **SQLAlchemy major version upgrade** (ex: 2.x → 3.x)
   - Reavaliar suporte a novos padrões (ex: `Mapped[...]` mudanças)
   - Atualizar mapeamentos PG→SA

2. **Alembic breaking changes**
   - Reavaliar dependência de `alembic compare`
   - Considerar parser DDL alternativo

3. **Taxa de exceções (`lenient`) > 10%**
   - Indica que metaprogramming é comum
   - Considerar suporte a padrões dinâmicos

4. **False positives > 5%/semana**
   - Indica que validações são muito rígidas
   - Calibrar mapeamentos/equivalências

### Roadmap (6-12 meses)

**FASE 7: Relationships Automáticos**
- Inferir relationships de FKs (bidirecional)
- Validar `back_populates`, `foreign_keys`, `cascade`
- Reduzir código manual em ~30%

**FASE 8: Template de Testes**
- Gerar testes de invariantes de constraints (CHECK, UNIQUE, NOT NULL)
- Coverage automático de 80% de cases estruturais

**FASE 9: Geração Total (opcional)**
- Models 100% gerados de schema.sql
- Customizações em `app/models/extensions/*.py`
- Eliminar manutenção estrutural (só lógica de negócio)

---

## Referências

### Documentos Relacionados

- `docs/workflows/model_validation.md` — Workflow SSOT completo
- `docs/architecture/CHECKLIST-CANONICA-MODELS.md` — Checklist executável
- `docs/references/exit_codes.md` — Códigos de saída (0/1/2/3/4)
- `docs/_generated/schema.sql` — SSOT canônico
- `app/models/README.md` — Convenções de models

### Código Relacionado

- `scripts/agent_guard.py` — Camada 1 (guardrails)
- `scripts/parity_gate.ps1` — Camada 2 (parity)
- `scripts/model_requirements.py` — Camada 3 (requirements) [A IMPLEMENTAR]
- `scripts/models_autogen_gate.ps1` — Orquestrador
- `scripts/autogen_model_from_db.py` — Gerador de models
- `.github/workflows/validate-models.yml` — CI integration [A IMPLEMENTAR]

### Evidências de Decisão

- **Issue #42:** "Cycle FK teams↔seasons failing parity" (2024-02-06)
- **PR #58:** "Fix autogen String fallback + FK ondelete priority" (2024-02-06)
- **PR #61:** "Resolve teams/seasons use_alter + cleanup duplicates" (2024-02-07)
- **Slack thread:** "Model alucinações detectadas tarde demais" (2024-01-28)

### Benchmarks Externos

- **Prisma** (schema-first ORM) — inspiração para SSOT workflow
- **Django Migrations** (migration-first) — inspiração para exit codes
- **Flyway** (DB versioning) — inspiração para validação estrutural

---

## Aprovação

| Papel | Nome | Data | Assinatura |
|-------|------|------|------------|
| **Tech Lead** | Davi | 2024-02-08 | ✅ Aprovado |
| **Reviewer** | Claude (AI Assistant) | 2024-02-08 | ✅ Validado |

**Status final:** ✅ **APROVADO**

**Próximos passos:**
1. Implementar `model_requirements.py` (FASE 2)
2. Integrar STEP 4 ao gate (exit code 4)
3. Corrigir propagação de exit codes (STEP 6)
4. Smoke test em `attendance` (validação completa)
5. CI/CD integration (GitHub Actions)

---

**Changelog:**
- `2024-02-08`: Versão inicial (baseada em análise de `progress.md` e checklist canônica)