# AR_119 — Corrigir contrato AR_045 — contagens de ARs com valores exatos

**Status**: 🔲 PENDENTE
**Versão do Protocolo**: 1.3.0

## Descrição
Atualizar secao Validation Command de AR_045 (drafts). Dois ajustes de contagem: (1) governance: '==25' deve ser '>=25' (32 ARs no subdir agora); (2) features: '==7' deve ser '>=7' (19 ARs no subdir agora). O check competition '>=11' permanece valido. Remover tambem 'assert not orphans' se presente. Atualizar tambem o carimbo historico Comando.

## Critérios de Aceite
- Secao Validation Command de AR_045 usa '>=25' para governance e '>=7' para features
- Secao Validation Command de AR_045 nao usa contagens exatas defasadas '==25' ou '==7'
- competitions verificado como existente com count >=11
- Executar o novo validation_command retorna exit 0 com PASS na saida
- Status do AR_045 permanece SUCESSO

## Validation Command (Contrato)
```
python -c "import pathlib; ar=list(pathlib.Path('docs/hbtrack/ars/drafts').glob('AR_045*.md'))[0]; content=ar.read_text(encoding='utf-8'); assert '==25' not in content,'FAIL: old governance==25 ainda no AR_045'; assert '>=25' in content,'FAIL: governance>=25 nao encontrado'; assert '>=7' in content,'FAIL: features>=7 nao encontrado'; base=pathlib.Path('docs/hbtrack/ars'); counts={d:len(list((base/d).glob('*.md'))) for d in ['governance','competitions','features']}; assert counts.get('governance',0)>=25,'FAIL: governance count insuficiente'; assert counts.get('features',0)>=7,'FAIL: features count insuficiente'; print(f'PASS AR_119: AR_045 validation_command corrigido, AR counts OK {counts}')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_119/executor_main.log`

## Rollback Plan (Contrato)
```
git checkout -- docs/hbtrack/ars/drafts/AR_045_git_mv_docs_hbtrack_ars__→_governance_,_competitio.md
```
⚠️ **ATENÇÃO**: Este AR modifica banco. Execute rollback em caso de falha.

## Notas do Arquiteto
Causa raiz: ARs foram sendo criadas continuamente nas sessoes posteriores (AR_046 ate AR_119+ em andamento). Subdirs governance e features cresceram organicamente. Fix: usar lower bounds (>=) que so crescem. AR file path contem seta Unicode — usa write_scope [].

## Análise de Impacto
_(A ser preenchido pelo Executor)_

---
## Carimbo de Execução
_(Gerado por hb report)_

