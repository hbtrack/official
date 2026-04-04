# PARTE 1 - Resumo executivo da descoberta inicial

Em 2026-04-02, o PR `#30` (`head_sha=0d1066c3ddad79887ff22f3f06a84c4078172af5`) falhou em dois checks que realmente bloqueiam merge na branch `main`:

- `Validate Contract Gates`
- `CI / Tests`

Fatos confirmados nesta fase:

- A branch protection de `main` exige 5 status checks: `Validate Contract Gates`, `Governance Tests`, `Architecture Drift Check`, `CI / Validate Contracts` e `CI / Tests`.
- No commit do PR, `Governance Tests`, `Architecture Drift Check` e `CI / Validate Contracts` passaram.
- No commit do PR, `Validate Contract Gates` falhou no passo `Check ops contract derived artifacts`.
- Essa falha foi reproduzida localmente em checkout limpo do mesmo commit: `scripts/compile/compile_ops_contracts.py --check` falha com drift em `compiled_ops/deploy/impact_report.json`.
- O workspace local atual nao esta limpo: ha modificacoes nao commitadas em `compiled_ops/deploy/impact_report.json` e em varios `_reports/*`.
- No workspace local atual, o mesmo comando `scripts/compile/compile_ops_contracts.py --check` passa.
- O teste `tests/pipeline_gates/test_ops_contract_compiler.py` passa no workspace atual e falha no checkout limpo do commit do PR.
- O arquivo `src/identity_access/middleware.py` contem um bug de runtime em `AuthenticationError(message=...)`; testes unitarios do modulo falham no workspace atual e tambem em reproducao tipo-CI.

Familias de causa hoje mais provaveis:

1. Divergencia entre workspace local e commit publicado.
   O caso mais forte ja confirmado e o drift de `compiled_ops/deploy/impact_report.json`: local atual passa porque o arquivo foi regenerado, mas o commit enviado ao GitHub ainda esta stale.

2. Divergencia de escopo entre o que esta sendo validado localmente e o que o GitHub realmente exige.
   O PR declara validacao local com `hb survival-suite`, `validate_contracts --profile ci`, suites pontuais e `pre-commit`, mas o GitHub tambem roda `compile_ops_contracts --check`, `pytest -q -m "not slow" --tb=short`, suites condicionais de governanca e, em outro job, frontend build/tests.

3. Divergencias de ambiente/path no job `CI / Tests`.
   Ha testes que assumem `REPO_ROOT/.venv-contract/bin/python`. Isso existe no workspace local atual, mas nao existe no checkout limpo do PR nem no job `CI / Tests` do GitHub. Esse caso foi reproduzido em `tests/pipeline_gates/test_backend_codegen_reports.py`.

4. Pelo menos um bug real do codigo publicado, nao apenas "GitHub diferente do local".
   O conjunto de falhas em `src/identity_access/tests/unit/test_jwt_auth_failure_handling.py` e os 500s em Schemathesis apontam para regressao real na camada de autenticacao JWT. Isso explica parte do `CI / Tests` falhando mesmo sem depender de cache ou runner exotico.

Lacuna critica que permaneceu:

- Nao foi possivel obter os logs brutos do GitHub Actions com `gh`, porque o token local do `gh` esta invalido.
- Tambem nao foi possivel baixar o artifact `contract-gates-report` sem autenticacao.
- Portanto, a confirmacao do stdout/stderr exato do GitHub foi substituida por API publica + reproducao local controlada.


# PARTE 2 - Mapa dos checks/gates

Observacao:

- Workflows GitHub-only existentes mas fora do escopo deste PR: `Context Efficiency Audit`, `Domain Completeness Audit` e `HB Track - Deploy Pipeline`.
- O PR atual disparou apenas `CI` e `Contract Gates`.
- Como o PR tocou arquivos de governanca, os jobs condicionais de governanca tambem rodaram.

| Gate/check | Onde roda localmente | Onde roda no GitHub | Mesmo comando? | Mesmo escopo? | Suspeita de divergencia |
|------------|----------------------|---------------------|----------------|---------------|-------------------------|
| `python3 scripts/validate_contracts.py` (default local) | Manual, README, shell local | Nao ha equivalente exato | Nao | Nao | Alta: local default cai em `profile=local`; GitHub usa `profile=precommit` ou `profile=ci` |
| `pre-commit` hook | `scripts/git-hooks/pre-commit` | Nao como hook; ha job parcial equivalente em `CI / Validate Contracts` | Parcialmente | Nao | Media: hook avalia staged/dirty workspace, hashes de artefatos e `SESSION_HANDOFF`; GitHub avalia checkout limpo |
| `hb preflight` | `scripts/hb preflight` | Nao ha job remoto com esse nome | Nao | Nao | Alta: o comando afirma reproduzir "todos os CI jobs", mas o codigo nao cobre `CI / Tests`, frontend nem Docker build |
| `Detectar mudanca em governanca` | Nao ha equivalente local explicito | `Contract Gates / detect-governance-change` | Nao | Nao | Baixa: helper de path filter; no PR atual foi `success` e habilitou jobs condicionais |
| `Validate Contract Gates` (required) | Manual ou via partes de `hb preflight` | `Contract Gates / validate-contracts` | Sim, se rodar compilers + `validate_contracts --profile ci` manualmente | Nao | Alta: falha remota reproduzida localmente em checkout limpo por drift de `compiled_ops/deploy/impact_report.json` |
| `Governance Tests` (required) | Manual ou `hb preflight` | `Contract Gates / governance-tests` | Sim | Quase | Baixa: passou remoto |
| `Adversarial Suite` | Manual ou `hb preflight` | `Contract Gates / adversarial-suite` | Sim | Quase | Baixa: passou remoto |
| `Architecture Drift Check` (required) | Manual ou `hb preflight` | `Contract Gates / architecture-drift-check` | Sim | Quase | Baixa: passou remoto |
| `Governance Enforcement (survival-suite)` | `python3 scripts/hb survival-suite` | `Contract Gates / governance-enforcement` | Sim | Nao completamente | Media: local tende a rodar sobre workspace atual; remoto roda em checkout limpo com `CI=true` e path filter |
| `Paridade Registry x Executor` | Manual ou `hb preflight` | `Contract Gates / registry-executor-parity` | Sim | Quase | Baixa: passou remoto |
| `Paridade Schema x Template x Skills` | Manual ou `hb preflight` | `Contract Gates / schema-template-skills-parity` | Sim | Quase | Baixa: passou remoto |
| `Validação Cruzada SESSION_HANDOFF <-> session_start` | Manual; hook local roda variante com `-m not slow` | `Contract Gates / session-handoff-crossval` | Parcialmente | Nao | Media: local hook usa selecao diferente; remoto roda suite completa `-v` |
| `CI / Validate Contracts` (required) | Manual com `python3 scripts/contracts/validate/validate_contracts.py --profile precommit` | `CI / validate` | Sim | Nao | Media: mesmo comando principal, mas ambiente e deps diferem; mesmo assim esse check passou remoto |
| `CI / Tests` (required) | Manual com `pytest -q -m "not slow" --tb=short` | `CI / test` | Sim | Nao | Alta: job remoto usa Postgres/Redis limpos, env explicito, checkout limpo; local declarado no PR nao mostra execucao desse comando completo |
| `Frontend Build + Tests` | Manual em `frontend/` | `CI / build-frontend` | Sim, se o usuario rodar os mesmos passos em `frontend/` | Nao necessariamente | Baixa no caso atual: remoto passou; ainda assim bootstrap local nao cobre frontend |
| `Docker Build Check` | Manual | `CI / build` | Sim, se o usuario rodar build docker equivalente | Nao necessariamente | Baixa no caso atual: ficou `skipped` porque `CI / Tests` falhou antes |


# PARTE 3 - Hipoteses iniciais

| ID | Hipotese | Evidencia a favor | Evidencia contra | Nivel de plausibilidade |
|----|----------|-------------------|------------------|-------------------------|
| H1 | O local esta validando sobre um workspace diferente do commit publicado, com artefatos derivados nao commitados | `git status` mostra `_reports/*` e `compiled_ops/deploy/impact_report.json` modificados; no workspace atual `compile_ops_contracts --check` passa; no checkout limpo do commit do PR o mesmo comando falha; `test_ops_contract_compiler.py` passa local atual e falha no checkout limpo | Nao explica sozinho os failures de JWT/auth | alta |
| H2 | O escopo da validacao local e mais estreito que o escopo dos checks exigidos pelo GitHub | O PR declara validacao local sem `pytest -q -m "not slow"` nem jobs frontend/docker; branch protection exige `Validate Contract Gates` e `CI / Tests`; `scripts/validate_contracts.py` sem `--profile` roda `local`, nao `ci` | Se o usuario tiver rodado exatamente todos os comandos do CI fora do PR body, essa hipotese perde forca | alta |
| H3 | Existe drift real de artefato operacional derivado no commit do PR | `Validate Contract Gates` falha em `Check ops contract derived artifacts`; reproducao local limpa mostra diff exato: `compiled_ops/deploy/impact_report.json` ainda lista `.github/workflows/deploy.yml` em `upstream_operational_inputs`, mas `docs/_canon/SYNC_MANIFEST.yaml` nao lista mais esse input | Nao cobre outras falhas do job `CI / Tests` | alta |
| H4 | Alguns testes passam localmente so porque dependem de `REPO_ROOT/.venv-contract`, que existe localmente mas nao existe no checkout do GitHub | `tests/pipeline_gates/test_backend_codegen_reports.py` usa caminho hard-coded `REPO_ROOT/.venv-contract/bin/python`; esse teste passa no workspace atual e falha no checkout limpo | Afeta um subconjunto especifico de testes, nao o `Validate Contract Gates` | alta |
| H5 | Ha um bug real de autenticacao JWT no codigo publicado, e o GitHub o encontra porque roda o job `CI / Tests` completo | `src/identity_access/tests/unit/test_jwt_auth_failure_handling.py` falha no workspace atual; erro objetivo em `AuthenticationError(message=...)`; reproducao tipo-CI mostrou 500s em Schemathesis e em testes de JWT | Isto nao e "divergencia de ambiente" pura; e regressao real combinada com falta de paridade de escopo local | alta |
| H6 | Diferencas de env local vs GitHub influenciam comportamento dos testes | `.env` existe so no workspace local; `config/settings.py` carrega `.env`; defaults locais usam `DB_PORT=5433`; o job `CI / Tests` usa env explicito, `DB_PORT=5432`, Postgres e Redis limpos | As falhas de JWT reproduzem tambem no local atual, entao nem tudo depende de env | media |
| H7 | O suite `hb preflight` gera falsa sensacao de paridade com o CI | O proprio help/comentario de `hb preflight` fala em reproduzir todos os CI jobs, mas o codigo cobre so contract-gates/governanca/compilers; nao cobre `CI / Tests`, frontend nem Docker builds | Nao ha prova de que o usuario efetivamente confiou nele nesta rodada | media |
| H8 | Existem testes order-dependent que leem `_reports/contract_gates/latest.json` mutavel, e isso muda o resultado do suite completo | `tests/pipeline_gates/test_warning_free_acceptance.py` e `tests/test_video_module.py::test_contract_gates_pass` passam isolados, mas falharam no final do suite completo quando `latest.json` estava `FAIL` | O teste exato que reescreve `latest.json` durante a suite ainda nao foi isolado | media |
| H9 | Diferencas de OS/Node/npm/caches sao a causa principal | Ha diferencas: local `WSL2 + Node 24.14.1 + npm 11.11.0`; workflows usam `ubuntu-22.04` e `ubuntu-latest`, com Node 22 em um workflow e 24 em outro | As falhas principais foram reproduzidas sem depender dessas diferencas; frontend passou | baixa |
| H10 | Cache/artifact stale do GitHub esta produzindo falso negativo remoto | Nao houve evidencia concreta dessa classe; o primeiro check remoto falhou por drift que tambem apareceu em reproducao local limpa | O problema ja foi reproduzido fora do GitHub em checkout limpo | baixa |


# PARTE 4 - Lacunas de investigacao

- Falta o log bruto do job `Validate Contract Gates` no GitHub (`run 23911091008`, `job 69732998884`).
- Falta o log bruto do job `CI / Tests` no GitHub (`run 23911090996`, `job 69733183702`).
- Falta o conteudo do artifact `contract-gates-report` (`artifact 6246095640`), que exigiu autenticacao para download.
- Falta a lista exata dos comandos que voce rodou localmente quando concluiu que "localmente passa". O que existe hoje e:
  - comandos declarados no PR
  - superficies de validacao definidas pelo repositorio
  - reproducoes feitas por mim
- Falta isolar qual teste ou grupo de testes reescreve `_reports/contract_gates/latest.json` durante a suite completa.
- Falta distinguir, dentro do `CI / Tests`, quais falhas do suite completo do PR atual batem exatamente com o job real do GitHub e quais foram agravadas pela reproducao local em worktree temporario.
- Falta medir se a presenca de `.env` local altera o comportamento de testes especificos alem do que ja foi confirmado por leitura de codigo.
- Falta verificar o npm exato e outras versoes efetivas do runner GitHub, embora hoje isso pareca secundario.


# PARTE 5 - Direcao da fase 2

1. Obter logs e artifacts reais do GitHub Actions.
   Reautenticar `gh` e coletar:
   - `gh run view 23911091008 --log`
   - `gh run view 23911090996 --log`
   - artifact `contract-gates-report`
   Sem isso, segue faltando o stdout/stderr oficial do GitHub.

2. Fechar a diferenca entre workspace local e commit publicado.
   Comparar sistematicamente `HEAD` do PR com o workspace atual e classificar cada mudanca nao commitada em:
   - artefato derivado que altera gate remoto
   - relatorio local apenas informativo
   O caso ja confirmado para aprofundar primeiro e `compiled_ops/deploy/impact_report.json`.

3. Reproduzir `CI / Tests` em checkout limpo com dois cenarios controlados.
   - Cenario A: sem `.venv-contract` no repo, como o job atual do GitHub.
   - Cenario B: com `.venv-contract` bootstrapado no checkout limpo.
   Isso separa bugs reais de caminho/ambiente.

4. Isolar o cluster de falhas de JWT/auth.
   Rodar primeiro:
   - `src/identity_access/tests/unit/test_jwt_auth_failure_handling.py`
   - `tests/test_fase1_validation.py::TestJWT401`
   - subset minimo de Schemathesis que toca `/api/users`, `/api/teams`, `/api/auth/me`
   Objetivo: provar quanto do `CI / Tests` e cascata da mesma regressao.

5. Isolar quem muta `_reports/contract_gates/latest.json` durante a suite.
   Medir hash do arquivo antes/depois de cada teste suspeito que:
   - chama `validate_contracts.py`
   - chama `hb stage3`
   - depende de `latest.json`
   Essa trilha precisa ser fechada para eliminar falhas order-dependent.

6. Revisar a paridade declarada versus a paridade real das superficies locais.
   Conferir especificamente:
   - `scripts/validate_contracts.py` default local versus perfis remotos
   - `hb preflight` versus os jobs reais de PR
   - `pre-commit` versus checkout limpo do CI
   O objetivo da fase 2 nao e "escolher um gate favorito", e sim definir exatamente qual superficie local deve espelhar cada check remoto.

7. Confirmar o ritual local que estava sendo usado antes do push.
   Se houver historico de shell confiavel ou se voce informar a sequencia exata, comparar cada comando local com os 5 checks exigidos pela branch protection.

