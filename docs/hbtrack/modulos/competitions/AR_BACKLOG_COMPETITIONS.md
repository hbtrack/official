# AR_BACKLOG_COMPETITIONS.md

Status: DRAFT
Versão: v0.1.0
Tipo de Documento: AR Materialization Backlog (Normativo Operacional / SSOT)
Módulo: COMPETITIONS
Fase: FASE_0 / FASE_1
Autoridade: NORMATIVO_OPERACIONAL
Owners:
- Arquitetura (Arquiteto): Agente Arquiteto
- Execução (Executor): Agente Executor
- Auditoria/Testes: Agente Testador

Última revisão: 2026-02-25
Próxima revisão recomendada: 2026-03-15

Dependências:
- INVARIANTS_COMPETITIONS.md
- COMPETITIONS_USER_FLOWS.md
- COMPETITIONS_SCREENS_SPEC.md
- COMPETITIONS_FRONT_BACK_CONTRACT.md
- TEST_MATRIX_COMPETITIONS.md

Nota: AR-COMP-001/002/003 mapeiam para ARs globais já executadas (AR_078/079/080).
ARs futuras AR-COMP-004+ mapeiam para AR_081+.

---

## 1. Objetivo (Normativo)

Decompor a implementação do módulo Competitions em ARs pequenas, rastreaváveis, testáveis e auditáveis, com ordem de execução, critérios binários de aceite e estratégia de validação (incluindo tentativas de violação de invariantes bloqueantes).

---

## 2. Escopo

### 2.1 Dentro do escopo
- Materialização dos itens do MCP da FASE_0 e FASE_1
- Correções de divergência contrato vs código do módulo
- Testes e evidências mínimas para fechamento das fases

### 2.2 Fora do escopo
- Refatorações amplas sem vínculo com itens do MCP
- Features fora do PRD/MCP
- Mudanças em outros módulos (salvo dependência explícita)
- Scout (módulo separado)

### 2.3 Regras obrigatórias de fatiamento
1. Preferir 1 AR = 1 classe (A/B/C/D/E/T)
2. Cada AR DEVE referenciar IDs SSOT alvo (INV/FLOW/SCREEN/CONTRACT)
3. Cada AR DEVE ter AC binário (PASS/FAIL observável)
4. Cada AR DEVE ter estratégia de validação com tentativa de violação para invariantes bloqueantes
5. AR híbrida A+B+D é proibida salvo justificativa aprovada

---

## 3. Classes de AR

- **A** — Banco/Persistência (migrations, constraints, models)
- **B** — Regras de Domínio/Services
- **C** — Cálculo/Derivados/Determinismo
- **D** — Frontend/UX
- **E** — Contrato Front-Back / integração
- **T** — Testes/Gates/Paridade

---

## 4. Tabela Resumo do Backlog de ARs

| AR ID | AR Global | Classe | Prioridade | Objetivo | Alvos SSOT | Dependências | Status |
|-------|-----------|--------|------------|----------|------------|--------------|--------|
| AR-COMP-001 | AR_078 | A | ALTA | CHECK constraints em competition_matches | INV-016, INV-018 | — | VERIFICADO |
| AR-COMP-002 | AR_079 | A | ALTA | UNIQUE partial indexes (match_roster, external_ref) | INV-014 | AR-COMP-001 | VERIFICADO |
| AR-COMP-003 | AR_080 | A | ALTA | points_per_win NOT NULL (migration 0064) | INV-007 | AR-COMP-002 | VERIFICADO |
| AR-COMP-004 | AR_081 | A | CRITICA | CHECK constraints FASE_0: score >=0, different teams | INV-016, INV-018 | AR-COMP-003 | PENDENTE |
| AR-COMP-005 | AR_082 | A | ALTA | UNIQUE: org+name+season, external_ref por competition | INV-009, INV-014 | AR-COMP-004 | PENDENTE |
| AR-COMP-006 | AR_083 | A | ALTA | Canonical opponent: tabela opponent_team_aliases + UNIQUE | INV-011 | AR-COMP-005 | PENDENTE |
| AR-COMP-007 | AR_084 | B | ALTA | Service: match_roster athlete-team link validation | INV-010 | AR-COMP-006 | PENDENTE |
| AR-COMP-008 | AR_085 | C | CRITICA | StandingsService: dynamic scoring, filtros, determinismo | INV-008,012,015,017,019,021,024,026,027,028 | AR-COMP-004,005 | PENDENTE |
| AR-COMP-009 | AR_086 | B | MEDIA | Anti-ingestão: tiebreaker rules, AI entity resolution | INV-013, INV-023, INV-029 | AR-COMP-008 | PENDENTE |
| AR-COMP-010 | AR_087 | E | ALTA | Formalizar contratos front-back (flags, error codes) | CONTRACT-001..009 | AR-COMP-008 | PENDENTE |
| AR-COMP-011 | AR_088 | D | MEDIA | Frontend: telas SCREEN-001..008 (fluxo mínimo) | FLOW-001..007, SCREEN-001..008 | AR-COMP-010 | PENDENTE |
| AR-COMP-012 | AR_089 | T | MEDIA | Tests + paridade: coverage invariantes bloqueantes | todos INV BLOQUEANTE | AR-COMP-008,011 | PENDENTE |

---

## 5. ARs Detalhadas (PENDENTES críticas)

---

### AR-COMP-004 — CHECK Constraints FASE_0 (AR_081)

**Status:** PENDENTE
**Classe:** A
**Prioridade:** CRITICA
**Fase:** FASE_0
**AR Global:** AR_081
**Objetivo:** Adicionar CHECK constraints em competition_matches: `home_score >= 0 AND away_score >= 0` e `home_team_id != away_team_id`.

#### Alvos SSOT
- INV-COMP-016: `ck_match_score_valid`
- INV-COMP-018: `ck_match_different_teams`

#### Dependências
- AR-COMP-003 VERIFICADO (migration 0064 aplicada)

#### Escopo de leitura
- `Hb Track - Backend/docs/ssot/schema.sql`
- `INVARIANTS_COMPETITIONS.md` (INV-016, INV-018)

#### Escopo de escrita
- `Hb Track - Backend/db/alembic/versions/0065_ar081_check_constraints_fase0.py` (nova)
- Model de CompetitionMatch
- `Hb Track - Backend/docs/ssot/schema.sql` (atualizar)

#### Fora do escopo
- NÃO alterar outras tabelas
- NÃO criar service layer
- NÃO alterar regras de standings

#### Acceptance Criteria

##### AC-001
**PASS:** `INSERT competition_matches home_score=-1` → `ERROR: ck_match_score_valid`
**FAIL:** INSERT com score negativo persiste

##### AC-002
**PASS:** `INSERT competition_matches home_team_id=X, away_team_id=X` → `ERROR: ck_match_different_teams`
**FAIL:** INSERT com mesmo time persiste

##### AC-003
**PASS:** INSERT score=0 e times distintos → persiste normalmente
**FAIL:** Partidas válidas rejeitadas

#### Estratégia de validação

```bash
cd "Hb Track - Backend" && alembic upgrade head
python temp/check_ar081_precheck.py --test-invalid-score
python temp/check_ar081_precheck.py --test-same-team
python temp/check_ar081_precheck.py --test-valid
```

---

### AR-COMP-005 — UNIQUE Constraints FASE_1 (AR_082)

**Status:** PENDENTE
**Classe:** A
**Prioridade:** ALTA
**Fase:** FASE_1
**AR Global:** AR_082
**Objetivo:** UNIQUE `(organization_id, name, season)` em competitions e `(competition_id, external_reference)` em competition_matches.

#### Alvos SSOT
- INV-COMP-009: `uq_competitions_org_name_season`
- INV-COMP-014: `uq_match_external_ref`

#### Acceptance Criteria

##### AC-001
**PASS:** Inserir 2 competições com mesmo nome+temporada na mesma org → `UniqueViolationError`
**FAIL:** Duplicata persiste

##### AC-002
**PASS:** Inserir 2 partidas com mesmo external_ref na mesma competição → `UniqueViolationError`
**FAIL:** Duplicata persiste

---

### AR-COMP-008 — StandingsService Completo (AR_085)

**Status:** PENDENTE
**Classe:** C
**Prioridade:** CRITICA
**Fase:** FASE_0
**AR Global:** AR_085
**Objetivo:** Implementar CompetitionStandingsService com pontuação dinâmica (sem hardcode), filtros corretos (draft excluído), idempotência, escopo por fase, determinismo.

#### Alvos SSOT
- INV-COMP-008, 012, 015, 017, 019, 021, 024, 026, 027, 028

#### Dependências
- AR-COMP-004 (CHECK constraints), AR-COMP-005 (UNIQUE)

#### Acceptance Criteria

##### AC-001
**PASS:** Competição com ppw=3 → service usa 3/vitória (não hardcoded 2)
**FAIL:** Service usa valor hardcoded

##### AC-002
**PASS:** Partida status=draft → não aparece nos standings
**FAIL:** Partida draft altera pontuação

##### AC-003
**PASS:** Chamar recalculate_standings N vezes → mesmo resultado
**FAIL:** Pontos acumulam a cada chamada

##### AC-004
**PASS:** Standings com phase_id=X só inclui partidas da fase X
**FAIL:** Partidas de outras fases contaminam resultado

#### Estratégia de validação

```bash
cd "Hb Track - Backend"
pytest tests/ -k "standings" -v
```

---

## 6. ARs Verificadas (resumo)

### AR-COMP-001 — CHECK Constraints (AR_078) — VERIFICADO
- Constraints: `ck_match_score_valid`, `ck_match_different_teams`

### AR-COMP-002 — UNIQUE Partial Indexes (AR_079) — VERIFICADO
- Commit: `7dadb4c — feat: seal AR_079`

### AR-COMP-003 — points_per_win NOT NULL (AR_080) — VERIFICADO
- Commit: `d672b8c — feat(AR_080): materialize INV-COMP-007`

---

## 7. Mapa de Dependências entre ARs

```
AR-COMP-001 (VERIFICADO)
    AR-COMP-002 (VERIFICADO)
        AR-COMP-003 (VERIFICADO)
            AR-COMP-004 (PENDENTE — CRITICA)
                AR-COMP-005 (PENDENTE)
                    AR-COMP-006 (PENDENTE)
                        AR-COMP-007 (PENDENTE)
                    AR-COMP-008 (PENDENTE — CRITICA)
                        AR-COMP-009 (PENDENTE)
                        AR-COMP-010 (PENDENTE)
                            AR-COMP-011 (PENDENTE)
                                AR-COMP-012 (PENDENTE)
```

---

## 8. Critérios de PASS/FAIL FASE_0

### PASS se:
- [ ] AR-COMP-004, AR-COMP-005, AR-COMP-008, AR-COMP-010 = VERIFICADO
- [ ] INV-007,009,012,014,015,016,017,018,019,021,024 com enforcement comprovado
- [ ] Fluxo mínimo: criar competição → partida → standings funcional
- [ ] TEST_MATRIX_COMPETITIONS.md atualizada

### FAIL se:
- [ ] Pontuação hardcoded no StandingsService
- [ ] Partidas draft contabilizadas nos standings
- [ ] Score negativo persiste no DB
- [ ] Duplicata de competição (org+nome+temporada) persiste
- [ ] AR VERIFICADO sem evidência

---

## 9. DoD da FASE_0

**PASS se (todos):**
- [ ] MCP mínimo aprovado (6 documentos)
- [ ] INV-007, 009, 016, 018 com DB constraint ativa
- [ ] StandingsService com dynamic scoring, filtro draft, idempotência
- [ ] Contratos front-back formalizados (AR-COMP-010 VERIFICADO)
- [ ] Fluxo mínimo end-to-end funcional
- [ ] Evidências de violação de invariantes bloqueantes coletadas
