# Auditoria de Compliance Operacional do Agente

> ⚠️ **ARTEFATO DERIVADO — NON-SOVEREIGN**: Este arquivo é uma auditoria derivada. Não possui autoridade normativa. Em caso de conflito, prevalecem: `scripts/hb` + `validate_contracts.py` > `contracts/schemas/` > `docs/_canon/` > `.contract_driven/CONTRACT_SYSTEM_RULES.md` > este arquivo.

Escopo desta auditoria:
- Base exclusiva em artefatos reais do workspace, estado persistido e enforcement executável local.
- Presença de arquivo não foi tratada como prova de governança.
- Evidência executada:
  - `python3 scripts/contracts/validate/validate_contracts.py --profile ci` gerou `_reports/contract_gates/latest.json` com `overall_status=PASS`, `exit_code=0`, `gates_total=51`, `canonical_scope=full_pipeline`.
  - `.venv/bin/python -m pytest tests/test_pipeline_governance.py tests/pipeline_gates/test_context_budgets_and_parity.py tests/pipeline_gates/test_phase_0_determinism.py tests/pipeline_gates/test_module_lifecycle_governance.py tests/pipeline_gates/test_roadmap_session_boot.py -q` retornou `44 passed, 1 skipped`.

## PARTE 1 — Visão geral do compliance do agente

O agente não está governado por uma camada única e clara. Há uma governança forte no plano documental e no validator central, mas a governança de boot, roteamento, sessão e prompts é difusa, dependente de leitura manual e com drift relevante entre o que os arquivos declaram e o que o enforcement realmente executa.

A camada de configuração funciona bem em três pontos:
- `scripts/contracts/validate/validate_contracts.py` é o enforcement real do pipeline.
- `scripts/hb` é o boot/registro real de sessão para o fluxo CDD e, na prática, também vem sendo usado em ROADMAP.
- `scripts/git-hooks/pre-commit` está ativo via `core.hooksPath=scripts/git-hooks`.

Mas ela falha em pontos estruturais:
- `BOOT_PROFILES.yaml` e `TASK_CATALOG.yaml` são lidos só parcialmente.
- `AGENT_INSTRUCTIONS.md`, `SESSION_HANDOFF.md` e `ROADMAP.md` são declarados como boot obrigatório, mas isso não é executado por `scripts/hb`.
- `GATES_REGISTRY.yaml` e `validate_contracts.py` não estão 100% alinhados.
- O estado persistente de sessão está incoerente no modo ROADMAP.

Há sinais claros de drift entre configuração e comportamento:
- O pipeline canônico passou com `PASS`, mas `_reports/session_start.json` continua registrando `boot_profile_id=roadmap_execution`, `task_type=execute_roadmap_phase`, `module=training`, `stage=0`, enquanto `SESSION_HANDOFF.md` registra `modulo_foco: governance`, `fase_roadmap: 0`, `task_id: completa`.
- `SESSION_HANDOFF.md` passou no gate com `data_ultima_sessao: 2026-03-24`, embora a data corrente da auditoria seja `2026-03-23`; o gate só bloqueia handoff velho, não handoff no futuro.
- O registry normativo de gates tem gates ativos que não entram no executor real, e o executor real roda gates que não estão no registry.

Conclusão da visão geral:
- governança documental: forte;
- governança executável: forte no validator, média no hook, fraca no boot e no roteamento;
- drift configuração x comportamento: alto.

## PARTE 2 — Matriz de governança das configurações

| Configuração / arquivo | Deveria governar? | Governa de fato? | O agente lê? | O agente interpreta corretamente? | O agente segue de fato? | Status de compliance | Observações |
|------------------------|-------------------|------------------|--------------|-----------------------------------|-------------------------|----------------------|------------|
| `docs/_canon/AGENT_INSTRUCTIONS.md` | sim | parcialmente | provável | parcialmente | parcialmente | parcialmente conforme | Declara boot obrigatório, mas `scripts/hb` não o consome nem lê `SESSION_HANDOFF.md`/`ROADMAP.md`. |
| `CLAUDE.md` | parcialmente | parcialmente | provável | parcialmente | parcialmente | parcialmente conforme | Ponte para Claude; útil como bridge, mas sem enforcement repo-local. |
| `.github/copilot-instructions.md` | parcialmente | parcialmente | não confirmado | não | não | não conforme | Diz que `session_handoff.schema.json` não é validador ativo, mas o gate ativo usa esse schema. |
| `.contract_driven/CONTRACT_SYSTEM_RULES.md` | sim | parcialmente | provável | parcialmente | parcialmente | parcialmente conforme | É a norma mais forte, mas várias regras não chegam até enforcement técnico. |
| `.contract_driven/CONTRACT_SYSTEM_LAYOUT.md` | sim | sim | confirmado | sim | parcialmente | parcialmente conforme | Governa path/naming e é refletido em gates e prompts; leitura não é universal no boot. |
| `.contract_driven/BOOT_PROFILES.yaml` | sim | parcialmente | confirmado | parcialmente | parcialmente | não conforme | `scripts/hb` só valida profile/path existência; `selection_rules`, `phase_profiles`, `integration` e semântica de `required_sections` não são executadas. |
| `.contract_driven/TASK_CATALOG.yaml` | sim | parcialmente | confirmado | parcialmente | parcialmente | não conforme | `scripts/hb` usa `task_type/status/profile/worker`; ignora `stage_allowed`, `routing_validation` e `phase_routing`. |
| `.contract_driven/agent_prompts/pre_contract_orchestrator.prompt.md` | parcialmente | parcialmente | provável | parcialmente | parcialmente | parcialmente conforme | Influencia execução humana/LLM, mas não é tecnicamente orquestrado; pede saída para `session_start.json` que o schema não modela. |
| `.contract_driven/agent_prompts/execute_roadmap_phase.prompt.md` | parcialmente | parcialmente | provável | parcialmente | parcialmente | parcialmente conforme | Define o modo ROADMAP, mas não há estado técnico compatível em `session_start.json` para fase/task_id. |
| `.contract_driven/agent_prompts/generate_code.prompt.md` | parcialmente | parcialmente | não confirmado | parcialmente | parcialmente | inconclusivo | Pré-requisitos são só parcialmente reforçados por `scripts/hb`; outputs de feature/handoff não são tecnicamente exigidos. |
| `docs/_canon/CONTRACT_PIPELINE.md` | sim | parcialmente | provável | parcialmente | parcialmente | parcialmente conforme | Define estágios e evidências, mas o pipeline completo não valida `session_start.json` e não força survival suite. |
| `docs/_canon/gates/GATES_REGISTRY.yaml` | sim | parcialmente | confirmado | parcialmente | parcialmente | não conforme | O executor real tem drift de gates em relação ao registry. |
| `scripts/contracts/validate/validate_contracts.py` | sim | sim | confirmado | parcialmente | sim | parcialmente conforme | É o enforcement central real; ainda assim diverge do registry e ignora parte do estado de sessão. |
| `scripts/hb` | sim | sim | confirmado | parcialmente | parcialmente | parcialmente conforme | É o boot real, mas não lê boot mínimo declarado e não consome semântica completa de profiles/catalog. |
| `scripts/git-hooks/pre-commit` | sim | sim | confirmado | parcialmente | parcialmente | parcialmente conforme | Hook está ativo, mas integridade/handoff só cobrem `contracts/` e `docs/hbtrack/`, deixando governança canônica fora do rastreio fino. |
| `contracts/schemas/shared/session_start.schema.json` | sim | parcialmente | confirmado | parcialmente | parcialmente | parcialmente conforme | Schema é usado por `hb` e hook, mas contém campos sem writer (`stage2_exit_code`, `stage3_exit_code`) e texto stale (`16 canônicos`, `44 gates`). |
| `_reports/session_start.json` | sim | parcialmente | confirmado | não | parcialmente | não conforme | Estado persistente real para `hb`/hook, mas não governa o pipeline completo e está incoerente com o handoff ROADMAP atual. |
| `contracts/schemas/shared/session_handoff.schema.json` | sim | sim | confirmado | parcialmente | sim | parcialmente conforme | É validador ativo do handoff, embora parte das instruções de bridge diga o contrário. |
| `docs/_canon/templates/SESSION_HANDOFF.template.md` | sim | parcialmente | provável | não | não | não conforme | Template não é schema-safe: `evidence_paths: []` conflita com `minItems: 1`; placeholders não são diretamente válidos. |
| `SESSION_HANDOFF.md` | sim | sim | confirmado | parcialmente | parcialmente | parcialmente conforme | Governa continuidade real e passa no gate, mas não é lido por `scripts/hb` e aceita data futura. |
| `docs/_canon/MODULE_REGISTRY.yaml` | sim | sim | confirmado | sim | sim | conforme | É o SSOT operacional mais efetivo para status e superfícies esperadas. |
| `docs/_canon/FEATURE_REGISTRY.yaml` | parcialmente | parcialmente | confirmado | parcialmente | parcialmente | parcialmente conforme | Existe gate e uso em prompt, mas ele só valida estrutura; não governa a maioria dos módulos implementados. |
| `docs/_canon/MODULE_SOURCE_AUTHORITY_MATRIX.yaml` | sim | sim | confirmado | sim | sim | conforme | Governa vários boundary gates reais e reduz inferência indevida. |
| `ROADMAP.md` | sim | parcialmente | provável | parcialmente | parcialmente | parcialmente conforme | Governa o modo ROADMAP no plano humano, mas sem binding técnico completo no estado de sessão. |
| `docs/_canon/CODE_ARCHITECTURE.md` | parcialmente | parcialmente | confirmado | sim | parcialmente | parcialmente conforme | Lido por prompts/gate de arquitetura; não é boot automático universal. |
| `_reports/agent_execution/*.json` | sim | sim | confirmado | sim | sim | conforme | Governa `PRE_CONTRACT_EVIDENCE_GATE`; hoje sustenta continuidade pré-contrato. |
| `_reports/evidence/boot_resolution_report.json` | não | não | não | não | não | conforme | Artefato legado fora do caminho crítico; está stale e não governa mais o fluxo real. |
| `.github/skills/hb-pipeline-orchestrator/SKILL.md` | parcialmente | parcialmente | não confirmado | não | não | não conforme | Espera saída `task_type_target` que `scripts/hb` não produz e diz para não tratar o schema de handoff como ativo. |
| `.github/skills/hb-roadmap-executor/SKILL.md` | parcialmente | parcialmente | não confirmado | não | não | não conforme | Exemplo de handoff sem YAML front matter obrigatório; conflito direto com o gate ativo de handoff. |
| `scripts/hbtrack_lint/**` | não | não | não | não | não | parcialmente conforme | Subsystem legado aponta para `docs/hbtrack/modulos/atletas/MOTORES.md`, que nem existe; não está no critical path atual. |
| `docs/guias/*` | não | não | não confirmado | não se aplica | não | parcialmente conforme | São explicitamente não-soberanos, mas vários guias ainda estão stale; o gate cobre essa pasta. |
| `DEVCONT.md`, `compilance.md`, `ADVERSARIAL.md`, `ANALISEARQUITETURA.md` | não | parcialmente | não confirmado | não se aplica | não | não conforme | Artefatos grandes, com linguagem forte e fora do escopo do `SHADOW_AUTHORITY_GATE`; podem influenciar indevidamente humano/agente. |
| `.claude/settings.local.json` / `.vscode/mcp.json` | parcialmente | parcialmente | não confirmado | parcialmente | não se aplica | inconclusivo | Afetam permissões/ferramentas em IDEs específicos, mas não entram no enforcement repo-local. |
| `docs/_canon/SURVIVAL_SUITE_POLICY.md` | sim | não | provável | sim | não | não conforme | Política manda rodar `python3 scripts/hb survival-suite` antes de merge/promoção; CI não faz isso. |

## PARTE 3 — Configurações que realmente governam o agente

Estas têm efeito real comprovado no comportamento:
- `scripts/contracts/validate/validate_contracts.py`
- `scripts/hb`
- `scripts/git-hooks/pre-commit`
- `docs/_canon/MODULE_REGISTRY.yaml`
- `docs/_canon/MODULE_SOURCE_AUTHORITY_MATRIX.yaml`
- `docs/_canon/gates/GATES_REGISTRY.yaml` como metadata parcial de blocking/severity
- `contracts/schemas/shared/session_start.schema.json`
- `_reports/session_start.json`
- `contracts/schemas/shared/session_handoff.schema.json`
- `SESSION_HANDOFF.md`
- `.contract_driven/TASK_CATALOG.yaml` em subset real (`task_type`, `status`, `worker_path`, `profile_id`)
- `.contract_driven/BOOT_PROFILES.yaml` em subset real (`profile_id`, resolvibilidade de paths)
- `_reports/agent_execution/*.json`
- `docs/_canon/FEATURE_REGISTRY.yaml` apenas no nível de validação estrutural

## PARTE 4 — Configurações que deveriam governar, mas não governam

- `docs/_canon/AGENT_INSTRUCTIONS.md`
  - Deveria governar o boot global.
  - Não governa tecnicamente porque `scripts/hb` não lê `AGENT_INSTRUCTIONS.md`, `SESSION_HANDOFF.md` ou `ROADMAP.md`.
  - Risco: boot manual inconsistente e perda de continuidade entre sessões.

- `.contract_driven/BOOT_PROFILES.yaml`
  - Deveria governar ordem de leitura, `required_sections`, seleção de profile e integração.
  - Hoje governa só existência de profile e resolvibilidade de path.
  - Risco: o agente “passa no boot” sem ter lido o que o profile diz que é obrigatório.

- `.contract_driven/TASK_CATALOG.yaml`
  - Deveria governar estágio permitido, validação de roteamento e fluxo por fase.
  - Hoje governa só task type/status/worker/profile.
  - Risco: task pode ser executada fora de ordem ou sem pré-condição material.

- `docs/_canon/gates/GATES_REGISTRY.yaml`
  - Deveria ser o registry normativo exato dos gates ativos.
  - Não governa integralmente porque o executor real tem drift.
  - Risco: o sistema declara controles que não rodam e roda controles sem base normativa explícita.

- `docs/_canon/DECISION_POLICY.md` via `ARCH_DECISION_PRESENCE_GATE`
  - Deveria bloquear contrato com decisão obrigatória em aberto.
  - O gate está no registry, mas não no executor.
  - Risco: decisão obrigatória pode ser pulada e descoberta tarde demais.

- `docs/_canon/SCOPE_BOUNDARY_POLICY.md` via `SCOPE_BOUNDARY_GATE`
  - Deveria bloquear overflow cross-module no pipeline central.
  - Está só em script/prompt periférico, não no gate executor central.
  - Risco: boundary overflow depender de disciplina manual ou execução ad hoc.

- `docs/_canon/SURVIVAL_SUITE_POLICY.md`
  - Deveria governar mudanças em gates/profiles/schema/hook.
  - Hoje é manual; CI não força `hb survival-suite`.
  - Risco: regressão em governança entrar com pipeline aparentemente verde.

- Estado ROADMAP (`phase`, `task_id`, `modulo_foco`)
  - Deveria governar continuidade do modo ROADMAP.
  - Não está modelado em `session_start.schema.json`; o estado fica dividido entre handoff e sessão.
  - Risco: execução de fase com memória operacional inconsistente.

- Skills `.github/skills/hb-pipeline-orchestrator/SKILL.md` e `.github/skills/hb-roadmap-executor/SKILL.md`
  - Deveriam orientar corretamente o agente em plataformas GitHub.
  - Estão desatualizados em relação ao schema/gates ativos.
  - Risco: o agente seguir um protocolo inválido e produzir handoff não conforme.

## PARTE 5 — Pontos de não-conformidade

| Configuração | Tipo de não-conformidade | Evidência | Impacto | Gravidade |
|--------------|---------------------------|-----------|---------|-----------|
| `.contract_driven/BOOT_PROFILES.yaml` | aplicação parcial | `selection_rules`, `phase_profiles` e `integration` não têm consumidores em código; `scripts/hb` só valida paths/sections resolvíveis | Boot “formal” não garante leitura real nem seleção correta de profile | alta |
| `.contract_driven/TASK_CATALOG.yaml` | aplicação parcial | `stage_allowed`, `routing_validation` e `phase_routing` não aparecem em runtime; só em testes de estrutura | Ordem de execução e bloqueios declarados podem ser ignorados | alta |
| `docs/_canon/gates/GATES_REGISTRY.yaml` vs `scripts/contracts/validate/validate_contracts.py` | conflito de precedência | `in_latest_not_registry=['SPECTRAL_LINTING_GATE','SURFACE_PROMOTION_COHERENCE_GATE']`; `in_registry_not_latest=['ARCH_DECISION_PRESENCE_GATE','FRONTEND_CONTRACT_GATE','SCOPE_BOUNDARY_GATE']` | Split-brain entre norma e enforcement | crítica |
| `docs/_canon/AGENT_INSTRUCTIONS.md` | governança fraca | `scripts/hb` não referencia `AGENT_INSTRUCTIONS`, `SESSION_HANDOFF` ou `ROADMAP`; o boot declarado é manual | Continuidade e contexto dependem de disciplina informal | alta |
| `_reports/session_start.json` + `SESSION_HANDOFF.md` | conflito de precedência | Hand-off atual: `modulo_foco=governance`, `fase_roadmap=0`; sessão atual: `module=training`, sem `phase`/`task_id` | Estado operacional divergente entre arquivos oficiais | alta |
| `contracts/schemas/shared/session_start.schema.json` | aplicação parcial | Schema define `stage2_exit_code` e `stage3_exit_code`; não há writer em `scripts/hb`; hook só faz warning se `stage2_exit_code` faltar | Rastreabilidade incompleta do avanço até o DONE | média |
| `contracts/schemas/shared/session_handoff.schema.json` vs `.github/copilot-instructions.md` | interpretação errada | Copilot diz que o schema “não deve ser tratado como validador ativo”; `_g_handoff_coherence` usa exatamente esse schema | Bridge doc orienta o agente a ignorar a regra ativa | alta |
| `.github/skills/hb-roadmap-executor/SKILL.md` | interpretação errada | Exemplo de fechamento cria `SESSION_HANDOFF.md` sem front matter YAML obrigatório | Handoff inválido pode ser produzido por instrução “oficial” | alta |
| `.github/skills/hb-pipeline-orchestrator/SKILL.md` | interpretação errada | Espera saída `task_type_target` de `hb verify --task-type pre_contract_boot`; `scripts/hb` não produz isso | Skill promete um fluxo que o runtime não suporta | média |
| `docs/_canon/templates/SESSION_HANDOFF.template.md` | leitura parcial | Template usa `evidence_paths: []`, mas o schema exige `minItems: 1` | Template pode induzir handoff inválido por copy-paste | média |
| `docs/_canon/SURVIVAL_SUITE_POLICY.md` | ignorada | Política diz “DONE = exit code 0. Não avançar sem suíte verde”; workflow CI não executa `hb survival-suite` | Mudanças críticas podem entrar sem regressão mínima obrigatória | alta |
| `scripts/git-hooks/pre-commit` | aplicação parcial | `get_staged_files()` rastreia só `contracts/` e `docs/hbtrack/` para integridade/handoff | Mudanças em `.contract_driven`, `docs/_canon`, `scripts/contracts/validate` escapam do rastreio fino de artifact/handoff | alta |
| `DEVCONT.md`, `compilance.md`, `ADVERSARIAL.md`, `ANALISEARQUITETURA.md` | governança fraca | Arquivos grandes na raiz, fora do `SHADOW_AUTHORITY_GATE`, com linguagem forte e diagnósticos operacionais | Podem virar pseudo-autoridade paralela e poluir o contexto do agente | alta |
| `_reports/evidence/boot_resolution_report.json` | obsolescência | Continua presente, com `taskType=contract_revision`, `profile=contract_revision`, `source_authority='CLAUDE.md §7'`; testes tratam como legado fora do critical path | Evidência velha pode ser confundida com boot atual | baixa |
| `scripts/hbtrack_lint/**` | obsolescência | Subsystem aponta para `docs/hbtrack/modulos/atletas/MOTORES.md`, inexistente; não é usado no pipeline atual | Governança morta aumenta ruído e custo de manutenção | média |
| `SESSION_HANDOFF.md` | governança fraca | Data do handoff é `2026-03-24`; data atual desta auditoria é `2026-03-23`; gate só checa staleness > 30 dias | Estado “do futuro” passa como coerente | baixa |
| `docs/_canon/FEATURE_REGISTRY.yaml` | governança fraca | Registry tem features em só 5 módulos; `MODULE_REGISTRY.yaml` marca 17 módulos `implemented`; gate só valida estrutura | Progresso funcional e DONE por feature ficam incompletos | média |

## PARTE 6 — Riscos operacionais

- Alucinação
  - Como o boot obrigatório não é tecnicamente executado, o agente pode operar com contexto presumido e não lido de fato.

- Deriva de escopo
  - O `SCOPE_BOUNDARY_GATE` declarado não roda no executor central.
  - Arquivos paralelos na raiz não são cobertos pelo `SHADOW_AUTHORITY_GATE`.

- Inconsistência entre sessões
  - `SESSION_HANDOFF.md` e `_reports/session_start.json` carregam estados distintos para a mesma operação ROADMAP.
  - `session_start` não modela `phase` nem `task_id`.

- Retrabalho
  - O sistema pode parecer verde (`validate_contracts.py` PASS, testes verdes), enquanto regras de boot, roteamento e sessão continuam não aplicadas.
  - O drift entre registry e executor faz correções voltarem depois.

- Conflito entre artefatos
  - Há conflito direto entre GATES_REGISTRY, skills GitHub, copilot instructions, schemas e executor real.
  - Isso reduz determinismo e abre espaço para o agente “obedecer” o artefato errado.

- DONE incorreto
  - O pipeline completo pode dar `PASS` mesmo com estado de sessão stale/incoerente.
  - O `FEATURE_REGISTRY` não sustenta DONE funcional para a maior parte dos módulos implementados.

- Decisão sem base suficiente
  - `ARCH_DECISION_PRESENCE_GATE` está normatizado, mas não executado.
  - Decisões obrigatórias podem ser puladas sem bloqueio técnico.

- Perda de rastreabilidade
  - `stage2_exit_code` e `stage3_exit_code` existem no schema, mas não são preenchidos pelo fluxo real.
  - O hook rastreia artefatos detalhadamente só em subset do repositório.

- Segurança e integridade operacional
  - Bridge docs e skills podem instruir o agente a gerar handoff inválido ou ignorar schema ativo.
  - Se isso ocorrer numa plataforma que realmente auto-carrega essas instruções, o agente fica formalmente fora de compliance sem perceber.

## PARTE 7 — Veredito final

- O agente está em compliance com as configurações que deveriam governá-lo?
  - parcialmente

- Quais configurações realmente governam o agente hoje?
  - `scripts/contracts/validate/validate_contracts.py`
  - `scripts/hb`
  - `scripts/git-hooks/pre-commit`
  - `docs/_canon/MODULE_REGISTRY.yaml`
  - `docs/_canon/MODULE_SOURCE_AUTHORITY_MATRIX.yaml`
  - `contracts/schemas/shared/session_start.schema.json`
  - `_reports/session_start.json`
  - `contracts/schemas/shared/session_handoff.schema.json`
  - `SESSION_HANDOFF.md`
  - `_reports/agent_execution/*.json`
  - subset real de `.contract_driven/TASK_CATALOG.yaml`
  - subset real de `.contract_driven/BOOT_PROFILES.yaml`

- Quais deveriam governar e não estão governando?
  - boot real descrito em `docs/_canon/AGENT_INSTRUCTIONS.md`
  - semântica completa de `.contract_driven/BOOT_PROFILES.yaml`
  - semântica completa de `.contract_driven/TASK_CATALOG.yaml`
  - `ARCH_DECISION_PRESENCE_GATE`
  - `SCOPE_BOUNDARY_GATE`
  - `FRONTEND_CONTRACT_GATE`
  - `docs/_canon/SURVIVAL_SUITE_POLICY.md`
  - modelo técnico completo de sessão ROADMAP (`phase`, `task_id`, `modulo_foco`)
  - skills e bridge docs GitHub alinhados ao schema/gates atuais

- Quais são os maiores riscos atuais?
  - drift entre norma e enforcement
  - continuidade entre sessões incorreta
  - decisão obrigatória passar sem gate
  - DONE aparente com rastreabilidade incompleta
  - artefatos paralelos influenciarem o agente como pseudo-autoridade

- O que precisa ser corrigido para o agente entrar em compliance real?
  - alinhar `GATES_REGISTRY.yaml` e `validate_contracts.py`: todo gate ativo precisa existir nos dois lados; todo gate registrado precisa ter executor real ou ser explicitamente removido/desativado
  - fazer `scripts/hb` executar boot de verdade: ler handoff/profile, aplicar `selection_rules`, validar `required_sections` por seção real e não só por path
  - unificar o estado de sessão ROADMAP: `session_start.schema.json` precisa suportar `phase`, `task_id` e foco não modular, ou então o ROADMAP precisa ter um state store próprio e ser cruzado com o handoff
  - alinhar `session_handoff.schema.json`, `SESSION_HANDOFF.template.md`, `.github/copilot-instructions.md` e os skills GitHub
  - tornar `SURVIVAL_SUITE_POLICY.md` enforcement real em CI para mudanças de governança
  - ampliar o controle de shadow authority para os arquivos analíticos de raiz ou movê-los/rotulá-los como derivados não soberanos
  - remover ou arquivar de vez evidências e subsistemas legados que já não governam o fluxo real (`boot_resolution_report`, `hbtrack_lint` legado)
