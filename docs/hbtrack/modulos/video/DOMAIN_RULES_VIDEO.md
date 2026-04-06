---
module: "video"
system_scope_ref: "../../../_canon/SYSTEM_SCOPE.md"
handball_rules_ref: "../../../_canon/HANDBALL_RULES_DOMAIN.md"
handball_semantic_applicability: false
type: "domain-rules"
contract_path_ref: "../../../../contracts/openapi/paths/video.yaml"
schemas_ref: "../../../../contracts/schemas/video/"
updated: "2026-03-19"
---

# DOMAIN_RULES_VIDEO.md

## Objetivo
Documentar as 10 principais regras de domínio que governam comportamento do módulo `video`.

## Regras de Domínio

### DR-VID-001: Timecode Único Obrigatório
Cada media segment **deve** ser associado a um timecode lógico único da partida, não só timestamp de captura. O timecode permite sincronização exata com eventos de scout, placar e tracking.

### DR-VID-002: Dual Pipeline Determinístico
Sistema produz simultaneamente dois outputs de um input de captura única:
- **Pipeline técnico**: baixa latência, scrubbing rápido, player técnico
- **Pipeline público**: ABR, CDN, renditions múltiplas para compatibilidade

Ambas saem do mesmo segmento mezzanine.

### DR-VID-003: Ingestão Edge-First
Toda captura começa em um edge node local (não na nuvem). Edge node mantém buffer, cache operacional, relógio sincronizado e store-and-forward. Garante captura contínua mesmo com falha de uplink.

### DR-VID-004: Clipping Semântico Sempre
Clipping **não é** apenas corte temporal. Cada clip deve incluir metadados semânticos (evento scout, zona de quadra, atletas envolvidos, contexto de placar) para ser pesquisável.

### DR-VID-005: Imutabilidade de Segments
Após `MediaSegment` ser finalizado (`state = FINALIZED`), nenhum campo pode ser alterado. Mudanças subsequentes criam novo segment (seguindo padrão append-only).

### DR-VID-006: Transcodificação Lazy (on-Demand)
Perfis de transcodificação são gerados **sob demanda**, não pré-computados. Mezzanine é a SSOT; derivados são cached.

### DR-VID-007: Acesso Baseado em MatchMediaSession
Autorização é sempre scopada ao nível de `MatchMediaSession` (partida). Um usuário vê toda a captura de uma partida ou nenhuma — não há acesso granular em-level-segment.

### DR-VID-008: Retenção Explícita
Cada `MatchMediaSession` tem `retentionPolicy` explícita (ex: `keep_30_days`, `archive_s3`, `public_forever`). Sem política explícita = padrão conservador (delete em 7 dias).

### DR-VID-009: Distribuição é Sempre Rastreada
Toda distribuição a um destino externo (CDN, parceiro, API) registra evento de auditoria: quem acessou, quando, por quanto tempo, de qualidade.

### DR-VID-010: Sincronização com Scout é Referência
Quando há conflito de timecode entre vídeo e evento de scout (ex: scout registra evento em T=300s mas vídeo diz T=295s), **scout marca o correto**. Video readapta se necessário durante sync layer.

## Âncoras estruturadas
- As entidades soberanas e seus campos mapeados para runtime estão em `docs/hbtrack/modulos/video/graph/entity_graph.yaml`.
- O mapa mínimo de operações e permissões publicadas está em `docs/hbtrack/modulos/video/graph/endpoints.yaml`.
- O mapa mínimo de erros transport/domain do módulo está em `docs/hbtrack/modulos/video/graph/errors.yaml`.

