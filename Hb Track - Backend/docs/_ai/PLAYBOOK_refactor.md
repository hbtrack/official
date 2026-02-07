# PLAYBOOK — REFACTOR (somente com [ALLOW_REFACTOR])

## Gate
Sem [ALLOW_REFACTOR] no pedido do usuário, NÃO executar refactor modular.

## Objetivo
Melhorar estrutura/legibilidade/performance sem alterar comportamento (a menos que explicitado).

## Procedimento
1) Delimitar escopo ("cut line")
- O que entra e o que não entra no refactor (arquivos/módulos).
- Proibir mudanças de contrato (OpenAPI) sem pedido explícito.

2) Estratégia incremental
- Passo 1: refactor mecânico (renome, extração) + checks
- Passo 2: refactor estrutural (camadas) + checks
- Passo 3: limpeza final + checks

3) Evidência e verificação
- Antes/depois: rodar checks.
- Se não houver testes, criar pelo menos 1 teste de caracterização (pytest) em ponto crítico.

## Formato de saída
Evidências:
- <paths>

Plano incremental:
- <3–6 passos>

Mudança:
- <patch por etapa>

Checks:
- <comandos e resultados por etapa>