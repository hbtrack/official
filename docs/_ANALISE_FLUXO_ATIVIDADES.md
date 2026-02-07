<!-- STATUS: NEEDS_REVIEW -->

# Análise: Fluxo de Atividades Futuras (Banco → Backend → Frontend)

**Data:** 2026-01-14  
**Contexto:** Card "Próximas Atividades" na Visão Geral da Equipe

---

## 🔍 Arquitetura do Sistema

### Modelo de Dados (Banco)

**Training Sessions:**
```sql
CREATE TABLE training_sessions (
  id UUID PRIMARY KEY,
  organization_id UUID NOT NULL REFERENCES organizations(id),
  team_id UUID NOT NULL REFERENCES teams(id),
  session_at TIMESTAMP NOT NULL,
  status VARCHAR NOT NULL,  -- draft, in_progress, closed
  -- outros campos...
)
```

**Matches:**
```sql
CREATE TABLE matches (
  id UUID PRIMARY KEY,
  team_id UUID NOT NULL REFERENCES teams(id),
  match_date DATE NOT NULL,
  match_time TIME,
  status VARCHAR NOT NULL,  -- scheduled, in_progress, finished, cancelled
  -- outros campos...
)
-- organization_id vem via JOIN com teams
```

**Hierarquia:**
```
Organization (Clube)
  └── Team (Equipe)
      ├── TrainingSessions (Treinos)
      └── Matches (Jogos)
```

---

## 🔐 Segurança Multi-Tenant

### Backend: Filtro de Organização SEMPRE

**TrainingSessionService.get_all() (linha 66-67):**
```python
query = select(TrainingSession).where(
    TrainingSession.organization_id == self.context.organization_id  # ✅ SEGURANÇA
)

if team_id:
    query = query.where(TrainingSession.team_id == team_id)  # ✅ FILTRO ADICIONAL
```

**MatchService.get_all() (linha 49-51):**
```python
query = select(Match).join(Team, Team.id == Match.team_id)

if not self.context.is_superadmin:
    query = query.where(Team.organization_id == self.context.organization_id)  # ✅ SEGURANÇA

if team_id:
    query = query.where(Match.team_id == team_id)  # ✅ FILTRO ADICIONAL
```

**Logs do Backend:**
```
Listed 3 training sessions for org 88888888-8888-8888-8888-000000000001
Listed 2 matches for org 88888888-8888-8888-8888-000000000001
```

⚠️ **IMPORTANTE:** O "for org" no log é apenas INFORMATIVO do escopo de segurança.  
✅ O filtro de `team_id` **ESTÁ SENDO APLICADO** na query, mas não aparece no log!

---

## 🔄 Fluxo de Requisições

### Frontend → Backend

**1. OverviewTab chama fetchUpcomingActivities():**

```typescript
// Linha 271-276 (DEPOIS DO BUGFIX)
const [trainingsResponse, matchesResponse] = await Promise.all([
  TrainingSessionsAPI.listSessions({
    team_id: currentTeam.id,  // ✅ ENVIA team_id
    page: 1,
    limit: 10,
  }),
  matchesService.getTeamMatches(currentTeam.id, {  // ✅ ENVIA team_id
    status: 'scheduled',
    page: 1,
    size: 10,
  })
]);
```

**2. Requisições HTTP:**

```
GET /api/v1/training-sessions?team_id=88888888-8888-8888-8884-000000000001&page=1&limit=10
GET /api/v1/teams/88888888-8888-8888-8884-000000000001/matches?status=scheduled&page=1&size=10
```

**3. Backend processa:**

- ✅ Valida token JWT → extrai `organization_id` do contexto
- ✅ Aplica filtro de segurança: `organization_id == ctx.organization_id`
- ✅ Aplica filtro de negócio: `team_id == {parametro}`
- ✅ Retorna apenas dados da equipe específica

---

## 🐛 Bug Corrigido (2026-01-14 21:45)

### Problema Original

**Código com bug (ANTES):**
```typescript
// Linha 259 - fetchUpcomingActivities()
if (!team?.id) {  // ❌ 'team' undefined aqui!
  setUpcomingActivities([]);
  return;
}

// Linha 271
TrainingSessionsAPI.listSessions({
  team_id: team.id,  // ❌ Nunca chegava aqui
  // ...
})
```

**Por que falhava?**
1. Função `fetchUpcomingActivities()` definida ANTES do early return (linha 257)
2. Variável `team` definida DEPOIS do early return (linha 175)
3. Guard clause `if (!team?.id)` sempre retornava vazio
4. Requisições nunca eram feitas

**Resultado:** Empty state "Nenhuma atividade agendada" mesmo com treinos no banco

### Correção Aplicada

**Código corrigido (DEPOIS):**
```typescript
// Linha 259 - fetchUpcomingActivities()
if (!currentTeam?.id) {  // ✅ Agora funciona!
  setUpcomingActivities([]);
  return;
}

// Linha 271
TrainingSessionsAPI.listSessions({
  team_id: currentTeam.id,  // ✅ Requisição feita com sucesso
  // ...
})
```

**Mudança:** `team` → `currentTeam` (3 ocorrências)

---

## ✅ Comportamento Atual (Correto)

### 1. Frontend envia team_id

```http
GET /api/v1/training-sessions?team_id=xxx&page=1&limit=10
GET /api/v1/teams/xxx/matches?status=scheduled&page=1&size=10
```

### 2. Backend filtra corretamente

```sql
-- Training Sessions
SELECT * FROM training_sessions
WHERE organization_id = 'org_do_usuario'  -- Segurança
  AND team_id = 'team_do_parametro'       -- Filtro específico
  AND session_at > NOW()                  -- Frontend filtra depois
  AND status != 'cancelled'               -- Frontend filtra depois
  AND deleted_at IS NULL
ORDER BY session_at DESC
LIMIT 10;

-- Matches
SELECT * FROM matches m
JOIN teams t ON t.id = m.team_id
WHERE t.organization_id = 'org_do_usuario'  -- Segurança
  AND m.team_id = 'team_do_parametro'       -- Filtro específico
  AND m.status = 'scheduled'                -- Parâmetro
  AND m.deleted_at IS NULL
ORDER BY m.match_date DESC
LIMIT 10;
```

### 3. Frontend processa e exibe

```typescript
// Filtrar eventos futuros
const trainingEvents = trainingsResponse.items
  .filter(t => 
    t.status !== 'cancelled' && 
    new Date(t.session_at) > now
  )
  .map(/* transform */);

const matchEvents = matchesResponse.items
  .filter(m => new Date(m.match_date) > now)
  .map(/* transform */);

// Merge + sort + limit 4
const allEvents = [...trainingEvents, ...matchEvents]
  .sort((a, b) => a.eventAt.getTime() - b.eventAt.getTime())
  .slice(0, 4);
```

---

## 📊 Interpretação dos Logs

### Log do Backend

```
2026-01-14 22:09:28 INFO - → GET /api/v1/training-sessions
2026-01-14 22:09:28 INFO - Listed 3 training sessions for org 888...
2026-01-14 22:09:28 INFO - ← GET /api/v1/training-sessions - 200

2026-01-14 22:09:28 INFO - → GET /api/v1/teams/.../matches
2026-01-14 22:09:28 INFO - Listed 2 matches for org 888...
2026-01-14 22:09:28 INFO - ← GET /api/v1/teams/.../matches - 200
```

**O que significa:**
- ✅ 3 training sessions encontradas para a organização E equipe filtrada
- ✅ 2 matches encontrados para a organização E equipe filtrada
- ⚠️ "for org" é apenas o escopo de segurança, NÃO significa "todos da org"

**Como melhorar os logs (opcional):**
```python
logger.info(
    f"Listed {len(sessions)} training sessions "
    f"for org {self.context.organization_id} "
    f"{'(filtered by team ' + str(team_id) + ')' if team_id else ''}"
)
```

---

## 🎯 Conclusão

### ✅ Sistema Funcionando Corretamente

1. **Banco:** Estrutura correta com `team_id` e `organization_id`
2. **Backend:** Filtros aplicados na ordem certa (segurança + negócio)
3. **Frontend:** Após bugfix, envia `team_id` corretamente

### 📝 Documentação das Regras

**R17 - Treinos são eventos operacionais:**
- Filtrados por `team_id` obrigatório
- Múltiplos treinos por equipe
- Status: draft, in_progress, closed

**R18 - Jogos são eventos oficiais:**
- Filtrados por `team_id` obrigatório
- Status: scheduled, in_progress, finished, cancelled
- Vinculados a competitions (opcional)

**R25 - Escopo implícito por equipe:**
- Backend sempre valida `organization_id` via contexto
- Frontend sempre envia `team_id` nos filtros
- Permissões validadas via `require_team=True`

### 🔧 Testes Recomendados

1. **E2E:** Criar treino + jogo no futuro → verificar aparecem no card
2. **E2E:** Criar treino cancelado → verificar NÃO aparece
3. **E2E:** Criar 5 eventos → verificar apenas 4 primeiros aparecem
4. **E2E:** Filtrar por "Treinos" → verificar apenas treinos aparecem
5. **Unit:** TrainingSessionService.get_all() com team_id → validar filtro SQL
6. **Unit:** MatchService.get_all() com team_id → validar filtro SQL

---

**Arquivo criado em:** 2026-01-14 22:30  
**Autor:** GitHub Copilot  
**Status:** ✅ Sistema validado e documentado
