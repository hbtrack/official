## Protocolo de Benchmark Competitivo — HB Track

**Propósito**: padronizar como o agente ancora decisões de produto em padrões de mercado consolidados antes de apresentar opções ao humano.

**Ativação**: obrigatória em qualquer worker que apresente decisões de design ao humano — UI, API, eventos, ou arquitetura.

---

### Mapa de Mercado por Domínio

| Domínio do módulo | Plataformas de referência (geral) |
|---|---|
| Treinamento / performance (`training`, `wellness`, `medical`) | XPS Network, KINEXON Sports, Catapult Sports, Wimu/Firstbeat, Coach Logic, Metrifit, Teamworks |
| Competição / scouting (`competitions`, `matches`, `scout`) | Handball.ai, InStat, Nacsport, Dartfish, Klipsdraw, Sporttotal.tv/Yes Tech |
| Gestão e acesso (`users`, `teams`, `seasons`, `identity_access`) | XPS Network, Sportserv, Engage Sports, Sport80, LeagueApps |
| Transversal (`analytics`, `reports`, `notifications`, `audit`, `ai_ingestion`) | KINEXON Sports (dados em tempo real), Handball.ai (IA/métricas), Amplitude, Tableau |

---

### Benchmark Específico — Handebol Europeu

Referências obrigatórias quando o módulo tiver gatilho esportivo ativo (ver `DECISION_POLICY.md §6`). O agente deve citar estas plataformas pelo nome ao embasar decisões.

| Plataforma | País/Origem | Especialidade | Relevância para HB Track |
|---|---|---|---|
| **XPS Network** | Internacional | Plataforma de gestão de treinamento usada por técnicos e atletas de seleções nacionais de handebol | Referência de workflow coach-atleta, planejamento de temporada e comunicação de treinos |
| **KINEXON Sports** | Alemanha | Líder em rastreamento de jogadores por LPS; fornece a iBall oficial para EHF e Bundesliga (velocidade de arremesso, posição, força) | SSOT para dados de movimento indoor; padrão de precisão centimétrica sem GPS |
| **Handball.ai** | Espanha/Global | Análise de dados por IA focada em métricas avançadas de desempenho para técnicos e olheiros | Referência de produto de analytics orientado a handebol — como exibir KPIs específicos do esporte |
| **SELECT Sport** | Dinamarca/Alemanha | Fabricante oficial da bola de handebol; parceira da KINEXON na SELECT Ultimate iBall (dados em tempo real) | Referência de integração hardware-software para coleta de dados da bola |
| **Catapult Sports** | Austrália/Europa | Wearables (GPS/IMU) e análise de vídeo tático para equipes de elite; integra carga de trabalho + vídeo | Referência de fusão de dados fisiológicos com vídeo — padrão para módulos `wellness` e `training` |
| **Nacsport** | Espanha | Análise de vídeo tático ao vivo e pós-jogo com tagging em tempo real; amplamente usado por clubes europeus | Padrão de UX para marcação de lances e categorização tática |
| **InStat** | Espanha/Global | Scouting e estatísticas detalhadas; análise técnica de adversários e avaliação individual | Referência para modelo de dados de scouting e profundidade de métricas por atleta |
| **Dartfish** | Suíça | Análise de vídeo com marcação, análise tática e feedback em tempo real para treinadores | Padrão para ferramentas de feedback visual de técnicos |
| **Wimu / Firstbeat** | Europa | Monitoramento físico indoor (LPS) e carga fisiológica; Wimu da RealTrack Systems | Referência para rastreamento indoor e indicadores de recuperação/esforço |
| **Klipsdraw** | Espanha | Telestração (desenho sobre vídeo) e análise tática; frequentemente integrada com Nacsport | Referência para ferramentas de comunicação tática técnico-jogador |
| **Sporttotal.tv / Yes Tech** | Alemanha | Transmissão automática de jogos e painéis LED/placar; visibilidade de ligas menores + análise de vídeo automatizada | Referência para contexto de visibilidade e integração com transmissões ao vivo |

#### Tendências Europeias que o Benchmark Deve Considerar

- **Dados ao vivo em transmissões**: KINEXON permite exibir velocidade de arremesso e tempo de salto em tempo real durante jogos da EHF EURO — decisões de UI/eventos devem considerar esse nível de latência e exibição.
- **Análise de goleiros**: as plataformas líderes priorizam métricas de eficiência defensiva e posicionamento de bola como KPIs de primeira classe — não como subtópico.
- **LPS em vez de GPS**: ambientes indoor requerem Local Positioning Systems (precisão centimétrica) — qualquer módulo de rastreamento físico deve assumir LPS como padrão, não GPS.

---

### Procedimento padrão (executar antes de apresentar qualquer decisão)

1. Identificar o domínio do módulo na tabela acima.
2. Para a decisão em análise, determinar:
   - **Padrão dominante**: o que a maioria das plataformas líderes faz e por quê está consolidado.
   - **Lacuna de mercado**: o que nenhuma líder resolve bem ou que poucas endereçam.
3. Estruturar as opções no formato abaixo.
4. A recomendação deve sempre favorecer diferenciação sobre paridade.

---

### Formato obrigatório de apresentação ao humano

```
📊 O que o mercado faz hoje:
[Padrão dominante nas plataformas líderes, em linguagem de produto — 2-3 linhas]

🎯 3 caminhos para o HB Track:
A) Seguir o mercado — [o que as líderes fazem; por que funciona; risco de paridade]
B) Evoluir o padrão — [versão melhorada do padrão de mercado; diferencial incremental]
C) Superar o mercado — [decisão que as líderes ainda não tomaram; resolve o problema de forma superior]

⭐ Recomendação: [opção A/B/C] — [motivo em linguagem de produto, conectado ao que as líderes NÃO oferecem]
```

---

### Critérios de qualidade

- A análise deve ser específica para o domínio do módulo — nunca genérica.
- O benchmark deve ser citado explicitamente ("Catapult faz X porque…", "Wyscout não resolve Y porque…").
- Nunca recomendar paridade se existir caminho real de diferenciação.
- Para decisões de alto impacto (arquitetura, modelo de dados principal), acionar também `decision_discovery.prompt.md`.

---

### Adaptações por Tipo de Contrato

Cada worker aplica o protocolo com foco diferente. Ler a seção correspondente ao contexto antes de executar o procedimento:

| Worker | Foco do benchmark |
|--------|------------------|
| `decision_discovery` | Padrões de arquitetura de sistemas: estrutura de dados, estratégias de autenticação, comunicação entre módulos, modelos de permissão, estratégias de consistência/cache. |
| `create_asyncapi_contract` | Granularidade de eventos (fino vs. grosso), topologia de canais (fan-out vs. direto), estratégias de payload (envelope completo vs. referência), nomenclatura de eventos, sequenciamento de sagas. |
| `create_openapi_contract` | Granularidade de recursos, estratégias de filtro e busca, convenções de nomenclatura, estrutura de resposta. **Ativar somente quando `api_rules.yaml` não cobre a decisão** — a maior parte do design é determinística via regras. |
| `create_ui_contract` | Padrões de navegação, fluxos de interação, organização de informação, experiências diferenciadas. *(Protocolo embutido inline no worker — não duplicar aqui.)* |

---

### Rastreabilidade

Toda decisão tomada com base neste protocolo deve ser registrada com o campo `benchmark_basis` no artefato de saída, contendo:
- qual opção foi escolhida (A/B/C)
- qual plataforma de referência embasou a análise
