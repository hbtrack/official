#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HB Track CLI — scripts/run/hb.py (Entrypoint Oficial)
Versão: v1.0.5
SSOT: docs/_canon/specs/Hb cli.md
Contrato: docs/_canon/contratos/Dev Flow.md
Schema: docs/_canon/contratos/ar_contract.schema.json
"""

import sys
import os
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Configurar stdout para UTF-8 (Windows fix)
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# ========== CONFIGURAÇÃO (CANON) ==========
HB_PROTOCOL_VERSION = "1.0.5"

# Paths canônicos (relativos à raiz do repo)
PLANS_DIR = "docs/_canon/planos"
AR_DIR = "docs/hbtrack/ars"
EV_DIR = "docs/hbtrack/evidence"
SSOT_FILES = [
    "docs/ssot/schema.sql",
    "docs/ssot/openapi.json",
    "docs/ssot/alembic_state.txt"
]
SCHEMA_PATH = "docs/_canon/contratos/ar_contract.schema.json"

# Governed roots (código que exige AR no commit)
GOVERNED_ROOTS = [
    "backend/",
    "Hb Track - Fronted/"
]

# Error codes determinísticos
E_DEP_JSONSCHEMA = "E_DEP_JSONSCHEMA"
E_PLAN_PATH = "E_PLAN_PATH"
E_PLAN_JSON = "E_PLAN_JSON"
E_PLAN_SCHEMA = "E_PLAN_SCHEMA"
E_PLAN_VERSION_MISMATCH = "E_PLAN_VERSION_MISMATCH"
E_TASK_EVIDENCE_ID_MISMATCH = "E_TASK_EVIDENCE_ID_MISMATCH"
E_AR_NOT_FOUND = "E_AR_NOT_FOUND"
E_CMD_MISMATCH = "E_CMD_MISMATCH"

# ========== UTILS ==========
def get_repo_root() -> Path:
    """Retorna o root do repo (assume que hb.py está em scripts/run/)."""
    return Path(__file__).resolve().parent.parent.parent

def fail(code: str, msg: str, exit_code: int = 1) -> None:
    """Imprime erro determinístico e sai."""
    print(f"❌ {code}: {msg}", file=sys.stderr)
    sys.exit(exit_code)

def run_cmd(cmd: str) -> Tuple[int, str, str]:
    """Executa comando e retorna (exit_code, stdout, stderr)."""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr

def slugify(text: str) -> str:
    """Converte título em slug simples."""
    return text.lower().replace(" ", "_").replace("/", "_")[:50]

# ========== COMANDOS ==========
def cmd_version() -> None:
    """Comando: hb version"""
    print(f"HB Track Protocol v{HB_PROTOCOL_VERSION}")
    sys.exit(0)

def cmd_plan(plan_path: str) -> None:
    """Comando: hb plan <plan_json_path>"""
    repo_root = get_repo_root()
    
    # P1: validar path dentro de PLANS_DIR
    plan_file = Path(plan_path)
    if not plan_file.is_absolute():
        plan_file = repo_root / plan_file
    
    plans_dir = repo_root / PLANS_DIR
    try:
        plan_file.resolve().relative_to(plans_dir.resolve())
    except ValueError:
        fail(E_PLAN_PATH, 
             f"Plan JSON must be inside {PLANS_DIR}/ (got: {plan_path})")
    
    # P2: validar JSON parseável
    try:
        with open(plan_file, "r", encoding="utf-8") as f:
            plan_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        fail(E_PLAN_JSON, f"Failed to parse plan JSON: {e}")
    
    # P3: validar contra schema (requer jsonschema)
    try:
        import jsonschema
    except ImportError:
        fail(E_DEP_JSONSCHEMA, 
             "jsonschema library not found. Install via: pip install jsonschema")
    
    schema_file = repo_root / SCHEMA_PATH
    try:
        with open(schema_file, "r", encoding="utf-8") as f:
            schema = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        fail(E_PLAN_SCHEMA, f"Failed to load schema: {e}")
    
    try:
        jsonschema.validate(instance=plan_data, schema=schema)
    except jsonschema.ValidationError as e:
        fail(E_PLAN_SCHEMA, 
             f"Plan JSON violates schema at {e.json_path}: {e.message}")
    
    # P4: validar versão do protocolo
    if plan_data.get("version") != HB_PROTOCOL_VERSION:
        fail(E_PLAN_VERSION_MISMATCH, 
             f"Plan version '{plan_data.get('version')}' != protocol version '{HB_PROTOCOL_VERSION}'")
    
    # P5 & P6: materializar ARs
    ar_dir = repo_root / AR_DIR
    ar_dir.mkdir(parents=True, exist_ok=True)
    
    created_ars = []
    for task in plan_data["tasks"]:
        task_id = task["id"]
        title = task["title"]
        description = task["description"]
        criteria = task["criteria"]
        validation_cmd = task["validation_command"]
        evidence_file = task["evidence_file"]
        ssot_touches = task.get("ssot_touches", [])
        notes = task.get("notes", "")
        risks = task.get("risks", [])
        
        # P6: coerência id ↔ evidence_file
        if f"AR_{task_id}" not in evidence_file:
            fail(E_TASK_EVIDENCE_ID_MISMATCH, 
                 f"Task {task_id}: evidence_file must contain 'AR_{task_id}' (got: {evidence_file})")
        
        # Gerar slug
        slug = slugify(title)
        ar_filename = f"AR_{task_id}_{slug}.md"
        ar_path = ar_dir / ar_filename
        
        # Escrever AR
        with open(ar_path, "w", encoding="utf-8") as f:
            f.write(f"# AR_{task_id} — {title}\n\n")
            f.write(f"**Status**: DRAFT\n")
            f.write(f"**Versão do Protocolo**: {HB_PROTOCOL_VERSION}\n\n")
            
            f.write(f"## Descrição\n{description}\n\n")
            f.write(f"## Critérios de Aceite\n{criteria}\n\n")
            
            if ssot_touches:
                f.write(f"## SSOT Touches\n")
                for ssot in ssot_touches:
                    f.write(f"- [ ] {ssot}\n")
                f.write("\n")
            
            f.write(f"## Validation Command (Contrato)\n```\n{validation_cmd}\n```\n\n")
            f.write(f"## Evidence File (Contrato)\n`{evidence_file}`\n\n")
            
            if notes:
                f.write(f"## Notas do Arquiteto\n{notes}\n\n")
            
            if risks:
                f.write(f"## Riscos\n")
                for risk in risks:
                    f.write(f"- {risk}\n")
                f.write("\n")
            
            f.write(f"## Análise de Impacto\n_(A ser preenchido pelo Executor)_\n\n")
            f.write(f"---\n## Carimbo de Execução\n_(Gerado por hb report)_\n\n")
        
        created_ars.append(ar_filename)
    
    print(f"✅ Plan materialized successfully:")
    for ar in created_ars:
        print(f"   - {AR_DIR}/{ar}")
    sys.exit(0)

def cmd_report(ar_id: str, command: str) -> None:
    """Comando: hb report <id> "<command>" """
    repo_root = get_repo_root()
    ar_dir = repo_root / AR_DIR
    
    # R1: localizar AR por prefixo
    ar_files = list(ar_dir.glob(f"AR_{ar_id}_*.md"))
    if not ar_files:
        fail(E_AR_NOT_FOUND, f"AR with id {ar_id} not found in {AR_DIR}/", exit_code=2)
    
    ar_file = ar_files[0]
    
    # Ler AR para extrair contrato (validation command e evidence file)
    with open(ar_file, "r", encoding="utf-8") as f:
        ar_content = f.read()
    
    # Extrair validation command (entre ```...```)
    import re
    match = re.search(r"## Validation Command \(Contrato\)\n```\n(.+?)\n```", ar_content, re.DOTALL)
    declared_cmd = match.group(1).strip() if match else ""
    
    # R2: validar command match
    if declared_cmd and declared_cmd != command:
        fail(E_CMD_MISMATCH, 
             f"Command mismatch.\nDeclared: {declared_cmd}\nReceived: {command}", 
             exit_code=3)
    
    # Extrair evidence file path
    match = re.search(r"## Evidence File \(Contrato\)\n`(.+?)`", ar_content)
    evidence_file_path = match.group(1).strip() if match else f"{EV_DIR}/AR_{ar_id}_evidence.log"
    
    # R3: executar comando
    print(f"🔄 Executing: {command}")
    exit_code, stdout, stderr = run_cmd(command)
    
    # Obter contexto git e Python
    git_head = run_cmd("git rev-parse HEAD")[1].strip() or "N/A"
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    
    # Gravar evidence pack
    ev_file = repo_root / evidence_file_path
    ev_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(ev_file, "w", encoding="utf-8") as f:
        f.write(f"AR_ID: {ar_id}\n")
        f.write(f"Command: {command}\n")
        f.write(f"Exit Code: {exit_code}\n")
        f.write(f"Git HEAD: {git_head}\n")
        f.write(f"Python Version: {python_version}\n")
        f.write(f"Protocol Version: {HB_PROTOCOL_VERSION}\n")
        f.write(f"\n--- STDOUT ---\n{stdout}\n")
        f.write(f"\n--- STDERR ---\n{stderr}\n")
    
    # Anexar carimbo na AR
    status_emoji = "✅ SUCESSO" if exit_code == 0 else "❌ FALHA"
    with open(ar_file, "a", encoding="utf-8") as f:
        f.write(f"\n### Execução em {git_head[:7]}\n")
        f.write(f"**Status Final**: {status_emoji}\n")
        f.write(f"**Comando**: `{command}`\n")
        f.write(f"**Exit Code**: {exit_code}\n")
        f.write(f"**Evidence File**: `{evidence_file_path}`\n")
        f.write(f"**Python Version**: {python_version}\n\n")
    
    print(f"{status_emoji} Evidence logged to: {evidence_file_path}")
    
    # Exit code do hb report reflete o resultado do comando
    sys.exit(0 if exit_code == 0 else 1)

def cmd_check(mode: str = "manual") -> None:
    """Comando: hb check --mode {manual|pre-commit}"""
    repo_root = get_repo_root()
    
    print(f"🔍 HB Check (Protocol v{HB_PROTOCOL_VERSION}) — mode: {mode}")
    
    # C1: SSOT MUST existir
    for ssot in SSOT_FILES:
        ssot_path = repo_root / ssot
        if not ssot_path.exists():
            fail("E_SSOT_MISSING", f"SSOT file missing: {ssot}", exit_code=1)
    
    # C2: SSOT com mudanças UNSTAGED => FAIL
    _, stdout, _ = run_cmd("git diff --name-only")
    unstaged_files = stdout.strip().split("\n") if stdout.strip() else []
    
    ssot_unstaged = [f for f in unstaged_files if f in SSOT_FILES]
    if ssot_unstaged:
        fail("E_SSOT_UNSTAGED", 
             f"SSOT files have unstaged changes: {ssot_unstaged}", exit_code=1)
    
    # C3 & C4: verificar staged files
    _, stdout, _ = run_cmd("git diff --cached --name-only")
    staged_files = stdout.strip().split("\n") if stdout.strip() else []
    
    ssot_staged = [f for f in staged_files if f in SSOT_FILES]
    governed_changed = any(
        any(f.startswith(root) for root in GOVERNED_ROOTS) 
        for f in staged_files
    )
    ars_staged = [f for f in staged_files if f.startswith(AR_DIR)]
    
    # C3: Se SSOT STAGED => exigir AR staged com sucesso + evidence staged
    if ssot_staged:
        if not ars_staged:
            fail("E_SSOT_NO_AR", 
                 f"SSOT files staged without AR: {ssot_staged}", exit_code=1)
        
        # Verificar se alguma AR staged cobre os SSOT e tem evidência válida
        valid_ar_found = False
        for ar_path in ars_staged:
            ar_file = repo_root / ar_path
            if not ar_file.exists():
                continue
            
            with open(ar_file, "r", encoding="utf-8") as f:
                ar_content = f.read()
            
            # Verificar se AR marca algum SSOT staged como [x]
            if any(f"[x] {ssot}" in ar_content for ssot in ssot_staged):
                # Verificar se AR tem carimbo com ✅ SUCESSO
                if "✅ SUCESSO" in ar_content:
                    # Extrair evidence file path
                    import re
                    match = re.search(r"## Evidence File \(Contrato\)\n`(.+?)`", ar_content)
                    if match:
                        ev_path = match.group(1).strip()
                        if ev_path in staged_files:
                            # Verificar se evidence tem Exit Code: 0
                            ev_file = repo_root / ev_path
                            if ev_file.exists():
                                with open(ev_file, "r", encoding="utf-8") as ef:
                                    ev_content = ef.read()
                                if "Exit Code: 0" in ev_content:
                                    valid_ar_found = True
                                    break
        
        if not valid_ar_found:
            fail("E_SSOT_NO_VALID_AR", 
                 "SSOT staged but no valid AR with [x] + ✅ SUCESSO + staged evidence (Exit Code: 0)", 
                 exit_code=1)
    
    # C4: Se governed roots mudaram => exigir pelo menos 1 AR staged
    if governed_changed and not ars_staged:
        fail("E_GOVERNED_NO_AR", 
             f"Governed roots changed without AR staged", exit_code=1)
    
    # C5: Anti-forja mínima (já coberto em C3)
    
    print("✅ Check PASSED")
    sys.exit(0)

# ========== MAIN ==========
def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: hb <command> [args]")
        print("Commands: version | plan <path> | report <id> \"<cmd>\" | check --mode <mode>")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "version":
        cmd_version()
    
    elif command == "plan":
        if len(sys.argv) < 3:
            fail("E_USAGE", "Usage: hb plan <plan_json_path>")
        cmd_plan(sys.argv[2])
    
    elif command == "report":
        if len(sys.argv) < 4:
            fail("E_USAGE", "Usage: hb report <id> \"<command>\"")
        cmd_report(sys.argv[2], sys.argv[3])
    
    elif command == "check":
        mode = "manual"
        if len(sys.argv) >= 4 and sys.argv[2] == "--mode":
            mode = sys.argv[3]
        cmd_check(mode)
    
    else:
        fail("E_UNKNOWN_COMMAND", f"Unknown command: {command}")

if __name__ == "__main__":
    main()

