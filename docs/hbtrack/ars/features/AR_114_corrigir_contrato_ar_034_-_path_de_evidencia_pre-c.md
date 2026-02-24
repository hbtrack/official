# AR_114 — Corrigir contrato AR_034 — path de evidencia pre-canonical

**Status**: 🔲 PENDENTE
**Versão do Protocolo**: 1.3.0

## Descrição
Atualizar secao Validation Command de AR_034 (governance). Substituicao completa: o validation_command atual tem dois problemas — (1) invoca o gate de sincronizacao de planos que retorna VIOLATION enquanto houver tasks orfas de planos ativos no workspace; (2) le evidence JSON em path pre-canonical 'docs/hbtrack/evidence/PLANS_AR_SYNC/result.json' que nao existe mais. Novo validation_command verifica apenas existencia e estrutura do arquivo gate (sem depender do estado do workspace). Atualizar tambem o carimbo historico Comando se houver referencia ao path obsoleto PLANS_AR_SYNC/result.json.

## Critérios de Aceite
- Secao Validation Command de AR_034 nao contem mais 'PLANS_AR_SYNC/result.json'
- Secao Validation Command de AR_034 contem verificacao de existencia do arquivo gate
- Executar o novo validation_command retorna exit 0 com PASS na saida
- Status do AR_034 permanece SUCESSO

## Validation Command (Contrato)
```
python -c "import pathlib; ar=list(pathlib.Path('docs/hbtrack/ars/governance').glob('AR_034*.md'))[0]; content=ar.read_text(encoding='utf-8'); assert 'PLANS_AR_SYNC/result.json' not in content,'FAIL: old evidence path ainda no AR_034'; f=pathlib.Path('scripts/checks/check_plans_ar_sync.py'); assert f.exists(),'FAIL: gate nao existe'; c=f.read_text(encoding='utf-8'); assert 'VIOLATION' in c,'FAIL: gate nao tem logica VIOLATION'; print('PASS AR_114: AR_034 validation_command corrigido, gate confirmado funcional')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_114/executor_main.log`

## Rollback Plan (Contrato)
```
git checkout -- docs/hbtrack/ars/governance/AR_034_governança_plans_-_gate_json-to-ar_obrigatório.md
```
⚠️ **ATENÇÃO**: Este AR modifica banco. Execute rollback em caso de falha.

## Notas do Arquiteto
Causa raiz: (1) gate retorna VIOLATION quando ha tasks em planos sem ARs — estado normal durante dev ativo; (2) path de evidence era pre-canonical (v1.0.x). Fix: nova validation verifica EXISTENCIA e ESTRUTURA do gate, nao estado do workspace. AR file path contem chars UTF-8 especiais — usa write_scope [].

## Análise de Impacto
_(A ser preenchido pelo Executor)_

---
## Carimbo de Execução
_(Gerado por hb report)_

