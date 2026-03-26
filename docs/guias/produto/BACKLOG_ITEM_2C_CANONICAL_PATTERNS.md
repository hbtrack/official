# BACKLOG ITEM 2C-1 — Consolidação de Patterns Canônicos

**Data:** 2026-03-20  
**Status:** REFERÊNCIA NORMATIVA — Fonte Única de Verdade  
**Fonte:** `.contract_driven/DOMAIN_AXIOMS.json`

---

## Parte A: Definições Normativas de Patterns

Estes são os **ÚNICOS** padrões válidos em HB Track. Qualquer campo que não corresponder a um destes padrões é uma violação.

| Pattern Name | Type | Regex / Definição | Aplicabilidade |
|---|---|---|---|
| **uuid_v4** | string | `^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$` | **Todos IDs públicos de entidade** (userId, sessionId, jobId, etc.) |
| **timestamp_utc** | string | `^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{3,6})?Z$` | **Todos campos timestamp** (createdAt, updatedAt, occurredAt, deliveredAt, etc.) |
| **date_only** | string | `^\d{4}-\d{2}-\d{2}$` | **Campos de data pura, sem hora** (endDate, startDate, birthDate) |
| **email** | string | `^[^\s@]+@[^\s@]+\.[^\s@]+$` | **Campos de email** |
| **slug_lower_kebab** | string | `^[a-z0-9]+(?:-[a-z0-9]+)*$` | **Slugs e identificadores URL-safe em minúscula** |
| **lower_snake_case** | string | `^[a-z0-9]+(?:_[a-z0-9]+)*$` | **Nomes de arquivo, documento, slug interno** |
| **upper_snake_case** | string | `^[A-Z0-9]+(?:_[A-Z0-9]+)*$` | **Símbolos de enum, constantes** |
| **camel_case** | string | `^[a-z][A-Za-z0-9]*$` | **Nomes de propriedade JSON** (openAPI/AsyncAPI) |
| **trace_id** | string | `^[A-Za-z0-9][A-Za-z0-9._:-]{7,127}$` | **IDs de rastreamento (logs, telemetria)** |
| **request_id** | string | `^[A-Za-z0-9][A-Za-z0-9._:-]{7,127}$` | **IDs de requisição HTTP** |
| **http_status_code** | integer | 100–599 (range) | **Códigos HTTP** |

---

## Parte B: Invariantes Globais de Dados

Estas regras definem qual pattern DEVE ser usado em cada tipo de campo:

| Regra | Pattern Obrigatório | Exemplo |
|---|---|---|
| Campos de data pura (sem hora) | `date_only` | `startDate`, `endDate`, `birthDate` |
| Campos de timestamp (com hora) | `timestamp_utc` | `createdAt`, `updatedAt`, `occurredAt`, `deliveredAt`, `publishedAt`, `finalizedAt` |
| Campos de ID público de entidade | `uuid_v4` | `userId`, `sessionId`, `jobId`, `teamId`, `athleteId`, `competitionId`, `matchId` |
| Nomes de propriedade JSON | `camel_case` | OpenAPI/AsyncAPI paths, schema properties |
| Nomes de enum symbol (YAML keys) | `upper_snake_case` | `ACTIVE`, `INACTIVE`, `IN_PROGRESS` |
| Nomes de campo de documento | `lower_snake_case` | Nomes de schema arquivo (`.yaml`, `.json`) |

---

## Parte C: Mapeamento de Campos com Violações (542 total)

### UUID4 Violations (~122 campos)

**Padrão:** Campo termina em `-id` ou contém semântica de identificador, mas **não tem pattern `uuid_v4` declarado**.

**Exemplos de campos:**
```
jobId, userId, sessionId, teamId, athleteId, competitionId, matchId,
exerciseId, eventId, deliveryId, entryId, clipId, segmentId, coachId,
trainingSessionId, generatedSessionId, generatedTrainingSessionId,
distributionId, distributionProfileId, edgeNodeId, homeTeamId, awayTeamId,
versionId, organizationId, and others...
```

**Regra de correção:** Se campo tem semântica de ID (termina em `-id`), **DEVE** ter `pattern: uuid_v4` em OpenAPI/AsyncAPI/JSON Schema.

### Timestamp_UTC Violations (~180 campos)

**Padrão:** Campo termina em `-At`, `-at`, `-Date`, `-Time`, mas **não tem pattern `timestamp_utc` declarado**.

**Exemplos de campos:**
```
createdAt, updatedAt, occurredAt, receivedAt, deliveredAt, 
publishedAt, finalizedAt, transcodeCompletedAt, failedAt, 
exportedAt, endedAt, decidedAt, lastAttemptAt, and others...
```

**Regra de correção:** Se campo tem semântica de timestamp (termina em `-At`, `-at`, etc.), **DEVE** ter `pattern: timestamp_utc`.

### Date_Only Violations (5 campos)

**Padrão:** Campo é data pura, mas **não tem pattern `date_only`**.

**Exemplos:** `startDate`, `endDate`

---

## Parte D: Estratégia de Correção (2C-2: Bulk Remediation)

### Casos Inequívocos (automático)

✅ **UUID4 candidates — AUTOMÁTICO quando:**
- Campo termina em `-id` (minúsculo)
- Campo é `Id`, `ID` (maiúsculo simples)
- Campo é identificador público de entidade
- Não é PII/credential (ex: não é `key`, `secret`, `token`)

✅ **Timestamp_UTC candidates — AUTOMÁTICO quando:**
- Campo termina em `-At`, `-at`, `-Date` (exceto date-only como `startDate`)
- Campo é `createdAt`, `updatedAt`, `occurredAt`, `publishedAt`, etc.

✅ **Date_Only candidates — AUTOMÁTICO quando:**
- Campo termina em `-Date` E semanticamente é data pura (não timestamp)
- Exemplo: `birthDate`, `eventDate`

### Casos Ambíguos (MANUAL REVIEW)

❓ **Casos que requerem revisão manual:**
- Campos com semântica ambígua (ex: um `-Id` que talvez não seja UUID)
- Campos com múltiplas possibilidades (ex: `date` poderia ser `date_only` ou `timestamp_utc`)
- Campos herdados ou deprecated com semântica inconsistente

---

## Parte E: Cronograma de Execução

### 2C-2: Bulk Remediation (próxima fase)
1. **Fase 1:** Detectar todos campos candidatos (UUID4 priorities)
2. **Fase 2:** Aplicar correção automática com audit trail de diff
3. **Fase 3:** Listar casos ambíguos para revisão (se houver)
4. **Fase 4:** Revalidar: 542 → 0 violações
5. **Fase 5:** Documentar casos especiais (se houver exceções)

### 2C-3: Regression Guard
- Atualizar templates de gerador para desembarcar novos artefatos COM patterns corretos
- CI enforcement: rejeitar novos campos sem pattern

---

## Referência Rápida: Checklist de Padrões

Use este checklist ao revisar cada violação:

```
[ ] Campo é ID público? → uuid_v4
[ ] Campo é timestamp (com hora)? → timestamp_utc
[ ] Campo é data pura (sem hora)? → date_only
[ ] Campo é email? → email
[ ] Campo é slug/URL-safe? → slug_lower_kebab
[ ] Campo é enum symbol? → upper_snake_case
[ ] Campo é propriedade JSON? → camel_case
```

---

**Próximo:** Item 2C-2 — Bulk Remediation Automática (aplicar padrões canônicos em massa)
