<!-- STATUS: DEPRECATED | arquivado -->

# MANUAL CANÔNICO — EXECUÇÃO E2E (PLAYWRIGHT) — HB TRACK (FRONTEND)

Este manual é a fonte única para rodar a suíte E2E de forma determinística (sem falso positivo), com ambiente controlado e ordem canônica.

---

## 1) Objetivo

Garantir que:

* a suíte rode com **mesmo resultado** em execuções consecutivas;
* falhas apontem **onde** está o problema (infra vs contrato vs funcional);
* não exista “resolver flake” com `waitForTimeout`, `networkidle`, ou asserts fracos.

---

## 2) Contexto do sistema (o que os testes assumem)

### 2.1 Rotas e guardas

* Rotas protegidas (ex.: `/teams/**`) **sem autenticação** redirecionam para:

  * `/signin?callbackUrl=<pathname+search>`
* O `callbackUrl` deve preservar exatamente `pathname + search`.

### 2.2 Contratos de erro (marcadores estáveis)

* 404 deve renderizar **sempre**: `data-testid="app-404"`
* 403 deve renderizar **sempre**: `data-testid="app-403"` (se existir no produto; se ainda não existe, é requisito para o contrato)

### 2.3 Roots por página (determinismo de UI)

Cada página/aba crítica deve ter um root estável em todos estados (loading/empty/ok):

* `/teams` → `data-testid="teams-dashboard"` (exemplo)
* `/teams/:id/overview` → `data-testid="team-overview-tab"`
* `/teams/:id/members` → `data-testid="team-members-tab"`
* `/teams/:id/settings` → `data-testid="teams-settings-root"`

A lista oficial fica em `tests/e2e/TESTIDS_MANIFEST.md`.

---

## 3) Ambiente canônico (obrigatório)

### 3.1 Serviços que precisam estar no ar

* **Postgres (E2E)**: `localhost:5433` (Docker Compose)
* **Backend**: `http://127.0.0.1:8000`
* **Frontend**: `http://localhost:3000`

### 3.2 Banco E2E dedicado

* Usar DB **exclusiva**: `hb_track_e2e`
* Antes de rodar E2E: **reset do schema + migrations + seed mínimo versionado**
* Seed mínimo inclui a organização **IDEC** (do seu seed mínimo).

### 3.3 Variáveis de ambiente (Frontend)

No `Hb Track - Fronted/.env.test` (ou equivalente):

* `PLAYWRIGHT_BASE_URL=http://localhost:3000`
* `BACKEND_BASE_URL=http://127.0.0.1:8000` (se helpers usam API)
* `E2E=1`
* `E2E_RUN_ID=<id-fixo-por-execução>` (ex.: `local-001`)

Credenciais E2E (usadas no setup):

* `TEST_ADMIN_EMAIL=...`
* `TEST_ADMIN_PASSWORD=...`
* (opcional) demais roles se seu setup gera múltiplos storageStates:

  * `TEST_DIRIGENTE_EMAIL`, `TEST_COACH_EMAIL`, etc.

**Regra:** se alguma credencial obrigatória não existir, `auth.setup.ts` deve falhar.

### 3.4 Variáveis de ambiente (Backend)

* `E2E=1`
* `DATABASE_URL=postgresql+psycopg2://hbtrack_dev:hbtrack_dev_pwd@localhost:5433/hb_track_e2e`

---

## 4) Preparação do banco (canônico)

### 4.1 Criar DB (uma vez)

```powershell
cd "C:\HB TRACK\infra"
docker compose exec -T postgres psql -U hbtrack_dev -d postgres -c "CREATE DATABASE hb_track_e2e;"
```

### 4.2 Reset + migrations (sempre antes da suíte E2E)

Fluxo canônico (exemplo de intenção):

1. dropar schema (ou recriar DB)
2. rodar `alembic upgrade head`
3. rodar `seed_e2e.py` (seed mínimo versionado)

Você já validou que `python -m alembic upgrade head` funciona a partir de `Hb Track - Backend\db`.

**Recomendação:** encapsular isso em um script único (ex.: `scripts/reset_e2e_db.ps1`) e usar sempre.

---

## 5) Estrutura de camadas dos testes (3 níveis)

### Camada 1 — GATE (infra)

Bloqueia tudo se falhar.

* `tests/e2e/health.gate.spec.ts`

Deve validar somente:

* backend responde (`/health` ou `/docs`)
* frontend carrega `/signin`
* rota protegida sem auth redireciona para `/signin?callbackUrl=...`

Proibido: login completo aqui.

### Camada 2 — CONTRATO (navegação + erros)

Valida comportamento “oficial” de redirects/401/404/roots.

* `tests/e2e/teams/teams.contract.spec.ts`

  * (recomendado separar internamente em blocos: unauth e auth)

### Camada 3 — FUNCIONAIS (fluxos)

Testes de features:

* `teams.crud.spec.ts`
* `teams.states.spec.ts`
* `teams.invites.spec.ts`
* `teams.welcome.spec.ts`
* `teams.rbac.spec.ts`

---

## 6) Autenticação canônica (storageState)

### 6.1 Setup

* `tests/e2e/setup/auth.setup.ts` gera:

  * `playwright/.auth/admin.json`
  * `playwright/.auth/dirigente.json`
  * etc.

### 6.2 Regras

* Specs autenticadas **nunca** fazem login por UI.
* Specs autenticadas sempre usam `storageState` correspondente.
* Specs unauth usam **projeto** com `storageState` vazio.

---

## 7) Execução canônica (ordem que não muda)

### Ordem oficial

1. Reset DB + migrations + seed mínimo (backend)
2. Subir backend (E2E=1 apontando para hb_track_e2e)
3. Subir frontend (E2E=1)
4. Rodar Playwright na ordem:

   1. `health.gate`
   2. `auth.setup`
   3. `teams.contract`
   4. `teams.crud`
   5. `teams.states`
   6. `teams.invites`
   7. `teams.welcome`
   8. `teams.rbac`

---

## 8) Comandos canônicos (PowerShell — determinístico)

Sempre usar:

* `--workers=1`
* `--retries=0`

### 8.1 Gate

```powershell
cd "c:\HB TRACK\Hb Track - Fronted"
npx playwright test tests/e2e/health.gate.spec.ts --project=chromium --workers=1 --retries=0
```

### 8.2 Auth setup

```powershell
cd "c:\HB TRACK\Hb Track - Fronted"
npx playwright test tests/e2e/setup/auth.setup.ts --project=setup --workers=1 --retries=0
```

### 8.3 Contrato (Teams)

```powershell
cd "c:\HB TRACK\Hb Track - Fronted"
npx playwright test tests/e2e/teams/teams.contract.spec.ts --project=chromium --workers=1 --retries=0
```

### 8.4 Funcionais (cada spec isolada)

```powershell
cd "c:\HB TRACK\Hb Track - Fronted"

npx playwright test tests/e2e/teams/teams.crud.spec.ts    --project=chromium --workers=1 --retries=0
npx playwright test tests/e2e/teams/teams.states.spec.ts  --project=chromium --workers=1 --retries=0
npx playwright test tests/e2e/teams/teams.invites.spec.ts --project=chromium --workers=1 --retries=0
npx playwright test tests/e2e/teams/teams.welcome.spec.ts --project=chromium --workers=1 --retries=0
npx playwright test tests/e2e/teams/teams.rbac.spec.ts    --project=chromium --workers=1 --retries=0
```

### 8.5 Validação final “hard mode” (3x seguidas)

Só considerar determinístico se passar 3 vezes seguidas:

```powershell
cd "c:\HB TRACK\Hb Track - Fronted"

npx playwright test tests/e2e/teams --project=chromium --workers=1 --retries=0
npx playwright test tests/e2e/teams --project=chromium --workers=1 --retries=0
npx playwright test tests/e2e/teams --project=chromium --workers=1 --retries=0
```

---

## 9) Regras de execução do agente (para não criar falso positivo)

### 9.1 Parar na primeira falha (regra operacional)

* Se qualquer teste falhar: **parar**, debugar, corrigir, reexecutar o mínimo, e só então continuar.

### 9.2 O que é permitido esperar

* `waitForURL`
* `expect(locator).toBeVisible()`
* `domcontentloaded` quando fizer sentido

Proibido:

* `waitForTimeout`
* `networkidle` como pronto

### 9.3 Assertions mínimas por navegação

Sempre validar:

1. URL final
2. root `data-testid`
3. 1 marcador adicional (título fixo, botão principal, input principal)

---

## 10) Diagnóstico quando falhar

1. Reproduzir o teste isolado (mesmo project, `--workers=1 --retries=0`)
2. Abrir evidências:

* `test-results/**/trace.zip`
* screenshot/vídeo

3. Classificar:

* **Infra** (cai no Gate)
* **Contrato** (redirect/404/roots)
* **Funcional** (CRUD/states/invites/welcome/rbac)

4. Corrigir (sem “afrouxar”):

* bug de código: ajustar middleware/rotas/handlers/testids
* bug de teste: seletor/sincronização/dado errado (nunca relaxar assert)

---

## 11) Políticas essenciais (determinismo real)

* E2E sempre contra `hb_track_e2e`
* Antes da suíte: reset + migrations + seed mínimo
* Dados criados em teste devem ter prefixo (`E2E-...`) e cleanup
* Global teardown é “segunda linha”, mas o reset do DB é o que zera crescimento e elimina dependência de soft delete

---

