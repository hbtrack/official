Abaixo está o guia final de implementação do reviewer automático do HB Track, em modo Pacote B, do Passo 0 até o DONE.

Ele assume este objetivo fechado:

* zero custo agora;
* Gemini automático no GitHub;
* modo híbrido: inline quando houver âncora segura no diff, summary quando não houver;
* alinhamento explícito ao modelo contract-driven do HB Track;
* reviewer advisory, sem bloquear merge;
* Claude continua manual/local, fora deste fluxo.

Também assume este recorte técnico:

* ambiente principal: WSL/Linux;
* repositório alvo: `hbtrack/official`;
* integração por GitHub Actions + Gemini Developer API + bridge script próprio.

## Visão de arquitetura

O reviewer final tem quatro peças:

1. `.github/workflows/ai-pr-review.yml`
   Orquestra o gatilho em PR, coleta diff, chama o modelo, executa o bridge e publica a review.

2. `.github/ai-review/config.yaml`
   Centraliza modo, modelo, limites, severidade, filtros de path e comportamento operacional.

3. `.github/ai-review/styleguide.md`
   Define a policy do reviewer em linguagem humana, explicitamente ancorada no canon do HB Track.

4. `scripts/ai_review_bridge.py`
   Converte a saída JSON do Gemini em:

   * comentários inline válidos para a Pull Request Reviews API do GitHub;
   * comentário consolidado residual para achados sem âncora segura.

A lógica central é:

* se o achado aponta para arquivo + linha válida no lado direito do diff, publica inline;
* se não houver âncora segura, cai para summary;
* se a severidade ficar abaixo do threshold, descarta;
* se o arquivo estiver em path excluído, ignora.

## Passo 0 — Preparação do ambiente WSL

No WSL, valide que você está no workspace correto e usando Linux/WSL como ambiente principal, o que já é o padrão declarado do projeto. 

Entre na raiz do projeto:

```bash
cd /home/davis/HB-TRACK
pwd
git rev-parse --show-toplevel
```

Instale as ferramentas operacionais mínimas:

```bash
sudo apt update
sudo apt install -y gh curl jq python3 python3-pip
```

Instale o `actionlint`:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/rhysd/actionlint/main/scripts/download-actionlint.bash)
sudo mv actionlint /usr/local/bin/
actionlint -version
```

Se você usa venv no projeto, ative-o. Se não, pode usar Python do sistema para este reviewer:

```bash
python3 -m pip install --upgrade pip
```

Autentique o GitHub CLI no WSL, se ainda não estiver autenticado:

```bash
gh auth login
gh auth status
```

Objetivo do Passo 0:

* `gh` instalado e autenticado;
* `actionlint` disponível;
* Python funcional;
* workspace correto do HB Track.

## Passo 1 — Confirmar o desenho normativo antes de implementar

Antes de editar qualquer coisa, confirme mentalmente estes princípios do HB Track, porque eles guiam o reviewer:

* contratos e canon têm precedência sobre implementação;
* enforcement e schemas têm autoridade maior que bridge docs;
* artefatos derivados não são soberanos;
* o pipeline oficial já existe e o reviewer novo deve ser advisory, não gate obrigatório.    

Decisão operacional que fica congelada aqui:

* o reviewer novo não substitui `contract-gates.yml`;
* o reviewer novo não comenta em `generated/**` nem `_reports/**`;
* o reviewer novo trabalha em português;
* o reviewer novo não faz sugestões cosméticas.

## Passo 2 — Estrutura canônica dos arquivos do reviewer

Na raiz do projeto, garanta estes paths:

```bash
mkdir -p .github/ai-review
mkdir -p .github/workflows
mkdir -p scripts
```

Os quatro arquivos finais devem existir exatamente nestes caminhos:

```text
/home/davis/HB-TRACK/.github/workflows/ai-pr-review.yml
/home/davis/HB-TRACK/.github/ai-review/config.yaml
/home/davis/HB-TRACK/.github/ai-review/styleguide.md
/home/davis/HB-TRACK/scripts/ai_review_bridge.py
```

Objetivo do Passo 2:
padronizar os paths e evitar dispersão de lógica fora do repositório.

## Passo 3 — Definir o modo de operação do reviewer

O modo final do HB Track deve ser `hybrid`.

Isso significa:

* inline comments só quando o bridge conseguir mapear com segurança o achado ao diff do PR;
* achados sem âncora segura vão para o review consolidado;
* severidade abaixo do mínimo configurado não é publicada.

Essa decisão evita o erro clássico de sistemas que “forçam inline” e passam a errar localização ou criar ruído em massa.

## Passo 4 — Configurar `config.yaml`

O `config.yaml` é a camada operacional do reviewer. Ele não deve conter prosa; só parâmetros.

Ele precisa definir:

* modo de publicação;
* modelo do Gemini;
* temperatura;
* limite de arquivos;
* limite de comentários;
* threshold mínimo de severidade;
* severidades permitidas;
* inclusão e exclusão de paths.

Estrutura recomendada:

```yaml
review:
  mode: hybrid
  model: gemini-2.5-flash
  temperature: 0.2
  max_files: 20
  max_comments: 6
  min_severity_to_publish: medium
  allowed_severities:
    - critical
    - high
    - medium
    - low

paths:
  include:
    - "docs/hbtrack/modulos/**/graph/**"
    - "contracts/**"
    - ".contract_driven/**"
    - "docs/_canon/**"
    - ".github/workflows/**"
    - "scripts/contracts/validate/**"
    - "scripts/hb"
    - "backend/**"
    - "frontend/**"
    - "tests/**"
  exclude:
    - "generated/**"
    - "_reports/**"
    - "dist/**"
    - "build/**"
    - "coverage/**"
    - "**/package-lock.json"
    - "**/pnpm-lock.yaml"
    - "**/yarn.lock"
    - "**/bun.lockb"
```

Regras de ouro para esse arquivo:

* modelo não fica hardcoded no Python;
* exclusões de derivados são obrigatórias;
* os paths devem refletir o espaço soberano do projeto.

## Passo 5 — Configurar `styleguide.md`

O `styleguide.md` é a política humana do reviewer e precisa dizer explicitamente que o projeto é o HB Track.

Ele deve cobrir:

* natureza do sistema;
* cadeia de autoridade;
* prioridade de revisão;
* o que não revisar;
* idioma;
* formato esperado dos comentários.

Conteúdo mínimo recomendado:

* o projeto é contract-driven;
* contratos são SSOT antes de implementação;
* em caso de conflito, prevalecem enforcement, depois schemas, depois canon;
* bridge docs e derivados não redefinem autoridade;
* não comentar sobre `generated/**` nem `_reports/**`;
* não fazer review cosmético;
* revisar conflitos entre contrato, canon, gate, schema e implementação;
* escrever em português claro e objetivo.

Objetivo do Passo 5:
garantir que o modelo revise o HB Track como HB Track, e não como projeto genérico.

## Passo 6 — Implementar `scripts/ai_review_bridge.py`

Esse script é a peça crítica do Pacote B.

Responsabilidades do bridge:

* ler o diff do PR já coletado pelo workflow;
* ler `config.yaml`;
* ler `styleguide.md`;
* validar a resposta JSON do Gemini;
* filtrar severidade;
* verificar se o arquivo é elegível;
* validar se a linha referenciada existe no lado correto do diff;
* separar achados em:

  * `inline_comments`
  * `summary_findings`
* produzir um payload final que o workflow consiga publicar.

Estrutura lógica obrigatória do JSON retornado pelo Gemini:

* `path`
* `line`
* `severity`
* `title`
* `body`
* `suggestion` opcional

Exemplo de shape:

```json
[
  {
    "path": "contracts/openapi/paths/matches.yaml",
    "line": 42,
    "severity": "high",
    "title": "operationId divergente do contrato canônico",
    "body": "O patch altera a semântica do endpoint sem atualizar a superfície contratual correspondente.",
    "suggestion": "Alinhar operationId e contrato antes de promover a mudança."
  }
]
```

Critérios do bridge:

* se `path` não estiver incluído ou estiver excluído, descarta;
* se `severity` estiver abaixo de `min_severity_to_publish`, descarta;
* se `line` não puder ser ancorada com segurança no diff do PR, move para summary;
* se tudo estiver válido, prepara comentário inline.

Objetivo do Passo 6:
impedir que o workflow dependa de texto livre ou de parsing frágil.

## Passo 7 — Ajustar `ai-pr-review.yml`

O workflow final deve ser separado do `contract-gates.yml`. O repositório já tem CI contratual formal, então este reviewer deve rodar ao lado, não dentro dele. 

O workflow deve:

* disparar em `pull_request`;
* cobrir `opened`, `synchronize`, `reopened`, `ready_for_review`;
* ignorar PR draft;
* ter `permissions` mínimas:

  * `contents: read`
  * `pull-requests: write`
* usar o `GITHUB_TOKEN` do workflow como padrão;
* fazer checkout com histórico suficiente;
* coletar arquivos e patches do PR;
* limitar arquivos elegíveis conforme `config.yaml`;
* chamar o Gemini;
* executar o bridge;
* publicar a review híbrida.

Ordem das etapas:

1. checkout
2. setup Python
3. instalar dependências
4. carregar config/styleguide
5. coletar diff do PR
6. chamar Gemini
7. rodar `ai_review_bridge.py`
8. publicar review via GitHub Review API

Importante:
não use `gh pr review --comment` como mecanismo central para inline comments. O caminho robusto é construir o payload de review a partir do bridge.

## Passo 8 — Secrets no GitHub

No GitHub, configure apenas o necessário.

Crie:

* `GEMINI_API_KEY`

Para o cenário inicial do HB Track, não introduza `GH_PAT` como padrão. O reviewer deve começar com o `GITHUB_TOKEN` nativo do workflow. Só migre para PAT se surgir uma limitação concreta.

Objetivo do Passo 8:
manter o menor volume possível de credenciais sensíveis.

## Passo 9 — Dependências Python do reviewer

Instale localmente, para testes, o necessário ao script:

```bash
python3 -m pip install pyyaml requests
```

Se o seu bridge usar o SDK oficial do Gemini para testes locais, instale também:

```bash
python3 -m pip install google-generativeai
```

No workflow, prefira instalar só o que o script realmente usa.

## Passo 10 — Lint e validação estática antes do primeiro commit

Rode o linter do workflow:

```bash
actionlint .github/workflows/ai-pr-review.yml
```

Valide sintaxe YAML dos arquivos do reviewer:

```bash
python3 - <<'PY'
import yaml
for path in [
    ".github/ai-review/config.yaml",
]:
    with open(path, "r", encoding="utf-8") as f:
        yaml.safe_load(f)
print("YAML OK")
PY
```

Valide sintaxe Python do bridge:

```bash
python3 -m py_compile scripts/ai_review_bridge.py
```

Objetivo do Passo 10:
não abrir PR com erro sintático evitável.

## Passo 11 — Revisão humana dos arquivos antes de commitar

Antes do commit, faça uma revisão manual curta:

Confirme:

* `config.yaml` está com `mode: hybrid`;
* `styleguide.md` menciona explicitamente HB Track, CDD, cadeia de autoridade e exclusão de derivados;
* `ai-pr-review.yml` não interfere em `contract-gates.yml`;
* `ai_review_bridge.py` não hardcodeia paths errados nem modelo fora do `config.yaml`.

## Passo 12 — Commit local da infraestrutura do reviewer

Adicione apenas os quatro arquivos do reviewer:

```bash
git add .github/workflows/ai-pr-review.yml
git add .github/ai-review/config.yaml
git add .github/ai-review/styleguide.md
git add scripts/ai_review_bridge.py
```

Commit recomendado:

```bash
git commit -m "infra(ai-review): add hybrid Gemini PR reviewer for HB Track"
```

## Passo 13 — Push para uma branch dedicada

Não faça isso direto em `main`.

Crie uma branch de infraestrutura:

```bash
git checkout -b chore/ai-reviewer-hybrid
git push -u origin chore/ai-reviewer-hybrid
```

Objetivo do Passo 13:
validar o reviewer como qualquer outra mudança governada do repositório.

## Passo 14 — Abrir um PR de teste controlado

Abra um PR pequeno e deliberado.

O teste ideal:

* alterar um arquivo soberano pequeno;
* preferencialmente em `contracts/**` ou `docs/hbtrack/modulos/**/graph/**`;
* evitar mexer em dezenas de arquivos;
* manter o PR em draft inicialmente.

Depois de abrir, mude de Draft para Ready for review.

Esse é o melhor gatilho para a primeira validação, porque evita ruído de sincronizações múltiplas e testa o evento certo.

## Passo 15 — Critério de validação do primeiro ciclo

Considere PASS se tudo abaixo ocorrer:

* o workflow aparece no PR;
* ele não quebra o `contract-gates.yml`;
* ele não comenta em `generated/**` nem `_reports/**`;
* ele publica review em português;
* inline comment só aparece quando o bridge encontra âncora segura;
* achados sem âncora vão para summary;
* o reviewer não publica comentário cosmético.

Considere DEGRADED se:

* o review consolidado sai, mas sem inline;
* o modelo responde, mas o bridge descarta vários achados por falta de âncora;
* a review está útil, porém excessivamente conservadora.

Considere FAIL se:

* o workflow quebra antes de chamar o modelo;
* a API key falha;
* o reviewer comenta em paths derivados;
* os comentários violam a lógica do HB Track;
* o workflow interfere no pipeline contratual oficial.

## Passo 16 — Ajuste fino após o primeiro PR

Só depois do primeiro teste real, ajuste:

* severidade mínima;
* número máximo de comentários;
* paths incluídos;
* paths excluídos;
* temperatura;
* modelo.

Ordem recomendada de tuning:

1. reduzir ruído;
2. melhorar precisão de ancoragem;
3. ampliar cobertura de paths;
4. só depois mexer no modelo.

## Passo 17 — Hardenização operacional

Depois que o primeiro PR passar bem:

* mantenha o reviewer como advisory;
* não marque como required check;
* não execute em todos os eventos possíveis;
* preserve `ready_for_review` e `synchronize`;
* monitore uso da quota gratuita.

No estágio “zero custo agora”, essa contenção é parte da arquitetura, não detalhe operacional.

## Passo 18 — Documentar o reviewer no repositório

Depois da validação inicial, registre a existência do reviewer na documentação operacional apropriada do projeto, sem tratá-lo como fonte normativa maior que o canon.

A documentação deve dizer:

* objetivo do reviewer;
* caráter advisory;
* paths elegíveis;
* exclusão de derivados;
* comportamento hybrid;
* necessidade do secret `GEMINI_API_KEY`.

## DONE

O reviewer está DONE quando:

* os quatro arquivos existem nos paths finais;
* `actionlint`, parsing YAML e compile Python passam;
* o secret `GEMINI_API_KEY` está configurado;
* um PR real de teste gera review útil;
* o reviewer respeita o modelo contract-driven do HB Track;
* o reviewer não interfere no `contract-gates.yml`;
* o reviewer atua em modo hybrid com inline seguro + summary residual;
* o reviewer permanece zero custo agora.

Resumo final do fluxo operacional:

```text
Passo 0  -> preparar WSL e ferramentas
Passo 1  -> congelar princípios do HB Track
Passo 2  -> garantir paths canônicos
Passo 3  -> fixar modo hybrid
Passo 4  -> configurar config.yaml
Passo 5  -> configurar styleguide.md
Passo 6  -> implementar ai_review_bridge.py
Passo 7  -> ajustar ai-pr-review.yml
Passo 8  -> criar GEMINI_API_KEY
Passo 9  -> instalar dependências Python
Passo 10 -> lint e validação estática
Passo 11 -> revisão humana final
Passo 12 -> commit
Passo 13 -> push em branch dedicada
Passo 14 -> PR de teste controlado
Passo 15 -> classificar PASS / DEGRADED / FAIL
Passo 16 -> tuning fino
Passo 17 -> hardenização operacional
Passo 18 -> documentar
DONE     -> reviewer híbrido validado no HB Track
```

Abaixo está o checklist operacional executável para o `hbtrack/official`, em WSL, no modo Pacote B. O repositório conectado está com PR aberto recente em `main`, então faz sentido validar o reviewer por branch dedicada e PR pequeno, sem encostar no fluxo principal de contratos. O PR aberto mais recente é o `#48` em `hbtrack/official`, ainda não mergeado. Isso reforça a necessidade de isolar a infraestrutura do reviewer numa branch própria.

Use este checklist na ordem.

## 0) Entrar no workspace correto

```bash id="zrrr14"
cd /home/davis/HB-TRACK
pwd
git rev-parse --show-toplevel
git remote -v
git branch --show-current
```

Critério:

* root do repo correto;
* remote do `hbtrack/official`;
* branch atual conhecida.

## 1) Garantir ferramentas no WSL

```bash id="gnhk8o"
sudo apt update
sudo apt install -y gh curl jq python3 python3-pip
```

Instalar `actionlint`:

```bash id="4mzi31"
bash <(curl -fsSL https://raw.githubusercontent.com/rhysd/actionlint/main/scripts/download-actionlint.bash)
sudo mv actionlint /usr/local/bin/
actionlint -version
```

Autenticar `gh` se necessário:

```bash id="pzwk2u"
gh auth status || gh auth login
```

Critério:

* `gh` responde;
* `actionlint` responde;
* Python disponível.

## 2) Criar branch dedicada para a infraestrutura do reviewer

```bash id="ud6dei"
git checkout -b chore/ai-reviewer-hybrid
```

Se a branch já existir:

```bash id="1cw75x"
git checkout chore/ai-reviewer-hybrid
```

Critério:

* nunca fazer isso direto em `main`.

## 3) Confirmar paths finais dos 4 arquivos

```bash id="mjlwm2"
ls -l .github/workflows/ai-pr-review.yml
ls -l .github/ai-review/config.yaml
ls -l .github/ai-review/styleguide.md
ls -l scripts/ai_review_bridge.py
```

Critério:

* os quatro arquivos existem exatamente nesses paths.

## 4) Validar conteúdo mínimo do `config.yaml`

Abra o arquivo e confirme manualmente:

* `mode: hybrid`
* modelo Gemini configurado no YAML, não hardcoded no Python
* `min_severity_to_publish`
* `include` e `exclude`
* exclusão explícita de `generated/**` e `_reports/**`

Validação sintática:

```bash id="hv6s8n"
python3 - <<'PY'
import yaml
p=".github/ai-review/config.yaml"
with open(p, "r", encoding="utf-8") as f:
    data=yaml.safe_load(f)
assert data["review"]["mode"] == "hybrid"
assert "model" in data["review"]
assert "min_severity_to_publish" in data["review"]
assert "include" in data["paths"]
assert "exclude" in data["paths"]
print("config.yaml OK")
PY
```

Critério:

* saída `config.yaml OK`.

## 5) Validar conteúdo mínimo do `styleguide.md`

Verifique manualmente se ele menciona explicitamente:

* HB Track;
* Contract-Driven Development;
* cadeia de autoridade;
* exclusão de derivados;
* português claro;
* proibição de review cosmético.

Checagem rápida:

```bash id="v7vhr8"
grep -n "HB Track" .github/ai-review/styleguide.md
grep -n "Contract-Driven" .github/ai-review/styleguide.md || grep -n "CDD" .github/ai-review/styleguide.md
grep -n "generated/" .github/ai-review/styleguide.md
grep -n "_reports/" .github/ai-review/styleguide.md
grep -n "portugu" .github/ai-review/styleguide.md || true
```

Critério:

* os temas aparecem de forma explícita.

## 6) Validar sintaxe do bridge Python

```bash id="z849z0"
python3 -m py_compile scripts/ai_review_bridge.py
```

Critério:

* nenhum erro de sintaxe.

## 7) Validar se o bridge lê o config, não valores hardcoded

Checagem rápida:

```bash id="6iet1b"
grep -n "config.yaml" scripts/ai_review_bridge.py
grep -n "gemini-" scripts/ai_review_bridge.py || true
```

Interpretação:

* idealmente o script referencia `config.yaml`;
* se houver `gemini-...` hardcoded no Python, corrija antes de seguir.

## 8) Validar o workflow com `actionlint`

```bash id="73m2e4"
actionlint .github/workflows/ai-pr-review.yml
```

Critério:

* sem saída = OK.

Se quiser validar todos os workflows:

```bash id="h85vx8"
actionlint .github/workflows/*.yml
```

## 9) Verificar se o workflow está isolado do pipeline contratual

Abra `.github/workflows/ai-pr-review.yml` e confirme manualmente:

* não altera `contract-gates.yml`;
* não está marcado como required check em branch protection;
* não escreve em `generated/**` ou `_reports/**`;
* só comenta/revisa.

Checagens rápidas:

```bash id="ag8p7u"
grep -n "pull_request" .github/workflows/ai-pr-review.yml
grep -n "ready_for_review" .github/workflows/ai-pr-review.yml || true
grep -n "synchronize" .github/workflows/ai-pr-review.yml || true
grep -n "pull-requests: write" .github/workflows/ai-pr-review.yml
grep -n "GEMINI_API_KEY" .github/workflows/ai-pr-review.yml
```

Critério:

* workflow de PR, permissões mínimas, uso da chave do Gemini.

## 10) Confirmar o secret no GitHub

No navegador:

* `hbtrack/official`
* Settings
* Secrets and variables
* Actions
* verificar se existe `GEMINI_API_KEY`

Critério:

* secret criado.

Não introduza `GH_PAT` agora, a menos que o reviewer falhe por limitação real do `GITHUB_TOKEN`.

## 11) Revisão rápida do modo híbrido

Confirme que o fluxo final é:

* Gemini retorna JSON;
* bridge separa inline e summary;
* workflow publica inline quando a âncora é segura;
* resto vai para review consolidado.

Checagem conceitual:

* se o workflow ainda só publica um body geral e ignora os comentários do bridge, ainda não está fechado.

## 12) Adicionar os arquivos ao git

```bash id="7n5f3y"
git add .github/workflows/ai-pr-review.yml
git add .github/ai-review/config.yaml
git add .github/ai-review/styleguide.md
git add scripts/ai_review_bridge.py
git status --short
```

Critério:

* só os quatro arquivos do reviewer aparecem como staged, ou o conjunto exato que você quer commitar.

## 13) Commitar

```bash id="c1l2ji"
git commit -m "infra(ai-review): add hybrid Gemini PR reviewer for HB Track"
```

Critério:

* commit criado sem erro.

## 14) Push da branch

```bash id="ra8ysd"
git push -u origin chore/ai-reviewer-hybrid
```

Critério:

* branch publicada no GitHub.

## 15) Abrir um PR de teste pequeno

Use uma mudança pequena e soberana. Evite um PR enorme.

Se ainda não existir PR para a branch:

```bash id="v8paul"
gh pr create \
  --repo hbtrack/official \
  --base main \
  --head chore/ai-reviewer-hybrid \
  --title "infra(ai-review): add hybrid Gemini reviewer" \
  --body "PR de validação do reviewer automático híbrido do HB Track."
```

Critério:

* PR criado.

## 16) Fazer o primeiro teste operacional correto

Recomendação:

* se abrir como Draft, depois mover para Ready for review;
* esse é o melhor teste do gatilho sem ruído excessivo.

Se quiser abrir no navegador:

```bash id="rt83mo"
gh pr view --web
```

No GitHub:

* se o PR estiver em draft, clique em “Ready for review”.

## 17) Acompanhar a execução do workflow

Listar runs:

```bash id="j4zk7n"
gh run list --limit 10
```

Ver logs da run mais recente:

```bash id="gfk6yl"
gh run view --log
```

Se quiser filtrar pelo workflow:

```bash id="ny2e17"
gh run list --workflow "ai-pr-review.yml" --limit 10
```

Critério:

* o workflow executa;
* não falha por YAML, sintaxe ou secret ausente.

## 18) Validar comportamento no PR

No PR, confirme:

* review apareceu;
* texto em português;
* sem comentários sobre `generated/**` e `_reports/**`;
* inline comment só onde a âncora faz sentido;
* restante em summary;
* nada cosmético.

Abrir PR no browser:

```bash id="t98l0c"
gh pr view --web
```

## 19) Classificar resultado do primeiro teste

PASS:

* workflow rodou;
* review útil apareceu;
* híbrido funcionou;
* sem ruído em derivados;
* sem interferir no pipeline contratual.

DEGRADED:

* review consolidado saiu, mas inline não;
* houve poucos comentários por excesso de filtro;
* útil, mas conservador demais.

FAIL:

* workflow quebrou;
* secret inválido;
* comentário em derivados;
* comentários desalinhados com o HB Track;
* interferência no `contract-gates`.

## 20) Ajuste fino imediato, se necessário

Se houver ruído:

* aumente `min_severity_to_publish`;
* reduza `max_comments`;
* estreite `include`.

Se houver poucos comentários:

* reduza o threshold;
* aumente `max_files`;
* refine o prompt no `styleguide.md`, não no YAML primeiro.

Se inline falhar demais:

* mantenha `hybrid`;
* endureça a lógica de âncora no bridge;
* não force inline artificialmente.

## 21) Repetir com um PR soberano pequeno real

Depois do PR de infraestrutura, teste o reviewer num PR pequeno real, preferencialmente em:

* `contracts/**`
* `docs/hbtrack/modulos/**/graph/**`
* `.contract_driven/**`

Isso valida o reviewer no coração do modelo CDD do projeto.

## 22) DONE

Considere DONE quando tudo abaixo for verdadeiro:

* os 4 arquivos existem nos paths finais;
* `actionlint` passa;
* `config.yaml` e `styleguide.md` estão aderentes ao HB Track;
* `ai_review_bridge.py` compila e lê a configuração;
* `GEMINI_API_KEY` está configurado;
* a branch foi publicada;
* o PR de teste executou o workflow;
* houve review híbrida útil;
* o reviewer não interferiu no `contract-gates`;
* o reviewer não tratou derivados como soberanos.

Resumo operacional curto:

```text id="e4lxzu"
[ ] Entrar em /home/davis/HB-TRACK
[ ] Garantir gh, actionlint, python3
[ ] Criar/usar branch chore/ai-reviewer-hybrid
[ ] Confirmar os 4 arquivos
[ ] Validar config.yaml
[ ] Validar styleguide.md
[ ] Compilar ai_review_bridge.py
[ ] Rodar actionlint
[ ] Confirmar secret GEMINI_API_KEY
[ ] git add dos 4 arquivos
[ ] git commit
[ ] git push
[ ] gh pr create
[ ] Mover PR para Ready for review
[ ] gh run list / gh run view --log
[ ] Verificar inline + summary no PR
[ ] Classificar PASS / DEGRADED / FAIL
[ ] Ajustar thresholds/path filters se necessário
```


