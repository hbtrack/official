<!-- STATUS: NEEDS_REVIEW -->

# Sistema de Permissões - HB Track

## Visão Geral

O sistema de autenticação agora retorna as **permissões** do usuário no momento do login, permitindo que o frontend controle o acesso a recursos de forma granular.

## Endpoints

### 1. POST /api/v1/auth/login

**Resposta inclui permissões:**

```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 86400,
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "full_name": "João Silva",
  "email": "joao@exemplo.com",
  "role_code": "treinador",
  "is_superadmin": false,
  "organization_id": "660e8400-e29b-41d4-a716-446655440001",
  "permissions": [
    "read_athlete",
    "read_training",
    "edit_training",
    "read_match",
    "read_wellness",
    "edit_wellness",
    "read_medical",
    "view_reports",
    "view_dashboard"
  ]
}
```

### 2. GET /api/v1/auth/permissions

Retorna apenas as permissões do usuário autenticado:

```json
[
  "read_athlete",
  "read_training",
  "edit_training",
  "read_match",
  "read_wellness",
  "edit_wellness",
  "read_medical",
  "view_reports",
  "view_dashboard"
]
```

**Requer:** Token JWT no header `Authorization: Bearer {token}`

## Permissões por Papel

### Superadmin
- Acesso total a todos os recursos
- Todas as permissões disponíveis

### Dirigente
- `read_athlete`, `edit_athlete`
- `read_training`, `edit_training`
- `read_match`, `edit_match`
- `read_wellness`, `read_medical`
- `admin_memberships`, `admin_organization`
- `admin_teams`, `admin_seasons`
- `view_reports`, `view_dashboard`

### Coordenador
- `read_athlete`, `edit_athlete`
- `read_training`, `edit_training`
- `read_match`, `edit_match`
- `read_wellness`, `read_medical`
- `admin_teams`
- `view_reports`, `view_dashboard`

### Treinador
- `read_athlete`
- `read_training`, `edit_training`
- `read_match`
- `read_wellness`, `edit_wellness`
- `read_medical`
- `view_reports`, `view_dashboard`

### Atleta
- `read_athlete` (apenas próprios dados)
- `read_training` (apenas próprios treinos)
- `read_wellness`, `edit_wellness` (apenas próprios dados)
- `view_dashboard` (dashboard pessoal)

## Uso no Frontend

### 1. Acessar permissões da sessão

```typescript
import { useSession } from '@/hooks/useSession'

function MyComponent() {
  const { session } = useSession()
  const permissions = session?.user?.permissions || []
  
  console.log(permissions)
}
```

### 2. Usar o hook usePermissions

```typescript
import { usePermissions } from '@/hooks/usePermissions'

function EditAthleteButton() {
  const { hasPermission } = usePermissions()
  
  if (!hasPermission('edit_athlete')) {
    return null
  }
  
  return <button>Editar Atleta</button>
}
```

### 3. Verificar múltiplas permissões

```typescript
import { usePermissions } from '@/hooks/usePermissions'

function AdminPanel() {
  const { hasAnyPermission, hasAllPermissions } = usePermissions()
  
  // Verifica se tem PELO MENOS UMA das permissões
  const canManage = hasAnyPermission('admin_teams', 'admin_organization')
  
  // Verifica se tem TODAS as permissões
  const fullAccess = hasAllPermissions('admin_teams', 'admin_organization', 'admin_seasons')
  
  return (
    <div>
      {canManage && <ManagementPanel />}
      {fullAccess && <AdvancedSettings />}
    </div>
  )
}
```

### 4. Componente RequirePermission

```typescript
import { RequirePermission } from '@/hooks/usePermissions'

function MyPage() {
  return (
    <div>
      <h1>Dashboard</h1>
      
      {/* Exibe apenas se tiver a permissão */}
      <RequirePermission permission="edit_training">
        <CreateTrainingButton />
      </RequirePermission>
      
      {/* Exibe fallback se não tiver permissão */}
      <RequirePermission 
        permission="admin_organization"
        fallback={<AccessDeniedMessage />}
      >
        <OrganizationSettings />
      </RequirePermission>
      
      {/* Exige múltiplas permissões (pelo menos uma) */}
      <RequirePermission permission={['edit_athlete', 'admin_teams']}>
        <TeamManagement />
      </RequirePermission>
      
      {/* Exige TODAS as permissões */}
      <RequirePermission 
        permission={['admin_teams', 'admin_seasons']}
        requireAll={true}
      >
        <AdvancedConfig />
      </RequirePermission>
    </div>
  )
}
```

## Validação no Backend

**Importante:** As permissões no frontend são apenas para UX. A validação de segurança real deve sempre ser feita no backend.

### Exemplo de validação no backend (implementação futura):

```python
from app.core.auth import require_permission

@router.post("/athletes")
@require_permission("edit_athlete")
async def create_athlete(
    payload: AthleteCreate,
    ctx: ExecutionContext = Depends(get_current_context)
):
    # Apenas usuários com permissão 'edit_athlete' chegam aqui
    ...
```

## Lista Completa de Permissões

| Permissão | Descrição |
|-----------|-----------|
| `read_athlete` | Visualizar atletas |
| `edit_athlete` | Criar/editar atletas |
| `delete_athlete` | Remover atletas |
| `read_training` | Visualizar treinos |
| `edit_training` | Criar/editar treinos |
| `delete_training` | Remover treinos |
| `read_match` | Visualizar jogos |
| `edit_match` | Criar/editar jogos |
| `delete_match` | Remover jogos |
| `read_wellness` | Visualizar dados de wellness |
| `edit_wellness` | Editar dados de wellness |
| `read_medical` | Visualizar dados médicos |
| `edit_medical` | Editar dados médicos |
| `admin_memberships` | Administrar vínculos de usuários |
| `admin_organization` | Administrar organização |
| `admin_teams` | Administrar equipes |
| `admin_seasons` | Administrar temporadas |
| `view_reports` | Visualizar relatórios |
| `view_dashboard` | Visualizar dashboard |

## Exemplos de Casos de Uso

### 1. Botão Condicional

```typescript
function AthleteCard({ athlete }) {
  const { hasPermission } = usePermissions()
  
  return (
    <div className="card">
      <h3>{athlete.name}</h3>
      <p>{athlete.position}</p>
      
      {hasPermission('edit_athlete') && (
        <button onClick={() => editAthlete(athlete.id)}>
          Editar
        </button>
      )}
    </div>
  )
}
```

### 2. Menu Dinâmico

```typescript
function Sidebar() {
  const { hasPermission } = usePermissions()
  
  const menuItems = [
    { label: 'Dashboard', path: '/dashboard', permission: 'view_dashboard' },
    { label: 'Atletas', path: '/athletes', permission: 'read_athlete' },
    { label: 'Treinos', path: '/trainings', permission: 'read_training' },
    { label: 'Jogos', path: '/matches', permission: 'read_match' },
    { label: 'Relatórios', path: '/reports', permission: 'view_reports' },
    { label: 'Configurações', path: '/settings', permission: 'admin_organization' },
  ]
  
  return (
    <nav>
      {menuItems.map(item => (
        hasPermission(item.permission) && (
          <Link key={item.path} href={item.path}>
            {item.label}
          </Link>
        )
      ))}
    </nav>
  )
}
```

### 3. Proteção de Rota

```typescript
// app/(protected)/settings/page.tsx
import { RequirePermission } from '@/hooks/usePermissions'
import { redirect } from 'next/navigation'

export default function SettingsPage() {
  return (
    <RequirePermission 
      permission="admin_organization"
      fallback={redirect('/dashboard')}
    >
      <SettingsContent />
    </RequirePermission>
  )
}
```

## Notas Importantes

1. **As permissões são retornadas no login** - Não é necessário fazer uma chamada adicional
2. **Use `GET /auth/permissions`** apenas se precisar atualizar as permissões sem fazer novo login
3. **Sempre valide no backend** - As permissões do frontend são para UX, não para segurança
4. **Superadmin tem todas as permissões** - Sempre retorna o conjunto completo
5. **Permissões são baseadas no papel** - Mudou o papel? Faça novo login para atualizar
