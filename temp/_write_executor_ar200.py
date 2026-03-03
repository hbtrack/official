"""Reescreve _reports/EXECUTOR.md com relatório AR_200."""
content = """# EXECUTOR_REPORT -- AR_200

| Campo | Valor |
|---|---|
| **EXECUTOR_REPORT** | EXECUTOR_REPORT_PRONTO_TESTADOR |
| **Protocolo** | v1.3.0 |
| **Branch** | dev-changes-2 |
| **HEAD** | b123a58 |
| **Data** | 2026-03-02 |
| **AR executada** | AR_200 |
| **Classe** | T (execucao de testes + evidencias) |

---

## AR_200 -- Top-10 DoD Evidence Execution

| Campo | Valor |
|---|---|
| **Exit Code hb report** | 1 (falso positivo -- ver KNOWN_ISSUE) |
| **Behavior Hash** | 468a9fc78b77c56b79e8fc8ae3a64228968e0750d62645b433528166c242cda8 |
| **Validation Output** | FAIL: NOT_RUN persiste na linha INV-TRAIN-005 (falso positivo) |
| **Evidence** | docs/hbtrack/evidence/AR_200/executor_main.log |
| **Status AR** | EXECUTADO_COM_KNOWN_ISSUE |

---

## Testes Executados

| # | ID | Status | Resumo pytest |
|---|---|---|---|
| 1 | INV-TRAIN-001 | FAIL | 1 failed, 2 passed |
| 2 | INV-TRAIN-002 | PASS | 3 passed |
| 3 | INV-TRAIN-003 | PASS | 5 passed |
| 4 | INV-TRAIN-004 | PASS | 8 passed |
| 5 | INV-TRAIN-005 | PASS | 6 passed |
| 6 | INV-TRAIN-008 | FAIL | 6 failed |
| 7 | INV-TRAIN-009 | PASS | 4 passed |
| 8 | INV-TRAIN-030 | FAIL | 7 failed |
| 9 | INV-TRAIN-032 | FAIL | 3 errors |
| 10 | CONTRACT-077..085 | FAIL | 20 failed |

Infraestrutura: import bypass via temp/run_training_tests.py (pre-patcha sys.modules app.core.database -- import quebrado em post_training.py e fora do write_scope).

---

## Evidencias Criadas (10 arquivos)

| Arquivo | AR Origem |
|---|---|
| _reports/training/TEST-TRAIN-INV-001.md | AR_200 |
| _reports/training/TEST-TRAIN-INV-002.md | AR_200 |
| _reports/training/TEST-TRAIN-INV-003.md | AR_200 |
| _reports/training/TEST-TRAIN-INV-004.md | AR_200 |
| _reports/training/TEST-TRAIN-INV-005.md | AR_200 |
| _reports/training/TEST-TRAIN-INV-008.md | AR_200 |
| _reports/training/TEST-TRAIN-INV-009.md | AR_200 |
| _reports/training/TEST-TRAIN-INV-030.md | AR_200 |
| _reports/training/TEST-TRAIN-INV-032.md | AR_200 |
| _reports/training/TEST-TRAIN-CONTRACT-077-085.md | AR_200 |

---

## TEST_MATRIX_TRAINING.md -- Alteracoes

- Versao: v1.6.0 -> v1.7.0
- Changelog v1.7.0 inserido
- 9 linhas INV (001/002/003/004/005/008/009/030/032): NOT_RUN -> 2026-03-02 + evidencia atualizada
- 9 linhas CONTRACT (077..085): NOT_RUN -> 2026-03-02 + evidencia atualizada

---

## KNOWN_ISSUE -- Falso Positivo na validation_command

**Mensagem**: FAIL: NOT_RUN persiste na linha INV-TRAIN-005

**Causa**: A validation_command usa janela de 450 chars a partir de `| INV-TRAIN-005`.
A linha INV-005 tem ~206 chars. Os 244 chars restantes alcancam INV-006
(nao estava no top-10, portanto tem NOT_RUN legitimamente). Falso positivo.

**Status AC-012 real**: SATISFEITO -- INV-TRAIN-005 tem 2026-03-02 no arquivo.
**ACs satisfeitos**: AC-001 a AC-011, AC-013 = OK por verificacao direta do arquivo.

Acao para Arquiteto: corrigir janela 450 chars ou usar split por newline.

---

## Criterios de Aceite

| AC | Status |
|---|---|
| AC-001 a AC-010: evidencias existem + AR Origem AR_200 | OK |
| AC-011: v1.7.0 no TEST_MATRIX | OK |
| AC-012: NOT_RUN removido INV rows (conferir por linha no arquivo) | OK arquivo / FALSO POSITIVO script |
| AC-013: NOT_RUN removido CONTRACT rows | OK |

---

## Stage Exato

  docs/hbtrack/evidence/AR_200/executor_main.log
  docs/hbtrack/ars/features/AR_200_executar_top-10_testes_coberto+not_run_e_salvar_ev.md
  docs/hbtrack/modulos/treinos/TEST_MATRIX_TRAINING.md
  _reports/training/TEST-TRAIN-INV-001.md
  _reports/training/TEST-TRAIN-INV-002.md
  _reports/training/TEST-TRAIN-INV-003.md
  _reports/training/TEST-TRAIN-INV-004.md
  _reports/training/TEST-TRAIN-INV-005.md
  _reports/training/TEST-TRAIN-INV-008.md
  _reports/training/TEST-TRAIN-INV-009.md
  _reports/training/TEST-TRAIN-INV-030.md
  _reports/training/TEST-TRAIN-INV-032.md
  _reports/training/TEST-TRAIN-CONTRACT-077-085.md
"""

import os
os.chdir(r"c:\HB TRACK")
with open("_reports/EXECUTOR.md", "w", encoding="utf-8") as f:
    f.write(content)
print("EXECUTOR.md written OK")
