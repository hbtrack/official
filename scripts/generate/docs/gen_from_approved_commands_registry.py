#!/usr/bin/env python3
"""
gen_from_approved_commands_registry.py

Purpose: Generate 08_APPROVED_COMMANDS.md FROM the YAML registry (SSOT)
Classification: generate/docs
Side Effects: FS_READ, FS_WRITE
Exit Codes:
  0 - Success (file generated / no drift)
  2 - Drift detected (--check mode)
  3 - Error (file not found, parse error)

Usage:
  python scripts/generate/docs/gen_from_approved_commands_registry.py [--check] [--dry-run] [--verbose]

Input (SSOT):
  - docs/_ai/_specs/approved_commands_registry.yaml

Output (derived):
  - docs/_canon/08_APPROVED_COMMANDS.md
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

try:
    import yaml
except ImportError:
    print("[ERROR] PyYAML not installed. Run: pip install pyyaml", file=sys.stderr)
    sys.exit(3)


REPO_ROOT = Path(__file__).resolve().parents[3]

YAML_SOURCE = REPO_ROOT / "docs" / "_ai" / "_specs" / "approved_commands_registry.yaml"
MD_OUTPUT = REPO_ROOT / "docs" / "_canon" / "08_APPROVED_COMMANDS.md"


def log(msg: str, verbose: bool) -> None:
    if verbose:
        print(f"[DEBUG] {msg}", file=sys.stderr)


def load_registry(path: Path) -> Dict[str, Any]:
    """Load and validate the approved commands registry YAML."""
    if not path.exists():
        print(f"[ERROR] SSOT not found: {path}", file=sys.stderr)
        sys.exit(3)
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not data or "categories" not in data:
        print(f"[ERROR] Invalid registry: missing 'categories' key", file=sys.stderr)
        sys.exit(3)
    return data


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

RISK_EMOJI = {
    "green": "🟢",
    "yellow": "🟡",
    "red": "🔴",
    "critical": "⛔",
}

APPROVAL_LABEL = {
    "automatic": "Automática",
    "required": "Obrigatória",
    "gated": "Gated (via validação)",
}


def _risk(level: str) -> str:
    return f"{RISK_EMOJI.get(level, '⚪')} {level}"


def _exit_codes_str(codes: List[int]) -> str:
    return ", ".join(str(c) for c in codes)


# ─────────────────────────────────────────────────────────────────────────────
# MD RENDERER
# ─────────────────────────────────────────────────────────────────────────────

def render_md(data: Dict[str, Any]) -> str:
    """Render 08_APPROVED_COMMANDS.md from registry data."""
    lines: List[str] = []
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    # ── Header ──────────────────────────────────────────────────────────
    lines.extend([
        "# Approved Commands — Whitelist Canônica para AI Agents (HB Track)",
        "",
        "| Propriedade | Valor |",
        "|---|---|",
        "| ID | CANON-APPROVED-COMMANDS-008 |",
        "| Status | CANÔNICO |",
        f"| Última geração | {ts} |",
        "| Porta de entrada | docs/_INDEX.yaml |",
        "| SSOT | `docs/_ai/_specs/approved_commands_registry.yaml` |",
        "| Depende de | docs/_canon/05_MODELS_PIPELINE.md, docs/references/exit_codes.md |",
        "| Objetivo | Whitelist autoritativa de comandos seguros para AI agents |",
        "",
        "> **Gerado automaticamente** a partir do YAML SSOT.",
        "> **NÃO EDITAR MANUALMENTE** — edite o YAML e regenere.",
        "",
        "---",
        "",
    ])

    # ── Global Rules ────────────────────────────────────────────────────
    global_rules = data.get("global_rules", {})
    if global_rules:
        lines.append("## Convenções e Regras Globais")
        lines.append("")
        for key, rule in global_rules.items():
            rule_id = rule.get("id", "")
            normative = rule.get("normative", "").strip()
            lines.append(f"### {rule_id}: {key.replace('_', ' ').title()}")
            lines.append("")
            lines.append(f"{normative}")
            lines.append("")
        lines.append("---")
        lines.append("")

    # ── CWD Definitions ────────────────────────────────────────────────
    cwd_defs = data.get("cwd_definitions", {})
    if cwd_defs:
        lines.append("## CWD Definitions")
        lines.append("")
        lines.append("| Alias | Path | Validação |")
        lines.append("|-------|------|-----------|")
        for alias, info in cwd_defs.items():
            path = info.get("path", "")
            validation = info.get("validation", "")
            lines.append(f"| `{alias}` | `{path}` | `{validation}` |")
        lines.append("")
        lines.append("---")
        lines.append("")

    # ── Index Tables ────────────────────────────────────────────────────
    categories = data.get("categories", {})
    lines.append("## Índice de Comandos Aprovados")
    lines.append("")

    # Summary index table
    lines.append("| ID | Comando | Categoria | Aprovação | Exit Codes |")
    lines.append("|-----|---------|-----------|-----------|------------|")
    for _cat_key, cat in categories.items():
        if not isinstance(cat, dict):
            continue
        for cmd in cat.get("commands", []):
            cid = cmd.get("id", "")
            name = cmd.get("name", "")
            cat_label = cat.get("label", "")
            approval = cmd.get("approval", cat.get("approval", ""))
            ecs = _exit_codes_str(cmd.get("exit_codes", []))
            dep = " *(deprecated)*" if cmd.get("deprecated") else ""
            lines.append(f"| {cid} | `{name}`{dep} | {cat_label} | {approval} | {ecs} |")
    lines.append("")
    lines.append("---")
    lines.append("")

    # ── Category Sections ───────────────────────────────────────────────
    cat_num = 0
    for _cat_key, cat in categories.items():
        if not isinstance(cat, dict):
            continue
        cat_num += 1
        cat_id = cat.get("id", f"CAT-{cat_num}")
        cat_label = cat.get("label", _cat_key)
        cat_approval = cat.get("approval", "")
        cat_risk = cat.get("risk_level", "")
        cat_desc = cat.get("description", "")

        lines.append(f"## Categoria {cat_num}: {cat_label}")
        lines.append("")
        if cat_desc:
            lines.append(f"{cat_desc}")
            lines.append("")
        lines.append(f"**Aprovação padrão:** {APPROVAL_LABEL.get(cat_approval, cat_approval)} | "
                      f"**Risco:** {_risk(cat_risk)}")
        lines.append("")

        for cmd in cat.get("commands", []):
            _render_command(lines, cmd, cat)

        lines.append("---")
        lines.append("")

    # ── Blacklist ───────────────────────────────────────────────────────
    blacklist = data.get("blacklist", [])
    if blacklist:
        lines.append("## Comandos Proibidos (Blacklist)")
        lines.append("")
        for bl in blacklist:
            bl_id = bl.get("id", "")
            bl_label = bl.get("label", "")
            normative = bl.get("normative", "").strip()
            examples = bl.get("examples", [])
            lines.append(f"### {bl_id}: {bl_label}")
            lines.append("")
            lines.append(f"{normative}")
            lines.append("")
            if examples:
                lines.append("**Exemplos proibidos:**")
                for ex in examples:
                    lines.append(f"- `{ex}`")
                lines.append("")
        lines.append("---")
        lines.append("")

    # ── Protected Files ─────────────────────────────────────────────────
    protected = data.get("protected_files", [])
    if protected:
        lines.append("## Arquivos Protegidos (Guard)")
        lines.append("")
        for pf in protected:
            pf_id = pf.get("id", "")
            pf_label = pf.get("label", "")
            normative = pf.get("normative", "").strip()
            paths = pf.get("paths", [])
            lines.append(f"### {pf_id}: {pf_label}")
            lines.append("")
            lines.append(f"{normative}")
            lines.append("")
            if paths:
                for p in paths:
                    lines.append(f"- `{p}`")
                lines.append("")
        lines.append("---")
        lines.append("")

    # ── Approval Protocol ───────────────────────────────────────────────
    protocol = data.get("approval_protocol", {})
    if protocol:
        lines.append("## Protocolo de Aprovação Condicional")
        lines.append("")
        desc = protocol.get("description", "").strip()
        if desc:
            lines.append(desc)
            lines.append("")
        options = protocol.get("options", {})
        if options:
            lines.append("| Opção | Ação |")
            lines.append("|-------|------|")
            for opt_key, opt_desc in options.items():
                lines.append(f"| `{opt_key}` | {opt_desc} |")
            lines.append("")
        lines.append("---")
        lines.append("")

    # ── Workflows ───────────────────────────────────────────────────────
    workflows = data.get("workflows", [])
    if workflows:
        lines.append("## Workflows de Referência")
        lines.append("")
        for wf in workflows:
            wf_id = wf.get("id", "")
            wf_name = wf.get("name", "")
            steps = wf.get("steps", [])
            lines.append(f"### {wf_id}: {wf_name}")
            lines.append("")
            for i, step in enumerate(steps, 1):
                lines.append(f"{i}. `{step}`")
            lines.append("")
        lines.append("---")
        lines.append("")

    # ── Footer ──────────────────────────────────────────────────────────
    lines.extend([
        f"**Gerado por:** `scripts/generate/docs/gen_from_approved_commands_registry.py`",
        f"**SSOT:** `docs/_ai/_specs/approved_commands_registry.yaml`",
        "",
    ])

    return "\n".join(lines)


def _render_command(lines: List[str], cmd: Dict[str, Any], cat: Dict[str, Any]) -> None:
    """Render a single command entry."""
    cid = cmd.get("id", "")
    name = cmd.get("name", "")
    syntax = cmd.get("syntax", "")
    desc = cmd.get("description", "")
    params = cmd.get("parameters", [])
    ecs = cmd.get("exit_codes", [])
    ec_map = cmd.get("exit_code_map", {})
    cwd = cmd.get("cwd", "")
    approval = cmd.get("approval", cat.get("approval", ""))
    risk = cmd.get("risk_level", cat.get("risk_level", ""))
    time_est = cmd.get("time_estimate", "")
    normative = cmd.get("normative", "").strip()
    deprecated = cmd.get("deprecated", False)
    deprecated_reason = cmd.get("deprecated_reason", "")
    script_path = cmd.get("script_path", "")
    artifacts = cmd.get("artifacts_generated", [])

    dep_badge = " *(DEPRECATED)*" if deprecated else ""
    lines.append(f"### {cid}: {name}{dep_badge}")
    lines.append("")

    if deprecated and deprecated_reason:
        lines.append(f"> ⚠️ **DEPRECATED:** {deprecated_reason}")
        lines.append("")

    if desc:
        lines.append(f"**Objetivo:** {desc}")
        lines.append("")

    if script_path:
        lines.append(f"**Script:** `{script_path}`")
        lines.append("")

    if syntax:
        lines.append("**Sintaxe:**")
        lines.append("```powershell")
        lines.append(syntax)
        lines.append("```")
        lines.append("")

    if params:
        lines.append("**Parâmetros:**")
        lines.append("")
        lines.append("| Parâmetro | Obrigatório | Descrição |")
        lines.append("|-----------|-------------|-----------|")
        for p in params:
            pname = p.get("name", "")
            preq = "✅" if p.get("required") else "—"
            pdesc = p.get("description", "")
            pdep = " *(deprecated)*" if p.get("deprecated") else ""
            pdang = " ⚠️" if p.get("dangerous") else ""
            lines.append(f"| `{pname}` | {preq} | {pdesc}{pdep}{pdang} |")
        lines.append("")

    if ecs:
        lines.append("**Exit Codes:**")
        for ec in ecs:
            meaning = ec_map.get(str(ec), "")
            suffix = f" — {meaning}" if meaning else ""
            lines.append(f"- `{ec}`{suffix}")
        lines.append("")

    meta_parts = []
    if cwd:
        meta_parts.append(f"**CWD:** `{cwd}`")
    if approval:
        meta_parts.append(f"**Aprovação:** {APPROVAL_LABEL.get(approval, approval)}")
    if risk:
        meta_parts.append(f"**Risco:** {_risk(risk)}")
    if time_est:
        meta_parts.append(f"**Tempo:** {time_est}")
    if meta_parts:
        lines.append(" | ".join(meta_parts))
        lines.append("")

    if normative:
        lines.append(f"**Regra normativa:** {normative}")
        lines.append("")

    if artifacts:
        lines.append("**Artefatos gerados:**")
        for a in artifacts:
            lines.append(f"- `{a}`")
        lines.append("")

    lines.append("")


# ─────────────────────────────────────────────────────────────────────────────
# DRIFT CHECK
# ─────────────────────────────────────────────────────────────────────────────

def check_drift(md_content: str, verbose: bool) -> bool:
    """Return True if generated content differs from existing file."""
    if not MD_OUTPUT.exists():
        log("MD file does not exist", verbose)
        return True

    current_md = MD_OUTPUT.read_text(encoding="utf-8")
    # Compare ignoring generation timestamp line
    current_lines = [
        l for l in current_md.splitlines()
        if not l.startswith("| Última geração") and not l.startswith("> Última geração")
    ]
    new_lines = [
        l for l in md_content.splitlines()
        if not l.startswith("| Última geração") and not l.startswith("> Última geração")
    ]
    if current_lines != new_lines:
        log("MD drift detected", verbose)
        return True
    return False


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate 08_APPROVED_COMMANDS.md from YAML registry"
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
    cat_count = len([c for c in data.get("categories", {}).values() if isinstance(c, dict)])
    cmd_count = sum(
        len(c.get("commands", []))
        for c in data.get("categories", {}).values()
        if isinstance(c, dict)
    )
    log(f"Loaded {cat_count} categories, {cmd_count} commands", args.verbose)

    print("📝 Rendering 08_APPROVED_COMMANDS.md...")
    md_content = render_md(data)

    if args.check:
        has_drift = check_drift(md_content, args.verbose)
        if has_drift:
            print("⚠️  Drift detected! 08_APPROVED_COMMANDS.md needs regeneration.")
            print(f"   Fix: python {Path(__file__).relative_to(REPO_ROOT)}")
            return 2
        print("✅ No drift. MD is in sync with YAML SSOT.")
        return 0

    if args.dry_run:
        print(f"\n[DRY-RUN] Would write: {MD_OUTPUT.relative_to(REPO_ROOT)}")
        print(f"\n--- MD preview (first 40 lines) ---")
        for line in md_content.splitlines()[:40]:
            print(line)
        return 0

    # Write file
    MD_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    MD_OUTPUT.write_text(md_content, encoding="utf-8")
    print(f"✅ Generated: {MD_OUTPUT.relative_to(REPO_ROOT)}")
    print(f"   {cat_count} categories, {cmd_count} commands rendered.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(3)
