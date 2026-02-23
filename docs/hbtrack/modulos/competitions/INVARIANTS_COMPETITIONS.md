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
