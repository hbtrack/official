# Google API Design Guide — Referências para HB Track

Este documento contém referências às melhores práticas de design de API do Google, aplicáveis ao HB Track.

## Referências

- [Google API Design Guide](https://cloud.google.com/apis/design)
- [Google API Improvement Proposals (AIPs)](https://google.aip.dev/)

## Convenções aplicadas no HB Track

### Nomenclatura de recursos
- Recursos são substantivos no plural: `/training-sessions`, `/matches`, `/teams`
- IDs são UUIDs v4 canônicos

### Métodos padrão
- `GET /resources` — listar
- `GET /resources/{id}` — obter
- `POST /resources` — criar
- `PATCH /resources/{id}` — atualizar parcial
- `DELETE /resources/{id}` — deletar

### Paginação
- Segue AIP-158: `page_size`, `page_token`, `next_page_token`

### Ordenação
- Segue AIP-132: `order_by` com campos separados por vírgula

### Filtros
- Segue AIP-160: sintaxe de filtro estruturada

## Desvios documentados

Nenhum desvio documentado até o momento.
