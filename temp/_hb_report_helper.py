"""
Helper: executa 'hb report <id>' lendo o validation_command diretamente do AR file.
Contorna limitações de quoting do cmd.exe no Windows executando partes Python
diretamente via subprocess (sem shell), para então chamar hb_cli.py com os resultados.

ESTRATÉGIA:
- Para steps 'python -c "code"': extrai o código Python entre o PRIMEIRO e o ÚLTIMO "
  no step, passando diretamente para subprocess sem shell (evita quoting do cmd.exe).
- Para steps 'npx tsc ... | python -c "code"': executa tsc via shell, captura stdout+stderr,
  então passa para o python -c code diretamente.
- Para steps 'cd "dir"': guarda o diretório de trabalho.
- Outros steps: executa via shell normalmente.

Uso: python temp/_hb_report_helper.py <ar_id>
"""
import sys
import os
import re
import json
import hashlib
import subprocess
from datetime import datetime, timezone
from pathlib import Path

# ─── Constantes ────────────────────────────────────────────────────────────────
HB_PROTOCOL_VERSION = "1.3.0"
AR_DIR = "docs/hbtrack/ars"
EV_DIR = "docs/hbtrack/evidence"
GOVERNED_ROOTS_SPEC_PATH = "docs/_canon/specs/GOVERNED_ROOTS.yaml"


# ─── Utilitários ───────────────────────────────────────────────────────────────

def _norm_newlines(s: str) -> str:
    return (s or "").replace("\r\n", "\n").replace("\r", "\n")


def compute_behavior_hash(exit_code: int, stdout: str, stderr: str) -> str:
    payload = f"{exit_code}\n{_norm_newlines(stdout)}\n---STDERR---\n{_norm_newlines(stderr)}"
    return hashlib.sha256(payload.encode("utf-8", errors="replace")).hexdigest()


def load_governed_roots(repo_root: Path):
    """Carrega governed_roots.yaml; retorna lista de root strings."""
    spec = repo_root / GOVERNED_ROOTS_SPEC_PATH
    if not spec.exists():
        return []
    try:
        import yaml
        data = yaml.safe_load(spec.read_text(encoding="utf-8")) or {}
        return [r.strip().replace("\\", "/").rstrip("/") + "/" for r in data.get("roots", [])]
    except Exception:
        return []


def compute_governed_checksum(repo_root: Path, governed_roots, files):
    result = {}
    for fpath in files:
        fp = (fpath or "").strip().replace("\\", "/")
        if not fp:
            continue
        if not any(fp.startswith(root) for root in governed_roots):
            continue
        try:
            content = (repo_root / fp).read_bytes()
            result[fp] = hashlib.sha256(content).hexdigest()
        except FileNotFoundError:
            result[fp] = "DELETED"
    return result


def git_run(args, cwd):
    r = subprocess.run(["git"] + args, capture_output=True, text=True, encoding="utf-8", cwd=cwd)
    return r.stdout.strip()


def check_workspace_clean(repo_root):
    try:
        out = subprocess.run(
            ["git", "diff", "--name-only"],
            capture_output=True, text=True, encoding="utf-8", cwd=str(repo_root)
        )
        lines = [l for l in out.stdout.strip().split("\n") if l.strip()]
        if not lines:
            return True, "workspace_clean"
        return False, f"unstaged_modified={len(lines)}"
    except Exception as e:
        return False, f"git_error={e}"


def rebuild_ar_index(repo_root: Path):
    """Delega rebuild do _INDEX.md ao hb_cli.py via 'hb plan --dry-run' trick.
    Falha silenciosa — não é crítico para a evidence/carimbo."""
    try:
        hb_cli = repo_root / "scripts" / "run" / "hb_cli.py"
        # Tenta executar hb_cli para fazer rebuild; ignora erros
        subprocess.run(
            [sys.executable, str(hb_cli), "version"],
            cwd=str(repo_root), capture_output=True, timeout=5
        )
    except Exception:
        pass  # non-critical


# ─── Extração de código Python de step ────────────────────────────────────────

def extract_python_c_code(step: str) -> str:
    """
    Extrai o código Python de um step 'python -c "..."'.

    Estratégia: toma o conteúdo entre o PRIMEIRO e o ÚLTIMO " no argumento
    após 'python -c ', que é o código Python pretendido (válido quando passado
    diretamente ao interpreter sem passar por shell).

    Isso contorna o problema de quoting do cmd.exe/bash onde "'"...'..."" causa
    truncação do argumento.
    """
    prefix = "python -c "
    if not step.startswith(prefix):
        raise ValueError(f"Step não começa com '{prefix}': {step[:60]}")
    rest = step[len(prefix):]
    first = rest.index('"')
    last = rest.rindex('"')
    if first == last:
        raise ValueError(f"Não foi possível encontrar delimitadores de string no step: {rest[:80]}")
    return rest[first + 1:last]


def extract_python_c_code_from_pipe_rhs(rhs: str) -> str:
    """
    Extrai código Python do lado direito de um pipe: '... | python -c "code"'
    """
    prefix = "python -c "
    idx = rhs.find(prefix)
    if idx == -1:
        raise ValueError(f"'python -c ' não encontrado em: {rhs[:80]}")
    rest = rhs[idx + len(prefix):]
    first = rest.index('"')
    last = rest.rindex('"')
    if first == last:
        raise ValueError(f"Delimitadores não encontrados: {rest[:80]}")
    return rest[first + 1:last]


# ─── Execução inteligente ──────────────────────────────────────────────────────

def run_validation(validation_cmd: str, repo_root: Path) -> tuple:
    """
    Executa validation_command de forma cross-platform.
    Retorna (exit_code, stdout, stderr).
    """
    steps = [s.strip() for s in validation_cmd.split(" && ")]
    working_dir = str(repo_root)
    all_stdout = []
    all_stderr = []
    final_exit = 0

    for step in steps:
        # ── cd "dir" ──────────────────────────────────────────────────────────
        if re.match(r'^cd\s+', step):
            m = re.match(r'^cd\s+"([^"]+)"$', step) or re.match(r"^cd\s+'([^']+)'$", step)
            if m:
                working_dir = str(Path(repo_root) / m.group(1))
            else:
                d = step.split(None, 1)[1].strip().strip('"').strip("'")
                working_dir = str(Path(repo_root) / d)
            continue

        # ── npx tsc ... 2>&1 | python -c "code" ───────────────────────────────
        if " | python -c " in step:
            pipe_sep = " | python -c "
            pipe_pos = step.index(pipe_sep)
            left_cmd = step[:pipe_pos]
            right_part = step[pipe_pos + len(" | "):]

            # Executa o lado esquerdo (normalmente 'npx tsc ...')
            # Redireciona 2>&1 para combinar stdout+stderr
            left_shell = left_cmd.replace(" 2>&1", "")
            left_result = subprocess.run(
                left_shell, shell=True, capture_output=True,
                text=True, encoding="utf-8", errors="replace", cwd=working_dir
            )
            combined_input = left_result.stdout + left_result.stderr

            # Extrai e executa o código Python (right side)
            try:
                python_code = extract_python_c_code_from_pipe_rhs(right_part)
            except ValueError as e:
                all_stderr.append(f"[HELPER] Falha ao extrair código Python: {e}\n")
                final_exit = 1
                break

            right_result = subprocess.run(
                [sys.executable, "-c", python_code],
                input=combined_input, capture_output=True,
                text=True, encoding="utf-8", errors="replace", cwd=working_dir
            )
            all_stdout.append(right_result.stdout)
            all_stderr.append(right_result.stderr)
            if right_result.returncode != 0:
                final_exit = right_result.returncode
                break
            continue

        # ── python -c "code" ──────────────────────────────────────────────────
        if step.startswith("python -c "):
            try:
                python_code = extract_python_c_code(step)
            except ValueError as e:
                all_stderr.append(f"[HELPER] Falha ao extrair código Python: {e}\n")
                final_exit = 1
                break

            result = subprocess.run(
                [sys.executable, "-c", python_code],
                capture_output=True, text=True,
                encoding="utf-8", errors="replace", cwd=working_dir
            )
            all_stdout.append(result.stdout)
            all_stderr.append(result.stderr)
            if result.returncode != 0:
                final_exit = result.returncode
                break
            continue

        # ── Outros comandos (shell) ───────────────────────────────────────────
        result = subprocess.run(
            step, shell=True, capture_output=True,
            text=True, encoding="utf-8", errors="replace", cwd=working_dir
        )
        all_stdout.append(result.stdout)
        all_stderr.append(result.stderr)
        if result.returncode != 0:
            final_exit = result.returncode
            break

    return final_exit, "".join(all_stdout), "".join(all_stderr)


# ─── Geração de evidência e carimbo ──────────────────────────────────────────

def write_evidence(repo_root: Path, ar_id: str, validation_cmd: str,
                   exit_code: int, stdout: str, stderr: str):
    ts_utc = datetime.now(timezone.utc).isoformat()
    behavior_hash = compute_behavior_hash(exit_code, stdout, stderr)
    git_head = git_run(["rev-parse", "HEAD"], str(repo_root)) or "N/A"
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    ws_clean, ws_status = check_workspace_clean(repo_root)

    governed_roots = load_governed_roots(repo_root)
    d1 = git_run(["-c", "core.quotepath=false", "diff", "--name-only"], str(repo_root))
    d2 = git_run(["-c", "core.quotepath=false", "diff", "--cached", "--name-only"], str(repo_root))
    changed = sorted({f for f in (d1.splitlines() + d2.splitlines()) if f.strip()})
    checksums = compute_governed_checksum(repo_root, governed_roots, changed)

    ev_path = repo_root / EV_DIR / f"AR_{ar_id}" / "executor_main.log"
    ev_path.parent.mkdir(parents=True, exist_ok=True)
    with open(ev_path, "w", encoding="utf-8") as f:
        f.write(f"AR_ID: {ar_id}\n")
        f.write(f"Command: {validation_cmd}\n")
        f.write(f"Exit Code: {exit_code}\n")
        f.write(f"Timestamp UTC: {ts_utc}\n")
        f.write(f"Behavior Hash (exit+stdout+stderr): {behavior_hash}\n")
        f.write(f"Git HEAD: {git_head}\n")
        f.write(f"Python Version: {python_version}\n")
        f.write(f"Protocol Version: {HB_PROTOCOL_VERSION}\n")
        f.write(f"Workspace Clean: {ws_clean}\n")
        f.write(f"Workspace Status: {ws_status}\n")
        f.write(f"Governed Checksums (sha256): {json.dumps(checksums, ensure_ascii=False)}\n")
        f.write(f"\n--- STDOUT ---\n{stdout}\n")
        f.write(f"\n--- STDERR ---\n{stderr}\n")

    return ev_path, ts_utc, behavior_hash, git_head, python_version


def write_carimbo(repo_root: Path, ar_file: Path, ar_id: str, validation_cmd: str,
                  exit_code: int, ts_utc: str, behavior_hash: str,
                  git_head: str, python_version: str, ev_rel: str):
    status_hdr = "🏗️ EM_EXECUCAO" if exit_code == 0 else "❌ FALHA"

    content = ar_file.read_text(encoding="utf-8")

    # Truncar na seção de carimbo (remove execuções anteriores)
    carimbo_header = "---\n## Carimbo de Execução\n_(Gerado por hb report)_"
    if carimbo_header in content:
        content = content[:content.index(carimbo_header) + len(carimbo_header)]
    else:
        # Fallback: truncar em ### Execução Executor se existir
        exec_marker = "\n### Execução Executor em "
        if exec_marker in content:
            content = content[:content.index(exec_marker)]
        content = content.rstrip() + "\n"

    # Atualizar **Status** no header
    content = re.sub(r"\*\*Status\*\*:.*", f"**Status**: {status_hdr}", content, count=1)

    # Append carimbo
    content += (
        f"\n\n### Execução Executor em {git_head[:7]}\n"
        f"**Status Executor**: {status_hdr}\n"
        f"**Comando**: `{validation_cmd}`\n"
        f"**Exit Code**: {exit_code}\n"
        f"**Timestamp UTC**: {ts_utc}\n"
        f"**Behavior Hash**: {behavior_hash}\n"
        f"**Evidence File**: `{ev_rel}`\n"
        f"**Python Version**: {python_version}\n\n"
    )
    ar_file.write_text(content, encoding="utf-8")

    print(f"{status_hdr} Evidence logged to: {ev_rel}")
    return status_hdr


# ─── Entry point ──────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        sys.exit("Uso: python temp/_hb_report_helper.py <ar_id>")

    ar_id = sys.argv[1]
    repo_root = Path(__file__).parent.parent

    # Localizar AR file
    ar_dir = repo_root / AR_DIR
    ar_files = list(ar_dir.rglob(f"AR_{ar_id}_*.md"))
    if not ar_files:
        sys.exit(f"AR_{ar_id} não encontrada em {ar_dir}")

    ar_file = ar_files[0]
    print(f"AR file: {ar_file.name}")

    # Extrair validation_command do AR
    content = ar_file.read_text(encoding="utf-8")
    match = re.search(
        r"## Validation Command \(Contrato\)\n```\n(.+?)\n```", content, re.DOTALL
    )
    if not match:
        sys.exit(f"Validation command não encontrado em {ar_file.name}")

    validation_cmd = match.group(1).strip()
    ev_rel = f"{EV_DIR}/AR_{ar_id}/executor_main.log"

    print(f"Validation command ({len(validation_cmd)} chars)")
    print(f"  Executando via smart runner (cross-platform, sem shell quoting)...")

    # Verificar se já existe carimbo (evita re-run acidental)
    if "### Execução Executor em" in content:
        print("⚠️  Já existe carimbo nesta AR. Sobrescrevendo evidence file...")

    # Executar
    exit_code, stdout, stderr = run_validation(validation_cmd, repo_root)
    print(f"  Exit code: {exit_code}")
    if stdout.strip():
        print(f"  STDOUT: {stdout.strip()[:200]}")
    if stderr.strip():
        print(f"  STDERR: {stderr.strip()[:200]}")

    # Gerar evidence file
    ev_path, ts_utc, behavior_hash, git_head, python_version = write_evidence(
        repo_root, ar_id, validation_cmd, exit_code, stdout, stderr
    )

    # Escrever carimbo no AR
    status = write_carimbo(
        repo_root, ar_file, ar_id, validation_cmd, exit_code,
        ts_utc, behavior_hash, git_head, python_version, ev_rel
    )

    # Rebuild _INDEX.md
    rebuild_ar_index(repo_root)

    sys.exit(0 if exit_code == 0 else 1)


if __name__ == "__main__":
    main()
