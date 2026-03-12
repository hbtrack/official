<!-- TEMPLATE: global-canon-template | DEST: docs/_canon/README.md | SOURCE: .contract_driven/templates/globais/README.md -->

# {{PROJECT_NAME}}

{{PROJECT_NAME}} é uma plataforma sports-tech orientada a contratos para gestão e operação de handebol.

## Objetivo
Descrever o sistema, sua organização documental, seus contratos e a forma correta de evoluí-lo sem quebrar compatibilidade.

## Estrutura
- `docs/_canon/SYSTEM_SCOPE.md`
- `docs/_canon/ARCHITECTURE.md`
- `docs/_canon/C4_CONTEXT.md`
- `docs/_canon/C4_CONTAINERS.md`
- `docs/_canon/MODULE_MAP.md`
- `docs/_canon/GLOBAL_INVARIANTS.md`
- `docs/_canon/CHANGE_POLICY.md`
- `docs/_canon/API_CONVENTIONS.md`
- `docs/_canon/ERROR_MODEL.md`
- `docs/_canon/UI_FOUNDATIONS.md`
- `docs/_canon/DESIGN_SYSTEM.md`
- `docs/_canon/DATA_CONVENTIONS.md`
- `docs/_canon/DOMAIN_GLOSSARY.md`
- `docs/_canon/HANDBALL_RULES_DOMAIN.md`
- `docs/_canon/SECURITY_RULES.md`
- `docs/_canon/CI_CONTRACT_GATES.md`
- `docs/_canon/TEST_STRATEGY.md`
- `docs/_canon/decisions/ADR-*.md`

## Contratos como fonte da verdade
A implementação deve derivar destes contratos e convenções:
- OpenAPI: `contracts/openapi/openapi.yaml`
- Arazzo: `contracts/workflows/`
- AsyncAPI: `contracts/asyncapi/`
- Schemas: `contracts/schemas/`

## Regras
1. Não inventar endpoint, payload, estado ou regra fora do contrato.
2. Toda mudança pública começa no contrato.
3. Toda mudança breaking deve ser explicitamente classificada.
4. Toda regra de negócio ligada ao esporte deve referenciar `HANDBALL_RULES_DOMAIN.md`.

## Como navegar
1. Leia `docs/_canon/SYSTEM_SCOPE.md`
2. Leia `docs/_canon/ARCHITECTURE.md`
3. Leia `docs/_canon/MODULE_MAP.md`
4. Leia `docs/_canon/API_CONVENTIONS.md`
5. Leia `docs/_canon/HANDBALL_RULES_DOMAIN.md`
6. Leia a pasta `contracts/`

## Status
- Projeto: `{{PROJECT_NAME}}`
- Maturidade contratual: `{{CDD_MATURITY_LEVEL}}`
- Última revisão: `{{LAST_REVIEW_DATE}}`
