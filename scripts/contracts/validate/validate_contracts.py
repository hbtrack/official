"""
HB Track -- validate_contracts.py

Contrato mínimo (sem interpretação livre):
- Este script consome `.contract_driven/DOMAIN_AXIOMS.json` e aplica validações determinísticas.
- As funções públicas abaixo DEVEM existir com as assinaturas exatas (pipeline contract).
- Execução completa (`profile=ci`, sem `--stage`) atualiza `_reports/contract_gates/latest.json`.
- Execuções parciais devem gerar evidência machine-readable em caminho escopado sob `_reports/contract_gates/`.

Blocking codes que o script deve conhecer:
  BLOCKED_ENUM_OUTSIDE_AXIOMS
  BLOCKED_FORMAT_VIOLATION
  BLOCKED_STATE_MACHINE_VIOLATION
  BLOCKED_FORBIDDEN_TRANSITION
  BLOCKED_NON_NORMALIZED_DERIVED_DIFF_CHECK
  BLOCKED_INVALID_MODULE_AXIOM_EXTENSION
  BLOCKED_AXIOM_EXTENSION_COLLISION
  BLOCKED_AXIOM_NAME_CLASH

  BLOCKED_AXIOM_* (AXIOM_INTEGRITY_GATE)

Observação: este arquivo define funções e utilitários mínimos. A orquestração completa dos
gates é descrita em `docs/_canon/CI_CONTRACT_GATES.md`.
"""

from __future__ import annotations

import dataclasses
import datetime
import hashlib
import importlib.util
import json
import os
import pathlib
import platform
import re
import shutil
import subprocess
import sys
import time
from typing import Any

import yaml


BLOCKED_ENUM_OUTSIDE_AXIOMS = "BLOCKED_ENUM_OUTSIDE_AXIOMS"
BLOCKED_FORMAT_VIOLATION = "BLOCKED_FORMAT_VIOLATION"
BLOCKED_STATE_MACHINE_VIOLATION = "BLOCKED_STATE_MACHINE_VIOLATION"
BLOCKED_FORBIDDEN_TRANSITION = "BLOCKED_FORBIDDEN_TRANSITION"
BLOCKED_ARAZZO_OPENAPI_LINK_MISSING = "BLOCKED_ARAZZO_OPENAPI_LINK_MISSING"
BLOCKED_ERROR_MODEL_MISMATCH = "BLOCKED_ERROR_MODEL_MISMATCH"
BLOCKED_CROSS_SPEC_DIVERGENCE = "BLOCKED_CROSS_SPEC_DIVERGENCE"
BLOCKED_NON_NORMALIZED_DERIVED_DIFF_CHECK = "BLOCKED_NON_NORMALIZED_DERIVED_DIFF_CHECK"
BLOCKED_INVALID_MODULE_AXIOM_EXTENSION = "BLOCKED_INVALID_MODULE_AXIOM_EXTENSION"
BLOCKED_AXIOM_EXTENSION_COLLISION = "BLOCKED_AXIOM_EXTENSION_COLLISION"
BLOCKED_AXIOM_NAME_CLASH = "BLOCKED_AXIOM_NAME_CLASH"

BLOCKED_LAYOUT_NONCOMPLIANCE = "BLOCKED_LAYOUT_NONCOMPLIANCE"
BLOCKED_MISSING_MODULE_DOC = "BLOCKED_MISSING_MODULE_DOC"
BLOCKED_INVALID_MODULE_DOC_HEADER = "BLOCKED_INVALID_MODULE_DOC_HEADER"
WARN_API_NORMATIVE_OUTSIDE_SSOT = "WARN_API_NORMATIVE_OUTSIDE_SSOT"
BLOCKED_OWASP_CONTROL_MATRIX_MISSING = "BLOCKED_OWASP_CONTROL_MATRIX_MISSING"
BLOCKED_OWASP_CONTROL_MATRIX_INVALID = "BLOCKED_OWASP_CONTROL_MATRIX_INVALID"
BLOCKED_MODULE_SOURCE_AUTHORITY_MATRIX_MISSING = "BLOCKED_MODULE_SOURCE_AUTHORITY_MATRIX_MISSING"
BLOCKED_MODULE_SOURCE_AUTHORITY_MATRIX_INVALID = "BLOCKED_MODULE_SOURCE_AUTHORITY_MATRIX_INVALID"
BLOCKED_MODULE_REGISTRY_MISSING = "BLOCKED_MODULE_REGISTRY_MISSING"
BLOCKED_MODULE_REGISTRY_INVALID = "BLOCKED_MODULE_REGISTRY_INVALID"
BLOCKED_BOUNDARY_USERS_IDENTITY_ACCESS = "BLOCKED_BOUNDARY_USERS_IDENTITY_ACCESS"
BLOCKED_WELLNESS_MEDICAL_BOUNDARY = "BLOCKED_WELLNESS_MEDICAL_BOUNDARY"
BLOCKED_SCOUT_TAXONOMY = "BLOCKED_SCOUT_TAXONOMY"
BLOCKED_ASYNC_REQUIRED_MODULE = "BLOCKED_ASYNC_REQUIRED_MODULE"
BLOCKED_EXTERNAL_SOURCE_AUTHORITY = "BLOCKED_EXTERNAL_SOURCE_AUTHORITY"
BLOCKED_OPENAPI_ROOT_MODULE_SYNC = "BLOCKED_OPENAPI_ROOT_MODULE_SYNC"
BLOCKED_PRE_CONTRACT_EVIDENCE = "BLOCKED_PRE_CONTRACT_EVIDENCE"
BLOCKED_SHADOW_AUTHORITY = "BLOCKED_SHADOW_AUTHORITY"
BLOCKED_CANON_INTRUDER = "BLOCKED_CANON_INTRUDER"
BLOCKED_TOOLING_CONFIG_INVALID = "BLOCKED_TOOLING_CONFIG_INVALID"

BLOCKED_TRACEABILITY_MANIFEST_INVALID = "BLOCKED_TRACEABILITY_MANIFEST_INVALID"
BLOCKED_TRACEABILITY_INPUT_MISSING = "BLOCKED_TRACEABILITY_INPUT_MISSING"
BLOCKED_TRACEABILITY_HASH_MISMATCH = "BLOCKED_TRACEABILITY_HASH_MISMATCH"

BLOCKED_AXIOM_FILE_NOT_FOUND = "BLOCKED_AXIOM_FILE_NOT_FOUND"
BLOCKED_INVALID_AXIOM_JSON = "BLOCKED_INVALID_AXIOM_JSON"
BLOCKED_AXIOM_SCHEMA_INVALID = "BLOCKED_AXIOM_SCHEMA_INVALID"
BLOCKED_AXIOM_INVALID_REGEX = "BLOCKED_AXIOM_INVALID_REGEX"
BLOCKED_AXIOM_BROKEN_INTERNAL_REFERENCE = "BLOCKED_AXIOM_BROKEN_INTERNAL_REFERENCE"
BLOCKED_AXIOM_INVALID_ENUM_DEFINITION = "BLOCKED_AXIOM_INVALID_ENUM_DEFINITION"
BLOCKED_AXIOM_ILLEGAL_OPEN_SET_POLICY = "BLOCKED_AXIOM_ILLEGAL_OPEN_SET_POLICY"
BLOCKED_AXIOM_ILLEGAL_CLOSED_SET_EXTENSION_POLICY = "BLOCKED_AXIOM_ILLEGAL_CLOSED_SET_EXTENSION_POLICY"
BLOCKED_AXIOM_INVALID_STATE_MACHINE = "BLOCKED_AXIOM_INVALID_STATE_MACHINE"
BLOCKED_AXIOM_ORPHAN_STATE = "BLOCKED_AXIOM_ORPHAN_STATE"
BLOCKED_AXIOM_DEAD_END_STATE = "BLOCKED_AXIOM_DEAD_END_STATE"
BLOCKED_AXIOM_FORBIDDEN_TRANSITION_CONFLICT = "BLOCKED_AXIOM_FORBIDDEN_TRANSITION_CONFLICT"
BLOCKED_AXIOM_TERMINAL_STATE_WITH_OUTGOING_EDGE = "BLOCKED_AXIOM_TERMINAL_STATE_WITH_OUTGOING_EDGE"
BLOCKED_AXIOM_INVALID_DISCIPLINARY_PROGRESSION = "BLOCKED_AXIOM_INVALID_DISCIPLINARY_PROGRESSION"
BLOCKED_AXIOM_DISCIPLINARY_PRECONDITION_MISSING = "BLOCKED_AXIOM_DISCIPLINARY_PRECONDITION_MISSING"
BLOCKED_AXIOM_DISCIPLINARY_ORDER_CONFLICT = "BLOCKED_AXIOM_DISCIPLINARY_ORDER_CONFLICT"
BLOCKED_AXIOM_INVALID_ERROR_MODEL = "BLOCKED_AXIOM_INVALID_ERROR_MODEL"
BLOCKED_AXIOM_MISSING_REQUIRED_ERROR_FIELD = "BLOCKED_AXIOM_MISSING_REQUIRED_ERROR_FIELD"
BLOCKED_AXIOM_INVALID_CROSS_SURFACE_CONSTRAINT = "BLOCKED_AXIOM_INVALID_CROSS_SURFACE_CONSTRAINT"
BLOCKED_AXIOM_INVALID_NORMALIZATION_POLICY = "BLOCKED_AXIOM_INVALID_NORMALIZATION_POLICY"
BLOCKED_AXIOM_INVALID_NORMALIZATION_REGEX = "BLOCKED_AXIOM_INVALID_NORMALIZATION_REGEX"
BLOCKED_AXIOM_INVALID_VALIDATOR_CONTRACT = "BLOCKED_AXIOM_INVALID_VALIDATOR_CONTRACT"
BLOCKED_AXIOM_INTEGRITY = "BLOCKED_AXIOM_INTEGRITY"
BLOCKED_FEATURE_COVERAGE_MISSING = "BLOCKED_FEATURE_COVERAGE_MISSING"
BLOCKED_LEGACY_IN_CRITICAL_PATH = "BLOCKED_LEGACY_IN_CRITICAL_PATH"  # FASE 7

MODULE_STATUS_ORDER = (
    "scaffold",
    "draft_contract",
    "validated_contract",
    "implementation_ready",
    "implemented",
    "staging_validated",
    "released",
)
IMPLEMENTATION_AUTHORIZED_STATUSES = {
    "implementation_ready",
    "implemented",
    "staging_validated",
    "released",
}
PRE_CONTRACT_EVIDENCE_STATUSES = {"validated_contract", *IMPLEMENTATION_AUTHORIZED_STATUSES}

_KNOWN_BLOCKING_CODES = {
    BLOCKED_ENUM_OUTSIDE_AXIOMS,
    BLOCKED_FORMAT_VIOLATION,
    BLOCKED_STATE_MACHINE_VIOLATION,
    BLOCKED_FORBIDDEN_TRANSITION,
    BLOCKED_ARAZZO_OPENAPI_LINK_MISSING,
    BLOCKED_ERROR_MODEL_MISMATCH,
    BLOCKED_CROSS_SPEC_DIVERGENCE,
    BLOCKED_NON_NORMALIZED_DERIVED_DIFF_CHECK,
    BLOCKED_INVALID_MODULE_AXIOM_EXTENSION,
    BLOCKED_AXIOM_EXTENSION_COLLISION,
    BLOCKED_AXIOM_NAME_CLASH,
    BLOCKED_LAYOUT_NONCOMPLIANCE,
    BLOCKED_MISSING_MODULE_DOC,
    BLOCKED_INVALID_MODULE_DOC_HEADER,
    WARN_API_NORMATIVE_OUTSIDE_SSOT,
    BLOCKED_OWASP_CONTROL_MATRIX_MISSING,
    BLOCKED_OWASP_CONTROL_MATRIX_INVALID,
    BLOCKED_MODULE_SOURCE_AUTHORITY_MATRIX_MISSING,
    BLOCKED_MODULE_SOURCE_AUTHORITY_MATRIX_INVALID,
    BLOCKED_MODULE_REGISTRY_MISSING,
    BLOCKED_MODULE_REGISTRY_INVALID,
    BLOCKED_BOUNDARY_USERS_IDENTITY_ACCESS,
    BLOCKED_WELLNESS_MEDICAL_BOUNDARY,
    BLOCKED_SCOUT_TAXONOMY,
    BLOCKED_ASYNC_REQUIRED_MODULE,
    BLOCKED_EXTERNAL_SOURCE_AUTHORITY,
    BLOCKED_OPENAPI_ROOT_MODULE_SYNC,
    BLOCKED_PRE_CONTRACT_EVIDENCE,
    BLOCKED_SHADOW_AUTHORITY,
    BLOCKED_CANON_INTRUDER,
    BLOCKED_TOOLING_CONFIG_INVALID,
    BLOCKED_TRACEABILITY_MANIFEST_INVALID,
    BLOCKED_TRACEABILITY_INPUT_MISSING,
    BLOCKED_TRACEABILITY_HASH_MISMATCH,
    BLOCKED_AXIOM_FILE_NOT_FOUND,
    BLOCKED_INVALID_AXIOM_JSON,
    BLOCKED_AXIOM_SCHEMA_INVALID,
    BLOCKED_AXIOM_INVALID_REGEX,
    BLOCKED_AXIOM_BROKEN_INTERNAL_REFERENCE,
    BLOCKED_AXIOM_INVALID_ENUM_DEFINITION,
    BLOCKED_AXIOM_ILLEGAL_OPEN_SET_POLICY,
    BLOCKED_AXIOM_ILLEGAL_CLOSED_SET_EXTENSION_POLICY,
    BLOCKED_AXIOM_INVALID_STATE_MACHINE,
    BLOCKED_AXIOM_ORPHAN_STATE,
    BLOCKED_AXIOM_DEAD_END_STATE,
    BLOCKED_AXIOM_FORBIDDEN_TRANSITION_CONFLICT,
    BLOCKED_AXIOM_TERMINAL_STATE_WITH_OUTGOING_EDGE,
    BLOCKED_AXIOM_INVALID_DISCIPLINARY_PROGRESSION,
    BLOCKED_AXIOM_DISCIPLINARY_PRECONDITION_MISSING,
    BLOCKED_AXIOM_DISCIPLINARY_ORDER_CONFLICT,
    BLOCKED_AXIOM_INVALID_ERROR_MODEL,
    BLOCKED_AXIOM_MISSING_REQUIRED_ERROR_FIELD,
    BLOCKED_AXIOM_INVALID_CROSS_SURFACE_CONSTRAINT,
    BLOCKED_AXIOM_INVALID_NORMALIZATION_POLICY,
    BLOCKED_AXIOM_INVALID_NORMALIZATION_REGEX,
    BLOCKED_AXIOM_INVALID_VALIDATOR_CONTRACT,
    BLOCKED_AXIOM_INTEGRITY,
    BLOCKED_FEATURE_COVERAGE_MISSING,
    BLOCKED_LEGACY_IN_CRITICAL_PATH,  # FASE 7
}


def _split_code_message(s: str, default_code: str) -> tuple[str, str]:
    if s in _KNOWN_BLOCKING_CODES:
        return (s, "")
    if ":" in s:
        maybe, rest = s.split(":", 1)
        maybe = maybe.strip()
        if maybe in _KNOWN_BLOCKING_CODES:
            return (maybe, rest.strip())
    return (default_code, s)


@dataclasses.dataclass(frozen=True)
class DomainAxioms:
    meta: dict
    global_formats: dict
    global_data_invariants: dict
    error_axioms: dict
    domain_enums: dict
    state_axioms: dict
    cross_surface_constraints: dict
    normalization_policy: dict
    validator_contract: dict
    module_extension_policy: dict

    @staticmethod
    def from_dict(d: dict) -> "DomainAxioms":
        if not isinstance(d, dict):
            raise ValueError("DOMAIN_AXIOMS inválido: esperado objeto JSON em `domain_axioms`.")
        missing = [
            k
            for k in (
                "meta",
                "global_formats",
                "global_data_invariants",
                "error_axioms",
                "domain_enums",
                "state_axioms",
                "cross_surface_constraints",
                "normalization_policy",
                "validator_contract",
                "module_extension_policy",
            )
            if k not in d
        ]
        if missing:
            raise ValueError(f"DOMAIN_AXIOMS inválido: chaves ausentes: {missing}")
        for k in (
            "meta",
            "global_formats",
            "global_data_invariants",
            "error_axioms",
            "domain_enums",
            "state_axioms",
            "cross_surface_constraints",
            "normalization_policy",
            "validator_contract",
            "module_extension_policy",
        ):
            if not isinstance(d.get(k), dict):
                raise ValueError(f"DOMAIN_AXIOMS inválido: `{k}` deve ser um objeto (dict).")
        return DomainAxioms(
            meta=d["meta"],
            global_formats=d["global_formats"],
            global_data_invariants=d["global_data_invariants"],
            error_axioms=d["error_axioms"],
            domain_enums=d["domain_enums"],
            state_axioms=d["state_axioms"],
            cross_surface_constraints=d["cross_surface_constraints"],
            normalization_policy=d["normalization_policy"],
            validator_contract=d["validator_contract"],
            module_extension_policy=d["module_extension_policy"],
        )


def _repo_root() -> pathlib.Path:
    """
    Resolve a raiz do repositório.

    Este script vive em `scripts/contracts/validate/`, então não pode assumir
    `..` como repo root.
    """
    here = pathlib.Path(__file__).resolve()
    for p in here.parents:
        if (p / ".git").exists():
            return p
        if (p / "CHECKLIST.md").exists() and (p / "contracts").exists() and (p / ".contract_driven").exists():
            return p
    # Fallback: validar ainda funciona em checkout "solto"
    # quando `.git` não está presente (ex.: export).
    return here.parents[3] if len(here.parents) >= 4 else here.parent


def _is_ci_environment() -> bool:
    value = os.environ.get("CI", "").strip().lower()
    return value not in ("", "0", "false", "no", "off")


def _layout_path(root: pathlib.Path) -> pathlib.Path:
    return root / ".contract_driven" / "CONTRACT_SYSTEM_LAYOUT.md"


def _load_canonical_modules_from_layout(root: pathlib.Path) -> list[str]:
    """
    SSOT de módulos: `docs/_canon/MODULE_REGISTRY.yaml` (taxonomia autoritativa).
    Extrai os módulos canônicos do registry machine-readable.

    Formato esperado no MODULE_REGISTRY.yaml:
        modules:
          users:
            status: "draft_contract"
            ...
          training:
            status: "implementation_ready"
            ...

    Valida:
    - Exatamente 17 módulos
    - Formato lower_snake_case
    - Unicidade

    Falha explicitamente se não conseguir carregar ou validar.
    """
    registry_path = root / "docs" / "_canon" / "MODULE_REGISTRY.yaml"
    if not registry_path.exists():
        return []

    try:
        registry = _load_yaml(registry_path)
    except Exception:
        return []

    if not isinstance(registry, dict):
        return []

    modules_dict = registry.get("modules", {})
    if not isinstance(modules_dict, dict):
        return []

    modules: list[str] = []
    for module_name in modules_dict.keys():
        # Validar formato lower_snake_case
        if re.match(r"^[a-z][a-z0-9]*(?:_[a-z0-9]+)*$", module_name):
            modules.append(module_name)

    # Validar unicidade (não deveria ter duplicatas em dict keys, mas para garantir)
    if len(modules) != len(set(modules)):
        return []

    # Validar contagem exata (17 módulos canônicos desde ADR-033: video module canonicalization)
    if len(modules) != 17:
        return []

    return sorted(modules)


def _parse_yaml_front_matter(path: pathlib.Path) -> dict | None:
    """
    Espera YAML front matter no formato:
      ---
      key: value
      ---
    Retorna dict quando presente e parseável; caso contrário None.
    """
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return None
    if not text.startswith("---\n") and not text.startswith("---\r\n"):
        return None
    # Find second delimiter at line start
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    end_idx = None
    for i in range(1, min(len(lines), 80)):  # header must be short
        if lines[i].strip() == "---":
            end_idx = i
            break
    if end_idx is None:
        return None
    header = "\n".join(lines[1:end_idx]).strip() + "\n"
    try:
        import yaml  # type: ignore
        obj = yaml.safe_load(header)
    except Exception:
        return None
    return _normalize_yaml_front_matter_obj(obj) if isinstance(obj, dict) else None


def _normalize_yaml_front_matter_obj(value: Any) -> Any:
    """Converte objetos YAML para escalares JSON-friendly antes da validação."""
    if isinstance(value, dict):
        return {str(key): _normalize_yaml_front_matter_obj(val) for key, val in value.items()}
    if isinstance(value, list):
        return [_normalize_yaml_front_matter_obj(item) for item in value]
    if isinstance(value, datetime.datetime):
        return value.isoformat()
    if isinstance(value, datetime.date):
        return value.isoformat()
    return value


def _read_text(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8")


def _load_json(path: pathlib.Path) -> dict:
    return json.loads(_read_text(path))


def _load_yaml(path: pathlib.Path) -> Any:
    try:
        import yaml  # type: ignore
    except ImportError as e:  # pragma: no cover
        raise RuntimeError("PyYAML não instalado (import yaml falhou).") from e
    return yaml.safe_load(_read_text(path))


def _module_doc_header_policy_path(root: pathlib.Path) -> pathlib.Path:
    return root / ".contract_driven" / "templates" / "modulos" / "MODULE_DOC_HEADER_POLICY.yaml"


def _load_module_doc_header_policy(root: pathlib.Path) -> dict | None:
    policy_path = _module_doc_header_policy_path(root)
    if not policy_path.exists():
        return None
    try:
        policy = _load_yaml(policy_path)
    except Exception:
        return None
    return policy if isinstance(policy, dict) else None


def _infer_module_doc_type(path: pathlib.Path, module: str, policy: dict) -> str | None:
    types = policy.get("types")
    if not isinstance(types, dict):
        return None
    module_upper = module.upper()
    for doc_type, cfg in types.items():
        if not isinstance(cfg, dict):
            continue
        filenames = cfg.get("filenames") or []
        if not isinstance(filenames, list):
            continue
        for pattern in filenames:
            if not isinstance(pattern, str):
                continue
            expected_name = pattern.replace("{module_upper}", module_upper)
            if path.name == expected_name:
                return doc_type
    return None


def _module_doc_expected_target(root: pathlib.Path, module: str, field: str) -> tuple[pathlib.Path, bool] | None:
    module_upper = module.upper()
    doc_dir = root / "docs" / "hbtrack" / "modulos" / module
    mapping: dict[str, tuple[pathlib.Path, bool]] = {
        "system_scope_ref": (root / "docs" / "_canon" / "SYSTEM_SCOPE.md", False),
        "handball_rules_ref": (root / "docs" / "_canon" / "HANDBALL_RULES_DOMAIN.md", False),
        "contract_path_ref": (root / "contracts" / "openapi" / "paths" / f"{module}.yaml", False),
        "schemas_ref": (root / "contracts" / "schemas" / module, True),
        "module_scope_ref": (doc_dir / f"MODULE_SCOPE_{module_upper}.md", False),
        "domain_rules_ref": (doc_dir / f"DOMAIN_RULES_{module_upper}.md", False),
        "invariants_ref": (doc_dir / f"INVARIANTS_{module_upper}.md", False),
        "test_matrix_ref": (doc_dir / f"TEST_MATRIX_{module_upper}.md", False),
        "state_model_ref": (doc_dir / f"STATE_MODEL_{module_upper}.md", False),
        "ui_contract_ref": (doc_dir / f"UI_CONTRACT_{module_upper}.md", False),
        "screen_map_ref": (doc_dir / f"SCREEN_MAP_{module_upper}.md", False),
        "error_model_ref": (root / "docs" / "_canon" / "OPERATIONS.md", False),
        "problem_schema_ref": (root / "contracts" / "openapi" / "components" / "schemas" / "shared" / "problem.yaml", False),
        "adr_ref": (root / "docs" / "_canon" / "decisions" / "ADR-017-training-session-state-machine.md", False),
    }
    return mapping.get(field)


def load_json_file(path: str) -> dict:
    return _load_json(pathlib.Path(path))


def _violation(blocking_code: str, message: str, artifact: str, details: dict | None = None) -> dict:
    return {
        "blocking_code": blocking_code,
        "message": message,
        "artifact": artifact,
        "details": details or {},
    }


def _axiom_violation(code: str, path: str, message: str, details: dict | None = None) -> dict:
    return {
        "code": code,
        "path": path,
        "message": message,
        "severity": "error",
        "details": details or {},
    }


def validate_against_json_schema(instance: dict, schema: dict) -> list[dict]:
    try:
        import jsonschema  # type: ignore
    except Exception as e:  # pragma: no cover
        return [_axiom_violation(BLOCKED_AXIOM_SCHEMA_INVALID, "$", f"jsonschema import falhou: {e}")]

    try:
        validator = jsonschema.Draft202012Validator(schema)
        errs = sorted(validator.iter_errors(instance), key=lambda er: (list(er.path), er.message))
    except Exception as e:
        return [_axiom_violation(BLOCKED_AXIOM_SCHEMA_INVALID, "$", "Schema inválido para Draft 2020-12.", {"error": str(e)})]
    out: list[dict] = []
    for er in errs:
        p = "$"
        if er.path:
            p = "$." + ".".join([str(x) for x in er.path])
        out.append(_axiom_violation(BLOCKED_AXIOM_SCHEMA_INVALID, p, er.message, {"validator": er.validator}))
    return out


def validate_regex_compilation(axioms: dict) -> list[dict]:
    violations: list[dict] = []
    gf = axioms.get("global_formats", {})
    if not isinstance(gf, dict):
        return [_axiom_violation(BLOCKED_AXIOM_INVALID_REGEX, "$.domain_axioms.global_formats", "global_formats inválido.")]
    for k, v in sorted(gf.items(), key=lambda kv: kv[0]):
        if not isinstance(v, dict):
            continue
        pat = v.get("pattern")
        if pat is None:
            continue
        if not isinstance(pat, str) or not pat:
            violations.append(
                _axiom_violation(
                    BLOCKED_AXIOM_INVALID_REGEX,
                    f"$.domain_axioms.global_formats.{k}.pattern",
                    "pattern ausente/ inválido.",
                )
            )
            continue
        try:
            re.compile(pat)
        except re.error as e:
            violations.append(
                _axiom_violation(
                    BLOCKED_AXIOM_INVALID_REGEX,
                    f"$.domain_axioms.global_formats.{k}.pattern",
                    "pattern não compila no Python.",
                    {"error": str(e)},
                )
            )

    np = axioms.get("normalization_policy", {})
    da = np.get("derived_artifacts") if isinstance(np, dict) else None
    strip = da.get("strip_volatile_lines_matching") if isinstance(da, dict) else None
    if isinstance(strip, list):
        for idx, pat in enumerate(strip):
            if not isinstance(pat, str) or not pat:
                violations.append(
                    _axiom_violation(
                        BLOCKED_AXIOM_INVALID_NORMALIZATION_REGEX,
                        f"$.domain_axioms.normalization_policy.derived_artifacts.strip_volatile_lines_matching[{idx}]",
                        "regex vazia/ inválida.",
                    )
                )
                continue
            try:
                re.compile(pat)
            except re.error as e:
                violations.append(
                    _axiom_violation(
                        BLOCKED_AXIOM_INVALID_NORMALIZATION_REGEX,
                        f"$.domain_axioms.normalization_policy.derived_artifacts.strip_volatile_lines_matching[{idx}]",
                        "regex não compila no Python.",
                        {"error": str(e)},
                    )
                )
    return violations


def validate_internal_references(axioms: dict) -> list[dict]:
    violations: list[dict] = []
    gf = axioms.get("global_formats", {}) if isinstance(axioms.get("global_formats"), dict) else {}

    def _require_format_ref(ref: str, path: str) -> None:
        if not isinstance(ref, str) or not ref:
            violations.append(_axiom_violation(BLOCKED_AXIOM_BROKEN_INTERNAL_REFERENCE, path, "format_ref inválido."))
            return
        if ref not in gf:
            violations.append(
                _axiom_violation(
                    BLOCKED_AXIOM_BROKEN_INTERNAL_REFERENCE,
                    path,
                    f"Referenced format `{ref}` não existe em global_formats.",
                    {"missing_ref": ref},
                )
            )

    gip = axioms.get("global_identifier_policy", {})
    dei = gip.get("default_entity_id") if isinstance(gip, dict) else {}
    _require_format_ref(dei.get("format_ref"), "$.domain_axioms.global_identifier_policy.default_entity_id.format_ref")

    gdi = axioms.get("global_data_invariants", {})
    if isinstance(gdi, dict):
        for k in ("date_fields_must_use", "timestamp_fields_must_use", "public_id_fields_must_use"):
            _require_format_ref(gdi.get(k), f"$.domain_axioms.global_data_invariants.{k}")

    ea = axioms.get("error_axioms", {})
    if isinstance(ea, dict):
        for bucket in ("required_fields", "optional_fields"):
            fields = ea.get(bucket)
            if not isinstance(fields, dict):
                continue
            for field, spec in sorted(fields.items(), key=lambda kv: kv[0]):
                if not isinstance(spec, dict):
                    continue
                if "format_ref" in spec:
                    _require_format_ref(spec.get("format_ref"), f"$.domain_axioms.error_axioms.{bucket}.{field}.format_ref")

    csc = axioms.get("cross_surface_constraints", {})
    if isinstance(csc, dict):
        openapi = csc.get("openapi", {})
        if isinstance(openapi, dict):
            for k in ("date_format_ref", "timestamp_format_ref", "public_id_format_ref"):
                _require_format_ref(openapi.get(k), f"$.domain_axioms.cross_surface_constraints.openapi.{k}")
        asyncapi = csc.get("asyncapi", {})
        if isinstance(asyncapi, dict):
            _require_format_ref(asyncapi.get("public_id_format_ref"), "$.domain_axioms.cross_surface_constraints.asyncapi.public_id_format_ref")
            _require_format_ref(asyncapi.get("timestamp_format_ref"), "$.domain_axioms.cross_surface_constraints.asyncapi.timestamp_format_ref")
            enum_ref = asyncapi.get("event_type_enum_ref")
            if isinstance(enum_ref, str) and enum_ref:
                den = axioms.get("domain_enums", {})
                if not isinstance(den, dict) or enum_ref not in den:
                    violations.append(
                        _axiom_violation(
                            BLOCKED_AXIOM_BROKEN_INTERNAL_REFERENCE,
                            "$.domain_axioms.cross_surface_constraints.asyncapi.event_type_enum_ref",
                            f"Referenced enum `{enum_ref}` não existe em domain_enums.",
                            {"missing_ref": enum_ref},
                        )
                    )
            else:
                violations.append(
                    _axiom_violation(
                        BLOCKED_AXIOM_BROKEN_INTERNAL_REFERENCE,
                        "$.domain_axioms.cross_surface_constraints.asyncapi.event_type_enum_ref",
                        "event_type_enum_ref inválido.",
                    )
                )

        st_models = csc.get("state_models", {})
        if isinstance(st_models, dict):
            den = axioms.get("domain_enums", {})
            for k, v in sorted(st_models.items(), key=lambda kv: kv[0]):
                if not isinstance(v, str) or not v:
                    continue
                if not isinstance(den, dict) or v not in den:
                    violations.append(
                        _axiom_violation(
                            BLOCKED_AXIOM_BROKEN_INTERNAL_REFERENCE,
                            f"$.domain_axioms.cross_surface_constraints.state_models.{k}",
                            f"Referenced enum `{v}` não existe em domain_enums.",
                            {"missing_ref": v},
                        )
                    )

        ui = csc.get("ui_contracts", {})
        if isinstance(ui, dict):
            _require_format_ref(ui.get("date_format_ref"), "$.domain_axioms.cross_surface_constraints.ui_contracts.date_format_ref")
            _require_format_ref(ui.get("timestamp_format_ref"), "$.domain_axioms.cross_surface_constraints.ui_contracts.timestamp_format_ref")
            ref = ui.get("public_error_shape_ref")
            if ref != "Problem":
                violations.append(
                    _axiom_violation(
                        BLOCKED_AXIOM_BROKEN_INTERNAL_REFERENCE,
                        "$.domain_axioms.cross_surface_constraints.ui_contracts.public_error_shape_ref",
                        "public_error_shape_ref deve ser `Problem`.",
                        {"actual": ref},
                    )
                )

    hbc = axioms.get("handball_domain_constraints", {})
    if isinstance(hbc, dict):
        mpa = hbc.get("match_phase_alignment", {})
        if isinstance(mpa, dict):
            phase_ref = mpa.get("phase_enum_ref")
            sm_ref = mpa.get("state_machine_ref")
            den = axioms.get("domain_enums", {})
            sm = axioms.get("state_axioms", {})
            if isinstance(phase_ref, str) and phase_ref and (not isinstance(den, dict) or phase_ref not in den):
                violations.append(
                    _axiom_violation(
                        BLOCKED_AXIOM_BROKEN_INTERNAL_REFERENCE,
                        "$.domain_axioms.handball_domain_constraints.match_phase_alignment.phase_enum_ref",
                        f"Referenced enum `{phase_ref}` não existe em domain_enums.",
                        {"missing_ref": phase_ref},
                    )
                )
            if isinstance(sm_ref, str) and sm_ref and (not isinstance(sm, dict) or sm_ref not in sm):
                violations.append(
                    _axiom_violation(
                        BLOCKED_AXIOM_BROKEN_INTERNAL_REFERENCE,
                        "$.domain_axioms.handball_domain_constraints.match_phase_alignment.state_machine_ref",
                        f"Referenced state machine `{sm_ref}` não existe em state_axioms.",
                        {"missing_ref": sm_ref},
                    )
                )

    return violations


def validate_enum_integrity(axioms: dict) -> list[dict]:
    violations: list[dict] = []
    den = axioms.get("domain_enums")
    if not isinstance(den, dict):
        return [_axiom_violation(BLOCKED_AXIOM_INVALID_ENUM_DEFINITION, "$.domain_axioms.domain_enums", "domain_enums inválido.")]

    fmt = (axioms.get("global_formats") or {}).get("upper_snake_case") if isinstance(axioms.get("global_formats"), dict) else None
    upper_pat = fmt.get("pattern") if isinstance(fmt, dict) else None
    upper_re = re.compile(upper_pat) if isinstance(upper_pat, str) and upper_pat else re.compile(r"^[A-Z0-9]+(?:_[A-Z0-9]+)*$")

    for enum_name, spec in sorted(den.items(), key=lambda kv: kv[0]):
        if not isinstance(spec, dict):
            violations.append(_axiom_violation(BLOCKED_AXIOM_INVALID_ENUM_DEFINITION, f"$.domain_axioms.domain_enums.{enum_name}", "Enum spec inválido."))
            continue
        if spec.get("strict_match") is not True:
            violations.append(
                _axiom_violation(
                    BLOCKED_AXIOM_INVALID_ENUM_DEFINITION,
                    f"$.domain_axioms.domain_enums.{enum_name}.strict_match",
                    "strict_match deve ser true.",
                )
            )
        values = spec.get("values")
        if not isinstance(values, list) or not values or any((not isinstance(v, str) or not v) for v in values):
            violations.append(
                _axiom_violation(
                    BLOCKED_AXIOM_INVALID_ENUM_DEFINITION,
                    f"$.domain_axioms.domain_enums.{enum_name}.values",
                    "values inválido.",
                )
            )
            continue
        if len(set(values)) != len(values):
            violations.append(
                _axiom_violation(
                    BLOCKED_AXIOM_INVALID_ENUM_DEFINITION,
                    f"$.domain_axioms.domain_enums.{enum_name}.values",
                    "values deve ser unique.",
                )
            )
        bad = [v for v in values if not upper_re.match(v)]
        if bad:
            violations.append(
                _axiom_violation(
                    BLOCKED_AXIOM_INVALID_ENUM_DEFINITION,
                    f"$.domain_axioms.domain_enums.{enum_name}.values",
                    "Valores de enum devem obedecer UPPER_SNAKE_CASE.",
                    {"bad_values": bad},
                )
            )

        closed = spec.get("closed_set")
        if not isinstance(closed, bool):
            violations.append(
                _axiom_violation(
                    BLOCKED_AXIOM_INVALID_ENUM_DEFINITION,
                    f"$.domain_axioms.domain_enums.{enum_name}.closed_set",
                    "closed_set inválido.",
                )
            )
            continue

        policy = spec.get("module_extension_policy")
        has_policy = isinstance(policy, dict)

        if closed is False and not has_policy:
            violations.append(
                _axiom_violation(
                    BLOCKED_AXIOM_ILLEGAL_OPEN_SET_POLICY,
                    f"$.domain_axioms.domain_enums.{enum_name}.module_extension_policy",
                    "Enums com closed_set=false devem declarar module_extension_policy.",
                )
            )
        if closed is True and has_policy and enum_name != "event_type":
            violations.append(
                _axiom_violation(
                    BLOCKED_AXIOM_ILLEGAL_CLOSED_SET_EXTENSION_POLICY,
                    f"$.domain_axioms.domain_enums.{enum_name}.module_extension_policy",
                    "Enums com closed_set=true não podem declarar module_extension_policy (exceto event_type).",
                )
            )

        if has_policy:
            if policy.get("merge_strategy") != "union_with_collision_block":
                violations.append(
                    _axiom_violation(
                        BLOCKED_AXIOM_INVALID_ENUM_DEFINITION,
                        f"$.domain_axioms.domain_enums.{enum_name}.module_extension_policy.merge_strategy",
                        "merge_strategy deve ser union_with_collision_block.",
                    )
                )
            if policy.get("require_upper_snake_case") is not True:
                violations.append(
                    _axiom_violation(
                        BLOCKED_AXIOM_INVALID_ENUM_DEFINITION,
                        f"$.domain_axioms.domain_enums.{enum_name}.module_extension_policy.require_upper_snake_case",
                        "require_upper_snake_case deve ser true.",
                    )
                )

    # Regra específica: event_type deve ser closed_set=true para permitir DELTA_ONLY por axiomas modulares.
    ev = den.get("event_type")
    if isinstance(ev, dict) and ev.get("closed_set") is not True:
        violations.append(
            _axiom_violation(
                BLOCKED_AXIOM_INVALID_ENUM_DEFINITION,
                "$.domain_axioms.domain_enums.event_type.closed_set",
                "event_type deve ser closed_set=true.",
            )
        )

    return violations


def validate_state_machine_integrity(axioms: dict) -> list[dict]:
    violations: list[dict] = []
    sm_all = axioms.get("state_axioms")
    if not isinstance(sm_all, dict):
        return [_axiom_violation(BLOCKED_AXIOM_INVALID_STATE_MACHINE, "$.domain_axioms.state_axioms", "state_axioms inválido.")]

    for sm_name, sm in sorted(sm_all.items(), key=lambda kv: kv[0]):
        base_path = f"$.domain_axioms.state_axioms.{sm_name}"
        if not isinstance(sm, dict):
            violations.append(_axiom_violation(BLOCKED_AXIOM_INVALID_STATE_MACHINE, base_path, "State machine inválida."))
            continue
        allowed = sm.get("allowed_transitions")
        forbidden = sm.get("forbidden_transitions")
        initial = sm.get("initial_states")
        terminal = sm.get("terminal_states")
        if not isinstance(allowed, dict) or not isinstance(forbidden, list) or not isinstance(initial, list) or not isinstance(terminal, list):
            violations.append(_axiom_violation(BLOCKED_AXIOM_INVALID_STATE_MACHINE, base_path, "Estrutura inválida (allowed/forbidden/initial/terminal)."))
            continue

        states: set[str] = set()
        for src, dsts in allowed.items():
            if isinstance(src, str) and src:
                states.add(src)
            if isinstance(dsts, list):
                for d in dsts:
                    if isinstance(d, str) and d:
                        states.add(d)

        for st in initial:
            if isinstance(st, str) and st not in states:
                violations.append(_axiom_violation(BLOCKED_AXIOM_INVALID_STATE_MACHINE, f"{base_path}.initial_states", "Estado inicial não existe no grafo.", {"state": st}))
        for st in terminal:
            if isinstance(st, str) and st not in states:
                violations.append(_axiom_violation(BLOCKED_AXIOM_INVALID_STATE_MACHINE, f"{base_path}.terminal_states", "Estado terminal não existe no grafo.", {"state": st}))

        # forbidden cannot intersect allowed
        forbidden_edges: set[tuple[str, str]] = set()
        for idx, pair in enumerate(forbidden):
            if not (isinstance(pair, list) and len(pair) == 2 and isinstance(pair[0], str) and isinstance(pair[1], str)):
                violations.append(_axiom_violation(BLOCKED_AXIOM_INVALID_STATE_MACHINE, f"{base_path}.forbidden_transitions[{idx}]", "Par de transição inválido."))
                continue
            forbidden_edges.add((pair[0], pair[1]))

        for src, dsts in allowed.items():
            if not isinstance(src, str) or not isinstance(dsts, list):
                continue
            for dst in dsts:
                if not isinstance(dst, str):
                    continue
                if (src, dst) in forbidden_edges:
                    violations.append(
                        _axiom_violation(
                            BLOCKED_AXIOM_FORBIDDEN_TRANSITION_CONFLICT,
                            f"{base_path}.forbidden_transitions",
                            "Transição proibida também está em allowed_transitions.",
                            {"from": src, "to": dst},
                        )
                    )

        # Reachability
        adj: dict[str, list[str]] = {}
        for src, dsts in allowed.items():
            if isinstance(src, str) and isinstance(dsts, list):
                adj[src] = [d for d in dsts if isinstance(d, str)]

        stack = [s for s in initial if isinstance(s, str)]
        reachable: set[str] = set()
        while stack:
            s = stack.pop()
            if s in reachable:
                continue
            reachable.add(s)
            for nxt in adj.get(s, []):
                if nxt not in reachable:
                    stack.append(nxt)

        for st in sorted(states):
            if st not in reachable:
                violations.append(_axiom_violation(BLOCKED_AXIOM_ORPHAN_STATE, base_path, "Estado inalcançável a partir de initial_states.", {"state": st}))

        for st in sorted(states):
            outgoing = adj.get(st, [])
            if st in terminal and outgoing:
                violations.append(
                    _axiom_violation(
                        BLOCKED_AXIOM_TERMINAL_STATE_WITH_OUTGOING_EDGE,
                        base_path,
                        "Estado terminal não pode ter saída.",
                        {"state": st, "outgoing": outgoing},
                    )
                )
            if st not in terminal and not outgoing:
                violations.append(
                    _axiom_violation(
                        BLOCKED_AXIOM_DEAD_END_STATE,
                        base_path,
                        "Estado não-terminal sem saída.",
                        {"state": st},
                    )
                )

    return violations


def validate_disciplinary_progression_integrity(axioms: dict) -> list[dict]:
    hbc = axioms.get("handball_domain_constraints", {})
    dp = hbc.get("disciplinary_progression") if isinstance(hbc, dict) else None
    if not isinstance(dp, dict):
        return [_axiom_violation(BLOCKED_AXIOM_INVALID_DISCIPLINARY_PROGRESSION, "$.domain_axioms.handball_domain_constraints.disciplinary_progression", "disciplinary_progression inválido.")]

    ordered = dp.get("ordered_levels")
    allowed = dp.get("allowed_transitions")
    pre = dp.get("preconditions")
    if not isinstance(ordered, list) or not ordered or any((not isinstance(x, str) or not x) for x in ordered):
        return [_axiom_violation(BLOCKED_AXIOM_INVALID_DISCIPLINARY_PROGRESSION, "$.domain_axioms.handball_domain_constraints.disciplinary_progression.ordered_levels", "ordered_levels inválido.")]
    if len(set(ordered)) != len(ordered):
        return [_axiom_violation(BLOCKED_AXIOM_INVALID_DISCIPLINARY_PROGRESSION, "$.domain_axioms.handball_domain_constraints.disciplinary_progression.ordered_levels", "ordered_levels contém duplicatas.")]
    if not isinstance(allowed, dict):
        return [_axiom_violation(BLOCKED_AXIOM_INVALID_DISCIPLINARY_PROGRESSION, "$.domain_axioms.handball_domain_constraints.disciplinary_progression.allowed_transitions", "allowed_transitions inválido.")]
    if not isinstance(pre, dict):
        return [_axiom_violation(BLOCKED_AXIOM_INVALID_DISCIPLINARY_PROGRESSION, "$.domain_axioms.handball_domain_constraints.disciplinary_progression.preconditions", "preconditions inválido.")]

    idx = {v: i for i, v in enumerate(ordered)}
    violations: list[dict] = []
    for src, dsts in allowed.items():
        if src not in idx:
            violations.append(_axiom_violation(BLOCKED_AXIOM_INVALID_DISCIPLINARY_PROGRESSION, "$.domain_axioms.handball_domain_constraints.disciplinary_progression.allowed_transitions", "Origem inválida.", {"from": src}))
            continue
        if not isinstance(dsts, list):
            violations.append(_axiom_violation(BLOCKED_AXIOM_INVALID_DISCIPLINARY_PROGRESSION, "$.domain_axioms.handball_domain_constraints.disciplinary_progression.allowed_transitions", "Destinos inválidos.", {"from": src}))
            continue
        for dst in dsts:
            if dst not in idx:
                violations.append(_axiom_violation(BLOCKED_AXIOM_INVALID_DISCIPLINARY_PROGRESSION, "$.domain_axioms.handball_domain_constraints.disciplinary_progression.allowed_transitions", "Destino inválido.", {"from": src, "to": dst}))
                continue
            if idx[dst] <= idx[src]:
                violations.append(_axiom_violation(BLOCKED_AXIOM_DISCIPLINARY_ORDER_CONFLICT, "$.domain_axioms.handball_domain_constraints.disciplinary_progression.allowed_transitions", "Transição contradiz ordem.", {"from": src, "to": dst}))

    blue = pre.get("BLUE_CARD")
    if not isinstance(blue, dict) or "requires_prior" not in blue or not isinstance(blue.get("requires_prior"), list):
        violations.append(_axiom_violation(BLOCKED_AXIOM_DISCIPLINARY_PRECONDITION_MISSING, "$.domain_axioms.handball_domain_constraints.disciplinary_progression.preconditions.BLUE_CARD", "BLUE_CARD.requires_prior ausente/ inválido."))
    else:
        if "RED_CARD" not in blue.get("requires_prior"):
            violations.append(_axiom_violation(BLOCKED_AXIOM_DISCIPLINARY_PRECONDITION_MISSING, "$.domain_axioms.handball_domain_constraints.disciplinary_progression.preconditions.BLUE_CARD.requires_prior", "BLUE_CARD deve requerer RED_CARD.", {"requires_prior": blue.get("requires_prior")}))

    return violations


def validate_error_axiom_integrity(axioms: dict) -> list[dict]:
    ea = axioms.get("error_axioms")
    if not isinstance(ea, dict):
        return [_axiom_violation(BLOCKED_AXIOM_INVALID_ERROR_MODEL, "$.domain_axioms.error_axioms", "error_axioms inválido.")]

    pes = ea.get("public_error_shape", {})
    if not isinstance(pes, dict):
        return [_axiom_violation(BLOCKED_AXIOM_INVALID_ERROR_MODEL, "$.domain_axioms.error_axioms.public_error_shape", "public_error_shape inválido.")]
    if pes.get("schema_name") != "Problem":
        return [_axiom_violation(BLOCKED_AXIOM_INVALID_ERROR_MODEL, "$.domain_axioms.error_axioms.public_error_shape.schema_name", "schema_name deve ser Problem.", {"actual": pes.get("schema_name")})]
    if pes.get("content_type") != "application/problem+json":
        return [_axiom_violation(BLOCKED_AXIOM_INVALID_ERROR_MODEL, "$.domain_axioms.error_axioms.public_error_shape.content_type", "content_type inválido.", {"actual": pes.get("content_type")})]

    required = ea.get("required_fields")
    if not isinstance(required, dict):
        return [_axiom_violation(BLOCKED_AXIOM_INVALID_ERROR_MODEL, "$.domain_axioms.error_axioms.required_fields", "required_fields inválido.")]
    for must in ("type", "title", "status", "traceId"):
        if must not in required:
            return [_axiom_violation(BLOCKED_AXIOM_MISSING_REQUIRED_ERROR_FIELD, "$.domain_axioms.error_axioms.required_fields", f"Campo requerido ausente: {must}.")]

    fb = ea.get("forbidden_behaviors")
    if not isinstance(fb, list) or not fb:
        return [_axiom_violation(BLOCKED_AXIOM_INVALID_ERROR_MODEL, "$.domain_axioms.error_axioms.forbidden_behaviors", "forbidden_behaviors não pode ser vazio.")]

    # status must reference integer http status code
    status = required.get("status")
    if not isinstance(status, dict) or status.get("format_ref") != "http_status_code":
        return [_axiom_violation(BLOCKED_AXIOM_INVALID_ERROR_MODEL, "$.domain_axioms.error_axioms.required_fields.status.format_ref", "status.format_ref deve ser http_status_code.")]

    trace = required.get("traceId")
    if not isinstance(trace, dict) or trace.get("format_ref") != "trace_id":
        return [_axiom_violation(BLOCKED_AXIOM_INVALID_ERROR_MODEL, "$.domain_axioms.error_axioms.required_fields.traceId.format_ref", "traceId.format_ref deve ser trace_id.")]
    return []


def validate_cross_surface_integrity(axioms: dict) -> list[dict]:
    csc = axioms.get("cross_surface_constraints")
    if not isinstance(csc, dict):
        return [_axiom_violation(BLOCKED_AXIOM_INVALID_CROSS_SURFACE_CONSTRAINT, "$.domain_axioms.cross_surface_constraints", "cross_surface_constraints inválido.")]
    openapi = csc.get("openapi")
    if not isinstance(openapi, dict):
        return [_axiom_violation(BLOCKED_AXIOM_INVALID_CROSS_SURFACE_CONSTRAINT, "$.domain_axioms.cross_surface_constraints.openapi", "openapi constraints inválido.")]
    if openapi.get("error_schema_name") != "Problem":
        return [_axiom_violation(BLOCKED_AXIOM_INVALID_CROSS_SURFACE_CONSTRAINT, "$.domain_axioms.cross_surface_constraints.openapi.error_schema_name", "error_schema_name deve ser Problem.")]
    if openapi.get("error_content_type") != "application/problem+json":
        return [_axiom_violation(BLOCKED_AXIOM_INVALID_CROSS_SURFACE_CONSTRAINT, "$.domain_axioms.cross_surface_constraints.openapi.error_content_type", "error_content_type inválido.")]

    asyncapi = csc.get("asyncapi")
    if not isinstance(asyncapi, dict):
        return [_axiom_violation(BLOCKED_AXIOM_INVALID_CROSS_SURFACE_CONSTRAINT, "$.domain_axioms.cross_surface_constraints.asyncapi", "asyncapi constraints inválido.")]
    if asyncapi.get("event_type_enum_ref") != "event_type":
        return [_axiom_violation(BLOCKED_AXIOM_INVALID_CROSS_SURFACE_CONSTRAINT, "$.domain_axioms.cross_surface_constraints.asyncapi.event_type_enum_ref", "event_type_enum_ref deve ser event_type.")]

    ui = csc.get("ui_contracts")
    if not isinstance(ui, dict) or ui.get("public_error_shape_ref") != "Problem":
        return [_axiom_violation(BLOCKED_AXIOM_INVALID_CROSS_SURFACE_CONSTRAINT, "$.domain_axioms.cross_surface_constraints.ui_contracts.public_error_shape_ref", "public_error_shape_ref deve ser Problem.")]
    return []


def validate_normalization_policy_integrity(axioms: dict) -> list[dict]:
    np = axioms.get("normalization_policy")
    da = np.get("derived_artifacts") if isinstance(np, dict) else None
    if not isinstance(da, dict):
        return [_axiom_violation(BLOCKED_AXIOM_INVALID_NORMALIZATION_POLICY, "$.domain_axioms.normalization_policy.derived_artifacts", "derived_artifacts inválido.")]
    req = ("strip_volatile_lines_matching", "normalize_line_endings_to", "trim_trailing_whitespace", "ensure_final_newline")
    missing = [k for k in req if k not in da]
    if missing:
        return [_axiom_violation(BLOCKED_AXIOM_INVALID_NORMALIZATION_POLICY, "$.domain_axioms.normalization_policy.derived_artifacts", "Campos obrigatórios ausentes.", {"missing": missing})]
    if da.get("normalize_line_endings_to") != "LF":
        return [_axiom_violation(BLOCKED_AXIOM_INVALID_NORMALIZATION_POLICY, "$.domain_axioms.normalization_policy.derived_artifacts.normalize_line_endings_to", "normalize_line_endings_to deve ser LF.")]
    return []


def validate_validator_contract_integrity(axioms: dict) -> list[dict]:
    vc = axioms.get("validator_contract")
    if not isinstance(vc, dict):
        return [_axiom_violation(BLOCKED_AXIOM_INVALID_VALIDATOR_CONTRACT, "$.domain_axioms.validator_contract", "validator_contract inválido.")]

    required_checks = vc.get("required_checks")
    forbidden = vc.get("forbidden_validator_behaviors")
    if not isinstance(required_checks, list) or not all(isinstance(x, str) and x for x in required_checks):
        return [_axiom_violation(BLOCKED_AXIOM_INVALID_VALIDATOR_CONTRACT, "$.domain_axioms.validator_contract.required_checks", "required_checks inválido.")]
    if not isinstance(forbidden, list) or not all(isinstance(x, str) and x for x in forbidden):
        return [_axiom_violation(BLOCKED_AXIOM_INVALID_VALIDATOR_CONTRACT, "$.domain_axioms.validator_contract.forbidden_validator_behaviors", "forbidden_validator_behaviors inválido.")]

    must_checks = {
        "validate_global_formats_by_regex",
        "validate_enums_against_closed_sets",
        "validate_state_transitions_against_axioms",
        "validate_error_shape_required_fields",
        "validate_cross_surface_alignment",
        "normalize_derived_outputs_before_diff",
    }
    missing = sorted([c for c in must_checks if c not in set(required_checks)])
    if missing:
        return [_axiom_violation(BLOCKED_AXIOM_INVALID_VALIDATOR_CONTRACT, "$.domain_axioms.validator_contract.required_checks", "required_checks não contém todos os checks obrigatórios.", {"missing": missing})]

    must_forbidden = {
        "llm_interpretation_for_semantic_validity",
        "implicit_enum_extension",
        "silent_format_coercion",
        "non_normalized_derived_diff_comparison",
    }
    missing_f = sorted([c for c in must_forbidden if c not in set(forbidden)])
    if missing_f:
        return [_axiom_violation(BLOCKED_AXIOM_INVALID_VALIDATOR_CONTRACT, "$.domain_axioms.validator_contract.forbidden_validator_behaviors", "forbidden_validator_behaviors incompleto.", {"missing": missing_f})]
    return []


def validate_axiom_integrity(axioms_path: str, schema_path: str) -> dict:
    start = time.monotonic()
    result: dict = {
        "gate_id": "AXIOM_INTEGRITY_GATE",
        "status": "FAIL",
        "blocking": True,
        "blocking_code": BLOCKED_AXIOM_INTEGRITY,
        "checked_artifact": axioms_path,
        "violations": [],
        "metrics": {"violations": 0, "checks_executed": 0, "duration_ms": 0},
    }

    def _finish() -> dict:
        result["metrics"]["violations"] = len(result["violations"])
        result["metrics"]["duration_ms"] = int((time.monotonic() - start) * 1000)
        if not result["violations"]:
            result["status"] = "PASS"
            result["blocking_code"] = None
        return result

    axioms_file = pathlib.Path(axioms_path)
    if not axioms_file.exists():
        result["violations"].append(_axiom_violation(BLOCKED_AXIOM_FILE_NOT_FOUND, "$", "Arquivo de axiomas não encontrado.", {"path": axioms_path}))
        result["metrics"]["checks_executed"] = 1
        return _finish()

    try:
        raw = axioms_file.read_text(encoding="utf-8")
        data = json.loads(raw)
    except Exception as e:
        result["violations"].append(_axiom_violation(BLOCKED_INVALID_AXIOM_JSON, "$", "JSON inválido.", {"error": str(e)}))
        result["metrics"]["checks_executed"] = 1
        return _finish()

    axioms = data.get("domain_axioms") if isinstance(data, dict) else None
    if not isinstance(axioms, dict):
        result["violations"].append(_axiom_violation(BLOCKED_INVALID_AXIOM_JSON, "$.domain_axioms", "Raiz domain_axioms ausente/ inválida."))
        result["metrics"]["checks_executed"] = 1
        return _finish()

    # Etapa 2 — Schema validation
    try:
        schema = load_json_file(schema_path)
    except Exception as e:
        result["violations"].append(_axiom_violation(BLOCKED_AXIOM_SCHEMA_INVALID, "$", "Schema não encontrado/ inválido.", {"error": str(e), "schema_path": schema_path}))
        result["metrics"]["checks_executed"] = 2
        return _finish()

    result["metrics"]["checks_executed"] = 2
    result["violations"].extend(validate_against_json_schema(data, schema))
    if result["violations"]:
        # Continua para coletar o máximo de evidência sem “interpretar”.
        pass

    # Etapa 3 — Regex compilation
    result["metrics"]["checks_executed"] = 3
    result["violations"].extend(validate_regex_compilation(axioms))

    # Etapa 4 — Internal refs
    result["metrics"]["checks_executed"] = 4
    result["violations"].extend(validate_internal_references(axioms))

    # Etapa 5 — Enums
    result["metrics"]["checks_executed"] = 5
    result["violations"].extend(validate_enum_integrity(axioms))

    # Etapa 6 — FSMs
    result["metrics"]["checks_executed"] = 6
    result["violations"].extend(validate_state_machine_integrity(axioms))

    # Etapa 7 — disciplinary progression
    result["metrics"]["checks_executed"] = 7
    result["violations"].extend(validate_disciplinary_progression_integrity(axioms))

    # Etapa 8 — Error model axioms
    result["metrics"]["checks_executed"] = 8
    result["violations"].extend(validate_error_axiom_integrity(axioms))

    # Etapa 9 — Cross-surface
    result["metrics"]["checks_executed"] = 9
    result["violations"].extend(validate_cross_surface_integrity(axioms))

    # Etapa 10 — Normalization policy
    result["metrics"]["checks_executed"] = 10
    result["violations"].extend(validate_normalization_policy_integrity(axioms))

    # Etapa 11 — Validator contract
    result["metrics"]["checks_executed"] = 11
    result["violations"].extend(validate_validator_contract_integrity(axioms))

    # FSM_COMPLETENESS: todo estado não-terminal deve ter ao menos uma transição de saída.
    for sm_name, sm_def in (axioms.get("state_axioms") or {}).items():
        if not isinstance(sm_def, dict):
            continue
        allowed = sm_def.get("allowed_transitions") or {}
        terminal_states = set(sm_def.get("terminal_states") or [])
        states: set[str] = set()
        states_with_exit: set[str] = set()
        for source, destinations in allowed.items():
            if not isinstance(source, str) or not source:
                continue
            states.add(source)
            if isinstance(destinations, list) and any(isinstance(dst, str) and dst for dst in destinations):
                states_with_exit.add(source)
            if isinstance(destinations, list):
                for destination in destinations:
                    if isinstance(destination, str) and destination:
                        states.add(destination)
        for state in sorted(states):
            if state in terminal_states:
                continue
            if state not in states_with_exit:
                result["violations"].append(
                    {
                        "blocking_code": "BLOCKED_AXIOM_VIOLATION",
                        "path": f"state_axioms.{sm_name}.allowed_transitions.{state}",
                        "message": (
                            f"Estado '{state}' sem transições de saída declaradas e "
                            "não está em terminal_states. Declare transições ou adicione a terminal_states."
                        ),
                        "severity": "warn",
                    }
                )

    return _finish()


def load_domain_axioms(path: str) -> dict:
    """Carrega `.contract_driven/DOMAIN_AXIOMS.json` e retorna `domain_axioms` (dict)."""
    data = _load_json(pathlib.Path(path))
    if "domain_axioms" not in data:
        raise ValueError("DOMAIN_AXIOMS.json inválido: chave raiz `domain_axioms` ausente.")
    axioms = data["domain_axioms"]
    _ = DomainAxioms.from_dict(axioms)
    return axioms


def load_module_axioms(module_name: str) -> dict | None:
    """
    Carrega `docs/hbtrack/modulos/<module>/DOMAIN_AXIOMS_<MODULE>.json` se existir.

    Retorna o dict `domain_axioms_module` ou None quando ausente.
    """
    root = _repo_root()
    module_dir = root / "docs" / "hbtrack" / "modulos" / module_name
    module_token = module_name.upper()
    path = module_dir / f"DOMAIN_AXIOMS_{module_token}.json"
    if not path.exists():
        return None
    try:
        data = _load_json(path)
    except Exception as e:
        raise ValueError(f"{BLOCKED_INVALID_MODULE_AXIOM_EXTENSION}: JSON inválido: {e}") from e
    if not isinstance(data, dict) or "domain_axioms_module" not in data:
        raise ValueError(f"{BLOCKED_INVALID_MODULE_AXIOM_EXTENSION}: raiz `domain_axioms_module` ausente: {path}")

    mod = data["domain_axioms_module"]
    if not isinstance(mod, dict):
        raise ValueError(f"{BLOCKED_INVALID_MODULE_AXIOM_EXTENSION}: `domain_axioms_module` deve ser objeto: {path}")

    allowed_top = {"meta", "module", "delta_only", "local_invariants_may_only_restrict", "local_invariants", "domain_enums"}
    extra_top = sorted([k for k in mod.keys() if k not in allowed_top])
    required_top = {"meta", "module", "delta_only", "local_invariants_may_only_restrict", "domain_enums"}
    missing_top = sorted([k for k in required_top if k not in mod])
    if missing_top or extra_top:
        raise ValueError(
            f"{BLOCKED_INVALID_MODULE_AXIOM_EXTENSION}: chaves inválidas em domain_axioms_module: missing={missing_top} extra={extra_top}"
        )

    meta = mod.get("meta")
    if not isinstance(meta, dict):
        raise ValueError(f"{BLOCKED_INVALID_MODULE_AXIOM_EXTENSION}: `meta` deve ser objeto.")
    if meta.get("artifact_id") != "DOMAIN_AXIOMS_MODULE":
        raise ValueError(f"{BLOCKED_INVALID_MODULE_AXIOM_EXTENSION}: meta.artifact_id deve ser DOMAIN_AXIOMS_MODULE.")
    if not isinstance(meta.get("version"), str) or not meta.get("version"):
        raise ValueError(f"{BLOCKED_INVALID_MODULE_AXIOM_EXTENSION}: meta.version deve ser string não vazia.")
    if meta.get("status") not in ("ACTIVE", "DRAFT", "DEPRECATED"):
        raise ValueError(f"{BLOCKED_INVALID_MODULE_AXIOM_EXTENSION}: meta.status inválido.")

    declared_module = mod.get("module")
    if declared_module != module_name:
        raise ValueError(
            f"{BLOCKED_INVALID_MODULE_AXIOM_EXTENSION}: module deve ser `{module_name}` (recebido: {declared_module!r})."
        )

    if mod.get("delta_only") is not True:
        raise ValueError(f"{BLOCKED_INVALID_MODULE_AXIOM_EXTENSION}: delta_only deve ser true.")
    if mod.get("local_invariants_may_only_restrict") is not True:
        raise ValueError(f"{BLOCKED_INVALID_MODULE_AXIOM_EXTENSION}: local_invariants_may_only_restrict deve ser true.")
    if "local_invariants" in mod and mod.get("local_invariants") is not None and not isinstance(mod.get("local_invariants"), dict):
        raise ValueError(f"{BLOCKED_INVALID_MODULE_AXIOM_EXTENSION}: local_invariants deve ser objeto quando presente.")

    domain_enums = mod.get("domain_enums")
    if not isinstance(domain_enums, dict):
        raise ValueError(f"{BLOCKED_INVALID_MODULE_AXIOM_EXTENSION}: domain_enums deve ser objeto.")
    for enum_name, ext in domain_enums.items():
        if not isinstance(enum_name, str) or not enum_name:
            raise ValueError(f"{BLOCKED_INVALID_MODULE_AXIOM_EXTENSION}: nome de enum inválido.")
        if not isinstance(ext, dict):
            raise ValueError(f"{BLOCKED_INVALID_MODULE_AXIOM_EXTENSION}: extensão de enum inválida ({enum_name}).")
        if set(ext.keys()) != {"values"}:
            raise ValueError(f"{BLOCKED_INVALID_MODULE_AXIOM_EXTENSION}: extensão deve conter apenas `values` ({enum_name}).")
        values = ext.get("values")
        if not isinstance(values, list) or not values:
            raise ValueError(f"{BLOCKED_INVALID_MODULE_AXIOM_EXTENSION}: values inválido ({enum_name}).")

        if enum_name == "event_type":
            # Para `event_type`, cada valor de extensão deve ser um objeto com semântica verificável.
            names: list[str] = []
            for v in values:
                if not isinstance(v, dict):
                    raise ValueError(f"{BLOCKED_INVALID_MODULE_AXIOM_EXTENSION}: event_type.values deve conter objetos ({enum_name}).")
                allowed_value_keys = {"name", "semantic_id", "description", "payload_constraints"}
                if set(v.keys()) != allowed_value_keys:
                    raise ValueError(f"{BLOCKED_INVALID_MODULE_AXIOM_EXTENSION}: chaves inválidas em event_type value.")
                if not isinstance(v.get("name"), str) or not v["name"]:
                    raise ValueError(f"{BLOCKED_INVALID_MODULE_AXIOM_EXTENSION}: event_type.name inválido.")
                if not isinstance(v.get("semantic_id"), str) or not v["semantic_id"]:
                    raise ValueError(f"{BLOCKED_INVALID_MODULE_AXIOM_EXTENSION}: event_type.semantic_id inválido.")
                if not isinstance(v.get("description"), str) or not v["description"]:
                    raise ValueError(f"{BLOCKED_INVALID_MODULE_AXIOM_EXTENSION}: event_type.description inválido.")
                pc = v.get("payload_constraints")
                if not isinstance(pc, dict) or set(pc.keys()) != {"required_fields", "field_formats"}:
                    raise ValueError(f"{BLOCKED_INVALID_MODULE_AXIOM_EXTENSION}: payload_constraints inválido.")
                req = pc.get("required_fields")
                if not isinstance(req, list) or any((not isinstance(x, str) or not x) for x in req):
                    raise ValueError(f"{BLOCKED_INVALID_MODULE_AXIOM_EXTENSION}: payload_constraints.required_fields inválido.")
                if len(set(req)) != len(req):
                    raise ValueError(f"{BLOCKED_INVALID_MODULE_AXIOM_EXTENSION}: required_fields deve ser uniqueItems.")
                ff = pc.get("field_formats")
                if not isinstance(ff, dict) or any((not isinstance(k, str) or not k or not isinstance(val, str) or not val) for k, val in ff.items()):
                    raise ValueError(f"{BLOCKED_INVALID_MODULE_AXIOM_EXTENSION}: payload_constraints.field_formats inválido.")
                names.append(v["name"])
            if len(set(names)) != len(names):
                raise ValueError(f"{BLOCKED_INVALID_MODULE_AXIOM_EXTENSION}: event_type.values deve ter `name` único por módulo.")
        else:
            if any((not isinstance(v, str) or not v) for v in values):
                raise ValueError(f"{BLOCKED_INVALID_MODULE_AXIOM_EXTENSION}: values inválido ({enum_name}).")
            if len(set(values)) != len(values):
                raise ValueError(f"{BLOCKED_INVALID_MODULE_AXIOM_EXTENSION}: values deve ser uniqueItems ({enum_name}).")

    return mod


def merge_enum_extensions(global_axioms: dict, module_axioms: dict | None) -> dict:
    """
    Retorna o mapa de enums efetivo após aplicar extensões modulares, se permitido.

    Regras obrigatórias:
    - só aceitar extensão modular quando allow_module_extensions=true
    - só aceitar quando o arquivo existir no path canônico
    - rejeitar colisões com o conjunto global
    """
    effective = json.loads(json.dumps(global_axioms["domain_enums"]))  # deep copy determinístico
    if module_axioms is None:
        return effective

    policy = global_axioms.get("module_extension_policy", {})
    global_allow = bool(policy.get("allow_module_extensions", False))

    extensions = module_axioms.get("domain_enums", {})
    if not isinstance(extensions, dict):
        raise ValueError(BLOCKED_INVALID_MODULE_AXIOM_EXTENSION)

    upper_snake_pat = None
    if isinstance(global_axioms.get("global_formats"), dict):
        fmt = global_axioms["global_formats"].get("upper_snake_case")
        if isinstance(fmt, dict) and isinstance(fmt.get("pattern"), str):
            upper_snake_pat = re.compile(fmt["pattern"])
    if upper_snake_pat is None:
        upper_snake_pat = re.compile(r"^[A-Z0-9]+(?:_[A-Z0-9]+)*$")

    for enum_name, ext in extensions.items():
        if enum_name not in effective:
            raise ValueError(BLOCKED_INVALID_MODULE_AXIOM_EXTENSION)

        global_enum = effective[enum_name]
        if not isinstance(global_enum, dict):
            raise ValueError(BLOCKED_INVALID_MODULE_AXIOM_EXTENSION)

        enum_policy = global_enum.get("module_extension_policy") if isinstance(global_enum.get("module_extension_policy"), dict) else {}
        enum_allow = bool(enum_policy.get("allow_module_extensions", False)) if isinstance(enum_policy, dict) else False
        allow = enum_allow or (global_allow and global_enum.get("closed_set", False) is not True)
        if not allow:
            raise ValueError(BLOCKED_INVALID_MODULE_AXIOM_EXTENSION)

        merge_strategy = enum_policy.get("merge_strategy")
        if merge_strategy is not None and merge_strategy != "union_with_collision_block":
            raise ValueError(BLOCKED_INVALID_MODULE_AXIOM_EXTENSION)
        require_upper = bool(enum_policy.get("require_upper_snake_case", False)) if isinstance(enum_policy, dict) else False

        ext_values = ext.get("values", [])
        if not isinstance(ext_values, list) or not ext_values:
            raise ValueError(BLOCKED_INVALID_MODULE_AXIOM_EXTENSION)

        global_values = list(global_enum.get("values", []))
        global_set = set(global_values)
        for v in ext_values:
            name = None
            if isinstance(v, str):
                name = v
            elif isinstance(v, dict) and isinstance(v.get("name"), str):
                name = v["name"]
            if not isinstance(name, str) or not name:
                raise ValueError(BLOCKED_INVALID_MODULE_AXIOM_EXTENSION)

            if require_upper and not upper_snake_pat.match(name):
                raise ValueError(BLOCKED_INVALID_MODULE_AXIOM_EXTENSION)

            if name in global_set:
                raise ValueError(BLOCKED_AXIOM_EXTENSION_COLLISION)
            global_values.append(name)
            global_set.add(name)

        global_enum["values"] = global_values
        effective[enum_name] = global_enum

    return effective


def _walk(obj: Any, *, path: tuple[str, ...] = ()) -> list[tuple[tuple[str, ...], Any]]:
    """Retorna uma lista estável de (path, node) para nós dict/list (DFS determinístico)."""
    out: list[tuple[tuple[str, ...], Any]] = []
    if isinstance(obj, dict):
        out.append((path, obj))
        for k in sorted(obj.keys(), key=lambda x: str(x)):
            out.extend(_walk(obj[k], path=path + (str(k),)))
    elif isinstance(obj, list):
        out.append((path, obj))
        for idx, item in enumerate(obj):
            out.extend(_walk(item, path=path + (str(idx),)))
    return out


def validate_global_formats_by_regex(artifacts: list[str], axioms: dict) -> list[dict]:
    """
    Falha se qualquer campo mapeado como data, timestamp, uuid, trace_id ou request_id violar regex canônica.

    Mapeamento determinístico (sem interpretação livre):
    - uuid: propriedade `id` ou sufixo `Id`
    - date: sufixo `Date`
    - timestamp: sufixo `At`
    - trace id: `traceId`
    - request id: `requestId`
    """
    violations: list[dict] = []
    domain = DomainAxioms.from_dict(axioms)

    def _pattern(format_key: str) -> str:
        fmt = domain.global_formats.get(format_key, {})
        p = fmt.get("pattern")
        if not isinstance(p, str) or not p:
            raise ValueError(f"global_formats.{format_key}.pattern ausente/ inválido")
        return p

    uuid_ref = domain.global_data_invariants.get("public_id_fields_must_use", "uuid_v4")
    date_ref = domain.global_data_invariants.get("date_fields_must_use", "date_only")
    ts_ref = domain.global_data_invariants.get("timestamp_fields_must_use", "timestamp_utc")

    def _pattern_by_ref(format_ref: str) -> str:
        return _pattern(format_ref)

    uuid_pat = _pattern_by_ref(str(uuid_ref))
    date_pat = _pattern_by_ref(str(date_ref))
    ts_pat = _pattern_by_ref(str(ts_ref))
    trace_pat = _pattern_by_ref("trace_id")
    req_pat = _pattern_by_ref("request_id")

    error_format_fields: dict[str, str] = {}
    for field_name, spec in (domain.error_axioms.get("required_fields") or {}).items():
        if isinstance(spec, dict) and isinstance(spec.get("format_ref"), str):
            fmt_ref = spec["format_ref"]
            if isinstance(domain.global_formats.get(fmt_ref), dict) and isinstance(domain.global_formats[fmt_ref].get("pattern"), str):
                error_format_fields[field_name] = fmt_ref
    for field_name, spec in (domain.error_axioms.get("optional_fields") or {}).items():
        if isinstance(spec, dict) and isinstance(spec.get("format_ref"), str):
            fmt_ref = spec["format_ref"]
            if isinstance(domain.global_formats.get(fmt_ref), dict) and isinstance(domain.global_formats[fmt_ref].get("pattern"), str):
                error_format_fields[field_name] = fmt_ref

    def _expected_pattern_for_field(field_name: str) -> tuple[str, str] | None:
        # Campos canônicos do error model têm precedência sobre heurísticas de sufixo.
        fmt_ref = error_format_fields.get(field_name)
        if isinstance(fmt_ref, str) and fmt_ref:
            return (fmt_ref, _pattern_by_ref(fmt_ref))
        if field_name == "traceId":
            return ("trace_id", trace_pat)
        if field_name == "requestId":
            return ("request_id", req_pat)
        if field_name == "id" or field_name.endswith("Id"):
            return (str(uuid_ref), uuid_pat)
        if field_name.endswith("Date"):
            return (str(date_ref), date_pat)
        if field_name.endswith("At"):
            return (str(ts_ref), ts_pat)
        return None

    for artifact in sorted(artifacts):
        path = pathlib.Path(artifact)
        if not path.exists():
            continue
        try:
            data = _load_json(path) if path.suffix == ".json" else _load_yaml(path)
        except Exception as e:
            violations.append(_violation(BLOCKED_FORMAT_VIOLATION, f"Falha ao ler/parsear: {e}", artifact))
            continue

        def _resolve_local_ref(doc: object, ref: str) -> dict | None:
            if not isinstance(ref, str) or not ref.startswith("#/"):
                return None
            if not isinstance(doc, dict):
                return None
            cur: object = doc
            for part in ref[2:].split("/"):
                if not isinstance(cur, dict):
                    return None
                if part not in cur:
                    return None
                cur = cur[part]
            return cur if isinstance(cur, dict) else None

        def _extract_effective_pattern(schema: dict, doc: object) -> str | None:
            # 1) pattern direto
            pat = schema.get("pattern")
            if isinstance(pat, str) and pat:
                return pat

            # 2) $ref local (#/definitions/... ou #/$defs/...)
            ref = schema.get("$ref")
            if isinstance(ref, str):
                resolved = _resolve_local_ref(doc, ref)
                if isinstance(resolved, dict):
                    return _extract_effective_pattern(resolved, doc)

            # 3) anyOf/oneOf com nullability (permitir union com null)
            for key in ("anyOf", "oneOf"):
                variants = schema.get(key)
                if isinstance(variants, list) and variants:
                    patterns: list[str] = []
                    for variant in variants:
                        if not isinstance(variant, dict):
                            continue
                        if variant.get("type") == "null":
                            continue
                        vpat = _extract_effective_pattern(variant, doc)
                        if isinstance(vpat, str) and vpat:
                            patterns.append(vpat)
                    # Se todas as variantes não-null convergem para 1 pattern, aceitar.
                    if patterns and len(set(patterns)) == 1:
                        return patterns[0]

            return None

        for node_path, node in _walk(data):
            if not isinstance(node, dict):
                continue
            # Evitar falsos positivos em schemas condicionais (if/then/else/not),
            # onde props podem redefinir tipos/guards (ex: deletedAt=null) e não representam
            # o contrato público do shape.
            if any(str(seg) in ("if", "then", "else", "not") for seg in node_path):
                continue
            props = node.get("properties")
            if not isinstance(props, dict):
                continue
            for field_name, schema in sorted(props.items(), key=lambda x: str(x[0])):
                if not isinstance(field_name, str) or not isinstance(schema, dict):
                    continue
                expected = _expected_pattern_for_field(field_name)
                if expected is None:
                    continue
                fmt_key, expected_pattern = expected
                actual_pattern = _extract_effective_pattern(schema, data)
                if actual_pattern != expected_pattern:
                    violations.append(
                        _violation(
                            BLOCKED_FORMAT_VIOLATION,
                            f"Campo `{field_name}` deve usar pattern canônico de {fmt_key}.",
                            artifact,
                            {
                                "field": field_name,
                                "expected_pattern": expected_pattern,
                                "actual_pattern": actual_pattern,
                                "path": "/".join(node_path),
                            },
                        )
                    )

    return violations


def validate_enums_against_closed_sets(artifacts: list[str], axioms: dict) -> list[dict]:
    """
    Falha se enum fechado (`closed_set=true`) tiver valor fora do conjunto canônico.

    Mapeamento determinístico:
    - para evitar interpretação por matching de valores, um enum só é validado quando declara
      explicitamente `x-domain-enum-ref: <enum_name>` apontando para uma chave em
      `domain_axioms.domain_enums` (ou na extensão modular permitida).
    """
    violations: list[dict] = []
    domain = DomainAxioms.from_dict(axioms)

    def _is_meta_schema(path: pathlib.Path) -> bool:
        # Contratos estruturais (ex: domain_axioms_module.schema.json) podem usar `enum` internamente.
        parts = path.as_posix().split("/")
        return "contracts/schemas/shared/" in path.as_posix() or (len(parts) >= 2 and parts[-2] == "shared")

    def _infer_module_name(path: pathlib.Path) -> str | None:
        p = path.as_posix()
        # JSON Schemas: contracts/schemas/<module>/*.schema.json
        if "/contracts/schemas/" in p:
            parts = p.split("/")
            try:
                idx = parts.index("schemas")
            except ValueError:
                idx = -1
            if idx >= 0 and idx + 1 < len(parts):
                module = parts[idx + 1]
                if module and module not in ("shared",):
                    return module
        # OpenAPI components: contracts/openapi/components/schemas/<module>/
        if "/contracts/openapi/components/schemas/" in p:
            parts = p.split("/")
            try:
                idx = parts.index("schemas")
            except ValueError:
                idx = -1
            if idx >= 0 and idx + 1 < len(parts):
                module = parts[idx + 1]
                if module and module not in ("shared",):
                    return module
        return None

    def _canonical_modules_from_openapi_paths(root: pathlib.Path) -> list[str]:
        paths_dir = root / "contracts" / "openapi" / "paths"
        if not paths_dir.exists():
            return []
        mods: list[str] = []
        for p in sorted(paths_dir.glob("*.yaml")):
            if p.name.startswith("_"):
                continue
            mods.append(p.stem)
        return mods

    def _load_all_module_axioms() -> tuple[dict[str, dict], list[dict]]:
        root = _repo_root()
        modules = _canonical_modules_from_openapi_paths(root)
        out: dict[str, dict] = {}
        errs: list[dict] = []
        for m in modules:
            try:
                mod_axioms = load_module_axioms(m)
            except ValueError as e:
                code, msg = _split_code_message(str(e), BLOCKED_INVALID_MODULE_AXIOM_EXTENSION)
                errs.append(_violation(code, msg or "DOMAIN_AXIOMS_<MODULE>.json inválido.", str(_module_axioms_file_path(m))))
                continue
            if isinstance(mod_axioms, dict):
                out[m] = mod_axioms
        return out, errs

    for artifact in sorted(artifacts):
        path = pathlib.Path(artifact)
        if not path.exists():
            continue
        if path.suffix == ".json" and _is_meta_schema(path):
            continue
        try:
            data = _load_json(path) if path.suffix == ".json" else _load_yaml(path)
        except Exception as e:
            violations.append(_violation(BLOCKED_ENUM_OUTSIDE_AXIOMS, f"Falha ao ler/parsear: {e}", artifact))
            continue

        # Enums são validados contra o conjunto global — extensões modulares removidas (allow_module_extensions=false).
        effective_enums = domain.domain_enums

        for node_path, node in _walk(data):
            if not isinstance(node, dict):
                continue
            if "enum" not in node or not isinstance(node.get("enum"), list):
                continue
            values = node.get("enum")
            if not isinstance(values, list):
                continue

            enum_ref = node.get("x-domain-enum-ref")
            if not isinstance(enum_ref, str) or not enum_ref:
                violations.append(
                    _violation(
                        BLOCKED_ENUM_OUTSIDE_AXIOMS,
                        "Enum encontrado sem `x-domain-enum-ref` (proibido por contrato).",
                        artifact,
                        {"path": "/".join(node_path)},
                    )
                )
                continue

            spec = effective_enums.get(enum_ref)
            if not isinstance(spec, dict):
                violations.append(
                    _violation(
                        BLOCKED_ENUM_OUTSIDE_AXIOMS,
                        f"`x-domain-enum-ref` aponta para enum inexistente em domain_axioms.domain_enums: {enum_ref}",
                        artifact,
                        {"enum_ref": enum_ref, "path": "/".join(node_path)},
                    )
                )
                continue

            closed = bool(spec.get("closed_set", False))
            if not closed:
                continue

            allowed = set(spec.get("values", []))
            extra = [v for v in values if v not in allowed]
            if extra:
                violations.append(
                    _violation(
                        BLOCKED_ENUM_OUTSIDE_AXIOMS,
                        f"Enum `{enum_ref}` contém valores fora do conjunto canônico (closed_set=true).",
                        artifact,
                        {"enum_ref": enum_ref, "extra_values": extra, "path": "/".join(node_path)},
                    )
                )

    return violations


def validate_state_transitions_against_axioms(state_models: list[str], axioms: dict) -> list[dict]:
    """
    Monta o grafo e falha se houver aresta fora de allowed_transitions ou dentro de forbidden_transitions.

    Entrada esperada (machine-readable):
    - cada arquivo em state_models deve ser JSON com:
      { "state_model": { "state_machine_ref": "<ref>", "allowed_transitions": {...} } }
    """
    violations: list[dict] = []
    domain = DomainAxioms.from_dict(axioms)

    for artifact in sorted(state_models):
        path = pathlib.Path(artifact)
        if not path.exists():
            continue
        try:
            data = _load_json(path)
        except Exception as e:
            violations.append(_violation(BLOCKED_STATE_MACHINE_VIOLATION, f"JSON inválido: {e}", artifact))
            continue

        sm = (data.get("state_model") or {}) if isinstance(data, dict) else {}
        ref = sm.get("state_machine_ref")
        allowed = sm.get("allowed_transitions")
        if not isinstance(ref, str) or not isinstance(allowed, dict):
            violations.append(
                _violation(
                    BLOCKED_STATE_MACHINE_VIOLATION,
                    "state_model inválido: requer `state_machine_ref` (string) e `allowed_transitions` (object).",
                    artifact,
                )
            )
            continue

        axi_sm = domain.state_axioms.get(ref)
        if not isinstance(axi_sm, dict):
            violations.append(
                _violation(
                    BLOCKED_STATE_MACHINE_VIOLATION,
                    f"state_machine_ref `{ref}` não existe em domain_axioms.state_axioms.",
                    artifact,
                )
            )
            continue

        axi_allowed = axi_sm.get("allowed_transitions", {})
        axi_forbidden = {tuple(x) for x in axi_sm.get("forbidden_transitions", []) if isinstance(x, list) and len(x) == 2}

        for from_state, tos in allowed.items():
            if not isinstance(from_state, str) or not isinstance(tos, list):
                continue
            allowed_targets = set(axi_allowed.get(from_state, [])) if isinstance(axi_allowed, dict) else set()
            for to_state in tos:
                if not isinstance(to_state, str):
                    continue
                edge = (from_state, to_state)
                if edge in axi_forbidden:
                    violations.append(
                        _violation(
                            BLOCKED_FORBIDDEN_TRANSITION,
                            f"Transição proibida presente: {from_state} -> {to_state}.",
                            artifact,
                            {"from": from_state, "to": to_state, "state_machine_ref": ref},
                        )
                    )
                if to_state not in allowed_targets:
                    violations.append(
                        _violation(
                            BLOCKED_STATE_MACHINE_VIOLATION,
                            f"Transição fora de allowed_transitions: {from_state} -> {to_state}.",
                            artifact,
                            {"from": from_state, "to": to_state, "state_machine_ref": ref},
                        )
                    )

    return violations


def validate_error_shape_required_fields(openapi_root: str, axioms: dict) -> list[dict]:
    """
    Falha se o shape público de erro não exigir type, title, status, trace_id (conforme axioms).
    """
    domain = DomainAxioms.from_dict(axioms)
    required = set(domain.error_axioms.get("required_fields", {}).keys())

    root = pathlib.Path(openapi_root)
    if not root.exists():
        return [_violation(BLOCKED_ERROR_MODEL_MISMATCH, "OpenAPI root não encontrado.", openapi_root)]

    try:
        openapi = _load_yaml(root)
    except Exception as e:
        return [_violation(BLOCKED_ERROR_MODEL_MISMATCH, f"Falha ao parsear OpenAPI: {e}", openapi_root)]

    components = (openapi or {}).get("components", {}) if isinstance(openapi, dict) else {}
    schemas = components.get("schemas", {}) if isinstance(components, dict) else {}
    problem_ref = None
    if isinstance(schemas, dict):
        problem = schemas.get("problem")
        if isinstance(problem, dict):
            problem_ref = problem.get("$ref")

    if not isinstance(problem_ref, str):
        return [
            _violation(
                BLOCKED_ERROR_MODEL_MISMATCH,
                "OpenAPI não define `components.schemas.problem` via `$ref`.",
                openapi_root,
            )
        ]

    resolved = (root.parent / problem_ref).resolve()
    if not resolved.exists():
        return [_violation(BLOCKED_ERROR_MODEL_MISMATCH, f"$ref do Problem não existe: {resolved}", openapi_root)]

    try:
        problem_schema = _load_yaml(resolved)
    except Exception as e:
        return [_violation(BLOCKED_ERROR_MODEL_MISMATCH, f"Falha ao parsear schema Problem: {e}", str(resolved))]

    schema_required = set(problem_schema.get("required", []) if isinstance(problem_schema, dict) else [])
    missing = sorted([f for f in required if f not in schema_required])
    if missing:
        return [
            _violation(
                BLOCKED_ERROR_MODEL_MISMATCH,
                "Schema Problem não exige todos os campos requeridos pelos axiomas.",
                str(resolved),
                {"missing_required_fields": missing, "required_by_axioms": sorted(required)},
            )
        ]
    return []


def _collect_openapi_operation_ids(openapi_root: pathlib.Path) -> set[str]:
    ids: set[str] = set()
    paths_dir = openapi_root.parent / "paths"
    if not paths_dir.exists():
        return ids
    for path in sorted(paths_dir.glob("*.yaml")):
        try:
            doc = _load_yaml(path)
        except Exception:
            continue
        for _, node in _walk(doc):
            if isinstance(node, dict) and "operationId" in node and isinstance(node["operationId"], str):
                ids.add(node["operationId"])
    return ids


_OPENAPI_HTTP_METHODS = {"get", "put", "post", "delete", "options", "head", "patch", "trace"}


def _load_openapi_doc(path: pathlib.Path) -> Any:
    suf = path.suffix.lower()
    if suf == ".json":
        return _load_json(path)
    if suf in (".yaml", ".yml"):
        return _load_yaml(path)
    # OpenAPI SSOT aqui é YAML/JSON; outros formatos são erro de infra/config.
    raise ValueError(f"OpenAPI doc com extensão não suportada: {path}")


def _json_pointer_resolve(doc: Any, pointer: str) -> Any:
    """
    Resolve JSON Pointer (RFC 6901) com escapes ~0/~1.
    Aceita pointer com ou sem prefixo '#'.
    """
    if not isinstance(pointer, str):
        raise KeyError("pointer inválido")
    p = pointer
    if p.startswith("#"):
        p = p[1:]
    if p == "":
        return doc
    if not p.startswith("/"):
        raise KeyError(f"pointer inválido (esperado '/'): {pointer!r}")
    cur: Any = doc
    for raw in p.lstrip("/").split("/"):
        tok = raw.replace("~1", "/").replace("~0", "~")
        if isinstance(cur, dict):
            if tok not in cur:
                raise KeyError(f"token ausente em dict: {tok}")
            cur = cur[tok]
        elif isinstance(cur, list):
            try:
                idx = int(tok)
            except ValueError as e:
                raise KeyError(f"token inválido para lista: {tok}") from e
            cur = cur[idx]
        else:
            raise KeyError(f"não é possível navegar em tipo: {type(cur).__name__}")
    return cur


def _resolve_ref_chain(
    *,
    ref: str,
    doc: Any,
    base_dir: pathlib.Path,
    max_depth: int = 8,
) -> Any:
    """
    Resolve cadeia de `$ref` (file + fragment JSON pointer) para um nó concreto.
    """
    if not isinstance(ref, str) or not ref.strip():
        raise KeyError("ref inválida")
    cur_ref = ref.strip()
    cur_doc = doc
    cur_base = base_dir

    for _ in range(max_depth):
        node: Any
        if cur_ref.startswith("#"):
            node = _json_pointer_resolve(cur_doc, cur_ref)
        else:
            if "#" in cur_ref:
                ref_path_str, frag = cur_ref.split("#", 1)
                frag = "#" + frag
            else:
                ref_path_str, frag = cur_ref, ""
            target_path = (cur_base / ref_path_str).resolve()
            if not target_path.exists():
                raise FileNotFoundError(f"$ref aponta para arquivo inexistente: {target_path}")
            target_doc = _load_openapi_doc(target_path)
            node = target_doc if not frag else _json_pointer_resolve(target_doc, frag)
            cur_doc = target_doc
            cur_base = target_path.parent

        if isinstance(node, dict) and isinstance(node.get("$ref"), str):
            cur_ref = node["$ref"]
            continue
        return node

    raise ValueError("Cadeia de $ref profunda demais (possível loop).")


def _collect_openapi_operations(root_path: pathlib.Path) -> set[tuple[str, str]]:
    """
    Coleta operações (method, path) a partir do OpenAPI root, resolvendo `$ref`
    em path items quando necessário.
    """
    doc = _load_openapi_doc(root_path)
    if not isinstance(doc, dict):
        raise ValueError("OpenAPI root inválido: esperado mapping no documento.")
    paths = doc.get("paths")
    if not isinstance(paths, dict):
        return set()

    ops: set[tuple[str, str]] = set()
    base_dir = root_path.parent
    for path_key, path_item in paths.items():
        if not isinstance(path_key, str) or not path_key:
            continue
        node = path_item
        if isinstance(path_item, dict) and isinstance(path_item.get("$ref"), str):
            node = _resolve_ref_chain(ref=path_item["$ref"], doc=doc, base_dir=base_dir)
        if not isinstance(node, dict):
            continue
        for k in node.keys():
            if isinstance(k, str) and k.lower() in _OPENAPI_HTTP_METHODS:
                ops.add((k.lower(), path_key))
    return ops


def _extract_arazzo_operation_ids(arazzo_doc: Any) -> set[str]:
    # Parsing mínimo determinístico: coletar qualquer string em chaves "operationId".
    op_ids: set[str] = set()
    for _, node in _walk(arazzo_doc):
        if isinstance(node, dict):
            v = node.get("operationId")
            if isinstance(v, str) and v:
                op_ids.add(v)
    return op_ids


def _module_axioms_file_path(module_name: str) -> pathlib.Path:
    root = _repo_root()
    return root / "docs" / "hbtrack" / "modulos" / module_name / f"DOMAIN_AXIOMS_{module_name.upper()}.json"


def _normalize_event_type_payload_constraints(payload_constraints: dict) -> dict:
    required_fields = payload_constraints.get("required_fields", [])
    field_formats = payload_constraints.get("field_formats", {})
    req = sorted([x for x in required_fields if isinstance(x, str)])
    ff = {k: v for k, v in field_formats.items() if isinstance(k, str) and isinstance(v, str)}
    return {
        "required_fields": req,
        "field_formats": dict(sorted(ff.items(), key=lambda kv: kv[0])),
    }


def _event_type_fingerprint(v: dict) -> dict:
    return {
        "semantic_id": v.get("semantic_id"),
        "description": v.get("description"),
        "payload_constraints": _normalize_event_type_payload_constraints(v.get("payload_constraints") or {}),
    }


def _validate_event_type_extension_semantics(axioms: dict, module_axioms_by_module: dict[str, dict]) -> list[dict]:
    """
    Regras de colisão semântica para extensões modulares de `event_type`:
    1) mesmo name + mesmo semantic_id + constraints idênticas => OK
    2) mesmo name + semantic_id diferente => FAIL
    3) mesmo name + mesmo semantic_id + payload diferente => FAIL
    4) nomes diferentes para mesma semântica (semantic_id) => conflito para revisão (FAIL)
    """
    violations: list[dict] = []
    domain = DomainAxioms.from_dict(axioms)
    event_spec = domain.domain_enums.get("event_type")
    if not isinstance(event_spec, dict):
        return violations

    enum_policy = event_spec.get("module_extension_policy") if isinstance(event_spec.get("module_extension_policy"), dict) else {}
    if not bool(enum_policy.get("allow_module_extensions", False)):
        return violations

    records_by_name: dict[str, list[dict]] = {}
    records_by_semantic_id: dict[str, list[dict]] = {}

    for module_name, mod_axioms in sorted(module_axioms_by_module.items(), key=lambda kv: kv[0]):
        domain_enums = mod_axioms.get("domain_enums", {})
        if not isinstance(domain_enums, dict):
            continue
        ext = domain_enums.get("event_type")
        if not isinstance(ext, dict):
            continue
        values = ext.get("values", [])
        if not isinstance(values, list):
            continue
        for v in values:
            if not isinstance(v, dict):
                continue
            name = v.get("name")
            semantic_id = v.get("semantic_id")
            if not isinstance(name, str) or not name or not isinstance(semantic_id, str) or not semantic_id:
                continue
            rec = {
                "module": module_name,
                "file": str(_module_axioms_file_path(module_name)),
                "value": name,
                "fingerprint": _event_type_fingerprint(v),
            }
            records_by_name.setdefault(name, []).append(rec)
            records_by_semantic_id.setdefault(semantic_id, []).append(rec)

    # (2) e (3): mesmo name com semântica/constraints divergentes
    for name, recs in sorted(records_by_name.items(), key=lambda kv: kv[0]):
        if len(recs) < 2:
            continue
        base = recs[0]
        for other in recs[1:]:
            fp_a = base["fingerprint"]
            fp_b = other["fingerprint"]
            sid_a = fp_a.get("semantic_id")
            sid_b = fp_b.get("semantic_id")
            if sid_a != sid_b:
                violations.append(
                    _violation(
                        BLOCKED_AXIOM_NAME_CLASH,
                        "Colisão semântica: mesmo name com semantic_id diferente.",
                        str(_repo_root() / "docs" / "hbtrack" / "modulos"),
                        {
                            "enum": "event_type",
                            "value": name,
                            "module_a": base["module"],
                            "module_b": other["module"],
                            "reason": "SAME_NAME_DIFFERENT_SEMANTICS",
                            "semantic_id_a": sid_a,
                            "semantic_id_b": sid_b,
                            "file_a": base["file"],
                            "file_b": other["file"],
                        },
                    )
                )
                continue

            diffs: list[str] = []
            if fp_a.get("description") != fp_b.get("description"):
                diffs.append("description")
            pc_a = fp_a.get("payload_constraints", {})
            pc_b = fp_b.get("payload_constraints", {})
            if pc_a.get("required_fields") != pc_b.get("required_fields"):
                diffs.append("required_fields")
            if pc_a.get("field_formats") != pc_b.get("field_formats"):
                diffs.append("field_formats")
            if diffs:
                violations.append(
                    _violation(
                        BLOCKED_AXIOM_EXTENSION_COLLISION,
                        "Colisão semântica: mesmo name/semantic_id com payload_constraints incompatíveis.",
                        str(_repo_root() / "docs" / "hbtrack" / "modulos"),
                        {
                            "enum": "event_type",
                            "value": name,
                            "module_a": base["module"],
                            "module_b": other["module"],
                            "reason": "SAME_NAME_SAME_SEMANTIC_ID_DIFFERENT_PAYLOAD_CONSTRAINTS",
                            "diff": ",".join(diffs),
                            "semantic_id": sid_a,
                            "file_a": base["file"],
                            "file_b": other["file"],
                        },
                    )
                )

    # (4): nomes diferentes para mesma semântica
    for semantic_id, recs in sorted(records_by_semantic_id.items(), key=lambda kv: kv[0]):
        names = sorted({r["value"] for r in recs if isinstance(r.get("value"), str)})
        if len(names) < 2:
            continue
        a = recs[0]
        b = next((r for r in recs if r["value"] != a["value"]), None)
        if b is None:
            continue
        violations.append(
            _violation(
                BLOCKED_AXIOM_EXTENSION_COLLISION,
                "Colisão semântica: nomes diferentes para o mesmo semantic_id.",
                str(_repo_root() / "docs" / "hbtrack" / "modulos"),
                {
                    "enum": "event_type",
                    "reason": "DIFFERENT_NAMES_SAME_SEMANTIC_ID",
                    "semantic_id": semantic_id,
                    "name_a": a["value"],
                    "name_b": b["value"],
                    "module_a": a["module"],
                    "module_b": b["module"],
                    "file_a": a["file"],
                    "file_b": b["file"],
                    "all_names": names,
                },
            )
        )

    return violations


def validate_disciplinary_progression_axioms(axioms: dict) -> list[dict]:
    """
    Valida que `handball_domain_constraints.disciplinary_progression` é uma regra verificável:
    - ordered_levels deve ser uma permutação do enum `disciplinary_card`
    - allowed_transitions deve respeitar o grafo declarado
    - preconditions deve ser consistente (ex: BLUE_CARD requer RED_CARD)
    """
    domain = DomainAxioms.from_dict(axioms)

    hbc = axioms.get("handball_domain_constraints", {})
    if not isinstance(hbc, dict):
        return [_violation(BLOCKED_CROSS_SPEC_DIVERGENCE, "handball_domain_constraints deve ser objeto.", "DOMAIN_AXIOMS.json")]
    dp = hbc.get("disciplinary_progression")
    if not isinstance(dp, dict):
        return [_violation(BLOCKED_CROSS_SPEC_DIVERGENCE, "disciplinary_progression ausente/ inválido.", "DOMAIN_AXIOMS.json")]

    ordered = dp.get("ordered_levels")
    allowed = dp.get("allowed_transitions")
    if not isinstance(ordered, list) or not ordered or not all(isinstance(x, str) and x for x in ordered):
        return [_violation(BLOCKED_CROSS_SPEC_DIVERGENCE, "ordered_levels inválido em disciplinary_progression.", "DOMAIN_AXIOMS.json")]
    if not isinstance(allowed, dict):
        return [_violation(BLOCKED_CROSS_SPEC_DIVERGENCE, "allowed_transitions inválido em disciplinary_progression.", "DOMAIN_AXIOMS.json")]

    enum_vals = domain.domain_enums.get("disciplinary_card", {}).get("values", [])
    if not isinstance(enum_vals, list) or sorted(enum_vals) != sorted(ordered):
        return [
            _violation(
                BLOCKED_CROSS_SPEC_DIVERGENCE,
                "ordered_levels deve conter exatamente os valores de domain_enums.disciplinary_card.",
                "DOMAIN_AXIOMS.json",
                {"disciplinary_card_values": enum_vals, "ordered_levels": ordered},
            )
        ]

    index = {name: i for i, name in enumerate(ordered)}
    violations: list[dict] = []
    for from_level, tos in allowed.items():
        if from_level not in index or not isinstance(tos, list):
            violations.append(
                _violation(
                    BLOCKED_CROSS_SPEC_DIVERGENCE,
                    "allowed_transitions contém nível inválido.",
                    "DOMAIN_AXIOMS.json",
                    {"from": from_level},
                )
            )
            continue
        for to in tos:
            if to not in index:
                violations.append(
                    _violation(
                        BLOCKED_CROSS_SPEC_DIVERGENCE,
                        "allowed_transitions contém destino inválido.",
                        "DOMAIN_AXIOMS.json",
                        {"from": from_level, "to": to},
                    )
                )
                continue
            if index[to] <= index[from_level]:
                violations.append(
                    _violation(
                        BLOCKED_CROSS_SPEC_DIVERGENCE,
                        "Transição disciplinar não pode regredir/ permanecer no mesmo nível.",
                        "DOMAIN_AXIOMS.json",
                        {"from": from_level, "to": to},
                    )
                )

    pre = dp.get("preconditions", {})
    if isinstance(pre, dict):
        for level, rule in pre.items():
            if not isinstance(rule, dict):
                continue
            req = rule.get("requires_prior")
            if not isinstance(req, list):
                continue
            for needed in req:
                if needed not in index:
                    violations.append(
                        _violation(
                            BLOCKED_CROSS_SPEC_DIVERGENCE,
                            "preconditions.requires_prior contém nível inválido.",
                            "DOMAIN_AXIOMS.json",
                            {"level": level, "requires_prior": needed},
                        )
                    )
    return violations


def validate_cross_surface_alignment(
    openapi_root: str,
    asyncapi_files: list[str],
    schema_files: list[str],
    docs_files: list[str],
    axioms: dict,
) -> list[dict]:
    """
    Valida alinhamento cross-surface mínimo exigido pelos axiomas (sem interpretação livre).
    """
    violations: list[dict] = []
    domain = DomainAxioms.from_dict(axioms)
    openapi_path = pathlib.Path(openapi_root)
    if not openapi_path.exists():
        return [_violation(BLOCKED_CROSS_SPEC_DIVERGENCE, "OpenAPI root não encontrado.", openapi_root)]

    operation_ids = _collect_openapi_operation_ids(openapi_path)

    # Arazzo -> operationId must exist
    for doc_path_str in sorted(docs_files):
        doc_path = pathlib.Path(doc_path_str)
        if doc_path.suffixes[-2:] != [".arazzo", ".yaml"] and doc_path.suffixes[-2:] != [".arazzo", ".yml"]:
            continue
        if not doc_path.exists():
            continue
        try:
            arazzo_doc = _load_yaml(doc_path)
        except Exception as e:
            violations.append(_violation(BLOCKED_ARAZZO_OPENAPI_LINK_MISSING, f"Falha ao parsear Arazzo: {e}", doc_path_str))
            continue
        used = _extract_arazzo_operation_ids(arazzo_doc)
        missing = sorted([op for op in used if op not in operation_ids])
        if missing:
            violations.append(
                _violation(
                    BLOCKED_ARAZZO_OPENAPI_LINK_MISSING,
                    "Arazzo referencia operationId inexistente no OpenAPI.",
                    doc_path_str,
                    {"missing_operation_ids": missing},
                )
            )

    # Extensões de enums (quando permitido): valida path canônico + contrato estrutural + colisões.
    root = _repo_root()
    modules_root = root / "docs" / "hbtrack" / "modulos"
    module_dirs = [p for p in sorted(modules_root.glob("*")) if p.is_dir()]
    allow_ext = bool(domain.module_extension_policy.get("allow_module_extensions", False))

    canonical_files: list[pathlib.Path] = []
    non_canonical_files: list[pathlib.Path] = []
    for module_dir in module_dirs:
        expected = module_dir / f"DOMAIN_AXIOMS_{module_dir.name.upper()}.json"
        found = [p for p in sorted(module_dir.glob("DOMAIN_AXIOMS_*.json")) if p.is_file()]
        for p in found:
            if p == expected:
                continue
            non_canonical_files.append(p)
        if expected.exists():
            canonical_files.append(expected)

    if non_canonical_files:
        violations.append(
            _violation(
                BLOCKED_INVALID_MODULE_AXIOM_EXTENSION,
                "Extensão modular fora do path canônico (somente `docs/hbtrack/modulos/<module>/DOMAIN_AXIOMS_<MODULE>.json` é válida).",
                str(modules_root),
                {"files": [str(p) for p in non_canonical_files]},
            )
        )

    if canonical_files and not allow_ext:
        violations.append(
            _violation(
                BLOCKED_INVALID_MODULE_AXIOM_EXTENSION,
                "Arquivos de extensão modular existem em disco, mas allow_module_extensions=false.",
                str(modules_root),
                {"files": [str(p) for p in canonical_files]},
            )
        )

    if allow_ext:
        module_axioms_by_module: dict[str, dict] = {}
        for module_dir in module_dirs:
            module_name = module_dir.name
            try:
                module_axioms = load_module_axioms(module_name)
            except ValueError as e:
                code, msg = _split_code_message(str(e), BLOCKED_INVALID_MODULE_AXIOM_EXTENSION)
                violations.append(_violation(code, msg or "DOMAIN_AXIOMS_<MODULE>.json inválido.", str(module_dir)))
                continue
            if module_axioms is None:
                continue
            module_axioms_by_module[module_name] = module_axioms
            try:
                _ = merge_enum_extensions(axioms, module_axioms)
            except ValueError as e:
                code, _ = _split_code_message(str(e), BLOCKED_INVALID_MODULE_AXIOM_EXTENSION)
                violations.append(_violation(code, "Extensão modular inválida.", str(module_dir)))

        violations.extend(_validate_event_type_extension_semantics(axioms, module_axioms_by_module))

    # Placeholders para futuras validações explícitas:
    _ = asyncapi_files
    _ = schema_files

    return violations


def normalize_generated_content(content: str, normalization_policy: dict) -> str:
    """
    Aplicar exatamente os strips declarados no axioma antes de qualquer hash ou diff.
    """
    policy = normalization_policy or {}
    derived = policy.get("derived_artifacts", {}) if isinstance(policy, dict) else {}

    normalized = content

    # line endings normalization
    if derived.get("normalize_line_endings_to") == "LF":
        normalized = normalized.replace("\r\n", "\n").replace("\r", "\n")

    lines = normalized.split("\n")
    patterns = derived.get("strip_volatile_lines_matching", [])
    if isinstance(patterns, list) and patterns:
        compiled = [re.compile(p) for p in patterns if isinstance(p, str) and p]
        kept: list[str] = []
        for line in lines:
            if any(r.match(line) for r in compiled):
                continue
            kept.append(line)
        lines = kept

    normalized = "\n".join(lines)

    if derived.get("trim_trailing_whitespace") is True:
        normalized = "\n".join([ln.rstrip() for ln in normalized.split("\n")])

    if derived.get("ensure_final_newline") is True and not normalized.endswith("\n"):
        normalized += "\n"

    return normalized


def compare_normalized_outputs(before: str, after: str, normalization_policy: dict) -> bool:
    """
    Só retorna drift real se a diferença persistir após normalização.

    Retorna True quando há drift remanescente após normalização; False quando equivalentes.
    """
    nb = normalize_generated_content(before, normalization_policy)
    na = normalize_generated_content(after, normalization_policy)
    return nb != na


# ──────────────────────────────────────────────────────────────────────────────
# Pipeline infrastructure — gates per CI_CONTRACT_GATES.md (inclui extensões do canon)
# ──────────────────────────────────────────────────────────────────────────────

_CANONICAL_GLOBAL_DOCS: list[str] = [
    "README.md",
    ".contract_driven/DOMAIN_AXIOMS.json",
    ".contract_driven/CONTRACT_SYSTEM_LAYOUT.md",
    ".contract_driven/CONTRACT_SYSTEM_RULES.md",
    ".contract_driven/GLOBAL_TEMPLATES.md",
    ".contract_driven/templates/README.md",
    ".contract_driven/templates/globais/README.md",
    ".contract_driven/templates/globais/SYSTEM_SCOPE.md",
    ".contract_driven/templates/globais/ARCHITECTURE.md",
    ".contract_driven/templates/globais/C4_CONTEXT.md",
    ".contract_driven/templates/globais/C4_CONTAINERS.md",
    ".contract_driven/templates/globais/MODULE_MAP.md",
    ".contract_driven/templates/globais/CHANGE_POLICY.md",
    ".contract_driven/templates/globais/DATA_CONVENTIONS.md",
    ".contract_driven/templates/globais/GLOBAL_INVARIANTS.md",
    ".contract_driven/templates/globais/DOMAIN_GLOSSARY.md",
    ".contract_driven/templates/globais/HANDBALL_RULES_DOMAIN.md",
    ".contract_driven/templates/globais/SECURITY_RULES.md",
    ".contract_driven/templates/globais/CI_CONTRACT_GATES.md",
    ".contract_driven/templates/globais/TEST_STRATEGY.md",
    ".contract_driven/templates/globais/decisions/ADR-0001-template.md",
    ".contract_driven/templates/modulos/README.md",
    ".contract_driven/templates/modulos/MODULE_SCOPE_{{MODULE_NAME_UPPER}}.md",
    ".contract_driven/templates/modulos/DOMAIN_RULES_{{MODULE_NAME_UPPER}}.md",
    ".contract_driven/templates/modulos/INVARIANTS_{{MODULE_NAME_UPPER}}.md",
    ".contract_driven/templates/modulos/SPORT_SCIENCE_RULES_{{MODULE_NAME_UPPER}}.md",
    ".contract_driven/templates/modulos/STATE_MODEL_{{MODULE_NAME_UPPER}}.md",
    ".contract_driven/templates/modulos/PERMISSIONS_{{MODULE_NAME_UPPER}}.md",
    ".contract_driven/templates/modulos/ERRORS_{{MODULE_NAME_UPPER}}.md",
    ".contract_driven/templates/modulos/UI_CONTRACT_{{MODULE_NAME_UPPER}}.md",
    ".contract_driven/templates/modulos/SCREEN_MAP_{{MODULE_NAME_UPPER}}.md",
    ".contract_driven/templates/modulos/TEST_MATRIX_{{MODULE_NAME_UPPER}}.md",
    ".contract_driven/templates/modulos/snippets/module_human_docs_header.yaml",
    ".contract_driven/templates/modulos/MODULE_DOC_HEADER_POLICY.yaml",
    ".contract_driven/templates/modulos/schemas/{{DOMAIN_ENTITY_SNAKE}}.schema.json",
    ".contract_driven/templates/api/api_rules.yaml",
    ".contract_driven/templates/api/ARCHITECTURE_MATRIX.yaml",
    ".contract_driven/templates/api/MODULE_PROFILE_REGISTRY.yaml",
    ".contract_driven/templates/api/CANONICAL_TYPE_REGISTRY.yaml",
    ".contract_driven/templates/api/REGRAS_API.md",
    ".contract_driven/templates/api/GoogleAPI.md",
    ".contract_driven/templates/api/AddidasAPI.md",
    ".contract_driven/templates/api/OWASPAPI.md",
    "scripts/contracts/validate/api/policy_compiler.py",
    "scripts/contracts/validate/api/compile_api_policy.py",
    "scripts/contracts/validate/root_module_consistency_gate.py",
    "scripts/contracts/validate/pre_contract_evidence_gate.py",
    "scripts/contracts/validate/shadow_authority_gate.py",
    "scripts/contracts/validate/tooling_config_gate.py",
    "generated/README.md",
    "contracts/openapi/openapi.yaml",
    "docs/_canon/CI_CONTRACT_GATES.md",
    "docs/_canon/TOOLCHAIN_HEALTH_POLICY.md",
    "docs/_canon/CONTRACT_PIPELINE.md",
    "docs/_canon/OPERATIONS.md",
    "docs/_canon/UI_CONTRACT_GUIDE.md",
    "docs/_canon/security/OWASP_API_CONTROL_MATRIX.yaml",
    "docs/_canon/MODULE_REGISTRY.yaml",
    "docs/_canon/MODULE_SOURCE_AUTHORITY_MATRIX.yaml",
    ".contract_driven/agent_prompts/create_asyncapi_contract.prompt.md",
    ".contract_driven/agent_prompts/create_arazzo_workflow.prompt.md",
    ".contract_driven/agent_prompts/create_json_schema_contract.prompt.md",
    "contracts/schemas/shared/owasp_api_control_matrix.schema.json",
    "contracts/schemas/shared/module_registry.schema.json",
    "contracts/schemas/shared/module_source_authority_matrix.schema.json",
    ".spectral.yaml",
    "redocly.yaml",
]

_PLACEHOLDER_TOKENS: list[str] = [
    "TODO",
    "TBD",
    "A definir",
    "{{",
    "<MODULE_NAME>",
    "<MODULE>",
    "<ENTITY>",
]

# Regex para detectar placeholders conceituais — referências diferidas sem conteúdo real.
# Ex: "Ver documentação de X", "Conforme definido em Y", "Definido em seção Z".
# Whitelist: URLs (https?://), RFC/ISO references são referências legítimas, não placeholders.
_PLACEHOLDER_CONCEPTUAL_RE = re.compile(
    r'\b(Ver\s+(?:document|especifica[çc]|se[çc][aã]o|o\s+arquivo|a\s+documenta[çc]|cap[ií]tulo)'
    r'|Conforme\s+(?:document|especifica[çc]|definido\s+em|descrito\s+em)'
    r'|Definido\s+em\s+\w'
    r'|Confira\s+em\s+\w'
    r'|A\s+(?:ser\s+definido|completar|preencher)\b)',
    re.IGNORECASE,
)
_PLACEHOLDER_CONCEPTUAL_WHITELIST_RE = re.compile(
    r'https?://|RFC\s*\d+|ISO\s+\d+',
    re.IGNORECASE,
)


def _pg(
    gate_id: str,
    status: str,
    blocking: bool,
    blocking_code: str | None,
    summary: str,
    inputs: list[str],
    artifacts_checked: list[str],
    evidence_files: list[str],
    violations: list[dict],
    duration_ms: int,
) -> dict:
    errors = len([v for v in violations if v.get("severity", "error") != "warn"])
    warnings = len([v for v in violations if v.get("severity") == "warn"])
    if status == "SKIP_NOT_APPLICABLE":
        exit_code = 0
    elif status in {"PASS", "DEGRADED"}:
        exit_code = 0
    else:
        exit_code = 2
    return {
        "gate_id": gate_id,
        "status": status,
        "blocking": blocking,
        "exit_code": exit_code,
        "blocking_code": blocking_code,
        "summary": summary,
        "inputs": inputs,
        "artifacts_checked": artifacts_checked,
        "evidence_files": evidence_files,
        "violations": violations,
        "metrics": {
            "errors": errors,
            "warnings": warnings,
            "violations": len(violations),
            "duration_ms": duration_ms,
        },
    }


def _skip(gate_id: str, reason: str, dur: int = 0) -> dict:
    return _pg(gate_id, "SKIP_NOT_APPLICABLE", False, None, reason, [], [], [], [], dur)


def _wsl_to_windows_path(path_str: str) -> str:
    """
    Convert WSL path (/mnt/c/...) to Windows path (C:\\...).
    If path doesn't start with /mnt/, return unchanged.
    """
    if not path_str.startswith("/mnt/"):
        return path_str
    # /mnt/c/foo/bar → C:\foo\bar
    parts = path_str.split("/")
    if len(parts) < 3:
        return path_str
    drive = parts[2].upper()
    rest = "/".join(parts[3:])
    windows_path = f"{drive}:\\" + rest.replace("/", "\\")
    return windows_path


def _try_tool(
    *cmd: str,
    cwd: pathlib.Path | None = None,
    env: dict[str, str] | None = None,
) -> tuple[int, str, str]:
    """Run external tool; returns (returncode, stdout, stderr). rc=-1 means tool not found."""
    # On Windows, npm-installed CLIs are .cmd wrappers; shell=True is required to resolve them.
    use_shell = sys.platform == "win32"
    merged_env = None
    if env:
        merged_env = dict(os.environ)
        merged_env.update(env)

    def _run_direct() -> tuple[int, str, str]:
        result = subprocess.run(
            list(cmd),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=str(cwd) if cwd else None,
            shell=use_shell,
            env=merged_env,
            timeout=90,
        )
        stdout = (result.stdout or b"").decode("utf-8", errors="replace")
        stderr = (result.stderr or b"").decode("utf-8", errors="replace")
        return result.returncode, stdout, stderr

    try:
        return _run_direct()
    except subprocess.TimeoutExpired:
        return -1, "", f"Tool timed out: {cmd[0]}"
    except FileNotFoundError:
        node_tool = pathlib.Path(cmd[0]).name in {"node", "npm", "npx"}
        nvm_path = pathlib.Path.home().joinpath(".nvm/nvm.sh")
        if sys.platform == "linux" and node_tool and nvm_path.exists():
            nvm_load = ". ~/.nvm/nvm.sh && "
            cmd_str = " ".join(f'"{c}"' if " " in c else c for c in cmd)
            full_cmd = f"{nvm_load}{cmd_str}"
            try:
                result = subprocess.run(
                    ["/bin/bash", "-c", full_cmd],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=str(cwd) if cwd else None,
                    env=merged_env,
                    timeout=90,
                )
                stdout = (result.stdout or b"").decode("utf-8", errors="replace")
                stderr = (result.stderr or b"").decode("utf-8", errors="replace")
                return result.returncode, stdout, stderr
            except subprocess.TimeoutExpired:
                return -1, "", f"Tool timed out (nvm fallback): {cmd[0]}"
            except FileNotFoundError:
                return -1, "", f"Tool not found: {cmd[0]}"
        return -1, "", f"Tool not found: {cmd[0]}"


def _looks_like_windows_command_not_found(tool: str, text: str) -> bool:
    """
    Em Windows (shell=True), comandos ausentes normalmente não levantam FileNotFoundError;
    o shell retorna stderr com mensagens do tipo "'tool' não é reconhecido...".
    """
    if not tool or not isinstance(text, str):
        return False
    t = text.lower()
    tool_l = tool.lower()
    if tool_l not in t:
        return False
    if "not recognized" in t:
        return True
    if "não é reconhecido" in t or "nao e reconhecido" in t:
        return True
    # mojibake comum quando a saída do cmd.exe vem em cp1252 e é decodada como utf-8
    if "n�o" in t and "reconhecido" in t:
        return True
    return False


def _looks_like_node_missing(text: str) -> bool:
    if not isinstance(text, str) or not text:
        return False
    t = text.lower()
    if "exec: node: not found" in t or "node: not found" in t:
        return True
    if "node is not recognized" in t:
        return True
    if ("não é reconhecido" in t or "nao e reconhecido" in t) and "node" in t:
        return True
    return False


def _looks_like_wsl_vsock_failure(text: str) -> bool:
    if not isinstance(text, str) or not text:
        return False
    return "UtilBindVsockAnyPort" in text


def _looks_like_redocly_update_only(text: str) -> bool:
    """Return True when redocly output contains only an update notice, no real lint errors."""
    if not isinstance(text, str) or not text:
        return False
    meaningful = [
        ln.strip()
        for ln in text.splitlines()
        if ln.strip() and not set(ln.strip()).issubset(set("═║╔╗╚╝ "))
    ]
    if not meaningful:
        return True
    update_keywords = ("a new version of redocly", "new version", "is available")
    return all(any(kw in ln.lower() for kw in update_keywords) for ln in meaningful)


def _parse_semver_triplet(v: str) -> tuple[int, int, int] | None:
    m = re.match(r"^v?(\d+)\.(\d+)\.(\d+)$", v.strip())
    if not m:
        return None
    return (int(m.group(1)), int(m.group(2)), int(m.group(3)))


def _find_wsl_node_bin() -> pathlib.Path | None:
    """
    Resolve um Node.js **WSL-native** (evita Windows interop via node.exe).

    Ordem:
    1) $HBTRACK_NODE_BIN (se definido)
    2) `node` no PATH (somente se NÃO for /mnt/* e NÃO terminar com .exe)
    3) $NVM_BIN/node
    4) ~/.nvm/versions/node/<maior versão>/bin/node
    """
    override = os.environ.get("HBTRACK_NODE_BIN")
    if override:
        p = pathlib.Path(override).expanduser()
        if p.exists():
            return p

    found = shutil.which("node")
    if found:
        p = pathlib.Path(found)
        # WSL interop: normalmente expõe binários Windows em /mnt/c/.../*.exe
        if not str(p).startswith("/mnt/") and not str(p).lower().endswith(".exe"):
            return p

    nvm_bin = os.environ.get("NVM_BIN")
    if nvm_bin:
        p = pathlib.Path(nvm_bin) / "node"
        if p.exists():
            return p

    base = pathlib.Path.home() / ".nvm" / "versions" / "node"
    if base.exists():
        candidates: list[tuple[tuple[int, int, int], pathlib.Path]] = []
        for d in base.iterdir():
            if not d.is_dir():
                continue
            ver = _parse_semver_triplet(d.name)
            if ver is None:
                continue
            node_bin = d / "bin" / "node"
            if node_bin.exists():
                candidates.append((ver, node_bin))
        if candidates:
            candidates.sort(key=lambda x: x[0])
            return candidates[-1][1]

    return None


def _node_prefix_from_node_bin(node_bin: pathlib.Path) -> pathlib.Path | None:
    """
    Para instalações tipo NVM:
      <prefix>/bin/node
      <prefix>/lib/node_modules/...
    """
    try:
        prefix = node_bin.resolve().parent.parent
    except Exception:  # pragma: no cover
        prefix = node_bin.parent.parent
    lib_nm = prefix / "lib" / "node_modules"
    return prefix if lib_nm.exists() else None


def _resolve_node_cli_script(
    root: pathlib.Path,
    *,
    tool: str,
    node_prefix: pathlib.Path | None,
    scope: str = "any",
) -> pathlib.Path | None:
    tool = tool.strip().lower()
    local_candidates: list[pathlib.Path] = []
    global_candidates: list[pathlib.Path] = []

    if tool == "redocly":
        local_candidates = [root / "node_modules" / "@redocly" / "cli" / "bin" / "cli.js"]
        if node_prefix:
            global_candidates = [node_prefix / "lib" / "node_modules" / "@redocly" / "cli" / "bin" / "cli.js"]
    elif tool == "spectral":
        local_candidates = [root / "node_modules" / "@stoplight" / "spectral-cli" / "dist" / "index.js"]
        if node_prefix:
            global_candidates = [node_prefix / "lib" / "node_modules" / "@stoplight" / "spectral-cli" / "dist" / "index.js"]
    elif tool == "asyncapi":
        # Prefer `bin/run` (NODE_ENV=development) para evitar strict-mode fatal do node-config no CLI.
        local_candidates = [root / "node_modules" / "@asyncapi" / "cli" / "bin" / "run"]
        if node_prefix:
            global_candidates = [node_prefix / "lib" / "node_modules" / "@asyncapi" / "cli" / "bin" / "run"]
    else:
        return None

    if scope == "local":
        search = local_candidates
    elif scope == "global":
        search = global_candidates
    else:
        search = local_candidates + global_candidates

    for p in search:
        if p.exists():
            return p
    return None


def _looks_like_node_module_resolution_failure(text: str) -> bool:
    if not isinstance(text, str) or not text:
        return False
    t = text.lower()
    # Node CJS loader common patterns
    if "cannot find module" in t:
        return True
    if "module_not_found" in t:
        return True
    return False


def _try_node_cli(root: pathlib.Path, *, tool: str, args: list[str], cwd: pathlib.Path | None = None) -> tuple[int, str, str]:
    """
    Executa CLI Node de forma WSL-native (sem wrappers Windows).
    Retorna (rc, stdout, stderr). rc=-1 indica tool/script/node ausente.
    """
    node_bin = _find_wsl_node_bin()
    if node_bin is None:
        return -1, "", "Node.js WSL-native não encontrado (configure NVM ou instale Node no WSL)."
    node_prefix = _node_prefix_from_node_bin(node_bin)

    # Candidatos (preferir local; fallback para global NVM quando o local está corrompido).
    local = _resolve_node_cli_script(root, tool=tool, node_prefix=None, scope="local")
    global_ = _resolve_node_cli_script(root, tool=tool, node_prefix=node_prefix, scope="global") if node_prefix else None
    candidates = [p for p in (local, global_) if p is not None]
    if not candidates:
        return -1, "", f"CLI `{tool}` não encontrada (nem local em node_modules, nem global em NVM)."

    tool_env: dict[str, str] | None = None
    if tool.strip().lower() == "asyncapi":
        # asyncapi-cli usa `path.join(__dirname, log.dir)` (não `resolve`), então para
        # sair do diretório do package e alcançar `/tmp`, precisamos subir até a raiz.
        # Extra `..` são inofensivos (normalizam para `/`).
        log_dir_rel_to_utils = "../../../../../../../../../../../../tmp/hbtrack_asyncapi_logs"
        spectral_node_modules_paths: list[str] = []
        local_spectral_nm = root / "node_modules" / "@stoplight" / "spectral-cli" / "node_modules"
        if local_spectral_nm.exists():
            spectral_node_modules_paths.append(str(local_spectral_nm))
        if node_prefix:
            global_spectral_nm = node_prefix / "lib" / "node_modules" / "@stoplight" / "spectral-cli" / "node_modules"
            if global_spectral_nm.exists():
                spectral_node_modules_paths.append(str(global_spectral_nm))
        node_path = ":".join(spectral_node_modules_paths)

        tool_env = {
            "NODE_ENV": "development",
            "NODE_CONFIG_STRICT_MODE": "0",
            "SUPPRESS_NO_CONFIG_WARNING": "1",
            # asyncapi-cli escreve logs em `__dirname/logs` por default; apontar para diretório gravável.
            "NODE_CONFIG": json.dumps({"log": {"dir": log_dir_rel_to_utils}}, ensure_ascii=False),
            # asyncapi-cli usa spectral internamente e pode tentar resolver formatters via require().
            # Forçar resolution em um node_modules conhecido.
            **({"NODE_PATH": node_path} if node_path else {}),
        }

    # 1) tentar local (se existir)
    rc, stdout, stderr = _try_tool(str(node_bin), str(candidates[0]), *args, cwd=cwd, env=tool_env)
    out = stdout + stderr
    if rc == 0:
        return rc, stdout, stderr

    # 2) fallback para global NVM somente quando o erro indica toolchain local quebrada.
    if local is not None and global_ is not None and candidates[0] == local and _looks_like_node_module_resolution_failure(out):
        return _try_tool(str(node_bin), str(global_), *args, cwd=cwd, env=tool_env)

    return rc, stdout, stderr


def _local_node_bin(tool: str) -> pathlib.Path | None:
    root = _repo_root()
    bin_dir = root / "node_modules" / ".bin"
    if not bin_dir.exists():
        return None
    if sys.platform == "win32":
        candidate = bin_dir / f"{tool}.cmd"
        return candidate if candidate.exists() else None
    candidate = bin_dir / tool
    return candidate if candidate.exists() else None


def _ms(t0: float) -> int:
    return int((time.monotonic() - t0) * 1000)


def _git_commit(root: pathlib.Path) -> str | None:
    rc, out, _ = _try_tool("git", "rev-parse", "--short", "HEAD", cwd=root)
    return out.strip() if rc == 0 else None


def _tool_ver(*cmd: str) -> str | None:
    if not cmd:
        return None
    tool = cmd[0]

    def _is_windows_interop_wrapper(path: pathlib.Path) -> bool:
        if str(path).startswith("/mnt/") or str(path).lower().endswith(".exe"):
            return True
        try:
            if not path.is_file():
                return False
            head = path.read_bytes()[:256]
        except Exception:
            return False
        if not head.startswith(b"#!"):
            return False
        text = head.decode("utf-8", errors="replace").lower()
        return any(marker in text for marker in (".exe", "cmd.exe", "powershell"))

    # Evitar interop WSL/Windows: wrappers que chamam *.exe tendem a gerar vsock errors.
    if tool == "oasdiff":
        p = shutil.which("oasdiff")
        if not p:
            return None
        pp = pathlib.Path(p)
        if _is_windows_interop_wrapper(pp):
            return None
        cmd = ("oasdiff", "--version")

    # Ferramentas Node.js (redocly, spectral, asyncapi): usar _try_node_cli para evitar que o
    # PATH (após sourcing do nvm.sh) resolva para binários Windows em /mnt/c/... — o que causa
    # freeze de 7-10 s até o timeout da subprocess.  _try_node_cli usa o caminho absoluto do
    # node WSL-native + o script local/global, contornando inteiramente o wrapper Windows.
    if tool in ("redocly", "spectral", "asyncapi"):
        root = _repo_root()
        rc, out, err = _try_node_cli(root, tool=tool, args=list(cmd[1:]), cwd=root)
        if rc != 0:
            return None
        text = (out or err).strip()
        if _looks_like_wsl_vsock_failure(text):
            return None
        return text.splitlines()[0] if text else "unknown"

    rc, out, err = _try_tool(*cmd)
    if rc == -1:
        return None
    text = (out or err).strip()
    if _looks_like_wsl_vsock_failure(text):
        return None
    return text.splitlines()[0] if text else "unknown"


def _collect_refs(obj: Any, refs: list[str]) -> None:
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == "$ref" and isinstance(v, str):
                refs.append(v)
            else:
                _collect_refs(v, refs)
    elif isinstance(obj, list):
        for item in obj:
            _collect_refs(item, refs)




# ── Gate implementations ──────────────────────────────────────────────────────

def _g1_path_canonicality(root: pathlib.Path) -> dict:
    t0 = time.monotonic()
    gate_id = "PATH_CANONICALITY_GATE"
    checked: list[str] = []
    violations: list[dict] = []
    openapi_canonical = root / "contracts" / "openapi" / "openapi.yaml"
    checked.append(str(openapi_canonical))
    if not openapi_canonical.exists():
        violations.append({
            "blocking_code": "BLOCKED_MISSING_CANONICAL_PATH",
            "artifact": str(openapi_canonical),
            "message": "contracts/openapi/openapi.yaml não encontrado.",
            "severity": "error",
        })
    else:
        # Only scan contracts/ — avoids node_modules and other large trees
        contracts_dir = root / "contracts"
        if contracts_dir.exists():
            for p in contracts_dir.rglob("openapi.yaml"):
                try:
                    rel = p.relative_to(root)
                except ValueError:
                    continue
                if str(rel).replace("\\", "/") != "contracts/openapi/openapi.yaml":
                    violations.append({
                        "blocking_code": "BLOCKED_MISSING_CANONICAL_PATH",
                        "artifact": str(rel),
                        "message": f"openapi.yaml fora do path canônico: {rel}",
                        "severity": "warn",
                    })
    asyncapi_canonical = root / "contracts" / "asyncapi" / "asyncapi.yaml"
    checked.append(str(asyncapi_canonical))

    for report_dir in sorted(root.rglob("_reports")):
        if not report_dir.is_dir():
            continue
        try:
            rel = report_dir.relative_to(root)
        except ValueError:
            continue
        if rel == pathlib.Path("_reports"):
            continue
        if any(part.startswith(".") for part in rel.parts):
            continue
        checked.append(str(report_dir))
        violations.append({
            "blocking_code": BLOCKED_LAYOUT_NONCOMPLIANCE,
            "artifact": str(rel).replace("\\", "/") + "/",
            "message": "Diretório `_reports` fora da raiz canônica é proibido.",
            "severity": "error",
        })

    # Canonical module-aware layout checks (SSOT = MODULE_REGISTRY.yaml)
    modules = _load_canonical_modules_from_layout(root)
    if not modules:
        violations.append({
            "blocking_code": BLOCKED_LAYOUT_NONCOMPLIANCE,
            "artifact": "docs/_canon/MODULE_REGISTRY.yaml",
            "message": "Não foi possível carregar a taxonomia canônica de módulos de MODULE_REGISTRY.yaml.",
            "severity": "error",
        })
    else:
        paths_dir = root / "contracts" / "openapi" / "paths"
        checked.append(str(paths_dir))
        if paths_dir.exists():
            expected_paths = {f"{m}.yaml" for m in modules}
            actual_paths = {p.name for p in paths_dir.glob("*.yaml") if p.is_file()}
            missing = sorted(expected_paths - actual_paths)
            extra = sorted(actual_paths - expected_paths)
            for name in missing:
                violations.append({
                    "blocking_code": BLOCKED_LAYOUT_NONCOMPLIANCE,
                    "artifact": f"contracts/openapi/paths/{name}",
                    "message": "Path file obrigatório ausente para módulo canônico.",
                    "severity": "error",
                })
            for name in extra:
                violations.append({
                    "blocking_code": BLOCKED_LAYOUT_NONCOMPLIANCE,
                    "artifact": f"contracts/openapi/paths/{name}",
                    "message": "Path file existe para módulo não-canônico (fora da taxonomia).",
                    "severity": "error",
                })
        else:
            violations.append({
                "blocking_code": BLOCKED_LAYOUT_NONCOMPLIANCE,
                "artifact": "contracts/openapi/paths/",
                "message": "Diretório obrigatório ausente: contracts/openapi/paths/",
                "severity": "error",
            })

        def _check_module_dirs(base_rel: str, allow_extra: set[str] | None = None) -> None:
            base = root / base_rel
            checked.append(str(base))
            if not base.exists():
                violations.append({
                    "blocking_code": BLOCKED_LAYOUT_NONCOMPLIANCE,
                    "artifact": base_rel + "/",
                    "message": f"Diretório obrigatório ausente: {base_rel}/",
                    "severity": "error",
                })
                return
            expected = set(modules)
            if allow_extra:
                expected |= set(allow_extra)
            actual = {p.name for p in base.iterdir() if p.is_dir()}
            missing_dirs = sorted(set(modules) - actual)
            extra_dirs = sorted(actual - expected)
            for d in missing_dirs:
                violations.append({
                    "blocking_code": BLOCKED_LAYOUT_NONCOMPLIANCE,
                    "artifact": f"{base_rel}/{d}/",
                    "message": "Diretório de módulo canônico ausente.",
                    "severity": "error",
                })
            for d in extra_dirs:
                violations.append({
                    "blocking_code": BLOCKED_LAYOUT_NONCOMPLIANCE,
                    "artifact": f"{base_rel}/{d}/",
                    "message": "Diretório existe para módulo não-canônico (fora da taxonomia).",
                    "severity": "error",
                })

        _check_module_dirs("contracts/schemas", allow_extra={"shared"})
        _check_module_dirs("contracts/workflows", allow_extra={"_global"})
        _check_module_dirs("contracts/openapi/components/schemas", allow_extra={"shared", "common"})

        # Naming validation (best-effort) for known contract surfaces
        schema_root = root / "contracts" / "schemas"
        if schema_root.exists():
            for mod in modules:
                mod_dir = schema_root / mod
                if not mod_dir.exists():
                    continue
                for p in sorted(mod_dir.glob("*.json")):
                    if not p.name.endswith(".schema.json"):
                        violations.append({
                            "blocking_code": BLOCKED_LAYOUT_NONCOMPLIANCE,
                            "artifact": str(p.relative_to(root)),
                            "message": "JSON Schema filename deve terminar em `.schema.json`.",
                            "severity": "warn",
                        })

        wf_root = root / "contracts" / "workflows"
        if wf_root.exists():
            for mod in modules:
                mod_dir = wf_root / mod
                if not mod_dir.exists():
                    continue
                for p in sorted(mod_dir.glob("*.y*ml")):
                    if ".arazzo." not in p.name:
                        violations.append({
                            "blocking_code": BLOCKED_LAYOUT_NONCOMPLIANCE,
                            "artifact": str(p.relative_to(root)),
                            "message": "Workflow filename deve terminar em `.arazzo.yaml`.",
                            "severity": "warn",
                        })

    if violations:
        primary = violations[0]["blocking_code"]
        return _pg(gate_id, "FAIL", True, primary,
                   f"{len(violations)} problema(s) de path/layout canônico.",
                   [], checked, [], violations, _ms(t0))
    return _pg(gate_id, "PASS", True, None,
               "Paths/layout canônicos corretos.", [], checked, [], [], _ms(t0))


def _g2_required_artifact_presence(root: pathlib.Path) -> dict:
    t0 = time.monotonic()
    gate_id = "REQUIRED_ARTIFACT_PRESENCE_GATE"
    missing: list[str] = []
    checked: list[str] = []
    for rel in _CANONICAL_GLOBAL_DOCS:
        p = root / rel
        checked.append(str(p))
        if not p.exists():
            missing.append(rel)
    # Module minimum docs (per RULES + operational plan)
    modules = _load_canonical_modules_from_layout(root)
    module_required_items: list[str] = []
    if modules:
        for mod in modules:
            up = mod.upper()
            module_required_items.extend([
                f"docs/hbtrack/modulos/{mod}/README.md",
                f"docs/hbtrack/modulos/{mod}/MODULE_SCOPE_{up}.md",
                f"docs/hbtrack/modulos/{mod}/DOMAIN_RULES_{up}.md",
                f"docs/hbtrack/modulos/{mod}/INVARIANTS_{up}.md",
                f"docs/hbtrack/modulos/{mod}/TEST_MATRIX_{up}.md",
                f"contracts/openapi/paths/{mod}.yaml",
            ])
            schema_dir = root / "contracts" / "schemas" / mod
            checked.append(str(schema_dir))
            if not schema_dir.exists() or not any(schema_dir.glob("*.schema.json")):
                missing.append(f"contracts/schemas/{mod}/*.schema.json")
    for rel in module_required_items:
        p = root / rel
        checked.append(str(p))
        if not p.exists():
            missing.append(rel)
    if missing:
        violations = []
        for m in missing:
            if m.startswith("docs/hbtrack/modulos/"):
                code = BLOCKED_MISSING_MODULE_DOC
            elif m.startswith("contracts/openapi/paths/"):
                code = "BLOCKED_MISSING_OPENAPI_PATH"
            elif m.startswith("contracts/schemas/"):
                code = "BLOCKED_MISSING_SCHEMA"
            else:
                code = "BLOCKED_MISSING_REQUIRED_ARTIFACT"
            violations.append({
                "blocking_code": code,
                "artifact": m,
                "message": f"Artefato obrigatório ausente: {m}",
                "severity": "error",
            })
        first_code = violations[0]["blocking_code"]
        return _pg(gate_id, "FAIL", True, first_code,
                   f"{len(missing)} artefato(s) obrigatório(s) ausente(s).",
                   [], checked, [], violations, _ms(t0))
    total_required = len(_CANONICAL_GLOBAL_DOCS) + len(module_required_items) + (len(modules) if modules else 0)
    return _pg(gate_id, "PASS", True, None,
               f"Todos os {total_required} artefatos obrigatórios presentes.",
               [], checked, [], [], _ms(t0))


def _g2a_module_doc_crossrefs(root: pathlib.Path) -> dict:
    t0 = time.monotonic()
    gate_id = "MODULE_DOC_CROSSREF_GATE"
    violations: list[dict] = []
    checked: list[str] = []
    modules = _load_canonical_modules_from_layout(root)
    if not modules:
        return _skip(gate_id, "Taxonomia canônica ausente — gate não aplicável.", _ms(t0))
    policy = _load_module_doc_header_policy(root)
    if not policy:
        return _skip(gate_id, "MODULE_DOC_HEADER_POLICY ausente ou inválido — gate não aplicável.", _ms(t0))
    types = policy.get("types")
    base = policy.get("base")
    if not isinstance(types, dict) or not isinstance(base, dict):
        return _skip(gate_id, "MODULE_DOC_HEADER_POLICY incompleto — gate não aplicável.", _ms(t0))

    module_files: list[tuple[pathlib.Path, str]] = []
    for mod in modules:
        module_dir = root / "docs" / "hbtrack" / "modulos" / mod
        if not module_dir.exists():
            continue
        for p in sorted(module_dir.glob("*.md")):
            inferred_type = _infer_module_doc_type(p, mod, policy)
            if inferred_type:
                module_files.append((p, inferred_type))

    for p, inferred_type in module_files:
        checked.append(str(p))
        hdr = _parse_yaml_front_matter(p)
        if not hdr:
            violations.append({
                "blocking_code": BLOCKED_INVALID_MODULE_DOC_HEADER,
                "artifact": str(p.relative_to(root)),
                "message": "Header YAML obrigatório ausente ou inválido (esperado YAML front matter).",
                "severity": "error",
            })
            continue

        mod = p.parent.name
        cfg = types.get(inferred_type) or {}
        if not isinstance(cfg, dict):
            continue
        allow_missing_type = bool(cfg.get("allow_missing_type"))
        declared_type = hdr.get("type")
        if declared_type is not None and declared_type != inferred_type:
            violations.append({
                "blocking_code": BLOCKED_INVALID_MODULE_DOC_HEADER,
                "artifact": str(p.relative_to(root)),
                "message": f"Header `type` divergente: esperado `{inferred_type}`.",
                "severity": "error",
            })
        if declared_type is None and not allow_missing_type:
            violations.append({
                "blocking_code": BLOCKED_INVALID_MODULE_DOC_HEADER,
                "artifact": str(p.relative_to(root)),
                "message": "Header `type` obrigatório ausente para doc condicional.",
                "severity": "error",
            })
        elif declared_type is not None and not isinstance(declared_type, str):
            violations.append({
                "blocking_code": BLOCKED_INVALID_MODULE_DOC_HEADER,
                "artifact": str(p.relative_to(root)),
                "message": "Header `type` deve ser string.",
                "severity": "error",
            })

        if hdr.get("module") != mod:
            violations.append({
                "blocking_code": BLOCKED_INVALID_MODULE_DOC_HEADER,
                "artifact": str(p.relative_to(root)),
                "message": "Header `module` não corresponde ao diretório do módulo.",
                "severity": "error",
            })

        base_required = [k for k in (base.get("required") or []) if isinstance(k, str)]
        base_optional = [k for k in (base.get("optional") or []) if isinstance(k, str)]
        type_required = [k for k in (cfg.get("required") or []) if isinstance(k, str)]
        type_optional = [k for k in (cfg.get("optional") or []) if isinstance(k, str)]
        allowed_keys = set(base_required + base_optional + type_required + type_optional)
        if allow_missing_type and "type" in allowed_keys:
            allowed_keys.add("type")

        for key in base_required + type_required:
            if key not in hdr:
                violations.append({
                    "blocking_code": BLOCKED_INVALID_MODULE_DOC_HEADER,
                    "artifact": str(p.relative_to(root)),
                    "message": f"Header YAML obrigatório ausente: {key}",
                    "severity": "error",
                })

        if "handball_semantic_applicability" in hdr and not isinstance(hdr.get("handball_semantic_applicability"), bool):
            violations.append({
                "blocking_code": BLOCKED_INVALID_MODULE_DOC_HEADER,
                "artifact": str(p.relative_to(root)),
                "message": "Header `handball_semantic_applicability` deve ser boolean.",
                "severity": "error",
            })
        for key in ("updated", "updated_at"):
            if key in hdr and not isinstance(hdr.get(key), str):
                violations.append({
                    "blocking_code": BLOCKED_INVALID_MODULE_DOC_HEADER,
                    "artifact": str(p.relative_to(root)),
                    "message": f"Header `{key}` deve ser string ISO/date-like.",
                    "severity": "error",
                })
        if "adr_refs" in hdr and not (
            isinstance(hdr.get("adr_refs"), list) and all(isinstance(v, str) for v in hdr.get("adr_refs"))
        ):
            violations.append({
                "blocking_code": BLOCKED_INVALID_MODULE_DOC_HEADER,
                "artifact": str(p.relative_to(root)),
                "message": "Header `adr_refs` deve ser lista de strings.",
                "severity": "error",
            })

        unknown_keys = sorted(k for k in hdr.keys() if k not in allowed_keys)
        for key in unknown_keys:
            violations.append({
                "blocking_code": BLOCKED_INVALID_MODULE_DOC_HEADER,
                "artifact": str(p.relative_to(root)),
                "message": f"Header `{key}` não está registrado no policy do tipo `{inferred_type}`.",
                "severity": "error",
            })

        for field, value in hdr.items():
            if not field.endswith("_ref"):
                continue
            expected = _module_doc_expected_target(root, mod, field)
            if expected is None:
                continue
            expected_abs, expect_dir = expected
            if not isinstance(value, str) or not value.strip():
                continue
            target = (p.parent / value).resolve()
            if target != expected_abs.resolve():
                violations.append({
                    "blocking_code": BLOCKED_INVALID_MODULE_DOC_HEADER,
                    "artifact": str(p.relative_to(root)),
                    "message": f"Header `{field}` não aponta para o path canônico esperado.",
                    "severity": "error",
                })
                continue
            if expect_dir and not target.is_dir():
                violations.append({
                    "blocking_code": BLOCKED_INVALID_MODULE_DOC_HEADER,
                    "artifact": str(p.relative_to(root)),
                    "message": f"Header `{field}` aponta para diretório inexistente.",
                    "severity": "error",
                })
            if (not expect_dir) and not target.exists():
                violations.append({
                    "blocking_code": BLOCKED_INVALID_MODULE_DOC_HEADER,
                    "artifact": str(p.relative_to(root)),
                    "message": f"Header `{field}` aponta para arquivo inexistente.",
                    "severity": "error",
                })

    if violations:
        return _pg(gate_id, "FAIL", True, BLOCKED_INVALID_MODULE_DOC_HEADER,
                   f"{len(violations)} problema(s) de cross-reference em docs de módulo.",
                   [], checked, [], violations, _ms(t0))
    return _pg(gate_id, "PASS", True, None,
               "Headers e cross-references de docs de módulo OK.", [], checked, [], [], _ms(t0))


def _g2b_api_normative_duplication(root: pathlib.Path) -> dict:
    t0 = time.monotonic()
    gate_id = "API_NORMATIVE_DUPLICATION_GATE"
    violations: list[dict] = []
    checked: list[str] = []
    canon_dir = root / "docs" / "_canon"
    if not canon_dir.exists():
        return _skip(gate_id, "docs/_canon ausente — gate não aplicável.", _ms(t0))

    # Heurística determinística: se um doc do canon menciona convenções/shape HTTP e
    # não aponta a SSOT (`.contract_driven/templates/api/api_rules.yaml`), sinaliza.
    api_markers = [
        "application/problem+json",
        "RFC 7807",
        "Problem Details",
        "pageSize",
        "pageToken",
        "nextPageToken",
        "HTTP Status",
        "status code",
    ]
    ssot_marker = ".contract_driven/templates/api/api_rules.yaml"
    exclude = {
        canon_dir / "CI_CONTRACT_GATES.md",
    }
    for p in sorted(canon_dir.rglob("*.md")):
        if "/decisions/" in str(p).replace("\\", "/"):
            continue
        if p in exclude:
            continue
        checked.append(str(p))
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        if not any(m in text for m in api_markers):
            continue
        if ssot_marker in text:
            continue
        violations.append({
            "blocking_code": WARN_API_NORMATIVE_OUTSIDE_SSOT,
            "artifact": str(p.relative_to(root)),
            "message": "Documento menciona convenção/shape HTTP mas não aponta a SSOT `.contract_driven/templates/api/api_rules.yaml` (risco de duplicação normativa).",
            "severity": "warn",
        })
    if violations:
        return _pg(gate_id, "FAIL", False, WARN_API_NORMATIVE_OUTSIDE_SSOT,
                   f"{len(violations)} doc(s) do canon com risco de duplicação normativa de API.",
                   [], checked, [], violations, _ms(t0))
    return _pg(gate_id, "PASS", False, None,
               "Sem risco detectável de duplicação normativa de API no canon.", [], checked, [], [], _ms(t0))


def _g2c_owasp_api_control_matrix(root: pathlib.Path) -> dict:
    t0 = time.monotonic()
    gate_id = "OWASP_API_CONTROL_MATRIX_GATE"
    matrix_path = root / "docs" / "_canon" / "security" / "OWASP_API_CONTROL_MATRIX.yaml"
    schema_path = root / "contracts" / "schemas" / "shared" / "owasp_api_control_matrix.schema.json"

    checked = [str(matrix_path), str(schema_path)]
    if not matrix_path.exists():
        return _pg(
            gate_id,
            "FAIL",
            True,
            BLOCKED_OWASP_CONTROL_MATRIX_MISSING,
            "Matriz OWASP canônica ausente (artefato normativo obrigatório).",
            [],
            checked,
            [],
            [{
                "blocking_code": BLOCKED_OWASP_CONTROL_MATRIX_MISSING,
                "artifact": str(matrix_path.relative_to(root)),
                "message": "Arquivo obrigatório ausente.",
                "severity": "error",
            }],
            _ms(t0),
        )

    try:
        data = _load_yaml(matrix_path)
    except Exception as e:
        return _pg(
            gate_id,
            "FAIL",
            True,
            BLOCKED_OWASP_CONTROL_MATRIX_INVALID,
            "Matriz OWASP não é YAML parseável.",
            [],
            checked,
            [],
            [{
                "blocking_code": BLOCKED_OWASP_CONTROL_MATRIX_INVALID,
                "artifact": str(matrix_path.relative_to(root)),
                "message": f"Erro ao parsear YAML: {e}",
                "severity": "error",
            }],
            _ms(t0),
        )

    if not isinstance(data, dict):
        return _pg(
            gate_id,
            "FAIL",
            True,
            BLOCKED_OWASP_CONTROL_MATRIX_INVALID,
            "Matriz OWASP inválida: raiz deve ser objeto YAML.",
            [],
            checked,
            [],
            [{
                "blocking_code": BLOCKED_OWASP_CONTROL_MATRIX_INVALID,
                "artifact": str(matrix_path.relative_to(root)),
                "message": "Raiz do YAML deve ser um objeto (mapping).",
                "severity": "error",
            }],
            _ms(t0),
        )

    if not schema_path.exists():
        return _pg(
            gate_id,
            "FAIL",
            True,
            "ERROR_INFRA",
            "Schema da matriz OWASP ausente (infra).",
            [],
            checked,
            [],
            [{
                "blocking_code": "ERROR_INFRA",
                "artifact": str(schema_path.relative_to(root)),
                "message": "Schema obrigatório ausente.",
                "severity": "error",
            }],
            _ms(t0),
        )

    try:
        schema = _load_json(schema_path)
    except Exception as e:
        return _pg(
            gate_id,
            "FAIL",
            True,
            "ERROR_INFRA",
            "Schema da matriz OWASP inválido (infra).",
            [],
            checked,
            [],
            [{
                "blocking_code": "ERROR_INFRA",
                "artifact": str(schema_path.relative_to(root)),
                "message": f"Erro ao carregar schema: {e}",
                "severity": "error",
            }],
            _ms(t0),
        )

    schema_violations = validate_against_json_schema(data, schema)
    violations: list[dict] = []
    for v in schema_violations:
        violations.append({
            "blocking_code": BLOCKED_OWASP_CONTROL_MATRIX_INVALID,
            "artifact": str(matrix_path.relative_to(root)),
            "message": f"{v.get('path')}: {v.get('message')}",
            "severity": v.get("severity", "error"),
            "details": {k: v.get(k) for k in ("code", "path") if k in v},
        })

    controls = data.get("control_matrix")
    if isinstance(controls, list):
        ids = [c.get("control_id") for c in controls if isinstance(c, dict)]
        seen: set[str] = set()
        dups: list[str] = []
        for cid in ids:
            if not isinstance(cid, str) or not cid:
                continue
            if cid in seen:
                dups.append(cid)
            seen.add(cid)
        if dups:
            violations.append({
                "blocking_code": BLOCKED_OWASP_CONTROL_MATRIX_INVALID,
                "artifact": str(matrix_path.relative_to(root)),
                "message": "control_id duplicado(s) na matriz OWASP.",
                "severity": "error",
                "details": {"duplicates": sorted(set(dups))},
            })

    canonical_modules = _load_canonical_modules_from_layout(root)
    applies_to = data.get("applies_to")
    if canonical_modules and isinstance(applies_to, list):
        applies = [x for x in applies_to if isinstance(x, str)]
        missing = sorted([m for m in canonical_modules if m not in set(applies)])
        extra = sorted([m for m in applies if m not in set(canonical_modules)])
        if missing or extra:
            violations.append({
                "blocking_code": BLOCKED_OWASP_CONTROL_MATRIX_INVALID,
                "artifact": str(matrix_path.relative_to(root)),
                "message": "applies_to não alinha com a taxonomia canônica de módulos (MODULE_REGISTRY.yaml).",
                "severity": "error",
                "details": {"missing": missing, "extra": extra},
            })

    if violations:
        return _pg(
            gate_id,
            "FAIL",
            True,
            BLOCKED_OWASP_CONTROL_MATRIX_INVALID,
            f"Matriz OWASP inválida: {len(violations)} violação(ões).",
            [],
            checked,
            [],
            violations,
            _ms(t0),
        )

    return _pg(
        gate_id,
        "PASS",
        True,
        None,
        "Matriz OWASP presente, parseável e válida contra schema.",
        [],
        checked,
        [],
        [],
        _ms(t0),
    )


def _load_module_source_authority_matrix(root: pathlib.Path) -> tuple[dict | None, dict | None, list[str]]:
    matrix_path = root / "docs" / "_canon" / "MODULE_SOURCE_AUTHORITY_MATRIX.yaml"
    schema_path = root / "contracts" / "schemas" / "shared" / "module_source_authority_matrix.schema.json"
    checked = [str(matrix_path), str(schema_path)]
    if not matrix_path.exists():
        return None, None, checked
    try:
        data = _load_yaml(matrix_path)
    except Exception:
        return None, None, checked
    if not isinstance(data, dict):
        return None, None, checked
    if not schema_path.exists():
        return data, None, checked
    try:
        schema = _load_json(schema_path)
    except Exception:
        return data, None, checked
    return data, schema, checked


def _load_module_registry(root: pathlib.Path) -> tuple[dict | None, dict | None, list[str]]:
    registry_path = root / "docs" / "_canon" / "MODULE_REGISTRY.yaml"
    schema_path = root / "contracts" / "schemas" / "shared" / "module_registry.schema.json"
    checked = [str(registry_path), str(schema_path)]
    if not registry_path.exists():
        return None, None, checked
    try:
        data = _load_yaml(registry_path)
    except Exception:
        return None, None, checked
    if not isinstance(data, dict):
        return None, None, checked
    if not schema_path.exists():
        return data, None, checked
    try:
        schema = _load_json(schema_path)
    except Exception:
        return data, None, checked
    return data, schema, checked


_MODULE_STATUS_ALIASES = {
    "draft": "draft_contract",
    "validated": "validated_contract",
}


def _normalize_module_registry_status(status: Any) -> Any:
    if not isinstance(status, str):
        return status
    return _MODULE_STATUS_ALIASES.get(status, status)


def _load_module_registry_entries(root: pathlib.Path) -> tuple[dict[str, dict] | None, list[str]]:
    data, _, checked = _load_module_registry(root)
    if not isinstance(data, dict):
        return None, checked
    modules_obj = data.get("modules")
    if not isinstance(modules_obj, dict):
        return None, checked
    out: dict[str, dict] = {}
    for module, entry in modules_obj.items():
        if isinstance(module, str) and isinstance(entry, dict):
            normalized = dict(entry)
            normalized["status"] = _normalize_module_registry_status(entry.get("status"))
            out[module] = normalized
    return out, checked


def _g2d_module_source_authority_matrix(root: pathlib.Path) -> dict:
    t0 = time.monotonic()
    gate_id = "MODULE_SOURCE_AUTHORITY_MATRIX_GATE"
    matrix_path = root / "docs" / "_canon" / "MODULE_SOURCE_AUTHORITY_MATRIX.yaml"
    schema_path = root / "contracts" / "schemas" / "shared" / "module_source_authority_matrix.schema.json"
    checked = [str(matrix_path), str(schema_path)]

    if not matrix_path.exists():
        return _pg(
            gate_id,
            "FAIL",
            True,
            BLOCKED_MODULE_SOURCE_AUTHORITY_MATRIX_MISSING,
            "Matriz canônica de fontes/autoridade por módulo ausente (artefato normativo obrigatório).",
            [],
            checked,
            [],
            [{
                "blocking_code": BLOCKED_MODULE_SOURCE_AUTHORITY_MATRIX_MISSING,
                "artifact": str(matrix_path.relative_to(root)),
                "message": "Arquivo obrigatório ausente.",
                "severity": "error",
            }],
            _ms(t0),
        )

    try:
        data = _load_yaml(matrix_path)
    except Exception as e:
        return _pg(
            gate_id,
            "FAIL",
            True,
            BLOCKED_MODULE_SOURCE_AUTHORITY_MATRIX_INVALID,
            "Matriz de fontes/autoridade não é YAML parseável.",
            [],
            checked,
            [],
            [{
                "blocking_code": BLOCKED_MODULE_SOURCE_AUTHORITY_MATRIX_INVALID,
                "artifact": str(matrix_path.relative_to(root)),
                "message": f"Erro ao parsear YAML: {e}",
                "severity": "error",
            }],
            _ms(t0),
        )

    if not isinstance(data, dict):
        return _pg(
            gate_id,
            "FAIL",
            True,
            BLOCKED_MODULE_SOURCE_AUTHORITY_MATRIX_INVALID,
            "Matriz inválida: raiz deve ser objeto YAML.",
            [],
            checked,
            [],
            [{
                "blocking_code": BLOCKED_MODULE_SOURCE_AUTHORITY_MATRIX_INVALID,
                "artifact": str(matrix_path.relative_to(root)),
                "message": "Raiz do YAML deve ser um objeto (mapping).",
                "severity": "error",
            }],
            _ms(t0),
        )

    if not schema_path.exists():
        return _pg(
            gate_id,
            "FAIL",
            True,
            "ERROR_INFRA",
            "Schema da matriz de fontes/autoridade ausente (infra).",
            [],
            checked,
            [],
            [{
                "blocking_code": "ERROR_INFRA",
                "artifact": str(schema_path.relative_to(root)),
                "message": "Schema obrigatório ausente.",
                "severity": "error",
            }],
            _ms(t0),
        )

    try:
        schema = _load_json(schema_path)
    except Exception as e:
        return _pg(
            gate_id,
            "FAIL",
            True,
            "ERROR_INFRA",
            "Schema da matriz de fontes/autoridade inválido (infra).",
            [],
            checked,
            [],
            [{
                "blocking_code": "ERROR_INFRA",
                "artifact": str(schema_path.relative_to(root)),
                "message": f"Erro ao carregar schema: {e}",
                "severity": "error",
            }],
            _ms(t0),
        )

    schema_violations = validate_against_json_schema(data, schema)
    violations: list[dict] = []
    for v in schema_violations:
        violations.append({
            "blocking_code": BLOCKED_MODULE_SOURCE_AUTHORITY_MATRIX_INVALID,
            "artifact": str(matrix_path.relative_to(root)),
            "message": f"{v.get('path')}: {v.get('message')}",
            "severity": v.get("severity", "error"),
            "details": {k: v.get(k) for k in ("code", "path") if k in v},
        })

    canonical_modules = _load_canonical_modules_from_layout(root)
    modules_obj = data.get("modules")
    if canonical_modules and isinstance(modules_obj, dict):
        declared = sorted([k for k in modules_obj.keys() if isinstance(k, str)])
        missing = sorted([m for m in canonical_modules if m not in set(declared)])
        extra = sorted([m for m in declared if m not in set(canonical_modules)])
        if missing or extra:
            violations.append({
                "blocking_code": BLOCKED_MODULE_SOURCE_AUTHORITY_MATRIX_INVALID,
                "artifact": str(matrix_path.relative_to(root)),
                "message": "modules não alinha com a taxonomia canônica de módulos.",
                "severity": "error",
                "details": {"missing": missing, "extra": extra},
            })

    if violations:
        return _pg(
            gate_id,
            "FAIL",
            True,
            BLOCKED_MODULE_SOURCE_AUTHORITY_MATRIX_INVALID,
            f"Matriz inválida: {len(violations)} violação(ões).",
            [],
            checked,
            [],
            violations,
            _ms(t0),
        )

    return _pg(
        gate_id,
        "PASS",
        True,
        None,
        "Matriz de fontes/autoridade presente e válida contra schema.",
        [],
        checked,
        [],
        [],
        _ms(t0),
    )


def _g2d1_module_registry(root: pathlib.Path) -> dict:
    t0 = time.monotonic()
    gate_id = "MODULE_REGISTRY_GATE"
    registry_path = root / "docs" / "_canon" / "MODULE_REGISTRY.yaml"
    schema_path = root / "contracts" / "schemas" / "shared" / "module_registry.schema.json"
    checked = [str(registry_path), str(schema_path)]

    if not registry_path.exists():
        return _pg(
            gate_id,
            "FAIL",
            True,
            BLOCKED_MODULE_REGISTRY_MISSING,
            "Registry canônico de módulos ausente (artefato normativo obrigatório).",
            [],
            checked,
            [],
            [{
                "blocking_code": BLOCKED_MODULE_REGISTRY_MISSING,
                "artifact": str(registry_path.relative_to(root)),
                "message": "Arquivo obrigatório ausente.",
                "severity": "error",
            }],
            _ms(t0),
        )

    try:
        data = _load_yaml(registry_path)
    except Exception as e:
        return _pg(
            gate_id,
            "FAIL",
            True,
            BLOCKED_MODULE_REGISTRY_INVALID,
            "Registry de módulos não é YAML parseável.",
            [],
            checked,
            [],
            [{
                "blocking_code": BLOCKED_MODULE_REGISTRY_INVALID,
                "artifact": str(registry_path.relative_to(root)),
                "message": f"Erro ao parsear YAML: {e}",
                "severity": "error",
            }],
            _ms(t0),
        )

    if not isinstance(data, dict):
        return _pg(
            gate_id,
            "FAIL",
            True,
            BLOCKED_MODULE_REGISTRY_INVALID,
            "Registry inválido: raiz deve ser objeto YAML.",
            [],
            checked,
            [],
            [{
                "blocking_code": BLOCKED_MODULE_REGISTRY_INVALID,
                "artifact": str(registry_path.relative_to(root)),
                "message": "Raiz do YAML deve ser um objeto (mapping).",
                "severity": "error",
            }],
            _ms(t0),
        )

    if not schema_path.exists():
        return _pg(
            gate_id,
            "FAIL",
            True,
            "ERROR_INFRA",
            "Schema do MODULE_REGISTRY ausente (infra).",
            [],
            checked,
            [],
            [{
                "blocking_code": "ERROR_INFRA",
                "artifact": str(schema_path.relative_to(root)),
                "message": "Schema obrigatório ausente.",
                "severity": "error",
            }],
            _ms(t0),
        )

    try:
        schema = _load_json(schema_path)
    except Exception as e:
        return _pg(
            gate_id,
            "FAIL",
            True,
            "ERROR_INFRA",
            "Schema do MODULE_REGISTRY inválido (infra).",
            [],
            checked,
            [],
            [{
                "blocking_code": "ERROR_INFRA",
                "artifact": str(schema_path.relative_to(root)),
                "message": f"Erro ao carregar schema: {e}",
                "severity": "error",
            }],
            _ms(t0),
        )

    schema_violations = validate_against_json_schema(data, schema)
    violations: list[dict] = []
    for v in schema_violations:
        violations.append({
            "blocking_code": BLOCKED_MODULE_REGISTRY_INVALID,
            "artifact": str(registry_path.relative_to(root)),
            "message": f"{v.get('path')}: {v.get('message')}",
            "severity": v.get("severity", "error"),
            "details": {k: v.get(k) for k in ("code", "path") if k in v},
        })

    canonical_modules = _load_canonical_modules_from_layout(root)
    modules_obj = data.get("modules")
    if canonical_modules and isinstance(modules_obj, dict):
        declared = sorted([k for k in modules_obj.keys() if isinstance(k, str)])
        missing = sorted([m for m in canonical_modules if m not in set(declared)])
        extra = sorted([m for m in declared if m not in set(canonical_modules)])
        if missing or extra:
            violations.append({
                "blocking_code": BLOCKED_MODULE_REGISTRY_INVALID,
                "artifact": str(registry_path.relative_to(root)),
                "message": "modules não alinha com a taxonomia canônica de módulos.",
                "severity": "error",
                "details": {"missing": missing, "extra": extra},
            })

    if violations:
        return _pg(
            gate_id,
            "FAIL",
            True,
            BLOCKED_MODULE_REGISTRY_INVALID,
            f"MODULE_REGISTRY inválido: {len(violations)} violação(ões).",
            [],
            checked,
            [],
            violations,
            _ms(t0),
        )

    return _pg(
        gate_id,
        "PASS",
        True,
        None,
        "MODULE_REGISTRY presente e válido contra schema.",
        [],
        checked,
        [],
        [],
        _ms(t0),
    )


def _collect_property_names(obj: Any, out: set[str]) -> None:
    if isinstance(obj, dict):
        props = obj.get("properties")
        if isinstance(props, dict):
            for k in props.keys():
                if isinstance(k, str):
                    out.add(k)
        for v in obj.values():
            _collect_property_names(v, out)
    elif isinstance(obj, list):
        for v in obj:
            _collect_property_names(v, out)


def _load_yaml_or_empty(path: pathlib.Path) -> Any:
    try:
        return _load_yaml(path)
    except Exception:
        return None


def _module_openapi_has_paths(root: pathlib.Path, module: str) -> bool:
    p = root / "contracts" / "openapi" / "paths" / f"{module}.yaml"
    if not p.exists():
        return False
    obj = _load_yaml_or_empty(p)
    if not isinstance(obj, dict):
        return False
    return any(isinstance(k, str) and k.startswith("/") for k in obj.keys())


def _module_contract_property_names(root: pathlib.Path, module: str) -> set[str]:
    names: set[str] = set()
    # OpenAPI components schemas (YAML)
    comp_dir = root / "contracts" / "openapi" / "components" / "schemas" / module
    if comp_dir.exists():
        for p in sorted(comp_dir.rglob("*.y*ml")):
            obj = _load_yaml_or_empty(p)
            _collect_property_names(obj, names)
    # OpenAPI path file (YAML)
    path_file = root / "contracts" / "openapi" / "paths" / f"{module}.yaml"
    if path_file.exists():
        obj = _load_yaml_or_empty(path_file)
        _collect_property_names(obj, names)
    # JSON Schemas (JSON)
    schema_dir = root / "contracts" / "schemas" / module
    if schema_dir.exists():
        for p in sorted(schema_dir.glob("*.json")):
            try:
                data = _load_json(p)
            except Exception:
                continue
            _collect_property_names(data, names)
    return names


def _module_openapi_paths(root: pathlib.Path, module: str) -> list[str]:
    p = root / "contracts" / "openapi" / "paths" / f"{module}.yaml"
    obj = _load_yaml_or_empty(p)
    if not isinstance(obj, dict):
        return []
    return [k for k in obj.keys() if isinstance(k, str) and k.startswith("/")]


def _openapi_root_module_refs(root: pathlib.Path) -> tuple[dict[str, set[str]], list[dict], list[str]]:
    openapi_root = root / "contracts" / "openapi" / "openapi.yaml"
    checked = [str(openapi_root)]
    obj = _load_yaml_or_empty(openapi_root)
    if not isinstance(obj, dict):
        return {}, [], checked
    paths_obj = obj.get("paths")
    if not isinstance(paths_obj, dict):
        return {}, [], checked

    ref_map: dict[str, set[str]] = {}
    violations: list[dict] = []
    for path_key, path_item in paths_obj.items():
        if not isinstance(path_key, str) or not path_key.startswith("/"):
            continue
        if not isinstance(path_item, dict):
            violations.append({
                "blocking_code": BLOCKED_OPENAPI_ROOT_MODULE_SYNC,
                "artifact": str(openapi_root.relative_to(root)),
                "message": f"Path `{path_key}` no root OpenAPI deve ser objeto contendo $ref para módulo.",
                "severity": "error",
            })
            continue
        ref = path_item.get("$ref")
        if not isinstance(ref, str):
            violations.append({
                "blocking_code": BLOCKED_OPENAPI_ROOT_MODULE_SYNC,
                "artifact": str(openapi_root.relative_to(root)),
                "message": f"Path `{path_key}` no root OpenAPI deve delegar via $ref para contracts/openapi/paths/<module>.yaml.",
                "severity": "error",
            })
            continue
        m = re.match(r"^\./paths/([a-z0-9_]+)\.yaml#", ref)
        if not m:
            violations.append({
                "blocking_code": BLOCKED_OPENAPI_ROOT_MODULE_SYNC,
                "artifact": str(openapi_root.relative_to(root)),
                "message": f"$ref do path `{path_key}` não aponta para ./paths/<module>.yaml: {ref}",
                "severity": "error",
            })
            continue
        ref_map.setdefault(m.group(1), set()).add(path_key)
    return ref_map, violations, checked


def _parse_iso8601_utc(value: Any) -> datetime.datetime | None:
    if not isinstance(value, str) or not value.endswith("Z"):
        return None
    try:
        return datetime.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _load_agent_execution_log(path: pathlib.Path, root: pathlib.Path) -> tuple[dict | None, list[dict]]:
    try:
        data = _load_json(path)
    except Exception as e:
        return None, [{
            "blocking_code": BLOCKED_PRE_CONTRACT_EVIDENCE,
            "artifact": str(path.relative_to(root)),
            "message": f"Arquivo de evidência de pré-contrato não é JSON válido: {e}",
            "severity": "error",
        }]

    violations: list[dict] = []
    if not isinstance(data, dict):
        violations.append({
            "blocking_code": BLOCKED_PRE_CONTRACT_EVIDENCE,
            "artifact": str(path.relative_to(root)),
            "message": "Raiz do log de execução deve ser objeto JSON.",
            "severity": "error",
        })
        return None, violations

    for field in ("schemaVersion", "sessionId", "startedAt", "endedAt", "module", "taskType", "entries"):
        if field not in data:
            violations.append({
                "blocking_code": BLOCKED_PRE_CONTRACT_EVIDENCE,
                "artifact": str(path.relative_to(root)),
                "message": f"Campo obrigatório ausente no log: {field}",
                "severity": "error",
            })
    if violations:
        return None, violations

    if _parse_iso8601_utc(data.get("startedAt")) is None or _parse_iso8601_utc(data.get("endedAt")) is None:
        violations.append({
            "blocking_code": BLOCKED_PRE_CONTRACT_EVIDENCE,
            "artifact": str(path.relative_to(root)),
            "message": "startedAt/endedAt devem estar em ISO-8601 UTC (`...Z`).",
            "severity": "error",
        })
    if not isinstance(data.get("module"), str) or not data["module"]:
        violations.append({
            "blocking_code": BLOCKED_PRE_CONTRACT_EVIDENCE,
            "artifact": str(path.relative_to(root)),
            "message": "Campo `module` deve ser string não vazia.",
            "severity": "error",
        })
    evidence_mode = data.get("evidence_mode", "live_session")
    if evidence_mode not in {"live_session", "baseline_backfill"}:
        violations.append({
            "blocking_code": BLOCKED_PRE_CONTRACT_EVIDENCE,
            "artifact": str(path.relative_to(root)),
            "message": f"evidence_mode inválido: {evidence_mode!r}",
            "severity": "error",
        })
    if evidence_mode == "baseline_backfill":
        reconstructed_from = data.get("reconstructed_from")
        if not isinstance(reconstructed_from, list) or not reconstructed_from:
            violations.append({
                "blocking_code": BLOCKED_PRE_CONTRACT_EVIDENCE,
                "artifact": str(path.relative_to(root)),
                "message": "baseline_backfill exige `reconstructed_from` não vazio.",
                "severity": "error",
            })
    entries = data.get("entries")
    if not isinstance(entries, list) or not entries:
        violations.append({
            "blocking_code": BLOCKED_PRE_CONTRACT_EVIDENCE,
            "artifact": str(path.relative_to(root)),
            "message": "Campo `entries` deve ser lista não vazia.",
            "severity": "error",
        })
        return (None, violations) if violations else (data, [])

    allowed_phases = {"ROUTING", "FOUNDATION_CHECK", "DECISION_DISCOVERY", "DOMAIN_ASSEMBLY", "WORKER_HANDOFF"}
    allowed_results = {"PASS", "BLOCK", "SKIP", "HANDOFF"}
    for idx, entry in enumerate(entries):
        if not isinstance(entry, dict):
            violations.append({
                "blocking_code": BLOCKED_PRE_CONTRACT_EVIDENCE,
                "artifact": str(path.relative_to(root)),
                "message": f"entries[{idx}] deve ser objeto.",
                "severity": "error",
            })
            continue
        phase = entry.get("phase")
        result = entry.get("result")
        if phase not in allowed_phases:
            violations.append({
                "blocking_code": BLOCKED_PRE_CONTRACT_EVIDENCE,
                "artifact": str(path.relative_to(root)),
                "message": f"entries[{idx}].phase inválido: {phase!r}",
                "severity": "error",
            })
        if result not in allowed_results:
            violations.append({
                "blocking_code": BLOCKED_PRE_CONTRACT_EVIDENCE,
                "artifact": str(path.relative_to(root)),
                "message": f"entries[{idx}].result inválido: {result!r}",
                "severity": "error",
            })
        if _parse_iso8601_utc(entry.get("timestamp")) is None:
            violations.append({
                "blocking_code": BLOCKED_PRE_CONTRACT_EVIDENCE,
                "artifact": str(path.relative_to(root)),
                "message": f"entries[{idx}].timestamp deve estar em ISO-8601 UTC (`...Z`).",
                "severity": "error",
            })

    return (None, violations) if violations else (data, [])


def _load_decision_ir_runner(root: pathlib.Path):
    module_path = root / "scripts" / "contracts" / "validate" / "decision_ir_gate.py"
    spec = importlib.util.spec_from_file_location("hbtrack_decision_ir_gate", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Não foi possível carregar decision_ir_gate.py.")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    runner = getattr(mod, "run_decision_ir_gate", None)
    if runner is None:
        raise RuntimeError("decision_ir_gate.py não expõe `run_decision_ir_gate`.")
    return runner


def _load_structured_doc(path: pathlib.Path):
    if path.suffix == ".json":
        return _load_json(path)
    return _load_yaml(path)


def _canonical_decision_ir_path(root: pathlib.Path, module: str) -> pathlib.Path:
    return root / ".contract_driven" / "decisions" / f"DECISION_IR_{module.upper()}.yaml"


def _module_surface_present(root: pathlib.Path, module: str, surface: str) -> bool:
    module_dir = root / "docs" / "hbtrack" / "modulos" / module
    up = module.upper()
    if surface == "module_docs_minimum":
        return _module_minimum_docs_present(root, module)
    if surface == "openapi_sync":
        return (root / "contracts" / "openapi" / "paths" / f"{module}.yaml").exists()
    if surface == "json_schema":
        return _module_schema_count(root, module) > 0
    if surface == "test_matrix":
        return (module_dir / f"TEST_MATRIX_{up}.md").exists()
    if surface == "state_model":
        return (module_dir / f"STATE_MODEL_{up}.md").exists()
    if surface == "permissions":
        return (module_dir / f"PERMISSIONS_{up}.md").exists()
    if surface == "errors":
        return (module_dir / f"ERRORS_{up}.md").exists()
    if surface == "sport_science":
        return (module_dir / f"SPORT_SCIENCE_RULES_{up}.md").exists()
    if surface == "ui_contract":
        return (module_dir / f"UI_CONTRACT_{up}.md").exists()
    if surface == "asyncapi":
        return _module_asyncapi_artifact_count(root, module) > 0
    if surface == "arazzo":
        return _module_workflow_count(root, module) > 0
    if surface == "decision_ir":
        return _module_has_decision_ir(root, module)
    return False


def _g2e_boundary_users_identity_access(root: pathlib.Path) -> dict:
    t0 = time.monotonic()
    gate_id = "BOUNDARY_USERS_IDENTITY_ACCESS_GATE"
    data, _, checked = _load_module_source_authority_matrix(root)
    if data is None:
        return _skip(gate_id, "Matriz de fontes/autoridade ausente/ inválida — skipping boundary gate.", _ms(t0))

    cfg = ((data.get("derived_gates") or {}).get("boundary_users_identity_access") or {})
    users_forbidden = (cfg.get("users_forbidden") or {})
    ia_forbidden = (cfg.get("identity_access_forbidden") or {})
    forbidden_user_fields = [x for x in (users_forbidden.get("fields") or []) if isinstance(x, str)]
    forbidden_user_path_markers = [x for x in (users_forbidden.get("path_markers") or []) if isinstance(x, str)]
    forbidden_ia_fields = [x for x in (ia_forbidden.get("fields") or []) if isinstance(x, str)]

    violations: list[dict] = []

    users_names = _module_contract_property_names(root, "users")
    hit_users = sorted([f for f in forbidden_user_fields if f in users_names])
    if hit_users:
        violations.append({
            "blocking_code": BLOCKED_BOUNDARY_USERS_IDENTITY_ACCESS,
            "artifact": "contracts/* (users)",
            "message": "Campos de credencial/auth encontrados no boundary de `users` (proibido).",
            "severity": "error",
            "details": {"fields": hit_users},
        })
    users_paths = _module_openapi_paths(root, "users")
    hit_path = sorted([p for p in users_paths if any(m in p for m in forbidden_user_path_markers)])
    if hit_path:
        violations.append({
            "blocking_code": BLOCKED_BOUNDARY_USERS_IDENTITY_ACCESS,
            "artifact": "contracts/openapi/paths/users.yaml",
            "message": "Rotas de auth encontradas no módulo `users` (proibido).",
            "severity": "error",
            "details": {"paths": hit_path},
        })

    ia_names = _module_contract_property_names(root, "identity_access")
    hit_ia = sorted([f for f in forbidden_ia_fields if f in ia_names])
    if hit_ia:
        violations.append({
            "blocking_code": BLOCKED_BOUNDARY_USERS_IDENTITY_ACCESS,
            "artifact": "contracts/* (identity_access)",
            "message": "Campos de athlete/profile encontrados no boundary de `identity_access` (proibido).",
            "severity": "error",
            "details": {"fields": hit_ia},
        })

    if violations:
        return _pg(
            gate_id,
            "FAIL",
            True,
            BLOCKED_BOUNDARY_USERS_IDENTITY_ACCESS,
            f"{len(violations)} violação(ões) de boundary users vs identity_access.",
            [],
            checked,
            [],
            violations,
            _ms(t0),
        )
    return _pg(
        gate_id,
        "PASS",
        True,
        None,
        "Boundaries users vs identity_access OK.",
        [],
        checked,
        [],
        [],
        _ms(t0),
    )


def _g2f_wellness_medical_boundary(root: pathlib.Path) -> dict:
    t0 = time.monotonic()
    gate_id = "WELLNESS_MEDICAL_BOUNDARY_GATE"
    data, _, checked = _load_module_source_authority_matrix(root)
    if data is None:
        return _skip(gate_id, "Matriz de fontes/autoridade ausente/ inválida — skipping wellness/medical boundary gate.", _ms(t0))

    cfg = ((data.get("derived_gates") or {}).get("wellness_medical_boundary") or {})
    wellness_forbidden = (cfg.get("wellness_forbidden") or {})
    forbidden_fields = [x for x in (wellness_forbidden.get("fields") or []) if isinstance(x, str)]

    wellness_names = _module_contract_property_names(root, "wellness")
    hit = sorted([f for f in forbidden_fields if f in wellness_names])
    if hit:
        violations = [{
            "blocking_code": BLOCKED_WELLNESS_MEDICAL_BOUNDARY,
            "artifact": "contracts/* (wellness)",
            "message": "Campos clínicos proibidos encontrados em `wellness`.",
            "severity": "error",
            "details": {"fields": hit},
        }]
        return _pg(
            gate_id,
            "FAIL",
            True,
            BLOCKED_WELLNESS_MEDICAL_BOUNDARY,
            f"{len(hit)} campo(s) clínico(s) proibido(s) em wellness.",
            [],
            checked,
            [],
            violations,
            _ms(t0),
        )

    return _pg(
        gate_id,
        "PASS",
        True,
        None,
        "Boundary wellness vs medical OK (sem campos clínicos em wellness).",
        [],
        checked,
        [],
        [],
        _ms(t0),
    )


def _g2g_scout_taxonomy(root: pathlib.Path) -> dict:
    t0 = time.monotonic()
    gate_id = "SCOUT_TAXONOMY_GATE"
    data, _, checked = _load_module_source_authority_matrix(root)
    if data is None:
        return _skip(gate_id, "Matriz de fontes/autoridade ausente/ inválida — skipping scout taxonomy gate.", _ms(t0))

    cfg = ((data.get("derived_gates") or {}).get("scout_taxonomy") or {})
    triggers = [x for x in (cfg.get("trigger_fields") or []) if isinstance(x, str)]
    req = (cfg.get("required_taxonomy_artifact") or {})
    req_path = req.get("path") if isinstance(req, dict) else None

    scout_names = _module_contract_property_names(root, "scout")
    triggered = sorted([t for t in triggers if t in scout_names])
    if not triggered:
        return _pg(
            gate_id,
            "PASS",
            True,
            None,
            "Nenhum campo de taxonomia detectado em scout; gate não exige artefato.",
            [],
            checked,
            [],
            [],
            _ms(t0),
        )

    if not isinstance(req_path, str) or not req_path:
        return _pg(
            gate_id,
            "FAIL",
            True,
            BLOCKED_SCOUT_TAXONOMY,
            "Taxonomia de scout foi acionada mas o path canônico do artefato não está declarado na matriz.",
            [],
            checked,
            [],
            [{
                "blocking_code": BLOCKED_SCOUT_TAXONOMY,
                "artifact": "docs/_canon/MODULE_SOURCE_AUTHORITY_MATRIX.yaml",
                "message": "required_taxonomy_artifact.path ausente/ inválido.",
                "severity": "error",
                "details": {"triggered_fields": triggered},
            }],
            _ms(t0),
        )

    p = root / req_path
    if not p.exists():
        return _pg(
            gate_id,
            "FAIL",
            True,
            BLOCKED_SCOUT_TAXONOMY,
            "Taxonomia de scout acionada mas artefato canônico está ausente.",
            [],
            checked + [str(p)],
            [],
            [{
                "blocking_code": BLOCKED_SCOUT_TAXONOMY,
                "artifact": req_path,
                "message": "Artefato de taxonomia canônica ausente.",
                "severity": "error",
                "details": {"triggered_fields": triggered},
            }],
            _ms(t0),
        )

    return _pg(
        gate_id,
        "PASS",
        True,
        None,
        "Taxonomia de scout acionada e artefato canônico presente.",
        [],
        checked + [str(p)],
        [],
        [],
        _ms(t0),
    )


def _g2h_async_required_module(root: pathlib.Path) -> dict:
    t0 = time.monotonic()
    gate_id = "ASYNC_REQUIRED_MODULE_GATE"
    data, _, checked = _load_module_source_authority_matrix(root)
    if data is None:
        return _skip(gate_id, "Matriz de fontes/autoridade ausente/ inválida — skipping async required gate.", _ms(t0))

    cfg = ((data.get("derived_gates") or {}).get("async_required_module") or {})
    rules = cfg.get("rules")
    if not isinstance(rules, list):
        return _skip(gate_id, "Regras async_required_module ausentes/ inválidas.", _ms(t0))

    violations: list[dict] = []
    for r in rules:
        if not isinstance(r, dict):
            continue
        module = r.get("module")
        if not isinstance(module, str) or not module:
            continue
        has_paths = _module_openapi_has_paths(root, module)
        if not has_paths:
            continue

        need_arazzo = bool(r.get("require_arazzo_when_openapi_has_paths"))
        need_asyncapi = bool(r.get("require_asyncapi_when_openapi_has_paths"))

        if need_arazzo:
            wf_dir = root / "contracts" / "workflows" / module
            has_wf = wf_dir.exists() and any(wf_dir.glob("*.arazzo.y*ml"))
            if not has_wf:
                violations.append({
                    "blocking_code": BLOCKED_ASYNC_REQUIRED_MODULE,
                    "artifact": str((root / "contracts" / "workflows" / module).relative_to(root)),
                    "message": "Módulo com OpenAPI paths exige Arazzo mas não possui workflow `.arazzo.yaml`.",
                    "severity": "error",
                    "details": {"module": module},
                })

        if need_asyncapi:
            async_root = root / "contracts" / "asyncapi"
            # Heurística determinística: filename contém o nome do módulo.
            # Suporta variação singular/plural (ex: "notifications" → "notification_*").
            mod_lower = module.lower()
            mod_variants = {mod_lower}
            if mod_lower.endswith("s"):
                mod_variants.add(mod_lower[:-1])  # strip trailing 's'
            has_any = False
            if async_root.exists():
                for p in sorted(async_root.rglob("*.y*ml")):
                    rel = str(p.relative_to(async_root)).lower()
                    if any(v in rel for v in mod_variants):
                        has_any = True
                        break
            if not has_any:
                violations.append({
                    "blocking_code": BLOCKED_ASYNC_REQUIRED_MODULE,
                    "artifact": "contracts/asyncapi/**",
                    "message": "Módulo com OpenAPI paths exige AsyncAPI mas não há artefatos do módulo em contracts/asyncapi/.",
                    "severity": "error",
                    "details": {"module": module},
                })

    if violations:
        return _pg(
            gate_id,
            "FAIL",
            True,
            BLOCKED_ASYNC_REQUIRED_MODULE,
            f"{len(violations)} requisito(s) async/workflow ausente(s) para módulos com OpenAPI paths.",
            [],
            checked,
            [],
            violations,
            _ms(t0),
        )

    return _pg(
        gate_id,
        "PASS",
        True,
        None,
        "Requisitos AsyncAPI/Arazzo atendidos para módulos com OpenAPI paths (quando aplicável).",
        [],
        checked,
        [],
        [],
        _ms(t0),
    )


def _g2i_external_source_authority(root: pathlib.Path) -> dict:
    t0 = time.monotonic()
    gate_id = "EXTERNAL_SOURCE_AUTHORITY_GATE"
    data, _, checked = _load_module_source_authority_matrix(root)
    if data is None:
        return _skip(gate_id, "Matriz de fontes/autoridade ausente/ inválida — skipping external source authority gate.", _ms(t0))

    cfg = ((data.get("derived_gates") or {}).get("external_source_authority") or {})
    markers = [x for x in (cfg.get("forbidden_ssot_markers") or []) if isinstance(x, str)]
    if not markers:
        return _skip(gate_id, "Sem forbidden_ssot_markers definidos.", _ms(t0))

    violations: list[dict] = []
    scan_dirs = [
        root / "docs" / "hbtrack" / "modulos",
        root / "docs" / "_canon",
    ]
    for d in scan_dirs:
        if not d.exists():
            continue
        for p in sorted(d.rglob("*.md")):
            try:
                text = p.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue
            for m in markers:
                if m in text:
                    violations.append({
                        "blocking_code": BLOCKED_EXTERNAL_SOURCE_AUTHORITY,
                        "artifact": str(p.relative_to(root)),
                        "message": "Marker proibido: benchmark tratado como SSOT.",
                        "severity": "error",
                        "details": {"marker": m},
                    })
                    break

    if violations:
        return _pg(
            gate_id,
            "FAIL",
            True,
            BLOCKED_EXTERNAL_SOURCE_AUTHORITY,
            f"{len(violations)} ocorrência(s) de benchmark tratado como SSOT.",
            [],
            checked,
            [],
            violations,
            _ms(t0),
        )

    return _pg(
        gate_id,
        "PASS",
        True,
        None,
        "Nenhum benchmark tratado como SSOT nos docs verificados.",
        [],
        checked,
        [],
        [],
        _ms(t0),
    )


def _g2j_pre_contract_evidence(root: pathlib.Path) -> dict:
    t0 = time.monotonic()
    gate_id = "PRE_CONTRACT_EVIDENCE_GATE"
    registry_entries, checked = _load_module_registry_entries(root)
    if registry_entries is None:
        return _skip(gate_id, "MODULE_REGISTRY ausente ou inválido — gate não aplicável.", _ms(t0))

    eligible_modules = sorted([
        module
        for module, entry in registry_entries.items()
        if entry.get("status") in PRE_CONTRACT_EVIDENCE_STATUSES
    ])
    if not eligible_modules:
        return _pg(
            gate_id,
            "PASS",
            True,
            None,
            "Nenhum módulo em status validated_contract+ exige evidência pré-contrato.",
            [],
            checked,
            [],
            [],
            _ms(t0),
        )

    log_dir = root / "_reports" / "agent_execution"
    checked.append(str(log_dir))
    if not log_dir.exists():
        violations = [{
            "blocking_code": BLOCKED_PRE_CONTRACT_EVIDENCE,
            "artifact": str(log_dir.relative_to(root)),
            "message": "Diretório de evidências pré-contrato ausente para módulos validated_contract+.",
            "severity": "error",
            "details": {"modules": eligible_modules},
        }]
        return _pg(
            gate_id,
            "FAIL",
            True,
            BLOCKED_PRE_CONTRACT_EVIDENCE,
            "Evidência de pré-contrato ausente para módulos validated_contract+.",
            [],
            checked,
            [],
            violations,
            _ms(t0),
        )

    violations: list[dict] = []
    evidence_files: list[str] = []
    coverage: dict[str, bool] = {module: False for module in eligible_modules}
    for path in sorted(log_dir.glob("*.json")):
        checked.append(str(path))
        data, errs = _load_agent_execution_log(path, root)
        if errs:
            violations.extend(errs)
            continue
        if not isinstance(data, dict):
            continue
        module = data.get("module")
        if module not in coverage:
            continue
        phases = {
            entry.get("phase"): entry.get("result")
            for entry in (data.get("entries") or [])
            if isinstance(entry, dict)
        }
        if phases.get("ROUTING") == "PASS" and phases.get("FOUNDATION_CHECK") == "PASS" and phases.get("DOMAIN_ASSEMBLY") == "PASS" and phases.get("WORKER_HANDOFF") in {"PASS", "HANDOFF"}:
            coverage[module] = True
            evidence_files.append(str(path))

    for module, ok in coverage.items():
        if ok:
            continue
        violations.append({
            "blocking_code": BLOCKED_PRE_CONTRACT_EVIDENCE,
            "artifact": "_reports/agent_execution/*.json",
            "message": f"Nenhuma evidência de pré-contrato completa encontrada para o módulo `{module}`.",
            "severity": "error",
            "details": {"module": module},
        })

    if violations:
        waiver_path = _find_active_waiver(root, gate_id)
        if waiver_path:
            waiver_rel = str(waiver_path.relative_to(root))
            return _pg(
                gate_id,
                "PASS",
                True,
                None,
                "Evidência pré-contrato ausente — waiver ativo aprovado. Ver contracts/_waivers/.",
                [],
                checked + [waiver_rel],
                [waiver_rel],
                [],
                _ms(t0),
            )
        return _pg(
            gate_id,
            "FAIL",
            True,
            BLOCKED_PRE_CONTRACT_EVIDENCE,
            f"{len(violations)} problema(s) de evidência pré-contrato detectado(s).",
            [],
            checked,
            evidence_files,
            violations,
            _ms(t0),
        )

    return _pg(
        gate_id,
        "PASS",
        True,
        None,
        f"Evidência pré-contrato presente para {len(evidence_files)} execução(ões) aplicáveis.",
        [],
        checked,
        evidence_files,
        [],
        _ms(t0),
    )


# Caminhos raiz soberanos: markdowns nestes prefixos são normativos por design e excluídos do scan
_ROOT_SOVEREIGN_PREFIXES: tuple[str, ...] = (
    "docs/_canon",
    ".contract_driven",
    ".github",
    "_archive",
    "temp",
    "_reports",
)


# Prefixos de nomes de arquivos de raiz que são artefatos operacionais/planejamento — excluídos do scan de shadow authority
_ROOT_OPERATIONAL_SKIP_PREFIXES: tuple[str, ...] = (
    "SESSION_HANDOFF",          # estado operacional de continuidade
    "ROADMAP",                  # roadmap oficial do produto
    "FINAL_HANDOFF",            # handoff operacional
    "HISTORICO",                # registro histórico
    "README",                   # readme padrão
    "AGENT_COMPLIANCE",         # plano de execução de compliance
    "AGENT.",                   # agent.md bridge
    "plano",                    # planejamento
    "design",                   # doc de design
)


def _g2k_shadow_authority(root: pathlib.Path) -> dict:
    t0 = time.monotonic()
    gate_id = "SHADOW_AUTHORITY_GATE"
    shadow_dirs = [
        root / "docs" / "hbtrack" / "decisoes",
        root / "docs" / "guias",
    ]
    existing_shadow_dirs = [path for path in shadow_dirs if path.exists()]
    checked = [str(path) for path in shadow_dirs]

    # FASE 7: também varrer markdowns diretamente na raiz de repo (fora de áreas soberanas)
    root_md_files = sorted(
        p for p in root.glob("*.md")
        if not any(
            str(p.relative_to(root)).startswith(pfx)
            for pfx in _ROOT_SOVEREIGN_PREFIXES
        )
        and not any(
            p.name.startswith(pfx) or p.name.lower().startswith(pfx.lower())
            for pfx in _ROOT_OPERATIONAL_SKIP_PREFIXES
        )
    )
    checked.extend(str(p) for p in root_md_files)

    if not existing_shadow_dirs and not root_md_files:
        return _skip(gate_id, "Nenhum diretório não-soberano monitorado encontrado.", _ms(t0))

    authority_patterns = [
        re.compile(r"\bssot\b", re.IGNORECASE),
        re.compile(r"fonte soberana", re.IGNORECASE),
        re.compile(r"source of truth", re.IGNORECASE),
        re.compile(r"fonte prim[aá]ria", re.IGNORECASE),
        re.compile(r"sem[aâ]ntica normativa", re.IGNORECASE),
        re.compile(r"verdade autoritativa", re.IGNORECASE),
    ]
    disclaimer_patterns = [
        re.compile(r"n[aã]o .*artefato can[oô]nico soberano", re.IGNORECASE),
        re.compile(r"n[aã]o[- ]soberan", re.IGNORECASE),
        re.compile(r"n[aã]o[- ]can[oô]nic", re.IGNORECASE),
        re.compile(r"n[aã]o .*ssot", re.IGNORECASE),
        re.compile(r"material de estudo", re.IGNORECASE),
        re.compile(r"apoio humano", re.IGNORECASE),
        re.compile(r"n[aã]o .*autoridade", re.IGNORECASE),
        re.compile(r"n[aã]o substitui", re.IGNORECASE),
        re.compile(r"fonte de racioc[ií]nio", re.IGNORECASE),
        re.compile(r"\bdss\b", re.IGNORECASE),
        # FASE 7: padrões em inglês para bridge docs
        re.compile(r"non[- ]sovereign", re.IGNORECASE),
        re.compile(r"bridge\s+only", re.IGNORECASE),
    ]

    def _scan_md(path: pathlib.Path) -> dict | None:
        """Retorna violação se o arquivo contém authority pattern sem disclaimer, else None."""
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            return None
        if not any(p.search(text) for p in authority_patterns):
            return None
        top = "\n".join(text.splitlines()[:40])
        if any(p.search(top) for p in disclaimer_patterns):
            return None
        return {
            "blocking_code": BLOCKED_SHADOW_AUTHORITY,
            "artifact": str(path.relative_to(root)),
            "message": "Documento não-soberano contém linguagem de autoridade sem disclaimer explícito no topo.",
            "severity": "error",
        }

    violations: list[dict] = []
    # Scan de dirs shadow existentes (comportamento original)
    for shadow_dir in existing_shadow_dirs:
        for path in sorted(shadow_dir.rglob("*.md")):
            checked.append(str(path))
            v = _scan_md(path)
            if v:
                violations.append(v)
    # FASE 7: scan de markdowns de raiz
    for path in root_md_files:
        v = _scan_md(path)
        if v:
            violations.append(v)

    if violations:
        return _pg(
            gate_id,
            "FAIL",
            True,
            BLOCKED_SHADOW_AUTHORITY,
            f"{len(violations)} documento(s) com shadow authority detectado(s).",
            [],
            checked,
            [],
            violations,
            _ms(t0),
        )

    return _pg(
        gate_id,
        "PASS",
        True,
        None,
        "Nenhum shadow authority detectado nos docs DSS verificados.",
        [],
        checked,
        [],
        [],
        _ms(t0),
    )


def _g2l_decision_ir_conformance(root: pathlib.Path) -> dict:
    t0 = time.monotonic()
    gate_id = "DECISION_IR_CONFORMANCE_GATE"
    registry_entries, checked = _load_module_registry_entries(root)
    if registry_entries is None:
        return _skip(gate_id, "MODULE_REGISTRY ausente ou inválido — gate não aplicável.", _ms(t0))

    eligible_modules = sorted([
        module
        for module, entry in registry_entries.items()
        if entry.get("status") in IMPLEMENTATION_AUTHORIZED_STATUSES and "decision_ir" in set(entry.get("expected_surfaces") or [])
    ])
    if not eligible_modules:
        return _skip(gate_id, "Nenhum módulo implementation_ready+ requer Decision IR no momento.", _ms(t0))
    violations: list[dict] = []
    for module in eligible_modules:
        ir_path = _canonical_decision_ir_path(root, module)
        checked.append(str(ir_path))
        if not ir_path.exists():
            violations.append({
                "blocking_code": "IR_SCHEMA_INVALID",
                "artifact": str(ir_path.relative_to(root)),
                "message": f"Decision IR canônico ausente para o módulo `{module}`.",
                "severity": "error",
            })
            continue

        try:
            ir_data = _load_structured_doc(ir_path)
        except Exception as e:
            violations.append({
                "blocking_code": "IR_SCHEMA_INVALID",
                "artifact": str(ir_path.relative_to(root)),
                "message": f"Falha ao ler Decision IR canônico: {e}",
                "severity": "error",
            })
            continue

        if not isinstance(ir_data, dict):
            violations.append({
                "blocking_code": "IR_SCHEMA_INVALID",
                "artifact": str(ir_path.relative_to(root)),
                "message": "Decision IR deve ser objeto/dicionário no topo.",
                "severity": "error",
            })
            continue

        decisions = ir_data.get("decisions")
        if isinstance(decisions, list) and decisions:
            continue

        ir_module = ir_data.get("module")
        if ir_module != module:
            violations.append({
                "blocking_code": "IR_UNKNOWN_MODULE",
                "artifact": str(ir_path.relative_to(root)),
                "message": f"module={ir_module!r} diverge do módulo esperado `{module}`.",
                "severity": "error",
            })
        if not isinstance(ir_data.get("status"), str) or not ir_data.get("status"):
            violations.append({
                "blocking_code": "IR_SCHEMA_INVALID",
                "artifact": str(ir_path.relative_to(root)),
                "message": "Campo obrigatório `status` ausente ou vazio.",
                "severity": "error",
            })
        if not isinstance(ir_data.get("decision_scope"), str) or not ir_data.get("decision_scope"):
            violations.append({
                "blocking_code": "IR_SCHEMA_INVALID",
                "artifact": str(ir_path.relative_to(root)),
                "message": "Campo obrigatório `decision_scope` ausente ou vazio.",
                "severity": "error",
            })
        if not ir_data.get("source"):
            violations.append({
                "blocking_code": "IR_SCHEMA_INVALID",
                "artifact": str(ir_path.relative_to(root)),
                "message": "Campo obrigatório `source` ausente ou vazio.",
                "severity": "error",
            })

    if violations:
        return _pg(
            gate_id,
            "FAIL",
            True,
            violations[0]["blocking_code"],
            f"Decision IR canônico inválido: {len(violations)} violação(ões).",
            [],
            checked,
            [],
            violations,
            _ms(t0),
        )

    return _pg(
        gate_id,
        "PASS",
        True,
        None,
        f"Decision IR canônico válido para {len(eligible_modules)} módulo(s) implementation_ready+.",
        [],
        checked,
        [],
        [],
        _ms(t0),
    )


def _g2n_canon_allowlist(root: pathlib.Path) -> dict:
    """
    CANON_ALLOWLIST_GATE — garante que apenas artefatos explicitamente autorizados
    existam em docs/_canon/ e seus subdiretórios canônicos.

    Previne que o agente crie documentos não-governança dentro do diretório normativo
    soberano, evitando que artefatos de módulo ou drafts passem a ser tratados como
    autoritativos pelo sistema.

    Allowlist derivada de docs/_canon/README.md (tabela de artefatos canônicos globais).
    Qualquer adição ao canon requer atualização desta lista (CHANGE_POLICY.md).
    """
    t0 = time.monotonic()
    gate_id = "CANON_ALLOWLIST_GATE"
    canon_dir = root / "docs" / "_canon"
    checked: list[str] = [str(canon_dir)]

    if not canon_dir.exists():
        return _skip(gate_id, "docs/_canon/ ausente — gate não aplicável.", _ms(t0))

    # Allowlist canônica top-level (SSOT: docs/_canon/README.md tabela §Artefatos Canônicos Globais)
    TOPLEVEL_ALLOWLIST: frozenset[str] = frozenset({
        "README.md",
        "OPERATIONS.md",
        "SYSTEM_SCOPE.md",
        "ARCHITECTURE.md",
        "CODE_ARCHITECTURE.md",
        "MODULE_MAP.md",
        "GLOBAL_INVARIANTS.md",
        "SECURITY_RULES.md",
        "DATA_CONVENTIONS.md",
        "CI_CONTRACT_GATES.md",
        "TEST_STRATEGY.md",
        "UI_CONTRACT_GUIDE.md",
        "C4_CONTEXT.md",
        "C4_CONTAINERS.md",
        "CHANGE_POLICY.md",
        "DOMAIN_GLOSSARY.md",
        "HANDBALL_RULES_DOMAIN.md",
        "MODULE_SOURCE_AUTHORITY_MATRIX.yaml",
        "MODULE_REGISTRY.yaml",
        "TOOLCHAIN_HEALTH_POLICY.md",
        "CONTRACT_PIPELINE.md",
        "DECISION_POLICY.md",
        "ARCHITECTURE_DECISION_BACKLOG.md",
        # Adicionados por ADRs posteriores (ADR-027..ADR-030)
        "DATA_MIGRATION_POLICY.md",
        "DEPLOY_PIPELINE.md",
        "RUNTIME_CONTRACT_MONITORING_POLICY.md",
        "FRONTEND_CONTRACT.md",
        "FEATURE_REGISTRY.yaml",
        "IR_TO_SURFACE_MAPPING.yaml",
        # Adicionados por ADR-031 e boot permanente
        "AGENT_INSTRUCTIONS.md",
        "SCOPE_BOUNDARY_POLICY.md",
        # Roadmap canônico de módulos
        "MODULE_ROADMAP_2026_03_17.md",
        # Política de regressão obrigatória (suíte de sobrevivência)
        "SURVIVAL_SUITE_POLICY.md",
        # Adicionados por ANALISEARQUITETURA.md FASE 4 — artefatos de runtime e componentes
        "C4_COMPONENTS_BACKEND.md",
        "INTEGRATION_FLOWS.md",
        "RUNTIME_CURRENT_STATE.md",
        "ADR_INDEX.md",
        # Adicionado FASE 3 — runbook de provisionamento VPS
        "VPS_SETUP.md",
    })

    # Subdiretórios autorizados
    SUBDIRS_ALLOWLIST: frozenset[str] = frozenset({"decisions", "gates", "security", "templates"})

    # Allowlist gates/ — apenas artefatos do registry de gates
    GATES_ALLOWLIST: frozenset[str] = frozenset({"GATES_REGISTRY.yaml", "README.md"})

    # security/ — apenas a matriz OWASP
    SECURITY_ALLOWLIST: frozenset[str] = frozenset({"OWASP_API_CONTROL_MATRIX.yaml"})

    # templates/ — templates de sessão/handoff
    TEMPLATES_ALLOWLIST: frozenset[str] = frozenset({"SESSION_HANDOFF.template.md"})

    # decisions/ — padrão ADR-NNN-*.md (README.md é excepcionado como arquivo de suporte)
    adr_pattern = re.compile(r"^ADR-\d{3}-.+\.md$")
    DECISIONS_EXEMPT: frozenset[str] = frozenset({"README.md"})

    violations: list[dict] = []

    # --- Verifica top-level ---
    for item in sorted(canon_dir.iterdir()):
        checked.append(str(item.relative_to(root)))
        if item.is_dir():
            if item.name not in SUBDIRS_ALLOWLIST:
                violations.append({
                    "blocking_code": BLOCKED_CANON_INTRUDER,
                    "artifact": str(item.relative_to(root)).replace("\\", "/") + "/",
                    "message": (
                        f"Subdiretório não autorizado em docs/_canon/: '{item.name}/'. "
                        "Subdiretórios permitidos: decisions/, gates/, security/, templates/."
                    ),
                    "severity": "error",
                })
        else:
            if item.name not in TOPLEVEL_ALLOWLIST:
                violations.append({
                    "blocking_code": BLOCKED_CANON_INTRUDER,
                    "artifact": str(item.relative_to(root)).replace("\\", "/"),
                    "message": (
                        f"Arquivo não autorizado em docs/_canon/: '{item.name}'. "
                        "Apenas artefatos registrados em docs/_canon/README.md são permitidos. "
                        "Para adicionar ao canon, siga CHANGE_POLICY.md e atualize a allowlist do gate."
                    ),
                    "severity": "error",
                })

    # --- Verifica gates/ ---
    gates_dir = canon_dir / "gates"
    if gates_dir.exists():
        for item in sorted(gates_dir.iterdir()):
            checked.append(str(item.relative_to(root)))
            if item.is_dir():
                violations.append({
                    "blocking_code": BLOCKED_CANON_INTRUDER,
                    "artifact": str(item.relative_to(root)).replace("\\", "/") + "/",
                    "message": f"Subdiretório não autorizado em docs/_canon/gates/: '{item.name}/'.",
                    "severity": "error",
                })
            elif item.name not in GATES_ALLOWLIST:
                violations.append({
                    "blocking_code": BLOCKED_CANON_INTRUDER,
                    "artifact": str(item.relative_to(root)).replace("\\", "/"),
                    "message": (
                        f"Arquivo não autorizado em docs/_canon/gates/: '{item.name}'. "
                        "gates/ deve conter apenas GATES_REGISTRY.yaml e README.md. "
                        "IRs de módulo pertencem a .dev/<MODULE>/ ou docs/hbtrack/modulos/<module>/."
                    ),
                    "severity": "error",
                })

    # --- Verifica security/ ---
    security_dir = canon_dir / "security"
    if security_dir.exists():
        for item in sorted(security_dir.iterdir()):
            checked.append(str(item.relative_to(root)))
            if item.is_dir():
                violations.append({
                    "blocking_code": BLOCKED_CANON_INTRUDER,
                    "artifact": str(item.relative_to(root)).replace("\\", "/") + "/",
                    "message": f"Subdiretório não autorizado em docs/_canon/security/: '{item.name}/'.",
                    "severity": "error",
                })
            elif item.name not in SECURITY_ALLOWLIST:
                violations.append({
                    "blocking_code": BLOCKED_CANON_INTRUDER,
                    "artifact": str(item.relative_to(root)).replace("\\", "/"),
                    "message": (
                        f"Arquivo não autorizado em docs/_canon/security/: '{item.name}'. "
                        "security/ deve conter apenas OWASP_API_CONTROL_MATRIX.yaml."
                    ),
                    "severity": "error",
                })

    # --- Verifica templates/ ---
    templates_dir = canon_dir / "templates"
    if templates_dir.exists():
        for item in sorted(templates_dir.iterdir()):
            checked.append(str(item.relative_to(root)))
            if item.is_dir():
                violations.append({
                    "blocking_code": BLOCKED_CANON_INTRUDER,
                    "artifact": str(item.relative_to(root)).replace("\\", "/") + "/",
                    "message": f"Subdiretório não autorizado em docs/_canon/templates/: '{item.name}/'.",
                    "severity": "error",
                })
            elif item.name not in TEMPLATES_ALLOWLIST:
                violations.append({
                    "blocking_code": BLOCKED_CANON_INTRUDER,
                    "artifact": str(item.relative_to(root)).replace("\\", "/"),
                    "message": (
                        f"Arquivo não autorizado em docs/_canon/templates/: '{item.name}'. "
                        "templates/ deve conter apenas SESSION_HANDOFF.template.md."
                    ),
                    "severity": "error",
                })

    # --- Verifica decisions/ ---
    decisions_dir = canon_dir / "decisions"
    if decisions_dir.exists():
        for item in sorted(decisions_dir.iterdir()):
            checked.append(str(item.relative_to(root)))
            if item.is_dir():
                violations.append({
                    "blocking_code": BLOCKED_CANON_INTRUDER,
                    "artifact": str(item.relative_to(root)).replace("\\", "/") + "/",
                    "message": f"Subdiretório não autorizado em docs/_canon/decisions/: '{item.name}/'.",
                    "severity": "error",
                })
            elif item.name not in DECISIONS_EXEMPT and not adr_pattern.match(item.name):
                violations.append({
                    "blocking_code": BLOCKED_CANON_INTRUDER,
                    "artifact": str(item.relative_to(root)).replace("\\", "/"),
                    "message": (
                        f"Arquivo em docs/_canon/decisions/ não segue padrão ADR-NNN-<slug>.md: '{item.name}'. "
                        "Decisões arquiteturais devem ser nomeadas como ADR-031-nome-kebab.md."
                    ),
                    "severity": "error",
                })

    if violations:
        return _pg(
            gate_id,
            "FAIL",
            True,
            BLOCKED_CANON_INTRUDER,
            f"{len(violations)} artefato(s) não autorizado(s) detectado(s) em docs/_canon/.",
            [],
            checked,
            [],
            violations,
            _ms(t0),
        )

    return _pg(
        gate_id,
        "PASS",
        True,
        None,
        "docs/_canon/ contém apenas artefatos autorizados.",
        [],
        checked,
        [],
        [],
        _ms(t0),
    )


def _g3_placeholder_residue(root: pathlib.Path) -> dict:
    t0 = time.monotonic()
    gate_id = "PLACEHOLDER_RESIDUE_GATE"
    violations: list[dict] = []
    checked: list[str] = []
    scan_dir = root / "contracts"
    if not scan_dir.exists():
        return _skip(gate_id, "contracts/ ausente — gate não aplicável.", _ms(t0))
    for p in sorted(scan_dir.rglob("*")):
        if p.suffix not in {".yaml", ".json", ".md"}:
            continue
        if not p.is_file():
            continue
        checked.append(str(p))
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        token_hit = False
        for token in _PLACEHOLDER_TOKENS:
            if token in text:
                violations.append({
                    "blocking_code": "BLOCKED_PLACEHOLDER_RESIDUE",
                    "artifact": str(p.relative_to(root)),
                    "message": f"Token placeholder '{token}' encontrado.",
                    "severity": "error",
                })
                token_hit = True
                break
        if not token_hit:
            m = _PLACEHOLDER_CONCEPTUAL_RE.search(text)
            if m:
                ctx_start = max(0, m.start() - 10)
                ctx_end = min(len(text), m.end() + 50)
                context = text[ctx_start:ctx_end]
                if not _PLACEHOLDER_CONCEPTUAL_WHITELIST_RE.search(context):
                    violations.append({
                        "blocking_code": "BLOCKED_PLACEHOLDER_RESIDUE",
                        "artifact": str(p.relative_to(root)),
                        "message": f"Placeholder conceitual detectado: '{m.group()}'.",
                        "severity": "warn",
                        "placeholder_conceptual": True,
                    })
    if violations:
        return _pg(gate_id, "FAIL", True, "BLOCKED_PLACEHOLDER_RESIDUE",
                   f"{len(violations)} arquivo(s) com tokens placeholder.",
                   [], checked, [], violations, _ms(t0))
    return _pg(gate_id, "PASS", True, None,
               f"Nenhum token placeholder em {len(checked)} arquivo(s) verificado(s).",
               [], checked, [], [], _ms(t0))


def _g4_ref_hermeticity(root: pathlib.Path) -> dict:
    t0 = time.monotonic()
    gate_id = "REF_HERMETICITY_GATE"
    violations: list[dict] = []
    checked: list[str] = []
    openapi_dir = root / "contracts" / "openapi"
    if not openapi_dir.exists():
        return _skip(gate_id, "contracts/openapi/ ausente — skipping ref hermeticity.", _ms(t0))
    for p in sorted(openapi_dir.rglob("*.yaml")):
        checked.append(str(p))
        try:
            obj = _load_yaml(p)
        except Exception:
            continue
        refs: list[str] = []
        _collect_refs(obj, refs)
        for ref in refs:
            if ref.startswith("#"):
                continue
            if ref.startswith("http://") or ref.startswith("https://"):
                violations.append({
                    "blocking_code": "BLOCKED_EXTERNAL_REF",
                    "artifact": str(p.relative_to(root)),
                    "message": f"$ref externo HTTP não permitido: {ref}",
                    "severity": "error",
                })
                continue
            # Separar arquivo de JSON Pointer (parte após #)
            ref_file = ref.split("#")[0] if "#" in ref else ref
            target = (p.parent / ref_file).resolve()
            try:
                target.relative_to(root)
            except ValueError:
                violations.append({
                    "blocking_code": "BLOCKED_EXTERNAL_REF",
                    "artifact": str(p.relative_to(root)),
                    "message": f"$ref aponta para fora do repositório: {ref}",
                    "severity": "error",
                })
                continue
            if not target.exists():
                violations.append({
                    "blocking_code": "BLOCKED_UNRESOLVED_REF",
                    "artifact": str(p.relative_to(root)),
                    "message": f"$ref não resolve para arquivo existente: {ref}",
                    "severity": "error",
                })
    if violations:
        return _pg(gate_id, "FAIL", True, violations[0]["blocking_code"],
                   f"{len(violations)} $ref(s) problemático(s).",
                   [], checked, [], violations, _ms(t0))
    return _pg(gate_id, "PASS", True, None,
               f"Todos os $refs herméticos ({len(checked)} arquivo(s)).",
               [], checked, [], [], _ms(t0))


def _g4a_tooling_config(root: pathlib.Path) -> dict:
    t0 = time.monotonic()
    gate_id = "TOOLING_CONFIG_GATE"
    scripts_dir = root / "scripts"
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
    try:
        from contracts.validate.tooling_config_gate import evaluate_tooling_config  # type: ignore
    except Exception as exc:
        return _pg(
            gate_id,
            "FAIL",
            True,
            "ERROR_INFRA",
            f"Falha ao carregar tooling_config_gate.py: {exc}",
            [],
            [str(root / "scripts" / "contracts" / "validate" / "tooling_config_gate.py")],
            [],
            [{
                "blocking_code": "ERROR_INFRA",
                "artifact": "scripts/contracts/validate/tooling_config_gate.py",
                "message": f"Erro ao importar gate de tooling: {exc}",
                "severity": "error",
            }],
            _ms(t0),
        )

    result = evaluate_tooling_config(
        root,
        tool_versions={
            "redocly": _tool_ver("redocly", "--version"),
            "spectral": _tool_ver("spectral", "--version"),
            "asyncapi": _tool_ver("asyncapi", "--version"),
            "oasdiff": _tool_ver("oasdiff", "version"),
            "schemathesis": _tool_ver("schemathesis", "--version"),
        },
        is_ci=_is_ci_environment(),
    )
    status = result.get("status") or "FAIL"
    checked = list(result.get("checked") or [])
    violations = list(result.get("violations") or [])
    if status == "FAIL":
        return _pg(
            gate_id,
            "FAIL",
            True,
            BLOCKED_TOOLING_CONFIG_INVALID,
            "Toolchain/config incompatível ou ferramenta obrigatória ausente.",
            [],
            checked,
            [],
            violations,
            _ms(t0),
        )
    if status == "DEGRADED":
        return _pg(
            gate_id,
            "DEGRADED",
            False,
            None,
            "Toolchain local degradada: fallback explícito permitido apenas fora de CI.",
            [],
            checked,
            [],
            violations,
            _ms(t0),
        )
    return _pg(
        gate_id,
        "PASS",
        True,
        None,
        "Toolchain/config compatíveis com o pipeline oficial.",
        [],
        checked,
        [],
        [],
        _ms(t0),
    )


def _g5_openapi_root_structure(root: pathlib.Path) -> dict:
    t0 = time.monotonic()
    gate_id = "OPENAPI_ROOT_STRUCTURE_GATE"
    openapi_root = root / "contracts" / "openapi" / "openapi.yaml"
    redocly_cfg = root / "redocly.yaml"
    if not openapi_root.exists():
        return _skip(gate_id, "openapi.yaml ausente.", _ms(t0))
    cmd = ["lint", str(openapi_root)]
    if redocly_cfg.exists():
        cmd += ["--config", str(redocly_cfg)]
    rc, stdout, stderr = _try_node_cli(root, tool="redocly", args=cmd, cwd=root)
    if rc == -1:
        return _pg(
            gate_id,
            "FAIL",
            True,
            "ERROR_INFRA",
            "redocly CLI não disponível via toolchain WSL-native (node_modules/NVM).",
            [str(openapi_root)],
            [str(openapi_root)],
            [],
            [{"blocking_code": "ERROR_INFRA", "artifact": "redocly", "message": (stderr or stdout), "severity": "error"}],
            _ms(t0),
        )
    output = stdout + stderr
    if rc != 0:
        if _looks_like_wsl_vsock_failure(output):
            return _pg(
                gate_id,
                "FAIL",
                True,
                "ERROR_INFRA",
                "redocly falhou por interop WSL/Windows (vsock). Use Node WSL-native e evite wrappers Windows.",
                [str(openapi_root)],
                [str(openapi_root)],
                [],
                [{"blocking_code": "ERROR_INFRA", "artifact": "redocly", "message": output.strip(), "severity": "error"}],
                _ms(t0),
            )
        if _looks_like_node_missing(output):
            return _pg(
                gate_id,
                "FAIL",
                True,
                "ERROR_INFRA",
                "redocly existe mas Node.js não está disponível no ambiente.",
                [str(openapi_root)],
                [str(openapi_root)],
                [],
                [{"blocking_code": "ERROR_INFRA", "artifact": "node", "message": output.strip(), "severity": "error"}],
                _ms(t0),
            )
        if _looks_like_redocly_update_only(output):
            return _pg(gate_id, "PASS", True, None,
                       "redocly lint: nenhum erro (aviso de nova versão ignorado).",
                       [str(openapi_root)], [str(openapi_root)], [], [], _ms(t0))
        lines = [ln for ln in output.splitlines() if ln.strip()]
        violations = [
            {"blocking_code": "BLOCKED_OPENAPI_STRUCTURE", "artifact": str(openapi_root.relative_to(root)), "message": ln, "severity": "error"}
            for ln in lines[:20]
        ]
        return _pg(gate_id, "FAIL", True, "BLOCKED_OPENAPI_STRUCTURE",
                   f"redocly lint falhou (rc={rc}).",
                   [str(openapi_root)], [str(openapi_root)], [], violations, _ms(t0))
    return _pg(gate_id, "PASS", True, None,
               "redocly lint: nenhum erro.",
               [str(openapi_root)], [str(openapi_root)], [], [], _ms(t0))


def _g5a_openapi_root_module_sync(root: pathlib.Path) -> dict:
    t0 = time.monotonic()
    gate_id = "OPENAPI_ROOT_MODULE_SYNC_GATE"
    registry_entries, checked = _load_module_registry_entries(root)
    if registry_entries is None:
        return _skip(gate_id, "MODULE_REGISTRY ausente ou inválido — gate não aplicável.", _ms(t0))

    root_refs, ref_violations, root_checked = _openapi_root_module_refs(root)
    checked.extend(root_checked)
    violations: list[dict] = list(ref_violations)

    modules = sorted([
        module
        for module, entry in registry_entries.items()
        if "openapi_sync" in set(entry.get("expected_surfaces") or [])
    ])
    module_set = set(modules)

    for module in modules:
        module_paths = set(_module_openapi_paths(root, module))
        path_file = root / "contracts" / "openapi" / "paths" / f"{module}.yaml"
        checked.append(str(path_file))
        root_module_paths = root_refs.get(module, set())
        if not module_paths:
            if root_module_paths:
                violations.append({
                    "blocking_code": BLOCKED_OPENAPI_ROOT_MODULE_SYNC,
                    "artifact": str(path_file.relative_to(root)),
                    "message": f"Root OpenAPI referencia path(s) do módulo `{module}`, mas o arquivo do módulo não contém path items reais.",
                    "severity": "error",
                    "details": {"extra_in_root": sorted(root_module_paths)},
                })
            continue

        missing_in_root = sorted(module_paths - root_module_paths)
        extra_in_root = sorted(root_module_paths - module_paths)
        if missing_in_root:
            violations.append({
                "blocking_code": BLOCKED_OPENAPI_ROOT_MODULE_SYNC,
                "artifact": str(path_file.relative_to(root)),
                "message": f"Root OpenAPI não referencia todos os path items reais do módulo `{module}`.",
                "severity": "error",
                "details": {"missing_in_root": missing_in_root},
            })
        if extra_in_root:
            violations.append({
                "blocking_code": BLOCKED_OPENAPI_ROOT_MODULE_SYNC,
                "artifact": str(path_file.relative_to(root)),
                "message": f"Root OpenAPI referencia path(s) inexistente(s) no módulo `{module}`.",
                "severity": "error",
                "details": {"extra_in_root": extra_in_root},
            })

    for module, paths in sorted(root_refs.items()):
        if module in module_set:
            continue
        violations.append({
            "blocking_code": BLOCKED_OPENAPI_ROOT_MODULE_SYNC,
            "artifact": "contracts/openapi/openapi.yaml",
            "message": f"Root OpenAPI referencia módulo não registrado ou sem superfície openapi_sync: `{module}`.",
            "severity": "error",
            "details": {"paths": sorted(paths)},
        })

    if violations:
        return _pg(
            gate_id,
            "FAIL",
            True,
            BLOCKED_OPENAPI_ROOT_MODULE_SYNC,
            f"{len(violations)} divergência(s) root↔módulos detectada(s) no OpenAPI.",
            [],
            checked,
            [],
            violations,
            _ms(t0),
        )

    return _pg(
        gate_id,
        "PASS",
        True,
        None,
        "Root OpenAPI alinhado aos path items reais dos módulos.",
        [],
        checked,
        [],
        [],
        _ms(t0),
    )


def _validate_openapi_policy_contract_rules(root: pathlib.Path) -> list[dict]:
    violations: list[dict] = []
    paths_dir = root / "contracts" / "openapi" / "paths"
    if not paths_dir.exists():
        return violations
    auth_conflict_exempt = {
        ("/auth/login", "post"),
        ("/auth/logout", "post"),
        ("/auth/refresh", "post"),
    }

    for path_file in sorted(paths_dir.glob("*.yaml")):
        rel = str(path_file.relative_to(root))
        doc = _load_yaml_or_empty(path_file) or {}
        if not isinstance(doc, dict):
            continue
        for route, path_item in doc.items():
            if not isinstance(path_item, dict):
                continue
            for method, op in path_item.items():
                if method not in {"get", "post", "put", "patch", "delete"} or not isinstance(op, dict):
                    continue
                responses = op.get("responses") or {}
                security = op.get("security")
                if isinstance(security, list) and security and "500" not in responses:
                    violations.append({
                        "blocking_code": "BLOCKED_OPENAPI_POLICY",
                        "artifact": rel,
                        "message": f"{method.upper()} {route} é operação protegida e não documenta response 500.",
                        "severity": "error",
                    })
                if method in {"post", "put", "patch", "delete"} and (route, method) not in auth_conflict_exempt and "409" not in responses:
                    violations.append({
                        "blocking_code": "BLOCKED_OPENAPI_POLICY",
                        "artifact": rel,
                        "message": f"{method.upper()} {route} é mutação contratual e não documenta response 409.",
                        "severity": "error",
                    })

    analytics_path = paths_dir / "analytics.yaml"
    if analytics_path.exists():
        doc = _load_yaml_or_empty(analytics_path) or {}
        op = (((doc.get("/analytics/query") or {}).get("post")) or {}) if isinstance(doc, dict) else {}
        if isinstance(op, dict):
            req_schema = (
                (((op.get("requestBody") or {}).get("content") or {}).get("application/json") or {}).get("schema")
                or {}
            )
            res_schema = (
                (((((op.get("responses") or {}).get("200") or {}).get("content") or {}).get("application/json") or {}).get("schema"))
                or {}
            )
            if not (isinstance(req_schema, dict) and req_schema.get("$ref") == "../components/schemas/analytics/analytics_query_request.yaml"):
                violations.append({
                    "blocking_code": "BLOCKED_OPENAPI_POLICY",
                    "artifact": str(analytics_path.relative_to(root)),
                    "message": "/analytics/query deve referenciar analytics_query_request.yaml como request soberano.",
                    "severity": "error",
                })
            if not (isinstance(res_schema, dict) and res_schema.get("$ref") == "../components/schemas/analytics/analytics_query_response.yaml"):
                violations.append({
                    "blocking_code": "BLOCKED_OPENAPI_POLICY",
                    "artifact": str(analytics_path.relative_to(root)),
                    "message": "/analytics/query deve referenciar analytics_query_response.yaml como response soberano.",
                    "severity": "error",
                })
    return violations


def _g6_openapi_policy_ruleset(root: pathlib.Path) -> dict:
    t0 = time.monotonic()
    gate_id = "OPENAPI_POLICY_RULESET_GATE"
    openapi_root = root / "contracts" / "openapi" / "openapi.yaml"
    spectral_cfg = root / ".spectral.yaml"
    if not openapi_root.exists():
        return _skip(gate_id, "openapi.yaml ausente.", _ms(t0))
    if not spectral_cfg.exists():
        return _skip(gate_id, ".spectral.yaml ausente.", _ms(t0))
    rc, stdout, stderr = _try_node_cli(
        root,
        tool="spectral",
        args=[
            "lint",
            str(openapi_root),
            "--ruleset",
            str(spectral_cfg),
            "--format",
            "json",
        ],
        cwd=root,
    )
    if rc == -1:
        return _pg(
            gate_id,
            "FAIL",
            True,
            "ERROR_INFRA",
            "spectral CLI não disponível via toolchain WSL-native (node_modules/NVM).",
            [str(openapi_root)],
            [str(openapi_root)],
            [],
            [{"blocking_code": "ERROR_INFRA", "artifact": "spectral", "message": (stderr or stdout), "severity": "error"}],
            _ms(t0),
        )
    combined = stdout + stderr
    if rc != 0 and _looks_like_wsl_vsock_failure(combined):
        return _pg(
            gate_id,
            "FAIL",
            True,
            "ERROR_INFRA",
            "spectral falhou por interop WSL/Windows (vsock). Use Node WSL-native e evite wrappers Windows.",
            [str(openapi_root)],
            [str(openapi_root)],
            [],
            [{"blocking_code": "ERROR_INFRA", "artifact": "spectral", "message": combined.strip(), "severity": "error"}],
            _ms(t0),
        )
    if rc != 0 and _looks_like_node_missing(combined):
        return _pg(
            gate_id,
            "FAIL",
            True,
            "ERROR_INFRA",
            "spectral existe mas Node.js não está disponível no ambiente.",
            [str(openapi_root)],
            [str(openapi_root)],
            [],
            [{"blocking_code": "ERROR_INFRA", "artifact": "node", "message": combined.strip(), "severity": "error"}],
            _ms(t0),
        )
    violations: list[dict] = []
    try:
        results = json.loads(stdout)
        if isinstance(results, list):
            for item in results:
                sev = item.get("severity", 0)
                sev_label = "error" if sev == 0 else "warn"
                violations.append({
                    "blocking_code": "BLOCKED_OPENAPI_POLICY",
                    "artifact": item.get("source", str(openapi_root.relative_to(root))),
                    "message": f"[{item.get('code', '?')}] {item.get('message', '')}",
                    "severity": sev_label,
                    "path": item.get("path", []),
                    "range": item.get("range", {}),
                })
    except (json.JSONDecodeError, TypeError):
        if rc != 0:
            for ln in (stdout + stderr).splitlines():
                if ln.strip():
                    violations.append({
                        "blocking_code": "BLOCKED_OPENAPI_POLICY",
                        "artifact": str(openapi_root.relative_to(root)),
                        "message": ln.strip(),
                        "severity": "error",
                    })
    violations.extend(_validate_openapi_policy_contract_rules(root))
    errors = [v for v in violations if v.get("severity") == "error"]
    if errors:
        return _pg(gate_id, "FAIL", True, "BLOCKED_OPENAPI_POLICY",
                   f"spectral: {len(errors)} erro(s), {len(violations) - len(errors)} aviso(s).",
                   [str(openapi_root)], [str(openapi_root)], [], violations, _ms(t0))
    return _pg(gate_id, "PASS", True, None,
               f"spectral: PASS ({len(violations)} aviso(s)).",
               [str(openapi_root)], [str(openapi_root)], [], violations, _ms(t0))


def _g7_json_schema_validation(root: pathlib.Path) -> dict:
    t0 = time.monotonic()
    gate_id = "JSON_SCHEMA_VALIDATION_GATE"
    schema_dir = root / "contracts" / "schemas"
    if not schema_dir.exists():
        return _skip(gate_id, "contracts/schemas/ ausente.", _ms(t0))
    files = sorted(schema_dir.rglob("*.schema.json"))
    if not files:
        return _skip(gate_id, "Nenhum *.schema.json encontrado em contracts/schemas/.", _ms(t0))
    checked: list[str] = []
    violations: list[dict] = []
    for p in files:
        checked.append(str(p))
        try:
            obj = _load_json(p)
        except json.JSONDecodeError as e:
            violations.append({
                "blocking_code": "BLOCKED_INVALID_JSON_SCHEMA",
                "artifact": str(p.relative_to(root)),
                "message": f"JSON inválido: {e}",
                "severity": "error",
            })
            continue
        if "$schema" not in obj:
            violations.append({
                "blocking_code": "BLOCKED_MISSING_SCHEMA_DECLARATION",
                "artifact": str(p.relative_to(root)),
                "message": "Campo '$schema' ausente.",
                "severity": "warn",
            })
        stem = p.stem
        if not stem.endswith(".schema"):
            violations.append({
                "blocking_code": "BLOCKED_INVALID_SCHEMA_NAMING",
                "artifact": str(p.relative_to(root)),
                "message": f"Nome de arquivo deve terminar com .schema.json: {p.name}",
                "severity": "warn",
            })
    errors = [v for v in violations if v.get("severity") == "error"]
    if errors:
        return _pg(gate_id, "FAIL", True, "BLOCKED_INVALID_JSON_SCHEMA",
                   f"JSON Schema: {len(errors)} erro(s).",
                   [], checked, [], violations, _ms(t0))
    return _pg(gate_id, "PASS", True, None,
               f"JSON Schema: {len(checked)} arquivo(s) válido(s), {len(violations)} aviso(s).",
               [], checked, [], violations, _ms(t0))


def _g8_cross_spec_alignment(root: pathlib.Path, axioms: "DomainAxioms") -> dict:
    t0 = time.monotonic()
    gate_id = "CROSS_SPEC_ALIGNMENT_GATE"
    openapi_root = root / "contracts" / "openapi" / "openapi.yaml"
    openapi_schema_files = (
        [str(p) for p in sorted((root / "contracts" / "openapi" / "components").rglob("*.yaml"))]
        if (root / "contracts" / "openapi" / "components").exists()
        else []
    )
    openapi_path_files = (
        [str(p) for p in sorted((root / "contracts" / "openapi" / "paths").glob("*.yaml"))]
        if (root / "contracts" / "openapi" / "paths").exists()
        else []
    )
    json_schema_files = (
        [str(p) for p in sorted((root / "contracts" / "schemas").rglob("*.schema.json"))]
        if (root / "contracts" / "schemas").exists()
        else []
    )
    asyncapi_files = (
        [str(p) for p in sorted((root / "contracts" / "asyncapi").rglob("*.yaml"))]
        if (root / "contracts" / "asyncapi").exists()
        else []
    )
    workflow_files = (
        [str(p) for p in sorted((root / "contracts" / "workflows").rglob("*.arazzo.yaml"))]
        if (root / "contracts" / "workflows").exists()
        else []
    )
    module_docs_files = (
        [str(p) for p in sorted((root / "docs" / "hbtrack" / "modulos").rglob("*"))]
        if (root / "docs" / "hbtrack" / "modulos").exists()
        else []
    )
    state_model_files = (
        [str(p) for p in sorted((root / "contracts" / "state_models").rglob("*.json"))]
        if (root / "contracts" / "state_models").exists()
        else []
    )
    artifacts_for_formats = openapi_schema_files + openapi_path_files + json_schema_files + asyncapi_files
    artifacts_for_enums = openapi_schema_files + json_schema_files + asyncapi_files
    all_artifacts = sorted(set(
        artifacts_for_formats + artifacts_for_enums + workflow_files + module_docs_files + state_model_files
    ))
    violations: list[dict] = []
    violations.extend(validate_error_shape_required_fields(str(openapi_root), axioms))
    violations.extend(validate_global_formats_by_regex(artifacts_for_formats, axioms))
    violations.extend(validate_enums_against_closed_sets(artifacts_for_enums, axioms))
    violations.extend(validate_state_transitions_against_axioms(state_model_files, axioms))
    violations.extend(
        validate_cross_surface_alignment(
            str(openapi_root),
            asyncapi_files=asyncapi_files,
            schema_files=json_schema_files,
            docs_files=workflow_files + module_docs_files,
            axioms=axioms,
        )
    )
    inputs = [
        str(openapi_root),
        str(root / "contracts" / "schemas"),
        str(root / "contracts" / "asyncapi"),
        str(root / "contracts" / "workflows"),
    ]
    if violations:
        waiver_path = _find_active_waiver(root, gate_id)
        if waiver_path:
            waiver_rel = str(waiver_path.relative_to(root))
            return _pg(
                gate_id, "PASS", True, None,
                f"Violações cross-spec — waiver ativo aprovado ({len(violations)} violation(s)). Ver contracts/_waivers/.",
                inputs, all_artifacts + [waiver_rel], [waiver_rel], [], _ms(t0),
            )
        return _pg(gate_id, "FAIL", True,
                   (violations[0] or {}).get("blocking_code", BLOCKED_CROSS_SPEC_DIVERGENCE),
                   f"{len(violations)} violação(ões) de alinhamento cross-spec.",
                   inputs, all_artifacts, [], violations, _ms(t0))
    return _pg(gate_id, "PASS", True, None,
               "Alinhamento cross-spec: PASS.",
               inputs, all_artifacts, [], [], _ms(t0))


def _find_active_waiver(root: pathlib.Path, gate_id: str) -> pathlib.Path | None:
    waivers_dir = root / "contracts" / "_waivers"
    if not waivers_dir.exists():
        return None
    now = datetime.datetime.now(datetime.timezone.utc)
    for wpath in sorted(waivers_dir.glob("*.json")):
        if wpath.name == "waiver.schema.json":
            continue
        try:
            waiver = json.loads(wpath.read_text(encoding="utf-8"))
        except Exception:
            continue
        if waiver.get("gate_id") != gate_id:
            continue
        expires = waiver.get("expires_at_utc")
        if expires:
            try:
                expiry = datetime.datetime.fromisoformat(expires.replace("Z", "+00:00"))
            except ValueError:
                continue
            if expiry.tzinfo is None:
                expiry = expiry.replace(tzinfo=datetime.timezone.utc)
            if expiry < now:
                continue
        return wpath
    return None


def _g_waiver_validity(root: pathlib.Path) -> dict:
    """
    Ordem 5: WAIVER_VALIDITY_GATE implementation.
    Validates all waivers in contracts/_waivers/ against schema.
    Rejects waivers with:
    - expires_at_utc in the past
    - expires_at_utc missing (required field)
    - Invalid schema structure
    """
    t0 = time.monotonic()
    gate_id = "WAIVER_VALIDITY_GATE"
    waivers_dir = root / "contracts" / "_waivers"
    waiver_schema_path = root / "contracts" / "schemas" / "shared" / "waiver.schema.json"
    
    if not waivers_dir.exists():
        return _skip(gate_id, "Sem waivers em contracts/_waivers/.", _ms(t0))
    
    # Carregar schema do waiver
    try:
        waiver_schema = json.loads(waiver_schema_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return _pg(gate_id, "FAIL", True, "WAIVER_SCHEMA_INVALID",
                   f"Falha ao carregar waiver.schema.json: {exc}",
                   [str(waiver_schema_path)], [str(waiver_schema_path)], [], [], _ms(t0))
    
    violations: list[dict] = []
    checked_files: list[str] = []
    now = datetime.datetime.now(datetime.timezone.utc)
    
    waiver_files = [f for f in waivers_dir.glob("*.json") if f.name != "waiver.schema.json"]
    
    if not waiver_files:
        return _skip(gate_id, "Nenhum waiver para validar.", _ms(t0))
    
    for wpath in sorted(waiver_files):
        try:
            waiver_data = json.loads(wpath.read_text(encoding="utf-8"))
        except Exception as exc:
            violations.append({
                "blocking_code": "WAIVER_SCHEMA_INVALID",
                "artifact": str(wpath),
                "message": f"Falha ao parsear waiver JSON: {exc}",
                "severity": "error",
            })
            checked_files.append(str(wpath))
            continue
        
        checked_files.append(str(wpath))
        
        # Validar contra schema JSON
        try:
            from jsonschema import validate as _jsonschema_validate
            _jsonschema_validate(instance=waiver_data, schema=waiver_schema)
        except Exception as exc:
            violations.append({
                "blocking_code": "WAIVER_SCHEMA_INVALID",
                "artifact": str(wpath),
                "message": f"Waiver não conformou ao schema: {exc}",
                "severity": "error",
            })
            continue
        
        # Ordem 5: Validar expires_at_utc (obrigatório + não vencido)
        expires_str = waiver_data.get("expires_at_utc")
        
        if not expires_str:
            # Campo obrigatório pelo schema, mas dupla-check aqui
            violations.append({
                "blocking_code": "WAIVER_MISSING_EXPIRY",
                "artifact": str(wpath),
                "message": "Waiver sem expires_at_utc — campo obrigatório.",
                "severity": "error",
            })
            continue
        
        try:
            expiry = datetime.datetime.fromisoformat(expires_str.replace("Z", "+00:00"))
            if expiry.tzinfo is None:
                expiry = expiry.replace(tzinfo=datetime.timezone.utc)
        except ValueError:
            violations.append({
                "blocking_code": "WAIVER_SCHEMA_INVALID",
                "artifact": str(wpath),
                "message": f"expires_at_utc com formato inválido: {expires_str}",
                "severity": "error",
            })
            continue
        
        if expiry < now:
            violations.append({
                "blocking_code": "WAIVER_EXPIRED",
                "artifact": str(wpath),
                "message": f"Waiver vencido em {expires_str} — renovar ou remover.",
                "severity": "error",
            })
    
    if violations:
        return _pg(gate_id, "FAIL", True, violations[0].get("blocking_code", "WAIVER_SCHEMA_INVALID"),
                   f"{len(violations)} waiver(s) inválido(s) ou vencido(s).",
                   checked_files, [str(waivers_dir)], [str(waivers_dir)], violations, _ms(t0))
    
    return _pg(gate_id, "PASS", False, None,
               f"{len(waiver_files)} waiver(s) válido(s) e em vigência.",
               checked_files, [str(waivers_dir)], [str(waivers_dir)], [], _ms(t0))


def _g9_contract_breaking_change(root: pathlib.Path) -> dict:
    t0 = time.monotonic()
    gate_id = "CONTRACT_BREAKING_CHANGE_GATE"
    ci_environment = _is_ci_environment()
    baseline = root / "contracts" / "openapi" / "baseline" / "openapi_baseline.json"
    openapi_root = root / "contracts" / "openapi" / "openapi.yaml"
    if not baseline.exists():
        return _skip(
            gate_id,
            "baseline/openapi_baseline.json ausente — gate não aplicável na fase de scaffolding.",
            _ms(t0),
        )
    if not openapi_root.exists():
        return _skip(gate_id, "openapi.yaml ausente.", _ms(t0))
    # Preferência: oasdiff WSL-native (evitar wrappers Windows que chamam oasdiff.exe).
    oasdiff_path = shutil.which("oasdiff")
    can_use_oasdiff = False
    if oasdiff_path:
        p = pathlib.Path(oasdiff_path)
        # Bloquear interop Windows: /mnt/* e/ou binários .exe ou wrappers chamando .exe.
        if not str(p).startswith("/mnt/") and not str(p).lower().endswith(".exe"):
            try:
                head = p.read_bytes()[:256] if p.is_file() else b""
                if not head.startswith(b"#!"):
                    can_use_oasdiff = True
                else:
                    content = head.decode("utf-8", errors="replace").lower()
                    if ".exe" not in content and "cmd.exe" not in content and "powershell" not in content:
                        can_use_oasdiff = True
            except Exception:
                # Se não dá para inspecionar, ainda tentamos (pode ser binário Linux).
                can_use_oasdiff = True

    if can_use_oasdiff:
        rc, stdout, stderr = _try_tool("oasdiff", "breaking", str(baseline), str(openapi_root), cwd=root)
        output = (stdout + stderr).strip()
        if rc != 0 and _looks_like_wsl_vsock_failure(output):
            if ci_environment:
                return _pg(
                    gate_id,
                    "FAIL",
                    True,
                    "ERROR_INFRA",
                    "oasdiff é obrigatório em CI e falhou por interop/infra.",
                    [str(baseline), str(openapi_root)],
                    [str(baseline), str(openapi_root)],
                    [],
                    [{"blocking_code": "ERROR_INFRA", "artifact": "oasdiff", "message": output or "vsock/interoperability failure", "severity": "error"}],
                    _ms(t0),
                )
            can_use_oasdiff = False
        elif rc == 0:
            return _pg(
                gate_id,
                "PASS",
                True,
                None,
                "Nenhuma breaking change detectada (oasdiff).",
                [str(baseline), str(openapi_root)],
                [str(baseline), str(openapi_root)],
                [],
                [],
                _ms(t0),
            )
        else:
            if not output:
                return _pg(
                    gate_id,
                    "FAIL",
                    True,
                    "ERROR_INFRA",
                    "oasdiff falhou sem output (infra/execução).",
                    [str(baseline), str(openapi_root)],
                    [str(baseline), str(openapi_root)],
                    [],
                    [{"blocking_code": "ERROR_INFRA", "artifact": "oasdiff", "message": "no output", "severity": "error"}],
                    _ms(t0),
                )
            low = output.lower()
            if (
                "failed to load base spec" in low
                or "failed to load revision spec" in low
                or "failed to parse" in low
                or "failed to read" in low
            ):
                return _pg(
                    gate_id,
                    "FAIL",
                    True,
                    "ERROR_INFRA",
                    "oasdiff não conseguiu carregar/parsear specs (baseline e/ou atual).",
                    [str(baseline), str(openapi_root)],
                    [str(baseline), str(openapi_root)],
                    [],
                    [{"blocking_code": "ERROR_INFRA", "artifact": str(baseline.relative_to(root)), "message": output, "severity": "error"}],
                    _ms(t0),
                )
            lines = [ln for ln in output.splitlines() if ln.strip()]
            violations = [
                {"blocking_code": "BLOCKED_BREAKING_CHANGE", "artifact": str(openapi_root.relative_to(root)), "message": ln, "severity": "error"}
                for ln in lines[:20]
            ]
            waiver_path = _find_active_waiver(root, gate_id)
            if waiver_path:
                waiver_rel = str(waiver_path.relative_to(root))
                return _pg(
                    gate_id,
                    "PASS",
                    True,
                    None,
                    "Breaking change detectada — waiver ativo aprovado. Ver contracts/_waivers/.",
                    [str(baseline), str(openapi_root)],
                    [str(baseline), str(openapi_root), waiver_rel],
                    [waiver_rel],
                    [],
                    _ms(t0),
                )
            return _pg(
                gate_id,
                "FAIL",
                True,
                "BLOCKED_BREAKING_CHANGE",
                f"oasdiff: {len(violations)} breaking change(s) detectada(s).",
                [str(baseline), str(openapi_root)],
                [str(baseline), str(openapi_root)],
                [],
                violations,
                _ms(t0),
            )

    if ci_environment:
        return _pg(
            gate_id,
            "FAIL",
            True,
            "ERROR_INFRA",
            "oasdiff é obrigatório em CI para CONTRACT_BREAKING_CHANGE_GATE.",
            [str(baseline), str(openapi_root)],
            [str(baseline), str(openapi_root)],
            [],
            [{"blocking_code": "ERROR_INFRA", "artifact": "oasdiff", "message": "Ferramenta ausente ou indisponível no ambiente de CI.", "severity": "error"}],
            _ms(t0),
        )

    # Fallback determinístico (hermético): detectar remoção de operações (method+path).
    try:
        base_ops = _collect_openapi_operations(baseline)
        cur_ops = _collect_openapi_operations(openapi_root)
    except Exception as e:
        return _pg(
            gate_id,
            "FAIL",
            True,
            "ERROR_INFRA",
            "Não foi possível executar breaking change gate (oasdiff indisponível e fallback falhou).",
            [str(baseline), str(openapi_root)],
            [str(baseline), str(openapi_root)],
            [],
            [{"blocking_code": "ERROR_INFRA", "artifact": "openapi", "message": str(e), "severity": "error"}],
            _ms(t0),
        )

    removed = sorted(base_ops - cur_ops, key=lambda x: (x[1], x[0]))
    if removed:
        violations = [
            {
                "blocking_code": "BLOCKED_BREAKING_CHANGE",
                "artifact": str(openapi_root.relative_to(root)),
                "message": f"Operação removida: {m.upper()} {p}",
                "severity": "error",
            }
            for (m, p) in removed[:40]
        ]
        waiver_path = _find_active_waiver(root, gate_id)
        if waiver_path:
            waiver_rel = str(waiver_path.relative_to(root))
            return _pg(
                gate_id,
                "PASS",
                True,
                None,
                "Breaking change detectada — waiver ativo aprovado. Ver contracts/_waivers/.",
                [str(baseline), str(openapi_root)],
                [str(baseline), str(openapi_root), waiver_rel],
                [waiver_rel],
                [],
                _ms(t0),
            )
        return _pg(
            gate_id,
            "FAIL",
            True,
            "BLOCKED_BREAKING_CHANGE",
            f"Breaking change(s) detectada(s) (fallback: {len(removed)} operação(ões) removida(s)).",
            [str(baseline), str(openapi_root)],
            [str(baseline), str(openapi_root)],
            [],
            violations,
            _ms(t0),
        )

    return _pg(
        gate_id,
        "PASS",
        True,
        None,
        "Nenhuma breaking change detectada (fallback: nenhuma operação removida).",
        [str(baseline), str(openapi_root)],
        [str(baseline), str(openapi_root)],
        [],
        [],
        _ms(t0),
    )


def _g10_transformation_feasibility(root: pathlib.Path) -> dict:
    t0 = time.monotonic()
    gate_id = "TRANSFORMATION_FEASIBILITY_GATE"
    generated_dir = root / "generated"
    if not generated_dir.exists():
        return _skip(gate_id, "generated/ ausente — gate não aplicável.", _ms(t0))
    files = list(generated_dir.rglob("*"))
    if not files:
        return _skip(gate_id, "generated/ vazio — gate não aplicável.", _ms(t0))
    return _pg(gate_id, "PASS", False, None,
               f"generated/ presente com {len(files)} artefato(s).",
               [], [str(generated_dir)], [], [], _ms(t0))


def _g11_http_runtime_contract(root: pathlib.Path) -> dict:
    t0 = time.monotonic()
    gate_id = "HTTP_RUNTIME_CONTRACT_GATE"
    staging_url = os.environ.get("HB_STAGING_URL", "").strip()
    if not staging_url:
        return _skip(gate_id, "HB_STAGING_URL não definida — gate não aplicável em ambiente local.", _ms(t0))

    openapi_path = root / "contracts" / "openapi" / "openapi.yaml"
    if not openapi_path.exists():
        return _skip(gate_id, "contracts/openapi/openapi.yaml ausente.", _ms(t0))

    schema_url = staging_url.rstrip("/") + "/api/openapi.json"

    # Verificar conectividade antes de rodar schemathesis — evita timeout de 120s
    try:
        import urllib.request
        req = urllib.request.urlopen(
            urllib.request.Request(schema_url, method="HEAD"),
            timeout=10,
        )
    except Exception as _conn_err:
        return _skip(
            gate_id,
            f"Staging inacessível ({schema_url}): {_conn_err}. Gate ignorado até staging estar disponível.",
            _ms(t0),
        )

    # schemathesis v4 usa CLI `st run` (sem __main__.py — `python -m schemathesis` não funciona)
    st_cli = shutil.which("st") or shutil.which("schemathesis")
    if not st_cli:
        return _pg(gate_id, "FAIL", True, "ERROR_INFRA",
                   "schemathesis CLI (`st`) não encontrada. Execute: pip install schemathesis",
                   [], [], [],
                   [{"blocking_code": "ERROR_INFRA", "artifact": "schemathesis", "message": "st CLI not found", "severity": "error"}],
                   _ms(t0))
    cmd = [
        st_cli, "run",
        schema_url,
        "--url", staging_url.rstrip("/"),
        "--include-path-regex", r"^/api/(auth|users|teams|seasons|training)/",
        "--checks", "not_a_server_error,response_schema_conformance",
        "--max-examples", "5",
        "--request-timeout", "10",
        "--no-color",
    ]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=300, cwd=str(root))
        output = (proc.stdout + proc.stderr).strip()
    except FileNotFoundError:
        return _pg(gate_id, "FAIL", True, "ERROR_INFRA",
                   "schemathesis não instalado. Execute: pip install schemathesis",
                   [], [], [],
                   [{"blocking_code": "ERROR_INFRA", "artifact": "schemathesis", "message": "schemathesis not found", "severity": "error"}],
                   _ms(t0))
    except subprocess.TimeoutExpired:
        return _pg(gate_id, "FAIL", True, "ERROR_INFRA",
                   "schemathesis excedeu timeout de 300s.",
                   [], [], [],
                   [{"blocking_code": "ERROR_INFRA", "artifact": staging_url, "message": "timeout", "severity": "error"}],
                   _ms(t0))

    if proc.returncode != 0:
        violations = [
            {"blocking_code": "BLOCKED_RUNTIME_VIOLATION", "artifact": staging_url,
             "message": line, "severity": "error"}
            for line in output.splitlines()
            if line.strip() and any(kw in line for kw in ("FAILED", "Error", "error", "violation", "5xx"))
        ][:10] or [{"blocking_code": "BLOCKED_RUNTIME_VIOLATION", "artifact": staging_url,
                    "message": output[:500], "severity": "error"}]
        return _pg(gate_id, "FAIL", True, "BLOCKED_RUNTIME_VIOLATION",
                   f"API em {staging_url} viola contrato OpenAPI.",
                   [str(openapi_path)], [str(openapi_path)], [], violations, _ms(t0))

    return _pg(gate_id, "PASS", True, None,
               f"API em {staging_url} conforme contrato OpenAPI (Ciclo 1).",
               [str(openapi_path)], [str(openapi_path)], [], [], _ms(t0))


def _g12_asyncapi_validation(root: pathlib.Path) -> dict:
    t0 = time.monotonic()
    gate_id = "ASYNCAPI_VALIDATION_GATE"
    asyncapi_root = root / "contracts" / "asyncapi" / "asyncapi.yaml"
    if not asyncapi_root.exists():
        return _skip(gate_id, "contracts/asyncapi/asyncapi.yaml ausente — gate não aplicável.", _ms(t0))
    try:
        content = asyncapi_root.read_text(encoding="utf-8")
    except Exception:
        return _skip(gate_id, "Não foi possível ler asyncapi.yaml.", _ms(t0))
    if len(content.strip()) < 50:
        return _skip(gate_id, "asyncapi.yaml é scaffolding vazio — gate não aplicável.", _ms(t0))
    rc, stdout, stderr = _try_node_cli(root, tool="asyncapi", args=["validate", str(asyncapi_root)], cwd=root)
    out = stdout + stderr
    if rc == -1:
        return _pg(
            gate_id,
            "FAIL",
            True,
            "ERROR_INFRA",
            "asyncapi CLI não disponível via toolchain WSL-native (node_modules/NVM).",
            [str(asyncapi_root)],
            [str(asyncapi_root)],
            [],
            [{"blocking_code": "ERROR_INFRA", "artifact": "asyncapi", "message": out.strip() or stderr, "severity": "error"}],
            _ms(t0),
        )
    if rc != 0:
        if _looks_like_wsl_vsock_failure(out):
            return _pg(
                gate_id,
                "FAIL",
                True,
                "ERROR_INFRA",
                "asyncapi falhou por interop WSL/Windows (vsock). Use Node WSL-native e evite wrappers Windows.",
                [str(asyncapi_root)],
                [str(asyncapi_root)],
                [],
                [{"blocking_code": "ERROR_INFRA", "artifact": "asyncapi", "message": out.strip(), "severity": "error"}],
                _ms(t0),
            )
        if _looks_like_node_missing(out):
            return _pg(
                gate_id,
                "FAIL",
                True,
                "ERROR_INFRA",
                "asyncapi existe mas Node.js não está disponível no ambiente.",
                [str(asyncapi_root)],
                [str(asyncapi_root)],
                [],
                [{"blocking_code": "ERROR_INFRA", "artifact": "node", "message": out.strip(), "severity": "error"}],
                _ms(t0),
            )
        violations = [
            {"blocking_code": "BLOCKED_ASYNCAPI_INVALID", "artifact": "asyncapi.yaml", "message": ln, "severity": "error"}
            for ln in (out).splitlines()[:10]
            if ln.strip()
        ]
        return _pg(gate_id, "FAIL", True, "BLOCKED_ASYNCAPI_INVALID",
                   "asyncapi validate falhou.",
                   [str(asyncapi_root)], [str(asyncapi_root)], [], violations, _ms(t0))
    return _pg(gate_id, "PASS", True, None,
               "asyncapi validate: PASS.",
               [str(asyncapi_root)], [str(asyncapi_root)], [], [], _ms(t0))


def _g13_arazzo_validation(root: pathlib.Path) -> dict:
    t0 = time.monotonic()
    gate_id = "ARAZZO_VALIDATION_GATE"
    workflow_dir = root / "contracts" / "workflows"
    if not workflow_dir.exists():
        return _skip(gate_id, "contracts/workflows/ ausente — gate não aplicável.", _ms(t0))
    arazzo_files = sorted(workflow_dir.rglob("*.arazzo.yaml"))
    if not arazzo_files:
        return _skip(gate_id, "Nenhum arquivo *.arazzo.yaml encontrado — gate não aplicável.", _ms(t0))
    checked = [str(p) for p in arazzo_files]
    violations: list[dict] = []
    for p in arazzo_files:
        try:
            obj = _load_yaml(p)
        except Exception as e:
            violations.append({
                "blocking_code": "BLOCKED_ARAZZO_INVALID_YAML",
                "artifact": str(p.relative_to(root)),
                "message": f"YAML inválido: {e}",
                "severity": "error",
            })
            continue
        if not isinstance(obj, dict):
            violations.append({
                "blocking_code": "BLOCKED_ARAZZO_INVALID_YAML",
                "artifact": str(p.relative_to(root)),
                "message": "Arazzo file must be a mapping.",
                "severity": "error",
            })
            continue
        if "arazzo" not in obj:
            violations.append({
                "blocking_code": BLOCKED_ARAZZO_OPENAPI_LINK_MISSING,
                "artifact": str(p.relative_to(root)),
                "message": "Campo 'arazzo' ausente.",
                "severity": "error",
            })
        sources = obj.get("sourceDescriptions", [])
        has_openapi_link = any(
            isinstance(s, dict) and s.get("type") == "openapi" for s in sources
        )
        if not has_openapi_link:
            violations.append({
                "blocking_code": BLOCKED_ARAZZO_OPENAPI_LINK_MISSING,
                "artifact": str(p.relative_to(root)),
                "message": "Nenhuma sourceDescription do tipo 'openapi' encontrada.",
                "severity": "error",
            })
    if violations:
        return _pg(gate_id, "FAIL", False, BLOCKED_ARAZZO_OPENAPI_LINK_MISSING,
                   f"Arazzo: {len(violations)} erro(s).",
                   [], checked, [], violations, _ms(t0))
    return _pg(gate_id, "PASS", False, None,
               f"Arazzo: {len(arazzo_files)} arquivo(s) válido(s).",
               [], checked, [], [], _ms(t0))


def _g13a_spectral_linting(root: pathlib.Path) -> dict:
    t0 = time.monotonic()
    gate_id = "SPECTRAL_LINTING_GATE"
    openapi_root = root / "contracts" / "openapi" / "openapi.yaml"
    if not openapi_root.exists():
        return _skip(gate_id, "contracts/openapi/openapi.yaml ausente — gate não aplicável.", _ms(t0))
    
    rc, stdout, stderr = _try_node_cli(root, tool="spectral", args=["lint", str(openapi_root)], cwd=root)
    if rc == -1:
        return _pg(
            gate_id,
            "FAIL",
            True,
            "ERROR_INFRA",
            "spectral CLI não disponível via toolchain WSL-native (node_modules/NVM).",
            [str(openapi_root)],
            [str(openapi_root)],
            [],
            [{"blocking_code": "ERROR_INFRA", "artifact": "spectral", "message": stderr, "severity": "error"}],
            _ms(t0),
        )
    
    output = stdout + stderr
    
    # spectral retorna rc=0 se não há erros, rc>0 se há erros
    if rc != 0:
        # Extrair linhas de erro do output
        lines = [ln for ln in output.splitlines() if ln.strip() and any(sev in ln for sev in ["error", "warning"])]
        violations = [
            {"blocking_code": "BLOCKED_OPENAPI_SPECTRAL_VIOLATION", "artifact": str(openapi_root.relative_to(root)), "message": ln[:150], "severity": "error"}
            for ln in lines[:20]
        ]
        return _pg(gate_id, "FAIL", True, "BLOCKED_OPENAPI_SPECTRAL_VIOLATION",
                   f"spectral lint falhou (rc={rc}). Veja violations para detalhes.",
                   [str(openapi_root)], [str(openapi_root)], [], violations, _ms(t0))
    
    return _pg(gate_id, "PASS", True, None,
               "spectral lint: nenhum erro encontrado.",
               [str(openapi_root)], [str(openapi_root)], [], [], _ms(t0))


def _g14_ui_doc_validation(root: pathlib.Path) -> dict:
    t0 = time.monotonic()
    gate_id = "UI_DOC_VALIDATION_GATE"
    ui_dir = root / "docs" / "hbtrack" / "modulos"
    paths_dir = root / "contracts" / "openapi" / "paths"
    openapi_root_f = root / "contracts" / "openapi" / "openapi.yaml"
    if not ui_dir.exists():
        return _skip(gate_id, "docs/hbtrack/modulos/ ausente.", _ms(t0))
    ui_contracts = list(ui_dir.rglob("UI_CONTRACT_*.md"))
    if not ui_contracts:
        return _skip(gate_id, "Nenhum UI_CONTRACT_*.md encontrado.", _ms(t0))
    if not openapi_root_f.exists():
        return _skip(gate_id, "openapi.yaml ausente.", _ms(t0))
    import re as _re
    all_openapi_text = openapi_root_f.read_text(encoding="utf-8")
    if paths_dir.exists():
        for p in paths_dir.rglob("*.yaml"):
            all_openapi_text += "\n" + p.read_text(encoding="utf-8")
    defined_ops = set(_re.findall(r"operationId:\s*(\S+)", all_openapi_text))
    violations: list[dict] = []
    checked: list[str] = []
    operation_prefixes = (
        "accept",
        "add",
        "archive",
        "cancel",
        "close",
        "complete",
        "copy",
        "create",
        "delete",
        "dismiss",
        "escalate",
        "get",
        "list",
        "publish",
        "record",
        "remove",
        "reorder",
        "resolve",
        "start",
        "submit",
        "unpublish",
        "update",
    )
    for ui_contract in ui_contracts:
        checked.append(str(ui_contract.relative_to(root)))
        ui_text = ui_contract.read_text(encoding="utf-8")
        for token in _PLACEHOLDER_TOKENS:
            if token in ui_text:
                violations.append({
                    "blocking_code": "BLOCKED_UI_CONTRACT_PLACEHOLDER",
                    "artifact": str(ui_contract.relative_to(root)),
                    "message": f"Token placeholder '{token}' em UI contract.",
                    "severity": "error",
                })
                break
        candidates = set(_re.findall(r"`([a-z][a-zA-Z0-9]{5,})`", ui_text))
        op_refs = {
            ref for ref in candidates
            if any(char.isupper() for char in ref[1:])
            and ref.startswith(operation_prefixes)
        }
        for op in sorted(op_refs):
            if op not in defined_ops:
                violations.append({
                    "blocking_code": "BLOCKED_CONTRACT_CONFLICT",
                    "artifact": str(ui_contract.relative_to(root)),
                    "message": f"operationId '{op}' no UI contract não existe no OpenAPI.",
                    "severity": "error",
                })
    if violations:
        blocking_code = "BLOCKED_UI_CONTRACT_PLACEHOLDER" if any(
            v.get("blocking_code") == "BLOCKED_UI_CONTRACT_PLACEHOLDER" for v in violations
        ) else "BLOCKED_CONTRACT_CONFLICT"
        return _pg(gate_id, "FAIL", False, blocking_code,
                   f"{len(violations)} problema(s) em UI contracts.",
                   [], checked, [], violations, _ms(t0))
    return _pg(gate_id, "PASS", False, None,
               f"UI contracts alinhados com OpenAPI ({len(checked)} arquivo(s)).",
               [], checked, [], [], _ms(t0))


_SHA256_HEX_RE = re.compile(r"^[0-9a-f]{64}$")


def _tree_hash(entries: list[dict[str, str]]) -> str:
    h = hashlib.sha256()
    for e in sorted(entries, key=lambda x: x["path"]):
        h.update(e["path"].encode("utf-8"))
        h.update(b"\0")
        h.update(e["sha256"].encode("utf-8"))
        h.update(b"\n")
    return h.hexdigest()


def _is_safe_traceability_relpath(relpath: str) -> bool:
    if not isinstance(relpath, str) or not relpath.strip():
        return False
    if "\0" in relpath:
        return False
    if relpath.startswith("/") or relpath.startswith("\\"):
        return False
    if relpath.startswith("//"):
        return False
    if "\\" in relpath:
        return False
    if re.match(r"^[A-Za-z]:", relpath):
        return False
    parts = pathlib.PurePosixPath(relpath).parts
    if ".." in parts:
        return False
    return True


def _validate_traceability_entry_list(
    *,
    root: pathlib.Path,
    manifest_rel: str,
    list_name: str,
    entries: Any,
) -> tuple[list[dict[str, str]], bool, list[dict]]:
    violations: list[dict] = []
    if not isinstance(entries, list):
        return (
            [],
            False,
            [
                {
                    "blocking_code": BLOCKED_TRACEABILITY_MANIFEST_INVALID,
                    "artifact": manifest_rel,
                    "message": f"Campo `{list_name}` inválido: esperado lista.",
                    "severity": "error",
                }
            ],
        )

    root_resolved = root.resolve()
    ok = True
    actual_entries: list[dict[str, str]] = []
    seen: set[str] = set()
    for idx, e in enumerate(entries):
        if not isinstance(e, dict):
            ok = False
            violations.append(
                {
                    "blocking_code": BLOCKED_TRACEABILITY_MANIFEST_INVALID,
                    "artifact": manifest_rel,
                    "message": f"`{list_name}[{idx}]` inválido: esperado mapping com `path` e `sha256`.",
                    "severity": "error",
                }
            )
            continue

        p = e.get("path")
        s = e.get("sha256")
        if not isinstance(p, str) or not p:
            ok = False
            violations.append(
                {
                    "blocking_code": BLOCKED_TRACEABILITY_MANIFEST_INVALID,
                    "artifact": manifest_rel,
                    "message": f"`{list_name}[{idx}].path` ausente/ inválido.",
                    "severity": "error",
                }
            )
            continue
        if not _is_safe_traceability_relpath(p):
            ok = False
            violations.append(
                {
                    "blocking_code": BLOCKED_TRACEABILITY_MANIFEST_INVALID,
                    "artifact": manifest_rel,
                    "message": f"`{list_name}[{idx}].path` não é um path relativo seguro: {p!r}.",
                    "severity": "error",
                }
            )
            continue
        if p in seen:
            ok = False
            violations.append(
                {
                    "blocking_code": BLOCKED_TRACEABILITY_MANIFEST_INVALID,
                    "artifact": manifest_rel,
                    "message": f"`{list_name}` contém path duplicado: {p!r}.",
                    "severity": "error",
                }
            )
            continue
        seen.add(p)

        full = (root / pathlib.Path(p)).resolve()
        try:
            full.relative_to(root_resolved)
        except Exception:
            ok = False
            violations.append(
                {
                    "blocking_code": BLOCKED_TRACEABILITY_MANIFEST_INVALID,
                    "artifact": manifest_rel,
                    "message": f"`{list_name}[{idx}].path` sai do repo root: {p!r}.",
                    "severity": "error",
                }
            )
            continue

        if not full.exists():
            ok = False
            violations.append(
                {
                    "blocking_code": BLOCKED_TRACEABILITY_INPUT_MISSING,
                    "artifact": p,
                    "message": f"Arquivo referenciado por `{list_name}` não existe: {p}",
                    "severity": "error",
                }
            )
            continue

        try:
            data = full.read_bytes()
        except Exception as ex:  # pragma: no cover
            ok = False
            violations.append(
                {
                    "blocking_code": BLOCKED_TRACEABILITY_MANIFEST_INVALID,
                    "artifact": p,
                    "message": f"Falha ao ler arquivo referenciado por `{list_name}`: {p}: {ex}",
                    "severity": "error",
                }
            )
            continue

        actual_sha = hashlib.sha256(data).hexdigest()
        if not isinstance(s, str) or not _SHA256_HEX_RE.match(s):
            ok = False
            violations.append(
                {
                    "blocking_code": BLOCKED_TRACEABILITY_MANIFEST_INVALID,
                    "artifact": manifest_rel,
                    "message": f"`{list_name}[{idx}].sha256` inválido para {p!r}: esperado hex sha256 lowercase.",
                    "severity": "error",
                }
            )
            continue
        if s != actual_sha:
            ok = False
            violations.append(
                {
                    "blocking_code": BLOCKED_TRACEABILITY_HASH_MISMATCH,
                    "artifact": p,
                    "message": f"Hash sha256 divergente para {p} (manifest={s}, atual={actual_sha}).",
                    "severity": "error",
                }
            )
            continue

        actual_entries.append({"path": p, "sha256": actual_sha})

    return actual_entries, ok, violations


def _validate_traceability_manifests(root: pathlib.Path) -> tuple[list[str], list[dict]]:
    manifests_dir = root / "generated" / "manifests"
    if not manifests_dir.exists():
        return [], [
            {
                "blocking_code": BLOCKED_TRACEABILITY_MANIFEST_INVALID,
                "artifact": "generated/manifests/",
                "message": "Pasta de manifests de rastreabilidade ausente (generated/manifests/).",
                "severity": "error",
            }
        ]

    manifests = sorted(manifests_dir.glob("*.traceability.yaml")) + sorted(manifests_dir.glob("*.traceability.yml"))
    checked = [str(p.relative_to(root)) for p in manifests]
    if not manifests:
        return checked, [
            {
                "blocking_code": BLOCKED_TRACEABILITY_MANIFEST_INVALID,
                "artifact": "generated/manifests/",
                "message": "Nenhum manifest *.traceability.yaml encontrado em generated/manifests/.",
                "severity": "error",
            }
        ]

    root_resolved = root.resolve()
    violations: list[dict] = []
    for mf in manifests:
        mf_rel = str(mf.relative_to(root))
        try:
            obj = _load_yaml(mf)
        except Exception as e:
            violations.append(
                {
                    "blocking_code": BLOCKED_TRACEABILITY_MANIFEST_INVALID,
                    "artifact": mf_rel,
                    "message": f"Manifest YAML inválido: {e}",
                    "severity": "error",
                }
            )
            continue
        if not isinstance(obj, dict) or not isinstance(obj.get("traceability_manifest"), dict):
            violations.append(
                {
                    "blocking_code": BLOCKED_TRACEABILITY_MANIFEST_INVALID,
                    "artifact": mf_rel,
                    "message": "Estrutura inválida: esperado mapping com `traceability_manifest` (mapping).",
                    "severity": "error",
                }
            )
            continue

        tm = obj["traceability_manifest"]
        policy_path = tm.get("policy_path")
        policy_sha = tm.get("policy_sha256")
        if not isinstance(policy_path, str) or not _is_safe_traceability_relpath(policy_path):
            violations.append(
                {
                    "blocking_code": BLOCKED_TRACEABILITY_MANIFEST_INVALID,
                    "artifact": mf_rel,
                    "message": "`policy_path` ausente/ inválido no manifest.",
                    "severity": "error",
                }
            )
        else:
            full_policy = (root / pathlib.Path(policy_path)).resolve()
            try:
                full_policy.relative_to(root_resolved)
            except Exception:
                violations.append(
                    {
                        "blocking_code": BLOCKED_TRACEABILITY_MANIFEST_INVALID,
                        "artifact": mf_rel,
                        "message": f"`policy_path` sai do repo root: {policy_path!r}.",
                        "severity": "error",
                    }
                )
            else:
                if not full_policy.exists():
                    violations.append(
                        {
                            "blocking_code": BLOCKED_TRACEABILITY_INPUT_MISSING,
                            "artifact": policy_path,
                            "message": f"policy_path não existe: {policy_path}",
                            "severity": "error",
                        }
                    )
                else:
                    try:
                        actual_policy_sha = hashlib.sha256(full_policy.read_bytes()).hexdigest()
                    except Exception as ex:  # pragma: no cover
                        violations.append(
                            {
                                "blocking_code": BLOCKED_TRACEABILITY_MANIFEST_INVALID,
                                "artifact": policy_path,
                                "message": f"Falha ao ler policy_path: {policy_path}: {ex}",
                                "severity": "error",
                            }
                        )
                    else:
                        if not isinstance(policy_sha, str) or not _SHA256_HEX_RE.match(policy_sha):
                            violations.append(
                                {
                                    "blocking_code": BLOCKED_TRACEABILITY_MANIFEST_INVALID,
                                    "artifact": mf_rel,
                                    "message": "`policy_sha256` ausente/ inválido no manifest.",
                                    "severity": "error",
                                }
                            )
                        elif policy_sha != actual_policy_sha:
                            violations.append(
                                {
                                    "blocking_code": BLOCKED_TRACEABILITY_HASH_MISMATCH,
                                    "artifact": policy_path,
                                    "message": f"Hash sha256 divergente para policy ({policy_path}) (manifest={policy_sha}, atual={actual_policy_sha}).",
                                    "severity": "error",
                                }
                            )

        source_inputs_actual, ok_inputs, v_inputs = _validate_traceability_entry_list(
            root=root, manifest_rel=mf_rel, list_name="source_inputs", entries=tm.get("source_inputs")
        )
        violations.extend(v_inputs)

        source_contracts_actual, ok_sources, v_sources = _validate_traceability_entry_list(
            root=root, manifest_rel=mf_rel, list_name="source_contracts", entries=tm.get("source_contracts")
        )
        violations.extend(v_sources)

        generated_actual, ok_gen, v_gen = _validate_traceability_entry_list(
            root=root, manifest_rel=mf_rel, list_name="generated_artifacts", entries=tm.get("generated_artifacts")
        )
        violations.extend(v_gen)

        if ok_sources:
            got = tm.get("source_tree_sha256")
            expected = _tree_hash(source_contracts_actual)
            if not isinstance(got, str) or not _SHA256_HEX_RE.match(got):
                violations.append(
                    {
                        "blocking_code": BLOCKED_TRACEABILITY_MANIFEST_INVALID,
                        "artifact": mf_rel,
                        "message": "`source_tree_sha256` ausente/ inválido no manifest.",
                        "severity": "error",
                    }
                )
            elif got != expected:
                violations.append(
                    {
                        "blocking_code": BLOCKED_TRACEABILITY_HASH_MISMATCH,
                        "artifact": mf_rel,
                        "message": f"source_tree_sha256 divergente (manifest={got}, atual={expected}).",
                        "severity": "error",
                    }
                )

        if ok_gen:
            got = tm.get("generated_tree_sha256")
            expected = _tree_hash(generated_actual)
            if not isinstance(got, str) or not _SHA256_HEX_RE.match(got):
                violations.append(
                    {
                        "blocking_code": BLOCKED_TRACEABILITY_MANIFEST_INVALID,
                        "artifact": mf_rel,
                        "message": "`generated_tree_sha256` ausente/ inválido no manifest.",
                        "severity": "error",
                    }
                )
            elif got != expected:
                violations.append(
                    {
                        "blocking_code": BLOCKED_TRACEABILITY_HASH_MISMATCH,
                        "artifact": mf_rel,
                        "message": f"generated_tree_sha256 divergente (manifest={got}, atual={expected}).",
                        "severity": "error",
                    }
                )

    return checked, violations


def _g15_derived_drift(root: pathlib.Path) -> dict:
    t0 = time.monotonic()
    gate_id = "DERIVED_DRIFT_GATE"
    generated_dir = root / "generated"
    if not generated_dir.exists():
        return _pg(
            gate_id,
            "FAIL",
            True,
            BLOCKED_NON_NORMALIZED_DERIVED_DIFF_CHECK,
            "generated/ ausente — não há enforcement de artefatos derivados.",
            [],
            [str(generated_dir)],
            [],
            [
                {
                    "blocking_code": BLOCKED_NON_NORMALIZED_DERIVED_DIFF_CHECK,
                    "artifact": "generated/",
                    "message": "Pasta canônica de derivados (`generated/`) não existe.",
                    "severity": "error",
                }
            ],
            _ms(t0),
        )
    if not list(generated_dir.rglob("*")):
        return _pg(
            gate_id,
            "FAIL",
            True,
            BLOCKED_NON_NORMALIZED_DERIVED_DIFF_CHECK,
            "generated/ vazio — não há manifests/policies gerados para validar.",
            [],
            [str(generated_dir)],
            [],
            [
                {
                    "blocking_code": BLOCKED_NON_NORMALIZED_DERIVED_DIFF_CHECK,
                    "artifact": "generated/",
                    "message": "Pasta `generated/` existe mas está vazia.",
                    "severity": "error",
                }
            ],
            _ms(t0),
        )

    checked_manifests, trace_violations = _validate_traceability_manifests(root)
    if trace_violations:
        return _pg(
            gate_id,
            "FAIL",
            True,
            BLOCKED_TRACEABILITY_MANIFEST_INVALID,
            f"Manifests de rastreabilidade inválidos: {len(trace_violations)} erro(s).",
            checked_manifests,
            checked_manifests or [str(generated_dir)],
            [],
            trace_violations[:30],
            _ms(t0),
        )

    # Drift determinístico: recomputa o esperado via compiler e compara byte-a-byte.
    import sys

    scripts_dir = root / "scripts"
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))

    try:
        from contracts.validate.api.policy_compiler import (  # type: ignore
            PolicyCompilerError,
            check_expected,
            compile_all_expected,
            detect_global_input_recompile_gap,
        )
    except Exception as e:  # pragma: no cover
        return _pg(
            gate_id,
            "FAIL",
            True,
            BLOCKED_NON_NORMALIZED_DERIVED_DIFF_CHECK,
            f"Falha ao carregar compiler de policy: {e}",
            [],
            [str(generated_dir)],
            [],
            [
                {
                    "blocking_code": BLOCKED_NON_NORMALIZED_DERIVED_DIFF_CHECK,
                    "artifact": "scripts/contracts/validate/api/policy_compiler.py",
                    "message": f"Não foi possível importar o compiler: {e}",
                    "severity": "error",
                }
            ],
            _ms(t0),
        )

    try:
        global_input_gaps = detect_global_input_recompile_gap(root)
        if global_input_gaps:
            violations = [
                {
                    "blocking_code": BLOCKED_NON_NORMALIZED_DERIVED_DIFF_CHECK,
                    "artifact": source_path,
                    "message": "Mudança em input global detectada sem recompilação total de todos os manifests afetados.",
                    "severity": "error",
                    "details": {
                        "global_input_changed_not_fully_recompiled": True,
                        "stale_manifests": manifests,
                    },
                }
                for source_path, manifests in global_input_gaps.items()
            ]
            evidence_files = sorted({manifest for manifests in global_input_gaps.values() for manifest in manifests})
            return _pg(
                gate_id,
                "FAIL",
                True,
                BLOCKED_NON_NORMALIZED_DERIVED_DIFF_CHECK,
                "Mudança em input global exige `compile_api_policy.py --all` antes do pipeline.",
                [],
                [str(generated_dir)],
                evidence_files,
                violations,
                _ms(t0),
            )

        expected = compile_all_expected(root)
        drifts = check_expected(root, expected)
    except PolicyCompilerError as e:
        return _pg(
            gate_id,
            "FAIL",
            True,
            BLOCKED_NON_NORMALIZED_DERIVED_DIFF_CHECK,
            f"Compiler de policy falhou: {e}",
            [],
            [str(generated_dir)],
            [],
            [
                {
                    "blocking_code": BLOCKED_NON_NORMALIZED_DERIVED_DIFF_CHECK,
                    "artifact": "generated/",
                    "message": str(e),
                    "severity": "error",
                }
            ],
            _ms(t0),
        )

    if drifts:
        violations = [
            {
                "blocking_code": BLOCKED_NON_NORMALIZED_DERIVED_DIFF_CHECK,
                "artifact": d.relpath,
                "message": f"Drift detectado em artefato gerado ({d.reason}). Regerar: python3 scripts/contracts/validate/api/compile_api_policy.py --all",
                "severity": "error",
            }
            for d in drifts[:15]
        ]
        return _pg(
            gate_id,
            "FAIL",
            True,
            BLOCKED_NON_NORMALIZED_DERIVED_DIFF_CHECK,
            f"{len(drifts)} drift(s) detectado(s) em `generated/`.",
            [],
            [str(generated_dir)],
            [],
            violations,
            _ms(t0),
        )

    return _pg(
        gate_id,
        "PASS",
        True,
        None,
        "generated/ alinhado ao compiler determinístico (sem drift).",
        [],
        [str(generated_dir)],
        [],
        [],
        _ms(t0),
    )


def _g_adversarial_analysis(root: pathlib.Path) -> dict:
    t0 = time.monotonic()
    gate_id = "ADVERSARIAL_ANALYSIS_GATE"
    reports_dir = root / "_reports" / "adversarial"
    if not reports_dir.exists():
        return _skip(gate_id, "_reports/adversarial/ ausente — nenhum módulo submetido à análise adversarial.", _ms(t0))
    # FIX Ordem 2: descoberta robusta de relatórios — canônico primeiro, depois glob fallback
    report_files = []
    # Procurar no padrão canônico: _reports/adversarial/<module>/ALL.adversarial.json
    for subdir in reports_dir.iterdir():
        if subdir.is_dir():
            canonical = subdir / "ALL.adversarial.json"
            if canonical.exists():
                report_files.append(canonical)
    # Fallback: qualquer .adversarial.json não já encontrado
    for rpath in sorted(reports_dir.rglob("*.adversarial.json")):
        if rpath not in report_files:
            report_files.append(rpath)
    
    if not report_files:
        return _skip(gate_id, "_reports/adversarial/ vazia — nenhum relatório adversarial encontrado.", _ms(t0))
    checked = [str(p) for p in report_files]
    violations: list[dict] = []
    module_statuses: dict[str, str] = {}
    registry_path = root / "docs" / "_canon" / "MODULE_REGISTRY.yaml"
    if registry_path.exists():
        try:
            import yaml as _yaml
            registry = _yaml.safe_load(registry_path.read_text(encoding="utf-8")) or {}
            for module_name, module_data in (registry.get("modules") or {}).items():
                if isinstance(module_name, str) and isinstance(module_data, dict):
                    module_statuses[module_name] = module_data.get("status", "draft_contract")
        except Exception:
            module_statuses = {}
    for rpath in report_files:
        try:
            data = json.loads(rpath.read_text(encoding="utf-8"))
        except Exception as e:
            violations.append({"blocking_code": "BLOCKED_ADVERSARIAL_PENDING",
                               "artifact": str(rpath.relative_to(root)),
                               "message": f"Relatório adversarial não pôde ser lido: {e}",
                               "severity": "error"})
            continue
        overall = data.get("overall_status")
        score = data.get("score", 100)
        risks = data.get("risks") or []
        critical_open = len([
            risk for risk in risks
            if isinstance(risk, dict)
            and risk.get("severity") == "critical"
            and risk.get("status") not in ("resolved", "accepted")
        ])
        if overall != "PASS":
            module = data.get("module", "?")
            resource = data.get("resource", "?")
            findings = data.get("critical_findings", [])
            violations.append({"blocking_code": "BLOCKED_ADVERSARIAL_PENDING",
                               "artifact": str(rpath.relative_to(root)),
                               "message": (f"Análise adversarial FAIL: módulo={module}, recurso={resource}, "
                                           f"status={overall}, achados_críticos={len(findings)}"),
                               "severity": "error"})
        module_name = data.get("module", "")
        module_status = module_statuses.get(module_name, "draft_contract")
        min_score = 90 if module_status in IMPLEMENTATION_AUTHORIZED_STATUSES else 80
        if score < min_score:
            violations.append({
                "blocking_code": "BLOCKED_ADVERSARIAL_PENDING",
                "artifact": str(rpath.relative_to(root)),
                "message": f"Score {score}/100 < {min_score} exigido para status='{module_status}'.",
                "severity": "error",
            })
        if module_status in IMPLEMENTATION_AUTHORIZED_STATUSES and critical_open > 0:
            violations.append({
                "blocking_code": "BLOCKED_ADVERSARIAL_PENDING",
                "artifact": str(rpath.relative_to(root)),
                "message": f"{critical_open} risco(s) crítico(s) aberto(s) bloqueiam implementation_ready+.",
                "severity": "error",
            })
    if violations:
        # FIX Ordem 2: marcar como FAIL BLOQUEANTE (não warning)
        return _pg(gate_id, "FAIL", True, "BLOCKED_ADVERSARIAL_PENDING",
                   f"Análise adversarial: {len(violations)} violação(ões) encontradas.",
                   [], checked, [], violations, _ms(t0))
    return _pg(gate_id, "PASS", True, None,
               f"Análise adversarial: {len(report_files)} relatório(s) — todos PASS.",
               [], checked, [], [], _ms(t0))



def _g_handoff_coherence(root: pathlib.Path) -> dict:
    t0 = time.monotonic()
    gate_id = "HANDOFF_COHERENCE_GATE"
    handoff = root / "SESSION_HANDOFF.md"
    schema_path = root / "contracts" / "schemas" / "shared" / "session_handoff.schema.json"
    
    # FIX Ordem 4: SESSION_HANDOFF ausente deve ser FAIL, não SKIP
    if not handoff.exists():
        return _pg(gate_id, "FAIL", True, "BLOCKED_HANDOFF_INCOMPLETE",
                   "SESSION_HANDOFF.md ausente — artefato obrigatório.",
                   [], [str(handoff), str(schema_path)], [], [
                       {"blocking_code": "BLOCKED_HANDOFF_INCOMPLETE",
                        "artifact": "SESSION_HANDOFF.md",
                        "message": "SESSION_HANDOFF.md não encontrado na raiz do workspace.",
                        "severity": "error"}
                   ], _ms(t0))
    
    text = handoff.read_text(encoding="utf-8")
    checked = [str(handoff), str(schema_path)]
    violations: list[dict] = []

    front_matter = _parse_yaml_front_matter(handoff)
    if front_matter is None:
        violations.append({
            "blocking_code": "BLOCKED_HANDOFF_INCOMPLETE",
            "artifact": "SESSION_HANDOFF.md",
            "message": "Front matter YAML obrigatório ausente ou inválido em SESSION_HANDOFF.md.",
            "severity": "error",
        })

    if not schema_path.exists():
        violations.append({
            "blocking_code": "BLOCKED_HANDOFF_INCOMPLETE",
            "artifact": str(schema_path.relative_to(root)),
            "message": "Schema ativo de handoff ausente.",
            "severity": "error",
        })
    elif front_matter is not None:
        try:
            import jsonschema  # type: ignore

            schema = _load_json(schema_path)
            validator = jsonschema.Draft202012Validator(schema)
            errors = sorted(validator.iter_errors(front_matter), key=lambda err: list(err.absolute_path))
            for error in errors:
                path_str = ".".join(str(part) for part in error.absolute_path) or "$"
                violations.append({
                    "blocking_code": "BLOCKED_HANDOFF_INCOMPLETE",
                    "artifact": "SESSION_HANDOFF.md",
                    "message": f"Front matter inválido em {path_str}: {error.message}",
                    "severity": "error",
                })
        except Exception as exc:
            violations.append({
                "blocking_code": "BLOCKED_HANDOFF_INCOMPLETE",
                "artifact": "SESSION_HANDOFF.md",
                "message": f"Falha ao validar front matter contra session_handoff.schema.json: {exc}",
                "severity": "error",
            })

    required_sections = [
        "## Estado Geral",
        "## O que foi feito",
        "## Evidências",
        "## Próxima ação permitida",
        "## Bloqueios ativos",
    ]
    for section in required_sections:
        if section not in text:
            violations.append({
                "blocking_code": "BLOCKED_HANDOFF_INCOMPLETE",
                "artifact": "SESSION_HANDOFF.md",
                "message": f"Seção obrigatória '{section}' ausente do handoff.",
                "severity": "error",
            })
    
    import re as _re
    session_date_raw = front_matter.get("data_ultima_sessao") if isinstance(front_matter, dict) else None
    if session_date_raw:
        try:
            session_date = datetime.date.fromisoformat(str(session_date_raw))
            age_days = (datetime.date.today() - session_date).days
            if age_days < 0:
                violations.append({
                    "blocking_code": "BLOCKED_HANDOFF_INCOMPLETE",
                    "artifact": "SESSION_HANDOFF.md",
                    "message": (
                        f"data_ultima_sessao '{session_date}' está no futuro "
                        f"({abs(age_days)} dia(s) à frente de hoje) — handoff inválido."
                    ),
                    "severity": "error",
                })
            elif age_days > 30:
                violations.append({
                    "blocking_code": "BLOCKED_HANDOFF_INCOMPLETE",
                    "artifact": "SESSION_HANDOFF.md",
                    "message": f"data_ultima_sessao há {age_days} dias — handoff pode estar desatualizado.",
                    "severity": "warn",
                })
        except ValueError:
            pass
    try:
        proc = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True,
            text=True,
            cwd=root,
            timeout=5,
            check=False,
        )
        current_branch = proc.stdout.strip()
        branch_value = front_matter.get("branch_ativo") if isinstance(front_matter, dict) else None
        if branch_value and current_branch and str(branch_value) != current_branch:
            violations.append({
                "blocking_code": "BLOCKED_HANDOFF_INCOMPLETE",
                "artifact": "SESSION_HANDOFF.md",
                "message": f"branch_ativo='{branch_value}' != branch atual='{current_branch}'.",
                "severity": "error",  # FIX Ordem 4: erro, não warning
            })
    except Exception:
        pass
    if isinstance(front_matter, dict):
        mode = front_matter.get("modo_operacao")
        task_type = str(front_matter.get("task_type") or "")
        boot_profile = front_matter.get("boot_profile_id")
        if mode == "ROADMAP":
            if task_type != "execute_roadmap_phase":
                violations.append({
                    "blocking_code": "BLOCKED_HANDOFF_INCOMPLETE",
                    "artifact": "SESSION_HANDOFF.md",
                    "message": "modo_operacao=ROADMAP exige task_type=execute_roadmap_phase.",
                    "severity": "error",
                })
            if boot_profile != "roadmap_execution":
                violations.append({
                    "blocking_code": "BLOCKED_HANDOFF_INCOMPLETE",
                    "artifact": "SESSION_HANDOFF.md",
                    "message": "modo_operacao=ROADMAP exige boot_profile_id=roadmap_execution.",
                    "severity": "error",
                })
        if mode == "CDD" and boot_profile == "roadmap_execution":
            violations.append({
                "blocking_code": "BLOCKED_HANDOFF_INCOMPLETE",
                "artifact": "SESSION_HANDOFF.md",
                "message": "modo_operacao=CDD não pode usar boot_profile_id=roadmap_execution.",
                "severity": "error",
            })

        result_value = front_matter.get("resultado")
        blockers = front_matter.get("bloqueios_ativos") or []
        if result_value == "DONE" and blockers:
            violations.append({
                "blocking_code": "BLOCKED_HANDOFF_INCOMPLETE",
                "artifact": "SESSION_HANDOFF.md",
                "message": "resultado=DONE não pode coexistir com bloqueios_ativos não vazios.",
                "severity": "error",
            })
        if result_value == "BLOCKED" and not blockers:
            violations.append({
                "blocking_code": "BLOCKED_HANDOFF_INCOMPLETE",
                "artifact": "SESSION_HANDOFF.md",
                "message": "resultado=BLOCKED exige ao menos um item em bloqueios_ativos.",
                "severity": "error",
            })

        evidence_paths = front_matter.get("evidence_paths") or []
        report_evidence: dict | None = None
        for raw_path in evidence_paths:
            evidence_rel = pathlib.Path(str(raw_path))
            evidence_abs = root / evidence_rel
            checked.append(str(evidence_abs))
            if not evidence_abs.exists():
                violations.append({
                    "blocking_code": "BLOCKED_HANDOFF_INCOMPLETE",
                    "artifact": "SESSION_HANDOFF.md",
                    "message": f"Evidência declarada não existe: {raw_path}",
                    "severity": "error",
                })
                continue
            if evidence_abs.suffix != ".json":
                continue
            try:
                evidence_data = _load_json(evidence_abs)
            except Exception as exc:
                violations.append({
                    "blocking_code": "BLOCKED_HANDOFF_INCOMPLETE",
                    "artifact": "SESSION_HANDOFF.md",
                    "message": f"Evidência JSON inválida em {raw_path}: {exc}",
                    "severity": "error",
                })
                continue
            if evidence_data.get("pipeline_id") == "HB_TRACK_CONTRACT_GATES":
                report_evidence = evidence_data

        ci_status = front_matter.get("ci_status")
        if ci_status != "UNKNOWN":
            if report_evidence is None:
                violations.append({
                    "blocking_code": "BLOCKED_HANDOFF_INCOMPLETE",
                    "artifact": "SESSION_HANDOFF.md",
                    "message": "ci_status diferente de UNKNOWN exige relatório de gates em evidence_paths.",
                    "severity": "error",
                })
            else:
                execution_context = report_evidence.get("execution_context") or {}
                if execution_context.get("canonical_scope") != "full_pipeline":
                    violations.append({
                        "blocking_code": "BLOCKED_HANDOFF_INCOMPLETE",
                        "artifact": "SESSION_HANDOFF.md",
                        "message": "Handoff só pode usar relatório de gates com canonical_scope=full_pipeline.",
                        "severity": "error",
                    })
                overall = report_evidence.get("overall_status")
                if ci_status == "PASS" and overall != "PASS":
                    violations.append({
                        "blocking_code": "BLOCKED_HANDOFF_INCOMPLETE",
                        "artifact": "SESSION_HANDOFF.md",
                        "message": f"ci_status=PASS diverge do relatório canônico ({overall}).",
                        "severity": "error",
                    })
                if ci_status == "FAIL" and overall == "PASS":
                    violations.append({
                        "blocking_code": "BLOCKED_HANDOFF_INCOMPLETE",
                        "artifact": "SESSION_HANDOFF.md",
                        "message": "ci_status=FAIL diverge do relatório canônico PASS.",
                        "severity": "error",
                    })

    # Validação cruzada com _reports/session_start.json (FASE 3 — unified session state)
    session_json_path = root / "_reports" / "session_start.json"
    if session_json_path.exists() and isinstance(front_matter, dict):
        try:
            session_data = _load_json(session_json_path)
            _cross_checks = [
                ("operation_mode", "modo_operacao", "modo de operação"),
                ("module_focus", "modulo_foco", "módulo foco"),
            ]
            for sess_field, hoff_field, label in _cross_checks:
                sess_val = session_data.get(sess_field)
                hoff_val = front_matter.get(hoff_field)
                if sess_val and hoff_val and sess_val != hoff_val:
                    violations.append({
                        "blocking_code": "BLOCKED_HANDOFF_INCOMPLETE",
                        "artifact": "SESSION_HANDOFF.md",
                        "message": (
                            f"Divergência de {label}: "
                            f"session_start.{sess_field}='{sess_val}'"
                            f" != SESSION_HANDOFF.{hoff_field}='{hoff_val}'."
                        ),
                        "severity": "error",
                    })
            sess_phase = session_data.get("roadmap_phase")
            hoff_phase = front_matter.get("fase_roadmap")
            if sess_phase is not None and hoff_phase is not None and sess_phase != hoff_phase:
                violations.append({
                    "blocking_code": "BLOCKED_HANDOFF_INCOMPLETE",
                    "artifact": "SESSION_HANDOFF.md",
                    "message": (
                        f"Divergência de fase: session_start.roadmap_phase={sess_phase}"
                        f" != SESSION_HANDOFF.fase_roadmap={hoff_phase}."
                    ),
                    "severity": "error",
                })
            sess_tid = session_data.get("roadmap_task_id")
            hoff_tid = front_matter.get("task_id")
            if sess_tid and hoff_tid and sess_tid != hoff_tid:
                violations.append({
                    "blocking_code": "BLOCKED_HANDOFF_INCOMPLETE",
                    "artifact": "SESSION_HANDOFF.md",
                    "message": (
                        f"Divergência de task_id: session_start.roadmap_task_id='{sess_tid}'"
                        f" != SESSION_HANDOFF.task_id='{hoff_tid}'."
                    ),
                    "severity": "error",
                })
        except Exception:
            pass  # session_start.json inacessível ou malformado — cross-check ignorado

    if violations:
        return _pg(gate_id, "FAIL", True, "BLOCKED_HANDOFF_INCOMPLETE",
                   f"SESSION_HANDOFF.md com {len(violations)} inconsistência(s).",
                   checked, checked, [], violations, _ms(t0))
    return _pg(gate_id, "PASS", True, None,
               "SESSION_HANDOFF.md coerente com estado atual.",
               checked, checked, [], [], _ms(t0))


def _g_module_status_coherence(root: pathlib.Path) -> dict:
    t0 = time.monotonic()
    gate_id = "MODULE_STATUS_COHERENCE_GATE"
    registry_path = root / "docs" / "_canon" / "MODULE_REGISTRY.yaml"
    adversarial_dir = root / "_reports" / "adversarial"
    if not registry_path.exists():
        return _skip(gate_id, "MODULE_REGISTRY.yaml ausente.", _ms(t0))
    try:
        import yaml as _yaml
        with open(registry_path, encoding="utf-8") as handle:
            registry = _yaml.safe_load(handle) or {}
    except Exception as exc:
        return _pg(gate_id, "FAIL", True, "BLOCKED_REGISTRY_MISMATCH",
                   f"Falha ao ler MODULE_REGISTRY.yaml: {exc}",
                   [str(registry_path)], [str(registry_path)], [], [], _ms(t0))
    violations: list[dict] = []
    checked = [str(registry_path)]
    high_statuses = PRE_CONTRACT_EVIDENCE_STATUSES
    for mod_name, mod_data in (registry.get("modules") or {}).items():
        if not isinstance(mod_data, dict):
            continue
        status = mod_data.get("status", "draft_contract")
        if status not in high_statuses:
            continue
        expected_surfaces = list(mod_data.get("expected_surfaces") or [])
        missing_surfaces = [surface for surface in expected_surfaces if not _module_surface_present(root, mod_name, surface)]
        if missing_surfaces:
            violations.append({
                "blocking_code": "BLOCKED_REGISTRY_MISMATCH",
                "artifact": f"docs/_canon/MODULE_REGISTRY.yaml#{mod_name}",
                "message": (
                    f"Módulo '{mod_name}' está em status '{status}' mas ainda não materializa "
                    f"as superfícies esperadas: {', '.join(missing_surfaces)}."
                ),
                "severity": "error",
            })
        if not _module_has_pre_contract_evidence(root, mod_name):
            violations.append({
                "blocking_code": BLOCKED_PRE_CONTRACT_EVIDENCE,
                "artifact": "_reports/agent_execution/*.json",
                "message": (
                    f"Módulo '{mod_name}' está em status '{status}' sem evidência mínima "
                    "de continuidade pré-contrato."
                ),
                "severity": "error",
            })
        if not adversarial_dir.exists():
            continue
        for rpath in adversarial_dir.rglob(f"*{mod_name}*.adversarial.json"):
            checked.append(str(rpath))
            try:
                data = json.loads(rpath.read_text(encoding="utf-8"))
            except Exception:
                continue
            overall = data.get("overall_status", "PASS")
            critical_open = len([
                risk for risk in (data.get("risks") or [])
                if isinstance(risk, dict)
                and risk.get("severity") == "critical"
                and risk.get("status") not in ("resolved", "accepted")
            ])
            if overall != "PASS":
                violations.append({
                    "blocking_code": "BLOCKED_ADVERSARIAL_PENDING",
                    "artifact": str(rpath.relative_to(root)),
                    "message": (
                        f"Módulo '{mod_name}' status='{status}' mas adversarial={overall}. "
                        "Requer overall_status=PASS para manter este status."
                    ),
                    "severity": "error",
                })
            elif critical_open > 0 and status in IMPLEMENTATION_AUTHORIZED_STATUSES:
                violations.append({
                    "blocking_code": "BLOCKED_ADVERSARIAL_PENDING",
                    "artifact": str(rpath.relative_to(root)),
                    "message": (
                        f"Módulo '{mod_name}' status='{status}' com "
                        f"{critical_open} risco(s) crítico(s) em aberto."
                    ),
                    "severity": "error",
                })
    if violations:
        return _pg(gate_id, "FAIL", True, "BLOCKED_REGISTRY_MISMATCH",
                   f"Status incoerente em {len(violations)} módulo(s).",
                   [str(registry_path)], checked, [], violations, _ms(t0))
    return _pg(gate_id, "PASS", True, None,
               "Status de todos os módulos coerente com bloqueios adversariais.",
               [str(registry_path)], checked, [], [], _ms(t0))


def _g_surface_promotion_coherence(root: pathlib.Path) -> dict:
    """
    SURFACE_PROMOTION_COHERENCE_GATE

    Detecta módulos subpromovidos: quando todas as expected_surfaces declaradas no
    MODULE_REGISTRY estão presentes no filesystem mas o status do módulo não foi
    atualizado. Impede que passos de promoção sejam silenciosamente ignorados.

    Regras:
    - draft_contract + todas surfaces presentes → FAIL (BLOCKED_PROMOTION_PENDING)
      O agente criou todos os artefatos mas não atualizou MODULE_REGISTRY.yaml.
    - validated_contract + todas surfaces presentes → PASS com warn informativo.
      Elegível para implementation_ready, mas a promoção é decisão consciente.
    """
    t0 = time.monotonic()
    gate_id = "SURFACE_PROMOTION_COHERENCE_GATE"
    registry_path = root / "docs" / "_canon" / "MODULE_REGISTRY.yaml"

    if not registry_path.exists():
        return _skip(gate_id, "MODULE_REGISTRY.yaml ausente.", _ms(t0))

    try:
        import yaml as _yaml
        with open(registry_path, encoding="utf-8") as _fh:
            registry = _yaml.safe_load(_fh) or {}
    except Exception as exc:
        return _skip(gate_id, f"Falha ao ler MODULE_REGISTRY.yaml: {exc}", _ms(t0))

    violations: list[dict] = []
    checked = [str(registry_path)]

    for mod_name, mod_data in (registry.get("modules") or {}).items():
        if not isinstance(mod_data, dict):
            continue
        status = mod_data.get("status", "scaffold")
        expected: list[str] = mod_data.get("expected_surfaces") or []
        if not expected or status == "scaffold" or status in IMPLEMENTATION_AUTHORIZED_STATUSES:
            continue

        missing = [s for s in expected if not _module_surface_present(root, mod_name, s)]
        present = [s for s in expected if _module_surface_present(root, mod_name, s)]

        if status == "draft_contract" and not missing:
            violations.append({
                "blocking_code": "BLOCKED_PROMOTION_PENDING",
                "artifact": f"docs/_canon/MODULE_REGISTRY.yaml#{mod_name}",
                "message": (
                    f"Módulo '{mod_name}' tem todas as {len(expected)} superfícies "
                    f"declaradas presentes mas status='{status}'. "
                    f"Atualize MODULE_REGISTRY.yaml para 'validated_contract' e execute "
                    f"'python3 scripts/hb artifact docs/_canon/MODULE_REGISTRY.yaml'."
                ),
                "severity": "error",
                "details": {
                    "module": mod_name,
                    "current_status": status,
                    "expected_status": "validated_contract",
                    "surfaces_present": present,
                    "surfaces_missing": [],
                },
            })

        elif status == "validated_contract" and not missing:
            violations.append({
                "blocking_code": None,
                "artifact": f"docs/_canon/MODULE_REGISTRY.yaml#{mod_name}",
                "message": (
                    f"[INFO] Módulo '{mod_name}' tem todas as {len(expected)} superfícies "
                    f"em 'validated_contract'. Elegível para 'implementation_ready' via "
                    f"task_type=readiness_promotion quando pronto."
                ),
                "severity": "warn",
                "details": {
                    "module": mod_name,
                    "current_status": status,
                    "eligible_for": "implementation_ready",
                    "surfaces_present": present,
                },
            })

    blocking = [v for v in violations if v.get("blocking_code")]
    informational = [v for v in violations if not v.get("blocking_code")]

    if blocking:
        return _pg(
            gate_id, "FAIL", True, "BLOCKED_PROMOTION_PENDING",
            f"{len(blocking)} módulo(s) subpromovido(s): todas as superfícies presentes "
            f"mas MODULE_REGISTRY.yaml não foi atualizado.",
            [str(registry_path)], checked, [], violations, _ms(t0),
        )
    if informational:
        return _pg(
            gate_id, "PASS", True, None,
            f"Sem bloqueios. {len(informational)} módulo(s) elegível(-eis) para "
            f"promoção a implementation_ready (não bloqueante).",
            [str(registry_path)], checked, [], violations, _ms(t0),
        )
    return _pg(
        gate_id, "PASS", True, None,
        "Todos os módulos com status coerente com superfícies declaradas.",
        [str(registry_path)], checked, [], [], _ms(t0),
    )


def _g_cross_module_boundary(root: pathlib.Path) -> dict:
    t0 = time.monotonic()
    gate_id = "CROSS_MODULE_BOUNDARY_GATE"
    matrix_path = root / "docs" / "_canon" / "MODULE_SOURCE_AUTHORITY_MATRIX.yaml"
    if not matrix_path.exists():
        return _skip(gate_id, "MODULE_SOURCE_AUTHORITY_MATRIX.yaml ausente.", _ms(t0))
    try:
        import yaml as _yaml
        matrix = _yaml.safe_load(matrix_path.read_text(encoding="utf-8")) or {}
    except Exception as exc:
        return _skip(gate_id, f"Erro ao ler matrix: {exc}", _ms(t0))
    import re as _re
    violations: list[dict] = []
    checked = [str(matrix_path)]
    paths_dir = root / "contracts" / "openapi" / "paths"
    if not paths_dir.exists():
        return _skip(gate_id, "contracts/openapi/paths/ ausente.", _ms(t0))
    for boundary in (matrix.get("boundaries") or []):
        if not isinstance(boundary, dict):
            continue
        owner = boundary.get("owner_module", "")
        forbidden_patterns = boundary.get("forbidden_write_patterns") or []
        if not forbidden_patterns:
            continue
        for path_file in paths_dir.rglob("*.yaml"):
            checked.append(str(path_file))
            if owner and owner in path_file.stem:
                continue
            content = path_file.read_text(encoding="utf-8")
            for pattern in forbidden_patterns:
                if _re.search(pattern, content):
                    violations.append({
                        "blocking_code": "BLOCKED_SCOPE_OVERFLOW",
                        "artifact": str(path_file.relative_to(root)),
                        "message": (
                            f"Módulo '{path_file.stem}' contém padrão proibido '{pattern}' "
                            f"de propriedade de '{owner}'."
                        ),
                        "severity": "error",
                    })
    if violations:
        return _pg(gate_id, "FAIL", False, "BLOCKED_SCOPE_OVERFLOW",
                   f"{len(violations)} violação(ões) de fronteira cross-módulo.",
                   [str(matrix_path)], checked, [], violations, _ms(t0))
    return _pg(gate_id, "PASS", False, None,
               "Fronteiras cross-módulo respeitadas.",
               [str(matrix_path)], checked, [], [], _ms(t0))


def _g_module_dependency_resolution(root: pathlib.Path) -> dict:
    """C-002 — MODULE_DEPENDENCY_RESOLUTION_GATE.

    Varre todos os arquivos em contracts/ em busca de $ref externos (não-HTTP, não-fragmento
    local). Para cada $ref resolve o caminho relativo à origem e verifica a existência do
    arquivo alvo. Usa um cache para evitar rechecagem do mesmo arquivo (O(n) amortizado).
    Não itera recursivamente nos alvos (sem risco de ciclos O(n²)).
    """
    t0 = time.monotonic()
    gate_id = "MODULE_DEPENDENCY_RESOLUTION_GATE"
    contracts_dir = root / "contracts"
    if not contracts_dir.exists():
        return _skip(gate_id, "contracts/ ausente — gate não aplicável.", _ms(t0))

    violations: list[dict] = []
    checked: list[str] = []
    resolved_ok: set[str] = set()   # cache: abs-path str de alvos já verificados como existentes
    broken_seen: set[str] = set()   # evita duplicar a mesma violação

    for p in sorted(contracts_dir.rglob("*")):
        if p.suffix not in {".yaml", ".json"}:
            continue
        if not p.is_file():
            continue
        checked.append(str(p))
        try:
            obj = _load_json(p) if p.suffix == ".json" else _load_yaml(p)
        except Exception:
            continue

        refs: list[str] = []
        _collect_refs(obj, refs)

        for ref in refs:
            if not isinstance(ref, str):
                continue
            # Ignorar refs HTTP e fragmentos locais
            if ref.startswith(("http://", "https://", "#")):
                continue
            ref_path_str = ref.split("#")[0]
            if not ref_path_str:
                continue
            try:
                target = (p.parent / ref_path_str).resolve()
            except Exception:
                continue
            cache_key = str(target)
            if cache_key in resolved_ok:
                continue
            if not target.exists():
                if cache_key not in broken_seen:
                    broken_seen.add(cache_key)
                    violations.append({
                        "blocking_code": "BLOCKED_DEPENDENCY_RESOLUTION",
                        "artifact": str(p.relative_to(root)),
                        "message": f"$ref não resolvível: '{ref}'.",
                        "severity": "error",
                        "details": {"ref": ref, "resolved_path": str(target)},
                    })
            else:
                resolved_ok.add(cache_key)

    if violations:
        return _pg(gate_id, "FAIL", True, "BLOCKED_DEPENDENCY_RESOLUTION",
                   f"{len(violations)} $ref(s) não resolvível(eis) detectado(s).",
                   [], checked, [], violations, _ms(t0))
    return _pg(gate_id, "PASS", True, None,
               f"Todos os $refs em {len(checked)} arquivo(s) são resolvíveis.",
               [], checked, [], [], _ms(t0))


def _g_readiness_generation_compatibility(root: pathlib.Path) -> dict:
    """C-003 — READINESS_GENERATION_COMPATIBILITY_GATE.

    Para cada módulo com status `implementation_ready+` no MODULE_REGISTRY, verifica que
    existe relatório de análise adversarial em `_reports/adversarial/*.adversarial.json`
    com `overall_status == PASS`. Impede promoção de modules sem auditoria adversarial.
    Bloqueio: READINESS_GENERATION_INCOMPATIBLE.
    """
    t0 = time.monotonic()
    gate_id = "READINESS_GENERATION_COMPATIBILITY_GATE"
    registry_entries, checked = _load_module_registry_entries(root)
    if registry_entries is None:
        return _skip(gate_id, "MODULE_REGISTRY ausente ou inválido — gate não aplicável.", _ms(t0))

    ready_modules = sorted([
        module for module, entry in registry_entries.items()
        if entry.get("status") in IMPLEMENTATION_AUTHORIZED_STATUSES
    ])
    if not ready_modules:
        return _pg(gate_id, "PASS", True, None,
                   "Nenhum módulo em implementation_ready+ — gate não aplicável.",
                   [], checked, [], [], _ms(t0))

    adversarial_dir = root / "_reports" / "adversarial"
    checked.append(str(adversarial_dir))
    violations: list[dict] = []

    for module in ready_modules:
        report_found = False
        report_pass = False
        if adversarial_dir.exists():
            for rpath in sorted(adversarial_dir.glob("**/*.adversarial.json")):
                try:
                    data = json.loads(rpath.read_text(encoding="utf-8"))
                except Exception:
                    continue
                if data.get("module") == module:
                    report_found = True
                    if data.get("overall_status") == "PASS":
                        report_pass = True
                    break

        if not report_found:
            violations.append({
                "blocking_code": "READINESS_GENERATION_INCOMPATIBLE",
                "artifact": (
                    str(adversarial_dir.relative_to(root))
                    if adversarial_dir.exists()
                    else "_reports/adversarial/"
                ),
                "message": (
                    f"Módulo '{module}' está em status '{registry_entries[module].get('status')}' mas não possui "
                    "relatório de análise adversarial em _reports/adversarial/."
                ),
                "severity": "error",
                "details": {"module": module},
            })
        elif not report_pass:
            violations.append({
                "blocking_code": "READINESS_GENERATION_INCOMPATIBLE",
                "artifact": "_reports/adversarial/*.adversarial.json",
                "message": (
                    f"Módulo '{module}' está em status '{registry_entries[module].get('status')}' "
                    "mas análise adversarial não é PASS."
                ),
                "severity": "error",
                "details": {"module": module},
            })

    if violations:
        return _pg(gate_id, "FAIL", True, "READINESS_GENERATION_INCOMPATIBLE",
                   f"{len(violations)} módulo(s) implementation_ready+ sem análise adversarial PASS.",
                   [], checked, [], violations, _ms(t0))
    return _pg(gate_id, "PASS", True, None,
               f"{len(ready_modules)} módulo(s) implementation_ready+ com análise adversarial PASS.",
               [], checked, [], [], _ms(t0))


def _g_readiness_human_confirmation(root: pathlib.Path) -> dict:
    """
    Ordem 6: READINESS_HUMAN_CONFIRMATION_GATE implementation.
    
    Valida que confirmação humana antes de promoção para `implementation_ready`
    não é rubber-stamp. Requer resposta documentada e coerente a pergunta técnica
    sobre conteúdo real do módulo. Bloqueia se resposta for genérica ou incoerente.
    """
    t0 = time.monotonic()
    gate_id = "READINESS_HUMAN_CONFIRMATION_GATE"
    confirmations_dir = root / ".contract_driven" / "confirmations"
    
    # Gate não aplicável se nenhum módulo está sendo promovido
    registry_entries, checked = _load_module_registry_entries(root)
    if registry_entries is None:
        return _skip(gate_id, "MODULE_REGISTRY ausente — gate não aplicável.", _ms(t0))
    
    # Procurar por módulos em validated_contract (candidatos a promoção)
    # Este gate valida que Se alguém tentar promover, a confirmação deve estar válida
    validated_modules = sorted([
        module for module, entry in registry_entries.items()
        if entry.get("status") == "validated_contract"
    ])
    
    if not validated_modules:
        return _skip(gate_id, "Nenhum módulo em validated_contract aguardando promoção.", _ms(t0))
    
    if not confirmations_dir.exists():
        # Se não há artefato de confirmação e há módulos aguardando, é OK
        # O gate é "não-bloqueante" nesta fase; bloqueia só durante promoção real
        return _pg(gate_id, "PASS", False, None,
                   "Nenhuma confirmação pendente encontrada — gate não aplicável nesta fase.",
                   [], checked, [], [], _ms(t0))
    
    violations: list[dict] = []
    confirmations_checked: list[str] = []
    
    # Validar todas as confirmações existentes
    for conf_file in sorted(confirmations_dir.glob("*.json")):
        confirmations_checked.append(str(conf_file))
        
        try:
            conf_data = json.loads(conf_file.read_text(encoding="utf-8"))
        except Exception as exc:
            violations.append({
                "blocking_code": "READINESS_CONFIRMATION_INVALID",
                "artifact": str(conf_file),
                "message": f"Falha ao parsear confirmação JSON: {exc}",
                "severity": "error",
            })
            continue
        
        # Validar estrutura mínima
        required = ["confirmation_id", "module", "human_answer", "answer_validation_status", "coherence_check_result"]
        for field in required:
            if field not in conf_data:
                violations.append({
                    "blocking_code": "READINESS_CONFIRMATION_INVALID",
                    "artifact": str(conf_file),
                    "message": f"Campo obrigatório '{field}' ausente da confirmação.",
                    "severity": "error",
                })
                continue
        
        # Verificar se resposta é "genérica" (rubber-stamp)
        answer = str(conf_data.get("human_answer", "")).strip().lower()
        generic_answers = {"sim", "yes", "ok", "okay", "concordo", "aprovo", "pode ser", "tá bom", "tá bem"}
        if answer in generic_answers:
            violations.append({
                "blocking_code": "READINESS_CONFIRMATION_INCOHERENT",
                "artifact": str(conf_file),
                "message": f"Resposta genérica '{answer}' não constitui confirmação substantiva. "
                           "Responda com informação técnica que demonstre compreensão do módulo.",
                "severity": "error",
            })
            continue
        
        # Verificar coherence_check_result
        if conf_data.get("coherence_check_result") is not True:
            violations.append({
                "blocking_code": "READINESS_CONFIRMATION_INCOHERENT",
                "artifact": str(conf_file),
                "message": "Resposta técnica não é coerente com artefatos inspecionados. "
                           f"Validação: {conf_data.get('answer_validation_status', '?')}",
                "severity": "error",
            })
    
    if violations:
        return _pg(gate_id, "FAIL", True, violations[0].get("blocking_code", "READINESS_CONFIRMATION_INVALID"),
                   f"{len(violations)} confirmação(ões) inválida(s) ou genérica(s).",
                   [], confirmations_checked + checked, [], violations, _ms(t0))
    
    return _pg(gate_id, "PASS", False, None,
               f"Confirmações humanas válidas e coerentes (ou nenhuma pendente).",
               [], confirmations_checked + checked, [], [], _ms(t0))


def _g_arazzo_completeness(root: pathlib.Path) -> dict:
    """C-004 — ARAZZO_COMPLETENESS_GATE.

    Decisão (conforme PLANO C-004): obrigatório apenas para módulos que declaram
    `arazzo` em `expected_surfaces` no MODULE_REGISTRY. Módulos sem essa declaração
    não são verificados.

    Para cada módulo elegível verifica:
    1. Diretório `contracts/workflows/<module>/` existe.
    2. Pelo menos um arquivo `*.arazzo.yaml` presente.
    3. Cada arquivo tem raiz YAML com campo `workflows` contendo lista não-vazia.
    """
    t0 = time.monotonic()
    gate_id = "ARAZZO_COMPLETENESS_GATE"
    registry_entries, checked = _load_module_registry_entries(root)
    if registry_entries is None:
        return _skip(gate_id, "MODULE_REGISTRY ausente ou inválido — gate não aplicável.", _ms(t0))

    arazzo_modules = sorted([
        module for module, entry in registry_entries.items()
        if "arazzo" in set(entry.get("expected_surfaces") or [])
    ])
    if not arazzo_modules:
        return _skip(
            gate_id,
            "Nenhum módulo declara 'arazzo' em expected_surfaces — gate não aplicável.",
            _ms(t0),
        )

    violations: list[dict] = []
    workflows_dir = root / "contracts" / "workflows"
    checked.append(str(workflows_dir))

    for module in arazzo_modules:
        mod_dir = workflows_dir / module
        checked.append(str(mod_dir))
        if not mod_dir.exists() or not mod_dir.is_dir():
            violations.append({
                "blocking_code": "ARAZZO_COMPLETENESS_MISSING",
                "artifact": f"contracts/workflows/{module}/",
                "message": (
                    f"Módulo '{module}' declara 'arazzo' em expected_surfaces "
                    "mas diretório de workflows está ausente."
                ),
                "severity": "error",
                "details": {"module": module},
            })
            continue

        arazzo_files = list(mod_dir.glob("*.arazzo.yaml")) + list(mod_dir.glob("*.arazzo.yml"))
        if not arazzo_files:
            violations.append({
                "blocking_code": "ARAZZO_COMPLETENESS_MISSING",
                "artifact": f"contracts/workflows/{module}/",
                "message": (
                    f"Módulo '{module}' declara 'arazzo' em expected_surfaces "
                    "mas nenhum arquivo *.arazzo.yaml encontrado."
                ),
                "severity": "error",
                "details": {"module": module},
            })
            continue

        for af in sorted(arazzo_files):
            checked.append(str(af))
            try:
                data = _load_yaml(af)
            except Exception as exc:
                violations.append({
                    "blocking_code": "ARAZZO_COMPLETENESS_MISSING",
                    "artifact": str(af.relative_to(root)),
                    "message": f"Arazzo workflow não parseável: {exc}",
                    "severity": "error",
                })
                continue
            if not isinstance(data, dict):
                violations.append({
                    "blocking_code": "ARAZZO_COMPLETENESS_MISSING",
                    "artifact": str(af.relative_to(root)),
                    "message": "Arazzo workflow raiz deve ser objeto YAML.",
                    "severity": "error",
                })
                continue
            # Suporta tanto `workflows` (Arazzo 1.x) quanto chave legada
            workflows = data.get("workflows") or data.get("workflowsSpec")
            if not workflows or not isinstance(workflows, list) or len(workflows) == 0:
                violations.append({
                    "blocking_code": "ARAZZO_COMPLETENESS_MISSING",
                    "artifact": str(af.relative_to(root)),
                    "message": "Arazzo workflow deve conter pelo menos 1 workflow na lista 'workflows'.",
                    "severity": "error",
                })

    if violations:
        return _pg(gate_id, "FAIL", True, "ARAZZO_COMPLETENESS_MISSING",
                   f"{len(violations)} problema(s) de completude Arazzo.",
                   [], checked, [], violations, _ms(t0))
    return _pg(gate_id, "PASS", True, None,
               f"Completude Arazzo verificada para {len(arazzo_modules)} módulo(s).",
               [], checked, [], [], _ms(t0))


def _g_feature_readiness(root: pathlib.Path) -> dict:
    t0 = time.monotonic()
    gate_id = "FEATURE_READINESS_GATE"
    registry_path = root / "docs" / "_canon" / "FEATURE_REGISTRY.yaml"
    if not registry_path.exists():
        return _skip(gate_id, "FEATURE_REGISTRY.yaml ausente — gate não aplicável.", _ms(t0))
    try:
        import yaml as _yaml  # noqa: PLC0415
        with open(registry_path, encoding="utf-8") as _f:
            registry = _yaml.safe_load(_f)
    except Exception as e:
        return _pg(gate_id, "FAIL", False, "BLOCKED_FEATURE_UNREGISTERED",
                   f"FEATURE_REGISTRY.yaml não pôde ser lido: {e}",
                   [], [str(registry_path)], [], [], _ms(t0))
    violations: list[dict] = []
    if not isinstance(registry, dict):
        violations.append({"blocking_code": "BLOCKED_FEATURE_UNREGISTERED",
                           "artifact": str(registry_path.relative_to(root)),
                           "message": "FEATURE_REGISTRY.yaml não é um mapeamento YAML válido.",
                           "severity": "error"})
    else:
        features = registry.get("features")
        if not isinstance(features, list):
            violations.append({"blocking_code": "BLOCKED_FEATURE_UNREGISTERED",
                               "artifact": str(registry_path.relative_to(root)),
                               "message": "Campo 'features' ausente ou inválido.",
                               "severity": "error"})
        else:
            required_keys = {"id", "name", "module", "status"}
            valid_statuses = {"planned", "in_contract", "validated", "implemented", "released"}
            for i, ft in enumerate(features):
                missing = required_keys - set(ft.keys())
                if missing:
                    violations.append({
                        "blocking_code": "BLOCKED_FEATURE_UNREGISTERED",
                        "artifact": str(registry_path.relative_to(root)),
                        "message": f"Feature[{i}] '{ft.get('id', '?')}': campos obrigatórios ausentes: {sorted(missing)}",
                        "severity": "error",
                    })
                if ft.get("status") not in valid_statuses:
                    violations.append({
                        "blocking_code": "BLOCKED_FEATURE_UNREGISTERED",
                        "artifact": str(registry_path.relative_to(root)),
                        "message": f"Feature '{ft.get('id', '?')}': status '{ft.get('status')}' inválido.",
                        "severity": "error",
                    })
    if violations:
        return _pg(gate_id, "FAIL", False, "BLOCKED_FEATURE_UNREGISTERED",
                   f"FEATURE_REGISTRY.yaml inválido: {len(violations)} problema(s).",
                   [], [str(registry_path)], [], violations, _ms(t0))
    features_list = registry.get("features", [])
    from collections import Counter as _Counter  # noqa: PLC0415
    by_status = _Counter(ft.get("status") for ft in features_list)
    summary = (f"FEATURE_REGISTRY: {len(features_list)} features — "
               + ", ".join(f"{v} {k}" for k, v in sorted(by_status.items())))
    return _pg(gate_id, "PASS", False, None, summary,
               [], [str(registry_path)], [], [], _ms(t0))


def _g_versioning_policy(root: pathlib.Path) -> dict:
    """VERSIONING_POLICY_GATE — verifica conformidade com ADR-024.

    PASS  : ADR-024 existe, openapi.yaml tem SemVer válido e CANONICAL_TYPE_REGISTRY
            registra versioning_strategy em resolved_policies.
    FAIL  : ADR-024 ausente ou openapi.yaml sem SemVer (BLOCKED_VERSIONING_MISSING).
    DEGRADED: apenas aviso de registro no CANONICAL_TYPE_REGISTRY.
    """
    import re as _re
    t0 = time.monotonic()
    gate_id = "VERSIONING_POLICY_GATE"
    violations: list[dict] = []
    checked: list[str] = []

    # 1. ADR-024 deve existir
    adr_path = root / "docs" / "_canon" / "decisions" / "ADR-024-contract-versioning-strategy.md"
    checked.append(str(adr_path.relative_to(root)))
    if not adr_path.exists():
        violations.append({
            "blocking_code": "BLOCKED_VERSIONING_MISSING",
            "artifact": str(adr_path.relative_to(root)),
            "message": "ADR-024 ausente — estratégia de versionamento de contratos não documentada.",
            "severity": "error",
        })

    # 2. openapi.yaml deve ter versão SemVer válida
    openapi_path = root / "contracts" / "openapi" / "openapi.yaml"
    checked.append(str(openapi_path.relative_to(root)))
    if openapi_path.exists():
        try:
            text = openapi_path.read_text(encoding="utf-8")
            if not _re.search(r'(?m)^\s*version:\s*["\']?(\d+\.\d+\.\d+)["\']?', text):
                violations.append({
                    "blocking_code": "BLOCKED_VERSIONING_MISSING",
                    "artifact": "contracts/openapi/openapi.yaml",
                    "message": "openapi.yaml não tem versão SemVer válida (esperado: MAJOR.MINOR.PATCH).",
                    "severity": "error",
                })
        except Exception as exc:
            violations.append({
                "blocking_code": "BLOCKED_VERSIONING_MISSING",
                "artifact": "contracts/openapi/openapi.yaml",
                "message": f"Erro ao ler openapi.yaml: {exc}",
                "severity": "error",
            })
    else:
        violations.append({
            "blocking_code": "BLOCKED_VERSIONING_MISSING",
            "artifact": "contracts/openapi/openapi.yaml",
            "message": "contracts/openapi/openapi.yaml ausente.",
            "severity": "error",
        })

    # 3. CANONICAL_TYPE_REGISTRY deve registrar versioning_strategy (aviso)
    registry_path = root / ".contract_driven" / "templates" / "api" / "CANONICAL_TYPE_REGISTRY.yaml"
    checked.append(str(registry_path.relative_to(root)))
    if registry_path.exists():
        try:
            reg_text = registry_path.read_text(encoding="utf-8")
            if "versioning_strategy" not in reg_text:
                violations.append({
                    "blocking_code": "BLOCKED_VERSIONING_MISSING",
                    "artifact": str(registry_path.relative_to(root)),
                    "message": "CANONICAL_TYPE_REGISTRY não registra 'versioning_strategy' em resolved_policies.",
                    "severity": "warn",
                })
        except Exception as exc:
            violations.append({
                "blocking_code": "BLOCKED_VERSIONING_MISSING",
                "artifact": str(registry_path.relative_to(root)),
                "message": f"Erro ao ler CANONICAL_TYPE_REGISTRY: {exc}",
                "severity": "warn",
            })

    if violations:
        hard_errors = [v for v in violations if v.get("severity") == "error"]
        if hard_errors:
            return _pg(gate_id, "FAIL", False, "BLOCKED_VERSIONING_MISSING",
                       f"Política de versionamento: {len(hard_errors)} erro(s) — ADR-024 ou SemVer ausente.",
                       [], checked, [], violations, _ms(t0))
        return _pg(gate_id, "DEGRADED", False, None,
                   f"Política de versionamento: {len(violations)} aviso(s) de conformidade.",
                   [], checked, [], violations, _ms(t0))

    return _pg(gate_id, "PASS", False, None,
               "Política de versionamento: ADR-024 presente, SemVer válido, estratégia registrada.",
               [], checked, [], [], _ms(t0))


def _g_pact_provider(root: pathlib.Path) -> dict:
    """PACT_PROVIDER_GATE — verifica consumer contracts via Pact Broker.

    SKIP_NOT_APPLICABLE:
      - env var PACT_BROKER_BASE_URL ausente (broker não configurado)
      - contracts/consumers/ ausente ou vazia (sem consumers registrados)
    PASS : todos os consumer contracts satisfeitos (broker acessível + verificado)
    FAIL : BLOCKED_PACT_MISSING se algum contrato não for satisfeito
    """
    import os
    t0 = time.monotonic()
    gate_id = "PACT_PROVIDER_GATE"

    # 1. Broker configurado?
    broker_url = os.environ.get("PACT_BROKER_BASE_URL", "").strip()
    if not broker_url:
        return _skip(gate_id,
                     "PACT_BROKER_BASE_URL não configurado — Pact Broker não ativo. "
                     "Configurar quando o primeiro consumer contract for publicado.",
                     _ms(t0))

    # 2. Consumers registrados?
    consumers_dir = root / "contracts" / "consumers"
    if not consumers_dir.exists():
        return _skip(gate_id,
                     "contracts/consumers/ ausente — nenhum consumer registrado.",
                     _ms(t0))
    consumers = [d for d in consumers_dir.iterdir() if d.is_dir()]
    if not consumers:
        return _skip(gate_id,
                     "contracts/consumers/ vazia — nenhum consumer registrado.",
                     _ms(t0))

    # 3. Verificar via CLI pact-broker (se disponível)
    import shutil
    import subprocess
    pact_bin = shutil.which("pact-broker")
    if not pact_bin:
        # CLI não instalada — degradar, não falhar
        return _pg(gate_id, "DEGRADED", False, None,
                   "pact-broker CLI não instalada — verificação de consumer contracts não executada. "
                   "Instalar pact-broker para habilitar gate completo.",
                   [], [str(consumers_dir)], [], [], _ms(t0))

    violations: list[dict] = []
    checked = [str(consumers_dir)]
    try:
        result = subprocess.run(
            [pact_bin, "can-i-deploy",
             "--broker-base-url", broker_url,
             "--pacticipant", "hbtrack-app",
             "--latest"],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            violations.append({
                "blocking_code": "BLOCKED_PACT_MISSING",
                "artifact": "pact-broker/can-i-deploy",
                "message": f"Consumer contract não satisfeito: {result.stdout.strip() or result.stderr.strip()}",
                "severity": "error",
            })
    except subprocess.TimeoutExpired:
        violations.append({
            "blocking_code": "BLOCKED_PACT_MISSING",
            "artifact": "pact-broker/can-i-deploy",
            "message": "Timeout ao contactar Pact Broker — VPS Locaweb inacessível?",
            "severity": "error",
        })
    except Exception as exc:
        violations.append({
            "blocking_code": "BLOCKED_PACT_MISSING",
            "artifact": "pact-broker/can-i-deploy",
            "message": f"Erro ao executar verificação Pact: {exc}",
            "severity": "error",
        })

    if violations:
        return _pg(gate_id, "FAIL", False, "BLOCKED_PACT_MISSING",
                   f"Pact: consumer contract não satisfeito — deploy bloqueado.",
                   [], checked, [], violations, _ms(t0))
    return _pg(gate_id, "PASS", False, None,
               f"Pact: {len(consumers)} consumer(s) verificado(s) — todos satisfeitos.",
               [], checked, [], [], _ms(t0))


def _g_code_architecture(root: pathlib.Path) -> dict:
    """CODE_ARCHITECTURE_GATE — verifica conformidade com ADR-026.

    SKIP_NOT_APPLICABLE: 'src/' ainda não existe (pré-implementação).
    PASS : ADR-026 + CODE_ARCHITECTURE.md existem; módulos implementation_ready+ têm src/<module>/.
    FAIL : ADR-026 ou CODE_ARCHITECTURE.md ausentes (BLOCKED_MISSING_ARCH_DECISION).
    """
    t0 = time.monotonic()
    gate_id = "CODE_ARCHITECTURE_GATE"
    violations: list[dict] = []
    checked: list[str] = []

    # 1. ADR-026 deve existir
    adr_path = root / "docs" / "_canon" / "decisions" / "ADR-026-code-architecture.md"
    checked.append(str(adr_path.relative_to(root)))
    if not adr_path.exists():
        violations.append({
            "blocking_code": "BLOCKED_MISSING_ARCH_DECISION",
            "artifact": str(adr_path.relative_to(root)),
            "message": "ADR-026 ausente — arquitetura de código não documentada.",
            "severity": "error",
        })

    # 2. CODE_ARCHITECTURE.md deve existir
    arch_path = root / "docs" / "_canon" / "CODE_ARCHITECTURE.md"
    checked.append(str(arch_path.relative_to(root)))
    if not arch_path.exists():
        violations.append({
            "blocking_code": "BLOCKED_MISSING_ARCH_DECISION",
            "artifact": "docs/_canon/CODE_ARCHITECTURE.md",
            "message": "CODE_ARCHITECTURE.md ausente — referência normativa da arquitetura não encontrada.",
            "severity": "error",
        })

    # 3. Se src/ ainda não existe — SKIP (pré-implementação)
    src_dir = root / "src"
    if not src_dir.exists():
        if not violations:
            return _skip(gate_id,
                         "'src/' ainda não existe — pré-implementação. "
                         "ADR-026 e CODE_ARCHITECTURE.md presentes e prontos.",
                         _ms(t0))
        # ADR ou arch ausentes + sem src — reportar erros
        hard = [v for v in violations if v.get("severity") == "error"]
        return _pg(gate_id, "FAIL", False, "BLOCKED_MISSING_ARCH_DECISION",
                   f"Arquitetura de código: {len(hard)} artefato(s) obrigatório(s) ausente(s).",
                   [], checked, [], violations, _ms(t0))

    # 4. Para módulos implementation_ready+ — verificar src/<module>/
    registry_path = root / "docs" / "_canon" / "MODULE_REGISTRY.yaml"
    if registry_path.exists():
        try:
            registry = _load_yaml(registry_path)
            modules_section = registry.get("modules", {})
            ready_modules = [
                m for m, info in modules_section.items()
                if isinstance(info, dict) and info.get("status") in IMPLEMENTATION_AUTHORIZED_STATUSES
            ]
            for mod in ready_modules:
                mod_src = src_dir / mod
                checked.append(str(mod_src.relative_to(root)))
                if not mod_src.exists():
                    violations.append({
                        "blocking_code": "BLOCKED_MISSING_ARCH_DECISION",
                        "artifact": str(mod_src.relative_to(root)),
                        "message": f"Módulo '{mod}' está em status '{modules_section[mod].get('status')}' mas src/{mod}/ não existe.",
                        "severity": "warn",
                    })
        except Exception:
            pass

    hard_errors = [v for v in violations if v.get("severity") == "error"]
    if hard_errors:
        return _pg(gate_id, "FAIL", False, "BLOCKED_MISSING_ARCH_DECISION",
                   f"Arquitetura de código: {len(hard_errors)} erro(s) — ADR-026 ou CODE_ARCHITECTURE.md ausente(s).",
                   [], checked, [], violations, _ms(t0))
    if violations:
        return _pg(gate_id, "DEGRADED", False, None,
                   f"Arquitetura de código: {len(violations)} aviso(s) — módulo(s) implementation_ready+ sem src/.",
                   [], checked, [], violations, _ms(t0))
    return _pg(gate_id, "PASS", False, None,
               "Arquitetura de código: ADR-026 presente, CODE_ARCHITECTURE.md presente.",
               [], checked, [], [], _ms(t0))



def _g_deploy_readiness(root: pathlib.Path) -> dict:
    t0 = time.monotonic()
    gate_id = "DEPLOY_READINESS_GATE"
    violations: list[dict] = []
    checked: list[str] = []

    deploy_pipeline = root / "docs" / "_canon" / "DEPLOY_PIPELINE.md"
    adr_027 = root / "docs" / "_canon" / "decisions" / "ADR-027-deploy-pipeline.md"
    deploy_yml = root / ".github" / "workflows" / "deploy.yml"

    has_pipeline = deploy_pipeline.exists()
    has_adr = adr_027.exists()
    has_yml = deploy_yml.exists()

    checked += [
        str(deploy_pipeline.relative_to(root)),
        str(adr_027.relative_to(root)),
        str(deploy_yml.relative_to(root)),
    ]

    # Nenhum existe -> SKIP (ainda nao foi configurado)
    if not has_pipeline and not has_adr and not has_yml:
        return _skip(gate_id,
                     "Nenhum artefato de deploy encontrado -- pre-configuracao de deploy.",
                     _ms(t0))

    # Algum existe mas incompleto -> FAIL
    missing = []
    if not has_pipeline:
        missing.append("docs/_canon/DEPLOY_PIPELINE.md")
    if not has_adr:
        missing.append("docs/_canon/decisions/ADR-027-deploy-pipeline.md")
    if not has_yml:
        missing.append(".github/workflows/deploy.yml")

    if missing:
        for m in missing:
            violations.append({
                "blocking_code": "BLOCKED_MISSING_ARCH_DECISION",
                "message": f"Artefato de deploy ausente: {m}",
                "file": m,
            })
        return _pg(gate_id, "FAIL", False, "BLOCKED_MISSING_ARCH_DECISION",
                   f"Deploy parcialmente configurado -- {len(missing)} artefato(s) ausente(s).",
                   violations, checked, [], [], _ms(t0))

    return _pg(gate_id, "PASS", False, None,
               "Deploy configurado: DEPLOY_PIPELINE.md, ADR-027 e deploy.yml presentes.",
               [], checked, [], [], _ms(t0))


def _g_data_migration(root: pathlib.Path) -> dict:
    t0 = time.monotonic()
    gate_id = "DATA_MIGRATION_GATE"
    violations: list[dict] = []
    checked: list[str] = []

    policy = root / "docs" / "_canon" / "DATA_MIGRATION_POLICY.md"
    adr_028 = root / "docs" / "_canon" / "decisions" / "ADR-028-data-migration-strategy.md"
    migrations_dir = root / "migrations"

    has_policy = policy.exists()
    has_adr = adr_028.exists()
    has_migrations = migrations_dir.exists()

    checked += [
        str(policy.relative_to(root)),
        str(adr_028.relative_to(root)),
        "migrations/",
    ]

    # Nenhum existe -> SKIP (pre-implementacao)
    if not has_policy and not has_adr and not has_migrations:
        return _skip(gate_id,
                     "Nenhum artefato de migration encontrado -- pre-implementacao.",
                     _ms(t0))

    # Algum existe mas incompleto -> FAIL
    missing = []
    if not has_policy:
        missing.append("docs/_canon/DATA_MIGRATION_POLICY.md")
    if not has_adr:
        missing.append("docs/_canon/decisions/ADR-028-data-migration-strategy.md")
    if not has_migrations:
        missing.append("migrations/")

    if missing:
        for m in missing:
            violations.append({
                "blocking_code": "BLOCKED_MISSING_ARCH_DECISION",
                "message": f"Artefato de migration ausente: {m}",
                "file": m,
            })
        return _pg(gate_id, "FAIL", False, "BLOCKED_MISSING_ARCH_DECISION",
                   f"Migration parcialmente configurada -- {len(missing)} artefato(s) ausente(s).",
                   violations, checked, [], [], _ms(t0))

    return _pg(gate_id, "PASS", False, None,
               "Migration configurada: DATA_MIGRATION_POLICY.md, ADR-028 e migrations/ presentes.",
               [], checked, [], [], _ms(t0))


def _g_monitoring_policy(root: pathlib.Path) -> dict:
    t0 = time.monotonic()
    gate_id = "MONITORING_POLICY_GATE"
    violations: list[dict] = []
    checked: list[str] = []

    policy = root / "docs" / "_canon" / "RUNTIME_CONTRACT_MONITORING_POLICY.md"
    adr_029 = root / "docs" / "_canon" / "decisions" / "ADR-029-runtime-monitoring.md"

    has_policy = policy.exists()
    has_adr = adr_029.exists()

    checked += [
        str(policy.relative_to(root)),
        str(adr_029.relative_to(root)),
    ]

    # Nenhum existe -> SKIP
    if not has_policy and not has_adr:
        return _skip(gate_id,
                     "Nenhum artefato de monitoramento encontrado -- pre-implementacao.",
                     _ms(t0))

    # Apenas um existe -> DEGRADED
    if has_policy != has_adr:
        missing = str(adr_029.relative_to(root)) if has_policy else str(policy.relative_to(root))
        violations.append({
            "blocking_code": "BLOCKED_MISSING_ARCH_DECISION",
            "message": f"Artefato de monitoramento ausente: {missing}",
            "file": missing,
        })
        return _pg(gate_id, "DEGRADED", False, None,
                   "Monitoramento parcialmente configurado -- 1 artefato ausente.",
                   violations, checked, [], [], _ms(t0))

    return _pg(gate_id, "PASS", False, None,
               "Monitoramento configurado: RUNTIME_CONTRACT_MONITORING_POLICY.md e ADR-029 presentes.",
               [], checked, [], [], _ms(t0))

def _g_feature_coverage(root: pathlib.Path) -> dict:
    """FEATURE_COVERAGE_GATE — todo módulo `implemented` no MODULE_REGISTRY deve ter
    ao menos uma feature com status `implemented` no FEATURE_REGISTRY.

    SKIP_NOT_APPLICABLE: MODULE_REGISTRY ou FEATURE_REGISTRY ausente/inválido.
    PASS : todos os módulos implemented têm cobertura mínima.
    FAIL : um ou mais módulos implemented sem nenhuma feature implemented.
    """
    t0 = time.monotonic()
    gate_id = "FEATURE_COVERAGE_GATE"

    registry_path = root / "docs" / "_canon" / "MODULE_REGISTRY.yaml"
    feature_path = root / "docs" / "_canon" / "FEATURE_REGISTRY.yaml"
    checked = [str(registry_path), str(feature_path)]

    if not registry_path.exists():
        return _skip(gate_id, "MODULE_REGISTRY.yaml ausente — gate não aplicável.", _ms(t0))
    if not feature_path.exists():
        return _skip(gate_id, "FEATURE_REGISTRY.yaml ausente — gate não aplicável.", _ms(t0))

    try:
        registry = _load_yaml(registry_path)
    except Exception as e:
        return _pg(gate_id, "FAIL", True, BLOCKED_FEATURE_COVERAGE_MISSING,
                   f"MODULE_REGISTRY.yaml inválido: {e}", [], checked, [], [], _ms(t0))

    try:
        feature_registry = _load_yaml(feature_path)
    except Exception as e:
        return _pg(gate_id, "FAIL", True, BLOCKED_FEATURE_COVERAGE_MISSING,
                   f"FEATURE_REGISTRY.yaml inválido: {e}", [], checked, [], [], _ms(t0))

    if not isinstance(registry, dict) or not isinstance(registry.get("modules"), dict):
        return _skip(gate_id, "MODULE_REGISTRY.yaml sem chave 'modules' — gate não aplicável.", _ms(t0))
    if not isinstance(feature_registry, dict) or not isinstance(feature_registry.get("features"), list):
        return _skip(gate_id, "FEATURE_REGISTRY.yaml sem chave 'features' — gate não aplicável.", _ms(t0))

    # Módulos com status=implemented
    implemented_modules = [
        m for m, entry in registry["modules"].items()
        if isinstance(entry, dict) and entry.get("status") == "implemented"
    ]

    # Features implemented por módulo
    features_by_module: dict[str, list[str]] = {}
    for ft in feature_registry["features"]:
        if not isinstance(ft, dict):
            continue
        mod = ft.get("module")
        status = ft.get("status")
        if isinstance(mod, str) and mod and status == "implemented":
            features_by_module.setdefault(mod, []).append(str(ft.get("id", "?")))

    violations: list[dict] = []
    for module in sorted(implemented_modules):
        covered = features_by_module.get(module, [])
        if not covered:
            violations.append({
                "blocking_code": BLOCKED_FEATURE_COVERAGE_MISSING,
                "artifact": str(feature_path.relative_to(root)),
                "message": (
                    f"Módulo `{module}` tem status `implemented` no MODULE_REGISTRY mas não possui "
                    "nenhuma feature com status `implemented` no FEATURE_REGISTRY."
                ),
                "severity": "error",
                "details": {"module": module},
            })

    if violations:
        return _pg(
            gate_id,
            "FAIL",
            True,
            BLOCKED_FEATURE_COVERAGE_MISSING,
            f"{len(violations)} módulo(s) implemented sem cobertura de feature.",
            [],
            checked,
            [],
            violations,
            _ms(t0),
        )

    total_covered = len([m for m in implemented_modules if features_by_module.get(m)])
    return _pg(
        gate_id,
        "PASS",
        True,
        None,
        f"Cobertura de features OK: {total_covered}/{len(implemented_modules)} módulos implemented cobertos.",
        [],
        checked,
        [],
        [],
        _ms(t0),
    )


def _g_legacy_isolation(root: pathlib.Path) -> dict:
    """LEGACY_CRITICAL_PATH_GATE — FASE 7.

    Garante que artefatos legados conhecidos:
      1. _reports/evidence/boot_resolution_report.json → tem ``"_legacy": true``
      2. scripts/hbtrack_lint/__init__.py → contém aviso de LEGACY/legado/deprecated
      3. Nenhum arquivo do caminho crítico (scripts/hb, validate_contracts.py) referencia hbtrack_lint

    SKIP_NOT_APPLICABLE: nenhum artefato legado encontrado (ambiente sem legado — ok em CI limpo).
    PASS: todos os artefatos legados estão marcados e isolados.
    FAIL: artefato legado sem marcador ou referenciado no caminho crítico.
    """
    t0 = time.monotonic()
    gate_id = "LEGACY_CRITICAL_PATH_GATE"

    boot_report = root / "_reports" / "evidence" / "boot_resolution_report.json"
    hbtrack_lint_init = root / "scripts" / "hbtrack_lint" / "__init__.py"
    critical_files = [
        root / "scripts" / "hb",
        root / "scripts" / "contracts" / "validate" / "validate_contracts.py",
    ]
    checked = [str(boot_report), str(hbtrack_lint_init)] + [str(p) for p in critical_files]

    any_legacy_present = boot_report.exists() or hbtrack_lint_init.exists()
    if not any_legacy_present:
        return _skip(gate_id, "Nenhum artefato legado monitorado encontrado.", _ms(t0))

    violations: list[dict] = []

    # 1. boot_resolution_report.json deve ter "_legacy": true
    if boot_report.exists():
        try:
            import json as _json
            data = _json.loads(boot_report.read_text(encoding="utf-8"))
            if not data.get("_legacy"):
                violations.append({
                    "blocking_code": BLOCKED_LEGACY_IN_CRITICAL_PATH,
                    "artifact": str(boot_report.relative_to(root)),
                    "message": (
                        "boot_resolution_report.json existe mas não tem '_legacy: true'. "
                        "Marcar como legado para impedir reintrodução no fluxo ativo."
                    ),
                    "severity": "error",
                })
        except Exception as exc:
            violations.append({
                "blocking_code": BLOCKED_LEGACY_IN_CRITICAL_PATH,
                "artifact": str(boot_report.relative_to(root)),
                "message": f"Falha ao ler boot_resolution_report.json: {exc}",
                "severity": "error",
            })

    # 2. scripts/hbtrack_lint/__init__.py deve mencionar LEGACY/legado/deprecated
    if hbtrack_lint_init.exists():
        try:
            text = hbtrack_lint_init.read_text(encoding="utf-8", errors="replace")
            if not re.search(r"LEGACY|legado|deprecated", text, re.IGNORECASE):
                violations.append({
                    "blocking_code": BLOCKED_LEGACY_IN_CRITICAL_PATH,
                    "artifact": str(hbtrack_lint_init.relative_to(root)),
                    "message": (
                        "scripts/hbtrack_lint/__init__.py não contém aviso LEGACY/legado/deprecated. "
                        "Marcar explicitamente para documentar o status de legado."
                    ),
                    "severity": "error",
                })
        except Exception:
            pass

    # 3. Caminhos críticos não devem importar hbtrack_lint
    for crit_path in critical_files:
        if not crit_path.exists():
            continue
        try:
            text = crit_path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        if re.search(r"(?:import|from)\s+hbtrack_lint", text):
            violations.append({
                "blocking_code": BLOCKED_LEGACY_IN_CRITICAL_PATH,
                "artifact": str(crit_path.relative_to(root)),
                "message": (
                    f"Caminho crítico '{crit_path.name}' importa 'hbtrack_lint' (legado). "
                    "Remover ou isolar import para impedir reintrodução no fluxo ativo."
                ),
                "severity": "error",
            })

    if violations:
        return _pg(
            gate_id,
            "FAIL",
            True,
            BLOCKED_LEGACY_IN_CRITICAL_PATH,
            f"{len(violations)} artefato(s) legado(s) sem isolamento adequado.",
            [],
            checked,
            [],
            violations,
            _ms(t0),
        )

    return _pg(
        gate_id,
        "PASS",
        True,
        None,
        "Isolamento de legado OK: artefatos marcados e fora do caminho crítico.",
        [],
        checked,
        [],
        [],
        _ms(t0),
    )


def _g16_readiness_summary(gates: list[dict]) -> dict:
    t0 = time.monotonic()
    gate_id = "READINESS_SUMMARY_GATE"
    blocking_fails = [g for g in gates if g.get("blocking") and g.get("status") == "FAIL"]
    non_blocking_fails = [g for g in gates if not g.get("blocking") and g.get("status") == "FAIL"]
    degraded = [g for g in gates if g.get("status") == "DEGRADED"]
    passes = [g for g in gates if g.get("status") == "PASS"]
    skips = [g for g in gates if g.get("status") == "SKIP_NOT_APPLICABLE"]
    if blocking_fails:
        summary = f"Pipeline FAIL: {len(blocking_fails)} gate(s) bloqueante(s) falharam."
        status = "FAIL"
    elif degraded:
        summary = f"Pipeline DEGRADED: {len(degraded)} gate(s) locais operaram em fallback explícito."
        status = "DEGRADED"
    elif non_blocking_fails:
        summary = f"Pipeline PASS com avisos: {len(non_blocking_fails)} gate(s) não-bloqueante(s) falharam."
        status = "PASS"
    else:
        summary = f"Pipeline PASS: {len(passes)} PASS, {len(skips)} SKIP."
        status = "PASS"
    return _pg(gate_id, status, False, None, summary, [], [], [], [], _ms(t0))


def _module_real_path_count(root: pathlib.Path, module: str) -> int:
    path_file = root / "contracts" / "openapi" / "paths" / f"{module}.yaml"
    if not path_file.exists():
        return 0
    try:
        obj = _load_yaml(path_file)
    except Exception:
        return 0
    if not isinstance(obj, dict):
        return 0
    return len([k for k in obj.keys() if isinstance(k, str) and k.startswith("/")])


def _module_schema_count(root: pathlib.Path, module: str) -> int:
    schema_dir = root / "contracts" / "schemas" / module
    if not schema_dir.exists():
        return 0
    return len(list(schema_dir.glob("*.schema.json")))


def _module_asyncapi_artifact_count(root: pathlib.Path, module: str) -> int:
    asyncapi_root = root / "contracts" / "asyncapi"
    if not asyncapi_root.exists():
        return 0
    singular = module
    if module.endswith("ies"):
        singular = module[:-3] + "y"
    elif module.endswith("es"):
        singular = module[:-2]
    elif module.endswith("s"):
        singular = module[:-1]

    def _matches(path: pathlib.Path) -> bool:
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            return False
        header = "\n".join(text.splitlines()[:8])
        comment_match = re.search(r"^#\s*Module:\s*([a-z0-9_]+)\s*$", header, re.MULTILINE)
        if comment_match and comment_match.group(1) == module:
            return True
        normalized_stem = path.stem.replace("-", "_")
        return normalized_stem.startswith(f"{module}_") or normalized_stem.startswith(f"{singular}_")

    count = 0
    for rel in ("channels", "messages"):
        base = asyncapi_root / rel
        if not base.exists():
            continue
        count += len([p for p in base.rglob("*.yaml") if _matches(p)])
    return count


def _module_workflow_count(root: pathlib.Path, module: str) -> int:
    workflow_dir = root / "contracts" / "workflows" / module
    if not workflow_dir.exists():
        return 0
    return len(list(workflow_dir.rglob("*.arazzo.yaml")))


def _module_has_pre_contract_evidence(root: pathlib.Path, module: str) -> bool:
    log_dir = root / "_reports" / "agent_execution"
    if not log_dir.exists():
        return False
    for path in sorted(log_dir.glob("*.json")):
        data, errs = _load_agent_execution_log(path, root)
        if errs or not data:
            continue
        if data.get("module") == module:
            return True
    return False


def _module_has_decision_ir(root: pathlib.Path, module: str) -> bool:
    ir_path = _canonical_decision_ir_path(root, module)
    if not ir_path.exists():
        return False
    try:
        data = _load_structured_doc(ir_path)
    except Exception:
        return False
    if not isinstance(data, dict):
        return False
    if data.get("module") == module:
        return True
    decisions = data.get("decisions")
    return isinstance(decisions, list) and len(decisions) > 0


def _module_minimum_docs_present(root: pathlib.Path, module: str) -> bool:
    module_dir = root / "docs" / "hbtrack" / "modulos" / module
    up = module.upper()
    required = [
        module_dir / "README.md",
        module_dir / f"MODULE_SCOPE_{up}.md",
        module_dir / f"DOMAIN_RULES_{up}.md",
        module_dir / f"INVARIANTS_{up}.md",
        module_dir / f"TEST_MATRIX_{up}.md",
    ]
    return all(p.exists() for p in required)


def _surface_status_for_module(
    root: pathlib.Path,
    module: str,
    surface: str,
    *,
    root_ref_count: int,
    path_count: int,
    schema_count: int,
    workflow_count: int,
    asyncapi_count: int,
    decision_ir_gate_status: str | None,
) -> str:
    if surface == "module_docs_minimum":
        return "ready" if _module_surface_present(root, module, surface) else "missing"
    if surface == "openapi_sync":
        path_file = root / "contracts" / "openapi" / "paths" / f"{module}.yaml"
        if not path_file.exists():
            return "missing"
        if path_count == 0:
            return "scaffold_only"
        if root_ref_count != path_count:
            return "drift"
        return "ready"
    if surface == "json_schema":
        return "ready" if _module_surface_present(root, module, surface) else "missing"
    if surface == "test_matrix":
        return "ready" if _module_surface_present(root, module, surface) else "missing"
    if surface == "state_model":
        return "ready" if _module_surface_present(root, module, surface) else "missing"
    if surface == "permissions":
        return "ready" if _module_surface_present(root, module, surface) else "missing"
    if surface == "errors":
        return "ready" if _module_surface_present(root, module, surface) else "missing"
    if surface == "sport_science":
        return "ready" if _module_surface_present(root, module, surface) else "missing"
    if surface == "ui_contract":
        return "ready" if _module_surface_present(root, module, surface) else "missing"
    if surface == "asyncapi":
        return "ready" if _module_surface_present(root, module, surface) else "missing"
    if surface == "arazzo":
        return "ready" if _module_surface_present(root, module, surface) else "missing"
    if surface == "decision_ir":
        if not _module_surface_present(root, module, surface):
            return "missing"
        return "ready" if decision_ir_gate_status == "PASS" else "drift"
    return "unknown"


def _write_module_readiness_scorecard(
    root: pathlib.Path,
    gates: list[dict],
    *,
    generated_at_utc: str,
    overall_status: str,
) -> None:
    evidence_dir = root / "_reports" / "evidence"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    registry_entries, _ = _load_module_registry_entries(root)
    modules = registry_entries or {}
    root_refs, _, _ = _openapi_root_module_refs(root)
    gate_status = {g.get("gate_id"): g.get("status") for g in gates}

    payload_modules: list[dict] = []
    markdown_lines = [
        "# MODULE READINESS SCORECARD",
        "",
        f"- Generated at: `{generated_at_utc}`",
        f"- Pipeline status: `{overall_status}`",
        "",
        "| Module | Registry | Owner | Ready % | OpenAPI | Schemas | Missing / Drift |",
        "|---|---|---|---:|---:|---:|---|",
    ]

    for module, entry in modules.items():
        expected_surfaces = list(entry.get("expected_surfaces") or [])
        root_ref_count = len(root_refs.get(module) or set())
        path_count = _module_real_path_count(root, module)
        schema_count = _module_schema_count(root, module)
        asyncapi_count = _module_asyncapi_artifact_count(root, module)
        workflow_count = _module_workflow_count(root, module)
        decision_ir_gate_status = gate_status.get("DECISION_IR_CONFORMANCE_GATE")
        surface_status = {
            surface: _surface_status_for_module(
                root,
                module,
                surface,
                root_ref_count=root_ref_count,
                path_count=path_count,
                schema_count=schema_count,
                workflow_count=workflow_count,
                asyncapi_count=asyncapi_count,
                decision_ir_gate_status=decision_ir_gate_status,
            )
            for surface in expected_surfaces
        }
        ready_surfaces = [s for s, status in surface_status.items() if status == "ready"]
        missing_surfaces = [s for s, status in surface_status.items() if status != "ready"]
        readiness_pct = int(round((len(ready_surfaces) / len(expected_surfaces)) * 100)) if expected_surfaces else 100

        module_payload = {
            "module": module,
            "owner": entry.get("owner"),
            "registry_status": entry.get("status"),
            "expected_surfaces": expected_surfaces,
            "readiness_pct": readiness_pct,
            "surface_status": surface_status,
            "evidence": {
                "minimum_docs_present": _module_minimum_docs_present(root, module),
                "openapi_root_ref_count": root_ref_count,
                "openapi_real_path_count": path_count,
                "schema_file_count": schema_count,
                "asyncapi_artifact_count": asyncapi_count,
                "workflow_count": workflow_count,
                "pre_contract_evidence": _module_has_pre_contract_evidence(root, module),
                "decision_ir_gate_status": decision_ir_gate_status,
            },
        }
        payload_modules.append(module_payload)

        missing_label = ", ".join(missing_surfaces[:4])
        if len(missing_surfaces) > 4:
            missing_label += f" +{len(missing_surfaces) - 4}"
        markdown_lines.append(
            f"| `{module}` | `{entry.get('status')}` | `{entry.get('owner')}` | {readiness_pct} | {root_ref_count}/{path_count} | {schema_count} | {missing_label or '—'} |"
        )

    payload = {
        "artifact_id": "HBTRACK_MODULE_READINESS_SCORECARD",
        "generated_at_utc": generated_at_utc,
        "overall_status": overall_status,
        "source_report": "_reports/contract_gates/latest.json",
        "modules": payload_modules,
    }
    (evidence_dir / "module_readiness_scorecard.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (evidence_dir / "module_readiness_scorecard.md").write_text(
        "\n".join(markdown_lines) + "\n",
        encoding="utf-8",
    )


def _gen_readiness_dashboard(
    root: pathlib.Path,
    gates: list[dict],
    overall: str,
    health: int,
    run_id: str,
    ts: str,
    output_path: pathlib.Path,
) -> None:
    try:
        import yaml as _yaml
        registry_path = root / "docs" / "_canon" / "MODULE_REGISTRY.yaml"
        modules = {}
        if registry_path.exists():
            modules = (_yaml.safe_load(registry_path.read_text(encoding="utf-8")) or {}).get("modules", {})
    except Exception:
        modules = {}
    lines = [
        "# Dashboard de Readiness - HB Track",
        f"> Gerado em {ts} | run_id: `{run_id}` | health: **{health}/100** | overall: **{overall}**",
        "",
        "## Modulos",
        "",
        "| Modulo | Status | Superficies |",
        "|---|---|---|",
    ]
    for name, data in (modules or {}).items():
        if not isinstance(data, dict):
            continue
        status = data.get("status", "?")
        surfaces = ", ".join(data.get("expected_surfaces") or data.get("surfaces") or [])
        lines.append(f"| {name} | `{status}` | {surfaces} |")
    lines += ["", "## Gates", "", "| Gate | Status | Blocking |", "|---|---|---|"]
    for gate in gates:
        gate_id = gate.get("gate_id", "?")
        status = gate.get("status", "?")
        blocking = "sim" if gate.get("blocking") else "nao"
        lines.append(f"| {gate_id} | {status} | {blocking} |")
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _persist_pipeline_artifacts(
    *,
    root: pathlib.Path,
    report_path: pathlib.Path,
    report: dict,
    gates: list[dict],
    overall: str,
    exit_code: int,
    ts: str,
    run_dir: pathlib.Path,
    run_id: str,
) -> None:
    import shutil as _shutil
    _shutil.copy2(report_path, run_dir / "contract_gates.json")
    scorecard = root / "_reports" / "evidence" / "module_readiness_scorecard.json"
    if scorecard.exists():
        _shutil.copy2(scorecard, run_dir / "module_readiness_scorecard.json")

    total = len(gates)
    passed = len([gate for gate in gates if gate.get("status") in ("PASS", "SKIP_NOT_APPLICABLE")])
    health = round((passed / total) * 100) if total > 0 else 0
    health_data = {
        "run_id": run_id,
        "timestamp_utc": ts,
        "health_score": health,
        "gates_total": total,
        "gates_passed": passed,
        "gates_failed": len([gate for gate in gates if gate.get("status") == "FAIL"]),
        "blocking_fails": len([gate for gate in gates if gate.get("blocking") and gate.get("status") == "FAIL"]),
        "overall_status": overall,
        "exit_code": exit_code,
    }
    (run_dir / "health.json").write_text(
        json.dumps(health_data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (root / "_reports" / "pipeline_health.json").write_text(
        json.dumps(health_data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    history_path = root / "_reports" / "pipeline_history.jsonl"
    history_entry = {
        "run_id": run_id,
        "timestamp_utc": ts,
        "overall_status": overall,
        "exit_code": exit_code,
        "health_score": health,
        "git_commit": report.get("environment", {}).get("git_commit"),
    }
    with open(history_path, "a", encoding="utf-8") as history_file:
        history_file.write(json.dumps(history_entry, ensure_ascii=False) + "\n")
    try:
        _gen_readiness_dashboard(
            root,
            gates,
            overall,
            health,
            run_id,
            ts,
            root / "_reports" / "READINESS_DASHBOARD.md",
        )
    except Exception:
        pass


# ── Orchestrator + main ───────────────────────────────────────────────────────

def _load_gates_metadata(root: pathlib.Path) -> dict[str, dict[str, Any]]:
    """
    Load GATES_REGISTRY.yaml and build dict: gate_id → gate metadata.
    
    Returns: {gate_id: {blocking, severity, order, ...}, ...}
    Raises: Exception if registry invalid or missing.
    """
    registry_path = root / "docs" / "_canon" / "gates" / "GATES_REGISTRY.yaml"
    if not registry_path.exists():
        raise FileNotFoundError(f"GATES_REGISTRY.yaml not found at {registry_path}")
    
    with open(registry_path, "r", encoding="utf-8") as f:
        registry_data = yaml.safe_load(f)
    
    if not registry_data or "gates" not in registry_data:
        raise ValueError(f"GATES_REGISTRY.yaml missing 'gates' key")
    
    gates_metadata = {}
    for gate in registry_data["gates"]:
        gate_id = gate.get("gate_id")
        if not gate_id:
            raise ValueError("Gate in GATES_REGISTRY.yaml missing gate_id")
        gates_metadata[gate_id] = gate
    
    return gates_metadata


def run_pipeline(
    profile: str = "ci",
    stage: "str | None" = None,
    artifact: "str | None" = None,
    module: "str | None" = None,
) -> tuple[dict, int]:
    root = _repo_root()
    axioms_path = root / ".contract_driven" / "DOMAIN_AXIOMS.json"
    axioms_schema_path = root / "contracts" / "schemas" / "shared" / "domain_axioms.schema.json"
    report_path = root / "_reports" / "contract_gates" / "latest.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    canonical_full_run = stage is None and profile == "ci"
    scoped_report_path = report_path
    if not canonical_full_run:
        scope_bits: list[str] = []
        if stage:
            scope_bits.append(f"stage-{stage}")
        if profile:
            scope_bits.append(profile)
        if not scope_bits:
            scope_bits.append("partial")
        scoped_report_path = report_path.parent / f"{'.'.join(scope_bits)}.latest.json"
    _required_tools = ["python3"]
    _optional_tools = ["redocly", "spectral", "oasdiff", "schemathesis", "asyncapi"]
    missing_required = [tool for tool in _required_tools if not shutil.which(tool)]
    missing_optional = [tool for tool in _optional_tools if not shutil.which(tool)]
    if missing_required:
        print(f"[BOOTSTRAP] ERRO: ferramentas obrigatórias ausentes: {missing_required}", file=sys.stderr)
    if missing_optional:
        print(f"[BOOTSTRAP] INFO: tools opcionais ausentes (gates entrarão em SKIP): {missing_optional}")
    openapi_root = root / "contracts" / "openapi" / "openapi.yaml"
    asyncapi_root_p = root / "contracts" / "asyncapi" / "asyncapi.yaml"
    ts = datetime.datetime.now(datetime.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    import uuid as _uuid
    run_id = datetime.datetime.now(datetime.UTC).strftime("%Y%m%dT%H%M%S") + "_" + _uuid.uuid4().hex[:6]
    run_dir = root / "_reports" / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    # PR3: Load GATES_REGISTRY.yaml as SSOT for gate metadata
    try:
        gates_metadata = _load_gates_metadata(root)
    except Exception as e:
        print(f"[BOOTSTRAP] ERRO: Não foi possível carregar GATES_REGISTRY.yaml: {e}", file=sys.stderr)
        gates_metadata = {}  # Fallback (will use defaults)

    def _build_report(all_gates: list[dict], overall: str, exit_code: int) -> dict:
        # R-006: status_detail composto — expõe realidade sem depender de SKIP na matemática
        _active = [g for g in all_gates if g.get("status") not in ("SKIP_NOT_APPLICABLE", "SKIP")]
        _active_pass = [g for g in _active if g.get("status") == "PASS"]
        _skip = [g for g in all_gates if g.get("status") in ("SKIP_NOT_APPLICABLE", "SKIP")]
        _critical = [
            {"gate_id": g["gate_id"], "status": g["status"]}
            for g in all_gates
            if g.get("blocking") is True
        ]
        status_detail = {
            "active_gates_passed": len(_active_pass),
            "skip_count": len(_skip),
            "critical_gates": _critical,
        }
        return {
            "pipeline_id": "HB_TRACK_CONTRACT_GATES",
            "timestamp_utc": ts,
            "target": {
                "scope": "system",
                "module": None,
                "openapi_root": str(openapi_root),
                "asyncapi_root": str(asyncapi_root_p) if asyncapi_root_p.exists() else None,
                "workflow_scope": str(root / "contracts" / "workflows"),
            },
            "environment": {
                "git_commit": _git_commit(root),
                "python_version": platform.python_version(),
                "tool_versions": {
                    "redocly": _tool_ver("redocly", "--version"),
                    "spectral": _tool_ver("spectral", "--version"),
                    "oasdiff": _tool_ver("oasdiff", "version"),
                    "schemathesis": _tool_ver("schemathesis", "--version"),
                    "json_schema_validator": None,
                    "asyncapi_validator": _tool_ver("asyncapi", "--version"),
                    "arazzo_validator": None,
                    "storybook": None,
                },
            },
            "overall_status": overall,
            "execution_context": {
                "profile": profile,
                "stage": stage,
                "canonical_scope": "full_pipeline" if canonical_full_run else "partial_validation",
            },
            "report_artifacts": {
                "scoped_report_path": str(scoped_report_path),
                "canonical_report_path": str(report_path),
                "run_dir": str(run_dir),
            },
            "status_detail": status_detail,
            "exit_code": exit_code,
            "gates": all_gates,
        }

    def _write_report_artifacts(report: dict, overall: str, exit_code: int, gates_out: list[dict]) -> None:
        scoped_report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        (run_dir / "contract_gates.json").write_text(
            json.dumps(report, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        if canonical_full_run:
            _write_module_readiness_scorecard(root, gates_out, generated_at_utc=ts, overall_status=overall)
            _persist_pipeline_artifacts(
                root=root,
                report_path=scoped_report_path,
                report=report,
                gates=gates_out,
                overall=overall,
                exit_code=exit_code,
                ts=ts,
                run_dir=run_dir,
                run_id=run_id,
            )

    # G0: AXIOM_INTEGRITY_GATE (blocking — prerequisite for all others)
    axiom_gate = validate_axiom_integrity(str(axioms_path), str(axioms_schema_path))
    axiom_result: dict = {
        "gate_id": "AXIOM_INTEGRITY_GATE",
        "status": axiom_gate["status"],
        "blocking": True,
        "exit_code": 0 if axiom_gate["status"] == "PASS" else 4,
        "blocking_code": axiom_gate.get("blocking_code"),
        "summary": (
            "Axiomas globais válidos."
            if axiom_gate["status"] == "PASS"
            else "Axiomas globais inválidos."
        ),
        "inputs": [str(axioms_path), str(axioms_schema_path)],
        "artifacts_checked": [str(axioms_path)],
        "evidence_files": [],
        "violations": axiom_gate.get("violations") or [],
        "metrics": {
            "errors": len(axiom_gate.get("violations") or []),
            "warnings": 0,
            "violations": len(axiom_gate.get("violations") or []),
            "duration_ms": int((axiom_gate.get("metrics") or {}).get("duration_ms") or 0),
        },
    }
    gates: list[dict] = [axiom_result]

    if axiom_gate["status"] != "PASS":
        g16 = _g16_readiness_summary(gates)
        gates.append(g16)
        report = _build_report(gates, "FAIL", 4)
        _write_report_artifacts(report, "FAIL", 4, gates)
        return report, 4

    try:
        axioms = load_domain_axioms(str(axioms_path))
    except Exception as e:
        gates.append(
            _pg("AXIOM_INTEGRITY_GATE", "FAIL", True, "BLOCKED_AXIOM_FILE_NOT_FOUND",
                f"Não foi possível carregar axiomas: {e}", [], [], [], [], 0)
        )
        g16 = _g16_readiness_summary(gates)
        gates.append(g16)
        report = _build_report(gates, "FAIL", 4)
        _write_report_artifacts(report, "FAIL", 4, gates)
        return report, 4

    _precommit_ids = {
        "PATH_CANONICALITY_GATE",
        "MODULE_REGISTRY_GATE",
        "PLACEHOLDER_RESIDUE_GATE",
        "UI_DOC_VALIDATION_GATE",
        "HANDOFF_COHERENCE_GATE",
        "MODULE_STATUS_COHERENCE_GATE",
        "SURFACE_PROMOTION_COHERENCE_GATE",
        "AXIOM_INTEGRITY_GATE",
        "CANON_ALLOWLIST_GATE",
        "READINESS_GENERATION_COMPATIBILITY_GATE",  # FIX Ordem 3: agora no padrão
        "WAIVER_VALIDITY_GATE",  # FIX Ordem 5: agora no padrão
        "READINESS_HUMAN_CONFIRMATION_GATE",  # FIX Ordem 6: agora no padrão
        "CROSS_SPEC_ALIGNMENT_GATE",  # FIX BACKLOG_ITEM_2 (2A): no padrão para validação de links
        # GAP-02: Gates de tooling adicionados ao perfil precommit (ferramentas instaladas no CI via npm ci)
        "REF_HERMETICITY_GATE",                # sem tool externo — puro Python
        "OPENAPI_ROOT_STRUCTURE_GATE",         # redocly lint
        "OPENAPI_ROOT_MODULE_SYNC_GATE",       # redocly / estrutura root
        "JSON_SCHEMA_VALIDATION_GATE",         # JSON Schema validation
        "OPENAPI_POLICY_RULESET_GATE",         # spectral lint (com .spectral.yaml)
        "SPECTRAL_LINTING_GATE",               # spectral lint (sem ruleset)
        "ASYNCAPI_VALIDATION_GATE",            # asyncapi validate
        "ARAZZO_VALIDATION_GATE",              # Arazzo YAML parsing
        "ARAZZO_COMPLETENESS_GATE",            # Arazzo completeness
        "TOOLING_CONFIG_GATE",                 # redocly.yaml / .spectral.yaml presentes
    }
    _local_ids = _precommit_ids | {
        "DECISION_IR_CONFORMANCE_GATE",
        "DERIVED_DRIFT_GATE",
        "ADVERSARIAL_ANALYSIS_GATE",
        "FEATURE_READINESS_GATE",
        # FIX BACKLOG_ITEM_1 (Passos E-F): Adicionar validadores externos ao default local profile
        "OPENAPI_ROOT_STRUCTURE_GATE",         # Redocly lint (validação OpenAPI)
        "ASYNCAPI_VALIDATION_GATE",            # AsyncAPI validate (validação AsyncAPI)
        "ARAZZO_VALIDATION_GATE",              # Arazzo YAML parsing (validação workflows)
        "JSON_SCHEMA_VALIDATION_GATE",         # JSON Schema validation
        "OPENAPI_ROOT_MODULE_SYNC_GATE",       # Sincronização root OpenAPI com paths de módulos
        "SPECTRAL_LINTING_GATE",               # FIX BACKLOG_ITEM_1 (Passo D): Spectral linting (estilos OpenAPI)
        # FIX BACKLOG_ITEM_2 (2A): CROSS_SPEC_ALIGNMENT_GATE para validação de links Arazzo
        "CROSS_SPEC_ALIGNMENT_GATE",           # Validação de operationIds em Arazzo vs OpenAPI
    }

    # Stage-specific gate sets (Fase 0 / 1 / 2)
    _session_start_ids = {
        "AXIOM_INTEGRITY_GATE",
        "HANDOFF_COHERENCE_GATE",
        "MODULE_STATUS_COHERENCE_GATE",
    }
    _pre_authoring_ids = {
        "AXIOM_INTEGRITY_GATE",
        "MODULE_REGISTRY_GATE",
        "REQUIRED_ARTIFACT_PRESENCE_GATE",
        "ADVERSARIAL_ANALYSIS_GATE",
        "CROSS_MODULE_BOUNDARY_GATE",
    }
    _artifact_ids = {
        "AXIOM_INTEGRITY_GATE",
        "PATH_CANONICALITY_GATE",
        "PLACEHOLDER_RESIDUE_GATE",
        "JSON_SCHEMA_VALIDATION_GATE",
        "UI_DOC_VALIDATION_GATE",
        "CROSS_MODULE_BOUNDARY_GATE",
        "OPENAPI_ROOT_STRUCTURE_GATE",
    }
    _stage_map: "dict[str, set[str]] | None" = (
        {"session-start": _session_start_ids, "pre-authoring": _pre_authoring_ids, "artifact": _artifact_ids}
        if stage else None
    )

    def _maybe(gate_fn, gate_id_hint: str) -> dict:
        if _stage_map is not None:
            allowed_for_stage = _stage_map.get(stage, set())  # type: ignore[arg-type]
            if gate_id_hint not in allowed_for_stage:
                return _skip(gate_id_hint, f"Pulado no estágio '{stage}'.", 0)
            return gate_fn()
        if profile == "ci":
            return gate_fn()
        allowed = _local_ids if profile == "local" else _precommit_ids
        if gate_id_hint in allowed:
            return gate_fn()
        return _skip(gate_id_hint, f"Pulado no perfil '{profile}'.", 0)

    gate_plan = [
        ("PATH_CANONICALITY_GATE", lambda: _g1_path_canonicality(root)),
        ("REQUIRED_ARTIFACT_PRESENCE_GATE", lambda: _g2_required_artifact_presence(root)),
        ("MODULE_DOC_CROSSREF_GATE", lambda: _g2a_module_doc_crossrefs(root)),
        ("API_NORMATIVE_DUPLICATION_GATE", lambda: _g2b_api_normative_duplication(root)),
        ("OWASP_API_CONTROL_MATRIX_GATE", lambda: _g2c_owasp_api_control_matrix(root)),
        ("MODULE_SOURCE_AUTHORITY_MATRIX_GATE", lambda: _g2d_module_source_authority_matrix(root)),
        ("MODULE_REGISTRY_GATE", lambda: _g2d1_module_registry(root)),
        ("BOUNDARY_USERS_IDENTITY_ACCESS_GATE", lambda: _g2e_boundary_users_identity_access(root)),
        ("WELLNESS_MEDICAL_BOUNDARY_GATE", lambda: _g2f_wellness_medical_boundary(root)),
        ("SCOUT_TAXONOMY_GATE", lambda: _g2g_scout_taxonomy(root)),
        ("ASYNC_REQUIRED_MODULE_GATE", lambda: _g2h_async_required_module(root)),
        ("EXTERNAL_SOURCE_AUTHORITY_GATE", lambda: _g2i_external_source_authority(root)),
        ("PRE_CONTRACT_EVIDENCE_GATE", lambda: _g2j_pre_contract_evidence(root)),
        ("SHADOW_AUTHORITY_GATE", lambda: _g2k_shadow_authority(root)),
        ("DECISION_IR_CONFORMANCE_GATE", lambda: _g2l_decision_ir_conformance(root)),
        ("CANON_ALLOWLIST_GATE", lambda: _g2n_canon_allowlist(root)),
        ("PLACEHOLDER_RESIDUE_GATE", lambda: _g3_placeholder_residue(root)),
        ("REF_HERMETICITY_GATE", lambda: _g4_ref_hermeticity(root)),
        ("TOOLING_CONFIG_GATE", lambda: _g4a_tooling_config(root)),
        ("OPENAPI_ROOT_STRUCTURE_GATE", lambda: _g5_openapi_root_structure(root)),
        ("OPENAPI_ROOT_MODULE_SYNC_GATE", lambda: _g5a_openapi_root_module_sync(root)),
        ("OPENAPI_POLICY_RULESET_GATE", lambda: _g6_openapi_policy_ruleset(root)),
        ("JSON_SCHEMA_VALIDATION_GATE", lambda: _g7_json_schema_validation(root)),
        ("CROSS_SPEC_ALIGNMENT_GATE", lambda: _g8_cross_spec_alignment(root, axioms)),
        ("CONTRACT_BREAKING_CHANGE_GATE", lambda: _g9_contract_breaking_change(root)),
        ("TRANSFORMATION_FEASIBILITY_GATE", lambda: _g10_transformation_feasibility(root)),
        ("HTTP_RUNTIME_CONTRACT_GATE", lambda: _g11_http_runtime_contract(root)),
        ("ASYNCAPI_VALIDATION_GATE", lambda: _g12_asyncapi_validation(root)),
        ("ARAZZO_VALIDATION_GATE", lambda: _g13_arazzo_validation(root)),
        ("SPECTRAL_LINTING_GATE", lambda: _g13a_spectral_linting(root)),  # FIX BACKLOG_ITEM_1 (Passo D): novo gate de Spectral
        ("ARAZZO_COMPLETENESS_GATE", lambda: _g_arazzo_completeness(root)),
        ("UI_DOC_VALIDATION_GATE", lambda: _g14_ui_doc_validation(root)),
        ("DERIVED_DRIFT_GATE", lambda: _g15_derived_drift(root)),
        ("ADVERSARIAL_ANALYSIS_GATE", lambda: _g_adversarial_analysis(root)),
        ("FEATURE_READINESS_GATE", lambda: _g_feature_readiness(root)),
        ("VERSIONING_POLICY_GATE", lambda: _g_versioning_policy(root)),
        ("PACT_PROVIDER_GATE", lambda: _g_pact_provider(root)),
        ("CODE_ARCHITECTURE_GATE", lambda: _g_code_architecture(root)),
        ("DEPLOY_READINESS_GATE", lambda: _g_deploy_readiness(root)),
        ("DATA_MIGRATION_GATE", lambda: _g_data_migration(root)),
        ("MONITORING_POLICY_GATE", lambda: _g_monitoring_policy(root)),
        ("HANDOFF_COHERENCE_GATE", lambda: _g_handoff_coherence(root)),
        ("MODULE_STATUS_COHERENCE_GATE", lambda: _g_module_status_coherence(root)),
        ("SURFACE_PROMOTION_COHERENCE_GATE", lambda: _g_surface_promotion_coherence(root)),
        ("CROSS_MODULE_BOUNDARY_GATE", lambda: _g_cross_module_boundary(root)),
        ("MODULE_DEPENDENCY_RESOLUTION_GATE", lambda: _g_module_dependency_resolution(root)),
        ("WAIVER_VALIDITY_GATE", lambda: _g_waiver_validity(root)),  # FIX Ordem 5: implementado
        ("READINESS_GENERATION_COMPATIBILITY_GATE", lambda: _g_readiness_generation_compatibility(root)),
        ("READINESS_HUMAN_CONFIRMATION_GATE", lambda: _g_readiness_human_confirmation(root)),  # FIX Ordem 6: implementado
        ("FEATURE_COVERAGE_GATE", lambda: _g_feature_coverage(root)),
        ("LEGACY_CRITICAL_PATH_GATE", lambda: _g_legacy_isolation(root)),  # FASE 7
    ]
    for gate_id_hint, gate_fn in gate_plan:
        gate_result = _maybe(gate_fn, gate_id_hint)
        
        # PR3: Consult GATES_REGISTRY for blocking status (only for non-SKIP gates)
        if gate_id_hint in gates_metadata and gate_result.get("status") not in ("SKIP", "DEGRADED"):
            metadata = gates_metadata[gate_id_hint]
            gate_result["blocking"] = metadata.get("blocking", gate_result.get("blocking", False))
        
        gates.append(gate_result)

    # G16: readiness summary
    g16 = _g16_readiness_summary(gates)
    gates.append(g16)

    blocking_fails = [g for g in gates if g.get("blocking") and g.get("status") == "FAIL"]
    error_infra = any(
        v.get("blocking_code") == "ERROR_INFRA"
        for g in gates
        for v in (g.get("violations") or [])
    )
    degraded = any(g.get("status") == "DEGRADED" for g in gates)
    
    # PR3: Phase-specific semantics — phase 0/1/2 must ALWAYS exit != 0 if blocking fail
    is_phase = stage in ("session-start", "pre-authoring", "artifact")
    
    if blocking_fails:
        overall = "FAIL"
        if is_phase:
            exit_code = 2  # Fase 0/1/2 — strict: ANY blocking fail = exit 2
        else:
            exit_code = 3 if error_infra else 2  # Full CI — infrastructure errors = 3
    elif degraded:
        overall = "DEGRADED"
        exit_code = 0
    elif any(g.get("status") == "FAIL" for g in gates):
        overall = "PASS_WITH_WARNINGS"
        exit_code = 0
    else:
        overall = "PASS"
        exit_code = 0

    report = _build_report(gates, overall, exit_code)
    _write_report_artifacts(report, overall, exit_code, gates)
    return report, exit_code


def main() -> int:
    import argparse as _argparse

    parser = _argparse.ArgumentParser(description="HB Track Contract Gates")
    parser.add_argument("--profile", choices=["local", "precommit", "ci"], default=None)
    parser.add_argument(
        "--stage",
        choices=["session-start", "pre-authoring", "artifact"],
        default=None,
        help="Executar apenas os gates da fase indicada (Fase 0/1/2).",
    )
    parser.add_argument("--artifact", default=None, help="Path do artefato (para --stage artifact).")
    parser.add_argument("--module", default=None, help="Módulo alvo (para --stage pre-authoring).")
    args, _ = parser.parse_known_args()
    profile = args.profile or ("ci" if os.environ.get("CI") else "local")
    stage = args.stage
    artifact = args.artifact
    module = args.module

    _stage_labels = {
        "session-start": "FASE 0: SESSION_BOOT",
        "pre-authoring": "FASE 1: PRE_AUTHORING",
        "artifact": "FASE 2: PER_ARTIFACT",
    }
    phase_label = _stage_labels.get(stage, "PIPELINE COMPLETO") if stage else "PIPELINE COMPLETO"
    artifact_label = f"  |  {artifact}" if artifact else (f"  |  módulo={module}" if module else "")

    sep = "═" * 62
    print(f"\n{sep}")
    print(f"  {phase_label}{artifact_label}")
    print(sep)

    report, exit_code = run_pipeline(profile=profile, stage=stage, artifact=artifact, module=module)
    gates = report.get("gates", [])
    overall = report.get("overall_status", "?")

    sep2 = "-" * 62
    print(f"\n{sep2}")
    print(f"  HB TRACK CONTRACT GATES  --  {overall}")
    print(sep2)
    for g in gates:
        status = g.get("status", "?")
        gid = g.get("gate_id", "?")
        summary = g.get("summary", "")
        if status == "PASS":
            icon = "+"
        elif status in ("SKIP_NOT_APPLICABLE", "SKIP"):
            icon = "~"
        else:
            icon = "!"
        print(f"  {icon} [{status:<24}] {gid}")
        if status == "FAIL":
            print(f"       {summary}")
            for v in (g.get("violations") or [])[:3]:
                msg = str(v.get("message", ""))[:100]
                action = v.get("action", "")
                print(f"       - {msg}")
                if action:
                    print(f"         Ação: {action}")
    print(sep2)
    print(f"  STATUS   : {overall}")
    report_path = report.get("report_artifacts", {}).get("scoped_report_path")
    if not report_path:
        root = _repo_root()
        report_path = str(root / "_reports" / "contract_gates" / "latest.json")
    print(f"  Report   : {report_path}")
    print(sep2)
    print(f"\nDONE = exitcode 0  |  atual exitcode = {exit_code}")
    if exit_code != 0 and stage:
        cmds = {
            "session-start": "hb verify",
            "pre-authoring": f"hb check --module {module or '<mod>'}",
            "artifact": f"hb artifact {artifact or '<path>'}",
        }
        print(f"Corrigir e re-executar: {cmds.get(stage, 'hb verify')}")
    print()
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
