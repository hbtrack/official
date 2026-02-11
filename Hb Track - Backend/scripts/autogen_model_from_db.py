from __future__ import annotations

import argparse
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import sqlalchemy as sa
from sqlalchemy import text
from sqlalchemy.engine import make_url


IMPORTS_BLOCK = """# HB-AUTOGEN-IMPORTS:BEGIN
from __future__ import annotations

from datetime import date, datetime
from typing import Optional
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy import ForeignKey, CheckConstraint, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB as PG_JSONB, INET as PG_INET, ENUM as PG_ENUM
# HB-AUTOGEN-IMPORTS:END
""".rstrip() + "\n"


CLASS_BLOCK_BEGIN = "# HB-AUTOGEN:BEGIN"
CLASS_BLOCK_END = "# HB-AUTOGEN:END"

# FKs que devem ser emitidas com use_alter=True para evitar ciclos de ordenação
# no autogenerate/compare do Alembic (não altera DDL final do banco).
FORCE_USE_ALTER_FK_NAMES: set[str] = {
    "fk_teams_season_id",  # quebra ciclo teams <-> seasons no metadata sort
    "fk_seasons_team_id",  # quebra ciclo teams <-> seasons no metadata sort
}

SCHEMA_SQL = Path("docs/_generated/schema.sql")


def _normalize_constraint_name(name: str) -> str:
    return (name or "").strip().strip('"')


def _fk_ondelete_map_from_schema_sql(path: Path) -> Dict[str, Optional[str]]:
    if not path.exists():
        return {}
    text_src = path.read_text(encoding="utf-8", errors="replace")
    pattern = re.compile(
        r"ADD\s+CONSTRAINT\s+(\S+)\s+FOREIGN\s+KEY.*?REFERENCES\s+.*?"
        r"(?:ON\s+DELETE\s+(RESTRICT|CASCADE|SET\s+NULL|SET\s+DEFAULT|NO\s+ACTION))?\s*;",
        re.IGNORECASE | re.DOTALL,
    )
    out: Dict[str, Optional[str]] = {}
    for m in pattern.finditer(text_src):
        name = _normalize_constraint_name(m.group(1))
        action_raw = m.group(2)
        action = re.sub(r"\s+", " ", action_raw.upper()).strip() if action_raw else None
        if name:
            out[name] = action
    return out


def _find_module_docstring_span(src: str) -> Tuple[int, int]:
    # returns (start,end) for module docstring if present, else (0,0)
    m = re.match(r"\s*(\"\"\".*?\"\"\"|'''.*?''')\s*", src, flags=re.DOTALL)
    if not m:
        return (0, 0)
    return (m.start(1), m.end(1))


def _remove_duplicate_imports_outside_autogen(src: str) -> str:
    """Remove import lines outside HB-AUTOGEN-IMPORTS that are already covered by the block.

    Specifically handles:
    - from __future__ import ... (MUST be removed to avoid SyntaxError)
    - from sqlalchemy import/from sqlalchemy.orm/from sqlalchemy.dialects ...
    - from typing import ...
    - from datetime import ...
    - from uuid import ...
    - import sqlalchemy as sa
    - Bare 'from app.models.base import Base' is KEPT (not in autogen imports).
    - Orphan import continuation lines (e.g., "    Boolean," left from incomplete removal)

    Lines inside any HB-AUTOGEN block are never touched.
    """
    if "HB-AUTOGEN-IMPORTS:BEGIN" not in src:
        return src

    # Patterns that are covered by the HB-AUTOGEN-IMPORTS block
    _covered_patterns = [
        re.compile(r'^\s*from\s+__future__\s+import\s+'),
        re.compile(r'^\s*from\s+sqlalchemy\b'),
        re.compile(r'^\s*import\s+sqlalchemy\b'),
        re.compile(r'^\s*from\s+typing\s+import\s+'),
        re.compile(r'^\s*from\s+datetime\s+import\s+'),
        re.compile(r'^\s*from\s+uuid\s+import\s+'),
    ]

    # Known SQLAlchemy symbols that may appear as orphan import continuation lines
    _sqlalchemy_symbols = {
        'Boolean', 'Integer', 'SmallInteger', 'BigInteger', 'Float', 'Numeric', 'Decimal',
        'String', 'Text', 'Unicode', 'UnicodeText', 'LargeBinary', 'PickleType',
        'Date', 'DateTime', 'Time', 'Interval', 'Enum',
        'ForeignKey', 'CheckConstraint', 'UniqueConstraint', 'PrimaryKeyConstraint',
        'Index', 'Column', 'Table', 'MetaData',
        'relationship', 'backref', 'Mapped', 'mapped_column',
        'text', 'func', 'and_', 'or_', 'not_', 'select', 'insert', 'update', 'delete',
        'ARRAY', 'UUID', 'JSONB', 'JSON', 'INET', 'ENUM',
    }

    # Pattern to detect orphan import continuation lines like "    Boolean," or ")"
    _orphan_pattern = re.compile(r'^\s+(\w+)\s*,?\s*$')
    _closing_paren_pattern = re.compile(r'^\s*\)\s*$')

    lines = src.split('\n')
    result = []
    in_autogen = False
    in_class = False
    in_multiline_import = False  # Track multiline imports with (...)
    paren_count = 0

    i = 0
    while i < len(lines):
        line = lines[i]
        
        if 'HB-AUTOGEN-IMPORTS:BEGIN' in line or 'HB-AUTOGEN:BEGIN' in line:
            in_autogen = True
        if 'HB-AUTOGEN-IMPORTS:END' in line or 'HB-AUTOGEN:END' in line:
            result.append(line)
            in_autogen = False
            i += 1
            continue

        # Track if we've entered a class definition (orphans only before classes)
        if re.match(r'^class\s+\w+', line):
            in_class = True

        if in_autogen:
            result.append(line)
            i += 1
            continue

        # If we're inside a multiline import being removed, skip until closed
        if in_multiline_import:
            paren_count += line.count('(') - line.count(')')
            if paren_count <= 0:
                in_multiline_import = False
                paren_count = 0
            i += 1
            continue  # skip this line (part of multiline import)

        # Outside autogen: check if this import is redundant
        is_redundant = any(p.match(line) for p in _covered_patterns)
        if is_redundant:
            # Check if this is a multiline import (opens parenthesis)
            if '(' in line and ')' not in line:
                # Start tracking multiline import
                paren_count = line.count('(') - line.count(')')
                if paren_count > 0:
                    in_multiline_import = True
            i += 1
            continue  # skip this line

        # Detect orphan import continuation lines (only at module level, before classes)
        if not in_class:
            # Check for closing parenthesis orphan
            if _closing_paren_pattern.match(line):
                i += 1
                continue  # skip orphan closing paren

            # Check for symbol-only lines like "    Boolean,"
            orphan_match = _orphan_pattern.match(line)
            if orphan_match:
                symbol = orphan_match.group(1)
                if symbol in _sqlalchemy_symbols:
                    i += 1
                    continue  # skip orphan import symbol

        result.append(line)
        i += 1

    # Clean up excessive blank lines left by removals (max 2 consecutive)
    cleaned = []
    blank_count = 0
    for line in result:
        if line.strip() == '':
            blank_count += 1
            if blank_count <= 2:
                cleaned.append(line)
        else:
            blank_count = 0
            cleaned.append(line)

    return '\n'.join(cleaned)


def _ensure_imports_block(src: str) -> str:
    # Detect if file uses relationship() OUTSIDE HB-AUTOGEN blocks
    # Remove HB-AUTOGEN blocks before searching
    src_without_autogen = re.sub(
        r'# HB-AUTOGEN(?:-IMPORTS)?:BEGIN.*?# HB-AUTOGEN(?:-IMPORTS)?:END',
        '',
        src,
        flags=re.DOTALL
    )
    has_relationship = bool(re.search(r'\brelationship\s*\(', src_without_autogen))
    
    # Build imports block dynamically
    orm_imports = "Mapped, mapped_column"
    if has_relationship:
        orm_imports += ", relationship"
    
    imports_block_dynamic = f"""# HB-AUTOGEN-IMPORTS:BEGIN
from __future__ import annotations

from datetime import date, datetime
from typing import Optional
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy import ForeignKey, CheckConstraint, Index, UniqueConstraint
from sqlalchemy.orm import {orm_imports}
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB as PG_JSONB, INET as PG_INET, ENUM as PG_ENUM
# HB-AUTOGEN-IMPORTS:END
""".rstrip() + "\n"
    
    if "HB-AUTOGEN-IMPORTS:BEGIN" in src and "HB-AUTOGEN-IMPORTS:END" in src:
        # replace existing imports block
        src = re.sub(
            r"# HB-AUTOGEN-IMPORTS:BEGIN.*?# HB-AUTOGEN-IMPORTS:END\s*\n",
            imports_block_dynamic,
            src,
            flags=re.DOTALL,
        )
        return src

    ds0, ds1 = _find_module_docstring_span(src)
    insert_at = ds1
    prefix = src[:insert_at]
    suffix = src[insert_at:]
    if insert_at > 0:
        return prefix + "\n\n" + imports_block_dynamic + "\n" + suffix.lstrip("\n")
    return imports_block_dynamic + "\n" + src.lstrip("\n")


def _camel(name: str) -> str:
    return "".join([p.capitalize() for p in re.split(r"[_\s]+", name) if p])


def _create_model_skeleton(path: Path, table: str, class_name: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        return
    content = f'''"""
Auto-generated model skeleton for table {table}.
Do not edit HB-AUTOGEN blocks manually.
"""

from app.models.base import Base


class {class_name}(Base):
    __tablename__ = "{table}"

    # Manual customizations below (preserved across regen)
'''
    path.write_text(content, encoding="utf-8")


def _pytype_for(coltype: sa.types.TypeEngine) -> str:
    # best-effort for typing only
    t = coltype
    if hasattr(sa.dialects.postgresql, "UUID") and isinstance(t, sa.dialects.postgresql.UUID):
        return "UUID"
    if isinstance(t, (sa.Integer, sa.BigInteger, sa.SmallInteger)):
        return "int"
    if isinstance(t, sa.Text):
        return "str"
    if isinstance(t, sa.String):
        return "str"
    if isinstance(t, sa.Boolean):
        return "bool"
    if isinstance(t, sa.Date):
        return "date"
    if isinstance(t, sa.DateTime):
        return "datetime"
    return "object"


def _sa_type_expr(coltype: sa.types.TypeEngine) -> str:
    t = coltype
    # PostgreSQL ARRAY — must come before scalar type checks
    if isinstance(t, sa.ARRAY) or (hasattr(sa.dialects.postgresql, 'ARRAY') and isinstance(t, sa.dialects.postgresql.ARRAY)):
        item_type = getattr(t, 'item_type', None)
        if item_type is not None:
            inner = _sa_type_expr(item_type)
            return f"sa.ARRAY({inner})"
        return "sa.ARRAY(sa.Text())"  # fallback if item_type unknown
    # PostgreSQL UUID
    if hasattr(sa.dialects.postgresql, "UUID") and isinstance(t, sa.dialects.postgresql.UUID):
        return "PG_UUID(as_uuid=True)"
    if hasattr(sa.dialects.postgresql, "JSONB") and isinstance(t, sa.dialects.postgresql.JSONB):
        return "PG_JSONB()"
    if hasattr(sa.dialects.postgresql, "INET") and isinstance(t, sa.dialects.postgresql.INET):
        return "PG_INET()"
    if hasattr(sa.dialects.postgresql, "ENUM") and isinstance(t, sa.dialects.postgresql.ENUM):
        enum_values = list(getattr(t, "enums", []) or [])
        enum_name = getattr(t, "name", None)
        values_expr = ", ".join(repr(v) for v in enum_values)
        if enum_name and values_expr:
            return f"PG_ENUM({values_expr}, name={enum_name!r}, create_type=False)"
        if enum_name:
            return f"PG_ENUM(name={enum_name!r}, create_type=False)"
        return "sa.Enum()"
    # string types
    if isinstance(t, sa.Text):
        return "sa.Text()"
    if isinstance(t, sa.String):
        length = getattr(t, "length", None)
        if length is None:
            return "sa.String()"
        return f"sa.String(length={length})"
    # numeric
    if isinstance(t, sa.SmallInteger):
        return "sa.SmallInteger()"
    if isinstance(t, sa.Integer):
        return "sa.Integer()"
    if isinstance(t, sa.BigInteger):
        return "sa.BigInteger()"
    if isinstance(t, sa.Numeric):
        prec = getattr(t, "precision", None)
        scale = getattr(t, "scale", None)
        if prec is not None and scale is not None:
            return f"sa.Numeric({prec}, {scale})"
        if prec is not None:
            return f"sa.Numeric({prec})"
        return "sa.Numeric()"
    # bool
    if isinstance(t, sa.Boolean):
        return "sa.Boolean()"
    # date/time
    if isinstance(t, sa.Date):
        return "sa.Date()"
    if isinstance(t, sa.DateTime):
        tz = bool(getattr(t, "timezone", False))
        return f"sa.DateTime(timezone={tz})"
    # fallback
    return f"sa.{t.__class__.__name__}()"


def _get_db_url(env_key: str) -> str:
    v = os.getenv(env_key)
    if not v or not v.strip():
        raise SystemExit(f"[ERROR] env var not set: {env_key}")
    return v.strip()


def _connect(url: str) -> sa.Engine:
    # allow DATABASE_URL (async) but prefer sync key already
    u = make_url(url)
    safe = u.render_as_string(hide_password=True)
    print(f"[INFO] db_url_safe={safe}")
    return sa.create_engine(url, pool_pre_ping=True)


@dataclass(frozen=True)
class FKSpec:
    name: str
    constrained: Tuple[str, ...]
    referred_table: str
    referred_cols: Tuple[str, ...]
    ondelete: Optional[str]


def _inspect_table(ins: sa.Inspector, table: str, schema: str) -> Tuple[List[dict], List[str], List[FKSpec], List[dict], List[dict], List[dict]]:
    cols = ins.get_columns(table, schema=schema)
    pk = ins.get_pk_constraint(table, schema=schema) or {}
    pk_cols = pk.get("constrained_columns") or []
    fks_raw = ins.get_foreign_keys(table, schema=schema) or []
    fks: List[FKSpec] = []
    for fk in fks_raw:
        opts = fk.get("options") or {}
        fks.append(
            FKSpec(
                name=fk.get("name") or "",
                constrained=tuple(fk.get("constrained_columns") or []),
                referred_table=fk.get("referred_table") or "",
                referred_cols=tuple(fk.get("referred_columns") or []),
                ondelete=(opts.get("ondelete") or None),
            )
        )
    checks = ins.get_check_constraints(table, schema=schema) or []
    uniques = ins.get_unique_constraints(table, schema=schema) or []
    indexes = ins.get_indexes(table, schema=schema) or []
    return cols, list(pk_cols), fks, checks, uniques, indexes


def _fk_for_col(fks: List[FKSpec], col: str) -> Optional[FKSpec]:
    # only single-column FK inline
    for fk in fks:
        if fk.constrained == (col,):
            return fk
    return None


def _render_class_block(table: str, cols: List[dict], pk_cols: List[str], fks: List[FKSpec], checks: List[dict], uniques: List[dict], indexes: List[dict], fk_ondelete_by_name: Optional[Dict[str, Optional[str]]] = None, indent: str = "    ") -> str:
    lines: List[str] = []
    fk_ondelete_by_name = fk_ondelete_by_name or {}
    lines.append(f"{indent}{CLASS_BLOCK_BEGIN}")
    lines.append(f"{indent}# AUTO-GENERATED FROM DB (SSOT). DO NOT EDIT MANUALLY.")
    lines.append(f"{indent}# Table: public.{table}")

    # table args: checks, uniques, indexes
    ta: List[str] = []

    for ck in checks:
        name = ck.get("name")
        sqltext = (ck.get("sqltext") or "").strip()
        if name and sqltext:
            ta.append(f"CheckConstraint({sqltext!r}, name={name!r})")

    for uq in uniques:
        name = uq.get("name")
        cols_uq = uq.get("column_names") or []
        if name and cols_uq:
            cols_expr = ", ".join([repr(c) for c in cols_uq])
            ta.append(f"UniqueConstraint({cols_expr}, name={name!r})")

    # PostgreSQL can reflect the backing index of a UNIQUE CONSTRAINT in get_indexes().
    # If we already emitted a UniqueConstraint from get_unique_constraints(), do not
    # emit an Index with the same name to avoid structural diffs in Alembic parity.
    unique_constraint_names = {
        uq.get("name")
        for uq in uniques
        if uq.get("name")
    }

    for ix in indexes:
        name = ix.get("name")
        col_names = ix.get("column_names") or []
        if not name or not col_names:
            continue
        unique = bool(ix.get("unique", False))
        if unique and name in unique_constraint_names:
            continue
        dialect_opts = ix.get("dialect_options") or {}
        pg_where = None
        # best-effort key used by SQLAlchemy for partial indexes
        pg_where = dialect_opts.get("postgresql_where") or dialect_opts.get("where") or None
        cols_expr = ", ".join([repr(c) for c in col_names])
        if pg_where:
            ta.append(f"Index({name!r}, {cols_expr}, unique={unique}, postgresql_where=sa.text({str(pg_where)!r}))")
        else:
            ta.append(f"Index({name!r}, {cols_expr}, unique={unique})")

    if ta:
        lines.append(f"{indent}__table_args__ = (")
        for x in ta:
            lines.append(f"{indent}    {x},")
        lines.append(f"{indent})")
        lines.append("")

    # columns
    # add typing imports hint if needed (date/datetime/UUID)
    needs_date = any(isinstance(c["type"], sa.Date) for c in cols)
    needs_dt = any(isinstance(c["type"], sa.DateTime) for c in cols)
    needs_uuid = any(hasattr(sa.dialects.postgresql, "UUID") and isinstance(c["type"], sa.dialects.postgresql.UUID) for c in cols)
    if needs_date or needs_dt or needs_uuid:
        # don't try to edit manual imports; just keep hints in comments
        lines.append(f"{indent}# NOTE: typing helpers may require: from datetime import date, datetime; from uuid import UUID")
        lines.append("")

    for c in cols:
        name = c["name"]
        coltype = c["type"]
        nv = c.get("nullable", True)
        nullable = True if nv is None else bool(nv)
        default = c.get("default")
        py_t = _pytype_for(coltype)
        sa_t = _sa_type_expr(coltype)

        ann_t = py_t
        if name not in pk_cols and nullable:
            ann_t = f"Optional[{py_t}]"

        kwargs: List[str] = []
        if name in pk_cols:
            kwargs.append("primary_key=True")
        if name not in pk_cols:
            kwargs.append("nullable=True" if nullable else "nullable=False")
        if default:
            # keep DB expression as server_default
            kwargs.append(f"server_default=sa.text({str(default)!r})")

        fk = _fk_for_col(fks, name)
        fk_expr = None
        if fk and fk.referred_table and fk.referred_cols:
            ref = f"{fk.referred_table}.{fk.referred_cols[0]}"
            fk_kwargs: List[str] = []
            if fk.name:
                fk_kwargs.append(f"name={fk.name!r}")
            normalized_fk_name = _normalize_constraint_name(fk.name)
            has_ssot_fk = bool(normalized_fk_name and normalized_fk_name in fk_ondelete_by_name)
            ssot_ondelete = fk_ondelete_by_name.get(normalized_fk_name) if has_ssot_fk else None
            effective_ondelete = ssot_ondelete if has_ssot_fk else (str(fk.ondelete).upper() if fk.ondelete else None)
            if effective_ondelete:
                fk_kwargs.append(f"ondelete={effective_ondelete!r}")
            if fk.name and fk.name in FORCE_USE_ALTER_FK_NAMES:
                fk_kwargs.append("use_alter=True")
            fk_expr = f"ForeignKey({ref!r}" + (", " + ", ".join(fk_kwargs) if fk_kwargs else "") + ")"

        args = [sa_t]
        if fk_expr:
            args.append(fk_expr)

        arg_s = ", ".join(args)
        kw_s = (", " + ", ".join(kwargs)) if kwargs else ""
        # mapped column
        lines.append(f"{indent}{name}: Mapped[{ann_t}] = mapped_column({arg_s}{kw_s})")

    lines.append(f"{indent}{CLASS_BLOCK_END}")
    return "\n".join(lines) + "\n"


def _find_model_file(models_dir: Path, table: str) -> Path:
    pat = re.compile(rf"__tablename__\s*=\s*['\"]{re.escape(table)}['\"]")
    hits: List[Path] = []
    for p in models_dir.rglob("*.py"):
        txt = p.read_text(encoding="utf-8", errors="replace")
        if pat.search(txt):
            hits.append(p)
    if not hits:
        raise SystemExit(f"[ERROR] model file not found for __tablename__='{table}' under {models_dir}")
    # deterministic: first by name
    hits.sort(key=lambda x: str(x))
    return hits[0]


def find_class_span_for_tablename(src: str, table: str) -> tuple[int, int, str]:
    """
    Find the span (start, end) of the class containing __tablename__ = '<table>'.

    Returns:
        (start_idx, end_idx, base_indent)
    """
    tab_m = re.search(rf"^(\s*)__tablename__\s*=\s*['\"]{re.escape(table)}['\"]\s*$",
                      src, flags=re.MULTILINE)
    if not tab_m:
        raise SystemExit(f"[ERROR] __tablename__='{table}' not found")

    base_indent = tab_m.group(1)
    tablename_pos = tab_m.start()

    # Find 'class ...:' before __tablename__
    before = src[:tablename_pos]
    class_matches = list(re.finditer(r'^class\s+\w+.*?:\s*$', before, re.MULTILINE))
    if not class_matches:
        raise SystemExit(f"[ERROR] No class found before __tablename__='{table}'")

    class_start = class_matches[-1].start()

    # Find end: next top-level class or EOF
    after = src[class_start+1:]
    m_next = re.search(r'(?m)^class\s+\w+.*?:\s*$', after)
    class_end = (class_start + 1 + m_next.start()) if m_next else len(src)

    # Sanity check: class_end must be after __tablename__
    if class_end <= tablename_pos:
        raise SystemExit(
            f"[ERROR] class_end ({class_end}) <= tablename_pos ({tablename_pos}). "
            f"Possible false positive in class boundary detection."
        )

    return (class_start, class_end, base_indent)


def remove_duplicate_columns_in_span(src: str, span_start: int, span_end: int) -> str:
    """Remove duplicate mapped_column ONLY within span (target class)."""
    prefix = src[:span_start]
    span = src[span_start:span_end]
    suffix = src[span_end:]
    span_cleaned = _remove_duplicate_column_definitions_impl(span)
    return prefix + span_cleaned + suffix


def _remove_duplicate_column_definitions_impl(src: str) -> str:
    """
    Implementation of duplicate removal.
    Operates on a single class body (span).

    Preserves:
    - Everything inside HB-AUTOGEN blocks
    - relationship() definitions
    - @property decorators and methods

    Removes:
    - Duplicate mapped_column() definitions outside HB-AUTOGEN
    - Bare Mapped[...] annotations without = assignment (implicit columns)
    - Duplicate __table_args__ definitions outside HB-AUTOGEN (always removed; autogen is SSOT)
    """
    lines = src.split('\n')
    result_lines = []
    in_autogen_block = False
    i = 0

    while i < len(lines):
        line = lines[i]

        # Track HB-AUTOGEN blocks (both IMPORTS and main block)
        is_begin = ('HB-AUTOGEN-IMPORTS:BEGIN' in line) or ('HB-AUTOGEN:BEGIN' in line)
        is_end   = ('HB-AUTOGEN-IMPORTS:END' in line) or ('HB-AUTOGEN:END' in line)

        if is_begin:
            in_autogen_block = True
            result_lines.append(line)
            i += 1
            continue

        if is_end:
            # Preserve END line (still part of the block)
            result_lines.append(line)
            in_autogen_block = False
            i += 1
            continue

        # Always keep lines inside HB-AUTOGEN blocks
        if in_autogen_block:
            result_lines.append(line)
            i += 1
            continue

        # Detect duplicate column definition patterns (outside HB-AUTOGEN)
        # Pattern 1 (new style): "    name: Mapped[...] = mapped_column(...)"
        # Pattern 2 (legacy):    "    name = Column(...)"
        # Pattern 3 (bare):      "    name: Mapped[...]" (without = assignment, implicit column)
        is_duplicate_column = (
            re.match(r'^\s+\w+:\s*Mapped\[.*\]\s*=\s*mapped_column\s*\(', line)
            or re.match(r'^\s+\w+\s*=\s*Column\s*\(', line)
            or re.match(r'^\s+\w+:\s*Mapped\[.*\]\s*$', line)
        )

        if is_duplicate_column:
            # Collect ALL lines of this definition (including continuations)
            definition_lines = [line]
            open_count = line.count('(')
            close_count = line.count(')')

            j = i + 1
            while j < len(lines) and open_count > close_count:
                definition_lines.append(lines[j])
                open_count += lines[j].count('(')
                close_count += lines[j].count(')')
                j += 1

            # Remove ALL duplicate column definitions outside HB-AUTOGEN
            # (including PKs - autogen will regenerate them inside the block)
            i = j
            continue

        # Detect __table_args__ outside HB-AUTOGEN (autogen is SSOT, always remove)
        is_duplicate_table_args = re.match(r'^\s+__table_args__\s*=', line)

        if is_duplicate_table_args:
            # Collect ALL lines of this __table_args__ definition (count parens)
            open_count = line.count('(')
            close_count = line.count(')')

            j = i + 1
            while j < len(lines) and open_count > close_count:
                open_count += lines[j].count('(')
                close_count += lines[j].count(')')
                j += 1

            # Warning: __table_args__ found outside autogen and removed
            print(f"[WARN] __table_args__ found outside HB-AUTOGEN block; removed (autogen is SSOT)")

            # Skip all lines of this definition
            i = j
            continue

        # Keep everything else (relationships, properties, methods, etc.)
        result_lines.append(line)
        i += 1

    return '\n'.join(result_lines)


def _patch_class_body(src: str, table: str, new_block: str) -> str:
    # Find class span for target table
    class_start, class_end, base_indent = find_class_span_for_tablename(src, table)

    # Extract class body
    class_body = src[class_start:class_end]

    # Check if markers exist WITHIN this class (not globally)
    markers_exist_in_class = (CLASS_BLOCK_BEGIN in class_body and
                              CLASS_BLOCK_END in class_body)

    # Find __tablename__ position within the class
    tab_m = re.search(rf"^(\s*)__tablename__\s*=\s*['\"]{re.escape(table)}['\"]\s*$",
                      class_body, flags=re.MULTILINE)
    if not tab_m:
        raise SystemExit(f"[ERROR] __tablename__='{table}' not found in class body")

    # Insert markers if missing in THIS class
    if not markers_exist_in_class:
        insert_pos = class_start + tab_m.end()
        src = src[:insert_pos] + "\n\n" + new_block + "\n" + src[insert_pos:]
        # Re-calculate class_end after insertion
        class_start, class_end, base_indent = find_class_span_for_tablename(src, table)
        class_body = src[class_start:class_end]

    # Replace between markers WITHIN this class only
    pattern = re.compile(
        rf"^{re.escape(base_indent)}{re.escape(CLASS_BLOCK_BEGIN)}.*?^{re.escape(base_indent)}{re.escape(CLASS_BLOCK_END)}\s*$",
        flags=re.MULTILINE | re.DOTALL,
    )

    if not pattern.search(class_body):
        # Fallback: simple replace without indent anchors (within class)
        pattern2 = re.compile(rf"{re.escape(CLASS_BLOCK_BEGIN)}.*?{re.escape(CLASS_BLOCK_END)}", flags=re.DOTALL)
        if not pattern2.search(class_body):
            raise SystemExit("[ERROR] could not locate HB-AUTOGEN block in target class")
        class_body = pattern2.sub(new_block.strip(), class_body)
    else:
        class_body = pattern.sub(new_block.strip(), class_body)

    # Reconstruct source with updated class
    src = src[:class_start] + class_body + src[class_end:]

    # Recalculate span after reconstruction (class boundaries may have shifted)
    class_start2, class_end2, _ = find_class_span_for_tablename(src, table)

    # Remove duplicate column definitions ONLY within target class (updated span)
    src = remove_duplicate_columns_in_span(src, class_start2, class_end2)

    return src


def cmd_apply(args: argparse.Namespace) -> int:
    table = args.table
    schema = args.schema
    env_key = args.db_env
    models_dir = Path(args.models_dir)
    out_file: Optional[Path] = Path(args.out).resolve() if args.out else None

    url = _get_db_url(env_key)
    eng = _connect(url)
    ins = sa.inspect(eng)

    cols, pk_cols, fks, checks, uniques, indexes = _inspect_table(ins, table, schema)
    fk_ondelete_by_name = _fk_ondelete_map_from_schema_sql(SCHEMA_SQL)

    model_file = (args.model_file or "").strip()
    if model_file:
        model_path = Path(model_file)
        if not model_path.is_absolute():
            model_path = Path.cwd() / model_path
        model_path = model_path.resolve()
        if not model_path.exists():
            if not args.create:
                raise SystemExit(f"[ERROR] model file not found: {model_path} (use --create)")
            class_name = (args.class_name or _camel(table)).strip()
            _create_model_skeleton(model_path, table, class_name)
    else:
        try:
            model_path = _find_model_file(models_dir, table)
        except SystemExit:
            if not args.create:
                raise
            model_path = (models_dir / f"{table}.py").resolve()
            class_name = (args.class_name or _camel(table)).strip()
            _create_model_skeleton(model_path, table, class_name)

    print(f"[INFO] model_path={model_path}")

    # render block with same indent as in file: detect from __tablename__ line
    src0 = model_path.read_text(encoding="utf-8", errors="replace")
    tab_m = re.search(rf"^(\s*)__tablename__\s*=\s*['\"]{re.escape(table)}['\"]\s*$", src0, flags=re.MULTILINE)
    indent = tab_m.group(1) if tab_m else "    "

    new_block = _render_class_block(
        table,
        cols,
        pk_cols,
        fks,
        checks,
        uniques,
        indexes,
        fk_ondelete_by_name=fk_ondelete_by_name,
        indent=indent,
    )

    # ensure imports marker exists and replace it
    src1 = _ensure_imports_block(src0)
    # remove original imports that are now covered by HB-AUTOGEN-IMPORTS
    src1 = _remove_duplicate_imports_outside_autogen(src1)
    src2 = _patch_class_body(src1, table, new_block)

    if out_file:
        out_file.parent.mkdir(parents=True, exist_ok=True)
        out_file.write_text(src2, encoding="utf-8")
        print(f"[OK] written: {out_file}")
    else:
        model_path.write_text(src2, encoding="utf-8")
        print(f"[OK] patched in-place: {model_path}")

    return 0


def cmd_preview(args: argparse.Namespace) -> int:
    table = args.table
    schema = args.schema
    env_key = args.db_env
    url = _get_db_url(env_key)
    eng = _connect(url)
    ins = sa.inspect(eng)

    cols, pk_cols, fks, checks, uniques, indexes = _inspect_table(ins, table, schema)
    fk_ondelete_by_name = _fk_ondelete_map_from_schema_sql(SCHEMA_SQL)
    block = _render_class_block(
        table,
        cols,
        pk_cols,
        fks,
        checks,
        uniques,
        indexes,
        fk_ondelete_by_name=fk_ondelete_by_name,
        indent="    ",
    )
    print(IMPORTS_BLOCK)
    print(block)
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(prog="autogen_model_from_db")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("preview")
    p.add_argument("--table", required=True)
    p.add_argument("--schema", default="public")
    p.add_argument("--db-env", default="DATABASE_URL_SYNC")
    p.set_defaults(func=cmd_preview)

    a = sub.add_parser("apply")
    a.add_argument("--table", required=True)
    a.add_argument("--schema", default="public")
    a.add_argument("--db-env", default="DATABASE_URL_SYNC")
    a.add_argument("--models-dir", default=r"app\models")
    a.add_argument("--out", default="")
    a.add_argument("--create", action="store_true")
    a.add_argument("--model-file", default="")
    a.add_argument("--class-name", default="")
    a.set_defaults(func=cmd_apply)

    args = ap.parse_args(argv)
    return int(args.func(args))  # type: ignore[misc]


if __name__ == "__main__":
    raise SystemExit(main())