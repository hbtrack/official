<!-- STATUS: NEEDS_REVIEW -->

# Plano de Validação - Módulo Teams para Staging

## Objetivo

Validar completamente o módulo Teams antes de deploy em staging, garantindo:
- ✅ Todos os testes E2E passando
- ✅ Cobertura de casos críticos
- ✅ Zero regressões
- ✅ Performance aceitável
- ✅ Logs e documentação atualizados

---

## Fase 1: Validação Local (Desenvolvimento)

### 1.1. Executar Suite Completa (Ordem Canônica)

**Objetivo**: Garantir que TODOS os testes passam localmente.

```powershell
# Criar script de execução completa
# Salvar como: tests/e2e/run-teams-suite.ps1

# 1. GATE (infraestrutura)
Write-Host "=== FASE 1: GATE ===" -ForegroundColor Cyan
npx playwright test tests/e2e/health.gate.spec.ts --project=chromium --workers=1 --retries=0
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ GATE falhou - Suite abortada" -ForegroundColor Red
    exit 1
}

# 2. SETUP (autenticação)
Write-Host "`n=== FASE 2: SETUP ===" -ForegroundColor Cyan
npx playwright test tests/e2e/setup/auth.setup.ts --project=setup --workers=1 --retries=0
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ SETUP falhou - Suite abortada" -ForegroundColor Red
    exit 1
}

# 3. CONTRATO (navegação/erros)
Write-Host "`n=== FASE 3: CONTRATO ===" -ForegroundColor Cyan
npx playwright test tests/e2e/teams/teams.contract.spec.ts --project=chromium --workers=1 --retries=0
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ CONTRATO falhou - Suite abortada" -ForegroundColor Red
    exit 1
}

# 4. FUNCIONAIS (features)
Write-Host "`n=== FASE 4: FUNCIONAIS ===" -ForegroundColor Cyan

$functionalSpecs = @(
    "teams.auth.spec.ts",
    "teams.crud.spec.ts",
    "teams.states.spec.ts",
    "teams.rbac.spec.ts",
    "teams.welcome.spec.ts",
    "teams.routing.spec.ts",
    "teams.invites.spec.ts",
    "teams.trainings.spec.ts",
    "teams.stats.spec.ts",
    "teams.athletes.spec.ts"
)

$failedSpecs = @()

foreach ($spec in $functionalSpecs) {
    Write-Host "`n--- Executando: $spec ---" -ForegroundColor Yellow
    npx playwright test "tests/e2e/teams/$spec" --project=chromium --workers=1 --retries=0
    if ($LASTEXITCODE -ne 0) {
        $failedSpecs += $spec
        Write-Host "❌ $spec FALHOU" -ForegroundColor Red
    } else {
        Write-Host "✅ $spec PASSOU" -ForegroundColor Green
    }
}

# Relatório final
Write-Host "`n=== RELATÓRIO FINAL ===" -ForegroundColor Cyan
if ($failedSpecs.Count -eq 0) {
    Write-Host "✅ TODOS OS TESTES PASSARAM!" -ForegroundColor Green
    exit 0
} else {
    Write-Host "❌ SPECS COM FALHAS:" -ForegroundColor Red
    foreach ($spec in $failedSpecs) {
        Write-Host "  - $spec" -ForegroundColor Red
    }
    exit 1
}
```

**Executar**:
```powershell
cd "C:\HB TRACK\Hb Track - Fronted"
.\tests\e2e\run-teams-suite.ps1
```

**Critério de Sucesso**: ✅ 100% de aprovação (0 falhas)

---

### 1.2. Validar Logs de Testes

**Objetivo**: Garantir que não há warnings/erros não tratados.

```powershell
# Executar com log detalhado
 playwright testnpx tests/e2e/teams --project=chromium --workers=1 --retries=0 > tests_log.txt 2>&1

# Analisar log
cat tests_log.txt | Select-String -Pattern "error|warning|failed|timeout" -CaseSensitive:$false
```

**Checklist**:
- [ ] Sem erros de timeout excessivos (>30s)
- [ ] Sem warnings de depreciação
- [ ] Sem console.errors não tratados
- [ ] Sem memory leaks reportados

---

### 1.3. Validar Cobertura Crítica

**Objetivo**: Garantir que fluxos críticos estão cobertos.

**Fluxos Críticos (Smoke Tests)**:

```powershell
# Criar arquivo: tests/e2e/smoke-tests.spec.ts
```

```typescript
/**
 * SMOKE TESTS - Fluxos Críticos para Staging
 *
 * Estes testes DEVEM passar antes de qualquer deploy.
 * Cobrem os 5 fluxos mais críticos do módulo Teams.
 */

import { test, expect } from '@playwright/test';
import { createTeamViaAPI, deleteTeamViaAPI, inviteMemberViaAPI } from './helpers/api';

test.describe('SMOKE TESTS - Teams Module', () => {

  test('CRÍTICO 1: Admin consegue criar equipe via UI', async ({ page }) => {
    await page.goto('/teams');
    await page.locator('[data-testid="create-team-btn"]').click();

    const teamName = `Smoke-${Date.now()}`;
    await page.locator('[data-testid="team-name-input"]').fill(teamName);
    await page.locator('[data-testid="team-category-select"]').selectOption('1');
    await page.locator('[data-testid="team-gender-select"]').selectOption('masculino');
    await page.locator('[data-testid="create-team-submit"]').click();

    await expect(page).toHaveURL(/\/teams\/[a-f0-9-]+\/members/);
  });

  test('CRÍTICO 2: Equipe criada aparece na lista', async ({ page, request }) => {
    const teamName = `Smoke-List-${Date.now()}`;
    const teamId = await createTeamViaAPI(request, { name: teamName });

    try {
      await page.goto('/teams');
      await expect(page.locator(`[data-testid="team-card-${teamId}"]`)).toBeVisible({ timeout: 15000 });
    } finally {
      await deleteTeamViaAPI(request, teamId);
    }
  });

  test('CRÍTICO 3: Owner consegue convidar membro', async ({ page, request }) => {
    const teamName = `Smoke-Invite-${Date.now()}`;
    const teamId = await createTeamViaAPI(request, { name: teamName });

    try {
      await page.goto(`/teams/${teamId}/members`);
      await page.locator('[data-testid="invite-member-btn"]').click();

      const testEmail = `smoke-${Date.now()}@teste.com`;
      await page.locator('[data-testid="invite-email-input"]').fill(testEmail);
      await page.locator('[data-testid="invite-submit-btn"]').click();

      await expect(page.locator('[data-testid="toast-success"]')).toBeVisible({ timeout: 10000 });
    } finally {
      await deleteTeamViaAPI(request, teamId);
    }
  });

  test('CRÍTICO 4: Owner consegue atualizar nome da equipe', async ({ page, request }) => {
    const teamName = `Smoke-Update-${Date.now()}`;
    const teamId = await createTeamViaAPI(request, { name: teamName });

    try {
      await page.goto(`/teams/${teamId}/settings`);

      const newName = `Smoke-Updated-${Date.now()}`;
      await page.locator('[data-testid="team-name-input"]').fill(newName);
      await page.locator('[data-testid="team-name-input"]').blur();

      await expect(page.locator('[data-testid="toast-success"]')).toBeVisible({ timeout: 10000 });

      await page.reload();
      await expect(page.locator('[data-testid="team-name-input"]')).toHaveValue(newName);
    } finally {
      await deleteTeamViaAPI(request, teamId);
    }
  });

  test('CRÍTICO 5: Owner consegue deletar equipe', async ({ page, request }) => {
    const teamName = `Smoke-Delete-${Date.now()}`;
    const teamId = await createTeamViaAPI(request, { name: teamName });

    await page.goto(`/teams/${teamId}/settings`);
    await page.locator('[data-testid="delete-team-btn"]').click();

    await page.getByPlaceholder('Digite o nome da equipe').fill(teamName);
    await page.locator('[data-testid="confirm-delete-btn"]').click();

    await expect(page).toHaveURL('/teams');

    // Verificar que não aparece mais (ou aparece arquivada)
    const cardVisible = await page.locator(`[data-testid="team-card-${teamId}"]`).isVisible().catch(() => false);
    if (cardVisible) {
      await expect(page.locator(`[data-testid="team-card-${teamId}"]`)).toHaveClass(/opacity-60/);
    }
  });
});
```

**Executar**:
```powershell
npx playwright test tests/e2e/smoke-tests.spec.ts --project=chromium --workers=1 --retries=0
```

**Critério de Sucesso**: ✅ 5/5 testes críticos passando

---

### 1.4. Verificar Ambiente de Teste

**Checklist**:
- [ ] `.env.test` configurado corretamente
- [ ] `TEST_ADMIN_EMAIL` e `TEST_ADMIN_PASSWORD` válidos
- [ ] API local rodando (`http://localhost:8000/health` retorna 200)
- [ ] Frontend local rodando (`http://localhost:3000`)
- [ ] Banco de dados com seed E2E aplicado

**Comando de verificação**:
```powershell
# Verificar API
curl http://localhost:8000/api/v1/health

# Verificar Frontend
curl http://localhost:3000

# Verificar variáveis de ambiente
cat .env.test | Select-String "TEST_"
```

---

## Fase 2: Validação de Regressão

### 2.1. Comparar com Baseline

**Objetivo**: Garantir que não houve regressões após integração de `teams_gaps`.

**Passos**:

1. **Criar snapshot de testes ANTES da integração** (se não tiver):
   ```powershell
   # Se ainda não rodou, rode a suite antiga e salve
   npx playwright test tests/e2e/teams --project=chromium --workers=1 --retries=0 --reporter=json > baseline-old.json
   ```

2. **Rodar suite NOVA e comparar**:
   ```powershell
   # Suite nova (pós-integração)
   npx playwright test tests/e2e/teams --project=chromium --workers=1 --retries=0 --reporter=json > baseline-new.json
   ```

3. **Analisar diferenças**:
   - Total de testes: deve ser >= baseline antiga
   - Taxa de aprovação: deve ser 100% em ambas
   - Tempo de execução: não deve aumentar >20%

**Critério de Sucesso**:
- ✅ Taxa de aprovação mantida ou melhorada
- ✅ Nenhum teste que passava agora falha
- ✅ Tempo total < baseline + 20%

---

### 2.2. Testar Cross-Browser (Opcional mas Recomendado)

**Objetivo**: Garantir compatibilidade entre navegadores.

```powershell
# Chromium (principal)
npx playwright test tests/e2e/smoke-tests.spec.ts --project=chromium --workers=1 --retries=0

# Firefox (secundário)
npx playwright test tests/e2e/smoke-tests.spec.ts --project=firefox --workers=1 --retries=0

# Webkit/Safari (terciário)
npx playwright test tests/e2e/smoke-tests.spec.ts --project=webkit --workers=1 --retries=0
```

**Critério de Sucesso**:
- ✅ Smoke tests passam em Chromium (obrigatório)
- ✅ Smoke tests passam em Firefox (recomendado)
- ⚠️ Webkit pode ter falhas conhecidas (documentar)

---

## Fase 3: Preparação para Staging

### 3.1. Atualizar Documentação

**Checklist**:
- [ ] `INDEX_E2E.md` atualizado com comandos corretos
- [ ] `INTEGRACAO_GAPS_COMPLETA.md` revisado
- [ ] `README.md` do projeto menciona nova estrutura de testes
- [ ] Changelog atualizado com features de Teams

**Arquivo**: `CHANGELOG.md`
```markdown
## [Unreleased] - 2026-01-11

### Added - Módulo Teams
- ✨ Aba Trainings: CRUD de treinos via API/UI
- ✨ Aba Stats: Estatísticas de equipe
- ✨ Athletes: Gerenciamento de registrations (atletas vinculados)

### Changed - Testes E2E
- 🔄 Integração completa de `teams_gaps` → estrutura canônica
- 🔄 Eliminadas duplicatas (387 testes → ~150 únicos)
- 🔄 Ordem canônica aplicada: GATE → SETUP → CONTRATO → FUNCIONAIS

### Fixed
- 🐛 Correções de validação em formulários
- 🐛 Autosave em settings estabilizado
- 🐛 Toasts de sucesso/erro padronizados
```

---

### 3.2. Criar Arquivo de Configuração para Staging

**Arquivo**: `.env.staging` (exemplo)
```bash
# API
NEXT_PUBLIC_API_URL=https://api-staging.hbtrack.com
NEXT_PUBLIC_API_VERSION=v1

# Frontend
NEXT_PUBLIC_APP_URL=https://staging.hbtrack.com

# Testes E2E (staging)
TEST_ADMIN_EMAIL=admin-e2e@staging.hbtrack.com
TEST_ADMIN_PASSWORD=<senha-segura-staging>
TEST_API_URL=https://api-staging.hbtrack.com
```

---

### 3.3. Preparar Script de Validação Pós-Deploy

**Arquivo**: `scripts/validate-staging.ps1`

```powershell
# Script de validação pós-deploy em staging
param(
    [string]$StagingUrl = "https://staging.hbtrack.com"
)

Write-Host "=== Validação Pós-Deploy - Staging ===" -ForegroundColor Cyan

# 1. Health check
Write-Host "`n1. Verificando health da API..." -ForegroundColor Yellow
$healthResponse = Invoke-WebRequest -Uri "$StagingUrl/api/v1/health" -Method GET
if ($healthResponse.StatusCode -eq 200) {
    Write-Host "✅ API online" -ForegroundColor Green
} else {
    Write-Host "❌ API offline ou com erro" -ForegroundColor Red
    exit 1
}

# 2. Frontend carregando
Write-Host "`n2. Verificando frontend..." -ForegroundColor Yellow
$frontendResponse = Invoke-WebRequest -Uri $StagingUrl -Method GET
if ($frontendResponse.StatusCode -eq 200) {
    Write-Host "✅ Frontend online" -ForegroundColor Green
} else {
    Write-Host "❌ Frontend offline ou com erro" -ForegroundColor Red
    exit 1
}

# 3. Smoke tests contra staging
Write-Host "`n3. Executando smoke tests..." -ForegroundColor Yellow
$env:NEXT_PUBLIC_API_URL = "$StagingUrl/api/v1"
npx playwright test tests/e2e/smoke-tests.spec.ts --project=chromium --workers=1 --retries=1

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ VALIDAÇÃO STAGING CONCLUÍDA COM SUCESSO!" -ForegroundColor Green
} else {
    Write-Host "`n❌ SMOKE TESTS FALHARAM EM STAGING" -ForegroundColor Red
    exit 1
}
```

---

## Fase 4: Checklist Final Pré-Deploy

### 4.1. Checklist Técnico

- [ ] **Testes**
  - [ ] Suite completa passou localmente (100%)
  - [ ] Smoke tests passaram (5/5)
  - [ ] Sem regressões detectadas
  - [ ] Logs limpos (sem errors/warnings críticos)

- [ ] **Código**
  - [ ] Branch atualizado com `main`/`develop`
  - [ ] Sem conflitos de merge
  - [ ] Linter passou (sem errors)
  - [ ] Build de produção gerado sem erros

- [ ] **Documentação**
  - [ ] INDEX_E2E.md atualizado
  - [ ] CHANGELOG.md atualizado
  - [ ] README.md revisado
  - [ ] Comentários de código adequados

- [ ] **Configuração**
  - [ ] `.env.staging` criado e validado
  - [ ] Secrets configurados no CI/CD
  - [ ] Variáveis de ambiente documentadas

---

### 4.2. Checklist de Produto

- [ ] **Funcionalidades Testadas Manualmente**
  - [ ] Criar equipe (admin)
  - [ ] Listar equipes
  - [ ] Navegar para detalhe
  - [ ] Convidar membro
  - [ ] Atualizar configurações
  - [ ] Deletar equipe
  - [ ] Aba Trainings funcional
  - [ ] Aba Stats funcional
  - [ ] Athletes/Registrations funcional

- [ ] **UX/UI**
  - [ ] Botões visíveis e clicáveis
  - [ ] Toasts aparecem e desaparecem
  - [ ] Modals abrem/fecham corretamente
  - [ ] Loading states aparecem quando necessário
  - [ ] Empty states são informativos

- [ ] **Permissões**
  - [ ] Admin vê todos os botões
  - [ ] Atleta tem acesso restrito
  - [ ] 403/404 aparecem quando apropriado

---

### 4.3. Checklist de Segurança

- [ ] **Autenticação**
  - [ ] Rotas protegidas redirecionam para /signin
  - [ ] Token de autenticação é httpOnly
  - [ ] Sessão expira corretamente

- [ ] **Autorização**
  - [ ] Usuário só vê equipes que tem acesso
  - [ ] Botões sensíveis (deletar) só aparecem para owners
  - [ ] API valida permissões no backend

- [ ] **Validação**
  - [ ] Inputs validados no frontend E backend
  - [ ] SQL injection prevenido (queries parametrizadas)
  - [ ] XSS prevenido (sanitização de inputs)

---

## Fase 5: Deploy e Validação em Staging

### 5.1. Deploy

```bash
# Exemplo de deploy via CI/CD
git checkout main
git pull origin main
git merge feature/teams-integration
git push origin main

# CI/CD automaticamente:
# 1. Roda testes
# 2. Faz build
# 3. Deploy em staging
```

---

### 5.2. Validação Pós-Deploy (15 minutos após deploy)

**Executar**:
```powershell
.\scripts\validate-staging.ps1 -StagingUrl "https://staging.hbtrack.com"
```

**Validação Manual (Checklist Rápido)**:

1. **Acesso básico** (2 min):
   - [ ] Consegue fazer login em staging
   - [ ] Dashboard `/teams` carrega
   - [ ] Equipes aparecem na lista

2. **Fluxo crítico 1: Criar equipe** (3 min):
   - [ ] Clicar em "Criar equipe"
   - [ ] Preencher formulário
   - [ ] Equipe criada com sucesso
   - [ ] Redirecionado para /members?isNew=true

3. **Fluxo crítico 2: Convidar membro** (3 min):
   - [ ] Abrir equipe criada
   - [ ] Ir para aba Members
   - [ ] Clicar "Convidar"
   - [ ] Preencher email
   - [ ] Convite enviado (toast sucesso)

4. **Fluxo crítico 3: Editar equipe** (3 min):
   - [ ] Ir para Settings
   - [ ] Alterar nome
   - [ ] Blur do input
   - [ ] Toast de sucesso
   - [ ] F5 e verificar persistência

5. **Fluxo crítico 4: Deletar equipe** (2 min):
   - [ ] Clicar "Deletar equipe"
   - [ ] Digitar nome para confirmar
   - [ ] Equipe deletada
   - [ ] Redirecionado para /teams

6. **Abas novas** (2 min):
   - [ ] Trainings carrega
   - [ ] Stats carrega
   - [ ] Athletes/Members seção visível

**Se TUDO passou**: ✅ **STAGING VALIDADO - PRONTO PARA PRODUÇÃO**

**Se ALGO falhou**: ❌ **ROLLBACK IMEDIATO**

---

## Fase 6: Monitoramento Pós-Deploy (Primeiras 24h)

### 6.1. Métricas a Monitorar

- **Erros de Frontend**:
  - Console errors em Sentry/LogRocket
  - Taxa de erro de API calls
  - Páginas com 404/500

- **Erros de Backend**:
  - API errors (500, 400, 403, 404)
  - Latência de endpoints `/teams/*`
  - Taxa de sucesso de operações CRUD

- **Performance**:
  - Tempo de carregamento de `/teams`
  - Tempo de resposta de POST /teams
  - Core Web Vitals (LCP, FID, CLS)

### 6.2. Alertas Críticos

Configurar alertas para:
- ❌ Taxa de erro de `/teams` > 5%
- ❌ Latência de API `/teams` > 3s
- ❌ Usuários não conseguem criar equipes (conversão < 80%)

---

## Resumo Executivo

### Pré-Requisitos para Deploy em Staging

| Fase | Critério | Status |
|------|----------|--------|
| **1. Validação Local** | Suite completa passou (100%) | ⬜ |
| **2. Smoke Tests** | 5/5 testes críticos passando | ⬜ |
| **3. Regressão** | Sem regressões detectadas | ⬜ |
| **4. Documentação** | Docs atualizados | ⬜ |
| **5. Segurança** | Checklist de segurança completo | ⬜ |

### Comando de Validação Final (All-in-One)

```powershell
# Executar ANTES de fazer deploy
.\tests\e2e\run-teams-suite.ps1 && `
npx playwright test tests/e2e/smoke-tests.spec.ts --project=chromium --workers=1 --retries=0 && `
Write-Host "`n✅ MÓDULO TEAMS VALIDADO - PRONTO PARA STAGING!" -ForegroundColor Green
```

### Critério GO/NO-GO

**GO para Staging** se:
- ✅ Suite completa passou (100%)
- ✅ Smoke tests 5/5
- ✅ Sem regressões
- ✅ Checklist técnico completo
- ✅ Checklist de produto completo

**NO-GO (Adiar Deploy)** se:
- ❌ Qualquer teste crítico falhando
- ❌ Regressões detectadas
- ❌ Problemas de segurança não resolvidos
- ❌ Documentação incompleta

---

## Próximos Passos (Pós-Staging)

Após validação bem-sucedida em staging por **3-7 dias**:

1. **Coletar feedback de QA/Product**
2. **Monitorar métricas de uso**
3. **Ajustar com base em bugs encontrados**
4. **Preparar deploy para produção** (repetir este plano adaptado)

---

## Contatos de Emergência

Em caso de problemas críticos em staging:

- **Tech Lead**: [nome]
- **DevOps**: [nome]
- **Product Owner**: [nome]

**Procedimento de Rollback**:
```bash
# Reverter deploy
git revert <commit-do-deploy>
git push origin main

# CI/CD faz rollback automático
```

---

**Última atualização**: 2026-01-11
**Responsável**: Claude (Assistente)
**Revisão**: Pendente (Time de Engenharia)
