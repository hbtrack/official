# HB Track — Visão de Produto
> Fonte: `_archive/chat.md` (conversa de produto original) | Versão: 1.0.0 | 2026-03-18
> Este documento é referência canônica de produto. Atualizar via ADR quando a visão mudar.

---

## O que é o HB Track

Plataforma unificada de sport tech para handebol. Consolida em um único sistema o que hoje está
fragmentado entre tracking, vídeo, scouting, analytics, athlete monitoring, operação de jogo,
gestão técnica, dados oficiais, mídia e competição.

**Problema central:** organizações de handebol operam múltiplos sistemas desconectados. Isso
gera duplicação de cadastro, reconciliação manual, perda de contexto entre treino/jogo/física/tática
e baixa velocidade de decisão.

**Proposta central:** uma única fonte de verdade para o handebol — do treino à competição, do
atleta à federação, do sensor ao insight.

---

## Posicionamento competitivo

Referência: mercado atual de sport tech para handebol (2026).

| Concorrente | Categoria | Ponto forte | Limitação relevante |
|---|---|---|---|
| KINEXON | Tracking atleta/bola | Parceiro EHF até 2028; elite | Não cobre vídeo, scouting ou operação |
| Handball.ai | Analytics e scouting | 6.500+ jogos/temporada; nativo handebol | Não cobre tracking físico, treino ou mídia |
| XPS Network / Sideline Sports | Workflow técnico | 20 anos; 30+ federações; parceiro EHF | Não cobre tracking de sensores ou IA avançada |
| Catapult | Wearables / athlete monitoring | Global; controle de carga e lesão | Não é handebol-first; não cobre vídeo/tático |
| Spiideo | Vídeo automatizado | Federação islandesa; captura automática | Não cobre tracking físico ou scouting tático |
| Steazzi | Estatística específica handebol | Acessível; semi-pro / amador | Sem performance, tracking ou vídeo avançado |
| Nacsport | Video analysis | Tagging maduro | Generalista; sem ecossistema integrado |
| Hudl | Ecossistema amplo vídeo/dados | 315k+ times; 40+ esportes | Não é handebol-first |
| Sportradar | Dados oficiais / APIs | 80+ ligas handebol; mídia/apostas | Não é ferramenta de clube ou comissão |
| STATSCORE | Data feeds / widgets | Cobertura digital ampla | Não é plataforma de performance ou análise |

**Diferencial do HB Track:** todos esses sistemas resolvem um problema. O HB Track resolve a
integração entre todos eles através de um modelo de dados único, um ID único de atleta/jogo/evento
e um fluxo operacional coeso.

---

## Proposta de valor por segmento

| Segmento | Dor principal | O que o HB Track resolve |
|---|---|---|
| Clubes / comissões técnicas | 4–6 ferramentas não conectadas | Um único fluxo: treino → jogo → vídeo → análise |
| Departamentos de alto rendimento | Dados de performance isolados de dados táticos | Convergência de físico + tático + vídeo + readiness |
| Federações e ligas | Estatística oficial frágil; distribuição manual | Operação de competição + live stats + APIs |
| Mídia e produto digital | Dependência de feeds externos caros | API nativa + widgets + highlights automáticos |

---

## Os cinco macroblocos funcionais

O produto opera em cinco camadas simultâneas:

1. **Captura** — sensores, vídeo, eventos de scouting, inputs de staff
2. **Processamento** — normalização, sincronização, enriquecimento, IA
3. **Inteligência** — dashboards, alertas, relatórios, predição, scouting de adversário
4. **Operação** — treino, jogo, staff, atletas, competição, mídia
5. **Distribuição** — apps, APIs, widgets, transmissões, relatórios, portais

---

## Pacotes comerciais

| Pacote | Fase | Conteúdo |
|---|---|---|
| **HB Track Coach** | MVP | Planejamento de treino, vídeo, scouting, relatórios, adversário |
| **HB Track Performance** | V2 | Tudo do Coach + tracking, readiness, carga, recovery, analytics avançado |
| **HB Track League** | V3 | Tudo do Performance + competição, live stats, mídia, widgets, APIs, portal público |

---

## Princípios arquiteturais não negociáveis

Estes princípios foram definidos na concepção do produto e devem orientar decisões de contrato:

- **Domain-driven design** — cada módulo tem linguagem própria (bounded context)
- **Event-driven** — tracking, alertas e live stats dependem de propagação assíncrona
- **CQRS** em áreas de leitura intensiva (live stats, dashboards de jogo, analytics)
- **Event sourcing seletivo** — timeline de jogo, auditoria crítica, homologação oficial
- **Storage polyglot** — operação no transacional; telemetria no time-series; mídia no object storage; histórico no lakehouse
- **Modular monolith evolutivo** — começar com monólito bem particionado; extrair serviços para tracking, vídeo, ingestão e analytics sob demanda
- **Multi-tenant forte** — segregação desde o início; dados de um clube nunca vazam para outro

---

## Referência completa

Documento de origem: [`_archive/chat.md`](../../_archive/chat.md)
Módulos canônicos: [`docs/_canon/MODULE_REGISTRY.yaml`](../_canon/MODULE_REGISTRY.yaml)
Escopo por fase: [`docs/guias/MVP_SCOPE.md`](MVP_SCOPE.md)
Perfis de usuário: [`docs/guias/USER_PROFILES.md`](USER_PROFILES.md)
