# AR_125 — CHECK times diferentes em competition_matches

**Status**: 🔲 PENDENTE
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
cd "Hb Track - Backend" && pytest tests/invariants/test_inv_comp_018_different_teams.py -v --tb=short
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
_(A ser preenchido pelo Executor)_

---
## Carimbo de Execução
_(Gerado por hb report)_

