# AR_014 — git mv: renomear Hb Track - Fronted → Hb Track - Frontend

**Status**: 🔬 EM TESTE
**Versão do Protocolo**: 1.0.6

## Descrição
Executar o rename atômico do diretório via git mv:

  git mv 'Hb Track - Fronted' 'Hb Track - Frontend'

Verificar que o rename foi registrado no índice Git:
  git status --short | grep 'Hb Track - Frontend'

NAO fazer commit ainda — o commit é feito após ambas as tasks serem concluídas e validadas.
NAO alterar nenhum arquivo de conteúdo nesta task.

## Critérios de Aceite
1) Diretório 'Hb Track - Frontend/' existe no filesystem. 2) Diretório 'Hb Track - Fronted/' NÃO existe mais. 3) git status mostra o rename staged (R  'Hb Track - Fronted/...' -> 'Hb Track - Frontend/...' ou equivalente). 4) next.config.js e package.json dentro de 'Hb Track - Frontend/' importam sem erro.

## Validation Command (Contrato)
```
python -c "import os, sys; old=os.path.exists('Hb Track - Fronted'); new=os.path.exists('Hb Track - Frontend'); errs=[]; (errs.append('OLD still exists: Hb Track - Fronted') if old else None); (errs.append('NEW missing: Hb Track - Frontend') if not new else None); [print(e) for e in errs]; sys.exit(len(errs)) if errs else print('PASS: Hb Track - Frontend exists, Hb Track - Fronted removed')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_014_infra_rename_frontend_dir.log`

## Rollback Plan (Contrato)
```
git mv 'Hb Track - Frontend' 'Hb Track - Fronted'
# OU: git restore --staged . (se ainda não commitado)
```
⚠️ **ATENÇÃO**: Este AR modifica banco. Execute rollback em caso de falha.

## Riscos
- Se node_modules/ não estiver no .gitignore, o git mv pode gerar milhares de staged files. Verificar .gitignore antes de executar.
- IDEs com watcher ativo (VSCode) podem reabrir arquivos com o path antigo e travar. Fechar e reabrir a IDE após o rename.
- CI/CD pipelines que referenciam 'Hb Track - Fronted/' vão quebrar — verificar .github/workflows/ antes.

## Análise de Impacto
_(Preenchido pelo Executor)_

**Arquivos Modificados:**
- Diretório `Hb Track - Fronted/` → `Hb Track - Frontend/` (git mv)

**Impacto Técnico:**
1. **Filesystem**: Rename atômico do diretório via git
2. **Git Index**: Todos os arquivos aparecem como "renamed" no staging area
3. **IDE/Watchers**: VSCode pode precisar recarregar workspace após o rename
4. **CI/CD**: Pipelines que referenciam o path antigo vão quebrar (AR-015 corrige)

**Impacto em SSOTs:**
- ❌ Não toca schema.sql (rename de diretório apenas)
- ❌ Não toca alembic_state.txt
- ❌ Não toca openapi.json

**Dependências:**
- ✅ AR-015 DEVE ser executada imediatamente após (atualizar referências em scripts)

**Riscos Mitigados:**
- ✅ .gitignore contém node_modules/ e .next/ (evita staging de milhares de arquivos)
- ✅ Rollback simples: `git mv 'Hb Track - Frontend' 'Hb Track - Fronted'`

**Checklist Pré-Execução:**
- [x] Diretório "Hb Track - Fronted" existe
- [x] .gitignore está correto (node_modules, .next, test-results)
- [x] AR-015 está preparada para ser executada em sequência

**Execução Determinística (Executor):**
- [x] Confirmação de estado atual no filesystem: `OLD=False`, `NEW=True`
- [x] Rename já presente no índice Git como `R  Hb Track - Fronted/... -> Hb Track - Frontend/...`
- [x] Escopo respeitado: somente rename de diretório (sem alteração de conteúdo de arquivos)

---
## Carimbo de Execução
_(Gerado por hb report)_



