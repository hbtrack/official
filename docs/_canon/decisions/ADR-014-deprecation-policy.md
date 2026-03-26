# ADR-014: Política de Deprecação de Contratos e APIs

- Status: Accepted
- Date: 2026-03-15
- Deciders: Equipe HB Track
- Tags: api-lifecycle, deprecation, change-management, versioning
- Resolves: ARCH-008

## Context

O HB Track já possui diretrizes de evolução de API em `CHANGE_POLICY.md §7`, mas sem ADR formal definindo: períodos mínimos de notice, mecanismo de comunicação machine-readable (headers HTTP), link entre deprecação e versão de substituição, e o que constitui "breaking change" para fins de deprecação obrigatória.

Sem política formal, breaking changes podem ser feitas sem notice adequado para consumers (módulos frontend, integrações), criando instabilidade contratual. Este ADR eleva `CHANGE_POLICY.md §7` ao status normativo via ADR formal.

## Decision

### Definição de breaking change que exige deprecação formal

Uma mudança **exige** o processo de deprecação formal quando:

| Tipo de mudança | Breaking? | Deprecação obrigatória? |
|----------------|-----------|------------------------|
| Remoção de endpoint | Sim | Sim |
| Remoção de campo obrigatório em response | Sim | Sim |
| Mudança de tipo de campo (ex: `string` → `integer`) | Sim | Sim |
| Mudança semântica de campo (ex: `status` enum com novo significado) | Sim | Sim |
| Adição de campo obrigatório em request | Sim | Sim |
| Mudança de método HTTP (ex: `PUT` → `PATCH`) | Sim | Sim |
| Adição de campo opcional em response | Não | Não (recomendado comunicar) |
| Novo endpoint | Não | Não |
| Mudança de validação mais permissiva | Não | Não |

### Períodos mínimos de notice

| Tipo de consumer | Período mínimo | Observação |
|----------------|---------------|-----------|
| APIs internas (módulo→módulo) | 90 dias | Commit de deprecação como data inicial |
| APIs mobile/frontend (Next.js app) | 180 dias | Sprint cycle considerado |
| APIs externas / parceiros (futuro) | 180 dias | Até comunicação explícita de migração concluída |

O período começa na data em que o header `Deprecation` é emitido em produção.

### Mecanismo machine-readable: headers HTTP

Conforme RFC 8594 (The Deprecation HTTP Header Field) e RFC 8288 (Web Linking):

```http
Deprecation: @1780000000
Sunset: @1795000000
Link: <https://api.hbtrack.com/v2/resource>; rel="successor-version"
```

- `Deprecation`: timestamp Unix da data de deprecação.
- `Sunset`: timestamp Unix da data de remoção (pode ser ausente se não determinado).
- `Link: rel="successor-version"`: URL do endpoint substituto (obrigatório se houver substituto).

Os headers devem ser emitidos em **todas as respostas** do endpoint deprecated, em todos os ambientes (staging + produção).

### Sinalização em contrato OpenAPI

O campo deprecated em OpenAPI é obrigatório para endpoints deprecados:

```yaml
/old-endpoint:
  get:
    deprecated: true
    description: |
      **DEPRECATED** desde 2026-03-15. Use `/new-endpoint` (ver Link header).
      Remoção prevista: 2026-09-15.
    x-deprecation-date: "2026-03-15"
    x-sunset-date: "2026-09-15"
    x-successor: "/new-endpoint"
```

Extensions `x-deprecation-date`, `x-sunset-date` e `x-successor` são as canonical extensions do HB Track.

### Processo de deprecação

1. **Decisão**: registrar change request em `CHANGE_POLICY.md` (changelog).
2. **Contrato**: marcar endpoint com `deprecated: true` + extensions no `openapi.yaml`.
3. **Implementação**: adicionar middleware/decorator que emite os headers `Deprecation` + `Sunset` + `Link`.
4. **Comunicação**: registrar no CHANGELOG interno com período e substituto.
5. **Monitor**: no `Sunset` date, remover endpoint e atualizar contrato (endpoint passa para `x-removed: true` ou é excluído do YAML).

### Versionamento e deprecação

A deprecação não implica criação automática de nova versão de media type. A estratégia de versionamento (ADR-003 — media type versioning) permanece. Deprecação é sobre lifecycle de endpoint; versionamento é sobre coexistência de formatos.

### Exceções ao período mínimo

Apenas duas condições justificam remoção sem período mínimo:
1. **Vulnerabilidade de segurança crítica** (ex: endpoint expõe PHI sem autenticação).
2. **Determinação legal** (ex: LGPD enforcement pela ANPD).

Ambas exigem registro em `CHANGE_POLICY.md` com justificativa documentada.

## Consequences

### Positive
- Headers machine-readable permitem que tooling de monitor de API detecte automaticamente deprecações.
- Períodos claros de 90/180 dias dão aos consumers tempo adequado de migração.
- Elevação formal de `CHANGE_POLICY.md §7` fecha o gap entre política escrita e status normativo.

### Negative
- Exige middleware de injeção de headers em produção — não apenas marcação em OpenAPI.
- Período de 180 dias para APIs externas pode parecer excessivo quando a mudança é simples.
- Dois conjuntos de extensões (`x-deprecation-date`, etc.) precisam ser validados no gate de contrato.

## Alternatives Considered

- **Sem headers, apenas OpenAPI deprecated**: não é machine-readable em runtime — apenas em spec. Consumer na API em produção não recebe sinal. Rejeitado.
- **Versionamento de URL (v1/v2) em vez de deprecation headers**: mudança de estratégia mais ampla, incompatível com ADR-003 (media type versioning já decidido). Rejeitado neste ADR.
- **Período diferenciado por módulo**: cria complexidade operacional sem benefício claro. Período único por tipo de consumer é suficiente.

## Links

- Resolves: `docs/_canon/ARCHITECTURE_DECISION_BACKLOG.md` ARCH-008
- Formalizes: `docs/_canon/CHANGE_POLICY.md §7` — elevado a status normativo via este ADR
- Related: `docs/_canon/decisions/ADR-003-api-versioning.md` (estratégia de versionamento)
- RFC 8594: <https://datatracker.ietf.org/doc/html/rfc8594>
- RFC 8288 (Web Linking): <https://datatracker.ietf.org/doc/html/rfc8288>
