# AR_123 — Fix AR_003 validation_command — cmd-safe via arquivo de verificacao dedicado

**Status**: 🔲 PENDENTE
**Versão do Protocolo**: 1.3.0

## Descrição
Causa raiz do REJEITADO AH_DIVERGENCE em AR_003: o campo '## Validation Command (Contrato)' contem codigo Python puro iniciando com 'import sys, uuid'. O run_cmd do hb_cli executa via subprocess.run(cmd, shell=True) e o cmd.exe do Windows tenta rodar 'import' como comando de shell, gerando 'nao reconhecido como comando interno' (stderr 108 chars, exit 1 consistente 3x). O Executor havia rodado o codigo diretamente como arquivo (exit 0), criando a divergencia. SOLUCAO: (1) Criar arquivo de verificacao dedicado em docs/hbtrack/evidence/AR_003/validate_ar003 (nome validate_ar003, extensao Python) com o codigo deterministico (UUID fixo '00000000-0000-0000-0000-000000000001', goalkeeper_save assert, sem outputs nao-deterministicos). (2) Atualizar a secao '## Validation Command (Contrato)' em AR_003.md para conter somente o comando de execucao desse arquivo de verificacao. A logica de verificacao nao muda: CanonicalEventType sem valores invalidos, ScoutEventCreate com campos period_number/game_time_seconds/x_coord/y_coord, goalkeeper_save requer related_event_id, EventType is CanonicalEventType.

## Critérios de Aceite
- Arquivo docs/hbtrack/evidence/AR_003/validate_ar003.py existe e contem o codigo deterministico (UUID fixo, goalkeeper_save assert)
- AR_003.md campo '## Validation Command (Contrato)' contem SOMENTE: python docs/hbtrack/evidence/AR_003/validate_ar003.py
- Executar o validation_command na raiz do repo: exit 0, stdout contem 'PASS: Schemas Pydantic canonicos OK'
- Triple run gera o mesmo comportamento (deterministico)
- Nenhuma outra logica de verificacao alterada

## Validation Command (Contrato)
```
python docs/hbtrack/evidence/AR_003/validate_ar003.py
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_123/executor_main.log`

## Rollback Plan (Contrato)
```
git checkout -- docs/hbtrack/ars/features/AR_003_schemas_pydantic_canônicos_de_scout.md
git clean -fd docs/hbtrack/evidence/AR_003/
```
⚠️ **ATENÇÃO**: Este AR modifica banco. Execute rollback em caso de falha.

## Notas do Arquiteto
write_scope=[] — alteracoes sao exclusivamente em docs/hbtrack/ars/ e docs/hbtrack/evidence/, nao em governed roots. Mesmo padrao do plano fix_ar003_deterministic_validation.json (AR_121). Nenhuma mudanca em codigo de produto.

## Análise de Impacto
_(A ser preenchido pelo Executor)_

---
## Carimbo de Execução
_(Gerado por hb report)_

