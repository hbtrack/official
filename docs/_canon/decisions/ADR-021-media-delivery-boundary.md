# ADR-021: Media Delivery Boundary

- Status: Accepted
- Date: 2026-03-16
- Deciders: Arquiteto HB Track
- Tags: architecture, exercises, media, asset-delivery, domain-boundary
- Context module: exercises (aplicável a todos os módulos com assets de mídia)

---

## Context

O módulo `exercises` contém atributos como `thumbnailUrl`, e futuramente referências a vídeos, diagramas, animações e PDFs pedagógicos. Existe risco de erosão de boundaries: à medida que a implementação avança, desenvolvedores podem começar a armazenar URLs transitórias, binários, metadados de CDN e identificadores de transcodificação diretamente no objeto `Exercise`, transformando um objeto de domínio semântico em uma pasta disfarçada de assets.

Este ADR foi emitido para tornar explícita e vinculante a separação entre domínio pedagógico e entrega de mídia, antes que a implementação avance e crie acoplamento difícil de desfazer.

---

## Decision

### Regra 1 — `Exercise` é soberano apenas sobre metadados pedagógicos

O objeto `Exercise` (e `ExerciseVersion`) contém exclusivamente:
- Atributos pedagógicos e operacionais (classificação, relações, objetivos, fases, carga, complexidade)
- Referências a assets de mídia por **identificador ou URL estável** — nunca binário, nunca URL transitória, nunca metadado de CDN

O objeto `Exercise` **nunca** contém:
- Binários de arquivo (vídeo, imagem, PDF)
- URLs presigned ou transitórias com TTL
- Metadados de transcodificação (bitrate, codec, resolução, formato de container)
- Identificadores internos de storage (S3 key, GCS blob, Cloudinary public_id)
- Status de processamento de mídia (uploading, transcoding, failed)

### Regra 2 — Todo asset é uma representação derivada do exercício, não sua essência

Um exercício existe independentemente de qualquer asset de mídia. Um exercício sem vídeo é um exercício completo. Um vídeo sem exercício é um asset órfão sem valor de domínio.

Consequência: a exclusão, substituição ou falha de um asset de mídia **nunca invalida** o objeto Exercise. O exercício permanece disponível e utilizável.

### Regra 3 — Tipos de asset devem ser explícitos e tipados

Toda referência de mídia associada a um exercício deve ter tipo explícito:

| Tipo | Uso |
|---|---|
| `thumbnail` | Preview estático na listagem (DR-EXB-008) |
| `short_clip` | Vídeo curto para visualização rápida no mobile |
| `full_video` | Vídeo completo de demonstração |
| `diagram` | Diagrama tático estático |
| `animation` | Animação tática interativa |
| `pdf` | Instrução impressa / material de apoio |

A entidade `ExerciseAsset` (Fase 2) representará estas referências. Em Fase 1, `thumbnailUrl` é a única referência direta permitida no `Exercise`.

### Regra 4 — A camada de entrega de mídia pode mudar sem afetar o contrato de domínio

O provedor de CDN, o serviço de transcodificação, o bucket de storage e os formatos de entrega são decisões operacionais que podem mudar a qualquer momento. O contrato do domínio `exercises` deve permanecer estável independentemente dessas mudanças.

Implementações que tornam o backend de storage insubstituível sem alterar o schema de `Exercise` violam este ADR.

### Regra 5 — Este ADR é critério de revisão de contrato

Toda mudança em `contracts/openapi/components/schemas/exercises/` e `contracts/schemas/exercises/` deve verificar:
- O exercício está adquirindo campos de entrega de mídia? → **BLOQUEADO**

Toda mudança na camada de asset delivery deve verificar:
- O contrato de domínio foi alterado? → **BLOQUEADO**

---

## Consequences

**Positivo:**
- Backend de storage e CDN são substituíveis sem retrabalho de domínio
- Frontend recebe URLs estáveis via camada de asset delivery; não depende de schema de Exercise para URLs
- `Exercise` permanece um objeto semântico coeso e testável independentemente de infraestrutura de mídia
- Múltiplas representações do mesmo exercício (clip curto, vídeo completo, diagrama) são suportadas sem poluir o objeto principal

**Negativo / Trade-off:**
- Adiciona uma camada de indireção para acesso a assets (buscar exercise → resolver asset_id → buscar URL via asset service)
- Fase 1 simplifica com `thumbnailUrl` direto — este é um trade-off explícito e temporário

---

## Compliance

- `contracts/openapi/components/schemas/exercises/exercise.yaml` — `thumbnailUrl` é a única referência de mídia direta. Fase 1 aceita.
- `contracts/schemas/exercises/exercise.schema.json` — idem.
- `docs/hbtrack/modulos/exercises/MODULE_SCOPE_EXERCISES.md` — "Delivery de assets de mídia: exercício referencia `asset_id` / URL; não armazena binário."

---

## Related

- ADR-018: HYBRID Persistence Pattern
- TRAIN-DEC-047: `exercises` é módulo soberano; `training` não embute exercício
- TRAIN-DEC-048: Versionamento pedagógico — `ExerciseVersion` armazena metadados, não assets
- MODULE_SCOPE_EXERCISES.md — Fora do escopo: "Delivery de assets de mídia"