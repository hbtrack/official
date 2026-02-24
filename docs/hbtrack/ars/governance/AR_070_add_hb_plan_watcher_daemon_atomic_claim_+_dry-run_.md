# AR_070 — Add hb_plan_watcher daemon (atomic claim + dry-run + diff staging)

**Status**: 🔴 REJEITADO
**Versão do Protocolo**: 1.2.0

## Descrição
Criar scripts/run/hb_plan_watcher.py que monitora docs/_canon/planos/*.json em loop, faz claim atômico por arquivo via lockfile (_reports/dispatch/plan_watcher/CLAIM_<hash>.lock), executa hb plan --dry-run antes de materializar (validação prévia) e faz staging apenas do diff produzido (ARs novas + _INDEX.md rebuild). Logs estruturados em _reports/dispatch/plan_watcher/<RUN_ID>/materialize_<timestamp>.log. Flags: --once (execução única), --dry-run (diagnóstico sem ação), --loop N (intervalo de poll em segundos, default 5).

## Critérios de Aceite
1) Claim atômico via lockfile impede dupla materialização do mesmo plan
2) Dry-run obrigatório antes de materialize (validação schema + gates)
3) Staging apenas diff before/after materialize (git diff --name-only)
4) Logs estruturados com RUN_ID único por execução
5) Flags --once, --dry-run, --loop implementadas
6) Daemon detecta novos JSONs via set difference (processed log)

## Write Scope
- scripts/run/hb_plan_watcher.py

## Validation Command (Contrato)
```
python -c "import pathlib; p=pathlib.Path('scripts/run/hb_plan_watcher.py'); assert p.exists(), 'hb_plan_watcher.py ausente'; src=p.read_text(encoding='utf-8'); assert 'CLAIM_' in src, 'Claim atômico ausente'; assert '--dry-run' in src, 'Dry-run flag ausente'; assert 'get_new_plans' in src, 'Detecção de novos plans ausente'; assert 'run_hb_plan' in src, 'Chamada hb plan ausente'; print('✅ hb_plan_watcher validado: claim + dry-run + diff staging')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_070/executor_main.log`

## Análise de Impacto
**Arquivos impactados:**
- `scripts/run/hb_plan_watcher.py` (criação nova)

**Dependências:**
- hb_cli.py (comando `plan`)
- Sistema de lockfiles (_reports/dispatch/plan_watcher/)
- Git staging para diff tracking

**Riscos:**
- Race condition se múltiplas instâncias rodarem (mitigado por lockfile atômico)
- Falha no dry-run pode bloquear materialização (comportamento desejado)
- Logs podem acumular sem rotação (aceito para MVP)

**Impacto esperado**: Daemon autônomo para materializar plans de forma segura e auditável. Reduz risco de materialização manual sem validação.

---
## Carimbo de Execução
_(Gerado por hb report)_


### Execução Executor em 457d095
**Status Executor**: ❌ FALHA
**Comando**: `python -c "import pathlib; p=pathlib.Path('scripts/run/hb_plan_watcher.py'); assert p.exists(), 'hb_plan_watcher.py ausente'; src=p.read_text(encoding='utf-8'); assert 'CLAIM_' in src, 'Claim atômico ausente'; assert '--dry-run' in src, 'Dry-run flag ausente'; assert 'get_new_plans' in src, 'Detecção de novos plans ausente'; assert 'run_hb_plan' in src, 'Chamada hb plan ausente'; print('✅ hb_plan_watcher validado: claim + dry-run + diff staging')"`
**Exit Code**: 1
**Timestamp UTC**: 2026-02-24T04:34:07.514432+00:00
**Behavior Hash**: 4eb75faf333aeefbd3dba5cbdf35060e03e70843bc5a1ced930887652fd63b65
**Evidence File**: `docs/hbtrack/evidence/AR_070/executor_main.log`
**Python Version**: 3.11.9


### Execução Executor em 457d095
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python -c "import pathlib; p=pathlib.Path('scripts/run/hb_plan_watcher.py'); assert p.exists(), 'hb_plan_watcher.py ausente'; src=p.read_text(encoding='utf-8'); assert 'CLAIM_' in src, 'Claim atômico ausente'; assert '--dry-run' in src, 'Dry-run flag ausente'; assert 'get_new_plans' in src, 'Detecção de novos plans ausente'; assert 'run_hb_plan' in src, 'Chamada hb plan ausente'; print('✅ hb_plan_watcher validado: claim + dry-run + diff staging')"`
**Exit Code**: 0
**Timestamp UTC**: 2026-02-24T04:35:06.204985+00:00
**Behavior Hash**: fa579aa5a7d33a95129db199c927628077db84528096a65567e0bab5147f82ff
**Evidence File**: `docs/hbtrack/evidence/AR_070/executor_main.log`
**Python Version**: 3.11.9


> 📋 Kanban routing: Arquiteto: Executor reported exit 0 but Testador got exit 1

### Verificacao Testador em 457d095
**Status Testador**: 🔴 REJEITADO
**Consistency**: AH_DIVERGENCE
**Triple-Run**: TRIPLE_FAIL (3x)
**Exit Testador**: 1 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_070_457d095/result.json`
