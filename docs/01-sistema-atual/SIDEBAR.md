<!-- STATUS: NEEDS_REVIEW -->

# Sidebar - Documentação do Sistema

## Visão Geral

A ProfessionalSidebar é o componente de navegação lateral do HB Track, organizado em seções temáticas com suporte a submenus colapsáveis, RBAC (controle de acesso por papel) e persistência de estado.

**Arquivo Principal:** `src/components/Layout/ProfessionalSidebar.tsx`
**Versão:** 4.3

## Estrutura de Seções

```
┌─────────────────────────┐
│ [Logo HB Track]    [<]  │
├─────────────────────────┤
│ [Contexto Equipe/Temp]  │
├─────────────────────────┤
│ INÍCIO                  │
│   Página Inicial        │
│   Dashboard             │
├─────────────────────────┤
│ ORGANIZAÇÃO             │
│   Equipes          [3]  │
│   Calendário Geral      │
├─────────────────────────┤
│ PLANEJAMENTO TÉCNICO    │
│ ▶ Treinos               │
│ ▶ Jogos                 │
│   Competições           │
├─────────────────────────┤
│ DESEMPENHO              │
│ ▶ Atletas               │
│ ▶ Estatísticas          │
├─────────────────────────┤
│ ─────── (divisor) ───── │
│ ▼ ADMINISTRAÇÃO         │
│   Cadastro e Permissões │
│   Comissão Técnica      │
│   Histórico / Auditoria │
│   Configurações         │
├─────────────────────────┤
│ [🌙] Modo Escuro        │
└─────────────────────────┘
```

## Componentes de Sidebar

### SidebarItem
Item de navegação simples com ícone, label e badge opcional.

```tsx
<SidebarItem
  name="Equipes"
  href="/teams"
  icon={UsersRound}
  isActive={pathname.startsWith('/teams')}
  isCollapsed={isCollapsed}
  badge={teams?.length}
/>
```

**Props:**
- `name`: Label do item
- `href`: URL de destino
- `icon`: Ícone Lucide
- `isActive`: Se está na rota atual
- `isCollapsed`: Se sidebar está colapsada
- `badge`: Número ou texto para badge
- `badgeVariant`: `default` | `warning` | `error` | `success`

### SidebarSubmenu
Menu colapsável com lista de subitens. Usado para Treinos, Jogos, Atletas e Estatísticas.

```tsx
<SidebarSubmenu
  name="Treinos"
  icon={Clipboard}
  items={treinosSubmenu}
  isCollapsed={isCollapsed}
  badge={routeVisibility.training.count > 0 ? undefined : '!'}
  tooltip="Sem treinos cadastrados"
/>
```

**Comportamento:**
- Abre automaticamente se um subitem está ativo
- Animação suave com Framer Motion
- Chevron rotaciona ao expandir/colapsar
- Border-left visual conectando subitens

### SidebarSection
Título de seção (apenas visual).

```tsx
<SidebarSection title="Planejamento Técnico" isCollapsed={isCollapsed} />
```

### SidebarCollapsibleSection
Seção inteira colapsável (usado em Administração).

```tsx
<SidebarCollapsibleSection
  title="Administração"
  icon={Settings}
  isCollapsed={isCollapsed}
  defaultExpanded={true}
  storageKey="hbtrack-admin-section-expanded"
>
  {/* Items */}
</SidebarCollapsibleSection>
```

### SidebarDivider
Linha divisória com espaçamento configurável.

```tsx
<SidebarDivider spacing="lg" />
```

## Submenu de Treinos (v4.3)

O módulo Treinos agora usa o padrão `SidebarSubmenu` igual aos outros módulos:

```typescript
const treinosSubmenu = [
  { name: 'Agenda Semanal', href: '/training/agenda', icon: CalendarDays },
  { name: 'Calendário', href: '/training/calendario', icon: Calendar },
  { name: 'Planejamento', href: '/training/planejamento', icon: ClipboardList },
  { name: 'Banco de Exercícios', href: '/training/exercise-bank', icon: ListChecks },
  { name: 'Analytics', href: '/training/analytics', icon: Activity },
  { name: 'Rankings', href: '/training/rankings', icon: Trophy },
  { name: 'Eficácia Preventiva', href: '/training/eficacia-preventiva', icon: Icons.Medical },
  { name: 'Configurações', href: '/training/configuracoes', icon: Settings },
];
```

## RBAC (Controle de Acesso)

### Estatísticas por Papel

```typescript
const getStatisticsSubmenu = (userRole: string | undefined) => {
  if (userRole === 'atleta') {
    return [{ name: 'Minhas Estatísticas', href: '/statistics/me' }];
  }

  if (['treinador', 'coordenador', 'admin', 'dirigente'].includes(userRole)) {
    return [
      { name: 'Por Equipes', href: '/statistics/teams' },
      { name: 'Por Atletas', href: '/statistics/athletes' },
      { name: 'Comparativos', href: '/statistics/comparativos' },
    ];
  }

  return [];
};
```

### Seção de Administração

Visível apenas para `admin` e `coordenador`:

```typescript
const canAccessAdmin = (role: string | undefined) => {
  return role && ['admin', 'coordenador'].includes(role);
};
```

## Persistência de Estado

| Chave localStorage | Descrição |
|-------------------|-----------|
| `hbtrack-sidebar-collapsed` | Se sidebar está colapsada |
| `hbtrack-admin-section-expanded` | Se seção admin está expandida |
| `hbtrack-selected-team` | ID da equipe selecionada |

## Estilos e Efeitos Hover

```tsx
// Item inativo
'text-gray-700 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800'

// Item ativo
'bg-emerald-50 dark:bg-emerald-900/20 text-emerald-700 dark:text-emerald-300'

// Transição
'transition-colors duration-200'
```

## Sidebar Colapsada

Quando `isCollapsed=true`:
- Apenas ícones são exibidos
- Tooltips aparecem ao hover
- Submenus abrem como popover

## Responsividade

- **Desktop (md+):** Sidebar fixa, largura 220px (ou 64px colapsada)
- **Mobile:** Sidebar em drawer (MobileDrawer), abre via menu hamburger

## Arquivos Relacionados

```
src/components/Sidebar/
├── index.ts              # Exports
├── SidebarItem.tsx       # Item simples
├── SidebarSubmenu.tsx    # Submenu colapsável
├── SidebarSection.tsx    # Título de seção
├── SidebarCollapsibleSection.tsx
├── SidebarDivider.tsx    # Divisor
├── SidebarTeamContext.tsx # Contexto de equipe
├── SidebarJourneyShortcuts.tsx # Atalhos inteligentes
├── SidebarBadge.tsx      # Badge numérico
└── SidebarTooltip.tsx    # Tooltip para modo colapsado
```
