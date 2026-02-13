#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HB Track - bootstrap_task.py (v0.1.0)
Deterministic scaffolding for a new execution task artifacts folder.

Creates (if missing):
  docs/execution_tasks/artifacts/<TASK_ID>/
    - event.json        (SSOT_SECONDARY input for compact_exec_logs)
    - HUMAN_SUMMARY.md  (human-readable; required headings)
    - PROOFS.md         (deterministic placeholders; final sha filled by compact_exec_logs)

This script DOES NOT generate derived outputs (STATUS_BOARD/CHANGELOG/EXECUTIONLOG/START_HERE).
Use: python scripts/compact_exec_logs.py --write

Exit codes:
  0 OK
  2 INVALID_ARGS
  3 NOT_A_GIT_REPO / REPO_ROOT_DETECT_FAIL
  4 EXISTS_CONFLICT (files exist and --force not set)
  5 WRITE_ERROR
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

ARTIFACTS_ROOT_REL = Path("docs/execution_tasks/artifacts")

REQUIRED_HUMAN_HEADINGS = [
  "O que foi implementado:",
  "O que NÃO foi implementado:",
  "Impacto:",
  "Como validar:",
]

def _utc_now_iso() -> str:
  return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def _run_git(args: list[str]) -> Tuple[int, str, str]:
  p = subprocess.run(["git"] + args, capture_output=True, text=True)
  return p.returncode, p.stdout.strip(), p.stderr.strip()

def _detect_repo_root() -> Optional[Path]:
  rc, out, _ = _run_git(["rev-parse", "--show-toplevel"])
  if rc == 0 and out:
    return Path(out)
  # fallback: search parents for .git
  here = Path(__file__).resolve()
  for p in [here.parent] + list(here.parents):
    if (p / ".git").exists():
      return p
  return None

def _normalize_newlines(s: str) -> str:
  s = s.replace("\r\n", "\n").replace("\r", "\n")
  if not s.endswith("\n"):
    s += "\n"
  return s

def _write_text(path: Path, content: str) -> None:
  path.parent.mkdir(parents=True, exist_ok=True)
  path.write_text(_normalize_newlines(content), encoding="utf-8", newline="\n")

def _write_json(path: Path, obj: Dict[str, Any]) -> None:
  path.parent.mkdir(parents=True, exist_ok=True)
  # Deterministic JSON formatting
  content = json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
  path.write_text(content, encoding="utf-8", newline="\n")

def _validate_task_id(task_id: str) -> bool:
  # Uppercase letters, digits, dash; must start with letter; no spaces
  return bool(re.fullmatch(r"[A-Z][A-Z0-9\-]{2,80}", task_id))

def _render_human_summary(task_id: str, one_liner: str) -> str:
  # 5–10 non-empty lines, headings case-sensitive
  ol = " ".join(one_liner.strip().split())
  if not ol:
    ol = "(descrever em 1 linha; manter determinístico)"
  lines = [
    f"O que foi implementado: {task_id} — {ol}",
    "O que NÃO foi implementado: N/A",
    f"Impacto: area=Unknown | status=DRAFT",
    "Como validar: python scripts/compact_exec_logs.py --check",
    "Notas: manter headings; edição permitida apenas no conteúdo após ':'",
  ]
  return "\n".join(lines)

def _render_proofs(task_id: str) -> str:
  # Placeholders; compact_exec_logs.py --write preencherá evidence_sha256 final
  files = f"docs/execution_tasks/artifacts/{task_id}/event.json, docs/execution_tasks/artifacts/{task_id}/HUMAN_SUMMARY.md, docs/execution_tasks/artifacts/{task_id}/PROOFS.md"
  lines = [
    f"task_id: {task_id}",
    "status: DRAFT",
    "scope: Unknown",
    "contract_ref: N/A",
    "tests: python scripts/compact_exec_logs.py --check",
    "evidence_sha256: PENDING",
    f"evidence_files: {files}",
  ]
  return "\n".join(lines)

def _make_event_json(task_id: str, one_liner: str, scope: str) -> Dict[str, Any]:
  # Minimal schema (compatible with compact_exec_logs expectations)
  return {
    "artifacts": [],
    "notes_short": one_liner.strip(),
    "scope": scope.strip() or "Unknown",
    "short_title": one_liner.strip(),
    "status": "DRAFT",
    "task_id": task_id,
    "timestamp_start": _utc_now_iso(),
    "timestamp_end": _utc_now_iso(),
    "type": "EXEC_TASK",
    "version_intent": "0.1.0",
  }

def main(argv: list[str]) -> int:
  ap = argparse.ArgumentParser(add_help=True)
  ap.add_argument("task_id", help="Ex: ARCH-XYZ-001 (uppercase, digits, dash)")
  ap.add_argument("--one-liner", "--title", dest="one_liner", default="", help="Resumo 1-linha (vai para event.json + HUMAN_SUMMARY)")
  ap.add_argument("--scope", default="Unknown", help="Área/escopo (vai para event.json)")
  ap.add_argument("--force", action="store_true", help="Sobrescrever arquivos existentes")
  args = ap.parse_args(argv)

  task_id = args.task_id.strip()
  if not _validate_task_id(task_id):
    sys.stderr.write("ERROR: invalid TASK_ID format. Expected: [A-Z][A-Z0-9-]{2,80}\n")
    return 2

  repo_root = _detect_repo_root()
  if repo_root is None:
    sys.stderr.write("ERROR: repo root detect failed (not a git repo?)\n")
    return 3

  target_dir = repo_root / ARTIFACTS_ROOT_REL / task_id
  event_path = target_dir / "event.json"
  human_path = target_dir / "HUMAN_SUMMARY.md"
  proofs_path = target_dir / "PROOFS.md"

  # conflict handling
  if not args.force:
    exists = [p for p in [event_path, human_path, proofs_path] if p.exists()]
    if exists:
      sys.stderr.write("ERROR: artifacts already exist (use --force to overwrite):\n")
      for p in exists:
        try:
           sys.stderr.write(f"- {p.relative_to(repo_root).as_posix()}\n")
        except ValueError:
           sys.stderr.write(f"- {p.as_posix()}\n")
      return 4

  try:
    event = _make_event_json(task_id, args.one_liner, args.scope)
    _write_json(event_path, event)
    _write_text(human_path, _render_human_summary(task_id, args.one_liner))
    _write_text(proofs_path, _render_proofs(task_id))

    # minimal heading assertion (self-check)
    hs = human_path.read_text(encoding="utf-8")
    for h in REQUIRED_HUMAN_HEADINGS:
      if h not in hs:
        raise RuntimeError(f"human_summary_missing_heading:{h}")

  except Exception as e:
    sys.stderr.write(f"ERROR: write_error:{e}\n")
    return 5

  try:
     rel = target_dir.relative_to(repo_root).as_posix()
  except ValueError:
     rel = target_dir.as_posix()
  sys.stdout.write(f"OK: created {rel}\n")
  return 0

if __name__ == "__main__":
  raise SystemExit(main(sys.argv[1:]))
