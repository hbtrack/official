# AR_029 — Evidence Integrity: SHA-256 Checksum + Git-Status Pre-Check Anti-Forja

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.1.0

## Descrição
ARQUIVO ALVO: scripts/run/hb_cli.py

### Problema
1) O Evidence Pack prova que o comando rodou, mas NÃO prova que o código testado é o mesmo que será commitado. O Executor pode alterar arquivos DEPOIS do teste.
2) O Testador pode gerar 'falsa evidência' se houver arquivos residuais não-commitados no workspace.

### Implementação (PATCH MÍNIMO)

(I1) FUNÇÃO compute_governed_checksum — inserir ANTES de cmd_report:

def compute_governed_checksum() -> Dict[str, str]:
    """Computa SHA-256 dos arquivos em GOVERNED_ROOTS que estão staged ou modified.
    Retorna dict {relative_path: sha256_hex_16}.
    Anti-forja: prova que o código no momento do teste é o código commitado.
    """
    import hashlib as _hl
    result = {}
    try:
        # Pega arquivos staged + modified nos governed roots
        out = subprocess.run(
            ['git', 'diff', '--name-only', 'HEAD'],
            capture_output=True, text=True, encoding='utf-8'
        )
        files = [f.strip() for f in out.stdout.strip().split('\n') if f.strip()]
        for fpath in files:
            for root in GOVERNED_ROOTS:
                if fpath.startswith(root):
                    try:
                        content = Path(fpath).read_bytes()
                        result[fpath] = _hl.sha256(content).hexdigest()[:16]
                    except FileNotFoundError:
                        result[fpath] = 'DELETED'
                    break
    except Exception:
        pass
    return result

(I2) FUNÇÃO check_workspace_clean — inserir APÓS compute_governed_checksum:

def check_workspace_clean() -> Tuple[bool, str]:
    """Verifica se o workspace tem arquivos não-commitados que podem contaminar o teste.
    Retorna (is_clean, status_summary).
    """
    try:
        out = subprocess.run(
            ['git', 'status', '--porcelain'],
            capture_output=True, text=True, encoding='utf-8'
        )
        lines = [l for l in out.stdout.strip().split('\n') if l.strip()]
        if not lines:
            return True, 'workspace_clean'
        return False, f'dirty_files={len(lines)}'
    except Exception as e:
        return False, f'git_error={e}'

(I3) INTEGRAR em cmd_report — APÓS execução do comando e ANTES de gravar evidence:
    # Evidence Integrity: checksum anti-forja
    governed_checksums = compute_governed_checksum()
    workspace_clean, workspace_status = check_workspace_clean()

Adicionar ao evidence pack (.log) as linhas:
    f'Governed Checksums: {json.dumps(governed_checksums)}'
    f'Workspace Status: {workspace_status}'

(I4) INTEGRAR em cmd_verify — ANTES do loop triple-run:
    # Pre-check: workspace limpo (anti-falsa-evidência)
    ws_clean, ws_status = check_workspace_clean()
    if not ws_clean:
        print(f'⚠️ WARNING: workspace não-limpo ({ws_status}). Resultados podem ser contaminados.')
    # Checksum snapshot ANTES do verify
    pre_checksums = compute_governed_checksum()

E APÓS o loop triple-run:
    # Checksum snapshot APÓS verify — comparar com pré
    post_checksums = compute_governed_checksum()
    checksum_drift = pre_checksums != post_checksums
    if checksum_drift:
        print('⚠️ WARNING: checksums mudaram DURANTE verify — possível contaminação')

Adicionar ao result dict:
    'governed_checksums_pre': pre_checksums,
    'governed_checksums_post': post_checksums,
    'checksum_drift': checksum_drift,
    'workspace_clean': ws_clean,

NÃO MODIFICAR lógica de validação existente. APENAS adicionar funções + integrar.

## Critérios de Aceite
1) hb_cli.py contém compute_governed_checksum(). 2) hb_cli.py contém check_workspace_clean(). 3) cmd_report grava 'Governed Checksums' no evidence. 4) cmd_verify checa workspace_clean antes do triple-run. 5) cmd_verify compara checksums pre/post verify. 6) hb version retorna v1.1.0 (não regride).

## Validation Command (Contrato)
```
python -c "import pathlib,subprocess,sys; hb=pathlib.Path('scripts/run/hb_cli.py').read_text(encoding='utf-8'); assert 'compute_governed_checksum' in hb,'FAIL no compute_governed_checksum'; assert 'check_workspace_clean' in hb,'FAIL no check_workspace_clean'; assert 'governed_checksums' in hb.lower() or 'Governed Checksums' in hb,'FAIL no governed_checksums in evidence'; assert 'workspace_clean' in hb,'FAIL no workspace_clean'; assert 'checksum_drift' in hb,'FAIL no checksum_drift'; v=subprocess.run([sys.executable,'scripts/run/hb_cli.py','version'],capture_output=True,text=True,encoding='utf-8'); assert 'v1.1.0' in v.stdout,f'FAIL version={v.stdout.strip()}'; print('PASS: Evidence Integrity (SHA-256 + git-status + anti-forja) OK')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_029_evidence_integrity_antiforja.log`

## Riscos
- compute_governed_checksum usa git diff HEAD — OK para detectar staged+modified vs último commit
- check_workspace_clean com git status --porcelain — cross-platform e parseável
- Se git não disponível, funções retornam gracefully ({} e False) — não quebra o fluxo
- Checksum drift (pre!=post) durante verify indica que algo modificou código DURANTE o teste — grave mas raro
- WARNING de workspace sujo NÃO bloqueia — é informativo. Bloqueio seria breaking change demais

## Análise de Impacto
_(A ser preenchido pelo Executor)_

---
## Carimbo de Execução
_(Gerado por hb report)_


### Execução em b2e7523
**Status Final**: ✅ SUCESSO
**Comando**: `python -c "import pathlib,subprocess,sys; hb=pathlib.Path('scripts/run/hb_cli.py').read_text(encoding='utf-8'); assert 'compute_governed_checksum' in hb,'FAIL no compute_governed_checksum'; assert 'check_workspace_clean' in hb,'FAIL no check_workspace_clean'; assert 'governed_checksums' in hb.lower() or 'Governed Checksums' in hb,'FAIL no governed_checksums in evidence'; assert 'workspace_clean' in hb,'FAIL no workspace_clean'; assert 'checksum_drift' in hb,'FAIL no checksum_drift'; v=subprocess.run([sys.executable,'scripts/run/hb_cli.py','version'],capture_output=True,text=True,encoding='utf-8'); assert 'v1.1.0' in v.stdout,f'FAIL version={v.stdout.strip()}'; print('PASS: Evidence Integrity (SHA-256 + git-status + anti-forja) OK')"`
**Exit Code**: 0
**Evidence File**: `docs/hbtrack/evidence/AR_029_evidence_integrity_antiforja.log`
**Python Version**: 3.11.9


### Verificacao Testador em b2e7523
**Status Testador**: ✅ VERIFICADO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_029_b2e7523/result.json`

### Verificacao Testador em b2e7523
**Status Testador**: ✅ VERIFICADO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_029_b2e7523/result.json`
