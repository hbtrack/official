# AR_027 — Agente-Testador Contract v2.0: Triple-Run Enterprise + Anti-Alucinação Máximo

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.1.0

## Descrição
ARQUIVO ALVO: docs/_canon/contratos/Testador Contract.md (UPGRADE de v1.0.0 para v2.0.0)

O contrato do Agente-Testador é upgradado para v2.0.0 com enforcement enterprise completo.

(C1) UPGRADE docs/_canon/contratos/Testador Contract.md — manter TODA a estrutura existente e ADICIONAR:

§0 HEADER (atualizar)
- v1.0.0 → v2.0.0
- Adicionar: 'Status: ENTERPRISE'
- Adicionar: 'Compatible: Protocol v1.1.0+'

§1 IDENTIDADE (atualizar)
- Adicionar diagrama enterprise:
  ```
  ┌─────────────┐    ┌────────────┐    ┌────────────┐    ┌─────────┐
  │  ARQUITETO   │───→│  EXECUTOR   │───→│  TESTADOR   │───→│ HUMANO  │
  │  (Planeja)   │    │ (Implementa)│    │ (Verifica)  │    │ (DONE)  │
  │  hb plan     │    │  hb report  │    │  hb verify  │    │         │
  └─────────────┘    └────────────┘    └────────────┘    └─────────┘
       ▲                    ▲                │
       │                    └────────────────┘
       │                    🔴 REJEITADO → E5→E4→T (ciclo)
       └─ BLOCKED_INPUT (sobe ao Arquiteto)
  ```

§2 REGRAS ANTI-ALUCINAÇÃO (atualizar AH-1 a AH-7, adicionar AH-8 a AH-12)
- AH-8: O Testador MUST executar EXATAMENTE TRIPLE_RUN_COUNT=3 runs independentes
- AH-9: Todos os 3 runs MUST ter exit 0 E stdout_hash idêntico para VERIFICADO
- AH-10: FLAKY_OUTPUT (todos exit 0 mas hash diferente) = REJEITADO (não-determinístico)
- AH-11: TRIPLE_FAIL (qualquer run com exit != 0) = REJEITADO
- AH-12: O Testador MUST verificar que o Evidence Pack do Executor foi gerado ANTES do verify (timestamp check)

§3 PROTOCOLO DE VERIFICAÇÃO ENTERPRISE (atualizar T1-T7, adicionar T4.5)
- T4 atualizar: 'Re-executar' → 'Re-executar TRIPLE_RUN_COUNT=3 vezes independentes'
- T4.5 (NOVO): TRIPLE-RUN CONSISTENCY CHECK
  Para cada run: registrar exit_code + stdout_hash=sha256(stdout)[:16]
  triple_consistency = OK | FLAKY_OUTPUT | TRIPLE_FAIL
  Regra: VERIFICADO requer triple_consistency=OK
- T8 (NOVO): RELATÓRIO AO ARQUITETO
  Após verificação, o Testador MUST entregar ao Arquiteto:
  - ar_id, status_testador, triple_consistency, run_count
  - runs_data (exit_code + stdout_hash por run)
  - rejection_reason (se aplicável)
  - evidence_pack_path

§4 RESULT.JSON ENTERPRISE (atualizar)
- Adicionar ao exemplo:
  'run_count': 3
  'runs': [{'run': 1, 'exit_code': 0, 'stdout_hash': 'abc123...', 'stdout_len': 45}, ...]
  'triple_consistency': 'OK'

§5 STATUS (atualizar)
- VERIFICADO agora exige: re-execução exit 0 + consistency OK + triple_consistency OK
- REJEITADO agora inclui: FLAKY_OUTPUT e TRIPLE_FAIL além de AH_DIVERGENCE

§9 CONTRATO ENTERPRISE: GARANTIA DOS 3 AGENTES (NOVO)
- O Testador é o ÚLTIMO guardião antes do Humano
- O Testador MUST NOT ter viés de confirmação — não sabe o que o Executor fez internamente
- O Testador MUST operar em ambiente IDÊNTICO ao do Executor (mesma máquina, mesmo venv, mesmo commit)
- O Testador MUST reportar FATOS, não interpretações
- Se o Testador encontrar divergência sistêmica (>3 ARs rejeitadas seguidas), MUST sinalizar ao Humano como possível BUG de processo

§10 INDEPENDÊNCIA ABSOLUTA (NOVO)
- O Testador MUST NOT receber instruções do Executor
- O Testador MUST NOT ler logs informais do Executor (apenas Evidence Pack formal)
- O Testador MUST NOT aceitar 'exceções' ou 'waivers' que não estejam em WAIVERS.yaml
- O Testador MUST NOT modificar código — se algo precisa ser corrigido, rejeitar e devolver ao Executor

§11 ANALOGIA DO HANDEBOL (contexto cultural do projeto) (NOVO)
- Como no handebol: o goleiro (Testador) é a última linha de defesa
- O armador (Arquiteto) cria as jogadas, o pivô (Executor) finaliza
- Mas é o goleiro que decide se o gol foi válido
- 3 jogadores, 3 papéis distintos, 1 objetivo: vitória determinística

MANTER todas as seções existentes (§1-§8) — apenas ADICIONAR e ATUALIZAR conforme descrito.

## Critérios de Aceite
1) docs/_canon/contratos/Testador Contract.md versão v2.0.0. 2) Contém AH-8 a AH-12. 3) Contém T4.5 com triple_consistency. 4) Contém §9 'GARANTIA DOS 3 AGENTES'. 5) Contém §10 'INDEPENDÊNCIA ABSOLUTA'. 6) Contém 'FLAKY_OUTPUT', 'TRIPLE_FAIL', triple_consistency. 7) Contém §11 referência ao handebol. 8) Mantém AH-1 a AH-7 originais intactas.

## Validation Command (Contrato)
```
python -c "import pathlib; tc=pathlib.Path('docs/_canon/contratos/Testador Contract.md').read_text(encoding='utf-8'); assert 'v2.0.0' in tc,'FAIL not v2.0.0'; assert 'AH-8' in tc,'FAIL no AH-8'; assert 'AH-9' in tc,'FAIL no AH-9'; assert 'AH-10' in tc,'FAIL no AH-10'; assert 'AH-11' in tc,'FAIL no AH-11'; assert 'AH-12' in tc,'FAIL no AH-12'; assert 'AH-1' in tc,'FAIL AH-1 removed'; assert 'AH-7' in tc,'FAIL AH-7 removed'; assert 'T4.5' in tc,'FAIL no T4.5'; assert 'triple_consistency' in tc,'FAIL no triple_consistency'; assert 'FLAKY_OUTPUT' in tc,'FAIL no FLAKY_OUTPUT'; assert 'TRIPLE_FAIL' in tc,'FAIL no TRIPLE_FAIL'; assert 'GARANTIA DOS 3 AGENTES' in tc or '9' in tc,'FAIL no S9'; assert 'INDEPEND' in tc.upper(),'FAIL no S10'; assert 'handebol' in tc.lower() or 'goleiro' in tc.lower(),'FAIL no S11'; print('PASS: Testador Contract v2.0.0 enterprise completo')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_027_testador_contract_enterprise.log`

## Riscos
- UPGRADE de arquivo existente — MUST preservar §1-§8 originais intactos.
- Header muda de v1.0.0 para v2.0.0 — MUST atualizar TODAS as referências de versão.
- §9-§11 são seções NOVAS — MUST ser adicionadas APÓS as existentes, não intercaladas.
- AH-8 a AH-12 MUST ser adicionadas ao bloco §2 existente, não em seção separada.
- Cross-reference: Testador Contract MUST referenciar Arquiteto Contract e Executor Contract.

## Análise de Impacto
- Arquivos afetados: [docs/hbtrack/ars/AR_027_agente-testador_contract_v2.0_triple-run_enterpris.md, docs/_canon/contratos/Testador Contract.md]
- Mudança no Schema? [Não]
- Risco de Regressão? [Baixo]

---
## Carimbo de Execução
_(Gerado por hb report)_



### Execução em b2e7523
**Status Final**: ✅ SUCESSO
**Comando**: `python -c "import pathlib; tc=pathlib.Path('docs/_canon/contratos/Testador Contract.md').read_text(encoding='utf-8'); assert 'v2.0.0' in tc,'FAIL not v2.0.0'; assert 'AH-8' in tc,'FAIL no AH-8'; assert 'AH-9' in tc,'FAIL no AH-9'; assert 'AH-10' in tc,'FAIL no AH-10'; assert 'AH-11' in tc,'FAIL no AH-11'; assert 'AH-12' in tc,'FAIL no AH-12'; assert 'AH-1' in tc,'FAIL AH-1 removed'; assert 'AH-7' in tc,'FAIL AH-7 removed'; assert 'T4.5' in tc,'FAIL no T4.5'; assert 'triple_consistency' in tc,'FAIL no triple_consistency'; assert 'FLAKY_OUTPUT' in tc,'FAIL no FLAKY_OUTPUT'; assert 'TRIPLE_FAIL' in tc,'FAIL no TRIPLE_FAIL'; assert 'GARANTIA DOS 3 AGENTES' in tc or '9' in tc,'FAIL no S9'; assert 'INDEPEND' in tc.upper(),'FAIL no S10'; assert 'handebol' in tc.lower() or 'goleiro' in tc.lower(),'FAIL no S11'; print('PASS: Testador Contract v2.0.0 enterprise completo')"`
**Exit Code**: 0
**Evidence File**: `docs/hbtrack/evidence/AR_027_testador_contract_enterprise.log`
**Python Version**: 3.11.9


### Verificacao Testador em b2e7523
**Status Testador**: ✅ VERIFICADO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_027_b2e7523/result.json`

### Verificacao Testador em b2e7523
**Status Testador**: ✅ VERIFICADO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_027_b2e7523/result.json`
