# HB_TRACK_PERSISTENCE_POLICY.md

version: 1.0.0
status: PROPOSTO
decision_type: politica_arquitetural
scope: hb_track
owners:
  - arquitetura
  - backend
  - dados
  - analytics
related_decisions:
  - HB_TRACK_ARCHITECTURE_DECISION.md
related_artifacts:
  - docs/_ssot/openapi.json
  - docs/_ssot/schema.sql
  - docs/_canon/MANUAL_BACKEND_CANONICO.md
  - docs/_canon/REGRAS_SISTEMAS.md

---

## 1. Objetivo

Definir a classificação canônica de persistência para cada módulo do HB Track e estabelecer as regras para quando um módulo ou subdomínio deve usar:

- CRUD
- EVENT_FIRST
- HYBRID

Esta política existe para prevenir:
- Event Sourcing em todo o sistema por entusiasmo
- perda de histórico de fatos onde isso importa
- deriva arquitetural entre módulos
- acoplamento acidental entre estado operacional e histórico analítico

---

## 2. Classes Canônicas de Persistência

### 2.1 CRUD

Definição:
Um módulo é classificado como CRUD quando sua preocupação principal é manter o estado operacional atual por meio de escritas transacionais e leituras relacionais diretas.

Características típicas:
- orientado ao estado atual
- esquema normalizado
- baixo valor de replay
- baixa necessidade de histórico imutável de fatos
- consultabilidade simples
- fluxo mais simples de depuração e migração

Use CRUD quando:
- o estado válido mais recente é o que importa
- replay histórico não é uma capacidade central do produto
- trilha de auditoria pode ser satisfeita por tabelas/logs de auditoria em vez de fluxos de eventos primários
- projeções derivadas não são centrais para o valor do módulo

---

### 2.2 EVENT_FIRST

Definição:
Um módulo é classificado como EVENT_FIRST quando sua fonte primária de verdade é uma sequência de fatos imutáveis ao longo do tempo.

Características típicas:
- escritas append-only ou orientadas a fatos
- alto valor de replay
- múltiplas projeções derivadas
- reconstrução temporal importa
- auditabilidade é intrínseca
- analytics depende da ordem e proveniência dos eventos

Use EVENT_FIRST quando:
- a sequência de fatos importa tanto quanto ou mais do que o estado atual
- replay/reconstrução é uma capacidade real
- projeções são críticas para o produto
- rastreabilidade imutável é necessária

---

### 2.3 HYBRID

Definição:
Um módulo é HYBRID quando requer tanto:
- gerenciamento transacional de estado atual
- histórico de fatos preservado como eventos append-only para fluxos específicos

Características típicas:
- estado operacional em agregados relacionais
- fluxos de fatos selecionados preservados para rastreabilidade, replay, analytics ou auditoria
- padrões de leitura mistos
- disciplina de modelagem mais rigorosa necessária

Use HYBRID quando:
- o estado atual importa operacionalmente
- mas parte do módulo produz fatos que não devem ser reduzidos a linhas sobrescrevíveis

---

## 3. Matriz de Classificação — Módulos Canônicos do HB Track

| Módulo | Classe | Razão Canônica |
|---|---|---|
| identity_access | CRUD | auth, roles, sessões, memberships, permissões são estado operacional |
| organizations | CRUD | dados mestres e estado de propriedade hierárquica |
| teams | CRUD | registro e estrutura/estado atual da equipe |
| athletes | CRUD | registro de atletas é centrado no estado atual |
| staff | CRUD | registro profissional e memberships |
| categories | CRUD | dados de referência/catálogo |
| venues | CRUD | dados de referência e suporte de agendamento |
| competitions | HYBRID | registro de competições é CRUD; ocorrências/resultados/histórico oficial podem gerar fluxos de fatos |
| matches | EVENT_FIRST | linha do tempo de partidas é fundamentalmente temporal e orientada a fatos |
| scouts | EVENT_FIRST | observações de scouting são fatos e anotações ao longo do tempo |
| training | HYBRID | planejamento/estado de sessão é CRUD; fatos de presença/eventos/progresso podem requerer histórico append-only |
| session_templates | CRUD | templates são artefatos de configuração em tempo de design |
| planning_periodization | CRUD | estruturas de planejamento são principalmente estado operacional/planejado |
| attendance | EVENT_FIRST | marcações de presença são fatos históricos com proveniência de ator/tempo |
| performance | HYBRID | KPIs atuais podem ser materializados, mas fatos medidos devem permanecer rastreáveis |
| analytics | EVENT_FIRST | projeções e insights derivam de fluxos de fatos brutos |
| reports | HYBRID | outputs gerados são artefatos atuais, mas alguns inputs/históricos de atualização de relatórios são baseados em fatos |
| video | HYBRID | registro de ativos é CRUD; anotações/marcações temporais são fluxos de fatos |
| attachments | CRUD | metadados de arquivo/blob e vinculação são registros de estado atual |
| notifications | EVENT_FIRST | tentativas de entrega, retentativas, resultados de canal são histórico de fatos |
| audit | EVENT_FIRST | trilha imutável por definição |
| wellbeing | HYBRID | formulários/indicadores operacionais podem ser estado atual; observações/inferências sensíveis requerem histórico rastreável |
| tasks_workflow | CRUD | estado de tarefas e quadros é principalmente operacional |
| comments_feedback | HYBRID | estado atual da thread é relacional, mas comentários autorais são fatos imutáveis de interação |
| integrations | CRUD | configurações de provedores, refs de credenciais, configurações de sincronização são estado operacional |
| ingestion | EVENT_FIRST | ingestão é proveniência de fatos, não meramente linhas mutáveis |
| projections | EVENT_FIRST | ciclo de vida de projeção depende de fatos upstream e capacidade de reconstrução |
| exports_imports | HYBRID | estado de job é CRUD; histórico de execução de importação/exportação é factual |
| billing | CRUD | assinaturas, refs de faturas, estado de plano são transacionais |
| settings | CRUD | preferências e estado de configuração |
| search | CRUD | geralmente camada operacional de suporte por índice, não fluxo de fatos fonte de verdade |
| dashboard | HYBRID | o dashboard em si é composição de projeção/leitura, baseado em fontes CRUD + derivadas de eventos |
| medical_health_adjacent | HYBRID / RESTRITO | formulários atuais podem ser CRUD, mas fatos sensíveis medidos/observados requerem forte rastreabilidade |
| psychology_support_ai | HYBRID / RESTRITO | inferência e observações requerem rastreabilidade, governança e separação da telemetria genérica |

---

## 4. Notas Canônicas por Módulo

### 4.1 identity_access = CRUD
Justificativa:
- usuários, roles, concessões, memberships, vínculos de auth e estado de sessão são entidades de estado atual
- auditoria imutável é necessária, mas pertence ao módulo `audit`, não ao modelo primário de persistência do módulo

Regra:
- não modele mudanças de permissão como estado primário via event sourcing a menos que haja necessidade comprovada de replay completo do histórico de autorização

---

### 4.2 matches = EVENT_FIRST
Justificativa:
- eventos de partida são inerentemente cronológicos
- evolução do placar, mudanças de posse, incidentes marcados, episódios táticos e referências de vídeo dependem da sequência temporal
- o placar atual é uma projeção; não é o fato primário

Regra:
- a fonte canônica deve preservar ordem do evento, ator, timestamp, proveniência e versão
- qualquer tabela de resumo mutável deve ser tratada como projeção derivada

---

### 4.3 scouts = EVENT_FIRST
Justificativa:
- scouting é orientado a observação
- sobrescrever uma observação destrói o histórico interpretativo
- analytics posterior pode reinterpretar fatos observados antigos sob novos modelos

Regra:
- cada registro de scouting deve ser modelado como fato ou anotação autorais com proveniência
- políticas de edição devem ser explícitas; sobrescrita destrutiva é desencorajada

---

### 4.4 training = HYBRID
Justificativa:
- sessões de treino têm estado operacional: rascunho, agendada, em_progresso, concluída, cancelada
- mas ocorrências de sessão também geram fatos: presença, transições de status, desvios de execução, notas do treinador, conclusão de exercício, observações de carga

Regra:
- agregado de sessão e agenda permanecem CRUD
- eventos de sessão com valor histórico devem ser append-only

Exemplos de fatos de treino append-only:
- presence_registered (presença_registrada)
- session_started (sessão_iniciada)
- session_finished (sessão_concluída)
- drill_completed (exercício_concluído)
- load_recorded (carga_registrada)
- coach_observation_added (observação_do_treinador_adicionada)

---

### 4.5 analytics = EVENT_FIRST
Justificativa:
- analytics não deve ser o escritor primário de verdade; deve consumir verdade a partir de fatos
- outputs analíticos são projeções, agregações, pontuações e snapshots derivados de fatos históricos

Regra:
- evite fazer tabelas de analytics a fonte canônica de verdade de negócio
- fatos brutos mensuráveis devem sobreviver independentemente da fórmula de pontuação atual

---

### 4.6 reports = HYBRID
Justificativa:
- definições de relatório, templates e metadados de arquivo gerado são relacionais
- tentativas de geração, gatilhos de atualização, logs de build e cadeias de proveniência são eventos factuais

Regra:
- um arquivo de relatório gerado pode ser metadados de estado atual
- histórico de geração deve permanecer rastreável como registros de fatos

---

### 4.7 audit = EVENT_FIRST
Justificativa:
- auditoria perde significado se reescrita
- imutabilidade é o ponto

Regra:
- registros de auditoria são append-only
- correções devem ser aditivas, nunca destrutivas

---

### 4.8 notifications = EVENT_FIRST
Justificativa:
- o valor de notificação inclui histórico de tentativas, resultado de entrega, contagem de retentativas, resposta do provedor e timing
- o "status" atual é apenas uma projeção sobre tentativas históricas

Regra:
- armazene cada tentativa de entrega como evento/fato
- exponha status resumido via projeção se necessário

---

### 4.9 wellbeing / psychology_support_ai = HYBRID / RESTRITO
Justificativa:
- pode haver estado operacional relacional como questionários, fluxos de revisão ou indicadores de status
- mas qualquer inferência, observação, evolução de pontuação ou cadeia de revisão humana requer rastreabilidade
- este domínio é sensível e não deve ser achatado em telemetria genérica do atleta

Regra:
- outputs de inferência devem carregar proveniência, contexto de modelo/versão e limite de revisão onde aplicável
- sobrescritas destrutivas de fatos interpretativos sensíveis são proibidas a menos que explicitamente governadas

---

## 5. Checklist de Admissão para EVENT_FIRST

Um módulo ou subdomínio pode ser classificado como EVENT_FIRST apenas se todos os itens abaixo forem satisfeitos.

### 5.1 Critérios obrigatórios
- [ ] o fato de negócio é naturalmente expresso como "algo aconteceu"
- [ ] a ordem histórica importa
- [ ] replay ou reconstrução fornece valor real
- [ ] pelo menos uma projeção derivada é necessária
- [ ] o esquema de evento pode ser versionado
- [ ] estratégia de idempotência existe
- [ ] identidade do produtor e proveniência são capturadas
- [ ] política de retenção e armazenamento existe
- [ ] política de reconstrução/reprocessamento existe
- [ ] observabilidade operacional existe para consumidores/projeções

### 5.2 Regra de bloqueio
Se três ou mais critérios obrigatórios não forem satisfeitos, o módulo NÃO DEVE ser EVENT_FIRST.

---

## 6. Checklist de Admissão para HYBRID

Um módulo pode ser HYBRID apenas se todos os itens abaixo forem verdadeiros.

- [ ] existe um agregado real de estado atual operacional
- [ ] existe um fluxo real de fatos dentro do mesmo contexto delimitado
- [ ] o fluxo de eventos tem consumidores explícitos
- [ ] o fluxo de eventos não é especulativo
- [ ] a propriedade do estado vs propriedade do fato está claramente definida
- [ ] não existe ambiguidade sobre qual camada é fonte de verdade para cada conceito

Regra de bloqueio:
Se a equipe não conseguir responder claramente "quais campos são aggregado de estado atual" e "quais fatos são append-only", o módulo deve regredir para CRUD até que seja esclarecido.

---

## 7. Regras Canônicas de Fonte de Verdade

### 7.1 Módulos CRUD
Fonte de verdade:
- tabelas de agregado relacionais

Suplementos permitidos:
- log de auditoria
- histórico de alterações
- caches derivados
- índices de busca

Mas esses suplementos não substituem o agregado como verdade primária.

### 7.2 Módulos EVENT_FIRST
Fonte de verdade:
- repositório imutável de fatos/eventos

Projeções permitidas:
- modelos de leitura
- dashboards
- resumos
- materializações de estado atual

Mas essas projeções devem ser reconstruíveis ou pelo menos rastreáveis aos fatos.

### 7.3 Módulos HYBRID
Fonte de verdade:
- dividida por conceito

Exemplo:
Em `training`:
- agendamento/status de sessão = agregado relacional
- marcações de presença e fatos de execução = fluxo de eventos append-only

Módulos híbridos DEVEM documentar essa divisão explicitamente.

---

## 8. Padrões Proibidos

Os seguintes padrões são proibidos.

### 8.1 Event Sourcing global por ideologia
Não force todos os módulos em event sourcing por uniformidade conceitual.

### 8.2 Resumos mutáveis como verdade histórica
Não sobrescreva histórico em módulos onde a sequência de fatos é relevante para o produto.

### 8.3 Fluxos de eventos sem consumidor
Não crie fluxos append-only que nenhuma funcionalidade, projeção ou necessidade de auditoria realmente utiliza.

### 8.4 Verdade mista sem propriedade
Não mantenha o mesmo conceito meio-autoritativo no estado de tabela e meio-autoritativo em logs de eventos sem regras explícitas de prioridade.

### 8.5 Analytics como verdade
Não promova outputs analíticos derivados a fonte primária de verdade para fatos esportivos brutos.

### 8.6 Inferência sensível sem proveniência
Não persista outputs de inferência psicológica/bem-estar sem proveniência, contexto de versão e política de revisão.

---

## 9. Regras Obrigatórias Entre Módulos

### 9.1 audit é sempre append-only
Qualquer módulo pode emitir para `audit`, mas não pode mutar fatos de auditoria passados.

### 9.2 notifications são logs de fatos
Qualquer módulo pode disparar notificações, mas o histórico de entrega de notificações pertence ao módulo `notifications` como tentativas/eventos factuais.

### 9.3 projeções nunca são verdade primária
Nenhuma tabela de projeção pode se tornar a fonte canônica a menos que seja explicitamente promovida por um registro de decisão separado.

### 9.4 importações/ingestão preservam proveniência
Quando dados externos entram no HB Track, a camada de ingestão deve preservar a fonte/proveniência mesmo que a camada operacional armazene estado normalizado.

---

## 10. Requisitos Mínimos de Esquema de Evento

Para cada fato append-only de EVENT_FIRST ou HYBRID, o registro armazenado DEVE incluir no mínimo:

- event_id
- event_type
- aggregate_type
- aggregate_id
- occurred_at
- recorded_at
- actor_type
- actor_id
- source_type
- source_system
- source_record_id
- payload_version
- payload
- correlation_id (quando aplicável)
- causation_id (quando aplicável)

Domínios sensíveis DEVEM adicionalmente incluir:
- review_status
- reviewer_id (se revisado por humano)
- model_name / model_version (se derivado de IA)
- confidence_level (se probabilístico)
- access_classification

---

## 11. Política de Migração

### 11.1 CRUD -> HYBRID
Permitido quando:
- um módulo previamente CRUD começa a produzir fatos com valor de replay/auditoria/analytics
- limites claros de fatos são definidos
- o modelo de estado antigo permanece válido para o estado atual operacional

### 11.2 HYBRID -> EVENT_FIRST
Permitido apenas com decisão arquitetural explícita porque isso muda a semântica de verdade primária.

### 11.3 EVENT_FIRST -> CRUD
Fortemente desencorajado.
Permitido apenas se:
- a adoção event-first foi prematura
- o valor de replay/projeção provou ser inexistente
- o caminho de migração preserva evidências históricas necessárias

---

## 12. Gate de Revisão para Novos Módulos

Todo novo módulo do HB Track DEVE declarar um dos seguintes:
- CRUD
- EVENT_FIRST
- HYBRID

E DEVE responder:
1. Qual é a fonte canônica de verdade?
2. A sequência de fatos importa?
3. Projeções são necessárias?
4. Replay é necessário?
5. O que é estado mutável vs fato imutável?
6. O módulo processa dados sensíveis?

Uma definição de módulo está incompleta sem essas respostas.

---

## 13. Conjunto Canônico Inicial Recomendado para o HB Track

### 13.1 CRUD
- identity_access
- organizations
- teams
- athletes
- staff
- categories
- venues
- session_templates
- planning_periodization
- attachments
- billing
- settings
- integrations
- tasks_workflow

### 13.2 EVENT_FIRST
- matches
- scouts
- analytics
- audit
- notifications
- ingestion
- projections
- attendance

### 13.3 HYBRID
- training
- competitions
- performance
- reports
- video
- dashboard
- comments_feedback
- exports_imports
- wellbeing
- medical_health_adjacent
- psychology_support_ai

---

## 14. Consequências Operacionais

### 14.1 Para backend
- repositórios e serviços devem respeitar a classe de persistência do módulo
- nenhum padrão de repositório genérico deve achatar semânticas de CRUD e EVENT_FIRST na mesma abstração

### 14.2 Para frontend
- telas de estado atual podem consumir DTOs de agregado
- telas de linha do tempo, analytics e marcação de vídeo devem preferir endpoints de projeção/visão derivados de fatos

### 14.3 Para analytics
- métricas derivadas devem referenciar fatos brutos estáveis, não apenas resumos mutáveis

### 14.4 Para governança
- ARs e contratos de módulo devem declarar explicitamente a classe de persistência
- verificações de paridade devem validar que a implementação corresponde à classe declarada

---

## 15. Definição de Pronto

Esta política está PRONTA apenas quando:
- cada módulo canônico tem uma classe de persistência atribuída
- contratos de módulo refletem a classe atribuída
- novos módulos não podem ser criados sem classificação
- módulos event-first/hybrid definem esquema mínimo de fatos
- módulos sensíveis definem sobreposições de governança
- revisão arquitetural usa esta política como referência bloqueante
