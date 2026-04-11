#!/usr/bin/env python3
"""
gen_from_exit_codes_registry.py

Purpose: Generate exit_codes.md + troubleshooting-map.json FROM the YAML registry (SSOT)
Classification: generate/docs
Side Effects: FS_READ, FS_WRITE
Exit Codes:
  0 - Success (files generated / no drift)
  2 - Drift detected (--check mode)
  3 - Error (file not found, parse error)

Usage:
  python scripts/generate/docs/gen_from_exit_codes_registry.py [--check] [--dry-run] [--verbose]

Input (SSOT):
  - docs/_ai/_specs/exit_codes_registry.yaml

Output (derived):
  - docs/references/exit_codes.md
  - docs/_ai/_maps/troubleshooting-map.json
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

try:
    import yaml
except ImportError:
    print("[ERROR] PyYAML not installed. Run: pip install pyyaml", file=sys.stderr)
    sys.exit(3)


REPO_ROOT = Path(__file__).resolve().parents[3]

YAML_SOURCE = REPO_ROOT / "docs" / "_ai" / "_specs" / "exit_codes_registry.yaml"
MD_OUTPUT = REPO_ROOT / "docs" / "references" / "exit_codes.md"
JSON_OUTPUT = REPO_ROOT / "docs" / "_ai" / "_maps" / "troubleshooting-map.json"


def log(msg: str, verbose: bool) -> None:
    if verbose:
        print(f"[DEBUG] {msg}", file=sys.stderr)


def load_registry(path: Path) -> Dict[str, Any]:
    """Load and validate the exit codes registry YAML."""
    if not path.exists():
        print(f"[ERROR] SSOT not found: {path}", file=sys.stderr)
        sys.exit(3)
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not data or "exit_codes" not in data:
        print(f"[ERROR] Invalid registry: missing 'exit_codes' key", file=sys.stderr)
        sys.exit(3)
    return data


# ─────────────────────────────────────────────────────────────────────────────
# MD GENERATOR
# ─────────────────────────────────────────────────────────────────────────────

def render_md(data: Dict[str, Any]) -> str:
    """Render exit_codes.md from registry data."""
    lines = [
        "# Exit Codes Reference - HB Track",
        "",
        "> **Gerado automaticamente** a partir de `docs/_ai/_specs/exit_codes_registry.yaml`.",
        f"> Última geração: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        "> **NÃO EDITAR MANUALMENTE** — edite o YAML SSOT e regenere.",
        "",
        "Guia de referência para os códigos de saída dos scripts de validação do HB Track.",
        "",
        "---",
        "",
    ]

    exit_codes = data.get("exit_codes", {})
    for code in sorted(exit_codes.keys(), key=lambda x: int(x)):
        entry = exit_codes[code]
        title = entry.get("title", "Unknown")
        description = entry.get("description", "").strip()
        severity = entry.get("severity", "")
        normative = entry.get("normative", "")
        emitters = entry.get("emitters", [])
        causes = entry.get("causes", [])
        symptoms = entry.get("symptoms", [])
        troubleshooting = entry.get("troubleshooting", [])

        lines.append(f"## Exit Code {code}: {title}")
        lines.append("")

        if description:
            lines.append(f"**Significado:** {description}")
            lines.append("")

        if severity:
            lines.append(f"**Severidade:** `{severity}`")
            lines.append("")

        if normative:
            lines.append(f"**Regra normativa (BCP 14):** {normative}")
            lines.append("")

        if emitters:
            lines.append("**Scripts que retornam este código:**")
            for e in emitters:
                path = e.get("path", "")
                context = e.get("context", "")
                lines.append(f"- `{path}` — {context}")
            lines.append("")

        if causes:
            lines.append("**Causas comuns:**")
            for c in causes:
                lines.append(f"- {c}")
            lines.append("")

        if symptoms:
            lines.append("**Sintomas:**")
            for s in symptoms:
                lines.append(f"- {s}")
            lines.append("")

        if troubleshooting:
            lines.append("**Resolução:**")
            for step in troubleshooting:
                s = step.get("step", "")
                cmd = step.get("command", "")
                lines.append(f"1. {s}")
                if cmd:
                    lines.append(f"   ```powershell")
                    lines.append(f"   {cmd}")
                    lines.append(f"   ```")
            lines.append("")

        lines.append("---")
        lines.append("")

    # Special codes
    special = data.get("special_codes", {})
    if special:
        lines.append("## Códigos Especiais (Windows)")
        lines.append("")
        for code, entry in special.items():
            title = entry.get("title", "")
            desc = entry.get("description", "").strip()
            lines.append(f"### Exit Code {code}: {title}")
            lines.append("")
            if desc:
                lines.append(f"**Significado:** {desc}")
                lines.append("")
            causes_s = entry.get("causes", [])
            if causes_s:
                for c in causes_s:
                    lines.append(f"- {c}")
                lines.append("")
        lines.append("---")
        lines.append("")

    lines.append(f"**Gerado por:** `scripts/generate/docs/gen_from_exit_codes_registry.py`")
    lines.append(f"**SSOT:** `docs/_ai/_specs/exit_codes_registry.yaml`")
    lines.append("")

    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# JSON GENERATOR
# ─────────────────────────────────────────────────────────────────────────────

def render_json(data: Dict[str, Any]) -> dict:
    """Render troubleshooting-map.json from registry data."""
    result = {
        "version": "3.0",
        "source": "Generated from docs/_ai/_specs/exit_codes_registry.yaml",
        "last_sync": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "exit_codes": {},
    }

    exit_codes = data.get("exit_codes", {})
    for code in sorted(exit_codes.keys(), key=lambda x: int(x)):
        entry = exit_codes[code]
        result["exit_codes"][code] = {
            "title": entry.get("title", ""),
            "description": entry.get("description", "").strip(),
            "severity": entry.get("severity", ""),
            "symptoms": entry.get("symptoms", []),
            "causes": entry.get("causes", []),
            "scripts": [
                f"`{e['path']}` — {e.get('context', '')}"
                for e in entry.get("emitters", [])
            ],
            "troubleshooting": [
                {"step": s.get("step", ""), "command": s.get("command", "")}
                for s in entry.get("troubleshooting", [])
            ],
        }

    return result


# ─────────────────────────────────────────────────────────────────────────────
# DRIFT CHECK
# ─────────────────────────────────────────────────────────────────────────────

def check_drift(md_content: str, json_data: dict, verbose: bool) -> bool:
    """Return True if generated content differs from existing files."""
    drift = False

    if MD_OUTPUT.exists():
        current_md = MD_OUTPUT.read_text(encoding="utf-8")
        # Compare ignoring generation timestamp line
        current_lines = [
            l for l in current_md.splitlines()
            if not l.startswith("> Última geração:")
        ]
        new_lines = [
            l for l in md_content.splitlines()
            if not l.startswith("> Última geração:")
        ]
        if current_lines != new_lines:
            drift = True
            log("MD drift detected", verbose)
    else:
        drift = True
        log("MD file does not exist", verbose)

    if JSON_OUTPUT.exists():
        current_json = json.loads(JSON_OUTPUT.read_text(encoding="utf-8"))
        # Compare ignoring last_sync date
        current_json.pop("last_sync", None)
        json_cmp = dict(json_data)
        json_cmp.pop("last_sync", None)
        if current_json != json_cmp:
            drift = True
            log("JSON drift detected", verbose)
    else:
        drift = True
        log("JSON file does not exist", verbose)

    return drift


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate exit_codes.md + troubleshooting-map.json from YAML registry"
    )
    parser.add_argument("--check", action="store_true",
                        help="Validate only, exit 2 if drift detected")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would change without writing files")
    parser.add_argument("--verbose", action="store_true",
                        help="Print detailed debug info")
    args = parser.parse_args()

    print(f"📖 Loading SSOT: {YAML_SOURCE.relative_to(REPO_ROOT)}")
    data = load_registry(YAML_SOURCE)
    log(f"Loaded {len(data.get('exit_codes', {}))} exit codes", args.verbose)

    print("📝 Rendering exit_codes.md...")
    md_content = render_md(data)

    print("📝 Rendering troubleshooting-map.json...")
    json_data = render_json(data)

    if args.check:
        has_drift = check_drift(md_content, json_data, args.verbose)
        if has_drift:
            print("⚠️  Drift detected! Derived files need regeneration.")
            print(f"   Fix: python {Path(__file__).relative_to(REPO_ROOT)}")
            return 2
        print("✅ No drift. Derived files are in sync with YAML SSOT.")
        return 0

    if args.dry_run:
        print(f"\n[DRY-RUN] Would write: {MD_OUTPUT.relative_to(REPO_ROOT)}")
        print(f"[DRY-RUN] Would write: {JSON_OUTPUT.relative_to(REPO_ROOT)}")
        print(f"\n--- MD preview (first 30 lines) ---")
        for line in md_content.splitlines()[:30]:
            print(line)
        return 0

    # Write files
    MD_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    MD_OUTPUT.write_text(md_content, encoding="utf-8")
    print(f"✅ Generated: {MD_OUTPUT.relative_to(REPO_ROOT)}")

    JSON_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(JSON_OUTPUT, "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)
    print(f"✅ Generated: {JSON_OUTPUT.relative_to(REPO_ROOT)}")

    print(f"\n✅ Done! {len(data['exit_codes'])} exit codes rendered.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(3)
