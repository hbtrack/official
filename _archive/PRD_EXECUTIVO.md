# PRD Executivo — Hb Track

## 1. Visão do produto

A **Hb Track** é uma plataforma unificada de sport tech para handebol, desenhada para consolidar em um único sistema as capacidades hoje distribuídas entre ferramentas de tracking, vídeo, scouting, analytics, athlete monitoring, operação de jogo, gestão técnica, dados oficiais, mídia e competição.

O problema que a Hb Track resolve é estrutural: o ecossistema atual obriga clubes, federações e ligas a operar múltiplos sistemas desconectados, com duplicação de cadastro, reconciliação manual de dados, baixa interoperabilidade real, alto custo operacional e perda de contexto entre o que acontece no treino, no jogo, no vídeo, na estatística e na performance física.

A proposta central da Hb Track é simples: **uma única fonte de verdade para o handebol**, do treino à competição, do atleta à federação, do sensor ao insight, do dado interno ao produto digital.

## 2. Problema de negócio

Hoje, a maioria das organizações de handebol opera com um stack fragmentado. Isso gera cinco problemas centrais.

Primeiro, **fragmentação operacional**. O analista usa uma ferramenta para vídeo, outra para tagging, outra para relatório, outra para estatística, outra para tracking, e frequentemente planilhas para unir tudo.

Segundo, **duplicação e inconsistência de dados**. O mesmo atleta, jogo ou evento existe com identificadores e interpretações diferentes em plataformas distintas.

Terceiro, **baixa velocidade de decisão**. A comissão técnica perde tempo consolidando informação em vez de decidir.

Quarto, **visão parcial do desempenho**. O staff técnico vê tática; o físico vê carga; o médico vê restrição; a diretoria vê relatório tardio. Ninguém vê o sistema inteiro em tempo adequado.

Quinto, **dependência de integrações externas**. O valor da operação fica refém de APIs, conectores frágeis, latência, divergência semântica e custos cumulativos de licenciamento.

A Hb Track nasce para eliminar esse modelo.

## 3. Objetivo estratégico

O objetivo da Hb Track é tornar-se a plataforma operacional e analítica padrão do handebol, atendendo três níveis de mercado.

No nível 1, **clubes e comissões técnicas**, com foco em vídeo, scouting, treino, jogo e performance.

No nível 2, **alto rendimento e departamentos integrados**, conectando tática, carga, readiness, recuperação, desenvolvimento individual e inteligência de adversário.

No nível 3, **federações, ligas e mídia**, oferecendo operação de competição, live stats, distribuição de dados, APIs, widgets, portais públicos e inteligência institucional.

## 4. Proposta de valor

A Hb Track entrega valor em quatro eixos.

**Eixo operacional**: reduz retrabalho, substitui múltiplas ferramentas e organiza a rotina esportiva em um único fluxo.

**Eixo analítico**: integra vídeo, evento, tracking, carga e contexto tático em uma camada única de inteligência.

**Eixo estratégico**: apoia treinador, direção esportiva, performance staff e federação com dados acionáveis, não apenas registros.

**Eixo institucional**: permite que o mesmo backbone sirva uso interno, operação oficial, mídia e produto digital.

## 5. Escopo do produto

A Hb Track é uma plataforma composta por módulos de domínio. Os módulos não são apenas áreas de interface; eles representam contextos de negócio.

### 5.1 Core Platform
Responsável por identidade, autenticação, autorização, multi-tenant, auditoria, notificações, configuração de ambiente e governança básica.

### 5.2 Master Data Management esportivo
Centraliza cadastro de atletas, staff, equipes, competições, temporadas, arenas e vínculos esportivos.

### 5.3 Training Planning & Session Management
Suporta planejamento de microciclos, sessões, objetivos, presença, restrições e comparação entre planejado e realizado.

### 5.4 Video Capture & Media Processing
Responsável por ingestão, armazenamento, sincronização, clipping, organização e distribuição de vídeo.

### 5.5 Video Analysis & Tagging
Permite tagging manual e semiautomático, playlists, filtros táticos e revisão contextualizada por evento.

### 5.6 Handball Event Scouting
Modela o jogo de handebol em eventos nativos: ataque, defesa, transição, superioridade, inferioridade, zonas, finalizações, ações de goleiro e padrões táticos.

### 5.7 Match Operations Center
É o cockpit de jogo ao vivo, com entrada de eventos, leitura em tempo real, dashboards operacionais e apoio a timeout e intervalo.

### 5.8 Opponent Intelligence
Consolida jogos e padrões do adversário, produz dossiês e playlists para preparação pré-jogo.

### 5.9 Performance Tracking Engine
Captura tracking de atletas e bola, com métricas espaciais e físicas em tempo real e histórico.

### 5.10 Athlete Monitoring & Readiness
Conecta carga, wellness, prontidão, restrições, fadiga e disponibilidade esportiva.

### 5.11 Medical & Recovery
Gerencia indisponibilidade, restrições, evolução clínica-funcional e retorno ao jogo, com controle rigoroso de acesso.

### 5.12 Goalkeeper Intelligence
Especializa a análise de goleiros por zona, tipo de finalização, 7 metros, contra-ataques e sinergia com o sistema defensivo.

### 5.13 Advanced Analytics & BI
Entrega KPIs oficiais, métricas avançadas, comparações, benchmarks e dashboards customizados.

### 5.14 AI Insight Layer
Aplica IA sobre dados, vídeo e eventos para sumarização, recomendação, classificação, busca semântica e apoio à decisão.

### 5.15 Competition & Federation Operations
Suporta ligas e federações na operação de competições, homologação, rankings e dados oficiais.

### 5.16 Media, Broadcast & Digital Products
Expõe live stats, widgets, APIs, minisites, highlights e feeds para mídia e propriedades digitais.

### 5.17 Reporting & Workflow Automation
Automatiza relatórios, alertas, distribuição de clipes, tarefas e rotinas recorrentes.

### 5.18 Data Platform
Sustenta ingestão, lakehouse, event store, time-series, catálogo de dados, semântica e serviços analíticos.

## 6. Capacidades centrais da Hb Track

A Hb Track deve ser capaz de:

- registrar treinos e jogos
- capturar, armazenar e indexar vídeo
- fazer tagging nativo de handebol
- gerar playlists e relatórios
- operar jogo ao vivo
- consolidar scouting técnico-tático
- analisar adversários
- planejar semanas de treino
- monitorar carga e prontidão
- integrar tracking com contexto tático
- gerenciar restrições e disponibilidade
- analisar goleiros com profundidade
- oferecer dashboards por persona
- automatizar relatórios e workflows
- produzir live stats e dados oficiais
- expor APIs, widgets e produtos digitais
- servir como backbone institucional de clubes, ligas e federações

## 7. Personas e perfis de usuário

A Hb Track atende múltiplos perfis, cada um com visão, fluxo e permissões diferentes.

Os principais perfis são:

- super admin da plataforma
- tenant admin
- diretor executivo
- diretor esportivo
- treinador principal
- auxiliar técnico
- analista de desempenho
- analista de vídeo
- scout
- preparador físico
- fisiologista
- fisioterapeuta
- médico
- nutricionista
- coordenador de base
- atleta
- operador de jogo
- oficial de competição
- operador de mídia
- federação/liga admin

O modelo de acesso deve ser híbrido, combinando **RBAC + ABAC + escopo hierárquico**. Em termos práticos, permissão não é apenas “quem é”, mas “quem é, sobre qual recurso, em qual contexto, para qual equipe, em qual temporada, com qual sensibilidade de dado”.

## 8. Princípios de autorização e segurança

A Hb Track deve tratar segurança como parte do produto, não como camada posterior.

Princípios obrigatórios:

- segregação multi-tenant forte
- controle por papel, escopo e contexto
- classificação de dados por sensibilidade
- trilha de auditoria completa
- criptografia em trânsito e em repouso
- masking de dados sensíveis
- acesso médico altamente restrito
- exportação governada por política
- step-up authentication para ações críticas
- observabilidade de acessos e eventos sensíveis

Sugestão de classificação:

- nível 1: público
- nível 2: interno operacional
- nível 3: competitivo confidencial
- nível 4: sensível pessoal
- nível 5: sensível regulado

## 9. Arquitetura de alto nível

A arquitetura da Hb Track deve ser distribuída, orientada a eventos e híbrida entre real-time e batch.

### 9.1 Camadas principais

**Camada de experiência**
Web app, tablet para banco e tribuna, mobile para atletas e staff, portal público e APIs de consumo.

**Camada de orquestração**
BFFs, workflow engine, notification service, rules engine e geração de relatórios.

**Camada de domínio**
Serviços de negócio por contexto: vídeo, scouting, tracking, training planning, match ops, monitoring, analytics, mídia, competição, etc.

**Camada de ingestão**
Entrada de sensores, eventos ao vivo, vídeo, dados históricos e pipelines de enriquecimento.

**Camada de dados**
Banco transacional, event store, time-series store, object storage, lakehouse, search index e cache.

**Camada de inteligência**
Metrics engine, analytics serving, ML/AI platform e semantic query layer.

**Camada de governança**
IAM, auditoria, observabilidade, lineage, backup, monitoramento e políticas.

### 9.2 Estilo arquitetural recomendado

A Hb Track deve seguir:

- domain-driven design
- arquitetura orientada a eventos
- CQRS em áreas críticas de leitura
- event sourcing seletivo em timeline esportiva e auditoria
- storage polyglot
- streaming + batch
- modular monolith evolutivo no início, com serviços separados para tracking, vídeo, ingestão e analytics pesado

### 9.3 Fluxos principais

**Jogo ao vivo**
sensores, console e vídeo entram via ingestão; eventos são sincronizados; dashboards são atualizados; alertas são disparados; live stats são publicados.

**Pós-jogo**
vídeo é processado, métricas são recalculadas, dados vão ao lakehouse, relatórios e playlists são gerados.

**Planejamento semanal**
microciclo é planejado; treino é executado; tracking e vídeo capturam o realizado; sistema compara com o planejado.

**Preparação de adversário**
jogos são ingeridos; padrões são classificados; playlists e dossiês são gerados.

## 10. Casos de uso prioritários

Os casos de uso mais importantes são os que validam a plataforma desde cedo.

### Caso de uso 1 — análise pós-jogo
O analista sobe o vídeo, marca eventos, gera clipes, monta playlists e produz relatório técnico para a comissão.

### Caso de uso 2 — preparação de adversário
O scout analisa jogos anteriores, identifica padrões, monta recortes e gera um dossiê pré-jogo.

### Caso de uso 3 — operação ao vivo
A comissão registra eventos em tempo real, acompanha indicadores de jogo e revisa lances no intervalo.

### Caso de uso 4 — planejamento semanal
O treinador planeja microciclo, associa objetivos, acompanha execução e ajusta a semana com base no jogo anterior.

### Caso de uso 5 — gestão de carga e disponibilidade
O staff físico acompanha carga e readiness; o médico/fisio registra restrições; o treinador consome status funcional sem acessar detalhes clínicos indevidos.

### Caso de uso 6 — live stats e competição
A liga ou federação opera a competição, homologa estatísticas e distribui dados oficiais para mídia e portal público.

## 11. Requisitos funcionais

### 11.1 Requisitos essenciais do núcleo técnico
- cadastro de clubes, equipes, atletas, staff, temporadas e competições
- upload e organização de vídeos
- tagging manual com templates de handebol
- filtros por atleta, zona, fase, sistema e evento
- geração de playlists
- relatórios pós-jogo
- dossiês pré-jogo
- match center básico
- planejamento de microciclos e sessões
- dashboards técnicos

### 11.2 Requisitos essenciais de performance
- captura de tracking
- cálculo de métricas físicas
- carga planejada versus realizada
- prontidão diária
- restrições esportivas
- timeline de disponibilidade

### 11.3 Requisitos essenciais institucionais
- operação de competição
- live stats
- homologação
- rankings
- portal de competição
- APIs para mídia

## 12. Requisitos não funcionais

A Hb Track deve atender requisitos enterprise desde o início.

### 12.1 Desempenho
- baixa latência para dashboards ao vivo
- tempo curto para atualização de eventos e live stats
- tempo controlado para clipping e sincronização
- tempo previsível para geração de relatórios

### 12.2 Escalabilidade
- crescimento por tenant
- crescimento por volume de vídeo
- crescimento por temporada e histórico
- escalabilidade independente para tracking, vídeo e analytics

### 12.3 Disponibilidade
- alta disponibilidade para módulos críticos de jogo
- tolerância a falhas de rede
- buffer local quando necessário
- modo degradado para operação manual

### 12.4 Segurança
- conformidade com LGPD e políticas aplicáveis
- trilha de auditoria
- segregação de dados sensíveis
- rotação de credenciais e gestão segura de segredos

### 12.5 Observabilidade
- logs estruturados
- métricas operacionais
- tracing distribuído
- alertas de falha em pipelines
- monitoramento da cadeia ingestão → processamento → entrega

## 13. Roadmap de produto

## 13.1 MVP
O MVP deve validar o núcleo operacional da comissão técnica.

Inclui:
- core platform
- cadastro mestre
- training planning básico
- vídeo e biblioteca
- tagging e scouting
- match operations básico
- reporting básico
- opponent intelligence básico

O MVP deve provar que a Hb Track substitui 3 a 4 ferramentas e acelera análise pós-jogo e preparação de adversário.

## 13.2 V2
A V2 deve transformar a Hb Track em plataforma integrada de alto rendimento.

Inclui:
- tracking de atletas
- athlete monitoring
- módulo médico-funcional básico
- analytics avançado
- módulo de goleiros
- automação de workflows
- camada inicial de IA

A V2 deve provar que a unificação entre tática, vídeo e físico produz insights superiores aos stacks fragmentados.

## 13.3 V3
A V3 deve escalar a Hb Track para o ecossistema institucional.

Inclui:
- competição e federação
- mídia e broadcast
- APIs e widgets
- portal público de dados
- IA avançada
- benchmarking de mercado
- academy e talent pipeline
- white-label institucional

A V3 deve posicionar a Hb Track como infraestrutura do handebol, não apenas software de clube.

## 14. Métricas de sucesso

### 14.1 Métricas do MVP
- redução do tempo de análise pós-jogo
- redução do tempo de produção de dossiê de adversário
- número de ferramentas substituídas
- frequência de uso por analista e treinador
- número de relatórios e playlists gerados
- taxa de adoção da comissão técnica

### 14.2 Métricas da V2
- adesão de preparadores físicos e staff de saúde
- uso integrado de dashboards físico+tático
- número de alertas acionáveis gerados
- redução de retrabalho entre áreas
- retenção por usuário de alta frequência

### 14.3 Métricas da V3
- número de competições operadas
- volume de dados distribuídos
- uso de APIs e widgets
- número de clubes/federações ativas
- receita institucional
- audiência do produto digital público

## 15. Posicionamento comercial

A Hb Track pode ser empacotada em três ofertas principais.

**Hb Track Coach**
Planejamento, vídeo, scouting, relatórios e adversário.

**Hb Track Performance**
Inclui Coach e adiciona tracking, readiness, carga, recovery e analytics avançado.

**Hb Track League**
Inclui Competition Ops, live stats, APIs, widgets, portal público e distribuição para mídia.

Esse empacotamento facilita adoção progressiva e reduz barreira inicial.

## 16. Diferenciais competitivos

A Hb Track se diferencia não por ter “mais features” isoladas, mas por ter um backbone unificado.

Os principais diferenciais são:

- modelo de dados único para atleta, jogo, treino, evento e vídeo
- unificação nativa entre vídeo, scouting, tracking e performance
- workflows orientados ao handebol, não genéricos
- analytics contextual, não apenas estatística plana
- possibilidade de escalar de clube para federação na mesma plataforma
- substituição estrutural de integrações externas como dependência operacional

## 17. Riscos principais

Os riscos estratégicos e técnicos mais relevantes são:

**Risco de escopo excessivo**
Tentar construir tudo cedo demais e comprometer execução.

**Risco de complexidade arquitetural prematura**
Adotar microserviços e pipelines complexos antes da validação do núcleo.

**Risco de adoção**
Criar uma plataforma completa, mas difícil de usar em ambiente real de staff esportivo.

**Risco de sensibilidade de dados**
Falha na separação entre informação esportiva, biométrica e médica.

**Risco de operação ao vivo**
Baixa confiabilidade em contexto de jogo oficial.

**Risco de modelagem genérica**
Perder especificidade do handebol ao tentar atender muitos segmentos cedo.

## 18. Decisões estratégicas recomendadas

As decisões mais corretas para a Hb Track são:

- começar pelo núcleo vídeo + scouting + operação técnica
- tratar tracking e vídeo como domínios tecnicamente separados desde cedo
- consolidar handebol como vertical profunda antes de expandir horizontalmente
- usar modularidade real no produto e no dado
- adotar governança e segurança enterprise desde o primeiro desenho
- construir IA sobre base semântica sólida, nunca como camada cosmética

## 19. Resumo executivo final

A Hb Track é uma plataforma de handebol end-to-end cujo objetivo é consolidar, em um único sistema, capacidades hoje distribuídas entre soluções de tracking, vídeo, análise, scouting, performance, competição e mídia.

Seu valor central está em eliminar a fragmentação do ecossistema atual e substituir múltiplas ferramentas desconectadas por um backbone único de dados, operação e inteligência.

A jornada recomendada é clara:

- **MVP** para provar utilidade operacional no núcleo técnico
- **V2** para provar superioridade analítica e integração físico-tática
- **V3** para provar escala institucional e dominância de plataforma