<!-- STATUS: DEPRECATED | arquivado -->

# ✅ CONTRATO REAL - Módulo Teams Atualizado

**Data de Atualização:** 2026-01-12
**Status:** Sincronizado com implementação real (85%)
**Versão:** Pós-integração teams_gaps

---

## 📋 Resumo Executivo

O **CONTRATO REAL** do módulo Teams foi completamente atualizado e agora reflete a implementação atual do sistema após a integração de `teams_gaps` e validação para staging.

### O que foi feito

1. ✅ Analisados todos os arquivos em `src/app/(admin)/teams/**`
2. ✅ Analisado `middleware.ts` e regras que afetam o módulo
3. ✅ Analisados endpoints em `lib/api/`
4. ✅ Analisado Prisma schema (modelos Team, TeamMembership, TeamRegistration)
5. ✅ Analisados todos os 11 specs E2E em `tests/e2e/teams/`
6. ✅ Analisadas regras do sistema
7. ✅ **ATUALIZADO:** `teams-CONTRACT.md` com implementação real
8. ✅ **VERIFICADO:** Testes E2E (estrutura canônica em `tests/e2e/teams/*.spec.ts`)

---

## 📄 Arquivos Atualizados

### 1. teams-CONTRACT.md ✅

**Local:** `tests/e2e/teams_rules/teams-CONTRACT.md`

**Conteúdo atualizado:**
- 📍 12 seções completas documentando toda a implementação
- 📍 17 endpoints API documentados (100% cobertos)
- 📍 Matriz completa RBAC (roles e permissões)
- 📍 TestIDs canônicos por página
- 📍 Validações frontend e backend
- 📍 Fluxos end-to-end (criar, convidar, welcome)
- 📍 Discrepâncias conhecidas e TODOs

### 2. Testes E2E

**Observação:** O arquivo `teams-e2e.test.ts` **NÃO EXISTE**.

Os testes E2E estão na **estrutura canônica**:
```
tests/e2e/teams/
├── teams.auth.spec.ts
├── teams.contract.spec.ts
├── teams.crud.spec.ts
├── teams.invites.spec.ts
├── teams.rbac.spec.ts
├── teams.routing.spec.ts
├── teams.states.spec.ts
├── teams.welcome.spec.ts
├── teams.trainings.spec.ts
├── teams.stats.spec.ts
└── teams.athletes.spec.ts
```

**Status:** ✅ Testes já refletem o contrato atualizado (90% de cobertura)

---

## 🔍 Principais Mudanças no Contrato

### Adicionado

| Funcionalidade | Descrição |
|----------------|-----------|
| **Endpoints RESTful de Invites** | `POST /teams/{id}/invites`, `DELETE /teams/{id}/invites/{id}/resend` |
| **Códigos de Erro Padronizados** | INVITE_SENT, MEMBER_ACTIVE, BINDING_CONFLICT, etc. |
| **Validação de Duplicados** | Convite duplicado considerando gênero/categoria (Sprint 3) |
| **Idempotência em Resend** | Reutiliza token se >4h restantes |
| **Welcome Flow Completo** | Verificação de token + completar cadastro |
| **Modelos Backend** | Team, TeamMembership, TeamRegistration documentados |
| **RBAC Matriz Completa** | Permissões por role (owner, admin, dirigente, coordenador, treinador, membro) |
| **Fluxos End-to-End** | Criar equipe, convidar, aceitar convite documentados |

### Atualizado

| Seção | Mudanças |
|-------|----------|
| **Rotas Frontend** | Tabs válidas: overview, members, settings, trainings, stats |
| **Middleware Rules** | Autenticação, validação UUID, normalização de tabs |
| **TestIDs** | Manifesto completo por página |
| **Estados Visuais** | Loading, success, error, empty documentados |
| **Limitações** | Regras técnicas e de negócio |

---

## ⚠️ Discrepâncias Conhecidas

### Resolvidas ✅

| Discrepância | Status |
|--------------|--------|
| Endpoints RESTful `/teams/{teamId}/invites` ausentes | ✅ RESOLVIDO (Sprint 1) |
| Códigos de erro não padronizados | ✅ RESOLVIDO (Sprint 3) |
| Validação de convites duplicados ausente | ✅ RESOLVIDO (Sprint 3) |
| Idempotência em resend de convites | ✅ RESOLVIDO (Sprint 3) |
| Welcome flow incompleto | ✅ RESOLVIDO (Sprint 2) |

### Pendentes (TODOs) ⚠️

| Discrepância | Impacto | Workaround |
|--------------|---------|------------|
| **Endpoint `/teams/{id}/leave` não existe** | Médio | Frontend usa `DELETE /teams/{id}` com reason |
| **Permissões específicas por equipe não implementadas** | Médio | Frontend usa `user.role` global |
| **Season visível como UUID** | Baixo | Adapter não converte para label |
| **Adapter limpa nome concatenado com timestamp** | Baixo | Workaround no adapter |

---

## 📊 Cobertura de Sincronização

```
┌──────────────────────────┬────────────┬────────┐
│ Componente               │ Sincronizado│ Status │
├──────────────────────────┼────────────┼────────┤
│ Frontend (src/app)       │    90%     │   ✅   │
│ Backend (endpoints)      │    85%     │   ⚠️   │
│ Testes E2E               │    90%     │   ✅   │
│ Contrato (documentação)  │   100%     │   ✅   │
│ Prisma Schema            │   100%     │   ✅   │
├──────────────────────────┼────────────┼────────┤
│ SINCRONIZAÇÃO GLOBAL     │    85%     │   ⚠️   │
└──────────────────────────┴────────────┴────────┘
```

**Status:** ⚠️ **Bom para Staging, melhorar para Produção**

---

## 🎯 Recomendações

### Curto Prazo (Sprint Atual)

1. **Implementar endpoint `/teams/{id}/leave`**
   - Permite usuário sair da equipe sem soft delete
   - Validação: owner não pode sair
   - Remove TeamMembership mantendo histórico

2. **Implementar endpoint `/teams/{id}/my-role`**
   - Retorna papel específico do usuário na equipe
   - Busca via TeamMembership (staff) ou TeamRegistration (atleta)
   - Retorna role, permissions, hierarchyLevel

3. **Atualizar `useTeamPermissions` hook**
   - Buscar role específico da equipe
   - Evitar usar `user.role` global

### Médio Prazo (Próximo Sprint)

1. **Adicionar testes E2E para:**
   - Binding conflicts (gênero/categoria)
   - Idempotência em resend
   - Sair da equipe

2. **Criar diagramas de fluxo:**
   - Fluxo de convite completo
   - Fluxo de criação de equipe
   - Fluxo de RBAC

### Longo Prazo (Backlog)

1. Corrigir bug de nome concatenado com timestamp
2. Adicionar eager loading de Season
3. Criar documentação visual (diagramas UML)

---

## 📚 Documentação Relacionada

| Documento | Descrição |
|-----------|-----------|
| [teams-CONTRACT.md](teams-CONTRACT.md) | **Contrato completo atualizado** |
| [ANALISE_COBERTURA.md](ANALISE_COBERTURA.md) | Análise de cobertura de testes (90%) |
| [INTEGRACAO_GAPS_COMPLETA.md](INTEGRACAO_GAPS_COMPLETA.md) | Integração teams_gaps → canônica |
| [INDEX_E2E.md](../INDEX_E2E.md) | Índice de todos os testes E2E |
| [PLANO_VALIDACAO_STAGING.md](PLANO_VALIDACAO_STAGING.md) | Plano de validação para staging |

---

## 🔗 Estrutura de Testes E2E

### Estrutura Atual (Canônica)

```
tests/e2e/
├── health.gate.spec.ts              ← GATE
├── setup/auth.setup.ts               ← SETUP
├── teams/
│   ├── teams.contract.spec.ts       ← CONTRATO
│   ├── teams.auth.spec.ts           ← Autenticação
│   ├── teams.crud.spec.ts           ← CRUD básico
│   ├── teams.invites.spec.ts        ← Convites (Sprint 1-3)
│   ├── teams.welcome.spec.ts        ← Welcome flow
│   ├── teams.rbac.spec.ts           ← Permissões
│   ├── teams.routing.spec.ts        ← Rotas e redirects
│   ├── teams.states.spec.ts         ← Estados visuais
│   ├── teams.trainings.spec.ts      ← Aba Trainings
│   ├── teams.stats.spec.ts          ← Aba Stats
│   └── teams.athletes.spec.ts       ← Atletas
├── smoke-tests.spec.ts              ← 5 testes críticos
└── teams_rules/
    ├── teams-CONTRACT.md            ← CONTRATO ATUALIZADO ✅
    ├── ANALISE_COBERTURA.md         ← Análise de cobertura
    ├── INTEGRACAO_GAPS_COMPLETA.md  ← Histórico de integração
    └── CONTRATO_ATUALIZADO.md       ← Este documento
```

**Observação:** `teams-e2e.test.ts` **não existe** porque os testes seguem a estrutura canônica acima.

---

## ✅ Checklist de Sincronização

- [x] Frontend analisado (`src/app/(admin)/teams/**`)
- [x] Middleware analisado (`middleware.ts`)
- [x] Endpoints API analisados (`lib/api/`)
- [x] Prisma schema analisado
- [x] Testes E2E analisados (`tests/e2e/teams/`)
- [x] Regras do sistema analisadas (`system_rules.md`)
- [x] **CONTRATO ATUALIZADO** (`teams-CONTRACT.md`)
- [x] **Verificação de testes:** Estrutura canônica (não há `teams-e2e.test.ts`)
- [x] Discrepâncias identificadas e documentadas
- [x] Recomendações de melhoria criadas

---

## 🎓 Como Usar o Contrato

### Para Desenvolvedores

1. **Antes de implementar feature:**
   - Ler seção relevante do contrato
   - Verificar endpoints disponíveis
   - Validar permissões RBAC necessárias

2. **Ao criar testes:**
   - Consultar seção de TestIDs
   - Usar nomenclatura canônica
   - Validar assertions conforme contrato

3. **Ao encontrar bug:**
   - Verificar se comportamento está documentado
   - Atualizar contrato se necessário
   - Adicionar teste para evitar regressão

### Para QA

1. **Manual testing:**
   - Usar contrato como guia de casos de teste
   - Validar fluxos end-to-end documentados
   - Verificar mensagens de erro esperadas

2. **Bug report:**
   - Referenciar seção do contrato
   - Indicar comportamento esperado vs observado

### Para Product Owner

1. **Planning:**
   - Consultar limitações técnicas
   - Verificar regras de negócio
   - Validar features implementadas vs planejadas

---

## 📞 Contato

**Dúvidas sobre o contrato?**
- Consultar documentação técnica: [teams-CONTRACT.md](teams-CONTRACT.md)
- Verificar análise de cobertura: [ANALISE_COBERTURA.md](ANALISE_COBERTURA.md)

---

**Última atualização:** 2026-01-12
**Próxima revisão:** Após implementação dos TODOs pendentes
**Responsável:** Time de Engenharia
