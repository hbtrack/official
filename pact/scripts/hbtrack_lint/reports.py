"""
Geração de relatórios de plano (JSON + Markdown).

SSOT: docs/hbtrack/modulos/atletas/MOTORES.md
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


def write_plan_reports(
    reports_dir: Path,
    status: str,
    errors: list,
    warnings: list,
    results: list,
    handoff_path: Path | None,
    anchor_manifest_path: Path | None,
) -> None:
    """Escreve _reports/hb_plan_result.json e _reports/hb_plan_result.md."""
    reports_dir.mkdir(parents=True, exist_ok=True)

    summary = {
        "status": status,
        "module_id": "ATHLETES",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "errors": errors,
        "warnings": warnings,
        "results": results,
        "handoff_path": str(handoff_path) if handoff_path else None,
        "anchor_manifest_path": str(anchor_manifest_path) if anchor_manifest_path else None,
        "checked_documents": [r["document"] for r in results if "document" in r],
        "passed_rules": [r["rule_id"] for r in results if isinstance(r, dict) and r.get("status") == "PASS"],
        "failed_rules": [e.get("rule_id", "") for e in errors],
        "waived_rules": [],
    }

    json_path = reports_dir / "hb_plan_result.json"
    json_path.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    _write_markdown_report(reports_dir / "hb_plan_result.md", summary)


def write_verify_reports(
    reports_dir: Path,
    status: str,
    errors: list,
    results: list,
) -> None:
    """Escreve _reports/hb_verify_result.json e _reports/hb_verify_result.md."""
    reports_dir.mkdir(parents=True, exist_ok=True)

    summary = {
        "status": status,
        "module_id": "ATHLETES",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "errors": errors,
        "results": results,
    }

    json_path = reports_dir / "hb_verify_result.json"
    json_path.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    _write_markdown_report(reports_dir / "hb_verify_result.md", summary)


def _write_markdown_report(path: Path, summary: dict) -> None:
    status = summary.get("status", "UNKNOWN")
    icon = "✅" if status == "PASS" else "❌"
    lines = [
        f"# HB Plan/Verify Report — {status} {icon}",
        f"",
        f"**Módulo:** {summary.get('module_id', '?')}",
        f"**Gerado em:** {summary.get('generated_at', '?')}",
        f"",
    ]

    errors = summary.get("errors", [])
    if errors:
        lines.append("## Erros")
        for err in errors:
            reason = err.get("reason", err.get("message", str(err)))
            rule_id = err.get("rule_id", "")
            prefix = f"**{rule_id}**: " if rule_id else ""
            lines.append(f"- {prefix}{reason}")
        lines.append("")

    warnings = summary.get("warnings", [])
    if warnings:
        lines.append("## Avisos")
        for w in warnings:
            reason = w.get("reason", str(w))
            lines.append(f"- {reason}")
        lines.append("")

    results = summary.get("results", [])
    pass_results = [r for r in results if isinstance(r, dict) and r.get("status") == "PASS"]
    if pass_results:
        lines.append("## Regras que passaram")
        for r in pass_results:
            lines.append(f"- {r.get('rule_id', r.get('checker_id', '?'))}")
        lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")
