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

