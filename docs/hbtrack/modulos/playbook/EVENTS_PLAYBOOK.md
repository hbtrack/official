EVENTS_PLAYBOOK.md — versão inicial

# EVENTS_PLAYBOOK.md — Eventos Canônicos do Módulo PLAYBOOK

Status: DRAFT_NORMATIVO
Versão: v0.1.0
Tipo de Documento: SSOT Normativo — Domain Events
Módulo: PLAYBOOK
Autoridade: NORMATIVO_TECNICO

## 0) Objetivo

Definir os eventos canônicos do módulo PLAYBOOK para rastreabilidade temporal, analytics, lineage, uso em treino/feedback e evolução futura do player/editor.

## 1) Aggregate Root Canônico

Aggregate root principal do módulo:

`play`

Aggregate secundário:
`playbook`

## 2) Convenções

Campos mínimos:
- event_id
- event_type
- event_version
- aggregate_type
- aggregate_id
- occurred_at
- actor_user_id
- payload

## 3) Catálogo de Eventos

### EVT-PLB-001 — playbook_created

Aggregate:
`playbook`

Trigger:
`create_playbook`

Payload mínimo:
- playbook_id: uuid
- team_id: uuid
- title: string
- category: string
- visibility_mode: string

### EVT-PLB-002 — play_created

Aggregate:
`play`

Trigger:
`create_play`

Payload mínimo:
- play_id: uuid
- playbook_id: uuid
- team_id: uuid
- title: string
- version: int
- is_published: bool

### EVT-PLB-003 — frame_added

Aggregate:
`play`

Trigger:
`create_frame`

Payload mínimo:
- play_id: uuid
- frame_id: uuid
- order_index: int
- duration_ms: int

### EVT-PLB-004 — frame_states_replaced

Aggregate:
`play`

Trigger:
`replace_frame_states`

Payload mínimo:
- play_id: uuid
- frame_id: uuid
- state_count: int

### EVT-PLB-005 — frame_annotations_replaced

Aggregate:
`play`

Trigger:
`replace_frame_annotations`

Payload mínimo:
- play_id: uuid
- frame_id: uuid
- annotation_count: int

### EVT-PLB-006 — play_published

Aggregate:
`play`

Trigger:
`publish_play`

Payload mínimo:
- play_id: uuid
- team_id: uuid
- version: int
- published_at: iso8601

### EVT-PLB-007 — play_copied

Aggregate:
`play`

Trigger:
`copy_play`

Payload mínimo:
- source_play_id: uuid
- source_team_id: uuid
- target_play_id: uuid
- target_team_id: uuid
- target_playbook_id: uuid|null
- version: int
- is_published: bool

Relações:
- contrato: `POST /plays/{play_id}/copy`
- fluxo: `PLB-08`
- invariantes: `INV-PLB-COPY-001`

### EVT-PLB-008 — play_attached_to_training

Aggregate:
`play`

Trigger:
`attach_play_to_training_session`

Payload mínimo:
- play_id: uuid
- play_version: int
- session_id: uuid
- attachment_id: uuid

### EVT-PLB-009 — play_attached_to_feedback

Aggregate:
`play`

Trigger:
`attach_play_to_feedback`

Payload mínimo:
- play_id: uuid
- play_version: int
- feedback_id: uuid
- attachment_id: uuid
