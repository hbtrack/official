---
name: audit_gate_coverage
description: "Auditoria de cobertura: mapeia RULES §2–§23 contra gates bloqueantes, calcula score (audit-only, não produz artefato normativo)"
---

# AUDITORIA DE COBERTURA DE GATES (RUBRICA POR REGRA)

## 1. Objetivo Exato

Mapear cada seção normativa de `CONTRACT_SYSTEM_RULES.md` a ≥ 1 gate em `GATES_REGISTRY.yaml`
com `blocking: true`.

Identificar:
- **Regras sem enforcement técnico** (regra normativa existe, gate não existe ou é non-blocking)
- **Gates órfãos** (gate existe, nenhuma regra normativa o justifica)
- **Score de cobertura** por seção da RULES

Não é "conferir se os gates funcionam". É provar que toda regra normativa tem dente.

---

## 2. Escopo Exato

**Fonte A — Regras normativas**: todas as seções de `CONTRACT_SYSTEM_RULES.md` (§1–§23)
que definem comportamento obrigatório do agente ou do pipeline.

**Fonte B — Gates de enforcement**: todos os gates com `status: active` em `GATES_REGISTRY.yaml`.

**Interação**: cada regra de Fonte A deve ter ≥ 1 gate de Fonte B com `blocking: true` que a implemente.

**Fora de escopo**: gates com `blocking: false` (são avisos, não enforcement), `CONTRACT_SYSTEM_LAYOUT.md`,
conteúdo de contratos técnicos.

---

## 3. Tipo de Teste

**Auditoria de cobertura por rubrica com score.**

Score calculado por seção: `gates_bloqueantes_mapeados / regras_normativas_nessa_seção × 100`.

Threshold de aprovação por seção:
- Seções §2–§9 (regras de canonização, idioma, artefatos): 100% obrigatório
- Seções §10–§18 (docs de módulo, DoD): 80% mínimo
- Seções §19–§23 (tooling, modos, evolution): 60% mínimo

---

## 4. Critérios Operacionais

| Critério | Definição de PASS |
|----------|------------------|
| **GC1 — Cobertura §2–§9** | 100% das regras normativas têm gate bloqueante |
| **GC2 — Cobertura §10–§18** | ≥ 80% das regras têm gate bloqueante |
| **GC3 — Cobertura §19–§23** | ≥ 60% das regras têm gate bloqueante ou ponteiro para CI |
| **GC4 — Zero gates órfãos** | Todo gate em GATES_REGISTRY tem referência explícita a uma seção normativa |
| **GC5 — Ordem de dependência** | Gates com `depends_on` implementam precedência correta de `RULES §5` |

Score global de cobertura = `total_regras_com_gate_bloqueante / total_regras_normativas × 100`.
Meta: ≥ 85%.

---

## 5. Mapeamento de Referência

Tabela inicial para verificação (completar na auditoria):

| Seção RULES | Obrigação normativa | Gate canônico | Blocking? | Coberto? |
|-------------|--------------------|--------------:|----------|---------|
| §2A — Canonização | Regra dos 3 níveis obrigatória | REQUIRED_ARTIFACT_PRESENCE_GATE | true | verificar |
| §2A.4 — Classificação boot | Todo artefato classifica boot | REQUIRED_ARTIFACT_PRESENCE_GATE | true | verificar |
| §2B — Naming | Convenções de idioma e path | PATH_CANONICALITY_GATE | true | verificar |
| §3A — Path compliance | Artefato fora de path = não-compliant | PATH_CANONICALITY_GATE | true | verificar |
| §5 — Precedência | Conflito no mesmo nível = bloqueio | CROSS_SPEC_ALIGNMENT_GATE | true | verificar |
| §6 — Boot do agente | Boot falha → bloquear, não inferir | PRE_CONTRACT_EVIDENCE_GATE | true | verificar |
| §8 — Modo estrito | Artefato ausente → bloquear | REQUIRED_ARTIFACT_PRESENCE_GATE | true | verificar |
| §9 — Códigos de bloqueio | 19 códigos canônicos | (verificar cada código) | varies | verificar |
| §10.1 — Docs obrigatórios | Presença mínima por módulo | REQUIRED_ARTIFACT_PRESENCE_GATE + MODULE_DOC_CROSSREF_GATE | true | verificar |
| §10.2 — Docs condicionais | Presença quando aplicável | ASYNC_REQUIRED_MODULE_GATE | true | verificar |
| §12 — Gatilho handebol | Link obrigatório para HANDBALL_RULES | (verificar gate específico) | ? | verificar |
| §14A — Domain Shapes | Schema soberano obrigatório | JSON_SCHEMA_VALIDATION_GATE | true | verificar |
| §16 — DoD contrato | Contrato pronto = todos os gates PASS | READINESS_SUMMARY_GATE | true | verificar |
| §16.1 — DoD HTTP | Gates específicos HTTP | OPENAPI_ROOT_STRUCTURE_GATE + OPENAPI_POLICY_RULESET_GATE | true | verificar |
| §16.2 — DoD AsyncAPI | ASYNCAPI_VALIDATION_GATE | ASYNCAPI_VALIDATION_GATE | true | verificar |
| §16.3 — DoD Arazzo | ARAZZO_VALIDATION_GATE | ARAZZO_VALIDATION_GATE | true | verificar |
| §22 — Fase pré-contrato | Não pular orchestrator | PRE_CONTRACT_EVIDENCE_GATE | true | verificar |
| §23 — Evolution Rule | Contract-first obrigatório | (verificar gate específico) | ? | verificar |

---

## 6. Formato de Saída Obrigatório

```
AUDITORIA DE COBERTURA DE GATES — HB TRACK
Data: <ISO-8601>
Executor: audit_gate_coverage.prompt.md v1.0.0

MAPEAMENTO COMPLETO
| Seção | Obrigação | Gate(s) | Blocking? | Score parcial |
|-------|-----------|---------|-----------|--------------|
| §2A   | ...       | ...     | true/false | N/M          |
| ... (todas as seções normativas) |

GAPS — REGRAS SEM ENFORCEMENT
| Seção | Obrigação normativa | Motivo da lacuna | Severidade |
|-------|--------------------|-----------------| -----------|
| ...   | ...               | gate ausente / non-blocking / dependência errada | CRÍTICA/ALTA/MÉDIA |

GATES ÓRFÃOS
| gate_id | Nenhuma seção mapeada | Ação recomendada |
| ...     | ...                   | remover / mapear  |

SCORE POR GRUPO
| Grupo | Threshold | Score | PASS/FAIL |
|-------|-----------|-------|-----------|
| §2–§9 | 100% | N% | PASS/FAIL |
| §10–§18 | 80% | N% | PASS/FAIL |
| §19–§23 | 60% | N% | PASS/FAIL |

SCORE GLOBAL: N% (meta ≥ 85%)

RESULTADO FINAL: PASS | FAIL
Gaps críticos: [lista ou NENHUM]
Gates órfãos: [N]
```

---

## 7. Restrições de Execução

- **Não contar gate non-blocking como cobertura.** Aviso ≠ dente.
- **Não aceitar "o gate cobre implicitamente".** Cobertura exige mapeamento explícito.
- **Não criar gates novos nesta auditoria.** Apenas reportar gaps — criação é tarefa separada.
- **Não dar score alto por quantidade de gates.** 28 gates com 5 regras descobertas = FAIL.

---

## 8. Iteração Guiada por Falha

- GC1 FAIL (gap em §2–§9): novo gate bloqueante é requisito obrigatório antes de próximo contrato
- GC4 FAIL (gate órfão): gate é candidato a remoção ou precisa de `spec_ref` adicionado ao GATES_REGISTRY
- Após iteração: re-executar auditoria até score global ≥ 85% com GC1 = 100%
