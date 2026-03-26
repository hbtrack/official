A direção correta é esta: não tentar “consertar” o pipeline com mais texto. Para ficar determinístico e sem alucinação no caminho crítico, cada conceito crítico precisa ter um único SSOT machine-readable e cada FAIL material precisa virar exit != 0.

Arquivos centrais a corrigir: PIPELINE_AUDIT.md, CLAUDE.md, SESSION_HANDOFF.md, CONTRACT_SYSTEM_RULES.md, OPERATIONS.md, CONTRACT_PIPELINE.md, GATES_REGISTRY.yaml, pre_contract_orchestrator.prompt.md, validate_contracts.py, scripts/hb, scripts/git-hooks/pre-commit, _reports/session_start.json.

Arquitetura-Alvo

Boot, task routing, gate metadata e sessão não podem depender de texto solto.
Um conceito, uma fonte: boot, task_type, gate metadata, session evidence, hook.
FAIL em fase 0/1/2 sempre gera exit != 0. PASS_WITH_WARNINGS só pode existir fora do caminho crítico.
Hook ativo e hook versionado devem ser o mesmo artefato.
Evidência antiga sai do caminho crítico.
CLAUDE.md vira entrypoint curto; não vira dumping de regras.
SESSION_HANDOFF.md vira delta operacional, não documento de arquitetura.
Recomendação Técnica

Criar docs/_canon/BOOT_PROFILES.yaml como SSOT de boot.
Criar docs/_canon/TASK_CATALOG.yaml como SSOT de task_type -> worker -> status.
Criar contracts/schemas/shared/session_start.schema.json para validar _reports/session_start.json.
Fazer GATES_REGISTRY.yaml virar SSOT de metadata de gate consumida por validate_contracts.py.
Usar .githooks/pre-commit ou scripts/git-hooks/pre-commit como única fonte instalada via core.hooksPath.
Plano de Implementação

Fase	Objetivo	Entregas	Critério de aceite
0. Baseline	Travar o estado atual antes da refatoração	Criar testes vermelhos para todos os bloqueadores do laudo	Os testes falham exatamente nos loopholes atuais
1. Autoridade única	Eliminar fontes fantasmas e catálogos duplicados	BOOT_PROFILES.yaml, TASK_CATALOG.yaml, repoint de CLAUDE/RULES/PIPELINE/orchestrator	rg "CLAUDE.md §7" não retorna referência ativa de boot; task catalog é único
2. Modelo de sessão	Tornar _reports/session_start.json prova real, não formalidade	Schema JSON, pipeline_version, task_type, module, boot_profile_id, write_scope, stage2_artifacts[].sha256, validated_at, validator_run_id	unknown deixa de existir; artefato revalidado atualiza hash e resultado
3. CLI rígida	Fechar scripts/hb contra defaults implícitos	hb verify --task-type --module, hb check --module --scope, hb artifact <path> com upsert por hash	hb verify sem args falha; hb check sem módulo falha
4. Validator determinístico	Fazer a execução refletir o registry e as fases reais	Stage contracts explícitos, leitura do metadata do registry, FAIL material => nonzero, alinhamento de UI_DOC_VALIDATION_GATE	Artifact com UI/OpenAPI desalinhados retorna nonzero
5. Hook único e forte	Impedir bypass local e stale evidence	Hook único versionado, core.hooksPath, parse error = block, hash do staged blob = obrigatório	JSON corrompido bloqueia commit; arquivo alterado após validação bloqueia commit
6. Limpeza do legado	Remover o modelo duplo antigo+novo	Tirar boot_resolution_report.json e _reports/agent_execution/latest.json do fluxo ativo; cortar claims arquiteturais do handoff	`rg "boot_resolution_report
7. Redução de contexto	Fazer a simplificação ser real e não cosmética	Enxugar CLAUDE, SESSION_HANDOFF, RULES, PIPELINE, OPERATIONS	Budgets de contexto cumpridos e sem perda de decisão
8. CI e regressão	Garantir estabilidade entre execuções	Testes de paridade, integração shell, golden tests de docs e hooks	Local e CI produzem o mesmo resultado para a mesma entrada
Detalhe por Fase

Fase 0:
Adicionar testes para: hb verify com unknown, hb check sem módulo, hb artifact com UI gate em FAIL, parse error no session_start, hash stale, divergência de hook.
Fase 1:
Migrar todas as referências de boot para BOOT_PROFILES.yaml.
Definir no TASK_CATALOG.yaml se generate_code e generate_frontend são active, frozen ou disabled.
Se forem congelados, o stage 0 deve bloquear com código explícito, não por omissão.
Fase 2:
Schema mínimo obrigatório para sessão:
pipeline_version, session_id, task_type, module, branch, boot_profile_id, write_scope, stage0_exit_code, stage1_exit_code, stage2_artifacts[{path, sha256, exit_code, validated_at, validator_run_id}].
write_scope não pode ser opcional no caminho crítico.
Fase 3:
scripts/hb não pode mais depender de env implícito.
hb artifact deve fazer upsert por path, recalcular hash e sobrescrever resultado anterior.
Incluir hb reset para iniciar sessão limpa e evitar resíduos.
Fase 4:
validate_contracts.py precisa consumir o metadata do registry em vez de duplicá-lo.
UI_DOC_VALIDATION_GATE precisa ter uma única semântica. Escolha uma e propague.
Stage 0 deve validar task_type, module, worker existence, boot profile.
Stage 1 deve validar module, write_scope, adversarial readiness.
Stage 2 deve falhar em qualquer FAIL material do artefato.
Fase 5:
O hook deve ler o blob staged, não o working tree.
session_start.json inválido, corrompido, stale ou com hash divergente deve bloquear.
O hook ativo deve ser instalado a partir da versão versionada, sem diferença local.
Fase 6:
SESSION_HANDOFF.md passa a conter só: estado atual, bloqueios atuais, próximos passos, decisões pendentes.
CLAUDE.md passa a conter só entrypoint, hard rules e ponteiros.
O orchestrator para de publicar evidência antiga.
Fase 7:
Metas de contexto:
CLAUDE.md <= 450 palavras.
SESSION_HANDOFF.md <= 350 palavras.
CONTRACT_PIPELINE.md <= 600 palavras.
pre_contract_orchestrator.prompt.md <= 700 palavras.
Boot base <= 2 arquivos permanentes.
Hand-off para worker <= 5 artefatos obrigatórios por task.
Matriz de Testes Obrigatória

hb verify sem --task-type ou --module => falha.
hb check sem --module => falha.
hb artifact com UI_DOC_VALIDATION_GATE=FAIL => falha.
session_start.json com unknown => hook bloqueia.
session_start.json corrompido => hook bloqueia.
Artefato validado e depois alterado => hook bloqueia por hash divergente.
Hook ativo e hook versionado => conteúdo idêntico.
TASK_CATALOG.yaml e roteamento em docs/prompts => teste de paridade.
GATES_REGISTRY.yaml e executor => teste de paridade.
rg "CLAUDE.md §7" => zero referências ativas de boot.
rg "boot_resolution_report|agent_execution/latest" => zero referências ativas no fluxo oficial.
Sequência de PRs

PR1: testes vermelhos + novos SSOTs BOOT_PROFILES, TASK_CATALOG, session_start.schema.
PR2: endurecimento de scripts/hb e do state model.
PR3: alinhamento de validate_contracts.py com GATES_REGISTRY.yaml.
PR4: hook único e instalação via core.hooksPath.
PR5: remoção do legado e limpeza de contexto.
PR6: CI, regressão e budgets de contexto.
Definition of Done

Não existe mais default implícito em ponto crítico.
Não existe mais fonte fantasma de boot.
Não existe mais FAIL material com exit 0 nas fases 0/1/2.
Não existe mais divergência entre hook local e hook versionado.
Não existe mais evidência stale aceitando commit.
Não existe mais pipeline antigo concorrendo com o novo.
O conjunto de task types, gates e regras de boot é único e testado.