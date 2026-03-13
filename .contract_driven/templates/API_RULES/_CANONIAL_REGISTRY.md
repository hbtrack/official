# CANONICAL_TYPE_REGISTRY v2.1.2 — Registro Canônico de Tipos

**Versão**: 2.1.1 (arquivo v2.1.2)  
**SSOT**: `.contract_driven/templates/api/CANONICAL_TYPE_REGISTRY.v2.1.2.yaml`  
**Status**: `FINAL_CANONICAL_FLATTENED_LOCKED`  
**Última atualização**: 2026-03-12

---

## ⚠️ AVISO: Artefato Canônico Achatado (Flattened)

Este artefato foi **achatado para consumo direto por agentes** e está **travado** (LOCKED).

### Características

```yaml
status: FINAL_CANONICAL_FLATTENED_LOCKED
notes:
  - Flattened for direct agent consumption
  - Each semantic type is self-contained
  - Use canonical_type_ref exactly as declared here
  - Pagination and idempotency infrastructure fields are also canonical 
    and must be typed here to prevent agent choice
```

**Regras de Uso**:
- ✅ Cada tipo semântico é **autocontido** (self-contained)
- ✅ Use `canonical_type_ref` **exatamente como declarado** aqui
- ✅ Campos de infraestrutura (paginação, idempotência) são **canônicos** e devem ser tipados aqui
- ❌ Agentes **não podem escolher** tipos alternativos para campos canônicos

---

## 1. Objetivo

Este registro define **tipos canônicos** para o HB Track, garantindo:

1. **Consistência semântica** — `athleteId` sempre tem o mesmo tipo em todo o sistema
2. **Prevenção de divergência** — Agentes não podem improvisar tipos
3. **Rastreabilidade** — Cada tipo tem um identificador versionado (`core.athlete.id.v1`)
4. **Evolução controlada** — Mudanças requerem nova versão do tipo

---

## 2. Estrutura de Tipos

### 2.1. Tipos Primitivos Resolvidos (Base)

Tipos base que servem como foundation para tipos semânticos:

| Tipo Resolvido | Tipo Primitivo | Formato | Nullable | Constraints | Escala |
|----------------|----------------|---------|----------|-------------|--------|
| **Identifier** | string | uuid | ❌ | - | - |
| **ExternalIdentifier** | string | - | ❌ | - | - |
| **SourceIdentifier** | string | - | ❌ | - | - |
| **Timestamp** | string | date-time | ❌ | - | - |
| **Date** | string | date | ❌ | - | - |
| **Count** | integer | - | ❌ | min: 0 | - |
| **DecimalSeconds** | number | - | ❌ | min: 0 | seconds_decimal |
| **Percentage100** | number | - | ❌ | min: 0, max: 100 | 0_to_100 |
| **Ratio01** | number | - | ❌ | min: 0, max: 1 | 0_to_1 |

---

## 3. Tipos Semânticos (Domínio)

### 3.1. Identificadores de Entidades Core

| Tipo Semântico | Nome Canônico | Tipo Base | Formato | Descrição |
|----------------|---------------|-----------|---------|-----------|
| `core.athlete.id.v1` | `athleteId` | string | uuid | ID de atleta |
| `core.team.id.v1` | `teamId` | string | uuid | ID de equipe |
| `core.match.id.v1` | `matchId` | string | uuid | ID de partida |
| `core.match_event.id.v1` | `matchEventId` | string | uuid | ID de evento de partida |
| `core.scout_event.id.v1` | `scoutEventId` | string | uuid | ID de evento de scout |

**Uso**:
```yaml
# OpenAPI Schema
athleteId:
  type: string
  format: uuid
  description: "ID do atleta (core.athlete.id.v1)"
```

---

### 3.2. Identificadores de Rastreabilidade

| Tipo Semântico | Nome Canônico | Tipo Base | Formato | Descrição |
|----------------|---------------|-----------|---------|-----------|
| `core.request.id.v1` | `requestId` | string | uuid | ID de requisição HTTP |
| `core.correlation.id.v1` | `correlationId` | string | uuid | ID de correlação cross-service |
| `core.external.id.v1` | `externalId` | string | - | ID de sistema externo |
| `core.source.id.v1` | `sourceId` | string | - | ID de fonte de dados |

**Uso**:
```yaml
# OpenAPI Header
X-Request-ID:
  schema:
    type: string
    format: uuid
  description: "Request ID (core.request.id.v1)"
```

---

### 3.3. Timestamps e Sequências

| Tipo Semântico | Nome Canônico | Tipo Base | Formato | Descrição |
|----------------|---------------|-----------|---------|-----------|
| `core.sequence.number.v1` | `sequenceNumber` | integer | - | Número de sequência (min: 1) |
| `core.occurred_at.v1` | `occurredAt` | string | date-time | Timestamp de ocorrência do evento |
| `core.recorded_at.v1` | `recordedAt` | string | date-time | Timestamp de registro no sistema |
| `core.processing_at.v1` | `processingAt` | string | date-time | Timestamp de início de processamento |

**Uso**:
```yaml
# Event Schema (AsyncAPI)
occurredAt:
  type: string
  format: date-time
  description: "Quando o evento ocorreu no mundo real (core.occurred_at.v1)"
recordedAt:
  type: string
  format: date-time
  description: "Quando o sistema registrou o evento (core.recorded_at.v1)"
```

---

### 3.4. Métricas de Tempo (Decimais)

| Tipo Semântico | Nome Canônico | Tipo Base | Min | Max | Escala | Descrição |
|----------------|---------------|-----------|-----|-----|--------|-----------|
| `core.clock.seconds.v1` | `clockSeconds` | number | 0 | - | seconds_decimal | Relógio do jogo em segundos |
| `core.video_timestamp.seconds.v1` | `videoTimestampSeconds` | number | 0 | - | seconds_decimal | Timestamp no vídeo |

**Uso**:
```yaml
# Match Event
clockSeconds:
  type: number
  minimum: 0
  description: "Tempo de jogo em segundos (core.clock.seconds.v1)"
  example: 1847.5  # 30min 47.5s
```

---

### 3.5. Métricas de Confiança e Compliance

| Tipo Semântico | Nome Canônico | Tipo Base | Min | Max | Escala | Descrição |
|----------------|---------------|-----------|-----|-----|--------|-----------|
| `core.confidence.ratio.v1` | `confidenceRatio` | number | 0 | 1 | 0_to_1 | Confiança do modelo de IA (0.0 a 1.0) |
| `core.compliance.percentage.v1` | `compliancePercentage` | number | 0 | 100 | 0_to_100 | Percentual de compliance (0 a 100) |

**Uso**:
```yaml
# AI Detection Result
confidenceRatio:
  type: number
  minimum: 0
  maximum: 1
  description: "Confiança da detecção (core.confidence.ratio.v1)"
  example: 0.92
```

---

### 3.6. Paginação (Infraestrutura Canônica)

| Tipo Semântico | Nome Canônico | Tipo Base | Min | Max | Nullable | Descrição |
|----------------|---------------|-----------|-----|-----|----------|-----------|
| `core.pagination.page_size.v1` | `pageSize` | integer | 1 | 100 | ❌ | Tamanho da página (1-100) |
| `core.pagination.page_token.v1` | `pageToken` | string | - | - | ❌ | Token da página atual |
| `core.pagination.next_page_token.v1` | `nextPageToken` | string | - | - | ❌ | Token da próxima página |
| `core.pagination.next_cursor.v1` | `nextCursor` | string | - | - | ❌ | Cursor da próxima página |
| `core.pagination.total_count.v1` | `totalCount` | integer | 0 | - | ❌ | Contagem total de itens |

**⚠️ Nota**: Campos de paginação são **canônicos** e **obrigatórios** — agentes não podem escolher tipos alternativos.

**Uso**:
```yaml
# Query Parameters (GET /athletes)
parameters:
  - name: pageSize
    in: query
    schema:
      type: integer
      minimum: 1
      maximum: 100
    description: "Tamanho da página (core.pagination.page_size.v1)"
  - name: pageToken
    in: query
    schema:
      type: string
    description: "Token da página (core.pagination.page_token.v1)"

# Response
responses:
  '200':
    content:
      application/json:
        schema:
          type: object
          properties:
            athletes:
              type: array
              items:
                $ref: '#/components/schemas/Athlete'
            nextPageToken:
              type: string
              description: "Token da próxima página (core.pagination.next_page_token.v1)"
```

---

## 4. Bindings de Campos (field_bindings)

Mapeamento **canônico** de nomes de campos para tipos semânticos:

### 4.1. Identificadores

| Nome do Campo | Tipo Semântico | Uso |
|---------------|----------------|-----|
| `athleteId` | `core.athlete.id.v1` | Sempre que referenciar atleta |
| `teamId` | `core.team.id.v1` | Sempre que referenciar equipe |
| `matchId` | `core.match.id.v1` | Sempre que referenciar partida |
| `matchEventId` | `core.match_event.id.v1` | Sempre que referenciar evento de partida |
| `scoutEventId` | `core.scout_event.id.v1` | Sempre que referenciar evento de scout |

### 4.2. Rastreabilidade

| Nome do Campo | Tipo Semântico | Uso |
|---------------|----------------|-----|
| `requestId` | `core.request.id.v1` | ID de requisição HTTP |
| `correlationId` | `core.correlation.id.v1` | ID de correlação entre serviços |
| `externalId` | `core.external.id.v1` | ID de sistema externo |
| `sourceId` | `core.source.id.v1` | ID de fonte de dados |

### 4.3. Timestamps

| Nome do Campo | Tipo Semântico | Uso |
|---------------|----------------|-----|
| `sequenceNumber` | `core.sequence.number.v1` | Número de sequência |
| `occurredAt` | `core.occurred_at.v1` | Quando evento ocorreu |
| `recordedAt` | `core.recorded_at.v1` | Quando foi registrado |
| `processingAt` | `core.processing_at.v1` | Quando começou processamento |

### 4.4. Métricas de Tempo

| Nome do Campo | Tipo Semântico | Uso |
|---------------|----------------|-----|
| `clockSeconds` | `core.clock.seconds.v1` | Tempo de jogo |
| `videoTimestampSeconds` | `core.video_timestamp.seconds.v1` | Posição no vídeo |

### 4.5. Métricas de Análise

| Nome do Campo | Tipo Semântico | Uso |
|---------------|----------------|-----|
| `confidenceRatio` | `core.confidence.ratio.v1` | Confiança de IA (0-1) |
| `compliancePercentage` | `core.compliance.percentage.v1` | Compliance (0-100) |

### 4.6. Paginação

| Nome do Campo | Tipo Semântico | Uso |
|---------------|----------------|-----|
| `pageSize` | `core.pagination.page_size.v1` | Tamanho da página (request) |
| `pageToken` | `core.pagination.page_token.v1` | Token da página atual (request) |
| `nextPageToken` | `core.pagination.next_page_token.v1` | Token da próxima página (response) |
| `nextCursor` | `core.pagination.next_cursor.v1` | Cursor da próxima página (response) |
| `totalCount` | `core.pagination.total_count.v1` | Total de itens (response) |

---

## 5. Regras de Uso para Agentes

### 5.1. ✅ Uso Correto

```yaml
# 1. Consultar binding canônico
field_name = "athleteId"
semantic_type = field_bindings[field_name]  # "core.athlete.id.v1"

# 2. Resolver tipo semântico
type_def = semantic_types[semantic_type]
# {
#   primitive_type: "string",
#   format: "uuid",
#   nullable: false,
#   canonical_name: "athleteId"
# }

# 3. Aplicar no schema OpenAPI
athleteId:
  type: string
  format: uuid
  description: "ID do atleta (core.athlete.id.v1)"
```

### 5.2. ❌ Uso Incorreto

```yaml
# PROIBIDO: Improvisar tipo para campo canônico
athleteId:
  type: string   # ❌ ERRADO: faltou format: uuid
  
# PROIBIDO: Escolher tipo alternativo
pageSize:
  type: integer
  minimum: 1
  maximum: 200  # ❌ ERRADO: max deve ser 100 (canônico)

# PROIBIDO: Renomear campo canônico
athlete_id:  # ❌ ERRADO: campo canônico é "athleteId" (camelCase)
  type: string
  format: uuid
```

### 5.3. Comportamentos Obrigatórios

| Campo | Tipo Obrigatório | Justificativa |
|-------|------------------|---------------|
| `athleteId` | `string/uuid` | Consistência de IDs de atleta em todo sistema |
| `pageSize` | `integer (1-100)` | Prevenir DoS via páginas grandes |
| `occurredAt` | `string/date-time` | Rastreabilidade de eventos |
| `confidenceRatio` | `number (0-1)` | Padronização de scores de IA |

---

## 6. Convenções de Nomenclatura

### 6.1. Formato de Tipo Semântico

```
<namespace>.<entity>.<attribute>.<version>

Exemplos:
  core.athlete.id.v1
  core.pagination.page_size.v1
  core.clock.seconds.v1
```

### 6.2. Formato de Nome Canônico

- **Estilo**: `camelCase` (api_rules.yaml §canonical_conventions)
- **Padrão**: `{entity}{Attribute}` ou `{attribute}{Qualifier}`

```
Exemplos:
  athleteId         → entidade + Id
  occurredAt        → ação + At
  clockSeconds      → contexto + Unidade
  nextPageToken     → qualificador + Contexto + Token
```

---

## 7. Evolução de Tipos

### 7.1. Adicionar Novo Tipo Semântico

```yaml
# 1. Adicionar ao YAML
semantic_types:
  core.injury.id.v1:
    primitive_type: string
    format: uuid
    nullable: false
    canonical_name: injuryId

# 2. Adicionar binding
field_bindings:
  injuryId: core.injury.id.v1

# 3. Atualizar este documento
# 4. Versionar (v2.1.3 → v2.2.0 se breaking change)
```

### 7.2. Versionar Tipo Existente (Breaking Change)

```yaml
# Exemplo: mudar athleteId de UUID para ULID

# 1. Criar nova versão
semantic_types:
  core.athlete.id.v2:  # ← nova versão
    primitive_type: string
    format: ulid        # ← mudança breaking
    nullable: false
    canonical_name: athleteId

# 2. Manter v1 para compatibilidade
  core.athlete.id.v1:
    primitive_type: string
    format: uuid
    nullable: false
    canonical_name: athleteId

# 3. Atualizar binding gradualmente
field_bindings:
  athleteId: core.athlete.id.v2  # migration complete
```

---

## 8. Validação e Gates

### 8.1. Gate: CANONICAL_TYPE_COMPLIANCE

**Objetivo**: Validar que schemas OpenAPI/AsyncAPI usam tipos canônicos

**Validações**:
1. Campo `athleteId` deve ser `string/uuid` (não `integer`)
2. Campo `pageSize` deve ter `maximum: 100`
3. Campo `occurredAt` deve ser `string/date-time`
4. Campos canônicos devem usar nome exato (camelCase)

**Comando**:
```bash
python scripts/gates/check_canonical_types.py contracts/openapi/openapi.yaml
```

### 8.2. Blocos de Erro

| Código | Descrição |
|--------|-----------|
| `BLOCKED_NON_CANONICAL_TYPE` | Campo canônico usa tipo incorreto |
| `BLOCKED_RENAMED_CANONICAL_FIELD` | Campo canônico foi renomeado |
| `BLOCKED_MISSING_CANONICAL_CONSTRAINT` | Constraint obrigatório ausente (ex: pageSize max) |

---

## 9. Tabela Completa de Tipos (Referência Rápida)

| Campo Canônico | Tipo Semântico | Primitivo | Formato | Min | Max | Nullable |
|----------------|----------------|-----------|---------|-----|-----|----------|
| athleteId | core.athlete.id.v1 | string | uuid | - | - | ❌ |
| teamId | core.team.id.v1 | string | uuid | - | - | ❌ |
| matchId | core.match.id.v1 | string | uuid | - | - | ❌ |
| matchEventId | core.match_event.id.v1 | string | uuid | - | - | ❌ |
| scoutEventId | core.scout_event.id.v1 | string | uuid | - | - | ❌ |
| sequenceNumber | core.sequence.number.v1 | integer | - | 1 | - | ❌ |
| occurredAt | core.occurred_at.v1 | string | date-time | - | - | ❌ |
| recordedAt | core.recorded_at.v1 | string | date-time | - | - | ❌ |
| processingAt | core.processing_at.v1 | string | date-time | - | - | ❌ |
| requestId | core.request.id.v1 | string | uuid | - | - | ❌ |
| correlationId | core.correlation.id.v1 | string | uuid | - | - | ❌ |
| externalId | core.external.id.v1 | string | - | - | - | ❌ |
| sourceId | core.source.id.v1 | string | - | - | - | ❌ |
| clockSeconds | core.clock.seconds.v1 | number | - | 0 | - | ❌ |
| videoTimestampSeconds | core.video_timestamp.seconds.v1 | number | - | 0 | - | ❌ |
| confidenceRatio | core.confidence.ratio.v1 | number | - | 0 | 1 | ❌ |
| compliancePercentage | core.compliance.percentage.v1 | number | - | 0 | 100 | ❌ |
| pageSize | core.pagination.page_size.v1 | integer | - | 1 | 100 | ❌ |
| pageToken | core.pagination.page_token.v1 | string | - | - | - | ❌ |
| nextPageToken | core.pagination.next_page_token.v1 | string | - | - | - | ❌ |
| nextCursor | core.pagination.next_cursor.v1 | string | - | - | - | ❌ |
| totalCount | core.pagination.total_count.v1 | integer | - | 0 | - | ❌ |

**Total**: 22 tipos semânticos canônicos

---

## 10. Exemplos Práticos

### 10.1. Schema de Evento de Partida (AsyncAPI)

```yaml
MatchEventOccurred:
  type: object
  required:
    - matchEventId
    - matchId
    - sequenceNumber
    - occurredAt
    - recordedAt
    - clockSeconds
  properties:
    matchEventId:
      type: string
      format: uuid
      description: "ID do evento (core.match_event.id.v1)"
    matchId:
      type: string
      format: uuid
      description: "ID da partida (core.match.id.v1)"
    sequenceNumber:
      type: integer
      minimum: 1
      description: "Número de sequência (core.sequence.number.v1)"
    occurredAt:
      type: string
      format: date-time
      description: "Quando ocorreu (core.occurred_at.v1)"
    recordedAt:
      type: string
      format: date-time
      description: "Quando foi registrado (core.recorded_at.v1)"
    clockSeconds:
      type: number
      minimum: 0
      description: "Tempo de jogo (core.clock.seconds.v1)"
```

### 10.2. Endpoint de Lista com Paginação (OpenAPI)

```yaml
/athletes:
  get:
    operationId: listAthletes
    parameters:
      - name: pageSize
        in: query
        required: false
        schema:
          type: integer
          minimum: 1
          maximum: 100
          default: 20
        description: "Tamanho da página (core.pagination.page_size.v1)"
      - name: pageToken
        in: query
        required: false
        schema:
          type: string
        description: "Token da página (core.pagination.page_token.v1)"
    responses:
      '200':
        content:
          application/json:
            schema:
              type: object
              required:
                - athletes
              properties:
                athletes:
                  type: array
                  items:
                    type: object
                    required:
                      - athleteId
                    properties:
                      athleteId:
                        type: string
                        format: uuid
                        description: "ID do atleta (core.athlete.id.v1)"
                nextPageToken:
                  type: string
                  description: "Token da próxima página (core.pagination.next_page_token.v1)"
                totalCount:
                  type: integer
                  minimum: 0
                  description: "Total de atletas (core.pagination.total_count.v1)"
```

---

## 11. Referências Normativas

- **api_rules.yaml** § `canonical_conventions.naming.json_fields` — Naming camelCase
- **api_rules.yaml** § `design_rules.google_aip_core.pagination` — Paginação cursor-based
- **docs/_canon/DATA_CONVENTIONS.md** — Convenções de dados e tipos
- **.spectral.yaml** — Regras de lint OpenAPI (valida tipos canônicos)

---

## 12. Status e Governança

| Campo | Valor |
|-------|-------|
| **Versão** | 2.1.1 (arquivo v2.1.2) |
| **Status** | FINAL_CANONICAL_FLATTENED_LOCKED |
| **Autoridade** | Arquiteto-chefe HB Track |
| **Mudanças** | Requerem ADR + nova versão |
| **Última revisão** | 2026-03-12 |
| **Total de tipos** | 22 tipos semânticos + 9 tipos base |

---

**Assinatura**: GitHub Copilot (Claude Sonnet 4.5)  
**Evidência**: Tradução canônica de CANONICAL_TYPE_REGISTRY.v2.1.2.yaml  
**Propósito**: Registro achatado para consumo direto — tipos canônicos obrigatórios
