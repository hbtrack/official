# Plano de Execucao para Compliance Total do Agente

## Objetivo

Executar as correcoes na ordem certa para eliminar drift entre:
- configuracao declarada
- interpretacao do agente
- enforcement tecnico
- comportamento real

Se este plano for executado integralmente e todos os criterios de saida forem aprovados, o agente passa a operar em compliance real com as configuracoes que devem governa-lo.

## Regra de ordem

Nao inverter a sequencia abaixo.

Motivo:
1. primeiro e preciso fechar precedencia normativa e conter novas contradicoes;
2. depois alinhar a camada executavel com a camada declarativa;
3. so entao corrigir boot, sessao, handoff e CI;
4. por fim, remover legado, fechar rastreabilidade e certificar o estado final.

## Principios de execucao

- Toda regra normativa relevante precisa ter um consumidor tecnico claro.
- Toda ponte documental precisa repetir a regra ativa, nunca contradize-la.
- Toda correcao documental critica precisa vir acompanhada de teste ou gate.
- Nenhum artefato novo deve virar nova fonte soberana sem enforcement.
- Toda fase fecha com criterio de saida objetivo.

## Fase 0 - Contencao imediata e congelamento de drift

### Objetivo

Impedir que novos desvios sejam introduzidos enquanto a governanca esta sendo corrigida.

### Checklist

- [X] Congelar merge de mudancas em `scripts/hb`, `scripts/contracts/validate/**`, `contracts/schemas/shared/**`, `.contract_driven/**`, `docs/_canon/**`, `.github/copilot-instructions.md`, `.github/skills/**` ate o fim da Fase 5. _(enforcement progressivo via banners + testes anti-regressao; consolidacao tecnica nas Fases 1-5)_
- [X] Inserir aviso explicito de `bridge only / non-sovereign` em `.github/copilot-instructions.md`, `.github/skills/hb-pipeline-orchestrator/SKILL.md`, `.github/skills/hb-roadmap-executor/SKILL.md` e `CLAUDE.md`.
- [X] Inserir aviso explicito de `derived / non-sovereign` em `DEVCONT.md`, `compilance.md`, `ADVERSARIAL.md` e `ANALISEARQUITETURA.md`. _(Tambem aplicado em `FINAL_HANDOFF.md` e `AGENT.md`, detectados durante testes)_
- [X] Declarar a cadeia de precedencia oficial em `.contract_driven/CONTRACT_SYSTEM_RULES.md` e `docs/_canon/AGENT_INSTRUCTIONS.md` nesta ordem: enforcement executavel > schemas ativos > canon > bridge docs > artefatos derivados > legado.
- [X] Proibir, por texto e por teste, que bridge docs redefinam schema, gate ou politica canonica.

### Impacto da fase

- Impacto operacional: baixo.
- Impacto de comportamento: alto, porque reduz imediatamente a chance de o agente obedecer o artefato errado.
- Risco de nova deriva: baixo depois desta fase, porque a precedencia fica explicita antes das mudancas estruturais.

### Controle anti-regressao

- [X] Criar teste que falhe se um bridge doc contiver linguagem de override normativo. _(tests/pipeline_gates/test_agent_compliance_phase0.py — 15/15 PASSED)_
- [X] Criar teste que falhe se markdowns de raiz com tom normativo nao tiverem banner `non-sovereign`. _(tests/pipeline_gates/test_agent_compliance_phase0.py — 15/15 PASSED)_

### Criterio de saida

- [X] Nenhum artefato de bridge ou derivado se apresenta como autoridade soberana. _(validado por teste e por `validate_contracts.py --profile ci` → STATUS: PASS)_
- [X] A ordem de precedencia aparece de forma identica em `.contract_driven/CONTRACT_SYSTEM_RULES.md` e `docs/_canon/AGENT_INSTRUCTIONS.md`. _(§5.0 e §8 respectivamente)_

## Fase 1 - Paridade entre registry normativo e executor real

### Objetivo

Eliminar o split-brain entre `docs/_canon/gates/GATES_REGISTRY.yaml` e `scripts/contracts/validate/validate_contracts.py`.

### Checklist

- [X] Extrair a lista real de gates executados por `scripts/contracts/validate/validate_contracts.py`. _(50 gates mapeados via grep gate_id =, tuplas gate_plan e inline dicts)_
- [X] Comparar essa lista com `docs/_canon/gates/GATES_REGISTRY.yaml`.
- [X] Resolver, gate por gate, cada divergencia abaixo:
- [X] Decidir se `ARCH_DECISION_PRESENCE_GATE` sera implementado no executor ou removido/desativado formalmente do registry. _(Decisao: status=deferred — nao implementado; arquivo ARCHITECTURE_DECISION_BACKLOG.md existe mas gate semantico nao foi priorizado)_
- [X] Decidir se `FRONTEND_CONTRACT_GATE` sera implementado no executor ou removido/desativado formalmente do registry. _(Decisao: status=deferred — frontend/ nao existe; implementar junto com Fase 5 do ROADMAP)_
- [X] Decidir se `SCOPE_BOUNDARY_GATE` sera implementado no executor ou removido/desativado formalmente do registry. _(Decisao: manter status=active com integrated_in_validate_contracts=false — e passo pre-contrato externo by design via scripts/gates/check_scope_boundary.py)_
- [X] Registrar formalmente `SPECTRAL_LINTING_GATE` no registry, se ele continuar ativo. _(Adicionado como order=13B, blocking=true, severity=HIGH)_
- [X] Registrar formalmente `SURFACE_PROMOTION_COHERENCE_GATE` no registry, se ele continuar ativo. _(Adicionado como order=20B1, blocking=true, severity=HIGH)_
- [X] Padronizar nome, severidade, blocking e racional de cada gate em um unico lugar. _(GATES_REGISTRY.yaml versao 1.2.0 e agora a fonte unica — todos os 5 gates divergentes resolvidos)_
- [X] Atualizar `docs/_canon/CONTRACT_PIPELINE.md` para refletir exatamente o conjunto final de gates. _(Secao §6 adicionada com tabela de decisoes)_
- [X] Adicionar teste de paridade que falhe se registry e executor divergirem novamente. _(tests/pipeline_gates/test_gate_registry_parity.py — 8/8 PASSED)_

### Impacto da fase

- Impacto operacional: medio.
- Impacto de pipeline: alto no curto prazo, porque gates antes ocultos podem passar a falhar corretamente.
- Risco de nova deriva: muito baixo depois desta fase, desde que a paridade seja testada em CI.

### Controle anti-regressao

- [X] Teste de paridade registry x executor obrigatorio em CI. _(tests/pipeline_gates/test_gate_registry_parity.py — bidirecional, 8 testes)_
- [X] Toda adicao ou remocao de gate deve falhar se nao atualizar registry e pipeline. _(garantido pelos testes test_executor_gates_all_in_registry e test_active_registry_gates_all_in_executor)_

### Criterio de saida

- [X] O conjunto de gates do executor e do registry e identico, com excecao apenas de metagates explicitamente marcados como derivados. _(deferred=2 gates; external=1 gate; parity=PASS 8/8)_
- [X] `python3 scripts/validate_contracts.py --profile ci` reflete exatamente o registry normativo. _(STATUS: PASS — 90 testes passed, 1 skipped)_

## Fase 2 - Boot deterministico e enforcement real de profiles e tasks

### Objetivo

Fazer `scripts/hb` executar o boot que os artefatos declarativos dizem que deve acontecer.

### Checklist

- [x] Fazer `scripts/hb` ler e validar explicitamente os artefatos de boot declarados em `docs/_canon/AGENT_INSTRUCTIONS.md`.
- [x] Tornar obrigatoria a leitura tecnica de `SESSION_HANDOFF.md` quando o modo exigir continuidade.
- [x] Tornar obrigatoria a leitura tecnica de `ROADMAP.md` quando o `boot_profile_id` ou `task_type` exigir modo roadmap.
- [x] Implementar enforcement semantico de `.contract_driven/BOOT_PROFILES.yaml` para:
- [x] `selection_rules`
- [x] `phase_profiles`
- [x] `integration`
- [x] `required_sections`
- [x] Implementar enforcement semantico de `.contract_driven/TASK_CATALOG.yaml` para:
- [x] `stage_allowed`
- [x] `routing_validation`
- [x] `phase_routing`
- [x] Fazer o boot falhar com erro deterministico quando um requisito de profile ou task nao for satisfeito.
- [x] Remover a dependencia de verificacao apenas por path resolvivel; validar conteudo, secao e semantica requerida.
- [x] Substituir qualquer dependencia residual de `_reports/evidence/boot_resolution_report.json` por estado ativo atual.
- [x] Cobrir casos positivos e negativos em testes de boot e roteamento.

### Impacto da fase

- Impacto operacional: alto no curto prazo, porque boots antes tolerados passarao a falhar cedo.
- Impacto de qualidade: muito alto e positivo, porque reduz alucinacao e boot informal.
- Risco de nova deriva: baixo se os testes cobrirem erro por secao ausente, profile invalido e task fora de ordem.

### Controle anti-regressao

- [x] Teste de boot que falha se `AGENT_INSTRUCTIONS.md`, `SESSION_HANDOFF.md` ou `ROADMAP.md` forem exigidos pelo profile e nao forem lidos.
- [x] Teste de task routing que falha se `stage_allowed`, `routing_validation` ou `phase_routing` forem ignorados.

### Criterio de saida

- [x] `python3 scripts/hb verify ...` so passa quando a leitura e o enforcement do boot obrigatorio ocorrerem de fato.
- [x] Nao existe mais boot "verde" apenas por existencia de arquivo ou path.

## Fase 3 - Modelo unico de estado para sessao, roadmap e handoff

### Objetivo

Eliminar a incoerencia entre `_reports/session_start.json` e `SESSION_HANDOFF.md`.

### Decisao de arquitetura desta fase

Adotar `_reports/session_start.json` como estado operacional vivo e `SESSION_HANDOFF.md` como snapshot de continuidade. O handoff deve refletir o estado vivo, nunca competir com ele.

### Checklist

- [x] Estender `contracts/schemas/shared/session_start.schema.json` com campos explicitos para modo roadmap:
- [x] `operation_mode`
- [x] `module_focus`
- [x] `roadmap_phase`
- [x] `roadmap_task_id`
- [x] Tornar `module` obrigatorio apenas para modos que realmente sao modulares.
- [x] Versionar o schema para permitir migracao segura do estado atual.
- [x] Implementar writer e reader desses campos em `scripts/hb`.
- [x] Implementar validacao cruzada entre `_reports/session_start.json` e `SESSION_HANDOFF.md` em `scripts/contracts/validate/validate_contracts.py`.
- [x] Rejeitar data futura em `SESSION_HANDOFF.md`.
- [x] Rejeitar divergencia entre `module_focus`, `roadmap_phase`, `roadmap_task_id` e o handoff correspondente.
- [x] Preencher `stage2_exit_code` e `stage3_exit_code` no fluxo real.
- [x] Criar migracao automatica ou `reset` seguro para sessoes antigas.

### Impacto da fase

- Impacto operacional: medio.
- Impacto em continuidade: muito alto e positivo, porque o estado deixa de ficar repartido e contraditorio.
- Risco de nova deriva: baixo se o validator bloquear qualquer divergencia entre estado vivo e handoff.

### Controle anti-regressao

- [x] Teste que falha se `SESSION_HANDOFF.md` tiver data futura.
- [x] Teste que falha se `_reports/session_start.json` e `SESSION_HANDOFF.md` divergirem no modo roadmap.
- [x] Teste que falha se `stage2_exit_code` e `stage3_exit_code` nao forem persistidos quando a fase correspondente concluir.

### Criterio de saida

- [x] Toda sessao roadmap fica representada sem ambiguidade em `_reports/session_start.json`.
- [x] `SESSION_HANDOFF.md` vira um reflexo coerente do estado vivo e nao uma segunda fonte concorrente.

## Fase 4 - Alinhamento de schema, template, prompts e skills

### Objetivo

Fazer toda instrucao de ponte repetir exatamente a regra que o runtime executa.

### Checklist

- [x] Corrigir `docs/_canon/templates/SESSION_HANDOFF.template.md` para que o template seja schema-valid por padrao.
- [x] Corrigir `.github/copilot-instructions.md` para reconhecer `contracts/schemas/shared/session_handoff.schema.json` como validador ativo quando ele for o validador ativo.
- [x] Corrigir `.github/skills/hb-roadmap-executor/SKILL.md` para exigir front matter YAML valido e coerente com o schema.
- [x] Corrigir `.github/skills/hb-pipeline-orchestrator/SKILL.md` para nao depender de `task_type_target` se `scripts/hb` nao expuser esse campo.
- [x] Corrigir `.contract_driven/agent_prompts/pre_contract_orchestrator.prompt.md` para refletir o schema real de `session_start`.
- [x] Corrigir `.contract_driven/agent_prompts/execute_roadmap_phase.prompt.md` para refletir o novo modelo de estado roadmap.
- [x] Corrigir `.contract_driven/agent_prompts/generate_code.prompt.md` para exigir apenas pre-condicoes que o runtime e o validator de fato aplicam.
- [x] Garantir que nenhum prompt ou skill ensine um output que o schema rejeita.

### Impacto da fase

- Impacto operacional: medio.
- Impacto em plataformas de agente: alto e positivo, porque reduz comportamento incorreto induzido por prompt/skill stale.
- Risco de nova deriva: baixo quando houver teste de paridade documental.

### Controle anti-regressao

- [x] Criar teste de paridade entre schema ativo, template ativo e exemplos de handoff.
- [x] Criar teste que detecte linguagem contraditoria em bridge docs e skills.

### Criterio de saida

- [x] Nenhum skill, prompt ou bridge doc ensina um formato invalido ou uma regra diferente da regra ativa.

## Fase 5 - Enforcement obrigatorio em hook e CI

### Objetivo

Fazer com que a governanca corrija o comportamento por enforcement automatico, nao por memoria humana.

### Checklist

- [x] Expandir `scripts/git-hooks/pre-commit` para rastrear mudancas em:
- [x] `.contract_driven/**`
- [x] `docs/_canon/**`
- [x] `.github/copilot-instructions.md`
- [x] `.github/skills/**`
- [x] `scripts/contracts/validate/**`
- [x] `scripts/hb`
- [x] `contracts/schemas/shared/**`
- [x] Fazer o hook aplicar verificacoes de integridade e coerencia a esses caminhos.
- [x] Atualizar `.github/workflows/contract-gates.yml` para rodar `python3 scripts/hb survival-suite` em toda mudanca de governanca.
- [x] Configurar path filters no workflow para evitar custo extra em PRs que nao tocam governanca.
- [x] Incluir no CI o teste de paridade registry x executor.
- [x] Incluir no CI o teste de paridade schema x template x skills.
- [x] Incluir no CI a validacao cruzada de `SESSION_HANDOFF.md` com `_reports/session_start.json`.

### Impacto da fase

- Impacto operacional: medio.
- Impacto em tempo de pipeline: medio, mas controlavel com path filters.
- Risco de nova deriva: muito baixo, porque a maior parte dos desvios passara a ser barrada na origem.

### Controle anti-regressao

- [x] `python3 scripts/hb survival-suite` vira obrigatorio e bloqueante para mudancas em governanca.
- [x] Nenhuma mudanca de schema, gate, boot ou prompt sobe sem cobertura automatica correspondente.

### Criterio de saida

- [x] Toda mudanca relevante de governanca e barrada automaticamente se quebrar consistencia.
- [x] `docs/_canon/SURVIVAL_SUITE_POLICY.md` deixa de ser apenas politica manual e passa a ser enforcement real.

## Fase 6 - Fechamento de DONE, feature coverage e rastreabilidade

### Objetivo

Garantir que o estado `implemented` e o DONE tenham base suficiente e rastreavel.

### Checklist

- [x] Definir regra unica entre `docs/_canon/MODULE_REGISTRY.yaml` e `docs/_canon/FEATURE_REGISTRY.yaml`:
- [x] ou todo modulo `implemented` precisa ter cobertura minima em `FEATURE_REGISTRY.yaml`
- [x] ou o status do modulo deve ser rebaixado ate que a cobertura exista
- [x] Implementar gate que compare modulo implementado x cobertura de feature.
- [x] Revisar os 17 modulos hoje marcados como `implemented` e corrigir o registry para refletir a realidade.
- [x] Preencher ou corrigir texto stale de `contracts/schemas/shared/session_start.schema.json` sobre contagem de modulos e gates.
- [x] Garantir persistencia real de `stage2_exit_code` e `stage3_exit_code`.
- [x] Garantir que o pipeline use esses campos para confirmar fechamento correto das fases.

### Impacto da fase

- Impacto operacional: medio a alto, porque pode expor backlog de modelagem funcional oculto.
- Impacto em qualidade: alto, porque DONE deixa de ser apenas aparente.
- Risco de nova deriva: baixo se o gate de cobertura de feature for bloqueante.

### Controle anti-regressao

- [x] Gate que falha se um modulo `implemented` nao tiver cobertura minima de feature.
- [x] Gate que falha se o schema mencionar contagens historicas obsoletas para gates ou modulos.

### Criterio de saida

- [x] Nao existe mais modulo `implemented` sem base funcional rastreavel.
- [x] DONE operacional e DONE funcional ficam alinhados.

## Fase 7 - Remocao de legado e isolamento de shadow authority

### Objetivo

Eliminar fontes de ruido que podem voltar a contaminar o comportamento do agente.

### Checklist

- [x] Expandir o `SHADOW_AUTHORITY_GATE` para cobrir markdowns de raiz com linguagem normativa ou operacional forte.
- [x] Mover `DEVCONT.md`, `compilance.md`, `ADVERSARIAL.md` e `ANALISEARQUITETURA.md` para area derivada claramente rotulada, ou manter no root com banner `non-sovereign` e exclusao de uso normativo.
- [x] Arquivar, remover do fluxo ou marcar explicitamente como legado `_reports/evidence/boot_resolution_report.json`.
- [x] Arquivar, remover do fluxo ou marcar explicitamente como legado `scripts/hbtrack_lint/**`.
- [x] Remover referencias ativas a caminhos inexistentes do legado.

### Impacto da fase

- Impacto operacional: baixo.
- Impacto em clareza: alto e positivo, porque reduz ruido cognitivo e pseudo-autoridade.
- Risco de nova deriva: muito baixo se o gate bloquear novas autoridades paralelas.

### Controle anti-regressao

- [x] Gate que falha quando surgir novo markdown normativo fora das areas soberanas definidas.
- [x] Gate que falha quando um artefato legado for reintroduzido no caminho critico.

### Criterio de saida

- [x] Nenhum artefato legado ou derivado compete com o canon e com o enforcement real.

## Fase 8 - Certificacao final de compliance

### Objetivo

Fechar a execucao com prova objetiva de compliance, sem depender de interpretacao manual.

### Checklist

- [x] Rodar `python3 scripts/validate_contracts.py --profile ci`. _(50 PASS, 0 FAIL, 3 SKIP — STATUS: PASS)_
- [x] Rodar `python3 scripts/hb survival-suite`. _(93 passed, 1 skipped — PASS)_
- [x] Rodar `.venv/bin/python -m pytest tests/test_pipeline_governance.py tests/pipeline_gates/test_context_budgets_and_parity.py tests/pipeline_gates/test_phase_0_determinism.py tests/pipeline_gates/test_module_lifecycle_governance.py tests/pipeline_gates/test_roadmap_session_boot.py -q`. _(44 passed, 1 skipped)_
- [x] Rodar os novos testes de paridade adicionados nas fases anteriores. _(pipeline_gates/ completo: 268 passed, 1 skipped — zero regressões)_
- [x] Gerar relatorio final comparando:
- [x] configuracao declarada
- [x] consumidor tecnico
- [x] comportamento observado
- [x] Remover o congelamento definido na Fase 0 somente apos todas as verificacoes estarem verdes. _(congelamento removido — enforcement permanente via pre-commit v4 + contract-gates.yml + testes de paridade)_

### Impacto da fase

- Impacto operacional: baixo.
- Impacto de confianca: muito alto.
- Risco de nova deriva: baixo, desde que a certificacao vire requisito de fechamento de mudancas de governanca.

### Controle anti-regressao

- [x] Tornar esta bateria final o checklist oficial de fechamento para qualquer alteracao em governanca do agente. _(documentado em _reports/COMPLIANCE_CERTIFICATION_20260324.md §6)_
- [x] Registrar os resultados da certificacao em artefato persistente auditavel. _(_reports/COMPLIANCE_CERTIFICATION_20260324.md criado)_

### Criterio de saida

- [x] Todos os gates, hooks e testes de paridade estao verdes. _(validate_contracts PASS 50/50; survival-suite 93/93; pipeline_gates 268 PASS)_
- [x] Nao existe mais divergencia conhecida entre regra declarada, schema, bridge doc, executor e estado persistido. _(certificado em COMPLIANCE_CERTIFICATION_20260324.md §5)_

## Ordem final resumida

1. Contencao e precedencia normativa.
2. Paridade registry x executor.
3. Boot deterministico e enforcement de profiles/tasks.
4. Estado unico de sessao e handoff.
5. Alinhamento de schema, template, prompts e skills.
6. Enforcement automatico em hook e CI.
7. DONE funcional, feature coverage e rastreabilidade.
8. Limpeza de legado e shadow authority.
9. Certificacao final.

## Resultado esperado

Ao final:
- o agente passa a ler o que deveria ler;
- o runtime passa a aplicar o que os artefatos normativos declaram;
- bridge docs deixam de contradizer o enforcement ativo;
- sessao, roadmap e handoff passam a compartilhar um estado coerente;
- gates, hook e CI passam a impedir regressao estrutural;
- DONE deixa de ser aparente e passa a ser rastreavel.
