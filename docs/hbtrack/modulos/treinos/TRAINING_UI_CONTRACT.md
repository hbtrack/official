# TRAINING_UI_CONTRACT.md

Status: NORMATIVO_VIGENTE  
Versão: v1.1.0  
Tipo de Documento: SSOT Normativo — Front-Back Contract  
Módulo: TRAINING  
Autoridade: UI_ARCHITECTURE_LAYER  
Última revisão: 2026-03-09  
Dependências:

* `DONE_CONTRACT_TRAINING.md`
* `TRAINING_STATE_MACHINE.yaml`
* `TRAINING_SCREENS_SPEC.md`
* `TRAINING_USER_FLOWS.md`
* `TRAINING_PERF_LIMITS.json`

---

# 1. Objetivo

Definir **a gramática estrutural da UI do módulo TRAINING**.

Este contrato existe para impedir que agentes de código:

* inventem estilos
* inventem layout
* criem componentes arbitrários
* quebrem design tokens
* omitirem `data-test-id`
* introduzam lógica de domínio em componentes visuais

A UI do módulo TRAINING deve ser **determinística, auditável e testável**.

---

# 2. Princípios

## 2.1 UI como gramática

A UI do sistema não é montada livremente.

Ela deve seguir a gramática:

```
Page
 └ Layout
     └ Section
         └ Primitive Components
```

O agente **não pode quebrar essa hierarquia**.

---

## 2.2 Composição proibitiva

Telas devem ser **composição de primitives**.

Nunca criar:

```
AttendanceCard
WellnessBox
CoachPanel
TrainingBlock
```

Esses são **anti-patterns de domínio na UI**.

---

## 2.3 UI sem lógica de domínio

Componentes visuais devem ser **pure functions**.

Proibido:

```
fetch
mutations
business logic
state machines
```

Essas responsabilidades pertencem a:

```
hooks
services
controllers
```

---

# 3. Design Tokens

Todos os estilos devem derivar exclusivamente de tokens.

Tokens são definidos em:

```
src/design/tokens.ts
```

## 3.1 Espaçamento

Permitido:

```
spacing.xs
spacing.sm
spacing.md
spacing.lg
spacing.xl
```

Proibido:

```
margin: 13px
padding: 7px
gap: 11px
```

---

## 3.2 Cores

Permitido:

```
colors.primary
colors.background
colors.surface
colors.border
colors.text
colors.muted
```

Proibido:

```
#FFFFFF
#000
rgb()
hsl()
```

---

## 3.3 Tipografia

Permitido:

```
typography.body
typography.label
typography.title
typography.subtitle
```

Proibido:

```
font-size manual
font-family manual
font-weight manual
```

---

# 4. Primitive Components Permitidos

O agente só pode importar componentes de:

```
@/design/primitives
```

Lista autorizada:

```
Button
Card
Box
Stack
Grid
Typography
Input
Select
Textarea
Badge
Tabs
Modal
Divider
Icon
Table
Loader
```

Qualquer outro componente exige **AR aprovado**.

---

# 5. Layout Components

Layouts permitidos:

```
PageLayout
DashboardLayout
FormLayout
ModalLayout
```

Regra:

```
Toda SCREEN deve começar em PageLayout
```

Arquivos canônicos (obrigatórios, em `src/design/layouts/`):

| Layout | Responsabilidade | max-width |
|---|---|---|
| `PageLayout` | Shell da página: background, altura mínima | — |
| `DashboardLayout` | Container administrativo: largura máxima, padding | `tokens.layout.pageMaxWidth` |
| `FormLayout` | Container de formulários narrow | `tokens.layout.contentMaxWidth` |
| `ModalLayout` | Wrapper de modais | — |

Valor canônico de `tokens.layout.pageMaxWidth`: **1600px** (decisão arquitetural registrada em 2026-03-09).
Este valor é global — todos os módulos que consumirem `tokens.layout.pageMaxWidth` herdam esse valor.
Proibido hardcode de qualquer largura máxima nos arquivos de layout.

---

# 6. Structural Grammar

Toda tela deve seguir:

```
PageLayout
 └ DashboardLayout  (ou FormLayout, conforme o tipo de tela)
     └ Stack
         ├ HeaderSection
         ├ AlertSection    (opcional — conditional render)
         ├ ContentSection
         └ ModalZone       (portais, isolados do fluxo de layout)
```

O padrão canônico de composição de página administrativa é **estrutura visual**,
não comportamento funcional. As seções são slots — o que vai em cada slot é
definido pela `TRAINING_SCREENS_SPEC.md`, não por este contrato.

Nenhuma implementação específica de tela existente no módulo é autoridade normativa
deste padrão. O padrão foi derivado por decisão arquitetural de design system.

---

# 6.1 Separação obrigatória de camadas

O agente deve respeitar três camadas distintas:

| Camada | Definida por | Este contrato toca? |
|---|---|---|
| **Estrutura visual canônica** | `TRAINING_UI_CONTRACT.md`, `tokens.ts`, `src/design/layouts/` | ✅ SIM |
| **Semântica funcional da tela** | `TRAINING_SCREENS_SPEC.md`, `TRAINING_USER_FLOWS.md` | ❌ NÃO |
| **Contrato FE↔BE** | `TRAINING_FRONT_BACK_CONTRACT.md`, `openapi.json` | ❌ NÃO |

Regras:
- Uma decisão de design system **não modifica** semântica funcional nem contrato de dados.
- Uma tela **não pode** exportar tokens ou definir estrutura de layout.
- Um contrato de dados **não pode** impor affordances visuais.
- Se o agente precisar decidir sobre estado de sessão, payload ou fluxo: parar e consultar a camada correta.

---

## 6.1 HeaderSection

Contém:

```
title
subtitle
context badges
```

---

## 6.2 ContentSection

Contém:

```
cards
tables
forms
lists
```

---

## 6.3 ActionSection

Contém:

```
primary action
secondary actions
```

---

# 7. Action Slots (Obrigatórios)

O layout define slots fixos.

O agente **não pode posicionar ações manualmente**.

Slots disponíveis:

```
primary-action
secondary-action
danger-action
```

Exemplo:

```
<PageLayout
  primaryAction={<Button />}
>
```

---

# 8. Input Controls

Inputs devem ser sempre wrappers de primitives.

Exemplo permitido:

```
<Input
  testId="training-attendance-input"
  label="Carga"
  type="number"
/>
```

Proibido:

```
<input type="number" />
```

---

# 9. Selectors de Teste

Todo primitive exige `testId`.

TypeScript obrigatório:

```
interface PrimitiveProps {
  testId: string
}
```

Exemplo:

```
<Button testId="training-attendance-save" />
```

---

## 9.1 Convenção de nome

Formato obrigatório:

```
module-entity-action
```

Exemplos:

```
training-attendance-save
training-wellness-submit
training-ai-apply-draft
training-session-start
```

---

# 10. UI State Machine

Componentes devem respeitar os estados definidos em:

```
TRAINING_STATE_MACHINE.yaml
```

UI só pode renderizar estados:

```
loading
empty
ready
error
readonly
```

Proibido:

```
estado inventado
```

---

# 11. Hooks de Dados

UI só pode acessar dados via hooks.

Permitido:

```
useTrainingSession()
useAttendance()
useWellness()
useAiDraft()
```

Proibido:

```
fetch()
axios()
direct API calls
```

---

# 12. Forbidden Patterns

O agente não pode gerar:

### CSS inline com valores arbitrários em layouts e páginas

```tsx
// PROIBIDO em layouts (PageLayout, DashboardLayout, FormLayout) e em páginas/telas:
<div style={{ padding: "13px", color: "#ff0000" }}>

// PERMITIDO em primitives (Button, Card etc.) quando consume exclusivamente tokens:
<button style={{ background: tokens.colors.action.primary }}>
```

A regra é: `style={{}}` com **tokens** é permitido em primitives. `style={{}}` com valores
literais, hex ou números arbitrários é proibido em qualquer arquivo.

### valores arbitrários Tailwind

```
p-[17px]
max-w-[1600px]   ← proibido mesmo que coincida com o token canônico
```

Use sempre tokens. Nunca repita o valor numérico de um token no JSX.

### classes Tailwind parametrizadas para spacing/layout em layouts

```tsx
// PROIBIDO em DashboardLayout, FormLayout, PageLayout:
<main className="px-6 lg:px-8 py-4">

// CORRETO — consumir tokens via style:
<main style={{ paddingInline: tokens.spacing.xl, paddingBlock: tokens.spacing.lg }}>
```

### cores hardcoded

```
bg-[#ff0000]
#FFFFFF
rgb()
hsl()
```

### div layout

```
<div className="flex">
```

Layout deve usar:

```
Stack
Grid
Box
```

---

# 13. Component Pollution

Proibido criar componentes:

```
AttendanceCard
WellnessCard
CoachSuggestionBox
TrainingBlock
```

Motivo:

Componentes de domínio acoplam lógica.

A UI deve compor primitives.

---

# 14. Enforcement Tools

## Tailwind Strict Mode

`tailwind.config.ts`

```
disallow arbitrary values
```

---

## Stylelint

Regras obrigatórias:

```
no-inline-style
no-hex-color
no-rgb
no-hsl
```

---

## ESLint

Regras:

```
no-div-layout
no-inline-css
```

---

# 15. Performance Constraints

A UI deve respeitar limites definidos em:

```
TRAINING_PERF_LIMITS.json
```

Exemplo:

```
agenda_load < 2000ms
attendance_submit < 3000ms
```

---

# 16. Test Compatibility

Toda tela deve ser compatível com:

```
Playwright
Traceability Matrix
Side Effect Validation
```

Sem `testId`, o componente é **inválido**.

---

# 17. Evidence Compatibility

A UI deve permitir:

```
E2E validation
visual regression
state machine verification
side effect verification
```

---

# 18. Fail Conditions

A implementação UI falha automaticamente se ocorrer:

* hex color em qualquer arquivo
* `style={{}}` com valor literal/arbitrário (números, hex, rgb) em layouts ou páginas
* `style={{}}` com qualquer valor não derivado de `tokens.*` em primitives
* classe Tailwind parametrizada para spacing/layout em arquivos de layout (`px-6`, `lg:px-8`, `max-w-[...]`)
* primitive ausente (criar componente de domínio como `AttendanceCard`)
* missing `testId` / `data-test-id`
* layout fora da gramática canônica
* criação de componente não registrado
* API call direta (`fetch`, `axios`)
* estado não definido na state machine
* tela decidindo sobre payload ou contrato FE↔BE (cruzamento de camada proibido)

---

# 19. Autoridade

Este contrato tem precedência sobre:

```
component implementations
style decisions
agent prompts
```

Em caso de conflito:

```
TRAINING_UI_CONTRACT.md vence
```

---
