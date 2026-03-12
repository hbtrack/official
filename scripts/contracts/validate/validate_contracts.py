"""
HB Track -- validate_contracts.py

Contrato mínimo (sem interpretação livre):
- Este script consome `.contract_driven/DOMAIN_AXIOMS.json` e aplica validações determinísticas.
- As funções públicas abaixo DEVEM existir com as assinaturas exatas (pipeline contract).
- O script gera evidência machine-readable em `_reports/contract_gates/latest.json`.

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
import json
import pathlib
import platform
import re
import subprocess
import sys
import time
from typing import Any


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


def _layout_path(root: pathlib.Path) -> pathlib.Path:
    return root / ".contract_driven" / "CONTRACT_SYSTEM_LAYOUT.md"


def _load_canonical_modules_from_layout(root: pathlib.Path) -> list[str]:
    """
    SSOT de módulos: `.contract_driven/CONTRACT_SYSTEM_LAYOUT.md` seção 2.
    Extrai os módulos listados em 2.1 e 2.2 (bullets `- <module>`).
    """
    lp = _layout_path(root)
    if not lp.exists():
        return []
    text = _read_text(lp)
    modules: list[str] = []
    in_taxonomy = False
    for line in text.splitlines():
        if line.startswith("### 2.1 "):
            in_taxonomy = True
            continue
        if line.startswith("### 2.2 "):
            in_taxonomy = True
            continue
        if line.startswith("### 2.3 "):
            break
        if not in_taxonomy:
            continue
        m = re.match(r"^\s*-\s*`?([a-z0-9]+(?:_[a-z0-9]+)*)`?\s*$", line)
        if m:
            modules.append(m.group(1))
    # unique, stable order
    seen: set[str] = set()
    out: list[str] = []
    for mod in modules:
        if mod in seen:
            continue
        seen.add(mod)
        out.append(mod)
    return out


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
    return obj if isinstance(obj, dict) else None


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

        module_name = _infer_module_name(path)
        module_axioms = None
        if module_name:
            try:
                module_axioms = load_module_axioms(module_name)
            except ValueError as e:
                code, msg = _split_code_message(str(e), BLOCKED_INVALID_MODULE_AXIOM_EXTENSION)
                violations.append(_violation(code, msg or "DOMAIN_AXIOMS_<MODULE>.json inválido.", artifact))
                module_axioms = None

        # Para superfícies sem namespace de módulo no path (ex: contracts/asyncapi/**),
        # a regra canônica é validar enums contra o universo efetivo (global + extensões modulares declaradas).
        ctx = {
            "domain_enums": domain.domain_enums,
            "module_extension_policy": axioms.get("module_extension_policy", {}),
            "global_formats": axioms.get("global_formats", {}),
        }
        try:
            effective_enums = merge_enum_extensions(ctx, module_axioms)
        except ValueError as e:
            code, _ = _split_code_message(str(e), BLOCKED_INVALID_MODULE_AXIOM_EXTENSION)
            violations.append(_violation(code, "Extensão modular inválida.", artifact))
            effective_enums = domain.domain_enums

        if module_name is None:
            module_axioms_by_module, errs = _load_all_module_axioms()
            violations.extend(errs)
            for _, mod_axioms in sorted(module_axioms_by_module.items(), key=lambda kv: kv[0]):
                try:
                    effective_enums = merge_enum_extensions(
                        {
                            "domain_enums": effective_enums,
                            "module_extension_policy": axioms.get("module_extension_policy", {}),
                            "global_formats": axioms.get("global_formats", {}),
                        },
                        mod_axioms,
                    )
                except ValueError as e:
                    code, _ = _split_code_message(str(e), BLOCKED_INVALID_MODULE_AXIOM_EXTENSION)
                    violations.append(_violation(code, "Extensão modular inválida.", artifact))
                    break

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
    ".contract_driven/templates/globais/API_CONVENTIONS.md",
    ".contract_driven/templates/globais/DATA_CONVENTIONS.md",
    ".contract_driven/templates/globais/ERROR_MODEL.md",
    ".contract_driven/templates/globais/GLOBAL_INVARIANTS.md",
    ".contract_driven/templates/globais/DOMAIN_GLOSSARY.md",
    ".contract_driven/templates/globais/HANDBALL_RULES_DOMAIN.md",
    ".contract_driven/templates/globais/SECURITY_RULES.md",
    ".contract_driven/templates/globais/UI_FOUNDATIONS.md",
    ".contract_driven/templates/globais/DESIGN_SYSTEM.md",
    ".contract_driven/templates/globais/CI_CONTRACT_GATES.md",
    ".contract_driven/templates/globais/TEST_STRATEGY.md",
    ".contract_driven/templates/globais/decisions/ADR-0001-template.md",
    ".contract_driven/templates/modulos/README.md",
    ".contract_driven/templates/modulos/MODULE_SCOPE_{{MODULE_NAME_UPPER}}.md",
    ".contract_driven/templates/modulos/DOMAIN_RULES_{{MODULE_NAME_UPPER}}.md",
    ".contract_driven/templates/modulos/INVARIANTS_{{MODULE_NAME_UPPER}}.md",
    ".contract_driven/templates/modulos/STATE_MODEL_{{MODULE_NAME_UPPER}}.md",
    ".contract_driven/templates/modulos/PERMISSIONS_{{MODULE_NAME_UPPER}}.md",
    ".contract_driven/templates/modulos/ERRORS_{{MODULE_NAME_UPPER}}.md",
    ".contract_driven/templates/modulos/UI_CONTRACT_{{MODULE_NAME_UPPER}}.md",
    ".contract_driven/templates/modulos/SCREEN_MAP_{{MODULE_NAME_UPPER}}.md",
    ".contract_driven/templates/modulos/TEST_MATRIX_{{MODULE_NAME_UPPER}}.md",
    ".contract_driven/templates/modulos/snippets/module_human_docs_header.yaml",
    ".contract_driven/templates/modulos/schemas/{{DOMAIN_ENTITY_SNAKE}}.schema.json",
    ".contract_driven/templates/API_RULES/API_RULES.yaml",
    ".contract_driven/templates/API_RULES/ARCHITECTURE_MATRIX.yaml",
    ".contract_driven/templates/API_RULES/MODULE_PROFILE_REGISTRY.yaml",
    ".contract_driven/templates/API_RULES/CANONICAL_TYPE_REGISTRY.yaml",
    ".contract_driven/templates/API_RULES/REGRAS_API.md",
    ".contract_driven/templates/API_RULES/GoogleAPI.md",
    ".contract_driven/templates/API_RULES/AddidasAPI.md",
    ".contract_driven/templates/API_RULES/OWASPAPI.md",
    "scripts/contracts/validate/api/policy_compiler.py",
    "scripts/contracts/validate/api/compile_api_policy.py",
    "generated/README.md",
    "contracts/openapi/openapi.yaml",
    "docs/_canon/CI_CONTRACT_GATES.md",
    "docs/_canon/ERROR_MODEL.md",
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
    elif status == "PASS":
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


def _try_tool(*cmd: str, cwd: pathlib.Path | None = None) -> tuple[int, str, str]:
    """Run external tool; returns (returncode, stdout, stderr). rc=-1 means tool not found."""
    # On Windows, npm-installed CLIs are .cmd wrappers; shell=True is required to resolve them.
    use_shell = sys.platform == "win32"
    try:
        result = subprocess.run(
            list(cmd),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=str(cwd) if cwd else None,
            shell=use_shell,
        )
        stdout = (result.stdout or b"").decode("utf-8", errors="replace")
        stderr = (result.stderr or b"").decode("utf-8", errors="replace")
        return result.returncode, stdout, stderr
    except FileNotFoundError:
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
    rc, out, err = _try_tool(*cmd)
    if rc == -1:
        return None
    text = (out or err).strip()
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

    # Canonical module-aware layout checks (SSOT = CONTRACT_SYSTEM_LAYOUT.md)
    modules = _load_canonical_modules_from_layout(root)
    if not modules:
        violations.append({
            "blocking_code": BLOCKED_LAYOUT_NONCOMPLIANCE,
            "artifact": str(_layout_path(root).relative_to(root)),
            "message": "Não foi possível carregar a taxonomia canônica de módulos do LAYOUT.",
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
        _check_module_dirs("contracts/openapi/components/schemas", allow_extra={"shared"})

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
    module_min_docs: list[str] = []
    if modules:
        for mod in modules:
            up = mod.upper()
            module_min_docs.extend([
                f"docs/hbtrack/modulos/{mod}/README.md",
                f"docs/hbtrack/modulos/{mod}/MODULE_SCOPE_{up}.md",
                f"docs/hbtrack/modulos/{mod}/DOMAIN_RULES_{up}.md",
                f"docs/hbtrack/modulos/{mod}/INVARIANTS_{up}.md",
                f"docs/hbtrack/modulos/{mod}/TEST_MATRIX_{up}.md",
            ])
    for rel in module_min_docs:
        p = root / rel
        checked.append(str(p))
        if not p.exists():
            missing.append(rel)
    if missing:
        violations = [
            {
                "blocking_code": BLOCKED_MISSING_MODULE_DOC if m.startswith("docs/hbtrack/modulos/") else "BLOCKED_MISSING_REQUIRED_ARTIFACT",
                "artifact": m,
                "message": f"Artefato obrigatório ausente: {m}",
                "severity": "error",
            }
            for m in missing
        ]
        first_code = violations[0]["blocking_code"]
        return _pg(gate_id, "FAIL", True, first_code,
                   f"{len(missing)} artefato(s) obrigatório(s) ausente(s).",
                   [], checked, [], violations, _ms(t0))
    total_required = len(_CANONICAL_GLOBAL_DOCS) + len(module_min_docs)
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

    required_files: list[pathlib.Path] = []
    for mod in modules:
        up = mod.upper()
        required_files.extend([
            root / "docs" / "hbtrack" / "modulos" / mod / "README.md",
            root / "docs" / "hbtrack" / "modulos" / mod / f"MODULE_SCOPE_{up}.md",
            root / "docs" / "hbtrack" / "modulos" / mod / f"DOMAIN_RULES_{up}.md",
            root / "docs" / "hbtrack" / "modulos" / mod / f"INVARIANTS_{up}.md",
            root / "docs" / "hbtrack" / "modulos" / mod / f"TEST_MATRIX_{up}.md",
        ])

    for p in required_files:
        checked.append(str(p))
        if not p.exists():
            continue
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
        if hdr.get("module") != mod:
            violations.append({
                "blocking_code": BLOCKED_INVALID_MODULE_DOC_HEADER,
                "artifact": str(p.relative_to(root)),
                "message": "Header `module` não corresponde ao diretório do módulo.",
                "severity": "error",
            })
        for key in ("system_scope_ref", "handball_rules_ref", "handball_semantic_applicability", "contract_path_ref", "schemas_ref"):
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

        def _resolve_rel(field: str, expected_abs: pathlib.Path, expect_dir: bool = False) -> None:
            rel = hdr.get(field)
            if not isinstance(rel, str) or not rel.strip():
                return
            target = (p.parent / rel).resolve()
            if target != expected_abs.resolve():
                violations.append({
                    "blocking_code": BLOCKED_INVALID_MODULE_DOC_HEADER,
                    "artifact": str(p.relative_to(root)),
                    "message": f"Header `{field}` não aponta para o path canônico esperado.",
                    "severity": "error",
                })
                return
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

        _resolve_rel("system_scope_ref", root / "docs" / "_canon" / "SYSTEM_SCOPE.md")
        _resolve_rel("handball_rules_ref", root / "docs" / "_canon" / "HANDBALL_RULES_DOMAIN.md")
        _resolve_rel("contract_path_ref", root / "contracts" / "openapi" / "paths" / f"{mod}.yaml")
        _resolve_rel("schemas_ref", root / "contracts" / "schemas" / mod, expect_dir=True)

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
    # não aponta a SSOT (`.contract_driven/templates/API_RULES/API_RULES.yaml`), sinaliza.
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
    ssot_marker = ".contract_driven/templates/API_RULES/API_RULES.yaml"
    exclude = {
        canon_dir / "API_CONVENTIONS.md",
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
            "message": "Documento menciona convenção/shape HTTP mas não aponta a SSOT `.contract_driven/templates/API_RULES/API_RULES.yaml` (risco de duplicação normativa).",
            "severity": "warn",
        })
    if violations:
        return _pg(gate_id, "FAIL", False, WARN_API_NORMATIVE_OUTSIDE_SSOT,
                   f"{len(violations)} doc(s) do canon com risco de duplicação normativa de API.",
                   [], checked, [], violations, _ms(t0))
    return _pg(gate_id, "PASS", False, None,
               "Sem risco detectável de duplicação normativa de API no canon.", [], checked, [], [], _ms(t0))


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
        for token in _PLACEHOLDER_TOKENS:
            if token in text:
                violations.append({
                    "blocking_code": "BLOCKED_PLACEHOLDER_RESIDUE",
                    "artifact": str(p.relative_to(root)),
                    "message": f"Token placeholder '{token}' encontrado.",
                    "severity": "error",
                })
                break
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
            target = (p.parent / ref).resolve()
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


def _g5_openapi_root_structure(root: pathlib.Path) -> dict:
    t0 = time.monotonic()
    gate_id = "OPENAPI_ROOT_STRUCTURE_GATE"
    openapi_root = root / "contracts" / "openapi" / "openapi.yaml"
    redocly_cfg = root / "redocly.yaml"
    if not openapi_root.exists():
        return _skip(gate_id, "openapi.yaml ausente.", _ms(t0))
    cmd = ["redocly", "lint", str(openapi_root)]
    if redocly_cfg.exists():
        cmd += ["--config", str(redocly_cfg)]
    rc, stdout, stderr = _try_tool(*cmd, cwd=root)
    if rc == -1:
        return _pg(gate_id, "FAIL", True, "ERROR_INFRA",
                   "redocly CLI não encontrado. Instale: npm install -g @redocly/cli",
                   [str(openapi_root)], [str(openapi_root)], [],
                   [{"blocking_code": "ERROR_INFRA", "artifact": "redocly", "message": stderr, "severity": "error"}],
                   _ms(t0))
    output = stdout + stderr
    if rc != 0:
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


def _g6_openapi_policy_ruleset(root: pathlib.Path) -> dict:
    t0 = time.monotonic()
    gate_id = "OPENAPI_POLICY_RULESET_GATE"
    openapi_root = root / "contracts" / "openapi" / "openapi.yaml"
    spectral_cfg = root / ".spectral.yaml"
    if not openapi_root.exists():
        return _skip(gate_id, "openapi.yaml ausente.", _ms(t0))
    if not spectral_cfg.exists():
        return _skip(gate_id, ".spectral.yaml ausente.", _ms(t0))
    rc, stdout, stderr = _try_tool(
        "spectral", "lint", str(openapi_root),
        "--ruleset", str(spectral_cfg),
        "--format", "json",
        cwd=root,
    )
    if rc == -1:
        return _pg(gate_id, "FAIL", True, "ERROR_INFRA",
                   "spectral CLI não encontrado. Instale: npm install -g @stoplight/spectral-cli",
                   [str(openapi_root)], [str(openapi_root)], [],
                   [{"blocking_code": "ERROR_INFRA", "artifact": "spectral", "message": stderr, "severity": "error"}],
                   _ms(t0))
    combined = stdout + stderr
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
        return _pg(gate_id, "FAIL", True,
                   (violations[0] or {}).get("blocking_code", BLOCKED_CROSS_SPEC_DIVERGENCE),
                   f"{len(violations)} violação(ões) de alinhamento cross-spec.",
                   inputs, all_artifacts, [], violations, _ms(t0))
    return _pg(gate_id, "PASS", True, None,
               "Alinhamento cross-spec: PASS.",
               inputs, all_artifacts, [], [], _ms(t0))


def _g9_contract_breaking_change(root: pathlib.Path) -> dict:
    t0 = time.monotonic()
    gate_id = "CONTRACT_BREAKING_CHANGE_GATE"
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
    rc, stdout, stderr = _try_tool("oasdiff", "breaking", str(baseline), str(openapi_root), cwd=root)
    if rc == -1:
        return _pg(gate_id, "FAIL", True, "ERROR_INFRA",
                   "oasdiff não encontrado. Instale: go install github.com/tufin/oasdiff@latest",
                   [str(baseline), str(openapi_root)], [str(baseline), str(openapi_root)], [],
                   [{"blocking_code": "ERROR_INFRA", "artifact": "oasdiff", "message": stderr, "severity": "error"}],
                   _ms(t0))
    output = (stdout + stderr).strip()
    if rc != 0:
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
        return _pg(gate_id, "FAIL", True, "BLOCKED_BREAKING_CHANGE",
                   f"oasdiff: {len(violations)} breaking change(s) detectada(s).",
                   [str(baseline), str(openapi_root)], [str(baseline), str(openapi_root)], [], violations, _ms(t0))
    return _pg(gate_id, "PASS", True, None,
               "Nenhuma breaking change detectada.",
               [str(baseline), str(openapi_root)], [str(baseline), str(openapi_root)], [], [], _ms(t0))


def _g10_transformation_feasibility(root: pathlib.Path) -> dict:
    t0 = time.monotonic()
    gate_id = "TRANSFORMATION_FEASIBILITY_GATE"
    generated_dir = root / "contracts" / "generated"
    if not generated_dir.exists():
        return _skip(gate_id, "contracts/generated/ ausente — gate não aplicável.", _ms(t0))
    files = list(generated_dir.rglob("*"))
    if not files:
        return _skip(gate_id, "contracts/generated/ vazio — gate não aplicável.", _ms(t0))
    return _pg(gate_id, "PASS", False, None,
               f"contracts/generated/ presente com {len(files)} artefato(s).",
               [], [str(generated_dir)], [], [], _ms(t0))


def _g11_http_runtime_contract(_root: pathlib.Path) -> dict:
    return _skip(
        "HTTP_RUNTIME_CONTRACT_GATE",
        "Gate requer servidor live — sempre SKIP em ambiente local/CI.",
    )


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
    tool_cmd = ("asyncapi", "validate", str(asyncapi_root))
    rc, stdout, stderr = _try_tool(*tool_cmd, cwd=root)
    out = stdout + stderr
    if rc == -1 or (sys.platform == "win32" and _looks_like_windows_command_not_found("asyncapi", out)):
        local = _local_node_bin("asyncapi")
        if local is None:
            return _pg(gate_id, "FAIL", False, "ERROR_INFRA",
                       "asyncapi CLI não encontrado no PATH e node_modules/.bin/asyncapi também está ausente.",
                       [str(asyncapi_root)], [str(asyncapi_root)], [],
                       [{"blocking_code": "ERROR_INFRA", "artifact": "asyncapi", "message": (out or stderr), "severity": "error"}],
                       _ms(t0))
        rc, stdout, stderr = _try_tool(str(local), "validate", str(asyncapi_root), cwd=root)
        out = stdout + stderr
        if rc == -1 or (sys.platform == "win32" and _looks_like_windows_command_not_found(str(local), out)):
            return _pg(gate_id, "FAIL", False, "ERROR_INFRA",
                       "asyncapi CLI não executou (node_modules/.bin).",
                       [str(asyncapi_root)], [str(asyncapi_root)], [],
                       [{"blocking_code": "ERROR_INFRA", "artifact": str(local), "message": out, "severity": "error"}],
                       _ms(t0))
    if rc != 0:
        if _looks_like_node_missing(out):
            return _pg(
                gate_id,
                "FAIL",
                False,
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
        return _pg(gate_id, "FAIL", False, "BLOCKED_ASYNCAPI_INVALID",
                   "asyncapi validate falhou.",
                   [str(asyncapi_root)], [str(asyncapi_root)], [], violations, _ms(t0))
    return _pg(gate_id, "PASS", False, None,
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


def _g14_ui_doc_validation(root: pathlib.Path) -> dict:
    t0 = time.monotonic()
    gate_id = "UI_DOC_VALIDATION_GATE"
    contracts_dir = root / "contracts"
    ui_contracts = list(contracts_dir.rglob("UI_CONTRACT_*.md")) if contracts_dir.exists() else []
    if not ui_contracts:
        return _skip(gate_id, "Nenhum UI_CONTRACT_*.md encontrado — gate não aplicável.", _ms(t0))
    checked = [str(p) for p in ui_contracts]
    violations: list[dict] = []
    for p in ui_contracts:
        content = p.read_text(encoding="utf-8", errors="replace")
        for token in _PLACEHOLDER_TOKENS:
            if token in content:
                violations.append({
                    "blocking_code": "BLOCKED_UI_CONTRACT_PLACEHOLDER",
                    "artifact": str(p.relative_to(root)),
                    "message": f"Token placeholder '{token}' em UI contract.",
                    "severity": "error",
                })
                break
    if violations:
        return _pg(gate_id, "FAIL", False, "BLOCKED_UI_CONTRACT_PLACEHOLDER",
                   f"UI contracts: {len(violations)} arquivo(s) com placeholders.",
                   [], checked, [], violations, _ms(t0))
    return _pg(gate_id, "PASS", False, None,
               f"UI contracts: {len(ui_contracts)} arquivo(s) válido(s).",
               [], checked, [], [], _ms(t0))


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


def _g16_readiness_summary(gates: list[dict]) -> dict:
    t0 = time.monotonic()
    gate_id = "READINESS_SUMMARY_GATE"
    blocking_fails = [g for g in gates if g.get("blocking") and g.get("status") == "FAIL"]
    non_blocking_fails = [g for g in gates if not g.get("blocking") and g.get("status") == "FAIL"]
    passes = [g for g in gates if g.get("status") == "PASS"]
    skips = [g for g in gates if g.get("status") == "SKIP_NOT_APPLICABLE"]
    if blocking_fails:
        summary = f"Pipeline FAIL: {len(blocking_fails)} gate(s) bloqueante(s) falharam."
        status = "FAIL"
    elif non_blocking_fails:
        summary = f"Pipeline PASS com avisos: {len(non_blocking_fails)} gate(s) não-bloqueante(s) falharam."
        status = "PASS"
    else:
        summary = f"Pipeline PASS: {len(passes)} PASS, {len(skips)} SKIP."
        status = "PASS"
    return _pg(gate_id, status, False, None, summary, [], [], [], [], _ms(t0))


# ── Orchestrator + main ───────────────────────────────────────────────────────

def run_pipeline() -> tuple[dict, int]:
    root = _repo_root()
    axioms_path = root / ".contract_driven" / "DOMAIN_AXIOMS.json"
    axioms_schema_path = root / "contracts" / "schemas" / "shared" / "domain_axioms.schema.json"
    report_path = root / "_reports" / "contract_gates" / "latest.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    openapi_root = root / "contracts" / "openapi" / "openapi.yaml"
    asyncapi_root_p = root / "contracts" / "asyncapi" / "asyncapi.yaml"
    ts = datetime.datetime.now(datetime.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    def _build_report(all_gates: list[dict], overall: str, exit_code: int) -> dict:
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
            "exit_code": exit_code,
            "gates": all_gates,
        }

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
        report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
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
        report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return report, 4

    # G1–G15: run all gates in canonical order
    gates.append(_g1_path_canonicality(root))
    gates.append(_g2_required_artifact_presence(root))
    gates.append(_g2a_module_doc_crossrefs(root))
    gates.append(_g2b_api_normative_duplication(root))
    gates.append(_g3_placeholder_residue(root))
    gates.append(_g4_ref_hermeticity(root))
    gates.append(_g5_openapi_root_structure(root))
    gates.append(_g6_openapi_policy_ruleset(root))
    gates.append(_g7_json_schema_validation(root))
    gates.append(_g8_cross_spec_alignment(root, axioms))
    gates.append(_g9_contract_breaking_change(root))
    gates.append(_g10_transformation_feasibility(root))
    gates.append(_g11_http_runtime_contract(root))
    gates.append(_g12_asyncapi_validation(root))
    gates.append(_g13_arazzo_validation(root))
    gates.append(_g14_ui_doc_validation(root))
    gates.append(_g15_derived_drift(root))

    # G16: readiness summary
    g16 = _g16_readiness_summary(gates)
    gates.append(g16)

    blocking_fails = [g for g in gates if g.get("blocking") and g.get("status") == "FAIL"]
    error_infra = any(
        v.get("blocking_code") == "ERROR_INFRA"
        for g in gates
        for v in (g.get("violations") or [])
    )
    if blocking_fails:
        overall = "FAIL"
        exit_code = 3 if error_infra else 2
    elif any(g.get("status") == "FAIL" for g in gates):
        overall = "PASS_WITH_WARNINGS"
        exit_code = 0
    else:
        overall = "PASS"
        exit_code = 0

    report = _build_report(gates, overall, exit_code)
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return report, exit_code


def main() -> int:
    report, exit_code = run_pipeline()
    gates = report.get("gates", [])
    overall = report.get("overall_status", "?")

    sep = "-" * 62
    print(f"\n{sep}")
    print(f"  HB TRACK CONTRACT GATES  --  {overall}")
    print(sep)
    for g in gates:
        status = g.get("status", "?")
        gid = g.get("gate_id", "?")
        summary = g.get("summary", "")
        if status == "PASS":
            icon = "+"
        elif status == "SKIP_NOT_APPLICABLE":
            icon = "~"
        else:
            icon = "!"
        print(f"  {icon} [{status:<24}] {gid}")
        if status == "FAIL":
            print(f"       {summary}")
            for v in (g.get("violations") or [])[:3]:
                print(f"       - {str(v.get('message', ''))[:100]}")
    print(sep)
    print(f"  Overall  : {overall}")
    print(f"  Exit code: {exit_code}")
    root = _repo_root()
    report_path = root / "_reports" / "contract_gates" / "latest.json"
    print(f"  Report   : {report_path}")
    print(f"{sep}\n")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
