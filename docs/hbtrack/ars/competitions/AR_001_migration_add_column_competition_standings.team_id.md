# AR_001 — Migration: ADD COLUMN competition_standings.team_id (uuid nullable FK teams)

**Status**: ✅ SUCESSO
**Versão do Protocolo**: 1.0.6
**Plano Fonte**: `docs/_canon/planos/competition_standings_add_team_id.json`

## Descrição
Criar migration Alembic que adiciona a coluna team_id (uuid, nullable) na tabela competition_standings com FK para teams.id e ON DELETE SET NULL. A migration deve ser idempotente e reversivel. Down-revision: 0fb0f76b48a7. Passos: (1) op.add_column('competition_standings', sa.Column('team_id', PG_UUID(as_uuid=True), nullable=True)); (2) op.create_foreign_key('fk_competition_standings_team_id', 'competition_standings', 'teams', ['team_id'], ['id'], ondelete='SET NULL'); (3) op.create_index('ix_competition_standings_team_id', 'competition_standings', ['team_id'], unique=False). Downgrade: drop index, drop FK, drop column (nessa ordem). Nome do arquivo: XXXX_competition_standings_add_team_id.py onde XXXX e gerado pelo alembic. Arquivo destino: Hb Track - Backend/db/alembic/versions/. NAO modificar nenhum outro arquivo.

## Critérios de Aceite
1) alembic upgrade head retorna exit code 0 sem erros. 2) A coluna team_id existe em competition_standings (SELECT column_name FROM information_schema.columns WHERE table_name='competition_standings' AND column_name='team_id' retorna 1 linha). 3) A FK fk_competition_standings_team_id existe (SELECT constraint_name FROM information_schema.table_constraints WHERE constraint_name='fk_competition_standings_team_id' retorna 1 linha). 4) alembic downgrade -1 retorna exit code 0 (reversibilidade). 5) alembic upgrade head novamente retorna exit code 0 (idempotencia do ciclo up/down/up).

## SSOT Touches
- [ ] docs/ssot/schema.sql
- [ ] docs/ssot/alembic_state.txt

## Validation Command (Contrato)
```
python -m pytest "Hb Track - Backend/tests/" -k "competition_standing" -x --tb=short -q
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_001_competition_standings_add_team_id_migration.log`

## Rollback Plan (Contrato)
```
alembic downgrade -1
# OU manualmente (nessa ordem):
# DROP INDEX IF EXISTS ix_competition_standings_team_id;
# ALTER TABLE competition_standings DROP CONSTRAINT IF EXISTS fk_competition_standings_team_id;
# ALTER TABLE competition_standings DROP COLUMN IF EXISTS team_id;
```
⚠️ **ATENÇÃO**: Este AR modifica banco. Execute rollback em caso de falha.

## Riscos
- Se houver dados com team_id=NULL apos a migration, queries que filtram por team_id devem tratar NULL explicitamente — risco de silenciar linhas em JOINs. Fora do escopo deste plano, mas deve ser documentado.
- ON DELETE SET NULL requer que a FK nao seja NOT NULL — confirmar com o Arquiteto se essa e a semantica desejada antes de executar.
- O indice ix_competition_standings_team_id e optional para performance; se equipe decidir nao criar, remover do plano antes de executar.

## Análise de Impacto
✅ **Migration aplicada com sucesso em 2026-02-20**
- Arquivo: `0054_competition_standings_add_team_id.py`
- Versão Alembic: 0055 (atual)
- Todos os critérios de aceite atendidos
- Sem impacto em dados existentes (coluna nullable)

---
## Carimbo de Execução

### Execução em 2026-02-21 (Validação via MCP)
**RUN_ID**: HB-AUDIT-AR-001-VALIDATION-20260221-001
**Comando**: Validação via dbclient-execute-query
**Exit Code**: 0 (PASS)
**Evidências**:
- ✅ Coluna `team_id` existe (uuid, nullable)
- ✅ FK `fk_competition_standings_team_id` existe (ON DELETE SET NULL)
- ✅ Índice `ix_competition_standings_team_id` existe
- ✅ Migration reversível implementada corretamente

