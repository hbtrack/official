#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HB Track CLI — scripts/run/hb_cli.py (Entrypoint Oficial)
Versão: v1.2.0
SSOT: docs/_canon/specs/Hb cli.md
Contrato: docs/_canon/contratos/Dev Flow.md
Schema: docs/_canon/contratos/ar_contract.schema.json

Changelog v1.0.8:
  - AR_010: hb report atualiza campo **Status** no header da AR
  - AR_011: rebuild automático de docs/hbtrack/_INDEX.md
  - AR_012: hb check com sync obrigatório do _INDEX + imutabilidade de AR SUCESSO
  - AR_020: hb verify (Testador), C3 version-aware (VERIFICADO para v1.0.8+)

Changelog v1.1.0:
  - AR_023: GATE P3.5 anti-trivial em hb plan, triple-run (3x) em hb verify, bump v1.1.0

Changelog v1.2.0:
  - AR_051: GATES_REGISTRY_PATH — path canônico docs/_canon/specs/GATES_REGISTRY.yaml
  - AR_051: cmd_gates_list() — lista gates ativos do registry
  - AR_051: cmd_gates_check(gate_id) — verifica gate específico por id
  - AR_055: check_retry_limit() agora chamada em cmd_plan() (gate ativo)
  - AR_055: Kanban write real via _write_kanban() em update_kanban_and_status()

Changelog v1.2.1 (patch — auto-dispatch autônomo):
  - check_workspace_clean(): migrado de git status --porcelain para git diff --name-only
    Semântica: mudanças STAGED (Executor) são PERMITIDAS; apenas unstaged tracked blocked.
    Permite hb verify com evidence staged (requisito do fluxo de 3 agentes autônomos).
  - hb_autotest.py: novo daemon Testador (scripts/run/hb_autotest.py v1.0.0)
  - hb_watch.py: bump v1.2.2 — rich JSON context dispatch (_reports/dispatch/<mode>_context.json)
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
HB_PROTOCOL_VERSION = "1.3.0"

# Paths canônicos (relativos à raiz do repo)
PLANS_DIR = "docs/_canon/planos"
AR_DIR = "docs/hbtrack/ars"
EV_DIR = "docs/hbtrack/evidence"
TESTADOR_DIR = "_reports/testador"
SSOT_FILES = [
    "docs/ssot/schema.sql",
    "docs/ssot/openapi.json",
    "docs/ssot/alembic_state.txt"
]
SCHEMA_PATH = "docs/_canon/contratos/ar_contract.schema.json"
KANBAN_PATH = "docs/hbtrack/Hb Track Kanban.md"  # AR_055: Kanban write target
GATES_REGISTRY_PATH = "docs/_canon/specs/GATES_REGISTRY.yaml"  # AR_051: Gates registry
GOVERNED_ROOTS_SPEC_PATH = "docs/_canon/specs/GOVERNED_ROOTS.yaml"

# SSOT files que indicam alteração de banco
DB_SSOT_FILES = ["docs/ssot/schema.sql", "docs/ssot/alembic_state.txt"]

# Keywords que indicam task de banco (lowercase para matching)
DB_KEYWORDS_CMD = ["alembic", "migration", "psql", "sql"]
DB_KEYWORDS_DESC = ["migration", "add column", "drop column", "alter table",
                    "create table", "drop table", "create index", "drop index",
                    "foreign key", "downgrade"]

# Padrões válidos de rollback — REMOVIDO, substituído por whitelist estrita linha por linha (I7/Q8)

# Tamanho mínimo de AR válido (bytes) — header + seções obrigatórias
MIN_AR_SIZE_BYTES = 200

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
E_VERIFY_NOT_READY = "E_VERIFY_NOT_READY"
E_VERIFY_NO_CMD = "E_VERIFY_NO_CMD"
E_VERIFY_REQUIRES_VERIFIED = "E_VERIFY_REQUIRES_VERIFIED"

# Error codes determinísticos — AR_012 (governança index + imutabilidade)
E_AR_INDEX_NOT_STAGED = "E_AR_INDEX_NOT_STAGED"
E_AR_IMMUTABLE = "E_AR_IMMUTABLE"

# Error codes determinísticos — v1.1.0 (triple-run + anti-trivial)
E_TRIVIAL_CMD = "E_TRIVIAL_CMD"
E_TRIPLE_FAIL = "E_TRIPLE_FAIL"
E_CLI_LOCKED = "E_CLI_LOCKED"

# Error codes determinísticos — v1.2.0 (SSOT loaders + seal)
E_DEP_PYYAML = "E_DEP_PYYAML"
E_SCHEMA_VERSION_MISSING = "E_SCHEMA_VERSION_MISSING"
E_SCHEMA_VERSION_INVALID = "E_SCHEMA_VERSION_INVALID"

E_GOVERNED_ROOTS_MISSING = "E_GOVERNED_ROOTS_MISSING"
E_GOVERNED_ROOTS_INVALID = "E_GOVERNED_ROOTS_INVALID"

E_EVIDENCE_PATH_FORBIDDEN = "E_EVIDENCE_PATH_FORBIDDEN"
E_EVIDENCE_MISSING = "E_EVIDENCE_MISSING"

# Error codes determinísticos — write_scope pipeline (GAP-001)
E_WRITE_SCOPE_MISSING = "E_WRITE_SCOPE_MISSING"
E_WRITE_SCOPE_FORBIDDEN = "E_WRITE_SCOPE_FORBIDDEN"

E_VERIFY_DIRTY_WORKSPACE = "E_VERIFY_DIRTY_WORKSPACE"

E_TESTADOR_REPORT_NOT_STAGED = "E_TESTADOR_REPORT_NOT_STAGED"

E_SEAL_NOT_READY = "E_SEAL_NOT_READY"
E_SEAL_MISSING_TESTADOR_REPORT = "E_SEAL_MISSING_TESTADOR_REPORT"
E_SEAL_REPORT_NOT_STAGED = "E_SEAL_REPORT_NOT_STAGED"
E_SEAL_EVIDENCE_NOT_STAGED = "E_SEAL_EVIDENCE_NOT_STAGED"

# ========== ANTI-TRIVIAL GATE (GATE P3.5) ==========
TRIPLE_RUN_COUNT = 3
MAX_RETRY_THRESHOLD = 3  # Limite de "bate e volta" entre Executor e Testador

TRIVIAL_PATTERNS = [
    r"^\s*echo\s",
    r"^\s*true\s*$",
    r"^\s*exit\s+0\s*$",
    r"^\s*:\s*$",
]

ASSERTION_KEYWORDS = ["assert ", "pytest", "unittest", "-c ", "verify", "check", "validate"]
MIN_NONTRIVIAL_LEN = 30


def is_trivial_command(cmd: str) -> Tuple[bool, str]:
    """Retorna (True, reason) se o validation_command for trivialmente passável."""
    cmd_s = cmd.strip()
    for pat in TRIVIAL_PATTERNS:
        if re.match(pat, cmd_s, re.IGNORECASE):
            return True, f"matches trivial pattern: {pat}"
    has_kw = any(kw in cmd_s for kw in ASSERTION_KEYWORDS)
    if not has_kw and len(cmd_s) < MIN_NONTRIVIAL_LEN:
        return True, f"sem assertion keyword e curto ({len(cmd_s)} < {MIN_NONTRIVIAL_LEN})"
    return False, ""


# ========== GATE AR_035: RETRY LIMIT ==========

def check_retry_limit(ar_data: Dict) -> None:
    """
    GATE AR_035: Impede a execução se a AR entrou em loop de erro.
    """
    retries = ar_data.get("retry_count", 0)
    if retries >= MAX_RETRY_THRESHOLD:
        ar_id = ar_data.get("id", "??")
        fail(E_CLI_LOCKED,
             f"AR_{ar_id} atingiu o limite de {MAX_RETRY_THRESHOLD} tentativas.\n"
             f"Causa provável: Requisitos ambíguos ou bug persistente.\n"
             f"AÇÃO REQUERIDA: Intervenção humana necessária para resetar 'retry_count'.",
             exit_code=5)


# ========== GATE I8 HELPER: FILE IN GIT ==========

def is_file_in_git(file_path: str, staged_files: List[str]) -> bool:
    """
    Verifica se arquivo está staged OU já commitado no repo.
    Resolve bug do gate I8: relatórios commitados devem ser aceitos.
    """
    if file_path in staged_files:
        return True
    # Verificar se arquivo já está commitado
    ret, _, _ = run_cmd(f"git ls-files --error-unmatch {file_path}")
    return ret == 0


# ========== HBLock: CONCURRENCY LOCK (AR_028) ==========
LOCK_FILE = ".hb_lock"


class HBLock:
    """File-based atomic lock para operações de escrita do hb_cli.
    Impede corrida concorrente entre Arquiteto, Executor e Testador.
    Implementação: AR_028.
    """
    MAX_RETRIES = 10
    MIN_WAIT = 0.1
    MAX_WAIT = 0.5

    def __init__(self):
        self.lock_path = get_repo_root() / LOCK_FILE
        self.pid = os.getpid()

    def __enter__(self):
        import random as _random
        import time as _time
        for attempt in range(self.MAX_RETRIES):
            try:
                fd = os.open(str(self.lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                with os.fdopen(fd, 'w') as f:
                    f.write(f'pid={self.pid}\ntimestamp={_time.time()}')
                return self
            except FileExistsError:
                wait = _random.uniform(self.MIN_WAIT, self.MAX_WAIT)
                _time.sleep(wait)
        fail(E_CLI_LOCKED,
             f'Lock file {self.lock_path} retido por outro agente após {self.MAX_RETRIES} tentativas.\n'
             f'Se o processo travou, remova manualmente: {self.lock_path}',
             exit_code=3)

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if self.lock_path.exists():
                self.lock_path.unlink()
        except Exception:
            pass
        return False


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
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return result.returncode, result.stdout, result.stderr

def slugify(text: str) -> str:
    """Converte título em slug simples (Windows-safe)."""
    # Remove/substitui caracteres problemáticos no Windows: : * ? " < > | ( ) —
    text = text.replace(":", "").replace("—", "-").replace("(", "").replace(")", "")
    text = re.sub(r'[*?"<>|]', '', text)
    text = text.lower().replace(" ", "_").replace("/", "_")
    return text[:50]


def _load_yaml_required(path: Path, err_missing: str, err_invalid: str) -> dict:
    """Carrega arquivo YAML SSOT obrigatório com validação."""
    if not path.exists():
        fail(err_missing, f"Arquivo SSOT ausente: {path.as_posix()}", exit_code=2)
    try:
        import yaml  # PyYAML
    except ImportError:
        fail(E_DEP_PYYAML, "PyYAML not found. Install via: pip install pyyaml", exit_code=3)
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception as e:
        fail(err_invalid, f"YAML inválido em {path.as_posix()}: {e}", exit_code=2)


def load_governed_roots(repo_root: Path) -> List[str]:
    """Carrega GOVERNED_ROOTS do SSOT YAML e valida."""
    spec_path = repo_root / GOVERNED_ROOTS_SPEC_PATH
    data = _load_yaml_required(spec_path, E_GOVERNED_ROOTS_MISSING, E_GOVERNED_ROOTS_INVALID)
    roots = data.get("roots")
    if not isinstance(roots, list) or not roots:
        fail(E_GOVERNED_ROOTS_INVALID,
             f"'roots' deve ser lista não-vazia em {GOVERNED_ROOTS_SPEC_PATH}",
             exit_code=2)
    norm: List[str] = []
    for r in roots:
        if not isinstance(r, str) or not r.strip():
            fail(E_GOVERNED_ROOTS_INVALID, f"Root inválida: {r!r}", exit_code=2)
        rr = r.strip().replace("\\", "/")
        if rr.startswith("/") or rr.startswith("../") or "/../" in rr:
            fail(E_GOVERNED_ROOTS_INVALID, f"Root proibida (path traversal/absoluto): {rr}", exit_code=2)
        if not rr.endswith("/"):
            rr += "/"
        norm.append(rr)
    return norm


def load_schema_version(schema: dict) -> str:
    """Extrai schema_version do schema JSON com validação."""
    v = schema.get("schema_version")
    if not isinstance(v, str) or not v.strip():
        fail(E_SCHEMA_VERSION_MISSING,
             "Schema sem 'schema_version' (string) em docs/_canon/contratos/ar_contract.schema.json",
             exit_code=2)
    return v.strip()


def _norm_newlines(s: str) -> str:
    """Normaliza newlines (CRLF→LF, CR→LF)."""
    return (s or "").replace("\r\n", "\n").replace("\r", "\n")


def compute_behavior_hash(exit_code: int, stdout: str, stderr: str) -> str:
    """Hash canônico (SHA-256) de exit_code + stdout_norm + stderr_norm."""
    import hashlib
    payload = f"{exit_code}\n{_norm_newlines(stdout)}\n---STDERR---\n{_norm_newlines(stderr)}"
    return hashlib.sha256(payload.encode("utf-8", errors="replace")).hexdigest()


def expected_executor_evidence_path(ar_id: str) -> str:
    """Retorna path determinístico do evidence do Executor."""
    return f"{EV_DIR}/AR_{ar_id}/executor_main.log"


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


def _is_safe_rel_path(p: str) -> bool:
    """Bloqueia absoluto / traversal óbvio. Regra mínima anti-efeito-colateral."""
    p = (p or "").strip().replace("\\", "/")
    if not p:
        return False
    if p.startswith("/") or re.match(r"^[A-Za-z]:/", p):
        return False
    if p.startswith("../") or "/../" in p or p == "..":
        return False
    return True


def _allowed_rollback_line(line: str) -> Tuple[bool, str]:
    """
    I7/Q8 whitelist estrita por linha:
      1) python scripts/run/hb_cli.py ...
      2) git checkout -- <file>
      3) git clean -fd <dir>
      4) psql -c "TRUNCATE..."
    """
    s = (line or "").strip()
    if not s:
        return False, "linha vazia não permitida"

    # 1) python scripts/run/hb_cli.py ...
    if re.match(r"^python\s+scripts/run/hb_cli\.py(\s+.+)?$", s):
        return True, "hb_cli"

    # 2) git checkout -- <file>
    m = re.match(r"^git\s+checkout\s+--\s+(.+)$", s)
    if m:
        path = m.group(1).strip()
        if not _is_safe_rel_path(path):
            return False, f"git checkout path inseguro: {path!r}"
        return True, "git checkout"

    # 3) git clean -fd <dir>
    m = re.match(r"^git\s+clean\s+-fd\s+(.+)$", s)
    if m:
        path = m.group(1).strip()
        if not _is_safe_rel_path(path):
            return False, f"git clean dir inseguro: {path!r}"
        return True, "git clean"

    # 4) psql -c "TRUNCATE..."
    if re.match(r"^psql\s+-c\s+\"TRUNCATE[^\"]*\"$", s):
        return True, "psql truncate"

    return False, "fora da whitelist"


def validate_rollback_mandatory(plan_data: Dict) -> None:
    """
    GATE 2.5 (I7/Q8): Toda task de banco MUST ter rollback_plan com comandos na whitelist estrita.
    Multi-linha permitida (1 comando por linha). Linhas vazias são proibidas.
    """
    for task in plan_data["tasks"]:
        task_id = task["id"]
        rollback_plan = (task.get("rollback_plan") or "").strip()

        if not _is_db_task(task):
            continue

        if not rollback_plan:
            ssot_touches = task.get("ssot_touches", [])
            fail(E_ROLLBACK_MISSING,
                 f"Task {task_id} modifica banco mas NÃO possui 'rollback_plan'.\n"
                 f"Detecção: ssot_touches={ssot_touches} / keywords.\n"
                 f"Whitelist permitida:\n"
                 f"  - python scripts/run/hb_cli.py ...\n"
                 f"  - git checkout -- <file>\n"
                 f"  - git clean -fd <dir>\n"
                 f"  - psql -c \"TRUNCATE...\" (somente staging/test)\n",
                 exit_code=2)

        lines = rollback_plan.splitlines()
        for idx, line in enumerate(lines, start=1):
            ok, why = _allowed_rollback_line(line)
            if not ok:
                fail(E_ROLLBACK_INVALID,
                     f"Task {task_id}: rollback_plan contém comando inválido na linha {idx}.\n"
                     f"Linha: {line!r}\n"
                     f"Motivo: {why}\n"
                     f"Whitelist permitida:\n"
                     f"  - python scripts/run/hb_cli.py ...\n"
                     f"  - git checkout -- <file>\n"
                     f"  - git clean -fd <dir>\n"
                     f"  - psql -c \"TRUNCATE...\" (somente staging/test)\n",
                     exit_code=2)


# ========== GATE 3: COLISÃO COM DISCO ==========
def check_ar_collision(ar_dir: Path, task_id: str, ar_filename: str,
                       mode: str = "default") -> Optional[str]:
    """
    GATE 3: Verifica se AR com mesmo ID já existe no disco (recursivo).

    Args:
        mode: "default" → falha, "force" → sobrescreve, "skip" → pula

    Returns:
        "skip" se deve pular, None se pode prosseguir.
    """
    existing = list(ar_dir.rglob(f"AR_{task_id}_*.md"))

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


def _get_ar_subdir(plan_basename: str) -> str:
    """Retorna o subdiretório de AR baseado no domínio do plano."""
    if plan_basename.startswith(('comp_db_', 'competition')):
        return 'competitions'
    if plan_basename.startswith(('gov_', 'AR_GOV')):
        return 'governance'
    if plan_basename.startswith('infra_'):
        return 'infra'
    return 'features'


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
    lines.append(f"**Status**: 🔲 PENDENTE\n")
    lines.append(f"**Versão do Protocolo**: {protocol_version}\n\n")

    lines.append(f"## Descrição\n{description}\n\n")
    lines.append(f"## Critérios de Aceite\n{criteria}\n\n")

    # Write Scope (opcional, mas obrigatório para código via GATE P3.6)
    write_scope = task.get("write_scope", [])
    if write_scope:
        lines.append("## Write Scope\n")
        for ws in write_scope:
            lines.append(f"- {ws}\n")
        lines.append("\n")

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

    1. Escreve em .tmp/ (relativo ao subdiretório da AR)
    2. Valida tamanho mínimo (anti-zero-bytes)
    3. Valida header obrigatório
    4. Valida encoding UTF-8
    5. Move atômico para destino final
    """
    tmp_dir = ar_path.parent / ".tmp"
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
    """Remove ARs já criados em caso de falha (rollback atômico).
    Varre recursivamente para garantir remoção em subdirs.
    """
    for ar_name in created_ars:
        found = list(ar_dir.rglob(ar_name))
        for ar_path in found:
            if ar_path.exists():
                ar_path.unlink()
                print(f"   🗑️ Rollback: removido {ar_name}", file=sys.stderr)

# ========== INDEX AUTO-REBUILD ==========
def rebuild_ar_index(repo_root: Path) -> None:
    """
    Auto-gera docs/hbtrack/_INDEX.md com tabela de todas as ARs.
    Chamado ao final de cmd_plan e cmd_report.
    """
    from datetime import date
    ar_dir = repo_root / AR_DIR
    index_path = repo_root / "docs/hbtrack/_INDEX.md"

    # Scanear AR_*.md (excluir _INDEX.md) usando rglob para subdirs
    ar_files = [
        f for f in ar_dir.rglob("AR_*.md")
        if re.match(r"AR_[0-9]", f.name)
    ]

    # Ordenar por ID numérico
    def ar_sort_key(p: Path) -> int:
        m = re.search(r"AR_([0-9]+)", p.name)
        return int(m.group(1)) if m else 9999

    ar_files.sort(key=ar_sort_key)

    rows: List[str] = []
    for ar_path in ar_files:
        try:
            content = ar_path.read_text(encoding="utf-8")
        except Exception:
            continue

        # Extrair ID
        id_match = re.search(r"AR_([0-9]+(?:\.[0-9]+)?)", ar_path.name)
        ar_id = f"AR_{id_match.group(1)}" if id_match else ar_path.stem

        # Extrair título (linha # AR_NNN — ...)
        title_match = re.match(r"#\s+AR_[^\s—–-]+\s*[—–-]+?\s*(.+)", content)
        title = title_match.group(1).strip() if title_match else "(sem título)"
        if len(title) > 60:
            title = title[:57] + "..."

        # Extrair status (linha **Status**: ...)
        status_match = re.search(r"\*\*Status\*\*:\s*(.+)", content)
        status = status_match.group(1).strip() if status_match else "DESCONHECIDO"

        # Extrair evidence file
        ev_match = re.search(r"## Evidence File \(Contrato\)\n`(.+?)`", content)
        evidence = ev_match.group(1).strip() if ev_match else "—"

        rows.append(f"| {ar_id} | {title} | {status} | {evidence} |")

    today = date.today().isoformat()
    lines = [
        "# Índice de Architectural Records (ARs)",
        "> ⚠️ Auto-gerado por `hb plan`/`hb report`. NÃO editar manualmente.",
        f"> Última atualização: {today}",
        "",
        "| ID | Título | Status | Evidence |",
        "|---|---|---|---|",
    ] + rows + [""]

    index_path.write_text("\n".join(lines), encoding="utf-8")


# ========== COMANDOS ==========
def cmd_version() -> None:
    """Comando: hb version"""
    print(f"HB Track Protocol v{HB_PROTOCOL_VERSION}")
    sys.exit(0)


def _load_gates_registry(repo_root: Path) -> Optional[dict]:
    """AR_051: Carrega GATES_REGISTRY.yaml. Retorna None se ausente (soft fail)."""
    registry_path = repo_root / GATES_REGISTRY_PATH
    if not registry_path.exists():
        return None
    try:
        import yaml  # PyYAML — disponível no venv
        return yaml.safe_load(registry_path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"⚠️  GATES_REGISTRY.yaml parse error (non-fatal): {e}")
        return None


def cmd_gates_list() -> None:
    """Comando: hb gates list — lista gates do GATES_REGISTRY.yaml"""
    repo_root = get_repo_root()
    registry = _load_gates_registry(repo_root)
    if registry is None:
        fail("E_GATES_REGISTRY_MISSING",
             f"GATES_REGISTRY.yaml não encontrado em {GATES_REGISTRY_PATH}", exit_code=2)
    gates = registry.get("gates", [])
    version = registry.get("version", "?")
    print(f"🔒 GATES_REGISTRY v{version} — {len(gates)} gates:")
    print()
    for g in gates:
        lifecycle = g.get("lifecycle", "?")
        gid = g.get("id", "?")
        name = g.get("name", "?")
        icon = "✅" if lifecycle == "ACTIVE" else ("⚠️" if lifecycle == "CONDITIONAL" else "❌")
        print(f"  {icon} [{lifecycle}] {gid} — {name}")
    print()
    active = sum(1 for g in gates if g.get("lifecycle") == "ACTIVE")
    print(f"Total: {len(gates)} gates | ACTIVE: {active}")
    sys.exit(0)


def cmd_gates_check(gate_id: str) -> None:
    """Comando: hb gates check <id> — exibe detalhes de um gate específico"""
    repo_root = get_repo_root()
    registry = _load_gates_registry(repo_root)
    if registry is None:
        fail("E_GATES_REGISTRY_MISSING",
             f"GATES_REGISTRY.yaml não encontrado em {GATES_REGISTRY_PATH}", exit_code=2)
    gates = registry.get("gates", [])
    gate = next((g for g in gates if g.get("id") == gate_id), None)
    if gate is None:
        fail("E_GATE_NOT_FOUND",
             f"Gate '{gate_id}' não encontrado no registry. Use 'hb gates list' para ver ids válidos.",
             exit_code=2)
    print(f"🔒 Gate: {gate.get('id')}")
    print(f"   Name      : {gate.get('name', '?')}")
    print(f"   Class     : {gate.get('class', '?')}")
    print(f"   Lifecycle : {gate.get('lifecycle', '?')}")
    proofs = gate.get("required_proofs", {})
    if proofs:
        if isinstance(proofs, dict):
            print(f"   Proofs ({len(proofs)}):")
            for proof_type, proof_desc in proofs.items():
                print(f"     - [{proof_type}] {proof_desc}")
        elif isinstance(proofs, list):
            print(f"   Proofs ({len(proofs)}):")
            for p in proofs:
                print(f"     - {p}")
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

    # P4: validar versão do plano (SEPARADA do protocolo) — I2
    schema_version = schema.get("schema_version")
    if not isinstance(schema_version, str) or not schema_version.strip():
        fail(E_SCHEMA_VERSION_MISSING,
             f"Schema sem 'schema_version' válido em {SCHEMA_PATH}",
             exit_code=2)

    schema_version = schema_version.strip()
    if not re.match(r"^[0-9]+\.[0-9]+\.[0-9]+$", schema_version):
        fail(E_SCHEMA_VERSION_INVALID,
             f"schema_version inválido no schema: '{schema_version}'",
             exit_code=2)

    if plan_data.get("version") != schema_version:
        fail(E_PLAN_VERSION_MISMATCH,
             f"Plan version '{plan_data.get('version')}' != schema_version '{schema_version}'")

    # ===== GATE P3.5: Anti-trivial validation_command =====
    for task in plan_data.get("tasks", []):
        vcmd = task.get("validation_command", "").strip()
        if vcmd:
            trivial, reason = is_trivial_command(vcmd)
            if trivial:
                fail(E_TRIVIAL_CMD,
                     f"Task {task['id']}: validation_command é trivial ({reason}).\n"
                     f"  Cmd: {vcmd[:80]}\n"
                     f"  Use assertions reais: pytest, python -c 'assert...', etc.",
                     exit_code=2)

    # ===== GATE P3.6: write_scope obrigatório para governed roots =====
    governed_roots = load_governed_roots(repo_root)
    
    for task in plan_data.get("tasks", []):
        task_id = task["id"]
        ws = task.get("write_scope", [])
        desc = task.get("description", "").lower()
        title = task.get("title", "").lower()
        
        # Heurística: detecta tasks de código
        touches_code = any(
            keyword in desc or keyword in title 
            for keyword in ["backend", "frontend", "script", "model", "router", "service", 
                           ".py", ".ts", ".tsx", "alembic", "migration", "endpoint"]
        )
        
        if touches_code and not ws:
            fail(E_WRITE_SCOPE_MISSING,
                 f"Task {task_id}: write_scope obrigatório para tasks de código.\n"
                 f"  Title: {task['title'][:60]}\n"
                 f"  Defina explicitamente os paths que podem ser modificados.",
                 exit_code=2)
        
        # Validar que write_scope não contém paths fora de governed roots (se houver)
        if ws:
            for path in ws:
                # Normalizar: remover leading/trailing /
                norm_path = path.strip().strip("/")
                # Verificar se está em governed root OU em docs/_canon OU em scripts/ (governança)
                is_governed = any(norm_path.startswith(root.strip("/")) for root in governed_roots)
                is_canon = norm_path.startswith("docs/_canon")
                is_scripts = norm_path.startswith("scripts/")
                
                if not (is_governed or is_canon or is_scripts):
                    fail(E_WRITE_SCOPE_FORBIDDEN,
                         f"Task {task_id}: write_scope contém path fora de governed roots:\n"
                         f"  Path: {path}\n"
                         f"  Governed roots: {governed_roots}\n"
                         f"  Permitido: governed roots, docs/_canon/, scripts/",
                         exit_code=2)

    # ===== GATE 2: IDs únicos no plan =====
    validate_unique_ids(plan_data)

    # ===== GATE 2.5: Rollback obrigatório para ARs de banco =====
    validate_rollback_mandatory(plan_data)

    # Materializar ARs
    ar_dir = repo_root / AR_DIR
    ar_dir.mkdir(parents=True, exist_ok=True)

    created_ars: List[str] = []
    skipped_ars: List[str] = []

    with HBLock():
        for task in plan_data["tasks"]:
            task_id = task["id"]
            title = task["title"]

            # I11: Evidence path determinístico (Arquiteto não escolhe path arbitrário)
            expected_ev = expected_executor_evidence_path(task_id)
            provided_ev = (task.get("evidence_file") or "").strip()
            if provided_ev and provided_ev != expected_ev:
                fail(E_EVIDENCE_PATH_FORBIDDEN,
                     f"Task {task_id}: evidence_file proibido.\n"
                     f"Expected: {expected_ev}\nGot     : {provided_ev}",
                     exit_code=2)
            task["evidence_file"] = expected_ev
            evidence_file = expected_ev

            # Gerar slug e filename
            slug = slugify(title)
            ar_filename = f"AR_{task_id}_{slug}.md"
            
            # Roteamento de subdiretório (AR_043)
            subdir = _get_ar_subdir(plan_file.name)
            target_dir = ar_dir / subdir
            target_dir.mkdir(parents=True, exist_ok=True)
            ar_path = target_dir / ar_filename

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

            # AR_055: GATE retry limit — bloqueia AR com retry_count >= MAX_RETRY_THRESHOLD
            check_retry_limit(task)

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

        # Resultado final (dentro do lock)
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
            rebuild_ar_index(repo_root)
    sys.exit(0)


# ========== EVIDENCE INTEGRITY (AR_029) ==========

def compute_governed_checksum(repo_root: Path, governed_roots: List[str], files: List[str]) -> Dict[str, str]:
    """SHA-256 dos arquivos governados fornecidos (paths relativos)."""
    import hashlib as _hl
    result: Dict[str, str] = {}
    for fpath in files:
        fp = (fpath or "").strip().replace("\\", "/")
        if not fp:
            continue
        if not any(fp.startswith(root) for root in governed_roots):
            continue
        try:
            content = (repo_root / fp).read_bytes()
            result[fp] = _hl.sha256(content).hexdigest()
        except FileNotFoundError:
            result[fp] = "DELETED"
    return result


def check_workspace_clean() -> Tuple[bool, str]:
    """Verifica se o workspace tem mudanças não-staged em arquivos rastreados.

    Semântica para operação autônoma (3 agentes):
    - Mudanças STAGED (trabalho do Executor) são PERMITIDAS — o Testador verifica exatamente esse estado.
    - Mudanças NÃO-STAGED em arquivos rastreados são PROIBIDAS — podem contaminar o validation_command.
    - Arquivos não-rastreados são ignorados — não afetam arquivos rastreados.

    Retorna (is_clean, status_summary).
    """
    try:
        # Checar apenas mudanças não-staged em arquivos rastreados (working tree vs index)
        out = subprocess.run(
            ['git', 'diff', '--name-only'],
            capture_output=True, text=True, encoding='utf-8'
        )
        lines = [l for l in out.stdout.strip().split('\n') if l.strip()]
        if not lines:
            return True, 'workspace_clean'
        return False, f'unstaged_modified={len(lines)}'
    except Exception as e:
        return False, f'git_error={e}'



def cmd_report(ar_id: str, command: str) -> None:
    """Comando: hb report <id> "<command>" """
    repo_root = get_repo_root()
    ar_dir = repo_root / AR_DIR
    
    # R1: localizar AR por prefixo (recursivo)
    ar_files = list(ar_dir.rglob(f"AR_{ar_id}_*.md"))
    if not ar_files:
        fail(E_AR_NOT_FOUND, f"AR with id {ar_id} not found in {AR_DIR}/", exit_code=2)
    
    ar_file = ar_files[0]
    
    # Ler AR para extrair contrato (validation command e evidence file)
    with open(ar_file, "r", encoding="utf-8") as f:
        ar_content = f.read()
    
    # Extrair validation command (entre ```...```)
    match = re.search(r"## Validation Command \(Contrato\)\n```\n(.+?)\n```", ar_content, re.DOTALL)
    declared_cmd = match.group(1).strip() if match else ""
    
    # R2: validar command match
    if declared_cmd and declared_cmd != command:
        fail(E_CMD_MISMATCH, 
             f"Command mismatch.\nDeclared: {declared_cmd}\nReceived: {command}", 
             exit_code=3)
    
    # Extrair Evidence File (Contrato) e aplicar I11: path determinístico
    match = re.search(r"## Evidence File \(Contrato\)\n`(.+?)`", ar_content)
    declared_ev = match.group(1).strip() if match else ""

    expected_ev = expected_executor_evidence_path(ar_id)

    # Evidence File é obrigatório e MUST ser determinístico (I11)
    if not declared_ev:
        fail("E_EVIDENCE_MISSING",
             f"AR_{ar_id} não declara Evidence File (Contrato). Expected: {expected_ev}",
             exit_code=2)

    # Normalizar separadores
    declared_ev_norm = declared_ev.replace("\\", "/")
    expected_ev_norm = expected_ev.replace("\\", "/")

    if declared_ev_norm != expected_ev_norm:
        fail(E_EVIDENCE_PATH_FORBIDDEN,
             f"AR_{ar_id}: Evidence File (Contrato) divergente do path determinístico.\n"
             f"Expected: {expected_ev_norm}\n"
             f"Got     : {declared_ev_norm}",
             exit_code=2)

    evidence_file_path = expected_ev_norm

    # Carregar governed_roots via YAML
    governed_roots = load_governed_roots(repo_root)
    
    # R3: executar comando
    print(f"🔄 Executing: {command}")
    exit_code, stdout, stderr = run_cmd(command)

    # timestamp UTC + hash canônico (I10)
    from datetime import datetime, timezone
    ts_utc = datetime.now(timezone.utc).isoformat()
    behavior_hash = compute_behavior_hash(exit_code, stdout, stderr)

    # Obter contexto git e Python
    git_head = run_cmd("git rev-parse HEAD")[1].strip() or "N/A"
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"

    # staged/dirty info
    ws_clean, ws_status = check_workspace_clean()

    # checksums dos arquivos governados tocados (staged + unstaged)
    _, d1, _ = run_cmd("git diff --name-only")
    _, d2, _ = run_cmd("git diff --cached --name-only")
    changed = sorted({f for f in (d1.splitlines() + d2.splitlines()) if f.strip()})
    governed_checksums = compute_governed_checksum(repo_root, governed_roots, changed)

    # Evidence path determinístico (I11)
    expected_ev = expected_executor_evidence_path(ar_id)
    if evidence_file_path.strip() != expected_ev:
        fail(E_EVIDENCE_PATH_FORBIDDEN,
             f"Evidence File (Contrato) proibido para AR_{ar_id}.\n"
             f"Expected: {expected_ev}\nGot     : {evidence_file_path}",
             exit_code=2)

    with HBLock():
        ev_file = repo_root / evidence_file_path
        ev_file.parent.mkdir(parents=True, exist_ok=True)

        with open(ev_file, "w", encoding="utf-8") as f:
            f.write(f"AR_ID: {ar_id}\n")
            f.write(f"Command: {command}\n")
            f.write(f"Exit Code: {exit_code}\n")
            f.write(f"Timestamp UTC: {ts_utc}\n")
            f.write(f"Behavior Hash (exit+stdout+stderr): {behavior_hash}\n")
            f.write(f"Git HEAD: {git_head}\n")
            f.write(f"Python Version: {python_version}\n")
            f.write(f"Protocol Version: {HB_PROTOCOL_VERSION}\n")
            f.write(f"Workspace Clean: {ws_clean}\n")
            f.write(f"Workspace Status: {ws_status}\n")
            f.write(f"Governed Checksums (sha256): {json.dumps(governed_checksums, ensure_ascii=False)}\n")
            f.write(f"\n--- STDOUT ---\n{stdout}\n")
            f.write(f"\n--- STDERR ---\n{stderr}\n")

        # Status do Executor (não é SUCESSO do Testador)
        status_hdr = "🏗️ EM_EXECUCAO" if exit_code == 0 else "❌ FALHA"

        # Append carimbo de execução
        with open(ar_file, "a", encoding="utf-8") as f:
            f.write(f"\n### Execução Executor em {git_head[:7]}\n")
            f.write(f"**Status Executor**: {status_hdr}\n")
            f.write(f"**Comando**: `{command}`\n")
            f.write(f"**Exit Code**: {exit_code}\n")
            f.write(f"**Timestamp UTC**: {ts_utc}\n")
            f.write(f"**Behavior Hash**: {behavior_hash}\n")
            f.write(f"**Evidence File**: `{evidence_file_path}`\n")
            f.write(f"**Python Version**: {python_version}\n\n")

        # Atualizar campo **Status** no header
        ar_content_updated = (repo_root / ar_file.relative_to(repo_root)).read_text(encoding="utf-8")
        ar_content_updated = re.sub(r"\*\*Status\*\*:.*", f"**Status**: {status_hdr}", ar_content_updated, count=1)
        (repo_root / ar_file.relative_to(repo_root)).write_text(ar_content_updated, encoding="utf-8")

        print(f"{status_hdr} Evidence logged to: {evidence_file_path}")

        # Rebuild _INDEX.md após atualizar Status
        rebuild_ar_index(repo_root)

    # Exit code do hb report reflete o resultado do comando
    sys.exit(0 if exit_code == 0 else 1)


def _write_kanban(ar_id: str, new_status: str, reason: str = None) -> None:
    """AR_055: Escreve roteamento do AR no Kanban.md de forma SAFE.

    Contrato:
    - Idempotente (2x não duplica card)
    - SAFE: se arquivo não existir, skip silencioso (nunca sys.exit)
    - try/except completo — falha silenciosa com warning
    - Deve ser chamada dentro de HBLock ativo (caller garante)
    """
    try:
        repo_root = get_repo_root()
        kanban_path = repo_root / KANBAN_PATH
        if not kanban_path.exists():
            print(f"⚠️  Kanban não encontrado em {KANBAN_PATH} — skip write (non-fatal)")
            return
        content = kanban_path.read_text(encoding="utf-8")
        ar_ref = f"AR_{ar_id}"
        # Mapa de status para coluna do Kanban
        status_to_column = {
            "✅ VERIFICADO": "✅ Concluído",
            "✅ SUCESSO": "✅ Concluído",
            "🔴 REJEITADO": "📥 Backlog",  # Default: Backlog (pode ser refinado pela reason)
            "⏸️ BLOQUEADO_INFRA": "⏸️ Bloqueado",
        }
        # Roteamento inteligente para REJEITADO baseado na reason
        if new_status == "🔴 REJEITADO" and reason:
            if "Executor:" in reason:
                coluna = "🛠️ Em Execução"  # Executor deve corrigir
            else:
                coluna = "📥 Backlog"  # Arquiteto/outros
        else:
            coluna = status_to_column.get(new_status, "📥 Backlog")
        note = f" — {reason}" if reason else ""
        card = f"- {ar_ref}{note}"
        # Se AR já está no Kanban, não duplicar
        if ar_ref in content:
            return
        # Append na coluna correta (busca por header da coluna)
        if f"### {coluna}" in content:
            content = content.replace(
                f"### {coluna}\n",
                f"### {coluna}\n{card}\n"
            )
        else:
            # Fallback: append no final
            content += f"\n### {coluna}\n{card}\n"
        kanban_path.write_text(content, encoding="utf-8")
    except Exception as e:
        print(f"⚠️  Kanban write falhou (non-fatal): {e}")


def update_kanban_and_status(ar_content: str, new_status: str, reason: str = None, ar_id: str = None) -> str:
    """Atualiza **Status** no conteúdo da AR e escreve roteamento no Kanban.md.

    AR_055: Expandido para escrever no Kanban.md via _write_kanban() (SAFE).
    Deve ser chamada dentro de um contexto HBLock ativo.
    Não escreve a AR no disco — o caller é responsável pelo write final.
    """
    ar_updated = re.sub(r"\*\*Status\*\*:.*", f"**Status**: {new_status}", ar_content, count=1)
    if reason:
        ar_updated += f"\n> 📋 Kanban routing: {reason}\n"
    # AR_055: escrever no Kanban.md se ar_id fornecido
    if ar_id:
        _write_kanban(ar_id, new_status, reason)
    return ar_updated


def finalize_verification(ar_id: str, ar_content: str, result_data: dict) -> tuple:
    """Roteia o resultado do Testador para o Kanban e define o próximo responsável.

    Status canônicos (Protocol v1.2.0 - Testador Contract §5):
    - SUCESSO           → ✅ SUCESSO (triple-run OK + consistency OK + temporal_check PASS)
    - REJEITADO         → 🔴 REJEITADO (AH_DIVERGENCE, INCOMPLETE_EVIDENCE, FLAKY_OUTPUT, TRIPLE_FAIL, AH_TEMPORAL_INVALID)
    - BLOQUEADO_INFRA   → ⏸️ BLOQUEADO_INFRA (infra inacessível — waiver necessário)

    Roteamento de Kanban (via reason):
    - REJEITADO + AH_DIVERGENCE → Backlog (Arquiteto: reason)
    - REJEITADO (outros)        → Em Execução (Executor: reason)

    Retorna (ar_updated_content, novo_status, final_exit).
    Deve ser chamada dentro de um contexto HBLock ativo.
    """
    status_testador = result_data["status"]
    consistency = result_data["consistency"]
    rejection_reason = result_data.get("rejection_reason") or ""

    if status_testador == "SUCESSO":
        # Protocol §5: SUCESSO → ✅ SUCESSO
        novo_status = "✅ SUCESSO"
        final_exit = 0
        print(f"✅ SUCESSO | Consistency: {consistency}")
        print(f"Report: _reports/testador/AR_{ar_id}_<git7>/result.json")
        ar_updated = update_kanban_and_status(ar_content, novo_status, ar_id=ar_id)

    elif status_testador == "REJEITADO":
        # Protocol §5: REJEITADO → 🔴 REJEITADO (sempre)
        novo_status = "🔴 REJEITADO"
        final_exit = 1
        
        # Roteamento de Kanban baseado em consistency para indicar responsável
        if consistency == "AH_DIVERGENCE":
            # Erro de contrato/lógica — Arquiteto precisa rever o plano
            kanban_reason = f"Arquiteto: {rejection_reason}"
            print(f"🔴 REJEITADO | Consistency: {consistency}")
            print(f"Reason: {rejection_reason}")
        else:
            # Erro técnico — Executor falhou na implementação
            kanban_reason = f"Executor: {rejection_reason}"
            print(f"🔴 REJEITADO | Consistency: {consistency}")
            print(f"Reason: {rejection_reason}")
        
        ar_updated = update_kanban_and_status(
            ar_content, novo_status, reason=kanban_reason, ar_id=ar_id
        )

    else:
        # Protocol §5: BLOQUEADO_INFRA → ⏸️ BLOQUEADO_INFRA
        novo_status = "⏸️ BLOQUEADO_INFRA"
        final_exit = 3
        print(f"⏸️ BLOQUEADO_INFRA | Consistency: {consistency}")
        print(f"Reason: waiver necessário")
        ar_updated = update_kanban_and_status(ar_content, novo_status, ar_id=ar_id)

    return ar_updated, novo_status, final_exit


def cmd_verify(ar_id: str) -> None:
    """Comando: hb verify <id> — Testador independente re-executa validation_command"""
    import json as _json
    from datetime import datetime, timezone

    repo_root = get_repo_root()
    ar_dir = repo_root / AR_DIR

    # V1: Localizar AR (recursivo)
    ar_files = list(ar_dir.rglob(f"AR_{ar_id}_*.md"))
    if not ar_files:
        fail(E_AR_NOT_FOUND, f"AR with id {ar_id} not found in {AR_DIR}/", exit_code=2)
    ar_file = ar_files[0]

    with open(ar_file, "r", encoding="utf-8") as f:
        ar_content = f.read()

    # V2: Verificar EM_EXECUCAO ou FALHA do Executor
    # Nota: não exigimos mais "✅ SUCESSO" explícito do report antigo,
    # pois o novo report escreve "🏭️ EM_EXECUCAO". Verificamos o evidence.
    # Para retrocompat, também aceitar "✅ SUCESSO" (legado v1.1.x).
    # Para v1.2.0, exigir evidence com Exit Code 0.

    # V3: Extrair validation_command
    match = re.search(
        r"## Validation Command \(Contrato\)\r?\n```\r?\n(.+?)\r?\n```",
        ar_content,
        re.DOTALL,
    )
    validation_cmd = match.group(1).strip() if match else ""
    if not validation_cmd:
        fail(
            E_VERIFY_NO_CMD,
            f"AR_{ar_id} has no Validation Command — not verifiable",
            exit_code=4,
        )

    # V4: Pre-check workspace sujo => FAIL hard (I5)
    ws_clean, ws_status = check_workspace_clean()
    if not ws_clean:
        fail(
            E_VERIFY_DIRTY_WORKSPACE,
            f"Workspace deve estar limpo antes do verify (anti-falsa-evidência). Status: {ws_status}",
            exit_code=2,
        )

    # V4: Re-executar validation_command — TRIPLE_RUN obrigatório (3x) com behavior_hash
    print(f"🔁 TESTADOR: triple-run ({TRIPLE_RUN_COUNT}x): {validation_cmd[:60]}...")
    runs_data: List[Dict] = []
    stdout, stderr = "", ""
    # Define HB_TRIPLE_RUN=1 para tornar scripts determinísticos (ex: doc_gates.py timestamp fixo)
    os.environ["HB_TRIPLE_RUN"] = "1"
    try:
        for run_n in range(1, TRIPLE_RUN_COUNT + 1):
            run_ec, run_out, run_err = run_cmd(validation_cmd)
            run_hash_full = compute_behavior_hash(run_ec, run_out, run_err)
            run_hash = run_hash_full[:16]
            runs_data.append({
                "run": run_n,
                "exit_code": run_ec,
                "hash_full": run_hash_full,
                "hash": run_hash,
                "stdout_len": len(run_out or ""),
                "stderr_len": len(run_err or ""),
            })
            print(f"  Run {run_n}/{TRIPLE_RUN_COUNT}: exit={run_ec} hash={run_hash}")
            if run_n == 1:
                stdout, stderr = run_out, run_err
    finally:
        # Limpa a variável de ambiente após o triple-run
        os.environ.pop("HB_TRIPLE_RUN", None)
    all_exit_0 = all(r["exit_code"] == 0 for r in runs_data)
    all_same_hash = len(set(r["hash_full"] for r in runs_data)) == 1
    if all_exit_0 and all_same_hash:
        triple_consistency = "OK"
        exit_code = 0
    elif all_exit_0:
        triple_consistency = "FLAKY_OUTPUT"
        exit_code = 2
    else:
        triple_consistency = "TRIPLE_FAIL"
        exit_code = next((r["exit_code"] for r in runs_data if r["exit_code"] != 0), 2)

    # V4.5: Post-check (opcional, para diagnóstico)
    # Nota: removido checksum_drift que chamava compute_governed_checksum() antiga

    # V5: Ler Evidence Pack
    match_ev = re.search(r"## Evidence File \(Contrato\)\n`(.+?)`", ar_content)
    ev_path = match_ev.group(1).strip() if match_ev else ""
    executor_exit = None
    evidence_pack_complete = False
    if ev_path:
        ev_file = repo_root / ev_path
        if ev_file.exists():
            ev_content = ev_file.read_text(encoding="utf-8")
            evidence_pack_complete = True
            m = re.search(r"Exit Code: (\d+)", ev_content)
            if m:
                executor_exit = int(m.group(1))

    # V6: Consistency check
    if executor_exit is not None:
        if executor_exit == 0 and exit_code != 0:
            consistency = "AH_DIVERGENCE"
        else:
            consistency = "OK"
    else:
        consistency = "UNKNOWN"

    # V7: Gerar TESTADOR_REPORT (com lock de concorrência)
    git_head = run_cmd("git rev-parse HEAD")[1].strip() or "N/A"
    hash7 = git_head[:7]
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"

    testador_run_dir = repo_root / TESTADOR_DIR / f"AR_{ar_id}_{hash7}"

    if exit_code == 0 and consistency == "OK":
        status = "SUCESSO"
        ah_flags = []
        rejection_reason = None
    elif triple_consistency == "FLAKY_OUTPUT":
        status = "REJEITADO"
        ah_flags = ["FLAKY_OUTPUT"]
        rejection_reason = (f"Output não-determinístico: behavior_hash diverge nos {TRIPLE_RUN_COUNT} runs "
                            f"(exit 0 em todos, mas hash diferente)")
    elif consistency == "AH_DIVERGENCE":
        status = "REJEITADO"
        ah_flags = ["AH_DIVERGENCE"]
        rejection_reason = f"Executor reported exit 0 but Testador got exit {exit_code}"
    elif not evidence_pack_complete:
        status = "REJEITADO"
        ah_flags = ["INCOMPLETE_EVIDENCE"]
        rejection_reason = "Evidence Pack missing or incomplete"
    else:
        status = "REJEITADO"
        ah_flags = []
        rejection_reason = f"Re-execution failed: exit {exit_code} (triple_consistency={triple_consistency})"

    context = {
        "run_id": f"TESTADOR-AR_{ar_id}-{hash7}",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "git": {"commit": git_head},
        "environment": {"python_version": python_version},
        "ar_id": ar_id,
        "ar_file": str(ar_file.relative_to(repo_root)),
    }
    result = {
        "ar_id": ar_id,
        "validation_command": validation_cmd,
        "run_count": TRIPLE_RUN_COUNT,
        "runs": runs_data,
        "triple_consistency": triple_consistency,
        "testador_exit_code": exit_code,
        "executor_exit_code": executor_exit,
        "consistency": consistency,
        "status": status,
        "ah_flags": ah_flags,
        "evidence_pack_complete": evidence_pack_complete,
        "rejection_reason": rejection_reason,
        "workspace_clean": ws_clean,
    }

    with HBLock():
        testador_run_dir.mkdir(parents=True, exist_ok=True)

        with open(testador_run_dir / "context.json", "w", encoding="utf-8") as f:
            _json.dump(context, f, indent=2, ensure_ascii=False)
        with open(testador_run_dir / "result.json", "w", encoding="utf-8") as f:
            _json.dump(result, f, indent=2, ensure_ascii=False)
        with open(testador_run_dir / "stdout.log", "w", encoding="utf-8") as f:
            f.write(stdout)
        with open(testador_run_dir / "stderr.log", "w", encoding="utf-8") as f:
            f.write(stderr)

        # V8: Rotear resultado para Kanban e atualizar Status da AR
        ar_updated, novo_status, final_exit = finalize_verification(ar_id, ar_content, result)

        # V9: Append stamp de verificação
        stamp = (
            f"\n### Verificacao Testador em {hash7}\n"
            f"**Status Testador**: {novo_status}\n"
            f"**Consistency**: {consistency}\n"
            f"**Triple-Run**: {triple_consistency} ({TRIPLE_RUN_COUNT}x)\n"
            f"**Exit Testador**: {exit_code} | **Exit Executor**: {executor_exit}\n"
            f"**TESTADOR_REPORT**: `{TESTADOR_DIR}/AR_{ar_id}_{hash7}/result.json`\n"
        )
        ar_updated = ar_updated + stamp

        with open(ar_file, "w", encoding="utf-8") as f:
            f.write(ar_updated)

    print(f"{novo_status} | Consistency: {consistency}")
    if rejection_reason:
        print(f"Reason: {rejection_reason}")
    print(f"Report: {TESTADOR_DIR}/AR_{ar_id}_{hash7}/result.json")
    sys.exit(final_exit)


def cmd_seal(ar_id: str, reason: str = "") -> None:
    """Comando: hb seal <id> [\"reason\"] — Selo humano final (✅ VERIFICADO)"""
    repo_root = get_repo_root()
    ar_dir = repo_root / AR_DIR

    ar_files = list(ar_dir.rglob(f"AR_{ar_id}_*.md"))
    if not ar_files:
        fail(E_AR_NOT_FOUND, f"AR with id {ar_id} not found in {AR_DIR}/", exit_code=2)
    ar_file = ar_files[0]
    ar_content = ar_file.read_text(encoding="utf-8")

    if "✅ VERIFICADO" in ar_content:
        print(f"✅ AR_{ar_id} já está VERIFICADO (idempotente).")
        sys.exit(0)

    if "✅ SUCESSO" not in ar_content:
        fail(E_SEAL_NOT_READY, f"AR_{ar_id} não está ✅ SUCESSO (Testador). Rode: hb verify {ar_id}", exit_code=2)

    # pegar o ÚLTIMO TESTADOR_REPORT
    reports = re.findall(r"\*\*TESTADOR_REPORT\*\*:\s*`(.+?)`", ar_content)
    if not reports:
        fail(E_SEAL_MISSING_TESTADOR_REPORT, f"AR_{ar_id} não declara TESTADOR_REPORT.", exit_code=2)
    report_path = reports[-1].strip()
    report_file = repo_root / report_path
    if not report_file.exists():
        fail(E_SEAL_MISSING_TESTADOR_REPORT, f"TESTADOR_REPORT não encontrado: {report_path}", exit_code=2)

    # staged files
    _, stdout, _ = run_cmd("git diff --cached --name-only")
    staged = set(f.strip().replace("\\", "/") for f in stdout.splitlines() if f.strip())

    if report_path.replace("\\", "/") not in staged:
        fail(E_SEAL_REPORT_NOT_STAGED, f"TESTADOR_REPORT deve estar staged: {report_path}", exit_code=2)

    # validar PASS no result.json
    try:
        result = json.loads(report_file.read_text(encoding="utf-8"))
    except Exception as e:
        fail(E_SEAL_NOT_READY, f"Falha ao ler result.json do Testador: {e}", exit_code=2)
    if result.get("status") not in ("SUCESSO", "OK", "PASS"):
        fail(E_SEAL_NOT_READY, f"Result do Testador não indica PASS: status={result.get('status')}", exit_code=2)

    # evidence do Executor (determinístico)
    ev_path = expected_executor_evidence_path(ar_id)
    ev_file = repo_root / ev_path
    if not ev_file.exists():
        fail(E_SEAL_NOT_READY, f"Evidence do Executor ausente: {ev_path}", exit_code=2)
    ev_rel = ev_path.replace("\\", "/")
    if ev_rel not in staged:
        fail(E_SEAL_EVIDENCE_NOT_STAGED, f"Evidence do Executor deve estar staged: {ev_path}", exit_code=2)
    ev_txt = ev_file.read_text(encoding="utf-8")
    if "Exit Code: 0" not in ev_txt:
        fail(E_SEAL_NOT_READY, "Evidence do Executor não contém Exit Code: 0", exit_code=2)

    # promover status + carimbo humano
    git_head = run_cmd("git rev-parse HEAD")[1].strip() or "N/A"
    from datetime import datetime, timezone
    ts_utc = datetime.now(timezone.utc).isoformat()

    with HBLock():
        ar_updated = re.sub(r"\*\*Status\*\*:.*", "**Status**: ✅ VERIFICADO", ar_content, count=1)
        stamp = (
            f"\n### Selo Humano em {git_head[:7]}\n"
            f"**Status Humano**: ✅ VERIFICADO\n"
            f"**Timestamp UTC**: {ts_utc}\n"
            f"**Motivo**: {reason.strip() if reason else '—'}\n"
            f"**TESTADOR_REPORT**: `{report_path}`\n"
            f"**Evidence File**: `{ev_path}`\n"
        )
        ar_updated += stamp
        ar_file.write_text(ar_updated, encoding="utf-8")
        rebuild_ar_index(repo_root)

    print(f"✅ AR_{ar_id} selada como VERIFICADO.")
    sys.exit(0)


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
    
    # Carregar governed_roots via YAML (I6)
    governed_roots = load_governed_roots(repo_root)
    
    ssot_staged = [f for f in staged_files if f in SSOT_FILES]
    governed_changed = any(
        any(f.startswith(root) for root in governed_roots) 
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
                # Version-aware: v1.0.8+ exige VERIFICADO; anterior aceita SUCESSO
                ar_proto_m = re.search(r"\*\*Versão do Protocolo\*\*: ([\d.]+)", ar_content)
                ar_proto = ar_proto_m.group(1) if ar_proto_m else "1.0.0"
                try:
                    ar_proto_tuple = tuple(int(x) for x in ar_proto.split("."))
                except Exception:
                    ar_proto_tuple = (1, 0, 0)

                requires_verified = ar_proto_tuple >= (1, 0, 8)
                has_valid_status = (
                    ("✅ VERIFICADO" in ar_content)
                    if requires_verified
                    else ("✅ SUCESSO" in ar_content or "✅ VERIFICADO" in ar_content)
                )

                if has_valid_status:
                    # Extrair evidence file path
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
                 "SSOT staged but no valid AR with [x] + status válido (✅ VERIFICADO para v1.0.8+; ✅ SUCESSO para legado) + staged evidence (Exit Code: 0)", 
                 exit_code=1)
    
    # C4: Se governed roots mudaram => exigir pelo menos 1 AR staged
    if governed_changed and not ars_staged:
        fail("E_GOVERNED_NO_AR",
             f"Governed roots changed without AR staged", exit_code=1)

    # C5: Sync obrigatório do _INDEX.md
    # ARs staged (excluindo _INDEX.md)
    ars_staged_no_index = [
        f for f in staged_files
        if f.startswith(AR_DIR) and "AR_" in f and not f.endswith("_INDEX.md")
    ]
    index_staged_path = "docs/hbtrack/_INDEX.md"
    if ars_staged_no_index and index_staged_path not in staged_files:
        fail(E_AR_INDEX_NOT_STAGED,
             f"ARs staged sem _INDEX.md staged: {ars_staged_no_index}\n"
             f"Execute 'hb plan' ou 'hb report' para regenerar o index antes de commitar.",
             exit_code=1)

    # C6: Imutabilidade de ARs com ✅ VERIFICADO (I9)
    # + Enforcement: TESTADOR_REPORT staged quando houver verify (I8)
    # + Enforcement: Evidence do Executor staged para ARs ✅ VERIFICADO (I9)
    for ar_rel_path in ars_staged_no_index:
        ar_file = repo_root / ar_rel_path
        try:
            current_content = ar_file.read_text(encoding="utf-8")
        except Exception:
            continue

        # I8: Se AR tem verify (✅ SUCESSO ou 🔴 REJEITADO), TESTADOR_REPORT MUST estar staged OU commitado
        if "✅ SUCESSO" in current_content or "🔴 REJEITADO" in current_content:
            reports = re.findall(r"\*\*TESTADOR_REPORT\*\*:\s*`(.+?)`", current_content)
            if reports:
                report_rel = reports[-1].strip().replace("\\", "/")
                if not is_file_in_git(report_rel, staged_files):
                    fail(E_TESTADOR_REPORT_NOT_STAGED,
                         f"{ar_rel_path}: AR com verify MUST ter TESTADOR_REPORT (staged ou commitado): {report_rel}",
                         exit_code=1)

        # I9: Imutabilidade de ARs com ✅ VERIFICADO
        if "✅ VERIFICADO" not in current_content:
            continue

        # AR ✅ VERIFICADO staged => verificar imutabilidade
        ret, original_content, _ = run_cmd(f'git show HEAD:{ar_rel_path}')
        if ret != 0:
            # Arquivo novo (Added) — pular check de imutabilidade
            continue
        if "**Status**: ✅ VERIFICADO" not in original_content:
            # Não estava VERIFICADO no HEAD, agora está — permitir (selo humano)
            continue

        # AR com VERIFICADO no HEAD — verificar que o corpo (pré-carimbo) não foi alterado
        # Extrair pré-carimbo: tudo antes de '---\n## Carimbo de Execução'
        separator = "---\n## Carimbo de Execução"
        original_pre = original_content.split(separator)[0].strip()
        staged_pre = current_content.split(separator)[0].strip()
        if original_pre != staged_pre:
            fail(E_AR_IMMUTABLE,
                 f"{ar_rel_path}: AR com ✅ VERIFICADO não pode ter corpo modificado manualmente.",
                 exit_code=1)

        # I9: Evidence do Executor MUST estar staged para ARs ✅ VERIFICADO
        ev_matches = re.findall(r"\*\*Evidence File\*\*:\s*`(.+?)`", current_content)
        if ev_matches:
            ev_rel = ev_matches[-1].strip().replace("\\", "/")
            if ev_rel not in staged_files:
                fail(E_SEAL_EVIDENCE_NOT_STAGED,
                     f"{ar_rel_path}: AR ✅ VERIFICADO MUST ter evidence staged: {ev_rel}",
                     exit_code=1)

    print("✅ Check PASSED")
    sys.exit(0)

# ========== MAIN ==========
def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: hb <command> [args]")
        print("Commands: version | plan <path> [--force|--skip-existing] [--dry-run]")
        print("          report <id> \"<cmd>\" | verify <id> | seal <id> [\"reason\"]")
        print("          check --mode <mode> | rebuild-index")
        print("          gates list | gates check <id>")
        sys.exit(1)

    command = sys.argv[1]

    if command == "version":
        cmd_version()

    elif command == "gates":
        subcommand = sys.argv[2] if len(sys.argv) > 2 else ""
        if subcommand == "list":
            cmd_gates_list()
        elif subcommand == "check":
            if len(sys.argv) < 4:
                fail("E_USAGE", "Usage: hb gates check <gate_id>")
            cmd_gates_check(sys.argv[3])
        else:
            fail("E_USAGE", "Usage: hb gates list | hb gates check <id>")

    elif command == "rebuild-index":
        rebuild_ar_index(get_repo_root())
        print("✅ AR Index rebuilt successfully.")
        sys.exit(0)

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

    elif command == "verify":
        if len(sys.argv) < 3:
            fail("E_USAGE", "Usage: hb verify <id>")
        cmd_verify(sys.argv[2])

    elif command == "seal":
        if len(sys.argv) < 3:
            fail("E_USAGE", "Usage: hb seal <id> [\"reason\"]")
        reason = sys.argv[3] if len(sys.argv) >= 4 else ""
        cmd_seal(sys.argv[2], reason)

    elif command == "check":
        mode = "manual"
        if len(sys.argv) >= 4 and sys.argv[2] == "--mode":
            mode = sys.argv[3]
        cmd_check(mode)

    else:
        fail("E_UNKNOWN_COMMAND", f"Unknown command: {command}")

if __name__ == "__main__":
    main()






