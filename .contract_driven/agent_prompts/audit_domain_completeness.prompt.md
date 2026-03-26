---
name: audit_domain_completeness
description: "Simulação de uso real: ciclo completo de módulo com injeção de borda para detectar lacunas silenciosas (audit-only, não produz artefato normativo)"
---

# AUDITORIA DE COMPLETUDE DE DOMÍNIO (SIMULAÇÃO DE USO REAL)

## 1. Objetivo Exato

Simular o ciclo completo de criação de contrato para um módulo específico e identificar
exatamente onde o pipeline:
1. **Bloquearia corretamente** (o que é esperado)
2. **Avançaria com lacuna não detectada** (o que é um bug)
3. **Forçaria inferência não-canônica** (o que é risco de alucinação)

Não é "verificar se os documentos existem". É simular o agente trabalhando e medir onde ele
pode errar sem ser detectado.

---

## 2. Escopo Exato

**Cenário de simulação padrão**: `module=wellness`, `task_type=new_contract`, `resource=wellness-entries`

Razão da escolha: `wellness` tem `status=draft_contract` (15 dos 16 módulos), sem documentação
elaborada, e tem limites com `medical` (módulo adjacente com boundary gate ativo).

**Sequência simulada**:
```
F0: Validação de entrada (orchestrator)
  → F1: Verificação de artefatos obrigatórios
    → Decision Discovery (backlog de decisões)
      → Authoring (criação do path file)
        → Validation (gates 0–16)
          → Readiness check
```

Para cada fase: registrar se o pipeline detecta a condição, o bloqueia corretamente, ou deixa passar.

---

## 3. Tipo de Teste

**Simulação próxima do uso real** com injeção deliberada de condições de borda.

A simulação executa o fluxo real com as entradas reais do repositório atual.
Em cada fase, é injetada uma condição problemática para testar o comportamento do pipeline.

---

## 4. Critérios Operacionais

| Critério | Definição de PASS |
|----------|------------------|
| **DC1 — Fase 0 determinística** | F0 do orchestrator produz resultado idêntico em execuções consecutivas com mesma entrada |
| **DC2 — Artefatos ausentes detectados** | Todos os artefatos obrigatórios ausentes de `wellness` geram `BLOCKED_REQUIRED_ARTIFACT_MISSING` |
| **DC3 — Boundary detectado** | Qualquer referência a `medical` dentro de `wellness` gera `WELLNESS_MEDICAL_BOUNDARY_GATE FAIL` |
| **DC4 — Sem lacuna silenciosa** | Nenhuma fase avança com artefato ausente sem emitir bloqueio ou warning explícito |
| **DC5 — Handoff materializável** | Se a simulação chega em Readiness com PASS, o handoff tem informação suficiente para implementação sem inferência adicional |

---

## 5. Injeções de Borda por Fase

### Fase 0 — Validação de Entrada

| Injeção | Comportamento esperado | Comportamento proibido |
|---------|----------------------|----------------------|
| `module=wellness` sem `DOMAIN_RULES_WELLNESS.md` | F0 PASS, F1 BLOCKED_REQUIRED_ARTIFACT_MISSING | Avançar para Authoring sem artefato |
| `task_type=new_contract` com `SESSION_HANDOFF.md` indicando bloqueio ativo | F0 deve mencionar o bloqueio do handoff | Ignorar SESSION_HANDOFF.md |

### Fase 1 — Artefatos Obrigatórios (wellness tem status draft_contract)

Lista de verificação: cada artefato ausente deve gerar bloqueio explícito.

| Artefato ausente | Bloqueio esperado |
|-----------------|------------------|
| `docs/hbtrack/modulos/wellness/README.md` | BLOCKED_REQUIRED_ARTIFACT_MISSING |
| `docs/hbtrack/modulos/wellness/DOMAIN_RULES_WELLNESS.md` | BLOCKED_MISSING_DOMAIN_RULE |
| `docs/hbtrack/modulos/wellness/INVARIANTS_WELLNESS.md` | BLOCKED_MISSING_INVARIANT |
| `contracts/schemas/wellness/*.schema.json` | BLOCKED_MISSING_SCHEMA |

### Decision Discovery — Decisões em Aberto

| Condição | Comportamento esperado |
|----------|----------------------|
| ADR obrigatória em aberto para `wellness` no backlog | BLOCKED_MISSING_ARCH_DECISION |
| Nenhuma ADR em aberto | PASS, avançar para Authoring |
| DSS (`docs/hbtrack/decisoes/wellness_notes.md`) referenciado como SSOT | BLOCKED_CONTRACT_CONFLICT ou SHADOW_AUTHORITY |

### Authoring — Criação do Contrato

| Condição | Comportamento esperado |
|----------|----------------------|
| Endpoint de `wellness` referencia campo que pertence a `medical` (ex: `diagnosisCode`) | WELLNESS_MEDICAL_BOUNDARY_GATE FAIL |
| operationId duplicado de outro módulo | CROSS_SPEC_ALIGNMENT_GATE FAIL |
| Campo sem `type` no schema | JSON_SCHEMA_VALIDATION_GATE FAIL |
| TODO residual no contrato | PLACEHOLDER_RESIDUE_GATE FAIL |

### Validation — Sequência de Gates (GATES_REGISTRY ordem 0→16)

Verificar que o pipeline executa na ordem correta e que um FAIL bloqueante para a sequência.

| Gate | Condição injetada | Deve parar em |
|------|------------------|--------------|
| AXIOM_INTEGRITY_GATE | `DOMAIN_AXIOMS.json` corrompido | Order:0, não avança |
| PATH_CANONICALITY_GATE | Artefato em path errado | Order:1, não avança para order:2 |
| PLACEHOLDER_RESIDUE_GATE | TODO em contrato | Order:3, não avança para REF_HERMETICITY |

---

## 6. Formato de Saída Obrigatório

```
AUDITORIA DE COMPLETUDE — HB TRACK
Data: <ISO-8601>
Executor: audit_domain_completeness.prompt.md v1.0.0
Módulo simulado: wellness
Task type simulado: new_contract

FASE 0 — VALIDAÇÃO DE ENTRADA
| Injeção | Esperado | Real | DC1: determinístico? | PASS/FAIL |
| ...     | ...      | ...  | SIM/NÃO              | ...       |

FASE 1 — ARTEFATOS OBRIGATÓRIOS
| Artefato testado | Bloqueio esperado | Bloqueio real | PASS/FAIL |
| README.md        | BLOCKED_REQUIRED... | <resultado>  | ...       |
| ... (todos os artefatos da lista) |

DECISION DISCOVERY
| Condição | Esperado | Real | PASS/FAIL |
| ...      | ...      | ...  | ...       |

AUTHORING — BORDA DE BOUNDARY
| Condição | Esperado | Real | DC3: boundary detectado? | PASS/FAIL |
| ...      | ...      | ...  | SIM/NÃO                  | ...       |

SEQUÊNCIA DE GATES
| Gate | Ordem | FAIL bloqueou sequência? | PASS/FAIL |
| ...  | ...   | SIM/NÃO                  | ...       |

LACUNAS SILENCIOSAS (DC4)
| Fase | Condição problemática | Detectada? | Se não: gap = |
| ... | ... | SIM/NÃO | descrição do gap |

HANDOFF MATERIALIZÁVEL (DC5)
Informações disponíveis ao implementador: [listar campos do handoff]
Inferência necessária: [listar campos que faltam]
DC5: PASS (zero inferência) | FAIL (N campos sem cobertura)

RESULTADO FINAL: PASS | FAIL
Lacunas silenciosas: <N>
Bloqueios corretos: <N>/<N_total>
Inferências necessárias no handoff: <N>
```

---

## 7. Restrições de Execução

- **Simular com o estado real do repositório.** Não criar artefatos hipotéticos.
- **Não corrigir lacunas durante a auditoria.** Reportar, não consertar.
- **Não aceitar "o agente avisaria o usuário" como cobertura de DC4.** Aviso sem bloqueio = lacuna.
- **Não marcar DC5 como PASS se houver um único campo de handoff sem fonte canônica.**
- **Módulo `wellness` pode mudar.** Repetir com `module=seasons` ou `module=teams` para validar generalização.

---

## 8. Iteração Guiada por Falha

- DC2 FAIL (artefato ausente não detectado): adicionar check explícito no gate correspondente
- DC3 FAIL (boundary não detectado): verificar se `WELLNESS_MEDICAL_BOUNDARY_GATE` está active e aplicável
- DC4 FAIL (lacuna silenciosa): o ponto de lacuna vira teste obrigatório no golden test suite
- DC5 FAIL (handoff incompleto): os campos ausentes viram campos obrigatórios no schema de session_start
- Após iteração: re-executar com módulo diferente (`seasons`) para confirmar que a correção generaliza
