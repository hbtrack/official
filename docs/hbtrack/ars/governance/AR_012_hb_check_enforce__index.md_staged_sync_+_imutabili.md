# AR_012 — hb check: enforce _INDEX.md staged sync + imutabilidade de ARs SUCESSO

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.0.6

## Descrição
PROBLEMA: Qualquer pessoa pode editar ARs concluídas (Status ✅ SUCESSO) diretamente sem deixar rastro. Além disso, nada impede que o _INDEX.md fique dessincronizado das ARs no commit.

FIX: Adicionar 2 novos checks em cmd_check (após o check C4 existente):

C5 — Sync obrigatório do _INDEX.md:
- Obter lista de ARs staged: ars_staged = [f for f in staged_files if f.startswith(AR_DIR) and 'AR_' in f and not f.endswith('_INDEX.md')]
- Se ars_staged não estiver vazia: verificar se 'docs/hbtrack/ars/_INDEX.md' está em staged_files
- Se _INDEX.md NÃO estiver staged: fail(E_AR_INDEX_NOT_STAGED, 'ARs staged sem _INDEX.md staged — execute hb plan ou hb report para regenerar o index', exit_code=1)

C6 — Imutabilidade de ARs SUCESSO:
- Para cada f em ars_staged que não é _INDEX.md:
  - Executar: git show HEAD:<f> (para obter conteúdo original no HEAD)
  - Se returncode != 0: arquivo é novo (Added) — pular check de imutabilidade
  - Se returncode == 0: ler conteúdo original
  - Se '**Status**: ✅ SUCESSO' em conteúdo_original:
    - Ler conteúdo staged atual (open(repo_root / f))
    - Extrair conteúdo PRÉ-CARIMBO: tudo antes da linha '---\n## Carimbo de Execução'
    - Comparar pre_carimbo_original vs pre_carimbo_staged
    - Se divergirem: fail(E_AR_IMMUTABLE, f'{f}: AR com ✅ SUCESSO não pode ter corpo modificado manualmente', exit_code=1)

ARQUIVO A MODIFICAR (ÚNICO): scripts/run/hb_cli.py
- Modificar função cmd_check: adicionar C5 e C6 após o bloco C4.
- Adicionar constantes de erro: E_AR_INDEX_NOT_STAGED e E_AR_IMMUTABLE (junto às outras constantes no topo do arquivo).

NAO modificar nenhum outro arquivo além de scripts/run/hb_cli.py.

## Critérios de Aceite
1) hb check falha com E_AR_INDEX_NOT_STAGED se AR staged sem _INDEX.md staged. 2) hb check falha com E_AR_IMMUTABLE se AR com Status ✅ SUCESSO no HEAD tiver corpo (pré-carimbo) modificado. 3) hb check continua passando quando _INDEX.md está staged junto com ARs. 4) ARs novas (Added, sem HEAD) não disparam E_AR_IMMUTABLE. 5) As constantes E_AR_INDEX_NOT_STAGED e E_AR_IMMUTABLE existem em hb_cli.py.

## Validation Command (Contrato)
```
python -c "import re, pathlib; src=pathlib.Path('scripts/run/hb_cli.py').read_text(encoding='utf-8'); assert 'E_AR_INDEX_NOT_STAGED' in src, 'FAIL: E_AR_INDEX_NOT_STAGED ausente'; assert 'E_AR_IMMUTABLE' in src, 'FAIL: E_AR_IMMUTABLE ausente'; fn=re.search(r'def cmd_check.*?(?=\ndef [a-z_]|\Z)', src, re.DOTALL); assert fn, 'cmd_check not found'; body=fn.group(0); assert '_INDEX.md' in body, 'FAIL: _INDEX.md check ausente em cmd_check'; assert 'E_AR_IMMUTABLE' in body, 'FAIL: imutabilidade ausente em cmd_check'; print('PASS: cmd_check contém C5 (index sync) e C6 (imutabilidade)')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_012_gov_ar_check_immutability.log`

## Riscos
- C6 usa 'git show HEAD:<path>' — se o repo não tiver HEAD (primeiro commit), o comando falha com returncode != 0. Tratar como 'arquivo novo' (pular check de imutabilidade) para não bloquear o primeiro commit.
- A comparação de pre-carimbo deve ser exata (strip() para remover whitespace trailing) para evitar falsos positivos por diferenças de newline.
- C5 (index sync): a constante AR_DIR já existe no hb_cli.py — usar a mesma para consistência na detecção de ARs staged.
- Se AR_010 ainda não foi implementada (Status header não atualizado), C6 pode não encontrar '✅ SUCESSO' no HEAD — comportamento degradado (não bloqueia). Implementar AR_010 antes de AR_012.

## Análise de Impacto
_(A ser preenchido pelo Executor)_

---
## Carimbo de Execução
_(Gerado por hb report)_


### Execução em b2e7523
**Status Final**: ✅ SUCESSO
**Comando**: `python -c "import re, pathlib; src=pathlib.Path('scripts/run/hb_cli.py').read_text(encoding='utf-8'); assert 'E_AR_INDEX_NOT_STAGED' in src, 'FAIL: E_AR_INDEX_NOT_STAGED ausente'; assert 'E_AR_IMMUTABLE' in src, 'FAIL: E_AR_IMMUTABLE ausente'; fn=re.search(r'def cmd_check.*?(?=\ndef [a-z_]|\Z)', src, re.DOTALL); assert fn, 'cmd_check not found'; body=fn.group(0); assert '_INDEX.md' in body, 'FAIL: _INDEX.md check ausente em cmd_check'; assert 'E_AR_IMMUTABLE' in body, 'FAIL: imutabilidade ausente em cmd_check'; print('PASS: cmd_check contém C5 (index sync) e C6 (imutabilidade)')"`
**Exit Code**: 0
**Evidence File**: `docs/hbtrack/evidence/AR_012_gov_ar_check_immutability.log`
**Python Version**: 3.11.9


### Verificacao Testador em b2e7523
**Status Testador**: ✅ VERIFICADO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_012_b2e7523/result.json`
