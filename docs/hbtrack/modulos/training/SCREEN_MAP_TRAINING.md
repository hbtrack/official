---
module: "training"
type: "screen-map"
ui_contract_ref: "./UI_CONTRACT_TRAINING.md"
contract_path_ref: "../../../../contracts/openapi/paths/training.yaml"
---

# SCREEN_MAP_TRAINING.md

> Mapa de navegação canônico do módulo **training**.
> Fonte soberana de hierarquia de telas, roles, contextos e pontos de entrada/saída.
> Em caso de divergência com UI_CONTRACT_TRAINING.md, o UI_CONTRACT é soberano.

**Versão:** 0.1.0
**Last Updated:** 2026-03-17

---

## Legenda

| Símbolo | Significado |
|---------|-------------|
| `→` | Navegação direta (tap/click) |
| `⇒` | Navegação condicional |
| `↩` | Retorno (back button / modal close) |
| `🏟️` | Contexto: quadra (mobile obrigatório) |
| `🖥️` | Contexto: escritório (desktop prioritário) |
| `👤` | Role: Athlete |
| `🎯` | Role: Coach / Head Coach / Assistant Coach |
| `⚠️` | Endpoint faltante — BLOCKED_MISSING_CANON_ARTIFACT |

---

## Mapa Geral — Árvore de Navegação

```
Root
├── 🎯 Coach — Modo Escritório 🖥️
│   ├── UIF-001: Session Planning & Configuration
│   │   ├── [1] Session List Screen ──────────────────── listTrainingSessions
│   │   │   └── → [2] Session Header Form
│   │   ├── [2] Session Header Form ─────────────────── createTrainingSession / updateTrainingSession
│   │   │   ├── → [3] Objectives Panel
│   │   │   ├── → [4] Session Blocks Builder
│   │   │   └── → [5] Recommendations Review (condicional)
│   │   ├── [3] Objectives Panel ────────────────────── listSessionObjectives / createSessionObjective
│   │   ├── [4] Session Blocks Builder ──────────────── listSessionBlocks / addSessionBlock / ...
│   │   ├── [5] Recommendations Review ⚠️ ─────────── MISSING (G-01)
│   │   └── [6] Session Published Confirmation ─────── publishTrainingSession
│   │       └── ↩ [1] Session List
│   │
│   ├── UIF-003: Coach Review & Intervention
│   │   ├── [1] Sessions to Review Queue ────────────── listTrainingSessions (status=COMPLETED)
│   │   │   └── → [2] Session Review Dashboard
│   │   ├── [2] Session Review Dashboard ────────────── getTrainingSessionById
│   │   │   ├── → [3] Attendance Panel
│   │   │   ├── → [4] Execution Summary
│   │   │   ├── → [5] Feedback & Interventions
│   │   │   └── → [6] Analytics Alerts (Attention Queue)
│   │   ├── [3] Attendance Panel ────────────────────── listSessionAttendance / recordSessionAttendance
│   │   ├── [4] Execution Summary ───────────────────── listExecutionRecords
│   │   ├── [5] Feedback & Interventions ────────────── listFeedbackThreads / createFeedbackThread
│   │   │   └── closeFeedbackThread ⚠️ ──────────────── MISSING (G-04)
│   │   ├── [6] Analytics Alerts ────────────────────── listAttentionQueueItems
│   │   │   └── resolve/dismiss/escalate ⚠️ ─────────── MISSING (G-03)
│   │   └── [7] Session Marked as Complete ──────────── completeTrainingSession
│   │       └── ↩ [1] Sessions to Review Queue
│   │
│   └── UIF-005: Load Chart — Modo Escritório 🖥️
│       ├── [1] Load Chart Dashboard ⚠️ ────────────── MISSING (G-05) getLoadChart
│       └── [2] Session Detail Tooltip (inline popover)
│
├── 🎯 Coach — Modo Quadra 🏟️
│   └── UIF-004: Team Readiness View
│       ├── [1] Session Quick Access ────────────────── listTrainingSessions (today, status=PUBLISHED/IN_PROGRESS)
│       │   └── → [2] Team Readiness Overview
│       ├── [2] Team Readiness Overview ─────────────── listSessionAttendance / getWellnessPre
│       │   ├── Exceções topo (readiness < 40 ou inelegível)
│       │   └── → [3] Athlete Detail Drill-down
│       └── [3] Athlete Detail Drill-down ───────────── getWellnessPre
│           └── → UIF-003 [5] Feedback (cross-flow)
│
└── 👤 Athlete — Modo Quadra 🏟️
    └── UIF-002: Athlete Check-in & Readiness
        ├── [1] Scheduled Sessions List ─────────────── listTrainingSessions (status=PUBLISHED)
        │   └── → [2] Pre-Training Check-in Form
        ├── [2] Pre-Training Check-in Form
        │   ├── → [3] Wellness Assessment
        │   ├── → [4] Readiness Score (client-side)
        │   └── → [5] Ineligibility Declaration ⚠️
        ├── [3] Wellness Assessment ─────────────────── submitWellnessPre / updateWellnessPre
        ├── [4] Readiness Score (calculado client-side)
        ├── [5] Ineligibility Declaration ⚠️ ─────────── MISSING (G-02)
        └── [6] Check-in Submitted Confirmation
            └── ↩ [1] Scheduled Sessions List
```

---

## Tabela de Telas

| UIF | Tela | ID | Contexto | Role | Entry Point | Exit Point(s) |
|-----|------|----|----------|------|-------------|---------------|
| 001 | Session List | UIF-001-S1 | 🖥️ escritório | 🎯 Coach | URL: `/training/sessions` | → S2, → S3 (edit) |
| 001 | Session Header Form | UIF-001-S2 | 🖥️ escritório | 🎯 Coach | Via S1 "Nova Sessão" ou "Editar" | → S3, S4, S5, S6 |
| 001 | Objectives Panel | UIF-001-S3 | 🖥️ escritório | 🎯 Coach | Painel dentro de S2 | ↩ S2 |
| 001 | Session Blocks Builder | UIF-001-S4 | 🖥️ escritório | 🎯 Coach | Painel dentro de S2 | ↩ S2 |
| 001 | Recommendations Review | UIF-001-S5 | 🖥️ escritório | 🎯 Coach | Condicional dentro de S2 ⚠️ | ↩ S2 |
| 001 | Published Confirmation | UIF-001-S6 | 🖥️ escritório | 🎯 Coach | Após S2 "Publicar" | → S1 ou reset S2 |
| 002 | Scheduled Sessions List | UIF-002-S1 | 🏟️ quadra | 👤 Athlete | URL: `/training/check-in` | → S2 |
| 002 | Pre-Training Check-in Form | UIF-002-S2 | 🏟️ quadra | 👤 Athlete | Via S1 tap sessão | → S3, S4, S5 |
| 002 | Wellness Assessment | UIF-002-S3 | 🏟️ quadra | 👤 Athlete | Painel dentro de S2 | → S4 (auto) |
| 002 | Readiness Score | UIF-002-S4 | 🏟️ quadra | 👤 Athlete | Auto após S3 (client-side) | → S5 |
| 002 | Ineligibility Declaration | UIF-002-S5 | 🏟️ quadra | 👤 Athlete | Painel dentro de S2 ⚠️ | → S6 |
| 002 | Check-in Confirmation | UIF-002-S6 | 🏟️ quadra | 👤 Athlete | Após "Confirmar" | ↩ S1 |
| 003 | Sessions to Review Queue | UIF-003-S1 | 🖥️ escritório | 🎯 Coach | URL: `/training/review` | → S2 |
| 003 | Session Review Dashboard | UIF-003-S2 | 🖥️ escritório | 🎯 Coach | Via S1 sessão | → S3, S4, S5, S6 |
| 003 | Attendance Panel | UIF-003-S3 | 🖥️ escritório | 🎯 Coach | Painel dentro de S2 | ↩ S2 |
| 003 | Execution Summary | UIF-003-S4 | 🖥️ escritório | 🎯 Coach | Painel dentro de S2 | ↩ S2 |
| 003 | Feedback & Interventions | UIF-003-S5 | 🖥️ escritório | 🎯 Coach | Painel dentro de S2 | ↩ S2 |
| 003 | Analytics Alerts | UIF-003-S6 | 🖥️ escritório | 🎯 Coach | Painel dentro de S2 | ↩ S2 |
| 003 | Session Marked as Complete | UIF-003-S7 | 🖥️ escritório | 🎯 Coach | Após "Completar Revisão" | ↩ S1 |
| 004 | Session Quick Access | UIF-004-S1 | 🏟️ quadra | 🎯 Coach | URL: `/training/pitch` | → S2 |
| 004 | Team Readiness Overview | UIF-004-S2 | 🏟️ quadra | 🎯 Coach | Via S1 "Ver equipe" | → S3 |
| 004 | Athlete Detail Drill-down | UIF-004-S3 | 🏟️ quadra | 🎯 Coach | Via S2 tap atleta | ↩ S2, → UIF-003 S5 |
| 005 | Load Chart Dashboard | UIF-005-S1 ⚠️ | 🖥️ escritório | 🎯 Coach/Coord | URL: `/training/load-chart` | — |
| 005 | Session Detail Tooltip | UIF-005-S2 | 🖥️ escritório | 🎯 Coach/Coord | Hover/click em S1 | ↩ S1 (dismiss) |

---

## Cross-Flow Links

| De | Para | Condição |
|----|------|----------|
| UIF-004 S3 (Athlete Detail) | UIF-003 S5 (Feedback) | Coach toca "Feedback" no drill-down |
| UIF-001 S1 (Session List) | UIF-003 S1 (Review Queue) | Sessão já COMPLETED (badge "Revisar") |
| UIF-002 S1 (Check-in List) | UIF-001 S1 | Atleta acessa visão read-only da sessão publicada |

---

## Gaps de Endpoints (resumo)

| Gap | UIF/Tela | Operação Bloqueada |
|-----|----------|--------------------|
| G-01 | UIF-001 S5 | Recomendações (listar/aceitar/rejeitar) |
| G-02 | UIF-002 S5 | Inelegibilidade (submeter/consultar) |
| G-03 | UIF-003 S6 | Attention Queue actions (resolver/rejeitar/escalar) |
| G-04 | UIF-003 S5 | Fechar feedback thread |
| G-05 | UIF-005 S1 | Load Chart (endpoint agregado ausente) |

> Ver detalhes completos em [UI_CONTRACT_TRAINING.md §Parte 8](./UI_CONTRACT_TRAINING.md#parte-8-gaps-de-contrato--blocked_missing_canon_artifact).

---

## Referências

- [UI_CONTRACT_TRAINING.md](./UI_CONTRACT_TRAINING.md) — contrato soberano de UI
- [STATE_MODEL_TRAINING.md](./STATE_MODEL_TRAINING.md) — FSM da training_session
- [PERMISSIONS_TRAINING.md](./PERMISSIONS_TRAINING.md) — roles por operação
- [contracts/openapi/paths/training.yaml](../../../../contracts/openapi/paths/training.yaml) — endpoints canônicos
