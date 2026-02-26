# AR_038 — Migration 0057: DROP uk_competition_standings_team_phase + CREATE UNIQUE NULLS NOT DISTINCT

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.1.0

## Descrição
Criar arquivo Hb Track - Backend/db/alembic/versions/0057_comp_db_004_standings_unique_nulls_not_distinct.py com revision='0057', down_revision='0056'.

Upgrade:
  # 1. Drop existing UNIQUE constraint (não é INDEX — é constraint)
  op.drop_constraint('uk_competition_standings_team_phase', 'competition_standings', type_='unique')

  # 2. Create new UNIQUE constraint with NULLS NOT DISTINCT
  op.create_unique_constraint(
      'uq_competition_standings_comp_phase_opponent',
      'competition_standings',
      ['competition_id', 'phase_id', 'opponent_team_id'],
      postgresql_nulls_not_distinct=True
  )

Downgrade:
  # Reverso exato
  op.drop_constraint('uq_competition_standings_comp_phase_opponent', 'competition_standings', type_='unique')
  op.create_unique_constraint(
      'uk_competition_standings_team_phase',
      'competition_standings',
      ['competition_id', 'phase_id', 'opponent_team_id']
  )

Docstring MUST incluir: 'COMP-DB-004: unique NULLS NOT DISTINCT em competition_standings(competition_id, phase_id, opponent_team_id)'.
NAO modificar nenhum outro arquivo.

## Critérios de Aceite
1) alembic upgrade head retorna exit_code=0. 2) uk_competition_standings_team_phase NÃO existe mais (SELECT constraint_name FROM information_schema.table_constraints WHERE constraint_name='uk_competition_standings_team_phase' retorna 0 linhas). 3) uq_competition_standings_comp_phase_opponent EXISTS (retorna 1 linha). 4) INSERT duplicado com phase_id=NULL levanta UniqueViolation (teste funcional: INSERT competition_standings com competition_id=X, phase_id=NULL, opponent_team_id=Y; segundo INSERT idêntico deve falhar com 23505). 5) alembic downgrade -1 retorna exit_code=0. 6) alembic upgrade head novamente retorna exit_code=0.

## SSOT Touches
- [ ] docs/ssot/schema.sql
- [ ] docs/ssot/alembic_state.txt

## Validation Command (Contrato)
```
python temp/ar038_validate.py
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_038/executor_main.log`

## Rollback Plan (Contrato)
```
alembic downgrade -1
# OU manualmente:
# ALTER TABLE competition_standings DROP CONSTRAINT IF EXISTS uq_competition_standings_comp_phase_opponent;
# ALTER TABLE competition_standings ADD CONSTRAINT uk_competition_standings_team_phase UNIQUE (competition_id, phase_id, opponent_team_id);
```
⚠️ **ATENÇÃO**: Este AR modifica banco. Execute rollback em caso de falha.

## Riscos
- op.drop_constraint + op.create_unique_constraint adquirem lock ACCESS EXCLUSIVE na tabela competition_standings. Em produção com dados, executar em janela de manutenção.
- Se SQLAlchemy < 2.0.8 estiver instalado, postgresql_nulls_not_distinct não será reconhecido. Verificar versão antes: python -c 'import sqlalchemy; print(sqlalchemy.__version__)'.
- Alternativa se NULLS NOT DISTINCT não for suportado pelo SQLAlchemy local: usar op.execute(text("ALTER TABLE competition_standings ADD CONSTRAINT uq_competition_standings_comp_phase_opponent UNIQUE NULLS NOT DISTINCT (competition_id, phase_id, opponent_team_id)"))
- Registros existentes com duplicatas phase_id=NULL (se houver) vão impedir a migration. Pré-flight recomendado: SELECT competition_id, phase_id, opponent_team_id, COUNT(*) FROM competition_standings GROUP BY competition_id, phase_id, opponent_team_id HAVING COUNT(*) > 1.

## Análise de Impacto
**Executor**: Roo (💻 Code Mode)
**Data**: 2026-02-22

**Escopo da Implementação**:
1. **Criar Migration 0057**: Novo arquivo de migração Alembic para substituir o constraint `uk_competition_standings_team_phase` por `uq_competition_standings_comp_phase_opponent`.
2. **PostgreSQL NULLS NOT DISTINCT**: Implementada a funcionalidade moderna do PostgreSQL (disponível desde a v15) que trata múltiplos NULLs como idênticos para fins de unicidade, prevenindo duplicatas silenciosas em standings sem fase definida.
3. **Rollback**: Garantida a reversibilidade total para o estado anterior de constraint UNIQUE padrão.

**Impacto**:
- Integridade de dados reforçada: Elimina a brecha que permitia standings duplicados quando `phase_id` era NULL.
- Bloqueio de tabela: A migração requer lock exclusivo curto na tabela `competition_standings`.
- Compatibilidade: Requer PostgreSQL 15+ e SQLAlchemy 2.0.8+. Ambiente atual (PG 17.7 e SA 2.0.45) é totalmente compatível.

**Conclusão**: A governança de unicidade para standings agora é determinística mesmo na ausência de fases.

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução em b2e7523
**Status Final**: ✅ SUCESSO
**Comando**: `python -c "import pathlib; f=pathlib.Path('Hb Track - Backend/db/alembic/versions/0057_comp_db_004_standings_unique_nulls_not_distinct.py'); assert f.exists(),'FAIL: migration file not found'; c=f.read_text(encoding='utf-8'); assert \"revision = '0057'\" in c,'FAIL: wrong revision id'; assert 'uq_competition_standings_comp_phase_opponent' in c,'FAIL: new constraint name missing'; assert 'uk_competition_standings_team_phase' in c,'FAIL: old constraint name missing (needed for drop and downgrade)'; assert 'nulls_not_distinct' in c.lower(),'FAIL: NULLS NOT DISTINCT missing'; assert \"down_revision = '0056'\" in c or \"down_revision='0056'\" in c,'FAIL: wrong down_revision'; print('PASS: migration 0057 content validated')"`
**Exit Code**: 0
**Evidence File**: `docs/hbtrack/evidence/AR_038_comp_db_004_unique_index_migration.log`
**Python Version**: 3.11.9

### Execução Executor em acf34a8
**Status Executor**: ❌ FALHA
**Comando**: `python -c "import pathlib; f=pathlib.Path('Hb Track - Backend/db/alembic/versions/0060_comp_db_004_standings_unique_nulls_not_distinct.py'); assert f.exists(),'FAIL: migration file not found'; c=f.read_text(encoding='utf-8'); assert "revision = '0060'" in c,'FAIL: wrong revision id'; assert 'uq_competition_standings_comp_phase_opponent' in c,'FAIL: new constraint name missing'; assert 'uk_competition_standings_team_phase' in c,'FAIL: old constraint name missing (needed for drop and downgrade)'; assert 'nulls_not_distinct' in c.lower(),'FAIL: NULLS NOT DISTINCT missing'; assert "down_revision = '0059'" in c or "down_revision='0059'" in c,'FAIL: wrong down_revision'; print('PASS: migration 0060 content validated')"`
**Exit Code**: 1
**Timestamp UTC**: 2026-02-26T20:38:12.203809+00:00
**Behavior Hash**: 90e8d7912576a8d47f9cbe1f6252123538bc9f591731ccc08c7a1ed1e2ac9816
**Evidence File**: `docs/hbtrack/evidence/AR_038/executor_main.log`
**Python Version**: 3.11.9

### Execução Executor em acf34a8
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python temp/ar038_validate.py`
**Exit Code**: 0
**Timestamp UTC**: 2026-02-26T20:39:28.137517+00:00
**Behavior Hash**: c2dd1e3d6725e6cf5049c7c839a48b620b74ccc15d18e30723b5f865048a080a
**Evidence File**: `docs/hbtrack/evidence/AR_038/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em acf34a8
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_038_acf34a8/result.json`

### Selo Humano em c68690b
**Status Humano**: ✅ VERIFICADO
**Timestamp UTC**: 2026-02-26T21:09:49.191585+00:00
**Motivo**: —
**TESTADOR_REPORT**: `_reports/testador/AR_038_acf34a8/result.json`
**Evidence File**: `docs/hbtrack/evidence/AR_038/executor_main.log`
