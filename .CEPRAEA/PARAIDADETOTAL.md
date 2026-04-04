# FASE 1 -- PARIDADE.md

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
| `Validacao Cruzada SESSION_HANDOFF <-> session_start` | Manual; hook local roda variante com `-m not slow` | `Contract Gates / session-handoff-crossval` | Parcialmente | Nao | Media: local hook usa selecao diferente; remoto roda suite completa `-v` |
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


# FASE 2 -- PARIDADE2.md

PARTE 1 -- O que foi confirmado nesta fase

- O branch `main` exige hoje 5 status checks required: `Validate Contract Gates`, `Governance Tests`, `Architecture Drift Check`, `CI / Validate Contracts` e `CI / Tests`.
- No PR `#30`, as falhas com evidencia mais forte continuam concentradas em `Validate Contract Gates` e `CI / Tests`.
- `Validate Contract Gates` falha por drift real do arquivo `compiled_ops/deploy/impact_report.json`. Em checkout limpo do commit `0d1066c3ddad79887ff22f3f06a84c4078172af5`, `python3 scripts/compile/compile_ops_contracts.py --check` reprova; no workspace atual o mesmo comando passa porque o artefato local ja esta regenerado e nao commitado.
- A cadeia causal do drift foi confirmada: `docs/_canon/SYNC_MANIFEST.yaml` nao trata mais `.github/workflows/deploy.yml` como `source_input` de `OPS_SOURCE_GRAPH_SYNC`, mas o `compiled_ops/deploy/impact_report.json` publicado no PR ainda carrega esse arquivo como input upstream.
- O fluxo local declarado no proprio PR nao cobre a mesma superficie dos required checks do GitHub. A validacao reportada no PR cita `python3 scripts/hb survival-suite`, `./.venv-contract/bin/python scripts/contracts/validate/validate_contracts.py --profile ci`, suites direcionadas e hook local; nao cita `pytest -q -m "not slow" --tb=short`, frontend tests/build nem `compile_ops_contracts.py --check`.
- `scripts/hb preflight` nao reproduz todos os jobs do GitHub apesar de afirmar isso no texto do comando. Ele cobre `validate_contracts --profile ci`, 3 compilers e 7 suites de governanca/paridade, mas nao executa o job `CI / Tests` completo, nem frontend tests, Pact ou Docker builds.
- `tests/pipeline_gates/test_backend_codegen_reports.py` depende explicitamente de `REPO_ROOT/.venv-contract/bin/python`. Em checkout limpo sem `.venv-contract` local ao repo, esse teste falha; ao inserir manualmente esse path via symlink, ele passa. Isso confirma divergencia estrutural de ambiente/path entre repo local e runner limpo.
- `src/identity_access/tests/unit/test_jwt_auth_failure_handling.py` falha tanto no workspace atual quanto em checkout limpo. A causa reproduzida e `AuthenticationError(message=...)` em `src/identity_access/middleware.py`, enquanto a classe instalada nao aceita esse keyword argument. Portanto, essa falha nao e "misterio do GitHub"; e regressao real do codigo que o GitHub esta executando.
- A hipotese de mutacao espontanea de `_reports/contract_gates/latest.json` perdeu forca nesta fase. Em experimento controlado no checkout limpo, a sequencia `test_runtime_promotions.py -> test_warning_free_acceptance.py -> test_video_module.py::TestVideoModuleIntegration::test_contract_gates_pass` preservou o hash de `latest.json` e todos os 17 testes passaram.

PARTE 2 -- Hipoteses refinadas

| ID | Hipotese refinada | Status | Evidencia principal | Impacto no problema |
|----|-------------------|--------|---------------------|---------------------|
| H1 | O PR publicou `compiled_ops/deploy/impact_report.json` stale, enquanto o workspace local ja tinha a versao regenerada | confirmada | `compile_ops_contracts.py --check` falha no checkout limpo do SHA do PR e passa no workspace atual; copiar o artefato local regenerado para o checkout limpo faz `test_ops_contract_compiler.py` voltar a passar | Explica diretamente a falha de `Validate Contract Gates` e o falso PASS local |
| H2 | O ritual local de validacao e mais fraco que os required checks do GitHub | confirmada | O corpo do PR lista apenas `survival-suite`, validator, suites direcionadas e hook; os workflows required rodam tambem `pytest -q -m "not slow"`, compilers `--check`, e ha jobs separados por gate | Explica por que o local aprova sem cobrir as mesmas superficies que o GitHub reprova |
| H3 | Parte do `CI / Tests` depende indevidamente de `.venv-contract` dentro do repo | confirmada | `tests/pipeline_gates/test_backend_codegen_reports.py` usa `REPO_ROOT/.venv-contract/bin/python`; falha em checkout limpo sem esse path e passa imediatamente quando o path e injetado | Explica falha remota que o repo local pode mascarar por estado preexistente |
| H4 | Ha regressao real no middleware JWT/autenticacao, independente de ambiente | confirmada | `src/identity_access/tests/unit/test_jwt_auth_failure_handling.py` falha localmente e em checkout limpo com `TypeError: AuthenticationError() takes no keyword arguments` | Explica parte substantiva de `CI / Tests`, inclusive cascata de 500s em testes HTTP/Schemathesis |
| H5 | Diferencas de `.env`, services e vars entre local e GitHub alteram comportamento do backend | fortalecida | `config/settings.py` carrega `.env` local automaticamente; o GitHub injeta vars explicitas, roda Postgres/Redis limpos e fixa portas/URLs; o checkout limpo nao tem `.env` | Pode esconder ou criar diferencas adicionais, embora nao seja necessario para explicar os dois sintomas ja reproduzidos |
| H6 | `hb preflight` cria falsa sensacao de paridade total com CI | confirmada | O proprio comando diz "Reproduzir todos os CI jobs localmente", mas `_CI_TEST_SUITES` cobre apenas 7 suites de governanca/paridade e nao inclui `CI / Tests` completo, frontend, Pact ou Docker | Mantem o gap entre PASS local e PASS exigido pelo GitHub |
| H7 | Algum teste reescreve `latest.json` e contamina testes posteriores no suite completo | enfraquecida | A suspeita veio de uma reproducao ampla em worktree previamente contaminado; no experimento controlado desta fase o hash de `latest.json` nao mudou | Hoje nao e uma causa-raiz forte; so volta a subir se reaparecer em reproducao limpa |
| H8 | OS/runner/versao de ferramenta e a causa primaria da divergencia atual | enfraquecida | As duas falhas principais foram reproduzidas localmente em Linux/checkout limpo, sem depender do runner do GitHub | Nao explica o problema principal neste momento |
| H9 | Cache ou artefato interno do GitHub esta sozinho causando a falha | descartada | As falhas principais foram reproduzidas localmente a partir do commit publicado, sem depender de cache do GitHub | Baixo valor investigativo para a proxima fase |

PARTE 3 -- Divergencias reais local vs GitHub

| Categoria | Local | GitHub | Diferenca encontrada | Pode explicar a falha? |
|-----------|-------|--------|----------------------|------------------------|
| comando | Validacao declarada no PR: `hb survival-suite`, validator `--profile ci`, suites direcionadas e hook local | `contract-gates.yml` roda compilers `--check` + validator; `ci.yml` roda `pytest -q -m "not slow"`, frontend tests, Pact e builds | O ritual local nao executa todos os comandos que o GitHub considera obrigatorios | Sim, diretamente |
| workflow | Fluxo manual/hook-driven, dependente do estado atual do workspace | Jobs separados, checkout limpo por job, branch rules com status checks required | O GitHub avalia o commit publicado; o local pode estar com artefatos regenerados e nao commitados | Sim, diretamente |
| ambiente | `.env` local presente; defaults de `settings.py` usam DB `5433`; `CI` so existe se setado manualmente | Vars explicitas no workflow; `CI=true` no gate remoto; Postgres/Redis provisionados limpos em `CI / Tests` | Diferenca de variaveis, portas, services e flags de execucao | Sim, parcialmente |
| paths/cwd | Workspace atual contem `.venv`, `.venv-contract`, `node_modules`, `frontend/node_modules` | Checkout limpo do runner nao contem esses caminhos ate os jobs instalarem o que cada job instala | Parte dos testes assume path repo-local (`.venv-contract`) que nao faz parte do contrato do runner | Sim, diretamente |
| dependencias | Ambiente local ja montado, com ferramentas e libs acumuladas | Cada job instala dependencias do zero; `CI / Tests` instala via `pip`, mas nao cria `.venv-contract` no root do repo | Diferenca de provisionamento e de forma de resolucao das dependencias | Sim, diretamente para alguns testes |
| arquivos lidos | Pode ler `.env`, `_reports/*` existentes e artefatos ja regenerados no disco | Le apenas o que esta commitado no checkout fresco e o que o job gera no proprio run | O local pode ler evidencias/artefatos mais novos que o commit ainda nao carrega | Sim, diretamente |
| arquivos gerados | Workspace atual ja tinha `compiled_ops/deploy/impact_report.json` modificado e varios `_reports/*` alterados | O GitHub parte do estado commitado e detecta drift se o artefato publicado estiver stale | O local estava "corrigido no disco", o GitHub nao | Sim, diretamente |
| escopo | Suites direcionadas e survival-suite; sem evidencia de execucao local do `pytest -q -m "not slow"` completo | `CI / Tests` cobre a suite ampla `not slow`; `Validate Contract Gates` cobre compilers e validator remoto | O escopo local e menor que o escopo required remoto | Sim, diretamente |
| gate | Local pode cair em profile `local` por default se `CI` nao estiver setado; survival-suite e pre-commit focam governanca | `CI / Validate Contracts` usa `validate_contracts.py --profile precommit`; `Validate Contract Gates` usa `CI=true` e dispara o profile `ci`, alem dos compilers | O GitHub nao roda apenas "o validator"; ele roda gates com definicoes e escopos diferentes entre workflows | Sim, criticamente |
| versao | Python `3.12.3`, Node `24.14.1`, npm `11.11.0` | Python `3.12.x`; Node `22` em `ci.yml` e `24` em `contract-gates.yml`; ferramentas instaladas de forma pinada no workflow | Existe diferenca de versao, mas ela nao foi necessaria para reproduzir as falhas principais | Nao como causa primaria |
| shell/runner | WSL2 Linux + `bash`, filesystem persistente | GitHub-hosted `ubuntu-22.04` / `ubuntu-latest` + `bash`, filesystem efemero por job | A diferenca mais relevante nao e o shell em si, e o isolamento/ephemeral state do runner | Sim, mas de forma indireta |
| cache/artefatos | Estado local acumulado entre execucoes pode mascarar drift | Cache GHA existe para npm/docker, mas as falhas principais reproduzem sem depender dele | O problema observado nao precisa de cache do GitHub; precisa apenas de checkout limpo | Sim para o lado local; nao para culpar cache do GitHub |

PARTE 4 -- Causas-raiz mais provaveis

1. O commit publicado no PR carrega um artefato derivado stale (`compiled_ops/deploy/impact_report.json`), enquanto o workspace local ja tinha a versao regenerada e nao commitada. Isso quebra `Validate Contract Gates` no GitHub e explica o PASS local enganoso.
2. O processo local de validacao nao replica os required checks de fato. Ele valida menos superficie que o GitHub, especialmente ao nao executar o `CI / Tests` completo e ao nao provar a mesma cadeia de gates/compilers requerida pelos workflows.
3. Parte da suite remota depende de um detalhe de ambiente que so existe localmente: `.venv-contract` dentro do repo. Isso torna o PASS local estruturalmente mais permissivo que o GitHub runner limpo.
4. Ha uma regressao real na camada JWT/autenticacao. O GitHub a encontra porque roda `CI / Tests`; o fluxo local usado para validar o PR nao a cobriu suficientemente.
5. Como causa secundaria, o ambiente local (`.env`, services, portas e variaveis`) nao e equivalente ao do runner, o que pode estar escondendo falhas adicionais mesmo apos resolver os sintomas principais.

PARTE 5 -- O que ainda precisa ser testado na Fase 3

- Obter os logs brutos autenticados do GitHub para os jobs falhos do PR `#30`, especialmente `Validate Contract Gates` e `CI / Tests`, para alinhar exatamente a ordem e os nomes dos testes que falham no runner.
- Reproduzir `CI / Tests` em checkout realmente pristino, em tres cenarios separados:
  1. sem `.venv-contract` repo-local;
  2. com `.venv-contract` repo-local;
  3. com exclusao temporaria dos testes ja explicados por `.venv-contract`, para revelar o proximo bloco real de falhas.
- Quebrar `CI / Tests` por familias de falha com `-x` e depois por subconjuntos: primeiro JWT/auth, depois testes HTTP/Schemathesis, para medir quanto da suite ampla falha por cascata do mesmo erro.
- Verificar se a presenca de `.env` local altera o resultado de subsets relevantes do backend, repetindo os testes prioritarios com e sem `.env` e com as mesmas vars do workflow.
- Revalidar a hipotese de contaminacao de `_reports/contract_gates/latest.json` apenas se uma reproducao limpa da suite ampla voltar a mudar o hash do arquivo. Sem isso, essa linha deve sair do foco principal.
- So se ainda restarem falhas nao explicadas apos os passos acima, comparar patch versions exatas do runner (`python 3.12.x`, Node `22.x`/`24.x`) e resolucao efetiva de dependencias no GitHub.


# FASE 3 -- PARIDADE3.md

PARTE 1 -- Diagnostico final

O problema "local passa, GitHub falha" nao tem uma causa unica. Ele e a combinacao de tres camadas:

1. O local nao estava validando o mesmo objeto nem a mesma superficie que o GitHub usa para decidir merge.
   O merge e governado pelos 5 status checks required da branch `main`, em checkout limpo do commit publicado. O "PASS local" que sustentou o PR foi obtido com um ritual mais estreito e sobre um workspace sujo, com artefatos ja regenerados fora do commit.

2. O commit publicado realmente contem falhas que o GitHub detecta corretamente.
   Em `Validate Contract Gates`, o commit do PR carrega `compiled_ops/deploy/impact_report.json` stale. Em `CI / Tests`, o commit carrega uma regressao real no middleware JWT: em vez de devolver 401, ele levanta `TypeError` e produz 500.

3. Alem das falhas reais, ha pelo menos um falso FAIL remoto gerado por implementacao de teste desalinhada com o runner oficial.
   `tests/pipeline_gates/test_backend_codegen_reports.py` assume `REPO_ROOT/.venv-contract/bin/python`, mas o job `CI / Tests` nao cria `.venv-contract` no checkout. Isso nao invalida o gate `CI / Tests`; invalida esse teste como implementacao fiel do gate.

Em termos forenses, o quadro final e:

- `Validate Contract Gates` falha legitimamente no GitHub, e essa falha e reproduzivel localmente em checkout limpo.
- `CI / Tests` tambem falha legitimamente no GitHub logo no inicio por causa da regressao JWT.
- Depois disso, o mesmo job ainda contem um segundo ponto de quebra artificial, causado pelo acoplamento de um teste a `.venv-contract`.
- Portanto, o "local passa" era majoritariamente um falso PASS local; o "GitHub falha" e majoritariamente correto, com um falso FAIL remoto adicional dentro do mesmo job de testes.

PARTE 2 -- Cadeia causal

| Etapa da cadeia causal | O que acontece | Evidencia | Papel na falha |
|------------------------|----------------|-----------|----------------|
| 1 | A fonte de verdade do merge e definida pelo canon + branch protection | `CONTRACT_PIPELINE.md` diz que a fase Validation e governada por `validate_contracts.py`, gates oficiais e CI; `CI_CONTRACT_GATES.md` define pipeline deterministico; branch protection de `main` exige 5 status checks | Define qual gate/check deve governar o desenvolvimento e invalida equivalencias locais nao oficiais |
| 2 | O ritual local usado para validar o PR nao cobre os mesmos checks required | O corpo do PR lista `hb survival-suite`, validator `--profile ci`, suites direcionadas e hook local; nao lista `pytest -q -m "not slow" --tb=short` nem prova execucao completa dos required checks | Gera falso PASS local por escopo insuficiente |
| 3 | O workspace local continha artefatos regenerados que nao estavam no commit publicado | `git status` mostrou `compiled_ops/deploy/impact_report.json` e varios `_reports/*` modificados; no workspace atual `compile_ops_contracts.py --check` passa | Faz o local aprovar um estado que o GitHub nunca recebeu |
| 4 | O GitHub avalia checkout limpo do SHA publicado, nao o workspace local | O SHA do PR e `0d1066c3ddad79887ff22f3f06a84c4078172af5`; em checkout limpo desse SHA, `compile_ops_contracts.py --check` falha | Fecha a diferenca entre "meu local" e "o que foi realmente enviado" |
| 5 | `Validate Contract Gates` falha porque o artefato operacional commitado esta stale | O drift em `compiled_ops/deploy/impact_report.json` foi reproduzido localmente; `SYNC_MANIFEST.yaml` nao trata mais `.github/workflows/deploy.yml` como source input, mas o artefato publicado ainda o lista | Causa legitima e suficiente para falha de `Validate Contract Gates` |
| 6 | `CI / Tests` inicia a suite ampla em ambiente limpo e encontra primeiro a regressao JWT | A ordem de coleta do Pytest coloca `tests/test_fase1_validation.py::TestJWT401::*` nas posicoes 44 e 45; o log parcial do run amplo mostrou `...........................................FF....` | Mostra que o primeiro bloqueio real de `CI / Tests` nao e `.venv-contract`; e autenticacao |
| 7 | Os dois primeiros testes que quebram no suite amplo falham pela mesma causa do middleware | Reproducao controlada de `tests/test_fase1_validation.py::TestJWT401` em checkout pristino falhou com `TypeError: AuthenticationError() takes no keyword arguments` em `src/identity_access/middleware.py` | Causa legitima e precoce da falha de `CI / Tests` |
| 8 | A regressao JWT nao e sintoma de ambiente; e bug do codigo publicado | `src/identity_access/tests/unit/test_jwt_auth_failure_handling.py` falha no workspace atual e no checkout limpo; a mesma assinatura invalida aparece nos traces | Confirma causa-raiz real de aplicacao, nao "misterio do runner" |
| 9 | Mais tarde no mesmo suite existe uma quebra estrutural extra por `.venv-contract` | `tests/pipeline_gates/test_backend_codegen_reports.py` esta nas posicoes 1068-1070 da coleta; em checkout pristino falha com `FileNotFoundError` para `/.venv-contract/bin/python`; com symlink manual, passa | Nao e a primeira causa da falha ampla, mas e um falso FAIL remoto real dentro de `CI / Tests` |
| 10 | O resultado final diverge porque o local mede uma superficie mais fraca e mais "contaminada" que o GitHub | Local aprova em workspace sujo e com comandos mais estreitos; GitHub reprova o commit publicado em checkout limpo, encontrando 2 falhas legitimas e 1 falha estrutural extra | Explica integralmente o padrao "local passa, GitHub falha" |

PARTE 3 -- Causa-raiz final

- Causa-raiz principal
  - O processo local de validacao nao estava alinhado com a superficie autoritativa de merge. Ele validou um workspace diferente do commit publicado e com um conjunto de checks mais fraco que o exigido pela branch protection.

- Causas-raiz secundarias
  - O commit publicado no PR contem `compiled_ops/deploy/impact_report.json` stale, o que quebra legitimamente `Validate Contract Gates`.
  - O commit publicado contem uma regressao real no middleware JWT, que quebra legitimamente `CI / Tests` logo no inicio.
  - O repositorio contem pelo menos um teste de `CI / Tests` acoplado a `.venv-contract` repo-local, o que introduz um falso FAIL remoto em runner limpo.

- Fatores contribuintes
  - Workspace local sujo com artefatos derivados nao commitados.
  - Uso de `hb survival-suite`, validator e suites direcionadas como substitutos de merge-readiness sem cobrir todos os required checks.
  - `hb preflight` afirma reproduzir todos os CI jobs, mas sua implementacao atual nao cobre `CI / Tests` completo nem frontend/builds.
  - Diferencas de `.env`, services e vars entre local e runner aumentam a chance de falso PASS local.

PARTE 4 -- Gate/configuracao correta

- Qual definicao de gate/check deve ser considerada correta?
  - A definicao correta e a do canon operacional (`CI_CONTRACT_GATES.md`, `GATES_REGISTRY.yaml`, `CONTRACT_PIPELINE.md`) materializada pelos 5 status checks required da branch `main` em checkout limpo do commit publicado.

- Por que?
  - Porque essa e a unica definicao que:
    - esta vinculada a branch protection;
    - corresponde explicitamente a fase Validation do sistema;
    - produz evidencia deterministica em `_reports/contract_gates/latest.json`;
    - impede falso PASS local por workspace sujo ou comando parcial;
    - representa a implementacao que de fato governa merge daqui para frente.

- Qual lado esta desalinhado: local, GitHub ou ambos?
  - Ambos, mas nao no mesmo grau.
  - O local esta primariamente desalinhado no processo de validacao: validou menos coisa e validou o estado errado.
  - O GitHub esta majoritariamente alinhado com a fonte de verdade, mas possui ao menos um teste desalinhado com o proprio ambiente oficial (`test_backend_codegen_reports.py` exigindo `.venv-contract` repo-local).

- O que hoje esta gerando falso PASS local ou falso FAIL remoto?
  - Falso PASS local:
    - validar o workspace atual em vez do commit publicado;
    - aceitar `hb survival-suite`/validator/suites direcionadas como equivalentes aos required checks;
    - executar checks com artefatos regenerados nao commitados;
    - depender de `.venv-contract`, `.env` e outros estados locais que o merge gate nao assume.
  - Falso FAIL remoto:
    - `tests/pipeline_gates/test_backend_codegen_reports.py` falha por acoplamento a `REPO_ROOT/.venv-contract/bin/python`, algo que o job `CI / Tests` nao provisiona.
  - FAIL remoto legitimo:
    - drift de `compiled_ops/deploy/impact_report.json`;
    - regressao JWT que converte 401 esperados em 500/TypeError.

PARTE 5 -- Condicoes obrigatorias para a correcao definitiva

- A correcao precisa alinhar a validacao local com a mesma superficie autoritativa dos 5 required checks da branch `main`.
- A correcao precisa eliminar a validacao sobre workspace sujo como criterio de aprovacao para merge.
- A correcao precisa resolver o drift deterministico de `compiled_ops/deploy/impact_report.json` no commit publicado, sem afrouxar o gate remoto.
- A correcao precisa restaurar o contrato correto da autenticacao JWT em `CI / Tests`: 401 esperado, sem `TypeError` e sem 500.
- A correcao precisa remover o acoplamento de testes de CI a `.venv-contract` repo-local, ou entao tornar esse ambiente parte explicita do workflow oficial. Hoje essa ambiguidade nao pode permanecer.
- A correcao precisa definir uma reproducao local de merge-readiness que seja verificavel e isomorfica aos checks required, em vez de depender de equivalencias implicitas.
- A correcao precisa neutralizar ou normalizar diferencas de `.env`, paths, services e cwd que hoje permitem falso PASS local.
- A correcao nao pode escolher o gate local mais fraco como referencia. A referencia obrigatoria e o canon oficial implementado pelos required checks do GitHub.
