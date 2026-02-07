<!-- STATUS: DEPRECATED | arquivado -->

# Run 7 - Resumo Executivo

**Data**: 2026-01-12 19:45
**Status**: ✅ CAUSA RAIZ IDENTIFICADA - Solução Pronta

---

## Resumo

Após corrigir IDs no seed E2E (de `e2e00000-...` para `88888888-...`), re-executados testes de training sessions. **Problema 409 persiste** mas agora a **causa raiz real foi identificada**.

---

## Correções Aplicadas

### 1. IDs E2E Padronizados

**Problema**: Mismatch entre IDs do seed (`e2e00000-...`) e esperados pelos testes (`88888888-...`)

**Solução**: Migrados todos os IDs para padrão `88888888-8888-8888-XXXX-YYYYYYYYYY`

| Recurso | ID Antigo | ID Novo | Sufixo |
|---------|-----------|---------|--------|
| Organization | `e2e00000-0000-0000-0000-000000000001` | `88888888-8888-8888-8888-000000000001` | 8888 |
| Team Base | `e2e00000-0000-0000-0004-000000000001` | `88888888-8888-8888-8884-000000000001` | 8884 |
| Pessoas | `e2e00000-0000-0000-0001-00000000000X` | `88888888-8888-8888-8881-00000000000X` | 8881 |
| Usuários | `e2e00000-0000-0000-0002-00000000000X` | `88888888-8888-8888-8882-00000000000X` | 8882 |
| Org Memberships | `e2e00000-0000-0000-0003-00000000000X` | `88888888-8888-8888-8883-00000000000X` | 8883 |

**Arquivo**: [scripts/seed_e2e.py](c:\HB TRACK\Hb Track - Backend\scripts\seed_e2e.py#L56-L90)

### 2. Seed E2E Idempotente

**Problema**: Re-executar seed falhava com "duplicate key" ou "unique violation"

**Solução**: Adicionado `ON CONFLICT DO UPDATE` nos inserts:

```python
INSERT INTO users (id, person_id, email, password_hash, ...)
VALUES (%s, %s, %s, %s, ...)
ON CONFLICT (id) DO UPDATE SET
    email = EXCLUDED.email,
    password_hash = EXCLUDED.password_hash,
    deleted_at = NULL  # Reativa usuários soft-deleted
```

**Arquivo**: [scripts/seed_e2e.py](c:\HB TRACK\Hb Track - Backend\scripts\seed_e2e.py#L306-L320)

### 3. Shared Data Centralizado

**Problema**: IDs hardcoded espalhados por vários arquivos de teste

**Solução**: Criado arquivo centralizado com todos os IDs E2E

**Arquivo**: [tests/e2e/shared-data.ts](c:\HB TRACK\Hb Track - Fronted\tests\e2e\shared-data.ts) (NOVO)

Benefícios:
- ✅ Sincronizado com seed_e2e.py
- ✅ Documentação clara do padrão de IDs
- ✅ Manutenção futura simplificada

---

## Resultados dos Testes

| Spec | Testes | Aprovados | Falhados | Taxa |
|------|--------|-----------|----------|------|
| setup/auth.setup.ts | 6 | 6 | 0 | 100% |
| teams.trainings.spec.ts | 8 | 5 | 3 | 62.5% |
| **TOTAL** | **14** | **11** | **3** | **78.57%** |

### Detalhamento teams.trainings.spec.ts

**✅ Navegação (3/3)** - 100%
**❌ CRUD (0/3)** - 0% (bloqueado por 409)
**✅ Estados (1/1)** - 100%
**✅ Permissões (1/1)** - 100%

---

## Causa Raiz Real - IDENTIFICADA

### Descoberta

Os testes de training sessions **NÃO usam team base do seed**. Cada teste cria seu próprio team via API:

```typescript
test.beforeAll(async ({ request }) => {
  teamId = await createTeamViaAPI(request, { name: 'E2E-Gap-TrainCRUD-...' });
});
```

### Fluxo do Erro 409

```
1. Teste cria team
   POST /teams { name: "E2E-Gap-TrainCRUD-abc123" }
   → Backend cria team (ID: xyz)
   → Backend NÃO cria team_membership automaticamente

2. Teste tenta criar training session
   POST /training-sessions { team_id: xyz, ... }

3. Backend valida permissões
   SELECT * FROM team_memberships WHERE team_id = xyz AND person_id = admin_e2e
   → Resultado: VAZIO (usuário NÃO é membro)

4. Backend rejeita
   → 409 DATABASE_CONSTRAINT_VIOLATION
```

### Causa Raiz

**Backend não cria automaticamente o team_membership quando um team é criado.**

O criador do team não se torna automaticamente membro/owner do team.

### Por Que Não Descobrimos Antes?

1. **Seed manual funcionaria**: Se testássemos com team base do seed (que tem memberships), passaria
2. **Teams via API falham**: Tests criam teams dinamicamente → sem memberships → 409
3. **Erro genérico**: Mensagem "DATABASE_CONSTRAINT_VIOLATION" não indicava qual constraint

---

## Soluções Propostas

### ✅ Opção 1: Backend Auto-Adicionar Criador (RECOMENDADO)

**Comportamento Esperado**: Quando um usuário cria um team, ele automaticamente se torna owner/admin desse team.

**Implementação no Backend**:

```python
# app/services/team_service.py - Método create()

async def create(self, data: TeamCreateSchema) -> Team:
    # Criar team
    team = await super().create(data)

    # Auto-adicionar criador como membro do team
    team_membership = TeamMembershipCreate(
        team_id=team.id,
        person_id=self.context.person_id,
        org_membership_id=self.context.membership_id,
        status='ativo'
    )
    await self.team_membership_service.create(team_membership)

    return team
```

**Vantagens**:
- ✅ Comportamento intuitivo e esperado
- ✅ Alinhado com padrões de SaaS (creator = owner)
- ✅ Testes passam sem workarounds
- ✅ Produção funciona corretamente

**Desvantagens**:
- Requer mudança no backend (1 arquivo, ~10 linhas)

---

### ⚠️ Opção 2: Helper createTeamViaAPI Adicionar Membership

**Workaround nos Testes**: Após criar team via API, adicionar criador como membro.

**Implementação no Frontend**:

```typescript
// tests/e2e/helpers/api.ts

export async function createTeamViaAPI(
  request: APIRequestContext,
  data?: CreateTeamInput,
  token?: string
): Promise<string> {
  // 1. Criar team
  const res = await request.post(`${API_BASE}/teams`, { data: body });
  const team = await res.json();

  // 2. Adicionar criador como membro
  await request.post(`${API_BASE}/teams/${team.id}/members`, {
    data: {
      person_id: SEED_PERSON_ADMIN_ID, // ou extrair do token
      org_membership_id: SEED_MEMBERSHIP_ADMIN_ID,
      status: 'ativo'
    },
    headers: getAuthHeaders(token)
  });

  return team.id;
}
```

**Vantagens**:
- ✅ Não toca backend
- ✅ Rápido de implementar

**Desvantagens**:
- ❌ Testes fazem mais que produção (discrepância)
- ❌ Não resolve problema real do backend
- ❌ Futuros testes precisarão do mesmo workaround

---

### ❌ Opção 3: Usar Team Base do Seed

**Fazer todos os testes usarem o mesmo team do seed.**

**Desvantagens**:
- ❌ Testes não isolados (compartilham state)
- ❌ Training sessions acumulam entre testes
- ❌ Falhas em um teste afetam outros
- ❌ Não escalável (conflitos de nomes, IDs, etc)

**Status**: ❌ NÃO RECOMENDADO

---

## Recomendação Final

**Implementar Opção 1 (Backend Auto-Adicionar Criador)**

Razões:
1. Corrige problema real do sistema
2. Comportamento esperado e intuitivo
3. Alinha com padrões de SaaS
4. Testes passam naturalmente
5. Beneficia tanto testes quanto produção

---

## Próximos Passos

### Fase 1: Implementar Solução
1. [ ] Modificar `team_service.py` para auto-adicionar criador como membro
2. [ ] Testar criação de team via API diretamente
3. [ ] Verificar se team_membership é criado

### Fase 2: Validar Correção
4. [ ] Re-executar testes de training sessions
5. [ ] Verificar que 14/14 testes passam (100%)
6. [ ] Documentar Run 8 no RUN_LOG.md

### Fase 3: Finalizar
7. [ ] Atualizar CHANGELOG.md
8. [ ] Marcar issue 409 como resolvido
9. [ ] Executar pipeline E2E completo

---

## Arquivos Modificados

| Arquivo | Tipo | Descrição |
|---------|------|-----------|
| `scripts/seed_e2e.py` | Backend | IDs corrigidos (linhas 56-90, 306-320) |
| `tests/e2e/shared-data.ts` | Frontend | NOVO - IDs centralizados |
| `tests/e2e/tests_log/PROBLEMA_409_ANALYSIS.md` | Docs | NOVO - Análise completa do erro |
| `tests/e2e/tests_log/RUN7_SUMMARY.md` | Docs | Este arquivo |

---

## Lições Aprendidas

1. **Erros genéricos dificultam debug**: "DATABASE_CONSTRAINT_VIOLATION" deveria especificar qual constraint
2. **Backend deve ter comportamento intuitivo**: Criador de recurso = owner automático
3. **Testes devem simular produção**: Se tests criam teams, produção também criará
4. **IDs centralizados são críticos**: shared-data.ts evita mismatches
5. **Seed deve ser idempotente**: ON CONFLICT permite re-execução sem falhas

---

**Status**: ✅ PRONTO PARA IMPLEMENTAÇÃO
**Próxima Ação**: Modificar `team_service.py` conforme Opção 1
**ETA**: 15-30 minutos (implementação + testes)
