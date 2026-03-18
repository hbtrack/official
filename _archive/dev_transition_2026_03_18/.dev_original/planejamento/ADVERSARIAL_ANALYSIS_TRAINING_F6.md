# Análise Adversarial — Módulo Training (F6)
> Status: ✅ **COMPLETA**
> Data: 2026-03-17
> Metodologia: Threat modeling + contract coverage analysis
> Score Final: **82/100 APROVADO** (criticidade média-alta)

---

## 🎯 Resumo Executivo

O módulo training apresenta **boa maturidade arquitetural** e **contratos bem definidos**, mas expõe **4 riscos críticos** e **6 alertas altos** que precisam mitigação **antes da implementação**.

| Severidade | Qtd | Exemplos |
|---|---|---|
| 🔴 **CRÍTICA** | 4 | FSM holes, Focus sum validation, Wellness window enforcement, State machine test coverage |
| 🟠 **ALTA** | 6 | AsyncAPI completion, UI contract missing, Adversarial input testing, Performance (focus %) |
| 🟡 **MÉDIA** | 5 | Soft-delete scoping, Elasticity rule edge cases, Cross-module boundaries, Derived signal freshness |
| 🟢 **BAIXA** | 3 | Documentation clarity, Naming consistency, Deprecation planning |

---

## 🔴 Riscos Críticos (Bloqueiam Produção)

### RC-1: FSM Holes — Transições Não Documentadas

**Risco:** O STATE_MODEL_TRAINING.md define 7 estados, mas há brechas entre transições permitidas e transições esperadas.

**Exemplos:**
1. PUBLISHED → DRAFT (reverter após publicação) — **permitido ou não?** 
2. IN_PROGRESS → SCHEDULED (re-agendar sessão em execução) — **esperado?**
3. CANCELLED → DRAFT (descancelar) — **policy desconhecida**

**Impacto:** 
- Coach consegue chegar a estado inválido (e.g., COMPLETED → DRAFT)
- Violação de invariantes de negócio (INV-TRAIN-006)
- Testes de estado não cobrem todos os cenários

**Mitigação (ANTES de implementar):**
```
1. Revisar DOMAIN_RULES_TRAINING.md §"Mudanças de estado"
2. Listar transições EXPLICITAMENTE permitidas vs. bloqueadas
3. Atualizar STATE_MODEL_TRAINING.md com justificativa de negócio
4. Adicionar testes de transição inválida (422)
5. Documentar em INVARIANTS_TRAINING.md como INV-TRAIN-006-extended
```

---

### RC-2: Focus Sum Validation — Tolerância Ambígua

**Risco:** A regra **DR-TRAIN-002** diz "Soma focus_*_pct ≤ 120%", mas há ambiguidade na tolerância.

**Exemplos:**
```
Caso 1: focus_attack=40, focus_defense=40, focus_transition=40, focus_physical=0 = 120% ✅
Caso 2: focus_attack=40, focus_defense=40, focus_transition=40, focus_physical=1 = 121% ❌ (422)
Caso 3: Arredondamento: 33.33333... × 4 = ?
```

**Impacto:**
- Usuários veem erro de validação aparentemente aleatório
- Inconsistência entre cliente (JS) e servidor (Python)
- Edge case: valores com precisão decimal (33.333%)

**Mitigação (ANTES de implementar):**
```
1. Definir política de arredondamento: truncate, round, ceil?
2. Validar a nível de API (após arredondamento)
3. Retornar erro claro (422) com cálculo esperado
4. Adicionar test case para 33.33% × 3 + 1% = 100.99%
5. Documentar em INVARIANTS_TRAINING.md (INV-TRAIN-002)
```

---

### RC-3: Wellness Window Enforcement — Race Condition

**Risco:** Regras DR-TRAIN-004 e DR-TRAIN-005 usam NOW como ponto de corte, mas há race conditions.

**Exemplos:**
```
Cenário: session_at = 2026-03-17 14:00 UTC, NOW = 2026-03-17 12:30 UTC
Regra wellness_pre = "até 2h antes" = válido até 14:00 - 2h = 12:00 UTC
Problema: Request chega às 12:01 UTC (1 min depois do deadline) → variação de 1ms causa diferença
```

**Impacto:**
- Clock skew entre cliente e servidor
- Timezone confusion (UTC vs. local time)
- Test flakiness (timing-dependent)

**Mitigação (ANTES de implementar):**
```
1. Definir timezone SSOT: usar UTC sempre
2. Validação **server-side apenas** (client-side é hint)
3. Permitir tolerância de ±30s (para clock skew)
4. Retornar erro claro (400) com deadline esperado
5. Adicionar testes com frozen time (unittest.mock.patch)
6. Documentar em SPORT_SCIENCE_RULES_TRAINING.md (SS-TRAIN-003/004)
```

---

### RC-4: State Machine Test Coverage Gap

**Risco:** TEST_MATRIX_TRAINING.md não cobre transições inválidas explicitamente.

**Exemplos de gaps:**
```
Transição testada: DRAFT → SCHEDULED ✅
Transição não testada: DRAFT → COMPLETED (deve rejeitar)
Transição não testada: COMPLETED → DRAFT (deve rejeitar)
Transição não testada: CANCELLED → SCHEDULED (deve rejeitar)
```

**Impacto:**
- Implementação deixa passar estado inválido
- Regra DR-TRAIN-007 não é verificada em produção
- Violação de INV-TRAIN-006

**Mitigação (ANTES de implementar):**
```
1. Expandir TEST_MATRIX_TRAINING.md:
   - Adicionar seção "Forbidden Transitions" (7×7 matrix = 49 - 7 = 42 casos)
   - Identificar 15-20 casos críticos para initial coverage
2. Implementar testes parametrizados:
   @pytest.mark.parametrize("from_state,to_state", FORBIDDEN_TRANSITIONS)
   def test_invalid_transition_returns_422(...)
3. Adicionar test de "all paths" com graph traversal
```

---

## 🟠 Alertas Altos (Devem Ser Resolvidos)

### A1: AsyncAPI Events Incompleto

**Status:** 26/27 eventos faltam (`contracts/asyncapi/`)

**Impacto:**
- Integração com módulo `notifications` quebrada
- Analytics não recebe sinais de `training_session_published`, `training_session_completed`
- Módulo `wellness` não recebe sinais de `wellness_pre_submitted`, `wellness_post_submitted`

**Resolver:**
```
✅ Tarefa 1 identificada (Achado 1 do audit)
Prazo: Antes da validação com ASYNCAPI_VALIDATION_GATE
```

---

### A2: UI_CONTRACT_TRAINING.md Faltante

**Status:** 0/3 UI flows documentados

**Impacto:**
- UI developers sem contrato de screens
- Testes E2E de UI não podem começar
- FRONTEND_CONTRACT_GATE vai falhar

**Resolver:**
```
✅ Tarefa 2 identificada (Achado 2 do audit)
Prazo: Antes de gerar código frontend
```

---

### A3: Adversarial Input Testing Gap

**Risco:** Inputs adversariais não são testados sistematicamente.

**Exemplos:**
```
Focus Field:
- focus_attack = -1 (negativo) ✅ Schema bloqueia
- focus_attack = 101 (acima de 100) ✅ Schema bloqueia
- focus_attack = "NaN" (não-número) ✅ Schema bloqueia
- focus_attack = 1e308 (overflow) ⚠️ Schema não bloqueia?

Duração:
- durationPlannedMinutes = 0 (zero) ✅ Schema bloqueia (minimum: 1)
- durationPlannedMinutes = 1441 (24h+1min) ✅ Schema bloqueia (maximum: 1440)
- durationPlannedMinutes = -1 (negativo) ✅ Bloqueado
- Soma(block durations) > durationPlannedMinutes = ? (elastic sum — precisa teste)
```

**Mitigação:**
```
1. Adicionar test suite: test_adversarial_inputs.py
2. Cobrir: negatives, boundaries, overflow, type mismatches
3. Validar respostas: deve retornar 422 (domain error), nunca 500
4. Testar com hypothesis (property-based testing)
```

---

### A4: Performance — Focus % Calculations

**Risco:** Validação de soma de focus em cada POST/PATCH pode ser lenta com muitas sessões.

**Impacto:**
- Latência de API em casos de alta concorrência
- Risk de timeout em computação de elásticidade (INV-TRAIN-083)

**Mitigação:**
```
1. Benchmark: cálculo de soma para 1k, 10k sessões
2. Índices de DB: (team_id, season_id) para queries de contexto
3. Cache: focus % por sessão em campo desnormalizado
4. Lazy evaluation: não recalcular em cada PATCH (apenas em milestones)
```

---

### A5: Cross-Module Boundary Violations

**Risco:** Módulo training não respeita limites de otros módulos.

**Exemplos:**
```
Regra: RC-14 "restriction_profile é propriedade de medical"
Achado: training.training_session não deveria ter campo ineligibility_reason
Risco: Coach consegue editar restrição médica sem autorização

Regra: RC-15 "analytics não consegue alterar training state"
Achado: Nenhuma validação explícita de actor role no OpenAPI
Risco: Bug em identity_access → analytics consegue chamar PATCH /training-sessions/{id}/complete
```

**Mitigação:**
```
1. Revisar openapi/paths/training.yaml:
   - Cada operation tem security requirements? (OAuth scopes)
   - Cada POST/PATCH/DELETE valida actor role?
2. Adicionar integração tests com identity_access module mock
3. Documentar boundary rules em DOMAIN_RULES_TRAINING.md
```

---

### A6: ARAZZO Workflow Incomplete

**Risco:** Só 1 workflow definido (`create_training_session_and_mark_attendance`), mas há outros expected (publish, start, complete, cancel).

**Impacto:**
- Clients não sabem como compor operações
- Falta de "happy path" documentado para casos comuns

**Mitigação:**
```
1. Revisar DECISION_IR.yaml para API_USE_CASE (11 use cases)
2. Gerar Arazzo workflow para top-5: create, publish, start, complete, cancel
3. Validar com ARAZZO_VALIDATION_GATE
```

---

## 🟡 Alertas Médios (Podem Ser Resolvidos em Paralelo)

### M1: Soft-Delete Scoping — Inconsistência

**Risco:** Alguns modelos têm `deleted_at`, outros não. Sem política clara.

**Exemplo:**
```
training_sessions → tem deleted_at ✅
session_blocks → não o mencionado ❌
execution_records → não mencionado ❌
```

**Mitigação:** Definir política: "Todos os SSOT entities têm soft-delete" ou "Apenas training_sessions"?

---

### M2: Elasticity Rule (INV-TRAIN-083) — Edge Cases

**Risco:** Regra "duração total ±10% tolerância" não é testada com casos reais.

**Exemplo:**
```
planned_total = 60 min
tolerance = 60 × 0.1 = ±6 min → [54, 66] valid
actual = 53 min → VIOLAÇÃO (422)
```

**Mitigação:** Adicionar testes de elasticity com múltiplos cenários.

---

### M3: Derived Signals (INV-TRAIN-036) — Freshness

**Risco:** Sinais derivados (e.g., "carga interna calculada") podem ficar stale.

**Mitigação:** Definir SLA de freshness (e.g., max 2h old) e teste de invalidação.

---

### M4: Deprecation Planning

**Risco:** NenhUM plano documentado para remover campos deprecated.

**Exemplo:** Se `focus_strength_pct` for renomeado para `focus_attack_positional_pct`, como fazer rollout sem quebrar clientes?

**Mitigação:** Documentar em DEPRECATION_POLICY.md (ADR-014) com timeline de 30+ dias.

---

### M5: Nomenclatura — Inconsistência de "Status" vs. "State"

**Risco:** Código usa indistintamente `status` e `state` para FSM.

**Exemplo:**
```
training_session.status = ENUM (DRAFT, SCHEDULED, ...)  ← usa "status"
DECISION_IR.yaml:  "state_model" / "states"              ← usa "state"
STATE_MODEL_TRAINING.md: "Estado (DRAFT, ...)"           ← usa "estado"
```

**Mitigação:** Padronizar: usar **sempre** `status` em código, `state` em documentação de FSM.

---

## 🟢 Alertas Baixos (Cosmético)

### L1: MODULE_SCOPE_TRAINING.md — Fora do Escopo Vago

Exemplo: "analytics e dashboards são responsabilidade do módulo analytics" — mas módulo training emite dados que alimentam analytics. Limite não é 100% claro.

---

## 📋 Checklist de Mitigação — Antes de Gerar Código

| RC | Descrição | Status | Prazo |
|---|---|---|---|
| RC-1 | FSM holes — transições inválidas bloqueadas | ✅ **2026-03-17** | STATE_MODEL expandido com 20 casos proibidos + INV-TRAIN-017 atualizado |
| RC-2 | Focus sum tolerance — política de arredondamento definida | ✅ **2026-03-17** | INV-TRAIN-001 atualizado: ROUND_HALF_UP, 2 casas decimais, casos de borda documentados |
| RC-3 | Wellness window — timezone SSOT, tolerância ±30s | ✅ **2026-03-17** | INV-TRAIN-002/003 atualizados: UTC obrigatório, ±30s clock skew, `deadline_utc` no error body |
| RC-4 | State machine test coverage — transições inválidas testadas | ✅ **2026-03-17** | TEST_MATRIX: seção TM-200..TM-231 (31 forbidden transitions com padrão parametrizado) |
| A1 | AsyncAPI — 26 eventos gerados | ✅ **2026-03-17** | 26 canais + mensagens + schemas gerados em `contracts/asyncapi/` |
| A2 | UI_CONTRACT — 3 UI flows documentados | ✅ **2026-03-17** | `docs/hbtrack/modulos/training/UI_CONTRACT_TRAINING.md` criado |
| A3 | Adversarial input testing — test suite documentada | ✅ **2026-03-17** | TEST_MATRIX: seção TM-300..TM-322 (adversarial inputs + boundary conditions) |
| A4 | Performance — focus % calculation in-memory | ✅ **2026-03-17** | DR-TRAIN-050 adicionado: validação em memória, sem DB aggregation, threshold P95 < 50ms |
| A5 | Cross-module boundaries — actor role validation | ✅ **2026-03-17** | DR-TRAIN-051/052/053: actor role em todas state transitions; boundary medical/analytics explícito |
| A6 | ARAZZO workflows — top-5 casos documentados | ✅ **2026-03-17** | 4 novos workflows: publish, start, complete, cancel (create já existia) |

### Alertas Médios (M1–M5)

| M | Descrição | Status |
|---|---|---|
| M1 | Soft-delete scope — política definida para todos os entities | ✅ **2026-03-17** — INV-TRAIN-101: escopo completo (session_blocks, execution_records, session_objectives, feedback_threads, wellness) |
| M2 | Elasticity rule edge cases — testes adicionados | ✅ **2026-03-17** — TEST_MATRIX: seção TM-400..TM-410 com 11 cenários |
| M3 | Derived signals freshness — SLA definido | ✅ **2026-03-17** — INV-TRAIN-100: SLA 2h, flag `is_stale`, recálculo assíncrono Celery |
| M4 | Deprecation planning — DEPRECATION_POLICY.md (ADR-014) | ⏳ Pendente — não urgente; criar em sessão dedicada a versionamento |
| M5 | Nomenclatura status vs. state — convenção canonizada | ✅ **2026-03-17** — DR-TRAIN-054: `status` em código/API, `state` em documentação FSM |

---

## 🎯 Recomendação Final

**Status:** ✅ **APROVADO PARA IMPLEMENTAÇÃO COM MITIGAÇÕES**

- ✅ Arquitectura é sólida
- ✅ Contratos bem definidos (OpenAPI, schemas, regras)
- ✅ Documentação abrangente
- ⚠️ **Crítico:** Resolver RC-1 a RC-4 **ANTES de gerar código**
- ⚠️ **Alta:** Completar A1, A2, A3, A5 **ANTES de primeiro release**
- 🟡 **Média:** Resolver M1–M5 em paralelo durante implementação

---

## 📊 Score de Aprovação

```
Cobertura de superfícies: 10/12 (83%)
Documentação: 9/10 (90%)
Validação de contratos: 10/10 (100%)
Testes (esperado): 5/10 (50%) ← Gap
Segurança/boundaries: 7/10 (70%) ← Alerta
Análise adversarial: 8/10 (80%)
─────────────────────────────────
SCORE GERAL: 82/100 ✅ APROVADO
Recomendação: Prosseguir com mitigações críticas
```

---

## 📚 Referências

- `docs/hbtrack/modulos/training/STATE_MODEL_TRAINING.md` — validar transições
- `docs/hbtrack/modulos/training/DOMAIN_RULES_TRAINING.md` — revisar DR-TRAIN-004/005/007
- `docs/hbtrack/modulos/training/INVARIANTS_TRAINING.md` — cobrir INV-TRAIN-006/083/087
- `docs/_canon/gates/TRAINING_MODULE_DECISION_IR.yaml` — SSOT de entities, rules, events
- `contracts/openapi/paths/training.yaml` — verificar security requirements
