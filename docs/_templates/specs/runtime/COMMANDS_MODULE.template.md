# COMMANDS_<MODULE>.md — Catálogo de Comandos do Módulo <MODULE>

Status: DRAFT_NORMATIVO
Versão: v0.1.0
Tipo de Documento: SSOT Normativo — Domain Commands
Módulo: <MODULE>
Autoridade: NORMATIVO_TECNICO

## 0) Objetivo

Definir os comandos canônicos do módulo `<MODULE>`.

Regra:
- comando representa intenção do domínio
- comando NÃO é evento
- comando pode falhar; evento representa fato aceito

---

## 1) Catálogo de Comandos

### CMD-<MODULE>-001 — <command_name>

Status: NORMATIVO
Command Name:
`<command_name>`

Descrição:
<intenção de negócio>

Trigger técnico:
- endpoint: `<METHOD /path>`
- service: `<service_method>`

Entradas:
- `<field_1>: <type>`
- `<field_2>: <type>`

Pré-condições:
- <item>
- <item>

Pós-condições esperadas:
- <estado alterado>
- evento(s) emitido(s): `<event_name>`

Falhas esperadas:
- `<domain_error_code>`

---

## 2) Critérios de aceite

- cada comando crítico do módulo está mapeado
- cada comando aponta para evento(s) esperados
- entradas e pré-condições estão explícitas
