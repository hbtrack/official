---
id: DOMAIN_MODEL
doc_mode: REFERENCE
status: CANONICAL
---

# HB Track — Domain Model

## Entity graph (high-level)

```
Person (root identity)
├── User (1:1, auth credentials)
│   └── OrgMembership (1:N)
│       ├── Organization
│       ├── Role → RolePermission → Permission
│       └── Season
├── Athlete (1:1, sports identity)
│   ├── TeamRegistration (1:N) → Team
│   ├── AthleteState (state machine: ativa/dispensada/arquivada)
│   └── Positions (offensive/defensive)
├── PersonContact (1:N)
├── PersonAddress (1:N)
├── PersonDocument (1:N)
└── PersonMedia (1:N)

TrainingCycle (macrocycle)
└── TrainingMicrocycle (week)
    └── TrainingSession (lifecycle: draft→scheduled→in_progress→pending_review→readonly)
        ├── SessionExercise (1:N, ordered, drag-drop)
        │   └── Exercise → ExerciseTag
        └── TrainingAlert (AI-generated)

Competition
├── CompetitionSeason
├── CompetitionPhase → CompetitionStanding
└── Match
    ├── MatchEvent (goal, foul, timeout, etc.)
    ├── MatchRoster
    ├── MatchPeriods
    └── MatchTeams

WellnessPre / WellnessPost (per session per athlete)
```

## Role hierarchy
`dirigente > coordenador > treinador > preparador_fisico > atleta`

Permissions resolved at login from canonical map (`app/core/permissions_map.py`).

## Key invariants (high-level)
- Person is the root entity; User and Athlete extend it (R1)
- No hard deletes; soft delete with `deleted_at` + `deleted_reason` (R29, RDB4)
- Training session lifecycle is one-directional (R18)
- Focus areas: 7 predefined, each 0-100%, total ≤120%
- Edit windows enforce temporal immutability (R40)
- All operations scoped to active membership + organization (R33, R42)
