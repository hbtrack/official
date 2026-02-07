Você é o Opus 4.5 com acesso total ao workspace.

TAREFA: Validação final end-to-end.

CHECKLIST:

Build e TypeScript

bash
npm run build
npx tsc --noEmit
✅ Sem erros

Linting

bash
npm run lint
✅ Sem warnings críticos

Testes Unitários (se existirem)

bash
npm run test
✅ 100% passing

Testes E2E Completos

bash
npx playwright test --workers=1
✅ 100% passing

Cross-browser

bash
npx playwright test --project=webkit --workers=1
npx playwright test --project=firefox --workers=1
✅ 100% passing

Smoke Test em Produção (se tiver staging)

Deploy para staging
Rode smoke tests
Valide flows críticos manualmente
ENTREGUE:

✅ Checklist completo
📊 Coverage report (se disponível)
📝 Documento final: docs/SYSTEM-READY.md contendo:
Módulos implementados e testados
Bugs corrigidos
Coverage de testes
Como rodar testes
Como fazer deploy
Code

---

## 🎯 **RESUMO DO FLUXO COMPLETO**

```mermaid
graph TD
    A[1. Mapear Arquitetura] --> B[2. Analisar Módulos]
    B --> C[3. Setup Testes]
    C --> D[4. Criar Specs]
    D --> E[5. Adicionar data-testids]
    E --> F[6. Rodar e Corrigir]
    F --> G{100% passing?}
    G -->|Não| F
    G -->|Sim| H[7. Auditar Bugs]
    H --> I[8. Validação Final]
    I --> J[✅ Sistema Pronto]