# AR_020 — Dev Flow v1.0.8 + hb_cli.py: cmd_verify, hb check C3 upgrade, bump protocolo (supersede AR_013)

**Status**: ⛔ SUPERSEDED — Dev Flow v1.0.8 check — Dev Flow está em v1.3.0; conteúdo absorvido por ARs de governança subsequentes
**Versão do Protocolo**: 1.0.6

## Descrição
SUPERSEDE AR_013. Esta task implementa: (A) bump protocolo v1.0.6→v1.0.8 em hb_cli.py, (B) novo comando hb verify (cmd_verify), (C) atualização hb check (C3 para VERIFICADO), (D) Dev Flow §9 + §10 + bump. Após completar, atualizar **Status** de AR_013 para '⛔ SUPERSEDED — ver AR_020'.

---
MUDANÇA A — scripts/run/hb_cli.py:

(A1) Linha com HB_PROTOCOL_VERSION:
Substituir '1.0.6' por '1.0.8'

(A2) Adicionar constantes de erro APÓS E_AR_ZERO_BYTES (linha ~88):
E_VERIFY_NOT_READY = 'E_VERIFY_NOT_READY'
E_VERIFY_NO_CMD = 'E_VERIFY_NO_CMD'
E_VERIFY_REQUIRES_VERIFIED = 'E_VERIFY_REQUIRES_VERIFIED'

(A3) Adicionar constante de diretório APÓS a linha EV_DIR (onde EV_DIR é definido, ~linha 35):
TESTADOR_DIR = '_reports/testador'

(A4) Adicionar função cmd_verify() APÓS a função cmd_report() e ANTES de cmd_check().
Implementação EXATA:

def cmd_verify(ar_id: str) -> None:
    """Comando: hb verify <id> — Testador independente re-executa validation_command"""
    import json as _json
    from datetime import datetime, timezone
    repo_root = get_repo_root()
    ar_dir = repo_root / AR_DIR

    # V1: Localizar AR
    ar_files = list(ar_dir.glob(f'AR_{ar_id}_*.md'))
    if not ar_files:
        fail(E_AR_NOT_FOUND, f'AR with id {ar_id} not found in {AR_DIR}/', exit_code=2)
    ar_file = ar_files[0]

    with open(ar_file, 'r', encoding='utf-8') as f:
        ar_content = f.read()

    # V2: Verificar SUCESSO
    if '\u2705 SUCESSO' not in ar_content:
        fail(E_VERIFY_NOT_READY,
             f'AR_{ar_id} must have \u2705 SUCESSO before verify. Run: hb report {ar_id} "<cmd>"',
             exit_code=4)

    # V3: Extrair validation_command
    import re
    match = re.search(r'## Validation Command \(Contrato\)\n```\n(.+?)\n```', ar_content, re.DOTALL)
    validation_cmd = match.group(1).strip() if match else ''
    if not validation_cmd:
        fail(E_VERIFY_NO_CMD,
             f'AR_{ar_id} has no Validation Command — not verifiable',
             exit_code=4)

    # V4: Re-executar validation_command
    print(f'\U0001f50d TESTADOR re-executing: {validation_cmd}')
    exit_code, stdout, stderr = run_cmd(validation_cmd)

    # V5: Ler Evidence Pack
    match_ev = re.search(r'## Evidence File \(Contrato\)\n`(.+?)`', ar_content)
    ev_path = match_ev.group(1).strip() if match_ev else ''
    executor_exit = None
    evidence_pack_complete = False
    if ev_path:
        ev_file = repo_root / ev_path
        if ev_file.exists():
            ev_content = ev_file.read_text(encoding='utf-8')
            evidence_pack_complete = True
            m = re.search(r'Exit Code: (\d+)', ev_content)
            if m:
                executor_exit = int(m.group(1))

    # V6: Consistency check
    if executor_exit is not None:
        if executor_exit == 0 and exit_code != 0:
            consistency = 'AH_DIVERGENCE'
        else:
            consistency = 'OK'
    else:
        consistency = 'UNKNOWN'

    # V7: Gerar TESTADOR_REPORT
    git_head = run_cmd('git rev-parse HEAD')[1].strip() or 'N/A'
    hash7 = git_head[:7]
    python_version = f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}'

    testador_run_dir = repo_root / TESTADOR_DIR / f'AR_{ar_id}_{hash7}'
    testador_run_dir.mkdir(parents=True, exist_ok=True)

    if exit_code == 0 and consistency == 'OK':
        status = 'VERIFICADO'
        ah_flags = []
        rejection_reason = None
    elif consistency == 'AH_DIVERGENCE':
        status = 'REJEITADO'
        ah_flags = ['AH_DIVERGENCE']
        rejection_reason = f'Executor reported exit 0 but Testador got exit {exit_code}'
    elif not evidence_pack_complete:
        status = 'REJEITADO'
        ah_flags = ['INCOMPLETE_EVIDENCE']
        rejection_reason = 'Evidence Pack missing or incomplete'
    else:
        status = 'REJEITADO'
        ah_flags = []
        rejection_reason = f'Re-execution failed: exit {exit_code}'

    context = {
        'run_id': f'TESTADOR-AR_{ar_id}-{hash7}',
        'timestamp_utc': datetime.now(timezone.utc).isoformat(),
        'git': {'commit': git_head},
        'environment': {'python_version': python_version},
        'ar_id': ar_id,
        'ar_file': str(ar_file.relative_to(repo_root))
    }
    result = {
        'ar_id': ar_id,
        'validation_command': validation_cmd,
        'testador_exit_code': exit_code,
        'executor_exit_code': executor_exit,
        'consistency': consistency,
        'status': status,
        'ah_flags': ah_flags,
        'evidence_pack_complete': evidence_pack_complete,
        'rejection_reason': rejection_reason
    }

    with open(testador_run_dir / 'context.json', 'w', encoding='utf-8') as f:
        _json.dump(context, f, indent=2, ensure_ascii=False)
    with open(testador_run_dir / 'result.json', 'w', encoding='utf-8') as f:
        _json.dump(result, f, indent=2, ensure_ascii=False)
    with open(testador_run_dir / 'stdout.log', 'w', encoding='utf-8') as f:
        f.write(stdout)
    with open(testador_run_dir / 'stderr.log', 'w', encoding='utf-8') as f:
        f.write(stderr)

    # V8: Atualizar **Status** header da AR
    if status == 'VERIFICADO':
        novo_status = '\u2705 VERIFICADO'
        final_exit = 0
    elif status == 'REJEITADO':
        novo_status = '\U0001f534 REJEITADO'
        final_exit = 2
    else:
        novo_status = '\u23f8\ufe0f BLOQUEADO_INFRA'
        final_exit = 3

    ar_updated = re.sub(r'\*\*Status\*\*:.*', f'**Status**: {novo_status}', ar_content, count=1)

    # V9: Append stamp de verificacao
    stamp = (f'\n### Verificacao Testador em {hash7}\n'
             f'**Status Testador**: {novo_status}\n'
             f'**Consistency**: {consistency}\n'
             f'**Exit Testador**: {exit_code} | **Exit Executor**: {executor_exit}\n'
             f'**TESTADOR_REPORT**: `{TESTADOR_DIR}/AR_{ar_id}_{hash7}/result.json`\n')
    ar_updated = ar_updated + stamp

    with open(ar_file, 'w', encoding='utf-8') as f:
        f.write(ar_updated)

    print(f'{novo_status} | Consistency: {consistency}')
    if rejection_reason:
        print(f'Reason: {rejection_reason}')
    print(f'Report: {TESTADOR_DIR}/AR_{ar_id}_{hash7}/result.json')
    sys.exit(final_exit)

(A5) Atualizar cmd_check: substituir a verificação de '\u2705 SUCESSO' no bloco C3 para ser version-aware.
NA função cmd_check, no bloco 'if any(...)' que verifica '\u2705 SUCESSO' em ar_content:

Substituir:
    if '\u2705 SUCESSO' in ar_content:

Por:
    # Version-aware: v1.0.8+ exige VERIFICADO; anterior aceita SUCESSO
    ar_proto_m = re.search(r'\*\*Vers\u00e3o do Protocolo\*\*: ([\d.]+)', ar_content)
    ar_proto = ar_proto_m.group(1) if ar_proto_m else '1.0.0'
    try:
        ar_proto_tuple = tuple(int(x) for x in ar_proto.split('.'))
    except Exception:
        ar_proto_tuple = (1, 0, 0)
    requires_verified = ar_proto_tuple >= (1, 0, 8)
    has_valid_status = ('\u2705 VERIFICADO' in ar_content) if requires_verified else ('\u2705 SUCESSO' in ar_content or '\u2705 VERIFICADO' in ar_content)
    if has_valid_status:

(A6) Atualizar main dispatcher (bloco elif no final de hb_cli.py):
Após o bloco 'elif command == "report":', adicionar:

    elif command == 'verify':
        if len(sys.argv) < 3:
            fail('E_USAGE', 'Usage: hb verify <id>')
        cmd_verify(sys.argv[2])

---
MUDANÇA B — docs/_canon/contratos/Dev Flow.md:

(B1) Linha 1: substituir 'v1.0.6' por 'v1.0.8'
(B2) §1 versão: substituir todas ocorrências de 'v1.0.6' por 'v1.0.8' em §1
(B3) §5 Ciclo de Vida (7 passos): adicionar Passo 6.5 ENTRE Passo 6 e Passo 7:

Passo 6.5 — TESTADOR
O Testador executa:
- python scripts/run/hb_cli.py verify <id>

Regras:
- O Testador re-executa o Validation Command independentemente.
- Grava TESTADOR_REPORT em _reports/testador/.
- Atualiza Status da AR para ✅ VERIFICADO (PASS) ou 🔴 REJEITADO (FAIL).
- Se REJEITADO: Executor MUST corrigir e repetir Passo 5→6→6.5.

(B4) §6 Regras determinísticas: substituir na regra R2:
    'AR com marcador ✅ SUCESSO'
    por:
    'AR com marcador ✅ VERIFICADO (v1.0.8+) ou ✅ SUCESSO (protocolo anterior)'

(B5) Adicionar ao final do arquivo (antes de '## 8. Nota de estabilidade') as seções §9 e §10:

## 9. Regras de Governança de ARs (obrigatório — mecanizado)

R-AR-1) _INDEX.md é AUTO-GERADO por hb plan e hb report. MUST NOT ser editado manualmente.
R-AR-2) ARs com Status ✅ VERIFICADO são IMUTÁVEIS. Corpo da AR não pode ser alterado manualmente.
R-AR-3) O hook pre-commit BLOQUEIA commits onde: (a) AR staged sem _INDEX.md staged (E_AR_INDEX_NOT_STAGED), (b) AR VERIFICADO teve corpo modificado manualmente (E_AR_IMMUTABLE).
R-AR-4) Status válidos: DRAFT | 🏗️ EM_EXECUCAO | ✅ SUCESSO | ✅ VERIFICADO | ❌ FALHA | 🔴 REJEITADO | ⏸️ BLOQUEADO_INFRA | ⛔ SUPERSEDED
R-AR-5) Toda AR MUST ser materializada via hb plan a partir de Plan JSON válido. Criação manual proibida.

## 10. Regras Anti-Alucinação (obrigatório)

R-AH-1) Source-inspection-only é proibido como único gate para tasks de código.
R-AH-2) Validation commands trivialmente passáveis são proibidos.
R-AH-3) O Testador MUST re-executar independentemente — nunca confiar no output do Executor.
R-AH-4) AH_DIVERGENCE (Executor=0, Testador!=0) resulta em REJEITADO automático.
R-AH-5) ERROR_INFRA no Testador gera BLOQUEADO_INFRA — não REJEITADO.
Ver contrato completo: docs/_canon/contratos/Testador Contract.md

---
FINAL: Após implementar A e B, atualizar manualmente o campo **Status** de AR_013 para '⛔ SUPERSEDED — ver AR_020'.
ARQUIVOS A MODIFICAR: scripts/run/hb_cli.py e docs/_canon/contratos/Dev Flow.md
NAO modificar nenhum outro arquivo.

## Critérios de Aceite
1) python scripts/run/hb_cli.py version retorna 'HB Track Protocol v1.0.8'. 2) hb verify 999 retorna E_AR_NOT_FOUND (exit != 0). 3) Dev Flow.md contém 'v1.0.8'. 4) Dev Flow.md contém 'Passo 6.5'. 5) Dev Flow.md contém '## 9. Regras de Governança' e '## 10. Regras Anti-Alucinação'. 6) hb_cli.py contém 'TESTADOR_DIR'. 7) hb_cli.py contém 'E_VERIFY_NOT_READY'. 8) AR_013 marcada como SUPERSEDED.

## Validation Command (Contrato)
```
python -c "import subprocess, pathlib; v=subprocess.run(['python','scripts/run/hb_cli.py','version'],capture_output=True,text=True,encoding='utf-8').stdout.strip(); assert 'v1.0.8' in v, f'FAIL version: {v}'; r=subprocess.run(['python','scripts/run/hb_cli.py','verify','999'],capture_output=True,text=True,encoding='utf-8'); assert r.returncode!=0, 'FAIL: verify should fail for unknown AR'; assert 'E_AR_NOT_FOUND' in r.stderr or '999' in r.stderr, f'FAIL E_AR_NOT_FOUND missing: {r.stderr[:200]}'; df=pathlib.Path('docs/_canon/contratos/Dev Flow.md').read_text(encoding='utf-8'); assert 'v1.0.8' in df,'FAIL: Dev Flow not v1.0.8'; assert 'Passo 6.5' in df,'FAIL: Passo 6.5 missing'; print('PASS: v1.0.8 + hb verify + Dev Flow Passo 6.5 OK')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_020_gov_testador_v108_implementation.log`

## Rollback Plan (Contrato)
```
git revert HEAD
# OU:
# git restore scripts/run/hb_cli.py
# git restore "docs/_canon/contratos/Dev Flow.md"
```
⚠️ **ATENÇÃO**: Este AR modifica banco. Execute rollback em caso de falha.

## Riscos
- cmd_verify usa unicode literals (\u2705 etc.) na string — garantir que o arquivo hb_cli.py seja salvo em UTF-8 e que os emojis sejam inseridos diretamente (não como escapes) para compatibilidade com re.sub.
- A mudança A5 (cmd_check version-aware) deve substituir EXATAMENTE a linha 'if "✅ SUCESSO" in ar_content:' — localizar com grep antes de editar.
- A mudança A6 (main dispatcher) deve manter a estrutura elif existente — não criar um if separado.
- Dev Flow.md §5 Ciclo de Vida: o Passo 6.5 deve ser inserido ENTRE 'Passo 6 — VALIDAÇÃO' e 'Passo 7 — FECHAMENTO' preservando numeração existente.
- AR_013 tem **Status**: DRAFT — atualizar para '⛔ SUPERSEDED — ver AR_020' via Edit direto no arquivo AR_013.
- TESTADOR_DIR = '_reports/testador' deve ser definido como string constante no topo do arquivo, junto com AR_DIR e EV_DIR.

## Análise de Impacto
- Arquivos afetados: [scripts/run/hb_cli.py, docs/_canon/contratos/Dev Flow.md]
- Mudança no Schema? [Não]
- Risco de Regressão? [Médio]

---
## Carimbo de Execução
_(Gerado por hb report)_



### Execução em b2e7523
**Status Final**: ✅ SUCESSO
**Comando**: `python -c "import subprocess, pathlib; v=subprocess.run(['python','scripts/run/hb_cli.py','version'],capture_output=True,text=True,encoding='utf-8').stdout.strip(); assert 'v1.0.8' in v, f'FAIL version: {v}'; r=subprocess.run(['python','scripts/run/hb_cli.py','verify','999'],capture_output=True,text=True,encoding='utf-8'); assert r.returncode!=0, 'FAIL: verify should fail for unknown AR'; assert 'E_AR_NOT_FOUND' in r.stderr or '999' in r.stderr, f'FAIL E_AR_NOT_FOUND missing: {r.stderr[:200]}'; df=pathlib.Path('docs/_canon/contratos/Dev Flow.md').read_text(encoding='utf-8'); assert 'v1.0.8' in df,'FAIL: Dev Flow not v1.0.8'; assert 'Passo 6.5' in df,'FAIL: Passo 6.5 missing'; print('PASS: v1.0.8 + hb verify + Dev Flow Passo 6.5 OK')"`
**Exit Code**: 0
**Evidence File**: `docs/hbtrack/evidence/AR_020_gov_testador_v108_implementation.log`
**Python Version**: 3.11.9


### Verificacao Testador em b2e7523
**Status Testador**: 🔴 REJEITADO
**Consistency**: AH_DIVERGENCE
**Triple-Run**: TRIPLE_FAIL (3x)
**Exit Testador**: 1 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_020_b2e7523/result.json`
