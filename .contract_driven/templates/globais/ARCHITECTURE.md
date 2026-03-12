<!-- TEMPLATE: global-canon-template | DEST: docs/_canon/ARCHITECTURE.md | SOURCE: .contract_driven/templates/globais/ARCHITECTURE.md -->

# ARCHITECTURE.md

## Objetivo
Descrever a arquitetura-alvo e a arquitetura corrente de `{{PROJECT_NAME}}`.

## Estilo Arquitetural
- Backend: `{{BACKEND_STYLE}}`
- Frontend: `{{FRONTEND_STYLE}}`
- Persistência: `{{DATA_STYLE}}`
- Integração: `{{INTEGRATION_STYLE}}`

## Princípios
1. Contrato antes da implementação
2. Evolução compatível por padrão
3. Regra de domínio explícita
4. Documentação e teste como artefatos de engenharia
5. Separação clara entre global e módulo

## Stack Base
- Backend: `{{BACKEND_STACK}}`
- Frontend: `{{FRONTEND_STACK}}`
- Banco: `{{DATABASE_STACK}}`
- Mensageria: `{{EVENT_STACK}}`
- Testes: `{{TEST_STACK}}`

## Fonte da Verdade
- API HTTP: `contracts/openapi/openapi.yaml`
- Workflows: `contracts/workflows/`
- Eventos: `contracts/asyncapi/`
- Schemas: `contracts/schemas/`

## Decisões Arquiteturais
As decisões significativas devem ser registradas em:
- `docs/_canon/decisions/ADR-*.md`

## Visões Arquiteturais
- Contexto do sistema: `C4_CONTEXT.md`
- Containers: `C4_CONTAINERS.md`

## Restrições Arquiteturais
- Não criar interface pública fora de OpenAPI
- Não criar payload estável fora de schema
- Não criar workflow multi-step relevante sem Arazzo
- Não criar regra esportiva sem rastreio para `HANDBALL_RULES_DOMAIN.md`

## Riscos Conhecidos
{{KNOWN_RISKS_MD_LIST}}

## Decisões em Aberto
{{OPEN_DECISIONS_MD_LIST}}
