# FASE 4 — PARIDADE4.md

# Analise estrutural definitiva: lacunas sistemicas que ainda nao viraram regra

Gerado em: 2026-04-02
Base: PARIDADE.md (Fase 1), PARIDADE2.md (Fase 2), PARIDADE3.md (Fase 3), GitHub Actions API (13 check runs, 7 SHAs, 14 workflow runs)

---

## DADOS COLETADOS DO GITHUB ACTIONS (api.github.com + MCP)

### Painel de check runs do commit do PR (sha=0d1066c3dd)

| Check Run | Conclusion |
|-----------|------------|
| Validate Contract Gates | **FAILURE** |
| Tests (CI) | **FAILURE** |
| Governance Tests | success |
| Architecture Drift Check | success |
| Adversarial Suite | success |
| Governance Enforcement (survival-suite) | success |
| Paridade Registry x Executor | success |
| Paridade Schema x Template x Skills | success |
| Validacao Cruzada SESSION_HANDOFF <-> session_start | success |
| Validate Contracts (CI) | success |
| Frontend Build + Tests | success |
| Docker Build Check | skipped (depende de Tests) |
| Detectar mudanca em governanca | success |

### Historico de todos os 7 SHAs da branch do PR

| SHA | Contract Gates | CI (Tests) | Padrao |
|-----|----------------|------------|--------|
| 8b9395c14c | FAIL (validator) | FAIL (pytest) | Ambos falham |
| 080b528703 | FAIL (validator) | FAIL (pytest) | Ambos falham |
| 4f9bc61e79 | FAIL (validator) | FAIL (pytest) | Ambos falham |
| 8b983990b2 | **SUCCESS** | FAIL (pytest) | Gates ok, testes quebram |
| ebdfed63f4 | **SUCCESS** | FAIL (pytest) | Gates ok, testes quebram |
| 004d927f70 | FAIL (ops drift) | FAIL (pytest) | Ambos falham |
| 0d1066c3dd | FAIL (ops drift) | FAIL (pytest) | Ambos falham |

**Fato critico**: O job `CI / Tests` falhou em TODOS os 7 commits, sempre no mesmo step (`Run tests (inclui schemathesis e pipeline_gates; exclui slow)`). Isso confirma que o bug JWT e a regressao de testes existem desde o primeiro commit da branch.

### Steps exatos de falha no Validate Contract Gates

- SHAs 8b9395c14c, 080b528703, 4f9bc61e79: Falha em `Validate contracts (warnings=failure B9-002)` — problema no validator
- SHAs 004d927f70, 0d1066c3dd: Falha em `Check ops contract derived artifacts` — drift de compiled_ops
- SHAs 8b983990b2, ebdfed63f4: SUCCESS completo — todos os steps passaram

Isso mostra que o drift de `compiled_ops/deploy/impact_report.json` e uma **regressao que apareceu nos commits mais recentes**, nao existia nos commits intermediarios. O validator foi corrigido nos commits intermediarios, mas os commits finais introduziram drift de artefato operacional.

### Annotations dos check runs falhos

- `Tests` (job 69733183702): `failure` annotation em `.github` line 168: "Process completed with exit code 1."
- `Validate Contract Gates` (job 69732998884): `failure` annotations: "Contract validation failed. Check the uploaded artifact for details." + "Process completed with exit code 2."

---

## PARTE 1 — Gaps e inconsistencias encontradas alem das fases 1-3

### GAP-1: `hb preflight` NAO cobre `CI / Tests`

O script `hb preflight` (scripts/hb, linhas 1234-1553) declara:

```
_CI_TEST_SUITES = [
    ("governance-tests", ...),
    ("adversarial-suite", ...),
    ("architecture-drift-checker", ...),
    ("architecture-drift-tests", ...),
    ("registry-executor-parity", ...),
    ("schema-template-skills-parity", ...),
    ("session-handoff-crossval", ...),
]
```

**Ausente**: `pytest -q -m "not slow" --tb=short` — que e exatamente o comando do job `CI / Tests` do GitHub. Este e o check que falha em 7/7 commits. O preflight cobre 7 suites de governanca e 3 compilers, mas ignora completamente o job de testes de aplicacao.

**Impacto**: O preflight pode dar PASS enquanto `CI / Tests` falha. Isso e exatamente o que aconteceu.

### GAP-2: `hb preflight` NAO cobre frontend (CI / Frontend Build + Tests)

O workflow `ci.yml` tem o job `build-frontend` que roda:
- `npm ci --legacy-peer-deps`
- `npx vitest run --reporter=verbose`
- `npm run test:pact`
- `npm run build`
- Docker build do frontend

Nenhum destes esta em `_CI_TEST_SUITES` do preflight.

### GAP-3: `hb preflight` NAO cobre Docker Build Check

O job `build` (Docker Build Check) no `ci.yml` depende de `test` e roda `docker build`. Nao existe equivalente local no preflight.

### GAP-4: Conftest.py usa DB_PORT=5433 por default, CI usa 5432

```python
# conftest.py linha 24
port = int(os.environ.get("DB_PORT", "5433"))
```

```yaml
# ci.yml job test env
DB_PORT: "5432"
```

Testes que dependem de Postgres podem ter comportamento diferente localmente. Isso e um falso-PASS local silencioso quando o Postgres local roda em 5433 e o CI espera 5432.

### GAP-5: Pre-commit hook usa `.venv/bin/python`, mas preflight usa `.venv-contract/bin/python`

O pre-commit hook (scripts/git-hooks/pre-commit) resolve:
```python
_venv_python = self.repo_root / ".venv" / "bin" / "python"
```

O preflight resolve via `_local_contract_python_candidates()`:
```python
self.local_contract_venv / "bin" / "python"  # .venv-contract
```

Isso cria dois ambientes Python diferentes validando coisas diferentes com dependencias potencialmente diferentes.

### GAP-6: Nenhum mecanismo impede commit de artefatos derivados stale

O pre-commit hook valida:
- Schema de session_start.json
- Stage exit codes
- Hash de artefatos staged vs session
- SESSION_HANDOFF.md
- validate_contracts --profile precommit
- Governance suites (se paths de governanca mudaram)

**Ausente**: Nao roda `compile_ops_contracts.py --check`, `compile_source_graph.py --all --check`, nem `compile_context_bundle.py --all --check`. Portanto, e perfeitamente possivel commitar artefatos derivados stale sem que o hook bloqueie.

### GAP-7: Nenhum mecanismo valida pytest completo antes de push

Nao existe pre-push hook. O `hb preflight` e manual e nao obrigatorio. O pre-commit hook nao roda `pytest -q -m "not slow"`. Portanto, regressions de aplicacao (como o bug JWT) passam pelo commit e pelo push sem deteccao local.

### GAP-8: test_backend_codegen_reports.py assume .venv-contract no runner

```python
# tests/pipeline_gates/test_backend_codegen_reports.py:12
PYTHON = REPO_ROOT / ".venv-contract" / "bin" / "python"
```

O job `CI / Tests` nao provisiona `.venv-contract`. Este teste e um falso FAIL remoto estrutural. Nao existe politica que detecte ou reprove testes acoplados a ambiente local.

### GAP-9: Dois testes de pipeline_gates verificam existencia de .venv-contract

- `test_dev_contract_env_script_exists.py` — verifica que `.venv-contract` existe
- `test_dev_contract_env_ps1_exists.py` — idem

Estes testes existem para validar que o ambiente de desenvolvimento esta configurado. Porem, se rodados no CI sem `.venv-contract`, falham. Eles deveriam OU ser marcados como `@pytest.mark.slow` (excluidos do CI), OU verificar condicialmente, OU estar fora do escopo de `pytest -q -m "not slow"`.

### GAP-10: contract-gates.yml usa Node 24, ci.yml usa Node 22

```yaml
# contract-gates.yml validate-contracts
node-version: "24"

# ci.yml validate
node-version: "22"
```

Ambos validam contratos com ferramentas Node (redocly, spectral, asyncapi), mas com versoes diferentes. Isso pode gerar divergencia entre `CI / Validate Contracts` e `Validate Contract Gates`.

### GAP-11: Dois validators rodando validate_contracts com profiles diferentes

- `ci.yml` / `Validate Contracts`: `--profile precommit`
- `contract-gates.yml` / `Validate Contract Gates`: sem flag explicita, mas com `CI=true` (cai em profile detectado automaticamente)

Dois jobs diferentes validando contratos com profiles potencialmente diferentes. Ambos sao required checks, mas podem divergir.

### GAP-12: Docker Build Check depende de Tests e fica skipped

No `ci.yml`:
```yaml
build:
  needs: test
```

Se Tests falha, Docker Build Check e skipped. Se este for um required check, ele nunca passa quando Tests falha. Se nao for required, e irrelevante para merge. De qualquer forma, a cadeia de dependencia mascarara falhas de Docker build enquanto Tests falhar.

---

## PARTE 2 — Respostas as perguntas estruturais

### P1: Qual arquivo/comando deve ser a fonte unica, executavel e obrigatoria dos checks de merge-readiness?

**Resposta**: Nenhum arquivo unico hoje cumpre esse papel. O mais proximo e `scripts/hb preflight`, mas ele tem gaps criticos (GAP-1, GAP-2, GAP-3).

**Regra necessaria**: Criar um unico arquivo de definicao de merge-readiness (proposta: `scripts/merge_readiness.yaml` ou equivalente embutido em `scripts/hb`) que:

1. Declare explicitamente TODOS os checks required da branch protection de `main`, mapeados 1:1 para comandos locais executaveis.
2. Seja consumido tanto pelo `hb preflight` quanto pelos workflows do GitHub (ou pelo menos verificavel contra eles).
3. A paridade entre este arquivo e os workflows do GitHub seja validada automaticamente por um teste de regressao.

```yaml
# Proposta de definicao canonica
merge_readiness_checks:
  - name: "Validate Contract Gates"
    local_command: |
      python3 scripts/compile/compile_source_graph.py --all --check
      python3 scripts/compile/compile_ops_contracts.py --check
      python3 scripts/compile/compile_context_bundle.py --all --check
      CI=true python3 scripts/validate_contracts.py
    github_workflow: contract-gates.yml
    github_job: validate-contracts
    required: true

  - name: "CI / Tests"
    local_command: |
      pytest -q -m "not slow" --tb=short
    github_workflow: ci.yml
    github_job: test
    required: true
    needs_services: [postgres, redis]

  - name: "Governance Tests"
    local_command: pytest tests/test_pipeline_governance.py -v
    github_workflow: contract-gates.yml
    github_job: governance-tests
    required: true

  - name: "Architecture Drift Check"
    local_command: |
      python3 scripts/audit/check_architecture_docs.py --json
      pytest tests/pipeline_gates/test_architecture_drift.py -v
    github_workflow: contract-gates.yml
    github_job: architecture-drift-check
    required: true

  - name: "CI / Validate Contracts"
    local_command: python3 scripts/contracts/validate/validate_contracts.py --profile precommit
    github_workflow: ci.yml
    github_job: validate
    required: true

  - name: "Frontend Build + Tests"
    local_command: |
      cd frontend && npm ci --legacy-peer-deps
      npx vitest run --reporter=verbose
      npm run test:pact
      npm run build
    github_workflow: ci.yml
    github_job: build-frontend
    required: false  # nao e required check hoje
```

### P2: Como tornar impossivel ou bloqueado qualquer PASS local baseado em artefatos nao commitados, cache local, .env, .venv-contract ou workspace sujo?

**Regras necessarias**:

1. **O preflight DEVE operar APENAS sobre o indice git (staged) ou sobre um stash isolado**, nunca sobre o workspace sujo. O `--strict` mode ja faz `git stash --keep-index`, mas:
   - Nao e o default. Deve ser o UNICO modo.
   - O modo sem --strict (que valida workspace sujo) deve ser removido ou renomeado para `hb lint` (sem pretensao de merge-readiness).

2. **O preflight DEVE desabilitar `.env`** durante a execucao:
   - Renomear `.env` -> `.env.bak` antes de rodar; restaurar depois.
   - Ou usar `env -i` com variaveis explicitas identicas ao CI.
   - Ou rodar dentro de container efemero.

3. **O preflight DEVE incluir compilers `--check`** (GAP-6 resolvido):
   - `compile_source_graph.py --all --check`
   - `compile_ops_contracts.py --check`
   - `compile_context_bundle.py --all --check`
   Ja existem no Step 5 do preflight. Mas o pre-commit hook NAO os roda. Adicionar ao hook ou criar pre-push hook obrigatorio.

4. **O pre-commit hook DEVE rodar compilers --check** para bloquear commit de artefatos derivados stale.

5. **Teste de regressao**: Um teste em `tests/pipeline_gates/` que verifica que `hb preflight` cobre todos os checks required da branch protection.

### P3: Qual e a definicao exata de "paridade local = GitHub"?

**Definicao**:

Paridade local = GitHub e verdadeira se e somente se TODAS as condicoes seguintes sao satisfeitas simultaneamente:

1. **Mesmo objeto**: O local valida exatamente o conteudo que sera enviado ao PR (indice git staged + commit), NAO o workspace sujo.
2. **Mesmo escopo**: O local executa os mesmos N comandos correspondentes aos N required checks da branch protection, sem omissoes e sem substituicoes por equivalentes mais fracos.
3. **Mesmo ambiente**: As variaveis de ambiente sao identicas ou funcionalmente equivalentes (mesmas portas, mesmos secrets dummy, mesmo `CI=true`).
4. **Mesmos services**: Se o CI provisiona Postgres e Redis, o local tambem provisiona Postgres e Redis com as mesmas configuracoes.
5. **Mesmos paths**: Se o CI nao tem `.venv-contract`, `.env`, `_reports/*` pre-existentes, o local tambem nao deve depender deles.
6. **Mesmo resultado**: Se o local da PASS, o GitHub DEVE dar PASS no mesmo SHA. Se divergir, a paridade esta quebrada.

**Condicoes minimas identicas**:
- `CI=true`
- `DB_PORT=5432` (nao 5433)
- Sem `.env` carregado
- Sem `.venv-contract` no PATH de resolucao de testes
- Postgres 16 e Redis 7 rodando
- Python 3.12.x
- Node 22 (para ci.yml) / Node 24 (para contract-gates.yml)
- `git config core.hooksPath scripts/git-hooks`

### P4: Quais testes, gates ou mecanismos automaticos devem existir para detectar regressao futura?

**Testes necessarios (novos)**:

1. **test_preflight_covers_all_required_checks.py**: Parsear `contract-gates.yml` e `ci.yml`, extrair jobs/steps required, comparar com `_CI_TEST_SUITES` e steps do preflight. FAIL se qualquer check required nao tiver equivalente local.

2. **test_no_venv_contract_dependency_in_ci_tests.py**: Varrer todos os arquivos em `tests/` e FAIL se algum hardcodar `.venv-contract` sem skip condicional.

3. **test_env_parity.py**: Comparar as env vars do job `test` em `ci.yml` com as env vars usadas pelo `conftest.py` defaults. FAIL se houver divergencia em portas, hosts ou flags.

4. **test_node_version_parity.py**: Extrair versoes de Node de todos os jobs dos dois workflows e FAIL se houver versoes inconsistentes sem justificativa documentada.

5. **test_compiler_check_in_precommit.py**: Verificar que o pre-commit hook roda compilers `--check`. FAIL se ausente.

**Gates necessarios (novos)**:

6. **PREFLIGHT_PARITY_GATE**: Executado no CI, verifica que a definicao do preflight local esta sincronizada com os workflows. Se divergir, o gate falha.

7. **STALE_ARTIFACT_GATE no pre-commit**: O hook DEVE rodar compilers `--check` antes de permitir commit.

### P5: Qual e o unico ritual local oficial de merge-readiness?

**Ritual unico**: `python3 scripts/hb preflight --strict`

**Regras para deslegitimar rituais mais fracos**:

1. O docstring do `hb survival-suite` DEVE declarar explicitamente: "Nao substitui `hb preflight`. Nao e merge-readiness."
2. O docstring do `hb stage3` DEVE declarar explicitamente que stage3 nao e validacao de merge.
3. O PR template DEVE exigir evidencia de `hb preflight --strict PASS` (exit code 0 + hash do output).
4. O validator `--profile precommit` DEVE declarar que e um subset do preflight, nao o preflight completo.
5. Qualquer documentacao que diga "roda X para validar antes de push" e que X != `hb preflight --strict` DEVE ser corrigida ou removida.

### P6: Qual politica deve reprovar testes que dependem de ambiente local nao provisionado pelo runner?

**Politica**:

1. **Regra**: Nenhum teste no escopo de `pytest -q -m "not slow"` pode depender de:
   - `.venv-contract/` existir como diretorio
   - `.env` existir
   - Diretorio `_reports/` com conteudo pre-existente que nao seja gerado pelo proprio teste
   - `node_modules/` instalados fora do step de setup
   - Qualquer path hard-coded que nao exista no checkout limpo do runner

2. **Enforcement**: Criar um teste de regressao `test_no_local_env_dependency.py` que:
   - Parseia todos os arquivos `.py` em `tests/`
   - Verifica se algum referencia `.venv-contract`, `.venv/`, `.env` sem um `pytest.mark.skipif` ou `pytest.importorskip` correspondente
   - FAIL se encontrar

3. **Correcao imediata necessaria**:
   - `test_backend_codegen_reports.py`: Alterar `PYTHON = REPO_ROOT / ".venv-contract" / "bin" / "python"` para resolver via `sys.executable` ou `shutil.which("python3")`.
   - `test_dev_contract_env_script_exists.py` e `test_dev_contract_env_ps1_exists.py`: Marcar como `@pytest.mark.slow` ou `@pytest.mark.skipif(os.environ.get("CI"), reason="local env only")`.

### P7: Como classificar formalmente falhas?

**Taxonomia formal**:

| Classe | Definicao | Evidencia minima | Responsavel |
|--------|-----------|------------------|-------------|
| **BUG_REAL** | Codigo de aplicacao que produz comportamento errado independente de ambiente | Reproducao em checkout limpo com env do CI; stack trace mostrando logica errada | Desenvolvedor |
| **DRIFT_ARTEFATO** | Artefato derivado commitado esta desincronizado com sua fonte de verdade | `compile_*_contracts.py --check` ou `compile_source_graph.py --all --check` retorna exit != 0 | Pipeline (compiler --check deve bloquear) |
| **PROBLEMA_TESTE** | Teste esta errado, acoplado a ambiente local ou order-dependent | Teste falha em checkout limpo sem depender de bug no codigo de aplicacao | Autor do teste |
| **DIVERGENCIA_AMBIENTE** | Resultado muda entre local e CI por causa de diferenca de env, path, service ou versao | Mesmo teste, mesmo codigo: PASS local, FAIL no CI (ou vice-versa), reproduzivel pela presenca/ausencia de env var ou service | Configuracao (ci.yml + conftest.py + .env) |
| **FALHA_PROCESSO** | O ritual local aprovou algo que o GitHub reprova, OU validou o objeto errado | O preflight deu PASS; o GitHub deu FAIL no mesmo SHA | Definicao do preflight / escopo local |

**Classificacao dos problemas atuais**:

| Problema | Classe |
|----------|--------|
| `AuthenticationError(message=...)` no middleware JWT | BUG_REAL |
| `compiled_ops/deploy/impact_report.json` stale | DRIFT_ARTEFATO |
| `test_backend_codegen_reports.py` hardcoda `.venv-contract` | PROBLEMA_TESTE |
| `test_dev_contract_env_*.py` falha no CI | PROBLEMA_TESTE |
| `DB_PORT=5433` local vs `5432` no CI | DIVERGENCIA_AMBIENTE |
| Node 22 vs Node 24 entre workflows | DIVERGENCIA_AMBIENTE |
| Preflight nao cobre `CI / Tests` | FALHA_PROCESSO |
| Pre-commit nao roda compilers --check | FALHA_PROCESSO |
| Workspace sujo com _reports/* e compiled_ops/* modificados | FALHA_PROCESSO |

### P8: Como garantir que o objeto validado localmente seja exatamente o SHA que sera enviado ao PR?

**Regra**:

1. `hb preflight --strict` DEVE ser o unico caminho. O modo `--strict` ja faz `git stash --keep-index`, o que isola o indice git. Porem:
   - **Tornar --strict obrigatorio** (renomear para default; remover modo sem strict).
   - Ou criar `hb preflight-commit` que: (a) faz um commit temporario para um ref local, (b) roda o preflight no worktree do commit temp, (c) apaga o ref temp.

2. **Pre-push hook** que verifica: "O ultimo commit local foi validado pelo preflight?" Mecanismo: o preflight grava um arquivo `_reports/preflight_last_pass.json` com `{"sha": "<commit-sha>", "timestamp": "...", "exit_code": 0}`. O pre-push hook compara o SHA do commit sendo pushado com o SHA do ultimo preflight PASS. Se nao bater, bloqueia.

3. **Alternativa forte**: Rodar o preflight dentro de `git worktree` temporario ou container baseado no checkout limpo do commit, identico ao que o runner do GitHub faz.

### P9: Como detectar e bloquear artefatos derivados stale antes do commit e antes do PR?

**Regra**:

1. **Pre-commit hook**: Adicionar chamada aos 3 compilers com `--check`:
   ```
   python3 scripts/compile/compile_source_graph.py --all --check
   python3 scripts/compile/compile_ops_contracts.py --check
   python3 scripts/compile/compile_context_bundle.py --all --check
   ```
   Se qualquer um falhar, o commit e bloqueado.

2. **Pre-push hook**: Idem, mas sobre o commit que esta sendo pushado (via worktree).

3. **CI dupla verificacao**: O workflow `contract-gates.yml` ja faz isso (steps `Check source graph derived artifacts`, `Check ops contract derived artifacts`, `Check compiled context bundles`). Manter como esta.

4. **Gate de regressao**: Teste em `tests/pipeline_gates/` que verifica que o pre-commit hook chama os 3 compilers. FAIL se ausente.

### P10: Qual deve ser o ambiente local limpo, reprodutivel e oficial de validacao?

**Opcoes**:

A. **Container efemero** (recomendado para paridade maxima):
   - Um `docker-compose.ci.yml` que levanta o mesmo ambiente do CI: Postgres 16, Redis 7, Python 3.12, Node 22.
   - Um script `scripts/hb ci-local` que: (1) faz checkout do indice para um temp dir, (2) sobe o container, (3) roda os checks dentro do container, (4) retorna exit code.
   - Vantagem: paridade maxima com o runner.
   - Desvantagem: mais lento, requer Docker.

B. **Script bootstrapado** (minimo viavel):
   - `scripts/bootstrap/merge_readiness_env.sh` que:
     1. Verifica `DB_PORT=5432`, Postgres e Redis ativos
     2. Desabilita `.env` (renomeia)
     3. Seta `CI=true` e todas as env vars do `ci.yml`
     4. Resolve Python para `.venv/bin/python` (nao `.venv-contract`)
     5. Roda `hb preflight --strict`
     6. Restaura `.env`

C. **Hibrido** (pragmatico):
   - Manter o preflight como esta, mas adicionar os checks faltantes (CI/Tests, compilers no hook).
   - Criar `scripts/hb ci-env` que configura as env vars identicas ao CI.
   - Criar `scripts/hb merge-ready` como alias para `CI=true hb preflight --strict` + `hb ci-env`.

### P11: Como garantir que nenhum comando local de "pronto para PR" rode escopo menor que os required checks?

**Regra**:

1. **Teste de paridade automatico**: `test_preflight_covers_required_checks.py` — parseia os required check names dos workflows e verifica que cada um tem equivalente no preflight. FAIL se estiver faltando.

2. **Enforcement no proprio preflight**: O preflight DEVE declarar, em codigo ou config, que cobre os checks X, Y, Z. Se a lista declarada divergir da lista do workflow, o teste de paridade falha.

3. **Nenhum outro comando pode afirmar merge-readiness**: O README, CLAUDE.md, copilot-instructions.md e PR template devem dizer explicitamente: "O unico comando de merge-readiness e `hb preflight --strict`."

### P12: Como validar que comandos/documentacao que afirmam reproduzir CI realmente o fazem?

**Regra**:

1. **Teste de invariante**: `test_preflight_ci_parity_claim.py`:
   - Parseia o docstring do `cmd_preflight` e verifica que cada claim ("63 gates", "7 test suites", "3 compilers") corresponde a realidade.
   - Parseia `_CI_TEST_SUITES` e verifica que cada suite corresponde a um job/step real dos workflows.
   - Se o preflight diz "reproduz todos os CI jobs" mas nao cobre `CI / Tests`, o teste FALHA.

2. **Gate de documentacao**: Se o docstring do preflight muda, o teste de paridade deve ser executado.

3. **Correcao imediata**: O docstring atual do `cmd_preflight` diz "Reproduzir todos os CI jobs localmente". Isso e FALSO hoje. Deve ser corrigido para "Reproduzir os gates de governanca e compilers. Para paridade completa com CI, use `hb merge-ready`." — OU o preflight deve ser expandido para realmente cobrir tudo.

### P13: Quais evidencias minimas o sistema deve registrar em toda validacao local e remota?

**Registro obrigatorio**:

```json
{
  "type": "preflight_report",
  "sha": "<git commit sha que foi validado>",
  "timestamp": "ISO8601",
  "workspace_clean": true,
  "env_vars_hash": "<hash das env vars usadas>",
  "checks_executed": [
    {"name": "...", "exit_code": 0, "duration_s": 12.3},
  ],
  "checks_required": ["Validate Contract Gates", "CI / Tests", ...],
  "checks_missing": [],
  "python_version": "3.12.x",
  "node_version": "22.x",
  "services": {"postgres": "16", "redis": "7"},
  "result": "PASS" | "FAIL",
  "report_path": "_reports/preflight/latest.json"
}
```

**Local**: Gravado em `_reports/preflight/latest.json` pelo preflight.
**Remoto**: Ja existe `_reports/contract_gates/latest.json` (upload como artifact). Expandir para incluir os campos acima.

### P14: Quais estados implicitos locais devem ser proibidos ou neutralizados?

| Estado implicito | Risco | Neutralizacao |
|------------------|-------|---------------|
| `.env` presente | Variaveis de ambiente diferentes do CI | Preflight DEVE renomear ou ignorar `.env` durante execucao |
| `.venv-contract/` presente | Testes assumem path local | Testes NAO devem hardcodar; resolver via `sys.executable` |
| `_reports/*` pre-existentes com dados stale | Testes leem relatorios pre-existentes em vez de gera-los | Preflight DEVE limpar `_reports/` ou rodar em worktree limpo |
| `compiled_ops/*` regenerado mas nao commitado | Compilers `--check` passam localmente, falham no CI | Pre-commit hook DEVE rodar compilers `--check` |
| `node_modules/` com versoes divergentes | Ferramentas Node com comportamento diferente | Preflight DEVE verificar `npm ls` vs `package-lock.json` |
| Postgres em porta 5433 | Testes conectam em porta diferente do CI | Preflight DEVE verificar e exigir porta 5432 ou setar `DB_PORT=5432` |
| `DB_NAME` diferente | Migracao cria tables em banco diferente | Preflight DEVE setar `DB_NAME=hbtrack_test` |
| `.venv/` com pacotes extras | Imports que funcionam local mas falham no CI | Nao e critico se o CI instala requirements explicitos |

### P15: Quais regras permanentes de governanca devem existir?

**Regras que devem ser convertidas em enforcement executavel**:

| # | Regra | Enforcement |
|---|-------|-------------|
| R1 | O preflight DEVE cobrir 100% dos required checks | Teste automatico `test_preflight_covers_required_checks.py` |
| R2 | Nenhum teste em escopo `not slow` pode depender de `.venv-contract` | Teste automatico `test_no_local_env_dependency.py` |
| R3 | Artefatos derivados DEVEM ser verificados no pre-commit | Compilers `--check` no hook |
| R4 | O preflight DEVE rodar sobre indice git, nao workspace sujo | `--strict` como default ou unico modo |
| R5 | `.env` DEVE ser neutralizado durante preflight | Renomear ou `env -i` |
| R6 | Todos os workflows DEVEM usar a mesma versao de Node | Ou justificar divergencia documentada |
| R7 | Pre-push hook DEVE verificar SHA do ultimo preflight PASS | Hook + `_reports/preflight/latest.json` |
| R8 | Nenhum comando pode afirmar "reproduz CI" sem ser verificavel | Teste de invariante de claims |
| R9 | Bug JWT DEVE ser corrigido antes de qualquer push | Fix de `AuthenticationError(message=...)` para `AuthenticationError()` |
| R10 | `DB_PORT` default local DEVE ser 5432, nao 5433 | Alterar conftest.py default |

---

## PARTE 3 — Perguntas que nao foram feitas mas sao criticas

### Q1: Os required checks da branch protection estao corretos e completos?

**Diagnostico**: Nao foi possivel obter a branch protection via API sem autenticacao. Porem, pela observacao dos check runs, os 5 required checks declarados nos documentos sao:
1. Validate Contract Gates
2. Governance Tests
3. Architecture Drift Check
4. CI / Validate Contracts
5. CI / Tests

**Lacuna critica**: `Frontend Build + Tests` NAO e required check. Isso significa que o frontend pode quebrar sem bloquear merge. Se o frontend faz parte do produto, isso e um gap de cobertura. `Docker Build Check` tambem nao e required (e depende de Tests, entao fica skipped quando Tests falha).

**Recomendacao**: Avaliar se `Frontend Build + Tests` deve ser adicionado como required check. Se o frontend e parte critica do deploy, a resposta e sim.

### Q2: O que acontece quando um job condicional (governance) NAO roda porque os paths nao mudaram?

Os jobs `governance-enforcement`, `registry-executor-parity`, `schema-template-skills-parity` e `session-handoff-crossval` sao condicionais (`if: needs.detect-governance-change.outputs.governance_changed == 'true'`).

Se NENHUM deles e required check, isso e correto. Se algum for required, ele ficara "pending" eternamente quando o PR nao tocar paths de governanca, e o PR NUNCA podera ser mergeado.

**Verificacao necessaria**: Confirmar que nenhum job condicional e required check. Se for, mudar para always-run ou remover de required.

### Q3: O Copilot code review e o Copilot coding agent afetam merge?

Existem dois workflows dinamicos:
- `Copilot code review`
- `Copilot coding agent`

Se algum deles gerar check runs que bloqueiam merge, isso precisa ser mapeado. Se nao bloqueiam, sao irrelevantes para paridade.

### Q4: O que acontece se validate_contracts.py muda de comportamento entre profiles?

Hoje:
- `ci.yml` usa `--profile precommit`
- `contract-gates.yml` usa `CI=true` sem `--profile` explicito

Se o validator detecta `CI=true` e auto-seleciona um profile mais estrito, o resultado pode divergir do local que roda `--profile precommit`. Isso e uma bomba-relogio de paridade.

**Recomendacao**: Ambos os workflows devem usar o MESMO profile explicito. Nenhum deve depender de auto-deteccao.

### Q5: Quem garante que o `SESSION_HANDOFF.md` do checkout do CI e valido?

Ambos os workflows fazem:
```yaml
- name: Sincronizar branch_ativo no SESSION_HANDOFF
  run: |
    CURRENT="${{ github.head_ref || github.ref_name }}"
    sed -i "s|^branch_ativo:.*|branch_ativo: ${CURRENT}|" SESSION_HANDOFF.md
```

Isso MODIFICA o checkout do CI antes de rodar os gates. Se algum gate valida o `SESSION_HANDOFF.md`, ele esta validando uma versao DIFERENTE do que esta commitado. Isso e uma fonte potencial de falso PASS remoto.

### Q6: Existe um mecanismo de rollback quando o preflight falha?

O `--strict` mode faz `git stash --keep-index` e depois `git stash pop`. Se o preflight crashar (kill, OOM, timeout), o stash fica pendurado e o workspace fica em estado inconsistente. Nao existe trap/cleanup.

**Recomendacao**: Adicionar `trap` ou `try/finally` para garantir que o stash e restaurado mesmo em caso de crash.

### Q7: O que acontece quando tests/pipeline_gates/ cresce e o escopo de `pytest -q -m "not slow"` muda silenciosamente?

O comando do CI e `pytest -q -m "not slow" --tb=short`. Qualquer novo teste adicionado sem `@pytest.mark.slow` sera automaticamente incluido. Se esse teste depender de .venv-contract ou Postgres local, ele quebra o CI silenciosamente.

**Recomendacao**: Um teste de regressao que verifica que nenhum teste coletado por `pytest -q -m "not slow" --collect-only` depende de estado local nao garantido pelo CI.

### Q8: Existe monitoramento de tendencia das falhas de CI ao longo do tempo?

A API mostra 262 workflow runs totais. Os 7 SHAs da branch do PR falharam 7/7 vezes em CI/Tests. Nao existe dashboard ou alerta que detecte "CI/Tests falhou N vezes consecutivas na mesma branch".

**Recomendacao**: Adicionar alerta quando o mesmo job falha > 3 vezes consecutivas na mesma branch. Isso teria detectado o problema muito mais cedo.

---

## PARTE 4 — Falsos positivos e inconsistencias nos documentos PARIDADE 1-3

### Inconsistencia 1: PARIDADE2.md afirma que a hipotese de mutacao de `latest.json` foi "enfraquecida"

A hipotese H7/H8 sobre `_reports/contract_gates/latest.json` sendo reescrito durante a suite foi classificada como "enfraquecida" na Fase 2. Porem, o mecanismo de contaminacao existe: o validator reescreve `latest.json` em cada execucao (profiles `ci` e `local`). Se algum teste roda o validator internamente, `latest.json` muda. O experimento controlado que "nao mudou o hash" pode ter sido insuficiente.

**Status real**: Nao refutada, apenas nao reproduzida em um cenario especifico. O risco permanece.

### Inconsistencia 2: PARIDADE3.md diz "dois primeiros testes que quebram no suite amplo"

O documento cita posicoes 44 e 45 na coleta do pytest. Porem, com `pytest -q -m "not slow"` (e nao `pytest -q` sem marker filter), a coleta pode ser diferente. A posicao exata depende do marker filter e da ordem de coleta.

**Status real**: A ordem de falha pode nao ser exatamente nas posicoes citadas. O que esta confirmado e que o cluster JWT falha; a posicao exata depende do ambiente.

### Inconsistencia 3: Todas as fases mencionam "obter logs brutos do GitHub" como lacuna

Os logs brutos dos jobs nao foram obtidos em nenhuma fase. A API publica retorna apenas annotations (que sao genericas: "Process completed with exit code 1"). Os logs detalhados requerem autenticacao, e agora `gh` ESTA autenticado.

**Status real**: Com `gh` autenticado, os logs PODEM ser obtidos agora. Isso deveria fechar a lacuna.

---

## PARTE 5 — Plano de acao ordenado por impacto

### Prioridade 1 (bloqueia merge imediatamente)
1. **Corrigir bug JWT**: Em `src/identity_access/middleware.py`, substituir `AuthenticationError(message=...)` por `AuthenticationError()` (BUG_REAL).
2. **Regenerar e commitar artefatos derivados**: `python3 scripts/compile/compile_ops_contracts.py` e commitar `compiled_ops/deploy/impact_report.json` (DRIFT_ARTEFATO).
3. **Corrigir test_backend_codegen_reports.py**: Substituir `.venv-contract` por `sys.executable` (PROBLEMA_TESTE).
4. **Marcar testes de .venv-contract como slow**: `test_dev_contract_env_script_exists.py` e `test_dev_contract_env_ps1_exists.py` (PROBLEMA_TESTE).

### Prioridade 2 (impede recorrencia)
5. **Expandir `hb preflight`** para incluir `pytest -q -m "not slow" --tb=short` (FALHA_PROCESSO).
6. **Adicionar compilers `--check` ao pre-commit hook** (FALHA_PROCESSO).
7. **Corrigir `DB_PORT` default** em `conftest.py` de 5433 para 5432 (DIVERGENCIA_AMBIENTE).

### Prioridade 3 (governanca permanente)
8. Criar teste `test_preflight_covers_required_checks.py`.
9. Criar teste `test_no_local_env_dependency.py`.
10. Unificar versao de Node entre workflows (22 ou 24, nao ambos).
11. Unificar profile do validator entre `ci.yml` e `contract-gates.yml`.
12. Criar pre-push hook que verifica SHA do ultimo preflight PASS.
13. Corrigir docstring do preflight para nao afirmar cobertura que nao existe.
14. Criar `_reports/preflight/latest.json` com evidencia auditavel.
15. Avaliar se `Frontend Build + Tests` deve ser required check.
