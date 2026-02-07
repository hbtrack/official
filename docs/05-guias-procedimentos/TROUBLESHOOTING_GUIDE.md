<!-- STATUS: NEEDS_REVIEW -->

# E2E Tests - Troubleshooting Guide

**Última Atualização**: 2026-01-13
**Contexto**: Baseado nas Runs 1-10 e problemas resolvidos

---

## 🔍 Diagnóstico Rápido

### Sintoma: testID não encontrado (TimeoutError)

**NÃO ASSUMA que o testID está faltando!** Primeiro verifique:

#### 1. Capture Screenshot
```bash
# Screenshot automático em test-results/
npx playwright test --headed
```

**Análise**:
- ✅ Se mostra o componente esperado → testID realmente falta
- ❌ Se mostra 404/erro → problema de autenticação/roteamento

#### 2. Verifique o Component Code
```bash
cd "src/components" && grep -r "data-testid=\"seu-testid\"" .
```

**Resultado**:
- Encontrou → problema é AUTENTICAÇÃO ou ROTEAMENTO
- Não encontrou → problema é testID faltando

#### 3. Check Console Logs
```typescript
// Adicione nos componentes:
console.log('[ComponentName] Renderizando com props:', props);
```

**Onde ver logs**:
- Client Components → Browser console (DevTools)
- Server Components → Next.js terminal

---

## 🐛 Problemas Comuns & Soluções

### 1. "testID não encontrado" mas testID existe

**Causa**: Página errada sendo renderizada (404, erro, loading infinito)

**Diagnóstico**:
```typescript
// No teste, adicione antes do expect:
await page.screenshot({ path: 'debug-screenshot.png' });
console.log('URL atual:', page.url());
console.log('HTML:', await page.content());
```

**Soluções**:
- 404 Page → Problema de autenticação ou ID inválido
- Loading infinito → API não responde, verificar network tab
- Página em branco → JavaScript error, verificar console

**Exemplo Real (Run 10)**:
```
Sintoma: testID "team-overview-tab" não encontrado
Screenshot: Mostrou 404 page
Causa: Server Component fetch SSR sem cookies → 401 → notFound()
Solução: Migrar para client-side fetch
```

---

### 2. 401 Unauthorized em E2E Tests

**Causa**: Cookies não sendo incluídos nas requests

**Diagnóstico**:
```typescript
// No teste:
const cookies = await context.cookies();
console.log('Cookies:', cookies);
```

**Cenários**:

#### A) Browser → Next.js (Client-side)
✅ **Funciona automaticamente**
- Browser inclui cookies em todas as requests

#### B) Browser → Next.js → Backend (SSR)
❌ **NÃO funciona automaticamente**
- Server-to-server fetch não inclui cookies
- Solução: Usar client-side fetch OU forward manualmente

**Código**:
```typescript
// ❌ BROKEN (SSR)
export default async function Page() {
  const data = await serverApiClient.get('/api/data'); // No cookies!
  return <Component data={data} />;
}

// ✅ WORKING (Client-side)
'use client';
export default function Component() {
  useEffect(() => {
    fetch('/api/data'); // Browser includes cookies automatically
  }, []);
}
```

---

### 3. 409 Conflict - Database Constraint

**Causa**: Violação de constraint única ou foreign key

**Diagnóstico**:
```sql
-- Verificar constraint:
SELECT constraint_name, constraint_type
FROM information_schema.table_constraints
WHERE table_name = 'sua_tabela';
```

**Exemplo Real (Run 7)**:
```
Error: 409 - team_memberships constraint violation
Causa: session_type = 'tecnico' (inválido)
Constraint: session_type IN ('quadra', 'fisico', 'video', 'reuniao', 'teste')
Solução: Usar valores válidos da constraint
```

**Prevenção**:
```typescript
// Sempre verificar migrations antes de criar payloads:
// migrations/versions/xxx_add_training_sessions.py
enum_type = sa.Enum('quadra', 'fisico', 'video', 'reuniao', 'teste', ...)

// Usar no teste:
const payload = {
  session_type: 'quadra' // ✅ Valor válido
  // session_type: 'tecnico' // ❌ Inválido
};
```

---

### 4. Seed E2E - IDs Inconsistentes

**Causa**: IDs hard-coded diferentes entre seed e testes

**Diagnóstico**:
```bash
# Verificar IDs no seed:
cd scripts && grep -n "e2e00000" seed_e2e.py

# Verificar IDs nos testes:
cd tests/e2e && grep -rn "e2e00000" .
```

**Solução**:
```typescript
// Centralizar IDs em um arquivo:
// tests/e2e/shared-data.ts
export const E2E_IDS = {
  TEAM: 'e2e00000-0000-0000-0004-000000000001',
  ADMIN_USER: 'e2e00000-0000-0000-0001-000000000001',
  // ...
};

// Usar nos testes:
import { E2E_IDS } from './shared-data';
await page.goto(`/teams/${E2E_IDS.TEAM}/overview`);
```

---

### 5. TypeScript Errors Após Mudanças

**Causa**: Tipos não compatíveis após refactor

**Diagnóstico**:
```bash
npx tsc --noEmit 2>&1 | grep "error TS"
```

**Soluções Comuns**:

#### A) Nullable Types
```typescript
// ❌ Error: Type 'Team | null' is not assignable to 'Team'
const team = currentTeam;

// ✅ Fix: Type assertion após verificação
if (!currentTeam) return <Loading />;
const team = currentTeam as Team;
```

#### B) SetState Types
```typescript
// ❌ Error: Type 'Team' is not assignable to 'SetStateAction<Team | null>'
setTeam(teamData);

// ✅ Fix: Cast explícito
setTeam(teamData as Team);
```

---

### 6. Next.js Cache - Mudanças Não Aparecem

**Causa**: Next.js cache de componentes/rotas

**Soluções**:
```bash
# 1. Hard restart
# Ctrl+C no terminal do Next.js
npm run dev

# 2. Clear .next cache
rm -rf .next
npm run dev

# 3. Clear browser cache
# DevTools → Network → Disable cache
```

---

### 7. Playwright Storage State - Token Expirado

**Causa**: Token JWT expirado no storage state

**Diagnóstico**:
```typescript
// Verificar storage state:
const storageState = JSON.parse(
  fs.readFileSync('playwright/.auth/admin.json', 'utf-8')
);
console.log('Cookies:', storageState.cookies);
```

**Solução**:
```bash
# Re-executar setup:
npx playwright test tests/e2e/setup/auth.setup.ts

# Ou deletar storage states:
rm -rf playwright/.auth/*.json
```

---

## 🛠️ Debugging Tools

### 1. Playwright Inspector
```bash
npx playwright test --debug
```

**Uso**:
- Pause execution
- Inspect locators
- Step through test

### 2. Headed Mode
```bash
npx playwright test --headed
```

**Uso**:
- Ver o que o browser está fazendo
- Inspecionar elementos
- Ver network requests

### 3. Trace Viewer
```bash
npx playwright test --trace on
npx playwright show-trace trace.zip
```

**Uso**:
- Timeline de ações
- Screenshots automáticos
- Network logs
- Console logs

### 4. Video Recording
```typescript
// playwright.config.ts
use: {
  video: 'on', // ou 'retain-on-failure'
}
```

---

## 📋 Checklist de Debugging

Quando um teste falha, siga esta ordem:

- [ ] 1. Capture screenshot
- [ ] 2. Check se página certa está renderizada
- [ ] 3. Verify URL está correta
- [ ] 4. Check console logs (browser + Next.js)
- [ ] 5. Inspect network requests (status codes)
- [ ] 6. Verify cookies estão presentes
- [ ] 7. Check database state (se CRUD test)
- [ ] 8. Verify testID existe no código
- [ ] 9. Check TypeScript errors
- [ ] 10. Try re-running auth setup

---

## 🔗 Referências Rápidas

### Logs Importantes
- **Run 10**: [SSR_COOKIE_FIX.md](SSR_COOKIE_FIX.md) - Problema de autenticação SSR
- **Run 8**: [RUN_LOG.md](RUN_LOG.md#run-8) - Problema 409 resolvido
- **Run 7**: [RUN7_SUMMARY.md](RUN7_SUMMARY.md) - session_type constraint

### Comandos Úteis
```bash
# Run específico teste:
npx playwright test tests/e2e/teams/teams.contract.spec.ts -g "overview"

# Com debug:
npx playwright test --debug --headed

# Apenas um browser:
npx playwright test --project=chromium

# Re-executar apenas falhados:
npx playwright test --last-failed

# Gerar HTML report:
npx playwright test --reporter=html
npx playwright show-report
```

---

## 💡 Dicas Pro

### 1. Sempre Capture Context
```typescript
test('meu teste', async ({ page }) => {
  // Antes de assert que vai falhar:
  console.log('URL:', page.url());
  console.log('Title:', await page.title());
  await page.screenshot({ path: 'debug.png' });

  // Agora seu assert:
  await expect(page.locator('[data-testid="foo"]')).toBeVisible();
});
```

### 2. Use waitForLoadState
```typescript
// Aguardar página carregar completamente:
await page.goto('/teams');
await page.waitForLoadState('domcontentloaded');
await page.waitForLoadState('networkidle'); // Aguarda requests
```

### 3. Timeouts Customizados
```typescript
// Para testes lentos (SSR, etc):
test('teste lento', async ({ page }) => {
  test.setTimeout(60000); // 60 segundos

  await expect(page.locator('[data-testid="foo"]'))
    .toBeVisible({ timeout: 30000 }); // 30s para este locator
});
```

### 4. Retry Strategy
```typescript
// playwright.config.ts
export default defineConfig({
  retries: process.env.CI ? 2 : 0, // Retry no CI, não em local
});
```

---

## 🎓 Lessons from Run 1-10

1. ✅ **Screenshot primeiro** - Revela o que realmente está renderizado
2. ✅ **Console logs são seus amigos** - Server vs Client component logs
3. ✅ **TypeScript não mente** - Fix TS errors antes de rodar tests
4. ✅ **Migrations são contrato** - Sempre consultar antes de criar payloads
5. ✅ **Padrões consistentes** - Se Members funciona, replique o padrão
6. ✅ **E2E revela edge cases** - Comportamento diferente de dev manual
7. ✅ **Restart Next.js após mudanças** - Cache pode esconder problemas
8. ✅ **Auth setup é crucial** - Tokens expirados = 401s misteriosos
9. ✅ **Database seed importa** - IDs consistentes entre seed e testes
10. ✅ **Debug iterativamente** - Um problema de cada vez

---

*Guia de troubleshooting mantido por Claude Code - 2026-01-13*
