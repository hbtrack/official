#!/usr/bin/env python3
"""
SSOT Generator/Validator - HB Track (v1.0)
SPEC: docs/hbtrack/specs/Gerador SSOTs.md
CONTRATO: docs/hbtrack/contratos/Contratos SSOTs.md

Gera/valida SSOTs canônicos em docs/ssot/:
- openapi.json
- schema.sql  
- alembic_state.txt

Usage:
  python scripts/generate/docs/gen_docs_ssot.py --all --mode generate
  python scripts/generate/docs/gen_docs_ssot.py --all --mode validate --profile vps
"""
import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import urlparse

# =============================================================================
# CONFIGURATION
# =============================================================================

REPO_ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = REPO_ROOT / "Hb Track - Backend"
SSOT_DIR = REPO_ROOT / "docs" / "ssot"
EVIDENCE_DIR = REPO_ROOT / "docs" / "evidence"

# Carregar .env do backend
try:
    from dotenv import load_dotenv
    env_path = BACKEND_ROOT / ".env"
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    pass  # dotenv opcional, mas recomendado

# Exit codes determinísticos
ERROR_CODES = {
    "E_IMPORT_OPENAPI": "E_IMPORT_OPENAPI",
    "E_HTTP_FALLBACK_FORBIDDEN": "E_HTTP_FALLBACK_FORBIDDEN",
    "E_OPENAPI_INVALID": "E_OPENAPI_INVALID",
    "E_PGDUMP_MISSING": "E_PGDUMP_MISSING",
    "E_DB_UNREACHABLE": "E_DB_UNREACHABLE",
    "E_SCHEMA_VOLATILE": "E_SCHEMA_VOLATILE",
    "E_SCHEMA_INVALID": "E_SCHEMA_INVALID",
    "E_ALEMBIC_MISSING": "E_ALEMBIC_MISSING",
    "E_ALEMBIC_FORMAT_INVALID": "E_ALEMBIC_FORMAT_INVALID",
    "E_MULTIPLE_HEADS": "E_MULTIPLE_HEADS",
    "E_MULTIPLE_CURRENT": "E_MULTIPLE_CURRENT",
    "E_DB_NOT_AT_HEAD": "E_DB_NOT_AT_HEAD",
    "E_MISMATCH_OPENAPI": "E_MISMATCH_OPENAPI",
    "E_MISMATCH_SCHEMA": "E_MISMATCH_SCHEMA",
    "E_MISMATCH_ALEMBIC": "E_MISMATCH_ALEMBIC",
}

# =============================================================================
# OPENAPI GENERATION
# =============================================================================

def generate_openapi(output_dir: Path, allow_http_fallback: bool = False) -> tuple[bool, str]:
    """
    Gera openapi.json via import app.openapi().
    Retorna (success, error_code_or_empty)
    """
    output_file = output_dir / "openapi.json"
    
    # Tentar import direto (MUST)
    try:
        sys.path.insert(0, str(BACKEND_ROOT))
        
        # Garantir JWT_SECRET dummy para config
        if not os.getenv("JWT_SECRET"):
            os.environ["JWT_SECRET"] = "dummy-secret-for-ssot-generation"
        
        from app.main import app
        schema = app.openapi()
        
        # Validar invariantes estruturais
        if not isinstance(schema, dict):
            return False, ERROR_CODES["E_OPENAPI_INVALID"]
        if not schema.get("openapi", "").startswith("3."):
            return False, ERROR_CODES["E_OPENAPI_INVALID"]
        if "paths" not in schema:
            return False, ERROR_CODES["E_OPENAPI_INVALID"]
        
        # Serializar deterministicamente
        with open(output_file, "w", encoding="utf-8", newline="\n") as f:
            json.dump(schema, f, sort_keys=True, indent=2, ensure_ascii=False)
            f.write("\n")
        
        return True, ""
    
    except Exception as e:
        # HTTP fallback é FORBIDDEN por padrão
        if not allow_http_fallback:
            print(f"[ERROR] {ERROR_CODES['E_IMPORT_OPENAPI']}: {e}", file=sys.stderr)
            return False, ERROR_CODES["E_IMPORT_OPENAPI"]
        
        # Se permitido, tentar HTTP (mas marcar como NONDETERMINISTIC)
        print(f"[WARN] Import falhou: {e}", file=sys.stderr)
        print("NONDETERMINISTIC_PATH=true", file=sys.stderr)
        return False, ERROR_CODES["E_HTTP_FALLBACK_FORBIDDEN"]

# =============================================================================
# SCHEMA SQL GENERATION
# =============================================================================

def generate_schema_sql(output_dir: Path) -> tuple[bool, str]:
    """
    Gera schema.sql via pg_dump (DB canônico VPS).
    Retorna (success, error_code_or_empty)
    """
    output_file = output_dir / "schema.sql"
    
    database_url = os.getenv("DATABASE_URL", "")
    if not database_url:
        print(f"[ERROR] {ERROR_CODES['E_DB_UNREACHABLE']}: DATABASE_URL not set", file=sys.stderr)
        return False, ERROR_CODES["E_DB_UNREACHABLE"]
    
    # Limpar URL
    clean_url = database_url
    for prefix in ["postgresql+asyncpg://", "postgresql+psycopg2://", "postgresql+psycopg://"]:
        clean_url = clean_url.replace(prefix, "postgresql://")
    
    parsed = urlparse(clean_url)
    if not all([parsed.hostname, parsed.username, parsed.path]):
        print(f"[ERROR] {ERROR_CODES['E_DB_UNREACHABLE']}: Invalid DATABASE_URL", file=sys.stderr)
        return False, ERROR_CODES["E_DB_UNREACHABLE"]
    
    # Verificar pg_dump existe
    try:
        subprocess.run(["pg_dump", "--version"], capture_output=True, check=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        print(f"[ERROR] {ERROR_CODES['E_PGDUMP_MISSING']}: pg_dump not found", file=sys.stderr)
        return False, ERROR_CODES["E_PGDUMP_MISSING"]
    
    # Build comando pg_dump
    pg_dump_args = [
        "pg_dump",
        "--schema-only",
        "--no-owner",
        "--no-privileges",
        "--no-comments",
        "-h", parsed.hostname,
        "-p", str(parsed.port or 5432),
        "-U", parsed.username,
        "-d", parsed.path.lstrip("/").split("?")[0],
    ]
    
    env = os.environ.copy()
    env["PGPASSWORD"] = parsed.password or ""
    if "sslmode" in database_url:
        env["PGSSLMODE"] = "require"
    
    try:
        result = subprocess.run(
            pg_dump_args,
            capture_output=True,
            text=False,
            env=env,
            timeout=120,
            check=False,
        )
        
        if result.returncode != 0:
            err = (result.stderr or b"").decode("utf-8", errors="replace")
            print(f"[ERROR] {ERROR_CODES['E_DB_UNREACHABLE']}: pg_dump failed: {err}", file=sys.stderr)
            return False, ERROR_CODES["E_DB_UNREACHABLE"]
        
        # Normalizar conteúdo: remover linhas voláteis
        content = (result.stdout or b"").decode("utf-8", errors="replace")
        
        # Remover linha \unrestrict <TOKEN> (security token volátil do pg_dump)
        lines = []
        for line in content.split("\n"):
            if line.startswith("\\unrestrict ") or line.startswith("\\restrict "):
                continue  # Skip volatile security token
            lines.append(line)
        
        normalized_content = "\n".join(lines)
        
        # Escrever SEM header volátil (MUST NOT incluir timestamp)
        with open(output_file, "w", encoding="utf-8", newline="\n") as f:
            f.write(normalized_content)
            if not normalized_content.endswith("\n"):
                f.write("\n")
        
        # Validar que não contém timestamp ISO-8601 (invariante)
        if re.search(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', normalized_content):
            print(f"[ERROR] {ERROR_CODES['E_SCHEMA_VOLATILE']}: schema.sql contém timestamp", file=sys.stderr)
            return False, ERROR_CODES["E_SCHEMA_VOLATILE"]
        
        return True, ""
    
    except subprocess.TimeoutExpired:
        print(f"[ERROR] {ERROR_CODES['E_DB_UNREACHABLE']}: pg_dump timeout", file=sys.stderr)
        return False, ERROR_CODES["E_DB_UNREACHABLE"]

# =============================================================================
# ALEMBIC STATE GENERATION
# =============================================================================

def generate_alembic_state(output_dir: Path, profile: str) -> tuple[bool, str]:
    """
    Gera alembic_state.txt com formato canônico (SEM timestamp).
    Retorna (success, error_code_or_empty)
    """
    output_file = output_dir / "alembic_state.txt"
    
    # Verificar alembic existe
    try:
        subprocess.run(["alembic", "--version"], capture_output=True, check=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        print(f"[ERROR] {ERROR_CODES['E_ALEMBIC_MISSING']}: alembic not found", file=sys.stderr)
        return False, ERROR_CODES["E_ALEMBIC_MISSING"]
    
    alembic_ini = BACKEND_ROOT / "alembic.ini"
    if not alembic_ini.exists():
        print(f"[ERROR] {ERROR_CODES['E_ALEMBIC_MISSING']}: alembic.ini not found", file=sys.stderr)
        return False, ERROR_CODES["E_ALEMBIC_MISSING"]
    
    # Preparar env com DATABASE_URL_SYNC
    env = os.environ.copy()
    db_url = os.getenv("DATABASE_URL", "")
    if not db_url:
        print(f"[ERROR] {ERROR_CODES['E_DB_UNREACHABLE']}: DATABASE_URL not set", file=sys.stderr)
        return False, ERROR_CODES["E_DB_UNREACHABLE"]
    
    if not os.getenv("DATABASE_URL_SYNC"):
        sync_url = db_url.replace("postgresql+asyncpg://", "postgresql+psycopg2://")
        if not sync_url.startswith("postgresql+psycopg2://"):
            sync_url = sync_url.replace("postgresql://", "postgresql+psycopg2://")
        env["DATABASE_URL_SYNC"] = sync_url
    
    try:
        # Get HEADS (repo)
        result_heads = subprocess.run(
            ["alembic", "-c", str(alembic_ini), "heads"],
            capture_output=True,
            text=True,
            cwd=BACKEND_ROOT,
            env=env,
            timeout=30,
            check=False,
        )
        
        # Get CURRENT (db)
        result_current = subprocess.run(
            ["alembic", "-c", str(alembic_ini), "current"],
            capture_output=True,
            text=True,
            cwd=BACKEND_ROOT,
            env=env,
            timeout=30,
            check=False,
        )
        
        # Parse heads (extrair somente revision id)
        heads_raw = result_heads.stdout.strip()
        heads = []
        for line in heads_raw.split("\n"):
            match = re.match(r'^([0-9a-f]{12})', line.strip())
            if match:
                heads.append(match.group(1))
        
        # Parse current (extrair somente revision id)
        current_raw = result_current.stdout.strip()
        current = []
        for line in current_raw.split("\n"):
            match = re.match(r'^([0-9a-f]{12})', line.strip())
            if match:
                current.append(match.group(1))
        
        # Ordenar lexicograficamente
        heads.sort()
        current.sort()
        
        # Aplicar policy single-head
        if len(heads) != 1:
            print(f"[ERROR] {ERROR_CODES['E_MULTIPLE_HEADS']}: heads_count={len(heads)}", file=sys.stderr)
            return False, ERROR_CODES["E_MULTIPLE_HEADS"]
        
        if len(current) != 1:
            print(f"[ERROR] {ERROR_CODES['E_MULTIPLE_CURRENT']}: current_count={len(current)}", file=sys.stderr)
            return False, ERROR_CODES["E_MULTIPLE_CURRENT"]
        
        if heads[0] != current[0]:
            print(f"[ERROR] {ERROR_CODES['E_DB_NOT_AT_HEAD']}: head={heads[0]}, current={current[0]}", file=sys.stderr)
            return False, ERROR_CODES["E_DB_NOT_AT_HEAD"]
        
        # Obter versões python/alembic
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        alembic_version_result = subprocess.run(
            ["alembic", "--version"],
            capture_output=True,
            text=True,
            check=False,
        )
        alembic_version = alembic_version_result.stdout.strip().split()[-1] if alembic_version_result.returncode == 0 else "unknown"
        
        # Gerar arquivo no formato canônico (SEM timestamp)
        lines = [
            "=== ALEMBIC META ===",
            f"profile: {profile}",
            "script_location: migrations",
            "version_table: alembic_version",
            f"python: {python_version}",
            f"alembic: {alembic_version}",
            "",
            "=== ALEMBIC HEADS (REPO) ===",
            *heads,
            "",
            "=== ALEMBIC CURRENT (DB) ===",
            *current,
            "",
            "=== DERIVED CHECKS ===",
            "db_reachable: true",
            f"repo_heads_count: {len(heads)}",
            f"db_current_count: {len(current)}",
            f"db_at_head: {str(heads[0] == current[0]).lower()}",
        ]
        
        with open(output_file, "w", encoding="utf-8", newline="\n") as f:
            f.write("\n".join(lines))
            f.write("\n")
        
        return True, ""
    
    except subprocess.TimeoutExpired:
        print(f"[ERROR] {ERROR_CODES['E_ALEMBIC_MISSING']}: alembic timeout", file=sys.stderr)
        return False, ERROR_CODES["E_ALEMBIC_MISSING"]

# =============================================================================
# VALIDATE MODE
# =============================================================================

def validate_ssot(ssot_name: str, generate_func, *args) -> tuple[bool, str]:
    """
    Valida SSOT: gera em temp, compara byte-a-byte com docs/ssot/.
    Retorna (success, error_code_or_empty)
    """
    canonical_file = SSOT_DIR / ssot_name
    if not canonical_file.exists():
        error_map = {
            "openapi.json": "E_MISMATCH_OPENAPI",
            "schema.sql": "E_MISMATCH_SCHEMA",
            "alembic_state.txt": "E_MISMATCH_ALEMBIC"
        }
        error_code = error_map.get(ssot_name, "E_MISMATCH_UNKNOWN")
        print(f"[ERROR] {error_code}: {canonical_file} não existe", file=sys.stderr)
        return False, error_code
    
    with tempfile.TemporaryDirectory() as tmpdir:
        temp_dir = Path(tmpdir)
        
        # Gerar SSOT em temp
        success, error_code = generate_func(temp_dir, *args)
        if not success:
            return False, error_code
        
        temp_file = temp_dir / ssot_name
        
        # Comparar byte-a-byte
        canonical_content = canonical_file.read_bytes()
        temp_content = temp_file.read_bytes()
        
        if canonical_content != temp_content:
            error_map = {
                "openapi.json": "E_MISMATCH_OPENAPI",
                "schema.sql": "E_MISMATCH_SCHEMA",
                "alembic_state.txt": "E_MISMATCH_ALEMBIC"
            }
            error_code = error_map.get(ssot_name, "E_MISMATCH_UNKNOWN")
            print(f"[ERROR] {error_code}: conteúdo difere", file=sys.stderr)
            return False, error_code
        
        return True, ""

# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="SSOT Generator/Validator - HB Track (v1.0)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--all", action="store_true", help="Processar todos os SSOTs")
    parser.add_argument("--openapi", action="store_true", help="Processar openapi.json")
    parser.add_argument("--schema", action="store_true", help="Processar schema.sql")
    parser.add_argument("--alembic", action="store_true", help="Processar alembic_state.txt")
    parser.add_argument("--mode", choices=["generate", "validate"], default="generate", help="Modo de operação")
    parser.add_argument("--profile", default="vps", help="Profile do DB (default: vps)")
    parser.add_argument("--allow-http-fallback", action="store_true", help="Permitir HTTP fallback (NONDETERMINISTIC)")
    
    args = parser.parse_args()
    
    # Default: --all
    if not (args.openapi or args.schema or args.alembic):
        args.all = True
    
    # HTTP fallback é FORBIDDEN em validate
    if args.mode == "validate" and args.allow_http_fallback:
        print(f"[ERROR] {ERROR_CODES['E_HTTP_FALLBACK_FORBIDDEN']}: --allow-http-fallback FORBIDDEN em validate", file=sys.stderr)
        print(f"FAIL SSOT_VALIDATE_MATCH")
        print(ERROR_CODES["E_HTTP_FALLBACK_FORBIDDEN"])
        sys.exit(1)
    
    # Criar diretórios
    if args.mode == "generate":
        SSOT_DIR.mkdir(parents=True, exist_ok=True)
        EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    
    # Processar SSOTs
    results = {}
    error_codes = []
    
    if args.all or args.openapi:
        if args.mode == "generate":
            success, error_code = generate_openapi(SSOT_DIR, args.allow_http_fallback)
        else:
            success, error_code = validate_ssot("openapi.json", generate_openapi, args.allow_http_fallback)
        
        results["SSOT_OPENAPI"] = success
        if not success:
            error_codes.append(error_code)
    
    if args.all or args.schema:
        if args.mode == "generate":
            success, error_code = generate_schema_sql(SSOT_DIR)
        else:
            success, error_code = validate_ssot("schema.sql", generate_schema_sql)
        
        results["SSOT_SCHEMA"] = success
        if not success:
            error_codes.append(error_code)
    
    if args.all or args.alembic:
        if args.mode == "generate":
            success, error_code = generate_alembic_state(SSOT_DIR, args.profile)
        else:
            success, error_code = validate_ssot("alembic_state.txt", generate_alembic_state, args.profile)
        
        results["SSOT_ALEMBIC"] = success
        if not success:
            error_codes.append(error_code)
    
    # Adicionar resultado de VALIDATE_MATCH se em modo validate
    if args.mode == "validate":
        all_pass = all(results.values())
        results["SSOT_VALIDATE_MATCH"] = all_pass
    
    # Imprimir resumo determinístico
    for key, success in results.items():
        status = "PASS" if success else "FAIL"
        print(f"{status} {key}")
    
    # Imprimir error codes
    for error_code in error_codes:
        print(error_code)
    
    # Exit code
    all_success = all(results.values())
    sys.exit(0 if all_success else 1)


if __name__ == "__main__":
    main()
