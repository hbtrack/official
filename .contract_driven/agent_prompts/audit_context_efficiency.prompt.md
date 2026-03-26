---
name: audit_context_efficiency
description: "Auditoria de contexto: mede orçamento de boot e alcançabilidade de regras críticas em ≤2 hops (audit-only, não produz artefato normativo)"
---

# AUDITORIA DE EFICIÊNCIA DE CONTEXTO

## 1. Objetivo Exato

Verificar se o orçamento de contexto do boot está sendo respeitado **sem perda de determinismo**:
cada regra crítica deve ser alcançável em ≤ 2 hops a partir do boot mínimo,
e nenhum artefato do boot mínimo deve exceder seu limite de palavras definido em `.dev/planejamento/execut.md`.

Não é "tornar os textos menores". É provar que a redução de contexto não criou lacunas que forçam inferência.

---

## 2. Escopo Exato

Artefatos do boot mínimo (únicos verificados nesta auditoria):

| Artefato | Budget máximo |
|----------|--------------|
| `docs/_canon/AGENT_INSTRUCTIONS.md` | 450 palavras |
| `SESSION_HANDOFF.md` | 350 palavras |
| `docs/_canon/CONTRACT_PIPELINE.md` | 600 palavras |
| `.contract_driven/agent_prompts/pre_contract_orchestrator.prompt.md` | 700 palavras |

Regras críticas que devem permanecer alcançáveis (2 hops máx desde boot):

| Regra crítica | Fonte soberana | Hop 1 | Hop 2 (máx) |
|---------------|---------------|-------|-------------|
| Bloqueios canônicos (19 códigos) | `docs/_canon/AGENT_INSTRUCTIONS.md §5` | — | — |
| Mapa task_type → worker | `docs/_canon/AGENT_INSTRUCTIONS.md §4` | — | — |
| Condição de bloqueio de fase pré-contrato | `RULES §22` | ponteiro em docs/_canon/AGENT_INSTRUCTIONS.md | RULES |
| Ordem de precedência de conflito | `RULES §5` | ponteiro em docs/_canon/AGENT_INSTRUCTIONS.md | RULES |
| DoD binário por superfície | `RULES §16–§17` | ponteiro em PIPELINE | RULES |
| Critérios de boot condicional | `docs/_canon/AGENT_INSTRUCTIONS.md §7` (quando implementado) | — | — |

**Fora de escopo**: conteúdo dos artefatos além dos 4 do boot mínimo, gates de validação, docs de módulo.

---

## 3. Tipo de Teste

**Medição por rubrica + teste de alcançabilidade.**

Dois sub-testes:
- **Sub-teste A** (medição): contar palavras de cada artefato do boot mínimo
- **Sub-teste B** (alcançabilidade): verificar se cada regra crítica tem ponteiro explícito
  rastreável em ≤ 2 hops desde o artefato de boot

---

## 4. Critérios Operacionais

| Critério | Definição binária de PASS |
|----------|--------------------------|
| **CE1 — Budget respeitado** | Palavras do artefato ≤ budget definido (contar com `wc -w` ou equivalente) |
| **CE2 — Ponteiro rastreável** | Cada regra crítica tem referência explícita (link, seção, path) — não inferida |
| **CE3 — Sem regra órfã** | Nenhuma regra de `RULES §2–§23` está acessível APENAS via artefato não-boot (seria lacuna) |
| **CE4 — Sem redundância no boot** | Nenhuma regra completa aparece duplicada em dois artefatos do boot mínimo |
| **CE5 — Sem default implícito** | Nenhum ponto do fluxo depende de "inferir pelo contexto" quando o contexto não está carregado |

---

## 5. Formato de Saída Obrigatório

```
AUDITORIA DE CONTEXTO — HB TRACK
Data: <ISO-8601>
Executor: audit_context_efficiency.prompt.md v1.0.0

SUB-TESTE A — MEDIÇÃO DE ORÇAMENTO
| Artefato | Budget | Palavras reais | Status | Delta |
|----------|--------|---------------|--------|-------|
| docs/_canon/AGENT_INSTRUCTIONS.md | 450 | <N> | PASS/FAIL | +/- N |
| SESSION_HANDOFF.md | 350 | <N> | PASS/FAIL | +/- N |
| CONTRACT_PIPELINE.md | 600 | <N> | PASS/FAIL | +/- N |
| pre_contract_orchestrator.prompt.md | 700 | <N> | PASS/FAIL | +/- N |

SUB-TESTE B — ALCANÇABILIDADE EM ≤2 HOPS
| Regra crítica | Hop 0 (artefato boot) | Hop 1 | Hop 2 | Alcançável? |
|---------------|----------------------|-------|-------|------------|
| Bloqueios canônicos | docs/_canon/AGENT_INSTRUCTIONS.md §5 | — | — | PASS/FAIL |
| ... (todas as regras da tabela §2) |

CRITÉRIO CE3 — REGRAS ÓRFÃS
| Seção RULES | Alcançável desde boot? | Se não: gap = |
| §2 Canonização | SIM/NÃO | nome do gap |
| ... (todas as seções §2–§23) |

CRITÉRIO CE4 — REDUNDÂNCIAS NO BOOT
| Regra duplicada | Artefato A | Artefato B | Ação recomendada |
| ... |

CRITÉRIO CE5 — DEFAULTS IMPLÍCITOS
| Ponto do fluxo | Contexto necessário | Carregado no boot? | PASS/FAIL |
| ... |

RESULTADO FINAL: PASS | FAIL
Palavras totais do boot base: <N> (meta: ≤ 2.100 somadas)
Regras órfãs encontradas: <N>
Redundâncias encontradas: <N>
```

---

## 6. Restrições de Execução

- **Não contar cabeçalhos YAML no total de palavras** (frontmatter é metadata, não conteúdo boot).
- **Não dar PASS se a regra crítica aparece apenas em comentário** ou em texto não-normativo.
- **Não sugerir remoção de regras para cumprir budget.** Se budget excedido, a saída correta é FAIL + listar o excedente.
- **Não compensar lacuna com "o agente sabe disso".** O agente não pode presumir regras não carregadas.

---

## 7. Iteração Guiada por Falha

- CE1 FAIL (budget excedido): identificar as N palavras em excesso e qual conteúdo é candidato a mover para `boot_condicional` ou `gate_only`
- CE3 FAIL (regra órfã): criar ponteiro explícito no artefato de boot adequado — não reescrever a regra
- CE5 FAIL (default implícito): o ponto de fluxo com default implícito vira bloqueio canônico explícito
