# ROUTER — Como recuperar contexto antes de decidir (Frontend; retrieve-then-reason)

Objetivo: minimizar alucinação e custo de contexto. Sempre buscar artefatos canônicos locais + código-alvo antes de concluir.

## A) Classificar a tarefa (1 escolha)
1) BUGFIX (UI/Client)
2) ENDPOINT/API (Integração)
3) REFACTOR (Frontend)

## B) Sequência de recuperação por tipo

### 1) BUGFIX (UI/Client)
1. Identificar sintoma observável (erro de runtime no browser, erro de build, type error, falha no lint, falha em Playwright, comportamento incorreto).
2. Abrir o arquivo mais próximo do sintoma (componente/tela, hook, provider, util, client).
3. Consultar canônicos locais quando relevante:
   - Se envolve contrato/shape de dados vindo da API: docs/_generated/openapi.json (snapshot local)
   - Se envolve scripts/regras de verificação: package.json, tsconfig.json, .eslintrc.json
4. Se o bug depende de dados persistidos, regras de schema, ou comportamento do backend:
   - Citar explicitamente o BACKEND repo como fonte externa (não buscar schema/alembic no frontend).
   - Se o contrato no OpenAPI estiver ausente/desatualizado: exigir atualização/sync antes de continuar.
5. Localizar testes existentes; se inexistentes, criar teste mínimo (unit/integration se houver) ou um cenário Playwright mínimo.
6. Patch mínimo + checks (npm run gate; Playwright quando fluxo crítico).

### 2) ENDPOINT/API (Integração)
0. Pré-condição: garantir contrato local atualizado.
   - Executar: npm run gate:api
     (equivalente a: npm run sync:openapi && npm run gate)
1. Abrir docs/_generated/openapi.json e localizar o endpoint (path + método) e:
   - schemas de request/response
   - status codes e erros
   - query params / headers relevantes
2. Localizar ponto(s) de consumo no frontend por busca:
   - client/fetch wrapper (onde requests são construídos)
   - hooks (TanStack Query) / query keys / mutations
   - schemas Zod / transformações / normalizações
   - componente/tela que renderiza o dado
3. Implementar/ajustar integração respeitando o contrato:
   - Tipagem (TS) coerente com o schema (evitar any)
   - Validação Zod quando aplicável (especialmente em fronteiras de dados)
   - Tratamento de erros e estados (loading/empty/error) coerente com o status code
4. Se o endpoint/contrato necessário NÃO existir no OpenAPI:
   - Bloquear a integração.
   - Exigir mudança no BACKEND + regeneração do OpenAPI + novo sync.
5. Checks:
   - npm run gate (obrigatório)
   - npx playwright test (quando afetar fluxo crítico)
   - Repetir npm run gate:api se houver mudanças subsequentes no contrato

### 3) REFACTOR (Frontend; somente com [ALLOW_REFACTOR])
1. Declarar escopo e "cut line" (o que NÃO será tocado).
2. Mapear dependências e usos:
   - imports e reexports
   - componentes consumidores
   - hooks dependentes e query keys
3. Refactor incremental (passos pequenos), rodando checks em cada etapa:
   - npm run gate
   - npm run gate:api se tocar em integração com API/contrato
4. Não misturar refactor com feature/bugfix na mesma mudança.
5. Se durante o refactor surgir necessidade de alteração de contrato de API:
   - Tratar como ENDPOINT/API: bloquear e exigir atualização no BACKEND + sync.