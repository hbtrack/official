---
meta:
  document: MANUAL_DETERMINISTICO.md
  version: "2.0"
  status: SSOT
  evidence_root: _reports/
  precedence: "overrides_conflicting_validation_texts"
---

# MANUAL_DETERMINISTICO.md — HB TRACK (v2.0, SSOT)

## Change Control

* Documento: `MANUAL_DETERMINISTICO.md`
* Versão: v2.0
* Status: **SSOT** (fonte de verdade)
* Root canônico de evidências: **`_reports/`**
* Precedência: este manual prevalece sobre qualquer outro texto conflitante sobre **validação**, **correção**, **evidência**, **gates/checks**, **rollback**, **casos**, **waivers**, **IDs**, **exit codes**, **estruturas de pastas**.
* Alterações: apenas via mudança versionada (commit/PR) e aprovação humana (ver “Governança e versionamento”).

---

## 0) Invariantes globais (MUST/MUST NOT)

0.1 Determinismo e auditoria

* Todo PASS/FAIL MUST ser **executável**, **binário**, **repetível**, **ancorado** (commit + ambiente) e **evidenciado** em `_reports/`.
* Nenhum PASS conta sem Evidence Pack persistido (anti-falso-positivo).

0.2 Snapshot e baselines (PERMITIDO, mas não é prova suficiente sozinho)

* Snapshot/baseline é **PERMITIDO** como mecanismo de diagnóstico, guard, drift detection e captura de contexto
  (ex.: baselines, "agent guard", context capture). Porém:

  - Snapshot **MUST NOT** ser aceito como prova única de "FUNCIONA".
  - Qualquer gate que use snapshot/baseline **MUST** declarar isso no registry (GATES_REGISTRY) e **MUST** persistir
    os artefatos no Evidence Pack em `_reports/`.

0.3 Automação/infra

* Automação/infra MUST ser **Python (`.py`)** usando **`config.py`**.
* Scripts `.sh` e `.ps1` são **banidos** para automação/infra **nova**: MUST NOT.
* Se existirem gates legados em PS1, só podem existir como **LEGADO** com **waiver formal** e plano de migração (ver “Waiver”).

0.4 “Chat não é estado”

* O chat NÃO é SSOT de caso. Estado e evidências MUST viver em `_reports/` (audit e cases).

0.5 Namespace único de gate

* **GATE_ID == CHECK_ID** (mesma string). Não existe namespace duplo.

0.6 Exit codes canônicos (únicos)
Todos os gates/checks MUST padronizar para:

* `0` = PASS
* `2` = FAIL_ACTIONABLE (bug/contrato violado)
* `3` = ERROR_INFRA (infra/rede/flake externo)
* `4` = BLOCKED_INPUT (evidência mínima incompleta / pré-requisito ausente)

Observação: qualquer ferramenta legada que só retorna “!=0 fail” MUST ser normalizada pelo runner e gravada como 2/3/4 no `result.json`.

---

## 1) Definições (você usa sempre)

1.1 “Funciona”
Uma capability é considerada funcionando quando existe **evidência executável** de que ela se comporta conforme esperado, **no ambiente-alvo**, **no commit-alvo**, com Evidence Pack auditável em `_reports/`.

1.2 Gate (Check)
Verificação executável que:

* termina com exit code determinístico (0/2/3/4),
* produz evidência mínima (stdout/stderr + metadata + result.json),
* registra commit e alvo/ambiente.

1.3 Evidence Pack
Conjunto de artefatos que tornam o resultado verificável por terceiros:

* comando executado,
* stdout/stderr,
* commit hash,
* alvo/ambiente,
* relatórios,
* summary consolidado.

Root canônico: `_reports/`.

1.4 Capability
Capacidade de produto (ex.: `AUTH_LOGIN`, `TRAINING_CYCLE_CRUD`). Cada capability tem uma “matriz mínima de prova” (quais gates a comprovam).

1.5 Regra anti-falso-positivo
Nenhum gate conta se:

* não registrar claramente alvo/ambiente e commit,
* não gravar evidência em `_reports/`.
  Nenhum PASS conta sem Evidence Pack.

---

## 2) Root canônico `_reports/` (estrutura única)

### 2.1 Audit (execução de gates)

Tudo que é execução de validação/correção produz:
`docs/hbtrack/evidence/AR_<id>/`

Obrigatório:

* `docs/hbtrack/evidence/AR_<id>/summary.json`
* `docs/hbtrack/evidence/AR_<id>/context.json`
* `docs/hbtrack/evidence/AR_<id>/checks/<GATE_ID>/stdout.log`
* `docs/hbtrack/evidence/AR_<id>/checks/<GATE_ID>/stderr.log`
* `docs/hbtrack/evidence/AR_<id>/checks/<GATE_ID>/result.json`

Adicionais (quando aplicável):

* Playwright: `playwright-report/` e/ou `test-results/`
* Pytest: junit/xml/html (se configurado)
* Contrato: relatório do validador
* DB: logs alembic + heads

### 2.2 Cases (estado e trilha de correção)

Casos de correção vivem em:
`_reports/cases/<CORR_ID>/`

Obrigatório:

* `state.yaml`
* `facts.yaml`
* `repro.yaml`
* `patch_plan.yaml`
* `gate_results.yaml`
* `rollback.yaml`
* `closure.yaml` (apenas ao fechar)
* `evidence_manifest.json` (hashes)
* `links.yaml` (liga CORR ↔ RUN_IDs)
* `logs/` (opcional; preferencialmente referenciar logs do audit)

### 2.3 Linkagem determinística (CORR ↔ RUN_ID)

* Todo caso MUST referenciar explicitamente os RUN_IDs usados para:

  * reproduzir (falhar),
  * verificar (passar).
* Regra recomendada: quando RUN_ID é gerado para um caso, ele MUST conter o CORR_ID (ex.: `RUN-CORR-2026-02-18-001-01`).

---

## 3) Protocolos de validação que realmente comprovam funcionamento (v1.0)

A regra de ouro: protocolo “real” é:

* Executável
* Binário (PASS/FAIL objetivo)
* Repetível (ou flakiness detectada e tratada)
* Ancorado (commit + ambiente)
* Evidenciado (Evidence Pack persistente)

Qualquer validação que dependa de “olhar e achar” (JSON, git status, “subiu”) não entra.

### PROTOCOLO A — E2E (Playwright) como prova comportamental

O que prova: fluxo real ponta-a-ponta (frontend→backend→DB).

Onde usar: AUTH, RBAC, fluxos críticos de TRAINING, fluxos de UI.

Como executar corretamente:

* projeto/browser fixo
* seed controlado
* teste cria/reset seu estado para evitar PASS por lixo antigo
* asserts claros (status/estado divergente falha)

Evidência mínima:

* relatório Playwright
* stdout/stderr do runner
* base_url frontend e backend usados
* commit hash (em context.json)

O que NÃO prova:

* drift estrutural se fluxo não passa por isso
* saúde operacional fora do caminho do teste

Erros comuns:

* rodar contra ambiente errado
* flakiness (passa 2/5). Flakey não valida: estabilize ou quarantine.

### PROTOCOLO B — Integração/serviço (pytest) como prova de regras e invariantes

O que prova: regras de negócio e edge cases no backend.

Onde usar: CSRF, refresh rotation, constraints, permissões por role, invariantes de training.

Como executar corretamente:

* DB de teste isolado (ou fixtures/transações)
* seed determinístico
* asserts sobre comportamento e erros

Evidência mínima:

* output pytest + exit code
* db_target (não pode ser prod)
* commit hash

O que NÃO prova:

* UI/UX real
* integração completa com frontend

Erros comuns:

* só happy path
* mocks que escondem bug de integração real

### PROTOCOLO C — Contrato de API (OpenAPI + validação automatizada)

O que prova: compatibilidade de request/response, schemas e status codes.

Onde usar: endpoints core expostos (principalmente AUTH e módulos base).

Como executar corretamente:

* OpenAPI como contrato versionado
* validador roda contra ambiente de prova
* valida schemas + status codes

Evidência mínima:

* relatório do validador (requests e falhas)
* base_url
* commit hash
* versão do contrato

O que NÃO prova:

* semântica completa (JSON no formato pode estar logicamente errado)
  → por isso C não substitui A/B.

### PROTOCOLO D — Banco e migrations (upgrade head) como prova estrutural

O que prova: migrations aplicam e schema final é consistente.

Onde usar: qualquer mudança DB-affecting.

Como executar corretamente:

* migrations em DB limpo (idealmente também em DB “antigo”)
* upgrade head + checks de paridade
* garantir que DB indisponível não vire PASS

Evidência mínima:

* log migrations
* head alembic final
* conexão redigida (host/porta/dbname) ou identificador do ambiente
* commit hash

O que NÃO prova:

* regra de negócio correta
* fluxo completo

### PROTOCOLO E — Smoke operacional (health + endpoints críticos)

O que prova: serviço responde e endpoints críticos funcionam no ambiente-alvo.

Onde usar: sempre (captura “subiu mas não funciona”, “infra quebrou”).

Como executar corretamente:

* health obrigatório
* smoke testa pelo menos 1 endpoint protegido (ex.: `/auth/me`) quando aplicável
* falha em 5xx, TLS/proxy, redirects inesperados
* registra base_url e endpoints exercitados

Evidência mínima:

* output do smoke (requests + status)
* base_url
* commit hash
* duração/timeouts

O que NÃO prova:

* edge cases e UX.

### PROTOCOLO F — Triangulação de Verdade (critério “VERIFIED”)

Não é teste; é regra de decisão.

Para capability crítica:

* 1 prova comportamental (A ou B; ideal A no fluxo central)
* 1 prova estrutural/contratual (C ou D)
* 1 prova operacional (E)

Regra canônica:

* VERIFIED = (Comportamental PASS) + (Estrutural/Contrato PASS) + (Operacional PASS)
  Se qualquer falhar: não está comprovado.

---

## 4) Como usar validação no dia a dia

4.1 Classifique a mudança (decide quais protocolos aplicar)
Tipos:

* logic-only
* DB-affecting
* API-contract impacting
* UI-flow impacting
* infra/runtime

Regra prática:

* logic-only → B + E (A se fluxo crítico)
* DB-affecting → D + E (+ A/B para regra/fluxo)
* API-contract → C + E (+ B para semântica)
* UI-flow → A + E (+ B/C se tocar backend)
* infra/runtime → E + (A ou smoke autenticado mínimo)

4.2 Execute gates e gere evidência
Runner MUST:

* gravar logs em `_reports/`
* registrar commit e alvo
* gerar `summary.json` com status por gate

4.3 Decida “funciona” por regra explícita

* capability crítica → Triangulação (3/3)
* capability não crítica → 2/3 permitido, mas **nunca** aceitando falha estrutural (C/D) como “funciona”

4.4 Falhou? Diagnóstico, não debate
Falhou = abrir Evidence Pack, identificar qual protocolo falhou (A/B/C/D/E), corrigir até PASS.

---

## 5) Matriz canônica de validação (Gates A/B/C/D/E) v1.0

### 5.1 Convenções

Tipos:

* A: E2E (Playwright)
* B: Integração/serviço (pytest)
* C: Contrato (OpenAPI)
* D: DB/migrations/paridade
* E: Smoke operacional

Regra “VERIFIED”:

* CRÍTICA: A + (C ou D) + E
* DB-AFFECTING: D + (A ou B) + E
* Lógica/sem DB: B + E (A recomendado se há UI)

### 5.2 Variáveis de ambiente padrão

* `HB_AUDIT_BASE_URL` (obrigatório para gates HTTP)
* `HB_AUDIT_EMAIL`, `HB_AUDIT_PASSWORD` (smoke autenticado)
* `DATABASE_URL` (B/D quando aplicável)

### 5.3 Execução (recomendado)

Runner recomendado:

* `python scripts/audit/audit_runner.py --only <GATE_ID> <GATE_ID> ...`
  PASS global: exit 0 + Evidence Pack completo em `docs/hbtrack/evidence/AR_<id>/`.

Execução direta (aceita):

* deve salvar stdout/stderr
* deve registrar commit (`git rev-parse HEAD`), base_url, RUN_ID e paths de relatórios

### 5.4 Matriz por capability (exemplos)

A matriz abaixo é **contrato** de validação. IDs e comandos finais MUST estar no registry canônico (seção 9).

AUTH — Login/Logout/Refresh (CRÍTICA)
Gates mínimos: A + C + E (ou A + D + E se tocar schema)

* `AUTH_E2E_LOGIN` (A)
  Comando: `npx playwright test -g "auth login" --project=chromium`
  PASS: exit 0 + testes executados (>0)
* `AUTH_CONTRACT_OPENAPI` (C)
  Comando: `python scripts/audit/check_openapi_contracts.py --scope auth`
  PASS: exit 0 sem violações schema/status
* `AUTH_SMOKE_RUNTIME` (E)
  Comando: `python scripts/audit/check_smoke_api.py --mode auth`
  PASS: `/health` 200 e `/auth/me` 200

RBAC — Roles/Permissões (CRÍTICA)
Gates mínimos: B + C + E (A recomendado se há UI)

* `RBAC_PYTEST_PERMISSIONS` (B): `python -m pytest -q tests/integration/test_rbac.py`
* `RBAC_CONTRACT_OPENAPI` (C): `python scripts/audit/check_openapi_contracts.py --scope rbac`
* `RBAC_SMOKE_PROTECTED` (E): `python scripts/audit/check_smoke_api.py --mode rbac`

TRAINING — ciclos/sessões/presença (CRÍTICA quando habilitado)
Gates mínimos: A + D + E (B recomendado para regras finas)

* `TRAINING_E2E_FLOW` (A)
* `TRAINING_PYTEST_RULES` (B)
* `DB_MIGRATIONS_UPGRADE_HEAD` (D)
* `TRAINING_SMOKE_RUNTIME` (E)

(ATHLETES, TEAMS, EVENTS, UPLOADS seguem o mesmo padrão do texto que você já definiu; a regra é: a matriz descreve “mínimos”, e o registry fixa comando, pré-requisitos e evidências.)

---

## 6) Correção determinística (protocolo de correção v1.0, SSOT)

### 6.1 Objetivo

Quando a IA recebe evidência por mensagem, ela MUST:

* classificar falha por enum fechado,
* exigir Evidence Pack mínimo por tipo,
* exigir REPRO_STEP executável (ou bloquear),
* produzir patch mínimo dentro de allowlist,
* rodar gates mínimos obrigatórios,
* registrar evidências em `_reports/`,
* oferecer rollback determinístico,
* manter auditabilidade fora do chat.

### 6.2 Enum fechado de tipos de falha (FAILURE_TYPE)

A classificação MUST usar exatamente um primário:

* `FT_AUTH_CONTRACT`
* `FT_API_CONTRACT`
* `FT_E2E_UI`
* `FT_UNIT_TEST`
* `FT_INTEGRATION_TEST`
* `FT_DB_MIGRATION`
* `FT_DB_PARITY`
* `FT_DB_CONNECTIVITY`
* `FT_DOCS_INDEX`
* `FT_DOCS_CANON`
* `FT_BUILD_DEPS`
* `FT_SECURITY_POLICY`
* `FT_INFRA_RUNTIME`
* `FT_TOOLING_GATES`

Sem evidência suficiente: MUST BLOCKED.

### 6.3 Caso de correção (CORR_ID) e estado

Formato: `CORR-YYYY-MM-DD-NNN`

Estado do caso MUST viver em:
`_reports/cases/<CORR_ID>/state.yaml`

Campos obrigatórios de `state.yaml`:

* `corr_id`
* `protocol_version: v1.0`
* `status: DRAFT|BLOCKED|IN_PROGRESS|FIXED|VERIFIED|CLOSED`
* `failure_type_primary` (+ `failure_type_secondary: []`)
* `mode: PROPOSE_ONLY|EXECUTE`
* `created_at_utc`
* `branch`, `base_commit`
* `ssot_refs: []`
* `scope_write_allowlist_ref`
* `primary_run_id`
* `run_ids_repro: []`
* `run_ids_verify: []`
* `repro: {command, expected, observed, exit_code, run_id}`
* `gates_required: [GATE_ID...]`
* `gates_results: {GATE_ID: PASS|FAIL_ACTIONABLE|ERROR_INFRA|BLOCKED_INPUT}`
* `waiver: {present: bool, waiver_id?: string}`
* `rollback_plan_ref`

### 6.4 Pacote mínimo de evidência por tipo (correção)

Regra global:

* sem mínimo completo → IA MUST responder **BLOCKED** com checklist objetivo, sem patch.

Campos globais obrigatórios:

* `repo_root` (lógico)
* `branch` + `base_commit` (ou “dirty + diff”)
* ambiente: `os`, `python_version`, `node_version` (se aplicável), lockfiles presentes, `db_target` (se aplicável)
* expected vs observed
* comando(s) exato(s)
* exit code(s)
* stdout/stderr (com truncation/redaction)
* path+linhas (Lx-Ly)

Mínimos por tipo (resumo):

* AUTH/API_CONTRACT: curl/httpie ou comando do teste, headers/cookies, trecho handler, trecho OpenAPI (se API), exit code
* DB_MIGRATION: comando alembic, revision head/target, trecho migration, stacktrace, alvo DB redigido
* DB_PARITY: comando parity, diffs estruturais, modelos/tabelas, alvo DB redigido
* DOCS: comando do gate, erro + path/âncora, trecho doc
* BUILD_DEPS: comando falho, lockfiles, diff/motivo, versões
* TOOLING_GATES: comando do gate, evidência de que é o gate (não o produto), trecho do gate

### 6.5 REPRO_STEP obrigatório

`_reports/cases/<CORR_ID>/repro.yaml` MUST existir:

* `command` (copiável)
* `prerequisites`
* `expected`
* `observed`
* `exit_code`
* `run_id` (audit run que prova)

Sem REPRO executável: MUST BLOCKED.

### 6.6 Patch mínimo e allowlist

* Patch MUST ser mínimo e atômico.
* Mudanças cosméticas/refactor amplo: MUST NOT.
* Escrita limitada por allowlist SSOT:
  `docs/_canon/_agent/CORRECTION_WRITE_ALLOWLIST.yaml`
* Fora da allowlist: abrir AR para ampliar ou waiver formal.

### 6.7 Mapeamento canônico: falha → gates mínimos obrigatórios

O set mínimo obrigatório vem de:
`docs/_canon/_agent/FAILURE_TO_GATES.yaml`

Regra:

* IA MUST executar (ou waiver formal) o set mínimo do FAILURE_TYPE primário.
* IA MUST NOT escolher gates arbitrários como substituto.
* Gates extras são permitidos, com justificativa.

### 6.8 Rollback determinístico

`rollback.yaml` MUST conter:

* strategy: `revert` | `restore`
* commands exatos
* evidence_preservation: true
* stop_conditions

Rollback:

* commits: `git revert` (sem force-push)
* não comitado: `git restore --staged . && git restore .`

### 6.9 Output contract da IA (formato obrigatório)

A resposta da IA (e/ou arquivo no case) MUST seguir:

* CORR_ID
* FAILURE_TYPE (primário + secundários)
* FACTS (F-###) com referência a evidência (RUN_ID + paths)
* MISSING_EVIDENCE_CHECKLIST (se BLOCKED)
* REPRO_STEP (command/expected/observed/exit/run_id)
* SSOT_BINDINGS (arquivos SSOT usados)
* PATCH_PLAN (arquivos/alterações exatas/risco/side-effects)
* REQUIRED_GATES (GATE_ID + comando)
* EVIDENCE_ARTIFACTS (o que será gerado em `docs/hbtrack/evidence/AR_<id>/`)
* ROLLBACK_PLAN
* STATUS_NEXT

---

## 7) Evidence Pack: redaction, truncation, LGPD, limites

Limites:

* logs por gate: preferencialmente em `docs/hbtrack/evidence/.../checks/...`
* max recomendado por log: 5 MB / 2000 linhas
* encoding: UTF-8

Truncation:

* se exceder: MUST truncar com marcador claro

Redaction (LGPD/secrets):

* MUST redigir tokens, cookies, segredos, emails, IDs pessoais, dumps com PII

Ferramenta canônica:

* `scripts/tools/evidence_pack_sanitize.py` (Python), configurado via `config.py`.

---

## 8) Flakiness, retries, timeouts (regras objetivas)

* Todo gate MUST declarar no registry:

  * `retries_max`
  * condições de retry
  * `timeout_seconds`

Regra default (se não definido):

* retries_max = 0 (sem retry)
* se falha intermitente, classificar e registrar como `ERROR_INFRA` somente com evidência objetiva (timeout/rede), e abrir caso `FT_TOOLING_GATES` ou estabilização.

Gate flakey:

* não conta para VERIFIED até estabilizar ou quarantinar (quarantine também precisa ser formalizada via waiver).

---

## 9) SSOTs obrigatórios (registries canônicos)

Os seguintes arquivos MUST existir e são SSOT:

* `docs/_canon/_agent/GATES_REGISTRY.yaml`
  Define cada gate: id, comando, pré-requisitos, evidências, exit codes, flakiness, timeout.

* `docs/_canon/_agent/FAILURE_TO_GATES.yaml`
  Mapeia `FAILURE_TYPE` → `[GATE_ID...]` mínimos obrigatórios.

* `docs/_canon/_agent/CORRECTION_WRITE_ALLOWLIST.yaml`
  Lista paths editáveis em correções.

* `docs/_canon/_agent/WAIVERS.yaml`
  Registro canônico de waivers.

Opcional (recomendado para tooling):

* `docs/_canon/_agent/FAILURE_TAXONOMY.yaml` (espelho do enum e descrições)

---

## 10) Waiver (escape hatch) — existe, mas é controlado

* Waiver MUST ter ID: `WAIVER-YYYY-MM-DD-NNN`
* MUST ser aprovado por HUMAN
* MUST declarar: requisito waivado, motivo, expiração, mitigação
* MUST ser registrado em:

  * `_reports/cases/<CORR_ID>/state.yaml`
  * `docs/_canon/_agent/WAIVERS.yaml`

Waiver informal é inválido.

---

## 11) Relação CORR vs AR (governança)

Regra canônica:

* CORR = correção de falha evidenciada (bug, contrato, gate, infra) com Evidence Pack e gates mínimos.
* AR = solicitação de arquitetura/feature/mudança de escopo.

Quando vira AR:

* necessidade de alterar SSOTs estruturais (ex.: criar novo gate, mudar pipeline, ampliar allowlist) sem falha imediata;
* mudança ampla não motivada por evidência;
* “melhoria”/refactor.

Quando CORR pode abrir AR:

* se para corrigir for preciso: ampliar allowlist, criar novo gate, migrar legado, ou mudar SSOT de registry.

---

## 12) Enforcement obrigatório (sem isso, vira “guia”)

Determinismo depende de enforcement.

MUST existir (Python):

* `scripts/checks/check_correction_protocol.py`
  Valida: estrutura do case, schema state.yaml, enum, repro, gates mínimos, allowlist, manifest/hashes, waivers.

Recomendado (também como gate):

* `scripts/checks/check_audit_pack.py`
  Valida: estrutura `docs/hbtrack/evidence/AR_<id>/`, presence de context/summary/result, exit code normalizado, base_url, commit.

Esses checks MUST estar registrados no `GATES_REGISTRY.yaml`.

---

## 13) Split/Merge de casos (evita caos)

Split obrigatório:

* se uma evidência contém múltiplas falhas primárias, abrir múltiplos CORR.

Merge proibido sem prova:

* só com mesmo REPRO_STEP, mesmo patch mínimo, e aprovação humana.

---

## 14) Governança e versionamento

* Este manual é SSOT.
* Mudanças MUST:

  * atualizar versão (v1.1…)
  * registrar rationale e impacto
  * definir migração (se schema mudar)
  * ter aprovação humana

Compatibilidade retroativa:

* casos antigos ficam congelados com `protocol_version` no `state.yaml`.

---

## 15) Templates mínimos (copiáveis)

### 15.1 `docs/hbtrack/evidence/AR_<id>/context.json`

```json
{
  "run_id": "RUN-... ",
  "timestamp_utc": "2026-02-18T00:00:00Z",
  "git": { "branch": "dev", "commit": "abcdef123" },
  "environment": {
    "os": "windows|linux",
    "python_version": "3.11.9",
    "node_version": "20.x",
    "db_target": "local|staging|neon|vps"
  },
  "base_url": {
    "api": "https://...",
    "web": "https://..."
  }
}
```

### 15.2 `docs/hbtrack/evidence/AR_<id>/summary.json`

```json
{
  "run_id": "RUN-...",
  "overall_exit_code": 2,
  "checks": [
    { "id": "AUTH_E2E_LOGIN", "exit_code": 2, "status": "FAIL_ACTIONABLE" },
    { "id": "AUTH_SMOKE_RUNTIME", "exit_code": 0, "status": "PASS" }
  ]
}
```

### 15.3 `docs/hbtrack/evidence/AR_<id>/checks/<GATE_ID>/result.json`

```json
{
  "id": "AUTH_E2E_LOGIN",
  "command": "npx playwright test ...",
  "exit_code": 2,
  "status": "FAIL_ACTIONABLE",
  "duration_ms": 123456,
  "artifacts": ["playwright-report/", "stdout.log", "stderr.log"]
}
```

### 15.4 `_reports/cases/<CORR_ID>/state.yaml`

```yaml
corr_id: CORR-2026-02-18-001
protocol_version: v1.0
status: BLOCKED
mode: PROPOSE_ONLY
failure_type_primary: FT_AUTH_CONTRACT
failure_type_secondary: []
created_at_utc: 2026-02-18T00:00:00Z
branch: dev
base_commit: abcdef123
ssot_refs:
  - docs/_canon/_agent/GATES_REGISTRY.yaml
scope_write_allowlist_ref: docs/_canon/_agent/CORRECTION_WRITE_ALLOWLIST.yaml
primary_run_id: RUN-CORR-2026-02-18-001-01
run_ids_repro: [RUN-CORR-2026-02-18-001-01]
run_ids_verify: []
repro:
  command: "python scripts/audit/audit_runner.py --only AUTH_SMOKE_RUNTIME"
  expected: "/health 200; /auth/me 200"
  observed: "/auth/me 401"
  exit_code: 2
  run_id: RUN-CORR-2026-02-18-001-01
gates_required: [AUTH_E2E_LOGIN, AUTH_CONTRACT_OPENAPI, AUTH_SMOKE_RUNTIME]
gates_results: {}
waiver: { present: false }
rollback_plan_ref: rollback.yaml
```

---



0.3.1 Politica VPS (PY-ONLY)

Na VPS, somente scripts Python (.py) sao implantados/executados.
Wrappers locais (.ps1/.sh) MAY existir para desenvolvimento local, mas MUST NOT ser requisito de operacao na VPS.
