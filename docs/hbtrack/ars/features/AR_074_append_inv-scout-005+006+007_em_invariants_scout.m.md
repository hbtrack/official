# AR_074 — Append INV-SCOUT-005+006+007 em INVARIANTS_SCOUT.md

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.3.0

## Descrição
APPEND 3 invariantes ao arquivo docs/hbtrack/modulos/scout/INVARIANTS_SCOUT.md (continuando INV-SCOUT-001 a INV-SCOUT-004 existentes). Usar formato SPEC YAML v1.0 (idem INV-SCOUT-001 a 004).

INV-SCOUT-005 (class C1 - Servico puro): Goleira Obrigatoria (ID=5)
- match_roster deve ter ao menos 1 jogador com defensive_position_id=5 (Goleira). RD13: ID=5 e Goleira.
- Evidence: schema.sql COMMENT ON TABLE defensive_positions (RD13); is_goalkeeper boolean em match_roster (schema.sql:1514)
- Status: PENDENTE DE MIGRACAO (sem trigger/check no schema - apenas convencao de dado)

INV-SCOUT-006 (class C2 - Servico + DB): RP10 - is_available Gate
- Atleta so pode ser inserido no match_roster se is_available=true em team_registration para a data da partida.
- Evidence: is_available boolean em team_registrations
- Status: PARCIALMENTE IMPLEMENTADO (campo existe, gate no servico a verificar)

INV-SCOUT-007 (class A+B - Constraint + Trigger): Imutabilidade de match_events
- Eventos de scout (match_events) sao imutaveis apos criacao - UPDATE/DELETE bloqueados por trigger de auditoria.
- Evidence: schema.sql (trigger de protecao em match_events)
- Status: IMPLEMENTADO

ATENCAO: APPEND ao final do arquivo existente - NAO sobrescrever INV-SCOUT-001 a 004.

## Critérios de Aceite
1. docs/hbtrack/modulos/scout/INVARIANTS_SCOUT.md contem INV-SCOUT-005, INV-SCOUT-006 e INV-SCOUT-007.
2. INV-SCOUT-005 referencia is_goalkeeper + status PENDENTE DE MIGRACAO.
3. INV-SCOUT-006 referencia is_available.
4. INV-SCOUT-007 documenta imutabilidade de match_events.
5. INV-SCOUT-001 a 004 preservados (nao modificados).

## Validation Command (Contrato)
```
python -c "import pathlib; src=pathlib.Path('docs/hbtrack/modulos/scout/INVARIANTS_SCOUT.md').read_text(encoding='utf-8'); assert 'INV-SCOUT-005' in src, 'FAIL INV-SCOUT-005'; assert 'INV-SCOUT-006' in src, 'FAIL INV-SCOUT-006'; assert 'INV-SCOUT-007' in src, 'FAIL INV-SCOUT-007'; assert 'is_goalkeeper' in src, 'FAIL goalkeeper'; assert 'is_available' in src, 'FAIL is_available'; assert 'PENDENTE' in src, 'FAIL status pendente'; assert 'INV-SCOUT-001' in src, 'FAIL INV-SCOUT-001 perdido'; print('PASS: INVARIANTS_SCOUT INV-SCOUT-005+006+007 OK')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_074/executor_main.log`

## Notas do Arquiteto
INV-SCOUT-005 marcada PENDENTE DE MIGRACAO: nao ha trigger/check no schema para goleira obrigatoria - apenas is_goalkeeper boolean como convencao de dado.

## Análise de Impacto
**Executor**: 2026-02-24

**Escopo**: Documentação pura - APPEND 3 invariantes em INVARIANTS_SCOUT.md existente.

**Riscos**:
- **BAIXO**: Apenas append de texto em arquivo .md fora dos governed roots.
- **BAIXO**: Validação verifica presença de INV-SCOUT-001 para garantir que arquivo existente não foi sobrescrito.

**Dependências**:
- Arquivo base: `docs/hbtrack/modulos/scout/INVARIANTS_SCOUT.md` (existe desde AR_048)
- Formato: SPEC YAML v1.0 (padrão existente INV-SCOUT-001 a 004)

**Patch**:
- 1 arquivo modificado: append ~60 linhas no final

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução Executor em c5f1ba8
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python -c "import pathlib; src=pathlib.Path('docs/hbtrack/modulos/scout/INVARIANTS_SCOUT.md').read_text(encoding='utf-8'); assert 'INV-SCOUT-005' in src, 'FAIL INV-SCOUT-005'; assert 'INV-SCOUT-006' in src, 'FAIL INV-SCOUT-006'; assert 'INV-SCOUT-007' in src, 'FAIL INV-SCOUT-007'; assert 'is_goalkeeper' in src, 'FAIL goalkeeper'; assert 'is_available' in src, 'FAIL is_available'; assert 'PENDENTE' in src, 'FAIL status pendente'; assert 'INV-SCOUT-001' in src, 'FAIL INV-SCOUT-001 perdido'; print('PASS: INVARIANTS_SCOUT INV-SCOUT-005+006+007 OK')"`
**Exit Code**: 0
**Timestamp UTC**: 2026-02-24T22:39:31.786519+00:00
**Behavior Hash**: e448793353c790d34f3828b178b628c705e167a53fdbfc9bdc415cea29f522dd
**Evidence File**: `docs/hbtrack/evidence/AR_074/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em c5f1ba8
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_074_c5f1ba8/result.json`

### Selo Humano em c5f1ba8
**Status Humano**: ✅ VERIFICADO
**Timestamp UTC**: 2026-02-24T22:55:05.433512+00:00
**Motivo**: —
**TESTADOR_REPORT**: `_reports/testador/AR_074_c5f1ba8/result.json`
**Evidence File**: `docs/hbtrack/evidence/AR_074/executor_main.log`
