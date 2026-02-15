# Troubleshooting — Guard & Parity (Models Pipeline)

| Propriedade | Valor |
|---|---|
| ID | CANON-TROUBLESHOOTING-GUARD-PARITY-009 |
| Status | CANÔNICO |
| Última verificação | 2026-02-10 (America/Sao_Paulo) |
| Porta de entrada | docs/_INDEX.yaml |
| Depende de | docs/_canon/05_MODELS_PIPELINE.md, docs/_canon/08_APPROVED_COMMANDS.md, docs/references/exit_codes.md |
| Objetivo | Diagnosticar e resolver problemas comuns de guard/parity/requirements |

---

## Como Usar Este Guia

1. **Identifique o exit code** do script que falhou
2. **Encontre a seção** correspondente abaixo
3. **Siga o diagnóstico** passo a passo
4. **Aplique a solução** recomendada
5. **Valide** com comando de verificação

**Se o problema persistir:** Documentar evidências e escalar para Tech Lead.

---

## Exit Code 2: Parity Structural Diffs

### Sintomas

```powershell
.\scripts\parity_gate.ps1 -Table "teams"
# Output:
# [FAIL] Parity check failed (exit=2)
# - modify_nullable(teams, 'name', existing_type, nullable=True → False)
$LASTEXITCODE  # 2
```

### Causa Raiz

A estrutura do model SQLAlchemy difere do schema PostgreSQL real. Possíveis causas:
- Migration pendente não aplicada
- Model alterado sem migration correspondente
- Schema PostgreSQL alterado manualmente (fora de Alembic)
- Drift entre branches (merge incorreto)

### Diagnóstico Passo a Passo

#### 1. Verificar parity_report.json

```powershell
cat "docs\_generated\parity_report.json" | jq '.diffs[] | select(.type=="structural")'
```

**O que procurar:**
- `modify_nullable`: Problema de NOT NULL ↔ nullable
- `modify_type`: Tipo de coluna incompatível
- `add_column` / `drop_column`: Coluna adicionada/removida
- `add_constraint` / `drop_constraint`: Constraint (FK, CHECK, UNIQUE) modificada

#### 2. Verificar estado do Alembic

```powershell
cd "Hb Track - Backend"
.\venv\Scripts\python.exe -m alembic current
```

**Output esperado:**
```
123abc456def (head)  # Indica que DB está na última migration
```

**Se diferente:**
```powershell
# Ver migrations pendentes
.\venv\Scripts\python.exe -m alembic history
```

#### 3. Comparar model com schema.sql

```powershell
# Verificar definição no schema.sql
Select-String -Path "docs\_generated\schema.sql" -Pattern "CREATE TABLE teams" -Context 0,30

# Verificar definição no model
cat "app\models\teams.py" | Select-String -Pattern "class Team" -Context 0,50
```

### Soluções

#### Solução A: Migration Pendente (DB está desatualizado)

**Quando usar:** `alembic current` mostra revisão anterior a `alembic history`.

```powershell
cd "Hb Track - Backend"
.\venv\Scripts\python.exe -m alembic upgrade head
# Validar
.\scripts\parity_gate.ps1 -Table "teams"
# Esperado: exit=0
```

#### Solução B: Model Incorreto (autogen necessário)

**Quando usar:** Mudança no model foi acidental ou está desalinhada com schema.sql.

```powershell
cd "Hb Track - Backend"
# Rodar autogen gate (corrige model automaticamente)
.\scripts\models_autogen_gate.ps1 -Table "teams" -Profile strict

# Validar
git diff app/models/teams.py  # Revisar mudanças
$LASTEXITCODE  # Esperado: 0
```

#### Solução C: Schema Manual Alterado (criar migration)

**Quando usar:** Schema PostgreSQL foi alterado fora do Alembic (DDL manual).

```powershell
cd "Hb Track - Backend"
# Criar migration que captura diferença
.\venv\Scripts\python.exe -m alembic revision --autogenerate -m "sync teams table with manual schema changes"

# Revisar migration gerada
code "db\alembic\versions\<novo_arquivo>.py"

# Aplicar
.\venv\Scripts\python.exe -m alembic upgrade head

# Validar
.\scripts\parity_gate.ps1 -Table "teams"
# Esperado: exit=0
```

#### Solução D: Reverter Model (mudança indesejada)

**Quando usar:** Mudança no model não deveria existir.

```powershell
cd "Hb Track - Backend"
# Reverter arquivo
git restore app/models/teams.py

# Validar
.\scripts\parity_gate.ps1 -Table "teams"
# Esperado: exit=0
```

### Validação

Após qualquer solução, executar:

```powershell
# 1. Parity deve passar
.\scripts\parity_gate.ps1 -Table "teams"
$LASTEXITCODE  # 0

# 2. Requirements deve passar
python scripts\model_requirements.py --table teams --profile strict
$LASTEXITCODE  # 0

# 3. Gate completo deve passar
.\scripts\models_autogen_gate.ps1 -Table "teams" -Profile strict
$LASTEXITCODE  # 0
```

### Referências

- **Exit Codes:** `docs/references/exit_codes.md` (seção Exit Code 2)
- **Scripts:**
  - `scripts/parity_gate.ps1` — Verifica parity (guard + alembic compare)
  - `scripts/parity_scan.ps1` — Apenas alembic compare (read-only)
  - `scripts/parity_classify.py` — Classifica diffs em structural/warning

---

## Exit Code 3: Guard Violations

### Sintomas

```powershell
.\scripts\models_autogen_gate.ps1 -Table "teams"
# Output:
# [FAIL] [GUARD] exited with code 3
# - Modified: app/routes/teams.py (not in allowlist)
$LASTEXITCODE  # 3
```

### Causa Raiz

Arquivo protegido foi modificado sem estar na allowlist (`-Allow` flag). O guard previne que correções de models "vazem" para outros arquivos (routes, tests, tasks).

### Diagnóstico Passo a Passo

#### 1. Identificar arquivo modificado

```powershell
git status --porcelain
# Output:
#  M app/models/teams.py      ← OK (intencional)
#  M app/routes/teams.py      ← Guard bloqueou (não estava em -Allow)
```

#### 2. Verificar baseline

```powershell
python scripts\agent_guard.py check --root . --baseline .hb_guard\baseline.json
```

**Output:**
```
[GUARD FAIL] Files modified without allowlist:
  - app/routes/teams.py (SHA256 changed)
```

#### 3. Determinar se mudança é legítima

**Perguntas:**
- A modificação em `app/routes/teams.py` é intencional?
- Foi causada por autogen (acidental)?
- É parte da correção ou efeito colateral?

### Soluções

#### Solução A: Modificação Legítima (adicionar ao allowlist)

**Quando usar:** Mudança em `app/routes/teams.py` é necessária para a correção.

```powershell
cd "Hb Track - Backend"
# Re-rodar gate com allowlist
.\scripts\models_autogen_gate.ps1 -Table "teams" -Allow "app/routes/teams.py"

# Validar
$LASTEXITCODE  # Esperado: 0 (se apenas guard falhava)
```

**Nota:** Allowlist é para **esta execução apenas**. Baseline não é atualizada automaticamente.

#### Solução B: Modificação Acidental (reverter)

**Quando usar:** Mudança foi efeito colateral indesejado (ex: autogen modificou imports).

```powershell
cd "Hb Track - Backend"
# Reverter arquivo
git restore app/routes/teams.py

# Re-rodar gate
.\scripts\models_autogen_gate.ps1 -Table "teams" -Profile strict

# Validar
$LASTEXITCODE  # Esperado: 0
```

#### Solução C: Baseline Desatualizada (atualizar)

**Quando usar:** Mudanças intencionais já foram revisadas e você quer novo baseline permanente.

**ATENÇÃO:** Requer autorização explícita ("AUTORIZADO: snapshot baseline").

```powershell
cd "Hb Track - Backend"
# 1. Confirmar repo limpo (exceto mudanças intencionais)
git status --porcelain
# Deve mostrar apenas arquivos revisados (ex: app/models/teams.py)

# 2. Snapshot baseline
python scripts\agent_guard.py snapshot --root . --out .hb_guard/baseline.json

# 3. Validar guard (baseline é local, nunca commitar)

```powershell
# Baseline é LOCAL (não fazer git add/commit)
git status --porcelain | Select-String -Pattern "baseline" 
# Esperado: blank (baseline.json nunca é versionado)

# Verificar conformidade local
python scripts\agent_guard.py check --root . --baseline .hb_guard\baseline.json
$LASTEXITCODE  # 0 = pass
```

# 2. Gate completo deve passar
.\scripts\models_autogen_gate.ps1 -Table "teams" -Profile strict
$LASTEXITCODE  # 0
```

### Referências

- **Exit Codes:** `docs/references/exit_codes.md` (seção Exit Code 3)
- **Scripts:**
  - `scripts/agent_guard.py` — Verifica/cria baseline
  - `scripts/models_autogen_gate.ps1` — Orquestrador (usa agent_guard internamente)
- **Comandos Aprovados:** `docs/_canon/08_APPROVED_COMMANDS.md` (seção Guard & Baseline)

---

## Exit Code 4: Requirements Violations

### Sintomas

```powershell
.\scripts\models_autogen_gate.ps1 -Table "attendance" -Profile strict
# Output:
# [FAIL] model_requirements strict profile violations (table=attendance)
#   - MISSING_SERVER_DEFAULT: is_medical_restriction expected_default=default_literal:false model_line=174
#   - TYPE_MISMATCH: date expected=date|None got=varchar|20 model_line=35
$LASTEXITCODE  # 4
```

### Causa Raiz

Model SQLAlchemy viola expectativas estruturais de `schema.sql` (SSOT). Diferente de parity (exit=2), requirements detecta problemas que Alembic pode não pegar (ex: server_default, tipos equivalentes mas não idênticos).

### Diagnóstico Passo a Passo

#### 1. Listar todas as violations

```powershell
python scripts\model_requirements.py --table attendance --profile strict
```

**Output típico:**
```
[FAIL] model_requirements strict profile violations (table=attendance)
  - MISSING_SERVER_DEFAULT: is_medical_restriction expected_default=default_literal:false model_line=174
  - TYPE_MISMATCH: date expected=date|None got=varchar|20 model_line=35
  - NULLABLE_MISMATCH: athlete_id expected=NOT NULL got=nullable=True model_line=52

Exit code: 4
```

#### 2. Verificar schema.sql (SSOT)

Para cada violation, consultar schema.sql:

```powershell
# Para MISSING_SERVER_DEFAULT
Select-String -Path "docs\_generated\schema.sql" -Pattern "is_medical_restriction" -Context 0,2

# Output esperado:
# is_medical_restriction boolean DEFAULT false NOT NULL,
```

```powershell
# Para TYPE_MISMATCH
Select-String -Path "docs\_generated\schema.sql" -Pattern "\\sdate\\s" -Context 0,2

# Output esperado:
# date date NOT NULL,
```

#### 3. Verificar model (linha específica)

```powershell
# Ver linha 174 (is_medical_restriction)
Get-Content "app\models\attendance.py" -TotalCount 174 | Select-Object -Last 1

# Ver linha 35 (date)
Get-Content "app\models\attendance.py" -TotalCount 35 | Select-Object -Last 1
```

### Soluções

#### Solução A: Autogen Corrige (maioria dos casos)

**Quando usar:** Violations são corrigíveis automaticamente por autogen.

```powershell
cd "Hb Track - Backend"
# Rodar gate com autogen
.\scripts\models_autogen_gate.ps1 -Table "attendance" -Profile strict

# Revisar mudanças
git diff app/models/attendance.py

# Validar
$LASTEXITCODE  # Esperado: 0
```

#### Solução B: Correção Manual (lógica custom)

**Quando usar:** Model tem lógica custom que autogen não deve sobrescrever.

**Exemplo: Corrigir MISSING_SERVER_DEFAULT**

```python
# ❌ ANTES (linha 174)
is_medical_restriction: Mapped[bool] = mapped_column(Boolean, nullable=False)

# ✅ DEPOIS
from sqlalchemy import text
is_medical_restriction: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))
```

**Exemplo: Corrigir TYPE_MISMATCH**

```python
# ❌ ANTES (linha 35)
date: Mapped[str] = mapped_column(String(20), nullable=False)

# ✅ DEPOIS
import datetime
date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
```

**Após correção manual:**

```powershell
# Validar
python scripts\model_requirements.py --table attendance --profile strict
$LASTEXITCODE  # Esperado: 0

# Gate completo
.\scripts\models_autogen_gate.ps1 -Table "attendance" -Profile strict
$LASTEXITCODE  # Esperado: 0
```

#### Solução C: Schema SQL Desatualizado (refresh SSOT)

**Quando usar:** schema.sql não reflete estado real do DB (migrations aplicadas mas SSOT não regenerado).

```powershell
cd "C:\HB TRACK"
# Refresh SSOT
powershell -NoProfile -ExecutionPolicy Bypass -File "scripts\inv.ps1" refresh

# Verificar mudanças
git diff "Hb Track - Backend\docs\_generated\schema.sql"

# Re-validar
cd "Hb Track - Backend"
python scripts\model_requirements.py --table attendance --profile strict
$LASTEXITCODE  # Esperado: 0 (se schema era o problema)
```

### Validação

```powershell
# 1. Requirements deve passar
python scripts\model_requirements.py --table attendance --profile strict
$LASTEXITCODE  # 0

# 2. Parity deve passar
.\scripts\parity_gate.ps1 -Table "attendance"
$LASTEXITCODE  # 0

# 3. Gate completo deve passar
.\scripts\models_autogen_gate.ps1 -Table "attendance" -Profile strict
$LASTEXITCODE  # 0
```

### Tipos de Violation (Quick Reference)

| Código | Significado | Fix Típico |
|--------|-------------|-----------|
| `MISSING_SERVER_DEFAULT` | Server default faltando | Adicionar `server_default=text("valor")` |
| `TYPE_MISMATCH` | Tipo PG ↔ SA incompatível | Corrigir tipo (ex: String → Date) |
| `NULLABLE_MISMATCH` | NOT NULL ↔ nullable incompatível | Adicionar `nullable=False` |
| `EXTRA_COLUMN` | Coluna no model não existe em schema | Remover coluna OU criar migration |
| `MISSING_COLUMN` | Coluna em schema falta no model | Adicionar coluna OU autogen |
| `MISSING_USE_ALTER` | FK de ciclo sem `use_alter=True` | Adicionar flag em ForeignKey |

### Referências

- **Exit Codes:** `docs/references/exit_codes.md` (seção Exit Code 4 com exemplos de fix)
- **Scripts:**
  - `scripts/model_requirements.py` — Validador estático (parser DDL + AST)
  - `scripts/models_autogen_gate.ps1` — Orquestrador (usa requirements internamente)
- **ADR:** `docs/ADR/013-ADR-MODELS.md` (critérios de validação detalhados)

---

## Exit Code 1: Internal Error / Crash

### Sintomas

```powershell
python scripts\model_requirements.py --table nonexistent
# Output:
# RuntimeError: CREATE TABLE for 'nonexistent' not found in schema.sql
$LASTEXITCODE  # 1
```

### Causa Raiz

Erro interno do script (não é falha de validação, é crash):
- Arquivo não encontrado (schema.sql, model.py)
- Erro de sintaxe Python
- Dependência faltando
- Problema de permissão

### Diagnóstico Passo a Passo

#### 1. Verificar stack trace completo

```powershell
# Re-rodar comando com output completo
python scripts\model_requirements.py --table <table> --profile strict 2>&1 | Out-File error.log
cat error.log
```

#### 2. Verificar pré-requisitos

```powershell
cd "Hb Track - Backend"

# Venv ativado?
Test-Path "venv\Scripts\python.exe"  # Deve ser True

# Dependências instaladas?
.\venv\Scripts\python.exe -m pip list | Select-String "sqlalchemy|alembic"

# Schema.sql existe?
Test-Path "docs\_generated\schema.sql"  # Deve ser True
```

#### 3. Verificar paths de arquivos

```powershell
# Model existe?
Test-Path "app\models\<table>.py"  # Deve ser True

# Schema.sql tem definição da tabela?
Select-String -Path "docs\_generated\schema.sql" -Pattern "CREATE TABLE <table>"
```

### Soluções

#### Solução A: Arquivo Faltando

```powershell
# Se schema.sql não existe: refresh SSOT
cd "C:\HB TRACK"
powershell -NoProfile -ExecutionPolicy Bypass -File "scripts\inv.ps1" refresh

# Se model não existe: tabela não tem model (esperado)
# Usar batch com -SkipGate para classificar como SKIP_NO_MODEL
cd "Hb Track - Backend"
.\scripts\models_batch.ps1 -SkipGate
```

#### Solução B: Dependência Faltando

```powershell
cd "Hb Track - Backend"
# Reinstalar dependências
.\venv\Scripts\python.exe -m pip install -r requirements.txt

# Validar
python scripts\model_requirements.py --table attendance --profile strict
```

#### Solução C: Erro de Sintaxe (bug no script)

**Quando usar:** Stack trace indica erro em scripts/*.py.

1. Revisar stack trace para identificar arquivo e linha
2. Abrir arquivo no editor
3. Corrigir sintaxe
4. Re-testar

**Se bug persiste:** Reportar para Tech Lead com evidências (stack trace completo + comando executado).

### Validação

```powershell
# Re-rodar comando original
python scripts\model_requirements.py --table <table> --profile strict
$LASTEXITCODE  # Esperado: 0 ou 4 (não 1)
```

### Referências

- **Exit Codes:** `docs/references/exit_codes.md` (seção Exit Code 1)

---

## Problemas Comuns (FAQ)

### Q1: parity_report.json mostra `table: null` e `column: null`

**Sintoma:**
```json
{
  "diffs": [
    { "type": "structural", "table": null, "column": null }
  ]
}
```

**Causa:** Bug crítico corrigido em 2026-02-10. `Tee-Object` do PowerShell 5.1 escrevia log Alembic em UTF-16LE, causando truncamento no parser Python.

**Diagnóstico:**
```powershell
# Verificar encoding do log
[System.IO.File]::ReadAllBytes("docs\_generated\parity-scan.log")[0..3]
# UTF-8 correto: 35 35 35 (### em ASCII)
# UTF-16LE problemático: FF FE (BOM) ou bytes 00 intercalados
```

**Solução:**
```powershell
# 1. Confirmar que parity_scan.ps1 usa WriteAllText (não Tee-Object)
Select-String -Path "scripts\parity_scan.ps1" -Pattern "WriteAllText"

# 2. Confirmar que parity_classify.py tem strip de NUL bytes
Select-String -Path "scripts\parity_classify.py" -Pattern "strip.*\\x00"

# 3. Se ainda problemático: re-gerar parity_scan.log
.\scripts\parity_scan.ps1 -TableFilter "attendance" -SkipDocsRegeneration
```

### Q2: $LASTEXITCODE está sempre 0 mesmo com falha

**Sintoma:**
```powershell
.\scripts\models_autogen_gate.ps1 -Table "teams"
# [FAIL] visível no output
$LASTEXITCODE  # 0 (deveria ser 2/3/4)
```

**Causa:** Pipeline (Tee-Object, Out-Null) entre execução e captura de `$LASTEXITCODE`.

**Diagnóstico:**
```powershell
# Revisar script que está chamando
cat "scripts\models_autogen_gate.ps1" | Select-String "Tee-Object|Out-Null"
```

**Solução:**
```powershell
# ❌ ERRADO
& comando | Tee-Object log.txt
$ec = $LASTEXITCODE  # Sempre 0

# ✅ CORRETO
$out = & comando 2>&1
$ec = $LASTEXITCODE  # Preserva exit code original
$out | Out-File log.txt
```

### Q3: Múltiplos exit codes possíveis, qual prevalece?

**Ordem de precedência no `models_autogen_gate.ps1`:**

1. **Exit 3** (guard) — verificado primeiro
2. **Exit 2** (parity) — verificado depois
3. **Exit 4** (requirements) — verificado por último
4. **Exit 0** — se todos passaram

**Exemplo:**
```powershell
# Se guard falha (exit=3):
# - Parity NÃO é executado
# - Requirements NÃO é executado
# - Exit final: 3

# Se guard passa mas parity falha (exit=2):
# - Requirements ainda é executado (para diagnóstico)
# - Exit final: 2 (parity prevalece sobre requirements)
```

### Q4: Batch retorna exit=0 mas vi FAIL no log

**Sintoma:**
```powershell
.\scripts\models_batch.ps1 -SkipGate
# Log mostra: FAIL: 3 tabelas
$LASTEXITCODE  # 0 (por quê?)
```

**Explicação:** `-SkipGate` (scan-only) sempre retorna 0. FAIL é **descoberta**, não falha de execução.

**Para obter exit != 0:**
```powershell
# Rodar sem -SkipGate (com fix)
.\scripts\models_batch.ps1
# Esperado: exit=2/3/4 na primeira tabela FAIL
```

### Q5: Repo sujo após execução do gate

**Sintoma:**
```powershell
.\scripts\models_autogen_gate.ps1 -Table "teams" -Profile strict
# Exit 0, mas:
git status --porcelain
# M  docs/_generated/schema.sql
# M  docs/_generated/manifest.json
```

**Causa:** Artefatos gerados (`docs/_generated/*`) são modificados como efeito colateral de refresh SSOT.

**Solução:** Limpar artefatos gerados (ver Prompt G em `docs/_ai/06_AGENT-PROMPTS.md`):

```powershell
git restore -- "docs/_generated/alembic_state.txt" "docs/_generated/manifest.json" "docs/_generated/parity_report.json" "docs/_generated/schema.sql" "docs/_generated/parity-scan.log"
git restore -- "..\docs/_generated/alembic_state.txt" "..\docs/_generated/manifest.json" "..\docs/_generated/schema.sql"

# Verificar
git status --porcelain
# Deve mostrar apenas mudanças intencionais (app/models/*.py)
```

---

## Escalação para Tech Lead

Se problema persiste após seguir todos os diagnósticos:

### Informações Obrigatórias para Escalação

1. **Comando exato executado** (copiar/colar)
2. **Exit code** (`$LASTEXITCODE`)
3. **Output completo** (últimas 200 linhas ou arquivo de log)
4. **git status --porcelain** (estado do working tree)
5. **Ambiente:**
   ```powershell
   $PSVersionTable.PSVersion
   python --version
   git --version
   ```
6. **Tentativas de resolução** (quais soluções foram aplicadas)

### Template de Reporte

```markdown
## Problema: [título curto]

**Comando:**
```powershell
<comando exato>
```

**Exit code:** `<código>`

**Output:**
```
<últimas 200 linhas>
```

**Git status:**
```
<output de git status --porcelain>
```

**Ambiente:**
- PowerShell: <versão>
- Python: <versão>
- Git: <versão>

**Tentativas de resolução:**
1. [Solução A aplicada] → Resultado: [falhou/parcial]
2. [Solução B aplicada] → Resultado: [falhou/parcial]

**Evidências adicionais:**
- [arquivos de log anexados]
- [screenshots se relevantes]
```

---

## Referências Cruzadas

### Documentos

| Documento | Path | Uso |
|-----------|------|-----|
| **Exit Codes (SSOT)** | `docs/references/exit_codes.md` | Detalhe de cada exit code com exemplos |
| **Comandos Aprovados** | `docs/_canon/08_APPROVED_COMMANDS.md` | Whitelist de comandos seguros |
| **Agent Prompts** | `docs/_ai/06_AGENT-PROMPTS.md` | Prompts prontos para corrigir problemas |
| **ADR Models** | `docs/ADR/013-ADR-MODELS.md` | Arquitetura do gate (3 camadas) |
| **Pipeline Models** | `docs/_canon/05_MODELS_PIPELINE.md` | Fluxo canônico SSOT → Requirements → Gate |

### Scripts

| Script | Path | Propósito |
|--------|------|-----------|
| **models_autogen_gate.ps1** | `scripts/models_autogen_gate.ps1` | Orquestrador (guard → parity → requirements) |
| **parity_gate.ps1** | `scripts/parity_gate.ps1` | Guard + parity scan |
| **parity_scan.ps1** | `scripts/parity_scan.ps1` | Apenas alembic compare (read-only) |
| **parity_classify.py** | `scripts/parity_classify.py` | Classifica diffs (structural/warning/comment) |
| **model_requirements.py** | `scripts/model_requirements.py` | Parser DDL + AST (validação estática) |
| **agent_guard.py** | `scripts/agent_guard.py` | Baseline snapshot/check |
| **models_batch.ps1** | `scripts/models_batch.ps1` | Batch runner (scan/fix em lote) |

---

---

## Exit Codes e Ações Corretivas (Playbook)

> **Versão machine-readable:** `docs/_canon/_machine/exit_code_playbook.yaml`
> **Registro completo de emitters:** `docs/_ai/_specs/exit_codes_registry.yaml`

Matriz prática: **exit code → causa provável → ação permitida → comando canônico → artefatos**.
Alinhada com o fluxo DB-first (SSOT = `schema.sql`) e com a regra "gate é juiz; agente só corrige até passar".

### Códigos do Pipeline Models (0–5)

#### Exit 0 — OK / PASS

| Campo | Valor |
|---|---|
| **Causa** | Operação concluída sem violations |
| **Ação** | Encerrar. Publicar artefatos (reports/logs). NÃO mexer em baseline |
| **Comando** | (nenhum — pipeline encerrado) |
| **Artefatos** | `parity_report.json`, `requirements_report` (se gerados) |

---

#### Exit 1 — INFRA / EXECUÇÃO INVÁLIDA

| Campo | Valor |
|---|---|
| **Causa** | Ambiente, dependências, comando, paths, crash interno |
| **Ação** | (a) Validar env (`.venv`, variáveis, DB/Redis). (b) Rerun UMA vez. (c) Se repetir, gerar diagnóstico mínimo (logs + versão ferramentas) e PARAR |
| **Comando validação** | `Test-Path "venv\Scripts\python.exe"` / `.\venv\Scripts\python.exe -m pip list \| Select-String "sqlalchemy\|alembic"` |
| **Regra** | NÃO "chutar" correções no código. Parar e escalar |
| **Artefatos** | Stack trace completo, `$PSVersionTable`, `python --version` |

---

#### Exit 2 — PARITY_ISSUE (Model ↔ DB diff estrutural)

| Campo | Valor |
|---|---|
| **Causa** | Estrutura do model SQLAlchemy difere do schema PostgreSQL |
| **Ação** | (a) Rodar autogen do(s) model(s) a partir de `schema.sql` (escopo mínimo: só tabelas que falharam). (b) Rodar normalizações permitidas (imports, TYPE_CHECKING, ordering, naming). (c) Reexecutar parity gate |
| **Comando fix** | `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\ops\infra\ops_models_autogen_gate.ps1 -Table <name> -Profile strict` |
| **Comando validação** | `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\ops\infra\ops_parity_gate.ps1 -Table <name>` |
| **Regra** | **NÃO editar schema.sql para "fazer bater"** (DB vence). Se persistir: abrir relatório de diff e corrigir gerador/normalizador, não o schema |
| **Artefatos** | `parity_report.json`, `git diff app/models/<table>.py` |

---

#### Exit 3 — GUARD_VIOLATION (violação de guardrail/política)

| Campo | Valor |
|---|---|
| **Causa** | Arquivo protegido modificado sem estar na allowlist. Baseline diverge |
| **Ação** | (a) Localizar regra violada no relatório. (b) Ajustar código para satisfazer a política. (c) Reexecutar |
| **Comando fix** | `git restore -- <arquivo_não_autorizado>` OU rerun com `-Allow "<path>"` |
| **Comando validação** | `python scripts\checks\db\check_agent_guard.py check --root . --baseline ".hb_guard\baseline.json"` |
| **Regra** | **Baseline snapshot MUST NOT acontecer por padrão.** Só atualizar com flag explícita (`-AllowBaselineSnapshot`) + registro de evidência (motivo + diff + commit) |
| **Artefatos** | Output do guard check, `git status --porcelain` |

---

#### Exit 4 — REQUIREMENTS_VIOLATION (regras/invariantes de requirements)

| Campo | Valor |
|---|---|
| **Causa** | Model viola expectativas estruturais de `schema.sql` (server_default, tipos, nullable, colunas extras/faltando) |
| **Ação** | (a) Abrir `requirements_report` (output ou JSON). (b) Aplicar correção mínima no nível correto (service/model/constraint). (c) Rerun requirements + gate |
| **Comando fix** | `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\ops\infra\ops_models_autogen_gate.ps1 -Table <name> -Profile strict` |
| **Comando validação** | `python scripts\checks\models\check_models_requirements.py --table <name> --profile strict` |
| **Regra** | Se a violação for causada por drift estrutural, voltar para EC 2 (parity) ou EC 5 (schema drift). **Não maquiar requirements** |
| **Artefatos** | Output do requirements, `git diff app/models/<table>.py` |

---

#### Exit 5 — SCHEMA_DRIFT (migrations aplicadas ≠ schema.sql / estado do banco)

| Campo | Valor |
|---|---|
| **Causa** | Migrations aplicadas não correspondem ao `schema.sql` versionado ou ao estado real do banco |
| **Ação** | (a) Aplicar migrations até head (ou reset controlado). (b) Regenerar `schema.sql` via comando canônico. (c) Commit do schema atualizado. (d) Rerun pipeline (parity + requirements) |
| **Comando fix** | `.\venv\Scripts\python.exe -m alembic upgrade head` → `powershell -NoProfile -ExecutionPolicy Bypass -File "C:\HB TRACK\scripts\inv.ps1" refresh` |
| **Comando validação** | `.\venv\Scripts\python.exe -m alembic current` + parity gate |
| **Regra** | Mudanças estruturais **MUST** entrar como migration; `schema.sql` é derivado |
| **Artefatos** | `alembic_state.txt`, `schema.sql` (diff), `parity_report.json` |

---

### Códigos Horizontais (Quality Gates — 10–20)

#### Exit 10 — LINT_FAIL (Ruff)

| Campo | Valor |
|---|---|
| **Causa** | Violações de lint (Ruff rules) |
| **Ação** | (a) `ruff check --fix` (escopo: arquivos alterados). (b) Rerun `ruff check` |
| **Regra** | Se fix automático piorar legibilidade/arquitetura, desabilitar rule pontual com justificativa local (inline `# noqa`) em vez de reformatar tudo |

#### Exit 11 — FORMAT_FAIL (Black)

| Campo | Valor |
|---|---|
| **Causa** | Código fora do padrão de formatação |
| **Ação** | (a) `black` no escopo do PR. (b) Rerun `black --check` |
| **Regra** | Formatação é mecânica; agente não deve discutir |

#### Exit 12 — TYPECHECK_FAIL (MyPy)

| Campo | Valor |
|---|---|
| **Causa** | Erro de tipos/annotations/imports |
| **Ação** | (a) Corrigir tipos/annotations/imports. (b) Preferir ajustes locais e Protocols. (c) Rerun `mypy` |
| **Regra** | Evitar `Any` indiscriminado; se precisar, isolar e justificar |

#### Exit 13 — SECURITY_FAIL (Bandit ou equivalente)

| Campo | Valor |
|---|---|
| **Causa** | Finding de segurança (parametrização, validação, secrets, hashing) |
| **Ação** | (a) Corrigir finding. (b) Rerun scanner |
| **Regra** | Silenciar finding SOMENTE com justificativa e se for falso positivo confirmado |

#### Exit 14 — COMPLEXITY_FAIL (Radon / CC > limite)

| Campo | Valor |
|---|---|
| **Causa** | Complexidade ciclomática acima do threshold |
| **Ação** | (a) Refatorar para reduzir caminhos (guard clauses, Strategy/Command, extração de funções). (b) Rerun radon |
| **Regra** | NÃO aumentar limite para "passar"; meta é manter orçamento de complexidade |

#### Exit 15 — TEST_FAIL (Pytest)

| Campo | Valor |
|---|---|
| **Causa** | Testes falhando |
| **Ação** | (a) Rodar só testes falhos com output detalhado (`pytest <path> -x -vv`). (b) Corrigir bug ou teste (o que estiver errado). (c) Rerun suite do escopo |
| **Regra** | Se bug é de drift estrutural, voltar para EC 2/5 — não remendar teste para "acompanhar bug" |

#### Exit 16 — COVERAGE_FAIL (abaixo do piso)

| Campo | Valor |
|---|---|
| **Causa** | Cobertura abaixo do threshold mínimo |
| **Ação** | (a) Adicionar testes unitários nos pontos tocados. (b) Priorizar regras de negócio. (c) Rerun coverage |
| **Regra** | NÃO omitir arquivo para ganhar cobertura, exceto itens genuinamente gerados/infra com regra explícita |

#### Exit 20 — CONTRACT_DRIFT (OpenAPI/contrato fora do esperado)

| Campo | Valor |
|---|---|
| **Causa** | Contrato OpenAPI difere do esperado (handlers/schemas) |
| **Ação** | (a) Regenerar OpenAPI a partir do app ou ajustar handlers/schemas. (b) Rerun testes de contrato. (c) Garantir compatibilidade com DB-first (DB continua vencendo) |
| **Regra** | Contrato é derivado do app; app é derivado do DB. Cadeia: `DB → Model → Service → Router → OpenAPI` |

---

## Convenção Operacional do Agente (Fix Loop)

> **Machine-readable:** `docs/_canon/_machine/exit_code_playbook.yaml` → campo `fix_loop`

### Regra Central

Para **qualquer exit code ≠ 0**, o agente executa no máximo **3 iterações** do ciclo:

```
fix → rerun gate → check exit code
```

### Fluxo

```
┌─────────────────────────────────┐
│  Executar gate/check            │
│  Capturar $LASTEXITCODE         │
└──────────┬──────────────────────┘
           │
     ┌─────▼─────┐
     │ EC == 0 ?  │──yes──▶ DONE (publicar artefatos, não mexer baseline)
     └─────┬──────┘
           │ no
     ┌─────▼──────────────┐
     │ iteração > 3 ?     │──yes──▶ STOP (não convergiu — escalar)
     └─────┬──────────────┘
           │ no
     ┌─────▼──────────────────────────────────────────────┐
     │ Consultar Playbook (seção EC correspondente)       │
     │ Aplicar ação corretiva MÍNIMA                      │
     │ Registrar: arquivo tocado, diff, exit code prévio  │
     └─────┬──────────────────────────────────────────────┘
           │
           └──────▶ (voltar ao topo: rerun gate)
```

### Condições de Parada

| Condição | Ação |
|---|---|
| Exit code 0 | Encerrar com sucesso |
| 3 iterações sem convergir | STOP. Devolver evidências e escalar |
| Exit code 1 (crash/infra) | STOP imediato. Não iterar (sem fix possível via código) |
| Fix geraria efeito fora do escopo | STOP. Reportar escopo expandido e pedir autorização |

### Evidências Obrigatórias ao Parar (STOP)

Ao parar (convergência ou não), o agente MUST devolver:

1. **Exit code** final (`$LASTEXITCODE`)
2. **Arquivos tocados** (`git status --porcelain`)
3. **Diff summary** (`git diff --stat`)
4. **Relatórios gerados** (parity_report.json, requirements output, logs)
5. **Hipótese de causa** (1–2 frases)
6. **Número de iterações** executadas

### Política de Baseline

- Snapshot baseline MUST NOT acontecer automaticamente
- Requer flag explícita (`-AllowBaselineSnapshot`) + autorização do usuário
- Registro obrigatório: motivo + diff + commit hash
- Baseline NUNCA é versionado (`.hb_guard/baseline.json` está em `.gitignore`)

---

## Referências Cruzadas

### Documentos

| Documento | Path | Uso |
|-----------|------|-----|
| **Exit Codes Registry (SSOT)** | `docs/_ai/_specs/exit_codes_registry.yaml` | Registro completo de exit codes + emitters |
| **Playbook Machine-Readable** | `docs/_canon/_machine/exit_code_playbook.yaml` | Versão YAML do playbook (agente consome) |
| **Exit Codes (Referência MD)** | `docs/references/exit_codes.md` | Detalhe de cada exit code com exemplos |
| **Comandos Aprovados (SSOT)** | `docs/_ai/_specs/approved_commands_registry.yaml` | Whitelist/blacklist de comandos |
| **Comandos Aprovados (MD)** | `docs/_canon/08_APPROVED_COMMANDS.md` | Referência humana de comandos |
| **Agent Prompts** | `docs/_ai/06_AGENT-PROMPTS.md` | Prompts prontos para corrigir problemas |
| **ADR Models** | `docs/ADR/013-ADR-MODELS.md` | Arquitetura do gate (3 camadas) |
| **Pipeline Models** | `docs/_canon/05_MODELS_PIPELINE.md` | Fluxo canônico SSOT → Requirements → Gate |

### Scripts

| Script | Path | Propósito |
|--------|------|-----------|
| **models_autogen_gate** | `scripts/ops/infra/ops_models_autogen_gate.ps1` | Orquestrador (guard → parity → requirements) |
| **parity_gate** | `scripts/ops/infra/ops_parity_gate.ps1` | Guard + parity scan |
| **parity_scan** | `scripts/ops/db/ops_parity_scan.ps1` | Apenas alembic compare (read-only) |
| **model_requirements** | `scripts/checks/models/check_models_requirements.py` | Parser DDL + AST (validação estática) |
| **agent_guard** | `scripts/checks/db/check_agent_guard.py` | Baseline snapshot/check |
| **models_batch** | `scripts/ops/infra/ops_models_batch.ps1` | Batch runner (scan/fix em lote) |
| **inv (refresh)** | `scripts/ops/ops_inv.ps1` | Wrapper SSOT refresh (schema.sql, openapi.json, etc.) |

---

**Última atualização:** 2026-02-15
**Responsável:** Tech Lead + AI Assistant
**Versão:** 2.0 (adicionado Playbook exit codes + Fix Loop convention)
