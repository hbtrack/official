# Plano de Paridade Local x GitHub

> **NON-SOVEREIGN** — Documento operacional de planejamento. Não é artefato canônico soberano. Não substitui `ROADMAP.md` nem os contratos em `contracts/`.

Data: 2026-04-02  
Escopo: eliminar divergência entre execução local e GitHub no sistema contract-driven do HB Track.

## Diagnóstico objetivo

O repositório já tem a intenção correta: `scripts/hb preflight` se propõe a reproduzir a CI localmente. O problema é que ainda existem múltiplas fontes de verdade para a mesma execução.

Drifts concretos encontrados no código versionado e confirmados via API ao vivo (2026-04-02):

- **Node.js — 3 valores divergentes:** `.nvmrc` fixa `v24.14.0`, `ci.yml` usa `"22"` (validate + build-frontend), `contract-gates.yml` e `deploy.yml` usam `"24"`.
- **Python — 2 valores divergentes:** `ci.yml`, `contract-gates.yml` e `deploy.yml` usam `"3.12"`, mas `context-efficiency-audit.yml` e `domain-completeness-audit.yml` usam `"3.11"`. Não existe `.python-version`.
- **Postgres — versão e porta divergentes:** `infra/docker-compose.yml` usa `postgres:12` na porta `5433`; CI usa `postgres:16` na porta `5432`; `conftest.py` e `hb preflight` hardcodam porta `5432`.
- **Bootstrap divergente:** `scripts/bootstrap/dev_contract_env.sh` instala toolchain de um jeito, enquanto os workflows instalam `npm`, `pip` e `oasdiff` de outros jeitos.
- **Nenhum manifesto de toolchain:** versões estão espalhadas em `.nvmrc`, YAMLs de workflow, `docker-compose`, `hb preflight` e bootstrap. Não há `engines` em `package.json` nem `frontend/package.json`.
- **Enforcement duplicado e parcial:** branch protection legada (7 required checks, `enforce_admins: false`) coexiste com ruleset `contract-gates` (5 required checks, `bypass_actors: []`). A dualidade cria ambiguidade operacional e potencial de bypass por admin.
- A suíte de teste depende de infraestrutura externa; local e GitHub não percorrem exatamente o mesmo caminho operacional.

Conclusão: o problema principal não é falta de gates. É excesso de pontos de verdade para bootstrap, serviços de teste e enforcement.

## Arquitetura mínima recomendada

Princípio central: **um executável canônico, workflows finos, serviços de teste efêmeros no próprio pytest, e enforcement server-side por ruleset**.

Desenho proposto:

```text
Local / pre-push / PR
  -> caller fino
     -> executável canônico do repo
        -> bootstrap de toolchain
        -> policy checks estáticos
        -> pytest
           -> Testcontainers(Postgres, Redis)
        -> build checks
        -> artifacts/evidence
  -> GitHub ruleset exige checks estáveis antes do merge
```

No seu caso, o executável canônico não precisa nascer do zero. O caminho mais pragmático é promover `scripts/hb preflight` para virar a fonte única real da CI, com perfis claros, e fazer os workflows do GitHub apenas chamarem esse executor.

**Pré-requisito estrutural:** antes de unificar o executor, é necessário formalizar dois manifestos canônicos:
- **Manifesto de toolchain** — SSOT de versões (Node, Python, Postgres, Redis, oasdiff) consumido por `.nvmrc`, workflows, docker-compose, conftest, bootstrap e `hb preflight`.
- **Manifesto de merge-readiness** — lista oficial do que bloqueia merge, qual executor canônico reproduz isso localmente, e quais checks são required vs informativos.

Sem esses manifestos, o executor e os workflows vão hardcodar as mesmas versões dispersas que existem hoje, só que num lugar diferente.

## Avaliação por prática

Escala:

- Custo de adoção: `1` baixo, `5` alto.
- Ganho de confiabilidade: `1` baixo, `5` alto.
- Ganho de velocidade: `1` baixo, `5` alto.

| Prática | Vale a pena no HB Track? | Problema que resolve | Custo | Confiabilidade | Velocidade | Ordem |
| --- | --- | --- | --- | --- | --- | --- |
| Reusable workflows + fonte única executável | **Sim, imediato** | Remove drift entre `ci.yml`, `contract-gates.yml`, bootstrap local e comandos reais de validação | 3 | 5 | 3 | 1 |
| Testcontainers para Postgres/Redis | **Sim, imediato** | Remove drift entre `docker-compose` local e `services` do GitHub; elimina dependência de infra manual para rodar teste | 3 | 5 | 3 | 2 |
| Rulesets + required checks + CODEOWNERS | **Sim, imediato** | Fecha bypass server-side; impede merge sem passar pelo caminho canônico | 2 | 4 | 1 | 3 |
| Caching controlado | **Sim, imediato** | Reduz tempo sem introduzir ambiente “podre” ou falso verde por cache velho | 2 | 3 | 4 | 4 |
| OPA/Conftest | **Sim, com escopo estreito** | Declara e protege invariantes de workflow, versões, cache e layout sem depender de teste imperativo para tudo | 3 | 4 | 1 | 5 |
| Ambiente local hermético | **Sim, mas depois do executor canônico** | Reduz drift de máquina, PATH, WSL e onboarding | 3 | 4 | 2 | 6 |
| Paralelização com `pytest-xdist` | **Sim, por fases** | Reduz wall-clock do teste, mas só depois que fixtures e isolamento estiverem sólidos | 2 | 2 | 4 | 7 |

## Conferência com alternativas líderes

Após revisar as fontes nativas dos fabricantes/projetos e as referências mais consolidadas do ecossistema, a conclusão é:

- **não apareceu um substituto melhor** para `reusable workflows`, `rulesets`, `Testcontainers`, `pytest-xdist` e cache nativo de `setup-node`/`setup-python` no seu contexto GitHub + Python;
- **apareceu uma ferramenta complementar melhor** para um ponto específico: `actionlint` é melhor que OPA/Conftest para validar sintaxe/semântica de GitHub Actions;
- **apareceu uma forma mais forte de hermeticidade** no médio prazo: `Dev Container Spec` junto de `devcontainers/ci`, se você quiser que o mesmo container de desenvolvimento seja reaproveitado na CI.

| Problema | Alternativas líderes verificadas | Melhor escolha para o HB Track | Veredito |
| --- | --- | --- | --- |
| Reutilizar pipeline no GitHub | Reusable workflows, composite actions, YAML anchors/templates | **Reusable workflow + executável do repo** | `composite action` não serve como substituto porque não contém jobs, não usa secrets e roda como um único step; ele é complementar, não concorrente |
| Validar políticas estruturais do repo | OPA/Conftest, actionlint, linters pontuais | **OPA/Conftest + actionlint** | OPA/Conftest continua sendo a melhor base de policy-as-code arbitrária; `actionlint` é a ferramenta melhor para workflow files de Actions |
| Subir Postgres/Redis reais em teste | Testcontainers, `services:` do GitHub Actions, `docker compose`, fixtures locais especializadas | **Testcontainers** | É a opção mais alinhada com paridade local/CI e com dependências efêmeras controladas por código |
| Paralelizar pytest | `pytest-xdist`, plugins paralelos menores, paralelismo ad hoc | **pytest-xdist** | Continua sendo a opção padrão e mais madura do ecossistema pytest |
| Cachear dependências | `setup-node`, `setup-python`, `actions/cache`, cache manual de diretórios | **cache nativo de `setup-node`/`setup-python`** | `actions/cache` só ganha quando você precisa de cache bespoke; para npm/pip, o nativo é mais seguro e simples |
| Enforcement no GitHub | Rulesets, branch protection legado | **Rulesets** | Em GitHub, rulesets são a forma mais poderosa e auditável de enforcement |
| Hermeticidade local | bootstrap ad hoc, devcontainer, devcontainer + CI, Nix/Bazel | **Dev Container Spec**, idealmente com `devcontainers/ci` no médio prazo | `Nix/Bazel` podem ser mais fortes em isolamento absoluto, mas são piores em custo/benefício para o seu caso hoje |

## Leitura correta de cada decisão

### Reusable workflows / fonte única executável

**Decisão:** sim, mas o ganho real vem da combinação de duas coisas:

- reusable workflow no GitHub;
- um comando canônico do repositório que GitHub e local chamam do mesmo jeito.

Se você fizer só reusable workflow, ainda sobra drift local.  
Se você fizer só script local, ainda sobra duplicação nos YAMLs.  
O ponto certo é: **workflow fino chamando executável fino**.

Recomendação prática para o HB Track:

- manter `scripts/hb` como autoridade operacional;
- criar um perfil explícito, por exemplo `python3 scripts/hb ci --profile pr`;
- fazer `ci.yml` e `contract-gates.yml` virarem callers finos de um workflow reutilizável;
- dentro do reusable workflow, chamar o executor canônico em vez de repetir `pip install`, `npm ci`, `oasdiff`, `pytest`, compilers e afins em YAML solto.

### Policy as code com OPA/Conftest

**Decisão:** vale a pena, mas não para substituir `validate_contracts.py`.

**Correção importante após comparar alternativas:** para GitHub Actions, eu adicionaria `actionlint` como complemento obrigatório.

Onde OPA/Conftest ajuda muito no seu caso:

- validar que todo workflow usa o reusable workflow aprovado;
- validar que versões de Node/Python vêm do manifesto canônico;
- bloquear caches proibidos;
- validar presença e formato de arquivos obrigatórios de governança;
- validar um manifesto versionado do ruleset desejado.

Onde **não** vale usar OPA/Conftest:

- lógica rica de domínio já coberta pelo seu pipeline de contratos;
- runtime contract validation;
- comportamento dinâmico de teste.

Onde `actionlint` entra melhor que OPA/Conftest:

- erro de sintaxe/semântica específico de GitHub Actions;
- expressions inválidas;
- uso incorreto de `uses`, `needs`, `if`, runners, shells e workflow keys;
- feedback de lint com foco em falso positivo baixo.

Resumo pragmático: use Rego para **invariantes estáticos de repositório** e `actionlint` para **workflow lint especializado**. Não use Rego para reimplementar o que `actionlint` já faz melhor.

### Testcontainers para Postgres/Redis

**Decisão:** é a mudança com melhor relação impacto/esforço para o seu problema específico.

Hoje o teste depende de coordenação externa. Isso é exatamente a origem de divergência entre laptop e GitHub.  
Com Testcontainers:

- local e GitHub sobem Postgres/Redis pelo mesmo código Python;
- você elimina o acoplamento entre `conftest.py` e `infra/docker-compose.yml` para testes;
- o `docker-compose` pode continuar existindo, mas só para subir a stack manual da aplicação, não para ser pré-requisito da suíte.

Recomendação prática:

- criar fixtures de sessão para `PostgresContainer("postgres:16")` e `RedisContainer("redis:7-alpine")`;
- injetar `DATABASE_URL`, `DB_*`, `REDIS_URL` e `CELERY_*` a partir dessas fixtures;
- remover dependência de `services:` do job de testes no GitHub;
- parar de usar o `docker-compose` de dev como mecanismo principal de teste.

### Paralelização de pytest

**Decisão:** vale a pena, mas não como primeiro movimento.

O risco clássico é acelerar uma suíte ainda não determinística e transformar drift em flake paralelizada.  
No seu contexto, a ordem correta é:

1. unificar executor;
2. unificar infraestrutura de teste com Testcontainers;
3. só então paralelizar.

Recomendação prática:

- adicionar `pytest-xdist`;
- começar apenas nas suítes unitárias e puras;
- usar `-n auto --dist worksteal` como default inicial para testes sem fixture compartilhada pesada;
- usar `--dist loadscope` ou `xdist_group` nos grupos que dependem de fixtures caras ou afinidade de processo;
- manter governança, migração e partes sensíveis serializadas no começo.

### Caching controlado

**Decisão:** sim, mas com disciplina.

Cache bom acelera. Cache errado cria falso verde.

Cache que faz sentido aqui:

- `setup-node` com cache do gerenciador e chave baseada em lockfile;
- `setup-python` com cache `pip` e chave baseada em `requirements*.txt` e arquivos equivalentes;
- cache do Buildx para imagens Docker.

Nota após revisar as fontes oficiais: para `npm`/`pip`, prefira os caches nativos de `setup-node` e `setup-python`, que já usam a infraestrutura de cache do GitHub por baixo. Só caia para `actions/cache` quando precisar de paths/chaves não cobertos pelo cache nativo.

Cache que **não** recomendo como padrão no seu caso:

- `node_modules`;
- `.venv` do projeto;
- banco de dados/volumes de teste;
- `_reports` gerados;
- qualquer artefato derivado de contrato usado para “pular” validação.

### Branch protection / rulesets

**Decisão:** sim, e eu prefiro **rulesets** a novas branch protections legadas.

#### Estado verificado ao vivo (2026-04-02)

Existem **dois mecanismos ativos em paralelo** na `main`:

**Branch Protection (legado):**
- `strict: true` (require up-to-date)
- `enforce_admins: false` — **admin pode bypassar**
- `required_conversation_resolution: false`
- `allow_force_pushes: false`
- 7 required checks: `Validate Contracts`, `Tests`, `Frontend Build + Tests`, `Validate Contract Gates`, `Governance Tests`, `Adversarial Suite`, `Architecture Drift Check`

**Ruleset `contract-gates` (ativo, enforcement=active):**
- Target: `~DEFAULT_BRANCH` (main)
- `bypass_actors: []` — **ninguém pode bypassar**
- `current_user_can_bypass: "never"`
- `required_review_thread_resolution: true`
- `dismiss_stale_reviews_on_push: true`
- `required_approving_review_count: 0`
- Regras: `deletion`, `non_fast_forward`, `pull_request`, `required_status_checks`
- 5 required checks: `Validate Contract Gates`, `Governance Tests`, `Architecture Drift Check`, `CI / Validate Contracts`, `CI / Tests`

**Branch `develop`:** não existe no GitHub (404).

#### Problemas encontrados

1. **Dualidade cria ambiguidade e vetor de bypass:** `enforce_admins: false` na branch protection permite que admins bypassem os 7 checks legados, enquanto o ruleset (`bypass_actors: []`) não permite bypass. Qual é a fonte de verdade?
2. **Nomes de check potencialmente frágeis:** o ruleset exige `CI / Validate Contracts` e `CI / Tests` (com prefixo do workflow name). Os check runs reais reportados são `Validate Contracts` e `Tests` (sem prefixo). Se o GitHub usa a convenção `workflow_name / job_name`, funciona; mas qualquer renomeação de workflow quebra silenciosamente.
3. **Jobs condicionais não bloqueiam merge:** 4 jobs de `contract-gates.yml` rodam só quando `governance_changed == 'true'` (Governance Enforcement, Paridade Registry×Executor, Paridade Schema×Template×Skills, Validação Cruzada SESSION_HANDOFF). Nenhum é required check — **correto**, mas se falharem em PR de governança, nada impede merge.

#### Ação necessária

- **Remover a branch protection legada** e manter apenas o ruleset (mais restritivo e auditável).
- Ou alinhar perfeitamente os dois. Do jeito atual, o sistema é auditavelmente confuso.
- Adicionar `Frontend Build + Tests` e `Adversarial Suite` ao ruleset se continuarem sendo gates reais.
- Documentar explicitamente quais checks são required vs informativos (manifesto de merge-readiness).

Configuração mínima recomendada para o ruleset unificado:

- target: `main`;
- require pull request before merging;
- require conversation resolution;
- require branches up to date;
- require status checks estáveis (com lista explícita do manifesto de merge-readiness);
- block force pushes;
- bypass mínimo e explícito (zero, se possível).

Checks mínimos que eu exigiria:

- workflow canônico de contracts/governance;
- workflow canônico de testes;
- opcionalmente build Docker se ele for gate real de release, não só conveniência.

### Ambiente local hermético

**Decisão:** sim, mas depois de estabilizar o executor canônico.

Se você congelar um ambiente antes de congelar o comando certo, só vai containerizar o drift atual.

A versão pragmática para o HB Track é:

- adicionar `.devcontainer/devcontainer.json`;
- pin de Node e Python;
- bootstrap automático chamando o mesmo setup canônico;
- acesso ao Docker socket para Testcontainers;
- usar o devcontainer como ambiente de desenvolvimento e também como fallback para troubleshooting de paridade.

Versão mais forte de médio prazo:

- reutilizar esse mesmo devcontainer na CI com `devcontainers/ci`, em vez de tratá-lo só como conveniência local.

Eu **não** faria Nix/Bazel/dev shell sofisticado agora. O ganho marginal não paga o custo num repositório que já tem um executor Python forte e roda em GitHub Actions hosted.

## Ordem de adoção recomendada (revisada após validação ao vivo)

1. **Resolver dualidade branch protection vs ruleset + formalizar merge-readiness**
   Motivo: hoje existe bypass por admin via branch protection legada; a coexistência dos dois mecanismos é auditavelmente confusa. Remover branch protection legada, manter só ruleset unificado, e formalizar num manifesto versionado quais checks são required vs informativos.
2. **Manifesto de toolchain versionado**
   Motivo: sem SSOT de versões, qualquer mudança precisa ser propagada manualmente em 4+ arquivos. O manifesto é pré-requisito para que o executor e os workflows consumam a mesma definição.
3. **actionlint como gate obrigatório**
   Motivo: hoje falta proteção estrutural de workflow — o `contract-gates.yml` já tem path errado em chamada de script (`scripts/validate_contracts.py` em vez de `scripts/contracts/validate/validate_contracts.py`). actionlint protege integridade antes de otimizar velocidade.
4. **Executável canônico + reusable workflow**
   Motivo: fecha o maior vazamento de drift. Agora possível porque manifestos de toolchain e merge-readiness já existem como SSOT.
5. **Testcontainers para Postgres/Redis**
   Motivo: unifica o caminho de teste local/GitHub. Versão e porta vêm do manifesto de toolchain.
6. **Rulesets com required checks estáveis (ajuste fino)**
   Motivo: com o executor e reusable workflows estabilizados, ajustar os nomes de check no ruleset para refletir a nova estrutura.
7. **Caching controlado**
   Motivo: recupera tempo sem reabrir drift.
8. **OPA/Conftest para invariantes estáticos**
   Motivo: evita regressão estrutural do arranjo novo (validar que workflows consomem manifesto, versões estão alinhadas, caches proibidos não aparecem).
9. **Ambiente local hermético**
   Motivo: consolida a paridade de máquina após estabilizar o pipeline.
10. **`pytest-xdist`**
    Motivo: aceleração segura só depois da determinização.

## Plano pragmático

### Mínimo viável para resolver o problema

Faça só isto:

1. Remova a branch protection legada da `main`. Mantenha só o ruleset `contract-gates` como enforcement único.
2. Formalize um manifesto de toolchain versionado (`toolchain.json` ou equivalente) com Node, Python, Postgres, Redis, oasdiff. Faça `.nvmrc`, workflows, docker-compose, conftest e bootstrap consumirem esse manifesto.
3. Formalize um manifesto de merge-readiness: lista oficial de required checks, qual executor canônico reproduz cada um, e quais jobs são informativos vs bloqueantes.
4. Adicione `actionlint` como gate obrigatório em CI (valida sintaxe/semântica dos workflows antes de qualquer outra coisa).
5. Transforme `scripts/hb` no executor oficial de CI local e GitHub, consumindo o manifesto de toolchain.
6. Extraia um reusable workflow e deixe `ci.yml` e `contract-gates.yml` como callers finos.
7. Troque `services:` do GitHub e pré-requisito de `docker-compose` em testes por Testcontainers para Postgres e Redis.
8. Ajuste os nomes de check no ruleset para refletir a nova estrutura de workflows.
9. Ajuste caches para lockfiles e requirements pinados, sem cachear ambiente pronto.

Se você fizer apenas esse bloco, elimina a divergência real observada hoje e resolve a ambiguidade de enforcement.

**Prova operacional definitiva:** mesmo SHA, executor local (`hb preflight`), push, required checks verdes no GitHub. Se ambos passam no mesmo commit, paridade confirmada.

### Ideal de médio prazo

Depois do MVP:

1. Adicione um pacote pequeno de políticas Rego com Conftest para workflow/version/cache/ruleset manifest.
2. Adicione `.devcontainer` para reduzir drift de máquina e WSL.
3. Se quiser paridade máxima, execute o caminho canônico dentro do devcontainer também na CI com `devcontainers/ci`.
4. Separe a suíte em grupos e introduza `pytest-xdist` nos grupos seguros.
5. Automatize verificação de alinhamento entre manifesto de toolchain e todos os consumidores (teste de invariante que falha se algum arquivo usar versão diferente do manifesto).

### Excesso de complexidade no seu caso

Eu evitaria agora:

- reescrever o pipeline em Bazel;
- migrar tudo para Nix flakes;
- self-hosted runner só para tentar espelhar bit a bit o ambiente local;
- cachear `node_modules`, `.venv` ou volumes de banco entre jobs;
- paralelizar a suíte inteira de uma vez;
- usar OPA/Conftest para substituir validação dinâmica que já está bem resolvida em Python.

## Recomendação final

Se o objetivo é **eliminar divergência**, a arquitetura mínima e mais eficaz para o HB Track é esta:

- **um manifesto único de toolchain** (SSOT de versões, consumido por todos os arquivos);
- **um manifesto único de merge-readiness** (SSOT de política de merge, consumido pelo ruleset);
- **uma fonte única executável no repositório** (consome os dois manifestos);
- **GitHub usando reusable workflows finos para chamar essa fonte**;
- **Testcontainers como mecanismo padrão de infraestrutura de teste**;
- **rulesets como enforcement server-side único** (branch protection legada removida);
- **`actionlint` como gate obrigatório** de lint de workflow;
- **cache só no nível de dependência, nunca no nível de ambiente pronto**.

OPA/Conftest, devcontainer e `pytest-xdist` entram depois para blindagem e velocidade, não como primeiro remédio. Se você quiser o caminho mais forte de hermeticidade no GitHub, o próximo degrau é `Dev Container Spec` com `devcontainers/ci`.

**Princípio de fecho:** o problema não será resolvido de forma definitiva só ajustando `hb preflight`, nem só com reusable workflow. Ele será resolvido quando existirem **quatro artefatos convergentes**: política única de merge, manifesto único de toolchain, executor único e ambiente de teste sem infra manual local. A prova operacional real (mesmo SHA → executor local → push → required checks verdes) é o que fecha o caso.

## Fontes oficiais consultadas

- GitHub reusable workflows: https://docs.github.com/en/enterprise-cloud@latest/actions/how-tos/reuse-automations/reuse-workflows
- GitHub reusable workflows vs composite actions: https://docs.github.com/en/actions/concepts/workflows-and-actions/reusing-workflow-configurations
- GitHub dependency caching: https://docs.github.com/en/actions/concepts/workflows-and-actions/dependency-caching
- GitHub rulesets: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets
- GitHub available rules for rulesets: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets
- `actions/setup-node`: https://github.com/actions/setup-node
- `actions/setup-python`: https://github.com/actions/setup-python
- `actionlint`: https://github.com/rhysd/actionlint
- Conftest: https://www.conftest.dev/options/
- OPA + Conftest ecosystem entry: https://www.openpolicyagent.org/ecosystem/entry/conftest
- OPA: https://www.openpolicyagent.org/docs
- OPA policy testing: https://www.openpolicyagent.org/docs/policy-testing
- Testcontainers for Python: https://testcontainers-python.readthedocs.io/
- Docker Docs on Testcontainers: https://docs.docker.com/testcontainers/
- `pytest-xdist`: https://pytest-xdist.readthedocs.io/en/stable/distribution.html
- Dev Container Specification overview: https://containers.dev/overview
- `devcontainers/ci`: https://github.com/devcontainers/ci

## Apêndice: Verificação ao vivo do enforcement (2026-04-02)

### Drifts confirmados

| Dimensão | Fonte 1 | Fonte 2 | Fonte 3 | Drift? |
|---|---|---|---|---|
| Node.js | `.nvmrc` → `v24.14.0` | `ci.yml` → `"22"` | `contract-gates.yml`/`deploy.yml` → `"24"` | **SIM — 3 valores** |
| Python | sem `.python-version` | `ci.yml`/`contract-gates.yml`/`deploy.yml` → `"3.12"` | audits → `"3.11"` | **SIM — 2 valores** |
| Postgres versão | `docker-compose` → `postgres:12` | CI → `postgres:16` | — | **SIM** |
| Postgres porta | `docker-compose` → `5433` | `conftest.py`/`hb preflight` → `5432` | CI → `5432` | **SIM** |
| Redis | `docker-compose` → `7-alpine` | CI → `7-alpine` | — | OK |
| oasdiff | bootstrap → `1.12.3` | `ci.yml` → `1.12.3` | `contract-gates.yml` → `1.12.3` | OK |

### Enforcement server-side

| Mecanismo | Target | Bypass | Required Checks | Conversation Resolution |
|---|---|---|---|---|
| Branch Protection (legado) | `main` | `enforce_admins: false` — admin pode bypassar | 7 checks | `false` |
| Ruleset `contract-gates` | `~DEFAULT_BRANCH` | `bypass_actors: []` — ninguém | 5 checks (nomes prefixados) | `true` |

### Check runs reais (último run)

**CI (run 23911090996, conclusion: failure):**
- Validate Contracts → success
- Tests → failure
- Frontend Build + Tests → success
- Docker Build Check → skipped

**Contract Gates (conclusion: failure):**
- Validate Contract Gates → failure
- Governance Tests → success
- Adversarial Suite → success
- Architecture Drift Check → success
- Governance Enforcement (survival-suite) → success (condicional)
- Paridade Registry × Executor → success (condicional)
- Paridade Schema × Template × Skills → success (condicional)
- Validação Cruzada SESSION_HANDOFF ↔ session_start → success (condicional)

### Ferramentas não implementadas

| Ferramenta | Status |
|---|---|
| Reusable workflows | Zero — nenhum `workflow_call` no repo |
| Manifesto de toolchain | Ausente |
| Manifesto de merge-readiness | Ausente |
| Testcontainers | Zero |
| actionlint | Zero |
| pytest-xdist | Zero |
| OPA/Conftest | Zero |
