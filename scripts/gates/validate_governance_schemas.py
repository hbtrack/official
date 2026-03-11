"""
GAP-B5 -- validate_governance_schemas.py
Gate automatico: valida ENGINE_CONSTITUTION.json e 00_ATLETAS_MODULE_RULES.json
contra seus respectivos schemas JSON Schema Draft-07.
Tambem valida integridade dos refs relativos (meta.schema_ref, meta.inherits_constitution).

Exit codes:
  0 -- todos passam
  1 -- algum falha (erro de validacao ou ref quebrada)
  2 -- jsonschema nao instalado
"""
from __future__ import annotations

import json
import pathlib
import sys


def _load_json(path: pathlib.Path, label: str) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"FAIL: {label} -- JSON invalido: {e}")
        sys.exit(1)


def _validate_refs(document: dict, document_path: pathlib.Path, label: str) -> bool:
    """Valida meta.schema_ref e meta.inherits_constitution como paths relativos existentes."""
    meta = document.get("meta", {})
    ok = True
    base_dir = document_path.parent

    for field in ("schema_ref", "inherits_constitution"):
        ref = meta.get(field)
        if ref is None:
            continue  # campo opcional para ENGINE_CONSTITUTION (schema_ref resolvido pelo caller)
        resolved = (base_dir / ref).resolve()
        if not resolved.exists():
            print(f"FAIL: {label} -- meta.{field} aponta para arquivo inexistente: {resolved}")
            ok = False
        else:
            try:
                json.loads(resolved.read_text(encoding="utf-8"))
            except json.JSONDecodeError as e:
                print(f"FAIL: {label} -- meta.{field} resolve para JSON invalido: {e}")
                ok = False
    return ok


def main() -> int:
    try:
        import jsonschema
    except ImportError:
        print("ERROR: jsonschema nao instalado. Execute: pip install jsonschema")
        return 2

    root = pathlib.Path(__file__).resolve().parent.parent.parent
    governance_dir = root / "docs" / "hbtrack" / "_governance"

    pairs = [
        (
            governance_dir / "ENGINE_CONSTITUTION.json",
            governance_dir / "ENGINE_CONSTITUTION.schema.json",
            "ENGINE_CONSTITUTION.json",
        ),
        (
            root / "docs" / "hbtrack" / "modulos" / "atletas" / "00_ATLETAS_MODULE_RULES.json",
            governance_dir / "00_MODULE_RULES.schema.json",
            "00_ATLETAS_MODULE_RULES.json",
        ),
    ]

    all_pass = True

    for doc_path, schema_path, label in pairs:
        # Verificar existencia dos arquivos
        if not doc_path.exists():
            print(f"FAIL: {label} -- arquivo nao encontrado: {doc_path}")
            all_pass = False
            continue
        if not schema_path.exists():
            print(f"FAIL: {label} -- schema nao encontrado: {schema_path}")
            all_pass = False
            continue

        document = _load_json(doc_path, label)
        schema = _load_json(schema_path, f"{label} schema")

        # 1. Validar refs de integridade (meta.schema_ref e meta.inherits_constitution)
        if not _validate_refs(document, doc_path, label):
            all_pass = False
            continue

        # 2. Validar documento contra schema
        try:
            jsonschema.validate(instance=document, schema=schema)
            print(f"PASS: {label}")
        except jsonschema.ValidationError as e:
            print(f"FAIL: {label} -- ValidationError: {e.message} (path: {list(e.absolute_path)})")
            all_pass = False
        except jsonschema.SchemaError as e:
            print(f"FAIL: {label} -- SchemaError (schema invalido): {e.message}")
            all_pass = False

    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
