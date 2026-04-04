# Auditoria Completa — HB Track

**Data**: 2026-03-31  
**Branch**: main @ `51363e9`  
**Escopo**: canon ↔ contratos ↔ código ↔ gates ↔ tooling

---

## Resumo Executivo

| Camada | Status | Nota |
|--------|--------|------|
| Código fonte (349 .py) | ✅ Zero erros de sintaxe | Todos parseable |
| Arquitetura 3-layer | ✅ 17/17 módulos completos | Clean Architecture |
| Roteamento URL | ✅ 17/17 montados corretamente | `config/urls.py` |
| Pipeline de validação | ⚠️ 21 PASS, 2 FAIL, 30 SKIP | 1 FAIL bloqueante (infra) |
| Paridade endpoints | ❌ 2 discrepâncias | training (27 faltam), video (1 extra) |
| Vinculação operation_id | ❌ 9/17 módulos sem binding | Drift potencial |
| Cobertura de testes | ⚠️ 11/17 com cobertura mínima | 1 arquivo de teste |
| MODULE_SCOPE docs | ⚠️ 13/17 são stubs (~20 linhas) | Sem conteúdo real |

---

## 🔴 CRÍTICOS — Impedimentos de Funcionamento Real

### C1. ASYNCAPI_VALIDATION_GATE em FAIL (bloqueante)

O **único gate bloqueante em FAIL** no pipeline precommit. Causa: timeout do Node.js ao chamar o CLI do AsyncAPI via NVM no WSL.

```json
{
  "gate_id": "ASYNCAPI_VALIDATION_GATE",
  "status": "FAIL",
  "blocking": true,
  "exit_code": 2,
  "blocking_code": "ERROR_INFRA",
  "summary": "asyncapi CLI não disponível via toolchain WSL-native (node_modules/NVM).",
  "violations": [{
    "blocking_code": "ERROR_INFRA",
    "artifact": "asyncapi",
    "message": "Tool timed out: /home/davis/.nvm/versions/node/v24.14.0/bin/node",
    "severity": "error"
  }]
}
```

**Impacto**: Pipeline precommit retorna `overall_status: FAIL, exit_code: 3`. O pre-commit hook v4 executa `validate_contracts.py --profile precommit` e o resultado global será FAIL.

**Opções de correção**:
1. Instalar/configurar corretamente o `@asyncapi/cli` no ambiente WSL
2. Criar waiver W-005 para `ASYNCAPI_VALIDATION_GATE` (scope: infra/WSL)
3. Ajustar o timeout do gate no validator

---

### C2. Training — 27 endpoints ausentes no código

| Métrica | Valor |
|---------|-------|
| OpenAPI operationIds | 53 |
| api.py @router decorators | 26 |
| Endpoints faltantes | **27** |

Categorias dos endpoints ausentes:
- Recomendações: `generateRecommendation`, `acceptRecommendation`, `dismissRecommendation` (3)
- Fila de atenção: `listAttentionQueue`, `getAttentionQueueItem`, `resolveAttentionQueueItem`, `createAttentionQueueItem` (4)
- Inelegibilidade: `markAthleteIneligible`, `clearAthleteIneligibility` (2)
- Feedback: `closeFeedbackThread` (1)
- Load chart: `getLoadChart` (1)
- Chat: `sendChatMessage` (1)
- Suggestion: `getSuggestedTraining` (1)
- CRUDs avançados e operações de periodização, execution records, wellness pre/post, attendance, reorder blocks, etc.

**Mitigação atual**: Waiver W-003 ativo (expira 2026-09-30). Implementação planejada para ROADMAP fases 7+.

---

### C3. Video — 1 endpoint excedente no código

| Métrica | Valor |
|---------|-------|
| OpenAPI operationIds | 9 |
| api.py @router decorators | 10 |
| **Endpoint extra** | `list_distributions` |

**Funções no código** (src/video/api.py):
1. `create_session` → `createSession` ✅
2. `list_sessions` → `listSessions` ✅
3. `get_session` → `getSession` ✅
4. `patch_session` → `patchSession` ✅
5. `create_segment` → `createSegment` ✅
6. `list_segments` → `listSegments` ✅
7. `create_clip` → `createClip` ✅
8. `list_clips` → `listClips` ✅
9. `publish_distribution` → `publishDistribution` ✅
10. **`list_distributions`** → ❌ **SEM operationId correspondente no contrato**

**OpenAPI (contracts/openapi/paths/video.yaml)** declara apenas `publishDistribution`, não `listDistributions`.

**Ação necessária**: Adicionar `listDistributions` ao contrato OpenAPI de video **OU** remover `list_distributions` do código.

---

### C4. 9/17 módulos sem binding `operation_id` nos decoradores de rota

| Status | Módulos | Count |
|--------|---------|-------|
| **SEM** operation_id | training, scout, exercises, analytics, reports, ai_ingestion, audit, notifications, video | 9 |
| **COM** operation_id | users(4), seasons(6), teams(8), matches(6), competitions(6), wellness(5), medical(5), identity_access(9) | 8 |

**Impacto**: Django Ninja não gerará as operationIds canônicas se `operation_id=` não for declarado no `@router`. O OpenAPI gerado pelo backend divergirá do contrato normativo, impossibilitando validação automática de paridade contrato↔runtime.

---

## 🟡 ALTO — Gaps Estruturais

### H1. 3 gates registrados no GATES_REGISTRY.yaml mas ausentes do validator

| Gate | blocking | Situação |
|------|----------|----------|
| `SCOPE_BOUNDARY_GATE` | true | Existe como script separado em `scripts/gates/check_scope_boundary.py` mas **NÃO é chamado** pelo `validate_contracts.py` |
| `ARCH_DECISION_PRESENCE_GATE` | true | Não implementado |
| `FRONTEND_CONTRACT_GATE` | false | Não implementado (FASE 5 futura) |

**Impacto**: O GATES_REGISTRY.yaml declara 56 gates mas o validator só executa 53. O SCOPE_BOUNDARY_GATE tem código pronto mas não está integrado na pipeline.

---

### H2. 13/17 MODULE_SCOPE docs são stubs vazios

| Linhas | Módulos |
|--------|---------|
| 145 | training |
| 111 | exercises |
| 94 | video |
| 24 | analytics |
| **≤20** | **ai_ingestion, audit, competitions, identity_access, matches, medical, notifications, reports, scout, seasons, teams, users, wellness** (13 módulos) |

Os documentos com ≤20 linhas contêm apenas o template vazio — nenhuma responsabilidade, limite de módulo, ou invariante específico definido.

---

### H3. Entidades de domínio vs modelos ORM — gaps de persistência

| Módulo | Entidades | ORM Models | Delta |
|--------|-----------|------------|-------|
| training | 17 | 10 | **-7** |
| video | 9 | 4 | **-5** |
| analytics | 3 | 1 | **-2** |
| users | 3 | 1 | **-2** |
| teams | 2 | 1 | -1 |
| seasons | 2 | 1 | -1 |
| competitions | 2 | 1 | -1 |
| notifications | 2 | 2 | ✅ |
| identity_access | 3 | 3 | ✅ |
| exercises | 4 | 4 | ✅ |
| matches | 1 | 1 | ✅ |
| medical | 1 | 1 | ✅ |
| scout | 1 | 1 | ✅ |
| audit | 1 | 1 | ✅ |
| reports | 1 | 1 | ✅ |
| ai_ingestion | 1 | 1 | ✅ |
| wellness | 2 | 1 | -1 |

Nem toda entidade de domínio precisa de ORM (value objects, DTOs), mas deltas grandes (training -7, video -5) indicam funcionalidades declaradas no domínio mas sem persistência implementada.

---

### H4. Cobertura de testes por módulo

| Arquivos de teste | Módulos |
|-------------------|---------|
| 26 | training |
| 3 | video, users, teams, seasons, identity_access |
| 2 | wellness, scout, medical, matches, competitions |
| **1** | **reports, notifications, exercises, audit, analytics, ai_ingestion** |

Complemento: `tests/pipeline_gates/` tem 18 arquivos / 342+ test functions cobrindo gates e invariantes.

---

## 🟢 VERIFICADOS OK

### Arquitetura e Código

| Aspecto | Resultado |
|---------|-----------|
| 349 arquivos Python | Zero erros de sintaxe |
| 17 módulos Clean Architecture | Todos com: `api.py`, `schemas.py`, `domain/entities.py`, `domain/rules.py`, `application/use_cases.py`, `infrastructure/repository.py`, `infrastructure/models.py` |
| URL routing (`config/urls.py`) | 17/17 módulos montados via `api.add_router()` com prefixos corretos |
| 15/17 endpoint parity | Todos exceto training e video |
| Auth pattern | Sem stubs 401 — usa Django Ninja auth via request attributes (`_session_id`, `_principal_user_id`, `_role_labels`) |
| Domain rules | Todos os 17 módulos têm `rules.py` com regras reais (39–264 linhas) |
| Root `models.py` | 17/17 vazios (legacy) — modelos ORM em `infrastructure/models.py` |

### Contratos

| Aspecto | Resultado |
|---------|-----------|
| OpenAPI root (`openapi.yaml`) | 17 $refs para `paths/*.yaml` — PASS no gate |
| AsyncAPI | `asyncapi.yaml` + 62 canais definidos em `channels/` |
| JSON Schemas | 47 arquivos em `contracts/schemas/` |
| OpenAPI $ref hermeticity | PASS — todos os $refs resolvem |
| Spectral linting | PASS |
| Arazzo workflows | PASS (structure + completeness) |

### Gates Pipeline

| Gate | Status |
|------|--------|
| AXIOM_INTEGRITY_GATE | ✅ PASS |
| PATH_CANONICALITY_GATE | ✅ PASS |
| CANON_ALLOWLIST_GATE | ✅ PASS |
| PLACEHOLDER_RESIDUE_GATE | ✅ PASS |
| REF_HERMETICITY_GATE | ✅ PASS |
| TOOLING_CONFIG_GATE | ✅ PASS |
| OPENAPI_ROOT_STRUCTURE_GATE | ✅ PASS |
| OPENAPI_ROOT_MODULE_SYNC_GATE | ✅ PASS |
| OPENAPI_POLICY_RULESET_GATE | ✅ PASS |
| JSON_SCHEMA_VALIDATION_GATE | ✅ PASS |
| CROSS_SPEC_ALIGNMENT_GATE | ✅ PASS |
| ARAZZO_VALIDATION_GATE | ✅ PASS |
| ARAZZO_COMPLETENESS_GATE | ✅ PASS |
| SPECTRAL_LINTING_GATE | ✅ PASS |
| UI_DOC_VALIDATION_GATE | ✅ PASS |
| HANDOFF_COHERENCE_GATE | ✅ PASS |
| MODULE_REGISTRY_GATE | ✅ PASS |
| MODULE_STATUS_COHERENCE_GATE | ✅ PASS |
| SURFACE_PROMOTION_COHERENCE_GATE | ✅ PASS |
| WAIVER_VALIDITY_GATE | ✅ PASS |
| READINESS_GENERATION_COMPATIBILITY_GATE | ✅ PASS |
| ASYNCAPI_VALIDATION_GATE | ❌ FAIL (ERROR_INFRA) |
| READINESS_SUMMARY_GATE | ❌ FAIL (non-blocking, derivado) |
| 30 gates | ⏭️ SKIP_NOT_APPLICABLE |

### Tooling e CI

| Aspecto | Resultado |
|---------|-----------|
| Pre-commit hook v4 | 7 fases de validação ativas |
| `scripts/hb` CLI v2 | verify, check, artifact, reset |
| PERMISSIONS docs | Alinhados com contratos (corrigido em `51363e9`) |
| CI pipeline | 12/12 checks passing em main |
| Waivers | 4 ativos (W-001..W-004) válidos |

---

## Waivers Ativos

| ID | Gate | Scope | Expira | Razão |
|----|------|-------|--------|-------|
| W-001 | HTTP_RUNTIME_CONTRACT_GATE | tests/schemathesis | 2026-06-30 | Schemathesis requer PostgreSQL + Redis + Django server. CI usa `HB_RUN_SCHEMATHESIS=1`. |
| W-002 | PIPELINE_GATES_SLOW_TEST | test_session_state_phase3.py::TestStage23ExitCodes | 2026-06-30 | Executa `hb stage3` (~2-5 min). Marcado `@pytest.mark.slow`, excluído do CI. |
| W-003 | ENDPOINT_PARITY_GATE | training | 2026-09-30 | 27 endpoints pendentes de fases 7+ do ROADMAP. |
| W-004 | IDENTITY_ACCESS_FEATURES | identity_access | 2026-05-31 | Password reset e MFA (TOTP) não implementados. Contrato será revisado via CDD. |

---

## Trabalho Não-commitado (pendente)

| Arquivo | Tipo | Descrição |
|---------|------|-----------|
| `config/settings.py` | Modificado | RateLimitMiddleware adicionado ao MIDDLEWARE |
| `src/shared/middleware.py` | Modificado | Implementação RateLimitMiddleware |
| `tests/pipeline_gates/test_layer_dependencies.py` | Novo | 68 testes de dependência de camada |
| `tests/pipeline_gates/test_rate_limiting.py` | Novo | 4 testes de rate limiting |
| `.contract_driven/waivers.json` | Modificado | 4 waivers formalizados |
| `_reports/session_start.json` | Modificado | Estado de sessão atualizado |

---

## Prioridades de Correção Recomendadas

| # | Gap | Severidade | Esforço | Ação |
|---|-----|------------|---------|------|
| 1 | C1 — ASYNCAPI_VALIDATION_GATE | Bloqueante | Baixo | Criar waiver W-005 ou corrigir toolchain Node.js/WSL |
| 2 | C3 — Video `list_distributions` surplus | Crítico | Baixo | Adicionar `listDistributions` ao contrato OpenAPI de video |
| 3 | C4 — 9 módulos sem `operation_id` | Crítico | Médio | Adicionar `operation_id=` a todos os `@router` dos 9 módulos |
| 4 | H1 — SCOPE_BOUNDARY_GATE não integrado | Alto | Baixo | Integrar `check_scope_boundary.py` no `validate_contracts.py` |
| 5 | H2 — 13 MODULE_SCOPE stubs | Alto | Alto | Preencher com responsabilidades, limites e invariantes reais |
| 6 | — Trabalho pendente não-commitado | Médio | Baixo | `git add` + commit dos arquivos listados acima |
| 7 | H3 — Gaps entidade/ORM | Médio | Alto | Avaliar quais entidades precisam de persistência real |
| 8 | H4 — 11 módulos com 1 teste | Médio | Alto | Expandir cobertura de testes unitários |

---

## Inventário Numérico

| Recurso | Quantidade |
|---------|-----------|
| Módulos canônicos | 17 |
| Arquivos Python (src/) | 349 |
| OpenAPI path files | 17 |
| JSON Schemas | 47 |
| AsyncAPI channels | 62 |
| Gates registrados | 56 |
| Gates executados | 53 |
| Gates PASS | 21 |
| Gates FAIL | 2 |
| Gates SKIP | 30 |
| Waivers ativos | 4 |
| Testes pipeline_gates | 342+ funções (18 arquivos) |
| Testes de módulo | 1–26 arquivos por módulo |
| Migrations | 2–5 por módulo |
| ADRs | 34 |
| Agent prompts | 19 |
| DECISION_IR YAMLs | 7 |
| Domain rules (linhas) | 39–264 por módulo |
