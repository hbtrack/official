# EXECUTOR BLOCKED — Migration 0060 + AR_024 Obsolete (2026-02-24)

## STATUS SUMMARY
- **ARs processadas**: 1/5 (AR_002.5_C ✅)
- **ARs bloqueadas**: 4/5 (AR_002.5_A/B/D + AR_024 ❌)
- **Executor status**: BLOCKED_INPUT (exit 4)

---

## BLOQUEADOR #1: PostgreSQL < 15 incompatível com migration 0060

### ARs afetadas
- AR_002.5_A (match_goalkeeper_stints)
- AR_002.5_B (attendance.justified)
- AR_002.5_D (match_analytics_cache)

### Validation commands (todas começam com)
```bash
alembic upgrade head && python -c "..."
```

### Erro ao executar
```
psycopg2.errors.SyntaxError: syntax error at or near "NULLS"
LINE 1: ...ADD CONSTRAINT ... UNIQUE NULLS NOT DISTINCT (...)
```

### Migration bloqueadora
- **Arquivo**: `Hb Track - Backend/db/alembic/versions/0060_comp_db_004_standings_unique_nulls_not_distinct.py`
- **SQL gerado**: `ALTER TABLE competition_standings ADD CONSTRAINT ... UNIQUE NULLS NOT DISTINCT (...)`
- **Requer**: PostgreSQL 15+
- **DB atual**: PostgreSQL < 15

### Migrations target (já existem, mas não podem ser aplicadas)
- ✅ 0057: add_match_goalkeeper_stints.py
- ✅ 0058: attendance_add_justified_status.py
- ✅ 0059: add_match_analytics_cache.py

### Opções de resolução

**1. Fix migration 0060** (retrocompatibilidade):
```python
# Em 0060_comp_db_004_standings_unique_nulls_not_distinct.py
from sqlalchemy import inspect

def upgrade():
    conn = op.get_bind()
    pg_version = conn.execute("SHOW server_version").scalar()
    major_version = int(pg_version.split('.')[0])
    
    if major_version >= 15:
        op.create_unique_constraint(
            'uq_competition_standings_comp_phase_opponent',
            'competition_standings',
            ['competition_id', 'phase_id', 'opponent_team_id'],
            nulls_not_distinct=True
        )
    else:
        # Fallback: partial unique index
        op.execute("""
            CREATE UNIQUE INDEX uq_competition_standings_comp_phase_opponent
            ON competition_standings(competition_id, phase_id, opponent_team_id)
            WHERE opponent_team_id IS NOT NULL
        """)
```

**2. Upgrade DB**: PostgreSQL 15+

**3. Skip migration 0060** temporariamente:
```bash
alembic downgrade 0059
# Aplicar ARs 002.5_A/B/D
# Resolver 0060 depois
```

**4. Validação alternativa** (sem alembic upgrade):
```bash
# Assumindo migrations já aplicadas manualmente
python -c "from sqlalchemy import inspect; from app.core.db import engine; ..."
```

**Recomendação**: Opção 1 (fix migration) ou Opção 4 (skip alembic upgrade).

---

## BLOQUEADOR #2: AR_024 validation obsoleta

### AR afetada
- AR_024 (Docs v1.1.0)

### Validation command espera
```python
assert 'v1.1.0' in df, 'FAIL Dev Flow v1.1.0'
assert 'TRIPLE_RUN_COUNT' in df, ...
```

### Estado real dos arquivos
- `Dev Flow.md`: **v1.2.0** (header) + **PROTOCOL_VERSION v1.3.0**
- `Hb cli Spec.md`: **v1.3.0**
- `Testador Contract.md`: Compatible with v1.1.0+

### Erro
```
AssertionError: FAIL Dev Flow v1.1.0
```

### Análise
- Arquivos **já contêm** `TRIPLE_RUN_COUNT`, `FLAKY_OUTPUT`, `E_TRIVIAL_CMD` (objetivo da AR_024)
- Versões são **superiores** à esperada (v1.2.0/v1.3.0 > v1.1.0)
- Análise de Impacto da AR_024: "já está materializado"

### Opções de resolução

**1. Atualizar validation** para v1.2.0+:
```python
assert re.search(r'v1\.[2-9]\.\d+', df), 'FAIL Dev Flow version'
```

**2. Marcar AR_024 como OBSOLETA**: Status → SKIPPED (superada por v1.2.0+)

**3. Noop validation** (objetivo já atingido):
```bash
python -c "print('PASS: AR_024 objective achieved in v1.2.0+'); exit(0)"
```

**Recomendação**: Opção 2 (OBSOLETA) ou Opção 3 (noop).

---

## EVIDENCES GERADAS

### ✅ AR_002.5_C (SUCESSO)
- **Evidence**: `docs/hbtrack/evidence/AR_002.5_C/executor_main.log`
- **Exit Code**: 0
- **Command**: `grep -E "escala 0-10|stress_level.*humor" docs/hbtrack/PRD\ HB\ TRACK.md`
- **Result**: PASS (matches found)
- **Staged**: ✅

### ❌ AR_002.5_A/B/D (BLOCKED)
- **Evidence files exist**: Sim (com Exit failures)
- **Root cause**: Migration 0060 SQL syntax error
- **Staged**: ❌ (bloqueador técnico)

### ❌ AR_024 (VALIDATION OBSOLETE)
- **Evidence**: `docs/hbtrack/evidence/AR_024/executor_main.log`
- **Exit Code**: 1
- **Error**: `AssertionError: FAIL Dev Flow v1.1.0`
- **Staged**: ❌ (validation mismatch)

---

## AÇÃO REQUERIDA

**Arquiteto ou DB Admin deve**:
1. Escolher resolução para bloqueador #1 (migration 0060)
2. Escolher resolução para bloqueador #2 (AR_024 obsolete)
3. Informar Executor qual estratégia adotar

**Executor permanece BLOCKED até decisão.**

---

**Timestamp**: 2026-02-24T15:40:00 UTC  
**Executor**: Cline v2.0 (Enterprise)  
**Protocol**: v1.3.0  
**Git HEAD**: 15ac28c (AR_002.5_C staged, 4 ARs blocked)
