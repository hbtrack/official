# AR_153 — DB: Attendance preconfirm + training_pending_items

**Status**: 🔲 PENDENTE
**Versão do Protocolo**: 1.3.0

## Descrição
Migração Alembic para estender attendance e criar pending_items:

1. ALTER TABLE attendance:
   - Atualizar ck_attendance_status para incluir 'preconfirm':
     CONSTRAINT ck_attendance_status CHECK (presence_status IN ('present','absent','justified','preconfirm'))
   Note: no PostgreSQL, ALTER TABLE ALTER CONSTRAINT não existe diretamente — DROP CONSTRAINT + ADD CONSTRAINT.

2. CREATE TABLE training_pending_items (
   id UUID DEFAULT gen_random_uuid() NOT NULL,
   training_session_id UUID NOT NULL REFERENCES training_sessions(id),
   athlete_id UUID NOT NULL REFERENCES users(id),
   item_type VARCHAR(50) NOT NULL CONSTRAINT ck_pending_item_type CHECK (item_type IN ('equipment','material','admin','other')),
   description TEXT NOT NULL,
   status VARCHAR(20) NOT NULL DEFAULT 'open' CONSTRAINT ck_pending_item_status CHECK (status IN ('open','resolved','cancelled')),
   created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
   updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
   resolved_at TIMESTAMP WITH TIME ZONE,
   resolved_by_user_id UUID REFERENCES users(id),
   PRIMARY KEY (id)
)

3. Gerar migração Alembic: alembic revision --autogenerate -m 'attendance_preconfirm_pending_items'
4. Atualizar SSOT via gen_docs_ssot.py

## Critérios de Aceite
1. attendance.presence_status aceita 'preconfirm' sem constraint violation. 2. attendance.presence_status rejeita valor inválido (ex: 'maybe') com ck_attendance_status. 3. training_pending_items table criada com ck_pending_item_type e ck_pending_item_status. 4. Alembic upgrade head sem erro.

## Write Scope
- Hb Track - Backend/alembic/versions/

## SSOT Touches
- [ ] docs/ssot/schema.sql
- [ ] docs/ssot/alembic_state.txt

## Validation Command (Contrato)
```
python -c "from pathlib import Path; base=Path('Hb Track - Backend/db/alembic/versions'); found=[f for f in base.glob('*.py') if 'training_pending_items' in f.read_text(encoding='utf-8')]; assert found, 'FAIL: nenhuma migration com training_pending_items encontrada em '+str(base); c=found[0].read_text(encoding='utf-8'); assert 'training_pending_items' in c, 'FAIL: CREATE TABLE training_pending_items ausente'; assert 'preconfirm' in c, 'FAIL: preconfirm ausente (attendance.presence_status)'; assert 'ck_pending_item_type' in c or 'ck_pending_item_status' in c, 'FAIL: constraints pending_item ausentes'; print('PASS AR_153: migration com pending_items+preconfirm+constraints OK em '+found[0].name)"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_153/executor_main.log`

## Rollback Plan (Contrato)
```
python scripts/run/hb_cli.py alembic -- downgrade -1
git checkout -- "Hb Track - Backend/docs/ssot/schema.sql"
git checkout -- "Hb Track - Backend/docs/ssot/alembic_state.txt"
```
⚠️ **ATENÇÃO**: Este AR modifica banco. Execute rollback em caso de falha.

## Notas do Arquiteto
Classe A (DB Constraint). DROP + ADD do check constraint para attendance.presence_status pode falhar se há dados existentes com valor novo antes da migração — safe: a constraint é só expandida (adicionando 'preconfirm'), não restringida. Backward compat garantida.

## Riscos
- ALTER CONSTRAINT para attendance.presence_status: se houver triggers ou views dependentes da constraint, rebuildá-los
- Dados existentes em attendance com presence_status='preconfirm' não devem existir antes da migration — verificar

## Análise de Impacto
_(A ser preenchido pelo Executor)_

---
## Carimbo de Execução
_(Gerado por hb report)_

