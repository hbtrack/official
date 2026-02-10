--- 
description: Executar ADR-MODELS-003 — implementar batch runner determinístico para varredura e correção de models (SSOT → requirements → gate) com fail-fast e repo hygiene
# applyTo: 'Hb Track - Backend/scripts/models_batch.ps1'
---

Você é o agente Copilot trabalhando no repo HB Track. Siga estritamente o escopo abaixo e pare no primeiro erro.

OBJETIVO
Implementar/atualizar o script: Hb Track - Backend/scripts/models_batch.ps1 conforme ADR-MODELS-003:
- Refresh SSOT 1x (inv.ps1 refresh) quando permitido
- Extrair tabelas automaticamente do SSOT docs/_generated/schema.sql
- Rodar requirements em lote e classificar PASS/FAIL/SKIP_NO_MODEL
- Rodar models_autogen_gate.ps1 apenas nas FAIL, 1 por vez
- Fail-fast: parar imediatamente no primeiro erro real (exit != 0) em qualquer etapa
- Repo hygiene: nunca criar arquivos temporários no repo; logs e CSV devem ir para %TEMP%
- Capturar $LASTEXITCODE imediatamente após cada comando (sem pipeline que altere o valor)
- SKIP_NO_MODEL deve ser detectado via Test-Path do arquivo app/models/<table>.py (não por texto)
- Usar código interno 100 para SKIP_NO_MODEL (não usar 2/3/4)

PREPARAÇÃO (LEITURA OBRIGATÓRIA)
Leia e siga:
1) docs/_canon/00_START_HERE.md
2) docs/_canon/01_AUTHORITY_SSOT.md
3) docs/_canon/05_MODELS_PIPELINE.md
4) docs/references/exit_codes.md
5) scripts/models_autogen_gate.ps1, scripts/model_requirements.py, scripts/agent_guard.py

REGRAS
- Não criar/modificar outros arquivos além de scripts/models_batch.ps1 (exceto se estritamente necessário e justificado).
- Não atualizar baseline automaticamente. Apenas implementar flag -AllowBaselineSnapshot que executa snapshot mas NÃO commita.
- Não alterar modelos, não rodar “fixes” nos models nesta tarefa.
- Não rodar comandos “tentando até dar certo”: se um comando falhar, pare e reporte o erro com o comando e saída.

ENTREGÁVEIS
1) scripts/models_batch.ps1 implementado com funções:
   Abort, Ensure-BackendRoot, Ensure-CleanRepo, Run-RefreshSSOT, Load-TablesFromSSOT, Load-TablesManual,
   Get-ProfileForTable, Restore-GeneratedArtifacts (sem engolir erro), Run-Requirements (Test-Path + 100),
   Run-Gate (captura exitcode segura), Maybe-SnapshotBaseline (somente com flag)
2) Parâmetros:
   -AutoTables FromSSOT/None, -ExcludeTables, -Tables, -TablesFile, -DefaultProfile strict/fk/lenient,
   -SkipRefresh, -SkipGate, -NoFailFast (failfast ON por default), -AllowBaselineSnapshot
3) Logs e CSV em %TEMP%: hb_models_batch_<timestamp>.log / .csv

TESTES (OBRIGATÓRIOS)
Após implementar, rode e cole os outputs:
A) git status --porcelain (deve estar vazio)
B) .\scripts\models_batch.ps1 -SkipGate -SkipRefresh (deve sair 0 e gerar CSV/LOG)
C) Confirmar que ao menos uma tabela sem model aparece como SKIP_NO_MODEL no CSV

PARE IMEDIATAMENTE se qualquer teste falhar e reporte:
- comando
- exit code
- últimas 30 linhas do output

```