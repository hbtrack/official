# Exit Codes Reference - HB Track

Guia de referência para os códigos de saída dos scripts de validação do HB Track.

---

## Exit Code 0: Success

**Significado:** Operação completada com sucesso, sem erros ou violations.

**Scripts que retornam 0:**
- `model_requirements.py` (quando model está 100% conforme)
- `models_autogen_gate.ps1` (quando todos os gates passam)
- `parity_gate.ps1` (quando estrutura DB ↔ Model está sincronizada)
- `parity_scan.ps1` (quando Alembic não detecta diffs estruturais)
- `parity_classify.py` (quando classificação conclui sem diffs impeditivos)
- `agent_guard.py` (quando nenhum arquivo protegido foi modificado)

**Exemplo:**
```powershell
.\scripts\models_autogen_gate.ps1 -Table "attendance" -Profile "strict"
# Output: ✅ ALL GATES PASSED — Model is 100% conformant
$LASTEXITCODE  # 0
```

---

## Exit Code 1: Internal Error

**Significado:** Erro interno do script (crash, exception não tratada).

**Causas comuns:**
- Arquivo não encontrado (schema.sql, model.py)
- Erro de sintaxe Python
- Dependência faltando
- Problema de permissão de arquivo

**Resolução:**
1. Verificar stack trace completo no output
2. Confirmar que pré-requisitos estão satisfeitos (venv, dependências)
3. Verificar paths de arquivos
4. Reportar como bug se persistir

**Exemplo:**
```powershell
python scripts\model_requirements.py --table nonexistent
# Output: RuntimeError: CREATE TABLE for 'nonexistent' not found in schema.sql
$LASTEXITCODE  # 1
```

---

## Exit Code 2: Parity Structural Diffs

**Origem:** `parity_gate.ps1` / `alembic compare`

**Significado:** A estrutura do model SQLAlchemy difere do banco de dados PostgreSQL.

**Causas comuns:**
- Coluna adicionada/removida no model sem migration
- Tipo de coluna alterado
- Constraint (FK, CHECK, UNIQUE) modificada
- Nullable alterado
- Migration pendente não aplicada

**Resolução:**
1. Revisar `docs/_generated/parity_report.json` (se disponível)
2. Identificar as diferenças listadas no output
3. **Opção A (migration necessária):**
   ```powershell
   alembic revision --autogenerate -m "descrição"
   alembic upgrade head
   ```
4. **Opção B (model incorreto):**
   - Reverter mudanças no model
   - Ou rodar autogen: `.\scripts\models_autogen_gate.ps1 -Table <nome>`

**Exemplo:**
```powershell
.\scripts\parity_gate.ps1 -Table "attendance"
# Output:
# [FAIL] Parity check failed (exit=2)
# - modify_nullable(attendance, 'athlete_id', existing_type, nullable=False → True)
$LASTEXITCODE  # 2
```

---

## Exit Code 3: Guard Violations

**Origem:** `agent_guard.py` (via `models_autogen_gate.ps1`)

**Significado:** Arquivo protegido foi modificado sem autorização explícita (via `-Allow` flag).

**Causas comuns:**
- Arquivo de test modificado (`tests/**`)
- Arquivo de API modificado (`app/routes/**`)
- Arquivo de ML/Celery modificado (`app/tasks/**`)
- Script auxiliar modificado sem estar na allowlist

**Resolução:**
1. Verificar output do agent_guard indicando qual arquivo foi modificado
2. **Opção A (modificação legítima):**
   ```powershell
   .\scripts\models_autogen_gate.ps1 -Table <nome> -Allow "path/to/file.py"
   ```
3. **Opção B (modificação acidental):**
   ```powershell
   git restore path/to/file.py  # Reverter mudanças
   ```
4. **Opção C (atualizar baseline):**
   ```powershell
   python scripts\agent_guard.py snapshot  # Apenas se mudança é permanente
   ```

**Exemplo:**
```powershell
.\scripts\models_autogen_gate.ps1 -Table "teams"
# Output:
# [FAIL] [GUARD] exited with code 3
# - Modified: app/routes/teams.py (not in allowlist)
$LASTEXITCODE  # 3
```

---

## Exit Code 4: Requirements Violation

**Origem:** `model_requirements.py`

**Significado:** O model SQLAlchemy viola expectativas estruturais de `schema.sql` (SSOT).

**Causas comuns:**
- **A1_EXTRA_COLUMN:** Coluna no model que não existe em schema.sql
- **A2_MISSING_COLUMN:** Coluna em schema.sql que falta no model
- **B1_TYPE_MISMATCH:** Tipo PG ↔ SA incompatível (ex: Date vs String)
- **C1_NULLABLE_MISMATCH:** NOT NULL no DB mas nullable=True no model
- **D4_MISSING_USE_ALTER:** FK de ciclo sem `use_alter=True`
- **E1_MISSING_CHECK:** CHECK constraint faltando no model
- **F1_MISSING_INDEX:** INDEX explícito faltando
- **G1_EXTRA_UNIQUE:** UNIQUE constraint duplicado com Index
- **H1_MISSING_SERVER_DEFAULT:** Server default faltando (ex: `server_default=False`)

**Resolução:**
1. Revisar `docs/_generated/requirements_report.json` (se implementado)
2. Verificar violations listadas no output (com line numbers)
3. Corrigir model conforme fix suggestions
4. Reexecutar gate: `.\scripts\models_autogen_gate.ps1 -Table <nome>`

**Exemplo:**
```powershell
.\scripts\models_autogen_gate.ps1 -Table "attendance" -Profile "strict"
# Output:
# [FAIL] model_requirements strict profile violations (table=attendance)
#   - MISSING_SERVER_DEFAULT: is_medical_restriction expected_default=default_literal:false model_line=174
#   - MISSING_SERVER_DEFAULT: source expected_default=default_literal:'manual'::character varying model_line=155
$LASTEXITCODE  # 4
```

**Fix suggestions por tipo de violation:**

### A1_EXTRA_COLUMN
```python
# ❌ ANTES (coluna não existe em schema.sql)
extra_field: Mapped[str] = mapped_column(String(100))

# ✅ DEPOIS (remover OU criar migration)
# Remover linha OU:
alembic revision --autogenerate -m "add extra_field to attendance"
```

### B1_TYPE_MISMATCH
```python
# ❌ ANTES (schema.sql tem Date, model tem String)
date: Mapped[str] = mapped_column(String(20))

# ✅ DEPOIS
date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
```

### C1_NULLABLE_MISMATCH
```python
# ❌ ANTES (schema.sql tem NOT NULL, model tem nullable=True implícito)
athlete_id: Mapped[int] = mapped_column(Integer, ForeignKey("athletes.id"))

# ✅ DEPOIS
athlete_id: Mapped[int] = mapped_column(Integer, ForeignKey("athletes.id"), nullable=False)
```

### D4_MISSING_USE_ALTER
```python
# ❌ ANTES (FK de ciclo sem use_alter)
season_id: Mapped[int] = mapped_column(Integer, ForeignKey("seasons.id"))

# ✅ DEPOIS (para ciclos FK documentados)
season_id: Mapped[int] = mapped_column(
    Integer, 
    ForeignKey("seasons.id", use_alter=True, name="fk_teams_season_id")
)
```

### H1_MISSING_SERVER_DEFAULT
```python
# ❌ ANTES (schema.sql tem DEFAULT false, model não tem server_default)
is_active: Mapped[bool] = mapped_column(Boolean, nullable=False)

# ✅ DEPOIS
is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))
```

---

## Códigos Especiais (Windows)

### -1073741510 (0xC000013A)
**Significado:** Processo terminado por Ctrl+C (KeyboardInterrupt).

**Causa:** Usuário cancelou execução manualmente ou timeout.

**Ação:** Nenhuma, comportamento esperado quando cancelando scripts longos.

---

## Troubleshooting

### Q: Exit code está sempre 1 mesmo quando deveria ser 2/3/4

**A:** Verificar se script está propagando exit codes corretamente:
```powershell
# ❌ ERRADO (achata todos para 1)
if ($exitCode -ne 0) { exit 1 }

# ✅ CORRETO (propaga código específico)
if ($exitCode -ne 0) { exit $exitCode }
```

### Q: `parity_report.json` mostra `table: null` e `column: null`

**A:** Isso era um bug crítico corrigido em 2026-02-10 (P0-A/P0-B).
Causa raiz: `Tee-Object` do PowerShell 5.1 escrevia o log Alembic em UTF-16LE,
causando truncamento no parser Python (`parity_classify.py`).

**Se persistir:**
1. Verificar encoding do log: `[System.IO.File]::ReadAllBytes("parity-scan.log")[0..3]`
   - UTF-8 correto: `35 35 35` (### em ASCII)
   - UTF-16LE problemático: `FF FE` (BOM) ou bytes `00` intercalados
2. Confirmar que `parity_scan.ps1` usa `WriteAllText` (não `Tee-Object`)
3. Confirmar que `parity_classify.py` tem strip de NUL bytes em `read_log_lines()`

### Q: Exit code 4 mas nenhuma violation listada

**A:** 
1. Verificar se output foi truncado (redirecionar para arquivo)
2. Confirmar que schema.sql está atualizado: `pg_dump > docs/_generated/schema.sql`
3. Verificar se model path está correto no output

### Q: Múltiplos exit codes possíveis, qual prevalece?

**A:** Ordem de precedência no `models_autogen_gate.ps1`:
1. Exit 3 (guard) — verificado primeiro
2. Exit 2 (parity) — verificado depois
3. Exit 4 (requirements) — verificado por último
4. Exit 0 — se todos passaram

---

## Quick Reference Table

| Code | Nome | Origem | Significado | Ação Típica |
|------|------|--------|-------------|-------------|
| **0** | Success | Todos | Tudo OK | Nenhuma |
| **1** | Internal Error | Todos | Crash/Bug | Debug + Fix |
| **2** | Parity Diff | parity_gate.ps1 | DB ≠ Model | Migration OU Autogen |
| **3** | Guard Violation | agent_guard.py | Arquivo protegido modificado | -Allow OU Revert |
| **4** | Requirements | model_requirements.py | Model viola schema.sql | Fix model |
| **100** | SKIP_NO_MODEL | models_batch.ps1 | Tabela sem model Python | Criar model OU ignorar |

---

## Exit Code 100: SKIP_NO_MODEL

**Origem:** `models_batch.ps1` (modo scan)

**Significado:** Tabela existe no schema.sql mas não possui model Python correspondente.

**Causas comuns:**
- Tabela de sistema (ex: `alembic_version`)
- Tabela legada não migrada para ORM
- Tabela gerenciada externamente (views materializadas)
- Model planejado mas ainda não implementado

**Comportamento:**
- NÃO é considerado erro (batch continua)
- Tabela é registrada como SKIP no relatório
- Não conta como FAIL na contagem final

**Exemplo:**
```powershell
.\scripts\models_batch.ps1 -SkipRefresh -SkipGate
# Output:
# advantage_states: SKIP_NO_MODEL (exit=100)
# alembic_version: SKIP_NO_MODEL (exit=100)
# === SUMMARY ===
# PASS: 51, SKIP: 6, FAIL: 0
```

**Tabelas típicas com SKIP_NO_MODEL:**
- `alembic_version` (controle Alembic)
- `advantage_states` (enum table sem ORM)
- Views materializadas (`mv_*`)

**Resolução:**
- Se a tabela DEVE ter model: criar via autogen
- Se é tabela de sistema: ignorar (comportamento esperado)

---

## Exemplos de Debugging

### Cenário 1: Exit 2 (Parity)
```powershell
# 1. Identificar diferença
.\scripts\parity_gate.ps1 -Table "teams"
# Output: modify_type(teams, 'name', String(100) → String(200))

# 2. Verificar se mudança é intencional
# - Se SIM: criar migration
alembic revision --autogenerate -m "increase teams.name to 200 chars"
alembic upgrade head

# - Se NÃO: reverter model
git restore app/models/teams.py
```

### Cenário 2: Exit 4 (Requirements)
```powershell
# 1. Ver violations detalhadas
python scripts\model_requirements.py --table attendance --profile strict
# Output:
#   - TYPE_MISMATCH: date expected=date|None got=varchar|20 model_line=35

# 2. Corrigir model (linha 35)
# Antes: date: Mapped[str] = mapped_column(String(20))
# Depois: date: Mapped[datetime.date] = mapped_column(Date, nullable=False)

# 3. Revalidar
.\scripts\models_autogen_gate.ps1 -Table attendance
# Exit 0 ✅
```

### Cenário 3: Exit 3 (Guard)
```powershell
# 1. Identificar arquivo modificado
.\scripts\models_autogen_gate.ps1 -Table "seasons"
# Output: Modified: app/routes/seasons.py

# 2. Se modificação é legítima (ex: endpoint precisa ajuste)
.\scripts\models_autogen_gate.ps1 -Table "seasons" -Allow "app/routes/seasons.py"

# 3. OU revert se foi acidental
git restore app/routes/seasons.py
```

---

**Última atualização:** 2026-02-11  
**Responsável:** Tech Lead + AI Assistant  
**Referências:** ADR-MODELS-001, EXEC_TASK_ADR_MODELS_001.md
