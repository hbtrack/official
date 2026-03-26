# Melhorar Pipeline do Agente de IA

## Escopo da análise

Esta análise foi baseada no estado atual do repositório, com foco nos artefatos que hoje controlam o fluxo do agente:

- `docs/_canon/CONTRACT_PIPELINE.md`
- `docs/_canon/CI_CONTRACT_GATES.md`
- `docs/_canon/gates/GATES_REGISTRY.yaml`
- `scripts/contracts/validate/validate_contracts.py`
- `scripts/contracts/validate/bootstrap_contract_tools.py`
- `.contract_driven/agent_prompts/pre_contract_orchestrator.prompt.md`
- `_reports/contract_gates/latest.json`
- `.github/workflows/contract-gates.yml`
- `.github/workflows/deploy.yml`
- `docs/_canon/decisions/ADR-015-agent-execution-log.md`
- `docs/_canon/decisions/ADR-027-deploy-pipeline.md`
- `docs/_canon/decisions/ADR-029-runtime-monitoring.md`

## Leitura executiva

O pipeline atual já tem uma base forte: canon claro, registry de gates, agregador único de validação, evidências estruturadas, scorecard de readiness, logs de pré-contrato e workflow de CI/deploy. O principal problema não é ausência total de governança; é a diferença entre governança declarada e governança realmente executada em alguns pontos críticos.

Os pontos mais sensíveis hoje são:

1. evidência e relatórios importantes ainda são sobrescritos em paths fixos, o que reduz auditabilidade e dificulta concorrência;
2. o pré-contrato ainda depende demais de disciplina do agente/prompt e pouco de runner determinístico;
3. a política de waiver de breaking change existe no canon, mas não está aplicada no gate;
4. parte dos derivados e relatórios vive fora da orquestração principal, o que cria drift operacional;
5. a saúde da toolchain local ainda é instável, mesmo já existindo script de bootstrap;
6. a cobertura de testes está boa em alguns pontos, mas ainda não protege os fluxos mais críticos de governança do agente.

## Oportunidades priorizadas

### 1. Introduzir `run_id` imutável + pasta de execução por rodada

- Problema que resolve:
  Hoje o pipeline escreve artefatos centrais sempre nos mesmos caminhos, como `_reports/contract_gates/latest.json`, `_reports/evidence/boot_resolution_report.json`, `_reports/evidence/module_readiness_scorecard.json` e `SESSION_HANDOFF.md`. Isso dificulta auditoria histórica, correlação entre artefatos e execução concorrente de múltiplos agentes/sessões.
- Como funcionaria na prática:
  Criar um runner como `scripts/pipeline/run_contract_pipeline.py` que gere um `run_id`, crie `_reports/runs/<run_id>/`, grave ali cópias imutáveis de:
  `contract_gates.json`, `boot_resolution_report.json`, `module_readiness_scorecard.json`, `feature_readiness.json`, `agent_execution.json`, `git_metadata.json`.
  Depois disso, atualizar apenas ponteiros `latest.json` de forma atômica.
- Evidência atual:
  `validate_contracts.py` grava direto em `latest.json` e scorecards fixos; o boot report e o handoff também são tratados como artefatos únicos da sessão corrente.
- Prioridade:
  `P0`
- Complexidade:
  `Média`
- Impacto esperado:
  `Muito alto` para auditabilidade, rastreabilidade, rollback de evidência e previsibilidade operacional.

### 2. Transformar o pré-contrato em runner determinístico com contrato de entrada

- Problema que resolve:
  O pré-contrato está bem descrito no prompt, mas a entrada ainda é essencialmente textual. Isso abre espaço para inconsistência entre sessões, variação na interpretação do prompt e baixa validabilidade antes do handoff.
- Como funcionaria na prática:
  Criar:
  `contracts/schemas/shared/pre_contract_request.schema.json`
  `scripts/agent/run_pre_contract.py`
  O runner receberia um payload estruturado com `module`, `task_type`, `resource`, `scope_description`, validaria contra `MODULE_REGISTRY.yaml`, `CLAUDE.md` e prompts disponíveis, emitiria saída JSON normalizada e já geraria o `agent_execution` e o `boot_resolution_report`.
- Evidência atual:
  `.contract_driven/agent_prompts/pre_contract_orchestrator.prompt.md` define o fluxo, mas a execução ainda depende de seguir o prompt corretamente.
- Prioridade:
  `P0`
- Complexidade:
  `Média/Alta`
- Impacto esperado:
  `Muito alto` para controle do agente, validação de entrada e reprodutibilidade.

### 3. Exigir handoff estruturado do agente antes de qualquer promoção de estágio

- Problema que resolve:
  O pipeline valida contratos e readiness, mas o output do agente ainda é parcialmente livre. `SESSION_HANDOFF.md` ajuda na continuidade, porém não substitui um manifesto executável e verificável de saída.
- Como funcionaria na prática:
  Criar:
  `contracts/schemas/shared/agent_handoff.schema.json`
  `scripts/agent/validate_handoff.py`
  O agente teria que emitir um handoff JSON com `run_id`, `module`, `task_type`, `files_touched`, `artifacts_generated`, `derived_updated`, `blockers_emitted`, `next_step`, `ready_for`.
  Um gate leve validaria estrutura, existência real dos arquivos e coerência com o que foi alterado.
- Evidência atual:
  Há precedentes de handoff estruturado em `scripts/hbtrack_lint/handoff_builder.py`, mas o pipeline atual do agente ainda depende mais de Markdown, logs e relatórios soltos.
- Prioridade:
  `P0`
- Complexidade:
  `Média`
- Impacto esperado:
  `Alto` para previsibilidade, rastreabilidade e redução de handoffs ambíguos.

### 4. Implementar engine real de waivers no `CONTRACT_BREAKING_CHANGE_GATE`

- Problema que resolve:
  O canon exige waiver machine-readable com fingerprint para breaking changes, mas a implementação atual do gate falha direto por diff e não processa os waivers existentes. Isso cria desalinhamento entre norma e enforcement.
- Como funcionaria na prática:
  Criar `scripts/contracts/validate/waivers.py` para:
  carregar `contracts/_waivers/waiver.schema.json`,
  validar escopo, módulo, expiracão, aprovador e fingerprint,
  associar o waiver ao diff detectado,
  incluir a evidência no relatório final do gate.
- Evidência atual:
  `CI_CONTRACT_GATES.md` e `GATES_REGISTRY.yaml` exigem waiver; `contracts/_waivers/` e o schema já existem; `_g9_contract_breaking_change` em `validate_contracts.py` não usa nada disso.
- Prioridade:
  `P0`
- Complexidade:
  `Média`
- Impacto esperado:
  `Muito alto` para governança de exceções, auditabilidade e controle de risco de mudança.

### 5. Tornar o bootstrap da toolchain parte obrigatória do fluxo

- Problema que resolve:
  O pipeline já sabe detectar tooling degradado, mas ainda depende de o operador lembrar de preparar o ambiente. Isso aumenta atrito local e gera resultados inconsistentes entre máquinas.
- Como funcionaria na prática:
  Integrar `scripts/contracts/validate/bootstrap_contract_tools.py` ao início do runner principal, ou criar um comando oficial `make doctor`/`python3 scripts/pipeline/doctor.py` que:
  verifica ferramentas,
  registra `_reports/contract_gates/bootstrap.json`,
  falha cedo com ação corretiva clara,
  opcionalmente tenta auto-instalação quando permitido.
- Evidência atual:
  `_reports/contract_gates/latest.json` local está em `FAIL` com `exit_code: 3` por ausência de `oasdiff` e `schemathesis`; o bootstrap existe, mas está desacoplado do fluxo principal.
- Prioridade:
  `P1`
- Complexidade:
  `Baixa/Média`
- Impacto esperado:
  `Alto` para previsibilidade do ambiente e redução de falso negativo operacional.

### 6. Orquestrar a atualização automática de relatórios e documentação derivada

- Problema que resolve:
  Parte dos derivados já tem generator dedicado, mas não está acoplada de forma consistente ao pipeline principal. Isso cria risco de drift entre o que o gate diz verificar e o que o relatório mostra.
- Como funcionaria na prática:
  Criar um passo `sync_derived_reports` para regenerar automaticamente:
  `_reports/feature_readiness.json`,
  scorecards,
  inventários derivados,
  docs geradas por templates.
  Em seguida, um gate de freshness verificaria se nenhum derivado ficou desatualizado.
- Evidência atual:
  `GATES_REGISTRY.yaml` afirma que `FEATURE_READINESS_GATE` gera `_reports/feature_readiness.json`, mas `_g_feature_readiness` apenas valida o registry; a geração está em `scripts/generate/gen_feature_readiness_report.py`, fora do orquestrador principal.
- Prioridade:
  `P1`
- Complexidade:
  `Média`
- Impacto esperado:
  `Alto` para coerência entre relatório, gate e documentação.

### 7. Adicionar lock de execução e proteção contra concorrência

- Problema que resolve:
  Se dois agentes ou duas execuções escreverem ao mesmo tempo, os arquivos `latest.*`, scorecards e handoff podem ficar inconsistentes ou perder causalidade.
- Como funcionaria na prática:
  Implementar lock por arquivo, por exemplo em `.dev/locks/contract_pipeline.lock`, com política simples:
  uma execução de validação por vez;
  timeout configurável;
  opção de `--force` apenas para manutenção.
  O runner por `run_id` reduziria o risco; o lock resolveria a corrida.
- Evidência atual:
  Os artefatos principais são gravados em paths fixos sem proteção visível de lock.
- Prioridade:
  `P1`
- Complexidade:
  `Baixa`
- Impacto esperado:
  `Alto` para robustez operacional em ambiente com múltiplas sessões/agentes.

### 8. Expandir a suíte de testes para cenários críticos de governança

- Problema que resolve:
  Existem testes para partes do pipeline, mas faltam testes de regressão justamente nos fluxos mais sensíveis: waivers, evidência de pré-contrato, ordem do pipeline, output do runner, concorrência e histórico.
- Como funcionaria na prática:
  Adicionar fixtures determinísticas em `tests/fixtures/pipeline/` e testes para:
  waiver válido, expirado e com fingerprint errado;
  `agent_execution` incompleto;
  `boot_resolution_report` inválido;
  geração de `run_id`;
  sincronização dos relatórios derivados;
  snapshot semântico do JSON final do pipeline.
- Evidência atual:
  A suíte cobre `tooling_config`, `global_input_recompile_policy` e partes de governança documental, mas não protege o miolo do controle do agente nem o gate de waiver.
- Prioridade:
  `P1`
- Complexidade:
  `Média`
- Impacto esperado:
  `Muito alto` para evitar regressões silenciosas no pipeline.

### 9. Criar histórico temporal e métricas de tendência do pipeline

- Problema que resolve:
  O pipeline responde bem à pergunta "como foi a última execução?", mas mal à pergunta "o que vem piorando?" ou "qual gate mais degrada ao longo do tempo?".
- Como funcionaria na prática:
  Ao final de cada execução, gerar uma linha resumida em:
  `_reports/history/contract_gates.jsonl`
  com `run_id`, `timestamp`, `overall_status`, `exit_code`, `duration_total_ms`, `gate_failures`, `gate_degraded`, `git_commit`.
  Um script `scripts/pipeline/gen_trend_report.py` geraria tendência semanal e top bloqueios.
- Evidência atual:
  O estado corrente está concentrado em `latest.json`; não há histórico consolidado de tendência do próprio pipeline.
- Prioridade:
  `P2`
- Complexidade:
  `Média`
- Impacto esperado:
  `Médio/Alto` para observabilidade, operação e melhoria contínua.

### 10. Fechar o ciclo de release com manifesto de deploy e rollback auditável

- Problema que resolve:
  O deploy já existe, inclusive com staging, aprovação e rollback, mas ainda falta um artefato único que conecte contrato validado, commit, imagem, migration e rollback target.
- Como funcionaria na prática:
  Criar `scripts/release/build_release_manifest.py` para produzir algo como:
  `_reports/releases/<run_id>.release.json`
  contendo `git_commit`, `contract_report_sha256`, `feature_readiness_sha256`, `docker_image_digest`, `migration_head`, `staging_healthcheck`, `rollback_image_digest`, `approved_by`.
  O deploy consumiria esse manifesto e anexaria a evidência do health check.
- Evidência atual:
  `.github/workflows/deploy.yml` já faz deploy e rollback, mas o encadeamento de evidência entre validação, build, deploy e rollback ainda está disperso.
- Prioridade:
  `P2`
- Complexidade:
  `Média/Alta`
- Impacto esperado:
  `Alto` para rollback seguro, auditoria de release e rastreabilidade ponta a ponta.

### 11. Implementar retenção automática + integridade criptográfica das evidências

- Problema que resolve:
  A política de retenção do log do agente já existe em ADR, mas sem script operacional. Além disso, os relatórios podem ser alterados depois da execução sem um selo simples de integridade.
- Como funcionaria na prática:
  Criar:
  `scripts/ops/purge_retention.py`
  `scripts/pipeline/build_evidence_manifest.py`
  O primeiro aplica TTL nos diretórios voláteis (`_reports/agent_execution/`, `_reports/runtime/`).
  O segundo gera um manifesto SHA-256 dos arquivos de evidência por `run_id`; opcionalmente pode ser assinado com `minisign` ou `cosign` em ambientes de release.
- Evidência atual:
  `ADR-015` e `ADR-011` citam `scripts/ops/purge_retention.py` como trabalho futuro; não há indício de assinatura ou manifesto de integridade das evidências correntes.
- Prioridade:
  `P2`
- Complexidade:
  `Média`
- Impacto esperado:
  `Médio/Alto` para segurança, compliance e auditabilidade forense.

### 12. Adicionar guarda de entrada para prompt injection, segredo e instrução anti-canon

- Problema que resolve:
  O pipeline valida muito bem contratos, mas ainda tem pouca defesa específica para entradas maliciosas ao agente, como instruções para ignorar o canon, colar credenciais ou executar fora do escopo.
- Como funcionaria na prática:
  Criar `scripts/agent/input_guard.py` para inspecionar `scope_description`, notas de sessão e payloads de entrada antes do handoff. A rotina pode marcar ou bloquear:
  instruções do tipo "ignore as regras",
  tentativas de redefinir a autoridade,
  segredos/credenciais,
  URLs externas não autorizadas,
  comandos fora do escopo permitido.
- Evidência atual:
  O controle atual está mais concentrado em gates de artefato e em disciplina de prompt do que em sanitização explícita de entrada do agente.
- Prioridade:
  `P2`
- Complexidade:
  `Média`
- Impacto esperado:
  `Alto` para segurança do agente e redução de bypass operacional.

## Ordem recomendada de implementação

### Fase 1

- Oportunidade 1: `run_id` imutável + bundle por execução
- Oportunidade 2: runner determinístico de pré-contrato
- Oportunidade 4: engine de waivers real
- Oportunidade 5: bootstrap/doctor obrigatório

### Fase 2

- Oportunidade 3: handoff estruturado
- Oportunidade 6: sync automático de derivados
- Oportunidade 7: lock de execução
- Oportunidade 8: testes de governança crítica

### Fase 3

- Oportunidade 9: histórico e tendências
- Oportunidade 10: release manifest + rollback auditável
- Oportunidade 11: retenção + integridade de evidência
- Oportunidade 12: guarda de entrada para o agente

## Recomendação final

Se o objetivo for elevar rapidamente a qualidade operacional do pipeline, eu trataria como núcleo mínimo obrigatório:

1. `run_id` imutável por execução
2. pré-contrato executável por runner, não só por prompt
3. waiver machine-readable realmente aplicado no gate
4. bootstrap/doctor obrigatório antes da validação
5. handoff estruturado do agente

Esse conjunto sozinho já melhora de forma material:

- controle do agente;
- validação de entradas e saídas;
- auditabilidade;
- rastreabilidade;
- previsibilidade;
- governança de exceções;
- robustez para escalar o fluxo com menos dependência de disciplina manual.
