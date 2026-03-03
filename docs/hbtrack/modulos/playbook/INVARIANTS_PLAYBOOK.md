# INVARIANTS_PLAYBOOK.md — Invariantes do Módulo Playbook (v0.1)

Status: DRAFT (Contract-Driven)
Scope: quadra + ícones + setas (sem mídia, sem IA)

## 0) Convenções

- Coordenadas são normalizadas: x_norm/y_norm ∈ [0..1]
- order_index começa em 0
- Slots pt-BR: GOL, PE, PD, LE, LD, AC, PIV
- support_state: CHAO|AEREO

## INV-PLB-001 — FrameOrderUnique

O sistema DEVE garantir que, dentro de um play:
- order_index é único por frame.
- order_index é inteiro >= 0.

Falha: 422 FrameOrderInvalid

## INV-PLB-002 — CoordinatesNormalized

O sistema DEVE rejeitar qualquer state/annotation com:
- x_norm < 0 ou > 1
- y_norm < 0 ou > 1

Falha: 422 CoordinatesOutOfRange

## INV-PLB-003 — SlotUniquePerFrame

Para cada frame, o sistema DEVE garantir:
- Não existem dois PLAYER com o mesmo slot_id.

Falha: 422 DuplicateSlotInFrame

## INV-PLB-004 — SingleBallPerFrame

Para cada frame, o sistema DEVE garantir:
- Existe exatamente 1 state com entity_type=BALL.

Falha: 422 BallStateCardinalityError

## INV-PLB-005 — PlayerStateRequiresSlotAndSupport

Para cada state:
- se entity_type=PLAYER: slot_id e support_state são obrigatórios.
- se entity_type=BALL: slot_id e support_state devem ser null.

Falha: 422 InvalidEntityState

## INV-PLB-006 — SixMeterRuleWithAerial

Definições:
- “Área de 6m” é uma função determinística de (x_norm, y_norm) definida no backend (p.ex. máscara/geom canônica).
- “Com bola” é has_ball=true (ou ball_owner_slot_id=slot_id, se esse modelo for adotado).

Regras:
A) PLAYER != GOL com bola e support_state=CHAO NÃO PODE estar na área de 6m.
B) PLAYER != GOL com bola e support_state=AEREO PODE estar sobre a área de 6m.

Falha: 422 SixMeterViolation

Nota v0.1:
- Não valida sequência de aterrissagem. Isso é v0.2+.

## INV-PLB-ACL-001 — TeamOwnerImmutable

Para Playbook e Play:
- team_id é obrigatório e imutável após criação.

Falha: 409 TeamOwnerImmutableViolation

## INV-PLB-COPY-001 — CopyOnShareDeepCopy

Operação copy:
- DEVE criar um novo Play com team_id=target_team_id.
- DEVE preencher source_play_id e source_team_id.
- DEVE copiar frames + states + annotations.
- DEVE setar version=1 e is_published=false no destino.

Falha: 500 CopyOperationError (infra) ou 422 CopyValidationError (input)

## INV-PLB-ATT-001 — AttachmentIsStable

Ao anexar play em treino/feedback:
- O attachment DEVE guardar play_id + play_version (ou snapshot_json).
- O attachment DEVE permanecer válido mesmo se o play original for editado depois.

Falha: 409 AttachmentStabilityViolation