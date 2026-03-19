1. Módulos do sistema da **Hb Track**

A arquitetura funcional da Hb Track deveria ser organizada em módulos de domínio, não apenas por telas. Isso evita acoplamento ruim e permite escalar produto, dados e operação com coerência. Abaixo está a decomposição recomendada.

**1. Core Platform**
É o núcleo transversal da plataforma. Sem ele, os outros módulos viram apenas features isoladas.

Capacidades:
- autenticação e autorização
- gestão de organizações, clubes, federações e competições
- gestão multi-tenant
- controle de perfis e permissões
- auditoria e trilha de ações
- configuração de ambiente, idioma, fuso, branding white-label
- notificações internas e externas
- central de integrações nativas internas entre módulos

Esse módulo também mantém o identificador único de atleta, staff, time, jogo, treino, evento e ativo de mídia.

**2. Master Data Management esportivo**
Esse é o módulo de cadastro mestre e governança de entidades esportivas.

Capacidades:
- cadastro de atletas
- cadastro de comissões técnicas
- cadastro de equipes e categorias
- cadastro de competições, temporadas e fases
- cadastro de arenas e quadras
- histórico esportivo por atleta
- elegibilidade, status contratual e vínculo competitivo
- versionamento de dados cadastrais

Ele resolve um dos maiores problemas das sport techs fragmentadas: múltiplas identidades para o mesmo atleta em sistemas diferentes.

**3. Performance Tracking Engine**
É o módulo responsável por tracking físico e espacial.

Capacidades:
- captura de dados de sensores e dispositivos indoor
- tracking de atletas em tempo real
- tracking da bola
- cálculo de velocidade, aceleração, desaceleração, distância e carga externa
- heatmaps e ocupação espacial
- reconstrução de deslocamentos e fases de jogo
- monitoramento em treino e jogo
- dashboards ao vivo de demanda física

Esse módulo é o equivalente ao bloco KINEXON + Catapult, mas nativamente unificado.

**4. Athlete Monitoring & Readiness**
Módulo voltado à disponibilidade física, fadiga, recuperação e risco.

Capacidades:
- carga aguda e crônica
- prontidão diária
- questionários de wellness
- monitoramento de fadiga
- alertas de risco de sobrecarga
- protocolos de retorno ao jogo
- restrições por atleta
- timeline de disponibilidade competitiva
- relatórios para performance staff e departamento médico

Ele consome dados do tracking e do calendário de treinos/jogos para transformar volume em decisão operacional.

**5. Video Capture & Media Processing**
Módulo para ingestão e processamento de vídeo.

Capacidades:
- captura de múltiplas câmeras
- ingestão automática de gravações
- sincronização entre vídeo, relógio de jogo e eventos
- geração de proxies e versões otimizadas
- indexação temporal
- armazenamento e arquivamento de mídia
- clipping automático
- highlights automáticos
- streaming interno e externo

Esse módulo é o backbone de mídia e análise visual.

**6. Video Analysis & Tagging**
É o módulo operacional de análise de vídeo.

Capacidades:
- tagging manual e semiautomático
- criação de templates por comissão técnica
- marcação de eventos ofensivos, defensivos e especiais
- associação de tags a atletas, zonas e sistemas
- busca de clipes por filtro
- playlists por tema, atleta, adversário ou jogo
- comparação lado a lado entre lances
- exportação de recortes para reuniões e feedback

Esse módulo substitui Nacsport, Hudl e parte de Spiideo no contexto técnico.

**7. Handball Event Scouting**
Módulo especializado em handebol para leitura técnico-tática.

Capacidades:
- modelagem de eventos nativos do handebol
- classificação de posse, ataque, defesa e transição
- leitura por sistema ofensivo e defensivo
- análise de superioridade e inferioridade numérica
- eficiência por zona e por fase
- scouting de goleiros
- scouting individual e coletivo
- relatórios pré-jogo e pós-jogo
- padrão de jogadas e recorrência tática

Esse é um dos módulos mais críticos do produto, porque é onde a plataforma deixa de ser “genérica de esporte” e vira handebol de verdade.

**8. Advanced Analytics & BI**
É o módulo analítico e de inteligência quantitativa.

Capacidades:
- KPIs operacionais e estratégicos
- estatística oficial e avançada
- métricas por posse
- eficiência contextual
- xG para handebol
- impacto por lineup
- comparação entre atletas, jogos e temporadas
- benchmarking por posição
- dashboards customizados
- exploração analítica ad hoc

Esse módulo deve funcionar tanto para analista de desempenho quanto para diretor esportivo.

**9. AI Insight Layer**
Camada de IA aplicada sobre dados, vídeo e eventos.

Capacidades:
- detecção de padrões táticos
- geração automática de relatórios
- sumarização de partidas em linguagem natural
- recomendação de clipes relevantes
- insights automáticos por atleta e equipe
- previsão de risco de queda de rendimento
- modelos de probabilidade de conversão
- identificação de semelhança entre atletas
- suporte a perguntas em linguagem natural sobre os dados

Esse módulo não deve ser tratado como feature isolada, e sim como uma camada transversal plugada aos demais domínios.

**10. Training Planning & Session Management**
Módulo para organização do processo de treino.

Capacidades:
- planejamento de microciclos e macrociclos
- agenda de sessões
- objetivos por treino
- catálogo de exercícios
- associação de exercícios a demandas físicas e táticas
- presença, minutagem e restrições
- comparação entre carga planejada e realizada
- observações da comissão técnica
- biblioteca metodológica

Ele conecta o “planejado” ao “executado”, o que quase sempre se perde em stacks fragmentados.

**11. Match Operations Center**
Módulo de operação de jogo ao vivo.

Capacidades:
- dashboard live para staff
- monitoramento físico em tempo real
- entrada de eventos ao vivo
- sincronização instantânea com vídeo
- visão de banco, tribuna e analista
- alertas de tendências de jogo
- comparação por parciais e lineups
- apoio a timeout e intervalo
- consolidação pós-jogo imediata

Na prática, esse é o cockpit da equipe durante a partida.

**12. Opponent Intelligence**
Módulo específico de preparação contra adversários.

Capacidades:
- consolidação de jogos anteriores do oponente
- padrões ofensivos e defensivos recorrentes
- zonas preferenciais
- tendência por treinador
- comportamento situacional
- scouting de atletas-chave adversários
- dossiês automáticos
- playlists para reunião pré-jogo
- matchup analysis

Esse módulo é uma vertical própria porque o workflow de “analisar o outro” é diferente do workflow de “analisar a si mesmo”.

**13. Goalkeeper Intelligence**
Módulo especializado para goleiros.

Capacidades:
- mapa de arremessos sofridos
- eficiência por zona
- leitura por tipo de finalização
- desempenho em 7 metros
- comportamento em contra-ataque
- sincronização com comportamento defensivo
- análise de tendência de arremessadores
- plano de preparação por adversário

Vale a pena separar esse módulo porque o handebol exige profundidade analítica específica para a posição.

**14. Medical & Recovery**
Módulo clínico-esportivo.

Capacidades:
- histórico de lesões
- status médico e restrições
- timeline de recuperação
- protocolos de reabilitação
- documentação clínica esportiva
- liberação progressiva
- conexão com carga e disponibilidade
- alertas para staff autorizado

Esse módulo precisa de segurança e segregação reforçadas por sensibilidade dos dados.

**15. Squad Management & Player Development**
Módulo de gestão esportiva do elenco e desenvolvimento.

Capacidades:
- perfil longitudinal do atleta
- objetivos individuais
- avaliação técnica, tática e física
- evolução por temporada
- plano de desenvolvimento por posição
- relatórios individuais
- gestão de base, transição e profissional
- histórico de minutagem e aproveitamento

Ele atende comissão, coordenação técnica e direção esportiva.

**16. Competition & Federation Operations**
Módulo orientado a ligas e federações.

Capacidades:
- cadastro e operação de competição
- gestão de calendário e jogos
- live stats oficiais
- homologação de dados
- operação de mesa e relatórios oficiais
- rankings e líderes estatísticos
- portal de competição
- distribuição de dados para parceiros

Esse módulo abre o mercado B2B institucional da Hb Track.

**17. Media, Broadcast & Digital Products**
Módulo para distribuição pública e comercial de informação.

Capacidades:
- widgets e overlays
- feed de live stats
- portal web de estatísticas
- minisites de competição
- API pública e privada
- highlights automáticos
- assets para imprensa
- pacotes de dados para narradores e comentaristas
- relatórios de consumo e engajamento

Aqui a Hb Track deixa de ser só software interno de performance e vira infraestrutura de produto digital.

**18. Reporting & Workflow Automation**
Módulo de automação operacional.

Capacidades:
- geração automática de relatórios
- envio programado de dashboards
- alertas por regra
- workflows de aprovação
- distribuição de vídeos e dossiês
- tarefas operacionais pós-jogo e pré-jogo
- automação de publicação em canais internos e externos

Esse módulo é o que reduz esforço humano repetitivo.

**19. Data Platform**
É a espinha dorsal técnica de dados da Hb Track.

Capacidades:
- ingestão de dados em batch e streaming
- normalização e enriquecimento
- event store esportivo
- time-series store para tracking
- data lake/lakehouse
- catálogo de dados
- versionamento e lineage
- camada semântica
- APIs internas entre módulos
- base para BI e IA

Sem esse módulo, o produto vira um conjunto de features desconectadas.

**20. API & Extensibility Layer**
Mesmo que a proposta seja eliminar dependência de integrações externas, a plataforma ainda precisa expor serviços de forma controlada.

Capacidades:
- APIs REST/GraphQL
- webhooks
- SDK interno
- event bus
- conectores para exportação institucional
- autenticação de parceiros
- rate limiting
- sandbox para parceiros autorizados

A diferença é que a integração deixa de ser “necessária para operar” e passa a ser “opcional para expandir”.

A forma mais correta de enxergar a Hb Track é em 5 macrocamadas:

- operação esportiva: treino, jogo, elenco, adversário
- performance: tracking, readiness, médico, recuperação
- inteligência: analytics, scouting, IA, benchmarking
- mídia e competição: live stats, broadcast, federações, APIs
- plataforma: core, dados, segurança, automação, governança


2. Arquitetura de alto nível da **Hb Track**

A arquitetura da Hb Track deve ser pensada como uma plataforma distribuída, orientada a eventos, com processamento híbrido de dados em tempo real e batch. O motivo é simples: handebol de alto rendimento exige simultaneamente latência baixa para operação ao vivo, consistência histórica para análise longitudinal e flexibilidade para evolução de produto.

A melhor forma de estruturar isso é separar a plataforma em 7 camadas principais:

**1. Camada de experiência e canais**
É a camada de entrada dos usuários e consumidores do sistema.

Componentes:
- web app para comissão técnica, analistas, gestores e federações
- app tablet para banco, tribuna e operação de jogo
- app mobile para atletas e staff
- console de captura/scouting ao vivo
- portal público de competição e estatísticas
- APIs externas para mídia, parceiros e produtos digitais

Objetivo:
entregar interfaces especializadas por persona, mas consumindo os mesmos serviços centrais.

Aqui o princípio arquitetural deve ser: front-end desacoplado do domínio, consumindo BFFs ou APIs de domínio, sem lógica de negócio crítica embutida na interface.

**2. Camada de aplicação e orquestração**
Essa camada organiza os fluxos de negócio e a experiência operacional.

Componentes:
- BFF para web de alto rendimento
- BFF para mobile de atletas
- BFF para match operations
- workflow engine
- notification service
- report generation orchestrator
- rules engine para alertas e automações

Função:
traduzir ações de usuário em chamadas coordenadas aos serviços de domínio, sem concentrar regras pesadas demais.

Exemplos:
- “gerar relatório pós-jogo”
- “publicar live stats”
- “criar dossiê do adversário”
- “enviar alertas de sobrecarga”
- “abrir vídeo correspondente ao evento tático”

Essa camada não deve armazenar estado de negócio principal; ela orquestra, não domina o dado.

**3. Camada de domínio esportivo e serviços de negócio**
Esse é o coração funcional da Hb Track. Aqui ficam os bounded contexts reais da plataforma.

Os principais serviços de domínio seriam:

- Identity & Access Service
- Organization & Tenant Service
- Athlete Registry Service
- Team & Competition Service
- Training Planning Service
- Match Operations Service
- Event Scouting Service
- Video Management Service
- Tracking Service
- Athlete Monitoring Service
- Medical & Recovery Service
- Goalkeeper Intelligence Service
- Opponent Intelligence Service
- Analytics Service
- Reporting Service
- Media Distribution Service
- Federation Operations Service

Cada serviço deve possuir:
- modelo de domínio próprio
- banco transacional próprio quando necessário
- APIs síncronas para consultas operacionais
- publicação de eventos assíncronos para o restante da plataforma

O princípio aqui é evitar um monólito funcional. Também não vale cair no erro oposto de microserviços excessivamente granulares desde o dia 1. O ideal é um **modular monolith evolutivo** ou **microserviços por domínio maior**, dependendo do estágio do produto.

Para Hb Track, a recomendação pragmática seria:
- começar com um **modular monolith bem particionado** para os domínios administrativos e operacionais
- usar serviços separados desde o início para componentes com alta demanda técnica específica: tracking, vídeo, ingestão de dados, analytics e IA

Isso reduz complexidade inicial sem sacrificar escalabilidade futura.

**4. Camada de ingestão e processamento de dados**
Como a Hb Track lida com sensores, vídeo, scouting manual, estatística oficial e automações, ela precisa de uma camada própria de ingestão.

Subcamadas:

**4.1 Ingestão em tempo real**
Responsável por:
- receber telemetria de sensores
- receber eventos ao vivo do scouting
- sincronizar relógio de jogo
- receber metadata de vídeo
- processar sinais de baixa latência

Tecnologias típicas:
- gateway de ingestão
- message broker
- stream processor
- event bus

Casos de uso:
- posição do atleta em tempo real
- evento de arremesso
- clipping automático
- alerta de carga ao vivo
- atualização de dashboard de banco

**4.2 Ingestão batch**
Responsável por:
- importar jogos históricos
- processar vídeos completos após partida
- recalcular métricas
- consolidar dados de temporada
- rodar pipelines analíticos pesados

Casos de uso:
- reprocessamento de tracking
- enriquecimento estatístico
- reindexação de acervo de vídeo
- cálculo de benchmark de liga

**4.3 Normalização e enriquecimento**
Essa é uma peça crítica. Toda entrada precisa ser convertida para um modelo canônico Hb Track.

Exemplos:
- padronizar atleta, equipe, competição e jogo
- alinhar timestamps entre vídeo, sensores e eventos
- associar evento tático a frame e posição em quadra
- enriquecer ação com contexto: fase, sistema, zona, lineup, placar, vantagem numérica

Sem essa camada, a promessa de unificação da Hb Track quebra.

**5. Camada de dados e armazenamento**
A Hb Track não deve usar um único banco para tudo. O modelo correto é poliglota, com armazenamento orientado ao tipo de dado.

**5.1 Banco transacional**
Uso:
- cadastro de atletas
- usuários e permissões
- calendários
- treinos
- jogos
- workflows
- configuração de competição

Perfil:
- consistência forte
- queries operacionais
- integridade relacional

**5.2 Event store**
Uso:
- eventos esportivos
- scouting
- ações de jogo
- mudanças de estado operacionais
- trilha auditável de eventos

Perfil:
- reconstrução de timeline
- reprocessamento
- auditabilidade

**5.3 Time-series store**
Uso:
- tracking de atletas
- tracking de bola
- métricas fisiológicas
- sinais contínuos e séries temporais

Perfil:
- alto volume
- compressão eficiente
- consultas por janela temporal

**5.4 Object storage**
Uso:
- vídeos brutos
- vídeos processados
- clipes
- imagens
- relatórios exportados
- datasets de treinamento de modelos

Perfil:
- grande escala
- baixo custo relativo
- versionamento

**5.5 Lakehouse analítico**
Uso:
- histórico consolidado
- BI
- benchmarking
- machine learning
- relatórios executivos
- consultas multidimensionais

Perfil:
- leitura analítica
- processamento batch e incremental
- semântica corporativa

**5.6 Search index**
Uso:
- busca por clipes
- busca por atletas
- busca por jogadas
- busca textual em relatórios e anotações

Perfil:
- recuperação rápida
- filtros avançados
- ranking por relevância

Em alto nível, a regra é:
- operação no banco transacional
- telemetria no time-series
- mídia no object storage
- histórico analítico no lakehouse
- recuperação textual no search index

**6. Camada de inteligência, analytics e IA**
Essa é a camada que transforma dados em decisão.

Ela deve ser separada em quatro blocos:

**6.1 Metrics Engine**
Responsável por:
- KPIs oficiais
- métricas avançadas
- eficiência por posse
- xG
- impacto por lineup
- cargas físicas derivadas
- métricas contextuais

**6.2 Analytics Serving Layer**
Responsável por:
- dashboards
- consultas agregadas
- comparações históricas
- ranking de atletas
- benchmarking entre equipes
- painéis de federação e mídia

**6.3 AI/ML Platform**
Responsável por:
- treinamento de modelos
- inferência em lote
- inferência quase em tempo real
- classificação de eventos
- recomendação de vídeo
- geração de linguagem natural
- previsão de risco e performance

**6.4 Semantic Query Layer**
Responsável por permitir consultas do tipo:
- “mostre todos os ataques 7x6 com perda de eficiência no segundo tempo”
- “traga clips de contra-ataque do ponta esquerda contra defesa 6:0”
- “quais atletas apresentam queda de conversão acima de certo limiar de carga?”

Essa camada é essencial para tornar a plataforma realmente superior às ferramentas isoladas.

**7. Camada de governança, segurança e observabilidade**
Por lidar com dados médicos, biométricos, competitivos e comerciais, a Hb Track precisa nascer enterprise.

Blocos obrigatórios:
- IAM com RBAC e ABAC
- segregação multi-tenant forte
- criptografia em trânsito e em repouso
- gestão de consentimento
- masking de dados sensíveis
- auditoria completa
- observabilidade de aplicações
- observabilidade de pipelines
- tracing distribuído
- monitoramento de latência de ingestão ao vivo
- backup e disaster recovery
- trilha de acesso a dados médicos e biométricos

Agora, em vez de descrever só as camadas, vale mostrar o fluxo técnico real.

**Fluxo de dados de alto nível**

**Fluxo A: jogo ao vivo**
1. sensores e console de scouting enviam dados
2. gateway de ingestão recebe os eventos
3. broker distribui para serviços interessados
4. tracking service processa sinais espaciais
5. event scouting service registra eventos táticos
6. sync engine alinha tracking, vídeo e relógio oficial
7. match operations service alimenta dashboards ao vivo
8. media distribution publica live stats
9. analytics serving atualiza métricas operacionais
10. rules engine dispara alertas em caso de risco ou padrões relevantes

**Fluxo B: pós-jogo**
1. vídeo bruto é consolidado
2. media processing gera proxies, capítulos e clipes
3. pipelines batch recalculam métricas avançadas
4. dados enriquecidos vão para lakehouse
5. reporting engine gera relatório pós-jogo
6. AI layer produz sumário e destaca padrões
7. playlists são distribuídas para comissão e atletas

**Fluxo C: planejamento semanal**
1. treinador monta microciclo
2. training planning service registra objetivos e sessões
3. athlete monitoring cruza disponibilidade e restrições
4. analytics sugere carga recomendada
5. staff executa treino
6. tracking e vídeo capturam o realizado
7. comparação planejado vs realizado alimenta avaliação semanal

**Fluxo D: preparação de adversário**
1. jogos do adversário são ingeridos
2. event pipelines e AI classificam comportamentos
3. opponent intelligence consolida padrões
4. video service organiza playlists temáticas
5. reporting engine gera dossiê pré-jogo
6. comissão consome dashboards e clips

A representação lógica da arquitetura pode ser resumida assim:

```text
[Web / Mobile / Tablet / Public Portal / API Consumers]
                    |
             [BFF / Orchestration]
                    |
 ---------------------------------------------------------
| Domínio Esportivo | Match Ops | Video | Tracking | BI  |
| Monitoring        | Medical   | Media | Scouting | AI  |
 ---------------------------------------------------------
                    |
        [Event Bus / Stream Processing / Workflow Engine]
                    |
 ---------------------------------------------------------
| Transaction DB | Event Store | Time-Series | Object    |
| Lakehouse      | Search      | Cache       | Feature   |
 ---------------------------------------------------------
                    |
      [Security / Governance / Observability / Audit]
```

Agora, do ponto de vista de estilo arquitetural, a Hb Track deveria seguir estes princípios:

**Arquitetura orientada a eventos**
Necessária porque tracking, vídeo, alertas e live stats dependem de propagação assíncrona e desacoplada.

**Domain-driven design**
Necessário porque o problema não é genérico. Handebol, goleiro, superioridade numérica, scouting e match operations têm linguagem própria e precisam de bounded contexts claros.

**CQRS em áreas críticas**
Especialmente útil em:
- live stats
- dashboards de jogo
- analytics de leitura intensiva
- reporting
- busca de clipes

**Event sourcing seletivo**
Não em tudo, mas faz sentido para:
- timeline de jogo
- eventos esportivos
- auditoria crítica
- fluxos de homologação oficial

**Storage polyglot**
Obrigatório pelo tipo de dado.

**Streaming + batch**
Obrigatório porque parte do valor é ao vivo e parte do valor depende de reprocessamento histórico.

Do ponto de vista de separação física, eu dividiria em quatro blocos de deploy.

**Bloco 1: plataforma transacional**
- core platform
- cadastro
- treinos
- jogos
- usuários
- permissões

**Bloco 2: real-time engine**
- ingestão
- tracking
- event bus
- match ops
- live stats
- alertas

**Bloco 3: media engine**
- ingestão de vídeo
- processamento
- clipping
- streaming
- catálogo de mídia

**Bloco 4: intelligence platform**
- lakehouse
- BI
- métricas
- ML
- IA generativa
- benchmarking

Isso permite escalar cada parte segundo seu padrão real de carga.

Também é importante definir fronteiras de latência:

- até 1–3 segundos: live scouting, live stats, dashboards de banco
- até 5–10 segundos: alertas táticos e físicos em jogo
- até poucos minutos: clipping automático e sincronização enriquecida
- até horas: relatório pós-jogo completo
- até dia seguinte: benchmarking consolidado e análises mais pesadas

Do ponto de vista de confiabilidade, os componentes críticos são:

- ingestão ao vivo
- sincronização de tempo
- tracking engine
- match operations
- event store
- video availability

Esses componentes exigem alta disponibilidade e fallback operacional. Em jogo oficial, a Hb Track não pode depender de processamento frágil ou de uma única máquina.

Por isso, a arquitetura deve prever:

- buffer local de captura em quadra
- reenvio de eventos em caso de falha de conexão
- modo degradado para operação manual
- sincronização posterior quando a conectividade voltar
- redundância de armazenamento para vídeo e eventos críticos

Em termos de fronteira entre produto e infraestrutura, o desenho ideal seria este:

**Produto**
define fluxos esportivos, regras, experiência e inteligência.

**Plataforma**
fornece autenticação, observabilidade, mensageria, storage, CI/CD, segurança e governança.

Essa separação é importante porque Hb Track não é apenas um app; é uma plataforma operacional crítica.

Em resumo, a arquitetura de alto nível da Hb Track deve fazer quatro coisas ao mesmo tempo:
operar o presente, registrar o passado, explicar o desempenho e prever o que vem a seguir.

Traduzindo isso para arquitetura:
- operar com baixa latência
- consolidar com alta consistência
- analisar com profundidade histórica
- servir inteligência acionável


3. Perfis de usuário e permissões da **Hb Track**

Na Hb Track, perfis de usuário não devem ser tratados apenas como “tipos de login”. Eles precisam ser modelados como uma combinação de função organizacional, escopo de dados, responsabilidade operacional e sensibilidade de acesso.

A abordagem correta é usar um modelo híbrido de autorização com:

- **RBAC** para papéis padrão
- **ABAC** para restrições contextuais
- **escopo hierárquico** por organização, equipe, competição, temporada e atleta
- **segregação por tenant** para clubes, federações, ligas e parceiros

Isso é essencial porque a plataforma mistura dados esportivos, médicos, biométricos, competitivos, comerciais e públicos.

Abaixo está a estrutura recomendada.

**1. Super Admin da plataforma**
É o perfil interno da Hb Track, responsável pela administração global da solução.

Pode fazer:
- gerenciar tenants
- configurar módulos habilitados por cliente
- administrar contratos, licenças e limites
- acompanhar observabilidade e saúde do sistema
- executar suporte avançado
- gerenciar templates globais
- administrar catálogos mestres da plataforma

Não deve acessar por padrão:
- dados médicos detalhados
- vídeo privado sensível
- relatórios estratégicos internos do cliente

Regra crítica:
mesmo o super admin não deve ter acesso irrestrito por default ao conteúdo sensível do cliente. O acesso precisa ser just-in-time, auditado e, idealmente, aprovado.

**2. Tenant Admin**
É o administrador principal de um clube, federação ou liga dentro da Hb Track.

Pode fazer:
- criar usuários
- atribuir perfis
- configurar equipes, categorias e temporadas
- definir branding e parâmetros do tenant
- gerenciar permissões locais
- configurar integrações autorizadas
- controlar políticas de retenção e visibilidade interna

Normalmente pertence a:
- diretor de tecnologia
- gestor de operações
- gerente administrativo esportivo
- head de performance digital

Não deve fazer por default:
- alterar registros médicos clínicos
- homologar dados oficiais de federação, salvo se também tiver esse papel

**3. Diretor Executivo / C-Level**
Perfil voltado a presidência, diretoria geral ou alta gestão.

Pode acessar:
- dashboards estratégicos
- indicadores consolidados
- performance institucional
- uso da plataforma
- relatórios executivos
- saúde do elenco em nível resumido
- KPIs financeiros-operacionais relacionados ao esporte

Deve ter acesso:
- predominantemente leitura
- visão consolidada
- comparativos de temporada
- relatórios de ROI, disponibilidade e performance global

Não deve ver por padrão:
- prontuário médico detalhado
- scouting sigiloso de atletas-alvo
- parâmetros técnicos operacionais excessivamente granulares

Esse perfil precisa de informação sintética, não de interface operacional.

**4. Diretor Esportivo**
É um dos perfis centrais da plataforma.

Pode fazer:
- acompanhar evolução do elenco
- consultar scouting interno e externo
- acessar relatórios de desempenho
- analisar disponibilidade de atletas
- comparar atletas por posição
- acompanhar plano de desenvolvimento
- acessar inteligência de mercado e benchmarking
- aprovar fluxos de contratação ou avaliação interna

Pode visualizar:
- desempenho técnico-tático
- histórico competitivo
- métricas físicas resumidas
- relatórios de risco em nível gerencial

Acesso médico:
somente visão resumida e funcional, nunca clínica detalhada, a menos que exista autorização explícita da política do clube.

**5. Head Coach / Treinador Principal**
É um dos usuários mais intensivos da Hb Track.

Pode fazer:
- acessar jogos, treinos, vídeos e relatórios
- montar microciclos
- revisar scouting do próprio time e adversários
- criar playlists de vídeo
- consultar dashboards táticos
- acompanhar disponibilidade esportiva do elenco
- registrar observações
- operar match center em jogo
- validar planos de sessão
- definir objetivos técnicos e táticos

Pode visualizar:
- carga de treino em visão operacional
- status de aptidão esportiva
- alertas de disponibilidade
- restrições aplicáveis ao treino/jogo

Não deve ver:
- diagnóstico médico sensível
- detalhes clínicos desnecessários
- informação contratual sigilosa, salvo se autorizado

A regra é: o treinador pode saber “o atleta está apto, restrito ou indisponível, e por quê em nível funcional”, mas não precisa ver detalhes médicos além do necessário.

**6. Assistant Coach / Auxiliar Técnico**
Semelhante ao treinador principal, mas com escopo potencialmente menor.

Pode fazer:
- revisar vídeo
- acessar relatórios técnicos
- colaborar no planejamento
- consultar scouting do adversário
- registrar observações
- montar recortes de análise
- operar parte do fluxo de match operations

Pode ter limitação:
- não aprovar relatórios finais
- não alterar configurações críticas
- não acessar inteligência estratégica integral sem delegação

**7. Analista de Desempenho / Performance Analyst**
Perfil crítico em clubes profissionais.

Pode fazer:
- criar e editar templates de scouting
- operar tagging ao vivo
- revisar tracking
- construir dashboards técnicos
- gerar relatórios pós-jogo
- produzir dossiês de adversário
- cruzar vídeo com evento e espaço
- consultar métricas avançadas
- comparar lineups, padrões táticos e eficiência

Pode acessar:
- vídeo completo
- evento detalhado
- analytics granular
- contextualização por fase, zona, atleta e sistema

Normalmente não deve:
- alterar dados cadastrais centrais
- acessar registros clínicos detalhados
- publicar dados públicos oficiais sem aprovação

Esse perfil tem permissão alta no domínio analítico, não no administrativo.

**8. Analista de Vídeo**
Perfil mais específico que o analista de desempenho.

Pode fazer:
- ingestão e organização de vídeo
- tagging
- corte e clipping
- criação de playlists
- associação de eventos a lances
- gestão do catálogo audiovisual
- produção de material de reunião

Pode ter acesso total:
- à biblioteca de vídeo do seu escopo

Pode ter acesso parcial:
- a métricas e scouting, apenas para contextualização

É útil separar este papel quando o clube tem estrutura maior.

**9. Scout / Scout de adversário**
Perfil focado em observação e inteligência competitiva.

Pode fazer:
- registrar observações
- classificar padrões do adversário
- montar relatórios de opponent intelligence
- anotar tendências individuais e coletivas
- alimentar biblioteca de scouting
- comparar equipes e jogadores

Pode acessar:
- vídeos e jogos do adversário dentro do escopo
- relatórios de inteligência
- métricas comparativas

Não deve:
- acessar dados médicos do próprio elenco
- alterar planejamento interno de treino
- ver contratos ou informações administrativas

**10. Preparador Físico / Strength & Conditioning Coach**
É o principal usuário da camada de performance.

Pode fazer:
- acompanhar carga externa e interna
- consultar prontidão
- analisar volume, intensidade e fadiga
- aprovar ou ajustar carga do treino
- registrar observações de performance
- gerir protocolos de retorno progressivo
- emitir alertas de sobrecarga
- comparar planejado vs realizado

Pode acessar:
- tracking detalhado
- séries temporais físicas
- dashboards de readiness
- restrições esportivas aplicáveis

Não deve acessar por default:
- prontuário clínico completo
- negociação contratual
- inteligência de mercado

**11. Fisiologista / Performance Scientist**
Perfil de profundidade analítica física.

Pode fazer:
- modelagem de carga
- análise longitudinal
- construção de benchmarks
- calibração de zonas e limiares
- estudos comparativos por posição
- suporte à prevenção de lesão
- validação de modelos de performance

Pode ter acesso:
- a datasets detalhados de tracking e readiness
- a módulos avançados de analytics físico

Esse perfil pode compartilhar espaço com o preparador físico, mas em organizações maduras vale separar.

**12. Fisioterapeuta**
Perfil clínico-funcional.

Pode fazer:
- registrar evolução de recuperação
- acompanhar restrições
- consultar histórico funcional
- operar protocolos de retorno
- documentar intervenções
- compartilhar status esportivo com staff autorizado

Pode acessar:
- dados clínico-funcionais do atleta
- parte do tracking relevante à reabilitação
- vídeos e cargas relacionados à recuperação

Não deve:
- divulgar dados médicos a perfis não autorizados
- acessar inteligência estratégica de mercado sem necessidade

**13. Médico**
Perfil de maior sensibilidade regulatória.

Pode fazer:
- registrar diagnósticos
- emitir aptidão médica
- estabelecer restrições
- acompanhar exames e histórico clínico
- controlar evolução médica
- liberar ou vetar participação
- consultar carga e contexto esportivo para decisão clínica

Pode acessar:
- o nível máximo de informação médica do seu escopo

Regra crítica:
todo acesso médico deve ser fortemente auditado, com trilha completa de leitura, edição e exportação.

**14. Nutricionista**
Pode fazer:
- registrar planos alimentares esportivos
- acompanhar indicadores relacionados à performance
- associar intervenções ao calendário esportivo
- registrar observações por atleta

Pode acessar:
- informações físicas e de rotina necessárias
- restrições esportivas relacionadas ao seu domínio

Não deve acessar:
- scouting detalhado
- inteligência de mercado
- dados clínicos além do estritamente necessário

**15. Coordenador de Base**
Perfil importante para clubes e federações.

Pode fazer:
- acompanhar categorias inferiores
- comparar evolução longitudinal
- controlar transição para categorias superiores
- visualizar carga, minutagem e desenvolvimento
- consolidar relatórios de formação
- acompanhar trilhas por posição

Pode acessar:
- módulos de desenvolvimento
- analytics da base
- histórico esportivo e técnico

Pode ter restrição:
- sem acesso ao profissional, salvo delegação
- sem acesso médico detalhado

**16. Atleta**
O atleta não deve ser tratado como usuário passivo; ele precisa de um portal próprio.

Pode fazer:
- ver agenda de treinos e jogos
- consumir clipes e feedbacks atribuídos
- visualizar indicadores pessoais liberados
- responder wellness e questionários
- acompanhar metas de desenvolvimento
- receber planos e tarefas
- consultar status de disponibilidade em linguagem apropriada

Pode acessar:
- apenas seus próprios dados
- apenas vídeos e relatórios compartilhados com ele
- apenas parte das métricas definidas pelo clube

Não deve acessar:
- dados de colegas
- scouting coletivo confidencial
- relatórios estratégicos do staff

**17. Staff de mesa / Operador de jogo**
Perfil operacional de competição ou clube.

Pode fazer:
- registrar eventos ao vivo
- validar cronologia do jogo
- operar match center
- controlar relógio e inputs oficiais
- revisar eventos em caso de correção
- exportar súmulas e relatórios permitidos

Pode ter acesso:
- muito restrito e focado na operação do evento

Esse perfil precisa de interface rápida e permissões estreitas.

**18. Árbitro / Delegado / Oficial de competição**
Perfil ligado a federação ou liga.

Pode fazer:
- consultar dados oficiais da partida
- validar informações operacionais
- homologar certos registros conforme regra da competição
- acessar documentos e evidências associadas ao jogo

Não deve:
- acessar inteligência interna do clube
- acessar dados médicos
- ver material privado de comissão técnica

**19. Operador de mídia / Broadcast**
Perfil voltado à distribuição pública.

Pode fazer:
- consumir feed de live stats
- acessar widgets e overlays
- baixar assets autorizados
- operar publicação de highlights
- integrar estatísticas ao produto digital
- usar dashboards públicos ou semipúblicos

Pode acessar:
- apenas dados liberados para mídia
- apenas vídeos marcados como publicáveis

Não deve:
- ver analytics estratégicos
- acessar scouting do adversário
- consultar dados de performance sensíveis

**20. Jornalista / Parceiro externo**
Perfil externo, de escopo muito limitado.

Pode acessar:
- portal público
- estatísticas oficiais públicas
- relatórios divulgáveis
- rankings e líderes
- clips públicos

Não deve acessar:
- nada interno ou sensível

**21. Federação / Liga Admin**
Perfil institucional.

Pode fazer:
- administrar competições
- definir estrutura de temporada
- configurar fases e regras
- homologar jogos
- publicar live stats oficiais
- acessar dashboards de competição
- distribuir dados oficiais para parceiros

Pode acessar:
- dados agregados e oficiais das entidades sob sua governança

Não deve acessar por default:
- medicina interna de clubes
- relatórios estratégicos privados de cada equipe

**22. Gestor comercial / patrocinador / parceiro institucional**
Em alguns casos a Hb Track pode ter visões específicas para parceiros.

Pode acessar:
- painéis de audiência
- uso de mídia
- highlights públicos
- métricas de ativação e exposição
- estatísticas públicas relevantes

Acesso sempre:
- agregado
- sem conteúdo sensível competitivo

Agora, além de perfis, a Hb Track precisa de um modelo claro de escopo.

**Modelo de escopo de acesso**

Todo usuário deve ter permissões combinadas com escopos como:

- organização
- unidade de negócio
- equipe
- categoria
- competição
- temporada
- jogo
- atleta
- módulo
- tipo de dado

Exemplo:
um preparador físico do sub-18 pode ter acesso total ao módulo físico daquela categoria, mas nenhum acesso ao elenco profissional.

Outro exemplo:
um analista de adversário pode acessar jogos da competição nacional adulta, mas não os dados médicos do próprio clube.

A regra correta é esta:

**Permissão = papel + ação + recurso + escopo + contexto**

Não basta “ser treinador”. É preciso definir:
- treinador de qual equipe
- em qual temporada
- com quais módulos
- com qual nível de escrita, leitura, exportação e compartilhamento

**Tipos de permissão por ação**

As ações devem ser padronizadas. Recomendo pelo menos estas:

- visualizar
- criar
- editar
- excluir
- homologar
- publicar
- exportar
- compartilhar
- aprovar
- administrar

Isso evita ambiguidades como “ele pode ver, mas pode exportar?” ou “ele pode editar, mas não publicar?”.

**Classificação de sensibilidade dos dados**

A Hb Track deveria classificar os dados em níveis, porque isso impacta UI, logs, exportação e políticas.

Sugestão:

**Nível 1 — Público**
- estatísticas oficiais públicas
- calendário público
- rankings divulgáveis

**Nível 2 — Interno operacional**
- treinos
- vídeo interno
- relatórios técnicos
- workflows de staff

**Nível 3 — Competitivo confidencial**
- scouting de adversário
- relatórios estratégicos
- modelos analíticos internos
- playlists táticas
- avaliações individuais confidenciais

**Nível 4 — Sensível pessoal**
- dados biométricos
- wellness
- tracking individual detalhado
- histórico funcional

**Nível 5 — Sensível regulado**
- diagnóstico médico
- documentos clínicos
- exames
- dados protegidos por exigência legal/regulatória

Cada nível deve impor exigências progressivas de:
- autenticação
- autorização
- criptografia
- mascaramento
- auditoria
- exportação restrita

**Regras especiais de autorização**

Além dos papéis, a Hb Track deve aplicar regras contextuais, por exemplo:

- médico só acessa registro médico se estiver vinculado ao atleta ou equipe
- treinador só vê restrição funcional, não laudo clínico
- atleta só vê relatórios explicitamente compartilhados
- mídia só consome estatística homologada e publicada
- exportação de dados biométricos exige política específica
- acesso fora do horário de competição ou fora do país pode exigir step-up auth
- ações de homologação oficial exigem dupla confirmação
- acesso de suporte do fornecedor deve expirar automaticamente

Essas regras são de ABAC e precisam existir desde o começo.

**Matriz resumida de perfis por macrodomínio**

| Perfil | Operação esportiva | Vídeo | Analytics | Performance física | Médico | Competição | Mídia | Administração |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| Super Admin | limitado e auditado | limitado | limitado | limitado | muito restrito | limitado | limitado | total plataforma |
| Tenant Admin | médio | baixo | médio | baixo | sem padrão | médio | baixo | alto tenant |
| Diretor Executivo | leitura | baixo | alto executivo | resumo | resumo | baixo | baixo | baixo |
| Diretor Esportivo | alto | médio | alto | resumo | resumo | baixo | baixo | médio |
| Head Coach | alto | alto | alto | médio funcional | restrito | baixo | baixo | baixo |
| Auxiliar Técnico | alto | alto | médio | médio | restrito | baixo | baixo | baixo |
| Analista de Desempenho | alto | alto | muito alto | médio | restrito | baixo | baixo | baixo |
| Preparador Físico | médio | baixo | alto físico | muito alto | baixo | baixo | baixo | baixo |
| Fisioterapeuta | médio | médio | médio reabilitação | alto | alto funcional | baixo | baixo | baixo |
| Médico | médio | baixo | médio clínico | médio | muito alto | baixo | baixo | baixo |
| Atleta | próprio escopo | próprio escopo | próprio escopo | próprio escopo | próprio escopo resumido | nenhum | nenhum | nenhum |
| Liga/Federação Admin | médio oficial | baixo | alto oficial | nenhum | nenhum | muito alto | médio | alto institucional |
| Operador de mídia | baixo | médio publicável | médio público | nenhum | nenhum | médio oficial | alto | nenhum |

**Modelo recomendado de implementação**

Eu implementaria isso em quatro níveis:

**Nível 1: Role catalog**
Catálogo fixo de perfis base do produto.

**Nível 2: Permission bundles**
Pacotes de permissão por módulo e ação.

**Nível 3: Scope binding**
Vinculação a equipe, competição, categoria, atleta e temporada.

**Nível 4: Policy engine**
Regras dinâmicas para dados sensíveis e contexto de acesso.

Exemplo técnico:

- papel: `HEAD_COACH`
- permissões: `view_match`, `edit_training_plan`, `view_video`, `view_team_readiness`
- escopo: `club=A`, `team=adulto_masculino`, `season=2026`
- política extra: `deny medical_diagnosis_details`
- política extra: `allow athlete_status_functional_summary`

Esse modelo é muito mais sólido do que uma lista solta de “admins e usuários”.

**Princípios de UX para permissões**

A interface também precisa refletir o modelo de acesso. Portanto:

- o usuário só deve ver menus que pode usar
- campos sensíveis devem aparecer mascarados quando necessário
- módulos não autorizados nem devem ser exibidos
- ações críticas devem exigir confirmação forte
- compartilhamento de relatório deve respeitar classificação do dado
- logs de acesso sensível devem ser visíveis a auditores autorizados

Permissão mal desenhada vira problema de segurança e de usabilidade ao mesmo tempo.

**Em resumo**

Os perfis da Hb Track devem ser construídos para refletir a realidade do ecossistema do handebol profissional e institucional. O ponto central não é “quem entra”, mas:

- quem pode ver o quê
- quem pode alterar o quê
- em qual contexto
- sobre qual equipe, atleta ou competição
- com qual nível de rastreabilidade

A estrutura correta é:

- perfis bem definidos
- escopo hierárquico
- sensibilidade de dados
- políticas contextuais
- auditoria forte

Sem isso, uma plataforma tão ampla quanto a Hb Track se tornaria insegura e operacionalmente caótica.