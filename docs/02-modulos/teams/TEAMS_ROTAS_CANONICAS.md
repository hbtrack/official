<!-- STATUS: NEEDS_REVIEW -->

# ✅ Teams: Migração para Rotas Canônicas

> **Data**: 2026-01-08  
> **Status**: COMPLETO E VERIFICADO

## Resumo

Migração completa de **query string** (`?teamId=X&tab=Y`) para **rotas canônicas** (`/teams/[teamId]/[tab]`).

---

## Checklist de Verificação

### 1. Rotas e Compatibilidade ✅

| Item | Status |
|------|--------|
| `/teams?teamId=X&tab=Y` → `/teams/X/Y` | ✅ Middleware redirect |
| `/teams?teamId=X` → `/teams/X/overview` | ✅ Default overview |
| `/teams?tab=Y` (sem teamId) → `/teams` | ✅ Sem loop |
| `/teams/X` → `/teams/X/overview` | ✅ Server redirect |
| `/teams/X/invalid` → 404 | ✅ Next.js automático |

### 2. Sidebar e Navegação ✅

| Item | Status |
|------|--------|
| Clicar em time → `/teams/{id}/overview` | ✅ `router.push()` |
| Sidebar ativa em todas subrotas | ✅ `pathname.startsWith('/teams/')` |
| Nenhum link gera `?teamId=` ou `?tab=` | ✅ Verificado |

### 3. Tabs Internas ✅

| Item | Status |
|------|--------|
| TeamNavigationTabs usa rotas | ✅ `<Link href={tab.href}>` |
| Highlight via `usePathname()` | ✅ Implementado |
| Sem refresh ao trocar aba | ✅ SPA navigation |

### 4. SearchParams Removido ✅

| Verificação | Status |
|-------------|--------|
| Nenhum `useSearchParams` em `[teamId]/**` | ✅ Nenhum |
| TeamNavigationTabs sem query | ✅ Verificado |
| Lógica "default tab" via redirect de rota | ✅ `page.tsx` |

### 5. SSR/Cookies ✅

| Item | Status |
|------|--------|
| Páginas server autenticadas | ✅ `serverApiClient` |
| Cookie passado no header | ✅ `hb_access_token` |
| Sem fetch dependendo de query | ✅ Verificado |

### 6. Estados da Lista ✅

| Item | Status |
|------|--------|
| `/teams` pode manter `?q=&page=` | ✅ Preparado |
| Filtros não vazam para detalhe | ✅ Verificado |

### 7. Loops e Re-renders ✅

| Item | Status |
|------|--------|
| Sem `router.replace` repetitivo | ✅ Nenhum nos componentes |
| Trocar time não trava | ✅ SPA navigation |

### 8. Erros ✅

| Cenário | Resposta |
|---------|----------|
| Team não encontrado | 404 via `notFound()` |
| Tab inválida | 404 via Next.js |
| Sem auth | Redirect `/signin` |

---

## Rotas Implementadas

| Rota | Descrição |
|------|-----------|
| `/teams` | Lista de equipes |
| `/teams/[teamId]` | Redirect → overview |
| `/teams/[teamId]/overview` | Visão geral |
| `/teams/[teamId]/members` | Membros |
| `/teams/[teamId]/trainings` | Treinos |
| `/teams/[teamId]/stats` | Estatísticas |
| `/teams/[teamId]/settings` | Configurações (RBAC) |

---

## Arquivos Chave

| Arquivo | Função |
|---------|--------|
| `src/middleware.ts` | Redirect de compatibilidade |
| `src/app/(admin)/teams/page.tsx` | Server Component (auth) |
| `src/app/(admin)/teams/page-original.tsx` | Client Component (dashboard) |
| `src/app/(admin)/teams/[teamId]/layout.tsx` | Shell com tabs |
| `src/app/(admin)/teams/[teamId]/page.tsx` | Redirect → overview |
| `src/components/teams/TeamNavigationTabs.tsx` | Navegação por tabs |

---

## Testes E2E

Criado: `tests/e2e/teams-navigation.spec.ts`

```bash
# Rodar testes
npx playwright test tests/e2e/teams-navigation.spec.ts
```

---

## Documentação Atualizada

> **Regra**: `teamId` e `tab` agora são segmentos de rota.  
> `searchParams` só é usado na lista (`?q=`, `?page=`).  
> O único parâmetro permitido no detalhe é `?isNew=true`.
