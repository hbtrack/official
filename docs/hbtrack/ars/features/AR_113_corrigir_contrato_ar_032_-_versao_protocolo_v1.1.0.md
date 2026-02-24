# AR_113 — Corrigir contrato AR_032 — versao protocolo v1.1.0 obsoleta

**Status**: 🔲 PENDENTE
**Versão do Protocolo**: 1.3.0

## Descrição
Atualizar secao Validation Command de AR_032 (governance). Uma unica mudanca cirurgica: substituir a verificacao de versao do protocolo de exato 'v1.1.0' para 'v1.' (aceitar qualquer v1.x). Protocolo evoluiu de v1.1.0 para v1.3.0; a verificacao estava desatualizada. Todos os outros checks de palavras-chave da especificacao permanecem intactos. SUBSTITUICAO: trocar apenas o trecho assert 'v1.1.0' in v.stdout pelo trecho assert 'v1.' in v.stdout. NAO alterar Status, Descricao, ACs, Write Scope, Evidence File, lista de keywords nem nenhuma outra linha. Atualizar tambem o carimbo historico Comando se houver referencia ao mesmo assert obsoleto.

## Critérios de Aceite
- Secao Validation Command de AR_032 nao contem mais 'v1.1.0' in v.stdout
- Secao Validation Command de AR_032 contem 'v1.' in v.stdout
- Todos os demais checks do validation_command permanecem intactos
- Executar o novo validation_command retorna exit 0 com PASS na saida
- Status do AR_032 permanece SUCESSO
- Nenhum outro arquivo modificado alem de AR_032

## Validation Command (Contrato)
```
python -c "import pathlib,subprocess,sys; ar=list(pathlib.Path('docs/hbtrack/ars/governance').glob('AR_032*.md'))[0]; content=ar.read_text(encoding='utf-8'); vc=content.split('Validation Command')[1].split('\`\`\`')[1] if 'Validation Command' in content else ''; assert \"'v1.1.0' in v.stdout\" not in vc,'FAIL: old v1.1.0 assertion still present'; assert \"'v1.' in v.stdout\" in vc,'FAIL: new v1. assertion not found'; assert 'E_TRIVIAL_CMD' in vc,'FAIL: keywords check removido'; v=subprocess.run([sys.executable,'scripts/run/hb_cli.py','version'],capture_output=True,text=True,encoding='utf-8'); assert 'v1.' in v.stdout,f'FAIL: CLI version inesperado: {v.stdout.strip()}'; print('PASS AR_113: AR_032 validation_command corrigido para aceitar v1.x')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_113/executor_main.log`

## Rollback Plan (Contrato)
```
git checkout -- docs/hbtrack/ars/governance/AR_032_hb_cli_spec.md_sync_v1.0.8_→_v1.1.0_gate_p3.5,_hbl.md
```
⚠️ **ATENÇÃO**: Este AR modifica banco. Execute rollback em caso de falha.

## Notas do Arquiteto
Causa raiz: CLI promovido de v1.1.0 para v1.3.0 em sessoes posteriores a criacao de AR_032. Fix: validacao aceita qualquer v1.x. AR file path contem seta Unicode e virgula — usa write_scope [].

## Análise de Impacto
_(A ser preenchido pelo Executor)_

---
## Carimbo de Execução
_(Gerado por hb report)_

