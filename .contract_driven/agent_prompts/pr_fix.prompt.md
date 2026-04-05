---
task_type: pr_fix
version: "1.0.0"
status: active
executor_canonical: "python3 scripts/hb ci --profile pr"
ssot_mapping: merge-readiness.json
---

# pr_fix — Worker de Correção de CI em PR

> **NON-SOVEREIGN**: Este worker é ponte operacional. SSOT de mapeamento: `merge-readiness.json`.
> Executor canônico padrão: `python3 scripts/hb ci --profile pr`

---

## REGRA ZERO — Lookup antes de qualquer ação

**Antes de ler qualquer arquivo de código, antes de rodar qualquer comando:**

1. Obter `check_context` exato do GitHub (case-sensitive) → `gh pr checks <PR> --watch`
2. Abrir `merge-readiness.json`
3. Encontrar o objeto onde `context == check_context`
4. Usar o campo `local_equivalent` como único executor autorizado

Se `check_context` não estiver em `merge-readiness.json` → **PARAR**.
Emitir: `GAP_DE_PARIDADE: check "<context>" não tem local_equivalent mapeado`.
Não improvisar comando alternativo.

---

## Algoritmo — 5 passos

### PASSO 1 — Identificar

```bash
gh pr checks <NUMERO_PR> --watch
```

Extrair o nome exato do check que falhou (`context` field, case-sensitive).
Exemplo: `ci / Tests`, `Validate Contract Gates`, `Governance Enforcement (survival-suite)`.

### PASSO 2 — Lookup no SSOT

```bash
python3 -c "
import json
m = json.load(open('merge-readiness.json'))
ctx = '<CHECK_CONTEXT_AQUI>'
c = next((x for x in m['checks'] if x['context'] == ctx), None)
if c:
    print(c.get('local_equivalent', 'SEM_LOCAL_EQUIVALENT'))
else:
    print('GAP_DE_PARIDADE: context nao encontrado')
"
```

Se o check for `conditional`: verificar primeiro se `governance_changed == true` antes de rodar
(ver seção "Checks Condicionais" abaixo).

### PASSO 3 — Executar local_equivalent exatamente

Rodar o comando `local_equivalent` do passo anterior sem modificação.
Não substituir por outro comando. Não adicionar flags extras.

### PASSO 4 — Diagnosticar e corrigir

Se o comando retornar exit code != 0:
- Ler a saída de erro completa
- Identificar o arquivo, linha e causa raiz
- Aplicar a correção mínima necessária (não expandir escopo)
- Re-executar o `local_equivalent` até PASS

### PASSO 5 — Revalidar e push

```bash
# Re-executar local_equivalent completo para confirmar PASS
python3 scripts/hb ci --profile pr   # ou o local_equivalent do check específico

# Push apenas após PASS local
git push
```

Aguardar CI. Se CI falhar em check diferente → recomeçar do PASSO 1 para o novo check.

---

## Checks Condicionais

Quatro checks só ativam quando `governance_changed == true`.
Detectar mudança de governança neste PR:

```bash
git diff --name-only $(git merge-base origin/main HEAD)...HEAD \
  | grep -qE "^\.(contract_driven|contracts|docs/_canon)/" \
  && echo "governance_changed=true" || echo "governance_changed=false"
```

### Mapeamento dos checks condicionais

| context (GitHub) | local_equivalent | condition |
|---|---|---|
| `Governance Enforcement (survival-suite)` | `CI=true python3 scripts/hb survival-suite` | governance_changed == true |
| `Paridade Registry × Executor` | `python -m pytest tests/pipeline_gates/test_gate_registry_parity.py -v` | governance_changed == true |
| `Paridade Schema × Template × Skills` | `python -m pytest tests/pipeline_gates/test_schema_template_parity_phase4.py -v` | governance_changed == true |
| `Validação Cruzada SESSION_HANDOFF ↔ session_start` | `python -m pytest tests/pipeline_gates/test_session_state_phase3.py -v` | governance_changed == true |

**GOVERNANCE_PATHS** (paths que ativam governance_changed):
- `.contract_driven/`
- `contracts/`
- `docs/_canon/`

---

## Proibições absolutas

- **Nunca** inferir ou substituir `local_equivalent` por comando alternativo
- **Nunca** alterar arquivos de governance (`.contract_driven/`, `contracts/`, `docs/_canon/`) sem falha explícita de check de governança
- **Nunca** usar `--no-verify`, `--force-push`, ou bypass de gate
- **Nunca** expandir escopo além do diff do PR para corrigir o check
- **Nunca** usar `GAP_DE_PARIDADE` como justificativa para improvisar — sempre reportar e parar

---

## Smoke test do local_equivalent

Para verificar que o executor mapeado funciona antes de corrigir código:

```bash
# Verificar que hb validate existe e aceita --profile
python3 scripts/hb validate --help

# Verificar que hb ci existe e aceita --profile
python3 scripts/hb ci --help

# Para checks condicionais: smoke test com arquivo existente
python -m pytest tests/pipeline_gates/test_gate_registry_parity.py --collect-only -q
```

---

## Referências canônicas

- `merge-readiness.json` — SSOT de mapeamento check → local_equivalent
- `scripts/hb` — executores canônicos (`hb validate`, `hb ci`, `hb survival-suite`)
- `.github/agents/hb-contract.agent.md` — Protocolo PR_FIX (seção)
- `.contract_driven/TASK_CATALOG.yaml` — entrada `pr_fix` (restrições operacionais)
