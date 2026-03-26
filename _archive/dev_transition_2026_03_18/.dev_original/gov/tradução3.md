# INGESTION_PROVIDER_CONTRACT.md

version: 1.0.0
status: PROPOSTO
decision_type: contrato_de_integracao
scope: hb_track
owners:
  - arquitetura
  - backend
  - dados
  - analytics
  - ia
related_decisions:
  - HB_TRACK_ARCHITECTURE_DECISION.md
  - HB_TRACK_PERSISTENCE_POLICY.md
related_modules:
  - ingestion
  - integrations
  - matches
  - scouts
  - training
  - analytics
  - video
  - reports
  - wellbeing
  - notifications
  - audit
related_artifacts:
  - docs/_ssot/openapi.json
  - docs/_ssot/schema.sql
  - docs/_canon/MANUAL_BACKEND_CANONICO.md
  - docs/_canon/REGRAS_SISTEMAS.md

---

## 1. Objetivo

Definir o contrato canônico de ingestão para todos os dados que entram no HB Track a partir de qualquer fonte que não seja domínio primário.

Este contrato existe para garantir que o HB Track possa ingerir dados de:
- provedores externos de esportes/estatísticas
- feeds de competição/federação
- entrada manual de treinadores/equipe
- importações CSV/planilha
- pipelines de marcação derivada de vídeo
- pipelines de IA/visão computacional
- futuras integrações com parceiros

sem acoplar:
- regras de domínio
- DTOs de API
- ViewModels de UI
- pipelines de analytics
- modelo interno de persistência

a formatos brutos de payload externo.

---

## 2. Decisão Principal

O HB Track DEVE implementar uma camada canônica de ingestão entre todas as entradas externas ou semi-estruturadas e todas as camadas internas de domínio/aplicação.

Esta camada de ingestão DEVE:
- preservar proveniência
- preservar contexto temporal
- preservar metadados de normalização
- preservar semântica de confiança quando aplicável
- isolar a deriva de esquema específica do provedor
- gerar registros internos normalizados

O HB Track NÃO DEVE permitir que módulos downstream dependam diretamente de nomes de campos nativos de provedores ou estruturas de payload, a menos que sejam explicitamente promovidos ao contrato canônico de ingestão.

---

## 3. Escopo da Ingestão

O contrato de ingestão se aplica a qualquer entrada cuja fonte de verdade ainda não seja o modelo de domínio canônico do HB Track.

Isso inclui:
- feeds de provedores oficiais
- entrada operacional manual que representa fatos importados/observados
- detecções extraídas por IA/visão computacional
- importações em massa
- payloads de parceiros via webhook/evento
- uploads baseados em planilha
- integrações com sensores/dispositivos
- integrações assíncronas baseadas em mensagens

Este contrato NÃO substitui:
- contratos de domínio
- contratos de DTO de API pública
- contratos de ViewModel de frontend

É um limite interno de normalização.

---

## 4. Categorias Canônicas de Fonte

Todo registro ingerido DEVE declarar um `source_type`.

Valores canônicos permitidos:

- `external_provider`
- `manual_staff_entry`
- `manual_coach_entry`
- `manual_athlete_entry`
- `video_annotation`
- `ai_cv_extraction`
- `spreadsheet_import`
- `csv_import`
- `federation_feed`
- `partner_webhook`
- `system_sync`
- `legacy_migration`
- `sensor_device`
- `other_controlled`

Nenhum outro valor é permitido a menos que seja adicionado por revisão explícita do contrato.

---

## 5. Princípios de Design da Ingestão

### 5.1 Proveniência é obrigatória
Nenhum registro ingerido pode se tornar dado interno canônico sem preservar sua origem.

### 5.2 Normalização é explícita
Normalização não é um mapeador informal. É um limite de transformação regido por contrato.

### 5.3 Payload bruto não é verdade de domínio
Payloads brutos de provedores são entradas de evidência, não verdade automaticamente válida no domínio.

### 5.4 Confiança é de primeira classe quando probabilística
Se os dados vêm de extração por IA/VC/inferência/probabilística, a confiança deve ser explícita.

### 5.5 Contexto temporal importa
Tempo observado e tempo de ingestão não devem ser confundidos.

### 5.6 Promoção ao domínio é controlada
Um campo só se torna um campo canônico interno após mapeamento explícito e regras de validação.

### 5.7 Idempotência é obrigatória
Chegadas duplicadas do mesmo fato externo devem ser detectáveis ou governáveis.

### 5.8 Controles de domínio sensível se propagam
Se dados ingeridos entram em um domínio sensível, classificação e restrições de acesso devem acompanhá-los.

---

## 6. Esquema Canônico de Registro de Ingestão

Todo registro ingerido DEVE estar de acordo com a seguinte estrutura lógica.

```yaml
ingestion_record:
  ingestion_id: string
  source_type: enum
  source_system: string
  source_record_id: string | null
  source_endpoint: string | null
  source_batch_id: string | null
  source_file_name: string | null
  source_file_checksum: string | null
  source_event_type: string | null
  source_schema_version: string | null

  observed_at: datetime | null
  occurred_at: datetime | null
  ingested_at: datetime
  processed_at: datetime | null

  entity_kind: string
  entity_external_key: string | null
  aggregate_hint: string | null

  normalization_status: enum
  normalization_version: string
  mapping_profile: string | null

  confidence_level: decimal | null
  confidence_label: string | null
  review_status: enum | null

  access_classification: enum
  sensitivity_class: enum

  payload_raw: object | string | null
  payload_normalized: object
  payload_fingerprint: string

  correlation_id: string | null
  causation_id: string | null
  trace_id: string | null

  actor_type: string | null
  actor_id: string | null

  validation_status: enum
  validation_errors: array
  warnings: array

  dedupe_key: string | null
  idempotency_key: string | null

  retained_until: datetime | null
  deleted_at: datetime | null
```

---

## 7. Semântica dos Campos Obrigatórios

### 7.1 Campos de identidade e rastreabilidade

`ingestion_id`
Identificador interno imutável do registro de ingestão.
Regra:
DEVE ser único
NUNCA deve ser reutilizado
DEVE identificar um único registro de ingestão normalizado

`source_system`
Identificador controlado e compreensível da fonte upstream.
Exemplos:
- `sportradar`
- `manual_coach_ui`
- `video_tagger_v1`
- `csv_roster_import`
- `federation_feed_cbhb`
- `open_cv_detector_v2`

`source_record_id`
Identificador original do registro upstream quando disponível.
Regra:
DEVE ser preservado exatamente quando fornecido
PODE ser nulo quando a fonte não fornece um

`payload_fingerprint`
Impressão digital determinística do payload normalizado ou bruto relevante, usada para fins de deduplicação/rastreamento.
Regra:
DEVE ser estável sob regras de canonicalização de entrada idênticas

---

### 7.2 Campos temporais

`observed_at`
Quando o fato foi observado no mundo real ou no contexto da fonte.

`occurred_at`
Quando o evento/fato realmente aconteceu, se distinto do tempo de observação.

`ingested_at`
Quando o HB Track recebeu os dados.

`processed_at`
Quando o processamento de normalização/validação foi concluído.

Regra:
`ingested_at` é obrigatório
`observed_at` e `occurred_at` não devem ser inferidos silenciosamente como o mesmo valor, a menos que as regras de mapeamento explicitamente assim estabeleçam

---

### 7.3 Campos de classificação

`entity_kind`
Tipo canônico do registro sendo ingerido.
Exemplos:
- `match_event`
- `training_attendance_fact`
- `athlete_registry_record`
- `video_annotation`
- `wellbeing_signal`
- `scout_observation`
- `report_generation_trigger`

`aggregate_hint`
Dica opcional do agregado interno provavelmente afetado.
Exemplos:
- `match`
- `training_session`
- `athlete`
- `competition`
- `video_asset`

Regra:
a dica é informativa, não é verdade canônica de domínio

---

### 7.4 Campos de normalização

`normalization_status`
Valores permitidos:
- `pending`
- `normalized`
- `rejected`
- `quarantined`
- `partially_normalized`

`normalization_version`
Versão do contrato de normalização ou lógica de mapeamento aplicada.

`mapping_profile`
Conjunto de regras de mapeamento nomeado para esta combinação de fonte/entidade.
Exemplos:
- `sportradar_match_event_v1`
- `csv_athlete_roster_v2`
- `manual_training_attendance_v1`

Regra:
qualquer mudança na semântica de mapeamento DEVE incrementar `normalization_version` ou o versionamento do perfil de mapeamento

---

### 7.5 Campos de confiança e revisão

`confidence_level`
Confiança numérica, obrigatória para dados probabilísticos ou inferidos.
Regra:
DEVE ser nulo para registros determinísticos/manuais, a menos que seja explicitamente significativo
DEVE estar presente para fatos extraídos por IA/VC/inferência quando uma probabilidade/confiança existe

`confidence_label`
Categoria semântica controlada para confiança.
Valores permitidos:
- `very_low`
- `low`
- `medium`
- `high`
- `very_high`

`review_status`
Valores permitidos:
- `not_required`
- `pending_human_review`
- `reviewed_accepted`
- `reviewed_rejected`
- `reviewed_corrected`

Regra:
registros sensíveis derivados de IA devem ter padrão `pending_human_review` quando materialmente impactantes

---

### 7.6 Campos de acesso e sensibilidade

`access_classification`
Valores permitidos:
- `public_internal`
- `restricted_staff`
- `restricted_coaching`
- `restricted_medical`
- `restricted_sensitive`
- `system_only`

`sensitivity_class`
Valores permitidos:
- `normal`
- `personal`
- `sensitive_health_adjacent`
- `sensitive_psychological`
- `sensitive_minor_related`
- `regulated_high_control`

Regra:
a classificação deve ser atribuída antes da exposição downstream

---

### 7.7 Campos de validação e deduplicação

`validation_status`
Valores permitidos:
- `valid`
- `invalid`
- `warning_only`
- `requires_review`

`dedupe_key`
Chave canônica de deduplicação quando suportada.

`idempotency_key`
Chave usada para evitar efeitos colaterais de processamento duplicado.

Regra:
deduplicação e idempotência são relacionadas mas não idênticas
ambas podem estar presentes

---

## 8. Regras de Payload Bruto vs Normalizado

### 8.1 `payload_raw`
Representa o payload de entrada original ou trecho bruto essencial.
Regra:
DEVE ser preservado quando legalmente correto, seguro e adequado ao armazenamento
PODE ser omitido ou redigido quando a minimização de dados sensíveis exigir
NÃO DEVE ser exposto diretamente a consumidores gerais de frontend

### 8.2 `payload_normalized`
Representa a estrutura intermediária normalizada canônica produzida pela camada de ingestão.
Regra:
DEVE ser o único formato de payload consumido pelas camadas de mapeamento de domínio downstream
DEVE seguir o perfil de mapeamento aprovado
NÃO DEVE incorporar formatação específica de UI

### 8.3 Regra de redação
Se o payload bruto contiver campos sensíveis ou excessivos não necessários para o processamento downstream:
- redija antes da persistência, ou
- armazene apenas trechos controlados e metadados seguros de rastreamento

---

## 9. Formato Canônico do Payload Normalizado

Cada `payload_normalized` DEVE ser estruturado como:

```yaml
payload_normalized:
  schema_name: string
  schema_version: string
  entity_kind: string
  canonical_fields: object
  source_overrides: object | null
  provenance_summary:
    source_type: string
    source_system: string
    source_record_id: string | null
    observed_at: datetime | null
    confidence_level: decimal | null
  mapping_notes: array
```

Regras:
- `canonical_fields` contém apenas campos normalizados internos
- `source_overrides` contém campos residuais específicos do provedor que não foram promovidos a campos canônicos mas precisam de retenção controlada
- `mapping_notes` contém diagnósticos não autoritativos, nunca verdade de negócio

---

## 10. Regras de Abstração de Provedores

### 10.1 Nenhum vazamento nativo de provedor
Nenhum módulo downstream pode depender de:
- valores de enum nativos do provedor
- nomes de campos nativos do provedor
- estrutura de aninhamento específica do provedor
- semântica de timestamp específica do provedor

a menos que seja explicitamente normalizado primeiro.

### 10.2 Registro controlado de provedores
Todo sistema fonte deve ser registrado em um registro controlado de provedores com:
- código do provedor
- nome de exibição do provedor
- modelo de autenticação
- esquemas esperados
- tipos de entidade suportados
- proprietário da normalização
- notas de risco

### 10.3 Tratamento de desigualdade de cobertura
O contrato de ingestão DEVE suportar cobertura parcial sem quebrar contratos internos de domínio.

Exemplos:
- provedor fornece eventos de partidas mas não dados de treino
- provedor fornece metadados de competição mas não detalhes em nível de atleta
- extração de vídeo por IA fornece eventos candidatos com confiança, não fatos verificados

---

## 11. Entrada Manual como Ingestão

Entrada operacional manual também pode entrar pelo contrato de ingestão quando representa:
- fatos observados externamente
- fatos históricos importados
- anotações vinculadas à proveniência
- observações de eventos autorais da equipe
- tags de vídeo do treinador
- fluxos de captura de fonte não primária

Regra:
- entrada manual que cria diretamente entidades de domínio primárias pode ignorar a ingestão e usar comandos de domínio diretamente
- entrada manual que registra fatos observacionais DEVE usar semântica de ingestão

Exemplos:
- criar um novo time = comando de domínio
- marcar um evento histórico de partida a partir de revisão de vídeo = fato de ingestão
- fazer upload de CSV de lista de atletas = fluxo de ingestão
- marcar episódio tático em vídeo = fato de ingestão

---

## 12. Regras de Ingestão de IA / VC

Registros derivados de IA/VC são permitidos apenas se carregarem:
- `source_type = ai_cv_extraction`
- identificador do modelo
- versão do modelo
- metadados de confiança
- política de revisão
- proveniência para o segmento de vídeo/fonte onde aplicável

Campos adicionais recomendados dentro de `payload_normalized.canonical_fields` ou `source_overrides`:
- `model_name`
- `model_version`
- `segment_start_ms`
- `segment_end_ms`
- `detection_type`
- `candidate_label`
- `review_required`

Regra:
- output de IA/VC não é automaticamente equivalente a verdade de domínio validada
- promoção para eventos autorizados de domínio deve passar por lógica definida de aceitação/revisão

---

## 13. Regras de Importação de Planilha / CSV

Para importações de CSV/planilha, os registros de ingestão DEVEM preservar:
- nome do arquivo
- checksum do arquivo quando viável
- ator do upload
- id do lote de importação
- número ou localizador da linha
- versão do parser
- perfil de mapeamento
- resultados de validação por linha

Regra:
- sucesso em nível de lote não deve ocultar falhas em nível de linha
- erros de linha devem ser atribuíveis e revisáveis

Campos recomendados de localizador de linha:
- `source_batch_id`
- `row_index`
- `sheet_name`
- `row_hash`

---

## 14. Regras de Feed de Federação / Oficial

Dados de origem oficial ou de federação AINDA devem passar pela normalização.

Regra:
- fonte oficial não significa imunidade de esquema
- fonte oficial aumenta a confiança, mas não remove requisitos de proveniência ou validação

Metadados sugeridos:
- autoridade da competição
- timestamp de publicação do feed
- status de oficialidade
- sequência de emenda/correção
- jurisdição/escopo

---

## 15. Sobreposição de Domínio Sensível

Se dados ingeridos tocam:
- dados médico-saúde adjacentes
- dados psicológicos/bem-estar
- contexto sensível relacionado a menores
- observações pessoais protegidas

então o registro de ingestão DEVE adicionalmente incluir ou derivar:
- `access_classification` mais rigorosa
- `sensitivity_class` mais rigorosa
- controle de retenção
- limite de revisão
- política de consumidores permitidos
- restrições de exposição a camadas de analytics/dashboard

Regra:
- ingestão sensível só é permitida se houver política de uso downstream
- nenhum comportamento do tipo "colete agora, governe depois" é permitido

---

## 16. Pipeline Canônico de Validação

Todo fluxo de ingestão DEVE implementar estas etapas:

1. Receber
2. Identificar fonte
3. Analisar
4. Validação básica de esquema
5. Normalizar
6. Enriquecer proveniência
7. Classificar sensibilidade
8. Aplicar verificações de deduplicação/idempotência
9. Validar restrições canônicas de negócio
10. Rotear:
    - aceitar
    - colocar em quarentena
    - rejeitar
    - aceitar com avisos
11. Emitir evento de auditoria
12. Publicar para consumo downstream se aceito

---

## 17. Resultados de Aceitação

Resultados finais de roteamento permitidos:
- `accepted`
- `accepted_with_warnings`
- `quarantined`
- `rejected`
- `awaiting_review`

Definições:

`accepted`
Registro é válido e pode alimentar o processamento downstream.

`accepted_with_warnings`
Registro é utilizável mas carrega problemas não bloqueantes.

`quarantined`
Registro está retido devido a problemas não resolvidos de integridade/sensibilidade/revisão.

`rejected`
Registro é inválido e não pode prosseguir.

`awaiting_review`
Registro pode ser estruturalmente válido, mas requer decisão humana antes da promoção.

---

## 18. Regras de Auditoria e Observabilidade

Todo fluxo de ingestão DEVE emitir entradas de trilha auditável para:
- recebimento
- tentativa de normalização
- resultado de validação
- resultado de roteamento
- decisão de promoção downstream quando aplicável

Dimensões de observabilidade recomendadas:
- source_system
- entity_kind
- mapping_profile
- normalization_version
- validation_status
- review_status
- processing_latency
- acceptance_outcome

---

## 19. Regras de Consumo Downstream

### 19.1 Serviços de domínio
Consomem registros de ingestão normalizados, não payloads brutos.

### 19.2 Analytics
Consome:
- fatos autorizados promovidos, ou
- fatos de ingestão controlados explicitamente permitidos para analytics

Analytics nunca deve misturar silenciosamente:
- fatos autorizados revisados
- candidatos de IA não revisados
- registros em quarentena

### 19.3 Frontend
Frontend nunca deve consumir registros de ingestão diretamente, a menos que:
- uma interface interna de operações/revisão explicitamente requeira
- o acesso seja autorizado
- a visão seja projetada como ferramenta de revisão, não abstração de produto para usuário final

---

## 20. Padrões Proibidos

Os seguintes padrões são proibidos.

### 20.1 Payload bruto direto para domínio
Nenhum payload de provedor pode ser tratado como modelo de domínio sem normalização.

### 20.2 Payload bruto direto para UI
Nenhum componente de UI pode se vincular diretamente a payloads brutos de ingestão.

### 20.3 Perda silenciosa de confiança
Nenhuma fonte probabilística pode ser normalizada em verdade categórica enquanto descarta metadados de confiança.

### 20.4 Colapso temporal silencioso
Não mescle `occurred_at`, `observed_at` e `ingested_at` em um único campo sem regra de mapeamento explícita.

### 20.5 Nomenclatura de lock-in de provedor
Não promova nomes nativos de provedores para campos canônicos internos por conveniência.

### 20.6 Acumulação de dados sensíveis sem propósito
Não preserve payload bruto sensível além do que a governança e o propósito do produto justificam.

### 20.7 Promoção de verdade de IA não revisada
Não eleve fatos candidatos de IA/VC a verdade autoritativa em domínio sensível sem política de aceitação definida.

---

## 21. Exemplos de Mapeamentos Canônicos

### 21.1 Evento de partida de provedor externo

```yaml
source_type: external_provider
source_system: sportradar
entity_kind: match_event
payload_normalized:
  schema_name: match_event_ingestion
  schema_version: 1.0.0
  entity_kind: match_event
  canonical_fields:
    external_match_id: "sr:match:123"
    event_code: "goal"
    team_external_id: "sr:competitor:456"
    athlete_external_id: "sr:player:789"
    occurred_at: "2026-03-10T20:13:00Z"
    period: 1
    clock_seconds: 754
```

### 21.2 Tag de vídeo manual do treinador

```yaml
source_type: manual_coach_entry
source_system: video_tagging_ui
entity_kind: video_annotation
payload_normalized:
  schema_name: video_annotation_ingestion
  schema_version: 1.0.0
  entity_kind: video_annotation
  canonical_fields:
    video_asset_id: "vid_001"
    segment_start_ms: 152000
    segment_end_ms: 164500
    tag_type: "defensive_transition_failure"
    authored_note: "recuperação central atrasada"
```

### 21.3 Candidato de detecção por IA/VC

```yaml
source_type: ai_cv_extraction
source_system: open_cv_detector_v2
entity_kind: candidate_match_event
confidence_level: 0.81
confidence_label: high
review_status: pending_human_review
payload_normalized:
  schema_name: candidate_match_event_ingestion
  schema_version: 1.0.0
  entity_kind: candidate_match_event
  canonical_fields:
    video_asset_id: "vid_001"
    segment_start_ms: 64000
    segment_end_ms: 66200
    candidate_label: "fast_break"
    model_name: "hb_cv_events"
    model_version: "2.4.1"
```

---

## 22. Promoção à Verdade de Domínio

Registros de ingestão não se tornam automaticamente verdade canônica de domínio.

Promoção requer:
- sucesso na validação
- aceitação do mapeamento
- compatibilidade com regras de domínio
- revisão se necessário
- classificação correta de fonte
- nenhum problema bloqueante de sensibilidade ou integridade

Resultados de promoção podem incluir:
- criar fato de domínio
- atualizar agregado
- criar tarefa de revisão
- criar apenas entrada de auditoria
- descartar/rejeitar
- colocar em quarentena para revisão de operações

---

## 23. Gate de Revisão para Novas Integrações

Cada nova integração/provedor deve definir:
- código do source_system
- source_type suportado
- tipos de entidade suportados
- exemplos de payload bruto
- perfil de mapeamento de normalização
- estratégia de deduplicação
- estratégia de idempotência
- semântica de confiança se probabilística
- regras de classificação de sensibilidade
- regras de revisão
- tratamento de falhas/quarentena
- ganchos de auditoria e observabilidade

Uma nova integração está incompleta sem essas definições.

---

## 24. Definição de Pronto

Este contrato está PRONTO apenas quando:
- toda fonte de integração tem um `source_system` registrado
- perfis de normalização existem para cada par suportado de fonte/tipo de entidade
- registros de ingestão preservam proveniência, timing e resultado de validação
- fluxos de IA/VC preservam confiança e status de revisão
- importações de CSV/planilha preservam rastreabilidade de lote e linha
- ingestão de domínio sensível aplica classificação antes da exposição downstream
- nenhum módulo downstream depende diretamente de payloads brutos de provedores
- trilha de auditoria existe para o ciclo de vida da ingestão
