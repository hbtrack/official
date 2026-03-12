---
doc_type: canon
version: "1.0.0"
last_reviewed: "2026-03-11"
status: active
---

# Regras do Domínio de Handebol — HB Track

## 1. Fonte Normativa

- **Rulebook**: IHF Rules of the Game — Indoor Handball (edição vigente)
- **Arquivo local**: `.contract_driven/09A - Rules of the Game_Indoor Handball_E.pdf`
- **Nota de integridade**: O PDF é a fonte primária. Este documento extrai, traduz e comenta as regras relevantes ao sistema. Em caso de conflito entre este documento e o PDF do rulebook, **o PDF prevalece**. Atualize este documento para corrigir a divergência.
- **Última revisão deste documento**: 2026-03-11

---

## 2. Regra Cardinal para Agentes de IA

> Agentes NÃO podem inferir, inventar ou extrapolar regras de handebol. Se uma regra não está documentada aqui com `Fonte` preenchida e referenciando o Rulebook IHF, o agente DEVE bloquear e solicitar atualização deste documento antes de prosseguir.

Esta regra vale para qualquer artefato que toque em: estado de partida, evento de jogo, sanção, substituição, composição de equipe, tempo de jogo, scout, métricas competitivas ou qualquer conceito derivado da modalidade.

---

## 3. Módulos Handball-Sensíveis

Os módulos abaixo têm alta probabilidade de depender das regras documentadas neste arquivo:

| Módulo | Nível de Dependência |
|--------|---------------------|
| `training` | Alto — exercícios orientados à modalidade, posições, fases do jogo |
| `competitions` | Alto — estrutura de fases, pontuação, tamanho de bola por categoria |
| `matches` | Crítico — timeline de eventos, sanções, substituições, fases da partida |
| `scout` | Crítico — todos os eventos rastreados derivam de regras da modalidade |
| `analytics` | Alto — métricas derivadas de eventos de jogo e treino |
| `wellness` | Médio — periodização vinculada ao calendário competitivo |

**Regra**: qualquer invariante nesses módulos que referencie regra esportiva DEVE citar um `HBR-XXX` deste documento. Invariante sem âncora `HBR-XXX` em módulo handball-sensível está incompleta.

---

## 4. Regras Documentadas (HBR-001 a HBR-014)

---

### HBR-001 — Tempo de Jogo

- **Fonte**: Regra 2 do Rulebook IHF (Playing Time)
- **Resumo**: Uma partida de handebol tem 2 tempos de 30 minutos cada, separados por intervalo de 10 minutos. Em caso de empate em fase eliminatória, prorrogação com 2 períodos de 5 minutos com intervalo de 1 minuto entre eles. Se o empate persistir após a prorrogação, disputa de tiros de 7 metros (penaltis).
- **Impacto no sistema**: módulos `matches`, `competitions`, `analytics`
- **Restrições de implementação**:
  - O sistema deve registrar a duração de cada tempo (1º tempo, 2º tempo, prorrogação 1, prorrogação 2)
  - Prorrogação é opcional e configurada por formato de competição — nem toda partida tem prorrogação
  - Tiros de 7m como desempate são opcionais e configurados por fase competitiva
  - O estado da partida deve evoluir pelas fases: `PRIMEIRO_TEMPO → INTERVALO → SEGUNDO_TEMPO → (FIM | PRORROGACAO_1 → PRORROGACAO_2 → (FIM | PENALTIS))`

---

### HBR-002 — Time-out de Equipe

- **Fonte**: Regra 2:10 do Rulebook IHF (Team Time-outs)
- **Resumo**: Cada equipe tem direito a 1 time-out de 1 minuto por tempo regular, totalizando 2 time-outs por partida (um por tempo). Em prorrogação, cada equipe pode solicitar 1 time-out adicional por período de prorrogação. O time-out só pode ser solicitado quando a equipe está em posse da bola.
- **Impacto no sistema**: módulos `matches`, `scout`
- **Restrições de implementação**:
  - O sistema deve rastrear time-outs utilizados por equipe e por tempo
  - Alerta quando todos os time-outs do tempo atual já foram utilizados
  - Evento de time-out deve registrar: equipe, tempo de jogo, fase (1º tempo, 2º tempo, prorrogação)
  - O sistema NÃO valida posse de bola em tempo real — registra o evento quando informado pelo operador

---

### HBR-003 — Sanções Disciplinares

- **Fonte**: Regra 16 do Rulebook IHF (Punishments)
- **Resumo**: Hierarquia de sanções, da mais leve à mais grave:
  1. Advertência verbal — sem registro oficial; correção de conduta
  2. Cartão amarelo — advertência formal; máximo de 3 cartões amarelos por equipe por jogo
  3. Suspensão de 2 minutos — jogador fora de quadra por 2 minutos; equipe em inferioridade numérica
  4. Cartão vermelho — expulsão definitiva do jogador; equipe não pode repor o jogador expulso por 2 minutos
  5. Desclassificação — punição mais grave; report obrigatório à federação
- **Impacto no sistema**: módulos `matches`, `scout`, `competitions`
- **Restrições de implementação**:
  - Sistema deve registrar todas as sanções com timestamp, jogador, tipo e fase da partida
  - Suspensões de 2 minutos afetam a composição em quadra — rastreável por scout
  - Cartão vermelho: jogador removido permanentemente; equipe fica em inferioridade pelos 2 minutos seguintes
  - Advertência verbal NÃO é registrada como evento formal no sistema
  - Acúmulo de 3 cartões amarelos por equipe deve ser sinalizável

---

### HBR-004 — Gol

- **Fonte**: Regra 9 do Rulebook IHF (Scoring a Goal)
- **Resumo**: Gol é marcado quando a bola passa completamente pela linha do gol, entre os postes e abaixo do travessão, sem que a equipe atacante tenha cometido infração antes ou durante o arremesso. Gol contra (na própria meta) conta para a equipe adversária.
- **Impacto no sistema**: módulos `matches`, `scout`, `analytics`
- **Restrições de implementação**:
  - Evento de gol deve registrar: jogador marcador, assistente (opcional), tempo de jogo, fase, goleiro adversário, posição de arremesso (opcional)
  - Gol contra deve ser registrado como gol para a equipe adversária, com indicação do jogador que marcou contra
  - O placar é derivado da contagem de eventos de gol — nunca inserido diretamente como número

---

### HBR-005 — Tiro de 7 Metros (Penalti)

- **Fonte**: Regra 14 do Rulebook IHF (The 7-metre Throw)
- **Resumo**: Concedido quando uma chance clara de gol é impedida de forma irregular, dentro ou fora da área de gol, por qualquer jogador incluindo o goleiro. É arremessado da linha de 7 metros por qualquer jogador de linha da equipe beneficiada. Todos os outros jogadores devem ficar fora da área entre 9m e o gol durante a cobrança.
- **Impacto no sistema**: módulos `matches`, `scout`
- **Restrições de implementação**:
  - Sistema deve registrar: motivo do penalti (infração ou decisão da mesa), jogador cobrador, resultado (gol, defesa, fora, poste)
  - Tiro de 7m como desempate ao fim da partida (série de penaltis) é um contexto diferente — registrado com fase `PENALTIS`
  - O sistema NÃO deve reduzir o tiro de 7m a "arremesso genérico" — é evento com semântica específica

---

### HBR-006 — Tiro Livre

- **Fonte**: Regra 13 do Rulebook IHF (Free Throw)
- **Resumo**: Principal método de reposição de jogo após infração. Cobrado do local da infração, ou da linha de 9 metros (tracejada) se a infração ocorreu entre a linha de 9m e a área de gol. A defesa deve recuar pelo menos 3 metros do cobrador. Pode ser cobrado rapidamente sem assobio do árbitro.
- **Impacto no sistema**: módulos `matches`, `scout`
- **Restrições de implementação**:
  - Tiro livre deve ser distinguido de outros tipos de cobrança (lateral, goleiro, 7m)
  - Para análise tática: registrar posição aproximada e cobrador quando informado pelo operador
  - O sistema não valida a distância de 3m da defesa — é responsabilidade dos árbitros

---

### HBR-007 — Substituição de Jogadores

- **Fonte**: Regra 4:4 do Rulebook IHF (Substitutions)
- **Resumo**: Substituições são ilimitadas durante o jogo e podem ocorrer a qualquer momento, sem parada de jogo. Cada equipe tem uma zona de substituição designada (próxima ao banco de reservas). O jogador substituído deve sair completamente da quadra antes do substituto entrar. Goleiro pode ser substituído por jogador de linha e vice-versa, sem restrições especiais.
- **Impacto no sistema**: módulos `matches`, `training`, `scout`
- **Restrições de implementação**:
  - Sistema deve rastrear entradas e saídas de jogadores com timestamp
  - Composição em quadra é derivada dos eventos de substituição — não inserida diretamente
  - Substituição de goleiro por jogador de linha deve ser registrada (relevante para análise tática e para composição da barreira defensiva)
  - Número de substituições é ilimitado — sem validação de cota

---

### HBR-008 — Composição de Equipe

- **Fonte**: Regra 4:1 do Rulebook IHF (Players and Officials)
- **Resumo**: Máximo de 16 jogadores por equipe inscritos em súmula. No máximo 7 jogadores em quadra simultaneamente (6 de linha + 1 goleiro). Mínimo de 5 jogadores para iniciar a partida. Membros da comissão técnica (técnico, preparador, médico, etc.) podem estar no banco mas não em quadra; podem ser sancionados com cartão amarelo/vermelho/desclassificação.
- **Impacto no sistema**: módulos `matches`, `teams`, `competitions`
- **Restrições de implementação**:
  - Sistema deve validar no máximo 16 jogadores inscritos na súmula de cada equipe
  - Sistema deve alertar se a composição em quadra ultrapassar 7 jogadores (dado derivado de eventos de substituição)
  - Comissão técnica (staff) deve ser distinguida de jogadores na súmula
  - Suspensões de 2 minutos reduzem temporariamente o número de jogadores permitidos em quadra

---

### HBR-009 — O Goleiro

- **Fonte**: Regra 6 do Rulebook IHF (The Goalkeeper)
- **Resumo**: O goleiro pode se mover livremente dentro de sua área de gol. Fora da área, está sujeito às mesmas regras dos jogadores de linha — inclusive de não poder tocar a bola com o pé abaixo do joelho. O goleiro pode arremessar em qualquer direção após sair da área. Dentro da área, não pode ser bloqueado fisicamente.
- **Impacto no sistema**: módulos `training`, `matches`, `scout`
- **Restrições de implementação**:
  - Sistema deve distinguir goleiros de jogadores de linha no elenco — são posições com semântica diferente
  - Estatísticas de goleiro (defesas, gols sofridos, saídas de área) são métricas distintas das de jogadores de linha
  - Em treinos, exercícios específicos de goleiro devem poder ser marcados como `GOLEIRO` na posição-alvo

---

### HBR-010 — Área de Gol

- **Fonte**: Regra 6 do Rulebook IHF (The Goal Area)
- **Resumo**: Área semicircular a 6 metros do gol — exclusiva ao goleiro da equipe defensora. Jogadores de linha não podem entrar na área de gol adversária (apenas a bola pode cair dentro). Linha tracejada a 9 metros define a linha de tiro livre. Arremessos em suspensão sobre a área de gol são válidos. Jogadores de linha não podem usar a área do próprio goleiro como vantagem.
- **Impacto no sistema**: módulos `matches`, `training`, `scout`
- **Restrições de implementação**:
  - O sistema não valida posições físicas dos jogadores em tempo real
  - Infrações de área devem ser registradas como eventos quando informadas pelo operador de scout
  - Em análise de dados, posições de arremesso são categorizadas em relação à área (6m, 9m, contra-ataque, 7m)

---

### HBR-011 — Bola: Tamanho por Categoria

- **Fonte**: Regra 3 do Rulebook IHF (The Ball)
- **Resumo**: O tamanho da bola é padronizado por gênero e faixa etária:
  - **Tamanho 3** (58–60 cm, 425–475 g): masculino adulto (IHF/Nacional)
  - **Tamanho 2** (54–56 cm, 325–375 g): feminino adulto, masculino juvenil (sub-18)
  - **Tamanho 1** (50–52 cm, 290–330 g): categorias de base e mini-handebol
- **Impacto no sistema**: módulos `competitions`, `training`
- **Restrições de implementação**:
  - Sistema deve associar categoria de competição ao tamanho de bola correto
  - Em planejamento de treinos, o tamanho de bola pode ser especificado por sessão quando relevante para a categoria
  - Enum de bola no sistema: `TAMANHO_1`, `TAMANHO_2`, `TAMANHO_3`

---

### HBR-012 — Mesa de Controle / Secretaria

- **Fonte**: Regra 18 do Rulebook IHF (Scorekeeper / Timekeeper)
- **Resumo**: A mesa de controle é responsável pela secretaria oficial de uma partida: cronometragem oficial, registro de gols e placar, controle de cartões e suspensões, registro de substituições, comunicação com os árbitros sobre irregularidades. A mesa não arbitra — ela registra e controla o tempo.
- **Impacto no sistema**: módulo `matches`
- **Restrições de implementação**:
  - O HB Track pode oferecer suporte digital à operação da mesa, mas NÃO substitui a secretaria oficial em jogos federados
  - Dados inseridos via suporte à mesa têm o mesmo nível de confiança que dados inseridos via scout — são registros operacionais
  - Importação de dados de mesa de sistemas externos (ex: software de secretaria) é permitida via módulo `matches`

---

### HBR-013 — Fases Cronológicas da Partida

- **Fonte**: Regra 2 do Rulebook IHF (Playing Time, Final Signal, Time-out)
- **Resumo**: Sequência canônica de fases de uma partida de handebol:
  1. **Pré-jogo** — aquecimento; tempo não regulamentado
  2. **Primeiro Tempo** — 30 minutos; cronômetro crescente ou decrescente conforme preferência
  3. **Intervalo** — 10 minutos entre os tempos
  4. **Segundo Tempo** — 30 minutos
  5. **Prorrogação 1** — 5 minutos; apenas em empate em fase eliminatória
  6. **Intervalo de Prorrogação** — 1 minuto
  7. **Prorrogação 2** — 5 minutos
  8. **Tiros de 7 Metros** — série de penaltis se empate persistir; apenas quando formato competitivo exige
  9. **Encerrado** — partida finalizada
- **Impacto no sistema**: módulos `matches`, `competitions`, `scout`, `analytics`
- **Restrições de implementação**:
  - O sistema deve modelar estas fases como estados de uma máquina de estados
  - Eventos de scout são vinculados obrigatoriamente a uma fase e ao tempo de jogo dentro da fase
  - Fases de prorrogação e penaltis só existem quando configuradas pelo formato de competição
  - Enum de fases: `PRE_JOGO`, `PRIMEIRO_TEMPO`, `INTERVALO`, `SEGUNDO_TEMPO`, `PRORROGACAO_1`, `INTERVALO_PRORROGACAO`, `PRORROGACAO_2`, `PENALTIS`, `ENCERRADO`

---

### HBR-014 — Treino Orientado à Modalidade

- **Fonte**: Interpretação pedagógica das regras IHF — este item não é uma regra do Rulebook. É uma sistematização do conhecimento técnico da modalidade para fins de modelagem no sistema.
- **Resumo**: O treinamento de handebol organiza-se por múltiplas dimensões:
  - **Categorias etárias**: mini-handebol, infantil (sub-14), juvenil (sub-16/sub-18), júnior (sub-20), adulto
  - **Posições**: goleiro, ponta esquerdo, ponta direito, armador esquerdo, armador central, armador direito, pivô
  - **Fases do jogo**: ataque organizado, contra-ataque, defesa fechada (5:1, 6:0, 3:2:1), transição defensiva, transição ofensiva
  - **Periodização**: macrociclo (temporada) → mesociclo (bloco de 3–6 semanas) → microciclo (semana) → sessão (treino individual)
  - **Capacidades físicas**: velocidade, resistência aeróbia/anaeróbia, força, coordenação, agilidade — cada uma com prevalência em fases distintas da periodização
- **Impacto no sistema**: módulos `training`, `analytics`, `wellness`
- **Restrições de implementação**:
  - Sistema deve suportar classificação de exercícios por posição-alvo e fase do jogo
  - Periodização deve ser modelável nos 4 níveis (macrociclo → sessão)
  - Categorias etárias devem ser configuráveis por temporada e equipe
  - Sistema não deve reduzir posições a um campo de texto livre — enum `POSICAO` é obrigatório para dados estruturados

---

## 5. Termos de Referência Rápida

| Termo IHF (inglês) | Termo PT-BR | HBR | Módulos |
|--------------------|-------------|-----|---------|
| Goal Area | Área de gol | HBR-010 | matches, training, scout |
| 7-metre throw | Tiro de 7m / Penalti | HBR-005 | matches, scout |
| Free throw | Tiro livre | HBR-006 | matches, scout |
| Suspension (2 min) | Suspensão de 2 minutos | HBR-003 | matches, scout, competitions |
| Yellow card | Cartão amarelo | HBR-003 | matches, scout |
| Red card | Cartão vermelho | HBR-003 | matches, scout, competitions |
| Disqualification | Desclassificação | HBR-003 | matches, competitions |
| Substitution | Substituição | HBR-007 | matches, training, scout |
| Team time-out | Time-out de equipe | HBR-002 | matches, scout |
| Playing time | Tempo de jogo | HBR-001 | matches, competitions, analytics |
| Goalkeeper | Goleiro | HBR-009 | training, matches, scout |
| Scorekeeper / Timekeeper | Mesa de controle / Secretaria | HBR-012 | matches |
| Goal | Gol | HBR-004 | matches, scout, analytics |
| Extra time / Overtime | Prorrogação | HBR-001 | matches, competitions |
| Pivot | Pivô | HBR-014 | training, analytics |
| Centre back | Armador central | HBR-014 | training, analytics |
| Wing | Ponta | HBR-014 | training, analytics |

---

## 6. Regra de Adaptação Local

O HB Track pode adaptar uma regra oficial do handebol ao contexto do produto **somente** quando a adaptação for registrada explicitamente neste documento ou em ADR vinculada.

**Proibições absolutas**:
- Adaptar regra da modalidade informalmente no código
- Adaptar regra apenas na UI sem registro normativo
- Adaptar regra apenas no banco sem rastreabilidade
- Usar termo esportivo ambíguo sem glossário ou regra correspondente neste documento

---

## 7. Critério de Evolução

Este documento deve ser atualizado quando:
- Um novo comportamento do produto depender de regra da modalidade não documentada aqui
- Uma adaptação local relevante for introduzida
- Uma ambiguidade esportiva afetar contrato, estado, evento ou analytics de qualquer módulo
- Um módulo handball-sensível começar a representar conceito ainda não traduzido aqui

---

## 8. Referências

- `SYSTEM_SCOPE.md` — missão, atores, macrodomínios
- `MODULE_MAP.md` — taxonomia técnica dos 16 módulos
- `DATA_CONVENTIONS.md` — convenções de enums, IDs e campos
- `.contract_driven/CONTRACT_SYSTEM_RULES.md` — regras operacionais do CDD
- `.contract_driven/09A - Rules of the Game_Indoor Handball_E.pdf` — rulebook IHF (fonte primária)
