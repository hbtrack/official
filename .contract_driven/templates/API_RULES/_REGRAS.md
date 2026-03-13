# HB Track — Regras Canônicas de API v2.1.1

**Versão:** 2.1.1  
**Artefato:** api_rules  
**Status:** FINAL_CANONICAL_LOCKED  
**Fonte SSOT:** `.contract_driven/templates/api/api_rules.v2.1.1.yaml`  
**Data:** 2026-03-11

---

## 1. Soberania e Autoridade Final

### 1.1. Autoridade Final

**Soberania:** `HB_TRACK_INTERNAL`

### 1.2. Papéis das Fontes Externas

#### OWASP
- **Papel:** `security_sovereign` (soberano em segurança)
- **Domínios:**
  - `authn` (autenticação)
  - `authz` (autorização)
  - `object_property_access` (acesso a propriedades de objetos)
  - `resource_consumption` (consumo de recursos)
  - `inventory` (inventário de APIs)
  - `sensitive_data` (dados sensíveis)

#### Google AIP
- **Papel:** `sync_resource_model_base` (base do modelo de recursos síncronos)
- **Domínios:**
  - `resource_model` (modelo de recursos)
  - `standard_methods` (métodos padrão)
  - `request_identification` (identificação de requests)
  - `pagination_model` (modelo de paginação)

#### Adidas
- **Papel:** `json_naming_and_error_model_base` (base de nomenclatura JSON e modelo de erros)
- **Domínios:**
  - `camel_case_json` (camelCase em JSON)
  - `problem_details` (detalhes de problemas/erros)
  - `rest_async_split` (separação REST/Async)

#### Zalando
- **Papel:** `rest_pragmatism_base` (base de pragmatismo REST)
- **Domínios:**
  - `compatibility` (compatibilidade)
  - `rest_constraints` (restrições REST)
  - `events_pragmatism` (pragmatismo de eventos)

---

## 2. Modo de Operação do Agente

### 2.1. Modo de Geração de Contratos

```yaml
strict_no_inference: true
blocking_on_unknown: true
```

**Instrução:** Se qualquer trigger, perfil ou tipo canônico obrigatório estiver ausente, **bloquear** em vez de adivinhar.

### 2.2. SSOT de Módulo Único

- **Fonte de configuração de módulo:** `MODULE_PROFILE_REGISTRY.yaml`
- **Papel da matriz de arquitetura:** `validation_only` (apenas validação)

### 2.3. Comportamentos de Agente Proibidos

❌ **PROIBIDO:**
- `infer_module_class` (inferir classe do módulo)
- `infer_enabled_surfaces` (inferir superfícies habilitadas)
- `infer_contract_targets` (inferir alvos de contrato)
- `infer_idempotency_transport` (inferir transporte de idempotência)
- `infer_correlation_field_name` (inferir nome do campo de correlação)

---

## 3. Autoridade Estrutural

| Aspecto | Autoridade |
|---------|------------|
| **Modelo de recursos síncronos** | `GOOGLE_AIP` |
| **Nomenclatura de payload síncrono e higiene de contrato** | `HB_TRACK_INTERNAL` |
| **Modelo de contrato de eventos** | `ADIDAS` |
| **Requisitos de segurança** | `OWASP` |
| **Desempate final** | `HB_TRACK_INTERNAL` |

---

## 4. Veto de Estilo

### 4.1. Nomenclatura

| Elemento | Estilo | Exemplo |
|----------|--------|---------|
| **Campos JSON** | `camelCase` | `athleteId`, `trainingDate` |
| **Query params** | `camelCase` | `pageSize`, `pageToken` |
| **Path params** | `camelCase` | `{athleteId}`, `{matchId}` |
| **Campos de payload async** | `camelCase` | `eventId`, `correlationId` |
| **Caminhos URI** | `kebab-case` | `/training-sessions`, `/match-events` |
| **Headers** | `Hyphenated-Pascal-Case` | `Content-Type`, `Idempotency-Key` |
| **Valores de enum** | `UPPER_SNAKE_CASE` | `ACTIVE`, `PENDING`, `COMPLETED` |
| **Idioma** | `en-US` | - |

### 4.2. Sufixos Canônicos

| Conceito | Sufixo | Exemplo |
|----------|--------|---------|
| **Identificador** | `Id` | `athleteId`, `matchId` |
| **Identificador externo** | `ExternalId` | `externalAthleteId` |
| **Identificador de fonte** | `SourceId` | `sourceSystemId` |
| **Identificador de correlação** | `Id` | `correlationId` |
| **Timestamp** | `At` | `createdAt`, `updatedAt` |
| **Data** | `Date` | `birthDate`, `matchDate` |
| **Contagem** | `Count` | `playerCount`, `totalCount` |
| **Valor monetário** | `Amount` | `feeAmount`, `priceAmount` |
| **Percentual (0-100)** | `Percentage` | `completionPercentage` |
| **Razão (0-1)** | `Ratio` | `confidenceRatio` |
| **Estado/Status** | `Status` | `matchStatus`, `playerStatus` |
| **Tipo** | `Type` | `eventType`, `injuryType` |
| **Versão** | `Version` | `schemaVersion`, `apiVersion` |

### 4.3. Sufixos Proibidos

❌ **PROIBIDO:**
- `Uuid` / `UUID`
- `Timestamp`
- `Dt`
- `Cnt`

### 4.4. Resolução de Conflito de Fonte

**Vencedor:** `HB_TRACK_INTERNAL`

**Notas:**
- Google AIP é usado para estrutura de método/recurso, **não** para casing de campos
- Adidas/Zalando informam nomenclatura e estilo de payload REST, mas o veto HB Track é final

---

## 5. Mapa de Substituição de Estilo

### 5.1. Google → HB Track

| Google AIP | HB Track |
|------------|----------|
| `page_token` | `pageToken` |
| `next_page_token` | `nextPageToken` |
| `page_size` | `pageSize` |
| `total_size` | `totalCount` |
| `request_id` | `requestId` |
| `update_mask` | `updateMask` |

### 5.2. Genérico → HB Track

| Padrão Genérico | HB Track |
|-----------------|----------|
| `created_time` | `createdAt` |
| `updated_time` | `updatedAt` |
| `event_uuid` | `eventId` |
| `athlete_uuid` | `athleteId` |
| `confidence_level` | `confidenceRatio` |

---

## 6. Enums de Trigger (x-hb-*)

### 6.1. `x-hb-module`

**Fonte:** `MODULE_PROFILE_REGISTRY.yaml/modules/*`

Valores válidos são definidos dinamicamente pelo registry de módulos.

### 6.2. `x-hb-surface`

**Valores permitidos:**
- `sync` (síncrono)
- `event` (evento)

### 6.3. `x-hb-operation-kind`

**Valores permitidos:**
- `create` (criar)
- `retrieve` (recuperar)
- `list` (listar)
- `update` (atualizar)
- `delete` (deletar)
- `action` (ação)
- `fact_emission` (emissão de fato)
- `projection_event` (evento de projeção)
- `command_event` (evento de comando)

### 6.4. `x-hb-data-classification`

**Valores permitidos:**
- `public` (público)
- `internal` (interno)
- `restricted` (restrito)
- `sensitive` (sensível)

### 6.5. `x-hb-security-profile`

**Valores permitidos:**
- `public_read_v1`
- `authenticated_read_v1`
- `authenticated_write_v1`
- `sensitive_read_v1`
- `sensitive_write_v1`
- `internal_event_v1`

### 6.6. `x-hb-pagination-profile`

**Valores permitidos:**
- `none` (sem paginação)
- `collection_token_v1`
- `collection_cursor_v1`

### 6.7. `x-hb-envelope-profile`

**Valores permitidos:**
- `none`
- `sync_command_v1`
- `sync_command_result_v1`
- `event_envelope_v1`
- `event_envelope_sensitive_v1`

---

## 7. Perfis de Segurança

### 7.1. `public_read_v1`

- `authentication_required`: **false**
- `authorization_scope_required`: **false**

### 7.2. `authenticated_read_v1`

- `authentication_required`: **true**
- `authorization_scope_required`: **true**

### 7.3. `authenticated_write_v1`

- `authentication_required`: **true**
- `authorization_scope_required`: **true**
- `audit_required`: **true**

### 7.4. `sensitive_read_v1`

- `authentication_required`: **true**
- `authorization_scope_required`: **true**
- `field_level_access_control_required`: **true**
- `audit_required`: **true**

### 7.5. `sensitive_write_v1`

- `authentication_required`: **true**
- `authorization_scope_required`: **true**
- `field_level_access_control_required`: **true**
- `audit_required`: **true**
- `heightened_assurance_required`: **true**

### 7.6. `internal_event_v1`

- `authentication_required`: **true**
- `producer_identity_required`: **true**

---

## 8. Política de Idempotência

### 8.1. Padrão Soberano

**Padrão:** `requestId_in_sync_command_envelope`

### 8.2. Campos e Headers

| Campo/Header | Obrigatório | Localização | Tipo |
|--------------|-------------|-------------|------|
| `requestId` | ✅ Sim | Request envelope (top-level) | UUID4 |
| `Idempotency-Key` | ❌ Opcional | Header HTTP | UUID4 |
| `correlationId` | ✅ Sim (em eventos) | Event envelope | UUID4 |

### 8.3. Comportamento de Espelhamento de Header

- **Permitido:** ✅ Sim
- **Restrição:** Se `Idempotency-Key` estiver presente, **MUST** ser igual a `requestId`

### 8.4. Campos de Mapeamento de Resultado

- `requestId`
- `deduplicated`

### 8.5. Aplica-se a Operation Kinds

- `create`
- `action`

### 8.6. Requisitos

| Requisito | Valor |
|-----------|-------|
| **Tipo de requestId** | `UUID4` |
| **Localização de requestId** | `top_level_request_envelope_field` |
| **Comportamento de duplicata com sucesso** | `return_previous_success_response` |
| **Fonte da política de retenção** | `module_rules.*.idempotency_retention_window` |

### 8.7. Notas Importantes

1. O campo `requestId` no body é **obrigatório** para create/action em envelopes síncronos
2. O header opcional `Idempotency-Key`, quando presente, **MUST** ser igual a `requestId` e **MUST_NOT** ser usado como fonte de autoridade independente

---

## 9. Perfis de Erro

### 9.1. `problem_v1`

**Media type:** `application/problem+json`

#### Campos Obrigatórios
- `type` (URI que identifica o tipo de problema)
- `title` (resumo legível do problema)
- `status` (código de status HTTP)
- `detail` (explicação detalhada específica desta ocorrência)

#### Campos Opcionais
- `instance` (URI que identifica a ocorrência específica)
- `x-hb-trace-id` (ID de trace do HB Track)
- `x-hb-error-code` (código de erro interno do HB Track)

---

## 10. Perfis de Paginação

### 10.1. `collection_token_v1`

#### Campos de Request
- `pageSize` (número de itens por página)
- `pageToken` (token opaco de paginação)

#### Campos de Response
- `items` (array de recursos)
- `nextPageToken` (token para próxima página)
- `totalCount` (total de itens, opcional)

#### Referências de Tipo Canônico
- `pageSize` → `core.pagination.page_size.v1`
- `pageToken` → `core.pagination.page_token.v1`
- `nextPageToken` → `core.pagination.next_page_token.v1`
- `totalCount` → `core.pagination.total_count.v1`

### 10.2. `collection_cursor_v1`

#### Campos de Request
- `pageSize`
- `cursor` (cursor de paginação)

#### Campos de Response
- `items`
- `nextCursor`
- `totalCount`

#### Referências de Tipo Canônico
- `pageSize` → `core.pagination.page_size.v1`
- `nextCursor` → `core.pagination.next_cursor.v1`
- `totalCount` → `core.pagination.total_count.v1`

---

## 11. Regras de Superfície

### 11.1. Superfície: `sync` (Síncrono)

**Autoridade de estrutura base:** `google_aip`

**Alvos de contrato permitidos:**
- `openapi`

**Configurações:**
- `request_body_profile_required_for_write`: **true**

#### Métodos Padrão

| Operação | Método HTTP |
|----------|-------------|
| `create` | `POST` |
| `retrieve` | `GET` |
| `list` | `GET` |
| `update` | `PATCH` |
| `delete` | `DELETE` |

#### Padrões Proibidos

❌ **PROIBIDO:**
- `PUT_as_default_update` (PUT como update padrão)
- `server_authority_fields_in_client_input` (campos de autoridade do servidor em input do cliente)

### 11.2. Superfície: `event` (Evento)

**Autoridade de estrutura base:** `adidas`

**Alvos de contrato permitidos:**
- `asyncapi`

**Configurações:**
- `event_payload_schema_registry_reference_preferred`: **true**

#### Padrões Proibidos

❌ **PROIBIDO:**
- `patch_on_event_payload` (PATCH em payload de evento)
- `mutable_event_facts` (fatos de evento mutáveis)

---

## 12. Requisitos de Metadados de Campo

| Requisito | Obrigatório |
|-----------|-------------|
| `x-hb-visibility` em campos sensíveis ou filtrados por superfície | ✅ Sim |
| `x-hb-authority` em campos gerados pelo servidor | ✅ Sim |
| `x-hb-temporal-role` em campos temporais | ✅ Sim |

---

## 13. Perfis de Módulo

### 13.1. `crud_sync`

- **Superfície:** `sync`
- **Alvo de contrato:** `openapi`

### 13.2. `event_first_standard`

**Superfícies:**
- `sync`
- `event`

**Configuração:**
- `sync_write_profile`: `sync_command_v1`
- `sync_result_profile`: `sync_command_result_v1`
- `event_envelope_profile`: `event_envelope_v1`
- `idempotency_required`: **true**
- `canonical_input_projection_required`: **true**

**Notas:**
- Campos de resultado de comando síncrono específicos do módulo **MUST** estender o template de resultado base com o identificador de evento canônico para o módulo
- Matches usa `matchEventId`; scout usa `scoutEventId`

### 13.3. `sensitive_overlay`

- `additive_only`: **true**

**Perfis de segurança obrigatórios:**
- `sensitive_read_v1`
- `sensitive_write_v1`

---

## 14. Regras de Módulos

### 14.1. Módulo: `training`

| Propriedade | Valor |
|-------------|-------|
| **Classe do módulo** | `HYBRID` |
| **Superfícies habilitadas** | `sync`, `event` |
| **Janela de retenção de idempotência** | `24h` |

#### Configuração Sync
- `pagination_profile`: `collection_token_v1`

#### Configuração Event
- `envelope_profile`: `event_envelope_v1`

### 14.2. Módulo: `matches`

| Propriedade | Valor |
|-------------|-------|
| **Classe do módulo** | `EVENT_FIRST` |
| **Superfícies habilitadas** | `sync`, `event` |
| **Perfil canônico** | `event_first_standard` |
| **Janela de retenção de idempotência** | `24h` |
| **Schema canônico** | `match_event_v1` |
| **Schema de projeção de input** | `match_event_submission_v1` |

#### Campos Obrigatórios de Resultado Síncrono
- `requestId`
- `matchEventId` ⭐
- `sequenceNumber`
- `deduplicated`
- `processingAt`

### 14.3. Módulo: `scout`

| Propriedade | Valor |
|-------------|-------|
| **Classe do módulo** | `EVENT_FIRST` |
| **Superfícies habilitadas** | `sync`, `event` |
| **Perfil canônico** | `event_first_standard` |
| **Janela de retenção de idempotência** | `24h` |
| **Schema canônico** | `scout_event_v1` |
| **Schema de projeção de input** | `scout_event_submission_v1` |

#### Campos Obrigatórios de Resultado Síncrono
- `requestId`
- `scoutEventId` ⭐
- `sequenceNumber`
- `deduplicated`
- `processingAt`

### 14.4. Módulo: `wellness`

| Propriedade | Valor |
|-------------|-------|
| **Classe do módulo** | `HYBRID` |
| **Superfícies habilitadas** | `sync`, `event` |
| **Overlays** | `sensitive_overlay` |
| **Janela de retenção de idempotência** | `24h` |

### 14.5. Módulo: `medical`

| Propriedade | Valor |
|-------------|-------|
| **Classe do módulo** | `CRUD` |
| **Superfícies habilitadas** | `sync` |
| **Overlays** | `sensitive_overlay` |

---

## 15. Templates de Contrato

### 15.1. `sync_command_v1`

#### Campos Obrigatórios
```json
{
  "requestId": "uuid-v4",
  "submittedAt": "2026-03-12T10:30:00Z",
  "payload": { /* dados específicos */ }
}
```

### 15.2. `sync_command_result_v1`

#### Campos Obrigatórios (para módulos event-first como matches/scout)
```json
{
  "requestId": "uuid-v4",
  "matchEventId": "uuid-v4",  // ou scoutEventId, etc.
  "sequenceNumber": 12345,
  "deduplicated": false,
  "processingAt": "2026-03-12T10:30:01Z"
}
```

### 15.3. `event_envelope_v1`

#### Campos Obrigatórios
```json
{
  "eventId": "uuid-v4",
  "eventType": "match.created",
  "eventVersion": "1.0.0",
  "producer": "hbtrack.matches.api",
  "recordedAt": "2026-03-12T10:30:00Z",
  "correlationId": "uuid-v4",
  "payload": { /* fatos do evento */ }
}
```

---

## 16. Bindings de Validação

### 16.1. Rulesets Spectral

| Ruleset | Caminho |
|---------|---------|
| **Style veto** | `.contract_driven/templates/api/spectral/hb-style-veto.spectral.yaml` |
| **Trigger required** | `.contract_driven/templates/api/spectral/hb-trigger-required.spectral.yaml` |
| **Idempotency** | `.contract_driven/templates/api/spectral/hb-idempotency.spectral.yaml` |

---

## 17. Notas Importantes

1. **`sync_command_result_v1`** é o template genérico de resultado síncrono event-first para a família matches/scout quando a identidade da entidade canônica é atribuída pelo servidor

2. **`requestId`** no envelope síncrono é a **chave de idempotência soberana**; o header `Idempotency-Key` é apenas um espelho opcional

3. **Campos específicos de módulo** (como `matchEventId`, `scoutEventId`) devem ser adicionados ao resultado síncrono conforme definido nas regras de cada módulo

4. **Overlays** (como `sensitive_overlay`) são **somente aditivos** e impõem requisitos adicionais de segurança sem modificar a estrutura base

5. **Inferência é proibida** — se um perfil, trigger ou tipo canônico estiver ausente, o agente **MUST** bloquear e reportar erro em vez de adivinhar

---

## Fim do Documento

**Documento gerado a partir de:** `.contract_driven/templates/api/api_rules.v2.1.1.yaml`  
**Formato:** Markdown (tradução canônica v2.1.1)  
**Status:** FINAL_CANONICAL_LOCKED  
**Data:** 2026-03-12
