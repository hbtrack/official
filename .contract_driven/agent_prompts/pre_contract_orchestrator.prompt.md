## Prompt Operacional — Orquestrador Pré-Contrato

**Objetivo**: executar a fase pré-contrato completa do HB Track antes de qualquer modo de criação ou revisão de contrato. Este prompt é o **ponto de entrada obrigatório** para toda tarefa de contratos.

**Regra de autoridade**:
- este prompt operacionaliza o canon;
- regras substantivas vivem em `.contract_driven/CONTRACT_SYSTEM_RULES.md`,
  `.contract_driven/CONTRACT_SYSTEM_LAYOUT.md`, `docs/_canon/CONTRACT_PIPELINE.md`,
  `docs/_canon/BOOT_PROFILES.md` e, quando aplicável, `docs/_canon/gates/GATES_REGISTRY.yaml`;
- se uma instrução deste prompt não estiver sustentada por esses artefatos, bloquear em vez de inferir.

Baseado nos padrões do InfoQ Agentic AI Architecture Framework (Foundation Tier + Workflow Tier):
- **Foundation Tier**: establece governança, transparência de raciocínio e lifecycle de dados antes de dar continuidade.
- **Workflow Tier**: implementa Prompt Chaining, Routing, Evaluator e Orchestrator-Workers.

---

### Entrada esperada (do humano)

| Campo | Obrigatório | Valores aceitos |
|-------|-------------|-----------------|
| `module` | sim | lower_snake_case — deve existir na taxonomia LAYOUT §2 |
| `task_type` | sim | `new_module` \| `new_contract` \| `contract_revision` \| `new_event` \| `new_workflow` \| `new_schema` \| `new_state_model` \| `new_ui_contract` \| `architecture_review` |
| `resource` | condicional | Entidade alvo (obrigatório para `new_contract`, `contract_revision`) |
| `scope_description` | recomendado | Descrição livre do que precisa ser feito |

---

### Mapa de roteamento (padrão Routing)

Com base em `task_type`, o orquestrador roteia para o worker correto após a fase pré-contrato:

| task_type | Worker prompt |
|-----------|--------------|
| `new_module` | `.contract_driven/agent_prompts/create_module_docs.prompt.md` |
| `new_contract` | `.contract_driven/agent_prompts/create_openapi_contract.prompt.md` |
| `contract_revision` | `.contract_driven/agent_prompts/create_openapi_contract.prompt.md` |
| `new_event` | `.contract_driven/agent_prompts/create_asyncapi_contract.prompt.md` |
| `new_workflow` | `.contract_driven/agent_prompts/create_arazzo_workflow.prompt.md` |
| `new_schema` | `.contract_driven/agent_prompts/create_json_schema_contract.prompt.md` |
| `new_state_model` | `.contract_driven/agent_prompts/create_state_model.prompt.md` |
| `new_ui_contract` | `.contract_driven/agent_prompts/create_ui_contract.prompt.md` |
| `architecture_review` | `.contract_driven/agent_prompts/decision_discovery.prompt.md` |

---

### Pré-Fase — Verificação de SESSION_HANDOFF

Antes de qualquer outra ação, verificar se existe `SESSION_HANDOFF.md` na raiz do projeto.

- Se existir → **ler integralmente** antes de prosseguir. O handoff contém o estado da sessão anterior, bloqueios ativos, decisões pendentes e próximos passos.
- Se não existir → criar a partir do template em `docs/_canon/templates/SESSION_HANDOFF.template.md` ao final da sessão.

Ao concluir qualquer tarefa neste orquestrador, **atualizar `SESSION_HANDOFF.md`** com:
- O que foi realizado nesta sessão
- Estado atual do módulo/contrato trabalhado
- Próximos passos recomendados
- Decisões que o humano precisa tomar

---

### Fase 0 — Classificação e Verificação de Entrada (padrão Routing)

Executar antes de qualquer leitura de domínio ou autoria:

1. **Validar `module`**: checar contra taxonomia em `.contract_driven/CONTRACT_SYSTEM_LAYOUT.md` §2.
   - Se não existir → `BLOCKED_MISSING_MODULE`. Parar.
2. **Validar `task_type`**: checar contra mapa de roteamento acima.
   - Se não mapeado → pedir esclarecimento ao humano.
3. **Identificar worker destino** pelo mapa de roteamento.
   - Se worker não existir → `BLOCKED_MISSING_AGENT_PROMPT`. Parar e registrar no backlog.
4. **Resolver o perfil de boot** em `docs/_canon/BOOT_PROFILES.md`.
   - Registrar quais artefatos são `boot_minimo`, `boot_condicional` e `gate_only`.
5. **Consultar `docs/_canon/MODULE_REGISTRY.yaml`**.
   - Registrar `status`, `owner` e `expected_surfaces` do módulo.
6. **Registrar abertura da execução** no log de execução do agente (ver §Observabilidade).

---

### Fase 1 — Foundation Readiness (padrão Evaluator)

Verificar se a Foundation Tier está sólida antes de prosseguir. Estas verificações são **binárias — PASS ou FAIL**.

#### F1.0 — Bootstrap de governança

Antes de qualquer checagem de domínio:

1. Carregar `.contract_driven/CONTRACT_SYSTEM_LAYOUT.md`.
2. Carregar `.contract_driven/CONTRACT_SYSTEM_RULES.md`.
3. Carregar `docs/_canon/CONTRACT_PIPELINE.md`.
4. Carregar `docs/_canon/BOOT_PROFILES.md`.
5. Carregar `docs/_canon/MODULE_REGISTRY.yaml`.
6. Se a tarefa puder chegar a validação, readiness ou handoff, carregar `docs/_canon/TOOLCHAIN_HEALTH_POLICY.md`.
7. Tratar `docs/_canon/gates/GATES_REGISTRY.yaml` como consulta `gate_only`, não como fonte substantiva.

Se qualquer artefato obrigatório do bootstrap estiver ausente ou contradizer o prompt, bloquear.

#### F1.1 — Presença de artefatos canônicos obrigatórios

Verificar presença dos seguintes arquivos para o módulo alvo:

| Artefato | Obrigatório sempre | Obrigatório quando |
|----------|-------------------|--------------------|
| `docs/hbtrack/modulos/<MODULE>/MODULE_SCOPE_<MODULE>.md` | sim | — |
| `docs/hbtrack/modulos/<MODULE>/DOMAIN_RULES_<MODULE>.md` | sim | — |
| `docs/hbtrack/modulos/<MODULE>/INVARIANTS_<MODULE>.md` | sim | — |
| `docs/hbtrack/modulos/<MODULE>/TEST_MATRIX_<MODULE>.md` | sim | — |
| `docs/hbtrack/modulos/<MODULE>/SPORT_SCIENCE_RULES_<MODULE>.md` | não | módulo é `training`, `wellness`, `medical` |
| `docs/hbtrack/modulos/<MODULE>/STATE_MODEL_<MODULE>.md` | não | módulo tem estados/máquina de estados |
| `docs/hbtrack/modulos/<MODULE>/PERMISSIONS_<MODULE>.md` | não | módulo tem RBAC específico |

Se algum artefato obrigatório estiver ausente → `BLOCKED_REQUIRED_ARTIFACT_MISSING`. Parar.

#### F1.2 — Decisões arquiteturais bloqueantes (padrão Evaluator-Optimizer)

1. Abrir `docs/_canon/ARCHITECTURE_DECISION_BACKLOG.md`.
2. Filtrar entradas com `criticidade: obrigatória` E `status: open`.
3. Para cada entrada, verificar se afeta o `module` alvo ou é global.
4. Se uma ou mais entradas bloqueantes forem encontradas:
   - Listar todas as entradas bloqueantes identificadas.
   - Emitir `BLOCKED_MISSING_ARCH_DECISION` para cada uma.
   - **Não prosseguir** — acionar Fase 2 (Decision Discovery) antes de continuar.
5. Se nenhuma entrada bloqueante for encontrada → F1.2 = PASS.

#### F1.3 — Checklist mínima de segurança de produção

Aplicável apenas para `task_type` ≠ `new_module` e ≠ `architecture_review`:

Verificar se as seguintes ADRs existem com `Status: Accepted`:

| Tópico | ADR esperada | Bloqueio se ausente |
|--------|-------------|---------------------|
| AUTH_STRATEGY | ADR com `identity_access` scope | sim (produção) |
| AUTHZ_STRATEGY | ADR com RBAC formal | sim (produção) |
| SENSITIVE_DATA_POLICY | ADR ou seção em SECURITY_RULES.md | se módulo lida com PII/PHI |
| SECRETS_POLICY | ADR ou seção em SECURITY_RULES.md | sim (produção) |

Se algum item obrigatório estiver ausente e o sistema declarar que está em modo de produção → `BLOCKED_MISSING_ARCH_DECISION`. Acionar Fase 2.

Se sistema estiver em modo experimental/placeholder → registrar aviso e prosseguir.

#### F1.4 — Verificação de hermeticidade de derivados

Verificar se `generated/resolved_policy/<MODULE>.sync.resolved.yaml` existe e está atualizado.
- Se não existir e `task_type` for `new_contract` ou `contract_revision` → avisar para rodar o compiler antes de concluir o worker.

**Resultado da Fase 1**: PASS (todas as verificações OK) ou BLOCKED (uma ou mais falhas).

---

### Fase 2 — Decision Discovery (padrão Prompt Chaining + Evaluator)

Executada **somente** quando a Fase 1 identificar decisões bloqueantes ou quando `task_type = architecture_review`.

1. Transferir execução para `.contract_driven/agent_prompts/decision_discovery.prompt.md`.
2. Passar contexto:
   - `module`, `task_type`, decisões bloqueantes identificadas em F1.2 / F1.3.
3. Aguardar saída do Decision Discovery:
   - Se bloqueios resolvidos (ADRs criadas, backlog atualizado) → retornar para Fase 1 e re-executar F1.2 / F1.3.
   - Se bloqueios não resolvidos (aguardando aprovação humana) → parar execução aqui. Retornar ao humano com sumário.

---

### Fase 3 — Montagem de Contexto de Domínio (padrão Prompt Chaining paralelo)

Fase 1 PASS confirmado. Montar o contexto completo de domínio para o worker.

O perfil de boot aplicável deve ser resolvido conforme `docs/_canon/BOOT_PROFILES.md`.

**Leituras obrigatórias — executar em paralelo quando possível**:

| Artefato | Sempre | Condicional |
|----------|--------|-------------|
| `.contract_driven/CONTRACT_SYSTEM_RULES.md` | sim | — |
| `.contract_driven/CONTRACT_SYSTEM_LAYOUT.md` | sim | — |
| `docs/_canon/CONTRACT_PIPELINE.md` | sim | — |
| `docs/_canon/BOOT_PROFILES.md` | sim | — |
| `docs/_canon/MODULE_REGISTRY.yaml` | sim | — |
| `docs/_canon/ARCHITECTURE.md` | sim | — |
| `docs/_canon/SYSTEM_SCOPE.md` | sim | — |
| `docs/_canon/DATA_CONVENTIONS.md` | sim | — |
| `docs/_canon/ERROR_MODEL.md` | sim, para contratos | — |
| `docs/_canon/SECURITY_RULES.md` | sim, para contratos | — |
| `docs/_canon/TOOLCHAIN_HEALTH_POLICY.md` | — | se a tarefa executar validação, readiness ou handoff |
| `docs/_canon/HANDBALL_RULES_DOMAIN.md` | — | gatilho esportivo ativo |
| `docs/hbtrack/modulos/<MODULE>/MODULE_SCOPE_<MODULE>.md` | sim | — |
| `docs/hbtrack/modulos/<MODULE>/DOMAIN_RULES_<MODULE>.md` | sim | — |
| `docs/hbtrack/modulos/<MODULE>/INVARIANTS_<MODULE>.md` | sim | — |
| `docs/hbtrack/modulos/<MODULE>/SPORT_SCIENCE_RULES_<MODULE>.md` | — | módulo sport-science |
| `docs/hbtrack/modulos/<MODULE>/STATE_MODEL_<MODULE>.md` | — | se existir |
| `docs/hbtrack/modulos/<MODULE>/PERMISSIONS_<MODULE>.md` | — | se existir |
| `docs/_canon/decisions/` (ADRs relevantes) | sim | — |

**Gatilho esportivo**: ativar se `module` ∈ {`matches`, `competitions`, `training`, `wellness`, `medical`} ou se `scope_description` mencionar regras de handebol/biomecânica/fisiologia.

**Consulta gate-only**:
- `docs/_canon/gates/GATES_REGISTRY.yaml` para saber quais bloqueios formais se aplicarão ao final do fluxo;
- esta leitura não substitui o contexto substantivo acima.

---

### Fase 4 — Transferência para Worker (padrão Orchestrator-Workers)

Condição de entrada: Fase 1 PASS, Fase 3 concluída.

1. Declarar explicitamente ao humano:
   ```
   ✅ Fase pré-contrato concluída.
   Módulo: <MODULE>
   Task: <task_type>
   Decisões bloqueantes: nenhuma
   Contexto carregado: <lista de artefatos lidos>
   Iniciando worker: <worker_prompt>
   ```
2. Transferir execução para o worker identificado na Fase 0.
3. Passar para o worker:
   - Módulo, resource, operações desejadas (da entrada humana).
   - `module_status`, `owner` e `expected_surfaces` vindos de `MODULE_REGISTRY`.
   - Contexto de domínio montado na Fase 3.
   - Lista de ADRs relevantes já resolvidas.
   - Flag de gatilho esportivo (sim/não).

---

### Observabilidade (Foundation Tier — audit trail de agente)

Em cada fase, registrar no output estruturado:

```
[PRE_CONTRACT_ORCHESTRATOR]
  fase: <0|1|2|3|4>
  modulo: <MODULE>
  task_type: <task_type>
  boot_profile: <profile>
  module_status: <scaffold|draft_contract|validated_contract|implementation_ready>
  expected_surfaces: [lista]
  resultado: PASS | BLOCKED | SKIP_NOT_APPLICABLE
  bloqueios_emitidos: [lista de códigos ou vazio]
  artefatos_lidos: [lista]
  gate_only_reads: [lista]
  worker_destino: <prompt ou NONE>
  decisoes_pendentes: [lista de ARCH-NNN ou vazio]
```

Este log satisfaz o padrão de *transparency in reasoning* do Foundation Tier e produz o audit trail de comportamento de agente exigido por `ARCH-009` (pendente).

Além do log por fase, o orquestrador deve publicar `_reports/evidence/boot_resolution_report.json`.

---

### Bloqueios canônicos deste orquestrador

| Código | Fase | Condição |
|--------|------|----------|
| `BLOCKED_MISSING_MODULE` | 0 | Módulo não existe no LAYOUT §2 |
| `BLOCKED_MISSING_AGENT_PROMPT` | 0 | Worker prompt não existe para o task_type |
| `BLOCKED_REQUIRED_ARTIFACT_MISSING` | 1 | Artefato de módulo obrigatório ausente |
| `BLOCKED_MISSING_ARCH_DECISION` | 1 | Decisão `obrigatória` em aberto no backlog |
| `BLOCKED_CONTRACT_CONFLICT` | 3 | Duas fontes canônicas contraditórias no mesmo nível |

---

### Saída esperada

**Se fase pré-contrato for bem-sucedida**:
- Declaração explícita de PASS com contexto montado.
- Início do worker com passagem de contexto estruturado.

**Se fase pré-contrato bloquear**:
- Relatório estruturado de cada bloqueio com código canônico.
- Para `BLOCKED_MISSING_ARCH_DECISION`: sumário de decisões pendentes e instrução para executar Decision Discovery.
- Para `BLOCKED_REQUIRED_ARTIFACT_MISSING`: lista de artefatos a criar com referência ao template canônico.

**Nunca**:
- Prosseguir silenciosamente ignorando bloqueio.
- Inventar conteúdo de domínio não documentado em artefato canônico.
- Executar worker sem completar as Fases 0-3.
