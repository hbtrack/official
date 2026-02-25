# AR_124 — CHECK score >= 0 em competition_matches

**Status**: 🏗️ EM_EXECUCAO
**Versão do Protocolo**: 1.3.0

## Descrição
Implementar constraint ck_match_score_valid para garantir que home_score >= 0 AND away_score >= 0. Scores de handebol nunca são negativos. Esta constraint impede erros de digitação e validações client-side falhas. Constraint: ck_match_score_valid CHECK ((home_score IS NULL OR home_score >= 0) AND (away_score IS NULL OR away_score >= 0)). Permitir NULL para partidas não finalizadas.

## Critérios de Aceite
1. EXISTE constraint ck_match_score_valid em schema.sql. 2. INSERT com home_score=-1 DEVE falhar com 23514/ck_match_score_valid. 3. INSERT com away_score=-5 DEVE falhar. 4. INSERT com home_score=30, away_score=25 DEVE passar. 5. INSERT com NULL scores DEVE passar (partida draft).

## Write Scope
- Hb Track - Backend/db/alembic/versions/*
- Hb Track - Backend/docs/ssot/schema.sql
- Hb Track - Backend/tests/invariants/test_inv_comp_016_score_valid.py

## SSOT Touches
- [ ] docs/ssot/schema.sql

## Validation Command (Contrato)
```
cd "Hb Track - Backend" && pytest tests/invariants/test_inv_comp_016_score_valid.py -v --tb=short
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_124/executor_main.log`

## Rollback Plan (Contrato)
```
git checkout -- Hb Track - Backend/db/alembic/versions/
git checkout -- Hb Track - Backend/docs/ssot/schema.sql
```
⚠️ **ATENÇÃO**: Este AR modifica banco. Execute rollback em caso de falha.

## Análise de Impacto

**Constraint alvo**: `ck_competition_matches_score_home_gte_0` + `ck_competition_matches_score_away_gte_0`
**Tabela**: `competition_matches`
**Migration existente**: `0062_comp_db_check_constraints_competition_matches.py` — constraints já criadas no DB.
**Schema SSOT**: `docs/ssot/schema.sql` — já reflete  as constraints (não requer nova migration).

**Obrigação A — Setup (ancorado no schema)**:
- Tabela: `organizations` (id uuid PK, name varchar(100) NOT NULL)
- Tabela: `competitions` (id uuid PK, organization_id uuid FK NOT NULL, name varchar(200) NOT NULL)
- Tabela: `competition_matches` (id uuid PK, competition_id uuid FK NOT NULL, home_score int NULL, away_score int NULL)
- FK chain: organizations → competitions → competition_matches

**Obrigação B — Critério de falha**:
- SQLSTATE `23514` (check_violation)
- Constraint names: `ck_competition_matches_score_home_gte_0` (home < 0) e `ck_competition_matches_score_away_gte_0` (away < 0)
- `IntegrityError` do SQLAlchemy wrapping `asyncpg.exceptions.CheckViolationError`

**Escopo do patch**: Apenas `tests/invariants/test_inv_comp_016_score_valid.py` (novo).
**Sem migration nova**: constraint já existe via 0062.
**SSOT touches**: schema.sql já atualizado — nenhuma alteração necessária.
**Risco de regressão**: Zero — só cria teste, não altera código de produção.

**Validação**: `pytest tests/invariants/test_inv_comp_016_score_valid.py -v --tb=short` (target: 4 testes PASS)

---
## Carimbo de Execução
_(Gerado por hb report)_


### Execução Executor em 529b87c
**Status Executor**: ❌ FALHA
**Comando**: `cd "Hb Track - Backend" && pytest tests/invariants/test_inv_comp_016_score_valid.py -v --tb=short`
**Exit Code**: 1
**Timestamp UTC**: 2026-02-25T17:55:29.574011+00:00
**Behavior Hash**: b9433b8826048952bb755100971a6da85215306f7a5eee613b03df63ee66f7e4
**Evidence File**: `docs/hbtrack/evidence/AR_124/executor_main.log`
**Python Version**: 3.11.9


### Execução Executor em 529b87c
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `cd "Hb Track - Backend" && pytest tests/invariants/test_inv_comp_016_score_valid.py -v --tb=short`
**Exit Code**: 0
**Timestamp UTC**: 2026-02-25T17:57:37.066212+00:00
**Behavior Hash**: 88a9304ffff8029a498597929f59c0792f76e55c47b4341ffa7562e3463e9b4e
**Evidence File**: `docs/hbtrack/evidence/AR_124/executor_main.log`
**Python Version**: 3.11.9

