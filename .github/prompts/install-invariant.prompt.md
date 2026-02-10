---
name: install-invariant
description: Instalar nova invariante de training seguindo protocolo/guardrails e atualizando SSOT + testes + evidência.
argument-hint: "opcional: INV-ID (ex: INV-TRAIN-041) ou 'next'"
agent: copilot
---

# Install Invariant Protocol

Objetivo: instalar 1 invariante de training com rastreabilidade total. Não inferir. Tudo deve ser ancorado em SSOT e evidências do workspace.

## Leia Primeiro

- [AI INDEX](../../docs/_ai/_INDEX.md)
- [AGENT PROTOCOL](../../docs/_ai/INVARIANTS_AGENT_PROTOCOL.md)
- [AGENT GUARDRAILS](../../docs/_ai/INVARIANTS_AGENT_GUARDRAILS.md)
- SSOT catálogo: [INVARIANTS_TRAINING](../../docs/02_modulos/training/INVARIANTS/INVARIANTS_TRAINING.md)
- Testes canônicos: [INVARIANTS_TESTING_CANON](../../docs/02_modulos/training/INVARIANTS/INVARIANTS_TESTING_CANON.md)
- Backlog/candidates: [candidates](../../docs/02_modulos/training/INVARIANTS/training_invariants_candidates.md) e [backlog](../../docs/02_modulos/training/INVARIANTS/training_invariants_backlog.md)

## Evidência/Artefatos

- status gerado: `docs/_generated/training_invariants_status.md` (se existir)
- verificador: `docs/scripts/verify_invariants_tests.py`
- logs/relatórios relevantes em `docs/_generated/_core/`

## Tarefa

1) **Determine qual invariante instalar:**
   - Se `${input:inv}` = 'next' ou vazio: escolha a próxima marcada como "promover" em candidates/backlog conforme protocolo
   - Se um INV-ID for fornecido: valide que não existe em INVARIANTS_TRAINING e não colide

2) **Escreva/atualize:**
   - SPEC no SSOT
   - implementação (classe/regra)
   - teste(s) conforme INVARIANTS_TESTING_CANON

3) **Execute** (ou instrua execução) do gate/verificador e apresente critérios claros de PASS/FAIL

4) **Atualize** candidates/backlog/status conforme protocolo

## Entrega (4 Blocos)

A) **Seleção do alvo** — e justificativa (citando candidates/backlog)  
B) **Mudanças necessárias** — SSOT + código + testes com paths  
C) **Comandos de validação** — e outputs esperados  
D) **Checklist de PR** — mínimo

Se arquivo-chave não for encontrado, declare PENDENTE e aponte o caminho correto a localizar no codebase.
