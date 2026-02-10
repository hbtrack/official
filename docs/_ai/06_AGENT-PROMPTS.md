---
description: Index of workspace slash commands and prompt files for Copilot agent
---

# Agent Prompts & Slash Commands

Prompts acionáveis no Copilot Chat usando `/`. VS Code carrega automaticamente do `.github/prompts/`.

---

## 📌 Workspace Prompts (Slash Commands)

### 1. `/parity-fix` — Model↔DB Alignment

**File:** `.github/prompts/parity-fix.prompt.md`

**When to Use:**
- Detectar divergências estruturais entre SQLAlchemy models e schema.sql
- Output de `requirements scan` com status FAIL (exit=4)
- Necessário corrigir nullability, constraints, ou indexes

**Input:** 
- Tabela alvo (e.g., `categories`) ou `'next'` (auto-select próxima de maior impacto)

**Output:**
- Diagnóstico com citações de parity_report.json + schema.sql
- Patch mínimo (model ajustado)
- Comando de validação com critério de sucesso

**Quick Example:**
```
@copilot /parity-fix categories
```

Output esperado:
```
DIAGNÓSTICO: 
- schema.sql: categories.created_at NOT NULL DEFAULT CURRENT_TIMESTAMP
- model: Column('created_at', nullable=True) ← MISMATCH

PATCH:
- Remover nullable=True em created_at

VALIDAÇÃO:
$ .\scripts\models_autogen_gate.ps1 -Table categories
Expected exit: 0 (PASS)
```

---

### 2. `/models-gate` — Gate Evaluation & Fix Guidance

**File:** `.github/prompts/models-gate.prompt.md`

**When to Use:**
- Rodar ou interpretar o gate de modelos (models_autogen_gate.ps1)
- Entender status de múltiplas tabelas em lote
- Guiar qual tabela corrigir primeiro (baseado em impacto)

**Input:**
- `'scan'` — gerar/interpretar parity_report.json
- `'fix-next'` — escolher próxima tabela FAIL (maior impacto)
- `table_name` — focar em 1 tabela específica

**Output:**
- Estado atual (PASS/FAIL count)
- Próxima ação recomendada
- Comandos aprovados para validação

**Quick Example:**
```
@copilot /models-gate scan
```

Output esperado:
```
Estado: 45 PASS, 5 FAIL

Próxima: athletes (MISSING_NULLABLE, 2 cols)
Comando: $ .\scripts\models_autogen_gate.ps1 -Table athletes -Profile strict
```

---

### 3. `/install-invariant` — Training Invariant Installation

**File:** `.github/prompts/install-invariant.prompt.md`

**When to Use:**
- Adicionar nova regra de validação de training (invariante)
- Seguir protocol de SSOT + implementação + testes
- Documentar no manifesto (training_invariants_status.md)

**Input:**
- INV-ID como `INV-TRAIN-041` ou `'next'` (auto-select from candidates)

**Output:**
- SPEC escrita no SSOT (INVARIANTS_TRAINING.md)
- Código de implementação (classe/decorator)
- Testes unitários conforme canon
- Checklist PR

**Quick Example:**
```
@copilot /install-invariant INV-TRAIN-041
```

Output esperado:
```
SPEC: "Focus percentage must be between 0-100"
IMPLEMENTATION: FocusPercentageInvariant class
TESTS: test_focus_percentage_valid, test_focus_percentage_invalid
CHECKLIST: ✓ SSOT updated, ✓ Tests added, ✓ Gate passes
```

---

### 4. `/generate-exec-task` — Generate EXEC_TASK from ADR

**File:** `.github/prompts/generate-exec-task.prompt.md`

**When to Use:**
- Transformar uma ADR em plano executável (EXEC_TASK)
- Estruturar ordem de passos, pré-requisitos, gates, validação final
- Documentar checklist de PR e atualização de logs

**Input:**
- ADR file path ou identificador (e.g., `docs/ADR/013-ADR-MODELS.md`)

**Output:**
- EXEC_TASK com Fases 1-4 (prep, execute, validate, commit)
- Pré-requisitos validáveis
- Gates em cada fase
- Smoke test final
- Checklist PR

**Quick Example:**
```
@copilot /generate-exec-task 013-ADR-MODELS.md
```

Output esperado:
```
EXEC_TASK gerado em: docs/execution_tasks/EXEC_TASK_ADR_MODELS_002.md

Estrutura:
Phase 1: Prerequisites ← 5 checks
Phase 2: Execute models_autogen_gate em lote
Phase 3: Validação (requirements scan todos PASS)
Phase 4: Commit + update CHANGELOG

Duração estimada: 4-6 horas
```

---

## 🔍 Descoberta: Como Copilot Carrega Prompts

1. **VS Code busca** `.github/prompts/*.prompt.md` automaticamente
2. **Registra** no Copilot Chat como `/nome_do_prompt`
3. **Carrega contexto** (frontmatter YAML + corpo) quando você digita `/`
4. **Executa** o protocolo definido no arquivo

**Se prompts não aparecerem:**
- Validar que `.github/prompts/` tem 4 `.prompt.md` files
- Recarregar VS Code (Cmd+K Cmd+L ou restart)
- Abrir Copilot Chat e digitar `/`

---

## 📋 Quick Reference: Qual Prompt Usar Quando?

| Situação | Prompt | Entrada | Saída | Tempo |
|----------|--------|---------|-------|-------|
| "Preciso saber se modelo X bate com schema" | `/models-gate` | `table_name` | Status + next step | ~2 min |
| "Achei divergência em nullability" | `/parity-fix` | `table_name` | Patch + validation command | ~5 min |
| "Quero adicionar regra de training" | `/install-invariant` | `INV-ID` | SPEC + código + testes | ~30 min |
| "Preciso virar essa ADR num plano" | `/generate-exec-task` | `ADR path` | EXEC_TASK com Gates | ~15 min |

---

## 🚀 Operacional: Como Chamar o Agente

### Opção A: Slash Command (Recomendado)
```
@copilot /parity-fix athletes
```
✅ Copilot carrega o protocolo estruturado  
✅ Context é 100% SSOT-driven  
✅ Validação automática

### Opção B: Comando Natural (Fallback)
```
@copilot Corrija o modelo de athletes para bater com schema.sql
```
⚠️ Funciona, mas sem estrutura de protocolo  
⚠️ Menos validação de pré-requisitos

### Opção C: EXEC_TASK (Tarefas Complexas)
```
@copilot Execute docs/execution_tasks/EXEC_TASK_ADR_MODELS_001.md
```
✅ Ordem estrita, tudo documentado  
✅ Gates em cada fase  
✅ Rollback claro se falhar

---

## 📌 Exemplos de Integração

**Cenário 1: Fix one table**
```
You: @copilot /parity-fix categories
Agent: [reads parity_report.json, schema.sql, app/models/category.py]
       Diagnostics + patch
You: Looks good, apply
Agent: Modifies category.py, runs gate
Output: PASS (exit=0) ✅
```

**Cenário 2: Batch fix (50 tables)**
```
You: @copilot /models-gate scan
Agent: [reads parity_report.json]
       45 PASS, 5 FAIL (athletes, categories, teams, ...)
You: Fix next
Agent: /parity-fix athletes
       [patch + validate]
[repeat until all PASS]
```

**Cenário 3: Install invariant**
```
You: @copilot /install-invariant INV-TRAIN-041
Agent: [reads INVARIANTS_TRAINING.md, candidates.md]
       SPEC: "focus_percent between 0-100"
       CODE: FocusPercentageInvariant class
       TESTS: 3 test functions
You: Mergeable?
Agent: ✓ SSOT updated, ✓ Tests pass, ✓ Gate ok
You: Commit
Agent: [creates PR checklist, updates CHANGELOG]
```

---

## 相互 Reference

- **Prompts source:** `.github/prompts/`
- **Canonical rules:** `docs/_canon/03_WORKFLOWS.md`
- **Guard rules:** `.hb_guard/baseline.json`
- **Execution templates:** `docs/execution_tasks/README.md`
