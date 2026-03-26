# Pipeline Automático — Arquitetura por Estágios
> v4.0.0 | 2026-03-17 | Substitui todas as versões anteriores
> Consolida: MELHORAR_PIPELINE.md (M1–M12) + MELHORAR_PIPELINE2.md (O1–O18)

---

## Princípio central: DONE = exitcode 0

Cada fase tem um único critério binário de conclusão.

```
DONE  = exitcode 0   → prosseguir para fase seguinte
FAIL  = exitcode ≠ 0 → ler log, corrigir, re-executar. NÃO AVANÇAR.
```

O agente não interpreta nem decide se está "ok". Ele lê o exit code. Se não é 0, não avança.

---

## Por que texto sozinho não controla IA

Instruções em texto (CLAUDE.md, prompts, checklists) são o mecanismo mais fraco: o agente pode
esquecer, ignorar ou racionalizar o bypass. A solução é arquitetural:

> **Projetar o sistema de forma que o comportamento desejado seja o único caminho possível —
> não o caminho recomendado.**

### Hierarquia de controle (TIER 1 = mais forte)

```
TIER 1 — AUTOMÁTICO  (agente não tem controle)
─────────────────────────────────────────────
  • Pre-commit hook: EXIT 1 se SESSION_HANDOFF não staged ou session_start.json inválido
  • CI/merge: bloqueado se gate blocking=true falhar
  • Gate blocking=true em validate_contracts.py: impede promoção de status com bloqueios ativos

TIER 2 — FORCING FUNCTION  (comportamento desejado = único caminho para o commit)
──────────────────────────────────────────────────────────────────────────────────
  • hb verify   → gera session_start.json com stage0_exit_code=0
  • hb check    → atualiza session_start.json com stage1_exit_code=0
  • hb artifact → registra artefato em stage2_artifacts[]
  • Pre-commit REQUER session_start.json com todas as fases com exitcode=0
  • Se agente pular qualquer fase → session_start.json incompleto → commit BLOQUEADO

TIER 3 — INSTRUÍDO  (apenas soft constraints não verificáveis por máquina)
──────────────────────────────────────────────────────────────────────────
  • CLAUDE.md: formato de comunicação, idioma, estilo
  • Checkpoints no orchestrator: reforço de tier 2 (não é a segurança real)
  • NÃO usar para invariantes críticos do pipeline
```

**Regra de design:** todo invariante crítico → TIER 1. Se não possível → TIER 2. Texto apenas
para o que a máquina não pode verificar.

---

## Invariantes críticos → tier atribuído

| Invariante | Tier | Mecanismo |
|---|---|---|
| Não commitar sem atualizar SESSION_HANDOFF.md | **TIER 1** | pre-commit hook (já existe) |
| Não promover módulo com RC críticos abertos | **TIER 1** | MODULE_STATUS_COHERENCE_GATE blocking=true (CI) |
| Não criar UI contract com operationId inexistente | **TIER 1** | UI_ALIGNMENT_GATE no precommit |
| Não iniciar trabalho sem validar handoff e status | **TIER 2** | session_start.json ausente → pre-commit BLOQUEIO |
| Não avançar de fase sem exitcode=0 | **TIER 2** | session_start.json incompleto → pre-commit BLOQUEIO |
| Não criar artefato fora do scope declarado | **TIER 2** | staged ∉ artifacts_validated → pre-commit BLOQUEIO |
| Formato de comunicação em português | TIER 3 | CLAUDE.md (não verificável por máquina) |

---

## Diagrama: as 5 fases

```
┌─────────────────────────────────────────────────────────────────────┐
│  FASE 0 — SESSION_BOOT                                              │
│  Comando : hb verify                                                │
│  DONE    : exitcode 0  →  session_start.json { stage0_exit_code:0 } │
│  Gates   : HANDOFF_COHERENCE, MODULE_STATUS_COHERENCE, PROMPT_VALID │
└──────────────────────────┬──────────────────────────────────────────┘
                           │ exitcode=0
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│  FASE 1 — PRE_AUTHORING                                             │
│  Comando : hb check --module <mod>                                  │
│  DONE    : exitcode 0  →  session_start.json { stage1_exit_code:0 } │
│  Gates   : ADVERSARIAL_COMPLETENESS, WRITE_SCOPE_DECLARATION        │
└──────────────────────────┬──────────────────────────────────────────┘
                           │ exitcode=0
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│  FASE 2 — PER_ARTIFACT  (repetir por artefato criado/modificado)   │
│  Comando : hb artifact <path>                                       │
│  DONE    : exitcode 0  →  path adicionado a stage2_artifacts[]      │
│  Gates   : UI_CONTRACT_ALIGNMENT, FSM_COMPLETENESS,                 │
│            CROSS_MODULE_BOUNDARY, PATH_CANONICALITY                 │
└──────────────────────────┬──────────────────────────────────────────┘
                           │ todos os artefatos com exitcode=0
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│  FASE 3 — PRE_COMMIT  (AUTOMÁTICO — hook)                          │
│  Trigger : git commit                                               │
│  DONE    : exitcode 0 → commit efetuado                             │
│  Valida  : session_start.json existe?                               │
│            stage0+stage1 exitcode=0?                                │
│            staged ⊆ artifacts_validated?                            │
│            SESSION_HANDOFF.md staged?                               │
│            breaking change → waiver presente?                       │
└──────────────────────────┬──────────────────────────────────────────┘
                           │ exitcode=0
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│  FASE 4 — CI  (AUTOMÁTICO — github actions, push/PR)               │
│  DONE    : todos gates blocking=true com PASS → merge permitido     │
│  Gates   : full suite + MODULE_STATUS_COHERENCE (blocking=true)     │
│            + oasdiff, spectral, schemathesis                        │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Artefato central: `_reports/session_start.json`

Escrito por `hb`. Lido pelo pre-commit. **Se ausente ou incompleto = commit BLOQUEADO.**

```json
{
  "session_id": "2026-03-17T14:23:00_a1b2c3",
  "task_type": "contract_revision",
  "module": "training",
  "branch": "hb-track-contratos-driven",
  "timestamp": "2026-03-17T14:23:00Z",
  "stages": {
    "stage0_exit_code": 0,
    "stage1_exit_code": 0,
    "stage2_artifacts": [
      {"path": "contracts/openapi/paths/training.yaml", "exit_code": 0},
      {"path": "docs/hbtrack/modulos/training/UI_CONTRACT_TRAINING.md", "exit_code": 0}
    ]
  }
}
```

---

## Formato de log — saída de cada comando `hb`

Todo log termina com o critério DONE e a ação corretiva específica. Agente não infere o que fazer.

```
══════════════════════════════════════════════════════════════
  FASE 0: SESSION_BOOT  |  STATUS: FAIL  (exitcode=2)
══════════════════════════════════════════════════════════════

  ✗ HANDOFF_COHERENCE_GATE
    Problema : branch_ativo='main' != branch atual='hb-track-training'
    Artefato : SESSION_HANDOFF.md linha 5
    Ação     : Atualizar campo branch_ativo para 'hb-track-training'
    Código   : BLOCKED_HANDOFF_INCOMPLETE

  ✗ MODULE_STATUS_COHERENCE_GATE
    Problema : training status='implementation_ready' com RC-1 crítico aberto
    Artefato : docs/_canon/MODULE_REGISTRY.yaml
    Ação     : Rebaixar status para 'validated_contract' OU resolver RC-1
    Código   : BLOCKED_ADVERSARIAL_PENDING

  ──────────────────────────────────────────────────────────
  DONE = exitcode 0  |  atual exitcode = 2
  Corrigir itens acima e re-executar: hb verify
══════════════════════════════════════════════════════════════
```

---

## Gates por fase — critérios e logs

### Fase 0 — `hb verify`
Gates: HANDOFF_COHERENCE_GATE, MODULE_STATUS_COHERENCE_GATE, PROMPT_VALIDATION_GATE

| Gate | Origem | Critério PASS | FAIL — log para o agente |
|---|---|---|---|
| HANDOFF_COHERENCE | O5 | branch_ativo=branch atual E data<30d | `branch_ativo='X' != atual='Y'. Ação: SESSION_HANDOFF.md linha 5` |
| MODULE_STATUS_COHERENCE | O1 | status ≤ bloqueios adversariais | `training: impl_ready com RC-1 aberto. Ação: rebaixar status ou resolver RC` |
| PROMPT_VALIDATION | O16 | task_type∈§4 E module∈REGISTRY E worker existe | `task_type='foo' inválido. Valores: [new_module, new_contract, ...]` |

### Fase 1 — `hb check --module <mod>`
Gates: ADVERSARIAL_COMPLETENESS_GATE, WRITE_SCOPE_GATE

| Gate | Origem | Critério PASS | FAIL — log para o agente |
|---|---|---|---|
| ADVERSARIAL_COMPLETENESS | O6 | score≥90 (impl_ready) ou ≥80 (validated), 0 RC críticos | `Score 82/100 < 90 para impl_ready. RC-1, RC-2 abertos. Resolver antes de autoria.` |
| WRITE_SCOPE_DECLARATION | O15 | scope declarado em session_start.json | `scope ausente. Executar: hb check --module training --scope "files..."` |

### Fase 2 — `hb artifact <path>`
Gates: UI_CONTRACT_ALIGNMENT_GATE, FSM_COMPLETENESS_GATE, CROSS_MODULE_BOUNDARY_GATE, PATH_CANONICALITY_GATE

| Gate | Origem | Critério PASS | FAIL — log para o agente |
|---|---|---|---|
| UI_CONTRACT_ALIGNMENT | O4 | operationIds no UI ∈ OpenAPI definidos | `'acceptRecommendation' inexistente no OpenAPI. Adicionar a training.yaml ou corrigir referência.` |
| FSM_COMPLETENESS | O12 | todo estado não-terminal tem ≥1 transição de saída | `Estado 'PUBLISHED' sem saída. Declarar transição ou adicionar a terminal_states.` |
| CROSS_MODULE_BOUNDARY | O10 | sem campos soberanos de outros módulos | `'restriction_profile' é soberano de 'medical'. Remover ou criar boundary rule.` |
| PATH_CANONICALITY | existente | path no diretório canônico correto | `Contrato em docs/ — deve estar em contracts/openapi/. Mover.` |

### Fase 3 — pre-commit hook (automático)
Verificações realizadas pelo hook antes de qualquer gate Python:

| Verificação | Critério PASS | FAIL — commit bloqueado |
|---|---|---|
| session_start.json existe | arquivo presente em _reports/ | `hb verify não foi executado. Executar: hb verify (DONE=0)` |
| stage0_exit_code == 0 | valor = 0 | `Fase 0 não completada. Re-executar: hb verify` |
| stage1_exit_code == 0 | valor = 0 | `Fase 1 não completada. Re-executar: hb check --module <mod>` |
| staged ⊆ artifacts_validated | todo staged∈contracts/ ou docs/hbtrack/ foi validado | `training.yaml staged sem hb artifact. Executar: hb artifact contracts/openapi/paths/training.yaml` |
| SESSION_HANDOFF.md staged | presente no staging area | `SESSION_HANDOFF.md não staged. Atualizar e: git add SESSION_HANDOFF.md` |
| WAIVER_CHECK | sem breaking change OU waiver ativo em _waivers/ | `Breaking change sem waiver. Criar contracts/_waivers/<id>.json` |
| SIGN_OFF_PRESENT | se promovendo status: signoff json existe | `Promoção de status sem sign-off. Aguardar aprovação humana.` |

Após verificações do hook: `python validate_contracts.py --profile precommit` (gates rápidos).

### Fase 4 — CI (automático)
Gates adicionais além dos estágios 0-3:

| Gate | Origem | Tier | blocking |
|---|---|---|---|
| CONTRACT_BREAKING_CHANGE + WAIVER_ENGINE | M4 | TIER 1 | true |
| PACT_PROVIDER | existente | TIER 1 | false |
| ADR_COVERAGE | O7 | TIER 4 | false (informativo) |
| HEALTH_SCORE + HISTORY | M9+O11 | TIER 4 | false (observabilidade) |
| BLOCKER_AGING | O14 | TIER 4 | false (escalation) |
| READINESS_DASHBOARD | O17 | TIER 4 | false (gerado automaticamente) |
| STALENESS | O18 | TIER 4 | false (informativo) |

---

## Implementação — 9 itens em ordem de execução

### Item 1: `scripts/hb` — CLI wrapper (NOVO)

**Arquivo:** `scripts/hb`
**Tipo:** bash executável (~55 linhas)
**DONE =** `chmod +x scripts/hb && hb verify && echo $?` → 0

```bash
#!/usr/bin/env bash
# HB Track Pipeline CLI
# DONE = exitcode 0. Não avançar de fase sem exitcode 0.
set -euo pipefail
ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
VALIDATOR="$ROOT/scripts/contracts/validate/validate_contracts.py"
SESSION_FILE="$ROOT/_reports/session_start.json"

_update_session() {
  python3 -c "
import json, pathlib, sys
p = pathlib.Path('${SESSION_FILE}')
d = json.loads(p.read_text(encoding='utf-8')) if p.exists() else {}
d.setdefault('stages', {})['${1}'] = ${2}
p.parent.mkdir(parents=True, exist_ok=True)
p.write_text(json.dumps(d, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
"
}

case "${1:-}" in
  verify)
    printf '\n══ FASE 0: SESSION_BOOT ══\n'
    python3 "$VALIDATOR" --stage session-start
    code=$?
    _update_session "stage0_exit_code" $code
    printf '\nDONE = exitcode 0  |  atual exitcode = %d\n\n' $code
    exit $code
    ;;
  check)
    printf '\n══ FASE 1: PRE_AUTHORING ══\n'
    python3 "$VALIDATOR" --stage pre-authoring "$@"
    code=$?
    _update_session "stage1_exit_code" $code
    printf '\nDONE = exitcode 0  |  atual exitcode = %d\n\n' $code
    exit $code
    ;;
  artifact)
    [[ -z "${2:-}" ]] && printf 'Uso: hb artifact <path>\n' && exit 1
    ARTIFACT="${2}"
    printf '\n══ FASE 2: PER_ARTIFACT | %s ══\n' "$ARTIFACT"
    python3 "$VALIDATOR" --stage artifact --artifact "$ARTIFACT"
    code=$?
    if [[ $code -eq 0 ]]; then
      python3 -c "
import json, pathlib
p = pathlib.Path('${SESSION_FILE}')
d = json.loads(p.read_text(encoding='utf-8')) if p.exists() else {}
d.setdefault('stages', {}).setdefault('stage2_artifacts', [])
existing = [a['path'] for a in d['stages']['stage2_artifacts']]
if '${ARTIFACT}' not in existing:
    d['stages']['stage2_artifacts'].append({'path': '${ARTIFACT}', 'exit_code': 0})
p.write_text(json.dumps(d, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
"
    fi
    printf '\nDONE = exitcode 0  |  atual exitcode = %d\n\n' $code
    exit $code
    ;;
  status)
    python3 "$VALIDATOR" --profile local
    ;;
  help|--help|-h|"")
    printf 'HB Track Pipeline CLI — DONE = exitcode 0\n\n'
    printf '  hb verify                  Fase 0: valida handoff, status, task_type\n'
    printf '  hb check --module <mod>    Fase 1: valida readiness do módulo\n'
    printf '  hb artifact <path>         Fase 2: valida artefato criado/modificado\n'
    printf '  hb status                  Estado completo do pipeline (local)\n\n'
    printf 'Não avançar de fase sem exitcode 0.\n'
    exit 0
    ;;
  *)
    printf 'Subcomando desconhecido: %s\n' "$1"
    printf 'Executar "hb help" para ver os comandos disponíveis.\n'
    exit 1
    ;;
esac
```

**Validação:**
```bash
chmod +x scripts/hb
hb verify; echo "exitcode=$?"          # deve mostrar FASE 0 e criar session_start.json
hb artifact contracts/openapi/paths/training.yaml; echo "exitcode=$?"
```

---

### Item 2: Expansão do `.git/hooks/pre-commit` (EXISTENTE)

**Arquivo:** `.git/hooks/pre-commit`
**Inserir:** ANTES do bloco `# Summary` existente
**DONE =** `git commit` bloqueado quando session_start.json ausente ou fase não completada

```bash
# ── FASE 3: SESSION_START ENFORCEMENT ─────────────────────────────
SESSION_FILE="$(git rev-parse --show-toplevel)/_reports/session_start.json"

if [[ ! -f "$SESSION_FILE" ]]; then
  printf '\n[FASE 3] BLOQUEADO: session_start.json ausente\n'
  printf '  Causa : hb verify nao foi executado nesta sessao\n'
  printf '  Acao  : executar hb verify (DONE=exitcode 0)\n'
  printf '          depois   hb check --module <mod> (DONE=exitcode 0)\n'
  printf '  DONE = exitcode 0  |  atual exitcode = 1\n\n'
  exit 1
fi

python3 - "$SESSION_FILE" <<'PYEOF'
import json, sys, subprocess, pathlib

session_file = sys.argv[1]
d = json.loads(pathlib.Path(session_file).read_text(encoding="utf-8"))
stages = d.get("stages", {})
fail = []

if stages.get("stage0_exit_code", -1) != 0:
    fail.append("Fase 0 nao completada. Re-executar: hb verify")

if stages.get("stage1_exit_code", -1) != 0:
    fail.append("Fase 1 nao completada. Re-executar: hb check --module <mod>")

validated = {
    a["path"] for a in stages.get("stage2_artifacts", [])
    if a.get("exit_code") == 0
}
staged_raw = subprocess.check_output(
    ["git", "diff", "--cached", "--name-only"], text=True
).splitlines()
must_validate_prefixes = ("contracts/", "docs/hbtrack/")
for f in staged_raw:
    if f.startswith(must_validate_prefixes) and f not in validated:
        fail.append(
            f"{f} staged sem validacao. Executar: hb artifact {f}"
        )

if fail:
    print("\n[FASE 3] BLOQUEADO:")
    for f in fail:
        print(f"  x {f}")
    print("\n  DONE = exitcode 0 em cada fase antes de commitar")
    sys.exit(1)

print("[FASE 3] session_start.json OK — todas as fases completadas")
PYEOF

[[ $? -ne 0 ]] && exit 1

# Gates rápidos do profile precommit
python3 "$(git rev-parse --show-toplevel)/scripts/contracts/validate/validate_contracts.py" \
  --profile precommit
# ── fim FASE 3 ─────────────────────────────────────────────────────
```

**Validação:**
```bash
rm -f _reports/session_start.json
echo "x" >> contracts/openapi/paths/training.yaml
git add contracts/openapi/paths/training.yaml SESSION_HANDOFF.md
git commit -m "test"  # → EXIT 1: session_start.json ausente
git restore contracts/openapi/paths/training.yaml
```

---

### Item 3: `validate_contracts.py` — `--stage` + header de fase (EXISTENTE)

**Arquivo:** `scripts/contracts/validate/validate_contracts.py`
**Pontos de inserção:**

**3a. `main()` L7088** — adicionar `--stage`:
```python
def main() -> int:
    import argparse as _argparse
    _parser = _argparse.ArgumentParser(description="HB Track Contract Gates")
    _parser.add_argument("--profile", choices=["local", "precommit", "ci"], default=None)
    _parser.add_argument(
        "--stage",
        choices=["session-start", "pre-authoring", "artifact", "ci"],
        default=None,
        help="Executar apenas gates do estágio especificado"
    )
    _parser.add_argument("--module", default=None)
    _parser.add_argument("--artifact", default=None)
    _args, _ = _parser.parse_known_args()

    _profile = _args.profile or ("ci" if os.environ.get("CI") else "local")
    _stage = _args.stage

    report, exit_code = run_pipeline(profile=_profile, stage=_stage,
                                     module=_args.module, artifact=_args.artifact)
    # ... output existente com header de fase adicionado:
    # print(f"  FASE: {_stage.upper() if _stage else 'CI'} | STATUS: {overall}")
```

**3b. `run_pipeline()` L6930** — adicionar `stage` parameter e gate filtering:
```python
def run_pipeline(profile: str = "ci", stage: str | None = None,
                 module: str | None = None, artifact: str | None = None) -> tuple[dict, int]:
    # ... código existente ...

    # Stage → subset de gates
    _STAGE_GATES = {
        "session-start": {
            "HANDOFF_COHERENCE_GATE", "MODULE_STATUS_COHERENCE_GATE", "PROMPT_VALIDATION_GATE"
        },
        "pre-authoring": {
            "ADVERSARIAL_ANALYSIS_GATE", "WRITE_SCOPE_GATE",
            "MODULE_STATUS_COHERENCE_GATE",
        },
        "artifact": {
            "UI_DOC_VALIDATION_GATE", "AXIOM_INTEGRITY_GATE",
            "CROSS_MODULE_BOUNDARY_GATE", "PATH_CANONICALITY_GATE",
        },
        "precommit": {  # profile precommit = stage 3
            "HANDOFF_COHERENCE_GATE", "MODULE_STATUS_COHERENCE_GATE",
            "AXIOM_INTEGRITY_GATE", "PATH_CANONICALITY_GATE",
            "UI_DOC_VALIDATION_GATE", "DERIVED_DRIFT_GATE",
            "PLACEHOLDER_RESIDUE_GATE", "WAIVER_ENGINE_GATE",
        },
    }
    allowed = _STAGE_GATES.get(stage) if stage else None
    # allowed=None → rodar tudo (CI/default)
```

**3c. `main()` output** — adicionar `DONE = exitcode 0 | atual exitcode = N` ao final:
```python
    # No final de main():
    stage_name = _stage.upper().replace("-", "_") if _stage else "CI_FULL"
    print(f"  Estágio  : FASE_{stage_name}")
    print(f"  DONE = exitcode 0  |  atual exitcode = {exit_code}")
    print(f"{sep}\n")
    return exit_code
```

**DONE =** `python validate_contracts.py --stage session-start` → mostra `FASE_SESSION_START`

---

### Item 4: Funções de gate novas em `validate_contracts.py` (EXISTENTE)

**Inserir após linha 6220** (fim de `_g_adversarial_analysis`):

**4a. HANDOFF_COHERENCE_GATE** (O5)
```python
def _g_handoff_coherence(root: pathlib.Path) -> dict:
    t0 = time.monotonic()
    gate_id = "HANDOFF_COHERENCE_GATE"
    handoff = root / "SESSION_HANDOFF.md"
    if not handoff.exists():
        return _skip(gate_id, "SESSION_HANDOFF.md ausente.", _ms(t0))
    text = handoff.read_text(encoding="utf-8")
    violations: list[dict] = []
    import re as _re
    m = _re.search(r"data_ultima_sessao[:\s]+(\d{4}-\d{2}-\d{2})", text)
    if m:
        try:
            delta = (datetime.date.today() - datetime.date.fromisoformat(m.group(1))).days
            if delta > 30:
                violations.append({
                    "blocking_code": "BLOCKED_HANDOFF_INCOMPLETE",
                    "artifact": "SESSION_HANDOFF.md",
                    "message": f"data_ultima_sessao há {delta} dias. Atualizar SESSION_HANDOFF.md.",
                    "severity": "warning",
                })
        except ValueError:
            pass
    try:
        proc = subprocess.run(["git", "branch", "--show-current"],
                              capture_output=True, text=True, cwd=root, timeout=5)
        current = proc.stdout.strip()
        bm = _re.search(r"branch_ativo[:\s]+(\S+)", text)
        if bm and current and bm.group(1) != current:
            violations.append({
                "blocking_code": "BLOCKED_HANDOFF_INCOMPLETE",
                "artifact": "SESSION_HANDOFF.md",
                "message": (f"branch_ativo='{bm.group(1)}' != branch atual='{current}'. "
                            f"Ação: atualizar SESSION_HANDOFF.md campo branch_ativo."),
                "severity": "error",
            })
    except Exception:
        pass
    if violations:
        return _pg(gate_id, "FAIL", False, "BLOCKED_HANDOFF_INCOMPLETE",
                   f"SESSION_HANDOFF.md com {len(violations)} inconsistência(s).",
                   [str(handoff)], [str(handoff)], [], violations, _ms(t0))
    return _pg(gate_id, "PASS", False, None,
               "SESSION_HANDOFF.md coerente.", [str(handoff)], [str(handoff)], [], [], _ms(t0))
```

**4b. MODULE_STATUS_COHERENCE_GATE** (O1) — blocking=true
```python
def _g_module_status_coherence(root: pathlib.Path) -> dict:
    t0 = time.monotonic()
    gate_id = "MODULE_STATUS_COHERENCE_GATE"
    registry_path = root / "docs" / "_canon" / "MODULE_REGISTRY.yaml"
    adversarial_dir = root / "_reports" / "adversarial"
    if not registry_path.exists():
        return _skip(gate_id, "MODULE_REGISTRY.yaml ausente.", _ms(t0))
    try:
        import yaml as _yaml
        registry = _yaml.safe_load(registry_path.read_text(encoding="utf-8"))
    except Exception as e:
        return _pg(gate_id, "FAIL", True, "BLOCKED_REGISTRY_MISMATCH",
                   f"Falha ao ler MODULE_REGISTRY.yaml: {e}",
                   [str(registry_path)], [str(registry_path)], [], [], _ms(t0))
    violations: list[dict] = []
    high_statuses = {"validated_contract", "implementation_ready"}
    for mod_name, mod_data in (registry.get("modules") or {}).items():
        if not isinstance(mod_data, dict):
            continue
        status = mod_data.get("status", "draft_contract")
        if status not in high_statuses or not adversarial_dir.exists():
            continue
        for rpath in adversarial_dir.rglob(f"*{mod_name}*.adversarial.json"):
            try:
                data = json.loads(rpath.read_text(encoding="utf-8"))
                overall = data.get("overall_status", "PASS")
                critical_open = len([r for r in (data.get("risks") or [])
                    if isinstance(r, dict)
                    and r.get("severity") == "critical"
                    and r.get("status") not in ("resolved", "accepted")])
                if overall != "PASS":
                    violations.append({
                        "blocking_code": "BLOCKED_ADVERSARIAL_PENDING",
                        "artifact": str(rpath.relative_to(root)),
                        "message": (f"Módulo '{mod_name}' status='{status}' mas adversarial={overall}. "
                                    f"Ação: rebaixar status ou corrigir análise adversarial."),
                        "severity": "error",
                    })
                elif critical_open > 0 and status == "implementation_ready":
                    violations.append({
                        "blocking_code": "BLOCKED_ADVERSARIAL_PENDING",
                        "artifact": str(rpath.relative_to(root)),
                        "message": (f"'{mod_name}' status='implementation_ready' com {critical_open} "
                                    f"risco(s) crítico(s) aberto(s). Resolver ou rebaixar status."),
                        "severity": "error",
                    })
            except Exception:
                pass
    if violations:
        return _pg(gate_id, "FAIL", True, "BLOCKED_REGISTRY_MISMATCH",
                   f"Status incoerente em {len(violations)} módulo(s).",
                   [str(registry_path)], [str(registry_path)], [], violations, _ms(t0))
    return _pg(gate_id, "PASS", True, None, "Status de módulos coerente com bloqueios.",
               [str(registry_path)], [str(registry_path)], [], [], _ms(t0))
```

**4c. Substituir corpo de `_g14_ui_doc_validation`** (O4 — atualmente sempre SKIP):
```python
def _g14_ui_doc_validation(root: pathlib.Path) -> dict:
    t0 = time.monotonic()
    gate_id = "UI_DOC_VALIDATION_GATE"
    ui_dir = root / "docs" / "hbtrack" / "modulos"
    paths_dir = root / "contracts" / "openapi" / "paths"
    openapi_f = root / "contracts" / "openapi" / "openapi.yaml"
    if not ui_dir.exists():
        return _skip(gate_id, "docs/hbtrack/modulos/ ausente.", _ms(t0))
    ui_contracts = list(ui_dir.rglob("UI_CONTRACT_*.md"))
    if not ui_contracts:
        return _skip(gate_id, "Nenhum UI_CONTRACT_*.md encontrado.", _ms(t0))
    if not openapi_f.exists():
        return _skip(gate_id, "openapi.yaml ausente.", _ms(t0))
    import re as _re
    all_oa = openapi_f.read_text(encoding="utf-8")
    if paths_dir.exists():
        for p in paths_dir.rglob("*.yaml"):
            all_oa += "\n" + p.read_text(encoding="utf-8")
    defined_ops = set(_re.findall(r"operationId:\s*(\S+)", all_oa))
    violations: list[dict] = []
    checked = []
    for ui_contract in ui_contracts:
        checked.append(str(ui_contract.relative_to(root)))
        ui_text = ui_contract.read_text(encoding="utf-8")
        candidates = set(_re.findall(r"`([a-z][a-zA-Z0-9]{5,})`", ui_text))
        op_refs = {r for r in candidates if any(c.isupper() for c in r[1:])}
        for op in op_refs:
            if op not in defined_ops:
                violations.append({
                    "blocking_code": "BLOCKED_CONTRACT_CONFLICT",
                    "artifact": str(ui_contract.relative_to(root)),
                    "message": (f"operationId '{op}' no UI contract não existe no OpenAPI. "
                                f"Adicionar ao training.yaml OU corrigir referência."),
                    "severity": "error",
                })
    if violations:
        return _pg(gate_id, "FAIL", False, "BLOCKED_CONTRACT_CONFLICT",
                   f"{len(violations)} operationId(s) sem correspondência.",
                   [], checked, [], violations, _ms(t0))
    return _pg(gate_id, "PASS", False, None,
               f"UI contracts alinhados ({len(checked)} arquivo(s)).", [], checked, [], [], _ms(t0))
```

**4d. Extensão de `_g_adversarial_analysis`** — score threshold (O6):
Localizar linha 6204 (`overall = data.get("overall_status")`). Inserir após:
```python
        score = data.get("score", 100)
        risks = data.get("risks") or []
        critical_open = len([r for r in risks if isinstance(r, dict)
            and r.get("severity") == "critical"
            and r.get("status") not in ("resolved", "accepted")])
        module_status = "draft_contract"
        reg_path = root / "docs" / "_canon" / "MODULE_REGISTRY.yaml"
        if reg_path.exists():
            try:
                import yaml as _yaml
                reg = _yaml.safe_load(reg_path.read_text(encoding="utf-8"))
                module_status = (reg.get("modules", {})
                                    .get(data.get("module", ""), {})
                                    .get("status", "draft_contract"))
            except Exception:
                pass
        min_score = 90 if module_status == "implementation_ready" else 80
        if score < min_score:
            violations.append({
                "blocking_code": "BLOCKED_ADVERSARIAL_PENDING",
                "artifact": str(rpath.relative_to(root)),
                "message": (f"Score {score}/100 < {min_score} exigido para '{module_status}'. "
                            f"Ação: resolver riscos e re-executar análise adversarial."),
                "severity": "error",
            })
        if module_status == "implementation_ready" and critical_open > 0:
            violations.append({
                "blocking_code": "BLOCKED_ADVERSARIAL_PENDING",
                "artifact": str(rpath.relative_to(root)),
                "message": (f"{critical_open} risco(s) crítico(s) aberto(s) bloqueiam "
                            f"'implementation_ready'. Ação: resolver RCs antes de avançar."),
                "severity": "error",
            })
```

**4e. WAIVER_ENGINE** em `_g9` — inserir antes de linha 5384:
```python
            # WAIVER_ENGINE: verificar waiver ativo antes de emitir FAIL
            waivers_dir = root / "contracts" / "_waivers"
            if waivers_dir.exists():
                for wpath in waivers_dir.glob("*.json"):
                    if wpath.name == "waiver.schema.json":
                        continue
                    try:
                        w = json.loads(wpath.read_text(encoding="utf-8"))
                        if w.get("gate_id") != gate_id:
                            continue
                        exp = w.get("expires_at_utc")
                        if exp:
                            exp_dt = datetime.datetime.fromisoformat(exp.replace("Z", "+00:00"))
                            if exp_dt < datetime.datetime.now(datetime.timezone.utc):
                                continue
                        return _pg(gate_id, "PASS", True, None,
                                   "Breaking change com waiver ativo aprovado.",
                                   [str(baseline), str(openapi_root)],
                                   [str(baseline), str(openapi_root)], [], [], _ms(t0))
                    except Exception:
                        pass
```

**4f. FSM_COMPLETENESS** em `validate_axiom_integrity` — inserir após validação de schema:
```python
    # FSM completeness: todo estado não-terminal deve ter ao menos 1 saída
    for sm_name, sm_def in (axioms_data.get("state_machines") or {}).items():
        if not isinstance(sm_def, dict):
            continue
        states = set(sm_def.get("states") or [])
        terminal_states = set(sm_def.get("terminal_states") or [])
        transitions = sm_def.get("transitions") or []
        states_with_exit = {t.get("from") for t in transitions if isinstance(t, dict)}
        for s in states:
            if s in terminal_states:
                continue
            if s not in states_with_exit:
                violations.append({
                    "blocking_code": "BLOCKED_AXIOM_VIOLATION",
                    "path": f"state_machines.{sm_name}.states.{s}",
                    "message": (f"Estado '{s}' sem transições de saída e não está em "
                                f"terminal_states. Declarar transição ou adicionar a terminal_states."),
                    "severity": "warning",
                })
```

**4g. Registrar novos gates em `run_pipeline()`** — após linha 7056:
```python
    gates.append(_g_handoff_coherence(root))
    gates.append(_g_module_status_coherence(root))
    # CROSS_MODULE_BOUNDARY: só se MODULE_SOURCE_AUTHORITY_MATRIX.yaml existir
    matrix = root / "docs" / "_canon" / "MODULE_SOURCE_AUTHORITY_MATRIX.yaml"
    if matrix.exists():
        gates.append(_g_cross_module_boundary(root))
```

**DONE =** `python validate_contracts.py --stage session-start` → HANDOFF_COHERENCE_GATE aparece em latest.json

---

### Item 5: Instruções no `pre_contract_orchestrator.prompt.md` (EXISTENTE)

**Localizar** cada `### Fase N` e adicionar LOGO APÓS o título:

```markdown
> **▶ CHECKPOINT — DONE = exitcode 0**
> Fase 0: `hb verify`  |  Fase 1: `hb check --module <mod>`  |  Fase 2: `hb artifact <path>`
> exitcode ≠ 0 → parar, ler log, corrigir, re-executar. **Não prosseguir para a próxima fase.**
```

**DONE =** `grep "DONE = exitcode 0" .contract_driven/agent_prompts/pre_contract_orchestrator.prompt.md` → encontra

---

### Item 6: `CLAUDE.md §6` — 2 regras (EXISTENTE)

**Localizar** `## 6. REGRAS CORE`. Adicionar ao final da árvore de decisão:

```
8. Antes de iniciar qualquer tarefa → hb verify → DONE = exitcode 0 → prosseguir
9. Após criar/modificar artefato canônico → hb artifact <path> → DONE = exitcode 0
```

**DONE =** `grep "hb verify" CLAUDE.md` → encontra

---

### Item 7: Ajustes canônicos em `GATES_REGISTRY.yaml` (EXISTENTE)

**Arquivo:** `docs/_canon/gates/GATES_REGISTRY.yaml`
**Inserir ao final da lista de gates:**

```yaml
  - gate_id: HANDOFF_COHERENCE_GATE
    order: 20A
    blocking: false
    stage: session-start
    description: "Verifica coerência de SESSION_HANDOFF.md com estado real do repo"
    implemented_in: scripts/contracts/validate/validate_contracts.py

  - gate_id: MODULE_STATUS_COHERENCE_GATE
    order: 20B
    blocking: true
    stage: session-start
    description: "Impede status alto com bloqueios adversariais ativos"
    implemented_in: scripts/contracts/validate/validate_contracts.py

  - gate_id: CROSS_MODULE_BOUNDARY_GATE
    order: 20C
    blocking: false
    stage: artifact
    description: "Verifica fronteiras cross-módulo contra MODULE_SOURCE_AUTHORITY_MATRIX"
    implemented_in: scripts/contracts/validate/validate_contracts.py
```

---

### Item 8: Atualização de `CONTRACT_PIPELINE.md` (EXISTENTE)

**Arquivo:** `docs/_canon/CONTRACT_PIPELINE.md`
**Localizar** a tabela de estágios (§2). Adicionar linha de Stage 0 e Stage 2:

```markdown
| Stage 0 | Pre-session | `hb verify` | session_start.json { stage0_exit_code:0 } | exitcode=0 |
| Stage 2 | Per-artifact | `hb artifact <path>` | session_start.json stage2_artifacts[...] | exitcode=0 |
```

---

### Item 9: `CLAUDE.md §8` — paths adicionais (EXISTENTE)

```
Pipeline CLI:           scripts/hb  (hb verify / hb artifact / hb check)
Session start:          _reports/session_start.json
Pipeline history:       _reports/pipeline_history.jsonl
Readiness dashboard:    _reports/READINESS_DASHBOARD.md
Pipeline health:        _reports/pipeline_health.json
```

---

## Tabela de ordem de implementação

| # | Item | Arquivo | Validação (DONE = exitcode 0) |
|---|---|---|---|
| 1 | CLI wrapper `hb` | scripts/hb (NOVO) | `chmod +x scripts/hb && hb help; echo $?` → 0 |
| 2 | pre-commit expansão | .git/hooks/pre-commit | Commitar sem session_start.json → EXIT 1 |
| 3 | `--stage` em main() | validate_contracts.py L7088 | `python validate_contracts.py --stage session-start; echo $?` → 0 |
| 4 | Novas funções gate (4a-4g) | validate_contracts.py | `python validate_contracts.py --stage session-start` → HANDOFF_COHERENCE_GATE no output |
| 5 | CHECKPOINT no orchestrator | pre_contract_orchestrator.prompt.md | `grep "DONE = exitcode 0" .contract_driven/agent_prompts/*.md` → encontra |
| 6 | §6 REGRAS CORE | CLAUDE.md | `grep "hb verify" CLAUDE.md` → encontra |
| 7 | GATES_REGISTRY | docs/_canon/gates/GATES_REGISTRY.yaml | `grep "HANDOFF_COHERENCE_GATE" docs/_canon/gates/GATES_REGISTRY.yaml` → encontra |
| 8 | CONTRACT_PIPELINE | docs/_canon/CONTRACT_PIPELINE.md | `grep "Stage 0" docs/_canon/CONTRACT_PIPELINE.md` → encontra |
| 9 | CLAUDE.md §8 | CLAUDE.md | `grep "session_start.json" CLAUDE.md` → encontra |

**Regra pós-cada item:** comparar `exit_code` em `_reports/contract_gates/latest.json` antes e depois.
Regressão → reverter e investigar antes de prosseguir ao próximo item.

---

## Verificação final do sistema

```bash
# 1. hb verify funciona (Fase 0)
hb verify && echo "FASE 0 DONE" || echo "FASE 0 FAIL exitcode=$?"

# 2. hb artifact funciona (Fase 2)
hb artifact contracts/openapi/paths/training.yaml && echo "FASE 2 DONE" || echo "FASE 2 FAIL"

# 3. Tier 2: pular Fase 0 bloqueia commit
rm -f _reports/session_start.json
echo "x" >> contracts/openapi/paths/training.yaml
git add contracts/openapi/paths/training.yaml SESSION_HANDOFF.md
git commit -m "test"  # → EXIT 1: session_start.json ausente
git restore contracts/openapi/paths/training.yaml

# 4. Tier 1: pular SESSION_HANDOFF bloqueia commit
echo "x" >> contracts/openapi/paths/training.yaml
git add contracts/openapi/paths/training.yaml   # sem SESSION_HANDOFF.md
git commit -m "test"  # → EXIT 1: SESSION_HANDOFF.md não staged
git restore contracts/openapi/paths/training.yaml

# 5. Full CI local
python scripts/contracts/validate/validate_contracts.py --profile ci
# → todos gates blocking=true devem ser PASS
```
