---
task_type: generate_frontend
version: "1.0.0"
status: FROZEN
frozen_reason: "Frontend paths não canonizados - awaiting real workspace structure"
requires: [ADR-030, FRONTEND_CONTRACT.md, OPENAPI_ROOT_MODULE_SYNC_GATE=PASS]
stack: react_vite_typescript
---

# generate_frontend — Worker de Geração de Código Frontend

⚠️ **WORKER CONGELADO** ⚠️

Este worker está temporariamente congelado até que:
1. A estrutura real de frontend seja implementada no workspace
2. FRONTEND_CONTRACT.md seja validado empiricamente
3. Stack final (React/Vite vs Next.js vs React Native) seja decidida em ADR

**Não executar este worker até implementação da estrutura de frontend no workspace.**

> **Nota**: Paths mencionados neste prompt (ex: `frontend/src/`) são placeholders da estrutura planejada.

---

## Pré-requisitos obrigatórios

Antes de executar este worker, verificar:

1. **ADR-030** existe em `docs/_canon/decisions/`
2. **FRONTEND_CONTRACT.md** existe em `docs/_canon/`
3. **Contrato OpenAPI** do módulo existe e está validado (gate `OPENAPI_ROOT_MODULE_SYNC_GATE` PASS)
4. **FEATURE_REGISTRY.yaml** contém a feature alvo com status `validated` ou superior
5. `contracts/openapi/openapi.yaml` está atualizado

Se qualquer pré-requisito estiver ausente → emitir bloqueio correspondente e parar.

---

## Input esperado

```
module:    <módulo canônico — ex: training>
feature:   <ID da feature no FEATURE_REGISTRY — ex: FT-001>
layer:     <camada a gerar: hooks | components | pages | all>
```

---

## Fase GF1 — Montagem de Contexto

Carregar **apenas** os artefatos necessários para a feature alvo:

```
contracts/openapi/paths/<module>.yaml         # endpoints do módulo
contracts/openapi/components/schemas/         # schemas de response/request
docs/_canon/FEATURE_REGISTRY.yaml            # feature → endpoints → descrição
docs/_canon/FRONTEND_CONTRACT.md             # regras de organização e stack
docs/_canon/DESIGN_SYSTEM.md                # tokens de design (se existir)
```

---

## Fase GF2 — Regeneração do Cliente OpenAPI

Antes de gerar código, verificar se `frontend/src/api/schema.d.ts` existe e está atualizado:

```bash
# Se não existir ou estiver desatualizado:
npx openapi-typescript contracts/openapi/openapi.yaml \
  --output frontend/src/api/schema.d.ts
```

O path de output é sempre `frontend/src/api/schema.d.ts`. Nunca editar este arquivo manualmente.

---

## Fase GF3 — Geração de Hooks (React Query)

Para cada endpoint da feature identificado no FEATURE_REGISTRY:

```typescript
// frontend/src/api/hooks/use<Module>.ts

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { client } from '../client';
import type { paths } from '../schema';

/**
 * Hook: <operação em português>
 * Feature: <feature_id> — <feature_name>
 * Endpoint: <METHOD> <path>
 */
export function use<OperationName>(<params>) {
  return useQuery({
    queryKey: ['<module>', '<resource>', <params>],
    queryFn: async () => {
      const { data, error } = await client.<METHOD>('<path>', {
        params: { path: { ... }, query: { ... } }
      });
      if (error) throw error;
      return data;
    },
  });
}

// Para mutações (POST/PUT/PATCH/DELETE):
export function use<MutationName>() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (body: paths['<path>']['<method>']['requestBody']['content']['application/json']) => {
      const { data, error } = await client.<METHOD>('<path>', { body });
      if (error) throw error;
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['<module>'] });
    },
  });
}
```

**Regra:** Os tipos de body/params/response vêm SEMPRE de `schema.d.ts`. Nunca definir interfaces manualmente para shapes de API.

---

## Fase GF4 — Geração de Componentes

Para cada componente identificado na feature:

```typescript
// frontend/src/features/<module>/components/<ComponentName>.tsx

import type { components } from '../../api/schema';

// Tipos derivados do contrato OpenAPI
type <Entity> = components['schemas']['<SchemaName>'];

interface <ComponentName>Props {
  <entity>: <Entity>;
  onAction?: (id: string) => void;
}

export function <ComponentName>({ <entity>, onAction }: <ComponentName>Props) {
  return (
    // JSX aqui
  );
}
```

**Regra de nomenclatura:**
- Componentes: PascalCase (`TrainingSessionCard`)
- Hooks: camelCase com prefixo `use` (`useTrainingSessions`)
- Arquivos: kebab-case (`training-session-card.tsx`)

---

## Fase GF5 — Geração de Páginas

Para cada rota associada à feature:

```typescript
// frontend/src/features/<module>/pages/<PageName>Page.tsx

import { use<OperationName> } from '../../api/hooks/use<Module>';
import { <ComponentName> } from '../components/<ComponentName>';

export function <PageName>Page() {
  const { data, isLoading, error } = use<OperationName>();

  if (isLoading) return <LoadingState />;
  if (error) return <ErrorState error={error} />;

  return (
    <div>
      {/* Página aqui */}
    </div>
  );
}
```

**Regras de página:**
- Páginas nunca fazem chamadas HTTP diretamente — apenas via hooks
- Páginas recebem dados via hooks e delegam renderização para componentes
- Tratamento de loading/error obrigatório em toda página com chamada assíncrona

---

## Fase GF6 — Geração de Testes

### Teste unitário de componente (Vitest + Testing Library)

```typescript
// frontend/src/features/<module>/components/<ComponentName>.test.tsx

import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { <ComponentName> } from './<ComponentName>';

describe('<ComponentName>', () => {
  it('renderiza corretamente com dados válidos', () => {
    const mock<Entity> = {
      // dados mínimos válidos derivados do schema
    };
    render(<ComponentName> <entity>={mock<Entity>} />);
    expect(screen.getByRole('...')).toBeInTheDocument();
  });
});
```

### Teste E2E do fluxo principal (Playwright)

```typescript
// frontend/e2e/<feature-slug>.spec.ts

import { test, expect } from '@playwright/test';

test('<nome da feature em português> — fluxo principal', async ({ page }) => {
  await page.goto('/<rota-da-feature>');
  // ... interações
  await expect(page.getByText('...')).toBeVisible();
});
```

---

## Fase GF7 — Checklist de Saída

Antes de concluir, verificar:

- [ ] `frontend/src/api/schema.d.ts` regenerado do OpenAPI atual
- [ ] Hooks em `frontend/src/api/hooks/use<Module>.ts` criados
- [ ] Componentes em `frontend/src/features/<module>/components/` criados
- [ ] Páginas em `frontend/src/features/<module>/pages/` criadas
- [ ] Nenhum tipo de API definido manualmente (tudo via `schema.d.ts`)
- [ ] Nenhuma chamada HTTP fora dos hooks
- [ ] Testes unitários criados para componentes principais
- [ ] Ao menos 1 teste E2E do fluxo principal

---

## Atualização de SESSION_HANDOFF

Ao concluir, atualizar `SESSION_HANDOFF.md` com:
- Feature implementada no frontend e seu status
- Próxima feature a implementar
- Qualquer decisão de UX que o humano precisa tomar
- Resultado dos testes

Se SESSION_HANDOFF.md não existir, criar a partir do template em `docs/_canon/templates/SESSION_HANDOFF.template.md`.
