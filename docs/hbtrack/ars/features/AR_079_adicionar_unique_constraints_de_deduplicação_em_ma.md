# AR_079 — Adicionar UNIQUE constraints de deduplicação em match_roster e competition_matches

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.3.0

## Descrição
Criar migração Alembic que adiciona 2 UNIQUE partial indexes:

1. `uq_match_roster_athlete_per_match`: UNIQUE (match_id, athlete_id) WHERE deleted_at IS NULL
   - Garante: Um atleta aparece no máximo uma vez na escalação de cada partida
   - Proteção contra: IA/OCR que lê mesmo jogador duas vezes na súmula
   - INV-COMP-009

2. `uq_competition_matches_external_ref`: UNIQUE (competition_id, external_reference_id) WHERE external_reference_id IS NOT NULL AND deleted_at IS NULL
   - Garante: Cada súmula é importada apenas uma vez por competição
   - Proteção contra: Re-importação acidental do mesmo documento
   - INV-COMP-014

EVIDÊNCIA ESPERADA:
- Migração aplica sem erro (exit 0)
- pg_dump mostra indexes no schema
- INSERT duplicado retorna ERROR com nome do index

## Critérios de Aceite
PASS: (1) Migração aplica com exit 0; (2) Indexes existem no schema.sql gerado; (3) INSERT de atleta duplicado em match_roster falha; (4) INSERT de external_reference_id duplicado em competition_matches falha. FAIL: Qualquer INSERT duplicado passa ou index não existe.

## Write Scope
- Hb Track - Backend/db/alembic/versions/*.py
- Hb Track - Backend/docs/ssot/schema.sql

## SSOT Touches
- [ ] docs/ssot/schema.sql

## Validation Command (Contrato)
```
python -c "import subprocess, sys; r1=subprocess.run(['python','-m','alembic','upgrade','head'], cwd='Hb Track - Backend', capture_output=True, text=True); print('MIGRATION:', 'OK' if r1.returncode==0 else 'FAIL:', r1.stdout.strip() or r1.stderr.strip()); db_url=next(l.split('=',1)[1].strip().strip(chr(34)).strip(chr(39)) for l in open('Hb Track - Backend/.env') if l.strip().startswith('DATABASE_URL')); from sqlalchemy import create_engine, text; engine=create_engine(db_url.replace('postgresql+asyncpg','postgresql')); conn=engine.connect(); names=['uq_match_roster_athlete_per_match','uq_competition_matches_external_ref']; rows=conn.execute(text(f'SELECT indexname FROM pg_indexes WHERE indexname = ANY(ARRAY{names!r}::text[])')).fetchall(); found_set={r[0] for r in rows}; found=sum(1 for n in names if n in found_set); print(f'INDEXES_FOUND: {found}/2'); [print(f'  {n}: OK' if n in found_set else f'  {n}: MISSING') for n in names]; sys.exit(0 if r1.returncode==0 and found>=2 else 1)"
```
> ⚠️ Validation command usa sqlalchemy sync + pg_indexes para verificar partial indexes diretamente no banco local (pg_dump do VPS não reflete migrations locais).

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_079/executor_main.log`

## Rollback Plan (Contrato)
```
python scripts/run/hb_cli.py downgrade head-1
git checkout -- Hb Track - Backend/docs/ssot/schema.sql
```
⚠️ **ATENÇÃO**: Este AR modifica banco. Execute rollback em caso de falha.

## Riscos
- Se existirem duplicatas em match_roster (mesmo atleta 2x por partida), migração falha → verificar antes
- Se existirem external_reference_id duplicados em competition_matches, migração falha → verificar antes
- Partial index ignora soft-deleted rows (deleted_at IS NOT NULL não conflita)

## Análise de Impacto

**Tipo**: Criação (migration) — UNIQUE partial indexes

**Migration criada**:
- `Hb Track - Backend/db/alembic/versions/0063_comp_db_unique_constraints_match_roster_compet.py`
- revision = '0063', down_revision = '0062'

**Indexes criados**:
1. `uq_match_roster_athlete_per_match`:  
   `UNIQUE (match_id, athlete_id) WHERE deleted_at IS NULL`  
   — Protege escalação contra atleta duplicado (INV-COMP-009)

2. `uq_competition_matches_external_ref`:  
   `UNIQUE (competition_id, external_reference_id) WHERE external_reference_id IS NOT NULL AND deleted_at IS NULL`  
   — Protege contra re-importação de súmula (INV-COMP-014)

**Pré-validação** (executado antes da migration):
- `match_roster` duplicates: 0 ✅
- `competition_matches` ext_ref duplicates: 0 ✅
- Colunas confirmadas: `match_roster.match_id`, `match_roster.athlete_id`, `competition_matches.external_reference_id`
- Alembic state: 0062 (pré-migração)

**NULL handling**:
- `uq_match_roster_athlete_per_match`: WHERE deleted_at IS NULL (soft-deleted não conflitam)
- `uq_competition_matches_external_ref`: WHERE IS NOT NULL AND deleted_at IS NULL (partidas sem external_reference são livres)

**Compatibilidade Windows**:
- Validation command original usa PowerShell (Select-String, Write-Host — não portável)
- Adaptado para Python one-liner com sqlalchemy sync + `pg_indexes` query direta ao banco local

**Rollback**: `alembic downgrade head-1` reverte migration 0063 (DROP INDEX dos dois partial indexes)

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução Executor em 7dadb4c
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python -c "import subprocess, sys; r1=subprocess.run(['python','-m','alembic','upgrade','head'], cwd='Hb Track - Backend', capture_output=True, text=True); print('MIGRATION:', 'OK' if r1.returncode==0 else 'FAIL:', r1.stdout.strip() or r1.stderr.strip()); db_url=next(l.split('=',1)[1].strip().strip(chr(34)).strip(chr(39)) for l in open('Hb Track - Backend/.env') if l.strip().startswith('DATABASE_URL')); from sqlalchemy import create_engine, text; engine=create_engine(db_url.replace('postgresql+asyncpg','postgresql')); conn=engine.connect(); names=['uq_match_roster_athlete_per_match','uq_competition_matches_external_ref']; rows=conn.execute(text(f'SELECT indexname FROM pg_indexes WHERE indexname = ANY(ARRAY{names!r}::text[])')).fetchall(); found_set={r[0] for r in rows}; found=sum(1 for n in names if n in found_set); print(f'INDEXES_FOUND: {found}/2'); [print(f'  {n}: OK' if n in found_set else f'  {n}: MISSING') for n in names]; sys.exit(0 if r1.returncode==0 and found>=2 else 1)"`
**Exit Code**: 0
**Timestamp UTC**: 2026-02-25T09:12:59.965393+00:00
**Behavior Hash**: eb0e51ec8c390326e83389beb2d8f193f0fe404b0f8254d13032271da0277ec7
**Evidence File**: `docs/hbtrack/evidence/AR_079/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em 7dadb4c
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_079_7dadb4c/result.json`

### Selo Humano em 529b87c
**Status Humano**: ✅ VERIFICADO
**Timestamp UTC**: 2026-02-25T17:04:23.883882+00:00
**Motivo**: —
**TESTADOR_REPORT**: `_reports/testador/AR_079_7dadb4c/result.json`
**Evidence File**: `docs/hbtrack/evidence/AR_079/executor_main.log`
