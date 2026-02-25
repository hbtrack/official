# AR_000 — Documentar INV-COMP-008 (Motor de Calculo Dinamico) em INVARIANTS_COMPETITIONS.md

**Status**: 🏗️ EM_EXECUCAO
**Versão do Protocolo**: 1.3.0

## Descrição
APPEND de INV-COMP-008 ao final de docs/hbtrack/modulos/competitions/INVARIANTS_COMPETITIONS.md (NAO sobrescrever INV-COMP-001 a 007). Formato SPEC YAML v1.0 identico ao padrao do arquivo. O conteudo completo da invariante esta no campo notes desta task.

## Critérios de Aceite
1) INVARIANTS_COMPETITIONS.md contem INV-COMP-008.
2) INV-COMP-008 referencia dynamic_scoring_rules e MUST NOT hardcoded.
3) INV-COMP-008 referencia competition.py:124-128 como evidence.
4) INV-COMP-001 a 007 preservados (nao modificados).
5) validation_command passa com exit_code=0.

## Validation Command (Contrato)
```
python -c "import pathlib; src=pathlib.Path('docs/hbtrack/modulos/competitions/INVARIANTS_COMPETITIONS.md').read_text(encoding='utf-8'); assert 'INV-COMP-008' in src,'FAIL: INV-COMP-008 not found'; assert 'dynamic_scoring_rules' in src,'FAIL: name not found'; assert 'MUST NOT' in src,'FAIL: MUST NOT not found'; assert 'hardcoded' in src,'FAIL: hardcoded keyword not found'; assert 'competition.py:124' in src,'FAIL: evidence anchor not found'; assert 'INV-COMP-007' in src,'FAIL: INV-COMP-007 lost'; assert 'INV-COMP-001' in src,'FAIL: INV-COMP-001 lost'; print('PASS: INV-COMP-008 appended OK - dynamic_scoring_rules documented')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_000/executor_main.log`

## Notas do Arquiteto
Conteudo a appendar verbatim (SPEC YAML v1.0):

## INV-COMP-008

```yaml
id: INV-COMP-008
class: C1
name: dynamic_scoring_rules
rule: >
  CompetitionStandingsService MUST carregar points_per_win, points_per_draw e
  points_per_loss da competition.id especifica (SELECT da tabela competitions).
  O service MUST NOT conter valores de pontuacao hardcoded ou DEFAULT constants.
  Regulamentos variam por competicao: 2/1/0 e padrao handebol, mas configuravel.
table: competitions
columns:
  - points_per_win (INTEGER DEFAULT 2)
  - points_per_draw (INTEGER DEFAULT 1)
  - points_per_loss (INTEGER DEFAULT 0)
evidence: >
  Hb Track - Backend/app/models/competition.py:124-128 (AR_036 VERIFICADO)
status: PENDENTE
note: >
  AR_076 implementa CompetitionStandingsService respeitando esta invariante.
  compute_points(wins, draws, losses, ppw, ppd, ppl) aceita parametros — sem defaults hardcoded.
  recalculate_standings le ppw/ppd/ppl via SELECT competition WHERE id=competition_id.
rationale: >
  Handebol nao tem pontuacao universal: competicoes regionais, nacionais e internacionais
  podem usar 2/1/0, 3/1/0 ou outros esquemas por regulamento da federacao.
  Logica hardcoded no service violaria o principio de configuracao por regulamento
  e criaria divergencia silenciosa quando competicoes usam esquema nao-padrao.
```

## Análise de Impacto

**Executor**: 2026-02-25

**Escopo**: Documentação pura - APPEND de INV-COMP-008 em INVARIANTS_COMPETITIONS.md.

**Impacto Técnico**:
- ✅ Arquivo fora dos governed roots (documentação de módulo)
- ✅ APPEND apenas - preserva INV-COMP-001 a 007 intactos
- ✅ Formato YAML v1.0 compatível com estrutura existente

**Conteúdo da Invariante**:
- **id**: INV-COMP-008
- **class**: C1 (Service Layer Invariant)
- **name**: dynamic_scoring_rules
- **rule**: CompetitionStandingsService MUST carregar ppw/ppd/ppl da competition específica (SELECT do banco), MUST NOT usar valores hardcoded
- **evidence**: competition.py:124-128 (AR_036 VERIFICADO)

**Riscos**:
- **BAIXO**: Documentação não afeta código em produção
- **BAIXO**: INV-COMP-008 documenta regra a ser implementada na AR_076

**Dependências**:
- AR_036 VERIFICADO: competitions tem points_per_win/draw/loss no banco
- AR_076 PENDENTE: Implementação do CompetitionStandingsService respeitando esta invariante

**Validação**:
- validation_command verifica 7 keywords: INV-COMP-008, dynamic_scoring_rules, MUST NOT, hardcoded, competition.py:124, INV-COMP-001, INV-COMP-007
- Confirma que invariantes anteriores não foram perdidas

---
## Carimbo de Execução
_(Gerado por hb report)_


### Execução Executor em 6210f7f
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python -c "import pathlib; src=pathlib.Path('docs/hbtrack/modulos/competitions/INVARIANTS_COMPETITIONS.md').read_text(encoding='utf-8'); assert 'INV-COMP-008' in src,'FAIL: INV-COMP-008 not found'; assert 'dynamic_scoring_rules' in src,'FAIL: name not found'; assert 'MUST NOT' in src,'FAIL: MUST NOT not found'; assert 'hardcoded' in src,'FAIL: hardcoded keyword not found'; assert 'competition.py:124' in src,'FAIL: evidence anchor not found'; assert 'INV-COMP-007' in src,'FAIL: INV-COMP-007 lost'; assert 'INV-COMP-001' in src,'FAIL: INV-COMP-001 lost'; print('PASS: INV-COMP-008 appended OK - dynamic_scoring_rules documented')"`
**Exit Code**: 0
**Timestamp UTC**: 2026-02-25T01:34:35.305353+00:00
**Behavior Hash**: ff651fcec2efffda24e1e00841b86379fd2bc8bbe1d4ae51e2e137435a161be8
**Evidence File**: `docs/hbtrack/evidence/AR_000/executor_main.log`
**Python Version**: 3.11.9

