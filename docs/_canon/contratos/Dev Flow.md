# HBTRACK_DEV_FLOW_CONTRACT — HB Track (Determinístico) — v1.2.0 (SSOT)

STATUS: **SSOT**
SSOT_KIND: **CONTRACT**
SCOPE: fluxo determinístico de desenvolvimento governado por AR + evidências (Arquiteto/Executor/Testador/Humano)
NORMS: MUST / MUST NOT / SHOULD / MAY (BCP14)

## 1) Versão e Governança (imutável sem AR de governança)

1.1) **PROTOCOL_VERSION = v1.3.0**

1.2) `scripts/run/hb_cli.py` MUST reportar **PROTOCOL_VERSION** via:

* `hb version`
* header do `hb check` (qualquer `--mode`)

1.3) Qualquer mudança em qualquer arquivo dentro de:

* `docs/_canon/contratos/**`
* `docs/_canon/specs/**`
  MUST:
  A) ser feita via **AR de governança** em `docs/hbtrack/ars/`
  B) bump de **PROTOCOL_VERSION**
  C) atualizar a versão reportada pelo `hb_cli.py`
  D) gerar evidence pack do gate de governança (Seção 6 + Seção 9)

## 2) Canon Paths (imutáveis sem AR de governança)

2.1) Referências

* PRD: `docs/hbtrack/PRD Hb Track.md`
* SSOT do sistema: `docs/ssot/`

  * `docs/ssot/schema.sql`
  * `docs/ssot/openapi.json`
  * `docs/ssot/alembic_state.txt`

2.2) Fluxo (artefatos governados)

* Planos (JSON do Arquiteto): `docs/_canon/planos/*.json`
* ARs (materialização do plano): `docs/hbtrack/ars/`
* Evidence packs (Executor/Testador): `docs/hbtrack/evidence/`
* Índice canônico (obrigatório): `docs/hbtrack/_INDEX.md`

2.3) Índice (regra dura)

* `docs/hbtrack/_INDEX.md` é o **Registry da Máquina de Estados** no commit.
* MUST ser **AUTO-GERADO** por hb (`hb plan` / `hb report` / `hb verify` / `hb index` se existir).
* MUST NOT ser editado manualmente.
* **Qualquer AR staged ⇒ `_INDEX.md` MUST estar staged** (enforcement no pre-commit).

2.4) Legado (proibido editar)

* `docs/hbtrack/ars/_INDEX.md` é LEGADO, NÃO é SSOT, MUST NOT ser editado.

2.5) Execução (scripts)

* CLI oficial: `scripts/run/hb_cli.py`
* Watcher + Dispatcher: `scripts/run/hb_watch.py` v1.2.2 (dashboard + dispatch context JSON em `_reports/dispatch/<modo>_context.json`)
* Daemon Plan Watcher: `scripts/run/hb_plan_watcher.py` (auto-materialize daemon — monitora `docs/_canon/planos/*.json`, claim atômico, dry-run obrigatório, staging apenas diff)
* Daemon Testador: `scripts/run/hb_autotest.py` (Testador autônomo — detecta evidence staged → `hb verify` → `hb seal`)
* Git hook: `scripts/git-hooks/pre-commit` (executável Python)
* Política: scripts operacionais MUST ser Python; `.sh` e `.ps1` são proibidos.

## 3) Definições (canônicas)

3.1) **Schema Version (AR Contract)**

* `ar_contract.schema.json` MUST declarar `schema_version` (string) em local canônico.
* Essa é a versão de estrutura do plano/AR (independente de PROTOCOL_VERSION).

3.2) **Plano (Plan JSON)**

* arquivo JSON criado pelo Arquiteto, validado por schema canônico.

3.3) **AR (Architectural Record)**

* arquivo `.md` gerado por `hb plan`, governando UMA tarefa atômica.

3.4) **Evidence pack do Executor**

* arquivo `.log` gerado por `hb report`, path MUST ser determinístico: `docs/hbtrack/evidence/<AR_ID>/executor_main.log`
* conteúdo mínimo obrigatório:

  * command_line (string)
  * exit_code (int)
  * stdout (texto bruto)
  * stderr (texto bruto)
  * behavior_hash (SHA-256 de exit_code + stdout_norm + stderr_norm) — Seção 6.6
  * checksums (SHA-256 por arquivo governado, snapshot do repo)
  * workspace_state (git status + HEAD)
  * timestamp_utc (ISO 8601 UTC)

3.5) **TESTADOR_REPORT**

* artefato gerado por `hb verify`, obrigatório em `_reports/testador/<AR_ID>/...` e **MUST estar staged quando houver verify** (Seção 8 e Seção 9).

3.6) **GOVERNED_ROOTS**

* NÃO pode estar hardcoded em scripts.
* Fonte canônica MUST ser arquivo SSOT em `docs/_canon/specs/GOVERNED_ROOTS.yaml` (Seção 4.4).

3.7) **AR como Única Voz (assíncrono)**

* Agentes MUST NOT se comunicar diretamente.
* Comunicação formal ocorre via campos da AR e do plano:

  * Arquiteto → `notes` do plano/AR
  * Executor → seção “Análise de Impacto” da AR + evidence do report
  * Testador → resultado do verify + reason + status
  * Humano → selo final “✅ VERIFICADO”

## 4) Contrato do Plano (AR Contract)

4.1) Path: plano MUST estar em `docs/_canon/planos/*.json`

4.2) Schema: plano MUST validar contra `docs/_canon/contratos/ar_contract.schema.json`

4.3) Versão: `plano.version` MUST ser **igual a `schema_version`** declarado no `ar_contract.schema.json` (separada de PROTOCOL_VERSION). Violação => FAIL com `E_PLAN_VERSION_MISMATCH`.

4.4) Governança de roots (SSOT)

* MUST existir `docs/_canon/specs/GOVERNED_ROOTS.yaml` como SSOT, contendo a lista de roots governados.
* `hb` MUST carregar essa lista e usá-la em `hb report`, `hb verify` e `hb check`.

Formato mínimo (normativo) do `GOVERNED_ROOTS.yaml`:

* `version` (string)
* `roots` (lista de paths relativos, sem glob ambíguo)
* `notes` (opcional)

4.5) Texto livre: permitido APENAS nos campos explicitamente previstos no schema (ex.: notes/assumptions/risks e notes por task). Fora disso => FAIL.

4.6) Banco/SSOT: tasks que tocam banco/SSOT (`ssot_touches` contém `schema.sql` ou `alembic_state.txt`) MUST incluir `rollback_plan` com comandos válidos (Seção 7).

## 5) Ciclo de Vida (fluxo oficial)

Passo 1 — REFERÊNCIA (Arquiteto)
Arquiteto lê PRD + SSOT.

Passo 2 — PLANO (Arquiteto)
Arquiteto cria plano JSON válido e salva em `docs/_canon/planos/<nome>.json`.

Passo 3 — MATERIALIZAÇÃO (Humano)
Executar:

* `python scripts/run/hb_cli.py plan docs/_canon/planos/<nome>.json [--force|--skip-existing|--dry-run]`

Efeitos:

* cria ARs em `docs/hbtrack/ars/AR_<id>_<slug>.md` (escrita atômica via `.tmp/`)
* atualiza `docs/hbtrack/_INDEX.md` (obrigatório)
* aplica gates: schema/version/anti-trivial (Seção 6)

Passo 4 — ANÁLISE (Executor)
Executor MUST preencher “Análise de Impacto” ANTES de alterar qualquer arquivo em GOVERNED_ROOTS.

Passo 5 — AÇÃO (Executor)
Executor implementa a mudança no código.

Passo 6 — EVIDÊNCIA (Executor)
Executar:

* `python scripts/run/hb_cli.py report <AR_ID> "<validation_command>"`

Regras:

* `<validation_command>` MUST ser idêntico ao declarado na task/AR quando existir; se não existir, MUST ser registrado como o comando da task no evidence pack (reprodutibilidade).
* `hb report` MUST gravar evidence pack em `docs/hbtrack/evidence/<AR_ID>/executor_*.log`.
* `hb report` MUST coletar checksums SHA-256 (pre) de arquivos governados e estado do workspace (pre).

Passo 6.5 — VERIFICAÇÃO (Testador)
Executar:

* `python scripts/run/hb_cli.py verify <AR_ID>`

Regras:

* Pre-check: workspace MUST NOT ter mudanças **não-staged** em arquivos rastreados (anti-falsa-evidência). Mudanças staged (trabalho do Executor) são **PERMITIDAS** — o Testador verifica exatamente esse estado. Workspace com unstaged modifications => FAIL hard com `E_VERIFY_DIRTY_WORKSPACE`.
* Testador MUST re-executar o validation_command independentemente.
* TRIPLE_RUN_COUNT = 3 (3 execuções independentes).
* PASS do Testador exige: (i) 3× exit 0, (ii) behavior_hash idêntico entre runs (Seção 6.6).
* FLAKY_OUTPUT: todos exit 0 mas hash diferente => **🔴 REJEITADO**.
* `hb verify` MUST produzir `TESTADOR_REPORT` em `_reports/testador/<AR_ID>/...`
* Testador SÓ DEVE atuar quando evidence do Executor estiver STAGED (enforcement via `hb_watch.py` dispatch + `hb_autotest.py` polling).
* Testador autônomo: `hb_autotest.py` detecta evidence staged → executa `hb verify` → staging automático de TESTADOR_REPORT → `hb seal` (quando SUCESSO).
* Testador MUST atualizar status da AR para:

  * **✅ SUCESSO** (quando PASS)
  * **🔴 REJEITADO** (quando FAIL_ACTIONABLE)
  * **⏸️ BLOQUEADO_INFRA** (quando ERROR_INFRA)
* Testador MUST NOT escrever "✅ VERIFICADO" diretamente — esse status MUST ser escrito via `hb seal` (Passo 7): pelo Humano ou pelo daemon `hb_autotest.py`.

Passo 7 — SELO — último gate de verificação (hb_autotest automático ou Humano)
Executar via `hb seal`:

* `python scripts/run/hb_cli.py seal <AR_ID> ["reason"]`

**Modo autônomo (`hb_autotest.py`):** quando `triple_consistency=OK + executor_exit=0 + ah_flags=[]`, o daemon executa `hb seal` automaticamente após staging de TESTADOR_REPORT. Não requer intervenção humana.

**Modo manual (Humano):** Humano executa `hb seal` diretamente — obrigatório em casos de REJEITADO resolvido, BLOQUEADO_INFRA com waiver, ou quando `hb_autotest` não estiver ativo.

Pré-condições duras (enforcement — idênticas em ambos os modos):

* AR MUST ter status **✅ SUCESSO** (Testador)
* AR MUST ter `TESTADOR_REPORT` staged
* `TESTADOR_REPORT`/result.json MUST indicar PASS
* Evidence do Executor (`docs/hbtrack/evidence/AR_<id>/executor_main.log`) MUST existir, conter "Exit Code: 0", e estar staged

Efeito:

* Promove AR para **✅ VERIFICADO** (selo final)
* Appenda carimbo com timestamp UTC + motivo
* Rebuild _INDEX.md

`✅ VERIFICADO` MUST ser escrito exclusivamente via `hb seal` — nunca por edição manual direta.

Passo 8 — PRE-COMMIT (enforcement)
No commit, o hook executa:

* `python scripts/run/hb_cli.py check --mode pre-commit`

## 6) Regras determinísticas mínimas (mecanizadas)

6.1) Anti-trivial command (bloqueio na materialização)
`validation_command` trivialmente passável MUST FAIL com `E_TRIVIAL_CMD`.

Definição mínima (normativa):

* comandos “sempre verdes” sem asserção real (ex.: `echo`, `true`, `exit 0`) MUST ser bloqueados;
* comandos cujo resultado não depende do código/artefato governado MUST ser bloqueados.

6.2) Plano inválido (path/schema/version) => `hb plan` FAIL e não materializa AR.

6.3) Evidence mínima para sucesso (por AR)
Para uma AR ser elegível a “✅ VERIFICADO”, MUST existir:

* evidence do Executor staged (Exit Code 0)
* status do Testador = **✅ SUCESSO**
* `TESTADOR_REPORT` staged (obrigatório)

6.4) SSOT-touch (staged)
Se `docs/ssot/**` estiver staged => MUST existir AR staged que:

* marcou o SSOT em `ssot_touches`
* tem `rollback_plan` válido
* possui evidence do Executor exit 0 staged
* possui `TESTADOR_REPORT` staged
* está **✅ VERIFICADO** (selo humano) antes do commit

6.5) Governed roots (staged)
Se qualquer arquivo dentro de qualquer root em `GOVERNED_ROOTS.yaml` estiver staged => MUST existir pelo menos 1 AR staged que cubra a mudança e esteja **✅ VERIFICADO**.

6.6) Hash canônico (triple-run) — behavior_hash
O hash MUST cobrir **exit_code + stdout + stderr**, com normalização determinística:

* converter CRLF→LF e CR→LF em stdout e stderr antes do hash
* payload do hash (exato):

  * `<exit_code>\n<stdout_norm>\n---STDERR---\n<stderr_norm>`
  * exemplo: `"0\nOK\n---STDERR---\n"`
* algoritmo: SHA-256 em UTF-8 (hex digest completo)
* qualquer timestamp/log não-determinístico no output é responsabilidade do validation_command; se variar, vira FLAKY_OUTPUT ⇒ REJEITADO.

Este hash é chamado **behavior_hash** no evidence pack e é canônico para comparação entre Executor e Testador.

## 7) Whitelist de rollback_plan (comandos válidos)

`rollback_plan` MUST conter apenas comandos na whitelist mínima abaixo:

A) `python scripts/run/hb_cli.py ...` (comandos internos HB Track)

B) `git checkout -- <file>`

* restrito a reversão de arquivos específicos

C) `git clean -fd <dir>`

* restrito a limpeza de artefatos não rastreados dentro do diretório explicitamente declarado

D) `psql -c "TRUNCATE ..."`

* restrito a **tabelas de staging/testes** (proibido truncar dados de produção)
* o plano/AR MUST declarar explicitamente quais tabelas são staging/test e justificar
* credenciais MUST NOT aparecer em texto plano no evidence pack (redação/mascara é obrigatória no hb)

Qualquer comando fora dessa whitelist => FAIL em `hb plan` (BLOCKED_INPUT) e em `hb check` (pre-commit).

## 8) Regras de Governança de ARs (mecanizadas)

R-AR-1) `docs/hbtrack/_INDEX.md` é AUTO-GERADO. MUST NOT editar manualmente.

R-AR-2) ARs "✅ VERIFICADO" são IMUTÁVEIS. Corpo MUST NOT ser alterado manualmente. ARs com "✅ SUCESSO" (Testador) AINDA SÃO MUTÁVEIS até o selo humano.

R-AR-3) Pre-commit MUST bloquear:

* AR staged sem `_INDEX.md` staged => `E_AR_INDEX_NOT_STAGED`
* AR "✅ VERIFICADO" alterada => `E_AR_IMMUTABLE`
* AR com verify (status ✅ SUCESSO/🔴 REJEITADO) sem `TESTADOR_REPORT` staged => `E_TESTADOR_REPORT_NOT_STAGED`
* AR "✅ VERIFICADO" sem evidence do Executor staged => `E_SEAL_EVIDENCE_NOT_STAGED`

R-AR-4) Status válidos (canônicos):

* 🔲 PENDENTE
* 🏗️ EM_EXECUCAO
* ✅ SUCESSO (somente Testador)
* 🔴 REJEITADO (somente Testador)
* ⏸️ BLOQUEADO_INFRA (somente Testador/hb)
* 🔍 NEEDS_REVIEW (somente Humano)
* ✅ VERIFICADO (somente Humano)
* ❌ FALHA
* ⛔ SUPERSEDED

R-AR-5) Toda AR MUST ser materializada via `hb plan`. Criação manual proibida.

R-AR-6) Autoridade por status (regra dura)

* Arquiteto: 🔲 PENDENTE (via plano materializado)
* Executor: 🏗️ EM_EXECUCAO (via preenchimento de seção + hb report)
* Testador: ✅ SUCESSO / 🔴 REJEITADO / ⏸️ BLOQUEADO_INFRA (via hb verify)
* Humano: ✅ VERIFICADO / 🔍 NEEDS_REVIEW (manual)

## 9) Regras Anti-Alucinação (obrigatório)

R-AH-1) “source-inspection-only” é proibido como único gate para tasks de código.

R-AH-2) validation_command trivial é proibido (E_TRIVIAL_CMD).

R-AH-3) Testador MUST re-executar independentemente — nunca confiar no output do Executor.

R-AH-4) AH_DIVERGENCE:

* Executor exit 0 e Testador exit != 0 ⇒ 🔴 REJEITADO automático.

R-AH-5) ERROR_INFRA no Testador ⇒ ⏸️ BLOQUEADO_INFRA (não REJEITADO).

## 10) Nota de estabilidade de paths (Frontend)

Se existir diretório “Hb Track - Frontend”, ele é path real do repo.
Renomear diretório é mudança de governança/infra: somente por AR dedicada + evidência de migração controlada.
### 10.5) AUTO-COMMIT (OPCIONAL)

Agente `hb_autotest.py` suporta auto-commit opt-in após `hb seal` bem-sucedido:

* **Opt-in explícito**: variável de ambiente `HB_AUTO_COMMIT=1` (default: OFF)
* **Allowlist estrita por AR**: apenas arquivos autorizados podem ser commitados:
  * `docs/hbtrack/evidence/AR_<id>/`
  * `docs/hbtrack/ars/`
  * `_reports/testador/AR_<id>/`
  * `docs/hbtrack/_INDEX.md`
* **Abort on violation**: se qualquer staged file estiver FORA da allowlist, commit é abortado e erro detalhado é logado
* **Staged-only**: NUNCA usa `git add .` — commit apenas arquivos previamente staged
* **Mensagem padronizada**:
  ```
  feat(ar_<id>): <title> [VERIFICADO]
  
  Evidence: docs/hbtrack/evidence/AR_<id>/executor_main.log
  Report: _reports/testador/AR_<id>/TESTADOR_REPORT.md
  Protocol: v1.3.0
  Agent: hb_autotest v1.0.0 (auto-commit)
  ```
* **Função**: `auto_commit_if_enabled(repo_root, ar_id, title, dry_run)`
* **Segurança**: validação de allowlist acontece ANTES do commit — nenhum arquivo não-autorizado pode entrar no commit por erro
## 11) Fluxo Enterprise de 3 Agentes (binding)

Contratos canônicos por agente:

* Arquiteto: `docs/_canon/contratos/Arquiteto Contract.md`
* Executor: `docs/_canon/contratos/Executor Contract.md`
* Testador: `docs/_canon/contratos/Testador Contract.md`

Todos esses contratos MUST declarar compatibilidade com **PROTOCOL_VERSION v1.3.0**.

### Passo Final — SELO (hb_autotest automático ou Humano)
Após `hb verify` resultar em ✅ SUCESSO:

**Modo autônomo:** `hb_autotest.py` (daemon) executa `hb seal` automaticamente quando `triple_consistency=OK + executor_exit=0 + ah_flags=[]`. Não requer intervenção humana.

**Modo manual:** Humano executa:
- python scripts/run/hb_cli.py seal <AR_ID> "<reason opcional>"

Regras:
- `hb seal` é o único mecanismo autorizado a escrever **✅ VERIFICADO** (proibido edição manual direta).
- `hb seal` MUST falhar se evidence canônico não estiver staged ou se TESTADOR_REPORT não estiver staged.
- Kanban NÃO libera commit. Commit é liberado apenas por: AR + evidence canônico + TESTADOR_REPORT + _INDEX.md + ✅ VERIFICADO.
- Modo autônomo (`hb_autotest.py`) é equivalente ao modo manual para fins de governança.

B) docs/_canon/specs/GOVERNED_ROOTS.yaml precisa existir no repo (SSOT), porque o hb_cli vai ler de lá (I6).
C) docs/_canon/specs/Hb cli.md (ou “Hb cli Spec.md”) deve documentar as mudanças: plan.version==schema_version, evidence path fixo, hb seal, verify sem ✅ VERIFICADO, hash canônico.