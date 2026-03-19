## Orquestrador Pré-Contrato — HB Track

**Propósito**: ponto de entrada obrigatório para toda tarefa de contratos.
**Autoridade*: operacionaliza docs/_canon/AGENT_INSTRUCTIONS.md; não define regras.

### Entrada Esperada
| Campo             | Obrigatório | Valores |
|------------------|-------------|---------|
| module           | sim         | 16 canônicos (docs/_canon/MODULE_REGISTRY.yaml) |
| task_type        | sim         | tipos ativos em .contract_driven/TASK_CATALOG.yaml |
| resource         | condicional | para new_contract, contract_revision |
| scope_description| recomendado | descrição livre |

---

### Pré-Fase — SESSION_HANDOFF
Se existir `SESSION_HANDOFF.md` → ler ANTES de qualquer ação.
Antes de mensagens ao humano: seguir docs/_canon/AGENT_INSTRUCTIONS.md §6 (etiqueta, vocabulário).

---

## FASE 0 — VALIDAÇÃO DE ENTRADA (bloqueante)

Executar `hb verify`. Se exitcode ≠ 0 → corrigir, re-executar.

| Check | Fonte | Falha |
|---|---|---|
| task_type declarado | Input | Perguntar task_type |
| task_type em .contract_driven/TASK_CATALOG.yaml | .contract_driven/TASK_CATALOG.yaml | BLOCKED_MISSING_AGENT_PROMPT |
| module declarado | Input | Perguntar module |
| module em MODULE_REGISTRY.yaml | MODULE_REGISTRY.yaml | BLOCKED_MISSING_MODULE |
| Worker .prompt.md existe | .contract_driven/agent_prompts/ | BLOCKED_MISSING_AGENT_PROMPT |
| SESSION_HANDOFF.md lido | Contexto | Ler antes |

---

## Fases 1-4 — Pre-Authoring, Artifact, Pre-commit
Ver [CONTRACT_PIPELINE.md](../../docs/_canon/CONTRACT_PIPELINE.md) para detalhes (Fases 1-2-3-4).

### FASE 1 — Descoberta de Artefatos (bloqueante)

Após FASE 0, se existir artefato de contrato (ex: contracts/openapi/paths/{module}.yaml):

1. **MODULE_REGISTRY_GATE**: verificar módulo está em MODULE_REGISTRY.yaml
   - Falha → BLOCKED_MISSING_MODULE

2. **SCOPE_BOUNDARY_GATE**: validar referências cross-module
   - Se artefato contém $ref, operationId ou channel com formato module.* indicando cross-module:
     - Executar: `python scripts/gates/check_scope_boundary.py {artifact_path}`
     - Exitcode 0 → PASS, continuar
     - Exitcode 1 → BLOCKED_SCOPE_OVERFLOW, bloquear
     - Exitcode 2-4 → ERROR (malformed, policy missing, module unknown)
   - Se nenhuma referência cross-module → SKIP este gate

3. **REQUIRED_ARTIFACT_PRESENCE_GATE**: verificar artefatos obrigatórios
   - Falha → BLOCKED_REQUIRED_ARTIFACT_MISSING

4. Decisões bloqueantes abertas em ARCHITECTURE_DECISION_BACKLOG.md?
   - Sim → Fase 2 (Decision Discovery)
   - Não → continuar

---

## Fases 1-4 — Pre-Authoring, Artifact, Pre-commit
Ver [CONTRACT_PIPELINE.md](../../docs/_canon/CONTRACT_PIPELINE.md) para detalhes (Fases 1-2-3-4).

---

## Observabilidade

Emitir por fase:
```
[ORCHESTRATOR] fase:<0-4> module:<M> task_type:<T>
  boot_profile:<P> module_status:<S>
  resultado: PASS | BLOCKED | SKIP
  bloqueios: [list]
  worker_destino: <prompt ou NONE>
```

Publicar `_reports/session_start.json` com resultado (PASS/BLOCKED/SKIP).

---

## Bloqueios Canônicos

| Código | Fase | Condição |
|--------|------|----------|
| BLOCKED_MISSING_MODULE | F0 | Módulo não em MODULE_REGISTRY.yaml |
| BLOCKED_MISSING_AGENT_PROMPT | F0 | Worker não existe |
| BLOCKED_REQUIRED_ARTIFACT_MISSING | F1 | Artefato obrigatório ausente |
| BLOCKED_MISSING_ARCH_DECISION | F1 | Decisão bloqueante aberta |

Nunca prosseguir ignorando bloqueio.
