# AR_073 — Append INV-COMP-005+006+007 em INVARIANTS_COMPETITIONS.md

**Status**: ✅ VERIFICADO
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
**Executor**: 2026-02-24

**Escopo**: Documentação pura - APPEND 3 invariantes em INVARIANTS_COMPETITIONS.md existente.

**Riscos**:
- **BAIXO**: Apenas append de texto em arquivo .md fora dos governed roots.
- **BAIXO**: Validação verifica presença de INV-COMP-001 para garantir que arquivo existente não foi sobrescrito.

**Dependências**:
- Arquivo base: `docs/hbtrack/modulos/competitions/INVARIANTS_COMPETITIONS.md` (existe desde AR_048)
- Formato: SPEC YAML v1.0 (padrão existente INV-COMP-001 a 004)

**Patch**:
- 1 arquivo modificado: append ~50 linhas no final

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução Executor em c5f1ba8
**Status Executor**: ❌ FALHA
**Comando**: `python -c "import pathlib; src=pathlib.Path('docs/hbtrack/modulos/competitions/INVARIANTS_COMPETITIONS.md').read_text(encoding='utf-8'); assert 'INV-COMP-005' in src, 'FAIL INV-COMP-005'; assert 'INV-COMP-006' in src, 'FAIL INV-COMP-006'; assert 'INV-COMP-007' in src, 'FAIL INV-COMP-007'; assert 'fk_competition_standings_team_id' in src, 'FAIL fk_team_id'; assert 'deleted_at' in src, 'FAIL soft_delete'; assert 'points_per_win' in src, 'FAIL scoring'; assert 'PARCIALMENTE IMPLEMENTADO' in src, 'FAIL status parcial'; assert 'INV-COMP-001' in src, 'FAIL INV-COMP-001 perdido'; print('PASS: INVARIANTS_COMPETITIONS INV-COMP-005+006+007 OK')"`
**Exit Code**: 1
**Timestamp UTC**: 2026-02-24T22:37:06.125554+00:00
**Behavior Hash**: 31a69f0866adc02ef8d2bb8f16c96a7707ace10b29f7b9281bffdb1ee8e01b1d
**Evidence File**: `docs/hbtrack/evidence/AR_073/executor_main.log`
**Python Version**: 3.11.9

### Execução Executor em c5f1ba8
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python -c "import pathlib; src=pathlib.Path('docs/hbtrack/modulos/competitions/INVARIANTS_COMPETITIONS.md').read_text(encoding='utf-8'); assert 'INV-COMP-005' in src, 'FAIL INV-COMP-005'; assert 'INV-COMP-006' in src, 'FAIL INV-COMP-006'; assert 'INV-COMP-007' in src, 'FAIL INV-COMP-007'; assert 'fk_competition_standings_team_id' in src, 'FAIL fk_team_id'; assert 'deleted_at' in src, 'FAIL soft_delete'; assert 'points_per_win' in src, 'FAIL scoring'; assert 'PARCIALMENTE IMPLEMENTADO' in src, 'FAIL status parcial'; assert 'INV-COMP-001' in src, 'FAIL INV-COMP-001 perdido'; print('PASS: INVARIANTS_COMPETITIONS INV-COMP-005+006+007 OK')"`
**Exit Code**: 0
**Timestamp UTC**: 2026-02-24T22:37:42.563049+00:00
**Behavior Hash**: 098e84230b85a2e32920a8ff415aab5505dbfae2081f8e025f64f6253671ef2a
**Evidence File**: `docs/hbtrack/evidence/AR_073/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em c5f1ba8
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_073_c5f1ba8/result.json`

### Selo Humano em c5f1ba8
**Status Humano**: ✅ VERIFICADO
**Timestamp UTC**: 2026-02-24T22:55:03.943434+00:00
**Motivo**: —
**TESTADOR_REPORT**: `_reports/testador/AR_073_c5f1ba8/result.json`
**Evidence File**: `docs/hbtrack/evidence/AR_073/executor_main.log`
