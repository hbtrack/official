# INVARIANTS_OPERACIONAIS_HBTRACK.md

Status: ATIVO
Versão: v1.4.0
Autoridade: NORMATIVO_OPERACIONAL (SSOT)
Escopo: Sistema HB Track (todos os módulos)
Última atualização: 2026-03-04

Última revisão: 2026-03-04  
Próxima revisão recomendada: 2026-03-11  

> **Ponteiro SSOT:** O path canônico deste documento é definido pela constante `DEFAULT_OPS_DOC` em `scripts/gates/check_ops_invariants.py` (autoridade única).
> A task VS Code `"HB: scan ops invariants"` em `.vscode/tasks.json` é apenas consumidora — não declara o path.
>
> Se este arquivo for movido, atualize **somente** `DEFAULT_OPS_DOC` no scanner.

> Changelog v1.4.0 (2026-03-04):
> - **Registro OPS-GATE-001 no GATES_REGISTRY**: gate manual com `required_proofs` e nota de comando — AR_900
> - **Ponteiro SSOT documentado** no cabeçalho do doc; output do scanner refatorado para `key=value` estável (`marker=OPS-SCAN/V1` em linha própria) — AR_900

> Changelog v1.3.0 (2026-03-04):
> - **Catálogo sequencial 001–015+DOC**: substitui numeração esparsa (001/002/003/010/020/030/040/050/060) — AR_900
>   - Adicionados INV-OPS-004 (encoding seguro), INV-OPS-005 (stdout/import), INV-OPS-006 (handoff SSOT), INV-OPS-007 (PROOF/TRACE), INV-OPS-008 (strict DoD), INV-OPS-009 (determinismo), INV-OPS-012 (WARN prefixo), INV-OPS-013 (paths imutáveis), INV-OPS-014 (tasks VS Code), INV-OPS-015 (gates com testes), INV-OPS-DOC — AR_900

> Changelog v1.2.0 (2026-03-04):
> - **INV-OPS-011 adicionado** (linguagem de automação oficial: Python; inventário de .sh/.ps1 com waivers) — AR_900

> Changelog v1.1.0 (2026-03-03):
> - Status DRAFT→ATIVO; `introduced_in` preenchido em INV-OPS-002/003 — AR_900

> Changelog v1.0.0 (2026-03-03):
> - Criação inicial com INV-OPS-001, INV-OPS-002, INV-OPS-003, INV-OPS-010

## 0) Regra de precedência (SSOT)

Ordem de precedência para decisões operacionais (quando houver conflito):

1. Este documento (INVARIANTS_OPERACIONAIS_HBTRACK.md)
2. `GATES_REGISTRY.yaml`
3. `hb_cli.py` (implementação)
4. `.github/agents/*.agent.md` (protocolo de agentes)
5. Docs de módulos (`docs/hbtrack/modulos/**`)
6. Histórico do chat (NUNCA é SSOT)

## 1) Glossário operacional

* Invariante Operacional: regra que deve ser verdadeira no runtime (dev/CI/prod) para o sistema ser considerado saudável e determinístico.
* Gate: verificação automatizada (script) registrada no `GATES_REGISTRY.yaml`.
* DoD: Definition of Done operacional por AR_ID.
* Handoff: `_reports/ARQUITETO.md`.

## 2) Formato canônico de Invariante Operacional

Cada invariante DEVE seguir o schema abaixo.

### 2.1 Identificador

Formato: `INV-OPS-###` (ex.: `INV-OPS-001`).

### 2.2 Campos obrigatórios

* `id`
* `name`
* `class` (A/B/C)
* `scope` (SYSTEM | DEV | CI | PROD | AGENTS | GATES | REPO | SECURITY | DATA | OBSERVABILITY)
* `statement` (texto normativo, com MUST/DEVE)
* `rationale` (por quê, curto)
* `enforcement` (como é verificado; comando + artefato)
* `evidence` (path(s) canônicos + marcador/âncora)
* `failure_mode` (como falha aparece)
* `exit_policy` (0/2/3/4 etc, quando aplicável)
* `waiver_policy` (quando e como pode ser waivado; sempre explícito)
* `owner` (Arquiteto/Executor/Testador/DevOps)
* `introduced_in` (data + AR/commit, se existir)

## 3) Catálogo de Invariantes Operacionais

### INV-OPS-001 — Entrypoint único do hb_cli

class: A
scope: SYSTEM
statement: O sistema DEVE possuir um único entrypoint efetivo para `hb plan/report/verify`; tasks, testes e runtime DEVEM apontar para o mesmo arquivo.
rationale: Evita divergência "editei um hb_cli, executei outro".
enforcement:
  * Verificar `.vscode/tasks.json` aponta para o mesmo path usado pelo pipeline.
  * Scanner: `check_ops_invariants.py` (INV-OPS-001).
evidence:
  * `.vscode/tasks.json`
  * `scripts/run/hb_cli.py`
failure_mode: testes passam mas runtime não reflete mudanças; selos sem marcador esperado.
waiver_policy: Proibido.
owner: DevOps/Executor
introduced_in: YYYY-MM-DD

### INV-OPS-002 — Workspace Clean é pré-condição para evidência válida

class: A
scope: DEV
statement: Qualquer evidência (executor_main.log/result.json) só é válida se o workspace estiver limpo no momento da execução.
rationale: Evita resultados não reproduzíveis.
enforcement:
  * hb_cli registra `Workspace Clean: True` no log.
  * Testador rejeita evidência com workspace sujo.
evidence:
  * `docs/hbtrack/evidence/AR_<id>/executor_main.log` contém `Workspace Clean: True`
failure_mode: AR marcada como NEEDS_REDO.
waiver_policy: Permitido apenas com justificativa explícita e AR de governança.
owner: Executor/Testador
introduced_in: YYYY-MM-DD

### INV-OPS-003 — Registro canônico de gates

class: A
scope: GATES
statement: Todo gate operacional DEVE estar registrado no `GATES_REGISTRY.yaml` com id único e trigger adequado.
rationale: Evita gates que existem no disco mas não são executados.
enforcement:
  * Scanner: `check_ops_invariants.py` (INV-OPS-003) verifica DOC-GATE-019/020/021.
  * hb_cli executa gates por trigger registrado.
evidence:
  * `docs/_canon/specs/GATES_REGISTRY.yaml`
failure_mode: gate não roda em hb report/verify; warnings nunca aparecem.
waiver_policy: Permitido temporariamente com waiver documentado e ticket/AR.
owner: Arquiteto/DevOps
introduced_in: YYYY-MM-DD

### INV-OPS-004 — Gates executam com encoding seguro

class: A
scope: GATES
statement: Todo `subprocess.run` que executa gates DEVE definir `encoding="utf-8"` e `errors="replace"`.
rationale: Evita UnicodeDecodeError/EncodeError no Windows e em pipes.
enforcement:
  * Scan estático no hb_cli por `subprocess.run(` em blocos de gate-runner.
  * Scanner: `check_ops_invariants.py` (INV-OPS-002).
  * Teste unitário cobrindo saída com caracteres não-ASCII.
evidence:
  * `scripts/run/hb_cli.py` (funções runner de gate)
  * `scripts/gates/tests/**`
failure_mode: `_readerthread UnicodeDecodeError` ou crash do gate ao imprimir ⚠️.
waiver_policy: Proibido.
owner: Executor
introduced_in: 2026-03-04 (AR_900 — fix encoding em _gate_handoff_preflight + _run_gate_output)

### INV-OPS-005 — Scripts de gate não alteram stdout/stderr no import

class: A
scope: GATES
statement: Scripts de gate NÃO DEVEM alterar `sys.stdout`/`sys.stderr` durante import; qualquer rewrap DEVE ocorrer apenas sob `if __name__ == "__main__":`.
rationale: Evita corromper pytest capture e imports.
enforcement:
  * grep/scan por `sys.stdout =` fora do bloco `__main__`.
  * Teste unitário: importar módulo sem side effects.
evidence:
  * `scripts/gates/*.py`
failure_mode: pytest capture quebrado, ImportError indireto, output truncado.
waiver_policy: Proibido.
owner: Executor/Testador
introduced_in: 2026-03-04 (AR_900 — rewrap movido para `__main__` em check_handoff_contract.py)

### INV-OPS-006 — Handoff é SSOT operacional

class: A
scope: AGENTS
statement: `_reports/ARQUITETO.md` é a única fonte de verdade operacional para Executor e Testador.
rationale: Evita inferência baseada em histórico de chat.
enforcement:
  * `.github/agents/Executor.agent.md` e `.github/agents/Testador.agent.md` contêm a regra explícita.
  * Scanner: `check_ops_invariants.py` (INV-OPS-010) valida needles mínimos.
evidence:
  * `_reports/ARQUITETO.md`
  * `.github/agents/*.agent.md`
failure_mode: execução fora de escopo, re-run desnecessário, drift.
waiver_policy: Proibido.
owner: Arquiteto/Executor/Testador
introduced_in: YYYY-MM-DD

### INV-OPS-007 — PROOF e TRACE obrigatórios por AR_ID

class: A
scope: AGENTS
statement: Cada AR_ID no handoff DEVE declarar PROOF e TRACE (ou `N/A (governance)` para suprimir gates 020/021).
rationale: Evita ARs incompletas e trabalho em ondas.
enforcement:
  * DOC-GATE-019 (`check_handoff_contract.py`) e DOC-GATE-020 (`check_trace_contract.py`).
evidence:
  * `_reports/ARQUITETO.md` (bloco por AR_ID)
failure_mode: WARN em DOD-TABLE, PROOF=[⚠] ou TRACE=[⚠].
waiver_policy: Declarar `PROOF: N/A (governance)` / `TRACE: N/A (governance)` no handoff.
owner: Arquiteto
introduced_in: YYYY-MM-DD

### INV-OPS-008 — Strict DoD no verify

class: A
scope: CI
statement: `hb verify <ar_id>` DEVE aplicar strict DoD antes do triple-run e falhar com exit 2 se houver WARN não-waivered para o AR_ID.
rationale: Impede que WARNs passem silenciosamente.
enforcement:
  * Testes dos helpers DoD em `scripts/gates/tests/test_dod_helpers.py`.
evidence:
  * `_reports/testador/AR_<id>_*/result.json` contém `"dod": {...}`
failure_mode: exit 2 `E_DOD_STRICT_WARN`.
waiver_policy: Apenas via PROOF/TRACE N/A no handoff.
owner: Testador
introduced_in: YYYY-MM-DD

### INV-OPS-009 — Evidência deve ser determinística

class: A
scope: CI
statement: Execuções repetidas de um mesmo `hb verify` DEVEM produzir hashes idênticos (triple-run).
rationale: Garante determinismo e impede evidência forjada.
enforcement:
  * Triple-run do `hb verify` com comparação de hashes.
evidence:
  * `_reports/testador/<ar>_*/result.json` → `consistency: OK`
failure_mode: hash mismatch → exit 2 `E_HASH_MISMATCH`.
waiver_policy: Proibido.
owner: Testador
introduced_in: YYYY-MM-DD

### INV-OPS-010 — Artefatos derivados devem ser materializáveis

class: B
scope: DEV/CI
statement: Quando testes contêm `@pytest.mark.trace("ID")`, o sistema DEVE ser capaz de materializar a TEST_MATRIX via `gen_test_matrix.py --update-matrix` sem erro.
rationale: Rastreabilidade não pode depender de edição manual.
enforcement:
  * smoke test com dry-run e update-matrix em fixture.
evidence:
  * `scripts/generate/gen_test_matrix.py`
  * diffs no `TEST_MATRIX_*.md`
failure_mode: IDs permanecem PENDENTE; matriz não atualiza.
waiver_policy: Permitido apenas se módulo não aderiu à política de derivação (explicitamente documentado).
owner: Executor/Arquiteto
introduced_in: YYYY-MM-DD

### INV-OPS-011 — Linguagem de automação oficial

class: B
scope: DEV | CI | OPS
statement: >
  Scripts de automação do sistema HB Track DEVEM ser implementados em Python (.py).
  Shell scripts (.sh) e PowerShell (.ps1) NÃO DEVEM conter lógica operacional do sistema
  (gates, reports, verify, CLI, policy checks).
  São permitidos apenas como wrappers triviais que delegam para scripts Python.
rationale: >
  Garantir portabilidade entre Windows (desenvolvimento) e Linux (VPS/CI) e
  evitar duplicação de lógica entre bash e PowerShell.
enforcement:
  * `git ls-files 'scripts/**/*.ps1' 'scripts/**/*.sh'` → revisar conteúdo.
  * Arquivo com lógica ≥5 linhas deve ter equiv. em `.py` ou migrar.
evidence:
  * `scripts/**/*.py`
  * `scripts/run/hb_cli.py`
failure_mode: >
  Duplicação de lógica em múltiplas linguagens; gates que funcionam no Windows
  mas quebram no CI Linux (ou vice-versa).
waiver_policy: >
  Permitido para:
  a) Infraestrutura externa: provisioning, Docker, CI runner, VPS bootstrap.
  b) Wrappers triviais: ≤3 linhas chamando `python <script>.py`.
  c) Tooling de frontend: scripts sob `Hb Track - Frontend/` fora de escopo.
  d) Arquivos temporários sob `temp/` (expira com a tarefa).
  Waiver deve ser documentado com `waiver_id` no §4 deste arquivo.
owner: Arquiteto
introduced_in: 2026-03-04 (AR_900 — inventário inicial de .sh/.ps1)

#### Inventário de .sh/.ps1 existentes (2026-03-04)

| Caminho | Kind | Status INV-OPS-011 |
|---------|------|---------------------|
| `scripts/run/run_*.ps1` | Stubs/runners ("Implementation pending") | ⚠ Migrar para `.py` ou wrapper trivial |
| `scripts/checks/**/*.ps1` | Lógica operacional (CHECK) | ⚠ Candidatos a migração Python |
| `scripts/_policy/*.ps1` | Validação de policy | ⚠ Candidatos a migração Python |
| `scripts/gates/SSOT/*.ps1` | Gate CI local | ⚠ Candidatos a migração Python |
| `scripts/generate/**/*.ps1` | Geração de artefatos | ⚠ Revisar/migrar |
| `scripts/ssot/gen_docs_ssot.ps1` | Geração SSOT | ⚠ Candidato a migração |
| `scripts/ops/infra/*.ps1` | PROC_START_STOP (Celery/Flower) | ✅ Waiver (a) — infra externa |
| `scripts/ops/db/*.ps1` | DB ops | ✅ Waiver (a) — infra externa |
| `scripts/reset/**/*.ps1` | Reset DB/serviços | ✅ Waiver (a) — infra externa |
| `scripts/diagnostics/runtime/diag_vps_python_runtime.sh` | Diagnóstico VPS | ✅ Waiver (a) — VPS bootstrap |
| `Hb Track - Frontend/**/*.ps1` | E2E / sync frontend | ✅ Fora de escopo (c) |
| `temp/*.ps1` | Rascunhos temporários | ✅ Waiver (d) — expiram com tarefa |

### INV-OPS-012 — Gates não bloqueantes devem registrar WARN

class: B
scope: GATES
statement: Gates WARN-only DEVEM sempre imprimir aviso explícito com prefixo `⚠️ WARN:` ou `[WARN]` antes de retornar exit 0.
rationale: Executor precisa ver o problema sem que o pipeline seja bloqueado.
enforcement:
  * Prefixo padrão `⚠ WARN:` ou `[WARN]` — capturável por `_parse_gate_warns_for_ar`.
evidence:
  * stdout do gate
failure_mode: WARN passa silenciosamente; DoD-TABLE mostra ✅ mesmo com problema real.
waiver_policy: Proibido.
owner: Executor
introduced_in: YYYY-MM-DD

### INV-OPS-013 — Paths de evidência são imutáveis

class: A
scope: REPO
statement: Paths de evidência DEVEM seguir o padrão `docs/hbtrack/evidence/AR_<id>/executor_main.log`; hb_cli não deve escrever nesses artefatos fora desse padrão.
rationale: Ferramentas (gates, scripts, CI) dependem desse padrão estável.
enforcement:
  * Validação no hb_cli ao escrever evidência.
evidence:
  * `docs/hbtrack/evidence/AR_<id>/executor_main.log`
failure_mode: gate não encontra log; DoD-TABLE falha.
waiver_policy: Proibido.
owner: Executor
introduced_in: YYYY-MM-DD

### INV-OPS-014 — Tasks VS Code refletem comandos oficiais

class: B
scope: DEV
statement: Tasks VS Code DEVEM mapear diretamente para comandos `hb_cli`, sem duplicar lógica.
rationale: Evita divergência entre o que o dev clica e o que o pipeline executa.
enforcement:
  * Scanner: `check_ops_invariants.py` (INV-OPS-001) valida entrypoint.
evidence:
  * `.vscode/tasks.json`
failure_mode: dev usa task que chama outro script; pipeline não é exercitado localmente.
waiver_policy: Permitido para tasks auxiliares (lint, build frontend) que não são pipeline HB.
owner: DevOps
introduced_in: YYYY-MM-DD

### INV-OPS-015 — Gates devem possuir testes

class: A
scope: GATES
statement: Todo script `check_*.py` em `scripts/gates/` DEVE ter um `test_check_*.py` correspondente em `scripts/gates/tests/`.
rationale: Gates são parte do sistema crítico; regressões devem ser capturadas antes do commit.
enforcement:
  * Scanner: `check_ops_invariants.py` (INV-OPS-015) valida correspondência arquivo a arquivo.
evidence:
  * `scripts/gates/tests/`
failure_mode: gate quebrado não é detectado; E2E falha silenciosamente.
waiver_policy: Proibido.
owner: Executor/Testador
introduced_in: 2026-03-04 (AR_900 — adicionados testes para check_handoff_contract, check_trace_contract, trace_stitcher, check_ops_invariants)

### INV-OPS-DOC — Doc SSOT de invariantes deve existir no path configurado

class: A
scope: SYSTEM
statement: O arquivo SSOT de invariantes operacionais DEVE existir no path configurado em `check_ops_invariants.py` (default: `docs/invariantes/INVARIANTS_OPERACIONAIS_HBTRACK.md`).
rationale: O scanner é inútil se o doc que ele protege não existir.
enforcement:
  * Scanner: `check_ops_invariants.py` (INV-OPS-DOC) — BLOCKED_INPUT se ausente.
evidence:
  * `docs/invariantes/INVARIANTS_OPERACIONAIS_HBTRACK.md`
failure_mode: scanner retorna BLOCKED_INPUT (exit 4).
waiver_policy: Proibido.
owner: Arquiteto
introduced_in: 2026-03-04 (AR_900 — check_ops_invariants.py)

## 4) Waivers

Registrar aqui waivers explícitos para invariantes com `waiver_policy` permissivo.

| waiver_id | invariante | AR/ticket | justificativa | expira |
|-----------|-----------|-----------|---------------|--------|
| W-INV-OPS-011-001 | INV-OPS-011 — scripts/run/run_*.ps1 | AR_900 | Stubs legados; migração planejada | 2026-06-01 |
| W-INV-OPS-011-002 | INV-OPS-011 — scripts/checks/**/*.ps1 | AR_900 | Revisão pendente; scripts sem equivalente Python | 2026-06-01 |

## 5) Changelog

Ver cabeçalho do documento (blocos `> Changelog vX.Y.Z`).

<!-- Histórico resumido para referência rápida:
  v1.4.0 (2026-03-04): OPS-GATE-001; ponteiro SSOT; output key=value — AR_900
  v1.3.0 (2026-03-04): catálogo sequencial 001–015+DOC — AR_900
  v1.2.0 (2026-03-04): INV-OPS-011 (automação Python) — AR_900
  v1.1.0 (2026-03-03): DRAFT→ATIVO; introduced_in — AR_900
  v1.0.0 (2026-03-03): criação inicial
-->
