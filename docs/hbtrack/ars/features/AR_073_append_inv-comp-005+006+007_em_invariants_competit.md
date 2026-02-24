# AR_073 — Append INV-COMP-005+006+007 em INVARIANTS_COMPETITIONS.md

**Status**: 🔲 PENDENTE
**Versão do Protocolo**: 1.3.0

## Descrição
APPEND 3 invariantes ao arquivo docs/hbtrack/modulos/competitions/INVARIANTS_COMPETITIONS.md (continuando INV-COMP-001 a INV-COMP-004 existentes). Usar formato SPEC YAML v1.0 (idem INV-COMP-001 a 004).

INV-COMP-005 (class A - DB Constraint): fk_competition_standings_team_id
- FK competition_standings.team_id referencias teams.id ON DELETE SET NULL
- Evidence: schema.sql:6039
- Status: IMPLEMENTADO

INV-COMP-006 (class A - DB Constraint): Soft Delete COMP-DB-001 (5 tabelas)
- deleted_at TIMESTAMPTZ + deleted_reason TEXT + CHECK ck_soft_delete em competitions, competition_matches, competition_standings, competition_match_events, match_rosters
- Evidence: schema.sql fase 0055 (AR_008)
- Status: IMPLEMENTADO

INV-COMP-007 (class A - DB Constraint): Scoring Rules
- points_per_win INTEGER DEFAULT 2 (schema.sql:994); points_per_draw e points_per_loss PENDENTES (AR_036)
- Evidence: schema.sql:994; AR_036 PENDENTE
- Status: PARCIALMENTE IMPLEMENTADO

ATENCAO: APPEND ao final do arquivo existente - NAO sobrescrever INV-COMP-001 a 004.

## Critérios de Aceite
1. docs/hbtrack/modulos/competitions/INVARIANTS_COMPETITIONS.md contem INV-COMP-005, INV-COMP-006 e INV-COMP-007.
2. INV-COMP-005 referencia fk_competition_standings_team_id + status IMPLEMENTADO.
3. INV-COMP-006 referencia deleted_at + 5 tabelas.
4. INV-COMP-007 referencia points_per_win + status PARCIALMENTE IMPLEMENTADO.
5. INV-COMP-001 a 004 preservados (nao modificados).

## Validation Command (Contrato)
```
python -c "import pathlib; src=pathlib.Path('docs/hbtrack/modulos/competitions/INVARIANTS_COMPETITIONS.md').read_text(encoding='utf-8'); assert 'INV-COMP-005' in src, 'FAIL INV-COMP-005'; assert 'INV-COMP-006' in src, 'FAIL INV-COMP-006'; assert 'INV-COMP-007' in src, 'FAIL INV-COMP-007'; assert 'fk_competition_standings_team_id' in src, 'FAIL fk_team_id'; assert 'deleted_at' in src, 'FAIL soft_delete'; assert 'points_per_win' in src, 'FAIL scoring'; assert 'PARCIALMENTE IMPLEMENTADO' in src, 'FAIL status parcial'; assert 'INV-COMP-001' in src, 'FAIL INV-COMP-001 perdido'; print('PASS: INVARIANTS_COMPETITIONS INV-COMP-005+006+007 OK')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_073/executor_main.log`

## Notas do Arquiteto
docs/hbtrack/modulos/ fora dos governed roots - write_scope vazio correto. APPEND ao final do arquivo existente.

## Análise de Impacto
_(A ser preenchido pelo Executor)_

---
## Carimbo de Execução
_(Gerado por hb report)_

