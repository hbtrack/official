# AR_118 — Corrigir contrato AR_044 — contagens de planos e orphan check

**Status**: 🔲 PENDENTE
**Versão do Protocolo**: 1.3.0

## Descrição
Atualizar secao Validation Command de AR_044 (drafts). Tres ajustes: (1) remover a assercao 'assert not orphans' (JSONs no diretorio raiz de planos sao validos para planos em elaboracao); (2) count de infra: '==3' deve ser '>=3' (quatro JSONs agora nessa pasta); (3) count de features: '==6' deve ser '>=4' (conta atual e 5). O check de subdiretorios existentes e o count governance >=11 permanecem. Atualizar tambem o carimbo historico Comando.

## Critérios de Aceite
- Secao Validation Command de AR_044 nao contem mais 'assert not orphans'
- Secao Validation Command de AR_044 usa '>=3' para infra e '>=4' para features
- Subdirs governance, competitions, infra, features ainda verificados como existentes
- Executar o novo validation_command retorna exit 0 com PASS na saida
- Status do AR_044 permanece SUCESSO

## Validation Command (Contrato)
```
python -c "import pathlib; ar=list(pathlib.Path('docs/hbtrack/ars/drafts').glob('AR_044*.md'))[0]; content=ar.read_text(encoding='utf-8'); assert 'assert not orphans' not in content,'FAIL: old assert not orphans ainda no AR_044'; base=pathlib.Path('docs/_canon/planos'); counts={d:len(list((base/d).glob('*.json'))) for d in ['governance','competitions','infra','features']}; assert counts.get('governance',0)>=11; assert counts.get('competitions',0)>=8; assert counts.get('infra',0)>=3; assert counts.get('features',0)>=4; print(f'PASS AR_118: AR_044 validation_command corrigido, counts OK {counts}')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_118/executor_main.log`

## Rollback Plan (Contrato)
```
git checkout -- docs/hbtrack/ars/drafts/AR_044_git_mv_docs__canon_planos__→_governance_,_competit.md
```
⚠️ **ATENÇÃO**: Este AR modifica banco. Execute rollback em caso de falha.

## Notas do Arquiteto
Causa raiz: novos planos foram criados pelo Arquiteto no root de docs/_canon/planos/ (pratica valida para planos em elaboracao pre-dispatch). Contagens de infra e features mudaram com adicao/remocao de planos. Fix: usar lower bounds (>=) em vez de exato (==), remover assert orphans. AR file path contem seta Unicode e virgula — usa write_scope [].

## Análise de Impacto
_(A ser preenchido pelo Executor)_

---
## Carimbo de Execução
_(Gerado por hb report)_

