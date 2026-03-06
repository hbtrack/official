# HB_SCRIPT_KIND=RESET
# HB_SCRIPT_SCOPE=db
# HB_SCRIPT_SIDE_EFFECTS=DB_WRITE,DESTRUCTIVE
# HB_SCRIPT_IDEMPOTENT=YES
# HB_SCRIPT_ENTRYPOINT=python scripts/db/reset_hb_track_test.py
# HB_SCRIPT_OUTPUTS=stdout
# ===========================================================================
# RESET + MIGRATION + SEED — BANCO DE DADOS DE TESTES (hb_track — VPS)
# ===========================================================================
#
# PROPOSITO: Preparar banco de testes do zero para a TRUTH SUITE do módulo
#            TRAINING (e demais módulos). Equivalente Python do reset_db_e2e.ps1.
#
# BANCO DE TESTES: hb_track (VPS — 191.252.185.34)
#   Acesso via SSH tunnel: ssh -L 5434:localhost:5432 deploy@191.252.185.34 -N
#   URL efetiva: postgresql+psycopg2://hbtrack_app:...@localhost:5434/hb_track
#
# BANCOS BLOQUEADOS (GUARDRAIL):
#   - hb_track_prod : produção — NUNCA usar em testes
#   - hb_track_dev  : Docker local — ambiente errado para TRUTH SUITE
#
# PIPELINE:
#   1. GUARDRAIL:   Verifica que DATABASE_URL aponta para hb_track (VPS)
#   2. MIGRATION:   Executa Alembic (alembic upgrade heads)
#   3. SEED:        Popula dados mínimos (best-effort)
#
# USO:
#   python scripts/db/reset_hb_track_test.py           # pipeline completo
#   python scripts/db/reset_hb_track_test.py --dry-run # só valida env, não executa
#
# PRE-REQUISITO: SSH tunnel ativo na porta 5434
#   ssh -L 5434:localhost:5432 -i ~/.ssh/hbtrack_deploy deploy@191.252.185.34 -N
#
# SAIDA:
#   Exit 0: banco pronto para testes
#   Exit 1: erro em alguma fase (mensagem descritiva em stderr)
#
# REFERENCIA: scripts/reset/db/reset_db_e2e.ps1 (lógica equivalente em PowerShell)
# ===========================================================================

import os
import sys
import subprocess
from pathlib import Path

# ---------------------------------------------------------------------------
# Constantes de caminho
# ---------------------------------------------------------------------------
WORKSPACE_ROOT = Path(__file__).resolve().parent.parent.parent   # c:\HB TRACK
BACKEND_ROOT   = WORKSPACE_ROOT / "Hb Track - Backend"
ALEMBIC_DIR    = BACKEND_ROOT          # alembic.ini vive na raiz do backend
SEED_SCRIPT    = WORKSPACE_ROOT / "scripts" / "run" / "run_test_seeds.py"

# URL padrão: hb_track na VPS — acesso direto (porta 5432 acessível externamente)
_DEFAULT_DB_URL_SYNC = (
    "postgresql+psycopg2://hbtrack_app:13Lyb6DDelb7y16ZFPcdkCQi@191.252.185.34:5432/hb_track"
)


def _load_root_env() -> None:
    """Carrega variáveis do .env da raiz do workspace (VPS settings).
    Não sobrescreve variáveis já definidas no ambiente.
    """
    env_file = WORKSPACE_ROOT / ".env"
    if not env_file.exists():
        return
    with open(env_file, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            # Remove inline comments (ex: VALUE=foo  # comment)
            value = value.split("#")[0].strip()
            if key and key not in os.environ:   # não sobrescreve env explícito
                os.environ[key] = value

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def ok(msg: str) -> None:
    print(f"[OK]   {msg}", flush=True)


def info(msg: str) -> None:
    print(f"[INFO] {msg}", flush=True)


def fail(msg: str) -> None:
    print(f"[ERRO] {msg}", file=sys.stderr, flush=True)
    sys.exit(1)


def run(cmd: list[str], cwd: Path, env: dict | None = None) -> None:
    """Executa subprocesso; aborta com exit 1 se retornar código != 0."""
    merged_env = {**os.environ, **(env or {})}
    result = subprocess.run(cmd, cwd=str(cwd), env=merged_env)
    if result.returncode != 0:
        fail(f"Comando falhou (exit {result.returncode}): {' '.join(cmd)}")


# ---------------------------------------------------------------------------
# Fase 0: Guardrail de banco
# ---------------------------------------------------------------------------

def guardrail_db_url() -> str:
    """
    Retorna DATABASE_URL_SYNC validada.

    BANCO PERMITIDO:  hb_track (VPS via SSH tunnel localhost:5434)
    BANCOS BLOQUEADOS:
      - hb_track_prod : produção — acesso proibido em testes
      - hb_track_dev  : Docker local — ambiente inválido para TRUTH SUITE
    """
    url = os.environ.get("DATABASE_URL_SYNC") or os.environ.get("DATABASE_URL") or _DEFAULT_DB_URL_SYNC

    if "hb_track_prod" in url:
        fail(
            f"GUARDRAIL: DATABASE_URL aponta para hb_track_prod — operação PROIBIDA (banco de produção).\n"
            f"  URL detectada: {url}\n"
            f"  Configure DATABASE_URL_SYNC apontando para hb_track (VPS, porta 5434)."
        )

    if "hb_track_dev" in url:
        fail(
            f"GUARDRAIL: DATABASE_URL aponta para hb_track_dev (Docker local) — ambiente inválido.\n"
            f"  URL detectada: {url}\n"
            f"  Banco de testes correto: hb_track na VPS via SSH tunnel (localhost:5434).\n"
            f"  Ative o tunnel: ssh -L 5434:localhost:5432 -i ~/.ssh/hbtrack_deploy deploy@191.252.185.34 -N"
        )

    if "hb_track" not in url:
        fail(
            f"GUARDRAIL: DATABASE_URL não contém 'hb_track' — banco de testes não identificado.\n"
            f"  URL detectada: {url}\n"
            f"  Configure DATABASE_URL_SYNC apontando para hb_track (VPS, porta 5434)."
        )

    ok(f"GUARDRAIL: banco validado → {url}")
    return url


# ---------------------------------------------------------------------------
# Fase 1: Migration (Alembic)
# ---------------------------------------------------------------------------

def run_migrations(db_url_sync: str) -> None:
    info("FASE MIGRATION: executando alembic upgrade heads ...")

    if not ALEMBIC_DIR.exists():
        fail(f"Diretório Alembic não encontrado: {ALEMBIC_DIR}")

    alembic_env = {
        "DATABASE_URL":      db_url_sync,
        "DATABASE_URL_SYNC": db_url_sync,
        # Alembic também pode precisar da versão async; ajuste se necessário
        "DATABASE_URL_ASYNC": db_url_sync.replace(
            "psycopg2", "asyncpg"
        ).replace("postgresql+asyncpg", "postgresql+asyncpg"),
    }

    run(
        [sys.executable, "-m", "alembic", "upgrade", "heads"],
        cwd=ALEMBIC_DIR,
        env=alembic_env,
    )

    ok("FASE MIGRATION: concluída — schema atualizado")


# ---------------------------------------------------------------------------
# Fase 2: Seed
# ---------------------------------------------------------------------------

def run_seed(db_url_sync: str) -> None:
    info("FASE SEED: executando seed ...")

    if not SEED_SCRIPT.exists():
        print(f"[AVISO] Script de seed não encontrado: {SEED_SCRIPT}", flush=True)
        print("[AVISO] Pulando seed — testes usam isolamento transacional (savepoints).", flush=True)
        return

    seed_env = {
        "DATABASE_URL":      db_url_sync,
        "DATABASE_URL_SYNC": db_url_sync,
    }

    # Seed é best-effort: falha não bloqueia testes com isolamento transacional
    result = subprocess.run(
        [sys.executable, str(SEED_SCRIPT)],
        cwd=WORKSPACE_ROOT,
        env={**os.environ, **seed_env},
    )
    if result.returncode != 0:
        print("[AVISO] Seed retornou erro — continuando (testes usam savepoints).", flush=True)
    else:
        ok("FASE SEED: concluída — dados mínimos inseridos")


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

def main() -> None:
    dry_run = "--dry-run" in sys.argv

    print("=" * 70, flush=True)
    print("HB TRACK — reset_hb_track_test.py", flush=True)
    print("Preparando banco de testes (TRUTH SUITE)", flush=True)
    print("Banco: hb_track — VPS via SSH tunnel (localhost:5434)", flush=True)
    if dry_run:
        print("[DRY-RUN] Apenas validação de ambiente — nenhuma operação executada", flush=True)
    print("=" * 70, flush=True)

    # Carrega .env da raiz do workspace (VPS settings) antes do guardrail
    _load_root_env()

    # Fase 0: guardrail (sempre executa, mesmo em dry-run)
    db_url = guardrail_db_url()

    if dry_run:
        ok("DRY-RUN: ambiente válido. Nenhuma operação destrutiva executada.")
        sys.exit(0)

    # Fase 1: migrations
    run_migrations(db_url)

    # Fase 2: seed
    run_seed(db_url)

    print("=" * 70, flush=True)
    ok("Banco de testes pronto. TRUTH SUITE pode ser executada.")
    print("  Comando: cd \"Hb Track - Backend\" && pytest -q tests/training/", flush=True)
    print("=" * 70, flush=True)
    sys.exit(0)


if __name__ == "__main__":
    main()
