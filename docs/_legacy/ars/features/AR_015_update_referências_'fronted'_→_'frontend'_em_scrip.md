# AR_015 — Update referências 'Fronted' → 'Frontend' em scripts e docs canônicos

**Status**: 🔬 EM TESTE
**Versão do Protocolo**: 1.0.6

## Descrição
Atualizar todas as ocorrências do string path 'Hb Track - Fronted' nos arquivos fora do diretório renomeado.

Arquivos obrigatórios (canônicos/scripts):
  1. scripts/run/hb_cli.py — GOVERNED_ROOTS: substituir 'Hb Track - Fronted/' por 'Hb Track - Frontend/'
  2. scripts/plans/config.py — substituir quaisquer ocorrências de 'Fronted' por 'Frontend' em paths
  3. scripts/scripts_roadmap.yaml — substituir path references

Arquivos de documentação (atualizar se referenciarem o path como string literal):
  4. docs/_canon/contratos/Dev Flow.md
  5. docs/_canon/specs/Hb cli Spec.md
  6. docs/hbtrack/manuais/AxE.md

Regra: substituir SOMENTE o string 'Hb Track - Fronted' por 'Hb Track - Frontend' (incluindo variações sem espaços se existirem). NÃO alterar lógica, apenas o string de path.
NAO modificar arquivos dentro de 'Hb Track - Frontend/' (já movidos pelo git mv da task 014).

## Critérios de Aceite
1) grep -r 'Hb Track - Fronted' scripts/ retorna 0 ocorrências. 2) grep -r 'Hb Track - Fronted' docs/_canon/ retorna 0 ocorrências. 3) python scripts/run/hb_cli.py version retorna exit_code=0 (import ok). 4) GOVERNED_ROOTS em hb_cli.py contém 'Hb Track - Frontend/' (não 'Fronted').

## Validation Command (Contrato)
```
python -c "import subprocess, sys; r=subprocess.run(['grep','-r','Hb Track - Fronted','scripts/','docs/_canon/'],capture_output=True,text=True); hits=r.stdout.strip(); print('REMAINING REFS:\n'+hits) if hits else print('PASS: 0 references to Fronted in scripts/ and docs/_canon/')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_015_infra_rename_frontend_refs.log`

## Rollback Plan (Contrato)
```
git restore scripts/run/hb_cli.py scripts/plans/config.py scripts/scripts_roadmap.yaml docs/_canon/contratos/Dev Flow.md docs/_canon/specs/Hb cli Spec.md docs/hbtrack/manuais/AxE.md
```
⚠️ **ATENÇÃO**: Este AR modifica banco. Execute rollback em caso de falha.

## Riscos
- Substituição global de 'Fronted' pode afetar texto em português que não seja path (ex: 'frontend' em prosa). Usar 'Hb Track - Fronted' como string de busca exata para evitar falsos positivos.
- Se config.py usa o path em imports ou como constante, testar que o módulo ainda importa após a substituição.
- docs/hbtrack/PRD Hb Track.md e TRD Traing.md também referenciam o path — são documentos históricos; atualizar se necessário mas não são canônicos críticos.

## Análise de Impacto
_(Preenchido pelo Executor)_

**Arquivos Alvo (execução real desta AR):**
- `scripts/plans/config.py`
- `docs/_canon/planos/infra_001_rename_frontend_dir.json`
- `docs/hbtrack/manuais/AxE.md`

**Impacto Técnico:**
1. **Scripts de planos:** fallback de diretório frontend passa a apontar para `Hb Track - Frontend`.
2. **Docs canônicos (`docs/_canon/`):** remoção de ocorrências literais de `Hb Track - Fronted` para cumprir critério de aceite.
3. **Manual AxE:** alinhamento textual com o path correto do frontend.

**Impacto em SSOTs:**
- ❌ Não toca `docs/ssot/schema.sql`
- ❌ Não toca `docs/ssot/alembic_state.txt`
- ❌ Não toca `docs/ssot/openapi.json`

**Dependências:**
- ✅ AR_014 já concluída em `🔬 EM TESTE` (rename do diretório já efetivado no git index)

**Riscos Mitigados:**
- ✅ Substituição restrita ao literal exato `Hb Track - Fronted`
- ✅ Sem alteração de lógica de negócio
- ✅ Rollback disponível no contrato da AR

---
## Carimbo de Execução
_(Gerado por hb report)_



