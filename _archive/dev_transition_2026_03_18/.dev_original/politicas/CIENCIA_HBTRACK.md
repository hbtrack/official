Abaixo está a análise do `SPORT_SCIENCE_RULES` ideal do HB Track, já alinhada às decisões arquitetônicas que fechamos nesta conversa e ao padrão real observado em plataformas maduras. Onde houver lacuna real, marquei `OPEN_DECISION`.

## 1. Funções operacionais do `SPORT_SCIENCE_RULES`

Esse arquivo resolve um problema central: transformar ciência aplicada do esporte em regra operacional determinística. No mundo real, times e plataformas maduras não trabalham só com “dados fisiológicos”; eles trabalham com regras explícitas que dizem o que medir, quando medir, como interpretar, quando o dado é válido e que decisão ele pode ou não sustentar. A WHOOP documenta constructs como `Recovery`, `Strain`, `Workout` e `Cycle` com significado, disponibilidade e uso claros; a Kitman Labs estrutura monitoramento de training load, physical performance, wellness trends e response to programming para apoiar decisões em tempo real. ([WHOOP para Desenvolvedores][1])

As unidades reais de valor operacional são:

* reduzir decisão ad hoc sobre carga, readiness, treino e recuperação;
* padronizar a leitura de wellness, sRPE, testing e indicadores derivados;
* ligar coleta → interpretação → decisão;
* impedir que treino, medical e analytics usem definições diferentes para a mesma métrica;
* permitir rastreabilidade e auditoria em ambiente contract-driven.
  A literatura recente sobre monitoramento em handebol também converge para isso: um AMS abrangente combina lesão/doença, carga interna/externa, bem-estar e prontidão, com suporte à análise e decisão. ([Kitman Labs][2])

## 2. Entidades e conceitos centrais

Normalmente, esse arquivo precisa conter entidades do tipo:

* métrica ou regra técnico-científica;
* janela de coleta;
* condição de disponibilidade do dado;
* inputs exigidos;
* lógica de interpretação;
* uso decisório;
* população/aplicabilidade;
* fonte/evidência;
* proibições de inferência.

Os conceitos centrais observáveis no mercado e nas fontes maduras são:

* carga interna;
* carga externa;
* readiness / prontidão;
* recovery / recuperação;
* wellness / bem-estar pré-sessão;
* esforço percebido de sessão;
* observação por ciclo ou janela fisiológica;
* testes físicos e funcionais;
* demanda competitiva específica da modalidade;
* especificidade posicional;
* prevenção integrada ao treino.
  WHOOP documenta explicitamente `Recovery`, `Strain`, `Cycle` e `Workout` como entidades distintas; ACSM se posiciona como padrão para testing e prescription; Aspetar explicita que entender as demands do handebol é essencial para prevenção, desenho do treino e especificidade por posição. ([WHOOP para Desenvolvedores][1])

## 3. Fluxos críticos

Os fluxos principais no `SPORT_SCIENCE_RULES` ideal são:

1. coleta pré-sessão
   O usuário informa ou o sistema recebe sinais de wellness/readiness antes do treino. A regra precisa dizer quando coletar, qual janela é válida e o que fazer se estiver ausente. WHOOP calcula `Recovery` ao acordar; no HB Track, a lógica equivalente é wellness/readiness pré-sessão com janela definida. ([WHOOP para Desenvolvedores][1])

2. captura de carga e sessão
   Durante ou após a sessão, entram dados de treino, esforço percebido, duração, eventuais testes rápidos e contexto do treino. WHOOP expõe `Workout` e `Strain`; os AMS líderes expõem training load e response to programming. ([WHOOP para Desenvolvedores][3])

3. derivação de indicador
   O sistema transforma entradas em um indicador operacional, por exemplo status de prontidão, carga da sessão, discrepância entre percepção e medida objetiva, ou sinal de revisão. Isso é o coração do documento: não guardar dado cru, mas regra de derivação e uso. ([Kitman Labs][4])

4. decisão aplicada
   Treinador, preparador ou staff usa o indicador para ajustar sessão, recuperação, progressão ou acompanhamento longitudinal. Esse é o padrão comum nas plataformas líderes. ([Kitman Labs][4])

5. análise longitudinal
   Os dados e regras alimentam tendências, comparação entre unidades, resposta ao programa e vigilância de risco. Kitman Labs explicita dashboards e reporting para isso. ([Kitman Labs][5])

## 4. Boundaries, integrações e escopo

O `SPORT_SCIENCE_RULES` toca diretamente:

* `training`, porque influencia planejamento, ajuste e interpretação de sessão;
* `wellness`, porque readiness/well-being entram como input;
* `analytics`, porque regras alimentam tendência, comparação e alertas;
* `medical`, porque prevenção, screening e return-to-play precisam de regras próprias;
* `DOMAIN_GLOSSARY`, porque os termos técnico-científicos precisam de semântica estável;
* `MODULE_SOURCE_AUTHORITY_MATRIX`, porque a autoridade da regra depende da fonte;
* eventualmente `DOMAIN_RULES_<MODULE>`, quando uma regra científica precisa ser consumida no fluxo funcional.

As integrações comuns no mercado são com wearable data, wellness forms, testing devices, systems de vídeo/tática e data platforms. WHOOP expõe OAuth, scopes e recursos separados para recovery/cycles/workout; Kitman Labs enfatiza centralização de wellness, performance e medical, e integração com dados táticos. ([WHOOP para Desenvolvedores][6])

`OPEN_DECISION`: quais integrações específicas o HB Track vai suportar primeiro. Isso não pode ser inferido sem decisão de produto.

## 5. Decisões arquitetônicas recorrentes

As decisões recorrentes observáveis em produtos líderes e que devem ser adotadas no HB Track são:

* centralizar métricas e regras em constructs semânticos estáveis, e não em campos soltos; WHOOP faz isso com `Recovery`, `Strain`, `Cycle` e `Workout`. ([WHOOP para Desenvolvedores][1])
* separar medida, janela/ciclo e decisão; WHOOP separa dados por recurso e por timing. ([WHOOP para Desenvolvedores][6])
* integrar wellness, load, performance e medical em uma mesma lógica de decisão; Kitman Labs faz isso explicitamente. ([Kitman Labs][7])
* combinar medidas subjetivas e objetivas, não depender de um único sinal; isso aparece nos AMS líderes e na literatura de monitoramento em handebol. ([Kitman Labs][4])
* preservar contexto esportivo: posição, fase, demanda competitiva, população; Aspetar reforça posição e demands do handebol. ([Revista de Medicina do Esporte Aspetar][8])
* documentar ausência/indisponibilidade do dado; WHOOP documenta explicitamente que nem todo ciclo terá `Recovery`. ([WHOOP para Desenvolvedores][9])
* evitar thresholds universais fora de contexto. Isso é uma decisão arquitetônica necessária para não congelar ciência aplicada como dogma.
  `OPEN_DECISION`: qual política formal de thresholds o HB Track vai adotar.

## 6. Tipos de contrato de API para `SPORT_SCIENCE_RULES`

Esse domínio não pode ser modelado como um CRUD comum porque o núcleo do problema não é “armazenar registros”; é governar ciclos de coleta, derivação, validade e decisão. Em um CRUD comum, você cria/lê/edita uma entidade como objeto estático. Aqui, boa parte do valor está em:

* regra de quando o dado existe;
* relação entre múltiplas entradas;
* derivação de indicador;
* consumo contextual pelo fluxo do treino;
* comportamento na ausência de dado.

WHOOP já mostra isso na prática: `Recovery` depende do `Cycle`, e nem todo ciclo tem recovery disponível. Isso não é semântica de CRUD puro; é semântica de observação fisiológica condicionada a janela válida. ([WHOOP para Desenvolvedores][9])

Também não é um “ecommerce adaptado”, porque não estamos lidando com catálogo, carrinho, pedido e estoque. O núcleo é evento fisiológico, monitoramento longitudinal e decisão esportiva. Os contratos corretos tendem a ser orientados a observações, janelas, indicadores derivados, reporting e consumo por workflows de treino, wellness, analytics e medical.

`OPEN_DECISION`: quais superfícies do pipeline do HB Track vão consumir isso primeiro.

## 7. Tradução para contract-driven

Para cada decisão importante:

**a) Métrica com semântica explícita**
SSOT: `DOMAIN_GLOSSARY.md` para definição do termo + `SPORT_SCIENCE_RULES.yaml` para funcionamento operacional.
Superfície: semântica + regra técnico-científica.
Não pode inferir: definição, inputs e uso decisório de cada constructo sem fonte.

**b) Janela de coleta e validade do dado**
SSOT: `SPORT_SCIENCE_RULES.yaml`.
Superfície: regra técnico-científica.
Não pode inferir: momento de coleta, janela válida, comportamento quando o dado faltar.

**c) Regra de disponibilidade/ausência**
SSOT: `SPORT_SCIENCE_RULES.yaml`, com reflexo posterior em validações e analytics.
Superfície: regra técnico-científica + possivelmente invariantes downstream.
Não pode inferir: que todo atleta sempre terá dado disponível.

**d) Integração de sinais subjetivos e objetivos**
SSOT: `SPORT_SCIENCE_RULES.yaml`; consumo em `DOMAIN_RULES_TRAINING.md` e analytics.
Superfície: ciência aplicada + regra funcional consumidora.
Não pode inferir: equivalência automática entre sinais subjetivos e objetivos.

**e) Especificidade do handebol e da posição**
SSOT: `SPORT_SCIENCE_RULES.yaml` quando for ciência aplicada da modalidade; `DOMAIN_AXIOMS_TRAINING.json` quando for verdade estrutural do módulo.
Superfície: ciência aplicada e axioma de módulo.
Não pode inferir: demands por posição, thresholds ou progressões sem fonte específica.

**f) Prevenção integrada ao treino**
SSOT: `DOMAIN_AXIOMS_TRAINING.json` para a verdade estrutural; `SPORT_SCIENCE_RULES.yaml` para métodos/protocolos; `DOMAIN_RULES_TRAINING.md` para consumo funcional.
Superfície: axioma + regra técnico-científica + regra funcional.
Não pode inferir: protocolo específico de prevenção só a partir do axioma.

**g) Autoridade da fonte**
SSOT: `MODULE_SOURCE_AUTHORITY_MATRIX.yaml`.
Superfície: governança de fontes.
Não pode inferir: promoção de benchmark funcional para axioma ou de ACSM para axioma específico de handebol.

## 8. Lista de UX/UI necessárias que aumentam usuários ativos

Como esse documento se relaciona diretamente com dado do usuário, UX/UI é decisiva. Os padrões de mercado sugerem que a adoção cresce quando a coleta é simples, o feedback é imediato e a interpretação é clara.

As UX/UI necessárias são:

* check-in pré-sessão rápido para wellness/readiness;
* visão diária do status do atleta/equipe;
* timeline de sessão com carga planejada vs observada;
* feedback pós-sessão simples para percepção de esforço;
* dashboards de tendência por atleta, posição, unidade e fase;
* alertas explicáveis, não “caixa-preta”;
* visualização de dados ausentes e qualidade da coleta;
* drill-down de por que uma decisão foi sugerida;
* comparação longitudinal sem sobrecarregar o usuário;
* superfície para staff interdisciplinar ver o mesmo atleta por lentes diferentes.
  WHOOP e Kitman Labs convergem em dashboards, reporting, recovery/readiness daily use e visão centralizada de performance. ([Kitman Labs][5])

`OPEN_DECISION`: qual conjunto mínimo de telas o HB Track quer lançar primeiro.

## 9. Aumento da performance / feedback de atletas de handebol

No mundo real, o impacto esperado é:

* melhor ajuste diário da carga;
* melhor adequação do treino ao estado do atleta;
* maior consistência entre staff técnico, físico e médico;
* menor ruído interpretativo sobre wellness/readiness;
* melhor identificação de discrepâncias entre percepção e resposta ao treino;
* melhor longitudinalidade do processo de desenvolvimento;
* mais personalização por posição, fase e categoria;
* mais rapidez para transformar dado em feedback útil ao treinador e ao atleta.
  A base pública para isso está no padrão dos AMS líderes e na literatura específica do handebol, que conecta demands, prevenção e desenho de treino à compreensão fina da modalidade. ([Kitman Labs][4])

Importante: esse impacto só aparece quando a regra é operacional e entra no workflow. Documento canônico sozinho não melhora performance; ele melhora consistência, rastreabilidade e capacidade do sistema de gerar decisão correta.

## 10. Roadmap

As decisões que você precisa fechar primeiro são:

1. o escopo formal do `SPORT_SCIENCE_RULES` dentro da governança;
2. se o arquivo nasce global ou por módulo — a decisão mais coerente continua sendo começar por `training`;
3. a taxonomia mínima de regra;
4. a política de autoridade de fonte;
5. a política de ausência de dado;
6. a política de thresholds/contextualização;
7. quais módulos consomem essa camada na primeira versão.

O lote mínimo de artefatos canônicos para começar é:

* `MODULE_SOURCE_AUTHORITY_MATRIX.yaml` atualizado;
* `SPORT_SCIENCE_RULES_TRAINING.yaml`;
* `DOMAIN_GLOSSARY.md` com os termos necessários;
* `DOMAIN_RULES_TRAINING.md` referenciando o consumo das regras;
* `DOMAIN_AXIOMS_TRAINING.json` com as verdades estruturais já fechadas.

As partes que devem ficar para depois são:

* thresholds detalhados e sensíveis a população;
* expansão para `medical`, `analytics` e `wellness` como arquivos próprios;
* integração específica com vendors externos;
* automações avançadas de decisão;
* regras de return-to-play mais profundas, a menos que o escopo inicial exija isso.

`OPEN_DECISION`: se o HB Track quer instalar também uma superfície de evidence review/versioning específica para cada regra técnico-científica.

### Tabela final

| decisão arquitetônica                        | superfície canônica recomendada                                                         | pode inferir?                                 | não pode inferir                                |
| -------------------------------------------- | --------------------------------------------------------------------------------------- | --------------------------------------------- | ----------------------------------------------- |
| constructs semânticos estáveis para métricas | `DOMAIN_GLOSSARY.md` + `SPORT_SCIENCE_RULES.yaml`                                       | pode inferir que precisa de definição formal  | não pode inferir definição específica sem fonte |
| janela de coleta e validade                  | `SPORT_SCIENCE_RULES.yaml`                                                              | pode inferir que toda regra precisa de timing | não pode inferir timing concreto                |
| comportamento com dado ausente               | `SPORT_SCIENCE_RULES.yaml`                                                              | pode inferir que ausência deve ser tratada    | não pode inferir fallback automático            |
| integração subjetivo + objetivo              | `SPORT_SCIENCE_RULES.yaml`                                                              | pode inferir necessidade de coexistência      | não pode inferir fórmula de combinação          |
| especificidade do handebol/posição           | `SPORT_SCIENCE_RULES.yaml` + `DOMAIN_AXIOMS_TRAINING.json`                              | pode inferir que contexto esportivo importa   | não pode inferir demand específica sem fonte    |
| prevenção integrada ao treino                | `DOMAIN_AXIOMS_TRAINING.json` + `SPORT_SCIENCE_RULES.yaml` + `DOMAIN_RULES_TRAINING.md` | pode inferir separação entre axioma e método  | não pode inferir protocolo preventivo           |
| autoridade de fonte                          | `MODULE_SOURCE_AUTHORITY_MATRIX.yaml`                                                   | pode inferir necessidade de governança        | não pode inferir promoção entre camadas         |
| consumo pelo fluxo do treino                 | `DOMAIN_RULES_TRAINING.md`                                                              | pode inferir que training consome a camada    | não pode inferir o fluxo final sem decisão      |
| analytics longitudinal                       | `SPORT_SCIENCE_RULES.yaml` + módulo `analytics` consumidor                              | pode inferir necessidade de tendência         | não pode inferir indicadores finais             |
| política de thresholds                       | `SPORT_SCIENCE_RULES.yaml`                                                              | pode inferir que thresholds exigem escopo     | não pode inferir cutoff universal               |

[CONTEXTO VERIFICADO]

A conclusão central da nossa conversa é esta: no HB Track, `SPORT_SCIENCE_RULES` não é um “arquivo de artigos” nem uma camada decorativa. Ele é a superfície canônica que transforma ciência aplicada em regra operacional determinística, separando com clareza o que é axioma do domínio, o que é regra funcional do módulo e o que é método/protocolo/cálculo/critério técnico-científico. Esse desenho é coerente com o padrão observado em plataformas maduras, que operam com wellness, readiness, load, testing e decision support como camada formal de produto, ainda que não publiquem um arquivo com esse nome.

## 1. Funções operacionais do `SPORT_SCIENCE_RULES`

No mundo real, esse arquivo entrega cinco vantagens operacionais principais.

Primeiro, ele impede que ciência aplicada contamine `DOMAIN_AXIOMS` e `DOMAIN_RULES`. Sem essa separação, o sistema tende a promover protocolo mutável para verdade estrutural, o que fragiliza o contract-driven.

Segundo, ele padroniza a relação entre coleta, interpretação e decisão. Isso é exatamente o que sistemas maduros fazem: transformar wellness, load, readiness, testing e injury risk em suporte à decisão diária, e não apenas em armazenamento de métricas.

Terceiro, ele torna explícito o comportamento esperado quando o dado existe, quando não existe, quando está incompleto e quando não pode ser usado para uma decisão. Esse padrão aparece com força em plataformas orientadas a performance e em APIs como a da WHOOP, que deixam claro quando determinados scores existem e como devem ser consumidos.

Quarto, ele cria uma base auditável para decisões de treino, recuperação, monitoramento e prevenção. Isso reduz arbitrariedade do agente e do produto.

Quinto, ele permite que o HB Track seja competitivo no mercado atual, porque líderes de mercado convergem em uma mesma lógica: dados multimodais, interpretação contextual, suporte operacional diário e integração entre coaching, performance e saúde.

As regras científicas esportivas que normalmente vivem aqui não são “verdades do handebol”. São regras como:

* quando coletar wellness;
* quando coletar sRPE;
* quando um indicador pode ser interpretado;
* como combinar carga interna e externa;
* quando um teste serve como readiness e quando não serve;
* como uma regra técnico-científica pode apoiar ajuste de carga, progressão, recuperação ou red flag.

## 2. Entidades e conceitos centrais

As entidades e conceitos centrais normalmente necessários nesse arquivo são:

* regra técnico-científica;
* fonte científica/autoritativa;
* aplicabilidade;
* janela de coleta;
* condição de validade;
* entrada requerida;
* indicador derivado;
* lógica de interpretação;
* uso decisório;
* comportamento com dado ausente;
* limitação de inferência;
* escopo populacional;
* papel consumidor da regra.

Em termos conceituais/fisiológicos, os candidatos mais recorrentes são:

* wellness pré-sessão;
* carga interna;
* carga externa;
* percepção subjetiva de esforço de sessão;
* readiness;
* recuperação;
* demanda competitiva;
* especificidade posicional;
* prevenção de lesão integrada;
* teste neuromuscular/funcional;
* progresso longitudinal;
* contexto de microciclo.

Campos funcionais mínimos que normalmente precisam existir por regra:

* identificador da regra;
* classe da regra;
* fonte/autoria;
* nível de evidência;
* contexto de aplicabilidade;
* entradas necessárias;
* momento de coleta;
* lógica de interpretação;
* finalidade decisória;
* consumidores autorizados;
* comportamento em ausência de dado;
* inferências proibidas;
* periodicidade de revisão.

`OPEN_DECISION`: o modelo final de campos do artefato ainda não foi formalizado no seu sistema canônico.

## 3. Fluxos críticos

O funcionamento lógico do `SPORT_SCIENCE_RULES` nos fluxos principais tende a seguir este padrão.

No fluxo pré-sessão, a regra governa wellness/readiness: quando coletar, em que janela, quais dados mínimos aceitar e quais decisões são permitidas com base neles.

No fluxo de sessão/treino, a regra governa observações de carga e contexto: o que pode ser registrado durante o treino e quais vínculos devem existir com sessão, objetivo, posição ou fase.

No fluxo pós-sessão, a regra governa sRPE, carga derivada e interpretação inicial da resposta ao treino. ACSM/GSSI é particularmente útil aqui para timing de coleta e integração entre medidas subjetivas e objetivas.

No fluxo longitudinal, a regra governa tendência, comparação planned vs achieved, coerência entre percepção e dados objetivos, e sinalização para revisão de plano.

No fluxo de prevenção/retorno progressivo, a regra governa como ciência aplicada pode apoiar continuidade ou restrição de treino sem substituir o módulo medical nem inventar decisão clínica.

No fluxo de analytics, a regra fornece o “como interpretar”, não apenas o “o que mostrar”.

## 4. Boundaries, integrações e escopo

Quem normalmente não “toca” diretamente o `SPORT_SCIENCE_RULES`:

* usuário final comum sem perfil técnico;
* módulo de identidade/acesso;
* regras oficiais da modalidade;
* glossário semântico puro;
* layout/UI contracts que só consomem saídas derivadas;
* contratos funcionais que não dependem de ciência aplicada.

Quem normalmente consome ou referencia:

* `training`;
* `wellness`;
* `analytics`;
* `medical` em pontos selecionados;
* relatórios de performance;
* mecanismos de alerta/insight;
* possíveis integrações com dispositivos e sistemas de athlete monitoring.

Arquivos que não devem ser confundidos com ele:

* `DOMAIN_AXIOMS` — verdade estrutural;
* `DOMAIN_RULES` — regra funcional do módulo;
* `HANDBALL_RULES_DOMAIN` — regra oficial/modalidade;
* `DOMAIN_GLOSSARY` — semântica normativa de termos.

Integrações comuns, no mundo real, são com:

* wearables;
* athlete monitoring systems;
* wellness/self-report apps;
* test devices;
* plataformas de vídeo/análise contextual;
* sistemas de medical/performance integrados.

`OPEN_DECISION`: quais integrações o HB Track adotará primeiro ainda não foi fechado e não deve ser inferido sem fonte/produto definidos.

## 5. Decisões arquitetônicas recorrentes

As decisões arquitetônicas mais recorrentes em sistemas líderes que devem ser adotadas no HB Track são as seguintes.

Separar definição, coleta, interpretação e decisão. WHOOP e plataformas maduras deixam claro que uma métrica não é só um número; ela tem definição, disponibilidade, uso e limitação.

Evitar métricas isoladas como fonte única de decisão. O padrão maduro é multimodal: wellness, load, readiness, performance testing, contexto e tendência longitudinal.

Assumir interpretação contextual e não binária. Plataformas e literatura recentes evitam reduzir retorno, carga e readiness a uma única regra simplista.

Modelar validade temporal do dado. Nem todo dado serve para toda decisão; a janela de coleta importa.

Separar autoridade científica de benchmark funcional. ACSM/Aspetar/EHF alimentam verdade técnico-científica; WHOOP, Sportplan, Learn Handball e líderes de mercado alimentam benchmark de modelagem de produto.

No HB Track, a execução prática dessas decisões implica:

* promover `SPORT_SCIENCE_RULES` à governança;
* exigir `source_id`, `decision_use`, `forbidden_inference` e janela de coleta;
* bloquear promoção de benchmark para regra científica;
* bloquear uso de regra científica como axioma estrutural;
* instalar gates de compatibilidade entre fonte, tipo de verdade e destino no contrato.

## 6. Tipos de contrato de API para `SPORT_SCIENCE_RULES`

Sem inventar endpoints, as especificidades de API aqui normalmente envolvem seis superfícies.

Superfície de coleta: entrada de wellness, percepção de esforço, observações, testes, medições e dados sincronizados.

Superfície de consulta: leitura de indicadores derivados, status de disponibilidade, contexto temporal e interpretação autorizada.

Superfície de processamento: transformação de entradas em indicadores/flags/regras aplicadas.

Superfície de auditoria: rastreabilidade de qual regra técnico-científica sustentou uma determinada interpretação.

Superfície de integração: ingestão/sincronização com fontes externas quando existirem.

Superfície de decisão derivada: exposição de outputs consumíveis por `training`, `analytics`, `wellness` ou `medical`.

Especificidades contratuais importantes:

* origem do dado;
* timestamp e janela válida;
* unidade/convenção;
* completude mínima;
* status de validade;
* provenance/regra aplicada;
* comportamento para dado ausente ou tardio;
* diferença entre valor observado e valor derivado.

`OPEN_DECISION`: o seu modelo canônico ainda não definiu se `SPORT_SCIENCE_RULES` influenciará APIs apenas por referência indireta ou se terá superfícies dedicadas em contratos.

## 7. Possíveis GAPS para contract-driven e como evitá-los

**GAP 1 — Misturar axioma, regra funcional e regra científica**
Como evitar: instalar `MODULE_SOURCE_AUTHORITY_MATRIX` e taxonomy clara de destinos.
Como identificar: o mesmo conteúdo aparece simultaneamente em `DOMAIN_AXIOMS`, `DOMAIN_RULES` e ciência aplicada.
Como solucionar: reclassificar por tipo de verdade e bloquear duplicação.

**GAP 2 — Congelar thresholds universais sem contexto**
Como evitar: exigir escopo populacional, posição, faixa etária, fase e fonte.
Como identificar: regra com cutoff sem contexto de aplicabilidade.
Como solucionar: descer para `OPEN_DECISION` ou restringir a população/uso.

**GAP 3 — Benchmark de mercado promovido a verdade científica**
Como evitar: separar `benchmark_functional` de `sport_science_authority`.
Como identificar: regra científica sustentada por vendor de produto sem base científica primária.
Como solucionar: mover benchmark para `DOMAIN_RULES` ou `MODULE_SOURCE_AUTHORITY_MATRIX`.

**GAP 4 — Falta de regra para dado ausente/inválido**
Como evitar: tornar obrigatório `missing_data_behavior`.
Como identificar: o sistema toma decisão mesmo sem dado válido.
Como solucionar: definir bloqueio, degradação ou fallback explícito.

**GAP 5 — Falta de temporalidade da coleta**
Como evitar: exigir `collection_window` e `validity_window`.
Como identificar: wellness pré-sessão coletado tarde demais ou sRPE interpretado fora de janela sem critério.
Como solucionar: modelar janelas e políticas de invalidação.

**GAP 6 — Ciência do esporte sem uso decisório explícito**
Como evitar: toda regra precisa declarar `decision_use`.
Como identificar: regra “interessante”, mas sem consumidor operacional.
Como solucionar: remover do canônico ou mover para nota/evidência.

**GAP 7 — Medical invadindo training ou training invadindo medical**
Como evitar: boundary explícito por módulo e por tipo de decisão.
Como identificar: regra técnico-científica vira recomendação clínica ou decisão terapêutica sem base.
Como solucionar: mover decisão clínica para escopo apropriado e limitar `decision_use`.

**GAP 8 — Falta de revisão científica periódica**
Como evitar: definir `review_cycle` por regra.
Como identificar: regra antiga sem revisão ou com fonte superada.
Como solucionar: marcar como desatualizada, suspender uso ou atualizar fonte.

## 8. Relação com os dados de usuários: segurança, ciência e performance

A relação do `SPORT_SCIENCE_RULES` com dados do usuário existe em três níveis.

Nível 1: semântico e estrutural.
Ele define quais tipos de dados têm significado operacional: wellness, load, readiness, testing, resposta ao treino.

Nível 2: interpretativo.
Ele determina como certos dados podem ser usados, quando podem gerar insight e quando não podem sustentar decisão.

Nível 3: sensível/performance.
Ele se relaciona com dados potencialmente sensíveis ou de alta criticidade operacional, porque envolve estado físico, resposta fisiológica, risco, prontidão e possíveis limitações de treino.

Por isso, o arquivo deve:

* restringir inferência;
* explicitar consumidores autorizados;
* separar observação de interpretação;
* evitar extrapolação clínica indevida;
* sustentar rastreabilidade e auditoria.

Do ponto de vista de segurança e governança, o dado não é só “Pessoal”. Ele também é “performance-critical”. O uso errado pode afetar treino, carga, recuperação e até risco operacional do atleta.

`OPEN_DECISION`: a política final de classificação de sensibilidade e controle de acesso por tipo de dado ainda precisa ser cristalizada no sistema.

## 9. Aplicação ao handebol

No mundo real do handebol, `SPORT_SCIENCE_RULES` pode sustentar ações como:

* governar wellness pré-treino para sessões técnicas, táticas e físicas;
* apoiar ajuste de volume/intensidade no microciclo;
* relacionar demanda competitiva com posição e função de jogo;
* apoiar interpretação de resposta ao treino em atletas de base versus adultos;
* integrar prevenção de lesão ao aquecimento e ao plano;
* qualificar leitura de carga em semanas com jogo, viagem ou acúmulo de sessões;
* sustentar testes simples e repetíveis de readiness quando apropriado;
* permitir analytics de planned vs achieved load;
* conectar dados físicos a contexto técnico/tático sem reduzir a análise a wearable-only;
* apoiar sinalização de atenção para treinador, performance staff e medical, cada um no seu boundary.

No handebol, o diferencial é que essas ações precisam sempre respeitar:

* posição;
* faixa etária;
* fase da temporada;
* contexto competitivo;
* natureza intermitente e específica da modalidade.

## 10. Roadmap

As decisões que você precisa fechar primeiro são:

1. se `SPORT_SCIENCE_RULES` deve começar por `training`;
2. qual taxonomia mínima de regras será aceita;
3. quais fontes têm autoridade científica por módulo;
4. qual boundary exato entre `SPORT_SCIENCE_RULES`, `DOMAIN_RULES`, `medical` e `analytics`;
5. se o artefato entra em YAML canônico e como será validado por gate.

O lote mínimo de artefatos canônicos para começar é:

* `MODULE_SOURCE_AUTHORITY_MATRIX.yaml` atualizado;
* ADR de instalação do artefato;
* inclusão de `SPORT_SCIENCE_RULES_<MODULE>` no layout e nas rules do sistema;
* template canônico do arquivo;
* `DOMAIN_GLOSSARY.md` com termos essenciais;
* versão inicial de `SPORT_SCIENCE_RULES_TRAINING.yaml`;
* regra de mudança/revisão científica;
* gate mínimo de compatibilidade entre fonte, tipo de verdade e destino.

As partes que devem ficar para depois são:

* thresholds mais específicos;
* baterias completas de teste;
* integrações concretas com dispositivos/vendors;
* regras avançadas de return-to-play;
* expansão imediata para todos os módulos;
* automações derivadas complexas antes da taxonomia mínima estabilizar.

## Tabela final

| decisão arquitetônica                                    | superfície canônica recomendada                                    | pode inferir?                                         | não pode inferir                                |
| -------------------------------------------------------- | ------------------------------------------------------------------ | ----------------------------------------------------- | ----------------------------------------------- |
| separar verdade estrutural de regra científica           | `DOMAIN_AXIOMS` vs `SPORT_SCIENCE_RULES`                           | classificar por tipo de verdade                       | promover protocolo a axioma                     |
| instalar autoridade de fonte por módulo                  | `MODULE_SOURCE_AUTHORITY_MATRIX.yaml`                              | permitir promoção por fonte autorizada                | tratar benchmark como autoridade científica     |
| centralizar ciência aplicada em artefato próprio         | `SPORT_SCIENCE_RULES_<MODULE>.yaml`                                | métodos, timing, interpretação, uso decisório         | revisão bibliográfica solta ou marketing        |
| exigir comportamento para dado ausente                   | `SPORT_SCIENCE_RULES_<MODULE>.yaml`                                | bloquear ou degradar decisão sem dado válido          | assumir disponibilidade implícita               |
| exigir janela de coleta/validade                         | `SPORT_SCIENCE_RULES_<MODULE>.yaml`                                | usar timing como parte da regra                       | interpretar métrica fora de janela sem critério |
| usar benchmark de mercado como inspiração de produto     | `MODULE_SOURCE_AUTHORITY_MATRIX.yaml` + `DOMAIN_RULES_<MODULE>.md` | derivar padrão funcional/UX                           | derivar regra científica ou axioma              |
| governar termos técnico-científicos                      | `DOMAIN_GLOSSARY.md`                                               | definir semântica normativa dos termos                | definir protocolo ou threshold no glossário     |
| manter regra oficial da modalidade separada              | `HANDBALL_RULES_DOMAIN.md`                                         | ancorar regra esportiva formal                        | levar coaching/science aplicada para HBR        |
| permitir consumo por training/analytics/wellness/medical | `DOMAIN_RULES_<MODULE>.md` + contratos derivados                   | usar outputs de ciência aplicada em fluxos do produto | dissolver boundaries entre módulos              |
| revisar cientificamente regras ao longo do tempo         | `SPORT_SCIENCE_RULES_<MODULE>.yaml` + política de mudança          | atualizar regra com revisão/fonte                     | assumir estabilidade eterna de regra científica |
