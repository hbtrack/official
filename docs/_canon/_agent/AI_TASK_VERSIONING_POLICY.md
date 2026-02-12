# AI_TASK_VERSIONING_POLICY.md

Status: CANONICAL
Version: 1.0.0
Scope: Versionamento formal de TASK BRIEF
Applies To: AI Architect (ChatGPT) + Repo Agent (Executor)

---

# 1. PURPOSE

Estabelecer um modelo formal de versionamento para TASK BRIEF com o objetivo de:

* Eliminar retrabalho caótico
* Impedir reexecuções ambíguas
* Garantir rastreabilidade histórica
* Permitir auditoria de decisões
* Controlar escopo incremental

Toda TASK deve possuir versão explícita.

---

# 2. VERSION FORMAT

Formato obrigatório:

TASK-<IDENTIFIER>-v<MAJOR>.<MINOR>

Exemplos:

TASK-MODEL-PARITY-001-v1.0
TASK-MODEL-PARITY-001-v1.1
TASK-MODEL-PARITY-001-v2.0

A versão deve constar:

* No título do TASK BRIEF
* No corpo do TASK BRIEF
* No EVIDENCE PACK
* Em qualquer PR relacionado

---

# 3. VERSIONING RULES

## 3.1 MAJOR VERSION (v2.0, v3.0, ...)

Incrementar MAJOR quando houver:

* Mudança no GOAL
* Mudança no SSOT
* Mudança estrutural no escopo (READ/WRITE)
* Mudança de estratégia de execução
* Alteração nos ACCEPTANCE CRITERIA
* Introdução de novo risco arquitetural
* Alteração em invariantes

MAJOR implica nova abordagem ou nova hipótese estrutural.

---

## 3.2 MINOR VERSION (v1.1, v1.2, ...)

Incrementar MINOR quando houver:

* Ajuste em comandos
* Refinamento de critérios
* Correção de ambiguidade
* Inclusão de STOP CONDITION
* Ajuste de BUDGET
* Correção de erro na definição

MINOR implica refinamento da mesma estratégia.

---

# 4. IMMUTABILITY RULE

Uma versão emitida é imutável.

Proibido:

* Editar silenciosamente um TASK BRIEF já emitido
* Alterar comandos sem incremento de versão
* Modificar ACCEPTANCE CRITERIA sem versionar

Qualquer modificação exige nova versão.

---

# 5. VERSION CHANGE SUMMARY (OBRIGATÓRIO)

Toda nova versão deve conter:

## VERSION CHANGE SUMMARY

Previous Version:
Version Type: MAJOR | MINOR
Reason for Increment:
Root Cause (se aplicável):
Changes Introduced:
Impact Surface:

Sem essa seção → versão inválida.

---

# 6. EXECUTION RULE

Executor deve declarar no EVIDENCE PACK:

TASK VERSION: <ID-vX.Y>

Se a versão executada não corresponder à última versão aprovada:

→ Execução inválida
→ STOP obrigatório

---

# 7. FAILURE ITERATION MODEL

Se STATUS FINAL = FAIL:

1. Architect analisa EVIDENCE PACK
2. Identifica causa raiz
3. Emite nova versão
4. Incremento deve ser justificado

Proibido:

* Reexecutar mesma versão esperando resultado diferente
* Alterar task informalmente
* Mudar escopo sem registrar

---

# 8. VERSIONING MATRIX

| Tipo de Mudança                         | Incremento |
| --------------------------------------- | ---------- |
| Ajuste de comando                       | MINOR      |
| Refinamento de critério                 | MINOR      |
| Correção textual sem impacto estrutural | MINOR      |
| Mudança de meta                         | MAJOR      |
| Mudança de SSOT                         | MAJOR      |
| Mudança de escopo READ/WRITE            | MAJOR      |
| Mudança de estratégia                   | MAJOR      |
| Novo risco estrutural                   | MAJOR      |
| Alteração de invariantes                | MAJOR      |

---

# 9. ARCHITECT DECLARATION (OBRIGATÓRIO)

Ao emitir nova versão, declarar explicitamente:

"TASK <ID> atualizada para vX.Y. Justificativa registrada conforme política de versionamento."

Sem essa declaração → versão inválida.

---

# 10. TRACEABILITY REQUIREMENT

Toda execução deve permitir responder objetivamente:

* Qual versão foi executada?
* Por que ela foi criada?
* O que mudou da versão anterior?
* Qual foi o resultado (PASS/FAIL)?

Se não for possível responder essas quatro perguntas → política foi violada.

---

# 11. RETRABALHO CAÓTICO (DEFINIÇÃO FORMAL)

Configura retrabalho caótico quando:

* Mesada versão é reexecutada após FAIL
* Escopo muda sem incremento MAJOR
* Critério muda sem incremento de versão
* Executor recebe instrução fora do TASK BRIEF

Quando detectado:

* Execução deve ser interrompida
* Nova versão deve ser emitida
* Incidente deve ser registrado

---

# 12. ENFORCEMENT

Se qualquer agente violar esta política:

* Execução é inválida
* Nova versão deve ser emitida
* Registro obrigatório em CHANGELOG

Este documento é obrigatório para qualquer evolução de TASK no HB Track.

---

END OF DOCUMENT
