# TEST_MATRIX_COMPETITIONS.md

Status: DRAFT
Versão: v0.1.0
Tipo de Documento: Verification & Traceability Matrix (Normativo Operacional / SSOT)
Módulo: COMPETITIONS
Fase: FASE_0 / FASE_1
Autoridade: NORMATIVO_OPERACIONAL
Owners:
- Arquitetura (Arquiteto): Agente Arquiteto
- Auditoria/Testes: Agente Testador
- Backend: Agente Executor

Última revisão: 2026-02-25
Próxima revisão recomendada: 2026-03-15

Dependências:
- INVARIANTS_COMPETITIONS.md
- COMPETITIONS_USER_FLOWS.md
- COMPETITIONS_SCREENS_SPEC.md
- COMPETITIONS_FRONT_BACK_CONTRACT.md
- AR_BACKLOG_COMPETITIONS.md

---

## 1. Objetivo (Normativo)

Garantir rastreabilidade e cobertura verificável entre contratos do módulo (INV/FLOW/SCREEN/CONTRACT), ARs de materialização, testes e evidências de execução.

---

## 2. Escopo

### 2.1 Dentro do escopo
- Mapeamento de cobertura por item do MCP
- Testes de violação de invariantes bloqueantes (obrigatório)
- Testes de fluxo (happy path e exceções)
- Testes de contrato front-back
- Evidências mínimas por item crítico

### 2.2 Fora do escopo
- Código dos testes
- Testes de performance/carga
- QA visual/pixel-perfect
- Scout (módulo separado)

---

## 3. Convenções

### Tipos de teste
UNIT | INTEGRATION | CONTRACT | E2E | MANUAL_GUIADO | GATE_CHECK | REGRESSION

### Criticidade
CRITICA | ALTA | MEDIA | BAIXA

### Status de cobertura
COBERTO | PARCIAL | PENDENTE | BLOQUEADO | NAO_APLICAVEL

### Última execução
PASS | FAIL | NOT_RUN

---

## 4. Regras Normativas

1. Toda invariante bloqueante DEVE ter pelo menos 1 teste de violação.
2. Todo fluxo principal DEVE ter cobertura E2E ou MANUAL_GUIADO.
3. Todo CONTRACT de alta prioridade DEVE ter teste de integração/contrato.
4. Teste de caminho feliz NÃO substitui teste de violação de invariante.
5. Item `COBERTO` DEVE ter referência de evidência objetiva.
6. Item `IMPLEMENTADO` sem cobertura deve ser marcado `PARCIAL` ou `PENDENTE`.

---

## 5. Matriz de Cobertura por Invariantes

| ID | Nome Curto | Tier | Classe | ID Teste | Tipo | Violação? | Criticidade | Cobertura | Últ. Exec | Evidência | AR |
|----|------------|------|--------|----------|------|-----------|-------------|-----------|-----------|-----------|-----|
| INV-COMP-001 | ck_competitions_status | DB_CONSTRAINT | A | TEST-COMP-INV-001-INT | INTEGRATION | SIM | CRITICA | PARCIAL | NOT_RUN | schema.sql:ck_competitions_status | AR-COMP-001 |
| INV-COMP-002 | ck_competitions_modality | DB_CONSTRAINT | A | TEST-COMP-INV-002-INT | INTEGRATION | SIM | CRITICA | PARCIAL | NOT_RUN | schema.sql:ck_competitions_modality | AR-COMP-001 |
| INV-COMP-003 | soft_delete_pair | DB_CONSTRAINT | A+B | TEST-COMP-INV-003-INT | INTEGRATION | SIM | ALTA | PARCIAL | NOT_RUN | migration 0055 | AR-COMP-001 |
| INV-COMP-004 | uq_standings_comp_phase | DB_CONSTRAINT | A | TEST-COMP-INV-004-INT | INTEGRATION | SIM | ALTA | PARCIAL | NOT_RUN | schema.sql:uq_competition_standings_comp_phase_opponent | AR-COMP-001 |
| INV-COMP-005 | fk_standings_team_id | DB_CONSTRAINT | A | TEST-COMP-INV-005-INT | INTEGRATION | SIM | ALTA | PARCIAL | NOT_RUN | schema.sql:6039 | AR-COMP-001 |
| INV-COMP-006 | soft_delete_5tables | DB_CONSTRAINT | A+B | TEST-COMP-INV-006-INT | INTEGRATION | SIM | ALTA | COBERTO | NOT_RUN | AR_008+AR_009+migration 0055 | AR-COMP-001 |
| INV-COMP-007 | points_per_win_not_null | DB_CONSTRAINT | A | TEST-COMP-INV-007-INT | INTEGRATION | SIM | CRITICA | COBERTO | NOT_RUN | migration 0064 (AR_080) | AR-COMP-003 |
| INV-COMP-008 | dynamic_scoring_rules | SERVICE | C1 | TEST-COMP-INV-008-UNIT | UNIT | SIM | CRITICA | PENDENTE | NOT_RUN | — | AR-COMP-008 |
| INV-COMP-009 | uq_competition_name_per_org | BLOQUEANTE | A | TEST-COMP-INV-009-INT | INTEGRATION | SIM | CRITICA | PENDENTE | NOT_RUN | — | AR-COMP-005 |
| INV-COMP-010 | athlete_team_link | ANTI_INGESTAO | D | TEST-COMP-INV-010-INT | INTEGRATION | SIM | MEDIA | PENDENTE | NOT_RUN | — | AR-COMP-007 |
| INV-COMP-011 | uq_opponent_canonical | ANTI_INGESTAO | A | TEST-COMP-INV-011-INT | INTEGRATION | SIM | ALTA | PENDENTE | NOT_RUN | — | AR-COMP-006 |
| INV-COMP-012 | match_draft_excluded | BLOQUEANTE | C2 | TEST-COMP-INV-012-INT | INTEGRATION | SIM | CRITICA | PENDENTE | NOT_RUN | — | AR-COMP-008 |
| INV-COMP-013 | tiebreaker_rules_required | BLOQUEANTE | C1 | TEST-COMP-INV-013-UNIT | UNIT | SIM | MEDIA | PENDENTE | NOT_RUN | — | AR-COMP-009 |
| INV-COMP-014 | uq_external_ref | ANTI_INGESTAO | A | TEST-COMP-INV-014-INT | INTEGRATION | SIM | ALTA | COBERTO | NOT_RUN | migration AR_079 (partial index) | AR-COMP-002 |
| INV-COMP-015 | standings_idempotent | SERVICE | C1 | TEST-COMP-INV-015-UNIT | UNIT | SIM | CRITICA | PENDENTE | NOT_RUN | — | AR-COMP-008 |
| INV-COMP-016 | ck_match_score_valid | DB_CONSTRAINT | A | TEST-COMP-INV-016-INT | INTEGRATION | SIM | CRITICA | PENDENTE | NOT_RUN | — | AR-COMP-004 |
| INV-COMP-017 | match_counted_once | BLOQUEANTE | C2 | TEST-COMP-INV-017-INT | INTEGRATION | SIM | CRITICA | PENDENTE | NOT_RUN | — | AR-COMP-008 |
| INV-COMP-018 | ck_different_teams | DB_CONSTRAINT | A | TEST-COMP-INV-018-INT | INTEGRATION | SIM | CRITICA | PENDENTE | NOT_RUN | — | AR-COMP-004 |
| INV-COMP-019 | standings_phase_scope | BLOQUEANTE | C2 | TEST-COMP-INV-019-INT | INTEGRATION | SIM | CRITICA | PENDENTE | NOT_RUN | — | AR-COMP-008 |
| INV-COMP-020 | goals_association | NAO_BLOQUEANTE | B | TEST-COMP-INV-020-UNIT | UNIT | NAO | BAIXA | PENDENTE | NOT_RUN | — | AR-COMP-008 |
| INV-COMP-021 | minimal_state_standings | BLOQUEANTE | C2 | TEST-COMP-INV-021-INT | INTEGRATION | SIM | CRITICA | PENDENTE | NOT_RUN | — | AR-COMP-008 |
| INV-COMP-022 | standings_no_doc_dependency | NAO_BLOQUEANTE | C1 | TEST-COMP-INV-022-UNIT | UNIT | NAO | BAIXA | PENDENTE | NOT_RUN | — | AR-COMP-008 |
| INV-COMP-023 | ai_no_auto_create | ANTI_INGESTAO | B | TEST-COMP-INV-023-INT | INTEGRATION | SIM | ALTA | PENDENTE | NOT_RUN | — | AR-COMP-009 |
| INV-COMP-024 | deterministic_standings | BLOQUEANTE | C2 | TEST-COMP-INV-024-INT | INTEGRATION | SIM | CRITICA | PENDENTE | NOT_RUN | — | AR-COMP-008 |
| INV-COMP-025 | metadata_no_standings_change | NAO_BLOQUEANTE | C1 | TEST-COMP-INV-025-UNIT | UNIT | NAO | BAIXA | PENDENTE | NOT_RUN | — | AR-COMP-008 |
| INV-COMP-026 | invalid_match_excluded | BLOQUEANTE | C2 | TEST-COMP-INV-026-INT | INTEGRATION | SIM | CRITICA | PENDENTE | NOT_RUN | — | AR-COMP-008 |
| INV-COMP-027 | standings_canonical_teams | BLOQUEANTE | C2 | TEST-COMP-INV-027-INT | INTEGRATION | SIM | CRITICA | PENDENTE | NOT_RUN | — | AR-COMP-006,008 |
| INV-COMP-028 | scoring_rules_explicit | BLOQUEANTE | C2 | TEST-COMP-INV-028-INT | INTEGRATION | SIM | CRITICA | PENDENTE | NOT_RUN | — | AR-COMP-008 |
| INV-COMP-029 | ai_prioritizes_current | ANTI_INGESTAO | B | TEST-COMP-INV-029-INT | INTEGRATION | SIM | MEDIA | PENDENTE | NOT_RUN | — | AR-COMP-009 |
| INV-COMP-030 | ux_minimal_actions | NAO_BLOQUEANTE | D | TEST-COMP-INV-030-E2E | E2E | NAO | BAIXA | PENDENTE | NOT_RUN | — | AR-COMP-011 |

---

## 6. Matriz de Cobertura por Fluxos

| ID Flow | Nome | Prioridade | ID Teste | Tipo | Cenário | Cobertura | Evidência | Telas | Contratos |
|---------|------|------------|----------|------|---------|-----------|-----------|-------|----------|
| FLOW-COMP-001 | Criar Competição | ALTA | TEST-COMP-FLOW-001-E2E | E2E | Happy path | PENDENTE | — | SCREEN-001,002,003 | CONTRACT-001,002 |
| FLOW-COMP-001 | Criar — Duplicata | ALTA | TEST-COMP-FLOW-001-DUP | E2E | 409 dupla | PENDENTE | — | SCREEN-002 | CONTRACT-002 |
| FLOW-COMP-002 | Import PDF/IA | ALTA | TEST-COMP-FLOW-002-MANUAL | MANUAL_GUIADO | Upload + revisão | PENDENTE | — | SCREEN-008 | CONTRACT-009 |
| FLOW-COMP-003 | Criar Fase | ALTA | TEST-COMP-FLOW-003-E2E | E2E | Happy path | PENDENTE | — | SCREEN-003,004 | CONTRACT-004 |
| FLOW-COMP-004 | Equipe Adversária | ALTA | TEST-COMP-FLOW-004-E2E | E2E | Happy path | PENDENTE | — | SCREEN-005 | CONTRACT-005 |
| FLOW-COMP-004 | Equipe — Canonical | ALTA | TEST-COMP-FLOW-004-DUP | E2E | 409 canonical | PENDENTE | — | SCREEN-005 | CONTRACT-005 |
| FLOW-COMP-005 | Registrar Partida | ALTA | TEST-COMP-FLOW-005-E2E | E2E | Criar + placar | PENDENTE | — | SCREEN-006 | CONTRACT-006,007 |
| FLOW-COMP-005 | Partida — Mesmo Time | ALTA | TEST-COMP-FLOW-005-SAME | E2E | 422 same_team | PENDENTE | — | SCREEN-006 | CONTRACT-006 |
| FLOW-COMP-005 | Partida — Placar Neg | ALTA | TEST-COMP-FLOW-005-NEG | E2E | 422 score < 0 | PENDENTE | — | SCREEN-006 | CONTRACT-007 |
| FLOW-COMP-006 | Ver Standings | ALTA | TEST-COMP-FLOW-006-E2E | E2E | Tabela completa | PENDENTE | — | SCREEN-007 | CONTRACT-008 |
| FLOW-COMP-006 | Standings — Dinâmico | ALTA | TEST-COMP-FLOW-006-DYN | INTEGRATION | ppw=3 testado | PENDENTE | — | SCREEN-007 | CONTRACT-008 |
| FLOW-COMP-007 | Resolver Pendências | MEDIA | TEST-COMP-FLOW-007-MANUAL | MANUAL_GUIADO | Ambig. adversário | PENDENTE | — | SCREEN-008 | CONTRACT-005,009 |

---

## 7. Matriz de Cobertura por Telas

| ID Screen | Rota | Estado UI | ID Teste | Criticidade | Cobertura | Últ. Exec |
|-----------|------|-----------|----------|-------------|-----------|----------|
| SCREEN-COMP-001 | /competitions | loading | TEST-COMP-SCREEN-001-LOAD | ALTA | PENDENTE | NOT_RUN |
| SCREEN-COMP-001 | /competitions | empty | TEST-COMP-SCREEN-001-EMPTY | ALTA | PENDENTE | NOT_RUN |
| SCREEN-COMP-001 | /competitions | data | TEST-COMP-SCREEN-001-DATA | ALTA | PENDENTE | NOT_RUN |
| SCREEN-COMP-002 | /competitions/new | form valid | TEST-COMP-SCREEN-002-VALID | ALTA | PENDENTE | NOT_RUN |
| SCREEN-COMP-002 | /competitions/new | error 409 | TEST-COMP-SCREEN-002-409 | ALTA | PENDENTE | NOT_RUN |
| SCREEN-COMP-003 | /competitions/{id} | data | TEST-COMP-SCREEN-003-DATA | ALTA | PENDENTE | NOT_RUN |
| SCREEN-COMP-003 | /competitions/{id} | badge pendências | TEST-COMP-SCREEN-003-PENDING | MEDIA | PENDENTE | NOT_RUN |
| SCREEN-COMP-006 | /matches | partida draft | TEST-COMP-SCREEN-006-DRAFT | CRITICA | PENDENTE | NOT_RUN |
| SCREEN-COMP-007 | /standings | data | TEST-COMP-SCREEN-007-DATA | CRITICA | PENDENTE | NOT_RUN |
| SCREEN-COMP-007 | /standings | empty | TEST-COMP-SCREEN-007-EMPTY | ALTA | PENDENTE | NOT_RUN |
| SCREEN-COMP-007 | /standings | is_our_team | TEST-COMP-SCREEN-007-OUR | ALTA | PENDENTE | NOT_RUN |

---

## 8. Matriz de Cobertura por Contratos

| ID Contract | Prioridade | ID Teste | Tipo | Payload OK | Resposta OK | Erros | Cobertura | Últ. Exec |
|-------------|------------|----------|------|------------|-------------|-------|-----------|----------|
| CONTRACT-COMP-001 | ALTA | TEST-COMP-C001-INT | CONTRACT | SIM | SIM | 401,403 | PENDENTE | NOT_RUN |
| CONTRACT-COMP-002 | ALTA | TEST-COMP-C002-INT | CONTRACT | SIM | SIM | 409,422 | PENDENTE | NOT_RUN |
| CONTRACT-COMP-003 | ALTA | TEST-COMP-C003-INT | CONTRACT | SIM | SIM (pending_count) | 404 | PENDENTE | NOT_RUN |
| CONTRACT-COMP-004 | ALTA | TEST-COMP-C004-INT | CONTRACT | SIM | SIM | 422 | PENDENTE | NOT_RUN |
| CONTRACT-COMP-005 | ALTA | TEST-COMP-C005-INT | CONTRACT | SIM | SIM (is_pending) | 409 | PENDENTE | NOT_RUN |
| CONTRACT-COMP-006 | ALTA | TEST-COMP-C006-INT | CONTRACT | SIM | SIM (counts_for_standings) | 409,422 | PENDENTE | NOT_RUN |
| CONTRACT-COMP-007 | ALTA | TEST-COMP-C007-INT | CONTRACT | SIM | SIM (standings_recalculated) | 422 | PENDENTE | NOT_RUN |
| CONTRACT-COMP-008 | ALTA | TEST-COMP-C008-INT | CONTRACT | SIM | SIM (scoring_rules, is_our_team) | 422 | PENDENTE | NOT_RUN |
| CONTRACT-COMP-009 | ALTA | TEST-COMP-C009-MANUAL | MANUAL_GUIADO | SIM | SIM (pending_items) | 409,422 | PENDENTE | NOT_RUN |

---

## 9. Mapa AR → Cobertura → Evidência

| AR ID | AR Global | Classe | Itens SSOT | Testes Previstos | Status |
|-------|-----------|--------|------------|------------------|--------|
| AR-COMP-001 | AR_078 | A | INV-016,018 | TEST-INV-016,018 | VERIFICADO |
| AR-COMP-002 | AR_079 | A | INV-014 | TEST-INV-014 | VERIFICADO |
| AR-COMP-003 | AR_080 | A | INV-007 | TEST-INV-007 | VERIFICADO |
| AR-COMP-004 | AR_081 | A | INV-016,018 | TEST-INV-016,018-INT | PENDENTE |
| AR-COMP-005 | AR_082 | A | INV-009,014 | TEST-INV-009,014-INT | PENDENTE |
| AR-COMP-006 | AR_083 | A | INV-011 | TEST-INV-011-INT | PENDENTE |
| AR-COMP-007 | AR_084 | B | INV-010 | TEST-INV-010-INT | PENDENTE |
| AR-COMP-008 | AR_085 | C | INV-008,012,015,017,019,021,024,026,027,028 | TEST-INV-008,012,015,017,019,021,024-INT | PENDENTE |
| AR-COMP-009 | AR_086 | B | INV-013,023,029 | TEST-INV-013,023,029-INT | PENDENTE |
| AR-COMP-010 | AR_087 | E | CONTRACT-001..009 | TEST-C001..009-INT | PENDENTE |
| AR-COMP-011 | AR_088 | D | FLOW-001..007, SCREEN-001..008 | TEST-FLOW-001..007-E2E | PENDENTE |
| AR-COMP-012 | AR_089 | T | todos INV BLOQUEANTE | todos TEST-COMP-INV-*-INT | PENDENTE |

---

## 10. Critérios de PASS/FAIL FASE_0

### PASS se:
- [ ] INV-007, 009, 016, 018 = COBERTO (DB constraints com prova de violação)
- [ ] INV-008, 012, 015, 017, 019, 021, 024 = COBERTO (StandingsService)
- [ ] FLOW-001, 005, 006 = COBERTO (fluxo mínimo)
- [ ] CONTRACT-001..008 = COBERTO
- [ ] Todas invariantes CRITICA com teste de violação PASS
- [ ] Evidências referenciadas para todos os itens CRITICA

### FAIL se:
- [ ] INV CRITICA sem teste de violação
- [ ] Fluxo mínimo sem cobertura
- [ ] scoring_rules ausente no response de standings
- [ ] Partidas draft contabilizadas nos standings
- [ ] COBERTO sem evidência

---

## 11. Protocolo de Atualização

Toda mudança em:
- Invariantes → atualizar seção 5
- Flows → atualizar seção 6
- Screens → atualizar seção 7
- Contratos → atualizar seção 8
- AR backlog → atualizar seção 9

Regra: atualização obrigatória no mesmo ciclo da AR.

---

## 12. Checklist do Auditor

- [ ] Cada INV CRITICA/BLOQUEANTE tem teste de violação
- [ ] Evidência real (não narrativa) para itens COBERTO
- [ ] COBERTO não foi usado por inferência
- [ ] Fluxo mínimo de valor coberto de ponta a ponta
- [ ] Contratos ALTA com teste de integração/contrato
- [ ] ARs materializadas no mapa AR → cobertura (seção 9)
