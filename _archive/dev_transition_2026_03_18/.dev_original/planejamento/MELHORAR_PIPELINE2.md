# Análise de Oportunidades — Pipeline do Agente HB Track
> Versão: 1.0.0 | Data: 2026-03-17
> Complementa: `.dev/planejamento/MELHORAR_PIPELINE.md`
> Autoridade de referência: `docs/_canon/CONTRACT_PIPELINE.md`, `docs/_canon/CI_CONTRACT_GATES.md`, `docs/_canon/gates/GATES_REGISTRY.yaml`, `scripts/contracts/validate/validate_contracts.py`

---

## Leitura Executiva

O pipeline atual tem uma base sólida: 30+ gates, validação semântica cross-spec, registry canônico, evidência machine-readable e workflow CI/CD. O problema central não é ausência de governança — é que a governança declarada e a governança realmente executada divergem em pontos críticos, e o pipeline ainda depende excessivamente de disciplina humana e textual em decisões que deveriam ser verificáveis por máquina.

Esta análise adiciona **14 oportunidades novas** — não cobertas no relatório anterior — além de aprofundar 4 das 12 existentes com evidências específicas do código e dos artefatos atuais.

A organização é por domínio funcional, não por ordem de implementação. A seção final traz a matriz de priorização consolidada.

---

## Domínio 1: Controle de Status e Promoção de Módulo

### O1 — Gate de coerência entre status do MODULE_REGISTRY e bloqueios reais

**Problema identificado:**
O módulo training foi marcado como `implementation_ready` no `MODULE_REGISTRY.yaml` enquanto tinha RC-1 a RC-4 pendentes da análise adversarial e sign-off ausente. O pipeline não detectou essa inconsistência porque nenhum gate cruza o status do registry com os bloqueadores ativos. A correção foi manual e dependeu de uma pergunta humana ("como ele está marcado como ready se tem passos pendentes?").

**Evidência no código:**
`validate_contracts.py` implementa `DECISION_IR_CONFORMANCE_GATE` apenas quando o módulo tem `decision_ir` na lista de superfícies **e** status `implementation_ready`. Não há verificação de que os riscos adversariais (BLOCKED_ADVERSARIAL_PENDING) estão resolvidos antes da promoção de status.

`ADVERSARIAL_ANALYSIS_GATE` (order 15C) é `blocking: false` — ou seja, um módulo pode avançar para `implementation_ready` com análise adversarial reprovada.

**Como funcionaria:**
Criar `scripts/contracts/validate/module_status_coherence_gate.py` que verifica:
- Se `status = validated_contract` ou `implementation_ready`, nenhum bloqueio ativo existe em `_reports/adversarial/*.json` com `overall_status = FAIL`
- Se `status = implementation_ready`, o sign-off foi registrado em `_reports/signoff/<module>.signoff.json`
- Cruzar com `SESSION_HANDOFF.md` — se o handoff lista bloqueios ativos, o módulo não pode ter status superior a `validated_contract`

Promover `ADVERSARIAL_ANALYSIS_GATE` para bloqueante quando `status ≥ validated_contract`.

**Prioridade:** P0
**Complexidade:** Média
**Impacto:** Muito alto — elimina a classe de erros "status no registry diverge da realidade observada"

---

### O2 — Mecanismo formal de sign-off antes da promoção de status

**Problema identificado:**
O pipeline não tem nenhum artefato ou gate que formalize o sign-off humano (PO, UX, Engineering Lead) como pré-requisito para promoção de status de módulo. O UI contract v1.1.0 do training está "aguardando sign-off" mas essa espera é textual — registrada apenas no SESSION_HANDOFF.md. Nada no pipeline bloqueia a promoção de `validated_contract` para `implementation_ready` sem essa aprovação.

**Como funcionaria:**
Criar esquema `contracts/schemas/shared/module_signoff.schema.json` com campos:
```
module, surface, version, status (APPROVED/REJECTED),
approved_by[] (role + name + date),
artifacts_approved[] (path + sha256),
valid_until, notes
```
Criar gate `SIGN_OFF_GATE` que verifica:
- Para promoção a `implementation_ready`, arquivo `_reports/signoff/<module>.signoff.json` existe e está válido
- `approved_by` contém ao menos 1 entrada com `role = engineering_lead`
- `artifacts_approved` bate com hashes atuais dos artefatos listados
- `valid_until` não expirou

O agente pode gerar o template preenchível; o humano assina e coloca em `_reports/signoff/`. O gate valida estrutura e hashes — não precisa de integração externa.

**Prioridade:** P1
**Complexidade:** Média
**Impacto:** Alto — torna o sign-off auditável e rastreável, sem depender de disciplina textual

---

### O3 — Versionamento automático de contratos ao modificar artefatos soberanos

**Problema identificado:**
O `training.yaml` recebeu 9 endpoints novos nesta sessão sem que a versão do contrato fosse incrementada automaticamente. O `VERSIONING_POLICY_GATE` verifica se a versão existe e é SemVer válida, mas não verifica se ela foi atualizada após uma mudança. O agente pode adicionar endpoints (mudança MINOR) ou remover campos (mudança MAJOR) sem que a versão reflita isso.

**Evidência:**
`GATES_REGISTRY.yaml` exige ADR-024 e SemVer no `openapi.yaml`, mas o gate não compara a versão do commit anterior com a atual nem verifica se o tipo de mudança (patch/minor/major) está alinhado ao tipo de diff.

**Como funcionaria:**
Criar `scripts/contracts/validate/version_bump_gate.py`:
- Ler versão do baseline `contracts/openapi/openapi.yaml` vs. HEAD
- Usar diff da oasdiff para classificar o tipo de mudança
- Verificar: se há novos paths → deve ser MINOR bump mínimo; se há breaking change → deve ser MAJOR bump; se só descritivo → PATCH é suficiente
- Bloquear se a versão não foi incrementada de acordo com o tipo de mudança detectado

Secundariamente, criar `scripts/generate/bump_contract_version.py` que automatiza o bump após classificação do diff.

**Prioridade:** P1
**Complexidade:** Média
**Impacto:** Alto — resolve D2 (versionamento de contratos) na prática, não apenas no papel

---

## Domínio 2: Validação de Entradas e Saídas do Agente

### O4 — Validação de completude do UI contract contra o OpenAPI

**Problema identificado:**
O `UI_CONTRACT_TRAINING.md` referencia operationIds por UIF (Endpoint Maps), mas o `UI_DOC_VALIDATION_GATE` (gate 14) apenas checa se o `storybook build` passa — e o storybook não existe. O gate está em `SKIP_NOT_APPLICABLE` permanentemente. Isso significa que o UI contract pode referenciar operationIds inexistentes no OpenAPI indefinidamente sem que o pipeline bloqueie.

**Evidência:**
A sessão atual criou 9 endpoints novos (G-01..G-05) e os adicionou ao UI contract. Nada verificou automaticamente que os operationIds como `acceptRecommendation`, `getLoadChart` etc. foram de fato adicionados ao training.yaml com as assinaturas corretas.

**Como funcionaria:**
Criar `scripts/contracts/validate/ui_contract_alignment_gate.py`:
- Parsear o UI contract (Markdown com seções estruturadas) extraindo todos os operationIds referenciados
- Cruzar com o conjunto de operationIds do OpenAPI bundle compilado
- Bloquear se qualquer operationId referenciado no UI contract não existe no OpenAPI
- Verificar também que os parâmetros críticos (path params, required body fields) são compatíveis

Esse gate substitui a dependência no storybook para a validação semântica do UI contract — o storybook continua sendo o gate de renderização visual, mas o alinhamento funcional passa a ser verificável independentemente.

**Prioridade:** P0
**Complexidade:** Média/Alta
**Impacto:** Muito alto — fecha o ciclo entre UI contract e OpenAPI sem dependência de tooling visual

---

### O5 — Validação de consistência do SESSION_HANDOFF.md

**Problema identificado:**
O `SESSION_HANDOFF.md` é atualizado manualmente e em linguagem mista (Markdown + tabelas textuais). Ele é lido como primeira instrução de cada sessão, mas nenhum gate verifica se o que está escrito é coerente com o estado real do repositório. Exemplos de inconsistência possível:
- Handoff diz "training: implementation_ready" mas MODULE_REGISTRY diz `validated_contract`
- Handoff lista bloqueios como resolvidos mas o gate ainda falha
- Handoff data está desatualizada (sessão de 2026-03-10 em repositório com commits de 2026-03-17)

**Como funcionaria:**
Criar `scripts/contracts/validate/handoff_coherence_gate.py`:
- Extrair campos estruturados do SESSION_HANDOFF.md (via regex ou frontmatter YAML)
- Verificar: `branch_ativo` bate com `git branch --show-current`
- Verificar: `ci_status` é coerente com o último `latest.json`
- Verificar: `modulo_foco` existe no MODULE_REGISTRY.yaml com status coerente com o descrito
- Verificar: `data_ultima_sessao` não é futura e não é mais de 30 dias no passado sem override

Alternativa mais robusta: migrar SESSION_HANDOFF.md para YAML com schema validável, mantendo seção de notas livres no final.

**Prioridade:** P1
**Complexidade:** Baixa/Média
**Impacto:** Alto — elimina a classe de erros "agente age baseado em handoff desatualizado ou inconsistente"

---

### O6 — Gate de completude de análise adversarial por módulo

**Problema identificado:**
O `ADVERSARIAL_ANALYSIS_GATE` verifica apenas se existe relatório em `_reports/adversarial/` e se `overall_status = PASS`. Mas o treinamento do módulo training passou com score 82/100 e tem 4 riscos críticos abertos (RC-1 a RC-4). O gate considera isso PASS porque `overall_status = PASS`.

O problema: o score mínimo de aprovação (100/100? 80/100? com zero RC abertos?) não está definido no gate nem no canon.

**Como funcionaria:**
Estender `adversarial_analysis_gate.py` para verificar:
- `score >= threshold` configurável (sugestão: 90/100 para `implementation_ready`, 80/100 para `validated_contract`)
- `critical_risks_open = 0` para promoção a `implementation_ready`
- Leitura do campo `risks` no relatório JSON e contagem por severidade

Criar `contracts/schemas/shared/adversarial_report.schema.json` para formalizar o formato do relatório adversarial e permitir validação automática.

**Prioridade:** P1
**Complexidade:** Baixa
**Impacto:** Alto — elimina cenário onde módulo com riscos críticos abertos avança no pipeline

---

## Domínio 3: Rastreabilidade e Auditoria

### O7 — Rastreabilidade de ADRs até o artefato que as implementa

**Problema identificado:**
ADRs são aprovadas (ADR-017 state model, ADR-026 code architecture, ADR-030 frontend strategy etc.) mas não há link rastreável entre a ADR e os artefatos que a implementam. Se a ADR-030 é revertida ou substituída, não há forma automatizada de descobrir quais artefatos precisam ser atualizados.

**Como funcionaria:**
Adicionar campo `implements_adr: ["ADR-030"]` no frontmatter YAML de artefatos canônicos relevantes.
Criar `scripts/contracts/validate/adr_coverage_gate.py`:
- Listar ADRs com `status: accepted` em `docs/_canon/decisions/`
- Verificar que cada ADR com `implementation_required: true` é referenciada em pelo menos um artefato canônico
- Verificar que artefatos que declaram `implements_adr` apontam para ADRs que existem e estão `accepted`

**Prioridade:** P2
**Complexidade:** Média
**Impacto:** Médio/Alto — rastreabilidade ponta a ponta entre decisão e implementação

---

### O8 — Changelog automático de contratos por commit

**Problema identificado:**
Quando o agente modifica `training.yaml` adicionando 9 endpoints, essa mudança não gera um changelog estruturado. O git log registra o commit, mas não há artefato que diga: "versão 1.1.0 → 1.2.0: adicionados endpoints G-01..G-05, impacto nos consumidores: nenhum (additive only)".

**Como funcionaria:**
Criar `scripts/generate/gen_contract_changelog.py`:
- Ao final de cada execução com mudança detectada pelo `CONTRACT_BREAKING_CHANGE_GATE`, gerar ou atualizar `contracts/CHANGELOG.md`
- Campos: versão anterior, versão nova, tipo de mudança (additive/breaking/patch), endpoints afetados, aprovador do waiver (se breaking), link para run_id

Integrar ao hook de pré-commit ou ao runner principal como passo obrigatório após o gate de breaking change.

**Prioridade:** P2
**Complexidade:** Média
**Impacto:** Médio — auditabilidade do histórico de contratos sem depender de `git log`

---

### O9 — Inventário de artefatos tocados por sessão do agente

**Problema identificado:**
O agente modifica múltiplos artefatos por sessão, mas o inventário de mudanças existe apenas no `git diff` e no `SESSION_HANDOFF.md` textual. Não há artefato machine-readable que liste: "nesta sessão, o agente tocou X arquivos, gerou Y artefatos novos, removeu Z, e o hash de N ficou diferente do esperado".

**Evidência:**
O `handoff_builder.py` em `scripts/hbtrack_lint/` gera esse tipo de artefato para o módulo atletas (sistema legado), mas o pipeline atual do agente CDD não tem equivalente.

**Como funcionaria:**
No runner principal (oportunidade P0 de MELHORAR_PIPELINE.md), adicionar geração de `_reports/runs/<run_id>/session_diff.json`:
```json
{
  "run_id": "...",
  "git_commit_before": "...",
  "git_commit_after": "...",
  "files_created": [...],
  "files_modified": [{"path": "...", "sha256_before": "...", "sha256_after": "..."}],
  "files_deleted": [...],
  "gates_affected": [...]
}
```
Criar gate leve `SESSION_DIFF_GATE` que verifica: nenhum arquivo fora do escopo declarado foi tocado.

**Prioridade:** P2
**Complexidade:** Baixa
**Impacto:** Alto — rastreabilidade por sessão, detecta efeitos colaterais não declarados

---

## Domínio 4: Robustez Operacional

### O10 — Gate de fronteiras cross-módulo granular por operação

**Problema identificado:**
`WELLNESS_MEDICAL_BOUNDARY_GATE` e `BOUNDARY_USERS_IDENTITY_ACCESS_GATE` existem para pares de módulos com sobreposição histórica. Mas as fronteiras entre training↔wellness (soberania de readiness), training↔medical (restriction_profile), e training↔analytics (recomendações) não têm gates equivalentes — estão documentadas textualmente em RC-2 e no MODULE_SOURCE_AUTHORITY_MATRIX, mas não são verificadas automaticamente.

**Como funcionaria:**
Estender `MODULE_SOURCE_AUTHORITY_MATRIX.yaml` com campo `forbidden_operationid_patterns` por par de módulos.
Criar `scripts/contracts/validate/cross_module_boundary_gate.py`:
- Para cada par de módulos com boundary declarada, verificar que operações proibidas não estão presentes no módulo errado
- Verificar que campos soberanos de um módulo (ex: `restriction_profile` de medical) não são escritos por outro módulo via operações POST/PATCH

**Prioridade:** P1
**Complexidade:** Média
**Impacto:** Alto — previne drift arquitetural cross-módulo que hoje só é detectado por revisão humana

---

### O11 — Métricas de saúde do agente (dívida técnica do pipeline)

**Problema identificado:**
Não há um "debt score" que acompanhe o acúmulo gradual de risco no pipeline:
- Quantos waivers ativos existem e qual o prazo de expiração do mais antigo?
- Quantas análises adversariais têm RC abertos?
- Quantas decisões do backlog arquitetural estão em `open` há mais de 30 dias?
- Quantos módulos têm sign-off expirado?
- Qual a tendência do score de gates DEGRADED vs. PASS ao longo do tempo?

**Como funcionaria:**
Criar `scripts/pipeline/gen_health_score.py`:
- Agregar métricas de: waivers ativos, RCs abertos por módulo, decisões sem resposta, gates DEGRADED por execução
- Gerar `_reports/pipeline_health.json` com score 0–100 e breakdown por categoria
- Adicionar `PIPELINE_HEALTH_GATE` (não bloqueante, informativo) que emite warning se score < 70

Exibir no `README.md` via badge gerado automaticamente (shield.io compatible).

**Prioridade:** P2
**Complexidade:** Média
**Impacto:** Médio — observabilidade proativa do acúmulo de risco antes que vire problema

---

### O12 — Validação da completude do FSM antes de promover módulo

**Problema identificado:**
RC-1 da análise adversarial identificou FSM holes no módulo training: transições não documentadas (PUBLISHED→DRAFT, CANCELLED→DRAFT, IN_PROGRESS→SCHEDULED). O `AXIOM_INTEGRITY_GATE` valida o state machine do `DOMAIN_AXIOMS.json`, mas não verifica completude das transições — só valida que as transições declaradas são consistentes.

**Como funcionaria:**
Adicionar ao `AXIOM_INTEGRITY_GATE` (ou criar gate separado `FSM_COMPLETENESS_GATE`):
- Para cada estado, verificar que existe ao menos uma transição de saída (exceto terminais declarados)
- Para cada par de estados, verificar que a ausência de transição é **explicitamente declarada** como `forbidden` (não apenas omitida)
- Gerar relatório de transições implicitamente não documentadas como WARNING ou FAIL

Isso torna RC-1 detectável automaticamente em vez de depender de análise adversarial manual.

**Prioridade:** P1
**Complexidade:** Média
**Impacto:** Alto — previne FSM holes silenciosos que só aparecem em produção

---

### O13 — Separação de perfis de execução (local / CI / pre-commit)

**Problema identificado:**
O `validate_contracts.py` é usado nos três contextos (local, pre-commit hook, CI GitHub Actions) com comportamento idêntico. O `latest.json` atual mostra `exit_code: 3` por `oasdiff` e `schemathesis` ausentes localmente — mas em CI esses tools estão disponíveis. Isso gera:
- Falsos negativos no CI quando o ambiente local não representa o CI
- Falsos positivos locais quando o dev não tem as ferramentas completas
- Ausência de perfil "rápido" para pre-commit (90s é longo para um hook de commit)

**Como funcionaria:**
Criar `scripts/pipeline/profiles.yaml` com perfis:
```yaml
local:
  gates_required: [AXIOM_INTEGRITY_GATE, PATH_CANONICALITY_GATE, ...]  # gates rápidos
  gates_optional: [OPENAPI_POLICY_RULESET_GATE, ...]
  skip_when_tool_absent: [oasdiff, schemathesis]
  max_duration_seconds: 30

precommit:
  gates_required: [AXIOM_INTEGRITY_GATE, ..., PLACEHOLDER_RESIDUE_GATE]
  max_duration_seconds: 60

ci:
  gates_required: all
  max_duration_seconds: 300
```
Runner detecta perfil via `--profile` flag ou variável de ambiente `CI=true`.

**Prioridade:** P1
**Complexidade:** Média
**Impacto:** Alto — elimina conflito entre velocidade do pre-commit e cobertura do CI

---

### O14 — Expiração e revisão periódica de bloqueios ativos

**Problema identificado:**
Bloqueios emitidos pelo pipeline (RC-1..RC-4, BLOCKED_VERSIONING_MISSING, BLOCKED_PACT_MISSING) não expiram. Se um bloqueio não é resolvido em semanas, ele se torna "ruído de fundo" e perde eficácia como sinal. Não há mecanismo de escalation — o mesmo RC pode permanecer em aberto indefinidamente sem alerta crescente.

**Como funcionaria:**
Criar `contracts/schemas/shared/active_blocker.schema.json`:
```json
{
  "blocker_id": "RC-1",
  "module": "training",
  "blocking_code": "BLOCKED_ADVERSARIAL_PENDING",
  "created_at": "2026-03-17T...",
  "escalation_threshold_days": 14,
  "owner": "performance-tech",
  "resolution_criteria": "..."
}
```
Criar gate `BLOCKER_AGING_GATE` que lê `_reports/active_blockers.json` e:
- Emite WARNING quando blocker > `escalation_threshold_days`
- Emite FAIL (se bloqueante) quando blocker > 2× threshold sem override humano

Gerar `_reports/active_blockers.json` automaticamente a partir dos gates que falham, com timestamp de criação preservado entre execuções.

**Prioridade:** P2
**Complexidade:** Média
**Impacto:** Médio/Alto — rastreabilidade temporal de bloqueios e pressão sistêmica para resolução

---

## Domínio 5: Segurança e Isolamento

### O15 — Escopo de escrita do agente por sessão (write-scope enforcement)

**Problema identificado:**
O agente tem acesso de escrita irrestrito ao repositório. Em sessões longas, o risco de modificar arquivos fora do escopo declarado é real — seja por erro do prompt, por instruções conflitantes ou por efeito colateral de ferramentas. O `handoff_builder.py` do sistema legado implementa `forbidden_write_paths` e `allowed_file_paths` com verificação de hash, mas o pipeline CDD atual não tem equivalente.

**Como funcionaria:**
No início de cada sessão, o agente declara `scope` em `_reports/agent_execution/<session_id>.json`:
```json
{
  "declared_write_scope": ["contracts/openapi/paths/training.yaml", "docs/hbtrack/modulos/training/..."],
  "declared_forbidden_paths": ["CLAUDE.md", "docs/_canon/MODULE_REGISTRY.yaml"]
}
```
Criar `scripts/agent/write_scope_gate.py` que, ao final da sessão, compara `git diff --name-only` com o escopo declarado e bloqueia commit se houver divergência.

Integrar ao hook de pre-commit: falhar se arquivo modificado está fora do escopo declarado da sessão.

**Prioridade:** P1
**Complexidade:** Média
**Impacto:** Muito alto — elimina efeitos colaterais não-declarados do agente, aumenta confiança operacional

---

### O16 — Validação semântica de prompts antes da execução

**Problema identificado:**
O `input_guard.py` proposto no relatório anterior foca em detecção de prompt injection. Mas há outro problema: prompts que não violam segurança mas são semanticamente ambíguos ou mal-formados passam direto para o agente, gerando saídas inconsistentes. Ex: "crie o contrato do módulo X" sem especificar `task_type` resulta em inferência livre, o que viola a regra do orchestrator.

**Como funcionaria:**
Criar `scripts/agent/prompt_validator.py` que, antes de executar qualquer worker:
- Verifica que `task_type` está declarado e pertence ao mapa do §4 do CLAUDE.md
- Verifica que `module` está no MODULE_REGISTRY.yaml
- Verifica que o worker correspondente existe em `.contract_driven/agent_prompts/`
- Emite erro estruturado com sugestão de correção se alguma verificação falhar

Integrar ao `run_pre_contract.py` (oportunidade P0 do relatório anterior) como fase 0 do runner.

**Prioridade:** P1
**Complexidade:** Baixa
**Impacto:** Alto — elimina execuções parciais causadas por entrada ambígua

---

## Domínio 6: Observabilidade e Continuidade

### O17 — Dashboard de readiness multi-módulo em formato legível por humano

**Problema identificado:**
O `MODULE_ROADMAP_2026_03_17.md` é atualizado manualmente a cada sessão. A `module_readiness_scorecard.json` existe mas é JSON técnico. Não há saída visual, auto-gerada e sempre atualizada que mostre ao humano leigo: "o training está 12/12 superfícies ✅, mas bloqueado por 4 itens; os demais 15 módulos precisam de X, Y, Z para avançar".

**Como funcionaria:**
Criar `scripts/generate/gen_readiness_dashboard.py`:
- Ler `MODULE_REGISTRY.yaml`, `module_readiness_scorecard.json`, `active_blockers.json`, `signoff/*.json`
- Gerar `_reports/READINESS_DASHBOARD.md` com tabela visual por módulo, indicadores de progresso e próximos passos por módulo em linguagem de produto (não jargão técnico)
- Executar automaticamente ao final de cada pipeline run (integrado ao runner principal)
- Substituir a necessidade de atualizar MODULE_ROADMAP manualmente a cada sessão

**Prioridade:** P2
**Complexidade:** Baixa/Média
**Impacto:** Alto — elimina drift entre roadmap textual e estado real do pipeline

---

### O18 — Alerta de staleness: artefatos não tocados por N dias com status alto

**Problema identificado:**
Um módulo pode ter status `validated_contract` mas os artefatos que o sustentam (docs de módulo, contracts) não foram revisados há 60+ dias. O pipeline valida que os artefatos existem e são válidos, mas não verifica se eles estão desatualizados em relação à realidade do negócio ou do domínio.

**Como funcionaria:**
Adicionar campo `last_reviewed` ao frontmatter de artefatos canônicos (já presente em alguns, como `CI_CONTRACT_GATES.md: last_reviewed: 2026-03-11`).
Criar `ARTIFACT_STALENESS_GATE` (não bloqueante):
- Para módulos com `status ≥ validated_contract`, verificar que todos os artefatos com `last_reviewed` foram revisados nos últimos N dias (ex: 90 dias)
- Emitir WARNING por artefato stale, FAIL se > 30% dos artefatos do módulo estão stale

**Prioridade:** P3
**Complexidade:** Baixa
**Impacto:** Médio — governa o ciclo de vida dos contratos após a criação

---

## Consolidação: Matriz de Priorização

| # | Oportunidade | Domínio | Prioridade | Complexidade | Impacto | Já coberto em MELHORAR_PIPELINE.md? |
|---|---|---|---|---|---|---|
| O1 | Gate de coerência status × bloqueios reais | Status/Promoção | **P0** | Média | Muito alto | Não |
| O4 | Validação UI contract × OpenAPI | Entradas/Saídas | **P0** | Média/Alta | Muito alto | Não |
| O2 | Mecanismo formal de sign-off | Status/Promoção | **P1** | Média | Alto | Não |
| O3 | Versionamento automático de contratos | Status/Promoção | **P1** | Média | Alto | Parcial (MELHORAR 4) |
| O5 | Validação de coerência do SESSION_HANDOFF | Entradas/Saídas | **P1** | Baixa/Média | Alto | Não |
| O6 | Gate de completude adversarial por score | Entradas/Saídas | **P1** | Baixa | Alto | Não |
| O10 | Gates cross-módulo granulares | Robustez | **P1** | Média | Alto | Não |
| O12 | FSM completeness gate | Robustez | **P1** | Média | Alto | Não |
| O13 | Perfis de execução local/CI/precommit | Robustez | **P1** | Média | Alto | Não |
| O15 | Write-scope enforcement por sessão | Segurança | **P1** | Média | Muito alto | Parcial (MELHORAR 12) |
| O16 | Validação semântica de prompts | Segurança | **P1** | Baixa | Alto | Parcial (MELHORAR 12) |
| O7 | Rastreabilidade ADR → artefato | Rastreabilidade | **P2** | Média | Médio/Alto | Não |
| O8 | Changelog automático de contratos | Rastreabilidade | **P2** | Média | Médio | Não |
| O9 | Inventário de artefatos por sessão | Rastreabilidade | **P2** | Baixa | Alto | Parcial (MELHORAR 3) |
| O11 | Health score / debt score do pipeline | Robustez | **P2** | Média | Médio | Não |
| O14 | Expiração e escalation de bloqueios | Robustez | **P2** | Média | Médio/Alto | Não |
| O17 | Dashboard de readiness auto-gerado | Observabilidade | **P2** | Baixa/Média | Alto | Não |
| O18 | Alerta de staleness de artefatos | Observabilidade | **P3** | Baixa | Médio | Não |

---

## Ordem de Implementação Recomendada

### Fase 1 — Controle de Status e Confiança nas Entradas
*(Sem isso, o agente pode agir baseado em estado incorreto)*

1. **O1** — Gate de coerência status × bloqueios: impede promoção prematura de módulo
2. **O4** — Validação UI contract × OpenAPI: fecha o ciclo contratual de UI
3. **O5** — Coerência do SESSION_HANDOFF: impede agente de agir em handoff incorreto
4. **O6** — Gate de completude adversarial com score: torna o threshold explícito e verificável

Do relatório anterior (P0): run_id, runner de pré-contrato, waiver engine, bootstrap obrigatório

### Fase 2 — Robustez Operacional e Segurança
*(Reduz dependência de disciplina manual)*

5. **O2** — Sign-off formal antes de promoção de status
6. **O3** — Versionamento automático (resolve D2 na prática)
7. **O13** — Perfis de execução por contexto (pré-commit rápido)
8. **O15** — Write-scope enforcement por sessão
9. **O16** — Validação semântica de prompts
10. **O10** — Gates cross-módulo granulares
11. **O12** — FSM completeness gate

Do relatório anterior (P1): handoff estruturado, sync de derivados, lock de execução, testes de governança

### Fase 3 — Observabilidade e Governança de Longo Prazo
*(Sustentabilidade do pipeline ao longo de múltiplos módulos)*

12. **O9** — Inventário de artefatos por sessão
13. **O7** — Rastreabilidade ADR → artefato
14. **O8** — Changelog automático de contratos
15. **O17** — Dashboard de readiness auto-gerado
16. **O11** — Health score / debt score
17. **O14** — Expiração e escalation de bloqueios
18. **O18** — Alerta de staleness

Do relatório anterior (P2/P3): histórico temporal, release manifest, retenção + integridade, input guard

---

## Diagnóstico Rápido: Problemas Observáveis Hoje

Os problemas a seguir foram observados no estado atual do repositório e ilustram as oportunidades acima:

| Observação | Gate faltante | Oportunidade |
|---|---|---|
| Training marcado `implementation_ready` com RC-1..RC-4 abertos | `MODULE_STATUS_COHERENCE_GATE` | O1 |
| `ADVERSARIAL_ANALYSIS_GATE` é `blocking: false` | Promover para bloqueante ≥ `validated_contract` | O1, O6 |
| `latest.json` em FAIL (exit_code 3) por tooling ausente — pré-commit roda mesmo assim | Perfis de execução + bootstrap obrigatório | O13 + MELHORAR 5 |
| 9 endpoints adicionados ao training.yaml sem bump de versão | `VERSION_BUMP_GATE` | O3 |
| UI contract referencia operationIds sem validação cruzada | `UI_CONTRACT_ALIGNMENT_GATE` | O4 |
| SESSION_HANDOFF.md atualizado manualmente, sem verificação de coerência | `HANDOFF_COHERENCE_GATE` | O5 |
| Sign-off do UI contract registrado apenas em texto no handoff | `SIGN_OFF_GATE` | O2 |
| MODULE_ROADMAP.md atualizado manualmente a cada sessão | Dashboard auto-gerado | O17 |

---

## Nota de Aplicação

Toda oportunidade desta análise que altere comportamento do agente ou introduza novo gate deve seguir o protocolo de canonização do pipeline definido em `docs/_canon/CONTRACT_PIPELINE.md §4`:
1. Registrar regra normativa em RULES e/ou LAYOUT
2. Registrar estágio em CONTRACT_PIPELINE.md
3. Classificar leitura em CLAUDE.md §7
4. Registrar em GATES_REGISTRY.yaml com gate_id único
5. Implementar em script/validator/gate

Nenhuma oportunidade desta lista pode ser implementada apenas como código sem passar pelos 5 níveis acima.
