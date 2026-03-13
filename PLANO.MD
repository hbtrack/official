# ✅ PLANO EXECUTADO - 2026-03-12

## Status: CONCLUÍDO

### Resumo da Execução

**Regras promovidas para api_rules.yaml:**
- ✅ HB-CROSS-SURFACE-001 (paridade cross-surface)
- ✅ HB-MATCHES-TEMPORAL-001 (separação occurredAt/recordedAt)
- ✅ HB-MATCHES-VISIBILITY-001 (filtro de visibilidade)
- ✅ HB-MATCHES-AUTHORITY-001 (autoridade servidor sobre matchEventId/sequenceNumber)

**Schemas JSON criados em `.contract_driven/templates/api/schemas/`:**
- ✅ sync_command_v1.schema.json
- ✅ sync_command_result_v1.schema.json
- ✅ event_envelope_v1.schema.json
- ✅ match_event_v1.schema.json
- ✅ match_event_submission_v1.schema.json

**Arquivo fonte arquivado:**
- ✅ `docs/hbtrack/planejamento/pendentes/MATCH_EVENTS_REGRAS_API.txt`
  → `docs/hbtrack/planejamento/executados/MATCH_EVENTS_REGRAS_API.MIGRADO_2026-03-12.txt`

**Evidência de migração:**
- ✅ `docs/hbtrack/planejamento/executados/MIGRACAO_MATCH_EVENTS_2026-03-12.md`

---

# PLANO ORIGINAL

Segue a tabela na lógica de saneamento canônico.

| Trecho do TXT | Destino correto | Ação |
| --- | --- | --- |
| Regra de paridade cross-surface para `matches` com `canonical_payload_parity_across_surfaces`, `identical_semantic_types`, `identical_field_names`, envelopes específicos por superfície e distinção entre `occurredAt` e `recordedAt` | `api_rules.final.yaml` como regra normativa específica de módulo `EVENT_FIRST`, porque complementa o perfil `event_first_standard` já existente | **Promover** |
| Sub-regra `HB-MATCHES-IDEMPOTENCY-001` exigindo `requestId` em `matches/sync/action` | **Não criar regra nova separada**; consolidar no que já existe em `api_rules.final.yaml`, porque a política de idempotência global já cobre `create` e `action` com `requestId` no envelope | **Arquivar** como evidência de auditoria; evitar duplicação normativa |
| Sub-regra `HB-MATCHES-TEMPORAL-001` exigindo `occurredAt` no payload e `recordedAt` no envelope, proibindo aliases de tempo de transporte no payload | `api_rules.final.yaml` ou um arquivo canônico de regras específicas de `matches`, porque vira binding normativo de papel temporal | **Promover** |
| Sub-regra `HB-MATCHES-VISIBILITY-001` exigindo `surface_visibility_filter: true` | `api_rules.final.yaml`, pois já existe exigência global de `x-hb-visibility` em campos sensíveis ou filtrados por superfície | **Promover** como regra específica de `matches` que operacionaliza a meta-regra global |
| Observação crítica: "o módulo sync também deve ter um schema de resposta de comando retornando `requestId -> matchEventId`" | Schema canônico real de `sync_command_result_v1` no registry/schema store; não deve ficar em TXT | **Promover** como artefato formal |
| Schema `sync_command_v1.schema.json` descrito no TXT | Já existe como envelope canônico em `api_rules.final.yaml` (`required_fields: requestId, submittedAt, payload`); qualquer refinamento deve ir para schema formal, não texto | **Arquivar** o trecho do TXT e materializar só se faltar o schema formal no repositório; não manter o TXT como norma |
| Trecho do schema com `clockSeconds` e `videoTimestampSeconds` como `integer` | `CANONICAL_TYPE_REGISTRY.final.yaml` já define ambos como `number` com escala decimal; o TXT conflita com o canon | **Descartar** esse trecho do TXT |
| Trecho com `confidenceLevel` no schema de `provenance` | `api_rules.final.yaml` faz substituição canônica `confidence_level -> confidenceRatio`, e o type registry fixa `confidenceRatio` 0..1 | **Descartar** como nome normativo; manter só como evidência de erro corrigido |
| Decisão textual: "não tornar `matchEventId` autoridade do cliente" e "não exigir `matchEventId` nem `sequenceNumber` no input de submissão" | `api_rules.final.yaml` como regra normativa específica de autoridade para `matches/sync/action` | **Promover** |
| Regra proposta `HB-MATCHES-AUTHORITY-001` com `input_schema_projection: match_event_submission_v1`, proibição de `matchEventId` e `sequenceNumber` no input, exigência deles no result | `api_rules.final.yaml`, porque fecha lacuna real sobre autoridade do servidor em módulo `EVENT_FIRST` | **Promover** |
| Enum detalhado de `eventType` dentro de `match_event_submission_v1.schema.json` | Schema canônico do domínio `match_event_submission_v1`; não pertence a TXT nem a `api_rules` | **Promover** para schema formal, não para regra textual |
| Schema `match_event_submission_v1.schema.json` como projeção de input | Já é previsto por `MODULE_PROFILE_REGISTRY` e `api_rules` como `input_projection_schema`; falta materialização formal | **Promover** como schema canônico real |
| Explicação narrativa sobre "paridade cross-surface continua existindo no núcleo semântico, mas a superfície de entrada usa projeção de escrita" | ADR/AR ou documento de auditoria, porque explica a decisão mas não precisa ficar como norma duplicada | **Arquivar** |
| Frases como "essa é a solução determinística", "não precisa de bypass", "não reintroduz alucinação" | Documento de auditoria ou decision log; não são regras executáveis | **Arquivar** |
| Recomendação de sufixos canônicos (`Id`, `At`, `Count`) repetida no TXT | `api_rules.final.yaml` já é a autoridade para naming e suffix veto | **Descartar** do TXT como regra; manter só no canon |

Veredito operacional:

O que é regra de comportamento do agente ou contrato deve ser **promovido**.
O que é explicação de decisão deve ser **arquivado**.
O que conflita com o canon ou duplica regra já soberana deve ser **descartado**.

A síntese mais importante é esta:

Promover:

* `HB-MATCHES-TEMPORAL-001`
* `HB-MATCHES-VISIBILITY-001`
* `HB-MATCHES-AUTHORITY-001`
* `sync_command_result_v1`
* `match_event_submission_v1`

Arquivar:

* justificativas textuais
* explicações sobre paridade semântica
* trechos que apenas reforçam idempotência já coberta globalmente

Descartar:

* qualquer schema local que use `integer` para `clockSeconds` / `videoTimestampSeconds`
* qualquer nome fora do canon, como `confidenceLevel` como campo normativo
* qualquer duplicação de naming/suffix rules já soberanas em `api_rules`

O que você provavelmente deveria fazer em seguida é transformar essa tabela em um plano de migração com coluna extra “arquivo de destino exato”.

ARQUIVO QUE PERDE CONTEUDO DE ACORDO COM A TABELA: 
`docs\hbtrack\planejamento\pendentes\MATCH_EVENTS_REGRAS_API.txt`

ARQUIVOS QUE GANHAM COTEUDO DE ACORDO COM A TABELA:
`.contract_driven/templates/API_RULE/`
`api_rules.yaml`
`ARCHITECTURE_MATRIX.yaml`
`CANONICAL_TYPE_REGISTRY`
`MODULE_PROFILE_REGISTRY.yaml`