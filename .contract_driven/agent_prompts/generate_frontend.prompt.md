---
task_type: generate_frontend
version: "1.0.0"
status: FROZEN
frozen_reason: "Frontend real existe, mas a reimplementação canônica ainda não passou no FRONTEND_CONTRACT_GATE"
requires: [ADR-030, FRONTEND_CONTRACT.md, UX_BRAND_CONTRACT.md, UX_SHELL_CONTRACT.md, AUTH_EXPERIENCE_CONTRACT.md, NAVIGATION_VISIBILITY_CONTRACT.md, OPENAPI_ROOT_MODULE_SYNC_GATE=PASS]
stack: react_vite_typescript
---

# generate_frontend — Worker de Geração de Código Frontend

⚠️ **WORKER CONGELADO** ⚠️

Este worker está temporariamente congelado até que:
1. `FRONTEND_CONTRACT.md` seja validado empiricamente
2. `FRONTEND_CONTRACT_GATE` passe contra o workspace real
3. haja sign-off explícito para descongelar o worker

**Não executar este worker enquanto o frontend real permanecer fora do contrato canônico.**

> **Nota**: Paths mencionados neste prompt (ex: `frontend/src/`) descrevem o target-state de implementação. O workspace real já existe, mas ainda precisa convergir aos contratos e ao `FRONTEND_CONTRACT_GATE`.

---

## Pré-requisitos obrigatórios

Antes de executar este worker, verificar:

1. **ADR-030** existe em `docs/_canon/decisions/`
2. **FRONTEND_CONTRACT.md** existe em `docs/_canon/`
3. **Contrato OpenAPI** do módulo existe e está validado (gate `OPENAPI_ROOT_MODULE_SYNC_GATE` PASS)
4. **FEATURE_REGISTRY.yaml** contém a feature alvo com status `validated` ou superior
5. `contracts/openapi/openapi.yaml` está atualizado
6. `frontend/` e `package.json` com scripts/toolchain frontend reais existem no workspace
7. `contracts/openapi/paths/identity_access.yaml` materializa forgot/reset/new-password/confirm-reset quando a tarefa tocar auth/shell base
8. `.env.example` declara `FRONTEND_URL`, `RESEND_*` e `CLOUDINARY_*` como readiness ativa do target-state
9. A superfície soberana de perfil expõe campo canônico de avatar
10. `FRONTEND_CONTRACT_GATE` está `PASS`

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
docs/_canon/UX_BRAND_CONTRACT.md            # branding, tipografia, tokens, assets
docs/_canon/UX_SHELL_CONTRACT.md            # shell oficial autenticada
docs/_canon/AUTH_EXPERIENCE_CONTRACT.md     # auth experience normativa
docs/_canon/NAVIGATION_VISIBILITY_CONTRACT.md # taxonomia visual e rollout
```

---

## Fase GF2 — Regeneração do Cliente OpenAPI

Antes de gerar código, verificar se `frontend/src/api/schema.d.ts` existe e está atualizado:

```bash
# Se não existir ou estiver desatualizado:
npm run api:generate
```

O path de output é sempre `frontend/src/api/schema.d.ts`. Nunca editar este arquivo manualmente.

---

## Regra transversal — Shell/Auth do primeiro batch

Se a tarefa tocar `App.tsx`, layouts compartilhados, auth pages ou navegação base, a implementação deve refletir exatamente o primeiro batch canônico:

- grupos: `Início`, `Organização`, `Planejamento Técnico`, `Jogo e Competição`, `Performance e Saúde`, `Administração`
- módulos ativos: `Dashboard`, `Teams`, `Seasons`, `Training`, `Users`, `Conta e Acesso`
- módulos visíveis porém desabilitados: `Competitions`, `Matches`, `Scout`, `Video`, `Wellness`, `Medical`, `Exercises`, `Analytics`, `Reports`, `AI Ingestion`, `Audit`
- top bar: `Breadcrumbs`, `Command palette`, `Notificações`, `User menu`
- auth: `generated/images/auth-logo.svg`, `generated/images/auth-logo-dark.svg`, tagline `Dados que decidem jogos`
- avatar: renderizar avatar processado quando disponível e fallback para iniciais apenas quando necessário
- reset de senha: alinhar o frontend ao fluxo real com `Resend` e `FRONTEND_URL`

Qualquer desvio dessa matriz deve ser tratado como bloqueio, não como liberdade de implementação.

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
- [ ] Shell/auth do primeiro batch respeitam a matriz visual canônica quando a tarefa tocar essas superfícies
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
