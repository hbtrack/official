import argparse
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

DET_RE = re.compile(r"Detected (.+)$")
WARN_RE = re.compile(r"SAWarning: (.+)$")

# Remover cores ANSI e ler com heurística de encoding (BOM / UTF-16LE fallback)
ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")

def read_log_lines(path: Path) -> List[str]:
    raw = path.read_bytes()

    if raw.startswith(b"\xff\xfe") or raw.startswith(b"\xfe\xff"):
        s = raw.decode("utf-16", errors="replace")
    elif raw.startswith(b"\xef\xbb\xbf"):
        s = raw.decode("utf-8-sig", errors="replace")
    else:
        # heurística: muitos NULs no início => UTF-16LE
        if raw[:200].count(b"\x00") > 20:
            s = raw.decode("utf-16le", errors="replace")
        else:
            s = raw.decode("utf-8", errors="replace")

    # remove ANSI colors, se existirem
    s = ANSI_RE.sub("", s)
    return s.splitlines()

def extract_table_col(msg: str) -> Dict[str, Optional[str]]:
    """
    Heurísticas:
      - 'table.column' aparece em: "column comment 'table.column'"
      - "on table X" aparece em várias mensagens
      - "on 'table.col'" em type change
    """
    table = None
    col = None

    m = re.search(r"on table ([a-zA-Z0-9_\.]+)", msg)
    if m:
        table = m.group(1).strip("'\"")

    m = re.search(r"'([a-zA-Z0-9_]+)\.([a-zA-Z0-9_]+)'", msg)
    if m:
        table = m.group(1)
        col = m.group(2)

    m = re.search(r"column comment '([a-zA-Z0-9_]+)\.([a-zA-Z0-9_]+)'", msg)
    if m:
        table = m.group(1)
        col = m.group(2)

    m = re.search(r"added column '([a-zA-Z0-9_]+)\.([a-zA-Z0-9_]+)'", msg)
    if m:
        table = m.group(1)
        col = m.group(2)

    m = re.search(r"removed column '([a-zA-Z0-9_]+)\.([a-zA-Z0-9_]+)'", msg)
    if m:
        table = m.group(1)
        col = m.group(2)

    return {"table": table, "column": col}

def classify(msg: str) -> str:
    s = msg.lower()

    # comments
    if "comment" in s:
        return "comment"

    # indexes
    if " index " in s or s.startswith("added index") or s.startswith("removed index"):
        return "index"

    # constraints
    if "foreign key" in s:
        return "constraint_fk"
    if "unique constraint" in s:
        return "constraint_unique"
    if "primary key" in s:
        return "constraint_pk"

    # table/column changes
    if s.startswith("added table") or s.startswith("removed table"):
        return "table"
    if "added column" in s or "removed column" in s:
        return "column"

    # type/default/nullability
    if "type change" in s:
        return "type"
    if "null on column" in s or "not null on column" in s:
        return "nullability"
    if "server default" in s:
        return "default"

    # sequences (normalmente ruído)
    if "detected sequence" in s:
        return "sequence"

    return "other"

def is_structural(category: str) -> bool:
    return category in {
        "table", "column", "type", "nullability",
        "constraint_fk", "constraint_unique", "constraint_pk",
        "default",
        # index pode ser estrutural dependendo do seu contrato; aqui deixo como não-estrutural por padrão
    }

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--log", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    log_path = Path(args.log)
    text = read_log_lines(log_path)

    warnings: List[Dict[str, str]] = []
    items: List[Dict[str, Any]] = []

    for line in text:
        w = WARN_RE.search(line)
        if w:
            warnings.append({"category": "sa_warning", "message": w.group(1).strip()})

        m = DET_RE.search(line)
        if not m:
            continue

        msg = m.group(1).strip()

        # Alembic informational noise: sequence ownership -> assume SERIAL (not a parity diff)
        low = msg.lower()
        if "sequence" in low and "assuming serial" in low and "omitting" in low:
            warnings.append({"category": "alembic_info", "message": msg})
            continue

        category = classify(msg)
        tc = extract_table_col(msg)

        items.append({
            "category": category,
            "structural": is_structural(category),
            "message": msg,
            **tc,
        })

    structural = [x for x in items if x["structural"]]
    non_structural = [x for x in items if not x["structural"]]

    report = {
        "summary": {
            "total": len(items),
            "structural_count": len(structural),
            "non_structural_count": len(non_structural),
            "by_category": {c: sum(1 for x in items if x["category"] == c) for c in sorted({x["category"] for x in items})},
            "warnings_count": len(warnings),
        },
        "warnings": warnings,
        "items": items,
    }

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

if __name__ == "__main__":
    main()
