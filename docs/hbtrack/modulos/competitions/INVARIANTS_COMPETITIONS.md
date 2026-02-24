# INVARIANTS_COMPETITIONS.md — Invariantes do Módulo Competitions

> Gerado por AR_048 (2026-02-22). Formato: SPEC YAML v1.0.

---

## INV-COMP-001

```yaml
id: INV-COMP-001
class: A
name: ck_competitions_status
rule: "status IN ('draft', 'active', 'finished', 'cancelled')"
table: competitions
constraint: ck_competitions_status
evidence: "Hb Track - Backend/app/models/competition.py:84"
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
name: ck_competitions_modality
rule: "modality IN ('masculino', 'feminino', 'misto')"
table: competitions
constraint: ck_competitions_modality
evidence: "Hb Track - Backend/app/models/competition.py:86"
rationale: >
  Modalidade esportiva determina elegibilidade de atletas e conformidade com
  regulamentos da federação. Domínio fechado — extensões requerem migração.
```

---

## INV-COMP-003

```yaml
id: INV-COMP-003
class: A+B
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
name: uq_competition_standings_comp_phase_opponent
rule: "UNIQUE (competition_id, phase_id, opponent_team_id) NULLS NOT DISTINCT"
table: competition_standings
constraint: uq_competition_standings_comp_phase_opponent
evidence: "Hb Track - Backend/app/models/competition_standing.py:71-73"
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
class: A
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
name: scoring_rules_competitions
rule: "points_per_win INTEGER DEFAULT 2; points_per_draw e points_per_loss (PENDENTES AR_036)"
table: competitions
evidence: "Hb Track - Backend/docs/_generated/schema.sql:994"
status: PARCIALMENTE IMPLEMENTADO
note: >
  AR_036 pendente para adicionar points_per_draw e points_per_loss em competitions.
  Atualmente apenas points_per_win está implementado com DEFAULT 2 (sistema handball padrão).
rationale: >
  Regras de pontuação determinam campeão de torneio.
  points_per_win DEFAULT 2 segue convenção handball padrão.
  Expansão para points_per_draw e points_per_loss aguarda AR_036 para cobrir modalidades
  com empates e penalizações específicas.
```
