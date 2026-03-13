# Adidas API Guidelines — Referências para HB Track

Este documento contém referências às diretrizes de API da Adidas, aplicáveis ao HB Track.

## Referências

- [Adidas API Guidelines](https://adidas.gitbook.io/api-guidelines/)

## Convenções aplicadas no HB Track

### Versionamento
- Media type versioning via `Accept: application/vnd.hbtrack.v1+json`
- Segue ADR-003 (media type versioning)

### HAL/HATEOAS
- Links hipermídia em respostas quando aplicável
- `_links` e `_embedded` para navegação

### Suporte a parciais
- PATCH com JSON Merge Patch (RFC 7396)
- Suporte a campos seletivos via `fields` query param

### Rate limiting
- Headers: `X-Rate-Limit-Limit`, `X-Rate-Limit-Remaining`, `X-Rate-Limit-Reset`

### Cache
- ETags para validação de cache
- `Cache-Control` headers apropriados

## Desvios documentados

- HB Track usa UUID v4 em vez de ULID: ver ADR-002

## Alinhamento canônico

Todas as diretrizes Adidas relevantes estão refletidas em:
- `.contract_driven/templates/api/api_rules.yaml`
- `docs/_canon/API_CONVENTIONS.md`
