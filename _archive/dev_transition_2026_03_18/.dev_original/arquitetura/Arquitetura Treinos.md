Leia o texto abaixo para entender o panorama de mercado, os padrões de produto, as decisões de arquitetura e as oportunidades estratégicas para o módulo `Training` do HB Track. 

# O panorama atual do mercado se divide em quatro blocos.

O primeiro bloco é o dos sistemas mais próximos do que você provavelmente quer como benchmark principal para `Training`: **XPS Network / Sideline Sports**. O produto se apresenta como uma plataforma para organizar e planejar treinamentos coletivos e individuais, comunicar com atletas, analisar treino/performance, manter observações de coaching, além de oferecer sessões de equipe, playbook, mensagens, perfil do atleta e strength & conditioning. Isso torna o XPS um dos benchmarks mais úteis para arquitetura de `Training`, porque ele trata treino como um domínio integrado de planejamento + execução + comunicação + análise, e não como cadastro simples de sessão. ([Sideline Sports](https://www.xpsnetwork.com/?utm_source=chatgpt.com))
O segundo bloco é o dos **AMS de alta performance** — sistemas maduros para esporte profissional, onde `Training` não vive isolado. Aqui entram **Smartabase**, **Teamworks AMS**, **Kitman Labs** e **Catapult Athlete Monitoring**. O padrão entre eles é consistente: centralização de dados de performance, formulários customizáveis, wellness/readiness, carga de treino, risco/injúria, relatórios e integrações com múltiplas fontes. Teamworks fala explicitamente em unificar contexto do atleta para decisão integrada; Smartabase enfatiza coleta de dados, agendamento e feedback ao atleta; Kitman Labs destaca agregação de milhares de pontos de dados e integração com centenas de provedores; Catapult centraliza sessões, partidas e dados de performance em um hub único. Isso mostra que, em sistemas maduros, `Training` quase sempre é um hub operacional conectado a wellness, medical, analytics e communication. 


O terceiro bloco é o dos sistemas focados em **prescrição e execução de treino/força**: **BridgeAthletic** e **TeamBuildr**. Eles são menos “AMS global” e mais fortes em builder de programas, bibliotecas de exercícios, templates, calendário individual, acompanhamento de sessão, métricas por treino, comunicação coach-atleta e entrega mobile. Bridge destaca builder, templates, assignment e tracking remoto; TeamBuildr enfatiza criação de programas, tracking de resultados, coach review, feed/chat e métricas de sessão. Esses produtos são úteis para desenhar a parte interna do `Training` que lida com prescrição, progressão, exercício, bloco, carga planejada vs executada e aderência. 
O quarto bloco é o dos sistemas de **club/youth operations** e dos sistemas **adjacentes ao treino**. Em club/youth, o nome mais maduro é **Sportlyzer**, que cobre calendário central, presença, disponibilidade, diary de treino, métricas diárias, lesão/doença, testes, integração com GPS e comunicação com atletas/pais. Para um produto como HB Track, isso é relevante porque mostra o padrão operacional de categorias de base e clubes menores. No adjacente, **Hudl** e **Handball.ai** importam, mas por razões diferentes: Hudl é fortíssimo em vídeo, análise e workflow técnico, porém não aparece como o melhor benchmark primário para o núcleo de `Training`; Handball.ai é claramente handebol-específico, mas o material público visível aponta mais para scouting/estatística e base digital do treinador do que para um AMS completo de treino. Então Handball.ai é bom benchmark de semântica do handebol; não, pelo que consegui verificar publicamente, de arquitetura full-stack de `Training`. ([sportlyzer.com](https://www.sportlyzer.com/en/?utm_source=chatgpt.com))
Se eu tivesse que reduzir isso a uma lista canônica de benchmarking para o HB Track, ficaria assim:

**Benchmark principal de arquitetura de `Training`**
XPS Network.

**Benchmark de ecossistema high-performance / AMS**
Smartabase, Teamworks AMS, Kitman Labs, Catapult.

**Benchmark de prescrição e execução de treino**
BridgeAthletic, TeamBuildr.

**Benchmark de operação de clube/base**
Sportlyzer.

**Benchmark semântico de handebol**
Handball.ai.

A pergunta que você não fez, mas deveria fazer antes de escrever contratos, é esta: **“qual tipo de sistema eu quero que o módulo `Training` seja dentro do HB Track?”** Porque a arquitetura muda bastante conforme a resposta.

Se o seu `Training` for um **planner operacional de coaching**, o benchmark dominante é XPS, e o contrato precisa nascer com entidades como `training_session`, `session_block`, `drill/exercise`, `attendance`, `coach_notes`, `attachments`, `playbook_reference`, `communication`, `session_status`, `team_scope` e `athlete_scope`. ([Sideline Sports](https://www.xpsnetwork.com/?utm_source=chatgpt.com))
Se ele for um **hub de performance**, então `Training` precisa ser desenhado desde o início para se acoplar formalmente a `wellness`, `medical`, `analytics`, `identity_access`, `audit` e `notifications`, porque o padrão de mercado é treino conectado a readiness, injury risk, monitoring e reporting. ([Teamworks](https://teamworks.com/ams/?utm_source=chatgpt.com))
Se ele for um **motor de prescrição individual/coletiva**, os contratos precisam suportar template de treino, progressão, exercise library, assignment individual, versionamento de plano, execução mobile e comparação planned vs completed. ([BridgeAthletic](https://www.bridgeathletic.com/?utm_source=chatgpt.com))
Minha leitura objetiva para o HB Track é esta: o seu módulo `Training` não deveria ser modelado como “agenda de sessões”. O mercado maduro mostra que isso é insuficiente. O formato mais robusto é tratar `Training` como um domínio central com quatro subcapacidades: **periodização/calendário, prescrição, execução/adesão, e telemetria operacional**. Isso é o que mais se repete entre os sistemas maduros. ([Sideline Sports](https://www.xpsnetwork.com/?utm_source=chatgpt.com))
Em termos práticos, para o HB Track eu começaria o benchmark arquitetural nesta ordem:
1. XPS Network, para desenho funcional do módulo.
2. Smartabase/Teamworks/Kitman/Catapult, para boundaries e integrações obrigatórias.
3. BridgeAthletic/TeamBuildr, para granularidade de prescrição.
4. Sportlyzer, para operação de base/clube.
5. Handball.ai, para vocabulário e casos handebol-específicos.

O próximo passo lógico é transformar esse levantamento em uma **matriz canônica do módulo `Training`** com quatro colunas: `capacidade de mercado`, `sistemas que a provam`, `artefato de contrato obrigatório`, `o agente pode/não pode inferir`. Isso é o que evita que o contrato nasça como CRUD genérico.

---

Em sistemas maduros, o módulo `Training` existe para reduzir fricção decisória do treinador e transformar informação dispersa em ação operacional diária. O padrão de mercado é este: o treinador não trabalha primeiro em “sessão”; ele trabalha em “intenção competitiva”, “necessidade detectada”, “plano”, “execução”, “resposta do atleta” e “ajuste”. XPS, por exemplo, combina planejamento de treino individual e coletivo, comunicação, monitoramento de readiness/wellness/training load e playbook/tática no mesmo fluxo; Teamworks AMS centraliza carga, testes, surveys e dashboards para produzir programas individualizados; BridgeAthletic e TeamBuildr focam em builder de programas, biblioteca de exercícios, tracking de prescrito vs realizado e adaptação rápida do plano. ([Sideline Sports](https://www.xpsnetwork.com/?utm_source=chatgpt.com))
No mundo real, o problema que esse módulo resolve não é “cadastrar treino”. O problema real é: o treinador precisa converter contexto competitivo e dados do elenco em uma intervenção treinável, coordenada e executável sem perder tempo com planilhas, mensagens soltas, vídeos dispersos e memória informal. Em clubes e equipes, isso significa decidir o que treinar, com quem, em que dose, com qual objetivo, com qual restrição, e depois verificar se o treino produziu a resposta esperada. Os sistemas maduros deixam claro que o valor está em centralizar contexto, reduzir esforço de coordenação e acelerar ajuste de decisão. Teamworks fala explicitamente em dar uma visão holística para decisão integrada; Smartabase destaca profiling, load planning e monitoring para tornar a informação acionável mais rápido; XPS enfatiza manter planejamento, comunicação, análise e feedback em um só lugar. ([Teamworks](https://www.smartabase.com/?utm_source=chatgpt.com))
A unidade real de valor operacional desse módulo, portanto, não é a “sessão” isolada. A unidade mais fiel ao mundo real é o **ciclo de intervenção de treino**: uma necessidade detectada gera um objetivo, que gera um plano, que gera uma sessão/bloco prescrito, que gera execução e resposta observada, que retroalimenta o próximo ajuste. Em termos de domínio, sua unidade pode ser modelada como `training_intervention` ou `training_prescription_cycle`; a `training_session` é só um dos artefatos internos desse ciclo. Isso é coerente com o que os sistemas maduros mostram: Sportlyzer organiza ciclos/volume/projeção; XPS conecta organização, monitoramento, tática e feedback; Smartabase e Teamworks operam com profiling → loading → monitoring → decision. ([sportlyzer.com](https://www.sportlyzer.com/en/?utm_source=chatgpt.com))
Sobre vídeos, playbooks e feedbacks conversacionais com atletas: fazem diferença, mas não como “acessórios”. Eles agregam valor quando encurtam o ciclo entre instrução, entendimento e correção. XPS posiciona playbook, diagramas, animações e feedback instantâneo como parte do fluxo de tática e análise, não como biblioteca passiva. BridgeAthletic destaca upload de vídeos, exemplos em mídia, mensagens e feedback remoto como parte do coaching e da adaptação do treino. Isso sugere uma regra importante para o HB Track: vídeo, playbook e feedback conversacional só têm valor operacional quando estão anexados a uma prescrição, a um bloco, a um objetivo ou a um evento de execução/avaliação. Se virarem mídia solta, não resolvem o problema central. ([Sideline Sports](https://www.xpsnetwork.com/?utm_source=chatgpt.com))
Também há uma distinção crítica que você não perguntou, mas deveria fixar no contrato: o módulo `Training` resolve dois trabalhos diferentes e ambos precisam aparecer no modelo. O primeiro é **coordenação coletiva**: calendário, presença, disponibilidade, plano semanal, staff, comunicação, logística. O segundo é **prescrição e adaptação individual**: carga, readiness, regressão/progressão, restrição médica, metas de desenvolvimento, evidência de resposta. Sportlyzer mostra fortemente o primeiro; Bridge, TeamBuildr, Smartabase e Teamworks mostram fortemente o segundo; XPS fica no meio e por isso é benchmark tão útil. ([sportlyzer.com](https://www.sportlyzer.com/en/?utm_source=chatgpt.com))
Se você quer listar as entidades, objetos e conceitos que normalmente precisam existir, eu separaria em camadas de domínio.

Primeiro, as entidades centrais de planejamento. Aqui entram `training_cycle` ou `periodization_cycle`, `microcycle`, `training_day`, `training_session`, `session_block`, `session_objective`, `session_theme`, `session_status`, `team_scope`, `athlete_scope`, `coach_assignment` e `facility/location`. Sem isso, você não modela o que os sistemas maduros chamam de season planning, cycles, daily/weekly planning e team/individual planning. ([sportlyzer.com](https://www.sportlyzer.com/en/?utm_source=chatgpt.com))
Depois, as entidades de prescrição. Aqui entram `exercise` ou `drill`, `exercise_library`, `exercise_variant`, `instruction`, `media_asset`, `video_clip`, `playbook_item`, `diagram`, `animation`, `parameter_set` e `prescription_line`. Em força e condicionamento isso inclui reps, sets, tempo, velocity, alternatives, progression/regression; em treino técnico-tático inclui tarefa, organização, regras, coaching points, constraints, tempo de bloco e critério de sucesso. Bridge explicita biblioteca grande de exercícios, templates e parâmetros de performance; XPS explicita diagramas, animações e playbook. ([BridgeAthletic](https://www.bridgeathletic.com/personal-trainer?utm_source=chatgpt.com))
Em seguida, as entidades de execução e adesão. Aqui entram `attendance`, `availability`, `rsvp`, `completion`, `performed_load`, `modified_prescription`, `athlete_note`, `coach_note`, `session_report`, `post_session_report` e `exception_event`. Sportlyzer trabalha fortemente com calendário, RSVP e attendance; Teamworks expõe post-session reporting e forms; Bridge e TeamBuildr trabalham com tracking do que foi realizado. ([sportlyzer.com](https://www.sportlyzer.com/en/?utm_source=chatgpt.com))
Na camada de monitoramento e contexto do atleta, normalmente precisam existir `wellness_check`, `readiness_score`, `training_load`, `rpe`, `acute_chronic_context` se você for modelar isso depois, `performance_test`, `injury_flag`, `illness_flag`, `restriction`, `return_to_play_status`, `survey_response` e `alert`. Os sistemas maduros repetem esse padrão: XPS fala em readiness, wellness e training load; Teamworks agrega load, testing, surveys, nutrition and medical; Smartabase trabalha com profiling, loading, monitoring, availability e hydration. ([Sideline Sports](https://www.xpsnetwork.com/?utm_source=chatgpt.com))
Há ainda a camada de desenvolvimento e inteligência técnica. Aqui entram `development_goal`, `individual_development_plan`, `need_detected`, `evidence_source`, `recommendation`, `coach_decision`, `review`, `feedback_thread` e `comparison_baseline`. Isso é o pedaço que liga estatística/analytics ao treino. Teamworks fala em data-informed Individual Development Plans; Catapult e outros vendors enfatizam usar monitoramento e análise para otimizar sessão e individualização. ([Teamworks](https://www.smartabase.com/?utm_source=chatgpt.com))
Por fim, existem conceitos transversais que quase sempre precisam estar explícitos, mesmo quando não são “entidades” principais: `planned_vs_actual`, `team_vs_individual`, `objective_vs_outcome`, `coach_visibility`, `staff_permissions`, `versioning`, `approval`, `audit trail`, `notification`, `integration_source` e `attachment provenance`. Os sistemas maduros mostram org/group/role structures, permissions-based views, API/integrations e fluxo colaborativo entre múltiplos stakeholders. ([Teamworks](https://www.smartabase.com/?utm_source=chatgpt.com))
Se eu condensar isso para o HB Track, a lista canônica mínima de objetos do módulo `Training` seria:

`training_cycle`, `microcycle`, `training_session`, `session_block`, `session_objective`, `exercise`, `exercise_library`, `prescription_line`, `media_asset`, `playbook_item`, `attendance`, `availability`, `wellness_check`, `readiness`, `training_load`, `rpe`, `restriction`, `session_report`, `coach_note`, `athlete_feedback`, `development_goal`, `individual_plan`, `recommendation`, `alert`, `notification_link`, `audit_event`.

A decisão arquitetural mais importante aqui é esta: **estatística não deveria criar treino diretamente**. O correto, pelo padrão dos sistemas maduros, é estatística gerar `need_detected` ou `recommendation`, e o treinador transformar isso em `objective` e `prescription`. Isso preserva a autoridade técnica do coach e evita automação opaca. Essa é uma das perguntas não feitas que mais afeta o contrato.

Minha recomendação objetiva para o HB Track é modelar `Training` como um domínio centrado em:
`Need -> Objective -> Prescription -> Session -> Execution -> Response -> Review -> Adjustment`

Esse fluxo representa melhor a unidade operacional real do módulo do que qualquer CRUD de sessão.

O próximo passo lógico é eu te entregar uma **matriz canônica do módulo `Training`** com:
`capacidade operacional -> problema real -> entidade/objeto obrigatório -> o que pode ser inferido -> o que é proibido inferir -> boundary com analytics/wellness/medical`.

---

Há uma resposta honesta e uma resposta estratégica.

A honesta é: eu não consigo afirmar, com base pública verificável, quais vendors “contrariam estatísticas do mercado” com uma taxa de retenção superior, porque quase nenhum publica churn, WAU/MAU, cohort retention ou stickiness de forma auditável. O que dá para verificar publicamente é outra coisa: **quais padrões de produto os sistemas maduros repetem quando querem aumentar uso contínuo e reduzir abandono**. Esses padrões aparecem de forma consistente em XPS, Teamworks AMS, BridgeAthletic, TeamBuildr, Kitman e Sportlyzer. ([Sideline Sports](https://www.xpsnetwork.com/?utm_source=chatgpt.com))
A estratégica é: sistemas esportivos são abandonados quando viram “lugar para preencher coisa”. Eles continuam vivos quando se tornam o **sistema operacional diário do treinador e do atleta**. É exatamente isso que os players maduros sinalizam: calendário, comunicação, readiness/wellness, prescrição, execução, feedback, vídeo, participação, alertas e decisão em um mesmo fluxo operacional. XPS se vende como lugar único para planejamento, comunicação, monitoramento, playbook e feedback instantâneo; Teamworks/Smartabase enfatiza visão holística e desenvolvimento individual; Kitman destaca status do atleta, alertas e comunicação em tempo real; TeamBuildr e Bridge focam em entrega simples do treino, tracking, vídeos, mensagens e ajuste em cima da prontidão do dia. ([Sideline Sports](https://www.xpsnetwork.com/?utm_source=chatgpt.com))
O que reduz abandono, na prática, não é “ter mais features”. É ter decisões corretas de produto.

Primeiro: **o sistema precisa economizar tempo toda vez que é aberto**. Bridge fala explicitamente em tirar horas de planilha/formatação e permitir criar e atribuir programas a grupos em minutos; Sportlyzer enfatiza calendário, RSVP, attendance, comunicação e relatórios rápidos; XPS fala em manter tudo em um só lugar. Quando o treinador sente economia líquida de tempo, ele volta. Quando sente burocracia, ele sai. ([Sideline Sports](https://www.xpsnetwork.com/?utm_source=chatgpt.com))
Segundo: **o sistema precisa fazer parte da rotina do atleta, não só da rotina do staff**. TeamBuildr entrega treino no app, questionários, vídeos, histórico e feedback; Kitman Player App permite wellness, RPE, agenda e feedback; Sportlyzer Player centraliza agenda, attendance, mensagens, lesão/doença e histórico. Isso aumenta recorrência porque o atleta tem algo real para fazer ali, e não apenas “receber ordem”. ([teambuildr.com](https://www.teambuildr.com/remote-training-with-teambuildr?utm_source=chatgpt.com))
Terceiro: **o sistema precisa reduzir ambiguidade**. Bridge destaca consistência, clareza e “tirar ambiguidade da equação”; XPS fala em instruções impossíveis de entender errado; Teamworks Forms mostra lógica condicional para reduzir campos inúteis e melhorar completion. Em produto esportivo, clareza operacional vale mais que sofisticação técnica invisível. ([BridgeAthletic](https://www.bridgeathletic.com/tactical?utm_source=chatgpt.com))
Quarto: **o sistema precisa capturar o contexto do dia e permitir ajuste imediato**. Os vendors maduros convergem aqui: readiness, RPE, wellness, restrição, disponibilidade, status, alertas e edição on-the-fly. Bridge fala em editar regressões/progressões com base em readiness, lesão e equipamento; XPS monitora readiness, wellness e training load; Kitman expõe status do jogador, alertas e comunicação em tempo real; TeamBuildr trabalha com readiness, tracking e feedback. Isso reduz abandono porque o sistema deixa de ser “arquivo histórico” e vira ferramenta de decisão naquele dia. ([Sideline Sports](https://www.xpsnetwork.com/?utm_source=chatgpt.com))
Quinto: **o sistema precisa devolver feedback visível e rápido**. XPS enfatiza instant feedback; TeamBuildr expõe progress graphs, workout history, goal feedback; Bridge mostra trends, PRs e leaderboards; Sportlyzer transforma attendance e agenda em histórico operacional. Usuário permanece quando sente retorno tangível do dado que registrou. ([Sideline Sports](https://www.xpsnetwork.com/?utm_source=chatgpt.com))
Sexto: **o sistema precisa sobreviver à troca de staff e à multidisciplinaridade**. O case público da University of Oregon em Smartabase menciona explicitamente turnover frequente de staff e a necessidade de processos robustos em plataforma unificada; Bridge também fala em abordagem multidisciplinar com vários praticantes no programa do atleta. Isso é decisivo para retenção institucional: não basta o treinador gostar; o sistema precisa continuar útil quando a equipe técnica muda. ([Smartabase Perform](https://perform.smartabase.com/hubfs/download/University_Oregon_SB_Success_Story.pdf?utm_source=chatgpt.com))
Agora, indo para a parte mais importante: o que, somado ao que você já citou, colocaria o HB Track no nível mais alto do mercado geral.

Eu não afirmaria “Top 1” como promessa. Isso seria marketing, não engenharia. Mas eu consigo dizer o que colocaria o HB Track em **classe superior** aos produtos atuais, porque aqui existe uma lacuna real no mercado: muitos sistemas são fortes em uma parte do ciclo, poucos fecham o ciclo inteiro de forma elegante para o treinador.

A decisão-mãe seria esta: o HB Track não deve ter `training_session` como centro semântico principal. O centro deveria ser algo como **`training_intervention_cycle`**:
`need_detected -> objective -> prescription -> delivery -> execution -> response -> review -> adjustment`.
Isso é uma inferência arquitetural minha, mas é diretamente suportada pelo padrão de mercado: XPS junta planejamento+monitoramento+feedback; Smartabase trabalha profiling/loading/monitoring; Kitman junta status, training, participation e alertas; TeamBuildr/Bridge juntam builder, entrega e execução. ([Sideline Sports](https://www.xpsnetwork.com/?utm_source=chatgpt.com))
As decisões de produto que eu adicionaria ao HB Track são estas.

**1. Tornar o módulo orientado a decisão, não a cadastro.**  
Toda sessão precisa nascer de uma `need_detected`, `goal_gap` ou `competitive_focus`, nunca de um formulário vazio. O sistema deve perguntar “qual necessidade isso resolve?” antes de “qual é a duração?”. Isso conecta analytics ao treino sem automatizar o treinador. Esse é exatamente o espaço que os players maduros ocupam parcialmente, mas raramente formalizam no modelo. ([Teamworks](https://www.smartabase.com/?utm_source=chatgpt.com))
**2. Criar dois loops explícitos no domínio: coletivo e individual.**  
Você já percebeu isso antes, mas aqui vale formalizar: um loop de equipe (`team_training_cycle`) e um loop individual (`individual_development_cycle`). O mercado maduro opera os dois, mas muitos sistemas deixam isso implícito. Teamworks/Smartabase enfatiza IDPs; XPS e Sportlyzer mostram o lado coletivo de calendário, RSVPs, attendance e organização. ([Teamworks](https://www.smartabase.com/?utm_source=chatgpt.com))
**3. Fazer vídeo e playbook serem objetos operacionais, não anexos.**  
No HB Track, `video_clip`, `diagram`, `playbook_pattern` e `coaching_cue` precisam ser vinculáveis a `objective`, `session_block`, `exercise_variant`, `error_pattern` e `feedback_thread`. XPS mostra que tática, diagramas, animações e análise funcionam quando fazem parte do fluxo técnico; TeamBuildr mostra vídeo coaching no fluxo do treino. ([Sideline Sports](https://www.xpsnetwork.com/?utm_source=chatgpt.com))
**4. Transformar feedback conversacional em entidade de coaching, não chatbot genérico.**  
Aqui está uma oportunidade muito forte para o HB Track. O mercado mostra mensagem, feedback, forms e communication, mas não vejo publicamente uma modelagem muito madura de conversa técnica contextual. Então eu criaria `feedback_thread`, `coach_prompt`, `athlete_reflection`, `action_commitment`, `followup_check`, `conversation_outcome` e `tone_profile`. A conversa teria sempre contexto de treino, objetivo, atleta, evidência e próximo passo. Isso evitaria IA decorativa e aumentaria adesão real porque o atleta percebe acompanhamento personalizado. Essa parte é inferência minha baseada na lacuna entre communication/messaging já existentes e coaching contextual mais profundo. ([Sideline Sports](https://www.xpsnetwork.com/?utm_source=chatgpt.com))
**5. Introduzir “fricção adaptativa”.**  
Teamworks Forms mostra conditional logic para reduzir campos e melhorar completion; isso deveria virar princípio sistêmico do HB Track. Se o atleta está apto e o dia é normal, o check-in deve ser curtíssimo. Se houver dor, fadiga, restrição ou baixa prontidão, o sistema abre perguntas extras. Esse padrão reduz abandono porque não trata todo dia como auditoria completa. ([Teamworks](https://teamworks.com/blog/forms-new-features-improve-experience/?utm_source=chatgpt.com))
**6. Tratar adesão como primeira classe do domínio.**  
Não apenas `attendance`, mas `adherence_status`, `miss_reason`, `partial_completion`, `reschedule_window`, `consistency_streak`, `engagement_signal`, `dropout_risk_signal`. TeamBuildr já flerta com streaks, leaderboards e engagement; Sportlyzer mostra attendance, RSVP e histórico. O HB Track poderia conectar isso a intervenção real antes que o atleta “desapareça”. ([blog.teambuildr.com](https://blog.teambuildr.com/how-to-build-a-remote-training-system-for-tactical-athletes?utm_source=chatgpt.com))
**7. Implementar edição viva do treino.**  
Se o treino do dia muda por readiness, dor, lotação, material, viagem ou clima, o sistema precisa suportar `live_session_adjustment`, `alternate_exercise`, `constraint_override`, `load_recalculation` e `coach_rationale`. Bridge é muito explícito nisso. Sem isso, o sistema é abandonado no primeiro choque com a vida real. ([BridgeAthletic](https://www.bridgeathletic.com/tactical?utm_source=chatgpt.com))
**8. Criar continuidade interstaff e memória técnica.**  
`observation_log`, `decision_rationale`, `why_this_plan`, `coach_annotation`, `staff_handoff`, `continuity_snapshot`. O case público de Oregon mostra o problema real de turnover e necessidade de continuidade. O HB Track pode ganhar vantagem enorme se o raciocínio técnico ficar rastreável, e não só os números. ([Smartabase Perform](https://perform.smartabase.com/hubfs/download/University_Oregon_SB_Success_Story.pdf?utm_source=chatgpt.com))
**9. Modelar explicitamente restrições e disponibilidade.**  
`injury_flag`, `return_to_play_guard`, `equipment_constraint`, `travel_context`, `time_budget`, `attendance_confidence`, `availability_status`. Kitman e Smartabase reforçam o valor de unificar performance, medical e participation; Bridge fala em ajustar por injury/equipment/readiness. ([Kitman Labs](https://www.kitmanlabs.com/platform/performance-optimization/?utm_source=chatgpt.com))
**10. Fazer o sistema provar valor em 30 segundos de uso.**  
Essa não é uma entidade, é uma regra de produto. Ao abrir o módulo, treinador e atleta devem ver “o que fazer agora”, “o que mudou”, “quem precisa de atenção”, “qual sessão exige ajuste”, “qual objetivo está atrasado”. Kitman Coach App enfatiza status, alertas e comunicação para decisão diária; isso aponta diretamente para um design de home operacional, não administrativa. ([Kitman Labs](https://www.kitmanlabs.com/platform/performance-optimization/?utm_source=chatgpt.com))
Se eu tivesse que te devolver a lista canônica ampliada de entidades/objetos/conceitos para um HB Track de classe superior, eu incluiria, além do que já falamos antes:

`training_intervention_cycle`  
`need_detected`  
`evidence_source`  
`competitive_focus`  
`objective_gap`  
`team_training_cycle`  
`individual_development_cycle`  
`prescription_template`  
`session_variant`  
`live_session_adjustment`  
`constraint_override`  
`alternate_exercise`  
`load_recalculation`  
`adherence_status`  
`consistency_streak`  
`engagement_signal`  
`dropout_risk_signal`  
`feedback_thread`  
`coach_prompt`  
`athlete_reflection`  
`action_commitment`  
`followup_check`  
`conversation_outcome`  
`observation_log`  
`decision_rationale`  
`staff_handoff`  
`continuity_snapshot`  
`error_pattern`  
`coaching_cue`  
`video_clip_link`  
`diagram_link`  
`playbook_pattern`  
`goal_progress_snapshot`  
`availability_status`  
`attendance_confidence`  
`restriction_profile`  
`return_to_play_guard`  
`notification_intent`  
`attention_queue`

Os conceitos de topo que eu congelaria no contrato são:

`planned_vs_actual`  
`team_vs_individual`  
`need_vs_objective`  
`objective_vs_outcome`  
`coach_authority_over_ai`  
`low_friction_capture`  
`contextual_feedback`  
`continuous_adjustment`  
`multidisciplinary_visibility`  
`decision_traceability`  
`adherence_as_signal`  
`conversation_as_intervention`

A peça mais importante de todas, e a que o mercado ainda não resolveu tão bem, é esta: **o sistema precisa transformar dado em intervenção sem tirar a autoria do treinador**. Se o HB Track conseguir fazer isso melhor que os outros — com menos fricção, mais contexto, mais rastreabilidade e melhor experiência diária — aí sim ele entra em território de topo de categoria.

Em uma frase: os produtos maduros prendem o usuário quando viram rotina; o HB Track pode ultrapassá-los se virar também **memória técnica + motor de intervenção + camada conversacional contextual**.

O próximo passo lógico é eu montar para você uma **matriz canônica “anti-abandono” do módulo Training** com quatro blocos:
`decisão de produto -> problema real que evita -> entidade/objeto obrigatório -> regra contratual para o agente não alucinar`.

---

Agora o foco muda de “o que existe dentro de `Training`” para “quais boundaries o módulo precisa respeitar”. Nos sistemas maduros, abandono e retrabalho também acontecem quando `Training` tenta virar dono de tudo; estou validando quais integrações aparecem com mais frequência para separar núcleo, adjacências e módulos transversais.

Nos sistemas maduros, `Training` quase nunca vive sozinho. Ele costuma ficar no centro de uma malha de módulos funcionais e transversais. O erro comum de arquitetura é deixar `Training` absorver responsabilidades que deveriam estar em outros domínios. O desenho mais robusto é: `Training` é o orquestrador da intervenção de treino, mas depende de contexto vindo de outros módulos e devolve eventos/sinais para eles.

Os módulos que mais frequentemente tocam `Training` são estes.

Primeiro, **Teams / Roster / Squad Management**. O módulo de treino precisa saber quem pertence ao time, grupo, categoria, staff e subgrupo do dia. Sem isso, não existe escopo de sessão, convocação, attendance, disponibilidade ou prescrição coletiva/individual. Produtos como Teamworks e Sportlyzer reforçam scheduling, staff/athlete sync e organização por equipe como base operacional do fluxo. ([Teamworks](https://teamworks.com/?utm_source=chatgpt.com))
Segundo, **Calendar / Scheduling / Operations**. Em mercado maduro, treino está acoplado a calendário, agenda, RSVP, logística e rotina diária. XPS se posiciona fortemente em organization & planning; Sportlyzer e Teamworks também convergem em scheduling e coordination. Para o HB Track, isso significa que `Training` não deve ser dono do calendário global, mas precisa integrar profundamente com ele. ([Sideline Sports](https://www.xpsnetwork.com/?utm_source=chatgpt.com))
Terceiro, **Analytics / Performance / Athlete Monitoring**. Esse é um boundary crítico. Os sistemas maduros conectam treino com readiness, wellness, training load, tracking de progresso e sinais de performance; eles não deixam o módulo de treino operar no escuro. XPS explicita readiness, wellness e training load; TeamBuildr fala em readiness, progress, recovery e athlete engagement; Kitman e Smartabase trabalham com visão unificada de performance. ([Sideline Sports](https://www.xpsnetwork.com/?utm_source=chatgpt.com))
Quarto, **Medical / Performance Medicine / Return to Play**. Em produto esportivo sério, `Training` precisa receber restrições, status clínico, dor, lesão, doença, retorno progressivo e guards de liberação. Kitman Labs é particularmente explícito em unir dados médicos e de performance para decisões de availability, workload e return to play. Isso implica que `Training` não deveria guardar prontuário médico completo, mas precisa consumir um `restriction_profile` e emitir/receber sinais de `return_to_play_guard`. ([Kitman Labs](https://www.kitmanlabs.com/blog/injury-management-software/?utm_source=chatgpt.com))
Quinto, **Exercises / Drill Library / Practice Design / Playbook**. Parte dos sistemas separa a biblioteca e o design técnico do treino do calendário/sessão. XPS trata playbook, diagramas, animações e análise como capacidade própria; Bridge enfatiza extensa exercise library, templates e customização; TeamBuildr Practice trabalha com drills, videos e session notes. Para o HB Track, isso sugere um boundary claro entre `Training` e um módulo ou subdomínio de `Exercises/Playbook`. ([Sideline Sports](https://www.xpsnetwork.com/?utm_source=chatgpt.com))
Sexto, **Communication / Messaging / Athlete App**. O mercado maduro mostra que treino persistente exige comunicação embutida: instruções, mensagens, feedback, journals, forms e feed do time. XPS destaca manter comunicação em um só lugar; TeamBuildr expõe app, private messaging, team feed, questionnaires e athlete journals; Kitman ressalta comunicação em tempo real. Isso significa que `Training` gera intenções de comunicação, mas provavelmente não deve ser o dono da infraestrutura de mensageria. ([Sideline Sports](https://www.xpsnetwork.com/?utm_source=chatgpt.com))
Sétimo, **Matches / Competition / Scouting / Video Analysis**. O treino em sistemas maduros frequentemente nasce de necessidade competitiva: análise de jogo, tendência do adversário, erro recorrente, meta tática. XPS liga tática, análise de jogo e treino; vários vendors trabalham a ponte entre performance data e coaching decisions. Então `Training` deveria receber `need_detected`, `error_pattern` e `competitive_focus` de módulos como `matches`, `scout` e `analytics`. ([Sideline Sports](https://www.xpsnetwork.com/?utm_source=chatgpt.com))
Oitavo, **Testing / Assessments**. Em ambientes maduros, treino conversa com testes físicos, técnicos e monitoramento recorrente. TeamBuildr diferencia explicitamente `testing` de `monitoring`, ambos úteis para informar ajuste de treino. No HB Track, isso pode ser um subdomínio de `analytics/performance` ou um módulo próprio, dependendo do nível de sofisticação. ([blog.teambuildr.com](https://blog.teambuildr.com/testing-vs.-monitoring-a-guide-to-practical-sport-science-assessments?utm_source=chatgpt.com))
Nono, **Identity & Access**. Em sistemas reais, o treino é multiator: treinador principal, assistente, preparador físico, fisioterapeuta, atleta, admin, analista. Teamworks AMS documenta papéis e permissões, inclusive gestão de integrações. No HB Track, isso reforça sua decisão anterior de manter `identity_access` como módulo transversal formal, não embutido em `Training`. ([help.teamworks.com](https://help.teamworks.com/ams/s/article/roles?utm_source=chatgpt.com))
Décimo, **Notifications**. O treino gera muitos gatilhos: sessão alterada, check-in pendente, restrição crítica, feedback novo, vídeo anexado, objetivo revisado. Os vendors maduros não tratam isso como detalhe; comunicação e alertas são parte da utilidade diária. Para o HB Track, `notifications` deve ser transversal, com eventos disparados por `Training`. ([Teamworks](https://teamworks.com/?utm_source=chatgpt.com))
Décimo primeiro, **Audit / Compliance / Decision Traceability**. Quanto mais o módulo interfere em carga, disponibilidade, dor, restrição e retorno, mais importante fica a trilha de decisão. Kitman destaca secure, auditable record e workflows; TeamBuildr também enfatiza segurança e MFA; Teamworks trabalha estrutura de roles. No seu caso, faz sentido total `audit` ser módulo transversal formal com contrato próprio. ([Kitman Labs](https://www.kitmanlabs.com/blog/injury-management-software/?utm_source=chatgpt.com))
Décimo segundo, **Integrations / External Data Connectors**. Sistemas maduros puxam dados de wearables, GPS, hardware de força, vídeo, formulários, EMR/medical systems e outras fontes. Bridge fala em data integration and analytics; Kitman explicita API e integrações; Teamworks AMS inclui módulo de integrações. Então o HB Track deveria tratar integrações como boundary formal, não como scripts ad hoc pendurados em `Training`. ([BridgeAthletic](https://www.bridgeathletic.com/tactical?utm_source=chatgpt.com))
Se eu traduzir isso para uma visão canônica de arquitetura para o HB Track, o mapa mais sólido fica assim:

`teams` toca `training` para escopo humano e organizacional.  
`seasons` toca `training` para contexto competitivo e periodização.  
`competitions` e `matches` tocam `training` para calendário competitivo e foco da intervenção.  
`scout` e `analytics` tocam `training` para gerar necessidade, evidência e recomendação.  
`exercises` toca `training` como biblioteca/base de prescrição.  
`wellness` e `medical` tocam `training` para restrições, readiness e safeguards.  
`reports` consome saídas de `training`, não deveria governá-lo.  
`identity_access`, `audit` e `notifications` são transversais formais.  
`ai_ingestion` não deveria criar sessão diretamente; deveria alimentar `need_detected`, `recommendation` ou enriquecimento contextual.

As integrações externas mais comuns que aparecem nesse tipo de ecossistema são relativamente previsíveis.

Há integrações com **wearables e tracking**: GPS, heart rate, workload, readiness devices e plataformas de monitoramento.  
Há integrações com **vídeo e mídia**: clips, playlists, análise e anexos instrucionais.  
Há integrações com **hardware de força/performance**: jump mats, bar velocity, force plates, dynamometers e sistemas de teste.  
Há integrações com **health/medical systems**: registros clínicos, imaging, rehab status e documentação de retorno.  
Há integrações com **mensageria e calendários**: push, e-mail, agenda, RSVP, reminders.  
Há integrações com **identity/SSO**: autenticação, grupos e permissões corporativas.  
Há integrações com **BI/export/reporting**: dashboards executivos, warehouse e análise longitudinal.  
Esses padrões aparecem nos vendors que enfatizam integrações, forms, analytics e connected ecosystems. ([BridgeAthletic](https://www.bridgeathletic.com/tactical?utm_source=chatgpt.com))
A parte mais importante, do ponto de vista contract-driven, é decidir o que `Training` deve possuir e o que ele deve apenas referenciar.

Minha recomendação objetiva para o HB Track é:

`Training` deve possuir:
`training_intervention_cycle`, `training_session`, `session_block`, `session_objective`, `prescription`, `execution`, `session_adjustment`, `coach_note`, `athlete_feedback`, `attention_queue`, `decision_rationale`.

`Training` deve referenciar, mas não ser dono de:
`athlete`, `team`, `season`, `competition`, `match`, `scout_signal`, `analytics_signal`, `medical_restriction`, `wellness_state`, `identity_role`, `notification_delivery`, `audit_record`, `external_sensor_measurement`.

Essa separação reduz acoplamento e evita que o módulo vire um “supermódulo” impossível de governar.

A pergunta não feita mais importante aqui é: **qual integração deve ser síncrona e qual deve ser orientada a evento?** Porque isso muda o contrato. Minha resposta inicial seria:

Síncrono, para leitura operacional imediata:
roster, availability atual, restriction status, session agenda, exercise lookup, permissions.

Orientado a evento, para desacoplamento:
session_created, session_updated, attendance_recorded, readiness_submitted, restriction_changed, feedback_posted, session_completed, alert_raised, recommendation_generated.

Se você quiser, o próximo passo mais útil é eu montar uma **matriz canônica de boundaries do módulo `Training`** no formato:
`módulo externo -> por que toca Training -> dados que fornece -> dados que consome -> ownership -> integração síncrona/evento -> risco de acoplamento indevido`.

---
Vou organizar os fluxos em dois grupos: fluxos de negócio do usuário e fluxos sistêmicos/orquestrais. Isso é o que normalmente falta antes de virar contrato, porque sem fluxo o agente cai em CRUD e perde o comportamento real do módulo.

Perfeito. Para o módulo `Training`, os fluxos principais não devem ser listados como telas soltas nem como endpoints soltos. Eles devem representar o comportamento operacional real do treinador, do atleta e do sistema.

A melhor forma de organizar é em três camadas:
fluxos do treinador e staff,
fluxos do atleta,
fluxos automáticos do sistema.

O padrão dos sistemas maduros sustenta exatamente isso: planejamento, comunicação, readiness/wellness, execução, feedback, ajuste e integração com performance/medical/analytics aparecem como fluxo contínuo, não como ações isoladas. 

Fluxos principais do treinador e staff

1. Detectar necessidade de treino  
O fluxo começa quando o treinador ou staff identifica uma necessidade: problema estatístico, objetivo competitivo, deficiência técnica, retorno de jogo, limitação física, meta individual ou foco do microciclo. Em sistemas maduros, treino nasce de contexto de performance, monitoramento e coaching, não de formulário vazio. 

2. Converter necessidade em objetivo técnico  
O treinador transforma a necessidade em objetivo de treino. Exemplo: “melhorar tomada de decisão no 2x2”, “reduzir erro de finalização sob fadiga”, “controlar carga de retorno progressivo”. Esse fluxo gera `need_detected -> objective -> success_criteria`.

3. Planejar ciclo e posicionar a sessão  
O treinador encaixa a intervenção no ciclo real:
temporada, fase, microciclo, dia, contexto competitivo, disponibilidade do elenco.  
Esse fluxo define se a sessão é coletiva, individual, regenerativa, técnico-tática, física, híbrida, pré-jogo, pós-jogo ou retorno progressivo.

4. Criar sessão ou intervenção  
O treinador cria a sessão com objetivo, duração, bloco, grupo-alvo, staff responsável, local, materiais e tags operacionais. Aqui nasce a `training_session` ou `training_intervention_cycle`.

5. Montar os blocos da sessão  
O treinador estrutura aquecimento, bloco principal, bloco situacional, bloco de finalização, recuperação, etc. Cada bloco tem objetivo, duração, intensidade esperada, exercício/tarefa, coaching cues e critério de sucesso.

6. Selecionar exercícios, tarefas, vídeos e playbooks  
O treinador usa a biblioteca de exercícios e associa vídeos, diagramas, padrões táticos, correções e referências. Nos produtos maduros, esse conteúdo é parte do fluxo de prescrição e instrução. 

7. Adaptar por grupo ou atleta  
O staff cria variantes por posição, idade, estado físico, restrição médica, nível técnico ou meta individual. Esse é um fluxo central em sistemas maduros de prescrição e monitoring. 

8. Publicar e comunicar a sessão  
Depois da montagem, a sessão é publicada para atletas e staff. O sistema envia agenda, instruções, anexos, local, horário, materiais e pedidos prévios como check-in ou questionário.

9. Revisar prontidão antes da execução  
Antes do treino, o treinador ou staff visualiza disponibilidade, wellness, dor, RPE prévio, restrições e alertas. Isso muda o plano do dia e é um dos núcleos dos sistemas maduros. 

10. Ajustar a sessão ao vivo  
Durante a execução, o treinador altera carga, exercício, ordem, duração, grupo ou variante por motivo real: atraso, material, clima, fadiga, dor, lotação, presença. Esse fluxo é decisivo para aderência ao mundo real.

11. Registrar execução e ocorrências  
Após ou durante o treino, staff registra presença, execução real, observações, desvios, resposta do grupo, desempenho relevante, incidentes e decisões técnicas.

12. Produzir feedback técnico  
O treinador envia feedback individual ou coletivo, associa vídeo/clipe, coaching cue, orientação para próxima sessão e follow-up.

13. Revisar resultado e ajustar o ciclo  
O staff compara objetivo planejado vs resposta observada e decide manter, escalar, reduzir, corrigir ou encerrar a intervenção. Esse é o fechamento do loop operacional.

Fluxos principais do atleta

1. Receber agenda e plano do dia  
O atleta vê o treino programado, horário, objetivo, instruções, mídia e expectativas.

2. Confirmar presença/disponibilidade  
Ele informa presença, atraso, ausência ou indisponibilidade.

3. Responder check-in pré-treino  
O atleta envia readiness, wellness, dor, fadiga, sono, humor ou restrição do dia. Esse é um fluxo recorrente nos sistemas maduros. 

4. Consumir instrução do treino  
O atleta vê exercícios, vídeos, playbook, coaching points e critérios de execução.

5. Executar o treino  
Pode registrar conclusão, carga percebida, observações, dificuldades, variações executadas ou impossibilidade de cumprir parte da sessão.

6. Receber e responder feedback  
O atleta recebe feedback técnico, responde reflexão, assume compromisso de ajuste e acompanha próximo passo.

7. Consultar evolução  
O atleta acompanha histórico, aderência, progresso de meta, consistência, feedbacks e comparativos.

Fluxos principais do sistema

1. Sugerir necessidade ou atenção  
O sistema consolida sinais de analytics, wellness, medical, scout, attendance ou carga e gera `need_detected`, `alert`, `recommendation` ou `attention_queue`, sem tirar a decisão do treinador.

2. Validar guards e restrições  
Ao criar ou ajustar sessão, o sistema verifica conflitos:
restrição médica, retorno progressivo, excesso de carga, atleta indisponível, conflito de agenda, falta de permissão.

3. Resolver escopo e elegibilidade  
O sistema determina quais atletas, grupos e staff são afetados pela sessão, variante ou ajuste.

4. Disparar notificações  
Ao publicar, alterar ou cancelar sessão, ou quando surge novo feedback/alerta, o sistema dispara notificações apropriadas.

5. Registrar trilha de decisão  
Mudanças em objetivo, sessão, carga, restrição, justificativa e feedback geram eventos de auditoria.

6. Consolidar planned vs actual  
O sistema compara o que foi prescrito com o que foi realizado e materializa diferenças para análise futura.

7. Atualizar sinais derivados  
Após check-ins, execução e feedback, o sistema recalcula prontidão, aderência, risco de abandono, consistência ou fila de atenção.

8. Sincronizar módulos externos  
O sistema consome ou publica informações para `analytics`, `wellness`, `medical`, `notifications`, `audit`, `matches`, `scout`, `reports`.

9. Encerrar ciclo da intervenção  
Quando há evidência suficiente, o sistema fecha a intervenção ou a mantém aberta para reavaliação, sempre preservando rastreabilidade.

Se eu condensar isso no formato mais útil para contrato, os fluxos canônicos do módulo `Training` são estes:

`Need identified -> Objective defined -> Session/intervention planned -> Content assigned -> Readiness checked -> Session delivered -> Execution recorded -> Feedback produced -> Outcome reviewed -> Plan adjusted`

`Athlete notified -> Availability confirmed -> Check-in submitted -> Session consumed -> Completion/response submitted -> Feedback received -> Follow-up tracked`

`Signals ingested -> Guards validated -> Notifications emitted -> Audit recorded -> Derived states recalculated -> Cross-module sync performed`

A pergunta que você não fez, mas deveria fazer agora, é: quais desses fluxos são obrigatórios no MVP contratual e quais são evolução posterior. Porque, se você tentar contratar tudo de uma vez, o agente vai supermodelar.

Minha recomendação objetiva de prioridade é:

Fase 1:
detectar necessidade, definir objetivo, criar sessão, montar blocos, publicar, confirmar presença, check-in pré-treino, registrar execução, feedback, ajuste.

Fase 2:
vídeo/playbook contextual, variantes por atleta, attention queue, guards de retorno progressivo, planned vs actual forte.

Fase 3:
feedback conversacional estruturado, risco de abandono, recomendações automáticas, continuidade interstaff.

O próximo passo lógico é eu transformar isso em uma tabela canônica:
`fluxo -> ator principal -> gatilho -> pré-condições -> entidades tocadas -> eventos emitidos -> pós-condições -> invariantes obrigatórias`.

---
--

Para esse módulo, as invariantes obrigatórias não são “boas práticas genéricas”. Elas são as regras de verdade que impedem o `Training` de degradar para agenda/CRUD e preservam a lógica que você definiu:

`Need -> Objective -> Prescription -> Session -> Execution -> Response -> Review -> Adjustment`

Se essa cadeia é o valor real do módulo, então as invariantes obrigatórias são as que impedem:
1. sessão sem propósito,
2. execução sem contexto,
3. ajuste sem evidência,
4. integração sem boundary,
5. automação que usurpa a decisão do treinador.

Abaixo eu separo em invariantes nucleares, operacionais, de integridade, de boundary e de governança.

### 1. Invariantes nucleares do domínio
Essas são as mais importantes. Sem elas, o módulo perde identidade.

**INV-TRAIN-001 — Nenhuma sessão nasce sem objetivo operacional**
Toda `training_session` deve possuir pelo menos um `session_objective` válido e explícito.  
Não pode existir sessão “vazia” ou “apenas calendário”.

**INV-TRAIN-002 — Todo objetivo deve estar ligado a uma necessidade rastreável**
Todo `session_objective` deve referenciar uma `need_detected`, `competitive_focus`, `development_goal` ou `manual_coach_rationale`.  
Objetivo sem origem vira arbitrariedade.

**INV-TRAIN-003 — Necessidade não cria sessão automaticamente**
`need_detected` ou `recommendation` jamais pode materializar `training_session` de forma autônoma.  
A criação/publicação da sessão exige ato explícito de treinador autorizado.

**INV-TRAIN-004 — IA e estatística só recomendam; treinador decide**
Qualquer saída de `analytics`, `ai_ingestion` ou regras automáticas entra como `recommendation` ou `signal`, nunca como decisão final de prescrição.

**INV-TRAIN-005 — Sessão publicada deve possuir conteúdo mínimo treinável**
Uma sessão só pode ser `PUBLISHED`/`SCHEDULED` se tiver:
- escopo (`team_scope` e/ou `athlete_scope`)
- objetivo
- horário/data
- pelo menos um bloco ou prescrição mínima
- responsável técnico

Sem isso, ela é apenas `DRAFT`.

**INV-TRAIN-006 — Toda execução deve referenciar uma prescrição ou justificativa de improviso controlado**
`execution_record` não pode existir solto.  
Ele deve apontar para uma `training_session`/`session_block`/`prescription_line`, ou carregar `coach_rationale` de ajuste ao vivo.

---

### 2. Invariantes de ciclo operacional
Essas protegem a lógica do fluxo real.

**INV-TRAIN-007 — Planned vs Actual é obrigatório para sessão executada**
Toda sessão concluída deve preservar separadamente:
- o que foi planejado
- o que foi executado
- o que foi alterado
- por que foi alterado

Nunca sobrescrever o planejado com o realizado.

**INV-TRAIN-008 — Ajuste ao vivo exige motivo**
Toda `live_session_adjustment`, `constraint_override`, `alternate_exercise` ou `load_recalculation` deve registrar motivo estruturado.

**INV-TRAIN-009 — Sessão concluída exige evidência mínima de resposta**
Uma sessão não deveria fechar como `COMPLETED` sem ao menos um conjunto mínimo de resposta:
- attendance/conclusão
- nota do staff, ou
- resposta do atleta, ou
- carga/RPE/observação equivalente

**INV-TRAIN-010 — Feedback pós-treino é contextual**
Todo `feedback_thread` ou feedback técnico deve referenciar pelo menos um destes:
- sessão
- bloco
- objetivo
- evidência
- atleta/grupo específico

Feedback solto não tem valor operacional.

**INV-TRAIN-011 — Revisão só pode ocorrer após execução ou evidência equivalente**
Não pode haver `review_outcome` sem `execution_record`, `post_session_report` ou evento equivalente.

**INV-TRAIN-012 — Ajuste futuro depende de revisão ou decisão explícita**
Toda mudança relevante de plano futuro deve derivar de:
- revisão documentada, ou
- decisão manual justificada do coach

---

### 3. Invariantes de escopo e ownership
Essas evitam supermódulo e confusão com outros domínios.

**INV-TRAIN-013 — Training não é dono de atleta, equipe, competição ou restrição médica**
O módulo `Training` referencia essas entidades; não as redefine soberanamente.

**INV-TRAIN-014 — Restrição médica consumida por Training é somente leitura operacional**
`Training` pode consumir `restriction_profile`, `return_to_play_guard` e status de aptidão, mas não criar/editar verdade clínica soberana.

**INV-TRAIN-015 — Analytics não altera estado soberano de Training sem comando autorizado**
`analytics` pode sugerir `need_detected` e `recommendation`; não pode alterar sessão, carga ou publicação diretamente.

**INV-TRAIN-016 — Exercises/Playbook fornecem conteúdo; Training governa uso contextual**
Biblioteca de exercícios e playbook não devem carregar sozinhos estado de execução de sessão.  
Esse estado pertence ao `Training`.

---

### 4. Invariantes de status e transição
Essas são críticas para contrato e automação.

**INV-TRAIN-017 — Status de sessão tem transições válidas e fechadas**
Exemplo canônico:
`DRAFT -> SCHEDULED/PUBLISHED -> IN_PROGRESS -> COMPLETED`
com saídas controladas para `CANCELLED` e `ARCHIVED`.

Não pode haver salto arbitrário, como `DRAFT -> COMPLETED`.

**INV-TRAIN-018 — Sessão publicada não pode perder campos mínimos**
Se uma sessão já publicada perder pré-requisitos mínimos, o sistema deve:
- bloquear a alteração, ou
- rebaixar o status para `DRAFT`

**INV-TRAIN-019 — Sessão em progresso não pode ser excluída fisicamente**
Após `IN_PROGRESS`, a política deve ser cancelamento lógico/encerramento com trilha, nunca hard delete simples.

**INV-TRAIN-020 — Sessão concluída é imutável no núcleo histórico**
Após `COMPLETED`, alterações no conteúdo histórico devem ocorrer por correção auditada/versionada, não edição destrutiva.

---

### 5. Invariantes de elegibilidade e segurança operacional
Essas evitam decisões erradas no dia a dia.

**INV-TRAIN-021 — Atleta inelegível não pode receber prescrição executável sem override explícito**
Se houver bloqueio por restrição, indisponibilidade severa ou guarda de retorno, o sistema deve barrar ou exigir override autorizado e auditado.

**INV-TRAIN-022 — Variante individual deve respeitar escopo e permissão**
Um coach não pode criar/adaptar prescrição individual fora de sua autoridade de equipe/categoria/papel.

**INV-TRAIN-023 — Attendance e execution não podem referenciar atleta fora do escopo da sessão**
Evita dados órfãos e execução em elenco errado.

**INV-TRAIN-024 — Sobreposição crítica de agenda deve ser detectável**
Se atleta ou grupo possuir conflito operacional relevante, isso deve ser sinalizado antes da publicação ou execução.

---

### 6. Invariantes de aderência e experiência real
Essas são as que mais protegem a utilidade real do produto.

**INV-TRAIN-025 — Toda interação pedida ao atleta deve ter propósito operacional**
Questionário, check-in, feedback ou confirmação não pode existir sem uso downstream claro.  
Sem isso, o sistema vira coleta vazia e aumenta abandono.

**INV-TRAIN-026 — Fricção adaptativa é obrigatória**
Se o estado do atleta estiver normal, o fluxo de check-in deve ser mínimo.  
Se houver risco/restrição/dor/anomalia, o sistema pode expandir perguntas e validações.

**INV-TRAIN-027 — Atenção do treinador deve ser finita e priorizada**
O módulo não pode gerar filas/alertas sem severidade, motivo e entidade-alvo.  
Tudo que entra em `attention_queue` precisa ter racional explícito.

**INV-TRAIN-028 — Conversa é intervenção, não chat genérico**
Toda conversa técnica relevante deve produzir um de:
- reflexão
- compromisso
- pendência
- follow-up
- decisão

Se não gera consequência operacional, não pertence ao núcleo do módulo.

---

### 7. Invariantes de rastreabilidade e auditoria
Essas sustentam determinismo e continuidade interstaff.

**INV-TRAIN-029 — Toda decisão relevante deve ser rastreável**
Mudanças em objetivo, publicação, ajuste, override, restrição aplicada, cancelamento e feedback crítico devem gerar trilha de auditoria.

**INV-TRAIN-030 — Justificativa humana deve sobreviver à troca de staff**
Elementos como `decision_rationale`, `coach_note`, `staff_handoff` e `continuity_snapshot` não podem ser descartáveis.

**INV-TRAIN-031 — Evidência de origem deve ser preservada**
Se uma necessidade veio de scout, analytics, wellness, match ou observação manual, a origem deve permanecer vinculada.

---

### 8. Invariantes de dados e integridade estrutural
Essas são mais “compilador” do contrato.

**INV-TRAIN-032 — IDs e referências cruzadas devem ser válidos no momento da transação**
Nada de criar execução para sessão inexistente, feedback para atleta fora do escopo etc.

**INV-TRAIN-033 — Objetivo e tipo de sessão devem ser semanticamente compatíveis**
Exemplo: um fluxo de retorno progressivo não pode ser classificado como sessão competitiva plena sem justificativa/override.

**INV-TRAIN-034 — Blocos não podem violar a duração total sem regra explícita**
Soma dos blocos deve ser coerente com a duração planejada, salvo política de tolerância documentada.

**INV-TRAIN-035 — Uma sessão não pode existir simultaneamente como coletiva e individual sem modelo explícito**
Se suportar híbrido, isso precisa estar formalizado; não pode ser ambíguo.

**INV-TRAIN-036 — Estados derivados não substituem dados fonte**
`readiness_score`, `dropout_risk_signal`, `engagement_signal` e similares são derivados; nunca substituem respostas brutas ou fatos originais.

---

### 9. Invariantes de boundary com seus módulos HB Track
Como seu ecossistema já está mais definido, eu congelaria estes acoplamentos formais:

**INV-TRAIN-037 — `training` consome `wellness` e `medical`, mas não os soberaniza**  
**INV-TRAIN-038 — `training` consome sinais de `analytics` e `scout`, mas mantém autoridade do coach**  
**INV-TRAIN-039 — `training` emite eventos para `notifications`, não entrega notificação diretamente**  
**INV-TRAIN-040 — `training` registra fatos auditáveis via `audit`, não mantém auditoria informal interna**  
**INV-TRAIN-041 — `identity_access` governa permissão; `training` só aplica policy decidida**  

---

### 10. Conjunto mínimo realmente obrigatório
Se você quiser o núcleo duro, o mínimo que eu trataria como inegociável é:

- sessão exige objetivo
- objetivo exige origem rastreável
- recomendação não vira sessão automaticamente
- sessão publicada exige conteúdo mínimo
- execução preserva planned vs actual
- ajuste exige motivo
- restrição crítica bloqueia ou exige override auditado
- feedback é contextual
- revisão exige evidência
- decisões relevantes geram trilha
- `training` não soberaniza `medical`, `analytics`, `identity_access`, `notifications`, `audit`

A pergunta não feita, mas necessária, é esta:
**qual dessas invariantes é de negócio puro, qual é de contrato API, qual é de banco, qual é de serviço/aplicação e qual é de gate de auditoria?**
Porque, se você não separar isso agora, vai tentar enfiar tudo em OpenAPI e vai falhar.
A separação correta seria:

- **Invariante de negócio**: regra semântica do domínio
- **Invariante de contrato**: campos/estados/transições obrigatórias expostas na API
- **Invariante de persistência**: uniqueness, FK, status allowed, soft delete, versioning
- **Invariante de aplicação**: guards, autorização contextual, transições
- **Invariante de auditoria/gate**: verificações automatizadas de conformidade

Se você concordar com essa lógica, o próximo passo certo não é escrever endpoint.  
O próximo passo certo é eu te entregar uma matriz canônica assim:

`ID -> nome -> regra -> tipo (business/api/db/app/gate) -> severidade -> evidência esperada -> módulo boundary -> automatizável?`

Essa matriz já sai pronta para virar:
- invariants registry
- checklist de contrato
- base de testes
- gates automatizados

Baseado na lógica de domínio que você consolidou para o HB Track nesta conversa, preservando:
- autoridade do treinador sobre recomendação automática
- cadeia `Need -> Objective -> Prescription -> Session -> Execution -> Response -> Review -> Adjustment`
- boundary formal com `analytics`, `wellness`, `medical`, `identity_access`, `audit` e `notifications`  
- objetivo de evitar que `Training` degrade para CRUD ou agenda.

# MATRIZ CANÔNICA DO MÓDULO TRAINING DO HB TRACK

- Crie aqui a matriz completa do módulo `Training` do HB Track, para funcionamento no mundo real, com base em tudo que foi discutido acima.

Uma matriz canônica e determinística do módulo `Training` é, na prática, uma **tabela soberana de decisões compiláveis**. Ela não serve para “explicar o módulo”; serve para **impedir que agente, dev ou gerador inventem comportamento**.

O erro mais comum é criar uma matriz bonita, mas narrativa. A matriz certa precisa funcionar como ponte entre:
decisão de negócio,
contrato,
boundary,
invariante,
e evidência de validação.

A pergunta que você não fez, mas deveria fazer antes de montar a matriz, é:
**“qual decisão essa matriz precisa travar?”**
Porque existem pelo menos quatro matrizes diferentes possíveis:
uma para arquitetura,
uma para contrato API,
uma para boundary/integração,
e uma para invariantes/gates.

Para o HB Track, eu faria uma **matriz canônica mestre do módulo `Training`** e, dela, derivaria submatrizes menores. A matriz mestre deveria ter cada linha como uma decisão operacional real do domínio.

A estrutura mais útil é esta:

`decision_id | capability | problema real | unidade operacional | entidade soberana | campos mínimos | origem permitida | origem proibida | regras/invariantes | boundary_owner | ação permitida | ação proibida | evento emitido | evidência esperada | gate automatizável`

Esse formato funciona porque obriga cada decisão a ficar amarrada ao resto do sistema.

Exemplo de lógica:
se a linha fala de “publicar sessão”, ela já precisa dizer:
qual entidade é tocada,
quais campos mínimos existem,
qual invariante bloqueia publicação inválida,
quem decide,
qual módulo é dono de cada verdade externa,
qual evento sai,
e qual evidência valida a implementação.

Sem isso, a matriz ainda deixa espaço para discricionariedade.

O processo para criar essa matriz de forma determinística é este.

Primeiro, você define o **eixo soberano do módulo**.
No seu caso, não é `training_session`. É:

`need -> objective -> prescription -> session -> execution -> response -> review -> adjustment`

Esse fluxo é o backbone. Toda linha da matriz deve cair em um desses estágios. Se alguma linha não encaixa, ou ela é ruído, ou pertence a outro módulo.

Depois, você separa as linhas por tipo de decisão. Para `Training`, eu usaria 6 blocos:

1. decisões de identidade do módulo
2. decisões de fluxo operacional
3. decisões de entidade e ownership
4. decisões de boundary/integração
5. decisões de estado/transição
6. decisões de invariantes e gates

A matriz não deve começar por “entidades”. Deve começar por **decisões irredutíveis do domínio**. Exemplos:

* sessão exige objetivo
* objetivo exige origem
* recommendation não cria sessão
* sessão publicada exige conteúdo mínimo
* execution preserva planned vs actual
* ajuste exige motivo
* feedback é contextual
* training consome medical, não soberaniza medical
* analytics recomenda, não decide
* notification é intent, não entrega direta

Cada uma dessas decisões vira uma linha.

Aí você transforma cada linha em formato compilável. Exemplo de uma linha real:

`TRAIN-DEC-001 | sessão publicada exige conteúdo mínimo | impedir agenda vazia | training_session | training_session | objective_ids, scope, responsible_staff_ref, scheduled_start_at, scheduled_end_at, minimally_trainable_content | coach/manual_authorized_action | analytics/ai direct creation | INV-TRAIN-001, INV-TRAIN-005, INV-TRAIN-018 | training owns session / identity_access owns permission | publish_session | auto_publish | training_session_published | teste de transição + payload válido + auditoria | yes`

Repare no ponto central:
a linha já diz o que pode e o que não pode.
Isso é o que faz a matriz ser determinística.

A segunda regra crítica é: **cada coluna deve ter semântica única**.

Por exemplo:

* `boundary_owner` só responde “quem é o dono soberano da verdade”
* `origem permitida` só responde “de onde essa decisão pode nascer”
* `ação proibida` só responde “qual comportamento deve ser barrado”
* `evidência esperada` só responde “como provar que a decisão foi implementada”

Se você misturar explicação com governança na mesma coluna, a matriz perde poder de gate.

A terceira regra é: **não use texto aberto onde deveria haver enum controlado**.

Por exemplo:

* `decision_stage`: `need | objective | prescription | session | execution | response | review | adjustment`
* `decision_type`: `business | boundary | lifecycle | authorization | integrity | audit`
* `gate_class`: `blocking | warning | documentation_only`
* `automation_level`: `fully_automatable | partially_automatable | manual_review_required`

Se deixar isso em linguagem livre, o agente volta a interpretar.

A quarta regra é: **cada linha deve apontar para artefatos físicos**.
Uma matriz boa não vive sozinha; ela aponta para onde a decisão se materializa.

Você precisa de colunas como:

`materializes_in_api`
`materializes_in_schema`
`materializes_in_state_model`
`materializes_in_test`
`materializes_in_gate`

Assim você força a rastreabilidade da decisão até os arquivos reais.

Para o HB Track, eu sugeriria esta versão canônica mínima de colunas:

`decision_id`
`decision_stage`
`decision_name`
`problem_real_world`
`operational_value_unit`
`entity_owner`
`entities_touched`
`minimum_required_fields`
`allowed_origin`
`forbidden_origin`
`allowed_actor`
`forbidden_actor`
`preconditions`
`postconditions`
`state_impact`
`events_emitted`
`invariants`
`boundary_rules`
`evidence_required`
`gate_class`
`automation_level`
`materializes_in`

Com isso, você já consegue derivar:

* IR
* checklist de contrato
* suite de testes
* gates de conformidade
* matriz de ownership

A quinta regra é a mais importante:
**a matriz precisa separar decisão de implementação**.

Exemplo:
“sessão publicada exige objetivo” é decisão.
“endpoint POST /training-sessions/{id}/publish” é implementação.

Se você misturar os dois, a matriz envelhece rápido e começa a mandar na API em vez de governar o domínio.

O melhor método é construir a matriz em 4 passadas.

Passada 1: decisão pura
Liste de 20 a 40 decisões nucleares do módulo.

Passada 2: binding estrutural
Para cada decisão, preencha entidade, campos mínimos, estado, atores, ownership e evento.

Passada 3: binding de conformidade
Associe invariantes, evidência e gate.

Passada 4: binding de materialização
Associe contrato, schema, teste e projeção.

É assim que ela vira determinística.

Para `Training`, os primeiros blocos da matriz provavelmente seriam:

Bloco 1 — Identidade do módulo
o que o módulo resolve, qual a unidade de valor e o que ele não é.

Bloco 2 — Núcleo operacional
need, objective, prescription, session, execution, response, review, adjustment.

Bloco 3 — Sessão e execução
publicação, presença, readiness, live adjustment, completion, planned vs actual.

Bloco 4 — Feedback e continuidade
feedback contextual, follow-up, decision rationale, handoff.

Bloco 5 — Boundaries
analytics, scout, wellness, medical, exercises, notifications, audit, identity_access.

Bloco 6 — Governança
status transitions, autorização, soft delete, auditabilidade, derived states.

O que você provavelmente deveria fazer logo depois é **não tentar começar com 100 linhas**.
Comece com 15 a 20 decisões de alta soberania.
Se essas 20 estiverem perfeitas, elas já seguram 80% da discricionariedade.

Uma mini-amostra de linhas canônicas do `Training` seria:

* `TRAIN-DEC-001`: sessão exige objetivo
* `TRAIN-DEC-002`: objetivo exige origem rastreável
* `TRAIN-DEC-003`: analytics/AI não cria sessão
* `TRAIN-DEC-004`: publicação exige conteúdo mínimo
* `TRAIN-DEC-005`: execution exige contexto
* `TRAIN-DEC-006`: planned vs actual é obrigatório
* `TRAIN-DEC-007`: ajuste exige motivo
* `TRAIN-DEC-008`: feedback é contextual
* `TRAIN-DEC-009`: restrição crítica bloqueia ou exige override
* `TRAIN-DEC-010`: training não soberaniza medical
* `TRAIN-DEC-011`: training não soberaniza permissions
* `TRAIN-DEC-012`: notifications são intents
* `TRAIN-DEC-013`: completed é imutável por edição destrutiva
* `TRAIN-DEC-014`: derived signals não substituem fatos-fonte
* `TRAIN-DEC-015`: conversa precisa gerar consequência operacional

Se você quiser uma definição curta:

**matriz canônica determinística = tabela em que cada linha é uma decisão irredutível do domínio, amarrada a ownership, invariantes, atores, estados, eventos, evidência e artefatos de materialização, sem deixar nenhum espaço para o agente inventar shape, origem, permissão ou comportamento.**


# SAÍDA DO MÓDULO TRAINING - PREENCHER O MODULE_DECISION_IR.json

- Preencher o `MODULE_DECISION_IR` com as informações que você consolidou sobre o módulo `Training`, através do texto acima

O segredo é este:

**não escrever o JSON para “explicar o módulo”; escrever o JSON para que nada importante precise ser decidido depois.**

Em outras palavras, o JSON correto não é o mais completo em prosa. É o que **elimina discricionariedade** do agente entre o IR e as superfícies canônicas. Isso é exatamente o que o seu pipeline exige: se faltar artefato crítico, convenção, estado, field, enum, evento, workflow, permissão, erro ou regra explícita, o agente deve bloquear em vez de inferir.

A regra prática mais importante é:

**cada informação do JSON precisa responder a uma destas perguntas:**

* isso gera qual superfície?
* isso preenche qual slot de template?
* isso referencia qual registry canônico?
* isso bloqueia se estiver ausente?

Se a resposta for “não sei”, o campo ainda está em forma de pensamento, não em forma de IR.

O JSON correto nasce quando você aplica sete regras.

**1. Escreva em forma de binding, não em forma de descrição.**
Em vez de dizer “training_session representa uma unidade de treino”, você precisa dizer qual entidade existe, quais campos existem, qual `semantic_type_ref` cada campo usa, quais relações ela tem, se tem lifecycle e qual superfície isso alimenta. O pipeline já separa soberania por superfície e exige contratos técnicos válidos em OpenAPI, JSON Schema, workflows e AsyncAPI; então o IR precisa alimentar essas superfícies sem prosa intermediária.

**2. Todo campo relevante precisa de tipo semântico canônico.**
Nunca use o JSON para deixar implícito se algo é `string`, `uuid`, `timestamp`, `enum`, referência externa ou valor derivado. Para gerar schema de domínio, o boot já exige `DOMAIN_AXIOMS.json`, template de schema e docs do módulo; isso significa que o IR certo aponta para tipo canônico, não para “tipo lógico genérico”.

**3. Toda relação precisa declarar soberania relacional.**
Não basta `from`, `to` e `cardinality`. O JSON correto precisa fechar:

* quem segura a referência,
* se é obrigatória,
* qual a política de delete,
* e se a relação é soberana ou apenas referência de boundary.
  Sem isso, o agente ainda precisa escolher implementação.

**4. Tudo que tem estado precisa vir com lifecycle fechado.**
Se uma entidade tem estado, o JSON precisa declarar:

* `entity_ref`
* estados válidos
* estado inicial
* transições permitidas
* transições proibidas
* guards relevantes
  O pipeline proíbe inventar transições de estado e manda bloquear quando `STATE_MODEL` aplicável estiver ausente. 

**5. Use cases de API precisam ser compiláveis, não narrativos.**
Não basta `goal` e `actor`. O JSON correto precisa fechar:

* `resource_ref`
* `operation`
* entidade de request
* entidade de response
* se depende de state model
* o que é proibido inferir
  Porque a superfície HTTP é soberana em `contracts/openapi/*`, e convenções de API vêm exclusivamente de `api_rules.yaml`. Se o IR deixar o agente escolher resource, operationId, tag ou shape HTTP, você perdeu o determinismo.

**6. O JSON tem que mapear decisão para superfície.**
O protocolo que você definiu exige que toda decisão promovida do navegador seja mapeada para superfícies canônicas e que o handoff seja fail-closed. Então o JSON correto precisa dizer explicitamente o que alimenta:

* `README`
* `MODULE_SCOPE`
* `DOMAIN_RULES`
* `INVARIANTS`
* `STATE_MODEL`
* `PERMISSIONS`
* `ERRORS`
* `UI_CONTRACT`
* `SCREEN_MAP`
* `OpenAPI`
* `Schema`
* `Workflow`
* `AsyncAPI`
  Se isso não estiver claro, você ainda está entregando pensamento, não material de compilação.

**7. Toda decisão aberta precisa ser tratada como bloqueio governado.**
O JSON correto não esconde lacuna. Ele declara `open_decisions` com impacto, superfície afetada e se bloqueia ou não. Isso combina com o seu modo estrito: artefato ausente ou decisão crítica ausente => bloquear. 

Então, em termos muito objetivos:

O segredo não é “escrever um JSON detalhado”.
O segredo é fazer o JSON obedecer a esta fórmula:

**decisão + tipo canônico + relação soberana + superfície alvo + regra de bloqueio**

Se faltar um desses elementos, o JSON ainda não está pronto.

A diferença entre um JSON ruim e um JSON bom é esta:

JSON ruim:

* descreve bem
* inspira bem
* organiza bem
* mas ainda exige interpretação

JSON bom:

* parece mais rígido
* parece menos elegante
* mas já vem quase “compilável”

A pergunta que você deve fazer para cada bloco é:
**“se eu apagar o agente e trocar por um template determinístico, isso ainda gera o artefato?”**

Se a resposta for não, aquele bloco ainda está errado.

Checklist mínimo para saber se o JSON está correto:

* cada entidade tem fields completos, não só nomes
* cada field tem `semantic_type_ref`
* cada relação tem ownership e delete policy
* cada lifecycle tem estado inicial e transições
* cada regra tem `subject_ref` e `formal_check_hint`
* cada use case HTTP é compilável
* cada parte aplicável do módulo aponta para uma superfície
* cada lacuna crítica está em `open_decisions`
* nenhuma parte obriga o agente a “escolher” algo importante

Esse é o segredo real.


**PREENCHER ABAIXO**

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "hbtrack/module-decision-ir.schema.json",
  "title": "HB Track Module Decision IR Schema",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "ir_version",
    "module",
    "status",
    "source",
    "decision_scope",
    "module_identity",
    "capabilities",
    "entities",
    "relations",
    "state_models",
    "rules",
    "api_use_cases",
    "ui_flows",
    "permissions",
    "errors",
    "events",
    "integrations",
    "open_decisions",
    "surface_mapping",
    "forbidden_inference_global"
  ],
  "properties": {
    "ir_version": {
      "type": "string"
    },
    "module": {
      "type": "string"
    },
    "status": {
      "type": "string",
      "enum": [
        "proposed",
        "approved",
        "draft"
      ]
    },
    "source": {
      "type": "string"
    },
    "decision_scope": {
      "type": "string",
      "enum": [
        "full_module",
        "feature",
        "revision"
      ]
    },
    "module_identity": {
      "type": "object"
    },
    "capabilities": {
      "type": "array"
    },
    "entities": {
      "type": "array"
    },
    "relations": {
      "type": "array"
    },
    "state_models": {
      "type": "array"
    },
    "rules": {
      "type": "array"
    },
    "api_use_cases": {
      "type": "array"
    },
    "ui_flows": {
      "type": "array"
    },
    "permissions": {
      "type": "object"
    },
    "errors": {
      "type": "array"
    },
    "events": {
      "type": "object"
    },
    "integrations": {
      "type": "array"
    },
    "open_decisions": {
      "type": "array"
    },
    "surface_mapping": {
      "type": "array"
    },
    "forbidden_inference_global": {
      "type": "array",
      "items": {
        "type": "string"
      }
    }
  }
}
```