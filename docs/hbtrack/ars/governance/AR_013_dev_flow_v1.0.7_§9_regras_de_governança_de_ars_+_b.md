# AR_013 — Dev Flow v1.0.7: §9 Regras de Governança de ARs + bump protocolo

**Status**: ⛔ SUPERSEDED — ver AR_020
**Versão do Protocolo**: 1.0.6

## Descrição
PROBLEMA: As regras de governança de ARs (index automático, imutabilidade, sync obrigatório) implementadas em AR_011 e AR_012 não estão documentadas no SSOT canônico do fluxo (Dev Flow.md). Sem documentação no contrato, as regras podem ser esquecidas ou ignoradas.

FIX em 2 arquivos:

(A) docs/_canon/contratos/Dev Flow.md:
- Linha 1: trocar 'v1.0.6' por 'v1.0.7'
- §1 (Versão): trocar 'v1.0.6' por 'v1.0.7' em todas as ocorrências
- Adicionar ao final do arquivo uma nova seção §9:

```
## 9. Regras de Governança de ARs (obrigatório — mecanizado)

R-AR-1) _INDEX.md é AUTO-GERADO por `hb plan` e `hb report`. MUST NOT ser editado manualmente. Qualquer edição manual será sobrescrita na próxima execução.

R-AR-2) ARs com Status `✅ SUCESSO` são IMUTÁVEIS. O corpo da AR (conteúdo antes do `## Carimbo de Execução`) não pode ser alterado manualmente após a AR atingir este status. Apenas `hb report` pode appendar novos carimbos.

R-AR-3) O hook pre-commit BLOQUEIA commits onde:
  (a) Qualquer `AR_*.md` está staged sem `_INDEX.md` staged (E_AR_INDEX_NOT_STAGED).
  (b) Uma AR com `✅ SUCESSO` no HEAD teve seu corpo modificado (E_AR_IMMUTABLE).

R-AR-4) Status válidos de AR: `DRAFT` | `🏗️ EM_EXECUCAO` | `✅ SUCESSO` | `❌ FALHA`. Qualquer outro valor é inválido e pode causar falha no hb check.

R-AR-5) Toda AR MUST ser materializada via `hb plan` a partir de um Plan JSON válido em `docs/_canon/planos/`. Criação manual de arquivo AR_*.md é proibida (violação de governança).
```

(B) scripts/run/hb_cli.py:
- Linha com HB_PROTOCOL_VERSION: trocar '1.0.6' por '1.0.7'

NAO modificar nenhum outro arquivo além dos 2 listados acima.

## Critérios de Aceite
1) python scripts/run/hb_cli.py version retorna 'HB Track Protocol v1.0.7'. 2) docs/_canon/contratos/Dev Flow.md tem 'v1.0.7' no header (linha 1). 3) Dev Flow.md contém seção '## 9. Regras de Governança de ARs'. 4) Dev Flow.md contém as 5 regras R-AR-1 a R-AR-5. 5) HB_PROTOCOL_VERSION em hb_cli.py é '1.0.7'.

## Validation Command (Contrato)
```
python -c "import subprocess, pathlib; v=subprocess.run(['python','scripts/run/hb_cli.py','version'],capture_output=True,text=True,encoding='utf-8').stdout.strip(); assert 'v1.0.7' in v, f'FAIL: esperado v1.0.7, obtido: {v}'; df=pathlib.Path('docs/_canon/contratos/Dev Flow.md').read_text(encoding='utf-8'); assert 'v1.0.7' in df, 'FAIL: Dev Flow sem v1.0.7'; assert 'Regras de Governança de ARs' in df, 'FAIL: §9 ausente'; assert 'R-AR-5' in df, 'FAIL: regras incompletas (R-AR-5 ausente)'; print('PASS: Protocol v1.0.7 + Dev Flow §9 AR governance rules OK')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_013_gov_devflow_ar_rules.log`

## Riscos
- Após o bump para v1.0.7, novos Plan JSONs devem usar version: '1.0.7' — planos existentes com version: '1.0.6' falharão com E_PLAN_VERSION_MISMATCH se tentarem ser materializados novamente.
- Mudança em docs/_canon/contratos/Dev Flow.md §1 exige que scripts/run/hb_cli.py reporte a mesma versão — ambos devem ser atualizados no mesmo commit.
- Garantir que todas as ocorrências de 'v1.0.6' no Dev Flow.md sejam substituídas por 'v1.0.7' (incluindo §1, §4, §5, e qualquer referência inline).

## Análise de Impacto
_(A ser preenchido pelo Executor)_

---
## Carimbo de Execução
_(Gerado por hb report)_

