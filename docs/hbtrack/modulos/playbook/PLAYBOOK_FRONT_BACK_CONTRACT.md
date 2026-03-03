# PLAYBOOK_FRONT_BACK_CONTRACT.md — Playbook Animado (v0.1)

Status: DRAFT (Contract-Driven)
Authority: Backend + OpenAPI (SSOT runtime)
Scope: Playbook v1 = quadra + ícones + setas (sem mídia, sem IA)

## 0) Objetivo

Permitir que treinadores criem e publiquem jogadas animadas por frames (keyframes) para o time, e atletas estudem via player (read-only).
Modelo de compartilhamento entre times: Copy-on-share (Modelo 2A).

## 1) Princípios de Contrato

1. TEAM é owner direto:
- Todo Playbook e Play possuem team_id obrigatório.
- team_id é imutável após criação (muda apenas via COPY, criando um novo objeto).

2. Play é versionado:
- version inicia em 1.
- Edição de conteúdo (frames/states/annotations) incrementa version (v0.1: pode ser incrementado no PATCH do play ou no publish; decisão de implementação, mas o valor deve existir).

3. Snapshot ao anexar (treino/feedback):
- Anexos armazenam play_id + play_version (ou snapshot_json imutável) para rastreabilidade.

4. Coordenadas normalizadas:
- Todas as coordenadas são x_norm/y_norm em [0..1] (inclusive).
- UI converte para escala 40x20 para render.

5. Slots (posições) persistidos como enum pt-BR:
- GOL, PE, PD, LE, LD, AC, PIV

6. Jogada aérea:
- support_state define CHAO|AEREO para PLAYER. Evita falso positivo na área 6m.

## 2) Entidades e Shapes (DTOs)

### 2.1 Enums

PlayCategory:
- ATAQUE | DEFESA | TRANSICAO | BOLA_PARADA

VisibilityMode:
- TEAM_ONLY | RESTRICTED

EntityType:
- PLAYER | BALL

SlotId (pt-BR):
- GOL | PE | PD | LE | LD | AC | PIV

SupportState:
- CHAO | AEREO

AnnotationKind:
- MOVE | PASS | DRIBBLE | SHOT | BLOCK | SCREEN

LineType:
- SOLID | DASHED | ZIGZAG

### 2.2 DTOs

PlaybookDTO:
- id: uuid
- team_id: uuid
- title: string
- category: PlayCategory
- visibility_mode: VisibilityMode
- created_by_user_id: uuid
- created_at: iso8601
- updated_at: iso8601

PlayDTO (summary):
- id: uuid
- playbook_id: uuid
- team_id: uuid
- title: string
- description?: string
- version: int
- is_published: bool
- source_play_id?: uuid
- source_team_id?: uuid
- created_by_user_id: uuid
- created_at: iso8601
- updated_at: iso8601

FrameDTO:
- id: uuid
- play_id: uuid
- order_index: int (start=0)
- duration_ms: int (>= 0)
- coach_note?: string

FrameStateDTO:
- id: uuid
- frame_id: uuid
- entity_type: EntityType
- slot_id?: SlotId (required when entity_type=PLAYER, null when BALL)
- x_norm: number (0..1)
- y_norm: number (0..1)
- support_state?: SupportState (required when entity_type=PLAYER, null when BALL)
- has_ball?: bool (valid only for PLAYER)
- ball_owner_slot_id?: SlotId (optional alternative; v0.1 choose ONE and document in OpenAPI)

FrameAnnotationDTO:
- id: uuid
- frame_id: uuid
- kind: AnnotationKind
- line_type: LineType
- from_slot_id?: SlotId
- to_slot_id?: SlotId
- from_x_norm?: number
- from_y_norm?: number
- to_x_norm?: number
- to_y_norm?: number
- label?: string

PlayDetailDTO:
- play: PlayDTO
- playbook: PlaybookDTO
- frames: FrameDTO[]
- states_by_frame: { [frame_id: uuid]: FrameStateDTO[] }
- annotations_by_frame: { [frame_id: uuid]: FrameAnnotationDTO[] }

## 3) Endpoints (v0.1)

Base path sugerido: /api/playbook (ou /api/playbooks). Definir em OpenAPI e manter canônico.

### 3.1 Playbooks

POST /playbooks
- body: { team_id, title, category, visibility_mode }
- 201: PlaybookDTO
- Errors:
  - 403 RBAC
  - 422 validation

GET /playbooks?team_id=...
- 200: PlaybookDTO[] (somente visíveis ao caller)

PATCH /playbooks/{playbook_id}
- body: { title?, category?, visibility_mode? }
- 200: PlaybookDTO
- Rules:
  - team_id imutável

DELETE /playbooks/{playbook_id}
- v0.1: soft-delete recomendado (seguir padrão do projeto)

### 3.2 Plays

POST /plays
- body: { playbook_id, team_id, title, description? }
- 201: PlayDTO (version=1, is_published=false)

GET /plays/{play_id}
- 200: PlayDetailDTO
- Rules:
  - Must enforce visibility_mode + ACL + membership

PATCH /plays/{play_id}
- body: { title?, description? }
- 200: PlayDTO

POST /plays/{play_id}/publish
- body: {}
- 200: PlayDTO (is_published=true)

POST /plays/{play_id}/copy
- body: { target_team_id, target_playbook_id?, copy_mode="DEEP_COPY" }
- 201: PlayDTO (new play_id, team_id=target_team_id, source_play_id filled, version=1)
- Copy behavior:
  - Copies all frames + states + annotations
  - Resets is_published=false on target by default (coach publishes explicitly)

### 3.3 Frames / States / Annotations (determinísticas)

POST /plays/{play_id}/frames
- body: { order_index, duration_ms, coach_note? }
- 201: FrameDTO

PATCH /frames/{frame_id}
- body: { duration_ms?, coach_note?, order_index? }
- 200: FrameDTO
- Rule:
  - order_index must remain unique per play

PUT /frames/{frame_id}/states
- body: FrameStateDTO[] (payload completo para o frame)
- 200: { frame_id, count }
- Determinism:
  - substitui 100% o estado do frame (delete+insert transacional)
- Validation:
  - exactly one BALL per frame
  - unique slot_id among PLAYER states

PUT /frames/{frame_id}/annotations
- body: FrameAnnotationDTO[]
- 200: { frame_id, count }
- Determinism:
  - substitui 100% annotations do frame

## 4) ACL e RBAC (v0.1)

v0.1 mínimo:
- Caller MUST be membro do team_id para ver TEAM_ONLY
- RESTRICTED exige ACL explícita ou creator_id

Capabilities sugeridas:
- playbook.create
- playbook.edit_own
- playbook.edit_any_team
- playbook.manage_acl
- playbook.publish_team
- playbook.copy_to_team
- playbook.view_team_catalog
- playbook.view_assigned

## 5) Attachments (v0.1 recomendado)

POST /training-sessions/{session_id}/attachments/plays
- body: { play_id, play_version }  (ou snapshot_json)
- 201: attachment_id

POST /athlete-feedback/{feedback_id}/attachments/plays
- body: { play_id, play_version }
- 201: attachment_id

Rule:
- Attachment MUST remain valid even if play changes later.

## 6) NFRs mínimos

- Payload leve (JSON), sem mídia.
- Render instantâneo em rede instável.
- Operações PUT determinísticas para estados/annotations.