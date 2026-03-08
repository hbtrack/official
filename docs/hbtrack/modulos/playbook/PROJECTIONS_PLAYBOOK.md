PROJECTIONS_PLAYBOOK.md — versão inicial

# PROJECTIONS_PLAYBOOK.md — Projeções Canônicas do Módulo PLAYBOOK

Status: DRAFT_NORMATIVO
Versão: v0.1.0
Tipo de Documento: SSOT Normativo — Projections / Read Models
Módulo: PLAYBOOK
Autoridade: NORMATIVO_TECNICO

## 1) Catálogo de Projeções

### PRJ-PLB-001 — play_catalog_projection

Objetivo:
Responder catálogo de jogadas visíveis por time.

Source Events:
- play_created
- play_published
- play_copied

Grão:
- 1 linha por play

Campos:
- play_id
- playbook_id
- team_id
- title
- version
- is_published
- source_play_id
- source_team_id

Refresh Mode:
async

Consistency Model:
eventual

Storage Target:
table

### PRJ-PLB-002 — play_lineage_projection

Objetivo:
Rastrear origem e cópias entre times.

Source Events:
- play_copied

Grão:
- 1 linha por relação source→target

Campos:
- source_play_id
- source_team_id
- target_play_id
- target_team_id
- copied_at
- copied_by

Refresh Mode:
async

Consistency Model:
eventual

Storage Target:
table

### PRJ-PLB-003 — play_usage_projection

Objetivo:
Medir uso de jogadas em treino e feedback.

Source Events:
- play_attached_to_training
- play_attached_to_feedback

Grão:
- 1 linha por play_id

Campos:
- play_id
- training_attachment_count
- feedback_attachment_count
- last_attached_at

Refresh Mode:
async

Consistency Model:
eventual

Storage Target:
table
