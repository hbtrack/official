# ADR-001: Adotar Contract-Driven Development como modelo de desenvolvimento

- Status: Accepted
- Date: 2026-03-11
- Deciders: Equipe HB Track
- Tags: governance, cdd, methodology

## Context

O HB Track é uma plataforma sports-tech multi-módulo com 16 domínios canônicos, API HTTP pública, eventos assíncronos e UI. Em modelos de desenvolvimento tradicionais, o código e a documentação tendem a divergir ao longo do tempo. Agentes de IA que atuam no desenvolvimento sem documentação estruturada introduzem inferências não documentadas e criam superfícies públicas sem contrato explícito.

## Decision

Adotar Contract-Driven Development (CDD) como modelo de desenvolvimento obrigatório. Nenhum componente público nasce primeiro no código: contratos OpenAPI, invariantes documentadas e schemas canônicos precedem a implementação.

A trilogia normativa (`.contract_driven/CONTRACT_SYSTEM_LAYOUT.md`, `.contract_driven/CONTRACT_SYSTEM_RULES.md`, `.contract_driven/GLOBAL_TEMPLATES.md`) é a fonte primária de regras. Agentes de IA são proibidos de inferir módulos, endpoints, fields, eventos, workflows ou regras de negócio sem artefato normativo explícito.

## Consequences

### Positive
- Interface pública rastreável: toda rota, schema e evento tem contrato antes de existir no código.
- Inferência proibida: agentes bloqueiam com código de erro explícito em vez de inventar comportamento.
- Governança estável: hierarquia de precedência clara entre contratos técnicos, canon global e implementação.
- Testabilidade contratual: Schemathesis, Spectral e Redocly validam contratos antes de testes de unidade.

### Negative
- Custo de entrada elevado: cada módulo exige artefatos mínimos antes da primeira linha de código.
- Overhead em decisões de design triviais: mesmo campos simples exigem schema canônico.

## Alternatives Considered

- **API-first sem governança normativa**: permite divergência gradual entre contrato e código; rejeitado.
- **Documentação após implementação**: invalida contratos como fonte de verdade; rejeitado.
- **OpenAPI gerado a partir do código**: contrato vira derivado do código, inverte a hierarquia de soberania; rejeitado.

## Links

- Related docs: `.contract_driven/CONTRACT_SYSTEM_RULES.md`, `.contract_driven/CONTRACT_SYSTEM_LAYOUT.md`, `docs/_canon/SYSTEM_SCOPE.md`
- Related contracts: `contracts/openapi/openapi.yaml`