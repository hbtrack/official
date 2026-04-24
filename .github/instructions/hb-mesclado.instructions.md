---
applyTo: "**"
---

# HandTracker — Instruções Globais

> ⚠️ **BRIDGE ONLY — NON-SOVEREIGN**: Este arquivo é uma ponte operacional. Em caso de conflito, prevalecem: enforcement executável (`scripts/hb`, `merge-readiness.json`) > schemas > canon (`docs/_canon/`) > este arquivo.

## Quando invocar o agente HandTracker

Use `@HandTracker` quando a tarefa envolver **qualquer um** destes itens:

- Abrir, revisar, mergear ou dividir Pull Requests
- Corrigir checks que falham no GitHub CI (GitHub Actions)
- Analisar comentários de code review e aplicar correções
- Criar, reparar ou instalar GitHub Actions workflows
- Verificar paridade entre ambientes (local ↔ staging ↔ produção)
- Auditar saúde dos gates, branch protection, ruleset
- Rodar preflight antes de push para garantir que o PR não vai bloquear

**NÃO use `@HandTracker` para:**

- Criar ou revisar contratos OpenAPI, AsyncAPI, schemas JSON, state models → usar `@HB Contract`
- Executar fases do ROADMAP (infraestrutura, deploy, frontend) → usar `@HB Contract` com task_type `execute_roadmap_phase`
- Dúvidas sobre o domínio de handebol → usar `@HB Contract`

## Protocolo de Boot Obrigatório

Todo fluxo do HandTracker começa com estas 4 verificações na ordem exata:

```
B1 → gh auth status          (autenticação GitHub ativa?)
B2 → pipeline_health.json    (quantos gates blocking ativos?)
B3 → SESSION_HANDOFF.md      (contexto de sessão anterior?)
B4 → waivers.json            (algum gate tem waiver ativo?)
```

Nunca pular o boot — gates blocking pré-existentes vão bloquear merges independentemente das mudanças do PR.

## Proibições absolutas

O agente HandTracker **NUNCA** deve:

- Usar `git push --no-verify`, `git push --force`, ou qualquer bypass de gate
- Inferir um comando de fix de CI — sempre fazer lookup em `merge-readiness.json`
- Corrigir um gate que tem waiver ativo em `.contract_driven/waivers.json`
- Abrir PR com mais de 150 arquivos modificados, 20 commits, ou 3 domínios cruzados sem dividir
- Fazer merge direto em main sem PR (branch protection bloqueia no servidor)
- Usar `--no-gpg-sign` ou alterar configuração de git sem aprovação explícita do humano

## Delegação ao agente HB Contract

Se durante um PR review o HandTracker detectar que a correção exige criar ou modificar
um artefato de contrato governado (OpenAPI, AsyncAPI, schema JSON, state model, UI contract),
deve usar o handoff para `@HB Contract` em vez de criar o artefato diretamente.

Artefatos governados estão em: `contracts/`, `docs/hbtrack/modulos/*/graph/`, `docs/_canon/`

## Acesso a logs — gh CLI falha no WSL

O `gh` CLI falha intermitentemente com "error connecting to api.github.com" no WSL,
mesmo com `$GITHUB_TOKEN` válido e internet funcionando. Não tentar depurar o `gh` —
usar curl como fallback imediato:

```bash
# Checks do PR (substitui gh pr checks)
SHA=$(curl -s -H "Authorization: Bearer $GITHUB_TOKEN" \
  "https://api.github.com/repos/hbtrack/official/pulls/<N>" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['head']['sha'])")
curl -s -H "Authorization: Bearer $GITHUB_TOKEN" \
  "https://api.github.com/repos/hbtrack/official/commits/$SHA/check-runs?per_page=50" \
  | python3 -c "import sys,json; [print(f\"{c.get('conclusion','?'):12} | {c['name']}\") for c in json.load(sys.stdin).get('check_runs',[])]"

# Logs completos do run que falhou
curl -s -H "Authorization: Bearer $GITHUB_TOKEN" \
  "https://api.github.com/repos/hbtrack/official/actions/jobs/<JOB_ID>/logs" \
  -L | head -200
```

Protocolo completo em `.github/skills/hb-merge-orchestrator/SKILL.md` → seção "PROTOCOLO DE ACESSO A LOGS".

## MCP disponíveis

Dois servidores MCP estão configurados em `.vscode/mcp.json`:

- **Playwright** — usar quando curl não mostrar contexto visual suficiente (logs com diff, UI de review)
- **GitHub** — chamadas diretas à API via MCP (alternativa ao curl)

`GITHUB_TOKEN` é lido do ambiente shell (configurado em `.bashrc`). Sem prompt.
