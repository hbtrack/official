# AR_070 — Add hb_plan_watcher daemon (atomic claim + dry-run + diff staging)

**Status**: 🔲 PENDENTE
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
_(A ser preenchido pelo Executor)_

---
## Carimbo de Execução
_(Gerado por hb report)_

