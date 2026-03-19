---
module: "video"
system_scope_ref: "../../../_canon/SYSTEM_SCOPE.md"
handball_rules_ref: "../../../_canon/HANDBALL_RULES_DOMAIN.md"
handball_semantic_applicability: false
type: "invariants"
updated: "2026-03-19"
---

# INVARIANTS_VIDEO.md

## Objetivo
Documentar as 12 invariantes operacionais que sistema deve garantir em tempo de execução.

## Invariantes

### INV-VID-001: Timecode é sempre ISO 8601 + Offset Lógico
Cada `MediaSegment` contém `timestamp_captured` (ISO 8601 UTC) + `timecode_logical` (inteiro, offset em ms desde início do jogo). Conversão entre eles é determinística e reversível.

### INV-VID-002: MatchMediaSession Imutável Após Published
Uma vez `state = PUBLISHED`, nenhum campo de `MatchMediaSession` (metadata, políticas de distribuição, retenção) pode ser alterado. Estados anteriores permitem edição.

### INV-VID-003: MediaSegment Sem Gaps Temporais
Para uma partida completa, a sequência de `MediaSegment`'s deve ser contígua no timecode lógico (nenhum gap, nenhuma sobreposição).

### INV-VID-004: Transcode Profile Resulta em Mezzanine
Dados que entram no pipeline de transcode **sempre** derivam de `mezzanine_asset_id`, nunca de outro perfil transcoded.

### INV-VID-005: Clipping Exige Contexto Semântico
Nenhum `ClipDefinition` pode ser criado sem pelo menos um dos seguintes: `scout_event_id`, `scenario_context`, `zone_label` ou `athlete_ids`. Clipping vazio é 422.

### INV-VID-006: Acesso Nunca Escapa do Scope
Um usuário nunca pode acessar um `MediaSegment` se não tem permissão no `MatchMediaSession` pai. Acesso granular é proibido do ponto de vista de autorização.

### INV-VID-007: Retenção Não pode ser Indefinida
Toda `MatchMediaSession` tem `retentionPolicy.expiresAt` definido (data+hora explícita). Sem expiração = padrão 7 dias (INV-VID-008).

### INV-VID-008: Retenção Padrão é Conservadora
Se `retentionPolicy` não for explicitamente set, sistema aplica `DELETE_AFTER_7_DAYS`. Nenhuma política de "armazena para sempre" silenciosa.

### INV-VID-009: Auditoria de Acesso Sempre Registrada
Toda leitura de `MediaSegment` por usuário cria entrada em log de auditoria: `user_id`, `session_id`, `segment_id`, `timestamp`, `duration_watched`.

### INV-VID-010: Scout Timecode Nunca Muda
Uma vez que um evento scout é registrado com `timecode_video = T`, esse timecode nunca é reescrito. Se há desalinhamento, é o vídeo que se ajusta (INV-VID-011), não o scout.

### INV-VID-011: Sync Layer Resolve Desalinhamento
Quando timecode de vídeo diverge de scout por >100ms, `SyncService` emite evento `VIDEO_SYNC_ADJUSTMENT` com novo timecode aceito. Histórico é preservado.

### INV-VID-012: Distribuição é Idempotente
Enviar um `ClipDefinition` para CDN duas vezes com mesmo `clip_id` não cria duplicatas. Segundo envio é ignorado (idempotência por chave).

