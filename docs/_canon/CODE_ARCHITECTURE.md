---
doc_type: canon
version: "1.0.0"
status: active
decision_ref: D4
adr_ref: ADR-026
---

# CODE_ARCHITECTURE.md

## 1. Stack Tecnológica (D4 = Opção A)

| Camada | Tecnologia |
|--------|-----------|
| Backend API | Python 3.12 + FastAPI |
| Banco de dados | PostgreSQL 16 |
| ORM | SQLAlchemy 2.x (async) |
| Migrações | Alembic |
| App mobile/web | React Native (Expo) |
| Testes | pytest (backend) + Jest (frontend) |
| Containerização | Docker + Docker Compose |

## 2. Princípios de Arquitetura

### Clean Architecture (4 camadas)

```
                ┌─────────────────────────────┐
                │   Interface (FastAPI routes) │  ← contratos OpenAPI = Ports
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

## 3. Organização de Pastas

```
Hb Track - Backend/
  src/
    <module>/               ← um diretório por módulo canônico
      domain/
        entities.py         ← entidades e value objects
        rules.py            ← domain rules (DOMAIN_RULES_<MODULE>.md)
        state_machine.py    ← FSM (STATE_MODEL_<MODULE>.md) se aplicável
      application/
        use_cases.py        ← casos de uso (um por feature do FEATURE_REGISTRY)
        dtos.py             ← Data Transfer Objects (Input/Output)
      infrastructure/
        repository.py       ← implementação SQLAlchemy
        models.py           ← modelos ORM (tabelas)
      interface/
        router.py           ← FastAPI router (implementa Port do contrato)
        schemas.py          ← Pydantic schemas (gerados do JSON Schema)
  tests/
    <module>/
      unit/                 ← testes de domain + application
      integration/          ← testes de interface + infrastructure
  alembic/                  ← migrações (ver DATA_MIGRATION_POLICY.md)
  main.py                   ← entrypoint FastAPI
  pyproject.toml
```

## 4. Padrão de Nomenclatura

| Artefato | Convenção | Exemplo |
|---------|-----------|---------|
| Entidades | PascalCase | `TrainingSession`, `Athlete` |
| Use cases | verbo + substantivo | `CreateTrainingSession`, `RecordAttendance` |
| Routers FastAPI | snake_case + `_router` | `training_router` |
| Schemas Pydantic | PascalCase + sufixo | `TrainingSessionInput`, `TrainingSessionOutput` |
| Tabelas DB | snake_case plural | `training_sessions`, `athletes` |
| Migrations Alembic | `<timestamp>_<description>` | `20260317_create_training_sessions` |

## 5. Regras de Geração de Código

### R1 — Contrato antes de código
Nenhum endpoint pode ser implementado sem existir no contrato OpenAPI.
O worker `generate_code.prompt.md` verifica isso antes de gerar qualquer arquivo.

### R2 — Schema Pydantic derivado do JSON Schema
Os schemas Pydantic em `interface/schemas.py` são derivados dos contratos
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
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/hbtrack
SECRET_KEY=<gerado>                    # ADR-012
PACT_BROKER_BASE_URL=http://<VPS>:9292 # ADR-025 (opcional em dev)
PACT_BROKER_TOKEN=<token>              # ADR-025 (opcional em dev)
```

### Docker Compose (desenvolvimento)

```yaml
services:
  api:
    build: .
    ports: ["8000:8000"]
    environment:
      - DATABASE_URL=postgresql+asyncpg://hbtrack:hbtrack@db:5432/hbtrack
    depends_on: [db]
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: hbtrack
      POSTGRES_PASSWORD: hbtrack
      POSTGRES_DB: hbtrack
    volumes: ["pgdata:/var/lib/postgresql/data"]
volumes:
  pgdata:
```

## 7. Gate CODE_ARCHITECTURE_GATE

Verifica conformidade com esta arquitetura no pipeline CI:
1. `Hb Track - Backend/src/` existe
2. `ADR-026-code-architecture.md` existe
3. Para módulos com status `implementation_ready` no MODULE_REGISTRY:
   - Estrutura de pastas `src/<module>/` presente

## 8. Referências

- `docs/_canon/decisions/ADR-026-code-architecture.md`
- `docs/_canon/FEATURE_REGISTRY.yaml` — features mapeiam para use cases
- `contracts/openapi/` — Ports da camada Interface
- `contracts/schemas/` — origem dos schemas Pydantic
- `docs/_canon/DATA_MIGRATION_POLICY.md` — política de migrações
