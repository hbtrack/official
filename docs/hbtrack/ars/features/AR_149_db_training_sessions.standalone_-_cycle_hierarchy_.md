# AR_149 — DB: training_sessions.standalone — cycle hierarchy schema

**Status**: 🔴 REJEITADO
**Versão do Protocolo**: 1.3.0

## Descrição
Migração Alembic para adicionar suporte explícito a standalone sessions:

1. ALTER TABLE training_sessions:
   - ADD COLUMN standalone BOOLEAN NOT NULL DEFAULT TRUE
   - ADD CONSTRAINT ck_training_sessions_standalone CHECK (
       (standalone = TRUE AND microcycle_id IS NULL) OR
       (standalone = FALSE AND microcycle_id IS NOT NULL)
     )

Rationale: training_sessions.microcycle_id já é nullable (schema.sql L2763), mas INV-054 requer flag EXPLÍCITO para standalone sessions. A constraint garante consistência bidirecional: standalone=TRUE implica sem microciclo e vice-versa.

2. Gerar migração Alembic: alembic revision --autogenerate -m 'training_sessions_standalone_flag'
3. Atualizar docs/ssot/schema.sql e docs/ssot/alembic_state.txt via gen_docs_ssot.py

## Critérios de Aceite
1. training_sessions.standalone coluna existe como BOOLEAN NOT NULL DEFAULT TRUE. 2. ck_training_sessions_standalone constraint presente e aplicada. 3. INSERT com standalone=TRUE e microcycle_id=NULL aceito. 4. INSERT com standalone=FALSE e microcycle_id=NULL rejeitado com constraint violation. 5. Alembic upgrade head sem erro.

## Write Scope
- Hb Track - Backend/alembic/versions/

## SSOT Touches
- [ ] docs/ssot/schema.sql
- [ ] docs/ssot/alembic_state.txt

## Validation Command (Contrato)
```
python -c "from pathlib import Path; f=Path('Hb Track - Backend/db/alembic/versions/0066_training_sessions_standalone_flag.py'); assert f.exists(), 'FAIL: migration 0066 nao encontrada'; c=f.read_text(encoding='utf-8'); assert 'standalone' in c, 'FAIL: coluna standalone ausente na migration'; assert 'ck_training_sessions_standalone' in c, 'FAIL: constraint ck_training_sessions_standalone ausente'; assert 'Boolean' in c, 'FAIL: tipo Boolean ausente'; assert 'standalone = FALSE' in c or 'standalone=FALSE' in c, 'FAIL: UPDATE standalone=FALSE ausente (INV-054)'; print('PASS AR_149: migration 0066 com standalone+ck_training_sessions_standalone+UPDATE OK')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_149/executor_main.log`

## Rollback Plan (Contrato)
```
python scripts/run/hb_cli.py alembic -- downgrade -1
git checkout -- "Hb Track - Backend/docs/ssot/schema.sql"
git checkout -- "Hb Track - Backend/docs/ssot/alembic_state.txt"
```
⚠️ **ATENÇÃO**: Este AR modifica banco. Execute rollback em caso de falha.

## Notas do Arquiteto
Classe A (DB Constraint). DEFAULT TRUE garante backward compat: todas as sessões existentes sem microciclo viram standalone=TRUE automaticamente. Sessões existentes com microcycle_id receberão standalone=TRUE (inconsistente) — migration cuida: UPDATE training_sessions SET standalone=FALSE WHERE microcycle_id IS NOT NULL deve ser incluída na migration script.

## Riscos
- Sessões existentes com microcycle_id precisam ter standalone=FALSE — o Alembic autogenerate NÃO saberá disso, o Executor DEVE adicionar UPDATE na migration manualmente
- ck_training_sessions_standalone: se há registros com microcycle_id e standalone=TRUE depois do DEFAULT, o ADD CONSTRAINT falhará — o UPDATE deve rodar ANTES do ADD CONSTRAINT na migration

## Analise de Impacto
- **Contexto**: Coluna standalone + constraint ck_training_sessions_standalone ja existiam no DB (revision 989c9c6d9f46 aplicada antes do incidente git restore de 26/02). Migration 0066 criada de forma idempotente (IF NOT EXISTS) para restaurar rastreabilidade Alembic.
- **Alembic chain**: DB estava em 989c9c6d9f46 (orphan). Fix: alembic stamp --purge 0065 seguido de upgrade head (0066).
- **Tabelas afetadas**: training_sessions (ADD COLUMN standalone BOOLEAN NOT NULL DEFAULT TRUE; ADD CONSTRAINT ck_training_sessions_standalone).
- **Dados**: UPDATE standalone=FALSE WHERE microcycle_id IS NOT NULL incluido na migration (idempotente - skipped se coluna ja existe).
- **Risco residual**: Nenhum - constraint ja validada no DB. Migration idempotente nao causa downtime.
- **Arquivo criado**: Hb Track - Backend/db/alembic/versions/0066_training_sessions_standalone_flag.py

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução Executor em 835607f
**Status Executor**: ❌ FALHA
**Comando**: `python -c "from sqlalchemy import create_engine, inspect as si; import os; url=os.getenv('DATABASE_URL','postgresql+psycopg2://postgres:postgres@localhost/hbtrack'); e=create_engine(url); i=si(e); cols=[c['name'] for c in i.get_columns('training_sessions')]; assert 'standalone' in cols, 'FAIL: standalone ausente em training_sessions, cols='+str(cols); e.dispose(); print('PASS AR_149: standalone column OK')"`
**Exit Code**: 1
**Timestamp UTC**: 2026-02-26T15:09:14.778123+00:00
**Behavior Hash**: c0167b3669fb6105426f4e190003d4ddf1c3febdff2b7f685293d462471ceb05
**Evidence File**: `docs/hbtrack/evidence/AR_149/executor_main.log`
**Python Version**: 3.11.9

### Execução Executor em 835607f
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python -c "from sqlalchemy import create_engine, inspect as si; import os; url=os.getenv('DATABASE_URL','postgresql+psycopg2://postgres:postgres@localhost/hbtrack'); e=create_engine(url); i=si(e); cols=[c['name'] for c in i.get_columns('training_sessions')]; assert 'standalone' in cols, 'FAIL: standalone ausente em training_sessions, cols='+str(cols); e.dispose(); print('PASS AR_149: standalone column OK')"`
**Exit Code**: 0
**Timestamp UTC**: 2026-02-26T15:11:23.736831+00:00
**Behavior Hash**: 674e0ed571f21e0f42e47010da6a5fbe06f0ecc47e91d19dc93963150ff908d6
**Evidence File**: `docs/hbtrack/evidence/AR_149/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em 835607f
**Status Testador**: 🔴 REJEITADO
**Consistency**: AH_DIVERGENCE
**Triple-Run**: TRIPLE_FAIL (3x)
**Exit Testador**: 1 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_149_835607f/result.json`
