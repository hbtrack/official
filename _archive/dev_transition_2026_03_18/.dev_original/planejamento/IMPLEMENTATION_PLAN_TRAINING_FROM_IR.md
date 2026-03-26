# IMPLEMENTATION_PLAN_TRAINING_FROM_IR.md

version: 1.0.0
status: PROPOSED
scope: hb_track.training
artifact_type: implementation_plan
authority: execution_plan_from_promoted_ir
owners:
  - architecture
  - backend
  - ai_governance
  - qa

## 1. Objetivo

Definir o plano de implementação determinística do módulo `training` a partir do `MODULE_DECISION_IR` promovido e aprovado no `DECISION_IR_CONFORMANCE_GATE`.

Este plano assume como pré-condição:

- `MODULE_DECISION_IR` promovido
- `DECISION_IR_CONFORMANCE_GATE = PASS`
- `READINESS_SUMMARY_GATE = PASS`
- `surface_mapping` completo
- zero ambiguidades bloqueantes para materialização

Regra central:
**o backend não interpreta o módulo; ele implementa o que já foi canonizado.**

## 2. Entradas obrigatórias

- `training.module_decision_ir.yaml/json` promovido
- `MODULE_DECISION_IR_SCHEMA.json`
- `DECISION_IR_CONFORMANCE_GATE.md`
- `IR_TO_SURFACE_MAPPING.yaml`
- `.contract_driven/CONTRACT_SYSTEM_LAYOUT.md`
- `.contract_driven/CONTRACT_SYSTEM_RULES.md`
- `.contract_driven/GLOBAL_TEMPLATES.md`
- `.contract_driven/templates/api/api_rules.yaml`
- docs globais canônicas aplicáveis
- registries soberanos exigidos pelo módulo
- matriz canônica do módulo `training`
- output do último run de gates com `PASS`

## 3. Resultado esperado

Ao final deste plano, o módulo `training` deverá possuir:

- superfícies soberanas materializadas nos paths canônicos
- backend Python aderente aos contratos
- state machines implementadas
- invariantes bloqueantes implementadas
- APIs nucleares implementadas
- integrações de boundary implementadas como adapters
- testes determinísticos cobrindo invariantes, estados e boundaries
- readiness operacional para fluxos críticos

## 4. Estratégia de implementação

A implementação será executada em 6 fases:

1. congelamento do IR
2. geração das superfícies soberanas
3. validação de isomorfismo IR ↔ superfícies
4. implementação backend dirigida por contrato
5. testes determinísticos
6. validação operacional e hardening

Nenhuma fase pode ser pulada.

## 5. Fase 0 — Congelamento do IR

### 5.1 Objetivo
Congelar o `MODULE_DECISION_IR` como baseline oficial da rodada.

### 5.2 Ações
- registrar versão do IR
- registrar hash/checksum no manifest
- marcar o IR como input oficial da rodada
- bloquear edição paralela enquanto a materialização estiver em curso
- registrar o commit base da rodada

### 5.3 Evidências esperadas
- manifest atualizado
- checksum registrado
- referência explícita ao commit base
- log de promoção do IR

### 5.4 Critério de saída
- IR congelado
- nenhuma `open_decision` bloqueante
- reprodutibilidade assegurada

## 6. Fase 1 — Geração das superfícies soberanas

### 6.1 Objetivo
Materializar todas as superfícies aplicáveis a partir do IR promovido.

### 6.2 Ordem obrigatória
1. `README`
2. `MODULE_SCOPE`
3. `DOMAIN_RULES`
4. `INVARIANTS`
5. `STATE_MODEL`
6. `PERMISSIONS`
7. `ERRORS`
8. `OpenAPI`
9. `Schema`
10. `Workflow`
11. `AsyncAPI`
12. `TEST_MATRIX`

### 6.3 Regra
Cada superfície deve ser gerada por template determinístico com binding explícito a partir do IR.

### 6.4 Artefatos esperados
- `docs/hbtrack/modulos/training/README*.md`
- `docs/hbtrack/modulos/training/MODULE_SCOPE*.md`
- `docs/hbtrack/modulos/training/DOMAIN_RULES*.md`
- `docs/hbtrack/modulos/training/INVARIANTS*.md`
- `docs/hbtrack/modulos/training/STATE_MODEL*.md`
- `docs/hbtrack/modulos/training/PERMISSIONS*.md`
- `docs/hbtrack/modulos/training/ERRORS*.md`
- `docs/hbtrack/modulos/training/TEST_MATRIX*.md`
- `contracts/openapi/...training...`
- `contracts/schemas/training/...`
- `contracts/workflows/training/...`
- `contracts/asyncapi/...training...`

### 6.5 Critério de saída
- todos os arquivos gerados nos paths canônicos
- zero placeholders
- zero drift entre superfícies
- gates contratuais seguem em `PASS`

## 7. Fase 2 — Validação de isomorfismo IR ↔ superfícies

### 7.1 Objetivo
Provar que a materialização preservou integralmente o conteúdo decisório do IR.

### 7.2 Checklist obrigatório
- toda entidade do IR existe nas superfícies correspondentes
- todo lifecycle existe no `STATE_MODEL`
- toda regra bloqueante existe em `DOMAIN_RULES` e/ou `INVARIANTS`
- todo use case HTTP existe no OpenAPI
- todo erro existe em `ERRORS`
- todo evento existe em AsyncAPI
- toda permissão aplicável existe em `PERMISSIONS`
- toda entrada de `surface_mapping` foi respeitada

### 7.3 Saída esperada
- relatório de isomorfismo
- lista de gaps zero ou vazia
- prova de binding 1:1

### 7.4 Critério de saída
- nenhuma decisão do IR ausente nas superfícies
- nenhuma superfície com conteúdo sem origem no IR
- nenhuma escolha criativa do agente detectada

## 8. Fase 3 — Implementação backend dirigida por contrato

### 8.1 Objetivo
Implementar o backend Python do módulo `training` obedecendo estritamente às superfícies soberanas geradas.

### 8.2 Subfases obrigatórias

#### 8.2.1 Entidades centrais
Implementar primeiro:
- `training_intervention_cycle`
- `training_session`
- `session_objective`
- `session_block`
- `prescription_line`
- `execution_record`
- `session_adjustment`
- `need_detected`
- `feedback_thread`
- `decision_rationale`
- `attention_queue_item`

#### 8.2.2 State machines
Implementar:
- `LIFECYCLE-TRAINING-SESSION`
- `LIFECYCLE-INTERVENTION-CYCLE`
- `LIFECYCLE-NEED-DETECTED`
- `LIFECYCLE-FEEDBACK-THREAD`

Cada transição deve conter:
- estado origem
- estado destino
- guardas
- erro formal em caso de violação
- evento correspondente

#### 8.2.3 Invariantes bloqueantes
Prioridade máxima para:
- sessão exige objetivo
- publish exige conteúdo mínimo
- execução exige contexto
- planned vs actual preservado
- ajuste exige motivo
- complete exige evidência
- feedback contextual
- restriction guard
- completed immutable
- no hard delete pós-execução
- boundaries com medical, analytics, notifications, audit, identity_access

#### 8.2.4 Repositories e query services
Implementar leitura e escrita aderentes às entidades soberanas e suas regras de persistência.

#### 8.2.5 Services / use cases
Implementar primeiro:
- criar ciclo
- criar sessão draft
- publicar sessão
- iniciar sessão
- registrar execução
- registrar ajuste
- completar sessão
- criar feedback thread
- fechar feedback thread
- criar need_detected
- listar e consultar sessões
- listar attention queue

#### 8.2.6 API handlers
Implementar handlers conforme OpenAPI gerado.
Nenhum endpoint fora do contrato.

#### 8.2.7 Adapters de integração
Implementar adapters para:
- `medical`
- `wellness`
- `analytics`
- `scout`
- `notifications`
- `audit`
- `identity_access`
- `exercises`
- `teams`
- `seasons`
- `matches`

Regra:
**adapter consome ou emite; não soberaniza.**

### 8.3 Critério de saída
- backend cobre todos os casos P1
- invariantes bloqueantes implementadas
- nenhuma violação de boundary
- nenhuma lógica crítica vive só em doc

## 9. Fase 4 — Testes determinísticos

### 9.1 Objetivo
Provar que a implementação executa exatamente o contrato promovido.

### 9.2 Camadas obrigatórias
1. testes de state machine
2. testes de invariantes
3. testes de boundary
4. testes de autorização
5. testes de API contract
6. testes de eventos
7. testes de persistência / imutabilidade

### 9.3 Casos mínimos obrigatórios
- criar sessão sem objetivo -> 422
- publicar sessão sem conteúdo mínimo -> 422
- transição proibida -> 422
- execução sem contexto -> 422
- ajuste sem motivo -> 422
- completar sessão sem evidência -> 422
- feedback sem anchor -> 422
- fechar feedback sem outcome -> 422
- atleta inelegível sem override -> 422
- mutação em sessão completed -> 409
- hard delete em sessão pós-execução -> 409
- analytics tentando mutar estado -> 403/blocked
- medical write via training -> 403/blocked
- notification delivery direta -> blocked
- permission bypass local -> blocked

### 9.4 Critério de saída
- todos os invariantes bloqueantes cobertos
- APIs aderentes ao OpenAPI
- schemas aderentes ao contrato
- eventos emitidos corretamente
- cobertura suficiente dos fluxos P1

## 10. Fase 5 — Validação operacional

### 10.1 Objetivo
Validar o módulo em fluxos reais de uso.

### 10.2 Fluxos obrigatórios
1. `need_detected -> objective -> session draft -> publish`
2. `athlete check-in -> readiness guard -> live adjustment`
3. `execution -> response evidence -> complete`
4. `feedback contextual -> close with outcome`
5. `cycle review -> adjust plan`
6. `restriction active -> block prescription without override`
7. `attention_queue -> resolve item`
8. `staff_handoff -> preserve continuity`

### 10.3 Evidências esperadas
- logs de fluxo ponta a ponta
- snapshots de estado antes/depois
- eventos emitidos
- nenhuma divergência runtime ↔ contrato

### 10.4 Critério de saída
- fluxos críticos executam corretamente
- sem necessidade de workaround manual
- boundaries preservados em runtime

## 11. Fase 6 — Hardening

### 11.1 Objetivo
Preparar o módulo para operação robusta.

### 11.2 Itens obrigatórios
- idempotência onde aplicável
- concorrência em transições de estado
- soft delete / archival policy
- performance de listagem e agenda
- logs estruturados
- retry seguro de eventos
- consistência transacional entre mutação e emissão
- proteção contra replay
- observabilidade mínima por fluxo crítico

### 11.3 Critério de saída
- operação robusta
- sem drift entre contrato e runtime
- preparado para evolução incremental

## 12. Lotes recomendados

### Lote A — Núcleo do treinador
- `training_intervention_cycle`
- `training_session`
- `session_objective`
- `session_block`
- `prescription_line`
- publish/start/complete
- invariantes críticas
- events básicos
- permission enforcement básico

### Lote B — Execução real
- `execution_record`
- `session_adjustment`
- planned vs actual
- attendance / evidence
- restriction guard
- readiness contextual

### Lote C — Feedback e revisão
- `feedback_thread`
- `coach_note`
- `decision_rationale`
- cycle review
- adjust future plan
- continuity snapshot

### Lote D — Atenção e refinamento
- `attention_queue_item`
- adaptive friction
- derived signals não soberanos
- refinamentos de UX
- integrações complementares

## 13. Definição de pronto por fase

### Fase 0 pronta
- IR congelado e versionado

### Fase 1 pronta
- superfícies geradas e validadas

### Fase 2 pronta
- isomorfismo comprovado

### Fase 3 pronta
- backend P1 implementado

### Fase 4 pronta
- testes determinísticos em PASS

### Fase 5 pronta
- fluxos operacionais validados

### Fase 6 pronta
- hardening concluído

## 14. Regras operacionais obrigatórias

- não implementar antes da materialização
- não editar manualmente artefato derivado sem regeneração controlada
- não introduzir endpoint fora do OpenAPI
- não introduzir estado fora do `STATE_MODEL`
- não criar regra crítica fora do IR/superfície soberana
- não violar boundary soberano
- não substituir raw data por derived signals
- não usar agentes para “completar lacuna” após o gate

## 15. Critério final de conclusão

O módulo `training` é considerado implementado deterministicamente quando:

- o IR promovido continua em `PASS`
- todas as superfícies aplicáveis estão materializadas
- o backend implementa o contrato sem divergência
- os testes bloqueantes estão em `PASS`
- os fluxos críticos funcionam em runtime
- as integrações respeitam boundaries soberanos
- não existe necessidade de interpretação criativa do agente em nenhuma etapa crítica

## 16. Regra final

**IR promovido é entrada.**
**Superfície soberana é contrato.**
**Código é consequência.**
