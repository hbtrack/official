---
doc_type: canon
version: "1.0.0"
last_reviewed: "2026-03-11"
status: active
---

# Escopo do Sistema — HB Track

## 1. Missão

O HB Track tem como missão suportar operações, gestão, treinamento, jogos, competições e analytics de handebol através de contratos fortes e documentação normativa viva.

O sistema existe para transformar regras do domínio do handebol e necessidades operacionais do produto em contratos verificáveis, implementação auditável e evolução controlada — com ou sem participação de agentes de IA.

## 2. Tipo de Sistema

Plataforma sports-tech de gestão de handebol — **monólito modular em camadas** (FastAPI) com SPA (Next.js 13+), dados relacionais (PostgreSQL) e workers assíncronos (Celery + Redis).

O sistema não é um microserviço. A modularidade é lógica (por domínio), não física (por deploy independente). Boundaries entre módulos são explícitos e governados por contratos internos; não por chamadas de rede.

## 3. Mercado Primário

**Handebol indoor — Brasil.**

Regras, terminologia, categorias e estrutura competitiva seguem o regulamento IHF (International Handball Federation) e suas adaptações pela Confederação Brasileira de Handebol (CBHb) quando aplicável.

## 4. Atores Canônicos e Modelo de Autorização

O sistema de identidade e autorização do HB Track opera em quatro camadas. A SSOT completa está em `docs/guias/IDENTITY_RBAC.md`.

```
Canonical Actor  →  Role Template  →  Permission Bundles  →  Scope Bindings  →  Policy Engine
```

- **Ator Canônico**: linguagem de negócio — quem usa o sistema e para qual finalidade (ex: Head Coach, Team Doctor, Performance Analyst)
- **Role Template**: perfil provisionável e auditável, composto por bundles (ex: `HEAD_COACH`, `TEAM_DOCTOR`)
- **Permission Bundles**: capacidades reutilizáveis por domínio (ex: `training_plan_manage_bundle`, `medical_record_manage_bundle`)
- **Scope Bindings**: escopos de aplicação — clube, equipe, temporada
- **Policy Engine**: restrições contextuais ABAC (ex: treinador vê readiness mas não diagnóstico clínico)

### Famílias de atores (resumo)

| Família | Atores canônicos |
|---------|-----------------|
| Plataforma | Platform Super Admin, Tenant Admin |
| Gestão esportiva | Executive Stakeholder, Sporting Director, Technical Coordinator |
| Comissão técnica | Head Coach, Assistant Coach, Performance Analyst, Video Analyst, Opponent Scout, Goalkeeper Coach |
| Performance e saúde | Strength & Conditioning Coach, Performance Scientist, Physiotherapist, Team Doctor, Nutritionist |
| Operação e competição | Match Operator, Competition Official, Referee-Linked Official |
| Ecossistema e mídia | Federation Operator, League Admin, Media Operator, External Partner |
| Atletas | Athlete, Academy Athlete Guardian Proxy |

**Total**: ~25 atores canônicos → ~30 permission bundles → ~20 role templates

**Regra**: Nenhum role template pode ser criado sem aprovação formal e registro em `docs/guias/IDENTITY_RBAC.md`. Variações de acesso entre tenants são resolvidas por composição de bundles, nunca por criação de novos roles ad hoc. Ver IDENTITY_RBAC.md §5 para a regra arquitetural completa.

## 5. Macrodomínios de Negócio

Os 9 macrodomínios abaixo organizam o negócio do HB Track. Macrodomínios de negócio ≠ módulos técnicos. Ver `MODULE_MAP.md` para a taxonomia técnica dos 16 módulos canônicos.

| Macrodomínio | Descrição |
|-------------|-----------|
| **Atletas** | Cadastro, perfil, posição, histórico, vínculo com equipes e temporadas |
| **Equipes** | Composição de elenco, categorias, configuração por temporada |
| **Treinos** | Planejamento de sessões, execução, feedback, wellness pós-treino, periodização |
| **Jogos** | Registro de partidas, composição de súmula, timeline de eventos, resultado |
| **Competições** | Fases competitivas, tabelas, chaveamentos, classificação e pontuação |
| **Analytics** | Métricas de desempenho, KPIs individuais e coletivos, dashboards, exportações |
| **Usuários e Permissões** | Identidade, autenticação, autorização, RBAC, sessão, tokens |
| **Comunicação** | Notificações internas, alertas de sistema, push e email via serviço externo |
| **Arquivos e Relatórios** | Relatórios gerados, exportações PDF/CSV, ingestão de mídia e IA |

## 6. Fora do Escopo

Os itens abaixo estão explicitamente fora do escopo do HB Track. Qualquer implementação que toque nesses domínios requer decisão formal antes de avançar.

- **Arbitragem oficial de partidas**: gestão de árbitros, credenciamento, escalações de arbitragem e comunicação com federações.
- **Broadcast e OTT público como domínio de negócio autônomo** (V3 / módulo `media`): plataforma de streaming pago, app OTT dedicado ao consumidor, widget público de estatísticas para portais externos, highlight pack para TV ou conteúdo de mídia como produto digital independente do sistema esportivo. Esses domínios requerem criação do módulo `media` no registry e decisão formal antes de avançar.

  > **Distinção crítica:** captura técnica de vídeo na arena, biblioteca interna de partidas, clipping manual, sincronização temporal e distribuição restrita a comissão técnica, banco e tribuna **estão dentro do escopo** — são responsabilidade do módulo `video` (MVP). O que está fora do escopo é o broadcast público como domínio de produto autônomo (plataforma OTT, CDN de consumidor, monetização de audiência).


- **Venda de ingressos e bilheteria**: e-commerce, pagamentos, emissão de ingressos e controle de acesso físico a eventos.

Funcionalidades adjacentes que se aproximem desses domínios devem ser avaliadas individualmente com clareza sobre onde o sistema termina e onde o sistema externo começa.

## 7. Dependências Externas

| Dependência | Integração | Módulo responsável |
|-------------|-----------|-------------------|
| Serviço de notificação externo (email / push) | Integrado via adapter interno | `notifications` |
| Storage externo para arquivos e mídia | Integrado via adapter interno | `reports`, `ai_ingestion` |

O HB Track não controla implementação interna desses serviços. A integração é encapsulada no módulo responsável e não deve vazar para outros módulos.

## 8. Riscos Documentados

1. **Drift entre contrato e implementação sem CI gates ativos**: se os gates de validação contratual não estiverem rodando em CI, a implementação pode divergir silenciosamente dos contratos OpenAPI e schemas canônicos.

2. **Módulos sem test matrix bloqueiam desenvolvimento guiado por IA**: agentes de IA sem test matrix explícita para o módulo são forçados a inferir cobertura, o que aumenta risco de regressão e viola o princípio de contrato antes de implementação.

3. **Regras de handebol sem âncora documental causam inconsistência entre módulos**: regras esportivas presentes apenas no código ou na memória do desenvolvedor não são verificáveis por agentes e criam divergência entre módulos que compartilham semântica esportiva.

## 9. Módulo Video (Plataforma de Mídia Integrada)

O módulo `video` é responsável por captura ao vivo, ingestão, sincronização temporal com rastreamento/scouting, transcodificação, distribuição técnica interna (baixa latência) e distribuição pública/broadcast. Ver ADR-033 para decisão de canonicalization.

**Responsabilidades de video:**
- Captura na arena (edge-first, com fallback local)
- Ingestão de feeds externos (TV, produtora, múltiplos ângulos)
- Sincronização temporal (relógio lógico único da partida)
- Transcodificação para perfis técnicos e de distribuição pública
- Clipping automático e manual com índice semântico
- Distribuição restrita a técnico/banco/tribuna
- Distribuição pública via CDN (quando aplicável)

**Não cobre (out-of-scope dentro do video):**
- Broadcast e OTT como domínio de negócio autônomo (futuro módulo `media`)
- Edição editorial complexa de pós-produção
- CDN global de varejo
- Monetização OTT avançada de assinatura

## 10. Decisões em Aberto

1. **Estratégia de versioning para breaking changes pós-v1**: o HB Track proíbe versão na URI e prevê compatibilidade via content negotiation / media-type quando necessário (SSOT: `.contract_driven/templates/api/api_rules.yaml`), mas a política de deprecação e ciclo de vida de versões antigas ainda não foi formalizada para o contexto de produção pós-v1.

2. **Broker externo (ex: RabbitMQ) quando a escala exigir**: atualmente o Celery usa Redis como broker. A decisão de migrar para um broker dedicado (RabbitMQ, Amazon SQS) está em aberto e depende de métricas de volume de mensagens em produção.

## 11. Princípios de Escopo

O HB Track opera sob 5 princípios que definem como o escopo deve ser interpretado e aplicado:

1. **Contrato antes da implementação** — nenhuma interface pública, shape estável, evento, workflow multi-step ou regra operacional relevante deve nascer primeiro no código.

2. **Contrato como fonte de verdade** — o sistema é governado por contratos técnicos e documentação normativa, não por inferência do agente nem por conveniência da implementação.

3. **Domínio esportivo explícito** — toda regra derivada do handebol que impacte produto deve estar ancorada em `HANDBALL_RULES_DOMAIN.md`.

4. **Escopo finito e taxonomia fechada** — o universo do sistema é limitado aos 16 módulos canônicos aprovados. Criação de módulos fora dessa lista requer decisão formal.

5. **Bloqueio em caso de lacuna crítica** — quando faltar artefato normativo necessário, o processo deve bloquear em vez de improvisar.

## 12. Critério de Aderência

O HB Track está aderente a este documento quando:

- Seus módulos reais pertencem à taxonomia canônica dos 16 módulos
- Seus contratos refletem apenas superfícies dentro do escopo definido
- Sua implementação não extrapola os limites das seções 5 e 6 deste documento
- Suas regras derivadas do handebol estão formalmente registradas em `HANDBALL_RULES_DOMAIN.md`
- Seus agentes de IA operam sem inventar domínio, módulo ou interface fora deste documento

## 13. Referências

- `ARCHITECTURE.md` — stack, princípios e estrutura de camadas
- `MODULE_MAP.md` — taxonomia técnica dos 16 módulos canônicos
- `HANDBALL_RULES_DOMAIN.md` — regras IHF documentadas (HBR-001..HBR-014)
- `.contract_driven/CONTRACT_SYSTEM_RULES.md` — regras operacionais do sistema CDD
- `.contract_driven/CONTRACT_SYSTEM_LAYOUT.md` — estrutura canônica de arquivos
