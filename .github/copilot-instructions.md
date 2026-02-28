# HB Track — Copilot Instructions (Repo-wide)

NÃO use histórico do chat como fonte de verdade. Fonte de verdade = arquivos SSOT do repositório.

Regras gerais:
- Não expandir escopo. Siga o papel do agente selecionado (Arquiteto/Executor/Testador).
- Proibido criar scripts .sh/.ps1. Infra/automação: somente Python (.py).
- Proibidos comandos destrutivos: git reset --hard, git checkout -- ., git clean -fd*, git restore (qualquer forma).
- Kanban é SSOT de ordem/estado operacional, mas NÃO autoriza commit.
- ✅ VERIFICADO é exclusivo do humano via hb seal.

SSOT principais:
- docs/_canon/contratos/Dev Flow.md
- docs/_canon/contratos/ar_contract.schema.json
- docs/_canon/specs/GOVERNED_ROOTS.yaml
- docs/_canon/specs/GATES_REGISTRY.yaml
- docs/_canon/specs/Hb cli Spec.md

Módulo TRAINING:
- docs/hbtrack/modulos/treinos/TRAINING_BATCH_PLAN_v1.md
- docs/hbtrack/modulos/treinos/AR_BACKLOG_TRAINING.md
- docs/hbtrack/Hb Track Kanban.md
- docs/hbtrack/modulos/treinos/* (invariants/specs/flows/screens)

Comandos destrutivos proibidos (hard-fail):
- git restore (qualquer forma)
- git reset --hard
- git checkout -- .
- git clean -fd*

Política HB Track:
- Scripts de automação/infra: somente Python (.py). Sem .sh/.ps1.
- Kanban orienta ordem/estado operacional, NÃO autoriza commit.

Se houver divergência entre Batch Plan / Backlog / Kanban:
- parar e reportar BLOCKED_INPUT (exit 4) com nota objetiva.


