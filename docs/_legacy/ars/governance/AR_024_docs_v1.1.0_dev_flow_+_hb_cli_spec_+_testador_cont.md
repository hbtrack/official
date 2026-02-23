# AR_024 — Docs v1.1.0: Dev Flow + Hb cli Spec + Testador Contract

**Status**: 🔬 EM TESTE
**Versão do Protocolo**: 1.0.8

## Descrição
ARQUIVOS ALVO: docs/_canon/contratos/Dev Flow.md, docs/_canon/specs/Hb cli Spec.md, docs/_canon/contratos/Testador Contract.md

(B1) docs/_canon/contratos/Dev Flow.md:
- Linha 1: 'v1.0.8' => 'v1.1.0' (header HBTRACK_DEV_FLOW_CONTRACT)
- §1 Versao do protocolo: 'v1.0.8' => 'v1.1.0' em todas as ocorrencias de versao
- §5 Passo 6.5 (TESTADOR): apos 'Se REJEITADO: Executor MUST corrigir e repetir Passo 5->6->6.5.', adicionar:
  '- O Testador executa TRIPLE_RUN_COUNT=3 runs independentes do validation_command.'
  '- Todos os 3 runs MUST ter exit 0 E stdout_hash identico (triple_consistency=OK).'
  '- FLAKY_OUTPUT (todos exit 0 mas hash diferente entre runs) => REJEITADO — output nao-deterministico.'
- §6 Regras deterministicas: adicionar R0 ANTES de R1:
  'R0) validation_command trivialmente passavel (echo, true, exit 0, ou <30 chars sem assertions) => hb plan FAIL E_TRIVIAL_CMD.'

(B2) docs/_canon/specs/Hb cli Spec.md:
- Header: 'v1.0.8' => 'v1.1.0'
- §1 HB_PROTOCOL_VERSION: '1.0.8' => '1.1.0'
- §5 (hb plan pipeline): adicionar entre P4 e GATE 2:
  'P3.5) validation_command MUST ser nao-trivial: nao pode ser echo|true|exit 0|noop OU (len<30 chars sem keywords assert/pytest/check/verify/validate).'
  '    Senao: FAIL E_TRIVIAL_CMD (exit 2)'
- §10 (hb verify) V4: substituir descricao de re-execucao simples por:
  'V4) Re-executar validation_command TRIPLE_RUN_COUNT=3 vezes independentes.'
  '    Para cada run: registrar exit_code e stdout_hash=sha256(stdout)[:16].'
  '    triple_consistency = OK (todos exit 0 e hash identico) | FLAKY_OUTPUT (todos exit 0 mas hash diferente) | TRIPLE_FAIL (algum exit!=0).'
  '    testador_exit_final = 0 se OK; 2 caso contrario (FLAKY_OUTPUT ou TRIPLE_FAIL).'
- §8 Error codes: adicionar E_TRIVIAL_CMD e E_TRIPLE_FAIL na lista de codigos adicionais

(B3) docs/_canon/contratos/Testador Contract.md:
- Header: 'v1.0.0' => 'v1.1.0'
- §3 Protocolo Passo T4: atualizar de 'Executar validation_command independentemente' para 'Re-executar TRIPLE_RUN_COUNT=3 vezes independentemente'
- Adicionar Passo T4.5 apos T4:
  'Passo T4.5 -- TRIPLE-RUN   Verificar triple_consistency:'
  '  OK (todos exit 0 e hash identico) => VERIFICADO'
  '  FLAKY_OUTPUT (exit 0 mas hash diferente) => REJEITADO (nao-deterministico)'
  '  TRIPLE_FAIL (algum exit!=0) => REJEITADO'
- §4.1 result.json: adicionar no exemplo JSON os campos:
  '"run_count": 3,'
  '"runs": [{"run": 1, "exit_code": 0, "stdout_hash": "abc123...", "stdout_len": 45}, ...],'
  '"triple_consistency": "OK",'
- §5 Status: VERIFICADO agora exige triple_consistency=OK (adicionar nota)
- §2 AH-2: reforcar que validation_command trivial e bloqueado por GATE P3.5 em hb plan (nao apenas recomendado)

NAO modificar nenhum outro arquivo.

## Critérios de Aceite
1) Dev Flow.md contem 'v1.1.0', 'TRIPLE_RUN_COUNT', 'FLAKY_OUTPUT', 'E_TRIVIAL_CMD'. 2) Hb cli Spec.md contem 'v1.1.0', 'P3.5', 'E_TRIVIAL_CMD', 'TRIPLE_RUN_COUNT'. 3) Testador Contract.md contem 'v1.1.0', 'triple_consistency', 'FLAKY_OUTPUT', 'T4.5'.

## Validation Command (Contrato)
```
python -c "import pathlib; df=pathlib.Path('docs/_canon/contratos/Dev Flow.md').read_text(encoding='utf-8'); sp=pathlib.Path('docs/_canon/specs/Hb cli Spec.md').read_text(encoding='utf-8'); tc=pathlib.Path('docs/_canon/contratos/Testador Contract.md').read_text(encoding='utf-8'); assert 'v1.1.0' in df,'FAIL Dev Flow v1.1.0'; assert 'TRIPLE_RUN_COUNT' in df,'FAIL Dev Flow TRIPLE_RUN_COUNT'; assert 'FLAKY_OUTPUT' in df,'FAIL Dev Flow FLAKY_OUTPUT'; assert 'E_TRIVIAL_CMD' in df,'FAIL Dev Flow E_TRIVIAL_CMD'; assert 'v1.1.0' in sp,'FAIL Spec v1.1.0'; assert 'P3.5' in sp,'FAIL Spec P3.5'; assert 'E_TRIVIAL_CMD' in sp,'FAIL Spec E_TRIVIAL_CMD'; assert 'TRIPLE_RUN_COUNT' in sp,'FAIL Spec TRIPLE_RUN_COUNT'; assert 'v1.1.0' in tc,'FAIL Testador Contract v1.1.0'; assert 'triple_consistency' in tc,'FAIL Testador Contract triple_consistency'; assert 'FLAKY_OUTPUT' in tc,'FAIL Testador Contract FLAKY_OUTPUT'; assert 'T4.5' in tc,'FAIL Testador Contract T4.5'; print('PASS: docs v1.1.0 + triple-run + anti-trivial documentados OK')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_024_docs_v110.log`

## Rollback Plan (Contrato)
```
git restore "docs/_canon/contratos/Dev Flow.md" "docs/_canon/specs/Hb cli Spec.md" "docs/_canon/contratos/Testador Contract.md"
```
⚠️ **ATENÇÃO**: Este AR modifica banco. Execute rollback em caso de falha.

## Riscos
- Dev Flow.md §5 Passo 6.5 ja existe — ADICIONAR ao bloco existente, nao substituir.
- Testador Contract.md usa 'v1.0.0' no header — confirmar antes de editar.
- Hb cli Spec.md §10 V4 descreve re-execucao simples — SUBSTITUIR a descricao, nao adicionar.
- Manter numbering de secoes existentes — nao renumerar §10 para §11 etc.

## Análise de Impacto
**Executor**: Cline (Execução determinística)  
**Data**: 2026-02-21

**Leitura obrigatória do plano JSON**:
- ✅ Plano localizado e lido em `docs/_canon/planos/gov_006_determinismo_triple_run_v110.json` (task `id: "024"`).

**Verificação de estado real (antes de codar)**:
- ✅ `docs/_canon/contratos/Dev Flow.md` já contém `v1.1.0`, `TRIPLE_RUN_COUNT`, `FLAKY_OUTPUT`, `E_TRIVIAL_CMD`.
- ✅ `docs/_canon/specs/Hb cli Spec.md` já contém `v1.1.0`, `P3.5`, `E_TRIVIAL_CMD`, `TRIPLE_RUN_COUNT`, `E_TRIPLE_FAIL`.
- ✅ `docs/_canon/contratos/Testador Contract.md` já contém `triple_consistency`, `FLAKY_OUTPUT`, `T4.5` e compatibilidade `v1.1.0+`.

**Decisão de execução**:
- Escopo da AR_024 já está materializado no estado atual do repositório.
- Não há delta técnico para aplicar sem violar a regra "NÃO modificar nenhum outro arquivo".

**Impacto**:
- Nenhuma alteração de código/documentação adicional necessária para cumprir os critérios desta AR.
- Fluxo seguirá para mudança de status para `🔬 EM TESTE` + pós-passos obrigatórios (SSOT, rebuild de índice, hb_watch).

---
## Carimbo de Execução
_(Gerado por hb report)_



