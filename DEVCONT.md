# Auditoria de Continuidade de Desenvolvimento Assistido por IA — HB Track

> ⚠️ **ARTEFATO DERIVADO — NON-SOVEREIGN**: Este arquivo é uma auditoria derivada. Não possui autoridade normativa. Não deve ser usado para redefinir schemas, gates, contratos ou políticas canônicas. Em caso de conflito, prevalecem: `scripts/hb` + `validate_contracts.py` > `contracts/schemas/` > `docs/_canon/` > `.contract_driven/CONTRACT_SYSTEM_RULES.md` > este arquivo.

## PARTE 1 — Visão geral do desenvolvimento assistido por IA

Hoje o HB Track é conduzido por um sistema em camadas. A camada mais forte é a de **governança CDD**: o agente é orientado por boot instructions, regras de canonização, registries, gates, matrizes de autoridade e prompts operacionais. Essa camada está bem representada por [docs/_canon/AGENT_INSTRUCTIONS.md](/home/davis/HB-TRACK/docs/_canon/AGENT_INSTRUCTIONS.md#L5), [.contract_driven/CONTRACT_SYSTEM_RULES.md](/home/davis/HB-TRACK/.contract_driven/CONTRACT_SYSTEM_RULES.md#L26), [docs/_canon/CONTRACT_PIPELINE.md](/home/davis/HB-TRACK/docs/_canon/CONTRACT_PIPELINE.md#L11), [docs/_canon/gates/GATES_REGISTRY.yaml](/home/davis/HB-TRACK/docs/_canon/gates/GATES_REGISTRY.yaml#L1), [docs/_canon/MODULE_REGISTRY.yaml](/home/davis/HB-TRACK/docs/_canon/MODULE_REGISTRY.yaml#L1) e [.contract_driven/TASK_CATALOG.yaml](/home/davis/HB-TRACK/.contract_driven/TASK_CATALOG.yaml#L1).

Na prática, o desenvolvimento parece acontecer em dois modos. O modo **CDD** cria, valida e promove contratos até `implementation_ready`, com forte anti-inferência e gates explícitos ([docs/_canon/AGENT_INSTRUCTIONS.md](/home/davis/HB-TRACK/docs/_canon/AGENT_INSTRUCTIONS.md#L8), [.contract_driven/CONTRACT_SYSTEM_RULES.md](/home/davis/HB-TRACK/.contract_driven/CONTRACT_SYSTEM_RULES.md#L344)). O modo **ROADMAP** tenta assumir a partir daí a implementação por fases 0–13 ([ROADMAP.md](/home/davis/HB-TRACK/ROADMAP.md#L99), [.contract_driven/BOOT_PROFILES.yaml](/home/davis/HB-TRACK/.contract_driven/BOOT_PROFILES.yaml#L82), [.contract_driven/TASK_CATALOG.yaml](/home/davis/HB-TRACK/.contract_driven/TASK_CATALOG.yaml#L253)). O problema é que o primeiro modo está muito mais institucionalizado e testado do que o segundo.

As camadas que mais orientam a continuidade hoje são:

- **Boot e entrada de sessão:** [docs/_canon/AGENT_INSTRUCTIONS.md](/home/davis/HB-TRACK/docs/_canon/AGENT_INSTRUCTIONS.md#L5), [CLAUDE.md](/home/davis/HB-TRACK/CLAUDE.md#L5), [.github/copilot-instructions.md](/home/davis/HB-TRACK/.github/copilot-instructions.md#L20)
- **Norma soberana:** [.contract_driven/CONTRACT_SYSTEM_RULES.md](/home/davis/HB-TRACK/.contract_driven/CONTRACT_SYSTEM_RULES.md#L26), [.contract_driven/CONTRACT_SYSTEM_LAYOUT.md](/home/davis/HB-TRACK/.contract_driven/CONTRACT_SYSTEM_LAYOUT.md#L1)
- **Roteamento e boot por tarefa:** [.contract_driven/BOOT_PROFILES.yaml](/home/davis/HB-TRACK/.contract_driven/BOOT_PROFILES.yaml#L14), [.contract_driven/TASK_CATALOG.yaml](/home/davis/HB-TRACK/.contract_driven/TASK_CATALOG.yaml#L218)
- **Validação e promoção:** [docs/_canon/CONTRACT_PIPELINE.md](/home/davis/HB-TRACK/docs/_canon/CONTRACT_PIPELINE.md#L11), [docs/_canon/gates/GATES_REGISTRY.yaml](/home/davis/HB-TRACK/docs/_canon/gates/GATES_REGISTRY.yaml#L1), [scripts/contracts/validate/validate_contracts.py](/home/davis/HB-TRACK/scripts/contracts/validate/validate_contracts.py#L6946)
- **Estado e continuidade:** [SESSION_HANDOFF.md](/home/davis/HB-TRACK/SESSION_HANDOFF.md#L1), [_reports/session_start.json](/home/davis/HB-TRACK/_reports/session_start.json), [_reports/READINESS_DASHBOARD.md](/home/davis/HB-TRACK/_reports/READINESS_DASHBOARD.md#L1), [ROADMAP.md](/home/davis/HB-TRACK/ROADMAP.md#L64)

Os arquivos mais importantes para continuidade segura hoje são:

- [docs/_canon/AGENT_INSTRUCTIONS.md](/home/davis/HB-TRACK/docs/_canon/AGENT_INSTRUCTIONS.md#L5)
- [.contract_driven/CONTRACT_SYSTEM_RULES.md](/home/davis/HB-TRACK/.contract_driven/CONTRACT_SYSTEM_RULES.md#L26)
- [.contract_driven/BOOT_PROFILES.yaml](/home/davis/HB-TRACK/.contract_driven/BOOT_PROFILES.yaml#L14)
- [.contract_driven/TASK_CATALOG.yaml](/home/davis/HB-TRACK/.contract_driven/TASK_CATALOG.yaml#L218)
- [docs/_canon/MODULE_REGISTRY.yaml](/home/davis/HB-TRACK/docs/_canon/MODULE_REGISTRY.yaml#L9)
- [ROADMAP.md](/home/davis/HB-TRACK/ROADMAP.md#L99)
- [SESSION_HANDOFF.md](/home/davis/HB-TRACK/SESSION_HANDOFF.md#L4)

Resumo objetivo: o repositório já tem um **sistema de governança de agente** real e sofisticado, mas ele está muito maduro até `implementation_ready` e ainda parcialmente desalinhado para conduzir a fase pós-contrato até o `DONE` do produto.

## PARTE 2 — Arquivos que governam o agente

| Arquivo | Papel no desenvolvimento | Tipo de influência | Impacto na continuidade | Risco se estiver fraco |
|--------|---------------------------|--------------------|-------------------------|------------------------|
| `docs/_canon/AGENT_INSTRUCTIONS.md` | Entry point global do agente, separa modo CDD e modo ROADMAP | instrução | Alto | agente mistura modos, carrega contexto errado ou ignora bloqueios |
| `.contract_driven/CONTRACT_SYSTEM_RULES.md` | Define precedência, anti-inferência, canonização em 3 níveis e bloqueios | governança | Muito alto | alucinação de regra, desvio de escopo, prompt virar pseudo-SSOT |
| `.contract_driven/CONTRACT_SYSTEM_LAYOUT.md` | Define paths canônicos e soberania de artefatos | governança | Alto | drift de paths, criação em local errado, duplicação soberana |
| `docs/_canon/CONTRACT_PIPELINE.md` | Define estágios oficiais, evidências e condição de avanço | roteamento | Alto | agente pula estágio ou promove artefato sem evidência |
| `.contract_driven/BOOT_PROFILES.yaml` | Define que contexto deve ser carregado por tipo de tarefa | roteamento | Muito alto | boot incompleto, leitura errada de contexto, continuidade frágil |
| `.contract_driven/TASK_CATALOG.yaml` | Mapeia task types para workers, status e artefatos produzidos | roteamento | Muito alto | worker errado, task inexistente, avanço em fluxo não suportado |
| `docs/_canon/gates/GATES_REGISTRY.yaml` | Registro oficial dos gates e do que cada um bloqueia | validação | Alto | falsa sensação de PASS sem cobertura real |
| `docs/_canon/MODULE_REGISTRY.yaml` | Define maturidade operacional e superfícies esperadas por módulo | estado/progresso | Muito alto | agente não sabe o que já está pronto nem o que promover |
| `docs/_canon/MODULE_SOURCE_AUTHORITY_MATRIX.yaml` | Define limites de inferência por módulo e fontes permitidas | governança | Alto | invenção de requisitos de domínio, benchmark virar regra |
| `.contract_driven/agent_prompts/pre_contract_orchestrator.prompt.md` | Orquestra entrada do fluxo CDD e publicação de evidência inicial | instrução | Médio/alto | trabalho contratual sem pré-contrato válido |
| `.contract_driven/agent_prompts/readiness_promotion.prompt.md` | Define promoção para `implementation_ready` e gate humano | definição de DONE | Alto | promoção indevida, handoff incompleto, readiness sem lastro |
| `.contract_driven/agent_prompts/generate_code.prompt.md` | Diz ao agente como materializar código a partir do contrato | instrução | Muito alto | código em estrutura errada, inconsistência arquitetural |
| `.contract_driven/agent_prompts/execute_roadmap_phase.prompt.md` | Tenta conduzir a implementação por fases pós-CDD | instrução | Muito alto | agente não sabe sequência operacional até v1.0 |
| `contracts/schemas/shared/session_start.schema.json` | Contrato da evidência de boot/sessão | validação | Alto | continuidade não rastreável, runtime e schema divergirem |
| `contracts/schemas/shared/session_handoff.schema.json` | Contrato auxiliar para handoff estruturado, mas não é o validador ativo | handoff | Médio | aparência de formalização sem enforcement real |
| `scripts/hb` | CLI operacional do fluxo CDD e da evidência de sessão | validação | Alto | execução aceita estado incoerente ou rejeita fluxo suportado |
| `scripts/contracts/validate/validate_contracts.py` | Enforcement real dos gates e da coerência geral | validação | Muito alto | governança vira documentação sem efeito |
| `SESSION_HANDOFF.md` | Handoff operacional corrente entre sessões | handoff | Muito alto | próxima sessão repete trabalho, perde contexto ou escolhe próxima ação errada |
| `ROADMAP.md` | Plano operacional pós-CDD até versões do produto | estado/progresso | Muito alto | agente fica sem roteiro para infra, frontend, deploy e release |
| `_reports/READINESS_DASHBOARD.md` | Snapshot derivado do readiness global | estado/progresso | Médio | progresso parecer melhor do que realmente está |
| `_reports/feature_readiness.json` | Snapshot derivado de features | estado/progresso | Médio | priorização por feature ficar obsoleta |
| `FINAL_HANDOFF.md` | Fechamento da remediação contratual CDD | contexto | Médio | agente interpretar “CDD concluído” como “produto concluído” |

## PARTE 3 — Avaliação anti-alucinação

### Avaliação qualitativa

**Implementação fora do escopo:** a configuração atual reduz bem esse risco no modo CDD. Há taxonomia fechada de módulos, matrizes de autoridade e regra explícita de “artefato ausente => bloquear” ([.contract_driven/CONTRACT_SYSTEM_RULES.md](/home/davis/HB-TRACK/.contract_driven/CONTRACT_SYSTEM_RULES.md#L344), [docs/_canon/MODULE_REGISTRY.yaml](/home/davis/HB-TRACK/docs/_canon/MODULE_REGISTRY.yaml#L31), [docs/_canon/MODULE_SOURCE_AUTHORITY_MATRIX.yaml](/home/davis/HB-TRACK/docs/_canon/MODULE_SOURCE_AUTHORITY_MATRIX.yaml)).

**Invenção de requisitos:** o risco é baixo a moderado em contratos, mas sobe na implementação porque há conflito entre artefatos que deveriam ser soberanos. Exemplo: o backend real/canônico aparece em `src/` no [docs/_canon/CODE_ARCHITECTURE.md](/home/davis/HB-TRACK/docs/_canon/CODE_ARCHITECTURE.md#L60), mas `generate_code`, `TASK_CATALOG`, skill e guardas ainda apontam para `backend/apps` ([.contract_driven/TASK_CATALOG.yaml](/home/davis/HB-TRACK/.contract_driven/TASK_CATALOG.yaml#L230), [.contract_driven/agent_prompts/generate_code.prompt.md](/home/davis/HB-TRACK/.contract_driven/agent_prompts/generate_code.prompt.md#L11), [.github/instructions/hb-contract-guards.instructions.md](/home/davis/HB-TRACK/.github/instructions/hb-contract-guards.instructions.md#L2), [scripts/hooks/check_backend_gate.py](/home/davis/HB-TRACK/scripts/hooks/check_backend_gate.py#L3)).

**Criação de código sem base contratual/documental:** o modo CDD cobre bem esse ponto. Já o modo ROADMAP ainda não está fechado no enforcement. O próprio repositório declara `roadmap_execution` em [BOOT_PROFILES.yaml](/home/davis/HB-TRACK/.contract_driven/BOOT_PROFILES.yaml#L82) e `execute_roadmap_phase` em [TASK_CATALOG.yaml](/home/davis/HB-TRACK/.contract_driven/TASK_CATALOG.yaml#L253), mas o contrato de sessão ainda não aceita esse profile nem esse task type ([contracts/schemas/shared/session_start.schema.json](/home/davis/HB-TRACK/contracts/schemas/shared/session_start.schema.json#L47)). Evidência executada na auditoria:

```text
python3 scripts/hb verify --task-type execute_roadmap_phase --module training
❌ Sessão inválida: 'roadmap_execution' is not one of ['default', 'contract_execution', 'architecture_decision', 'diagnostic']
```

**Deriva entre módulos:** o risco é moderado. Há gates e boundaries fortes, mas coexistem documentos antigos e novos com stacks e caminhos diferentes. Isso abre espaço para o agente obedecer ao artefato errado.

**Decisões não rastreáveis:** o risco é moderado. Existe rastreabilidade boa em `_reports/`, `pipeline_history`, `session_start` e dashboards. Mas o handoff operacional continua textual, o schema de handoff não é o validador ativo ([.github/copilot-instructions.md](/home/davis/HB-TRACK/.github/copilot-instructions.md#L61), [contracts/schemas/shared/session_handoff.schema.json](/home/davis/HB-TRACK/contracts/schemas/shared/session_handoff.schema.json#L1)), e o gate atual de handoff é raso ([scripts/contracts/validate/validate_contracts.py](/home/davis/HB-TRACK/scripts/contracts/validate/validate_contracts.py#L6946)).

**Continuidade inconsistente entre sessões:** o risco é alto. O `SESSION_HANDOFF.md` deveria ser delta-only, mas hoje concentra histórico longo e conflita com o budget de consumo da própria suíte. Evidência executada:

```text
./.venv/bin/pytest -q tests/pipeline_gates/test_context_budgets_and_parity.py::TestContextBudgets
FAILED: SESSION_HANDOFF.md is 6624w, budget is 350w
FAILED: Total is 7688w, max budget is 2100w
```

O budget esperado está definido em [tests/pipeline_gates/test_context_budgets_and_parity.py](/home/davis/HB-TRACK/tests/pipeline_gates/test_context_budgets_and_parity.py#L15).

**Regressões por falta de contexto de progresso:** o risco é alto. O sistema sabe muito bem o que é `implementation_ready`, mas não tem uma trilha igualmente forte para `implemented`, `staging_validated` e `released` no nível de módulo. O [MODULE_REGISTRY.yaml](/home/davis/HB-TRACK/docs/_canon/MODULE_REGISTRY.yaml#L9) para em `implementation_ready`. O [FEATURE_REGISTRY.yaml](/home/davis/HB-TRACK/docs/_canon/FEATURE_REGISTRY.yaml#L6) vai até `released`, mas só no nível de feature, e o snapshot derivado [_reports/feature_readiness.json](/home/davis/HB-TRACK/_reports/feature_readiness.json#L1) está obsoleto e mostra apenas 10 features de `training`.

### Notas (0 a 100)

| Critério | Nota |
|---|---:|
| clareza de instrução | 82 |
| restrição de escopo | 84 |
| rastreabilidade | 72 |
| continuidade entre sessões | 54 |
| definição de progresso | 61 |
| definição de DONE | 66 |
| capacidade de priorização | 58 |
| resistência à alucinação | 68 |

Leitura dessas notas:

- O **CDD** está bem blindado.
- A **ponte CDD → implementação → release** ainda está incompleta.
- O maior risco não é “o agente inventar um endpoint”, e sim **seguir o artefato errado, perder o estado operacional ou interpretar `implementation_ready` como `DONE`**.

## PARTE 4 — Gaps que impedem continuidade segura até o DONE

### O que ainda está faltando

- **Fechamento do modo ROADMAP no enforcement real.**
  Hoje ele existe em instruções e registries, mas não fecha no schema/runtime de sessão. `BOOT_PROFILES` já conhece `roadmap_execution`, mas [session_start.schema.json](/home/davis/HB-TRACK/contracts/schemas/shared/session_start.schema.json#L47) não.

- **Estado operacional machine-readable da implementação.**
  O sistema tem `implementation_ready`, mas não tem um SSOT equivalente de módulo para `implemented`, `staging_validated` e `released`.

- **Fase atual e próxima ação persistidas de forma estruturada.**
  O skill de roadmap espera handoff com `Fase ROADMAP` e `Resultado` ([.github/skills/hb-roadmap-executor/SKILL.md](/home/davis/HB-TRACK/.github/skills/hb-roadmap-executor/SKILL.md#L123)), mas o [SESSION_HANDOFF.md](/home/davis/HB-TRACK/SESSION_HANDOFF.md#L4) atual não carrega esse cabeçalho operacional.

- **Sincronização dos artefatos de progresso.**
  [_reports/feature_readiness.json](/home/davis/HB-TRACK/_reports/feature_readiness.json#L1) não reflete o estado atual descrito em [ROADMAP.md](/home/davis/HB-TRACK/ROADMAP.md#L64) e em [FEATURE_REGISTRY.yaml](/home/davis/HB-TRACK/docs/_canon/FEATURE_REGISTRY.yaml#L6).

### O que está ambíguo

- **Stack de frontend.**
  [docs/_canon/ARCHITECTURE.md](/home/davis/HB-TRACK/docs/_canon/ARCHITECTURE.md#L70) e [ROADMAP.md](/home/davis/HB-TRACK/ROADMAP.md#L77) apontam para React + Vite; [docs/_canon/CODE_ARCHITECTURE.md](/home/davis/HB-TRACK/docs/_canon/CODE_ARCHITECTURE.md#L23) ainda fala em Next.js 14; [README.md](/home/davis/HB-TRACK/README.md#L23) ainda fala em FastAPI + Next.js 13+.

- **Estrutura canônica do backend.**
  O canon atual aponta `src/` ([docs/_canon/CODE_ARCHITECTURE.md](/home/davis/HB-TRACK/docs/_canon/CODE_ARCHITECTURE.md#L60)), mas o fluxo de geração e guardas ainda apontam `backend/apps/` ([.contract_driven/TASK_CATALOG.yaml](/home/davis/HB-TRACK/.contract_driven/TASK_CATALOG.yaml#L230), [.contract_driven/agent_prompts/generate_code.prompt.md](/home/davis/HB-TRACK/.contract_driven/agent_prompts/generate_code.prompt.md#L11), [scripts/hooks/check_backend_gate.py](/home/davis/HB-TRACK/scripts/hooks/check_backend_gate.py#L79)).

- **Escopo do “done final”.**
  [FINAL_HANDOFF.md](/home/davis/HB-TRACK/FINAL_HANDOFF.md#L13) declara “100/100 em robustez contratual CDD”, o que é verdadeiro para a remediação contratual, mas não equivale ao `DONE` do produto descrito em [ROADMAP.md](/home/davis/HB-TRACK/ROADMAP.md#L21).

### O que depende demais de inferência

- Inferir **qual fase do roadmap vem agora** a partir de texto livre.
- Inferir **qual artefato de arquitetura está mais atualizado** quando README, ARCHITECTURE, CODE_ARCHITECTURE, prompts e guards divergem.
- Inferir **se o sistema já está em “implementado” ou apenas “implementation_ready”**.
- Inferir **qual dashboard de progresso é confiável** quando há múltiplos snapshots e alguns estão obsoletos.

### O que pode fazer o agente travar, repetir trabalho ou inventar próximos passos

- `SESSION_HANDOFF.md` excessivamente longo e histórico demais.
- `ROADMAP.md` existente, mas ainda não fechado no schema/CLI/handoff.
- `ROADMAP.md` e `hb-roadmap-executor` estarem presentes no workspace, porém o `git status --short` mostra ambos como não rastreados, o que reduz continuidade real entre clones/sessões.
- Artefatos roadmap-like concorrentes e conflitantes, como [docs/guias/MODULE_ROADMAP_2026_03_17.md](/home/davis/HB-TRACK/docs/guias/MODULE_ROADMAP_2026_03_17.md#L1), que ainda mostra 15 módulos `validated_contract`, 1 `implementation_ready` e 1 `draft_contract`, enquanto o registry oficial já está em 17 `implementation_ready` ([docs/_canon/MODULE_REGISTRY.yaml](/home/davis/HB-TRACK/docs/_canon/MODULE_REGISTRY.yaml#L31)).
- Guardas/hook de backend desalinhados com a estrutura real e em `fail-open` em caso de erro ([scripts/hooks/check_backend_gate.py](/home/davis/HB-TRACK/scripts/hooks/check_backend_gate.py#L110)).

## PARTE 5 — Avaliação sobre ROADMAP.md

### Resposta objetiva

- **devo criar ROADMAP.md?** sim
- **por quê?** porque existe uma lacuna operacional real entre “contratos prontos” e “produto entregue”, e essa lacuna não é coberta pelo CDD puro
- **qual problema concreto ele resolveria?** sequenciamento determinístico da implementação, infraestrutura, frontend, deploy e releases
- **esse problema já é resolvido por arquivos existentes?** parcialmente, mas de forma incompleta e hoje ainda não totalmente integrada
- **ROADMAP.md adicionaria controle real, clareza de progresso e direção para o agente, ou seria redundante?** adiciona controle real se for promovido e integrado ao enforcement; seria redundante apenas se virar mais um documento paralelo

### Interpretação correta nesta auditoria

O ponto importante é este: **o arquivo já existe no workspace**, e ele é útil. Então a recomendação não é “criar outro roadmap”. A recomendação é **institucionalizar o ROADMAP operacional já existente**. Sem isso, o agente continua muito forte para contrato e relativamente solto para continuar até v0.1/v0.2/v1.0.

### Função exata do ROADMAP.md

Ser o **SSOT operacional pós-CDD** para responder, sem inferência:

- em que fase o produto está
- o que entra e sai de cada fase
- qual é a próxima ação permitida
- qual evidência fecha a fase
- quando uma fase está `DONE`

### O que ele deve conter

- visão de releases e ciclos de valor
- estado atual consolidado do produto
- fases ordenadas com dependências explícitas
- critério de entrada e critério de done por fase
- paths canônicos dos artefatos de implementação por fase
- testes/evidências mínimas por fase
- bloqueios humanos obrigatórios
- relação fase → módulo/feature/evidência

### O que ele não deve conter

- histórico longo de sessões
- duplicação de regras de domínio, invariantes ou contratos de módulo
- racional arquitetural já decidido em ADR
- lista narrativa de mudanças antigas
- snapshots concorrentes de status já cobertos por dashboards derivados

### Como ele deve se relacionar com os arquivos já existentes

- **`AGENT_INSTRUCTIONS.md` / `CLAUDE.md` / `copilot-instructions.md`**: apontam para ele como entrada do modo ROADMAP
- **`BOOT_PROFILES.yaml`**: carrega o profile `roadmap_execution`
- **`TASK_CATALOG.yaml`**: referencia `execute_roadmap_phase`
- **`SESSION_HANDOFF.md`**: guarda apenas delta operacional da fase corrente
- **`MODULE_REGISTRY.yaml`**: continua como maturidade contratual/técnica por módulo
- **`FEATURE_REGISTRY.yaml`**: continua como progresso por feature
- **`_reports/*`**: continuam como derivados, nunca como SSOT do plano

Conclusão desta parte: **sim, o ROADMAP é necessário**, mas o repositório já aponta para isso. O trabalho certo agora é **promover, rastrear e fechar as integrações do ROADMAP atual**, não inventar um novo artefato paralelo.

## PARTE 6 — Veredito final

### Resposta objetiva

- **a configuração atual permite continuar o desenvolvimento do HB Track com segurança até o DONE?** parcialmente
- **quais são os principais bloqueadores restantes?**
  - modo ROADMAP não está fechado no schema/runtime/evidência
  - conflitos entre artefatos que o agente usa para arquitetura, stack e paths
  - ausência de estado estruturado da fase atual e próxima ação
  - ausência de lifecycle pós-`implementation_ready` no nível de módulo
  - handoff operacional superdimensionado e já reprovado pela própria suíte
- **qual é o conjunto de ajustes determinísticos necessários para deixar o agente apto a continuar sem alucinar?**
  - consolidar o modo ROADMAP como fluxo oficialmente validado
  - eliminar conflitos de stack e estrutura de código
  - transformar fase atual/próxima ação em estado estruturado
  - reduzir o handoff a delta consumível
  - alinhar dashboards derivados com o estado real

### Veredito técnico

O HB Track tem **governança suficiente para não alucinar fortemente no domínio contratual**, mas **ainda não tem governança suficientemente fechada para garantir continuidade segura até o DONE do produto sem depender de interpretação humana**.

Hoje o agente:

- sabe muito bem **como não inventar contrato**
- sabe razoavelmente **como validar readiness contratual**
- ainda não sabe de forma totalmente determinística **como atravessar implementação, integração, frontend, deploy e release sem cair em artefatos conflitantes ou estado operacional ambíguo**

### Plano de correção com fases e checklist

#### Fase 0 — Congelar a autoridade operacional

- [x] Confirmar que o **ROADMAP operacional atual** será o artefato oficial do modo implementação
- [x] Adicionar `ROADMAP.md` ao controle de versão se ele ainda estiver apenas no worktree
- [x] Adicionar `.github/skills/hb-roadmap-executor/` ao controle de versão se ele ainda estiver apenas no worktree
- [x] Arquivar ou desautorizar explicitamente artefatos concorrentes de roadmap/status como [docs/guias/MODULE_ROADMAP_2026_03_17.md](/home/davis/HB-TRACK/docs/guias/MODULE_ROADMAP_2026_03_17.md#L1)
- [x] Escopar [FINAL_HANDOFF.md](/home/davis/HB-TRACK/FINAL_HANDOFF.md#L13) explicitamente como “conclusão da remediação CDD”, não “DONE do produto”

#### Fase 1 — Reconciliar canon e prompts

- [x] Escolher uma única stack de frontend e propagar para [docs/_canon/ARCHITECTURE.md](/home/davis/HB-TRACK/docs/_canon/ARCHITECTURE.md#L57), [docs/_canon/CODE_ARCHITECTURE.md](/home/davis/HB-TRACK/docs/_canon/CODE_ARCHITECTURE.md#L13), [README.md](/home/davis/HB-TRACK/README.md#L30) e [ROADMAP.md](/home/davis/HB-TRACK/ROADMAP.md#L64)
- [x] Corrigir [docs/_canon/CODE_ARCHITECTURE.md](/home/davis/HB-TRACK/docs/_canon/CODE_ARCHITECTURE.md#L187) removendo o bloco legado FastAPI/SQLAlchemy duplicado
- [x] Fixar `src/` como único path canônico de backend em:
  - [docs/_canon/CODE_ARCHITECTURE.md](/home/davis/HB-TRACK/docs/_canon/CODE_ARCHITECTURE.md#L60)
  - [.contract_driven/TASK_CATALOG.yaml](/home/davis/HB-TRACK/.contract_driven/TASK_CATALOG.yaml#L230)
  - [.contract_driven/agent_prompts/generate_code.prompt.md](/home/davis/HB-TRACK/.contract_driven/agent_prompts/generate_code.prompt.md#L11)
  - [.github/instructions/hb-contract-guards.instructions.md](/home/davis/HB-TRACK/.github/instructions/hb-contract-guards.instructions.md#L2)
  - [scripts/hooks/check_backend_gate.py](/home/davis/HB-TRACK/scripts/hooks/check_backend_gate.py#L79)
  - [.github/skills/hb-roadmap-executor/SKILL.md](/home/davis/HB-TRACK/.github/skills/hb-roadmap-executor/SKILL.md#L100)

#### Fase 2 — Fechar o runtime do modo ROADMAP

- [x] Atualizar [contracts/schemas/shared/session_start.schema.json](/home/davis/HB-TRACK/contracts/schemas/shared/session_start.schema.json#L47) para aceitar `roadmap_execution`
- [x] Atualizar o mesmo schema para aceitar `execute_roadmap_phase`
- [x] Revisar `write_scope` para contemplar infra/frontend/mobile/deploy quando em modo ROADMAP
- [x] Atualizar [scripts/hb](/home/davis/HB-TRACK/scripts/hb#L308) para não gravar `write_scope: "contracts"` para toda tarefa
- [x] Decidir deterministicamente uma das duas opções:
  - [x] opção A: `scripts/hb` passa a suportar oficialmente `execute_roadmap_phase`
  - [x] opção B: descartada por decisão operacional; o runtime oficial do modo ROADMAP permanece integrado a `scripts/hb`
- [x] Criar testes de paridade boot/schema para o modo ROADMAP

#### Fase 3 — Estruturar continuidade entre sessões

- [x] Reduzir [SESSION_HANDOFF.md](/home/davis/HB-TRACK/SESSION_HANDOFF.md#L1) a um handoff realmente delta-only
- [x] Fazer `SESSION_HANDOFF.md` voltar a passar no budget da suíte ([tests/pipeline_gates/test_context_budgets_and_parity.py](/home/davis/HB-TRACK/tests/pipeline_gates/test_context_budgets_and_parity.py#L15))
- [x] Promover o handoff para uma estrutura mínima obrigatória e validável por gate, preferencialmente com front matter YAML no topo de [SESSION_HANDOFF.md](/home/davis/HB-TRACK/SESSION_HANDOFF.md#L1)
  - [x] `fase_roadmap`
  - [x] `task_id`
  - [x] `resultado`
  - [x] `proxima_acao_permitida`
  - [x] `bloqueios_ativos`
- [x] Atualizar [docs/_canon/templates/SESSION_HANDOFF.template.md](/home/davis/HB-TRACK/docs/_canon/templates/SESSION_HANDOFF.template.md#L1) e [SESSION_HANDOFF.md](/home/davis/HB-TRACK/SESSION_HANDOFF.md#L1) para usar exatamente a mesma estrutura obrigatória
- [x] Atualizar o `HANDOFF_COHERENCE_GATE` em [scripts/contracts/validate/validate_contracts.py](/home/davis/HB-TRACK/scripts/contracts/validate/validate_contracts.py#L6960) para parsear e validar essa estrutura, em vez de depender só de convenção textual rasa
- [x] Alinhar [contracts/schemas/shared/session_handoff.schema.json](/home/davis/HB-TRACK/contracts/schemas/shared/session_handoff.schema.json#L1) e [docs/_canon/gates/GATES_REGISTRY.yaml](/home/davis/HB-TRACK/docs/_canon/gates/GATES_REGISTRY.yaml#L260) ao enforcement real: se o schema continuar auxiliar, isso deve ficar explícito e sem promessa de validação ativa; se virar ativo, o gate deve consumi-lo de fato

#### Fase 4 — Definir progresso até o DONE

- [x] Estender o lifecycle de progresso para além de `implementation_ready`
- [x] Definir um SSOT explícito para os estados canônicos pós-`implementation_ready`:
  - [x] `implemented`
  - [x] `staging_validated`
  - [x] `released`
- [x] Descartar os rótulos não canônicos `integration_validated` e `staging_ready`; quando necessários, tratá-los como evidência operacional ou terminologia legada, nunca como novos estados oficiais
- [x] Decidir se esses estados viverão em `MODULE_REGISTRY.yaml`, em novo registry operacional ou em ambos com responsabilidades distintas
- [x] Ligar cada estado a evidência objetiva e gate correspondente
- [x] Regenerar snapshots derivados como [_reports/feature_readiness.json](/home/davis/HB-TRACK/_reports/feature_readiness.json#L1) para refletir o estado real

#### Fase 5 — Remover ambiguidades residuais

- [x] Ajustar [README.md](/home/davis/HB-TRACK/README.md#L17) para não contradizer o canon
- [x] Revisar [FINAL_HANDOFF.md](/home/davis/HB-TRACK/FINAL_HANDOFF.md#L138) e remover recomendações conflitantes com o estado atual do `TASK_CATALOG`
- [x] Classificar explicitamente `docs/guias/` como material humano de estudo/ideação, não canônico e não soberano, e `_reports/` como artefatos derivados/evidência
- [x] Criar `README` de raiz em `docs/guias/` e `_reports/` com disclaimer operacional claro para impedir leitura desses diretórios como SSOT
- [x] Remover linguagem de SSOT/autoridade dos guias que ainda a usam, em especial:
  - [x] [docs/guias/IDENTITY_RBAC.md](/home/davis/HB-TRACK/docs/guias/IDENTITY_RBAC.md#L1)
  - [x] [docs/guias/MVP_SCOPE.md](/home/davis/HB-TRACK/docs/guias/MVP_SCOPE.md#L1)
  - [x] [docs/guias/USER_PROFILES.md](/home/davis/HB-TRACK/docs/guias/USER_PROFILES.md#L1)
- [x] Revisar todas as referências de `docs/_canon/**` para `docs/guias/**` e remover qualquer delegação normativa; quando a referência for mantida, ela deve ser explicitamente marcada como apoio não canônico
  - [x] Corrigir [docs/_canon/SYSTEM_SCOPE.md](/home/davis/HB-TRACK/docs/_canon/SYSTEM_SCOPE.md#L30)
  - [x] Corrigir [docs/_canon/GLOBAL_INVARIANTS.md](/home/davis/HB-TRACK/docs/_canon/GLOBAL_INVARIANTS.md#L35)
- [x] Estender o `SHADOW_AUTHORITY_GATE` em [scripts/contracts/validate/validate_contracts.py](/home/davis/HB-TRACK/scripts/contracts/validate/validate_contracts.py#L4621) para cobrir `docs/guias/**`, não só `docs/hbtrack/decisoes/**`
- [x] Corrigir em [docs/_canon/ARCHITECTURE.md](/home/davis/HB-TRACK/docs/_canon/ARCHITECTURE.md#L226) a referência inexistente `docs/_canon/contratos/Ambiente.md`, apontando para artefato real ou removendo a falsa SSOT de infraestrutura

#### Fase 6 — Revalidar deterministicamente

- [x] Rodar `./.venv/bin/pytest -q tests/pipeline_gates/test_context_budgets_and_parity.py`
- [x] Rodar a survival suite de governança
- [x] Rodar `python3 scripts/contracts/validate/validate_contracts.py`
- [x] Rodar smoke test do modo ROADMAP sem erro de schema/profile
- [x] Após concluir as pendências das Fases 3 e 5, rerodar a bateria de governança:
  - [x] `./.venv/bin/pytest -q tests/pipeline_gates/test_context_budgets_and_parity.py`
  - [x] survival suite de governança
  - [x] `python3 scripts/contracts/validate/validate_contracts.py`
  - [x] smoke test do modo ROADMAP
- [x] Substituir o critério genérico de “repo limpo” por uma allowlist explícita de governança crítica e fechar a auditoria apenas quando esse conjunto estiver limpo e versionado:
  - [x] `docs/_canon/**`
  - [x] `.contract_driven/**`
  - [x] `contracts/schemas/shared/**`
  - [x] `scripts/hb`
  - [x] `scripts/contracts/validate/validate_contracts.py`
  - [x] `scripts/hooks/check_backend_gate.py`
  - [x] `SESSION_HANDOFF.md`
  - [x] `ROADMAP.md`
  - [x] `DEVCONT.md`
  - [x] `tests/pipeline_gates/**`
  - [x] `generated/manifests/**`
  - [x] `generated/contracts/schemas/shared/**`
  - [x] `_reports/contract_gates/latest.json`

### Fechamento executivo

Se você quer que o agente continue até o `DONE` **sem alucinar, sem desviar do escopo e sem perder consistência**, o repositório já tem uma base forte, mas ainda precisa de uma última consolidação: **transformar o ROADMAP de documento útil em mecanismo operacional tão robusto quanto o CDD**.

Hoje o sistema está pronto para continuar **com supervisão cuidadosa**. Depois das correções acima, ele passa a estar pronto para continuar **com continuidade operacional muito mais segura e bem menos dependente de interpretação humana**.
