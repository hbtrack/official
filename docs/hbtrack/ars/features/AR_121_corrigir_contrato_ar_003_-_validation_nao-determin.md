# AR_121 — Corrigir contrato AR_003 — validation nao-deterministica

**Status**: 🔲 PENDENTE
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
python -c "import pathlib,subprocess,sys; ar=list(pathlib.Path('docs/hbtrack/ars/features').glob('AR_003*.md'))[0]; content=ar.read_text(encoding='utf-8'); assert 'temp/validate_ar003' not in content,'FAIL: arquivo de validacao legado ainda referenciado no AR_003'; assert '00000000-0000-0000-0000-000000000001' in content,'FAIL: UUID fixo nao encontrado no novo validation command'; vc_raw=[s for s in content.split('\`\`\`') if 'sys.path' in s or ('uuid.UUID' in s and 'import' in s)]; assert vc_raw,'FAIL: nenhum code block com UUID fixo encontrado'; cmd=vc_raw[0].strip(); runs=[subprocess.run([sys.executable,'-c',cmd[len('python -c '):].strip().strip('\"')],capture_output=True,text=True,encoding='utf-8') for _ in range(3)]; assert all(r.returncode==0 for r in runs),f'FAIL: exit nao-zero: {runs[0].stderr[:200]}'; hashes=list(set(r.stdout.strip() for r in runs)); assert len(hashes)==1,f'FAIL: outputs divergem entre runs (nao-deterministico): {hashes}'; assert 'PASS' in runs[0].stdout,'FAIL: PASS nao na saida'; print('PASS AR_121: AR_003 validation_command corrigido e deterministico')"
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
_(A ser preenchido pelo Executor)_

---
## Carimbo de Execução
_(Gerado por hb report)_

