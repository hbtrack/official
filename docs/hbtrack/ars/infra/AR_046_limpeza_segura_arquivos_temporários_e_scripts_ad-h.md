# AR_046 — Limpeza Segura: Arquivos Temporários e Scripts Ad-hoc

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.1.0

## Descrição
ARQUIVOS ALVO: Raiz do repositório (múltiplos arquivos temporários e scripts ad-hoc)

### Problema
O repositório está cheio de arquivos temporários, scripts ad-hoc e artefatos de debug que foram criados durante implementações e testes. Esses arquivos poluem o workspace, dificultam navegação, criam ruído no git status, e podem causar bugs se executados acidentalmente. A governança exige um repositório limpo e organizado.

**Arquivos identificados para remoção**:

**Categoria 1: Scripts Ad-hoc de Debug/Test (REMOVER)**
- check_ar_status.py
- complete_ar_reports.py
- consolidar_docs.py
- mark_blocked_ars.py
- preparar_contexto.py
- rebuild_index_real.py
- testador_final_report.py
- insert_vps_policy.py
- temp_validate_ar002.py
- test_gate_f.py
- validate_ar_translation.py
- temp_report_032.py
- temp_report_033.py
- temp_report_038.py
- temp_report_039.py
- temp_report_040.py
- temp_report_041.py
- temp_report_042.py
- temp_report_043.py
- temp_report_044.py
- fix_moves_044.py
- fix_moves_045.py
- validation_ar036.log

**Categoria 2: Scripts Batch/PowerShell Ad-hoc (REMOVER)**
- report_ar002.bat
- run_report_ar002.ps1

**Categoria 3: Arquivos de Documentação Temporária (REMOVER)**
- gemini.md
- Hb Track KANBAN.md
- tarefa_atual.md
- protocolo de correção.txt

**Categoria 4: Artefatos de Output/Cache (REMOVER)**
- arquivos_consolidados.txt
- docs_consolidado.txt
- _audit_output.txt
- tmp_plan.json

**Categoria 5: Arquivos de Teste Frontend (AVALIAR)**
- test-cookie-flow.js

### Implementação

**FASE 1: BACKUP SAFETY CHECK**
Antes de remover qualquer arquivo, verificar:
1. Arquivo não está referenciado em código crítico
2. Arquivo não está em uso por processo ativo
3. Git status clean ou arquivos estão untracked

**FASE 2: REMOÇÃO SEGURA (Python Script)**
```python
import pathlib
import shutil
import datetime

# Lista de arquivos temporários para remover
temp_files = [
    'gemini.md', 'preparar_contexto.py', 'testador_final_report.py',
    'complete_ar_reports.py', 'rebuild_index_real.py', 'mark_blocked_ars.py',
    'insert_vps_policy.py', 'check_ar_status.py', 'consolidar_docs.py',
    'temp_validate_ar002.py', 'test_gate_f.py', 'tmp_plan.json',
    'validate_ar_translation.py', 'report_ar002.bat', 'run_report_ar002.ps1',
    'arquivos_consolidados.txt', 'docs_consolidado.txt', '_audit_output.txt',
    'protocolo de correção.txt', 'Hb Track KANBAN.md', 'tarefa_atual.md',
    'test-cookie-flow.js',
    'temp_report_032.py', 'temp_report_033.py', 'temp_report_038.py',
    'temp_report_039.py', 'temp_report_040.py', 'temp_report_041.py',
    'temp_report_042.py', 'temp_report_043.py', 'temp_report_044.py',
    'fix_moves_044.py', 'fix_moves_045.py', 'validation_ar036.log'
]

# Criar evidence log
evidence_path = pathlib.Path('docs/hbtrack/evidence')
evidence_path.mkdir(parents=True, exist_ok=True)
log_file = evidence_path / 'AR_046_removed_files.log'

with open(log_file, 'w', encoding='utf-8') as log:
    log.write('AR_046 - Limpeza Segura de Arquivos Temporários\n')
    log.write(f'Timestamp: {datetime.datetime.utcnow().isoformat()}Z\n\n')
    log.write('ARQUIVOS REMOVIDOS:\n')
    
    total_size = 0
    removed_count = 0
    
    for fname in temp_files:
        fpath = pathlib.Path(fname)
        if fpath.exists():
            try:
                size = fpath.stat().st_size
                fpath.unlink()
                log.write(f'- {fname} ({size/1024:.1f} KB)\n')
                total_size += size
                removed_count += 1
            except Exception as e:
                log.write(f'- {fname} (FALHA: {e})\n')
    
    log.write(f'\n[total: {removed_count} arquivos, {total_size/1024:.1f} KB liberados]\n\n')
    
    # Limpar pastas temporárias
    log.write('PASTAS LIMPAS:\n')
    temp_dirs = ['.hb_guard', '.hb_tmp_tests']
    for dirname in temp_dirs:
        dpath = pathlib.Path(dirname)
        if dpath.exists() and dpath.is_dir():
            count = len(list(dpath.rglob('*')))
            try:
                shutil.rmtree(dpath)
                dpath.mkdir(exist_ok=True)  # Recriar vazia
                log.write(f'- {dirname}/ ({count} arquivos removidos)\n')
            except Exception as e:
                log.write(f'- {dirname}/ (FALHA: {e})\n')
    
    # Verificar arquivos críticos
    log.write('\nARQUIVOS CRÍTICOS VERIFICADOS (PRESERVADOS):\n')
    critical = [
        'scripts/run/hb_cli.py', 'docs/hbtrack/_INDEX.md',
        'scripts', 'docs', 'Hb Track - Backend', 'Hb Track - Frontend', '.gitignore'
    ]
    all_ok = True
    for crit in critical:
        exists = pathlib.Path(crit).exists()
        status = '✓' if exists else '✗'
        log.write(f'{status} {crit}\n')
        if not exists:
            all_ok = False
    
    log.write(f'\nSTATUS: {"✅ LIMPEZA CONCLUÍDA SEM QUEBRAS" if all_ok else "❌ FALHA - ARQUIVOS CRÍTICOS FALTANDO"}')

print(f'Limpeza concluída. Evidence: {log_file}')
```

**FASE 3: VALIDAÇÃO PÓS-LIMPEZA**
O validation_command verifica:
- Arquivos críticos existem
- Arquivos temporários foram removidos
- Evidence log foi criado
- .gitignore preservado com entradas corretas

**REGRAS DE SEGURANÇA**:
1. NUNCA remover: scripts/, docs/, backends, frontends, infra/, .git/
2. NUNCA remover: .gitignore, .clinerules, hb_cli.py, _INDEX.md
3. PARAR se qualquer arquivo crítico falhar verificação
4. LOG completo em evidence file
5. Operação idempotente

### Arquivos a PRESERVAR (NÃO TOCAR)
- .env, .editorconfig, .gitignore, .gitattributes
- .clinerules, .clauderules, .clineignore
- Diretórios: scripts/, docs/, Hb Track - Backend/, Hb Track - Frontend/, infra/, postman/, templates/
- ROADMAP.md
- .hb_lock (gerenciado automaticamente por HBLock)

## Critérios de Aceite
1) Todos os 25+ arquivos temporários listados foram removidos do disco. 2) Pastas .hb_guard/ e .hb_tmp_tests/ foram limpas. 3) Arquivos críticos preservados: scripts/run/hb_cli.py existe. 4) Arquivos críticos preservados: docs/hbtrack/_INDEX.md existe. 5) Diretórios principais intactos. 6) Evidence log criado: docs/hbtrack/evidence/AR_046_removed_files.log. 7) git status limpo ou apenas arquivos relevantes. 8) Nenhum arquivo critical removido. 9) .gitignore contém entradas temp. 10) Operação idempotente.

## Validation Command (Contrato)
```
python -c "import pathlib,sys,os; critical=['scripts/run/hb_cli.py','docs/hbtrack/_INDEX.md','scripts','docs','Hb Track - Backend','Hb Track - Frontend','.gitignore']; missing=[f for f in critical if not pathlib.Path(f).exists()]; assert not missing,f'FAIL critical missing: {missing}'; temp=['gemini.md','preparar_contexto.py','testador_final_report.py','complete_ar_reports.py','rebuild_index_real.py','mark_blocked_ars.py','insert_vps_policy.py','check_ar_status.py','consolidar_docs.py','temp_validate_ar002.py','test_gate_f.py','tmp_plan.json','validate_ar_translation.py','report_ar002.bat','run_report_ar002.ps1','arquivos_consolidados.txt','docs_consolidado.txt','_audit_output.txt','protocolo de correção.txt','tarefa_atual.md','Hb Track KANBAN.md','temp_report_032.py','temp_report_033.py','temp_report_038.py','temp_report_039.py','temp_report_040.py','temp_report_041.py','temp_report_042.py','temp_report_043.py','temp_report_044.py','fix_moves_044.py','fix_moves_045.py','validation_ar036.log']; present=[f for f in temp if pathlib.Path(f).exists()]; assert not present,f'FAIL temp still exist: {present}'; evidence=pathlib.Path('docs/hbtrack/evidence/AR_046_removed_files.log'); assert evidence.exists(),f'FAIL no evidence log'; gi=pathlib.Path('.gitignore').read_text(encoding='utf-8'); assert '.hb_guard' in gi and '.hb_tmp_tests' in gi,'FAIL .gitignore missing temp dirs'; print('PASS: Limpeza segura OK — arquivos mortos removidos, críticos preservados')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_046_removed_files.log`

## Notas do Arquiteto
TESTES DETERMINÍSTICOS:

GATE-CLEANUP-001: Arquivos críticos preservados
  cmd: python -c "import pathlib; critical=['scripts/run/hb_cli.py','docs/hbtrack/_INDEX.md']; assert all(pathlib.Path(f).exists() for f in critical); print('PASS')"
  PASS: 'PASS'
  FAIL: AssertionError

GATE-CLEANUP-002: Arquivos temporários removidos
  cmd: python -c "import pathlib; temp=['gemini.md','preparar_contexto.py','tmp_plan.json']; present=[f for f in temp if pathlib.Path(f).exists()]; assert not present,f'FAIL: {present}'; print('PASS')"
  PASS: 'PASS'
  FAIL: lista de arquivos ainda presentes

GATE-CLEANUP-003: Evidence log criado
  cmd: python -c "import pathlib; assert pathlib.Path('docs/hbtrack/evidence/AR_046_removed_files.log').exists(); print('PASS')"
  PASS: 'PASS'
  FAIL: FileNotFoundError

GATE-CLEANUP-004: .gitignore intacto
  cmd: python -c "import pathlib; gi=pathlib.Path('.gitignore').read_text(encoding='utf-8'); assert '.hb_guard' in gi and '.hb_tmp_tests' in gi; print('PASS')"
  PASS: 'PASS'
  FAIL: AssertionError

NOTA DE TRIPLE-RUN: Após a limpeza ser executada uma vez, rodar validation_command 3x sempre retornará mesmo stdout (lista de arquivos é estática) → triple_consistency=OK garantido.

DETERMINISMO: A operação é determinística porque:
- Lista de arquivos é fixa (hardcoded)
- Filesystem operations são atômicas (unlink, rmtree)
- Evidence log timestamp varia mas validação não checa conteúdo do log, apenas existência
- Cross-platform via pathlib (Windows + Linux)

## Riscos
- Windows pode bloquear remoção de arquivo se estiver aberto em editor/processo — try/except graceful
- Arquivos tracked no git requerem 'git rm --cached' antes de unlink — verificar git status
- Pastas não vazias podem falhar com rmdir — usar shutil.rmtree()
- test-cookie-flow.js pode ter lugar adequado em Hb Track - Frontend/ — se causar problema, mover ao invés de deletar
- Se script rodar 2x, não deve causar erro (idempotência via 'if exists' antes de unlink)
- _reports/ contém outputs do testador — NÃO limpar totalmente, apenas arquivos temporários específicos

## Análise de Impacto
**Executor**: Claude Sonnet 4.6 (Modo Executor)
**Data**: 2026-02-22

**Escopo**: Remoção de 25+ arquivos temporários da raiz do repositório via script Python pathlib. Nenhum arquivo crítico tocado. Evidence log gerado em `docs/hbtrack/evidence/AR_046_removed_files.log`.

**Arquivos removidos**: gemini.md, temp_report_032–044.py, fix_moves_044/045.py, check_ar_status.py, complete_ar_reports.py, consolidar_docs.py, mark_blocked_ars.py, rebuild_index_real.py, testador_final_report.py, insert_vps_policy.py, temp_validate_ar002.py, tmp_plan.json, validate_ar_translation.py, report_ar002.bat, run_report_ar002.ps1, arquivos_consolidados.txt, docs_consolidado.txt, _audit_output.txt, protocolo de correção.txt, Hb Track KANBAN.md, tarefa_atual.md, validation_ar036.log

**Impacto**: Repositório limpo — git status sem ruído de arquivos ad-hoc.

---
## Carimbo de Execução
_(Gerado por hb report)_


### Execução em b2e7523
**Status Final**: ✅ SUCESSO
**Comando**: `python -c "import pathlib,sys,os; critical=['scripts/run/hb_cli.py','docs/hbtrack/_INDEX.md','scripts','docs','Hb Track - Backend','Hb Track - Frontend','.gitignore']; missing=[f for f in critical if not pathlib.Path(f).exists()]; assert not missing,f'FAIL critical missing: {missing}'; temp=['gemini.md','preparar_contexto.py','testador_final_report.py','complete_ar_reports.py','rebuild_index_real.py','mark_blocked_ars.py','insert_vps_policy.py','check_ar_status.py','consolidar_docs.py','temp_validate_ar002.py','test_gate_f.py','tmp_plan.json','validate_ar_translation.py','report_ar002.bat','run_report_ar002.ps1','arquivos_consolidados.txt','docs_consolidado.txt','_audit_output.txt','protocolo de correção.txt','tarefa_atual.md','Hb Track KANBAN.md','temp_report_032.py','temp_report_033.py','temp_report_038.py','temp_report_039.py','temp_report_040.py','temp_report_041.py','temp_report_042.py','temp_report_043.py','temp_report_044.py','fix_moves_044.py','fix_moves_045.py','validation_ar036.log']; present=[f for f in temp if pathlib.Path(f).exists()]; assert not present,f'FAIL temp still exist: {present}'; evidence=pathlib.Path('docs/hbtrack/evidence/AR_046_removed_files.log'); assert evidence.exists(),f'FAIL no evidence log'; gi=pathlib.Path('.gitignore').read_text(encoding='utf-8'); assert '.hb_guard' in gi and '.hb_tmp_tests' in gi,'FAIL .gitignore missing temp dirs'; print('PASS: Limpeza segura OK — arquivos mortos removidos, críticos preservados')"`
**Exit Code**: 0
**Evidence File**: `docs/hbtrack/evidence/AR_046_removed_files.log`
**Python Version**: 3.11.9


### Verificacao Testador em b2e7523
**Status Testador**: ✅ VERIFICADO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_046_b2e7523/result.json`

### Verificacao Testador em b2e7523
**Status Testador**: ✅ VERIFICADO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_046_b2e7523/result.json`
