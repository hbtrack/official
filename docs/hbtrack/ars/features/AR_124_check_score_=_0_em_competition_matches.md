# AR_124 — CHECK score >= 0 em competition_matches

**Status**: 🔲 PENDENTE
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
_(A ser preenchido pelo Executor)_

---
## Carimbo de Execução
_(Gerado por hb report)_

