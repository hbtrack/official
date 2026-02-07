<!-- STATUS: DEPRECATED | arquivado -->

# ✅ Validação Teams para Staging - RESUMO EXECUTIVO

## 🎯 Objetivo

Validar módulo Teams completamente antes de deploy em staging usando a suíte E2E integrada (pós-eliminação de `teams_gaps`).

---

## 📋 Checklist Pré-Deploy (OBRIGATÓRIO)

### ✅ FASE 1: Validação Local (30 minutos)

```powershell
# 1. Executar suite completa
cd "C:\HB TRACK\Hb Track - Fronted"
.\tests\e2e\run-teams-suite.ps1

# 2. Executar smoke tests (críticos)
npx playwright test tests/e2e/smoke-tests.spec.ts --project=chromium --workers=1 --retries=0
```

**Critério GO**: Ambos devem passar 100%

---

### ✅ FASE 2: Smoke Tests (5 testes críticos - 15 minutos)

Os 5 fluxos que **DEVEM** funcionar:

| # | Teste | O que valida |
|---|-------|--------------|
| 1 | Criar equipe via UI | Modal, formulário, validação, redirect |
| 2 | Equipe aparece na lista | API GET, listagem, card visível |
| 3 | Convidar membro | Modal convite, validação email, toast |
| 4 | Atualizar nome | Autosave, persistência, reload |
| 5 | Deletar equipe | Confirmação, soft delete, redirect |

**Comando**:
```powershell
npx playwright test tests/e2e/smoke-tests.spec.ts --project=chromium --workers=1 --retries=0
```

**Critério GO**: 5/5 testes passando

---

### ✅ FASE 3: Checklist Técnico (10 minutos)

- [ ] **Testes**
  - [ ] Suite completa: 100% aprovação
  - [ ] Smoke tests: 5/5 passando
  - [ ] Zero timeouts > 30s
  - [ ] Logs limpos (sem errors críticos)

- [ ] **Código**
  - [ ] Branch atualizado com `main`
  - [ ] Build produção gerado: `npm run build`
  - [ ] Linter passou: `npm run lint`

- [ ] **Documentação**
  - [ ] [INDEX_E2E.md](tests/e2e/INDEX_E2E.md) atualizado
  - [ ] [INTEGRACAO_GAPS_COMPLETA.md](tests/e2e/teams_rules/INTEGRACAO_GAPS_COMPLETA.md) criado
  - [ ] CHANGELOG.md atualizado

---

### ✅ FASE 4: Validação Manual (15 minutos)

Testar manualmente em ambiente local:

1. **Login** → `/teams` carrega
2. **Criar equipe** → Modal abre, formulário válido, equipe criada
3. **Listar equipes** → Equipes aparecem nos cards
4. **Convidar membro** → Email válido, toast sucesso
5. **Editar equipe** → Autosave funciona, F5 persiste
6. **Deletar equipe** → Confirmação, soft delete, redirect
7. **Abas novas**:
   - Trainings carrega sem erro
   - Stats carrega sem erro
   - Athletes/Members seção visível

**Critério GO**: Todos os 7 fluxos funcionam sem erro

---

## 🚀 Decisão GO/NO-GO para Staging

### ✅ GO (Liberar Deploy)

**Todos os critérios abaixo DEVEM ser atendidos**:

- ✅ Suite completa passou (100%)
- ✅ Smoke tests 5/5
- ✅ Validação manual 7/7
- ✅ Build produção sem erros
- ✅ Linter passou
- ✅ Documentação atualizada

**Comando final de verificação**:
```powershell
.\tests\e2e\run-teams-suite.ps1 && `
npx playwright test tests/e2e/smoke-tests.spec.ts --project=chromium --workers=1 --retries=0 && `
npm run build && `
npm run lint && `
Write-Host "`n✅✅✅ TUDO OK - GO PARA STAGING! ✅✅✅" -ForegroundColor Green
```

### ❌ NO-GO (Bloquear Deploy)

**Qualquer um dos critérios abaixo bloqueia deploy**:

- ❌ Qualquer teste da suite falhando
- ❌ Qualquer smoke test falhando
- ❌ Build de produção com erro
- ❌ Linter com errors (warnings OK)
- ❌ Validação manual encontrou bug crítico

**Ação**: Corrigir problemas → Repetir FASE 1-4

---

## 📊 Estrutura de Testes (Pós-Integração)

```
tests/e2e/
├── health.gate.spec.ts              ← GATE
├── setup/auth.setup.ts               ← SETUP
├── teams/
│   ├── teams.contract.spec.ts       ← CONTRATO
│   ├── teams.auth.spec.ts           ← Funcionais
│   ├── teams.crud.spec.ts           ← Funcionais
│   ├── teams.states.spec.ts         ← Funcionais
│   ├── teams.rbac.spec.ts           ← Funcionais
│   ├── teams.welcome.spec.ts        ← Funcionais
│   ├── teams.routing.spec.ts        ← Funcionais
│   ├── teams.invites.spec.ts        ← Funcionais
│   ├── teams.trainings.spec.ts      ← Funcionais (NOVO)
│   ├── teams.stats.spec.ts          ← Funcionais (NOVO)
│   └── teams.athletes.spec.ts       ← Funcionais (NOVO)
└── smoke-tests.spec.ts              ← CRÍTICOS
```

**Total**: ~150 testes únicos (387 antes, eliminadas duplicatas)

---

## 🔥 Smoke Tests (Validação Rápida)

Se tiver **pouco tempo** antes do deploy, rode apenas:

```powershell
# 15 minutos - Validação mínima crítica
npx playwright test tests/e2e/smoke-tests.spec.ts --project=chromium --workers=1 --retries=0
```

**5 testes críticos**:
1. ✅ Criar equipe
2. ✅ Equipe aparece
3. ✅ Convidar membro
4. ✅ Atualizar nome
5. ✅ Deletar equipe

**Se 5/5 passam**: Risco baixo de deploy

---

## 📝 Pós-Deploy em Staging

### Validação Imediata (15 min após deploy)

1. **Health Check** (2 min):
   ```bash
   curl https://staging.hbtrack.com/api/v1/health
   # Deve retornar 200 OK
   ```

2. **Smoke Tests em Staging** (10 min):
   ```powershell
   # Configurar ambiente para staging
   $env:NEXT_PUBLIC_API_URL = "https://api-staging.hbtrack.com"
   npx playwright test tests/e2e/smoke-tests.spec.ts --project=chromium --workers=1 --retries=1
   ```

3. **Validação Manual Rápida** (3 min):
   - [ ] Login em staging funciona
   - [ ] `/teams` carrega
   - [ ] Criar 1 equipe funciona
   - [ ] Equipe aparece na lista

**Se TUDO OK**: ✅ Deploy validado
**Se ALGO FALHA**: ❌ Rollback imediato

---

## 🚨 Monitoramento (Primeiras 24h)

### Alertas Críticos

Configurar alertas para:
- ❌ Taxa de erro `/teams/*` > 5%
- ❌ Latência API `/teams` > 3s
- ❌ Console errors em Sentry > 10/hora

### Métricas a Acompanhar

- **Frontend**: Console errors, taxa de erro de calls API
- **Backend**: Erros 500/400, latência endpoints
- **Uso**: Equipes criadas, convites enviados

---

## 📞 Procedimento de Rollback

Se houver **problemas críticos** em staging:

```bash
# Reverter último commit
git revert <commit-hash>
git push origin main

# CI/CD faz rollback automático
```

**Critério para Rollback**:
- ❌ Smoke tests falhando em staging
- ❌ Taxa de erro > 10%
- ❌ Funcionalidade crítica quebrada (criar/listar/deletar equipes)

---

## ✨ Novidades nesta Versão

### Features Adicionadas

- ✨ **Aba Trainings**: CRUD de treinos (API + UI)
- ✨ **Aba Stats**: Estatísticas de equipe
- ✨ **Athletes**: Gerenciamento de registrations

### Melhorias de Testes

- 🔄 Estrutura canônica aplicada (GATE → SETUP → CONTRATO → FUNCIONAIS)
- 🔄 Eliminadas duplicatas (387 → ~150 testes únicos)
- 🔄 Smoke tests criados (5 críticos)
- 🔄 Script de validação automatizado

---

## 📚 Documentação Completa

- **Plano Detalhado**: [PLANO_VALIDACAO_STAGING.md](tests/e2e/teams_rules/PLANO_VALIDACAO_STAGING.md)
- **Índice E2E**: [INDEX_E2E.md](tests/e2e/INDEX_E2E.md)
- **Integração Gaps**: [INTEGRACAO_GAPS_COMPLETA.md](tests/e2e/teams_rules/INTEGRACAO_GAPS_COMPLETA.md)
- **Regras de Testes**: [REGRAS_TESTES.md](tests/e2e/teams_rules/REGRAS_TESTES.md)

---

## 🎯 TL;DR - Comandos Essenciais

```powershell
# 1. Validação completa local (30 min)
.\tests\e2e\run-teams-suite.ps1

# 2. Smoke tests (15 min)
npx playwright test tests/e2e/smoke-tests.spec.ts --project=chromium --workers=1 --retries=0

# 3. Build produção
npm run build

# 4. Linter
npm run lint

# ✅ Se TUDO passou → GO para staging
# ❌ Se ALGO falhou → Corrigir e repetir
```

---

**Última atualização**: 2026-01-11
**Responsável**: Time de Engenharia
**Status**: ⬜ Pendente Execução
