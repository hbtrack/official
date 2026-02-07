<!-- STATUS: NEEDS_REVIEW -->

# Implementação e Melhorias - Página /teams

**Data:** 2026-01-04  
**Contexto:** Refatoração completa da interface de gerenciamento de equipes com foco em UX enterprise

---

## 1. Problema Inicial: AsyncSession vs Sync Sessions

### Contexto
O projeto utiliza Neon PostgreSQL no plano Free, que tem limitação de conexões simultâneas. Para otimizar, o sistema foi configurado para usar apenas **sessões síncronas** (`Session`) ao invés de assíncronas (`AsyncSession`).

### Erro Encontrado
```
TypeError: object of type 'coroutine' has no len()
NotImplementedError: AsyncSession desabilitado para economizar conexões no Neon Free
```

### Solução Implementada

#### Backend - Routers
**Arquivo:** `app/api/v1/routers/team_registrations.py`

Convertidos todos os 4 endpoints de async para sync:
- `list_team_registrations` (GET /teams/{team_id}/registrations)
- `create_team_registration` (POST /teams/{team_id}/registrations/{athlete_id})
- `update_team_registration` (PATCH /teams/{team_id}/registrations/{registration_id})
- `get_team_registration` (GET /teams/{team_id}/registrations/{registration_id})

**Mudanças:**
```python
# Antes
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_async_db

async def list_team_registrations(
    db: AsyncSession = Depends(get_async_db)
):
    regs = await service.list_by_team(...)

# Depois
from sqlalchemy.orm import Session
from app.core.db import get_db

def list_team_registrations(
    db: Session = Depends(get_db)
):
    regs = service.list_by_team(...)
```

#### Backend - Services
**Arquivo:** `app/services/team_registration_service.py`

Convertido completamente de async para sync (12 métodos):
- Todos os `async def` → `def`
- Todos os `await` removidos
- `AsyncSession` → `Session`

**Impacto:** Sistema agora compatível com limitações de Neon Free tier, sem perda de funcionalidade.

---

## 2. Exibição do Nome da Organização

### Requisito
- Coluna 1: Filtrar equipes apenas da organização do usuário logado
- Coluna 2: Mostrar "Clube: IDEC" ao invés de "Organização: UUID"

### Implementação

#### Backend - Schema
**Arquivo:** `app/schemas/teams.py`

```python
class TeamBase(BaseModel):
    id: UUID
    organization_id: UUID
    organization_name: Optional[str] = None  # ← NOVO
    name: str
    # ...
```

#### Backend - Service
**Arquivo:** `app/services/team_service.py`

Adicionado join com tabela `organizations` para incluir o nome:

```python
from app.models.organization import Organization

def list_teams(self, organization_id: UUID, ...) -> tuple[list[Team], int]:
    # ... query existente ...
    results = self.db.scalars(query).all()
    
    # Adicionar organization_name a cada team
    teams_list = []
    for team in results:
        org = self.db.get(Organization, team.organization_id)
        team.organization_name = org.name if org else None
        teams_list.append(team)
    
    return teams_list, total

def get_by_id(self, team_id: UUID) -> Optional[Team]:
    team = self.db.get(Team, team_id)
    if team:
        org = self.db.get(Organization, team.organization_id)
        team.organization_name = org.name if org else None
    return team
```

#### Frontend - Interface
**Arquivo:** `src/lib/api/teams.ts`

```typescript
export interface Team {
  id: string;
  name: string;
  organization_id: string;
  organization_name?: string;  // ← NOVO
  // ...
}
```

#### Frontend - Componente
**Arquivo:** `src/components/Teams/TeamsManagementAPI.tsx`

```tsx
{/* Antes */}
<label>Organização</label>
<p>{selectedTeam.organization_id}</p>

{/* Depois */}
<label>Clube</label>
<p>{selectedTeam.organization_name || selectedTeam.organization_id}</p>
```

**Resultado:**
- Lista já filtrava por organização via `ctx.organization_id` (sem mudanças necessárias)
- Detalhes agora exibem "Clube: IDEC" ao invés de UUID

---

## 3. Arquitetura de UX Enterprise

### Princípios Implementados

#### 3.1 Regra de Ouro para Modais vs Páginas Dedicadas

**Modal:** Apenas para ações simples e reversíveis
- Editar nome da equipe
- Ativar/desativar
- Trocar categoria ou gênero

**Página Dedicada (/admin/teams/[id]/edit):** Obrigatória para
- Vínculo ou remoção de atletas
- Vínculo ou remoção de treinadores
- Mudança de temporada
- Regras de elegibilidade
- Impacto em relatórios, calendário ou estatísticas

**Sidebar:** Visualização rápida e edição de dados básicos (implementação atual)

---

## 4. Ajustes Finos de UX (Alto Impacto)

### 4.1 Feedback Imediato - Skeleton Loading

**Antes:** Texto simples "Carregando..."

**Depois:** Skeleton animado realista

```tsx
{loadingStaff ? (
  <div className="space-y-3">
    {[1, 2].map((i) => (
      <div key={i} className="flex items-center gap-3 p-4 bg-gray-2 rounded-lg animate-pulse">
        <div className="w-12 h-12 bg-stroke rounded-full"></div>
        <div className="flex-1 space-y-2">
          <div className="h-4 bg-stroke rounded w-3/4"></div>
          <div className="h-3 bg-stroke rounded w-1/2"></div>
        </div>
      </div>
    ))}
  </div>
) : ...}
```

**Benefício:** Feedback visual claro durante carregamento, reduz ansiedade do usuário.

---

### 4.2 Estado de Leitura vs Edição

**Implementação:**
```tsx
<div className="flex items-center gap-3 mb-1">
  <h2>{selectedTeam.name}</h2>
  <span className="px-2 py-0.5 text-xs font-medium bg-success/10 text-success rounded">
    MODO LEITURA
  </span>
</div>
```

**Benefício:** Usuário sabe imediatamente que está visualizando, não editando. Evita cliques acidentais.

---

### 4.3 Ações Fixas e Previsíveis

**Header da Sidebar (topo direito):**
```tsx
<div className="flex items-center gap-2">
  <button onClick={() => handleCopyTeamLink(team.id)} title="Copiar link direto">
    <Copy />
  </button>
  <button onClick={handleCloseDetails} title="Fechar">
    <X />
  </button>
</div>
```

**Botões de Ação Principais:**
```tsx
<div className="flex gap-2">
  <button className="bg-primary">Editar Dados Básicos</button>
  <button disabled title="Em breve: ...">
    <ExternalLink /> Editar Equipe (Avançado)
  </button>
</div>
```

**Benefício:** Layout consistente, botões sempre no mesmo lugar, sem surpresas.

---

### 4.4 Indicadores de Impacto

**Confirmação de Exclusão:**
```javascript
const handleDeleteTeam = async (teamId: string) => {
  if (!confirm('⚠️ Tem certeza que deseja excluir esta equipe?\n\nImpacto: Todos os vínculos com atletas e treinadores serão perdidos.')) 
    return;
  // ...
}
```

**Microtexto no Footer:**
```tsx
<div className="flex-1 flex items-center text-xs text-bodydark px-2">
  💡 Para editar vínculos de atletas/treinadores, use o botão "Editar Equipe (Avançado)" no topo
</div>
```

**Benefício:** Usuário entende consequências antes de agir, reduz erros e medo.

---

### 4.5 Deep Link Interno

**Implementação:**

```typescript
// Hooks
const router = useRouter()
const searchParams = useSearchParams()
const [scrollPosition, setScrollPosition] = useState(0)

// Carregar equipe da URL
useEffect(() => {
  const teamId = searchParams.get('team')
  if (teamId && teams.length > 0) {
    const team = teams.find(t => t.id === teamId)
    if (team) handleSelectTeam(team)
  }
}, [searchParams, teams])

// Atualizar URL ao selecionar
const handleSelectTeam = async (team: Team) => {
  // Salvar scroll
  const listElement = document.querySelector('[data-teams-list]')
  if (listElement) setScrollPosition(listElement.scrollTop)
  
  // Atualizar URL
  const url = new URL(window.location.href)
  url.searchParams.set('team', team.id)
  window.history.pushState({}, '', url.toString())
  // ...
}

// Copiar link
const handleCopyTeamLink = async (teamId: string) => {
  const url = new URL(window.location.href)
  url.searchParams.set('team', teamId)
  await navigator.clipboard.writeText(url.toString())
  alert('Link copiado! Compartilhe para acesso direto a esta equipe.')
}
```

**URLs geradas:**
- `/admin/teams`
- `/admin/teams?team=d51d68a2-da1a-4923-90fa-10a3929c6728`

**Benefício:** 
- Suporte pode enviar link direto para equipe específica
- Debug facilitado
- Compartilhamento interno simplificado

---

### 4.6 Persistência de Contexto

**Implementação:**

```typescript
// Ao fechar sidebar
const handleCloseDetails = () => {
  setShowDetails(false)
  
  // Remover team da URL
  const url = new URL(window.location.href)
  url.searchParams.delete('team')
  window.history.pushState({}, '', url.toString())
  
  // Restaurar scroll
  setTimeout(() => {
    const listElement = document.querySelector('[data-teams-list]')
    if (listElement) {
      listElement.scrollTop = scrollPosition
    }
  }, 0)
}
```

**Lista com data attribute:**
```tsx
<div className="flex-1 overflow-y-auto" data-teams-list>
  {/* equipes */}
</div>
```

**Seleção visual persistida:**
```tsx
className={`... ${
  selectedTeam?.id === team.id 
    ? 'bg-primary/10 border-l-4 border-primary'  // ← borda azul esquerda
    : ''
}`}
```

**Benefício:** UX profissional, contexto mantido, menos frustração ao navegar.

---

### 4.7 Preparação para o Futuro

**Botão "Editar Avançado" desabilitado com tooltip educativo:**

```tsx
<button
  disabled
  title="Em breve: Página dedicada para gerenciar atletas, treinadores e histórico completo"
  className="opacity-60 cursor-not-allowed"
>
  <div className="flex items-center gap-2">
    <ExternalLink className="w-4 h-4" />
    Editar Equipe (Avançado)
  </div>
</button>
```

**Benefício:**
- Usuário sabe que funcionalidade está planejada
- Evita surpresa ao implementar
- Educa sobre arquitetura (modal vs página dedicada)

---

## 5. Resumo de Arquivos Modificados

### Backend

1. **`app/api/v1/routers/team_registrations.py`**
   - Convertidos 4 endpoints de async → sync
   - Mudança: `AsyncSession` → `Session`, removidos `await`

2. **`app/services/team_registration_service.py`**
   - Convertidos 12 métodos de async → sync
   - Service completamente síncrono

3. **`app/schemas/teams.py`**
   - Adicionado campo `organization_name: Optional[str]`

4. **`app/services/team_service.py`**
   - Adicionado import `Organization`
   - Métodos `list_teams` e `get_by_id` agora incluem `organization_name`

### Frontend

5. **`src/lib/api/teams.ts`**
   - Adicionado campo `organization_name?: string` à interface `Team`

6. **`src/components/Teams/TeamsManagementAPI.tsx`**
   - Adicionado deep link com router e searchParams
   - Implementado skeleton loading animado
   - Badge "MODO LEITURA"
   - Botões fixos no topo direito
   - Persistência de scroll
   - Função `handleCopyTeamLink`
   - Indicadores de impacto
   - Botão "Editar Avançado" preparado para futuro
   - Label "Clube:" ao invés de "Organização:"

---

## 6. Métricas de Impacto

| Aspecto | Antes | Depois |
|---------|-------|--------|
| **Carregamento de atletas** | Erro AsyncSession | ✅ Funcional (sync) |
| **Identificação da organização** | UUID incompreensível | Nome legível "IDEC" |
| **Feedback visual** | Texto "Carregando..." | Skeleton animado realista |
| **Contexto ao navegar** | Scroll perdido | Scroll preservado |
| **Compartilhamento** | URL genérica | Deep link com ?team=id |
| **Clareza de impacto** | Confirmação genérica | Texto explicativo de consequências |
| **Preparação futura** | Sem indicação | Botão educativo desabilitado |

---

## 7. Próximos Passos Sugeridos

### Curto Prazo
1. Implementar modal simples para "Editar Dados Básicos" (nome, categoria, gênero)
2. Adicionar toast notifications (sucesso/erro) ao invés de alerts
3. Implementar PermissionGateV2 para ocultar botões sem permissão

### Médio Prazo
4. Criar página dedicada `/admin/teams/[id]/edit` com abas:
   - Dados da equipe
   - Atletas vinculados (adicionar/remover)
   - Treinadores vinculados (adicionar/remover)
   - Histórico de mudanças
5. Substituir placeholders (Building2, User icons) por imagens do Cloudinary

### Longo Prazo
6. Sistema de busca/filtro na lista de equipes
7. Exportação de relatórios (PDF/Excel)
8. Integração com calendário de jogos

---

## 8. Boas Práticas Aplicadas

✅ **Separation of Concerns:** Lógica de negócio no service, apresentação no componente  
✅ **User Feedback:** Skeleton loading, tooltips, confirmações com impacto  
✅ **Progressive Enhancement:** Funcionalidades futuras sinalizadas sem quebrar UX atual  
✅ **Deep Linking:** URLs significativas, compartilháveis  
✅ **State Persistence:** Scroll e seleção mantidos  
✅ **Accessibility:** Títulos descritivos, labels claros  
✅ **Performance:** Sync sessions para economizar conexões DB  
✅ **Consistency:** Ações fixas, layout previsível  

---

## 9. Notas Técnicas

### Neon Free Tier Constraints
- **Limitação:** Máximo de conexões simultâneas reduzido
- **Solução adotada:** Desabilitar AsyncSession, usar apenas Session síncrona
- **Trade-off:** Menor throughput assíncrono, mas funcionalidade preservada
- **Ganho:** Economia de conexões, compatibilidade com plano gratuito

### Decisão Arquitetural: Modal vs Página
Seguindo princípio enterprise, ações que **alteram vínculos** ou **afetam histórico** devem sempre usar página dedicada, nunca modal. Isso garante:
- Espaço suficiente para formulários complexos
- Histórico de navegação correto
- URLs compartilháveis
- Separação clara de responsabilidades

---

**Documento criado em:** 2026-01-04  
**Versão:** 1.0  
**Responsável:** Implementação completa da página /teams com foco em UX enterprise
