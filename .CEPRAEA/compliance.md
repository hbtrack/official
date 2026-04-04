RELATÓRIO DE COMPLIANCE: Agente vs PIPELINE.md

> ⚠️ **ARTEFATO DERIVADO — NON-SOVEREIGN**: Este arquivo é um relatório de compliance derivado. Não possui autoridade normativa. Não deve ser usado para redefinir schemas, gates, contratos ou políticas canônicas. Em caso de conflito, prevalecem: `scripts/hb` + `validate_contracts.py` > `contracts/schemas/` > `docs/_canon/` > `.contract_driven/CONTRACT_SYSTEM_RULES.md` > este arquivo.

Escopo da auditoria
Validação do comportamento do agente durante a criação do módulo scout contra as exigências formais documentadas em PIPELINE.md.

Leia: /home/davis/HB-TRACK/docs/guias/produto/PIPELINE.md

BOOT — Leitura de SESSION_HANDOFF.md
Requisito	Cumprido?	Evidência
Ler SESSION_HANDOFF.md antes de qualquer coisa se existir	PARCIAL	O agente não leu SESSION_HANDOFF_CURRENT.md (handoff oficial). Na raiz existe SESSION_HANDOFF_RED_TEAM_20260318.md, que também não foi lido explicitamente antes de iniciar o trabalho do scout.
Ler AGENT_INSTRUCTIONS.md no boot	NÃO	Não há evidência de que o agente carregou AGENT_INSTRUCTIONS.md no início da sessão do scout.
Severidade: ALTA — o pipeline exige isso como pré-condição absoluta.

FASE 0 — Session Boot (Orquestrador)
Requisito	Cumprido?	Evidência
Executar hb verify --task-type <T> --module scout	NÃO	O hb verify nunca foi executado para o módulo scout.
Criar/atualizar session_start.json com module: scout	NÃO	O arquivo session_start.json atual registra module: wellness, task_type: contract_revision — de uma sessão anterior. Nenhum registro do scout.
Validar task_type ∈ TASK_CATALOG.yaml (status=active)	NÃO	Nenhuma validação formal feita. O agente não consultou TASK_CATALOG.yaml para determinar o task_type correto (que deveria ser new_contract).
Validar module ∈ MODULE_REGISTRY.yaml	PARCIAL	O agente verificou que o scout existia no registry (como draft_contract), mas não via o mecanismo formal (hb verify).
Selecionar boot_profile_id de BOOT_PROFILES.yaml	NÃO	Nenhum boot profile foi selecionado ou referenciado.
Emitir log de observabilidade [ORCHESTRATOR] fase:0...	NÃO	Nenhum log de orquestração emitido.
Severidade: CRÍTICA — A Fase 0 é a porta de entrada obrigatória. Nenhuma etapa foi cumprida formalmente.

FASE 1 — Discovery
Requisito	Cumprido?	Evidência
Executar hb check --module scout	NÃO	Nunca executado.
Verificar docs mínimas (README, DOMAIN_RULES, INVARIANTS, TEST_MATRIX, MODULE_SCOPE)	SIM (informal)	O agente leu os arquivos de docs do módulo scout, confirmando a existência de README, DOMAIN_RULES, INVARIANTS, TEST_MATRIX, MODULE_SCOPE. Porém, fez isso manualmente, não via gate formal.
Verificar ARCHITECTURE_DECISION_BACKLOG.md para decisões abertas do scout	NÃO	O backlog não contém menção a "scout", e o agente não verificou formalmente.
Executar check_scope_boundary.py se refs cross-module	NÃO	O contrato scout tem refs cross-module (matchId → matches, athleteUserId → identity, teamId → teams), mas check_scope_boundary.py nunca foi executado.
Severidade: ALTA — Discovery é obrigatória e foi executada apenas de forma informal.

DECISION DISCOVERY
Requisito	Cumprido?	Evidência
Carregar decision_discovery.prompt.md	NÃO	O worker de Decision Discovery nunca foi carregado.
Ler as 12 fontes mínimas obrigatórias	NÃO	Não há evidência de leitura de DECISION_POLICY, COMPETITIVE_BENCHMARK_PROTOCOL, ADRs relevantes, SECURITY_RULES, DATA_CONVENTIONS, etc.
Executar benchmark competitivo antes de apresentar opções	NÃO	As 3 decisões foram apresentadas ao humano sem benchmark competitivo. O pipeline exige 📊 mercado → 🎯 3 caminhos (A/B/C) → ⭐ recomendação.
Apresentar opções A/B/C com recomendação	PARCIAL	Opções A/B/C foram apresentadas, mas sem benchmark de mercado e sem recomendação explicitamente destacada (⭐).
Aguardar aprovação explícita	SIM	O agente aguardou e recebeu 1-c/2-b/3-c do humano.
Criar ADR formal após aprovação (docs/_canon/decisions/ADR-NNN-slug.md)	NÃO	Foi criado DECISION_IR_SCOUT.yaml (correto), porém nenhum ADR formal foi gerado em decisions.
Atualizar ARCHITECTURE_DECISION_BACKLOG.md	NÃO	O backlog não foi atualizado.
Severidade: ALTA — Benchmarks competitivos e ADRs são exigências formais da Decision Discovery.

FASE 2 — Authoring
Requisito	Cumprido?	Evidência
Carregar worker prompt correspondente ao task_type	NÃO	O worker create_openapi_contract.prompt.md nunca foi carregado/lido. Os outros workers (create_asyncapi_contract.prompt.md, create_arazzo_workflow.prompt.md) também não.
Ler fontes SSOT na ordem prescrita (CONTRACT_SYSTEM_RULES, CONTRACT_SYSTEM_LAYOUT, api_rules.yaml, MODULE_PROFILE_REGISTRY, etc.)	PARCIAL	O agente leu o OpenAPI root, asyncapi root, e referências de módulos anteriores (audit), mas não leu api_rules.yaml, CONTRACT_SYSTEM_RULES.md, CONTRACT_SYSTEM_LAYOUT.md, ou MODULE_PROFILE_REGISTRY.yaml.
Criar artefatos nos paths canônicos corretos	SIM	Todos os artefatos foram criados nos paths corretos conforme CONTRACT_SYSTEM_LAYOUT.
Executar hb artifact <path> após cada artefato criado	NÃO	hb artifact nunca foi executado para nenhum dos ~12 artefatos criados.
Executar compile_api_policy.py --module scout --surface sync pós-authoring	SIM	O agente executou compile_api_policy.py --all (mais abrangente) e depois validate_contracts.py.
Severidade: ALTA — Workers não carregados significa que as regras específicas de cada tipo de artefato foram ignoradas.

FASE 3 — Validation (44 Gates)
Requisito	Cumprido?	Evidência
Executar validate_contracts.py	SIM	Pipeline executado com 10/10 gates PASS.
Gates em latest.json	SIM	O resultado registra overall_status: PASS com 44 gates.
Severidade: OK — Esta fase foi cumprida corretamente.

FASE 4 — Readiness
Requisito	Cumprido?	Evidência
Atualizar MODULE_REGISTRY.yaml (scout → validated_contract)	SIM	Status atualizado de draft_contract para validated_contract com 8 expected_surfaces.
Atualizar module_readiness_scorecard.json	PARCIAL	O scorecard existe mas não contém scout — ele foi gerado pela sessão anterior (wellness). O agente não regenerou o scorecard para incluir scout.
Registrar em pipeline_history.jsonl	NÃO	grep -i scout pipeline_history.jsonl retorna zero resultados. A execução do scout não foi registrada no histórico.
Severidade: MÉDIA — O registry foi atualizado, mas a rastreabilidade falhou.

FASE 5 — Handoff
Requisito	Cumprido?	Evidência
Atualizar SESSION_HANDOFF.md com resultado da sessão	NÃO	Nenhum SESSION_HANDOFF foi atualizado ou criado após a conclusão do scout.
Criar agent_execution com evidência de pré-contrato	NÃO	agent_execution não existe.
Severidade: ALTA — Sem handoff, a próxima sessão não terá contexto do que foi feito.

RESUMO EXECUTIVO
Fase	Status	Itens cumpridos / Total
Boot	FALHA	0/2
Fase 0 (Session Boot)	FALHA	0/6
Fase 1 (Discovery)	PARCIAL	1/4 (informal)
Decision Discovery	PARCIAL	2/7
Fase 2 (Authoring)	PARCIAL	2/5
Fase 3 (Validation)	PASS	2/2
Fase 4 (Readiness)	PARCIAL	1/3
Fase 5 (Handoff)	FALHA	0/2
TOTAL		8/31 (~26%)
VIOLAÇÕES MAIS GRAVES
hb verify nunca executado — O ponto de entrada obrigatório do pipeline foi completamente pulado. Isso deveria ter sido o primeiro comando, antes de qualquer leitura de artefato.

session_start.json não criado para scout — Sem rastreabilidade de sessão. O arquivo atual registra a sessão de wellness, não scout.

Workers nunca carregados — Nenhum dos prompts especializados (create_openapi_contract.prompt.md, create_asyncapi_contract.prompt.md, create_arazzo_workflow.prompt.md) foi lido. As regras específicas de cada tipo de artefato foram ignoradas.

Benchmark competitivo ausente na Decision Discovery — O pipeline exige 📊 mercado → 🎯 3 caminhos → ⭐ recomendação. As decisões foram apresentadas diretamente sem benchmark de mercado.

hb artifact nunca executado — Nenhum dos ~12 artefatos criados foi registrado formalmente na sessão.

SESSION_HANDOFF não atualizado — A próxima sessão não terá contexto de que o scout foi criado.

Sem ADR formal — As decisões do scout foram registradas em DECISION_IR_SCOUT.yaml mas não geraram ADRs em decisions.

DIAGNÓSTICO
O agente operou num modo que eu chamaria de "authoring direto" — saltou diretamente para a criação de artefatos com base em conhecimento acumulado da conversa, sem passar pelo protocolo formal de fases. A Fase 3 (validação com 44 gates) e a compilação de policy foram executadas corretamente, o que mostra que o final do pipeline foi respeitado, mas todo o início (Boot → Fase 0 → Fase 1 → Decision Discovery formal → Authoring com worker) foi pulado.

A compliance real do agente com o PIPELINE.md é de aproximadamente 26% (8 de 31 checkpoints).


Por que a compliance não é 100%
1. O pipeline foi projetado para o Claude Code (terminal nativo), não para o GitHub Copilot
O PIPELINE.md assume que o agente tem acesso direto e persistente a um terminal onde pode executar:


hb verify --task-type new_contract --module scouthb check --module scouthb artifact contracts/openapi/paths/scout.yaml
Esses comandos são o mecanismo de enforcement das Fases 0-2. Sem executá-los, não existem:

session_start.json com o módulo correto
Validação formal de task_type + module
Registro de artefatos com SHA-256
Logs de observabilidade [ORCHESTRATOR]
O GitHub Copilot pode rodar comandos no terminal, mas nenhuma instrução no contexto do agente (copilot-instructions.md, CLAUDE.md) diz quando ou como executá-los. O CLAUDE.md diz "ler AGENT_INSTRUCTIONS.md" — mas não diz "executar hb verify antes de criar artefatos".

2. Os worker prompts não são carregados automaticamente
O pipeline pressupõe que o agente carrega e segue prompts como create_openapi_contract.prompt.md antes de criar qualquer contrato. Isso funciona no Claude Code porque o AGENT_INSTRUCTIONS.md §4 mapeia task_type → worker, e o agente de terminal lê esse mapeamento.

No Copilot, o agente recebe:

copilot-instructions.md → apenas um ponteiro para AGENT_INSTRUCTIONS.md
CLAUDE.md → outro ponteiro para AGENT_INSTRUCTIONS.md
Mas nenhum mecanismo força o agente a realmente ler AGENT_INSTRUCTIONS.md no início da conversa, e muito menos a seguir a cadeia:


AGENT_INSTRUCTIONS.md → task_type → TASK_CATALOG.yaml → worker_path → ler worker prompt
3. O "Boot mínimo" não está no contexto automático do Copilot
O pipeline define um boot mínimo de 4 artefatos (~2.100 palavras):

Artefato	Carregado automaticamente?
AGENT_INSTRUCTIONS.md	NÃO — precisa ser lido manualmente
SESSION_HANDOFF.md	NÃO — precisa ser lido manualmente
CONTRACT_PIPELINE.md	NÃO — precisa ser lido manualmente
pre_contract_orchestrator.prompt.md	NÃO — precisa ser lido manualmente
No Claude Code, esses são lidos porque CLAUDE.md está na raiz e é carregado como system prompt. No Copilot, o copilot-instructions.md é carregado, mas ele apenas aponta para esses arquivos — não os inclui.

4. Sem estado persistente entre turnos de conversa
O pipeline depende de session_start.json como memória persistente. Quando o agente executa hb verify, esse arquivo é criado com session_id, task_type, module, stage. Cada fase subsequente consulta esse arquivo para saber onde está.

O agente Copilot não executou hb verify, então nunca criou essa sessão. Sem sessão formal, não há:

Rastreamento de estágio (stage 0 → 1 → 2)
Registro de artefatos (stage2_artifacts[])
Entrada em pipeline_history.jsonl
5. A Decision Discovery exige benchmark competitivo — o agente não sabe disso
O protocolo exige que antes de apresentar opções A/B/C, o agente execute um benchmark competitivo (📊 mercado → 🎯 3 caminhos → ⭐ recomendação). Isso está documentado em:

decision_discovery.prompt.md (worker)
COMPETITIVE_BENCHMARK_PROTOCOL.md
Como nenhum desses foi carregado, o agente apresentou as decisões no formato A/B/C que parece correto, mas faltou:

Pesquisa de mercado (como outras plataformas resolvem scouting?)
Recomendação explícita com justificativa comparativa
ADR formal em docs/_canon/decisions/ADR-NNN-slug.md
6. O Handoff é responsabilidade do agente, mas nada o lembra
O pipeline exige que ao final de uma task, o agente atualize SESSION_HANDOFF.md. No Claude Code, o orchestrator prompt contém essa instrução na Fase 5. No Copilot, o agente simplesmente "termina" quando o trabalho parece completo — ninguém lembra ele de fazer o handoff.

Resumo: o gap é estrutural
Causa raiz	Impacto
Boot mínimo não está no contexto automático	Fases 0-1 inteiras ignoradas
hb verify / hb artifact nunca executados	Sem rastreabilidade de sessão
Workers nunca carregados	Regras específicas de cada artefato ignoradas
Benchmark competitivo desconhecido	Decision Discovery incompleta
Handoff não lembrado	Perda de contexto entre sessões
A compliance não é 100% porque o pipeline foi construído para um agente que lê prompts encadeados numa ordem prescrita e executa CLIs de controle — e nada no setup atual do Copilot garante que isso aconteça. O agente faz o que sabe (criar artefatos, rodar validação) mas pula o protocolo formal porque nunca carregou as instruções que descrevem esse protocolo.

---

# AUDIT #2 — Sessão Video Backend (2026-03-19)

## Escopo da auditoria
Análise de duas violações críticas identificadas na sessão de implementação do módulo video:
1. Código backend gerado para módulo que **não está em `implementation_ready`**
2. **FASE 6 (git commit) totalmente omitida**

---

## VIOLAÇÃO 1 — Código gerado sem elegibilidade formal

### O que aconteceu
O agente gerou código Django (models.py, views.py, tasks.py) para o módulo `video` após o usuário pedir "Opção A: Video Backend Design". O agente criou os arquivos sem checar as pré-condições canônicas.

### O que o TASK_CATALOG.yaml exige para `generate_code`

```yaml
generate_code:
  input_requirements:
    - module (status=validated_contract)   # ← vídeo está em draft_contract
  blocking_gates:
    - AXIOM_INTEGRITY_GATE
    - OPENAPI_ROOT_STRUCTURE_GATE
    - ADVERSARIAL_ANALYSIS_GATE            # ← nunca executado
```

### Sequência canônica obrigatória (não seguida)

| Etapa | Status Exigido | Status Real |
|---|---|---|
| 1. Promover video: `draft_contract` → `validated_contract` | `draft_contract` → `validated_contract` | ❌ Pulado |
| 2. Rodar `readiness_promotion` | `validated_contract` + todas expected_surfaces | ❌ Pulado |
| 3. Rodar `adversarial_analysis` | `ADVERSARIAL_ANALYSIS_GATE=PASS` | ❌ Pulado |
| 4. Gerar código com `generate_code` | `implementation_ready` | ❌ Executado fora de ordem |

**Status real do módulo no momento:** `draft_contract` (MODULE_REGISTRY.yaml linha 222)
**Status exigido para `generate_code`:** `validated_contract` (mínimo); `implementation_ready` (ideal)

### Causa raiz
O agente recebeu o pedido do usuário ("Opção A") e interpretou como autorização suficiente para gerar código. Não consultou `TASK_CATALOG.yaml` para verificar `input_requirements.status`. Não emitiu `BLOCKED_REQUIRED_ARTIFACT_MISSING` — que deveria ter sido o comportamento correto.

**Regra violada (CONTRACT_PIPELINE.md §3):**
> "Sem pular estágios; nenhuma implementação antes de Validation + Readiness"

**Regra violada (CONTRACT_SYSTEM_RULES.md §16-17):**
> "Um módulo não está pronto para implementação enquanto seus JSON Schemas obrigatórios não existirem e não validarem [...] Contrato pronto apenas quando todos forem verdadeiros"

### Sinal de alerta que o agente deveria ter emitido
```
BLOCKED_REQUIRED_ARTIFACT_MISSING
Módulo video está em draft_contract.
Para gerar código são necessários:
1. Promoção para validated_contract (hb verify + pipeline PASS)
2. Readiness promotion (readiness_promotion task)
3. Adversarial analysis (adversarial_analysis task, ADVERSARIAL_ANALYSIS_GATE=PASS)
```

---

## VIOLAÇÃO 2 — FASE 6 (git commit) omitida

### O que aconteceu
A sessão terminou após FASE 5 (SESSION_HANDOFF.md criado). A FASE 6 — `git add + git commit` — nunca foi executada.

### O que o pipeline exige

Do modo `HB Contract` (copilot-instructions.md):
```
FASE 6 → git add <artefatos> SESSION_HANDOFF.md &&
          git commit -m "feat(contract): <module> — <task_type> pipeline PASS"
```

Das regras AGENT_INSTRUCTIONS.md:
> "NUNCA terminar sessão sem commit."

Do CONTRACT_PIPELINE.md:
> "Implementation-first seguido de documentação depois é proibido."

### Consequências
- O pre-commit hook (`scripts/git-hooks/pre-commit`) nunca executou — gates de commit não foram verificados
- `pipeline_history.jsonl` não registra a sessão video
- O trabalho não é rastreável via `git log`
- Qualquer artefato canônico criado (OpenAPI, AsyncAPI, STATE_MODEL, etc.) ficou sem hash registrado no controle de versão

### Causa raiz
O agente tratou a FASE 6 como opcional após o usuário escolher continuar para implementação backend. O contexto do `SESSION_HANDOFF` foi criado mas o commit foi pulado porque o agente priorizou avançar para a "próxima fase" ao invés de fechar a sessão corrente de forma rastreável.

---

## Resumo das duas violações

| Violação | Regra violada | Severidade | Código de bloqueio correto |
|---|---|---|---|
| Código gerado sem `implementation_ready` | TASK_CATALOG `input_requirements`, CONTRACT_PIPELINE §3, RULES §16-17 | **CRÍTICA** | `BLOCKED_REQUIRED_ARTIFACT_MISSING` |
| FASE 6 omitida | Modo HB Contract FASE 6, AGENT_INSTRUCTIONS "nunca terminar sem commit" | **ALTA** | N/A — falha de procedimento |

---

## Causa raiz comum (sistema)

Ambas as violações têm a mesma origem estrutural: **o agente responde ao pedido do usuário diretamente sem verificar as pré-condições canônicas registradas em `TASK_CATALOG.yaml`**.

O pipeline exige que toda tarefa passe por `hb verify --task-type <T> --module <M>` *antes* de qualquer ação. Esse comando é o portão que leria `input_requirements.status` e emitiria o bloqueio correto. Como `hb verify` nunca foi executado, o portão não funcionou.

O commit (FASE 6) não tem um mecanismo de enforcement equivalente — depende inteiramente do agente seguir a sequência até o fim, o que não aconteceu quando o contexto de conversa mudou de direção (contratos → implementação).

Após analisar os arquivos necessários

# Plano de Ação para Compliance Total com PIPELINE.md

Crie abaixo o plano deterministico, com o passo a passo em forma de checklist, distibuido por fases e ordem de implementação correta.

- Configure todos os arquivos necessários para que o agente possa seguir o pipeline corretamente e atingir 100% de compliance na próxima execução.

- Configure as skills necessárias para que o agente execute os comandos de terminal exigidos (hb verify, hb artifact, etc.) no momento certo do pipeline.

Próximo passo correto: Antes de qualquer código backend, o módulo video precisa passar por readiness_promotion (validated_contract → implementation_ready) e adversarial_analysis. Quer iniciar esse caminho agora?