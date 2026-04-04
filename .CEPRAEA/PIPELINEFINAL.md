# PIPELINEFINAL

## 0. Base desta auditoria

- Escopo validado: varredura integral dos 314 arquivos em `.contract_driven/`, `.github/` e `docs/`.
- Extras lidos para enforcement real: `scripts/hb`, `scripts/contracts/validate/validate_contracts.py`, `scripts/contracts/validate/tooling_config_gate.py`, `scripts/hooks/check_backend_gate.py`, `scripts/hooks/check_session_commit.py`, `scripts/git-hooks/pre-commit`, `contracts/schemas/shared/session_handoff.schema.json`, `contracts/schemas/shared/session_start.schema.json`, `CLAUDE.md`, `.claude/settings.local.json`, `.codex`.
- Estado atual do pipeline: `python3 scripts/validate_contracts.py --profile ci` em `_reports/contract_gates/latest.json` esta `PASS`.
- Limite atual do ambiente local: `python3 scripts/hb survival-suite` falha por falta de `pytest`, portanto a governanca completa nao esta plenamente reproduzivel localmente.

## 0.1 Validacao deste documento contra o sistema atual

Blocos que ficaram validados como verdadeiros no sistema atual:

- existe pipeline executavel real de contratos, gates, CI e deploy com validacao live
- nao existe backend codegen deterministico oficial
- `generate_code` ainda e o driver oficial de implementacao backend
- o ruleset atual de merge exige apenas `Validate Contract Gates`
- `generate_code` ainda aceita modulo em `validated_contract`
- existem modulos OpenAPI em ref direto ao schema soberano e outros ainda em projecao
- `ARCH_DECISION_PRESENCE_GATE` segue `deferred`
- o fluxo `implementation_ready -> implemented` ainda nao tem worker formal unico

Blocos que exigiram ajuste de formulacao para ficarem tecnicamente corretos:

- "contratos 100 por cento fieis a `.contract_driven`":
  - ajuste correto: `.contract_driven` deve governar boot, routing, gating, prompts e handoff
  - o conteudo substantivo dos contratos deve nascer de `docs/_canon` + `docs/hbtrack/modulos` + IR estruturado
- "OpenAPI 1:1":
  - ajuste correto: a validacao atual foi feita em `contracts/openapi/components/schemas/**`, nao em toda a superficie HTTP end-to-end
- "sincronismo perfeito":
  - ajuste correto: so e possivel com source master unico e artefatos derivados; com edicao manual multipla isso e impossivel
- "apagar o codigo atual e gerar tudo de novo":
  - ajuste correto: isso so e seguro depois de haver codegen deterministico, parity harness, replay staging e estrategia de cutover

Blocos rejeitados como estrategia imediata:

- apagar todo `src/` agora e reescrever tudo em big-bang
- manter contratos, docs e codigo todos editaveis manualmente e ainda prometer drift zero

## 1. Veredito validado

- O HB Track ja possui um ecossistema real de Contract Driven Development + Decision Support System + validator + CI + deploy com validacao live.
- O sistema atual ainda nao torna o agente incapaz de alucinar ou inferir. Ele reduz fortemente a inferencia, mas ainda depende de gates, hooks, prompts, CI e disciplina operacional.
- O caminho oficial atual de implementacao backend e o worker `generate_code`, mas nao existe hoje um gerador deterministico de backend equivalente a um compilador.
- Os contratos atuais sao melhores do que "contratos bonitos", porque existe enforcement real. Mesmo assim, eles ainda nao sao uniformemente excelentes nem uniformemente fieis por construcao.
- O maior problema estrutural atual e este: o repositorio ainda opera com multiplas superficies manuais que se sobrepoem. Com multi-master editing, sincronismo perfeito e drift zero sao impossiveis.

## 2. Respostas criticas validadas

### 2.1 Qual e o gerador oficial e deterministico de backend

- O caminho oficial e `generate_code`, definido em `.contract_driven/TASK_CATALOG.yaml` e implementado operacionalmente por `.contract_driven/agent_prompts/generate_code.prompt.md`.
- `scripts/generate/` hoje cobre artefatos derivados deterministas, nao backend canonico.
- Portanto:
  - gerador oficial de backend: `generate_code`
  - gerador deterministico de backend: nao existe hoje

### 2.2 Quais modulos ja tem OpenAPI 1:1 com schemas soberanos

No nivel de `contracts/openapi/components/schemas/**`, hoje estao em ref direto para os schemas soberanos:

- `analytics`
- `audit`
- `identity_access`
- `matches`
- `medical`
- `scout`

Ainda usam projecoes OpenAPI proprias:

- `ai_ingestion`
- `competitions`
- `exercises`
- `notifications`
- `reports`
- `seasons`
- `teams`
- `training`
- `users`
- `video`
- `wellness`

Observacao vital:

- isso responde pela camada `components/schemas`
- um modulo "1:1" aqui ainda pode ter `paths` com envelopes, recortes ou composicoes
- a meta correta nao e "alguns componentes referenciam o schema", mas sim "todo payload HTTP nasce do mesmo source graph soberano"

### 2.3 Quais gates sao obrigatorios para merge por branch protection

Estado atual confirmado via GitHub:

- `main` nao usa branch protection classico
- existe um ruleset ativo chamado `contract-gates`
- o ruleset exige um unico status check: `Validate Contract Gates`
- o ruleset nao exige approvers humanos
- o ruleset nao exige code owner review
- o ruleset nao exige resolucao de review threads

Consequencia pratica:

- tudo que falha dentro do job `Validate Contract Gates` e merge-blocking
- o job `Validate Contract Gates` roda `python3 scripts/validate_contracts.py`
- portanto, os gates bloqueantes executados por `validate_contracts.py` sao hoje os gates realmente merge-blocking

Hoje sao disciplina operacional, mas nao branch-protected pelo ruleset:

- `Governance Tests`
- `Architecture Drift Check`
- `Governance Enforcement (survival-suite)`
- `Paridade Registry x Executor`
- `Paridade Schema x Template x Skills`
- `Validacao Cruzada SESSION_HANDOFF x session_start`
- o workflow `CI` como um todo

### 2.4 Evidencia minima para `validated_contract -> implementation_ready`

Este caminho esta formalizado e e o mais consistente do sistema atual.

Minimo exigido hoje:

- modulo em `validated_contract` no `docs/_canon/MODULE_REGISTRY.yaml`
- `_reports/contract_gates/latest.json` com `overall_status = PASS`
- sem decisoes arquiteturais abertas no backlog
- todas as `expected_surfaces` do modulo presentes
- artefatos nao vazios e sem placeholder
- adversarial analysis executada e com `PASS`
- confirmacao humana substantiva
- atualizacao do `MODULE_REGISTRY`
- atualizacao do `_reports/evidence/module_readiness_scorecard.json`
- revalidacao do pipeline apos a promocao

### 2.5 Evidencia minima para `implementation_ready -> implemented`

Este caminho existe no canon, mas esta menos formalizado do que o anterior.

Minimo hoje inferido do canon e do enforcement:

- codigo materializado em `src/<module>/`
- `api.py`, `migrations/` e `tests/` presentes
- runtime real e testes reais do modulo
- pelo menos uma feature do modulo marcada como `implemented` no `FEATURE_REGISTRY`

Gap importante:

- nao encontrei um worker formal unico para promover `implementation_ready -> implemented`
- essa transicao depende hoje de semantica distribuida em `CONTRACT_PIPELINE`, `MODULE_REGISTRY`, `generate_code`, `FEATURE_COVERAGE_GATE` e `check_architecture_docs.py`

## 3. Diagnostico dos gaps reais

### P0 - Gaps criticos

- Nao existe backend codegen deterministico. O backend ainda e agent-driven, nao contract-compiled.
- O ruleset de merge exige apenas `Validate Contract Gates`. Isso e insuficiente para governanca total.
- O sistema ainda aceita `generate_code` a partir de `validated_contract`, quando o target-state correto deveria ser `implementation_ready`.
- Existem docs stale em `docs/guias/` que contradizem o estado executavel atual.
- O sincronismo entre `docs/_canon`, `docs/hbtrack/modulos`, `.contract_driven`, `contracts/**` e `src/**` ainda nao e de source unico com geracao automatica.
- Existem projecoes OpenAPI manuais que nao nascem do mesmo source graph dos schemas soberanos.
- O fluxo `implementation_ready -> implemented` ainda nao tem promotion worker formal.
- O DSS ainda nao esta fechado end-to-end por gate tecnico obrigatorio em todos os pontos.

### P1 - Gaps altos

- `ARCH_DECISION_PRESENCE_GATE` segue `deferred`.
- `check_backend_gate.py` tem comportamento fail-open em erro.
- `stage_allowed` em `scripts/hb` e warning, nao bloqueio hard.
- `CLAUDE.md` e `.codex` nao tem o mesmo nivel de bridge local que Copilot.
- `survival-suite` nao e reproduzivel localmente sem ajustar deps.
- Nem todo modulo HTTP esta 1:1 com o schema soberano.
- Parte da superficie continua fora do escopo CDD hard, como `config/`, `infra/`, `.github/workflows/`, `frontend/`, `mobile/`.

### P2 - Gaps estruturais

- O sistema ainda usa Markdown livre como fonte normativa para partes que exigem sincronismo absoluto.
- Prompts ainda carregam responsabilidade substantiva demais.
- Nao existe um grafo canonico de dependencias entre regra, modulo, schema, path, evento, teste e codigo.
- Nao existe propagacao automatica obrigatoria de mudanca entre doc -> contrato -> codigo -> teste.

## 4. Principio nao-negociavel para eliminar drift

Sincronismo perfeito nao e atingivel com multi-master editing.

Para garantir fidelidade total, o HB Track precisa migrar para:

- um unico source graph soberano
- varios artefatos derivados gerados automaticamente
- zero edicao manual em artefatos derivados

Traducao pratica:

- `docs/_canon` deve guardar somente regra global, registry, ADR, policy e mapping canonico
- `docs/hbtrack/modulos` deve guardar somente verdade funcional e semantica do modulo
- `.contract_driven` deve guardar somente boot, routing, prompts, tasks, manifests e regra de execucao
- `contracts/**`, bridge docs, parte de `docs/guias/` e grande parte do codigo scaffolding devem passar a ser derivados

## 5. Target-state obrigatorio

Quando este plano estiver integralmente implementado e todos os criterios de saida estiverem verdes, o sistema passara a ter:

- contratos 100 por cento fieis ao canon substantivo em `docs/_canon` e `docs/hbtrack/modulos`
- contratos 100 por cento fieis a governanca de execucao em `.contract_driven`
- contratos 100 por cento fieis a `docs/hbtrack/modulos`
- `docs/hbtrack/modulos` 100 por cento fieis ao canon global quando houver regra compartilhada, sem capacidade de override local
- atualizacao automatica e obrigatoria entre doc, contrato, teste e codigo
- drift bloqueado tecnicamente, nao apenas detectado tardiamente
- agente guiado por bundle compilado e deterministico, nao por leitura dispersa

## 5.1 Regras deterministicas de autoridade

Para remover ambiguidade, estas regras passam a ser parte do target-state:

- `docs/_canon/**` e a fonte master para:
  - politicas globais
  - lifecycle
  - registries
  - ADRs
  - mappings globais
- `docs/hbtrack/modulos/<module>/**` e a fonte master para:
  - semantica funcional do modulo
  - regras de dominio do modulo
  - invariants
  - state model
  - permissions
  - erros e cenarios de teste do modulo
- `.contract_driven/**` e a fonte master para:
  - boot
  - perfis
  - routing
  - prompts operacionais
  - task catalog
  - handoff e governanca de execucao
- `contracts/**` deve ser derivado do source graph soberano; nao pode ser master de negocio
- `src/**` deve ser derivado ou extension point controlado; nao pode redefinir contrato nem regra soberana

Regra de conflito:

- se `docs/hbtrack/modulos` conflitar com `docs/_canon` em regra global, `docs/_canon` prevalece
- se `.contract_driven` conflitar com conteudo substantivo de dominio, o source graph soberano prevalece
- se `contracts/**` conflitar com o source graph soberano, `contracts/**` deve ser regenerado, nao corrigido manualmente

## 6. Plano de correcao e hardening

## 6.0 Regras de execucao sem pendencia

Para que nenhuma fase deixe o sistema em estado intermediario perigoso, cada fase deve obedecer:

- nao introduzir dual-authority permanente
- nao criar artefato gerado sem gate de freshness correspondente
- nao mudar regra normativa sem atualizar automaticamente todos os consumidores obrigatorios
- nao remover codigo legado antes de existir substituto gerado, testado e validado em staging
- cada fase deve fechar com:
  - gate novo ativo
  - teste anti-regressao
  - ruleset/CI atualizado quando o risco for de governanca
  - rollback definido

Formato obrigatorio de cada entrega:

- entrada canonica
- transformacao deterministica
- saida canonica
- gates de verificacao
- criterio de promocao
- criterio de rollback

### Fase 0 - Congelamento de drift e reclassificacao de autoridade

Objetivo:

- parar de tratar muitos arquivos como soberanos ao mesmo tempo

Acoes:

- declarar em um novo `docs/_canon/SOURCE_AUTHORITY_GRAPH.yaml` qual artefato e master para cada conceito
- proibir por gate que um mesmo conceito tenha dois masters
- reclassificar `docs/guias/**` como derivado ou archival, nunca normativo
- criar banner obrigatorio `DERIVED - DO NOT EDIT` em todo arquivo gerado
- criar `NON_SOVEREIGN_BRIDGE` para todo bridge doc de agente

Criterio de saida:

- todo conceito relevante do sistema tem exatamente um owner source
- nenhum arquivo derivado se apresenta como autoridade

### Fase 1 - Estruturar o canon para geracao, nao para leitura humana apenas

Objetivo:

- transformar a base normativa em dados compilaveis

Acoes:

- introduzir companion files estruturados para regras livres de markdown:
  - `docs/_canon/graph/*.yaml`
  - `docs/hbtrack/modulos/<module>/graph/*.yaml`
- cada modulo passa a ter IR soberano por feature, entidade, endpoint, evento, state machine, permission, error model e test obligation
- markdowns viram views derivadas do IR, nao fonte primaria unica
- `docs/hbtrack/modulos` passa a ter manifest fixo por modulo com hash de sincronismo

Criterio de saida:

- nenhuma regra critica depende apenas de frase solta em markdown
- todo dado necessario para gerar contrato e codigo existe em IR estruturado

### Fase 2 - Criar o compiler de sincronismo soberano

Objetivo:

- gerar contratos, docs derivadas e bundles de agente a partir do source graph

Acoes:

- criar `scripts/compile/compile_source_graph.py`
- entradas:
  - `docs/_canon/**`
  - `docs/hbtrack/modulos/**`
  - `.contract_driven/**`
- saidas geradas:
  - `contracts/openapi/**`
  - `contracts/asyncapi/**`
  - `contracts/workflows/**`
  - views derivadas em `docs/guias/**`
  - bridge docs de agente
  - bundles de contexto por modulo e por feature
- toda mudanca em source soberano dispara recompilacao obrigatoria

Criterio de saida:

- `contracts/**` deixa de ser editado manualmente nos pontos que puderem ser compilados
- `docs/guias/**` nao diverge mais do estado real

Detalhe deterministico obrigatorio:

- o compiler deve gerar um `impact_report.json` listando exatamente:
  - quais modulos foram impactados
  - quais contratos foram regenerados
  - quais bundles de agente foram regenerados
  - quais testes devem rodar
  - quais artefatos antigos ficaram obsoletos

### Fase 3 - Eliminar projecoes OpenAPI manuais

Objetivo:

- fazer OpenAPI nascer do mesmo source graph dos schemas soberanos

Acoes:

- banir projecoes manuais nao justificadas em `contracts/openapi/components/schemas/**`
- todo payload HTTP deve:
  - referenciar schema soberano
  - ou ser derivado automaticamente de um source graph tipado e rastreavel
- adicionar justificativa obrigatoria para qualquer projection exception
- criar `OPENAPI_SCHEMA_EQUIVALENCE_GATE`

Criterio de saida:

- todo componente OpenAPI e:
  - ref direto ao schema soberano
  - ou derivado automaticamente com mapa de equivalencia campo a campo

### Fase 4 - Criar backend codegen deterministico

Objetivo:

- sair de implementacao agent-driven para implementacao contract-compiled

Acoes:

- criar `scripts/generate/backend_codegen.py`
- gerar deterministicamente:
  - `src/<module>/generated/schemas.py`
  - `src/<module>/generated/api.py`
  - `src/<module>/generated/domain/entities.py`
  - `src/<module>/generated/application/use_cases.py`
  - `src/<module>/generated/infrastructure/repository.py`
  - `src/<module>/generated/tests/*`
  - `src/<module>/generated/migrations/*` quando aplicavel
- manter arquivos canônicos de runtime como adaptadores estaveis:
  - `src/<module>/api.py`
  - `src/<module>/schemas.py`
  - `src/<module>/models.py`
- esses arquivos de runtime devem apenas importar ou compor a camada gerada e pontos de extensao controlados
- separar claramente:
  - zona gerada
  - zona de extensao manual
- proibir edicao manual dentro de `src/<module>/generated/**`
- criar hash manifest por artefato gerado
- adicionar `CODEGEN_DRIFT_GATE`

Criterio de saida:

- o codigo estrutural do backend nasce do contrato
- o agente deixa de "inventar" estrutura base

### Fase 4A - Estrategia deterministica para o codigo atual

Decisao validada contra o sistema atual:

- hoje existe backend materializado coerente em `src/` para 17 modulos
- portanto, apagar tudo agora geraria risco desnecessario e pendencias enormes
- a estrategia correta nao e big-bang delete
- a estrategia correta e regeneracao limpa controlada por modulo

Estrategia obrigatoria:

1. congelar edicao manual nas superficies que vao virar geradas
2. criar camada `generated/` para um modulo piloto
3. comparar comportamento antigo vs novo por:
   - snapshot de contrato
   - testes do modulo
   - replay de fluxo real
   - validacao em staging
4. so depois do parity PASS:
   - trocar adaptadores canonicos para apontar para o codigo gerado
   - remover implementacao manual antiga daquele modulo
5. repetir modulo a modulo

Proibicao:

- e proibido remover todos os modulos de `src/` antes de existir codegen deterministico validado e parity harness verde

### Fase 5 - Formalizar todas as promocoes de status

Objetivo:

- transformar lifecycle inteiro em workflow tecnico, nao em semantica dispersa

Acoes:

- restringir `generate_code` para `implementation_ready` apenas
- criar worker formal `implementation_promotion`
- criar worker formal `staging_promotion`
- criar worker formal `release_promotion`
- cada promocao deve ter:
  - inputs canonicos
  - evidence bundle
  - gates obrigatorios
  - atualizacoes atomicas em registry

Workers obrigatorios do lifecycle:

- `readiness_promotion`
- `implementation_promotion`
- `staging_promotion`
- `release_promotion`

Bundles minimos por worker:

- input manifest
- evidence manifest
- impacted artifacts
- gates executed
- promotion decision
- rollback target

Criterio de saida:

- nenhuma mudanca de status acontece fora de worker formal
- `implementation_ready -> implemented` deixa de ser lacuna

### Fase 6 - Hardening de DSS e de aprovacao humana

Objetivo:

- impedir inferencia silenciosa em decisao arquitetural e em design de dominio

Acoes:

- implementar `ARCH_DECISION_PRESENCE_GATE`
- transformar toda decisao critica em ADR ou entry formal de backlog antes de contrato
- DSS passa a produzir somente:
  - proposta
  - comparacao
  - impacto
  - risco
  - recomendacao
- DSS nao escreve contrato nem codigo diretamente
- criar `DECISION_TO_CONTRACT_TRACE_GATE`

Criterio de saida:

- nao existe contrato ou codigo com premissa critica sem rastro de decisao humana aprovada

### Fase 7 - Endurecer hooks, CI e merge rules

Objetivo:

- mover governanca de "boa pratica" para "enforcement de merge"

Acoes:

- tornar `check_backend_gate.py` fail-closed
- tornar `stage_allowed` bloqueio hard
- expandir GOVERNANCE_PATHS para incluir:
  - `.github/agents/**`
  - `.github/instructions/**`
  - `CLAUDE.md`
  - `.codex`
- atualizar ruleset do GitHub para exigir:
  - `Validate Contract Gates`
  - `Governance Tests`
  - `Architecture Drift Check`
  - `CI / Validate Contracts`
  - `CI / Tests`
  - checks de frontend quando houver impacto
- exigir no minimo 1 aprovacao humana
- exigir thread resolution

Criterio de saida:

- merge sem governanca total verde deixa de ser possivel

### Fase 8 - Sincronismo automatico doc -> contrato -> codigo -> teste

Objetivo:

- impedir qualquer update parcial

Acoes:

- criar `SYNC_MANIFEST.yaml` com mapa de propagacao obrigatoria
- para cada tipo de mudanca, declarar consumers obrigatorios
- regras deterministicas minimas:
  - mudanca em `docs/_canon` global atualiza contratos afetados, bundles de agente, docs derivadas, impact report e testes afetados
  - mudanca em `docs/hbtrack/modulos/<module>` atualiza contratos do modulo, codigo gerado do modulo, testes do modulo e views derivadas
  - mudanca em `.contract_driven` atualiza bridge docs, schemas de sessao, handoff templates e testes de prompt/schema parity
  - mudanca em source graph de contrato atualiza obrigatoriamente backend codegen dos modulos impactados
  - mudanca em regra global que afeta runtime invalida qualquer bundle compilado anterior
- adicionar `PARTIAL_UPDATE_GATE`
- adicionar `IMPACT_ANALYSIS_GATE`

Criterio de saida:

- nenhuma alteracao normativa consegue entrar sem todos os consumers atualizados

### Fase 9 - Bundle compilado para o agente

Objetivo:

- fazer o agente sempre saber exatamente como desenvolver, sem leitura dispersa e sem inferencia

Acoes:

- gerar automaticamente `compiled_context/<module>/<feature>.json`
- cada bundle deve conter:
  - regras globais aplicaveis
  - decisoes aprovadas
  - schemas
  - endpoints
  - eventos
  - state transitions
  - permissions
  - invariants
  - test obligations
  - codegen targets
- prompts passam a consumir bundle compilado, nao floresta de markdown solto
- adicionar `CONTEXT_BUNDLE_FRESHNESS_GATE`

Criterio de saida:

- o agente recebe um pacote fechado e rastreavel para cada tarefa

### Fase 10 - Validacao de mundo real sem gaps

Objetivo:

- garantir que o sistema final nao apenas parece coerente, mas roda no mundo real

Acoes:

- tornar `HTTP_RUNTIME_CONTRACT_GATE` obrigatorio em ambiente de staging antes de release
- ativar de fato o `PACT_PROVIDER_GATE` com broker funcional
- criar seeded staging dataset por modulo
- criar cenarios de negocio reais por modulo e por ciclo operacional
- adicionar replay de fluxo real em staging
- atrelar promocao para `staging_validated` a evidencia operacional salva

Criterio de saida:

- nenhuma release passa sem validacao live, rastreavel e reproduzivel

## 7. O que deve ser corrigido e nao foi pedido, mas e vital

- A arquitetura precisa abandonar multi-master editing. Sem isso, "sincronismo perfeito" e promessa falsa.
- `docs/guias/**` precisa perder qualquer peso normativo residual.
- O fluxo de `implemented`, `staging_validated` e `released` precisa ter workers formais, nao apenas semantica em texto.
- O backend precisa de codegen deterministico real.
- O ruleset do GitHub precisa ser endurecido. Hoje ele protege pouco.
- O DSS precisa ser fechado como sistema de aprovacao, nao como fonte de conteudo direto.
- Os prompts precisam deixar de carregar regra substantiva que nao exista no source graph.
- `Codex` precisa de bridge local equivalente e gerado automaticamente.
- `Claude` precisa de bridge local mais forte do que um arquivo de permissoes vazio.
- `survival-suite` precisa ser verde localmente por padrao.

## 8. O que nao foi citado, mas deveria ser tratado como ajuste critico

- Criar uma taxonomia formal de "projection allowed" vs "projection forbidden".
- Criar um diff semantico, nao apenas textual, entre:
  - canon global
  - docs de modulo
  - contratos
  - codigo gerado
- Criar coverage por campo e nao apenas por arquivo.
- Criar ownership tecnico por modulo e por feature.
- Criar merge queue com compilacao e replay automatico.
- Criar baseline adversarial fixa para toda fase de promocao.
- Registrar hash de source graph por release.

## 9. Melhorias que aceleram muito o desenvolvimento com IA

- backend codegen deterministico para scaffolding estrutural
- bundle compilado por modulo e por feature, reduzindo contexto e custo de prompt
- impact analysis automatico, evitando leitura manual do repositorio inteiro a cada mudanca
- replay pack de cenarios reais por modulo
- golden tests por feature
- seed pack de staging por ciclo de negocio
- roteamento automatico de tarefas por feature, nao apenas por modulo
- template unico de promotion evidence bundle
- geracao automatica de PR checklist por tipo de mudanca
- suporte a "one command build":
  - `hb sync`
  - `hb compile`
  - `hb promote`
  - `hb verify-live`

## 10. Plano de acoes em ordem de execucao

### Ordem obrigatoria

1. Congelar drift e reclassificar autoridade
2. Estruturar source graph soberano
3. Implementar compiler de sincronismo
4. Eliminar projecoes manuais OpenAPI
5. Implementar backend codegen deterministico
6. Formalizar promocoes de status
7. Endurecer DSS, hooks, CI e merge rules
8. Tornar sincronismo doc -> contrato -> codigo -> teste automatico
9. Migrar prompts para bundles compilados
10. Fechar validacao live e Pact

### Resultado esperado por fase

- Fase 0 a 2: fim do split-brain documental
- Fase 3 a 5: fim da geracao backend por inferencia estrutural
- Fase 6 a 8: fim de atualizacao parcial e governanca fraca
- Fase 9 a 10: agente operando sobre bundle deterministico e sistema validado em ambiente real

## 10.1 Sequencia operacional sem ambiguidade

Para qualquer mudanca futura, o fluxo obrigatorio deve ser este:

1. editar apenas o source master correto
2. rodar compiler de source graph
3. rodar codegen dos modulos impactados
4. rodar testes impactados
5. rodar `validate_contracts.py --profile ci`
6. rodar replay de staging quando houver impacto funcional
7. so entao promover status ou abrir merge

Se qualquer etapa falhar:

- a alteracao nao pode ser promovida
- os artefatos gerados devem ser regenerados ou descartados
- nenhum ajuste manual downstream e permitido como "atalho"

## 11. Adversarial acceptance criteria

Estas garantias so podem ser declaradas como verdadeiras depois que todas as suites abaixo estiverem verdes sem warning.

### CA - O plano e suas implementacoes devem passar em analise adversarial forte

Suites obrigatorias:

- authority drift suite
- source graph ambiguity suite
- partial update suite
- prompt/schema parity suite
- doc/contract parity suite
- contract/code parity suite
- projection drift suite
- promotion coherence suite
- DSS traceability suite
- runtime conformance suite
- stale bundle suite
- merge-rules enforcement suite

Regra:

- zero warning
- zero skip indevido
- zero fallback silencioso

### CA2 - Fluxo pronto para desenvolver todo o sistema e validar no mundo real

So pode ser declarado verdadeiro quando:

- backend codegen deterministico estiver ativo
- source graph soberano estiver ativo
- sincronismo automatico estiver ativo
- ruleset de merge estiver endurecido
- runtime staging e production validation estiverem ativas
- Pact e smoke/live checks estiverem operacionais
- parity harness entre codigo legado e codigo regenerado estiver ativo durante a migracao

### CA3 - Agente sempre saber como desenvolver sem inferencia

So pode ser declarado verdadeiro quando:

- toda tarefa consumir bundle compilado por feature
- nao existir regra substantiva exclusiva em prompt
- toda decisao critica estiver aprovada e rastreada
- toda mudanca disparar propagacao automatica obrigatoria
- todo codigo estrutural nascer de codegen deterministico
- os bundles compilados forem a unica entrada operacional permitida para tasks de implementacao

## 12. Definicao honesta de "100 por cento"

No contexto do HB Track, "100 por cento" so pode ser aceito com esta definicao:

- 100 por cento dos conceitos relevantes tem source master unico
- 100 por cento dos derivados sao regenerados automaticamente
- 100 por cento dos updates normativos tem propagacao obrigatoria
- 100 por cento dos merges passam por checks obrigatorios
- 100 por cento das promocoes de status passam por worker formal
- 100 por cento dos contratos relevantes passam por equivalencia semantica com o source graph
- 100 por cento do codigo estrutural nasce de codegen deterministico ou extension point controlado

Sem isso, "100 por cento" vira slogan, nao engenharia.

## 13. Conclusao executiva

O HB Track esta perto de um sistema forte de desenvolvimento por IA, mas ainda nao esta no estado de perfeicao operacional que voce descreveu.

Para chegar la, o repositorio precisa parar de operar como um conjunto de documentos paralelos e passar a operar como um sistema de compilacao normativa:

- um source graph soberano
- varios derivados gerados
- promocao formal de lifecycle
- codegen deterministico
- merge rules endurecidas
- validacao live obrigatoria
- agente consumindo bundles compilados e nao texto disperso

Quando isso estiver implementado e todos os criterios de saida acima estiverem verdes, ai sim o fluxo estara pronto para desenvolver todo o HB Track com nivel maximo de compliance, velocidade e previsibilidade.

## 14. Decisao executiva sobre apagar o codigo atual

Validacao contra o sistema atual:

- o codigo atual em `src/` existe para 17 modulos e esta coerente com o `MODULE_REGISTRY`
- o repositrio possui deploy, health check, validacao de contratos e sinal de runtime real
- portanto, apagar tudo agora seria tecnicamente regressivo

Decisao:

- apagar o codigo atual inteiro agora: reprovado
- substituir o codigo atual modulo a modulo por geracao limpa e validada: aprovado

Plano de substituicao limpa:

1. escolher um modulo piloto de baixa centralidade
2. compilar source graph do modulo
3. gerar backend novo do modulo em `generated/`
4. rodar parity suite contra implementacao antiga
5. validar em staging
6. fazer cutover do modulo
7. remover implementacao manual antiga apenas daquele modulo
8. repetir ate eliminar o legado manual

Condicao para reset amplo futuro:

- so sera aceitavel cogitar remocao em massa do legado quando:
  - codegen deterministico estiver provado
  - parity suite estiver madura
  - staging replay estiver verde
  - rollback por modulo estiver testado
