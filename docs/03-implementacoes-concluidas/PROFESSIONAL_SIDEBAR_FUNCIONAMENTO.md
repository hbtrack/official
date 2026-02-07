<!-- STATUS: DEPRECATED | implementacao concluida -->

# Professional Sidebar - Documentação Técnica
**Arquivo**: `src/components/Layout/ProfessionalSidebar.tsx`  
**Data**: 2026-01-04  
**Status**: ✅ Implementado e Funcional

---

## 1. Visão Geral

A **Professional Sidebar** é o componente de navegação principal do HB Track, implementado como uma barra lateral colapsável com suporte a:

- ✅ **Menu hierárquico** com submenus expansíveis
- ✅ **RBAC** (Role-Based Access Control) integrado
- ✅ **Tema claro/escuro** sincronizado
- ✅ **Estado colapsado/expandido** com transições suaves
- ✅ **Responsividade** para mobile
- ✅ **Active state** automático baseado na rota

---

## 2. Estrutura Visual

### Estados da Sidebar

#### Estado Expandido (220px)
```
┌─────────────────────────┐
│  [Logo HB Track]    [<] │  ← Header (64px altura)
├─────────────────────────┤
│  🏠 Página Inicial      │
│  💬 Mensagens           │
│  📊 Dashboard           │
│  ➕ Cadastro            │
│  👥 Equipes             │
│  🏃 Atletas             │
│  📹 Scout ao Vivo       │
│                         │
│  📊 Estatísticas     ▼  │  ← Submenu expansível
│    ├─ Operacional       │
│    ├─ Equipes           │
│    └─ Atletas           │
│                         │
│  📅 Eventos          ▼  │  ← Submenu expansível
│    ├─ Calendário        │
│    ├─ Competições       │
│    └─ Treinos           │
│                         │
└─────────────────────────┘
```

#### Estado Colapsado (64px)
```
┌─────┐
│ [🏠]│  ← Ícone do logo
├─────┤
│ 🏠  │
│ 💬  │
│ 📊  │
│ ➕  │
│ 👥  │
│ 🏃  │
│ 📹  │
│ 📊  │
│ 📅  │
└─────┘
```

---

## 3. Características Técnicas

### 3.1 Props e Estado

```typescript
interface ProfessionalSidebarProps {}

// Estados internos
const [isCollapsed, setIsCollapsed] = useState(false);
const [eventosOpen, setEventosOpen] = useState(false);
const [statisticsOpen, setStatisticsOpen] = useState(false);
```

### 3.2 Hooks Utilizados

```typescript
const pathname = usePathname();           // Next.js routing
const { theme } = useTheme();             // Tema claro/escuro
const { user } = useAuth();               // Dados do usuário autenticado
```

### 3.3 Animações

**Biblioteca**: `framer-motion`

**Transições**:
- Colapsar/Expandir: `0.2s` (width animation)
- Submenu open/close: `0.2s` (height + opacity)
- Hover states: `transition-all duration-200`

---

## 4. Navegação Principal

### 4.1 Menu Fixo (Sempre Visível)

```typescript
const navigation = [
  { name: 'Página Inicial', href: '/inicio', icon: Home },
  { name: 'Mensagens', href: '/messages', icon: MessageSquare },
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Cadastro', href: '/admin/cadastro', icon: UserPlus },
  { name: 'Equipes', href: '/teams', icon: UsersRound },
  { name: 'Atletas', href: '/admin/athletes', icon: Users },
  { name: 'Scout ao Vivo', href: '/scout/live', icon: Video },
];
```

**Características**:
- 7 itens de menu principais
- Ícones: `lucide-react`
- Sempre visíveis independente do papel do usuário
- Active state: `pathname === item.href`

---

## 5. RBAC - Submenu Estatísticas

### 5.1 Lógica de Permissões

```typescript
const getStatisticsSubmenu = (userRole: string | undefined) => {
  if (!userRole) return [];
  
  // ATLETA: Visão restrita (apenas dados próprios)
  if (userRole === 'atleta') {
    return [
      { 
        name: 'Minhas Estatísticas', 
        href: '/statistics/me', 
        icon: TrendingUp,
        tooltip: 'Seu acompanhamento pessoal'
      },
    ];
  }
  
  // COMISSÃO TÉCNICA: Visão completa
  if (['treinador', 'coordenador', 'admin', 'dirigente'].includes(userRole)) {
    return [
      { 
        name: 'Operacional', 
        href: '/statistics', 
        icon: BarChart3,
        tooltip: 'Controle do treino ou jogo do dia'
      },
      { 
        name: 'Equipes', 
        href: '/statistics/teams', 
        icon: UsersRound,
        tooltip: 'Análise de desempenho coletivo'
      },
      { 
        name: 'Atletas', 
        href: '/statistics/athletes', 
        icon: Users,
        tooltip: 'Análise individual para a comissão técnica'
      },
    ];
  }
  
  return [];
};
```

### 5.2 Matriz de Permissões

| Papel | `/statistics/me` | `/statistics` | `/statistics/teams` | `/statistics/athletes` |
|-------|------------------|---------------|---------------------|------------------------|
| **Atleta** | ✅ Visível | ❌ Oculto | ❌ Oculto | ❌ Oculto |
| **Treinador** | ❌ Oculto | ✅ Visível | ✅ Visível | ✅ Visível |
| **Coordenador** | ❌ Oculto | ✅ Visível | ✅ Visível | ✅ Visível |
| **Dirigente** | ❌ Oculto | ✅ Visível | ✅ Visível | ✅ Visível |
| **Admin** | ❌ Oculto | ✅ Visível | ✅ Visível | ✅ Visível |

### 5.3 Tooltips (UX Informativo)

- **Operacional**: "Controle do treino ou jogo do dia"
- **Equipes**: "Análise de desempenho coletivo"
- **Atletas**: "Análise individual para a comissão técnica"
- **Minhas Estatísticas**: "Seu acompanhamento pessoal"

---

## 6. Submenu Eventos

### 6.1 Estrutura Fixa

```typescript
const eventosSubmenu = [
  { name: 'Calendário', href: '/calendar', icon: CalendarDays },
  { name: 'Competições', href: '/eventos/competicoes', icon: Trophy },
  { name: 'Treinos', href: '/eventos/treinos', icon: Dumbbell },
];
```

**Características**:
- 3 itens sempre visíveis
- Sem RBAC (disponível para todos)
- Expansível com animação

---

## 7. Sistema de Temas

### 7.1 Lógica de Logos

```typescript
const getLogo = () => {
  if (isCollapsed) {
    return theme === 'dark' 
      ? '/images/logo/logo-icon-dark.svg'
      : '/images/logo/logo-icon.svg';
  }
  return theme === 'dark'
    ? '/images/logo/logo-dark.svg'
    : '/images/logo/logo.svg';
};
```

### 7.2 Assets de Logo

| Estado | Tema Claro | Tema Escuro |
|--------|-----------|-------------|
| **Expandido** | `logo.svg` (89x24px) | `logo-dark.svg` (89x24px) |
| **Colapsado** | `logo-icon.svg` (35x35px) | `logo-icon-dark.svg` (35x35px) |

---

## 8. Estados Visuais

### 8.1 Active State (Item Selecionado)

```typescript
className={cn(
  'flex items-center gap-2.5 px-3 py-2 rounded-lg text-xs font-medium',
  isActive
    ? 'bg-brand-50 dark:bg-brand-900/20 text-brand-700 dark:text-brand-400'
    : 'text-gray-700 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800'
)}
```

**Cores**:
- **Claro ativo**: `bg-brand-50` + `text-brand-700`
- **Escuro ativo**: `bg-brand-900/20` + `text-brand-400`
- **Hover**: `hover:bg-gray-100 dark:hover:bg-gray-800`

### 8.2 Submenu Active Detection

```typescript
// Estatísticas
const isStatisticsActive = statisticsSubmenu.some(
  item => pathname === item.href || pathname.startsWith(item.href + '/')
);

// Eventos
const isEventosActive = eventosSubmenu.some(
  item => pathname === item.href
);
```

**Lógica**:
- Menu pai fica ativo se qualquer filho estiver ativo
- Suporte a rotas aninhadas (`startsWith`)

---

## 9. Responsividade

### 9.1 Breakpoints

```typescript
animate={{ width: isCollapsed ? 64 : 220 }}
```

**Larguras**:
- **Expandido**: 220px
- **Colapsado**: 64px

### 9.2 Mobile

⚠️ **Nota**: A sidebar atual não tem comportamento mobile específico (hamburger menu, overlay, etc.). Em telas pequenas, mantém o comportamento colapsado.

**TODO**: Implementar overlay mobile com `z-50` e backdrop blur.

---

## 10. Classes CSS Customizadas

### 10.1 Scrollbar Customizada

```css
.custom-scrollbar {
  scrollbar-width: thin;
  scrollbar-color: rgba(156, 163, 175, 0.3) transparent;
}

.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}

.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: rgba(156, 163, 175, 0.3);
  border-radius: 3px;
}
```

### 10.2 Utilitários Tailwind

```typescript
import { cn } from '@/lib/utils';

// cn() = className merge com suporte a condicionais
// Internamente usa: clsx + tailwind-merge
```

---

## 11. Hierarquia de Componentes

```
ProfessionalSidebar
├── Header (Logo + Toggle Button)
│   ├── Link (Logo) → /inicio
│   └── Button (Collapse Toggle)
│
└── Navigation
    ├── Menu Principal (7 itens)
    │   └── Link → pathname match
    │
    ├── Submenu Estatísticas (RBAC)
    │   ├── Button (Expand/Collapse)
    │   └── AnimatePresence
    │       └── motion.div (Submenu Items)
    │           └── Link → pathname match
    │
    └── Submenu Eventos
        ├── Button (Expand/Collapse)
        └── AnimatePresence
            └── motion.div (Submenu Items)
                └── Link → pathname match
```

---

## 12. Integração com Contextos

### 12.1 AuthContext

```typescript
const { user } = useAuth();

// Uso: Determinar submenu de estatísticas baseado em user.role
const statisticsSubmenu = getStatisticsSubmenu(user?.role);
```

### 12.2 ThemeContext

```typescript
const { theme } = useTheme();

// Uso: Selecionar logo apropriado (claro/escuro)
const logoSrc = getLogo();
```

### 12.3 Next.js Router

```typescript
import { usePathname } from 'next/navigation';

const pathname = usePathname();

// Uso: Determinar active state de itens
const isActive = pathname === item.href;
```

---

## 13. Animações Framer Motion

### 13.1 Sidebar Width

```typescript
<motion.aside
  animate={{ width: isCollapsed ? 64 : 220 }}
  transition={{ duration: 0.2 }}
  className="..."
>
```

### 13.2 Submenu Expand/Collapse

```typescript
<AnimatePresence>
  {statisticsOpen && !isCollapsed && (
    <motion.div
      initial={{ height: 0, opacity: 0 }}
      animate={{ height: 'auto', opacity: 1 }}
      exit={{ height: 0, opacity: 0 }}
      transition={{ duration: 0.2 }}
    >
      {/* Submenu items */}
    </motion.div>
  )}
</AnimatePresence>
```

**Propriedades**:
- `initial`: Estado antes de montar
- `animate`: Estado final
- `exit`: Estado ao desmontar
- `transition.duration`: 0.2s

---

## 14. Acessibilidade (A11y)

### 14.1 Implementado

✅ Botões semânticos (`<button>`)  
✅ Links semânticos (`<Link>`)  
✅ Ícones com `flex-shrink-0` (não distorcem)  
✅ Tooltips em submenus (contexto adicional)  
✅ Estados visuais claros (active, hover)

### 14.2 Melhorias Futuras

⚠️ **TODO**:
- [ ] ARIA labels em botões de collapse
- [ ] `aria-expanded` em submenus
- [ ] `aria-current="page"` em item ativo
- [ ] Keyboard navigation (Tab, Enter, Escape)
- [ ] Focus visible com outline

---

## 15. Performance

### 15.1 Otimizações

✅ `useState` local (não causa re-render em parent)  
✅ `usePathname()` memoizado por Next.js  
✅ Imagens com `priority` (logo no fold)  
✅ `width: 'auto', height: 'auto'` (responsive images)  
✅ CSS transitions nativas (GPU accelerated)

### 15.2 Bundle Size

**Dependências**:
- `framer-motion`: ~40KB (tree-shakeable)
- `lucide-react`: ~2KB por ícone (tree-shakeable)
- Total estimado: **~50KB** (gzipped)

---

## 16. Fluxo de Usuário

### 16.1 Primeiro Acesso

1. Usuário faz login → `AuthContext` atualiza `user`
2. Sidebar renderiza com `user.role`
3. `getStatisticsSubmenu(user.role)` retorna itens permitidos
4. Menu renderizado conforme RBAC

### 16.2 Navegação

1. Usuário clica em item/submenu
2. `Link` atualiza `pathname` (Next.js router)
3. `usePathname()` detecta mudança
4. `isActive()` recalcula estados
5. Classes CSS atualizadas (active state)

### 16.3 Collapse/Expand

1. Usuário clica em botão toggle
2. `setIsCollapsed(!isCollapsed)`
3. `framer-motion` anima width (64px ↔ 220px)
4. Logo e texto aparecem/desaparecem
5. Transição completa em 0.2s

---

## 17. Casos de Uso

### 17.1 Atleta Navegando

**Cenário**: Atleta João acessa /statistics/me

```typescript
// user.role = 'atleta'
statisticsSubmenu = [
  { name: 'Minhas Estatísticas', href: '/statistics/me', ... }
]

// Sidebar exibe:
// - Menu principal (7 itens)
// - Estatísticas (1 item: Minhas Estatísticas)
// - Eventos (3 itens)
```

### 17.2 Treinador Navegando

**Cenário**: Treinador Maria acessa /statistics/teams

```typescript
// user.role = 'treinador'
statisticsSubmenu = [
  { name: 'Operacional', href: '/statistics', ... },
  { name: 'Equipes', href: '/statistics/teams', ... },
  { name: 'Atletas', href: '/statistics/athletes', ... }
]

// Sidebar exibe:
// - Menu principal (7 itens)
// - Estatísticas (3 itens: Operacional, Equipes, Atletas)
//   ↳ "Equipes" está ativo (pathname match)
// - Eventos (3 itens)
```

---

## 18. Manutenção e Extensão

### 18.1 Adicionar Item ao Menu Principal

```typescript
const navigation = [
  // ... itens existentes
  { name: 'Novo Item', href: '/novo-item', icon: NovoIcon },
];
```

### 18.2 Adicionar Item ao Submenu Eventos

```typescript
const eventosSubmenu = [
  // ... itens existentes
  { name: 'Jogos', href: '/eventos/jogos', icon: Trophy },
];
```

### 18.3 Modificar RBAC

```typescript
// Adicionar novo papel
if (['treinador', 'coordenador', 'admin', 'dirigente', 'novo_papel'].includes(userRole)) {
  return [...]; // Acesso completo
}

// Criar nível intermediário
if (userRole === 'treinador_junior') {
  return [
    { name: 'Operacional', href: '/statistics', ... },
    // Sem acesso a /statistics/teams
  ];
}
```

---

## 19. Testes

### 19.1 Testes Manuais

✅ **Colapsar/Expandir**: Botão funciona, animação suave  
✅ **Submenus**: Expandem/colapsam corretamente  
✅ **Active State**: Item correto destacado  
✅ **RBAC**: Atleta vê apenas "Minhas Estatísticas"  
✅ **Tema**: Logo troca corretamente claro/escuro  

### 19.2 Testes Automatizados (TODO)

```typescript
// Cypress E2E
describe('ProfessionalSidebar', () => {
  it('should collapse/expand on button click', () => {
    cy.get('[data-testid="sidebar-toggle"]').click();
    cy.get('[data-testid="sidebar"]').should('have.class', 'w-[64px]');
  });

  it('should show correct items for atleta role', () => {
    cy.login('atleta'); // Helper que faz login
    cy.visit('/inicio');
    cy.get('[data-testid="sidebar"]')
      .should('contain', 'Minhas Estatísticas')
      .should('not.contain', 'Equipes'); // Submenu Estatísticas
  });
});
```

---

## 20. Problemas Conhecidos

### 20.1 Mobile Layout

⚠️ **Issue**: Sidebar não fecha automaticamente em mobile após navegação.

**Solução proposta**:
```typescript
useEffect(() => {
  if (window.innerWidth < 768 && isMobileOpen) {
    setIsMobileOpen(false);
  }
}, [pathname]);
```

### 20.2 Scroll Position

⚠️ **Issue**: Ao expandir submenu, scroll não ajusta automaticamente.

**Solução proposta**:
```typescript
const submenuRef = useRef<HTMLDivElement>(null);

useEffect(() => {
  if (statisticsOpen && submenuRef.current) {
    submenuRef.current.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }
}, [statisticsOpen]);
```

---

## 21. Checklist de Qualidade

### Backend Integration
- [x] AuthContext integrado
- [x] User role disponível
- [x] RBAC funcional

### Frontend UX
- [x] Animações suaves
- [x] Active state preciso
- [x] Hover states claros
- [x] Tema claro/escuro suportado
- [x] Logo responsivo

### Código
- [x] TypeScript sem erros
- [x] ESLint sem warnings
- [x] Componentes modulares
- [x] Props tipadas
- [ ] Testes E2E (pendente)

### A11y
- [ ] ARIA labels (pendente)
- [ ] Keyboard navigation (pendente)
- [x] Focus states visíveis
- [x] Semântica HTML correta

---

## 22. Referências

**Arquivos relacionados**:
- `src/components/Layout/ProfessionalSidebar.tsx` (320 linhas)
- `src/context/AuthContext.tsx` (auth + user state)
- `src/context/ThemeContext.tsx` (tema claro/escuro)
- `src/app/(admin)/layout.tsx` (layout que usa sidebar)

**Bibliotecas**:
- `framer-motion`: https://www.framer.com/motion/
- `lucide-react`: https://lucide.dev/
- `tailwindcss`: https://tailwindcss.com/

**Design System**:
- Brand colors: `brand-50` a `brand-900`
- Gray scale: `gray-50` a `gray-950`
- Spacing: `gap-2.5`, `px-3`, `py-2`
- Typography: `text-xs` (12px), `font-medium` (500)

---

**Última atualização**: 2026-01-04  
**Autor**: Sistema HB Track  
**Status**: ✅ Documentação completa
