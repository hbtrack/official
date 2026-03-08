# EVENTS_<MODULE>.md — Eventos Canônicos do Módulo <MODULE>

Status: DRAFT_NORMATIVO
Versão: v0.1.0
Tipo de Documento: SSOT Normativo — Domain Events
Módulo: <MODULE>
Autoridade: NORMATIVO_TECNICO

## 0) Objetivo

Definir os eventos canônicos do módulo `<MODULE>` para:

- rastreabilidade temporal do domínio
- analytics derivados por projeção
- auditoria funcional
- integração futura com IA/recomendações
- reprocessamento histórico

Regras:
- Evento de domínio NÃO é log técnico.
- Evento de domínio representa fato de negócio já aceito pelo sistema.
- Eventos são imutáveis.
- Alteração de schema de evento exige `event_version` novo.

---

## 1) Aggregate Root Canônico

Aggregate root principal do módulo:

`<AGGREGATE_ROOT>`

Regras:
- Todo evento DEVE declarar `aggregate_type` e `aggregate_id`.
- O aggregate root deve ser estável e semanticamente central ao módulo.
- Eventos auxiliares podem existir, mas o módulo deve ter um root primário.

Exemplos:
- TRAINING → `training_session`
- PLAYBOOK → `play`
- COMPETITIONS → `match`

---

## 2) Convenções

Campos canônicos mínimos de todo evento:

- `event_id: uuid`
- `event_type: string`
- `event_version: int`
- `aggregate_type: string`
- `aggregate_id: uuid|string`
- `occurred_at: iso8601`
- `actor_user_id: uuid|null`
- `payload: json object`

Campos opcionais:

- `team_id`
- `org_id`
- `correlation_id`
- `causation_id`
- `source_module`
- `trace_id`

Regras:
- `payload` deve conter apenas dados necessários para reprocessamento funcional.
- Não incluir dados efêmeros de UI.
- Não usar nomes ambíguos como `updated_data`, `misc`, `metadata` sem schema.

---

## 3) Catálogo de Eventos

### EVT-<MODULE>-001 — <event_name>

Status: NORMATIVO
Event Type:
`<event_name>`

Aggregate:
`<aggregate_type>`

Trigger:
`<service_method_or_command>`

Descrição:
<descrever fato de negócio>

Precondições:
- <item>
- <item>

Payload mínimo:
- `<field_1>: <type>`
- `<field_2>: <type>`

Campos opcionais:
- `<field_x>: <type>`

Emissão:
- síncrona | assíncrona

Garantias:
- emitido somente após persistência do estado principal
- não pode ser emitido em caso de rollback

Consumidores previstos:
- projections
- analytics
- auditoria
- IA futura

---

### EVT-<MODULE>-002 — <event_name_2>

Status: NORMATIVO
Event Type:
`<event_name_2>`

Aggregate:
`<aggregate_type>`

Trigger:
`<service_method_or_command>`

Descrição:
<descrever fato de negócio>

Payload mínimo:
- `<field_1>: <type>`
- `<field_2>: <type>`

Emissão:
- síncrona | assíncrona

---

## 4) Regras de Versionamento

- Mudança backward-compatible no payload pode manter `event_version`.
- Mudança semântica ou estrutural incompatível DEVE gerar novo `event_version`.
- Nunca reutilizar significado de `event_type`.
- Se a semântica mudar, criar novo evento ou nova versão explícita.

---

## 5) Regras de Persistência

- Eventos DEVEM ser persistidos em `event_store`.
- Persistência do evento deve ocorrer na mesma transação lógica do fato de domínio, quando aplicável.
- Se a arquitetura não permitir mesma transação física, deve existir estratégia explícita de consistência (ex.: outbox).

---

## 6) Relação com Contrato / Fluxos / Invariantes

Cada evento deve rastrear:

- comando/origem
- contrato impactado
- fluxo impactado
- invariantes relacionadas

Exemplo:
- `play_copied`
  - contrato: `POST /plays/{play_id}/copy`
  - fluxo: `PLB-08`
  - invariantes: `INV-PLB-COPY-001`

---

## 7) Critérios de aceite

- todos os eventos canônicos do módulo estão nomeados
- aggregate root está explícito
- payload mínimo de cada evento está definido
- versionamento está definido
- projeções consumidoras principais estão identificadas

---