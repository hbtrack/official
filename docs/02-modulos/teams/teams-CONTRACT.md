<!-- STATUS: NEEDS_REVIEW | verificar contra openapi.json -->

# CONTRATO REAL - Módulo Teams

**Última atualização:** 15 de Janeiro de 2026
**Versão:** 1.5 (gestão completa de staff + banner sem coach)
**Arquivos analisados:**
- Frontend: `src/app/(admin)/teams/**`, `components/teams-v2/**`
- Middleware: `middleware.ts`
- API: `lib/api/teams.ts`, `lib/api/client.ts`
- Backend: `app/api/v1/routers/teams.py`, `app/api/v1/routers/team_invites.py`, `app/api/v1/routers/team_members.py`
- Modelos: `app/models/team.py`, `app/models/team_membership.py`, `app/models/team_registration.py`
- Testes: `tests/e2e/teams/*.spec.ts`

---

## 1. ROTAS FRONTEND

### 1.1. Rotas Públicas (sem auth)
Nenhuma. Todas as rotas /teams/** exigem autenticação.

### 1.2. Rotas Protegidas (requer auth)

| Rota | Página | RBAC | TestID Root | Descrição |
|------|--------|------|-------------|-----------|
| `/teams` | Dashboard | Autenticado | `teams-dashboard` | Lista de equipes do usuário |
| `/teams/:id` | Redirect | - | - | Redireciona para `/teams/:id/overview` |
| `/teams/:id/overview` | Overview (SSR) | Autenticado | `team-overview-tab` | Visão geral da equipe |
| `/teams/:id/members` | Members (CSR) | Autenticado | `team-members-tab` | Staff e atletas |
| `/teams/:id/trainings` | Trainings (CSR) | Autenticado | - | Treinos da equipe |
| `/teams/:id/stats` | Stats (SSR) | Autenticado | - | Estatísticas |
| `/teams/:id/settings` | Settings (SSR+CSR) | `canManageTeam` | `teams-settings-root` | Configurações da equipe |
| `/teams/:id/[...tab]` | Catch-all | - | - | Redirect para overview se tab inválida |

**Tabs válidas:** `['overview', 'members', 'trainings', 'stats', 'settings']`

**Nota:** Tab "settings" só aparece no layout se `canManageTeam === true`.

---

## 2. ENDPOINTS API

### 2.1. Teams (Core)

#### GET /teams
**Descrição:** Lista equipes da organização do usuário

**Permissões:** `dirigente`, `coordenador`, `treinador`

**Query Params:**
- `season_id` (opcional, UUID): Filtrar por temporada
- `page` (opcional, int, default: 1): Número da página
- `limit` (opcional, int, default: 50, max: 100): Itens por página
- `include_deleted` (opcional, bool, default: true): Incluir equipes arquivadas

**Response 200:**
```json
{
  "items": [
    {
      "id": "uuid",
      "organization_id": "uuid",
      "name": "string",
      "category_id": 1,
      "gender": "feminino|masculino|misto",
      "is_our_team": true,
      "active_from": "2026-01-01",
      "active_until": null,
      "created_by_user_id": "uuid",
      "created_at": "2026-01-01T00:00:00Z",
      "updated_at": "2026-01-01T00:00:00Z",
      "deleted_at": null,
      "deleted_reason": null
    }
  ],
  "page": 1,
  "limit": 50,
  "total": 10
}
```

**Errors:**
- 401: Não autenticado
- 403: Sem permissão (role inválido)
- 500: Erro interno

---

#### POST /teams
**Descrição:** Cria nova equipe

**Permissões:** `dirigente`, `coordenador`

**Payload:**
```json
{
  "name": "string",              // min 3 chars
  "category_id": 1,              // 1-7
  "gender": "feminino",          // enum
  "is_our_team": true,           // default: true
  "coach_membership_id": "uuid"  // opcional
}
```

**Validações:**
- `name`: min 3 caracteres, max 255
- `category_id`: 1-7 (Mirim, Infantil, Cadete, Juvenil, Júnior, Adulto, Master)
- `gender`: obrigatório, enum ('masculino', 'feminino', 'misto')
- `organization_id`: extraído do token (context)

**Response 201:**
```json
{
  "id": "uuid",
  "organization_id": "uuid",
  "name": "string",
  "category_id": 1,
  "gender": "feminino",
  "is_our_team": true,
  ...
}
```

**Errors:**
- 400: Validação falhou
- 401: Não autenticado
- 403: Sem permissão
- 500: Erro interno

**Pós-criação:** Frontend redireciona para `/teams/{id}/members?isNew=true`

---

#### GET /teams/{teamId}
**Descrição:** Busca detalhes de uma equipe

**Permissões:** `dirigente`, `coordenador`, `treinador`

**Response 200:**
```json
{
  "id": "uuid",
  "organization_id": "uuid",
  "name": "string",
  "category_id": 1,
  "gender": "feminino",
  "is_our_team": true,
  "active_from": "2026-01-01",
  "active_until": null,
  "coach_membership_id": "uuid",
  "created_at": "2026-01-01T00:00:00Z",
  "updated_at": "2026-01-01T00:00:00Z",
  "deleted_at": null
}
```

**Errors:**
- 401: Não autenticado
- 403: Sem permissão (não pertence à organização)
- 404: Equipe não encontrada ou deletada
- 500: Erro interno

---

#### PATCH /teams/{teamId}
**Descrição:** Atualiza equipe

**Permissões:** `dirigente`, `coordenador`

**Payload (todos opcionais):**
```json
{
  "name": "string",
  "category_id": 1,
  "gender": "feminino",
  "is_our_team": true,
  "active_from": "2026-01-01",
  "active_until": "2026-12-31",
  "coach_membership_id": "uuid"
}
```

**Response 200:**
```json
{
  "id": "uuid",
  ...
}
```

**Errors:**
- 400: Validação falhou
- 401: Não autenticado
- 403: Sem permissão
- 404: Equipe não encontrada
- 500: Erro interno

**Pós-update:** Frontend executa `router.refresh()` para revalidar Server Components

---

#### DELETE /teams/{teamId}
**Descrição:** Exclui equipe (soft delete)

**Permissões:** `coordenador`, `dirigente`

**Query Params:**
- `reason` (opcional, string, default: "Exclusão manual"): Motivo da exclusão

**Response 204:** No Content

**Comportamento:**
- Marca `deleted_at = now()`
- Define `deleted_reason = {reason}`
- Não remove fisicamente do banco
- Equipe passa a aparecer como "Arquivada" no frontend

**Errors:**
- 401: Não autenticado
- 403: Sem permissão
- 404: Equipe não encontrada
- 500: Erro interno

---

### 2.2. Team Staff (Membros)

#### GET /teams/{teamId}/staff
**Descrição:** Lista comissão técnica (staff) vinculada à equipe via `team_memberships`

**Permissões:** `dirigente`, `coordenador`, `treinador`

**Query Params:**
- `active_only` (opcional, bool, default: true): Apenas vínculos ativos

**Response 200:**
```json
{
  "items": [
    {
      "id": "uuid",
      "person_id": "uuid",
      "full_name": "João Silva",
      "role": "treinador",
      "status": "ativo",
      "start_at": "2026-01-01T00:00:00Z",
      "end_at": null,
      "resend_count": 0,
      "can_resend_invite": false
    },
    {
      "id": "uuid",
      "person_id": "uuid",
      "full_name": "Maria Santos",
      "role": "coordenador",
      "status": "pendente",
      "start_at": null,
      "end_at": null,
      "invite_token": "abc123",
      "invited_at": "2026-01-10T10:00:00Z",
      "resend_count": 1,
      "can_resend_invite": true
    }
  ],
  "total": 2
}
```

**Nota:** Retorna TODOS os membros da comissão técnica (treinadores, coordenadores, dirigentes) com status `ativo` ou `pendente`. Inclui dados de convites pendentes do fluxo welcome.

**Errors:**
- 401: Não autenticado
- 403: Sem permissão
- 404: Equipe não encontrada
- 500: Erro interno

---

#### DELETE /teams/{teamId}/staff/{membershipId}
**Descrição:** Remove membro da comissão técnica (universal para dirigentes/coordenadores/treinadores)

**Permissões:** `dirigente`, `coordenador`

**Path Params:**
- `teamId` (UUID): ID da equipe
- `membershipId` (UUID): ID do `team_membership` a ser removido

**Comportamento condicional:**
- **SE treinador:** Encerra vínculo (`end_at=now()`, `status='inativo'`), seta `team.coach_membership_id = NULL`, cria notificação WebSocket, retorna `{team_without_coach: true}`
- **SENÃO:** Soft delete (`deleted_at=now()`, `deleted_reason="Removido por {role}"`), retorna `{team_without_coach: false}`

**Response 200:**
```json
{
  "success": true,
  "team_without_coach": true,
  "message": "Treinador removido com sucesso. Equipe sem treinador."
}
```

**Errors:**
- 400: `membership_id` não pertence à equipe especificada
- 401: Não autenticado
- 403: Sem permissão (apenas dirigente/coordenador)
- 404: Membership não encontrado
- 500: Erro interno

---

### 2.3. Team Invites (RESTful - Sprint 1)

#### GET /teams/{teamId}/invites
**Descrição:** Lista convites pendentes da equipe

**Permissões:** `dirigente`, `coordenador`, `treinador`

**Response 200:**
```json
{
  "items": [
    {
      "id": "uuid",
      "person_id": "uuid",
      "name": "Maria Silva",
      "email": "maria@example.com",
      "role": "Treinador",
      "status": "pendente",
      "invited_at": "2026-01-10T10:00:00Z",
      "expires_at": "2026-01-12T10:00:00Z",
      "is_expired": false,
      "hours_remaining": 42,
      "initials": "MS"
    }
  ],
  "total": 1
}
```

**Campos:**
- `is_expired` (bool): Token expirado (Sprint 3)
- `hours_remaining` (int): Horas restantes até expiração (Sprint 3)

**Errors:**
- 401: Não autenticado
- 403: Sem permissão
- 404: Equipe não encontrada
- 500: Erro interno

---

#### POST /teams/{teamId}/invites
**Descrição:** Envia convite para novo membro (token 48h)

**Permissões:** `dirigente`, `coordenador`

**Payload:**
```json
{
  "email": "user@example.com",
  "role": "membro"  // opcional, default: "membro"
}
```

**Validações (Sprint 3 - Hardening + R15 - 14/01/2026):**
- Verifica se já é membro ATIVO → bloqueia (409 MEMBER_ACTIVE)
- Verifica se já existe convite pendente → bloqueia (409 INVITE_EXISTS)
- Verifica conflitos de gênero/categoria → bloqueia (409 BINDING_CONFLICT)
  - Pessoa com vínculo em equipe feminina NÃO pode ser convidada para equipe masculina
  - Pessoa com vínculo em Sub-16 NÃO pode ser convidada para Sub-18 (categoria superior ou igual)
  - Pessoa com vínculo em Sub-16 PODE ser convidada para Sub-14 (categoria inferior)
- **NOTA R15 (14/01/2026):** Validação de idade x categoria SOMENTE ocorre no **welcome/complete**
  - No convite: backend não valida idade (pessoa pode não ter birth_date ainda)
  - No welcome: birth_date se torna obrigatório e validação R15 é aplicada

**Response 201:**
```json
{
  "success": true,
  "message": "Convite enviado com sucesso",
  "code": "INVITE_SENT",
  "person_id": "uuid",
  "email_sent": true
}
```

**Códigos de Erro (Sprint 3):**

| Código | HTTP | Descrição |
|--------|------|-----------|
| `INVITE_SENT` | 201 | Convite enviado com sucesso |
| `TEAM_NOT_FOUND` | 404 | Equipe não encontrada |
| `INVITE_EXISTS` | 409 | Já existe convite pendente |
| `MEMBER_ACTIVE` | 409 | Já é membro ativo |
| `BINDING_CONFLICT` | 409 | Conflito de gênero/categoria |
| `EMAIL_FAILED` | 500 | Falha ao enviar email |

**Errors:**
- 400: Validação falhou
- 401: Não autenticado
- 403: Sem permissão
- 404: Equipe não encontrada
- 409: Conflito (já existe convite/membro ou binding conflict)
- 500: Erro ao enviar email

**Comportamento:**
1. Cria `Person` se não existir
2. Cria `User` com `status='inativo'` se não existir
3. Cria `PasswordReset` com `token_type='welcome'`, expira em 48h
4. Cria `OrgMembership` com role especificado
5. Cria `TeamMembership` com `status='pendente'`
6. Envia email com token
7. Commit se email enviado com sucesso, rollback caso contrário

---

#### POST /teams/{teamId}/invites/{inviteId}/resend
**Descrição:** Reenvia convite expirado (Sprint 3 - Idempotência)

**Permissões:** `dirigente`, `coordenador`

**Comportamento (Sprint 3):**
- Se token ainda válido (>4h restantes): reutiliza token, apenas reenvia email
- Se token expirado ou <4h restantes: invalida token antigo, cria novo (48h)

**Response 200:**
```json
{
  "success": true,
  "message": "Convite reenviado com sucesso",
  "code": "INVITE_RESENT",
  "person_id": "uuid",
  "email_sent": true
}
```

**Errors:**
- 401: Não autenticado
- 403: Sem permissão
- 404: Convite não encontrado ou não está pendente
- 500: Erro ao enviar email

---

#### DELETE /teams/{teamId}/invites/{inviteId}
**Descrição:** Cancela convite pendente (soft delete)

**Permissões:** `dirigente`, `coordenador`

**Comportamento:**
1. Invalida token welcome (`used_at = now()`)
2. Soft delete do `TeamMembership` (`deleted_at`, `deleted_reason`)

**Response 200:**
```json
{
  "success": true,
  "message": "Convite cancelado com sucesso",
  "code": "INVITE_REVOKED",
  "person_id": "uuid",
  "email_sent": false
}
```

**Errors:**
- 401: Não autenticado
- 403: Sem permissão
- 404: Convite não encontrado
- 500: Erro interno

---

### 2.4. Team Registrations (Atletas)

#### POST /teams/{teamId}/registrations
**Descrição:** Move atleta para equipe na temporada (encerra vínculos ativos e cria novo)

**Permissões:** `treinador`, `coordenador`, `dirigente`

**Payload:**
```json
{
  "athlete_id": "uuid",
  "start_at": "2026-01-01",           // opcional, default: today
  "end_previous_at": "2026-01-01",    // opcional, default: start_at
  "role": "string"                    // opcional
}
```

**Comportamento:**
1. Valida que equipe e atleta existem
2. Calcula categoria natural do atleta baseado em `season.year` e `athlete.birth_date`
3. Encerra vínculos ativos do atleta na temporada (`end_at = end_previous_at`)
4. Cria novo `TeamRegistration` na equipe de destino

**Response 201:**
```json
{
  "id": "uuid",
  "athlete_id": "uuid",
  "team_id": "uuid",
  "season_id": "uuid",
  "category_id": 1,
  "organization_id": "uuid",
  "start_at": "2026-01-01T00:00:00Z",
  "end_at": null,
  ...
}
```

**Errors:**
- 401: Não autenticado
- 403: Sem permissão
- 404: Equipe ou atleta não encontrado
- 409: Período sobreposto (RDB10)
- 422: Categoria não encontrada ou range de datas inválido
- 500: Erro interno

---

## 3. MODELOS DE DADOS (Backend)

### 3.1. Team

**Tabela:** `teams`

**Campos:**
```python
id: UUID (PK)
organization_id: UUID (FK organizations, NOT NULL)
name: String(255, NOT NULL)
category_id: Integer (FK categories, NOT NULL)
gender: String(20, NOT NULL)  # 'masculino', 'feminino', 'misto'
is_our_team: Boolean (NOT NULL, default=True)
active_from: Date (NULL)
active_until: Date (NULL)
created_by_user_id: UUID (FK users, NULL)
created_at: DateTime (NOT NULL, default=now())
updated_at: DateTime (NOT NULL, default=now())
deleted_at: DateTime (NULL)  # soft delete
deleted_reason: Text (NULL)  # soft delete
```

**Relações:**
- `organization` → `Organization` (many-to-one)
- `registrations` → `TeamRegistration[]` (one-to-many)

**Properties:**
- `is_deleted: bool` → `deleted_at is not None`
- `is_active: bool` → não deletado + dentro do período active_from/active_until

**Métodos:**
- `soft_delete(reason: str)` → marca deleted_at e deleted_reason

**Nota:** NÃO tem `season_id`. NÃO tem `created_by_membership_id`.

---

### 3.2. TeamMembership (Staff)

**Tabela:** `team_memberships`

**Campos:**
```python
id: UUID (PK)
person_id: UUID (FK persons, NOT NULL)
team_id: UUID (FK teams, NOT NULL)
org_membership_id: UUID (FK org_memberships, NULL)
start_at: DateTime (NOT NULL, default=now())
end_at: DateTime (NULL)  # NULL = ativo
status: String (NOT NULL, default='pendente')  # 'pendente', 'ativo', 'inativo'
created_at: DateTime (NOT NULL, default=now())
updated_at: DateTime (NOT NULL, default=now())
deleted_at: DateTime (NULL)
deleted_reason: Text (NULL)
```

**Relações:**
- `person` → `Person` (many-to-one)
- `team` → `Team` (many-to-one)
- `org_membership` → `OrgMembership` (many-to-one, optional)

**Properties:**
- `is_active: bool` → status=='ativo' e end_at is None e não deletado
- `is_pending: bool` → status=='pendente' e não deletado

---

### 3.3. TeamRegistration (Atletas)

**Tabela:** `team_registrations`

**Campos:**
```python
id: UUID (PK)
athlete_id: UUID (FK athletes, NOT NULL)
team_id: UUID (FK teams, NOT NULL)
start_at: DateTime (NOT NULL, default=now())
end_at: DateTime (NULL)  # NULL = ativo
created_at: DateTime (NOT NULL, default=now())
updated_at: DateTime (NOT NULL, default=now())
deleted_at: DateTime (NULL)
deleted_reason: Text (NULL)
```

**Relações:**
- `athlete` → `Athlete` (many-to-one)
- `team` → `Team` (many-to-one)

**Properties:**
- `is_active: bool` → end_at is None e deleted_at is None

**Constraints:**
- `CheckConstraint`: `end_at IS NULL OR end_at >= start_at`

**Nota:** NÃO tem `season_id`, `category_id`, `organization_id` (V1.2).

---

## 4. RBAC (Permissões)

### 4.1. Roles e Permissões

**Hierarquia:**
```typescript
owner: 5
admin: 4
dirigente: 4
coordenador: 3
treinador: 2
membro: 1
atleta: 1
```

**Matriz de Permissões:**

| Role | canManageTeam | canDeleteTeam | canManageMembers | canChangeRoles | canCreateTraining | canEditTraining | canDeleteTraining | canViewStats | canExportData | canLeaveTeam |
|------|---------------|---------------|------------------|----------------|-------------------|-----------------|-------------------|--------------|---------------|--------------|
| owner | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| admin | ✅ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| dirigente | ✅ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| coordenador | ❌ | ❌ | ✅ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| treinador | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | ❌ | ✅ | ❌ | ✅ |
| membro | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ✅ |
| atleta | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ✅ |

**Implementação:**
- Frontend: `useTeamPermissions(teamId)` hook
- Backend: `permission_dep(roles=[...])` dependency

**Nota:** Por enquanto, frontend usa `user.role` global. Backend valida por `org_membership.role`.

---

## 5. NAVEGAÇÃO E REDIRECTS

### 5.1. Redirects Automáticos

| De | Para | Motivo |
|----|------|--------|
| `/teams/:id` | `/teams/:id/overview` | Rota raiz sem tab |
| `/teams/:id/invalid-tab` | `/teams/:id/overview` | Tab não está em VALID_TEAM_TABS |
| `/teams?teamId=X&tab=Y` | `/teams/X/Y` | URL legada (middleware) |
| `/teams?teamId=X` | `/teams/X/overview` | URL legada sem tab (middleware) |
| `/teams/not-uuid/overview` | 404 | teamId não é UUID válido |
| `/teams/fake-uuid/overview` | 404 | teamId não existe no banco |
| `/teams` (sem auth) | `/signin?callbackUrl=/teams` | Sem autenticação |

### 5.2. Middleware Rules (middleware.ts)

**Ordem de execução:**
1. Ignora rotas públicas (`/api`, `/_next`, `/images`, etc)
2. **Autenticação:** Verifica cookie `hb_access_token`
   - Sem token → redirect para `/signin?callbackUrl=...`
   - Com token em rota pública → redirect para `/inicio`
3. **Validação de UUID:** `/teams/:teamId/*`
   - UUID inválido → Next.js resolve (404)
   - UUID válido continua
4. **Validação de tab:** `/teams/:teamId/:tab`
   - Tab inválida → redirect para `/teams/:teamId/overview`
   - Tab uppercase → redirect para lowercase (ex: `/OVERVIEW` → `/overview`)
5. **Redirect legado:** `/teams?teamId=X`
   - Com teamId válido → redirect para `/teams/:teamId/overview`

**Nota Windows:** NTFS é case-insensitive. `/OVERVIEW` pode renderizar diretamente sem redirect do middleware. O layout.tsx tem fallback client-side para normalizar.

---

## 6. VALIDAÇÕES

### 6.1. Frontend

**CreateTeamModal:**
- `name`: trim(), min 3 chars, max 100 chars
- `category_id`: obrigatório, 1-7
- `gender`: obrigatório, enum

**InviteMemberModal:**
- `email`: regex `/^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/`

**SettingsTab:**
- `name`: trim(), min 3 chars
- Confirmação de exclusão: digitar nome da equipe

### 6.2. Backend

**POST /teams:**
- `name`: required, min 3 chars, max 255 chars
- `category_id`: required, FK válido
- `gender`: required, enum válido

**POST /teams/{teamId}/invites:**
- `email`: EmailStr (Pydantic), lowercase
- Validação de duplicidade (Sprint 3)
- Validação de conflito gênero/categoria (Sprint 3)

---

## 7. ESTADOS VISUAIS

### 7.1. Loading
- Skeleton loader para lista de equipes (opcional - muito rápido)
- Skeleton loader para membros/atletas
- Botão "Salvar" desabilitado durante submit

### 7.2. Success
- Toast sucesso após create/update/delete/invite
- Auto-dismiss em 5s
- Redirect após criar equipe (para `/teams/:id/members?isNew=true`)

### 7.3. Error
- Toast erro para erros de API (400, 403, 409, 500)
- Mensagens de validação inline (formulários)
- Retry button em tela de erro

### 7.4. Empty
- Empty state sem equipes (dashboard): CTA "Criar primeira equipe"
- Empty state sem membros: CTA "Convidar primeiro membro"
- Empty state sem treinos: CTA "Criar primeiro treino"
- Empty state sem stats: Mensagem informativa

---

## 8. TESTIDS (Manifesto Completo)

### 8.1. Dashboard (/teams)
- `teams-dashboard`: root da página
- `create-team-btn`: botão criar equipe
- `team-card-{id}`: card de equipe (grid)
- `view-team-{id}`: botão ver equipe

### 8.2. Overview (/teams/:id/overview)
- `team-overview-tab`: root da aba
- (outros testIDs a serem definidos)

### 8.3. Members (/teams/:id/members)
- `team-members-tab`: root da aba
- `invite-member-btn`: botão convidar membro
- `pending-invites-section`: seção de convites pendentes
- `staff-section`: seção de staff
- `athletes-section`: seção de atletas

### 8.4. Settings (/teams/:id/settings)
- `teams-settings-root`: root da aba
- `team-name-input`: input do nome da equipe
- `save-settings-btn`: botão salvar
- `delete-team-btn`: botão excluir equipe

### 8.5. Modals
- `create-team-modal`: modal de criar equipe
- `invite-member-modal`: modal de convidar membro
- `confirm-delete-modal`: modal de confirmação de exclusão

### 8.6. Not Found
- `not-found-page`: página 404

---

## 9. CACHE E PERFORMANCE

### 9.1. Client-side (React Query)
- **staleTime:** 5 minutos
- **gcTime:** 10 minutos
- **refetchOnWindowFocus:** true
- **retry:** 3

### 9.2. Server-side (SSR)
- **serverApiClient:** `cache: 'no-store'` (sempre busca dados frescos)
- **getSession():** cache automático do Next.js

### 9.3. API Client Cache (lib/api/client.ts)
- **Endpoints cacheáveis:** `/teams`, `/categories`, `/positions`, `/seasons`
- **TTL padrão:** 5 minutos
- **Invalidação:** Manual via `invalidateCache(pattern)`

---

## 10. LIMITAÇÕES E REGRAS DE NEGÓCIO

### 10.1. Limites Técnicos
- **Paginação:** Default 50 itens, máx 100 itens por página
- **Timeout API:** 15 segundos (cold start Neon Free Tier)
- **Token convite:** Expira em 48 horas
- **Batch invites:** Máximo 5 por vez (frontend)

### 10.2. Regras de Negócio (system_rules.md)

**R6. Vínculo organizacional:**
- Staff: vínculo via `org_memberships` (organização)
- Atleta: vínculo via `team_registrations` (equipe)

**R7. Vínculo ativo:**
- Staff: apenas 1 vínculo ativo por organização
- Atleta: múltiplos vínculos ativos permitidos (mesma organização)

**R28. Soft delete:**
- Todas as exclusões são lógicas (`deleted_at`, `deleted_reason`)

**R29. Reativação:**
- Reativação cria nova linha (novo UUID), não reabre linha anterior

**RF6. Criação de equipes:**
- Permitido para: dirigente, coordenador, treinador (V1.3)
- Campos obrigatórios: name, category_id, gender

**RF7. Alteração de treinador:**
- Apenas dirigente ou coordenador pode alterar
- Treinador só acessa equipes onde é responsável

**2.X.6. Validação de convites duplicados (Sprint 3):**
- Usuário com vínculo pendente/ativo NÃO pode receber novo convite
- **EXCEÇÃO:** Pode receber se for para equipes do mesmo gênero e categoria inferior
- Validações:
  - Gênero diferente → bloqueio
  - Categoria superior/igual → bloqueio
  - Categoria inferior → permitido

---

## 11. DISCREPÂNCIAS CONHECIDAS

### 11.1. Implementação vs Contrato Anterior

**Resolvidas (pós-integração):**
- ✅ Endpoints RESTful `/teams/{teamId}/invites` implementados (Sprint 1)
- ✅ Códigos de erro padronizados (Sprint 3)
- ✅ Validação de convites duplicados (Sprint 3)
- ✅ Idempotência em resend (Sprint 3)
- ✅ Welcome flow completo (Sprint 2)

**Pendentes:**
- ⚠️ Endpoint `/teams/{id}/leave` NÃO existe. Frontend usa DELETE com reason.
- ⚠️ Permissões específicas por equipe NÃO implementadas. Frontend usa `user.role` global.
- ⚠️ Season visível como UUID, não como label legível.
- ⚠️ Adapter limpa nome concatenado com timestamp (bug conhecido do backend).

### 11.2. TODOs no Código

**DashboardV2.tsx:90**
```typescript
// TODO: Implementar endpoint /teams/{id}/leave
await teamsService.delete(teamId, 'Usuário saiu da equipe');
```

**useTeamPermissions.tsx:119**
```typescript
// TODO: Buscar papel específico na equipe via endpoint
// Por enquanto, usa papel global do usuário
```

**teams-v2-adapter.ts:38**
```typescript
// TODO: Integrar com sistema de permissões real quando disponível
```

---

## 12. FLUXOS COMPLETOS

### 12.1. Criar Equipe
1. User clica em "Criar equipe"
2. Modal abre com formulário
3. User preenche: nome, categoria, gênero
4. Frontend valida: nome >= 3 chars, categoria != '', gender != ''
5. Frontend envia POST /teams
6. Backend valida: name, category_id, gender
7. Backend cria Team com `organization_id` do token
8. Backend retorna Team criado (201)
9. Frontend fecha modal
10. Frontend redireciona para `/teams/{id}/members?isNew=true`
11. MembersTab detecta `?isNew=true` e mostra wizard

### 12.2. Convidar Membro (Sprint 3 - Hardening)
1. User clica em "Convidar membro"
2. Modal abre com formulário
3. User preenche: email, role
4. Frontend valida: email regex
5. Frontend envia POST /teams/{teamId}/invites
6. Backend valida:
   - Email válido
   - Equipe existe
   - Categoria da equipe existe
7. Backend verifica duplicidade:
   - Já é membro ativo? → 409 MEMBER_ACTIVE
   - Já tem convite pendente? → 409 INVITE_EXISTS
8. Backend verifica vínculos existentes:
   - Tem vínculo em equipe de gênero diferente? → 409 BINDING_CONFLICT
   - Tem vínculo em equipe de categoria superior/igual? → 409 BINDING_CONFLICT
9. Backend cria/atualiza:
   - Person (se não existir)
   - PersonContact (email)
   - User (status='inativo')
   - PasswordReset (token_type='welcome', 48h)
   - OrgMembership (role)
   - TeamMembership (status='pendente')
10. Backend envia email com token
11. Backend retorna 201 INVITE_SENT
12. Frontend fecha modal
13. Frontend exibe toast sucesso
14. Frontend revalida lista de convites pendentes

### 12.3. Completar Cadastro (Welcome Flow - Sprint 2 + Validação R15 - 14/01/2026)
1. User recebe email com link `/welcome?token=...`
2. User abre link
3. Frontend envia GET /auth/welcome/verify?token=...
4. Backend valida token:
   - Token existe? Token não usado? Token não expirado?
   - Se inválido → retorna erro (INVALID_TOKEN, TOKEN_EXPIRED, TOKEN_USED)
5. Backend retorna dados do convite (email, nome, role, etc)
6. Frontend renderiza formulário:
   - Step 1: Definir senha (min 8 chars)
   - Step 2: Completar perfil (**birth_date OBRIGATÓRIO** desde 14/01/2026)
     - Nome completo (obrigatório)
     - Data de nascimento (obrigatório)
     - Telefone (opcional)
     - Gênero (obrigatório)
7. User preenche e submete
8. Frontend envia POST /auth/welcome/complete
9. Backend:
   - Valida token novamente
   - **VALIDA CATEGORIA (R15 - 14/01/2026):**
     - Se role='atleta': calcula categoria natural (idade → categoria)
     - Compara com categoria da equipe
     - Se categoria natural > categoria equipe → BLOQUEIA (400 INVALID_CATEGORY)
     - Exemplo: atleta 21 anos (Júnior) NÃO pode entrar em equipe Infantil (max 14)
   - Define senha do usuário (bcrypt hash)
   - Atualiza Person com dados do formulário (birth_date obrigatório)
   - Cria Athlete se role='atleta'
   - Ativa TeamMembership (status='pendente' → 'ativo')
   - Marca token como usado (used_at=now())
   - Cria sessão (cookies HttpOnly)
10. Backend retorna 200 + cookies de sessão (ou 400 se validação falhar)
11. Frontend redireciona para `/teams/{teamId}/overview` (ou exibe erro de categoria)

---

## 4. COMPONENTES FRONTEND

### 4.1. StaffList Component
**Arquivo:** `src/components/teams-v2/StaffList.tsx`
**Localização:** Aba Members (`/teams/{id}/members`)

**Props:**
- `teamId: string` - ID da equipe
- `canManage: boolean` - Se usuário pode gerenciar staff (dirigente/coordenador)

**Funcionalidades:**
1. **Lista de Comissão Técnica:**
   - Busca staff via `GET /teams/{id}/staff?active_only=true`
   - Exibe cards com Avatar (w-9 h-9), nome, Badge de papel, data de início
   - Ações: Edit (Shield icon), Delete (Trash2 icon) - apenas se `canManage`
   - Estilos: hover:bg-slate-50, dark mode completo

2. **Banner "Sem Treinador":**
   - Condicional: `{!hasCoach && canManage}`
   - Alert amber com AlertCircle icon
   - Texto: "Equipe sem treinador. A equipe precisa de um treinador..."
   - Botão: "Adicionar Treinador" (bg-amber-600) → abre modal

3. **Modal de Remoção (AlertDialog):**
   - Mensagem condicional:
     - SE treinador: "⚠️ A equipe ficará SEM TREINADOR após esta ação." (text-amber-600)
     - SENÃO: "{nome} será removido da comissão técnica"
   - Ao confirmar: `DELETE /teams/{id}/staff/{membershipId}`
   - **Toast com ação** (Step 37.2):
     - SE `response.team_without_coach === true`:
       - Toast error com duration 7000ms
       - Action button: "Adicionar Novo Treinador"
       - onClick: abre modal de adicionar coach
     - SENÃO: toast simples de sucesso

4. **Modal "Adicionar Treinador" (Dialog):**
   - Busca coaches: `GET /org-memberships?role_id=3&active_only=true`
   - Select customizado:
     - Items com Avatar (w-6 h-6 bg-violet-100) + nome + email
     - Dropdown com scroll se muitos coaches
   - Separador "ou" com border-dashed
   - Botão: "Cadastrar Novo Treinador" (border-dashed)
     - Navega para `/organization/members?action=invite&role=treinador`
   - Ao submeter: `PATCH /teams/{id}/coach` (endpoint existente Step 18)
   - Sucesso: toast, fecha modal, `setHasCoach(true)`, recarrega lista

**TestIDs:**
- `staff-section` - Seção principal
- `staff-member-{id}` - Card de membro individual
- `staff-empty-state` - Empty state quando sem staff
- `add-coach-button` - Botão adicionar treinador no banner
- `remove-staff-dialog` - Modal de confirmação de remoção
- `add-coach-dialog` - Modal de adicionar treinador
- `coach-select` - Select de coaches disponíveis

### 4.2. OverviewTab - Banner Sem Coach
**Arquivo:** `src/components/teams-v2/OverviewTab.tsx`
**Localização:** Aba Overview (`/teams/{id}/overview`)

**Funcionalidade:**
- **Banner condicional** após seção "Membros Recentes"
- **Trigger:** `{!hasCoach && canManageTeam}`
- **Estado:** `hasCoach` detectado em `fetchTeamData()`:
  ```typescript
  const coachExists = staffResponse.items.some(
    m => m.role === 'treinador' && m.status === 'ativo'
  );
  setHasCoach(coachExists);
  ```

**Componentes:**
- Alert component (bg-amber-50 border-amber-200)
- AlertCircle icon (w-4 h-4 text-amber-600)
- Texto: "Equipe sem treinador" (font-semibold) + descrição
- Button "Adicionar" (px-3 py-1.5 bg-amber-600)
  - onClick: `router.push(/teams/${team.id}/members)`
  - Navega para aba Members onde StaffList permite adicionar coach

**TestIDs:**
- `no-coach-banner` - Banner principal
- `add-coach-redirect-btn` - Botão que redireciona

### 4.3. MembersTab - Integração StaffList
**Arquivo:** `src/components/teams-v2/MembersTab.tsx`

**Estrutura:**
```tsx
<section> {/* Comissão Técnica */}
  <header>
    <h2>Comissão Técnica & Gestão</h2>
    <button>Convidar membro</button>
  </header>
  <StaffList teamId={teamId} canManage={canManageMembers} />
</section>

<section> {/* Atletas */}
  {/* Tabela de atletas existente */}
</section>
```

**Separação:**
- Staff: Gerenciado por StaffList (Step 37)
- Atletas: Tabela existente com filtros
- Modais: InviteMemberModal, EditMemberRoleModal, RemoveMemberModal (já existentes)

---

## 5. FLUXOS DE UI

### 5.1. Fluxo: Remover Membro da Comissão Técnica
**Ator:** Dirigente ou Coordenador
**Local:** `/teams/{id}/members` → Seção "Comissão Técnica"

**Passos:**
1. User clica ícone Trash2 ao lado do membro
2. AlertDialog abre com mensagem condicional:
   - SE treinador: "⚠️ A equipe ficará SEM TREINADOR"
   - SENÃO: "{nome} será removido da comissão técnica"
3. User clica "Confirmar"
4. Frontend chama `DELETE /teams/{id}/staff/{membershipId}`
5. Backend:
   - SE treinador: `end_at=now(), status='inativo', team.coach_membership_id=NULL`
   - SENÃO: `deleted_at=now(), deleted_reason`
   - Retorna `{success: true, team_without_coach: boolean}`
6. Frontend:
   - SE `team_without_coach === true`:
     - Toast error: "Equipe sem treinador" (7000ms)
     - Action button: "Adicionar Novo Treinador"
     - onClick action: abre modal de adicionar coach
     - Banner amber aparece no topo da lista
   - SENÃO: Toast simples "Membro removido com sucesso"
7. Lista de staff atualiza automaticamente

### 5.2. Fluxo: Adicionar Treinador
**Ator:** Dirigente ou Coordenador
**Local:** `/teams/{id}/members` → Seção "Comissão Técnica"

**Trigger:**
- Clique no botão "Adicionar Treinador" no banner (se !hasCoach)
- OU clique na action do toast após remover coach

**Passos:**
1. Modal "Adicionar Treinador" abre
2. Frontend busca `GET /org-memberships?role_id=3&active_only=true`
3. Select popula com coaches disponíveis (avatar + nome + email)
4. User seleciona coach OU clica "Cadastrar Novo Treinador"
5. SE "Cadastrar Novo":
   - Navega para `/organization/members?action=invite&role=treinador`
6. SE seleciona coach existente:
   - User clica "Adicionar"
   - Frontend chama `PATCH /teams/{id}/coach`
   - Backend:
     - Encerra vínculo do coach antigo (se existir)
     - Cria novo TeamMembership
     - Atualiza `team.coach_membership_id`
     - Notifica ambos os coaches (antigo + novo)
   - Frontend:
     - Toast sucesso: "Treinador adicionado com sucesso"
     - Modal fecha
     - `setHasCoach(true)`
     - Banner desaparece
     - Lista de staff atualiza

### 5.3. Fluxo: Navegação do Banner (OverviewTab)
**Ator:** Dirigente ou Coordenador
**Local:** `/teams/{id}/overview`

**Trigger:** Equipe sem treinador (`hasCoach === false`)

**Passos:**
1. User acessa aba Overview
2. `fetchTeamData()` detecta `hasCoach === false`
3. Banner amber aparece após seção "Membros Recentes"
4. User clica botão "Adicionar"
5. `router.push(/teams/${team.id}/members)`
6. Aba Members abre com StaffList exibindo banner
7. User pode adicionar treinador via modal (fluxo 5.2)

---

## CHANGELOG

### [15 Jan 2026] - v1.5: Gestão completa de staff + banner sem coach
- ✅ **StaffList Component** implementado (Steps 37, 37.2, 38):
  - Lista completa de comissão técnica
  - Modal de remoção com aviso condicional para coaches
  - Toast com ação (7000ms) quando equipe fica sem treinador
  - Modal "Adicionar Treinador" com Select de coaches + opção cadastrar novo
  - Banner amarelo quando `!hasCoach`
- ✅ **OverviewTab Banner** implementado (Step 39):
  - Banner amber após seção "Membros Recentes"
  - Botão "Adicionar" que navega para aba Members
  - Estado `hasCoach` sincronizado com staff
- ✅ **Endpoints atualizados:**
  - `GET /teams/{id}/staff` - retorna TODOS os staff (ativos + pendentes)
  - `DELETE /teams/{id}/staff/{membershipId}` - remoção universal com lógica condicional
- ✅ **Schemas atualizados:**
  - `TeamStaffMember` - campos novos: status, resend_count, can_resend_invite, invite_token
- ✅ **Acessibilidade:**
  - Checklist completo criado: `docs/05-guias-procedimentos/ACCESSIBILITY_CHECKLIST.md`
  - WCAG 2.1 AA compliance
  - Keyboard navigation, ARIA labels, focus visible, dark mode
- ✅ **Documentação:**
  - Componentes frontend documentados
  - Fluxos de UI completos
  - TestIDs mapeados

### [14 Jan 2026] - v1.4: Validação categoria welcome + birth_date obrigatório
- ✅ **birth_date é OBRIGATÓRIO** no welcome flow (era opcional)
- ✅ **Validação R15** implementada no welcome/complete:
  - Calcula categoria natural do atleta baseado na birth_date
  - Compara com categoria da equipe (max_age)
  - Bloqueia se atleta for "velho demais" para a equipe
  - Exemplo: atleta 21 anos não pode entrar em equipe Infantil (max 14)
- ✅ Código de erro: `INVALID_CATEGORY` (400) com mensagem descritiva
- ✅ Implementado em: `app/api/v1/routers/auth.py` L1668-1720
- ✅ Função validadora: `athlete_validations.validate_birth_date_for_team()`
- ✅ Seeds atualizados: atleta E2E corrigido (21→14 anos), veterano adicionado (39 anos)
- ✅ Documentação: `VALIDACAO_CATEGORIA_WELCOME.md` criada

### [12 Jan 2026] - Atualização completa pós-integração teams_gaps
- ✅ Sincronizado com implementação real do backend (Python/FastAPI)
- ✅ Adicionados endpoints RESTful `/teams/{teamId}/invites` (Sprint 1)
- ✅ Documentados códigos de erro padronizados (Sprint 3)
- ✅ Validação de convites duplicados e binding conflicts (Sprint 3)
- ✅ Idempotência em resend de convites (Sprint 3)
- ✅ Welcome flow completo (Sprint 2)
- ✅ Atualizado RBAC com hierarquia
- ✅ Documentados todos endpoints com payloads e responses
- ✅ Mapeados modelos de dados do backend (Team, TeamMembership, TeamRegistration)
- ✅ Sincronizado middleware.ts com redirects e validações
- ✅ Documentadas limitações e TODOs conhecidos
- ✅ Adicionados fluxos completos (criar equipe, convidar membro, welcome flow)

---

**FIM DO CONTRATO**
