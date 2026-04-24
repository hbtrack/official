# Baseline Classifier — Runtime Findings

> Auditoria técnica de repositório contract-driven.
> Data: 2026-04-23
> Escopo: artefatos de baseline (`00-baseline/`)
> Regras aplicadas: AGAUDIT v1.1

---

## Resumo executivo

| Métrica | Valor |
|---|---|
| Fontes analisadas | 5 artefatos |
| Gates falhados | 3 (`DERIVED_DRIFT_GATE`, `HANDOFF_COHERENCE_GATE`, `READINESS_SUMMARY_GATE`) |
| Testes falhados | 3 / 2030 |
| Causas-raiz identificadas | 5 |
| Falhas derivadas | 2 |
| Erros confirmados | 3 |
| Drifts prováveis | 2 |
| Problemas de ambiente | 1 |
| Falsos positivos | 0 |

---

## Achados

---

### ACHADO-001

```
ACHADO-ID: ACHADO-001
Categoria: Drift de artefato — manifest de rastreabilidade
Módulo: shared (contracts/schemas/shared)
Severidade: alta
Estado: drift provável
```

**Camadas em conflito:**
- contrato (`contracts/schemas/shared/session_start.schema.json`)
- generated (manifests de rastreabilidade — hash divergente)

**Descrição:**
O `DERIVED_DRIFT_GATE` reportou 30 erros de hash sha256 divergente, todos apontando para o mesmo arquivo: `contracts/schemas/shared/session_start.schema.json`. O manifest registrado tem hash `39f5ed0e8ad...` mas o arquivo atual tem hash diferente. A repetição de 30 entradas indica que múltiplos manifests distribuídos pelo repositório referenciam este schema — e todos estão desatualizados ao mesmo tempo.

**Evidência A:**
```
! [FAIL] DERIVED_DRIFT_GATE
  Manifests de rastreabilidade inválidos: 30 erro(s).
  - Hash sha256 divergente para contracts/schemas/shared/session_start.schema.json (manifest=39f5ed0e8ad...)
  [repetido 30 vezes]
```

**Evidência B:**
O fato de ser exatamente o mesmo arquivo em todos os 30 erros (não 30 arquivos distintos com drift) indica uma única modificação no `session_start.schema.json` que não passou pelo pipeline de re-hash (`hb artifact`).

**Causa-raiz:**
`contracts/schemas/shared/session_start.schema.json` foi modificado diretamente — sem rodar `hb artifact <path>` após a edição — fazendo com que todos os manifests que referenciam este arquivo fiquem com hash estale.

**Sintomas:**
- `DERIVED_DRIFT_GATE` falha com 30 erros
- `READINESS_SUMMARY_GATE` falha como consequência (ACHADO-003)

**Impacto:**
Pipeline CDD bloqueado. Qualquer tarefa que exija `hb verify` com profile completo falha.

**Correção mínima:**
```bash
hb artifact contracts/schemas/shared/session_start.schema.json
```
Se `hb artifact` não aceitar esse caminho diretamente, re-hashar via pipeline de geração que produz o schema.

**Correção ideal:**
Garantir que toda modificação em `contracts/schemas/shared/` passe obrigatoriamente pelo `hb artifact` como parte do fluxo. Avaliar se o pre-commit hook cobre este caminho.

**Bloqueia merge?:** sim

**Classificação:** drift (não é bug de lógica — é sincronização de artefatos não executada)

---

### ACHADO-002

```
ACHADO-ID: ACHADO-002
Categoria: Incoerência de metadados de sessão
Módulo: governança (SESSION_HANDOFF.md / session_start.json)
Severidade: alta
Estado: drift provável
```

**Camadas em conflito:**
- documentação canônica (`SESSION_HANDOFF.md`)
- runtime (`_reports/session_start.json`)

**Descrição:**
O `HANDOFF_COHERENCE_GATE` encontrou 3 inconsistências entre `SESSION_HANDOFF.md` e `session_start.json`. O `session_start.json` captura o estado no início da sessão; `SESSION_HANDOFF.md` documenta o estado que deveria ser handoff para a próxima sessão. Os dois documentos descrevem realidades diferentes:

- `session_start.json` diz: `module_focus='training'`, `roadmap_phase=1`
- `SESSION_HANDOFF.md` diz: `modulo_foco='infrastructure'` (ou similar), `fase_roadmap=6`

A divergência de fase (1 vs 6) é especialmente significativa — indica que um dos dois está muito defasado em relação ao estado real do projeto.

**Evidência A:**
```
! [FAIL] HANDOFF_COHERENCE_GATE
  SESSION_HANDOFF.md com 3 inconsistência(s).
  - Divergência de módulo foco: session_start.module_focus='training' != SESSION_HANDOFF.modulo_foco='in...'
  - Divergência de fase: session_start.roadmap_phase=1 != SESSION_HANDOFF.fase_roadmap=6.
  - Divergência: SESSION_HANDOFF.roadmap_phase=6 != session_start.roadmap_phase=1.
```

**Evidência B:**
A memory do projeto (MEMORY.md) confirma que a fase atual é 4 (A1+B1 concluído) — o que contradiz tanto fase=1 quanto fase=6 no output. Isso sugere que `session_start.json` foi gerado em contexto diferente do estado atual do projeto.

**Causa-raiz:**
`session_start.json` foi gerado em um contexto de sessão mais antigo (ou foi regenerado com parâmetros incorretos) e `SESSION_HANDOFF.md` foi atualizado separadamente, sem regenerar o `session_start.json` correspondente.

**Sintomas:**
- `HANDOFF_COHERENCE_GATE` falha com 3 inconsistências
- `READINESS_SUMMARY_GATE` falha como consequência (ACHADO-003)

**Impacto:**
Pipeline CDD bloqueado. A incoerência de metadados de sessão impede que o sistema de governança saiba em qual fase/módulo o projeto realmente está.

**Correção mínima:**
Verificar o estado real do `SESSION_HANDOFF.md` e do `_reports/session_start.json` e sincronizá-los. Se o SESSION_HANDOFF está correto (fase 6), regenerar session_start.json com os parâmetros corretos:
```bash
hb session-start  # ou equivalente que regenera session_start.json
```

**Correção ideal:**
Entender por que os dois artefatos divergem tanto (fase 1 vs 6) e garantir que o processo de início de sessão sempre leia SESSION_HANDOFF.md antes de gerar session_start.json.

**Bloqueia merge?:** sim

**Classificação:** drift (metadados de sessão desatualizados — não é bug de código)

---

### ACHADO-003

```
ACHADO-ID: ACHADO-003
Categoria: Falha derivada de pipeline
Módulo: governança (validate_contracts.py)
Severidade: média
Estado: falso positivo como causa-raiz independente
```

**Camadas em conflito:**
- runtime (resultado do pipeline)

**Descrição:**
`READINESS_SUMMARY_GATE` falha com "2 gate(s) bloqueante(s) falharam". Este gate é um agregador — ele falha porque DERIVED_DRIFT_GATE e HANDOFF_COHERENCE_GATE falharam. Não existe falha independente aqui.

**Evidência A:**
```
! [FAIL] READINESS_SUMMARY_GATE
  Pipeline FAIL: 2 gate(s) bloqueante(s) falharam.
```

**Causa-raiz:** ACHADO-001 + ACHADO-002.

**Correção mínima:** resolver ACHADO-001 e ACHADO-002. Este gate passará automaticamente.

**Bloqueia merge?:** sim (derivado)

**Classificação:** falha derivada — não atacar diretamente

---

### ACHADO-004

```
ACHADO-ID: ACHADO-004
Categoria: Gate executado sem registro canônico
Módulo: governança (GATES_REGISTRY.yaml / validate_contracts.py)
Severidade: alta
Estado: erro confirmado
```

**Camadas em conflito:**
- documentação canônica (`GATES_REGISTRY.yaml`)
- runtime (`validate_contracts.py` — executor)
- teste (`tests/pipeline_gates/test_gate_registry_parity.py`)

**Descrição:**
`GOVERNANCE_REGRESSION_GATE` é executado em `validate_contracts.py` e **passa** (o gate em si está funcionando). Porém, está **ausente do `GATES_REGISTRY.yaml`**. O teste `test_executor_gates_all_in_registry` verifica exatamente esta paridade — e falha porque o gate não está registrado.

**Evidência A (teste):**
```
AssertionError: Gates executados em validate_contracts.py mas AUSENTES do GATES_REGISTRY.yaml:
    - GOVERNANCE_REGRESSION_GATE
assert not {'GOVERNANCE_REGRESSION_GATE'}
```

**Evidência B (validate_contracts.py):**
```
+ [PASS] GOVERNANCE_REGRESSION_GATE
```
O gate existe, executa, e passa. O problema é exclusivamente a ausência de registro no YAML canônico.

**Causa-raiz:**
`GOVERNANCE_REGRESSION_GATE` foi implementado no executor sem o correspondente entry no `GATES_REGISTRY.yaml`. O processo de adição de gate exige registro antes de execução (conforme o próprio teste documenta).

**Sintomas:**
- `test_executor_gates_all_in_registry` falha
- `test_contract_gates_pass` (video) herda o FAIL do latest.json (ACHADO-005)

**Impacto:**
O gate funciona, mas não é rastreável pelo registry. Qualquer ferramenta que consuma o registry para listar gates disponíveis não saberá que `GOVERNANCE_REGRESSION_GATE` existe. Viola o invariante do sistema CDD.

**Correção mínima:**
Adicionar `GOVERNANCE_REGRESSION_GATE` ao `GATES_REGISTRY.yaml` com os campos obrigatórios (id, description, severity, blocker, etc.).

**Correção ideal:**
Verificar se existe gate de pré-commit ou linting que impeça adicionar gates ao executor sem o registro correspondente — se não existir, considerar criá-lo.

**Bloqueia merge?:** sim

**Classificação:** erro confirmado (gap de governança — gate sem registro)

---

### ACHADO-005

```
ACHADO-ID: ACHADO-005
Categoria: Falha derivada de contract gates
Módulo: video (tests/test_video_module.py)
Severidade: baixa
Estado: falha derivada
```

**Camadas em conflito:**
- teste (`tests/test_video_module.py`)
- runtime (`_reports/contract_gates/latest.json`)

**Descrição:**
`TestVideoModuleIntegration::test_contract_gates_pass` lê `_reports/contract_gates/latest.json` e verifica `overall_status == "PASS"`. O `latest.json` tem `overall_status == "FAIL"` porque DERIVED_DRIFT_GATE e HANDOFF_COHERENCE_GATE falharam na última execução do pipeline. O teste não tem skip porque `canonical_scope == "full_pipeline"` estava presente.

**Evidência A:**
```
AssertionError: Contract gates failed: FAIL
assert 'FAIL' == 'PASS'
```

**Evidência B:**
O teste é marcado `@pytest.mark.slow` e tem lógica de skip se `latest.json` ausente ou não for `full_pipeline`. Não skipou, portanto `latest.json` existe e é full_pipeline — confirmando que o FAIL vem dos gates reais.

**Causa-raiz:** ACHADO-001 + ACHADO-002 (que fizeram o pipeline falhar e geraram `latest.json` com FAIL).

**Correção mínima:** resolver ACHADO-001 e ACHADO-002, re-rodar `validate_contracts.py`, `latest.json` será PASS.

**Bloqueia merge?:** não (como causa independente — é derivado)

**Classificação:** falha derivada — não atacar diretamente

---

### ACHADO-006

```
ACHADO-ID: ACHADO-006
Categoria: Variável de ambiente ausente em teste de performance
Módulo: training (tests/test_performance_phase4.py / src/training/api/deps.py)
Severidade: média
Estado: erro confirmado
```

**Camadas em conflito:**
- runtime (`src/training/api/deps.py` — `get_cursor_codec()`)
- teste (`tests/test_performance_phase4.py`)
- infra (configuração de ambiente)

**Descrição:**
`TestPerformancePhase4::test_list_training_sessions_response_time` falha com `RuntimeError: TRAINING_CURSOR_SECRET não definida`. O handler de `GET /api/training/training-sessions` chama `get_cursor_codec()`, que tenta resolver a secret do cursor de paginação. A lógica é:

1. `TRAINING_CURSOR_SECRETS` (CSV) → usa
2. `TRAINING_CURSOR_SECRET` (singular) → usa
3. Fallback `SECRET_KEY` do Django → **apenas se DEBUG=True E ENV != production**

O fallback falhou, o que significa que no momento do teste `DEBUG=False` **ou** `ENV` estava setado como "production" ou "prod".

**Evidência A (traceback):**
```
src/training/api/deps.py:94: RuntimeError: TRAINING_CURSOR_SECRET não definida.
Em produção, defina TRAINING_CURSOR_SECRET ou TRAINING_CURSOR_SECRETS explicitamente.
```

**Evidência B:**
2027 outros testes passam (incluindo testes de integração do módulo training). Isso sugere que os testes de integração têm conftest.py com as env vars configuradas — mas o teste de performance (`tests/test_performance_phase4.py`) usa `django.test.Client` diretamente sem a configuração de ambiente necessária.

**Causa-raiz:**
O `test_performance_phase4.py` não configura `TRAINING_CURSOR_SECRET` ou `TRAINING_CURSOR_SECRETS` no ambiente antes de chamar o endpoint. O conftest.py do escopo correto não cobre este diretório de teste, ou o teste não importa o fixture que configura o ambiente.

**Não é:** bug no `get_cursor_codec()` — a lógica está correta e defensiva. É ausência de fixture de ambiente no escopo do teste de performance.

**Sintomas:**
- `RuntimeError` ao chamar `GET /api/training/training-sessions` no teste de performance
- Não afeta testes de integração (que possuem a env var configurada)

**Impacto:**
O teste de performance não consegue medir a performance real do endpoint. O requisito de `< 200ms` fica sem verificação.

**Correção mínima:**
Adicionar ao `conftest.py` do diretório `tests/` (ou ao próprio `test_performance_phase4.py`):
```python
import os
os.environ.setdefault("TRAINING_CURSOR_SECRET", "test-secret-for-perf")
```
Ou usar o fixture que os testes de integração já usam para configurar o ambiente.

**Correção ideal:**
Criar um fixture compartilhado (em `tests/conftest.py`) que configure `TRAINING_CURSOR_SECRET` para todos os testes que precisam de acesso a endpoints de training paginados — e garantir que testes de performance importem esse fixture.

**Bloqueia merge?:** não (mas oculta regressões de performance)

**Classificação:** problema de ambiente (env var ausente no escopo do teste de performance)

---

### ACHADO-007

```
ACHADO-ID: ACHADO-007
Categoria: Migration pendente — modelo diverge do estado persistido
Módulo: training (src/training/)
Severidade: alta
Estado: erro confirmado
```

**Camadas em conflito:**
- persistência (`src/training/migrations/`)
- runtime (`src/training/infrastructure/models/` — `TrainingSessionModel`)

**Descrição:**
`manage.py makemigrations --check --dry-run` (exit 1) e `manage.py migrate` (warning) convergem para o mesmo ponto: `TrainingSessionModel` teve o índice `training_session_at_id_idx` removido no código Python, mas nenhuma migration foi criada para refletir essa remoção no banco.

O `--dry-run` mostra o que **seria gerado**:
```
src/training/migrations/0008_remove_trainingsessionmodel_training_session_at_id_idx.py
  - Remove index training_session_at_id_idx from trainingsessionmodel
```

**Evidência A (makemigrations_check.txt):**
```
Migrations for 'training':
  src/training/migrations/0008_remove_trainingsessionmodel_training_session_at_id_idx.py
    - Remove index training_session_at_id_idx from trainingsessionmodel
```

**Evidência B (manage.py migrate):**
```
Your models in app(s): 'training' have changes that are not yet reflected in a migration,
and so won't be applied.
```

**Causa-raiz:**
O índice `training_session_at_id_idx` foi removido do modelo `TrainingSessionModel` (provavelmente em `src/training/infrastructure/models/`) sem rodar `makemigrations` após a remoção. O banco de dados em produção/staging ainda tem o índice; o modelo Python não o declara mais.

**Impacto:**
O banco de dados de produção mantém um índice que o modelo não conhece mais. Se o índice for removido manualmente do banco sem a migration, o estado fica inconsistente. Se a migration for criada e aplicada depois, o Django tentará dropar um índice que pode ou não existir dependendo do ambiente.

**Correção mínima:**
```bash
python manage.py makemigrations training
# verificar o conteúdo gerado
python manage.py migrate
```

**Correção ideal:**
Verificar se a remoção do índice foi intencional (há evidência de que sim — o nome sugere que era um índice composto `at` + `id` que provavelmente foi substituído ou considerado redundante). Documentar a decisão no commit da migration.

**Bloqueia merge?:** sim (model/migration out of sync é bloqueante para deploy)

**Classificação:** erro confirmado (persistência diverge do modelo Python)

---

### ACHADO-008

```
ACHADO-ID: ACHADO-008
Categoria: Shims de compatibilidade em uso extenso — módulo training
Módulo: training (múltiplos subpacotes)
Severidade: baixa
Estado: drift provável
```

**Camadas em conflito:**
- runtime (`src/training/api/`, `src/training/application/`, `src/training/infrastructure/`)
- domínio (`src/training/domain/`)
- teste (`src/training/tests/`)

**Descrição:**
O pytest registrou ~80 `DeprecationWarning` — todos do módulo training, todos sobre importação de símbolos via shims de compatibilidade ao invés dos subpacotes diretos. Os shims cobrem:

- `training.domain.entities` → deveria ser `training.domain.entities.<subpacote>` ou `training.domain.common.enums`
- `training.infrastructure.models` → deveria ser `training.infrastructure.models.<subpacote>`
- `training.infrastructure.repository` → deveria ser `training.infrastructure.repository.<subpacote>`
- `training.schemas` → deveria ser `training.schemas.<subpacote>`
- `training.application.use_cases` → deveria ser `training.application.<subdomínio>.commands`

Os shims se autodocumentam como "será removido em release N+2".

**Evidência A:** 80+ DeprecationWarnings no output do pytest, distribuídos por:
- `src/training/api/*.py` (chat, attention, blocks, feedback, planning, recommendations, sessions, wellness, eligibility, execution, analytics, mappers)
- `src/training/application/**/*.py`
- `src/training/infrastructure/repository/*.py`
- `src/training/tests/**/*.py`
- `src/training/domain/rules.py`

**Causa-raiz:**
Refatoração de subpacotes do módulo training foi iniciada (criando subpacotes granulares) mas os imports no código de produção e nos testes não foram migrados para os novos caminhos. Os shims estão mantendo compatibilidade mas o código de produção (`api/`, `application/`, `infrastructure/`) ainda usa os caminhos antigos — não apenas os testes.

**Impacto:**
Risco de quebra em release N+2, quando os shims forem removidos. A amplidão do drift (API + application + domain + infrastructure + testes) indica que a migração precisa ser planejada sistematicamente, não pontualmente.

**Correção mínima:** nenhuma imediata — shims estão funcionando. Registrar o débito técnico.

**Correção ideal:** migrar imports em todos os arquivos afetados para os subpacotes diretos. Pode ser feito em batch com `sed` ou equivalente para cada símbolo mapeado pelo shim.

**Bloqueia merge?:** não (por enquanto — bloqueará quando shims forem removidos)

**Classificação:** drift provável (refatoração de módulo incompleta — código de produção ainda no caminho antigo)

---

## Agrupamento por causa-raiz

### CR-001 — session_start.schema.json modificado sem re-hash

- **Achados originados:** ACHADO-001 (direto), ACHADO-003 (derivado), ACHADO-005 (derivado)
- **Módulo:** shared / governança
- **Severidade consolidada:** alta
- **Prioridade:** 1 (resolve em cascata 3 achados)
- **Ação:** `hb artifact contracts/schemas/shared/session_start.schema.json`

### CR-002 — session_start.json e SESSION_HANDOFF.md desincronizados

- **Achados originados:** ACHADO-002 (direto), ACHADO-003 (derivado), ACHADO-005 (derivado)
- **Módulo:** governança
- **Severidade consolidada:** alta
- **Prioridade:** 2 (necessário para liberar pipeline)
- **Ação:** sincronizar SESSION_HANDOFF.md com estado real e regenerar session_start.json

### CR-003 — GOVERNANCE_REGRESSION_GATE sem entrada no registry

- **Achados originados:** ACHADO-004 (direto)
- **Módulo:** governança (GATES_REGISTRY.yaml)
- **Severidade consolidada:** alta
- **Prioridade:** 3
- **Ação:** adicionar entry do gate no GATES_REGISTRY.yaml

### CR-004 — migration ausente para remoção de índice em training

- **Achados originados:** ACHADO-007 (direto)
- **Módulo:** training / persistência
- **Severidade consolidada:** alta
- **Prioridade:** 4
- **Ação:** `python manage.py makemigrations training && python manage.py migrate`

### CR-005 — env var TRAINING_CURSOR_SECRET ausente no escopo do teste de performance

- **Achados originados:** ACHADO-006 (direto)
- **Módulo:** training / testes
- **Severidade consolidada:** média
- **Prioridade:** 5
- **Ação:** configurar env var no conftest.py correto

### CR-006 — imports training via shims em código de produção

- **Achados originados:** ACHADO-008 (direto)
- **Módulo:** training (múltiplos)
- **Severidade consolidada:** baixa
- **Prioridade:** 6 (não urgente, mas deve ser planejado antes de N+2)
- **Ação:** migrar imports para subpacotes diretos em batch

---

## Falhas derivadas (não atacar diretamente)

| Achado | Causa-raiz que resolve |
|---|---|
| ACHADO-003 (READINESS_SUMMARY_GATE) | CR-001 + CR-002 |
| ACHADO-005 (test_contract_gates_pass) | CR-001 + CR-002 + CR-003 |

---

## Sanidade geral do repositório

Com 2027 testes passando de 2030 (99.85%), o repositório está em boa saúde funcional. Os 3 falhos são:
- 1 de ambiente (não é bug de código)
- 1 de registro (gate funciona, não está catalogado)
- 1 derivado (latest.json herdado)

Os gates de contrato que passam (`OPENAPI_POLICY_RULESET_GATE`, `ASYNCAPI_VALIDATION_GATE`, `SPECTRAL_LINTING_GATE`, `JSON_SCHEMA_VALIDATION_GATE`, `GOVERNANCE_REGRESSION_GATE` etc.) indicam que a camada de contratos está sólida. As falhas são de sincronização de metadados, não de violação de contrato.
