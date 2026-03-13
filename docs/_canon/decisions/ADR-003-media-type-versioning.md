# ADR-003: Versionamento de API via media type (não URL)

- Status: Accepted
- Date: 2026-03-11
- Deciders: Equipe HB Track
- Tags: api-design, versioning, breaking-change

## Context

O HB Track expõe uma API HTTP pública. Quando breaking changes são necessárias, é preciso definir como versionar a API. As estratégias mais comuns são: versionamento via URL (`/v1/`, `/v2/`), versionamento via header `Accept` (media type) ou versionamento via query param.

A SSOT de convenções/templates/validações de API (`.contract_driven/templates/api/api_rules.yaml`) proíbe versionamento na URI e orienta compatibilidade via content negotiation / media-type quando necessário.

## Decision

Usar versionamento via media type no header `Accept` e `Content-Type`, **não** via URL path. Versão no path URL (`/v1/...`) é proibida como estratégia de versionamento de API pública.

Exemplo: `Accept: application/vnd.hbtrack.v2+json`

Enquanto a plataforma estiver em v0 (pré-produção), versão não é exposta. A estratégia entra em vigor na primeira breaking change pós-v1.0.

## Consequences

### Positive
- URLs estáveis: o mesmo path serve múltiplas versões sem duplicação de rotas.
- Alinha com a SSOT de API: proibição de versão na URI + compatibilidade via media-type.
- Permite negociação de conteúdo no client sem alterar URLs em cache.

### Negative
- Maior complexidade para clientes: exige header explícito em vez de simplesmente mudar a URL.
- Menor visibilidade em logs/proxies que não inspecionam headers.
- Ferramentas de teste de API (ex: cURL básico) requerem header explícito.

## Alternatives Considered

- **URL versioning (`/v1/`, `/v2/`)**: simples de entender, mas prolifera duplicação de rotas e viola a SSOT de API (versão na URI é proibida). Rejeitado.
- **Query param (`?version=2`)**: poluí a URL e não é cacheável corretamente por proxies. Rejeitado.
- **Sem versionamento (always latest)**: impossível para clientes que precisam de compatibilidade. Rejeitado como estratégia única.

## Links

- SSOT de API: `.contract_driven/templates/api/api_rules.yaml`
- Related docs: `docs/_canon/API_CONVENTIONS.md`, `docs/_canon/CHANGE_POLICY.md`
- Related contracts: `contracts/openapi/openapi.yaml`
