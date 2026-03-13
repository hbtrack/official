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

## 4. Atores Canônicos

Os 5 papéis abaixo são os únicos reconhecidos pelo sistema de permissões (RBAC). Toda variação de papel deve ser mapeada a um destes.

| Ator | Nível RBAC | Responsabilidade Principal |
|------|-----------|---------------------------|
| **Dirigente** | 1 (mais alto) | Gestão estratégica do clube: temporadas, equipes, usuários, relatórios executivos |
| **Coordenador** | 2 | Coordenação de comissão técnica, aprovação de planos de treino, gestão de atletas |
| **Treinador** | 3 | Planejamento e execução de treinos, gestão de sessões, análise de desempenho |
| **Atleta** | 4 | Visualização de próprios dados: treinos, wellness, histórico de partidas |
| **Membro** | 5 (mais baixo) | Acesso básico ao sistema — papel base para funções de suporte operacional |

**Regra**: Nenhum novo papel pode ser criado sem aprovação formal e atualização deste documento. Variações como "preparador físico" ou "analista" são mapeadas ao papel mais próximo e suas permissões adicionais são concedidas explicitamente via módulo `identity_access`.

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
- **Transmissão e streaming ao vivo de partidas**: captura, codificação e distribuição de vídeo em tempo real.
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

## 9. Decisões em Aberto

1. **Estratégia de versioning para breaking changes pós-v1**: o HB Track proíbe versão na URI e prevê compatibilidade via content negotiation / media-type quando necessário (SSOT: `.contract_driven/templates/api/api_rules.yaml`), mas a política de deprecação e ciclo de vida de versões antigas ainda não foi formalizada para o contexto de produção pós-v1.

2. **Broker externo (ex: RabbitMQ) quando a escala exigir**: atualmente o Celery usa Redis como broker. A decisão de migrar para um broker dedicado (RabbitMQ, Amazon SQS) está em aberto e depende de métricas de volume de mensagens em produção.

## 10. Princípios de Escopo

O HB Track opera sob 5 princípios que definem como o escopo deve ser interpretado e aplicado:

1. **Contrato antes da implementação** — nenhuma interface pública, shape estável, evento, workflow multi-step ou regra operacional relevante deve nascer primeiro no código.

2. **Contrato como fonte de verdade** — o sistema é governado por contratos técnicos e documentação normativa, não por inferência do agente nem por conveniência da implementação.

3. **Domínio esportivo explícito** — toda regra derivada do handebol que impacte produto deve estar ancorada em `HANDBALL_RULES_DOMAIN.md`.

4. **Escopo finito e taxonomia fechada** — o universo do sistema é limitado aos 16 módulos canônicos aprovados. Criação de módulos fora dessa lista requer decisão formal.

5. **Bloqueio em caso de lacuna crítica** — quando faltar artefato normativo necessário, o processo deve bloquear em vez de improvisar.

## 11. Critério de Aderência

O HB Track está aderente a este documento quando:

- Seus módulos reais pertencem à taxonomia canônica dos 16 módulos
- Seus contratos refletem apenas superfícies dentro do escopo definido
- Sua implementação não extrapola os limites das seções 5 e 6 deste documento
- Suas regras derivadas do handebol estão formalmente registradas em `HANDBALL_RULES_DOMAIN.md`
- Seus agentes de IA operam sem inventar domínio, módulo ou interface fora deste documento

## 12. Referências

- `ARCHITECTURE.md` — stack, princípios e estrutura de camadas
- `MODULE_MAP.md` — taxonomia técnica dos 16 módulos canônicos
- `HANDBALL_RULES_DOMAIN.md` — regras IHF documentadas (HBR-001..HBR-014)
- `.contract_driven/CONTRACT_SYSTEM_RULES.md` — regras operacionais do sistema CDD
- `.contract_driven/CONTRACT_SYSTEM_LAYOUT.md` — estrutura canônica de arquivos
