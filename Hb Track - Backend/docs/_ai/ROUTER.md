# ROUTER — Como recuperar contexto antes de decidir (Backend; retrieve-then-reason)

Objetivo: minimizar alucinação e custo de contexto. Sempre buscar artefatos canônicos + código-alvo antes de concluir.

## A) Classificar a tarefa (1 escolha)
1) BUGFIX (API/DB/Worker)
2) ENDPOINT/API (Contrato + Implementação)
3) REFACTOR (Backend)

## B) Sequência de recuperação por tipo

### 1) BUGFIX (API/DB/Worker)
1. Identificar sintoma observável:
   - stack trace
   - erro de request (status/response)
   - teste pytest falhando
   - exceção em task Celery
   - divergência em docs/_generated/*
2. Abrir o arquivo/camada mais próxima do sintoma:
   - router/endpoint (FastAPI)
   - service/use-case
   - repo/query/SQLAlchemy
   - task Celery
3. Consultar canônicos quando relevante:
   - Contrato de API: docs/_generated/openapi.json
   - Estado de dados: docs/_generated/schema.sql
   - Linha do tempo de migrations: docs/_generated/alembic_state.txt
4. Se o bug envolver DB:
   - localizar migration relacionada (alembic/versions) e/ou model
   - verificar estado atual (alembic current/heads)
5. Localizar testes existentes; se inexistentes, criar teste mínimo (pytest) que falha e depois passa.
6. Patch mínimo + checks (migrations quando aplicável).

### 2) ENDPOINT/API (Contrato + Implementação)
1. Abrir docs/_generated/openapi.json e localizar o endpoint (path + método) e:
   - schemas de request/response
   - status codes e erros
2. Localizar implementação via busca:
   - routers (FastAPI)
   - handlers/services
   - dependências (auth/permissions)
3. Se a mudança altera persistência/validação:
   - conferir docs/_generated/schema.sql
   - identificar migrations necessárias (Alembic)
4. Implementar com contrato explícito:
   - validação/serialização consistente (Pydantic)
   - tratamento de erros coerente com status codes declarados
   - garantir que auth/perms seguem regras do sistema
5. Atualizar artefatos gerados (obrigatório quando houver impacto):
   - python scripts/generate_docs.py --openapi (ou --all)
   - python scripts/generate_docs.py --schema (se mexer em DB)
   - python scripts/generate_docs.py --alembic (se mexer em migrations)
6. Checks:
   - docker compose up -d postgres redis (se necessário)
   - alembic upgrade head (quando houver migrations)
   - pytest -q
   - smoke check do endpoint (quando aplicável)

### 3) REFACTOR (Backend; somente com [ALLOW_REFACTOR])
1. Declarar escopo e "cut line" (o que NÃO será tocado).
2. Mapear dependências e acoplamentos:
   - imports
   - camadas (router/service/repo)
   - modelos e migrations afetadas
3. Refactor incremental (passos pequenos), rodando checks em cada etapa:
   - pytest -q
   - alembic upgrade head (quando aplicável)
4. Não misturar refactor com feature/bugfix na mesma mudança.
5. Ao final, regenerar artefatos canônicos se houver qualquer impacto de contrato/dados:
   - python scripts/generate_docs.py --all