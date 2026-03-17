# RELATÓRIO 2 — ANÁLISE DE PIPELINE: VISÃO × REALIDADE × LACUNAS

**Perspectiva:** Arquiteto de Software e Engenheiro de Governança Sênior
**Data:** 2026-03-17
**Escopo:** Análise da visão do humano × pipeline atual × identificação de lacunas críticas
**Tipo:** Diagnóstico estratégico de pipeline CDD com IA como desenvolvedor

---

## PARTE 1 — COMO O SEU PIPELINE FUNCIONA HOJE

O que você tem construído é uma **fundação de governança sólida, mas incompleta na execução**. O pipeline atual cobre até o ponto de "contrato pronto" e para. O restante — código, testes, frontend, produção — não existe ainda.

### O que existe e funciona

```
Humano fornece: módulo + task_type + descrição
        ↓
Pre-Contract Orchestrator (4 fases)
  Fase 0 — valida módulo (16 canônicos) + roteia para worker
  Fase 1 — verifica artefatos obrigatórios do módulo + decisões bloqueantes
  Fase 2 — Decision Discovery (debate arquitetural, aguarda aprovação humana)
  Fase 3 — carrega contexto de domínio completo
  Fase 4 — transfere para worker especializado
        ↓
Worker prompt (9 mapeados, 4 existem, 5 faltam)
        ↓
Contrato escrito no path canônico
        ↓
CI/CD (GitHub Actions) → validate_contracts.py
  oasdiff (breaking changes)      ✅
  Spectral (linting OpenAPI)      ✅
  Redocly CLI (validação)         ✅
  Schemathesis (contract testing) ⚠️ precisa de API live
        ↓
_reports/contract_gates/latest.json
```

### Workers: o que existe vs. o que falta

| Worker | Existe? | Task type que serve |
|---|:---:|---|
| `pre_contract_orchestrator.prompt.md` | ✅ | ponto de entrada de tudo |
| `decision_discovery.prompt.md` | ✅ | `architecture_review` |
| `create_arazzo_workflow.prompt.md` | ✅ | `new_workflow` |
| `create_asyncapi_contract.prompt.md` | ✅ | `new_event` |
| `create_json_schema_contract.prompt.md` | ✅ | `new_schema` |
| `create_module_docs.prompt.md` | ❌ | `new_module` |
| `create_openapi_contract.prompt.md` | ❌ | `new_contract`, `contract_revision` |
| `create_state_model.prompt.md` | ❌ | `new_state_model` |
| `create_ui_contract.prompt.md` | ❌ | `new_ui_contract` |

### Status atual dos módulos

`training` = `implementation_ready` (único módulo pronto).
Os outros **15 módulos** = `draft_contract`.
O sistema está pronto para um módulo, bloqueado nos outros 15.

### Status atual do pipeline CI

**FAIL** em dois gates bloqueantes:
- `OPENAPI_ROOT_STRUCTURE_GATE` — FAIL
- `DERIVED_DRIFT_GATE` — FAIL

O pipeline CI está vermelho. Construir fases novas sobre um pipeline vermelho é construir sobre areia.

---

## PARTE 2 — ANÁLISE DA SUA IDEIA

Sua ideia tem 4 fases implícitas. Cada uma é analisada com o que está certo, o que pode melhorar e como os melhores sistemas do mercado operam.

---

### Fase A — "Humano propõe → IA debate → Humano decide"

**O que está certo:**
Este modelo é o correto. Corresponde ao `Decision Discovery` que você já tem. A IA apresenta opções, aguarda aprovação explícita, registra como ADR. É o padrão de Architecture Decision Records usado por Netflix, Spotify e Stripe.

**O que pode melhorar:**
Hoje o Decision Discovery é técnico demais para um leigo. Ele apresenta "qual é o AUTH_STRATEGY" — não "como você quer que os usuários façam login". O debate acontece em linguagem de engenharia, não em linguagem de produto.

**Abordagem melhor (padrão de mercado):**
Sistemas como Vercel, Linear e Notion adotam o padrão **"3 opções com trade-off em linguagem humana + recomendação explícita"**:

```
Opção A: simples, rápido, pode limitar depois        → Recomendada para agora
Opção B: robusto, mas leva 3x mais tempo para construir
Opção C: o que grandes empresas usam, você não precisa hoje
IA diz claramente: "Recomendo A porque [razão em 1 frase]"
```

---

### Fase B — "IA analisa, critica, tenta quebrar, simula hacker"

**O que está certo:**
Este pensamento adversarial é correto e ausente em 99% dos projetos pequenos. É o que diferencia um sistema robusto de um sistema que quebra em produção.

**O que pode melhorar:**
Você está descrevendo 4 coisas diferentes que precisam ser separadas:

| # | Tipo de análise | Status atual |
|---|---|---|
| 1 | **Segurança** (OWASP, STRIDE, injeção, auth bypass) | ❌ Não existe |
| 2 | **Compatibilidade de consumidores** (Pact) — "quem quebra se eu mudar esta API?" | ❌ Não existe |
| 3 | **Gaps de domínio** — "o que falta para fechar esta feature?" | ❌ Não existe como fase formal |
| 4 | **Invariantes** — "o que nunca pode ser violado neste módulo?" | ✅ Existe (INVARIANTS por módulo) |

**Abordagem melhor:**
Empresas como Netflix e Amazon usam "contract mutation testing" — a IA deliberadamente tenta quebrar o próprio contrato que criou para encontrar fraquezas antes que qualquer código exista. Isso deve acontecer antes do handoff para implementação, não depois.

---

### Fase C — "IA executa: contratos, código, testes, frontend, Pact"

**O que está certo:**
A ideia de que a IA executa tudo é viável hoje com as ferramentas certas. É o modelo "AI-as-developer" que GitHub (Copilot Workspace), Cursor e Devin estão construindo.

**O que precisa estar claro:**
"IA executa" não significa "IA decide". Significa: dado um contrato aprovado pelo humano (que é a SSOT), a IA materializa esse contrato em código, testes e UI. O humano não precisa entender o código — mas precisa confirmar que o comportamento corresponde ao que pediu.

**O que falta para isso funcionar:** veja Parte 3 e Parte 4.

---

### Fase D — "IA diz o que falta para fechar uma feature"

**O que está certo:**
Este é o mecanismo mais valioso para um humano leigo. O `MODULE_REGISTRY.yaml` já rastreia status dos módulos — mas em YAML técnico ilegível para você. O que você precisa é de uma versão traduzida em linguagem humana, gerada automaticamente a cada sessão.

---

## PARTE 3 — O QUE VOCÊ NÃO ESTÁ DESCREVENDO (MAS É VITAL)

Estas são as peças que, se ausentes, impedem o sistema de funcionar mesmo que tudo mais esteja correto.

---

### 1. A CAMADA DE TRADUÇÃO (a mais crítica de todas)

Você é leigo em desenvolvimento. Quando você diz "quero registrar um treino", a IA precisa traduzir isso para:

```
POST /v1/training-sessions
Body: { athleteIds[], date, coachId, sessionType, blocks[] }
Response: TrainingSession com status DRAFT
```

E quando a IA pede uma decisão arquitetural, precisa traduzir:

```
TÉCNICO:  "qual estratégia de autenticação: JWT stateless vs. session-based?"

HUMANO:   "como usuários fazem login?
           Opção A: cada dispositivo independente (mais simples)
           Opção B: um login controla todos os dispositivos (mais controle)
           → Recomendo A para começar."
```

**Esta camada de tradução bidirecional não existe hoje no seu pipeline.** Sem ela, o sistema é tecnicamente correto mas inacessível para você. Você dependerá de um engenheiro para intermediar cada sessão.

---

### 2. CONTINUIDADE ENTRE SESSÕES (o problema invisível)

Cada conversa com a IA começa do zero. Ela não sabe o que foi decidido na sessão anterior, qual feature estava sendo construída, quais decisões foram tomadas. Isso significa:

- Você repete contexto toda vez
- A IA pode contradizer decisões anteriores sem saber
- O trabalho acumulado de uma sessão não acelera a próxima

O seu pipeline tem o `_reports/evidence/boot_resolution_report.json`, mas ele registra o boot técnico, não o estado da conversa com você. **Não existe hoje um "caderno de trabalho" que a IA lê no início de cada sessão para saber onde você parou.**

---

### 3. O QUE É UMA "FEATURE"? (definição ausente)

Você fala em "fechar uma feature" e "fechar um módulo". Mas o sistema não tem uma definição canônica de feature. Hoje existe apenas módulo (nível alto) e endpoint (nível técnico). Não existe o nível intermediário que você usa naturalmente: "quero a feature de registrar presença no treino".

Sem essa definição, a IA não consegue te dizer "esta feature está 70% pronta, faltam X e Y" — porque não sabe o que delimita uma feature.

---

### 4. ARQUITETURA DO CÓDIGO (o "como" da implementação)

Você tem contratos para a interface pública (OpenAPI), para os dados (JSON Schema), para os fluxos (Arazzo). Mas não existe nenhum documento definindo como o código interno deve ser organizado. Quando a IA for escrever o código, ela precisará saber:

- Qual padrão arquitetural? (Clean Architecture? Hexagonal? MVC?)
- Qual framework backend? (FastAPI? NestJS? Django?)
- Como se conecta ao banco de dados?
- Onde ficam as regras de negócio no código?
- Como a estrutura de pastas reflete os 16 módulos canônicos?

**Sem isso, a IA vai improvisar a arquitetura do código.** Cada sessão pode gerar código inconsistente com o da sessão anterior. O resultado é um sistema que funciona por partes mas não se integra.

---

### 5. PIPELINE DE DEPLOY (do código para o usuário)

Você descreve até "IA escreve o código". Mas depois do código pronto, como ele chega ao usuário? Isso envolve:

- Onde o código roda? (servidor próprio, cloud, Vercel, Railway?)
- Como o banco de dados é criado e atualizado?
- Como você aprova um deploy?
- O que acontece se algo quebrar depois do deploy?

**Este pipeline inteiro não existe no seu sistema hoje** e precisa ser decidido antes de qualquer linha de código ser escrita — porque a arquitetura do código depende de onde ele vai rodar.

---

### 6. MIGRAÇÃO DE DADOS (o problema que aparece tarde demais)

Quando o sistema estiver em produção com dados reais e você quiser mudar um contrato (ex.: adicionar um campo obrigatório num schema), o banco de dados precisa ser migrado. Os dados existentes precisam ser transformados.

**Um humano leigo não vai perceber que isso é necessário** até os dados corrompidos aparecerem em produção. O pipeline precisa detectar automaticamente "esta mudança de schema exige migração de dados" e perguntar ao humano antes de executar — antes do deploy, não depois.

---

### 7. PACT BROKER (infraestrutura ausente)

Você mencionou Pact (produtor/consumidor). Para funcionar, o Pact precisa de um servidor central (Pact Broker) onde os contratos de consumidor são publicados. Perguntas não respondidas:

- Quem são os consumidores das suas APIs? (o app mobile? o frontend web? um parceiro externo?)
- Onde fica o Pact Broker? (PactFlow gratuito? self-hosted?)
- Quando no pipeline os contratos do consumidor são verificados?

Sem isso definido, "implementar Pact" é uma instrução sem destino.

---

### 8. GERAÇÃO DE FRONTEND (a mais vaga das suas ideias)

"Frontend gerado automaticamente" — gerado como? De quê? Para qual plataforma?

Hoje existem ferramentas que geram partes da UI a partir de OpenAPI (Orval para React, OpenAPI Generator), mas nenhuma gera um produto completo. Elas geram apenas o layer de comunicação com a API (hooks, tipos, clients HTTP). A UI real (telas, fluxos, design) ainda precisa ser construída.

**Você precisa decidir antes de qualquer execução:**
- O frontend é web? mobile? tablet para técnicos em campo?
- Qual framework? (React/Next.js? Flutter? React Native?)
- O que exatamente é "gerado automaticamente" vs. o que precisa ser desenhado?

---

### 9. MONITORAMENTO EM PRODUÇÃO (contratos vs. realidade)

Depois que o sistema está no ar, como você sabe que está funcionando conforme os contratos? O Schemathesis no CI testa antes do deploy. Mas depois do deploy, APIs quebram por razões que os testes não capturam: dados reais, carga real, integrações reais.

**Não existe hoje nenhum mecanismo de monitoramento pós-deploy no seu pipeline.**

---

### 10. PROTOCOLO DE EMERGÊNCIA PARA O HUMANO LEIGO

Quando algo quebrar em produção (e vai quebrar), você vai receber um erro. Como leigo, você não vai entender o stack trace. O sistema precisa de um protocolo de "tradução de emergência": recebe o erro técnico → explica em linguagem humana → apresenta opções → aguarda sua decisão.

---

## PARTE 4 — O QUE FALTA PARA ATINGIR O OBJETIVO

Apresentado em ordem de prioridade real.

---

### PRIORIDADE 0 — Fechar o que está quebrado antes de expandir

O pipeline CI está em FAIL. `OPENAPI_ROOT_STRUCTURE_GATE` e `DERIVED_DRIFT_GATE` estão falhando. Antes de construir qualquer fase nova, o foundation precisa estar verde. Nenhuma outra prioridade avança com o pipeline vermelho.

**Ação:** corrigir os dois gates bloqueantes.

---

### PRIORIDADE 1 — Completar os workers faltantes

4 workers do orquestrador não existem. Sem eles, o orquestrador roteia para um prompt que não existe e para completamente para os task_types afetados.

**Ação:** criar `create_module_docs.prompt.md`, `create_openapi_contract.prompt.md`, `create_state_model.prompt.md`, `create_ui_contract.prompt.md` seguindo o padrão dos workers existentes.

---

### PRIORIDADE 2 — A Camada de Tradução (Human Interface Layer)

Precisa existir como um artefato formal no sistema: um documento que define como a IA se comunica com você.

**Regras que precisam existir:**
- Nunca usar jargão técnico sem tradução imediata
- Toda decisão apresentada em máximo 3 opções com trade-off em linguagem de produto
- Toda opção com recomendação explícita e razão em 1 frase
- Todo bloqueio técnico explicado como "o que você não pode fazer agora e por quê"
- Toda saída de gate/validação traduzida para "o que isso significa para você"

**Ação:** criar `docs/_canon/HUMAN_INTERFACE_POLICY.md`. Referenciar em todos os prompts de agente.

---

### PRIORIDADE 3 — Session State Handoff (Caderno de Trabalho)

Um template que a IA cria ao final de cada sessão e lê no início da próxima.

```yaml
# SESSION_HANDOFF.md — gerado ao final de cada sessão

sessao_data: 2026-03-17
feature_em_trabalho: "Registrar treino com presença de atletas"
modulo: training
fase_atual: contrato_criado_aguardando_codigo
decisoes_tomadas_hoje:
  - "Autenticação via JWT stateless (ADR-022)"
  - "Banco PostgreSQL (ADR-023)"
proxima_acao_ia: "Criar código de implementação do endpoint POST /v1/training-sessions"
decisoes_pendentes_do_humano:
  - "Confirmar: atletas ausentes devem gerar notificação automática? (sim/não)"
bloqueios_ativos: []
```

**Ação:** criar template em `.contract_driven/templates/`. Adicionar geração deste artefato como última etapa obrigatória de qualquer worker.

---

### PRIORIDADE 4 — Feature Registry (definição canônica de feature)

Um arquivo onde cada feature do sistema é definida em linguagem humana com suas dependências técnicas.

```yaml
# FEATURE_REGISTRY.yaml (exemplo)

features:
  registrar_treino:
    nome_humano: "Registrar um treino"
    descricao: "Técnico cria uma sessão de treino, define exercícios e registra presença"
    modulos_envolvidos: [training, exercises, wellness]
    surfaces_necessarias: [openapi_sync, state_model, permissions, arazzo]
    status: implementation_ready
    percentual_completo: 100
    falta_para_fechar: []

  monitorar_carga_atleta:
    nome_humano: "Monitorar carga de treino do atleta"
    modulos_envolvidos: [training, wellness, analytics]
    surfaces_necessarias: [sport_science, asyncapi, json_schema]
    status: draft_contract
    percentual_completo: 40
    falta_para_fechar:
      - "Regras científicas de cálculo de carga (SPORT_SCIENCE_RULES_WELLNESS)"
      - "Contrato de eventos para notificar analytics quando carga é registrada"
```

**Ação:** criar `docs/_canon/FEATURE_REGISTRY.yaml` e script que gera relatório legível a partir dele.

---

### PRIORIDADE 5 — Fase Adversarial Formal (Red Team Phase)

Um prompt `adversarial_analysis.prompt.md` que executa após o contrato ser criado e antes do handoff para código.

**Etapas formais:**

**1. OWASP Top 10 checklist aplicada ao contrato**
- Autenticação está presente em todos os endpoints?
- Autorização está definida por role?
- Dados sensíveis estão marcados e protegidos?
- Rate limiting está previsto?

**2. STRIDE Threat Modeling**
- Spoofing: alguém pode se passar por outro usuário?
- Tampering: alguém pode alterar dados em trânsito?
- Repudiation: ações críticas têm audit trail?
- Info Disclosure: dados vazam em respostas de erro?
- DoS: um endpoint pode ser sobrecarregado facilmente?
- Elevation: usuário comum pode executar ação de admin?

**3. Consumer Break Simulation**
- Se este contrato mudar desta forma, qual consumidor quebra?
- Existe field obrigatório novo que quebraria integração existente?

**4. Gap Analysis de Domínio**
- Quais casos de uso do `DOMAIN_RULES` não estão cobertos por este contrato?
- Quais invariantes do módulo não têm endpoint correspondente?

**Output para o humano:**
```
🔴 BLOQUEANTE (3): endpoint POST /training-sessions não tem autenticação definida
🟡 AVISO (2): campo `coachNotes` não tem política de dado sensível declarada
🟢 INFORMAÇÃO (1): consumer app-mobile pode quebrar se removermos campo `status`
```

---

### PRIORIDADE 6 — Arquitetura de Código Canônica

Antes de a IA escrever qualquer linha de código, as seguintes decisões precisam estar em ADRs aceitas:

| Decisão | Por que precisa estar definida antes |
|---|---|
| Stack backend (linguagem + framework) | A IA não pode alternar entre Python e TypeScript entre sessões |
| Padrão arquitetural (Clean Architecture / Hexagonal) | Define onde ficam regras de negócio, ports, adapters |
| Banco de dados (PostgreSQL? MongoDB?) | Impacta como os JSON Schemas se traduzem em tabelas |
| Estrutura de pastas por módulo | Cada um dos 16 módulos canônicos precisa de um destino no código |

**Recomendação:** Clean Architecture com ports & adapters funciona especialmente bem com CDD porque os contratos OpenAPI são literalmente os ports da aplicação.

---

### PRIORIDADE 7 — Pact Setup (Consumer-Driven Contract Testing)

**Passo a passo:**

1. **Definir consumidores:** frontend web, app mobile, integrações externas
2. **Escolher Pact Broker:** PactFlow (gratuito para projetos pequenos)
3. **Integrar no pipeline CI:**
   - Consumer publica contrato no broker após testes passarem
   - Provider verifica contratos do broker antes do deploy
   - Se consumer contrato quebrar → FAIL no gate `PACT_PROVIDER_GATE`
4. **Criar gate formal** `PACT_PROVIDER_GATE` em `docs/_canon/gates/GATES_REGISTRY.yaml`

---

### PRIORIDADE 8 — Deploy Pipeline

**Recomendação para humano leigo:**

| Plataforma | Por que | Trade-off |
|---|---|---|
| Railway | Deploy automático com push, banco gerenciado, rollback com 1 clique | Custo médio |
| Render | Similar ao Railway, free tier generoso | Mais lento no free tier |
| Vercel + Supabase | Excelente para Next.js frontend + API | Dois serviços para gerenciar |

**O que precisa ser decidido como ADR antes de escrever código:**
- Onde roda o backend?
- Onde fica o banco de dados?
- Como você (o humano) aprova antes de ir para produção?

---

### PRIORIDADE 9 — Human-Readable Module Readiness Report

Um script que lê `MODULE_REGISTRY.yaml` + artefatos existentes e produz relatório em linguagem humana.

**Exemplo de saída:**
```
=== RELATÓRIO DE PRONTIDÃO — HB TRACK ===
Data: 2026-03-17

✅ TRAINING — Pronto para desenvolvimento
   Todos os contratos aprovados. Pode começar o código.

⚠️  WELLNESS — 60% pronto
   O que falta para poder desenvolver:
   → Criar regras científicas de monitoramento de carga
   → Criar permissões de quem pode ver dados de saúde do atleta
   → Criar testes de validação do contrato
   Estimativa: 2 sessões de trabalho com a IA

❌ MEDICAL — 30% pronto
   O que falta:
   → Definir quais dados são considerados sigilosos (decisão sua)
   → Definir quem pode registrar e quem pode ver dados médicos (decisão sua)
   → Criar 6 artefatos de contrato
   Estimativa: 4 sessões de trabalho com a IA
```

---

## RESUMO EXECUTIVO

### O que você descreveu vs. o que existe hoje

| O que você descreveu | Status hoje |
|---|---|
| Humano propõe → IA debate → Humano decide | ⚠️ Existe (Decision Discovery), mas técnico demais para leigo |
| IA analisa e tenta quebrar | ❌ Não existe como fase formal |
| IA cria contratos de API | ⚠️ Parcialmente (4 de 9 workers existem, CI em FAIL) |
| IA cria testes | ❌ Não existe (Schemathesis precisa de API live) |
| Pact produtor/consumidor | ❌ Não existe |
| Frontend gerado automaticamente | ❌ Não existe (precisa ser definido antes) |
| IA escreve código | ❌ Não existe |
| Playwright tests | ❌ Não existe |
| IA pergunta ao humano quando necessário | ⚠️ Parcialmente (só decisões arquiteturais) |
| IA diz o que falta para fechar uma feature | ❌ Não existe em linguagem humana |

### O que você não descreveu mas é vital

| Lacuna | Impacto se continuar ausente |
|---|---|
| Camada de tradução (leigo ↔ técnico) | Você não consegue usar o sistema sem ajuda técnica terceira |
| Continuidade entre sessões | Cada sessão repete trabalho; IA pode contradizer decisões passadas |
| Definição canônica de "feature" | IA não consegue dizer o que falta para fechar algo |
| Arquitetura de código canônica | IA gera código inconsistente entre sessões |
| Pipeline de deploy | O código nunca chega ao usuário de forma controlada |
| Migração de dados | Dados corrompidos em produção sem aviso prévio |
| Pact Broker (infraestrutura) | Pact não funciona sem servidor centralizado definido |
| Monitoramento pós-deploy | Falhas em produção invisíveis até usuário reclamar |
| Protocolo de emergência traduzido | Você não reage a problemas sem engenheiro ao lado |
| Definição do que é "frontend gerado" | Objetivo impossível de executar sem decisão de escopo |

### Sequência recomendada de execução

```
AGORA (antes de qualquer desenvolvimento):
  1. Corrigir gates FAIL no CI
  2. Criar 4 workers faltantes
  3. Criar HUMAN_INTERFACE_POLICY.md (camada de tradução)
  4. Criar SESSION_HANDOFF template
  5. Decidir stack de deploy → ADR

CURTO PRAZO (próximas sessões):
  6. Criar FEATURE_REGISTRY.yaml
  7. Criar prompt de Fase Adversarial
  8. Decidir arquitetura de código → ADR
  9. Configurar Pact Broker

MÉDIO PRAZO (antes de ir para produção):
 10. Human-Readable Readiness Report script
 11. Pipeline de deploy com aprovação humana
 12. Monitoramento pós-deploy
 13. Protocolo de emergência traduzido
```

---

**Conclusão:** seu pipeline hoje é excelente em governança e fraco em execução. A fundação está correta — o que não é pouca coisa. O que falta não é reinventar o que existe, é completar as 9 prioridades acima em ordem. A maior delas, a Camada de Tradução, é a que determina se você consegue ou não trabalhar com o sistema de forma autônoma. Sem ela, toda a sofisticação da governança fica atrás de uma barreira técnica que você não consegue cruzar sozinho.

---

Os 3 pontos mais importantes do relatório, para você não perder de vista:

1. Seu pipeline para na metade certa
A governança (contratos, regras, validações) é sólida. Mas o pipeline para em "contrato pronto" — código, testes, frontend e deploy não existem ainda. E o CI está vermelho em 2 gates antes de qualquer expansão.

2. A lacuna mais crítica que você não descreveu: a Camada de Tradução
Toda a sofisticação do seu sistema CDD fica inacessível para você sem um mecanismo que traduza bidirecional: sua intenção em linguagem humana → contratos técnicos, e decisões técnicas → opções em linguagem de produto com recomendação explícita. Sem isso, você precisa de um engenheiro para intermediar cada sessão.

3. A sequência importa
Não adianta construir Pact, código ou frontend enquanto o CI está vermelho e 4 workers estão faltando. A ordem correta é: fechar o que quebrou → completar os workers → criar a camada de tradução → só então expandir para execução (código, testes, deploy).

*`PRE_CONTRACT_SKIPPED: audit-only, no normative contract artifact produced`*
