---
module: "video"
system_scope_ref: "../../../_canon/SYSTEM_SCOPE.md"
handball_rules_ref: "../../../_canon/HANDBALL_RULES_DOMAIN.md"
handball_semantic_applicability: false
type: "state-model"
contract_path_ref: "../../../../contracts/openapi/paths/video.yaml"
asyncapi_ref: "../../../../contracts/asyncapi/asyncapi.yaml"
schemas_ref: "../../../../contracts/schemas/video/"
diagram_format: "mermaid"
decision_ir_ref: "ADR-033: Video Module Canonicalization"
updated: "2026-03-19"
---

# STATE_MODEL_VIDEO.md

## Objetivo
Documentar os estados e transições válidas de uma MatchMediaSession no módulo `video`. 
Governa o ciclo de vida completo: captura edge-first → sincronização com scout → 
transcodificação multi-codec → publicação em CDN/broadcast.

## Entidade Principal
- **MatchMediaSession** — raiz de autorização, identifica uma captura única de partida

## Regras de Modelagem

1. **Toda transição é gatilhada por evento ou ação explicita** — nenhuma transição silenciosa
2. **Estado é imutável pós-PUBLISHED** (INV-VID-002) — somente backward: PUBLISHED → ARCHIVED (futuro)
3. **Cada transição tem pré/pós-condições documentadas** — validadas em TEST_MATRIX_VIDEO.md
4. **Timecode é sincronizado em SYNCING** — scout é referência de verdade (DR-VID-010)
5. **Segmentos são append-only** — ao transicionar para próximo estado, novos segmentos não podem ser adicionados ao anterior

## Diagrama de Estados

```mermaid
stateDiagram-v2
  [*] --> DRAFT
  
  DRAFT --> CAPTURING: POST /sessions/{id} state=CAPTURING\n(iniciar captura edge)
  
  CAPTURING --> SYNCING: MediaSegments finalizados\n+ timecode validado vs scout
  
  SYNCING --> TRANSCODING: Sync adjustment aplicado\n+ todos segments em final state
  
  TRANSCODING --> PUBLISHED: Todos DistributionProfiles\ncodificados com sucesso
  
  PUBLISHED --> [*]
  
  DRAFT -.->|erro setup| DRAFT: retry setup
  CAPTURING -.->|erro segmento| CAPTURING: novo tentativa segmento
  SYNCING -.->|desalinhamento| SYNCING: sync adjustment
  TRANSCODING -.->|falha codec| TRANSCODING: retry transcode
```

## Tabela de Estados

| Estado | Descrição | Estado Inicial | Estado Terminal | Duração Típica |
|---|---|---|---|---|
| **DRAFT** | Sessão criada, awaiting start de captura. Metadados e policies podem ser editados. | Sim | Não | 0-5 min |
| **CAPTURING** | Captura em progresso no edge node. MediaSegments sendo ingeridos e finalizados iterativamente. | Não | Não | 60-120 min (duração do jogo) |
| **SYNCING** | Todos os segmentos finalizados; sync service sincronizando timecodes com scout (DR-VID-010, INV-VID-011). Scout é referência; video readapta se necessário. | Não | Não | 5-15 min |
| **TRANSCODING** | Segmentos sincronizados; transcodificação lazy iniciada para cada DistributionProfile (H.264, H.265, VP9, AV1). Celery jobs em progresso (ADR-031). | Não | Não | 30-180 min (depende de codecs + bitrates) |
| **PUBLISHED** | Todos os profiles transcodificados e publicados em CDN/broadcast (DR-VID-002, INV-VID-002). ClipDefinitions públicos acessíveis. **Irrevogável.** | Não | Sim | até retentionPolicy expiration |

## Tabela de Transições

| De | Para | Gatilho | Pré-condição | Pós-condição | Erro se inválido | Observações |
|---|---|---|---|---|---|---|
| DRAFT | CAPTURING | `PATCH /sessions/{id}` com `state=CAPTURING` | MatchMediaSession.state = DRAFT | TimecodeLogicalStart inicializado; edge node buffer pronto; evento `video.capture.started` emitido | 400 Bad Request | DR-VID-001, INV-VID-001: timecode lógico obrigatório |
| CAPTURING | SYNCING | Todos MediaSegments → state=FINALIZED + SyncService triggered | Todos segmentos flushed para mezzanine; timecodes lógicos contíguos (INV-VID-003) | SyncService emite `video.sync.adjustment_applied` se houver divergência >100ms vs scout (INV-VID-011) | 409 Conflict | DR-VID-010: scout é SSOT; video readapta se necessário |
| SYNCING | TRANSCODING | SyncService completa ajustes; transcodificação queued | Timecodes validados e finalizados; INV-VID-010 satisfeita (scout timecode nunca muda) | Celery jobs queued para cada DistributionProfile (ADR-031: Celery 5 + Redis 7) | 500 Internal Server Error | DR-VID-006: lazy transcode; mezzanine é SSOT |
| TRANSCODING | PUBLISHED | Todos DistributionProfiles → encoding complete; DistributionFabric publica em CDN/broadcast | Nenhum transcode job falhou; todos profiles salvos em cache/CDN | INV-VID-002 ativa: MatchMediaSession state=PUBLISHED é imutável; eventos `video.distribution.published` emitidos por target | 503 Service Unavailable | DR-VID-002 dual pipeline: técnico (baixa latência) + público (ABR) |

## Transições de Erro (Estado → Mesmo Estado)

| Gatilho | Estado | Ação | Máx Retries | Backoff |
|---|---|---|---|---|
| MediaSegment ingestão timeout | CAPTURING | Registrar evento `video.distribution.failed` com `failureReason=timeout`; aguardar retry manual | 3 | exponential 5s-30s |
| Sync desalinhamento não-crítico (<100ms) | SYNCING | Ignorar; log e audit (INV-VID-009) | N/A | N/A |
| Transcode codec incompatibility | TRANSCODING | Emitir evento `video.transcode.completed` com erro; registrar em audit; oferecer fallback H.264 | 1 (fallback) | N/A |

## Invariantes por Estado

### DRAFT
- `retentionPolicy` é obrigatório (INV-VID-007, INV-VID-008)
- `technicalContactUserId` é obrigatório
- Nenhum MediaSegment ainda foi criado

### CAPTURING
- **INV-VID-001:** Timecode é ISO 8601 + offset lógico
- **INV-VID-003:** Segmentos sem gaps temporais (contíguo)
- **INV-VID-005:** Clipping semântico exige contexto (scout_event_id, zone_label, athlete_ids ou scenario_context)

### SYNCING
- **INV-VID-010:** Scout timecode nunca muda — somente video se ajusta
- **INV-VID-011:** Sync layer resolve desalinhamen >100ms
- Todos segmentos estão em state=FINALIZED

### TRANSCODING
- **INV-VID-004:** Mezzanine é SSOT; nenhuma rendition pode ser source de outra
- **INV-VID-012:** Distribuição é idempotente (clip_id deduplicado)

### PUBLISHED
- **INV-VID-002:** MatchMediaSession imutável pós-publicação
- **INV-VID-006:** Acesso nunca escapa do scope (BOLA enforcement via MatchMediaSession)
- **INV-VID-009:** Todas as leituras de segmento criaram entrada de auditoria

## Eventos Emitidos por Transição

| Transição | Evento AsyncAPI | Consumidores Esperados |
|---|---|---|
| DRAFT → CAPTURING | `video.capture.started` | scout (sincronizar timecode), analytics (iniciar coreografia), notifications |
| CAPTURING → SYNCING | `video.segment.ready` (iterativo) | transcode pipeline, analytics (clip queries) |
| SYNCING → TRANSCODING | `video.sync.adjustment_applied` (zero ou mais) | audit, analytics (refazer timecodes), scout (log de divergências) |
| TRANSCODING → PUBLISHED | `video.transcode.completed` (por profile) | distribution fabric, public API |
| PUBLISHED (delivery) | `video.distribution.published` \| `video.distribution.failed` | broadcast partners, analytics, audit |

## Cross-Module Boundary Contracts

1. **video ↔ scout** (DR-VID-010)
   - Scout marca timecode em evento; video sincroniza contra ele
   - Scout timecode **nunca** é reescrito; video readapta (INV-VID-010, INV-VID-011)
   - Referência: `scout_event_id` em ClipDefinition

2. **video ↔ analytics**
   - Analytics requisita clip ranges via ClipDefinition + timecode range
   - Video retorna com audit (INV-VID-009)

3. **video ↔ matches**
   - MatchMediaSession.matchId references matches module
   - Match.video_session_id backref (futuro)

4. **video ↔ users**
   - `technicalContactUserId`, `userId` in access logs
   - BOLA enforcement: user sempre no escopo da MatchMediaSession

## Referências de Domínio

- **DR-VID-001..010:** Domain Rules em DOMAIN_RULES_VIDEO.md
- **INV-VID-001..012:** Invariantes em INVARIANTS_VIDEO.md
- **ADR-033:** Video Module Canonicalization (decision to create video as 17th module)
- **ADR-031:** Celery 5 + Redis 7 for async task execution
- **HANDBALL_RULES_DOMAIN.md:** Nenhuma regra de handebol impactando estados de vídeo neste modelo

## Testing Strategy

Cobertura esperada em TEST_MATRIX_VIDEO.md:
- [x] DRAFT → CAPTURING (happy path + setup error retry)
- [x] CAPTURING → SYNCING com segment finalização
- [x] SYNCING → TRANSCODING com scout alignment
- [x] TRANSCODING → PUBLISHED com multi-codec success
- [x] Transições de erro (same-state retry)
- [x] INV-VID-002 enforcement: PUBLISHED é irrevogável
- [x] INV-VID-006 enforcement: BOLA na leitura de segmento

