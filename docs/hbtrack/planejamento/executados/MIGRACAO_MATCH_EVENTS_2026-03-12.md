# MIGRAÇÃO: Match Events Regras API → api_rules Canônico

**Data de migração**: 2026-03-12  
**Arquivo fonte**: `docs/hbtrack/planejamento/pendentes/MATCH_EVENTS_REGRAS_API.txt`  
**Status**: ✅ MIGRADO PARA CANON

## Resumo da Migração

### 1. Regras Promovidas para api_rules.yaml

As seguintes regras foram promovidas para `.contract_driven/templates/api/api_rules.yaml` na seção `module_specific_rules.matches`:

- **HB-CROSS-SURFACE-001**: Paridade de payload canônico entre superfícies para o módulo matches
  - identical_semantic_types, identical_field_names
  - envelopes específicos por superfície
  - occurredAt no payload, recordedAt no envelope
  - filtro de visibilidade por superfície

- **HB-MATCHES-TEMPORAL-001**: Separação de campos temporais
  - occurredAt pertence ao payload (tempo de domínio)
  - recordedAt pertence ao envelope (tempo de transporte/persistência)
  - proibição de aliases de tempo de transporte no payload

- **HB-MATCHES-VISIBILITY-001**: Filtro de visibilidade por superfície
  - Campos marcados com `x-hb-visibility` são filtrados por superfície
  - Coerente com OWASP API3:2023 sobre exposição indevida

- **HB-MATCHES-AUTHORITY-001**: Autoridade do servidor sobre identificadores canônicos
  - matchEventId e sequenceNumber são gerados pelo servidor
  - Proibição desses campos no input de submissão (match_event_submission_v1)
  - Obrigatoriedade deles no resultado sync

### 2. Schemas JSON Criados

Os seguintes schemas JSON foram criados em `.contract_driven/templates/api/schemas/`:

1. **sync_command_v1.schema.json**: Envelope de comando sync
   - requestId (UUID, idempotência)
   - submittedAt (timestamp de submissão)
   - payload (referência ao schema específico do módulo)

2. **sync_command_result_v1.schema.json**: Resultado de comando sync
   - requestId → matchEventId (mapeamento)
   - sequenceNumber (número de ordenação canônico)
   - deduplicated (flag de deduplicação)
   - processingAt (timestamp de processamento)

3. **event_envelope_v1.schema.json**: Envelope de evento assíncrono
   - eventId (UUID do envelope)
   - recordedAt (tempo de persistência/publicação)
   - correlationId (rastreabilidade)
   - payload (referência ao schema canônico)

4. **match_event_v1.schema.json**: Schema canônico de match event
   - matchEventId, sequenceNumber (autoridade do servidor)
   - occurredAt (tempo de domínio)
   - clockSeconds, videoTimestampSeconds (number, não integer)
   - confidenceRatio (0-1, não confidenceLevel)
   - x-hb-visibility por campo

5. **match_event_submission_v1.schema.json**: Projeção de input para submissão
   - Remove matchEventId e sequenceNumber (autoridade do servidor)
   - Mantém todos os outros campos do schema canônico
   - Usado no input sync de criação de match events

### 3. Validações no CANONICAL_TYPE_REGISTRY.yaml

Confirmado que o registro já está correto:
- `clockSeconds`: `number` (não integer), escala seconds_decimal
- `videoTimestampSeconds`: `number` (não integer), escala seconds_decimal
- `confidenceRatio`: `number` 0-1 (não confidenceLevel)

### 4. Conteúdo Descartado (Conflitos com Canon)

Os seguintes trechos do TXT foram descartados por conflitarem com o canon:
- Schema com clockSeconds/videoTimestampSeconds como `integer` (canon = number)
- Nome `confidenceLevel` como campo normativo (canon = confidenceRatio)
- Duplicação de regras de sufixos já presentes em api_rules (Id, At, Count)

### 5. Conteúdo Arquivado (Não Normativo)

O arquivo TXT original foi movido para:
`docs/hbtrack/planejamento/executados/MATCH_EVENTS_REGRAS_API.MIGRADO_2026-03-12.txt`

Justificativas textuais e explicações de decisão foram arquivadas mas não promovidas como regras normativas:
- Explicações sobre paridade semântica cross-surface
- Frases como "essa é a solução determinística"
- Reforço de idempotência global (já coberta por api_rules)

## Decisões Arquiteturais Chave

1. **O cliente NÃO é autoridade sobre matchEventId**: O servidor oficializa o fato e gera o identificador canônico.

2. **requestId é a chave de idempotência**: O cliente usa requestId para deduplicação, não precisa de UUID temporário de evento.

3. **Projeção de input separada do schema canônico**: match_event_submission_v1 é a projeção de escrita, match_event_v1 é o núcleo canônico.

4. **Paridade cross-surface no núcleo semântico**: As superfícies sync e event compartilham o mesmo núcleo canônico (match_event_v1), mas com envelopes diferentes.

## Próximos Passos

✅ Regras migradas para api_rules.yaml  
✅ Schemas JSON materializados  
✅ Arquivo TXT arquivado  

Pendente:
- [ ] Validação com Spectral dos schemas criados
- [ ] Atualização dos endpoints OpenAPI para referenciar os schemas
- [ ] Atualização do AsyncAPI para referenciar event_envelope_v1
- [ ] Testes de conformidade com as novas regras

---

**Fim da documentação de migração**
