# TEST_MATRIX_TEAMS.md

Status: DRAFT  
Versão: v0.1.0  
Tipo de Documento: Verification & Traceability Matrix (Normativo Operacional / SSOT)  
Módulo: TEAMS  
Fase: FASE_0  
Autoridade: NORMATIVO_OPERACIONAL  
Owners:
- Arquitetura: Codex (Arquiteto v2.2.0)
- Auditoria/Testes: (a definir)
- Backend/Frontend: (a definir)

Última revisão: 2026-03-03  
Próxima revisão recomendada: 2026-03-10  

Dependências:
- INVARIANTS_TEAMS.md
- TEAMS_USER_FLOWS.md
- TEAMS_SCREENS_SPEC.md
- TEAMS_FRONT_BACK_CONTRACT.md
- AR_BACKLOG_TEAMS.md

---

## REGRA SSOT (obrigatória)

**DB/schema.sql > services/domain rules > OpenAPI > frontend > PRD.**

---

## 1) Objetivo (Normativo)

Ser o SSOT do DONE do módulo TEAMS: rastreabilidade entre INV/FLOW/SCREEN/CONTRACT ↔ AR ↔ TEST ↔ EVIDÊNCIA.

---

## 2) Regras normativas de verificação

1. Toda `INV-TEAMS-*` `BLOQUEANTE_VALIDACAO` DEVE ter teste com **tentativa de violação** quando aplicável.
2. Todo `CONTRACT-TEAMS-*` P0 DEVE ter teste `CONTRACT` e evidência de execução PASS em `_reports/*`.
3. Todo `FLOW-TEAMS-*` P0 DEVE ter `E2E` ou `MANUAL_GUIADO` com evidência em `_reports/*`.
4. `COBERTO` sem evidência é proibido.

---

## 3) Convenções

### 3.1 Tipos de teste
- UNIT
- INTEGRATION
- CONTRACT
- E2E
- MANUAL_GUIADO

### 3.2 Status de cobertura
- COBERTO
- PARCIAL
- PENDENTE
- BLOQUEADO
- NAO_APLICAVEL

### 3.3 Resultado da última execução
- PASS
- FAIL
- NOT_RUN

---

## 5) Matriz de Cobertura — Invariantes

| ID Item | Severidade | Camada | ID Teste | Tipo | Objetivo | Violação | Criticidade | Status | Últ. Exec | Evidência `_reports/*` | AR |
|---|---|---|---|---|---|---|---|---|---|---|---|
| INV-TEAMS-001 | BLOQUEANTE_VALIDACAO | db | TEST-TEAMS-INV-001 | INTEGRATION | Inserir gender inválido | SIM | CRITICA | PENDENTE | NOT_RUN | — | AR-TEAMS-005 |
| INV-TEAMS-003 | BLOQUEANTE_VALIDACAO | db | TEST-TEAMS-INV-003 | INTEGRATION | Soft delete exige reason | SIM | CRITICA | PENDENTE | NOT_RUN | — | AR-TEAMS-003 |
| INV-TEAMS-004 | BLOQUEANTE_VALIDACAO | db+api | TEST-TEAMS-INV-004 | CONTRACT | PATCH settings fora de 1..3 | SIM | CRITICA | PENDENTE | NOT_RUN | — | AR-TEAMS-007 |
| INV-TEAMS-007 | BLOQUEANTE_VALIDACAO | db | TEST-TEAMS-INV-007 | INTEGRATION | Duplicar convite ativo/pendente | SIM | ALTA | PENDENTE | NOT_RUN | — | AR-TEAMS-002 |
| INV-TEAMS-009 | BLOQUEANTE_VALIDACAO | db | TEST-TEAMS-INV-009 | INTEGRATION | Duplicar registro ativo athlete+team | SIM | ALTA | PENDENTE | NOT_RUN | — | AR-TEAMS-007 |
| INV-TEAMS-020 | BLOQUEANTE_VALIDACAO | db+service | TEST-TEAMS-INV-020 | INTEGRATION | Overlap por temporada (RDB10) | SIM | CRITICA | BLOQUEADO | NOT_RUN | — | DEC-TEAMS-002 |

---

## 6) Matriz de Cobertura — Flows

| ID Flow | Prioridade | ID Teste | Tipo | Cenário | Status | Últ. Exec | Evidência `_reports/*` | AR |
|---|---|---|---|---|---|---|---|---|
| FLOW-TEAMS-001 | P0 | TEST-TEAMS-FLOW-001 | E2E | Dashboard carrega + paginação | PENDENTE | NOT_RUN | — | AR-TEAMS-008 |
| FLOW-TEAMS-002 | P0 | TEST-TEAMS-FLOW-002 | E2E | Criar equipe via UI | PENDENTE | NOT_RUN | — | AR-TEAMS-008 |
| FLOW-TEAMS-004 | P0 | TEST-TEAMS-FLOW-004 | E2E | Atualizar threshold Step 15 | PENDENTE | NOT_RUN | — | AR-TEAMS-008 |
| FLOW-TEAMS-007 | P0 | TEST-TEAMS-FLOW-007 | E2E | Convidar + listar + reenviar + cancelar | BLOQUEADO | NOT_RUN | — | AR-TEAMS-002 |

---

## 7) Matriz de Cobertura — Screens

| ID Screen | Rota | ID Teste | Tipo | Cenário | Status | Últ. Exec | Evidência `_reports/*` |
|---|---|---|---|---|---|---|---|
| SCREEN-TEAMS-001 | /teams | TEST-TEAMS-SCREEN-001 | E2E | loading/error/empty/data | PENDENTE | NOT_RUN | — |
| SCREEN-TEAMS-004 | /teams/{id}/members | TEST-TEAMS-SCREEN-004 | E2E | staff + atletas estados | PENDENTE | NOT_RUN | — |
| SCREEN-TEAMS-005 | /teams/{id}/settings | TEST-TEAMS-SCREEN-005 | E2E | editar nome + threshold | PENDENTE | NOT_RUN | — |

---

## 8) Matriz de Cobertura — Contratos Front-Back

| ID Contract | Prioridade | ID Teste | Tipo | Payload mínimo | Resposta mínima | Status | Últ. Exec | Evidência `_reports/*` | AR |
|---|---|---|---|---|---|---|---|---|---|
| CONTRACT-TEAMS-001 | P0 | TEST-TEAMS-CONTRACT-001 | CONTRACT | query page/limit | {items,total} | PENDENTE | NOT_RUN | — | AR-TEAMS-001 |
| CONTRACT-TEAMS-002 | P0 | TEST-TEAMS-CONTRACT-002 | CONTRACT | TeamCreate mínimo | TeamBase | PENDENTE | NOT_RUN | — | AR-TEAMS-007 |
| CONTRACT-TEAMS-006 | P0 | TEST-TEAMS-CONTRACT-006 | CONTRACT | {alert_threshold_multiplier} | TeamBase | PENDENTE | NOT_RUN | — | AR-TEAMS-007 |
| CONTRACT-TEAMS-013 | P0 | TEST-TEAMS-CONTRACT-013 | CONTRACT | query active_only/page/limit | TeamRegistrationPaginatedResponse | PENDENTE | NOT_RUN | — | AR-TEAMS-007 |

---

## 9) Mapa AR → Cobertura → Evidência

| AR ID | Classe | Itens SSOT alvo | Testes previstos | Evidência esperada | Status |
|---|---|---|---|---|---|
| AR-TEAMS-001 | E | CONTRACT-TEAMS-001 | TEST-TEAMS-CONTRACT-001 | `_reports/testador/AR_TEAMS_001/*` | PENDENTE |
| AR-TEAMS-002 | E | FLOW-TEAMS-007, CONTRACT-TEAMS-020..023 | TEST-TEAMS-FLOW-007 | `_reports/testador/AR_TEAMS_002/*` | PENDENTE |
| AR-TEAMS-007 | T | CONTRACT P0 (TEAMS) | TEST-TEAMS-CONTRACT-* | `_reports/testador/AR_TEAMS_007/*` | PENDENTE |
| AR-TEAMS-008 | T | FLOW/SCR P0 | TEST-TEAMS-FLOW-*/SCREEN-* | `_reports/testador/AR_TEAMS_008/*` | PENDENTE |

---

## 10) §10 — Critérios de PASS/FAIL do Módulo TEAMS (DONE SSOT)

### PASS (módulo TEAMS) se:

A) Invariantes

- [ ] Todos os `INV-TEAMS-*` `BLOQUEANTE_VALIDACAO` = COBERTO com teste de violação (quando aplicável) + evidência PASS em `_reports/*`

B) Contratos

- [ ] Todos os contratos `CONTRACT-TEAMS-*` prioridade P0 = COBERTO via testes `CONTRACT` + evidência PASS em `_reports/*`

C) Flows

- [ ] Todos os flows `FLOW-TEAMS-*` prioridade P0 = COBERTO via `E2E` ou `MANUAL_GUIADO` + evidência PASS em `_reports/*`

D) Screens (se aplicável)

- [ ] Todas as screens `SCREEN-TEAMS-*` prioridade P0 = COBERTO via smoke `MANUAL_GUIADO` ou `E2E` + evidência PASS em `_reports/*`

### FAIL (módulo TEAMS) se:

- [ ] Alguma invariante `BLOQUEANTE_VALIDACAO` sem teste de violação (não justificável)
- [ ] Algum contrato P0 sem teste `CONTRACT` + evidência PASS
- [ ] Algum flow P0 sem evidência de execução
- [ ] Qualquer item marcado COBERTO sem evidência `_reports/*`

---

## 11) Evidências AS-IS (existência de testes no repo)

> Esta seção prova existência de testes (não execução).

- BE: `Hb Track - Backend/tests/api/test_teams.py`
  - Âncora: `class TestTeamsAPI`
  - Trecho:
    ```py
    class TestTeamsAPI:
        def test_list_teams_without_auth_returns_401(self):
    ```
- FE E2E: `Hb Track - Frontend/tests/e2e/teams/teams.invites.spec.ts`
  - Âncora: `CONTRATO`
  - Trecho:
    ```ts
    // POST /teams/{teamId}/invites → Criar convite
    ```
