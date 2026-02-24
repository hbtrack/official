# AR_072 — Governance: Document daemons + bump PROTOCOL_VERSION v1.3.0

**Status**: 🔲 PENDENTE
**Versão do Protocolo**: 1.2.0

## Descrição
Atualizar docs/_canon/contratos/Dev Flow.md: (1) §2.5 'Execução (scripts)' para documentar hb_plan_watcher.py (auto-materialize daemon), (2) adicionar §10.5 'AUTO-COMMIT (OPCIONAL)' documentando policy completa de auto-commit opt-in (env var, allowlist, abort, mensagem padronizada), (3) §1.1 bump PROTOCOL_VERSION de v1.2.0 para v1.3.0. Atualizar scripts/run/hb_cli.py linha 49: HB_PROTOCOL_VERSION='1.3.0'. Garantir que hb version e header do hb check reportem v1.3.0 corretamente.

## Critérios de Aceite
1) Dev Flow §2.5 menciona hb_plan_watcher.py (auto-materialize daemon)
2) Dev Flow novo §10.5 documenta auto-commit opt-in policy completa
3) Dev Flow §1.1 PROTOCOL_VERSION=v1.3.0
4) hb_cli.py linha 49 HB_PROTOCOL_VERSION='1.3.0'
5) hb version reporta 1.3.0 (stdout)
6) hb check header reporta Protocol v1.3.0

## Write Scope
- docs/_canon/contratos/Dev Flow.md
- scripts/run/hb_cli.py

## Validation Command (Contrato)
```
python -c "import pathlib; flow=pathlib.Path('docs/_canon/contratos/Dev Flow.md').read_text(encoding='utf-8'); assert 'hb_plan_watcher' in flow, 'hb_plan_watcher ausente no Dev Flow'; assert 'auto-commit' in flow.lower() or 'AUTO-COMMIT' in flow, 'auto-commit policy ausente no Dev Flow'; assert 'v1.3.0' in flow, 'v1.3.0 ausente no Dev Flow'; cli=pathlib.Path('scripts/run/hb_cli.py').read_text(encoding='utf-8'); assert 'HB_PROTOCOL_VERSION = \"1.3.0\"' in cli, 'HB_PROTOCOL_VERSION não bumpado para 1.3.0'; print('✅ Governança v1.3.0 validada: Dev Flow + hb_cli.py')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_072/executor_main.log`

## Análise de Impacto
_(A ser preenchido pelo Executor)_

---
## Carimbo de Execução
_(Gerado por hb report)_

