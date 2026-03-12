"""
Markdown report writer — CONNECTIVITY_DIAGNOSTIC_CONTRACT v1.1.0
Writes _reports/connectivity_diagnostic_report.md
"""
from __future__ import annotations

import pathlib

from tools.diagnostics.models.diagnostic_result import DiagnosticResult


def write_md_report(result: DiagnosticResult, path: str) -> None:
    """Persist a human-readable diagnostic summary as Markdown."""
    output_path = pathlib.Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    d = result.to_dict()
    status_badge = "✅ PASS" if d["status"] == "pass" else "❌ FAIL"

    lines: list = [
        "# Connectivity Diagnostic Report",
        "",
        f"**Contract:** `{d['contract']}` v{d['version']}",
        f"**Status:** {status_badge}  |  **Exit Code:** `{d['exit_code']}`",
        "",
        "---",
        "",
        "## Inputs",
        "",
        "| Parameter | Value |",
        "|-----------|-------|",
    ]
    for k, v in d.get("inputs", {}).items():
        lines.append(f"| `{k}` | `{v}` |")

    lines += [
        "",
        "---",
        "",
        "## Root Cause",
        "",
        f"**Code:** `{d['root_cause_code']}`",
        "",
        f"**Summary:** {d['root_cause_summary']}",
        "",
        f"**Recommended Action:** {d['recommended_action']}",
        "",
        "---",
        "",
        "## Checks",
        "",
        "| # | Check | Status | Evidence |",
        "|---|-------|--------|----------|",
    ]

    for i, check in enumerate(d.get("checks", []), 1):
        evidence = check.get("evidence", "")
        if isinstance(evidence, dict):
            evidence = "; ".join(f"{k}={v}" for k, v in evidence.items())
        elif not isinstance(evidence, str):
            evidence = str(evidence)
        # Truncate long evidence for readability
        if len(evidence) > 120:
            evidence = evidence[:117] + "..."
        status_icon = {"pass": "✅", "fail": "❌", "skip": "⏭️", "warn": "⚠️"}.get(
            check.get("status", ""), "?"
        )
        lines.append(
            f"| {i} | `{check['name']}` | {status_icon} {check.get('status', '')} | {evidence} |"
        )

    with open(output_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
