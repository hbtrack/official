# HB Track — Escopo por Fase: MVP, V2 e V3
> Fonte: `_archive/chat.md` (seção 4 + PRD) | Versão: 1.0.0 | 2026-03-18
> Documento de apoio humano, não canônico e não soberano. Serve para estudo e exploração de escopo; não substitui `docs/_canon/`, `ROADMAP.md` ou o registry de módulos.

---

## Regra de uso

Antes de adicionar uma capacidade a um módulo, usar este material apenas como referência exploratória.
O escopo operacional vigente deve ser decidido pelo canon ativo e pelos artefatos de roadmap já promovidos.

---

## Mapeamento: módulos do produto → módulos do registry

A visão de produto descreve 20 módulos funcionais. Os 16 módulos canônicos do registry cobrem
a maioria deles. O mapeamento abaixo é a referência para saber onde cada capacidade deve ser contratada.

| Módulo do produto (chat.md) | Módulo canônico (registry) | Fase | Observação |
|---|---|---|---|
| Core Platform (auth, authz, multi-tenant, auditoria, notificações) | `identity_access` + `audit` + `notifications` | MVP | Três módulos separados no registry |
| Master Data Management (atletas, equipes, temporadas, competições) | `users` + `teams` + `seasons` + `competitions` | MVP | Quatro módulos separados no registry |
| Training Planning & Session Management | `training` | MVP | ✅ `implementation_ready` |
| Video Capture & Media Processing | **sem módulo no registry** | MVP | ⚠️ Gap: `video` precisa ser criado |
| Video Analysis & Tagging | **sem módulo no registry** | MVP | ⚠️ Gap: coberto pelo mesmo `video` |
| Handball Event Scouting | `scout` | MVP | Stub — inclui opponent + goalkeeper |
| Match Operations Center | `matches` | MVP | Stub |
| Opponent Intelligence | `scout` (sub-domínio) | MVP | Não é módulo separado no registry |
| Reporting & Workflow Automation | `reports` + `notifications` | MVP | Stub |
| Performance Tracking Engine (sensores) | **sem módulo no registry** | V2 | Novo módulo a criar em V2 |
| Athlete Monitoring & Readiness | `wellness` | V2 | Stub — escopo V2 |
| Medical & Recovery | `medical` | V2 | Stub — escopo V2 |
| Goalkeeper Intelligence | `scout` (sub-domínio) | V2 | Sub-domínio do scout |
| Advanced Analytics & BI | `analytics` | V2 | Stub |
| AI Insight Layer | `ai_ingestion` | V2 | Stub |
| Squad Management & Player Development | `training` (parcial) + `users` | V2 | Sem módulo dedicado; capacidades distribuídas |
| Competition & Federation Operations | `competitions` | V3 | Stub — escopo V3 |
| Media, Broadcast & Digital Products | **sem módulo no registry** | V3 | Novo módulo a criar em V3 |
| Data Platform (lakehouse, event store) | infraestrutura transversal | V2/V3 | Não é módulo de domínio; é infra |
| API & Extensibility Layer | infraestrutura transversal | V2/V3 | Não é módulo de domínio; é infra |

---

## MVP — O que está no escopo

**Objetivo:** provar que um clube consegue trocar 3–4 ferramentas por uma só.

**Critério de validação do MVP:**
- Um clube consegue trocar 3–4 ferramentas por uma só
- O analista reduz retrabalho operacional
- O treinador ganha velocidade de decisão e qualidade de preparação

### Módulos e capacidades incluídos

| Módulo | Capacidades MVP |
|---|---|
| `identity_access` | Login, autenticação, autorização, multi-tenant básico, perfis principais |
| `users` | Cadastro de atletas e staff; elenco por temporada |
| `teams` | Cadastro de equipes e categorias |
| `seasons` | Temporadas, competições básicas |
| `training` | Microciclos, sessões, objetivos, presença, observações — ✅ implementation_ready |
| `video` ⚠️ | Upload, biblioteca, organização, sincronização temporal, clipes manuais, streaming interno |
| `scout` | Tagging manual, templates de handebol, playlists, eventos ofensivos/defensivos/transição, superioridade, goleiro |
| `matches` | Console live básico, cronologia, dashboards simples ao vivo, consolidação pós-jogo |
| `reports` | Relatório pós-jogo, relatório individual simples, dossiê pré-jogo, export PDF |
| `notifications` | Distribuição básica de material ao staff |
| `audit` | Trilha de auditoria básica |

### Personas atendidas no MVP

Primárias: treinador principal, auxiliar técnico, analista de desempenho, analista de vídeo, scout.
Secundária: diretor esportivo (visão executiva leve), atleta (recebe vídeo/feedback — passivo).

### Os 4 fluxos centrais do MVP

**Fluxo 1 — Pós-jogo**
subir vídeo → marcar eventos → associar tags → gerar relatório → montar playlists → distribuir ao staff

**Fluxo 2 — Preparação de adversário**
acessar jogos anteriores → identificar padrões → montar recortes → produzir dossiê técnico

**Fluxo 3 — Semana de treino**
registrar microciclo → documentar sessões → associar objetivos → usar aprendizados do jogo anterior

**Fluxo 4 — Operação ao vivo**
registrar eventos durante a partida → acompanhar indicadores → revisar lances no intervalo

### KPIs do MVP

- Tempo para análise pós-jogo
- Tempo para montar dossiê de adversário
- Número de ferramentas substituídas
- Frequência de uso por treinador e analista
- Taxa de adoção por comissão técnica

---

## V2 — O que está no escopo

**Objetivo:** unificar a camada de alto rendimento — conectar tática, vídeo, físico e inteligência.

| Módulo | Capacidades V2 |
|---|---|
| `wellness` | Carga aguda/crônica, prontidão, readiness, alertas de fadiga, carga planejada vs realizada |
| `medical` | Status médico-funcional, indisponibilidade, restrições, timeline de retorno, prontuário funcional |
| `analytics` | KPIs avançados, eficiência por posse, análise contextual, comparação por lineup, benchmarking interno |
| `ai_ingestion` | Sumarização automática, sugestão de clipes, padrões frequentes, busca semântica básica |
| `scout` (expandido) | Goalkeeper Intelligence: mapas por zona, 7m, contra-ataque; análise de tendência de arremessadores |
| `reports` (expandido) | Distribuição automática, alertas operacionais, playlists automáticas pós-jogo |
| `tracking` ⚠️ | Novo módulo: ingestão de sensores, tracking de atletas indoor, heatmaps, séries temporais físicas |

**Personas ampliadas:** preparador físico, fisiologista, fisioterapeuta, médico (camada funcional), coordenador técnico, coordenador de base.

**Perguntas que a V2 responde:**
- A queda ofensiva no 2º tempo foi tática ou física?
- Quais atletas estão em risco de sobrecarga?
- Qual a relação entre microciclo planejado e resposta competitiva?
- Como o goleiro performa por zona e tipo de finalização?

### KPIs da V2

- Aderência do staff físico e médico
- Redução de retrabalho entre áreas
- Volume de alertas acionáveis
- Correlação entre planejamento e execução capturada

---

## V3 — O que está no escopo

**Objetivo:** transformar o HB Track em infraestrutura do ecossistema do handebol.

| Módulo | Capacidades V3 |
|---|---|
| `competitions` (expandido) | Operação de competição, live stats oficiais, homologação, rankings, portal de competição |
| `media` ⚠️ | Novo módulo: widgets, overlays, feeds de dados, APIs públicas/privadas, minisites, highlights automáticos, pacotes para broadcast |
| `analytics` (expandido) | Benchmarking cross-competition, scouting de talento, recrutamento, análise de evolução de mercado |
| `ai_ingestion` (expandido) | Classificação automática por visão computacional, modelos preditivos, copiloto em linguagem natural |
| Academy / Talent Pipeline | Acompanhamento longitudinal de base, benchmarks etários, detecção de talento (sub-domínio de `users`/`training`) |

**Novos mercados:** federações nacionais, ligas profissionais, centros de formação, broadcasters, plataformas digitais.

### KPIs da V3

- Número de competições operadas
- Volume de dados distribuídos via API
- Adoção por federações e ligas
- Audiência e consumo de produto digital

---

## Gaps críticos de módulo

Dois módulos descritos no produto não existem ainda no registry:

| Módulo ausente | Fase necessária | Impacto |
|---|---|---|
| `video` | **MVP** — bloqueante | Os 4 fluxos centrais do MVP dependem de vídeo. Sem esse módulo no registry, o MVP não pode ser desenvolvido completo. |
| `tracking` | V2 | Necessário para conectar físico + tático. Não bloqueia MVP. |
| `media` | V3 | Necessário para distribuição institucional. Não bloqueia MVP nem V2. |

**Ação requerida:** decidir quando adicionar `video` ao `MODULE_REGISTRY.yaml` antes de iniciar o sprint de MVP.

---

## O que está fora do MVP (não contratar agora)

- Tracking por sensores e bola em tempo real
- Monitoramento físico avançado (carga aguda/crônica)
- Módulo médico completo
- IA generativa avançada
- Benchmarking de liga em grande escala
- Portal público de competição
- APIs externas robustas
- Live stats para mídia
- Clipping automático por visão computacional
- xG avançado

---

## Referência completa

Documento de origem: [`_archive/chat.md`](../../_archive/chat.md) (seções 4 e PRD)
Módulos canônicos: [`docs/_canon/MODULE_REGISTRY.yaml`](../_canon/MODULE_REGISTRY.yaml)
Visão de produto: [`docs/guias/PRODUCT_VISION.md`](PRODUCT_VISION.md)
