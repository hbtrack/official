---
document: "ACTION_ITEM_TRACKER"
module: "training"
version: "1.1.0"
date: "2026-03-17"
status: "LIVE_TRACKING"
---

# Action Item Tracker — UI Contract Training v1.1.0

**Módulo:** training  
**Status:** validated_contract → implementation_ready (pendente sign-off)  
**Última Atualização:** 2026-03-17 14:30 UTC  
**Responsável:** Engineering Lead (tracking), PO (validação negócio), UX (validação design)

---

## 📊 Status Geral

| Categoria | Total | Completo | Pendente | % |
|-----------|-------|----------|----------|---|
| 📋 Pré-requisitos Técnicos | 4 | 4 | 0 | ✅ 100% |
| 🎯 Decisões de Design | 9 | 9 | 0 | ✅ 100% |
| 💻 Fluxos de UI (UIFs) | 5 | 5 | 0 | ✅ 100% |
| 🔌 Endpoints OpenAPI | 34 | 34 | 0 | ✅ 100% |
| 📦 Schemas JSON | 10 | 10 | 0 | ✅ 100% |
| ✍️ **Sign-off Doctos** | 3 | 3 | 0 | ✅ 100% |

---

## ✅ PRÉ-REQUISITOS TÉCNICOS (Tudo Pronto)

### Item 1: OpenAPI - 34 Endpoints

| ID | Status | Detalhes | Verificação |
|----|--------|----------|-------------|
| **✅ UIF-001** | Completo | 11 endpoints (session planning) | `contracts/openapi/paths/training.yaml` linha ~XXX |
| **✅ UIF-002** | Completo | 5 endpoints (check-in) | `contracts/openapi/paths/training.yaml` linha ~XXX |
| **✅ UIF-003** | Completo | 13 endpoints (review + feedback) | `contracts/openapi/paths/training.yaml` linha ~XXX |
| **✅ UIF-004** | Completo | 5 endpoints (team readiness) | `contracts/openapi/paths/training.yaml` linha ~XXX |
| **✅ UIF-005** | Completo | 1 endpoint (load chart) | `contracts/openapi/paths/training.yaml` linha ~XXX |
| **✅ G-01–G-05** | Completo | 9 endpoints (gaps resolvidos) | Todos em training.yaml (2026-03-17) |

**Ação:** Nenhuma — `training.yaml` estava atualizado em 2026-03-17.

---

### Item 2: JSON Schemas - 10 Schemas

| Schema | Status | Path | Validação |
|--------|--------|------|-----------|
| **✅ training_session** | ✅ Existe | `contracts/schemas/training/training_session.v1.json` | Schema válido v7 |
| **✅ session_objective** | ✅ Existe | `contracts/schemas/training/session_objective.v1.json` | ✓ |
| **✅ session_block** | ✅ Existe | `contracts/schemas/training/session_block.v1.json` | ✓ |
| **✅ training_attendance_marked** | ✅ Existe | `contracts/schemas/training/training_attendance_marked.v1.json` | ✓ |
| **✅ wellness_assessment** | ✅ Existe | `contracts/schemas/training/wellness_assessment.v1.json` | ✓ |
| **✅ athlete_ineligibility_declaration** | ✅ Existe | `contracts/schemas/training/athlete_ineligibility_declaration.v1.json` | ✓ G-02 |
| **✅ feedback_thread** | ✅ Existe | `contracts/schemas/training/feedback_thread.v1.json` | ✓ |
| **✅ attention_queue_item** | ✅ Existe | `contracts/schemas/training/attention_queue_item.v1.json` | ✓ |
| **✅ recommendation** | ✅ Existe | `contracts/schemas/training/recommendation.v1.json` | ✓ G-01 |
| **✅ load_chart** | ✅ Existe | `contracts/schemas/training/load_chart.v1.json` | ✓ G-05 |

**Ação:** Nenhuma — todos os 10 schemas foram criados.

---

### Item 3: Backend Stack Confirmation

| Componente | Decisão | Status | ADR | Aprovado |
|------------|---------|--------|-----|----------|
| Language | Python 3.12 | ✅ | ADR-031 | ✅ |
| Framework | Django 5.x | ✅ | ADR-031 | ✅ |
| API Layer | Django Ninja 1.x | ✅ | ADR-031 | ✅ |
| Database | PostgreSQL 16 | ✅ | ADR-031 | ✅ |
| ORM | Django ORM | ✅ | ADR-031 | ✅ |
| Async Tasks | Celery 5.x + Redis 7 | ✅ | ADR-031 | ✅ |
| WebSocket | Django Channels 4.x | ✅ | ADR-031 | ✅ |

**Ação:** Nenhuma — ADR-031 aprovado e ratificado.

---

### Item 4: Frontend Stack Confirmation

| Componente | Decisão | Status | ADR | Aprovado |
|------------|---------|--------|-----|----------|
| Framework | Next.js 14 (App Router) | ✅ | ADR-030 | ✅ |
| UI Library | shadcn/ui + Tailwind CSS | ✅ | ADR-030 | ✅ |
| Charting | Recharts | ✅ | D-UI-18 | ✅ |
| Drag-and-Drop | dnd-kit | ✅ | D-UI-18 | ✅ |
| PWA | next-pwa | ✅ | D-UI-17, ADR-030 | ✅ |
| Deployment | Vercel (recomendado) | ✅ | ADR-030 | — |

**Ação:** Nenhuma — ADR-030 aprovado e ratificado.

---

## 🎯 DECISÕES DE DESIGN (Tudo Documentado)

### Decisões Arquiteturais (D-UI-15 a D-UI-19)

| ID | Decisão | Escolha | Status | Referência |
|----|---------|---------|--------|-----------|
| **D-UI-15** | Offline Functionality | **Online obrigatório** (sem cache) | ✅ | UI_CONTRACT_TRAINING.md Parte 0 |
| **D-UI-16** | Plataforma Prioritária | **Split**: quadra (mobile) + escritório (desktop) | ✅ | UI_CONTRACT_TRAINING.md Parte 0 |
| **D-UI-SP-01** | Readiness Score | **Adotado**: coach vê score antes de sessão | ✅ | UIF-004, Parte 0 |
| **D-UI-SP-02** | Visão de Equipe | **Adotado**: tela primária é equipe (não indiv) | ✅ | UIF-004 [2], Parte 0 |
| **D-UI-SP-03** | Progressive Disclosure | **Adotado**: 1 cor + 1 número (primeiro), dados em 2ª camada | ✅ | UIF-002 [1], Parte 0 |
| **D-UI-SP-04** | Load Chart Desktop | **Adotado**: ATL/CTL inspirado TrainingPeaks | ✅ | UIF-005, Parte 0 |
| **D-UI-17** | Mecanismo Entrega | **PWA**: único codebase, installável mobile | ✅ | ADR-030, Parte 0 |
| **D-UI-18** | Stack Frontend | **Next.js 14 + shadcn/ui + Tailwind** | ✅ | ADR-031, Parte 0 |
| **D-UI-19** | Gaps MVP | **Todos (G-01–G-05) no MVP v1.0** | ✅ | Parte 8 |

**Ação:** Nenhuma — todas as 9 decisões documentadas e ratificadas em 2026-03-17.

---

## 💻 FLUXOS DE UI (5 UIFs Completos)

### Visão Geral

| UIF | Nome | Telas | Endpoints | Estados | Status |
|-----|------|-------|-----------|---------|--------|
| **001** | Session Planning & Configuration | 6 | 11 | ✅ | Completo |
| **002** | Athlete Check-in & Readiness | 6 | 5 | ✅ | Completo |
| **003** | Coach Review & Intervention | 7 | 13 | ✅ | Completo |
| **004** | Team Readiness View (Quadra) | 3 | 5 | ✅ | Completo |
| **005** | Load Chart (Escritório) | 2 | 1 | ✅ | Completo |

**Total:** 24 telas, 34 endpoints, 100% mapeado

### Detalhes por UIF

---

#### **UIF-001: Session Planning & Configuration** ✅

| Elemento | Detalhes | Status |
|----------|----------|--------|
| Telas | [1] List, [2] Header, [3] Objectives, [4] Blocks, [5] Recommendations, [6] Confirmed | ✅ |
| Endpoints | listSessions, createSession, updateSession, listObjectives, createObjective, listBlocks, addBlock, updateBlock, deleteBlock, reorderBlocks, publishSession | ✅ |
| Schemas | training_session, session_objective, session_block, recommendation | ✅ |
| Componentes | card, form, select, textarea, slider(7), draggable-list, microButton | ✅ |
| Estados | loading, success, error, empty, disabled | ✅ |
| Endpoints Especiais | G-01: listRecommendations, acceptRecommendation, dismissRecommendation | ✅ |

**Ação:** Nenhuma — UIF-001 100% documentado.

---

#### **UIF-002: Athlete Check-in & Readiness** ✅

| Elemento | Detalhes | Status |
|----------|----------|--------|
| Telas | [1] Scheduled Sessions, [2] Header, [3] Wellness, [4] Readiness, [5] Ineligibility, [6] Confirmation | ✅ |
| Endpoints | listTrainingSessions (PUBLISHED), submitWellnessPre, getWellnessPre, updateWellnessPre, submitIneligibilityDeclaration | ✅ |
| Schemas | wellness_assessment, athlete_ineligibility_declaration | ✅ |
| Componentes | card-list, likert-scale, emoji-selector, checkbox, circular-progress, textarea | ✅ |
| Algoritmo | readiness = (sleep + mood + hr + fatigue) / 4 | ✅ |
| Progressive Disclosure | [1] 1 cor + 1 número; [3] dados completos em 2ª camada | ✅ |
| Endpoints Especiais | G-02: submitIneligibilityDeclaration, getIneligibilityStatus | ✅ |

**Ação:** Nenhuma — UIF-002 100% documentado.

---

#### **UIF-003: Coach Review & Intervention** ✅

| Elemento | Detalhes | Status |
|----------|----------|--------|
| Telas | [1] Queue, [2] Dashboard, [3] Attendance, [4] Execution, [5] Feedback, [6] Alerts, [7] Complete | ✅ |
| Endpoints | listSessions (COMPLETED), getSession, listAttendance, recordAttendance, listExecutionRecords, listFeedbackThreads, createFeedbackThread, listAttentionQueue | ✅ |
| Schemas | training_attendance_marked, feedback_thread, attention_queue_item | ✅ |
| Componentes | table, checkbox, card-list, modal, button, textarea | ✅ |
| Endpoints Especiais | G-03: resolveItem, dismissItem, escalateItem; G-04: closeFeedbackThread | ✅ |

**Ação:** Nenhuma — UIF-003 100% documentado.

---

#### **UIF-004: Team Readiness View (Quadra)** ✅

| Elemento | Detalhes | Status |
|----------|----------|--------|
| Telas | [1] Session Quick Access, [2] Team Readiness, [3] Athlete Detail | ✅ |
| Endpoints | listSessions (today), startSession, listSessionAttendance, getWellnessPre (2x) | ✅ |
| Contexto | Quadra — mobile PWA instalada | ✅ |
| Touch Targets | 48 × 48 px mínimo | ✅ |
| Decision Refs | D-UI-SP-01, D-UI-SP-02 | ✅ |
| Bloco Exceção | Topo automático: readiness < 40, inelegibilidade, sem check-in | ✅ |
| Componentes | session-hero-card, athlete-readiness-row, circular-progress, sparkline | ✅ |

**Ação:** Nenhuma — UIF-004 100% documentado.

---

#### **UIF-005: Load Chart (Escritório)** ✅

| Elemento | Detalhes | Status |
|----------|----------|--------|
| Telas | [1] Dashboard (área + linha), [2] Popover detalhe | ✅ |
| Endpoints | getLoadChart (G-05) [team_id, athlete_id, range] | ✅ |
| Schema | load_chart.v1.json com load_points[], readiness_points[] | ✅ |
| Contexto | Escritório — desktop prioritário (degradação mobile aceitável) | ✅ |
| Estados | loading, success, empty (< 3 sessões), loading (on period change) | ✅ |
| Componentes | line-area-chart (Recharts), select, date-range, legend, popover | ✅ |
| Feature | ATL (carga) + readiness (curva verde) + zona de risco (< 40 por 3+ dias) | ✅ |
| Endpoints Especiais | G-05: getLoadChart | ✅ |

**Ação:** Nenhuma — UIF-005 100% documentado.

---

## 📋 DOCUMENTAÇÃO DE SIGN-OFF (3 Documentos Criados)

| Documento | Propósito | Status | Path |
|-----------|-----------|--------|------|
| **✅ SIGN_OFF_CHECKLIST** | Questões detalhadas por role (PO, UX, Eng) | ✅ Criado | `SIGN_OFF_CHECKLIST_v1.1.0.md` |
| **✅ EXECUTIVE_SUMMARY** | Resumo 50.000 pés (1 página, decisão esperada) | ✅ Criado | `EXECUTIVE_SUMMARY_v1.1.0.md` |
| **✅ PRESENTATION_DECK** | Slides (15 slides markdown) | ✅ Criado | `PRESENTATION_DECK_v1.1.0.md` |

**Ação:** Nenhuma — todos os documentos foram criados em 2026-03-17.

---

## 🎯 AÇÕES ESPERADAS ANTES DE SIGN-OFF (PO, UX, ENG LEAD)

### Para: Product Owner 🎯

**Responsabilidade:** Validar viabilidade operacional do product

| # | Ação | Data Target | Status |
|----|------|-------------|--------|
| 1 | Ler [EXECUTIVE_SUMMARY_v1.1.0.md](./EXECUTIVE_SUMMARY_v1.1.0.md) (5 min) | 2026-03-17 EOD | ⏳ PENDENTE |
| 2 | Ler [PRESENTATION_DECK_v1.1.0.md](./PRESENTATION_DECK_v1.1.0.md) (10 min) | 2026-03-17 EOD | ⏳ PENDENTE |
| 3 | Analisar [SIGN_OFF_CHECKLIST_v1.1.0.md](./SIGN_OFF_CHECKLIST_v1.1.0.md) — Seção 2 (UIF Checklist) | 2026-03-18 | ⏳ PENDENTE |
| 4 | Validar: 5 UIFs cobrem fluxo operacional real? | 2026-03-18 | ⏳ PENDENTE |
| 5 | Validar: Readiness score é clinicamente defensável + inelegibilidades cobrem casos? | 2026-03-18 | ⏳ PENDENTE |
| 6 | Assinar Seção 9 do Checklist: **GO** / **NO-GO** / **GO w/conditions** | 2026-03-18 | ⏳ PENDENTE |

**Decisão Esperada:** ✅ GO | ❌ NO-GO | ⚠️ GO w/conditions: _____

---

### Para: UX Designer 🎨

**Responsabilidade:** Validar acessibilidade, responsiveness, design system

| # | Ação | Data Target | Status |
|----|------|-------------|--------|
| 1 | Ler [EXECUTIVE_SUMMARY_v1.1.0.md](./EXECUTIVE_SUMMARY_v1.1.0.md) Seção "Design Tokens & Componentes" (5 min) | 2026-03-17 EOD | ⏳ PENDENTE |
| 2 | Ler [UI_CONTRACT_TRAINING.md](./UI_CONTRACT_TRAINING.md) Parte 1 (Design Principles, Design System, Spacing, Dark Mode) | 2026-03-18 | ⏳ PENDENTE |
| 3 | Validar: WCAG AA labels, focus, color + text + icon em todos 24 telas | 2026-03-18 | ⏳ PENDENTE |
| 4 | Validar: Touch targets 48×48 px (quadra), 44×44 px (escritório) | 2026-03-18 | ⏳ PENDENTE |
| 5 | Validar: Dark mode tokens aplicados (9 cores semânticas) | 2026-03-18 | ⏳ PENDENTE |
| 6 | Validar: Responsiveness 360px → 2560px sem layout quebrado | 2026-03-18 | ⏳ PENDENTE |
| 7 | Assinar Seção 9 do Checklist: **GO** / **NO-GO** / **GO w/conditions** | 2026-03-18 | ⏳ PENDENTE |

**Decisão Esperada:** ✅ GO | ❌ NO-GO | ⚠️ GO w/conditions: _____

---

### Para: Engineering Lead ⚙️

**Responsabilidade:** Validar implementability, endpoint/schema readiness, viabilidade de phases

| # | Ação | Data Target | Status |
|----|------|-------------|--------|
| 1 | Verificar: 34 endpoints em `contracts/openapi/paths/training.yaml` | 2026-03-17 EOD | ⏳ PENDENTE |
| 2 | Verificar: 10 schemas em `contracts/schemas/training/` + validação v7 | 2026-03-17 EOD | ⏳ PENDENTE |
| 3 | Confirmar: Backend stack (Django 5.x + Django Ninja 1.x) per ADR-031 | 2026-03-17 EOD | ⏳ PENDENTE |
| 4 | Confirmar: Frontend stack (Next.js 14 + shadcn/ui + Tailwind) per ADR-030 | 2026-03-17 EOD | ⏳ PENDENTE |
| 5 | Confirmar: PWA + next-pwa viável com stack backend | 2026-03-17 EOD | ⏳ PENDENTE |
| 6 | Revisar: Roadmap Phases 1–7 timeline (~14 semanas) é realista com equipe atual | 2026-03-18 | ⏳ PENDENTE |
| 7 | Assinar Seção 9 do Checklist: **GO** / **NO-GO** / **GO w/conditions** | 2026-03-18 | ⏳ PENDENTE |

**Decisão Esperada:** ✅ GO | ❌ NO-GO | ⚠️ GO w/conditions: _____

---

## ✍️ SIGN-OFF FINAL (3 Signatários)

### Seção para Preenchimento Manual

Este texto deve ser preenchido (copy-paste em 2026-03-18 EOD):

```
---
SIGN-OFF FORMAL — Training UI Contract v1.1.0
Data: 2026-03-18
Status: [GO / NO-GO / GO_WITH_CONDITIONS]
---

### Product Owner
Nome: ____________________________
Decisão: [GO / NO-GO / GO w/conditions: ______]
Assinatura: ____________________________
Data: ____________________________

### UX Designer
Nome: ____________________________
Decisão: [GO / NO-GO / GO w/conditions: ______]
Assinatura: ____________________________
Data: ____________________________

### Engineering Lead
Nome: ____________________________
Decisão: [GO / NO-GO / GO w/conditions: ______]
Assinatura: ____________________________
Data: ____________________________

---

RESULTADO FINAL:
☐ GO (3 GO) → Phase 1 coding starts 2026-03-24
☐ NO-GO (1+ NO-GO) → Retornar para revisão
☐ GO WITH CONDITIONS (todos GO mas com condições) → GO após condição resolvida
```

---

## 🎯 Se GO: Próximos Passos Imediatos

### 2026-03-18 (Reunião de Sign-off)

1. ✍️ **Assinar checklist** (seção 9)
2. 📊 **Documentar resultado** (GO / NO-GO / condições)

### 2026-03-19

1. 📅 **Phase 1 Planning Meeting** (Eng Lead + Squad)
   - Quebrar Phase 1: Session Planning em tasks
   - Estimar story points
   - Designar responsáveis

### 2026-03-24 (MON)

1. 🚀 **Coding Starts — Phase 1**
   - Backend: Django models + Django Ninja endpoints
   - Frontend: Next.js pages + shadcn/ui components
   - QA: Testes unitários + e2e

---

## 📊 Tracking de Progress

**Data:** 2026-03-17 14:30 UTC  
**Última Atualização:** _______  
**Responsável:** Engineering Lead

| Data | Ação | Status | Notas |
|------|------|--------|-------|
| 2026-03-17 | Criar documentos de sign-off (3 docs) | ✅ Completo | SIGN_OFF_CHECKLIST, EXECUTIVE_SUMMARY, PRESENTATION_DECK |
| 2026-03-17 EOD | Eng Lead verifica endpoints (34) + schemas (10) | ⏳ PENDENTE | Check de confirmação esperada |
| 2026-03-18 | PO + UX + Eng Lead leem documentos + decidem | ⏳ PENDENTE | Reunião de sign-off |
| 2026-03-18 EOD | Assinar checklist + documentar resultado | ⏳ PENDENTE | GO / NO-GO / GO w/conditions |
| 2026-03-19 | Phase 1 planning (se GO) | ⏳ PENDENTE | Eng Lead + Squad |
| 2026-03-24 | Coding starts (se GO) | ⏳ PENDENTE | Dev team |

---

## 🎯 Conclusão

### Checklist Pré-Sign-off

- ✅ 4 pré-requisitos técnicos (endpoints, schemas, stacks) — TUDO PRONTO
- ✅ 9 decisões de design documentadas — TUDO PRONTO
- ✅ 5 UIFs completos (24 telas, 34 endpoints) — TUDO PRONTO
- ✅ 3 documentos de sign-off criados — TUDO PRONTO
- ⏳ Assinaturas de PO, UX, Eng Lead — PENDENTE

### Decisão Esperada

**2026-03-18 (amanhã):** ✅ GO | ❌ NO-GO | ⚠️ GO w/conditions?

---

**Document Version:** 1.1.0  
**Last Updated:** 2026-03-17 14:30 UTC  
**Responsibility:** Engineering Lead  
**Escalation:** Product Owner (se bloqueio)
