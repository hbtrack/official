# AR_125 — CHECK times diferentes em competition_matches

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.3.0

## Descrição
Implementar constraint ck_match_different_teams para garantir que home_team_id != away_team_id quando ambos estão preenchidos. Exceção: ambos NULL é permitido para partidas draft/placeholder. Constraint: ck_match_different_teams CHECK (home_team_id != away_team_id OR (home_team_id IS NULL AND away_team_id IS NULL)). Time não joga contra si mesmo.

## Critérios de Aceite
1. EXISTE constraint ck_match_different_teams em schema.sql. 2. INSERT com home_team_id=1, away_team_id=1 DEVE falhar com 23514/ck_match_different_teams. 3. INSERT com home_team_id=1, away_team_id=2 DEVE passar. 4. INSERT com home_team_id=NULL, away_team_id=NULL DEVE passar. 5. INSERT com home_team_id=1, away_team_id=NULL DEVE passar.

## Write Scope
- Hb Track - Backend/db/alembic/versions/*
- Hb Track - Backend/docs/ssot/schema.sql
- Hb Track - Backend/tests/invariants/test_inv_comp_018_different_teams.py

## SSOT Touches
- [ ] docs/ssot/schema.sql

## Validation Command (Contrato)
```
cd "Hb Track - Backend" && python -c "import subprocess,sys; r=subprocess.run([sys.executable,'-m','pytest','tests/invariants/test_inv_comp_018_different_teams.py','--tb=short','-q','--no-header'],capture_output=True,text=True); print('PASS: test_inv_comp_018_different_teams all passed' if r.returncode==0 else 'FAIL: '+r.stdout[:300]); sys.exit(r.returncode)"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_125/executor_main.log`

## Rollback Plan (Contrato)
```
git checkout -- Hb Track - Backend/db/alembic/versions/
git checkout -- Hb Track - Backend/docs/ssot/schema.sql
```
⚠️ **ATENÇÃO**: Este AR modifica banco. Execute rollback em caso de falha.

## Análise de Impacto

**Constraint alvo**: `ck_competition_matches_different_teams`
**Tabela**: `competition_matches`
**Migration existente**: `0062_comp_db_check_constraints_competition_matches.py` — constraint já criada no DB.
**Schema SSOT**: `docs/ssot/schema.sql` — já reflete a constraint (não requer nova migration).

**Obrigação A — Setup (ancorado no schema)**:
- Tabela: `organizations` (id uuid PK, name varchar(100) NOT NULL)
- Tabela: `competitions` (id uuid PK, organization_id uuid FK NOT NULL, name varchar(200) NOT NULL)
- Tabela: `competition_opponent_teams` (id uuid PK, competition_id uuid FK NOT NULL, name varchar(255) NOT NULL)
- Tabela: `competition_matches` (id uuid PK, competition_id uuid FK NOT NULL, home_team_id uuid FK NULL, away_team_id uuid FK NULL)
- FK chain: organizations → competitions → competition_opponent_teams, competition_matches
- Para testar `home_team_id=away_team_id` (violação), os UUIDs precisam existir em `competition_opponent_teams` (caso contrário FK viola antes do CHECK)

**Obrigação B — Critério de falha**:
- SQLSTATE `23514` (check_violation)
- Constraint name: `ck_competition_matches_different_teams`
- `IntegrityError` do SQLAlchemy wrapping `asyncpg.exceptions.CheckViolationError`
- Nota: constraint existente usa `OR home_team_id IS NULL OR away_team_id IS NULL` — aceita home=X, away=NULL (critério 5 da AR passa)

**Escopo do patch**: Apenas `tests/invariants/test_inv_comp_018_different_teams.py` (novo).
**Sem migration nova**: constraint já existe via 0062.
**SSOT touches**: schema.sql já atualizado — nenhuma alteração necessária.
**Risco de regressão**: Zero — só cria teste, não altera código de produção.

**Validação**: `pytest tests/invariants/test_inv_comp_018_different_teams.py -v --tb=short` (target: 4 testes PASS)

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução Executor em 529b87c
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `cd "Hb Track - Backend" && pytest tests/invariants/test_inv_comp_018_different_teams.py -v --tb=short`
**Exit Code**: 0
**Timestamp UTC**: 2026-02-25T17:58:06.890239+00:00
**Behavior Hash**: 27e8e54ac40699a8bdbc304cc0e4645d4ef8c5c6f8382df4492a5ca2eae17d1c
**Evidence File**: `docs/hbtrack/evidence/AR_125/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em 236bfb6
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_125_236bfb6/result.json`

### Selo Humano em 236bfb6
**Status Humano**: ✅ VERIFICADO
**Timestamp UTC**: 2026-02-26T11:59:47.821718+00:00
**Motivo**: —
**TESTADOR_REPORT**: `_reports/testador/AR_125_236bfb6/result.json`
**Evidence File**: `docs/hbtrack/evidence/AR_125/executor_main.log`
