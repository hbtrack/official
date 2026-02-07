# CHECKS — Verificação objetiva (local)

Princípio: nenhuma tarefa está "concluída" sem checks executados (ou sem declarar exatamente o motivo e o comando correto).

## 0) Pré-requisitos
- Node/npm
- PowerShell (para sync do OpenAPI)
- No repo BACKEND: gerar OpenAPI quando necessário:
  - Origem: `Hb Track - Backend/docs/_generated/openapi.json` (gerado via `python scripts/generate_docs.py --openapi`)
  - Frontend sincroniza via `npm run sync:openapi` para cópia local

## 1) OpenAPI (obrigatório em tarefas de integração API)
- npm run sync:openapi
  (ou: powershell -ExecutionPolicy Bypass -File scripts/sync_openapi.ps1)

Critério:
- docs/_generated/openapi.json deve existir antes de implementar/ajustar integração de endpoints.

**Definition of Done (para integração API):**
```bash
npm run gate:api  # Must pass: sync OK + hygiene + typecheck + lint
```
Qualquer tarefa de integração API não está concluída sem `npm run gate:api` ✓.

## 2) Frontend hygiene (obrigatório quando tocar em TS/React/UI)
- npm run gate (ou npm run gate:api quando envolver integração com API)
  (ou, no mínimo: npm run typecheck + npm run lint)

## 3) E2E (quando a mudança afetar fluxos críticos)
- npx playwright test

## 4) Formato de reporte (o agente deve sempre devolver)
Evidências:
- <paths consultados, incluindo docs/_generated/* quando relevante>

Mudança:
- <resumo do patch mínimo>

Checks:
- <lista de comandos executados + resultado>
- Se algo não foi executado: <motivo objetivo + como executar>