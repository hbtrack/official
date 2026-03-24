---
doc_type: canon
version: "1.1.0"
status: active
decision_ref: D7
adr_ref: ADR-030
state_semantics: target-state
---

# FRONTEND_CONTRACT.md

## 0. Status Operacional Atual

Este documento descreve o **target-state normativo** do frontend. O worker `generate_frontend` permanece `frozen` enquanto:

- `frontend/` não existir no workspace com paths canonizados
- `package.json` não declarar a toolchain frontend real (React/Vite/Vitest/Playwright)
- o `FRONTEND_CONTRACT_GATE` continuar em `SKIP_NOT_APPLICABLE`
- não houver validação empírica do contrato sobre a estrutura real

## 1. Decisão de Plataforma (D7 = Opção D)

**Estratégia:** Web primeiro, mobile depois.

| Fase | Plataforma | Justificativa |
|------|-----------|---------------|
| v1.0 | Web (React + Vite) | Ciclo de desenvolvimento mais rápido; valida produto antes de investir em mobile |
| v2.0 | React Native (Expo) | Reaproveitamento de lógica e componentes do web |

## 2. Stack de Frontend

| Componente | Tecnologia |
|-----------|-----------|
| Framework | React 18 + Vite |
| Linguagem | TypeScript |
| Roteamento | React Router v6 |
| Estado global | Zustand |
| HTTP client | openapi-fetch |
| Testes unitários | Vitest + Testing Library |
| Testes E2E | Playwright |
| Estilo | Tailwind CSS |
| Componentes | shadcn/ui |

## 3. Regra Fundamental — Frontend consome apenas contratos OpenAPI

**O frontend nunca chama endpoints não documentados no contrato OpenAPI.**

Todo cliente HTTP é **gerado automaticamente** a partir do contrato:

```bash
# Gerar tipos TypeScript e cliente a partir do OpenAPI
npx openapi-typescript contracts/openapi/openapi.yaml -o frontend/src/api/schema.d.ts
# client.ts instancia openapi-fetch usando os tipos gerados em schema.d.ts
```

Qualquer endpoint novo no frontend → contrato OpenAPI deve ser atualizado primeiro.

## 4. Organização de Pastas

```
frontend/
  src/
    api/
      schema.d.ts           ← gerado automaticamente do OpenAPI (não editar)
      client.ts             ← cliente HTTP tipado (gerado)
      hooks/                ← React Query hooks por módulo
        useTraining.ts
        useUsers.ts
        ...
    features/               ← um diretório por feature do FEATURE_REGISTRY
      training/
        components/         ← componentes de UI da feature
        pages/              ← páginas/rotas da feature
        utils.ts            ← helpers locais da feature
    shared/
      components/           ← componentes reutilizáveis (design system)
      layouts/              ← layouts de página
      utils/                ← helpers globais
    App.tsx
    main.tsx
  public/
  index.html
  vite.config.ts
  tailwind.config.ts
  tsconfig.json
```

## 5. Regras de Desenvolvimento

### R1 — Types derivados do contrato, nunca manuais
Tipos TypeScript de request/response vêm exclusivamente de `schema.d.ts` (gerado do OpenAPI).
Nunca definir manualmente interfaces que repliquem shapes da API.

### R2 — Uma feature = uma pasta em `src/features/`
Cada feature do `FEATURE_REGISTRY.yaml` tem sua própria pasta.
Sem features cross-cutting — compartilhar via `shared/`.

### R3 — Sem chamadas HTTP fora de `api/hooks/`
Todas as chamadas à API passam pelos hooks em `api/hooks/`.
Componentes nunca chamam `fetch` ou o client HTTP diretamente.

### R4 — Estado do servidor via React Query
Estado derivado de dados da API → React Query (cache, loading, error).
Estado de UI local → useState.
Estado global de app (auth, preferências) → Zustand.

### R5 — Testes obrigatórios para cada feature
Toda feature implementada requer:
- Testes unitários dos componentes principais (Vitest + Testing Library)
- Ao menos 1 teste E2E do fluxo principal (Playwright)

## 6. Gate — FRONTEND_CONTRACT_GATE

O gate verifica que:
1. `frontend/src/api/schema.d.ts` foi gerado do OpenAPI e está atualizado
2. Nenhum endpoint hardcoded em componentes (apenas via hooks)
3. Tipos de API derivam de `schema.d.ts` (sem interfaces duplicadas)
4. `package.json` inclui script `gen:api` para regenerar o cliente

Se `frontend/` não existir, o gate deve permanecer `SKIP_NOT_APPLICABLE` e o worker continua congelado.

Gate registrado em: `docs/_canon/gates/GATES_REGISTRY.yaml`

## 7. Geração de Código Frontend

Worker: `.contract_driven/agent_prompts/generate_frontend.prompt.md`
Acionado via orchestrator com `task_type: generate_frontend`

O worker recebe:
- `module` — módulo canônico
- `feature` — ID da feature no FEATURE_REGISTRY (ex: FT-001)
- `layer` — `components` | `pages` | `hooks` | `all`

## 8. Conexão com o Pipeline

```
Contrato OpenAPI atualizado
    ↓
Rodar: npx openapi-typescript → regenera schema.d.ts
    ↓
generate_frontend worker gera components/pages/hooks
    ↓
Testes unitários + E2E
    ↓
FRONTEND_CONTRACT_GATE PASS
    ↓
Deploy (via DEPLOY_PIPELINE.md)
```
