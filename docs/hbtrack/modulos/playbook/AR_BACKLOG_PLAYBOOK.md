# AR_BACKLOG_PLAYBOOK.md — Backlog (Playbook Animado) — v0.1

Status: DRAFT
Modelo: TEAM-owner + Copy-on-share (Deep copy)
Escopo v1: quadra + ícones + setas (sem mídia, sem IA)

## Batches

Batch 1 — BE Core (Schema + Services + OpenAPI)
Batch 2 — FE Player (read-only)
Batch 3 — FE Editor (drag/drop + frames + annotations)
Batch 4 — Copy UX (copy-on-share)

---

## Batch 1 — BE Core

| AR-ID | Prio | Título | Entrega | Depende | Status |
|------:|:----:|--------|---------|---------|:------:|
| AR-PLB-001 | ALTA | Schema: playbooks/plays/frames/states/annotations | schema.sql + alembic_state | — | PENDENTE |
| AR-PLB-002 | ALTA | Models/Services: CRUD Playbook/Play/Frame | BE services + guards | AR-PLB-001 | PENDENTE |
| AR-PLB-003 | ALTA | Endpoints: CRUD + GET detail | OpenAPI canônico | AR-PLB-002 | PENDENTE |
| AR-PLB-004 | ALTA | PUT determinístico states/annotations | replace-all transacional | AR-PLB-003 | PENDENTE |
| AR-PLB-005 | ALTA | Copy-on-share (deep copy) + lineage | /plays/{id}/copy | AR-PLB-004 | PENDENTE |
| AR-PLB-006 | MÉDIA | Attachments (treino/feedback) com play_version | endpoints + schema | AR-PLB-005 | PENDENTE |
| AR-PLB-007 | ALTA | Invariantes (INV-PLB-001..006, ACL, COPY, ATT) + testes | pytest | AR-PLB-006 | PENDENTE |

DoD Batch 1:
- OpenAPI SSOT regenerado.
- Testes PASS cobrindo invariantes mínimas.
- Copy-on-share cria novo play com version=1 e is_published=false.

---

## Batch 2 — FE Player

| AR-ID | Prio | Título | Entrega | Depende | Status |
|------:|:----:|--------|---------|---------|:------:|
| AR-PLB-008 | ALTA | UI Player: render quadra + slots + bola | tela player | Batch 1 | PENDENTE |
| AR-PLB-009 | ALTA | Timeline frames: play/pause/step | controles + keyframes | AR-PLB-008 | PENDENTE |
| AR-PLB-010 | MÉDIA | Exibir annotations (setas/linhas) | overlay layer | AR-PLB-009 | PENDENTE |

DoD Batch 2:
- Player funciona em rede instável (payload JSON leve).
- Não existe modo de edição no player.

---

## Batch 3 — FE Editor

| AR-ID | Prio | Título | Entrega | Depende | Status |
|------:|:----:|--------|---------|---------|:------:|
| AR-PLB-011 | ALTA | Editor: criar/editar play e frames | UI editor | Batch 2 | PENDENTE |
| AR-PLB-012 | ALTA | Drag/drop slots + bola por frame | states editor | AR-PLB-011 | PENDENTE |
| AR-PLB-013 | ALTA | Editor annotations (MOVE/PASS/DRIBBLE + line_type) | overlay editor | AR-PLB-012 | PENDENTE |
| AR-PLB-014 | MÉDIA | Publish/visibility_mode no FE | publish flow | AR-PLB-013 | PENDENTE |

DoD Batch 3:
- Salvar usa PUT replace-all (states/annotations).
- Validations de invariantes aparecem como erro UX claro (422).

---

## Batch 4 — Copy UX

| AR-ID | Prio | Título | Entrega | Depende | Status |
|------:|:----:|--------|---------|---------|:------:|
| AR-PLB-015 | ALTA | UI: copiar jogada para outro time | modal copy | Batch 3 | PENDENTE |
| AR-PLB-016 | MÉDIA | Exibir lineage (copied from) | info | AR-PLB-015 | PENDENTE |

DoD Batch 4:
- Copy cria novo play no team destino, não altera o original.