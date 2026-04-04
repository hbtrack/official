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
