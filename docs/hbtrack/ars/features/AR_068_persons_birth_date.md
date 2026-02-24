# AR_068 — Migration: persons.birth_date NOT NULL + Trigger de Paridade com athletes

**Status**: 🔲 PENDENTE
**Versão**: 1.1
**Criado em**: 2026-02-19
**Plano de Execução**: `docs/_canon/planos/AR_068_migration_persons_birth_date.json`
**Modo**: EXECUTE
**Autor**: Arquiteto  
**PRD Source**: docs/hbtrack/PRD HB Track.md §8.2 — Invariante de Dados

---

## Invariante de Negócio

> O campo birth_date é obrigatório para todas as pessoas classificadas como Atletas. O sistema deve garantir paridade entre persons.birth_date e athletes.birth_date.

---

## SSOT Bindings

- **Schema SSOT**: `docs/ssot/schema.sql`
- **Model Person**: `Hb Track - Backend/app/models/person.py`
- **Model Athlete**: `Hb Track - Backend/app/models/athlete.py`
- **Alembic Versions Dir**: `Hb Track - Backend/db/alembic/versions/`
- **Alembic Current Head**: `0fb0f76b48a7`

---

## Context

### Current State
- **persons.birth_date**: `date, nullable=True` — coluna PERMITE NULL no banco e no model SQLAlchemy
- **athletes.birth_date**: `date, NOT NULL` — já obrigatório desde migration 0005
- **Model Person Line**: `Hb Track - Backend/app/models/person.py:57` — `birth_date: Mapped[Optional[date]] = mapped_column(sa.Date(), nullable=True)`
- **Gap**: Atletas vinculados via `athletes.person_id → persons.id` podem ter `persons.birth_date = NULL`, violando o invariante do PRD

### Target State
- **persons.birth_date**: `date, NOT NULL` — obrigatório para todos os registros ativos
- **Parity Guarantee**: TRIGGER de banco garante `persons.birth_date == athletes.birth_date` em INSERT/UPDATE em ambas as tabelas
- **Model Person Line**: `Hb Track - Backend/app/models/person.py:57` — `birth_date: Mapped[date] = mapped_column(sa.Date(), nullable=False)`

---

## Pre-Flight Checks

### PF-001: Persons de atletas com birth_date NULL (backfillável automaticamente)
**SQL**:
```sql
SELECT p.id, p.full_name, p.birth_date AS persons_birth_date, 
       a.id AS athlete_id, a.birth_date AS athletes_birth_date
FROM athletes a
JOIN persons p ON a.person_id = p.id
WHERE p.birth_date IS NULL 
  AND a.deleted_at IS NULL 
  AND p.deleted_at IS NULL;
```
**Expected Result**: 0 linhas (ideal). Se > 0, executar MIG-002 (backfill automático).  
**Action if Non-Zero**: CONTINUAR — backfill via MIG-002  
**Blocker**: ❌ Não

---

### PF-002: Persons NÃO-atletas com birth_date NULL (NÃO backfillável automaticamente)
**SQL**:
```sql
SELECT p.id, p.full_name
FROM persons p
WHERE p.birth_date IS NULL 
  AND p.deleted_at IS NULL
  AND NOT EXISTS (
      SELECT 1 FROM athletes a 
      WHERE a.person_id = p.id 
        AND a.deleted_at IS NULL
  );
```
**Expected Result**: 0 linhas. Se > 0, a migration NÃO pode ser executada sem correção manual de dados.  
**Action if Non-Zero**: ⛔ BLOCKED — retornar BLOCKED_INPUT (4). Listar persons encontrados para o operador corrigir birth_date manualmente antes de reexecutar.  
**Blocker**: ✅ SIM

---

### PF-003: Divergência de birth_date entre persons e athletes (dados inconsistentes pré-existentes)
**SQL**:
```sql
SELECT p.id, p.full_name, 
       p.birth_date AS persons_bd, 
       a.birth_date AS athletes_bd
FROM athletes a
JOIN persons p ON a.person_id = p.id
WHERE p.birth_date IS NOT NULL 
  AND p.birth_date != a.birth_date
  AND a.deleted_at IS NULL 
  AND p.deleted_at IS NULL;
```
**Expected Result**: 0 linhas. Se > 0, indicar ao operador quais registros possuem divergência para resolver manualmente antes da migration.  
**Action if Non-Zero**: ⛔ BLOCKED — retornar BLOCKED_INPUT (4). Listar divergências para resolução manual.  
**Blocker**: ✅ SIM

---

## Migration Steps

### MIG-001: Pre-flight gate: abortar se PF-002 ou PF-003 retornarem linhas
**Type**: `data_check`  
**Alembic Pattern**: `op.get_bind() + conn.execute(text(...)).scalar()`  
**Exit Code on Fail**: 4  
**Description**: Executar PF-002 e PF-003 via conn.execute(). Se count > 0 em qualquer um, levantar RuntimeError com lista dos IDs bloqueadores. A migration NÃO deve continuar.

---

### MIG-002: Backfill: copiar athletes.birth_date → persons.birth_date onde NULL
**Type**: `data_migration`  
**SQL**:
```sql
UPDATE persons p
SET birth_date = a.birth_date,
    updated_at = now()
FROM athletes a
WHERE a.person_id = p.id
  AND p.birth_date IS NULL
  AND a.deleted_at IS NULL
  AND p.deleted_at IS NULL;
```
**Description**: Somente executa se PF-001 retornou linhas (count > 0). Idempotente — safe para executar mesmo se não há linhas.

---

### MIG-003: Verificação pós-backfill: confirmar 0 nulls restantes para atletas
**Type**: `data_check`  
**SQL**:
```sql
SELECT COUNT(*)
FROM persons p
JOIN athletes a ON a.person_id = p.id
WHERE p.birth_date IS NULL 
  AND a.deleted_at IS NULL;
```
**Expected Count**: 0  
**Exit Code on Fail**: 2  
**Description**: Deve retornar 0. Se não, o backfill falhou parcialmente e a migration deve abortar com FAIL_ACTIONABLE (2).

---

### MIG-004: DDL: ALTER TABLE persons ALTER COLUMN birth_date SET NOT NULL
**Type**: `ddl_alter_column`  
**Alembic Op**: `op.alter_column('persons', 'birth_date', existing_type=sa.Date(), nullable=False)`  
**Description**: Aplica a constraint NOT NULL na coluna. Só pode executar após MIG-001 a MIG-003 confirmarem 0 nulls.

---

### MIG-005: DDL: Criar função fn_sync_birth_date_athletes_to_persons (athletes → persons)
**Type**: `ddl_trigger_function`  
**SQL**:
```sql
CREATE OR REPLACE FUNCTION fn_sync_birth_date_athletes_to_persons()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.birth_date IS DISTINCT FROM OLD.birth_date THEN
        UPDATE persons
        SET birth_date = NEW.birth_date,
            updated_at = now()
        WHERE id = NEW.person_id 
          AND deleted_at IS NULL;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```
**Description**: Função de trigger: quando athletes.birth_date é atualizado, propaga para persons.birth_date.

---

### MIG-006: DDL: Criar trigger trg_sync_birth_date_athletes (AFTER UPDATE OF birth_date ON athletes)
**Type**: `ddl_trigger`  
**SQL**:
```sql
CREATE TRIGGER trg_sync_birth_date_athletes
AFTER UPDATE OF birth_date ON athletes
FOR EACH ROW
EXECUTE FUNCTION fn_sync_birth_date_athletes_to_persons();
```
**Description**: Dispara MIG-005 após qualquer UPDATE em athletes.birth_date.

---

### MIG-007: DDL: Criar função fn_validate_birth_date_parity_on_person (persons → athletes validação)
**Type**: `ddl_trigger_function`  
**SQL**:
```sql
CREATE OR REPLACE FUNCTION fn_validate_birth_date_parity_on_person()
RETURNS TRIGGER AS $$
DECLARE
    v_athlete_birth_date date;
BEGIN
    SELECT a.birth_date INTO v_athlete_birth_date
    FROM athletes a
    WHERE a.person_id = NEW.id 
      AND a.deleted_at IS NULL
    ORDER BY a.created_at DESC
    LIMIT 1;
    
    IF v_athlete_birth_date IS NOT NULL
       AND NEW.birth_date IS DISTINCT FROM v_athlete_birth_date THEN
        RAISE EXCEPTION
            'INV-PARITY-001: persons.birth_date (%) deve ser igual a athletes.birth_date (%) para person_id=%',
            NEW.birth_date, v_athlete_birth_date, NEW.id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```
**Description**: Função de trigger: quando persons.birth_date é atualizado, valida que não diverge de athletes.birth_date. Levanta exception com código INV-PARITY-001 se divergir.

---

### MIG-008: DDL: Criar trigger trg_validate_birth_date_persons (BEFORE UPDATE OF birth_date ON persons)
**Type**: `ddl_trigger`  
**SQL**:
```sql
CREATE TRIGGER trg_validate_birth_date_persons
BEFORE UPDATE OF birth_date ON persons
FOR EACH ROW
EXECUTE FUNCTION fn_validate_birth_date_parity_on_person();
```
**Description**: Dispara MIG-007 antes de qualquer UPDATE em persons.birth_date, bloqueando divergências.

---

## Alembic Migration

### Metadata
- **Filename Pattern**: `XXXX_persons_birth_date_not_null_parity.py`
- **Down Revision**: `0fb0f76b48a7`
- **Revision**: `<alembic_autogenerate>`

### Upgrade Body
```python
import sqlalchemy as sa
from alembic import op

def upgrade():
    conn = op.get_bind()

    # MIG-001: PF-002 — non-athlete persons com birth_date NULL
    result = conn.execute(sa.text("""
        SELECT COUNT(*) FROM persons p
        WHERE p.birth_date IS NULL AND p.deleted_at IS NULL
          AND NOT EXISTS (
              SELECT 1 FROM athletes a WHERE a.person_id = p.id AND a.deleted_at IS NULL
          )
    """)).scalar()
    if result > 0:
        rows = conn.execute(sa.text("""
            SELECT id, full_name FROM persons p
            WHERE p.birth_date IS NULL AND p.deleted_at IS NULL
              AND NOT EXISTS (SELECT 1 FROM athletes a WHERE a.person_id = p.id AND a.deleted_at IS NULL)
        """)).fetchall()
        raise RuntimeError(
            f'MIGRATION BLOCKED (PF-002): {result} non-athlete person(s) with NULL birth_date. '
            f'Correct manually before running: {[(str(r.id), r.full_name) for r in rows]}'
        )

    # MIG-001: PF-003 — divergência person vs athlete birth_date
    result = conn.execute(sa.text("""
        SELECT COUNT(*) FROM athletes a
        JOIN persons p ON a.person_id = p.id
        WHERE p.birth_date IS NOT NULL AND p.birth_date != a.birth_date
          AND a.deleted_at IS NULL AND p.deleted_at IS NULL
    """)).scalar()
    if result > 0:
        rows = conn.execute(sa.text("""
            SELECT p.id, p.full_name, p.birth_date AS persons_bd, a.birth_date AS athletes_bd
            FROM athletes a JOIN persons p ON a.person_id = p.id
            WHERE p.birth_date IS NOT NULL AND p.birth_date != a.birth_date
              AND a.deleted_at IS NULL AND p.deleted_at IS NULL
        """)).fetchall()
        raise RuntimeError(
            f'MIGRATION BLOCKED (PF-003): {result} person(s) with birth_date divergence. '
            f'Resolve manually: {[(str(r.id), r.full_name, str(r.persons_bd), str(r.athletes_bd)) for r in rows]}'
        )

    # MIG-002: Backfill persons.birth_date from athletes.birth_date
    op.execute(sa.text("""
        UPDATE persons p
        SET birth_date = a.birth_date,
            updated_at = now()
        FROM athletes a
        WHERE a.person_id = p.id
          AND p.birth_date IS NULL
          AND a.deleted_at IS NULL
          AND p.deleted_at IS NULL
    """))

    # MIG-003: Verificar backfill — deve retornar 0
    remaining = conn.execute(sa.text("""
        SELECT COUNT(*) FROM persons p
        JOIN athletes a ON a.person_id = p.id
        WHERE p.birth_date IS NULL AND a.deleted_at IS NULL
    """)).scalar()
    if remaining > 0:
        raise RuntimeError(
            f'BACKFILL INCOMPLETE (MIG-003): {remaining} athlete person(s) still have NULL birth_date.'
        )

    # MIG-004: ALTER COLUMN — NOT NULL
    op.alter_column('persons', 'birth_date', existing_type=sa.Date(), nullable=False)

    # MIG-005: Função fn_sync_birth_date_athletes_to_persons
    op.execute(sa.text("""
        CREATE OR REPLACE FUNCTION fn_sync_birth_date_athletes_to_persons()
        RETURNS TRIGGER AS $$
        BEGIN
            IF NEW.birth_date IS DISTINCT FROM OLD.birth_date THEN
                UPDATE persons
                SET birth_date = NEW.birth_date,
                    updated_at = now()
                WHERE id = NEW.person_id AND deleted_at IS NULL;
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """))

    # MIG-006: Trigger athletes → persons sync
    op.execute(sa.text("""
        CREATE TRIGGER trg_sync_birth_date_athletes
        AFTER UPDATE OF birth_date ON athletes
        FOR EACH ROW
        EXECUTE FUNCTION fn_sync_birth_date_athletes_to_persons();
    """))

    # MIG-007: Função fn_validate_birth_date_parity_on_person
    op.execute(sa.text("""
        CREATE OR REPLACE FUNCTION fn_validate_birth_date_parity_on_person()
        RETURNS TRIGGER AS $$
        DECLARE
            v_athlete_birth_date date;
        BEGIN
            SELECT a.birth_date INTO v_athlete_birth_date
            FROM athletes a
            WHERE a.person_id = NEW.id AND a.deleted_at IS NULL
            ORDER BY a.created_at DESC
            LIMIT 1;
            IF v_athlete_birth_date IS NOT NULL
               AND NEW.birth_date IS DISTINCT FROM v_athlete_birth_date THEN
                RAISE EXCEPTION
                    'INV-PARITY-001: persons.birth_date (%) deve ser igual a athletes.birth_date (%) para person_id=%',
                    NEW.birth_date, v_athlete_birth_date, NEW.id;
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """))

    # MIG-008: Trigger persons → athletes validation
    op.execute(sa.text("""
        CREATE TRIGGER trg_validate_birth_date_persons
        BEFORE UPDATE OF birth_date ON persons
        FOR EACH ROW
        EXECUTE FUNCTION fn_validate_birth_date_parity_on_person();
    """))
```

### Downgrade Body
```python
def downgrade():
    op.execute(sa.text('DROP TRIGGER IF EXISTS trg_validate_birth_date_persons ON persons;'))
    op.execute(sa.text('DROP FUNCTION IF EXISTS fn_validate_birth_date_parity_on_person();'))
    op.execute(sa.text('DROP TRIGGER IF EXISTS trg_sync_birth_date_athletes ON athletes;'))
    op.execute(sa.text('DROP FUNCTION IF EXISTS fn_sync_birth_date_athletes_to_persons();'))
    op.alter_column('persons', 'birth_date', existing_type=sa.Date(), nullable=True)
```

---

## Model Changes

### File: `Hb Track - Backend/app/models/person.py`
**Line**: ~57

**OLD**:
```python
birth_date: Mapped[Optional[date]] = mapped_column(sa.Date(), nullable=True)
```

**NEW**:
```python
birth_date: Mapped[date] = mapped_column(sa.Date(), nullable=False)
```

**Import Change**: Remove `Optional` de `Mapped[Optional[date]]` se não usado por outros campos. Verificar imports no topo do arquivo.

---

## Success Criteria

- [ ] PF-002 retorna 0 linhas antes e depois da migration
- [ ] PF-003 retorna 0 linhas antes e depois da migration
- [ ] ALTER COLUMN persons.birth_date SET NOT NULL aplicado com sucesso (verificar via `\d persons` no psql)
- [ ] Trigger `trg_sync_birth_date_athletes` existe em `information_schema.triggers`
- [ ] Trigger `trg_validate_birth_date_persons` existe em `information_schema.triggers`
- [ ] `UPDATE athletes SET birth_date='2000-01-01' WHERE ...` propaga para `persons.birth_date`
- [ ] `UPDATE persons SET birth_date='1999-12-31' WHERE id=(atleta)` levanta exception INV-PARITY-001
- [ ] Model `Person.birth_date` typado como `Mapped[date]` (não Optional)
- [ ] `alembic upgrade head` retorna exit code 0
- [ ] `alembic downgrade -1` retorna exit code 0 (reversibilidade verificada)

---

## Evidence File (Contrato)

`docs/evidence/AR_068_persons_birth_date_not_null.log`

---

## Rollback Plan

### Alembic
```bash
alembic downgrade -1
```

**Effect**: Restaura persons.birth_date para nullable=True. Remove os dois triggers e as duas funções. NÃO reverte o backfill de dados (persons que tiveram birth_date preenchida mantenha o valor — não há perda de informação).

### Model Revert
```bash
git restore 'Hb Track - Backend/app/models/person.py'
```
Reverter para `Mapped[Optional[date]] + nullable=True`

---

## Required Gates

⚠️ Verificar existência de gates no `_INDEX.yaml` antes de executar — o Executor NÃO deve criar gates novos.

**Candidatos esperados** (verificar IDs reais no repo):
- Gate de models vs schema (structural sync)
- Gate de alembic head (db_at_head)

---

## Risk Assessment

### Data Loss
**Nível**: NENHUM  
**Justificativa**: Backfill só adiciona dados, não remove.

### Downtime
**Nível**: MÍNIMO  
**Justificativa**: ALTER COLUMN NOT NULL requer lock breve em tabela persons; executar em janela de baixo tráfego.

### Regression
**Nível**: MÉDIO  
**Justificativa**: Código que cria Person sem birth_date irá falhar após a migration; auditar endpoints de criação de Person.

#### Endpoints to Audit
- `POST /persons` (se existir endpoint direto)
- `POST /users` (cria Person internamente)
- `POST /athletes` (cria Person + Athlete — já passa birth_date via athletes)

---

## Análise de Impacto

### Arquivos Alterados
| Arquivo | Tipo | Alteração |
|---------|------|-----------|
| `Hb Track - Backend/app/models/person.py` | Model | `birth_date`: `Mapped[Optional[date]]` → `Mapped[date]`, `nullable=True` → `nullable=False` |
| `Hb Track - Backend/db/alembic/versions/0053_persons_birth_date_not_null_parity.py` | Migration | Nova migration: backfill + ALTER NOT NULL + 2 triggers + 2 funções |

### Impacto em Serviços (Código que cria/atualiza Person)
| Serviço | Risco | Nota |
|---------|-------|------|
| `app/services/intake/ficha_unica_service.py` | MÉDIO | Fluxo principal de cadastro — já recebe `birth_date` via ficha do atleta |
| `app/services/intake/ficha_service.py` | MÉDIO | Idem acima — validar que `birth_date` é obrigatório no schema de entrada |
| `app/services/person_service.py` | ALTO | Criação direta de Person — MUST garantir `birth_date` não-null no payload |
| `app/services/unified_person_service.py` | MÉDIO | Criação/update unificado de Person — validar input |
| `app/services/athlete_service_v1_2.py` | BAIXO | Cria Person + Athlete juntos — `birth_date` já vem do athlete payload |
| `app/api/v1/routers/auth.py` | ALTO | Cria Person no signup — verificar se `birth_date` é passado |
| `app/core/athlete_validations.py` | BAIXO | Validações de atleta — apenas leitura |

### Impacto em Banco de Dados
- **DDL**: `ALTER TABLE persons ALTER COLUMN birth_date SET NOT NULL`
- **Triggers criados**: `trg_sync_birth_date_athletes` (AFTER UPDATE ON athletes), `trg_validate_birth_date_persons` (BEFORE UPDATE ON persons)
- **Funções criadas**: `fn_sync_birth_date_athletes_to_persons()`, `fn_validate_birth_date_parity_on_person()`
- **Lock**: Breve table-level lock em `persons` durante ALTER NOT NULL

### Reversibilidade
- `alembic downgrade -1` remove triggers, funções e reverte `nullable=True`
- Backfill de dados NÃO é revertido (sem perda de informação)
- Model revertido via `git restore`

---

## Carimbo de Execução
_(Gerado por hb report)_


## 🏁 Evidência de Execução (2026-02-20 06:53:26)
**Status Final:** ✅ SUCESSO
**Comando de Validação:** `alembic current`
**Exit Code:** 0

### 📋 Log Output:
```text
0053 (head)


[STDERR]
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.

```

---


## 🏁 Evidência de Execução (2026-02-20 06:54:04)
**Status Final:** ✅ SUCESSO
**Comando de Validação:** `alembic current`
**Exit Code:** 0

### 📋 Log Output:
```text
0053 (head)


[STDERR]
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.

```

---

### Execução em 9bebd2c
**Status Final**: ✅ SUCESSO
**Comando**: `alembic current`
**Exit Code**: 0
**Evidence File**: `docs/hbtrack/evidence/AR_003.5_evidence.log`
**Python Version**: 3.11.9


### Execução em 9bebd2c
**Status Final**: ✅ SUCESSO
**Comando**: `alembic current`
**Exit Code**: 0
**Evidence File**: `docs/hbtrack/evidence/AR_003.5_evidence.log`
**Python Version**: 3.11.9

