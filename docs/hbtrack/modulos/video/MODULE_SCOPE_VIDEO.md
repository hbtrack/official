---
module: "video"
system_scope_ref: "../../../_canon/SYSTEM_SCOPE.md"
handball_rules_ref: "../../../_canon/HANDBALL_RULES_DOMAIN.md"
handball_semantic_applicability: false
type: "module-scope"
contract_path_ref: "../../../../contracts/openapi/paths/video.yaml"
schemas_ref: "../../../../contracts/schemas/video/"
updated: "2026-03-19"
---

# MODULE_SCOPE_VIDEO.md

## Objetivo
Definir claramente o que o módulo `video` faz e o que não faz.

## Missão do módulo
`video` existe para ser a **plataforma de mídia ao vivo soberana do HB Track** — capturando, sincronizando, transcod

ificando e distribuindo vídeo através de dois pipelines (técnico e público) como infraestrutura central unificada com tracking, scouting e dados de competição.

## Responsabilidades

- Captura ao vivo em edge nodes (arena) com buffer local e fallback
- Ingestão de feeds externos (TV, produtora, múltiplos ângulos)
- Sincronização temporal com relógio lógico único da partida (TIMECODE)
- Transcodificação para perfis técnicos (baixa latência, scrubbing) e públicos (ABR, CDN)
- Clipping automático/manual com índice semântico (contexto de jogo)
- Distribuição técnica (player para banco, tribuna, comissão)
- Distribuição pública (OTT, broadcasting, parceiros)
- Observabilidade: latência ponta-a-ponta, detecção de perda de sinal

## Atores

| Ator | Papel |
|---|---|
| Match Operator | Inicia/para captura, monitora saúde |
| Technical Analyst | Acessa player técnico, faz clipping, revisa timecode |
| Broadcasting Partner | Recebe feed público, controla distribuição CDN |
| Scout/Video Analyst | Sincroniza anotações com vídeo (via events do scout) |
| System (audit) | Registra acesso a feeds e distribuição |

## Entidades principais

| Entidade | Papel |
|---|---|
| `MatchMediaSession` | Agregado: captura + ingest + sync + transcode + distribuição para uma partida |
| `MediaSegment` | Fato imutável: trecho de vídeo com timecode, codec, bitrate, durações |
| `ClipDefinition` | Recorte semântico: range temporal + contexto (evento scout, placar, zona) |
| `DistributionProfile` | Receita de transcode + empacotamento para um destino (técnico/público) |
| `AccessPolicy` | Quem vê o quê: técnico restrito, público público, parceiros parametrizados |

## Dentro do escopo
- Captura em tempo real (múltiplos modos: panorâmica, auto-follow, multi-ângulo)
- Sincronização temporal com tracking, scouting, placar
- Transcodificação e empacotamento para entrega
- Clipping e indexação semântica
- API de playback (técnica e pública)
- Gestão de retenção de mídia
- Auditoria de acesso e distribuição

## Fora do escopo
- **Broadcast como domínio de negócio** (OTT de varejista, app de streamer, monetização de audiência): implicações comerciais de longo prazo → futuro módulo `media`
- **Edição editorial de pós-produção**: efeitos, color grading, montagem editorial
- **Infra de CDN global**: assumir existe gerenciador externo (CloudFront, Akamai)
- **DRM e gerenciamento de licenças de mídia**: políticas de distribuição externas

## Dependências
- **Módulos upstream:** `matches` (metadados de partida), `scout` (eventos para sincronização), `identity_access` (autenticação de acesso)
- **Módulos downstream:** `analytics` (clipping para análise), `reports` (geração de assets), `audit` (logging de acesso)
- **Artefatos globais:**
  - `SYSTEM_SCOPE.md`
  - `ARCHITECTURE.md` (stack: Celery, Redis, HTTP/streaming)
  - Decisões: ADR-033 (canonicalization), ADR-031 (scope boundary)

## Regras de fronteira

1. Video não assume governança de autorização: identidade vem de `identity_access`, policies de acesso são aplicadas internamente.
2. Video não armazena metadados de partida: vem de `matches`.
3. Video não armazena eventos técnicos: vem de `scout`. Sincroniza por timecode.
4. Video não computa métricas: `analytics` consome clipping e computa.

## Ciclo de vida (simplificado)

```
MatchMediaSession
├── DRAFT (configuração de captura)
├── CAPTURING (ao vivo)
├── SYNCING (sincronização com scout/tracking)
├── TRANSCODING (processamento de perfis)
└── PUBLISHED (distribuição pronta)
```

Reference visual: `docs/guias/video.md` (visão conceitual de 4 blocos: capture edge, live media core, semantic sync, distribution fabric)
