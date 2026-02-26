# AR_149 — DB: training_sessions.standalone — cycle hierarchy schema

**Status**: 🔲 PENDENTE
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
cd "Hb Track - Backend" && python -m alembic upgrade head 2>&1 | Select-String -Pattern 'Running|ERROR|FAILED'; python -c "from app.db.session import engine; import sqlalchemy as sa; insp=sa.inspect(engine); cols=[c['name'] for c in insp.get_columns('training_sessions')]; assert 'standalone' in cols, 'standalone missing'; print('standalone column OK')" 2>&1
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

## Análise de Impacto
_(A ser preenchido pelo Executor)_

---
## Carimbo de Execução
_(Gerado por hb report)_

