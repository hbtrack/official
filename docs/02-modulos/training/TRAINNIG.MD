<!-- STATUS: NEEDS_REVIEW -->

Ok.

---

## 1. Explicação de UX

A rota `/training_sessions` não é uma tela de cadastro comum. Em termos de UX, ela é um **hub operacional de treinos**, usado em três momentos mentais distintos: antes do treino (planejamento rápido), durante/imediatamente após (registro sob pressão de tempo) e dias depois (consulta e decisão).

O erro clássico em sistemas esportivos é tentar resolver esses três momentos com uma única interface. A melhor prática, validada em produtos como Teamworks, Hudl e sistemas internos olímpicos, é aplicar **progressive disclosure**: mostrar apenas o que é relevante para o estado atual do treino.

Do ponto de vista cognitivo, o treinador opera sob **carga alta e tempo curto**. Isso exige:

* Poucas decisões por tela (Lei de Hick).
* Controles grandes e diretos (Lei de Fitts).
* Estados claros de progresso (heurística de visibilidade de status).

Outro princípio central é **estado explícito**. Um treino no HB Track não é “um formulário”, é uma entidade com ciclo de vida: rascunho → em andamento → fechado → somente leitura. UX madura torna esse estado visível e governa o que pode ou não ser editado, evitando erros e retrabalho.

Por fim, a UX precisa respeitar o domínio esportivo real: treinadores pensam em “quem treinou”, “como foi a carga”, “o foco do treino” e “se há risco”. A interface deve espelhar essa ordem mental, não a ordem do banco de dados.

---

## 2. Configuração da rota `/training_sessions` no HB Track

### 2.1 Estrutura da rota

Criar três rotas claras, evitando overload de uma única tela:

* `/training_sessions`
  Lista operacional de treinos.
* `/training_sessions/new`
  Criação rápida de treino.
* `/training_sessions/[id]`
  Visão operacional do treino (com estados).

Isso mantém consistência com o padrão já adotado no sistema (ex.: atletas, equipes) e reduz dívida técnica.

### 2.2 Lista de treinos (`/training_sessions`)

UX correta:

* Filtro obrigatório por equipe.
* Filtro secundário por período (7, 14, 30 dias).
* Cards ou tabela leve com:
  data, equipe, status, presença %, carga média, badge de risco.

Nada de gráficos aqui. Essa tela responde apenas: “qual treino eu preciso olhar agora?”.

### 2.3 Criação de treino (`/training_sessions/new`)

Criar em **menos de 10 segundos**.

Campos mínimos:

* Equipe (obrigatório).
* Data e tipo (treino normal, regenerativo, treino-jogo).
* Temporada (auto-preenchida se houver).

Estado inicial sempre como **rascunho** (conforme RF18). Nenhuma métrica pesada aqui. O objetivo é não bloquear o treinador antes do treino acontecer.

### 2.4 Visão do treino (`/training_sessions/[id]`)

Esta é a tela mais crítica de UX.

Organizar em blocos sequenciais, refletindo o fluxo mental real:

1. Contexto fixo no topo
   Equipe, data, status do treino, botão claro de “Fechar treino”.

2. Presença
   Lista automática de atletas via `team_registrations`. Estados simples: presente, ausente, DM, lesionada. Mostrar presença consolidada em tempo real.

3. Carga e RPE
   Campos rápidos, com média automática visível. Alertas apenas quando fora de faixa, nunca como bloqueio.

4. Focos de treino
   Os 7 sliders já definidos no RAG, com contador total visível. Preenchimento obrigatório apenas no fechamento do treino, nunca antes.

5. Wellness pós-treino (se aplicável)
   Compacto, sem obrigatoriedade imediata.

6. Estado do treino
   Ao fechar:

* Validar presença.
* Validar foco (>0 e soma ≤120).
* Tornar o treino somente leitura (R38).

### 2.5 Integração com estatísticas

Todo treino fechado alimenta diretamente:

* `/statistics` (operacional diário).
* `/statistics/teams` (correlação treino → jogo).

UX importante: deixar claro na interface que “treinos em rascunho não entram em relatórios”. Isso evita desconfiança nos dados.

---
Ok.

---

## 1. Explicação de UX

Quando o domínio de treinos passa a contemplar **microciclos, mesociclos e macrociclos**, a rota `/training_sessions` deixa de ser apenas operacional e passa a ser **estratégica de planejamento**. Em UX, isso muda completamente a hierarquia mental do usuário.

Treinadores **não pensam em treinos isolados**. Eles pensam em blocos temporais com objetivo claro. A melhor experiência surge quando a interface reflete essa lógica natural, seguindo o princípio de **correspondência com o modelo mental do usuário** (Nielsen).

O erro mais comum seria criar uma única tela que misture:
– planejamento anual
– planejamento semanal
– registro do treino do dia

Isso quebra a Lei de Hick (muitas opções simultâneas) e aumenta carga cognitiva. A solução correta é **separar níveis de decisão**, mantendo fluidez entre eles.

Outro princípio crítico é **progressão temporal explícita**. Micro, meso e macro não são “tipos de treino”, são **camadas de intenção**. UX madura trata essas camadas como contexto, não como campos soltos.

Por fim, a UX precisa equilibrar **liberdade do treinador** com **estrutura mínima para análise futura**. Isso significa planejar com flexibilidade, mas registrar com consistência suficiente para gerar estatística, correlação e aprendizado.

---

## 2. Configuração da rota `/training_sessions` no HB Track

### 2.1 Como a rota deve aparecer na sidebar

Na sidebar, **não use o nome “Training Sessions”** como item único. Isso é técnico demais e não reflete o domínio esportivo.

A melhor UX é um **submenu chamado “Treinos”**, com três níveis claros:

Treinos
– Planejamento
– Sessões
– Ciclos

Isso respeita a ordem mental do treinador: primeiro planeja, depois executa, depois analisa.

### 2.2 Função de cada sub-rota

**Treinos → Planejamento**
Visão semanal e mensal. Aqui entram:
– Planejamento de microciclo (semana)
– Objetivo do período
– Distribuição prevista de focos (físico, técnico, tático)
– Observações livres

Nada de presença ou carga real aqui. É intenção, não execução.

**Treinos → Sessões**
Corresponde à atual `/training_sessions`.
Uso diário, rápido, operacional.
Registro do treino realizado, presença, carga, RPE, focos reais.

Essa separação é fundamental em UX: evita confundir “o que planejei” com “o que aconteceu”.

**Treinos → Ciclos**
Visão estratégica:
– Mesociclos (ex.: 4–6 semanas)
– Macrociclo (temporada ou fase)
– Objetivos esportivos
– Relação com competições

Aqui o treinador enxerga coerência, não detalhes.

---

## 3. Impacto no banco de dados (sim, é necessário)

Sim, **é necessário aplicar novas tabelas**, mas com escopo controlado. Não se deve inflar `training_sessions`.

### Estrutura recomendada (alto nível)

1. **training_cycles**
   Representa macro e mesociclos.
   Campos essenciais:
   – id
   – team_id
   – type (macro | meso)
   – start_date
   – end_date
   – objective
   – notes

2. **training_microcycles**
   Representa o microciclo (semana).
   Campos:
   – id
   – team_id
   – cycle_id (FK para meso/macro)
   – week_start
   – week_end
   – planned_focus_distribution (json ou campos percentuais)

3. **training_sessions** (já existente)
   Adicionar apenas:
   – microcycle_id (FK opcional)
   – planned_session (boolean)

Nada mais. O treino continua sendo o treino.

Essa modelagem respeita o RAG: dados primários simples, dados estratégicos agregados e derivados.

---

## 4. Resultado em UX

Com essa estrutura:
– O treinador planeja sem atrito.
– Executa rápido no dia a dia.
– Analisa com clareza semanal e mensal.
– O sistema gera correlação real entre planejamento e performance.

Isso é UX de sistema profissional, não app genérico.

Ok.

Abaixo está o **fluxo completo de telas** do domínio de **Treinos** no HB Track, estruturado para refletir o modelo mental real do treinador (planejar → executar → avaliar), com mínima carga cognitiva e máxima utilidade decisória.

---

## 1. Entrada pela Sidebar (arquitetura de navegação)

**Sidebar → Treinos**

* Planejamento
* Sessões
* Ciclos

Essa separação evita sobreposição conceitual e reduz erros de uso. Cada item corresponde a um nível diferente de decisão.

---

## 2. Treinos → Ciclos (visão estratégica)

### Objetivo da tela

Definir **intenção de médio e longo prazo**. Esta tela é pouco acessada, mas altamente estratégica.

### Conteúdo da tela

* Lista de ciclos ativos e passados
* Tipo do ciclo: macrociclo ou mesociclo
* Período (datas)
* Objetivo principal
* Equipes vinculadas
* Status (ativo, encerrado)

### Ações possíveis

* Criar novo ciclo
* Editar objetivo/notas
* Encerrar ciclo

### Regras de UX

* Nenhuma métrica operacional
* Nenhuma presença, carga ou RPE
* Linguagem estratégica, não estatística

Saída natural do usuário: entrar no planejamento semanal.

---

## 3. Treinos → Planejamento (microciclo)

### Objetivo da tela

Planejar **a semana de treino** com clareza e flexibilidade.

### Estrutura principal

* Seletor de equipe
* Seletor de semana (microciclo)
* Indicador do ciclo maior ao qual pertence (meso/macro)

### Visão central

* Grade semanal (seg–dom)
* Cada dia mostra:

  * Tipo de treino previsto
  * Objetivo do dia
  * Distribuição planejada de focos (visual simples)
  * Observações livres

### Ações possíveis

* Criar microciclo
* Ajustar plano da semana
* Duplicar semana anterior
* Criar sessão planejada (atalho)

### Regras de UX

* Tudo aqui é **intenção**
* Nenhuma validação rígida
* Planejamento não gera estatística

Saída natural: clicar em um dia e ir para a sessão real.

---

## 4. Treinos → Sessões (lista operacional)

### Objetivo da tela

Responder rapidamente: “qual treino eu preciso registrar ou revisar agora?”

### Conteúdo

* Filtro obrigatório por equipe
* Filtro por período curto
* Lista de sessões com:

  * Data
  * Equipe
  * Status (rascunho, em andamento, fechada)
  * Presença %
  * Badge de risco (se houver)

### Ações

* Criar nova sessão
* Acessar sessão existente

Nenhum gráfico. Nenhuma análise profunda.

---

## 5. Sessão de treino (tela principal `/training_sessions/[id]`)

### Objetivo da tela

Registrar o treino **sob pressão de tempo**, sem erro.

### Blocos sequenciais (ordem fixa)

**1. Contexto fixo**

* Equipe, data, tipo
* Status visível
* Botão “Fechar treino”

**2. Presença**

* Lista automática de atletas
* Estados simples
* Presença consolidada em tempo real

**3. Carga e RPE**

* Entrada rápida
* Médias automáticas
* Alertas apenas informativos

**4. Focos do treino**

* 7 sliders
* Contador total
* Validação só no fechamento

**5. Wellness (opcional)**

* Compacto
* Não bloqueante

### Fechamento do treino

Ao fechar:

* Valida presença
* Valida focos
* Bloqueia edição
* Habilita uso analítico

---

## 6. Retorno analítico (feedback ao treinador)

Após o fechamento:

* Sessão passa a alimentar:

  * Estatística operacional diária
  * Correlação treino → jogo
* Interface deixa claro:
  “Este treino agora impacta relatórios.”

Isso gera confiança no sistema.

---

## 7. Fluxo resumido (mental do usuário)

1. Defino o ciclo (raramente)
2. Planejo a semana
3. Executo e registro o treino
4. Fecho a sessão
5. Analiso impacto depois

Esse fluxo **imita o trabalho real do treinador**, não o banco de dados.

---

Ok.

---

## 1. Explicação de UX

Fazer o **planejamento semanal influenciar automaticamente os focos da sessão** é uma decisão de UX madura, desde que seja **assistiva e não impositiva**. O princípio central aqui é *Human-in-the-loop*: o sistema sugere, o treinador decide.

Dois riscos precisam ser evitados.
O primeiro é o **over-automation**: travar focos com base no planejamento gera rejeição imediata, porque o treino real muda por contexto (número de atletas, clima, fadiga, imprevistos).
O segundo é a **invisibilidade da lógica**: se o sistema sugere algo sem explicar o porquê, o treinador perde confiança.

A solução correta segue três princípios clássicos de UX avançado:

* **Reconhecimento > lembrança**: o treinador não precisa lembrar o plano da semana; ele é apresentado no momento certo.
* **Defaults inteligentes**: sugestões pré-preenchidas reduzem esforço inicial.
* **Override explícito**: qualquer sugestão pode ser ajustada livremente, sem penalidade.

Em termos cognitivos, isso reduz tempo de preenchimento, aumenta consistência histórica e melhora a qualidade da análise sem aumentar carga mental.

---

## 2. Configuração no HB Track (fluxo e regras)

### 2.1 Regra de ouro (UX + domínio)

O planejamento **nunca escreve diretamente nos dados reais** da sessão.
Ele apenas gera **sugestões iniciais**, visíveis e editáveis.

Planejamento = intenção
Sessão = realidade

Essa separação mantém integridade analítica e evita vieses artificiais.

---

### 2.2 Comportamento na criação da sessão

Fluxo correto:

1. Sessão é criada a partir de um dia pertencente a um microciclo planejado.
2. O sistema verifica:

   * Existe `microcycle_id`?
   * Existe distribuição planejada de focos para esse dia?
3. Se sim:

   * Pré-preenche os **sliders de foco** com os valores planejados.
   * Exibe um rótulo claro:
     “Sugestão baseada no planejamento semanal”.

Nenhum bloqueio. Nenhuma obrigatoriedade.

---

### 2.3 UX na tela da sessão (`/training_sessions/[id]`)

No bloco **Focos do treino**:

* Sliders já posicionados conforme o planejamento.
* Um pequeno indicador textual:
  “Planejado: Ataque Posicional 30%, Transição 25%, Técnico 20%…”
* Ao alterar qualquer slider:

  * Indicador muda para:
    “Valores ajustados em relação ao planejamento”.

Isso cria consciência sem julgamento.

---

### 2.4 Feedback pós-fechamento (UX estratégica)

Após o fechamento do treino, armazenar **dois conjuntos conceituais**:

* Foco planejado (do microciclo)
* Foco realizado (da sessão)

Isso permite, no futuro:

* Mostrar divergência planejado × executado
* Aprender padrões reais de treino
* Melhorar planejamento futuro

Importante: **não transformar isso em nota ou score automático**. Apenas visualização comparativa.

---

## 3. Impacto necessário no banco de dados

Sim, é necessário um ajuste leve e correto.

### 3.1 Onde armazenar o planejamento

No nível de **microciclo** (ou dia do microciclo):

* Distribuição planejada de focos
  Pode ser:
* Campos percentuais espelhados aos focos reais, ou
* Um campo JSON estruturado

Esses dados **não pertencem** à `training_sessions`.

---

### 3.2 Ajuste mínimo em `training_sessions`

Adicionar apenas:

* `microcycle_id` (FK opcional)
* Nenhum campo novo de foco planejado

A sessão continua armazenando apenas o **real executado**.

---

## 4. Benefício final de UX

Com essa abordagem:

* O treinador preenche focos mais rápido.
* O sistema aprende sem impor.
* A análise ganha profundidade real.
* A confiança no dado aumenta.

Isso é exatamente como sistemas profissionais de alto rendimento operam.

Ok.

---

## 1. Explicação de UX

Alertar automaticamente quando o treino executado **foge muito do planejamento semanal** é uma funcionalidade de alto impacto, desde que o alerta seja **contextual, proporcional e não punitivo**. Em UX, isso se enquadra em *decision-support alerts*, não em *error alerts*.

Três princípios devem guiar o desenho.

**Proporcionalidade do alerta.** Alertas binários (“certo/errado”) geram rejeição. O correto é trabalhar com **desvio relevante**, definido por limiar configurável. A UX deve comunicar “houve uma diferença significativa” e não “você treinou errado”.

**Momento certo.** O alerta **não deve interromper o preenchimento** do treino. Interrupção durante input aumenta carga cognitiva e erros. O alerta deve aparecer **após o fechamento da sessão**, quando o treinador já concluiu a tarefa principal.

**Explicabilidade.** Todo alerta precisa responder implicitamente a três perguntas:

1. do que diferiu,
2. quanto diferiu,
3. por que isso importa.
   Sem isso, o alerta vira ruído e é ignorado (alert fatigue).

UX madura trata esse alerta como um **espelho de consciência**, não como fiscalização.

---

## 2. Configuração no HB Track

### 2.1 Regra conceitual (fundamental)

O alerta é **derivado**, nunca armazenado como dado primário.
Ele nasce da comparação entre:

* foco planejado do microciclo (intenção),
* foco executado da sessão (realidade).

Nada é bloqueado. Nada impede o fechamento do treino.

---

### 2.2 Lógica de desvio (backend)

Definir um limiar simples e explicável, por padrão:

* Desvio absoluto ≥ **20 pontos percentuais** em qualquer foco
  OU
* Desvio agregado ≥ **30%** entre planejamento e execução

Esses valores devem ser **configuráveis por organização**, mas com default sensato.

O backend calcula isso no fechamento da sessão e expõe no relatório operacional da sessão.

---

### 2.3 Onde o alerta aparece (UX correta)

**Nunca durante o preenchimento.**

Após o fechamento do treino, na tela `/training_sessions/[id]`, exibir um bloco leve:

“Diferença relevante entre planejamento e execução”

Abaixo, exemplos claros:

* Planejado: Transição Ofensiva 30% → Executado: 10%
* Planejado: Técnico Defensivo 15% → Executado: 35%

Sem cores agressivas. Amarelo neutro, não vermelho.

---

### 2.4 Comportamento no dia seguinte (UX estratégica)

Na rota `/statistics` (operacional diária), o treino aparece com um **badge discreto**:
“Desvio de planejamento”.

Clicar no badge leva direto à sessão, já com o bloco explicativo visível.

Isso respeita o fluxo real de decisão: o treinador percebe o alerta quando está analisando, não quando está registrando.

---

### 2.5 Justificativa opcional (sem obrigatoriedade)

UX avançada: permitir um campo opcional de justificativa pós-alerta, com textos rápidos:

* “Número reduzido de atletas”
* “Adaptação tática”
* “Condição física do grupo”
* “Outro”

Nunca obrigatório. Justificativa forçada gera preenchimento falso.

---

## 3. Impacto no banco de dados

Nenhuma nova tabela é obrigatória.

Apenas:

* Planejamento armazenado no microciclo (já previsto).
* Execução armazenada na sessão (já existente).
* Desvio calculado **on the fly** ou via relatório derivado.

Se quiser histórico analítico futuro, pode-se armazenar apenas:

* `planning_deviation_flag` (boolean derivado)
  Nada além disso.

---

## 4. Benefício real de UX

Com esse desenho:

* O treinador mantém autonomia.
* O sistema cria consciência estratégica.
* A análise semanal ganha profundidade.
* Não há rejeição nem fadiga de alertas.

Isso posiciona o HB Track como **assistente técnico**, não como fiscal.

Ok.

---

## Decisão recomendada: **ambos, porém em níveis diferentes**

A melhor experiência de UX — e a mais madura do ponto de vista organizacional — é tornar o alerta **visível imediatamente para a comissão técnica** e **visível de forma agregada e contextualizada para coordenação/direção**. Não é a mesma informação, nem o mesmo momento.

Abaixo explico o porquê e como implementar sem gerar ruído, controle excessivo ou quebra de confiança.

---

## 1. Explicação de UX

### Comissão técnica (treinador / assistentes)

Para quem executa o treino, o alerta tem função **operacional e reflexiva**.

Boas práticas de UX mostram que feedback imediato funciona melhor para quem está no controle direto da ação. Aqui, o alerta:

* Ajuda o treinador a perceber padrões (“tenho adaptado demais?”).
* Apoia ajustes no próximo microciclo.
* Não carrega julgamento hierárquico.

Por isso, o alerta **individual por sessão** deve ser sempre visível para a comissão técnica, diretamente na sessão e no operacional diário.

---

### Coordenação / direção

Para níveis hierárquicos acima, o alerta **não pode ser granular nem diário**. Mostrar “treino X desviou” cria microgestão e ansiedade organizacional — um erro clássico de UX em sistemas esportivos.

Para coordenação/direção, o valor está em **tendência**, não em evento isolado.

A UX correta aqui segue o princípio de **abstração progressiva**:

* Menos detalhe
* Mais contexto
* Frequência menor

O alerta só faz sentido se responder:

> “O planejamento está sendo respeitado ao longo da semana/mês?”

---

## 2. Configuração correta no HB Track

### 2.1 Comissão técnica (nível sessão)

Visibilidade:

* Tela `/training_sessions/[id]` após fechamento.
* Badge discreto em `/statistics` (operacional diário).

Conteúdo:

* Diferença planejado × executado por foco.
* Texto explicativo curto.
* Justificativa opcional.

Sem logs administrativos. Sem destaque excessivo.

---

### 2.2 Coordenação / direção (nível agregado)

Criar **visão agregada semanal/mensal**, nunca por sessão.

Onde:

* `/statistics/teams`
* ou painel específico de coordenação

Como mostrar:

* Percentual de sessões com desvio relevante no período.
* Distribuição dos tipos de desvio (ex.: físico acima do planejado).
* Nenhum link direto para “treino problemático”.

Exemplo de leitura:

* “Na última semana, 30% dos treinos divergiram do planejamento previsto.”
* “Principal ajuste recorrente: aumento de carga técnica.”

Isso transforma o alerta em **insight de gestão**, não em ferramenta de cobrança.

---

### 2.3 Regras de visibilidade (importante)

* Coordenação **não vê alertas individuais por sessão**.
* Direção **não recebe notificação automática**.
* Tudo é passivo e analítico.

Isso preserva:

* Autonomia do treinador.
* Confiança no sistema.
* Cultura de desenvolvimento, não vigilância.

---

## 3. Impacto técnico (mínimo)

Nenhuma tabela nova obrigatória.

Regras:

* Alerta individual: calculado no fechamento da sessão.
* Visão agregada: cálculo derivado por período (semana/mês).
* Controle de acesso via RBAC já existente.

---

## 4. Síntese da decisão

* Comissão técnica: alerta **detalhado, imediato, contextual**.
* Coordenação/direção: alerta **agregado, tardio, estratégico**.
* Nenhuma hierarquia vê o mesmo alerta do mesmo jeito.

Esse desenho é o que diferencia um **sistema de alto rendimento** de um sistema de controle.

Ok.

---

## 1. Explicação de UX

Fazer o sistema **aprender padrões recorrentes de desvio** e **sugerir ajustes no planejamento futuro** é o nível mais alto de maturidade em UX para plataformas de alto rendimento. O princípio central aqui é **aprendizado assistivo, não prescritivo**.

Há três regras de UX inegociáveis.

Primeiro, **o sistema nunca “corrige” o treinador**. Ele observa, identifica padrões estáveis no tempo e sugere hipóteses. Isso preserva autonomia e evita rejeição psicológica. Em termos de heurísticas de Nielsen, trata-se de *user control and freedom* aplicada à inteligência do sistema.

Segundo, **aprendizado só faz sentido com recorrência**, nunca com eventos isolados. UX ruim gera sugestões baseadas em um treino atípico. UX madura só sugere algo quando há repetição estatisticamente relevante, dentro de um mesmo contexto (equipe, fase da temporada, tipo de microciclo).

Terceiro, **a sugestão precisa ser explicável**. O treinador deve entender por que o sistema está sugerindo algo, com base em dados reais anteriores. Sistemas “caixa-preta” perdem credibilidade rapidamente no esporte.

O papel do HB Track aqui não é ser um “planejador automático”, mas um **espelho inteligente de comportamento real**.

---

## 2. Configuração do HB Track

### 2.1 O que o sistema deve aprender

O aprendizado deve focar apenas em **diferença recorrente entre planejado e executado**, cruzando:

* Tipo de microciclo (ex.: carga alta, recuperação, pré-jogo)
* Foco planejado
* Foco executado
* Frequência do desvio
* Direção do desvio (sempre mais físico, sempre menos transição, etc.)

Critério mínimo para aprendizado:

* Mesmo foco desviando
* Mesmo sentido
* Em pelo menos 3 microciclos semelhantes

Antes disso, o sistema **não sugere nada**.

---

### 2.2 Onde a sugestão aparece (UX correta)

As sugestões **não aparecem na sessão de treino**.

Elas aparecem apenas em **Treinos → Planejamento**, quando o treinador:

* Abre um novo microciclo
* Ou duplica um microciclo anterior

Nesse momento, o sistema exibe um bloco discreto:

“Sugestão baseada em treinos anteriores”

Exemplo de linguagem correta:
“Nos últimos 4 microciclos semelhantes, os treinos executados tiveram, em média, +15% de foco físico em relação ao planejado. Deseja ajustar o planejamento desta semana?”

Com ações claras:

* Aplicar sugestão
* Ignorar

Sem julgamento. Sem alerta.

---

### 2.3 Como a sugestão funciona tecnicamente

O sistema:

1. Identifica o contexto do microciclo (equipe, fase, tipo).
2. Busca histórico de microciclos equivalentes.
3. Calcula média de desvio por foco.
4. Se passar o limiar configurado, gera sugestão.

A sugestão:

* Ajusta apenas o **planejamento**
* Nunca altera dados históricos
* Nunca se aplica automaticamente

---

### 2.4 Impacto no banco de dados

Nenhuma tabela nova obrigatória para a V1.

Recomendação:

* Gerar sugestões **on the fly** via serviço analítico.
* Opcionalmente armazenar:

  * `suggestion_shown_at`
  * `suggestion_applied` (boolean)

Isso permite evoluir o sistema sem inflar o modelo.

---

## 3. Governança e confiança

Regras essenciais:

* Sugestões são visíveis apenas para comissão técnica.
* Coordenação vê apenas tendências agregadas, nunca sugestões individuais.
* O sistema não “aprende” se o treinador ignora repetidamente as sugestões.

Isso evita vieses e mantém o sistema como parceiro técnico, não avaliador.

---

## 4. Resultado final em UX

Com essa abordagem:

* O planejamento fica mais realista ao longo do tempo.
* O sistema aprende o **estilo real de treino** da equipe.
* A confiança cresce porque nada é imposto.
* A performance melhora por coerência, não por controle.

Ok.

---

## 1. Explicação de UX

Adotar **aprendizado em dois níveis (equipe + organização)** é a decisão mais avançada possível sem quebrar confiança ou autonomia. Em UX, isso se chama **inteligência hierárquica contextualizada**.

O ponto crítico é: **o mesmo dado não pode ter o mesmo significado para públicos diferentes**.

Para o treinador, o sistema aprende o **estilo real daquela equipe**. Para a coordenação, o sistema identifica **padrões estruturais da organização**. Misturar esses níveis gera sensação de vigilância e rejeição. Separá-los gera valor.

Três princípios sustentam essa decisão.

**Context first.** Todo aprendizado nasce no nível mais próximo da ação (equipe). Só depois é agregado. Isso respeita o princípio de proximidade cognitiva: quem executa vê detalhe, quem coordena vê tendência.

**Assimetria de poder refletida na interface.** O treinador recebe sugestões acionáveis. A coordenação recebe insights comparativos. Ninguém vê “o que não deveria ver”.

**Aprendizado explicável em camadas.** O sistema nunca diz “faça isso”. Ele diz “isso costuma acontecer”. Essa linguagem preserva autoridade técnica humana, essencial no esporte.

---

## 2. Configuração no HB Track

### 2.1 Nível 1 — Aprendizado por equipe (operacional-técnico)

**Escopo**

* Equipe específica
* Microciclos semelhantes
* Planejado × executado

**O que o sistema aprende**

* Focos que sistematicamente aumentam ou diminuem
* Direção do desvio
* Intensidade média do ajuste

**Onde aparece (UX correta)**

* Apenas em **Treinos → Planejamento**
* Ao criar ou duplicar microciclo

**Formato da sugestão**
Texto curto, explicável e acionável:
“Nos últimos 5 microciclos desta equipe, os treinos executados tiveram em média +12% de foco físico em relação ao planejado. Deseja ajustar o planejamento?”

Ações:

* Aplicar
* Ignorar

Nada automático. Nada obrigatório.

---

### 2.2 Nível 2 — Aprendizado transversal (coordenação / direção)

**Escopo**

* Todas as equipes da organização
* Mesociclos ou períodos comparáveis
* Somente dados agregados

**O que o sistema aprende**

* Tendências comuns entre equipes
* Padrões recorrentes de desvio (ex.: físico acima do planejado em categorias de base)
* Diferença entre categorias, gêneros ou fases da temporada

**Onde aparece**

* `/statistics/teams` (visão de coordenação)
* Painel analítico, nunca operacional

**Formato**
Leitura estratégica, não interventiva:
“Em 4 das 6 equipes da organização, treinos executados apresentam maior foco técnico-defensivo do que o planejado nos microciclos intermediários.”

Sem links para sessões. Sem nomes de treinadores. Sem ranking.

---

## 3. Regras de governança (críticas)

Estas regras devem ser explícitas no sistema:

* Sugestões por equipe: **visíveis só para a comissão técnica**
* Padrões transversais: **visíveis só para coordenação/direção**
* Coordenação **não vê** sugestões individuais aplicadas ou ignoradas
* O sistema **não aprende** a partir de sugestões ignoradas repetidamente

Isso mantém:

* Confiança
* Autonomia
* Cultura de desenvolvimento

---

## 4. Impacto técnico

Nenhuma tabela nova obrigatória.

Implementação recomendada:

* Serviços analíticos separados:

  * `TeamTrainingPatternService`
  * `OrganizationTrainingPatternService`
* Cálculo sob demanda
* Cache por período

Opcional:

* Log leve de sugestão exibida/aplicada para evolução futura do modelo

---

## 5. Resultado final em UX

Com essa arquitetura:

* O treinador sente que o sistema o entende.
* A coordenação enxerga coerência ou desalinhamento estrutural.
* O HB Track se posiciona como **sistema inteligente de alto rendimento**, não como software de controle.

Ok.

---

## 1. Explicação de UX

Expandir as **sugestões inteligentes** para abranger **focos de treino**, **carga semanal** e **distribuição de tipos de sessão** é correto desde que se preserve uma regra central de UX: **sugestão ≠ prescrição**.

Há três fundamentos que tornam essa decisão segura e eficaz.

**Separação de camadas decisórias.** Focos de treino, carga semanal e tipo de sessão operam em níveis diferentes de decisão. Focos são táticos (conteúdo), carga é fisiológica (dose) e tipo de sessão é estrutural (organização da semana). UX madura sugere cada uma dessas camadas de forma **independente**, evitando “pacotes fechados” que reduzem controle do treinador.

**Economia cognitiva.** Treinadores já fazem esses ajustes intuitivamente. O sistema não deve criar novos campos ou formulários; deve **revelar padrões já existentes** e oferecer atalhos de ajuste. Isso reduz tempo de planejamento e aumenta coerência histórica.

**Explicabilidade contextual.** Quanto mais impactante a sugestão (ex.: reduzir carga), maior precisa ser a clareza do motivo. O sistema deve sempre ancorar a sugestão em dados observáveis: recorrência, direção do desvio e contexto do microciclo.

O erro a evitar é sugerir tudo ao mesmo tempo. A UX correta prioriza **uma sugestão por camada**, quando há evidência suficiente.

---

## 2. Configuração no HB Track

### 2.1 Onde as sugestões aparecem

As sugestões aparecem **exclusivamente em Treinos → Planejamento**, no momento de:

* criar um novo microciclo,
* duplicar um microciclo anterior.

Nunca aparecem em sessões, estatísticas diárias ou telas operacionais.

---

### 2.2 Tipos de sugestão (três camadas)

#### A. Sugestões de foco de treino (conteúdo)

Base: planejamento × execução recorrente.

Exemplo de UX:
“Nos últimos 4 microciclos semelhantes, o foco físico executado foi em média +12% maior que o planejado.”

Ação:

* Aplicar ajuste de foco
* Ignorar

Impacto:

* Ajusta apenas os percentuais planejados do microciclo.

---

#### B. Sugestões de carga semanal (dose)

Base: soma real de carga (RPE × minutos) × planejamento previsto.

Exemplo de UX:
“A carga semanal executada tem sido consistentemente maior do que o planejado neste tipo de microciclo.”

Ação:

* Reduzir carga planejada da semana
* Manter planejamento

Nunca sugerir valores exatos fechados; apenas direção (reduzir / manter / redistribuir).

---

#### C. Sugestões de distribuição de tipos de sessão (estrutura)

Base: diferença recorrente entre sessões planejadas e realizadas.

Exemplo de UX:
“Em microciclos como este, sessões regenerativas têm sido substituídas por sessões técnicas em 3 das últimas 4 semanas.”

Ação:

* Ajustar tipo de uma sessão
* Ignorar

O sistema **não cria sessões novas automaticamente**.

---

### 2.3 Ordem e prioridade das sugestões (UX crítica)

As sugestões devem seguir esta hierarquia visual:

1. Focos de treino
2. Carga semanal
3. Tipos de sessão

Nunca exibir mais de **uma sugestão por camada** ao mesmo tempo. Isso evita sobrecarga e mantém controle humano.

---

## 3. Impacto no banco de dados

Nenhuma nova tabela obrigatória.

Pré-requisitos já existentes:

* Focos planejados no microciclo
* Focos executados nas sessões
* Carga real (RPE × minutos)
* Tipo de sessão

Sugestões são:

* Calculadas via serviço analítico
* Aplicadas apenas ao planejamento
* Nunca persistidas como dado primário

Opcionalmente, registrar:

* sugestão exibida
* sugestão aplicada (boolean)

---

## 4. Resultado final em UX

Com esse desenho:

* O sistema aprende sem impor.
* O planejamento se aproxima da realidade ao longo do tempo.
* O treinador mantém autoridade total.
* A coordenação ganha coerência estrutural sem microgestão.

O HB Track passa a atuar como **assistente técnico inteligente**, alinhado ao alto rendimento.

Ok.

---

## 1. Explicação de UX

Explicar **visualmente a evolução do planejamento ao longo da temporada** é uma das ferramentas mais poderosas para gerar **aprendizado real** sem gerar julgamento. Em UX avançado, isso se chama **reflective visualization**: o sistema não diz o que fazer, ele mostra como as decisões evoluíram frente à realidade.

Há três princípios essenciais aqui.

**Temporalidade visível.** Planejamento esportivo só faz sentido no tempo. Mostrar “antes e depois” isolados é fraco. A UX correta revela **trajetória**: como o plano inicial foi sendo ajustado semana a semana conforme execução, carga e contexto.

**Comparação semântica, não numérica crua.** Treinadores não querem ler tabelas de percentuais históricos. Eles querem enxergar padrões: “planejava mais físico no início”, “passei a priorizar técnico”, “reduzi carga perto da competição”. Visualizações devem privilegiar forma e tendência, não precisão matemática excessiva.

**Separação entre intenção e realidade.** UX madura nunca mistura esses conceitos no mesmo traço sem legenda clara. Planejado e executado devem ser distinguíveis, sempre com linguagem neutra. Caso contrário, a visualização vira julgamento implícito.

O maior erro a evitar é transformar isso em “avaliação do treinador”. Essa visualização é **pedagógica**, não avaliativa.

---

## 2. Configuração no HB Track

### 2.1 Onde essa visualização deve existir

Criar uma seção específica dentro de:

**Treinos → Planejamento → Evolução da Temporada**

Nunca colocar isso em `/statistics` operacional. O momento mental aqui é reflexivo, não decisório imediato.

Acesso:

* Comissão técnica: visão detalhada da própria equipe.
* Coordenação: visão agregada por equipe (sem detalhe de sessões).

---

### 2.2 Estrutura da visualização (UX recomendada)

#### Bloco 1 — Linha do tempo da temporada

Uma linha horizontal com:

* Microciclos
* Marcos importantes (início de mesociclo, competição, pausa)

Serve como âncora cognitiva.

---

#### Bloco 2 — Evolução dos focos de treino

Gráfico de área ou linhas sobrepostas com:

* Planejado (linha contínua clara)
* Executado (linha tracejada)

Mostrar:

* Tendência por foco (ataque, defesa, físico etc.)
* Destaques automáticos apenas quando há mudança consistente, não pontual

Legenda sempre explícita: “planejado” vs “executado”.

---

#### Bloco 3 — Evolução da carga semanal

Visual simples:

* Faixa planejada
* Carga executada real

Objetivo não é precisão fisiológica, mas coerência: carga subindo, estabilizando ou caindo ao longo da temporada.

---

#### Bloco 4 — Mudanças estruturais no planejamento

Resumo textual assistido:
“Ao longo da temporada, o planejamento passou a priorizar sessões técnicas em detrimento de regenerativas nas semanas intermediárias.”

Esse texto é **gerado**, mas editável ou ocultável.

---

### 2.3 Regras de UX importantes

* Não exibir alertas nessa tela.
* Não usar cores de erro.
* Não mostrar rankings entre semanas.
* Sempre permitir alternar: “ver apenas planejamento”, “ver apenas executado”.

Controle do usuário é central.

---

## 3. Impacto técnico

Nenhuma tabela nova obrigatória.

Dados já existentes:

* Planejamento por microciclo
* Execução por sessão
* Carga real agregada semanalmente

Implementação:

* Serviço analítico que consolida por semana/microciclo
* Renderização frontend sob demanda
* Cache por período

---

## 4. Valor final para o HB Track

Com essa visualização:

* O treinador entende como seu planejamento evoluiu de forma orgânica.
* O sistema ensina sem confrontar.
* A coordenação enxerga maturidade do processo, não “erros”.
* O HB Track se diferencia como **plataforma de aprendizagem esportiva**, não apenas de controle.

Ok.

A decisão de ter **as duas visualizações (contínua e segmentada por fase)** é correta e necessária. A UX ideal não escolhe entre elas; **orquestra quando cada uma aparece e para quem**.

---

## 1. Explicação de UX

Essas duas leituras atendem **modelos mentais diferentes**, ambos legítimos no alto rendimento.

### Visualização contínua (linha da temporada)

Atende ao pensamento **longitudinal** do treinador experiente:
“Como meu planejamento evoluiu ao longo do ano?”

Princípios de UX envolvidos:

* Continuidade temporal reduz vieses de memória.
* Permite identificar tendências lentas (ex.: aumento progressivo de carga).
* Favorece aprendizado reflexivo, não decisão imediata.

É a visualização certa para **autocrítica técnica** e consolidação de método.

---

### Visualização segmentada por fase

Atende ao pensamento **situacional e competitivo**:
“O que mudou quando entramos em competição?”
“Como treinamos diferente na pré-temporada?”

Princípios de UX envolvidos:

* Chunking cognitivo: fases reduzem complexidade.
* Comparação semântica entre contextos distintos.
* Melhor leitura para coordenação e direção.

É a visualização certa para **decisão estratégica e alinhamento institucional**.

---

O erro seria misturar as duas leituras no mesmo gráfico sem controle. A solução correta é **camadas de leitura com alternância explícita**.

---

## 2. Configuração no HB Track (como implementar)

### 2.1 Onde isso vive no sistema

**Treinos → Planejamento → Evolução da Temporada**

Essa tela é reflexiva e estratégica. Nunca operacional.

---

### 2.2 Controle principal de UX (chave da experiência)

No topo da tela, um controle claro:

Modo de visualização:

* Temporada completa
* Por fase competitiva

Esse toggle muda **a lógica de leitura**, não apenas o filtro visual.

---

### 2.3 Modo 1 — Temporada completa (contínuo)

O que mostrar:

* Linha do tempo contínua por microciclo
* Focos planejados vs executados
* Carga semanal planejada vs real

UX rules:

* Linhas suaves
* Destaques apenas para mudanças consistentes
* Sem divisões duras

Uso típico:

* Treinador
* Análise de método
* Pós-temporada ou pausas longas

---

### 2.4 Modo 2 — Por fase competitiva (segmentado)

Fases derivadas da temporada:

* Pré-temporada
* Competição
* Transição / pausa
  (ou definidas manualmente, se quiser mais controle)

O que mostrar:

* Cards ou blocos por fase
* Média de focos planejados vs executados
* Carga média da fase
* Distribuição de tipos de sessão

UX rules:

* Comparação entre fases
* Texto-resumo automático por fase
* Leitura rápida e executiva

Uso típico:

* Coordenação
* Direção
* Ajustes de planejamento macro

---

### 2.5 Regras de visibilidade (governança)

* Comissão técnica:

  * Acesso total aos dois modos, por equipe.
* Coordenação/direção:

  * Acesso prioritário ao modo segmentado.
  * Modo contínuo apenas agregado, sem detalhe fino.

Isso preserva autonomia e evita microgestão.

---

## 3. Impacto técnico

Nenhuma tabela nova é obrigatória.

Pré-requisitos já existentes:

* Microciclos com período
* Sessões com data e focos
* Temporadas com datas

Derivações:

* Fase competitiva pode ser:

  * inferida por data,
  * ou configurada por temporada (campo leve, opcional).

Tudo calculado de forma derivada.

---

## 4. Resultado final em UX

Com as duas visualizações:

* O treinador entende **como e por que** seu planejamento evoluiu.
* A coordenação enxerga coerência estrutural.
* O sistema ensina sem julgar.
* O HB Track atinge nível de **plataforma de aprendizagem esportiva**, não só gestão.

Ok.

---

## 1. Explicação de UX

Alimentar **automaticamente relatórios de fim de mesociclo (mensal)** e **fim de temporada** é a evolução natural de um sistema que já coleta, interpreta e aprende com o uso real. Do ponto de vista de UX, isso transforma o HB Track em um **sistema de síntese**, não apenas de visualização.

Três princípios são críticos.

**Automação silenciosa.** O relatório não deve exigir ação manual para existir. Ele é gerado automaticamente a partir do uso normal do sistema. UX madura elimina tarefas administrativas que não agregam valor técnico.

**Narrativa técnica, não estatística bruta.** Relatórios eficazes contam uma história coerente: intenção inicial, ajustes feitos, padrão real de treino e implicações esportivas. Tabelas extensas reduzem leitura; sínteses visuais + texto explicativo aumentam retenção e tomada de decisão.

**Adequação ao horizonte temporal.** Um mesociclo responde a “o que aconteceu neste bloco?”. Uma temporada responde a “como nosso método evoluiu?”. Misturar esses níveis no mesmo relatório gera confusão cognitiva. Cada relatório deve ter estrutura própria, embora compartilhem a mesma base de dados.

Esses relatórios não são para fiscalização. São para **aprendizado institucional**.

---

## 2. Configuração no HB Track

### 2.1 Onde os relatórios vivem

Criar uma área clara e previsível:

**Treinos → Relatórios**

* Relatório de Mesociclo
* Relatório de Temporada

Não misturar com `/statistics`. Estatística é leitura pontual; relatório é síntese formal.

---

### 2.2 Relatório de Mesociclo (mensal)

**Geração**

* Automática ao final do período do mesociclo.
* Regerado se dados atrasados forem consolidados (sem versionar rascunhos).

**Conteúdo essencial**

* Objetivo planejado do mesociclo.
* Evolução dos focos: planejado × executado (visual resumido).
* Carga semanal média e tendência.
* Distribuição real de tipos de sessão.
* Principais desvios recorrentes (sem alerta, apenas constatação).
* Texto-síntese gerado automaticamente, com linguagem neutra.

**UX**

* Leitura em 2–3 minutos.
* Exportável (PDF).
* Editável apenas no campo de observações finais (opcional).

Público:

* Comissão técnica
* Coordenação

---

### 2.3 Relatório de Temporada

**Geração**

* Automática no encerramento da temporada.
* Pode ser visualizado a qualquer momento como “prévia”.

**Conteúdo essencial**

* Evolução longitudinal do planejamento (linha contínua).
* Comparação entre fases competitivas.
* Como o planejamento inicial foi ajustado ao longo do ano.
* Tendências estáveis de foco, carga e estrutura.
* Síntese técnica da temporada (texto assistido).

**UX**

* Estrutura clara por seções.
* Visualizações comparativas, não densas.
* Linguagem institucional e técnica.

Público:

* Comissão técnica (detalhado)
* Coordenação/direção (visão estratégica)

---

### 2.4 Governança e regras importantes

* Relatórios são **somente leitura**.
* Não exibem “erros”, apenas padrões.
* Coordenação não vê sessões individuais.
* Nenhum ranking entre equipes ou treinadores.

Isso preserva confiança e cultura de desenvolvimento.

---

## 3. Impacto técnico

Nenhuma tabela nova obrigatória.

Relatórios são:

* Derivados dos dados existentes (planejamento, sessões, carga).
* Gerados por serviços analíticos.
* Cacheados por período.

Opcional:

* Persistir snapshot final do relatório (PDF ou JSON) para histórico institucional.

---

## 4. Resultado final

Com essa arquitetura:

* O sistema “fecha o ciclo” do treinamento.
* O planejamento vira método documentado.
* A comissão técnica aprende com o próprio histórico.
* A organização constrói memória esportiva.

Ok.

---

## 1. Explicação de UX

Permitir um **campo de interpretação final do treinador** nos relatórios oficiais é decisivo para transformar automação em **aprendizado humano validado**. Em UX avançado, isso resolve um problema clássico: relatórios automáticos são corretos, mas **incompletos sem contexto**.

Três princípios sustentam essa escolha.

**Autoridade técnica preservada.** O sistema sintetiza dados; quem dá sentido final é o treinador. Isso atende à heurística de *user control and freedom* e evita a percepção de que o software “avaliou” o trabalho humano.

**Memória institucional qualificada.** Dados mostram o “o que aconteceu”; a interpretação explica o “por quê”. Em ciclos longos, essa camada narrativa é o que permite aprendizado real na temporada seguinte.

**Encerramento cognitivo.** O campo final funciona como ritual de fechamento do mesociclo/temporada. UX bem desenhada cria esse momento explícito, evitando relatórios frios e desconectados da prática.

O erro a evitar é transformar esse campo em obrigação extensa. Ele deve ser **curto, guiado e opcional**, mas valorizado.

---

## 2. Configuração no HB Track

### 2.1 Onde o campo aparece

No **Relatório de Mesociclo** e no **Relatório de Temporada**, sempre **ao final do documento**, após gráficos e sínteses automáticas.

Título claro:
**Interpretação Técnica do Treinador**

Isso deixa explícito que é uma leitura humana complementar, não correção do sistema.

---

### 2.2 Estrutura do campo (UX recomendada)

Campo único de texto, com apoio leve:

* Placeholder orientador, por exemplo:
  “Contextualize os principais ajustes feitos, limitações enfrentadas e aprendizados deste período.”

* Contador de caracteres visível (ex.: 1.000–1.500).
  Limite evita relatórios longos e melhora legibilidade futura.

* Salvamento explícito com feedback claro:
  “Interpretação registrada no relatório oficial.”

Nada de autosave silencioso aqui. O ato de salvar é simbólico.

---

### 2.3 Regras de edição e governança

* Editável apenas por:

  * Treinador responsável
  * Coordenador (opcional, se quiser permitir complemento)
* Janela de edição:

  * Até o encerramento do próximo ciclo
* Após isso:

  * Campo fica somente leitura
  * Qualquer alteração exige nova versão (opcional)

Isso garante integridade histórica.

---

### 2.4 Como isso aparece para outros perfis

* Comissão técnica:

  * Vê o texto completo.
* Coordenação/direção:

  * Vê o texto como parte do relatório, sem edição.
* Nunca usar esse texto para métricas, rankings ou comparações.

É **registro institucional**, não insumo analítico.

---

## 3. Impacto técnico

Necessário **um ajuste simples**.

Opções recomendadas:

* Campo `coach_interpretation` associado ao relatório (mesociclo/temporada)
* Metadados:

  * autor
  * data de registro
  * versão

Nenhuma alteração em `training_sessions`.

---

## 4. Resultado final em UX

Com esse campo:

* O relatório deixa de ser “gerado pelo sistema” e passa a ser **assinado pelo treinador**.
* O HB Track cria memória esportiva de alto nível.
* A tecnologia apoia, mas não substitui, o raciocínio técnico.
* A confiança institucional no sistema aumenta.

Ok.

---

## 1. Explicação de UX

Fazer a **interpretação final do treinador alimentar automaticamente o planejamento da próxima temporada** é o fechamento correto do ciclo de UX orientado a aprendizado. O princípio central é **continuidade cognitiva**: o sistema não “recomeça do zero”; ele carrega memória qualificada para o próximo ciclo decisório.

Três fundamentos garantem boa UX.

**Contexto reapresentado no momento certo.** A interpretação só tem valor quando reaparece **no início do novo planejamento**, não durante a execução. Isso respeita o fluxo mental do treinador e evita interferência operacional.

**Sugestão passiva, nunca prescritiva.** O texto do treinador vira **referência contextual** e **insumo de sugestão**, não regra. O sistema destaca trechos-chave e padrões, mas não impõe metas.

**Rastreabilidade temporal.** O usuário precisa ver claramente: “isto veio do relatório anterior”. Transparência mantém confiança e evita sensação de viés automático.

Armadilha a evitar: converter texto humano em decisões automáticas. O papel do sistema é **lembrar e sugerir**, não decidir.

---

## 2. Configuração no HB Track

### 2.1 Onde a herança aparece no fluxo

Ao criar:

* **Novo macrociclo** ou
* **Primeiro mesociclo da temporada**

o sistema abre um **Painel de Continuidade** no topo do planejamento.

Título claro:
**Referências da Temporada Anterior**

---

### 2.2 O que é carregado automaticamente

Do relatório anterior (mesociclo final + temporada):

1. **Interpretação final do treinador**
   Exibida em bloco colapsável, somente leitura, com autor e data.

2. **Síntese assistida pelo sistema**
   Trechos destacados (não reescritos), por exemplo:

* “A carga real ficou acima do planejado no início.”
* “Sessões técnicas substituíram regenerativas nas semanas intermediárias.”

Essa síntese é explicativa, não conclusiva.

---

### 2.3 Como isso influencia o novo planejamento

No **planejamento do micro/mesociclo**, o sistema pode:

* Pré-sugerir ajustes de **focos** com base nos padrões recorrentes anteriores.
* Sugerir atenção à **carga** (direção, não valor).
* Sugerir revisão da **distribuição de tipos de sessão**.

UX importante:

* Cada sugestão traz o rótulo: “Baseado na temporada anterior”.
* Botões claros: Aplicar | Ignorar.
* Nenhuma aplicação automática.

---

### 2.4 Controles do usuário (UX crítica)

* Toggle: “Mostrar referências anteriores”.
* Opção: “Não usar referências nesta temporada”.

Respeitar controle explícito evita rejeição e mantém autonomia técnica.

---

## 3. Governança e permissões

* Comissão técnica:

  * Vê e usa as referências no planejamento.
* Coordenação/direção:

  * Vê as referências como contexto estratégico, sem editar.
* Nada disso é usado para avaliação de desempenho.

---

## 4. Impacto técnico (mínimo e seguro)

Adicionar relação leve:

* `previous_season_report_id` no novo planejamento (opcional).
* Reuso do campo `coach_interpretation` já existente.

Sem alteração em `training_sessions`.

---

## 5. Resultado final em UX

Com essa herança:

* O planejamento ganha continuidade real.
* O aprendizado vira método.
* O treinador sente o sistema como parceiro de longo prazo.
* O HB Track se consolida como **plataforma de memória esportiva e inteligência aplicada**.

Ok.

---

## 1. Explicação de UX

Tornar a **herança obrigatória no primeiro planejamento da temporada** é a decisão correta para garantir **continuidade metodológica** sem retirar autonomia. Em UX, isso é chamado de **forced exposure with optional adoption**: o sistema **mostra** o contexto anterior de forma obrigatória, mas **não obriga a usá-lo**.

Por que isso funciona:

* **Previne amnésia organizacional.** O maior erro no início de temporada é “resetar” decisões sem considerar aprendizados reais. A exposição obrigatória reduz esse viés.
* **Respeita o controle do usuário.** Obrigatório visualizar ≠ obrigatório aplicar. A heurística de *user control and freedom* é preservada.
* **Cria ritual de início de ciclo.** UX madura marca transições importantes com momentos explícitos. O primeiro planejamento da temporada é um deles.

Armadilha a evitar: bloquear o avanço até “aceitar” sugestões. O correto é **confirmar ciência**, não concordância.

---

## 2. Configuração do HB Track

### 2.1 Quando a herança é acionada

No **primeiro acesso ao Planejamento** da nova temporada (macrociclo inicial ou primeiro mesociclo), o sistema exibe um **Painel de Continuidade** antes da edição.

Condição:

* Temporada nova detectada
* Existe relatório final da temporada anterior (ou mesociclo final)

---

### 2.2 Painel de Continuidade (obrigatório visualizar)

Conteúdo:

1. **Interpretação final do treinador (temporada anterior)**
   Somente leitura, com autor e data.
2. **Síntese assistida do sistema**
   Destaques de padrões recorrentes (focos, carga, tipos de sessão).

Ações disponíveis:

* “Confirmar leitura e prosseguir”
* “Prosseguir sem aplicar sugestões”

Não existe botão “pular”. O usuário precisa **ver** e **confirmar ciência**.

---

### 2.3 Como isso influencia o planejamento

Após a confirmação:

* O planejamento abre normalmente.
* Sugestões aparecem como **cards opcionais** (focos, carga, tipos de sessão).
* Cada card indica: “Baseado na temporada anterior”.

O usuário pode:

* Aplicar
* Ignorar
* Fechar card (sem penalidade)

---

### 2.4 Registro institucional (importante)

Registrar apenas:

* `inheritance_viewed_at`
* `inheritance_confirmed_by`

Não registrar se aplicou ou não sugestões como métrica de avaliação.

Isso garante rastreabilidade sem criar pressão.

---

## 3. Governança e permissões

* Comissão técnica: visualiza e confirma.
* Coordenação/direção: visualiza como contexto (sem confirmação).
* Não há impacto em permissões ou relatórios comparativos.

---

## 4. Impacto técnico

Ajustes mínimos:

* Flag de temporada para “primeiro planejamento”
* Registro leve de confirmação
* Reuso do `coach_interpretation` e sínteses já calculadas

Nenhuma mudança em dados primários.

---

## 5. Resultado final

Com herança obrigatória:

* O sistema impõe **consciência**, não decisões.
* O método evolui de forma explícita.
* A temporada começa alinhada ao aprendizado real.
* O HB Track consolida-se como plataforma de **continuidade técnica**.

Ok.

---

## 1. Explicação de UX

Adicionar um **campo curto de comentário opcional (“Considerações iniciais da nova temporada”)** no ritual de herança é uma decisão de UX de alto nível. Ele cumpre três funções comprovadas.

**Ritual cognitivo de transição.** Marcar explicitamente a passagem entre temporadas reduz vieses de continuidade automática e força reflexão consciente. Em UX, isso melhora a qualidade das decisões iniciais sem aumentar carga operacional.

**Autoridade humana explícita.** Ao permitir que o treinador registre uma leitura inicial, o sistema deixa claro que os dados informam, mas **a interpretação final é humana**. Isso preserva controle e aumenta adesão às sugestões assistidas.

**Memória institucional contextualizada.** Esse comentário vira a “capa” da nova temporada. No futuro, ele explica por que certas escolhas foram feitas desde o início, algo que gráficos não capturam.

A chave é manter o campo **curto, opcional e guiado**. Longos textos reduzem taxa de preenchimento; campos obrigatórios geram respostas artificiais.

---

## 2. Configuração no HB Track

### 2.1 Onde o campo aparece

No **Painel de Continuidade** exibido obrigatoriamente no **primeiro planejamento da temporada**, logo após a visualização da herança (interpretação final anterior + síntese assistida).

Título claro:
**Considerações iniciais da nova temporada (opcional)**

---

### 2.2 Comportamento do campo

* Campo de texto único, curto.
* Placeholder orientador, por exemplo:
  “Registre prioridades, ajustes desejados ou condicionantes iniciais para esta temporada.”
* Limite recomendado: **300–500 caracteres**.
* Totalmente opcional.
* Salvamento explícito junto da ação “Confirmar leitura e prosseguir”.

Não usar autosave aqui. O clique consciente reforça o ritual.

---

### 2.3 Regras de edição e governança

* Autor: treinador responsável.
* Editável apenas **antes do fechamento do primeiro mesociclo**.
* Após isso: somente leitura.
* Exibido como contexto no planejamento, não como métrica.

---

### 2.4 Como esse comentário é reutilizado

Esse texto passa a:

* Aparecer como **referência fixa** no Planejamento da temporada.
* Ser incluído no **Relatório de Temporada** como “Contexto Inicial”.
* Servir de pano de fundo para sugestões assistidas (sem ser processado como regra).

Nenhuma inferência automática direta deve ser feita a partir do texto.

---

## 3. Impacto técnico

Ajuste simples e isolado:

* Campo `season_initial_considerations`
* Metadados: autor, data
* Relacionado à temporada

Sem impacto em `training_sessions`, microciclos ou cálculos analíticos.

---

## 4. Resultado final

Com esse campo:

* A temporada começa com intenção explícita.
* O sistema registra método, não apenas números.
* O aprendizado vira narrativa contínua.
* O HB Track consolida um ciclo completo: **planejar → executar → refletir → replanejar**.

Ok.

A decisão de manter o campo **“Considerações iniciais da nova temporada” restrito à comissão técnica** é a escolha correta para preservar confiança, autonomia e qualidade do uso.

---

## 1. Explicação de UX

Restringir esse campo à comissão técnica atende a três princípios fundamentais.

**Segurança psicológica.** Esse comentário é reflexivo e prospectivo. Torná-lo visível à coordenação/direção criaria autocensura, reduzindo valor técnico. UX madura protege espaços de pensamento livre.

**Separação clara entre reflexão técnica e governança.** Coordenação precisa de sínteses e tendências; o treinador precisa de um espaço para registrar hipóteses, dúvidas e intenções iniciais. Misturar esses níveis empobrece ambos.

**Aumento da honestidade do dado.** Campos restritos produzem conteúdo mais autêntico e útil no médio prazo, especialmente quando revisitados durante a temporada.

Esse campo não é relatório institucional. É **âncora cognitiva do treinador**.

---

## 2. Configuração no HB Track

### 2.1 Visibilidade e permissões

* **Visível apenas para**:

  * Treinador responsável
  * Comissão técnica da equipe
* **Não visível para**:

  * Coordenação
  * Direção
  * Relatórios agregados institucionais

Controle via RBAC já existente.

---

### 2.2 Onde o campo aparece

1. **Painel de Continuidade**
   No primeiro planejamento da temporada, como etapa obrigatória de visualização.

2. **Planejamento da Temporada**
   Exibido como bloco colapsável “Contexto Inicial da Temporada”.

3. **Relatório de Temporada (visão técnica)**
   Apenas na versão detalhada da comissão técnica.
   Não aparece na versão executiva.

---

### 2.3 Regras de edição

* Campo opcional.
* Limite curto (300–500 caracteres).
* Editável até o fechamento do primeiro mesociclo.
* Após isso, somente leitura.

Metadados registrados:

* autor
* data
* temporada

---

## 3. Impacto técnico

Apenas um campo novo associado à temporada:

* `season_initial_considerations`
* Escopo de leitura restrito por papel

Nenhum impacto em estatísticas, sessões ou relatórios executivos.

---

## 4. Resultado final

Com essa restrição:

* O treinador ganha um espaço seguro de reflexão.
* O sistema mantém integridade institucional.
* A herança entre temporadas fica mais rica e honesta.
* O HB Track fecha um ciclo completo de UX de alto rendimento.

Ok.

---

## 1. Explicação de UX

Lembrar automaticamente o treinador de **reler as considerações iniciais da temporada em momentos-chave** é uma aplicação correta de **nudges contextuais**, não de notificações intrusivas. Em UX avançado, o objetivo é **reativar intenção original no momento certo**, evitando tanto esquecimento quanto fadiga de alertas.

Três princípios orientam o desenho.

**Timing sem interrupção.** O lembrete deve aparecer apenas quando o treinador já está em modo de planejamento, nunca durante registro operacional. Isso reduz carga cognitiva e aumenta taxa de leitura real.

**Contexto explícito.** O lembrete precisa explicar por que está aparecendo (“início de novo mesociclo”, “virada de fase”), evitando sensação de aleatoriedade.

**Ação mínima.** O treinador deve poder reler, fechar ou marcar como revisado em um clique. Qualquer exigência adicional reduz adesão.

O erro clássico seria usar notificações genéricas ou recorrentes. UX madura usa **poucos lembretes, altamente relevantes**.

---

## 2. Configuração no HB Track

### 2.1 Momentos-chave que disparam o lembrete

Configurar três gatilhos automáticos, derivados do domínio já existente:

1. **Início de novo mesociclo**
   Quando um novo mesociclo é criado ou iniciado.

2. **Mudança de fase competitiva**
   Transição para competição, pausa ou transição.

3. **Metade da temporada**
   Marco temporal simples para reancoragem metodológica.

Não usar lembretes semanais ou por sessão.

---

### 2.2 Onde o lembrete aparece (UX correta)

O lembrete aparece **apenas em Treinos → Planejamento**, no topo da tela, como banner discreto:

“Referência da temporada: releia suas considerações iniciais antes de planejar este período.”

Ações:

* Reler considerações
* Fechar

Nenhuma notificação push, e-mail ou modal bloqueante.

---

### 2.3 Comportamento do lembrete

* Ao clicar em “Reler”, o texto abre em painel lateral somente leitura.
* Após fechar ou reler, o lembrete desaparece para aquele período.
* Registrar apenas `last_reminder_seen_at`.

Não exigir confirmação escrita. O objetivo é **reativar memória**, não coletar dado.

---

### 2.4 Governança e visibilidade

* Visível apenas para comissão técnica.
* Coordenação e direção não veem lembretes nem registros de leitura.
* Não usar leitura como métrica de engajamento.

---

## 3. Impacto técnico

Ajuste leve e seguro:

* Flags de período (mesociclo, fase, temporada)
* Campo `last_considerations_reminder_at`
* Lógica derivada no frontend ou service layer

Nenhuma alteração em sessões ou estatísticas.

---

## 4. Resultado final

Com esses lembretes:

* A intenção inicial não se perde ao longo do ano.
* O planejamento mantém coerência metodológica.
* O sistema atua como **memória ativa**, não fiscal.
* O HB Track fecha o ciclo completo de UX orientado a aprendizado contínuo.

Ok.

---

## 1. Explicação de UX

Tornar os lembretes **configuráveis pelo treinador** é a decisão correta para maximizar adesão e reduzir fadiga. Em UX, isso aplica o princípio de **controle progressivo**: o sistema sugere comportamentos saudáveis, mas o usuário ajusta a intensidade conforme sua rotina.

Três pontos garantem eficácia:

**Autonomia explícita.** Quando o treinador controla *quais* lembretes recebe e *quando*, a taxa de leitura aumenta e a rejeição cai. Isso preserva a heurística de controle e liberdade do usuário.

**Configuração contextual, não genérica.** Preferências devem ser ajustadas no contexto de planejamento (onde o valor é claro), não em um painel genérico de notificações.

**Defaults inteligentes.** O sistema deve vir com gatilhos ativados por padrão, baseados em melhores práticas, permitindo desativação simples. Isso evita setup inicial complexo.

Evitar armadilhas: múltiplos canais (push/email), granularidade excessiva e linguagem alarmista. Lembretes aqui são *nudges*, não alertas.

---

## 2. Configuração no HB Track

### 2.1 Onde configurar

Adicionar uma seção leve em **Treinos → Planejamento → Preferências** (ou um ícone de engrenagem contextual no topo do Planejamento).

Título claro:
**Lembretes de Continuidade da Temporada**

---

### 2.2 Gatilhos configuráveis (toggle on/off)

Cada gatilho com descrição objetiva:

* **Início de novo mesociclo**
  “Relembrar considerações iniciais ao planejar um novo mesociclo.”

* **Mudança de fase competitiva**
  “Relembrar considerações ao entrar em pré-temporada, competição ou transição.”

* **Marco temporal da temporada**
  “Relembrar considerações no meio da temporada.”

Defaults:

* Todos **ativados** inicialmente.

---

### 2.3 Comportamento do lembrete (quando ativo)

* Exibição **somente** em Treinos → Planejamento.
* Banner discreto, não bloqueante.
* Ações: **Reler** | **Fechar**.
* Ao reler/fechar, o lembrete não reaparece para aquele período.

Sem push, sem e-mail, sem modal.

---

### 2.4 Governança e visibilidade

* Preferências são **individuais do treinador**.
* Visíveis apenas para a comissão técnica.
* Coordenação/direção não vê preferências nem eventos de leitura.

---

## 3. Impacto técnico

Ajuste mínimo:

* Tabela/JSON de preferências por usuário (ex.: `coach_preferences`):

  * `remind_on_new_mesocycle` (bool)
  * `remind_on_phase_change` (bool)
  * `remind_mid_season` (bool)
* Campo de controle:

  * `last_considerations_reminder_at` (timestamp)

Lógica derivada; sem impacto em sessões ou estatísticas.

---

## 4. Resultado final

Com lembretes configuráveis:

* O treinador controla o ritmo do sistema.
* A intenção inicial permanece viva sem ruído.
* A adesão aumenta por respeito à autonomia.
* O HB Track consolida-se como **memória ativa assistiva**, não intrusiva.

Ok.

---

## 1. Explicação de UX

Configurar os lembretes **por equipe** é a escolha correta quando o treinador atua em múltiplos contextos. Em UX, isso resolve o problema de **interferência cruzada**: equipes diferentes têm ritmos, fases e necessidades distintas. Um único padrão por treinador gera ruído; granularidade por equipe gera relevância.

Princípios aplicados:

* **Contextualidade máxima**: o lembrete aparece apenas quando faz sentido para aquela equipe.
* **Redução de fadiga**: evita notificações irrelevantes em equipes com ciclos distintos.
* **Controle local**: o treinador ajusta a intensidade por equipe sem perder defaults inteligentes.

Armadilha evitada: centralizar preferências no usuário e forçar um compromisso que não reflete a prática real.

---

## 2. Configuração no HB Track

### 2.1 Onde configurar (UX)

Em **Treinos → Planejamento**, com equipe selecionada, exibir um ícone de preferências contextual.

Título:
**Lembretes de Continuidade — [Nome da Equipe]**

Essa ancoragem visual deixa claro que a configuração é **por equipe**, não global.

---

### 2.2 Gatilhos configuráveis (por equipe)

Toggles independentes, com defaults ativados:

* **Início de novo mesociclo**
* **Mudança de fase competitiva**
* **Marco do meio da temporada**

Descrição curta em linguagem operacional. Sem termos técnicos.

---

### 2.3 Comportamento do lembrete

* Exibição apenas em **Treinos → Planejamento** da equipe configurada.
* Banner discreto, não bloqueante.
* Ações: **Reler** | **Fechar**.
* Após interação, não reaparece para aquele período daquela equipe.

Nenhum push, e-mail ou modal.

---

### 2.4 Governança e visibilidade

* Preferências **exclusivas da comissão técnica**.
* Coordenação/direção não visualiza preferências nem eventos de leitura.
* Preferências não são usadas como métrica de engajamento.

---

## 3. Impacto técnico

Implementação simples e segura:

* Tabela/registro por equipe e usuário (ex.: `team_coach_preferences`):

  * `team_id`
  * `coach_id`
  * `remind_on_new_mesocycle` (bool)
  * `remind_on_phase_change` (bool)
  * `remind_mid_season` (bool)
  * `last_reminder_seen_at` (timestamp)

Lógica derivada no frontend/service. Sem impacto em `training_sessions`.

---

## 4. Resultado final

Com preferências por equipe:

* Relevância máxima dos lembretes.
* Menos ruído cognitivo.
* Maior adesão à leitura reflexiva.
* HB Track atua como **memória contextual inteligente**.

Ok.

---

## 1. Explicação de UX

Herdar automaticamente as preferências ao duplicar o planejamento, mas marcá-las como **“Revisão Necessária”**, é uma solução de UX **extremamente madura**. Ela combina três princípios que raramente aparecem juntos de forma correta.

**Continuidade sem inércia.** A herança automática evita retrabalho e mantém coerência entre ciclos. O status de revisão impede que decisões antigas sigam “no piloto automático”.

**Exposição obrigatória, decisão livre.** O treinador é obrigado a *ver* que algo foi herdado, mas não é obrigado a mudar. Isso segue o mesmo raciocínio da herança de planejamento da temporada.

**Sinalização de estado explícita.** Estados visuais claros (“revisão necessária”, “confirmado”) reduzem erro humano e aumentam confiança no sistema, atendendo à heurística de visibilidade de status.

O erro clássico seria herdar silenciosamente ou forçar reconfiguração total. Sua decisão evita ambos.

---

## 2. Configuração no HB Track

### 2.1 Comportamento ao duplicar planejamento

Ao duplicar:

* Microciclo
* Mesociclo
* Planejamento semanal

O sistema:

1. Copia as preferências de lembrete **por equipe**.
2. Marca todas como **Revisão Necessária**.

Nenhuma preferência entra como “confirmada”.

---

### 2.2 Como o status aparece na UX

Em **Treinos → Planejamento**, com a equipe ativa:

Exibir um banner leve no topo:
**“Preferências de lembrete herdadas — revisão necessária”**

Ações disponíveis:

* Revisar agora
* Manter como está

Ambas removem o status de revisão.

---

### 2.3 Tela de revisão (UX simples)

Na revisão:

* Toggles aparecem com o estado herdado.
* Rótulo visual discreto “herdado”.
* Texto curto: “Essas preferências foram copiadas do planejamento anterior.”

Sem obrigatoriedade de mudança. O ato de confirmar já encerra o estado.

---

### 2.4 Regras de comportamento

* Enquanto estiver em “Revisão Necessária”:

  * Lembretes **continuam ativos** (não bloquear).
  * O banner aparece apenas uma vez por planejamento duplicado.
* Após confirmação:

  * Preferências passam a “Confirmadas”.

Nunca reabrir revisão automaticamente.

---

## 3. Impacto técnico

Pequeno ajuste na estrutura já proposta:

Adicionar:

* `preferences_status`:

  * `inherited_needs_review`
  * `confirmed`

Ao duplicar planejamento:

* Copiar preferências
* Setar status = `inherited_needs_review`

Registrar:

* `reviewed_at`
* `reviewed_by`

Nenhuma mudança em sessões ou relatórios.

---

## 4. Resultado final em UX

Com essa abordagem:

* O sistema economiza tempo.
* Evita decisões inconscientes.
* Cria um ritual leve de revisão.
* Mantém confiança e clareza operacional.

O HB Track passa a operar com **memória consciente**, não apenas memória automática.

Ok.

---

## 1. Explicação de UX

Usar um **lembrete sutil recorrente** enquanto o status estiver em **“Revisão Necessária”** é a escolha certa quando o objetivo é **evitar esquecimento sem gerar fadiga**. Em UX, isso é um *persistent nudge*: permanece visível no contexto correto, com baixa saliência, até a ação mínima ocorrer.

Princípios aplicados:

**Persistência contextual, não interrupção.** O lembrete reaparece apenas quando o treinador está em **Treinos → Planejamento** da equipe afetada. Não há modais, notificações push ou bloqueios de fluxo.

**Sinal fraco, mensagem clara.** Visual discreto (linha informativa, ícone neutro), texto curto e ação óbvia reduzem ruído e mantêm legibilidade ao longo do tempo.

**Resolução simples.** Qualquer ação consciente (“Revisar agora” ou “Manter como está”) encerra o estado. Não há penalidade por postergar.

Erro a evitar: lembrete global, cronificado ou multicanal. Isso vira spam cognitivo.

---

## 2. Configuração no HB Track

### 2.1 Onde o lembrete aparece

Somente em **Treinos → Planejamento**, quando:

* A equipe ativa possui preferências herdadas
* `preferences_status = inherited_needs_review`

Formato:

* **Banner inline** no topo do planejamento (abaixo do cabeçalho da equipe)
* Altura baixa, sem cores de alerta

Texto recomendado:
“Preferências de lembrete herdadas deste planejamento. Revisão necessária.”

Ações:

* **Revisar agora**
* **Manter como está**

---

### 2.2 Frequência e recorrência (regra exata)

* O banner aparece **todas as vezes** que o treinador acessar o Planejamento dessa equipe
* **Não aparece** em outras áreas (Sessões, Estatísticas)
* **Desaparece permanentemente** após qualquer uma das ações

Não usar timers, contadores de dias ou reaparição fora do contexto.

---

### 2.3 Comportamento das ações

**Revisar agora**

* Abre painel lateral com toggles herdados
* Confirmação encerra o status

**Manter como está**

* Confirma explicitamente a herança
* Encerra o status sem alteração

Ambas registram:

* `reviewed_at`
* `reviewed_by`
* Novo status: `confirmed`

---

### 2.4 Regras importantes

* Enquanto em “Revisão Necessária”, os lembretes **funcionam normalmente**
* O banner **não bloqueia** criação/edição de planejamento
* Não reaparecer após confirmação, mesmo ao duplicar novamente (novo ciclo gera novo status)

---

## 3. Impacto técnico

Apenas lógica de exibição:

* Condição:

  * `preferences_status == inherited_needs_review`
  * rota == Planejamento
  * team_id correspondente

Sem novas tabelas além das já definidas para preferências por equipe.

---

## 4. Resultado final em UX

Com o lembrete sutil recorrente:

* Nenhuma decisão passa despercebida
* Zero interrupção operacional
* Alta taxa de resolução voluntária
* Memória do sistema permanece **consciente e controlada**

Ok.

---

## 1. Explicação de UX

Tornar o **histórico de revisões visível para auditoria da coordenação em nível agregado** é a escolha correta para equilibrar **governança** e **segurança psicológica**. Em UX, isso é **observabilidade sem vigilância**.

Três princípios sustentam essa decisão.

**Abstração adequada ao papel.** A coordenação precisa saber *se* os rituais de revisão estão acontecendo, não *como* cada treinador decide. Mostrar eventos agregados preserva autonomia e evita microgestão.

**Transparência institucional.** Auditoria agregada cria confiança no processo (“o método está sendo revisado”) sem expor conteúdo sensível. Isso atende à heurística de visibilidade do status do sistema, no nível certo.

**Não punitivo por design.** Ao não expor textos, escolhas específicas ou links diretos para planejamentos, o sistema evita efeitos colaterais comportamentais (autocensura, gaming).

---

## 2. Configuração no HB Track

### 2.1 O que a coordenação vê (e o que não vê)

**Visível (agregado):**

* Percentual de planejamentos duplicados com revisão confirmada.
* Tempo médio até revisão.
* Tendência mensal/por mesociclo (ex.: revisões em dia vs atrasadas).
* Distribuição por equipe/categoria (sem nomes).

**Não visível:**

* Conteúdo das considerações iniciais.
* Detalhe das preferências escolhidas.
* Quem clicou “manter como está” vs “revisar”.
* Links para sessões ou planejamentos específicos.

---

### 2.2 Onde isso aparece

Adicionar um painel em **Estatísticas → Coordenação → Governança de Planejamento**.

Leitura executiva, sem ações operacionais.

---

### 2.3 Linguagem e visual (UX)

* Linguagem neutra e processual (“estado”, “tendência”).
* Sem cores de erro.
* Sem rankings.
* Sem alertas automáticos.

Exemplo de leitura:
“85% dos planejamentos duplicados tiveram revisão confirmada neste período.”

---

### 2.4 Regras de coleta (backend)

Registrar apenas eventos mínimos:

* `preferences_status_changed_at`
* `status` (inherited_needs_review → confirmed)
* `team_id`
* `period` (mesociclo/temporada)

Nada de logs verbosos.

---

## 3. Impacto técnico

Baixo impacto:

* Reuso dos campos já definidos.
* Agregações por período.
* RBAC para limitar acesso à coordenação.

Nenhuma mudança em sessões, relatórios técnicos ou sugestões.

---

## 4. Resultado final

Com auditoria agregada:

* A coordenação enxerga maturidade do processo.
* A comissão técnica mantém autonomia e segurança.
* O sistema demonstra governança sem controle excessivo.
* O HB Track se posiciona como **plataforma de alto rendimento com cultura saudável**.

Ok.

---

## 1. Explicação de UX

Adicionar **anotações institucionais** ao painel de governança é correto quando elas são tratadas como **camada de leitura estratégica**, não como instrumento operacional. Em UX, isso resolve um problema clássico: decisões e percepções da coordenação ficam dispersas em e-mails, reuniões ou memória informal, perdendo continuidade.

Três princípios são essenciais para não quebrar a cultura do sistema.

**Separação rígida de esferas.** A anotação institucional **não pode interferir** no fluxo do treinador. Ela serve para registro, alinhamento e memória organizacional, nunca para cobrança direta.

**Agregação + assíncrono.** Coordenação pensa em ciclos, não em eventos pontuais. As anotações devem ser associadas a **períodos** (mesociclo, temporada), não a equipes ou planejamentos individuais.

**Leitura sem resposta obrigatória.** UX madura evita “comentários que exigem reação”. Essas anotações são unidirecionais e reflexivas, não diálogos operacionais.

Erro a evitar: permitir comentários por equipe ou vinculados a ações específicas. Isso vira microgestão disfarçada.

---

## 2. Configuração no HB Track

### 2.1 Onde as anotações vivem

No painel:

**Estatísticas → Coordenação → Governança de Planejamento**

Adicionar uma seção clara:
**Anotações Institucionais do Período**

Sempre associadas a:

* Mesociclo
  ou
* Temporada

Nunca a sessões, microciclos ou treinadores individuais.

---

### 2.2 Estrutura da anotação (UX)

* Campo de texto livre, porém **curto**.
* Limite recomendado: **800–1.200 caracteres**.
* Um campo por período (pode haver múltiplas versões ao longo do tempo).

Metadados visíveis:

* Autor (cargo, não nome pessoal se preferir)
* Data
* Período de referência

Ação explícita:
**Registrar anotação institucional**

Nada de autosave silencioso.

---

### 2.3 Visibilidade e acesso

* **Quem pode escrever**:

  * Coordenação
  * Direção técnica (se existir)
* **Quem pode ler**:

  * Coordenação
  * Direção
  * Comissão técnica (opcional, apenas leitura)

Recomendação de UX:
Comissão técnica **vê**, mas **não responde**. Isso evita ruído e mantém hierarquia clara.

---

### 2.4 Relação com o resto do sistema

Essas anotações:

* Não afetam sugestões
* Não alteram planejamento
* Não geram alertas
* Não entram em métricas

Elas aparecem:

* Em relatórios institucionais de fim de temporada
* Como histórico consultável em ciclos futuros

---

## 3. Impacto técnico

Estrutura simples:

* Tabela `institutional_notes`

  * `id`
  * `period_type` (mesociclo | temporada)
  * `period_id`
  * `content`
  * `author_role`
  * `created_at`

RBAC garante acesso correto.

Nenhum impacto em `training_sessions`, sugestões ou relatórios técnicos.

---

## 4. Resultado final em UX

Com anotações institucionais:

* A organização constrói memória estratégica real.
* A coordenação registra contexto sem pressionar a comissão.
* O treinador entende o “clima institucional” sem cobrança direta.
* O HB Track passa a operar também como **arquivo de decisão esportiva**.

Ok.

---

## 1. Explicação de UX

Versionar as **anotações institucionais** mantendo **histórico completo** é a decisão correta quando o objetivo é criar **memória organizacional confiável**. Em UX de sistemas complexos, isso atende ao princípio de **auditabilidade sem fricção**: o usuário não precisa “gerenciar versões”, o sistema preserva tudo automaticamente.

Por que versionar é superior a substituir:

**Rastreabilidade temporal.** Decisões institucionais mudam conforme contexto. Manter versões permite entender *quando* e *por que* a leitura estratégica evoluiu ao longo do período.

**Redução de conflitos futuros.** Sem histórico, surgem narrativas concorrentes (“não foi isso que pensamos na época”). UX madura evita esse tipo de atrito.

**Baixa carga cognitiva.** Versionamento automático não exige escolha do usuário. Cada nova anotação vira uma nova camada, não uma sobrescrita.

Erro comum a evitar: expor controle manual de versões. O versionamento deve ser **implícito e silencioso**.

---

## 2. Configuração no HB Track

### 2.1 Comportamento de versionamento

Cada nova anotação institucional:

* Cria **uma nova versão**
* Nunca altera versões anteriores
* Fica vinculada ao mesmo período (mesociclo ou temporada)

Não existe “editar”. Existe **adicionar nova leitura institucional**.

---

### 2.2 Como as versões aparecem na UX

No painel:

**Estatísticas → Coordenação → Governança de Planejamento**

Exibir:

* Versão mais recente **em destaque**
* Histórico colapsável abaixo

Formato sugerido:

* “Anotação institucional — 12/03/2026”
* Clique expande conteúdo
* Versões anteriores listadas cronologicamente

Sem diff textual. Leitura integral é mais clara nesse contexto.

---

### 2.3 Metadados visíveis

Para cada versão:

* Data
* Autor (cargo)
* Período de referência

Não mostrar:

* Identificador técnico
* Status
* Flags internas

---

### 2.4 Regras de visibilidade

* Coordenação/direção:

  * Veem todo o histórico
* Comissão técnica:

  * Pode ver (se você optar), sempre em modo leitura
* Nenhuma versão é deletável pela interface

---

## 3. Impacto técnico

Modelo simples e robusto:

Tabela `institutional_notes`:

* `id`
* `period_type`
* `period_id`
* `content`
* `author_role`
* `created_at`
* `version_number` (opcional, pode ser implícito por data)

Sem updates, apenas inserts.

---

## 4. Resultado final em UX

Com versionamento completo:

* O HB Track se torna um **arquivo histórico de decisões esportivas**.
* A coordenação ganha clareza retrospectiva.
* O treinador entende a evolução institucional sem ruído.
* A governança é forte sem ser opressiva.

Ok.

---

## 1. Explicação de UX

Incluir **automaticamente as anotações institucionais como contexto nos relatórios de fim de temporada** é a decisão correta para fechar o ciclo de aprendizagem organizacional. Em UX, isso cria **coerência narrativa**: dados mostram *o que aconteceu*; anotações explicam *como a instituição leu aquele período*.

Princípios aplicados:

**Contextualização sem interferência.** O contexto aparece como leitura complementar, não como conclusão do relatório. Isso evita viés e preserva a autonomia técnica da comissão.

**Hierarquia de informação.** O relatório mantém a primazia dos dados e sínteses técnicas; o contexto institucional entra como moldura interpretativa, reduzindo interpretações equivocadas fora do tempo.

**Memória confiável.** Relatórios históricos ganham densidade ao registrar decisões e percepções no momento em que ocorreram, evitando reinterpretações tardias.

Armadilha evitada: misturar contexto institucional com avaliação de desempenho técnico. O papel é explicar o cenário, não julgar resultados.

---

## 2. Configuração no HB Track

### 2.1 Onde o contexto aparece no relatório

No **Relatório de Temporada**, adicionar uma seção específica e fixa:

**Contexto Institucional da Temporada**

Posicionamento recomendado:

* Após o sumário executivo
* Antes das análises técnicas detalhadas

Isso orienta a leitura sem contaminar a análise.

---

### 2.2 Como o conteúdo é exibido (UX)

* Mostrar **a versão mais recente** da anotação institucional como destaque.
* Abaixo, um link colapsável: **“Ver histórico de anotações desta temporada”**.
* Cada versão com data e cargo do autor.
* Conteúdo somente leitura.

Nunca mesclar textos institucionais com gráficos ou métricas.

---

### 2.3 Regras de visibilidade

* Comissão técnica:

  * Vê o contexto institucional como leitura complementar.
* Coordenação/direção:

  * Vê o contexto completo (última versão + histórico).
* Relatórios executivos:

  * Podem exibir apenas a versão mais recente, se desejado.

Nenhuma dessas anotações gera alertas, notas ou rankings.

---

### 2.4 Atualização automática

* Sempre que uma nova anotação institucional for registrada para a temporada:

  * O relatório passa a exibir automaticamente a versão mais recente.
* Relatórios exportados (PDF) incluem:

  * Versão mais recente
  * Histórico opcional, conforme perfil.

Sem necessidade de republicar manualmente.

---

## 3. Impacto técnico

Ajuste simples:

* Relatório de temporada passa a consultar:

  * `institutional_notes` por `period_type = temporada` e `period_id`
* Ordenação por `created_at DESC`
* Renderização:

  * destaque da última
  * histórico colapsável

Nenhuma mudança em sessões, microciclos ou cálculos analíticos.

---

## 4. Resultado final

Com o contexto institucional integrado aos relatórios:

* O relatório vira documento estratégico completo.
* A organização constrói narrativa consistente ao longo dos anos.
* A comissão técnica entende o ambiente decisório.
* O HB Track se consolida como **plataforma de dados + contexto + memória**.

Ok.

Confirmação registrada: **o contexto institucional aparecerá apenas nos relatórios de fim de temporada**, não nos relatórios mensais (mesociclos).

**Implementação final (síntese objetiva):**

**UX**

* Seção fixa no **Relatório de Temporada**: *Contexto Institucional da Temporada*.
* Exibe automaticamente a **versão mais recente** da anotação institucional.
* Histórico completo acessível via área colapsável.
* Somente leitura; sem alertas, sem métricas, sem rankings.
* Comissão técnica vê como contexto; coordenação/direção vê destaque + histórico.

**Regras**

* Não aparece em relatórios de mesociclo.
* Atualização automática ao registrar nova anotação institucional.
* Exportação (PDF): inclui a versão mais recente; histórico opcional conforme perfil.

**Técnico**

* Consulta por `institutional_notes` com `period_type = temporada`.
* Ordenação por `created_at DESC`.
* Renderização separada das análises técnicas.

Ok.

**Decisão confirmada:** a seção **Contexto Institucional da Temporada** será **fixa logo após o Sumário Executivo** no Relatório de Fim de Temporada.

### Implementação final (objetiva)

**UX**

* Ordem do relatório:

  1. Capa
  2. Sumário Executivo
  3. **Contexto Institucional da Temporada** (fixa)
  4. Análises técnicas (planejamento × execução, carga, focos, estrutura)
  5. Sínteses e conclusões
* Destaque da **versão mais recente** da anotação institucional.
* Histórico completo disponível em seção colapsável.
* Linguagem neutra; somente leitura; sem métricas ou rankings.

**Governança**

* Visível para comissão técnica e coordenação/direção.
* Não aparece em relatórios de mesociclo.
* Atualiza automaticamente ao registrar nova anotação.

**Técnico**

* Consulta `institutional_notes` por `period_type = temporada`, ordenação `created_at DESC`.
* Renderização separada do bloco técnico.
* PDF inclui a versão mais recente; histórico conforme perfil.

Ok.

Abaixo está a **especificação completa do template visual do PDF** do **Relatório de Fim de Temporada do HB Track**, desenhada para leitura executiva, arquivo institucional e uso técnico real.

---

## 1. Explicação de UX (por que este template funciona)

Relatórios de alto nível falham quando tentam ser dashboards impressos. O PDF do HB Track deve seguir três princípios clássicos de UX editorial.

**Hierarquia editorial clara.** O leitor precisa entender a estrutura em segundos. Isso exige títulos fortes, subtítulos funcionais e separação visual rigorosa entre narrativa e dados.

**Leitura escaneável.** Coordenação e direção não leem linha por linha. O template prioriza blocos, resumos e gráficos com legenda direta, evitando densidade excessiva.

**Neutralidade institucional.** O visual não pode parecer promocional nem punitivo. Tipografia, cores e espaçamento devem transmitir método, não opinião.

Este template é pensado para:

* leitura em tela,
* impressão A4,
* arquivamento histórico.

---

## 2. Template visual do PDF – Especificação

### 2.1 Formato geral

* Papel: A4
* Margens: amplas (mín. 20–25 mm)
* Layout: coluna única (evita ruído)
* Numeração de páginas: rodapé discreto

---

### 2.2 Tipografia

**Fonte primária (texto):**

* Sans-serif neutra e institucional
  Exemplos: Inter, Source Sans 3, Helvetica Neue

**Hierarquia:**

* Título principal (H1): 22–24 pt, peso semibold
* Seções (H2): 16–18 pt, peso semibold
* Subtítulos (H3): 13–14 pt, peso medium
* Corpo de texto: 10.5–11.5 pt, regular
* Legendas e notas: 9 pt

Nunca usar itálico excessivo. Ênfase sempre com peso ou espaçamento.

---

### 2.3 Cores

Paleta restrita e funcional:

* Preto / cinza escuro: texto
* Cinza médio: divisores, legendas
* Uma cor institucional do HB Track para títulos ou gráficos

Regras:

* Sem vermelho ou verde (evita julgamento)
* Sem gradientes
* Alto contraste para acessibilidade

---

### 2.4 Estrutura fixa do documento

#### Capa

* Nome da organização
* Equipe
* Temporada
* Data de geração
* Logo discreta

Nada mais.

---

#### Sumário Executivo (1 página)

* Texto curto (3–5 parágrafos)
* Síntese técnica da temporada
* Escrita objetiva, sem adjetivação emocional

---

#### Contexto Institucional da Temporada (fixa, logo após o sumário)

**Bloco destacado**, com fundo cinza muito claro ou linha lateral.

Conteúdo:

* Última anotação institucional (texto integral)
* Metadados: período, data, cargo do autor
* Histórico colapsável (em PDF: páginas subsequentes ou apêndice)

Este bloco nunca mistura gráficos.

---

#### Análises Técnicas (miolo)

Cada seção segue o mesmo padrão visual:

1. **Título da seção**
2. **Resumo curto (2–3 linhas)**
3. **Visual principal**
4. **Leitura orientada (bullet curto ou parágrafo)**

Seções típicas:

* Evolução do planejamento (planejado × executado)
* Distribuição de focos
* Evolução da carga
* Estrutura das sessões

Gráficos:

* Linhas simples
* Áreas suaves
* Sempre com legenda textual abaixo (“O que este gráfico mostra”)

---

#### Síntese Final Técnica

* Texto assistido + interpretação do treinador
* Campo claramente identificado como “Leitura Técnica Final”
* Sem gráficos

---

### 2.5 Elementos proibidos no PDF

* Tabelas extensas
* Rankings
* Alertas visuais
* Ícones decorativos
* Linguagem avaliativa (“baixo desempenho”, “falha”)

---

## 3. Implementação técnica (direto ao ponto)

* Geração via template server-side (HTML → PDF)
* CSS dedicado para print
* Fontes embutidas
* Quebras de página explícitas por seção
* Cabeçalho discreto com nome do relatório
* Rodapé com página + confidencialidade

---

## 4. Resultado final

Com esse template:

* O relatório é lido, não ignorado.
* A instituição cria memória séria e profissional.
* O treinador se reconhece no documento.
* O HB Track entrega padrão **enterprise / alto rendimento**.

Ok.

---

## 1. Explicação de UX

Gerar **duas versões automáticas do PDF** — **Técnica Completa** e **Executiva Resumida** — é a melhor prática para públicos com **objetivos cognitivos distintos**. Em UX editorial, isso evita o erro comum de “um relatório para todos”, que acaba não servindo bem a ninguém.

**Princípios aplicados**

* **Progressive disclosure**: quem decide rápido vê síntese; quem executa aprofunda.
* **Adequação ao papel**: coordenação/direção precisa de leitura estratégica; comissão técnica precisa de método, evidência e memória.
* **Consistência narrativa**: ambas as versões contam a mesma história, com densidades diferentes, evitando contradições.

**Armadilhas evitadas**

* Duplicar manutenção manual.
* Resumos que “interpretam demais” os dados técnicos.
* PDFs longos ignorados por decisores.

---

## 2. Configuração no HB Track

### 2.1 Geração automática (uma fonte, duas saídas)

* **Uma única pipeline de dados** (planejamento, execução, carga, focos, anotações institucionais).
* **Dois templates** que consomem a mesma fonte:

  * `season_report_technical.pdf`
  * `season_report_executive.pdf`
* Geração simultânea no encerramento da temporada ou sob demanda.

### 2.2 Versão Técnica Completa (Comissão Técnica)

**Público**: treinadores e comissão.
**Extensão**: 15–25 páginas (dependendo da temporada).

**Estrutura**

1. Capa
2. Sumário Executivo
3. **Contexto Institucional da Temporada** (fixa, após o sumário)
4. Evolução do Planejamento (contínua e por fases)
5. Focos: planejado × executado (tendências)
6. Carga semanal (planejada × real)
7. Estrutura de sessões (tipos)
8. Aprendizados e ajustes recorrentes
9. **Interpretação Final do Treinador**
10. Apêndice visual (opcional)

**UX**

* Gráficos explicados (“o que este gráfico mostra”).
* Texto técnico, sem rankings ou julgamentos.
* Histórico institucional colapsável.

### 2.3 Versão Executiva Resumida (Coordenação/Direção)

**Público**: coordenação e direção.
**Extensão**: 3–5 páginas.

**Estrutura**

1. Capa
2. **Sumário Executivo (1 página)**
3. **Contexto Institucional da Temporada** (versão mais recente)
4. Tendências-chave (3–5 insights visuais)
5. Implicações estratégicas (texto curto)

**UX**

* Visual limpo, poucos gráficos.
* Linguagem estratégica, não operacional.
* **Sem detalhes de sessões**, sem justificativas individuais.

### 2.4 Regras de visibilidade

* Comissão técnica: acesso às **duas versões**.
* Coordenação/direção: acesso padrão à **Executiva**; Técnica apenas se autorizado.
* Mesociclos: **não** incluem contexto institucional.

### 2.5 PDF e exportação

* Botões claros: **Exportar Técnico** | **Exportar Executivo**.
* Metadados no rodapé (temporada, data, confidencialidade).
* Fontes embutidas, A4, margens amplas.

---

## 3. Impacto técnico

* Dois templates HTML/CSS de print.
* Mesmo serviço de agregação de dados.
* Feature flags por perfil (RBAC).
* Cache por temporada para reexportação rápida.

---

## 4. Resultado final

* Leitura rápida para decisores, profundidade para técnicos.
* Menos retrabalho, mais clareza.
* Memória institucional consistente.
* Padrão **enterprise** para o HB Track.

Ok.

Abaixo está a **decisão objetiva de quais gráficos entram e quais saem da versão Executiva Resumida**, alinhada ao papel de coordenação/direção e às decisões já tomadas no HB Track.

---

## Gráficos que **ENTRAM** na versão Executiva

**1. Evolução global dos focos (planejado × executado, agregado)**
Mostra tendência da temporada, não semanas individuais.
Gráfico simples de áreas ou linhas médias.
Objetivo: coerência metodológica, não detalhe técnico.

**2. Carga semanal média por fase competitiva**
Comparação entre pré-temporada, competição e transição.
Sem valores diários, apenas médias por fase.
Objetivo: visão macro de dose e risco.

**3. Distribuição de tipos de sessão (percentual)**
Ex.: técnico, tático, físico, regenerativo.
Gráfico de barras simples ou donut.
Objetivo: leitura estrutural do processo de treino.

**4. Indicador agregado de desvios de planejamento**
Percentual de sessões com desvio relevante por período.
Sem apontar quais sessões ou equipes específicas.
Objetivo: governança e alinhamento institucional.

**5. Linha de marcos da temporada**
Início de ciclos, fases competitivas, pausas.
Visual leve, quase editorial.
Objetivo: contextualizar decisões no tempo.

---

## Gráficos que **SAEM** da versão Executiva

**1. Gráficos por sessão individual**
Detalhe operacional demais.
Pertencem exclusivamente à versão técnica.

**2. Planejado × executado por microciclo ou semana**
Excesso de granularidade para decisão executiva.
Gera microgestão involuntária.

**3. Gráficos de wellness, RPE individual ou dispersão**
Leitura clínica/técnica.
Não agregam valor estratégico direto.

**4. Correlações treino → jogo detalhadas**
Complexas e sujeitas a interpretação técnica.
Executivo precisa de síntese, não causalidade fina.

**5. Históricos completos ou séries longas**
Ruído visual alto.
Resumo é preferível à exaustão.

---

## Regra de ouro da versão Executiva

Se o gráfico responde à pergunta:
**“O método está coerente ao longo da temporada?” → ENTRA**

Se responde:
**“Como exatamente treinamos naquela semana?” → SAI**

---

## Resultado final em UX

* Leitura em 3–5 páginas.
* Nenhuma tentação de microgestão.
* Clareza institucional sem perda de profundidade técnica.
* Consistência total com o desenho de governança que você definiu.

Ok.

**Decisão fixada:** a **versão Executiva Resumida** terá **limite rígido de até 5 gráficos**, sem exceções.

### Os 5 gráficos fixos (ordem e função)

**1) Evolução global dos focos (planejado × executado, agregado)**
Mostra coerência metodológica ao longo da temporada.
Agregado por fase; sem semanas/sessões.

**2) Carga semanal média por fase competitiva**
Comparação entre pré-temporada, competição e transição.
Apenas médias por fase.

**3) Distribuição de tipos de sessão (percentual)**
Visão estrutural do processo (técnico, tático, físico, regenerativo).
Gráfico simples e legível.

**4) Indicador agregado de desvio de planejamento**
Percentual de sessões com desvio relevante por período.
Sem detalhamento por equipe/sessão.

**5) Linha de marcos da temporada**
Contextualiza decisões no tempo (ciclos, fases, pausas).
Visual editorial, baixo ruído.

### Regras de governança (travadas)

* Nenhum gráfico adicional entra na versão Executiva.
* Gráficos técnicos detalhados ficam **exclusivos da versão Técnica**.
* Mesma base de dados; templates distintos; RBAC aplicado.

Ok.

**Decisão consolidada:** a **versão Executiva Resumida** terá **ordem fixa e imutável** dos **5 gráficos**, em **todas as temporadas**.

### Ordem fixa (travada)

1. Evolução global dos focos (planejado × executado, agregado)
2. Carga semanal média por fase competitiva
3. Distribuição de tipos de sessão (percentual)
4. Indicador agregado de desvio de planejamento
5. Linha de marcos da temporada

### Regras finais

* Nenhum gráfico adicional entra.
* Nenhuma reordenação permitida.
* Mesma base de dados; template executivo único.
* Governança garantida por RBAC e cache por temporada.

1. Princípio estrutural (decisão de UX)

Treinos ≠ Statistics ≠ Reports

Cada domínio corresponde a um estado mental diferente do usuário:

Treinos → ação, planejamento e execução (escrita de dados)

Statistics → leitura analítica e decisão recorrente (dados agregados)

Reports → narrativa formal e fechamento institucional (documentos)

Misturar esses domínios degrada UX, gera erro e quebra confiança. O mapa abaixo elimina isso.

2. TREINOS — Planejar e Executar (operacional)
Sidebar → Treinos
2.1 Treinos → Ciclos

Rota: /trainings/cycles
Escopo: planejamento estratégico da temporada (intenção)

Componentes principais:
Breadcrumbs (Clube > Equipe > Temporada > Ciclos)
Lista de ciclos (macro/meso)
Objetivo do ciclo
Status (ativo/encerrado)
Empty State de início de temporada

Não há métricas, gráficos ou comparações.

2.2 Treinos → Planejamento (Microciclo)

Rota: /trainings/planning
Escopo: intenção semanal

Componentes:
Stepper de fase da temporada
Grade semanal (microciclo)
Distribuição planejada de focos
Sugestões assistivas (foco, carga ou tipo)
Modal de Herança Inteligente
Badges: “Revisão Necessária”

Planejamento não gera estatística.

2.3 Treinos → Sessões (lista)

Rota: /trainings/sessions
Escopo: controle diário

Componentes:
Lista leve de sessões
Status (rascunho / aberta / fechada)
Presença %
Badge de risco
Badge de desvio (somente indicador)

Nenhuma análise profunda aqui.

2.4 Sessão de Treino (Execução)

Rota: /trainings/sessions/[id]
Escopo: execução real

Componentes:
Sticky header de contexto
Presença
Carga e RPE
Focos executados
FAB para scout rápido

Após fechar: somente leitura.
O alerta de desvio apenas informa, não analisa.

3. STATISTICS — Analisar e Decidir (analítico)
Sidebar → Estatísticas
3.1 Estatísticas → Operacional

Rota: /statistics
Escopo: decisão diária/recorrente

Componentes:
Cards operacionais
Sessões com badge de desvio
Links para sessão

Não há texto narrativo nem PDFs.

3.2 Estatísticas → Equipes

Rota: /statistics/teams
Escopo: visão da comissão e coordenação

Componentes:
Dashboards agregados
Cards colapsáveis por mesociclo
Indicadores de desvio agregados
Métricas de auditoria sem texto

Coordenação não vê sessões individuais.

3.3 Estatísticas → Atletas

Rota: /statistics/athletes
Escopo: análise individual técnica

Componentes:
Sticky header da atleta
Filtros por posição / percentil
Gráficos individuais

Sem planejamento, sem execução, sem governança.

4. REPORTS — Formalizar e Encerrar (institucional)
Não é Treinos.
Não é Statistics.
É um terceiro eixo.
4.1 Relatório de Mesociclo

Rota: /reports/mesocycle/[id]

Componentes:
Campo Markdown (limite dinâmico)
Narrativa técnica
Visualizador de PDF in-app

Somente leitura após fechamento.

4.2 Relatório Final da Temporada

Rota: /reports/season/[id]

Componentes:
Sumário executivo
Seção técnica
Anotações institucionais (automáticas)
Toggle PDF: Técnica | Executiva
Executiva: máx. 5 gráficos, ordem fixa

Este é o único lugar onde narrativa institucional aparece.

5. Governança e Continuidade (suporte, não domínio)
5.1 Painel de Continuidade

Rota: /season/continuity

Componentes:
Interpretação final do treinador
Herança de preferências
Badge de auditoria
Confirmação de ciência obrigatória

Não planeja, não executa, não analisa.

6. Síntese final (sem ambiguidade)

Treinos escreve dados

Statistics interpreta dados

Reports formaliza decisões

Nada “fica dentro” de Treinos além de planejar e executar.
Nada analítico pesado fica em Treinos.
Nada narrativo vive em Statistics.

Este é o desenho de UX correto, maduro e escalável para o HB Track.

1. Escopo e responsabilidade (fechado)

TREINOS é o domínio de escrita do sistema.
Ele planeja (intenção) e registra (execução).
Ele não analisa profundamente, não gera PDFs e não cria narrativa institucional.

Tudo é team_id + season_id.

2. Modelo de dados (tabelas)
2.1 training_cycles

Representa macro e mesociclos da temporada.

Campos essenciais:

id

organization_id

team_id

season_id

type (macro | meso)

name

start_date

end_date

objective (text)

notes (text, opcional)

status (active | closed)

created_at

closed_at (nullable)

Regras:

Não atravessa temporada

Encerrar ciclo bloqueia edição

2.2 training_microcycles

Representa o planejamento semanal.

Campos:

id

organization_id

team_id

season_id

cycle_id (FK → training_cycles)

week_start

week_end

planned_focus_distribution (JSON ou colunas percentuais)

planned_load_hint (opcional)

planned_session_types (JSON)

status (active | closed)

created_from_inheritance (boolean)

review_required (boolean)

created_at

closed_at

Regras:

Planejamento ≠ execução

Microciclo fechado é somente leitura

review_required=true quando herdado

2.3 training_sessions

Execução real do treino (já existente, apenas consolidado).

Campos relevantes:

id

organization_id

team_id

season_id

microcycle_id (FK opcional)

date

session_type

status (draft | open | closed | read_only)

attendance_*

rpe_avg

minutes_avg

load_avg

focus_*_pct (7 focos)

planning_deviation_flag (boolean derivado)

closed_at

Regras:

Só sessões closed alimentam outros domínios

Após closed: read_only

3. Estados e transições (máquina de estados)
Ciclos

active → closed

Nunca reabre

Microciclos

active → closed

Fecha automaticamente ao fechar último treino da semana (opcional, configurável)

Sessões

draft → open → closed → read_only

Nenhuma transição reversa

4. Eventos de domínio (internos)
Ao fechar sessão

Dispara:

Validação de presença

Validação de focos (≥1 foco, soma ≤120)

Cálculo de planning_deviation_flag

Disponibilização para Statistics

Ao criar microciclo

Avalia herança

Gera sugestões (não aplica)

Marca review_required se herdado

5. Contratos de API (TREINOS)
Ciclos

POST /teams/{team_id}/seasons/{season_id}/training-cycles

GET /teams/{team_id}/seasons/{season_id}/training-cycles

PATCH /training-cycles/{id}

POST /training-cycles/{id}/close

Microciclos (Planejamento)

POST /training-cycles/{cycle_id}/microcycles

GET /training-cycles/{cycle_id}/microcycles

PATCH /training-microcycles/{id}

POST /training-microcycles/{id}/close

POST /training-microcycles/{id}/inherit
Retorna preview + review_required=true

Sessões (Execução)

POST /training-sessions

GET /training-sessions?team_id&season_id&period

GET /training-sessions/{id}

PATCH /training-sessions/{id}

POST /training-sessions/{id}/close

6. Regras de RBAC (resumo)

Treinador / Coordenador

Criar, editar e fechar

Atleta

Nunca escreve

Coordenação

Não edita Treinos

Só consome via Statistics

7. O que TREINOS NÃO faz (explícito)

Não gera gráficos analíticos

Não gera PDFs

Não cria texto institucional

Não compara temporadas

Não reabre estados fechados

8. Integração com outros domínios

Statistics

Consome apenas sessões closed

Reports

Nunca lê diretamente Treinos

Sempre via Statistics

9. Resultado

Esta especificação:

É executável

Evita vazamento de responsabilidade

Mantém UX coerente

Reduz dívida técnica futura

Ok. Abaixo está a **especificação técnica completa do domínio STATISTICS**, no mesmo nível de rigor do domínio TREINOS, sem invadir Reports nem reabrir decisões já fechadas.

---

## 1. Escopo e responsabilidade (fechado)

**STATISTICS** é o domínio de **leitura analítica** do HB Track.

Ele:
– interpreta dados **já fechados**
– agrega, compara e sinaliza
– apoia decisão recorrente (diária, semanal, mensal)

Ele **não escreve dados esportivos**, **não planeja**, **não gera PDFs** e **não cria narrativa institucional**.

STATISTICS **consome TREINOS** e **alimenta REPORTS**.

---

## 2. Natureza técnica do domínio

STATISTICS **não é CRUD-centric**.
Ele é composto por:
– queries agregadas
– regras derivadas
– métricas calculadas
– visões RBAC

Por princípio, **não cria tabelas primárias de negócio**.
Quando há persistência, ela é **derivada, leve e opcional**.

---

## 3. Fontes de dados (somente leitura)

STATISTICS consome **exclusivamente**:

– `training_sessions` com `status = closed`
– `attendance` consolidada
– `load`, `rpe`, `minutes`
– focos executados (`focus_*_pct`)
– vínculos (`team_registrations`, `memberships`)
– metadados de ciclo/microciclo (contexto, nunca edição)

Qualquer sessão não fechada **é invisível** para STATISTICS.

---

## 4. Entidades lógicas (não tabelas)

### 4.1 OperationalSnapshot (diário)

Representa o “estado do dia”.

Campos derivados:
– total de sessões do período
– presença média
– carga média
– flags de risco
– flags de desvio (boolean)

Não persistido.

---

### 4.2 TeamAggregate (semanal / mensal)

Visão agregada por equipe.

Campos:
– médias e dispersões de carga
– distribuição de focos executados
– percentual de sessões com desvio
– indicadores de consistência

Pode ser calculado on-the-fly ou cacheado.

---

### 4.3 AthleteAggregate

Visão individual.

Campos:
– carga acumulada
– histórico de presença
– métricas individuais
– comparação percentil (opcional)

Somente leitura.

---

## 5. Regras analíticas centrais

### 5.1 Regra de visibilidade

– Atleta vê **apenas dados próprios**
– Comissão vê dados da equipe
– Coordenação vê **somente agregado**, nunca sessão individual

RBAC é obrigatório em todos os endpoints.

---

### 5.2 Regra de desvio de planejamento

Derivado de:
– foco planejado (microciclo)
– foco executado (sessão)

Critério padrão:
– desvio ≥ X pontos em qualquer foco
OU
– desvio agregado ≥ Y%

Resultado:
– `planning_deviation = true | false`

Nunca bloqueia nada.

---

### 5.3 Regra de risco

STATISTICS **interpreta** alertas, não cria novos eventos esportivos.

Exemplos:
– carga fora de faixa
– presença abaixo de X%
– sessão operacional em risco

Tudo é **indicador**, nunca erro.

---

## 6. Contratos de API (STATISTICS)

### 6.1 Operacional (diário)

`GET /statistics`

Retorna:
– sessões recentes
– indicadores rápidos
– badges de risco e desvio
– links para leitura contextual (sessão)

Sem gráficos complexos.

---

### 6.2 Equipes

`GET /statistics/teams?team_id&season_id&period`

Retorna:
– agregados por semana/mês
– cards colapsáveis por mesociclo
– percentuais de desvio
– métricas de consistência

Nunca retorna:
– texto livre
– sessão individual detalhada

---

### 6.3 Atletas

`GET /statistics/athletes?team_id&season_id&filters`

Retorna:
– métricas individuais
– percentis
– comparação contextual

Com:
– sticky header da atleta
– filtros por posição / percentil

---

### 6.4 Suporte a Reports

`GET /statistics/snapshots/{scope}/{id}`

Escopos:
– `mesocycle`
– `season`

Retorna:
– dados consolidados
– prontos para narrativa e PDF
– sem estado mutável

---

## 7. Estados e mutabilidade

STATISTICS **não tem estados próprios**.

Tudo é:
– calculado
– derivado
– reproduzível

Se um dado muda, é porque o domínio TREINOS mudou antes.

---

## 8. O que STATISTICS NÃO faz (explícito)

– Não edita dados
– Não fecha períodos
– Não cria textos
– Não gera PDFs
– Não dispara notificações
– Não aprende padrões (isso é Planejamento)

---

## 9. Integração com outros domínios

– **TREINOS**
Consome sessões fechadas

– **REPORTS**
Fornece snapshots consolidados

– **Governança**
Exibe métricas agregadas, nunca decisões

---

## 10. Resultado

Esta especificação garante que STATISTICS seja:
– confiável
– previsível
– auditável
– sem risco de “vazamento de responsabilidade”

E, principalmente:
**UX limpa**, porque leitura, decisão e narrativa não se misturam.

Ok. Abaixo está a **especificação técnica completa do domínio REPORTS**, fechada, consistente com TREINOS e STATISTICS, e pronta para implementação sem risco de sobreposição de responsabilidades.

---

## 1. Escopo e responsabilidade (fechado)

**REPORTS** é o domínio de **formalização institucional**.

Ele:
– consolida períodos **já encerrados**
– transforma dados analíticos em **narrativa oficial**
– gera **artefatos imutáveis** (PDFs)

Ele **não calcula métricas primárias**, **não interpreta operacionalmente**, **não planeja** e **não executa**.

REPORTS **consome STATISTICS**, nunca TREINOS diretamente.

---

## 2. Princípio estrutural (fundamental)

REPORTS trabalha com **snapshots**.

Um relatório:
– reflete o estado dos dados **no momento do fechamento**
– não se altera se dados históricos mudarem depois
– pode ter versões, mas cada versão é imutável

Isso garante:
– rastreabilidade
– confiança institucional
– coerência histórica

---

## 3. Tipos de relatório (escopo fechado)

### 3.1 Relatório de Mesociclo

Escopo: avaliação técnica periódica.

Identidade:
– team_id
– season_id
– mesocycle_id

Periodicidade:
– 1 por mesociclo

---

### 3.2 Relatório Final da Temporada

Escopo: fechamento institucional.

Identidade:
– team_id
– season_id

Periodicidade:
– 1 por temporada

---

## 4. Modelo de dados (tabelas)

### 4.1 `reports`

Tabela base comum.

Campos:

* `id`
* `organization_id`
* `team_id`
* `season_id`
* `scope` (`mesocycle` | `season`)
* `scope_id` (nullable para season)
* `status` (`draft` | `finalized` | `locked`)
* `version`
* `created_at`
* `finalized_at`
* `locked_at`
* `created_by`

Regras:

* `locked` é irreversível
* Nova edição = nova versão

---

### 4.2 `report_snapshots`

Snapshot técnico (dados).

Campos:

* `id`
* `report_id`
* `statistics_payload` (JSONB)
* `generated_at`

Origem:

* Exclusivamente de STATISTICS

---

### 4.3 `report_narratives`

Narrativa humana.

Campos:

* `id`
* `report_id`
* `section` (`summary` | `technical` | `interpretation`)
* `content_markdown`
* `char_limit`
* `created_at`

Regras:

* Limite dinâmico por tipo de relatório
* Editável só enquanto `draft`

---

### 4.4 `report_institutional_notes`

Notas institucionais (coordenação).

Campos:

* `id`
* `organization_id`
* `season_id`
* `period_scope` (`season` | `mesocycle`)
* `period_id`
* `content`
* `visibility` (`internal` | `external`)
* `version`
* `created_at`

Versionamento automático, histórico completo.

---

## 5. Estados e transições

### Relatório

* `draft`
  – edição permitida
* `finalized`
  – leitura completa
  – PDFs gerados
* `locked`
  – imutável
  – referência institucional

Nenhuma transição reversa.

---

## 6. Contratos de API (REPORTS)

### 6.1 Criação

`POST /reports`

Payload:

* `team_id`
* `season_id`
* `scope`
* `scope_id`

Ação:
– gera snapshot via STATISTICS
– cria versão 1 em `draft`

---

### 6.2 Leitura

`GET /reports/{id}`
`GET /reports?team_id&season_id`

Retorna:
– narrativa
– dados consolidados
– metadados de versão

---

### 6.3 Edição narrativa (draft apenas)

`PATCH /reports/{id}/narratives/{section}`

Valida:
– limite de caracteres
– permissões

---

### 6.4 Finalização

`POST /reports/{id}/finalize`

Ação:
– congela narrativa
– gera PDFs
– muda status para `finalized`

---

### 6.5 Lock institucional

`POST /reports/{id}/lock`

Ação:
– status `locked`
– bloqueio definitivo

---

## 7. PDFs (regra rígida)

### Técnica

– completa
– todos os gráficos
– narrativa detalhada

### Executiva

– **máx. 5 gráficos**
– **ordem fixa**
– sem texto operacional
– foco decisório

Mesma base de dados, templates distintos.

---

## 8. RBAC

* **Treinador**
  – edita narrativa técnica (draft)
* **Coordenador**
  – adiciona notas institucionais
* **Direção**
  – leitura apenas
* **Atleta**
  – sem acesso

---

## 9. O que REPORTS NÃO faz (explícito)

– Não recalcula métricas
– Não acessa TREINOS
– Não sugere ajustes
– Não gera alertas
– Não planeja continuidade

---

## 10. Integração com outros domínios

– **STATISTICS**
– única fonte de dados técnicos
– **Governança**
– notas versionadas
– **Continuidade**
– interpretação final usada como insumo, nunca automática

---

## 11. Resultado

Esta especificação:
– fecha o ciclo completo do sistema
– separa ação, análise e formalização
– garante confiança institucional
– elimina ambiguidade técnica e de UX

Com TREINOS, STATISTICS e REPORTS especificados, o sistema está **pronto para contratos finais e implementação**.

Ok. Abaixo está o **mapa final de eventos entre domínios (event-driven)** do HB Track, fechado, sem ambiguidades e pronto para orientar backend, filas, jobs e contratos assíncronos.

---

## 1. Princípio estrutural do modelo event-driven

O HB Track **não é real-time streaming**.
Ele é **event-driven por marcos de estado**.

Eventos:
– **nascem apenas em domínios de escrita**
– **são emitidos somente em transições irreversíveis**
– **nunca carregam lógica de negócio**, apenas fatos
– **domínios consumidores nunca respondem com eventos de volta**

Isso evita loops, acoplamento e efeitos colaterais.

---

## 2. Domínios emissores e consumidores

### Emissores

* **TREINOS** (principal)
* **REPORTS** (institucional)

### Consumidores

* **STATISTICS**
* **REPORTS**
* **Governança / Continuidade** (leitura contextual)

STATISTICS **nunca emite eventos**.

---

## 3. Eventos do domínio TREINOS

### 3.1 `training.session.closed`

**Emitido quando**
Sessão muda de `open` → `closed`.

**Payload mínimo**

* session_id
* team_id
* season_id
* microcycle_id (nullable)
* closed_at

**Consumidores**

* STATISTICS
* Governança (agregado)

**Efeitos**

* Sessão torna-se visível para estatísticas
* Cálculo de métricas derivadas
* Cálculo de `planning_deviation_flag`

Nenhum retorno. Nenhuma mutação em TREINOS.

---

### 3.2 `training.microcycle.closed`

**Emitido quando**
Microciclo muda de `active` → `closed`.

**Payload**

* microcycle_id
* team_id
* season_id
* cycle_id

**Consumidores**

* STATISTICS
* REPORTS (habilitação)

**Efeitos**

* Consolidação semanal disponível
* Libera criação de relatório de mesociclo

---

### 3.3 `training.cycle.closed`

**Emitido quando**
Ciclo (meso ou macro) é encerrado.

**Payload**

* cycle_id
* team_id
* season_id
* type (meso|macro)

**Consumidores**

* STATISTICS
* REPORTS

**Efeitos**

* Fecha janelas analíticas do período
* Marca ciclo como elegível para relatório

---

## 4. Eventos do domínio STATISTICS

**STATISTICS NÃO EMITE EVENTOS.**

Justificativa:
– domínio puramente derivado
– outputs são sempre reproduzíveis
– evita inconsistência e duplicação

STATISTICS reage a eventos, nunca os propaga.

---

## 5. Eventos do domínio REPORTS

### 5.1 `report.created`

**Emitido quando**
Relatório é criado (draft).

**Payload**

* report_id
* scope (mesocycle|season)
* scope_id
* team_id
* season_id

**Consumidores**

* Governança
* Auditoria

**Efeitos**

* Início de rastreabilidade institucional

---

### 5.2 `report.finalized`

**Emitido quando**
Relatório muda de `draft` → `finalized`.

**Payload**

* report_id
* version
* finalized_at

**Consumidores**

* Continuidade
* Auditoria

**Efeitos**

* PDFs gerados
* Conteúdo congelado
* Disponível para leitura executiva

---

### 5.3 `report.locked`

**Emitido quando**
Relatório muda de `finalized` → `locked`.

**Payload**

* report_id
* version
* locked_at

**Consumidores**

* Continuidade
* Governança

**Efeitos**

* Artefato institucional definitivo
* Base para herança entre temporadas

---

## 6. Eventos de Continuidade (derivados, não esportivos)

### 6.1 `season.continuity.confirmed`

**Emitido quando**
Comissão confirma ciência da herança.

**Payload**

* team_id
* season_id
* confirmed_at

**Consumidores**

* Governança
* Auditoria

**Efeitos**

* Registro formal de ciência
* Não altera planejamento automaticamente

---

## 7. O que NÃO é evento (decisão explícita)

Não são eventos:

* alertas de desvio
* sugestões de planejamento
* badges de auditoria
* mudanças visuais de UI
* leitura de relatórios

Tudo isso é **estado derivado ou visual**, não fato de domínio.

---

## 8. Ordem cronológica típica (exemplo real)

1. Sessão fechada
   → `training.session.closed`
   → STATISTICS calcula métricas

2. Última sessão da semana fechada
   → `training.microcycle.closed`

3. Mesociclo encerrado
   → `training.cycle.closed`

4. Relatório criado
   → `report.created`

5. Relatório finalizado
   → `report.finalized`

6. Relatório travado
   → `report.locked`

7. Nova temporada
   → `season.continuity.confirmed`

Fluxo linear, auditável, sem loops.

---

## 9. Benefício técnico e de UX

Tecnicamente:
– baixo acoplamento
– fácil de testar
– escalável
– auditável

Em UX:
– estados claros
– nenhuma surpresa para o usuário
– confiança nos dados
– governança sem vigilância

---

## 10. Estado do sistema após este mapa

Com:

* TREINOS especificado
* STATISTICS especificado
* REPORTS especificado
* Eventos entre domínios fechados

O HB Track está **arquiteturalmente completo**.

1. Explicação de UX

Infra de eventos (fila + assíncrono) impacta UX por um motivo simples: ela define se o sistema “parece confiável”. Em HB Track, quando o treinador fecha uma sessão, a expectativa mental é: “fechei, virou verdade e vai aparecer nas estatísticas/relatórios”. Se você depender de processamento assíncrono sem garantias (perdas, duplicações, atrasos sem feedback), a UX degrada rápido: o usuário passa a desconfiar do dado, retrabalhar e criar “planilhas paralelas”.

O desenho correto é tornar o assíncrono invisível para o usuário, exceto quando houver atraso anormal. Isso exige: (1) eventos nunca se perderem, (2) reprocessamento seguro (idempotência), (3) retries com backoff e DLQ, e (4) estados de interface sempre refletindo a verdade do domínio (ex.: sessão fechada é fechada, mesmo que o “snapshot estatístico” demore). Isso combina com a regra do sistema de preservar histórico, rastreabilidade e auditoria em ações relevantes. 

REGRAS

2. Configuração do HB Track

Abaixo vai um blueprint de infra pronto para implementar sem mudar o modelo de UX (Treinos escreve; Statistics/Reports leem).

Fila e execução assíncrona

Use um broker (Redis+BullMQ, RabbitMQ ou SQS). O requisito não é “qual”, é garantir: ack explícito, retries nativos, DLQ, visibilidade de tentativas e atraso. O processamento assíncrono deve ficar em “workers” separados do servidor HTTP.

Publicação confiável: Transactional Outbox

Quando TREINOS muda estado (ex.: training.session.closed), você precisa garantir que ou grava no banco e emite evento, ou não faz nenhum dos dois. A solução canônica é Outbox no mesmo Postgres: na mesma transação que fecha a sessão, insira um registro em outbox_events (com event_id, event_type, payload, occurred_at, status=pending). Um dispatcher (job recorrente) lê pendentes e publica na fila; após publish, marca como published. Isso evita “sessão fechada sem evento” (pior caso de UX).

Idempotência ponta a ponta

Cada evento tem event_id (UUID) e cada consumidor mantém processed_events(event_id, processed_at) com UNIQUE. Ao receber, tenta inserir event_id; se já existir, ignora (dedupe). Isso torna reprocessamento seguro e impede duplicar agregações/gerações de PDF.

Além disso, para endpoints críticos (ex.: POST /training-sessions/{id}/close), aceite Idempotency-Key no header e armazene idempotency_keys(key, request_hash, response_blob, created_at) por janela (ex.: 24h). Repetiu a mesma chamada, devolve a mesma resposta.

Retries, backoff, DLQ e “poison messages”

Retries: exponencial com jitter (ex.: 10s, 30s, 2m, 10m, 30m) e limite (ex.: 10 tentativas). Se falhar por validação de payload (erro permanente), manda direto para DLQ. Se falhar por dependência (DB, rede), retry. DLQ precisa de painel interno (admin) para reprocessar.

Consistência percebida na UI

Ao fechar sessão, o backend responde imediatamente “closed” (verdade do domínio). Statistics/Reports podem “atualizar em alguns segundos”; se passar de um limiar (ex.: 30–60s), mostre status leve “Atualizando…” nas telas de leitura, sem bloquear. Isso preserva confiança sem expor complexidade.


Ok. Abaixo está a **especificação técnica concreta** de `outbox_events`, `processed_events` e `idempotency_keys`, **encaixada diretamente** no stack **FastAPI + Neon (PostgreSQL) + Alembic** do HB Track, sem abstrações genéricas.

---

## 1. Por que essas três tabelas são obrigatórias no HB Track

No seu sistema, há **eventos irreversíveis** (fechar sessão, fechar microciclo, finalizar relatório). UX correta exige que:

– o estado mude imediatamente para o usuário
– nenhum evento se perca
– retries não dupliquem efeitos
– reprocessar seja seguro

Essas três tabelas resolvem isso **sem acoplar Treinos, Statistics e Reports**.

---

## 2. `outbox_events` — Transactional Outbox

### Finalidade

Garantir que **toda mudança crítica de estado** gere exatamente **um evento publicável**, mesmo com crash, timeout ou retry.

### Tabela (PostgreSQL / Neon)

```sql
CREATE TABLE outbox_events (
  id UUID PRIMARY KEY,
  event_type TEXT NOT NULL,
  aggregate_type TEXT NOT NULL,
  aggregate_id UUID NOT NULL,
  payload JSONB NOT NULL,
  status TEXT NOT NULL DEFAULT 'pending',
  occurred_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  published_at TIMESTAMPTZ
);

CREATE INDEX idx_outbox_status ON outbox_events (status);
CREATE INDEX idx_outbox_event_type ON outbox_events (event_type);
```

### Uso no FastAPI (padrão obrigatório)

No **mesmo transaction scope** que fecha uma sessão:

```python
with session.begin():
    training_session.status = "closed"

    outbox = OutboxEvent(
        id=uuid4(),
        event_type="training.session.closed",
        aggregate_type="training_session",
        aggregate_id=training_session.id,
        payload={
            "session_id": training_session.id,
            "team_id": training_session.team_id,
            "season_id": training_session.season_id,
            "microcycle_id": training_session.microcycle_id,
            "closed_at": datetime.utcnow().isoformat()
        }
    )
    session.add(outbox)
```

Regra absoluta:
**nunca publique direto na fila dentro do request HTTP**.

---

## 3. Dispatcher assíncrono (worker)

### Função

Processo separado (Celery, RQ, BullMQ, ou loop simples) que:

1. lê `outbox_events` com `status = pending`
2. publica na fila
3. marca como `published`

```sql
UPDATE outbox_events
SET status = 'published', published_at = now()
WHERE id = :id;
```

Se o worker cair, os eventos continuam no banco. Nada se perde.

---

## 4. `processed_events` — Idempotência do consumidor

### Finalidade

Evitar **efeitos duplicados** quando:
– o broker redeliver
– o worker reinicia
– o mesmo evento é processado duas vezes

### Tabela

```sql
CREATE TABLE processed_events (
  event_id UUID PRIMARY KEY,
  consumer TEXT NOT NULL,
  processed_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### Uso no consumidor (Statistics / Reports)

Fluxo padrão:

1. recebe evento
2. tenta inserir `event_id`
3. se falhar (unique violation) → **ignora**
4. se inserir → processa normalmente

```python
try:
    session.add(ProcessedEvent(
        event_id=event.id,
        consumer="statistics"
    ))
    session.commit()
except IntegrityError:
    return  # evento já processado
```

Isso torna **reprocessamento 100% seguro**.

---

## 5. `idempotency_keys` — proteção de endpoints HTTP

### Finalidade

Evitar duplicação quando:
– frontend faz retry
– usuário clica duas vezes
– conexão cai após resposta

Crítico para:

* `POST /training-sessions/{id}/close`
* `POST /reports/{id}/finalize`
* `POST /reports/{id}/lock`

### Tabela

```sql
CREATE TABLE idempotency_keys (
  key TEXT PRIMARY KEY,
  request_hash TEXT NOT NULL,
  response JSONB NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### Uso no FastAPI (middleware ou decorator)

Fluxo:

1. cliente envia `Idempotency-Key`
2. backend calcula hash do request
3. se chave existe → retorna `response` salva
4. se não → executa, salva resposta, retorna

```python
existing = session.get(IdempotencyKey, key)
if existing:
    return JSONResponse(existing.response)

response = handler()
session.add(IdempotencyKey(
    key=key,
    request_hash=hash,
    response=response.dict()
))
```

TTL recomendado: 24h (job de limpeza).

---

## 6. Como isso se encaixa no fluxo do HB Track

### Exemplo real: fechar sessão

1. API fecha sessão (TREINOS)
2. grava `outbox_events`
3. responde **imediatamente** ao frontend
4. dispatcher publica evento
5. Statistics consome
6. Statistics grava `processed_events`
7. métricas ficam disponíveis
8. Reports só reage depois

UX:
– usuário vê sessão fechada na hora
– estatísticas aparecem segundos depois
– nenhum risco de duplicação

---

## 7. Alembic (ordem de migrations)

Ordem recomendada:

1. `outbox_events`
2. `processed_events`
3. `idempotency_keys`

Nunca misturar essas migrations com tabelas de negócio.

---

## 8. O que isso NÃO faz (importante)

– não cria consistência forte cross-domain (não precisa)
– não torna tudo síncrono
– não expõe fila ao frontend
– não aumenta carga cognitiva

Ele apenas **garante confiabilidade**, que é base da UX que você desenhou.

---

## 9. Estado final

Com essas três tabelas:
– eventos não se perdem
– retries são seguros
– auditoria é completa
– UX permanece previsível

Isso fecha **infra + arquitetura + experiência**.

Sim. **Agora a experiência de UX está completa e fechada**, nos três níveis corretos: **arquitetura de navegação**, **páginas/telas** e **padrões de interação**. Não há lacunas conceituais nem decisões pendentes de UX.

Abaixo está a confirmação objetiva, item a item, com **onde entra**, **por quê** e **status**.

---

## 1. Arquitetura de páginas, telas e navegação

**Status: FECHADO**

* Separação clara e definitiva:

  * **Treinos** = planejar e executar (escrita)
  * **Statistics** = analisar e decidir (leitura)
  * **Reports** = formalizar e encerrar (institucional)
* Sidebar profissional respeitada.
* Breadcrumbs hierárquicos garantem orientação espacial.
* Nenhuma sobreposição de responsabilidade entre domínios.

---

## 2. Validação dos componentes de UX (um a um)

### Modal de Herança Inteligente

**Usado** em Planejamento / início de temporada.
Decisão consciente, preview explícito.
Status: correto e fechado.

### Empty State de Início de Ciclo

**Usado** em Treinos → Planejamento.
CTA único para Ritual de Início.
Status: correto e fechado.

### Sticky Header de Identificação da Atleta

**Usado** em Statistics (listas longas) e Reports.
Evita desorientação cognitiva.
Status: correto e fechado.

### Campo Markdown com limite dinâmico

**Usado** em Reports (sumário, interpretação).
Controla densidade sem engessar narrativa.
Status: correto e fechado.

### Stepper de Progresso da Temporada

**Usado** em Planejamento e visão da temporada.
Reflete modelo mental real (Pré/Comp/Trans).
Status: correto e fechado.

### Toggle de Visibilidade (governança)

**Usado** apenas em notas institucionais.
Clareza de audiência, sem vigilância.
Status: correto e fechado.

### Floating Action Button (FAB)

**Usado** somente em Sessão de Treino / Scout ao vivo.
Nunca em planejamento ou análise.
Status: correto e fechado.

### Dashboard de Cards Colapsáveis

**Usado** em Statistics (equipes / mesociclo).
Progressive disclosure bem aplicado.
Status: correto e fechado.

### Badge de Status de Auditoria

**Usado** em heranças, preferências e governança.
Feedback de estado, não punitivo.
Status: correto e fechado.

### Breadcrumbs Hierárquicos

**Obrigatórios** em todas as telas profundas.
Previne erro e perda de contexto.
Status: correto e fechado.

### Botão de Confirmação “Cópia Suja”

**Usado** em herança de planejamento.
Deixa explícito que revisão é esperada.
Status: correto e fechado.

### Timeline Lateral de Versões

**Usada** em anotações da coordenação.
Leitura passiva, histórico transparente.
Status: correto e fechado.

### Visualizador de PDF In-app

**Usado** em Reports.
Toggle Técnico | Executivo, mesma base de dados.
Status: correto e fechado.

### Date Range Picker Travado

**Usado** em Statistics e Reports.
Elimina leituras inválidas.
Status: correto e fechado.

### Quick Search Filter

**Usado** em listas longas de atletas.
Busca semântica > literal.
Status: correto e fechado.

---

Ok. Abaixo está o **checklist final de UX para QA**, focado **exclusivamente no que precisa ser validado antes de liberar**, organizado por domínio e por risco de UX. Se tudo aqui passar, o sistema está pronto para uso real sem degradação de confiança.

---

## 1. Navegação e Arquitetura Global

* Sidebar respeita RBAC em todos os papéis (atleta, treinador, coordenação, admin).
* Itens **Treinos**, **Statistics** e **Reports** nunca se misturam visual ou semanticamente.
* Breadcrumbs aparecem em todas as telas profundas e refletem corretamente: Clube > Equipe > Temporada > Ciclo.
* Troca de equipe ou temporada limpa corretamente o contexto (sem “vazamento” de dados).

---

## 2. Treinos — Planejamento (UX de intenção)

* Empty State aparece quando não há ciclo/microciclo e CTA leva corretamente ao Ritual de Início.
* Modal de Herança Inteligente:

  * Mostra preview claro do que será herdado.
  * Não aplica nada sem confirmação explícita.
  * Após confirmar, status “Revisão Necessária” fica visível.
* Stepper de Progresso da Temporada reflete corretamente a fase atual.
* Sugestões:

  * Máximo de uma por camada (foco / carga / tipo).
  * Sempre explicam a base histórica.
  * Nunca se aplicam automaticamente.
* Planejamento não gera estatística nem aparece em Statistics.

---

## 3. Treinos — Sessões (UX sob pressão)

* Criar sessão é possível em poucos segundos.
* FAB aparece apenas em sessão/scout, nunca em planejamento ou estatísticas.
* Pré-preenchimento de focos funciona quando há planejamento e é totalmente editável.
* Fechamento de sessão:

  * Valida presença e focos.
  * Não bloqueia por alertas de desvio.
  * Após fechar, tela fica somente leitura.
* Recarregar a página após fechar não reabre edição.

---

## 4. Statistics — Leitura Analítica

* `/statistics` mostra apenas sessões fechadas.
* Badges de risco/desvio:

  * São visuais, não bloqueantes.
  * Não exibem texto narrativo.
* `/statistics/teams`:

  * Mostra apenas dados agregados.
  * Coordenação não consegue acessar sessões individuais.
* `/statistics/athletes`:

  * Sticky header da atleta permanece visível em scroll longo.
  * Quick Search Filter funciona por posição e percentil.
* Date Range Picker:

  * Está travado aos marcos da temporada.
  * Não permite intervalos inválidos.

---

## 5. Reports — Formalização Institucional

* Relatório só pode ser criado para período elegível (mesociclo fechado ou temporada).
* Snapshot é congelado na criação (alterar dados depois não muda relatório).
* Campo Markdown:

  * Contador de caracteres funciona.
  * Limite muda conforme tipo de relatório.
* Toggle de visibilidade (notas institucionais):

  * Interno não aparece na versão externa.
* Timeline lateral de versões:

  * Mostra histórico completo.
  * Versões antigas são somente leitura.
* Visualizador de PDF in-app:

  * Toggle Técnico | Executivo funciona.
  * Versão Executiva respeita limite rígido de 5 gráficos e ordem fixa.

---

## 6. Governança e Continuidade

* Interpretação final:

  * Campo opcional.
  * Editável até fechamento.
  * Somente leitura após.
* Painel de Continuidade:

  * Heranças visíveis.
  * Aplicar é opcional.
  * Confirmar ciência é obrigatório.
* Badge de Auditoria:

  * Estados corretos (Pendente / Revisado / Aprovado).
  * Sem acesso a textos individuais pela coordenação.

---

## 7. Infra com impacto direto em UX (crítico)

* Repetir ação crítica (fechar sessão, finalizar relatório) com mesma Idempotency-Key:

  * Retorna mesma resposta.
  * Não duplica efeito.
* Simular falha do worker:

  * Evento fica em `outbox_events`.
  * Processa corretamente ao retomar.
* Reprocessar evento:

  * `processed_events` impede duplicação.
* UI nunca mostra “estado intermediário confuso” (ex.: sessão aberta mas estatística parcialmente visível).

---

## 8. Testes finais de confiança do usuário

* Usuário entende claramente:

  * o que é planejamento,
  * o que é execução,
  * o que é análise,
  * o que é relatório.
* Nenhuma ação gera surpresa ou sensação de vigilância.
* Não existe caminho onde o usuário “não sabe o que fazer”.

---

## Conclusão objetiva

Se **todos os itens acima passam**, então:

* a UX está íntegra,
* o modelo mental está preservado,
* o sistema é confiável para operação real,
* não haverá rejeição silenciosa do usuário.

formulário de fechamento de treino

(UX + campos + validações)

1. Momento e papel do formulário

O formulário de fechamento de treino é o ponto de consolidação da execução real.
Enquanto a sessão está em draft ou open, os dados são editáveis e não entram em estatísticas.
Somente ao acionar Fechar treino a sessão:

passa para closed

torna-se dado oficial

fica elegível para Statistics e Reports

depois transita para read_only

Isso está explicitamente definido no RAG como regra de integridade do sistema.

2. Estrutura de UX da tela (estado atual)

A tela de sessão possui blocos fixos e ordem estável, para reduzir carga cognitiva:

Header de contexto

Equipe

Data

Tipo de sessão

Status (Draft / Open / Closed)

Presença

Lista de atletas

Estados: presente, ausente, DM, lesionado

Presença é obrigatória para fechar

Carga do treino

RPE médio (0–10)

Minutos médios

Carga interna derivada

Esses campos já existem no schema e são esperados no fechamento

Focos do treino (núcleo do formulário)

7 focos fixos

Preenchidos via sliders de 0 a 100

Contador visual da soma total

Aviso visual se exceder o limite

Wellness / observações (opcional)

Clima do grupo

Destaques

Correções futuras

Botão “Fechar treino”

Ação explícita

Idempotente

Último passo do fluxo

3. Focos de treino — como estão definidos hoje
3.1 Natureza dos focos

Os focos não são uma tabela editável pelo usuário.
Eles são campos primários da sessão de treino, definidos por migration.

Hoje existem 7 focos fixos, persistidos como colunas focus_*_pct na tabela training_sessions.

Esses campos são:

parte obrigatória da execução

base direta das estatísticas de equipe

usados para identificar tipos de treino e evolução técnica

3.2 Regras de validação (já documentadas no RAG)

No fechamento da sessão, o backend valida:

Cada foco deve estar entre 0 e 100

A soma total dos focos ≤ 120

permite treinos híbridos

Pelo menos um foco > 0 é obrigatório para fechar

Sessões antigas podem ter focos nulos (legado), mas sessões novas não

Importante:
O sistema não bloqueia o preenchimento enquanto o usuário edita.
A validação acontece no ato de fechar, com feedback claro.

4. Tempo e fricção esperados (UX)

O RAG define explicitamente:

Preenchimento dos focos deve levar menos de 15 segundos

Por isso:

sliders em vez de inputs numéricos

contador automático

aviso visual, não erro modal

O objetivo é viabilizar uso em quadra, sob pressão de tempo.

5. Contrato técnico do fechamento
Endpoint

POST /training-sessions/{id}/close

O que acontece ao fechar

Validação de presença

Validação de focos (regras acima)

Persistência definitiva

Emissão de evento training.session.closed

Sessão passa para closed → read_only

Repetir a chamada com a mesma Idempotency-Key retorna a mesma resposta (sem duplicar efeito).

6. O que o formulário não faz (importante)

Não recalcula estatísticas

Não sugere ajustes

Não compara com planejamento

Não gera relatório

Não avalia desempenho individual

Ele apenas registra fielmente o que foi treinado.

7. Resumo objetivo

Hoje, o formulário de fechamento de treino está configurado para:

ser rápido

coletar os 7 focos obrigatórios

garantir integridade estatística

separar execução de análise

alimentar corretamente Statistics e Reports

O que ainda pode existir como gap não é conceitual, é implementação de UI completa (sliders, contador, feedback visual), pois o backend e o modelo já estão preparados.

Segue **exatamente o que falta implementar no frontend** para o **formulário de fechamento de treino** ficar **100% alinhado ao RAG**, **campo por campo**, sem propor nada novo.

---

## 1. Header de contexto (TOPO DA TELA)

**Estado atual**

* Contexto parcial ou inconsistente entre telas.

**Falta implementar**

* Header fixo (sticky) com:

  * Equipe
  * Data da sessão
  * Tipo de sessão
  * Status visual: `Draft | Open | Closed | Read-only`
* Mudança visual clara ao transitar para `closed`.

**Validação UX**

* Em `closed/read-only`, inputs desabilitados.
* Header permanece visível durante scroll.

---

## 2. Presença (OBRIGATÓRIO)

**Estado atual**

* Lista existe, mas fechamento nem sempre valida corretamente.

**Falta implementar**

* Validação **bloqueante no frontend** ao fechar:

  * Todos os atletas devem ter um estado definido.
* Indicador visual de conclusão do bloco (check ou badge).
* Mensagem clara se tentar fechar sem presença completa.

**Regra**

* Presença é requisito mínimo para fechar.

---

## 3. Carga do treino (RPE / Minutos)

**Estado atual**

* Campos existem no schema, UX inconsistente.

**Falta implementar**

* Inputs claros para:

  * RPE médio (slider 0–10 ou stepper)
  * Minutos médios
* Exibir carga interna calculada (read-only).
* Validação leve:

  * Não bloquear digitação
  * Avisar se vazio ao tentar fechar

**Regra**

* RAG espera esses dados no fechamento, mesmo que simples.

---

## 4. FOCOS DO TREINO (NÚCLEO — CRÍTICO)

### 4.1 Sliders dos 7 focos

**Estado atual**

* Backend pronto
* Frontend incompleto ou inexistente

**Falta implementar**

* 7 sliders (0–100), um para cada foco fixo.
* Labels fixos (não editáveis).
* Inputs sempre visíveis, sem accordion.

---

### 4.2 Contador da soma total

**Falta implementar**

* Contador em tempo real da soma dos 7 focos.
* Estados visuais:

  * Normal: ≤ 120
  * Atenção: > 120 (amarelo/vermelho)

---

### 4.3 Validações no fechamento

**Falta implementar**

* No clique em **Fechar treino**, validar:

  * Cada foco ∈ [0, 100]
  * Soma total ≤ 120
  * Pelo menos **1 foco > 0**
* Mensagem inline clara, sem modal bloqueante durante edição.

**Importante**

* Não bloquear enquanto edita.
* Bloquear apenas no ato de fechar.

---

### 4.4 Performance e tempo

**Falta implementar**

* UX otimizada para:

  * Preenchimento < 15 segundos
  * Sliders grandes (mobile/quadra)
  * Sem digitação obrigatória

---

## 5. Wellness / Observações (OPCIONAL)

**Estado atual**

* Campos existem, mas sem hierarquia clara.

**Falta implementar**

* Campos claramente marcados como opcionais:

  * Clima do grupo
  * Destaques
  * Correções futuras
* Limite de caracteres visível (se aplicável).
* Nunca bloquear fechamento por esses campos.

---

## 6. Botão “Fechar treino”

**Estado atual**

* Endpoint existe, UX incompleta.

**Falta implementar**

* Botão primário destacado:

  * Texto claro: “Fechar treino”
* Ao clicar:

  * Rodar todas as validações acima
  * Enviar `POST /training-sessions/{id}/close`
  * Usar `Idempotency-Key`
* Feedback imediato:

  * Sucesso → status muda para `closed`
  * Erro → mensagem específica (qual regra falhou)

---

## 7. Pós-fechamento (READ-ONLY)

**Falta implementar**

* Após sucesso:

  * Desabilitar todos os campos
  * Remover FAB
  * Mostrar aviso: “Sessão encerrada — somente leitura”
* Refresh da página mantém estado correto (não reabre edição).

---

## 8. Estados de erro e edge cases

**Falta implementar**

* Se backend retornar erro:

  * 409 (estado inválido)
  * 422 (validação de focos)
* Mensagens humanas, não técnicas.
* Nunca perder dados já digitados.

---

## 9. O que NÃO falta (já está decidido)

* Não falta regra de negócio.
* Não falta modelo de dados.
* Não falta decisão de UX.
* Não falta endpoint.

O **único gap real é frontend**.

---

## RESUMO FINAL

Para ficar 100% alinhado ao RAG, o frontend precisa:

* Expor corretamente **os 7 focos com sliders**
* Validar **somente no fechamento**
* Garantir **presença + focos** como mínimo obrigatório
* Travar corretamente após `closed`
* Manter UX rápida, sem burocracia




































