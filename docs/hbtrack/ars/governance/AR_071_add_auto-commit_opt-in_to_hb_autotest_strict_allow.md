# AR_071 — Add auto-commit opt-in to hb_autotest (strict allowlist + abort)

**Status**: ✅ VERIFICADO
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
**Arquivos impactados:**
- `scripts/run/hb_autotest.py` (modificação - adicionar lógica de auto-commit)

**Dependências:**
- Git (comandos diff, commit)
- Variável de ambiente HB_AUTO_COMMIT (opt-in)
- hb seal (já existente no hb_autotest.py)

**Riscos:**
- Commit acidental de arquivos não-auditados (mitigado por allowlist estrita)
- Mensagem de commit incorreta (mitigado por template padronizado)
- Feature opt-in garante compatibilidade com fluxo manual existente

**Impacto esperado**: Automação end-to-end do fluxo Testador (verify → seal → commit) com segurança via allowlist. Reduz overhead manual para ARs de baixo risco.

---
## Carimbo de Execução
_(Gerado por hb report)_


### Execução Executor em 457d095
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python -c "import pathlib; p=pathlib.Path('scripts/run/hb_autotest.py'); src=p.read_text(encoding='utf-8'); assert 'HB_AUTO_COMMIT' in src, 'HB_AUTO_COMMIT env var ausente'; assert 'allowlist' in src.lower(), 'Allowlist validation ausente'; assert 'abort' in src.lower() or 'return' in src, 'Abort-on-violation ausente'; assert 'auto_commit_if_enabled' in src, 'Função auto_commit_if_enabled ausente'; print('✅ hb_autotest auto-commit validado: opt-in + allowlist + abort')"`
**Exit Code**: 0
**Timestamp UTC**: 2026-02-24T04:37:21.233668+00:00
**Behavior Hash**: 659b3bfba6c3b88bdb2832aae9591d453765fab38f6cc054bb8a06877b64e72f
**Evidence File**: `docs/hbtrack/evidence/AR_071/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em 457d095
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_071_457d095/result.json`

### Selo Humano em a06d856
**Status Humano**: ✅ VERIFICADO
**Timestamp UTC**: 2026-02-24T19:04:38.628968+00:00
**Motivo**: —
**TESTADOR_REPORT**: `_reports/testador/AR_071_457d095/result.json`
**Evidence File**: `docs/hbtrack/evidence/AR_071/executor_main.log`
