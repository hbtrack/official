# PLANO: Pipeline Robusto com AR como SSOT de Execução

**Status**: VALIDADO  
**Versão**: 1.0  
**Protocolo**: v1.3.0  
**Data**: 2026-02-26  
**Arquiteto**: Yan

## Objetivo

Desacoplar execução do pipeline do `_INDEX.md`, tornando as ARs a fonte única de verdade (SSOT) para decisões de execução. `_INDEX.md` se torna apenas cache/relatório que pode ficar desatualizado sem quebrar o fluxo.

## Problema Atual

- `hb_watch.py` depende de `parse_index()` para decidir quais ARs processar
- `hb_autotest.py` depende de `parse_index()` para detectar ARs em 🏗️ EM_EXECUCAO
- `hb verify` executa `rebuild_ar_index()` obrigatoriamente, criando dependência desnecessária
- `hb verify` escreve em Kanban, criando side-effect não-essencial
- `hb verify` tem risco de `restore` (via `check_workspace_clean`)
- Pipeline quebra se `_INDEX.md` ficar desatualizado

## Solução: AR-First Pipeline

### Mudança de Paradigma

**ANTES**: `_INDEX.md` → fonte de verdade → daemons leem índice → executam  
**DEPOIS**: AR.md → fonte de verdade → daemons leem ARs diretamente → `_INDEX.md` é só cache

### Componentes Afetados

1. **hb_watch.py** (AR_150): Scan recursivo de ARs + extração direta de status
2. **hb_autotest.py** (AR_151): Detecção via AR.md + evidence staged (sem índice)
3. **hb_cli.py - cmd_verify** (AR_152): Rebuild index OPCIONAL, Kanban removido
4. **hb_cli.py - check_workspace_clean** (AR_153): Sem restore, gate correto
5. **Documentação** (AR_154): Atualizar contratos e specs

---

## AR_150: hb_watch.py — AR-First Dispatcher

### Título
Modificar hb_watch.py para ler ARs diretamente (sem depender de _INDEX.md)

### Escopo de Mudança

**Arquivo**: `scripts/run/hb_watch.py`

**Funções modificadas**:
- `parse_index()` → `scan_ars_by_status()`
- `render_dashboard()` → atualizar chamada
- `main()` → atualizar fluxo

**Nova lógica**:
```python
def scan_ars_by_status(repo_root: Path, target_status: str) -> list:
    """
    Varre docs/hbtrack/ars/**/AR_*.md recursivamente e extrai ARs
    cujo campo **Status**: contém target_status.
    
    Retorna: [{"id": "055", "ar_file": "...", "title": "...", "status": "...", 
               "validation_command": "...", "write_scope": [...], "evidence": "..."}]
    """
    ar_dir = repo_root / AR_DIR
    ars = []
    for ar_file in ar_dir.rglob("AR_*.md"):
        content = ar_file.read_text(encoding="utf-8")
        
        # Extrair ID
        id_match = re.search(r"AR_(\d+)", ar_file.name)
        if not id_match:
            continue
        ar_id = id_match.group(1)
        
        # Extrair Status
        status_match = re.search(r'\*\*Status\*\*:\s*(.+)', content)
        status = status_match.group(1).strip() if status_match else ""
        
        # Filtrar por target_status
        if target_status not in status:
            continue
        
        # Extrair outros campos (read_ar_details já faz isso)
        details = read_ar_details(repo_root, ar_id)
        
        # Extrair título (primeira linha após # AR_)
        title_match = re.search(r'^#\s+AR_\d+[^\n]*\n(.+)', content, re.MULTILINE)
        title = title_match.group(1).strip()[:50] if title_match else ""
        
        ars.append({
            "id": ar_id,
            "id_num": ar_id,
            "ar_file": str(ar_file.relative_to(repo_root)),
            "title": title,
            "status": status,
            "validation_command": details.get("validation_command", ""),
            "write_scope": details.get("write_scope", []),
            "ssot_touches": details.get("ssot_touches", []),
            "evidence": details.get("ar_file", ""),  # Placeholder
        })
    
    return ars
```

**Modificar `render_dashboard()`**:
```python
def render_dashboard(repo_root: Path, mode: str) -> list:
    # ANTES: ars = parse_index(repo_root)
    # DEPOIS:
    status_map = {
        "architect": ["PROPOSTA", "STUB", "🔴 REJEITADO", "NEEDS_REVIEW"],
        "executor": ["🔲 PENDENTE"],
        "testador": ["🏗️ EM_EXECUCAO"],
    }
    
    target_statuses = status_map.get(mode, [])
    all_ars = []
    for status in target_statuses:
        all_ars.extend(scan_ars_by_status(repo_root, status))
    
    # Resto da lógica permanece igual
    ...
```

**Fallback para _INDEX.md**: REMOVIDO — `_INDEX.md` é ignorado pelo dispatcher

### Write Scope
- `scripts/run/hb_watch.py`

### Validation Command
```bash
python temp/ar150_validate.py
```

**Conteúdo de temp/ar150_validate.py**:
```python
#!/usr/bin/env python3
"""Valida que hb_watch.py funciona sem _INDEX.md atualizado"""
import subprocess
import sys
from pathlib import Path

repo_root = Path(__file__).parent.parent

# Simular: desatualizar _INDEX.md (renomear temporariamente)
index_old = repo_root / "docs/hbtrack/_INDEX.md"
index_bak = repo_root / "docs/hbtrack/_INDEX.md.bak_ar150"

if index_old.exists():
    index_old.rename(index_bak)

try:
    # Executar hb_watch uma vez
    result = subprocess.run(
        ["python", "scripts/run/hb_watch.py", "--mode", "executor", "--once"],
        capture_output=True,
        text=True,
        cwd=repo_root
    )
    
    # PASS se:
    # 1. Exit code 0
    # 2. Não menciona "_INDEX.md nao encontrado"
    # 3. Lista contexto de executor corretamente
    
    assert result.returncode == 0, f"Exit != 0: {result.returncode}"
    assert "nao encontrado" not in result.stdout.lower(), "Erro de _INDEX.md detectado"
    assert "executor" in result.stdout.lower() or "pending_ars" in result.stdout.lower(), \
        "Contexto de executor não gerado"
    
    print("✓ AR_150 PASS: hb_watch funciona sem _INDEX.md")
    sys.exit(0)
    
except AssertionError as e:
    print(f"✗ AR_150 FAIL: {e}", file=sys.stderr)
    sys.exit(1)
    
finally:
    # Restaurar _INDEX.md
    if index_bak.exists():
        index_bak.rename(index_old)
```

### Critérios de Aceitação
- [ ] `scan_ars_by_status()` implementada e testada
- [ ] `render_dashboard()` usa nova função
- [ ] Nenhuma referência a `parse_index()` em chamadas de execução
- [ ] `_INDEX.md` pode ser deletado temporariamente sem quebrar dispatch
- [ ] Validation command retorna exit 0

---

## AR_151: hb_autotest.py — AR-First Detection

### Título
Modificar hb_autotest.py para detectar ARs via status direto (sem _INDEX.md)

### Escopo de Mudança

**Arquivo**: `scripts/run/hb_autotest.py`

**Funções modificadas**:
- `parse_index()` → `find_ars_ready_for_verify()`
- `poll_and_execute()` → usar nova função

**Nova lógica**:
```python
def find_ars_ready_for_verify(repo_root: Path) -> list:
    """
    Encontra ARs elegíveis para verify lendo ARs diretamente.
    
    Critérios de elegibilidade:
    1. Status é 🏗️ EM_EXECUCAO (ou ✅ SUCESSO para retrocompat)
    2. Evidence do Executor existe: docs/hbtrack/evidence/AR_<id>/executor_main.log
    3. Evidence está staged: git diff --cached --name-only
    4. Não existe TESTADOR_REPORT staged para esse AR (evitar reprocessar)
    
    Retorna: [{"id": "055", "ar_file": "...", "evidence_path": "..."}]
    """
    ar_dir = repo_root / AR_DIR
    staged = get_staged_files(repo_root)
    
    eligible = []
    
    for ar_file in ar_dir.rglob("AR_*.md"):
        content = ar_file.read_text(encoding="utf-8")
        
        # Extrair ID
        id_match = re.search(r"AR_(\d+)", ar_file.name)
        if not id_match:
            continue
        ar_id = id_match.group(1)
        
        # Critério 1: Status
        status_match = re.search(r'\*\*Status\*\*:\s*(.+)', content)
        status = status_match.group(1).strip() if status_match else ""
        
        if not ('🏗️' in status or 'EM_EXECUCAO' in status or '✅ SUCESSO' in status):
            continue
        
        # Critério 2: Evidence existe
        evidence_path = f"docs/hbtrack/evidence/AR_{ar_id}/executor_main.log"
        evidence_file = repo_root / evidence_path
        if not evidence_file.exists():
            continue
        
        # Critério 3: Evidence está staged
        if evidence_path not in staged:
            continue
        
        # Critério 4: Não existe TESTADOR_REPORT staged
        testador_pattern = f"_reports/testador/AR_{ar_id}_"
        has_testador_staged = any(testador_pattern in f for f in staged)
        if has_testador_staged:
            continue
        
        eligible.append({
            "id": ar_id,
            "ar_file": str(ar_file.relative_to(repo_root)),
            "evidence_path": evidence_path,
        })
    
    return eligible
```

**Modificar `poll_and_execute()`**:
```python
def poll_and_execute(repo_root: Path, dry_run: bool = False) -> int:
    # ANTES: em_execucao = parse_index(repo_root)
    # DEPOIS:
    eligible_ars = find_ars_ready_for_verify(repo_root)
    
    if not eligible_ars:
        log("Nenhuma AR elegível para verify")
        return 0
    
    for ar in eligible_ars:
        ar_id = ar["id"]
        log(f"AR_{ar_id} ELEGÍVEL: evidence staged, status pronto")
        
        # Executar hb verify
        ec, stdout, stderr = run_hb_verify(repo_root, ar_id, dry_run)
        
        if ec == 0:
            log(f"✓ AR_{ar_id}: verify SUCESSO")
            # Auto-add TESTADOR_REPORT + AR
            # ...
        else:
            log_error(f"✗ AR_{ar_id}: verify FALHOU (exit {ec})")
    
    return len(eligible_ars)
```

### Write Scope
- `scripts/run/hb_autotest.py`

### Validation Command
```bash
python temp/ar151_validate.py
```

**Conteúdo de temp/ar151_validate.py**:
```python
#!/usr/bin/env python3
"""Valida que hb_autotest funciona sem _INDEX.md"""
import subprocess
import sys
from pathlib import Path

repo_root = Path(__file__).parent.parent

# Pré-condição: precisa de 1 AR em EM_EXECUCAO com evidence staged
# Para teste, usar AR_147 (última executada)

# Desatualizar _INDEX.md
index_old = repo_root / "docs/hbtrack/_INDEX.md"
index_bak = repo_root / "docs/hbtrack/_INDEX.md.bak_ar151"

if index_old.exists():
    index_old.rename(index_bak)

try:
    # Executar autotest uma vez
    result = subprocess.run(
        ["python", "scripts/run/hb_autotest.py", "--once", "--dry-run"],
        capture_output=True,
        text=True,
        cwd=repo_root
    )
    
    # PASS se:
    # 1. Exit code 0
    # 2. Lista ARs elegíveis sem mencionar erro de _INDEX.md
    # 3. Detecta AR_147 ou outra AR staged
    
    assert result.returncode == 0, f"Exit != 0: {result.returncode}"
    assert "_INDEX.md" not in result.stderr, "Erro de _INDEX.md detectado"
    
    # Se houver AR staged, deve listar
    output = result.stdout + result.stderr
    if "AR_" in output:
        assert "ELEGÍVEL" in output or "elegível" in output.lower(), \
            "AR não detectada como elegível"
    
    print("✓ AR_151 PASS: hb_autotest funciona sem _INDEX.md")
    sys.exit(0)
    
except AssertionError as e:
    print(f"✗ AR_151 FAIL: {e}", file=sys.stderr)
    sys.exit(1)
    
finally:
    if index_bak.exists():
        index_bak.rename(index_old)
```

### Critérios de Aceitação
- [ ] `find_ars_ready_for_verify()` implementada
- [ ] 4 critérios de elegibilidade validados
- [ ] `poll_and_execute()` usa nova função
- [ ] Nenhuma chamada a `parse_index()` em código de execução
- [ ] Validation command retorna exit 0

---

## AR_152: hb_cli.py - cmd_verify — Kanban-Free e Index-Optional

### Título
Remover obrigatoriedade de rebuild_index e Kanban write de cmd_verify

### Escopo de Mudança

**Arquivo**: `scripts/run/hb_cli.py`

**Funções modificadas**:
- `cmd_verify()` — remover `rebuild_ar_index()` obrigatório (tornar opcional)
- `finalize_verification()` — remover `update_kanban_and_status()` call

**Mudanças**:

1. **Remover Kanban write**:
```python
def finalize_verification(ar_id: str, ar_content: str, result: dict):
    """Roteia status do verify (SEM Kanban write)"""
    status = result["status"]
    consistency = result["consistency"]
    
    if status == "SUCESSO":
        novo_status = "✅ SUCESSO"
    elif status == "REJEITADO":
        novo_status = "🔴 REJEITADO"
    else:
        novo_status = "⏸️ BLOQUEADO_INFRA"
    
    # ANTES: ar_updated = update_kanban_and_status(ar_content, novo_status, ar_id)
    # DEPOIS: apenas atualizar campo **Status** na AR
    ar_updated = re.sub(
        r'(\*\*Status\*\*:)\s*.+',
        fr'\1 {novo_status}',
        ar_content
    )
    
    # Sem Kanban write — Kanban é atualizado apenas por hb seal ou manualmente
    
    final_exit = 0 if status == "SUCESSO" else 2
    return ar_updated, novo_status, final_exit
```

2. **Tornar rebuild_index OPCIONAL (comentado)**:
```python
def cmd_verify(ar_id: str) -> None:
    # ... (todo código de verify)
    
    # V9.5: Index rebuild É OPCIONAL — pipeline não depende mais dele
    # Index será reconstruído por hb seal ou por comando dedicado hb index
    
    # REMOVIDO (antes era obrigatório):
    # staged_ars = get_staged_ars(repo_root)
    # if len(staged_ars) > 1:
    #     print(f"  ⚠ BATCH MODE: skip rebuild")
    # else:
    #     rebuild_ar_index(repo_root)
    
    # NOVO: index rebuild é responsabilidade do humano/seal
    print(f"  ℹ Index rebuild SKIPPED (execute 'hb index' se necessário)")
```

### Write Scope
- `scripts/run/hb_cli.py`

### Validation Command
```bash
python temp/ar152_validate.py
```

**Conteúdo de temp/ar152_validate.py**:
```python
#!/usr/bin/env python3
"""Valida que verify não toca Kanban e não exige index rebuild"""
import subprocess
import sys
import re
from pathlib import Path

repo_root = Path(__file__).parent.parent
kanban_path = repo_root / "docs/hbtrack/Hb Track Kanban.md"

# Pré-condição: AR_147 em EM_EXECUCAO com evidence staged

# Capturar estado inicial do Kanban
kanban_before = kanban_path.read_text(encoding="utf-8") if kanban_path.exists() else ""

# Executar verify
result = subprocess.run(
    ["python", "scripts/run/hb_cli.py", "verify", "147"],
    capture_output=True,
    text=True,
    cwd=repo_root
)

# PASS se:
# 1. Exit 0 (ou exit esperado do verify)
# 2. Kanban não foi modificado
# 3. Não executa rebuild_index (mensagem "Index rebuild SKIPPED")

kanban_after = kanban_path.read_text(encoding="utf-8") if kanban_path.exists() else ""

try:
    # Kanban deve permanecer intacto
    assert kanban_before == kanban_after, "Kanban foi modificado pelo verify"
    
    # Deve mencionar skip de index
    output = result.stdout + result.stderr
    assert "Index rebuild SKIPPED" in output or "index" not in output.lower(), \
        "Index rebuild não foi pulado"
    
    # AR deve ter sido atualizada com stamp do Testador
    ar_147 = list((repo_root / "docs/hbtrack/ars").rglob("AR_147_*.md"))[0]
    ar_content = ar_147.read_text(encoding="utf-8")
    assert "### Verificacao Testador" in ar_content, "Stamp do Testador não foi adicionado"
    
    print("✓ AR_152 PASS: verify não toca Kanban e index é opcional")
    sys.exit(0)
    
except AssertionError as e:
    print(f"✗ AR_152 FAIL: {e}", file=sys.stderr)
    sys.exit(1)
```

### Critérios de Aceitação
- [ ] `finalize_verification()` não chama `update_kanban_and_status()`
- [ ] `cmd_verify()` não chama `rebuild_ar_index()`
- [ ] Mensagem "Index rebuild SKIPPED" presente no output
- [ ] Kanban permanece inalterado após verify
- [ ] Status da AR é atualizado corretamente

---

## AR_153: hb_cli.py - Anti-Restore Gate

### Título
Remover qualquer caminho de código que execute git restore no verify

### Escopo de Mudança

**Arquivo**: `scripts/run/hb_cli.py`

**Funções modificadas**:
- `check_workspace_clean()` — CONFIRMAÇÃO (já está correto)

**Auditoria de Segurança**:

Procurar por padrões perigosos:
- `git restore`
- `git reset`
- `git clean`
- `subprocess.*restore`
- `run_cmd.*restore`

**Resultado esperado**: NENHUMA ocorrência em código de execução do verify

**Gate existente em check_workspace_clean()**:
```python
def check_workspace_clean() -> Tuple[bool, str]:
    """
    Workspace limpo = SEM unstaged changes em tracked files.
    
    STAGED files são PERMITIDOS (trabalho do Executor em andamento).
    Untracked files são IGNORADOS (não afetam verify).
    
    Este gate NÃO executa git restore/reset/clean.
    Apenas DETECTA e BLOQUEIA verify se houver unstaged changes.
    """
    try:
        out = subprocess.run(
            ['git', 'diff', '--name-only'],  # SÓ tracked unstaged
            capture_output=True, text=True, encoding='utf-8'
        )
        lines = [l for l in out.stdout.strip().split('\n') if l.strip()]
        if not lines:
            return True, 'workspace_clean'
        return False, f'unstaged_modified={len(lines)}'
    except Exception as e:
        return False, f'git_error={e}'
```

**Confirmação**: Gate JÁ está correto. Apenas DETECTA, nunca executa restore.

### Write Scope
- `scripts/run/hb_cli.py` (auditoria apenas, sem mudança de código)

### Validation Command
```bash
python temp/ar153_validate.py
```

**Conteúdo de temp/ar153_validate.py**:
```python
#!/usr/bin/env python3
"""Valida que verify nunca executa git restore/reset/clean"""
import sys
from pathlib import Path

repo_root = Path(__file__).parent.parent
hb_cli = repo_root / "scripts/run/hb_cli.py"

content = hb_cli.read_text(encoding="utf-8")

# Padrões proibidos
forbidden_patterns = [
    r'git\s+restore',
    r'git\s+reset',
    r'git\s+clean',
    r'subprocess.*restore',
    r'run_cmd.*restore',
]

import re

violations = []
for pattern in forbidden_patterns:
    if re.search(pattern, content, re.IGNORECASE):
        violations.append(pattern)

if violations:
    print(f"✗ AR_153 FAIL: Padrões proibidos encontrados: {violations}", file=sys.stderr)
    sys.exit(1)

# Verificar que check_workspace_clean usa git diff --name-only (correto)
if "git diff --name-only" not in content:
    print("✗ AR_153 FAIL: check_workspace_clean não usa git diff correto", file=sys.stderr)
    sys.exit(1)

# Verificar mensagem anti-restore em check_workspace_clean
if "DETECTA e BLOQUEIA" not in content and "nunca executa" not in content.lower():
    print("⚠ AR_153 WARNING: Comentário anti-restore não encontrado", file=sys.stderr)

print("✓ AR_153 PASS: Nenhum git restore/reset/clean no verify")
sys.exit(0)
```

### Critérios de Aceitação
- [ ] Zero ocorrências de `git restore` em hb_cli.py
- [ ] Zero ocorrências de `git reset` em código de verify
- [ ] Zero ocorrências de `git clean` em código de verify
- [ ] `check_workspace_clean()` usa apenas `git diff --name-only`
- [ ] Validation command retorna exit 0

---

## AR_154: Documentação - Atualizar Contratos

### Título
Atualizar Dev Flow e contratos para refletir AR-First Pipeline

### Escopo de Mudança

**Arquivos**:
- `docs/_canon/contratos/Dev Flow.md`
- `docs/_canon/contratos/Testador Contract.md`
- `docs/_canon/specs/Hb cli.md`

**Mudanças em Dev Flow.md**:

Seção 2.3 (Índice):
```markdown
2.3) Índice (regra dura)

* `docs/hbtrack/_INDEX.md` é o **Cache de Visualização** gerado automaticamente.
* DEVE ser AUTO-GERADO por hb (`hb index` ou `hb seal`).
* NÃO é usado como fonte de verdade para execução do pipeline.
* **Pipeline executa lendo ARs diretamente** — `_INDEX.md` pode ficar desatualizado temporariamente.
* MUST NOT ser editado manualmente.
* **AR staged ⇒ `_INDEX.md` SHOULD estar staged** (recomendação, não bloqueio hard).
```

**Mudanças em Testador Contract.md**:

Seção §3, Passo T1:
```markdown
Passo T1 — LOCALIZAR
  hb verify <id> → localiza AR_<id>_*.md DIRETAMENTE (sem depender de _INDEX.md)
```

Seção §5 (Status de AR):
```markdown
## §5 STATUS DE AR APÓS TESTADOR

Testador escreve status na AR via atualização do campo **Status**:
- ✅ SUCESSO → validação passou (triple-run OK, exit 0, consistency OK)
- 🔴 REJEITADO → falha detectada (AH_DIVERGENCE, FLAKY_OUTPUT, TRIPLE_FAIL, etc)
- ⏸️ BLOQUEADO_INFRA → falha de infra (timeout, db offline, etc) exige waiver

**KANBAN NÃO É ATUALIZADO PELO VERIFY** — Kanban é sincronizado por:
- `hb seal` (após selo humano)
- `hb kanban sync` (comando dedicado)
```

**Mudanças em Hb cli.md**:

Nova seção §13:
```markdown
## §13 hb index

**Sintaxe**:
```bash
hb index
```

**Função**: Rebuild de `docs/hbtrack/_INDEX.md` a partir das ARs.

**Quando usar**:
- Após batch de ARs (múltiplas ARs seladas)
- Quando `_INDEX.md` ficar desatualizado
- Para gerar relatório atualizado

**NÃO é necessário para**:
- Pipeline continuar funcionando (ARs são SSOT)
- Verify ou seal executarem
```

### Write Scope
- `docs/_canon/contratos/Dev Flow.md`
- `docs/_canon/contratos/Testador Contract.md`
- `docs/_canon/specs/Hb cli.md`

### Validation Command
```bash
python temp/ar154_validate.py
```

**Conteúdo de temp/ar154_validate.py**:
```python
#!/usr/bin/env python3
"""Valida que documentação menciona AR-First Pipeline"""
import sys
from pathlib import Path

repo_root = Path(__file__).parent.parent

files_to_check = [
    "docs/_canon/contratos/Dev Flow.md",
    "docs/_canon/contratos/Testador Contract.md",
    "docs/_canon/specs/Hb cli.md",
]

required_keywords = {
    "Dev Flow.md": ["Cache de Visualização", "Pipeline executa lendo ARs diretamente"],
    "Testador Contract.md": ["DIRETAMENTE", "sem depender de _INDEX.md"],
    "Hb cli.md": ["hb index", "ARs são SSOT"],
}

all_pass = True

for file_rel in files_to_check:
    file_path = repo_root / file_rel
    if not file_path.exists():
        print(f"✗ {file_rel}: arquivo não encontrado", file=sys.stderr)
        all_pass = False
        continue
    
    content = file_path.read_text(encoding="utf-8")
    keywords = required_keywords.get(file_path.name, [])
    
    for keyword in keywords:
        if keyword not in content:
            print(f"✗ {file_rel}: keyword '{keyword}' não encontrada", file=sys.stderr)
            all_pass = False

if all_pass:
    print("✓ AR_154 PASS: Documentação atualizada com AR-First Pipeline")
    sys.exit(0)
else:
    sys.exit(1)
```

### Critérios de Aceitação
- [ ] Dev Flow menciona "_INDEX.md como cache"
- [ ] Testador Contract menciona "leitura direta de ARs"
- [ ] Hb cli.md documenta `hb index` como comando opcional
- [ ] Validation command retorna exit 0

---

## Checklist de Teste (3 Testes de Validação)

### Teste 1: _INDEX.md desatualizado não quebra dispatch

**Pré-condição**:
- hb_watch rodando
- Escolher AR pequena (ex: AR_147 ou criar AR_999 de teste)

**Execução**:
1. NÃO regenerar `_INDEX.md` (deixar desatualizado)
2. Executar: `python scripts/run/hb_watch.py --mode executor --once`
3. Verificar output do contexto

**PASS se**:
- Contexto de executor inclui a AR correta lendo `**Status**:` da AR.md
- Nenhum erro de "_INDEX.md não encontrado"
- AR listada corretamente mesmo com índice desatualizado

**FAIL se**:
- hb_watch só lista ARs do índice e ignora ARs reais
- Erro de arquivo não encontrado

---

### Teste 2: Autotest dispara por AR + evidence staged

**Pré-condição**:
- AR_147 (ou outra) implementada
- Evidence staged: `docs/hbtrack/evidence/AR_147/executor_main.log`

**Execução**:
1. NÃO regenerar `_INDEX.md`
2. Stage apenas evidence + código modificado
3. Observar logs do hb_autotest (ou executar `--once`)

**PASS se**:
- hb_autotest detecta AR elegível lendo AR.md + verificando evidence staged
- Executa `hb verify 147` automaticamente
- Gera `_reports/testador/AR_147_<hash>/result.json`

**FAIL se**:
- hb_autotest não faz nada até `_INDEX.md` ser atualizado
- Erro ou skip inesperado

---

### Teste 3: Verify não toca Kanban e não usa restore

**Pré-condição**:
- AR elegível para verify
- 1 arquivo tracked modificado SEM stage (tripwire)

**Execução**:
1. Modificar 1 linha em arquivo governado (ex: README.md) SEM `git add`
2. Executar: `python scripts/run/hb_cli.py verify 147`
3. Observar comportamento

**PASS FASE 1** (gate correto):
- verify FALHA com `E_VERIFY_DIRTY_WORKSPACE`
- Mensagem: "unstaged_modified=1"
- NÃO executa git restore automaticamente

**Execução Fase 2**:
1. Reverter tripwire manualmente: `git restore README.md`
2. Re-executar verify

**PASS FASE 2** (sem Kanban write):
- verify gera `_reports/testador/AR_147_<hash>/context.json` + `result.json`
- Atualiza stamp na AR.md
- **Kanban NÃO modificado** (verificar `git diff docs/hbtrack/Hb Track Kanban.md`)
- Nenhum `git restore` executado (checkável por logs ou ausência de mudanças "sumidas")

**Sinais de PASS visual**:
```bash
git diff --cached --name-only
# DEVE mostrar:
# docs/hbtrack/ars/features/AR_147_*.md
# _reports/testador/AR_147_<hash>/context.json
# _reports/testador/AR_147_<hash>/result.json

# NÃO DEVE mostrar:
# docs/hbtrack/Hb Track Kanban.md
```

---

## Dependências e Riscos

### Dependências
- Nenhuma AR bloqueadora
- Workspace limpo para implementação
- ARs de teste disponíveis (AR_147 ou criar AR_999)

### Riscos

**R1: Retrocompatibilidade**
- Solução: Manter `_INDEX.md` sendo gerado por `hb seal` e `hb index`
- Scripts antigos que dependem do índice continuarão funcionando
- Transição gradual (daemons novos → scripts antigos deprecados)

**R2: Performance de scan recursivo**
- Solução: `rglob()` do Python é eficiente para ~100 ARs
- Cache pode ser implementado posteriormente se necessário
- Primeira implementação: scan completo a cada poll (aceitável para daemon)

**R3: ARs com status ambíguo**
- Solução: Regex de status é precisa (`**Status**:`)
- Validar todos os formatos de status existentes
- Gate anti-status-malformado já existe em hb plan/report

---

## Ordem de Execução Recomendada

1. **AR_153** (Auditoria anti-restore) — zero risco, apenas confirmação
2. **AR_150** (hb_watch AR-first) — impacto isolado no dispatcher
3. **AR_151** (hb_autotest AR-first) — depende de 150 conceitualmente
4. **AR_152** (verify Kanban-free) — impacto no verify
5. **AR_154** (Documentação) — última, após implementação validada

---

## Definition of Done (Pipeline Robusto)

Pipeline é considerado robusto quando:

- [ ] Teste 1 PASSA: _INDEX.md desatualizado não quebra dispatch
- [ ] Teste 2 PASSA: autotest detecta por AR + evidence
- [ ] Teste 3 PASSA: verify sem Kanban/restore
- [ ] Zero ocorrências de `git restore` em verify
- [ ] hb_watch lê ARs diretamente (scan recursivo)
- [ ] hb_autotest lê ARs diretamente (4 critérios de elegibilidade)
- [ ] cmd_verify não chama rebuild_index obrigatório
- [ ] cmd_verify não escreve Kanban
- [ ] Documentação atualizada (Dev Flow, Testador Contract, Hb cli)
- [ ] Batch de ARs pode ser processado sem "desatualização" do índice
- [ ] `_INDEX.md` vira cache opcional (pode ficar 30s atrasado sem quebrar)

---

## Próximos Passos

Após validação do plano:

1. Criar plano JSON para cada AR (AR_150 a AR_154)
2. Executar `hb plan` para cada plano
3. Executor implementa em sequência (AR_153 → AR_150 → AR_151 → AR_152 → AR_154)
4. Testador valida cada AR com triple-run
5. Executar os 3 testes de validação do pipeline completo
6. Bump PROTOCOL_VERSION para v1.4.0 (mudança de paradigma)
