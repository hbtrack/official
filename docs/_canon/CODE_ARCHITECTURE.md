---
doc_type: canon
version: "1.1.0"
status: active
decision_ref: D4
adr_ref: ADR-026, ADR-031
---

# CODE_ARCHITECTURE.md

> **v1.1.0 (2026-03-23):** Stack consolidada em Django Ninja + React/Vite; bloco legado FastAPI removido.

## 1. Stack Tecnológica (D4 = Django Ninja — ADR-031)

| Camada | Tecnologia |
|--------|-----------|
| Backend API | Python 3.12 + Django 5.x + Django Ninja 1.x |
| Banco de dados | PostgreSQL 16 |
| ORM | Django ORM |
| Migrações | Django Migrations (nativo) |
| Task queue | Celery 5.x + Redis 7 |
| WebSocket | Django Channels 4.x + Redis |
| Frontend | React 18 + Vite 5.x + TypeScript + PWA |
| Testes | pytest + pytest-django (backend) + Vitest + Playwright (frontend) |
| Containerização | Docker + Docker Compose |

## 2. Princípios de Arquitetura

### Clean Architecture (4 camadas)

```
                ┌─────────────────────────────┐
                │  Interface (Django Ninja)    │  ← contratos OpenAPI = Ports
                ├─────────────────────────────┤
                │   Application (use cases)    │  ← orquestra domínio
                ├─────────────────────────────┤
                │   Domain (entities + rules) │  ← núcleo do negócio
                ├─────────────────────────────┤
                │   Infrastructure (DB, etc.) │  ← adapters externos
                └─────────────────────────────┘
```

**Regra de dependência:** Cada camada só conhece a camada abaixo dela.
Infrastructure e Interface dependem de Domain, nunca o contrário.

### Contratos OpenAPI = Ports

Os contratos em `contracts/openapi/` definem a interface pública da API.
O código gerado na camada Interface deve implementar **exatamente** o que
está contratado — sem adicionar nem remover endpoints, campos ou status codes.

> **SSOT de convenções HTTP**: `.contract_driven/templates/api/api_rules.yaml` define
> error model, paginação, status codes e naming conventions para toda a API.

## 3. Organização de Pastas

> **STATUS**: estrutura canônica em uso no workspace.

```
src/
  <module>/               ← Django app para cada módulo canônico
    models.py             ← Django ORM models (entidades + soft-delete + enums)
    api.py                ← Django Ninja router (implementa Port do contrato)
    schemas.py            ← Pydantic schemas (derivados dos JSON Schema contracts)
    domain/
      entities.py         ← entidades e value objects
      rules.py            ← domain rules (DOMAIN_RULES_<MODULE>.md)
      state_machine.py    ← FSM (STATE_MODEL_<MODULE>.md) se aplicável
    application/
      use_cases.py        ← casos de uso (um por feature do FEATURE_REGISTRY)
    infrastructure/
      repository.py       ← queries Django ORM (sem lógica de negócio)
    tasks.py              ← tarefas Celery do módulo
    migrations/           ← Django Migrations (geradas com makemigrations)
config/
  settings.py             ← Django settings (base + dev + prod)
  urls.py                 ← URL config + Django Ninja router mount
  celery.py               ← Celery app config
tests/
  <module>/
    unit/                 ← testes de domain + application
    integration/          ← testes de interface + infrastructure
manage.py
pyproject.toml
```

> **Nota ADR-031:** A pasta `migrations/training/versions/` na raiz é um artefato de referência
> de schema (Alembic — obsoleto). As migrações reais serão `src/training/migrations/`.

## 4. Padrão de Nomenclatura

| Artefato | Convenção | Exemplo |
|---------|-----------|---------|
| Entidades | PascalCase | `TrainingSession`, `Athlete` |
| Use cases | verbo + substantivo | `CreateTrainingSession`, `RecordAttendance` |
| Routers Django Ninja | snake_case + `_router` | `training_router` |
| Schemas Pydantic | PascalCase + sufixo | `TrainingSessionIn`, `TrainingSessionOut` |
| Tabelas DB | snake_case plural | `training_sessions`, `athletes` |
| Migrations Django | `<seq>_<description>` | `0001_create_training_sessions` |
| Tasks Celery | snake_case + `_task` | `refresh_analytics_cache_task` |

## 5. Regras de Geração de Código

### R1 — Contrato antes de código
Nenhum endpoint pode ser implementado sem existir no contrato OpenAPI.
O worker `generate_code.prompt.md` verifica isso antes de gerar qualquer arquivo.

### R2 — Schema Pydantic derivado do JSON Schema
Os schemas Pydantic em `<module>/schemas.py` são derivados dos contratos
em `contracts/schemas/<module>/`. Drift → `BLOCKED_SCHEMA_DRIFT`.

### R3 — Um use case por feature
Cada feature do `FEATURE_REGISTRY.yaml` corresponde a um use case em
`application/use_cases.py`. Nunca implementar lógica de negócio no router.

### R4 — Análise adversarial antes de implementar
O gate `ADVERSARIAL_ANALYSIS_GATE` deve estar PASS para o módulo
antes de qualquer código de produção ser gerado.

### R5 — Testes obrigatórios
Todo use case gerado deve ter ao menos um teste unitário correspondente.
Todo endpoint do router deve ter ao menos um teste de integração.

## 6. Configuração dos Serviços

### Variáveis de ambiente obrigatórias

```env
DATABASE_URL=postgresql://user:pass@localhost:5432/hbtrack
SECRET_KEY=<gerado>                    # ADR-012
REDIS_URL=redis://localhost:6379/0     # Celery + Channels
PACT_BROKER_BASE_URL=http://<VPS>:9292 # ADR-025 (opcional em dev)
PACT_BROKER_TOKEN=<token>              # ADR-025 (opcional em dev)
```

### Docker Compose (desenvolvimento)

```yaml
services:
  api:
    build: .
    command: python manage.py runserver 0.0.0.0:8000
    ports: ["8000:8000"]
    environment:
      - DATABASE_URL=postgresql://hbtrack:hbtrack@db:5432/hbtrack
      - REDIS_URL=redis://redis:6379/0
    depends_on: [db, redis]
  celery:
    build: .
    command: celery -A config worker -l info
    depends_on: [db, redis]
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: hbtrack
      POSTGRES_PASSWORD: hbtrack
      POSTGRES_DB: hbtrack
    volumes: ["pgdata:/var/lib/postgresql/data"]
  redis:
    image: redis:7-alpine
    volumes: ["redisdata:/data"]
volumes:
  pgdata:
  redisdata:
```

## 7. Gate CODE_ARCHITECTURE_GATE

> **STATUS**: SKIP_NOT_APPLICABLE até primeira implementação de código.

Quando ativo, verifica conformidade com esta arquitetura no pipeline CI:
1. `src/` existe
2. `docs/_canon/decisions/ADR-031-backend-framework.md` existe
3. Para módulos com status `implementation_ready` no MODULE_REGISTRY:
   - Estrutura de pastas `src/<module>/` presente com `models.py`, `api.py`, `schemas.py`

## 8. Referências

- `docs/_canon/decisions/ADR-031-backend-framework.md` (stack atual)
- `docs/_canon/decisions/ADR-026-code-architecture.md` (princípios — §1 supersedida)
- `docs/_canon/decisions/ADR-028-data-migration-strategy.md` (estratégia — §Ferramenta supersedida)
- `docs/_canon/FEATURE_REGISTRY.yaml` — features mapeiam para use cases
- `contracts/openapi/` — Ports da camada Interface
- `contracts/schemas/` — origem dos schemas Pydantic
