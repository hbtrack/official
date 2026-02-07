"""
Generate docs/_generated/training_invariants_status.md from INVARIANTS_TRAINING.md.

Usage:
    python docs/scripts/generate_training_invariants_status.py
"""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path


def _clean_bullet(line: str) -> str:
    line = line.strip()
    if line.startswith(("* ", "- ")):
        return line[2:].strip()
    if line.startswith("*"):
        return line.lstrip("*").strip()
    return line


def _is_field_line(line: str) -> bool:
    return bool(re.match(r"^\*+\s*\*\*[^*]+\*\*:", line.strip()))


def _section_status(section: str | None) -> str | None:
    if not section:
        return None
    name = section.lower()
    if "confirmad" in name:
        return "CONFIRMADA"
    if "pretendid" in name:
        return "PRETENDIDA"
    if "backlog" in name:
        return "BACKLOG"
    if "inativ" in name:
        return "INATIVA"
    return None


def main() -> int:
    repo_root = Path(__file__).resolve().parents[2]
    source_path = repo_root / "docs" / "02-modulos" / "training" / "INVARIANTS_TRAINING.md"
    output_path = repo_root / "docs" / "_generated" / "training_invariants_status.md"

    if not source_path.exists():
        print(f"ERROR: source not found: {source_path}")
        return 1

    lines = source_path.read_text(encoding="utf-8").splitlines()

    items: list[dict] = []
    current: dict | None = None
    section: str | None = None
    collecting: str | None = None

    for raw_line in lines:
        line = raw_line.rstrip()

        if line.startswith("## "):
            section = line[3:].strip()
            collecting = None
            continue

        if line.startswith("### "):
            if current:
                items.append(current)
            header = line[4:].strip()
            match = re.match(r"^(?P<id>INV-[A-Z0-9-]+)\s+—\s+(?P<title>.+)$", header)
            if not match:
                current = None
                continue
            current = {
                "id": match.group("id"),
                "title": match.group("title"),
                "section": section,
                "status": None,
                "status_type": None,
                "legacy_id": None,
                "evidence": [],
                "tests": [],
            }
            collecting = None
            continue

        if not current:
            continue

        if collecting and (line.startswith("### ") or line.startswith("## ")):
            collecting = None

        if collecting and _is_field_line(line):
            collecting = None

        if line.startswith("* **Status**:"):
            value = line.split(":", 1)[1].strip()
            status_match = re.match(r"([A-ZÇÃÕ]+)(?:\s*\((\w)\))?", value)
            if status_match:
                current["status"] = status_match.group(1)
                if status_match.group(2):
                    current["status_type"] = status_match.group(2)
            else:
                current["status"] = value
            continue

        if line.startswith("* Legacy ID:"):
            value = line.split(":", 1)[1].strip()
            if value:
                current["legacy_id"] = value
            continue

        if line.startswith("* **Evidência**:"):
            value = line.split(":", 1)[1].strip()
            if value:
                current["evidence"].append(value)
                collecting = None
            else:
                collecting = "evidence"
            continue

        if line.startswith("* **Teste**:"):
            value = line.split(":", 1)[1].strip()
            if value:
                current["tests"].append(value)
                collecting = None
            else:
                collecting = "tests"
            continue

        if collecting == "evidence":
            if line.strip() == "":
                # Allow blank lines inside evidence blocks
                continue
            if line.strip().startswith(("*", "-")):
                current["evidence"].append(_clean_bullet(line))
            continue

        if collecting == "tests":
            if line.strip() == "":
                # Allow blank lines inside test blocks
                continue
            if line.strip().startswith(("*", "-")):
                current["tests"].append(_clean_bullet(line))
            continue

    if current:
        items.append(current)

    status_defaults = {
        "CONFIRMADA": "A",
        "BACKLOG": "B",
        "PRETENDIDA": "P",
    }

    counts = {
        "CONFIRMADA": 0,
        "PRETENDIDA": 0,
        "BACKLOG": 0,
    }

    ordered_items: list[dict] = []
    inactive_items: list[dict] = []

    for item in items:
        status = item["status"] or _section_status(item["section"])
        item["status_final"] = status
        if status == "INATIVA":
            inactive_items.append(item)
        else:
            ordered_items.append(item)
            if status in counts:
                counts[status] += 1

    output_lines: list[str] = []
    output_lines.append("# Training Invariants Status Report")
    output_lines.append("")
    output_lines.append(
        "AUTO-GENERATED by docs/scripts/generate_training_invariants_status.py. Do not edit by hand."
    )
    output_lines.append("")
    output_lines.append(f"Gerado: {date.today().isoformat()}")
    output_lines.append("")
    output_lines.append("Totais:")
    output_lines.append(f"- CONFIRMADAS: {counts['CONFIRMADA']}")
    output_lines.append(f"- PRETENDIDAS: {counts['PRETENDIDA']}")
    output_lines.append(f"- BACKLOG: {counts['BACKLOG']}")
    output_lines.append("")
    output_lines.append("Lista por ID:")

    for item in ordered_items:
        status = item["status_final"] or "DESCONHECIDO"
        status_type = item["status_type"] or status_defaults.get(status, "?")
        legacy = item.get("legacy_id") or "—"
        evidence = "; ".join([e for e in item["evidence"] if e]) or "sem evidencia registrada"
        tests = "; ".join([t for t in item["tests"] if t]) or "nao verificado nesta execucao"
        output_lines.append(
            f"- [{item['id']}] — {status} — {status_type} — Legacy ID: {legacy} — {evidence} — Teste: {tests}"
        )

    output_lines.append("")
    output_lines.append("Inativas (fora do total):")
    if inactive_items:
        for item in inactive_items:
            legacy = item.get("legacy_id") or "—"
            evidence = "; ".join([e for e in item["evidence"] if e]) or "sem evidencia registrada"
            output_lines.append(f"- {item['id']} — INATIVA — Legacy ID: {legacy} — evidencia: {evidence}")
    else:
        output_lines.append("- (nenhuma)")

    output_path.write_text("\n".join(output_lines) + "\n", encoding="utf-8")
    print(f"[OK] training_invariants_status.md written to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
