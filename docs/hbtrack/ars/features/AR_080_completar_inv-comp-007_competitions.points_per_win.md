# AR_080 — Completar INV-COMP-007: competitions.points_per_win NOT NULL + model fix

**Status**: 🔲 PENDENTE
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
cd 'Hb Track - Backend'; python -m pytest tests/unit/test_competition_standings_service.py -x -q 2>&1; python -m alembic upgrade head 2>&1; python -c "import subprocess,sys; r=subprocess.run(['python','-c','import psycopg2; conn=psycopg2.connect(host=\"localhost\",port=5433,dbname=\"hbtrack\",user=\"hbtrack\",password=\"hbtrack\"); cur=conn.cursor(); cur.execute(\"INSERT INTO competitions(organization_id,name,points_per_win) VALUES(gen_random_uuid(),\\"test\\",NULL)\"); conn.commit(); print(\"FAIL: NULL aceito\")'], capture_output=True, text=True, cwd='Hb Track - Backend'); print('OK: NULL rejeitado' if r.returncode!=0 else 'FAIL: NULL aceito'); sys.exit(0 if r.returncode!=0 else 1)"
```

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
_(A ser preenchido pelo Executor)_

---
## Carimbo de Execução
_(Gerado por hb report)_

