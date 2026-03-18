---
module: "training"
document: "SIGN_OFF_CHECKLIST"
version: "1.1.0"
date: "2026-03-17"
status: "PENDING_APPROVAL"
reference: "UI_CONTRACT_TRAINING.md v1.1.0"
---

# Sign-off Checklist — UI Contract Training v1.1.0

**Módulo:** training  
**Documento de Referência:** [UI_CONTRACT_TRAINING.md](./UI_CONTRACT_TRAINING.md)  
**Status:** implementation_ready — **Aguardando Aprovação**  
**Versão:** 1.1.0  
**Data:** 2026-03-17

---

## 1. DECISÕES DE DESIGN ARQUITETURAL (D-UI-15 a D-UI-19)

Todas as 9 decisões de design foram documentadas e resolvidas. Cada uma foi aprovada no contexto de seu ADR.

| ID | Decisão | Opção Escolhida | Status | Referência |
|----|---------|-----------------|--------|-----------|
| **D-UI-16** | Plataforma prioritária | **Split por contexto:** modo quadra (mobile) + modo escritório (desktop) | ✅ RESOLVIDA | ADR-030 |
| **D-UI-15** | Funcionamento offline | **Online obrigatório** — Sem cache, erro se desconectado | ✅ RESOLVIDA | ADR-030 |
| **D-UI-SP-01** | Readiness Score como entrada | **Adotado** — Coach vê score de prontidão por atleta antes de iniciar | ✅ RESOLVIDA | TRAIN-DEC-024 |
| **D-UI-SP-02** | Visão de equipe no modo quadra | **Adotado** — Tela primária do coach no mobile exibe equipe inteira + exceções destacadas | ✅ RESOLVIDA | UIF-004 |
| **D-UI-SP-03** | Progressive disclosure no wellness | **Adotado** — Atleta vê 1 cor + 1 número; dados completos em segunda camada | ✅ RESOLVIDA | UIF-002 |
| **D-UI-SP-04** | Gráfico de carga no modo escritório | **Adotado** — ATL/CTL inspirado em TrainingPeaks; desktop only | ✅ RESOLVIDA | UIF-005 |
| **D-UI-17** | Mecanismo de entrega frontend | **PWA (Progressive Web App)** — Único codebase web instalável no celular | ✅ RESOLVIDA | ADR-030 |
| **D-UI-18** | Stack frontend | **Next.js (App Router) + shadcn/ui + Tailwind CSS** | ✅ RESOLVIDA | ADR-031 |
| **D-UI-19** | Gaps G-01 a G-05 no MVP | **Todos no MVP v1.0** — 9 endpoints faltantes adicionados ao OpenAPI | ✅ RESOLVIDA | Parte 8 |

---

## 2. COBERTURA DE FLOWS

5 User Interaction Flows definidos e completamente documentados.

### ✅ UIF-TRAINING-001: Session Planning & Configuration
- **Ator:** Coach (head_coach, assistant_coach)
- **Objetivo:** Criar, configurar e publicar sessão com objetivos e blocos
- **Status:** ✅ 6 telas + 11 endpoints mapeados + estados de transição
- **Checklist — Product Owner:**
  - [ ] Fluxo de criação de sessão é compreensível e viável operacionalmente?
  - [ ] Painel de Objetivos permite vincular automaticamente "necessidades abertas" ao treinamento?
  - [ ] Drag-and-drop de blocos é a melhor forma de organizar fase → exercícios → duração?
  - [ ] Painel de Recomendações é suficiente para coach revisar ~5 recomendações de analytics antes de publicar?
- **Checklist — UX Designer:**
  - [ ] Telas [1], [2], [3], [4], [5], [6] são intuitivas?
  - [ ] Componentes (select, slider, drag-and-drop) seguem design system?
  - [ ] Estados de erro/loading são claros?
  - [ ] Acessibilidade WCAG AA: labels, focus, announce errors?
- **Checklist — Engineering Lead:**
  - [ ] Endpoints (`listTrainingSessions`, `createTrainingSession`, `updateTrainingSession`, `listSessionObjectives`, `createSessionObjective`, `listSessionBlocks`, `addSessionBlock`, `updateSessionBlock`, `deleteSessionBlock`, `reorderSessionBlocks`, `publishTrainingSession`) estão no OpenAPI?
  - [ ] Schemas (`training_session`, `session_objective`, `session_block`) estão em `contracts/schemas/training/`?
  - [ ] Reorder de blocos (PATCH em massa) é possível no backend?

---

### ✅ UIF-TRAINING-002: Athlete Check-in & Readiness Assessment
- **Ator:** Athlete
- **Objetivo:** Auto-avaliação pré-treino (wellness, readiness, inelegibilidades)
- **Status:** ✅ 6 telas + 5 endpoints mapeados + estados de transição
- **Checklist — Product Owner:**
  - [ ] Escalas Likert (sono, humor, FC repouso, fadiga) cobrem bem-estar adequadamente?
  - [ ] Algoritmo de readiness (média aritmética de 4 componentes) é clinicamente defensável?
  - [ ] 5 checkboxes de inelegibilidade capturam todos os cenários de restrição (lesão, testagem, recuperação ativa)?
  - [ ] Modal de confirmação com score exibido é suficiente para validar envio?
- **Checklist — UX Designer:**
  - [ ] **[D-UI-SP-03] Progressive Disclosure:** primeira camada (1 cor + 1 número) é clara na [1]?
  - [ ] [3] Escalas Likert com emoji (mood) são acessíveis e intuitivas?
  - [ ] [4] Visualização de readiness com breakdown é compreensível?
  - [ ] [5] Checkboxes de inelegibilidade + textarea condicional funcionam bem em mobile quadra?
- **Checklist — Engineering Lead:**
  - [ ] Endpoints (`submitWellnessPre`, `getWellnessPre`, `updateWellnessPre`, `submitIneligibilityDeclaration`, `getIneligibilityStatus`) estão no OpenAPI (G-02)?
  - [ ] Schemas (`wellness_assessment`, `athlete_ineligibility_declaration`) criados?
  - [ ] Cálculo de readiness é client-side (sem chamada API cheia)?

---

### ✅ UIF-TRAINING-003: Coach Review & Intervention
- **Ator:** Coach
- **Objetivo:** Revisar execução, feedback de atletas, ações sobre alertas
- **Status:** ✅ 7 telas + 13 endpoints mapeados + estados de transição
- **Checklist — Product Owner:**
  - [ ] Fila de revisão [1] (sessões COMPLETED aguardando coach) é priorizada corretamente?
  - [ ] Attendance Panel [3] permite marcar presença + notas de observação com validação de mínimo de atletas?
  - [ ] Execution Summary [4] mostra diferença estimado vs. real por bloco de forma clara?
  - [ ] Feedback & Interventions [5] permite coach criar threads + fechar com resumo?
  - [ ] Attention Queue [6] mostra alertas (wellness, lesão, performance) com ações: resolver, descartar, escalar?
  - [ ] Workflows de ação (resolver + recolher evidence) são suficientes para compliance?
- **Checklist — UX Designer:**
  - [ ] [1] Queue badges (alertas, atletas) é visual claramente?
  - [ ] [3] Tabela de presença é responsiva (mobile não deve estar aqui, apenas desktop)?
  - [ ] [5] Thread de feedback: layout card → click abre detail é fluido?
  - [ ] [6] Cards de alertas com 3 botões (resolve, dismiss, escalate) é intuitivo?
  - [ ] States (loading, empty, error) bem sinalizados?
- **Checklist — Engineering Lead:**
  - [ ] Endpoints (attendance, execution_records, feedback_threads, attention_queue_items) estão no OpenAPI?
  - [ ] Closing feedback thread (G-04) recebe `resolution_summary` no body?
  - [ ] Ações de attention queue (resolve, dismiss, escalate — G-03) recebem `resolution_evidence`?
  - [ ] Schemas para `training_attendance_marked`, `feedback_thread`, `attention_queue_item` criados?

---

### ✅ UIF-TRAINING-004: Team Readiness View — Modo Quadra
- **Ator:** Coach (modo quadra — mobile instalado via PWA)
- **Objetivo:** Visualizar prontidão de equipe, identificar exceções imediatamente
- **Status:** ✅ 3 telas + 5 endpoints mapeados + states
- **Checklist — Product Owner:**
  - [ ] **[D-UI-SP-01] Bloco de exceção (readiness < 40, inelegibilidade, sem check-in)** no topo é automático e visível?
  - [ ] **[D-UI-SP-02] Visão de equipe é tela primária** (não há drilldown para sessão antes disso)?
  - [ ] Drill-down para atleta individual [3] mostra breakdown de readiness + histórico (últimos 3 scores)?
  - [ ] Toque em thread de feedback navega corretamente para UIF-003?
- **Checklist — UX Designer:**
  - [ ] **Touch targets 48×48 px mínimo** para uso com luvas/mãos suadas?
  - [ ] Cor + ícone + texto para exceções (não apenas cor — WCAG AA)?
  - [ ] Sparkline de histórico é legível em 360px?
  - [ ] Sem navegação confusa: [1] → [2] → [3] é linear?
- **Checklist — Engineering Lead:**
  - [ ] **[D-UI-17] PWA instalável** via next-pwa configurado?
  - [ ] Service worker para UI de erro offline (D-UI-15) — sem cache de dados?
  - [ ] Endpoint `getWellnessPre` (per atleta) retorna readiness breakdown?

---

### ✅ UIF-TRAINING-005: Load Chart — Modo Escritório
- **Ator:** Coach, Coordinator (desktop)
- **Objetivo:** Visualizar carga + recuperação ao longo do tempo para decisões de periodização
- **Status:** ✅ 2 telas + 1 endpoint mapeado (G-05) + tooltip
- **Checklist — Product Owner:**
  - [ ] Gráfico de carga (ATL proxy) × readiness médio (curva verde) é interpretável para tomada de decisão?
  - [ ] Toggle Equipe / Atleta permite comparação 1:1 (equipe agregada vs. indiv)?
  - [ ] Período (7d, 30d, temporada) é suficiente ou faltam opções?
  - [ ] Linha vermelha tracejada (zone de risco: readiness < 40 por 3+ dias) é útil para alertas de descarga?
- **Checklist — UX Designer:**
  - [ ] **Desktop prioritário** — degradação aceitável em mobile (scroll, sem redesenho)?
  - [ ] Gráfico de área é acessível (alt text, cores + padrão, legend)?
  - [ ] Popover no hover/click mostra sessão do dia (title, duração, readiness)?
  - [ ] Legenda clara: qual eixo Y é carga vs. readiness?
- **Checklist — Engineering Lead:**
  - [ ] Endpoint `getLoadChart` (G-05) agregado está no OpenAPI (parâmetros: `team_id`, `athlete_id`, `range`)?
  - [ ] Schema `load_chart.v1.json` criado com `load_points[]` e `readiness_points[]`?
  - [ ] Biblioteca de gráficos: **Recharts** (conforme D-UI-18)?

---

## 3. DESIGN TOKENS & COMPONENTES (WCAG AA)

Todos os componentes definidos com **shadcn/ui + Tailwind CSS** (D-UI-18).

### ✅ Tipografia
- [ ] Escala de tamanhos: `text-[10px]`, `text-xs`, `text-sm`, `text-lg`
- [ ] Pesos: `font-medium`, `font-normal`
- [ ] Fonte base: `font-sans` (Inter → system-ui)
- [ ] Dark mode: variantes `dark:` para todos

### ✅ Cores Semânticas
- [ ] `warning.*` (âmbar): readiness médio, alertas
- [ ] `danger.*` (vermelho): readiness crítico, inelegibilidade, erro
- [ ] `info.ring` (azul): recomendação pendente
- [ ] `text.secondary` (cinza): desabilitado, meta info
- [ ] `semantic.success` (emerald-500 `#10b981`): wellness verde, readiness alto
- [ ] `surface` + `page`: dark mode backgrounds

### ✅ Componentes Base (Tabela 3.1)
- [ ] `emptyStateCard`: ícone + título + descrição
- [ ] `alertBanner`: sessão aguardando revisão, wellness em risco
- [ ] `microButton`: aceitar recomendação, marcar presença
- [ ] `compactPill`: status badges, contadores
- [ ] `error-state`: carregamento falho + retry
- [ ] `spinner`: loading states
- [ ] `wellness-indicator`: ponto 12px (verde/âmbar/vermelho)
- [ ] `circular-progress`: readiness score visual
- [ ] `athlete-readiness-row`: nome + score + status + exceção
- [ ] `sparkline`: miniatura histórico 3 pontos
- [ ] `line-area-chart`: Recharts (load chart)
- [ ] `draggable-list`: dnd-kit (reorder blocos)

### ✅ Acessibilidade (WCAG 2.1 AA)
- [ ] Todos inputs têm `<label>` ou `aria-label` visível
- [ ] Erros anunciados para screen readers
- [ ] Focus visível em todos elementos interativos
- [ ] Cor não é único meio de conveyance (ícones + textos)
- [ ] Touch targets: 48×48 px (quadra), 44×44 px (escritório)

### ✅ Dark Mode
- [ ] Toda tela suporta `dark:` classes
- [ ] Opacidades ajustadas (ex: `dark:bg-red-900/20`)
- [ ] Contrast ratio ≥ 4.5:1 (normal text), ≥ 3:1 (large text)

---

## 4. ENDPOINTS MAPEADOS & GAPS (G-01 a G-05)

### Todos os Gaps Resolvidos em 2026-03-17

| Gap | Afeta UIF | Endpoints Adicionados | Status |
|-----|-----------|-------------------|--------|
| **G-01** | UIF-001 [5] Recommendations | `listRecommendations`, `acceptRecommendation`, `dismissRecommendation` | ✅ RESOLVIDA |
| **G-02** | UIF-002 [5] Ineligibility | `submitIneligibilityDeclaration`, `getIneligibilityStatus` | ✅ RESOLVIDA |
| **G-03** | UIF-003 [6] Attention Queue | `resolveAttentionQueueItem`, `dismissAttentionQueueItem`, `escalateAttentionQueueItem` | ✅ RESOLVIDA |
| **G-04** | UIF-003 [5] Feedback Threads | `closeFeedbackThread` | ✅ RESOLVIDA |
| **G-05** | UIF-005 [1] Load Chart | `getLoadChart` | ✅ RESOLVIDA |

**Total de Endpoints Mapeados:** 34 (por UIF)

- [ ] **Product Owner** — Todos os endpoints refletem a realidade operacional do handebol?
- [ ] **Engineering Lead** — Todos os 34 endpoints estão no OpenAPI (`contracts/openapi/paths/training.yaml`)?
- [ ] **Engineering Lead** — Schemas JSON necessários estão criados em `contracts/schemas/training/`?

---

## 5. DATA CONTRACTS (JSON Schemas)

Todos os schemas referenciados estão em `contracts/schemas/training/`.

| Schema | Referência em | Status |
|--------|------------|--------|
| `training_session` | UIF-001 [2], [3], [4] | ✅ Existem |
| `session_objective` | UIF-001 [3] | ✅ Existem |
| `session_block` | UIF-001 [4] | ✅ Existem |
| `training_attendance_marked` | UIF-003 [3] | ✅ Existem |
| `wellness_assessment` | UIF-002 [3], UIF-004 [3] | ✅ Existem |
| `athlete_ineligibility_declaration` | UIF-002 [5], G-02 | ✅ Existem (G-02) |
| `feedback_thread` | UIF-003 [5] | ✅ Existem |
| `attention_queue_item` | UIF-003 [6] | ✅ Existem |
| `recommendation` | UIF-001 [5], G-01 | ✅ Existem (G-01) |
| `load_chart` | UIF-005 [1], G-05 | ✅ Existem (G-05) |

- [ ] **Engineering Lead** — Todos os 10 schemas são válidos JSON Schema v7 (ou draft)?
- [ ] **Engineering Lead** — Tipo de resposta de `getLoadChart` (G-05) inclui `load_points` e `readiness_points`?

---

## 6. ROADMAP DE IMPLEMENTAÇÃO (7 Phases)

Conforme **Parte 7** do UI Contract, fases ordenadas do core ao polish.

| Phase | Objetivo | Aprox. Duração | Bloqueado por |
|-------|----------|--|--|
| **Phase 1** | Session Planning core (UIF-001 [1]–[4]) | 2 semanas | Nada (pode começar após sign-off) |
| **Phase 2** | Athlete Check-in (UIF-002 + G-02) | 2 semanas | Phase 1 parcialmente (schemas) |
| **Phase 3** | Coach Review (UIF-003 + G-03 + G-04) | 3 semanas | Phase 2 (schemas de attendance) |
| **Phase 4** | Recommendations (UIF-001 [5] + G-01) | 1 semana | Phase 1 |
| **Phase 5** | Modo Quadra (UIF-004) | 2 semanas | Phase 2 (PWA + wellness) |
| **Phase 6** | Load Chart (UIF-005 + G-05) | 2 semanas | Todas as fases anteriores (agregação) |
| **Phase 7** | Polish (notifications, filters, exports, PWA) | 2 semanas | Phases 1–6 |

**Total estimado: 14–16 semanas para MVP v1.0 completo (7 phases).**

- [ ] **Engineering Lead** — Estimativas de duração por phase são viáveis com equipe atual?
- [ ] **Product Owner** — Priorização de phases alinha com roadmap de negócio?

---

## 7. DECISÕES CRÍTICAS (ADRs & Resoluções)

Todas as decisões humanas bloqueantes foram resolvidas.

| Decisão | Status | Referência |
|---------|--------|-----------|
| **D-UI-15:** Online obrigatório (sem cache offline) | ✅ RESOLVIDA | Parte 0, D-UI-15 |
| **D-UI-16:** Split modo quadra (mobile) × escritório (desktop) | ✅ RESOLVIDA | Parte 0, D-UI-16 |
| **D-UI-17:** PWA + next-pwa para entrega | ✅ RESOLVIDA | Parte 0, D-UI-17, ADR-030 |
| **D-UI-18:** Next.js + shadcn/ui + Tailwind CSS | ✅ RESOLVIDA | Parte 0, D-UI-18, ADR-031 |
| **D-UI-19:** Gaps G-01 a G-05 são MVP (não future) | ✅ RESOLVIDA | Parte 0, Parte 8 |
| **TRAIN-DEC-006:** Session configuration format (title, focus %) | ✅ RESOLVIDA | Parte 5, UIF-001 [2] |
| **TRAIN-DEC-024:** Athlete check-in form (wellness + readiness) | ✅ RESOLVIDA | Parte 5, UIF-002 |
| **TRAIN-DEC-025:** Coach review + feedback + interventions | ✅ RESOLVIDA | Parte 5, UIF-003 |

---

## 8. REVISÃO ARQUITETURAL COMPLETA

Análise de consistência entre documentação, OpenAPI e schemas.

- [ ] **Engineering Lead** — OpenAPI `training.yaml` está atualizado com 9 endpoints novos (G-01 a G-05)?
- [ ] **Engineering Lead** — Todos os schemas em `contracts/schemas/training/` validam contra OpenAPI `$ref`?
- [ ] **Engineering Lead** — Não há conflito entre `training_session` schema e OpenAPI definitions?
- [ ] **Product Owner** — Flows de UIF-001 a UIF-005 respeitam invariantes de domínio do treinamento (ex: readiness ∈ [0,100])?

---

## 9. OBSERVAÇÕES FINAIS & RECOMENDAÇÕES

### ✅ Pontos Fortes do Contrato

1. **Completude:** Todas as 5 UIFs documentadas com 6+ telas cada, states, componentes, endpoints
2. **Cobertura de Decisões:** 9 decisões arquiteturais esclarecidas (D-UI-15 a D-UI-19)
3. **Gaps Resolvidos:** G-01 a G-05 (9 endpoints) já adicionados ao OpenAPI
4. **Acessibilidade:** WCAG AA aplicado, touch targets aumentados para quadra
5. **Stack Decidido:** Next.js + shadcn/ui + Tailwind Solido para v1.0
6. **Roadmap:** Phases 1–7 desagregadas com durações estimadas
7. **Component Design System:** Tokens, dark mode, responsive behavior claros

### ⚠️ Dependências Críticas Antes de Go/No-Go

1. **OpenAPI Atualizado:** Todos os 34 endpoints (34 em UIF-001, 5 em UIF-002, etc.) **devem estar no `training.yaml`** antes do sign-off
2. **Schemas Criados:** 10 schemas (`training_session`, `recommendation`, `load_chart`, etc.) **devem estar validados**
3. **Backend Stack Confirmado:** Django 5.x + Django Ninja 1.x (ADR-031) — **confirmar com Engineering Lead que stack foi decidido**
4. **PWA & Service Worker:** next-pwa e service worker para error UI offline **devem estar configurados**

### 🎯 Recomendação para Sign-off

**GO** para implementação (Phases 1–7) **se e somente se:**

1. ✅ Produto Owner aprova 5 UIFs + decisions (Seção 1–2)
2. ✅ UX Designer aprova design tokens, acessibilidade, responsiveness (Seção 3)
3. ✅ Engineering Lead confirma:
   - Todos 34 endpoints no OpenAPI
   - Todos 10 schemas criados
   - Backend stack (Django 5.x + Django Ninja 1.x) aprovado
   - PWA + next-pwa + service worker possível com stack escolhido
4. ✅ Roadmap (Seção 6) alinha com timeline de negócio

---

## Próximas Ações Imediatas

| Ação | Responsável | Data Target |
|------|-------------|-----------|
| Validate OpenAPI endpoints (34 total) | Engineering Lead | 2026-03-17 EOD |
| Create/validate 10 JSON schemas | Engineering Lead | 2026-03-17 EOD |
| Review WCAG AA + touch targets | UX Designer | 2026-03-17 |
| Confirm backend stack (Django 5.x + Django Ninja) | Engineering Lead | 2026-03-17 |
| Final GO/NO-GO decision | PO + UX + Engineering Lead | 2026-03-18 AM |
| Promote to `implementation_ready` (if GO) | Engineering Lead | 2026-03-18 |
| Start Phase 1 coding | Engineering Team | 2026-03-18 or later |

---

## Signatários

**Uma vez preenchido, este checklist confirma que o UI contract v1.1.0 foi reviado e aprovado por all stakeholders.**

### Product Owner
- **Nome:** ___________________________
- **Assinatura:** ___________________________
- **Data:** ___________________________
- **Decisão:** [ ] GO | [ ] NO-GO | [ ] GO with conditions (specify):

### UX Designer
- **Nome:** ___________________________
- **Assinatura:** ___________________________
- **Data:** ___________________________
- **Decisão:** [ ] GO | [ ] NO-GO | [ ] GO with conditions (specify):

### Engineering Lead
- **Nome:** ___________________________
- **Assinatura:** ___________________________
- **Data:** ___________________________
- **Decisão:** [ ] GO | [ ] NO-GO | [ ] GO with conditions (specify):

---

**Document Version:** 1.1.0  
**Last Updated:** 2026-03-17  
**Authority:** UI Contract Training Module (MODULE_REGISTRY.yaml — training = validated_contract)
