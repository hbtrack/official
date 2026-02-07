# CHECKS — Verificação objetiva (local)

Princípio: nenhuma tarefa está "concluída" sem checks executados (ou sem declarar exatamente o motivo e o comando correto).

## 0) Env e pré-requisitos (Windows/PowerShell)
Fonte primária: .env na raiz do workspace. Scripts Python usam load_dotenv().
Em PowerShell, quando precisar exportar para sessão, use:

- Carregar .env para $env:*
  - Get-Content .env | ForEach-Object {
      if ($_ -match '^\s*#' -or $_ -notmatch '=') { return }
      $name, $value = $_ -split '=', 2
      $env:$name = $value
    }

Verificações rápidas:
- Garanta que DATABASE_URL e DATABASE_URL_SYNC estão em linhas separadas no .env (1 variável por linha).
- Confirme no PowerShell:
  - echo $env:DATABASE_URL
  - echo $env:DATABASE_URL_SYNC

Ferramentas:
- Docker + docker compose
- Python (venv)
- pg_dump disponível no PATH (para schema.sql)
- alembic disponível no ambiente Python

## 1) Infra local (Docker Compose)
Seu compose atual sobe apenas postgres e redis.

- docker compose up -d postgres redis
- docker compose ps
- docker compose logs -f postgres
- docker compose logs -f redis

## 2) Banco + Migrations (Alembic)
Obrigatório quando mexer em models/migrations/tabelas:

- alembic upgrade head
- alembic current
- alembic heads

## 3) Backend (FastAPI + pytest)
Testes:
- pytest -q

API (quando a tarefa envolver endpoint/API):
- Suba a API localmente 
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --log-level info
- Smoke check:
- GET http://localhost:8000/api/v1/openapi.json

Se você não souber <APP_IMPORT_PATH>:
- Buscar no repo por "FastAPI(" e localizar o arquivo onde existe "app = FastAPI(...)"
- O import path é <caminho_do_modulo_sem_.py>:app

## 4) Celery + Redis (quando relevante)
Se a mudança tocar tasks assíncronas:
- Suba o worker manualmente

python -m celery -A app.core.celery_app worker --pool=solo --concurrency=4 --loglevel=info
python -m celery -A app.core.celery_app beat --loglevel=info
python -m celery -A app.core.celery_app flower --port=5555 --basic_auth=admin:hbtrack2026

  - celery -A <CELERY_APP_IMPORT> worker -l info

Se não souber <CELERY_APP_IMPORT>:
- Buscar no repo por "Celery(" ou "celery_app" ou "Celery(" e localizar o ponto de criação do app.

## 5) Geração de artefatos canônicos (docs/_generated/*)
Todos os artefatos canônicos são gerados por scripts/generate_docs.py.

Gerar tudo:
- python scripts/generate_docs.py --all

Ou individual:
- python scripts/generate_docs.py --openapi
- python scripts/generate_docs.py --schema
- python scripts/generate_docs.py --alembic

Pré-condições por artefato:
- openapi.json:
  - Preferencial: import do app funciona (app.openapi()).
  - Fallback: FastAPI rodando e GET /api/v1/openapi.json acessível.
- schema.sql:
  - pg_dump instalado + DATABASE_URL configurada (apontando para o DB local).
- alembic_state.txt:
  - alembic disponível + DATABASE_URL_SYNC ou DATABASE_URL configurada.

Obrigatório:
- Se mexeu em rotas/schemas request/response -> gerar openapi.json.
- Se mexeu em models/migrations/tabelas -> gerar schema.sql e alembic_state.txt.

## 6) Frontend (Next.js)
Rodar quando tocar em TS/React/UI:
- npm run typecheck
- npm run lint
- npm run gate

## 7) E2E (Playwright)
Rodar quando a mudança afetar fluxos críticos:
- npx playwright test

Observação:
- Seus E2E atualmente podem sobrescrever DATABASE_URL via $env:DATABASE_URL hardcoded.
- Garanta que o DB de E2E não conflita com o DB dev local.

## 8) Formato de reporte (o agente deve sempre devolver)
Evidências:
- <paths consultados, incluindo docs/_generated/* quando relevante>

Mudança:
- <resumo do patch mínimo>

Checks:
- <lista de comandos executados + resultado>
- Se algo não foi executado: <motivo objetivo + como executar>