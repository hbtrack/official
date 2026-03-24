---
adr_id: ADR-033
title: "Video como 17º Módulo Canônico — Plataforma de Mídia Integrada"
status: Accepted
date: "2026-03-19"
deciders: [product-lead, tech-lead, platform-architect]
decision: "Elevar video de funcionalidade implícita para módulo soberano no MODULE_REGISTRY com OpenAPI, AsyncAPI e boundary contracts"
tags: [architecture, modules, media, streaming, cdd]
benchmark_basis: "Opção C — Spiideo, KINEXON, Catapult demonstram que captura/ingest é domínio soberano, não sub-feature"
---

# ADR-033 — Video como 17º Módulo Canônico

## Contexto

O HB Track necessita plataforma de mídia ao vivo que unifique:
- Captura e ingestão na arena (edge-first)
- Sincronização temporal com tracking, scouting e placar
- Transcodificação e empacotamento para múltiplos destinos
- Distribuição dual: técnica interna (baixa latência) e pública/broadcast (escala de CDN)
- Indexação semântica para clipping e recuperação contextual

Os 16 módulos canônicos atuais cobrem:
- Treinamento (`training`), bem-estar (`wellness`), medicina (`medical`)
- Competição (`competitions`, `matches`, `teams`, `seasons`), scouting (`scout`)
- Gestão (`users`, `identity_access`), análise (`analytics`, `reports`)
- Plataforma (`notifications`, `audit`, `ai_ingestion`)
- Exercícios (`exercises`)

**Video não se encaixa naturalmente em nenhum deles.**

### Alternativas Consideradas

1. **Video como funcionalidade de scout**: integrar captura + ingest em scout (análise técnica)
   - ❌ Scout é domínio de análise, não infraestrutura de mídia
   - ❌ Clipping e distribuição pública não cabem em scout
   - ❌ Difícil separar futuramente se video crescer

2. **Video como subsistema transversal (implicit em platform-core)**: sem entrada em MODULE_REGISTRY
   - ❌ Viola CDD: módulo sem registro quebra determinismo de gates
   - ❌ Impossibilita versionamento formal (OpenAPI, AsyncAPI)
   - ❌ Risco de boundary violations não detectadas

3. **Video como 17º módulo canônico** ✅ **RECOMENDADO**
   - ✅ Solução clara: nomeação explícita, registrado em MODULE_REGISTRY
   - ✅ Boundary contracts formais com scout (sincronização), analytics (clipping semântico)
   - ✅ Escalável: suporta edge nodes, transcode profiles, distribuidores customizados
   - ✅ Diferenciação: "plataforma de mídia integrada" vs "vídeo como feature"

## Decisão

**Video é promovido a 17º módulo canônico com:**

1. **Registro em MODULE_REGISTRY.yaml**
   - module: `video`
   - owner: `platform-core`
   - status: `scaffold` (docs) → `draft_contract` (OpenAPI) → `validated_contract`
   - expected_surfaces: openapi_sync, json_schema, test_matrix, asyncapi, arazzo, permissions, decision_ir

2. **Documentação mínima (Fase 1: new_module)**
   - `docs/hbtrack/modulos/video/README.md`
   - `docs/hbtrack/modulos/video/MODULE_SCOPE_VIDEO.md`
   - `docs/hbtrack/modulos/video/DOMAIN_RULES_VIDEO.md`
   - `docs/hbtrack/modulos/video/INVARIANTS_VIDEO.md`
   - `docs/hbtrack/modulos/video/TEST_MATRIX_VIDEO.md`

3. **Contratos técnicos (Fase 2: new_contract, new_event, new_workflow)**
   - OpenAPI: captura live, ingest, transcode status, playback sessions
   - AsyncAPI: capture.started, segment.ready, transcode.completed, distribution.published
   - Arazzo: workflows de captura → sync → distribuição
   - Permissions: RBAC para acesso a feeds técnico/público

4. **Boundary contracts**
   - **video ↔ scout**: sincronização (scout eventos → video timecode)
   - **video ↔ analytics**: clipping semântico (analytics eventos → video ranges)
   - **video ↔ training**: contexto de sessão (training session → video session)
   - **video ↔ audit**: rastreamento de acesso e distribuição

## Consequências

**Vantagens:**
- Clareza operacional: módulo nomeado, auditável, com contratos formais
- Extensibilidade: suporta edge nodes, transcoders, distribuidores sem quebra arquitetural
- Diferenciação: plataforma de mídia integrada diferencia HB Track de mercado modular
- Determinismo CDD: gates de boundary validation detectam violações precoce

**Desvantagens:**
- Complexidade de MODULE_REGISTRY cresce (17 em vez de 16)
- Requer gates adicionais para validação de boundaries (video ↔ scout, video ↔ analytics)
- Timeline: novo módulo exige passar por pipeline completo (Fases 0-5)

## Impact Map

**Artefatos canônicos a atualizar:**
- `docs/_canon/MODULE_REGISTRY.yaml` — adicionar entry para `video` (status: scaffold)
- `docs/_canon/SYSTEM_SCOPE.md` — adicionar seção "video module" com responsabilidades
- `docs/_canon/ARCHITECTURE.md` — diagrama: video como peer de scout, analytics, training
- `.contract_driven/GATES_REGISTRY.yaml` — adicionar VIDEO_SCOPE_BOUNDARY_GATE
- `docs/_canon/ARCHITECTURE_DECISION_BACKLOG.md` — status: resolved

**Gates a executar (após Fase 2):**
- `compile_api_policy.py --all` (após criar contratos)
- `validate_contracts.py` (validar nenhum gate quebrou)
- `check_scope_boundary.py` (validar video ↔ scout, video ↔ analytics, video ↔ training)

**Pipeline esperado:**
- Fase 0: `hb verify --task-type new_module --module video` ✓
- Fase 1: `hb check --module video` (docs mínimas) ✓
- Fase 2: `new_contract` (OpenAPI), `new_event` (AsyncAPI), `new_workflow` (Arazzo)
- Fase 3: Validação de gates (10/10 PASS esperado)
- Fase 4: Atualizar MODULE_REGISTRY (status: draft_contract)
- Fase 5: Handoff final

## Decisões Relacionadas

- **ADR-034**: Scope Boundary Validation — detecta violações cross-module
- **ADR-025**: CDCT/Pact Strategy — testes de boundary contracts
- **ADR-024**: Contract Versioning — versionamento de APIs de video
- **ADR-007/008**: Auth/Authz — aplicadas a endpoints de video

## Próximas Ações

1. ✅ ADR-033 Accepted (este documento)
2. → Executar `hb verify --task-type new_module --module video`
3. → Criar docs mínimas do módulo (README, DOMAIN_RULES, INVARIANTS, MODULE_SCOPE, TEST_MATRIX)
4. → Criar OpenAPI para captura, ingest, playback
5. → Criar AsyncAPI para eventos de ciclo de vida de mídia
6. → Validar gates

Reference: `docs/guias/video.md` (apoio conceitual não canônico da arquitetura de mídia)
