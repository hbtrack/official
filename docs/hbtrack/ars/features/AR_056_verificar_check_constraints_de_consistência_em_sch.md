# AR_056 — Verificar CHECK constraints de consistência em schema.sql

**Status**: 🏗️ EM_EXECUCAO
**Versão do Protocolo**: 1.3.0

## Descrição
Verificar que os principais CHECK constraints de consistência de dados estão declarados no schema.sql SSOT. Os constraints cobrem: (1) soft-delete pair — deleted_at IS NULL ↔ deleted_reason IS NULL em athletes, attendance, competition_matches, etc; (2) shirt_number range 1..99; (3) attendance status enum (present/absent); (4) attendance source enum (manual/import/correction); (5) categories max_age > 0; (6) match_events score >= 0. Estes constraints são a linha de defesa de consistência no banco — sua ausência indica drift entre modelo e DB.

## Critérios de Aceite
- ck_athletes_deleted_reason presente em schema.sql
- ck_athletes_shirt_number presente em schema.sql
- ck_attendance_status presente em schema.sql
- ck_attendance_source presente em schema.sql
- ck_categories_max_age_positive presente em schema.sql
- ck_match_events_score_our presente em schema.sql
- ck_attendance_correction_fields presente em schema.sql
- hb report gera evidence exit 0

## Write Scope
- Hb Track - Backend/docs/ssot/schema.sql

## Validation Command (Contrato)
```
python -c "import pathlib; s=pathlib.Path('Hb Track - Backend/docs/ssot/schema.sql').read_text(encoding='utf-8'); checks={'ck_athletes_deleted_reason':'ck_athletes_deleted_reason' in s,'ck_athletes_shirt_number':'ck_athletes_shirt_number' in s,'ck_attendance_status':'ck_attendance_status' in s,'ck_attendance_source':'ck_attendance_source' in s,'ck_categories_max_age_positive':'ck_categories_max_age_positive' in s,'ck_match_events_score_our':'ck_match_events_score_our' in s,'ck_attendance_correction_fields':'ck_attendance_correction_fields' in s}; fails=[k for k,v in checks.items() if not v]; [print(f'FAIL: CHECK constraint ausente: {f}') for f in fails]; exit(len(fails)) if fails else print(f'PASS AR_056: {len(checks)} CHECK constraints de consistência verificados em schema.sql')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_056/executor_main.log`

## Rollback Plan (Contrato)
```
git checkout -- "Hb Track - Backend/docs/ssot/schema.sql"
```
⚠️ **ATENÇÃO**: Este AR modifica banco. Execute rollback em caso de falha.

## Notas do Arquiteto
Task doc-only de verificação. Executor não altera código — apenas verifica invariante existente. Se algum constraint estiver ausente do schema.sql, Executor deve checar se está no alembic mais recente e reportar para Arquiteto.

## Análise de Impacto
- Verificação confirmada dos CHECK constraints listados no [schema.sql](Hb%20Track%20-%20Backend/docs/ssot/schema.sql:677).
- Nenhuma alteração de código necessária; apenas validação e geração de evidência.
- Risco baixo: sem migrações ou mudanças de comportamento.
- Rollback não aplicável (sem alterações no SSOT).

---
## Carimbo de Execução
_(Gerado por hb report)_


### Execução Executor em c08f148
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python -c "import pathlib; s=pathlib.Path('Hb Track - Backend/docs/ssot/schema.sql').read_text(encoding='utf-8'); checks={'ck_athletes_deleted_reason':'ck_athletes_deleted_reason' in s,'ck_athletes_shirt_number':'ck_athletes_shirt_number' in s,'ck_attendance_status':'ck_attendance_status' in s,'ck_attendance_source':'ck_attendance_source' in s,'ck_categories_max_age_positive':'ck_categories_max_age_positive' in s,'ck_match_events_score_our':'ck_match_events_score_our' in s,'ck_attendance_correction_fields':'ck_attendance_correction_fields' in s}; fails=[k for k,v in checks.items() if not v]; [print(f'FAIL: CHECK constraint ausente: {f}') for f in fails]; exit(len(fails)) if fails else print(f'PASS AR_056: {len(checks)} CHECK constraints de consistência verificados em schema.sql')"`
**Exit Code**: 0
**Timestamp UTC**: 2026-02-24T21:28:50.012262+00:00
**Behavior Hash**: edf1ebf11cd0584c3575207ab679629dfc39c77a09520712f159ef98d4761167
**Evidence File**: `docs/hbtrack/evidence/AR_056/executor_main.log`
**Python Version**: 3.11.9

