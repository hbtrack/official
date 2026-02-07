Você é o AGENTE com acesso total ao workspace. 

TAREFA: Analisar o módulo [training] e atualizar seu CONTRATO REAL.

1. Leia todos os arquivos em src/app/(admin)/[training]/**
2. Leia middleware.ts e identifique regras que afetam este módulo
3. Leia lib/api/ e identifique endpoints relacionados
4. Leia o Prisma schema para modelos relacionados
5. Leia testes e2e relacionados ao módulo
6. Leia as regras do sistema que possam afetar este módulo em C:\HB TRACK\Hb Track - Fronted\tests\e2e\training\system_rules.md

7. Atualize: Hb Track - Fronted\tests\e2e\training\training-CONTRACT.md 
8. Atualize os testes e2e em C:\HB TRACK\Hb Track - Fronted\tests\e2e\training\training-e2e.test.ts para refletir o CONTRATO REAL ATUALIZADO.

contendo: 

## CONTRATO REAL DO MÓDULO [training]

### Rotas e Navegação
- Rota principal: [URL]
- Subrotas: [lista]
- Redirects: [de → para, condições]
- 404: [quando acontece]

### Autenticação e Autorização
- Middleware:  [regras]
- Roles permitidos: [lista]
- Comportamento sem auth: [redirect para onde]
- Comportamento com role errado: [401/403]

### Server Components e Data Fetching
- Quais pages são Server Components
- APIs chamadas no servidor:  [lista]
- Cookies usados: [lista]
- Cache strategy: [no-store, revalidate]

### Client Components e Interações
- Formulários:  [lista + validações]
- Ações: [criar, editar, deletar, etc.]
- Estados: [loading, error, empty]
- Feedback: [toasts, redirects]

### Fluxos de Dados (CRUD)
Para cada entidade:
- CREATE: [endpoint, payload, validações, resposta]
- READ: [endpoint, params, paginação]
- UPDATE: [endpoint, payload, validações]
- DELETE: [endpoint, soft/hard delete]

### Dependências com Outros Módulos
- [lista de relações]

### Edge Cases e Bugs Conhecidos
- [liste qualquer TODO, FIXME, try/catch vazio, comportamento estranho]

Não invente.  Se algo não estiver implementado, escreva "NÃO IMPLEMENTADO". 