# AR_049 — Criar INVARIANTS_SCOUT.md (INV-SCOUT-001 a INV-SCOUT-004)

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.1.0

## Descrição
CONTEXTO: As invariantes do módulo Scout (match_events) existem no código mas não em arquivo canônico de invariantes. Esta AR documenta as 4 principais invariantes observadas na auditoria.

AÇÃO: Criar o arquivo docs/hbtrack/modulos/scout/INVARIANTS_SCOUT.md com 4 blocos de invariante.

INV-SCOUT-001 (Classe A — DB constraint):
  id: INV-SCOUT-001
  name: ck_match_events_source
  rule: source IN ('live', 'video', 'post_game_correction')
  table: match_events
  constraint: ck_match_events_source
  evidence: Hb Track - Backend/app/models/match_event.py:55
  rationale: Rastreabilidade da origem do dado. 'post_game_correction' requer auditoria extra.

INV-SCOUT-002 (Classe A — DB constraint):
  id: INV-SCOUT-002
  name: ck_match_events_period
  rule: period_number >= 1
  table: match_events
  constraint: ck_match_events_period
  evidence: Hb Track - Backend/app/models/match_event.py:52
  rationale: Períodos de handebol são numerados a partir de 1 (1=1T, 2=2T, 3=prorrogação).

INV-SCOUT-003 (Classe A — DB constraint dupla):
  id: INV-SCOUT-003
  name: ck_match_events_coords
  rule: (x_coord IS NULL OR x_coord BETWEEN 0 AND 100) AND (y_coord IS NULL OR y_coord BETWEEN 0 AND 100)
  table: match_events
  constraints: ck_match_events_x_coord, ck_match_events_y_coord
  evidence: Hb Track - Backend/app/models/match_event.py:57-58
  rationale: Coordenadas representam posição normalizada no campo (0-100%). NULL = evento sem posição (ex: substituição).

INV-SCOUT-004 (Classe C1 — serviço Pydantic):
  id: INV-SCOUT-004
  name: goalkeeper_save_requires_related_event
  rule: WHEN event_type = 'goalkeeper_save' THEN related_event_id IS NOT NULL
  layer: Pydantic validator (app/schemas/match_events.py, ScoutEventCreate)
  evidence: Hb Track - Backend/app/schemas/match_events.py (ScoutEventCreate validator)
  rationale: Defesa de goleiro é sempre relacionada a um chute anterior. Sem related_event_id, o evento fica órfão analiticamente.

Criar também o diretório docs/hbtrack/modulos/scout/ se não existir.

## Critérios de Aceite
1) Arquivo docs/hbtrack/modulos/scout/INVARIANTS_SCOUT.md existe. 2) Contém exatamente os blocos INV-SCOUT-001, INV-SCOUT-002, INV-SCOUT-003, INV-SCOUT-004. 3) Cada bloco tem campos: id, name, rule, evidence. 4) Arquivo tem mais de 400 bytes.

## Validation Command (Contrato)
```
python -c "import pathlib; p=pathlib.Path('docs/hbtrack/modulos/scout/INVARIANTS_SCOUT.md'); assert p.exists(), f'FAIL: {p} not found'; content=p.read_text(encoding='utf-8'); missing=[inv for inv in ['INV-SCOUT-001','INV-SCOUT-002','INV-SCOUT-003','INV-SCOUT-004'] if inv not in content]; assert not missing, f'FAIL: missing invariants: {missing}'; assert p.stat().st_size > 400, f'FAIL: file too small ({p.stat().st_size} bytes)'; print(f'PASS: INVARIANTS_SCOUT.md exists with all 4 INVs ({p.stat().st_size} bytes)')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_049_invariants_scout.log`

## Notas do Arquiteto
INV-SCOUT-004 é Classe C1 (validador de serviço Pydantic) — não tem constraint de DB correspondente. Documentar explicitamente a camada onde a invariante vive.

## Riscos
- INV-SCOUT-004 valida apenas no nível Pydantic — INSERT direto no banco não passa pelo validator. Documentar como gap known e potencial INV Classe B futura (trigger no DB).

## Análise de Impacto
**Executor**: Claude Sonnet 4.6 (Modo Executor)
**Data**: 2026-02-22

**Escopo**: Criação de `docs/hbtrack/modulos/scout/INVARIANTS_SCOUT.md` com 4 invariantes (INV-SCOUT-001 a INV-SCOUT-004), classes A e C1. INV-SCOUT-004 documentada como gap conhecido (C1 Pydantic only — sem trigger de DB correspondente).

**Impacto**: Documentação — nenhum arquivo de produto ou schema alterado.

---
## Carimbo de Execução
_(Gerado por hb report)_


### Execução em b2e7523
**Status Final**: ✅ SUCESSO
**Comando**: `python -c "import pathlib; p=pathlib.Path('docs/hbtrack/modulos/scout/INVARIANTS_SCOUT.md'); assert p.exists(), f'FAIL: {p} not found'; content=p.read_text(encoding='utf-8'); missing=[inv for inv in ['INV-SCOUT-001','INV-SCOUT-002','INV-SCOUT-003','INV-SCOUT-004'] if inv not in content]; assert not missing, f'FAIL: missing invariants: {missing}'; assert p.stat().st_size > 400, f'FAIL: file too small ({p.stat().st_size} bytes)'; print(f'PASS: INVARIANTS_SCOUT.md exists with all 4 INVs ({p.stat().st_size} bytes)')"`
**Exit Code**: 0
**Evidence File**: `docs/hbtrack/evidence/AR_049_invariants_scout.log`
**Python Version**: 3.11.9


### Verificacao Testador em b2e7523
**Status Testador**: ✅ VERIFICADO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_049_b2e7523/result.json`

### Verificacao Testador em b2e7523
**Status Testador**: ✅ VERIFICADO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_049_b2e7523/result.json`
