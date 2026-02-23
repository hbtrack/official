# AR_022 — BATCH_001: assignment das ARs pendentes para Executor A e Executor B

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.0.6

## Descrição
PROBLEMA: As 9 ARs pendentes (AR_010..AR_012, AR_016..AR_020) precisam ser atribuídas formalmente a Executor A e Executor B para execução paralela conforme o Dual Executor Contract (AR_021).

ANÁLISE DE DOMÍNIO:
- AR_010: hb_cli.py → Executor A
- AR_011: hb_cli.py → Executor A (executar APÓS 010: usa cmd_report já corrigido)
- AR_012: hb_cli.py → Executor A (mesmo domínio)
- AR_020: hb_cli.py + Dev Flow.md → Executor A (ÚLTIMA de A: bumpa para v1.0.8)
- AR_016: PRD Hb Track.md → Executor B
- AR_017: PRD Hb Track.md → Executor B (executar APÓS 016: mesmo arquivo)
- AR_018: Testador Contract.md (arquivo novo) → Executor B
- AR_019: Hb cli Spec.md → Executor B

NAO há dependências cross-executor: A não depende de nada de B, B não depende de nada de A.

FIX: Criar diretório docs/_canon/agentes/ e o arquivo BATCH_001_exec_assignments.yaml com o seguinte conteúdo exato:

---INÍCIO DO CONTEÚDO---
batch_id: BATCH_001
base_branch: dev-changes-2
base_commit: FILL_ON_EXECUTION
created_at: '2026-02-20'
protocol_ref: docs/_canon/contratos/Dual Executor Contract.md

executor_a:
  branch: executor-a/batch-001
  ar_sequence:
    - '010'
    - '011'
    - '012'
    - '020'
  file_ownership:
    - scripts/run/hb_cli.py
    - docs/_canon/contratos/Dev Flow.md
  notes: >
    AR_010 MUST ser executada antes de AR_011 (011 depende de cmd_report corrigido).
    AR_012 e AR_020 sao independentes entre si mas no mesmo arquivo — executar nessa ordem.
    AR_020 e a ultima: bumpa HB_PROTOCOL_VERSION para 1.0.8.
    AR_013 ja foi marcada como SUPERSEDED por AR_020 — nao aparece na sequencia.

executor_b:
  branch: executor-b/batch-001
  ar_sequence:
    - '016'
    - '017'
    - '018'
    - '019'
  file_ownership:
    - docs/hbtrack/PRD Hb Track.md
    - docs/_canon/contratos/Testador Contract.md
    - docs/_canon/specs/Hb cli Spec.md
  notes: >
    AR_016 e AR_017 tocam o mesmo arquivo (PRD Hb Track.md) — executar nessa ordem.
    AR_018 cria arquivo novo (Testador Contract.md) — independente.
    AR_019 atualiza Hb cli Spec.md — independente de 016/017/018.

file_ownership_conflict_check:
  shared_files: []

completion_signals:
  executor_a: 'BATCH_001_EXEC_A: CONCLUIDO — branch executor-a/batch-001 pronta para merge'
  executor_b: 'BATCH_001_EXEC_B: CONCLUIDO — branch executor-b/batch-001 pronta para merge'

merge_order:
  - executor-a/batch-001
  - executor-b/batch-001
---FIM DO CONTEÚDO---

DIRETÓRIO A CRIAR: docs/_canon/agentes/ (se nao existir)
ARQUIVO A CRIAR (ÚNICO): docs/_canon/agentes/BATCH_001_exec_assignments.yaml
NAO modificar nenhum outro arquivo.

## Critérios de Aceite
1) docs/_canon/agentes/BATCH_001_exec_assignments.yaml existe. 2) Contém executor_a com ar_sequence contendo 010, 011, 012, 020. 3) Contém executor_b com ar_sequence contendo 016, 017, 018, 019. 4) Contém file_ownership_conflict_check com shared_files vazio. 5) Contém completion_signals para ambos os executores. 6) Contém protocol_ref apontando para Dual Executor Contract.md. 7) Contém merge_order definida.

## Validation Command (Contrato)
```
python -c "import pathlib; content = pathlib.Path('docs/_canon/agentes/BATCH_001_exec_assignments.yaml').read_text(encoding='utf-8'); assert 'executor_a' in content, 'FAIL: executor_a ausente'; assert 'executor_b' in content, 'FAIL: executor_b ausente'; assert all(x in content for x in ['010','011','012','020']), 'FAIL: ar_sequence executor_a incompleta'; assert all(x in content for x in ['016','017','018','019']), 'FAIL: ar_sequence executor_b incompleta'; assert 'shared_files' in content, 'FAIL: shared_files ausente'; assert 'completion_signals' in content, 'FAIL: completion_signals ausente'; assert 'merge_order' in content, 'FAIL: merge_order ausente'; assert 'protocol_ref' in content, 'FAIL: protocol_ref ausente'; print('PASS: BATCH_001_exec_assignments.yaml valido — Executor A=[010,011,012,020], Executor B=[016,017,018,019]')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_022_gov_dual_executor_batch_001.log`

## Riscos
- base_commit='FILL_ON_EXECUTION' — o Executor responsável por este AR DEVE substituir pelo hash real de git rev-parse HEAD no momento de criar a branch.
- Se Executor B iniciar antes de Executor A concluir AR_010 e precisar testar hb report, encontrará o bug de Status nao atualizado — isso é aceitável pois B nao depende de hb_cli.py.
- AR_019 (Hb cli Spec.md) documenta cmd_verify enquanto AR_020 (Executor A) implementa o codigo — spec e implementacao ficam em branches separadas e sao unificadas pelo merge do Arquiteto.
- A ordem do merge_order (A antes de B) garante que as mudancas de hb_cli.py entram primeiro, facilitando qualquer teste pos-merge.

## Análise de Impacto
_(A ser preenchido pelo Executor)_

---
## Carimbo de Execução
_(Gerado por hb report)_


### Execução em b2e7523
**Status Final**: ✅ SUCESSO
**Comando**: `python -c "import pathlib; content = pathlib.Path('docs/_canon/agentes/BATCH_001_exec_assignments.yaml').read_text(encoding='utf-8'); assert 'executor_a' in content, 'FAIL: executor_a ausente'; assert 'executor_b' in content, 'FAIL: executor_b ausente'; assert all(x in content for x in ['010','011','012','020']), 'FAIL: ar_sequence executor_a incompleta'; assert all(x in content for x in ['016','017','018','019']), 'FAIL: ar_sequence executor_b incompleta'; assert 'shared_files' in content, 'FAIL: shared_files ausente'; assert 'completion_signals' in content, 'FAIL: completion_signals ausente'; assert 'merge_order' in content, 'FAIL: merge_order ausente'; assert 'protocol_ref' in content, 'FAIL: protocol_ref ausente'; print('PASS: BATCH_001_exec_assignments.yaml valido — Executor A=[010,011,012,020], Executor B=[016,017,018,019]')"`
**Exit Code**: 0
**Evidence File**: `docs/hbtrack/evidence/AR_022_gov_dual_executor_batch_001.log`
**Python Version**: 3.11.9


### Verificacao Testador em b2e7523
**Status Testador**: ✅ VERIFICADO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_022_b2e7523/result.json`
