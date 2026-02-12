# AI_INCIDENT_RESPONSE_POLICY.md

Status: CANONICAL
Version: 1.0.0
Scope: Tratamento formal de incidentes críticos envolvendo Gates, SSOT, Parity e Invariantes
Applies To: AI Architect (ChatGPT) + Repo Agent (Executor)

---

# 1. PURPOSE

Estabelecer um protocolo estruturado para identificação, contenção, análise e resolução de falhas graves no HB Track.

Este documento cobre incidentes como:

* Gate quebrado (parity, guard, requirements)
* SSOT corrompido ou inconsistente
* Divergência Model ↔ DB pós-migration
* Invariantes violados
* Regressão estrutural após PASS anterior
* Falha sistêmica após execução automatizada

Objetivos:

* Conter impacto imediatamente
* Preservar rastreabilidade
* Impedir agravamento
* Restaurar estado íntegro
* Formalizar causa raiz
* Endurecer o sistema pós-incidente

---

# 2. INCIDENT CLASSIFICATION

## SEVERITY LEVELS

SEV-1 (CRITICAL)

* Corrupção de SSOT
* structural_diff_count > 0 após merge aprovado
* Migration aplicada com divergência estrutural
* Violação de invariantes críticos
* Gate regressivo em branch principal

Impacto: Integridade estrutural comprometida.

---

SEV-2 (HIGH)

* Gate falhando consistentemente
* Requirements violation em módulo core
* Guard violation inesperada
* Divergência entre ambientes

Impacto: Estabilidade ameaçada.

---

SEV-3 (MEDIUM)

* Falha isolada de task
* Divergência local sem merge
* Erro controlado e reversível

Impacto: Limitado ao escopo local.

---

# 3. INCIDENT LIFECYCLE (OBRIGATÓRIO)

Todo incidente deve seguir 6 fases formais:

1. Detection
2. Containment
3. Evidence Capture
4. Root Cause Analysis
5. Remediation
6. Post-Incident Hardening

Nenhuma fase pode ser omitida.

---

# 4. DETECTION RULE

Incidente deve ser declarado quando ocorrer qualquer um:

* EXIT != esperado
* structural_diff_count > 0 inesperado
* SSOT modificado sem versionamento
* Gate regressivo após PASS anterior
* Invariantes falhando em ambiente validado

Declaração obrigatória:

"INCIDENT DECLARED: <INCIDENT-ID> | Severity: SEV-X"

Sem declaração formal → não é incidente válido.

---

# 5. CONTAINMENT PROTOCOL

Após declaração:

1. Suspender novas TASKs relacionadas
2. Bloquear merges no branch afetado
3. Proibir autogen automático
4. Capturar estado atual (git status + HEAD SHA)
5. Registrar ambiente (branch, commit, timestamp)

Proibido:

* Corrigir antes de capturar evidência
* Alterar SSOT durante contenção

---

# 6. EVIDENCE CAPTURE (OBRIGATÓRIO)

Registrar no momento do incidente:

* Commit SHA
* Branch
* Exit codes
* structural_diff_count
* parity_report.json
* requirements_report.json (se aplicável)
* stdout completo do gate
* Lista de arquivos modificados
* Última TASK VERSION executada

Sem evidence capture completo → análise inválida.

---

# 7. ROOT CAUSE ANALYSIS (RCA)

RCA deve responder objetivamente:

1. O que mudou?
2. Quando mudou?
3. Qual versão da TASK introduziu?
4. Qual regra do protocolo foi violada?
5. Era prevenível pelo checklist?
6. Houve falha humana ou sistêmica?

Classificação formal da causa:

* TASK mal definida
* Executor fora de escopo
* SSOT inconsistente
* Migration incorreta
* Script defeituoso
* Falha humana
* Falha de governança

RCA deve ser documentada.

---

# 8. REMEDIATION RULES

Remediação deve seguir ordem estrita:

1. Restaurar estado íntegro (rollback se necessário)
2. Revalidar todos os gates
3. Emitir nova TASK versionada (se aplicável)
4. Ajustar protocolo se falha foi estrutural

Proibido:

* Aplicar correção silenciosa
* Alterar SSOT sem versionamento
* Reexecutar mesma versão esperando resultado diferente

---

# 9. SSOT CORRUPTION PROTOCOL

Se SSOT estiver inconsistente:

1. Confirmar fonte correta
2. Identificar último commit íntegro
3. Restaurar via commit verificado
4. Reexecutar parity e requirements
5. Validar structural_diff_count = 0

Qualquer alteração em SSOT exige:

* Incremento MAJOR em TASK
* Registro em CHANGELOG
* Justificativa formal

---

# 10. PARITY DIVERGENCE PÓS-MIGRATION

Se após migration aplicada:

structural_diff_count > 0

Procedimento obrigatório:

1. Confirmar migration aplicada = head
2. Gerar novo schema.sql via dump
3. Comparar com modelo atual
4. Identificar lado incorreto (Model ou Migration)
5. Nunca ajustar ambos simultaneamente

Correção deve ser única e versionada.

---

# 11. INCIDENT REPORT TEMPLATE

Todo incidente deve gerar relatório:

---

## INCIDENT REPORT

Incident ID:
Severity:
Detected By:
Timestamp:

Trigger Condition:

Impact Surface:

Evidence Summary:

Root Cause:

Remediation Applied:

Preventive Action:

Protocol Change Required? YES | NO

Linked TASK Versions:

---

Sem relatório → incidente não encerrado.

---

# 12. HARDENING PHASE

Após resolução:

* Atualizar AI_PROTOCOL_CHECKLIST se necessário
* Atualizar AI_TASK_VERSIONING_POLICY se aplicável
* Adicionar nova STOP CONDITION se recorrente
* Documentar aprendizado no CHANGELOG
* Avaliar necessidade de nova ADR

Objetivo: reduzir probabilidade de reincidência.

---

# 13. INCIDENT CLOSURE RULE

Incidente só pode ser fechado quando:

* structural_diff_count = 0
* Gates retornam EXIT esperado
* SSOT validado
* Relatório preenchido
* Architect declara formalmente encerrado

Declaração obrigatória:

"INCIDENT <ID> CLOSED. Sistema restaurado à integridade estrutural."

---

# 14. ENFORCEMENT

Se qualquer agente:

* Ignorar fase de contenção
* Alterar estado antes de capturar evidência
* Omitir RCA
* Aplicar correção sem versionamento

→ Execução inválida
→ Incidente escalado automaticamente para SEV-1

Este documento é obrigatório para qualquer falha estrutural relevante no HB Track.

---

END OF DOCUMENT
