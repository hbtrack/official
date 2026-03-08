# PROJECTIONS_<MODULE>.md — Projeções Canônicas do Módulo <MODULE>

Status: DRAFT_NORMATIVO
Versão: v0.1.0
Tipo de Documento: SSOT Normativo — Projections / Read Models
Módulo: <MODULE>
Autoridade: NORMATIVO_TECNICO

## 0) Objetivo

Definir projeções canônicas do módulo `<MODULE>` derivadas de eventos de domínio para:

- leitura rápida
- analytics
- dashboards
- histórico agregável
- consumo por IA/recomendação

Regra:
- projeção não é fonte primária do fato
- projeção é materialização derivada
- projeção pode ser reconstruída a partir de eventos

---

## 1) Convenções

Campos mínimos por projeção:

- `projection_name`
- `source_events`
- `grain`
- `refresh_mode`
- `consistency_model`
- `storage_target`
- `rebuild_strategy`

Valores típicos:
- `refresh_mode`: sync | async | batch
- `consistency_model`: strong | eventual
- `storage_target`: table | materialized_view | cache | search_index

---

## 2) Catálogo de Projeções

### PRJ-<MODULE>-001 — <projection_name>

Status: NORMATIVO
Nome:
`<projection_name>`

Objetivo:
<descrever o que a projeção responde>

Source Events:
- `<event_type_1>`
- `<event_type_2>`

Grão:
- 1 linha por `<aggregate|team|athlete|session|play>`

Campos:
- `<field_1>`
- `<field_2>`
- `<field_3>`

Refresh Mode:
`sync|async|batch`

Consistency Model:
`strong|eventual`

Storage Target:
`table|materialized_view|cache`

Rebuild Strategy:
- full rebuild permitido? sim|não
- incremental? sim|não

Consumidores:
- endpoint `<...>`
- dashboard `<...>`
- tela `<...>`

---

### PRJ-<MODULE>-002 — <projection_name_2>

Status: NORMATIVO
Nome:
`<projection_name_2>`

Objetivo:
<descrição>

Source Events:
- `<event_type_x>`

Grão:
- 1 linha por `<...>`

Campos:
- `<...>`

Refresh Mode:
`async`

Consistency Model:
`eventual`

Storage Target:
`table`

---

## 3) Regras

- toda projeção deve apontar explicitamente para seus source events
- projeção deve poder ser reconstruída sem depender de UI
- campos derivados devem ser documentados
- projeções para analytics não devem ser usadas como fonte de verdade transacional

---

## 4) Critérios de aceite

- principais perguntas analíticas do módulo possuem projeção mapeada
- cada projeção possui source events explícitos
- grain e consistency model estão definidos
- estratégia de rebuild está definida


