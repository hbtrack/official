---
doc_type: canon
version: "1.0.0"
last_reviewed: "2026-03-11"
status: active
---

# Glossário de Domínio — HB Track

## 1. Propósito

Este glossário define os termos canônicos do domínio do HB Track. Quando um termo está listado aqui, sua definição é **normativa** — módulos, contratos e código devem usá-lo consistentemente.

**Regra**: se um termo do domínio não está aqui, ele não deve ser usado em contratos sem primeiro ser adicionado a este glossário via processo `documentation-only` (ver CHANGE_POLICY.md §3).

---

## 2. Convenção de Uso

- **Português**: termos em PT-BR; equivalente em inglês quando necessário para código
- **Identificador técnico** (`code_name`) (en-US): nome usado em código e artefatos técnicos; em API/JSON segue camelCase conforme SSOT de API e em banco segue snake_case conforme `DATA_CONVENTIONS.md`
- **Módulos relacionados**: quais módulos utilizam o conceito como entidade principal ou referência
- Referências a regras de handebol: `HBR-NNN` conforme `HANDBALL_RULES_DOMAIN.md`

---

## 3. Glossário

---

### CATEGORIA: Papéis e Atores

---

### Dirigente (`dirigente`)
**Definição**: Gestor máximo do clube, associação ou organização esportiva dentro do HB Track. Responsável pela configuração global do sistema, aprovação de decisões estratégicas e acesso irrestrito a todos os módulos.

**Contexto**: Papel com o nível mais alto na hierarquia de RBAC. Pode criar temporadas, gerenciar equipes, aprovar sessões de treino fora da janela padrão e visualizar dados de todos os atletas, incluindo médicos.

**Módulos**: `identity_access`, `users`, `seasons`, `teams`, `training`, `medical`, `competitions`

**Ver também**: Coordenador, RBAC, identity_access

---

### Coordenador (`coordenador`)
**Definição**: Usuário responsável pela coordenação de múltiplos times ou categorias dentro de uma organização. Tem acesso amplo mas não irrestrito — abaixo do Dirigente na hierarquia.

**Contexto**: Típico em clubes com múltiplas equipes (sub-16, sub-18, adulto). Pode visualizar e gerenciar treinos de todas as equipes sob sua coordenação, mas não tem acesso a configurações globais.

**Módulos**: `identity_access`, `users`, `teams`, `training`, `competitions`

**Ver também**: Dirigente, Treinador, RBAC

---

### Treinador (`treinador`)
**Definição**: Responsável técnico pelo treino e estratégia tática de um time específico. Cria e gerencia sessões de treino, define composições e planeja mesociclos.

**Contexto**: Principal ator do módulo `training`. Tem janela de 10 minutos para editar sessões de treino após criação. Pode visualizar dados de wellness dos atletas sob sua responsabilidade.

**Módulos**: `training`, `wellness`, `teams`, `matches`, `scout`

**Ver também**: Sessão de Treino, Janela de Edição, PSE

---

### Atleta (`atleta`)
**Definição**: Jogador registrado no sistema. Acessa seu próprio perfil, sessões de treino das suas equipes, histórico de wellness e dados de performance. Não acessa dados de outros atletas.

**Contexto**: Ator com acesso mais restrito do sistema. Submete check-ins de wellness, visualiza sessões planejadas e seu próprio histórico. Em módulo `scout`, pode visualizar suas próprias estatísticas.

**Módulos**: `users`, `training`, `wellness`, `medical`, `teams`

**Ver também**: Wellness, PSE, Carga de Treino

---

### Membro (`membro`)
**Definição**: Usuário sem papel esportivo ativo — pode ser um dirigente júnior, observador externo, parceiro de patrocínio ou funcionário administrativo do clube sem envolvimento técnico-esportivo direto.

**Contexto**: Papel com acesso mínimo ao sistema. Geralmente pode apenas visualizar informações públicas da organização (calendário de partidas, classificação). Não acessa dados de treino ou wellness.

**Módulos**: `identity_access`, `users`

**Ver também**: Dirigente, RBAC

---

### CATEGORIA: Entidades Esportivas

---

### Equipe (`team`)
**Definição**: Grupo organizado de atletas com identidade esportiva própria, geralmente definido por categoria etária (sub-16, adulto) e gênero (masculino, feminino, misto).

**Contexto**: Entidade central do sistema. Sessões de treino, partidas e competições são sempre vinculadas a uma ou mais equipes. Uma equipe pertence a uma temporada através do elenco.

**Módulos**: `teams`, `training`, `matches`, `competitions`, `wellness`

**Ver também**: Elenco, Temporada, Composição de Equipe

---

### Elenco (`roster`)
**Definição**: Conjunto de atletas oficialmente inscritos em uma equipe para uma temporada específica. O elenco é o vínculo temporal entre atleta, equipe e temporada.

**Contexto**: Um atleta pode participar de múltiplos elencos (em equipes diferentes) na mesma temporada. O elenco define quem tem acesso ao conteúdo de treino e wellness de uma equipe específica.

**Módulos**: `teams`, `training`, `wellness`, `competitions`

**Ver também**: Equipe, Temporada, Atleta

---

### Sessão de Treino (`training_session`)
**Definição**: Unidade básica e atômica de planejamento e execução de treino. Contém data, hora, duração planejada, objetivos táticos/físicos, lista de exercícios e estado de ciclo de vida.

**Contexto**: Entidade central do módulo `training`. Possui lifecycle próprio: DRAFT → SCHEDULED → IN_PROGRESS → PENDING_REVIEW → READONLY. Após 60 dias da data da sessão, torna-se imutável independentemente do estado.

**Módulos**: `training`, `wellness`, `analytics`

**Ver também**: Janela de Edição, PSE, Exercício, Microciclo

---

### Partida (`match`)
**Definição**: Jogo oficial de handebol com placar, eventos de jogo registrados, resultado e súmula. Entidade operacional que representa um confronto real entre duas equipes.

**Contexto**: A partida é o resultado canônico — placar oficial, cartões, exclusões, gols. O módulo `scout` registra a análise tática derivada da partida. Partidas pertencem a competições, mas têm lifecycle independente.

**Módulos**: `matches`, `competitions`, `scout`, `analytics`

**Ver também**: Competição, Scout, Evento de Jogo, Súmula

---

### Competição (`competition`)
**Definição**: Torneio, campeonato, liga ou copa com múltiplas partidas organizadas em fases, com classificação e sistema de pontuação definidos.

**Contexto**: Estrutura que organiza partidas em fases (grupos, quartas, semis, final). Define o formato competitivo: pontos por vitória/empate/derrota, critérios de desempate, número de participantes.

**Módulos**: `competitions`, `matches`, `teams`, `seasons`

**Ver também**: Fase, Partida, Equipe, Temporada

---

### Scout (`scout`)
**Definição**: Análise tática detalhada de uma partida com registro granular de eventos por jogador — passes, finalizações, bloqueios, posicionamentos, erros técnicos e acertos.

**Contexto**: Módulo derivado de `matches`. O scout enriquece o resultado da partida com análise técnico-tática. É alimentado durante e após a partida por analistas tático-técnicos. Eventos de scout são mais granulares que os eventos de jogo da súmula oficial.

**Módulos**: `scout`, `matches`, `analytics`

**Ver também**: Partida, Evento de Scout, Estatísticas

---

### CATEGORIA: Conceitos de Handebol

---

### Goleiro (`goalkeeper`)
**Definição**: Jogador com papel especial e equipamento diferenciado, responsável pela defesa da área de gol (área de 6 metros). Único autorizado a entrar na área de gol durante o jogo.

**Contexto**: O goleiro tem regras específicas de jogo (HBR-010): pode tocar a bola com qualquer parte do corpo dentro da área; fora da área, é tratado como jogador de linha.

**Módulos**: `matches`, `scout`, `teams`

**Ver também**: Área de Gol, Composição de Equipe, HBR-010

---

### Área de Gol (`goal_area`)
**Definição**: Área semicircular de 6 metros exclusiva ao goleiro durante o jogo. Nenhum outro jogador (de qualquer equipe) pode entrar nessa área com a bola.

**Contexto**: Referenciada em eventos de scout (invasão de área, gol anulado por invasão). Relevante para o módulo `matches` no registro de infrações. Ver regra formal HBR-010.

**Módulos**: `matches`, `scout`

**Ver também**: Goleiro, HBR-010, HANDBALL_RULES_DOMAIN.md

---

### Exclusão (`suspension`)
**Definição**: Suspensão de 2 minutos aplicada a um jogador por infração mais grave (falta perigosa, antidesportividade). O jogador sai de quadra e a equipe joga em inferioridade numérica pelo período.

**Contexto**: Evento registrado na súmula oficial da partida (módulo `matches`) e no scout (módulo `scout`). Três exclusões ao mesmo jogador resultam em desqualificação. Ver HBR-003.

**Módulos**: `matches`, `scout`

**Ver também**: Partida, Desqualificação, HBR-003, HANDBALL_RULES_DOMAIN.md

---

### Tiro de 7m (`seven_meter_throw`)
**Definição**: Penalti em handebol — cobrança de posição fixa a 7 metros do gol, concedido quando há infração que priva claramente de oportunidade de gol.

**Contexto**: Evento registrado na súmula (módulo `matches`) e analisado no scout. Equivalente ao pênalti do futebol. Cobrado com apenas o cobrador e o goleiro. Ver HBR-005.

**Módulos**: `matches`, `scout`

**Ver também**: Partida, HBR-005, HANDBALL_RULES_DOMAIN.md

---

### Tiro Livre (`free_throw`)
**Definição**: Reposição de bola concedida à equipe prejudicada por infração. Cobrado de até a linha de 9 metros (linha de tiro livre). O adversário deve recuar 3 metros.

**Contexto**: Evento mais frequente de infração — distingue-se do tiro de 7m pelo local e pela gravidade da infração. Ver HBR-006.

**Módulos**: `matches`, `scout`

**Ver também**: Tiro de 7m, HBR-006, HANDBALL_RULES_DOMAIN.md

---

### Substituição (`substitution`)
**Definição**: Troca de jogador durante o jogo sem necessidade de parada. O jogador sainte deve cruzar a linha de substituição antes do entrante entrar em quadra.

**Contexto**: Evento registrado na súmula. Sem limite de substituições no handebol — jogadores podem entrar e sair múltiplas vezes. Erro de substituição resulta em exclusão temporária. Ver HBR-007.

**Módulos**: `matches`, `scout`

**Ver também**: Composição de Equipe, HBR-007, HANDBALL_RULES_DOMAIN.md

---

### Time-out (`timeout`)
**Definição**: Parada do jogo solicitada por uma equipe para orientação técnica. Cada equipe tem direito a 1 time-out por tempo (2 por partida).

**Contexto**: Evento registrado na súmula. Relevante para análise tática no scout — frequentemente coincide com mudanças de estratégia ou composição. Ver HBR-002.

**Módulos**: `matches`, `scout`

**Ver também**: Partida, HBR-002, HANDBALL_RULES_DOMAIN.md

---

### Composição de Equipe (`team_lineup`)
**Definição**: Conjunto de até 7 jogadores em quadra simultaneamente em um dado momento (1 goleiro + 6 jogadores de linha). Definida pela equipe técnica e pode mudar a cada substituição.

**Contexto**: Registrada em eventos de scout para análise de eficiência por composição. O módulo `matches` registra a composição inicial; o `scout` rastreia variações durante o jogo. Máximo 7 jogadores simultâneos em quadra. Ver HBR-008.

**Módulos**: `matches`, `scout`, `teams`

**Ver também**: Substituição, Goleiro, HBR-008, HANDBALL_RULES_DOMAIN.md

---

### CATEGORIA: Periodização e Planejamento

---

### Temporada (`season`)
**Definição**: Período anual (ou específico) de atividade esportiva organizada. Contém competições, ciclos de treino, elencos ativos e contexto histórico. A temporada é o container temporal máximo do sistema.

**Contexto**: Toda entidade com contexto temporal no sistema (equipe, elenco, competição) está vinculada a uma temporada. Gerenciada pelo módulo `seasons`.

**Módulos**: `seasons`, `teams`, `training`, `competitions`

**Ver também**: Mesociclo, Microciclo, Elenco

---

### Mesociclo (`mesocycle`)
**Definição**: Bloco de treino de 3 a 6 semanas com objetivo físico-técnico-tático específico. Exemplos: bloco de força, bloco de velocidade, bloco técnico, período competitivo.

**Contexto**: Unidade de planejamento intermediária — acima do microciclo (semana), abaixo da temporada. Usado pelo treinador para estruturar a periodização. Referenciado no módulo `training` como agrupador de sessões.

**Módulos**: `training`, `seasons`

**Ver também**: Microciclo, Temporada, Sessão de Treino

---

### Microciclo (`microcycle`)
**Definição**: Semana de treino — a menor unidade recorrente de planejamento. Contém as sessões de treino planejadas para cada dia da semana, carga prevista e objetivos semanais.

**Contexto**: Base da periodização semanal. O treinador planeja microciclos dentro dos mesociclos. Sessões de treino são os elementos atômicos de um microciclo.

**Módulos**: `training`

**Ver também**: Mesociclo, Sessão de Treino

---

### Fase (`phase`)
**Definição**: Subfase de uma competição (fase de grupos, quartas de final, semifinais, final) ou período de preparação de treino (preparatório, competitivo, transição).

**Contexto**: No módulo `competitions`, uma fase define o formato de disputa (grupos, mata-mata) e os critérios de classificação. No módulo `training`, uma fase define o período de periodização e seus objetivos.

**Módulos**: `competitions`, `training`, `seasons`

**Ver também**: Competição, Mesociclo, Temporada

---

### CATEGORIA: Métricas e Bem-Estar

---

### Wellness (`wellness`)
**Definição**: Check-in diário de bem-estar subjetivo do atleta, composto por múltiplas dimensões: qualidade do sono, nível de fadiga, estresse, humor, dor muscular, hidratação e nutrição.

**Contexto**: Reportado pelo próprio atleta, geralmente na manhã anterior ao treino. Dados de wellness informam o treinador sobre a prontidão (readiness) do atleta para a carga do dia. Não é diagnóstico médico.

**Módulos**: `wellness`, `training`, `analytics`

**Ver também**: PSE, Carga de Treino, Readiness, Atleta

---

### PSE — Percepção Subjetiva de Esforço (`perceived_exertion`)
**Definição**: Escala Borg CR-10 (0 a 10) que o atleta usa para reportar o esforço percebido ao final de uma sessão de treino. PSE = 0 significa repouso absoluto; PSE = 10 significa esforço máximo imaginável.

**Contexto**: Coletada após cada sessão de treino. Multiplicada pela duração da sessão em minutos, resulta na Carga de Treino. É a métrica de intensidade subjetiva principal do HB Track.

**Módulos**: `wellness`, `training`, `analytics`

**Ver também**: Carga de Treino, Wellness, Sessão de Treino

---

### Carga de Treino (`training_load`)
**Definição**: Métrica numérica calculada como: `PSE × duração da sessão em minutos`. Representa o volume total de estresse fisiológico imposto ao atleta em uma sessão.

**Contexto**: Usada no módulo `analytics` para monitorar acúmulo de carga, relação carga-recuperação e risco de overtraining. Uma sessão de PSE 7 com 90 minutos resulta em carga de 630 unidades arbitrárias (UA).

**Módulos**: `wellness`, `training`, `analytics`

**Ver também**: PSE, Sessão de Treino, Wellness

---

### Janela de Edição (`edit_window`)
**Definição**: Período de tempo durante o qual uma sessão de treino pode ser modificada pelo criador ou por um superior. Define o controle de auditabilidade do registro de treino.

**Contexto**: Três janelas canônicas no HB Track: (1) Autor: 10 minutos após criação; (2) Superior (coordenador/dirigente): 24 horas após a sessão; (3) Após 60 dias da data da sessão: imutável para todos.

**Módulos**: `training`

**Ver também**: Sessão de Treino, Treinador, Invariante INV-TRAIN

---

### Readiness (`readiness`)
**Definição**: Prontidão física e mental do atleta para a carga de treino do dia, estimada a partir dos dados de wellness e histórico de carga recente. Não é diagnóstico — é indicador operacional.

**Contexto**: Calculada automaticamente pelo sistema com base no check-in de wellness do dia. Exibida ao treinador como indicador semafórico (verde/amarelo/vermelho) antes de confirmar a presença do atleta no treino.

**Módulos**: `wellness`, `training`, `analytics`

**Ver também**: Wellness, Carga de Treino, PSE

---

### CATEGORIA: Conceitos do Sistema Contract-Driven

---

### PR — Pull Request (`pr`)
**Definição**: Unidade versionada de mudança revisável. É o veículo canônico para propor e aprovar alterações em contratos e documentação normativa.

**Contexto**: Um PR deve declarar o tipo de mudança (non-breaking/breaking/internal-only/documentation-only), listar módulos e artefatos afetados e anexar evidência de validação (`_reports/contract_gates/latest.json`) quando aplicável.

**Módulos**: Sistema transversal (todos os módulos)

**Ver também**: CHANGE_POLICY.md, CI_CONTRACT_GATES.md

---

### Invariante (`invariant`)
**Definição**: Regra de negócio imutável que deve ser sempre verdadeira no sistema, independentemente de operação, estado ou ator. Invariantes não têm exceções — se uma exceção é necessária, a invariante estava mal definida.

**Contexto**: Vivem no contrato antes do código. São documentadas em `docs/hbtrack/modulos/<module>/INVARIANTS_<MOD>.md` por módulo. Classificadas por camada: A (DB constraint), B (trigger), C1 (service puro), C2 (service+DB), D (router/RBAC), E (workers), F (OpenAPI).

**Módulos**: Sistema transversal

**Ver também**: CONTRACT_SYSTEM_RULES.md

---

### SSOT — Single Source of Truth (`ssot`)
**Definição**: Arquivo ou localização que é a única fonte de verdade para um artefato específico. Duplicação de informação canônica é proibida — toda referência aponta para o SSOT.

**Contexto**: Princípio fundamental do sistema contract-driven do HB Track. Exemplos: `contracts/openapi/openapi.yaml` é a fonte primária da superfície HTTP; `contracts/openapi/paths/<module>.yaml` contém a superfície pública por módulo; este glossário é o SSOT dos termos de domínio. Modificar uma cópia sem atualizar o SSOT é uma violação.

**Módulos**: Sistema transversal

**Ver também**: CONTRACT_SYSTEM_RULES.md, CONTRACT_SYSTEM_LAYOUT.md

---

### Contrato (`contract`)
**Definição**: Artefato normativo (OpenAPI spec, schema JSON, invariante, DB contract, UI contract) que governa uma interface ou comportamento de forma vinculante. O contrato é a lei — implementação que o viola é um bug.

**Contexto**: No HB Track, "contrato" tem sentido amplo: inclui OpenAPI, AsyncAPI, invariantes, DB contracts, UI contracts, workflows Arazzo. Todos devem ser aprovados antes da implementação correspondente.

**Módulos**: Sistema transversal

**Ver também**: SSOT, invariante, API_CONVENTIONS.md, CI_CONTRACT_GATES.md

---

## 4. Termos de Referência Rápida (IHF/Handebol)

Ver `HANDBALL_RULES_DOMAIN.md §5` para tabela completa de terminologia IHF (inglês → PT-BR → código HBR → módulos afetados).

Referências rápidas:
| Código | Termo PT-BR | Definição resumida |
|--------|-------------|-------------------|
| HBR-002 | Time-out | 1 por tempo, solicitado pela equipe |
| HBR-003 | Exclusão | Suspensão de 2 minutos |
| HBR-005 | Tiro de 7m | Penalti do handebol |
| HBR-006 | Tiro livre | Reposição por infração |
| HBR-007 | Substituição | Troca sem parada de jogo |
| HBR-008 | Composição em quadra | Máx. 7 jogadores simultâneos |
| HBR-010 | Área de gol | Semicírculo de 6m exclusivo ao goleiro |

---

## 5. Atualizando o Glossário

Para adicionar um termo:
1. Verificar se não existe entrada similar (buscar sinônimos e traduções)
2. Seguir o formato da seção §3 (definição + contexto + módulos + ver também)
3. Abrir PR do tipo `documentation-only` se mudança for isolada
4. Garantir consistência com `SYSTEM_SCOPE.md`, `HANDBALL_RULES_DOMAIN.md` e contratos de módulo
5. Se o termo afeta código (field name, enum value, table name), a mudança pode ser breaking change — ver `CHANGE_POLICY.md §4`
