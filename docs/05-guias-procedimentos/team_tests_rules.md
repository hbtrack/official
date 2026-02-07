<!-- STATUS: NEEDS_REVIEW -->

## Regras fundamentais para testes determinísticos com Playwright

### 1) Teste deve ser repetível

* Rodar 10 vezes seguidas e dar o mesmo resultado.
* Se depende de “ordem”, “horário”, “rede”, “cache” ou “dados existentes”, não é determinístico.

### 2) Cada teste controla o próprio estado

Escolha 1 modelo e seja consistente:

* Reset do banco antes da suíte (mais confiável), ou
* Criar dados via API por teste + cleanup obrigatório.
  Evite “usar dados que já existem”.

### 3) Assertions só em sinais estáveis

Prefira:

* URL final (`toHaveURL`)
* Elemento raiz da página/aba com `data-testid` (`toBeVisible`)
* Textos/labels estáveis (títulos fixos)
  Evite:
* layout/posicionamento
* classes CSS
* `img[alt="..."]` como base de erro
* conteúdo muito variável (listas, contagens)

### 4) Nunca use “networkidle” como pronto

* `networkidle` é frágil em SPA (polling, websockets, analytics).
  Use em vez disso:
* `await page.waitForURL(...)`
* `await expect(page.getByTestId('root')).toBeVisible()`

### 5) Não capture status HTTP via `page.goto()` em rotas do App Router

Redirecionamentos e middleware podem fazer `response` ser irrelevante.
Para 404/401/redirect, valide pela UI:

* URL final
* presença de `app-404` (ou heading 404)
* presença do formulário de login

### 6) Seletores: uma hierarquia clara

Ordem de preferência:

1. `getByTestId('...')`
2. `getByRole('button', { name: '...' })`
3. `getByLabel('...')`
4. `getByText('...')` (só se for texto fixo)
   Nunca use seletores frágeis:

* `.class > div:nth-child(2)`
* XPath
* textos que mudam (datas, números, nomes aleatórios)

### 7) Padronize “roots” por página

Para cada página/aba importante, tenha um root fixo:

* `data-testid="page-xxx-root"`
  Mesmo em loading/empty/error, esse root deve existir.
  Isso elimina flakiness de estados intermediários.

### 8) Autenticação: setup único, validado

* Um `auth.setup.ts` que faz login e salva `storageState`.
* O setup deve falhar se não tiver credenciais.
* Após login, valide que o cookie/token realmente existe.
* Testes autenticados sempre usam o `storageState`.
* Testes sem auth usam um projeto separado com storageState vazio.

### 9) Evite “try/catch para passar”

* `try/catch` genérico mascara bug e cria falso positivo.
* Se um fluxo pode ter 2 comportamentos válidos, isso tem que ser um “contrato” do sistema, não um “aceita qualquer coisa”.
  Se existir comportamento duplo, congele um e corrija o código.

### 10) Timeouts e retries não são solução

* Retry alto esconde instabilidade.
* Para ser determinístico:

  * `--retries=0` na validação final
  * `--workers=1` quando há estado compartilhado
    Se com `--workers=1` e `--retries=0` ainda falha, tem causa real.

### 11) Paralelismo só depois que estiver estável

Primeiro:

* estabiliza com `workers=1`
  Depois:
* aumenta workers e resolve conflitos (dados, sessões, rate limit).

### 12) Logs e artefatos são parte do teste

Configure e use:

* trace em falha (`trace: 'on-first-retry'` ou sempre em debug)
* screenshot/vídeo em falha
* console logs do app quando necessário (`page.on('console', ...)`)
  E principalmente: ao investigar redirect, logue as navegações (`framenavigated`).

### 13) Contrato oficial do comportamento

Antes de escrever testes, escreva o contrato:

* redirects
* 401/403/404
* fallback de rotas inválidas
* rotas canônicas
  Os testes validam o contrato; o código implementa o contrato.
  Sem contrato, você fica “ajustando teste” indefinidamente.

### 14) Uma causa por falha

Quando falhar:

1. Reproduza com `--retries=0 --workers=1`
2. Veja URL final + root esperado
3. Decida: falha é no código ou no teste?

* Se contrato diz que devia redirecionar e não redirecionou: bug de código.
* Se contrato diz que o root existe e o teste procura seletor errado: bug de teste.

### 15) Suíte mínima indispensável (ordem ideal)

1. Auth setup
2. Unauth redirect (guards/middleware)
3. Navegação canônica (lista → detalhe)
4. Tabs/rotas internas
5. Reload/F5 (sem loop)
6. 404 determinístico (id inexistente, slug inválido)
7. CRUD principal (criar/editar/deletar) via UI ou API+UI


### 16) Isole efeitos colaterais do app em modo teste

* Desative analytics, Sentry, hotkeys globais, polling agressivo, websocket, “auto refresh” quando `process.env.E2E=1`.
* Se não puder desativar, garanta que os testes não dependem de estados que esses efeitos mudam.

### 17) Congelar tempo e aleatoriedade (quando afeta UI)

* Se UI mostra “Hoje”, “há 3 minutos”, contagens ou datas: injete clock fixo em modo teste (ou abstraia para não testar isso).
* Evite gerar nomes com `Date.now()` se depois você precisa achar pelo texto; prefira um identificador fixo por teste (`E2E-<testId>`).

### 18) Banco/ambiente de teste dedicado

* Ideal: DB só de teste (ou schema separado) + seed conhecido.
* Nunca rode E2E contra seu ambiente “dev real” cheio de dados.
* Se for multi-tenant, garanta que o usuário de teste pertence a uma organização “E2E”.

### 19) Cleanup sempre, e “garantia de limpeza”

* Use cleanup em `afterEach/afterAll` e tenha um “garbage collector” opcional (ex: deletar entidades `name like 'E2E-%'`).
* Se cleanup falhar, o teste deve falhar (não esconder).

### 20) Não misture responsabilidades no mesmo teste

Um teste bom valida 1 comportamento:

* “redirect sem auth”
* “tab inválida redireciona”
* “criar time aparece na lista”
  Quando mistura tudo, qualquer instabilidade vira flake.

### 21) Evite dependência em ordenação/paginação

* Se valida que algo aparece numa lista, filtre por nome/id do dado que você criou.
* Não use “primeiro card” ou “última linha” sem garantir ordenação determinística.

### 22) Valide navegação por “URL final + root”

Regra prática: após cada ação que navega:

* `await page.waitForURL(...)`
* `await expect(root).toBeVisible()`
  Isso elimina 80% dos flakes de App Router.

### 23) Teste “o que importa” do backend via API, não via UI (quando o foco é determinismo)

* Para preparar estado (criar time, criar treino, criar membro), prefira API.
* UI fica para validar que o estado é exibido e as rotas/fluxos funcionam.
  Isso reduz muito tempo e flakiness.

### 24) Faça um “modo CI” local igual ao CI

Antes de confiar:

* `--headless`
* `--retries=0`
* `--workers=1`
* rodar 3x seguidas
  Se não aguenta isso, ainda não é determinístico.

### 25) Tenha um “manifesto” de testids

Documente:

* quais pages/abas têm root testid
* quais componentes críticos têm testid
* proibido remover sem atualizar testes
  Isso evita regressões silenciosas.

### 26) Controle de concorrência e locks

* Se o app usa cache, revalidação, filas, cron, websockets: em E2E rode com `workers=1` e desabilite jobs paralelos em modo teste.
* Se dois testes podem criar/editar a mesma entidade, use identificador único por teste e nunca “reaproveite” fixtures globais sem lock.

### 27) Evite estados “eventualmente consistentes”

* Se a UI depende de revalidate/ISR, prefira `no-store` no modo teste ou endpoints específicos “fresh”.
* Se houver fila/async no backend, exponha um endpoint/flag de “await processamento” para testes (ou polling determinístico com timeout curto e condição objetiva).

### 28) Defina contratos de erro por rota

* Para cada rota: 401/redirect, 403, 404, 500 (pelo menos em alto nível).
* Teste isso com asserts claros e estáveis (ex: `data-testid="app-403"`, `app-404`).

### 29) Logging de diagnóstico padronizado

* Em falha, sempre capture: URL final, screenshot, trace, console logs, requests falhas.
* Padronize um helper: `attachDebug(page)` que registra `framenavigated`, `console`, `pageerror`, `requestfailed`.

### 30) “No silent pass”

* Se um teste depende de uma ação (ex: criar team), valide que a API respondeu OK e retornou ID antes de seguir.
* Se um endpoint falhou e a UI caiu em empty state, o teste não pode “passar” por acidente.

### 31) Versões fixas e ambiente reprodutível

* Trave versão do Playwright e browsers (`npx playwright install --with-deps` no CI).
* Evite “atualizei e quebrou tudo” sem mudança no código.

### 32) Seletores acessíveis primeiro, testid para o resto

* Use `getByRole` quando o texto/label for estável e parte do produto.
* Use `data-testid` para elementos técnicos (roots, loaders, skeletons, containers, ícones).

### 33) “Teste de saúde” antes da suíte

* Um teste simples que verifica: app subiu, /signin carrega, API responde, login funciona.
* Se falhar, pare cedo (não gere 40 falhas cascata).

### 34) Política de flakes

* Qualquer flake vira bug: ou no teste (sincronização/seletores) ou no produto (race/redirect).
* Regra: “não mergeia com flake”, e “não resolve flake afrouxando assert”.

### 35) Isolamento por “tenant/organização”

Se o sistema é multi-tenant, todo teste precisa criar/selecionar um tenant exclusivo (ou um namespace) e nunca depender do tenant “padrão”. Isso evita passar local e falhar no CI.

### 36) Seed mínimo versionado

Tenha um seed “oficial de testes” (migrado junto com o schema) e trate como contrato. Se mudou schema e seed não acompanha, o teste deve falhar cedo.

### 37) Congelar relógio e timezone quando importa

Para telas de agenda/calendário, relatórios “hoje/amanhã”, expiração de token:

* fixe `timezoneId`
* injete “clock” no backend (modo teste) ou use datas absolutas nos fixtures.

### 38) Neutralizar features “não determinísticas”

* A/B tests, feature flags remotas, experiments, recomendações, ordenação “popular”.
* Em modo teste: flags fixas e ordenação determinística.

### 39) Dependências externas

Email/SMS/push, pagamentos, storage externo:

* trocar por stub/local fake em E2E (ou capturar via API interna).
* nunca depender de entregas reais.

### 40) Controle de dados “globalmente únicos”

Emails/CPF/username: gere com sufixo único por teste e garanta cleanup mesmo em falha.

### 41) “State reset” de frontend

Se usa localStorage/sessionStorage:

* limpe explicitamente no `beforeEach` (ou use `storageState` controlado).
* não deixe preferências de UI vazarem entre testes.

### 42) Contrato de navegação e redirect

Defina “para onde vai” em:

* sem auth
* sem permissão
* slug inválido
* aba inválida
  E implemente no middleware/route guard uma única fonte canônica. Teste exatamente isso.

### 43) Teste por camada, não só UI

O mais determinístico é: preparar dados via API + validar UI.
E para bugs de redirect/auth: validar a URL final + um root testid.

### 44) Proibição de “assert visual implícito”

Nunca assumir que “se carregou, está certo”.
Sempre valide um marcador semântico (root testid + 1 elemento-chave + URL final).

### 45) Critério de aceite objetivo

Antes de começar: defina “passou” como:

* 0 flaky em 3 execuções seguidas
* `--retries=0`
* 0 skipped
* workers=1 para specs críticos


46. Separar testes por risco e por custo

* Smoke (rápidos): sobem app, login, 1 navegação crítica.
* Críticos (determinísticos): auth/guards/rotas/CRUD principal.
* Pesados (lentos): fluxos longos, relatórios, uploads.
  Regra: CI sempre roda Smoke + Críticos; Pesados em nightly.

47. Política para seeds e migrações

* Migração sempre roda antes do E2E.
* Seed mínimo versionado junto com schema.
* Se seed falhar, aborta a suíte (erro “infra”, não “app”).

48. Estratégia de dados únicos sem depender de Date.now
    Use um `runId` fixo por execução (env var) + sufixo por teste (`test.info().title` sanitizado). Facilita selecionar e limpar sem colisão.

49. “Read your writes” no backend
    Se backend usa transação/replica/caches, crie um endpoint/flag de teste para garantir leitura consistente, ou force `no-store`/`revalidate=0` no modo E2E. Sem isso, flake nasce do backend.

50. Testes de permissão (RBAC) como suíte própria
    Não misture no fluxo funcional. Faça 3-5 casos essenciais:

* sem permissão → 403
* com permissão → ok
* role muda → efeito imediato
  E asserts sempre por `app-403`/URL final.

51. Upload/download e arquivos
    Para fluxos com arquivo:

* use fixtures pequenas e estáveis (ex.: png 1kb)
* valide por “sinal de conclusão” (toast estável + item listado)
* não valide conteúdo binário no E2E; isso é teste de integração.

52. Evitar asserts em toast (como critério principal)
    Toast é instável por timing. Se usar, que seja secundário.
    Critério principal: UI final mudou (root + item criado/editado visível).

53. Definição clara de “done” por página
    Para cada rota: “pronto” = root testid + 1 marcador de conteúdo. Documente isso num arquivo (ex.: TESTIDS_MANIFEST.md) e trate como contrato.

54. Sanitizar estado do navegador entre testes
    Mesmo com storageState:

* limpar `localStorage` não essencial
* desabilitar service worker em E2E (ou controlar)
  Service worker costuma causar “cache fantasma”.

55. Se rodar com Turbo/Dev, tenha uma política
    Dev server pode causar flake (HMR, rebuild). Preferível:

* E2E determinístico em `next build && next start` (CI)
* Dev só para debug local

56. “Gate” de regressão
    Quando um bug real aparece, crie um teste que falha antes da correção. Só então corrija o código. Isso evita testes “otimistas” que não pegam regressão.


### Pontos avançados que mais derrubam determinismo

1. **Concorrência no backend**
   Jobs assíncronos (filas), webhooks, cron, listeners. Em modo teste: desligar ou “sync mode”.

2. **Consistência eventual**
   Se backend faz escrita e depois indexa/propaga (cache, search, analytics), o teste precisa esperar um “sinal final” (endpoint de status) e não “sleep”.

3. **Cache em múltiplas camadas**
   CDN, browser cache, Next cache, fetch cache. Em teste: desabilitar/forçar no-store e invalidar de forma explícita.

4. **Ordenação instável**
   Listas sem ORDER BY ou ordenadas por created_at com empates. Sempre garantir tie-break (id) ou ordenar no backend.

5. **Selectors frágeis por i18n**
   Labels mudam (“Configurações” vs “Settings”). Preferir testid ou role+name estável por dicionário fixo.

6. **Animações e transições**
   Menu, tabs, toasts. Em teste: reduzir motion (prefers-reduced-motion) ou desabilitar animação.

7. **Flakiness por foco/scroll**
   Cliques em elemento fora da viewport ou coberto por header. Use `toBeVisible()` + `scrollIntoViewIfNeeded()` e clique no elemento certo.

8. **State compartilhado entre specs**
   Um spec cria dados e outro assume. Proibir dependência entre specs.

9. **Ambiente inconsistente**
   Rodar com versão diferente de Node, Playwright, browsers, fonts. Fixar versões e instalar browsers no CI.

10. **Telemetria/logs que atrasam UI**
    Se app faz chamadas extras (Sentry, analytics), em teste: stub/disable.

### Refinamentos finais que costumam eliminar os últimos 1–2 flakies:

1. Contrato “pronto para interagir”
   Defina, por página, 1 sinal único de “pronto” (ex: data-testid root + um elemento-chave). Nunca use “carregou” por load/networkidle.

2. Estado do app controlado por flags de teste
   Ex.: `E2E=1` para:

* desativar tours, anúncios, toasts automáticos
* desativar polling
* reduzir animações
* desativar prefetch agressivo

3. Interceptar chamadas não essenciais
   Bloqueie domínios externos (analytics, sentry, fonts remotas). Menos ruído = menos variação.

4. Dados fixos para asserts
   Evite datas relativas (hoje/amanhã) e IDs aleatórios no UI. Use “semente” (seed) ou payloads determinísticos.

5. “Test API” para preparação/limpeza
   Crie endpoints exclusivos de teste (ou scripts) para:

* reset do banco
* seed mínimo
* criar usuário/time e retornar IDs
  Isso reduz dependência de UI para setup.

6. Isolamento por worker
   Se rodar paralelo:

* banco por worker (schema/tenant por WORKER_ID) ou
* prefixo único por worker em tudo que cria
  Se não rodar paralelo, mantenha workers=1 como regra.

7. Timeout e retry como diagnóstico, não solução
   No caminho para “0 flaky”, rode com `--retries=0` e timeouts moderados. Retry só no CI depois de estabilizar.

8. Assert de navegação sem ambiguidade
   Sempre valide:

* URL final
* root testid
* e um “marker” da aba/tela
  Isso detecta redirects silenciosos.

9. Evitar “first()” em listas
   Sempre selecione pelo dado que você criou (nome/ID) para não clicar no item errado.

10. Captura de evidência automática
    Em falha: screenshot + trace + console logs + requests/redirect chain. Isso acelera correções sem “achismo”.


11. Congelar timezone/locale e relógio
    Se o app usa data/hora, congele `timezoneId`, `locale` (já faz) e, quando necessário, use clock fixo (ex.: injetar `Date.now` via flag E2E ou endpoint que retorna “agora” fixo).

12. Acessibilidade como seletor principal
    Prefira `getByRole` + `name` para fluxos estáveis. Use `data-testid` só para “roots” e casos sem semântica acessível.

13. Uma forma canônica de autenticar
    Escolha 1: storageState por cookie OU login via API e set-cookie. Evite misturar métodos dentro do mesmo spec.

14. Nunca depender de ordenação default
    Se lista não tem ordenação garantida, force ordenação no app (query `sort=created_at desc`) quando `E2E=1`, ou selecione pelo item criado.

15. Saúde do backend antes dos testes
    Antes da suíte: ping em endpoints críticos (health + auth + teams). Se falhar, aborta cedo com erro útil.

16. Limpeza “à prova de falha”
    Mesmo se o teste falhar no meio, `afterAll`/global teardown deve tentar limpar tudo que foi criado (best-effort).

17. Evitar dependência entre testes
    Cada teste deve poder rodar sozinho. Se precisar de sequência, agrupe num único teste (fluxo) ou use `serial` com justificativa.

18. Snapshot visual com cuidado
    Snapshots de DOM (ou screenshot) só para páginas extremamente estáveis. Para o resto, prefira asserts funcionais.

19. Rotas/redirects: comportamento oficial documentado
    Para cada rota crítica: tabela “entrada → saída” (URL final + status/404/redirect). Testes viram validação desse contrato.

20. CI idêntico ao local
    Mesma versão de Node, Playwright browsers instalados, mesmas env vars, mesma seed/reset. Divergência aqui é fonte clássica de flaky.

21. Detectar “navegação dupla” e redirects inesperados
    Coloque um helper opcional que registra `framenavigated`, `response.status()` das navegações e `page.on('requestfailed')`. Em caso de falha, anexe isso ao erro. Evita perder horas em “interrupted by another navigation”.

22. Contrato de erros (401/403/404) consistente e testável
    Padronize páginas/handlers: 404 sempre renderiza `data-testid="app-404"`, 403 `app-403`, 401 sempre redireciona para `/signin?callbackUrl=...`. Sem isso, os testes viram “aceita qualquer coisa”.

23. Feature flags para E2E
    Tenha `E2E=1` (ou similar) para:

* desabilitar animações/transition
* reduzir polling
* usar seeds previsíveis
* logs mais verbosos
  Sem mudar UX em produção.

24. Limitar efeitos de rede do frontend
    Se existir prefetch agressivo, websockets, polling: desligar em E2E ou tornar determinístico (intervalo controlado). Isso reduz flakiness no WebKit.

25. Isolar dependências externas
    Emails, S3, serviços terceiros: stub/fake em E2E (ou ambiente sandbox). Teste integrações em suíte separada (não no e2e principal).

26. Medir flake de forma objetiva
    Regra: rodar 3x com `--retries=0` por browser para cada spec crítico. Se falhar 1 vez, não “aceita” — corrige a causa.

27. Sempre deixar um caminho de debug rápido
    Comando padrão por spec (1 browser, 1 worker, retries=0) + abrir trace. Se não for rápido de debugar, vai virar “afrouxa assert”.

Sim. Está super completo.

### 3 itens “raros”:

1. Service Worker e cache persistente
   Se houver PWA/service worker, ele pode causar comportamento diferente entre execuções. Em E2E, desabilite ou garanta limpeza/controle (senão nasce flake fantasma).

2. Isolamento de execução por “run id” com teardown global
   Além de cleanup por teste, tenha um `globalTeardown` que apaga tudo que começar com `E2E-{RUN_ID}-` (mesmo se o teste morrer no meio). Isso fecha a maior fonte de “lixo” acumulado.

3. Separar “contrato” do “teste” em arquivo versionado
   Crie um `E2E_CONTRACT.md` (entrada → saída por rota, redirects, erros, permissão) e trate como canônico. Quando mudar o produto, muda contrato primeiro, depois testes. Isso evita ajuste infinito.



Agora temos 3 camadas separadas: Camada 1: GATE (bloqueia tudo se falhar) tests/e2e/health.gate.spec.ts├── Backend responde em /health ou /docs├── Frontend carrega /signin sem erro  └── Rota protegida /teams redireciona para /signin?callbackUrl Camada 2: CONTRATO (navegação + erros) tests/e2e/teams/teams.contract.spec.ts├── Contrato: 401 - Sem Autenticação│   ├── /teams → /signin?callbackUrl=/teams│   ├── /teams/:id/overview → /signin?callbackUrl preserva path│   └── /teams/:id/members → /signin?callbackUrl preserva path├── Contrato: Redirects Canônicos│   ├── /teams/:id → /teams/:id/overview (sem tab)│   ├── /teams/:id/invalid-tab → /teams/:id/overview│   └── /teams/:id/OVERVIEW → redirect ou 404├── Contrato: 404 - Não Encontrado│   ├── UUID inválido (não é UUID) → 404│   ├── UUID válido mas inexistente → 404│   └── Team deletado (soft delete) → 404├── Contrato: Páginas carregam com root testid│   ├── /teams → teams-dashboard visível│   ├── /teams/:id/overview → team-overview-tab visível│   ├── /teams/:id/members → team-members-tab visível│   └── /teams/:id/settings → teams-settings-root visível└── Contrato: Marcadores estáveis por página    ├── /teams tem botão criar equipe    ├── /teams/:id/members tem botão convidar    └── /teams/:id/settings tem input de nome Camada 3: FUNCIONAIS (já existentes) tests/e2e/teams/├── teams.crud.spec.ts     → Create/Read/Update/Delete├── teams.states.spec.ts   → Loading/Empty/Error/Success├── teams.invites.spec.ts  → Criar/Cancelar/Reenviar convites├── teams.welcome.spec.ts  → Fluxo de primeiro acesso└── teams.rbac.spec.ts     → Permissões por role Ordem de Execução Canônica: # 1. GATE (se falhar, PARA)npx playwright test tests/e2e/health.gate.spec.ts --project=chromium --workers=1 --retries=0# 2. CONTRATO (se falhar, debugar navegação/erros)npx playwright test tests/e2e/teams/teams.contract.spec.ts --project=chromium --workers=1 --retries=0# 3. FUNCIONAIS (cada spec isolada)npx playwright test tests/e2e/teams/teams.crud.spec.ts --project=chromium --workers=1 --retries=0# ... etc Princípio aplicado: Falhou onde Significa health.gate Infra down (backend/frontend) teams.contract Navegação/redirect/404 quebrado teams.crud CRUD específico com bug teams.rbac Permissão específica errada

