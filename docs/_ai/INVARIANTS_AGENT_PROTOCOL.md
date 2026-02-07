# Invariants Agent Protocol (Local-First)

Este documento estabelece o protocolo obrigatório para agents (humanos ou IA) ao trabalhar com invariantes do sistema HB Track.

## Propósito

Garantir que toda alteração em invariantes ou infraestrutura de testes seja validada localmente antes de commit, mantendo a consistência com os artefatos canônicos.

---

## Regra 0: SSOT (Single Source of Truth)

**Antes de validar qualquer invariante, garantir que os artefatos canônicos estão atualizados.**

### Checklist Executável (Forma Rápida)

```powershell
# Comando único que regenera todos os 3 artefatos canônicos e valida
cd "C:\HB TRACK"
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\inv.ps1 refresh
# Alias: powershell -NoProfile -ExecutionPolicy Bypass -File scripts\inv.ps1 ssot
```

### Checklist Executável (Forma Manual)

```powershell
# 1. Atualizar schema.sql (DDL + COMMENT ON COLUMN)
cd "C:\HB TRACK"
& "C:\HB TRACK\Hb Track - Backend\venv\Scripts\alembic.exe" upgrade head
python docs/scripts/dump_schema.py

# 2. Atualizar openapi.json
# (executar aplicação FastAPI e gerar via /openapi.json endpoint)
# Ou usar comando específico do projeto se existir

# 3. Verificar estado do Alembic (opcional)
& "C:\HB TRACK\Hb Track - Backend\venv\Scripts\alembic.exe" current
```

### Artefatos Canônicos

- **`docs/_generated/openapi.json`**: Contrato OpenAPI completo (gerado pelo FastAPI)
- **`docs/_generated/schema.sql`**: DDL completo + COMMENT ON COLUMN (gerado por dump_schema.py)
- **`docs/_generated/alembic_state.txt`**: Estado atual das migrações (opcional)

### Quando Aplicar

- Após alterar modelos SQLAlchemy
- Após criar/modificar routers FastAPI
- Após executar migrações Alembic
- Antes de criar/modificar testes de invariantes

---

## Regra 1: Loop Obrigatório por INV

**Para qualquer INV alterada ou criada, executar gate individual até EXIT_CODE=0.**

### Checklist Executável

```powershell
# 1. Executar gate individual
cd "C:\HB TRACK"
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/run_invariant_gate.ps1 INV-TRAIN-XXX

# 2. Verificar EXIT_CODE
# - EXIT_CODE=0  → PASS (pode prosseguir)
# - EXIT_CODE=1  → FAIL (corrigir erros de verifier ou pytest)
# - EXIT_CODE=3  → DRIFT ou GOLDEN_MISSING (revisar mudança e promover golden se VERIFY_EXIT=0 e PYTEST_EXIT=0)

# 3. Se EXIT_CODE != 0, corrigir e repetir passo 1

# 4. Só então permitir "DONE"
```

### Critérios de Sucesso

- ✅ `VERIFY_EXIT: 0` (sem violações de qualidade)
- ✅ `PYTEST_EXIT: 0` (testes passaram)
- ✅ `EXIT_CODE: 0` (sem drift de golden baseline)

### Exemplo de Output Válido

```
========================================
GATE VERDICT
========================================
Report:           C:\HB TRACK\docs\_generated\_reports\INV-TRAIN-015\20260203_060258
VERIFY_EXIT:      0
PYTEST_EXIT:      0
GOLDEN_DRIFT:     NO
EXIT_CODE:        0

RESULT: PASS
```

---

## Regra 2: Golden Baseline Promotion

**Golden baselines só são promovidos após validação rigorosa.**

### Checklist Executável

```powershell
# 1. Verificar condições para promoção
# - VERIFY_EXIT: 0
# - PYTEST_EXIT: 0
# - EXIT_CODE: 3 (drift detectado)

# 2. Revisar mudanças canônicas
# O gate imprime quais arquivos mudaram (INVARIANTS_TRAINING.md, verify_invariants_tests.py, etc)

# 3. Para promoção individual (após revisar)
cd "C:\HB TRACK"
# Copiar comando impresso pelo gate:
Remove-Item 'C:\HB TRACK\docs\_generated\_reports\INV-TRAIN-XXX\_golden_CLASS' -Recurse -Force
Copy-Item -Recurse 'C:\HB TRACK\docs\_generated\_reports\INV-TRAIN-XXX\TIMESTAMP' 'C:\HB TRACK\docs\_generated\_reports\INV-TRAIN-XXX\_golden_CLASS'

# 4. Para promoção bulk (após revisar lista completa)
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/run_invariant_gate_all.ps1 -WhatIf
# Revisar lista de comandos
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/run_invariant_gate_all.ps1 -Promote
# Verificar EXIT_ALL=0
```

### Critérios de Validação

- ✅ Drift é legítimo (mudança intencional em SPEC ou validador)
- ✅ Todos os testes passaram (VERIFY_EXIT=0, PYTEST_EXIT=0)
- ✅ Revisão manual da lista de INVs afetadas (no caso de bulk)

### Anti-Patterns (PROIBIDO)

- ❌ Promover golden com EXIT_CODE=1 (testes falhando)
- ❌ Promover golden sem revisar mudanças canônicas
- ❌ Usar `-Promote` sem primeiro rodar `-WhatIf` (em bulk)
- ❌ Rodar promote esperando bootstrap funcionar quando o discovery do gate_all ainda não inclui golden_missing: YES
- ❌ Promover se VERIFY_EXIT != 0 ou PYTEST_EXIT != 0

---

## Bootstrap do Golden (Primeira Vez)

**Para novos invariantes sem golden baseline existente.**

### Checklist Executável

```powershell
# 0. (Opcional, mas recomendado) Atualizar artefatos canônicos
cd "C:\HB TRACK"
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\inv.ps1 refresh

# 1. Rodar gate do INV
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\inv.ps1 gate INV-TRAIN-043

# 2. Verificar EXIT_CODE=3 e golden_missing: YES no meta.txt
# - VERIFY_EXIT: 0 (obrigatório)
# - PYTEST_EXIT: 0 (obrigatório)
# - EXIT_CODE: 3
# - golden_missing: YES

# 3. Promover baseline
# OPÇÃO A: Se gate_all já descobre golden_missing (recomendado):
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\inv.ps1 promote

# OPÇÃO B: Se gate_all ainda não descobre (promoção manual):
# Usar comando impresso pelo próprio gate:
# Copy-Item -Recurse '<report_dir>' '<inv_dir>\_golden_<PRIMARY_CLASS>' -Force

# 4. Rodar gate de novo e exigir EXIT_CODE=0
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\inv.ps1 gate INV-TRAIN-043

# 5. Validar no gate_all
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\inv.ps1 all
```

### ⚠️ Discovery Limitation (Importante)

**Pegadinha atual do `inv.ps1 promote`:**

O comando `inv.ps1 promote` executa `run_invariant_gate_all.ps1 -Promote`, que:
- Descobre invariantes procurando por diretórios `_golden_*` existentes
- **Invariantes novos (sem golden) não são descobertos automaticamente**
- Solução: usar promoção manual (comando do gate) ou ajustar o discovery

**Recomendação técnica**: O script `run_invariant_gate_all.ps1` foi atualizado para descobrir também INVs sem golden, lendo `meta.txt` do report mais recente e promovendo quando `exit_code=3` + `verify_exit=0` + `pytest_exit=0` + `golden_missing: YES`.

---

## Regra 3: Mudança de Infraestrutura

**Qualquer alteração em `verify_invariants_tests.py` ou `INVARIANTS_TRAINING.md` afeta múltiplos invariantes.**

### Checklist Executável

```powershell
# 0. (Opcional, mas recomendado) Regenerar artefatos canônicos antes de qualquer promoção
cd "C:\HB TRACK"
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/inv.ps1 refresh
# ou: powershell -NoProfile -ExecutionPolicy Bypass -File scripts/inv.ps1 ssot

# 1. Após alterar verify_invariants_tests.py ou INVARIANTS_TRAINING.md
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/run_invariant_gate_all.ps1

# 2. Se EXIT_ALL=3 (drift detectado)
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/run_invariant_gate_all.ps1 -WhatIf
# Revisar lista completa de INVs afetadas

# 3. Promover goldens (se mudança é legítima)
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/run_invariant_gate_all.ps1 -Promote

# 4. Verificar EXIT_ALL=0
# O script re-executa automaticamente e exige EXIT_ALL=0 no final
```

### Exemplo de Output Válido

```
========================================
FINAL RESULT
========================================
EXIT_ALL:  0
RESULT:    ALL PASS (promotion successful)
```

### Quando Aplicar

- Após adicionar/modificar validadores de classe (A, B, C1, C2, D, E1, F)
- Após adicionar/modificar regras de DoD-0, Obrigação A/B
- Após criar novos invariantes no SPEC
- Após atualizar anchors (db.*, code.*, api.*)

---

## Regra 5: Helper Canônico para Testes DB

**Testes de invariantes DB runtime (classe A) devem usar helper canônico para asserts de violações Postgres.**

### Contexto

Testes DB que verificam violações de constraints (CHECK, UNIQUE, FK) historicamente acessavam atributos internos do driver:
- psycopg2 (sync): `orig.diag.constraint_name`
- asyncpg (async): `orig.__cause__.constraint_name`

Problema: acoplamento ao "shape" interno do erro, divergência entre drivers, manutenção duplicada.

### Solução: Helper Canônico

**Localização**: `Hb Track - Backend/tests/_helpers/pg_error.py`

```python
from tests._helpers.pg_error import assert_pg_constraint_violation
```

### Contrato (API pública)

```python
assert_pg_constraint_violation(
    exc_info,              # pytest.ExceptionInfo[IntegrityError]
    expected_sqlstate,     # str: "23514" (CHECK) ou "23505" (UNIQUE)
    expected_constraint    # str: nome da constraint
)
```

### Exemplo de Uso

**❌ Código antigo (acoplado ao driver)**:
```python
with pytest.raises(IntegrityError) as exc_info:
    await async_db.flush()

# psycopg2 (sync)
orig = exc_info.value.orig
assert orig.pgcode == "23514"
diag = orig.diag
assert diag.constraint_name == "ck_wellness_post_rpe"

# asyncpg (async) - diferente!
orig = exc_info.value.orig
assert orig.pgcode == "23514"
cause = orig.__cause__
assert cause.constraint_name == "ck_wellness_post_rpe"
```

**✅ Código novo (helper canônico)**:
```python
with pytest.raises(IntegrityError) as exc_info:
    await async_db.flush()

# Driver-agnostic (funciona com ambos)
assert_pg_constraint_violation(
    exc_info, "23514", "ck_wellness_post_rpe"
)
```

### Estratégia de Extração (ordem de tentativa)

O helper tenta, em ordem:

1. `exc.value.orig.pgcode` → SQLSTATE (comum em ambos drivers)
2. `orig.diag.constraint_name` → psycopg2 (sync)
3. `orig.__cause__.constraint_name` → asyncpg (async)

### Migração de Testes Existentes

**Checklist para localizar candidatos**:

```powershell
cd "C:\HB TRACK\Hb Track - Backend"
Select-String -Path "tests\training\invariants\*.py" -Pattern "IntegrityError|orig\.diag|__cause__|pgcode|constraint_name" -List
```

**Processo de migração (1 arquivo por vez)**:

1. Adicionar import:
   ```python
   from tests._helpers.pg_error import assert_pg_constraint_violation
   ```

2. Substituir bloco manual (4-5 linhas) por chamada ao helper:
   ```python
   # ANTES:
   orig = exc_info.value.orig
   assert orig.pgcode == "23514"
   diag = orig.diag  # ou: cause = orig.__cause__
   assert diag.constraint_name == "constraint_name"
   
   # DEPOIS:
   assert_pg_constraint_violation(exc_info, "23514", "constraint_name")
   ```

3. Rodar gate individual:
   ```powershell
   pwsh scripts/inv.ps1 gate INV-TRAIN-XXX
   ```

4. Se `EXIT_CODE=3` (drift no test_file hash):
   - Validar que mudança é intencional
   - Promover golden baseline

5. Re-executar gate para confirmar `EXIT_CODE=0`

### Arquivos Migrados (Status Atual)

| Arquivo | Status | Test Methods |
|---------|--------|--------------|
| test_inv_train_001_focus_sum_constraint.py | ✅ Migrado | 2 |
| test_inv_train_032_wellness_post_rpe.py | ✅ Migrado | 2 |
| test_inv_train_043_microcycle_dates_check.py | ✅ Migrado | 2 |
| test_inv_train_044_analytics_cache_unique.py | ✅ Migrado | 2 |

**Candidatos pendentes**:
- test_inv_train_008_soft_delete_reason_pair.py
- test_inv_train_009_wellness_pre_uniqueness.py
- test_inv_train_010_wellness_post_uniqueness.py
- test_inv_train_030_attendance_correction_fields.py
- test_inv_train_033_wellness_pre_sleep_hours.py
- test_inv_train_034_wellness_pre_sleep_quality.py
- test_inv_train_035_session_templates_unique_name.py
- test_inv_train_036_wellness_rankings_unique.py
- test_inv_train_037_cycle_dates.py
- (e seus testes runtime equivalentes)

### Benefícios

- ✅ Driver-agnostic (psycopg2 + asyncpg)
- ✅ Reduz 5 linhas → 1 chamada
- ✅ Elimina acesso direto a atributos internos
- ✅ Centraliza lógica de extração
- ✅ Facilita evolução futura (adicionar fallback de mensagem, logging, etc)

### Regras de Enforcement

**PROIBIDO** em testes de invariantes:
- ❌ Acessar `orig.diag.constraint_name` diretamente
- ❌ Acessar `orig.__cause__.constraint_name` diretamente
- ❌ Parse manual de mensagens de erro para extrair constraint_name

**OBRIGATÓRIO**:
- ✅ Usar `assert_pg_constraint_violation()` para todas as verificações de constraints DB

### Validação no Verifier (Futuro)

Após migração completa, atualizar `verify_invariants_tests.py`:
- Adicionar rule "warning" (depois "error") detectando `orig.diag` ou `__cause__.constraint_name` em testes de invariantes
- Exceção: helper `pg_error.py` pode continuar acessando (é a única abstração permitida)

---

## Regra 4: Evidência no Output

**O agent deve sempre colar evidência completa no relatório final.**

### Checklist de Evidência

Para **alteração de 1 invariante** (Regra 1):
```
========================================
GATE VERDICT
========================================
Report:           <path>
VERIFY_EXIT:      0
PYTEST_EXIT:      0
GOLDEN_DRIFT:     NO
EXIT_CODE:        0

RESULT: PASS
```

Para **alteração de infraestrutura** (Regra 3):
```
========================================
GATE ALL SUMMARY
========================================

INV_ID              EXIT_CODE   RESULT
--------------------------------------------------
INV-TRAIN-002       0           PASS
INV-TRAIN-003       0           PASS
...

----------------------------------------
Total:  6
PASS:   6
DRIFT:  0
FAIL:   0

========================================
AGGREGATED RESULT
========================================
EXIT_CODE:  0
RESULT:     ALL PASS

EXIT_ALL=0
```

### Anti-Patterns (PROIBIDO)

- ❌ Reportar "testes passaram" sem colar output do gate
- ❌ Omitir EXIT_CODE ou EXIT_ALL
- ❌ Colar apenas parte do output (sem GATE VERDICT ou SUMMARY)

---

## Regra 5: UNIQUE INDEX Parcial (Soft Delete)

**Quando a evidência é CREATE UNIQUE INDEX idx_* ... WHERE deleted_at IS NULL, tratar como Classe A e citar o idx_* + a cláusula WHERE.**

### Contexto

Indexes únicos parciais implementam constraints de unicidade que respeitam soft-delete:
- Apenas registros não deletados (WHERE deleted_at IS NULL) são considerados
- Nome do constraint é o nome do index (idx_*)
- SQLSTATE retornado: 23505 (UNIQUE_VIOLATION)

### Checklist de Implementação

```python
# 1. No docstring do teste, especificar índice + filtro
"""
Evidência: CREATE UNIQUE INDEX idx_teams_org_name_deleted 
           ON teams (organization_id, name) 
           WHERE deleted_at IS NULL
"""

# 2. No SPEC.md, citar constraint_name como idx_*
anchors:
  - file: docs/_generated/schema.sql
    line: "CREATE UNIQUE INDEX idx_teams_org_name_deleted"
    class: A

# 3. No teste, validar usando helper canônico
with pytest.raises(IntegrityError) as exc_info:
    # ação que viola constraint
    ...

# 4. Validar com assert_pg_constraint_violation
from tests._helpers.pg_error import assert_pg_constraint_violation
assert_pg_constraint_violation(
    exc_info,
    sqlstate="23505",
    constraint_name="idx_teams_org_name_deleted"
)
```

### Critérios de Validação

- ✅ Docstring menciona idx_* + cláusula WHERE
- ✅ SPEC anchor cita linha CREATE UNIQUE INDEX
- ✅ Teste valida com helper pg_error (SQLSTATE 23505)
- ✅ Verifier aceita idx_* como constraint_name válido

---

## Comandos Quick Reference

### Validação Individual
```powershell
# Executar gate para 1 invariante
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/run_invariant_gate.ps1 INV-TRAIN-XXX

# Wrapper (equivalente)
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/inv.ps1 gate INV-TRAIN-XXX
```

### Validação Bulk
```powershell
# Executar gate para todos os invariantes com golden
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/run_invariant_gate_all.ps1

# Wrapper (equivalente)
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/inv.ps1 all
```

### Promoção de Goldens
```powershell
# Dry-run (listar comandos)
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/run_invariant_gate_all.ps1 -WhatIf

# Wrapper (equivalente)
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/inv.ps1 drift

# Executar promoção
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/run_invariant_gate_all.ps1 -Promote

# Wrapper (equivalente)
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/inv.ps1 promote
```

---

## Exit Codes Semânticos

| Exit Code | Significado | Ação Required |
|-----------|-------------|---------------|
| **0** | PASS | Nenhuma (pode prosseguir) |
| **1** | FAIL | Corrigir erros (verifier ou pytest) |
| **3** | DRIFT | Promover golden (se mudança legítima) |

---

## Fluxo de Trabalho Típico

### Cenário 1: Criar Novo Invariante

```powershell
# 1. Atualizar SSOT (se necessário)
python docs/scripts/dump_schema.py

# 2. Criar teste test_inv_train_XXX_*.py

# 3. Executar gate individual
pwsh scripts/inv.ps1 gate INV-TRAIN-XXX

# 4. Se EXIT_CODE=1, corrigir erros e repetir passo 3

# 5. Se EXIT_CODE=0, criar golden baseline
# (primeira execução não tem golden, então EXIT_CODE=0 significa "pronto para criar baseline")
Copy-Item -Recurse '<report_dir>' '<report_dir>/../_golden_<CLASS>'

# 6. Re-executar gate para confirmar
pwsh scripts/inv.ps1 gate INV-TRAIN-XXX
# Deve retornar EXIT_CODE=0
```

### Cenário 2: Modificar Validator (Infra)

```powershell
# 1. Modificar docs/scripts/verify_invariants_tests.py

# 2. Executar gate all
pwsh scripts/inv.ps1 all
# Espera EXIT_ALL=3 (drift em múltiplos INVs)

# 3. Revisar lista de INVs afetadas
pwsh scripts/inv.ps1 drift

# 4. Promover goldens
pwsh scripts/inv.ps1 promote
# Script re-executa e exige EXIT_ALL=0

# 5. Colar evidência (GATE ALL SUMMARY + EXIT_ALL=0)
```

### Cenário 3: Fix de Bug em Teste

```powershell
# 1. Modificar test_inv_train_XXX_*.py

# 2. Executar gate individual
pwsh scripts/inv.ps1 gate INV-TRAIN-XXX

# 3. Se EXIT_CODE=3 (drift devido a mudança no test_file hash)
# - Revisar que mudança é intencional
# - Promover golden individual (comando impresso pelo gate)

# 4. Re-executar gate para confirmar
pwsh scripts/inv.ps1 gate INV-TRAIN-XXX
# Deve retornar EXIT_CODE=0
```

---

## Integração com Git Hooks

O sistema suporta enforcement local via Git hooks versionados:

```powershell
# Ativar hooks (uma vez por clone)
git config core.hooksPath .githooks
```

O hook `.githooks/pre-commit` executa automaticamente:
```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/run_invariant_gate_all.ps1
```

Se `EXIT_ALL != 0`, o commit é bloqueado.

---

## Troubleshooting

### "Fatal error in launcher"
**Causa**: Python executable não encontrado ou launcher com problemas.  
**Solução**: Scripts usam resolução hardened de Python (venv primeiro, fallback para global).

### "GOLDEN_BASELINE_OUTDATED"
**Causa**: Golden foi criado antes da adição de canonical inputs tracking.  
**Solução**: Promover report recente para golden (comando impresso pelo gate).

### "EXIT_CODE=1" persistente
**Causa**: Erros reais de qualidade (DoD-0, Obrigação A/B, validadores de classe).  
**Solução**: 
1. Ler `verify_inv.txt` no report (violations filtradas)
2. Corrigir violações
3. Re-executar gate

### "EXIT_ALL=3" após mudança não-intencional
**Causa**: Mudança acidental em SPEC ou validator.  
**Solução**:
1. Reverter mudança acidental
2. Re-executar `pwsh scripts/inv.ps1 all`
3. Deve retornar `EXIT_ALL=0`

---

## Apêndice: Estrutura de Reports

```
docs/_generated/_reports/
└── INV-TRAIN-XXX/
    ├── _golden_<CLASS>/          # Golden baseline (hash reference)
    │   ├── hashes.txt
    │   ├── meta.txt
    │   ├── verify.txt
    │   ├── verify_inv.txt
    │   └── pytest.txt
    ├── 20260203_055939/          # Report timestamped
    │   ├── hashes.txt            # SHA256 dos canonical inputs
    │   ├── meta.txt              # Metadata (inv_id, exit_code, primary_class)
    │   ├── verify.txt            # Output completo do verifier
    │   ├── verify_inv.txt        # Violations filtradas (apenas deste INV)
    │   └── pytest.txt            # Output completo do pytest
    └── 20260203_060113/          # Outro report
        └── ...
```

---

## Glossary

- **SSOT**: Single Source of Truth (artefatos canônicos)
- **DoD-0**: Definition of Done nível 0 (nomenclatura básica)
- **Obrigação A**: Documentação de constraints de DB no docstring
- **Obrigação B**: Documentação de error handling (SQLSTATE, constraint_name, operationId)
- **Golden Baseline**: Snapshot de referência para drift detection
- **Canonical Inputs**: Arquivos rastreados para drift (openapi.json, schema.sql, INVARIANTS_TRAINING.md, verify_invariants_tests.py, test_file)
- **Primary Class**: Classe principal do invariante (A, B, C1, C2, D, E1, F)

---

**Versão**: 1.0  
**Data**: 2026-02-03  
**Última Atualização**: Implementação de gate_all com -Promote/-WhatIf
