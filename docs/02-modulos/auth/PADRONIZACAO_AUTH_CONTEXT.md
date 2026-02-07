<!-- STATUS: DEPRECATED | razao: detalhes de implementacao, nao referencia canonica -->

# ✅ Padronização Completa - Auth Context & PermissionGate

## 📋 Resumo das Mudanças

### 1. **Contrato Fixo para `/auth/context`** ⭐

Padronizamos o endpoint GET `/auth/context` com um **contrato fixo** que o frontend sempre pode confiar.

#### Backend (`auth.py`):
```python
class AuthContextResponse(BaseModel):
    """CONTRATO FIXO - Sempre retorna todos os campos"""
    user_id: str
    person_id: Optional[str] = None
    role_code: str
    is_superadmin: bool = False
    organization_id: Optional[str] = None
    organization_name: Optional[str] = None          # ✨ NOVO
    membership_id: Optional[str] = None
    current_season_id: Optional[str] = None           # ✨ NOVO
    current_season_name: Optional[str] = None         # ✨ NOVO
    team_registrations: List[TeamRegistrationContext] = []
```

#### Garantias do Contrato:
- ✅ **Todos os campos sempre presentes** (nunca `undefined`)
- ✅ Campos opcionais são `null` (não ausentes)
- ✅ Arrays vazios ao invés de `null` (`team_registrations: []`)
- ✅ Booleans têm default (`is_superadmin: false`)

#### Frontend (`types/auth.ts`):
```typescript
export interface AuthContext {
  user_id: string
  person_id: string | null
  role_code: string
  is_superadmin: boolean
  organization_id: string | null
  organization_name: string | null          // ✨ NOVO
  membership_id: string | null
  current_season_id: string | null          // ✨ NOVO
  current_season_name: string | null        // ✨ NOVO
  team_registrations: TeamRegistrationContext[]
}
```

---

### 2. **PermissionGate - Controle de UI** 🚪

Criamos um componente React para controle de visibilidade baseado em permissões.

#### ⚠️ IMPORTANTE: Não é Segurança!

```
┌─────────────────────────────────────────┐
│  PermissionGate = UX                    │
│  Backend = SEGURANÇA                    │
└─────────────────────────────────────────┘
```

#### O que FAZ:
- ✅ Melhora UX (esconde elementos inacessíveis)
- ✅ Evita requisições desnecessárias
- ✅ Reduz confusão do usuário

#### O que NÃO FAZ:
- ❌ **NÃO é segurança** (código é público no cliente)
- ❌ NÃO impede requisições diretas ao backend
- ❌ Backend SEMPRE valida (403/401)

#### Uso:

```tsx
// Permissão única
<PermissionGate permission="manage_users">
  <button>Criar Usuário</button>
</PermissionGate>

// Qualquer uma (OR)
<PermissionGate anyOf={["view_reports", "generate_reports"]}>
  <Link href="/reports">Relatórios</Link>
</PermissionGate>

// Todas (AND)
<PermissionGate allOf={["manage_teams", "manage_athletes"]}>
  <button>Configurar Equipe</button>
</PermissionGate>

// Com fallback
<PermissionGate 
  permission="manage_organization"
  fallback={<div>Sem permissão</div>}
>
  <button>Editar</button>
</PermissionGate>
```

#### PermissionGateInverse:

```tsx
// Mostra apenas se NÃO tiver permissão
<PermissionGateInverse permission="manage_users">
  <div>Entre em contato com administrador</div>
</PermissionGateInverse>
```

---

## 📁 Arquivos Modificados

### Backend:
1. ✏️ `app/api/v1/routers/auth.py`
   - Atualizado `AuthContextResponse` (+ 3 campos)
   - Endpoint `GET /auth/context` busca organização e temporada ativa
   - Documentação expandida sobre contrato fixo

### Frontend:
2. ✏️ `src/types/auth.ts`
   - Adicionado interface `AuthContext` (contrato fixo)
   - Adicionado interface `TeamRegistrationContext`

3. ✏️ `src/lib/auth/actions.ts`
   - `getContextAction()` tipado com `AuthContext`
   - Documentação sobre contrato fixo

4. ✨ `src/components/auth/PermissionGate.tsx`
   - Componente `PermissionGate` (3 modos: single, anyOf, allOf)
   - Componente `PermissionGateInverse`
   - Documentação inline extensa sobre não ser segurança

5. ✨ `src/app/examples/permission-gate/page.tsx`
   - 8 exemplos práticos de uso
   - Seção de alerta sobre segurança
   - Casos reais (menu, dashboard, etc)

6. ✏️ `ENDPOINTS_AUTH_COMPLETO.md`
   - Seção sobre contrato fixo de `/auth/context`
   - Seção sobre `PermissionGate`
   - Exemplos de uso

---

## 🎯 Benefícios

### 1. **Previsibilidade**
Frontend sempre sabe exatamente o que esperar de `/auth/context`:
```typescript
// Sempre funciona (nunca undefined)
const orgName = context?.organization_name ?? 'Sem organização'
const seasonName = context?.current_season_name ?? 'Sem temporada'
```

### 2. **Type Safety**
TypeScript garante que todos os campos estão presentes:
```typescript
// ❌ Erro de compilação se campo não existir
context.org_name  // Property 'org_name' does not exist

// ✅ Correto
context.organization_name  // string | null
```

### 3. **Melhor UX**
Interface adapta-se automaticamente às permissões:
```tsx
<nav>
  <a href="/">Home</a>
  
  {/* Só aparece se tiver permissão */}
  <PermissionGate permission="view_athletes">
    <a href="/athletes">Atletas</a>
  </PermissionGate>
  
  <PermissionGate permission="manage_teams">
    <a href="/teams">Equipes</a>
  </PermissionGate>
</nav>
```

### 4. **Menos Requisições 403**
Usuário não vê botões que retornariam erro:
```tsx
{/* Botão só aparece se puder usar */}
<PermissionGate permission="manage_users">
  <button onClick={createUser}>Criar Usuário</button>
</PermissionGate>

{/* Ao invés de mostrar e depois dar erro 403 */}
```

---

## 🔒 Segurança - Lembretes Importantes

### 1. **PermissionGate não é segurança**
```
Usuário pode:
- Inspecionar código React
- Manipular state local
- Ver componentes "escondidos"
- Fazer requisições diretas via fetch/curl

Por isso:
Backend SEMPRE valida permissões!
```

### 2. **Backend é a fonte da verdade**
```python
# Backend valida em CADA endpoint
@router.post("/users")
async def create_user(
    user: UserCreate,
    current_user: User = Depends(require_permission("manage_users"))
):
    # Só executa se tiver permissão
    ...
```

### 3. **401/403 são esperados**
Se alguém tentar burlar o frontend:
```
POST /api/v1/users
Authorization: Bearer <token_sem_permissao>

← 403 Forbidden
{
  "error_code": "FORBIDDEN",
  "message": "Permissão insuficiente"
}
```

---

## 🧪 Como Testar

### Teste 1: Contrato Fixo
```typescript
// Fazer login
const login = await loginAction(credentials)

// Buscar contexto
const { context } = await getContextAction()

// Verificar que todos os campos existem (nunca undefined)
console.assert(context.user_id !== undefined)
console.assert(context.role_code !== undefined)
console.assert(context.is_superadmin !== undefined)
console.assert('organization_name' in context)  // existe (pode ser null)
console.assert('current_season_name' in context)  // existe (pode ser null)
```

### Teste 2: PermissionGate
```tsx
// 1. Login como usuário SEM permissão "manage_users"
// 2. Verificar que botão não aparece:
<PermissionGate permission="manage_users">
  <button id="create-user">Criar Usuário</button>
</PermissionGate>

// 3. Login como usuário COM permissão "manage_users"
// 4. Verificar que botão APARECE

// 5. Tentar manipular JavaScript no console:
document.querySelector('#create-user').click()
// Ainda assim, backend retorna 403
```

### Teste 3: Menu Adaptativo
```tsx
// Login como diferentes roles
// Verificar que menu adapta-se:

// Atleta: vê apenas "Home" e "Meu Perfil"
// Treinador: vê + "Treinos" e "Atletas"
// Coordenador: vê + "Equipes" e "Relatórios"
// Dirigente: vê + "Usuários" e "Organização"
```

---

## 📚 Documentação Atualizada

1. ✅ **ENDPOINTS_AUTH_COMPLETO.md**
   - Seção sobre contrato fixo de `/auth/context`
   - Seção sobre `PermissionGate`
   - Exemplos de uso
   - Avisos de segurança

2. ✅ **Exemplos Práticos**
   - `/examples/permission-gate` - 8 casos de uso
   - Menu adaptativo
   - Dashboard por permissões
   - Fallbacks e inversão

---

## ✅ Checklist Final

- [x] Backend: `AuthContextResponse` padronizado (+ 3 campos)
- [x] Backend: Endpoint `/context` busca org + season
- [x] Frontend: Interface `AuthContext` tipada
- [x] Frontend: `getContextAction()` usa tipo correto
- [x] Frontend: `PermissionGate` implementado
- [x] Frontend: `PermissionGateInverse` implementado
- [x] Frontend: Exemplos práticos (8 casos)
- [x] Documentação: Contrato fixo explicado
- [x] Documentação: PermissionGate com avisos de segurança
- [x] Testes: Sem erros TypeScript

---

## 🚀 Próximos Passos

1. **Testar fluxo completo:**
   - Login → `getContextAction()` → Verificar campos
   - Testar com diferentes roles
   - Verificar que backend rejeita requisições sem permissão

2. **Usar em produção:**
   - Aplicar `PermissionGate` em menus existentes
   - Proteger botões de ações sensíveis
   - Adicionar mensagens de "sem permissão" com `fallback`

3. **Monitorar:**
   - Logs de 403 (tentativas de acesso não autorizado)
   - Feedback de usuários sobre UX melhorada
   - Performance (cache de permissões no client)

---

**Status:** ✅ **COMPLETO**  
**Data:** Janeiro 2026  
**Versão:** 2.0 - Contrato Fixo + PermissionGate
