<!-- STATUS: NEEDS_REVIEW -->

# MANUAL CANÔNICO DE EXECUÇÃO E2E (PLAYWRIGHT) — HB TRACK (FRONTEND)

Este manual é a fonte única para um agente executar a suíte E2E corretamente, de forma determinística, sem falsos positivos e sem “afrouxar” asserts.

---

## Objetivo e regra de ouro

**Objetivo:** executar e manter testes E2E **repetíveis** (mesmo resultado em execuções consecutivas) para o módulo **Teams** e infra básica.

**Regra de ouro:**
Quando um teste falha, **não ajuste o teste para “passar”**. Primeiro confirme o **comportamento oficial** (contrato). Depois corrija **o código** ou **o teste**, mas sempre preservando asserts fortes.

---

## Estrutura real do repositório (atual)

Dentro de `Hb Track - Fronted/`:

* `tests/e2e/teams/` (suíte principal de Teams)
* `tests/e2e/setup/` (configurações globais, ex.: auth)
* `tests/e2e/health.spec.ts` (health check básico)
* `tests/e2e/tests_log/` (logs de execução e mudanças)
* `tests/e2e/temas_gaps/` (suíte de gaps, complementar) 
 * `tests/e2e/helpers/` (helpers compartilhados)
* `tests/e2e/teams_rules/teams-CONTRACT` (contrato canônico)
* `tests/e2e/TESTIDS_MANIFEST.md` (contrato de `data-testid`)

* Saídas:

  * `test-results/` (traces, screenshots, vídeos)
  * `playwright-report/`

---

## Ordem canônica de execução (não negocia)

## Pré-requisitos (sempre validar antes de rodar)

### Serviços

* Frontend acessível em `PLAYWRIGHT_BASE_URL` (default: `http://localhost:3000`)
* Backend acessível em `BACKEND_BASE_URL` (se seus helpers usam API)

### Variáveis de ambiente (obrigatórias)

No Frontend, garantir (em `.env.local` ou `.env.test`, conforme sua prática):

* `PLAYWRIGHT_BASE_URL=http://localhost:3000`
* `TEST_USER_EMAIL=...`
* `TEST_USER_PASSWORD=...`
* (se aplicável) `BACKEND_BASE_URL=http://localhost:8000`
* Recomendado para rastreabilidade:

  * `E2E=1`
  * `E2E_RUN_ID=<id-fixo-por-execução>` (ex: `local-001`)

**Regra:** `tests/e2e/setup/auth.setup.ts` deve **falhar** se `TEST_USER_EMAIL/PASSWORD` não existirem.

## Preparação do banco (OBRIGATÓRIO para suíte determinística)

### Regra canônica

Antes de rodar qualquer E2E (incluindo health.spec.ts), o agente deve garantir um banco hb_track_e2e limpo, com:

* reset (schema limpo via drop/create do banco)

* alembic upgrade head

* seed_e2e.py aplicado

* Se qualquer etapa falhar, parar e corrigir antes de continuar.

### 5.1 Comandos canônicos (Docker Compose + Alembic + Seed)

Executar no host (PowerShell), na pasta do compose:

cd "C:\HB TRACK\infra"

# (Re)criar o banco hb_track_e2e (idempotente)
docker compose exec -T postgres psql -U hbtrack_dev -d postgres -c "DROP DATABASE IF EXISTS hb_track_e2e WITH (FORCE);"
docker compose exec -T postgres psql -U hbtrack_dev -d postgres -c "CREATE DATABASE hb_track_e2e;"

Depois, aplicar migrações e seed no backend:

cd "C:\HB TRACK\Hb Track - Backend\db"

# Alembic (SQLAlchemy)
$env:DATABASE_URL="postgresql+psycopg2://hbtrack_dev:hbtrack_dev_pwd@localhost:5433/hb_track_e2e"
python -m alembic upgrade head

# Seed (psycopg2 puro exige DSN sem "+psycopg2")
$env:PG_DSN="postgresql://hbtrack_dev:hbtrack_dev_pwd@localhost:5433/hb_track_e2e"
python ..\scripts\seed_e2e.py

## Regra de conexão no seed (evitar DSN inválido)

Se seed_e2e.py usa psycopg2.connect(...), ele deve receber PG_DSN no formato:

postgresql://user:pass@host:port/db

e nunca postgresql+psycopg2://....

### Estratégia: seed/reset do banco antes da suíte

* Use seed mínimo versionado no backend.
* Indicada se o time quer máxima previsibilidade e não se importa com tempo.
* Use IDEC como base (mais simples), mas **isole dados E2E por prefixo** (`E2E-...`) para permitir cleanup.

## Reset do banco hb_track_e2e (schema limpo)

cd "C:\HB TRACK\infra"

docker compose ps

docker compose exec -T postgres psql -U hbtrack_dev -d postgres -c "DROP DATABASE IF EXISTS hb_track_e2e WITH (FORCE);"
docker compose exec -T postgres psql -U hbtrack_dev -d postgres -c "CREATE DATABASE hb_track_e2e;"

* Migrations (alembic) no banco E2E
cd "C:\HB TRACK\Hb Track - Backend\db"
$env:DATABASE_URL="postgresql+psycopg2://hbtrack_dev:hbtrack_dev_pwd@localhost:5433/hb_track_e2e"
python -m alembic upgrade head

* Seed E2E (psycopg2 DSN sem "+psycopg2")
cd "C:\HB TRACK\Hb Track - Backend"
$env:PG_DSN="postgresql://hbtrack_dev:hbtrack_dev_pwd@localhost:5433/hb_track_e2e"
python scripts/seed_e2e.py

Regras: Se falhar em qualquer etapa acima: parar e corrigir antes de rodar Playwright.

## Rodar no modo determinístico (um browser)

Sempre usar:

--workers=1

--retries=0

cd "c:\HB TRACK\Hb Track - Fronted"

## Validação final (3x por browser)

Só considerar “determinístico” se passar 3 vezes seguidas (por browser), com --workers=1 --retries=0:

cd "c:\HB TRACK\Hb Track - Fronted"

# Chromium (3x)
npx playwright test tests/e2e/teams --project=chromium --workers=1 --retries=0
npx playwright test tests/e2e/teams --project=chromium --workers=1 --retries=0
npx playwright test tests/e2e/teams --project=chromium --workers=1 --retries=0

# Firefox (3x)
npx playwright test tests/e2e/teams --project=firefox --workers=1 --retries=0
npx playwright test tests/e2e/teams --project=firefox --workers=1 --retries=0
npx playwright test tests/e2e/teams --project=firefox --workers=1 --retries=0

# WebKit (3x)
npx playwright test tests/e2e/teams --project=webkit --workers=1 --retries=0
npx playwright test tests/e2e/teams --project=webkit --workers=1 --retries=0
npx playwright test tests/e2e/teams --project=webkit --workers=1 --retries=0


## Regra de diagnóstico quando falhar

Quando um teste falhar:

1. **Reproduzir o mesmo teste** isolado:

   * mesmo `--project`
   * `--workers=1 --retries=0`
2. Abrir os artefatos:

   * `test-results/<pasta>/trace.zip`
   * screenshot/vídeo
3. Classificar a falha:

   * **Bug no código**: URL final está errada, redirect não acontece, root não aparece porque tela não renderizou.
   * **Bug no teste**: seletor errado, espera incorreta, clicou no item errado (ex.: “primeiro card”).
4. Corrigir:

   * Se for navegação/redirect: usar `helpers/redirectDebug.ts`
   * Se for UI pronta: garantir `data-testid` root em todos estados
   * Se for lista: selecionar pelo **nome/ID criado pelo teste**, nunca por `.first()`

**Proibido:** resolver flake aumentando retry, adicionando `waitForTimeout`, ou relaxando asserts.

### Sinais estáveis

* Sempre validar:

  1. `toHaveURL(...)` (URL final)
  2. `root testid` visível
  3. 1 marcador adicional (ex.: título fixo ou botão principal)

### Seletores (ordem)

1. `getByTestId`
2. `getByRole`
3. `getByLabel`
4. `getByText` (só texto fixo)

### Esperas permitidas

* `waitForURL`
* `expect(...).toBeVisible()`
* `domcontentloaded` quando fizer sentido
* Nunca usar `networkidle` como “pronto”.

---

## Checklist de “pronto para rodar” (gate rápido)

Antes de rodar Teams:

* `health.spec.ts` passou
* `auth.setup.ts` passou
* `playwright/.auth/*.json` existe e contém cookie/token esperado
* Manifesto de testids atualizado
* Seed/reset ou estratégia API escolhida e aplicada consistentemente

---

##  Documentação de execução e correções

## Sempre registrar no “Run Log” por execução

Após cada comando `npx playwright test ...`, o AGENTE deve criar/atualizar um arquivo único, por exemplo:

* `Hb Track - Fronted\tests\e2e\tests_log\RUN_LOG.md`

Conteúdo mínimo por rodada:

* Data/hora
* Comando exato executado
* Projeto (`chromium/firefox/webkit/unauthenticated/setup`)
* Resultado (pass/fail) + quantos testes
* Se falhou: nome do teste + caminho da pasta em `test-results/` do failure
* Ação tomada (código ou teste) + arquivos alterados
* Comando de reexecução usado para confirmar

## Sempre registrar “Change Log” por correção

Para cada correção aplicada, adicionar uma seção em:

* `Hb Track - Fronted\tests\e2e\tests_log\CHANGELOG_E2E.md`

Mínimo:
* Motivo (qual teste falhou e por quê)
* Classificação: bug de código vs bug de teste
* Mudança por arquivo (descrição curta)
* Evidência (qual assert passou depois + re-run)

## Sempre atualizar contrato quando comportamento oficial mudar

Se o AGENTE precisar alterar middleware/redirect/404/testid, ele deve atualizar:

* `docs/modules/teams-CONTRACT.md` (ou o contrato canônico que você usar)
* `Hb Track - Fronted\tests\e2e\tests_log\TESTIDS_MANIFEST.md` (se mexeu em testid)

Sem atualizar contrato/manifesto, a correção fica “solta” e você volta a ter flake mais tarde.

## Sempre anexar evidências (sem copiar arquivos enormes)

No log, apenas referenciar:

* caminho do trace: `test-results/.../trace.zip`
* screenshot/video se existir
* URL final observada (quando o erro for redirect)


