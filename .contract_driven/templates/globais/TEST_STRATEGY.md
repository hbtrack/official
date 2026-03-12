<!-- TEMPLATE: global-canon-template | DEST: docs/_canon/TEST_STRATEGY.md | SOURCE: .contract_driven/templates/globais/TEST_STRATEGY.md -->

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

## Ferramentas
- `{{UNIT_TEST_TOOL}}`
- `{{INTEGRATION_TEST_TOOL}}`
- `{{CONTRACT_TEST_TOOL}}`
- `{{E2E_TEST_TOOL}}`

## Cobertura Guiada por Risco
| Área | Risco | Tipo de teste prioritário |
|---|---|---|
| {{AREA}} | {{RISK_LEVEL}} | {{TEST_TYPE}} |
