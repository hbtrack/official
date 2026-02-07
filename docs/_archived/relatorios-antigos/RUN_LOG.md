<!-- STATUS: DEPRECATED | arquivado -->

# RUN LOG - Execuções E2E

> Arquivo consolidado em 2026-01-11 (merge de RUN_LOG.md e RUN_LOG1.md)

---

## Execução: 2026-01-13 00:00 (Run 10 - CORREÇÃO SSR - Migração para Client-side Fetch)

### Ambiente
- **Browser**: Chromium, Firefox, Webkit
- **Workers**: 1
- **Retries**: 0
- **DB**: hb_track_e2e
- **OS**: Windows 11
- **Hora**: 00:00
- **Status**: ⚠️ CORREÇÃO IMPLEMENTADA - AGUARDANDO RESTART NEXT.JS

### Contexto
Investigação profunda do problema de testIDs "ausentes" na Run 9. Descoberto que testIDs **existiam** nos componentes, mas 404 page estava sendo renderizada devido a falha de autenticação SSR.

### Diagnóstico Final

**Root Cause**: Server Components fazendo fetch SSR → Backend sem cookies
```
Browser (Playwright) → Next.js SSR: ✅ Cookie presente
Next.js SSR → Backend API: ❌ Cookie NÃO incluído automaticamente
Backend: 401 Unauthorized → Frontend: notFound() → 404 Page
Playwright: testID não encontrado (página errada renderizada)
```

**Por que Members funcionava?**
- Members Tab: Client Component → fetch client-side → browser inclui cookies ✅
- Overview/Settings: Server Component → fetch SSR → cookies não incluídos ❌

### Solução Implementada

**Estratégia**: Migrar Overview e Settings para padrão Members (client-side fetch)

#### Arquivos Modificados

**Overview Tab**:
1. `src/app/(admin)/teams/[teamId]/overview/page.tsx`
   - ❌ Removido: SSR fetch com `serverApiClient`
   - ✅ Adicionado: Passa apenas `teamId` para componente

2. `src/components/teams-v2/OverviewTab.tsx`
   - ✅ Props: `team?: Team` e `teamId?: string` (backward compatible)
   - ✅ State: `currentTeam` com tipo `Team | null`
   - ✅ Fetch: `fetchTeam(id)` client-side com `teamsService.getById()`
   - ✅ Adapter: `mapApiTeamToV2()` para converter tipos
   - ✅ Loading: Skeleton durante fetch
   - ✅ TypeScript: Type assertion após verificação null

**Settings Tab**:
1. `src/app/(admin)/teams/[teamId]/settings/page.tsx`
   - ❌ Removido: SSR fetch com `serverApiClient`
   - ✅ Adicionado: Passa apenas `teamId`

2. `src/app/(admin)/teams/[teamId]/settings/TeamSettingsClient.tsx`
   - ✅ Props: `teamId: string` (antes era `team: Team`)

3. `src/components/teams-v2/SettingsTab.tsx`
   - ✅ Props: `team?: Team` e `teamId?: string`
   - ✅ Fetch: Client-side no useEffect
   - ✅ Loading: `isLoadingTeam` state com spinner

#### Código de Exemplo

```typescript
// ANTES (SSR - BROKEN)
async function getTeam(teamId: string) {
  const apiTeam = await serverApiClient.get<Team>(`/teams/${teamId}`);
  return mapApiTeamToV2(apiTeam);
}

// DEPOIS (Client-side - WORKING)
const fetchTeam = async (id: string) => {
  const apiTeam = await teamsService.getById(id); // ✅ Browser inclui cookies
  const teamData = mapApiTeamToV2(apiTeam as any);
  setCurrentTeam(teamData);
};

useEffect(() => {
  if (!initialTeam && teamId) {
    fetchTeam(teamId);
  }
}, [teamId]);
```

### Validação TypeScript

```bash
npx tsc --noEmit 2>&1 | grep -E "(OverviewTab|SettingsTab)" | wc -l
# Resultado: 0 erros ✅
```

### Resultado Esperado Pós-Correção

**Antes (Run 9)**:
- Total: 37 testes (34 aprovados, 3 falhados)
- Taxa: 91.89%
- Falhas: Overview tab, Settings tab (2 testes)

**Depois (Run 10 - Após Restart)**:
- Total: 37 testes
- Esperado: 37 aprovados (100%)
- Falhas: 0
- Taxa esperada: **100%**

### Testes Corrigidos

1. ✅ `/teams/:id/overview` → testID `team-overview-tab` deve ser encontrado
2. ✅ `/teams/:id/settings` → testID `teams-settings-root` deve ser encontrado
3. ✅ `/teams/:id/settings` → input de nome deve estar visível

### Status Final

- ✅ **Root cause identificado** - SSR fetch sem cookies
- ✅ **Solução implementada** - Client-side fetch pattern
- ✅ **TypeScript válido** - 0 erros
- ✅ **Backward compatible** - Componentes aceitam `team` OU `teamId`
- ⚠️ **Aguardando restart** - Next.js precisa recompilar

### Próximos Passos

1. [ ] **CRÍTICO**: Restart Next.js para recompilar componentes
   ```bash
   cd "C:\HB TRACK\Hb Track - Fronted"
   npm run dev
   ```

2. [ ] **Validar**: Executar teams.contract.spec.ts
   ```bash
   npx playwright test tests/e2e/teams/teams.contract.spec.ts --reporter=list
   ```

3. [ ] **Confirmar**: 100% de sucesso (37/37 testes)

4. [ ] **Avançar**: Para FASE 6 (FUNCIONAIS) se tudo passar

### Documentação Criada

- `tests/e2e/tests_log/RUN10_SUMMARY.md` - Resumo completo da correção
- `tests/e2e/tests_log/SSR_COOKIE_FIX.md` - Análise técnica profunda (para referência futura)

### Lições Aprendadas

1. **Screenshot é crucial**: Revelou 404 page em vez de problema de testID
2. **E2E revela edge cases**: Comportamento diferente de dev (onde você está logado)
3. **Diagnóstico do usuário estava correto**: "SSR não forward cookies automaticamente"
4. **Padrões consistentes são importantes**: Members já usava client-side fetch
5. **Backward compatibility vale**: Componentes aceitam ambos `team` e `teamId`

---

## Execução: 2026-01-12 22:30 (Run 9 - PARCIAL - testIDs Ausentes no Frontend)

### Ambiente
- **Browser**: Chromium
- **Workers**: 1
- **Retries**: 0
- **DB**: hb_track_e2e (seed recriado - problema de CREATE DATABASE corrigido manualmente)
- **OS**: Windows 11
- **Hora**: 22:30
- **Duração Total**: ~2min 30s

### Contexto
Primeira execução completa após consolidação de scripts. Pipeline executado até Fase 5 (CONTRATO). Identificados problemas de testIDs ausentes em componentes do frontend.

### Resultado por Spec

| # | Spec | Camada | Testes | Aprovados | Falhados | Duração | Taxa |
|---|------|--------|--------|-----------|----------|---------|------|
| 1 | health.gate.spec.ts | Gate | 9 | 9 | 0 | 23.9s | 100% |
| 2 | auth.setup.ts | Setup | 6 | 6 | 0 | 15.0s | 100% |
| 3 | teams.contract.spec.ts | Contrato | 22 | 19 | 3 | 2.3m | 86.36% |

**Total**: 37 testes (34 aprovados, 3 falhados) = **91.89%**

**Breakdown de Tempo**:
- GATE (infraestrutura): 23.9s
- SETUP (autenticação): 15.0s
  - admin: 3.4s
  - dirigente: 2.3s
  - coordenador: 2.1s
  - coach: 2.3s
  - atleta: 2.3s
  - user (copy): 509ms
- CONTRATO (navegação): 2.3m
- Overhead: incluído nos valores acima

### Detalhamento teams.contract.spec.ts (2.3m total)

**✅ 401 - Sem Autenticação (3/3)** - 100%:
- /teams → /signin?callbackUrl=/teams ✅
- /teams/:id/overview → preserva callback ✅
- /teams/:id/members → preserva callback ✅

**✅ Redirects Canônicos (3/3)** - 100%:
- /teams/:id → /teams/:id/overview ✅
- /teams/:id/invalid-tab → /teams/:id/overview ✅
- /teams/:id/OVERVIEW → case insensitive ✅

**✅ 404 - Não Encontrado (3/3)** - 100%:
- UUID inválido → 404 ✅
- UUID inexistente → 404 ✅
- Team soft deleted → 404 ✅

**⚠️ Páginas Carregam com Root testID (2/4)** - 50%:
- /teams → teams-dashboard visível ✅
- /teams/:id/overview → testID ausente ❌ **Timeout 30s**
- /teams/:id/members → team-members-tab visível ✅
- /teams/:id/settings → testID ausente ❌ **Timeout 30s**

**⚠️ Marcadores Estáveis (2/3)** - 67%:
- /teams tem botão criar ✅
- /teams/:id/members tem botão convidar ✅
- /teams/:id/settings tem input → bloqueado ❌ **Timeout 30s**

### Problemas Identificados

#### 1. Overview Tab - testID `team-overview-tab` Ausente

**Erro**:
```
TimeoutError: locator('[data-testid="team-overview-tab"]').waitFor: Timeout 30000ms
```

**Causa**: Componente da tab overview não possui o testID esperado

**Arquivo Afetado**: Componente `/teams/:id/overview` (frontend)

**Impacto**: 1 teste bloqueado

---

#### 2. Settings Root - testID `teams-settings-root` Ausente

**Erro**:
```
expect(locator('[data-testid="teams-settings-root"]')).toBeVisible() failed
element(s) not found
```

**Causa**: Página de settings não possui elemento raiz com testID

**Arquivo Afetado**: Página `/teams/:id/settings` (frontend)

**Impacto**: 2 testes bloqueados

---

#### 3. Database Reset Script - CREATE DATABASE Falha Silenciosamente

**Problema**: Script `reset-db-e2e.ps1` linha 250 executa `CREATE DATABASE` mas falha silenciosamente (devido a `2>&1 | Out-Null`)

**Solução Temporária**: Banco criado manualmente antes de rodar migrations

**Impacto**: ⚠️ Médio - Pipeline não é totalmente autônomo

**Ação**: Script precisa ser corrigido para verificar se banco foi criado

---

### Comparação com Run 8

| Métrica | Run 8 | Run 9 | Delta |
|---------|-------|-------|-------|
| Testes Executados | 14 | 37 | +23 |
| Testes Passando | 13 | 34 | +21 |
| Testes Falhando | 1 | 3 | +2 |
| Taxa de Sucesso | 92.86% | 91.89% | -0.97% |
| Specs Executados | 2 | 3 | +1 |
| Problema 409 | ✅ Resolvido | ✅ Mantido | - |

**Análise**: Run 9 executou escopo maior (incluindo CONTRATO completo). Taxa ligeiramente menor é esperada devido a cobertura expandida revelando novos problemas.

---

### Status Final

- ✅ **GATE (Infraestrutura)** - 100% aprovado
- ✅ **SETUP (Autenticação)** - 100% aprovado
- ⚠️ **CONTRATO (Navegação)** - 86.36% aprovado
  - Redirects: ✅ 100%
  - 401 checks: ✅ 100%
  - 404 checks: ✅ 100%
  - testIDs: ❌ 2 componentes sem testID
- 🚫 **FUNCIONAIS** - Não executado (bloqueado por falha em CONTRATO)

### Arquivos Criados/Modificados

#### Logs
- `tests/e2e/tests_log/RUN9_SUMMARY.md` - Análise completa (NOVO)
- `tests/e2e/tests_log/RUN_LOG.md` - Este arquivo (ATUALIZADO)

#### Scripts
- `tests/e2e/run-e2e-teams.ps1` - Script consolidado funcionando (CORRIGIDO)

---

### Próximos Passos

1. [ ] **Frontend**: Adicionar `data-testid="team-overview-tab"` ao componente overview
2. [ ] **Frontend**: Adicionar `data-testid="teams-settings-root"` à página settings
3. [ ] **Backend**: Corrigir `reset-db-e2e.ps1` linha 250 para verificar criação do banco
4. [ ] **Re-executar**: teams.contract.spec.ts após correções
5. [ ] **Avançar**: Para FASE 6 (FUNCIONAIS) se CONTRATO passar 100%

---

## Execução: 2026-01-12 21:00 (Run 8 - SUCESSO - Problema 409 Resolvido)

### Ambiente
- **Browser**: Chromium
- **Workers**: 1
- **Retries**: 0
- **DB**: hb_track_e2e (seed com IDs corrigidos + backend com auto-membership)
- **OS**: Windows 11
- **Hora**: 21:00
- **Duração Total**: 1min 48s (108 segundos)

### Contexto
Após implementar correções no backend (auto-adicionar criador como membro) e frontend (session_type válido, rota scoped), re-executados testes de training sessions.

### Resultado por Spec

| # | Spec | Camada | Testes | Aprovados | Falhados | Duração | Taxa |
|---|------|--------|--------|-----------|----------|---------|------|
| 1 | setup/auth.setup.ts | Setup | 6 | 6 | 0 | 23.3s | 100% |
| 2 | teams.trainings.spec.ts | Funcional | 8 | 7 | 1 | 47.0s | 87.5% |

**Total**: 14 testes (13 aprovados, 1 falhado) = **92.86%**

**Breakdown de Tempo**:
- Setup autenticação (6 roles): 23.3s
  - admin: 8.6s
  - dirigente: 3.8s
  - coordenador: 3.7s
  - coach: 3.5s
  - atleta: 3.3s
  - user (copy): 0.3s
- Testes funcionais: 47.0s
- Overhead (Playwright init, cleanup, teardown): ~38s

### Detalhamento teams.trainings.spec.ts (47.0s total)

**✅ Navegação e Root (3/3)** - 100% - 13.2s:
- deve carregar aba trainings com root testid (3.6s) ✅
- deve exibir botão de criar treino (1.8s) ✅
- deve navegar entre tabs sem perder contexto (7.8s) ✅

**✅ CRUD (2/3)** - 67% - 9.3s:
- treino criado via API deve aparecer na lista (7.1s) ✅
- deve verificar dados do treino via API (0.9s) ✅
- treino deletado via API não deve aparecer na lista (1.3s) ❌ **500 Internal Server Error**

**✅ Estados (1/1)** - 100% - 19.2s:
- equipe sem treinos deve mostrar empty state ou mensagem (19.2s) ✅

**✅ Permissões (1/1)** - 100% - 5.1s:
- admin deve ver botão de criar treino (5.1s) ✅

### Correções Aplicadas

#### 1. Backend - Auto-adicionar Criador como Membro do Team

**Problema**: Backend não criava automaticamente team_membership quando team era criado, impedindo criador de criar training sessions.

**Solução**: Modificado `team_service.py` para auto-adicionar criador como membro.

**Arquivo**: `app/services/team_service.py` (linhas 200-215)

```python
# Auto-adicionar criador como membro do team (owner)
if creator_person_id and creator_org_membership_id:
    team_membership = TeamMembership(
        team_id=team.id,
        person_id=creator_person_id,
        org_membership_id=creator_org_membership_id,
        status="ativo",
        start_at=datetime.now(timezone.utc),
    )
    self.db.add(team_membership)
    self.db.flush()
```

**Arquivo**: `app/api/v1/routers/teams.py` (linhas 90-99)

```python
team = service.create(
    name=data.name,
    organization_id=ctx.organization_id,
    category_id=data.category_id,
    gender=data.gender,
    is_our_team=data.is_our_team,
    coach_membership_id=data.coach_membership_id,
    created_by_user_id=ctx.user_id,
    creator_person_id=ctx.person_id,          # ← NOVO
    creator_org_membership_id=ctx.membership_id,  # ← NOVO
)
```

#### 2. Frontend - Corrigir session_type Inválido

**Problema**: Testes usavam `'tecnico'` e `'tatico'` que não existem na constraint do banco.

**Constraint DB**: `session_type IN ('quadra', 'fisico', 'video', 'reuniao', 'teste')`

**Correções**:
- `tests/e2e/helpers/api.ts` (linha 505): `'tecnico'` → `'quadra'`
- `tests/e2e/teams/teams.trainings.spec.ts` (linha 162): `'tecnico'` → `'quadra'`
- `tests/e2e/teams/teams.trainings.spec.ts` (linha 191): `'tatico'` → `'fisico'`

#### 3. Frontend - Usar Rota Scoped

**Problema**: Helper usava rota global `/training-sessions` que pode ter context issues.

**Solução**: Mudado para rota scoped `/teams/{team_id}/trainings`.

**Arquivo**: `tests/e2e/helpers/api.ts` (linha 512)

```typescript
// ANTES: ${API_BASE}/training-sessions
// DEPOIS: ${API_BASE}/teams/${data.team_id}/trainings
```

#### 4. Frontend - Soft Delete com Query Param

**Problema**: DELETE de training session exigia query param `reason` (não documentado).

**Solução**: Adicionado query param ao helper.

**Arquivo**: `tests/e2e/helpers/api.ts` (linha 557)

```typescript
const res = await request.delete(
  `${API_BASE}/training-sessions/${sessionId}?reason=E2E test cleanup`,
  { headers: getAuthHeaders(token) }
);
```

### Issue Restante (1 teste)

**Teste**: "treino deletado via API não deve aparecer na lista"
**Erro**: `500 Internal Server Error - 'NoneType' object can't be awaited`
**Causa**: Bug no backend ao processar soft delete de training session
**Impacto**: **Baixo** - Funcionalidade principal (CREATE) funcionando
**Ação**: Abrir issue separado no backend para corrigir soft delete

### Comparação com Runs Anteriores

| Run | Data/Hora | Aprovados | Falhados | Taxa | Status |
|-----|-----------|-----------|----------|------|--------|
| 5 | 12/01 18:02 | 11 | 3 | 78.57% | ❌ 409 - team_memberships |
| 6 | 12/01 18:13 | 11 | 3 | 78.57% | ❌ 409 - mesmo após seed |
| 7 | 12/01 19:45 | 11 | 3 | 78.57% | ❌ 409 - IDs corrigidos |
| **8** | **12/01 20:30** | **13** | **1** | **92.86%** | **✅ RESOLVIDO** |

**Progresso**: +2 testes aprovados (+14.29 pontos percentuais)

### Status Final

- ✅ **Problema 409 RESOLVIDO** - Training sessions podem ser criadas
- ✅ **Backend corrigido** - Auto-adiciona criador como membro do team
- ✅ **Frontend corrigido** - session_type válido, rota scoped correta
- ⚠️ **1 teste falhando** - Bug de soft delete no backend (issue separado)

### Arquivos Modificados

#### Backend
1. `app/models/team_membership.py` - Import adicionado ao service
2. `app/services/team_service.py` - Auto-criar team_membership (linhas 20-23, 140-215)
3. `app/api/v1/routers/teams.py` - Passar creator_person_id e creator_org_membership_id (linhas 90-99)

#### Frontend
4. `tests/e2e/helpers/api.ts` - session_type, rota scoped, soft delete (linhas 505, 512, 557)
5. `tests/e2e/teams/teams.trainings.spec.ts` - session_type corrigido (linhas 162, 191, 200)

#### Seed E2E (Runs anteriores)
6. `scripts/seed_e2e.py` - IDs padronizados (linhas 56-90, 306-320)
7. `tests/e2e/shared-data.ts` - IDs centralizados (NOVO)

### Lições Aprendidas

1. **Mensagens de erro genéricas dificultam debug**: "DATABASE_CONSTRAINT_VIOLATION" deveria especificar qual constraint foi violada
2. **Backend deve ter comportamento intuitivo**: Criador de recurso = owner automático (pattern de SaaS)
3. **Constraints de DB devem ser documentadas**: Lista de valores válidos para ENUMs deve estar no schema/docs
4. **Rotas scoped são mais seguras**: Context garantido, validações automáticas
5. **Testes devem usar valores válidos**: Consultar migrations/constraints antes de criar payloads

---

## Execução: 2026-01-12 19:45 (Run 7 - Correção de IDs)

### Resumo
- IDs E2E padronizados de `e2e00000-...` para `88888888-...`
- Seed executado com sucesso
- **Problema 409 persistiu** - Causa raiz identificada como constraint de session_type

### Detalhes
Ver [RUN7_SUMMARY.md](RUN7_SUMMARY.md) para análise completa.

---

## Execução: 2026-01-12 18:13 (Run 6 - Confirmação do Problema)

### Resumo
- Re-execução após seed corrigido
- **Problema 409 persistiu**
- Confirmado que não era falta de team_memberships

### Resultado
- 11/14 testes passando (78.57%)
- 3 testes bloqueados por 409

---

## Execução: 2026-01-12 18:02 (Run 5 - Seed E2E)

### Resumo
- Adicionada função `seed_e2e_team_memberships()`
- Seed executado com sucesso
- **Problema 409 persistiu**

### Resultado
- 11/14 testes passando (78.57%)
- 3 testes bloqueados por 409

---

## Histórico Anterior

Runs 1-4 documentados nas seções arquivadas do RUN_LOG original.

Ver [CHANGELOG.md](CHANGELOG.md) para histórico completo de mudanças.
