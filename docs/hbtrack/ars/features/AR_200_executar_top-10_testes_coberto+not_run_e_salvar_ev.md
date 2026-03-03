# AR_200 — Executar Top-10 testes COBERTO+NOT_RUN e salvar evidências

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.3.0

## Descrição
Executar pytest para cada um dos 10 itens COBERTO+NOT_RUN selecionados por prioridade §10 DoD (BLOQUEANTE_VALIDACAO/ARQUITETURA + CRITICA + COBERTO + NOT_RUN no TEST_MATRIX v1.6.0).

PRÉ-REQUISITO: cd 'Hb Track - Backend' antes de rodar os testes. Os caminhos de teste são relativos ao root do backend.

──────────────────────────────────────────────
ITENS TOP-10 (ordem de execução — preservar esta ordem):
──────────────────────────────────────────────
1. INV-TRAIN-001 — focus_total_max_120_pct
   Teste: tests/training/invariants/test_inv_train_001_focus_sum_constraint.py
   Evidência: _reports/training/TEST-TRAIN-INV-001.md
   Prioridade: BLOQUEANTE_VALIDACAO + CRITICA

2. INV-TRAIN-002 — wellness_pre_deadline_2h_before_session
   Teste: tests/training/invariants/test_inv_train_002_wellness_pre_deadline.py
   Evidência: _reports/training/TEST-TRAIN-INV-002.md
   Prioridade: BLOQUEANTE_VALIDACAO + CRITICA

3. INV-TRAIN-003 — wellness_post_edit_window_24h_after_created
   Teste: tests/training/invariants/test_inv_train_003_wellness_post_deadline.py
   Evidência: _reports/training/TEST-TRAIN-INV-003.md
   Prioridade: BLOQUEANTE_VALIDACAO + CRITICA

4. INV-TRAIN-004 — session_edit_window_by_role
   Teste: tests/training/invariants/test_inv_train_004_edit_window_time.py
   Evidência: _reports/training/TEST-TRAIN-INV-004.md
   Prioridade: BLOQUEANTE_VALIDACAO + CRITICA

5. INV-TRAIN-005 — session_immutable_after_60_days
   Teste: tests/training/invariants/test_inv_train_005_immutability_60_days.py
   Evidência: _reports/training/TEST-TRAIN-INV-005.md
   Prioridade: BLOQUEANTE_VALIDACAO + CRITICA

6. INV-TRAIN-008 — soft_delete_reason_pair
   Teste: tests/training/invariants/test_inv_train_008_soft_delete_reason_pair.py
   Evidência: _reports/training/TEST-TRAIN-INV-008.md
   Prioridade: BLOQUEANTE_ARQUITETURA + CRITICA

7. INV-TRAIN-009 — unique_wellness_pre_per_athlete_session
   Teste: tests/training/invariants/test_inv_train_009_wellness_pre_uniqueness.py
   Evidência: _reports/training/TEST-TRAIN-INV-009.md
   Prioridade: BLOQUEANTE_VALIDACAO + CRITICA

8. INV-TRAIN-030 — attendance_correction_requires_audit_fields
   Teste: tests/training/invariants/test_inv_train_030_attendance_correction_fields.py
   Evidência: _reports/training/TEST-TRAIN-INV-030.md
   Prioridade: BLOQUEANTE_VALIDACAO + CRITICA

9. INV-TRAIN-032 — wellness_post_rpe_range
   Teste: tests/training/invariants/test_inv_train_032_wellness_post_rpe.py
   Evidência: _reports/training/TEST-TRAIN-INV-032.md
   Prioridade: BLOQUEANTE_VALIDACAO + CRITICA

10. CONTRACT-TRAIN-077..085 — alerts-suggestions (grupo de 9 endpoints)
    Teste: tests/training/contracts/test_contract_train_077_085_alerts_suggestions.py
    Evidência: _reports/training/TEST-TRAIN-CONTRACT-077-085.md
    Prioridade: COBERTO + NOT_RUN (únicos contratos COBERTO na matriz v1.6.0)

──────────────────────────────────────────────
PASSO A — EXECUÇÃO (para cada item 1..10):
──────────────────────────────────────────────
Para cada item, executar:
  pytest <caminho_teste> -v 2>&1

Capturar stdout+stderr completo do pytest (incluindo cabeçalho de coleção, linha de resultado por função de teste, e linha de sumário PASSED/FAILED).

Criar o arquivo de evidência em _reports/training/ com o seguinte formato exato:
```
# TEST-TRAIN-<ID> — Evidência de Execução
- Data: YYYY-MM-DD
- Status: PASS
- Comando: pytest tests/training/invariants/test_inv_train_<XXX>_<nome>.py -v
- AR Origem: AR_200

## Output pytest

```
<stdout+stderr completo do comando pytest acima>
```
```

Se o pytest retornar exit code != 0 (algum teste FAILED ou ERROR), o Status deve ser FAIL.

──────────────────────────────────────────────
PASSO B — ATUALIZAÇÃO TEST_MATRIX_TRAINING.md:
──────────────────────────────────────────────
Após executar todos os 10 testes, atualizar docs/hbtrack/modulos/treinos/TEST_MATRIX_TRAINING.md:

B1) HEADER — Bump versão:
   'Versão: v1.6.0' → 'Versão: v1.7.0'
   Atualizar 'Última revisão:' para a data de execução
   Adicionar entrada no Changelog acima do '### v1.6.0':
   '### v1.7.0 (<DATA>) — AR_200\n- §5: INV-TRAIN-001/002/003/004/005/008/009/030/032 Últ.Execução + Evidência atualizados (PASS/FAIL)\n- §8: CONTRACT-TRAIN-077..085 Últ.Execução + Evidência atualizados (PASS/FAIL)'

B2) §5 — Para cada um dos 9 invariantes (001/002/003/004/005/008/009/030/032):
   - Coluna 'Últ.Execução': NOT_RUN → <DATA_EXECUCAO>
   - Coluna 'Evidência': `-` → `_reports/training/TEST-TRAIN-INV-<XXX>.md`
   - NÃO alterar colunas: ID, Nome, Prioridade, ID-Teste, Tipo, Status-Cobertura

B3) §8 — Para cada um dos 9 contratos CONTRACT-TRAIN-077 até CONTRACT-TRAIN-085:
   - Coluna 'Últ.Execução': NOT_RUN → <DATA_EXECUCAO>
   - Coluna 'Evidência': `-` → `_reports/training/TEST-TRAIN-CONTRACT-077-085.md`
   - NÃO alterar colunas: ID, Endpoint, Prioridade, ID-Teste, Tipo, Status-Cobertura

NOTA CRÍTICA: Preservar exatamente a estrutura pipe-delimited das tabelas Markdown. Alterar APENAS os valores das duas colunas descritas. Não adicionar espaços extras ou quebrar formatação das tabelas.

## Critérios de Aceite
AC-001: _reports/training/TEST-TRAIN-INV-001.md existe e contém 'AR Origem: AR_200'. AC-002: _reports/training/TEST-TRAIN-INV-002.md existe e contém 'AR Origem: AR_200'. AC-003: _reports/training/TEST-TRAIN-INV-003.md existe e contém 'AR Origem: AR_200'. AC-004: _reports/training/TEST-TRAIN-INV-004.md existe e contém 'AR Origem: AR_200'. AC-005: _reports/training/TEST-TRAIN-INV-005.md existe e contém 'AR Origem: AR_200'. AC-006: _reports/training/TEST-TRAIN-INV-008.md existe e contém 'AR Origem: AR_200'. AC-007: _reports/training/TEST-TRAIN-INV-009.md existe e contém 'AR Origem: AR_200'. AC-008: _reports/training/TEST-TRAIN-INV-030.md existe e contém 'AR Origem: AR_200'. AC-009: _reports/training/TEST-TRAIN-INV-032.md existe e contém 'AR Origem: AR_200'. AC-010: _reports/training/TEST-TRAIN-CONTRACT-077-085.md existe e contém 'AR Origem: AR_200'. AC-011: TEST_MATRIX_TRAINING.md contém 'v1.7.0'. AC-012: Linhas de INV-TRAIN-001/002/003/004/005/008/009/030/032 no TEST_MATRIX NÃO contêm NOT_RUN na coluna Últ.Execução. AC-013: Linhas de CONTRACT-TRAIN-077..085 no TEST_MATRIX NÃO contêm NOT_RUN na coluna Últ.Execução.

## Write Scope
- docs/hbtrack/modulos/treinos/TEST_MATRIX_TRAINING.md

## Validation Command (Contrato)
```
python -c "import os,sys; base='_reports/training'; ids=['INV-001','INV-002','INV-003','INV-004','INV-005','INV-008','INV-009','INV-030','INV-032','CONTRACT-077-085']; [sys.exit('FAIL: missing '+base+'/TEST-TRAIN-'+i+'.md') for i in ids if not os.path.exists(base+'/TEST-TRAIN-'+i+'.md')]; [sys.exit('FAIL: AR Origem ausente em '+base+'/TEST-TRAIN-'+i+'.md') for i in ids if 'AR Origem: AR_200' not in open(base+'/TEST-TRAIN-'+i+'.md',encoding='utf-8').read()]; t=open('docs/hbtrack/modulos/treinos/TEST_MATRIX_TRAINING.md',encoding='utf-8').read(); assert 'v1.7.0' in t,'FAIL: TEST_MATRIX nao bump para v1.7.0'; inv=[('001','INV-TRAIN-001'),('002','INV-TRAIN-002'),('003','INV-TRAIN-003'),('004','INV-TRAIN-004'),('005','INV-TRAIN-005'),('008','INV-TRAIN-008'),('009','INV-TRAIN-009'),('030','INV-TRAIN-030'),('032','INV-TRAIN-032')]; [sys.exit('FAIL: NOT_RUN persiste na linha '+lbl) for _,lbl in inv if any('NOT_RUN' in ln for ln in t.split('\n') if ln.startswith('| '+lbl+' '))]; ct_ids=['CONTRACT-TRAIN-077','CONTRACT-TRAIN-078','CONTRACT-TRAIN-079','CONTRACT-TRAIN-080','CONTRACT-TRAIN-081','CONTRACT-TRAIN-082','CONTRACT-TRAIN-083','CONTRACT-TRAIN-084','CONTRACT-TRAIN-085']; [sys.exit('FAIL: NOT_RUN persiste na linha '+c) for c in ct_ids if any('NOT_RUN' in ln for ln in t.split('\n') if ln.startswith('| '+c+' '))]; print('PASS: 10 evidencias criadas com AR_200 + TEST_MATRIX v1.7.0 + NOT_RUN removido')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_200/executor_main.log`

## Riscos
- Testes de invariantes dependem de DB de teste (conftest.py). Se DB offline → FAIL de infra, não de lógica. Neste caso: registrar INFRA_FAIL na evidência e reportar ao Arquiteto.
- INV-TRAIN-004 possui dois arquivos: test_inv_train_004_edit_window_time.py e test_inv_train_004_edit_window_constants_runtime.py — usar APENAS test_inv_train_004_edit_window_time.py nesta AR.
- INV-TRAIN-032 possui dois arquivos: test_inv_train_032_wellness_post_rpe.py e test_inv_train_032_wellness_post_rpe_runtime.py — usar APENAS test_inv_train_032_wellness_post_rpe.py nesta AR.
- CONTRACT-077-085 é um arquivo único que cobre 9 contratos. A evidência TEST-TRAIN-CONTRACT-077-085.md deve referênciar todos os 9 IDs de contrato na linha de Evidência do TEST_MATRIX.

## Análise de Impacto

**Arquivos alterados:**
- `_reports/training/TEST-TRAIN-INV-001.md` — CRIADO (evidência pytest INV-001)
- `_reports/training/TEST-TRAIN-INV-002.md` — CRIADO (evidência pytest INV-002)
- `_reports/training/TEST-TRAIN-INV-003.md` — CRIADO (evidência pytest INV-003)
- `_reports/training/TEST-TRAIN-INV-004.md` — CRIADO (evidência pytest INV-004)
- `_reports/training/TEST-TRAIN-INV-005.md` — CRIADO (evidência pytest INV-005)
- `_reports/training/TEST-TRAIN-INV-008.md` — CRIADO (evidência pytest INV-008)
- `_reports/training/TEST-TRAIN-INV-009.md` — CRIADO (evidência pytest INV-009)
- `_reports/training/TEST-TRAIN-INV-030.md` — CRIADO (evidência pytest INV-030)
- `_reports/training/TEST-TRAIN-INV-032.md` — CRIADO (evidência pytest INV-032)
- `_reports/training/TEST-TRAIN-CONTRACT-077-085.md` — CRIADO (evidência pytest CONTRACT-077..085)
- `docs/hbtrack/modulos/treinos/TEST_MATRIX_TRAINING.md` — EDITADO (bump v1.6.0 → v1.7.0; colunas Últ.Execução + Evidência para 9 INV + 9 CONTRACT)

**Impacto em Backend/Frontend:** NENHUM — zero alterações em código de produto.

**Impacto em SSOTs:** `TEST_MATRIX_TRAINING.md` é SSOT de cobertura; bump de versão + preenchimento de colunas de execução está dentro do write_scope.

**Risco identificado:** Testes de invariantes com DB (INV-001..009/030/032) dependem de `conftest.py` + fixtures de DB de teste. Se DB offline, resultado será FAIL de infra — será registrado como INFRA_FAIL na evidência. Testes de contrato (077..085) usam tipo PRE (mocks/schemas), sem dependência de DB.

**Zero regressão esperada:** Esta AR não modifica nenhum arquivo de código; apenas lê testes existentes e grava evidências + atualiza matriz de rastreamento.

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução Executor em b123a58
**Status Executor**: ❌ FALHA (contrato corrigido por AR_201)
**Comando**: `python -c "import os,sys; base='_reports/training'; ids=['INV-001','INV-002','INV-003','INV-004','INV-005','INV-008','INV-009','INV-030','INV-032','CONTRACT-077-085']; [sys.exit('FAIL: missing '+base+'/TEST-TRAIN-'+i+'.md') for i in ids if not os.path.exists(base+'/TEST-TRAIN-'+i+'.md')]; [sys.exit('FAIL: AR Origem ausente em '+base+'/TEST-TRAIN-'+i+'.md') for i in ids if 'AR Origem: AR_200' not in open(base+'/TEST-TRAIN-'+i+'.md',encoding='utf-8').read()]; t=open('docs/hbtrack/modulos/treinos/TEST_MATRIX_TRAINING.md',encoding='utf-8').read(); assert 'v1.7.0' in t,'FAIL: TEST_MATRIX nao bump para v1.7.0'; inv=[('001','INV-TRAIN-001'),('002','INV-TRAIN-002'),('003','INV-TRAIN-003'),('004','INV-TRAIN-004'),('005','INV-TRAIN-005'),('008','INV-TRAIN-008'),('009','INV-TRAIN-009'),('030','INV-TRAIN-030'),('032','INV-TRAIN-032')]; [sys.exit('FAIL: NOT_RUN persiste na linha '+lbl) for _,lbl in inv if any('NOT_RUN' in ln for ln in t.split('\n') if ln.startswith('| '+lbl+' '))]; ct_ids=['CONTRACT-TRAIN-077','CONTRACT-TRAIN-078','CONTRACT-TRAIN-079','CONTRACT-TRAIN-080','CONTRACT-TRAIN-081','CONTRACT-TRAIN-082','CONTRACT-TRAIN-083','CONTRACT-TRAIN-084','CONTRACT-TRAIN-085']; [sys.exit('FAIL: NOT_RUN persiste na linha '+c) for c in ct_ids if any('NOT_RUN' in ln for ln in t.split('\n') if ln.startswith('| '+c+' '))]; print('PASS: 10 evidencias criadas com AR_200 + TEST_MATRIX v1.7.0 + NOT_RUN removido')"`
**Exit Code**: 1
**Timestamp UTC**: 2026-03-02T23:27:05.078315+00:00
**Behavior Hash**: 468a9fc78b77c56b79e8fc8ae3a64228968e0750d62645b433528166c242cda8
**Evidence File**: `docs/hbtrack/evidence/AR_200/executor_main.log`
**Python Version**: 3.11.9

### Execução Executor em b123a58
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python -c "import os,sys; base='_reports/training'; ids=['INV-001','INV-002','INV-003','INV-004','INV-005','INV-008','INV-009','INV-030','INV-032','CONTRACT-077-085']; [sys.exit('FAIL: missing '+base+'/TEST-TRAIN-'+i+'.md') for i in ids if not os.path.exists(base+'/TEST-TRAIN-'+i+'.md')]; [sys.exit('FAIL: AR Origem ausente em '+base+'/TEST-TRAIN-'+i+'.md') for i in ids if 'AR Origem: AR_200' not in open(base+'/TEST-TRAIN-'+i+'.md',encoding='utf-8').read()]; t=open('docs/hbtrack/modulos/treinos/TEST_MATRIX_TRAINING.md',encoding='utf-8').read(); assert 'v1.7.0' in t,'FAIL: TEST_MATRIX nao bump para v1.7.0'; inv=[('001','INV-TRAIN-001'),('002','INV-TRAIN-002'),('003','INV-TRAIN-003'),('004','INV-TRAIN-004'),('005','INV-TRAIN-005'),('008','INV-TRAIN-008'),('009','INV-TRAIN-009'),('030','INV-TRAIN-030'),('032','INV-TRAIN-032')]; [sys.exit('FAIL: NOT_RUN persiste na linha '+lbl) for _,lbl in inv if any('NOT_RUN' in ln for ln in t.split('\n') if ln.startswith('| '+lbl+' '))]; ct_ids=['CONTRACT-TRAIN-077','CONTRACT-TRAIN-078','CONTRACT-TRAIN-079','CONTRACT-TRAIN-080','CONTRACT-TRAIN-081','CONTRACT-TRAIN-082','CONTRACT-TRAIN-083','CONTRACT-TRAIN-084','CONTRACT-TRAIN-085']; [sys.exit('FAIL: NOT_RUN persiste na linha '+c) for c in ct_ids if any('NOT_RUN' in ln for ln in t.split('\n') if ln.startswith('| '+c+' '))]; print('PASS: 10 evidencias criadas com AR_200 + TEST_MATRIX v1.7.0 + NOT_RUN removido')"`
**Exit Code**: 0
**Timestamp UTC**: 2026-03-03T00:15:09.536286+00:00
**Behavior Hash**: 1395a5b2bd65d91752e4a52bf58ced5f3146cc2964eb212c9cf55bdf50d6160c
**Evidence File**: `docs/hbtrack/evidence/AR_200/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em b123a58
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_200_b123a58/result.json`

### Selo Humano em b123a58
**Status Humano**: ✅ VERIFICADO
**Timestamp UTC**: 2026-03-03T00:33:47.742811+00:00
**Motivo**: —
**TESTADOR_REPORT**: `_reports/testador/AR_200_b123a58/result.json`
**Evidence File**: `docs/hbtrack/evidence/AR_200/executor_main.log`
