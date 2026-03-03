"""Helper temporário: extrai validation_command da AR e executa hb report."""
import subprocess
import sys
import re
from pathlib import Path


def get_val_cmd(ar_path: Path) -> str | None:
    content = ar_path.read_text(encoding="utf-8")
    # Try backtick code block first
    backtick3 = chr(96) * 3
    pattern = r"##\s*Validation Command.*?" + backtick3 + r"\n(.*?)\n" + backtick3
    m = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
    if m:
        return m.group(1).strip()
    # Fallback: plain text line after "## Validation Command" heading
    m2 = re.search(r"##\s*Validation Command[^\n]*\n([^\n]+)", content, re.IGNORECASE)
    if m2:
        return m2.group(1).strip()
    return None


def find_ar_path(ar_id: str) -> Path | None:
    """Encontra arquivo AR por ID usando glob."""
    pattern = f"AR_{ar_id}_*.md"
    results = list(Path("docs/hbtrack/ars/features/").glob(pattern))
    if not results:
        results = list(Path("docs/hbtrack/ars/").rglob(pattern))
    return results[0] if results else None


def run_report(ar_id: str) -> int:
    ar_path = find_ar_path(ar_id)
    if ar_path is None:
        print(f"ERROR: AR file not found for AR_{ar_id}", file=sys.stderr)
        return 1
    print(f"[AR_{ar_id}] AR file: {ar_path}")
    cmd = get_val_cmd(ar_path)
    if cmd is None:
        print(f"ERROR: validation_command not found in {ar_path}", file=sys.stderr)
        return 1
    print(f"[AR_{ar_id}] validation_command: {cmd[:80]}...")
    result = subprocess.run(
        [sys.executable, "scripts/run/hb_cli.py", "report", ar_id, cmd]
    )
    print(f"[AR_{ar_id}] exit: {result.returncode}")
    return result.returncode


if __name__ == "__main__":
    ar_id = sys.argv[1]
    exit_code = run_report(ar_id)
    sys.exit(exit_code)
