# HB Track — Plano Unificado de Execucao Antifraude por Agentes

> Artefato de planejamento tecnico consolidado.
> Este documento registra o plano unificado que foi executado para introduzir
> o trilho de execucao comprovavel por agentes no repositorio.
> Em caso de conflito, prevalecem: enforcement executavel > schemas >
> `docs/_canon/` > este arquivo.

## 1. Objetivo

Implementar um trilho operacional antifraude, auditavel e verificavel para
execucao por agentes, com separacao formal entre:

- implementacao de um plano aprovado;
- validacao adversarial pos-PR;
- evidencia objetiva de diff, testes, estado e PR remoto;
- bloqueio mecanico de escopo falso, rastreabilidade falsa e conclusao sem prova.

O desenho consolidado introduz dois task types reais:

- `implementation_execution`
- `adversarial_test_execution`

Eles coexistem com os fluxos ja existentes (`generate_code`,
`execute_roadmap_phase`, `adversarial_analysis`) sem substitui-los.

## 2. Arquitetura Alvo

### 2.1 Principios

- `Hb Contract` continua sendo a autoridade soberana do sistema.
- O executor de implementacao passa a ser um task type formal, nao apenas um papel narrativo.
- O tester adversarial passa a ser um task type formal separado do implementador.
- Evidencia de execucao passa a ser schema-valid, persistida em caminho canonico e validada por gates reais.
- O fluxo deve bloquear implementacao fora do plano, ausencia de PR remoto, ausencia de pack de evidencia, ausencia de validacao adversarial e transicao de estado invalida.

### 2.2 Task Types Novos

- `implementation_execution`
  - executa implementacao de um plano aprovado;
  - exige branch limpa, plano aprovado, escopo fechado e artifacts de execucao.

- `adversarial_test_execution`
  - executa validacao adversarial pos-PR;
  - exige `pr_url`, evidence pack, implementation state e manifestos de teste negativo.

### 2.3 Perfis de Boot Novos

- `implementation_execution`
- `adversarial_validation`

## 3. Escopo Consolidado Implementado

## 3.1 Catalogo e Boot

Arquivos:

- `.contract_driven/TASK_CATALOG.yaml`
- `.contract_driven/BOOT_PROFILES.yaml`
- `.contract_driven/CONTRACT_SYSTEM_RULES.md`

Transformacoes:

- inclusao dos task types `implementation_execution` e `adversarial_test_execution`;
- vinculacao de `worker_id`, `worker_path`, `profile_id`, `allowed_modes`,
  `artifacts_produced`, `blocking_gates`, `prohibited_actions`;
- criacao dos perfis `implementation_execution` e `adversarial_validation`;
- inclusao das validacoes de boot:
  - `approved_plan_read`
  - `clean_worktree_required`
  - `remote_pr_required`
  - `evidence_pack_required`
  - `implementation_state_required`
- inclusao dos blocking codes canonicos:
  - `BLOCKED_MISSING_REMOTE_PR`
  - `BLOCKED_MISSING_EVIDENCE_PACK`
  - `BLOCKED_ADVERSARIAL_NOT_RUN`
  - `BLOCKED_STATE_TRANSITION_INVALID`
  - `BLOCKED_DIRTY_WORKTREE`
  - `BLOCKED_CANON_PLAN_CONFLICT`
  - `REPROVADO_OPERACIONALMENTE`

## 3.2 Schemas de Sessao e Artifacts

Arquivos:

- `contracts/schemas/shared/session_start.schema.json`
- `contracts/schemas/shared/session_handoff.schema.json`
- `contracts/schemas/shared/implementation_evidence_pack.schema.json`
- `contracts/schemas/shared/plan_to_diff_trace.schema.json`
- `contracts/schemas/shared/negative_test_manifest.schema.json`
- `contracts/schemas/shared/implementation_flow_state.schema.json`

Transformacoes:

- extensao de enums de `task_type` e `boot_profile_id`;
- introducao de `write_scope=implementation`;
- novos campos opcionais/condicionais em `session_start`:
  - `approved_plan_path`
  - `allowed_files`
  - `forbidden_files`
  - `pr_url`
  - `evidence_pack_path`
  - `implementation_state_path`
  - `decision_ids_affected`
- exigencia de `evidence_paths` coerentes em handoff para os novos task types;
- criacao de schemas fechados para:
  - evidence pack;
  - plan-to-diff trace;
  - manifest de testes negativos;
  - maquina de estados de implementacao.

## 3.3 Runtime Canonico

Arquivo:

- `scripts/hb`

Transformacoes:

- extensao de `_validate_profile_validations` para as cinco novas validacoes;
- mapeamento de `write_scope`:
  - `implementation_execution -> implementation`
  - `adversarial_test_execution -> readonly`
- aceitacao dos dois novos task types em `CDD`;
- extensao de `cmd_verify` com suporte a:
  - `--approved-plan-path`
  - `--pr-url`
  - `--implementation-state-path`
  - `--evidence-pack-path`
  - `--allowed-file`
  - `--forbidden-file`
  - `--decision-id`
- gravacao de artifacts auxiliares em `_reports/implementation_flow/`;
- geracao de stub de `current_state.json` para os novos fluxos;
- inclusao dos campos de execucao nos artifacts de sessao.

## 3.4 Gates Reais

Arquivos:

- `scripts/contracts/validate/validate_contracts.py`
- `docs/_canon/gates/GATES_REGISTRY.yaml`

Gates adicionados:

- `IMPLEMENTATION_SCOPE_FIREWALL_GATE`
- `PLAN_DIFF_TRACE_GATE`
- `NEGATIVE_TEST_COVERAGE_GATE`
- `POST_PR_ADVERSARIAL_GATE`
- `IMPLEMENTATION_STATE_GATE`
- `EVIDENCE_PACK_COMPLETENESS_GATE`

Comportamentos implementados:

- leitura dos artifacts em `_reports/implementation_flow/`;
- validacao contra os schemas novos;
- emissao de blocking codes canonicos;
- registro de `checked_files`, `artifacts`, `violations` e `blocking_code`;
- inclusao dos gates no plano de execucao do validator;
- extensao da classificacao de quarentena para tratar
  `contracts/schemas/shared/` e `.contract_driven/BOOT_PROFILES.yaml`
  como enforcement, nao como produto.

## 3.5 Prompts e Policy Canonica

Arquivos:

- `.contract_driven/agent_prompts/hb_implementer.prompt.md`
- `.contract_driven/agent_prompts/hb_adversarial_tester.prompt.md`
- `docs/_canon/AI_EXECUTION_ROLES_POLICY.md`
- `docs/_canon/README.md`
- `docs/_canon/DOC_USAGE_MANIFEST.yaml`

Transformacoes:

- criacao do prompt formal do implementador;
- criacao do prompt formal do tester adversarial;
- criacao da policy canonica de papeis, limites e soberania;
- registro do novo doc no canon e no manifesto de uso documental.

## 3.6 Rastreabilidade Derivada

Arquivos:

- `generated/manifests/*.traceability.yaml`

Transformacoes:

- atualizacao dos hashes de `session_start.schema.json` e
  `session_handoff.schema.json`;
- recomputacao de `source_tree_sha256` para todos os manifests impactados;
- alinhamento com `DERIVED_DRIFT_GATE`.

## 3.7 Testes

Arquivos atualizados:

- `tests/pipeline/test_rule_change_quarantine.py`
- `tests/pipeline_gates/test_agent_operability_matrix.py`
- `tests/pipeline_gates/test_boot_enforcement_phase2.py`
- `tests/pipeline_gates/test_session_state_phase3.py`

Arquivos novos:

- `tests/pipeline_gates/test_implementation_execution_boot.py`
- `tests/pipeline_gates/test_implementation_flow_gates.py`

Cobertura adicionada:

- reconhecimento dos novos task types e profiles;
- novas validacoes de boot;
- requirements condicionais dos schemas de sessao;
- paridade entre catalogo e prompts;
- gates antifraude para escopo, plan trace, coverage negativa, estado,
  evidence pack e relatorio adversarial;
- ajuste da quarentena para enforcement em `contracts/schemas/shared/`.

## 4. Fases Consolidadas do Plano

### Fase 0 — Preparacao do Executor

- iniciar em branch limpa e worktree limpo;
- nao alterar branch protegida diretamente;
- registrar SHA base e branch de trabalho.

### Fase 1 — Revalidacao do Plano

- confirmar task types, profiles, schemas, gates e comandos reais;
- impedir uso de comando inexistente ou categoria invalida.

### Fase 2 — Baseline

- rodar baseline local antes de alterar;
- registrar falhas pre-existentes separadas das falhas introduzidas.

### Fase 3 — Estrutura Contratual

- criar task types;
- criar boot profiles;
- estender session schemas;
- criar schemas novos de artifacts;
- registrar blocking codes novos.

### Fase 4 — Runtime de Sessao

- tornar `scripts/hb` compativel com os fluxos novos;
- produzir session artifacts e state stubs coerentes;
- validar plano aprovado, PR remoto, evidence pack e state path.

### Fase 5 — Gates Antifraude

- materializar enforcement mecanico no validator;
- registrar os 6 gates novos;
- validar escopo, rastreabilidade, estado, coverage negativa e evidencia.

### Fase 6 — Prompts e Policy

- alinhar prompts com schemas;
- documentar papeis e limites no canon;
- manter paridade entre catalogo, prompts e docs.

### Fase 7 — Integracao de CI

- reutilizar `hb validate --profile ci` como trilho remoto principal;
- nao introduzir check inventado;
- manter `merge-readiness.json` valido se alterado.

### Fase 8 — Testes Antifraude

- provar falha real para:
  - arquivo fora de `allowed_files`;
  - evidence pack sem `pr_url`;
  - plan trace com `extra_files`;
  - manifest negativo com `coverage_ratio < 0.80`;
  - mismatch de PR entre evidence e relatorio adversarial;
  - transicao invalida de estado.

### Fase 9 — Validacao Local Completa

- executar suites de governanca, pipeline gates, parity e validator;
- bloquear avancos sem evidencia objetiva.

### Fase 10 — PR Futuro

- exigir `PR_URL`, `base_sha`, `head_sha`, artifacts de implementacao
  e matriz de rastreabilidade.

### Fase 11 — Tratamento de PR

- corrigir checks sem relaxar gate;
- atualizar teste correspondente quando houver correcao funcional.

### Fase 12 — Merge e Relatorio Final

- merge apenas com checks obrigatorios aprovados;
- registrar SHA final, PR e evidencias.

## 5. Artefatos Canonicos do Trilho Novo

Diretorio:

- `_reports/implementation_flow/`

Artifacts previstos:

- `implementation_evidence_pack.json`
- `plan_to_diff_trace.json`
- `negative_test_manifest.json`
- `current_state.json`
- `adversarial_report.json`

## 6. Regras Antifalsidade Consolidadas

- sem diff, a fase nao existe;
- sem arquivo de teste, o teste nao existe;
- sem comando executado e resultado, a validacao nao existe;
- sem `PR_URL`, a implementacao nao existe operacionalmente;
- sem `implementation_evidence_pack.json`, a entrega e invalida;
- sem `plan_to_diff_trace.json`, nao ha rastreabilidade;
- sem `negative_test_manifest.json`, nao ha validacao adversarial;
- sem gate PASS ou bloqueio objetivo, nao ha avanco;
- enfraquecer teste, schema, gate ou assert para passar e falha de execucao.

## 7. Comandos de Validacao Reais do Repositorio

Comandos usados ou esperados no fluxo:

- `python3 scripts/hb verify --help`
- `python3 scripts/hb validate --help`
- `python3 scripts/hb ci --help`
- `python3 scripts/hb validate --profile local`
- `python3 scripts/hb validate --profile ci`
- `python3 scripts/hb survival-suite`
- `python3 scripts/hb preflight`
- `python3 scripts/hb ci --profile pr`
- `pytest -q -m "not slow" --tb=short`
- `python3 -m pytest tests/pipeline_gates -q`
- `python3 -m pytest tests/test_pipeline_governance.py -q`
- `npx vitest run --reporter=verbose`

Comandos especificos do trilho novo:

- `python3 scripts/hb verify --task-type implementation_execution --module notifications --approved-plan-path temp/AAG.md`
- `python3 scripts/hb verify --task-type adversarial_test_execution --module notifications --pr-url https://github.com/org/repo/pull/123 --implementation-state-path _reports/implementation_flow/current_state.json --evidence-pack-path _reports/implementation_flow/implementation_evidence_pack.json`

## 8. Critérios de Aceite

O plano consolidado e considerado atendido quando:

- os task types `implementation_execution` e `adversarial_test_execution`
  existem e sao reconhecidos por `scripts/hb`;
- os perfis `implementation_execution` e `adversarial_validation`
  existem e passam em boot validation;
- os 4 schemas novos existem e validam os artifacts previstos;
- os 6 gates novos existem, estao no registry e executam no validator;
- os prompts novos estao em paridade com catalogo e schemas;
- a policy canonica de papeis foi registrada no canon;
- os manifests derivados foram atualizados para refletir os schemas alterados;
- os testes novos e atualizados provam casos positivos e negativos do trilho novo.

## 9. Estado de Execucao Registrado

Implementacao concluida neste ciclo:

- task types novos: sim
- boot profiles novos: sim
- blocking codes novos: sim
- schemas novos: sim
- runtime `scripts/hb`: sim
- gates novos no validator: sim
- registry de gates: sim
- prompts novos: sim
- policy canonica: sim
- manifests derivados atualizados: sim
- testes focados e de governanca: sim

Observacao operacional:

- a validacao ampla `python3 scripts/hb validate --profile local` ainda pode
  refletir incoerencias pre-existentes de `SESSION_HANDOFF.md` e outros
  artifacts de workspace sujos, que nao foram sobrescritos por este trabalho.

## 10. Arquivos Principais Impactados

Criados:

- `.contract_driven/agent_prompts/hb_implementer.prompt.md`
- `.contract_driven/agent_prompts/hb_adversarial_tester.prompt.md`
- `contracts/schemas/shared/implementation_evidence_pack.schema.json`
- `contracts/schemas/shared/plan_to_diff_trace.schema.json`
- `contracts/schemas/shared/negative_test_manifest.schema.json`
- `contracts/schemas/shared/implementation_flow_state.schema.json`
- `docs/_canon/AI_EXECUTION_ROLES_POLICY.md`
- `_reports/implementation_flow/.gitkeep`
- `tests/pipeline_gates/test_implementation_execution_boot.py`
- `tests/pipeline_gates/test_implementation_flow_gates.py`

Atualizados:

- `.contract_driven/TASK_CATALOG.yaml`
- `.contract_driven/BOOT_PROFILES.yaml`
- `.contract_driven/CONTRACT_SYSTEM_RULES.md`
- `contracts/schemas/shared/session_start.schema.json`
- `contracts/schemas/shared/session_handoff.schema.json`
- `scripts/hb`
- `scripts/contracts/validate/validate_contracts.py`
- `docs/_canon/gates/GATES_REGISTRY.yaml`
- `docs/_canon/README.md`
- `docs/_canon/DOC_USAGE_MANIFEST.yaml`
- `tests/pipeline/test_rule_change_quarantine.py`
- `tests/pipeline_gates/test_agent_operability_matrix.py`
- `tests/pipeline_gates/test_boot_enforcement_phase2.py`
- `tests/pipeline_gates/test_session_state_phase3.py`
- `generated/manifests/*.traceability.yaml`

## 11. Resultado

Este plano unificado materializa no repositorio um fluxo formal de:

- plano aprovado -> implementacao controlada -> PR remoto -> teste adversarial
  -> evidencia -> gates -> merge autorizado

sem depender de confianca narrativa no executor.
