# 📋 Relatório de Dívida Técnica — HB Track
> **Auditoria Senior:** 2026-02-21 | Escopo: 46 ARs materializadas em `docs/hbtrack/ars/`
> **Método:** Cross-reference entre código implementado (ARs ✅) e arquivos `.md` de invariantes

---

## 1. Invariantes Não Documentadas

> Regras de negócio **implementadas no código** (via ARs concluídas) que **ainda não possuem** um arquivo `.md` correspondente na pasta de invariantes modulares. A pasta `docs/hbtrack/modulos/` **não possui nenhum arquivo INVARIANTS_.md** — toda a dívida de documentação está em aberto.

### 1.1 Domínio: Competitions (implementado via AR_001, AR_008, AR_009, AR_003)

| ID Proposto | Classe | Regra Implementada | Evidência (AR) | Arquivo Invariante Ausente |
|-------------|--------|--------------------|----------------|---------------------------|
| INV-COMP-001 | **A** (DB Constraint) | Soft delete obrigatório em 5 tabelas: `competition_matches`, `competition_opponent_teams`, `competition_phases`, `match_events`, `match_roster` — par `(deleted_at, deleted_reason)` enforced por CHECK `ck_{tabela}_deleted_reason`: `(IS NULL AND IS NULL) OR (IS NOT NULL AND IS NOT NULL)` | AR_008 ✅ | `docs/hbtrack/modulos/competitions/INVARIANTS_COMPETITIONS.md` |
| INV-COMP-002 | **B** (Trigger) | Trigger `trg_{tabela}_block_delete` nas 5 tabelas bloqueia DELETE físico (EXIT EXCEPTION), forçando que toda remoção seja via soft delete. Função base `trg_block_physical_delete()` já existia no schema. | AR_008 ✅ | `docs/hbtrack/modulos/competitions/INVARIANTS_COMPETITIONS.md` |
| INV-COMP-003 | **A** (DB Constraint) | `competition_standings.team_id NOT NULL FK → teams.id ON DELETE RESTRICT` — classificação DEVE estar vinculada diretamente a uma equipe cadastrada; impede registro órfão | AR_001 ✅ | `docs/hbtrack/modulos/competitions/INVARIANTS_COMPETITIONS.md` |
| INV-COMP-004 | **C2** (Model) | Models `CompetitionMatch`, `CompetitionOpponentTeam`, `CompetitionPhase`, `MatchEvent`, `MatchRoster` expõem `deleted_at` e `deleted_reason` como `mapped_column` opcionais; queries de listagem DEVEM filtrar `WHERE deleted_at IS NULL` por padrão | AR_009 ✅ | `docs/hbtrack/modulos/competitions/INVARIANTS_COMPETITIONS.md` |

### 1.2 Domínio: Scout / Match Events (implementado via AR_003)

| ID Proposto | Classe | Regra Implementada | Evidência (AR) | Arquivo Invariante Ausente |
|-------------|--------|--------------------|----------------|---------------------------|
| INV-SCOUT-001 | **F** (OpenAPI/Pydantic) | `CanonicalEventType` enum: apenas 11 valores válidos (`goal`, `shot`, `seven_meter`, `goalkeeper_save`, `turnover`, `foul`, `exclusion_2min`, `yellow_card`, `red_card`, `substitution`, `timeout`). Valores legados (`goal_7m`, `own_goal`, `shot_on_target`, `assist`, `technical_foul`) são **inválidos** e devem retornar 422 | AR_003 ✅ | `docs/hbtrack/modulos/scout/INVARIANTS_SCOUT.md` |
| INV-SCOUT-002 | **C1** (Service Pure) | Quando `event_type = 'goalkeeper_save'`, o campo `related_event_id` é **OBRIGATÓRIO**. Pydantic validator levanta `ValidationError` se ausente. Regra: toda defesa deve referenciar o evento de arremesso original | AR_003 ✅ | `docs/hbtrack/modulos/scout/INVARIANTS_SCOUT.md` |
| INV-SCOUT-003 | **F** (OpenAPI/Pydantic) | `ScoutEventCreate` exige campos de posicionamento na escala 0–100: `x_coord ∈ [0, 100]`, `y_coord ∈ [0, 100]`. Valores fora deste range retornam 422 | AR_003 ✅ | `docs/hbtrack/modulos/scout/INVARIANTS_SCOUT.md` |
| INV-SCOUT-004 | **F** (OpenAPI/Pydantic) | Campo `source` de `ScoutEventCreate` é `Literal['live', 'video', 'post_game_correction']` — nenhum outro valor é aceito | AR_003 ✅ | `docs/hbtrack/modulos/scout/INVARIANTS_SCOUT.md` |

### 1.3 Domínio: Wellness (divergência detectada via AR_002.5_C)

| ID Proposto | Classe | Regra Real (Schema) | Regra PRD (Incorreta) | Evidência | Ação |
|-------------|--------|--------------------|-----------------------|-----------|------|
| INV-WELLNESS-001 | **A** (DB Constraint) | `stress_level ∈ [0, 10]` (proxy de humor — semântica **inversa**: 0=ótimo, 10=estressado) | PRD diz "1-5" | AR_002.5_C 🔲 | Atualizar PRD + criar invariante |
| INV-WELLNESS-002 | **A** (DB Constraint) | `fatigue_pre ∈ [0, 10]` | PRD diz "1-5" | AR_002.5_C 🔲 | Idem |
| INV-WELLNESS-003 | **A** (DB Constraint) | `muscle_soreness ∈ [0, 10]` | PRD diz "1-5" | AR_002.5_C 🔲 | Idem |
| INV-WELLNESS-004 | **A** (DB Constraint) | `sleep_quality ∈ [1, 5]` | PRD diz "1-5" ✅ | AR_002.5_C 🔲 | Apenas documentar |
| INV-WELLNESS-005 | **A** (DB Constraint) | `sleep_hours` é `numeric(4,1)` em horas reais (ex: 7.5h) | NÃO estava no PRD | AR_002.5_C 🔲 | Adicionar ao PRD |

---

## 2. Inconsistências de Status no _INDEX.md

| AR | Status no INDEX | Status Real (AR body) | Risco | Ação |
|----|----------------|-----------------------|-------|------|
| **AR_003** | DESCONHECIDO | ✅ SUCESSO (execution stamp presente) | Baixo — AR parece concluída | Executar `hb report AR_003` para sincronizar _INDEX |
| **AR_008** | ✅ CONCLUIDO | ❌ FALHA (execution stamp linha 111 mostra exit code 1) | **ALTO** — migration 0055 pode não estar aplicada no DB local | Verificar `alembic current` + re-executar se necessário |

---

## 3. Funcionalidades Implementadas Não Refletidas no PRD (antes desta auditoria)

| Funcionalidade | Implementada em | Status PRD (antes) | Atualização feita |
|---------------|-----------------|-------------------|-------------------|
| Soft delete (5 tabelas competitions/scout) | AR_008 ✅ + AR_009 ✅ | "EXECUTING (infra bloqueada)" | ✅ PRD §4.2 atualizado (21/02) |
| Schemas Pydantic canônicos de scout | AR_003 ✅ | Não mencionado | ✅ SCOUT-001 adicionado na tabela PRD §4.2 |
| competition_standings.team_id migration | AR_001 ✅ | BACKLOG | ✅ PRD §4.2 mostra PARCIAL (migration ✅, model 🔲) |
| ScoutEventCreate com validação goalkeeper | AR_003 ✅ | Não mencionado | ✅ SCOUT-001 adicionado |
| COMP-DB-006 (check constraints) | ARs 040-042 planejadas | Ausente do PRD | ✅ Linha COMP-DB-006 adicionada no PRD |
| Escalas reais wellness_pre (0-10 vs 1-5) | Schema real | PRD dizia "1-5" incorretamente | ✅ PRD §7 US-002 corrigido + glossário |

---

## 4. Dívida de Infra — Rename Frontend

> **Severidade: ALTA** — afeta CI/CD, Dockerfile, scripts e referências de import

O diretório `Hb Track - Fronted/` foi renomeado para `Hb Track - Frontend/` (git status mostra 150+ arquivos R/renamed), mas:
- AR_014 (git mv do diretório) → 🔲 PENDENTE
- AR_015 (update de referências em scripts/docs) → 🔲 PENDENTE
- Arquivos de configuração (`next.config.ts`, `Dockerfile`, CI/CD scripts) podem ainda referenciar o path antigo.

**Risco:** Deploy em VPS pode falhar se scripts referenciarem `Hb Track - Fronted/` que não existe mais.

---

## 5. Próximas Ações Priorizadas

| Prioridade | Ação | AR | Responsável |
|-----------|------|----|-------------|
| P0 | Verificar AR_008: `alembic current` confirma migration 0055 aplicada? | AR_008 | Executor |
| P0 | Sincronizar _INDEX: AR_003 status DESCONHECIDO → ✅ SUCESSO | AR_003 | hb_cli |
| P0 | Fechar AR_002 (model standings team_id) para desbloquear COMP-DB-003..006 | AR_002 | Executor |
| P0 | Executar AR_014 + AR_015 (rename Frontend) antes de qualquer deploy | AR_014-015 | Executor |
| P1 | Criar `docs/02-modulos/competitions/INVARIANTS_COMPETITIONS.md` com INV-COMP-001..004 | — | Arquiteto |
| P1 | Criar `docs/02-modulos/scout/INVARIANTS_SCOUT.md` com INV-SCOUT-001..004 | — | Arquiteto |
| P1 | Resolver AR_002.5_C: decisão PO sobre escala 0-10 vs 1-5 no wellness | AR_002.5_C | PO + Arquiteto |
| P2 | Fechar pipeline COMP-DB-003..006 (AR_036..042) | AR_036-042 | Executor |
| P2 | Concluir SCOUT-002 + SCOUT-003 (AR_004 + AR_005) | AR_004-005 | Executor |

---

*Gerado por auditoria técnica senior — 2026-02-21. Não editar manualmente — atualizar via nova AR de auditoria.*
