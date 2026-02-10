````md
# docs/_canon/06_AGENT_PROMPTS_MODELS.md

| Propriedade | Valor |
|---|---|
| ID | CANON-AGENT-PROMPTS-MODELS-006 |
| Status | CANÔNICO |
| Última verificação | 2026-02-09 (America/Sao_Paulo) |
| Porta de entrada | docs/_canon/00_START_HERE.md |
| Depende de | docs/_canon/05_MODELS_PIPELINE.md, docs/references/exit_codes.md |
| Objetivo | Prompts prontos para detecção/correção de models sem sair do escopo |

## Regras globais para qualquer prompt deste arquivo

1) CWD obrigatório:
```powershell
Set-Location "C:\HB TRACK\Hb Track - Backend"
````

2. Antes de qualquer execução:

```powershell
git status --porcelain
# esperado: vazio; se não estiver, ABORTAR
```

3. Capturar `$LASTEXITCODE` imediatamente após o comando (sem pipeline, sem Select-Object).
4. Stop-on-first-failure: qualquer exit != 0 => parar e trazer evidência.
5. Proibido criar arquivos temporários/backups dentro do repo.
6. Proibido atualizar baseline sem autorização explícita.
7. Logs (quando necessários) devem ir para `$env:TEMP`, nunca para o repo.

---

## Prompt A — Varredura em lote (SSOT auto) + resumo PASS/FAIL

**Quando usar:** você quer saber rapidamente quais tabelas estão OK/FAIL sem editar nada manualmente.

**O que o agent deve fazer:**

* Rodar batch em modo padrão (SSOT auto).
* Se houver falha, parar e colar evidência.
* Não rodar snapshot baseline.

**Prompt para colar no chat do agent:**

Execute o pipeline canônico de varredura/correção em lote (SSOT auto), seguindo as regras de stop-on-first-failure.

1. Set-Location "C:\HB TRACK\Hb Track - Backend"
2. Verifique repo limpo: git status --porcelain (se não estiver vazio, ABORTAR).
3. Rode: .\scripts\models_batch.ps1
4. Capture $LASTEXITCODE imediatamente.
5. Se exit != 0: pare e cole:

   * últimas ~120 linhas do log em %TEMP%\hb_models_batch_*.log
   * git status --porcelain
   * comando executado + exit code
     Não atualize baseline. Não crie arquivos no repo.

---

## Prompt B — Corrigir UMA tabela (manual) e parar na primeira falha

**Quando usar:** você já sabe qual tabela falhou (exit=4/2/3) e quer corrigir só ela.

**Prompt:**

Corrija a tabela "<TABLE>" usando o pipeline canônico, sem sair do escopo.
Regras: stop na primeira falha, sem temporários no repo, sem snapshot baseline.
Passos:

1. Set-Location "C:\HB TRACK\Hb Track - Backend"
2. git status --porcelain (deve estar vazio; senão ABORTAR)
3. Rode inv.ps1 refresh uma vez:
   powershell -NoProfile -ExecutionPolicy Bypass -File "C:\HB TRACK\scripts\inv.ps1" refresh
   capture $LASTEXITCODE (se !=0 ABORTAR)
4. Rode gate:
   .\scripts\models_autogen_gate.ps1 -Table "<TABLE>" -Profile strict
   capture $LASTEXITCODE imediatamente
5. Se exit=0: mostre "PASS" e então rode:
   git status --porcelain
   (não commitar automaticamente)
6. Se exit != 0: pare e cole:

   * output completo do gate (últimas ~120 linhas)
   * git status --porcelain
   * exit code final

---

## Prompt C — Somente DETECTAR violations (requirements direto)

**Quando usar:** você quer evidência rápida do requirements sem rodar autogen/parity.

**Prompt:**

Execute requirements direto para a tabela "<TABLE>" e reporte PASS/FAIL.

1. Set-Location "C:\HB TRACK\Hb Track - Backend"
2. git status --porcelain (se não estiver vazio, ABORTAR)
3. Rode:
   & "venv\Scripts\python.exe" scripts\model_requirements.py --table "<TABLE>" --profile strict
4. Capture $LASTEXITCODE imediatamente.
5. Se exit=4: pare e cole as violations (últimas ~80 linhas) + caminho do report gerado.
   Não rode gate, não rode baseline.

---

## Prompt D — Baseline snapshot (somente com autorização)

**Quando usar:** mudanças intencionais já revisadas e você quer atualizar baseline para o novo estado.

**PROMPT (exige que o usuário diga “AUTORIZADO: snapshot baseline”)**

AUTORIZADO: snapshot baseline.
Condições: repo limpo, sem temporários e sem artefatos gerados.

1. Set-Location "C:\HB TRACK\Hb Track - Backend"
2. git status --porcelain (deve estar vazio; senão ABORTAR)
3. Rode snapshot:
   & "venv\Scripts\python.exe" scripts\agent_guard.py snapshot `  --root "."`
   --out ".hb_guard/baseline.json" `
   --exclude "venv,.venv,**pycache**,.pytest_cache,docs_generated"
4. Capture $LASTEXITCODE (se !=0 ABORTAR)
5. Mostre git status --porcelain (deve mostrar baseline.json modificado)
6. NÃO commitar a menos que o usuário diga “AUTORIZADO: commitar baseline”.

---

## Prompt E — Commit por intenção (sem sujar repo)

**Quando usar:** após gate PASS e você quer commitar mudanças intencionais (models) sem incluir gerados.

**Prompt:**

Prepare um commit limpo para a mudança em "<ARQUIVOS INTENCIONAIS>".

1. Set-Location "C:\HB TRACK\Hb Track - Backend"
2. Rode git status --porcelain e liste tudo.
3. Reverta artefatos gerados:
   git restore -- "docs/_generated/alembic_state.txt" "docs/_generated/manifest.json" "docs/_generated/parity_report.json" "docs/_generated/schema.sql"
   git restore -- "..\docs/_generated/alembic_state.txt" "..\docs/_generated/manifest.json" "..\docs/_generated/schema.sql" "..\docs/_generated/trd_training_permissions_report.txt"
4. Rode git status --porcelain novamente e confirme que só restaram arquivos intencionais.
5. git add apenas os arquivos intencionais
6. git commit -m "<tipo(escopo): mensagem>"
7. Mostre git log -1 --stat

Se hooks falharem por ambiente, use --no-verify e registre isso no PR.

---

## Prompt F — PR via gh (terminal) + merge só com autorização

**Quando usar:** você já commitou e quer PR. Só merge quando o usuário autorizar.

**Prompt:**

Abra um PR via terminal para o branch atual.

1. Set-Location "C:\HB TRACK\Hb Track - Backend"
2. git status --porcelain (deve estar vazio; senão ABORTAR)
3. git push -u origin HEAD
4. gh pr create --base main --head HEAD --fill
5. gh pr view --web

NÃO faça merge automaticamente.
Só faça merge quando o usuário responder: "AUTORIZADO: merge".

---

## Prompt G — Limpeza pós-run (quando docs/_generated sujam o working tree)

**Quando usar:** depois de rodar gate/batch e o working tree ficou com docs/_generated modificados.

**Prompt:**

Limpe apenas artefatos gerados (sem perder mudanças intencionais).

1. Set-Location "C:\HB TRACK\Hb Track - Backend"
2. git status --porcelain (listar)
3. Execute:
   git restore -- "docs/_generated/alembic_state.txt" "docs/_generated/manifest.json" "docs/_generated/parity_report.json" "docs/_generated/schema.sql"
   git restore -- "..\docs/_generated/alembic_state.txt" "..\docs/_generated/manifest.json" "..\docs/_generated/schema.sql" "..\docs/_generated/trd_training_permissions_report.txt"
4. git status --porcelain (confirmar limpeza)
   Não commitar nada automaticamente.

---

## Prompt H — “Parar imediatamente se falhar” (macro)

**Quando usar:** você quer reforçar que o agent deve parar no primeiro erro em qualquer etapa.

**Frase para anexar a qualquer prompt:**
Se qualquer comando retornar exit code != 0, pare imediatamente e cole:

* comando exato
* $LASTEXITCODE
* últimas ~120 linhas do output/log
* git status --porcelain
  Não tente variações. Não rode snapshot baseline. Não crie arquivos no repo.

```

