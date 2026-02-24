# AR_104 — Modificar migration 0060 para detectar versão PostgreSQL e aplicar sintaxe compatível

**Status**: ✅ SUCESSO
**Versão do Protocolo**: 1.3.0

## Descrição
Alterar Hb Track - Backend/db/alembic/versions/0060_comp_db_004_standings_unique_nulls_not_distinct.py para: (1) Obter versão do PostgreSQL via SQL 'SHOW server_version', (2) Se major_version >= 15: usar op.create_unique_constraint(..., postgresql_nulls_not_distinct=True), (3) Se major_version < 15: usar op.execute() com CREATE UNIQUE INDEX parcial (WHERE phase_id IS NOT NULL OR opponent_team_id IS NOT NULL), (4) Manter downgrade() com lógica simétrica (detectar versão e reverter apropriadamente), (5) Adicionar comentário explicando retrocompatibilidade e comportamento equivalente. Preservar constraint/index name 'uq_competition_standings_comp_phase_opponent' em ambos os casos. NÃO modificar migrations anteriores (0057-0059) ou posteriores (0061).

## Critérios de Aceite
- Função upgrade() detecta versão do PostgreSQL via 'SHOW server_version'
- Se PG >= 15: usa create_unique_constraint com postgresql_nulls_not_distinct=True
- Se PG < 15: usa op.execute com CREATE UNIQUE INDEX parcial (WHERE phase_id IS NOT NULL OR opponent_team_id IS NOT NULL)
- Função downgrade() tem lógica simétrica (detecta versão e reverte apropriadamente)
- Comentário docstring explica retrocompatibilidade e semântica equivalente
- Nome do constraint/index é 'uq_competition_standings_comp_phase_opponent' em ambos os casos
- Código Python é idiomático e seguro (sem SQL injection, usa binding se necessário)

## Write Scope
- Hb Track - Backend/db/alembic/versions/0060_comp_db_004_standings_unique_nulls_not_distinct.py

## Validation Command (Contrato)
```
python temp/validate_ar104.py
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_104/executor_main.log`

## Rollback Plan (Contrato)
```
git checkout -- Hb Track - Backend/db/alembic/versions/0060_comp_db_004_standings_unique_nulls_not_distinct.py
```
⚠️ **ATENÇÃO**: Este AR modifica banco. Execute rollback em caso de falha.

## Análise de Impacto
**Escopo**: Migration 0060 (retrocompatibilidade PostgreSQL 12-14)

**Impacto**:
- Modifica lógica de upgrade/downgrade para detectar versão PG dinamicamente
- PG >= 15: Comportamento atual (NULLS NOT DISTINCT nativo)
- PG < 15: Fallback para UNIQUE INDEX parcial (semântica equivalente)
- ARs bloqueadas (002.5_A/B/D): Desbloqueadas após esta implementação

**Risco**: Baixo (preserva semântica, apenas muda sintaxe SQL por versão)

---
## Carimbo de Execução
_(Gerado por hb report)_


### Execução Executor em 15ac28c
**Status Executor**: ❌ FALHA
**Comando**: `cd 'Hb Track - Backend' && alembic upgrade head && python -c "from sqlalchemy import inspect, text; from db.session import engine; insp = inspect(engine); assert 'competition_standings' in insp.get_table_names(), 'Tabela competition_standings não existe'; with engine.connect() as conn: version = conn.execute(text('SHOW server_version')).scalar(); major = int(version.split('.')[0]); print(f'PostgreSQL version: {major}'); constraints = [c['name'] for c in insp.get_unique_constraints('competition_standings')]; indexes = [i['name'] for i in insp.get_indexes('competition_standings')]; target_name = 'uq_competition_standings_comp_phase_opponent'; assert target_name in constraints or target_name in indexes, f'Constraint/index {target_name} não encontrado (constraints={constraints}, indexes={indexes})'; print(f'✅ PASS: Constraint/index {target_name} existe para PG {major}')"`
**Exit Code**: 1
**Timestamp UTC**: 2026-02-24T16:01:06.649563+00:00
**Behavior Hash**: 579219a4efbc60e5acc757e65baa1396a1df894e6b431ac0d59a4e1b83f177a3
**Evidence File**: `docs/hbtrack/evidence/AR_104/executor_main.log`
**Python Version**: 3.11.9


### Execução Executor em 15ac28c
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python temp/validate_ar104.py`
**Exit Code**: 0
**Timestamp UTC**: 2026-02-24T16:02:34.059918+00:00
**Behavior Hash**: c5de730d3ff9a535905ba1a2d00b0a9b44c5fbac65787acfb4019050be244395
**Evidence File**: `docs/hbtrack/evidence/AR_104/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em 15ac28c
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_104_15ac28c/result.json`
