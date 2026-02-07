# PRD_REVIEW — Analise e Recomendacoes para o PRD HB Track

> Revisao tecnica do `docs/Hb Track/PRD_HB_TRACK.md` (v2.0, 07/02/2026).
> Objetivo: identificar lacunas, oportunidades de melhoria e proximos passos.

---

## 1. Score Geral

| Criterio | Nota | Comentario |
|----------|------|------------|
| Clareza do Problema | 10/10 | Dor real, quantificada, com personas especificas |
| Escopo e Priorizacao | 9/10 | MoSCoW claro, falta matriz de priorizacao V1.1 |
| Requisitos Funcionais | 10/10 | User stories bem escritas, criterios de aceitacao tecnicos |
| Modelo de Dados | 9/10 | Conceitual claro, falta normalizacao de alguns campos |
| Nao Funcionais | 8/10 | Bom, faltam SLAs de uptime/suporte |
| Seguranca e LGPD | 10/10 | Excelente cobertura, RACI definido, auditoria completa |
| Riscos e Mitigacoes | 9/10 | Bem categorizados, faltam riscos de mercado (concorrencia) |
| IA e Futuro | 7/10 | Visao ambiciosa, falta analise de viabilidade tecnica/custo |
| Go-to-Market | 5/10 | Ausente: modelo de negocio, pricing, CAC/LTV, canais |

**Score Total: 8.6/10** — Excelente PRD, pronto para desenvolvimento com ajustes menores.

---

## 2. Pontos Fortes

### 2.1 Estrutura e Organizacao
- PRD bem formatado com secoes logicas e numeradas
- Historico de versoes e controle de status claro
- Glossario tecnico detalhado (essencial para onboarding)
- Sistema de emojis para status torna leitura visual

### 2.2 Contexto de Negocio
- Dor real identificada: 60-70% do tempo em burocracia vs. 30-40% em tatica
- Impacto quantificado: reducao de 50% em tarefas administrativas
- Problema definido com evidencias concretas (8-12h de edicao de video)

### 2.3 Personas
- 4 personas primarias com dores especificas e stack tecnologico
- Detalhamento de necessidades tecnicas (ex: "internet instavel", "Smartphone Android")
- Personas secundarias identificadas para futuro (pais, preparadores fisicos)

### 2.4 Roadmap
- Faseamento claro: V1.0 (concluido) -> V1.1 (em desenvolvimento) -> V2.0+ (planejado)
- Priorizacao MoSCoW implicita (In Scope / Out Scope)
- Criterios de sucesso por fase com KPIs mensuraveis

### 2.5 Seguranca e Compliance
- Secao dedicada a LGPD com requisitos especificos
- Matriz RACI de responsabilidades
- Plano de auditoria e logs imutaveis

### 2.6 Gestao de Riscos
- Riscos categorizados: tecnicos, negocio, legais, IA
- Probabilidade + Impacto + Mitigacao para cada risco
- Suposicoes criticas com plano B

---

## 3. Lacunas Identificadas

### 3.1 Metricas de Sucesso (Secao 14) — Faltam Baselines

As metas estao definidas mas faltam baselines quantitativos:

| Atual | Recomendado |
|-------|-------------|
| "Taxa de adocao entre treinadores" | "Taxa de adocao: 75% em 3 meses (baseline: 0%)" |
| "Reducao de tempo em tarefas administrativas" | "De 60% para 30% em 6 meses" |

### 3.2 SLAs Ausentes (Secao 10)

Secao 10 lista RNFs mas falta Service Level Agreements formais:
- Uptime: 99.5% (permite 3.6h downtime/mes)
- Janela de manutencao: Domingos 2h-4h
- Tempo de primeira resposta (suporte): < 4h (horario comercial)
- Resolucao de bugs criticos: < 24h

### 3.3 Priorizacao V1.1 Sem Criterios

V1.1 tem 5 features em desenvolvimento sem ordem de prioridade:
- Nao esta claro qual sera entregue primeiro
- Falta analise de impacto nos KPIs
- Dependencias tecnicas entre features nao documentadas

**Recomendacao**: Adicionar matriz de priorizacao:

| Feature V1.1 | Valor Negocio | Esforco | Risco | Prioridade |
|--------------|--------------|---------|-------|------------|
| Scout de Jogo | Alto (diferencial) | Medio | Baixo | P0 |
| Notificacoes | Alto (retencao) | Baixo | Medio | P0 |
| Relatorios PDF | Medio | Baixo | Baixo | P1 |
| Banco de Exercicios | Medio | Baixo | Baixo | P1 |
| Competicoes | Alto | Alto | Medio | P1 |

### 3.4 Viabilidade IA (Secao 16)

Features de IA sao ambiciosas mas faltam:
- Estimativa de custos de infra (GPUs, APIs OpenAI/AWS)
- Analise de build vs. buy (usar SaaS existente como Hudl?)
- Proof of Concept planejado com criterios de go/no-go

### 3.5 Modelo de Negocio Ausente

Nao esta claro o modelo de monetizacao:
- Freemium? Assinatura por clube? Por usuario?
- Preco diferenciado por categoria (base vs. profissional)?
- Trial gratuito?

### 3.6 Onboarding de Usuarios

Como os usuarios serao onboardados?
- Tutorial interativo na primeira sessao?
- Webinar de treinamento para treinadores?
- Documentacao/videos de ajuda?

---

## 4. Recomendacoes Estrategicas

### 4.1 Secao 18: Modelo de Negocio (NOVA)

**Sugestao de estrutura de pricing**:
- Plano Starter (Gratuito): 1 equipe, ate 15 atletas, features basicas
- Plano Pro (R$ 99/mes): 5 equipes, wellness, relatorios PDF
- Plano Enterprise (sob consulta): Ilimitado, scout, API, suporte dedicado

**Unit economics estimados**:
- CAC via campeonatos regionais: ~R$ 200/clube
- CAC via Google Ads: ~R$ 350/clube
- CAC via indicacao: ~R$ 50/clube
- LTV (Pro): R$ 99 x 18 meses = R$ 1.782
- LTV/CAC > 3:1 (saudavel)

### 4.2 Secao 19: Go-to-Market (NOVA)

| Fase | Periodo | Estrategia | Objetivo |
|------|---------|-----------|----------|
| Early Adopters | Q1/2026 | Piloto com 3 clubes parceiros (gratuito por feedback) | 90% satisfacao + 3 depoimentos |
| Expansao Regional | Q2/2026 | Campeonatos estaduais (SP, RJ, MG) + workshops | 10 clubes pagantes |
| Nacional | Q3/2026 | Parcerias CBHb + federacoes | 50 clubes pagantes |

### 4.3 Integracao Hibrida WhatsApp (V1.2)

Mitigar risco de resistencia ao abandono do WhatsApp:
- Enviar alertas do sistema via WhatsApp (Twilio/MessageBird)
- Comando `/hbtrack` para consultar dados sem sair do WhatsApp
- Reducao de atrito de adocao sem comprometer o valor da plataforma

### 4.4 PoC de IA (V2)

Antes de investir em IA de video, validar viabilidade:
- PoC com 5 videos de jogos reais
- Custo estimado de processamento por video
- Precisao minima aceitavel (>85%)
- Criterio de go/no-go: custo < R$ 10/video E precisao > 85%

---

## 5. Proximos Passos

### Curto Prazo (esta semana)
1. Adicionar Secao 18 "Modelo de Negocio" ao PRD
2. Adicionar Secao 19 "Go-to-Market" ao PRD
3. Definir SLAs na Secao 10 (uptime, suporte)
4. Criar matriz de priorizacao para V1.1

### Medio Prazo (proximo sprint)
5. Planejar PoC de IA de video (custo vs. beneficio)
6. Definir plano de UAT (testes com usuarios reais)

### Longo Prazo (Q2/2026)
7. Criar documento separado `GTM_STRATEGY.md`
8. Analise competitiva (Hudl, TeamSnap, etc.)
9. Roadmap de parcerias (CBHb, federacoes estaduais)

---

> Fonte: Analise baseada em `PRD_HB_TRACK.md` v2.0 e codigo-fonte do backend.
