<!-- STATUS: NEEDS_REVIEW -->

# Plan: Refatoração Completa do Sistema de Permissões (Breaking Change)

**TL;DR:** Unificar sistema de permissões para usar `Dict[str, bool]` em todos os endpoints, remover código duplicado (2 mapas ROLE_PERMISSIONS), corrigir inconsistência nomenclatura (singular→plural), adicionar type safety TypeScript. Breaking change aceito em DEV para arquitetura limpa.

---

## Steps

### 1. **Backend - Remover duplicação e unificar fonte de verdade**

**Arquivo:** [app/api/v1/routers/auth.py](c:\HB TRACK\Hb Track - Backend\app\api\v1\routers\auth.py)

**1.1 - Adicionar import** (inserir após linha 40, antes dos outros imports do módulo)
```python
from app.core.permissions_map import get_permissions_for_role
```

**1.2 - Deletar código duplicado** (remover linhas 48-124 completas)
- Remove `ROLE_PERMISSIONS` antigo (Dict com List[str])
- Remove função `get_permissions_for_role()` duplicada
- Total: 77 linhas deletadas

**1.3 - Atualizar LoginResponse schema** (linha 152)
```python
# ANTES:
permissions: List[str] = Field(default_factory=list, description="Lista de permissões do usuário")

# DEPOIS:
permissions: Dict[str, bool] = Field(default_factory=dict, description="Mapa de permissões do usuário")
```

**Resultado:** POST `/auth/login` e GET `/auth/me` agora retornam formato consistente

---

### 2. **Backend - Corrigir nomenclatura nas validações**

**Arquivo:** [app/api/v1/routers/teams.py](c:\HB TRACK\Hb Track - Backend\app\api\v1\routers\teams.py#L187)

**2.1 - Corrigir validação PATCH /teams/{id}** (linha 187)
```python
# ANTES:
ctx.requires("can_manage_team")  # ❌ Singular - não existe no permissions_map

# DEPOIS:
ctx.requires("can_manage_teams")  # ✅ Plural - consistente com permissions_map linha 116
```

**2.2 - Atualizar docstring** (linha 185)
```python
# ANTES:
"""Atualiza equipe. Regras: RF7, Step 2: Validação de permissão can_manage_team"""

# DEPOIS:
"""Atualiza equipe. Regras: RF7, Step 2: Validação de permissão can_manage_teams"""
```

**2.3 - Atualizar comentário** (linha 186)
```python
# ANTES:
# Step 2: Validar permissão can_manage_team

# DEPOIS:
# Step 2: Validar permissão can_manage_teams (plural - consistente com permissions_map)
```

**Validação:** Confirmar outras rotas estão corretas
- ✅ [team_members.py#L78](c:\HB TRACK\Hb Track - Backend\app\api\v1\routers\team_members.py#L78): `"can_manage_members"` (correto)
- ✅ [training_sessions.py#L206](c:\HB TRACK\Hb Track - Backend\app\api\v1\routers\training_sessions.py#L206): `"can_create_training"` (correto)

---

### 3. **Frontend - Atualizar tipos TypeScript**

**Arquivo:** [src/types/auth.ts](c:\HB TRACK\Hb Track - Fronted\src\types\auth.ts)

**3.1 - LoginResponse interface** (linha 28)
```typescript
// ANTES:
permissions: string[]

// DEPOIS:
permissions: Record<string, boolean>
```

**3.2 - User interface** (buscar linha ~52, após `photo_url`)
```typescript
// ANTES:
permissions: string[]

// DEPOIS:
permissions: Record<string, boolean>
```

**3.3 - Adicionar import no topo** (se necessário para documentação)
```typescript
// Opcional: importar novo tipo se criado
import type { PermissionsMap } from './permissions'
```

---

### 4. **Frontend - Ajustar lógica de autenticação**

**Arquivo:** [src/lib/auth/actions.ts](c:\HB TRACK\Hb Track - Fronted\src\lib\auth\actions.ts)

**4.1 - loginAction function** (linha 148)
```typescript
// ANTES:
permissions: response.permissions || [],

// DEPOIS:
permissions: response.permissions || {},
```

**4.2 - Verificar getSessionAction** (se usar permissions)
- Buscar usos de `session.user.permissions`
- Garantir tratamento como objeto, não array

---

### 5. **Frontend - Corrigir hook useTeamPermissions**

**Arquivo:** [src/lib/hooks/useTeamPermissions.tsx](c:\HB TRACK\Hb Track - Fronted\src\lib\hooks\useTeamPermissions.tsx)

**5.1 - PERMISSION_MAP** (linha 30)
```tsx
// ANTES:
const PERMISSION_MAP = {
  can_manage_team: 'canManageTeam',
  can_manage_members: 'canManageMembers',
  can_create_training: 'canCreateTraining',
} as const;

// DEPOIS:
const PERMISSION_MAP = {
  can_manage_teams: 'canManageTeam',     // ← Mudou para PLURAL
  can_manage_members: 'canManageMembers',
  can_create_training: 'canCreateTraining',
} as const;
```

**5.2 - Adicionar comentário de documentação** (após linha 28)
```tsx
// Step 8: Mapeamento explícito Backend → Frontend
// ⚠️ IMPORTANTE: Backend usa PLURAL para entidades (teams, members, trainings)
```

**5.3 - queryFn tipagem** (linha 172)
```tsx
// ANTES:
const data = await apiClient.get<{ permissions: Record<string, boolean> }>('/auth/me');

// DEPOIS (se criar type safety):
import type { PermissionsMap } from '@/types/permissions';
const data = await apiClient.get<{ permissions: PermissionsMap }>('/auth/me');
```

**5.4 - Resolver permissões** (linha 223)
```tsx
// ANTES:
canManageTeam = backendPermissions.can_manage_team ?? false;

// DEPOIS:
canManageTeam = backendPermissions.can_manage_teams ?? false;  // ← PLURAL
```

---

### 6. **Frontend - Criar type safety para permissões**

**Arquivo:** [src/types/permissions.ts](c:\HB TRACK\Hb Track - Fronted\src\types\permissions.ts) **(CRIAR NOVO)**

```typescript
/**
 * Tipos TypeScript para permissões do backend
 * 
 * ⚠️ FONTE CANÔNICA: app/core/permissions_map.py
 * Manter sincronizado manualmente ou gerar via script
 * 
 * NOMENCLATURA PADRÃO:
 * - Entidades: PLURAL (can_manage_teams, can_manage_members)
 * - Ações específicas: SINGULAR (can_create_team, can_edit_team)
 */

export type BackendPermission =
  // === Controles integrados (sidebar) ===
  | 'can_manage_teams'          // Gestão completa de equipes
  | 'can_manage_athletes'       // Gestão de atletas
  | 'can_manage_trainings'      // Gestão de treinos
  | 'can_manage_matches'        // Gestão de jogos
  | 'can_manage_wellness'       // Gestão de wellness
  
  // === Acesso e navegação ===
  | 'public_access'
  | 'can_view_dashboard'
  | 'can_access_intake'
  | 'can_view_statistics'
  | 'can_use_live_scout'
  | 'can_view_calendar'
  | 'can_view_competitions'
  | 'can_view_training_schedule'
  | 'can_view_athlete_360'
  | 'can_view_team_360'
  | 'can_generate_reports'
  
  // === Gestão organizacional ===
  | 'can_manage_org'
  | 'can_manage_users'
  | 'can_manage_members'        // Adicionar/remover membros de equipes
  | 'can_manage_seasons'
  
  // === Ações específicas - Teams ===
  | 'can_create_team'
  | 'can_edit_team'
  | 'can_delete_team'
  | 'can_view_teams'
  
  // === Ações específicas - Training ===
  | 'can_create_training'
  | 'can_edit_training'
  | 'can_delete_training'
  | 'can_view_training'
  
  // === Ações específicas - Athletes ===
  | 'can_create_athlete'
  | 'can_edit_athlete'
  | 'can_delete_athlete'
  | 'can_view_athletes'
  
  // === Ações específicas - Matches ===
  | 'can_create_match'
  | 'can_edit_match'
  | 'can_delete_match'
  | 'can_view_matches'
  
  // === Reports e Wellness ===
  | 'can_view_reports'
  | 'can_export_reports'
  | 'can_view_wellness'
  | 'can_edit_wellness';

/**
 * Mapa completo de permissões (todas as chaves são BackendPermission)
 */
export type PermissionsMap = Record<BackendPermission, boolean>;

/**
 * Resposta do backend contendo permissões
 */
export interface PermissionsResponse {
  permissions: PermissionsMap;
}

/**
 * Type guard para validar se uma string é uma permissão válida
 */
export function isValidPermission(key: string): key is BackendPermission {
  const validPermissions: BackendPermission[] = [
    'can_manage_teams',
    'can_manage_members',
    'can_create_training',
    // ... adicionar todas conforme necessário
  ];
  return validPermissions.includes(key as BackendPermission);
}
```

---

### 7. **Documentação - Atualizar PERMISSIONS.md**

**Arquivo:** [PERMISSIONS.md](c:\HB TRACK\PERMISSIONS.md)

**7.1 - Adicionar ao final do arquivo** (após linha 644):

```markdown

---

## 🔧 REFATORAÇÃO CIRÚRGICA DO SISTEMA DE PERMISSÕES - 15/Jan/2026

### 🎯 Problema Identificado

**Causa Raiz:** Inconsistência de nomenclatura + duplicação de código

| Localização | Estrutura | Nomenclatura | Status |
|-------------|-----------|--------------|--------|
| `permissions_map.py` (canônico) | `Dict[str, bool]` | `can_manage_teams` (PLURAL) | ✅ Correto |
| `auth.py` (duplicado) | `List[str]` | `"can_manage_team"` | ❌ Remover |
| `teams.py` validação | - | `"can_manage_team"` (SINGULAR) | ❌ Corrigir |
| Frontend hook | `Record<string, boolean>` | `can_manage_team` (SINGULAR) | ❌ Corrigir |

**Impacto:**
- ❌ Coordenadores NÃO viam aba "Configurações"
- ❌ `canManageTeam` sempre retornava `false`
- ❌ Backend tinha 2 fontes de verdade diferentes

---

### Solução Implementada (Breaking Change em DEV)

#### Backend - Mudanças

**1. Removido código duplicado** - [auth.py#L48-L124](c:\HB TRACK\Hb Track - Backend\app\api\v1\routers\auth.py)
- ❌ DELETADO: `ROLE_PERMISSIONS` antigo (retornava `List[str]`)
- ❌ DELETADO: Função `get_permissions_for_role()` duplicada
- ✅ IMPORTADO: `from app.core.permissions_map import get_permissions_for_role`

**2. Unificado formato de resposta** - [auth.py#L152](c:\HB TRACK\Hb Track - Backend\app\api\v1\routers\auth.py#L152)
```python
# LoginResponse agora retorna Dict[str, bool] (consistente com /auth/me)
permissions: Dict[str, bool] = Field(default_factory=dict, ...)
```

**3. Corrigido nomenclatura** - [teams.py#L187](c:\HB TRACK\Hb Track - Backend\app\api\v1\routers\teams.py#L187)
```python
ctx.requires("can_manage_teams")  # Mudou de singular → plural
```

#### Frontend - Mudanças

**4. Atualizado tipos TypeScript** - [types/auth.ts](c:\HB TRACK\Hb Track - Fronted\src\types\auth.ts)
```typescript
// LoginResponse.permissions: string[] → Record<string, boolean>
// User.permissions: string[] → Record<string, boolean>
```

**5. Ajustado lógica de login** - [actions.ts#L148](c:\HB TRACK\Hb Track - Fronted\src\lib\auth\actions.ts#L148)
```typescript
permissions: response.permissions || {},  // Mudou de [] → {}
```

**6. Corrigido hook** - [useTeamPermissions.tsx](c:\HB TRACK\Hb Track - Fronted\src\lib\hooks\useTeamPermissions.tsx)
- L30: `can_manage_team` → `can_manage_teams` (PERMISSION_MAP)
- L223: `backendPermissions.can_manage_team` → `backendPermissions.can_manage_teams`

**7. Adicionado type safety** - [types/permissions.ts](c:\HB TRACK\Hb Track - Fronted\src\types\permissions.ts) *(novo arquivo)*
- Type `BackendPermission` com todas as permissões válidas
- Type guard `isValidPermission()`
- Interface `PermissionsMap`

---

### 📐 Nomenclatura Padrão (Documentação Canônica)

⚠️ **REGRA FUNDAMENTAL:**

**Entidades = PLURAL** (gerencia múltiplos itens)
-  `can_manage_teams` - Gestão de equipes
-  `can_manage_members` - Gestão de membros
-  `can_manage_trainings` - Gestão de treinos
-  `can_manage_athletes` - Gestão de atletas

**Ações específicas = SINGULAR** (atua em um item por vez)
-  `can_create_team` - Cria UMA equipe
-  `can_edit_team` - Edita UMA equipe
-  `can_delete_team` - Deleta UMA equipe

**Visualização = contexto define**
-  `can_view_teams` - Ver lista de equipes (plural)
-  `can_view_dashboard` - Ver dashboard (singular)

---

### 🔴 Breaking Changes (Aceitos em DEV)

**Backend API:**
- ❌ POST `/auth/login` response: `permissions` mudou de `List[str]` → `Dict[str, bool]`
- ⚠️ Sessões antigas incompatíveis

**Frontend:**
- ❌ `LoginResponse.permissions` type mudou
- ❌ `User.permissions` type mudou
- ⚠️ Código que iterava sobre `user.permissions` como array quebrou

**Ação Requerida Pós-Deploy:**
```bash
# Todos os desenvolvedores devem:
1. Fazer logout
2. Limpar cookies do navegador (F12 → Application → Clear storage)
3. Fazer login novamente
4. Hard refresh (Ctrl+Shift+R)
```

---

### 📊 Arquivos Modificados

**Backend (3 arquivos):**
- [app/api/v1/routers/auth.py](c:\HB TRACK\Hb Track - Backend\app\api\v1\routers\auth.py) - Removido duplicação (77 linhas) + mudou schema
- [app/api/v1/routers/teams.py](c:\HB TRACK\Hb Track - Backend\app\api\v1\routers\teams.py#L187) - Corrigido nomenclatura

**Frontend (4 arquivos + 1 novo):**
- [src/types/auth.ts](c:\HB TRACK\Hb Track - Fronted\src\types\auth.ts) - Atualizado 2 interfaces
- [src/lib/auth/actions.ts](c:\HB TRACK\Hb Track - Fronted\src\lib\auth\actions.ts#L148) - Ajustado fallback
- [src/lib/hooks/useTeamPermissions.tsx](c:\HB TRACK\Hb Track - Fronted\src\lib\hooks\useTeamPermissions.tsx) - Corrigido 2 lugares
- [src/types/permissions.ts](c:\HB TRACK\Hb Track - Fronted\src\types\permissions.ts) - **NOVO** (type safety)

**Linhas totais:** ~85 deletadas, ~120 adicionadas/modificadas

---

### Validação

**Manual:**
- [ ] Login como coordenador → Acessar equipe → Verificar aba "Configurações" visível
- [ ] GET `/api/v1/auth/me` retorna `{"can_manage_teams": true, ...}`
- [ ] Hook `useTeamPermissions` retorna `canManageTeam: true`

**Automatizado:**
```bash
# E2E tests
npx playwright test tests/e2e/teams/teams.permissions.spec.ts

# Backend unit tests
pytest app/tests/test_permissions_map.py -v
```

**Checklist Pós-Deploy:**
- [ ] Backend compilando sem erros
- [ ] Frontend compilando sem erros TypeScript
- [ ] Todos os devs fizeram logout/login
- [ ] Cache do navegador limpo
- [ ] Testes E2E passando (mínimo 10/13)

---

### 🎓 Lições Aprendidas

1. **Nunca duplicar código** - Tinha 2 `ROLE_PERMISSIONS` causando divergências
2. **Nomenclatura consistente** - Singular vs plural causou bug silencioso
3. **Type safety salva** - TypeScript teria detectado o problema mais cedo
4. **Breaking changes em DEV são OK** - Melhor arquitetura vale o custo
5. **Documentar decisões** - Este registro previne regressão futura

---

### 🔮 Próximos Passos

**Curto prazo:**
- [ ] Adicionar CI check: comparar permissions_map.py com `types/permissions.ts`
- [ ] Script de geração automática de `BackendPermission` type
- [ ] Testes unitários para `PERMISSION_MAP` (frontend)

**Longo prazo:**
- [ ] Migrar para permissões por equipe (não apenas globais)
- [ ] Adicionar cache de permissões no Redis
- [ ] GraphQL schema para permissões (alternativa REST)


➕ Step 8 ADICIONAL - Backend: Compatibilidade MockUser
Necessário para: Não quebrar testes legados que usam MockUser

Arquivo: [app/core/auth.py](c:\HB TRACK\Hb Track - Backend\app\core\auth.py)

8.1 - Atualizar init signature (linha 44)


def __init__(    self,    user_id: str = "09cd9e07-3a95-4d1e-8f19-d3d81e1dd8b4",    person_id: str = "8a99ff63-66e9-4d1b-b288-60332667467f",    membership_id: str = "11111111-1111-1111-1111-111111111111",    organization_id: str = "85b5a651-6677-4a6a-a08f-60e657a624a2",    role: str = "coordenador",    permissions: dict[str, bool] | list[str] | None = None,  # Aceita ambos):    self.user_id = user_id    self.person_id = person_id    self.membership_id = membership_id    self.organization_id = organization_id    self.role = role        # Normalizar permissions para dict (compatibilidade com código legado)    if permissions is None:        self.permissions = {"*": True}    elif isinstance(permissions, list):        # Converter lista legada → dict (ex: ["read", "write"] → {"read": True, "write": True})        self.permissions = {perm: True for perm in permissions}    else:        self.permissions = permissions


8.2 - Atualizar has_permission (linha ~53)


def has_permission(self, permission: str) -> bool:    # Suportar dict (novo formato)    if isinstance(self.permissions, dict):        return self.permissions.get(permission, False) or self.permissions.get("*", False)        # Fallback para lista (deprecated - nunca deveria chegar aqui após __init__)    if "*" in self.permissions:        return True    return permission in self.permissions

8.3 - Atualizar to_dict (linha ~63)


def to_dict(self) -> dict:    return {        "user_id": self.user_id,        "person_id": self.person_id,        "membership_id": self.membership_id,        "organization_id": self.organization_id,        "role": self.role,        "permissions": self.permissions,  # ✅ Já retorna dict após normalização    }
✅ CHECKLIST FINAL DE VALIDAÇÃO

Backend
- [ ] auth.py: Remover duplicação 
- [ ] auth.py: LoginResponse schema 
- [ ] teams.py: Nomenclatura plural 
- [ ] auth.py: MockUser compatibilidade
- [ ] ExecutionContext: Correto 
- [ ] permissions_map.py: Canônico intacto 

Frontend
- [ ] types/auth.ts: 2 interfaces ✅
- [ ] actions.ts: Fallback ajustado ✅
- [ ] useTeamPermissions.tsx: 2 correções ✅
- [ ] types/permissions.ts: Criar novo ✅
- [ ] PermissionGateV2: Já correto ✅

Testes
- [ ] E2E: Já validam dict 
- [ ] Unit: MockUser precisa suportar ambos 


## Considerações Finais: 

1. **Invalidação de cache** - Adicionar versão ao queryKey: `['user-permissions-v2']` para forçar refetch após deploy.

2. **Migração de dados** - Se houver sessões persistidas em banco/Redis com formato antigo `permissions: []`, criar migration script para converter → `permissions: {}`

3. **Script de validação** - Criar ferramenta que compara `permissions_map.py` com `types/permissions.ts` e alerta se estiverem dessincronizados (executar no CI/CD)

4. **Testes de regressão** - Adicionar teste E2E específico: "Coordenador vê aba Configurações" para prevenir regressão deste bug

5. **Monitoramento** - Adicionar log/métrica quando `ctx.requires()` falha por permissão inexistente (detectar typos futuros)