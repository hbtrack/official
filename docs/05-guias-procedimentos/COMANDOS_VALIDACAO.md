<!-- STATUS: NEEDS_REVIEW -->

# 🚀 Comandos Prontos - Validação Teams para Staging

## Copy & Paste - Validação Completa

### 1️⃣ Validação Local (30 min)

```powershell
# Ir para diretório do projeto
cd "C:\HB TRACK\Hb Track - Fronted"

# Executar suite completa (ordem canônica)
.\tests\e2e\run-teams-suite.ps1

# Se passou ✅, continuar para smoke tests
```

---

### 2️⃣ Smoke Tests (15 min)

```powershell
# Executar 5 testes críticos
npx playwright test tests/e2e/smoke-tests.spec.ts --project=chromium --workers=1 --retries=0

# ✅ Esperado: 5/5 testes passando
```

---

### 3️⃣ Build Produção (5 min)

```powershell
# Build de produção
npm run build

# ✅ Esperado: Build successful
```

---

### 4️⃣ Linter (2 min)

```powershell
# Rodar linter
npm run lint

# ✅ Esperado: 0 errors (warnings OK)
```

---

### 5️⃣ Comando All-in-One (Validação Completa)

```powershell
# Rodar tudo de uma vez
.\tests\e2e\run-teams-suite.ps1 && `
npx playwright test tests/e2e/smoke-tests.spec.ts --project=chromium --workers=1 --retries=0 && `
npm run build && `
npm run lint && `
Write-Host "`n✅✅✅ VALIDAÇÃO COMPLETA - GO PARA STAGING! ✅✅✅" -ForegroundColor Green -BackgroundColor DarkGreen

# ✅ Se TUDO passar: Deploy liberado
# ❌ Se ALGO falhar: Corrigir e repetir
```

---

## Comandos de Deploy

### 1️⃣ Commit e Push (se ainda não fez)

```powershell
# Adicionar arquivos
git add .

# Commit
git commit -m "feat(teams): adiciona abas trainings, stats e athletes

- Aba Trainings: CRUD de treinos via API/UI
- Aba Stats: estatísticas de equipe
- Athletes: gerenciamento de registrations
- Integração completa teams_gaps → estrutura canônica
- Eliminadas duplicatas (387 → 150 testes únicos)
- Smoke tests criados (5 críticos)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"

# Push para main (ou develop)
git push origin main
```

---

### 2️⃣ Aguardar CI/CD (10 min)

```bash
# CI/CD automaticamente:
# 1. Roda testes
# 2. Faz build
# 3. Deploy em staging

# Acompanhar logs no GitHub Actions / GitLab CI
```

---

## Validação Pós-Deploy em Staging

### 1️⃣ Health Check (2 min)

```powershell
# Verificar API
curl https://api-staging.hbtrack.com/api/v1/health

# ✅ Esperado: 200 OK
```

```powershell
# Verificar Frontend
curl https://staging.hbtrack.com

# ✅ Esperado: 200 OK
```

---

### 2️⃣ Smoke Tests em Staging (10 min)

```powershell
# Configurar ambiente para staging
$env:NEXT_PUBLIC_API_URL = "https://api-staging.hbtrack.com"
$env:NEXT_PUBLIC_APP_URL = "https://staging.hbtrack.com"

# Executar smoke tests contra staging
npx playwright test tests/e2e/smoke-tests.spec.ts `
  --project=chromium `
  --workers=1 `
  --retries=1

# ✅ Esperado: 5/5 testes passando
```

---

### 3️⃣ Validação Manual em Staging (3 min)

```
1. Abrir: https://staging.hbtrack.com
2. Fazer login com credenciais de teste
3. Ir para /teams
4. Criar 1 equipe → Deve funcionar
5. Equipe aparece na lista → Deve aparecer
```

---

## Comandos de Rollback (Se Necessário)

### ❌ Se Algo Falhar em Staging

```powershell
# Reverter último commit
git log -1
# Copiar hash do commit

git revert <commit-hash>
git push origin main

# CI/CD faz rollback automático
```

---

## Comandos de Debug

### Debug de Teste Específico

```powershell
# Rodar 1 spec com debug
npx playwright test tests/e2e/teams/teams.crud.spec.ts `
  --project=chromium `
  --workers=1 `
  --retries=0 `
  --debug

# Abre inspetor do Playwright
```

---

### Ver Relatório HTML de Testes

```powershell
# Gerar relatório HTML
npx playwright test tests/e2e/teams --reporter=html

# Abrir relatório
npx playwright show-report
```

---

### Ver Screenshots/Vídeos de Falhas

```powershell
# Screenshots ficam em:
ls test-results/**/*.png

# Vídeos ficam em:
ls test-results/**/*.webm
```

---

## Comandos de Monitoramento (Pós-Deploy)

### Ver Logs da API (Staging)

```bash
# Exemplo com Kubernetes
kubectl logs -f deployment/api-staging -n staging

# Exemplo com Docker
docker logs -f api-staging
```

---

### Ver Errors no Sentry

```
# Acessar Sentry
https://sentry.io/organizations/hbtrack/issues/

# Filtrar:
# - Environment: staging
# - Release: latest
# - Time: Last 1 hour
```

---

## Atalhos Rápidos

### Rodar Apenas 1 Spec

```powershell
# Contrato
npx playwright test tests/e2e/teams/teams.contract.spec.ts --project=chromium --workers=1 --retries=0

# CRUD
npx playwright test tests/e2e/teams/teams.crud.spec.ts --project=chromium --workers=1 --retries=0

# States
npx playwright test tests/e2e/teams/teams.states.spec.ts --project=chromium --workers=1 --retries=0

# RBAC
npx playwright test tests/e2e/teams/teams.rbac.spec.ts --project=chromium --workers=1 --retries=0

# Trainings (NOVO)
npx playwright test tests/e2e/teams/teams.trainings.spec.ts --project=chromium --workers=1 --retries=0

# Stats (NOVO)
npx playwright test tests/e2e/teams/teams.stats.spec.ts --project=chromium --workers=1 --retries=0

# Athletes (NOVO)
npx playwright test tests/e2e/teams/teams.athletes.spec.ts --project=chromium --workers=1 --retries=0
```

---

### Rodar Suite em Modo Headed (Ver Navegador)

```powershell
# Ver navegador durante testes
npx playwright test tests/e2e/smoke-tests.spec.ts --project=chromium --headed
```

---

### Gerar Logs Detalhados

```powershell
# Rodar com log completo
$env:DEBUG = "pw:api"
npx playwright test tests/e2e/smoke-tests.spec.ts --project=chromium > tests_debug.log 2>&1

# Ver log
cat tests_debug.log
```

---

## Checklist Pré-Deploy (Marcar ✅)

```powershell
# Copiar e marcar conforme executa:

# PRÉ-DEPLOY
Write-Host "□ Suite completa passou" -ForegroundColor Yellow
.\tests\e2e\run-teams-suite.ps1
Write-Host "✅ Suite completa passou" -ForegroundColor Green

Write-Host "□ Smoke tests 5/5" -ForegroundColor Yellow
npx playwright test tests/e2e/smoke-tests.spec.ts --project=chromium --workers=1 --retries=0
Write-Host "✅ Smoke tests 5/5" -ForegroundColor Green

Write-Host "□ Build OK" -ForegroundColor Yellow
npm run build
Write-Host "✅ Build OK" -ForegroundColor Green

Write-Host "□ Lint OK" -ForegroundColor Yellow
npm run lint
Write-Host "✅ Lint OK" -ForegroundColor Green

Write-Host "`n✅ TUDO OK - GO PARA STAGING!" -ForegroundColor Green -BackgroundColor DarkGreen
```

---

## Comandos Úteis para CI/CD

### GitHub Actions (Exemplo)

```yaml
# .github/workflows/staging-deploy.yml
name: Deploy to Staging

on:
  push:
    branches: [main]

jobs:
  test-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Node
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install dependencies
        run: npm ci

      - name: Run E2E Tests
        run: |
          npx playwright install --with-deps chromium
          npx playwright test tests/e2e/smoke-tests.spec.ts --project=chromium --workers=1 --retries=1

      - name: Build
        run: npm run build

      - name: Deploy to Staging
        run: |
          # Seu comando de deploy aqui
          # Exemplo: vercel deploy --prod
```

---

## FAQ - Comandos

### ❓ Como rodar testes em paralelo (mais rápido)?

```powershell
# NÃO RECOMENDADO para validação final, mas pode usar para dev:
npx playwright test tests/e2e/teams --project=chromium --workers=4 --retries=0

# Atenção: Pode causar race conditions
```

---

### ❓ Como ver relatório de cobertura?

```powershell
# Playwright não tem cobertura nativa E2E
# Mas você pode ver quantos testes cobrem cada feature:

npx playwright test tests/e2e/teams --list | Select-String "CRUD|States|RBAC"
```

---

### ❓ Como rodar em outro navegador?

```powershell
# Firefox
npx playwright test tests/e2e/smoke-tests.spec.ts --project=firefox

# Webkit (Safari)
npx playwright test tests/e2e/smoke-tests.spec.ts --project=webkit
```

---

## Última Checagem Antes de Deploy

```powershell
# Executar este comando FINAL:
Write-Host "`n=== CHECAGEM FINAL ===" -ForegroundColor Cyan
Write-Host "1. Suite completa..." -ForegroundColor Yellow
.\tests\e2e\run-teams-suite.ps1
if ($LASTEXITCODE -ne 0) { Write-Host "❌ BLOQUEADO" -ForegroundColor Red; exit 1 }

Write-Host "2. Smoke tests..." -ForegroundColor Yellow
npx playwright test tests/e2e/smoke-tests.spec.ts --project=chromium --workers=1 --retries=0
if ($LASTEXITCODE -ne 0) { Write-Host "❌ BLOQUEADO" -ForegroundColor Red; exit 1 }

Write-Host "3. Build..." -ForegroundColor Yellow
npm run build
if ($LASTEXITCODE -ne 0) { Write-Host "❌ BLOQUEADO" -ForegroundColor Red; exit 1 }

Write-Host "4. Lint..." -ForegroundColor Yellow
npm run lint
if ($LASTEXITCODE -ne 0) { Write-Host "❌ BLOQUEADO" -ForegroundColor Red; exit 1 }

Write-Host "`n✅✅✅ LIBERADO PARA STAGING ✅✅✅" -ForegroundColor Green -BackgroundColor DarkGreen
Write-Host "Pode fazer: git push origin main" -ForegroundColor Green
```

---

**Última atualização**: 2026-01-11
**Responsável**: Time de Engenharia

**Próximo passo**: Executar comandos e validar! 🚀
