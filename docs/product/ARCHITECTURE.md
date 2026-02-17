---
id: ARCHITECTURE
doc_mode: REFERENCE
status: CANONICAL
---

# HB Track — Architecture

## Containers (C4 Level 2)

```
┌─────────────┐     HTTPS/JSON      ┌──────────────────┐
│  Browser     │ ──────────────────► │  Next.js Frontend │
│  (SPA)       │                     │  (App Router)     │
└─────────────┘                     └────────┬─────────┘
                                             │ fetch
                                             ▼
                                    ┌──────────────────┐
                                    │  FastAPI Backend  │
                                    │  /api/v1/*        │
                                    └──┬──────────┬────┘
                                       │          │
                              ┌────────▼──┐  ┌────▼──────┐
                              │ PostgreSQL │  │ Redis     │
                              │ (asyncpg)  │  │ (broker)  │
                              └───────────┘  └─────┬─────┘
                                                   │
                                              ┌────▼──────┐
                                              │ Celery    │
                                              │ (workers) │
                                              └───────────┘
```

## Backend layers

| Layer | Path | Responsibility |
|-------|------|----------------|
| Routers | `app/api/v1/` | HTTP handling, auth guards, response shaping |
| Services | `app/services/` | Business logic, invariant enforcement |
| Models | `app/models/` | SQLAlchemy ORM, DB constraints, soft delete |
| Schemas | `app/schemas/` | Pydantic validation (request/response) |
| Core | `app/core/` | Security (JWT), ExecutionContext, permissions map, exceptions |
| Migrations | `db/alembic/` | Schema versioning via Alembic |

## Frontend layers

| Layer | Path | Responsibility |
|-------|------|----------------|
| Pages | `src/app/(admin)/`, `src/app/(protected)/` | Route-based views |
| Components | `src/components/` | Reusable UI (Radix UI base) |
| Hooks | `src/hooks/` | Data fetching (React Query), UI state |
| Contexts | `src/contexts/` | Auth, sidebar, theme providers |
| API client | `src/api/` or `src/lib/` | Fetch wrappers to backend |

## Authentication flow

1. `POST /api/v1/auth/login` → returns JWT access + refresh token
2. Access token in `Authorization: Bearer` header
3. Refresh token stored in DB (`refresh_token` table), 7-day validity
4. `ExecutionContext` built per-request: user, role, org, permissions resolved

## Multi-tenancy
All queries scoped to `organization_id` from ExecutionContext. Single-club in V1 (R34).

## Async processing
Celery workers handle: training alerts (Step 18), email queue, export jobs, analytics cache refresh.
Broker: Redis. Monitoring: Flower (optional).

## Key constraints
- Soft delete everywhere (R29): `deleted_at` + `deleted_reason` CHECK pair
- Active membership required (R42, except superadmin)
- Audit logging mandatory (R31/R32)
- Edit windows: 10min author, 24h superior, >24h readonly (R40)
