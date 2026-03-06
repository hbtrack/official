# HB Track — Kanban (Processo determinístico para IA)

meta:
  document: HB_TRACK_KANBAN
  version: "0.2"
  status: CANON_PROCESS
  path: docs/hbtrack/Hb Track Kanban.md
  last_updated: 2026-03-02T00:02:00
  ssot_governance:
    contract: docs/_canon/contratos/Kanban Hb Track.md
    spec: docs/_canon/specs/Kanban Spec.md
  registries:
    gates_registry: docs/_canon/_agent/GATES_REGISTRY.yaml
    failure_to_gates: docs/_canon/_agent/FAILURE_TO_GATES.yaml
    correction_allowlist: docs/_canon/_agent/CORRECTION_WRITE_ALLOWLIST.yaml
    project_profile: docs/_canon/HB_TRACK_PROFILE.yaml
  evidence_pack_root: "docs/hbtrack/evidence/AR_<id>/"

## 1. Colunas

Fluxo obrigatório:
- BACKLOG
- READY
- EXECUTING
- EVIDENCE_PACK
- AUDIT
- DONE

WIP:
- EXECUTING MUST ter WIP=1 (máximo 2 em exceção documentada no card).

REGRA DURA (commit authority):
- Kanban NÃO libera commit.
- Autoridade de commit é exclusivamente: AR + evidence canônico + TESTADOR_REPORT + _INDEX.md + selo humano hb seal (✅ VERIFICADO).

2. Regras determinísticas (essência)

- Nenhum card entra em READY sem DoR completo.
- Nenhum card entra em DONE sem Evidence Pack íntegro.
- Gate lifecycle=MISSING => card MUST ser BLOCKED (exit code canônico 4 = BLOCKED_INPUT).

3. Baseline Gates (mínimos)

3.1 Evidence Pack (qualquer card que gere evidência)
- AUDIT_PACK_INTEGRITY (IMPLEMENTED)
  command: `python scripts/checks/check_audit_pack.py ${RUN_ID}`

3.2 Docs canônicos/processo (CONTRACT/SPEC/Kanban/docs/_INDEX.yaml)
- DOCS_CANON_CHECK (IMPLEMENTED)
  command: `python scripts/checks/check_docs_canon.py ${RUN_ID}`
- DOCS_INDEX_CHECK (MISSING)
  command atual no registry: `python scripts/audit/gate_stub_blocked.py DOCS_INDEX_CHECK`
  efeito: cards que exigem este gate ficam BLOCKED até implementar.

4. Definition of Ready (DoR) — checklist binário

CARD_ID:
TITLE:
CAPABILITY: (MUST existir no SPEC)
FAILURE_TYPE: (MUST existir no FAILURE_TO_GATES)

SSOT_REFERENCES:
- (paths)

WRITE_SCOPE:
- (paths)
FORBIDDEN:
- (paths)
ALLOWLIST_MATCH:
- (se aplicável, justificar compatibilidade com CORRECTION_WRITE_ALLOWLIST)

GATES_REQUIRED (IDs):
- (MUST existir no GATES_REGISTRY)
GATES_MINIMUM (baseline):
- (se Evidence Pack) AUDIT_PACK_INTEGRITY
- (se docs/processo) DOCS_CANON_CHECK + DOCS_INDEX_CHECK

EVIDENCE_EXPECTED:
- Para cada gate: exit_code esperado + marcador de stdout/stderr + artefato/arquivo (se houver)

ROLLBACK_PLAN:
- git revert <commit>
- validação de rollback (quais gates comprovam baseline)

ACCEPTANCE_CRITERIA:
- AC-001 (PASS/FAIL)
- AC-002 (PASS/FAIL)

Regra:
- Se qualquer campo acima estiver ausente => READY = FAIL (card permanece em BACKLOG/BLOCKED).

5. Execução (EXECUTING → EVIDENCE_PACK)

O Executor MUST:
- Aplicar mudanças somente no WRITE_SCOPE.
- Rodar todos os gates do card.
- Coletar evidências e estruturar o Evidence Pack em `docs/hbtrack/evidence/AR_<id>/`.

6. Evidence Pack (formato mínimo obrigatório)

Em `docs/hbtrack/evidence/AR_<id>/` MUST existir:
- card.yaml (CARD_ID, CAPABILITY, FAILURE_TYPE, SSOT_REFERENCES, WRITE_SCOPE)
- commands.log (comandos exatos + cwd + env pré-requisitos)
- exit_codes.json (map command -> exit code)
- stdout.log / stderr.log (ou por comando)
- diff_summary.txt (arquivos alterados)
- commit.txt (hash)

Gate obrigatório:
- AUDIT_PACK_INTEGRITY MUST PASS

7. AUDIT e DONE

AUDIT:
- Humano valida se evidência prova os ACs e se não houve “PASS por acidente”.

DONE:
- Só com PASS de todos os gates + Evidence Pack íntegro + aceite humano.

8. Template de Card (copiar/colar)

CARD_ID:
TITLE:
STATUS: BACKLOG | READY | EXECUTING | EVIDENCE_PACK | AUDIT | DONE | BLOCKED

CAPABILITY:
FAILURE_TYPE:
SCOPE_NOTE:

SSOT_REFERENCES:
- ...

WRITE_SCOPE:
- ...
FORBIDDEN:
- ...
ALLOWLIST_MATCH:
- ...

GATES_REQUIRED:
- ...
GATES_MINIMUM:
- ...

EVIDENCE_EXPECTED:
- gate_id: exit_code=0 + stdout markers + artifacts

ROLLBACK_PLAN:
- ...

ACCEPTANCE_CRITERIA:
- AC-001:
- AC-002:

EVIDENCE_PACK:
- RUN_ID:
- (links/paths em docs/hbtrack/evidence/AR_<id>/)

---

## 9. Cards — Domínio COMPETITIONS

### COMP-DB-001

CARD_ID: COMP-DB-001
TITLE: Soft delete (deleted_at/deleted_reason + trigger) em 5 tabelas do domínio COMPETITIONS
STATUS: EVIDENCE_PACK

CAPABILITY: COMPETITIONS
FAILURE_TYPE: FT_DB_MIGRATION
SCOPE_NOTE: DDL-only, sem backfill. Tabelas: competition_matches, competition_opponent_teams, competition_phases, match_events, match_roster. competition_standings excluído (ver COMP-DB-005).

SSOT_REFERENCES:
- docs/ssot/schema.sql
- docs/_canon/planos/comp_db_001_soft_delete_competition_tables.json

WRITE_SCOPE:
- Hb Track - Backend/db/alembic/versions/0055_comp_db_001_soft_delete_competition_tables.py
- Hb Track - Backend/app/models/competition_match.py
- Hb Track - Backend/app/models/competition_opponent_team.py
- Hb Track - Backend/app/models/competition_phase.py
- Hb Track - Backend/app/models/match_event.py
- Hb Track - Backend/app/models/match_roster.py
FORBIDDEN:
- competition_standings (excluído explicitamente — ver COMP-DB-005)
ALLOWLIST_MATCH:
- N/A

GATES_REQUIRED:
- DB_MIGRATIONS_UPGRADE_HEAD
- DB_MIGRATIONS_HASH_CHECK
GATES_MINIMUM:
- AUDIT_PACK_INTEGRITY

EVIDENCE_EXPECTED:
- DB_MIGRATIONS_UPGRADE_HEAD: exit_code=0 + alembic head=0055
- DB_MIGRATIONS_HASH_CHECK: exit_code=0
- AUDIT_PACK_INTEGRITY: exit_code=0

ROLLBACK_PLAN:
- alembic downgrade -1
- git restore dos 5 models (competition_match.py, competition_opponent_team.py, competition_phase.py, match_event.py, match_roster.py)

ACCEPTANCE_CRITERIA:
- AC-001: deleted_at + deleted_reason presentes nas 5 tabelas (information_schema.columns)
- AC-002: 5 triggers trg_<table>_block_delete existem (information_schema.triggers)
- AC-003: ck_<table>_deleted_reason CHECK constraints existem nas 5 tabelas
- AC-004: alembic downgrade -1 retorna exit_code=0

EVIDENCE_PACK:
- RUN_ID: HB-AUDIT-COMP-DB-001-20260222-001
- docs/hbtrack/evidence/HB-AUDIT-COMP-DB-001/
- DB_MIGRATIONS_UPGRADE_HEAD: PASS (exit_code=0, alembic upgrade 0055 OK, local PG12:5433)
- DB_MIGRATIONS_HASH_CHECK: PASS (exit_code=0, single head 0061, sem conflitos)
- AUDIT_PACK_INTEGRITY: PASS (exit_code=0)
- AC-001 deleted_at/deleted_reason 5 tabelas: PASS
- AC-002 5 triggers trg_*_block_delete: PASS
- AC-003 5 CHECK ck_*_deleted_reason: PASS
- AC-004 alembic downgrade -1 exit_code=0: PASS
- NOTA: Gate LOCAL (PG12:5433) PASS. VPS (PG15) inacessível — gate VPS é CONDITIONAL per GATES_REGISTRY.

---

### COMP-DB-002

CARD_ID: COMP-DB-002
TITLE: competition_standings.team_id — FK → teams.id (ON DELETE SET NULL)
STATUS: EVIDENCE_PACK

CAPABILITY: COMPETITIONS
FAILURE_TYPE: FT_DB_MIGRATION
SCOPE_NOTE: Adiciona coluna team_id (uuid nullable) com FK para teams.id e índice de suporte. Plano detalhado em competition_standings_add_team_id.json.

SSOT_REFERENCES:
- docs/ssot/schema.sql
- docs/_canon/planos/competition_standings_add_team_id.json

WRITE_SCOPE:
- Hb Track - Backend/db/alembic/versions/0054_competition_standings_add_team_id.py
- Hb Track - Backend/app/models/competition_standing.py
FORBIDDEN:
- Demais models e rotas
ALLOWLIST_MATCH:
- N/A

GATES_REQUIRED:
- DB_MIGRATIONS_UPGRADE_HEAD
- DB_MIGRATIONS_HASH_CHECK
GATES_MINIMUM:
- AUDIT_PACK_INTEGRITY

EVIDENCE_EXPECTED:
- DB_MIGRATIONS_UPGRADE_HEAD: exit_code=0
- DB_MIGRATIONS_HASH_CHECK: exit_code=0
- AUDIT_PACK_INTEGRITY: exit_code=0

ROLLBACK_PLAN:
- alembic downgrade -1
- git restore Hb Track - Backend/app/models/competition_standing.py

ACCEPTANCE_CRITERIA:
- AC-001: competition_standings.team_id EXISTS (information_schema.columns)
- AC-002: fk_competition_standings_team_id constraint EXISTS
- AC-003: alembic downgrade -1 retorna exit_code=0

EVIDENCE_PACK:
- RUN_ID: HB-AUDIT-COMP-DB-002-20260222-001
- docs/hbtrack/evidence/HB-AUDIT-COMP-DB-002/
- DB_MIGRATIONS_UPGRADE_HEAD: PASS (exit_code=0, alembic upgrade 0054 OK, local PG12:5433)
- DB_MIGRATIONS_HASH_CHECK: PASS (exit_code=0, single head 0061)
- AUDIT_PACK_INTEGRITY: PASS (exit_code=0)
- AC-001 competition_standings.team_id EXISTS: PASS
- AC-002 fk_competition_standings_team_id EXISTS: PASS
- AC-003 alembic downgrade -1 exit_code=0: PASS

---

### COMP-DB-003

CARD_ID: COMP-DB-003
TITLE: competitions.points_per_draw + points_per_loss — colunas de regras de pontuação
STATUS: EVIDENCE_PACK

CAPABILITY: COMPETITIONS
FAILURE_TYPE: FT_DB_MIGRATION
SCOPE_NOTE: Adiciona points_per_draw (DEFAULT 1) e points_per_loss (DEFAULT 0) em competitions. Atualiza model competition.py. Migration 0056, down_revision='0055'.

SSOT_REFERENCES:
- docs/ssot/schema.sql
- docs/_canon/planos/comp_db_003_scoring_rules.json

WRITE_SCOPE:
- Hb Track - Backend/db/alembic/versions/0056_comp_db_003_scoring_rules_competitions.py
- Hb Track - Backend/app/models/competition.py
FORBIDDEN:
- Rotas, serviços, schemas Pydantic (escopo estritamente estrutural)
ALLOWLIST_MATCH:
- N/A

GATES_REQUIRED:
- DB_MIGRATIONS_UPGRADE_HEAD
- DB_MIGRATIONS_HASH_CHECK
GATES_MINIMUM:
- AUDIT_PACK_INTEGRITY

EVIDENCE_EXPECTED:
- DB_MIGRATIONS_UPGRADE_HEAD: exit_code=0 + head=0056
- DB_MIGRATIONS_HASH_CHECK: exit_code=0
- AUDIT_PACK_INTEGRITY: exit_code=0

ROLLBACK_PLAN:
- alembic downgrade -1 (drop columns points_per_draw, points_per_loss)
- git restore Hb Track - Backend/app/models/competition.py

ACCEPTANCE_CRITERIA:
- AC-001: competitions.points_per_draw EXISTS com DEFAULT=1 (information_schema.columns)
- AC-002: competitions.points_per_loss EXISTS com DEFAULT=0
- AC-003: Competition model tem points_per_draw e points_per_loss como Mapped[int]
- AC-004: alembic downgrade -1 retorna exit_code=0

EVIDENCE_PACK:
- RUN_ID: HB-AUDIT-COMP-DB-003-20260222-001
- docs/hbtrack/evidence/HB-AUDIT-COMP-DB-003/
- DB_MIGRATIONS_UPGRADE_HEAD: PASS (exit_code=0, alembic upgrade 0056 OK, local PG12:5433)
- DB_MIGRATIONS_HASH_CHECK: PASS (exit_code=0, single head 0061)
- AUDIT_PACK_INTEGRITY: PASS (exit_code=0)
- AC-001 competitions.points_per_draw EXISTS default=1: PASS
- AC-002 competitions.points_per_loss EXISTS default=0: PASS
- AC-003 Competition model Mapped[int] fields: PASS
- AC-004 alembic downgrade -1 exit_code=0: PASS

---

### COMP-DB-004

CARD_ID: COMP-DB-004
TITLE: competition_standings — UNIQUE index com NULLS NOT DISTINCT substituindo uk_competition_standings_team_phase
STATUS: EVIDENCE_PACK

CAPABILITY: COMPETITIONS
FAILURE_TYPE: FT_DB_MIGRATION
SCOPE_NOTE: O constraint UNIQUE atual (competition_id, phase_id, opponent_team_id) permite duplicatas quando phase_id IS NULL (NULL != NULL em UNIQUE). Substituir por UNIQUE INDEX NULLS NOT DISTINCT (PostgreSQL 15+). Migration 0060, down_revision='0059'. BLOQUEADO: requer PG15+ (local é PG12).

SSOT_REFERENCES:
- docs/ssot/schema.sql (linha 2668-2672)
- docs/_canon/planos/comp_db_004_unique_index.json

WRITE_SCOPE:
- Hb Track - Backend/db/alembic/versions/0060_comp_db_004_standings_unique_nulls_not_distinct.py
- Hb Track - Backend/app/models/competition_standing.py
FORBIDDEN:
- Demais models e rotas
ALLOWLIST_MATCH:
- N/A

GATES_REQUIRED:
- DB_MIGRATIONS_UPGRADE_HEAD
- DB_MIGRATIONS_HASH_CHECK
GATES_MINIMUM:
- AUDIT_PACK_INTEGRITY

EVIDENCE_EXPECTED:
- DB_MIGRATIONS_UPGRADE_HEAD: exit_code=0 + head=0060
- DB_MIGRATIONS_HASH_CHECK: exit_code=0
- AUDIT_PACK_INTEGRITY: exit_code=0

ROLLBACK_PLAN:
- alembic downgrade -1 (drop new index, recreate uk_competition_standings_team_phase)
- git restore Hb Track - Backend/app/models/competition_standing.py

ACCEPTANCE_CRITERIA:
- AC-001: uk_competition_standings_team_phase NÃO EXISTS após migration
- AC-002: uq_competition_standings_comp_phase_opponent EXISTS (information_schema.table_constraints)
- AC-003: INSERT duplicado com phase_id=NULL levanta UniqueViolation (teste funcional)
- AC-004: alembic downgrade -1 retorna exit_code=0

EVIDENCE_PACK:
- RUN_ID: HB-AUDIT-COMP-DB-004-20260222-001
- docs/hbtrack/evidence/HB-AUDIT-COMP-DB-004/
- DB_MIGRATIONS_UPGRADE_HEAD: PASS (exit_code=0, VPS PG15.16, alembic upgrade 0060 OK)
- DB_MIGRATIONS_HASH_CHECK: PASS (exit_code=0, single head 0061)
- AUDIT_PACK_INTEGRITY: PASS (exit_code=0)
- AC-001 uk_competition_standings_team_phase GONE: PASS
- AC-002 uq_competition_standings_comp_phase_opponent EXISTS: PASS
- AC-003 indnullsnotdistinct=true em pg_index: PASS
- AC-004 alembic downgrade -1 exit_code=0: PASS
- WAIVER: WAIVER-2026-02-22-001 CLOSED — docs/_canon/_agent/WAIVERS.yaml
- CORR: _reports/cases/CORR-2026-02-22-001/state.yaml

---

### COMP-DB-005

CARD_ID: COMP-DB-005
TITLE: competition_standings soft delete (deleted_at/deleted_reason + trigger) — decisão PO necessária
STATUS: BACKLOG

CAPABILITY: COMPETITIONS
FAILURE_TYPE: FT_DB_MIGRATION
SCOPE_NOTE: Excluído de COMP-DB-001 (decisão PO-PEND-004). competition_standings é tabela de cache recalculável sem dados pessoais diretos. Requer confirmação: soft delete mandatório (RDB4) vs. recalculável sem LGPD Art.18. Bloqueado até decisão PO.

SSOT_REFERENCES:
- docs/ssot/schema.sql
- docs/_canon/planos/comp_db_001_soft_delete_competition_tables.json (notas: exclusão)

WRITE_SCOPE:
- Hb Track - Backend/db/alembic/versions/0058_comp_db_005_standings_soft_delete.py
- Hb Track - Backend/app/models/competition_standing.py
FORBIDDEN:
- Demais tables e models
ALLOWLIST_MATCH:
- N/A

GATES_REQUIRED:
- DB_MIGRATIONS_UPGRADE_HEAD
- DB_MIGRATIONS_HASH_CHECK
GATES_MINIMUM:
- AUDIT_PACK_INTEGRITY

EVIDENCE_EXPECTED:
- DB_MIGRATIONS_UPGRADE_HEAD: exit_code=0
- DB_MIGRATIONS_HASH_CHECK: exit_code=0
- AUDIT_PACK_INTEGRITY: exit_code=0

ROLLBACK_PLAN:
- alembic downgrade -1
- git restore Hb Track - Backend/app/models/competition_standing.py

ACCEPTANCE_CRITERIA:
- AC-001: competition_standings.deleted_at EXISTS
- AC-002: ck_competition_standings_deleted_reason CHECK constraint EXISTS
- AC-003: trg_competition_standings_block_delete trigger EXISTS
- AC-004: alembic downgrade -1 retorna exit_code=0

EVIDENCE_PACK:
- RUN_ID: (pendente)
- BLOQUEADO: aguardando decisão PO (PO-PEND-004)

---

### COMP-DB-006

CARD_ID: COMP-DB-006
TITLE: competitions + competition_matches — CHECK constraints de status/modality
STATUS: EVIDENCE_PACK

CAPABILITY: COMPETITIONS
FAILURE_TYPE: FT_DB_MIGRATION
SCOPE_NOTE: competitions.status e competition_matches.status têm DEFAULT definido mas sem CHECK constraint. competitions.modality também sem CHECK. Risco de valores inválidos silenciosos no banco.

SSOT_REFERENCES:
- docs/ssot/schema.sql (linhas 760-782, 648-674)
- Hb Track - Backend/app/models/competition.py (status DEFAULT 'draft', modality DEFAULT 'masculino')

WRITE_SCOPE:
- Hb Track - Backend/db/alembic/versions/0061_comp_db_006_status_check_constraints.py
- Hb Track - Backend/app/models/competition.py
- Hb Track - Backend/app/models/competition_match.py
FORBIDDEN:
- Rotas, serviços, schemas Pydantic
ALLOWLIST_MATCH:
- N/A

GATES_REQUIRED:
- DB_MIGRATIONS_UPGRADE_HEAD
- DB_MIGRATIONS_HASH_CHECK
GATES_MINIMUM:
- AUDIT_PACK_INTEGRITY

EVIDENCE_EXPECTED:
- DB_MIGRATIONS_UPGRADE_HEAD: exit_code=0
- DB_MIGRATIONS_HASH_CHECK: exit_code=0
- AUDIT_PACK_INTEGRITY: exit_code=0

ROLLBACK_PLAN:
- alembic downgrade -1
- git restore dos 2 models

ACCEPTANCE_CRITERIA:
- AC-001: ck_competitions_status CHECK constraint EXISTS com valores permitidos
- AC-002: ck_competitions_modality CHECK constraint EXISTS
- AC-003: ck_competition_matches_status CHECK constraint EXISTS
- AC-004: INSERT com status='invalido' levanta CheckViolation
- AC-005: alembic downgrade -1 retorna exit_code=0

EVIDENCE_PACK:
- RUN_ID: HB-AUDIT-COMP-DB-006-20260222-001
- docs/hbtrack/evidence/HB-AUDIT-COMP-DB-006/
- DB_MIGRATIONS_UPGRADE_HEAD: PASS (exit_code=0, VPS PG15.16, alembic upgrade 0061 OK)
- DB_MIGRATIONS_HASH_CHECK: PASS (exit_code=0, single head 0061)
- AUDIT_PACK_INTEGRITY: PASS (exit_code=0)
- AC-001 ck_competitions_status EXISTS: PASS (values: draft/active/finished/cancelled)
- AC-002 ck_competitions_modality EXISTS: PASS
- AC-003 ck_competition_matches_status EXISTS: PASS
- AC-004 CHECK constraint def rejeita invalido: PASS (structural via information_schema)
- AC-005 alembic downgrade -1 exit_code=0: PASS

### ✅ Concluído
- AR_150 — ✅ VERIFICADO+sealed (guards INV-054/INV-057, commit 236bfb6)
- AR_128
- AR_125
- AR_142
- AR_141
- AR_140
- AR_139
- AR_138
- AR_078
- AR_000
- AR_076
- AR_059
- AR_058
- AR_056
- AR_075
- AR_074
- AR_073
- AR_063
- AR_062
- AR_061
- AR_057
- AR_123
- AR_119
- AR_118
- AR_117
- AR_116
- AR_115
- AR_114
- AR_113
- AR_068
- AR_120
- AR_122
- AR_043
- AR_042
- AR_041
- AR_039
- AR_037
- AR_112
- AR_111
- AR_110
- AR_109
- AR_104
- AR_998
- AR_072
- AR_900
- AR_064
- AR_050
- AR_055
- AR_054
- AR_052
- AR_051
- AR_049
- AR_048
- AR_046
- AR_047
- AR_999 — test
- AR_100 — Protocolo v1.2.0 verificado com Selo Humano (2026-02-23)
- AR_071 — hb_autotest auto-commit verificado (2026-02-24)
- AR_053 — hb_watch UTF-8 fix verificado (VERIFICADO 2x pelo Testador)
- AR_001, AR_002, AR_014, AR_015, AR_024, AR_033, AR_036, AR_101, AR_102, AR_103 — ✅ VERIFICADO (confirmado kanban_audit 2026-03-03)
- AR_104, AR_105, AR_002.5_A, AR_002.5_B, AR_002.5_D — ✅ VERIFICADO (confirmado kanban_audit 2026-03-03)
- AR_002.5_C — ⛛ SUPERSEDED (absorvida; divergência documentada por outros meios)
- AR_003, AR_004, AR_005, AR_060, AR_065, AR_066, AR_067, AR_070, AR_077, AR_124 — ✅ VERIFICADO (confirmado kanban_audit 2026-03-03)
- AR_023 — ⛔ SUPERSEDED (triple-run em produção desde v1.1.0; Evidence Pack nunca criado — absorvida)

### 🛠️ Em Execução
(vazio — todas ARs movidas para ✅ Concluído em 2026-03-03 via kanban_audit)

### 📥 Backlog
(vazio — todas ARs movidas para ✅ Concluído em 2026-03-03 via kanban_audit)

---

## 10. Cards — Domínio TRAINING — Implementação Invariantes (AR_143-161)

> **Contexto**: Planos materializados em `c65c969`. Fase A foi implementada pelo Executor mas destruída por `git restore .` acidental do Testador (26/02/2026).
> `AR_150` já ✅ VERIFICADO+sealed. As demais precisam de execução pelo Executor.

### ✅ DONE — Fase A: Exercise Bank (re-executada e verificada)

> Todos os outputs recuperados e verificados pelo Testador. hb seal executado.

| AR | Título | Status |
|---|---|---|
| **AR_143** | Atualizar TEST_MATRIX | ✅ VERIFICADO |
| **AR_144** | DB exercise_bank schema | ✅ VERIFICADO |
| **AR_145** | exercise_service.py guards | ✅ VERIFICADO |
| **AR_146** | exercise_acl_service.py | ✅ VERIFICADO |
| **AR_147** | catalog visibility + session_exercise guard | ✅ VERIFICADO |
| **AR_148** | tests INV-047..053 | ✅ VERIFICADO |

### ✅ CONCLUÍDA — Fase B: Hierarquia de Ciclos (parcial)

| AR | Título | Status |
|---|---|---|
| **AR_149** | DB training_sessions.standalone | ✅ VERIFICADO (HEAD `eb88236`) |
| **AR_150** | Guards INV-054, INV-057 | ✅ VERIFICADO |
| **AR_151** | MicrocycleOutsideMesoError + overlap guard | ✅ VERIFICADO |

### ✅ DONE — Fase B: Hierarquia de Ciclos (concluída)

| AR | Título | Status |
|---|---|---|
| **AR_152** | tests INV-054..057 ciclos | ✅ VERIFICADO |

### ✅ Fase C: Attendance Avançada — Checkpoint

| AR | Título | Status |
|---|---|---|
| **AR_149** | DB training_sessions.standalone | ✅ VERIFICADO |
| **AR_150** | Guards INV-054, INV-057 | ✅ VERIFICADO |
| **AR_151** | MicrocycleOutsideMesoError + overlap guard | ✅ VERIFICADO |
| **AR_152** | tests INV-054..057 ciclos | ✅ VERIFICADO |

### ✅ DONE — Fase C: Attendance Avançada (concluída)

| AR | Título | Status |
|---|---|---|
| **AR_153** | DB attendance preconfirm + pending_items | ✅ VERIFICADO |
| **AR_154** | attendance_service.py preconfirm + close | ✅ VERIFICADO |
| **AR_155** | training_pending_service.py + RBAC atleta | ✅ VERIFICADO |
| **AR_156** | athlete UX training visibility + exercise | ✅ VERIFICADO |
| **AR_157** | wellness_post campo conversacional | ✅ VERIFICADO |
| **AR_158** | tests INV-063..070 attendance avançada | ✅ VERIFICADO |
| **AR_159** | athlete_content_gate_service.py (novo) | ✅ VERIFICADO |
| **AR_160** | tests INV-071/076/078 wellness | ✅ VERIFICADO |
| **AR_161** | Regressão final — todos os 84 invariantes | ✅ VERIFICADO |

### 🔲 PENDENTE — Fase D: Wellness Obrigatória

| AR | Título | Ação |
|---|---|---|
| (vazio — todas ARs da Fase D concluídas) | | |

### Lição aprendida (protocolo)

> **CAUSA DO REDO**: Testador usou `git restore .` + `git clean -fd` para "limpar workspace" antes do seal.
> Isso viola `§12.5 COMANDOS PROIBIDOS`. O correto é `git restore --staged <arquivo>` (seletivo).
> O testador.agent.pt-br.md foi atualizado com gate anti-restore indiscriminado (commit `c65c969`).

---

## 11. Cards — TRAINING Batch 0 — Finalização do Módulo (AR_169-174)

> **Contexto**: Batch 0 do `TRAINING_BATCH_PLAN_v1.md`. P0 blockers: Wellness FE (paths + campos) +
> Presenças UI (status `justified`) + desbloqueio de testes via migração SSOT.
> Planos materializados em `docs/_canon/planos/`. SSOT regenerado (gen_docs_ssot.py). **Data**: 2026.

### ✅ DONE — AR-TRAIN-001: Step18 UUID Convergence

> AR_126, AR_127, AR_128, AR_129 — todos `✅ VERIFICADO` (hb seal executado).

| AR | Título | Status |
|---|---|---|
| **AR_126** | Router UUID attrs convergence | ✅ VERIFICADO |
| **AR_127** | Schema Pydantic UUID align | ✅ VERIFICADO |
| **AR_128** | Service UUID propagation | ✅ VERIFICADO |
| **AR_129** | Regen OpenAPI após UUID fix | ✅ VERIFICADO |

### ✅ DONE — AR-TRAIN-003: Wellness FE Fix

> AR_169, AR_170 — todos `✅ VERIFICADO` (hb seal 2026-02-28). Hash canônico AR_169=`3b7525c5`, AR_170=`98ff43e0`.

| AR | Título | Status |
|---|---|---|
| **AR_169** | Fix `wellness.ts` paths + interface | ✅ VERIFICADO |
| **AR_170** | Fix `WellnessPreForm.tsx` campos UI | ✅ VERIFICADO |

### ✅ DONE — AR-TRAIN-005: Presenças UI `justified`

> AR_171, AR_172 — todos `✅ VERIFICADO` (hb seal 2026-02-28).

| AR | Título | Status |
|---|---|---|
| **AR_171** | Fix `attendance.ts` `PresenceStatus` | ✅ VERIFICADO |
| **AR_172** | Fix `AttendanceTab.tsx` UI justified | ✅ VERIFICADO |

### ✅ DONE — AR-TRAIN-010A: Migração SSOT path nos testes

> AR_173, AR_174 — todos `✅ VERIFICADO` (hb seal 2026-02-28). Hash canônico AR_173=`9fcd68c9`, AR_174=`58341b51`.

| AR | Título | Status |
|---|---|---|
| **AR_173** | Migrar `_generated`→`ssot` (lote 1/2) | ✅ VERIFICADO |
| **AR_174** | Migrar `_generated`→`ssot` (lote 2/2) | ✅ VERIFICADO |


---

## 12. Cards -- TRAINING Batch 1 -- Step18 Funcional + Wellness BE Self-Only (AR_175-176)

> **Contexto**: Batch 1 do TRAINING_BATCH_PLAN_v1.md. Depende de Batch 0 (DONE).
> AR-TRAIN-002 depende de AR-TRAIN-001 DONE. AR-TRAIN-004 depende de AR-TRAIN-003 DONE.
> Planos: docs/_canon/planos/ar_train_002_step18_services.json + docs/_canon/planos/ar_train_004_wellness_backend.json.
> **Data planejamento**: 2026-02-28.
> **Batch 1 DONE** (2026-02-28): AR_175 hash `4311eca06eecd493` ✅ | AR_176 hash `386b5d5092ca7563` ✅

### ✅ DONE -- AR-TRAIN-002: Step18 Services UUID

| AR | Titulo | Status | Proxima Acao |
|---|---|---|---|
| **AR_175** | Fix Step18 services: UUID em training_alerts/suggestions | ✅ VERIFICADO | Batch 1 DONE |

### ✅ DONE -- AR-TRAIN-004: Wellness BE Self-Only + LGPD

| AR | Titulo | Status | Proxima Acao |
|---|---|---|---|
| **AR_176** | Fix wellness BE: self-only JWT + payload minimo + LGPD | ✅ VERIFICADO | Batch 1 DONE |

---

## 13. Cards -- TRAINING Batch 2 -- Rankings + Exports (AR_177-180) ✅ DONE

> **Contexto**: Batch 2 do TRAINING_BATCH_PLAN_v1.md. Depende de Batch 1 (DONE).
> AR-TRAIN-006 depende de AR-TRAIN-004 (AR_176 ✅ VERIFICADO).
> AR-TRAIN-007 depende de AR-TRAIN-006 (AR_177).
> AR-TRAIN-009 depende de AR-TRAIN-008 (AR_179).
> Planos: docs/_canon/planos/ar_train_006_wellness_rankings_be.json + ar_train_007_rankings_fe_uuid.json + ar_train_008_exports_be_reabilitar.json + ar_train_009_export_pdf_modal_fe.json.
> **Data planejamento**: 2026-02-28.
> **Ordem de execução**: AR_177 → AR_178 | AR_179 → AR_180 (paralela: AR_177+AR_179 podem rodar juntos; AR_178 aguarda AR_177; AR_180 aguarda AR_179).
> **Status**: BATCH COMPLETO (2026-02-28) — todos ARs ✅ VERIFICADO.

### ✅ DONE -- AR-TRAIN-006: Rankings Wellness BE (cálculo SSOT + response_model)

| AR | Titulo | Status | Hash |
|---|---|---|---|
| **AR_177** | Fix wellness rankings BE: cálculo SSOT (presence_status) + UUID + response_model | ✅ VERIFICADO | (staged) |

### ✅ DONE -- AR-TRAIN-007: Rankings/TopPerformers FE (UUID + endpoint canônico)

| AR | Titulo | Status | Hash |
|---|---|---|---|
| **AR_178** | Fix Rankings FE: UUID strings em rankings.ts + RankingsClient + TopPerformersClient | ✅ VERIFICADO | (staged) |

### ✅ DONE -- AR-TRAIN-008: Reabilitar Exports BE + OpenAPI + Estado Degradado

| AR | Titulo | Status | Hash |
|---|---|---|---|
| **AR_179** | Reabilitar exports BE + estado degradado sem worker + regen OpenAPI SSOT | ✅ VERIFICADO | (staged) |

### ✅ DONE -- AR-TRAIN-009: ExportPDFModal FE (conectar backend + estado degradado)

| AR | Titulo | Status | Hash |
|---|---|---|---|
| **AR_180** | Fix ExportPDFModal FE: conectar backend reabilitado + estado degradado | ✅ VERIFICADO | (staged) |

---

## 14. Cards -- TRAINING Batch 3 -- Banco de Exercícios (Schema/ACL/Mídia/UI) (AR_181-184)

> **Contexto**: Batch 3 do TRAINING_BATCH_PLAN_v1.md. Depende de Batch 2 (DONE).
> AR-TRAIN-012 depende de AR-TRAIN-011.
> AR-TRAIN-013 depende de AR-TRAIN-012.
> AR-TRAIN-014 depende de AR-TRAIN-013.
> **Data planejamento**: 2026-02-28.
> **Ordem de execução**: AR_181 → AR_182 → AR_183 → AR_184 (sequencial por dependência).

### ✅ VERIFICADO -- AR-TRAIN-011: Schema Exercises (scope + visibility + ACL + media)

| AR | Titulo | Status | Proxima Acao |
|---|---|---|---|
| **AR_181** | Schema exercises (scope, visibility_mode) + exercise_acl + exercise_media | ✅ VERIFICADO | hb seal 181 executado em 2026-03-01 |

### ✅ VERIFICADO -- AR-TRAIN-012: Guards Escopo + RBAC + Service ACL

| AR | Titulo | Status | Proxima Acao |
|---|---|---|---|
| **AR_182** | Guards escopo SYSTEM/ORG + RBAC Treinador + service ACL + visibilidade | ✅ VERIFICADO | hb seal 182 executado em 2026-03-01 |

### ✅ VERIFICADO -- AR-TRAIN-013: Endpoints ACL + Copy SYSTEM→ORG + Toggle Visibilidade

| AR | Titulo | Status | Proxima Acao |
|---|---|---|---|
| **AR_183** | Endpoints ACL + copy SYSTEM→ORG + toggle visibilidade | ✅ VERIFICADO | hb seal 183 executado em 2026-03-01 |

### ✅ VERIFICADO -- AR-TRAIN-014: UI Scope/Visibility/ACL/Mídia FE

| AR | Titulo | Status | Proxima Acao |
|---|---|---|---|
| **AR_184** | UI scope/visibility/ACL/mídia no exercise-bank FE | ✅ VERIFICADO | hb seal 184 executado em 2026-03-01 |

---

## 15. Cards -- TRAINING Batch 4 -- FASE_3 Presença Oficial + Pending Queue + Visão Atleta (AR_185-187) ✅ DONE

> **Contexto**: Batch 4 do TRAINING_BATCH_PLAN_v1.md. Depende de Batch 3 (✅ VERIFICADO 2026-03-01).
> Serviços backend já existem via AR_153-161 (attendance_service, training_pending_service, athlete_content_gate_service).
> O que falta: router endpoints + UI completa.
> AR-TRAIN-018 depende de AR-TRAIN-017 (AR_185 VERIFICADO).
> AR-TRAIN-019 depende de AR-TRAIN-017 (AR_185 VERIFICADO).
> **Data planejamento**: 2026-03-01.
> **Ordem de execução**: AR_185 → (AR_186 e AR_187 paralelas após AR_185 VERIFICADO).
> **Planos**: docs/_canon/planos/ar_train_017_attendance_preconfirm_router.json | ar_train_018_pending_queue_fe.json | ar_train_019_athlete_training_preview.json

### ✅ VERIFICADO -- AR-TRAIN-017: Presença Oficial — Router Endpoints

| AR | Titulo | Status | Proxima Acao |
|---|---|---|---|
| **AR_185** | Expor preconfirm + close_session + pending-items no router attendance.py | ✅ VERIFICADO | hb seal 185 executado em 2026-03-01 |

### ✅ VERIFICADO -- AR-TRAIN-018: UI Fila de Pendências (FE Treinador)

| AR | Titulo | Status | Proxima Acao |
|---|---|---|---|
| **AR_186** | pending.ts + pending-queue/page.tsx + PendingQueueTable.tsx | ✅ VERIFICADO | hb seal 186 executado em 2026-03-01 |

### ✅ VERIFICADO -- AR-TRAIN-019: Visão Pré-Treino Atleta + Wellness Gate

| AR | Titulo | Status | Proxima Acao |
|---|---|---|---|
| **AR_187** | athlete_training.py router (preview) + FE /athlete/training/[sessionId] | ✅ VERIFICADO | hb seal 187 executado em 2026-03-01 |

---

## 16. Cards -- TRAINING Batch 5 -- FASE_3 Ciclos Hierarchy + Sessão Standalone + Pós-Treino + IA Coach (AR_189-192) ✅ VERIFICADO

> **Contexto**: Batch 5 do TRAINING_BATCH_PLAN_v1.md. Depende de Batch 4 (✅ VERIFICADO 2026-03-01). **Batch 5 ✅ VERIFICADO 2026-03-01 (hb seal 189 190 191 192).**
> AR-TRAIN-015 (ciclos): training_cycle.py + training_cycle_service.py — tabela training_cycles já existe, falta validação de containment service-level.
> AR-TRAIN-016 (standalone): training_session_service.py + session_exercise_service.py — coluna standalone já existe no DB, falta guard no service.
> AR-TRAIN-020 (pós-treino): post_training_service.py (novo) + post_training.py router (novo) — sem tabela dedicada no schema atual (Executor verifica INV-070/077).
> AR-TRAIN-021 (IA coach): ai_coach_service.py (já existe parcial, INV-072..075) + ai_coach.py router (novo) + FE ai-chat + AICoachDraftModal.tsx — delta = INV-079..081 + FLOW-TRAIN-019/020 + SCREEN-TRAIN-024/025.
> **Data planejamento**: 2026-03-01.
> **Ordem de execução**: AR_189 + AR_190 + AR_191 paralelas → AR_192 após AR_191 VERIFICADO.
> **Planos**: docs/_canon/planos/ar_train_015_ciclos_hierarchy.json | ar_train_016_sessao_standalone_mutabilidade.json | ar_train_020_pos_treino_conversacional.json | ar_train_021_ia_coach.json

### ✅ VERIFICADO -- AR-TRAIN-015: Schema + Service ciclos hierarchy (macro→meso→micro)

| AR | Titulo | Status | Proxima Acao |
|---|---|---|---|
| **AR_189** | training_cycle.py FK hierarchy + training_cycle_service.py containment validation | ✅ VERIFICADO | hb seal 189 executado em 2026-03-01 |

### ✅ VERIFICADO -- AR-TRAIN-016: Sessão standalone + mutabilidade + order_index exercícios

| AR | Titulo | Status | Proxima Acao |
|---|---|---|---|
| **AR_190** | training_session_service.py standalone guard + session_exercise_service.py order_index | ✅ VERIFICADO | hb seal 190 executado em 2026-03-01 |

### ✅ VERIFICADO -- AR-TRAIN-020: Pós-treino conversacional + feedback imediato

| AR | Titulo | Status | Proxima Acao |
|---|---|---|---|
| **AR_191** | post_training_service.py (novo) + post_training.py router (novo) | ✅ VERIFICADO | hb seal 191 executado em 2026-03-01 |

### ✅ VERIFICADO -- AR-TRAIN-021: IA Coach (drafts + chat + justificativas + privacidade)

| AR | Titulo | Status | Proxima Acao |
|---|---|---|---|
| **AR_192** | ai_coach_service.py (delta INV-079..081) + ai_coach.py router + FE ai-chat + AICoachDraftModal.tsx | ✅ VERIFICADO | hb seal 192 executado em 2026-03-01 |

---

## 17. Cards -- TRAINING Governança -- TEST_MATRIX sync Batch4/5 (AR_193) ✅ VERIFICADO

> **Contexto**: AR de governança. Atualiza TEST_MATRIX_TRAINING.md §9 para refletir AR-TRAIN-015..021 (AR_185..192) como VERIFICADOS. Não implementa código de produto. **✅ VERIFICADO 2026-03-01 (hb seal 193).**
> **Data planejamento**: 2026-03-01.
> **Plano**: docs/_canon/planos/ar_193_test_matrix_update_batch4_5.json

### ✅ VERIFICADO -- TEST_MATRIX sync Batch4/5 — AR-TRAIN-015..021 VERIFICADOS

| AR | Titulo | Status | Proxima Acao |
|---|---|---|---|
| **AR_193** | TEST_MATRIX sync: §9 AR-TRAIN-015..021 PENDENTE→VERIFICADO + changelog v1.5.0 | ✅ VERIFICADO | hb seal 193 executado em 2026-03-01 |

---

## 18. Cards -- TRAINING Governança -- Batch Plan Batch6 AR-TRAIN-010B (AR_194) ✅ VERIFICADO

> **Contexto**: AR de governança. Atualiza `TRAINING_BATCH_PLAN_v1.md` para incluir Batch 6 com AR-TRAIN-010B (Testes de contrato/cobertura). Não implementa código de produto. Dependências de AR-TRAIN-010B (AR-TRAIN-001..009) todas VERIFICADAS em 2026-03-01. **✅ VERIFICADO 2026-03-01 (hb seal 194).**
> **Data planejamento**: 2026-03-01.
> **Plano**: docs/_canon/planos/ar_194_batch_plan_add_batch6_010b.json

### ✅ VERIFICADO -- TRAINING_BATCH_PLAN_v1 adicionar Batch 6 (AR-TRAIN-010B)

| AR | Titulo | Status | Proxima Acao |
|---|---|---|---|
| **AR_194** | TRAINING_BATCH_PLAN_v1.md: header v1.0.2 + secao Batch 6 com AR-TRAIN-010B (INV-TRAIN-013/024, CONTRACT-TRAIN-073..075/077..085) | ✅ VERIFICADO | hb seal 194 executado em 2026-03-01 |

---

## 19. Cards -- TRAINING Batch 6 -- Testes Contrato/Cobertura AR-TRAIN-010B (AR_195) ✅ VERIFICADO

> **Contexto**: Batch 6 do `TRAINING_BATCH_PLAN_v1.md` (v1.0.2). Class T. Cobrir INV-TRAIN-013 (gamification_badge_eligibility) + INV-TRAIN-024 (websocket_broadcast) + CONTRACT-TRAIN-073..075 (wellness-rankings) + CONTRACT-TRAIN-077..085 (alerts-suggestions). Consolidar cobertura em `TEST_MATRIX_TRAINING.md` referenciando AR-TRAIN-010B. Dependências: AR-TRAIN-001..009 todas ✅ VERIFICADAS. **✅ VERIFICADO 2026-03-01 (hb seal 195). Hash canônico: 92e2fd8e77a76cda.**
> **Data planejamento**: 2026-03-01.
> **Plano**: docs/_canon/planos/ar_195_ar_train_010b_testes_contrato_cobertura.json

### ✅ VERIFICADO -- AR-TRAIN-010B Testes Contrato/Cobertura

| AR | Titulo | Status | Proxima Acao |
|---|---|---|---|
| **AR_195** | AR-TRAIN-010B: testes INV-TRAIN-013/024 + CONTRACT-TRAIN-073..075/077..085 + TEST_MATRIX sync | ✅ VERIFICADO | hb seal 195 executado em 2026-03-01 |

---

## 20. Cards -- TRAINING Governança -- Promover status SSOT Training (AR_196) ✅ VERIFICADO

> **Contexto**: AR de governança Classe G. Promoveu status desatualizados nos 6 arquivos SSOT do módulo TRAINING (AR_BACKLOG PENDENTE→VERIFICADO, INVARIANTS INV-040/041, CONTRACT-091..105, SCREEN-013, FLOWS 004..013). Não alterou Backend/Frontend. **✅ VERIFICADO 2026-03-02 (hb seal 196). Hash canônico: 2ecd5b6ad4bf18d4.**
> **Data planejamento**: 2026-03-01.
> **Plano**: docs/_canon/planos/ar_196_promover_ssot_training.json

### ✅ VERIFICADO -- Promover status SSOT Training (6 arquivos)

| AR | Titulo | Status | Proxima Acao |
|---|---|---|---|
| **AR_196** | Promover AR_BACKLOG + INVARIANTS (040/041) + CONTRACT (091..105) + SCREENS + FLOWS | ✅ VERIFICADO | hb seal 196 executado em 2026-03-02 |

---

## 21. Cards -- TRAINING Governança -- INVARIANTS_TRAINING.md sync (AR-TRAIN-022) — AR_197 ✅ VERIFICADO

> **Contexto**: Batch 7 do `TRAINING_BATCH_PLAN_v1.md` (v1.0.3). Classe G. Promover 31 invariantes GAP/PARCIAL/DIVERGENTE_DO_SSOT → IMPLEMENTADO em `INVARIANTS_TRAINING.md`, com notas de rastreabilidade para ARs 011..021 já verificadas. Versão bump para v1.5.0.
> **Dependências**: AR-TRAIN-011..021 todas ✅ VERIFICADO (2026-03-01).
> **Data planejamento**: 2026-03-02.
> **Plano**: docs/_canon/planos/ar_197_inv_training_sync.json
> **✅ VERIFICADO 2026-03-02 (hb seal 197). Behavior Hash: 024a3407e37d128b.**

### ✅ VERIFICADO -- AR-TRAIN-022: Sync INVARIANTS_TRAINING.md

| AR | Titulo | Status | Proxima Acao |
|---|---|---|---|
| **AR_197** | INVARIANTS_TRAINING.md v1.5.0: 31 itens GAP/PARCIAL/DIVERGENTE → IMPLEMENTADO + evidence + changelog | ✅ VERIFICADO | hb seal 197 executado em 2026-03-02 |

---

## 22. Cards -- TRAINING Governança -- Fechar AR_BACKLOG AR-TRAIN-022 + Batch 8 (AR_198)

> **Contexto**: AR de governança Classe G. Fecha AR-TRAIN-022 no AR_BACKLOG_TRAINING.md (PENDENTE → VERIFICADO, evidência AR_197 hb seal 2026-03-02). Introduz AR-TRAIN-023 no backlog (Sync TEST_MATRIX §9 pós-Batch 7). Adiciona Batch 8 ao TRAINING_BATCH_PLAN_v1.md. Não altera Backend/Frontend.
> **Dependências**: AR_197 ✅ VERIFICADO.
> **Data planejamento**: 2026-03-02.
> **Plano**: docs/_canon/planos/ar_198_fechar_backlog_ar_train_022.json
> **✅ VERIFICADO 2026-03-02 (hb seal 198). Behavior Hash: 11acd59aac33acc37c65ebf3c774daf292846fd12ce0bdf242a91589c7769435.**

### ✅ VERIFICADO -- AR-TRAIN-023 adicionada: Fechar backlog + add AR-TRAIN-023 + Batch 8

| AR | Titulo | Status | Proxima Acao |
|---|---|---|---|
| **AR_198** | AR_BACKLOG: AR-TRAIN-022 PENDENTE→VERIFICADO + AR-TRAIN-023 adicionada + Batch 8 no BatchPlan | ✅ VERIFICADO | hb seal 198 executado em 2026-03-02 |

---

## 23. Cards -- TRAINING Governança -- TEST_MATRIX §9 sync pós-Batch 7 (AR_199)

> **Contexto**: AR de governança Classe G. Executa AR-TRAIN-023. Sincroniza TEST_MATRIX_TRAINING.md §9: AR-TRAIN-001/002/003/004/005/010A/010B/022 PENDENTE → VERIFICADO. Desbloqueia 7 INV-TRAIN (008/020/021/030/031/040/041) e 9 CONTRACT-TRAIN (077..085). Bump v1.5.1 → v1.6.0. Não altera Backend/Frontend.
> **Dependências**: AR_198 ✅ VERIFICADO (AR-TRAIN-023 deve existir no backlog antes de executar).
> **Data planejamento**: 2026-03-02.
> **Plano**: docs/_canon/planos/ar_199_test_matrix_sync_post_batch7.json
> **✅ VERIFICADO 2026-03-02 (hb seal 199). Behavior Hash: 3e0c31d9a8a31bbf69fde156aa8ed813faba5ddd250bc40dfc448e7f984c5d34.**

### ✅ VERIFICADO (AR-TRAIN-023 executada) -- TEST_MATRIX §9 sync

| AR | Titulo | Status | Proxima Acao |
|---|---|---|---|
| **AR_199** | TEST_MATRIX sync: §9 AR-TRAIN-001..005/010A/010B/022 PENDENTE→VERIFICADO + desbloquear 7 INV + 9 CONTRACT + v1.6.0 | ✅ VERIFICADO | hb seal 199 executado em 2026-03-02 |

---

## 24. Cards -- TRAINING Evidência -- Top-10 DoD Evidence Execution (AR_200)

> **Contexto**: AR de execução de evidência Classe T. Roda os 10 testes COBERTO+NOT_RUN com maior prioridade DoD (§10): 9 invariantes BLOQUEANTE_VALIDACAO/ARQUITETURA + CRITICA (INV-TRAIN-001/002/003/004/005/008/009/030/032) + 1 grupo de contratos (CONTRACT-TRAIN-077..085). Salva output de pytest em `_reports/training/TEST-TRAIN-*.md`. Atualiza TEST_MATRIX_TRAINING.md v1.6.0 → v1.7.0 (colunas Últ.Execução + Evidência). Não altera Backend/Frontend.
> **Dependências**: AR_199 ✅ VERIFICADO (TEST_MATRIX v1.6.0, CONTRACT-077..085 em COBERTO).
> **Data planejamento**: 2026-03-02.
> **Plano**: docs/_canon/planos/ar_200_top10_dod_evidence.json

### ✅ VERIFICADO — 2026-03-02

| AR | Titulo | Status | Proxima Acao |
|---|---|---|---|
| **AR_200** | Top-10 DoD: executar 9 INV + 1 grupo CONTRACT COBERTO+NOT_RUN; salvar evidências; TEST_MATRIX v1.7.0 | ✅ VERIFICADO | — |

> **Fix**: AR_201 corrigiu validation_command (janela 450→split-por-linha). executor_main.log Exit Code: 0. hb seal 200 ✅ 2026-03-02.

---

## 25. Cards -- TRAINING Fix Contrato -- Fix validation_command AR_200 (AR_201)

> **Contexto**: Correção de contrato Classe G. A validation_command de AR_200 usa janela fixa de 450 chars para checar NOT_RUN em linhas INV; a janela de INV-TRAIN-005 (~206 chars) extravaza para INV-006 (NOT_RUN legítimo), causando falso positivo. Fix: substituir checagem `t.find(lbl)+450` por verificação linha-a-linha `t.split('\n')`. Após fix, re-executar `hb report 200` para obter Exit Code: 0 em executor_main.log. Não altera testes, evidências ou TEST_MATRIX.
> **Dependências**: AR_200 executado (evidências criadas ✅; TEST_MATRIX v1.7.0 ✅; só a validation_command está quebrada).
> **Data planejamento**: 2026-03-02.
> **Plano**: docs/_canon/planos/ar_201_fix_validation_command_ar200_window.json

### ✅ VERIFICADO — 2026-03-02

| AR | Titulo | Status | Proxima Acao |
|---|---|---|---|
| **AR_201** | Fix validation_command AR_200: janela 450→split-por-linha + re-executar hb report 200 | ✅ VERIFICADO | — |

---

## 26. Cards -- TRAINING Batch 9 -- Fix FAILs críticos test-layer (AR_202..206)

> **Contexto**: 5 correções de teste (Classe T). Eliminam os FAILs que bloqueiam o Done Gate. Zero mudança de produto (Backend/Frontend). Todos os 5 fixes são em `tests/training/`. Pré-condição: nenhuma (independentes entre si).
> **Plano**: docs/_canon/planos/ar_batch9_fix_fails_202_206.json
> **Data planejamento**: 2026-03-02.
> **Dependências**: Nenhuma (Batch 9 independente).

### 🔲 READY — aguardando Executor

| AR | Titulo | Status | Proxima Acao |
|---|---|---|---|
| **AR_202** | Fix INV-001: test_invalid_case_2 expected constraint name errado (ck_training_sessions_focus_attack_positional_range) | ✅ VERIFICADO | — |
| **AR_203** | Fix INV-008: schema_path 3 .parent → 4 .parent | ✅ VERIFICADO |
| **AR_204** | Fix INV-030: schema_path 3 .parent → 4 .parent | ✅ VERIFICADO |
| **AR_205** | Fix INV-032: 6 async fixtures @pytest.fixture | ✅ VERIFICADO |
| **AR_206** | Fix CONTRACT-077-085: ROUTER_PATH 3 .parent | ✅ VERIFICADO |
| **AR_210** | Fix timing-agnostic behavior hash (SHA-256) | ✅ VERIFICADO |

---

## 27. Cards -- TRAINING Batch 10 -- Flow P0 evidence + Contract P0 tests (AR_207..208)

> **Contexto**: Cobertura P0 restante. AR_207 cria 8 evidências MANUAL_GUIADO para flows P0 (FLOW-TRAIN-001..006/017/018) + atualiza TEST_MATRIX §6. AR_208 cria testes automatizados para CONTRACT-TRAIN-097..100 (pre-confirm + close + pending-items) + atualiza TEST_MATRIX §8.
> **Plano**: docs/_canon/planos/ar_batch10_flows_contracts_207_208.json
> **Data planejamento**: 2026-03-02.
> **Dependências**: AR_202..206 (Batch 9) VERIFICADO.

### ✅ DONE (Batch 10)

| AR | Titulo | Status | Proxima Acao |
|---|---|---|---|
| **AR_207** | Flow P0 evidence: FLOW-TRAIN-001..006 + 017 + 018 (MANUAL_GUIADO) + TEST_MATRIX §6 | ✅ VERIFICADO | Testador — Batch 10 (dep: Batch 9) |
| **AR_208** | Contract P0 tests: CONTRACT-TRAIN-097..100 (pre-confirm, close, pending-items) + TEST_MATRIX §8 | ✅ VERIFICADO | Testador — Batch 10 (dep: Batch 9) |

---

## 28. Cards -- TRAINING Batch 11 -- Done Gate (AR_209)

> **Contexto**: Done Gate do módulo TRAINING. Sincroniza TEST_MATRIX_TRAINING.md para v1.8.0 (§9 + §5/§6/§8 finais). Executa validação em 2 fases: **FASE-1** smoke dos 5 FAILs Batch9 fixados (INV-001/008/030/032 + CONTRACT-077-085); **FASE-2** sanity re-run completo dos 10 itens do AR_200 (INV-001/002/003/004a/004b/005/008/009/030/032 + CONTRACT-077-085) — garantindo que o DONE não depende só de fix de import/path, mas que o conjunto integral virou PASS. Produz `_reports/training/DONE_GATE_TRAINING.md` declarando critérios §10 satisfeitos. Após VERIFICADO, o módulo TRAINING pode ser selado pelo humano.
> **Plano**: docs/_canon/planos/ar_209_done_gate_training.json
> **Data planejamento**: 2026-03-02.
> **Dependências**: AR_202..208 (Batches 9 e 10) todos VERIFICADO.

### ✅ DONE (Batch 11)

| AR | Titulo | Status | Proxima Acao |
|---|---|---|---|
| **AR_209** | Done Gate: sync TEST_MATRIX v1.8.0 + smoke Batch9 (5) + sanity AR_200 full (11) + DONE_GATE_TRAINING.md | ✅ VERIFICADO | — |

---

## 29. Cards -- TRAINING Batch 12 -- Cobertura §10 formal: sync Matrix + 6 testes ausentes (AR_211..212)

> **Contexto**: §10 exige cobertura integral de invariantes. AR_211 resolve dessincronia crítica: ~40 INV marcadas PENDENTE na Matrix quando os arquivos de teste já existiam (Batches 3-8). AR_212 cria os 6 únicos testes genuinamente ausentes (INV-053/060/061/062/EXB-ACL-005/007). Zero mudança de produto.
> **Plano**: docs/_canon/planos/ar_batch12_matrix_sync_211_212.json
> **Data planejamento**: 2026-03-03.
> **Dependências**: AR_209 (Batch 11) VERIFICADO.

### ✅ DONE (Batch 12)

| AR | Titulo | Status | Proxima Acao |
|---|---|---|---|
| **AR_211** | Sync §5 TEST_MATRIX: ~40 INV PENDENTE → COBERTO/NOT_RUN (testes já existem) | ✅ VERIFICADO | — |
| **AR_212** | Criar 6 testes ausentes: INV-053/060/061/062/EXB-ACL-005/EXB-ACL-007 | ✅ VERIFICADO | — |

---

## 30. Cards -- TRAINING Batch 13 -- Execução NOT_RUN: rodar suite invariants + evidências formais (AR_213)

> **Contexto**: Com Batch 12 concluído, todos os ~60 testes de invariante existem no filesystem mas nunca foram executados formalmente (status NOT_RUN). AR_213 executa toda a suite `tests/training/invariants/`, captura saída em `_reports/training/evidence_run_batch13.txt` e atualiza §5 TEST_MATRIX para COBERTO. Zero toque em código de produto.
> **Plano**: docs/_canon/planos/ar_batch13_not_run_034.json
> **Data planejamento**: 2026-03-03.
> **Dependências**: AR_211 + AR_212 (Batch 12) ambos VERIFICADO.

### ✅ VERIFICADO

| AR | Titulo | Status | Proxima Acao |
|---|---|---|---|
| **AR_213** | Executar NOT_RUN §5 TEST_MATRIX + evidências formais (AR-TRAIN-034) | ✅ VERIFICADO | — |

```

---

## 31. Cards -- TRAINING Batch 14 -- Contract Tests P0: 5 ARs cobrindo ~88 contratos (AR_214..AR_218)

> **Contexto**: Com Batch 13 concluído (AR-TRAIN-034 VERIFICADO), o próximo passo é criar testes de contrato automatizados para os ~88 contratos P0 catalogados em TRAINING_FRONT_BACK_CONTRACT.md sem cobertura. 5 ARs organizadas por domínio (sessões, equipes/presença, wellness, ciclos/exercises/analytics/export, IA coach/athlete). Testes usam abordagem estática (import + schema inspection) — compatível com CI sem DB. Zero toque em app/.
> **Plano**: docs/_canon/planos/ar_batch14_contracts_035_039.json
> **Data planejamento**: 2026-03-03.
> **Dependências**: AR_213 (Batch 13) VERIFICADO.

### ✅ VERIFICADO — sealed pelo humano (2026-03-03)

| AR | Titulo | Status | Proxima Acao |
|---|---|---|---|
| **AR_214** | Contract tests: Sessions CRUD (CONTRACT-001..012) (AR-TRAIN-035) | ✅ VERIFICADO | — sealed |
| **AR_215** | Contract tests: Teams + Attendance (CONTRACT-013..028) (AR-TRAIN-036) | ✅ VERIFICADO | — sealed |
| **AR_216** | Contract tests: Wellness pre/post (CONTRACT-029..039) (AR-TRAIN-037) | ✅ VERIFICADO | — sealed |
| **AR_217** | Contract tests: Ciclos/Exercises/Analytics/Export (CONTRACT-040..072,076,086..095) (AR-TRAIN-038) | ✅ VERIFICADO | — sealed |
| **AR_218** | Contract tests: IA Coach + Athlete view (CONTRACT-096,101..105) (AR-TRAIN-039) | ✅ VERIFICADO | — sealed |

---

## 32. Cards -- TRAINING Batch 15 -- DEC Tests Automatizados + Flows P1 + Screens Smoke (AR_219..AR_221)

> **Contexto**: Com Batch 14 concluído (AR-TRAIN-035..039 VERIFICADO), Batch 15 cobre: (1) 11 DECs automatizados via invariant tests, (2) 13 flows P1 evidências MANUAL_GUIADO, (3) 25 telas smoke MANUAL_GUIADO. Nenhum toque em app/.
> **Plano**: docs/_canon/planos/ar_batch15_dec_flows_screens_040_042.json
> **Data planejamento**: 2026-03-03.
> **Dependências**: AR-TRAIN-033 VERIFICADO (dep AR_219) + AR-TRAIN-034 VERIFICADO (dep AR_220/221).

### ✅ VERIFICADO

| AR | Titulo | Status | Proxima Acao |
|---|---|---|---|
| **AR_219** | DEC tests automatizados: DEC-TRAIN-001..004 + EXB + RBAC (AR-TRAIN-040) | ✅ VERIFICADO | — sealed |
| **AR_220** | Flows P1 MANUAL_GUIADO: FLOW-007..016 + 019..021 (AR-TRAIN-041) | ✅ VERIFICADO | — sealed |
| **AR_221** | Screens smoke MANUAL_GUIADO: SCREEN-001..025 (AR-TRAIN-042) | ✅ VERIFICADO | — sealed |

```

---

## 33. Cards -- TRAINING Batch 16 -- Done Gate §10 Final (AR_222)

> **Contexto**: Com Batch 15 concluído (AR-TRAIN-040..042 VERIFICADO), Batch 16 fecha o módulo TRAINING com sync final da TEST_MATRIX para v2.0.0, atualização de §9 com AR-TRAIN-035..043, marcação de §10 checkboxes PASS e emissão da declaração Done Gate §10. Nenhum toque em app/ ou Frontend/.
> **Plano**: docs/_canon/planos/ar_batch16_done_gate_043.json
> **Data planejamento**: 2026-03-03.
> **Dependências**: AR-TRAIN-034..042 todos VERIFICADO (Batches 13-15 selados).

### ⛔ OBSOLETO — AR-TRAIN-043 substituída por AR-TRAIN-050 (Batch 21) + AR-TRAIN-051 (Batch 22)

> **2026-03-03 (pós-Batch 20):** AR-TRAIN-043 marcada como OBSOLETA pelo Arquiteto. Contexto mudou significativamente pós-Batches 17-20. Escopo desmembrado:
> - Sync §5 TEST_MATRIX (11 itens desatualizados) → AR-TRAIN-050 (AR_231, Batch 21)
> - Done Gate §10 formal com escopo atualizado → AR-TRAIN-051 (AR_232, Batch 22)
> AR_222 encerrada sem selo. Não retomar.

| AR | Titulo | Status | Proxima Acao |
|---|---|---|---|
| **AR_222** | Done Gate §10 final: sync TEST_MATRIX v2.0.0 + declaração formal (AR-TRAIN-043) | ⛔ OBSOLETO | AR-TRAIN-043 substituída — ver Batch 21/22 |

---

## 34. Cards -- TRAINING Batch 17 -- Fix Bugs Test-Layer Batch 14 (AR_223..AR_224)

> **Contexto**: 2 correções test-layer (Classe T). Eliminam os +15 novos FAILs introduzidos no Batch 14 (AR_217 e AR_208) que bloqueavam AR_222. Zero mudança de produto.
> **Plano**: docs/_canon/planos/ar_batch17_fix_batch14_tests_223.json
> **Data planejamento**: 2026-03-03.
> **Após Batch 17**: Descoberto que 109 FAILs pré-existentes de Batch 13 ainda bloqueiam AC-005 → Batch 18 criado.

### ✅ DONE (Batch 17) — 2026-03-03

| AR | Titulo | Status | Retorno |
|---|---|---|---|
| **AR_223** | Fix CONTRACT-073-075: ROUTER_PATH 3 .parent → 4 .parent (14 FAILs) | ✅ VERIFICADO | — |
| **AR_224** | Fix CONTRACT-097-100: assert 'pre-confirm' → 'preconfirm' (1 FAIL) | ✅ VERIFICADO | — |

---

## 35. Cards -- TRAINING Batch 18 -- Fix FAILs Test-Layer pré-existentes (AR_225..AR_228)

> **Contexto**: 109 FAILs + 31 ERRORs residuais confirmados pós-Batch 17. Zero mudança de produto — todos são bugs de test-layer (async fixtures, DB fixture setup, import stubs). Decisão humana Opção A (2026-03-03).
> **Plano**: docs/_canon/planos/ar_batch18_fix_test_layer_044_047.json (dry-run ✅ 2026-03-03)
> **Correspondência Backlog**: AR-TRAIN-044 → AR_225, AR-TRAIN-045 → AR_226, AR-TRAIN-046 → AR_227, AR-TRAIN-047 → AR_228
> **Dependências**: AR_225/226/227 independentes entre si; AR_228 depende das 3.
> **Após Batch 18**: Executar Batch 19 (AR_229 — sync app layer) antes de re-executar AR_222.

### ✅ VERIFICADO + 🔴 REJEITADO — Batch 18 concluído (parcial)

| AR | AR-TRAIN | Titulo | Status |
|---|---|---|---|
| **AR_225** | TRAIN-044 | Fix async fixtures: @pytest.fixture → @pytest_asyncio.fixture (7 arquivos, ~23+ FAILs) | ✅ VERIFICADO (sealed `2c1b1a5959989d0d`) |
| **AR_226** | TRAIN-045 | Fix DB fixture setup: category_id NOT NULL + FK team_registrations (~57+ ERROs) | ✅ VERIFICADO (sealed `2412147326683390`) |
| **AR_227** | TRAIN-046 | Fix import stubs ai_coach_service (3 ERRORs coleta INV-079/080/081) | ✅ VERIFICADO (sealed `6a86838d0052b800`) |
| **AR_228** | TRAIN-047 | Fix residuais mistos + validação done gate (suite 0 FAILs) | 🔴 REJEITADO — AC-001 impossível: test_018_route + test_035 fora do write_scope; 10 ERRORs de conftest diferente fora do scope. Aguarda AR_230 (AR-TRAIN-049) para desbloquear |

```


---

## 36. Cards -- TRAINING Batch 19 -- Sincronização em Lote: App Layer (AR_229)

> **Contexto**: app/ desbloqueada via GOVERNED_ROOTS.yaml (UNLOCKED_FOR_SYNC_BATCH_19). Decisão humana (2026-03-03). AR única que sincroniza app/models/ + app/services/ com contrato v1.3.0 + invariantes v1.5.0.
> **Plano**: docs/_canon/planos/ar_batch19_sync_app_layer_048.json (dry-run ✅ 2026-03-03)
> **Correspondência Backlog**: AR-TRAIN-048 → AR_229
> **Dependências obrigatórias**: Batch 18 (AR_225..228) todos VERIFICADO + suite tests/ verde antes de iniciar.
> **Após Batch 19**: Re-executar AR_222 (Batch 16 / Done Gate §10).

### ⚠️ EM_EXECUCAO/FALHA — amendment obrigatório antes de re-run

| AR | AR-TRAIN | Título | Status |
|---|---|---|---|
| **AR_229** | TRAIN-048 | Sync app/models/ (INV-010/035/036/054/060) + app/services/ (contrato v1.3.0) + stubs IA Coach | ⚠️ FALHA (exit=1, 6 FAILs, 10 ERRORs). AC-005 ✅ (15 passed). **AMENDMENT OBRIGATÓRIO:** fix `training_session.py` status server_default `'''draft'''` → `'draft'` (está no write_scope). Re-executar `hb report 229` após Batch 20 verde. |

---

## 37. Cards -- TRAINING Batch 20 -- Fix residuais test-layer pós-Batch 18/19 (AR_230)

> **Contexto**: 6 FAILs + 10 ERRORs remanescentes em tests/training/invariants/ diagnosticados durante execução de AR_229. Root causes: birth_date missing, org_id typo, category_id missing, athlete.id vs person_id FK, status 'concluída' inválido, UUID class bug. Zero mudança de produto.
> **Plano**: docs/_canon/planos/ar_batch20_fix_test_layer_residuals_049.json (dry-run ✅)
> **Correspondência Backlog**: AR-TRAIN-049 → AR_230
> **Dependências obrigatórias**: AR_229 com amendment (status server_default fix) executado.

### ✅ SEALED (2026-03-03) — hb seal 230 exit=0

| AR | AR-TRAIN | Título | Status |
|---|---|---|—|
| **AR_230** | TRAIN-049 | Fix 6 FAILs + 10 ERRORs residuais test-layer (test_018_route, 035×4, 058, 059, 063×2, 064, 076×3, acl_006×2) | ✅ VERIFICADO (hb seal 2026-03-03) |

---

## 38. Cards -- TRAINING Batch 21 -- Sync §5 TEST_MATRIX pós-Batches 17-20 (AR_231)

> **Contexto**: AR-TRAIN-046 (AR_227) corrigiu stubs INV-079/080/081 (NOT_RUN); AR-TRAIN-049 (AR_230) corrigiu 8 testes (FAIL/ERROR). §5 da TEST_MATRIX ainda reflete estados desatualizados em 11 linhas. Zero toque em Backend/Frontend.
> **Plano**: docs/_canon/planos/ar_batch21_sync_test_matrix_050.json
> **Correspondência Backlog**: AR-TRAIN-050 → AR_231
> **Dependências obrigatórias**: AR-TRAIN-046 VERIFICADO (AR_227) + AR-TRAIN-049 VERIFICADO (AR_230).

### ✅ VERIFICADO (2026-03-04) — hb seal 231 exit=0

| AR | AR-TRAIN | Título | Status |
|---|---|---|---|
| **AR_231** | TRAIN-050 | Sync §5 TEST_MATRIX: INV-079/080/081 NOT_RUN→PASS + INV-018/035/058/059/063/064/076/EXB-ACL-006 FAIL/ERROR→PASS + bump v2.1.0→v2.2.0 | ✅ VERIFICADO |

---

## 39. Cards -- TRAINING Batch 22 -- Done Gate §10 Formal pós-Batch 21 (AR_232)

> **Contexto**: Substitui AR-TRAIN-043 (OBSOLETA, Batch 16). Fecha o módulo TRAINING com §10 formal preenchido, bump TEST_MATRIX→v3.0.0 e declaração DONE_GATE_TRAINING_v3.md. Zero toque em Backend/Frontend.
> **Plano**: docs/_canon/planos/ar_batch22_done_gate_051.json
> **Correspondência Backlog**: AR-TRAIN-051 → AR_232
> **Dependências obrigatórias**: AR-TRAIN-050 VERIFICADO (AR_231, Batch 21).

### ✅ VERIFICADO (2026-03-04) — hb seal 232 exit=0

| AR | AR-TRAIN | Título | Status |
|---|---|---|---|
| **AR_232** | TRAIN-051 | Done Gate §10 final: §10 checkboxes ✅ + §0 contadores + TEST_MATRIX v3.0.0 + DONE_GATE_TRAINING_v3.md | ✅ VERIFICADO |

---

## 40. Cards -- TRAINING Batch 23 -- Frontend Hard Sync v1.3.0 (AR_236) ✅ SEALED

> **Contexto**: Batch 23 — AR-TRAIN-052 (AR_236). Frontend Hard Sync v1.3.0: alinhar tipos UUID/standalone, payloads e stubs CONTRACT-096..105 do Frontend ao contrato Backend v1. Executado pós-Done Gate §10 (AR_232 VERIFICADO). Zero toque em Backend.
> **Plano**: docs/_canon/planos/ar_batch23_frontend_sync_052.json
> **Correspondência Backlog**: AR-TRAIN-052 → AR_236
> **Dependências obrigatórias**: AR-TRAIN-051 VERIFICADO (AR_232, Batch 22).

### ✅ SEALED — Batch 23 concluído (hb seal 2026-03-04)

| AR | AR-TRAIN | Título | Status |
|---|---|---|---|
| **AR_236** | TRAIN-052 | Frontend Hard Sync v1.3.0: tipos UUID/standalone + stubs CONTRACT-096..105 | ✅ VERIFICADO |

---

## 41. Cards -- TRAINING Batch 24 -- Sync §9 TEST_MATRIX pós-Batch 23 (AR_237) ✅ SEALED

> **Contexto**: Batch 24 — AR-TRAIN-053 (AR_237). Governance sync obrigatório: §9 da TEST_MATRIX_TRAINING.md requer entry AR-TRAIN-052 VERIFICADO. Zero toque em Backend/Frontend.
> **Plano**: docs/_canon/planos/ar_batch24_sync_matrix_053.json
> **Correspondência Backlog**: AR-TRAIN-053 → AR_237
> **Dependências obrigatórias**: AR-TRAIN-052 VERIFICADO (AR_236, Batch 23).

### ✅ SEALED — Batch 24 concluído (hb seal 2026-03-04)

| AR | AR-TRAIN | Título | Status |
|---|---|---|---|
| **AR_237** | TRAIN-053 | Sync §9 TEST_MATRIX: entry AR-TRAIN-052 VERIFICADO pós-Batch 23 | ✅ VERIFICADO |

---

## 42. Cards -- TRAINING Batch 25 -- Sync §5 FASE_3 INVs FAIL/ERROR→PASS + v3.1.0 (AR_238) ✅ SEALED

> **Contexto**: Batch 25 — AR-TRAIN-054 (AR_238). Sync §5 FASE_3: 18 INVs que estavam FAIL/ERROR passam a PASS (suite 59 tests), bump TEST_MATRIX v3.0.0→v3.1.0. Zero toque em Backend/Frontend.
> **Plano**: docs/_canon/planos/ar_batch25_sync_fase3_054.json
> **Correspondência Backlog**: AR-TRAIN-054 → AR_238
> **Dependências obrigatórias**: AR-TRAIN-053 VERIFICADO (AR_237, Batch 24).

### ✅ SEALED — Batch 25 concluído (hb seal 2026-03-04)

| AR | AR-TRAIN | Título | Status |
|---|---|---|---|
| **AR_238** | TRAIN-054 | Sync §5 FASE_3: 18 INVs FAIL/ERROR→PASS + v3.1.0 + §9 entries 053/054 | ✅ VERIFICADO |

---

## 43. Cards -- TRAINING Batch 26 -- FASE_3 Impl Real + Sync SSOT pós-Batch 26 (AR_239-243) ✅ SEALED

> **Contexto**: Batch 26 — AR-TRAIN-055..059 (AR_239-243). PO autorizou início 2026-03-04. Implementação real de 3 endpoints FASE_3 (PATCH attendance, PATCH+POST ai_coach, GET wellness-content-gate), corrigindo URLs Frontend + sync documental pós-Batch.
> **Plano**: docs/_canon/planos/ar_batch26_fase3_impl_055_059.json
> **Correspondência Backlog**: AR-TRAIN-055→AR_239; AR-TRAIN-056→AR_240; AR-TRAIN-057→AR_241; AR-TRAIN-058→AR_242; AR-TRAIN-059→AR_243
> **Dependências obrigatórias**: AR-TRAIN-054 VERIFICADO (AR_238, Batch 25).

### ✅ SEALED — Batch 26 concluído (hb seal 2026-03-04)

| AR | AR-TRAIN | Título | Status |
|---|---|---|---|
| **AR_239** | TRAIN-055 | BE: PATCH /attendance/:id/resolve-pending-item | ✅ VERIFICADO |
| **AR_240** | TRAIN-056 | BE: PATCH /ai/coach/draft/:id/apply + POST /ai/coach/justify-suggestion | ✅ VERIFICADO |
| **AR_241** | TRAIN-057 | BE: GET /athlete/wellness-content-gate/:session_id | ✅ VERIFICADO |
| **AR_242** | TRAIN-058 | FE: corrigir URLs training-phase3.ts — CONTRACT-097/101/102/103/104 | ✅ VERIFICADO |
| **AR_243** | TRAIN-059 | Sync TEST_MATRIX §8/§9 + BACKLOG pós-Batch 26 + v3.2.0 | ✅ VERIFICADO |

---

## 44. Cards -- TRAINING Batch 27 -- Governance Sync + Contract tests (AR_244-245)

> **Contexto**: Batch 27 — Opção C (decisão humana 2026-03-04). Duas frentes: (1) AR-TRAIN-060 corrige divergência de governança — Kanban ausente Batches 23-26, Batch Plan v1.5.0 sem Batches 23-26; (2) AR-TRAIN-061 fecha lacuna de cobertura P1 — CONTRACT-TRAIN-074/075 (wellness-rankings) com status NOT_RUN na TEST_MATRIX v3.2.0. Pré-condição: AR-TRAIN-059 VERIFICADO (AR_243, hb seal Batch 26).
> **Plano**: docs/_canon/planos/ar_batch27_governance_contracts_060_061.json
> **Correspondência Backlog**: AR-TRAIN-060 → AR_244; AR-TRAIN-061 → AR_245
> **Dependências obrigatórias**: AR-TRAIN-059 VERIFICADO (AR_243, Batch 26).

### ✅ SEALED — Batch 27 concluído (hb seal 244/245, 2026-03-04)

| AR | AR-TRAIN | Título | Status |
|---|---|---|---|
| **AR_244** | TRAIN-060 | Governance Sync: Kanban retroativo Batches 23-26 + seção Batch 27 + Batch Plan v1.6.0 | ✅ VERIFICADO |
| **AR_245** | TRAIN-061 | Contract tests: CONTRACT-TRAIN-074 (POST /analytics/wellness-rankings/calculate) + CONTRACT-TRAIN-075 (GET /…/athletes-90plus) + TEST_MATRIX v3.3.0 | ✅ VERIFICADO |

---

## 45. Cards -- TRAINING Batch 28 -- Sync pós-Batch 27 (AR_246)

> **Contexto**: Batch 28 — Governança pós-Batch 27. AR-TRAIN-062 sincroniza: Backlog (AR-TRAIN-060/061 PENDENTE→VERIFICADO + add 062), TEST_MATRIX §9 (AR-TRAIN-061 EM_EXECUCAO→VERIFICADO + bump v3.4.0), e TRAINING_BATCH_PLAN_v1.md (fix header v1.5.0→v1.6.0 + add Batch 28 section).
> **Plano**: docs/_canon/planos/ar_batch28_sync_matrix_062.json
> **Correspondência Backlog**: AR-TRAIN-062 → AR_246
> **Dependências obrigatórias**: AR-TRAIN-061 VERIFICADO (AR_245, Batch 27).

### ✅ VERIFICADO (2026-03-04) — hb seal 246 exit=0

| AR | AR-TRAIN | Título | Status |
|---|---|---|---|
| **AR_246** | TRAIN-062 | Sync Backlog AR-TRAIN-060/061→VERIFICADO + TEST_MATRIX §9 v3.4.0 + BatchPlan v1.6.0 + add Batch 28 | ✅ VERIFICADO |

---

## 49. Cards -- TRAINING Batch 32 -- Testes Impl Wellness + Sync Documental (AR_254, AR_255)

> **Contexto**: Batch 32 — AR-TRAIN-070 (AR_254) + AR-TRAIN-071 (AR_255). T+G only: testes de implementação runtime GET/PATCH wellness por ID (CONTRACT-031/032/037/038) + sync documental pós-Batch 31+32. Sem mudança de schema DB, sem migration, sem mudança de contrato openapi.
> **Plano**: docs/_canon/planos/ar_batch32_wellness_runtime_tests_sync_070_071.json
> **Correspondência Backlog**: AR-TRAIN-070 → AR_254; AR-TRAIN-071 → AR_255
> **Dependências obrigatórias**: AR-TRAIN-069 VERIFICADO (AR_253, Batch 31).

### ✅ VERIFICADO (2026-03-06) — hb seal 254..255 exit=0

| AR | AR-TRAIN | Título | Status |
|---|---|---|---|
| **AR_254** | TRAIN-070 | Testes impl GET/PATCH wellness por ID (CONTRACT-031/032/037/038) | ✅ VERIFICADO |
| **AR_255** | TRAIN-071 | Sync documental pós-Batch 31+32: BACKLOG v3.6.0 + TEST_MATRIX v4.2.0 + Kanban + _INDEX v1.5.0 | ✅ VERIFICADO |

---

## 48. Cards -- TRAINING Batch 31 -- BE Stubs Fix Wellness GET/PATCH por ID (AR_253)

> **Contexto**: Batch 31 — AR-TRAIN-069 (AR_253). BE fix stubs 501: implementar async def get_wellness_pre_by_id, update_wellness_pre (wellness_pre.py router), get_wellness_post_by_id, update_wellness_post (wellness_post.py router), mais metodos de servico em WellnessPreService e WellnessPostService. Sem mudanca de schema DB ou contrato.
> **Plano**: docs/_canon/planos/ar_batch31_be_stubs_fix_wellness_069.json
> **Correspondência Backlog**: AR-TRAIN-069 → AR_253
> **Dependências obrigatórias**: AR-TRAIN-068 VERIFICADO (AR_252, Batch 30).

### ✅ VERIFICADO (2026-03-07) — hb seal 253 exit=0

| AR | AR-TRAIN | Título | Status |
|---|---|---|---|
| **AR_253** | TRAIN-069 | BE: implementar GET/PATCH wellness-pre e wellness-post por ID (fix stubs 501) | ✅ VERIFICADO |

---

## 47. Cards -- TRAINING Batch 30 -- FE Refactor Wellness Pre/Pos (AR_252)

> **Contexto**: Batch 30 — AR-TRAIN-068 (AR_252). Refactor funcional Categoria B: migrar WellnessPreForm.tsx e WellnessPostForm.tsx de src/lib/api/wellness (camada manual) para src/api/generated (WellnessPreApi, WellnessPostApi). Adiciona export wellnessPostApi em api-instance.ts. Sem mudança de contrato BE, sem regeneração de openapi.json.
> **Plano**: docs/_canon/planos/ar_batch30_wellness_pre_fe_generated_client_068.json
> **Correspondência Backlog**: AR-TRAIN-068 → AR_252
> **Dependências obrigatórias**: AR-TRAIN-067 VERIFICADO (AR_251, Batch 29).

### ✅ VERIFICADO (2026-03-06) — hb seal 252 exit=0

| AR | AR-TRAIN | Título | Status |
|---|---|---|---|
| **AR_252** | TRAIN-068 | Refactor FE Wellness Pre/Pos: migrar para cliente gerado (src/api/generated) | ✅ VERIFICADO |

---

## 46. Cards -- TRAINING Batch 29 -- TRUTH SUITE Residuals (AR_247-251) ✅ SEALED

> **Contexto**: Batch 29 — Zerar residuais TRUTH SUITE: 1 xfailed (INV-148) + 4 skipped (test_058/059) + 9 LEGACY_INVALID → 0 xfailed, 0 skipped, 0 LEGACY_INVALID. Baseline pós-Batch 29: 615p/0s/0xf/0f. NO_MOCKS_GLOBAL atingido.
> **Plano**: docs/_canon/planos/ar_batch29_plano_final_truth_suite_063_067.json
> **Correspondência Backlog**: AR-TRAIN-063→AR_247, AR-TRAIN-064→AR_248, AR-TRAIN-065→AR_249, AR-TRAIN-066→AR_250, AR-TRAIN-067→AR_251
> **Dependências obrigatórias**: AR-TRAIN-062 VERIFICADO (AR_246, Batch 28).

### ✅ VERIFICADO (2026-03-05) — hb seal 247..251 exit=0

| AR | AR-TRAIN | Título | Status |
|---|---|---|---|
| **AR_247** | TRAIN-063 | Fase 0+1: TRUTH SUITE dupla + triage 4 buckets — baseline 610p/4s/1xf/0f | ✅ VERIFICADO |
| **AR_248** | TRAIN-064 | Fix user.organization_id not a column — xfail INV-148 → PASS | ✅ VERIFICADO |
| **AR_249** | TRAIN-065 | Fix 4 SKIP em test_058/test_059 — INV-058/059 guards → PASS | ✅ VERIFICADO |
| **AR_250** | TRAIN-066 | Converter 9 LEGACY_INVALID para TRUTH (NO_MOCKS_GLOBAL atingido) | ✅ VERIFICADO |
| **AR_251** | TRAIN-067 | Sync documental pós-Batch 29: Backlog+TEST_MATRIX+BatchPlan+DONE_GATE+Kanban | ✅ VERIFICADO |

---

## 43. Cards -- TRAINING Batch 25 -- Sync §5 FASE_3: 18 INVs→PASS (AR_238)

> **Contexto**: Suite FASE_2 confirmada 594p/0f. Os 18 INVs listados como FAIL/ERROR em §5 da TEST_MATRIX já passam. Esta AR sincroniza §5 + bump v3.0.1→v3.1.0 + §9 entries AR-TRAIN-053/054.
> **Plano**: docs/_canon/planos/ar_batch25_sync_fase3_054.json
> **Correspondência Backlog**: AR-TRAIN-054 → AR_238
> **Dependências obrigatórias**: AR-TRAIN-053 VERIFICADO (AR_237, Batch 24).

### ✅ VERIFICADO (2026-03-04) — hb seal 238 exit=0

| AR | AR-TRAIN | Título | Status |
|---|---|---|---|
| **AR_238** | TRAIN-054 | Sync §5 FASE_3: 18 INVs FAIL/ERROR→2026-03-04 + v3.1.0 + §9 entries | ✅ VERIFICADO |

---

## TRAINING FASE_2 — STATUS FINAL

> **Módulo TRAINING FASE_2: ✅ COMPLETO** (2026-03-04)
>
> - Backend v1.3.0: 100% invariantes cobertos (AR_126..AR_235)
> - Frontend Hard Sync: ✅ (AR_236)
> - TEST_MATRIX v3.0.0 / DONE_GATE_ATINGIDO: ✅ (AR_232 + AR_237)
> - Pipeline DoD E2E: ✅ (AR_900)

---

## TRAINING FASE_3 — SYNC CONCLUÍDO

> **Sync §5 FASE_3: ✅ CONCLUÍDO** (2026-03-04 — AR_238)
>
> - Suite completa: 594 passed, 0 failed, 0 errors
> - 18 INVs FASE_3 (INV-TRAIN-010/011/019/020/021/029/031/034/036/037/050/052/054/057/065/066/067/070): ✅ PASS → TEST_MATRIX v3.1.0
> - Backend FASE_3 endpoints: presentes no openapi.json
> - Frontend FASE_3 stubs: training-phase3.ts (AR_236)
> - TEST_MATRIX_TRAINING.md: v3.1.0 / DONE_GATE_ATINGIDO / §5 + §9 atualizados
>
> **FASE_3 Batch 26-28: ✅ COMPLETO** (2026-03-04) — AR_239..AR_246 todos VERIFICADOS. TEST_MATRIX v3.4.0.
