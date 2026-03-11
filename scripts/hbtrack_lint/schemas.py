"""
Validação de documentos contra seus JSON Schemas.

SSOT: docs/hbtrack/modulos/atletas/MOTORES.md
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class SchemaValidationResult:
    errors: list[dict] = field(default_factory=list)
    warnings: list[dict] = field(default_factory=list)
    results: list[dict] = field(default_factory=list)


# Mapeamento: nome do documento → caminho relativo ao module_root para o schema
SCHEMA_MAP = {
    "00_ATLETAS_CROSS_LINTER_RULES.json": "00_ATLETAS_CROSS_LINTER_RULES.schema.json",
    "12_ATLETAS_EXECUTION_BINDINGS.yaml": "12_ATLETAS_EXECUTION_BINDINGS.schema.json",
}


def validate_documents_against_schemas(
    repo_root: Path,
    module_root: Path,
    contracts: dict[str, object],
) -> SchemaValidationResult:
    result = SchemaValidationResult()

    try:
        from jsonschema import Draft202012Validator
    except ImportError:
        result.warnings.append({
            "reason": "jsonschema não instalado — validação de schemas ignorada"
        })
        return result

    for doc_name, schema_rel in SCHEMA_MAP.items():
        if doc_name not in contracts:
            continue

        schema_path = module_root / schema_rel
        if not schema_path.exists():
            result.warnings.append({
                "document": doc_name,
                "reason": f"Schema não encontrado: {schema_path}",
            })
            continue

        schema = json.loads(schema_path.read_text(encoding="utf-8"))

        try:
            validator = Draft202012Validator(schema)
        except Exception as exc:
            result.errors.append({
                "document": doc_name,
                "reason": f"Schema inválido: {exc}",
            })
            continue

        doc_errors = sorted(
            validator.iter_errors(contracts[doc_name]),
            key=lambda e: list(e.path),
        )

        if doc_errors:
            for err in doc_errors:
                result.errors.append({
                    "document": doc_name,
                    "reason": err.message,
                    "path": list(err.path),
                })
        else:
            result.results.append({"document": doc_name, "status": "PASS_SCHEMA"})

    return result
