# ADR-031 — Backend Framework: Django Ninja

**Status:** accepted
**Data:** 2026-03-17
**Decisores:** Humano (D4 backend — decisão 2026-03-17)
**Supersede (parcialmente):** ADR-026 §1 Stack (FastAPI → Django Ninja), ADR-028 §Ferramenta (Alembic → Django Migrations)

---

## Contexto

ADR-026 estabeleceu a stack inicial de backend como **Python + FastAPI + SQLAlchemy + Alembic**.
A escolha foi revisitada em 2026-03-17 ao constatar que:

1. O módulo `training` sozinho possui 101 invariantes de negócio, FSM de 7 estados, soft-delete em todas as entidades e 8+ tarefas Celery documentadas — nível de complexidade relacional que é o ponto forte do Django ORM.
2. FastAPI gera o contrato OpenAPI **a partir** do código — contrário ao princípio CDD do HB Track, onde o contrato é SSOT e o código segue o contrato.
3. Django Ninja combina:
   - ORM maduro do Django (FK, ENUM, JSONB, triggers, índices compostos)
   - Django Migrations (nativo, sem dependência de SQLAlchemy)
   - Sintaxe moderna equivalente ao FastAPI (type hints + Pydantic)
   - Django Admin (gestão interna da plataforma)
   - Django Channels (WebSocket para notificações em tempo real — INV-TRAIN-024)
   - Celery nativo (integração completa com Django)

---

## Decisão

**Framework backend:** Django 5.x + Django Ninja 1.x

**Stack completa (substitui §1 do ADR-026):**

| Camada | Tecnologia |
|--------|-----------|
| Backend API | Python 3.12 + Django 5.x + Django Ninja 1.x |
| Banco de dados | PostgreSQL 16 |
| ORM | Django ORM |
| Migrações | Django Migrations (nativo) |
| Task queue | Celery 5.x + Redis 7 |
| WebSocket | Django Channels 4.x + Redis |
| Frontend | React 18 + Vite (decidido em ADR-030 / D7 — SSOT: `FRONTEND_CONTRACT.md`) |
| Testes | pytest + pytest-django (backend) + Jest (frontend) |
| Containerização | Docker + Docker Compose |

**Ferramenta de migração:** Django Migrations substitui Alembic (ADR-028 §Ferramenta).
A ESTRATÉGIA de migração do ADR-028 (staging obrigatório, reversibilidade, zero-downtime) permanece válida — apenas a ferramenta muda.

**Nota sobre arquivos existentes:** O arquivo `migrations/training/versions/20260317_001_create_training_tables.py` (Alembic) é um ARTEFATO DE REFERÊNCIA de schema — não será executado. As migrações reais serão Django Migrations em `src/training/migrations/` quando a implementação começar.

---

## Alternativas Consideradas

| Opção | Motivo da rejeição |
|---|---|
| FastAPI + SQLAlchemy (ADR-026 original) | Gera contrato a partir do código (anti-CDD); ORM menos maduro para 101 invariantes |
| Django REST Framework | Verboso, serializers explícitos menos produtivos; Django Ninja é mais moderno e alinhado |
| Django Ninja | **ESCOLHIDO** |

---

## Consequências

**Positivas:**
- Django ORM nativo para FSM, soft-delete, RBAC, audit — sem adaptadores SQLAlchemy
- Django Admin disponível para gestão interna
- Celery + Django = integração de primeira classe (shared_task, django-celery-beat)
- Django Channels para WebSocket (INV-TRAIN-024 notificações em tempo real)
- pytest-django para testes integrados ao Django settings

**Atenção:**
- `DATABASE_URL` usa formato Django: `django.db.backends.postgresql` (não `postgresql+asyncpg`)
- Pasta `migrations/<module>/` existente (Alembic) é referência — não executar
- Django é síncrono por padrão; operações async via Django Ninja async views quando necessário

---

## Referências

- `docs/_canon/CODE_ARCHITECTURE.md` v1.1.0 (atualizado)
- `docs/_canon/decisions/ADR-026-code-architecture.md` (§1 Stack supersedida)
- `docs/_canon/decisions/ADR-028-data-migration-strategy.md` (§Ferramenta supersedida)
- `docs/_canon/decisions/ADR-030-frontend-strategy.md` (frontend stack)
