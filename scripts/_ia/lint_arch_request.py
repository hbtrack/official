#!/usr/bin/env python3
# scripts/_ia/lint_arch_request.py
"""
Regex-based linter for ARCH_REQUEST markdown.

Checks:
- Required header fields
- Required sections (by exact heading match)
- Presence of RFC2119 MUST language in objectives
- Prohibits opinion/hedging words inside normative sections
- SSOT paths must be repo-relative (no Windows absolute paths) unless explicitly allowed

Exit codes:
  0 = OK
  2 = DSL/structure violations
  3 = Normative language violations
  4 = SSOT/path violations
"""

from __future__ import annotations

import argparse
import glob
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple


REQUIRED_HEADER_PATTERNS = [
    (re.compile(r"^#\s+ARCH_REQUEST\s+—\s+.+\s+\(v\d+\.\d+\.\d+\)\s*$", re.MULTILINE), "Missing/invalid title header: '# ARCH_REQUEST — ... (vX.Y.Z)'"),
    (re.compile(r"^\*\*TASK_ID:\*\*\s+\S+", re.MULTILINE), "Missing TASK_ID line: '**TASK_ID:** ...'"),
    (re.compile(r"^\*\*Determinism Score:\*\*\s+[1-5]/5", re.MULTILINE), "Missing Determinism Score line: '**Determinism Score:** N/5'"),
    (re.compile(r"^\*\*Priority:\*\*\s+\S+", re.MULTILINE), "Missing Priority line: '**Priority:** ...'"),
]

REQUIRED_SECTIONS = [
    "## 1. CONTEXTO / PROBLEMA",
    "## 2. OBJETIVOS (MUST)",
    "## 3. SSOT & AUTORIDADE",
    "## 4. DELTA ESTRUTURAL",
    "## 5. PROTOCOLO DO EXECUTOR (MANDATÓRIO)",
    "## 6. ESPECIFICAÇÃO DO event.json",
    "## 7. GATES DE ACEITAÇÃO",
]

# Hedging/opinion words that must not appear in normative sections
HEDGING_WORDS = [
    r"\bacho\b",
    r"\btalvez\b",
    r"\bpode ser\b",
    r"\brecomendo\b",
    r"\bideal\b",
    r"\bna minha opinião\b",
    r"\bseria bom\b",
]

WINDOWS_ABS_PATH = re.compile(r"[A-Za-z]:\\")
UNC_PATH = re.compile(r"\\\\")  # \\server\share

RFC2119_WORD = re.compile(r"\bMUST\b|\bMUST NOT\b|\bSHALL\b|\bSHALL NOT\b|\bSHOULD\b|\bSHOULD NOT\b")


@dataclass
class LintIssue:
    file: str
    code: str
    message: str


def _read_text(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="replace")


def _extract_sections(md: str) -> Dict[str, str]:
    """
    Very simple section extractor keyed by exact heading lines.
    Captures text until next '## ' heading (same level).
    """
    sections: Dict[str, str] = {}
    # find all H2 headings with their positions
    matches = list(re.finditer(r"^##\s+.+$", md, flags=re.MULTILINE))
    for i, m in enumerate(matches):
        heading = m.group(0).strip()
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(md)
        sections[heading] = md[start:end]
    return sections


def lint_file(path: Path, allow_abs_paths: bool) -> List[LintIssue]:
    md = _read_text(path)
    issues: List[LintIssue] = []

    # Header checks
    for pat, msg in REQUIRED_HEADER_PATTERNS:
        if not pat.search(md):
            issues.append(LintIssue(str(path), "ARCH_HDR", msg))

    # Section checks
    sections = _extract_sections(md)
    for s in REQUIRED_SECTIONS:
        if s not in sections:
            issues.append(LintIssue(str(path), "ARCH_SEC", f"Missing required section heading: '{s}'"))

    # Normative language checks (only if objectives section exists)
    obj_key = "## 2. OBJETIVOS (MUST)"
    if obj_key in sections:
        obj_text = sections[obj_key]
        if not RFC2119_WORD.search(obj_text):
            issues.append(LintIssue(str(path), "ARCH_NORM", "Section 'OBJETIVOS (MUST)' must contain RFC2119 keywords (MUST/MUST NOT/SHALL/etc.)."))

        # Hedging words forbidden in objectives
        for w in HEDGING_WORDS:
            if re.search(w, obj_text, flags=re.IGNORECASE):
                issues.append(LintIssue(str(path), "ARCH_HEDGE", f"Hedging/opinion word forbidden in 'OBJETIVOS (MUST)': pattern '{w}'"))

    # Hedging words forbidden in Gates as well
    gates_key = "## 7. GATES DE ACEITAÇÃO"
    if gates_key in sections:
        gates_text = sections[gates_key]
        for w in HEDGING_WORDS:
            if re.search(w, gates_text, flags=re.IGNORECASE):
                issues.append(LintIssue(str(path), "ARCH_HEDGE", f"Hedging/opinion word forbidden in 'GATES DE ACEITAÇÃO': pattern '{w}'"))

    # SSOT/path checks
    ssot_key = "## 3. SSOT & AUTORIDADE"
    if ssot_key in sections and not allow_abs_paths:
        ssot_text = sections[ssot_key]
        if WINDOWS_ABS_PATH.search(ssot_text) or UNC_PATH.search(ssot_text):
            issues.append(LintIssue(str(path), "ARCH_PATH", "SSOT section contains absolute/UNC Windows paths. Use repo-relative paths (e.g., 'docs/...')."))

    # If there are missing headings, treat as structure violation even if other issues exist
    return issues


def classify_exit_code(issues: List[LintIssue]) -> int:
    if not issues:
        return 0
    codes = {i.code for i in issues}
    # priority: PATH (4) > NORM (3) > structure (2)
    if any(c in {"ARCH_PATH"} for c in codes):
        return 4
    if any(c in {"ARCH_NORM", "ARCH_HEDGE"} for c in codes):
        return 3
    return 2


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", help="Single file to lint")
    ap.add_argument("--glob", dest="glob_pattern", help="Glob pattern for files (e.g., 'docs/**/ARCH_REQUEST*.md')")
    ap.add_argument("--allow-absolute-paths", action="store_true", help="Allow Windows absolute paths in SSOT (not recommended)")
    args = ap.parse_args()

    targets: List[str] = []
    if args.file:
        targets = [args.file]
    elif args.glob_pattern:
        targets = glob.glob(args.glob_pattern, recursive=True)
    else:
        print("ERROR: provide --file or --glob", file=sys.stderr)
        return 2

    if not targets:
        print("[OK] No files matched. Nothing to lint.")
        return 0

    all_issues: List[LintIssue] = []
    for t in sorted(set(targets)):
        p = Path(t)
        if not p.exists() or not p.is_file():
            continue
        all_issues.extend(lint_file(p, allow_abs_paths=args.allow_absolute_paths))

    if all_issues:
        for i in all_issues:
            print(f"{i.file}: {i.code}: {i.message}", file=sys.stderr)

    rc = classify_exit_code(all_issues)
    if rc == 0:
        print("[OK] ARCH_REQUEST lint passed.")
    else:
        print(f"[FAIL] ARCH_REQUEST lint failed (exit {rc}).", file=sys.stderr)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())