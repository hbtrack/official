from __future__ import annotations

import argparse
import ast
import re
from pathlib import Path
from typing import Set


RE_CREATE_TABLE = re.compile(r"^CREATE TABLE public\.([a-zA-Z0-9_]+)\s*\(", re.MULTILINE)
RE_TABLENAME = re.compile(r"__tablename__\s*=\s*['\"]([^'\"]+)['\"]")
DEFAULT_ENV_FILE = Path("db") / "alembic" / "env.py"


def parse_schema_tables(schema_sql: Path) -> Set[str]:
    txt = schema_sql.read_text(encoding="utf-8", errors="replace")
    return set(RE_CREATE_TABLE.findall(txt))


def parse_model_tablenames(models_dir: Path) -> Set[str]:
    names: Set[str] = set()
    for p in models_dir.glob("*.py"):
        if p.name in {"__init__.py", "base.py"}:
            continue
        txt = p.read_text(encoding="utf-8", errors="replace")
        for m in RE_TABLENAME.finditer(txt):
            names.add(m.group(1))
    return names


def _load_skip_stub_only_tables(env_file: Path) -> Set[str]:
    """
    Extrai SKIP_STUB_ONLY_TABLES de db/alembic/env.py sem importar o módulo
    (evita efeitos colaterais do env do Alembic).
    """
    try:
        text = env_file.read_text(encoding="utf-8")
    except Exception:
        return set()

    # 1) Tenta AST literal_eval
    try:
        tree = ast.parse(text)
        for node in tree.body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "SKIP_STUB_ONLY_TABLES":
                        val = ast.literal_eval(node.value)
                        if isinstance(val, (set, list, tuple)):
                            return {str(x) for x in val}
                        # fallback conservador
                        return set()
    except Exception:
        pass

    return set()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--schema", default="docs/_generated/schema.sql")
    parser.add_argument("--models-dir", default="app/models")
    parser.add_argument(
        "--env-file",
        default=str(DEFAULT_ENV_FILE),
        help="Path do db/alembic/env.py para extrair SKIP_STUB_ONLY_TABLES (default: db/alembic/env.py)",
    )
    parser.add_argument("--exclude", default="")  # CSV de tabelas a ignorar
    parser.add_argument(
        "--include-stub-only",
        action="store_true",
        help="Se setado, NÃO ignora SKIP_STUB_ONLY_TABLES (mostra o missing bruto).",
    )
    parser.add_argument(
        "--include-alembic-version",
        action="store_true",
        help="Se setado, NÃO ignora alembic_version.",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Imprime detalhes do filtro aplicado (stubs ignorados etc.).",
    )
    args = parser.parse_args()

    schema = Path(args.schema)
    models_dir = Path(args.models_dir)
    env_file = Path(args.env_file)

    external_exclude = {x.strip() for x in args.exclude.split(",") if x.strip()}

    db_tables = parse_schema_tables(schema) - external_exclude
    orm_tables = parse_model_tablenames(models_dir)

    missing_tables = db_tables - orm_tables
    raw_missing = sorted(set(missing_tables))  # preserve determinism

    ignored = set()
    if not args.include_alembic_version:
        ignored.add("alembic_version")

    skip_stubs = _load_skip_stub_only_tables(env_file)
    if not args.include_stub_only:
        ignored |= skip_stubs

    filtered_missing = sorted(set(raw_missing) - ignored)
    suggested = filtered_missing[0] if filtered_missing else None

    if args.debug:
        print(f"env_file={env_file.as_posix()}")
        print(f"raw_missing_count={len(raw_missing)}")
        print(f"ignored_count={len(ignored)}")
        # só mostra o que realmente foi ignorado por estar no raw_missing
        ignored_hit = sorted(set(raw_missing) & ignored)
        print(f"ignored_hit_count={len(ignored_hit)}")
        print(f"ignored_hit={ignored_hit}")
        print(f"skip_stub_only_tables_count={len(skip_stubs)}")

    print(f"missing_count={len(filtered_missing)}")
    print(f"missing_tables={filtered_missing}")
    print(f"suggested_table={suggested}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())