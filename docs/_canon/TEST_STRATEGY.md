# TEST_STRATEGY.md

## Objetivo
Definir a estratégia de testes do sistema.

## Camadas
- unit
- integration
- contract
- workflow
- e2e
- performance (quando aplicável)

## Princípio
Contrato guia teste. Teste protege implementação. Implementação não redefine contrato.

## Estratégia por Tipo

### Unit
Valida lógica isolada.

### Integration
Valida integração entre componentes internos.

### Contract
Valida aderência da implementação ao contrato.

### Workflow
Valida fluxos multi-etapa.

### E2E
Valida jornada do usuário.

## Critérios Mínimos
- toda rota pública deve ter proteção contratual
- toda regra crítica deve ter teste correspondente
- todo módulo deve possuir matriz mínima de verificação

## Ferramentas (referência)
- unit: runner do stack (ex.: jest/vitest/pytest)
- integration: runner do stack (ex.: supertest/pytest)
- contract: Schemathesis
- e2e: Playwright ou Cypress

## Cobertura Guiada por Risco
| Área | Risco | Tipo de teste prioritário |
|---|---|---|
| Autorização (BOLA/BFLA) | Alto | contract + integration |
| Regras de domínio críticas | Alto | integration + e2e |
| UI (fluxos principais) | Médio | e2e |

## TDD Operacional

**Fonte normativa**: `.contract_driven/CONTRACT_SYSTEM_RULES.md §26.4`

Quando o comportamento a implementar é verificável por oráculo executável (teste, script ou gate existente), o ciclo RED → GREEN é obrigatório antes de marcar a tarefa como Done.

**Escopo**: protocolo operacional "quando aplicável". Não é enforcement automático. Se enforcement real for necessário, abrir issue separada com teste vermelho/verde explícito antes de codificar.

**Oráculo verificável sempre**: qualquer implementação com comportamento especificável deve ter pelo menos um teste que falha sem a implementação e passa com ela.

