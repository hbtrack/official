#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script: gen_ar_index.py
Regenera o arquivo docs/hbtrack/_INDEX.md a partir das ARs em docs/hbtrack/ars/

Usage:
    python scripts/generate/docs/gen_ar_index.py
"""

import sys
import re
from pathlib import Path
from datetime import date
from typing import List

# Constantes (alinhadas com hb_cli.py)
AR_DIR = "docs/hbtrack/ars"


def get_repo_root() -> Path:
    """Retorna o root do repo (assume que script está em scripts/generate/docs/)."""
    # scripts/generate/docs/gen_ar_index.py -> scripts/generate/docs -> scripts/generate -> scripts -> repo_root
    return Path(__file__).resolve().parent.parent.parent.parent


def rebuild_ar_index(repo_root: Path) -> None:
    """
    Auto-gera docs/hbtrack/_INDEX.md com tabela de todas as ARs.
    (Cópia da função em hb_cli.py)
    """
    ar_dir = repo_root / AR_DIR
    index_path = repo_root / "docs/hbtrack/_INDEX.md"

    # Scanear AR_*.md (excluir _INDEX.md)
    ar_files = [
        f for f in ar_dir.iterdir()
        if re.match(r"AR_[0-9]", f.name) and f.suffix == ".md"
    ]

    # Ordenar por ID numérico
    def ar_sort_key(p: Path) -> int:
        m = re.search(r"AR_([0-9]+)", p.name)
        return int(m.group(1)) if m else 9999

    ar_files.sort(key=ar_sort_key)

    rows: List[str] = []
    for ar_path in ar_files:
        try:
            content = ar_path.read_text(encoding="utf-8")
        except Exception:
            continue

        # Extrair ID
        id_match = re.search(r"AR_([0-9]+(?:\.[0-9]+)?)", ar_path.name)
        ar_id = f"AR_{id_match.group(1)}" if id_match else ar_path.stem

        # Extrair título (linha # AR_NNN — ...)
        title_match = re.match(r"#\s+AR_[^\s—–-]+\s*[—–-]+?\s*(.+)", content)
        title = title_match.group(1).strip() if title_match else "(sem título)"
        if len(title) > 60:
            title = title[:57] + "..."

        # Extrair status (linha **Status**: ...)
        status_match = re.search(r"\*\*Status\*\*:\s*(.+)", content)
        status = status_match.group(1).strip() if status_match else "DESCONHECIDO"

        # Extrair evidence file
        ev_match = re.search(r"## Evidence File \(Contrato\)\n`(.+?)`", content)
        evidence = ev_match.group(1).strip() if ev_match else "—"

        rows.append(f"| {ar_id} | {title} | {status} | {evidence} |")

    today = date.today().isoformat()
    lines = [
        "# Índice de Architectural Records (ARs)",
        "> ⚠️ Auto-gerado por `hb plan`/`hb report`. NÃO editar manualmente.",
        f"> Última atualização: {today}",
        "",
        "| ID | Título | Status | Evidence |",
        "|---|---|---|---|",
    ] + rows + [""]

    index_path.write_text("\n".join(lines), encoding="utf-8")

def main():
    print("🔄 Regenerando docs/hbtrack/_INDEX.md...")
    
    try:
        repo_root = get_repo_root()
        rebuild_ar_index(repo_root)
        print("✅ Índice regenerado com sucesso!")
        print(f"📄 Arquivo: docs/hbtrack/_INDEX.md")
    except Exception as e:
        print(f"❌ Erro ao regenerar índice: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
