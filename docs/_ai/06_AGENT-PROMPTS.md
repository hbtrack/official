# Agent Prompts — Models Pipeline (Canônico)

| Propriedade | Valor |
|---|---|
| ID | CANON-AGENT-PROMPTS-MODELS-006 |
| Status | CANÔNICO |
| Última verificação | 2026-02-10 (America/Sao_Paulo) |
| Porta de entrada | docs/_canon/00_START_HERE.md |
| Depende de | docs/_canon/05_MODELS_PIPELINE.md, docs/_canon/08_APPROVED_COMMANDS.md, docs/references/exit_codes.md |
| Objetivo | Prompts prontos para agentes executarem validação/correção de models sem sair do escopo |

---

## Regras Globais (Todos os Prompts)

### Pré-requisitos Obrigatórios

1. **CWD:** Sempre iniciar em `C:\HB TRACK\Hb Track - Backend`
   ```powershell
   Set-Location "C:\HB TRACK\Hb Track - Backend"
   ```

2. **Repo Limpo:** Antes de qualquer execução
   ```powershell
   git status --porcelain
   # Esperado: vazio (nenhum output)
   # Se houver output: ABORTAR e reportar estado
   ```

3. **Captura de Exit Code:** Imediatamente após comando (sem pipeline)
   ```powershell
   # ✅ CORRETO
   $output = & comando 2>&1
   $exitCode = $LASTEXITCODE

   # ❌ ERRADO (Tee-Object altera $LASTEXITCODE)
   comando 2>&1 | Tee-Object -FilePath log.txt
   $exitCode = $LASTEXITCODE
   ```

### Políticas de Execução

4. **Stop-on-First-Failure:** Qualquer exit != 0 → parar e trazer evidência
5. **Sem Temporários no Repo:** Logs devem ir para `$env:TEMP`, nunca tracked
6. **Sem Auto-Baseline:** Não atualizar baseline sem autorização explícita
7. **Sem Auto-Commit:** Commits exigem aprovação do usuário

### Evidências Obrigatórias em Falha

Quando exit != 0, sempre coletar:
- Comando exato executado
- `$LASTEXITCODE` capturado
- Últimas ~120 linhas do output/log
- `git status --porcelain` (estado do working tree)

---

## Prompt A — Varredura em Lote (Batch Scan)

**Quando usar:** Descobrir rapidamente quais tabelas estão PASS/FAIL sem fazer correções.

**O que o agent faz:**
- Roda batch em modo dry-run (scan-only)
- Se houver falha, para e cola evidência
- Não roda snapshot baseline

**Prompt para colar:**

```
Execute o pipeline canônico de varredura em lote (SSOT auto + scan-only), seguindo regras de stop-on-first-failure.

1. Set-Location "C:\HB TRACK\Hb Track - Backend"
2. Verifique repo limpo: git status --porcelain (se não vazio, ABORTAR)
3. Rode: .\scripts\models_batch.ps1 -SkipGate -SkipRefresh
4. Capture $LASTEXITCODE imediatamente
5. Se exit != 0: pare e cole:
   - últimas ~120 linhas do log em %TEMP%\hb_models_batch_*.log
   - git status --porcelain
   - comando executado + exit code

Não atualize baseline. Não crie arquivos no repo.
```

**Output esperado (sucesso):**
```
Scan completo:
  PASS: 10 tabelas
  FAIL: 3 tabelas (athletes, teams, seasons)
  SKIP_NO_MODEL: 2 tabelas

CSV gerado: %TEMP%\models_batch_20260210_143201.csv
Exit code: 0
```

---

## Prompt B — Corrigir UMA Tabela (Manual Gate)

**Quando usar:** Você sabe qual tabela falhou (exit=4/2/3) e quer corrigir especificamente ela.

**O que o agent faz:**
- Roda gate completo para tabela específica
- Para na primeira falha
- Não commita automaticamente

**Prompt para colar:**

```
Corrija a tabela "<TABLE>" usando o pipeline canônico, sem sair do escopo.
Regras: stop na primeira falha, sem temporários no repo, sem snapshot baseline.

Passos:
1. Set-Location "C:\HB TRACK\Hb Track - Backend"
2. git status --porcelain (deve estar vazio; senão ABORTAR)
3. Rode inv.ps1 refresh UMA VEZ:
   powershell -NoProfile -ExecutionPolicy Bypass -File "C:\HB TRACK\scripts\inv.ps1" refresh
   capture $LASTEXITCODE (se !=0 ABORTAR)
4. Rode gate:
   .\scripts\models_autogen_gate.ps1 -Table "<TABLE>" -Profile strict
   capture $LASTEXITCODE imediatamente
5. Se exit=0: mostre "✅ PASS" e rode git status --porcelain (não commitar)
6. Se exit != 0: pare e cole:
   - output completo do gate (últimas ~120 linhas)
   - git status --porcelain
   - exit code final
```

**Substituir:**
- `<TABLE>`: Nome da tabela (ex: `athletes`, `teams`)

**Perfis disponíveis:**
- `strict`: Validação completa (padrão)
- `fk`: Permite SAWarnings de ciclos FK (teams/seasons)

---

## Prompt C — Somente Detectar Violations (Requirements Direto)

**Quando usar:** Evidência rápida de violations sem rodar autogen/parity.

**O que o agent faz:**
- Executa apenas `model_requirements.py` (read-only)
- Reporta violations encontradas
- Não faz correções

**Prompt para colar:**

```
Execute requirements direto para a tabela "<TABLE>" e reporte PASS/FAIL.

1. Set-Location "C:\HB TRACK\Hb Track - Backend"
2. git status --porcelain (se não vazio, ABORTAR)
3. Rode:
   & "venv\Scripts\python.exe" scripts\model_requirements.py --table "<TABLE>" --profile strict
4. Capture $LASTEXITCODE imediatamente
5. Se exit=4: pare e cole violations (últimas ~80 linhas) + caminho do report gerado
   Não rode gate. Não rode baseline.
```

**Substituir:**
- `<TABLE>`: Nome da tabela

**Output esperado (FAIL):**
```
[FAIL] model_requirements strict profile violations (table=attendance)
  - MISSING_SERVER_DEFAULT: is_medical_restriction expected_default=default_literal:false model_line=174
  - TYPE_MISMATCH: date expected=date|None got=varchar|20 model_line=35

Exit code: 4
```

---

## Prompt D — Baseline Snapshot (Somente com Autorização)

**Quando usar:** Mudanças intencionais já revisadas e você quer atualizar baseline para o novo estado.

**ATENÇÃO:** Exige que usuário diga **"AUTORIZADO: snapshot baseline"** explicitamente.

**Prompt para colar:**

```
AUTORIZADO: snapshot baseline.
Condições: repo limpo, sem temporários, sem artefatos gerados pendentes.

1. Set-Location "C:\HB TRACK\Hb Track - Backend"
2. git status --porcelain (deve estar vazio; senão ABORTAR)
3. Rode snapshot:
   & "venv\Scripts\python.exe" scripts\agent_guard.py snapshot `
     --root "." `
     --out ".hb_guard/baseline.json" `
     --exclude "venv,.venv,**pycache**,.pytest_cache,docs_generated"
4. Capture $LASTEXITCODE (se !=0 ABORTAR)
5. Mostre git status --porcelain (deve mostrar baseline.json modificado)
6. NÃO commitar a menos que o usuário diga "AUTORIZADO: commitar baseline"
```

**Pré-requisito:** Usuário deve ter autorizado explicitamente com a frase acima.

---

## Prompt E — Commit Limpo (Sem Artefatos Gerados)

**Quando usar:** Após gate PASS e você quer commitar mudanças intencionais (models) sem incluir gerados.

**O que o agent faz:**
- Restaura artefatos gerados (`docs/_generated/*`)
- Adiciona apenas arquivos intencionais
- Cria commit com mensagem estruturada

**Prompt para colar:**

```
Prepare um commit limpo para a mudança em "<ARQUIVOS_INTENCIONAIS>".

1. Set-Location "C:\HB TRACK\Hb Track - Backend"
2. Rode git status --porcelain e liste tudo
3. Reverta artefatos gerados:
   git restore -- "docs/_generated/alembic_state.txt" "docs/_generated/manifest.json" "docs/_generated/parity_report.json" "docs/_generated/schema.sql" "docs/_generated/parity-scan.log"
   git restore -- "..\docs/_generated/alembic_state.txt" "..\docs/_generated/manifest.json" "..\docs/_generated/schema.sql" "..\docs/_generated/trd_training_permissions_report.txt"
4. Rode git status --porcelain novamente e confirme que só restaram arquivos intencionais
5. git add apenas os arquivos intencionais (listar explicitamente)
6. git commit -m "<tipo(escopo): mensagem>"
   Exemplo: "fix(models): correct attendance nullable fields via autogen"
7. Mostre git log -1 --stat

Se hooks falharem por ambiente, use --no-verify e registre isso no PR.
```

**Substituir:**
- `<ARQUIVOS_INTENCIONAIS>`: Ex: `app/models/attendance.py, app/models/teams.py`
- `<tipo(escopo): mensagem>`: Mensagem de commit semântico

**Tipos de commit:**
- `fix`: Correção de bug/violation
- `feat`: Nova funcionalidade
- `refactor`: Refatoração sem mudança de comportamento
- `docs`: Mudanças de documentação

---

## Prompt F — PR via gh CLI (Terminal + Merge com Autorização)

**Quando usar:** Você já commitou e quer abrir PR. Só merge quando usuário autorizar.

**O que o agent faz:**
- Push do branch
- Cria PR via `gh`
- Abre PR no navegador
- **NÃO** faz merge automaticamente

**Prompt para colar:**

```
Abra um PR via terminal para o branch atual.

1. Set-Location "C:\HB TRACK\Hb Track - Backend"
2. git status --porcelain (deve estar vazio; senão ABORTAR)
3. git push -u origin HEAD
4. gh pr create --base main --head HEAD --fill
5. gh pr view --web

NÃO faça merge automaticamente.
Só faça merge quando o usuário responder: "AUTORIZADO: merge".
```

**Pós-ação:** Aguardar aprovação do usuário antes de `gh pr merge`.

---

## Prompt G — Limpeza Pós-Run (Artefatos Gerados)

**Quando usar:** Depois de rodar gate/batch e o working tree ficou com `docs/_generated/*` modificados.

**O que o agent faz:**
- Restaura apenas artefatos gerados
- Preserva mudanças intencionais (models)
- Não commita nada

**Prompt para colar:**

```
Limpe apenas artefatos gerados (sem perder mudanças intencionais).

1. Set-Location "C:\HB TRACK\Hb Track - Backend"
2. git status --porcelain (listar tudo)
3. Execute:
   git restore -- "docs/_generated/alembic_state.txt" "docs/_generated/manifest.json" "docs/_generated/parity_report.json" "docs/_generated/schema.sql" "docs/_generated/parity-scan.log"
   git restore -- "..\docs/_generated/alembic_state.txt" "..\docs/_generated/manifest.json" "..\docs/_generated/schema.sql" "..\docs/_generated/trd_training_permissions_report.txt"
4. git status --porcelain (confirmar limpeza — só devem restar arquivos intencionais)

Não commitar nada automaticamente.
```

---

## Prompt H — Fail-Fast Macro (Reforço de Política)

**Quando usar:** Reforçar que o agent deve parar no primeiro erro em qualquer etapa.

**Frase para anexar a qualquer prompt:**

```
[FAIL-FAST] Se qualquer comando retornar exit code != 0, pare imediatamente e cole:
- Comando exato
- $LASTEXITCODE
- Últimas ~120 linhas do output/log
- git status --porcelain

Não tente variações. Não rode snapshot baseline. Não crie arquivos no repo.
```

---

## Comandos Aprovados (Quick Reference)

Todos os comandos abaixo estão na whitelist de `docs/_canon/08_APPROVED_COMMANDS.md`:

**Read-Only (sempre permitido):**
```powershell
git status --porcelain
git diff <file>
python scripts\model_requirements.py --table <name> --profile strict
.\scripts\models_batch.ps1 -SkipGate  # scan-only
.\scripts\parity_scan.ps1 -TableFilter <name> -SkipDocsRegeneration
```

**Execução com Gates (permitido via validação):**
```powershell
.\scripts\models_autogen_gate.ps1 -Table <name> -Profile strict
.\scripts\parity_gate.ps1 -Table <name>
```

**Requer Aprovação Explícita:**
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "C:\HB TRACK\scripts\inv.ps1" refresh
python scripts\agent_guard.py snapshot --root . --out .hb_guard/baseline.json
git add <file>
git commit -m "msg"
git push
```

**Proibido (nunca executar):**
```powershell
git reset --hard   # ❌ Destrutivo
git clean -f       # ❌ Destrutivo
Invoke-Expression  # ❌ Risco de injeção
```

---

## Fluxo de Trabalho Típico (Exemplo)

**Cenário:** Corrigir 3 tabelas com FAIL

```
1. Usuário: Execute Prompt A (varredura)
   → Agent: FAIL detectado em: athletes, teams, seasons

2. Usuário: Execute Prompt B para "athletes"
   → Agent: Gate PASS (exit=0), mudanças em app/models/athlete.py

3. Usuário: Execute Prompt E para commitar (athlete.py)
   → Agent: Commit criado com mensagem "fix(models): correct athlete nullable fields"

4. Repetir steps 2-3 para "teams" e "seasons"

5. Usuário: Execute Prompt F para abrir PR
   → Agent: PR criado, URL exibido, aguardando "AUTORIZADO: merge"

6. Usuário (após CI passar): "AUTORIZADO: merge"
   → Agent: gh pr merge --auto --squash
```

---

## Troubleshooting de Prompts

### Problema: Agent ignorou exit code != 0 e continuou

**Solução:** Adicionar Prompt H (fail-fast macro) ao final de qualquer prompt.

### Problema: $LASTEXITCODE está sempre 0 mesmo com falha

**Solução:** Verificar se há pipeline (Tee-Object, Out-Null) entre comando e captura.
```powershell
# ❌ ERRADO
comando | Tee-Object log.txt
$ec = $LASTEXITCODE  # Sempre 0

# ✅ CORRETO
$out = comando 2>&1
$ec = $LASTEXITCODE
$out | Out-File log.txt
```

### Problema: Repo sujo após execução

**Solução:** Executar Prompt G (limpeza de artefatos gerados).

---

## Referências

- **Comandos Aprovados:** `docs/_canon/08_APPROVED_COMMANDS.md`
- **Exit Codes:** `docs/references/exit_codes.md`
- **Troubleshooting:** `docs/_canon/09_TROUBLESHOOTING_GUARD_PARITY.md`
- **Pipeline Canônico:** `docs/_canon/05_MODELS_PIPELINE.md`
- **ADR:** `docs/ADR/013-ADR-MODELS.md` (Gate Model↔DB)

**Última atualização:** 2026-02-10
**Responsável:** Tech Lead + AI Assistant
