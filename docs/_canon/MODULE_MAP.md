---
doc_type: canon
version: "1.0.0"
last_reviewed: "2026-03-11"
status: active
---

# Mapa de Módulos — HB Track

## 1. Nota de Taxonomia

Os macrodomínios de negócio (SYSTEM_SCOPE.md §5) são agrupamentos funcionais para comunicação com stakeholders. Os 16 módulos técnicos abaixo são a taxonomia canônica do sistema. Um macrodomínio pode cruzar múltiplos módulos.

**Regra fundamental**: se um módulo não estiver nesta lista, ele não existe no sistema sem decisão formal registrada em `docs/_canon/decisions/`.

---

## 2. Módulos Funcionais (13)

| Módulo | Responsabilidade | Dependências | API | UI | Workers | Eventos |
|--------|-----------------|--------------|-----|----|---------|---------|
| `users` | Perfis de usuário, preferências, dados cadastrais (sem auth) | `identity_access` | Sim | Sim | Não | `user.updated` |
| `seasons` | Temporadas, mesociclos, microciclos, configuração de período | Nenhuma | Sim | Sim | Não | `season.started`, `season.ended` |
| `teams` | Equipes, composição de elenco, categorias | `users`, `seasons` | Sim | Sim | Não | `team.composition.changed` |
| `training` | Sessões de treino, planos, exercícios em contexto tático | `teams`, `exercises`, `wellness` | Sim | Sim | Sim (Celery) | `session.created`, `session.completed` |
| `wellness` | Check-in diário de bem-estar, PSE pós-treino, carga de treino | `training`, `users` | Sim | Sim | Não | `wellness.submitted` |
| `medical` | Lesões, histórico médico, retorno ao jogo, prontuário esportivo | `users`, `teams` | Sim | Sim | Não | `injury.reported` |
| `competitions` | Torneios, fases, classificação, calendário competitivo | `teams`, `seasons` | Sim | Sim | Não | `competition.phase.started` |
| `matches` | Partidas, placar, eventos de jogo, súmula oficial | `competitions`, `teams` | Sim | Sim | Sim (Celery) | `match.started`, `match.ended`, `match.event` |
| `scout` | Análise tática, eventos detalhados de partida, estatísticas por jogador | `matches`, `teams` | Sim | Sim | Sim (Celery) | `scout.event` |
| `exercises` | Biblioteca de exercícios, categorias, mídia, metadados | Nenhuma | Sim | Sim | Não | Nenhum |
| `analytics` | Dashboards, métricas agregadas, relatórios dinâmicos, KPIs | `training`, `matches`, `wellness`, `scout` | Sim | Sim | Sim (Celery) | Nenhum |
| `reports` | Geração de relatórios (PDF/Excel), exportação, entrega de saída | `analytics`, `matches` | Sim | Sim | Sim (Celery) | `report.ready` |
| `ai_ingestion` | Ingestão de dados externos, integração com IA, importação em lote | Múltiplos | Sim | Não | Sim (Celery) | `ingestion.completed` |

**Coluna Workers**: indica se o módulo possui tasks Celery assíncronas. Módulos sem workers operam exclusivamente de forma síncrona via requisições HTTP.

---

## 3. Módulos Transversais (3)

| Módulo | Responsabilidade | Consumido por |
|--------|-----------------|---------------|
| `identity_access` | Autenticação JWT, RBAC, scopes de permissão, gestão de credenciais e sessão | Todos os módulos funcionais |
| `audit` | Log de auditoria imutável de eventos críticos, rastreabilidade de ações | Todos os módulos com ação auditável |
| `notifications` | Disparo de notificações (email/push/in-app), rastreamento de entrega | `training`, `matches`, `medical`, `competitions` |

**Módulos transversais não possuem domínio funcional próprio.** Eles provêm infraestrutura comportamental que outros módulos consomem. Um módulo transversal não deve absorver responsabilidade funcional de nenhum módulo que o consome.

---

## 4. Fronteiras Críticas

As fronteiras abaixo são as que mais geram confusão em decisões de implementação e modelagem.

| Fronteira | Módulo A | Módulo B | Regra de Separação |
|-----------|----------|----------|-------------------|
| `users` vs `identity_access` | `users`: dados de perfil, nome, foto, preferências, vínculo funcional | `identity_access`: credenciais, JWT, scopes, MFA, sessão | Nunca misturar perfil de pessoa com autenticação/autorização |
| `training` vs `exercises` | `training`: sessão de treino com contexto tático, data, atletas, objetivos | `exercises`: biblioteca de exercícios reutilizáveis, definição pura | `exercises` é lookup; `training` é evento operacional |
| `matches` vs `scout` | `matches`: resultado oficial, placar, súmula, estado do jogo | `scout`: análise tática detalhada por evento por jogador | `matches` é canônico; `scout` é derivado analítico |
| `wellness` vs `medical` | `wellness`: auto-report diário (PSE, carga, sono, humor, energia) | `medical`: diagnóstico clínico, lesões, prontuário, retorno ao jogo | `wellness` é operacional rotineiro; `medical` é clínico |
| `analytics` vs `reports` | `analytics`: cálculo, agregação, métrica, análise, KPIs | `reports`: empacotamento, formatação, entrega de saída analítica | Relatório não é fonte da métrica; analytics não formata saída final |
| `competitions` vs `matches` | `competitions`: estrutura do torneio, fases, classificação geral | `matches`: partida individual com placar e eventos | Partida pertence a competição, mas tem lifecycle próprio |

---

## 5. Diagrama de Dependências (Mermaid)

```mermaid
graph TD
    identity_access --> users
    identity_access --> seasons
    identity_access --> teams
    identity_access --> training
    identity_access --> wellness
    identity_access --> medical
    identity_access --> competitions
    identity_access --> matches
    identity_access --> scout
    identity_access --> exercises
    identity_access --> analytics
    identity_access --> reports
    identity_access --> ai_ingestion

    users --> teams
    users --> wellness
    users --> medical

    seasons --> teams
    seasons --> competitions

    teams --> training
    teams --> matches
    teams --> competitions

    exercises --> training

    training --> wellness
    training --> analytics

    competitions --> matches

    matches --> scout
    matches --> analytics

    wellness --> analytics
    scout --> analytics

    analytics --> reports

    audit -.->|observa| training
    audit -.->|observa| matches
    audit -.->|observa| medical
    audit -.->|observa| users

    notifications -.->|notifica| training
    notifications -.->|notifica| matches
    notifications -.->|notifica| medical
    notifications -.->|notifica| competitions
```

**Convenção**: setas sólidas são dependências diretas (o módulo de origem chama o de destino); setas tracejadas são observação ou notificação assíncrona (os transversais não acoplam funcionalmente).

---

## 6. Localização dos Contratos por Módulo

Padrão de localização: `docs/hbtrack/modulos/<modulo>/`

Arquivos esperados por módulo quando materializado via processo MCP:

| Número | Arquivo | Descrição |
|--------|---------|-----------|
| `00` | `00_<MODULO>_MODULE_RULES.json` | Regras do módulo, atores, dependências |
| `01` | `01_<MODULO>_OPENAPI.yaml` | Contrato OpenAPI do módulo |
| `04` | `04_<MODULO>_WORKFLOWS.arazzo.yaml` | Workflows Arazzo |
| `05` | `05_<MODULO>_EVENTS.asyncapi.yaml` | Eventos AsyncAPI |
| `06` | `06_<MODULO>_CONSUMER_CONTRACTS.md` | Contratos de consumo |
| `08` | `08_<MODULO>_TRACEABILITY.yaml` | Rastreabilidade |
| `12` | `12_<MODULO>_EXECUTION_BINDINGS.yaml` | Bindings de execução |
| `13` | `13_<MODULO>_DB_CONTRACT.yaml` | Contrato de banco de dados |
| `14` | `14_<MODULO>_UI_CONTRACT.yaml` | Contrato de UI |
| `15` | `15_<MODULO>_INVARIANTS.yaml` | Invariantes do módulo |
| `16` | `16_<MODULO>_AGENT_HANDOFF.json` | Handoff de agente |
| `17` | `17_<MODULO>_PROJECTIONS.yaml` | Projeções de estado |
| `18` | `18_<MODULO>_SIDE_EFFECTS.yaml` | Efeitos colaterais |
| `19` | `19_<MODULO>_TEST_SCENARIOS.yaml` | Cenários de teste |
| `20` | `20_<MODULO>_EXECUTOR_RESTRICTION_PROMPT.md` | Restrições do executor |

Ver `CONTRACT_SYSTEM_LAYOUT.md` para lista completa e regras de nomenclatura.

**Estado de materialização (2026-03-11):**

| Módulo | Estado MCP | Observações |
|--------|-----------|-------------|
| `training` | Avançado | Documentação extensa em `docs/hbtrack/modulos/treinos/` |
| `users` (subset `atletas`) | Iniciado | `docs/hbtrack/modulos/atletas/` — MCP parcial |
| `competitions` | FASE_0 | Documentação de fase inicial completa |
| Demais 13 módulos | Não iniciado | Aguardam processo MCP formal |

---

## 7. Processo MCP (Master Materialization Plan)

Ver `docs/hbtrack/modulos/MCP.md` para o processo completo de materialização de módulos.

**Regra**: módulos sem documentação MCP aprovada não podem receber ARs de implementação de funcionalidades. ARs de infraestrutura transversal são exceção com justificativa formal.

---

## 8. Heurística de Decisão de Módulo

Ao decidir onde uma nova regra, contrato ou comportamento pertence, responder:

1. Isso descreve **quem é a pessoa** ou **quem pode acessar o quê**? → `users` ou `identity_access`
2. Isso descreve **treino**, **exercício**, **jogo** ou **evento de scout**? → módulo específico correspondente
3. Isso é **métrica** ou **saída formatada**? → `analytics` ou `reports`
4. Isso é **bem-estar rotineiro** ou **informação clínica**? → `wellness` ou `medical`
5. Isso é **organização competitiva** ou **partida individual**? → `competitions` ou `matches`
6. Isso é responsabilidade funcional de um módulo ou preocupação transversal (auth, auditoria, notificação)? → módulo funcional ou transversal correspondente

Se a resposta continuar ambígua após estas perguntas, a decisão deve ser formalizada via ADR antes da implementação.

---

## 9. Regras de Expansão do Mapa

Um novo módulo só pode ser criado se todas as condições abaixo forem atendidas:
- Não couber semanticamente em nenhum dos 16 módulos existentes
- Não puder ser tratado como responsabilidade transversal formal já existente
- A sobrecarga semântica em um módulo atual for comprovada com evidências
- Houver decisão formal registrada em `docs/_canon/decisions/` antes de qualquer implementação

---

## 10. Referências Normativas

Este documento deve ser lido em conjunto com:
- `SYSTEM_SCOPE.md` — macrodomínios e escopo do produto
- `CONTRACT_SYSTEM_LAYOUT.md` — estrutura de filesystem e nomenclatura
- `CONTRACT_SYSTEM_RULES.md` — regras operacionais do sistema contract-driven
- `HANDBALL_RULES_DOMAIN.md` — regras formais do handebol (relevante para `training`, `competitions`, `matches`, `scout`, `analytics`)
- `docs/hbtrack/modulos/MCP.md` — processo de materialização de módulos
