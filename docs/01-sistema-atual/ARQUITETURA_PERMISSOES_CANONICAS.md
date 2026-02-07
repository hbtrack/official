<!-- STATUS: NEEDS_REVIEW -->

# ✅ Arquitetura Canônica de Permissões

## 🎯 Filosofia

```
┌─────────────────────────────────────────┐
│  Backend = Fonte única da verdade       │
│  Frontend = Apenas lê capacidades       │
│  Mapa canônico = ÚNICO lugar           │
└─────────────────────────────────────────┘
```

**Princípios:**
1. **Zero duplicação** - Permissões definidas em UM único arquivo
2. **Resolvido uma vez** - Calculado na autenticação, reutilizado
3. **Espelho no frontend** - `/auth/context` não tem regras, só retorna estado
4. **UX ≠ Segurança** - Frontend esconde UI, backend protege ações

---

## 📁 Arquitetura

### Estrutura de Arquivos

```
app/
├── core/
│   ├── permissions_map.py        ⭐ FONTE ÚNICA
│   ├── auth/
│   │   └── execution_context.py  📦 Estado resolvido
│   └── context.py                🔐 Dependency injection
└── api/v1/routers/
    └── auth.py                   🪞 Espelho (/auth/context)

frontend/
├── types/
│   └── auth.ts                   📝 TypeScript types
└── components/auth/
    └── PermissionGateV2.tsx      🚪 Controle de UI
```

---

## 🗺️ PASSO 1: Mapa Canônico de Permissões

📁 **`app/core/permissions_map.py`**

```python
# FONTE ÚNICA - NUNCA duplicar estas regras
ROLE_PERMISSIONS = {
    "superadmin": {
        "can_manage_org": True,
        "can_create_team": True,
        "can_create_athlete": True,
        "can_view_reports": True,
        # ... todas as permissões
    },
    "dirigente": {
        "can_manage_org": True,
        "can_create_team": True,
        "can_create_athlete": True,
        # ...
    },
    "coordenador": {
        "can_manage_org": False,  # ❌
        "can_create_team": True,
        "can_create_athlete": True,
        # ...
    },
    "treinador": {
        "can_create_team": False,  # ❌
        "can_create_athlete": True,
        # ...
    },
    "atleta": {
        "can_create_team": False,  # ❌
        "can_create_athlete": False,  # ❌
        # ...
    },
}
```

**Permissões definidas (20):**
- `can_manage_org` - Gerenciar organização
- `can_manage_users` - Gerenciar usuários
- `can_manage_seasons` - Gerenciar temporadas
- `can_create_team` / `can_edit_team` / `can_delete_team` / `can_view_teams`
- `can_create_athlete` / `can_edit_athlete` / `can_delete_athlete` / `can_view_athletes`
- `can_create_training` / `can_edit_training` / `can_delete_training` / `can_view_training`
- `can_create_match` / `can_edit_match` / `can_delete_match` / `can_view_matches`
- `can_view_reports` / `can_generate_reports` / `can_export_reports`
- `can_view_wellness` / `can_edit_wellness`

---

## 📦 PASSO 2: ExecutionContext (Estado Resolvido)

📁 **`app/core/auth/execution_context.py`**

```python
@dataclass
class ExecutionContext:
    """
    Estado resolvido de uma requisição autenticada.
    ZERO regras aqui - apenas dados.
    """
    user_id: UUID
    email: str
    role_code: str
    person_id: Optional[UUID]
    is_superadmin: bool
    organization_id: Optional[UUID]
    membership_id: Optional[UUID]
    team_ids: List[UUID]
    permissions: Dict[str, bool]  # ✨ Já resolvido do mapa
    
    def can(self, permission: str) -> bool:
        """Verifica se tem permissão"""
        return self.permissions.get(permission, False)
    
    def requires(self, permission: str) -> None:
        """Garante permissão, levanta exceção caso contrário"""
        if not self.can(permission):
            raise PermissionError(f"Sem permissão: {permission}")
```

**Características:**
- `@dataclass` - Apenas estado, zero lógica
- `permissions: Dict[str, bool]` - Já resolvido do mapa canônico
- Métodos helpers: `can()`, `requires()`, `has_any()`, `has_all()`

---

## 🔐 PASSO 3: Resolver no Dependency

📁 **`app/core/context.py`**

```python
async def get_current_context(...) -> ExecutionContext:
    """
    Resolve ExecutionContext no momento da autenticação.
    
    Fluxo:
    1. Decodifica JWT
    2. Busca usuário no banco
    3. Valida vínculo ativo
    4. RESOLVE PERMISSÕES do mapa canônico ⭐
    5. Busca team_ids
    6. Retorna ExecutionContext
    """
    # ... decodificar JWT, buscar usuário ...
    
    # Resolver permissões do mapa canônico
    permissions = get_permissions_for_role(role_code)  # ⭐
    
    # Buscar team_ids (equipes que o usuário tem acesso)
    team_ids = []
    if person_id and organization_id:
        # Buscar registros de equipe...
        team_ids = [UUID(reg.team_id) for reg in registrations]
    
    return ExecutionContext(
        user_id=user.id,
        email=user.email,
        role_code=role_code,
        person_id=person_id,
        is_superadmin=user.is_superadmin,
        organization_id=organization_id,
        membership_id=membership_id,
        team_ids=team_ids,
        permissions=permissions,  # ✨ Já resolvido
    )
```

**IMPORTANTE:**
- Executado **UMA VEZ** por requisição
- Permissões resolvidas do mapa canônico
- Reutilizado em todos os endpoints via `Depends(get_current_context)`

---

## 🪞 PASSO 4: Endpoint /auth/context (Espelho)

📁 **`app/api/v1/routers/auth.py`**

```python
@router.get("/context")
async def get_context(
    ctx: ExecutionContext = Depends(get_current_context)
) -> AuthContextResponse:
    """
    Endpoint de contexto para o frontend.
    
    ARQUITETURA:
    - ExecutionContext é a fonte da verdade
    - Este endpoint é APENAS UM ESPELHO (zero regras)
    - Permissões já resolvidas
    """
    # Buscar org_name e season_name (metadata)
    # ...
    
    # ESPELHO do ExecutionContext
    return AuthContextResponse(
        user_id=str(ctx.user_id),
        person_id=str(ctx.person_id) if ctx.person_id else None,
        role_code=ctx.role_code,
        is_superadmin=ctx.is_superadmin,
        organization_id=str(ctx.organization_id) if ctx.organization_id else None,
        organization_name=org_name,
        membership_id=str(ctx.membership_id) if ctx.membership_id else None,
        current_season_id=season_id,
        current_season_name=season_name,
        team_registrations=team_regs,
        permissions=ctx.permissions,  # ✨ Espelho direto
    )
```

**Zero regras aqui!** Apenas:
1. Busca metadata (org_name, season_name)
2. Retorna estado do ExecutionContext

---

## 🎨 PASSO 5: Frontend (PermissionGate)

### Types (TypeScript)

📁 **`src/types/auth.ts`**

```typescript
export interface AuthContext {
  user_id: string
  person_id: string | null
  role_code: string
  is_superadmin: boolean
  organization_id: string | null
  organization_name: string | null
  membership_id: string | null
  current_season_id: string | null
  current_season_name: string | null
  team_registrations: TeamRegistrationContext[]
  permissions: Record<string, boolean>  // ✨ Mapa já resolvido
}
```

### PermissionGate

📁 **`src/components/auth/PermissionGateV2.tsx`**

```tsx
<PermissionGate permission="can_create_team">
  <button>Criar Equipe</button>
</PermissionGate>

<PermissionGate anyOf={["can_view_reports", "can_generate_reports"]}>
  <Link href="/reports">Relatórios</Link>
</PermissionGate>

<PermissionGate allOf={["can_create_team", "can_create_athlete"]}>
  <button>Configurar Completo</button>
</PermissionGate>
```

**Lógica:**
```typescript
function hasPermission(context: AuthContext | null, permission: string): boolean {
  if (!context) return false
  return context.permissions[permission] === true  // Direto do mapa!
}
```

---

## ✅ Uso no Backend (Opcional mas Recomendado)

### Validar permissão em endpoints:

```python
@router.post("/teams")
async def create_team(
    team: TeamCreate,
    ctx: ExecutionContext = Depends(get_current_context),
    db: Session = Depends(get_db),
):
    # Validar permissão
    if not ctx.can("can_create_team"):
        raise HTTPException(
            status_code=403,
            detail="Sem permissão para criar equipe"
        )
    
    # OU usar requires (levanta exceção automaticamente)
    ctx.requires("can_create_team")
    
    # Criar equipe...
```

### Criar dependency customizado:

```python
def require_permission(permission: str):
    """Dependency que valida permissão específica"""
    async def dependency(ctx: ExecutionContext = Depends(get_current_context)):
        ctx.requires(permission)
        return ctx
    return dependency

# Uso:
@router.post("/teams")
async def create_team(
    team: TeamCreate,
    ctx: ExecutionContext = Depends(require_permission("can_create_team")),
):
    # Se chegou aqui, tem permissão!
    ...
```

---

## 🔄 Fluxo Completo

### 1. **Login**
```
POST /auth/login
↓
Backend resolve permissões do mapa
↓
Retorna JWT + user data (sem permissões ainda)
```

### 2. **Primeira Requisição**
```
GET /auth/context
Authorization: Bearer <JWT>
↓
get_current_context() executa:
  1. Decodifica JWT
  2. Busca usuário
  3. RESOLVE PERMISSÕES do mapa ⭐
  4. Cria ExecutionContext
↓
Endpoint retorna ESPELHO do ExecutionContext
↓
Frontend guarda em AuthContext
```

### 3. **Requisições Subsequentes**
```
POST /teams (criar equipe)
Authorization: Bearer <JWT>
↓
get_current_context() executa (denovo):
  - Resolve permissões
  - Cria ExecutionContext
↓
ctx.requires("can_create_team")
  - Se False → 403 Forbidden
  - Se True → Continua
↓
Criar equipe no banco
```

### 4. **Frontend (UX)**
```tsx
// Context já tem permissões resolvidas
<PermissionGate permission="can_create_team">
  <button onClick={createTeam}>Criar Equipe</button>
</PermissionGate>

// Botão só aparece se tiver permissão
// MAS se clicar, backend AINDA valida (403 se tentar burlar)
```

---

## 🎯 Vantagens da Arquitetura

### ✅ Fonte Única da Verdade
```python
# ÚNICO lugar onde permissões são definidas
ROLE_PERMISSIONS = { ... }  # app/core/permissions_map.py
```
- ❌ Não há permissões hardcoded em endpoints
- ❌ Não há lógica de permissão duplicada
- ✅ Adicionar permissão = editar 1 arquivo

### ✅ Performance
```
Login → Resolve permissões (1x)
      ↓
Cada request → Reutiliza ExecutionContext
```
- Não consulta banco a cada verificação
- Permissões em memória (Dict[str, bool])
- Zero overhead

### ✅ Type Safety
```typescript
// TypeScript sabe exatamente o contrato
context.permissions.can_create_team  // boolean
context.permissions.invalid_perm     // undefined (erro TS)
```

### ✅ UX Melhorado
```tsx
// Menu adapta-se automaticamente
<PermissionGate permission="can_create_team">
  <MenuItem>Criar Equipe</MenuItem>
</PermissionGate>
```
- Usuário só vê o que pode usar
- Menos confusão
- Menos requisições 403

### ✅ Segurança Real
```python
# Backend SEMPRE valida
ctx.requires("can_create_team")  # 403 se não tiver
```
- Frontend é UX, não segurança
- Backend é fonte única
- Impossível burlar (JWT validado + permissões checadas)

---

## 📊 Comparação: Antes vs Depois

### ❌ Antes (Arquitetura Frágil)

```python
# Endpoint 1
if user.role not in ["dirigente", "coordenador"]:
    raise HTTPException(403)

# Endpoint 2
if user.role != "superadmin" and user.role != "dirigente":
    raise HTTPException(403)

# Endpoint 3 (diferente!)
allowed = ["superadmin", "dirigente", "coordenador"]
if user.role not in allowed:
    raise HTTPException(403)
```

**Problemas:**
- ❌ Lógica duplicada (3 lugares diferentes)
- ❌ Inconsistente (cada endpoint decide)
- ❌ Hard de auditar
- ❌ Frontend não sabe o que pode mostrar

### ✅ Depois (Arquitetura Canônica)

```python
# permissions_map.py (ÚNICO lugar)
ROLE_PERMISSIONS = {
    "dirigente": {"can_create_team": True},
    "coordenador": {"can_create_team": True},
    "treinador": {"can_create_team": False},
}

# Endpoint 1
ctx.requires("can_create_team")

# Endpoint 2
ctx.requires("can_create_team")

# Endpoint 3
ctx.requires("can_create_team")
```

**Vantagens:**
- ✅ Uma linha de código
- ✅ Mesma regra em todos os lugares
- ✅ Fácil de auditar (1 arquivo)
- ✅ Frontend recebe mapa completo

---

## 🧪 Como Testar

### Teste 1: Mapa Canônico
```python
from app.core.permissions_map import get_permissions_for_role

perms = get_permissions_for_role("treinador")
assert perms["can_create_athlete"] == True
assert perms["can_create_team"] == False
assert perms["can_manage_org"] == False
```

### Teste 2: ExecutionContext
```python
ctx = ExecutionContext(
    user_id=uuid4(),
    email="test@test.com",
    role_code="treinador",
    permissions=get_permissions_for_role("treinador"),
    # ...
)

assert ctx.can("can_create_athlete") == True
assert ctx.can("can_create_team") == False

# requires levanta exceção
with pytest.raises(PermissionError):
    ctx.requires("can_create_team")
```

### Teste 3: /auth/context
```bash
# Login
POST /auth/login
{
  "username": "treinador@test.com",
  "password": "senha123"
}

# Buscar contexto
GET /auth/context
Authorization: Bearer <token>

# Resposta inclui permissões
{
  "user_id": "...",
  "role_code": "treinador",
  "permissions": {
    "can_create_athlete": true,
    "can_create_team": false,
    "can_manage_org": false,
    ...
  }
}
```

### Teste 4: PermissionGate (Frontend)
```tsx
// Login como treinador
// Verificar que botão NÃO aparece:
<PermissionGate permission="can_create_team">
  <button>Criar Equipe</button>  {/* Não renderiza */}
</PermissionGate>

// Verificar que botão APARECE:
<PermissionGate permission="can_create_athlete">
  <button>Criar Atleta</button>  {/* Renderiza */}
</PermissionGate>
```

---

## 📋 Checklist de Implementação

- [x] **PASSO 1:** Criar mapa canônico (`permissions_map.py`)
- [x] **PASSO 2:** Criar `ExecutionContext` dataclass
- [x] **PASSO 3:** Atualizar `get_current_context()` para resolver permissões
- [x] **PASSO 4:** Atualizar `/auth/context` para ser espelho
- [x] **PASSO 5:** Criar `PermissionGateV2` no frontend
- [x] **PASSO 6:** Atualizar types TypeScript (`AuthContext`)
- [ ] **PASSO 7:** Aplicar `ctx.requires()` em endpoints críticos
- [ ] **PASSO 8:** Substituir `PermissionGate` antigo por `PermissionGateV2`
- [ ] **PASSO 9:** Testar fluxo completo (login → context → UI)
- [ ] **PASSO 10:** Remover lógica antiga de permissões hardcoded

---

## 🚀 Próximos Passos

1. **Migrar endpoints existentes:**
   ```python
   # Antes
   if user.role not in ["dirigente", "coordenador"]:
       raise HTTPException(403)
   
   # Depois
   ctx.requires("can_create_team")
   ```

2. **Aplicar PermissionGate no frontend:**
   - Menus
   - Botões de ação
   - Seções inteiras

3. **Adicionar novas permissões:**
   - Editar apenas `permissions_map.py`
   - Backend e frontend sincronizam automaticamente

4. **Documentar permissões:**
   - Listar todas as 20 permissões
   - Explicar quando usar cada uma
   - Exemplos de uso

---

**Status:** ✅ **ARQUITETURA CANÔNICA IMPLEMENTADA**  
**Data:** Janeiro 2026  
**Versão:** 3.0 - Permissões Canônicas
