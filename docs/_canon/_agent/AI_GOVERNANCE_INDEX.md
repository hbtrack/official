# AI_GOVERNANCE_INDEX.md

Status: CANONICAL
Version: 1.0.0
Scope: Índice central de governança de agentes e hierarquia normativa
Applies To: AI Architect + AI Executor

---

# 1. PURPOSE

Este documento centraliza todos os artefatos normativos relacionados à governança de agentes no HB Track.

Objetivos:

* Declarar hierarquia normativa
* Evitar conflitos entre documentos
* Definir precedência formal
* Garantir coerência sistêmica
* Servir como ponto único de auditoria
* Formalizar cadeia de autoridade

Este é o índice autoritativo da governança de IA no projeto.

---

# 2. NORMATIVE HIERARCHY (ORDEM DE PRECEDÊNCIA)

Em caso de conflito entre documentos, aplica-se a seguinte hierarquia:

LEVEL 0 — PROJECT CONSTITUTION

* ADRs estruturais aprovadas
* SSOT oficialmente declarado (ex: schema.sql)
* Regras de invariantes canônicas

Nível máximo. Não pode ser sobrescrito por nenhum documento inferior.

---

LEVEL 1 — CORE GOVERNANCE

1. AI_ARCH_EXEC_PROTOCOL.md
2. AI_INCIDENT_RESPONSE_POLICY.md

Define papéis, ciclo de execução e tratamento de falhas críticas.

---

LEVEL 2 — CONTROL LAYERS

3. AI_PROTOCOL_CHECKLIST.md
4. AI_TASK_VERSIONING_POLICY.md

Controla emissão e evolução de TASK.

---

LEVEL 3 — TASK-LEVEL DOCUMENTS

5. TASK BRIEF (versionado)
6. EVIDENCE PACK

Devem obedecer integralmente os níveis superiores.

---

### LEVEL 4 — EXECUTION ARTIFACTS (Human Visibility Layer)

**Autoridade SSOT:** `event.json` (Machine) | `HUMAN_SUMMARY.md` (Audit)

1. **`event.json`**: Ponte de dados determinística para automação e logs.
2. **`HUMAN_SUMMARY.md`**: Camada de visibilidade humana sobre a execução técnica.
3. **`PROOFS.md`**: Registro de integridade (SHA256) do trio de execução.
4. **`STATUS_BOARD.md`**: Painel centralizado do estado de todas as tasks.

Artefatos operacionais com prova de integridade. Obrigatórios para fechamento de task.

---

Regra fundamental:

Documento de nível inferior nunca pode sobrescrever regra de nível superior.

---

# 2.1. INTEGRATION WITH DOCUMENTATION HIERARCHY

**This governance framework integrates with the project's documentation hierarchy as follows:**

```
┌─────────────────────────────────────────────────────────────┐
│ LEVEL 0: PROJECT CONSTITUTION (Highest Authority)          │
│  ├─ ADRs (Architecture Decision Records)                    │
│  ├─ SSOT (schema.sql, openapi.json, alembic_state.txt)     │
│  ├─ Invariantes canônicas (INVARIANTS_TRAINING.md)         │
│  └─ THIS DOCUMENT (AI_GOVERNANCE_INDEX.md)                  │
└─────────────────────────────────────────────────────────────┘
                           │
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ LEVEL 1: CANONICAL DOCUMENTATION (Navigation Authority)    │
│  ├─ 00_START_HERE.md (Single Entry Point)                  │
│  ├─ 01_AUTHORITY_SSOT.md (Precedence rules)                │
│  ├─ 05_MODELS_PIPELINE.md (Validation workflows)           │
│  ├─ 08_APPROVED_COMMANDS.md (Command whitelist)            │
│  ├─ 09_TROUBLESHOOTING_GUARD_PARITY.md (Exit codes)        │
│  └─ docs/_canon/_agent/*.md (Governance protocols)         │
└─────────────────────────────────────────────────────────────┘
                           │
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ LEVEL 2: OPERATIONAL DOCUMENTATION (Execution Guidance)    │
│  ├─ docs/_ai/*.md (Prompts, protocols, guardrails)         │
│  ├─ docs/_ai/_context/*.md (Agent constraints)             │
│  ├─ docs/_ai/_specs/*.md (Formal specs)                    │
│  ├─ docs/_ai/_checklists/*.md (Validation checklists)      │
│  └─ .github/instructions/*.md (Conditional loading)        │
└─────────────────────────────────────────────────────────────┘
                           │
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ LEVEL 3: GENERATED ARTIFACTS (Evidence/SSOT State)         │
│  ├─ schema.sql (Database DDL)                              │
│  ├─ openapi.json (API contract)                            │
│  ├─ parity_report.json (Model-schema alignment)            │
│  ├─ manifest.json (Generation traceability)                │
│  └─ baseline.json (Guard state — LOCAL ONLY)               │
└─────────────────────────────────────────────────────────────┘
                           │
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ LEVEL 4: EXECUTION ARTIFACTS (Operational Logs)            │
│  ├─ Gate logs (parity, requirements, guard outputs)        │
│  ├─ EXECUTIONLOG.md (Session logs)                         │
│  ├─ CHANGELOG.md (Change history)                          │
│  └─ Test outputs (pytest, invariant validation)            │
└─────────────────────────────────────────────────────────────┘
```

**Cross-Level Precedence Rules:**

1. **LEVEL 0 overrides all:** If ADR or SSOT contradicts any lower-level document, LEVEL 0 wins.
2. **LEVEL 1 is navigation authority:** All agents MUST start at `00_START_HERE.md` before consulting operational docs.
3. **LEVEL 2 cannot create new rules:** Operational docs interpret/implement LEVEL 1 rules but cannot contradict them.
4. **LEVEL 3 is read-only truth:** Generated artifacts reflect system state; never edited manually.
5. **LEVEL 4 is evidence only:** Logs do not have normative authority.

**Integration Point:** Agents following `AI_ARCH_EXEC_PROTOCOL.md` MUST:
- Start at `docs/_canon/00_START_HERE.md` for all operational tasks
- Consult `AI_GOVERNANCE_INDEX.md` (this file) for governance decisions
- Follow hierarchy LEVEL 0 → LEVEL 1 → LEVEL 2 → LEVEL 3 in case of uncertainty

**Audit Trail:** Any conflict between levels must be escalated via `AI_INCIDENT_RESPONSE_POLICY.md` (SEV-2 or higher).

---

# 3. GOVERNANCE MAP (RESPONSABILIDADES)

AI_ARCH_EXEC_PROTOCOL.md
→ Define separação de papéis, ciclo formal e enforcement estrutural.

AI_PROTOCOL_CHECKLIST.md
→ Garante determinismo antes da emissão de qualquer TASK.

AI_TASK_VERSIONING_POLICY.md
→ Controla evolução incremental e rastreabilidade de tasks.

AI_INCIDENT_RESPONSE_POLICY.md
→ Controla falhas críticas, contenção e restauração de integridade.

---

# 4. SUPREMACY RULES

## 4.1 Protocol Supremacy

Se um TASK BRIEF conflitar com AI_ARCH_EXEC_PROTOCOL:

→ TASK é inválida.

---

## 4.2 Incident Override Rule

Durante INCIDENT SEV-1:

AI_INCIDENT_RESPONSE_POLICY assume precedência temporária sobre qualquer TASK em execução.

---

## 4.3 SSOT Supremacy

Se qualquer documento conflitar com SSOT declarado:

→ SSOT prevalece.

---

## 4.4 Version Integrity Rule

Nenhuma execução é válida sem:

* TASK versionada
* Checklist validado
* Evidence Pack completo

---

# 5. GOVERNANCE WORKFLOW (CANÔNICO)

Fluxo obrigatório:

1. Consultar AI_GOVERNANCE_INDEX
2. Validar AI_PROTOCOL_CHECKLIST
3. Emitir TASK versionada
4. Executar conforme AI_ARCH_EXEC_PROTOCOL
5. Produzir EVIDENCE PACK
6. Validar ACCEPTANCE CRITERIA
7. Declarar PASS ou FAIL
8. Se FAIL → aplicar AI_INCIDENT_RESPONSE_POLICY

Desvio desse fluxo configura violação normativa.

---

# 6. CONFLICT RESOLUTION PROCEDURE

Se dois documentos entrarem em conflito:

1. Identificar níveis hierárquicos
2. Aplicar precedência superior
3. Declarar conflito formalmente
4. Emitir nova versão do documento inferior
5. Registrar em CHANGELOG

Nenhum conflito pode permanecer implícito.

---

# 7. GOVERNANCE INTEGRITY CHECK

Toda execução de agente deve ser capaz de responder objetivamente:

* Qual regra normativa está sendo aplicada?
* Qual documento fundamenta a decisão?
* Qual versão da TASK foi usada?
* Qual foi o resultado formal (PASS/FAIL)?

Se não for possível responder → governança comprometida.

---

# 8. AMENDMENT RULE

Qualquer alteração neste índice exige:

* Incremento de versão
* Justificativa formal
* Atualização cruzada dos documentos impactados
* Registro em CHANGELOG

---

# 9. META-GOVERNANCE PRINCIPLE

Governança existe para:

* Reduzir entropia
* Impedir decisões implícitas
* Preservar integridade estrutural
* Permitir evolução controlada

Se uma regra aumentar complexidade sem reduzir risco, deve ser revisada.

---

END OF DOCUMENT
