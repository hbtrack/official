# DESIGN_SYSTEM

## 1. Princípios visuais

### 1.1 Direção visual
A interface adota uma estética de produto interno moderno, com:
- base neutra
- contraste suave
- componentes compactos
- uso funcional de cor para status
- foco em legibilidade e densidade de informação controlada

### 1.2 Características principais
- superfícies claras com contraste baixo a médio
- suporte nativo a dark mode
- cantos arredondados moderados
- uso consistente de bordas em vez de sombras pesadas
- tipografia utilitária, com ênfase em clareza
- feedback semântico por cor para erro, alerta, rascunho e revisão

---

## 2. Tipografia

## 2.1 Família tipográfica
O código não explicita a fonte, então o sistema assume a stack padrão do app com perfil neutro, compatível com produtos SaaS:

```ts
fontFamily: {
  sans: [
    'Inter',
    'ui-sans-serif',
    'system-ui',
    '-apple-system',
    'BlinkMacSystemFont',
    '"Segoe UI"',
    'sans-serif',
  ],
}
````

### 2.2 Escala tipográfica inferida

#### Títulos

* `text-lg font-medium`

  * usado em headings de empty state
  * função: título de bloco ou estado

#### Corpo

* `text-sm`

  * texto principal secundário
  * descrições, mensagens, feedbacks

#### Microcopy

* `text-xs`

  * indicadores compactos
  * contadores, badges textuais

#### Meta / auxiliar

* `text-[10px]`

  * labels muito compactas
  * apoio visual em painéis menores

### 2.3 Pesos tipográficos

* `font-medium`: principal peso de ênfase
* `font-normal`: corpo padrão implícito
* `font-semibold`: não aparece explicitamente no trecho, mas pode ser previsto para evolução

### 2.4 Hierarquia recomendada

* Heading principal de seção: `text-lg font-medium`
* Subheading / bloco auxiliar: `text-sm font-medium`
* Texto descritivo: `text-sm`
* Meta informação: `text-xs`
* Micro label: `text-[10px]`

---

## 3. Cores

## 3.1 Fundo global

### Light

* `#f6f6f8`

  * fundo da página
  * aparência neutra, levemente aquecida

### Dark

* `#111621`

  * fundo principal escuro
  * usado no wrapper da página

## 3.2 Superfícies

### Light

* `#ffffff`

  * cards e estados vazios

### Dark

* `#0f0f0f`

  * superfície escura profunda para blocos

## 3.3 Neutros / Slate / Gray

Tokens inferidos via classes Tailwind:

* `slate-900`
* `slate-800`
* `slate-700`
* `slate-500`
* `slate-400`
* `slate-300`
* `slate-200`
* `gray-100`
* `gray-400`
* `gray-500`

Uso:

* texto principal: `slate-900`
* texto secundário: `slate-500`
* texto auxiliar dark mode: `slate-400` / `slate-300`
* fundos utilitários: `gray-100`
* ações compactas: `gray-400` e hover `gray-500`

## 3.4 Semânticas

### Alerta / revisão pendente

* border: `amber-200`
* bg: `amber-50`
* text: `amber-700`

Dark:

* border: `amber-800`
* bg: `amber-900/20`
* text: `amber-300`

### Erro

* border: `red-200`
* bg: `red-50`
* text heading: `red-800`
* text body: `red-700`
* icon/action: `red-600`

Dark:

* border: `red-800`
* bg: `red-900/20`
* heading: `red-300`
* body/icon: `red-400`

### Sucesso / objetivo alcançado / readiness alto

Usado para: sessão completa, readiness ≥ 70, objetivo alcançado, check-in bem-sucedido, wellness-indicator verde.

* bg: `emerald-50`
* border: `emerald-200`
* text: `emerald-700`
* icon/action: `emerald-500` (`#10b981`)

Dark:

* bg: `emerald-900/20`
* border: `emerald-800`
* text: `emerald-300`

### Info / rascunho / destaque momentâneo

* info icon: `slate-500` / `slate-400`
* highlight temporário: `ring-blue-400`
* botão contextual: `bg-gray-400 hover:bg-gray-500 text-white`

## 3.5 Paleta consolidada

```ts
colors: {
  page: {
    light: '#f6f6f8',
    dark: '#111621',
  },
  surface: {
    light: '#ffffff',
    dark: '#0f0f0f',
  },
  text: {
    primary: {
      light: 'rgb(15 23 42)',   // slate-900
      dark: '#ffffff',
    },
    secondary: {
      light: 'rgb(100 116 139)', // slate-500
      dark: 'rgb(148 163 184)',  // slate-400
    },
    muted: {
      light: 'rgb(148 163 184)', // slate-400
      dark: 'rgb(203 213 225)',  // slate-300
    },
  },
  border: {
    light: 'rgb(226 232 240)',   // slate-200
    dark: 'rgb(30 41 59)',       // slate-800
  },
  semantic: {
    warning: {
      lightBg: 'rgb(255 251 235)',   // amber-50
      lightBorder: 'rgb(253 230 138)', // amber-200
      lightText: 'rgb(180 83 9)',    // amber-700
      darkBg: 'rgb(120 53 15 / 0.2)',
      darkBorder: 'rgb(146 64 14)',  // amber-800
      darkText: 'rgb(252 211 77)',   // amber-300
    },
    danger: {
      lightBg: 'rgb(254 242 242)',   // red-50
      lightBorder: 'rgb(254 202 202)', // red-200
      lightText: 'rgb(185 28 28)',   // red-700
      lightHeading: 'rgb(153 27 27)', // red-800
      darkBg: 'rgb(127 29 29 / 0.2)',
      darkBorder: 'rgb(153 27 27)',  // red-800
      darkText: 'rgb(248 113 113)',  // red-400
      darkHeading: 'rgb(252 165 165)', // red-300
    },
    success: {
      lightBg: 'rgb(236 253 245)',   // emerald-50
      lightBorder: 'rgb(167 243 208)', // emerald-200
      lightText: 'rgb(4 120 87)',    // emerald-700
      lightIcon: 'rgb(16 185 129)',  // emerald-500 (#10b981)
      darkBg: 'rgb(6 78 59 / 0.2)',  // emerald-900/20
      darkBorder: 'rgb(6 95 70)',    // emerald-800
      darkText: 'rgb(110 231 183)',  // emerald-300
    },
    info: {
      icon: {
        light: 'rgb(100 116 139)', // slate-500
        dark: 'rgb(148 163 184)',  // slate-400
      },
      ring: 'rgb(96 165 250)', // blue-400
    },
  },
}
```

---

## 4. Spacing

## 4.1 Espaçamentos identificados

* `px-2`
* `px-3`
* `px-4`
* `px-6`
* `lg:px-10`
* `py-1`
* `py-2`
* `py-4`
* `p-6`
* `p-12`
* `mb-2`
* `mb-4`
* `mb-6`
* `mt-1`
* `mt-2`
* `mt-8`
* `gap-1`
* `gap-2`
* `gap-3`

### 4.2 Escala recomendada

```ts
spacing: {
  1: '0.25rem',   // 4px
  2: '0.5rem',    // 8px
  3: '0.75rem',   // 12px
  4: '1rem',      // 16px
  6: '1.5rem',    // 24px
  8: '2rem',      // 32px
  10: '2.5rem',   // 40px
  12: '3rem',     // 48px
}
```

### 4.3 Regras de uso

* elementos compactos: spacing 1–2
* conteúdo interno de banners e pills: spacing 2–4
* cards e blocos de estado: spacing 6
* estados vazios robustos: spacing 12
* separação entre blocos principais: margin 6–8

---

## 5. Layout

## 5.1 Container principal

```ts
layout: {
  pageMaxWidth: '1600px',
  pagePaddingX: {
    base: '1.5rem', // px-6
    lg: '2.5rem',   // px-10
  },
  pagePaddingY: '1rem', // py-4
}
```

### 5.2 Estrutura

* wrapper vertical com `min-h-screen`
* `main` centralizado com `mx-auto`
* largura máxima generosa para agenda densa
* layout preparado para visualização semanal e mensal

### 5.3 Alinhamentos recorrentes

* blocos de feedback no fluxo vertical
* ações auxiliares alinhadas à direita
* conteúdo de empty state centralizado
* elementos internos com `flex items-center` e `gap-*`

---

## 6. Bordas, radius e sombras

## 6.1 Radius identificados

* `rounded-md`
* `rounded-lg`
* `rounded-full`

### Uso recomendado

* `rounded-md`

  * badges maiores
  * painéis compactos
* `rounded-lg`

  * cards, estados, banners
* `rounded-full`

  * ícones circulares e elementos decorativos

## 6.2 Bordas

* uso frequente de `border`
* bordas comunicam estrutura com mais força que sombras
* contraste de borda adaptado para dark mode

## 6.3 Shadows

* `shadow-sm`
* hover também mantém `shadow-sm`

A sombra é discreta e subordinada à borda.

### Tokens recomendados

```ts
radius: {
  sm: '0.375rem',
  md: '0.5rem',
  lg: '0.75rem',
  full: '9999px',
},

shadow: {
  sm: '0 1px 2px rgba(0, 0, 0, 0.05)',
  none: 'none',
}
```

## 7. Componentes 

## 7.1 Page shell

Características:

* fundo global neutro
* altura mínima da viewport
* container centralizado
* espaçamento horizontal responsivo

## 7.2 Alert banner

Usado para:

* treinos aguardando revisão operacional

Estrutura:

* banner simples
* cor semântica de alerta
* tipografia `text-sm`
* border + bg + text coerentes

Padrão:

```ts
components: {
  alertBanner: {
    borderRadius: '0.75rem',
    paddingX: '1rem',
    paddingY: '0.5rem',
    fontSize: '0.875rem',
    fontWeight: 400,
  },
}
```

## 7.3 Compact status pill

Usado para:

* contador de rascunhos
* CTA secundário de foco visual

Características:

* largura ajustada ao conteúdo (`w-fit`)
* alinhamento à direita (`ml-auto`)
* interior com flex horizontal
* microtipografia
* botão embutido pequeno

## 7.4 Empty state card

Estrutura:

* card com fundo e borda
* ícone circular destacado
* título + descrição
* alinhamento central

Padrão visual:

* container generoso (`p-12`)
* ícone em disco circular `w-16 h-16`
* título `text-lg font-medium`
* descrição `text-sm`

## 7.5 Error card

Estrutura:

* card semântico vermelho
* ícone à esquerda
* conteúdo textual empilhado
* ação inline com hover underline

## 7.6 Action micro button

Botão compacto identificado no bloco de rascunhos:

* `px-2 py-1`
* `text-[10px] font-medium`
* `rounded`
* fundo médio com hover mais escuro
* ícone pequeno

---

## 8. Ícones

## 8.1 Padrões observados

* ícones pequenos: `h-3 w-3`
* ícones médios: `w-6 h-6`
* ícones grandes em empty state: `w-8 h-8`

### Escala recomendada

```ts
iconSize: {
  xs: '0.75rem',  // 12px
  sm: '1rem',     // 16px
  md: '1.5rem',   // 24px
  lg: '2rem',     // 32px
}
```

## 9. Estados de interface

## 9.1 Sem equipe selecionada

Objetivo:

* orientar o usuário a escolher um contexto antes da agenda aparecer

Padrão:

* card centralizado
* ícone representativo
* mensagem direta
* sem CTA primário agressivo

## 9.2 Erro de carregamento

Objetivo:

* informar falha de carregamento
* permitir retry imediato

Padrão:

* semântica danger
* título + descrição + ação
* visual de alta clareza

## 9.3 Busca sem resultados

Objetivo:

* explicar ausência de resultados
* oferecer reversão rápida do filtro

Padrão:

* componente `EmptyState`
* ícone de busca
* CTA “Limpar filtros”

## 9.4 Destaque contextual temporário

Objetivo:

* levar o usuário até o primeiro draft
* aplicar foco visual transitório

Padrão:

* `scrollIntoView`
* `ring-2`
* `ring-blue-400`
* `ring-offset-2`

## 10. Modo escuro

## 10.1 Estratégia

O dark mode não inverte simplesmente as cores; ele redefine:

* fundo global
* superfícies
* bordas
* contraste tipográfico
* semânticas com opacidade controlada

## 10.2 Regras

* fundo de página escuro profundo
* superfícies quase pretas
* textos claros em escala slate
* semânticas em tons suavizados com alpha
* bordas escuras continuam estruturando os blocos

## 11. Densidade e ritmo visual

### 11.1 Densidade

A interface sugere densidade média:

* muitas informações por tela
* blocos compactos
* espaçamentos suficientes para escaneabilidade

### 11.2 Ritmo

O ritmo é construído por:

* margens verticais de 16px a 32px
* agrupamentos internos com `gap-2` e `gap-3`
* títulos curtos e descrições objetivas
* banners e estados posicionados antes do conteúdo principal

## 12. Tokens recomendados

```ts
export const designSystem = {
  fontFamily: {
    sans: [
      'Inter',
      'ui-sans-serif',
      'system-ui',
      '-apple-system',
      'BlinkMacSystemFont',
      '"Segoe UI"',
      'sans-serif',
    ],
  },

  fontSize: {
    micro: '10px',
    xs: '12px',
    sm: '14px',
    base: '16px',
    lg: '18px',
  },

  fontWeight: {
    normal: 400,
    medium: 500,
    semibold: 600,
  },

  lineHeight: {
    tight: 1.2,
    normal: 1.5,
    relaxed: 1.6,
  },

  colors: {
    page: {
      light: '#f6f6f8',
      dark: '#111621',
    },
    surface: {
      light: '#ffffff',
      dark: '#0f0f0f',
    },
    text: {
      primary: {
        light: 'rgb(15 23 42)',
        dark: '#ffffff',
      },
      secondary: {
        light: 'rgb(100 116 139)',
        dark: 'rgb(148 163 184)',
      },
      muted: {
        light: 'rgb(148 163 184)',
        dark: 'rgb(203 213 225)',
      },
    },
    border: {
      light: 'rgb(226 232 240)',
      dark: 'rgb(30 41 59)',
    },
    neutral: {
      gray100: 'rgb(243 244 246)',
      gray400: 'rgb(156 163 175)',
      gray500: 'rgb(107 114 128)',
      slate300: 'rgb(203 213 225)',
      slate400: 'rgb(148 163 184)',
      slate500: 'rgb(100 116 139)',
      slate700: 'rgb(51 65 85)',
      slate800: 'rgb(30 41 59)',
      slate900: 'rgb(15 23 42)',
    },
    success: {
      bgLight: 'rgb(236 253 245)',    // emerald-50
      borderLight: 'rgb(167 243 208)', // emerald-200
      textLight: 'rgb(4 120 87)',     // emerald-700
      iconLight: 'rgb(16 185 129)',   // emerald-500 (#10b981)
      bgDark: 'rgb(6 78 59 / 0.2)',   // emerald-900/20
      borderDark: 'rgb(6 95 70)',     // emerald-800
      textDark: 'rgb(110 231 183)',   // emerald-300
    },
    warning: {
      bgLight: 'rgb(255 251 235)',
      borderLight: 'rgb(253 230 138)',
      textLight: 'rgb(180 83 9)',
      bgDark: 'rgb(120 53 15 / 0.2)',
      borderDark: 'rgb(146 64 14)',
      textDark: 'rgb(252 211 77)',
    },
    danger: {
      bgLight: 'rgb(254 242 242)',
      borderLight: 'rgb(254 202 202)',
      titleLight: 'rgb(153 27 27)',
      textLight: 'rgb(185 28 28)',
      bgDark: 'rgb(127 29 29 / 0.2)',
      borderDark: 'rgb(153 27 27)',
      titleDark: 'rgb(252 165 165)',
      textDark: 'rgb(248 113 113)',
    },
    info: {
      ring: 'rgb(96 165 250)',
    },
    white: '#ffffff',
  },

  spacing: {
    1: '4px',
    2: '8px',
    3: '12px',
    4: '16px',
    6: '24px',
    8: '32px',
    10: '40px',
    12: '48px',
  },

  radius: {
    sm: '6px',
    md: '8px',
    lg: '12px',
    full: '9999px',
  },

  shadow: {
    sm: '0 1px 2px rgba(0, 0, 0, 0.05)',
    none: 'none',
  },

  iconSize: {
    xs: '12px',
    sm: '16px',
    md: '24px',
    lg: '32px',
  },

  layout: {
    minPageHeight: '100vh',
    maxWidth: '1600px',
    paddingX: {
      base: '24px',
      lg: '40px',
    },
    paddingY: {
      base: '16px',
    },
  },

  components: {
    alertBanner: {
      radius: '12px',
      paddingX: '16px',
      paddingY: '8px',
      fontSize: '14px',
    },
    compactPill: {
      radius: '8px',
      paddingX: '12px',
      paddingY: '8px',
    },
    emptyStateCard: {
      radius: '12px',
      padding: '48px',
      iconWrapper: '64px',
    },
    microButton: {
      paddingX: '8px',
      paddingY: '4px',
      fontSize: '10px',
      radius: '6px',
      shadow: '0 1px 2px rgba(0, 0, 0, 0.05)',
    },
  },
} as const;
```

## 13. Diretrizes de implementação

### 13.1 Para novos componentes

Novos componentes da agenda devem seguir:

* superfícies claras e bordas suaves
* tipografia compacta
* spacing em múltiplos de 4
* semânticas já estabelecidas
* dark mode com contraste equivalente

### 13.2 Para consistência

Evitar:

* sombras fortes
* cores saturadas fora do sistema semântico
* excesso de tamanhos tipográficos
* padding arbitrário fora da escala
* CTAs visuais desproporcionais ao contexto

### 13.3 Para evolução

Este design system pode ser expandido depois para incluir:

* tokens de calendário
* grid da agenda semanal
* cards de sessão
* estados de drag and drop
* modais de criação e edição
* dropdown de equipe
* sistema completo de status dos treinos


