A recomendação correta para a Hb Track é: **atores canônicos + permission bundles + roles expandidos formalmente**. Não escolha apenas um desses modelos. Cada um resolve um problema distinto.

Os **atores canônicos** servem para modelagem de produto e linguagem de negócio. Eles respondem à pergunta: “quem usa o sistema e para qual finalidade?”. Exemplos: treinador principal, analista de desempenho, preparador físico, médico, atleta, operador de mídia, administrador de federação. Esses atores são úteis para discovery, UX, fluxos, jornadas, backlog e bounded contexts. Eles não deveriam ser a unidade primária de autorização.

Os **permission bundles** servem para composição de acesso. Eles respondem à pergunta: “quais capacidades esse usuário precisa ter?”. Exemplos: `video_review`, `live_scouting`, `team_readiness_view`, `medical_record_write`, `competition_homologation`, `public_stats_publish`. Esses bundles são a peça mais importante para a implementação, porque evitam rigidez e permitem variações entre clientes, ligas e estruturas organizacionais.

Os **roles expandidos formalmente** servem para governança, compliance, provisionamento e operação. Eles respondem à pergunta: “qual perfil reconhecível a organização quer atribuir a alguém?”. Exemplos: `HEAD_COACH`, `ASSISTANT_COACH`, `PERFORMANCE_ANALYST`, `PHYSIOTHERAPIST`, `LEAGUE_ADMIN`. Eles não devem ser apenas labels visuais; precisam existir formalmente como agregados de bundles, com escopo e políticas associadas.

Então, do ponto de vista arquitetural, a estrutura ideal é esta:

**1. Atores canônicos**
Camada conceitual de produto e UX.

Exemplo:

* Head Coach
* Assistant Coach
* Performance Analyst
* S&C Coach
* Physiotherapist
* Team Doctor
* Athlete
* Match Operator
* League Admin

Uso:

* personas
* jornadas
* telas
* workflows
* documentação funcional

**2. Permission bundles**
Camada principal de autorização reutilizável.

Exemplo:

* `training_plan_manage`
* `team_video_view`
* `team_video_edit`
* `opponent_scouting_view`
* `opponent_scouting_edit`
* `match_live_operate`
* `athlete_monitoring_view`
* `athlete_monitoring_edit`
* `medical_summary_view`
* `medical_record_edit`
* `public_stats_publish`

Uso:

* composição de roles
* customização por tenant
* upgrade de plano
* ativação de módulos
* separação por sensibilidade

**3. Roles formais**
Camada de governança e provisionamento.

Exemplo:

* `HEAD_COACH = training_plan_manage + team_video_view + opponent_scouting_view + match_live_operate + team_readiness_view`
* `PHYSIOTHERAPIST = athlete_monitoring_view + rehab_plan_edit + medical_summary_view + return_to_play_edit`
* `LEAGUE_ADMIN = competition_manage + official_match_validate + public_stats_publish`

Uso:

* onboarding
* administração
* auditoria
* políticas organizacionais
* integração com IAM corporativo

**4. Policies contextuais**
Camada de restrição fina.

Exemplo:

* treinador pode ver readiness, mas não diagnóstico clínico
* atleta só vê seu próprio material
* analista só vê vídeos do time e dos adversários do seu campeonato
* exportação médica exige dupla confirmação
* homologação oficial exige permissão + escopo + estado do jogo

Uso:

* ABAC
* restrições por escopo
* sensibilidade do dado
* contexto operacional

A decisão prática é esta: **não use apenas roles expandidos como fonte primária de autorização**. Isso fica rígido, prolifera perfis e quebra quando surgem exceções. Em plataformas como Hb Track, isso acontece muito rápido. Exemplo: um auxiliar técnico pode precisar operar match center em um clube, mas não em outro; um fisioterapeuta pode ter acesso ao tracking de retorno ao jogo em uma organização e não em outra; uma federação pode querer separar “homologar” de “publicar”.

Se tudo estiver codificado só em roles formais, você cai em explosão combinatória:

* Head Coach Basic
* Head Coach Pro
* Head Coach With Medical Summary
* Head Coach International Competition
* Assistant Coach With Live Ops
* Assistant Coach Without Opponent Scouting

Isso degrada o modelo.

Também não recomendo usar apenas bundles sem roles formais. Isso gera flexibilidade máxima, mas dificulta administração, entendimento humano, auditoria e adoção. O administrador do tenant não quer montar 47 permissões manualmente para cada usuário. Ele quer partir de um perfil reconhecível e ajustar exceções.

Portanto, a resposta objetiva é:

* **sim**, Hb Track deve ter **atores canônicos**
* **sim**, deve ter **permission bundles**
* **sim**, os **roles devem ser formalmente expandidos**
* mas os roles formais devem ser **compostos por bundles**, e não hardcoded diretamente como listas soltas de permissões

A melhor hierarquia é:

**Canonical Actor -> Default Role Template -> Permission Bundles -> Scoped Policies**

Ou, em termos mais operacionais:

```text
Canonical Actor
   ↓
Role Template
   ↓
Permission Bundles
   ↓
Scope Bindings
   ↓
Policy Engine
```

Um exemplo concreto:

```text
Canonical Actor: Head Coach

Default Role Template: HEAD_COACH

Bundles:
- training_plan_manage
- team_video_view
- team_video_edit
- team_scouting_view
- opponent_scouting_view
- match_live_operate
- team_readiness_view

Scopes:
- club=Pinheiros
- team=Adulto Masculino
- season=2026

Policies:
- deny medical_diagnosis_detail
- allow medical_functional_status_summary
- deny export_sensitive_biometric_data
```

Esse desenho é o mais sólido para Hb Track porque suporta:

* produto multi-tenant
* customização por clube/federação
* compliance
* auditoria
* expansão futura sem refatoração dolorosa

Minha recomendação final é esta:

**Formalize os roles, mas não os trate como a menor unidade de segurança.**
A menor unidade de segurança deve ser o bundle ou até a permissão atômica.
O role formal existe para governança, UX administrativa e provisionamento.
O ator canônico existe para produto e modelagem.
A policy existe para controle real.

Abaixo está a definição arquitetural recomendada para o **Hb Track** no nível de identidade, autorização e operação. Vou separar em três blocos formais:

1. **atores canônicos**
2. **permission bundles**
3. **roles expandidos**

A modelagem correta é: os **atores canônicos** representam a linguagem de negócio; os **permission bundles** representam capacidades reutilizáveis; os **roles expandidos** representam perfis provisionáveis, auditáveis e atribuíveis no sistema.

---

# 1. Atores canônicos do Hb Track

Os atores canônicos não são “perfis de acesso” em si. Eles são entidades funcionais do ecossistema do produto. Eles orientam UX, workflows, bounded contexts, ownership de dados e regras de negócio.

## 1.1 Atores de plataforma

### 1. Platform Super Admin

Ator interno do fornecedor Hb Track.

Responsabilidade:

* operar a plataforma global
* administrar tenants
* gerenciar feature flags, licenças e ambientes
* prestar suporte avançado auditado

Escopo:

* multi-tenant global

---

### 2. Tenant Admin

Ator administrador do cliente.

Responsabilidade:

* administrar usuários
* atribuir roles
* configurar equipes, categorias, temporadas, módulos
* controlar parâmetros do tenant

Escopo:

* um clube, federação, liga ou grupo esportivo

---

## 1.2 Atores de gestão esportiva

### 3. Executive Stakeholder

Ator executivo institucional.

Exemplos:

* CEO
* presidente
* diretor geral
* board observer

Responsabilidade:

* consumir informação executiva consolidada
* acompanhar performance institucional e adoção da plataforma

Escopo:

* organização ou grupo de organizações

---

### 4. Sporting Director

Ator de gestão esportiva.

Responsabilidade:

* acompanhar elenco
* tomar decisões esportivas
* avaliar evolução de atletas
* usar inteligência de mercado e benchmarking interno

Escopo:

* clube, categoria, programa esportivo

---

### 5. Technical Coordinator

Ator de coordenação técnica.

Responsabilidade:

* coordenar metodologia
* alinhar base e profissional
* supervisionar staff técnico
* acompanhar desenvolvimento por categoria

Escopo:

* uma ou várias categorias/equipes

---

## 1.3 Atores de comissão técnica

### 6. Head Coach

Responsabilidade:

* comandar treino e jogo
* decidir plano técnico-tático
* consumir e validar análise
* usar dados operacionais de disponibilidade

---

### 7. Assistant Coach

Responsabilidade:

* apoiar preparação de treino e jogo
* revisar vídeo
* colaborar em scouting e operação

---

### 8. Performance Analyst

Responsabilidade:

* produzir análise técnico-tática
* operar scouting
* construir relatórios
* cruzar vídeo, evento e analytics

---

### 9. Video Analyst

Responsabilidade:

* organizar vídeo
* fazer tagging
* gerar clips e playlists
* manter biblioteca audiovisual operacional

---

### 10. Opponent Scout

Responsabilidade:

* analisar adversários
* identificar padrões
* preparar dossiês pré-jogo
* alimentar intelligence library

---

### 11. Goalkeeper Coach

Responsabilidade:

* trabalhar análise específica de goleiros
* preparar relatórios e recortes dedicados
* acompanhar tendência de finalização adversária

---

## 1.4 Atores de performance, saúde e disponibilidade

### 12. Strength & Conditioning Coach

Responsabilidade:

* controlar carga
* ajustar volume/intensidade
* acompanhar readiness e resposta física

---

### 13. Performance Scientist

Responsabilidade:

* modelagem física
* análise longitudinal
* calibração de métricas
* estudos de desempenho e risco

---

### 14. Physiotherapist

Responsabilidade:

* conduzir reabilitação
* gerenciar restrições funcionais
* apoiar retorno ao jogo

---

### 15. Team Doctor

Responsabilidade:

* emitir aptidão
* registrar diagnóstico
* liberar ou restringir participação
* gerir camada clínica formal

---

### 16. Nutritionist

Responsabilidade:

* acompanhar nutrição esportiva
* correlacionar rotina alimentar e performance
* registrar planos e observações autorizadas

---

## 1.5 Atores operacionais e competitivos

### 17. Match Operator

Responsabilidade:

* operar jogo ao vivo
* registrar cronologia e eventos
* controlar inputs operacionais de partida

---

### 18. Competition Official

Exemplos:

* delegado
* oficial de mesa
* supervisor de competição

Responsabilidade:

* validar ou homologar registros oficiais
* acompanhar conformidade operacional da partida

---

### 19. Referee-Linked Official

Ator de suporte institucional ligado à arbitragem.

Responsabilidade:

* consultar evidências e registros oficiais autorizados
* interagir com camada homologatória, não com conteúdo estratégico interno

---

## 1.6 Atores de ecossistema, mídia e distribuição

### 20. Federation Operator

Responsabilidade:

* operar competição
* consolidar estatística oficial
* publicar dados institucionais
* administrar temporadas e fases

---

### 21. League Admin

Responsabilidade:

* governar competição profissional
* homologar publicação
* distribuir dados oficiais
* operar portais e produtos digitais

---

### 22. Media Operator

Responsabilidade:

* consumir e publicar estatísticas públicas
* operar widgets, overlays e highlights liberados

---

### 23. External Partner

Exemplos:

* broadcaster
* patrocinador
* parceiro tecnológico
* consultoria autorizada

Responsabilidade:

* consumir dados ou conteúdo explicitamente compartilhado

---

## 1.7 Atores individuais esportivos

### 24. Athlete

Responsabilidade:

* consumir feedback
* responder wellness
* acompanhar agenda, planos e material compartilhado

Escopo:

* exclusivamente seus próprios dados autorizados

---

### 25. Academy Athlete Guardian Proxy

Ator opcional para categorias menores.

Responsabilidade:

* acompanhar agenda e informações permitidas de atleta de base
* consumir apenas dados autorizados pelo clube/política

---

# 2. Permission Bundles do Hb Track

Os bundles são conjuntos coerentes de capacidades. Eles devem ser a unidade principal de composição dos roles.

A nomenclatura recomendada é consistente, orientada a domínio e sem ambiguidade.

---

## 2.1 Bundles de administração e governança

### `platform_admin_bundle`

Capacidades:

* gerenciar tenants
* feature flags
* licenças
* suporte auditado
* configuração global

---

### `tenant_admin_bundle`

Capacidades:

* gerenciar usuários do tenant
* atribuir roles
* gerenciar equipes, temporadas e módulos
* configurar branding e parâmetros locais

---

### `audit_and_compliance_bundle`

Capacidades:

* visualizar logs
* trilha de auditoria
* revisar exportações sensíveis
* acompanhar acessos críticos

---

## 2.2 Bundles de identidade e organização

### `organization_management_bundle`

Capacidades:

* criar/editar organização
* unidades, categorias, equipes
* calendários e temporadas

---

### `user_access_management_bundle`

Capacidades:

* convidar usuários
* ativar/desativar acesso
* vincular escopos
* atribuir templates de role

---

### `master_data_management_bundle`

Capacidades:

* manter cadastro de atletas
* staff
* competições
* jogos
* arenas
* elenco por temporada

---

## 2.3 Bundles de treino e operação técnica

### `training_plan_view_bundle`

Capacidades:

* visualizar sessões
* agenda
* microciclos
* objetivos de treino

---

### `training_plan_manage_bundle`

Capacidades:

* criar/editar microciclos
* sessões
* objetivos
* observações técnicas

---

### `session_execution_bundle`

Capacidades:

* registrar presença
* execução
* comentários operacionais
* vínculo planejado vs realizado

---

## 2.4 Bundles de vídeo

### `video_library_view_bundle`

Capacidades:

* acessar biblioteca de vídeo
* pesquisar jogos, treinos, clips e playlists

---

### `video_library_manage_bundle`

Capacidades:

* subir vídeos
* organizar acervo
* classificar ativos
* gerenciar metadados

---

### `video_tagging_bundle`

Capacidades:

* marcar eventos
* criar clips
* usar templates de tagging
* comentar lances

---

### `video_playlist_bundle`

Capacidades:

* montar playlists
* compartilhar material interno
* preparar reuniões de vídeo

---

### `video_publish_internal_bundle`

Capacidades:

* publicar material para staff e atletas dentro do tenant

---

### `video_publish_public_bundle`

Capacidades:

* liberar vídeos/clips publicáveis
* aprovar assets públicos

---

## 2.5 Bundles de scouting e análise técnica

### `live_scouting_bundle`

Capacidades:

* operar scouting ao vivo
* registrar eventos em tempo real
* corrigir timeline durante o jogo

---

### `technical_scouting_bundle`

Capacidades:

* classificar ações ofensivas
* defensivas
* transições
* eventos especiais de handebol

---

### `opponent_intelligence_view_bundle`

Capacidades:

* consumir dossiês de adversário
* acessar análise comparativa

---

### `opponent_intelligence_manage_bundle`

Capacidades:

* criar dossiês
* editar observações
* montar análise de adversário
* consolidar padrões

---

### `goalkeeper_analysis_bundle`

Capacidades:

* analisar goleiros
* mapas de arremesso
* relatórios específicos
* tendências de finalização

---

## 2.6 Bundles de analytics e relatórios

### `analytics_basic_view_bundle`

Capacidades:

* visualizar dashboards básicos
* métricas de jogo
* métricas de equipe e atleta

---

### `analytics_advanced_view_bundle`

Capacidades:

* análises contextuais
* comparação por lineup
* filtros avançados
* benchmarks internos

---

### `analytics_authoring_bundle`

Capacidades:

* criar dashboards
* definir indicadores customizados
* construir relatórios analíticos

---

### `reporting_view_bundle`

Capacidades:

* consultar relatórios
* baixar versões autorizadas

---

### `reporting_manage_bundle`

Capacidades:

* gerar relatórios
* editar templates
* programar distribuição interna

---

## 2.7 Bundles de performance física

### `tracking_view_bundle`

Capacidades:

* visualizar tracking
* deslocamentos
* mapas de calor
* carga externa

---

### `tracking_manage_bundle`

Capacidades:

* configurar coleta
* validar ingestão
* recalibrar ou consolidar dados autorizados

---

### `readiness_view_bundle`

Capacidades:

* visualizar prontidão esportiva
* disponibilidade
* risco funcional resumido

---

### `readiness_manage_bundle`

Capacidades:

* registrar wellness
* ajustar thresholds
* validar readiness
* configurar alertas

---

### `load_management_bundle`

Capacidades:

* acompanhar volume, intensidade, carga aguda/crônica
* comparar planejado vs realizado

---

### `performance_science_bundle`

Capacidades:

* análises longitudinais
* modelos de risco
* calibração de zonas e limiares
* estudos por posição e fase

---

## 2.8 Bundles de saúde, recuperação e medicina

### `medical_summary_view_bundle`

Capacidades:

* visualizar status funcional resumido
* restrições esportivas
* aptidão geral

Importante:
não inclui diagnóstico detalhado.

---

### `medical_record_view_bundle`

Capacidades:

* visualizar prontuário clínico detalhado

---

### `medical_record_manage_bundle`

Capacidades:

* criar/editar prontuário
* laudos
* diagnósticos
* liberações
* histórico clínico

---

### `rehab_management_bundle`

Capacidades:

* plano de reabilitação
* evolução funcional
* retorno progressivo
* observações terapêuticas

---

### `availability_decision_support_bundle`

Capacidades:

* emitir status esportivo
* apto / restrito / indisponível
* integrar saúde e performance para decisão operacional

---

## 2.9 Bundles de competição, oficialização e mídia

### `competition_management_bundle`

Capacidades:

* criar competição
* fases
* jogos
* tabela
* parâmetros institucionais

---

### `official_match_validation_bundle`

Capacidades:

* validar cronologia oficial
* revisar inconsistências
* homologar dados da partida

---

### `official_stats_publish_bundle`

Capacidades:

* publicar estatísticas oficiais
* liberar leaderboards e rankings

---

### `media_feed_access_bundle`

Capacidades:

* consumir feeds públicos ou institucionais
* widgets, overlays e live stats autorizados

---

### `media_operations_bundle`

Capacidades:

* operar publicação para mídia
* highlights públicos
* portais públicos
* ativos digitais de competição

---

## 2.10 Bundles de atleta e self-service

### `athlete_self_service_bundle`

Capacidades:

* agenda
* wellness
* materiais compartilhados
* métricas pessoais permitidas
* feedback individual

---

### `athlete_development_view_bundle`

Capacidades:

* visualizar plano de desenvolvimento do atleta
* metas individuais
* clips e relatórios atribuídos

---

## 2.11 Bundles de exportação e compartilhamento

### `data_export_basic_bundle`

Capacidades:

* exportar relatórios e dados não sensíveis

---

### `data_export_sensitive_bundle`

Capacidades:

* exportar dados sensíveis sob política reforçada

---

### `external_sharing_bundle`

Capacidades:

* compartilhar conteúdo com usuários externos autorizados

---

# 3. Roles expandidos do Hb Track

Agora entram os roles formais. Eles são compostos por bundles e serão atribuídos a usuários.

O role expandido deve conter:

* nome formal
* propósito
* bundles padrão
* restrições típicas
* escopo normal esperado

---

## 3.1 Roles de plataforma e administração

### Role: `PLATFORM_SUPER_ADMIN`

Propósito:
administração global da solução.

Bundles:

* `platform_admin_bundle`
* `audit_and_compliance_bundle`

Restrições:

* acesso a conteúdo sensível do cliente apenas sob procedimento auditado
* sem acesso clínico detalhado por default

Escopo:

* global

---

### Role: `TENANT_ADMIN`

Propósito:
administração do cliente.

Bundles:

* `tenant_admin_bundle`
* `organization_management_bundle`
* `user_access_management_bundle`
* `master_data_management_bundle`
* `reporting_view_bundle`

Restrições:

* sem acesso médico detalhado por padrão
* sem homologação oficial, salvo composição adicional

Escopo:

* tenant inteiro ou unidade organizacional

---

## 3.2 Roles executivos e gerenciais

### Role: `EXECUTIVE_VIEWER`

Propósito:
consumo executivo de informação consolidada.

Bundles:

* `analytics_basic_view_bundle`
* `reporting_view_bundle`

Restrições:

* leitura apenas
* sem clínico detalhado
* sem edição operacional

Escopo:

* organização ou grupo

---

### Role: `SPORTING_DIRECTOR`

Propósito:
gestão esportiva e suporte à decisão.

Bundles:

* `analytics_basic_view_bundle`
* `analytics_advanced_view_bundle`
* `reporting_view_bundle`
* `opponent_intelligence_view_bundle`
* `goalkeeper_analysis_bundle`
* `medical_summary_view_bundle`
* `athlete_development_view_bundle`

Restrições:

* sem prontuário clínico detalhado por padrão

Escopo:

* clube, equipe ou programa esportivo

---

### Role: `TECHNICAL_COORDINATOR`

Propósito:
coordenação metodológica e esportiva.

Bundles:

* `training_plan_view_bundle`
* `training_plan_manage_bundle`
* `analytics_basic_view_bundle`
* `reporting_view_bundle`
* `athlete_development_view_bundle`
* `opponent_intelligence_view_bundle`

Escopo:

* múltiplas equipes/categorias

---

## 3.3 Roles de comissão técnica

### Role: `HEAD_COACH`

Propósito:
gestão técnico-tática principal.

Bundles:

* `training_plan_view_bundle`
* `training_plan_manage_bundle`
* `session_execution_bundle`
* `video_library_view_bundle`
* `video_playlist_bundle`
* `technical_scouting_bundle`
* `opponent_intelligence_view_bundle`
* `analytics_basic_view_bundle`
* `reporting_view_bundle`
* `readiness_view_bundle`
* `medical_summary_view_bundle`
* `goalkeeper_analysis_bundle`

Restrições:

* sem `medical_record_view_bundle`
* sem `medical_record_manage_bundle`
* sem exportação sensível por padrão

Escopo:

* equipe/categoria/temporada

---

### Role: `ASSISTANT_COACH`

Propósito:
apoio técnico-tático e operacional.

Bundles:

* `training_plan_view_bundle`
* `session_execution_bundle`
* `video_library_view_bundle`
* `video_tagging_bundle`
* `video_playlist_bundle`
* `technical_scouting_bundle`
* `opponent_intelligence_view_bundle`
* `analytics_basic_view_bundle`
* `readiness_view_bundle`

Restrições:

* geralmente sem poder pleno de aprovação
* escopo reduzido comparado ao head coach

---

### Role: `PERFORMANCE_ANALYST`

Propósito:
produção analítica técnico-tática.

Bundles:

* `video_library_view_bundle`
* `video_library_manage_bundle`
* `video_tagging_bundle`
* `video_playlist_bundle`
* `live_scouting_bundle`
* `technical_scouting_bundle`
* `opponent_intelligence_view_bundle`
* `opponent_intelligence_manage_bundle`
* `analytics_basic_view_bundle`
* `analytics_advanced_view_bundle`
* `analytics_authoring_bundle`
* `reporting_view_bundle`
* `reporting_manage_bundle`
* `goalkeeper_analysis_bundle`

Restrições:

* sem acesso médico detalhado por padrão

---

### Role: `VIDEO_ANALYST`

Propósito:
operação e análise de vídeo.

Bundles:

* `video_library_view_bundle`
* `video_library_manage_bundle`
* `video_tagging_bundle`
* `video_playlist_bundle`
* `video_publish_internal_bundle`
* `reporting_view_bundle`

Restrições:

* sem bundles de saúde e medicina
* analytics mais limitado que o performance analyst

---

### Role: `OPPONENT_SCOUT`

Propósito:
inteligência competitiva de adversários.

Bundles:

* `video_library_view_bundle`
* `video_tagging_bundle`
* `opponent_intelligence_view_bundle`
* `opponent_intelligence_manage_bundle`
* `analytics_basic_view_bundle`
* `reporting_view_bundle`
* `reporting_manage_bundle`

Restrições:

* sem dados médicos
* sem gestão administrativa

---

### Role: `GOALKEEPER_COACH`

Propósito:
gestão analítica e técnica de goleiros.

Bundles:

* `video_library_view_bundle`
* `video_playlist_bundle`
* `goalkeeper_analysis_bundle`
* `analytics_basic_view_bundle`
* `reporting_view_bundle`
* `opponent_intelligence_view_bundle`

Escopo:

* goleiros do time e análise de finalizadores adversários

---

## 3.4 Roles de performance e saúde

### Role: `STRENGTH_AND_CONDITIONING_COACH`

Propósito:
controle físico e carga.

Bundles:

* `training_plan_view_bundle`
* `session_execution_bundle`
* `tracking_view_bundle`
* `readiness_view_bundle`
* `readiness_manage_bundle`
* `load_management_bundle`
* `medical_summary_view_bundle`
* `availability_decision_support_bundle`
* `reporting_view_bundle`

Restrições:

* sem prontuário clínico detalhado

---

### Role: `PERFORMANCE_SCIENTIST`

Propósito:
análise avançada de performance.

Bundles:

* `tracking_view_bundle`
* `tracking_manage_bundle`
* `readiness_view_bundle`
* `load_management_bundle`
* `performance_science_bundle`
* `analytics_advanced_view_bundle`
* `analytics_authoring_bundle`
* `reporting_view_bundle`
* `reporting_manage_bundle`

Restrições:

* visão clínica apenas resumida por padrão

---

### Role: `PHYSIOTHERAPIST`

Propósito:
reabilitação e restrição funcional.

Bundles:

* `medical_summary_view_bundle`
* `rehab_management_bundle`
* `availability_decision_support_bundle`
* `tracking_view_bundle`
* `readiness_view_bundle`
* `reporting_view_bundle`

Opcional por tenant:

* `medical_record_view_bundle`

Restrições:

* se tiver prontuário detalhado, acesso deve ser auditado e escopado por atleta/equipe

---

### Role: `TEAM_DOCTOR`

Propósito:
gestão clínica formal.

Bundles:

* `medical_summary_view_bundle`
* `medical_record_view_bundle`
* `medical_record_manage_bundle`
* `availability_decision_support_bundle`
* `tracking_view_bundle`
* `readiness_view_bundle`
* `reporting_view_bundle`

Restrições:

* exportação sensível controlada
* logging reforçado

---

### Role: `NUTRITIONIST`

Propósito:
suporte nutricional esportivo.

Bundles:

* `athlete_development_view_bundle`
* `medical_summary_view_bundle`
* `reporting_view_bundle`

Opcional:

* `readiness_view_bundle`

Restrições:

* sem prontuário clínico completo por padrão

---

## 3.5 Roles operacionais e institucionais

### Role: `MATCH_OPERATOR`

Propósito:
operação live da partida.

Bundles:

* `live_scouting_bundle`
* `technical_scouting_bundle`
* `reporting_view_bundle`

Restrições:

* acesso estreito e focado em jogo
* sem analytics amplo
* sem saúde e médico

---

### Role: `COMPETITION_OFFICIAL`

Propósito:
validação institucional de jogo.

Bundles:

* `competition_management_bundle`
* `official_match_validation_bundle`
* `reporting_view_bundle`

Restrições:

* sem dados privados do clube
* sem acesso médico
* sem opponent intelligence privado

---

### Role: `FEDERATION_OPERATOR`

Propósito:
operação de federação.

Bundles:

* `competition_management_bundle`
* `official_match_validation_bundle`
* `official_stats_publish_bundle`
* `media_operations_bundle`
* `reporting_view_bundle`
* `analytics_basic_view_bundle`

Restrições:

* sem clínico interno de clube
* sem scouting estratégico privado

---

### Role: `LEAGUE_ADMIN`

Propósito:
administração de liga profissional.

Bundles:

* `competition_management_bundle`
* `official_match_validation_bundle`
* `official_stats_publish_bundle`
* `media_feed_access_bundle`
* `media_operations_bundle`
* `analytics_basic_view_bundle`
* `reporting_view_bundle`

---

### Role: `MEDIA_OPERATOR`

Propósito:
operação de mídia e publicação pública.

Bundles:

* `media_feed_access_bundle`
* `media_operations_bundle`
* `video_publish_public_bundle`
* `reporting_view_bundle`

Restrições:

* sem acesso interno estratégico
* sem dados sensíveis

---

### Role: `EXTERNAL_PARTNER_VIEWER`

Propósito:
consumo externo controlado.

Bundles:

* `reporting_view_bundle`
* `media_feed_access_bundle`

Opcional:

* `external_sharing_bundle`

Restrições:

* leitura somente
* escopo explicitamente compartilhado

---

## 3.6 Roles de atleta

### Role: `ATHLETE`

Propósito:
self-service e desenvolvimento individual.

Bundles:

* `athlete_self_service_bundle`
* `athlete_development_view_bundle`

Restrições:

* apenas próprio escopo
* sem acesso a colegas
* sem analytics coletivos confidenciais

---

### Role: `ACADEMY_GUARDIAN_VIEWER`

Propósito:
responsável autorizado de atleta de base.

Bundles:

* `athlete_self_service_bundle`

Restrições:

* somente materiais explicitamente liberados
* sem dados sensíveis amplos
* sujeito à política de menor de idade

---

# 4. Relação formal entre ator canônico, bundles e role

A estrutura correta do Hb Track deve ser esta:

## Exemplo 1

**Ator canônico:** Head Coach
**Role formal:** `HEAD_COACH`
**Bundles:**

* `training_plan_manage_bundle`
* `video_library_view_bundle`
* `technical_scouting_bundle`
* `opponent_intelligence_view_bundle`
* `readiness_view_bundle`
* `medical_summary_view_bundle`

---

## Exemplo 2

**Ator canônico:** Team Doctor
**Role formal:** `TEAM_DOCTOR`
**Bundles:**

* `medical_record_view_bundle`
* `medical_record_manage_bundle`
* `availability_decision_support_bundle`

---

## Exemplo 3

**Ator canônico:** Federation Operator
**Role formal:** `FEDERATION_OPERATOR`
**Bundles:**

* `competition_management_bundle`
* `official_match_validation_bundle`
* `official_stats_publish_bundle`

---

# 5. Regra arquitetural recomendada

A regra do Hb Track deve ser:

**ator canônico != role != bundle**

Porque:

* **ator canônico** modela o negócio
* **bundle** modela capacidade
* **role** modela provisionamento e governança

Se misturar esses três níveis, o sistema fica rígido e confuso.

---

# 6. Modelo mínimo de dados para implementação

No nível de engenharia de sistema, eu recomendaria estas entidades:

### `CanonicalActor`

Campos:

* `id`
* `code`
* `name`
* `description`
* `domain_family`

### `PermissionBundle`

Campos:

* `id`
* `code`
* `name`
* `description`
* `sensitivity_level`
* `module_family`

### `Permission`

Campos:

* `id`
* `resource`
* `action`
* `condition_schema`

### `RoleTemplate`

Campos:

* `id`
* `code`
* `name`
* `canonical_actor_id`
* `description`
* `is_system_default`

### `RoleBundleAssignment`

Campos:

* `role_id`
* `bundle_id`

### `BundlePermissionAssignment`

Campos:

* `bundle_id`
* `permission_id`

### `UserRoleBinding`

Campos:

* `user_id`
* `role_id`
* `scope_type`
* `scope_id`
* `valid_from`
* `valid_to`

### `PolicyConstraint`

Campos:

* `id`
* `role_id` ou `bundle_id`
* `policy_type`
* `rule_expression`

---

# 7. Recomendação final

Para o Hb Track, a definição formal deve ficar assim:

* **25 atores canônicos** aproximadamente, orientados a negócio
* **25 a 35 permission bundles** organizados por domínio
* **18 a 22 roles expandidos** como templates padrão do sistema

Essa proporção é saudável.
Menos do que isso tende a simplificar demais.
Muito mais do que isso no início tende a gerar overengineering.

A melhor prática é:

* manter os atores estáveis
* permitir evolução moderada dos bundles
* tratar roles como templates versionáveis por tenant


Como arquiteto de software e engenheiro de sistemas do **Hb Track**, eu fecharia as decisões de transmissão e streaming ao vivo como um desenho deliberadamente diferente do mercado atual. O mercado maduro hoje continua dividido em camadas especializadas: Spiideo explicita análise e streaming como produtos adjacentes; Hudl separa captura/livestream de análise; KINEXON se posiciona fortemente em tracking em tempo real; Sportradar se posiciona como backbone de dados ao vivo e APIs. O Hb Track parte de uma premissa diferente: **vídeo, tracking, eventos, carga e distribuição são partes do mesmo sistema operacional do handebol**, e não domínios integrados depois por APIs ou workflow humano. ([Spiideo][1])

A decisão central é esta: no Hb Track, “transmissão” tem dois significados oficiais e simultâneos. O primeiro é **transmissão técnica interna**, para comissão, analistas, banco, tribuna, arbitragem e revisão operacional. O segundo é **transmissão pública/broadcast**, para OTT, TV, portal de competição, app do clube, widgets e parceiros de mídia. O erro do mercado atual é tratar essas duas necessidades como produtos separados ou apenas acoplados. O Hb Track deve tratá-las como **dois pipelines de entrega derivados da mesma ingestão, da mesma linha temporal e do mesmo catálogo semântico de mídia**. Essa decisão responde diretamente ao padrão observado em Spiideo Perform/Play e Hudl TV/Sportscode, mas vai além dele. ([Spiideo][2])

A partir disso, a arquitetura de mídia do Hb Track deve ser organizada em quatro blocos: **capture edge**, **live media core**, **semantic sync layer** e **distribution fabric**. O capture edge resolve confiabilidade na arena; o live media core cuida de ingestão, transcodificação e empacotamento; a semantic sync layer alinha vídeo com tracking, scouting, placar e contexto; e a distribution fabric entrega o mesmo evento para banco, portal, broadcast partner, clipping e APIs. Isso é coerente com a necessidade de backbone temporal único e com o fato de KINEXON já demonstrar, no mercado, que tracking de alta frequência e sincronização com vídeo dependem de infraestrutura temporal precisa. ([KINEXON SPORTS][3])

A primeira decisão explícita é **edge-first capture**. Toda arena relevante deve ter um nó local do Hb Track. Esse edge node recebe câmeras IP, PTZ, panorâmicas, SDI/HDMI via encoder, feeds externos de produtora e eventuais múltiplos ângulos de replay. Ele mantém buffer local, relógio sincronizado, cache operacional e store-and-forward para a nuvem. Isso reduz dependência de conectividade e garante que captura técnica e clipping continuem mesmo com falhas de uplink. Essa escolha se alinha ao que o mercado já sugere em soluções físicas de captura e tracking — como a infraestrutura de arena da Spiideo e a rede de sensores/antenas da KINEXON — mas no Hb Track ela vira requisito de plataforma, não só atributo de um módulo. ([Spiideo][4])

A segunda decisão é **um relógio lógico único da partida**. Toda captura de vídeo, evento de scouting, dado de tracking, estado do placar e métrica de carga precisa ser associada a um mesmo eixo temporal canônico. No mercado, KINEXON publicamente enfatiza sincronização frame-perfect entre toque na bola e vídeo; isso mostra que o estado da arte já reconhece o valor operacional da precisão temporal. O Hb Track deve generalizar essa precisão para tudo: cada frame de vídeo, cada evento técnico, cada métrica física e cada atualização de live stats deve ser endereçável pelo mesmo timecode lógico do jogo. ([KINEXON SPORTS][3])

A terceira decisão é **dual pipeline de mídia**, mas não dual platform. Ou seja: uma ingestão só, dois pipelines de saída. O pipeline técnico interno prioriza baixa latência, scrubbing rápido, clipping quase em tempo real, timeline navegável, correlação com tracking e busca semântica. O pipeline público prioriza escala, compatibilidade, ABR, entrega por CDN, segurança de distribuição e eventual monetização. Essa distinção é necessária porque o uso do banco e o uso do fã têm requisitos diferentes; é também a principal divergência arquitetural do Hb Track em relação ao mercado, onde a separação costuma ocorrer por produto. Spiideo e Hudl mostram essa separação na oferta; o Hb Track a traz para dentro de um mesmo core de mídia. ([Spiideo][1])

Em captura, o Hb Track deve suportar quatro modos operacionais. O primeiro é **single panoramic acquisition**, útil para análise de treino e categorias com menor orçamento. O segundo é **auto-follow multi-zone**, para jogos e treinos com automação de enquadramento. O terceiro é **multi-angle analysis**, com câmera tática, câmera lateral, câmera de goleiro e feed broadcast. O quarto é **broadcast ingest mode**, em que o Hb Track recebe um feed principal de uma produtora ou TV e o reinjeta no backbone temporal da plataforma. Isso permite que clubes, federações e ligas usem a mesma plataforma em cenários simples ou premium, sem quebrar o modelo de dados. A aderência dessa decisão ao mercado aparece claramente em Spiideo, que já vende captura automatizada, AutoFollow e streaming em handebol, enquanto Hudl e KINEXON cobrem outras partes do fluxo. ([Spiideo][4])

Na codificação, eu tomaria uma decisão de engenharia simples e robusta: **preservar um mezzanine interno e gerar derivados especializados**. O mezzanine serve como fonte canônica de qualidade para clipping, replay, auditoria, highlights e reprocessamento. A partir dele, o sistema gera proxies de baixa latência para uso técnico, perfis ABR para distribuição pública, assets recortados para playlists e cópias otimizadas para machine vision e indexação. O benefício é eliminar reencodes desnecessários e permitir que o mesmo momento de jogo exista em versões diferentes sem perder coerência semântica. Essa decisão é mais forte que o padrão público observado nos players do mercado, porque transforma o vídeo em ativo estruturado de plataforma. ([Spiideo][1])

Para o **pipeline técnico interno**, eu adotaria uma codificação com GOP curto, proxies de navegação, indexação temporal agressiva e publicação em latência baixa o suficiente para uso em timeout, intervalo e revisão imediata. A prioridade aqui não é “perfeição visual de OTT”, e sim navegabilidade operacional, sincronização precisa e disponibilidade de clip em segundos. Esse pipeline deve alimentar o player técnico do Hb Track, o console de análise, o banco e a tribuna. O mercado já mostra a importância disso: Hudl Sportscode explicitamente passou a suportar streaming da captura ao vivo para análise distribuída, e Spiideo Perform se apresenta como plataforma de análise ao vivo em nuvem. O Hb Track internaliza isso, mas ligando o stream ao contexto semântico do handebol. ([Spiideo][1])

Para o **pipeline público**, eu adotaria empacotamento adaptativo para web e mobile, distribuição por CDN, tokenização de acesso, geofencing opcional, DRM quando a federação ou a liga exigirem, e duas modalidades de saída: stream com overlays Hb Track e feed limpo para parceiros. A camada de broadcast também deve permitir geração de highlights em tempo quase real, publicação de clips sociais e alimentação de widgets de live stats. Essa decisão conversa diretamente com a realidade do mercado: Spiideo Play já enfatiza produção e distribuição de live sport com suporte em nuvem, enquanto Hudl TV se posiciona como plataforma simples de livestreaming esportivo. O diferencial do Hb Track é que os overlays e os eventos de mídia saem do mesmo backbone que produz o scouting e o tracking, não de uma integração posterior. ([Spiideo][2])

A camada de distribuição deve ser **multi-destino por design**. Os destinos mínimos são: player técnico interno, player público/OTT, feed para parceiros de broadcast, APIs para mídia/dados, repositório de clipes e distribuição para atletas e staff. Cada destino consome a mesma entidade “match media session”, mas com perfis diferentes de autorização, latência, bitrate, watermark, overlays e retenção. Isso resolve um problema recorrente do mercado modular: o mesmo jogo costuma ser replicado em várias ferramentas, cada uma com permissões e metadados próprios. No Hb Track, a entidade jogo e a entidade sessão de mídia são únicas; o que muda é a política de entrega. A necessidade de uma camada robusta de distribuição de dados para mídia é confirmada pelo posicionamento de Sportradar em APIs de esporte e pelo seu Handball API com cobertura ampla e live scoring. ([Sportradar Marketplace][5])

A grande decisão diferencial do Hb Track é tratar **vídeo como dado semântico**, não apenas como stream. Cada segmento de vídeo precisa poder responder perguntas como: qual o atleta envolvido, qual a zona da quadra, qual o contexto numérico, qual o sistema defensivo enfrentado, qual a carga acumulada do atleta naquele momento, qual o placar, qual a probabilidade histórica de conversão daquela ação e quais clips semelhantes existem no acervo. Isso exige que o pipeline de mídia publique eventos de domínio para a camada analítica, e que tracking, scouting e vídeo convirjam em um grafo semântico da partida. O mercado atual já sugere partes disso — Handball.ai em busca de eventos e clips, KINEXON em sincronização com tracking, Spiideo em análise + streaming — mas não de forma unificada em uma plataforma handebol-first cobrindo clube, federação e mídia ao mesmo tempo. ([Spiideo][1])

Em termos de fluxo operacional, eu padronizaria quatro jornadas. A primeira é **match live ops**: câmera/encoder → edge node → ingest gateway → sync layer → publish técnico → clip automático → dashboard do banco. A segunda é **broadcast live**: mesma ingestão → transcode ABR → adição de overlays → distribuição por CDN → apps e portais. A terceira é **analytics enrichment**: tracking + scouting + vídeo → semantic join → motor analítico → índices consultáveis e playlists. A quarta é **post-match industrialization**: o mezzanine consolidado alimenta reprocessamento, highlights, assets de mídia, dossiê técnico e benchmarking. O mercado atual normalmente reparte essas jornadas entre empresas diferentes; o Hb Track precisa assumi-las como um fluxo único de plataforma. ([Spiideo][1])

Do ponto de vista de software, eu não concentraria tudo em um único serviço de vídeo. Eu separaria pelo menos estes componentes: **Ingest Service**, **Edge Agent**, **Sync Service**, **Transcode Service**, **Media Catalog**, **Clip Orchestrator**, **Playback Gateway**, **Broadcast Packager**, **Rights & Access Service** e **Semantic Linking Service**. O mercado modular chegou a algo parecido por necessidade de especialização, só que dividido entre fornecedores; o Hb Track faria isso dentro de casa, preservando um modelo comum de dados e uma trilha temporal única. Isso é a resposta arquitetural correta ao contraste entre “plataforma unificada” e “ecossistema best-of-breed”. ([Spiideo][1])

Para confiabilidade, as decisões devem ser conservadoras: buffer local obrigatório, retry idempotente de upload, detecção de perda de sinal, fallback para modo degrado sem internet, reidratação de sessões após reconnect, observabilidade da latência ponta a ponta e alarmes separados para captura, sincronização, transcoding e distribuição. Em jogo oficial, o sistema não pode falhar silenciosamente. A arena precisa continuar capturando mesmo que a nuvem ou a CDN sofram degradação. Essa exigência é coerente com o caráter mission-critical de tracking ao vivo, que a KINEXON enfatiza com transmissão UWB de alta frequência e uso em decisão em tempo real. ([KINEXON SPORTS][3])

Em segurança e direitos, eu definiria quatro níveis de exposição: **private technical**, **restricted team**, **institutional federation/media** e **public fan-facing**. O mesmo vídeo pode existir em quatro superfícies com políticas distintas de watermark, download, clipping, redistribuição e retenção. Essa segmentação não é detalhe; ela é necessária porque o Hb Track atende clube, federação e mídia no mesmo core. O mercado atual costuma resolver isso com sistemas distintos por público; no Hb Track isso deve ser controlado nativamente na camada de rights/access. A relevância de uma arquitetura forte de distribuição institucional é reforçada pelo posicionamento de Sportradar como provedor de dados para múltiplos contextos de consumo. ([Sportradar Marketplace][5])

A decisão final de arquitetura, portanto, é esta: **o Hb Track não terá um módulo de streaming; terá uma plataforma de mídia em tempo real integrada ao sistema esportivo**. Captura, codificação, clipping, análise técnica, tracking, workload e broadcast público nascem da mesma sessão de jogo. Isso é exatamente o que diferencia o Hb Track do mercado atual: enquanto o mercado continua excelente, porém modular, o Hb Track deve ser concebido como um **media-and-performance operating system para handebol**, em que toda transmissão ao vivo é simultaneamente um ativo técnico, analítico, institucional e de mídia. ([Spiideo][1])

[1]: https://www.spiideo.com/spiideo-perform/?utm_source=chatgpt.com "Spiideo Perform"
[2]: https://www.spiideo.com/spiideo-play/?utm_source=chatgpt.com "Spiideo Play"
[3]: https://kinexon-sports.com/technology/ball-tracking?utm_source=chatgpt.com "Experience Live Handball and Football Tracking"
[4]: https://www.spiideo.com/handball-video-analysis-software/?utm_source=chatgpt.com "Handball"
[5]: https://marketplace.sportradar.com/products/652fc0fe3bc9b0cb71d1dc67?utm_source=chatgpt.com "Handball API"

Abaixo está a especificação técnica de alto nível para o subsistema de vídeo ao vivo do **Hb Track**.

## 1. Objetivo do subsistema

O subsistema de vídeo ao vivo do Hb Track existe para cumprir quatro funções ao mesmo tempo:

operar a revisão técnica em tempo real, transmitir ao público, alimentar analytics e preservar um acervo semântico pesquisável.

Em termos de engenharia, isso significa que o vídeo não é tratado como mídia isolada. Ele é tratado como uma entidade central do domínio esportivo, sincronizada com:

* relógio oficial da partida
* tracking de atletas e bola
* eventos de scouting
* placar e estado do jogo
* contexto físico e de carga
* metadados de competição, equipe, atleta e staff

## 2. Escopo funcional

O subsistema cobre:

* captura ao vivo na arena
* ingestão de feeds externos
* sincronização temporal
* codificação e transcodificação
* empacotamento para múltiplos destinos
* clipping automático e manual
* distribuição técnica interna
* distribuição pública/broadcast
* indexação semântica
* recuperação por evento e contexto
* arquivamento e reprocessamento

Não cobre, como responsabilidade primária:

* edição editorial complexa de pós-produção
* produção televisiva completa com switcher de estúdio
* CDN própria global de varejo
* monetização OTT avançada de assinatura como domínio de negócio separado

Esses pontos podem existir como extensões, mas não são o core inicial.

## 3. Requisitos arquiteturais

O desenho do sistema deve obedecer a estes requisitos.

**R1. Backbone temporal único**
Toda entidade audiovisual precisa ser referenciada por um tempo canônico da partida.

**R2. Captura resiliente em edge**
A captura deve continuar operando mesmo com conectividade degradada.

**R3. Dual pipeline**
O sistema deve produzir simultaneamente saídas para uso técnico e para uso público.

**R4. Vídeo como dado semântico**
Cada segmento deve ser pesquisável por contexto esportivo, não apenas por timestamp.

**R5. Multi-tenant enterprise**
Clubes, federações, ligas e mídia precisam coexistir com segregação forte.

**R6. Latência operacional baixa**
O staff precisa revisar eventos poucos segundos após ocorrerem.

**R7. Reprocessamento histórico**
O sistema deve suportar recalcular índices, highlights e classificações após a partida.

**R8. Direitos e acesso por perfil**
O mesmo vídeo pode ter superfícies e permissões diferentes.

## 4. Modelo de implantação

A arquitetura física recomendada é híbrida:

* **arena edge**
* **core cloud**
* **distribution/CDN layer**

### 4.1 Arena edge

Na arena, há um **Hb Track Edge Node**.

Funções:

* receber sinais de câmera
* capturar feeds locais
* bufferizar mídia
* manter relógio local sincronizado
* gerar proxies iniciais
* empacotar stream técnico local
* garantir store-and-forward
* suportar clipping mesmo sem uplink perfeito

### 4.2 Core cloud

Na nuvem, ficam os serviços persistentes e distribuídos:

* catálogo de mídia
* sincronização semântica
* transcodificação pesada
* storage central
* distribuição autenticada
* analytics
* IA
* geração de relatórios
* APIs

### 4.3 Distribution layer

A camada de distribuição usa:

* entrega autenticada para usuários internos
* empacotamento OTT para consumo público
* saídas para parceiros e mídia
* integração com CDN

## 5. Componentes principais

### 5.1 Edge Agent

Agente executado no nó local.

Responsabilidades:

* discovery de fontes de vídeo
* health check das entradas
* captura local
* buffering
* sincronização inicial com relógio da partida
* envio de heartbeats
* reenvio em caso de falha
* cache de metadata operacional

Interfaces principais:

* recebe configuração da sessão
* publica estado do dispositivo
* envia chunks ou segmentos de mídia
* envia telemetria operacional

### 5.2 Ingest Service

Serviço central de entrada de mídia.

Responsabilidades:

* registrar novas sessões de captura
* validar origem
* aceitar streams ao vivo
* aceitar uploads pós-evento
* associar feed a partida, câmera, ângulo e organização
* emitir eventos de domínio de início/fim de ingestão

### 5.3 Time Sync Service

Serviço central de sincronização temporal.

Responsabilidades:

* manter relógio lógico da partida
* alinhar vídeo, tracking, scouting e placar
* corrigir drift
* atribuir timecode canônico
* resolver discrepâncias entre fontes

Esse é um dos serviços mais críticos da plataforma.

### 5.4 Transcode Service

Serviço de codificação e derivação de mídia.

Responsabilidades:

* gerar proxy técnico
* gerar mezzanine persistente
* gerar ladder ABR público
* extrair thumbnails
* gerar assets de clipping
* preparar material para visão computacional

### 5.5 Media Catalog Service

Catálogo central dos ativos.

Responsabilidades:

* registrar assets
* versionar mídia
* relacionar asset com sessão, jogo, atleta, evento e competição
* armazenar metadados técnicos e semânticos
* controlar retenção

### 5.6 Clip Orchestrator

Serviço de geração de recortes.

Responsabilidades:

* criar clipes por tag manual
* criar clipes por evento detectado
* compor playlists
* gerar highlights automáticos
* publicar recortes para destinos autorizados

### 5.7 Playback Gateway

Camada de entrega de mídia para consumidores internos.

Responsabilidades:

* autenticação
* autorização
* entrega de manifestos ou URLs assinadas
* seleção de perfil de reprodução
* watermarking quando necessário
* auditoria de acesso

### 5.8 Broadcast Packager

Serviço orientado à saída pública.

Responsabilidades:

* empacotamento de stream público
* composição de overlays
* geração de feed limpo e feed enriquecido
* emissão para OTT, portal e parceiros
* integração com distribuição externa

### 5.9 Semantic Linking Service

Serviço que conecta vídeo ao domínio esportivo.

Responsabilidades:

* ligar segmentos de vídeo a eventos, zonas, atletas e contexto
* indexar clips por posse, sistema, situação numérica e carga
* servir consultas semânticas
* enriquecer mídia com inferências de analytics e IA

### 5.10 Rights & Policy Service

Camada de direitos.

Responsabilidades:

* política por tenant
* política por tipo de ativo
* regras de download, clipping, retenção e compartilhamento
* controle por perfil de usuário
* geofencing e restrições comerciais quando aplicável

## 6. Componentes auxiliares

Além dos serviços centrais, o sistema precisa de:

* message broker / event bus
* object storage
* time-series store para telemetria operacional
* banco transacional para catálogo e política
* search index
* observabilidade central
* secrets/config service
* rules engine
* notification service

## 7. Fluxos principais

### 7.1 Fluxo de captura ao vivo

1. a sessão de jogo é criada
2. o Edge Agent recebe configuração
3. as fontes de vídeo são descobertas ou associadas
4. o Edge Agent inicia captura
5. o Ingest Service registra a sessão
6. o Time Sync Service cria o relógio lógico
7. segmentos ou chunks passam a ser enviados
8. o Media Catalog registra o ativo
9. o Transcode Service gera derivados
10. o Playback Gateway disponibiliza para uso técnico
11. o Broadcast Packager publica para uso público, se habilitado

### 7.2 Fluxo de clipping automático

1. ocorre evento de scouting ou detecção automática
2. o evento recebe timestamp canônico
3. o Semantic Linking Service localiza janela de vídeo
4. o Clip Orchestrator cria recorte
5. o Media Catalog registra o clip
6. o clip é publicado em playlist, dashboard ou surface pública autorizada

### 7.3 Fluxo de revisão técnica em tempo real

1. o analista abre a partida
2. o Playback Gateway entrega o stream técnico
3. a timeline mostra tags, tracking, placar e carga
4. o usuário seleciona um evento
5. o player busca o trecho correspondente
6. o usuário comenta, recorta ou adiciona à playlist

### 7.4 Fluxo de broadcast público

1. a sessão pública é ativada
2. o Broadcast Packager gera perfis públicos
3. overlays e dados oficiais são compostos
4. o stream é entregue ao destino configurado
5. métricas de audiência e qualidade são coletadas
6. eventos importantes podem disparar geração de highlights

## 8. APIs principais

A especificação abaixo é conceitual. Não é sintaxe final.

### 8.1 Session API

Cria e administra sessões de mídia.

Exemplos de operações:

* criar sessão
* iniciar sessão
* encerrar sessão
* listar sessões de uma partida
* associar câmera a sessão

Entidades:

* `match_id`
* `session_id`
* `camera_id`
* `angle_type`
* `tenant_id`

### 8.2 Ingest API

Recebe mídia ou metadados de ingestão.

Operações:

* registrar feed
* publicar heartbeat
* reportar falha
* enviar fragmento/segmento
* finalizar ingestão

### 8.3 Sync API

Expõe relógio e marcações temporais.

Operações:

* obter relógio atual da partida
* registrar offset
* corrigir drift
* mapear timestamp local para timestamp canônico

### 8.4 Clip API

Opera clips e playlists.

Operações:

* criar clip
* buscar clip por evento
* gerar playlist
* anexar comentário
* publicar clip

### 8.5 Playback API

Entrega manifests e autorizações.

Operações:

* obter URL assinada
* obter stream técnico
* obter stream público
* obter asset por política de acesso

### 8.6 Semantic Query API

Busca vídeo por contexto esportivo.

Operações:

* buscar eventos por atleta
* buscar clips por sistema
* buscar posses por contexto numérico
* buscar arremessos por zona
* buscar lances correlacionados com carga

Exemplo conceitual:
“traga todos os contra-ataques do ponta direita no segundo tempo, com FC acima do limiar e finalização na zona 2”.

## 9. Eventos de domínio

O backbone do Hb Track deve ser orientado a eventos. Alguns eventos fundamentais:

* `media.session.created`
* `media.session.started`
* `media.session.ended`
* `media.feed.connected`
* `media.feed.disconnected`
* `media.segment.received`
* `media.asset.created`
* `media.asset.transcoded`
* `media.proxy.ready`
* `media.clip.created`
* `media.highlight.generated`
* `media.playback.authorized`
* `media.broadcast.started`
* `media.broadcast.failed`
* `match.clock.updated`
* `match.event.recorded`
* `tracking.sample.ingested`
* `semantic.link.created`
* `rights.policy.changed`

Esses eventos permitem desacoplamento entre captura, vídeo, scouting, analytics e distribuição.

## 10. Modelo de dados principal

### 10.1 Entidade MatchMediaSession

Campos principais:

* session_id
* tenant_id
* match_id
* session_type
* source_type
* start_time
* end_time
* sync_state
* ingest_state
* broadcast_state

### 10.2 Entidade MediaAsset

Campos:

* asset_id
* parent_asset_id
* asset_type
* storage_uri
* codec_profile
* resolution
* duration_ms
* created_from_session_id
* retention_policy_id

### 10.3 Entidade MediaReference

Campos:

* reference_id
* asset_id
* canonical_start_ms
* canonical_end_ms
* linked_event_id
* linked_athlete_ids
* linked_team_id
* zone_id
* tactical_context
* score_context
* load_context

### 10.4 Entidade Clip

Campos:

* clip_id
* source_asset_id
* start_ms
* end_ms
* creation_reason
* created_by
* semantic_tags
* publication_targets

## 11. Perfis de saída

### 11.1 Saída técnica

Uso:

* staff
* banco
* analistas
* atletas em revisão

Características:

* baixa latência
* proxies rápidos
* timeline navegável
* overlays técnicos opcionais
* multi-angle se disponível

### 11.2 Saída institucional

Uso:

* federação
* liga
* arbitragem
* parceiros autorizados

Características:

* qualidade estável
* acesso controlado
* metadata oficial
* retenção maior
* export auditável

### 11.3 Saída pública

Uso:

* fãs
* portal
* app
* OTT

Características:

* ABR
* grande escala
* baixa fricção
* overlays de placar e dados
* controle comercial

### 11.4 Saída de parceiro

Uso:

* TV
* mídia
* integradores

Características:

* feed limpo ou enriquecido
* APIs paralelas
* contratos de direitos
* políticas específicas por competição

## 12. Requisitos não funcionais

### 12.1 Latência

Metas recomendadas:

* revisão técnica: poucos segundos
* clipping automático: segundos a dezenas de segundos
* stream público: estável com latência controlada
* publicação de highlights: minutos ou menos para eventos simples

### 12.2 Disponibilidade

Componentes críticos:

* Edge Agent
* Ingest Service
* Time Sync Service
* Playback Gateway
* Broadcast Packager

Esses precisam de alta disponibilidade e recuperação rápida.

### 12.3 Durabilidade

* assets críticos devem ter persistência redundante
* store-and-forward deve suportar desconexão temporária
* eventos de domínio devem ser idempotentes

### 12.4 Segurança

* autenticação forte
* autorização por recurso
* criptografia em trânsito e em repouso
* trilha de auditoria
* segregação multi-tenant
* masking para superfícies não autorizadas

### 12.5 Observabilidade

Métricas mínimas:

* ingest bitrate
* packet loss / frame drop
* transcode latency
* sync drift
* clip generation time
* playback errors
* CDN egress health
* edge disk pressure
* reconnect frequency

## 13. Decisões de engenharia por contraste com o mercado

Em relação ao mercado modular atual, o Hb Track toma decisões específicas.

O mercado costuma separar análise técnica e streaming público em produtos diferentes. O Hb Track unifica ingestão e semântica, separando apenas a entrega.

O mercado trata vídeo, tracking e dados como domínios integráveis. O Hb Track trata esses elementos como manifestações diferentes do mesmo evento esportivo.

O mercado frequentemente opera com sincronizações parciais ou por importação. O Hb Track exige sincronização canônica de tempo.

O mercado frequentemente entrega vídeo como arquivo ou stream anotado. O Hb Track entrega vídeo como entidade semântica consultável.

O mercado costuma resolver mídia, scouting e dados com fornecedores especializados. O Hb Track resolve isso com uma plataforma multi-domínio handebol-first.

## 14. Caminho de implementação

### Fase 1

* Edge Agent
* Ingest Service
* Playback técnico
* Media Catalog
* Clip manual
* Sync básico com scouting
* stream público simples

### Fase 2

* Broadcast Packager completo
* semantic linking
* clipping automático
* integração com tracking
* playlists e highlights

### Fase 3

* query semântica avançada
* enriquecimento por IA
* multi-angle avançado
* overlays dinâmicos por contexto
* distribuição institucional completa

## 15. Formulação final

A decisão final de arquitetura é esta:

o Hb Track deve ser construído como uma **plataforma de mídia esportiva em tempo real, semanticamente integrada ao motor esportivo**, e não como um “módulo de streaming”.

Isso implica:

* captura resiliente em edge
* relógio único da partida
* ingestão única com saídas múltiplas
* vídeo tratado como dado de domínio
* clipping, análise, broadcast e analytics derivados da mesma sessão
* políticas nativas para clube, federação e mídia

Abaixo está o **diagrama C4 do Hb Track** em formato textual, organizado nos níveis mais úteis para arquitetura: **Contexto (L1)**, **Containers (L2)** e **Componentes do subsistema de vídeo ao vivo (L3)**.

## C4 — Nível 1: Contexto do Sistema

```text
System Context - Hb Track

[Comissão Técnica] --------------------------\
[Analista de Desempenho] -------------------- \
[Preparador Físico / Performance] ------------ > [Hb Track]
[Departamento Médico] ----------------------- /
[Atletas] ----------------------------------/
[Diretor Esportivo] ------------------------/
[Federação / Liga] ------------------------/
[Parceiros de Mídia / Broadcast] ----------/
[Fãs / Público] ---------------------------/

[Hb Track] --> [Plataformas OTT / CDN]
[Hb Track] --> [Parceiros de Broadcast]
[Hb Track] --> [Apps / Sites de Clubes e Ligas]
[Hb Track] --> [Dispositivos de Captura / Edge Nodes]
[Hb Track] --> [Sensores de Tracking de Atletas e Bola]
```

### Interpretação

O Hb Track é o sistema central que atende:

* operação esportiva interna
* análise técnica e tática
* monitoramento físico
* operação de competição
* mídia e transmissão pública

Diferente do mercado fragmentado, ele centraliza vídeo, tracking, scouting, carga, analytics e distribuição.

---

## C4 — Nível 2: Containers

```text
Container Diagram - Hb Track

Users
-----
[Coaches / Analysts / Staff / Athletes / Federation / Media / Fans]

Primary Containers
------------------
[Web App]
[Tablet App - Match Ops]
[Mobile App]
[Public Portal / OTT Experience]

Application / Access Layer
--------------------------
[API Gateway / BFF Layer]

Core Domain Containers
----------------------
[Core Platform Service]
[Match Operations Service]
[Training & Planning Service]
[Scouting Service]
[Tracking Service]
[Athlete Monitoring Service]
[Medical & Recovery Service]
[Opponent Intelligence Service]
[Analytics & BI Service]
[Media Management Service]
[Broadcast & Distribution Service]
[Rights & Policy Service]
[Notification & Workflow Service]

Data / Platform Containers
--------------------------
[Event Bus]
[Operational Database]
[Event Store]
[Time-Series Store]
[Object Storage]
[Lakehouse / Analytical Store]
[Search Index]
[Observability Stack]

Edge / Field Containers
-----------------------
[Hb Track Edge Node]
[Capture Sources: IP Cameras / PTZ / SDI Encoders]
[Tracking Hardware / Sensors]
[Local Operator Console]

External Containers
-------------------
[CDN / OTT Delivery]
[Broadcast Partners]
[External Club / League Apps]
```

### Relações principais

```text
[Web App] --> [API Gateway / BFF Layer]
[Tablet App - Match Ops] --> [API Gateway / BFF Layer]
[Mobile App] --> [API Gateway / BFF Layer]
[Public Portal / OTT Experience] --> [API Gateway / BFF Layer]

[API Gateway / BFF Layer] --> [Core Platform Service]
[API Gateway / BFF Layer] --> [Match Operations Service]
[API Gateway / BFF Layer] --> [Scouting Service]
[API Gateway / BFF Layer] --> [Tracking Service]
[API Gateway / BFF Layer] --> [Athlete Monitoring Service]
[API Gateway / BFF Layer] --> [Analytics & BI Service]
[API Gateway / BFF Layer] --> [Media Management Service]
[API Gateway / BFF Layer] --> [Broadcast & Distribution Service]
[API Gateway / BFF Layer] --> [Rights & Policy Service]

[Hb Track Edge Node] --> [Media Management Service]
[Hb Track Edge Node] --> [Match Operations Service]
[Hb Track Edge Node] --> [Event Bus]

[Capture Sources] --> [Hb Track Edge Node]
[Tracking Hardware / Sensors] --> [Tracking Service]
[Local Operator Console] --> [Scouting Service]

[Scouting Service] --> [Event Bus]
[Tracking Service] --> [Event Bus]
[Match Operations Service] --> [Event Bus]
[Media Management Service] --> [Event Bus]

[Core Platform Service] --> [Operational Database]
[Match Operations Service] --> [Operational Database]
[Training & Planning Service] --> [Operational Database]
[Medical & Recovery Service] --> [Operational Database]

[Scouting Service] --> [Event Store]
[Match Operations Service] --> [Event Store]
[Tracking Service] --> [Time-Series Store]
[Media Management Service] --> [Object Storage]
[Analytics & BI Service] --> [Lakehouse / Analytical Store]
[Analytics & BI Service] --> [Search Index]

[Broadcast & Distribution Service] --> [CDN / OTT Delivery]
[Broadcast & Distribution Service] --> [Broadcast Partners]
[Broadcast & Distribution Service] --> [External Club / League Apps]
```

### Leitura arquitetural

No nível L2, o Hb Track se divide em:

* interfaces de usuário
* serviços de domínio
* plataforma de dados
* edge na arena
* distribuição externa

O ponto mais importante é que **Media Management**, **Tracking**, **Scouting** e **Match Operations** compartilham o **Event Bus** e convergem em um backbone temporal e semântico único.

---

## C4 — Nível 3: Componentes do container “Media Management Service”

Esse é o nível mais importante para o subsistema de vídeo ao vivo.

```text
Component Diagram - Media Management Service

[Hb Track Edge Node]
    |
    v
[Ingest API]
    |
    +--> [Session Manager]
    +--> [Source Registry]
    +--> [Ingest Validator]
    |
    v
[Time Sync Engine]
    |
    +--> [Canonical Match Clock Adapter]
    +--> [Drift Correction]
    +--> [Timestamp Mapper]
    |
    v
[Transcode Orchestrator]
    |
    +--> [Proxy Generator]
    +--> [Mezzanine Encoder]
    +--> [ABR Packager]
    +--> [Thumbnail Extractor]
    |
    v
[Media Catalog]
    |
    +--> [Asset Registry]
    +--> [Metadata Store Adapter]
    +--> [Retention Manager]
    |
    +--> [Semantic Linking Adapter] <--> [Semantic Linking Service]
    |
    v
[Clip Orchestrator]
    |
    +--> [Manual Clip Builder]
    +--> [Auto Clip Builder]
    +--> [Playlist Builder]
    +--> [Highlight Generator]
    |
    v
[Playback Gateway]
    |
    +--> [Signed URL Issuer]
    +--> [Access Policy Checker] <--> [Rights & Policy Service]
    +--> [Technical Stream Delivery]
    +--> [Internal Watermarking]
    |
    v
[Broadcast Output Adapter]
    |
    +--> [Public Stream Publisher]
    +--> [Clean Feed Publisher]
    +--> [Overlay Composition Adapter]
    +--> [CDN Delivery Adapter]
```

### Relações externas do Media Management Service

```text
[Hb Track Edge Node] --> [Ingest API]
[Scouting Service] --> [Time Sync Engine]
[Tracking Service] --> [Time Sync Engine]
[Match Operations Service] --> [Time Sync Engine]

[Media Catalog] --> [Object Storage]
[Media Catalog] --> [Operational Database]
[Clip Orchestrator] --> [Object Storage]

[Playback Gateway] --> [Web App]
[Playback Gateway] --> [Tablet App - Match Ops]
[Playback Gateway] --> [Mobile App]

[Broadcast Output Adapter] --> [Broadcast & Distribution Service]
[Broadcast Output Adapter] --> [CDN / OTT Delivery]

[Semantic Linking Service] --> [Search Index]
[Semantic Linking Service] --> [Lakehouse / Analytical Store]
```

---

## C4 — Nível 3: Componentes do “Hb Track Edge Node”

```text
Component Diagram - Hb Track Edge Node

[Camera Connector]
[Encoder Connector]
[Local Buffer Manager]
[Edge Session Agent]
[Edge Health Monitor]
[Local Time Sync Client]
[Fallback Clip Cache]
[Store-and-Forward Uploader]
[Telemetry Publisher]

[Camera Connector] --> [Edge Session Agent]
[Encoder Connector] --> [Edge Session Agent]
[Edge Session Agent] --> [Local Buffer Manager]
[Edge Session Agent] --> [Local Time Sync Client]
[Edge Session Agent] --> [Store-and-Forward Uploader]
[Edge Session Agent] --> [Telemetry Publisher]
[Fallback Clip Cache] --> [Store-and-Forward Uploader]
[Edge Health Monitor] --> [Telemetry Publisher]
```

### Função do Edge Node

Ele garante:

* captura local resiliente
* buffer em caso de falha de rede
* continuidade operacional na arena
* sincronização inicial com o relógio da partida
* reenvio posterior para a nuvem

---

## C4 — Nível 3: Componentes do “Semantic Linking Service”

```text
Component Diagram - Semantic Linking Service

[Event Correlator]
[Tracking Correlator]
[Score Context Resolver]
[Load Context Resolver]
[Tactical Context Resolver]
[Semantic Index Writer]
[Query Translator]

[Scouting Service] --> [Event Correlator]
[Tracking Service] --> [Tracking Correlator]
[Match Operations Service] --> [Score Context Resolver]
[Athlete Monitoring Service] --> [Load Context Resolver]
[Opponent Intelligence Service] --> [Tactical Context Resolver]

[Event Correlator] --> [Semantic Index Writer]
[Tracking Correlator] --> [Semantic Index Writer]
[Score Context Resolver] --> [Semantic Index Writer]
[Load Context Resolver] --> [Semantic Index Writer]
[Tactical Context Resolver] --> [Semantic Index Writer]

[Semantic Index Writer] --> [Search Index]
[Semantic Index Writer] --> [Lakehouse / Analytical Store]

[Analytics & BI Service] --> [Query Translator]
[Playback Gateway] --> [Query Translator]
```

### Função desse serviço

É ele que transforma vídeo em dado pesquisável por perguntas como:

* todos os contra-ataques no 2º tempo
* arremessos do ponta em superioridade numérica
* lances com queda de performance após carga alta
* sequências defensivas contra 7x6

---

## C4 — Nível 4: Sequência resumida de um jogo ao vivo

Isso já é quase um diagrama dinâmico, mas ajuda a fechar o C4 com comportamento.

```text
Dynamic Flow - Live Match

1. Edge Node inicia sessão de captura
2. Ingest API registra a sessão
3. Time Sync Engine cria relógio canônico da partida
4. Tracking Service envia amostras em tempo real
5. Scouting Service registra eventos ao vivo
6. Media Management recebe e segmenta vídeo
7. Transcode Orchestrator gera proxy técnico e perfis públicos
8. Playback Gateway disponibiliza stream técnico ao banco e analistas
9. Broadcast Output Adapter publica stream público na CDN
10. Semantic Linking Service correlaciona vídeo + evento + tracking + carga + placar
11. Clip Orchestrator gera recortes automáticos
12. Analytics & BI consome eventos enriquecidos
```

---

## Versão resumida em estilo Structurizr DSL

Se você quiser uma base mais “copiável” para documentação, esta é uma versão simplificada.

```text
workspace "Hb Track" "C4 model for live video and media architecture" {

  model {
    user = person "Usuário Interno" "Treinador, analista, staff, atleta"
    federation = person "Federação/Liga" "Operação institucional"
    mediaPartner = person "Parceiro de Mídia" "Broadcast e distribuição"
    fan = person "Público" "Consome transmissões e highlights"

    hbtrack = softwareSystem "Hb Track" "Plataforma unificada handebol-first"

    web = container hbtrack "Web App" "UI web para staff e gestão"
    tablet = container hbtrack "Tablet App Match Ops" "UI para banco e operação ao vivo"
    mobile = container hbtrack "Mobile App" "UI para atletas e staff"
    publicPortal = container hbtrack "Public Portal / OTT" "Portal público de consumo"

    api = container hbtrack "API Gateway / BFF" "Orquestra acesso aos serviços"
    media = container hbtrack "Media Management Service" "Captura, transcode, catálogo, clipping e playback"
    tracking = container hbtrack "Tracking Service" "Tracking de atletas e bola"
    scouting = container hbtrack "Scouting Service" "Eventos táticos e técnicos"
    matchOps = container hbtrack "Match Operations Service" "Relógio, placar, operação do jogo"
    analytics = container hbtrack "Analytics & BI Service" "KPIs, dashboards e consultas"
    rights = container hbtrack "Rights & Policy Service" "Políticas de acesso e direitos"
    semantic = container hbtrack "Semantic Linking Service" "Liga vídeo ao contexto esportivo"

    edge = container hbtrack "Hb Track Edge Node" "Captura local resiliente"
    objectStorage = container hbtrack "Object Storage" "Armazenamento de vídeo e clips"
    eventBus = container hbtrack "Event Bus" "Mensageria"
    search = container hbtrack "Search Index" "Busca semântica"
    lakehouse = container hbtrack "Lakehouse" "Histórico analítico"

    cdn = softwareSystem "CDN / OTT Delivery" "Distribuição pública"
    cameras = softwareSystem "Capture Sources" "Câmeras IP/PTZ/Encoders"
    sensors = softwareSystem "Tracking Hardware" "Sensores e dispositivos"

    user -> web "Usa"
    user -> tablet "Usa"
    user -> mobile "Usa"
    federation -> web "Opera"
    mediaPartner -> publicPortal "Consome e integra"
    fan -> publicPortal "Assiste"

    web -> api "HTTPS"
    tablet -> api "HTTPS"
    mobile -> api "HTTPS"
    publicPortal -> api "HTTPS"

    api -> media "Usa"
    api -> tracking "Usa"
    api -> scouting "Usa"
    api -> matchOps "Usa"
    api -> analytics "Usa"
    api -> rights "Usa"

    cameras -> edge "Envia vídeo"
    edge -> media "Ingestão"
    sensors -> tracking "Envia telemetria"

    scouting -> eventBus "Publica eventos"
    tracking -> eventBus "Publica eventos"
    matchOps -> eventBus "Publica eventos"
    media -> eventBus "Publica eventos"

    media -> objectStorage "Armazena assets"
    media -> semantic "Solicita vínculo semântico"
    semantic -> search "Indexa"
    semantic -> lakehouse "Enriquece histórico"

    media -> cdn "Publica streaming"
    rights -> media "Valida políticas"
    analytics -> lakehouse "Consulta"
  }
}
```

## Conclusão

O C4 do Hb Track mostra três decisões fundamentais:

1. **o vídeo não é um subsistema isolado**, ele está no centro do modelo esportivo;
2. **o edge node é parte obrigatória da arquitetura**, não acessório;
3. **o pipeline técnico e o pipeline público compartilham a mesma origem e a mesma semântica**, mas saem por canais diferentes.

Segue a versão em **PlantUML C4**, separada em três blocos: **Contexto (L1)**, **Containers (L2)** e **Componentes (L3)** do subsistema de vídeo ao vivo do Hb Track.

### 1. System Context

```plantuml
@startuml HbTrack_SystemContext
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Context.puml

title Hb Track - System Context

Person(coach, "Comissão Técnica", "Treinadores e comissão técnica")
Person(analyst, "Analista de Desempenho", "Análise técnica, tática e vídeo")
Person(performance, "Preparador Físico / Performance", "Carga, readiness e performance")
Person(medical, "Departamento Médico", "Recuperação, restrições e retorno")
Person(athlete, "Atletas", "Consumo de feedback, clips e planos")
Person(director, "Diretor Esportivo", "Gestão esportiva e decisão")
Person(federation, "Federação / Liga", "Operação institucional e competições")
Person(mediaPartner, "Parceiros de Mídia / Broadcast", "TV, OTT e distribuição")
Person(fan, "Público / Fãs", "Consumo de transmissões e highlights")

System(hbtrack, "Hb Track", "Plataforma unificada, multi-domínio, handebol-first, com backbone temporal único, edge capture, dual pipeline técnico/broadcast, vídeo semântico e analytics cruzando tracking + vídeo + carga + contexto.")

System_Ext(cdn, "Plataformas OTT / CDN", "Distribuição pública e entrega de vídeo")
System_Ext(broadcastPartners, "Parceiros de Broadcast", "TV e distribuição externa")
System_Ext(externalApps, "Apps / Sites de Clubes e Ligas", "Portais e aplicações externas")
System_Ext(captureDevices, "Dispositivos de Captura / Edge Nodes", "Câmeras, encoders e captura local")
System_Ext(trackingHardware, "Sensores de Tracking", "Tracking de atletas e bola")

Rel(coach, hbtrack, "Opera, analisa e decide")
Rel(analyst, hbtrack, "Analisa vídeo, scouting e eventos")
Rel(performance, hbtrack, "Monitora carga e readiness")
Rel(medical, hbtrack, "Consulta restrições e recuperação")
Rel(athlete, hbtrack, "Consome feedback, clips e planos")
Rel(director, hbtrack, "Consulta indicadores e relatórios")
Rel(federation, hbtrack, "Opera competição e distribuição institucional")
Rel(mediaPartner, hbtrack, "Integra mídia e distribuição")
Rel(fan, hbtrack, "Assiste transmissões e highlights")

Rel(hbtrack, cdn, "Distribui streaming público")
Rel(hbtrack, broadcastPartners, "Entrega feeds e metadados")
Rel(hbtrack, externalApps, "Expõe vídeo, dados e widgets")
Rel(hbtrack, captureDevices, "Recebe vídeo ao vivo")
Rel(hbtrack, trackingHardware, "Recebe telemetria e tracking")

@enduml
```

---

### 2. Container Diagram

```plantuml
@startuml HbTrack_Containers
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Container.puml

title Hb Track - Container Diagram

Person(user, "Usuário Interno", "Treinador, analista, staff, atleta")
Person(federationUser, "Federação / Liga", "Operação institucional")
Person(mediaUser, "Parceiro de Mídia", "Broadcast e distribuição")
Person(publicUser, "Público", "Consome streams e highlights")

System_Boundary(hb, "Hb Track") {

  Container(web, "Web App", "Web", "Interface web para staff, gestão, federação e mídia")
  Container(tablet, "Tablet App - Match Ops", "Tablet App", "Interface de banco, tribuna e operação ao vivo")
  Container(mobile, "Mobile App", "Mobile App", "Interface para atletas e staff")
  Container(publicPortal, "Public Portal / OTT Experience", "Web / Mobile", "Consumo público de streams, highlights e estatísticas")

  Container(api, "API Gateway / BFF Layer", "API Gateway / BFF", "Ponto de entrada para apps e orquestração de acesso")

  Container(core, "Core Platform Service", "Application Service", "Usuários, tenants, permissões, auditoria e configuração")
  Container(matchOps, "Match Operations Service", "Application Service", "Relógio oficial, placar, estados de jogo e operação ao vivo")
  Container(training, "Training & Planning Service", "Application Service", "Planejamento de treino e microciclos")
  Container(scouting, "Scouting Service", "Application Service", "Eventos técnicos, táticos e tagging")
  Container(tracking, "Tracking Service", "Realtime / Application Service", "Tracking de atletas e bola")
  Container(monitoring, "Athlete Monitoring Service", "Application Service", "Carga, readiness, wellness e risco")
  Container(medical, "Medical & Recovery Service", "Application Service", "Restrições, recuperação e retorno")
  Container(opponent, "Opponent Intelligence Service", "Application Service", "Scouting de adversário")
  Container(analytics, "Analytics & BI Service", "Analytics Service", "KPIs, dashboards, consultas e benchmarking")
  Container(media, "Media Management Service", "Media Service", "Captura, ingestão, sincronização, transcode, catálogo, clipping e playback")
  Container(broadcast, "Broadcast & Distribution Service", "Distribution Service", "Empacotamento público, distribuição e parceiros")
  Container(rights, "Rights & Policy Service", "Security / Policy Service", "Políticas de acesso, direitos e retenção")
  Container(workflow, "Notification & Workflow Service", "Workflow Service", "Alertas, automações e notificações")

  ContainerDb(operationalDb, "Operational Database", "Relational DB", "Dados operacionais e administrativos")
  ContainerDb(eventStore, "Event Store", "Event Store", "Eventos esportivos e trilha de jogo")
  ContainerDb(timeSeries, "Time-Series Store", "Time-Series DB", "Tracking e séries temporais")
  ContainerDb(objectStorage, "Object Storage", "Object Storage", "Vídeos, clips, proxies e assets")
  ContainerDb(lakehouse, "Lakehouse / Analytical Store", "Analytical Store", "Histórico analítico, BI e IA")
  ContainerDb(search, "Search Index", "Search Engine", "Busca semântica e recuperação")
  Container(observability, "Observability Stack", "Monitoring / Logging / Tracing", "Telemetria e observabilidade")

  Container(edge, "Hb Track Edge Node", "Edge Runtime", "Captura local resiliente, buffering e store-and-forward")
  Container(captureSources, "Capture Sources", "IP Cameras / PTZ / SDI Encoders", "Fontes de vídeo da arena")
  Container(trackingSensors, "Tracking Hardware / Sensors", "Sensors", "Sensores de tracking de atletas e bola")
  Container(localConsole, "Local Operator Console", "Console", "Operação local de scouting e captura")
}

System_Ext(cdn, "CDN / OTT Delivery", "Distribuição pública")
System_Ext(partners, "Broadcast Partners", "Parceiros de TV e distribuição")
System_Ext(externalApps, "External Club / League Apps", "Apps e portais externos")

Rel(user, web, "Usa")
Rel(user, tablet, "Usa")
Rel(user, mobile, "Usa")
Rel(federationUser, web, "Usa")
Rel(mediaUser, web, "Usa")
Rel(publicUser, publicPortal, "Usa")

Rel(web, api, "HTTPS")
Rel(tablet, api, "HTTPS")
Rel(mobile, api, "HTTPS")
Rel(publicPortal, api, "HTTPS")

Rel(api, core, "Usa")
Rel(api, matchOps, "Usa")
Rel(api, scouting, "Usa")
Rel(api, tracking, "Usa")
Rel(api, monitoring, "Usa")
Rel(api, analytics, "Usa")
Rel(api, media, "Usa")
Rel(api, broadcast, "Usa")
Rel(api, rights, "Usa")
Rel(api, workflow, "Usa")

Rel(captureSources, edge, "Envia vídeo")
Rel(edge, media, "Ingestão de mídia")
Rel(trackingSensors, tracking, "Envia telemetria")
Rel(localConsole, scouting, "Registra eventos")

Rel(scouting, eventStore, "Grava eventos")
Rel(matchOps, eventStore, "Grava estados do jogo")
Rel(tracking, timeSeries, "Grava tracking")
Rel(core, operationalDb, "Lê/escreve")
Rel(matchOps, operationalDb, "Lê/escreve")
Rel(training, operationalDb, "Lê/escreve")
Rel(medical, operationalDb, "Lê/escreve")
Rel(media, objectStorage, "Armazena assets")
Rel(analytics, lakehouse, "Consulta / escreve")
Rel(analytics, search, "Indexa / consulta")

Rel(scouting, analytics, "Publica eventos enriquecíveis")
Rel(tracking, analytics, "Envia séries e métricas")
Rel(matchOps, analytics, "Envia contexto de jogo")
Rel(media, analytics, "Envia metadata de vídeo")

Rel(media, rights, "Valida políticas")
Rel(broadcast, rights, "Valida políticas")

Rel(media, broadcast, "Entrega streams e assets")
Rel(broadcast, cdn, "Publica streams")
Rel(broadcast, partners, "Entrega feed")
Rel(broadcast, externalApps, "Expõe streams, dados e widgets")

Rel(edge, observability, "Envia telemetria")
Rel(media, observability, "Envia logs e métricas")
Rel(broadcast, observability, "Envia logs e métricas")
Rel(tracking, observability, "Envia logs e métricas")

@enduml
```

---

### 3. Component Diagram — Media Management Service

```plantuml
@startuml HbTrack_MediaManagement_Components
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Component.puml

title Hb Track - Media Management Service - Component Diagram

Container_Boundary(mediaBoundary, "Media Management Service") {

  Component(ingestApi, "Ingest API", "API Component", "Recebe streams, uploads e registra sessões")
  Component(sessionManager, "Session Manager", "Application Component", "Cria e controla sessões de mídia")
  Component(sourceRegistry, "Source Registry", "Application Component", "Registra fontes, câmeras e ângulos")
  Component(ingestValidator, "Ingest Validator", "Application Component", "Valida origem, formato e permissões")

  Component(timeSync, "Time Sync Engine", "Domain Component", "Mantém o relógio canônico da partida")
  Component(clockAdapter, "Canonical Match Clock Adapter", "Domain Component", "Integra com o relógio oficial")
  Component(driftCorrection, "Drift Correction", "Domain Component", "Corrige desvios de sincronização")
  Component(timestampMapper, "Timestamp Mapper", "Domain Component", "Mapeia timestamps locais para o tempo canônico")

  Component(transcode, "Transcode Orchestrator", "Media Component", "Orquestra derivados de mídia")
  Component(proxyGen, "Proxy Generator", "Media Component", "Gera proxies técnicos")
  Component(mezzanine, "Mezzanine Encoder", "Media Component", "Gera o mezzanine canônico")
  Component(abrPackager, "ABR Packager", "Media Component", "Gera perfis adaptativos públicos")
  Component(thumbnails, "Thumbnail Extractor", "Media Component", "Extrai thumbnails")

  Component(mediaCatalog, "Media Catalog", "Domain Component", "Catálogo central de ativos")
  Component(assetRegistry, "Asset Registry", "Domain Component", "Registra assets e versões")
  Component(metadataAdapter, "Metadata Store Adapter", "Persistence Adapter", "Persiste metadados")
  Component(retentionManager, "Retention Manager", "Policy Component", "Aplica retenção e lifecycle")

  Component(clipOrchestrator, "Clip Orchestrator", "Media Component", "Orquestra clips, playlists e highlights")
  Component(manualClip, "Manual Clip Builder", "Media Component", "Gera clip sob demanda")
  Component(autoClip, "Auto Clip Builder", "Media Component", "Gera clip por evento")
  Component(playlistBuilder, "Playlist Builder", "Media Component", "Monta playlists")
  Component(highlightGen, "Highlight Generator", "Media Component", "Gera highlights automáticos")

  Component(playbackGateway, "Playback Gateway", "Delivery Component", "Entrega reprodução para superfícies internas")
  Component(signedUrl, "Signed URL Issuer", "Security Component", "Emite URLs assinadas")
  Component(accessChecker, "Access Policy Checker", "Security Component", "Valida acesso e perfil")
  Component(technicalDelivery, "Technical Stream Delivery", "Delivery Component", "Entrega stream técnico")
  Component(watermarking, "Internal Watermarking", "Delivery Component", "Aplica watermark interno")

  Component(broadcastAdapter, "Broadcast Output Adapter", "Delivery Component", "Adapta saídas públicas e institucionais")
  Component(publicPublisher, "Public Stream Publisher", "Delivery Component", "Publica stream público")
  Component(cleanFeed, "Clean Feed Publisher", "Delivery Component", "Publica feed limpo")
  Component(overlayAdapter, "Overlay Composition Adapter", "Delivery Component", "Compõe overlays")
  Component(cdnAdapter, "CDN Delivery Adapter", "Delivery Component", "Integra com CDN")
}

Container_Ext(edge, "Hb Track Edge Node", "Captura local resiliente")
Container_Ext(scouting, "Scouting Service", "Eventos táticos e técnicos")
Container_Ext(tracking, "Tracking Service", "Tracking de atletas e bola")
Container_Ext(matchOps, "Match Operations Service", "Relógio, placar e estados do jogo")
Container_Ext(rights, "Rights & Policy Service", "Políticas de acesso")
Container_Ext(semantic, "Semantic Linking Service", "Vínculo semântico entre vídeo e contexto")
Container_Ext(web, "Web App", "Interface web")
Container_Ext(tablet, "Tablet App - Match Ops", "Interface tablet")
Container_Ext(mobile, "Mobile App", "Interface mobile")
ContainerDb_Ext(objectStorage, "Object Storage", "Vídeos e assets")
ContainerDb_Ext(operationalDb, "Operational Database", "Metadados")
System_Ext(cdn, "CDN / OTT Delivery", "Distribuição pública")
Container_Ext(broadcastService, "Broadcast & Distribution Service", "Distribuição e parceiros")

Rel(edge, ingestApi, "Envia vídeo / chunks / segmentos")
Rel(ingestApi, sessionManager, "Cria / atualiza sessão")
Rel(ingestApi, sourceRegistry, "Registra fonte")
Rel(ingestApi, ingestValidator, "Valida ingestão")

Rel(sessionManager, timeSync, "Solicita relógio e sincronização")
Rel(timeSync, clockAdapter, "Consulta relógio oficial")
Rel(timeSync, driftCorrection, "Corrige drift")
Rel(timeSync, timestampMapper, "Mapeia timestamps")

Rel(sessionManager, transcode, "Orquestra derivados")
Rel(transcode, proxyGen, "Gera proxy")
Rel(transcode, mezzanine, "Gera mezzanine")
Rel(transcode, abrPackager, "Gera perfis ABR")
Rel(transcode, thumbnails, "Extrai thumbnails")

Rel(transcode, mediaCatalog, "Registra ativos")
Rel(mediaCatalog, assetRegistry, "Registra assets")
Rel(mediaCatalog, metadataAdapter, "Persiste metadados")
Rel(mediaCatalog, retentionManager, "Aplica retenção")
Rel(mediaCatalog, objectStorage, "Armazena / lê mídia")
Rel(metadataAdapter, operationalDb, "Lê/escreve")

Rel(clipOrchestrator, manualClip, "Usa")
Rel(clipOrchestrator, autoClip, "Usa")
Rel(clipOrchestrator, playlistBuilder, "Usa")
Rel(clipOrchestrator, highlightGen, "Usa")
Rel(clipOrchestrator, mediaCatalog, "Lê/grava clips")

Rel(playbackGateway, signedUrl, "Emite URL assinada")
Rel(playbackGateway, accessChecker, "Valida acesso")
Rel(accessChecker, rights, "Consulta políticas")
Rel(playbackGateway, technicalDelivery, "Entrega stream técnico")
Rel(playbackGateway, watermarking, "Aplica watermark")

Rel(broadcastAdapter, publicPublisher, "Publica stream público")
Rel(broadcastAdapter, cleanFeed, "Publica feed limpo")
Rel(broadcastAdapter, overlayAdapter, "Compõe overlays")
Rel(broadcastAdapter, cdnAdapter, "Entrega para CDN")
Rel(cdnAdapter, cdn, "Entrega stream")

Rel(scouting, timeSync, "Fornece eventos ao vivo")
Rel(tracking, timeSync, "Fornece tracking")
Rel(matchOps, timeSync, "Fornece relógio, placar e estado")

Rel(mediaCatalog, semantic, "Solicita vínculo semântico")
Rel(clipOrchestrator, semantic, "Busca contexto para clips")

Rel(playbackGateway, web, "Entrega playback")
Rel(playbackGateway, tablet, "Entrega playback")
Rel(playbackGateway, mobile, "Entrega playback")

Rel(broadcastAdapter, broadcastService, "Entrega stream e assets")

@enduml
```

---

### 4. Component Diagram — Hb Track Edge Node

```plantuml
@startuml HbTrack_EdgeNode_Components
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Component.puml

title Hb Track - Edge Node - Component Diagram

Container_Boundary(edgeBoundary, "Hb Track Edge Node") {
  Component(cameraConnector, "Camera Connector", "Edge Component", "Conecta câmeras IP / PTZ")
  Component(encoderConnector, "Encoder Connector", "Edge Component", "Conecta encoders SDI / HDMI")
  Component(bufferManager, "Local Buffer Manager", "Edge Component", "Bufferiza mídia localmente")
  Component(edgeSession, "Edge Session Agent", "Edge Component", "Coordena a sessão de captura")
  Component(healthMonitor, "Edge Health Monitor", "Edge Component", "Monitora saúde do nó")
  Component(timeSyncClient, "Local Time Sync Client", "Edge Component", "Sincroniza com relógio canônico")
  Component(clipCache, "Fallback Clip Cache", "Edge Component", "Cache local de recortes críticos")
  Component(uploader, "Store-and-Forward Uploader", "Edge Component", "Reenvia mídia quando a conectividade volta")
  Component(telemetry, "Telemetry Publisher", "Edge Component", "Publica métricas e telemetria")
}

Container_Ext(media, "Media Management Service", "Serviço central de mídia")
Container_Ext(observability, "Observability Stack", "Monitoramento e logs")

Rel(cameraConnector, edgeSession, "Envia vídeo")
Rel(encoderConnector, edgeSession, "Envia vídeo")
Rel(edgeSession, bufferManager, "Bufferiza")
Rel(edgeSession, timeSyncClient, "Sincroniza relógio")
Rel(edgeSession, uploader, "Publica mídia")
Rel(edgeSession, telemetry, "Publica estado")
Rel(clipCache, uploader, "Reenvia clips")
Rel(healthMonitor, telemetry, "Publica saúde")

Rel(uploader, media, "Envia mídia e chunks")
Rel(telemetry, observability, "Envia métricas e logs")

@enduml
```

---

### 5. Component Diagram — Semantic Linking Service

```plantuml
@startuml HbTrack_SemanticLinking_Components
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Component.puml

title Hb Track - Semantic Linking Service - Component Diagram

Container_Boundary(semanticBoundary, "Semantic Linking Service") {
  Component(eventCorrelator, "Event Correlator", "Domain Component", "Correlaciona eventos de scouting com vídeo")
  Component(trackingCorrelator, "Tracking Correlator", "Domain Component", "Correlaciona tracking com vídeo")
  Component(scoreResolver, "Score Context Resolver", "Domain Component", "Resolve placar e estado do jogo")
  Component(loadResolver, "Load Context Resolver", "Domain Component", "Resolve carga e contexto físico")
  Component(tacticalResolver, "Tactical Context Resolver", "Domain Component", "Resolve sistema e contexto tático")
  Component(indexWriter, "Semantic Index Writer", "Persistence Component", "Escreve índices semânticos")
  Component(queryTranslator, "Query Translator", "Application Component", "Traduz consultas semânticas")
}

Container_Ext(scouting, "Scouting Service", "Eventos táticos")
Container_Ext(tracking, "Tracking Service", "Tracking em tempo real")
Container_Ext(matchOps, "Match Operations Service", "Relógio e placar")
Container_Ext(monitoring, "Athlete Monitoring Service", "Carga e readiness")
Container_Ext(opponent, "Opponent Intelligence Service", "Contexto tático")
Container_Ext(analytics, "Analytics & BI Service", "Consultas analíticas")
Container_Ext(playback, "Playback Gateway", "Consulta por contexto")
ContainerDb_Ext(search, "Search Index", "Busca semântica")
ContainerDb_Ext(lakehouse, "Lakehouse / Analytical Store", "Histórico analítico")

Rel(scouting, eventCorrelator, "Envia eventos")
Rel(tracking, trackingCorrelator, "Envia tracking")
Rel(matchOps, scoreResolver, "Envia placar/estado")
Rel(monitoring, loadResolver, "Envia carga")
Rel(opponent, tacticalResolver, "Envia contexto tático")

Rel(eventCorrelator, indexWriter, "Escreve relações")
Rel(trackingCorrelator, indexWriter, "Escreve relações")
Rel(scoreResolver, indexWriter, "Escreve relações")
Rel(loadResolver, indexWriter, "Escreve relações")
Rel(tacticalResolver, indexWriter, "Escreve relações")

Rel(indexWriter, search, "Indexa")
Rel(indexWriter, lakehouse, "Enriquece")

Rel(analytics, queryTranslator, "Solicita consultas")
Rel(playback, queryTranslator, "Solicita consultas")
Rel(queryTranslator, search, "Consulta")
Rel(queryTranslator, lakehouse, "Consulta")

@enduml
```


