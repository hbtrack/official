CANARY: HBTRACK_DOCS_LOADED_v1

# CANON — Fontes de Verdade e Invariantes (HB Track)

Este repositório usa "Context-as-a-Service": decisões devem ser ancoradas em artefatos canônicos recuperáveis.

## 1) Fontes de Verdade (ordem de prioridade)
1. docs/_generated/openapi.json  (contrato da API)
2. docs/_generated/schema.sql     (estado atual do schema)
3. docs/_generated/alembic_state.txt (estado/linha do tempo de migrations)

Regra: se houver divergência entre código, docs humanas e artefatos gerados, os arquivos em docs/_generated/* prevalecem.
Docs humanas servem para explicar intenções, não para substituir contratos.

## 2) Stack (para evitar inferência)
Backend:
- Python 3.10+, FastAPI, SQLAlchemy, Alembic
- PostgreSQL 17 (Neon em cloud; local via Docker/Compose)
- Auth: JWT + bcrypt
- Async: Celery + Redis
- Integrações: Gemini API, Cloudinary, Resend
- Testes: pytest

Frontend:
- Next.js 16 (App Router), React 19, TS 5.9
- Tailwind 3.4, Radix UI
- React Hook Form + Zod, TanStack Query
- Testes: Playwright
- Libs: FullCalendar, ApexCharts, Framer Motion

## 3) Política de mudanças (gates)
- Default: patch mínimo por tarefa (menor diff que resolve).
- Refactor modular: permitido apenas quando o usuário explicitamente habilitar o gate:
  Gate string: [ALLOW_REFACTOR]
  Sem isso, qualquer "refactor grande" deve ser convertido em sequência de patches pequenos ou recusado.

## 4) Contrato de evidência (obrigatório)
Antes de propor alteração de código, declarar:
- Evidências consultadas: paths (ex.: openapi.json, schema.sql, arquivos do módulo)
- Hipóteses (se existirem): rotuladas e minimizadas
- Mudança proposta: patch mínimo
- Verificação: checks executados (ou, se não executáveis, por quê + como executar)