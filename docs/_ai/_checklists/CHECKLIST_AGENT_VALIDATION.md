# CHECKLIST_AGENT_VALIDATION.md

## Descrição
Checklist durante execução: validar que agent está operando dentro de guardrails, não violando constraints, e produzindo output esperado.

---

## Durante Execução

### Exit Code Validation
- [ ] Cada comando retorna exit code esperado
  ```powershell
  $LASTEXITCODE  # capture imediatamente
  ```
- [ ] Não há flutuações de exit code (0→1→0→1 é sinal de instabilidade)
- [ ] Se exit != esperado:
  - [ ] Parar execução
  - [ ] Revisar output (últimas 50 linhas)
  - [ ] Verificar git status
  - [ ] Reportar antes de retry

### Output/Logs Validation
- [ ] Nenhum stack trace exposto (se sim, investigate)
- [ ] Nenhuma PII/secrets em logs
- [ ] Nenhuma mensagem ambígua (ex: "done" sem contexto)
- [ ] URLs não hardcoded
- [ ] Paths escritos usando variáveis (não absolutos quando possível)

### Git State Validation (antes de cada write)
- [ ] `git status --porcelain` revisado
- [ ] Apenas arquivos esperados estão dirty
- [ ] Nenhum arquivo de SSOT está sujo acidentalmente
  ```powershell
  git status --short | sls "schema.sql|openapi.json|baseline"  # expect nothing
  ```
- [ ] `.hb_guard/baseline.json` NÃO aparece em `git status`

### Model/Database Validation (após gates)
- [ ] `parity_report.json` existe e é válido JSON
- [ ] No DIFFs aparecem (exit=0)
- [ ] Model.py não foi completamente reescrito (sanity check: file size)
- [ ] Nenhum arquivo temporário deixado no repo

### Checkpoint Validation (a cada 5 min de execução)
- [ ] Agent ainda está responsivo (não travado)
- [ ] CPU/memory dentro do esperado (não memory leak)
- [ ] Disk space sufficient (se gera artifacts)
- [ ] Network connectivity OK (se faz calls)

---

## Critério de Parada (Early Exit)

### Parar Imediatamente Se...
- ❌ Exit code != esperado por 2+ tentativas
- ❌ Git estado corrompido (detached HEAD, unmerged paths)
- ❌ Baseline.json commitado acidentalmente
- ❌ Schema.sql/openapi.json sujo inexpectedly
- ❌ Agent não response por > 30 seg
- ❌ Disk space crítico (< 1 GB)

### Ação: Antes de Retry
1. `git status --porcelain` + salvar output
2. `get-process | where CPU > 80` (verificar recursos)
3. Se Git corrompido: contate humano (não tente repair auto)
4. Se recurso limitado: cleanup + retry
5. Se agent travado: kill processo + restart

---

## Pós-Execução Validation

### Commit Validation (antes de git add/commit)
- [ ] `git diff --stat` revisado (quantas linhas adicionadas/removidas)
- [ ] `.hb_guard/baseline.json` NÃO aparece em mudanças
- [ ] Arquivos non-expected não foram modificados
- [ ] Commit message é descritivo (ex: "fix(models): MAJOR#2 baseline pre-check")

### SSOT Artifacts Validation
- [ ] Schema.sql atualizado recentemente (age < 24h)
- [ ] OpenAPI JSON válido (pode fazer parse?)
- [ ] Parity report tem data/time (recente)
- [ ] Nenhum artefato foi deletado

### Logs/Output Validation
- [ ] Output log salvo (se aplicável)
- [ ] Nenhuma linha truncada (se muito longo)
- [ ] Timestamps são sequenciais (não retroativo)

---

## Checklist Consolidado (Single Pass)

```
PRÉ-EXEC:    ✓ Env ✓ Repo ✓ Scripts ✓ Baseline ✓ Docs
DURANTE:     ✓ ExitCode ✓ Output ✓ GitState ✓ Models ✓ Checkpoint
PÓS-EXEC:    ✓ Commit ✓ SSOT ✓ Logs
SUCESSO?     ✓ ALL checks passed → proceed or finish
ERRO?        ❌ Qualquer falha → STOP + investigate + report
```

---

## TODO
- [ ] Criar automated validation script (todas essas checks)
- [ ] Adicionar alerting para desvios
- [ ] Documentar recovery path para cada failure mode
