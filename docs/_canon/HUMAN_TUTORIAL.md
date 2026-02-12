# Tutorial para Desenvolvedores Humanos

**Versão:** 2.0  
**Data:** 2026-02-12  
**Público:** Desenvolvedores humanos trabalhando com HB Track

---

## 📋 Pré-requisitos

Antes de começar, certifique-se de que você tem:

1. **PowerShell 5.1+** (Windows) ou PowerShell Core 7+
2. **Python 3.9+** com venv configurado
3. **Git 2.30+**
4. **Docker** e **Docker Compose** (para PostgreSQL local)
5. **Acesso ao repositório:** `https://github.com/Davisermenho/Hb_Track`

**Validação de ambiente:**  
Arquivo de validação: `IMPLEMENTATION_SUMMARY.md` (linhas 187-196)

```powershell
# Verificar versões
pwsh --version          # PowerShell
python --version        # Python 3.9+
git --version          # Git
docker --version       # Docker
```

---

## 🚀 Setup Inicial

### 1. Clone e Configure o Ambiente

```powershell
# Clone o repositório
git clone https://github.com/Davisermenho/Hb_Track.git
cd Hb_Track

# Entre no diretório backend
cd "Hb Track - Backend"

# Crie e ative o ambiente virtual Python
python -m venv venv
.\venv\Scripts\Activate.ps1

# Instale dependências
pip install -r requirements.txt
pip install PyYAML>=6.0.1 radon
```

**Evidência:** `scripts/_ia/utils/yaml_loader.py` (linha 17) requer PyYAML 6.0.1+

### 2. Inicie o PostgreSQL

```powershell
# No diretório raiz do projeto
cd "C:\HB TRACK"
docker-compose up -d postgres
```

**Comando aprovado:** `docs/_ai/_context/approved-commands.yml` (linhas 308-326)

### 3. Verifique que o Working Directory está correto

```powershell
# Sempre valide antes de executar scripts
$expectedPath = "Hb Track - Backend"
$currentPath = Get-Location
if ($currentPath -notmatch [regex]::Escape($expectedPath)) {
    Write-Host "[ERROR] Wrong CWD. Expected: *$expectedPath, Got: $currentPath" -ForegroundColor Red
    exit 1
}
```

**Evidência:** `docs/_ai/_context/approved-commands.yml` (linhas 6-9)

---

## 🎯 Comandos Canônicos (PowerShell)

### Categoria 1: Inspeção de Estado (Read-Only)

#### 1.1 Verificar estado do repositório Git

```powershell
# Ver arquivos modificados (formato curto)
git status --porcelain

# Ver diferenças em arquivo específico
git diff app/models/athletes.py

# Ver histórico recente de commits
git log --oneline -n 5

# Ver detalhes de um commit específico
git show 09cdbeb
```

**Evidências:**
- `docs/_ai/_context/approved-commands.yml` (linhas 29-82)
- Saída esperada em `approved-commands.yml` (linhas 30-36, 42-46, 52-62, 68-82)

#### 1.2 Verificar baseline do Agent Guard

```powershell
# Verificar se arquivos protegidos foram modificados
.\venv\Scripts\python.exe scripts\agent_guard.py check baseline
# Exit code 0: nenhum arquivo protegido modificado
# Exit code 3: violação detectada (ver troubleshooting)
```

**Evidências:**
- `scripts/_ia/generators/generate-handshake-template.py` output referencia `agent_guard.py`
- `docs/_ai/_context/approved-commands.yml` (linhas 253-265)

---

### Categoria 2: Validação de Invariantes

#### 2.1 Executar gate individual

```powershell
# Wrapper unificado (RECOMENDADO)
.\scripts\inv.ps1 gate INV-TRAIN-015

# Ou diretamente
.\scripts\run_invariant_gate.ps1 INV-TRAIN-015
```

**Evidências:**
- `scripts/inv.ps1` (linhas 1-11, 39-60)
- `scripts/run_invariant_gate.ps1` (linhas 1-23)

**Exit codes:**
- **0:** PASS (todas as validações ok)
- **1:** CRASH (erro interno)
- **2:** PARITY FAIL (divergência estrutural)
- **3:** GUARD FAIL (arquivo protegido modificado)
- **4:** REQUIREMENTS FAIL (violação de restrições)

**Referência completa:** `docs/_ai/_maps/troubleshooting-map.json` (linhas 4-65)

#### 2.2 Executar validação de todos os gates

```powershell
# Executar gate all
.\scripts\inv.ps1 all

# Dry-run (apenas scan, sem aplicar correções)
.\scripts\inv.ps1 drift
```

**Evidência:** `scripts/inv.ps1` (linhas 63-78)

---

### Categoria 3: SSOT e Regeneração de Artefatos

#### 3.1 Regenerar artefatos canônicos

```powershell
# Regenera schema.sql, openapi.json, alembic_state.txt, manifest.json
.\scripts\inv.ps1 refresh
```

**Evidência:**
- `scripts/inv.ps1` menciona comando `refresh`
- `docs/_ai/_context/approved-commands.yml` (linhas 202-233)

#### 3.2 Extrair comandos aprovados para YAML

```powershell
# Converte docs/_canon/08_APPROVED_COMMANDS.md → approved-commands.yml
.\venv\Scripts\python.exe scripts\_ia\extractors\extract-approved-commands.py
```

**Evidência:** `scripts/_ia/extractors/extract-approved-commands.py` (linhas 1-73)

**Output esperado:**
```
✅ Extracted 5 categories to docs/_ai/_context/approved-commands.yml
ExitCode: 0
```

**Validação:** `IMPLEMENTATION_SUMMARY.md` (linhas 198-201)

#### 3.3 Extrair troubleshooting map

```powershell
# Converte docs/_canon/09_TROUBLESHOOTING_GUARD_PARITY.md → troubleshooting-map.json
.\venv\Scripts\python.exe scripts\_ia\extractors\extract-troubleshooting.py
```

**Evidência:** `scripts/_ia/extractors/extract-troubleshooting.py` referenciado em `IMPLEMENTATION_SUMMARY.md` (linhas 56-65)

**Output esperado:**
```
✅ Extracted troubleshooting for 4 exit codes to docs/_ai/_maps/troubleshooting-map.json
ExitCode: 0
```

**Validação:** `IMPLEMENTATION_SUMMARY.md` (linhas 203-205)

---

### Categoria 4: Models Pipeline (Autogen/Parity/Requirements)

#### 4.1 Gate individual de model com autogen

```powershell
# Executar gate com correção automática
.\scripts\models_autogen_gate.ps1 -Table "athletes" -Profile strict

# Com permissão para warnings de ciclo (FK circular)
.\scripts\models_autogen_gate.ps1 -Table "athletes" -Profile fk -AllowCycleWarning
```

**Evidência:** `docs/_ai/_context/approved-commands.yml` (linhas 126-152)

**Exit codes:**
- **0:** PASS (modelo 100% conforme)
- **2:** PARITY FAIL (divergência estrutural entre DB e model)
- **3:** GUARD FAIL (arquivo protegido modificado)
- **4:** REQUIREMENTS FAIL (violação de tipo, nullable, FK, etc)

#### 4.2 Parity check (sem autogen)

```powershell
# Apenas verificar paridade (sem aplicar correções)
.\scripts\parity_gate.ps1 -Table "athletes"

# Pular regeneração de docs (usar schema.sql existente)
.\scripts\parity_gate.ps1 -Table "athletes" -SkipDocsRegeneration
```

**Evidência:** `docs/_ai/_context/approved-commands.yml` (linhas 153-158)

#### 4.3 Validar requirements (sem autogen)

```powershell
# Validar tipos, nullable, FK, CHECK, INDEX, server_default
.\venv\Scripts\python.exe scripts\model_requirements.py --table athletes --profile strict

# Perfis disponíveis: strict (rigoroso), fk (apenas FK), lenient (permissivo)
.\venv\Scripts\python.exe scripts\model_requirements.py --table athletes --profile fk
```

**Evidência:**
- `docs/_ai/_context/approved-commands.yml` (linhas 266-291)
- `docs/_ai/_specs/invocation-examples.yml` (linhas 1-9)

---

### Categoria 5: Batch Operations

#### 5.1 Scan de múltiplas tabelas (dry-run)

```powershell
# Escanear todos os models sem aplicar correções
.\scripts\models_batch.ps1 -DryRun -SkipRefresh
```

**Evidência:** `docs/_ai/_context/approved-commands.yml` (linhas 159-184)

**Output esperado:**
```
[PHASE 3: Scan - COMPLETE]
PASS: 10, FAIL: 3, SKIP: 2
Exit code: 0
```

#### 5.2 Batch fix (aplicar correções)

```powershell
# Executar scan + fix para tabelas com falha
.\scripts\models_batch.ps1 -SkipRefresh
```

**Evidência:** `docs/_ai/_context/approved-commands.yml` (linhas 185-201)

---

## 🔍 Troubleshooting

### Exit Code 2: Parity Structural Diffs

**Causas comuns:**
- Migration pendente não aplicada
- Model alterado sem migration correspondente
- Schema PostgreSQL alterado manualmente (fora de Alembic)

**Referência:** `docs/_ai/_maps/troubleshooting-map.json` (linhas 5-22)

**Solução:**
1. Verificar migrations pendentes: `.\env\Scripts\python.exe -m alembic current`
2. Aplicar migrations: `.\env\Scripts\python.exe -m alembic upgrade head`
3. Consultar: `docs/references/exit_codes.md` (seção Exit Code 2)

### Exit Code 3: Guard Violations

**Causas comuns:**
- Arquivo protegido foi modificado (ex: `app/routes/teams.py`)

**Referência:** `docs/_ai/_maps/troubleshooting-map.json` (linhas 23-36)

**Solução:**
1. Verificar modificações: `git diff app/routes/teams.py`
2. Se intencional: atualizar baseline: `.\env\Scripts\python.exe scripts\agent_guard.py snapshot baseline`
3. Se acidental: reverter: `git restore -- app/routes/teams.py`
4. Consultar: `docs/_ai/_context/approved-commands.yml` (seção Guard & Baseline)

### Exit Code 4: Requirements Violations

**Causas comuns:**
- Tipo incompatível (ex: `expected=Integer got=String`)
- Nullable mismatch (ex: `expected=NOT NULL got=omitted`)
- Missing server_default (ex: `expected=default_literal:false`)

**Referência:** `docs/_ai/_maps/troubleshooting-map.json` (linhas 37-46)

**Solução:**
1. Ver violações detalhadas no output do script
2. Corrigir model manualmente (ex: adicionar `server_default=text("false")`)
3. Consultar: `docs/references/exit_codes.md` (seção Exit Code 4)

---

## 📚 Documentação Complementar

| Documento | Caminho | Descrição |
|-----------|---------|-----------|
| **Start Here** | `docs/_canon/00_START_HERE.md` | Ponto de entrada da documentação canônica |
| **Approved Commands** | `docs/_canon/08_APPROVED_COMMANDS.md` | Lista completa de comandos aprovados |
| **Troubleshooting** | `docs/_canon/09_TROUBLESHOOTING_GUARD_PARITY.md` | Guia de resolução de problemas |
| **Exit Codes** | `docs/references/exit_codes.md` | Referência completa de códigos de saída |
| **Workflows** | `docs/_canon/03_WORKFLOWS.md` | Fluxos de trabalho detalhados |
| **Checklist Models** | `docs/execution_tasks/CHECKLIST-CANONICA-MODELS.md` | Checklist para models |
| **Implementation Summary** | `IMPLEMENTATION_SUMMARY.md` | Resumo da infraestrutura AI |

**Evidências:**
- Estrutura de `docs/_canon/` obtida via GitHub API
- Estrutura de `docs/references/` obtida via GitHub API
- Estrutura de `docs/execution_tasks/` obtida via GitHub API

---

## 🛠️ Utilitários Python

### 1. JSON Loader

```powershell
# Carregar JSON com validação
.\venv\Scripts\python.exe -c "from scripts._ia.utils.json_loader import load_json; print(load_json('docs/_ai/_maps/troubleshooting-map.json'))"
```

**Evidência:** `scripts/_ia/utils/json_loader.py` (linhas 16-43)

### 2. YAML Loader

```powershell
# Carregar YAML com validação
.\venv\Scripts\python.exe -c "from scripts._ia.utils.yaml_loader import load_yaml; print(load_yaml('docs/_ai/_context/approved-commands.yml'))"
```

**Evidência:** `scripts/_ia/utils/yaml_loader.py` (linhas 21-44)

---

## ⚠️ Comandos Proibidos

**NUNCA execute:**
```powershell
# ❌ Perde trabalho local permanentemente
git reset --hard <commit>

# ❌ Remove untracked files (sem recovery)
git clean -f

# ❌ Reescreve histórico remoto (quebra colaboração)
git push --force

# ❌ Deleta diretórios sem confirmação
Remove-Item -Recurse -Force <path>

# ❌ Risco de injeção de código
Invoke-Expression <string>
```

**Evidência:** `docs/_ai/_context/approved-commands.yml` (linhas 364-405)

---

## 🎓 Próximos Passos

1. **Leia:** `docs/_canon/00_START_HERE.md` para contexto completo
2. **Pratique:** Execute `.\scripts\inv.ps1 gate INV-TRAIN-015` para validar setup
3. **Consulte:** `docs/_canon/08_APPROVED_COMMANDS.md` para comandos avançados
4. **Aprenda:** `docs/_canon/03_WORKFLOWS.md` para fluxos de trabalho completos

---

**Última atualização:** 2026-02-12 07:45:52  
**Autor:** GitHub Copilot  
**Baseado em:** Artefatos existentes no repositório `Davisermenho/Hb_Track`