# AR_036 — Migration 0056: ADD COLUMN competitions.points_per_draw + competitions.points_per_loss

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.1.0

## Descrição
Criar arquivo Hb Track - Backend/db/alembic/versions/0056_comp_db_003_scoring_rules_competitions.py com revision='0056', down_revision='0055'.

Upgrade:
  op.add_column('competitions', sa.Column('points_per_draw', sa.Integer(), nullable=False, server_default=sa.text('1')))
  op.add_column('competitions', sa.Column('points_per_loss', sa.Integer(), nullable=False, server_default=sa.text('0')))

Downgrade:
  op.drop_column('competitions', 'points_per_loss')
  op.drop_column('competitions', 'points_per_draw')

Docstring da migration MUST incluir: 'COMP-DB-003: scoring rules — points_per_draw e points_per_loss em competitions'.
NAO modificar nenhum outro arquivo.

## Critérios de Aceite
1) alembic upgrade head retorna exit_code=0 sem erros. 2) SELECT column_name, column_default FROM information_schema.columns WHERE table_name='competitions' AND column_name IN ('points_per_draw','points_per_loss') retorna 2 linhas com defaults '1' e '0'. 3) SELECT points_per_draw, points_per_loss FROM competitions LIMIT 1 retorna valores 1 e 0 para registros existentes. 4) alembic downgrade -1 retorna exit_code=0. 5) alembic upgrade head novamente retorna exit_code=0.

## SSOT Touches
- [x] docs/ssot/schema.sql
- [x] docs/ssot/alembic_state.txt

## Validation Command (Contrato)
```
python -c "import pathlib; s=pathlib.Path('Hb Track - Backend/docs/ssot/schema.sql'); assert s.exists(),'FAIL: schema.sql missing'; c=s.read_text(encoding='utf-8'); assert 'points_per_draw' in c,'FAIL: schema.sql missing points_per_draw column'; assert 'points_per_loss' in c,'FAIL: schema.sql missing points_per_loss column'; assert 'DEFAULT 1' in c or 'default 1' in c.lower(),'FAIL: points_per_draw DEFAULT missing'; print('PASS: schema.sql regenerated with migrations 0056-0061 applied')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_036/executor_main.log`

## Rollback Plan (Contrato)
```
alembic downgrade -1
# OU manualmente:
# ALTER TABLE competitions DROP COLUMN IF EXISTS points_per_loss;
# ALTER TABLE competitions DROP COLUMN IF EXISTS points_per_draw;
```
⚠️ **ATENÇÃO**: Este AR modifica banco. Execute rollback em caso de falha.

## Riscos
- Serviços que calculam classificação com valores hardcoded (ex: DRAW_POINTS = 1) podem entrar em conflito com os valores configurados no banco após a migration. Verificar competition_service.py (ou equivalente) — mas NÃO alterar neste escopo.
- nullable=False com server_default garante zero downtime. Registros existentes receberão points_per_draw=1 e points_per_loss=0 automaticamente.
- Se o Alembic gerar autogenerate após esta migration, ele detectará os novos campos — OK, é o comportamento esperado.

## Análise de Impacto
- **Escopo de código (mínimo e atômico):** criar apenas a migration `0056_comp_db_003_scoring_rules_competitions.py` em `Hb Track - Backend/db/alembic/versions/`.
- **Impacto de banco:** inclusão de 2 colunas `NOT NULL` com `server_default` na tabela `competitions` (`points_per_draw=1`, `points_per_loss=0`), evitando backfill manual para linhas existentes.
- **Compatibilidade:** `down_revision='0055'` preserva encadeamento Alembic atual.
- **Risco técnico principal:** serviços que ainda usem pontuação hardcoded podem divergir da configuração persistida em banco (fora do escopo desta AR).
- **SSOT afetados por contrato:** `docs/ssot/schema.sql` e `docs/ssot/alembic_state.txt` serão regenerados ao final via `scripts/gen_docs_ssot.py`.
- **Rollback planejado:** `alembic downgrade -1` (ou remoção manual das colunas conforme plano da AR).

---
## Carimbo de Execução
_(Gerado por hb report)_

> 📋 Kanban routing: Executor: Evidence Pack missing or incomplete

### Execução Executor em f8f030f
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python -c "import pathlib; s=pathlib.Path('Hb Track - Backend/docs/ssot/schema.sql'); assert s.exists(),'FAIL: schema.sql missing'; c=s.read_text(encoding='utf-8'); assert 'points_per_draw' in c,'FAIL: schema.sql missing points_per_draw column'; assert 'points_per_loss' in c,'FAIL: schema.sql missing points_per_loss column'; assert 'DEFAULT 1' in c or 'default 1' in c.lower(),'FAIL: points_per_draw DEFAULT missing'; print('PASS: schema.sql regenerated with migrations 0056-0061 applied')"`
**Exit Code**: 0
**Timestamp UTC**: 2026-02-24T23:42:07.716690+00:00
**Behavior Hash**: 058cf463747d01cf9eec1a64ce0eeb1afc6ae2cf003e2c75362d68f864bd4b23
**Evidence File**: `docs/hbtrack/evidence/AR_036/executor_main.log`
**Python Version**: 3.11.9

### Selo Humano em f8f030f
**Status Humano**: ✅ VERIFICADO
**Timestamp UTC**: 2026-02-24T23:53:35.432729+00:00
**Motivo**: —
**TESTADOR_REPORT**: `_reports/testador/AR_036_f8f030f/result.json`
**Evidence File**: `docs/hbtrack/evidence/AR_036/executor_main.log`

### Verificacao Testador em 529b87c
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_036_529b87c/result.json`

### Selo Humano em eb88236
**Status Humano**: ✅ VERIFICADO
**Timestamp UTC**: 2026-02-26T18:56:26.500375+00:00
**Motivo**: —
**TESTADOR_REPORT**: `_reports/testador/AR_036_529b87c/result.json`
**Evidence File**: `docs/hbtrack/evidence/AR_036/executor_main.log`
