---
doc_type: canon
version: "1.0.0"
last_reviewed: "2026-03-11"
status: active
---

# Convenções de Dados — HB Track

## 1. Identificadores (IDs)

### 1.1 Padrão Canônico

- **Tipo**: UUID v4 — string, nunca number/bigint (#174, #238)
- **Formato RFC 4122**: `xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx`
- **Campo no recurso**: sempre chamado `id`
- **Referências cruzadas (API JSON)**: `<resource>Id` (ex: `teamId`, `athleteId`, `sessionId`)
- **Referências cruzadas (Banco de dados)**: `<resource>_id` (ex: `team_id`, `athlete_id`, `session_id`)
- **URL-friendly** (#228): apenas caracteres `[a-zA-Z0-9:._\-/]*`
- **Nunca expor IDs sequenciais** — IDs incrementais revelam volume de dados e são vetores de enumeração

### 1.2 Exemplos

```json
// Recurso próprio
{ "id": "550e8400-e29b-41d4-a716-446655440000" }

// Referências cruzadas
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "teamId": "550e8400-e29b-41d4-a716-446655440000",
  "athleteId": "770e8400-e29b-41d4-a716-446655440002",
  "sessionId": "880e8400-e29b-41d4-a716-446655440003"
}
```

### 1.3 Regras de Consistência

- O mesmo conceito usa sempre o mesmo nome de campo — `team_id` nunca vira `squad_id` ou `group_id` para o mesmo conceito
- Referências a recursos deletados (soft delete) são mantidas no banco — a FK aponta para o registro deletado
- É proibido misturar nomes semanticamente equivalentes para a mesma referência sem decisão formal

---

## 2. Datas e Horas

### 2.1 Padrão Canônico

- **Norma**: ISO 8601 / RFC 3339 (#169, #238)
- **Separador**: `T` maiúsculo obrigatório — nunca espaço entre data e hora
- **Sufixo UTC**: `Z` maiúsculo obrigatório — nunca `z` minúsculo, nunca `+00:00`
- **Formato completo**: `YYYY-MM-DDTHH:MM:SSZ` — ex: `2026-03-11T14:30:00Z`
- **Somente data (calendário)**: format `date` — ex: `2026-03-11`
- **Timezone**: armazenamento sempre em UTC; conversão para exibição é responsabilidade do cliente

### 2.2 Quando Usar Cada Tipo

| Situação | Tipo OpenAPI | Exemplo |
|----------|-------------|---------|
| Evento pontual no tempo (criação, início, conclusão) | `string` format `date-time` | `2026-03-11T14:30:00Z` |
| Data de calendário sem horário (data de partida, nascimento) | `string` format `date` | `2026-03-11` |
| Duração de treino ou sessão | `string` format `duration` (ISO 8601) | `PT90M` ou `P0DT1H30M` |
| Intervalo de tempo (período de temporada) | objeto com `start_at` + `end_at` | — |
| Apenas o ano (temporada anual) | `integer` format `int32` | `2026` |

### 2.3 Naming de Campos Temporais (#235)

- **Eventos no tempo**:
  - API / JSON: sufixo `At` — ex: `createdAt`, `updatedAt`, `deletedAt`, `scheduledAt`, `startedAt`, `completedAt`, `publishedAt`, `submittedAt`
  - Banco de dados: sufixo `_at` — ex: `created_at`, `updated_at`, `deleted_at`, `scheduled_at`, `started_at`, `completed_at`, `published_at`, `submitted_at`
- **Datas de calendário**:
  - API / JSON: sufixo `Date` ou `On` — ex: `birthDate`, `matchDate`, `effectiveOn`, `expiryDate`
  - Banco de dados: sufixo `_date` ou `_on` — ex: `birth_date`, `match_date`, `effective_on`, `expiry_date`
- **Janelas de tempo**:
  - API / JSON: prefixo `start` e `end` — ex: `startAt`, `endAt`, `seasonStartDate`, `seasonEndDate`
  - Banco de dados: prefixo `start_` e `end_` — ex: `start_at`, `end_at`, `season_start_date`, `season_end_date`

### 2.4 Anti-Patterns Proibidos

- `2026-03-11 14:30:00` — espaço em vez de `T`
- `2026-03-11T14:30:00z` — `z` minúsculo
- `2026-03-11T14:30:00+00:00` — offset explícito em vez de `Z`
- `1741701000` — Unix timestamp sem documentação explícita do formato

---

## 3. Naming de Campos

### 3.1 API / JSON: camelCase (SSOT)

Para contratos HTTP/OpenAPI, nomes de campos em JSON seguem **camelCase**.

- **SSOT**: `.contract_driven/templates/api/api_rules.yaml` → `hbtrack_api_rules.canonical_conventions.naming.json_fields.style`

Mapeamento de referência (API JSON ↔ Banco de dados):

| API / JSON | Banco de dados |
|-----------|----------------|
| `sessionId` | `session_id` |
| `teamName` | `team_name` |
| `athleteCount` | `athlete_count` |
| `scheduledAt` | `scheduled_at` |
| `deletedReason` | `deleted_reason` |
| `trainingLoad` | `training_load` |
| `perceivedExertion` | `perceived_exertion` |

**Regra**: mudanças globais de naming em API são potencialmente breaking changes e seguem `CHANGE_POLICY.md`.

### 3.2 Banco de Dados: snake_case

- **Tabelas**: snake_case plural — ex: `training_sessions`, `match_events`, `team_rosters`, `wellness_entries`
- **Colunas**: snake_case singular — ex: `athlete_id`, `scheduled_at`, `deleted_at`, `training_load`
- **Índices**: `ix_<tabela>_<coluna(s)>` — ex: `ix_training_sessions_team_id`, `ix_match_events_match_id_type`
- **Constraints CHECK**: `ck_<tabela>_<descricao>` — ex: `ck_training_sessions_status_valid`
- **Constraints UNIQUE**: `uq_<tabela>_<descricao>` — ex: `uq_competitions_org_name_season`
- **Foreign Keys**: `fk_<tabela>_<coluna>_ref` — ex: `fk_training_sessions_team_id_ref`
- **Primary Keys**: `pk_<tabela>` — ex: `pk_training_sessions`

### 3.3 Idioma

Identificadores técnicos sempre em inglês americano — colunas, tabelas, schemas, operationIds, field names.

---

## 4. Valores Nulos e Ausentes

### 4.1 Regras

- **null e ausente têm mesma semântica** (#123) — o sistema não distingue campo ausente de campo com valor null; clientes não devem depender dessa diferença
- **null para boolean é PROIBIDO** (#122) — um boolean é `true` ou `false`; se há terceiro estado semântico ("desconhecido"), usar enum nomeado (`UNKNOWN`, `NOT_SET`)
- **null para array vazio é PROIBIDO** (#124) — usar `[]` (array vazio); nunca retornar `null` onde um array é esperado
- **Nullable somente quando semanticamente significativo** — um campo nullable deve ter semântica clara de "ausência intencional" documentada no schema

### 4.2 Campos Nullable Canônicos

Campos que são nullable intencionalmente no HB Track:

| Campo | Tipo | Nulo significa |
|-------|------|---------------|
| `deleted_at` | `string \| null` | Registro ativo (não deletado) |
| `deleted_reason` | `string \| null` | Registro ativo |
| `completed_at` | `string \| null` | Sessão ainda não concluída |
| `end_at` | `string \| null` | Intervalo em aberto ou sessão em progresso |
| `notes` | `string \| null` | Sem notas adicionadas |
| `external_ref` | `string \| null` | Sem referência externa |

---

## 5. Enums

### 5.1 Formato dos Valores

Valores sempre UPPER_SNAKE_CASE (#240):
- Correto: `DRAFT`, `IN_PROGRESS`, `PENDING_REVIEW`, `READONLY`, `SCHEDULED`
- Proibido: `draft`, `inProgress`, `pending_review`, `ReadOnly`, `scheduled`

### 5.2 Enums Extensíveis vs. Fechados

```yaml
# Extensível — clientes devem aceitar valores futuros sem falha
status:
  type: string
  description: >
    Status da sessão de treino.
    [Extensible enum — novos valores podem ser adicionados em versões futuras.
    Clientes DEVEM aceitar e ignorar valores desconhecidos (#108)]
  examples:
    - DRAFT
    - SCHEDULED
    - IN_PROGRESS
    - PENDING_REVIEW
    - READONLY

# Fechado — conjunto definitivo e estável
gender_category:
  type: string
  description: Categoria de gênero da equipe.
  enum:
    - MALE
    - FEMALE
    - MIXED
```

### 5.3 Regras de Uso

- Enums extensíveis: usar `examples` (NUNCA `enum` keyword) para permitir evolução sem breaking change
- Enums fechados: usar `enum` apenas quando o conjunto é definitivamente fechado e estável
- Clientes DEVEM aceitar valores desconhecidos em enums extensíveis sem erro ou crash (#108)
- Nunca enum implícito — strings sem documentação no schema são proibidas
- Adicionar valor a enum extensível é non-breaking; remover valor de enum fechado é breaking

### 5.4 Enums Canônicos HB Track

| Campo | Tipo | Valores | Extensível |
|-------|------|---------|-----------|
| `training_session.status` | string | `DRAFT`, `SCHEDULED`, `IN_PROGRESS`, `PENDING_REVIEW`, `READONLY` | Sim |
| `match.status` | string | `SCHEDULED`, `IN_PROGRESS`, `HALF_TIME`, `COMPLETED`, `CANCELLED`, `POSTPONED` | Sim |
| `competition.phase` | string | `GROUPS`, `ROUND_OF_16`, `QUARTER_FINALS`, `SEMI_FINALS`, `FINAL`, `THIRD_PLACE` | Sim |
| `wellness.category` | string | `SLEEP`, `FATIGUE`, `STRESS`, `MOOD`, `MUSCLE_SORENESS`, `HYDRATION`, `NUTRITION` | Sim |
| `user.role` | string | `dirigente`, `coordenador`, `treinador`, `atleta`, `membro` | Não |

---

## 6. Números e Formatos

Sempre especificar `format` para números (#171):

| Tipo OpenAPI | Format | Uso no HB Track |
|-------------|--------|----------------|
| `integer` | `int32` | Contadores, posições, anos de temporada (< 2^31) |
| `integer` | `int64` | Contadores de larga escala |
| `number` | `float` | Métricas de treino (PSE 0-10, percentuais de foco 0-100) |
| `number` | `double` | Coordenadas geográficas, cálculos de alta precisão |
| `string` | `decimal` | Valores monetários, se aplicável |
| `string` | `uuid` | IDs de recursos (UUID v4) |
| `string` | `date` | Datas de calendário (YYYY-MM-DD) |
| `string` | `date-time` | Timestamps RFC-3339 (YYYY-MM-DDTHH:MM:SSZ) |
| `string` | `duration` | Durações ISO 8601 (PT90M, P1DT2H) |
| `string` | `byte` | Dados binários base64url (#239) |

### 6.1 Restrições de Domínio

Métricas específicas do domínio do handebol/treinamento:

| Campo | Restrição | Justificativa |
|-------|-----------|--------------|
| `perceived_exertion` (PSE) | `0 <= x <= 10` | Escala Borg CR-10 |
| `focus_percentage` | `0 <= x <= 100` (por área) | Percentual por categoria |
| `total_focus_percentage` | `<= 120` (soma das 7 áreas) | Regra de negócio HB Track |
| `duration_minutes` | `> 0` | Duração sempre positiva |
| `athlete_count` | `>= 0` | Contagem não negativa |

---

## 7. Soft Delete

### 7.1 Padrão Canônico

O HB Track usa soft delete para preservar histórico e integridade referencial. O par `deleted_at` + `deleted_reason` é obrigatório e indivisível:

- `deleted_at`: `null` quando ativo; timestamp RFC-3339 quando excluído logicamente
- `deleted_reason`: `null` quando ativo; string descritiva **obrigatória** quando `deleted_at` preenchido
- O par deve ser atualizado atomicamente — nunca um sem o outro

### 7.2 Comportamento em Listagens

- Registros com `deleted_at NOT NULL` são excluídos logicamente — **invisíveis por default** em todas as listagens
- Endpoints de auditoria/histórico podem expor registros deletados com filtro explícito: `?include_deleted=true`
- Endpoints que exibem registros deletados devem documentar isso explicitamente no contrato

### 7.3 Exemplo

```json
// Registro ativo
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Treino de força",
  "deleted_at": null,
  "deleted_reason": null
}

// Registro deletado logicamente
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Treino de força",
  "deleted_at": "2026-03-11T14:30:00Z",
  "deleted_reason": "Sessão duplicada — substituída por ID 660e8400-e29b-41d4-a716-446655440001"
}
```

### 7.4 Constraint de Banco de Dados

```sql
-- Constraint canônica para soft delete
CONSTRAINT ck_<tabela>_soft_delete_pair CHECK (
  (deleted_at IS NULL AND deleted_reason IS NULL) OR
  (deleted_at IS NOT NULL AND deleted_reason IS NOT NULL)
)
```

---

## 8. Campos Comuns (Common Fields)

Todo recurso principal deve incluir (#174):

| Campo | Tipo | Format | Obrigatório | Descrição |
|-------|------|--------|-------------|-----------|
| `id` | string | uuid | Sim | Identificador UUID v4 único, imutável |
| `created_at` | string | date-time | Sim | Timestamp de criação (UTC, imutável após criação) |
| `updated_at` | string | date-time | Sim | Timestamp da última atualização (UTC) |
| `deleted_at` | string \| null | date-time | Sim | Soft delete timestamp; null = ativo |
| `deleted_reason` | string \| null | — | Sim | Motivo do soft delete; null = ativo |

**Regra de imutabilidade**: `id` e `created_at` são imutáveis após criação. Nenhum endpoint deve permitir alteração desses campos.

---

## 9. Fontes de Verdade por Superfície de Dados

Cada shape de dados tem exatamente uma fonte de verdade. Duplicação é proibida.

| Superfície | Fonte de Verdade |
|-----------|-----------------|
| HTTP API pública | `contracts/openapi/openapi.yaml` (por módulo: `contracts/openapi/paths/<module>.yaml`) |
| Schemas reutilizáveis entre módulos | `contracts/schemas/shared/` |
| Schemas de módulo específico | `contracts/schemas/<modulo>/` |
| Eventos assíncronos (pub/sub) | `contracts/asyncapi/asyncapi.yaml` (e subpastas `contracts/asyncapi/**`) |

**Regra**: nenhuma superfície pode ter duas fontes primárias simultâneas. Um schema de módulo não deve virar shape compartilhado apenas por conveniência — promoção para `shared/` exige reutilização real e semântica comum.

**Nota (Banco de Dados)**: este workspace governa contratos e documentação normativa. DDL/migrations vivem nos repositórios de implementação, mas devem obedecer `DATA_CONVENTIONS.md` e invariantes normativas por módulo.

---

## 10. Dados Sensíveis

### 10.1 Classificação

| Categoria | Exemplos | Tratamento |
|-----------|---------|------------|
| Dados médicos | Diagnósticos, lesões, medicamentos | Minimização, acesso restrito por RBAC (`medical.read`) |
| Dados biométricos | Peso, altura, frequência cardíaca | Minimização, visível apenas ao próprio atleta e staff médico |
| PII (Personally Identifiable Information) | Nome, CPF, data de nascimento, foto | Nunca em traces; mascarado em logs |
| Credenciais | Senhas, tokens, chaves de API | Variáveis de ambiente; nunca em código ou docs |

### 10.2 Regras Operacionais

- Campos sensíveis DEVEM ser mascarados em logs e traces distribuídos
- PII nunca aparece em mensagens de erro expostas ao cliente (ex: "Usuário com CPF 123... não encontrado")
- Secrets exclusivamente em variáveis de ambiente (`.env`); nunca commitados em código ou documentação
- Respostas com dados sensíveis devem incluir no contrato: escopo de acesso requerido, justificativa de exposição

---

## 11. Dados Binários

- Arquivos e imagens inline: base64url encoding (#239) quando o tamanho for adequado
- Arquivos > 1MB: preferir URL de storage externo (S3 ou equivalente) em vez de inline
- Content-Type para binários: `application/octet-stream` ou tipo MIME específico (`image/png`, `application/pdf`)
- Referências a arquivos externos: campo do tipo `string` format `uri`

---

## 12. Estados e Status

Todo campo de status persistido ou semanticamente estável deve ser explicitamente contratado no OpenAPI do módulo. O schema não deve definir status fora do state model canônico do módulo correspondente.

Para módulos com lifecycle complexo, o state model completo é documentado em `docs/hbtrack/modulos/<modulo>/STATE_MODEL_<MODULO>.md` (quando existente) ou equivalente.

Exemplo de restrição de transição de estado (training_session):
```
DRAFT → SCHEDULED (quando data/hora definida)
SCHEDULED → IN_PROGRESS (quando sessão iniciada)
IN_PROGRESS → PENDING_REVIEW (quando sessão finalizada pelo treinador)
PENDING_REVIEW → READONLY (quando aprovada por superior)
Qualquer estado → READONLY (automaticamente após 60 dias da data da sessão)
```

---

## 13. Anti-Patterns Proibidos

| Anti-pattern | Proibição |
|-------------|-----------|
| Campo estável apenas no código | Todo shape relevante para integração deve estar no contrato |
| Enum estável sem contrato | Strings "mágicas" não documentadas no schema são proibidas |
| Duplicação semântica | Mesmo conceito com nomes diferentes sem decisão formal |
| Mistura de idiomas em identificadores | Nunca misturar PT-BR e EN no mesmo campo — use inglês |
| Campo "mágico" com semântica implícita | Toda semântica especial deve ser documentada |
| Schema compartilhado por conveniência | Promoção para `shared/` exige reutilização real |
| Shape de evento sem contrato AsyncAPI | Todo evento publicado/consumido deve ter contrato |
| Status persistido fora do state model | Status deve ser consistente com state model do módulo |
| `null` para boolean | Use `true`/`false`; terceiro estado = enum nomeado |
| `null` para array vazio | Use `[]` |
| ID sequencial exposto na API | Use UUID v4 |

---

## 14. Referências Cruzadas

- `.contract_driven/templates/api/api_rules.yaml` — SSOT de convenções/templates/validações de API HTTP
- `API_CONVENTIONS.md` — guia/ponteiros (não-SSOT) para API
- `CHANGE_POLICY.md` — processo formal para breaking changes de dados
- `ERROR_MODEL.md` — modelo de erros Problem Details
- `docs/hbtrack/modulos/<module>/INVARIANTS_<MOD>.md` — invariantes do módulo (inclui constraints críticas)
- `HANDBALL_RULES_DOMAIN.md` — conceitos de domínio que afetam modelagem de dados (fases, eventos, composições)
