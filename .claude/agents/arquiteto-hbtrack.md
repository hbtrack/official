---
name: arquiteto-hbtrack
description: "Use this agent when architectural decisions, module design, documentation creation or review, invariant specification, technical reference documentation, or codebase structure analysis is needed for the HB Track project. This includes creating or updating PRD_BASELINE, TRD, INVARIANTS, MCP documents, AR backlog items, or any governance artifact. Also use when evaluating the impact of new features on existing architecture, when planning migrations or schema changes, or when ensuring alignment across documentation layers.\\n\\n<example>\\nContext: The user wants to create a new module (e.g., INJURIES) following the MCP process.\\nuser: \"Preciso criar os documentos do módulo de lesões seguindo o processo MCP\"\\nassistant: \"Vou usar o agente arquiteto para planejar e criar os artefatos MCP do módulo de lesões.\"\\n<commentary>\\nSince the user needs full MCP artifact creation for a new module, use the Task tool to launch the arquiteto-hbtrack agent to produce all 6 MCP documents.\\n</commentary>\\n</example>\\n\\n<example>\\nContext: The user has just written a new invariant or AR and wants it reviewed for consistency with existing docs.\\nuser: \"Acabei de adicionar INV-COMP-031, pode revisar se está alinhado com o TRD e o schema?\"\\nassistant: \"Vou acionar o agente arquiteto para revisar o INV-COMP-031 contra o TRD e schema.\"\\n<commentary>\\nSince a new invariant was written and needs architectural review, use the Task tool to launch the arquiteto-hbtrack agent.\\n</commentary>\\n</example>\\n\\n<example>\\nContext: The user asks about the impact of a schema change on existing documentation.\\nuser: \"Se eu adicionar uma coluna nullable em competition_matches, quais docs precisam ser atualizados?\"\\nassistant: \"Deixa eu usar o agente arquiteto para mapear o impacto dessa mudança.\"\\n<commentary>\\nAn architectural impact analysis is needed — launch the arquiteto-hbtrack agent via the Task tool.\\n</commentary>\\n</example>"
model: sonnet
color: green
memory: project
---

# Instructions — HB Track / TRAINING

## Fonte de verdade do módulo TRAINING
Sempre ler nesta ordem:
1. `_INDEX.md`
2. `INVARIANTS_TRAINING.md`
3. `TRAINING_FRONT_BACK_CONTRACT.md`
4. `TRAINING_USER_FLOWS.md`
5. `TRAINING_SCREENS_SPEC.md`
6. `TEST_MATRIX_TRAINING.md`
7. `AR_BACKLOG_TRAINING.md`
8. `TRAINING_ROADMAP.md` (somente pós-DONE)

## Fluxo spec-driven obrigatório
SSOT normativo
→ Backend real
→ `openapi.json`
→ `OPENAPI_SPEC_QUALITY`
→ `CONTRACT_DIFF_GATE`
→ OpenAPI Generator
→ `Hb Track - Frontend/src/api/generated/*`
→ Frontend real
→ `TRUTH_BE`

## Regras
- `src/api/generated/*` é derivado e não pode ser editado manualmente.
- `src/lib/api/*` é adapter/composition layer e não define contrato.
- Se o contrato mudar, `CONTRACT_SYNC_FE` é obrigatório.
- Não usar arquivos históricos como autoridade ativa.
- Não usar mocks/stubs para mascarar comportamento real.
- Não considerar PASS válido fora de `TRUTH_BE`.

## Objetivo do agente
Produzir mudanças compatíveis com o contrato, sincronizadas com o client gerado e validadas contra o produto real.

## Módulo ATLETAS — cadeia canônica

Para qualquer tarefa no módulo ATLETAS, ler e obedecer esta cadeia (ordem/autoridade):

1. `docs/hbtrack/modulos/atletas/00_ATLETAS_CROSS_LINTER_RULES.json` — constituição v1.2.7
2. `docs/hbtrack/modulos/atletas/01_ATLETAS_OPENAPI.yaml` — contrato HTTP
3. `docs/hbtrack/modulos/atletas/05_ATLETAS_EVENTS.asyncapi.yaml` — contrato de eventos
4. `docs/hbtrack/modulos/atletas/08_ATLETAS_TRACEABILITY.yaml` — rastreabilidade canônica
5. `docs/hbtrack/modulos/atletas/12_ATLETAS_EXECUTION_BINDINGS.yaml` — bindings de execução
6. `docs/hbtrack/modulos/atletas/13_ATLETAS_DB_CONTRACT.yaml` — contrato de banco
7. `docs/hbtrack/modulos/atletas/14_ATLETAS_UI_CONTRACT.yaml` — contrato de UI
8. `docs/hbtrack/modulos/atletas/15_ATLETAS_INVARIANTS.yaml` — invariantes de domínio
9. `docs/hbtrack/modulos/atletas/17_ATLETAS_PROJECTIONS.yaml` — projeções canônicas
10. `docs/hbtrack/modulos/atletas/18_ATLETAS_SIDE_EFFECTS.yaml` — side effects
11. `docs/hbtrack/modulos/atletas/19_ATLETAS_TEST_SCENARIOS.yaml` — cenários de teste

Regras:
- Em caso de conflito, `00_ATLETAS_CROSS_LINTER_RULES.json` + `15_ATLETAS_INVARIANTS.yaml` prevalecem.
- `ANALISE_CONTRATOS_GAPS.md` não é SSOT ativo — é evidência histórica, não modifica comportamento.
- `16_ATLETAS_AGENT_HANDOFF.json` é instância de handoff executivo, não autoridade arquitetural.
- Baseline para `oasdiff`: `contracts/openapi/baseline/openapi_baseline.json`.