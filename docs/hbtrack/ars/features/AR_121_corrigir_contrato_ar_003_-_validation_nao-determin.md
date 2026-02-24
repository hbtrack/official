# AR_121 — Corrigir contrato AR_003 — validation nao-deterministica

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.3.0

## Descrição
Atualizar secao '## Validation Command (Contrato)' de AR_003 (features). O validation_command atual invoca o arquivo de validacao legado na pasta temp que usa uuid4() gerando um UUID aleatorio a cada execucao. O valor aleatoria aparece na saida da excecao impressa via str(e), gerando behavior_hash diferente nos 3 runs do Testador. Resultado: REJEITADO com consistency=AH_DIVERGENCE. SUBSTITUICAO COMPLETA do validation_command por comando inline deterministico: usar UUID hardcoded fixo '00000000-0000-0000-0000-000000000001', NAO imprimir o conteudo da excecao no bloco goalkeeper_save (apenas checar presenca de palavras-chave em str(e) sem printar). A verificacao de canais: (1) CanonicalEventType nao tem valores invalidos; (2) ScoutEventCreate aceita campos period_number, game_time_seconds, x_coord, y_coord; (3) goalkeeper_save levanta ValidationError quando related_event_id=None; (4) EventType aponta para CanonicalEventType. Saida final: 'PASS: Schemas Pydantic canonicos OK'. Atualizar tambem o '**Comando**:' no carimbo historico se houver referencia ao arquivo legado de temp.

## Critérios de Aceite
- Secao '## Validation Command (Contrato)' de AR_003 nao contem mais a referencia ao arquivo de validacao legado da pasta temp
- Secao '## Validation Command (Contrato)' de AR_003 contem UUID fixo '00000000-0000-0000-0000-000000000001'
- Executar o novo validation_command 3 vezes gera o MESMO behavior_hash (deterministico)
- Executar o novo validation_command retorna exit 0 com 'PASS' na saida
- Status do AR_003 permanece inalterado — apenas o contrato de verificacao muda
- Nenhum outro arquivo modificado alem de AR_003.md

## Validation Command (Contrato)
```
python temp/validate_ar121.py
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_121/executor_main.log`

## Rollback Plan (Contrato)
```
git checkout -- docs/hbtrack/ars/features/AR_003_schemas_pydantic_canônicos_de_scout.md
```
⚠️ **ATENÇÃO**: Este AR modifica banco. Execute rollback em caso de falha.

## Notas do Arquiteto
Causa raiz: uuid4() muda a cada run; str(e) na impressao do ValidationError incluia o UUID. Fix: UUID hardcoded + NAO imprimir conteudo da excecao. AH_DIVERGENCE: nova versao do validation_command (nao nova implementacao). AR path tem caractere especial — write_scope [].

## Análise de Impacto
**Escopo**: Edição direta em `docs/hbtrack/ars/features/AR_003_schemas_pydantic_canônicos_de_scout.md`.

**Impacto**:
- Substituído o `validation_command` atual (que referencia `temp/validate_ar003.py` com `uuid4()` não-determinístico) por comando inline com UUID fixo `00000000-0000-0000-0000-000000000001`.
- Output passa a ser determinístico entre runs, eliminando AH_DIVERGENCE no Testador.
- Nenhum código de produto modificado — apenas o contrato de verificação da AR_003.

**Risco**: Baixo. Mudança isolada em arquivo de documentação de AR.

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução Executor em a06d856
**Status Executor**: ❌ FALHA
**Comando**: `python temp/validate_ar121.py`
**Exit Code**: 1
**Timestamp UTC**: 2026-02-24T19:04:44.003115+00:00
**Behavior Hash**: f9ea257a0b3bc2bc136ea9c22f16c956225ee6e05c3a3ab93818ab634d66ccd7
**Evidence File**: `docs/hbtrack/evidence/AR_121/executor_main.log`
**Python Version**: 3.11.9

### Execução Executor em a06d856
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python temp/validate_ar121.py`
**Exit Code**: 0
**Timestamp UTC**: 2026-02-24T19:05:30.503987+00:00
**Behavior Hash**: 4740a157d82b13950ffeb35bf430b98b17cc726f1feac96917508a86a0d7e112
**Evidence File**: `docs/hbtrack/evidence/AR_121/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em 09654e9
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_121_09654e9/result.json`

### Selo Humano em 162dc4e
**Status Humano**: ✅ VERIFICADO
**Timestamp UTC**: 2026-02-24T19:18:45.431664+00:00
**Motivo**: —
**TESTADOR_REPORT**: `_reports/testador/AR_121_09654e9/result.json`
**Evidence File**: `docs/hbtrack/evidence/AR_121/executor_main.log`
