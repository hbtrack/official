# AR_008 — Migration 0055: soft delete (COMP-DB-001) em 5 tabelas do domínio COMPETITIONS

**Status**: ✅ CONCLUIDO
**Versão do Protocolo**: 1.0.6

## Descrição
Criar arquivo Hb Track - Backend/db/alembic/versions/0055_comp_db_001_soft_delete_competition_tables.py com revision='0055', down_revision='0054'. A migration é DDL-only (sem backfill) e deve ser idempotente e reversível.

Upgrade (executar nesta ordem para cada tabela):

# competition_matches
op.add_column('competition_matches', sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True))
op.add_column('competition_matches', sa.Column('deleted_reason', sa.Text(), nullable=True))
op.create_check_constraint('ck_competition_matches_deleted_reason', 'competition_matches', "(deleted_at IS NULL AND deleted_reason IS NULL) OR (deleted_at IS NOT NULL AND deleted_reason IS NOT NULL)")
op.execute("CREATE TRIGGER trg_competition_matches_block_delete BEFORE DELETE ON competition_matches FOR EACH ROW EXECUTE FUNCTION public.trg_block_physical_delete()")

# competition_opponent_teams
op.add_column('competition_opponent_teams', sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True))
op.add_column('competition_opponent_teams', sa.Column('deleted_reason', sa.Text(), nullable=True))
op.create_check_constraint('ck_competition_opponent_teams_deleted_reason', 'competition_opponent_teams', "(deleted_at IS NULL AND deleted_reason IS NULL) OR (deleted_at IS NOT NULL AND deleted_reason IS NOT NULL)")
op.execute("CREATE TRIGGER trg_competition_opponent_teams_block_delete BEFORE DELETE ON competition_opponent_teams FOR EACH ROW EXECUTE FUNCTION public.trg_block_physical_delete()")

# competition_phases
op.add_column('competition_phases', sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True))
op.add_column('competition_phases', sa.Column('deleted_reason', sa.Text(), nullable=True))
op.create_check_constraint('ck_competition_phases_deleted_reason', 'competition_phases', "(deleted_at IS NULL AND deleted_reason IS NULL) OR (deleted_at IS NOT NULL AND deleted_reason IS NOT NULL)")
op.execute("CREATE TRIGGER trg_competition_phases_block_delete BEFORE DELETE ON competition_phases FOR EACH ROW EXECUTE FUNCTION public.trg_block_physical_delete()")

# match_events
op.add_column('match_events', sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True))
op.add_column('match_events', sa.Column('deleted_reason', sa.Text(), nullable=True))
op.create_check_constraint('ck_match_events_deleted_reason', 'match_events', "(deleted_at IS NULL AND deleted_reason IS NULL) OR (deleted_at IS NOT NULL AND deleted_reason IS NOT NULL)")
op.execute("CREATE TRIGGER trg_match_events_block_delete BEFORE DELETE ON match_events FOR EACH ROW EXECUTE FUNCTION public.trg_block_physical_delete()")

# match_roster
op.add_column('match_roster', sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True))
op.add_column('match_roster', sa.Column('deleted_reason', sa.Text(), nullable=True))
op.create_check_constraint('ck_match_roster_deleted_reason', 'match_roster', "(deleted_at IS NULL AND deleted_reason IS NULL) OR (deleted_at IS NOT NULL AND deleted_reason IS NOT NULL)")
op.execute("CREATE TRIGGER trg_match_roster_block_delete BEFORE DELETE ON match_roster FOR EACH ROW EXECUTE FUNCTION public.trg_block_physical_delete()")

Downgrade (ordem inversa — triggers primeiro, depois constraints, depois colunas):

TABLES = ['match_roster', 'match_events', 'competition_phases', 'competition_opponent_teams', 'competition_matches']
for t in TABLES:
    op.execute(f'DROP TRIGGER IF EXISTS trg_{t}_block_delete ON {t}')
for t in TABLES:
    op.drop_constraint(f'ck_{t}_deleted_reason', t)
for t in TABLES:
    op.drop_column(t, 'deleted_reason')
    op.drop_column(t, 'deleted_at')

NAO modificar nenhum outro arquivo além do arquivo de migration acima.

## Critérios de Aceite
1) alembic upgrade head retorna exit code 0 sem erros. 2) SELECT column_name FROM information_schema.columns WHERE table_name='match_events' AND column_name IN ('deleted_at','deleted_reason') retorna 2 linhas. 3) SELECT column_name FROM information_schema.columns WHERE table_name='match_roster' AND column_name IN ('deleted_at','deleted_reason') retorna 2 linhas. 4) SELECT column_name FROM information_schema.columns WHERE table_name='competition_matches' AND column_name IN ('deleted_at','deleted_reason') retorna 2 linhas. 5) SELECT column_name FROM information_schema.columns WHERE table_name='competition_opponent_teams' AND column_name IN ('deleted_at','deleted_reason') retorna 2 linhas. 6) SELECT column_name FROM information_schema.columns WHERE table_name='competition_phases' AND column_name IN ('deleted_at','deleted_reason') retorna 2 linhas. 7) SELECT trigger_name FROM information_schema.triggers WHERE trigger_name LIKE '%block_delete%' retorna pelo menos 5 novas linhas. 8) alembic downgrade -1 retorna exit code 0 (reversibilidade). 9) alembic upgrade head novamente retorna exit code 0 (idempotência do ciclo up/down/up). 10) Suite de testes existente não quebra (sem regressão).

## SSOT Touches
- [ ] docs/ssot/schema.sql
- [ ] docs/ssot/alembic_state.txt

## Validation Command (Contrato)
```
python -m pytest "Hb Track - Backend/tests/" -x --tb=short -q
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_008_comp_db_001_soft_delete_migration.log`

## Rollback Plan (Contrato)
```
alembic downgrade -1
# OU manualmente (executar nesta ordem exata):
# DROP TRIGGER IF EXISTS trg_match_roster_block_delete ON match_roster;
# DROP TRIGGER IF EXISTS trg_match_events_block_delete ON match_events;
# DROP TRIGGER IF EXISTS trg_competition_phases_block_delete ON competition_phases;
# DROP TRIGGER IF EXISTS trg_competition_opponent_teams_block_delete ON competition_opponent_teams;
# DROP TRIGGER IF EXISTS trg_competition_matches_block_delete ON competition_matches;
# ALTER TABLE match_roster DROP CONSTRAINT IF EXISTS ck_match_roster_deleted_reason;
# ALTER TABLE match_events DROP CONSTRAINT IF EXISTS ck_match_events_deleted_reason;
# ALTER TABLE competition_phases DROP CONSTRAINT IF EXISTS ck_competition_phases_deleted_reason;
# ALTER TABLE competition_opponent_teams DROP CONSTRAINT IF EXISTS ck_competition_opponent_teams_deleted_reason;
# ALTER TABLE competition_matches DROP CONSTRAINT IF EXISTS ck_competition_matches_deleted_reason;
# ALTER TABLE match_roster DROP COLUMN IF EXISTS deleted_reason, DROP COLUMN IF EXISTS deleted_at;
# ALTER TABLE match_events DROP COLUMN IF EXISTS deleted_reason, DROP COLUMN IF EXISTS deleted_at;
# ALTER TABLE competition_phases DROP COLUMN IF EXISTS deleted_reason, DROP COLUMN IF EXISTS deleted_at;
# ALTER TABLE competition_opponent_teams DROP COLUMN IF EXISTS deleted_reason, DROP COLUMN IF EXISTS deleted_at;
# ALTER TABLE competition_matches DROP COLUMN IF EXISTS deleted_reason, DROP COLUMN IF EXISTS deleted_at;
```
⚠️ **ATENÇÃO**: Este AR modifica banco. Execute rollback em caso de falha.

## Notas do Arquiteto
A migration deve incluir no docstring: 'COMP-DB-001: soft delete em 5 tabelas domínio competições/scout'. O trigger trg_block_physical_delete já existe como função no banco — NÃO recriar a função, apenas criar os triggers que a referenciam. competition_standings é explicitamente excluído desta migration.

## Riscos
- match_events.deleted_at=NULL por padrão em todos os registros existentes — queries que filtram 'WHERE deleted_at IS NULL' retornarão todos os eventos históricos, o que é correto. Documentar para os serviços existentes.
- O trigger trg_match_events_block_delete bloqueia DELETE físico em match_events — serviços que faziam DELETE direto precisarão ser adaptados para soft delete. Verificar match_event_service.py antes de executar.
- competition_opponent_teams: nome de trigger trg_competition_opponent_teams_block_delete é longo (>63 chars PostgreSQL limit). Verificar: len('trg_competition_opponent_teams_block_delete') = 42 chars — OK.

## Análise de Impacto
- Arquivos afetados: [Hb Track - Backend/db/alembic/versions/0055_comp_db_001_soft_delete_competition_tables.py, docs/hbtrack/ars/AR_008_migration_0055_soft_delete_comp-db-001_em_5_tabela.md]
- Mudança no Schema? [Sim]
- Risco de Regressão? [Médio]

---
## Carimbo de Execução
_(Gerado por hb report)_



### Execução em b2e7523
**Status Final**: ❌ FALHA
**Comando**: `python -m pytest "Hb Track - Backend/tests/" -x --tb=short -q`
**Exit Code**: 1
**Evidence File**: `docs/hbtrack/evidence/AR_008_comp_db_001_soft_delete_migration.log`
**Python Version**: 3.11.9

