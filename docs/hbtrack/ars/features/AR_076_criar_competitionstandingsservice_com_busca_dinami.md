# AR_076 — Criar CompetitionStandingsService com busca dinamica de regras de pontuacao (INV-COMP-008)

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.3.0

## Descrição
Criar Hb Track - Backend/app/services/competition_standings_service.py contendo a classe CompetitionStandingsService.

REGRA MANDATORIA (INV-COMP-008): O service MUST NOT definir constantes de pontuacao. Valores ppw/ppd/ppl SAO SEMPRE lidos do banco via SELECT na competition especifica.

Metodo 1 - ESTATICO compute_points:
  assinatura: compute_points(wins: int, draws: int, losses: int, points_per_win: int, points_per_draw: int, points_per_loss: int) -> int
  formula: wins * points_per_win + draws * points_per_draw + losses * points_per_loss
  SEM IO, SEM DB, SEM defaults hardcoded - apenas calculo puro, todos os parametros obrigatorios.
  docstring deve referenciar: INV-COMP-008: parametros de pontuacao SEMPRE fornecidos pelo caller (nunca hardcoded)
  docstring deve referenciar: INV-COMP-007 (competition.py:124-128: points_per_win DEFAULT 2 no DB)

Metodo 2 - ASSÍNCRONO recalculate_standings:
  assinatura: async recalculate_standings(self, competition_id: UUID, db: AsyncSession, phase_id: UUID | None = None) -> list[CompetitionStanding]
  1) SELECT competition WHERE id=competition_id AND deleted_at IS NULL
     - se nao encontrada: raise NotFoundError
     - le competition.points_per_win, competition.points_per_draw, competition.points_per_loss DO BANCO
     - MUST NOT usar valores DEFAULT, MUST NOT usar constantes MODULE-LEVEL
  2) SELECT competition_matches WHERE competition_id=? AND status=finished AND deleted_at IS NULL (INV-COMP-006)
     - se phase_id fornecido, filtra tambem por phase_id
  3) Agrega por opponent_team (home_team_id/away_team_id): wins, draws, losses, goals_for, goals_against
     - vitoria: home_score > away_score (home wins) ou away_score > home_score (away wins)
     - empate: home_score == away_score
     - NAO contar partidas onde score e NULL
  4) Para cada opponent_team: points = compute_points(wins, draws, losses, ppw, ppd, ppl) onde ppw/ppd/ppl vem do passo 1
  5) goal_difference = goals_for - goals_against
  6) Upserta competition_standings: atualiza points, played, wins, draws, losses, goals_for, goals_against, goal_difference
     - preserva team_id existente (NAO sobrescreve com NULL, INV-COMP-005)
  7) Ordena por points DESC, goal_difference DESC, goals_for DESC; atualiza position sequencialmente
  8) Retorna lista CompetitionStanding atualizada

Criar tambem Hb Track - Backend/tests/unit/test_competition_standings_service.py com classe TestCompetitionStandingsServiceComputePoints:
  test_three_match_scenario_default_handball_rules:
    Cenario round-robin 3 equipes, ppw=2, ppd=1, ppl=0 (passados explicitamente):
      M1: TeamA 3x1 TeamB -> A: wins=1; B: losses=1
      M2: TeamA 2x2 TeamC -> A: draws=1; C: draws=1
      M3: TeamB 4x0 TeamC -> B: wins=1; C: losses=1
    TeamA(W=1,D=1,L=0) -> 3pts; TeamB(W=1,D=0,L=1) -> 2pts; TeamC(W=0,D=1,L=1) -> 1pt
  test_dynamic_rules_isolation (INV-COMP-008):
    Mesmo scenario com ppw=3 (padrao futebol-like): TeamA(1W1D0L) = 4pts NAO 3pts
    Prova que compute_points usa o parametro recebido, nao um valor hardcoded
  test_compute_points_custom_rules: ppw=3, ppd=1, ppl=0 -> 1W1D0L = 4 (\!=3 com ppw=2)
  test_compute_points_all_wins: compute_points(5,0,0,2,1,0) == 10
  test_compute_points_zero_games: compute_points(0,0,0,2,1,0) == 0

## Critérios de Aceite
1) Arquivo Hb Track - Backend/app/services/competition_standings_service.py existe com classe CompetitionStandingsService.
2) compute_points e staticmethod puro sem IO e sem valores default nos parametros.
3) recalculate_standings le ppw/ppd/ppl DO BANCO via SELECT competition (NAO de constantes).
4) recalculate_standings filtra deleted_at IS NULL em competition_matches (INV-COMP-006).
5) recalculate_standings preserva team_id ao upsert (INV-COMP-005).
6) validation_command: round-robin OK (3/2/1) E ppw customizado (3) produz 4 \!= 3 (prova ausencia de hardcode).

## Write Scope
- Hb Track - Backend/app/services/competition_standings_service.py
- Hb Track - Backend/tests/unit/test_competition_standings_service.py

## Validation Command (Contrato)
```
python -c "import sys; sys.path.insert(0,'Hb Track - Backend'); from app.services.competition_standings_service import CompetitionStandingsService as CSS; a=CSS.compute_points(1,1,0,2,1,0); b=CSS.compute_points(1,0,1,2,1,0); c=CSS.compute_points(0,1,1,2,1,0); assert a==3,f'FAIL TeamA={a}\!=3'; assert b==2,f'FAIL TeamB={b}\!=2'; assert c==1,f'FAIL TeamC={c}\!=1'; dyn=CSS.compute_points(1,1,0,3,1,0); assert dyn==4,f'FAIL INV-COMP-008: ppw=3 deu {dyn}\!=4 (hardcoded ppw=2?)'; print(f'PASS: round-robin A={a} B={b} C={c} | INV-COMP-008 dynamic ppw=3->{dyn} OK')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_076/executor_main.log`

## Riscos
- CRITICO (INV-COMP-008): NAO definir DEFAULT_PPW/DEFAULT_PPD/DEFAULT_PPL no modulo - todo valor de pontuacao vem do banco
- competition_standings.points e INT - compute_points deve retornar int (nao float)
- recalculate_standings deve filtrar competition_matches com deleted_at IS NULL (INV-COMP-006)
- upsert em competition_standings deve preservar team_id existente (INV-COMP-005, FK SET NULL)

## Análise de Impacto

**Executor**: 2026-02-25

**Escopo**: Criar CompetitionStandingsService (novo service) + unit tests.

**Impacto Técnico**:
1. **Novo arquivo**: `Hb Track - Backend/app/services/competition_standings_service.py`
   - Classe `CompetitionStandingsService`
   - Método estático `compute_points()` (puro, sem IO)
   - Método async `recalculate_standings()` (busca ppw/ppd/ppl do banco)

2. **Novo arquivo de testes**: `Hb Track - Backend/tests/unit/test_competition_standings_service.py`
   - `TestCompetitionStandingsServiceComputePoints`
   - 5 test cases: round-robin, dynamic rules, custom rules, all wins, zero games

**Invariantes Respeitadas**:
- **INV-COMP-008** (NOVA): MUST NOT hardcoded scoring values → busca dinâmica do banco
- **INV-COMP-005**: Preserva team_id ao upsert standings (FK SET NULL)
- **INV-COMP-006**: Filtra deleted_at IS NULL em competition_matches

**Regra Mandatória (INV-COMP-008)**:
- ❌ **PROIBIDO**: Definir constantes DEFAULT_PPW/DEFAULT_PPD/DEFAULT_PPL
- ✅ **OBRIGATÓRIO**: `compute_points()` recebe ppw/ppd/ppl como parâmetros obrigatórios
- ✅ **OBRIGATÓRIO**: `recalculate_standings()` faz SELECT competition para buscar regras

**Validation Command (Antifrágil)**:
- Testa round-robin: TeamA(1W1D0L, ppw=2) → 3pts
- Testa regra customizada: TeamA(1W1D0L, ppw=3) → 4pts ≠ 3
- Se ppw fosse hardcoded=2, o assert dyn==4 falharia (prova de ausência de hardcode)

**Riscos Mitigados**:
- ✅ compute_points retorna int (competition_standings.points é INT)
- ✅ Sem defaults hardcoded (INV-COMP-008)
- ✅ recalculate_standings filtra deleted_at IS NULL (INV-COMP-006)
- ✅ Ups

ert preserva team_id existente (INV-COMP-005)

**Dependências**:
- AR_036 VERIFICADO: competitions tem points_per_win/draw/loss (DEFAULT 2/1/0)
- AR_000 (TASK 000): INV-COMP-008 documentada

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução Executor em 6210f7f
**Status Executor**: ❌ FALHA
**Comando**: `python -c "import sys; sys.path.insert(0,'Hb Track - Backend'); from app.services.competition_standings_service import CompetitionStandingsService as CSS; a=CSS.compute_points(1,1,0,2,1,0); b=CSS.compute_points(1,0,1,2,1,0); c=CSS.compute_points(0,1,1,2,1,0); assert a==3,f'FAIL TeamA={a}\!=3'; assert b==2,f'FAIL TeamB={b}\!=2'; assert c==1,f'FAIL TeamC={c}\!=1'; dyn=CSS.compute_points(1,1,0,3,1,0); assert dyn==4,f'FAIL INV-COMP-008: ppw=3 deu {dyn}\!=4 (hardcoded ppw=2?)'; print(f'PASS: round-robin A={a} B={b} C={c} | INV-COMP-008 dynamic ppw=3->{dyn} OK')"`
**Exit Code**: 1
**Timestamp UTC**: 2026-02-25T01:36:47.331123+00:00
**Behavior Hash**: bcd8b656edb10457c97661aa43eb7636b06f47db113f7de9f2ef082c11c7c9b6
**Evidence File**: `docs/hbtrack/evidence/AR_076/executor_main.log`
**Python Version**: 3.11.9

### Execução Executor em 6210f7f
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python -c "import sys; sys.path.insert(0,'Hb Track - Backend'); from app.services.competition_standings_service import CompetitionStandingsService as CSS; a=CSS.compute_points(1,1,0,2,1,0); b=CSS.compute_points(1,0,1,2,1,0); c=CSS.compute_points(0,1,1,2,1,0); assert a==3,f'FAIL TeamA={a}\!=3'; assert b==2,f'FAIL TeamB={b}\!=2'; assert c==1,f'FAIL TeamC={c}\!=1'; dyn=CSS.compute_points(1,1,0,3,1,0); assert dyn==4,f'FAIL INV-COMP-008: ppw=3 deu {dyn}\!=4 (hardcoded ppw=2?)'; print(f'PASS: round-robin A={a} B={b} C={c} | INV-COMP-008 dynamic ppw=3->{dyn} OK')"`
**Exit Code**: 0
**Timestamp UTC**: 2026-02-25T01:39:31.010089+00:00
**Behavior Hash**: 429a6e6be7f274f9e4768ba3405de27488010027f921984c97d53c9e6b6a0a33
**Evidence File**: `docs/hbtrack/evidence/AR_076/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em 6210f7f
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_076_6210f7f/result.json`

### Selo Humano em 6643f97
**Status Humano**: ✅ VERIFICADO
**Timestamp UTC**: 2026-02-25T01:58:35.544630+00:00
**Motivo**: CompetitionStandingsService implementado com dynamic scoring (INV-COMP-008)
**TESTADOR_REPORT**: `_reports/testador/AR_076_6210f7f/result.json`
**Evidence File**: `docs/hbtrack/evidence/AR_076/executor_main.log`
