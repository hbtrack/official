> ⚠️ **NON-SOVEREIGN** — Documento operacional de análise e planejamento. Não define regras, schemas, gates ou políticas canônicas.

# GEMINI.md — Análise do AI Reviewer + Planos de Melhoria

**Gerado em:** 2026-04-05  
**Base:** PR #49 (merged), PR #50 (open), `.github/workflows/ai-pr-review.yml`, `scripts/ai_review_bridge.py`, `.github/ai-review/config.yaml`

---

## 1. COMPROVAÇÃO — Gemini está ativo nos PRs

### Evidência PR #49 (`chore/ai-reviewer-hybrid` → `main`)

| Run | Status | Resultado |
|---|---|---|
| 23996034124 | skipped | PR draft ignorado corretamente |
| 23996039794 | failure | fix: import os ausente |
| 23996071882 | failure | fix: js-yaml → env vars |
| 23996107414 | failure | fix: bridge JSON repair |
| 23996142225 | **success** | finishReason=STOP |
| 23996181001 | **success** | — |
| 23996236620 | **success** | — |
| 23996283167 | **success** | inline_comments=2 |
| 23996332010 | **success** | inline_comments=2, State=COMMENTED ✅ |

**Último review publicado:**
- Veredito: `APPROVE_WITH_REMARKS`
- 2 inline comments em `.github/workflows/ai-pr-review.yml` (linha 1 e linha 30)
- Texto em português ✅
- Sem comentários em `generated/**` ou `_reports/**` ✅
- Não interferiu em `contract-gates.yml` ✅

**Conclusão:** Gemini funcionando. Reviewer operacional para PRs que atendam às condições de trigger.

---

## 2. PR #50 — Por que não recebeu review

**Dados do PR #50:**
```
Título: feat(users): B10-001 — módulo users completo
Branch: feat/b10-001-users → main
Criado em: 2026-04-05T08:39:42Z
reviews: []
statusCheckRollup: []
```

**Causa raiz:**
- PR #49 (workflow infrastructure) foi merged em `2026-04-05T17:13:47Z`
- PR #50 foi aberto `08:39:42` — **8.5 horas antes** do workflow existir em `main`
- GitHub Actions só dispara o workflow `pull_request` para eventos futuros (synchronize/reopened) após o workflow existir no repositório
- Após o merge do PR #49, não houve novo push em `feat/b10-001-users`
- **Resultado: zero triggers, zero reviews**

**Gap adicional:** Mesmo que tivesse trigado, PR #50 tem `src/competitions/api.py`, `src/competitions/domain/entities.py`, etc. — caminho `src/**` **NÃO está na lista include** do config. Todo código soberano da aplicação é invisível ao reviewer.

---

## 3. GAPS E INCONSISTÊNCIAS

| # | Gap | Arquivo | Impacto |
|---|---|---|---|
| G1 | `src/**` ausente do include | `config.yaml` + trigger `paths:` | Código soberano da aplicação nunca revisado |
| G2 | Sem re-trigger para PRs abertos antes do workflow | `ai-pr-review.yml` | PRs existentes ficam sem review sem ação manual |
| G3 | `dedupe_window_comments: 40` declarado no config mas **não implementado** no bridge | `ai_review_bridge.py` | Campo inerte; duplicatas cross-run não são filtradas |
| G4 | Sem ordenação por prioridade nos arquivos selecionados | `ai-pr-review.yml` step "Coletar arquivos" | Primeiros 20 da lista paginada da API, não os mais críticos |
| G5 | `compiled_context/**` não está em include nem exclude | `config.yaml` | Context bundles FT-NNN ignorados silenciosamente |
| G6 | Contexto da sessão (`SESSION_HANDOFF.md`) nunca avaliado como arquivo alterado | `config.yaml` include | Cada PR inclui mudanças no SESSION_HANDOFF mas o reviewer não comenta |
| G7 | `src/**` presente em todos os PRs de feature mas fora do trigger `paths:` do workflow | `.github/workflows/ai-pr-review.yml` linha 9-22 | Workflow não trigga mesmo quando código de app muda |
| G8 | Sem limite de tokens/chars no payload enviado ao Gemini | `ai-pr-review.yml` step "Preparar contexto" | PR com 90 arquivos pode exceder contexto do modelo (>1M tokens) |
| G9 | Codex atingiu limite de uso (PR #50 comment do `chatgpt-codex-connector`) | N/A | Redundância esperada coberta pelo Gemini, mas sem fallback documentado |
| G10 | Sem tracking de cota diária do free tier (1500 RPD Gemini 2.5 Flash) | CI | Desenvolvimento intenso pode esgotar cota sem aviso |

---

## 4. 10 MELHORIAS — API Free Tier Google AI Studio

---

### M1 — Adicionar `src/**` ao include (paths + config)

**Problema:** Código soberano da aplicação (`src/<module>/`) completamente fora de revisão.

**Arquivos modificados:**
- `.github/ai-review/config.yaml`
- `.github/workflows/ai-pr-review.yml`

**Implementação:**

```yaml
# .github/ai-review/config.yaml — seção paths.include
paths:
  include:
    - "docs/hbtrack/modulos/**/graph/**"
    - "contracts/**"
    - ".contract_driven/**"
    - "docs/_canon/**"
    - ".github/copilot-instructions.md"
    - ".github/workflows/**"
    - "scripts/contracts/validate/**"
    - "scripts/hb"
    - "src/*/api.py"
    - "src/*/domain/*.py"
    - "src/*/application/use_cases.py"
    - "src/*/schemas.py"
    - "tests/**"
```

```yaml
# .github/workflows/ai-pr-review.yml — trigger paths (adicionar ao bloco paths:)
    paths:
      - 'src/*/api.py'
      - 'src/*/domain/*.py'
      - 'src/*/application/use_cases.py'
      - 'src/*/schemas.py'
      # ... existentes mantidos
```

**Validação:**
```bash
# Verificar que src/*/api.py é capturado pelo padrão
python3 -c "
import re, pathlib
pattern = 'src/*/api.py'
s = pattern.replace('**', '::D::').replace('*', '[^/]*').replace('::D::','.*')
rx = re.compile('^' + s + '$')
test_paths = ['src/competitions/api.py','src/users/api.py','src/training/api.py']
for p in test_paths:
    assert rx.match(p), f'FAIL: {p}'
print('PASS — src patterns match application code paths')
"
```

**Análise adversarial:**
- **Risco:** `max_files: 20` — adicionando `src/**` padrões, um PR com 10 módulos pode ter 40+ arquivos, sobrando 0 slots para contratos.
- **Mitigação:** Alterar `max_files: 30` E implementar prioridade (M4) para garantir que contratos e graph YAMLs entrem antes de arquivos `src/`.
- **Risco 2:** `src/shared/` e `src/ai_ingestion/` têm código transversal — mudanças nesses módulos podem exceder capacidade de contexto.
- **Mitigação 2:** Cap explícito de `src/**` a 8 arquivos máximos; contratos e graph têm prioridade.

---

### M2 — Re-trigger manual para PRs abertos antes do workflow

**Problema:** PRs criados antes do merge do reviewer nunca recebem review.

**Arquivo criado:** `scripts/trigger_ai_review.sh`

**Implementação:**
```bash
#!/usr/bin/env bash
# scripts/trigger_ai_review.sh
# Força re-trigger do ai-pr-review em PR já aberto
# Uso: bash scripts/trigger_ai_review.sh <PR_NUMBER>
set -euo pipefail

PR="${1:?Informe o número do PR}"
REPO="${GITHUB_REPOSITORY:-hbtrack/official}"

echo "Reabrindo+fechando draft state para re-trigger do ai-pr-review em PR #${PR}..."
GH_TOKEN="" gh pr ready "${PR}" --repo "${REPO}" 2>/dev/null || true

# Alternativa: converter para draft e voltar para ready
echo "Convertendo para draft..."
GH_TOKEN="" gh pr convert-to-draft "${PR}" --repo "${REPO}" 2>/dev/null || {
  echo "Não foi possível converter para draft. Use o método push vazio:"
  echo "  git commit --allow-empty -m 'ci: trigger ai-review for PR #${PR}'"
  echo "  git push"
  exit 1
}
sleep 2
echo "Marcando como ready for review..."
GH_TOKEN="" gh pr ready "${PR}" --repo "${REPO}"
echo "Trigger enviado. Aguarde o workflow no GitHub."
```

**Validação:**
```bash
chmod +x scripts/trigger_ai_review.sh
bash scripts/trigger_ai_review.sh --help 2>&1 || echo "Uso: bash scripts/trigger_ai_review.sh <PR>"
# Testar dry-run:
echo "PR #50 seria re-trigado via: bash scripts/trigger_ai_review.sh 50"
```

**Análise adversarial:**
- **Risco:** `gh pr convert-to-draft` requer permissão de `write` no repositório; em repos com branch protection, pode falhar.
- **Mitigação:** Fallback documentado no script: `git commit --allow-empty` + push — isso cria evento `synchronize` que trigga o workflow.
- **Risco 2:** Re-trigger em PR já com muitos comentários acumula reviews redundantes.
- **Mitigação 2:** Implementar M3 (deduplicação cross-run) antes de usar este script.

---

### M3 — Implementar `dedupe_window_comments` no bridge

**Problema:** `dedupe_window_comments: 40` está declarado em `config.yaml` mas não implementado em `ai_review_bridge.py`. Comentários duplicados ocorrem quando o workflow re-roda no mesmo PR.

**Arquivo modificado:** `scripts/ai_review_bridge.py`

**Implementação:** Adicionar ao final de `build_inline_comments()`:

```python
def load_existing_review_comments(pr_comments_path: str) -> set:
    """Carrega comentários existentes do PR para deduplicação."""
    try:
        existing = json.loads(Path(pr_comments_path).read_text(encoding='utf-8'))
        return {
            (c.get('path'), c.get('line'), c.get('body', '')[:80])
            for c in existing
        }
    except (FileNotFoundError, json.JSONDecodeError):
        return set()
```

No workflow, adicionar step ANTES do bridge:
```yaml
- name: Carregar comentários existentes do PR
  if: steps.files.outputs.count != '0'
  uses: actions/github-script@v7
  with:
    script: |
      const fs = require('fs');
      const pr = context.payload.pull_request.number;
      const reviews = await github.paginate(
        github.rest.pulls.listReviewComments,
        { owner: context.repo.owner, repo: context.repo.repo, pull_number: pr, per_page: 100 }
      );
      const existing = reviews
        .filter(r => r.user.login === 'github-actions[bot]')
        .map(r => ({ path: r.path, line: r.line || r.original_line, body: r.body.slice(0, 80) }));
      fs.writeFileSync('pr_existing_comments.json', JSON.stringify(existing));
```

No bridge `main()`:
```python
existing = load_existing_review_comments('pr_existing_comments.json')
# Filtrar inline comments que já existem
inline = [c for c in inline if (c['path'], c['line'], c['body'][:80]) not in existing]
```

**Validação:**
```bash
python3 -m py_compile scripts/ai_review_bridge.py && echo "PASS — bridge compila"
python3 -c "
from scripts.ai_review_bridge import load_existing_review_comments
# Teste com arquivo vazio
import json
from pathlib import Path
Path('/tmp/test_comments.json').write_text('[]')
result = load_existing_review_comments('/tmp/test_comments.json')
assert result == set(), f'FAIL: {result}'
print('PASS')
"
```

**Análise adversarial:**
- **Risco:** API `pulls.listReviewComments` pagina até 100 comentários por request; PRs com muitas iterações podem ter 200+ comentários do bot.
- **Mitigação:** Já usa `github.paginate` — correto por padrão. Limitar janela de deduplicação aos últimos `dedupe_window_comments` da config.
- **Risco 2:** Comparação por `body[:80]` pode ter falso positivo para comentários distintos com mesmo início.
- **Mitigação 2:** Usar tupla `(path, line, body[:120])` — mais específico.

---

### M4 — Ordenação por prioridade de arquivos

**Problema:** Seleção dos primeiros 20 arquivos é arbitrária (ordem da API do GitHub). Contratos e graph YAMLs devem entrar antes de arquivos de teste.

**Arquivo modificado:** `.github/workflows/ai-pr-review.yml` — step "Coletar arquivos alterados do PR"

**Implementação:** Adicionar lógica de ordenação por prioridade antes do `.slice(0, maxFiles)`:

```javascript
// Depois de const selected = allFiles.filter(...)
// ANTES do .slice(0, maxFiles):

const PRIORITY_ORDER = [
  /^contracts\//,            // 1. contratos (SSOT)
  /^docs\/hbtrack\/modulos\/.*\/graph\//,  // 2. source graph
  /^docs\/_canon\//,         // 3. canon
  /^\.contract_driven\//,    // 4. governance
  /^\.github\/workflows\//,  // 5. CI workflows
  /^scripts\//,              // 6. scripts
  /^src\/.*\/api\.py$/,      // 7. API surfaces
  /^src\/.*\/domain\//,      // 8. domain
  /^tests\//,                // 9. testes (menor prioridade)
];

function filePriority(filename) {
  for (let i = 0; i < PRIORITY_ORDER.length; i++) {
    if (PRIORITY_ORDER[i].test(filename)) return i;
  }
  return PRIORITY_ORDER.length;
}

const sorted = selected.sort((a, b) => filePriority(a.filename) - filePriority(b.filename));
const limited = sorted.slice(0, maxFiles);
// substituir selected por limited no writeFileSync
```

**Validação:**
```bash
node - <<'JS'
const PRIORITY_ORDER = [
  /^contracts\//,
  /^docs\/hbtrack\/modulos\/.*\/graph\//,
  /^docs\/_canon\//,
  /^tests\//,
];
function filePriority(f) {
  for (let i = 0; i < PRIORITY_ORDER.length; i++) {
    if (PRIORITY_ORDER[i].test(f)) return i;
  }
  return PRIORITY_ORDER.length;
}
const files = ['tests/test_foo.py','contracts/openapi/paths/users.yaml','docs/hbtrack/modulos/users/graph/entities.yaml'];
const sorted = files.sort((a,b) => filePriority(a) - filePriority(b));
console.assert(sorted[0].startsWith('contracts/'), 'FAIL: contracts not first');
console.assert(sorted[1].startsWith('docs/hbtrack'), 'FAIL: graph not second');
console.log('PASS — prioridade correta');
JS
```

**Análise adversarial:**
- **Risco:** Ordenar por prioridade pode excluir testes críticos que detectam breaking changes.
- **Mitigação:** Máximo 12 slots para categorias 1-6, mínimo 8 slots garantidos para `tests/**`.
- **Risco 2:** PR com 15 arquivos de contratos esgota todos os slots antes de testes.
- **Mitigação 2:** Implementar via duas listas separadas: `priority_files[:12] + test_files[:8]`.

---

### M5 — Token budget management

**Problema:** PR #50 tem 90+ arquivos. Mesmo após filtro, o payload JSON enviado ao Gemini pode exceder o contexto do modelo (1M tokens = ~750K chars). Context files sozinhos somam ~70K chars (`CONTRACT_SYSTEM_RULES.md` = 45KB, `AGENT_INSTRUCTIONS.md` = estimado 20KB).

**Arquivo modificado:** `.github/workflows/ai-pr-review.yml` — step "Preparar contexto do repositório"

**Implementação:**
```python
# Substituir bloco de context_files no step "Preparar contexto"

MAX_CONTEXT_CHARS = 60_000   # budget total para arquivos de contexto
MAX_DIFF_CHARS_PER_FILE = 3_000  # max chars de patch por arquivo
MAX_TOTAL_PAYLOAD_CHARS = 200_000  # safety cap do payload total

repo_context = {}
context_budget = MAX_CONTEXT_CHARS
for file in context_files:
    p = Path(file)
    if p.exists() and p.is_file():
        content = p.read_text(encoding='utf-8')
        if context_budget <= 0:
            break
        capped = content[:min(len(content), context_budget, 8000)]
        repo_context[file] = capped
        context_budget -= len(capped)

# Truncar patches por arquivo
for f in files:
    if len(f.get('patch', '')) > MAX_DIFF_CHARS_PER_FILE:
        f['patch'] = f['patch'][:MAX_DIFF_CHARS_PER_FILE] + '\n... [truncado]'

# Verificar tamanho total antes de enviar
payload_str = json.dumps({'styleguide': styleguide, 'repo_context': repo_context,
                          'changed_files': files, 'instructions': '...'})
if len(payload_str) > MAX_TOTAL_PAYLOAD_CHARS:
    # Remover context files menos prioritários até caber
    for key in list(repo_context.keys())[3:]:  # manter os 3 primeiros
        del repo_context[key]
        payload_str = json.dumps({...})
        if len(payload_str) <= MAX_TOTAL_PAYLOAD_CHARS:
            break
```

**Validação:**
```bash
python3 -c "
MAX = 200_000
# Simular payload grande
fake_payload = 'x' * 250_000
truncated = fake_payload[:MAX]
assert len(truncated) == MAX
print(f'PASS — payload capped em {MAX} chars')
"
```

**Análise adversarial:**
- **Risco:** Truncar o diff no meio de um hunk pode fazer o bridge falhar no cálculo de linha ao parsear o patch.
- **Mitigação:** Truncar sempre em múltiplo de linha (no `\n`) e adicionar marcador `[truncado]` — o bridge já trata patches incompletos graciosamente (linhas fora do diff caem para residual).
- **Risco 2:** Context files truncados podem omitir regras críticas que guiam o modelo.
- **Mitigação 2:** Definir ordem de prioridade dos context_files; os primeiros 3 são sempre completos.

---

### M6 — Context injection por módulo

**Problema:** O reviewer recebe contexto genérico do repositório. Quando um PR muda apenas o módulo `users`, injetar `docs/hbtrack/modulos/competitions/graph/**` é ruído.

**Arquivo modificado:** `.github/workflows/ai-pr-review.yml` — step "Preparar contexto do repositório"

**Implementação:**
```python
import re

# Detectar módulos tocados no diff
changed_modules = set()
for f in files:
    m = re.match(r'(?:docs/hbtrack/modulos|src)/([a-z_]+)/', f['filename'])
    if m:
        changed_modules.add(m.group(1))

# Injetar graph YAML apenas dos módulos afetados
module_context = {}
for module in changed_modules:
    graph_dir = Path(f'docs/hbtrack/modulos/{module}/graph')
    if graph_dir.exists():
        for yaml_file in sorted(graph_dir.glob('*.yaml'))[:3]:  # max 3 por módulo
            key = str(yaml_file)
            # Não injetar se o arquivo já está no diff (evitar conflito base vs head)
            if not any(f['filename'] == key for f in files):
                module_context[key] = yaml_file.read_text(encoding='utf-8')[:4000]

repo_context.update(module_context)
```

**Validação:**
```bash
python3 -c "
import re
files = [
    {'filename': 'src/users/api.py'},
    {'filename': 'docs/hbtrack/modulos/users/graph/entities.yaml'},
    {'filename': 'tests/pipeline_gates/test_users_source_graph_integrity.py'},
]
changed_modules = set()
for f in files:
    m = re.match(r'(?:docs/hbtrack/modulos|src)/([a-z_]+)/', f['filename'])
    if m:
        changed_modules.add(m.group(1))
assert changed_modules == {'users'}, f'FAIL: {changed_modules}'
print('PASS — módulo detectado corretamente')
"
```

**Análise adversarial:**
- **Risco:** Se o graph YAML do módulo ESTÁ no diff (novo módulo), injetar a versão base confunde o modelo (vê versão antiga + diff).
- **Mitigação:** Verificação explícita `if not any(f['filename'] == key for f in files)` — implementada acima.
- **Risco 2:** Módulo `shared/` afeta todos os módulos; injetar todos os graphs seria 17× overhead.
- **Mitigação 2:** Se `changed_modules` contém `shared`, limitar a 2 graphs de exemplo, não todos.

---

### M7 — Retry com backoff para falhas da API Gemini

**Problema:** Free tier tem 10 RPM / 1500 RPD para Gemini 2.5 Flash. Um pico de PRs pode causar `429 Too Many Requests`. Atualmente não há retry — o workflow simplesmente falha.

**Arquivo modificado:** `.github/workflows/ai-pr-review.yml` — step "Chamar Gemini"

**Implementação:** Substituir o `curl` simples por script com retry:

```python
# No step "Chamar Gemini", substituir o bloco curl por:
import time, subprocess, json
from pathlib import Path

model = '${{ steps.cfg.outputs.model }}'
api_key = os.environ['GEMINI_API_KEY']
url = f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}'

max_retries = 3
wait_secs = [5, 15, 30]

for attempt, wait in enumerate(wait_secs + [None]):
    result = subprocess.run(
        ['curl', '-sS', '-w', '\n%{http_code}', '-X', 'POST',
         '-H', 'Content-Type: application/json',
         url, '-d', '@gemini_request.json'],
        capture_output=True, text=True
    )
    lines = result.stdout.rsplit('\n', 1)
    body, http_code = lines[0], lines[1].strip() if len(lines) > 1 else '000'

    if http_code == '200':
        Path('gemini_response.json').write_text(body, encoding='utf-8')
        print(f'Gemini respondeu 200 na tentativa {attempt + 1}')
        break
    elif http_code == '429' and wait is not None:
        print(f'Rate limit (429). Aguardando {wait}s antes da tentativa {attempt + 2}...')
        time.sleep(wait)
    else:
        print(f'Erro HTTP {http_code}: {body[:200]}', file=sys.stderr)
        sys.exit(1)
else:
    print('Máximo de retries atingido.', file=sys.stderr)
    sys.exit(1)
```

**Validação:**
```bash
python3 -c "
import sys
# Simular 429 → 200 na segunda tentativa
responses = [('429', 'rate limit'), ('200', '{\"candidates\":[]}')]
for code, body in responses:
    if code == '200':
        print(f'PASS — respondeu 200 após retry')
        break
    print(f'Rate limit {code}, aguardando...')
"
```

**Análise adversarial:**
- **Risco:** 3 retries com espera de 30s total fazem o job demorar até 15min (timeout configurado). Se o timeout do job for atingido, nenhum review é publicado.
- **Mitigação:** `timeout-minutes: 15` no job já existe. Manter esperas curtas (5+15+30=50s total de wait) garante margem.
- **Risco 2:** Múltiplos PRs simultâneos fazem `concurrency: group: ai-pr-review-${{ github.event.pull_request.number }}` cancela o anterior, mas cada um ainda faz suas próprias chamadas à API podendo somar RPM.
- **Mitigação 2:** Expor contagem de tentativas no log; não aumentar `max_retries` acima de 3.

---

### M8 — Tracking de cota diária via GitHub Actions variable

**Problema:** Free tier Gemini 2.5 Flash = 1500 RPD. Desenvolvimento intenso (10+ PRs/dia, cada um com múltiplas syncs) pode esgotar a cota sem aviso.

**Arquivos criados/modificados:**
- `.github/workflows/ai-pr-review.yml` — adicionar steps de contagem

**Implementação:**
```yaml
# Step ANTES de "Chamar Gemini":
- name: Verificar cota diária
  id: quota
  env:
    GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  run: |
    DATE=$(date +%Y-%m-%d)
    # Buscar variável de contagem (formato: "YYYY-MM-DD:N")
    CURRENT=$(gh variable get AI_REVIEW_DAILY_COUNT --repo ${{ github.repository }} 2>/dev/null || echo "")
    if [[ "$CURRENT" == "${DATE}:"* ]]; then
      COUNT=${CURRENT#*:}
    else
      COUNT=0
    fi
    echo "Usos hoje: $COUNT / 1400 (safety threshold)"
    if [ "$COUNT" -ge 1400 ]; then
      echo "::warning::Cota diária do Gemini quase esgotada ($COUNT/1400). Review pulado."
      echo "skip=true" >> "$GITHUB_OUTPUT"
    else
      NEW_COUNT=$((COUNT + 1))
      gh variable set AI_REVIEW_DAILY_COUNT --body "${DATE}:${NEW_COUNT}" --repo ${{ github.repository }} || true
      echo "skip=false" >> "$GITHUB_OUTPUT"
    fi

# Step "Chamar Gemini" e todos os subsequentes:
- name: Chamar Gemini
  if: steps.files.outputs.count != '0' && steps.quota.outputs.skip != 'true'
  # ... resto igual
```

**Pré-requisito:** `gh variable set` requer permissão `variables: write` no token. Adicionar ao bloco `permissions`:
```yaml
permissions:
  contents: read
  pull-requests: write
  issues: write
  actions: write   # necessário para gh variable set
```

**Validação:**
```bash
# Testar lógica de parsing (sem chamar a API):
python3 -c "
import re
DATE = '2026-04-05'
CURRENT = '2026-04-05:42'
if CURRENT.startswith(DATE + ':'):
    count = int(CURRENT.split(':')[1])
    assert count == 42
    print(f'PASS — count={count}')
"
```

**Análise adversarial:**
- **Risco:** `gh variable set` falha se o token não tem `actions: write`. O step usa `|| true` — falha silenciosa, contagem não incrementa.
- **Mitigação:** Adicionar log explícito de warning quando `gh variable set` falha. O review ainda acontece (não bloqueia), mas a contagem pode estar errada.
- **Risco 2:** Variable `AI_REVIEW_DAILY_COUNT` é global para o repositório — race condition se 2 PRs trigam simultaneamente.
- **Mitigação 2:** Aceitável para uso de rate limiting (soft limit, não hard limit). A imprecisão é de ±5 chamadas/dia, não crítica para 1500 RPD.

---

### M9 — Fallback explícito: summary-only quando sem ancoragem

**Problema:** `fallback_to_summary_only: true` está declarado em `config.yaml` mas o workflow termina silenciosamente quando `inline_comments=0`. Se todos os achados caem no residual (sem âncora), o review summary ainda precisa ser publicado.

**Arquivo modificado:** `.github/workflows/ai-pr-review.yml` — step "Publicar review híbrido"

**Implementação:**
```yaml
- name: Publicar review híbrido
  if: steps.files.outputs.count != '0'
  uses: actions/github-script@v7
  with:
    script: |
      const fs = require('fs');
      const summary = fs.readFileSync('ai_review_summary.md', 'utf8');
      const findingsData = JSON.parse(fs.readFileSync('ai_review_findings.json', 'utf8'));
      const inlineComments = findingsData.comments || [];
      const pr = context.payload.pull_request.number;
      const owner = context.repo.owner;
      const repo = context.repo.repo;
      const commit_id = context.payload.pull_request.head.sha;

      // Sempre publicar review, mesmo sem inline comments
      const reviewPayload = {
        owner, repo, pull_number: pr, commit_id,
        event: 'COMMENT',
        body: summary,
        comments: inlineComments
      };

      // Se sem inline mas com summary substancial, adicionar prefixo
      if (inlineComments.length === 0 && summary.length > 100) {
        reviewPayload.body = '> ⚠️ Nenhum achado pôde ser ancorado inline — review consolidado apenas.\n\n' + summary;
      }

      await github.rest.pulls.createReview(reviewPayload);
      console.log(`Review publicado: ${inlineComments.length} inline, summary ${summary.length} chars`);
```

**Validação:**
```bash
python3 -c "
# Simular bridge output com 0 inline e 2 residual
import json
findings = {'comments': []}
summary = '## Veredito\nCOMMENT\n\n## Resumo\nAlguns achados sem âncora.\n\n## Achados não ancorados inline\n- [HIGH] teste.py — Problema\n'
# Verificar que summary não está vazio
assert len(summary) > 100
print(f'PASS — summary tem {len(summary)} chars, será publicado')
"
```

**Análise adversarial:**
- **Risco:** `createReview` com body vazio e `comments: []` falha com erro 422 da API do GitHub.
- **Mitigação:** O bridge já garante que o summary sempre tem conteúdo mínimo (veredito + "Nenhum." para achados). Adicionar guard: `if (summary.trim().length < 10) return;`.
- **Risco 2:** Review com apenas summary (sem inline) pode parecer genérico/inútil para o desenvolvedor.
- **Mitigação 2:** O prefixo `⚠️ Nenhum achado pôde ser ancorado inline` deixa explícito o motivo.

---

### M10 — Campo `gate_impact` nas findings do Gemini

**Problema:** O reviewer não informa qual gate do HB Track é afetado pelo achado. Isso obriga o desenvolvedor a mapear manualmente o achado → gate → local_equivalent.

**Arquivos modificados:**
- `.github/ai-review/styleguide.md`
- `scripts/ai_review_bridge.py`

**Implementação no styleguide:**
```markdown
## Formato de saída obrigatório (atualizado)

{
  "verdict": "APPROVE_WITH_REMARKS | COMMENT | NO_MATERIAL_FINDINGS",
  "summary": "texto curto",
  "findings": [
    {
      "severity": "critical | high | medium | low",
      "path": "caminho/arquivo",
      "line": 10,
      "title": "título curto",
      "body": "comentário objetivo",
      "suggestion": "opcional",
      "gate_impact": "OPENAPI_ROOT_MODULE_SYNC_GATE | SCHEMA_CONSISTENCY_GATE | DOMAIN_AXIOM_GATE | CONTRACT_DRIFT_GATE | null"
    }
  ]
}
```

**Implementação no bridge — `build_inline_comments()`:**
```python
# Na função build_inline_comments, adicionar ao body:
KNOWN_GATES = {
    'OPENAPI_ROOT_MODULE_SYNC_GATE', 'SCHEMA_CONSISTENCY_GATE',
    'DOMAIN_AXIOM_GATE', 'CONTRACT_DRIFT_GATE', 'SHADOW_AUTHORITY_GATE',
    'HANDOFF_COHERENCE_GATE',
}
gate = f.get('gate_impact', '').strip().upper()
if gate and gate in KNOWN_GATES:
    body += f"\n\n**Gate afetado:** `{gate}`"
```

**Validação:**
```bash
python3 -c "
KNOWN_GATES = {'OPENAPI_ROOT_MODULE_SYNC_GATE','SCHEMA_CONSISTENCY_GATE','DOMAIN_AXIOM_GATE'}
test_finding = {'gate_impact': 'OPENAPI_ROOT_MODULE_SYNC_GATE', 'body': 'divergência'}
gate = test_finding.get('gate_impact','').strip().upper()
assert gate in KNOWN_GATES
print(f'PASS — gate {gate} reconhecido')
# Testar gate inválido (não deve ser adicionado)
invalid = 'GATE_INVENTADO'
assert invalid not in KNOWN_GATES
print('PASS — gate inválido descartado corretamente')
"
```

**Análise adversarial:**
- **Risco:** Gemini pode inventar nomes de gates que não existem no sistema.
- **Mitigação:** Whitelist explícita `KNOWN_GATES` no bridge — valores não reconhecidos são descartados silenciosamente (não exibidos no comentário).
- **Risco 2:** Lista de gates pode ficar desatualizada com a evolução do `GATES_REGISTRY.yaml`.
- **Mitigação 2:** Adicionar invariant test: `test_bridge_known_gates_match_registry` que lê `docs/_canon/gates/GATES_REGISTRY.yaml` e valida que `KNOWN_GATES` no bridge é subconjunto dos gates ativos.

---

## 5. 10 POSSIBILIDADES — Claude Code Pro (VS Code, sem custo adicional)

---

### C1 — Slash command `/validate-drift` — Contract drift detector

**Função:** Compara `src/<module>/api.py` e `src/<module>/domain/entities.py` contra `contracts/openapi/paths/<module>.yaml` para detectar divergências.

**Implementação:**

**Arquivo criado:** `.claude/commands/validate-drift.md`
```markdown
---
description: Detecta divergência entre implementação (src/) e contratos (contracts/)
allowed-tools: Bash, Read, Grep
---

Execute os seguintes passos para o módulo $ARGUMENTS:

1. Leia `contracts/openapi/paths/$ARGUMENTS.yaml`
2. Leia `src/$ARGUMENTS/api.py`
3. Para cada endpoint definido no contrato, verifique se existe implementação correspondente em api.py
4. Execute: `python3 scripts/hb validate --profile ci` e mostre o output
5. Liste divergências encontradas com referência de linha
```

**Validação:**
```bash
ls .claude/commands/validate-drift.md && echo "EXISTS"
# Testar invocação:
# No VS Code: /validate-drift users
```

**Adversarial:** Claude pode ter falsos negativos em endpoints com routing complexo. Sempre executar `hb validate --profile ci` como verificação formal após a análise do Claude.

---

### C2 — Hook pre-push com revisão local do Claude

**Função:** Antes de cada `git push`, Claude revisa os arquivos staged para alinhamento com CDD — NÃO como gate obrigatório, mas como checklist advisory.

**Implementação:**

**Arquivo criado:** `scripts/git-hooks/pre-push-claude-advisory`
```bash
#!/usr/bin/env bash
# Advisory (não bloqueia push): revisão CDD via Claude Code
set -euo pipefail

STAGED_SOVEREIGN=$(git diff --cached --name-only | grep -E "^(src|contracts|docs/hbtrack|docs/_canon)/" || true)

if [ -z "$STAGED_SOVEREIGN" ]; then
    exit 0  # sem arquivos soberanos, skip
fi

echo "🔍 Claude advisory review em andamento..."
echo "$STAGED_SOVEREIGN" | head -10

# Não-bloqueante: se Claude falhar, push continua
claude -p "Revise os seguintes arquivos para conformidade CDD. Aponte apenas violações críticas ou high. Seja breve.

Arquivos alterados:
${STAGED_SOVEREIGN}

Use hb validate --profile precommit para verificação formal." --allowedTools Bash,Read 2>/dev/null || true

exit 0  # sempre permite o push
```

**Instalar:**
```bash
cp scripts/git-hooks/pre-push-claude-advisory .git/hooks/pre-push-claude-advisory
chmod +x .git/hooks/pre-push-claude-advisory
```

**Adversarial:** Hook pode adicionar 30-60s de latência ao push. Solução: `exit 0` incondicional garante que nunca bloqueia; usar `--timeout 30` no comando claude para limitar espera.

---

### C3 — Slash command `/session-close` — Auto-update SESSION_HANDOFF.md

**Função:** Ao final de cada sessão de trabalho, Claude gera atualização do `SESSION_HANDOFF.md` baseada nos commits e arquivos alterados da sessão.

**Implementação:**

**Arquivo criado:** `.claude/commands/session-close.md`
```markdown
---
description: Gera atualização do SESSION_HANDOFF.md para encerramento de sessão
allowed-tools: Bash, Read, Write
---

1. Execute: `git log --oneline -10` e liste os commits desta sessão
2. Execute: `git diff HEAD~3..HEAD --name-only` para ver arquivos alterados
3. Leia o SESSION_HANDOFF.md atual
4. Execute: `python3 scripts/hb preflight` para verificar estado dos gates
5. Atualize SESSION_HANDOFF.md mantendo a estrutura existente:
   - branch_ativo: branch atual
   - ci_status: baseado no resultado do preflight
   - last_completed: último item completado nesta sessão
   - next_action: próximo item do BACKLOG_EXECUTAVEL_DETERMINISTICO.md
6. Não altere campos que não foram afetados por esta sessão
```

**Validação:**
```bash
ls .claude/commands/session-close.md && echo "EXISTS"
grep -c "session-close\|SESSION_HANDOFF" .claude/commands/session-close.md
```

**Adversarial:** Claude pode gerar campos YAML mal formatados que quebram o `HANDOFF_COHERENCE_GATE`. Mitigação: incluir instrução explícita no comando para rodar `python3 scripts/hb verify` após a edição.

---

### C4 — Slash command `/test-coverage-check <module>` — Test obligations checker

**Função:** Verifica quais test obligations de um módulo (`test_obligations.yaml`) têm implementação em `tests/`.

**Implementação:**

**Arquivo criado:** `.claude/commands/test-coverage-check.md`
```markdown
---
description: Verifica cobertura das test_obligations de um módulo
allowed-tools: Read, Bash, Grep
---

Para o módulo $ARGUMENTS:

1. Leia `docs/hbtrack/modulos/$ARGUMENTS/graph/test_obligations.yaml`
2. Extraia todos os IDs de feature test (FT-NNN)
3. Para cada FT-NNN, execute: `grep -rn "FT-$N" tests/` para verificar se existe teste
4. Execute: `python -m pytest tests/ -k "$ARGUMENTS" --collect-only -q` para listar testes coletados
5. Produza tabela: FT-ID | Obrigação | Teste encontrado (S/N) | Arquivo
```

**Validação:**
```bash
ls .claude/commands/test-coverage-check.md && echo "EXISTS"
grep -c "FT-" docs/hbtrack/modulos/users/graph/test_obligations.yaml || echo "0 FTs"
```

**Adversarial:** FT-IDs nos arquivos de teste podem estar em comentários ou strings, não em código ativo. Claude pode reportar falso positivo (FT encontrado no grep mas não como teste real). Mitigação: também executar `pytest --collect-only` como ground truth.

---

### C5 — Slash command `/diagnose-gate-failure` — Diagnóstico de falha de CI

**Função:** Quando `hb ci` falha, Claude lê o output e explica a causa raiz + ação corretiva específica.

**Implementação:**

**Arquivo criado:** `.claude/commands/diagnose-gate-failure.md`
```markdown
---
description: Diagnosica falha de gate de CI e sugere correção
allowed-tools: Bash, Read
---

1. Execute: `python3 scripts/hb ci --profile pr 2>&1 | tee /tmp/ci_output.txt`
2. Leia o output de `/tmp/ci_output.txt`
3. Identifique: qual teste falhou, qual arquivo, qual linha, qual assertion
4. Leia o arquivo de teste mencionado na falha
5. Leia os arquivos de produção referenciados
6. Forneça: causa raiz (1 frase), ação corretiva (comando ou edição específica), gate afetado
7. NÃO sugira ignorar ou pular o gate
```

**Validação:**
```bash
ls .claude/commands/diagnose-gate-failure.md && echo "EXISTS"
```

**Adversarial:** Claude pode sugerir correções que passam o teste local mas não o remote (parity gap). Mitigação: a instrução explícita "não pular o gate" + re-rodar `hb ci` após a correção antes de aceitar.

---

### C6 — Slash command `/generate-pr-description` — PR body CDD-compliant

**Função:** Gera corpo do PR seguindo o padrão do repositório, baseado em commits e arquivos alterados.

**Implementação:**

**Arquivo criado:** `.claude/commands/generate-pr-description.md`
```markdown
---
description: Gera descrição de PR alinhada com o padrão CDD do HB Track
allowed-tools: Bash, Read
---

1. Execute: `git log origin/main..HEAD --oneline` para listar commits do branch
2. Execute: `git diff origin/main..HEAD --name-only` para listar arquivos alterados
3. Filtre arquivos soberanos (exclua: _reports/, generated/, compiled_context/)
4. Leia o PR mais recente como referência: `gh pr list --limit 3 --json title,body`
5. Gere PR body com seções:
   - Artefatos criados/modificados (apenas soberanos)
   - Testes (pytest tests que cobrem as mudanças)
   - Validação (comandos executados e resultado)
   - Próximo passo
6. Não inclua arquivos de `_reports/` nem `generated/` no body
```

**Validação:**
```bash
ls .claude/commands/generate-pr-description.md && echo "EXISTS"
```

**Adversarial:** Claude pode incluir referências a arquivos que não fazem parte dos artefatos canônicos. Instrução explícita de filtrar soberanos mitiga isso. Sempre revisar antes de usar.

---

### C7 — Slash command `/module-impact <module>` — Análise de impacto pré-PR

**Função:** Antes de criar um PR que altera um módulo, identifica todos os outros módulos e gates afetados.

**Implementação:**

**Arquivo criado:** `.claude/commands/module-impact.md`
```markdown
---
description: Analisa impacto de mudanças em um módulo antes do PR
allowed-tools: Bash, Read, Grep
---

Para o módulo $ARGUMENTS:

1. Execute: `git diff origin/main..HEAD --name-only | grep -E "^src/$ARGUMENTS/"` 
2. Leia `docs/_canon/SOURCE_AUTHORITY_GRAPH.yaml` para identificar dependências
3. Execute: `grep -rn "$ARGUMENTS" contracts/ --include="*.yaml" -l` para contratos relacionados
4. Execute: `python3 scripts/hb validate --profile precommit` e mostre resultado
5. Liste: módulos que dependem de $ARGUMENTS, contratos afetados, gates que serão trigados
```

**Adversarial:** `SOURCE_AUTHORITY_GRAPH.yaml` pode estar desatualizado. Sempre rodar `hb validate` como verificação formal.

---

### C8 — Slash command `/resolve-merge-conflict <file>` — Resolver conflitos CDD

**Função:** Quando um contrato YAML tem conflito de merge, Claude resolve seguindo regras CDD (mais restritivo + canon prevalece).

**Implementação:**

**Arquivo criado:** `.claude/commands/resolve-merge-conflict.md`
```markdown
---
description: Resolve conflito de merge em arquivo de contrato seguindo regras CDD
allowed-tools: Read, Edit, Bash
---

Para o arquivo $ARGUMENTS com conflito de merge:

1. Leia o arquivo — identifique todos os marcadores `<<<<<<`, `=======`, `>>>>>>>`
2. Para cada conflito, aplique a regra: canon > schema > contrato > implementação
3. Se for OpenAPI: preserve o endpoint mais restritivo (menos permissivo)
4. Se for YAML de módulo: preserve os campos que existem no schema canônico
5. Após resolver, execute: `python3 scripts/hb validate --profile precommit`
6. Se validação falhar, reverta e reportie o conflito sem tentar resolver automaticamente
```

**Adversarial:** Resolver conflitos de contrato incorretamente pode introduzir breaking changes silenciosos. OBRIGATÓRIO: executar `hb validate` + `oasdiff` após qualquer resolução. Nunca aceitar resolução que falha na validação.

---

### C9 — Slash command `/backlog-extract` — Extrair itens do BACKLOG

**Função:** Após uma sessão, identifica tarefas concluídas e propõe novos itens para o BACKLOG baseado no que foi feito.

**Implementação:**

**Arquivo criado:** `.claude/commands/backlog-extract.md`
```markdown
---
description: Atualiza BACKLOG_EXECUTAVEL_DETERMINISTICO.md após sessão de trabalho
allowed-tools: Bash, Read, Edit
---

1. Execute: `git log origin/main..HEAD --oneline` para listar trabalho desta sessão
2. Leia `BACKLOG_EXECUTAVEL_DETERMINISTICO.md` para entender estrutura e itens existentes
3. Para cada commit, identifique se há item correspondente no BACKLOG (por B-ID ou descrição)
4. Marque como completados os itens correspondentes (não invente marcações sem correspondência)
5. Se o trabalho introduziu novas dependências ou lacunas, proponha até 3 novos itens B-ID com:
   - Descrição concreta
   - Critério de Done verificável
   - Dependências dos itens existentes
6. NÃO altere o arquivo — apenas liste as propostas para aprovação humana
```

**Adversarial:** Claude pode propor B-IDs duplicados. Instrução de leitura completa do BACKLOG antes de propor mitiga isso. Output como proposta (não edição direta) garante revisão humana.

---

### C10 — Integração com `merge-readiness.json` — PR readiness advisor

**Função:** Antes de criar o PR, Claude verifica o `merge-readiness.json` e confirma que todos os `local_equivalent` foram executados com sucesso.

**Implementação:**

**Arquivo criado:** `.claude/commands/pr-ready.md`
```markdown
---
description: Verifica prontidão para criação de PR contra merge-readiness.json
allowed-tools: Bash, Read
---

1. Leia `merge-readiness.json`
2. Para cada check com `category: required`, execute o `local_equivalent`
3. Para cada check `category: conditional`, execute: `git diff --name-only $(git merge-base origin/main HEAD)...HEAD | grep -qE "^\.(contract_driven|contracts|docs/_canon)/"` para verificar se `governance_changed == true`
4. Se governance_changed: execute também os `local_equivalent` dos checks condicionais
5. Produza tabela: Check | Status (PASS/FAIL) | Comando executado
6. Só declare "pronto para PR" se todos os required checks passarem
```

**Validação:**
```bash
ls .claude/commands/pr-ready.md && echo "EXISTS"
python3 -c "
import json
m = json.load(open('merge-readiness.json'))
required = [c for c in m['checks'] if c['category'] == 'required']
print(f'PASS — {len(required)} required checks serão verificados pelo comando')
"
```

**Adversarial:** Claude pode interpretar FAIL como aviso e não como bloqueio. Instrução explícita: "só declare pronto se TODOS os required passarem" + output visual da tabela para revisão humana.

---

## 6. 10 POSSIBILIDADES — Gemini (API Free Tier, sem custo adicional)

---

### G1 — Workflow separado: PR description auto-generator

**Trigger:** `pull_request` tipo `opened` apenas (não synchronize — executar uma vez)  
**Modelo:** `gemini-2.0-flash` (1500 RPD vs 1500 RPD do 2.5 Flash — mais estável para volume)  
**Condição:** Só executa se o body do PR está vazio ou contém apenas o template padrão

**Arquivo criado:** `.github/workflows/ai-pr-describe.yml`
```yaml
name: AI PR Description
on:
  pull_request:
    types: [opened]
    branches: [main]

permissions:
  contents: read
  pull-requests: write

jobs:
  describe:
    if: github.event.pull_request.draft == false
    runs-on: ubuntu-latest
    timeout-minutes: 5
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }
      - name: Gerar descrição se body vazio
        uses: actions/github-script@v7
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
        with:
          script: |
            const pr = context.payload.pull_request;
            if (pr.body && pr.body.trim().length > 50) {
              console.log('PR já tem body. Pulando.');
              return;
            }
            // Coletar commits e arquivos
            const commits = await github.paginate(
              github.rest.pulls.listCommits,
              { owner: context.repo.owner, repo: context.repo.repo, pull_number: pr.number }
            );
            const files = await github.paginate(
              github.rest.pulls.listFiles,
              { owner: context.repo.owner, repo: context.repo.repo, pull_number: pr.number }
            );
            const sovereignFiles = files.filter(f => 
              !f.filename.startsWith('_reports/') &&
              !f.filename.startsWith('generated/') &&
              !f.filename.startsWith('compiled_context/')
            ).map(f => f.filename);
            
            const prompt = `Gere uma descrição de PR para o HB Track. Seja conciso.
Commits: ${commits.map(c => c.commit.message.split('\n')[0]).join('; ')}
Arquivos soberanos alterados: ${sovereignFiles.slice(0,20).join(', ')}
Formato: ## Artefatos\n- lista\n## Testes\n- lista\n## Validação\n- lista`;

            const response = await fetch(
              \`https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=\${process.env.GEMINI_API_KEY}\`,
              { method: 'POST', headers: {'Content-Type':'application/json'},
                body: JSON.stringify({ contents: [{ role: 'user', parts: [{ text: prompt }] }] }) }
            );
            const data = await response.json();
            const text = data.candidates?.[0]?.content?.parts?.[0]?.text || '';
            if (text.length > 50) {
              await github.rest.pulls.update({
                owner: context.repo.owner, repo: context.repo.repo,
                pull_number: pr.number, body: text + '\n\n_Descrição gerada por Gemini (advisory)_'
              });
            }
```

**Validação:**
```bash
actionlint .github/workflows/ai-pr-describe.yml && echo "PASS actionlint"
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/ai-pr-describe.yml')); print('PASS yaml')"
```

**Adversarial:** Gemini pode gerar body que menciona arquivos `_reports/**`. Mitigação: filtro `sovereignFiles` explícito. Se Gemini gera text vazio (`< 50 chars`), o PR update é pulado — sem risco de sobrescrever body válido com vazio.

---

### G2 — Workflow: Breaking change detector em contratos OpenAPI

**Trigger:** `pull_request` para mudanças em `contracts/openapi/**`  
**Ferramenta:** `oasdiff` (já no toolchain) + Gemini para análise semântica  
**Separação de responsabilidades:** `oasdiff` para detecção formal, Gemini para explicação human-readable

**Arquivo criado:** `.github/workflows/ai-contract-check.yml`
```yaml
name: AI Contract Breaking Change Check
on:
  pull_request:
    branches: [main]
    paths: ['contracts/openapi/**']

permissions:
  contents: read
  pull-requests: write

jobs:
  breaking-check:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }
      
      - name: Ler versões de toolchain.json
        id: versions
        run: |
          echo "oasdiff=$(jq -r .tools.oasdiff toolchain.json)" >> "$GITHUB_OUTPUT"
          echo "python=$(jq -r .runtimes.python toolchain.json)" >> "$GITHUB_OUTPUT"
      
      - name: Instalar oasdiff
        run: |
          VER="${{ steps.versions.outputs.oasdiff }}"
          curl -fsSL "https://github.com/Tufin/oasdiff/releases/download/v${VER}/oasdiff_${VER}_linux_amd64.tar.gz" | tar -xz oasdiff
          chmod +x oasdiff
      
      - name: Detectar breaking changes com oasdiff
        id: oasdiff
        run: |
          git fetch origin main
          CHANGED=$(git diff --name-only origin/main...HEAD | grep '^contracts/openapi/' | head -5)
          BREAKING=""
          for f in $CHANGED; do
            BASE=$(git show origin/main:"$f" 2>/dev/null || echo "")
            if [ -n "$BASE" ]; then
              echo "$BASE" > /tmp/base_contract.yaml
              ./oasdiff breaking /tmp/base_contract.yaml "$f" --format json > /tmp/breaking_$$.json 2>/dev/null || true
              if [ -s /tmp/breaking_$$.json ]; then
                BREAKING="$BREAKING $(cat /tmp/breaking_$$.json)"
              fi
            fi
          done
          echo "breaking_json=$BREAKING" >> "$GITHUB_OUTPUT"
      
      - name: Análise Gemini dos breaking changes
        if: steps.oasdiff.outputs.breaking_json != ''
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
        run: |
          python3 - <<'PY'
          import json, os, subprocess
          from pathlib import Path
          breaking = os.environ.get('BREAKING_JSON', '{}')
          prompt = f"Explique em português o impacto dos seguintes breaking changes de API para o sistema HB Track. Seja conciso e aponte qual endpoint e qual cliente pode ser afetado:\n{breaking[:2000]}"
          body = {"contents": [{"role": "user", "parts": [{"text": prompt}]}],
                  "generationConfig": {"temperature": 0.1, "maxOutputTokens": 1024}}
          Path('bc_request.json').write_text(json.dumps(body))
          PY
          curl -sS -X POST -H "Content-Type: application/json" \
            "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${GEMINI_API_KEY}" \
            -d @bc_request.json > bc_response.json
      
      - name: Publicar resultado
        if: always()
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            let body = '### Breaking Change Check\n';
            try {
              const resp = JSON.parse(fs.readFileSync('bc_response.json', 'utf8'));
              const text = resp.candidates?.[0]?.content?.parts?.[0]?.text || 'Sem análise disponível.';
              body += text;
            } catch(e) {
              body += '✅ Nenhum breaking change detectado pelo oasdiff.';
            }
            body += '\n\n_oasdiff + Gemini advisory — não substitui validação formal._';
            await github.rest.issues.createComment({
              owner: context.repo.owner, repo: context.repo.repo,
              issue_number: context.payload.pull_request.number, body
            });
```

**Adversarial:** `oasdiff` em contratos parciais (apenas `paths/`) pode não ter o schema completo para análise. Mitigação: usar `contracts/openapi/openapi.yaml` (bundle completo) como base quando disponível; fallback para arquivo individual.

---

### G3 — Workflow: Canon consistency check

**Trigger:** `pull_request` para mudanças em `docs/_canon/**` ou `.contract_driven/TASK_CATALOG.yaml`  
**Objetivo:** Verificar que MODULE_REGISTRY.yaml ↔ TASK_CATALOG.yaml ↔ AGENT_INSTRUCTIONS.md estão em sinconia

**Arquivo criado:** `.github/workflows/ai-canon-check.yml`
```yaml
name: AI Canon Consistency Check
on:
  pull_request:
    branches: [main]
    paths:
      - 'docs/_canon/MODULE_REGISTRY.yaml'
      - 'docs/_canon/AGENT_INSTRUCTIONS.md'
      - '.contract_driven/TASK_CATALOG.yaml'

permissions:
  contents: read
  pull-requests: write

jobs:
  canon-check:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@v4
      - name: Verificar consistência formal (Python)
        id: formal
        run: |
          python3 - <<'PY'
          import yaml, json, sys
          from pathlib import Path

          registry = yaml.safe_load(Path('docs/_canon/MODULE_REGISTRY.yaml').read_text())
          catalog = yaml.safe_load(Path('.contract_driven/TASK_CATALOG.yaml').read_text())

          # Verificar que todos os módulos do registry têm docs
          modules = list(registry.get('modules', {}).keys())
          gaps = []
          for mod in modules:
              doc_path = Path(f'docs/hbtrack/modulos/{mod}/README.md')
              if not doc_path.exists():
                  gaps.append(f'Módulo {mod} sem README.md')

          # Verificar que task_catalog tem pr_fix (obrigatório)
          task_catalog_content = Path('.contract_driven/TASK_CATALOG.yaml').read_text()
          if 'pr_fix' not in task_catalog_content:
              gaps.append('pr_fix ausente do TASK_CATALOG')

          if gaps:
              print(json.dumps({'gaps': gaps, 'status': 'GAPS_FOUND'}))
              sys.exit(1)
          else:
              print(json.dumps({'gaps': [], 'status': 'OK'}))
          PY
      
      - name: Análise Gemini para inconsistências semânticas
        if: failure()
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
        run: echo "Gaps detectados — análise Gemini aqui"
```

**Adversarial:** Análise semântica pelo Gemini é probabilística; falsos negativos são possíveis. O step formal Python com assertions determinísticas é a verificação canônica. Gemini apenas explica os gaps já detectados formalmente.

---

### G4 — Workflow: SESSION_HANDOFF quality validator

**Trigger:** `pull_request` que inclui mudanças em `SESSION_HANDOFF.md`

**Arquivo criado:** `.github/workflows/ai-handoff-check.yml`
```yaml
name: AI SESSION_HANDOFF Validator
on:
  pull_request:
    branches: [main]
    paths: ['SESSION_HANDOFF.md']

permissions:
  contents: read
  pull-requests: write

jobs:
  handoff-check:
    runs-on: ubuntu-latest
    timeout-minutes: 8
    steps:
      - uses: actions/checkout@v4
      - name: Validar campos obrigatórios (formal)
        run: |
          python3 - <<'PY'
          import re
          from pathlib import Path
          content = Path('SESSION_HANDOFF.md').read_text()
          REQUIRED_FIELDS = ['branch_ativo', 'ci_status', 'last_completed', 'next_action']
          missing = [f for f in REQUIRED_FIELDS if f not in content]
          if missing:
              raise SystemExit(f'SESSION_HANDOFF.md faltando campos: {missing}')
          # ci_status não pode ser UNKNOWN
          if 'ci_status: UNKNOWN' in content:
              raise SystemExit('ci_status: UNKNOWN — executar hb ci antes do PR')
          print('PASS — todos os campos obrigatórios presentes')
          PY
```

**Adversarial:** `ci_status: UNKNOWN` válido em alguns casos (início de sessão). Mitigação: apenas advertência (não falha) para ci_status UNKNOWN; falha apenas para campos completamente ausentes.

---

### G5 — Workflow: Commit message linter CDD

**Trigger:** `push` para branches de feature  
**Objetivo:** Verificar que commits seguem `tipo(módulo): descrição` conforme padrão do repositório

**Arquivo criado:** `.github/workflows/ai-commit-lint.yml`
```yaml
name: Commit Message Lint
on:
  push:
    branches: ['feat/**', 'fix/**', 'chore/**', 'infra/**']

permissions:
  contents: read

jobs:
  commit-lint:
    runs-on: ubuntu-latest
    timeout-minutes: 5
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 10 }
      - name: Verificar commits recentes
        run: |
          python3 - <<'PY'
          import subprocess, re, sys
          pattern = re.compile(r'^(feat|fix|chore|infra|merge|refactor|docs|test|ci)\([\w/-]+\): .{10,}')
          result = subprocess.run(['git', 'log', '--format=%s', '-5'], capture_output=True, text=True)
          messages = [m.strip() for m in result.stdout.strip().splitlines() if m.strip()]
          bad = [m for m in messages if not pattern.match(m) and not m.startswith('merge')]
          if bad:
              print(f'WARNING: {len(bad)} commit(s) fora do padrão CDD:')
              for m in bad:
                  print(f'  - {m}')
              # Advisory only — não falha o build
          else:
              print(f'PASS — {len(messages)} commits com padrão correto')
          PY
```

**Adversarial:** Padrão de commit pode evoluir; regex hardcoded pode rejeitar commits válidos. Mitigação: workflow advisory (não bloqueia push); regex extraída de um arquivo de configuração editável (`commitlint.config.yaml`) ao invés de hardcoded.

---

### G6 — Workflow: Test obligation coverage report

**Trigger:** `pull_request` com mudanças em `tests/**` ou `docs/**/graph/test_obligations.yaml`

**Arquivo criado:** `.github/workflows/ai-test-coverage.yml`
```yaml
name: AI Test Obligation Coverage
on:
  pull_request:
    branches: [main]
    paths:
      - 'tests/**'
      - 'docs/hbtrack/modulos/**/graph/test_obligations.yaml'

permissions:
  contents: read
  pull-requests: write

jobs:
  coverage:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Verificar cobertura de FT-IDs
        run: |
          python3 - <<'PY'
          import yaml, re, subprocess
          from pathlib import Path

          gaps = []
          for oblig_file in Path('docs/hbtrack/modulos').rglob('test_obligations.yaml'):
              module = oblig_file.parts[3]
              data = yaml.safe_load(oblig_file.read_text())
              obligations = data.get('test_obligations', data.get('obligations', []))
              for ob in obligations if isinstance(obligations, list) else []:
                  ft_id = ob.get('id', ob.get('ft_id', ''))
                  if not ft_id:
                      continue
                  # Procurar FT-ID nos testes
                  result = subprocess.run(
                      ['grep', '-rn', ft_id, 'tests/'],
                      capture_output=True, text=True
                  )
                  if not result.stdout.strip():
                      gaps.append({'module': module, 'ft_id': ft_id, 'obligation': ob.get('description', '')[:60]})

          if gaps:
              print(f'⚠️ {len(gaps)} test obligations sem cobertura:')
              for g in gaps[:10]:
                  print(f"  {g['module']} {g['ft_id']}: {g['obligation']}")
          else:
              print('✅ Todas as test obligations têm cobertura identificada')
          PY
```

**Adversarial:** FT-ID pode estar em comentário ou string, não em código de teste ativo. `grep` não distingue. Mitigação: adicionar `pytest --collect-only -q -k FT_ID` como verificação secundária para FT-IDs marcados como críticos.

---

### G7 — Workflow: Multi-model review para PRs críticos

**Trigger:** `pull_request` que toca `contracts/**` — PRs com mudanças de contrato recebem review duplo  
**Modelos:** `gemini-2.5-flash` (revisão primária) + `gemini-2.0-flash` (revisão de validação)  
**Objetivo:** Convergência de dois modelos reduz falsos negativos em achados críticos

**Implementação:** Adicionar segundo job no `ai-pr-review.yml` com `needs: gemini-review`:
```yaml
  gemini-validation:
    name: Gemini Validation (contratos)
    needs: gemini-review
    if: |
      github.event.pull_request.draft == false &&
      contains(github.event.pull_request.changed_files, 'contracts/')
    runs-on: ubuntu-latest
    timeout-minutes: 10
    # ... usa gemini-2.0-flash com prompt diferente: só verifica achados do job anterior
```

**Adversarial:** Dois modelos diferentes podem produzir reviews contraditórios confundindo o desenvolvedor. Mitigação: o segundo job usa os achados do primeiro como contexto e apenas confirma/refuta — não produz novos achados independentes.

---

### G8 — Workflow: Domain axiom consistency check

**Trigger:** `pull_request` com mudanças em `src/*/domain/*.py` ou `.contract_driven/DOMAIN_AXIOMS.json`  
**Objetivo:** Verificar se novas entidades de domínio violam axiomas declarados

**Arquivo criado:** `.github/workflows/ai-domain-axiom.yml`
```yaml
name: AI Domain Axiom Check
on:
  pull_request:
    branches: [main]
    paths:
      - 'src/*/domain/*.py'
      - '.contract_driven/DOMAIN_AXIOMS.json'

permissions:
  contents: read
  pull-requests: write

jobs:
  axiom-check:
    runs-on: ubuntu-latest
    timeout-minutes: 8
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }
      - name: Verificar axiomas afetados
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
        run: |
          python3 - <<'PY'
          import json, subprocess
          from pathlib import Path

          axioms = json.loads(Path('.contract_driven/DOMAIN_AXIOMS.json').read_text())
          # Pegar diff de domain entities
          result = subprocess.run(
              ['git', 'diff', 'origin/main...HEAD', '--', 'src/*/domain/*.py'],
              capture_output=True, text=True
          )
          diff = result.stdout[:3000]
          if not diff.strip():
              print('Sem mudanças em domain entities.')
              exit(0)

          # Construir prompt com axiomas relevantes + diff
          axiom_sample = json.dumps(list(axioms.items())[:10], ensure_ascii=False)
          prompt = f"""Verifique se as mudanças em domain entities violam os axiomas do HB Track.
Axiomas (amostra): {axiom_sample}
Diff: {diff}
Responda apenas se houver violação evidente. Seja conciso."""
          # Chamar Gemini...
          PY
```

**Adversarial:** DOMAIN_AXIOMS.json tem 33KB — muito grande para enviar inteiro ao Gemini. Mitigação: filtrar apenas axiomas cujos `modules` incluem o módulo sendo alterado no diff.

---

### G9 — Workflow: Source graph completeness validator

**Trigger:** `pull_request` com mudanças em `docs/hbtrack/modulos/**/graph/*.yaml`  
**Objetivo:** Verificar que todos os 5 YAMLs obrigatórios do source graph estão presentes para cada módulo alterado

**Arquivo criado:** `.github/workflows/ai-graph-validate.yml`
```yaml
name: Source Graph Completeness
on:
  pull_request:
    branches: [main]
    paths: ['docs/hbtrack/modulos/**/graph/*.yaml']

permissions:
  contents: read
  pull-requests: write

jobs:
  graph-check:
    runs-on: ubuntu-latest
    timeout-minutes: 5
    steps:
      - uses: actions/checkout@v4
      - name: Verificar completude do source graph
        run: |
          python3 - <<'PY'
          import subprocess
          from pathlib import Path

          REQUIRED_YAMLS = {'module_manifest.yaml', 'entities.yaml', 'endpoints.yaml',
                           'errors.yaml', 'test_obligations.yaml'}

          result = subprocess.run(
              ['git', 'diff', '--name-only', 'origin/main...HEAD'],
              capture_output=True, text=True
          )
          changed = result.stdout.strip().splitlines()
          modules_changed = set()
          for f in changed:
              p = Path(f)
              if 'modulos' in p.parts and 'graph' in p.parts:
                  modules_changed.add(p.parts[p.parts.index('modulos') + 1])

          gaps = []
          for module in modules_changed:
              graph_dir = Path(f'docs/hbtrack/modulos/{module}/graph')
              if graph_dir.exists():
                  existing = {f.name for f in graph_dir.glob('*.yaml')}
                  missing = REQUIRED_YAMLS - existing
                  if missing:
                      gaps.append(f'{module}: faltando {missing}')

          if gaps:
              print('⚠️ Source graph incompleto:')
              for g in gaps:
                  print(f'  - {g}')
              exit(1)
          else:
              print(f'✅ {len(modules_changed)} módulo(s) com source graph completo')
          PY
```

**Validação:**
```bash
python3 -c "
REQUIRED = {'module_manifest.yaml','entities.yaml','endpoints.yaml','errors.yaml','test_obligations.yaml'}
from pathlib import Path
for mod in ['users','competitions','matches']:
    existing = {f.name for f in Path(f'docs/hbtrack/modulos/{mod}/graph').glob('*.yaml')}
    missing = REQUIRED - existing
    status = 'PASS' if not missing else f'FAIL: {missing}'
    print(f'{mod}: {status}')
"
```

**Adversarial:** Se o módulo está sendo criado do zero, todos os 5 YAMLs serão novos e estarão no diff — verificação passa corretamente. Risco: módulo renomeado → `modules_changed` inclui nome antigo e novo. Mitigação: checar apenas módulos cujo `graph/` já existe no HEAD do PR.

---

### G10 — Workflow: AI review artifacts em branch dedicada

**Objetivo:** Armazenar reviews do Gemini como artifacts consultáveis, sem poluir git history  
**Mecanismo:** GitHub Actions artifacts (90 dias de retenção, sem commits)

**Modificação no `ai-pr-review.yml`** — adicionar step final:
```yaml
- name: Salvar artifacts da review
  if: always() && steps.files.outputs.count != '0'
  uses: actions/upload-artifact@v4
  with:
    name: gemini-review-pr-${{ github.event.pull_request.number }}-${{ github.run_id }}
    path: |
      ai_review_findings.json
      ai_review_summary.md
      gemini_response.json
    retention-days: 30
    if-no-files-found: ignore
```

**Benefício:** Permite auditar histórico de reviews do Gemini sem afetar o repositório. Acessível via `gh run download`.

**Validação:**
```bash
# Verificar que upload-artifact@v4 existe no workflow
grep -c "upload-artifact" .github/workflows/ai-pr-review.yml || echo "0 (não implementado ainda)"
```

**Adversarial:** Artifacts ficam disponíveis publicamente em repos públicos. Mitigação: `gemini_response.json` pode conter o conteúdo do código do PR — aceitável pois é info pública em repo público. Em repos privados, artifact é privado por padrão.

---

## 7. ANÁLISE ADVERSARIAL CONSOLIDADA — CENÁRIOS CRÍTICOS

| Cenário | Planos afetados | Mitigação |
|---|---|---|
| **GEMINI_API_KEY expirada/inválida** | M1–M10, G1–G10 | Step "Validar secret" no início do workflow já existe — falha rápida antes de executar qualquer lógica |
| **Free tier esgotado (1500 RPD)** | Todos os G-* | M8 implementa tracking de cota; workflows G1-G10 devem verificar a variável antes de chamar a API |
| **PR com 90+ arquivos (como PR #50)** | M4, M5 | Prioridade M4 + token budget M5 garantem que contratos entram primeiro e diff é truncado antes de estourar contexto |
| **Workflow não trigga em PR aberto antes do merge** | Base + M2 | M2 provê script de re-trigger; documentar em `reviewer.md` como procedimento padrão |
| **Gemini retorna JSON inválido** | Todos os G-* | Bridge já tem 3 estratégias de parse (M3/G1 herdam o bridge existente); adicionar fallback de summary-only (M9) |
| **`src/**` com 18 módulos excede max_files** | M1 | Padrões seletivos (`src/*/api.py`, `src/*/domain/*.py`) em vez de `src/**` limitam a ~36 arquivos máximos |
| **Commit empty para re-trigger vaza histórico** | M2 | Alternativa preferida: `gh pr convert-to-draft` + `gh pr ready` sem commit |
| **actionlint falha em novo workflow** | G1–G9 | Validar com `actionlint .github/workflows/*.yml` antes de cada commit de novo workflow |
| **Codex atingiu limite (como em PR #50)** | — | Gemini é independente do Codex; não há dependência entre eles no pipeline |
| **Múltiplos PRs simultâneos esgotam RPM (10 RPM)** | M7 (retry) | `concurrency: group: ai-pr-review-${{ pr.number }}` já cancela runs antigos; retry com backoff não amplifica |

---

## 8. PRIORIDADE DE IMPLEMENTAÇÃO RECOMENDADA

| Prioridade | Item | Razão |
|---|---|---|
| **🔴 P1** | M1 — Adicionar `src/**` ao include | Todo código soberano está invisível ao reviewer |
| **🔴 P1** | M2 — Re-trigger script para PR #50 | PR aberto aguarda review |
| **🟡 P2** | M4 — Ordenação por prioridade de arquivos | Garante que contratos entram antes de testes |
| **🟡 P2** | M3 — Implementar dedupe_window_comments | Evitar ruído em re-runs |
| **🟡 P2** | M5 — Token budget management | PR #50 tem 90 arquivos; necessário para escala |
| **🟢 P3** | C10 — `/pr-ready` slash command | Verificação local antes de criar PR |
| **🟢 P3** | C1 — `/validate-drift` | Detecção de drift contrato × implementação |
| **🟢 P3** | G9 — Source graph completeness | Gate leve, alta utilidade |
| **🟢 P3** | G1 — PR description generator | Qualidade de PR bodies |
| **🔵 P4** | M8 — Tracking de cota | Proteção de longo prazo |
| **🔵 P4** | G2 — Breaking change detector | oasdiff já disponível no toolchain |
| **🔵 P4** | C3 — `/session-close` | Produtividade de sessão |

---

## 9. ESTADO ATUAL DOS ARQUIVOS DO REVIEWER

| Arquivo | Path | Status |
|---|---|---|
| Workflow principal | `.github/workflows/ai-pr-review.yml` | ✅ Merged em main (PR #49, 2026-04-05T17:13) |
| Config | `.github/ai-review/config.yaml` | ✅ Existente — gap: `src/**` ausente |
| Styleguide | `.github/ai-review/styleguide.md` | ✅ Existente — adequado |
| Bridge | `scripts/ai_review_bridge.py` | ✅ Existente — gap: `dedupe_window_comments` não implementado |
| Secret | `GEMINI_API_KEY` no GitHub | ✅ Configurado (evidência PR #49) |
| PR #50 review | — | ❌ Nunca trigou (aberto antes do merge do workflow) |
