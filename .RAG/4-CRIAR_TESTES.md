Você é o Opus 4.5 com acesso total ao workspace.

TAREFA: Criar suite de testes E2E para o módulo [teams].

CONTEXTO: Você já leu e documentou o contrato real em docs/modules/[teams]-CONTRACT.md

REGRAS OBRIGATÓRIAS:

❌ PROIBIDO try/catch para mascarar falhas
❌ PROIBIDO sleeps ou timeouts fixos
❌ PROIBIDO asserts tipo "ou" (expect(a || b))
✅ USE page.waitForURL para redirects
✅ USE expect(locator).toBeVisible para elementos
✅ USE data-testid (adicione se não existir)
✅ Cada teste cria seus próprios dados via API
✅ Testes rodam isolados (não dependem de ordem)
ESTRUTURA OBRIGATÓRIA: Crie tests/e2e/[teams]/ com os arquivos:

[teams].routing.spec.ts

Navegação entre rotas
Redirects canônicos
URLs legadas
404 para IDs inválidos
F5/reload sem loops
[teams].auth.spec.ts

Sem auth → redirect /signin com callbackUrl
Com auth → acesso permitido
Role errado → 403
[teams].rbac.spec.ts

Para cada role (admin, user, etc. ):
O que pode ver
O que pode criar/editar/deletar
O que retorna 403
[teams].crud.spec.ts

Criar entidade (validações)
Editar entidade (persistência)
Listar (estados: vazio, com dados, paginação)
Deletar/arquivar (se existir)
[teams].states.spec.ts

Estado vazio
Loading states
Error boundaries
Validações de formulário
FORMATO DE CADA SPEC:

TypeScript
/**
 * CONTRATO REAL (derivado de docs/modules/[teams]-CONTRACT.md):
 * - [regra 1]
 * - [regra 2]
 * - ... 
 */

import { test, expect } from '@playwright/test';
import { loginViaAPI, create[Entidade]ViaAPI } from '../helpers/api';

test.describe('[Módulo] - [Aspecto]', () => {
  let authToken: string;
  let [entidade]Id: string;

  test.beforeAll(async () => {
    authToken = await loginViaAPI('admin@test.com', 'senha');
    [entidade]Id = await create[Entidade]ViaAPI(authToken, { name: `e2e-${Date.now()}` });
  });

  test('deve [comportamento específico]', async ({ page }) => {
    // Arrange
    await page.goto('/[módulo]');
    
    // Act
    // ... 
    
    // Assert (expectativa única, determinística)
    await expect(page).toHaveURL(/\/[modulo]\/[regex-esperado]/);
    await expect(page. locator('[data-testid="elemento"]')).toBeVisible();
  });
});
PARA CADA SPEC:

Leia o contrato real
Implemente os testes
Identifique data-testids necessários (NÃO adicione ainda ao código)
Marque com test.skip se funcionalidade não existir (+ comentário explicando)
ENTREGUE:

Conteúdo de cada spec
Lista de data-testids necessários por componente
Lista de testes pulados (skip) e motivo
