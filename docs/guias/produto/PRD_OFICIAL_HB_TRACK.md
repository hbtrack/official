# HB Track — PRD Oficial

> Versão: 1.0.0  
> Data: 2026-03-19  
> Natureza: documento oficial de referência para produto, design, engenharia e agentes de implementação  
> Fontes primárias: `_archive/PRD_EXECUTIVO.md`, `_archive/PRD_INICIAL.md`  
> Fontes complementares: `docs/guias/PRODUCT_VISION.md`, `docs/guias/MVP_SCOPE.md`, `docs/guias/USER_PROFILES.md`, `docs/_canon/SYSTEM_SCOPE.md`, `docs/_canon/MODULE_MAP.md`, `docs/_canon/ARCHITECTURE.md`, `docs/_canon/MODULE_REGISTRY.yaml`, `docs/hbtrack/modulos/training/*`, `docs/hbtrack/modulos/wellness/*`, `docs/hbtrack/modulos/medical/*`

## Como ler este documento

- **Fato**: informação confirmada nas fontes acima.
- **Hipótese**: inferência necessária para conectar documentos incompletos ou conflitantes.
- **Recomendação**: direção sugerida para reduzir ambiguidade e viabilizar implementação.
- **Fase**:
  `MVP` = primeira entrega comercial validável;
  `V2` = expansão para alto rendimento;
  `V3` = expansão institucional para ligas/federações/mídia.
- **Prioridade**:
  `P0` = bloqueia MVP;
  `P1` = importante após MVP;
  `P2` = expansão posterior.

## PARTE A — Visão Executiva

## 1. Visão geral do produto

### Fatos consolidados

- **Fato**: o HB Track é uma plataforma sports-tech unificada para handebol indoor, com mercado primário no Brasil.
- **Fato**: a visão-alvo do produto é cobrir treino, jogo, vídeo, scouting, analytics, readiness, operação de competição e distribuição de dados em uma única plataforma.
- **Fato**: a proposta de valor central é ser uma única fonte de verdade para o handebol, substituindo um stack fragmentado de ferramentas desconectadas.
- **Fato**: a jornada de produto já está estruturada em três ondas: `Coach/MVP`, `Performance/V2` e `League/V3`.

### Hipóteses de trabalho

- **Hipótese**: o primeiro beachhead comercial mais viável é clube/comissão técnica, não federação ou mídia.
- **Hipótese**: a adoção inicial dependerá mais de velocidade operacional e substituição de ferramentas do que de analytics avançado ou distribuição pública.

### Recomendações

- **Recomendação**: assumir oficialmente que o HB Track é uma plataforma end-to-end em visão de longo prazo, mas com entrada de mercado por comissão técnica.
- **Recomendação**: separar sempre "visão de plataforma" de "escopo entregue no MVP" para evitar sobrecarga de roadmap.

## 2. Contexto e problema

### Fatos consolidados

- **Fato**: o ecossistema atual de handebol opera com múltiplos sistemas desconectados para vídeo, scouting, tracking, planilhas, relatórios e comunicação.
- **Fato**: essa fragmentação gera duplicação de cadastro, reconciliação manual, inconsistência entre dados e baixa velocidade de decisão.
- **Fato**: treinadores e analistas gastam tempo excessivo com tarefas burocráticas e edição manual de vídeo.
- **Fato**: o uso de WhatsApp para comunicação técnica cria perda de contexto, dispersão de decisões e pouca rastreabilidade.
- **Fato**: o acompanhamento integrado entre tática, carga, wellness, restrições e disponibilidade esportiva é insuficiente ou inexistente em muitos cenários.
- **Fato**: existe dependência relevante de integrações externas frágeis para consolidar informação operacional.

### Problemas que o produto resolve

- Fragmentação operacional entre treino, jogo, vídeo, scout, performance e competição.
- Duplicação e inconsistência de cadastros e identificadores.
- Baixa velocidade para análise pós-jogo e preparação de adversário.
- Falta de visão integrada entre staff técnico, performance e saúde.
- Comunicação técnica não estruturada.
- Baixa governança de dados sensíveis e clínicos.
- Dependência excessiva de fornecedores isolados.

### Recomendações

- **Recomendação**: tratar a substituição do stack fragmentado como principal tese de valor do MVP.
- **Recomendação**: tratar comunicação estruturada e governança de contexto como requisitos de produto, não como detalhe de UX.

## 3. Objetivos de negócio

| ID | Objetivo | Classificação | Fase | Base |
|---|---|---|---|---|
| OBJ-BIZ-001 | Tornar o HB Track a plataforma operacional e analítica padrão do handebol para clubes, depois alto rendimento e por fim federações/ligas. | Fato | MVP-V3 | `PRD_EXECUTIVO.md` |
| OBJ-BIZ-002 | Permitir que um clube piloto substitua de 3 a 4 ferramentas por uma única plataforma. | Fato | MVP | `PRD_EXECUTIVO.md`, `MVP_SCOPE.md` |
| OBJ-BIZ-003 | Reduzir em 50% o tempo gasto pelo treinador com burocracia de planejamento e edição/análise operacional. | Fato de origem inicial; validação ainda pendente | MVP | `PRD_INICIAL.md` |
| OBJ-BIZ-004 | Acelerar análise pós-jogo e produção de dossiê pré-jogo para aumentar velocidade de decisão da comissão técnica. | Fato | MVP | `PRD_EXECUTIVO.md`, `MVP_SCOPE.md` |
| OBJ-BIZ-005 | Criar um backbone único de dados para atleta, treino, jogo, vídeo, evento e disponibilidade. | Fato | MVP-V2 | `PRD_EXECUTIVO.md`, `PRODUCT_VISION.md` |
| OBJ-BIZ-006 | Expandir monetização por pacotes progressivos: `Coach`, `Performance` e `League`. | Fato | MVP-V3 | `PRD_EXECUTIVO.md`, `PRODUCT_VISION.md` |

## 4. Objetivos do usuário

| ID | Usuário | Objetivo do usuário | Classificação | Fase |
|---|---|---|---|---|
| OBJ-USER-001 | Treinador principal | Planejar microciclos e sessões com menos retrabalho e com contexto do jogo anterior. | Fato | MVP |
| OBJ-USER-002 | Analista de desempenho / scout | Subir vídeo, marcar eventos, gerar playlists e entregar relatório técnico em menos tempo. | Fato | MVP |
| OBJ-USER-003 | Auxiliar técnico | Colaborar em revisão de vídeo, preparação de adversário e planejamento semanal. | Fato | MVP |
| OBJ-USER-004 | Diretor esportivo | Acompanhar evolução do elenco e KPIs executivos sem acessar dados clínicos indevidos. | Fato | MVP |
| OBJ-USER-005 | Atleta | Receber treinos, feedbacks e, quando habilitado, registrar wellness e interagir com recursos assistivos. | Fato parcial | MVP-V2 |
| OBJ-USER-006 | Preparador físico / performance staff | Relacionar carga, prontidão, restrições e resposta competitiva. | Fato | V2 |
| OBJ-USER-007 | Médico / fisioterapeuta | Registrar restrições e autorizações clínicas com acesso fortemente controlado. | Fato | V2 |
| OBJ-USER-008 | Federação / liga | Operar competição, homologar dados e publicar estatísticas oficiais. | Fato | V3 |

## 5. Perfis de usuário / personas

### Fatos consolidados

- **Fato**: o catálogo canônico prevê cerca de 20 perfis de usuário, com autorização baseada em `papel + ação + recurso + escopo + contexto`.
- **Fato**: os dados possuem cinco níveis de sensibilidade, de público até sensível regulado.

### Personas prioritárias por fase

| Persona | JTBD principal | Dados que consome | Limites de acesso | Fase |
|---|---|---|---|---|
| Head Coach | Planejar, ajustar e decidir | treino, vídeo, scout, status funcional | não vê diagnóstico clínico detalhado | MVP |
| Assistant Coach | Colaborar na preparação e revisão | vídeo, scout, planejamento | menor poder de aprovação | MVP |
| Analista de Desempenho | Produzir leitura técnico-tática acionável | eventos, vídeo, dashboards técnicos | sem administração de tenant | MVP |
| Analista de Vídeo | Organizar biblioteca, clipping e playlists | vídeo, tags, playlists | visão analítica parcial | MVP |
| Scout | Mapear padrões do adversário | jogos anteriores, tags, recortes | não vê dados médicos do elenco | MVP |
| Diretor Esportivo | Ler KPIs executivos e evolução do elenco | relatórios e dashboards | visão clínica apenas funcional | MVP |
| Atleta | Ver agenda, feedback e registrar auto-relato | próprio histórico, wellness, materiais compartilhados | só acessa dados próprios | MVP-V2 |
| Preparador Físico | Gerenciar carga e prontidão | wellness, tracking, disponibilidade | não vê prontuário completo | V2 |
| Médico / Fisioterapeuta | Controlar restrição e retorno | registros médicos e funcionais | acesso clínico máximo no próprio escopo | V2 |
| Match Operator / Oficial | Operar jogo e homologar | cronologia oficial, súmula, estatística oficial | sem acesso a inteligência privada do clube | V3 |
| Federação / Liga Admin | Operar competição e dados oficiais | competições, rankings, publicação | sem acesso ao conteúdo médico interno dos clubes | V3 |
| Operador de Mídia | Consumir e distribuir dados publicáveis | live stats, widgets, assets autorizados | só dados homologados e publicados | V3 |

### Recomendação

- **Recomendação**: manter o catálogo completo de papéis em `USER_PROFILES.md`, mas tratar as personas acima como as que dirigem backlog, UX e critérios de aceite por fase.

## 6. Escopo do produto

### 6.1 Escopo-alvo da plataforma

| Capacidade de produto | Mapeamento atual | Fase-alvo | Situação atual |
|---|---|---|---|
| Core platform, auth, autorização, multi-tenant, auditoria, notificações | `identity_access`, `audit`, `notifications` | MVP | Parcialmente contratado; `audit` ainda é stub |
| Cadastro mestre esportivo | `users`, `teams`, `seasons`, `competitions` | MVP | `users` avançado; demais com maturidade desigual |
| Planejamento e gestão de treino | `training` | MVP | Mais maduro no acervo atual |
| Vídeo e biblioteca de mídia | módulo `video` inexistente no registry | MVP | **Gap crítico** |
| Tagging e análise de vídeo | `scout` + futuro `video` | MVP | `scout` ainda é stub; `video` ausente |
| Match operations center | `matches` | MVP | Stub |
| Opponent intelligence | subdomínio de `scout` | MVP | Stub |
| Reports e automação operacional | `reports` + `notifications` | MVP | `reports` stub; `notifications` avançado |
| Wellness e readiness | `wellness` | V2 | Contratos já existem |
| Medical & recovery | `medical` | V2 | Stub |
| Analytics & BI | `analytics` | V2 | Stub |
| AI insight layer | `ai_ingestion` | V2 | Stub |
| Competition & federation ops | `competitions` | V3 | Stub |
| Media, widgets e APIs públicas | módulo `media` inexistente no registry | V3 | Gap futuro |

### 6.2 Fatos críticos de escopo

- **Fato**: o MVP definido na visão executiva cobre comissão técnica, vídeo, scouting, match operations básico, relatório e adversário.
- **Fato**: o módulo `video` é bloqueante para o MVP, mas ainda não existe no registry técnico canônico.
- **Fato**: wellness, medical, analytics e AI aparecem no produto, mas estão posicionados para `V2`.
- **Fato**: competição institucional, live stats públicos e mídia estão posicionados para `V3`.

### 6.3 Recomendações de escopo

- **Recomendação**: formalizar `video` como módulo canônico antes de qualquer sprint de MVP.
- **Recomendação**: tratar `HB Pro Coach`, comunicação estruturada e coaching assistido por IA como extensão de `MVP v1.1` ou `V2`, não como bloqueio do `MVP v1.0`.
- **Recomendação**: não ampliar o MVP com tracking por sensores, competição oficial ou mídia pública.

## 7. Funcionalidades principais

### 7.1 Funcionalidades principais do MVP

- Gestão de identidade, papéis, escopo e multi-tenant.
- Cadastro de atletas, staff, equipes, temporadas e contexto operacional.
- Planejamento de microciclos, sessões, objetivos e blocos de treino.
- Upload, biblioteca e organização de vídeo interno.
- Tagging manual nativo de handebol.
- Filtros por atleta, zona, fase do jogo, sistema e evento.
- Geração de clipes e playlists.
- Operação básica de jogo ao vivo e revisão de intervalo.
- Relatórios pós-jogo, relatórios individuais simples e dossiês de adversário.
- Distribuição interna de material para comissão técnica.

### 7.2 Funcionalidades principais da V2

- Wellness diário e resumo por atleta.
- Gestão de restrições, indisponibilidade e retorno ao treino/jogo.
- Dashboards físico+tático e sinais derivados.
- IA consultiva para sumarização, busca e sugestão de treino/recortes.
- Expansão de opponent intelligence e goalkeeper intelligence.

### 7.3 Funcionalidades principais da V3

- Operação de competição e homologação.
- Rankings, calendário e portal público de competição.
- Live stats oficiais.
- APIs, widgets, overlays e distribuição para mídia.

### 7.4 Itens com escopo ambíguo

| Item | Classificação | Situação |
|---|---|---|
| Canais por tópicos para substituir WhatsApp | Hipótese herdada do `PRD_INICIAL` | sem módulo canônico definido |
| IA conversacional de saúde mental / psicóloga virtual | Hipótese herdada do `PRD_INICIAL` | não formalizada em módulo canônico |
| `HB Pro Coach` com chat e sugestão de treino | Fato documental, mas ainda não baseline do MVP | aparece no módulo `training` como `MVP v1.1` |

## PARTE B — Requisitos Detalhados

## 8. Requisitos funcionais

> Nota: os requisitos abaixo são normativos para produto. Onde houver dependência de módulo ainda não formalizado, isso está explicitado na coluna `Base / observação`.

### 8.1 Requisitos funcionais P0 — MVP

| ID | Requisito | Verificação objetiva | Prioridade | Fase | Base / observação |
|---|---|---|---|---|---|
| RF-CORE-001 | O sistema deve suportar autenticação e autorização multi-tenant com acesso restrito por papel, escopo e contexto. | Usuário autenticado não acessa recurso fora do tenant, equipe ou temporada autorizados. | P0 | MVP | Fato |
| RF-CORE-002 | O sistema deve manter trilha de auditoria para ações sensíveis e mudanças de estado relevantes. | Criação, publicação, aprovação, exportação e override sensível geram registro auditável. | P0 | MVP | Fato |
| RF-MDM-001 | O sistema deve permitir cadastro e manutenção de atletas e staff com vínculo por equipe e temporada. | Usuário com permissão cria, edita e consulta cadastros válidos. | P0 | MVP | Fato |
| RF-MDM-002 | O sistema deve permitir cadastro de equipes, categorias e temporadas operacionais. | É possível associar elenco e sessões a equipe/categoria/temporada. | P0 | MVP | Fato |
| RF-TRAIN-001 | O sistema deve suportar periodização em quatro níveis: temporada, mesociclo, microciclo e sessão. | Usuário autorizado consegue navegar e registrar a hierarquia completa. | P0 | MVP | Fato |
| RF-TRAIN-002 | O sistema deve permitir criar sessão de treino com data, tipo, objetivos, foco e metadados operacionais. | Sessão criada atende validações de contrato e regras de domínio. | P0 | MVP | Fato |
| RF-TRAIN-003 | O sistema deve exigir objetivo operacional explícito para publicação/agendamento de sessão. | Sessão sem objetivo válido permanece em rascunho e não pode ser publicada. | P0 | MVP | Fato |
| RF-TRAIN-004 | O sistema deve registrar blocos de sessão e referenciar exercícios por `exercise_id` e `exercise_version_id`. | Sessão publicada possui ao menos um bloco válido e referência versionada de exercício. | P0 | MVP | Fato |
| RF-TRAIN-005 | O sistema deve preservar separadamente o planejado e o realizado na execução do treino. | Alterações ao vivo não sobrescrevem o plano original. | P0 | MVP | Fato |
| RF-TRAIN-006 | O sistema deve registrar presença, execução e observações de sessão. | Staff autorizado consegue concluir sessão com evidência mínima de execução. | P0 | MVP | Fato |
| RF-VIDEO-001 | O sistema deve permitir upload, armazenamento, organização e recuperação de vídeos internos de treino e jogo. | Staff autorizado sobe vídeo e o encontra na biblioteca por filtros operacionais. | P0 | MVP | Fato com gap técnico | depende de criação do módulo `video` |
| RF-VIDEO-002 | O sistema deve permitir clipping manual e sincronização temporal básica de vídeo com o contexto da partida/treino. | Usuário cria recorte reutilizável e o vincula ao contexto correto. | P0 | MVP | Fato com gap técnico | depende de `video` |
| RF-SCOUT-001 | O sistema deve permitir tagging manual de eventos nativos de handebol. | Analista registra eventos ofensivos, defensivos, transição, superioridade e goleiro. | P0 | MVP | Fato | contrato do módulo ainda é stub |
| RF-SCOUT-002 | O sistema deve permitir filtrar eventos por atleta, zona, fase do jogo, sistema e tipo de evento. | Usuário obtém recortes consistentes a partir desses filtros. | P0 | MVP | Fato | depende de `scout` + `video` |
| RF-SCOUT-003 | O sistema deve gerar playlists e dossiês de adversário a partir de eventos e clipes selecionados. | Usuário autorizado exporta ou compartilha dossiê pré-jogo. | P0 | MVP | Fato |
| RF-MATCH-001 | O sistema deve suportar operação básica ao vivo com cronologia, eventos de jogo e indicadores simples. | Staff registra jogo em andamento e consulta painel operacional. | P0 | MVP | Fato | contrato do módulo ainda é stub |
| RF-REPORT-001 | O sistema deve gerar relatório pós-jogo e relatório individual simples. | Após um jogo, o sistema produz relatório consultável e exportável. | P0 | MVP | Fato |
| RF-REPORT-002 | O sistema deve gerar dossiê técnico pré-jogo para adversário. | O dossiê consolida padrões, recortes e observações do adversário. | P0 | MVP | Fato |
| RF-NOTIF-001 | O sistema deve distribuir materiais e notificações operacionais para membros da comissão técnica. | Staff recebe material compartilhado com rastreabilidade mínima de entrega. | P0 | MVP | Fato |

### 8.2 Requisitos funcionais P1 — V2

| ID | Requisito | Verificação objetiva | Prioridade | Fase | Base / observação |
|---|---|---|---|---|---|
| RF-WELL-001 | O sistema deve permitir registro de wellness diário por atleta, incluindo prontidão, fadiga, dor, recuperação e sono. | Atleta ou staff autorizado registra entrada válida com faixas controladas. | P1 | V2 | Fato |
| RF-WELL-002 | O sistema deve disponibilizar histórico e resumo de wellness por atleta sem transformar auto-relato em dado clínico. | Resumos não contêm diagnóstico, tratamento ou prontuário. | P1 | V2 | Fato |
| RF-MED-001 | O sistema deve permitir registro de avaliação clínica, restrições e autorizações de retorno ao treino e retorno ao jogo. | Médico/fisio autorizado registra e consulta estado clínico contratual. | P1 | V2 | Fato |
| RF-MED-002 | O sistema deve expor aos treinadores apenas o status funcional necessário à decisão esportiva. | Coach visualiza `apto/restrito/indisponível` e motivo funcional, sem laudo clínico detalhado. | P1 | V2 | Fato |
| RF-AN-001 | O sistema deve consolidar métricas técnico-táticas e físico-funcionais em dashboards e comparativos. | Usuário autorizado acessa painel agregado por atleta, equipe e período. | P1 | V2 | Fato |
| RF-AI-001 | O sistema deve oferecer recomendações e sumarizações baseadas em dados, mas sem automatizar decisões esportivas ou clínicas. | A IA produz sugestão/sinal; decisão final exige ato explícito humano autorizado. | P1 | V2 | Fato |
| RF-AI-002 | Sugestões de treino geradas por IA para atleta devem exigir aprovação do treinador responsável antes de serem executáveis. | Sugestão permanece em `pending_approval` até aceite ou recusa do coach. | P1 | V2 ou MVP v1.1 | Fato documental no módulo `training`; baseline ainda pendente |

### 8.3 Requisitos funcionais P2 — V3

| ID | Requisito | Verificação objetiva | Prioridade | Fase | Base / observação |
|---|---|---|---|---|---|
| RF-COMP-001 | O sistema deve permitir operar competições, fases, calendário, classificação e homologação. | Operador institucional registra e publica dados oficiais válidos. | P2 | V3 | Fato |
| RF-COMP-002 | O sistema deve publicar live stats e rankings após homologação. | Apenas estatísticas homologadas ficam disponíveis ao público/mídia. | P2 | V3 | Fato |
| RF-MEDIA-001 | O sistema deve expor APIs, widgets e produtos digitais com base em dados oficiais autorizados. | Canal de mídia consome somente dados publicados e com política correta. | P2 | V3 | Fato com gap técnico | módulo `media` ainda ausente |

### 8.4 Requisitos funcionais candidatos, ainda não consolidados

| ID | Requisito candidato | Classificação | Impacto |
|---|---|---|---|
| RF-COMMS-001 | Substituir WhatsApp por canais oficiais por tópico com confirmação de leitura. | Hipótese forte vinda do `PRD_INICIAL` | alta relevância para adesão, mas sem módulo/contrato definido |
| RF-AI-PSY-001 | Oferecer interface conversacional para coleta de humor, estresse, sono e dores sem formulários. | Hipótese forte vinda do `PRD_INICIAL` | pode diferenciar o produto, mas exige decisão de privacidade, domínio e responsabilidade clínica |
| RF-COMMS-002 | Mural de avisos com protocolo de `Ciente` para mensagens táticas importantes. | Recomendação | encaixa bem em `notifications` ou em futuro módulo de comunicação |

## 9. Requisitos não funcionais

| ID | Requisito | Verificação objetiva | Classificação | Fase | Base |
|---|---|---|---|---|---|
| RNF-SEC-001 | O sistema deve garantir segregação multi-tenant forte. | Testes de autorização não permitem acesso cruzado entre tenants. | Fato | MVP | `SYSTEM_SCOPE.md`, `ARCHITECTURE.md` |
| RNF-SEC-002 | O sistema deve classificar dados por sensibilidade e aplicar política de acesso proporcional. | Dados médicos e pessoais têm masking, auditoria e restrição superiores aos dados públicos. | Fato | MVP-V3 | `USER_PROFILES.md`, `PRD_EXECUTIVO.md` |
| RNF-SEC-003 | O sistema deve cumprir LGPD e políticas aplicáveis, incluindo tratamento de dados de menores. | Fluxos de consentimento, retenção e exclusão seguem política vigente. | Fato | MVP-V3 | `PRD_INICIAL.md`, `PRD_EXECUTIVO.md`, `ARCHITECTURE.md` |
| RNF-OPS-001 | O sistema deve oferecer observabilidade ponta a ponta de requests, workers e eventos críticos. | Operações críticas propagam `X-Flow-ID` e geram logs estruturados correlacionáveis. | Fato | MVP | `ARCHITECTURE.md` |
| RNF-OPS-002 | O produto deve operar em modo degradado para cenários críticos de jogo. | Em falha parcial de rede, a operação ao vivo mantém registro local ou fluxo manual controlado. | Fato | MVP | `PRD_EXECUTIVO.md` |
| RNF-OPS-003 | O módulo de scout ao vivo deve funcionar com latência de interação compatível com operação de jogo. | Ação de registro individual responde dentro da meta acordada de operação. | Fato de origem inicial; meta exata a ratificar | MVP | `PRD_INICIAL.md` cita `<100ms` |
| RNF-OPS-004 | O módulo de scout ao vivo deve operar offline com sincronização posterior quando tecnicamente viável. | Registro local é sincronizado após restabelecimento de conexão, sem perda de ordem crítica. | Fato de origem inicial; ainda não contratado | MVP | `PRD_INICIAL.md` |
| RNF-UX-001 | O fluxo de planejamento de microciclo deve ser rápido para um treinador treinado. | Usuário de referência conclui o fluxo alvo dentro da meta acordada. | Fato de origem inicial; meta exata a ratificar | MVP | `PRD_INICIAL.md` cita `<5 min` |
| RNF-PERF-001 | Dashboards ao vivo e live stats devem ter atualização com latência baixa e previsível. | Atualização dentro do SLA operacional definido para o piloto. | Fato | MVP-V3 | `PRD_EXECUTIVO.md` |
| RNF-PERF-002 | Geração de relatórios e clipping deve ter tempo previsível e monitorado. | Jobs assíncronos expõem estado e conclusão auditável. | Fato | MVP | `PRD_EXECUTIVO.md` |
| RNF-ARCH-001 | O produto deve seguir abordagem contract-first e monólito modular em camadas, salvo ADR formal em contrário. | Nenhuma superfície pública existe sem contrato correspondente. | Fato | MVP-V3 | `ARCHITECTURE.md`, `README.md` |
| RNF-INFRA-001 | Processamento intensivo de vídeo deve ocorrer fora de dispositivos móveis do usuário. | Upload via cliente aciona processamento em backend/nuvem. | Fato | MVP | `PRD_INICIAL.md` |

## 10. Fluxos principais do sistema

### 10.1 Fluxo principal — Pós-jogo

- **Objetivo**: transformar jogo e vídeo em relatório técnico acionável.
- **Atores**: analista de desempenho, analista de vídeo, treinador principal.
- **Pré-condições**: jogo registrado; vídeo disponível; permissões de equipe válidas.
- **Sequência-alvo**:
  1. subir ou vincular vídeo da partida;
  2. marcar eventos relevantes;
  3. criar clipes;
  4. agrupar em playlists;
  5. consolidar relatório pós-jogo;
  6. distribuir ao staff.
- **Saída esperada**: relatório pós-jogo + playlists + evidência consultável.
- **Dependências críticas**: `video`, `scout`, `reports`, `notifications`.
- **Status**: fluxo central do MVP, porém bloqueado pela ausência formal do módulo `video`.

### 10.2 Fluxo principal — Preparação de adversário

- **Objetivo**: reduzir tempo para construir dossiê técnico pré-jogo.
- **Atores**: scout, analista de desempenho, treinador principal, auxiliar técnico.
- **Pré-condições**: jogos anteriores do adversário disponíveis; tagging consistente.
- **Sequência-alvo**:
  1. acessar jogos anteriores;
  2. aplicar filtros táticos;
  3. recortar padrões ofensivos/defensivos;
  4. montar playlists;
  5. gerar dossiê técnico;
  6. revisar com a comissão.
- **Saída esperada**: dossiê pré-jogo e playlists temáticas.
- **Dependências críticas**: `video`, `scout`, `reports`.
- **Status**: fluxo central do MVP.

### 10.3 Fluxo principal — Semana de treino

- **Objetivo**: conectar aprendizado do jogo anterior com o planejamento da semana.
- **Atores**: treinador principal, auxiliar técnico, coordenador.
- **Pré-condições**: equipe e temporada cadastradas; exercícios disponíveis; sessão anterior revisada.
- **Sequência-alvo**:
  1. registrar microciclo;
  2. definir objetivos por sessão;
  3. montar blocos e cargas;
  4. publicar/agendar sessão;
  5. registrar execução, presença e observações;
  6. comparar planejado vs realizado;
  7. ajustar ciclo seguinte.
- **Saída esperada**: histórico de treino utilizável por analytics e revisão técnica.
- **Dependências críticas**: `training`, `exercises`, `teams`, `seasons`.
- **Status**: fluxo central do MVP e o mais maduro na documentação atual.

### 10.4 Fluxo principal — Operação ao vivo

- **Objetivo**: apoiar leitura de jogo em tempo real.
- **Atores**: operador de jogo, analista, treinador principal.
- **Pré-condições**: partida aberta; permissões válidas; console operacional disponível.
- **Sequência-alvo**:
  1. iniciar cronologia;
  2. registrar eventos em tempo real;
  3. acompanhar indicadores simples;
  4. revisar lances no intervalo;
  5. consolidar pós-jogo.
- **Saída esperada**: timeline coerente do jogo e base para relatório.
- **Dependências críticas**: `matches`, `scout`, `video`.
- **Status**: fluxo central do MVP, mas `matches` e `scout` ainda precisam de contratos completos.

### 10.5 Fluxo expandido — Wellness e ajuste de carga

- **Objetivo**: capturar prontidão e apoiar decisão esportiva sem medicalização indevida.
- **Atores**: atleta, preparador físico, treinador, médico/fisio.
- **Pré-condições**: módulo `wellness` ativo; política de acesso definida.
- **Sequência-alvo**:
  1. atleta registra wellness;
  2. sistema consolida resumo;
  3. staff físico avalia risco e disponibilidade;
  4. treinador consome apenas visão funcional;
  5. restrições clínicas, se existirem, vêm de `medical`.
- **Saída esperada**: ajuste de sessão, carga ou elegibilidade com rastreabilidade.
- **Status**: fluxo da `V2`.

## 11. Regras de negócio

| ID | Regra | Classificação | Fonte |
|---|---|---|---|
| RB-001 | Permissão é sempre combinação de papel, ação, recurso, escopo e contexto. | Fato | `USER_PROFILES.md`, `SYSTEM_SCOPE.md` |
| RB-002 | O treinador vê status funcional do atleta, nunca diagnóstico clínico detalhado. | Fato | `USER_PROFILES.md`, `PRD_INICIAL.md`, `DOMAIN_RULES_MEDICAL.md` |
| RB-003 | `wellness` é auto-relato consultivo e não pode ser tratado como prontuário, diagnóstico ou liberação clínica. | Fato | `DOMAIN_RULES_WELLNESS.md` |
| RB-004 | `trainingSessionId` em wellness contextualiza a coleta, mas não comprova presença nem autorização para treinar. | Fato | `DOMAIN_RULES_WELLNESS.md`, OpenAPI `wellness.yaml` |
| RB-005 | Sessão de treino só pode ser criada por treinador ou coordenador autorizado. | Fato | `DOMAIN_RULES_TRAINING.md` |
| RB-006 | Sessão publicada deve ter objetivo operacional explícito, escopo válido, horário e ao menos um bloco. | Fato | `DOMAIN_RULES_TRAINING.md` |
| RB-007 | A soma dos percentuais de foco da sessão deve respeitar a regra de consistência definida no módulo `training`. | Fato | `DOMAIN_RULES_TRAINING.md`, OpenAPI `training.yaml` |
| RB-008 | O planejado e o realizado devem ser preservados separadamente. | Fato | `DOMAIN_RULES_TRAINING.md` |
| RB-009 | Sessão concluída não pode sofrer edição destrutiva; correções históricas exigem trilha auditada. | Fato | `DOMAIN_RULES_TRAINING.md` |
| RB-010 | Atleta com restrição médica ativa não recebe prescrição executável sem override explícito, autorizado e auditado. | Fato | `DOMAIN_RULES_TRAINING.md` |
| RB-011 | IA e analytics podem sugerir e sinalizar, mas não decidir ou executar automaticamente sessão, treino ou liberação clínica. | Fato | `DOMAIN_RULES_TRAINING.md`, `PRD_EXECUTIVO.md` |
| RB-012 | `training` referencia exercícios por identificador e versão; não copia o catálogo soberano de `exercises`. | Fato | `DOMAIN_RULES_TRAINING.md` |
| RB-013 | Só dados homologados e publicados podem ser expostos a mídia e portal público. | Fato | `PRD_EXECUTIVO.md`, `USER_PROFILES.md` |
| RB-014 | Dados públicos, operacionais, competitivos, pessoais e regulados devem receber controles de acesso proporcionais ao nível de sensibilidade. | Fato | `USER_PROFILES.md`, `PRD_EXECUTIVO.md` |

## 12. Critérios de sucesso / métricas

| ID | Métrica | Definição operacional | Meta inicial | Classificação | Fase |
|---|---|---|---|---|---|
| MET-001 | Ferramentas substituídas | Quantidade de ferramentas legadas descontinuadas pelo piloto | 3 a 4 por organização piloto | Fato | MVP |
| MET-002 | Tempo de análise pós-jogo | Intervalo entre fim da partida e distribuição do relatório técnico | redução mensurável versus baseline do piloto | Fato; alvo numérico pendente | MVP |
| MET-003 | Tempo de dossiê pré-jogo | Intervalo entre início da análise e dossiê pronto para comissão | redução mensurável versus baseline do piloto | Fato; alvo numérico pendente | MVP |
| MET-004 | Tempo de planejamento semanal | Tempo para montar e publicar microciclo/sessões da semana | redução de 50% versus baseline é meta recomendada | Fato de origem inicial | MVP |
| MET-005 | Adoção da comissão técnica | WAU/MAU de treinador, analista e auxiliar no tenant piloto | adoção majoritária da comissão | Fato; alvo numérico pendente | MVP |
| MET-006 | Relatórios e playlists gerados | Quantidade de saídas geradas por jogo e por semana | crescimento contínuo no piloto | Fato | MVP |
| MET-007 | Engajamento de wellness | Percentual de atletas ativos com submissões no período | alvo a ratificar por programa de alto rendimento | Fato | V2 |
| MET-008 | Uso integrado físico+tático | Percentual de decisões/revisões que usam dados de mais de um domínio | alvo a definir com piloto V2 | Fato | V2 |
| MET-009 | Alertas acionáveis | Percentual de sinais gerados que resultam em ação do staff | alvo a definir | Fato | V2 |
| MET-010 | Competições operadas | Número de competições executadas integralmente na plataforma | alvo comercial a definir | Fato | V3 |
| MET-011 | Consumo de APIs/widgets | Chamadas úteis, integrações ativas e uso de widgets publicados | alvo comercial a definir | Fato | V3 |

### Recomendação de instrumentação

- **Recomendação**: toda métrica de tempo deve ser medida com baseline anterior ao piloto.
- **Recomendação**: medir adoção por persona, não apenas por tenant.
- **Recomendação**: separar claramente métricas de eficiência operacional, qualidade analítica e expansão comercial.

## 13. Restrições e dependências

### Restrições

- **Fato**: mercado primário é handebol indoor no Brasil.
- **Fato**: o produto é governado por abordagem contract-first.
- **Fato**: a arquitetura canônica vigente descreve monólito modular em camadas.
- **Fato**: dados sensíveis e clínicos exigem segregação, masking, auditoria e políticas de exportação específicas.
- **Fato**: processamento intensivo de vídeo não deve sobrecarregar dispositivos móveis do usuário.
- **Fato**: serviços externos já previstos incluem notificação e storage/mídia.

### Dependências de produto e execução

- Criação formal do módulo `video`.
- Evolução contratual real dos módulos `matches`, `scout`, `reports`, `analytics`, `medical`, `competitions` e `audit`.
- Definição final do escopo de comunicação estruturada.
- Definição final do escopo de IA conversacional para atleta.
- Integração estável entre `training`, `wellness`, `medical`, `analytics` e `ai_ingestion` para V2.

### Conflitos documentais que precisam de decisão

- **Fato**: `ARCHITECTURE.md` e `README.md` posicionam o backend em FastAPI; `MODULE_ROADMAP_2026_03_17.md` menciona Django/Django Ninja para `training`.
- **Fato**: `MODULE_REGISTRY.yaml` marca `training` como `validated_contract`; o roadmap operacional o trata como `implementation_ready`.
- **Recomendação**: essas divergências devem ser resolvidas antes de usar o PRD como base de planejamento de implementação detalhada.

## 14. Riscos

| ID | Risco | Impacto | Probabilidade | Mitigação recomendada |
|---|---|---|---|---|
| R-001 | Escopo excessivo no MVP | atraso e perda de foco | alta | congelar MVP em comissão técnica + vídeo + scout + match ops + reports |
| R-002 | Ausência do módulo `video` no registry | bloqueio direto dos fluxos centrais do MVP | alta | formalizar módulo e contratos antes do sprint de MVP |
| R-003 | Contratos stub em `matches`, `scout`, `reports` | risco de retrabalho de engenharia e UX | alta | priorizar maturidade contratual desses módulos |
| R-004 | Baixa adoção por treinadores e analistas | produto completo, mas pouco usado | média/alta | desenhar para velocidade operacional real e pilotar com staff de campo |
| R-005 | Vazamento ou uso indevido de dados sensíveis | impacto legal, reputacional e clínico | média/alta | ABAC, auditoria, masking, segregação e step-up authentication |
| R-006 | Dependência de operação ao vivo sem tolerância a falhas | quebra em cenário de partida oficial | média | modo degradado, sincronização posterior e fluxo manual controlado |
| R-007 | Drift entre visão de produto e documentação canônica | backlog incoerente e decisões contraditórias | alta | manter PRD, roadmap e registry alinhados por decisão formal |
| R-008 | Resistência cultural à troca do WhatsApp e do fluxo atual | adoção parcial | média | atacar primeiro dores de alto valor e manter transição assistida |
| R-009 | IA produzir recomendações inadequadas ou opacas | perda de confiança do staff e do atleta | média | IA apenas consultiva, com aprovação humana e rastreabilidade |

## 15. Itens fora de escopo

### Fora do escopo do MVP

- Tracking por sensores e bola em tempo real.
- Monitoramento físico avançado com carga aguda/crônica.
- Prontuário médico completo e workflows clínicos avançados.
- Portal público de competição.
- APIs públicas robustas para mídia.
- Broadcast público e OTT como produto autônomo.
- Benchmarking amplo de liga/mercado.
- Clipping automático por visão computacional como dependência do MVP.

### Fora do escopo do produto atual sem decisão formal

- Gestão de arbitragem oficial, credenciamento e escalas de árbitros.
- Venda de ingressos e bilheteria.
- Rede social aberta entre atletas.
- Chat social aberto entre atletas.
- Qualquer capacidade fora dos módulos canônicos sem decisão formal.

## 16. Dúvidas em aberto

| ID | Dúvida | Impacto se não responder | Tipo |
|---|---|---|---|
| Q-001 | Quando e como o módulo `video` entra no registry canônico? | bloqueia o MVP | crítica |
| Q-002 | O MVP comercial é clube/comissão técnica ou já inclui algum piloto institucional? | muda backlog e critérios de aceite | crítica |
| Q-003 | Comunicação estruturada substituindo WhatsApp será parte do MVP, MVP v1.1 ou ficará para V2? | afeta UX, arquitetura e adoção | alta |
| Q-004 | A IA conversacional do atleta cobre apenas coaching esportivo ou também saúde mental? | afeta privacidade, responsabilidade e limites clínicos | crítica |
| Q-005 | O requisito de operação offline do scout ao vivo é obrigatório para o MVP? | afeta arquitetura e priorização | alta |
| Q-006 | Qual é a stack backend oficial para implementação: FastAPI canônico ou transição para Django/Ninja? | afeta toda a execução técnica | crítica |
| Q-007 | Qual documento é SSOT para readiness do módulo `training`: registry ou roadmap? | afeta planejamento de engenharia | alta |
| Q-008 | Quais metas numéricas do piloto serão oficialmente adotadas: 50% de redução, 3-4 ferramentas, WAU mínimo, prazo de relatório? | sem isso, sucesso fica subjetivo | alta |
| Q-009 | Competição/homologação entra apenas na V3 ou existe pacote institucional intermediário? | altera roadmap e pacote comercial | média |
| Q-010 | Política operacional para atletas desligados será arquivar, anonimizar ou excluir por tenant policy? | afeta LGPD, retenção e UX administrativa | média |

## 17. Roadmap inicial / priorização

### 17.1 Prioridade imediata — Fechamento de lacunas de base

1. Formalizar módulo `video`.
2. Resolver conflito de stack e de readiness documental.
3. Completar contratos de `matches`, `scout` e `reports`.
4. Fechar a linha-mestra do pacote `Coach/MVP`.

### 17.2 MVP v1.0 — HB Track Coach

**Objetivo**: provar substituição de 3 a 4 ferramentas e ganho de velocidade operacional da comissão técnica.

**Escopo recomendado**:

- `identity_access`
- `users`
- `teams`
- `seasons`
- `training`
- `video`
- `scout`
- `matches`
- `reports`
- `notifications`
- `audit`

**Funcionalidades que definem sucesso do MVP**:

- semana de treino estruturada;
- biblioteca de vídeo com clipping manual;
- tagging nativo de handebol;
- operação básica ao vivo;
- relatório pós-jogo;
- dossiê pré-jogo;
- distribuição interna para staff.

### 17.3 MVP v1.1 — Extensões assistidas

- `HB Pro Coach` para atleta com contexto esportivo.
- Sugestões de treino com aprovação do treinador.
- Componentes de comunicação estruturada, se a decisão de escopo for positiva.

### 17.4 V2 — HB Track Performance

- `wellness`
- `medical`
- `analytics`
- `ai_ingestion`
- futuro módulo `tracking`

**Critério de entrada em V2**: MVP comprovou uso recorrente por comissão técnica e criou base mínima de dados confiáveis.

### 17.5 V3 — HB Track League

- `competitions` expandido
- futuro módulo `media`
- live stats oficiais
- APIs/widgets/portal público

## 18. Critérios de aceite

### 18.1 Critérios de aceite do PRD como baseline

- O documento diferencia explicitamente fato, hipótese e recomendação.
- O documento separa visão-alvo da plataforma e escopo do MVP.
- O documento identifica gaps críticos que impedem implementação direta.
- O documento fornece requisitos verificáveis e fluxos principais utilizáveis por design e engenharia.

### 18.2 Critérios de aceite do MVP v1.0

| ID | Critério de aceite |
|---|---|
| CA-MVP-001 | Um tenant piloto consegue ser configurado com usuários, equipes, elenco e temporada. |
| CA-MVP-002 | O treinador consegue planejar um microciclo e publicar sessões com objetivos e blocos válidos. |
| CA-MVP-003 | A comissão técnica consegue subir vídeo, organizar biblioteca e criar clipes manuais. |
| CA-MVP-004 | O analista consegue marcar eventos de handebol e gerar playlists por filtros táticos. |
| CA-MVP-005 | Durante um jogo, a equipe consegue registrar eventos e manter cronologia operacional básica. |
| CA-MVP-006 | Após o jogo, o sistema gera relatório pós-jogo e permite compartilhar material ao staff. |
| CA-MVP-007 | O scout consegue montar dossiê de adversário usando recortes e eventos históricos. |
| CA-MVP-008 | O controle de acesso impede vazamento cross-tenant e exposição de dados sensíveis indevidos. |
| CA-MVP-009 | Ações sensíveis e mudanças de estado relevantes ficam auditáveis. |
| CA-MVP-010 | O piloto confirma substituição operacional de ao menos 3 ferramentas do stack anterior. |

### 18.3 Critérios de aceite da V2

| ID | Critério de aceite |
|---|---|
| CA-V2-001 | Atletas e staff autorizado conseguem registrar e consultar wellness dentro dos limites de domínio definidos. |
| CA-V2-002 | Restrição clínica e autorização de retorno são geridas em `medical`, sem vazamento para módulos não autorizados. |
| CA-V2-003 | Treinador consome visão funcional, não clínica detalhada. |
| CA-V2-004 | Dashboards integrados físico+tático estão disponíveis para papéis corretos. |
| CA-V2-005 | Recomendações de IA permanecem consultivas e exigem aceite humano quando afetam ação operacional. |

### 18.4 Critérios de aceite da V3

| ID | Critério de aceite |
|---|---|
| CA-V3-001 | Operador institucional consegue criar e operar competição com fases e classificação. |
| CA-V3-002 | Live stats e ranking só são publicados após homologação. |
| CA-V3-003 | APIs e widgets expõem apenas dados autorizados para uso público ou institucional. |

## Versão resumida executiva

O HB Track é uma plataforma unificada para handebol cujo objetivo é substituir um stack fragmentado de ferramentas por uma única fonte de verdade para treino, jogo, vídeo, scouting, performance e, mais à frente, competição e mídia. O produto tem uma visão ampla de plataforma, mas o ponto de entrada mais viável é o pacote `Coach`: comissão técnica, planejamento, vídeo, tagging, match ops básico, relatórios e adversário.

O principal problema atual não é falta de feature isolada; é fragmentação operacional. Treinadores, analistas e staff perdem tempo consolidando planilhas, vídeos, chats e sistemas diferentes. A proposta do HB Track é reduzir esse retrabalho, acelerar análise pós-jogo e preparação de adversário e criar um backbone único de dados esportivos.

O maior risco hoje não é comercial; é de definição. O MVP depende de `video`, mas esse módulo ainda não existe no registry canônico. Além disso, `matches`, `scout` e `reports` ainda precisam sair de stubs contratuais, e há divergência documental sobre stack e readiness do módulo `training`. O PRD, portanto, formaliza um caminho claro: congelar o MVP em comissão técnica, resolver as lacunas críticas e só então expandir para `Performance/V2` e `League/V3`.

## Principais lacunas que ainda precisam de resposta

1. Criar e formalizar o módulo `video`.
2. Fechar os contratos reais de `matches`, `scout` e `reports`.
3. Decidir o lugar de comunicação estruturada no produto.
4. Decidir o escopo exato da IA conversacional para atleta.
5. Resolver a divergência FastAPI vs Django/Ninja.
6. Resolver a divergência `validated_contract` vs `implementation_ready` para `training`.
7. Confirmar se offline no scout ao vivo é requisito obrigatório do MVP.
8. Ratificar metas numéricas oficiais do piloto.

## Proposta de MVP

### Objetivo do MVP

Provar que uma comissão técnica de handebol consegue operar a semana de treino, a análise pós-jogo, a preparação de adversário e a revisão ao vivo em um único sistema.

### Usuários do MVP

- treinador principal
- auxiliar técnico
- analista de desempenho
- analista de vídeo
- scout
- diretor esportivo em leitura leve

### Escopo recomendado do MVP

- autenticação e autorização multi-tenant
- cadastros esportivos essenciais
- treino: microciclo, sessão, objetivo, bloco, execução
- vídeo: upload, biblioteca, clipping manual, sincronização básica
- scout: tagging manual nativo de handebol
- match ops: cronologia e painel simples ao vivo
- reports: pós-jogo, individual simples, adversário
- notifications + audit

### Fora do MVP

- tracking por sensores
- prontuário médico completo
- analytics avançado
- competição oficial institucional
- APIs públicas e mídia
- broadcast/OTT
- IA clínica ou decisória

### Pré-condições para iniciar o MVP

1. Formalizar `video` no registry.
2. Fechar contrato funcional mínimo de `matches`, `scout` e `reports`.
3. Resolver divergências documentais de stack e readiness.
4. Escolher um piloto de clube/comissão técnica e levantar baselines reais de tempo.
