---
module: "training"
system_scope_ref: "../../../_canon/SYSTEM_SCOPE.md"
handball_rules_ref: "../../../_canon/HANDBALL_RULES_DOMAIN.md"
handball_semantic_applicability: true
contract_path_ref: "../../../../contracts/openapi/paths/training.yaml"
schemas_ref: "../../../../contracts/schemas/training/"
type: "ui-contract"
ui_contract_guide_ref: "../../../../docs/_canon/UI_CONTRACT_GUIDE.md"
---

# UI_CONTRACT_TRAINING.md

**Módulo:** training
**Status:** implementation_ready (pendente sign-off)
**Last Updated:** 2026-03-17
**Version:** 1.2.0 (com HB Pro Coach)
**Governance IDs:** UIF-TRAINING-001, UIF-TRAINING-002, UIF-TRAINING-003, UIF-TRAINING-004, UIF-TRAINING-005, UIF-TRAINING-006

---

## Overview

Contrato de UI para o módulo **training** (treinamento) em HB Track.

Define 5 principais user interaction flows:
1. **Session Planning & Configuration** (Coach) — criar e configurar sessões
2. **Athlete Check-in & Readiness** (Athlete) — auto-avaliação pré-treino
3. **Coach Review & Intervention** (Coach) — análise e feedback pós-sessão
4. **Team Readiness View** (Coach) — visualizar equipe + prontidão em modo quadra (mobile)
5. **HB Pro Coach — Virtual Assistant Chat** (Athlete) — assistente de IA para respostas sobre treino, exercícios, dicas de preparação e sugestão de treinos compensatórios

Cada flow mapeia:
- **Screens** (telas primárias e transições)
- **States** (loading, success, error, empty, disabled)
- **Components** (reutilizáveis do design system)
- **Actions** (operações e submissões)
- **Data Contracts** (referências a JSON Schemas)
- **Decision Refs** (ADRs/TRAINs de design)

---

## Parte 0: Decisões de Design Arquitetural

Decisões tomadas pelo Product Owner e registradas antes da implementação.
Todas as telas e flows abaixo devem respeitar estas decisões.

| ID | Decisão | Opção Escolhida | Referência de Mercado |
|----|---------|-----------------|----------------------|
| D-UI-16 | Plataforma prioritária | **C — Split por contexto**: "modo quadra" (mobile) e "modo escritório" (desktop) são experiências distintas | Hudl, Catapult, Teamworks |
| D-UI-15 | Funcionamento offline | **A — Online obrigatório**. Sem cache offline. Conexão perdida → error state | — |
| D-UI-SP-01 | Readiness Score como entrada | **Adotado**: antes de iniciar qualquer sessão, o coach vê um score de prontidão por atleta (0–100). Quem está em risco aparece em destaque automaticamente | Whoop, Kitman Labs |
| D-UI-SP-02 | Visão de equipe no modo quadra | **Adotado**: a tela principal do coach no mobile exibe a equipe inteira, não um atleta individual. Exceção (inelegível, readiness baixo) aparece no topo com destaque cromático | Catapult, Kinexon |
| D-UI-SP-03 | Progressive disclosure no wellness | **Adotado**: o atleta vê apenas uma cor (verde / âmbar / vermelho) na tela inicial. Os dados completos ficam um toque abaixo. Reduz fricção e aumenta taxa de preenchimento | Whoop |
| D-UI-SP-04 | Gráfico de carga no modo escritório | **Adotado**: o coordinator/coach vê uma curva de carga × recuperação ao longo da temporada (inspirada no modelo ATL/CTL do TrainingPeaks). Desktop only | TrainingPeaks |
| D-UI-17 | Mecanismo de entrega do frontend | **B — PWA (Progressive Web App)**: único codebase web instalável no celular. Modo quadra = PWA com touch otimizado (48px targets). Modo escritório = mesmo app no desktop. Sem app nativo separado na v1. | Times europeus de menor orçamento; padrão emergente |
| D-UI-18 | Stack frontend | **C — Next.js (App Router) + shadcn/ui + Tailwind CSS**: SSR nativo para performance em redes de ginásio, roteamento file-based, shadcn/ui para componentes acessíveis (WCAG AA) sem lock-in, Tailwind para estilos. Gráficos: Recharts. Drag-and-drop: dnd-kit. PWA via next-pwa. | Next.js (Vercel), padrão emergente em plataformas de dados esportivos |
| D-UI-19 | Escopo MVP dos gaps G-01 a G-05 | **Todos no MVP (v1.0)**: G-01 (recomendações), G-02 (inelegibilidade), G-03 (ações de attention queue), G-04 (fechar feedback thread), G-05 (load chart). Os 9 endpoints faltantes devem ser adicionados ao OpenAPI antes da implementação. | — |
| D-UI-20 | HB Pro Coach — Mode e contexto | **Adotado**: Chat modal em canto inferior direito, acessível do contexto de atleta (UIF-TRAINING-002 e além). Powered by Feature Store interno (integração com ai_ingestion) + regras especializadas em handebol. Coach entende cada atleta a partir de seus dados históricos (treinos, wellness, medical, analytics). Sugestões de treino precisam aprovação do treinador (workflow assíncrono). | Catapult Analytics (AI Coach), Kitman Labs (Data-driven), TrainingPeaks (comissão técnica) |
| D-UI-21 | HB Pro Coach — Comportamento (Feature Store + Regras) | **Adotado**: Respostas focadas em (1) handebol + posição + categoria etária do atleta, (2) explicações dos exercícios praticados + histórico pessoal, (3) wellness + recuperação + dados médicos integrando `medical`, `wellness`, `analytics`, (4) nutrição + descanso adaptado à fadiga detectada. **Inteligência contextual:** Coach acessa Feature Store para cada resposta — \"Vi que você treinou força 3x essa semana, então recomendo recuperação hoje\". **Compreensão total de linguagem natural** — entende abreviações sem apontar ou corrigir. Rejeita palavrões e off-topic com resposta gentil. Comunica elevando autoestima com elogios genuínos baseados em DADOS (progresso documentado, aderência, melhoria). Incentiva próxima mensagem. Respeta age-group. **Sem foto/vídeo na v1**. Dados integrados: `training` (sessões faltadas, feedback), `wellness` (readiness, fadiga, lesões), `medical` (restrições, lesões), `analytics` (sinais de desempenho). | Catapult Analytics (Sports Science), Kitman Labs (Clube com IA interna), TrainingPeaks (Comissão Técnica) |

### Regras derivadas das decisões acima

- **D-UI-16 → Regra de contexto:** Toda tela deve ser classificada em `context: quadra` (mobile obrigatório, toque otimizado) ou `context: escritório` (desktop prioritário, pode funcionar em mobile com degradação aceitável).
- **D-UI-15 → Regra offline:** O estado `offline` não é uma feature — é um error state. Exibir mensagem de erro + botão "Tentar novamente". Nenhum dado deve ser salvo localmente.
- **D-UI-SP-02 → Regra de visão:** Telas de quadra do coach mostram equipe → atleta (drill-down). Telas de escritório podem mostrar atleta diretamente em listas.
- **D-UI-SP-03 → Regra de disclosure:** A primeira camada visual do atleta é sempre 1 cor + 1 número. Dados brutos ficam na segunda camada (tap/click para expandir).
- **D-UI-17 → Regra de entrega:** O frontend é uma PWA única. Não existe app nativo separado na v1. O modo quadra é entregue via PWA instalada no celular do coach/atleta. O modo escritório é a mesma PWA no desktop. Service workers são configurados para UI de erro offline (não para cache de dados — D-UI-15).
- **D-UI-18 → Regra de componentes:** Todos os componentes do UI contract devem ser implementados com shadcn/ui + Tailwind CSS. Gráficos (UIF-005) usam Recharts. Drag-and-drop (UIF-001 blocos) usa dnd-kit. Nenhuma outra biblioteca de componentes deve ser introduzida sem ADR.
- **D-UI-20 → Regra de HB Pro Coach (Acessibilidade + Inclusividade):** HB Pro Coach é um componente de chat modal tipo chat bubble, aberto via botão no header/footer do contexto do atleta (canto inferior direito). Suporta dark mode (classes `dark:`). Coach é especialista em CADA ATLETA — consulta Feature Store interno com dados históricos (treinos faltados, wellness pré/pós, lesões, feedback do treinador, progresso de força/técnica). Respostas sempre contextualizadas no histórico pessoal do atleta e adaptadas à sua posição + categoria etária. O coach **entende naturalmente a linguagem informal dos atletas** — vc, pq, oq, taum, msm, etc — e responde fluentemente **sem apontar ou corrigir erros de digitação**. Comunicação **elevadora de autoestima** com elogios genuínos baseados em dados reais (\"Você progrediu 12% em velocidade esta semana!\", \"Sua dedicação aos treinos é impressionante!\"). Palavrões e off-topic → resposta com redirecionamento educado (e.g., \"Sou coach de handebol, posso ajudar com treino!\"). Comunicação age-appropriate (linguagem, tone e incentivos adaptados à idade do atleta). **Sem dependência externa** — tudo roda no HB Track, respeitando privacidade dos dados (LGPD).
- **D-UI-21 → Regra de Workflow de Treino Sugerido (Feature Store):** Quando atleta solicita "sugestão de treino" (missing session ou objetivo específico), HB Pro Coach: (1) consulta Feature Store do atleta (treinos recentes, gaps, wellness, lesões, restrições médicas), (2) aplica regras especializadas em handebol para sugerir estrutura: nome + duração + focos principais (escolhido via regras, não template genérico), (3) sistema envia notificação assíncrona ao treinador com [treino_sugerido + features_calculadas + contexto_atleta + wellness_pré + histórico_recente] + botões "Aprovar" / "Recusar", (4) treinador responde via notificação (AsyncAPI event), (5) atleta tem acesso ao treino aprovado com status "Aprovado pelo Coach [Nome]". Se recusado: notificação ao atleta explicando que o treinador desaprovou + sugestão para conversar com o coach. **Rastreamento:** Cada sugestão é auditada no Feature Store para medir aderência e eficácia das recomendações.

---

## Parte 1: Fundamentos

### Design Principles (Training-Specific)
- **Transparency:** Coach vê toda evidência subjacente às recomendações
- **Coach-in-Loop:** Todo recomendação de analytics requer revisão coach
- **Athlete Agency:** Atleta pode marcar inelegibilidade/restrições
- **Continuity:** Sessões mantêm contexto histórico (snapshots)
- **Feedback Loop:** Conversas coach-atleta são rastreáveis e contextualizadas

### Design System
> Tokens canônicos do projeto. Este contrato os referencia — não os redefine.

#### Tipografia
| Uso | Classe Tailwind | Token |
|-----|----------------|-------|
| Heading de seção / título de tela | `text-lg font-medium` | `fontSize.lg + fontWeight.medium` |
| Subheading / label de painel | `text-sm font-medium` | `fontSize.sm + fontWeight.medium` |
| Corpo / descrição | `text-sm` | `fontSize.sm` |
| Badge / meta info | `text-xs` | `fontSize.xs` |
| Micro label (contadores compactos) | `text-[10px] font-medium` | `fontSize.micro` |
| Fonte base | `font-sans` (Inter → system-ui) | `fontFamily.sans` |

#### Cores semânticas
| Token | Light | Dark | Uso neste módulo |
|-------|-------|------|-----------------|
| `warning.bg/border/text` | amber-50 / amber-200 / amber-700 | amber-900/20 / amber-800 / amber-300 | Readiness médio (40–69), alertas de bem-estar, sessão aguardando revisão |
| `danger.bg/border/text` | red-50 / red-200 / red-700 | red-900/20 / red-800 / red-400 | Readiness crítico (< 40), inelegibilidade, erro de operação |
| `info.ring` | blue-400 (`rgb(96 165 250)`) | — | Recomendação pendente revisão, destaque contextual temporário |
| `text.secondary` | slate-500 | slate-400 | Estados desabilitados, campos de leitura, meta info |
| `border` | slate-200 | slate-800 | Bordas de card, separadores de painel |
| `surface` | `#ffffff` | `#0f0f0f` | Fundo de cards, modais, painéis |
| `page` | `#f6f6f8` | `#111621` | Fundo da página |

> Token `semantic.success`: usar `emerald-500` (`#10b981`) como cor principal do `<wellness-indicator>` verde e `<circular-progress>` de readiness alto.

#### Componentes base
| Padrão | Uso neste módulo | Tailwind / token |
|-----------------|-----------------|-----------------|
| `emptyStateCard` | Empty states de todas as telas (sem sessões, sem atletas, sem alertas) | `p-12 rounded-lg border bg-surface` · ícone `w-16 h-16 rounded-full` |
| `alertBanner` | Sessão aguardando revisão (UIF-003), wellness em risco | `px-4 py-2 rounded-lg text-sm` · cores `warning.*` |
| `microButton` | Ações compactas inline (aprovar recomendação, marcar presença) | `px-2 py-1 text-[10px] font-medium rounded shadow-sm` |
| `compactPill` | Contadores de drafts, status da sessão | `px-3 py-2 rounded-md w-fit` |
| Error card | Estados de erro de carregamento em todas as telas | `border rounded-lg` · cores `danger.*` |

#### Spacing e radius
- Espaçamentos seguem grade de 4px: `gap-2` (8px), `gap-3` (12px), `p-4` (16px), `p-6` (24px), `p-12` (48px)
- Cards e painéis: `rounded-lg` (12px)
- Badges e pills: `rounded-md` (8px)
- Ícones circulares: `rounded-full`
- Sombras: `shadow-sm` apenas — sem sombras fortes

#### Dark mode
- Toda tela suporta dark mode via classes `dark:` do Tailwind
- Semânticas usam variantes com opacidade (ex: `dark:bg-red-900/20`)
- Superfícies: `dark:bg-[#0f0f0f]`; página: `dark:bg-[#111621]`

### States (Global)
Todos os flows suportam os estados abaixo:

| Estado | Padrão visual |
|--------|---------------------------|
| **loading** | Spinner inline (`<spinner>`) — sem skeleton por padrão |
| **success** | Feedback positivo via toast ou modal — sem cor especial de fundo |
| **error** | Error card semântico (`danger.*`) — título + descrição + botão "Tentar novamente" |
| **empty** | `emptyStateCard` — ícone circular + título `text-lg font-medium` + descrição `text-sm` |
| **disabled** | `text.secondary` (slate-500 / slate-400) — sem interação |
| **offline** | Error card `danger.*` — mensagem "Sem conexão" + botão retry. Sem fallback local (D-UI-15) |

---

## Parte 2: UI Flows

### UIF-TRAINING-001: Session Planning & Configuration

**Ator:** Coach (head_coach, assistant_coach)  
**Objetivo:** Criar, configurar e publicar sessão de treino com objetivos e blocos  
**Frequência:** Diária/semanal  
**Decision Refs:** TRAIN-DEC-006, TRAIN-DEC-007, TRAIN-DEC-008

#### Screens

```
[1] Session List Screen
    ↓ (click "New Session" or edit existing)
[2] Session Header Form
    ├─ [3] Objectives Panel
    ├─ [4] Session Blocks Builder
    └─ [5] Recommendations Review (if auto-generated)
    ↓ (click "Publish")
[6] Session Published Confirmation
```

#### Screen Definitions

**[1] Session List Screen**
- Card per session com status badge (DRAFT, SCHEDULED, IN_PROGRESS, COMPLETED, ARCHIVED)
- Filter by date range, team, status
- Action buttons: New, Edit, View, Archive
- Empty State: "Nenhuma sessão. Criar primeira sessão."

**Components:**
- `<table>` or `<card-list>` (responsive)
- `<status-badge status="DRAFT" />`
- `<button label="Nova Sessão" variant="primary" />`
- `<input type="date-range" />` (filters)

**Data:** Referencia `contracts/schemas/training/training_session.v1.json`

---

**[2] Session Header Form**
- Team selector (dropdown, default = current team)
- Session title (text input)
- Scheduled date/time (datetime picker)
- Duration estimate (number input, minutes)
- Focus percentages (7 dimensions: technical, tactical, physical, mental, recovery, team, individual)

**Components:**
- `<select>` (team dropdown)
- `<input type="text" placeholder="Título da sessão" />`
- `<input type="datetime-local" />`
- `<input type="number" min="30" max="180" />` (duration)
- `<slider>` × 7 (focus percentages, must sum ≤ 100%)

**Validation:**
- Title required, max 100 chars
- Date must be future date (or today)
- Duration: 30–180 minutes
- Focus sum validator (R2 from DB schema: sum ≤ 100%)

**Data:** Subset of `training_session` schema (create_input payload)

**State:** success|error|loading

---

**[3] Objectives Panel**
- List existing session objectives (origin, status, achieved flag)
- Add objective form:
  - Objective type (dropdown: competitive_focus, development_goal, need_detected, coach_rationale)
  - If need_detected: auto-populate from need_detected that are OPEN
  - Objective description (text area)
- Remove objective button

**Components:**
- `<chip>` with origin color code
- `<select>` (objective type dropdown)
- `<select>` (need_detected if applicable, filtered by OPEN status)
- `<textarea>` (objective description)
- `<button>` (remove)

**Data:** References `contracts/schemas/training/session_objective.v1.json`

**State:** loading (while fetching open needs), success, error

---

**[4] Session Blocks Builder**
- Table/drag-and-drop list of session blocks
- Per block: phase (ACTIVATION, CONDITIONING, SKILL_WORK, STRENGTH, RECOVERY), exercises, duration
- Add block → form opens
- Remove block → confirmation modal
- Reorder (drag-and-drop)

**Components:**
- `<draggable-list>`
- `<select>` (phase enum)
- `<input>` (duration)
- `<button>` (add/remove)

**Data:** References `contracts/schemas/training/session_block.v1.json`  
**Validation:** At least 1 block, total duration matches form

---

**[5] Recommendations Review (Optional)**
Appears only if `training_session.analytics_recommendations > 0`

- Cards per recommendation (ID, rule, action type, status)
- Accept/Dismiss buttons per recommendation
- Status changes async

**Components:**
- `<card>` (per recommendation)
- `<button label="Aceitar" variant="success" />`
- `<button label="Rejeitar" variant="secondary" />`
- `<spinner>` (loading on action)

**Data:** References `contracts/schemas/training/recommendation.v1.json`  
**State:** loading, success, error

---

**[6] Session Published Confirmation**
- Modal: "Sessão publicada com sucesso"
- Summary: title, date, num objectives, num blocks
- Actions: "Ver Sessão" (navigate to [1]), "Criar Outra" (reset [2])

**Components:**
- `<modal>` with success icon
- `<button>` (primary, secondary)

**State:** success

---

#### Endpoint Map (UIF-001)

| Tela | Ação do Usuário | operationId | Método |
|------|----------------|-------------|--------|
| [1] Session List | Carregar lista | `listTrainingSessions` | GET |
| [2] Session Header Form | Criar sessão | `createTrainingSession` | POST |
| [2] Session Header Form | Editar sessão | `updateTrainingSession` | PATCH |
| [3] Objectives Panel | Listar objetivos | `listSessionObjectives` | GET |
| [3] Objectives Panel | Criar objetivo | `createSessionObjective` | POST |
| [4] Blocks Builder | Listar blocos | `listSessionBlocks` | GET |
| [4] Blocks Builder | Adicionar bloco | `addSessionBlock` | POST |
| [4] Blocks Builder | Editar bloco | `updateSessionBlock` | PATCH |
| [4] Blocks Builder | Remover bloco | `deleteSessionBlock` | DELETE |
| [4] Blocks Builder | Reordenar blocos | `reorderSessionBlocks` | PATCH |
| [6] Published Confirmation | Publicar sessão | `publishTrainingSession` | POST |
| [5] Recommendations | Listar recomendações | ⚠️ `MISSING` — ver §8 | — |
| [5] Recommendations | Aceitar recomendação | ⚠️ `MISSING` — ver §8 | — |
| [5] Recommendations | Rejeitar recomendação | ⚠️ `MISSING` — ver §8 | — |

---

#### State Transitions

```
[1] Session List
    → loading (fetch sessions)
    → success (render list)
    → error (API failure) → retry button

[2] Session Header Form
    → loading (validate)
    → error (validation failed) → highlight field
    → success (validated)

[3] Objectives Panel
    → loading (fetch open needs)
    → success (render objectives)
    → error (API failure)

[4] Session Blocks Builder
    → success (render blocks, validate total duration)
    → error (validation failed) → tooltip

[5] Recommendations Review
    → loading (fetch recommendations if any)
    → empty (no recommendations)
    → success (render cards)
    → loading (on accept/dismiss action)

[6] Published Confirmation
    → success (modal)
    → (navigate to [1])
```

---

### UIF-TRAINING-002: Athlete Check-in & Readiness Assessment

**Ator:** Athlete  
**Objetivo:** Responder check-in pré-treino (readiness, wellness, ineligibilities)  
**Frequência:** Diária (cada dia com sessão agendada)  
**Decision Refs:** TRAIN-DEC-024

#### Screens

```
[1] Scheduled Sessions List
    ↓ (click session card)
[2] Pre-Training Check-in Form
    ├─ [3] Wellness Assessment
    ├─ [4] Readiness Score
    └─ [5] Ineligibility Declaration
    ↓ (click "Confirmar")
[6] Check-in Submitted Confirmation
```

#### Screen Definitions

**[1] Scheduled Sessions List**
- Cards: scheduled sessions for today/upcoming
- Per card: title, time, coach
- **[D-UI-SP-03] Primeira camada (progressive disclosure):** indicador cromático de wellness na sessão do dia
  - `verde` → readiness ≥ 70 (ou check-in ainda não feito: exibir "Fazer check-in" em âmbar)
  - `âmbar` → readiness 40–69
  - `vermelho` → readiness < 40 ou inelegibilidade declarada
  - Um toque no card → expande segunda camada (dados completos do check-in)
- "Your Status" badge (not_checked_in, checked_in)
- Tap para abrir o check-in form

**Components:**
- `<card-list>`
- `<wellness-indicator color="green|amber|red" />` (ponto colorido 12px + label de status)
- `<status-badge status="AWAITING_CHECK_IN" color="warning" />`
- `<button label="Fazer check-in" />`

**Contexto:** `context: quadra` (mobile obrigatório — D-UI-16)
**State:** loading, empty ("Nenhuma sessão agendada para hoje"), success

---

**[2] Pre-Training Check-in Form**
- Hero section: session title, time, coach name
- Mandatory completion indicator (e.g., "3 de 3 seções completas")

**Components:**
- `<header>` (session info)
- `<progress-bar value="66%" />`

---

**[3] Wellness Assessment**
Likert 5-point scales (muito ruim, ruim, neutro, bom, muito bom):
- Sleep quality (0–10 visual scale, convert to enum)
- Mood (emoji selector: 😢 😐 😊)
- Resting HR (number input, validation: 40–120 bpm for handball)
- Perceived fatigue from yesterday (0–10 slider)
- Injury/pain (checkbox: "Tenho dor/lesão" → open textarea)

**Components:**
- `<likert-scale>` (5 items)
- `<emoji-selector>`
- `<input type="number">`
- `<slider>`
- `<checkbox>` + conditional `<textarea>`

**Validation:**
- All mandatory
- HR: 40–120 bpm

**Data:** `contracts/schemas/training/wellness_assessment.v1.json`

---

**[4] Readiness Score**
- Computed readiness score (0–100) displayed as:
  - Large circular progress
  - Color: green (high), amber (moderate), red (low)
  - Breakdown (read-only): sleep_quality (25%), mood (25%), resting_hr (25%), yesterdays_fatigue (25%)

**Components:**
- `<circular-progress>` (diameter: 120px)
- `<legend>` (breakdown)

**Algorithm:**
```
readiness_score = (sleep_q[0-10] + mood[0-10] + (120-resting_hr)/8 + (10-fatigue[0-10])) / 4
= (s + m + h + f) / 4, where s,m,h,f in 0-100
```

**State:** success (auto-computed after [3] validation)

---

**[5] Ineligibility Declaration**
Checkboxes (multi-select):
- "Tenho consulta médica hoje"
- "Estou machucado/lesionado"
- "Recuperação ativa apenas (sem atividade competitiva)"
- "Estou testando (anti-doping, competição)"
- "Outro (pedir permissão coach)" → opens reason textarea

If any checked:
- Ineligibility reason stored
- Coach sees "athlete flagged as ineligible" in session review
- Prescription may auto-adjust (descale)

**Components:**
- `<checkbox>` × 5
- Conditional `<textarea>` for "Outro"

**Data:** `contracts/schemas/training/athlete_ineligibility_declaration.v1.json`

---

**[6] Check-in Submitted Confirmation**
- Modal: "Check-in enviado com sucesso ✓"
- Readiness score displayed
- "Ver Sessão" button (navigate to session detail)
- "Voltar" (navigate to [1])

**Components:**
- `<modal>` with success icon
- Display readiness score circular progress
- `<button>` (primary, secondary)

**State:** success

---

#### Endpoint Map (UIF-002)

| Tela | Ação do Usuário | operationId | Método |
|------|----------------|-------------|--------|
| [1] Scheduled Sessions List | Carregar sessões agendadas | `listTrainingSessions` (filter: `status=PUBLISHED`) | GET |
| [3] Wellness Assessment | Submeter wellness pré-treino | `submitWellnessPre` | POST |
| [3] Wellness Assessment | Consultar wellness pré-treino | `getWellnessPre` | GET |
| [3] Wellness Assessment | Atualizar wellness pré-treino | `updateWellnessPre` | PATCH |
| [4] Readiness Score | Calculado client-side (sem chamada de API) | — | — |
| [5] Ineligibility Declaration | Declarar inelegibilidade | ⚠️ `MISSING` — ver §8 | — |
| [5] Ineligibility Declaration | Consultar inelegibilidade | ⚠️ `MISSING` — ver §8 | — |

---

#### State Transitions

```
[1] Scheduled Sessions List
    → loading
    → empty (no sessions)
    → success

[2] Pre-Training Check-in Form
    → loading (on first render)

[3] Wellness Assessment
    → success (after input validation)
    → error (validation failed, e.g., invalid HR)

[4] Readiness Score
    → success (auto-computed after [3])

[5] Ineligibility Declaration
    → success

[6] Check-in Submitted Confirmation
    → success (async POST to backend)
    → error (submission failed, retry button)
    → (navigate to [1])
```

---

### UIF-TRAINING-003: Coach Review & Intervention

**Ator:** Coach  
**Objetivo:** Revisar execução da sessão, feedback, e intervenções necessárias  
**Frequência:** Pós-sessão (após IN_PROGRESS → COMPLETED)  
**Decision Refs:** TRAIN-DEC-025

#### Screens

```
[1] Sessions to Review Queue
    ↓ (click session)
[2] Session Review Dashboard
    ├─ [3] Attendance Panel
    ├─ [4] Execution Summary
    ├─ [5] Feedback & Interventions
    └─ [6] Analytics Alerts (Attention Queue)
    ↓ (click "Completar Revisão")
[7] Session Marked as Complete
```

#### Screen Definitions

**[1] Sessions to Review Queue**
- List of COMPLETED sessions awaiting coach review
- Per session: title, date, team, num athletes checked in, num attendance gaps
- Badges: "Alertas" count if attention_queue items

**Components:**
- `<card-list>`
- `<badge label="3 atletas" />`
- `<badge label="2 alertas" variant="warning" />`

**State:** loading, empty, success

---

**[2] Session Review Dashboard**
- Header: session title, date, team, status
- 4 sub-panels below

---

**[3] Attendance Panel**
- Table: athlete name, check-in time, readiness score, ineligibility flags
- Per athlete: attendance marked (checkbox), notes (text input)
- Bulk actions: "Marcar todos", "Desmarcar tudo"

**Components:**
- `<table>`
- `<checkbox>` (attendance per athlete)
- `<input type="text">` (notes, placeholder="Observações do atleta")
- `<button>` (bulk)

**Validation:**
- At least N athletes marked (config)
- If ineligibility flagged, cannot uncheck attendance

**Data:** `contracts/schemas/training/training_attendance_marked.v1.json`

---

**[4] Execution Summary**
- Cards per session block executed:
  - Block phase, exercises, duration estimate vs actual
  - Adjustments made (if any): exercise swaps, load increases/decreases
  - Visualizations: timeline chart (estimated vs actual duration per phase)

**Components:**
- `<card-list>`
- `<timeline-chart>`

**Data:** Pulls from `execution_record` list with `execution_type` in [SESSION_EXECUTION, BLOCK_EXECUTION, LIVE_ADJUSTMENT]

---

**[5] Feedback & Interventions**
- List of feedback_thread items (coach→athlete conversations)
- Per thread: athlete, timestamp, conversation outcome (reflection, commitment, pending_action, followup, decision)
- Button to open/close feedback thread (modal or new screen)
- Quick-add feedback form: athlete selector, message, outcome

**Components:**
- `<card-list>` (feedback threads)
- `<badge>` (outcome type)
- `<button>` (open thread detail)
- `<form>` (quick add: select athlete, textarea for message, outcome dropdown)

**Data:** `contracts/schemas/training/feedback_thread.v1.json`  
**Behavior:**
- onClick thread card → Opens feedback_thread detail (read-only)
- Quick-add form → POST new feedback_thread
- On success → thread appears in list, form resets

---

**[6] Analytics Alerts (Attention Queue)**
- List of attention_queue_item (status = ACTIVE)
- Per item: type (wellness_alert, medical_flag, recovery_concern, individual_performance, group_dynamics), athlete, alert message, created time
- Actions per item: Resolve (status=RESOLVED), Dismiss (status=DISMISSED), Escalate (status=ESCALATED)
- On action → resolution_evidence text input

**Components:**
- `<card-list>`
- `<status-badge type="wellness_alert" color="warning" />`
- `<button variant="success">Resolvido</button>`
- Modal w/ `<textarea>` for resolution_evidence

**Data:** `contracts/schemas/training/attention_queue_item.v1.json`

---

**[7] Session Marked as Complete**
- Modal: "Revisão concluída ✓"
- Summary: X athletes marked, Y feedback threads, Z attention items resolved
- "Voltar" (navigate to [1])

---

#### Endpoint Map (UIF-003)

| Tela | Ação do Usuário | operationId | Método |
|------|----------------|-------------|--------|
| [1] Sessions to Review Queue | Carregar sessões para revisar | `listTrainingSessions` (filter: `status=COMPLETED`) | GET |
| [2] Session Review Dashboard | Carregar detalhes da sessão | `getTrainingSessionById` | GET |
| [3] Attendance Panel | Listar presença | `listSessionAttendance` | GET |
| [3] Attendance Panel | Registrar presença | `recordSessionAttendance` | POST |
| [4] Execution Summary | Listar execution records | `listExecutionRecords` | GET |
| [5] Feedback & Interventions | Listar feedback threads | `listFeedbackThreads` | GET |
| [5] Feedback & Interventions | Criar feedback thread | `createFeedbackThread` | POST |
| [5] Feedback & Interventions | Fechar feedback thread | ⚠️ `MISSING` — ver §8 | — |
| [6] Attention Queue | Listar attention queue | `listAttentionQueueItems` | GET |
| [6] Attention Queue | Resolver item | ⚠️ `MISSING` — ver §8 | — |
| [6] Attention Queue | Rejeitar item | ⚠️ `MISSING` — ver §8 | — |
| [6] Attention Queue | Escalar item | ⚠️ `MISSING` — ver §8 | — |
| [7] Session Marked as Complete | Completar sessão | `completeTrainingSession` | POST |

---

#### State Transitions

```
[1] Sessions to Review Queue
    → loading
    → empty (no sessions to review)
    → success

[2] Session Review Dashboard
    → loading (fetch all sub-panels)
    → success

[3] Attendance Panel
    → success (render table)
    → error (validation on save) → tooltip on athlete row

[4] Execution Summary
    → success (render cards/timeline)

[5] Feedback & Interventions
    → loading (fetch threads)
    → success
    → loading (on quick-add submit)
    → success (thread added to list)
    → error (submit failed) → error toast

[6] Analytics Alerts
    → loading (fetch attention queue)
    → empty (no alerts)
    → success
    → loading (on action click) → modal resolution_evidence
    → success (status updated)

[7] Session Marked as Complete
    → success (modal)
    → (navigate to [1])
```

---

---

### UIF-TRAINING-004: Team Readiness View — Modo Quadra

**Ator:** Coach (head_coach, assistant_coach)
**Objetivo:** Ver prontidão de toda a equipe antes e durante a sessão, identificar exceções de imediato
**Frequência:** Ao iniciar ou monitorar qualquer sessão IN_PROGRESS
**Contexto:** `context: quadra` — mobile obrigatório (D-UI-16)
**Decision Refs:** D-UI-SP-01, D-UI-SP-02

#### Screens

```
[1] Session Quick Access (mobile home do coach)
    ↓ (tap na sessão do dia)
[2] Team Readiness Overview
    ├─ Atletas com exceção (topo, destacados)
    └─ Demais atletas (lista por status)
    ↓ (tap em atleta específico)
[3] Athlete Detail Drill-down
```

#### Screen Definitions

**[1] Session Quick Access**
- Tela inicial do coach no mobile: exibe a sessão do dia com hora, time e botão "Ver equipe"
- Se não há sessão hoje: "Nenhuma sessão hoje"

**Components:**
- `<session-hero-card>` (título, hora, time)
- `<button label="Ver equipe" variant="primary" />`

---

**[2] Team Readiness Overview**
- Lista de todos os atletas convocados para a sessão
- **[D-UI-SP-01] Bloco de exceção no topo (automático):**
  - Atletas com readiness < 40 → badge vermelho + ícone de alerta
  - Atletas com inelegibilidade declarada → badge cinza + ícone de restrição
  - Atletas sem check-in → badge âmbar + "Aguardando"
- **Bloco normal abaixo:** atletas com readiness ≥ 70 (verde)
- **[D-UI-SP-02] Visão de equipe é a tela primária** — não existe tela de sessão no mobile sem passar por esta

**Componentes:**
- `<athlete-readiness-row>` por atleta:
  - Nome | Score circular (40px) | Status badge | Ícone de exceção (se aplicável)
- `<section-header label="Atenção necessária" />` (se houver exceções)
- `<section-header label="Prontos" />`
- Tap em qualquer atleta → navega para [3]

**Dados:** Agrega `wellness_assessment.readiness_score` + `athlete_ineligibility_declaration` por atleta na sessão

**State:** loading, success, empty ("Nenhum atleta com check-in ainda")

---

**[3] Athlete Detail Drill-down**
- Header: nome do atleta, foto (se disponível), readiness score (circular grande, 80px)
- Breakdown de readiness (segunda camada — D-UI-SP-03):
  - Sono, Humor, FC repouso, Fadiga — com valor e barra de nível
- Inelegibilidades declaradas (se houver)
- Histórico simplificado: últimos 3 scores (mini-sparkline)
- Ação rápida: "Abrir thread de feedback" → navega para UIF-003 Feedback

**Components:**
- `<circular-progress size="large" />`
- `<metric-breakdown-row>` × 4
- `<sparkline>` (3 pontos)
- `<button label="Feedback" variant="secondary" />`

**State:** loading, success

---

#### Endpoint Map (UIF-004)

| Tela | Ação do Usuário | operationId | Método |
|------|----------------|-------------|--------|
| [1] Session Quick Access | Sessão do dia | `listTrainingSessions` (filter: `today + status=PUBLISHED,IN_PROGRESS`) | GET |
| [1] Session Quick Access | Iniciar sessão | `startTrainingSession` | POST |
| [2] Team Readiness Overview | Listar check-ins da equipe | `listSessionAttendance` | GET |
| [2] Team Readiness Overview | Wellness por atleta | `getWellnessPre` | GET |
| [3] Athlete Detail | Wellness detalhado do atleta | `getWellnessPre` | GET |

---

#### State Transitions

```
[1] Session Quick Access
    → loading (fetch today's session)
    → empty (no session today)
    → success

[2] Team Readiness Overview
    → loading (fetch team check-ins)
    → empty (no check-ins yet)
    → success (partition: exceptions topo, ok abaixo)

[3] Athlete Detail
    → loading (fetch athlete wellness detail)
    → success
```

---

### UIF-TRAINING-005: Load Chart — Modo Escritório

**Ator:** Coach, Coordinator
**Objetivo:** Visualizar a curva de carga e recuperação da equipe ao longo do tempo para tomar decisões de periodização
**Frequência:** Semanal / planejamento de ciclo
**Contexto:** `context: escritório` — desktop prioritário (D-UI-16)
**Decision Refs:** D-UI-SP-04

#### Screens

```
[1] Load Chart Dashboard
    ├─ Seletor: Equipe ou Atleta individual
    ├─ Seletor de período (7d, 30d, temporada)
    └─ Curva de carga (ATL) × recuperação (readiness médio)
    ↓ (click em ponto da curva)
[2] Session Detail Tooltip / Popover
```

#### Screen Definitions

**[1] Load Chart Dashboard**
- Título: "Carga & Recuperação — [Team Name]"
- Seletor de modo:
  - `Equipe` → curva agregada (média de readiness + contagem de sessões)
  - `Atleta` → dropdown para selecionar atleta individual
- Seletor de período: `Últimos 7 dias` | `Últimos 30 dias` | `Temporada completa`
- **Gráfico principal (área + linha):**
  - Eixo X: data (dias)
  - Eixo Y esquerdo: número de sessões / carga (volume × intensidade)
  - Eixo Y direito: readiness médio (0–100)
  - Área azul clara = carga acumulada (ATL proxy)
  - Linha verde = readiness médio da equipe/atleta
  - Linha vermelha tracejada = zona de risco (readiness < 40 por 3+ dias seguidos)
- Legenda: Carga | Readiness | Zona de risco

**Componentes:**
- `<line-area-chart>` (biblioteca a definir na implementação)
- `<segmented-control>` (Equipe / Atleta)
- `<select>` (atleta, visível apenas no modo Atleta)
- `<date-range-selector>` (7d / 30d / Temporada)

**Dados:**
- Agrega `training_session` (por data, por time/atleta) × `wellness_assessment.readiness_score`
- Endpoint dedicado: `GET /training/load-chart?team_id=&athlete_id=&range=`

**State:** loading, success, empty ("Sem dados suficientes para o período selecionado")

---

**[2] Session Detail Tooltip / Popover**
- Click / hover em qualquer ponto da curva de carga
- Popover exibe:
  - Data
  - Sessão(ões) do dia: título, duração, fase de periodização
  - Readiness médio do dia
  - Número de atletas com exceção

**Components:**
- `<popover>` ancorado ao ponto do gráfico
- `<session-mini-card>` dentro do popover

---

#### Endpoint Map (UIF-005)

| Tela | Ação do Usuário | operationId | Método |
|------|----------------|-------------|--------|
| [1] Load Chart Dashboard | Carregar dados de carga | ⚠️ `MISSING` — ver §8 | — |
| [2] Session Detail Tooltip | Click em ponto da curva | Dados já carregados no [1] (sem chamada adicional) | — |

> **Nota de contexto para UIF-005:** Dados de mesociclo/microciclo disponíveis via `listMesocycles` / `listMicrocycles` para contexto de periodização, mas o endpoint agregado `GET /training/load-chart` não existe no OpenAPI. Ver §8.

---

#### State Transitions

```
[1] Load Chart Dashboard
    → loading (fetch aggregated load data)
    → empty (insufficient data — < 3 sessions in range)
    → success (render chart)
    → loading (on period/mode change → refetch)

[2] Tooltip
    → visible (on hover/click)
    → hidden (on blur/click outside)
```

---

## Parte 3: Componentes Reutilizáveis

> SSOT visual: `UI_CONTRACT_GUIDE.md`. Todos os componentes implementados com **shadcn/ui + Tailwind CSS** (D-UI-18).
> Tokens de cor, spacing e radius definidos na Parte 1 acima.

### 3.1 Mapeamento de padrões visuais → componentes do módulo

| Padrão visual | Componente neste módulo | Tokens aplicados |
|-------------------|------------------------|-----------------|
| `emptyStateCard` | Empty states de [1] em todos os UIFs | `p-12 rounded-lg border` · ícone `w-16 h-16 rounded-full bg-gray-100` · título `text-lg font-medium` · desc `text-sm text-slate-500` |
| `alertBanner` | Sessão aguardando revisão (UIF-003 [1] badge "Alertas"), wellness em risco | `px-4 py-2 rounded-lg text-sm border` · cores `warning.*` |
| `microButton` | Aceitar/rejeitar recomendação inline (UIF-001 [5]), marcar presença (UIF-003 [3]) | `px-2 py-1 text-[10px] font-medium rounded shadow-sm` |
| `compactPill` | Status badge da sessão (DRAFT, SCHEDULED…), contadores de alertas | `px-3 py-2 rounded-md w-fit text-xs` |
| Error card | Telas de erro de carregamento em todos os UIFs | `border rounded-lg` · cores `danger.*` · título `text-sm font-medium` + ação com `hover:underline` |

### 3.2 Tabela de presença por UIF

| Componente | Tokens | UIF-001 | UIF-002 | UIF-003 | UIF-004 | UIF-005 |
|------------|-----------------|---------|---------|---------|---------|---------|
| `<button>` primário | shadcn `Button` default | New, Publish, Add | Confirmar | Completar revisão | Ver equipe | — |
| `<button>` secundário | shadcn `Button variant="ghost"` | Add/Remove bloco | Back, Cancelar | Dismiss, Escalate | Feedback | — |
| `<button>` micro | `microButton` (`px-2 py-1 text-[10px] font-medium rounded shadow-sm`) | Aceitar/Rejeitar rec. | — | Resolve inline | — | — |
| `<select>` | shadcn `Select` | Team, Phase, Need | — | Athlete, Outcome | — | Atleta, Período |
| `<input text>` | shadcn `Input` `text-sm` | Title, Obj. Desc | — | Feedback message | — | — |
| `<textarea>` | shadcn `Textarea` `text-sm` | Obj. Desc, Dismissal | Inelegib. Other | Feedback, Resolution | — | — |
| `<input date>` | shadcn `Input type="date"` | Session date | — | — | — | — |
| `<input number>` | shadcn `Input type="number"` | Duration | HR input | — | — | — |
| `<slider>` | shadcn `Slider` | Focus % (×7) | Wellness, Fatigue | — | — | — |
| `<checkbox>` | shadcn `Checkbox` | Block remove confirm | Inelegib. flags | Attendance | — | — |
| `<card>` | `rounded-lg border shadow-sm surface` | Sessions, Blocos, Rec. | Session cards | Exec., Threads | Session hero | Tooltip sessions |
| `<table>` | shadcn `Table` `text-sm` | Session list | — | Attendance, Exec | — | — |
| `<modal>` | shadcn `Dialog` | Published Confirm | Check-in Confirm | Feedback, Attention | — | — |
| `<badge>` / status pill | `compactPill` (`px-3 py-2 rounded-md w-fit text-xs`) | Status da sessão | Readiness, Check-in | Attendance, Alert | Readiness atleta | — |
| `<spinner>` | Lucide `Loader2` `animate-spin` | ✓ | ✓ | ✓ | ✓ | ✓ |
| `<toast>` | shadcn `Sonner` / `toast` | — | — | Success/error | — | — |
| `<empty-state>` | `p-12 rounded-lg border` · ícone `w-16 h-16 rounded-full` · título `text-lg font-medium` | ✓ | ✓ | ✓ | ✓ | ✓ |
| `<error-state>` | `border rounded-lg` · cores `danger.*` · título `text-sm font-medium` + retry | ✓ | ✓ | ✓ | ✓ | ✓ |
| `<alert-banner>` | `px-4 py-2 rounded-lg text-sm border` · cores `warning.*` | — | — | Review Queue [1] | — | — |
| `<wellness-indicator>` | Ponto 12px `rounded-full` · cores: `emerald-500`¹ / `amber-500` / `red-500` | — | Check-in list [1] | — | — | — |
| `<circular-progress>` | SVG + `text-sm font-medium` · cor semântica | — | Readiness [4] | — | Drill-down [3] | — |
| `<athlete-readiness-row>` | `flex items-center gap-3` + circular 40px | — | — | — | Team Overview [2] | — |
| `<sparkline>` | SVG 3 pontos · cor `slate-400` | — | — | — | Drill-down [3] | — |
| `<line-area-chart>` | Recharts (D-UI-18) · área azul + linha verde + linha vermelha tracejada | — | — | — | — | Load Chart [1] |
| `<segmented-control>` | shadcn `ToggleGroup` | — | — | — | — | Equipe/Atleta |
| `<popover>` | shadcn `Popover` `rounded-lg border shadow-sm` | — | — | — | — | Session detail [2] |
| `<draggable-list>` | dnd-kit `DndContext` (D-UI-18) | Blocos [4] | — | — | — | — |

> ¹ `emerald-500` (`#10b981`) = token `semantic.success` do projeto.

### 3.3 Regras de uso

- **Sombras:** `shadow-sm` apenas. Sem `shadow-md`, `shadow-lg`.
- **Radius:** cards/modais = `rounded-lg` (12px); badges/pills = `rounded-md` (8px); ícones circulares = `rounded-full`.
- **Tipografia:** seguir escala da Parte 1. Não introduzir tamanhos fora de `text-[10px]`, `text-xs`, `text-sm`, `text-lg`.
- **Cores:** usar tokens semânticos da Parte 1. Não usar hexadecimais arbitrários em componentes.
- **Dark mode:** todo componente deve ter variante `dark:` equivalente.

---

## Parte 4: Data Contracts

### Input Schemas (User Submissions)

- `training_session` (create/update): title, team, scheduled_at, duration, focus_percentages[7]
- `session_objective` (create): type origin, need_id (if applicable), description
- `session_block` (create): phase, exercises[], duration
- `training_attendance_marked`: athlete_id, marked=true, notes (optional)
- `wellness_assessment`: sleep_quality, mood, resting_hr, yesterdays_fatigue, injury_notes (optional)
- `athlete_ineligibility_declaration`: reason_flags[], reason_other (if applicable)
- `feedback_thread` (create): athlete_id, message, conversation_outcome
- `attention_queue_item` (update status): attention_queue_item_id, status, resolution_evidence

All ref: `contracts/schemas/training/`

---

## Parte 5: Decision Refs & Related ADRs

- **TRAIN-DEC-006:** Session configuration (title, focus percentages, team)
- **TRAIN-DEC-007:** Objective creation and linking
- **TRAIN-DEC-008:** Block-level planning and adjustment
- **TRAIN-DEC-024:** Athlete check-in and readiness assessment design
- **TRAIN-DEC-025:** Coach review, feedback loop, and interventions

**Decisões de Design Arquitetural (§ Parte 0):**
- **D-UI-16:** Split por contexto — modo quadra (mobile) vs. modo escritório (desktop)
- **D-UI-15:** Online obrigatório — sem cache offline
- **D-UI-SP-01:** Readiness Score como entrada da sessão (inspiração: Whoop, Kitman Labs)
- **D-UI-SP-02:** Visão de equipe como tela primária do coach no modo quadra (inspiração: Catapult, Kinexon)
- **D-UI-SP-03:** Progressive disclosure no wellness do atleta (inspiração: Whoop)
- **D-UI-SP-04:** Gráfico de carga × recuperação no modo escritório (inspiração: TrainingPeaks)

Related ADRs:
- **ADR-006:** Coach-in-Loop recomendação strategy
- **ADR-007:** Athlete self-assessment and readiness scoring
- **ADR-008:** Real-time feedback and coach intervention

---

## Parte 6: Accessibility & UX

### WCAG 2.1 AA Compliance
- All inputs have visible labels or `aria-label`
- Form errors announced to screen readers
- Focus visible on all interactive elements
- Color not sole means of conveying information (use icons, text labels, patterns)

### Responsiveness (D-UI-16: Split por Contexto)

| Contexto | Telas | Breakpoint primário | Degradação aceitável |
|----------|-------|---------------------|----------------------|
| `quadra` (mobile) | UIF-002 atleta, UIF-004 coach | 360px | Versão desktop existe mas não é prioritária |
| `escritório` (desktop) | UIF-001, UIF-003, UIF-005 | 1024px+ | Funciona em mobile com scroll, sem redesenho dedicado |

- Breakpoints disponíveis: 360, 768, 1024, 1440 (per UI_CONTRACT_GUIDE.md)
- Touch targets modo quadra: mínimo **48×48 px** (aumentado para uso na quadra com luvas/mãos suadas)
- Touch targets modo escritório: mínimo 44×44 px

### Performance
- Lazy load session details (avoid fetching all recommendations in [1])
- Cache athlete list and team list
- Optimistic updates on checkbox actions (attendance)

---

## Parte 7: Implementation Roadmap

> **Decisão D-UI-19:** G-01 a G-05 são todos MVP v1.0. O roadmap abaixo reflete isso.
> **Pré-requisito:** Contract revision de `training.yaml` adicionando 9 endpoints (G-01 a G-05) deve ser concluída antes das Phases 2–5.

### Phase 1 (MVP — UIF-TRAINING-001 core)
- [ ] Session List + Header Form
- [ ] Objectives Panel (manual entry + auto-population de needs abertas)
- [ ] Session Blocks Builder (drag-and-drop via dnd-kit)
- [ ] Published Confirmation
- [ ] _Pré-req para [5]: contract revision G-01_

### Phase 2 (MVP — UIF-TRAINING-002 + G-02)
- [ ] Scheduled Sessions for Athletes
- [ ] Wellness Assessment Form (`submitWellnessPre`)
- [ ] Readiness Score Display (client-side)
- [ ] Ineligibility Declaration (`submitIneligibilityDeclaration` — G-02)
- [ ] Check-in Confirmation

### Phase 3 (MVP — UIF-TRAINING-003 + G-03 + G-04)
- [ ] Sessions to Review Queue
- [ ] Attendance Panel (`recordSessionAttendance`)
- [ ] Execution Summary (`listExecutionRecords`)
- [ ] Feedback & Interventions (`createFeedbackThread` + `closeFeedbackThread` — G-04)
- [ ] Analytics Alerts com ações resolve/dismiss/escalate (G-03)
- [ ] Complete Session (`completeTrainingSession`)

### Phase 4 (MVP — UIF-TRAINING-001 [5] Recommendations + G-01)
- [ ] Recommendations Review panel dentro do Session Header Form
- [ ] Accept/Dismiss recomendações (`acceptRecommendation`, `dismissRecommendation` — G-01)

### Phase 5 — Modo Quadra (UIF-TRAINING-004)
- [ ] Session Quick Access (coach mobile home, PWA instalada)
- [ ] Team Readiness Overview com partição automática de exceções
- [ ] Athlete Detail Drill-down com progressive disclosure

### Phase 6 — Load Chart (UIF-TRAINING-005 + G-05)
- [ ] Load Chart Dashboard (equipe) (`getLoadChart` — G-05)
- [ ] Load Chart Dashboard (atleta individual)
- [ ] Session Detail Popover
- [ ] _Pré-req: endpoint `GET /training/load-chart` adicionado ao OpenAPI_

### Phase 7 (Polish & Integration)
- [ ] Notifications on new alerts
- [ ] Advanced filtering/search on lists
- [ ] Bulk operations (export, re-schedule)
- [ ] PWA manifest + next-pwa configuration

---

## UIF-TRAINING-006: HB Pro Coach — Virtual Assistant Chat

**Ator:** Atleta (qualquer idade)  
**Objetivo:** Conversar com assistente de IA especializado em handebol para tirar dúvidas sobre treino, exercícios, preparação física, nutrição, descanso, feedback de sessões anteriores e receber sugestões de treino compensatório  
**Frequência:** Ad-hoc durante contexto de treino ou pré/pós-treino  
**Decision Refs:** D-UI-20, D-UI-21, TRAIN-DEC-009  
**Scope:** Atleta pode acessar chat a partir de qualquer contexto de treino (UIF-TRAINING-002 or beyond)

### Características Principais

#### 1. Interface do Chat

**Chat Modal**
- Abre via botão "?" ou "Coach" no header/footer (sempre visível)
- Posicionamento: canto inferior direito (bottom-right, `fixed`)
- Dimensões: 400px × 600px (mobile responsivo, 100% width em `<640px`)
- Animação: slide-up com fade-in
- Dark mode completo

**Components Chat:**
- `<chat-bubble-container>`
  - Histórico de mensagens (scrollable, auto-scroll on new message)
  - Timestamp + avatar (H = HB Pro Coach, initials = Athlete)
  - Mensagens do coach: `bg-info.bg`, ícone com bagde "Coach"
  - Mensagens do atleta: `bg-blue-100 dark:bg-blue-900/30`, alinhado à direita
  - `<input-field>` com placeholder: "Escreva sua pergunta ao Coach..."
  - `<button-send>` (ícone de envio, disabled enquanto enviando)
  - `<typing-indicator>` (3 pontos animados) quando coach está "respondendo" (LLM processando)

**States do Chat:**
- `loading_initial`: Primeira carga do histórico
- `typing`: Coach respondendo (LLM em processamento)
- `error_message`: Falha de envio ou resposta (retry button)
- `success`: Mensagem enviada + resposta recebida
- `offline`: Error state (sem conexão)

#### 2. Escopo de Respostas — Behavioral Rules

O HB Pro Coach pode responder a perguntas sobre:

1. **Treino & Exercícios**
   - "O que é esse exercício?" → Explicação de movimento, propósito, músculos trabalhados
   - "Como faço exercício X?" → Instruções passo-a-passo, dicas de segurança
   - "Qual é o objetivo desse bloco?" → Contexto do treino planejado

2. **Handebol — Aspectos Técnicos & Táticos**
   - "Qual é minha posição?" → Info da posição configurada + atributos
   - "Como jogo bem em minha posição?" → Dicas específicas de posição ofensiva/defensiva
   - "O que é essa formação?" → Explicação de formações defensivas, tipos de defesa
   - "Tipos de arremesso" → Gancho, parado, em queda, com salto, etc.
   - "Movimentação tática" → Deslocamentos, dinâmica de jogo por posição
   - "Regras do handebol" → Clarificações rápidas de regras básicas

3. **Wellness & Recuperação**
   - "Estou cansado" → Análise do histórico de wellness pré-treino + sugestões (mais descanso, alimentação)
   - "Devo fazer treino pesado?" → Recomendação baseada em wellness score + histórico
   - "Quanto devo dormir?" → Recomendações de sleep por idade + posição
   - "Nutrição pré/pós-treino" → Dicas simples de alimentação para handebolistas

4. **Histórico & Feedback**
   - "Por que não treinei ontem?" → Se atleta faltou, coach contextualiza + oferece compensatório
   - "O que foi treinado ontem?" → Resumo da sessão anterior (blocos, objetivos, foco %)
   - "Qual foi meu feedback?" → Resumo de comentários pós-treino do coach (se houver)
   - "Como posso melhorar?" → Recomendação personalizada baseada em treinos passados

5. **Motivação & Aderência**
   - Todas as respostas são encorajadoras, age-appropriate
   - Finaliza muitas respostas com incentivo: "Vamos nessa! 💪" (tone: entusiasta, nunca robótico)
   - Redirecionamento: "Conversei com o Coach sobre isso. Pergunte na próxima sessão!" (quando answer está fora de scope)

#### 3. Rejeição de Off-Topic

Se atleta pergunta sobre algo **fora de escopo** (política, futebol, videogame, namoro, etc.):

```
HB Pro Coach: "Sou treinador virtual de handebol! 
Posso ajudar com dúvidas sobre exercícios, 
técnica, wellness ou preparação. 
O que quer saber sobre seus treinos? 😊"
```

**Exemplos de rejeição:**
- Off-topic: "Qual é seu time de futebol?"
- Palavrão: "Que #$%@ exercício é esse?"
- Spam/test: "aaaaaaa"

→ Sempre resposta amigável, nunca agressiva.

#### 4. Compreensão de Linguagem Natural & Inclusividade

O coach **entende fluentemente** abreviações, gírias e linguagem informal comum entre atletas — e responde **de forma natural e motivadora**, sem apontar ou corrigir:

```
Atleta: "vc pode me ensinar pq o arremesso eh importante?"
HB Pro Coach: "Ótima pergunta! O arremesso é a finalização do seu treino.
Na sua posição [Posição], você treina [tipo de arremesso] porque...
Tá indo bem em buscar aprender! 💪"
```

**Abreviações entendidas automaticamente:** vc (você), pq (porque), oq (o que), taum (tá um), msm (mesmo), blz (blz), flw (falou), n/nao (não), tb/tbm (também), etc.

**Princípio Core:** Nenhuma correção. Nenhuma frustração. Resposta natural + elogio genuíno. Comunicação que **eleva a autoestima** do atleta.

#### 5. Sugestão de Treino Compensatório (Feature Store + AI_INGESTION)

Quando atleta **perdeu uma sessão**, **quer treino de objetivos específicos**, ou **Coach detecta padrão**:

**Flow arquitetural:**

1. **Atleta inicia:**
   - Via chat: "Perdi o treino ontem, posso fazer hoje?"
   - **Ou** Coach proativamente: "Vi que você não treinou [data]. Quer uma sessão para compensar?"

2. **HB Pro Coach consulta Feature Store** (via `ai_ingestion`):
   - **Dados consultados:** 
     - Treinos ultimos 30 dias (gaps, frequência por tipo)
     - Wellness pré/pós-treino (fadiga, lesões atuais, restrições médicas)
     - Performance analytics (velocidade, força, defesa — trending)
     - Histórico de feedback (fraquezas recomendadas pelo treinador)
     - Categoria etária + posição
   - **Features calculadas:**
     - `fatigue_score` (0-10) = f(wellness pré-treino, gaps, sleep, resting_hr recentes)
     - `performance_gap` = última sessão vs. objective (p. ex., "faltou velocidade")
     - `injury_status` = restrições ativas (câncer, no-contact, partial return)
     - `recommended_focus` = output de regra determinística baseada em features

3. **Regras especializadas** geram sugestão (sem LLM externo):
   - Exemplo: `IF fatigue_score > 7 AND performance_gap.velocity > 15% THEN focus = [técnica, recuperação] ELSE [força, velocidade]`
   - Cada posição tem regras próprias (ponteira treina força ≠ golaço treina reação)
   - Design decision: DR-TRAIN-COACH-08 documenta todas as regras de seleção

4. Coach mostra **preview** ao atleta (sem blocos, sem local/data):
   ```
   "Recomendo: TREINO TÉCNICA - PONTA (40min)
   
   Por quê? Vi que você progrediu em velocidade 
   (12% essa semana!), mas técnica pode evoluir.
   
   Objetivos: Précisão de arremesso + movimentação
   
   Vou mandar para seu treinador revisar e aprovar!"
   ```
   - Nome + duração + justificativa personalizada (baseada em features reais)
   - **SEM blocos detalhados** (apenas preview com contexto)

5. **Sistema envia Async Notification ao Treinador:**
   - Backend: `POST /hb-pro-coach/training-suggestions`
   - Payload: `{ athleteId, coachId, trainingName, duration, objectives[], blocks[], features: { fatigue_score, performance_gap, injury_status }, athleteWellness, context, generationTimestamp }`
   - Treinador recebe **com features enviadas** (para auditoria + entender raciocínio da IA)
   - Treinador vê sugestão **completa** (blocos de exercícios + progressão)
   - Botões: **[Aprovar]** **[Recusar]** **[Editar & Aprovar]**

6. **Treinador da Equipe responde:**
   - Clica "Aprovar" → Backend gera evento AsyncAPI: `training.suggestion.approved` + registra em Feature Store
   - Clica "Recusar" → Backend gera evento AsyncAPI: `training.suggestion.rejected` + registra motivo
   - Clica "Editar & Aprovar" → Modifica blocos/foco, depois aprova (ambos registrados)

7. **Atleta notificado:**
   - ✅ Se aprovado: "[Nome do Treinador] aprovou seu treino! Vá em frente. 💪" + treino aparece em "Sessões Agendadas" com status "Aprovado por [Nome]"
   - ❌ Se recusado: "Seu treinador revisou a sugestão. Próximas alternativas: [lista similar] ou conversa diretamente com ele!" + redirecionamento para chat com coach

**Integração com `ai_ingestion`:**
- Cada dado consultado (treino, wellness, medical) passa por `ai_ingestion` antes de chegar ao Coach
- Rastreamento: `ai_ingestion` registra cada consulta (auditía, LGPD)
- Idempotência: se atleta refaz sugestão 2x no mesmo dia, `ai_ingestion` dedup com `idempotencyKey`
- Especialização: Feature Store é o "conhecimento" do Coach — quanto mais histórico + dados integrados, melhor as sugestões

#### 6. Contextualização com Wellness & Histórico (Feature Store)

Cada resposta do HB Pro Coach **consulta Feature Store** para ser personalizada ao atleta:
- **Wellness pré-treino** (HR, RPE, sono, desconforto): "Vi que sua frequência cardíaca está alta. Recomendo treino com intensidade moderada hoje."
- **Treinos faltados**: "Notei que você não treinou [data]. Que tal [sugestão compensatória]?"
- **Histórico de feedback**: "Na última sessão, o Coach comentou que você pode melhorar em [aspecto]. Dica: [resposta contextualizada com base em dados]"
- **Recomendações de preparação física**: "Vimos que você precisa de mais recuperação. Seu resting HR está elevado. Dorme mais de 8 horas por noite?"
- **Dados integrados** (via `ai_ingestion`): Coach acessa treinos passados, lesões médicas, readiness trends, progresso de força — resposta sempre tem contexto real do atleta, nunca genérica

---

### Estrutura de Telas (UIF-TRAINING-006)

#### [1] Chat Modal (Default)

**Quando abre:**
- Se é primeira conversa: "Olá! Sou HB Pro Coach. Como posso ajudar com seus treinos?" (welcome message)
- Se histórico existe: carrega últimas 20 mensagens (pagesized load)

**Layout:**
```
┌─────────────────────────────────┐
│ HB Pro Coach          [minimize] │ ← Header (com ícone + close button)
├─────────────────────────────────┤
│ ← Msg coach: "Como posso ajudar?" │ ← Histórico scrollable
│                                 │
│ Msg atleta: "Como treinar força?"→ │
│                                 │
│ ← Msg coach: "Exercícios..."    │
│                                 │
│ ← [typing indicator]            │ ← Coach respondendo (state: typing)
├─────────────────────────────────┤
│ [input field] [send button]     │ ← Input + send
└─────────────────────────────────┘
```

**States:**
- `messages.empty`: "Comece a conversa!"
- `messages.loading`: Spinner ao carregar histórico
- `message.sending`: Input disabled, spinner no botão enviar
- `message.error`: Card de erro com retry

#### [2] Treino Sugerido — Preview para Atleta (Modal Overlay)

Após o Coach sugerir treino, mostra preview ao atleta **sem blocos de exercício**:

```
┌──────────────────────────────────────┐
│ Sugestão de Treino Criada            │
├──────────────────────────────────────┤
│ FORÇA - PONTA (45min)                │
│ Objetivos: Fortalecer superiores     │
│            + core                    │
│                                      │
│ Enviando para seu treinador          │
│ revisar e aprovar...                 │
│                                      │
│ [Entendi] [Cancelar]                 │
└──────────────────────────────────────┘
```

**Nota:** Atleta vê apenas **preview** (nome + duração + objetivos). **Blocos completos** são enviados ao treinador da equipe.

States:
- `sending`: Loading state while notifying coach
- `sent`: "Seu treinador [Nome] vai revisar. Você receberá notificação quando responder!"
- `error`: "Erro ao enviar. Tentar novamente?"

#### [3] Notificação de Resposta do Treinador (In-app + UI update)

O **Treinador da Equipe** responde à sugestão. Atleta recebe notificação:

**Se aprovado:**
```
← Seu treinador [Nome] aprovou! 
  "FORÇA - PONTA" já está em suas sessões para quando precisar. 
  Vá em frente! 💪
```

**Se rejeitado:**
```
← Seu treinador [Nome] revisou a sugestão. 
  Próximas opções: treino leve, recuperação, técnica. 
  Converse com ele na próxima sessão para entender melhor!
```

---

### Endpoint Map (UIF-TRAINING-006)

| Tela | Ação | operationId | Método |
|------|------|-------------|--------|
| [1] Chat Modal | Carregar histórico | ⚠️ `listChatMessages` — G-06 | GET |
| [1] Chat Modal | Enviar mensagem | ⚠️ `sendChatMessage` — G-06 | POST |
| [1] Chat Modal | Obter resposta HB Pro Coach (Feature Store) | ⚠️ `generateCoachResponse` — G-06 | POST |
| [2] Training Suggestion Card | Sugerir treino ao coach | ⚠️ `submitTrainingSuggestion` — G-06 | POST |
| [3] Notification | Notificar atleta (via AsyncAPI) | ⚠️ `training.suggestion.approved` event | AsyncAPI |
| [3] Notification | Notificar atleta (rejeição) | ⚠️ `training.suggestion.rejected` event | AsyncAPI |

---

### State Transitions (UIF-TRAINING-006)

```
[Chat Modal opens]
  ├─ loading_initial (fetch histórico)
  ├─ success (render histórico ou empty state)
  └─ error (retry)

[User types + sends message]
  ├─ message.sending (input disabled)
  ├─ message.sent (add to chat bubble)
  ├─ generating_response (typing indicator)
  ├─ response.received (LLM response)
  ├─ response.error (retry option)
  └─ success

[Coach suggests training]
  ├─ suggestion.display (card overlay)
  ├─ suggestion.sending (notifying coach)
  ├─ suggestion.sent (await coach response)
  └─ suggestion.response (event via AsyncAPI)
     ├─ approved → success state + in-chat message
     └─ rejected → info state + suggestion alternatives
```

---

### Componentes do Design System (UIF-TRAINING-006)

| Padrão | Uso neste UIF | Tailwind |
|--------|----|----|
| `<chat-bubble>` | Mensagem individual (coach ou atleta) | `rounded-lg p-3 mb-3` · cores info/primary |
| `<chat-avatar>` | Avatar do coach/atleta | `w-8 h-8 rounded-full` |
| `<chat-input>` | Campo de texto para mensagem | `w-full p-3 border rounded-lg` · `focus:ring-2` |
| `<typing-indicator>` | 3 pontos animados enquanto coach responde | `flex gap-1` · `animate-bounce` |
| `<training-suggestion-card>` | Card de overlay com sugestão de treino | `rounded-lg border p-4` · cores warning/info |
| `<coach-notification>` | Notificação in-chat de resposta do coach | `rounded-lg p-4` · cores success/danger |
| `<button-send>` | Botão de enviar mensagem | `px-4 py-2 rounded-lg bg-primary` |

---

### Accessibility (a11y) — UIF-TRAINING-006

- **ARIA labels:** `aria-label="Chat message from coach"` em every bubble
- **Keyboard nav:** Tab → input field → send button → close modal
- **Screen reader:** Chat history readable in order (oldest → newest)
- **Dark mode:** All bubbles support `dark:` classes
- **Touch targets:** Send button min 48px × 48px (mobile)
- **Focus ring:** Blue ring (info.ring) on input focus

---

### Data Contracts (Schemas) — UIF-TRAINING-006

Referencia:
- `contracts/schemas/training/athlete_chat_message.v1.json`
- `contracts/schemas/training/athlete_chat_conversation.v1.json`
- `contracts/schemas/training/training_suggestion.v1.json`
- `contracts/schemas/training/training_suggestion_approval.v1.json`

---

## Parte 8: Gaps de Contrato — `BLOCKED_MISSING_CANON_ARTIFACT`

As telas/ações abaixo dependem de endpoints **ausentes no OpenAPI atual** (`contracts/openapi/paths/training.yaml`).
Per regra do worker `create_ui_contract.prompt.md`: "Se o contrato de UI depender de endpoint inexistente no OpenAPI: bloquear com BLOCKED_MISSING_CANON_ARTIFACT."

Cada gap abaixo é um bloqueio parcial — bloqueia **apenas as telas listadas**, não o UIF inteiro.

### Gap G-01: Endpoints de Recomendações (bloqueia UIF-001 [5])

| operationId sugerido | Método | Path sugerido | Bloqueia |
|---------------------|--------|--------------|---------|
| `listRecommendations` | GET | `/training-sessions/{id}/recommendations` | UIF-001 [5] Recommendations Review |
| `acceptRecommendation` | POST | `/training-sessions/{id}/recommendations/{recId}/accept` | UIF-001 [5] botão "Aceitar" |
| `dismissRecommendation` | POST | `/training-sessions/{id}/recommendations/{recId}/dismiss` | UIF-001 [5] botão "Rejeitar" |

**Resolução:** Adicionar endpoints ao OpenAPI + schema `recommendation.v1.json` antes de implementar UIF-001 [5].

---

### Gap G-02: Endpoint de Inelegibilidade (bloqueia UIF-002 [5])

| operationId sugerido | Método | Path sugerido | Bloqueia |
|---------------------|--------|--------------|---------|
| `submitIneligibilityDeclaration` | POST | `/training-sessions/{id}/ineligibility` | UIF-002 [5] Ineligibility Declaration |
| `getIneligibilityStatus` | GET | `/training-sessions/{id}/ineligibility` | UIF-002 [5] estado atual |

**Resolução:** Adicionar endpoints ao OpenAPI + schema `athlete_ineligibility_declaration.v1.json`.

---

### Gap G-03: Ações de Attention Queue (bloqueia UIF-003 [6])

| operationId sugerido | Método | Path sugerido | Bloqueia |
|---------------------|--------|--------------|---------|
| `resolveAttentionQueueItem` | POST | `/training-sessions/{id}/attention-queue/{itemId}/resolve` | UIF-003 [6] botão "Resolvido" |
| `dismissAttentionQueueItem` | POST | `/training-sessions/{id}/attention-queue/{itemId}/dismiss` | UIF-003 [6] botão "Ignorar" |
| `escalateAttentionQueueItem` | POST | `/training-sessions/{id}/attention-queue/{itemId}/escalate` | UIF-003 [6] botão "Escalar" |

**Resolução:** Adicionar endpoints ao OpenAPI. Cada ação recebe `resolution_evidence` no body.

---

### Gap G-04: Fechar Feedback Thread (bloqueia UIF-003 [5] parcialmente)

| operationId sugerido | Método | Path sugerido | Bloqueia |
|---------------------|--------|--------------|---------|
| `closeFeedbackThread` | POST | `/training-sessions/{id}/feedback-threads/{threadId}/close` | UIF-003 [5] fechar thread |

**Resolução:** Adicionar endpoint ao OpenAPI. Body: `{ "resolution_summary": "string" }`.

---

### Gap G-05: Endpoint de Load Chart (bloqueia UIF-005 inteiro)

| operationId sugerido | Método | Path sugerido | Bloqueia |
|---------------------|--------|--------------|---------|
| `getLoadChart` | GET | `/training/load-chart` | UIF-005 [1] Load Chart Dashboard |

**Parâmetros sugeridos:**
```
team_id:     string (obrigatório quando mode=team)
athlete_id:  string (obrigatório quando mode=athlete)
range:       enum [7d, 30d, season] (default: 30d)
```

**Resolução:** Adicionar endpoint ao OpenAPI + definir schema de resposta com `load_points[]` e `readiness_points[]` antes de implementar UIF-005.

---

### Gap G-06: Endpoints de HB Pro Coach Chat (bloqueia UIF-TRAINING-006 [1], [2], [3])

| operationId sugerido | Método | Path sugerido | Bloqueia | Descrição |
|---------------------|--------|--------------|---------|-----------|
| `listChatMessages` | GET | `/hb-pro-coach/conversations/{conversationId}/messages?page=X&pageSize=20` | UIF-006 [1] Chat History | Carregar histórico paginado de mensagens (20 por página) |
| `sendChatMessage` | POST | `/hb-pro-coach/conversations/{conversationId}/messages` | UIF-006 [1] User Input | Enviar mensagem do atleta (body: `{ text: string }`) |
| `generateCoachResponse` | POST | `/hb-pro-coach/messages/{messageId}/generate-response` | UIF-006 [1] Coach Response | Gerar e retornar resposta HB Pro Coach (Feature Store + regras) |
| `submitTrainingSuggestion` | POST | `/hb-pro-coach/training-suggestions` | UIF-006 [2] Training Suggestion | Submeter sugestão de treino gerada pelo coach (body: `{ athleteId, trainingName, duration, objectives[], context }`) |
| `notifyCoachTrainingSuggestion` | POST | `/hb-pro-coach/training-suggestions/{suggestionId}/notify-coach` | UIF-006 [2] Coach Notification | Enviar notificação assíncrona ao treinador do atleta com aprovação pendente |

**Parâmetros & Details:**

```yaml
GET /hb-pro-coach/conversations/{conversationId}/messages:
  parameters:
    - page: integer (default: 1)
    - pageSize: integer (default: 20, max: 100)
  response:
    items:
      - id: uuid
        senderRole: enum [athlete, hb_pro_coach]
        senderName: string (name of athlete or "HB Pro Coach")
        text: string (message content)
        timestamp: datetime
        messageType: enum [text, system_notification] (for coach responses + training suggestions)
    nextPageToken: string | null

POST /hb-pro-coach/conversations/{conversationId}/messages:
  requestBody:
    text: string (required, max: 1000 chars)
    athleteId: uuid (from auth context, auto-populated)
  response:
    id: uuid (message ID)
    status: enum [pending, sent]

POST /hb-pro-coach/messages/{messageId}/generate-response:
  requestBody:
    athleteId: uuid
    athleteAgeGroup: enum [U10, U12, U14, U16, U18, ADULT]
    athletePosition: string (e.g., "Ponta", "Armador", "Goleiro")
    conversationContext: object { previous_messages: [], athlete_wellness: { hr, rpe, sleep, discomfort } }
    detectedMissingSessions: array [{ date, reason }]
    trainingHistory: object { last_5_sessions: [], feedback: [] }
  response:
    responseText: string
    suggestsTraining: boolean (if true, coaching suggests compensation training)
    suggestionDetails?: object { training_name, duration, objectives } (if suggestsTraining=true)

POST /hb-pro-coach/training-suggestions:
  requestBody:
    athleteId: uuid
    coachSuggestedTraining: object { name, duration, objectives[], context }
    athleteWellnessAtRequest: object { hr, rpe, sleep_hours, discomfort_areas }
    missingSessions?: array [{ date, reason }]
  response:
    suggestionId: uuid
    status: enum [pending_coach_approval, approved, rejected]

POST /hb-pro-coach/training-suggestions/{suggestionId}/notify-coach:
  requestBody:
    coachId: uuid (trainer assigned to athlete)
    suggestion: object { name, duration, objectives }
    athleteContext: object { wellness, missing_sessions, position }
  response:
    notificationId: uuid
    deliveryStatus: enum [sent, scheduled]
```

**Regras de Contexto (Coaching Intelligence via Feature Store):**

O endpoint `generateCoachResponse` **deve** aplicar as seguintes regras (integradas com `ai_ingestion`):
1. **Escopo permitido:** Apenas perguntas sobre handebol, treino, wellness, exercícios, feedback histórico
2. **Rejeição de off-topic:** Detectar palavrões e off-topic → resposta redirecionadora educada (nunca agressiva)
3. **Compreensão de linguagem natural:** Entender fluentemente abreviações (vc, pq, oq, taum, msm, etc) **sem apontar ou sugerir correções** — resposta sempre tem contexto personalizado do atleta
4. **Comunicação elevadora de autoestima com dados:** Incluir elogios genuínos baseados em progresso real ("Você progrediu 12% em velocidade esta semana!", "Vejo seu comprometimento nos últimos 3 treinos!") para aumentar aderência
5. **Contextualização com wellness + Feature Store:** Se `fatigue_score` > 7 ou `sleep` < 6h → sugerir repouso/recovery baseado em dados do atleta; se `performance_gap.velocity` > 15% → sugerir treino técnico específico
6. **Referência a histórico:** Se missing sessions detectadas → oferecer compensatório personalizado (via features: fadiga, posição, objetivos de treino)
7. **Age-appropriate language:** Adaptar tom, complexidade e incentivos à `ageGroup` (U10-U12 = simples/lúdico, ADULT = técnico/performance)
8. **Especialização por posição:** Respostas sobre técnica/tática adaptadas à posição do atleta (pointeira ≠ golaço ≠ armador ≠ goleiro)
8. **Position-specific tips:** Quando apropriado, dar dicas especializadas para a posição do atleta (Ponta, Armador, Pivô, Goleiro)

**Resoluções:**
- Adicionar endpoints ao OpenAPI + refEFERENCIAR contratos de schemas abaixo antes de implementar UIF-006
- Schemas pendentes: 
  - `athlete_chat_message.v1.json`
  - `athlete_chat_conversation.v1.json`
  - `training_suggestion.v1.json`
  - `training_suggestion_approval.v1.json`
- **Integração LLM:** Backend deve integrar LLM provider (e.g., OpenAI, Azure OpenAI, Anthropic) com system prompt especializado em handebol + context injection

---

### Sumário de Gaps

> **Decisão D-UI-19 (2026-03-17):** Todos os gaps G-01 a G-05 são **MVP v1.0**. Status atualizado abaixo.

> **Decisão D-UI-22 (2026-03-17):** Gap G-06 (HB Pro Coach) é **MVP v1.1** — depende de aprovação de LLM provider e refinamento de behavioral rules durante implementacao.

| Gap | Afeta | Status |
|-----|-------|--------|
| G-01 Recommendations | UIF-001 [5] | ✅ Resolvido — `listRecommendations`, `acceptRecommendation`, `dismissRecommendation` adicionados ao `training.yaml` (2026-03-17) |
| G-02 Ineligibility | UIF-002 [5] | ✅ Resolvido — `submitIneligibilityDeclaration`, `getIneligibilityStatus` adicionados ao `training.yaml` (2026-03-17) |
| G-03 Attention Queue Actions | UIF-003 [6] | ✅ Resolvido — `resolveAttentionQueueItem`, `dismissAttentionQueueItem`, `escalateAttentionQueueItem` adicionados ao `training.yaml` (2026-03-17) |
| G-04 Close Feedback Thread | UIF-003 [5] | ✅ Resolvido — `closeFeedbackThread` adicionado ao `training.yaml` (2026-03-17) |
| G-05 Load Chart | UIF-005 [1] | ✅ Resolvido — `getLoadChart` adicionado ao `training.yaml` (2026-03-17) |
| G-06 HB Pro Coach Chat | UIF-006 [1,2,3] | ⏳ **NOVO — MVP v1.1**: `listChatMessages`, `sendChatMessage`, `generateCoachResponse`, `submitTrainingSuggestion`, `notifyCoachTrainingSuggestion` **pendentes** de adição ao OpenAPI. Requer integração ai_ingestion (Feature Store) + regras especializadas em handebol + schemas. |

> **Status resumido em 2026-03-17:**
> - **G-01 a G-05:** ✅ Resolvidos — 9 endpoints já adicionados ao OpenAPI (2026-03-17)
> - **G-06:** ⏳ Novo feature (HB Pro Coach com Feature Store) — bloqueado até aprovação de arquitetura (ai_ingestion integration) e schedule de implementação
> - **Schemas pendentes de criação:** `recommendation.yaml`, `athlete_ineligibility_declaration.yaml`, `load_chart.yaml`, `athlete_chat_message.yaml`, `athlete_chat_conversation.yaml`, `training_suggestion.yaml` em `contracts/schemas/training/`.

---

## Versionamento

- **Version:** 1.2.0 (implementation_candidates — G-01 a G-05 ready, G-06 scoped)
- **Changelog:**
  - 0.1.0 — flows UIF-001 a UIF-005, decisões D-UI-15/16, SP-01 a SP-04
  - 0.2.0 — YAML frontmatter, endpoint maps por UIF, gaps G-01 a G-05 documentados
  - 0.3.0 — decisões D-UI-17 (PWA), D-UI-18 (Next.js stack), D-UI-19 (gaps = MVP); roadmap atualizado
  - 1.0.0 — todos os gaps G-01 a G-05 resolvidos; 9 endpoints adicionados ao OpenAPI; 3 schemas criados
  - 1.1.0 — Parte 1 com tokens canônicos (tipografia, cores semânticas, spacing, dark mode); Parte 3 com mapeamento visual → componentes; token `semantic.success` (emerald-500) definido
  - 1.2.0 — **NEW**: UIF-TRAINING-006 (HB Pro Coach Chat) adicionado; decisões D-UI-20/21 (Coach baseado em Feature Store + regras, integrado com ai_ingestion); Gap G-06 documentado com endpoints + behavioral rules; AsyncAPI integration scoped para training suggestion approval workflow; atualização arquitetural: Coach interno (não LLM externo) especializado em cada atleta

---

## Sign-off

- [ ] Product Owner: Aprovó design?
- [ ] UX Designer: Aprovó accessibility?
- [ ] Engineering Lead: Aprovó implementability?

**Status:** IMPLEMENTATION_READY — Await sign-off

