<!-- STATUS: NEEDS_REVIEW -->

# SISTEMA DE PERMISSÕES - HB TRACK

## 📋 Índice
1. [Visão Geral](#visão-geral)
2. [Arquitetura](#arquitetura)
3. [Breaking Changes](#breaking-changes)
4. [Guia de Uso](#guia-de-uso)
5. [Roles e Permissões](#roles-e-permissões)
6. [Troubleshooting](#troubleshooting)

---

## 🎯 Visão Geral

O sistema de permissões do HB TRACK controla o acesso de usuários a funcionalidades específicas baseado em seus **roles** (papéis) e **permissões granulares**.

### Características
- ✅ **Single Source of Truth**: Único mapa canônico de permissões
- ✅ **Type Safety**: Validação de tipos em compilação (Backend e Frontend)
- ✅ **Formato Unificado**: `Dict[str, bool]` (Backend) / `Record<string, boolean>` (Frontend)
- ✅ **Nomenclatura Consistente**: Sempre plural para recursos (`can_manage_teams` não `can_manage_team`)
- ✅ **Backward Compatible**: MockUser aceita ambos formatos antigo e novo

---

## 🏗️ Arquitetura

### Backend (Python/FastAPI)

#### Fonte Canônica de Permissões
**Arquivo:** `app/core/permissions_map.py`

```python
from typing import Dict

def get_permissions_for_role(role_code: str) -> Dict[str, bool]:
    """
    Retorna o mapa de permissões para um role específico.
    
    Returns:
        Dict[str, bool]: Mapa de permissões onde key é o nome da permissão 
                         e value é True/False indicando se está habilitada
    """
    ROLE_PERMISSIONS: Dict[str, Dict[str, bool]] = {
        "superadmin": {
            "can_view_athletes": True,
            "can_create_athletes": True,
            "can_manage_teams": True,  # ✅ SEMPRE PLURAL
            # ... outras permissões
        },
        "coordenador": {
            "can_view_athletes": True,
            "can_manage_teams": True,  # ✅ Coordenador pode gerenciar equipes
            "can_manage_members": True,
            # ... outras permissões
        },
        # ... outros roles
    }
    return ROLE_PERMISSIONS.get(role_code, {})
```

#### Endpoints de Autenticação

##### POST `/api/v1/auth/login`
**Response Format:**
```json
{
  "access_token": "eyJ...",
  "user_id": "uuid",
  "role_code": "coordenador",
  "permissions": {
    "can_view_athletes": true,
    "can_manage_teams": true,
    "can_manage_members": true
  }
}
```

##### GET `/api/v1/auth/me`
**Response Format:**
```json
{
  "user_id": "uuid",
  "email": "user@example.com",
  "role_code": "coordenador",
  "permissions": {
    "can_view_athletes": true,
    "can_manage_teams": true,
    "can_manage_members": true
  }
}
```

#### ExecutionContext (Validação de Permissões)

**Arquivo:** `app/core/context.py`

```python
class ExecutionContext:
    def __init__(
        self,
        user_id: str,
        role: str,
        permissions: Dict[str, bool],  # ✅ Sempre dict
        # ... outros campos
    ):
        self.permissions = permissions
    
    def requires(self, permission: str) -> None:
        """Valida se usuário tem a permissão. Lança PermissionDenied se não tiver."""
        if not self.permissions.get(permission, False):
            raise PermissionDenied(f"Permissão '{permission}' necessária")
    
    def has_any(self, permissions: List[str]) -> bool:
        """Retorna True se usuário tem QUALQUER uma das permissões."""
        return any(self.permissions.get(p, False) for p in permissions)
    
    def has_all(self, permissions: List[str]) -> bool:
        """Retorna True se usuário tem TODAS as permissões."""
        return all(self.permissions.get(p, False) for p in permissions)
```

**Exemplo de Uso:**
```python
@router.put("/teams/{team_id}")
async def update_team(
    team_id: str,
    ctx: ExecutionContext = Depends(permission_dep(roles=["coordenador"]))
):
    # Validar permissão específica
    ctx.requires("can_manage_teams")  # ✅ SEMPRE PLURAL
    
    # ... lógica do endpoint
```

---

### Frontend (TypeScript/React)

#### Type Definitions

**Arquivo:** `src/types/permissions.ts` ✨ **NOVO**

```typescript
/**
 * Backend permission names (snake_case)
 * CRITICAL: Must match exactly with app/core/permissions_map.py
 */
export type BackendPermission =
  // Teams  
  | 'can_view_teams'
  | 'can_create_teams'
  | 'can_manage_teams'  // ✅ ALWAYS PLURAL
  | 'can_delete_teams'
  
  // Team Members
  | 'can_view_members'
  | 'can_manage_members'
  
  // Training
  | 'can_view_training'
  | 'can_create_training'
  | 'can_edit_training'
  | 'can_delete_training'
  
  // ... outras permissões
  ;

/**
 * Permission map type returned by backend
 * Format: { "can_view_teams": true, "can_manage_teams": false, ... }
 */
export type PermissionsMap = Record<BackendPermission, boolean>;

/**
 * Partial permissions (user may not have all permissions)
 */
export type UserPermissions = Partial<PermissionsMap>;
```

**Arquivo:** `src/types/auth.ts`

```typescript
export interface LoginResponse {
  access_token: string
  user_id: string
  role_code: string
  permissions: Record<string, boolean>  // ✅ Object format
  // ... outros campos
}

export interface User {
  id: string
  email: string
  role: UserRole
  permissions: Record<string, boolean>  // ✅ Object format
  // ... outros campos
}
```

#### Hook de Permissões

**Arquivo:** `src/lib/hooks/useTeamPermissions.tsx`

```typescript
// Mapeamento Backend → Frontend
const PERMISSION_MAP = {
  can_manage_teams: 'canManageTeam',        // ✅ Backend usa PLURAL
  can_manage_members: 'canManageMembers',
  can_create_training: 'canCreateTraining',
} as const;

export function useTeamPermissions(teamId?: string): TeamPermissions {
  const { user } = useAuth();
  
  // Buscar permissões do backend
  const { data: backendPermissions } = useQuery({
    queryKey: ['team-permissions', teamId],
    queryFn: () => apiClient.get(`/teams/${teamId}/permissions`),
  });
  
  // Resolver permissões
  const canManageTeam = backendPermissions?.can_manage_teams ?? false;  // ✅ PLURAL
  const canManageMembers = backendPermissions?.can_manage_members ?? false;
  
  return {
    canManageTeam,
    canManageMembers,
    // ... outras permissões
  };
}
```

#### Componente de Permissões

**Arquivo:** `src/components/PermissionGateV2.tsx`

```typescript
export function PermissionGateV2({ 
  permission, 
  children 
}: { 
  permission: keyof User['permissions'], 
  children: ReactNode 
}) {
  const { user } = useAuth();
  
  // ✅ Acesso direto ao objeto
  if (!user?.permissions?.[permission]) {
    return null;
  }
  
  return <>{children}</>;
}
```

**Exemplo de Uso:**
```tsx
<PermissionGateV2 permission="can_manage_teams">
  <Button>Editar Equipe</Button>
</PermissionGateV2>
```

---

## ⚠️ Breaking Changes

### 🔴 MUDANÇAS INCOMPATÍVEIS - Requer Ação Imediata

#### 1. Formato de Response da API `/auth/login`

**Antes (❌ DEPRECATED):**
```json
{
  "permissions": ["can_manage_team", "can_manage_members"]
}
```

**Depois (✅ ATUAL):**
```json
{
  "permissions": {
    "can_manage_teams": true,
    "can_manage_members": true,
    "can_view_athletes": true
  }
}
```

**Impacto:**
- ⚠️ Clientes que consomem a API precisam atualizar código
- ⚠️ Frontend deve usar `Object.keys()` ao invés de array iteration
- ⚠️ Sessões antigas (antes do deploy) são **INCOMPATÍVEIS**

**Ação Requerida:**
1. Atualizar código do cliente para esperar objeto
2. Invalidar todas as sessões no momento do deploy
3. Forçar logout/login de todos usuários

---

#### 2. Nomenclatura de Permissões: Singular → Plural

**Antes (❌ DEPRECATED):**
```python
# Backend
ctx.requires("can_manage_team")  # ❌ SINGULAR
```

```typescript
// Frontend
backendPermissions.can_manage_team  // ❌ SINGULAR
```

**Depois (✅ ATUAL):**
```python
# Backend
ctx.requires("can_manage_teams")  # ✅ PLURAL
```

```typescript
// Frontend
backendPermissions.can_manage_teams  // ✅ PLURAL
```

**Impacto:**
- ⚠️ Código que usa `can_manage_team` (singular) **QUEBRA**
- ⚠️ Permissão singular não existe no mapa canônico → sempre retorna `false`

**Ação Requerida:**
1. Buscar e substituir todas ocorrências de `can_manage_team` (singular)
2. Validar com IDE/TypeScript que nenhum uso do singular permanece

**Comando de Busca:**
```bash
# Backend
grep -r "can_manage_team" --include="*.py" app/

# Frontend
grep -r "can_manage_team" --include="*.ts" --include="*.tsx" src/
```

---

#### 3. TypeScript Types Atualizados

**Antes (❌ DEPRECATED):**
```typescript
interface LoginResponse {
  permissions: string[]  // ❌ Array
}

interface User {
  permissions: string[]  // ❌ Array
}
```

**Depois (✅ ATUAL):**
```typescript
interface LoginResponse {
  permissions: Record<string, boolean>  // ✅ Object
}

interface User {
  permissions: Record<string, boolean>  // ✅ Object
}
```

**Impacto:**
- ⚠️ Código TypeScript que usa `permissions.includes()` **NÃO COMPILA**
- ⚠️ Loops com `permissions.forEach()` **NÃO COMPILAM**

**Ação Requerida:**
1. Substituir `permissions.includes(perm)` por `permissions[perm]`
2. Substituir loops de array por `Object.keys(permissions)` ou `Object.entries(permissions)`

**Exemplos de Migração:**
```typescript
// ❌ ANTES
if (user.permissions.includes('can_manage_teams')) { }

// ✅ DEPOIS
if (user.permissions['can_manage_teams']) { }

// ❌ ANTES
user.permissions.forEach(perm => console.log(perm))

// ✅ DEPOIS
Object.entries(user.permissions).forEach(([perm, hasIt]) => {
  if (hasIt) console.log(perm)
})
```

---

### 🟢 Backward Compatibility Mantida

#### MockUser (Testes)
O `MockUser` **ACEITA AMBOS** formatos para não quebrar testes existentes:

```python
# ✅ Formato antigo (ainda funciona)
mock_user = MockUser(permissions=["can_manage_teams", "can_view_athletes"])

# ✅ Formato novo
mock_user = MockUser(permissions={
    "can_manage_teams": True,
    "can_view_athletes": True
})

# Conversão automática
# Lista → Dict internamente
```

**Nenhuma ação necessária** nos testes existentes.

---

## 📚 Guia de Uso

### Backend: Como Validar Permissões

#### Opção 1: Validar uma permissão específica
```python
@router.post("/teams/{team_id}/members")
async def add_member(
    team_id: str,
    ctx: ExecutionContext = Depends(permission_dep(roles=["coordenador"]))
):
    # Lança PermissionDenied se usuário não tiver a permissão
    ctx.requires("can_manage_members")
    
    # ... lógica
```

#### Opção 2: Validar múltiplas permissões (OR)
```python
# Usuário precisa ter QUALQUER uma das permissões
if ctx.has_any(["can_manage_teams", "can_manage_members"]):
    # ... lógica
```

#### Opção 3: Validar múltiplas permissões (AND)
```python
# Usuário precisa ter TODAS as permissões
if ctx.has_all(["can_view_athletes", "can_manage_teams"]):
    # ... lógica
```

#### Opção 4: Validação condicional
```python
# Não lança exceção, apenas retorna bool
if ctx.permissions.get("can_manage_teams", False):
    # ... lógica para quem tem permissão
else:
    # ... lógica alternativa
```

---

### Frontend: Como Verificar Permissões

#### Opção 1: Hook useTeamPermissions
```tsx
function TeamSettingsTab({ teamId }: { teamId: string }) {
  const { canManageTeam } = useTeamPermissions(teamId);
  
  if (!canManageTeam) {
    return <p>Você não tem permissão para gerenciar esta equipe.</p>;
  }
  
  return <SettingsForm />;
}
```

#### Opção 2: PermissionGateV2 Component
```tsx
<PermissionGateV2 permission="can_manage_teams">
  <Button onClick={handleEdit}>Editar Equipe</Button>
</PermissionGateV2>
```

#### Opção 3: useAuth Hook (Global)
```tsx
function Navbar() {
  const { user } = useAuth();
  
  return (
    <nav>
      {user?.permissions.can_view_athletes && (
        <Link href="/athletes">Atletas</Link>
      )}
      
      {user?.permissions.can_manage_teams && (
        <Link href="/teams/settings">Configurações</Link>
      )}
    </nav>
  );
}
```

---

## 👥 Roles e Permissões

### Mapa Completo de Permissões por Role

#### Superadmin
```json
{
  "can_view_athletes": true,
  "can_create_athletes": true,
  "can_edit_athletes": true,
  "can_delete_athletes": true,
  "can_view_teams": true,
  "can_create_teams": true,
  "can_manage_teams": true,
  "can_delete_teams": true,
  "can_manage_members": true,
  "can_view_training": true,
  "can_create_training": true,
  "can_edit_training": true,
  "can_delete_training": true,
  "can_view_matches": true,
  "can_create_matches": true,
  "can_edit_matches": true,
  "can_delete_matches": true,
  "can_view_wellness": true,
  "can_edit_wellness": true,
  "can_view_medical": true,
  "can_edit_medical": true,
  "can_manage_organization": true,
  "can_manage_seasons": true,
  "can_view_reports": true,
  "can_view_dashboard": true,
  "can_manage_system": true
}
```

#### Dirigente
```json
{
  "can_view_athletes": true,
  "can_create_athletes": true,
  "can_edit_athletes": true,
  "can_view_teams": true,
  "can_create_teams": true,
  "can_manage_teams": true,
  "can_manage_members": true,
  "can_view_training": true,
  "can_create_training": true,
  "can_edit_training": true,
  "can_view_matches": true,
  "can_create_matches": true,
  "can_edit_matches": true,
  "can_view_wellness": true,
  "can_view_medical": true,
  "can_manage_organization": true,
  "can_manage_seasons": true,
  "can_view_reports": true,
  "can_view_dashboard": true
}
```

#### Coordenador
```json
{
  "can_view_athletes": true,
  "can_edit_athletes": true,
  "can_view_teams": true,
  "can_manage_teams": true,        // ✅ POR ISSO A ABA APARECE
  "can_manage_members": true,
  "can_view_training": true,
  "can_create_training": true,
  "can_edit_training": true,
  "can_view_matches": true,
  "can_create_matches": true,
  "can_edit_matches": true,
  "can_view_wellness": true,
  "can_view_medical": true,
  "can_view_reports": true,
  "can_view_dashboard": true
}
```

#### Treinador
```json
{
  "can_view_athletes": true,
  "can_view_teams": true,
  "can_view_training": true,
  "can_create_training": true,
  "can_edit_training": true,
  "can_view_matches": true,
  "can_view_wellness": true,
  "can_edit_wellness": true,
  "can_view_medical": true,
  "can_view_reports": true,
  "can_view_dashboard": true
}
```

#### Atleta
```json
{
  "can_view_athletes": true,       // Apenas próprios dados
  "can_view_training": true,       // Apenas próprios treinos
  "can_view_wellness": true,       // Apenas próprios dados
  "can_edit_wellness": true,       // Pode editar próprio wellness
  "can_view_dashboard": true       // Dashboard pessoal
}
```

---

## 🔧 Troubleshooting

### Problema: Aba "Configurações" não aparece para coordenador

**Sintomas:**
- Coordenador faz login
- Acessa página de equipe
- Aba "Configurações" não é exibida

**Causa Raiz:**
1. Backend retorna `can_manage_team` (singular) ❌
2. Frontend busca `can_manage_team` (singular) ❌
3. Permissão não encontrada → `undefined` → `false`

**Solução:**
✅ **CORRIGIDO** na refatoração:
- Backend agora usa `can_manage_teams` (plural)
- Frontend busca `can_manage_teams` (plural)
- Permissão existe no mapa → `true` → Aba aparece

**Validação:**
```bash
# Backend
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/auth/me

# Deve retornar:
{
  "permissions": {
    "can_manage_teams": true  # ✅ PLURAL
  }
}

# Frontend (DevTools Console)
console.log(user.permissions.can_manage_teams)  // ✅ true
```

---

### Problema: Erro 403 Forbidden ao acessar endpoint

**Sintomas:**
- Request retorna `{"detail": "Permissão 'can_xxx' necessária"}`

**Causa Raiz:**
1. Usuário não tem a permissão no role
2. Nome da permissão incorreto (typo ou singular vs plural)
3. Token expirado/inválido

**Solução:**
1. **Validar role do usuário:**
   ```python
   # No endpoint
   print(f"Role: {ctx.role}")
   print(f"Permissions: {ctx.permissions}")
   ```

2. **Verificar nome da permissão:**
   ```python
   # Sempre use plural para recursos
   ctx.requires("can_manage_teams")  # ✅ Correto
   ctx.requires("can_manage_team")   # ❌ Errado (não existe)
   ```

3. **Validar token:**
   ```bash
   curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/auth/me
   ```

---

### Problema: TypeScript error - Property 'includes' does not exist

**Sintomas:**
```typescript
// Erro de compilação
Property 'includes' does not exist on type 'Record<string, boolean>'
```

**Causa Raiz:**
- Código usa API de array (`includes`, `forEach`) em objeto

**Solução:**
```typescript
// ❌ ERRADO
if (permissions.includes('can_manage_teams')) { }

// ✅ CORRETO
if (permissions['can_manage_teams']) { }
if (permissions.can_manage_teams) { }
```

---

### Problema: MockUser em testes não funciona

**Sintomas:**
- Testes falham com `AttributeError` ou `TypeError`

**Causa Raiz:**
- MockUser agora espera `dict` mas teste passa `list`

**Solução:**
✅ **NÃO PRECISA MUDAR** - MockUser aceita ambos formatos:

```python
# ✅ Ambos funcionam
mock_user = MockUser(permissions=["can_manage_teams"])  # Lista
mock_user = MockUser(permissions={"can_manage_teams": True})  # Dict
```

Se ainda assim falhar:
```python
# Atualizar para novo formato
mock_user = MockUser(permissions={
    "can_manage_teams": True,
    "can_view_athletes": True
})
```

---

## 📝 Checklist de Validação

### Backend
- [ ] GET `/api/v1/auth/me` retorna `permissions: Dict[str, bool]`
- [ ] POST `/api/v1/auth/login` retorna `permissions: Dict[str, bool]`
- [ ] Coordenador tem `can_manage_teams: true` (plural)
- [ ] Validações com `ctx.requires("can_manage_teams")` funcionam
- [ ] Testes unitários passam (MockUser backward compatible)

### Frontend
- [ ] Login retorna objeto `Record<string, boolean>`
- [ ] TypeScript compila sem erros
- [ ] `useTeamPermissions` retorna `canManageTeam: true` para coordenador
- [ ] Aba "Configurações" aparece para coordenador
- [ ] `PermissionGateV2` funciona corretamente
- [ ] E2E tests passam

### Geral
- [ ] Todas as sessões antigas invalidadas
- [ ] Desenvolvedores fizeram logout/login
- [ ] Monitoramento Sentry sem erros relacionados a permissões
- [ ] Taxa de erro 403 não aumentou
- [ ] Documentação atualizada

---

## 📚 Referências

- **Código Canônico:** `app/core/permissions_map.py`
- **ExecutionContext:** `app/core/context.py`
- **Types Frontend:** `src/types/permissions.ts`
- **Hook Permissões:** `src/lib/hooks/useTeamPermissions.tsx`
- **Log de Mudanças:** [LOG_PERMISSIONS.md](./LOG_PERMISSIONS.md)
- **Plano Original:** [_PLANO_GESTAO_STAFF.md](./_PLANO_GESTAO_STAFF.md)

---

**Última Atualização:** 2024 (Refatoração Completa)  
**Status:** ✅ PRODUÇÃO  
**Breaking Changes:** Sim (v2.0.0)
