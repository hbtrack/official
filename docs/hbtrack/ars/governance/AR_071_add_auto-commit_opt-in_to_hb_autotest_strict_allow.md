# AR_071 — Add auto-commit opt-in to hb_autotest (strict allowlist + abort)

**Status**: 🔲 PENDENTE
**Versão do Protocolo**: 1.2.0

## Descrição
Modificar scripts/run/hb_autotest.py para, após hb seal marcar ✅ VERIFICADO com sucesso, executar git commit automaticamente SOMENTE SE: (1) variável de ambiente HB_AUTO_COMMIT=1 estiver setada (opt-in explícito), (2) todos os staged files estejam na allowlist exata da AR (docs/hbtrack/evidence/AR_<id>/, docs/hbtrack/ars/**, _reports/testador/AR_<id>/, docs/hbtrack/_INDEX.md). Se qualquer arquivo staged estiver FORA da allowlist, aborta commit e loga erro detalhado. Mensagem de commit padronizada: 'feat(ar_<id>): <title> [VERIFICADO]' + metadata (evidence path, report path, protocol version, auto-commit agent).

## Critérios de Aceite
1) HB_AUTO_COMMIT=1 controla feature (default OFF se variável ausente)
2) Allowlist exata por AR valida TODOS os staged files
3) Em violação de allowlist, aborta commit e loga paths violadores
4) Não usa 'git add .' (commit APENAS staged files pré-existentes)
5) Mensagem padronizada inclui Protocol version e agent
6) Função auto_commit_if_enabled chamada após hb seal bem-sucedido

## Write Scope
- scripts/run/hb_autotest.py

## Validation Command (Contrato)
```
python -c "import pathlib; p=pathlib.Path('scripts/run/hb_autotest.py'); src=p.read_text(encoding='utf-8'); assert 'HB_AUTO_COMMIT' in src, 'HB_AUTO_COMMIT env var ausente'; assert 'allowlist' in src.lower(), 'Allowlist validation ausente'; assert 'abort' in src.lower() or 'return' in src, 'Abort-on-violation ausente'; assert 'auto_commit_if_enabled' in src, 'Função auto_commit_if_enabled ausente'; print('✅ hb_autotest auto-commit validado: opt-in + allowlist + abort')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_071/executor_main.log`

## Análise de Impacto
_(A ser preenchido pelo Executor)_

---
## Carimbo de Execução
_(Gerado por hb report)_

