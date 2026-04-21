---
doc_type: canon
version: "1.0.0"
status: active
state_semantics: target-state
owner: product-owner
related_docs:
  - docs/_canon/FRONTEND_CONTRACT.md
  - docs/_canon/decisions/ADR-030-frontend-strategy.md
---

# UX_BRAND_CONTRACT.md

## 0. Objetivo
Define a identidade visual normativa do HB Track Web.

## 1. Princípios visuais
- O app deve comunicar software profissional de alto rendimento esportivo.
- A interface deve privilegiar leitura operacional e densidade informacional.
- Regra canônica: densidade > impacto; dados primeiro.
- A área autenticada não deve usar linguagem visual de landing page.

## 2. Tipografia oficial
- Base: Inter
- Títulos: Manrope
- Monoespaçada: JetBrains Mono

## 3. Assets oficiais de marca
Todos os assets oficiais de marca do frontend devem ser consumidos a partir de `generated/images`.

### Assets canonizados
- `generated/images/logo.svg`
- `generated/images/logo-dark.svg`
- `generated/images/logo-icon.svg`
- `generated/images/logo-icon-dark.svg`
- `generated/images/auth-logo.svg`
- `generated/images/auth-logo-dark.svg`
- `generated/images/hbicon.ico`

### Regras
- É proibido substituir a marca por texto cru "HB Track" em staging aprovado ou produção.
- É proibido duplicar assets de marca fora do diretório canônico sem decisão formal.
- O favicon oficial deve ser `generated/images/hbicon.ico`.

## 4. Microcopy institucional da auth
- tagline oficial inicial: "Dados que decidem jogos"

## 5. Paleta canônica
### Família principal
- brand-25 a brand-950

### Famílias auxiliares
- gray-25 a gray-950
- success-25 a success-950
- error-25 a error-950
- warning-25 a warning-950
- orange-25 a orange-950

### Tokens específicos de handebol
- court
- goal-area
- shot-success
- shot-miss
- save
- turnover
- load-deficit
- load-optimal
- load-excess

## 6. Escala visual do app
- Nenhum título de app deve exceder 18px sem justificativa documental.
- A UI deve priorizar controle, legibilidade e densidade.

## 7. Light/Dark mode
- O sistema deve suportar light e dark mode.
- Os assets e tokens devem ser coerentes em ambos os modos.

## 8. Critérios de aceite
Uma tela só pode ser aprovada se:
- usar tipografia oficial
- usar assets oficiais
- usar tokens canônicos
- respeitar a escala visual do app
- respeitar light/dark mode quando aplicável

### Regras

- E proibido substituir a marca por texto cru `HB Track` em staging aprovado ou producao.
- E proibido duplicar logos em paths paralelos sem decisao documental.
- O favicon oficial deve ser `generated/images/hbicon.ico`.

## 4. Paleta canonica

### Familia principal

- `brand-25` a `brand-950`

### Familias auxiliares

- `gray-25` a `gray-950`
- `success-25` a `success-950`
- `error-25` a `error-950`
- `warning-25` a `warning-950`
- `orange-25` a `orange-950`

### Tokens especificos de handebol

- `court`
- `goal-area`
- `shot-success`
- `shot-miss`
- `save`
- `turnover`
- `load-deficit`
- `load-optimal`
- `load-excess`

### Regras

- Componentes devem consumir tokens, nao hex solto em JSX, salvo excecao documentada.
- Tokens semanticos devem existir em light e dark mode.

## 5. Escala visual do app

### Regra geral

- Nenhum titulo de app deve exceder 18px sem justificativa documental.
- A UI deve priorizar controle, legibilidade e densidade.

### Classes conceituais obrigatorias

- `app-title`
- `app-subtitle`
- `app-card`
- `app-card-header`
- `app-card-title`
- `app-card-body`
- `app-card-footer`
- `app-section-title`
- `app-section-description`
- `app-table-header`

## 6. Modo claro/escuro

- O sistema deve suportar dark mode.
- A marca deve possuir variacoes compativeis.
- Nenhuma tela critica pode depender exclusivamente do modo claro.

## 7. Criterios de aceite

Uma tela so pode ser aprovada se:

- usar tipografia oficial
- usar assets oficiais de marca
- usar tokens canonicos
- respeitar a escala visual do app
- respeitar light/dark mode quando aplicavel
