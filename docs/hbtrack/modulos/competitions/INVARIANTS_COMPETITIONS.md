# INVARIANTS_COMPETITIONS.md — Invariantes do Módulo Competitions

> Versão 2.0 — 30 invariantes (Reconstituído por Arquiteto, 2025-02-23).  
> Formato: SPEC YAML v1.0.  
> Categorias: BLOQUEANTE_TABELA (11), ANTI_INGESTÃO (5), NÃO_BLOQUEANTE (4), DB_CONSTRAINT (8), SERVICE (2).

---

## Sumário de Categorias

| Tier | Count | IDs |
|------|-------|-----|
| **DB_CONSTRAINT (Class A/B)** | 8 | 001-006, 007, 016 |
| **BLOQUEANTE_TABELA** | 11 | 012, 013, 017, 018, 019, 021, 024, 026, 027, 028, 009 |
| **ANTI_INGESTÃO** | 5 | 010, 011, 014, 023, 029 |
| **NÃO_BLOQUEANTE** | 4 | 020, 022, 025, 030 |
| **SERVICE (Class C1)** | 2 | 008, 015 |

---

## INV-COMP-001

```yaml
id: INV-COMP-001
class: A
tier: DB_CONSTRAINT
name: ck_competitions_status
rule: "status IN ('draft', 'active', 'finished', 'cancelled')"
table: competitions
constraint: ck_competitions_status
evidence: "Hb Track - Backend/app/models/competition.py:84"
status: IMPLEMENTADO
rationale: >
  Competição passa por ciclo de vida controlado.
  'cancelled' é estado terminal — sem transição de saída.
  Valores fora do domínio violam integridade do fluxo de torneio.
```

---

## INV-COMP-002

```yaml
id: INV-COMP-002
class: A
tier: DB_CONSTRAINT
name: ck_competitions_modality
rule: "modality IN ('masculino', 'feminino', 'misto')"
table: competitions
constraint: ck_competitions_modality
evidence: "Hb Track - Backend/app/models/competition.py:86"
status: IMPLEMENTADO
rationale: >
  Modalidade esportiva determina elegibilidade de atletas e conformidade com
  regulamentos da federação. Domínio fechado — extensões requerem migração.
```

---

## INV-COMP-003

```yaml
id: INV-COMP-003
class: A+B
tier: DB_CONSTRAINT
name: ck_competition_tables_soft_delete_pair
rule: >
  (deleted_at IS NULL AND deleted_reason IS NULL)
  OR
  (deleted_at IS NOT NULL AND deleted_reason IS NOT NULL)
tables:
  - competition_matches
  - competition_opponent_teams
  - competition_phases
  - match_events
  - match_roster
constraints:
  - ck_competition_matches_deleted_reason
  - ck_competition_opponent_teams_deleted_reason
  - ck_competition_phases_deleted_reason
  - ck_match_events_deleted_reason
  - ck_match_roster_deleted_reason
triggers:
  - trg_competition_matches_block_delete
  - trg_competition_opponent_teams_block_delete
  - trg_competition_phases_block_delete
  - trg_match_events_block_delete
  - trg_match_roster_block_delete
evidence: >
  Hb Track - Backend/db/alembic/versions/0055_comp_db_001_soft_delete_competition_tables.py
note: >
  Migration 0055 pendente de aplicação no DB local (Docker postgres:12 porta 5433).
  Triggers existem no arquivo de migração. VPS (postgres:15) tem migration aplicada.
status: IMPLEMENTADO
rationale: >
  Soft delete atômico — remoção física bloqueada por trigger.
  Razão (deleted_reason) obrigatória quando deleted_at preenchido.
  Garante auditabilidade e reversibilidade de exclusões em domínio de competição/scout.
```

---

## INV-COMP-004

```yaml
id: INV-COMP-004
class: A
tier: DB_CONSTRAINT
name: uq_competition_standings_comp_phase_opponent
rule: "UNIQUE (competition_id, phase_id, opponent_team_id) NULLS NOT DISTINCT"
table: competition_standings
constraint: uq_competition_standings_comp_phase_opponent
evidence: "Hb Track - Backend/app/models/competition_standing.py:71-73"
status: IMPLEMENTADO
rationale: >
  Classificação é única por equipe × fase dentro de uma competição.
  phase_id NULL representa classificação geral — permitida uma vez por equipe por
  competição (NULLS NOT DISTINCT garante unicidade mesmo com NULL).
  competition_standings NÃO tem trigger block_delete por design (exclusão física permitida).
```

---

## INV-COMP-005

```yaml
id: INV-COMP-005
class: A
tier: DB_CONSTRAINT
name: fk_competition_standings_team_id
rule: "competition_standings.team_id REFERENCES teams(id) ON DELETE SET NULL"
table: competition_standings
constraint: fk_competition_standings_team_id
evidence: "Hb Track - Backend/docs/_generated/schema.sql:6039"
status: IMPLEMENTADO
rationale: >
  Classificação de competição referencia equipe adversária (opponent team).
  ON DELETE SET NULL permite preservar histórico de standings mesmo quando equipe é excluída.
  Mantém integridade referencial sem causar cascata de exclusões em histórico de competições.
```

---

## INV-COMP-006

```yaml
id: INV-COMP-006
class: A+B
tier: DB_CONSTRAINT
name: soft_delete_comp_db_001
rule: >
  (deleted_at IS NULL AND deleted_reason IS NULL)
  OR
  (deleted_at IS NOT NULL AND deleted_reason IS NOT NULL)
tables:
  - competitions
  - competition_matches
  - competition_standings
  - competition_match_events
  - match_rosters
constraints:
  - ck_soft_delete_competitions
  - ck_soft_delete_competition_matches
  - ck_soft_delete_competition_standings
  - ck_soft_delete_competition_match_events
  - ck_soft_delete_match_rosters
evidence: "Migration 0055 (AR_008): Hb Track - Backend/db/alembic/versions/0055_comp_db_001_soft_delete_competition_tables.py"
status: IMPLEMENTADO
rationale: >
  Soft delete padronizado para 5 tabelas do módulo competitions (COMP-DB-001).
  deleted_at e deleted_reason devem ser preenchidos atomicamente.
  Garante auditabilidade e reversibilidade de exclusões lógicas em domínio de competição.
  Triggers de bloqueio de DELETE físico aplicados nas 5 tabelas.
```

---

## INV-COMP-007

```yaml
id: INV-COMP-007
class: A
tier: DB_CONSTRAINT
name: scoring_rules_competitions
rule: "points_per_win INTEGER NOT NULL DEFAULT 2; points_per_draw e points_per_loss (PENDENTES AR_036)"
table: competitions
evidence: "Hb Track - Backend/docs/ssot/schema.sql:994"
status: PARCIALMENTE IMPLEMENTADO
note: >
  AR_036 pendente para adicionar points_per_draw e points_per_loss em competitions.
  AR_080 pendente para adicionar NOT NULL em points_per_win.
  Atualmente points_per_win é NULLABLE com DEFAULT 2 (gap).
rationale: >
  Regras de pontuação determinam campeão de torneio.
  points_per_win DEFAULT 2 segue convenção handball padrão.
  NOT NULL garante que toda competição tem pontuação definida.
```

---

## INV-COMP-008

```yaml
id: INV-COMP-008
class: C1
tier: SERVICE
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

---

## INV-COMP-009

```yaml
id: INV-COMP-009
class: A
tier: BLOQUEANTE_TABELA
name: uq_competition_name_per_org
rule: "UNIQUE (organization_id, name, season)"
table: competitions
constraint: uq_competitions_org_name_season
evidence: PENDENTE
status: PENDENTE
rationale: >
  Não pode existir duas competições com mesmo nome+temporada dentro de uma organização.
  Evita duplicidade de torneios e confusão de dados históricos.
  Constraint garante integridade a nível de DB antes de qualquer validação de service.
```

---

## INV-COMP-010

```yaml
id: INV-COMP-010
class: D
tier: ANTI_INGESTÃO
name: athlete_in_match_roster_requires_team_link
rule: >
  Atleta escalado em match_roster DEVE ter link ativo com team_id da partida.
  INSERT em match_roster com athlete sem vínculo ativo com o time DEVE falhar.
table: match_roster
fk_check: "athlete_id → athletes → team_athletes → team_id"
evidence: PENDENTE
status: PENDENTE
note: >
  Pendência de workflow: requer JOIN validation ou trigger.
  Atleta pode existir no sistema mas não estar vinculado ao time da partida.
rationale: >
  Impede escalação de atletas que não pertencem ao time.
  Garante integridade do elenco e conformidade com regulamentos de competição.
```

---

## INV-COMP-011

```yaml
id: INV-COMP-011
class: A
tier: ANTI_INGESTÃO
name: uq_opponent_team_per_competition_canonical
rule: >
  UNIQUE (competition_id, canonical_name) com canonical_name = normalize(name).
  Aliases não duplicam entidade — diferentes grafias mapeiam para mesmo opponent_team.
table: competition_opponent_teams
constraint: uq_opponent_canonical
evidence: PENDENTE
status: PENDENTE
note: >
  canonical_name é computed column ou trigger que normaliza (lowercase, trim, unaccent).
  Aliases como "São Paulo FC", "SAO PAULO", "Sao Paulo" convergem para mesma entidade.
rationale: >
  Evita duplicação de adversários por variação de grafia.
  IA de ingestão deve mapear aliases para entidade canônica existente.
```

---

## INV-COMP-012

```yaml
id: INV-COMP-012
class: C2
tier: BLOQUEANTE_TABELA
name: match_requires_resolved_teams_for_standings
rule: >
  Partida com status='draft' ou home_team_id IS NULL ou away_team_id IS NULL
  MUST NOT ser incluída no cálculo de standings.
  Service DEVE filtrar: WHERE status != 'draft' AND home_team_id IS NOT NULL AND away_team_id IS NOT NULL.
table: competition_matches
service: CompetitionStandingsService
evidence: PENDENTE
status: PENDENTE
rationale: >
  Partidas incompletas corrompem classificação.
  Rascunhos são workspace do usuário — não afetam tabela oficial.
  Equipes indefinidas (TBD/placeholder) não geram pontos.
```

---

## INV-COMP-013

```yaml
id: INV-COMP-013
class: C1
tier: BLOQUEANTE_TABELA
name: scoring_tiebreaker_rules_required
rule: >
  Competição DEVE ter regras de desempate definidas para gerar classificação válida.
  Mínimo: (1) total de pontos, (2) saldo de gols, (3) gols marcados.
  Regras adicionais (confronto direto, carões) são opcionais.
table: competitions
columns:
  - tiebreaker_rules (JSONB ou colunas específicas)
evidence: PENDENTE
status: PENDENTE
rationale: >
  Empate de pontos é comum em torneios de handebol.
  Sem critério de desempate, classificação fica indefinida.
  Regulamento da federação exige critérios explícitos.
```

---

## INV-COMP-014

```yaml
id: INV-COMP-014
class: A
tier: ANTI_INGESTÃO
name: uq_external_reference_per_competition
rule: "UNIQUE (competition_id, external_reference)"
table: competition_matches
constraint: uq_match_external_ref
evidence: PENDENTE
status: PENDENTE
note: >
  external_reference é ID de súmula/documento externo (CBHb, federação estadual, etc.).
  Deduplicação por referência externa evita importação duplicada da mesma partida.
rationale: >
  Ingestão de dados externos (PDF, API federação) deve ser idempotente.
  Mesma súmula importada 2x não cria 2 partidas.
```

---

## INV-COMP-015

```yaml
id: INV-COMP-015
class: C1
tier: SERVICE
name: standings_calculation_idempotent
rule: >
  Chamar recalculate_standings(competition_id) N vezes produz mesmo resultado.
  Service DEVE ser idempotente — sem side effects cumulativos.
evidence: PENDENTE
status: PENDENTE
rationale: >
  Recálculo pode ser triggado por múltiplos eventos (nova partida, edição, rollback).
  Resultado deve ser determinístico e estável independente de quantas vezes é chamado.
```

---

## INV-COMP-016

```yaml
id: INV-COMP-016
class: A
tier: DB_CONSTRAINT
name: ck_match_score_valid
rule: "home_score >= 0 AND away_score >= 0"
table: competition_matches
constraint: ck_match_score_valid
evidence: PENDENTE
status: PENDENTE
rationale: >
  Placar de handebol não pode ser negativo.
  Constraint de DB garante integridade antes de qualquer validação de aplicação.
```

---

## INV-COMP-017

```yaml
id: INV-COMP-017
class: C2
tier: BLOQUEANTE_TABELA
name: match_counted_once
rule: >
  Cada partida contribui exatamente 1x para standings de cada equipe.
  Double-counting corrompe classificação.
  Service DEVE usar DISTINCT ou LEFT JOIN apropriado.
table: competition_standings
service: CompetitionStandingsService
evidence: PENDENTE
status: PENDENTE
rationale: >
  Bug comum em sistemas de classificação é contar partida múltiplas vezes.
  Invariante garante integridade do cálculo.
```

---

## INV-COMP-018

```yaml
id: INV-COMP-018
class: A
tier: BLOQUEANTE_TABELA
name: ck_match_different_teams
rule: "home_team_id != away_team_id OR (home_team_id IS NULL AND away_team_id IS NULL)"
table: competition_matches
constraint: ck_match_different_teams
evidence: PENDENTE
status: PENDENTE
rationale: >
  Time não joga contra si mesmo.
  Exceção: ambos NULL em partida draft/placeholder.
```

---

## INV-COMP-019

```yaml
id: INV-COMP-019
class: C2
tier: BLOQUEANTE_TABELA
name: standings_respects_scope
rule: >
  Standings com phase_id NOT NULL DEVE usar apenas partidas WHERE phase_id = X.
  Standings com phase_id IS NULL (geral) usa todas as partidas da competição.
  Escopo mal definido corrompe classificação por fase/grupo.
table: competition_standings
service: CompetitionStandingsService
evidence: PENDENTE
status: PENDENTE
rationale: >
  Competições de handebol têm fases (grupos, eliminatórias).
  Classificação por fase deve isolar partidas daquela fase.
```

---

## INV-COMP-020

```yaml
id: INV-COMP-020
class: C1
tier: NÃO_BLOQUEANTE
name: goals_association_consistency
rule: >
  Soma de gols em match_events WHERE event_type='goal' DEVE igualar score do match.
  Inconsistência é warning, não bloqueio — permite correção posterior.
tables:
  - competition_matches (home_score, away_score)
  - match_events (event_type='goal', team_id)
evidence: PENDENTE
status: PENDENTE
rationale: >
  Scout detalhado (quem fez gol) deve bater com placar.
  Inconsistência indica erro de digitação, não invalida partida.
```

---

## INV-COMP-021

```yaml
id: INV-COMP-021
class: C1
tier: BLOQUEANTE_TABELA
name: minimal_state_for_standings
rule: >
  Para gerar standings, partida DEVE ter:
  (1) home_team_id NOT NULL
  (2) away_team_id NOT NULL
  (3) home_score NOT NULL
  (4) away_score NOT NULL
  (5) status IN ('finished', 'official')
  Partidas incompletas são ignoradas no cálculo.
table: competition_matches
evidence: PENDENTE
status: PENDENTE
rationale: >
  Estado mínimo garante que apenas partidas finalizadas afetam classificação.
  Partidas em andamento ou rascunho não contam.
```

---

## INV-COMP-022

```yaml
id: INV-COMP-022
class: C1
tier: NÃO_BLOQUEANTE
name: standings_not_dependent_on_document
rule: >
  Standings DEVE ser calculado a partir de dados estruturados (competition_matches).
  Documento fonte (súmula PDF) é referência, não fonte de cálculo.
  Se súmula e dados estruturados divergem, dados estruturados prevalecem.
evidence: PENDENTE
status: PENDENTE
rationale: >
  Súmula é documento de entrada, não SSOT.
  Após ingestão, dados estruturados são canônicos.
  Evita reprocessamento de PDF para cada recálculo.
```

---

## INV-COMP-023

```yaml
id: INV-COMP-023
class: D
tier: ANTI_INGESTÃO
name: ai_never_auto_creates_entity
rule: >
  IA de ingestão MUST NOT criar competition, team ou athlete automaticamente.
  IA DEVE mapear para entidades existentes ou retornar PENDING_REVIEW.
  Criação de entidades requer confirmação humana.
service: IngestaoService
evidence: PENDENTE
status: PENDENTE
rationale: >
  Auto-criação de entidades gera duplicidades e dados órfãos.
  Humano valida se entidade nova é necessária ou se é alias de existente.
```

---

## INV-COMP-024

```yaml
id: INV-COMP-024
class: C1
tier: BLOQUEANTE_TABELA
name: deterministic_standings_calculation
rule: >
  Dado mesmo conjunto de partidas, standings DEVE produzir mesma ordem.
  Não pode haver randomização ou dependência de ordem de inserção.
  Critérios de desempate DEVEM ser aplicados consistentemente.
service: CompetitionStandingsService
evidence: PENDENTE
status: PENDENTE
rationale: >
  Classificação não pode mudar sem mudança de dados.
  Determinismo é requisito para auditoria e reprodutibilidade.
```

---

## INV-COMP-025

```yaml
id: INV-COMP-025
class: C1
tier: NÃO_BLOQUEANTE
name: metadata_edit_no_standings_change
rule: >
  Edição de metadados de partida (local, árbitro, observações) NÃO DEVE
  triggerar recálculo de standings nem alterar classificação.
  Apenas edição de score, teams ou status afeta standings.
service: CompetitionMatchService
evidence: PENDENTE
status: PENDENTE
rationale: >
  Metadados são informativos, não computacionais.
  Evita recálculos desnecessários e efeitos colaterais inesperados.
```

---

## INV-COMP-026

```yaml
id: INV-COMP-026
class: C2
tier: BLOQUEANTE_TABELA
name: invalid_match_explicitly_excluded
rule: >
  Partidas com status='cancelled' ou status='suspended' DEVEM ser
  explicitamente excluídas do cálculo de standings.
  Service DEVE ter filtro: WHERE status NOT IN ('cancelled', 'suspended', 'draft').
table: competition_matches
service: CompetitionStandingsService
evidence: PENDENTE
status: PENDENTE
rationale: >
  Partidas canceladas não geram pontos.
  Partidas suspensas podem ser retomadas — não contam até finalização.
```

---

## INV-COMP-027

```yaml
id: INV-COMP-027
class: C2
tier: BLOQUEANTE_TABELA
name: standings_teams_canonical
rule: >
  Standings DEVE usar opponent_team_id canônico, não aliases.
  Se partida tem alias de team, resolver para ID canônico antes de agregar.
  Mesma equipe não pode aparecer 2x no standings com IDs diferentes.
table: competition_standings
service: CompetitionStandingsService
evidence: PENDENTE
status: PENDENTE
rationale: >
  Aliases de equipes (variações de nome) devem convergir para única entrada.
  Duplicação de equipe no standings invalida classificação.
```

---

## INV-COMP-028

```yaml
id: INV-COMP-028
class: C1
tier: BLOQUEANTE_TABELA
name: scoring_rules_explicit
rule: >
  Cálculo de pontos DEVE usar regras explícitas da competição.
  PROIBIDO assumir 2/1/0 como default universal.
  Se competition.points_per_win IS NULL, standings não pode ser calculado — retorna erro.
table: competitions
service: CompetitionStandingsService
evidence: PENDENTE
status: PENDENTE
rationale: >
  Regras de pontuação variam por regulamento.
  Assumir default pode gerar classificação incorreta.
```

---

## INV-COMP-029

```yaml
id: INV-COMP-029
class: D
tier: ANTI_INGESTÃO
name: ai_prioritizes_current_competition
rule: >
  IA de ingestão DEVE priorizar mapeamento para competição atualmente ativa.
  Se múltiplas competições têm nome similar, usar context (data, organização) para desambiguar.
  Não criar nova competição se existe competição ativa com mesmo nome na mesma org.
service: IngestaoService
evidence: PENDENTE
status: PENDENTE
rationale: >
  Evita fragmentação de dados entre competições duplicadas.
  Contexto temporal e organizacional ajuda IA a escolher corretamente.
```

---

## INV-COMP-030

```yaml
id: INV-COMP-030
class: E
tier: NÃO_BLOQUEANTE
name: ux_minimal_actions
rule: >
  Para operações frequentes (registrar resultado, escalar atleta), UX DEVE
  requerer no máximo 3 cliques/ações do usuário.
  Workflows complexos (criar competição, definir regras) podem ter mais passos.
evidence: PENDENTE
status: PENDENTE
rationale: >
  Usuário principal (treinador) opera em contexto de jogo — precisa de agilidade.
  UX bloat causa abandono de registro de dados.
```

---

## Changelog

| Versão | Data | Alteração |
|--------|------|-----------|
| 1.0 | 2025-02-22 | 8 invariantes iniciais (AR_048) |
| 2.0 | 2025-02-23 | Expansão para 30 invariantes (Arquiteto reconstituição) |

