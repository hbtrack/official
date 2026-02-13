#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HB Track - compact_exec_logs.py (v0.1.0)
Deterministic generator/validator for:
  - docs/execution_tasks/STATUS_BOARD.md
  - docs/execution_tasks/CHANGELOG.md
  - docs/execution_tasks/EXECUTIONLOG.md
  - docs/_canon/00_START_HERE.md (or ./00_START_HERE.md) section between markers
  - docs/execution_tasks/artifacts/<TASK_ID>/{HUMAN_SUMMARY.md, PROOFS.md} presence/format

Modes:
  --write : generate/update derived outputs + auto-create missing HUMAN_SUMMARY/PROOFS from event.json (deterministic)
  --check : validate presence/format + validate derived outputs are exact match (byte-for-byte)

Exit codes:
  0 OK
  2 MISSING_REQUIRED (event.json / HUMAN_SUMMARY.md / PROOFS.md / derived files)
  3 INVALID_FORMAT   (bad json / missing headings / invalid min format)
  4 MISMATCH_DERIVED (STATUS_BOARD/CHANGELOG/EXECUTIONLOG/LAST_TASKS differs from recomputed)
  5 UNEXPECTED
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

def get_repo_root() -> Path:
  """Find the root of the repo (where .git is)."""
  # Try starting from script location
  start = Path(__file__).resolve().parent
  for parent in [start] + list(start.parents):
    if (parent / ".git").exists():
      return parent
  # Fallback to CWD
  cwd = Path.cwd().resolve()
  for parent in [cwd] + list(cwd.parents):
    if (parent / ".git").exists():
      return parent
  return cwd

REPO_ROOT = get_repo_root()

ARTIFACTS_ROOT = REPO_ROOT / "docs" / "execution_tasks" / "artifacts"
OUTPUT_DIR = REPO_ROOT / "docs" / "execution_tasks"
STATUS_BOARD_PATH = OUTPUT_DIR / "STATUS_BOARD.md"
CHANGELOG_PATH = OUTPUT_DIR / "CHANGELOG.md"
EXECUTIONLOG_PATH = OUTPUT_DIR / "EXECUTIONLOG.md"

START_HERE_CANDIDATES = [
  REPO_ROOT / "docs" / "_canon" / "00_START_HERE.md",
  REPO_ROOT / "00_START_HERE.md",
]

LAST_TASKS_START = "<!-- AUTO:LAST_TASKS_START -->"
LAST_TASKS_END = "<!-- AUTO:LAST_TASKS_END -->"

REQUIRED_HUMAN_HEADINGS = [
  "O que foi implementado:",
  "O que NÃO foi implementado:",
  "Impacto:",
  "Como validar:",
]

# Human summary constraints (non-empty lines)
HUMAN_MIN_LINES = 5
HUMAN_MAX_LINES = 15

PROOFS_REQUIRED_KEYS = [
  "task_id:",
  "status:",
  "scope:",
  "evidence_sha256:",
  "evidence_files:",
]

def _read_text(path: Path) -> str:
  return path.read_text(encoding="utf-8")

def _write_text_if_changed(path: Path, content: str) -> bool:
  # Deterministic newline normalization: always '\n', always end with '\n'
  norm = content.replace("\r\n", "\n").replace("\r", "\n")
  if not norm.endswith("\n"):
    norm += "\n"
  if path.exists():
    current = _read_text(path).replace("\r\n", "\n").replace("\r", "\n")
    # Ensure current also ends with '\n' for fair comparison
    if not current.endswith("\n"):
      current += "\n"
    if current == norm:
      return False
  path.parent.mkdir(parents=True, exist_ok=True)
  path.write_text(norm, encoding="utf-8", newline="\n")
  return True

def _sha256_bytes(b: bytes) -> str:
  h = hashlib.sha256()
  h.update(b)
  return h.hexdigest()

def _sha256_files(paths: List[Path]) -> str:
  h = hashlib.sha256()
  for p in paths:
    content = p.read_bytes()
    # Normalize PROOFS.md for deterministic hashing: replace evidence_sha256 line with placeholder
    if p.name == "PROOFS.md":
      text = content.decode("utf-8")
      # Replace any evidence_sha256 line with fixed placeholder
      import re
      text = re.sub(r"evidence_sha256:.*", "evidence_sha256: SHA256_PLACEHOLDER", text)
      content = text.encode("utf-8")
    h.update(content)
  return h.hexdigest()

def _safe_load_json(path: Path) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
  try:
    raw = path.read_text(encoding="utf-8")
  except Exception as e:
    return None, f"read_error:{e}"
  try:
    obj = json.loads(raw)
  except Exception as e:
    return None, f"json_error:{e}"
  if not isinstance(obj, dict):
    return None, "json_error:root_not_object"
  return obj, None

def _parse_iso(ts: Optional[str]) -> Optional[datetime]:
  if not ts or not isinstance(ts, str):
    return None
  # Accept Z suffix or offset; fallback None on parse errors.
  try:
    if ts.endswith("Z"):
      return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    return datetime.fromisoformat(ts)
  except Exception:
    return None

def _git_head_commit() -> str:
  try:
    r = subprocess.run(
      ["git", "rev-parse", "HEAD"],
      capture_output=True,
      text=True,
      check=True,
    )
    return r.stdout.strip()
  except Exception:
    return ""

def _count_nonempty_lines(text: str) -> int:
  lines = [ln.strip() for ln in text.replace("\r\n", "\n").replace("\r", "\n").split("\n")]
  return sum(1 for ln in lines if ln)

def _validate_human_summary(text: str) -> List[str]:
  errors: List[str] = []
  norm = text.replace("\r\n", "\n").replace("\r", "\n")
  lines = [ln.strip() for ln in norm.split("\n") if ln.strip()]
  # headings presence (case-sensitive)
  for h in REQUIRED_HUMAN_HEADINGS:
    if not any(ln.startswith(h) for ln in lines):
      errors.append(f"missing_heading:{h}")
  # line count constraint
  nonempty = len(lines)
  if nonempty < HUMAN_MIN_LINES or nonempty > HUMAN_MAX_LINES:
    errors.append(f"invalid_line_count:{nonempty} (expected {HUMAN_MIN_LINES}-{HUMAN_MAX_LINES} non-empty lines)")
  return errors

def _validate_proofs(text: str) -> List[str]:
  errors: List[str] = []
  norm = text.replace("\r\n", "\n").replace("\r", "\n")
  lines = [ln.strip() for ln in norm.split("\n") if ln.strip()]
  for k in PROOFS_REQUIRED_KEYS:
    if not any(ln.lower().startswith(k) for ln in lines):
      errors.append(f"missing_key:{k}")
  return errors

def _extract_first_sentence(value: str, max_len: int = 120) -> str:
  v = " ".join(value.strip().split())
  if not v:
    return ""
  # sentence-ish split
  m = re.split(r"[.!?]\s+", v, maxsplit=1)
  out = m[0].strip()
  if len(out) > max_len:
    out = out[: max_len - 1].rstrip() + "…"
  return out

def _rel(path: Path) -> Path:
  """Get path relative to REPO_ROOT if absolute."""
  if path.is_absolute():
    try:
      return path.relative_to(REPO_ROOT)
    except ValueError:
      return path
  return path

def _render_human_summary(event: Dict[str, Any]) -> str:
  # Deterministic: no current timestamps, only SSOT-derived fields.
  short_title = str(event.get("short_title") or event.get("notes_short") or "").strip()
  scope = str(event.get("scope") or event.get("area") or "Unknown").strip()
  status = str(event.get("status") or "UNKNOWN").strip()
  artifacts = event.get("artifacts") if isinstance(event.get("artifacts"), list) else []
  artifacts_preview = ", ".join(str(x) for x in artifacts[:3]) if artifacts else "N/A"

  impl = short_title or f"Task {event.get('task_id', 'UNKNOWN')} ({scope})"
  impl_1 = _extract_first_sentence(impl)

  return "\n".join([
    f"O que foi implementado: {impl_1}",
    "O que NÃO foi implementado: N/A (derivado de SSOT; refine manualmente se aplicável)",
    f"Impacto: status={status} | area={scope} | artifacts_preview={artifacts_preview}",
    "Como validar: python scripts/compact_exec_logs.py --check",
    "Notas: este resumo é determinístico e pode ser editado, mantendo headings e 5–10 linhas.",
  ])

def _render_proofs(event: Dict[str, Any], evidence_sha256: str, evidence_files: List[Path]) -> str:
  task_id = str(event.get("task_id") or "UNKNOWN").strip()
  status = str(event.get("status") or "UNKNOWN").strip()
  scope = str(event.get("scope") or event.get("area") or "Unknown").strip()
  contract = str(event.get("contract_ref") or event.get("contract") or "N/A").strip()

  tests = event.get("tests")
  if isinstance(tests, list):
    tests_str = ", ".join(str(x) for x in tests)
  else:
    tests_str = "python scripts/compact_exec_logs.py --check"

  files_str = ", ".join(_rel(p).as_posix() for p in evidence_files)

  return "\n".join([
    f"task_id: {task_id}",
    f"status: {status}",
    f"scope: {scope}",
    f"contract_ref: {contract}",
    f"tests: {tests_str}",
    f"evidence_sha256: {evidence_sha256}",
    f"evidence_files: {files_str}",
  ])

@dataclass(frozen=True)
class TaskRow:
  task_id: str
  status: str
  area: str
  resumo: str
  commit: str
  evidence_sha256: str
  artifacts_dir: Path
  ts_sort: str  # ISO string for ordering (stable)

def _task_timestamp_sort_key(event: Dict[str, Any]) -> str:
  # Prefer timestamp_end, then timestamp_start; fallback empty.
  te = event.get("timestamp_end")
  ts = event.get("timestamp_start")
  dt = _parse_iso(te) or _parse_iso(ts)
  if not dt:
    return ""
  # normalize ISO with Z for sorting stability
  try:
    iso = dt.astimezone().isoformat()
  except Exception:
    iso = dt.isoformat()
  return iso

def _discover_tasks() -> Tuple[List[TaskRow], List[str], List[str]]:
  missing: List[str] = []
  invalid: List[str] = []
  rows: List[TaskRow] = []

  if not ARTIFACTS_ROOT.exists():
    missing.append(f"missing_dir:{ARTIFACTS_ROOT.as_posix()}")
    return rows, missing, invalid

  for d in sorted([p for p in ARTIFACTS_ROOT.iterdir() if p.is_dir()], key=lambda p: p.name):
    task_id_dir = d.name
    event_path = d / "event.json"
    if not event_path.exists():
      missing.append(f"{task_id_dir}:missing_event.json")
      continue

    event, err = _safe_load_json(event_path)
    if err or event is None:
      invalid.append(f"{task_id_dir}:invalid_event.json:{err}")
      continue

    task_id = str(event.get("task_id") or "").strip()
    if not task_id:
      invalid.append(f"{task_id_dir}:event_missing_task_id")
      continue
    if task_id != task_id_dir:
      invalid.append(f"{task_id_dir}:task_id_mismatch:event={task_id}")
      continue

    status = str(event.get("status") or "UNKNOWN").strip()
    area = str(event.get("scope") or event.get("area") or "Unknown").strip()
    short_title = str(event.get("short_title") or event.get("notes_short") or "").strip()
    resumo = _extract_first_sentence(short_title) if short_title else f"{task_id} ({area})"
    commit = str(event.get("git_commit") or "").strip()

    # Ensure deterministic evidence hash is based on required trio (event + human + proofs).
    human_path = d / "HUMAN_SUMMARY.md"
    proofs_path = d / "PROOFS.md"
    evidence_files = [event_path, human_path, proofs_path]

    # evidence_sha256 computed later (after auto-create in --write)
    rows.append(TaskRow(
      task_id=task_id,
      status=status,
      area=area,
      resumo=resumo,
      commit=commit,
      evidence_sha256="",
      artifacts_dir=d,
      ts_sort=_task_timestamp_sort_key(event),
    ))

  return rows, missing, invalid

def _ensure_human_artifacts(task: TaskRow, mode_write: bool) -> Tuple[Optional[str], Optional[str], List[str], List[str]]:
  missing: List[str] = []
  invalid: List[str] = []
  d = task.artifacts_dir
  event_path = d / "event.json"
  human_path = d / "HUMAN_SUMMARY.md"
  proofs_path = d / "PROOFS.md"

  event, err = _safe_load_json(event_path)
  if err or event is None:
    invalid.append(f"{task.task_id}:invalid_event.json:{err}")
    return None, None, missing, invalid

  # HUMAN_SUMMARY
  if not human_path.exists():
    if mode_write:
      _write_text_if_changed(human_path, _render_human_summary(event))
    else:
      missing.append(f"{task.task_id}:missing_HUMAN_SUMMARY.md")
  if human_path.exists():
    hs = _read_text(human_path)
    errs = _validate_human_summary(hs)
    if errs:
      invalid.append(f"{task.task_id}:HUMAN_SUMMARY_invalid:{'|'.join(errs)}")

  # PROOFS (needs evidence hash; compute provisional after ensuring both exist)
  if not proofs_path.exists():
    if not mode_write:
      missing.append(f"{task.task_id}:missing_PROOFS.md")

  # At this point, if write mode and proofs missing, we need to compute evidence hash over trio.
  if mode_write and (not proofs_path.exists()):
    # Ensure human exists (write mode may have created it)
    if not human_path.exists():
      _write_text_if_changed(human_path, _render_human_summary(event))
    # Compute evidence hash with a placeholder PROOFS content first? No: compute after writing proofs.
    # Use temporary deterministic placeholder to bootstrap, then recompute and rewrite proofs once.
    placeholder = "\n".join([
      f"task_id: {task.task_id}",
      f"status: {str(event.get('status') or 'UNKNOWN').strip()}",
      f"scope: {str(event.get('scope') or event.get('area') or 'Unknown').strip()}",
      "contract_ref: N/A",
      "tests: python scripts/compact_exec_logs.py --check",
      "evidence_sha256: PENDING",
      f"evidence_files: {event_path.as_posix()}, {human_path.as_posix()}, {proofs_path.as_posix()}",
    ])
    _write_text_if_changed(proofs_path, placeholder)

    # Now compute final evidence hash and rewrite PROOFS deterministically.
    evidence_sha256 = _sha256_files([event_path, human_path, proofs_path])
    _write_text_if_changed(proofs_path, _render_proofs(event, evidence_sha256, [event_path, human_path, proofs_path]))

  # Validate proofs format
  if proofs_path.exists():
    ps = _read_text(proofs_path)
    errs = _validate_proofs(ps)
    if errs:
      invalid.append(f"{task.task_id}:PROOFS_invalid:{'|'.join(errs)}")

  # Compute final evidence hash (post any rewrites)
  if human_path.exists() and proofs_path.exists():
    evidence_sha256 = _sha256_files([event_path, human_path, proofs_path])
    # Ensure PROOFS contains the exact sha (enforce deterministically in write mode)
    if mode_write:
      # Reload event for rendering
      event2, _ = _safe_load_json(event_path)
      if event2:
        _write_text_if_changed(proofs_path, _render_proofs(event2, evidence_sha256, [event_path, human_path, proofs_path]))
    return evidence_sha256, _extract_first_sentence(str(event.get("short_title") or event.get("notes_short") or "")) or task.resumo, missing, invalid

  if not human_path.exists():
    missing.append(f"{task.task_id}:missing_HUMAN_SUMMARY.md")
  if not proofs_path.exists():
    missing.append(f"{task.task_id}:missing_PROOFS.md")

  return None, None, missing, invalid

def _render_status_board(rows: List[TaskRow]) -> str:
  header = "\n".join([
    "# STATUS_BOARD",
    "",
    "Derivado de: docs/execution_tasks/artifacts/**/event.json (SSOT_SECONDARY).",
    "Regra: NÃO editar manualmente este arquivo; usar `python scripts/compact_exec_logs.py --write`.",
    "",
    "| TASK_ID | Status | Área | Resumo 1-linha | Commit | Evidence SHA256 | Path artifacts |",
    "|---|---|---|---|---|---|---|",
  ])
  lines = [header]
  for r in rows:
    human_link = (_rel(r.artifacts_dir) / "HUMAN_SUMMARY.md").as_posix()
    artifacts_link = _rel(r.artifacts_dir).as_posix()
    commit = r.commit
    lines.append(
      f"| [{r.task_id}]({human_link}) | {r.status} | {r.area} | {r.resumo} | {commit} | {r.evidence_sha256} | {artifacts_link} |"
    )
  return "\n".join(lines)

def _render_changelog(rows: List[TaskRow]) -> str:
  out = ["# CHANGELOG", "", "Uma linha por TASK_ID (derivado de event.json).", ""]
  for r in rows:
    # Use ts_sort (may be empty); show only date part if present
    date = r.ts_sort.split("T")[0] if r.ts_sort else "UNKNOWN_DATE"
    out.append(f"- {date} | {r.task_id} | {r.status} | {r.area} | {r.resumo} | [{r.task_id}]({_rel(r.artifacts_dir / 'HUMAN_SUMMARY.md').as_posix()})")
  return "\n".join(out)

def _render_executionlog(rows: List[TaskRow]) -> str:
  out = ["# EXECUTIONLOG", "", "Índice curto (derivado de event.json).", "Validação canônica: `python scripts/compact_exec_logs.py --check`.", ""]
  for r in rows:
    out.append(f"- {r.task_id} | status={r.status} | evidence_sha256={r.evidence_sha256} | artifacts={_rel(r.artifacts_dir).as_posix()}")
  return "\n".join(out)

def _select_start_here_path() -> Optional[Path]:
  for p in START_HERE_CANDIDATES:
    if p.exists():
      return p
  return None

def _render_last_tasks_block(start_here_path: Path, rows_sorted_desc: List[TaskRow]) -> str:
  # Build relative links from start_here_path to each HUMAN_SUMMARY
  base = start_here_path.parent
  lines = []
  for r in rows_sorted_desc[:10]:
    target = Path(r.artifacts_dir.as_posix()) / "HUMAN_SUMMARY.md"
    rel = os.path.relpath(target.as_posix(), base.as_posix()).replace("\\", "/")
    lines.append(f"- [{r.task_id}]({rel}) — {r.status} — {r.resumo}")
  body = "\n".join(lines) if lines else "- (nenhuma task encontrada)"
  return "\n".join([
    LAST_TASKS_START,
    "## Últimas 10 tasks implementadas",
    body,
    LAST_TASKS_END,
  ])

def _upsert_last_tasks_section(start_here_path: Path, rows_sorted_desc: List[TaskRow], mode_write: bool) -> Tuple[Optional[str], Optional[str]]:
  """
  Returns (new_content, error) where:
    - new_content is the updated file content (only if mode_write)
    - error is set if markers missing in check mode
  """
  current = _read_text(start_here_path).replace("\r\n", "\n").replace("\r", "\n")
  new_block = _render_last_tasks_block(start_here_path, rows_sorted_desc)

  if (LAST_TASKS_START not in current) or (LAST_TASKS_END not in current):
    if not mode_write:
      return None, "missing_markers"
    # Deterministic append (first-time install)
    updated = current.rstrip("\n") + "\n\n" + new_block + "\n"
    return updated, None

  # Replace block between markers (inclusive)
  pattern = re.compile(re.escape(LAST_TASKS_START) + r".*?" + re.escape(LAST_TASKS_END), re.DOTALL)
  updated = pattern.sub(new_block, current, count=1)
  return updated, None

def _sort_rows_for_board(rows: List[TaskRow]) -> List[TaskRow]:
  # Board stable order: newest first if ts_sort present, else lexical by task_id
  def key(r: TaskRow) -> Tuple[int, str, str]:
    has_ts = 1 if r.ts_sort else 0
    # reverse ts_sort in sort by using negative flag + later reverse
    return (has_ts, r.ts_sort, r.task_id)
  # We'll sort ascending then reverse for newest first when ts present.
  sorted_rows = sorted(rows, key=key)
  return list(reversed(sorted_rows))

def main(argv: List[str]) -> int:
  ap = argparse.ArgumentParser(add_help=True)
  g = ap.add_mutually_exclusive_group(required=True)
  g.add_argument("--check", action="store_true")
  g.add_argument("--write", action="store_true")
  args = ap.parse_args(argv)

  mode_write = bool(args.write)

  # Discover tasks (event.json must exist)
  rows, missing0, invalid0 = _discover_tasks()
  if missing0 or invalid0:
    # In write mode we still cannot create event.json; fail.
    msgs = missing0 + invalid0
    sys.stderr.write("ERROR: preflight failures\n")
    for m in msgs:
      sys.stderr.write(f"- {m}\n")
    return 2 if missing0 else 3

  # Ensure human artifacts exist + valid; compute evidence sha
  missing: List[str] = []
  invalid: List[str] = []
  enriched: List[TaskRow] = []

  for r in rows:
    evidence_sha, resumo_override, miss, inv = _ensure_human_artifacts(r, mode_write)
    missing.extend(miss)
    invalid.extend(inv)

    if evidence_sha is None:
      continue

    # Patch commit if empty (optional: fill from current HEAD, but only if event doesn't carry it)
    commit = r.commit
    if not commit:
      commit = ""

    resumo = resumo_override or r.resumo
    enriched.append(TaskRow(
      task_id=r.task_id,
      status=r.status,
      area=r.area,
      resumo=resumo,
      commit=commit,
      evidence_sha256=evidence_sha,
      artifacts_dir=r.artifacts_dir,
      ts_sort=r.ts_sort,
    ))

  if missing or invalid:
    sys.stderr.write("ERROR: human artifacts validation failures\n")
    for m in missing:
      sys.stderr.write(f"- {m}\n")
    for m in invalid:
      sys.stderr.write(f"- {m}\n")
    return 2 if missing else 3

  # Derive outputs
  rows_board = _sort_rows_for_board(enriched)
  status_board = _render_status_board(rows_board)
  changelog = _render_changelog(rows_board)
  executionlog = _render_executionlog(rows_board)

  # Update STATUS_BOARD/CHANGELOG/EXECUTIONLOG
  if mode_write:
    _write_text_if_changed(STATUS_BOARD_PATH, status_board)
    _write_text_if_changed(CHANGELOG_PATH, changelog)
    _write_text_if_changed(EXECUTIONLOG_PATH, executionlog)
  else:
    # Must exist and must match expected bytes
    mismatches: List[str] = []
    for p, expected in [
      (STATUS_BOARD_PATH, status_board),
      (CHANGELOG_PATH, changelog),
      (EXECUTIONLOG_PATH, executionlog),
    ]:
      if not p.exists():
        mismatches.append(f"missing_derived:{p.as_posix()}")
        continue
      current = _read_text(p).replace("\r\n", "\n").replace("\r", "\n")
      exp = expected.replace("\r\n", "\n").replace("\r", "\n")
      if not exp.endswith("\n"):
        exp += "\n"
      if current != exp:
        mismatches.append(f"mismatch_derived:{p.as_posix()}")
    if mismatches:
      sys.stderr.write("ERROR: derived outputs mismatch\n")
      for m in mismatches:
        sys.stderr.write(f"- {m}\n")
      return 4 if any(m.startswith("mismatch_derived") for m in mismatches) else 2

  # Update START_HERE last tasks section
  start_here = _select_start_here_path()
  if start_here is None:
    sys.stderr.write("ERROR: start_here_missing (docs/_canon/00_START_HERE.md or ./00_START_HERE.md)\n")
    return 2

  updated, err = _upsert_last_tasks_section(start_here, rows_board, mode_write)
  if err:
    sys.stderr.write(f"ERROR: {err} ({LAST_TASKS_START} / {LAST_TASKS_END})\n")
    return 3
  if mode_write and updated is not None:
    _write_text_if_changed(start_here, updated)
  if not mode_write:
    # Validate current equals recomputed
    new_expected, _ = _upsert_last_tasks_section(start_here, rows_board, True)
    current = _read_text(start_here).replace("\r\n", "\n").replace("\r", "\n")
    exp = (new_expected or "").replace("\r\n", "\n").replace("\r", "\n")
    if not exp.endswith("\n"):
      exp += "\n"
    if current != exp:
      sys.stderr.write("ERROR: mismatch_start_here_last_tasks\n")
      return 4

  # Final assertion: STATUS_BOARD must have >= 1 task row
  if len(rows_board) < 1:
    sys.stderr.write("ERROR: no_tasks_found_in_event.json\n")
    return 3

  return 0

if __name__ == "__main__":
  try:
    raise SystemExit(main(sys.argv[1:]))
  except SystemExit as e:
    raise
  except Exception as e:
    sys.stderr.write(f"ERROR: unexpected:{e}\n")
    raise SystemExit(5)
