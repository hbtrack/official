# AR_074 — Append INV-SCOUT-005+006+007 em INVARIANTS_SCOUT.md

**Status**: 🔲 PENDENTE
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
_(A ser preenchido pelo Executor)_

---
## Carimbo de Execução
_(Gerado por hb report)_

