# AR_201 — Fix validation_command AR_200 - janela 450 para split-por-linha

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.3.0

## Descrição
A validation_command de AR_200 contém checagem por janela fixa de 450 chars (t.find('| '+lbl):t.find('| '+lbl)+450) para detectar NOT_RUN em linhas INV. A linha INV-TRAIN-005 tem ~206 chars; os 244 chars restantes da janela de 450 estendem-se para INV-006, que legitimamente tem NOT_RUN (não estava no top-10). Resultado: falso positivo FAIL no hb report 200 — Exit Code: 1.

Ação obrigatória:

1. Editar docs/hbtrack/ars/features/AR_200_executar_top-10_testes_coberto+not_run_e_salvar_ev.md, seção '## Validation Command (Contrato)'. Substituir a linha de checagem INV (que contém +450) pela versão line-by-line abaixo.

2. Nova validation_command completa para AR_200 (substituição total do bloco de código):
python -c "import os,sys; base='_reports/training'; ids=['INV-001','INV-002','INV-003','INV-004','INV-005','INV-008','INV-009','INV-030','INV-032','CONTRACT-077-085']; [sys.exit('FAIL: missing '+base+'/TEST-TRAIN-'+i+'.md') for i in ids if not os.path.exists(base+'/TEST-TRAIN-'+i+'.md')]; [sys.exit('FAIL: AR Origem ausente em '+base+'/TEST-TRAIN-'+i+'.md') for i in ids if 'AR Origem: AR_200' not in open(base+'/TEST-TRAIN-'+i+'.md',encoding='utf-8').read()]; t=open('docs/hbtrack/modulos/treinos/TEST_MATRIX_TRAINING.md',encoding='utf-8').read(); assert 'v1.7.0' in t,'FAIL: TEST_MATRIX nao bump para v1.7.0'; inv=[('001','INV-TRAIN-001'),('002','INV-TRAIN-002'),('003','INV-TRAIN-003'),('004','INV-TRAIN-004'),('005','INV-TRAIN-005'),('008','INV-TRAIN-008'),('009','INV-TRAIN-009'),('030','INV-TRAIN-030'),('032','INV-TRAIN-032')]; [sys.exit('FAIL: NOT_RUN persiste na linha '+lbl) for _,lbl in inv if any('NOT_RUN' in ln for ln in t.split('\n') if ln.startswith('| '+lbl+' '))]; ct_ids=['CONTRACT-TRAIN-077','CONTRACT-TRAIN-078','CONTRACT-TRAIN-079','CONTRACT-TRAIN-080','CONTRACT-TRAIN-081','CONTRACT-TRAIN-082','CONTRACT-TRAIN-083','CONTRACT-TRAIN-084','CONTRACT-TRAIN-085']; [sys.exit('FAIL: NOT_RUN persiste na linha '+c) for c in ct_ids if any('NOT_RUN' in ln for ln in t.split('\n') if ln.startswith('| '+c+' '))]; print('PASS: 10 evidencias criadas com AR_200 + TEST_MATRIX v1.7.0 + NOT_RUN removido')"

3. Re-executar hb report 200 com a nova validation_command (deve retornar Exit Code: 0 e PASS na saída).

## Critérios de Aceite
AC-001: docs/hbtrack/ars/features/AR_200*.md nao contem '+450' na validation_command. AC-002: docs/hbtrack/ars/features/AR_200*.md contem split('\n') na validation_command. AC-003: docs/hbtrack/evidence/AR_200/executor_main.log contem 'Exit Code: 0'. AC-004: docs/hbtrack/evidence/AR_200/executor_main.log contem 'PASS: 10 evidencias criadas'.

## Write Scope
- docs/hbtrack/ars/features/
- docs/hbtrack/evidence/AR_200/

## Validation Command (Contrato)
```
python -c "import sys; ar200=open('docs/hbtrack/ars/features/AR_200_executar_top-10_testes_coberto+not_run_e_salvar_ev.md',encoding='utf-8').read(); assert '+450' not in ar200,'FAIL: janela 450 ainda presente em AR_200'; assert 'split' in ar200,'FAIL: split-por-linha ausente em AR_200'; log=open('docs/hbtrack/evidence/AR_200/executor_main.log',encoding='utf-8').read(); assert 'Exit Code: 0' in log,'FAIL: executor_main.log AR_200 nao tem Exit Code: 0'; assert 'PASS: 10 evidencias' in log,'FAIL: PASS ausente em executor_main.log AR_200'; print('PASS: AR_200 validation_command corrigida + executor_main.log Exit Code: 0')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_201/executor_main.log`

## Riscos
- hb report 200 deve ser re-executado com a nova validation_command exata (cmd-match obrigatorio). Se o Executor usar python temp/_run_ar200_report.py, deve atualizar o script para a nova validation_command.
- A nova validation_command usa t.split('\n') e ln.startswith('| INV-TRAIN-XXX ') — exige espaco após o ID para evitar match de prefixo (e.g. INV-TRAIN-001 nao captura INV-TRAIN-0010 hipotetico).

## Análise de Impacto

**Arquivos alterados:**
- `docs/hbtrack/ars/features/AR_200_executar_top-10_testes_coberto+not_run_e_salvar_ev.md` — EDITADO: seção `## Validation Command (Contrato)` — substituição de checagem por janela fixa (+450) por verificação linha-a-linha via `t.split('\n')` com `ln.startswith('| '+lbl+' ')`.
- `docs/hbtrack/evidence/AR_200/executor_main.log` — REGENERADO via re-execução de `hb report 200` com a nova validation_command.

**Impacto em Backend/Frontend:** NENHUM — nenhum arquivo de código de produto é alterado.

**Impacto em SSOTs:** Nenhuma SSOT estrutural é alterada. O arquivo AR_200 é artefato de rastreamento; a substituição é cirúrgica na seção de contrato.

**Causa raiz do bug:** `INV-TRAIN-005` ocupa ~206 chars na linha da tabela. A janela de 450 extravaza 244 chars para a linha seguinte `INV-TRAIN-006`, que contém `NOT_RUN` legítimo (não estava no top-10). Fix: `any('NOT_RUN' in ln for ln in t.split('\n') if ln.startswith('| '+lbl+' '))` — examina exatamente a linha do ID.

**Zero regressão:** Nenhum teste, evidência ou TEST_MATRIX é alterado. Apenas o contrato de AR_200 é corrigido para refletir corretamente o que foi executado.

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução Executor em b123a58
**Status Executor**: ❌ FALHA
**Comando**: `python -c "import sys; ar200=open('docs/hbtrack/ars/features/AR_200_executar_top-10_testes_coberto+not_run_e_salvar_ev.md',encoding='utf-8').read(); assert '+450' not in ar200,'FAIL: janela 450 ainda presente em AR_200'; assert 'split' in ar200,'FAIL: split-por-linha ausente em AR_200'; log=open('docs/hbtrack/evidence/AR_200/executor_main.log',encoding='utf-8').read(); assert 'Exit Code: 0' in log,'FAIL: executor_main.log AR_200 nao tem Exit Code: 0'; assert 'PASS: 10 evidencias' in log,'FAIL: PASS ausente em executor_main.log AR_200'; print('PASS: AR_200 validation_command corrigida + executor_main.log Exit Code: 0')"`
**Exit Code**: 1
**Timestamp UTC**: 2026-03-03T00:15:51.163155+00:00
**Behavior Hash**: 9c9f39f75830c94f32b3a4a8253bab53c13d4f94c1dc98b4239f887e081cf15a
**Evidence File**: `docs/hbtrack/evidence/AR_201/executor_main.log`
**Python Version**: 3.11.9

### Execução Executor em b123a58
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python -c "import sys; ar200=open('docs/hbtrack/ars/features/AR_200_executar_top-10_testes_coberto+not_run_e_salvar_ev.md',encoding='utf-8').read(); assert '+450' not in ar200,'FAIL: janela 450 ainda presente em AR_200'; assert 'split' in ar200,'FAIL: split-por-linha ausente em AR_200'; log=open('docs/hbtrack/evidence/AR_200/executor_main.log',encoding='utf-8').read(); assert 'Exit Code: 0' in log,'FAIL: executor_main.log AR_200 nao tem Exit Code: 0'; assert 'PASS: 10 evidencias' in log,'FAIL: PASS ausente em executor_main.log AR_200'; print('PASS: AR_200 validation_command corrigida + executor_main.log Exit Code: 0')"`
**Exit Code**: 0
**Timestamp UTC**: 2026-03-03T00:18:06.443915+00:00
**Behavior Hash**: 29fff797fd5a052f2845c56325a0f00cf37d3ded9a65361c464eedc7d4a15119
**Evidence File**: `docs/hbtrack/evidence/AR_201/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em b123a58
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_201_b123a58/result.json`

### Selo Humano em b123a58
**Status Humano**: ✅ VERIFICADO
**Timestamp UTC**: 2026-03-03T00:35:01.084818+00:00
**Motivo**: —
**TESTADOR_REPORT**: `_reports/testador/AR_201_b123a58/result.json`
**Evidence File**: `docs/hbtrack/evidence/AR_201/executor_main.log`
