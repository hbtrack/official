<!-- STATUS: NEEDS_REVIEW -->

ARQUITETURA FINAL DE ESTATÍSTICAS DO HB TRACK
1️⃣ Estatísticas Operacionais (Equipe – uso diário)

Objetivo: controle operacional + decisão imediata
Quando: antes e depois de treinos e jogos
Quem usa: treinadores, coordenação

Perguntas que responde:
Quem treinou?
Quem não treinou?
Quem não respondeu wellness?
Quem está sobrecarregado?
Quem está fora do processo?

UX correta:
– Página única, direta, sem comparação profunda
– Exceções sempre no topo
– Estados binários e alertas visuais
– Foco em ação, não em análise

Blocos obrigatórios:
– Status da sessão (treino/jogo atual ou último)
– Pendências do processo (presença, wellness, acesso)
– Alertas de carga
– Lista acionável de atletas (status por atleta)

Essa é a página que “abre o dia”.

2️⃣ Estatísticas de Equipes (Análise coletiva)

Objetivo: entender performance coletiva e direcionar melhoria
Quando: pós-ciclo, semana, competição
Quem usa: comissão técnica, coordenação

Perguntas que responde:
Como a equipe está evoluindo?
Onde estamos perdendo rendimento?
Carga está adequada?
Wellness está caindo?
Treino está convertendo em jogo?

UX correta:
– Comparação temporal (não individual)
– Tendências, não alertas
– Gráficos claros, poucas tabelas
– Leitura estratégica, não operacional

Blocos obrigatórios:
– Tendência de carga vs presença
– Wellness médio ao longo do tempo
– Indicadores de performance em jogos
– Pontos fortes e gargalos do período

Aqui não existe atleta como protagonista, existe equipe.

3️⃣ Estatísticas de Atletas (Visão individual protegida)

Objetivo: autoconhecimento, engajamento e foco de melhoria
Quando: consulta pessoal, acompanhamento contínuo
Quem usa: atleta (e comissão no perfil do atleta)

Perguntas que responde:
Como estou em relação a mim mesmo?
Estou evoluindo?
Onde preciso melhorar?
Minha carga está equilibrada?

UX crítica (regra de ouro):
❌ NUNCA comparar com outras atletas
✅ Comparar apenas:
– atleta vs histórico próprio
– atleta vs metas individuais
– atleta vs faixa saudável (zonas)

Blocos obrigatórios:
– Presença pessoal
– Wellness pessoal
– Carga ao longo do tempo
– Feedback interpretativo simples (“atenção”, “ok”, “em evolução”)

Isso evita ansiedade, competição interna tóxica e abandono do sistema.

HB Track Configuration

No HB Track, isso se traduz em:

– Uma rota operacional principal (estatísticas do dia / sessão)
– Uma rota analítica por equipe (estatísticas coletivas)
– Uma rota individual por atleta, com regras rígidas de visibilidade

Todos consomem os mesmos /reports, mas:
– mudam hierarquia
– mudam linguagem
– mudam permissões
– mudam comparações

Atletas só veem dados próprios. Comissão vê coletivo. Tudo passa por PermissionGateV2.

Resumo em uma frase

Você não está criando “páginas de estatísticas”.
Você está criando um sistema de governança esportiva em três níveis.

Próximo passo lógico:
você quer começar desenhando primeiro a visão operacional diária ou a visão individual do atleta? Isso define a fundação do resto.

a rota é essa http://localhost:3000/statistics
vamos configurar a a visão operacional diária

Perfeito. Vamos configurar UMA ÚNICA visão operacional diária, dentro da rota já definida:

/statistics

Sem modelos paralelos, sem ambiguidade.

UX Explanation — Visão Operacional Diária

Essa página responde apenas uma pergunta:

“O processo esportivo está sob controle hoje?”

Portanto, ela não é analítica, não é histórica profunda e não é comparativa.
Ela é situacional, acionável e binária.

Princípios que regem essa tela:

1. Exceção no topo (Exception-Driven UX)
O usuário não entra para ver médias. Ele entra para ver quem está fora do processo. Tudo que exige ação aparece primeiro.

2. Estado > número
“Respondido / Não respondido”, “Presente / Ausente”, “Normal / Alerta”.
Estados são mais rápidos que gráficos para decisão diária.

3. Uma linha = um atleta = uma decisão
Cada atleta precisa caber em uma leitura rápida, com status claros e sem interpretação subjetiva.

4. Pré e Pós na mesma tela
A página sempre mostra a sessão mais recente ou ativa.
O que muda é o estado dos dados, não a estrutura da UI.

HB Track Configuration — /statistics (Visão Operacional)
Estrutura fixa da página (ordem obrigatória)
1️⃣ Header de contexto (hard requirement)

Sempre visível no topo:

Sessão: Treino ou Jogo
Equipe
Data
Status: em andamento | concluída | pendente

Sem sessão válida → a página não renderiza métricas, apenas orientação.

2️⃣ Bloco crítico — Pendências do processo (PRIORIDADE MÁXIMA)

Cards simples, grandes e sem gráfico:

– Atletas ausentes
– Wellness pendente (pré ou pós)
– Atletas sem acesso / sem resposta
– Alertas ativos de carga

Esses cards devem:
– usar cores semânticas
– ser clicáveis
– levar diretamente à lista filtrada de atletas

Isso é o “painel de risco do dia”.

3️⃣ Bloco de carga — decisão competitiva

Visual simples (linha ou barras curtas):

– Carga da sessão
– Média recente
– Faixa segura (zona visual)

Abaixo:
lista automática de atletas fora da zona esperada.

Nada além disso.
Sem histórico longo aqui.

4️⃣ Lista operacional de atletas (núcleo da página)

Tabela compacta, sempre visível:

Colunas:
– Nome
– Presença
– Wellness
– Carga
– Status geral

Regras:
– Status visual (ok / atenção / crítico)
– Clique leva ao perfil do atleta
– Nenhuma comparação entre atletas
– Ordenação padrão por problema, não por nome

Essa lista é o coração da UX.

5️⃣ Alertas persistentes

Qualquer alerta crítico:
– não some
– não colapsa
– não depende de refresh

Segue a regra de notificação bloqueante do sistema.

Implementação técnica no HB Track

– Página como Server Component
– Dados carregados via /reports
– Promise.all para sessão, presença, wellness, carga
– Skeletons obrigatórios
– Controle de visibilidade com PermissionGateV2
– Atleta vê apenas sua própria linha
– Comissão vê o coletivo

Essa página não salva nada, não edita nada.
Ela mostra o estado do processo.

Critério de sucesso (Definition of Done)

Você bate o olho e, em 30 segundos, consegue responder:
– Quem eu preciso cobrar?
– Quem eu preciso proteger?
– Posso seguir com o treino/jogo como está?

UX Explanation — Seleção Manual Obrigatória

Exigir seleção manual reforça consciência de contexto e evita decisões baseadas em dados errados. Em UX, isso reduz erros por auto-assunção e melhora a qualidade da decisão.

Princípios aplicados:

1. Context First (hard gate)
Sem contexto explícito, o sistema não mostra números. Isso previne leituras equivocadas e cumpre Error Prevention.

2. Escolha consciente > automação invisível
Automação é boa quando não muda decisões. Aqui, muda. Portanto, o usuário deve confirmar qual sessão está analisando.

3. Estado vazio instrutivo
Tela vazia não é erro. É orientação. O usuário entende o que precisa fazer para avançar.

HB Track Configuration — /statistics com seleção manual
Comportamento inicial da página

Ao acessar /statistics:

– Nenhuma métrica renderiza
– Exibe estado vazio guiado
– CTA claro: “Selecionar treino ou jogo”

1️⃣ Estado vazio (primeira carga)

Conteúdo obrigatório:

– Mensagem clara:
“Selecione um treino ou jogo para visualizar o controle operacional.”

– CTA primário: Selecionar sessão

Nada além disso.
Sem gráficos “cinza”, sem placeholders enganosos.

2️⃣ Modal de seleção de sessão (hard gate)

Abrir modal bloqueante com:

Campos obrigatórios:
– Tipo: Treino | Jogo
– Sessão (lista filtrada por equipe e temporada)

Regras de UX:
– Não fecha sem seleção válida
– Últimas sessões aparecem primeiro
– Sessões incompatíveis com permissões não aparecem

Ao confirmar:
– Fecha modal
– Renderiza a visão operacional completa

3️⃣ Header de contexto persistente

Após seleção, o topo da página deve mostrar:

Sessão selecionada
Equipe
Data
Status

Com ação secundária discreta: Trocar sessão

Isso evita ambiguidade durante toda a leitura.

4️⃣ Persistência controlada (opcional, recomendada)

Salvar a última sessão selecionada:
– Apenas por usuário
– Apenas para navegação interna
– Nunca assumir automaticamente em nova sessão crítica

UX correta aqui é lembrar, mas não decidir pelo usuário.

Regras de visibilidade e segurança

– Comissão vê todas as sessões permitidas
– Atleta só vê sessões próprias
– Nenhuma sessão → nenhum dado
– Troca de sessão → reload completo dos dados

Tudo passa pelo contexto de autenticação e permissões.

HB Track Configuration — Implementação objetiva
Rotas

/statistics
Visão operacional diária (comissão técnica)

/statistics/me
Visão individual do atleta (sem comparação)

/statistics — Fluxo exato

Entrada na rota

Renderiza apenas estado vazio instrutivo

Nenhum dado carregado

CTA

“Selecionar treino ou jogo”

Modal bloqueante
Campos obrigatórios:

Tipo: Treino | Jogo

Sessão (filtrada por equipe, temporada e permissão)

Regras:

Não fecha sem seleção válida

Sessões ordenadas da mais recente para a mais antiga

Sem sessão válida → sem dados

Após seleção

Header fixo com sessão, equipe, data e status

Botão discreto “Trocar sessão”

Carregamento dos dados operacionais

Blocos renderizados após seleção (ordem fixa)

Pendências do processo
Presença, wellness não respondido, atletas fora do fluxo, alertas ativos

Carga da sessão
Carga agregada + lista de atletas fora da zona segura

Lista operacional de atletas
Uma linha por atleta
Status visual claro
Ordenação por problema
Clique → perfil do atleta

Alertas persistentes
Não colapsáveis, não ignoráveis

/statistics/me — Atleta

Sem modal de seleção

Sessão mais recente do próprio atleta

Apenas dados individuais

Comparação apenas com histórico próprio ou zonas saudáveis

Linguagem interpretativa (“atenção”, “ok”, “em evolução”)

Nenhum ranking, nenhuma média da equipe

Regras técnicas obrigatórias (HB Track)

Server Component

Dados via /reports

Promise.all para sessão, presença, wellness, carga

Skeletons obrigatórios

PermissionGateV2 em todos os blocos

Comissão vê coletivo

Atleta nunca vê terceiros

Definition of Done (objetiva)

Em menos de 30 segundos, a comissão responde:

Quem está fora do processo

Quem exige ação hoje

Se a sessão pode acontecer com segurança

E o atleta responde:

Como estou

Onde melhorar

Sem comparação externa

VALIDAÇÃO REAL DOS /reports NO BACKEND HB TRACK
✅ O que EXISTE de forma canônica

De acordo com o RAG:

Existe /reports como fonte única de dashboards e estatísticas

O frontend já está orientado a consumir /reports

Há suporte a:

métricas de treino

wellness

carga

presença

alertas

O padrão correto é:

backend calcula

frontend apenas renderiza

Isso está 100% alinhado com o que você definiu.

❌ O que NÃO existe exatamente como nome/endpoint isolado

Os endpoints abaixo não existem ainda como rotas independentes:

/reports/session-attendance

/reports/wellness-compliance

/reports/engagement

/reports/session-operational-roster

/reports/training-load/session

/reports/training-load/recent-baseline

/reports/alerts/active

/reports/session-context

⚠️ Isso NÃO significa que os dados não existem.
Significa apenas que eles ainda não estão expostos como contratos claros e separados.

Hoje, o backend trabalha com:

relatórios mais genéricos

múltiplas responsabilidades por endpoint

lógica ainda espalhada

O QUE JÁ EXISTE EM DADOS (confirmado pelo RAG)

Os dados abaixo já existem no backend, mesmo que não estejam agrupados como você quer:

Presença (attendance / attendance_scoped)

Wellness pré e pós

Carga interna (RPE × minutos)

Alertas médicos

Vínculos atleta–sessão

Sessões de treino e jogos

Contexto de temporada, equipe e papel

Regras de visibilidade por papel

Ou seja: 100% da matéria-prima já existe.

CONCLUSÃO TÉCNICA (importante)

Você não precisa criar novos dados
Você não precisa mudar UX
Você não precisa mudar frontend

O que precisa ser feito é uma consolidação de relatórios, exatamente como você desenhou.

COMO ISSO DEVE SER FEITO CORRETAMENTE (sem refatoração grande)

A forma correta no HB Track é:

Opção recomendada (enterprise, limpa)

Manter UM endpoint canônico:

GET /reports/operational-session


Com parâmetros:

session_id

viewer_role

Esse endpoint retorna tudo que a página /statistics precisa, já organizado por bloco:

{
  "context": { ... },
  "process_status": { ... },
  "load_summary": { ... },
  "athletes": [ ... ],
  "alerts": [ ... ]
}


Internamente, ele:

reutiliza queries já existentes

centraliza regras

evita N chamadas no frontend

CONFIGURAÇÃO CANÔNICA
/reports/operational-session

Esse passa a ser o único endpoint que alimenta a rota:

/statistics (visão operacional diária)

UX Explanation — por que esse endpoint é o certo

Um dashboard operacional não pode depender de múltiplas chamadas nem de lógica no frontend.
O usuário precisa de uma verdade única, consistente, atômica e contextualizada.

Esse endpoint garante:

Coerência de leitura (todos os blocos usam o mesmo snapshot)

Performance

Menos risco de estado inconsistente

Frontend burro, backend inteligente (padrão enterprise)

CONTRATO FINAL DO ENDPOINT
Rota
GET /reports/operational-session

Query params obrigatórios
session_id=<uuid>

Contexto implícito

Derivado do token:

user_id

role_code

organization_id

season_id

team scope

RESPONSE — SHAPE CANÔNICO (FECHADO)
{
  "context": {
    "session_id": "uuid",
    "session_type": "training | match",
    "team": {
      "id": "uuid",
      "name": "CEPRAEA Sub-16"
    },
    "date": "2026-01-04",
    "status": "scheduled | ongoing | completed"
  },

  "process_status": {
    "total_athletes": 16,
    "present": 14,
    "absent": 2,
    "wellness_pending": 3,
    "inactive_engagement": 1
  },

  "load_summary": {
    "session_load_avg": 420,
    "team_baseline_avg": 390,
    "deviation_pct": 7.7,
    "out_of_zone_athletes": 2
  },

  "athletes": [
    {
      "athlete_id": "uuid",
      "name": "Maria Clara",
      "presence": "present",
      "wellness": "ok | pending",
      "load_status": "ok | alert",
      "overall_status": "ok | attention | critical"
    }
  ],

  "alerts": [
    {
      "type": "medical | load | attendance | compliance",
      "level": "critical | warning",
      "athlete_id": "uuid",
      "message": "Carga acima do limite nos últimos 3 dias"
    }
  ]
}

RESPONSABILIDADE DE CADA BLOCO (SEM AMBIGUIDADE)
Backend (obrigatório)

Calcula carga

Define zonas

Consolida status geral

Aplica regras por papel

Remove atletas fora de escopo

Decide alertas

Frontend (/statistics)

Renderiza blocos

Mostra estados

Ordena por overall_status

Não calcula nada

Não cruza dados

REGRAS DE VISIBILIDADE (CRÍTICAS)

Comissão técnica:

recebe todos os atletas da sessão

Atleta:

não consome esse endpoint

usa /statistics/me com outro contrato

Endpoint valida:

vínculo ativo

papel

sessão compatível

IMPLEMENTAÇÃO BACKEND (PASSOS OBJETIVOS)

Criar router:

app/api/v1/routers/reports_operational.py


Adicionar rota:

@router.get("/reports/operational-session")


Internamente reutilizar:

attendance

wellness_pre / wellness_post

training_sessions ou matches

team_registrations

medical flags

regras de carga já existentes

Nenhuma query nova “inventada”

Nenhuma regra duplicada no frontend

IMPLEMENTAÇÃO FRONTEND (SIMPLES)

Na rota /statistics:

Modal seleciona session_id

Server Component chama 1 endpoint

Renderiza:

Header

Pendências

Carga

Lista de atletas

Alertas

DEFINITION OF DONE (FINAL)

A feature está pronta quando:

/statistics funciona com 1 chamada

Nenhuma lógica de status existe no frontend

Um treinador entende tudo em <30 segundos

Um erro de contexto é impossível


1️⃣ Regras de PRESENÇA — ajuste necessário (baixo impacto)
Situação atual (RAG)

Presença existe e é correta (attendance, attendance_scoped)

Estados previstos: presente, ausente, DM, lesionado

Regra por temporada e vínculo já está correta

Ajuste necessário

Falta uma regra de fechamento operacional da sessão

Hoje:

Presença é correta individualmente
Falta:

Um estado consolidado da sessão, usado para decisão diária

Ajuste requerido

Criar regra derivada (apenas no relatório):

sessão_em_risco = true se:

ausentes > 0 OU

presença < X% configurável

Nenhuma mudança em tabela.
Apenas regra de agregação no /reports/operational-session.

2️⃣ Regras de WELLNESS — ajuste necessário (médio impacto)
Situação atual

Wellness pré e pós existem

Bloqueio de duplicidade existe

Regra por treino existe

Problema atual

O sistema não diferencia semanticamente:

wellness_pendente_aceitável (pré ainda dentro da janela)

wellness_pendente_crítico (pós não respondido após sessão)

Para UX operacional isso é crítico.

Ajuste requerido

Adicionar regra temporal no relatório:

wellness_status:

ok

pending_pre (antes do treino)

pending_post (crítico após sessão)

Isso não muda tabela, só classificação no relatório.

3️⃣ Regras de CARGA — ajuste necessário (importante)
Situação atual

Carga (RPE × minutos) existe

Dados brutos existem

Uso em relatórios já ocorre

Problema atual

A zona de risco não está formalizada como contrato único.

Hoje:

Carga é número

Interpretação é implícita

Ajuste obrigatório antes do endpoint

Formalizar no backend:

zona_carga: ok | alert | critical

Baseado em:

baseline recente (7 dias)

desvio percentual configurável

Essa regra precisa existir antes do /reports/operational-session, senão o frontend volta a interpretar carga (o que é proibido).

4️⃣ Regras de ENGAJAMENTO — ajuste necessário (baixo impacto)
Situação atual

Há dados de acesso, preenchimento, vínculo

Não existe conceito fechado de “fora do processo”

Ajuste requerido

Criar regra derivada no relatório:

engagement_status:

active

inactive

Exemplo de regra:

inactive se:

não respondeu wellness em X sessões OU

ausência recorrente

Sem nova tabela. Apenas consolidação.

5️⃣ Regras de ALERTAS — ajuste necessário (alto impacto UX)
Situação atual

Alertas existem

Notificação crítica bloqueante existe

Problema

Alertas não estão priorizados semanticamente.

Para a visão operacional, é obrigatório:

level: warning | critical

origem: medical | load | attendance | compliance

Ajuste requerido

Normalizar alertas retornados pelo relatório:

sem texto genérico

sempre com nível e tipo

Isso garante que o bloco “Alertas Persistentes” funcione sem lógica no frontend.

6️⃣ Regras de VISIBILIDADE — já corretas (nenhum ajuste)

Comissão vê coletivo

Atleta vê apenas dados próprios

Escopo por temporada/equipe está correto

PermissionGateV2 já reflete backend

Nenhum ajuste necessário aqui.



Este checklist não altera UX, não cria tabelas, não muda fluxos. Ele apenas fecha regras de negócio já existentes no nível correto (relatórios).

CHECKLIST — REGRAS DE NEGÓCIO (OBRIGATÓRIO)
1️⃣ Contexto da Sessão

Validar session_id pertence ao escopo do usuário (org, season, team).

Identificar session_type (training | match).

Determinar session_status (scheduled | ongoing | completed).

Se sessão inválida → retornar erro de domínio claro.

2️⃣ Presença (Attendance)

Consolidar presença por sessão:

total_athletes

present

absent (inclui DM/lesionadas conforme regra vigente)

Criar flag derivada:

session_risk = true se ausentes > 0 ou presença < limite configurável.

Não calcular presença no frontend.

3️⃣ Wellness (Pré e Pós)

Classificar wellness por contexto temporal:

ok

pending_pre (antes da sessão)

pending_post (após sessão concluída)

pending_post deve ser tratado como crítico.

Bloqueio de duplicidade permanece intacto.

4️⃣ Carga (Load)

Calcular carga interna da sessão (RPE × minutos).

Calcular baseline recente (ex.: 7 dias).

Formalizar zona de carga no backend:

ok

alert

critical

Retornar apenas status e agregados; números brutos são opcionais.

5️⃣ Engajamento (Aderência ao Processo)

Definir engagement_status por atleta:

active

inactive

Regra mínima:

inactive se não respondeu wellness em X sessões ou ausência recorrente.

Não expor métricas de acesso brutas no frontend.

6️⃣ Status Geral do Atleta

Derivar overall_status no backend:

critical → ausência ou wellness pós pendente ou carga crítica

attention → qualquer alerta isolado

ok → tudo conforme

Frontend apenas ordena e exibe.

7️⃣ Alertas

Normalizar alertas retornados pelo relatório:

type: medical | load | attendance | compliance

level: warning | critical

message: clara e acionável

Alertas críticos devem persistir até resolução.

8️⃣ Visibilidade e Escopo

Garantir exclusão de atletas fora do escopo da sessão.

Comissão técnica vê coletivo.

Atleta não consome este endpoint.

Nenhuma regra de permissão no frontend.

9️⃣ Performance e Consistência

Todas as regras acima aplicadas no mesmo snapshot.

Nenhuma lógica crítica no frontend.

Um único retorno JSON coerente.

Definition of Ready (objetiva)

O endpoint /reports/operational-session pode ser implementado quando:

Todas as regras acima estão consolidadas no backend.

Não existe cálculo de status no frontend.

A página /statistics depende de uma única chamada.

A leitura operacional é inequívoca em <30 segundos


VISÃO INDIVIDUAL DO ATLETA — PRINCÍPIO CENTRAL

A pergunta que essa tela responde é apenas uma:

“Como eu estou em relação a mim mesmo e no que focar agora?”

Se a tela responder qualquer coisa além disso, ela está errada.

CHECKLIST — REGRAS DE NEGÓCIO (/statistics/me)
1️⃣ Escopo e Contexto (hard rule)

Endpoint ignora session_id externo

Contexto é sempre:

atleta autenticado

sessões em que ele participou

Nunca retorna dados de terceiros

Nunca retorna ranking ou médias da equipe

2️⃣ Presença (Autopercepção)

Retornar:

presença no período

faltas recentes

sequência de presenças (streak)

Comparação permitida:

atleta vs histórico próprio

Comparação proibida:

atleta vs equipe

atleta vs outro atleta

UX: mostrar constância, não culpa.

3️⃣ Wellness (Consciência corporal)

Retornar:

wellness pré e pós do próprio atleta

tendência curta (ex.: últimos 7–14 registros)

Classificar:

stable

attention

declining

Nunca mostrar:

médias da equipe

“pior / melhor”

4️⃣ Carga (Proteção e educação)

Retornar:

carga por sessão (somente do atleta)

tendência temporal

zona saudável personalizada

Classificação obrigatória:

within_zone

above_zone

below_zone

Linguagem UX:

educativa (“atenção”, “equilíbrio”, “recuperação”)

nunca punitiva

5️⃣ Status Geral do Atleta

Derivado no backend:

ok

attention

Nunca usar critical para atleta
(regra psicológica importante)

Esse status serve para:

orientar conversa com treinador

não gerar ansiedade

6️⃣ Alertas (filtrados)

Atleta recebe apenas:

alertas pessoais

linguagem interpretativa

Nunca recebe:

alertas sistêmicos

alertas comparativos

Alertas não são bloqueantes para atleta

7️⃣ Linguagem e UX (regra não-negociável)

Sem cores agressivas

Sem rankings

Sem percentis

Sem tabelas comparativas

Foco em:

evolução

consistência

próximos passos

Essa tela não cobra, orienta.

ENDPOINT CANÔNICO RECOMENDADO
GET /reports/athlete-self

Response (shape conceitual)
{
  "context": {
    "athlete_id": "uuid",
    "period": "last_14_sessions"
  },
  "presence": { ... },
  "wellness": { ... },
  "load": { ... },
  "overall_status": "ok | attention",
  "insights": [
    "Sua carga está equilibrada",
    "Fique atenta à recuperação pós-treino"
  ]
}


Frontend não interpreta, apenas exibe.

Definition of Ready — /statistics/me

A visão individual do atleta está pronta quando:

Nenhuma comparação externa é possível

Nenhum dado coletivo é retornado

O atleta entende sua situação sem ansiedade

A tela incentiva adesão, não evasão

Backend decide tudo que é “status”

Relação entre as duas visões (importante)
Operacional (/statistics)	Atleta (/statistics/me)
Controle	Autoconhecimento
Exceções	Tendências
Alertas críticos	Orientações
Comparação permitida	Comparação proibida



Abaixo está o **pseudo-código FastAPI** dos **dois endpoints**, já **aplicando integralmente os checklists** que você aprovou. É código orientativo, fiel ao RAG, sem invenções de regra no frontend.

---

# 1) `/reports/operational-session`

**Uso:** `/statistics` (comissão técnica)
**Responsabilidade:** consolidar estado operacional da sessão em um snapshot único.

```python
# app/api/v1/routers/reports_operational.py

@router.get("/reports/operational-session")
def get_operational_session(
    session_id: UUID,
    ctx: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_db),
):
    # 1. CONTEXTO E ESCOPO
    session = get_session_or_404(db, session_id)
    assert_session_in_scope(session, ctx)  # org/season/team/role
    session_status = compute_session_status(session)

    # 2. ROSTER DA SESSÃO (escopo fechado)
    athletes = get_session_roster(db, session)

    # 3. PRESENÇA (AGREGADO + POR ATLETA)
    attendance = get_attendance_by_session(db, session_id)
    attendance_agg = aggregate_attendance(attendance, athletes)
    session_risk = (
        attendance_agg.absent > 0
        or attendance_agg.presence_rate < SETTINGS.MIN_PRESENCE_RATE
    )

    # 4. WELLNESS (CLASSIFICAÇÃO TEMPORAL)
    wellness = get_wellness_by_session(db, session_id)
    wellness_status = classify_wellness(
        wellness,
        session_status=session_status,
        now=utcnow()
    )
    wellness_pending_count = count_pending_wellness(wellness_status)

    # 5. CARGA (ZONAS FORMALIZADAS)
    load_by_athlete = compute_session_load(db, session_id)  # RPE × minutos
    baseline = compute_team_baseline(db, session.team_id, window_days=7)
    load_status = classify_load_zones(load_by_athlete, baseline)

    # 6. ENGAJAMENTO (ADERÊNCIA AO PROCESSO)
    engagement = compute_engagement_status(
        db,
        athletes,
        window_sessions=SETTINGS.ENGAGEMENT_WINDOW
    )

    # 7. STATUS GERAL POR ATLETA (BACKEND DECIDE)
    roster = []
    for a in athletes:
        overall = derive_overall_status(
            presence=attendance[a.id],
            wellness=wellness_status[a.id],
            load=load_status[a.id],
            engagement=engagement[a.id]
        )
        roster.append({
            "athlete_id": a.id,
            "name": a.name,
            "presence": attendance[a.id].status,
            "wellness": wellness_status[a.id].label,
            "load_status": load_status[a.id].zone,
            "overall_status": overall
        })

    # 8. ALERTAS NORMALIZADOS
    alerts = build_alerts(
        medical=get_medical_alerts(db, session),
        load=load_status,
        attendance=attendance,
        compliance=wellness_status,
    )

    # 9. RESPONSE ÚNICO (SNAPSHOT)
    return {
        "context": {
            "session_id": session.id,
            "session_type": session.type,
            "team": {"id": session.team_id, "name": session.team.name},
            "date": session.date,
            "status": session_status,
        },
        "process_status": {
            "total_athletes": len(athletes),
            "present": attendance_agg.present,
            "absent": attendance_agg.absent,
            "wellness_pending": wellness_pending_count,
            "inactive_engagement": count_inactive(engagement),
            "session_risk": session_risk,
        },
        "load_summary": {
            "session_load_avg": avg(load_by_athlete.values()),
            "team_baseline_avg": baseline.avg,
            "deviation_pct": deviation_pct(
                avg(load_by_athlete.values()), baseline.avg
            ),
            "out_of_zone_athletes": count_out_of_zone(load_status),
        },
        "athletes": sorted_by_overall_status(roster),
        "alerts": alerts,
    }
```

---

# 2) `/reports/athlete-self`

**Uso:** `/statistics/me` (atleta)
**Responsabilidade:** autoconhecimento sem comparação externa.

```python
# app/api/v1/routers/reports_athlete.py

@router.get("/reports/athlete-self")
def get_athlete_self(
    ctx: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_db),
):
    athlete = get_athlete_from_context(ctx)  # hard rule
    sessions = get_recent_sessions_for_athlete(
        db, athlete.id, limit=SETTINGS.SELF_WINDOW_SESSIONS
    )

    # 1. PRESENÇA (HISTÓRICO PRÓPRIO)
    presence = compute_presence_trends(db, athlete.id, sessions)

    # 2. WELLNESS (TENDÊNCIA CURTA)
    wellness = compute_wellness_trends(db, athlete.id, sessions)
    wellness_class = classify_wellness_trend(wellness)

    # 3. CARGA (ZONA PESSOAL)
    load = compute_load_by_athlete(db, athlete.id, sessions)
    load_zone = classify_personal_load_zone(load)

    # 4. STATUS GERAL (SEM “CRITICAL”)
    overall_status = derive_self_overall_status(
        wellness=wellness_class,
        load=load_zone,
        presence=presence
    )

    # 5. ALERTAS FILTRADOS (NÃO BLOQUEANTES)
    alerts = filter_personal_alerts(
        get_all_alerts(db, athlete.id)
    )

    return {
        "context": {
            "athlete_id": athlete.id,
            "period": f"last_{len(sessions)}_sessions",
        },
        "presence": presence,          # streaks, faltas recentes
        "wellness": wellness,          # tendência, sem médias da equipe
        "load": load,                  # histórico pessoal + zona
        "overall_status": overall_status,  # ok | attention
        "alerts": alerts,              # linguagem interpretativa
        "insights": generate_insights(
            presence, wellness_class, load_zone
        ),
    }
```

---

## Garantias Arquiteturais (confirmadas)

* Frontend **não calcula** status.
* Um endpoint por visão.
* Snapshot único por chamada.
* Atleta nunca recebe comparação.
* Comissão recebe exceções prontas.
Mapear exatamente quais funções já existem no backend e quais são wrappers novos
