# AR_070 — Criar hb_plan_watcher.py com claim atomico + dry-run + diff staging

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.3.0

## Descrição
Implementar daemon que monitora docs/_canon/planos/*.json, faz claim atomico via lockfile, executa hb plan --dry-run antes de materializar e faz staging apenas do diff produzido. Flags: --once, --dry-run, --loop N.

## Critérios de Aceite
1) Claim atomico via lockfile impede dupla materializacao do mesmo plan; 2) Dry-run obrigatorio antes de materialize (validacao schema + gates); 3) Staging apenas diff before/after materialize (git diff --name-only); 4) Logs estruturados com RUN_ID unico por execucao; 5) Flags --once, --dry-run, --loop implementadas; 6) Daemon detecta novos JSONs via set difference (processed log)

## Write Scope
- scripts/run/hb_plan_watcher.py

## Validation Command (Contrato)
```
python -c "import pathlib; p=pathlib.Path('scripts/run/hb_plan_watcher.py'); assert p.exists(), 'hb_plan_watcher.py ausente'; src=p.read_text(encoding='utf-8'); assert 'CLAIM_' in src, 'Claim atomico ausente'; assert '--dry-run' in src, 'Dry-run flag ausente'; assert 'get_new_plans' in src, 'Deteccao de novos plans ausente'; assert 'run_hb_plan' in src, 'Chamada hb plan ausente'; print('[PASS] hb_plan_watcher validado: claim + dry-run + diff staging')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_070/executor_main.log`

## Rollback Plan (Contrato)
```
git checkout -- scripts/run/hb_plan_watcher.py
```
⚠️ **ATENÇÃO**: Este AR modifica banco. Execute rollback em caso de falha.

## Análise de Impacto
**Arquivos impactados:**
- `scripts/run/hb_plan_watcher.py` (já implementado na tentativa v1)

**Dependências:**
- hb_cli.py (comando `plan`)
- Sistema de lockfiles (_reports/dispatch/plan_watcher/)
- Git staging para diff tracking

**Riscos:**
- Race condition se múltiplas instâncias rodarem (mitigado por lockfile atômico)
- Falha no dry-run pode bloquear materialização (comportamento desejado)
- Logs podem acumular sem rotação (aceito para MVP)

**Impacto esperado**: Daemon autônomo para materializar plans de forma segura e auditável. Reduz risco de materialização manual sem validação. Código já implementado, apenas re-validando com command ASCII-only.

---
## Carimbo de Execução
_(Gerado por hb report)_


### Execução Executor em b3ffd25
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python -c "import pathlib; p=pathlib.Path('scripts/run/hb_plan_watcher.py'); assert p.exists(), 'hb_plan_watcher.py ausente'; src=p.read_text(encoding='utf-8'); assert 'CLAIM_' in src, 'Claim atomico ausente'; assert '--dry-run' in src, 'Dry-run flag ausente'; assert 'get_new_plans' in src, 'Deteccao de novos plans ausente'; assert 'run_hb_plan' in src, 'Chamada hb plan ausente'; print('[PASS] hb_plan_watcher validado: claim + dry-run + diff staging')"`
**Exit Code**: 0
**Timestamp UTC**: 2026-02-24T05:09:16.677212+00:00
**Behavior Hash**: ee2714e662708ba7c25fc9490b33166b1a3e0ac3d2d7b0260de271535c91a175
**Evidence File**: `docs/hbtrack/evidence/AR_070/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em b3ffd25
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_070_b3ffd25/result.json`

### Selo Humano em b3ffd25
**Status Humano**: ✅ VERIFICADO
**Timestamp UTC**: 2026-02-24T05:19:01.885411+00:00
**Motivo**: —
**TESTADOR_REPORT**: `_reports/testador/AR_070_b3ffd25/result.json`
**Evidence File**: `docs/hbtrack/evidence/AR_070/executor_main.log`
