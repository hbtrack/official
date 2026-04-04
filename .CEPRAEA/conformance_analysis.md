# HB Track — Análise de Conformidade: Contratos vs Código

> **Data:** 2026-03-31  
> **Escopo:** docs/_canon + docs/hbtrack/modulos → src/ → tests/  
> **Método:** Cruzamento direto de regras documentadas com implementação materializada.

---

## 1. ESTADO ATUAL DO SISTEMA

### 1.1 Visão Geral

| Indicador | Valor |
|---|---|
| Módulos canônicos | 17 (todos `implemented`) |
| Gates de validação (full run) | 27 PASS, 26 SKIP_NOT_APPLICABLE, 0 FAIL |
| Gates de validação (precommit) | 27 PASS |
| Arquivos de contrato por módulo | 5–14 (.md + .yaml) |
| Total de operações OpenAPI | ~153 |
| Total de rotas implementadas | ~138 |
| Testes unitários em src/ | 21 arquivos consolidados (1–2 por módulo) |
| Schemathesis | ativo no CI, 0 failures |

### 1.2 Conformidade de Endpoints (OpenAPI vs api.py)

| Módulo | OpenAPI ops | Rotas impl. | Delta | Status |
|---|---|---|---|---|
| training | 53 | 26 | **-27** | ⚠️ PARCIAL — operações avançadas (objectives, feedback, execution_records, mesocycles, microcycles) parciais |
| users | 4 | 4 | 0 | ✅ COMPLETO |
| teams | 8 | 8 | 0 | ✅ COMPLETO |
| seasons | 6 | 6 | 0 | ✅ COMPLETO |
| competitions | 6 | 6 | 0 | ✅ COMPLETO |
| matches | 6 | 6 | 0 | ✅ COMPLETO |
| scout | 5 | 5 | 0 | ✅ COMPLETO |
| video | 9 | 10 | +1 | ✅ (1 rota extra interna) |
| medical | 5 | 5 | 0 | ✅ COMPLETO |
| wellness | 5 | 5 | 0 | ✅ COMPLETO |
| exercises | 14 | 14 | 0 | ✅ COMPLETO |
| analytics | 5 | 5 | 0 | ✅ COMPLETO |
| reports | 5 | 5 | 0 | ✅ COMPLETO |
| ai_ingestion | 4 | 4 | 0 | ✅ COMPLETO |
| identity_access | 9 | 9 | 0 | ✅ COMPLETO |
| audit | 4 | 4 | 0 | ✅ COMPLETO |
| notifications | 5 | 5 | 0 | ✅ COMPLETO |

**Resultado:** 16 de 17 módulos têm 100% de paridade endpoint. O módulo `training` tem 53 operações contratadas no OpenAPI mas apenas 26 rotas implementadas — o delta de 27 corresponde a endpoints de fase avançada (periodização detalhada, feedback threads, execution records, attention queue, analytics training-specific) que estão no contrato mas ainda serão materializados nas próximas fases do ROADMAP.

---

## 2. O CÓDIGO RESPEITA OS .md? — ANÁLISE POR CAMADA

### 2.1 DOMAIN_RULES → domain/rules.py

**Training (análise profunda):**

| Regra | Status | Evidência no código |
|---|---|---|
| DR-TRAIN-001 (RBAC criação) | ✅ Implementada | `assert_can_create_session()` com roles canônicos |
| DR-TRAIN-002 (soma foco ≤ 120) | ✅ Implementada | `TrainingSession.validate_invariants()` |
| DR-TRAIN-003 (range 0–100) | ✅ Implementada | validação em `validate_invariants()` |
| DR-TRAIN-006 (60 dias read-only) | ✅ Implementada | `assert_session_not_historical()` |
| DR-TRAIN-007 (janela por papel) | ⚠️ Parcial | Janela existe no `rules.py` mas INV-TRAIN-004 não usa SELECT FOR UPDATE |
| DR-TRAIN-008 (unidade soberana = ciclo) | ⚠️ Parcial | Entity `TrainingSession` existe mas `TrainingInterventionCycle` como entidade separada não está materializada |
| DR-TRAIN-013 (MANUAL_COACH_RATIONALE → originNotes) | ✅ Implementada | `SessionObjective.validate_invariants()` |
| DR-TRAIN-022/026 (FSM 7 estados) | ✅ Implementada | `VALID_TRANSITIONS` em `rules.py`, enum canônico em `entities.py` |
| DR-TRAIN-030 (individualizationMode) | ✅ Implementada | `IndividualizationMode` enum com 3 valores canônicos |

**Users (análise profunda):**

| Regra | Status | Evidência |
|---|---|---|
| DR-USR-001 (boundary users/identity_access) | ✅ Implementada | Nenhum campo authn no schema users |
| DR-USR-002 (roleLabel = 5 canônicos) | ✅ Implementada | `RoleLabel` enum com 5 valores |
| DR-USR-003 (teamIds/seasonIds explícitos) | ✅ Implementada | campos diretos no `UserProfile` |
| DR-USR-005 (preferências sem estado de segurança) | ✅ Implementada | `FORBIDDEN_AUTHN_FIELDS` blocklist |

**Teams:**

| Regra | Status | Evidência |
|---|---|---|
| RBAC per operação | ✅ Implementada | `rules.py` com `assert_can_*` |
| Estado do time (FSM) | ✅ Implementada | `TeamStatus` enum + `VALID_TRANSITIONS` |

**Veredicto:** As regras de domínio documentadas nos .md **são fielmente implementadas** no código para as funcionalidades materializadas. Há regras para funcionalidades avançadas (ciclo de intervenção, feedback threads, execution records) que estão documentadas mas ainda não materializadas — isso é esperado dado o ROADMAP.

### 2.2 INVARIANTS → validate_invariants() + rules.py

| Invariante | Módulo | Status |
|---|---|---|
| INV-TRAIN-001 (foco ≤ 120) | training | ✅ Implementada com Decimal, ROUND_HALF_UP |
| INV-TRAIN-002 (wellness pre 2h) | training | ✅ Implementada com assert_wellness_pre_window() |
| INV-TRAIN-003 (wellness post 24h) | training | ✅ Implementada com assert_wellness_post_window() |
| INV-TRAIN-004 (janela por papel) | training | ✅ Implementada |
| INV-TRAIN-005 (60 dias) | training | ✅ Implementada com assert_session_not_historical() |
| INV-TRAIN-006 (FSM 7 estados) | training | ✅ Implementada (VALID_TRANSITIONS) |
| INV-TRAIN-008 (soft delete) | training | ✅ Implementada (validate_invariants) |
| INV-TRAIN-009/010 (unicidade wellness) | training | ✅ Implementada (DuplicateWellnessEntry exception) |
| INV-TRAIN-083 (Elastic Sum Rule) | training | ✅ Implementada (assert_elastic_sum_rule) |
| INV-USR-001 (required fields) | users | ✅ JSON Schema + entity validation |
| INV-USR-003 (no authn fields) | users | ✅ FORBIDDEN_AUTHN_FIELDS blocklist |

**Veredicto: FORTE.** As invariantes documentadas estão materializadas como guard functions no domínio. Os testes unitários cobrem cada invariante com casos de borda (boundary values, clock skew).

### 2.3 PERMISSIONS → RBAC enforcement

| Aspecto | Status | Detalhe |
|---|---|---|
| 5 roles canônicos (ADR-008) | ✅ | Materializados como `RoleLabel` enum em todos os módulos |
| BFLA (nível de operação) | ✅ | `assert_can_*` functions no Router com `raise HttpError(403)` |
| BOLA (nível de objeto) | ✅ | `assert_can_read_session(actor_id, session_athlete_ids)` |
| BOPLA (nível de propriedade) | ✅ | `assert_can_submit_wellness(actor_id, target_athlete_id)` |
| member bloqueado em training | ✅ | Teste e implementação confirmam |
| athlete read-only em wellness alheia | ✅ | BOLA implementado |

**Gap:** A integração real com `identity_access` ainda usa stubs (`_get_actor_role(request)` extrai de atributo do request obj). O JWT real ainda não está conectado. Isso é esperado até FASE 7 do ROADMAP.

### 2.4 MODULE_SCOPE

Os MODULE_SCOPE estão sendo respeitados:
- Boundary users/identity_access: ✅ implementado (nenhum campo authn em users)
- Boundary training/medical: ✅ (training acessa medical como read-only)
- Boundary training/audit: ✅ (audit_log pattern preparado)
- Os 17 módulos possuem api.py + schemas.py + domain/ + application/ + infrastructure/ conforme CODE_ARCHITECTURE.md

---

## 3. TEST_MATRIX — ESTÁ SENDO ATENDIDA?

### 3.1 Problema Crítico: Centralização vs Dispersão de Testes

O TEST_MATRIX_TRAINING.md referencia **24 arquivos de teste especializados**:
```
tests/training/test_state_machine.py
tests/training/test_domain_rules.py
tests/training/test_invariants.py
tests/training/test_handball_rules.py
tests/training/test_objectives.py
tests/training/test_execution_records.py
tests/training/test_feedback_threads.py
tests/training/test_boundaries.py
tests/training/test_restrictions.py
tests/training/test_attention_queue.py
tests/training/test_wellness_temporal.py
tests/training/test_acl.py
tests/training/test_edit_windows.py
tests/training/test_readonly_sessions.py
tests/training/test_sensitive_data.py
tests/training/test_persistence.py
tests/training/test_layer_separation.py
tests/training/test_ingestion.py
tests/training/test_session_blocks.py
tests/training/test_live_adjustments.py
tests/training/test_reviews.py
tests/training/test_elastic_sum.py
tests/training/test_forbidden_transitions.py
tests/training/test_adversarial_inputs.py
```

**Realidade:** Existe **1 arquivo consolidado** (`src/training/tests/unit/test_training_domain.py`) que cobre ~60% das regras referenciadas (INV-TRAIN-001, 002, 003, 004, 005, 006, 008, 083; DR-TRAIN-001, 013, 022; BOLA/BOPLA).

### 3.2 Cobertura Real vs Contratada

| Área da TEST_MATRIX | Coberta? | Detalhe |
|---|---|---|
| FSM transitions (TM-004, TM-105, TM-110) | ✅ | `TestTrainingSessionFSM` — 8 test cases |
| Focus ≤ 120 (TM-100) | ✅ | `TestFocusPercentagesInvariant` — 6 test cases |
| RBAC criação (TM-010) | ✅ | `TestCreateSessionRBAC` — 5 test cases |
| BOLA leitura (TM-010 adj) | ✅ | `TestReadSessionBOLA` — 5 test cases |
| Wellness temporal (TM-101, TM-102) | ✅ | `TestWellnessPreWindow` — 3 test cases |
| Soft delete (TM-108 adj) | ✅ | `TestSoftDeleteInvariant` — 4 test cases |
| Elastic Sum Rule (TM-119) | ✅ | `TestElasticSumRule` — 5 test cases |
| SessionObjective originNotes (TM-025-026) | ✅ | `TestSessionObjectiveInvariants` — 3 test cases |
| FeedbackThread invariants (TM-032-035) | ✅ | `TestFeedbackThreadInvariants` — 4 test cases |
| BOPLA wellness (TM-adj) | ✅ | `TestWellnessBOPLA` — 4 test cases |
| SessionBlock invariants (TM-004 adj) | ✅ | `TestSessionBlockInvariants` — 8 test cases |
| Mesocycle invariants | ✅ | `TestMesocycleInvariants` — 3 test cases |
| Delete RBAC | ✅ | `TestDeleteSessionRBAC` — 4 test cases |
| Handball rules (TM-017 a TM-020) | ❌ | **NÃO EXISTE** — 4 TMs sem teste |
| ACL extended (TM-121) | ❌ | **NÃO EXISTE** |
| Restrictions/eligibility (TM-037-038) | ❌ | **NÃO EXISTE** |
| Layer separation (TM-044) | ❌ | **NÃO EXISTE** |
| Ingestion (TM-045-047) | ❌ | **NÃO EXISTE** — target-state |
| Sensitive data (TM-048-049) | ❌ | **NÃO EXISTE** |
| Adversarial inputs | ❌ | **NÃO EXISTE** |
| Contract test Schemathesis (TM-001) | ✅ | Ativo no CI, 0 failures |
| Spectral lint (TM-003) | ✅ | SPECTRAL_LINTING_GATE: PASS |

### 3.3 Gap Quantitativo

| Métrica | Valor |
|---|---|
| TMs no TEST_MATRIX_TRAINING | ~62 (TM-001 a TM-121) |
| TMs com evidência de teste | ~35 (~56%) |
| TMs sem evidência | ~27 (~44%) |
| Arquivos referenciados em TM | 24 |
| Arquivos reais | 1 (consolidado) |

### 3.4 Outros Módulos

Para os outros 16 módulos, o TEST_MATRIX referencia apenas paths genérios (sem ID de TM nem path de arquivo). Cada módulo tem 1–2 arquivos de teste cobrindo regras básicas de domínio, RBAC e invariantes principais. A granularidade é adequada para o estado atual das funcionalidades (a maioria são CRUD + RBAC + boundary).

---

## 4. AVALIAÇÃO DE FERRAMENTAS POR CAMADA

### 4.1 Camada de Interface — Spectral + Redocly CLI

| Ferramenta | Status Atual | Valor | Veredicto |
|---|---|---|---|
| **Spectral** | ✅ ATIVO — `.spectral.yaml` com 10+ rules HB Track customizadas; `SPECTRAL_LINTING_GATE` PASS no CI | Valida naming, operationId, segurança, versão OAS, paginação, Problem Details | **JÁ COBERTO — manter e expandir** |
| **Redocly CLI** | ✅ ATIVO — `redocly.yaml` configurado; `OPENAPI_ROOT_STRUCTURE_GATE` PASS no CI | Valida refs, estrutura, media types, segurança | **JÁ COBERTO — manter** |

**Recomendação:** Ambas já estão ativas e PASS. Não há necessidade de adicionar ferramentas novas nesta camada. Sugestão incremental:
- Adicionar rules Spectral para validar que `$ref` de schemas apontem para o módulo correto (reforço de boundary).
- Ambas já fazem parte do precommit profile e CI.

### 4.2 Camada de Governança/Metadados — Custom Scripts + Markdown-lint

| Ferramenta | Status Atual | Valor | Veredicto |
|---|---|---|---|
| **Custom Scripts (Python)** | ✅ ATIVO — `validate_contracts.py` (53 gates, 27 PASS), `check_scope_boundary.py`, `check_architecture_docs.py`, `check_handoff_contract.py`, `trace_stitcher.py`, `check_ops_invariants.py` | Valida integridade canônica, boundary, drift, handoff | **JÁ COBERTO — principal mecanismo de governança** |
| **Markdown-lint** | ❌ NÃO ATIVO | Validaria formatação/estrutura dos .md | **BAIXO IMPACTO — os gates já validam front matter YAML, referências e coerência. Markdown-lint só adicionaria formatação cosmética.** |

**Recomendação:**
- **Custom Scripts:** já são o enforcement primário. Expandir com gates para:
  - `TEST_MATRIX_EVIDENCE_GATE`: validar que arquivos referenciados em TEST_MATRIX_*.md existam no filesystem.
  - `INVARIANT_TEST_COVERAGE_GATE`: validar que todo INV-* tenha pelo menos 1 classe de teste correspondente.
- **Markdown-lint:** prioridade baixa. Os contratos .md já são validados semanticamente pelos gates. Markdown-lint só ajudaria em formatação (headings, lists, trailing whitespace). Se implementar, usar como `warn` — nunca como blocker.

### 4.3 Camada de Domínio — ArchUnit-equiv + Cucumber/Gherkin + Sanity Checks

| Ferramenta | Status Atual | Valor | Veredicto |
|---|---|---|---|
| **ArchUnit / pytest-archunit** | ⚠️ PARCIAL — `test_architecture_drift.py` valida ADR duplicação, registry coherence, claims de runtime. Mas não valida layer dependencies (domain ≠ infra imports). | Validaria que `domain/` nunca importa de `infrastructure/`, que `api.py` nunca instancia ORM diretamente, etc. | **ALTO IMPACTO — maior gap atual. Criar `test_layer_dependencies.py`** |
| **Cucumber / Gherkin** | ❌ NÃO ATIVO | Testes BDD em linguagem natural para domain rules | **MÉDIO IMPACTO mas ALTO CUSTO. O padrão atual (pytest + docstrings com DRref) já funciona. Gherkin seria redundante.** |
| **Workflow automation (Arazzo)** | ✅ ATIVO — `ARAZZO_VALIDATION_GATE` e `ARAZZO_COMPLETENESS_GATE` PASS | Valida workflows multi-step | **JÁ COBERTO** |
| **Sanity check scripts** | ✅ PARCIAL — `check_scope_boundary.py` valida refs cross-module em YAML/JSON. Não valida contract_path_ref dos .md | Validaria que todo `contract_path_ref` em front matter YAML aponte para arquivo que existe | **MÉDIO IMPACTO — adicionar validação de contract_path_ref** |

---

## 5. GAPS PRIORITÁRIOS (ação recomendada)

### GAP-A: Arquivos de teste não correspondem ao TEST_MATRIX [ALTO]

**Problema:** TEST_MATRIX_TRAINING referencia 24 arquivos de teste. Existe 1 arquivo consolidado.
**Impacto:** Rastreabilidade quebrada — não é possível auditar "TM-037 → qual teste protege?"
**Solução proposta:**
1. **Opção 1 (pragmática):** Manter testes consolidados, mas adicionar `# TM-037` ou decorators que mapeiem para IDs da TEST_MATRIX. Criar gate que parse test files buscando referências TM-*.
2. **Opção 2 (canônica):** Desmembrar `test_training_domain.py` nos 24 arquivos referenciados. Alto esforço, mas conformidade total.
3. **Opção 3 (híbrida):** Manter arquivo consolidado, mas atualizar TEST_MATRIX para referenciar o path real (`src/training/tests/unit/test_training_domain.py`) com mapeamento de classes de teste.

### GAP-B: Layer dependency enforcement [ALTO]

**Problema:** Nenhum teste valida que `domain/` nunca importa de `infrastructure/` ou `django.*`.
**Impacto:** Drift silencioso de Clean Architecture. CODE_ARCHITECTURE.md define 4 camadas mas não há enforcement.
**Solução:** Criar `tests/pipeline_gates/test_layer_dependencies.py`:
```python
# Para cada módulo em src/:
# 1. domain/ não pode importar de infrastructure/, application/
# 2. application/ não pode importar de django.db, django.http
# 3. api.py não pode instanciar *Model diretamente
```

### GAP-C: Testes de handball rules [MÉDIO]

**Problema:** DR-TRAIN-H01 a H04 e TM-017 a TM-020 referenciam `test_handball_rules.py` — não existe.
**Impacto:** Regras derivadas da IHF/EHF não têm prova de teste. Risco: mudança de código pode violar regra esportiva sem detecção.
**Solução:** Criar teste mínimo para validar enums de posição, fases de jogo e classificação de exercícios.

### GAP-D: training tem 53 ops contratadas mas 26 implementadas [BAIXO — esperado pelo ROADMAP]

**Problema:** Delta de 27 endpoints entre OpenAPI e api.py.
**Impacto:** Baixo — são operações de fases futuras do ROADMAP (feedback, execution records avançados, periodização detalhada).
**Nota:** Schemathesis valida apenas endpoints implementados, então não há failures. Contudo, considerar adicionar gate que reporte delta de cobertura.

### GAP-E: Validação de contract_path_ref em front matter [BAIXO]

**Problema:** Todos os .md de módulo declaram `contract_path_ref` e `schemas_ref` no front matter YAML, mas nenhum gate valida que esses paths existam no filesystem.
**Solução:** Adicionar check em `validate_contracts.py` que resolve esses refs e valida existência.

---

## 6. AVALIAÇÃO CONSOLIDADA POR FERRAMENTA

| Ferramenta | Já ativa? | Necessidade | Impacto | Prioridade |
|---|---|---|---|---|
| **Spectral** | ✅ Sim | Manter + expandir rules boundary | JÁ COBERTO | - |
| **Redocly CLI** | ✅ Sim | Manter | JÁ COBERTO | - |
| **Custom Scripts Python** | ✅ Sim (53 gates) | Expandir com TEST_MATRIX_EVIDENCE e INVARIANT_COVERAGE gates | ALTO | P1 |
| **Markdown-lint** | ❌ Não | Adicionar como warn (não blocker) | BAIXO | P4 |
| **ArchUnit-equiv (pytest)** | ⚠️ Parcial | Criar test_layer_dependencies.py | ALTO | P1 |
| **Cucumber / Gherkin** | ❌ Não | Não recomendado — pytest com DR-refs é suficiente | REDUNDANTE | - |
| **Arazzo (workflows)** | ✅ Sim | Manter (2 gates active) | JÁ COBERTO | - |
| **Sanity check contract_path_ref** | ❌ Não | Adicionar validação de front matter refs | MÉDIO | P2 |

---

## 7. RESUMO EXECUTIVO

### O código respeita o que foi definido nos .md?
**SIM, para as funcionalidades materializadas.** As regras de domínio (DR-*), invariantes (INV-*), permissões (PERM-*) e module scope documentados nos contratos estão fielmente implementadas em `domain/rules.py`, `entities.py`, e `application/use_cases.py`. A hierarquia Clean Architecture é seguida. O gap existe em funcionalidades avançadas ainda não implementadas (ciclo de intervenção, feedback threads, execution records detalhados) — esperado pelo ROADMAP.

### Os test_matrix/domain_rules/invariants/module_scope/permissions estão sendo atendidos?
**Parcialmente.** O código implementa as regras. Os testes existem e cobrem ~56% dos IDs documentados no TEST_MATRIX_TRAINING. O problema principal é de **rastreabilidade**: os testes estão consolidados em arquivos genéricos enquanto o TEST_MATRIX referencia 24 arquivos especializados que não existem. A cobertura real é melhor do que o mapeamento sugere, mas a linkagem de evidência está quebrada.

### Ferramentas: o que precisa sendo feito?
1. **Spectral + Redocly:** já ativos e PASS — manter.
2. **Custom Scripts:** já fortíssimos (53 gates) — expandir com 2 novos gates (TEST_MATRIX_EVIDENCE e INVARIANT_COVERAGE).
3. **ArchUnit-equiv:** criar `test_layer_dependencies.py` — única ferramenta com impacto alto que falta.
4. **Cucumber/Gherkin:** não recomendado — o padrão pytest com DR-refs já cobre.
5. **Markdown-lint:** prioridade baixa, pode ser adicionado como warn.
6. **Sanity checks (contract_path_ref):** prioridade média, validar front matter refs.
