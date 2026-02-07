Você é o Opus 4.5 com acesso total ao workspace.

TAREFA: Executar testes e corrigir até ficar 100% estável.

ETAPAS:

Rode: npx playwright test tests/e2e/[teams] --workers=1

Cole aqui a saída completa do terminal
Para cada teste que falhou:
a) Leia o trace/screenshot (se gerado) 
b) Identifique a causa raiz (não o sintoma) 
c) Classifique:

❌ BUG no código de produção (não no teste)
❌ FLAKINESS (race condition, timing)
❌ EXPECTATIVA ERRADA (teste não reflete contrato real)
❌ SELETOR INCORRETO


Corrija:

Se BUG no código → corrija o código de produção
Se FLAKINESS → adicione wait correto (waitForURL, waitForSelector)
Se EXPECTATIVA ERRADA → ajuste o teste para refletir contrato real
Se SELETOR INCORRETO → ajuste data-testid
Repita até 100% passing

Rode 3x em WebKit: npx playwright test tests/e2e/[teams.auth.spec.ts] --project=webkit --workers=1 (executar 3 vezes)

Se houver QUALQUER falha em 1 das 3 execuções → é flaky → corrija

ENTREGUE:

Log de todas as execuções
Lista de bugs encontrados no código de produção + correções
Lista de flakiness corrigidos + como corrigiu
Confirmação de 3 execuções webkit 100% passing