<!-- STATUS: NEEDS_REVIEW -->

# TopBar - Documentação do Sistema

## Visão Geral

A TopBar é o componente de navegação superior fixo do HB Track, responsável por exibir breadcrumbs contextuais, controles de busca, notificações e menu do usuário.

**Arquivo Principal:** `src/components/Layout/TopBar.tsx`

## Estrutura

```
┌────────────────────────────────────────────────────────────────────┐
│ [☰] [Breadcrumbs: Home > Treinos > Agenda]    [🔍] [🔔] [❓] [👤] │
└────────────────────────────────────────────────────────────────────┘
```

### Componentes

| Posição | Componente | Descrição |
|---------|------------|-----------|
| Esquerda | Menu hamburger | Abre sidebar mobile (apenas em telas pequenas) |
| Esquerda | Breadcrumbs | Navegação contextual baseada na rota atual |
| Direita | Busca (Ctrl+K) | Botão de busca global |
| Direita | SyncStatusIndicator | Status de sincronização de dados |
| Direita | NotificationDropdown | Centro de notificações |
| Direita | HelpDropdown | Menu de ajuda e suporte |
| Direita | Menu do usuário | Avatar, nome e opções do usuário |

## Breadcrumbs

**Arquivo:** `src/components/TopBar/Breadcrumbs.tsx`

### Funcionamento

1. Lê a rota atual via `usePathname()`
2. Divide em segmentos
3. Mapeia cada segmento para um label amigável via `ROUTE_LABELS`
4. Renderiza links navegáveis, exceto o último (página atual)

### Mapeamento de Rotas

```typescript
const ROUTE_LABELS: Record<string, string> = {
  'training': 'Treinos',
  'agenda': 'Agenda',
  'calendario': 'Calendário',
  'planejamento': 'Planejamento',
  'exercise-bank': 'Banco de Exercícios',
  'analytics': 'Analytics',
  'rankings': 'Rankings',
  'eficacia-preventiva': 'Eficácia Preventiva',
  'configuracoes': 'Configurações',
  // ... demais rotas
};
```

### Rotas Ocultas

Breadcrumbs não são exibidos em:
- `/signin`, `/signup`
- `/reset-password`, `/new-password`
- Rotas de nível único (ex: `/dashboard`)

### Tratamento de IDs

Para rotas com IDs dinâmicos (ex: `/teams/abc-123`), o breadcrumb usa um label genérico baseado no segmento anterior:
- `/teams/{id}` → "Equipe"
- `/athletes/{id}` → "Atleta"
- `/games/{id}` → "Jogo"

## Exemplo de Breadcrumbs por Módulo

| Rota | Breadcrumb |
|------|------------|
| `/training/agenda` | Home > Treinos > Agenda |
| `/training/analytics` | Home > Treinos > Analytics |
| `/training/rankings` | Home > Treinos > Rankings |
| `/training/eficacia-preventiva` | Home > Treinos > Eficácia Preventiva |
| `/training/configuracoes` | Home > Treinos > Configurações |
| `/games/escalacoes` | Home > Jogos > Escalações |

## Estilos

```tsx
// TopBar container
<div className="fixed top-0 right-0 left-0 md:left-[220px] z-40">

// Breadcrumb item ativo
<span className="text-xs font-medium text-gray-700 dark:text-gray-300">

// Breadcrumb link
<Link className="text-xs text-gray-500 dark:text-gray-400 hover:text-gray-700">
```

## Responsividade

- **Desktop (md+):** Breadcrumbs visíveis, sidebar fixa à esquerda
- **Mobile:** Menu hamburger visível, breadcrumbs ocultos ou simplificados

## Integração com Layout

A TopBar é renderizada dentro do layout admin/protected:

```tsx
<div className="flex-1 flex flex-col overflow-hidden">
  <TopBar onLogout={handleLogout} onMenuClick={toggleMobileSidebar} />
  <main className="flex-1 overflow-y-auto pt-14">
    {children}
  </main>
</div>
```

O `pt-14` no main compensa a altura fixa da TopBar.
