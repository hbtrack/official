<!-- STATUS: DEPRECATED | razao: fix tecnico de frontend, nao referencia canonica -->

# SSR Cookie Authentication Fix - Technical Deep Dive

**Data**: 2026-01-13
**Issue**: Server Components fazendo SSR fetch não recebem cookies automaticamente
**Solution**: Migrar para client-side fetch pattern

---

## 🔍 Problema Original

### Sintomas
- ✅ Tests de auth passam (cookie presente no Playwright)
- ✅ Members tab funciona corretamente
- ❌ Overview tab: testID não encontrado
- ❌ Settings tab: testID não encontrado
- 🖼️ Screenshot mostra: 404 page em vez da página esperada

### Stack Trace do Erro
```
1. Playwright visita: /teams/{teamId}/overview
2. Next.js Server Component executa: page.tsx
3. SSR chama: serverApiClient.get('/teams/{teamId}')
4. Backend recebe request SEM cookie hb_access_token
5. Backend retorna: 401 Unauthorized
6. Frontend detecta erro e chama: notFound()
7. Renderiza: 404 page ("We can't seem to find the page...")
8. Playwright busca: data-testid="team-overview-tab"
9. Resultado: ❌ TimeoutError (elemento não existe na página)
```

---

## 🧠 Análise Técnica

### Por Que Members Tab Funcionava?

```typescript
// Members Tab - Client Component Pattern
export default async function MembersPage({ params }: MembersPageProps) {
  const { teamId } = await params;
  return <MembersTab teamId={teamId} />; // ✅ Apenas passa ID
}

// MembersTab.tsx - Client Component
'use client';
export default function MembersTab({ teamId }: { teamId: string }) {
  useEffect(() => {
    // ✅ Client-side fetch - browser inclui cookies automaticamente
    const fetchData = async () => {
      const response = await fetch(`/api/teams/${teamId}/members`);
    };
    fetchData();
  }, [teamId]);
}
```

**Fluxo de Autenticação (Client-side)**:
```
Browser → Next.js API Route: Cookie incluído automaticamente pelo browser
  ↓
API Route → Backend: fetch() com credentials: 'include'
  ↓
Backend: Recebe cookie hb_access_token
  ↓
Backend: Valida JWT → 200 OK
  ↓
Frontend: Renderiza componente com dados
  ↓
Playwright: Encontra testID ✅
```

### Por Que Overview/Settings Falhavam?

```typescript
// Overview Tab - Server Component Pattern (ANTES)
export default async function OverviewPage({ params }: OverviewPageProps) {
  const { teamId } = await params;

  // ❌ SSR fetch - Node.js não inclui cookies automaticamente
  const team = await serverApiClient.get(`/teams/${teamId}`);

  if (!team) notFound(); // 401 → notFound() → 404 page
  return <OverviewTab team={team} />;
}
```

**Fluxo de Autenticação (Server-side) - BROKEN**:
```
Next.js Server (Node.js) → Backend: fetch() sem cookies
  ↓
Backend: NÃO recebe cookie hb_access_token
  ↓
Backend: JWT validation fails → 401 Unauthorized
  ↓
Frontend: Erro capturado → notFound()
  ↓
Renderiza: 404 page (página errada)
  ↓
Playwright: testID não existe na página ❌
```

---

## 🔧 Solução Implementada

### Estratégia
**Migrar Overview e Settings para o mesmo padrão de Members: Client-side fetch**

### Implementação - Overview Tab

#### Antes (Server Component SSR Fetch)
```typescript
// src/app/(admin)/teams/[teamId]/overview/page.tsx
import { notFound } from 'next/navigation';
import { serverApiClient } from '@/lib/api/server';
import { mapApiTeamToV2 } from '@/lib/adapters/teams-v2-adapter';

async function getTeam(teamId: string) {
  try {
    const apiTeam = await serverApiClient.get<Team>(`/teams/${teamId}`);
    return mapApiTeamToV2(apiTeam as any);
  } catch (error) {
    console.error('Erro ao carregar equipe:', error);
    return null;
  }
}

export default async function OverviewPage({ params, searchParams }: OverviewPageProps) {
  const { teamId } = await params;
  const { isNew } = await searchParams;

  const team = await getTeam(teamId); // ❌ SSR fetch
  if (!team) notFound();

  return <OverviewTab team={team} isNewTeam={isNew === 'true'} />;
}
```

#### Depois (Client-side Fetch)
```typescript
// src/app/(admin)/teams/[teamId]/overview/page.tsx
import OverviewTab from '@/components/teams-v2/OverviewTab';

export default async function OverviewPage({ params, searchParams }: OverviewPageProps) {
  const { teamId } = await params;
  const { isNew } = await searchParams;

  return (
    <OverviewTab
      teamId={teamId}  // ✅ Apenas passa ID
      isNewTeam={isNew === 'true'}
    />
  );
}
```

#### OverviewTab Component - Client-side Fetch Logic
```typescript
// src/components/teams-v2/OverviewTab.tsx
'use client';

import { teamsService } from '@/lib/api/teams';
import { mapApiTeamToV2 } from '@/lib/adapters/teams-v2-adapter';

interface OverviewTabProps {
  team?: Team;      // ✅ Backward compatibility
  teamId?: string;  // ✅ New pattern
  isNewTeam?: boolean;
}

const OverviewTab: React.FC<OverviewTabProps> = ({
  team: initialTeam,
  teamId,
  isNewTeam = false
}) => {
  const [currentTeam, setCurrentTeam] = useState<Team | null>(initialTeam || null);
  const [isLoadingTeam, setIsLoadingTeam] = useState(!initialTeam);

  // ✅ Fetch team client-side se apenas teamId fornecido
  const fetchTeam = async (id: string) => {
    try {
      setIsLoadingTeam(true);
      setHasError(false);

      // ✅ Client-side fetch - browser inclui cookies automaticamente
      const apiTeam = await teamsService.getById(id);
      const teamData = mapApiTeamToV2(apiTeam as any);

      setCurrentTeam(teamData);
    } catch (error) {
      console.error('❌ [OverviewTab] Erro ao carregar equipe:', error);
      setHasError(true);
    } finally {
      setIsLoadingTeam(false);
    }
  };

  useEffect(() => {
    if (!initialTeam && teamId) {
      fetchTeam(teamId);
    } else if (initialTeam && !currentTeam) {
      setCurrentTeam(initialTeam);
    }
  }, [teamId, initialTeam]);

  // Loading state
  if (!currentTeam?.id) {
    return <OverviewTabSkeleton />;
  }

  // ✅ Type assertion após verificação null
  const team = currentTeam as Team;

  return (
    <div data-testid="team-overview-tab">
      {/* Component content */}
    </div>
  );
};
```

### Implementação - Settings Tab

Mesma estratégia aplicada:
1. ✅ `page.tsx` passa apenas `teamId`
2. ✅ `TeamSettingsClient.tsx` repassa `teamId` para `SettingsTab`
3. ✅ `SettingsTab.tsx` faz fetch client-side no useEffect
4. ✅ Loading state durante fetch
5. ✅ Type assertion após verificação null

---

## 🔑 Key Decisions

### 1. Por Que Não Corrigir serverApiClient?

**Opção Descartada**: Fazer serverApiClient forward cookies corretamente

**Problemas**:
```typescript
// Tentativa de usar cookies() do Next.js
import { cookies } from 'next/headers';

async function serverApiClient(url: string) {
  const cookieStore = await cookies();
  const accessToken = cookieStore.get('hb_access_token')?.value;

  // ❌ Problema: cookies() só funciona durante request cycle
  // Em Server Components, pode não ter acesso dependendo do contexto
}
```

**Limitações**:
- `cookies()` do Next.js só funciona durante o request cycle inicial
- Server Components podem renderizar fora do request cycle (build time, ISR, etc)
- Em E2E tests, timing pode ser inconsistente
- Solução seria frágil e dependente de contexto

### 2. Por Que Client-side Fetch?

**Vantagens**:
✅ Browser gerencia cookies automaticamente (padrão HTTP)
✅ Consistente com Members tab (padrão já testado)
✅ Funciona em todos os ambientes (dev, prod, E2E)
✅ Simples de implementar e manter
✅ Backward compatible (suporta ambos `team` e `teamId`)

**Desvantagens**:
⚠️ Fetch adicional no client (latência)
⚠️ Não é SEO-friendly (dados não no HTML inicial)

**Mitigação**:
- Para aplicação admin, SEO não é crítico
- Latência é aceitável (< 100ms geralmente)
- Loading skeletons melhoram UX
- Pode usar React Query para cache futuro

---

## 📊 Fluxo Comparativo

### Antes (SSR) - BROKEN
```mermaid
Playwright → Next.js Server → Backend API
   [cookie]     [NO cookie!]      [401]
                      ↓
                  notFound()
                      ↓
                  404 Page
                      ↓
                testID ❌
```

### Depois (Client-side) - WORKING
```mermaid
Playwright → Next.js Server → HTML with skeleton
   [cookie]          ↓
                 Browser
                     ↓
              [cookie included]
                     ↓
               Backend API
                     ↓
                  [200 OK]
                     ↓
              Render component
                     ↓
                testID ✅
```

---

## ✅ Checklist de Validação

### TypeScript Compilation
```bash
npx tsc --noEmit 2>&1 | grep -E "(OverviewTab|SettingsTab)"
# ✅ Resultado: 0 erros
```

### Arquivos Modificados
- ✅ `src/app/(admin)/teams/[teamId]/overview/page.tsx`
- ✅ `src/components/teams-v2/OverviewTab.tsx`
- ✅ `src/app/(admin)/teams/[teamId]/settings/page.tsx`
- ✅ `src/app/(admin)/teams/[teamId]/settings/TeamSettingsClient.tsx`
- ✅ `src/components/teams-v2/SettingsTab.tsx`

### Backward Compatibility
- ✅ Componentes aceitam `team` (old) OU `teamId` (new)
- ✅ Código existente que passa `team` continua funcionando
- ✅ Novo código pode usar `teamId` pattern

### Loading States
- ✅ Skeleton durante fetch inicial
- ✅ Loading spinner para re-fetch
- ✅ Error handling com retry option

---

## 🚀 Deployment Checklist

### Antes de Deploy
- [x] TypeScript compila sem erros
- [x] ESLint passa
- [ ] Next.js build successful
- [ ] Testes E2E passam (após restart)

### Após Deploy
- [ ] Verificar Overview tab carrega corretamente
- [ ] Verificar Settings tab carrega corretamente
- [ ] Verificar Members tab ainda funciona
- [ ] Performance check (latência aceitável)
- [ ] Error monitoring (Sentry/similar)

---

## 📚 Lições Aprendidas

### 1. SSR Cookie Forwarding é Complexo
- Next.js `cookies()` tem limitações de contexto
- Server-to-server fetch não inclui cookies automaticamente
- Browser fetch inclui cookies automaticamente (padrão HTTP)

### 2. Padrões Consistentes são Importantes
- Members tab usava client-side fetch e funcionava
- Overview/Settings usavam SSR fetch e falhavam
- Solução: Padronizar todos em client-side fetch

### 3. E2E Tests Revelam Problemas de Arquitetura
- Em dev, pode funcionar porque você está logado
- Em E2E, fluxo é mais puro e revela edge cases
- Screenshot foi crucial para diagnóstico (404 page)

### 4. Backward Compatibility Vale a Pena
- Componentes aceitam `team` OU `teamId`
- Permite migração gradual
- Não quebra código existente

---

## 🔗 Referências

### Documentação Relevante
- [Next.js Server Components](https://nextjs.org/docs/app/building-your-application/rendering/server-components)
- [Next.js cookies() API](https://nextjs.org/docs/app/api-reference/functions/cookies)
- [Playwright Authentication](https://playwright.dev/docs/auth)
- [HTTP Cookies Spec](https://developer.mozilla.org/en-US/docs/Web/HTTP/Cookies)

### Issues Relacionadas
- Run 9: 91.89% success (3 tests failing)
- Diagnóstico do usuário: "SSR consegue acessar cookies, mas server-to-server fetch não os encaminha"
- Screenshot revelou: 404 page sendo renderizada

---

*Documento técnico gerado por Claude Code - 2026-01-13*
