---
# Substituir CADA campo antes de salvar — front matter é validado por session_handoff.schema.json
# via HANDOFF_COHERENCE_GATE em validate_contracts.py. Campos inválidos bloqueiam o pipeline.
data_ultima_sessao: "2026-01-01"          # YYYY-MM-DD — nunca data futura
branch_ativo: "hb-track-contratos-driven" # git branch ativo
modo_operacao: CDD                        # enum: CDD | ROADMAP
ci_status: PASS                           # enum: PASS | FAIL | UNKNOWN
modulo_foco: "governance"                 # módulo, trilha ou área principal
fase_roadmap: 0                           # inteiro >= 0
roadmap_phase: 0                          # OBRIGATÓRIO quando task_type=execute_roadmap_phase. Mesmo valor de fase_roadmap; alinha com session_start.roadmap_phase
task_type: "new_contract"                 # task_type canônico do TASK_CATALOG
boot_profile_id: contract_execution       # enum: default | contract_execution | architecture_decision | diagnostic | roadmap_execution
task_id: "fase-X-task-Y"                  # identificador da tarefa
resultado: PENDENTE                       # enum: DONE | PENDENTE | BLOCKED
proxima_acao_permitida: "Descrever a próxima ação executável sem ambiguidade (mín. 10 caracteres)"
bloqueios_ativos: []                      # lista vazia ou itens de string
evidence_paths:                           # OBRIGATÓRIO: mín. 1 path de evidência
  - "_reports/runs/<run_id>/contract_gates.json"
---
# SESSION HANDOFF — HB TRACK
> Atualizar ao final de cada sessão produtiva. Delta-only. Este arquivo é lido antes de qualquer outra ação.

## Estado Geral
**Data:** YYYY-MM-DD | **Branch:** <branch> | **CI:** PASS
**Modo:** <CDD|ROADMAP> | **task_type:** <task_type> | **boot_profile:** <boot_profile_id>
**Módulo foco:** <module> | **Fase ROADMAP:** <fase> | **task_id:** <task> | **Resultado:** <resultado>

## O que foi feito
- item objetivo 1
- item objetivo 2

## Evidências
- `_reports/runs/<run_id>/contract_gates.json`
- `_reports/runs/<run_id>/health.json`

## Próxima ação permitida
Descrever a próxima ação executável, sem ambiguidade.

## Bloqueios ativos
Nenhum.
