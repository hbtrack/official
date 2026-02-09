# ENFORCEMENT (MANDATORY)

Fontes obrigatórias (ler e seguir):
- `C:\HB TRACK\docs\_ai\_INDEX.md`
- `C:\HB TRACK\docs\_ai\SYSTEM_DESIGN.md` (seguir as diretrizes de design de sistema para decisões arquiteturais)

**Antes de criar qualquer migration ou model**
- Consulte as regras de integridade (RDB) na Seção 8.3 do `C:\HB TRACK\docs\Hb Track\PRD_HB_TRACK.md`

**Autoridade / Artefatos canônicos:**
- `Hb Track - Backend/docs/_generated/openapi.json (contrato FastAPI)`
- `Hb Track - Backend/docs/_generated/schema.sql (DDL + COMMENT ON COLUMN)`
- `Hb Track - Backend/docs/_generated/alembic_state.txt (estado de migrações)`

# .clinerules — Windows + VS Code + PowerShell (HB Track)

# 0) Shell obrigatório
- Use EXCLUSIVAMENTE PowerShell no Windows.
- NÃO use bash, sh, zsh, git-bash, WSL, cmd.exe, ou comandos POSIX (ls, cat, grep, sed, awk, find, xargs).
- Se precisar de "grep": use Select-String.
- Se precisar de "cat": use Get-Content.
- Se precisar de "find files": use Get-ChildItem.

# .clinerules — HB Track — Windows — PowerShell 5.1 — Repo: C:\HB TRACK

# SHELL / AMBIENTE (OBRIGATÓRIO)
- Você está em Windows com PowerShell 5.1. Use EXCLUSIVAMENTE powershell.exe.
- NÃO use pwsh, bash, sh, zsh, git-bash, WSL, cmd.exe, ou comandos POSIX (ls, cat, grep, sed, awk, find, xargs).

# DIRETÓRIO DE TRABALHO (OBRIGATÓRIO)
- Antes de qualquer comando, garantir que o diretório atual é o root do repo:
  Set-Location "C:\HB TRACK"

# FORMA CANÔNICA DE EXECUTAR QUALQUER COMANDO
- Todo comando DEVE ser executado como UMA linha via wrapper:
  powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "& { Set-Location 'C:\HB TRACK'; <COMANDO> }"
- Não execute comandos “crus” sem esse wrapper.

# QUOTING / PATHS (PARA NÃO QUEBRAR)
- Todo path com espaço deve estar entre aspas duplas: "C:\HB TRACK\..."
- Para executar um script .ps1: SEMPRE use call operator:
  & "C:\HB TRACK\scripts\algum.ps1" <args>
- Nunca use ./script.ps1
- Escape aspas internas com backtick: `"

# Ao final de cada tarefa (OBRIGATORIO):
- Atualizar o `CHANGELOG.md` (C:\HB TRACK\docs\adr\architecture\CHANGELOG.md), registrando a data, descrição da mudança, e impacto no sistema.

Blueprint (modelos estruturado) do `CHANGELOG.md` abaixo:
# Changelog - HB Track
Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]
### Adicionado
* **Módulo Training**: Implementação da base do banco de exercícios de handebol.
* **Segurança**: Implementação do Gate de Validação (ADR-MODELS-001) para integridade Model ↔ DB.
* **Abas**: Estruturação das rotas de Agenda, Planejamento e Exercícios no PRD/TRD.

### Corrigido
* **Terminal**: Ajuste na execução de scripts Python para evitar erros de aspas no PowerShell.
* **Models**: Correção de Foreign Keys cíclicas entre `teams` e `seasons`.

---

## [0.1.0] - 2024-02-08
### Adicionado
* Estrutura inicial do projeto com FastAPI e PostgreSQL.
* Configuração do Alembic para migrações.
* Documentação de Baseline (PRD/TRD/Invariants).

- Atualizar o `EXECUTIONLOG.md` (C:\HB TRACK\docs\adr\architecture\EXECUTIONLOG.md), registrando detalhes de execução, resultados dos gates, e lições aprendidas.

Blueprint (modelos estruturado) do `EXECUTIONLOG.md` abaixo:
# Execution Log - HB Track
Registro técnico de execuções, auditorias e sessões de trabalho do Agent.

| Data/Hora | Task ID | Ação/Comando | Status | Observação |
| :--- | :--- | :--- | :--- | :--- |
| 2024-02-08 14:30 | `T-101` | `verify_models_gate.py --table exercises` | ✅ PASS | Validação estrutural ok. |
| 2024-02-08 14:35 | `T-102` | `models_autogen_gate.ps1 -Table tags` | ❌ FAIL | Erro de aspas no PS (Resolvido). |
| 2024-02-08 15:00 | `T-103` | `alembic upgrade head` | ✅ PASS | Migração de favoritos aplicada. |

---

### Detalhes de Falhas Relevantes
#### Task T-102 (14:35)
* **Erro**: `The string is missing the terminator: '`.
* **Causa**: Cline tentou injetar código multi-linha via `powershell -Command`.
* **Solução**: Mudança para estratégia `write_to_file` + `python script.py`.

# COMANDOS PROIBIDOS (QUEBRAM NO PS OU CAUSAM LOOP)
- Proibido: &&, || (encadeamento estilo bash), export, set -e, $(...), 2>/dev/null, heredoc, pipes com utilitários POSIX.
- Proibido: ls/cat/grep/sed/awk/find/xargs.
- Use equivalentes PowerShell:
  - grep -> Select-String
  - cat  -> Get-Content
  - find -> Get-ChildItem -Recurse

# POLÍTICA DE FALHA (ANTI-SPAM DE COMANDOS)
- Se um comando falhar por sintaxe do shell (ParserError, Unexpected token, The term is not recognized):
  PARE. NÃO tente outras variações.
  Corrija quoting/wrapper e execute 1 tentativa por vez.
- Se o mesmo erro ocorrer 2 vezes, parar e explicar o bloqueio com evidência.

# SEGURANÇA (SEM DESTRUIÇÃO)
- Proibido executar sem autorização explícita:
  Remove-Item (recursivo), del, rmdir, git clean, git reset --hard, dropdb, docker system prune/prune -a.
- Antes de qualquer ação destrutiva: mostrar preview:
  git status --porcelain
  git diff --name-only "origin/main...HEAD"
  e pedir confirmação.

# GIT (SEM POSIX)
- Use comandos git sem pipes POSIX:
  git status --porcelain
  git diff --name-only "origin/main...HEAD"
  git log -n 1 --oneline

# PYTHON / VENV (PREFERENCIAL)
- Preferir sempre a venv do backend quando existir:
  & "C:\HB TRACK\Hb Track - Backend\venv\Scripts\python.exe" <args>
- Se a venv não existir, usar python e reportar a limitação.

# PADRÃO DE EVIDÊNCIA (OBRIGATÓRIO)
- Após rodar qualquer gate/script, sempre registrar:
  - comando completo
  - trecho relevante do output
  - $LASTEXITCODE
- Se houver relatório JSON, ler via:
  Get-Content "<path>" -Raw | ConvertFrom-Json

# EXECUÇÃO INCREMENTAL (ANTI-LOOP)
- Não rodar mais de 1 comando de build/gate por tentativa.
- Após cada comando: registrar output + $LASTEXITCODE + próximo passo único.

# POWERHELL 5.1: EVITAR FEATURES DO PS7
- Não usar operadores/recursos típicos do PS7 (ex.: ??, ?:, ForEach-Object -Parallel).
- Manter compatibilidade com PS 5.1.

# POWERSHELL EXEC_TASK WRAPPER (OBRIGATÓRIO)
- Todos os comandos do EXEC_TASK devem ser executados pelo wrapper canônico:
  powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "& { Set-Location 'C:\HB TRACK'; <COMANDO> }"
- Justificativa: garante working directory consistente e evita contaminação de profile

**Alternativa Aprovada: Invoke-External Pattern**
- O pattern de models_autogen_gate.ps1 (linhas 17-32) usa Push-Location/Pop-Location + call operator &
- Exemplo válido:
  ```powershell
  Push-Location "C:\HB TRACK"
  try {
      & $comando @args
      $exitCode = $LASTEXITCODE
  } finally {
      Pop-Location
  }
  ```
- Ambos patterns são aceitos; preferir wrapper canônico para novos scripts isolados.

# VENV VALIDATION (OBRIGATÓRIA)
- Antes de executar python/pip no EXEC_TASK, validar que venv existe e é funcional:
  ```powershell
  $venvPy = "C:\HB TRACK\Hb Track - Backend\venv\Scripts\python.exe"
  if (-not (Test-Path $venvPy -PathType Leaf)) { 
      Write-Error "Venv não encontrado em $venvPy. Abortar EXEC_TASK."
      exit 1 
  }
  ```
- PROIBIDO: executar `pip list | Select-String` com python global (fora do venv/repo)
- Se venv não existir: agent deve reportar no pré-requisito e ABORTAR, nunca tentar "consertar" automaticamente
- Justificativa: evita corrompimento de ambiente global; força isolamento de dependências

# INVOKE-EXPRESSION: PROIBIDO
- `Invoke-Expression` e `iex` são PROIBIDOS quando houver alternativa (99% dos casos)
- Razão: quebra de quoting com paths/espaços em PowerShell 5.1; risco de segurança

**Alternativa Obrigatória: Call Operator com Array de Args**
```powershell
# ❌ PROIBIDO (anti-pattern)
$cmd = "python 'Hb Track - Backend\scripts\algo.py' --arg 'valor com espaços'"
Invoke-Expression $cmd

# ✅ CORRETO (usar sempre)
$args = @("Hb Track - Backend\scripts\algo.py", "--arg", "valor com espaços")
& python $args
```

**IMPORTANTE: Paths Corretos dos Scripts**
- Scripts Python do backend: `Hb Track - Backend\scripts\*.py`
- Scripts PowerShell do backend: `Hb Track - Backend\scripts\*.ps1`
- Sempre usar caminho completo a partir do repo root (`C:\HB TRACK\`)

**Exemplo Real:**
```powershell
$venvPy = "C:\HB TRACK\Hb Track - Backend\venv\Scripts\python.exe"
& $venvPy "Hb Track - Backend\scripts\model_requirements.py" --table attendance
```

**Caso Específico: EXEC_TASK linha 376**
- Path correto: `"Hb Track - Backend\scripts\model_requirements.py"`
- Implementar como: `& $venvPy @requirementsArgs`

# EXEC_TASK PREREQUISITES VALIDATION (OBRIGATÓRIA)
Antes de executar qualquer EXEC_TASK (ex: EXEC_TASK_ADR_MODELS_001.md), rodar checklist obrigatória:

```powershell
# CHECK 1: PowerShell versão 5.1
if ($PSVersionTable.PSVersion.Major -ne 5) {
    Write-Error "PowerShell 5.1 obrigatório. Versão atual: $($PSVersionTable.PSVersion)"
    exit 1
}

# CHECK 2: Venv válido
$venvPy = "C:\HB TRACK\Hb Track - Backend\venv\Scripts\python.exe"
if (-not (Test-Path $venvPy -PathType Leaf)) {
    Write-Error "Venv não encontrado. Executar setup antes."
    exit 1
}

# CHECK 3: Python versão 3.11+
$pyVersion = & $venvPy --version 2>&1
if ($pyVersion -notmatch "Python 3\.1[1-9]") {
    Write-Error "Python 3.11+ obrigatório. Versão: $pyVersion"
    exit 1
}

# CHECK 4: Dependências instaladas
$pipList = & $venvPy -m pip list 2>&1
if ($pipList -notmatch "sqlalchemy" -or $pipList -notmatch "alembic") {
    Write-Error "Dependências faltando (sqlalchemy/alembic). Rodar pip install."
    exit 1
}

# CHECK 5: Baseline existe
if (-not (Test-Path "C:\HB TRACK\Hb Track - Backend\.hb_guard\baseline.json")) {
    Write-Error "Baseline não encontrado. Executar pré-requisito do EXEC_TASK."
    exit 1
}

# CHECK 6: Schema.sql atual (age < 1 dia ou commit recente)
$schemaPath = "C:\HB TRACK\Hb Track - Backend\docs\_generated\schema.sql"
if (-not (Test-Path $schemaPath)) {
    Write-Error "schema.sql não encontrado. Gerar docs antes."
    exit 1
}
$schemaAge = (Get-Date) - (Get-Item $schemaPath).LastWriteTime
if ($schemaAge.TotalHours -gt 24) {
    Write-Warning "schema.sql desatualizado (age: $($schemaAge.TotalHours)h). Considerar regenerar."
}
```

**Política de Falha:**
- Se QUALQUER check falhar: ABORTAR EXEC_TASK imediatamente
- Reportar qual pré-requisito falhou com evidência específica
- NÃO tentar "consertar" automaticamente (risco de quebrar ambiente)
- Justificativa: reduz 70% de erros por ambiente errado; fail-fast com diagnóstico claro

# EXIT CODE VALIDATION PATTERN (OBRIGATÓRIO)
- Após cada comando externo, capturar e validar $LASTEXITCODE antes de prosseguir

**Semântica de Exit Codes do EXEC_TASK:**
- `0`: PASS (conformidade total)
- `2`: Parity structural diffs (tabela difere de schema.sql)
- `3`: Guard violations (arquivo ML/API/test modificado sem autorização)
- `4`: Requirements violations (model viola regras de negócio/validação)
- `1`: Internal crash (erro de execução do próprio script)

**Pattern Obrigatório:**
```powershell
& $comando @args
$exitCode = $LASTEXITCODE

if ($exitCode -ne 0) {
    Write-Host "[FAIL] Comando falhou com código $exitCode" -ForegroundColor Red
    
    # Interpretar código específico (quando aplicável)
    switch ($exitCode) {
        2 { Write-Host "  → Parity: estrutura difere do schema.sql" -ForegroundColor Yellow }
        3 { Write-Host "  → Guard: arquivo protegido foi modificado" -ForegroundColor Yellow }
        4 { Write-Host "  → Requirements: model viola regras de validação" -ForegroundColor Yellow }
        default { Write-Host "  → Erro genérico ou crash interno" -ForegroundColor Yellow }
    }
    
    # Propagar código específico (NÃO flatten para 1)
    exit $exitCode
}

Write-Host "[SUCCESS] Comando executado com sucesso" -ForegroundColor Green
```

**Anti-Pattern (NÃO fazer):**
```powershell
# ❌ ERRADO: perde informação diagnóstica
if ($LASTEXITCODE -ne 0) {
    exit 1  # Flatten todos erros para 1
}
```

**Referência de Implementação Correta:**
- Ver models_autogen_gate.ps1 linhas 186-188 (já implementado corretamente)
- C:\HB TRACK\docs\_ai\EXEC_TASK_ADR_MODELS_001.md Phase 3 pode estar baseada em versão antiga do código


