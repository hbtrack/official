# ERRORS_<MODULE>.md — Catálogo de Erros do Módulo <MODULE>

Status: DRAFT_NORMATIVO
Versão: v0.1.0
Tipo de Documento: SSOT Normativo — Domain Errors
Módulo: <MODULE>
Autoridade: NORMATIVO_TECNICO

## 0) Objetivo

Definir erros canônicos do domínio para o módulo `<MODULE>`.

Regra:
- erro de domínio não é stack trace
- erro deve ser semanticamente estável
- erro deve ser rastreável a invariantes/comandos/contratos

---

## 1) Catálogo de Erros

### ERR-<MODULE>-001 — <error_code>

Status: NORMATIVO
Error Code:
`<error_code>`

HTTP sugerido:
`422|409|403|404|500`

Descrição:
<significado do erro>

Origem provável:
- comando: `<command_name>`
- invariante: `<INV-ID>`
- contrato: `<CONTRACT-ID ou endpoint>`

Payload mínimo sugerido:
- `code`
- `message`
- `details`

Mensagem UX sugerida:
`<mensagem legível>`

---

## 2) Critérios de aceite

- erros críticos do domínio estão nomeados
- cada erro tem origem normativa rastreável
- payload mínimo está definido