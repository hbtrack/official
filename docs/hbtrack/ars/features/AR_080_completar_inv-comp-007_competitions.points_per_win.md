# AR_080 — Completar INV-COMP-007: competitions.points_per_win NOT NULL + model fix

**Status**: 🏗️ EM_EXECUCAO
**Versão do Protocolo**: 1.3.0

## Descrição
Criar migração Alembic que:

1. UPDATE competitions SET points_per_win = 2 WHERE points_per_win IS NULL;
   (data migration — preenche NULLs com valor padrão handebol antes de ALTER)

2. ALTER TABLE competitions ALTER COLUMN points_per_win SET NOT NULL;
   (torna coluna consistente com points_per_draw e points_per_loss)

3. Atualizar model competition.py:
   - Trocar `Optional[int]` → `int` em points_per_win
   - Trocar `nullable=True` → `nullable=False` no mapped_column

INVARIANTE MATERIALIZADA:
- INV-COMP-007 (scoring_rules_competitions): consistência entre ppw, ppd, ppl (todos NOT NULL DEFAULT)

EVIDÊNCIA ESPERADA:
- schema.sql: points_per_win integer DEFAULT 2 NOT NULL
- model: Mapped[int] em vez de Mapped[Optional[int]]
- INSERT com points_per_win=NULL retorna ERROR

## Critérios de Aceite
PASS: (1) Migration aplica com exit 0; (2) grep em schema.sql mostra 'points_per_win integer DEFAULT 2 NOT NULL'; (3) INSERT com points_per_win=NULL em competitions falha com not-null violation; (4) INV-COMP-008 service continua funcional (compute_points recebe int, não None). FAIL: INSERT com NULL passa, ou migration falha, ou tests de service regridem.

## Write Scope
- Hb Track - Backend/db/alembic/versions/*.py
- Hb Track - Backend/docs/ssot/schema.sql
- Hb Track - Backend/app/models/competition.py

## SSOT Touches
- [ ] docs/ssot/schema.sql

## Validation Command (Contrato)
```
python temp/run_ar080_wrapper.py
```
> ⚠️ Validation command usa sqlalchemy sync para verificar NOT NULL via information_schema + testa rejeição de NULL insert. Wrapper: temp/run_ar080_wrapper.py

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_080/executor_main.log`

## Rollback Plan (Contrato)
```
python scripts/run/hb_cli.py downgrade head-1
git checkout -- "Hb Track - Backend/docs/ssot/schema.sql"
git checkout -- "Hb Track - Backend/app/models/competition.py"
```
⚠️ **ATENÇÃO**: Este AR modifica banco. Execute rollback em caso de falha.

## Riscos
- Se existirem competitions com points_per_win NULL, o UPDATE deve preceder o ALTER — verificar ordem na migration
- Model change (Optional→int) pode quebrar serializers/schemas Pydantic que esperam Optional — Executor deve revisar schemas
- service compute_points já recebe int como parâmetro (sem defaults) — não é afetado

## Análise de Impacto

**Tipo**: Modificação DB (NOT NULL) + Modificação Model

**Migration criada**: `0064_comp_db_ppw_not_null.py` (revision=0064, down_revision=0063)
- Step 1 (data): `UPDATE competitions SET points_per_win = 2 WHERE points_per_win IS NULL`
- Step 2 (DDL): `ALTER TABLE competitions ALTER COLUMN points_per_win SET NOT NULL`
- Downgrade: `ALTER TABLE competitions ALTER COLUMN points_per_win DROP NOT NULL`

**Pre-check executado**: 0 registros com points_per_win=NULL (DB safe)

**Model alterado**: `app/models/competition.py` linha 124
- Antes: `Mapped[Optional[int]] = mapped_column(sa.Integer(), nullable=True, server_default=sa.text('2'))`
- Depois: `Mapped[int] = mapped_column(sa.Integer(), nullable=False, server_default=sa.text('2'))`

**Schemas Pydantic**: `competitions_v2.py` mantém `Optional[int]` propositalmente (PATCH permite omitir campo), sem breaking change.

**SSOT**: `docs/ssot/schema.sql` linha 996 atualizada para `points_per_win integer DEFAULT 2 NOT NULL`

**Riscos mitigados**:
- Zero NULLs no DB → UPDATE é no-op, ALTER seguro
- points_per_draw e points_per_loss já eram NOT NULL → consistência
- Schemas de resposta (`CompetitionV2Response`) mantém Optional para retrocompat

---
## Carimbo de Execução
_(Gerado por hb report)_


### Execução Executor em ef6f73a
**Status Executor**: ❌ FALHA
**Comando**: `python temp/run_ar080_wrapper.py`
**Exit Code**: 1
**Timestamp UTC**: 2026-02-25T11:11:38.864819+00:00
**Behavior Hash**: 87e1207ff9fa677f3d9d34bdb9010ae9fdb59f8030539b4f512f2a371d88b2ef
**Evidence File**: `docs/hbtrack/evidence/AR_080/executor_main.log`
**Python Version**: 3.11.9


### Execução Executor em ef6f73a
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python temp/run_ar080_wrapper.py`
**Exit Code**: 0
**Timestamp UTC**: 2026-02-25T11:12:04.116714+00:00
**Behavior Hash**: fbc0352fc47623ca00977c8429ff2a0c19e4de860e26d21618157187f8fb59fc
**Evidence File**: `docs/hbtrack/evidence/AR_080/executor_main.log`
**Python Version**: 3.11.9

