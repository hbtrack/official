---
name: ar-handoff-writer
description: Escreve _reports/ARQUITETO.yaml no formato canônico HB Track (PLAN_HANDOFF), incluindo tabela de planos, ordem e diagnóstico por AR.
---

# Skill — Arquiteto: Handoff Writer (PLAN_HANDOFF)

Objetivo
- Preencher `_reports/ARQUITETO.yaml` no seu layout real:
  - cabeçalho (protocolo/branch/head/data/status)
  - tabela “Planos Materializados”
  - “Ordem de execução”
  - “Diagnóstico por AR” (write_scope + validation_command + ACs)

Inputs mínimos
- Lista de (AR_id, AR-TRAIN id, plan_json_path, dependência)
- Resultado do `hb plan --dry-run` (exit + observações, ex.: colisão/force/skip)
- Estado Kanban (Batch alvo e status)

Template obrigatório (estrutura)
1) Título: `# ARQUITETO.yaml — Handoff para Executor`
2) Metadados: Protocolo / Branch / HEAD / Data / Status = PLAN_HANDOFF
3) Contexto
- Ex.: “Batch 1 concluído ✅ … gen_docs_ssot.py rodado …”
4) Planos Materializados (tabela)
- AR | AR-TRAIN | Plano JSON | Dependência
5) Ordem de execução
- Sequência e paralelismo conforme Kanban (ex.: AR_177→AR_178; AR_179→AR_180; paralelas)
6) Diagnóstico por AR
- write_scope
- validation_command
- critérios de aceite (ACs) e riscos
- gates_required (somente gates existentes no registry)

Regras
- Não referenciar gate inexistente (checar `docs/_canon/specs/GATES_REGISTRY.yaml`).
- Não inventar AR/IDs: tudo deve existir no Kanban/Backlog/Batch.
- Se divergência entre Batch Plan/Backlog/Kanban -> BLOCKED_INPUT (exit 4) e registrar.

Saída
- Sobrescrever `_reports/ARQUITETO.yaml` com o conteúdo final.