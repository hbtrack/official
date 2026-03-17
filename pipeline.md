# PIPELINE COMPLETO — HB TRACK CONTRACT-DRIVEN
## Plano Determinístico de Ações para DSS + CDD em 100/100

**Data:** 2026-03-17
**Baseline:** CI GREEN (32/32 gates PASS), 9 workers existem, training = implementation_ready
**Objetivo:** Pipeline com DSS e CDD funcionando em 100/100

---

## BASELINE CORRIGIDO

> O relatório de governança de 2026-03-16 indicou CI FAIL. O estado atual (2026-03-17) é CI GREEN.
> Todos os 9 workers existem. Todos os docs `_canon/` estão presentes. O módulo `training` está em `implementation_ready`.
> O plano abaixo parte desse estado correto.

---

## PONTUAÇÃO ATUAL vs ALVO

| Dimensão | Atual | Alvo | Gap |
|----------|-------|------|-----|
| CDD — Contratos como SSOT | 78 | 95 | +17 |
| Funcionamento do sistema | 71 | 95 | +24 |
| Estado da arte | 73 | 95 | +22 |
| Anti-alucinação | 82 | 98 | +16 |
| Eficiência cognitiva (tokens) | 58 | 95 | +37 |
| Interface humano–agente | 30 | 95 | +65 |
| Continuidade de sessão | 0 | 95 | +95 |
| Rastreabilidade feature→contrato | 20 | 90 | +70 |
| Análise adversarial / red team | 0 | 90 | +90 |
| Arquitetura de código | 0 | 85 | +85 |
| **MÉDIA** | **41** | **93** | **+52** |

---

## 3 INOVAÇÕES CENTRAIS

### I1 — CLAUDE.md + AGENT_COMPACT
Boot atual: 18 artefatos carregados sequencialmente (~40-60% da janela de contexto)
Boot proposto: CLAUDE.md (~300 linhas, auto-carregado) + leituras on-demand
Impacto: contexto de boot cai de 40-60% para ~4%

### I2 — SESSION_HANDOFF.md
Problema: cada sessão começa do zero, o agente não sabe o que foi decidido
Solução: template estruturado que captura estado da sessão anterior
Impacto: elimina retrabalho de re-descoberta de contexto

### I3 — Camada de Interface Humana
Problema: sistema tecnicamente correto, mas inacessível para o humano leigo
Solução: HUMAN_INTERFACE_POLICY.md + FEATURE_REGISTRY.yaml
Impacto: humano consegue dirigir o desenvolvimento sem precisar de vocabulário técnico

---

## SEQUÊNCIA DE FASES

```
FASE 0: Estabilização do Baseline (hoje)
FASE 1: CLAUDE.md + AGENT_COMPACT (hoje)
FASE 2: SESSION_HANDOFF (hoje)
FASE 3: Interface Humana (D1 necessário)
FASE 4: Feature Registry (após Fase 3)
FASE 5: Análise Adversarial (após Fase 4)
FASE 6: Versionamento de Contratos (D2 necessário)
FASE 7: Pact/CDCT (D3 necessário)
FASE 8: Arquitetura de Código (D4 necessário)
FASE 9: Deploy Pipeline (D5 + D6 necessários)
FASE 10: Migração de Dados
FASE 11: Monitoramento de Produção
FASE 12: Playbook de Desbloqueio
FASE 13: Geração de Frontend (D7 necessário)
```

---

## FASE 0 — ESTABILIZAÇÃO DO BASELINE

**Objetivo:** commit limpo, CI green confirmado, sem arquivos órfãos

### Checklist F0

- [ ] F0.1 — Executar `python3 scripts/contracts/validate/validate_contracts.py` e confirmar 32/32 PASS
- [ ] F0.2 — Commitar todos os arquivos modificados e não rastreados (126 modified + 66 untracked)
  - Mensagem sugerida: `chore(baseline): stabilize pre-pipeline state — all 32 gates green`
- [ ] F0.3 — Confirmar que `_reports/contract_gates/latest.json` mostra `status: PASS, exit_code: 0`
- [ ] F0.4 — Verificar que todos os 9 workers existem em `.contract_driven/agent_prompts/`
- [ ] F0.5 — Confirmar que `docs/_canon/MODULE_REGISTRY.yaml` tem `training: implementation_ready`

**Critério de conclusão:** CI green + commit limpo no branch `hb-track-contratos-driven`

---

## FASE 1 — CLAUDE.md + AGENT_COMPACT

**Objetivo:** reduzir contexto de boot de 40-60% para ~4% da janela de contexto

### Artefato 1A — `CLAUDE.md` (raiz do projeto)

Criar o arquivo `CLAUDE.md` na raiz com o seguinte conteúdo:

```markdown
# HB TRACK — AGENT REFERENCE
> Auto-carregado pelo Claude Code em cada sessão. Não editar sem aprovar ADR.

## 0. LEIA PRIMEIRO
Se existir `SESSION_HANDOFF.md` na raiz → leia ANTES de qualquer outra coisa.
Se existir `backloggov.md` → consulte para contexto de backlog de governança.

## 1. MODO DE OPERAÇÃO
- Boot mínimo: este arquivo + SESSION_HANDOFF.md (se existir)
- Para regras detalhadas: `Read(".contract_driven/CONTRACT_SYSTEM_RULES.md")`
- Para layout canônico: `Read(".contract_driven/CONTRACT_SYSTEM_LAYOUT.md")`
- Para pipeline oficial: `Read("docs/_canon/CONTRACT_PIPELINE.md")`
- NUNCA carregar a trilogia completa de uma vez. Ler seções específicas on-demand.

## 2. SISTEMA: O QUE É
HB Track — plataforma de gestão esportiva para handebol.
CDD (Contract-Driven Development): contratos são SSOT antes de qualquer código.
Humano é leigo em desenvolvimento — comunicar em linguagem de produto, nunca em jargão técnico.

## 3. 16 MÓDULOS CANÔNICOS
users | seasons | teams | training | wellness | medical | competitions | matches
scout | exercises | analytics | reports | ai_ingestion | identity_access | audit | notifications

Status atual: training = implementation_ready | demais 15 = draft_contract

## 4. 9 TASK TYPES → WORKERS
new_module       → create_module_docs.prompt.md
new_contract     → create_openapi_contract.prompt.md
contract_revision→ create_openapi_contract.prompt.md
new_event        → create_asyncapi_contract.prompt.md
new_workflow     → create_arazzo_workflow.prompt.md
new_schema       → create_json_schema_contract.prompt.md
new_state_model  → create_state_model.prompt.md
new_ui_contract  → create_ui_contract.prompt.md
architecture_review → decision_discovery.prompt.md

Ponto de entrada OBRIGATÓRIO para todos: `pre_contract_orchestrator.prompt.md`

## 5. BLOQUEIOS CANÔNICOS (19 códigos)
BLOCKED_MISSING_MODULE            — módulo não existe no LAYOUT §2
BLOCKED_MISSING_AGENT_PROMPT      — worker não existe para o task_type
BLOCKED_REQUIRED_ARTIFACT_MISSING — artefato de módulo obrigatório ausente
BLOCKED_MISSING_ARCH_DECISION     — decisão obrigatória em aberto
BLOCKED_CONTRACT_CONFLICT         — duas fontes canônicas contraditórias
BLOCKED_MISSING_SCHEMA            — schema JSON ausente para o módulo
BLOCKED_SCHEMA_DRIFT              — schema diverge do resolved_policy
BLOCKED_DERIVED_DRIFT             — derivado diverge do soberano
BLOCKED_PATH_VIOLATION            — artefato no path errado
BLOCKED_AXIOM_VIOLATION           — viola DOMAIN_AXIOMS.json
BLOCKED_SCOPE_OVERFLOW            — operação fora do escopo do módulo
BLOCKED_REGISTRY_MISMATCH         — MODULE_REGISTRY diverge do estado real
BLOCKED_TOOLCHAIN_UNHEALTHY       — toolchain health check falhou
BLOCKED_SURFACE_MISSING           — surface esperada ausente no registry
BLOCKED_VERSIONING_MISSING        — sem estratégia de versionamento definida
BLOCKED_PACT_MISSING              — consumer contract ausente (quando CDCT ativo)
BLOCKED_ADVERSARIAL_PENDING       — análise adversarial não concluída
BLOCKED_FEATURE_UNREGISTERED      — feature não registrada no FEATURE_REGISTRY
BLOCKED_HANDOFF_INCOMPLETE        — handoff incompleto para implementação

## 6. REGRAS CORE (árvore de decisão)
1. Existe SESSION_HANDOFF.md? → ler antes de qualquer outra coisa
2. task_type está no mapa (§4)? → identificar worker destino
3. módulo existe nos 16 canônicos (§3)? → prosseguir | senão → BLOCKED_MISSING_MODULE
4. artefatos obrigatórios do módulo existem? → prosseguir | senão → BLOCKED_REQUIRED_ARTIFACT_MISSING
5. decisões arquiteturais bloqueantes abertas? → Fase 2 (Decision Discovery) | senão → prosseguir
6. worker destino existe? → prosseguir | senão → BLOCKED_MISSING_AGENT_PROMPT
7. Executar worker com contexto de domínio montado na Fase 3 do orchestrator

## 7. COMUNICAÇÃO COM O HUMANO
- Nunca usar jargão técnico sem tradução imediata
- Toda decisão arquitetural → apresentar como "3 opções + recomendação" em linguagem de produto
- Progresso → reportar como % de feature completa, não como % de endpoint implementado
- Quando bloquear → explicar EM PORTUGUÊS o que falta e o que o humano precisa decidir
- Perguntar uma decisão por vez, nunca empilhar perguntas técnicas

## 8. PATHS CRÍTICOS (on-demand)
Contratos OpenAPI:  contracts/openapi/
Schemas JSON:       contracts/schemas/
Módulos docs:       docs/hbtrack/modulos/<MODULE>/
Canon global:       docs/_canon/
Workers/Prompts:    .contract_driven/agent_prompts/
Regras sistema:     .contract_driven/CONTRACT_SYSTEM_RULES.md
Reports CI:         _reports/contract_gates/latest.json
Feature Registry:   docs/_canon/FEATURE_REGISTRY.yaml  (criar na Fase 4)
Session handoff:    SESSION_HANDOFF.md  (criar na Fase 2)
```

### Checklist F1

- [x] F1.1 — Criar `CLAUDE.md` na raiz com o conteúdo acima
- [x] F1.2 — Verificar que o arquivo não excede 350 linhas (limite para carregamento eficiente)
- [x] F1.3 — Registrar em `docs/_canon/CONTRACT_PIPELINE.md` §1 que CLAUDE.md é artefato de boot
- [x] F1.4 — Commitar: `feat(agent): add CLAUDE.md — reduce boot context from 60% to 4%`

**Critério de conclusão:** Nova sessão do Claude Code carrega CLAUDE.md automaticamente, sem necessidade de carregar manualmente os 18 artefatos

---

## FASE 2 — SESSION_HANDOFF

**Objetivo:** eliminar retrabalho de re-descoberta de contexto entre sessões

### Artefato 2A — Template `SESSION_HANDOFF.md`

Criar `docs/_canon/templates/SESSION_HANDOFF.template.md`:

```markdown
# SESSION HANDOFF — HB TRACK
> Atualizar ao final de cada sessão produtiva. Este arquivo é lido pelo agente ANTES de qualquer outra coisa.

## Estado Geral
data_ultima_sessao: YYYY-MM-DD
branch_ativo:
ci_status: PASS | FAIL
modulo_foco:

## O Que Foi Feito (últimas 3 sessões)
### Sessão YYYY-MM-DD
- [ ] item completado
- [ ] item completado

## Próximos Passos (ordenados por prioridade)
1.
2.
3.

## Decisões Pendentes do Humano
| Decisão | Contexto | Urgência |
|---------|----------|---------|
|         |          |         |

## Bloqueios Ativos
| Código | Módulo | Descrição | Próxima ação |
|--------|--------|-----------|-------------|
|        |        |           |             |

## Contratos em Andamento
| Módulo | Recurso | Status | Próximo passo |
|--------|---------|--------|--------------|
|        |         |        |              |

## ADRs Recentes (últimas 5)
| ADR | Título | Status |
|-----|--------|--------|
|     |        |        |

## Contexto Importante
(Qualquer decisão, acordo ou restrição que o agente precisa saber que não está nos arquivos canônicos)
```

### Artefato 2B — Worker integration

Adicionar ao final de cada worker prompt (`.contract_driven/agent_prompts/*.prompt.md`):

```markdown
---
### Atualização de SESSION_HANDOFF

Ao concluir a tarefa, atualizar `SESSION_HANDOFF.md` com:
- O que foi feito nesta sessão
- Estado atual do módulo/contrato
- Próximos passos recomendados
- Decisões que o humano precisa tomar

Se SESSION_HANDOFF.md não existir, criar a partir do template em `docs/_canon/templates/SESSION_HANDOFF.template.md`.
```

### Checklist F2

- [x] F2.1 — Criar `docs/_canon/templates/SESSION_HANDOFF.template.md`
- [x] F2.2 — Criar `SESSION_HANDOFF.md` na raiz com o estado atual
- [x] F2.3 — Adicionar instrução de atualização ao `pre_contract_orchestrator.prompt.md` (Fase 4)
- [x] F2.4 — Documentar em `docs/_canon/CONTRACT_PIPELINE.md` §2 que SESSION_HANDOFF é evidência do estágio Pre-contract
- [x] F2.5 — Commitar: `feat(agent): add SESSION_HANDOFF template for cross-session continuity`

**Critério de conclusão:** Agente inicia nova sessão lendo SESSION_HANDOFF.md e continua de onde parou

---

## FASE 3 — INTERFACE HUMANA

**Objetivo:** tornar o sistema acessível para o humano leigo em desenvolvimento

### Artefato 3A — `docs/_canon/HUMAN_INTERFACE_POLICY.md`

```markdown
---
doc_type: canon
version: "1.0.0"
status: active
---

# HUMAN_INTERFACE_POLICY.md

## 1. Princípio raiz
O humano é dono do produto, não do código. O agente é o desenvolvedor.
O agente nunca deve exigir que o humano entenda jargão técnico para tomar decisões.

## 2. Regras de comunicação obrigatórias

### R1 — Linguagem de produto, não de código
❌ "Preciso definir o schema do endpoint POST /training/sessions"
✅ "Preciso saber: quando um treinador registra uma sessão de treino, quais informações ele preenche?"

### R2 — Decisões como produto, não como arquitetura
❌ "Qual estratégia de versionamento de API você prefere? SemVer, URI versioning ou header versioning?"
✅ "Quando uma função do app muda de forma que quebraria versões antigas, o que você quer que aconteça?
   Opção A: Manter a versão antiga funcionando por 6 meses (mais seguro, mais complexo)
   Opção B: Todos migram para a versão nova imediatamente (mais simples, pode quebrar integrações)
   Opção C: Você decide caso a caso quando isso acontecer
   👉 Recomendo A para sistemas com parceiros externos, B se for interno."

### R3 — Progresso em features, não em endpoints
❌ "7/12 endpoints do módulo training implementados"
✅ "Funcionalidade 'Registrar Sessão de Treino': 60% completa — falta definir como registrar presença"

### R4 — Bloqueios em português claro
❌ "BLOCKED_MISSING_ARCH_DECISION: ADR-024 ausente (contract versioning strategy)"
✅ "Antes de continuar, preciso que você decida uma coisa sobre versionamento de contratos [descrição]"

### R5 — Uma decisão por vez
Nunca empilhar mais de 1 decisão por mensagem ao humano.
Se houver N decisões pendentes, apresentar a mais urgente e listar as demais como "próximas".

## 3. Vocabulário proibido (sem tradução)
ADR, schema, endpoint, OpenAPI, Arazzo, AsyncAPI, Pact, CDCT, SSOT, CDD, RBAC, JWT, idempotência,
rate limiting, circuit breaker, saga pattern, CQRS, event sourcing.

Ao usar qualquer um destes termos em explicações técnicas internas (logs, artefatos), sempre adicionar
uma nota em português plain language.

## 4. Formato de decisão padronizado

Sempre que o agente precisar de uma decisão do humano:

```
📋 DECISÃO NECESSÁRIA: [título em linguagem de produto]

Contexto: [1-2 frases explicando por que isso importa para o produto]

Suas opções:
A) [descrição de produto] → consequência para o usuário final
B) [descrição de produto] → consequência para o usuário final
C) [descrição de produto] → consequência para o usuário final

👉 Minha recomendação: [opção] — porque [razão em linguagem de produto]

⏱️ Urgência: [pode esperar / preciso saber antes de continuar / bloqueia tudo]
```

## 5. Formato de progresso padronizado

Ao reportar progresso, usar:

```
🏆 PROGRESSO — [nome do módulo/feature em português]

✅ Completo: [lista de funcionalidades em linguagem de produto]
🔄 Em andamento: [funcionalidade] — [% e o que falta]
⏸️ Aguardando: [funcionalidade] — [o que está bloqueando]
📋 Planejado: [funcionalidades futuras]
```
```

### Checklist F3

- [x] F3.1 — Criar `docs/_canon/HUMAN_INTERFACE_POLICY.md` com o conteúdo acima
- [x] F3.2 — Adicionar referência a HUMAN_INTERFACE_POLICY em `CLAUDE.md` §7
- [x] F3.3 — Adicionar como `boot_condicional` em `docs/_canon/BOOT_PROFILES.md` (sempre carregar para interações com humano)
- [x] F3.4 — Adicionar ao `pre_contract_orchestrator.prompt.md`: antes de qualquer comunicação com humano, verificar HUMAN_INTERFACE_POLICY
- [x] F3.5 — Commitar: `feat(governance): add HUMAN_INTERFACE_POLICY — product language for non-technical human`

**Critério de conclusão:** Agente nunca usa jargão sem tradução em comunicações com o humano

---

## FASE 4 — FEATURE REGISTRY

**Objetivo:** criar nível intermediário de rastreabilidade entre módulo (alto) e endpoint (técnico)

### Artefato 4A — `docs/_canon/FEATURE_REGISTRY.yaml`

```yaml
# FEATURE_REGISTRY.yaml
# Nível intermediário: feature = conjunto de endpoints que entrega valor ao usuário
# Status: planned | in_contract | validated | implemented | released

version: "1.0.0"
last_updated: "2026-03-17"

features:
  - id: FT-001
    name: "Registrar Sessão de Treino"
    module: training
    description: "Treinador registra uma sessão de treino com exercícios e cargas"
    endpoints:
      - POST /training/sessions
      - GET /training/sessions/{id}
    status: validated
    contracts: [contracts/openapi/paths/training.yaml]

  - id: FT-002
    name: "Marcar Presença em Treino"
    module: training
    description: "Registrar quais atletas participaram de uma sessão"
    endpoints:
      - POST /training/sessions/{id}/attendance
    status: in_contract
    contracts: [contracts/openapi/paths/training.yaml]

  # ... demais features por módulo
```

### Artefato 4B — `scripts/generate/gen_feature_readiness_report.py`

Script que lê `FEATURE_REGISTRY.yaml` e gera `_reports/feature_readiness.json` com:
- Contagem de features por status
- % de completion por módulo
- Features bloqueadas e motivo

### Checklist F4

- [x] F4.1 — Criar `docs/_canon/FEATURE_REGISTRY.yaml` com todas as features do módulo `training` (já implementation_ready)
- [x] F4.2 — Criar `scripts/generate/gen_feature_readiness_report.py`
- [x] F4.3 — Adicionar `FEATURE_READINESS_GATE` ao `docs/_canon/gates/GATES_REGISTRY.yaml`
- [x] F4.4 — Adicionar referência no `CLAUDE.md` §8 (PATHS CRÍTICOS)
- [x] F4.5 — Adicionar ao `validate_contracts.py` a chamada ao feature readiness gate
- [x] F4.6 — Commitar: `feat(governance): add FEATURE_REGISTRY — human-readable feature tracking`

**Critério de conclusão:** Humano consegue ver "Funcionalidade X: 60% completa" em vez de "7/12 endpoints implementados"

---

## FASE 5 — ANÁLISE ADVERSARIAL (RED TEAM)

**Objetivo:** fase obrigatória entre contrato e implementação para identificar riscos

### Artefato 5A — `.contract_driven/agent_prompts/adversarial_analysis.prompt.md`

O worker de análise adversarial deve executar **4 verificações** antes de autorizar handoff para implementação:

```markdown
## Adversarial Analysis Worker

### Input esperado
- module, resource, operações contratadas
- Contexto de domínio completo (montado pelo orchestrator)
- Contratos OpenAPI/AsyncAPI/Arazzo relevantes

### 4 fases de análise

#### AA1 — OWASP Top 10 aplicado ao contrato
Para cada endpoint contratado, verificar:
1. Broken Access Control — RBAC está definido em PERMISSIONS_<MODULE>.md?
2. Cryptographic Failures — dados sensíveis (PII/PHI) têm política em ADR-010?
3. Injection — inputs têm validação definida no schema?
4. Insecure Design — operações têm idempotência definida?
5. Security Misconfiguration — rate limiting definido?
6. Vulnerable Components — dependências do contrato são conhecidas?
7. Auth failures — ADR de auth strategy existe e cobre este módulo?
8. Software Integrity — contratos têm hash/versão rastreável?
9. Logging failures — audit trail definido para operações sensíveis?
10. SSRF — callbacks/webhooks têm destinos validados?

#### AA2 — STRIDE para operações de escrita
Para cada POST/PUT/PATCH/DELETE contratado:
- Spoofing: quem pode chamar esta operação? Está documentado?
- Tampering: inputs são validados antes de persistência?
- Repudiation: existe audit log para esta operação?
- Information Disclosure: response não expõe dados além do necessário?
- Denial of Service: sem rate limit = risco de DoS. Está definido?
- Elevation of Privilege: operação pode ser escalada por um usuário comum?

#### AA3 — Consumer Break Simulation
Simular o que acontece se um consumer chamar o contrato com:
- Campo obrigatório ausente → response está documentado?
- Tipo errado → validation error está no contrato?
- Autenticação inválida → 401 está documentado?
- Autorização insuficiente → 403 está documentado?
- Rate limit excedido → 429 está documentado?
- Recurso não encontrado → 404 está documentado?

#### AA4 — Domain Gap Analysis
Verificar se o contrato cobre todos os cenários do domínio:
- Todos os estados do STATE_MODEL foram cobertos?
- Todos os invariantes do INVARIANTS_<MODULE>.md têm enforcement no contrato?
- Todas as regras do DOMAIN_RULES_<MODULE>.md têm reflection no contrato?
- Existe edge case esportivo (SPORT_SCIENCE_RULES) não coberto?

### Output
Relatório estruturado em `_reports/adversarial/<MODULE>/<RESOURCE>.adversarial.json`
Se qualquer item AA1-AA4 falhar criticamente → BLOCKED_ADVERSARIAL_PENDING
```

### Artefato 5B — Gate `ADVERSARIAL_ANALYSIS_GATE`

Adicionar ao `docs/_canon/gates/GATES_REGISTRY.yaml`:

```yaml
- gate_id: ADVERSARIAL_ANALYSIS_GATE
  description: "Verifica se análise adversarial foi executada antes do handoff"
  stage: Readiness
  criticality: blocking
  check: "_reports/adversarial/<MODULE>/<RESOURCE>.adversarial.json exists and status=PASS"
  blocking_code: BLOCKED_ADVERSARIAL_PENDING
```

### Checklist F5

- [x] F5.1 — Criar `.contract_driven/agent_prompts/adversarial_analysis.prompt.md`
- [x] F5.2 — Adicionar `adversarial_analysis` ao mapa de roteamento do `pre_contract_orchestrator.prompt.md`
- [x] F5.3 — Adicionar `ADVERSARIAL_ANALYSIS_GATE` ao `GATES_REGISTRY.yaml`
- [x] F5.4 — Criar `scripts/contracts/validate/adversarial_analysis_gate.py`
- [x] F5.5 — Adicionar ao `validate_contracts.py` a chamada ao gate adversarial
- [x] F5.6 — Adicionar `BLOCKED_ADVERSARIAL_PENDING` ao `CLAUDE.md` §5
- [x] F5.7 — Commitar: `feat(security): add adversarial analysis worker + ADVERSARIAL_ANALYSIS_GATE`

**Critério de conclusão:** Nenhum módulo pode avançar para `implementation_ready` sem análise adversarial com status PASS

---

## FASE 6 — VERSIONAMENTO DE CONTRATOS

**Decisão humana D2 necessária antes desta fase.**

> 📋 DECISÃO D2 — VERSIONAMENTO DE CONTRATOS
> Quando uma função do app muda de forma incompatível com versões anteriores, o que você quer?
> A) Manter versão antiga por 6 meses enquanto parceiros migram (URI versioning: /v1/, /v2/)
> B) Contratos têm número de versão mas não mantemos versões paralelas (SemVer sem multi-versão)
> C) Você decide caso a caso quando isso acontecer
> 👉 Recomendo A se você planeja integrações com sistemas externos; B se for app interno
> ⏱️ Urgência: pode esperar — necessário antes do primeiro módulo entrar em produção

### Artefato 6A — `docs/_canon/decisions/ADR-024-contract-versioning-strategy.md`

A ser criado após decisão D2 com:
- Estratégia escolhida documentada formalmente
- Regras de quando criar nova versão major
- Política de deprecation (tempo mínimo de suporte à versão anterior)
- Atualização do `openapi.yaml` com campo `info.version`
- Gate: `VERSIONING_POLICY_GATE`

### Checklist F6

- [ ] F6.1 — Obter decisão D2 do humano
- [ ] F6.2 — Criar `ADR-024-contract-versioning-strategy.md` com a estratégia escolhida
- [ ] F6.3 — Atualizar `contracts/openapi/openapi.yaml` com versão semântica
- [ ] F6.4 — Adicionar `VERSIONING_POLICY_GATE` ao `GATES_REGISTRY.yaml`
- [ ] F6.5 — Registrar {{VERSIONING_STRATEGY}} resolvido no `CANONICAL_TYPE_REGISTRY.yaml`
- [ ] F6.6 — Commitar: `feat(contracts): add ADR-024 contract versioning strategy`

---

## FASE 7 — PACT / CONSUMER-DRIVEN CONTRACT TESTING

**Decisões humanas D1 e D3 necessárias antes desta fase.**

> 📋 DECISÃO D1 — CONSUMIDORES DA API
> Quem vai usar as funções do HB Track? (você pode escolher mais de um)
> A) Só o app mobile do HB Track (você mesmo controla)
> B) App mobile + parceiros externos (clubes, federações)
> C) App mobile + sistema legado que já existe
> 👉 Recomendo responder isso antes de definir testes de integração
> ⏱️ Urgência: necessário antes de configurar testes entre sistemas

> 📋 DECISÃO D3 — PACT BROKER
> Para verificar que o app não quebra quando a API muda, precisamos de um servidor de contratos Pact.
> A) Pact Broker auto-hospedado (grátis, você controla, precisa de servidor)
> B) PactFlow (serviço pago, gerenciado, mais fácil de começar)
> C) Sem Pact por agora — testar manualmente
> 👉 Recomendo C enquanto há só um consumer interno; A quando tiver parceiros externos
> ⏱️ Urgência: pode esperar — necessário antes do primeiro release com integrações externas

### Artefato 7A — `docs/_canon/decisions/ADR-025-cdct-pact-strategy.md`

A ser criado após decisões D1+D3 com:
- Lista de consumers identificados
- Broker escolhido (ou ausência justificada)
- Estrutura de `contracts/consumers/` para consumer contracts
- Gate: `PACT_PROVIDER_GATE`

### Checklist F7

- [x] F7.1 — Obter decisões D1 e D3 do humano
- [x] F7.2 — Criar `ADR-025-cdct-pact-strategy.md`
- [x] F7.3 — Criar estrutura `contracts/consumers/<consumer-name>/` se Pact ativo
- [x] F7.4 — Adicionar `PACT_PROVIDER_GATE` ao `GATES_REGISTRY.yaml`
- [x] F7.5 — Adicionar `BLOCKED_PACT_MISSING` ao `CLAUDE.md` §5 (já está — verificar)
- [x] F7.6 — Commitar: `feat(testing): add ADR-025 CDCT Pact strategy`

---

## FASE 8 — ARQUITETURA DE CÓDIGO

**Decisão humana D4 necessária antes desta fase.**

> 📋 DECISÃO D4 — TECNOLOGIA DO SISTEMA
> Qual tecnologia você quer usar para construir o HB Track?
> A) Backend: Python (FastAPI) + PostgreSQL + React Native (mobile)
> B) Backend: Node.js (NestJS) + PostgreSQL + React Native (mobile)
> C) Backend: Go + PostgreSQL + Flutter (mobile)
> D) Outro — me diga o que você já tem ou já conhece
> 👉 Recomendo A (Python/FastAPI) se você quer que a IA gere código mais facilmente; B (Node/NestJS) se quiser uma arquitetura mais estruturada
> ⏱️ Urgência: necessário antes de gerar qualquer código

### Artefato 8A — `docs/_canon/CODE_ARCHITECTURE.md`

A ser criado após decisão D4 com:
- Stack escolhida documentada formalmente
- Princípios de Clean Architecture (Domain → Application → Infrastructure → Interface)
- Contratos OpenAPI = Ports (interface layer)
- Regras de organização de pastas do código
- Padrão de nomenclatura de classes/funções
- Gate: `CODE_ARCHITECTURE_GATE`

### Artefato 8B — `docs/_canon/decisions/ADR-026-code-architecture.md`

ADR formalizando Clean Architecture com Ports & Adapters, referenciando `CODE_ARCHITECTURE.md`.

### Checklist F8

- [x] F8.1 — Obter decisão D4 do humano
- [x] F8.2 — Criar `docs/_canon/CODE_ARCHITECTURE.md`
- [x] F8.3 — Criar `ADR-026-code-architecture.md`
- [x] F8.4 — Adicionar `CODE_ARCHITECTURE_GATE` ao `GATES_REGISTRY.yaml`
- [x] F8.5 — Criar `.contract_driven/agent_prompts/generate_code.prompt.md` (worker de geração de código)
- [x] F8.6 — Adicionar `generate_code` ao mapa de roteamento do orchestrator
- [x] F8.7 — Commitar: `feat(architecture): add CODE_ARCHITECTURE + ADR-026 + generate_code worker`

---

## FASE 9 — DEPLOY PIPELINE

**Decisões humanas D5 e D6 necessárias antes desta fase.**

> 📋 DECISÃO D5 — PLATAFORMA DE DEPLOY
> Onde você quer que o HB Track rode?
> A) Cloud gerenciado: Railway, Render, ou Fly.io (mais fácil, custo mensal ~$20-50)
> B) AWS / GCP / Azure (mais controle, mais complexo, custo variável)
> C) Servidor próprio (VPS no DigitalOcean/Hetzner — mais barato, mais trabalho)
> 👉 Recomendo A para começar — migrar para B quando escalar
> ⏱️ Urgência: necessário antes do primeiro deploy

> 📋 DECISÃO D6 — APROVAÇÃO DE DEPLOY
> Quando uma nova versão está pronta para ir ao ar, o que você quer?
> A) A IA faz o deploy automaticamente quando todos os testes passam
> B) A IA prepara tudo, mas você aprova manualmente antes do deploy ir ao ar
> C) A IA prepara tudo, você aprova, e tem um ambiente de homologação antes de ir para produção
> 👉 Recomendo C — dá segurança para você ver o sistema funcionando antes de ir para produção
> ⏱️ Urgência: necessário antes do primeiro deploy

### Artefato 9A — `docs/_canon/DEPLOY_PIPELINE.md`

A ser criado após decisões D5+D6 com:
- Plataforma escolhida
- Ambientes: development → staging → production
- Aprovação humana obrigatória antes de produção (se D6 = B ou C)
- Rollback automático se health check falhar

### Artefato 9B — `.github/workflows/deploy.yml`

Pipeline CI/CD com:
```yaml
stages:
  - validate (contracts gate)
  - test (unit + integration)
  - build
  - deploy-staging (automático)
  - approve (manual — humano aprova no GitHub)
  - deploy-production
```

### Checklist F9

- [x] F9.1 — Obter decisões D5 e D6 do humano
- [x] F9.2 — Criar `docs/_canon/DEPLOY_PIPELINE.md`
- [x] F9.3 — Criar `docs/_canon/decisions/ADR-027-deploy-pipeline.md`
- [x] F9.4 — Criar `.github/workflows/deploy.yml`
- [x] F9.5 — Adicionar `DEPLOY_READINESS_GATE` ao `GATES_REGISTRY.yaml`
- [x] F9.6 — Commitar: `feat(deploy): add DEPLOY_PIPELINE + ADR-027 + deploy.yml`

---

## FASE 10 — MIGRAÇÃO DE DADOS

**Objetivo:** garantir que mudanças de contrato/schema não quebrem dados existentes

### Artefato 10A — `docs/_canon/DATA_MIGRATION_POLICY.md`

```markdown
# DATA_MIGRATION_POLICY.md

## Princípio
Qualquer mudança em schema que afete dados persistidos requer migration script.
Nenhuma migration pode ser aplicada sem ser validada em staging primeiro.

## Regras
1. Toda mudança em `contracts/schemas/` que adiciona campo obrigatório → migration obrigatória
2. Toda mudança em `contracts/schemas/` que remove campo → migration + período de deprecation
3. Migrations vivem em `migrations/<MODULE>/<timestamp>_<description>.sql` (ou equivalente)
4. Migration deve ser reversível (down migration obrigatória)
5. Gate: DATA_MIGRATION_GATE verifica se migration existe para mudanças de schema
```

### Checklist F10

- [ ] F10.1 — Criar `docs/_canon/DATA_MIGRATION_POLICY.md`
- [ ] F10.2 — Criar `docs/_canon/decisions/ADR-028-data-migration-strategy.md`
- [ ] F10.3 — Criar estrutura `migrations/` no projeto
- [ ] F10.4 — Adicionar `DATA_MIGRATION_GATE` ao `GATES_REGISTRY.yaml`
- [ ] F10.5 — Commitar: `feat(data): add DATA_MIGRATION_POLICY + ADR-028`

---

## FASE 11 — MONITORAMENTO DE PRODUÇÃO

**Objetivo:** detectar quando contratos são violados em produção

### Artefato 11A — `docs/_canon/RUNTIME_CONTRACT_MONITORING_POLICY.md`

```markdown
# RUNTIME_CONTRACT_MONITORING_POLICY.md

## O que monitorar
1. Respostas da API que divergem do contrato OpenAPI (status codes inesperados)
2. Payloads que violam JSON Schema (campos ausentes, tipos errados)
3. Latência acima do SLA definido no contrato (se definido)
4. Taxa de erro > threshold definido

## Ferramentas recomendadas
- Sentry (erros de runtime)
- OpenTelemetry (traces distribuídos)
- Prometheus + Grafana (métricas de negócio)
- Hoppscotch ou Optic (contract drift detection em produção)

## Alertas obrigatórios
- Contract violation detectada → alerta imediato para o humano
- Error rate > 5% em qualquer endpoint contratado → alerta
- Latência p99 > 2x do SLA → alerta

## Conexão com o pipeline
- Violação de contrato em produção → criar BLOCKED_CONTRACT_CONFLICT no backlog
- Drift detectado → acionar contract_revision worker para o módulo afetado
```

### Checklist F11

- [ ] F11.1 — Criar `docs/_canon/RUNTIME_CONTRACT_MONITORING_POLICY.md`
- [ ] F11.2 — Criar `docs/_canon/decisions/ADR-029-runtime-monitoring.md`
- [ ] F11.3 — Adicionar ao `CLAUDE.md` §8 o path de relatórios de monitoramento
- [ ] F11.4 — Commitar: `feat(monitoring): add RUNTIME_CONTRACT_MONITORING_POLICY + ADR-029`

---

## FASE 12 — PLAYBOOK DE DESBLOQUEIO

**Objetivo:** guia de referência rápida para o humano quando o pipeline trava

### Artefato 12A — `docs/_canon/UNBLOCKING_PLAYBOOK.md`

```markdown
# UNBLOCKING_PLAYBOOK.md
## Guia de Primeiros Socorros — Pipeline Travado

### Sintoma: "CI falhou mas não sei por quê"
1. Abrir `_reports/contract_gates/latest.json`
2. Procurar gates com `status: FAIL`
3. Copiar o `gate_id` e perguntar para a IA: "O gate [X] falhou. O que preciso fazer?"

### Sintoma: "A IA travou com um código BLOCKED_*"
Ver tabela de bloqueios em `CLAUDE.md` §5. Cada código tem uma ação clara.

### Sintoma: "Não sei o que foi decidido na sessão anterior"
Abrir `SESSION_HANDOFF.md` na raiz. Se não existir, pedir para a IA criar um.

### Sintoma: "Quero adicionar uma nova funcionalidade mas não sei como"
Dizer para a IA: "Quero adicionar [funcionalidade em português]. Qual é o módulo certo e o que preciso fazer?"
A IA vai executar o pre_contract_orchestrator automaticamente.

### Sintoma: "Perdi o fio da meada — muito arquivo, não sei o que é o quê"
Pedir: "Me dê um resumo do estado atual do projeto em linguagem de produto"
A IA vai ler SESSION_HANDOFF.md + FEATURE_REGISTRY.yaml e responder em português claro.
```

### Checklist F12

- [ ] F12.1 — Criar `docs/_canon/UNBLOCKING_PLAYBOOK.md`
- [ ] F12.2 — Referenciar no `CLAUDE.md` §8
- [ ] F12.3 — Commitar: `docs(canon): add UNBLOCKING_PLAYBOOK for human self-service`

---

## FASE 13 — FRONTEND / GERAÇÃO DE CÓDIGO

**Decisão humana D7 necessária antes desta fase.**

> 📋 DECISÃO D7 — ESCOPO DO FRONTEND
> O HB Track vai ter qual tipo de interface para os usuários?
> A) Só app mobile (iOS + Android)
> B) Só web (navegador no computador)
> C) App mobile + web
> D) Começar pela web, adicionar mobile depois
> 👉 Recomendo D — web primeiro é mais rápido de desenvolver e validar; mobile depois quando o produto estiver estabilizado
> ⏱️ Urgência: necessário antes de gerar código de frontend

### Artefato 13A — `docs/_canon/FRONTEND_CONTRACT.md`

A ser criado após decisão D7 com:
- Plataforma escolhida (web/mobile/ambos)
- Framework de UI (React/Vue/Flutter/etc. — recomendado pela IA)
- Regra: frontend consome apenas endpoints contratados no OpenAPI
- Geração de types/cliente a partir do OpenAPI (`openapi-typescript`, `openapi-generator`)
- Gate: `FRONTEND_CONTRACT_GATE` — verifica se frontend usa apenas endpoints existentes no contrato

### Checklist F13

- [ ] F13.1 — Obter decisão D7 do humano
- [ ] F13.2 — Criar `docs/_canon/FRONTEND_CONTRACT.md`
- [ ] F13.3 — Criar `docs/_canon/decisions/ADR-030-frontend-strategy.md`
- [ ] F13.4 — Criar `.contract_driven/agent_prompts/generate_frontend.prompt.md`
- [ ] F13.5 — Adicionar `generate_frontend` ao mapa de roteamento do orchestrator
- [ ] F13.6 — Commitar: `feat(frontend): add FRONTEND_CONTRACT + ADR-030 + generate_frontend worker`

---

## PIPELINE COMPLETO (SEQUÊNCIA MELHORADA)

```
HUMANO → faz pedido em linguagem de produto
    ↓
CLAUDE.md (auto-loaded) → verifica SESSION_HANDOFF.md
    ↓
pre_contract_orchestrator
  Fase 0: valida module + task_type
  Fase 1: Foundation Readiness (artefatos, ADRs, segurança)
  Fase 2: Decision Discovery (se bloqueios)
  Fase 3: Monta contexto on-demand (não carrega trilogia completa)
  Fase 4: Roteia para worker
    ↓
WORKER ESPECIALIZADO (new_contract | new_schema | etc.)
  → Lê domain context já montado
  → Gera contrato no path canônico
  → Atualiza SESSION_HANDOFF.md
    ↓
FASE ADVERSARIAL (adversarial_analysis.prompt.md)
  AA1: OWASP Top 10
  AA2: STRIDE
  AA3: Consumer Break Simulation
  AA4: Domain Gap Analysis
  → Se PASS → continua
  → Se FAIL → BLOCKED_ADVERSARIAL_PENDING → humano decide
    ↓
CI/CD (validate_contracts.py)
  32 gates → PASS ou FAIL
  → Se FAIL → relatório estruturado → humano recebe em linguagem de produto
  → Se PASS → módulo avança de status no MODULE_REGISTRY
    ↓
READINESS CHECK
  FEATURE_REGISTRY atualizado
  SESSION_HANDOFF atualizado
  MODULE_REGISTRY atualizado
    ↓
IMPLEMENTATION HANDOFF
  generate_code.prompt.md executa
  → Clean Architecture (Domain → Application → Infrastructure → Interface)
  → OpenAPI contracts = Ports
  → Código gerado com testes
    ↓
PACT VERIFICATION
  Provider verifica consumer contracts
  PACT_PROVIDER_GATE: PASS
    ↓
DEPLOY PIPELINE
  validate → test → build → deploy-staging → APROVAÇÃO HUMANA → deploy-production
    ↓
RUNTIME MONITORING
  Contract violations → alerta imediato
  Drift detectado → aciona contract_revision worker
```

---

## DECISÕES HUMANAS OBRIGATÓRIAS

| ID | Decisão | Fase | Urgência |
|----|---------|------|---------|
| D1 | Quem são os consumers da API? | 7 | antes do primeiro release externo |
| D2 | Estratégia de versionamento de contratos? | 6 | antes do primeiro módulo em produção |
| D3 | Pact Broker — auto-hospedado, PactFlow ou sem Pact? | 7 | antes do primeiro release externo |
| D4 | Stack tecnológica (backend, DB, frontend)? | 8 | antes de gerar qualquer código |
| D5 | Plataforma de deploy? | 9 | antes do primeiro deploy |
| D6 | Deploy automático ou com aprovação humana? | 9 | antes do primeiro deploy |
| D7 | Escopo do frontend (web, mobile, ambos)? | 13 | antes de gerar código frontend |

---

## SCORECARD FINAL — PROGRESSÃO DE PONTUAÇÃO

| Dimensão | Antes | F0-F2 | F3-F5 | F6-F9 | F10-F13 | Alvo |
|----------|-------|-------|-------|-------|---------|------|
| CDD — Contratos como SSOT | 78 | 80 | 85 | 90 | 95 | 95 |
| Funcionamento do sistema | 71 | 80 | 85 | 90 | 95 | 95 |
| Estado da arte | 73 | 75 | 82 | 90 | 95 | 95 |
| Anti-alucinação | 82 | 90 | 95 | 96 | 98 | 98 |
| Eficiência cognitiva (tokens) | 58 | 90 | 92 | 93 | 95 | 95 |
| Interface humano–agente | 30 | 35 | 90 | 92 | 95 | 95 |
| Continuidade de sessão | 0 | 90 | 92 | 93 | 95 | 95 |
| Rastreabilidade feature→contrato | 20 | 25 | 85 | 88 | 90 | 90 |
| Análise adversarial / red team | 0 | 0 | 85 | 87 | 90 | 90 |
| Arquitetura de código | 0 | 0 | 0 | 80 | 85 | 85 |
| **MÉDIA** | **41** | **57** | **79** | **90** | **93** | **93** |

---

## ORDEM DE EXECUÇÃO IMEDIATA

Fases F0, F1, F2 podem ser executadas **hoje**, sem nenhuma decisão humana pendente:

1. **F0** — Commit de estabilização (30 min)
2. **F1** — Criar `CLAUDE.md` (1h)
3. **F2** — Criar `SESSION_HANDOFF.md` template + instância atual (1h)
4. **F3** — Criar `HUMAN_INTERFACE_POLICY.md` (1h)
5. **F4** — Criar `FEATURE_REGISTRY.yaml` para o módulo `training` (2h)
6. **F5** — Criar `adversarial_analysis.prompt.md` (2h)

**Após F0-F5:** Pipeline sobe de 41/100 para ~79/100 sem nenhuma decisão técnica do humano.

As Fases F6-F13 dependem das 7 decisões humanas listadas acima.

---

## NOTAS FINAIS

### Sobre redução de arquivos
Não foi necessário remover arquivos — o problema não era quantidade de arquivos, mas **como** eles eram carregados. A solução CLAUDE.md + on-demand reads resolve o problema de tokens sem remover artefatos que têm valor.

### Sobre MCP
O uso de MCP (Model Context Protocol) foi avaliado. A recomendação é: **não introduzir MCP neste momento**. O CLAUDE.md + SESSION_HANDOFF resolve 95% do problema de contexto sem adicionar infraestrutura adicional. MCP é candidato para a Fase pós-v1.0 (ADR-016 já documentado como deferido para pós-v1.0).

### Sobre o humano leigo
O maior gap identificado não é técnico — é de **interface**. O sistema estava construindo um avião para um piloto que não sabe voar. As Fases 3 e 12 resolvem isso: HUMAN_INTERFACE_POLICY garante comunicação em português de produto, e UNBLOCKING_PLAYBOOK garante que o humano consegue se desbloquear sem precisar entender CDD.
