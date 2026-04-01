# AUDITORIA SÊNIOR — Contract-Driven Development (CDD) do HB Track

> Data: 2026-03-31 | Auditor: Agente Sênior CDD | Commit base: `20935b8` (main)
> Escopo: processo CDD completo — do contrato ao código ao DONE

---

## PARTE 1 — Veredito Executivo

### O CDD do HB Track está sendo efetivo?

**PARCIALMENTE.**

O CDD é genuinamente efetivo na **camada de autoria e estruturação de contratos**. Os contratos OpenAPI, AsyncAPI, JSON Schema e Arazzo existem para todos os 17 módulos, são estruturalmente íntegros, e o código backend implementado reflete fielmente esses contratos em endpoints, schemas, FSMs e regras de domínio.

No entanto, o CDD **falha como processo ponta a ponta** em três dimensões críticas:

1. **Enforcement em runtime é desligado** — Schemathesis (a única validação que prova que o código vivo obedece ao contrato) está excluído do CI e só roda manualmente com flag explícita. O teste de conformidade contrato→código **não é automático**.

2. **Gate coverage real é superficial** — O perfil `precommit` (usado no CI) executa apenas **11 de 53 gates**; os outros 40 são `SKIP_NOT_APPLICABLE` porque ferramentas externas (redocly, spectral, asyncapi) não estão instaladas no ambiente CI. O número "54 gates PASS" reportado vem de execuções locais com tooling completo, não do CI.

3. **Evidência de processo é sintética** — Os 17 `baseline_backfill.json` foram gerados no mesmo dia (2026-03-23) com timestamps idênticos e `evidence_mode: baseline_backfill`. Não representam execução real do pipeline CDD e sim uma reconstrução retroativa.

### Está funcionando como processo completo ou apenas como estrutura documental?

**Funciona como processo para autoria de contratos. Funciona parcialmente como governança. Não funciona como enforcement de ponta a ponta.**

A cadeia `contrato → código → validação → deploy` tem rupturas: o contrato dirige a autoria do código, mas não prova continuamente que o código permanece conforme, e o deploy não é condicionado a essa prova.

### Está ajudando o sistema a chegar ao DONE de forma previsível?

**PARCIALMENTE.** O ROADMAP com fases sequenciais e critérios de DONE por fase é um instrumento real e funcional. Fases 0-3 foram concluídas com evidência tangível. Porém, a FASE 4 está parcialmente concluída (auth enforcement feito, mas Schemathesis contra staging pendente), e as Fases 5-6 não têm evidência executável. A definição de DONE no nível de "fase concluída" é boa; no nível de "módulo realmente pronto para produção" ela é incompleta.

---

## PARTE 2 — Mapa do Processo Real

| Etapa do processo | O que deveria acontecer | O que realmente acontece | Artefatos envolvidos | Status |
|:---|:---|:---|:---|:---|
| **Boot de sessão** | Agente lê `SESSION_HANDOFF.md` → identifica modo (CDD/ROADMAP) → carrega boot profile | Funciona. Agente lê handoff, identifica modo, carrega profile correspondente. Boot profiles existem e são resolvidos. | `SESSION_HANDOFF.md`, `BOOT_PROFILES.yaml`, `AGENT_INSTRUCTIONS.md` | **Alinhado** |
| **Identificação de tarefa** | `TASK_CATALOG.yaml` roteia task_type → worker prompt | Funciona. 18 task types mapeados, cada um com worker associado. Routing automático via `pre_contract_orchestrator`. | `TASK_CATALOG.yaml`, `pre_contract_orchestrator.prompt.md` | **Alinhado** |
| **Verificação pré-authoring** | `hb verify` valida módulo, task_type, boot profile → exitcode 0 | Funciona para verificação estrutural. Mas `hb verify` na prática aciona a mesma engine de gates que `validate_contracts.py`, e o gate `READINESS_SUMMARY_GATE` falha quando a sessão anterior deixou `session_start` em modo incompatível. | `scripts/hb`, `MODULE_REGISTRY.yaml`, `session_start.json` | **Parcialmente alinhado** |
| **Authoring de contrato** | Worker especializado cria artefato seguindo template + regras canônicas | Funciona bem. Contratos são criados em paths canônicos com estrutura correta. OpenAPI, AsyncAPI, Arazzo, JSON Schema — todos existem para 17 módulos. | Worker prompts, templates, `CONTRACT_SYSTEM_RULES.md` | **Alinhado** |
| **Registro de artefato** | `hb artifact <path>` registra SHA-256 do artefato criado | Existe e funciona quando executado. A questão é que no Modo ROADMAP (onde está o desenvolvimento atual), `hb artifact` **não é usado** por design. | `scripts/hb` | **Parcialmente alinhado** |
| **Validação estrutural** | `validate_contracts.py` executa todos os gates → exitcode 0 | Executa, mas com **cobertura real de ~20%** no perfil `precommit` (CI). 40 de 53 gates são SKIP por falta de tooling local. A validação completa só roda localmente com ferramentas instaladas. | `validate_contracts.py`, `GATES_REGISTRY.yaml` | **Desalinhado** |
| **Validação de contrato→código** | Schemathesis testa se a API implementada conforma ao schema OpenAPI | **Excluído do CI** (`--ignore=tests/schemathesis`). Só roda com `HB_RUN_SCHEMATHESIS=1` + banco e Redis ativos. O teste mais importante do CDD como processo de enforcement está desligado. | `tests/schemathesis/`, `contracts/openapi/` | **Desalinhado** |
| **Geração de código** | Worker `generate_code` produz código a partir do contrato, com Clean Architecture | Funcionou. 17 módulos com `domain/`, `application/`, `infrastructure/`, `api.py`, `schemas.py`. Endpoints conformes ao contrato. | `generate_code.prompt.md`, `src/*/` | **Alinhado** |
| **Promoção de status de módulo** | `draft_contract` → `validated_contract` → `implementation_ready` → `implemented` com gates em cada transição | Todos os 17 módulos estão em `implemented` desde 2026-03-23, mas os `baseline_backfill` usados como evidência de pré-contrato foram gerados sinteticamente. A promoção real através dos gates não é verificável. | `MODULE_REGISTRY.yaml`, `_reports/agent_execution/` | **Parcialmente alinhado** |
| **Handoff de sessão** | `SESSION_HANDOFF.md` atualizado ao final de cada sessão com estado, bloqueios, próxima ação | Funciona, mas está **fragmentado**: existem 7 arquivos `SESSION_HANDOFF_*.md` na raiz, sem linhagem clara. O principal `SESSION_HANDOFF.md` está atualizado, mas o `HANDOFF_COHERENCE_GATE` está **falhando** (divergência de modo CDD vs ROADMAP no session_start). | `SESSION_HANDOFF.md`, `session_handoff.schema.json` | **Parcialmente alinhado** |
| **Deploy com validação** | CI → staging → health check → validação humana → produção | Workflow existe (`.github/workflows/deploy.yml`). VPS configurado. Mas deploy real em staging **não tem evidência registrada** (nenhum URL, nenhum health check output). | `deploy.yml`, `infra/`, `VPS/` | **Desalinhado** |

---

## PARTE 3 — Avaliação do CDD por Dimensão

| Dimensão | Avaliação | Evidência | Problema principal | Impacto |
|:---|:---|:---|:---|:---|
| **Contratos dirigem decisões** | **Forte** | Decision IR para 7 módulos críticos. ADRs referenciadas nos contratos. `DECISION_IR_CONFORMANCE_GATE` PASS. | Decisões de 10 módulos sem Decision IR (por design — superfície não exigida). | Baixo — módulos simples não precisam. |
| **Contratos dirigem código** | **Forte** | 100% match `operationId` ↔ endpoints em `training` (22/22) e `teams` (8/8). FSM no `rules.py` reflete contrato. Schemas Pydantic derivados. | O código foi gerado a partir dos contratos. A aderência é estrutural, não acidental. | Alto — é o ponto mais forte do CDD. |
| **Sequência processual correta** | **Parcial** | Pipeline (boot → verify → check → authoring → artifact → validate) definido e funcional. Modo ROADMAP separado por design. | No Modo ROADMAP (onde o projeto está agora), a sequência CDD **não se aplica**. A separação é correta, mas significa que o CDD está "inativo" para o trabalho atual. | Médio — CDD fez seu trabalho na fase de contratos; agora está em modo passivo. |
| **Alinhamento contrato-código** | **Forte** | Endpoints, schemas, FSMs, enums (`DOMAIN_AXIOMS`) e regras de domínio (`rules.py`) todos conformes. 54 enums validados por `AXIOM_INTEGRITY_GATE`. | Nenhuma verificação automática contínua de que o alinhamento se mantém ao longo do tempo. Schemathesis deveria fazer isso mas está desligado no CI. | **Alto** — o alinhamento pode degradar sem detecção. |
| **Alinhamento contrato-prompt** | **Forte** | Workers prompts referenciam contratos, MODULE_REGISTRY e TASK_CATALOG. `pre_contract_orchestrator` roteia via SSOT. | Prompt não pode ser a única fonte de regra (regra canônica). Conformidade verificável. | Baixo. |
| **Alinhamento contrato-gate** | **Parcial** | Registry com 53 gates, 42 integrados em `validate_contracts.py`. Paridade verificada por `test_gate_registry_parity.py`. | **Teste de paridade excluído do CI** (`--ignore=tests/pipeline_gates`). Na prática, se um gate for adicionado ao executor e removido do registry (ou vice-versa), o CI não detecta. | **Alto** — a paridade é verificada mas não enforçada. |
| **Continuidade entre sessões** | **Parcial** | `SESSION_HANDOFF.md` existe, tem schema validador, inclui bloqueios e próxima ação. | 7 arquivos de handoff na raiz sem consolidação. `HANDOFF_COHERENCE_GATE` está **FALHANDO** no momento (divergência CDD/ROADMAP). Timestamps não-lineares sugerem sessões paralelas sem lineage. | **Médio** — o handoff principal funciona, mas a fragmentação cria ruído. |
| **Definição de progresso** | **Forte** | ROADMAP com 14 fases, cada uma com tarefas atômicas e checkbox. `MODULE_REGISTRY` com lifecycle normativo. `FEATURE_REGISTRY` com 31 features rastreadas. | Checkboxes marcados sem evidência executável linkada (ex: "1142 PASS" citado no ROADMAP sem link para log de execução). | Médio — progresso é declarado, não provado por artefato. |
| **Definição de DONE** | **Parcial** | Cada fase do ROADMAP tem "Critério de Done" explícito. Cada módulo tem lifecycle com estados definidos. | DONE no nível de "módulo implemented" não garante que o módulo funciona em staging. DONE no nível de fase precisa de evidência executável (health check output, URL de staging, log de teste). | **Alto** — DONE é declarativo, não verificável por terceiros. |
| **Redução de alucinação** | **Forte** | `DOMAIN_AXIOMS.json` como SSOT de enums. Workers carregam contratos como contexto. Regra: "se prompt conflita com canon, bloquear". `BLOCKED_*` codes definidos. | Alucinação residual detectada na auditoria de auth (2026-03-27): 13 módulos tinham stubs que "pareciam implementados" mas não enforçavam auth. | Médio — o CDD reduz alucinação na autoria, mas não impede stubs no código gerado. |
| **Rastreabilidade** | **Parcial** | `_reports/agent_execution/` com 17 backfills + 1 evidência real. `_reports/contract_gates/latest.json` com resultado de gates. Git log com commits atomicos por tarefa. | Backfills são sintéticos (mesmo dia, mesmos timestamps). Rastreabilidade real do processo de autoria de cada módulo **não existe** — foi reconstruída retroativamente. | **Alto** — não é possível auditar "quando" e "como" cada contrato foi criado. |
| **Efetividade operacional** | **Parcial** | ROADMAP fases 0-3 concluídas com evidência tangível. Infra Docker, CI/CD, VPS configurados. Backend com 17 módulos implementados e 393+ testes passando. | Fase 4 parcialmente completa (auth corrigido, Schemathesis pendente). Deploy em staging sem evidência. CI exclui testes críticos. O "último mile" do CDD (provar que funciona em produção) está incompleto. | **Alto** — o sistema **quase** chega ao DONE mas os últimos passos não estão enforçados. |

---

## PARTE 4 — O que no CDD Funciona de Verdade

### 1. Contratos como SSOT para autoria de código
Os contratos OpenAPI são a fonte de verdade real. O código em `src/*/api.py` foi gerado a partir deles e mantém conformidade verificável: operationIds, schemas de request/response, FSMs, enums. Isso **não é aparência** — é a fundação real do sistema.

### 2. DOMAIN_AXIOMS como vocabulário controlado
O `DOMAIN_AXIOMS.json` com 84 enums funciona como dicionário canônico. O `AXIOM_INTEGRITY_GATE` verifica que contratos usam apenas enums autorizados. Isso elimina uma classe inteira de inconsistências (nomes de status, roles, categorias).

### 3. Separação CDD / ROADMAP
A decisão de ter dois modos operacionais (CDD para contratos, ROADMAP para implementação) é genuinamente útil. Evita que infraestrutura e deploy sejam bloqueados por gates de contrato. O ROADMAP é um instrumento real de progresso.

### 4. Clean Architecture enforçada por módulo
A estrutura `domain/ → application/ → infrastructure/ → api.py` é consistente nos 17 módulos. Isso não é acidental — o worker `generate_code` usa o contrato como input e produz código com essa arquitetura.

### 5. FSM e regras de domínio derivadas do contrato
O `training/domain/rules.py` com 7 estados e transição fechada (`VALID_TRANSITIONS`) reflete diretamente o state model do contrato. Invariantes como `INV-TRAIN-002/003` estão codificadas como exceções de domínio.

### 6. Pipeline de gates como checklist estruturado
O `validate_contracts.py` com 53 gates organizados por tier é um instrumento real de checklist. Quando executado com tooling completo, valida integridade estrutural de todos os artefatos. É genuinamente útil para detectar drift.

### 7. `HANDOFF_COHERENCE_GATE`
O gate que valida `SESSION_HANDOFF.md` contra schema JSON é provavelmente o gate mais operacionalmente útil: garante que o estado declarado da sessão é estruturalmente válido. O fato de estar **falhando agora** prova que funciona como detector.

### 8. Schemathesis como bridge contrato→runtime
O design do teste Schemathesis (property-based testing contra o schema OpenAPI) é exatamente o que um CDD precisa para provar conformidade em runtime. O fato de existir e funcionar (quando ativado) é um ponto forte do design.

---

## PARTE 5 — O que no CDD é Só Aparência

### 1. "54 gates PASS" — número inflado
O número "54 gates PASS" reportado em `latest.json` vem de uma execução local com ferramentas completas (redocly, spectral, asyncapi CLI). No CI real (`--profile precommit`), **apenas 11 gates executam** e 40 são `SKIP_NOT_APPLICABLE`. O CI vê ~20% dos gates. O número 54 é verdadeiro **em contexto local**, mas não representa enforcement automático.

### 2. Baseline backfill como evidência de processo
Os 17 arquivos `*_baseline_backfill.json` em `_reports/agent_execution/` foram criados no mesmo dia (2026-03-23) com `evidence_mode: baseline_backfill` e `workerDest: baseline_backfill`. São explicitamente reconstruções retroativas, não evidências de que o pipeline CDD foi executado para cada módulo. O gate `PRE_CONTRACT_EVIDENCE_GATE` aceita esses backfills por design, mas isso significa que **a evidência de processo é auto-satisfeita**.

### 3. Status "implemented" para 17 módulos sem staging
Todos os 17 módulos estão em `implemented` no `MODULE_REGISTRY.yaml` desde 2026-03-23. Mas "implemented" deveria significar "código em `src/<module>/`, runtime/testes reais". Na prática, 13 módulos tinham auth stubs que aceitavam requests anônimos até 2026-03-27 (4 dias depois da promoção). O status não regrediu quando o bug foi descoberto.

### 4. Waivers vazios com problemas conhecidos
O `waivers.json` está vazio (`[]`), mas existem problemas conhecidos não-waivados:
- Schemathesis excluído do CI (deveria ter waiver formal ou fix)
- `test_session_state_phase3.py` trava (deveria ter waiver formal)
- `HANDOFF_COHERENCE_GATE` falhando (deveria ter waiver ou fix)

A ausência de waivers formais quando há problemas conhecidos sugere que o sistema de waivers não está sendo usado como deveria.

### 5. Workflows Arazzo — existem mas não governam
Os workflows Arazzo definem composições multi-step (ex: "criar time → adicionar atleta → criar temporada"). Nenhum mecanismo executa esses workflows contra o código real. O `ARAZZO_VALIDATION_GATE` verifica que o YAML é válido, não que o workflow funciona. São documentação de intenção, não governança executável.

### 6. AsyncAPI — 68 eventos sem consumers reais
Os 68 canais AsyncAPI estão definidos e validados estruturalmente. Mas no código, eventos são emitidos via Celery tasks (`src/*/tasks.py`) sem aderência formal ao schema AsyncAPI. Não existe gate que verifique que o evento emitido pelo código conforma ao schema declarado no contrato.

### 7. FEATURE_REGISTRY com "21 implemented" sem teste de feature
As 21 features em status `implemented` no `FEATURE_REGISTRY.yaml` não têm testes de feature (acceptance tests) que provem que a feature funciona end-to-end. Os testes existentes são unitários (domínio) e de integração (API), não de feature.

---

## PARTE 6 — Gaps do Processo

### GAP-01: Schemathesis desligado no CI
**Severidade: CRÍTICA**
O único teste que prova conformidade contrato→código em runtime está excluído do CI com `--ignore=tests/schemathesis`. Motivo: timeout e dependência de banco. Sem esse teste, qualquer mudança em `api.py` ou `schemas.py` pode divergir do contrato sem detecção automática.

### GAP-02: Tooling ausente no CI degrada gates para ~20%
**Severidade: ALTA**
Os gates `OPENAPI_ROOT_STRUCTURE_GATE`, `OPENAPI_POLICY_RULESET_GATE`, `ASYNCAPI_VALIDATION_GATE`, `SPECTRAL_LINTING_GATE`, `REF_HERMETICITY_GATE`, `ARAZZO_COMPLETENESS_GATE` e mais ~30 gates são `SKIP_NOT_APPLICABLE` no CI porque `redocly`, `spectral` e `asyncapi` não estão instalados. A validação estrutural dos contratos **não é enforçada automaticamente**.

### GAP-03: Pipeline tests excluídos do CI
**Severidade: ALTA**
`--ignore=tests/pipeline_gates` exclui testes como `test_gate_registry_parity.py`, `test_architecture_drift.py`, `test_module_lifecycle_governance.py`. Esses testes verificam a integridade do **próprio** sistema CDD. Sem eles, o CDD pode degradar sem detecção.

### GAP-04: HANDOFF_COHERENCE_GATE falhando
**Severidade: MÉDIA**
O gate está detectando divergência entre `session_start.operation_mode='CDD'` e `SESSION_HANDOFF.modo_operacao='ROADMAP'`. Isso significa que o `session_start.json` não foi atualizado para refletir o modo atual. O gate funciona (detecta o problema), mas ninguém o corrigiu.

### GAP-05: Evidência de processo é retroativa
**Severidade: MÉDIA**
Os 17 `baseline_backfill.json` com `evidence_mode: baseline_backfill` satisfazem o `PRE_CONTRACT_EVIDENCE_GATE`, mas não provam que o pipeline CDD foi realmente executado para cada módulo em sequência. A rastreabilidade do processo de autoria é artificial.

### GAP-06: Status de módulo não regride
**Severidade: MÉDIA**
Quando a auditoria de auth (2026-03-27) descobriu que 13 módulos tinham stubs inseguros, os módulos permaneceram em `implemented`. Não houve regressão de status. O lifecycle normativo (`implemented` → `staging_validated` → `released`) não tem mecanismo de downgrade quando um bug grave é encontrado.

### GAP-07: Ausência de testes de contrato para eventos
**Severidade: MÉDIA**
Os 68 eventos AsyncAPI não têm testes que verifiquem que o código emite eventos conforme o schema declarado. Celery tasks existem, mas a conformidade é informal.

### GAP-08: Deploy sem evidência executável
**Severidade: MÉDIA**
Nenhum health check output, URL de staging, ou log de Schemathesis contra staging está registrado como artefato. O ROADMAP marca Fase 3 como DONE, mas a prova de que deploy funciona é declarativa.

### GAP-09: Fragmentação de handoff
**Severidade: BAIXA**
7 arquivos `SESSION_HANDOFF_*.md` na raiz sem consolidação. O principal `SESSION_HANDOFF.md` é o canônico, mas os outros criam confusão e não estão arquivados.

### GAP-10: Nenhum enforcement de feature end-to-end
**Severidade: BAIXA**
`FEATURE_REGISTRY` rastreia 31 features, mas não existe nem test suite de feature nem acceptance criteria executável que prove que cada feature funciona como descrita.

---

## PARTE 7 — Riscos Criados pelos Gaps

### Código fora de contrato (sem detecção)
**Risco: ALTO.** Com Schemathesis desligado no CI, qualquer PR que altere um endpoint, mude um schema Pydantic, ou adicione um campo pode criar divergência entre contrato OpenAPI e código sem que o CI detecte. Hoje o alinhamento existe porque o código foi gerado dos contratos, mas qualquer manutenção futura não tem rede de segurança automática.

### Decisão sem base (baixo risco atual)
**Risco: BAIXO.** As decisões arquiteturais estão bem documentadas em ADRs e Decision IRs. O risco existe apenas se o projeto crescer em número de contribuidores sem manter a disciplina de Decision Discovery.

### Retrabalho
**Risco: MÉDIO.** A ausência da auditoria auth por 8 dias (módulos promoted antes do fix) é um exemplo concreto. Sem validação de runtime contínua, bugs de conformidade acumulam e depois requerem varreduras manuais caras.

### Falsa sensação de governança
**Risco: ALTO.** O número "54 gates PASS" reportado no `latest.json` é tecnicamente verdadeiro (execução local), mas o CI só executa ~11 gates. O humano pode acreditar que todos os gates estão passando automaticamente, quando na verdade a maioria é skipped. Esse é o gap mais perigoso: o sistema relata governança que não está sendo enforçada.

### Progresso fake
**Risco: MÉDIO.** Os checkboxes do ROADMAP são marcados sem link para artefato de evidência. "✅ Schemathesis PASS para Ciclo 1" está marcado no ROADMAP, mas Schemathesis está excluído do CI e requer flag manual. Se alguém ler o ROADMAP, vai acreditar que Schemathesis é parte do pipeline automático.

### DONE incorreto
**Risco: MÉDIO.** O lifecycle `implemented` não garante que o módulo funciona em staging. A definição real de DONE para um módulo deveria ser `staging_validated` (deploy + health check + Schemathesis contra staging), mas nenhum módulo chegou formalmente a esse status.

### Drift entre artefatos
**Risco: MÉDIO (crescente).** Hoje o drift é mínimo porque o código é recente e foi gerado dos contratos. Mas sem Schemathesis no CI e sem gates de tooling, cada mudança manual no código aumenta a probabilidade de drift. O risco cresce proporcionalmente ao número de PRs sem validação de contrato.

### Perda de direção do agente
**Risco: BAIXO.** O `HANDOFF_COHERENCE_GATE` falhando é um sinal de que o estado da sessão está inconsistente. Se não for corrigido, o próximo agente pode carregar contexto errado (acreditar que está em modo CDD quando deveria estar em ROADMAP). Os boot profiles mitigam parcialmente.

---

## PARTE 8 — Veredito Final

### O CDD está funcionando como processo real?

**Parcialmente sim.** O CDD do HB Track não é teatro — os contratos realmente dirigiram a geração de código, a estrutura dos módulos, e as regras de domínio. A separação CDD/ROADMAP é inteligente e funcional. Os gates, quando executados com tooling completo, detectam problemas reais (o `HANDOFF_COHERENCE_GATE` falhando agora é prova disso).

Mas o CDD **não está fechado como ciclo**. Ele funciona de "contrato → código", mas não de "código → prova de conformidade contínua". É um CDD de **autoria**, não um CDD de **enforcement**.

### Quais partes já são efetivas?

1. **Contratos como SSOT de autoria** — genuinamente efetivo
2. **DOMAIN_AXIOMS como vocabulário controlado** — genuinamente efetivo
3. **Geração de código via worker** — produziu 17 módulos consistentes
4. **ROADMAP com fases e critérios de DONE** — instrumento real de progresso
5. **Clean Architecture consistente** — mantida em todos os módulos
6. **FSM e regras de domínio** — derivadas do contrato, enforçadas no código
7. **Separação CDD/ROADMAP** — evita bloqueio cruzado

### Quais partes ainda falham?

1. **Enforcement de contrato→código em CI** — desligado (Schemathesis + pipeline_gates)
2. **Cobertura de gates no CI** — 11/53 (tooling ausente)
3. **Evidência de processo** — retroativa e sintética
4. **Status de módulo sem regressão** — não reflete bugs descobertos post-promoção
5. **Conformidade de eventos** — AsyncAPI existe mas sem enforcement
6. **Deploy sem evidência** — declarativo sem artefato executável

### Menor conjunto de ajustes para tornar o CDD efetivo até o DONE

**5 ações, em ordem de prioridade:**

#### 1. Habilitar Schemathesis no CI (impacto: CRÍTICO)
Instalar `schemathesis` como dependência CI. Adicionar services PostgreSQL + Redis ao job de teste. Remover `--ignore=tests/schemathesis`. Usar `HB_RUN_SCHEMATHESIS=1` com `max_examples=10` (rápido o suficiente para CI). Isso fecha o gap mais importante: provar que o código conforma ao contrato em cada PR.

#### 2. Instalar tooling de contratos no CI (impacto: ALTO)
Adicionar `npx @redocly/cli`, `npx @stoplight/spectral-cli`, `npx @asyncapi/cli` ao job `validate` do CI. Isso eleva a cobertura de gates de 11 para ~42 (passagem de `SKIP_NOT_APPLICABLE` para execução real). Custo: ~2 minutos adicionais no CI.

#### 3. Remover `--ignore=tests/pipeline_gates` do CI (impacto: ALTO)
Corrigir os dois testes problemáticos (`test_session_state_phase3.py` com timeout, `test_ciclo1_contracts.py` com `django_db` marker) e habilitar a suite `pipeline_gates` no CI. Esses testes verificam a integridade do próprio CDD.

#### 4. Corrigir `HANDOFF_COHERENCE_GATE` (impacto: MÉDIO)
Atualizar `session_start.json` para refletir `operation_mode: ROADMAP` ou resetar a sessão. Isso restaura a coerência do estado de sessão e permite que o gate volte a PASS.

#### 5. Arquivar handoffs antigos (impacto: BAIXO)
Mover os 6 `SESSION_HANDOFF_*.md` da raiz para `_archive/`. Manter apenas `SESSION_HANDOFF.md` como canônico. Isso elimina confusão e reduz ruído para o próximo agente.

---

> **Conclusão**: O CDD do HB Track é um sistema de desenvolvimento genuinamente útil que precisa de **enforcement automático no CI** para cumprir a promessa de ser contract-driven de ponta a ponta. As 5 ações acima transformam um CDD de autoria forte + enforcement fraco em um CDD de ciclo completo. O investimento é pequeno (configuração de CI) e o retorno é alto (cada PR futura será validada contra os contratos que já existem e já são bons).
