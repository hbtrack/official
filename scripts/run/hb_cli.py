#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HB Track CLI — scripts/run/hb_cli.py (Entrypoint Oficial)
Versão: v1.0.6
SSOT: docs/_canon/specs/Hb cli.md
Contrato: docs/_canon/contratos/Dev Flow.md
Schema: docs/_canon/contratos/ar_contract.schema.json

Changelog v1.0.6:
  - GATE 2: Validação de IDs únicos no plan JSON
  - GATE 2.5: Rollback obrigatório para ARs de banco
  - GATE 3: Detecção de colisão com ARs existentes no disco
  - GATE 4+5: Escrita atômica (.tmp/) + pós-validação anti-zero-bytes
  - Flags CLI: --force, --skip-existing, --dry-run
"""

import sys
import os
import re
import json
import shutil
import subprocess
from collections import Counter
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Configurar stdout para UTF-8 (Windows fix)
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# ========== CONFIGURAÇÃO (CANON) ==========
HB_PROTOCOL_VERSION = "1.0.6"

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

# SSOT files que indicam alteração de banco
DB_SSOT_FILES = ["docs/ssot/schema.sql", "docs/ssot/alembic_state.txt"]

# Keywords que indicam task de banco (lowercase para matching)
DB_KEYWORDS_CMD = ["alembic", "migration", "psql", "sql"]
DB_KEYWORDS_DESC = ["migration", "add column", "drop column", "alter table",
                    "create table", "drop table", "create index", "drop index",
                    "foreign key", "downgrade"]

# Padrões válidos de rollback (case-insensitive)
VALID_ROLLBACK_PATTERNS = [
    "alembic downgrade", "git revert", "drop index", "drop constraint",
    "drop column", "drop table", "alter table", "delete from", "update",
    "drop foreign key", "rollback"
]

# Tamanho mínimo de AR válido (bytes) — header + seções obrigatórias
MIN_AR_SIZE_BYTES = 200

# Governed roots (código que exige AR no commit)
GOVERNED_ROOTS = [
    "backend/",
    "Hb Track - Fronted/"
]

# Error codes determinísticos — originais
E_DEP_JSONSCHEMA = "E_DEP_JSONSCHEMA"
E_PLAN_PATH = "E_PLAN_PATH"
E_PLAN_JSON = "E_PLAN_JSON"
E_PLAN_SCHEMA = "E_PLAN_SCHEMA"
E_PLAN_VERSION_MISMATCH = "E_PLAN_VERSION_MISMATCH"
E_TASK_EVIDENCE_ID_MISMATCH = "E_TASK_EVIDENCE_ID_MISMATCH"
E_AR_NOT_FOUND = "E_AR_NOT_FOUND"
E_CMD_MISMATCH = "E_CMD_MISMATCH"

# Error codes determinísticos — v1.0.6 (novos gates)
E_DUPLICATE_IDS = "E_DUPLICATE_IDS"
E_AR_COLLISION = "E_AR_COLLISION"
E_ROLLBACK_MISSING = "E_ROLLBACK_MISSING"
E_ROLLBACK_INVALID = "E_ROLLBACK_INVALID"
E_AR_MATERIALIZE = "E_AR_MATERIALIZE"
E_AR_ZERO_BYTES = "E_AR_ZERO_BYTES"

# ========== UTILS ==========
def get_repo_root() -> Path:
    """Retorna o root do repo (assume que hb_cli.py está em scripts/run/)."""
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
    """Converte título em slug simples (Windows-safe)."""
    # Remove/substitui caracteres problemáticos no Windows: : * ? " < > | ( ) —
    text = text.replace(":", "").replace("—", "-").replace("(", "").replace(")", "")
    text = re.sub(r'[*?"<>|]', '', text)
    text = text.lower().replace(" ", "_").replace("/", "_")
    return text[:50]


# ========== GATE 2: IDs ÚNICOS NO PLAN ==========
def validate_unique_ids(plan_data: Dict) -> None:
    """
    GATE 2: Valida que não existem IDs duplicados dentro do plan JSON.
    Falha com E_DUPLICATE_IDS se detectar IDs repetidos.
    """
    task_ids = [task["id"] for task in plan_data["tasks"]]
    id_counts = Counter(task_ids)
    duplicates = {tid: count for tid, count in id_counts.items() if count > 1}

    if duplicates:
        dup_str = ", ".join(f"ID '{tid}' aparece {count}x" for tid, count in duplicates.items())
        fail(E_DUPLICATE_IDS,
             f"IDs duplicados detectados no plan JSON: {dup_str}.\n"
             f"Cada task MUST ter um ID único no formato 001..999.",
             exit_code=2)


# ========== GATE 2.5: ROLLBACK OBRIGATÓRIO PARA ARs DE BANCO ==========
def _is_db_task(task: Dict) -> bool:
    """Detecta se uma task modifica banco usando 3 critérios."""
    ssot_touches = task.get("ssot_touches", [])
    validation_cmd = task.get("validation_command", "").lower()
    description = task.get("description", "").lower()

    # Critério 1: ssot_touches contém SSOT de banco
    touches_db = any(ssot in ssot_touches for ssot in DB_SSOT_FILES)

    # Critério 2: validation_command menciona banco
    mentions_db = any(kw in validation_cmd for kw in DB_KEYWORDS_CMD)

    # Critério 3: description menciona migration/DDL
    describes_db = any(kw in description for kw in DB_KEYWORDS_DESC)

    return touches_db or mentions_db or describes_db


def validate_rollback_mandatory(plan_data: Dict) -> None:
    """
    GATE 2.5: Valida que toda task de banco possui rollback_plan com comandos válidos.
    Falha com E_ROLLBACK_MISSING ou E_ROLLBACK_INVALID.
    """
    for task in plan_data["tasks"]:
        task_id = task["id"]
        rollback_plan = task.get("rollback_plan", "").strip()

        if not _is_db_task(task):
            continue

        # Task de banco sem rollback_plan → FAIL
        if not rollback_plan:
            ssot_touches = task.get("ssot_touches", [])
            fail(E_ROLLBACK_MISSING,
                 f"Task {task_id} modifica banco mas NÃO possui 'rollback_plan'.\n"
                 f"Detecção: ssot_touches={ssot_touches}, "
                 f"description contém keywords de banco.\n"
                 f"Adicione 'rollback_plan' com comandos exatos "
                 f"(ex: 'alembic downgrade -1').",
                 exit_code=2)

        # rollback_plan sem comandos válidos → FAIL
        has_valid_cmd = any(
            pattern.lower() in rollback_plan.lower()
            for pattern in VALID_ROLLBACK_PATTERNS
        )
        if not has_valid_cmd:
            fail(E_ROLLBACK_INVALID,
                 f"Task {task_id}: rollback_plan não contém comandos válidos.\n"
                 f"Conteúdo: '{rollback_plan[:100]}...'\n"
                 f"Padrões aceitos: {VALID_ROLLBACK_PATTERNS}",
                 exit_code=2)


# ========== GATE 3: COLISÃO COM DISCO ==========
def check_ar_collision(ar_dir: Path, task_id: str, ar_filename: str,
                       mode: str = "default") -> Optional[str]:
    """
    GATE 3: Verifica se AR com mesmo ID já existe no disco.

    Args:
        mode: "default" → falha, "force" → sobrescreve, "skip" → pula

    Returns:
        "skip" se deve pular, None se pode prosseguir.
    """
    existing = list(ar_dir.glob(f"AR_{task_id}_*.md"))

    if not existing:
        return None  # Sem colisão

    existing_names = [f.name for f in existing]

    if mode == "skip":
        print(f"⏭️  SKIP: AR_{task_id} já existe ({existing_names[0]}), pulando.")
        return "skip"

    if mode == "force":
        for f in existing:
            f.unlink()
        print(f"🔄 FORCE: AR_{task_id} existente removido, será reescrito.")
        return None

    if mode == "dry-force":
        print(f"🔄 DRY-FORCE: AR_{task_id} existente seria sobrescrito.")
        return None

    # mode == "default" → FAIL
    fail(E_AR_COLLISION,
         f"AR_{task_id} já existe no disco: {existing_names}.\n"
         f"Opções:\n"
         f"  --force          → sobrescrever ARs existentes\n"
         f"  --skip-existing  → pular ARs que já existem\n"
         f"  --dry-run        → simular sem criar arquivos",
         exit_code=2)
    return None  # unreachable, mas satisfaz type checker


# ========== GATE 4+5: ESCRITA ATÔMICA + PÓS-VALIDAÇÃO ==========
def build_ar_content(task: Dict, protocol_version: str) -> str:
    """Constrói conteúdo completo do AR em memória (string)."""
    task_id = task["id"]
    title = task["title"]
    description = task["description"]
    criteria = task["criteria"]
    validation_cmd = task["validation_command"]
    evidence_file = task["evidence_file"]
    ssot_touches = task.get("ssot_touches", [])
    notes = task.get("notes", "")
    risks = task.get("risks", [])
    rollback_plan = task.get("rollback_plan", "")

    lines: List[str] = []
    lines.append(f"# AR_{task_id} — {title}\n\n")
    lines.append(f"**Status**: DRAFT\n")
    lines.append(f"**Versão do Protocolo**: {protocol_version}\n\n")

    lines.append(f"## Descrição\n{description}\n\n")
    lines.append(f"## Critérios de Aceite\n{criteria}\n\n")

    if ssot_touches:
        lines.append("## SSOT Touches\n")
        for ssot in ssot_touches:
            lines.append(f"- [ ] {ssot}\n")
        lines.append("\n")

    lines.append(f"## Validation Command (Contrato)\n```\n{validation_cmd}\n```\n\n")
    lines.append(f"## Evidence File (Contrato)\n`{evidence_file}`\n\n")

    if rollback_plan:
        lines.append(f"## Rollback Plan (Contrato)\n```\n{rollback_plan}\n```\n")
        lines.append(f"⚠️ **ATENÇÃO**: Este AR modifica banco. Execute rollback em caso de falha.\n\n")

    if notes:
        lines.append(f"## Notas do Arquiteto\n{notes}\n\n")

    if risks:
        lines.append("## Riscos\n")
        for risk in risks:
            lines.append(f"- {risk}\n")
        lines.append("\n")

    lines.append("## Análise de Impacto\n_(A ser preenchido pelo Executor)_\n\n")
    lines.append("---\n## Carimbo de Execução\n_(Gerado por hb report)_\n\n")

    return "".join(lines)


def materialize_ar_atomic(ar_dir: Path, ar_path: Path, content: str,
                          task_id: str) -> None:
    """
    GATE 4+5: Materializa AR de forma atômica com pós-validação.

    1. Escreve em .tmp/ (não contamina ars/)
    2. Valida tamanho mínimo (anti-zero-bytes)
    3. Valida header obrigatório
    4. Valida encoding UTF-8
    5. Move atômico para destino final
    """
    tmp_dir = ar_dir / ".tmp"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    tmp_path = tmp_dir / ar_path.name

    try:
        # 1) Escrita em área temporária
        with open(tmp_path, "w", encoding="utf-8") as f:
            f.write(content)

        # 2) Validação de tamanho mínimo (anti-zero-bytes)
        file_size = tmp_path.stat().st_size
        if file_size < MIN_AR_SIZE_BYTES:
            raise ValueError(
                f"AR_{task_id} tem apenas {file_size} bytes "
                f"(mínimo: {MIN_AR_SIZE_BYTES}). "
                f"Possível falha de escrita ou slug inválido."
            )

        # 3) Validação de header obrigatório
        with open(tmp_path, "r", encoding="utf-8") as f:
            first_line = f.readline().strip()
        expected_prefix = f"# AR_{task_id}"
        if not first_line.startswith(expected_prefix):
            raise ValueError(
                f"Header inválido: esperado '{expected_prefix}...', "
                f"encontrado '{first_line[:60]}'"
            )

        # 4) Validação de encoding UTF-8 (leitura completa)
        with open(tmp_path, "r", encoding="utf-8") as f:
            full_content = f.read()
        if len(full_content) == 0:
            raise ValueError("Arquivo vazio após leitura UTF-8")

        # 5) Move atômico para destino final
        tmp_path.replace(ar_path)

    except Exception as e:
        # Cleanup: remove tmp se falhar
        if tmp_path.exists():
            tmp_path.unlink()
        raise ValueError(f"Falha na materialização de AR_{task_id}: {e}")
    finally:
        # Limpar diretório .tmp/ se vazio
        try:
            if tmp_dir.exists() and not any(tmp_dir.iterdir()):
                tmp_dir.rmdir()
        except OSError:
            pass


def rollback_created_ars(ar_dir: Path, created_ars: List[str]) -> None:
    """Remove ARs já criados em caso de falha (rollback atômico)."""
    for ar_name in created_ars:
        ar_path = ar_dir / ar_name
        if ar_path.exists():
            ar_path.unlink()
            print(f"   🗑️ Rollback: removido {ar_name}", file=sys.stderr)

# ========== COMANDOS ==========
def cmd_version() -> None:
    """Comando: hb version"""
    print(f"HB Track Protocol v{HB_PROTOCOL_VERSION}")
    sys.exit(0)

def cmd_plan(plan_path: str, collision_mode: str = "default",
             dry_run: bool = False) -> None:
    """
    Comando: hb plan <plan_json_path> [--force|--skip-existing] [--dry-run]

    Pipeline de validação:
      P1: Path dentro de PLANS_DIR
      P2: JSON parseável
      P3: Schema validation (jsonschema)
      P4: Versão do protocolo
      GATE 2: IDs únicos no plan
      GATE 2.5: Rollback obrigatório para ARs de banco
      P6: Coerência id ↔ evidence_file
      GATE 3: Colisão com ARs existentes no disco
      GATE 4+5: Escrita atômica + pós-validação anti-zero-bytes
    """
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
             f"Plan version '{plan_data.get('version')}' != "
             f"protocol version '{HB_PROTOCOL_VERSION}'")

    # ===== GATE 2: IDs únicos no plan =====
    validate_unique_ids(plan_data)

    # ===== GATE 2.5: Rollback obrigatório para ARs de banco =====
    validate_rollback_mandatory(plan_data)

    # Materializar ARs
    ar_dir = repo_root / AR_DIR
    ar_dir.mkdir(parents=True, exist_ok=True)

    created_ars: List[str] = []
    skipped_ars: List[str] = []

    for task in plan_data["tasks"]:
        task_id = task["id"]
        title = task["title"]
        evidence_file = task["evidence_file"]

        # P6: coerência id ↔ evidence_file
        if f"AR_{task_id}" not in evidence_file:
            rollback_created_ars(ar_dir, created_ars)
            fail(E_TASK_EVIDENCE_ID_MISMATCH,
                 f"Task {task_id}: evidence_file must contain "
                 f"'AR_{task_id}' (got: {evidence_file})")

        # Gerar slug e filename
        slug = slugify(title)
        ar_filename = f"AR_{task_id}_{slug}.md"
        ar_path = ar_dir / ar_filename

        # ===== GATE 3: Colisão com disco =====
        # Em dry-run, não executar ações destrutivas (force delete)
        effective_collision_mode = collision_mode
        if dry_run and collision_mode == "force":
            effective_collision_mode = "dry-force"  # simular force sem deletar

        collision_result = check_ar_collision(
            ar_dir, task_id, ar_filename, mode=effective_collision_mode
        )
        if collision_result == "skip":
            skipped_ars.append(ar_filename)
            continue

        # Construir conteúdo em memória
        ar_content = build_ar_content(task, HB_PROTOCOL_VERSION)

        if dry_run:
            # DRY-RUN: validar sem criar arquivos
            content_size = len(ar_content.encode("utf-8"))
            is_db = _is_db_task(task)
            has_rollback = bool(task.get("rollback_plan", "").strip())
            print(f"   📋 AR_{task_id}_{slug}.md "
                  f"({content_size} bytes) "
                  f"{'[DB]' if is_db else ''} "
                  f"{'[ROLLBACK ✓]' if has_rollback else ''}")
            created_ars.append(ar_filename)
            continue

        # ===== GATE 4+5: Escrita atômica + pós-validação =====
        try:
            materialize_ar_atomic(ar_dir, ar_path, ar_content, task_id)
            created_ars.append(ar_filename)
        except ValueError as e:
            # Rollback: remover ARs já criados
            rollback_created_ars(ar_dir, created_ars)
            fail(E_AR_MATERIALIZE,
                 f"{e}\nRollback executado: {len(created_ars)} ARs removidos.",
                 exit_code=2)

    # Resultado final
    if dry_run:
        print(f"\n🔍 DRY-RUN: {len(created_ars)} ARs seriam criados, "
              f"{len(skipped_ars)} seriam pulados. "
              f"Todas as validações passaram.")
    else:
        print(f"✅ Plan materialized successfully:")
        for ar in created_ars:
            print(f"   - {AR_DIR}/{ar}")
        if skipped_ars:
            print(f"⏭️  Skipped ({len(skipped_ars)}):")
            for ar in skipped_ars:
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
        print("Commands: version | plan <path> [--force|--skip-existing] [--dry-run]")
        print("          report <id> \"<cmd>\" | check --mode <mode>")
        sys.exit(1)

    command = sys.argv[1]

    if command == "version":
        cmd_version()

    elif command == "plan":
        if len(sys.argv) < 3:
            fail("E_USAGE", "Usage: hb plan <plan_json_path> "
                 "[--force|--skip-existing] [--dry-run]")

        # Parse flags
        args = sys.argv[2:]
        plan_path = None
        collision_mode = "default"
        dry_run = False

        for arg in args:
            if arg == "--force":
                collision_mode = "force"
            elif arg == "--skip-existing":
                collision_mode = "skip"
            elif arg == "--dry-run":
                dry_run = True
            elif plan_path is None:
                plan_path = arg
            else:
                fail("E_USAGE", f"Argumento inesperado: {arg}")

        if plan_path is None:
            fail("E_USAGE", "Plan path é obrigatório.")

        cmd_plan(plan_path, collision_mode=collision_mode, dry_run=dry_run)

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

