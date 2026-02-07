Você é o Opus 4.5 com acesso total ao workspace.

TAREFA: Configurar infraestrutura Playwright determinística.

1. Verifique se playwright.config.ts existe e está otimizado para: 
   - workers:  1 (evitar race conditions)
   - retries: 0 (detectar flakiness)
   - projects: chromium, firefox, webkit
   - baseURL: process.env.PLAYWRIGHT_BASE_URL
   - storageState para reusar auth

2. Crie: tests/e2e/helpers/api.ts com funções:
   ```typescript
   // Baseado nas APIs reais que você leu
   export async function loginViaAPI(email:  string, password: string): Promise<string>
   export async function createTeamViaAPI(token: string, data: CreateTeamInput): Promise<string>
   export async function createUserViaAPI(data: CreateUserInput): Promise<string>
   // ...  para cada entidade principal
Crie: tests/e2e/setup/auth.setup.ts para gerar storageState:

TypeScript
// Login de usuários com diferentes roles e salvar estados
Crie: . env.test com placeholders:

Code
PLAYWRIGHT_BASE_URL=http://localhost:3000
TEST_ADMIN_EMAIL=
TEST_ADMIN_PASSWORD=
TEST_USER_EMAIL=
TEST_USER_PASSWORD=
DATABASE_URL_TEST=
Crie: tests/e2e/helpers/selectors.ts com data-testids padrão:

TypeScript
export const SELECTORS = {
  teams: {
    list: '[data-testid="teams-list-root"]',
    row: (id: string) => `[data-testid="team-row-${id}"]`,
    // ... 
  }
}
Não adicione data-testid aos componentes ainda. Apenas prepare a estrutura.

ENTREGUE:

Lista de arquivos criados
Conteúdo de cada arquivo
Próximos passos
Code

---

