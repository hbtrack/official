CANARY: HBTRACK_DOCS_LOADED_v1

# CANON — Fontes de Verdade e Invariantes (HB Track)

Este repositório usa "Context-as-a-Service": decisões devem ser ancoradas em artefatos canônicos recuperáveis.

## 1) Fontes de Verdade (ordem de prioridade)
1. **docs/_generated/openapi.json** (contrato de API — snapshot local, obrigatório)
2. package.json (scripts de verificação: gate/typecheck/lint)
3. tsconfig.json (contrato de types)
4. .eslintrc.json (contrato de lint)

### OpenAPI: Contrato Local (Frontend)
- **Origem**: `Hb Track - Backend/docs/_generated/openapi.json` (gerado via `python scripts/generate_docs.py --openapi`)
- **Cópia local**: sincronizada para `docs/_generated/openapi.json` via `npm run sync:openapi` (ou `powershell -ExecutionPolicy Bypass -File scripts/sync_openapi.ps1`)
- **Validação**: script valida freshness “warning se > 7 dias; erro se > 30 dias”
- **Obrigatoriedade**: qualquer tarefa de integração com API deve:
  1. Rodar `npm run sync:openapi` antes de iniciar (ou declarar por que não pode)
  2. Consultar `docs/_generated/openapi.json` como fonte de verdade
  3. Se estiver desatualizado, bloquear integração até sync ser bem-sucedido
  4. Declarar "validação de freshness OK" no reporte final

Quando mexer em integração de API:

# Sincronizar + rodar gate

npm run gate:api

**ou manualmente:**

npm run sync:openapi
npm run gate

Backend gera:
python scripts/generate_docs.py --openapi

## 2) Stack (para evitar inferência)
Backend (referência externa): FastAPI + SQLAlchemy/Alembic; contrato consumido aqui é o snapshot em `docs/_generated/openapi.json` (sincronizado via `npm run sync:openapi`).

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
- Evidências consultadas: paths locais (ex.: docs/_generated/openapi.json, arquivos do módulo). Se precisar de dados/schema, citar explicitamente o BACKEND repo como fonte externa.
- Hipóteses (se existirem): rotuladas e minimizadas
- Mudança proposta: patch mínimo
- Verificação: checks executados (ou, se não executáveis, por quê + como executar)