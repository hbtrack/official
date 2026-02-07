<!-- STATUS: NEEDS_REVIEW -->

# Fluxo de Validação - Teams para Staging

## Diagrama Visual do Processo

```
┌─────────────────────────────────────────────────────────────────────┐
│                     INÍCIO: Código Pronto                            │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│  FASE 1: VALIDAÇÃO LOCAL (30 min)                                   │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │ 1. Executar suite completa                                    │  │
│  │    .\tests\e2e\run-teams-suite.ps1                            │  │
│  │                                                               │  │
│  │    ├─ GATE (health check)                                    │  │
│  │    ├─ SETUP (autenticação)                                   │  │
│  │    ├─ CONTRATO (navegação/404/redirects)                     │  │
│  │    └─ FUNCIONAIS (10 specs)                                  │  │
│  │                                                               │  │
│  │ 2. Executar smoke tests                                      │  │
│  │    npx playwright test tests/e2e/smoke-tests.spec.ts         │  │
│  │                                                               │  │
│  │ 3. Build produção                                            │  │
│  │    npm run build                                             │  │
│  │                                                               │  │
│  │ 4. Linter                                                    │  │
│  │    npm run lint                                              │  │
│  └───────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
                        ┌─────────────────┐
                        │ TODOS PASSARAM? │
                        └─────────────────┘
                          │               │
                    SIM ▼               ▼ NÃO
                        │               │
                        │               └──────────────┐
                        │                              │
                        │                              ▼
                        │               ┌────────────────────────────┐
                        │               │ ❌ NO-GO                   │
                        │               │                            │
                        │               │ Ações:                     │
                        │               │ 1. Analisar falhas         │
                        │               │ 2. Corrigir código         │
                        │               │ 3. Repetir FASE 1          │
                        │               └────────────────────────────┘
                        │                              │
                        │                              └─────────┐
                        │                                        │
                        ▼                                        │
┌─────────────────────────────────────────────────────────────────────┐
│  FASE 2: VALIDAÇÃO MANUAL (15 min)                                  │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │ Testar em localhost:3000:                                     │  │
│  │                                                               │  │
│  │ ✅ 1. Login → /teams carrega                                 │  │
│  │ ✅ 2. Criar equipe → Modal, formulário, redirect             │  │
│  │ ✅ 3. Listar equipes → Cards aparecem                        │  │
│  │ ✅ 4. Convidar membro → Email, toast                         │  │
│  │ ✅ 5. Editar equipe → Autosave, F5                           │  │
│  │ ✅ 6. Deletar equipe → Confirmação, soft delete              │  │
│  │ ✅ 7. Trainings/Stats/Athletes → Abas carregam               │  │
│  └───────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
                        ┌─────────────────┐
                        │ 7/7 FUNCIONAM?  │
                        └─────────────────┘
                          │               │
                    SIM ▼               ▼ NÃO
                        │               │
                        │               └──────────────┐
                        │                              │
                        ▼                              ▼
┌─────────────────────────────────────┐  ┌────────────────────────────┐
│  ✅ GO PARA STAGING                 │  │ ❌ NO-GO                   │
│                                     │  │                            │
│  Checklist final:                   │  │ Bug crítico encontrado     │
│  ✅ Suite 100%                      │  │ → Corrigir                 │
│  ✅ Smoke 5/5                       │  │ → Repetir FASE 1 e 2       │
│  ✅ Manual 7/7                      │  └────────────────────────────┘
│  ✅ Build OK                        │               │
│  ✅ Lint OK                         │               │
│  ✅ Docs OK                         │               └─────────┐
└─────────────────────────────────────┘                         │
                  │                                             │
                  ▼                                             │
┌─────────────────────────────────────────────────────────────────────┐
│  DEPLOY EM STAGING                                                  │
│                                                                     │
│  1. git push origin main                                            │
│  2. CI/CD roda testes                                               │
│  3. CI/CD faz build                                                 │
│  4. CI/CD deploya em staging                                        │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│  VALIDAÇÃO PÓS-DEPLOY (15 min após deploy)                          │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │ 1. Health Check (2 min)                                       │  │
│  │    curl https://staging.hbtrack.com/api/v1/health             │  │
│  │    → Deve retornar 200 OK                                     │  │
│  │                                                               │  │
│  │ 2. Smoke Tests em Staging (10 min)                           │  │
│  │    Configurar: $env:NEXT_PUBLIC_API_URL = "staging"          │  │
│  │    npx playwright test smoke-tests.spec.ts --retries=1       │  │
│  │                                                               │  │
│  │ 3. Validação Manual Rápida (3 min)                           │  │
│  │    ✅ Login em staging                                        │  │
│  │    ✅ /teams carrega                                          │  │
│  │    ✅ Criar 1 equipe                                          │  │
│  │    ✅ Equipe aparece                                          │  │
│  └───────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
                        ┌─────────────────┐
                        │  TUDO OK?       │
                        └─────────────────┘
                          │               │
                    SIM ▼               ▼ NÃO
                        │               │
                        │               └──────────────┐
                        │                              │
                        ▼                              ▼
┌─────────────────────────────────────┐  ┌────────────────────────────┐
│  ✅ DEPLOY VALIDADO                 │  │ 🚨 ROLLBACK IMEDIATO       │
│                                     │  │                            │
│  Próximos passos:                   │  │ Ações:                     │
│  1. Monitorar 24h                   │  │ 1. git revert <commit>     │
│  │  - Sentry errors                 │  │ 2. git push origin main    │
│  │  - Latência API                  │  │ 3. CI/CD rollback auto     │
│  │  - Taxa de erro                  │  │ 4. Investigar problema     │
│  │                                  │  │ 5. Corrigir local          │
│  2. Coletar feedback QA             │  │ 6. Repetir desde FASE 1    │
│  3. Preparar deploy produção        │  └────────────────────────────┘
│     (após 3-7 dias)                 │
└─────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    FIM: Staging Validado ✅                          │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Decisões em Cada Etapa

### ❓ Quando NO-GO na FASE 1 (Validação Local)?

**Bloqueadores absolutos**:
- ❌ Qualquer teste da suite completa falhando
- ❌ Qualquer smoke test falhando (5 críticos)
- ❌ Build de produção com erro
- ❌ Linter com errors (warnings aceitáveis)

**Ação**: Corrigir → Repetir FASE 1

---

### ❓ Quando NO-GO na FASE 2 (Validação Manual)?

**Bloqueadores absolutos**:
- ❌ Não consegue fazer login
- ❌ Criar equipe quebrado
- ❌ Listar equipes quebrado
- ❌ Deletar equipe quebrado
- ❌ Erro 500 em qualquer fluxo crítico

**Ação**: Bug crítico → Corrigir → Repetir FASE 1 e 2

---

### ❓ Quando ROLLBACK após Deploy em Staging?

**Critérios de rollback imediato** (primeiros 15 min):
- ❌ Health check falha (API offline)
- ❌ Smoke tests falhando em staging (2+ de 5)
- ❌ Erro fatal visível na UI (500, crash)
- ❌ Funcionalidade crítica quebrada

**Critérios de rollback tardio** (primeiras 24h):
- ❌ Taxa de erro > 10%
- ❌ Latência API > 5s consistentemente
- ❌ Sentry reportando > 50 errors/hora
- ❌ Usuários não conseguem usar feature principal

**Ação**: Rollback → Investigar → Corrigir local → Repetir tudo

---

## Tempo Total Estimado

| Fase | Tempo | Pode Pular? |
|------|-------|-------------|
| **FASE 1: Suite completa** | 30 min | ❌ NÃO |
| **FASE 2: Validação manual** | 15 min | ❌ NÃO |
| Deploy (CI/CD) | 10 min | - |
| **Validação pós-deploy** | 15 min | ❌ NÃO |
| **TOTAL** | **~70 min** | - |

**Atalho**: Se **muito urgente**, rode apenas smoke tests (15 min) mas com **risco elevado**.

---

## Matriz de Risco

| Cenário | Risco | Mitigação |
|---------|-------|-----------|
| Pular suite completa | 🔴 ALTO | Rodar pelo menos smoke tests |
| Pular validação manual | 🟡 MÉDIO | Rodar smoke tests em staging |
| Pular smoke pós-deploy | 🔴 ALTO | Rollback preventivo se problema |
| Deployar sem testes | 🔴 CRÍTICO | ❌ NUNCA FAZER |

---

## Contatos de Emergência

**Se houver problema crítico em staging**:

1. **Tech Lead**: [nome] - [contato]
2. **DevOps**: [nome] - [contato]
3. **Product Owner**: [nome] - [contato]

**Procedimento**:
1. Informar no canal #eng-alerts
2. Executar rollback se necessário
3. Criar post-mortem
4. Planejar correção

---

## Checklist Rápido (Print & Pin)

```
┌────────────────────────────────────────┐
│  VALIDAÇÃO TEAMS PARA STAGING          │
├────────────────────────────────────────┤
│  PRÉ-DEPLOY                            │
│  □ Suite completa passou (100%)        │
│  □ Smoke tests 5/5                     │
│  □ Validação manual 7/7                │
│  □ Build OK                            │
│  □ Lint OK                             │
│  □ Docs atualizados                    │
│                                        │
│  PÓS-DEPLOY                            │
│  □ Health check OK                     │
│  □ Smoke tests em staging OK           │
│  □ Validação manual rápida OK          │
│  □ Sem errors em Sentry (primeiros 1h) │
│                                        │
│  ✅ GO: Todos marcados                 │
│  ❌ NO-GO: Qualquer desmarcado         │
└────────────────────────────────────────┘
```

---

**Última atualização**: 2026-01-11
