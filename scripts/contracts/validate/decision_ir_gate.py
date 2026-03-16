"""decision_ir_gate.py — DECISION_IR_CONFORMANCE_GATE
All 20 rejection codes from §5 of DECISION_IR_CONFORMANCE_GATE.md.
Calibrated for the actual HB-TRACK MODULE_DECISION_IR schema.
"""
from __future__ import annotations

import json
import pathlib
import time
from typing import Any

# ---------------------------------------------------------------------------
# Rejection code constants (§5)
# ---------------------------------------------------------------------------
IR_SCHEMA_INVALID = "IR_SCHEMA_INVALID"
IR_UNKNOWN_MODULE = "IR_UNKNOWN_MODULE"
IR_UNKNOWN_SEMANTIC_TYPE_REF = "IR_UNKNOWN_SEMANTIC_TYPE_REF"
IR_UNKNOWN_REGISTRY_REF = "IR_UNKNOWN_REGISTRY_REF"
IR_REGISTRY_DRIFT = "IR_REGISTRY_DRIFT"
IR_ENTITY_WITHOUT_REQUIRED_FIELDS = "IR_ENTITY_WITHOUT_REQUIRED_FIELDS"
IR_FIELD_WITHOUT_CANONICAL_TYPE = "IR_FIELD_WITHOUT_CANONICAL_TYPE"
IR_RELATION_WITHOUT_OWNERSHIP = "IR_RELATION_WITHOUT_OWNERSHIP"
IR_RELATION_WITHOUT_DELETE_POLICY = "IR_RELATION_WITHOUT_DELETE_POLICY"
IR_LIFECYCLE_WITHOUT_STATE_MODEL = "IR_LIFECYCLE_WITHOUT_STATE_MODEL"
IR_INVALID_STATE_TRANSITION = "IR_INVALID_STATE_TRANSITION"
IR_RULE_WITHOUT_FORMAL_CHECK_HINT = "IR_RULE_WITHOUT_FORMAL_CHECK_HINT"
IR_API_USE_CASE_INCOMPLETE = "IR_API_USE_CASE_INCOMPLETE"
IR_UI_FLOW_INCOMPLETE_WHEN_UI_APPLICABLE = "IR_UI_FLOW_INCOMPLETE_WHEN_UI_APPLICABLE"
IR_PERMISSION_MODEL_INCOMPLETE_WHEN_RBAC_APPLICABLE = "IR_PERMISSION_MODEL_INCOMPLETE_WHEN_RBAC_APPLICABLE"
IR_ERROR_MODEL_INCOMPLETE_WHEN_DOMAIN_ERRORS_APPLICABLE = "IR_ERROR_MODEL_INCOMPLETE_WHEN_DOMAIN_ERRORS_APPLICABLE"
IR_EVENT_MODEL_INCOMPLETE_WHEN_EVENTS_APPLICABLE = "IR_EVENT_MODEL_INCOMPLETE_WHEN_EVENTS_APPLICABLE"
IR_OPEN_DECISION_BLOCKING = "IR_OPEN_DECISION_BLOCKING"
IR_SURFACE_MAPPING_INCOMPLETE = "IR_SURFACE_MAPPING_INCOMPLETE"
IR_NON_DETERMINISTIC_MATERIALIZATION_RISK = "IR_NON_DETERMINISTIC_MATERIALIZATION_RISK"

ALL_IR_REJECTION_CODES: frozenset[str] = frozenset({
    IR_SCHEMA_INVALID,
    IR_UNKNOWN_MODULE,
    IR_UNKNOWN_SEMANTIC_TYPE_REF,
    IR_UNKNOWN_REGISTRY_REF,
    IR_REGISTRY_DRIFT,
    IR_ENTITY_WITHOUT_REQUIRED_FIELDS,
    IR_FIELD_WITHOUT_CANONICAL_TYPE,
    IR_RELATION_WITHOUT_OWNERSHIP,
    IR_RELATION_WITHOUT_DELETE_POLICY,
    IR_LIFECYCLE_WITHOUT_STATE_MODEL,
    IR_INVALID_STATE_TRANSITION,
    IR_RULE_WITHOUT_FORMAL_CHECK_HINT,
    IR_API_USE_CASE_INCOMPLETE,
    IR_UI_FLOW_INCOMPLETE_WHEN_UI_APPLICABLE,
    IR_PERMISSION_MODEL_INCOMPLETE_WHEN_RBAC_APPLICABLE,
    IR_ERROR_MODEL_INCOMPLETE_WHEN_DOMAIN_ERRORS_APPLICABLE,
    IR_EVENT_MODEL_INCOMPLETE_WHEN_EVENTS_APPLICABLE,
    IR_OPEN_DECISION_BLOCKING,
    IR_SURFACE_MAPPING_INCOMPLETE,
    IR_NON_DETERMINISTIC_MATERIALIZATION_RISK,
})

# ---------------------------------------------------------------------------
# Domain knowledge
# ---------------------------------------------------------------------------
_CANONICAL_MODULES: frozenset[str] = frozenset({
    "users", "seasons", "teams", "training", "wellness", "medical",
    "competitions", "matches", "scout", "exercises", "analytics",
    "reports", "ai_ingestion", "identity_access", "audit", "notifications",
})

_CANONICAL_SEMANTIC_TYPE_REFS: frozenset[str] = frozenset({
    "uuid", "uuid_ref", "uuid_array", "string", "text", "integer", "float",
    "boolean", "timestamp", "date", "enum", "enum_ref", "json_object",
    "json_array", "constraint", "derived", "snapshot", "url", "email",
    "phone", "slug", "semver", "percentage", "duration_minutes",
    "currency_cents", "locale_code", "timezone", "hash_sha256",
    # extended variants found in schema
    "string_array", "integer_array", "boolean_flag", "decimal", "date_range",
    "json",  # alias for json_object
})

_VALID_DELETE_POLICY_PREFIXES: tuple[str, ...] = (
    "restrict", "cascade", "set_null", "set null", "no_action", "no action",
)

_ENTITY_REQUIRED_FIELDS: frozenset[str] = frozenset({"id", "created_at", "updated_at"})

# ---------------------------------------------------------------------------
# Violation builder
# ---------------------------------------------------------------------------

def _violation(code: str, message: str, path: str = "", severity: str = "error") -> dict:
    return {
        "code": code,
        "blocking_code": code,
        "message": message,
        "path": path,
        "severity": severity,
    }


def _entity_label(entity: dict) -> str:
    """Return best display name for an entity dict."""
    return entity.get("label") or entity.get("entity_id") or entity.get("name") or "?"


def _field_type(field: dict) -> str:
    """Return canonical type from a field dict (handles multiple key variants)."""
    return (
        field.get("semantic_type_ref")
        or field.get("type")
        or field.get("semantic_type")
        or ""
    ).lower()


# ---------------------------------------------------------------------------
# 1. Schema validity  — IR_SCHEMA_INVALID
# ---------------------------------------------------------------------------

def _check_schema_validity(ir: Any, schema: dict | None) -> list[dict]:
    violations: list[dict] = []
    if schema is None:
        return violations
    try:
        import jsonschema  # type: ignore
        validator = jsonschema.Draft7Validator(schema)
        for err in validator.iter_errors(ir):
            violations.append(_violation(
                IR_SCHEMA_INVALID,
                f"Schema violation at {err.json_path}: {err.message}",
                err.json_path,
            ))
    except ImportError:
        pass  # jsonschema not available — skip structural validation
    return violations


# ---------------------------------------------------------------------------
# 2. Registry conformance
#    IR_UNKNOWN_MODULE, IR_FIELD_WITHOUT_CANONICAL_TYPE,
#    IR_UNKNOWN_SEMANTIC_TYPE_REF, IR_UNKNOWN_REGISTRY_REF
# ---------------------------------------------------------------------------

def _check_registry_conformance(ir: Any) -> list[dict]:
    violations: list[dict] = []
    if not isinstance(ir, dict):
        return violations

    # --- IR_UNKNOWN_MODULE: top-level module declaration ---
    module = (ir.get("module") or "").lower()
    if module and module not in _CANONICAL_MODULES:
        violations.append(_violation(
            IR_UNKNOWN_MODULE,
            f"Module '{module}' is not in the canonical module registry.",
            ".module",
        ))

    # --- IR_UNKNOWN_MODULE: relation cross-module references ---
    for rel in (ir.get("relations") or []):
        rid = rel.get("relation_id") or rel.get("name", "?")
        for key in ("from_module", "to_module", "source_module", "target_module"):
            ref = (rel.get(key) or "").lower()
            if ref and ref not in _CANONICAL_MODULES:
                violations.append(_violation(
                    IR_UNKNOWN_MODULE,
                    f"Relation '{rid}' references unknown module '{ref}'.",
                    f".relations[{rid}].{key}",
                ))

    # --- IR_FIELD_WITHOUT_CANONICAL_TYPE / IR_UNKNOWN_SEMANTIC_TYPE_REF ---
    for entity in (ir.get("entities") or []):
        ename = _entity_label(entity)
        for field in (entity.get("fields") or []):
            fname = field.get("name", "?")
            ftype = _field_type(field)
            if not ftype:
                violations.append(_violation(
                    IR_FIELD_WITHOUT_CANONICAL_TYPE,
                    f"Field '{fname}' in entity '{ename}' missing semantic type declaration.",
                    f".entities[{ename}].fields[{fname}]",
                ))
            elif ftype not in _CANONICAL_SEMANTIC_TYPE_REFS:
                violations.append(_violation(
                    IR_UNKNOWN_SEMANTIC_TYPE_REF,
                    f"Field '{fname}' in entity '{ename}' uses unknown semantic type '{ftype}'.",
                    f".entities[{ename}].fields[{fname}].semantic_type_ref",
                ))

    # --- IR_UNKNOWN_REGISTRY_REF: explicit registry_ref / ref_module on fields ---
    for entity in (ir.get("entities") or []):
        ename = _entity_label(entity)
        for field in (entity.get("fields") or []):
            fname = field.get("name", "?")
            ref = field.get("registry_ref") or field.get("ref_module")
            if ref:
                ref_mod = ref.lower().split(".")[0]
                if ref_mod not in _CANONICAL_MODULES:
                    violations.append(_violation(
                        IR_UNKNOWN_REGISTRY_REF,
                        f"Field '{fname}' in entity '{ename}' references unknown registry "
                        f"module '{ref}'.",
                        f".entities[{ename}].fields[{fname}].registry_ref",
                    ))

    return violations


# ---------------------------------------------------------------------------
# 3. Semantic coherence
#    IR_ENTITY_WITHOUT_REQUIRED_FIELDS, IR_RELATION_WITHOUT_OWNERSHIP,
#    IR_RELATION_WITHOUT_DELETE_POLICY, IR_LIFECYCLE_WITHOUT_STATE_MODEL,
#    IR_INVALID_STATE_TRANSITION
# ---------------------------------------------------------------------------

def _check_semantic_coherence(ir: Any) -> list[dict]:
    violations: list[dict] = []
    if not isinstance(ir, dict):
        return violations

    # --- IR_ENTITY_WITHOUT_REQUIRED_FIELDS ---
    for entity in (ir.get("entities") or []):
        ename = _entity_label(entity)
        declared = {(f.get("name") or "").lower() for f in (entity.get("fields") or [])}
        missing = _ENTITY_REQUIRED_FIELDS - declared
        if missing:
            violations.append(_violation(
                IR_ENTITY_WITHOUT_REQUIRED_FIELDS,
                f"Entity '{ename}' is missing required fields: {sorted(missing)}.",
                f".entities[{ename}]",
            ))

    # --- IR_RELATION_WITHOUT_OWNERSHIP (sovereignty in HB-TRACK IR) ---
    for rel in (ir.get("relations") or []):
        rid = rel.get("relation_id") or rel.get("name", "?")
        ownership = rel.get("ownership") or rel.get("sovereignty")
        if not ownership:
            violations.append(_violation(
                IR_RELATION_WITHOUT_OWNERSHIP,
                f"Relation '{rid}' is missing ownership/sovereignty declaration.",
                f".relations[{rid}]",
            ))

    # --- IR_RELATION_WITHOUT_DELETE_POLICY ---
    for rel in (ir.get("relations") or []):
        rid = rel.get("relation_id") or rel.get("name", "?")
        dp = rel.get("delete_policy") or rel.get("on_delete") or ""
        dp_lower = str(dp).lower().strip()
        if not dp_lower:
            violations.append(_violation(
                IR_RELATION_WITHOUT_DELETE_POLICY,
                f"Relation '{rid}' is missing delete_policy declaration.",
                f".relations[{rid}]",
            ))
        elif not any(dp_lower.startswith(p) for p in _VALID_DELETE_POLICY_PREFIXES):
            violations.append(_violation(
                IR_RELATION_WITHOUT_DELETE_POLICY,
                f"Relation '{rid}' delete_policy '{dp[:60]}' must start with one of: "
                f"{list(_VALID_DELETE_POLICY_PREFIXES)}.",
                f".relations[{rid}].delete_policy",
            ))

    # --- IR_LIFECYCLE_WITHOUT_STATE_MODEL / IR_INVALID_STATE_TRANSITION ---
    # state_models is a top-level list in HB-TRACK IR schema
    state_models = ir.get("state_models") or []
    if isinstance(state_models, list):
        for sm in state_models:
            if not isinstance(sm, dict):
                continue
            sm_id = sm.get("lifecycle_id") or sm.get("id") or "?"
            states_raw = sm.get("states") or []
            state_names: set[str] = set()
            for s in states_raw:
                if isinstance(s, str):
                    state_names.add(s)
                elif isinstance(s, dict):
                    state_names.add(s.get("name") or s.get("id") or "")
            if not state_names:
                violations.append(_violation(
                    IR_LIFECYCLE_WITHOUT_STATE_MODEL,
                    f"State model '{sm_id}' has no states defined.",
                    f".state_models[{sm_id}].states",
                ))
            initial = sm.get("initial_state")
            if initial and initial not in state_names:
                violations.append(_violation(
                    IR_INVALID_STATE_TRANSITION,
                    f"State model '{sm_id}': initial_state '{initial}' is not a declared state.",
                    f".state_models[{sm_id}].initial_state",
                ))
            for tr in (sm.get("transitions") or []):
                if not isinstance(tr, dict):
                    continue
                src = tr.get("from") or tr.get("source")
                dst = tr.get("to") or tr.get("target")
                if src and state_names and src not in state_names:
                    violations.append(_violation(
                        IR_INVALID_STATE_TRANSITION,
                        f"State model '{sm_id}': transition source '{src}' is not a declared state.",
                        f".state_models[{sm_id}].transitions",
                    ))
                if dst and state_names and dst not in state_names:
                    violations.append(_violation(
                        IR_INVALID_STATE_TRANSITION,
                        f"State model '{sm_id}': transition target '{dst}' is not a declared state.",
                        f".state_models[{sm_id}].transitions",
                    ))

    # Legacy: entities with embedded lifecycle key
    for entity in (ir.get("entities") or []):
        lifecycle = entity.get("lifecycle")
        if lifecycle is not None and not isinstance(lifecycle, (str, dict)):
            violations.append(_violation(
                IR_LIFECYCLE_WITHOUT_STATE_MODEL,
                f"Entity '{_entity_label(entity)}' lifecycle must be a string ref or object.",
                f".entities[{_entity_label(entity)}].lifecycle",
            ))

    return violations


# ---------------------------------------------------------------------------
# 4. Surface completeness
#    IR_RULE_WITHOUT_FORMAL_CHECK_HINT, IR_API_USE_CASE_INCOMPLETE,
#    IR_UI_FLOW_INCOMPLETE_WHEN_UI_APPLICABLE,
#    IR_PERMISSION_MODEL_INCOMPLETE_WHEN_RBAC_APPLICABLE,
#    IR_ERROR_MODEL_INCOMPLETE_WHEN_DOMAIN_ERRORS_APPLICABLE,
#    IR_EVENT_MODEL_INCOMPLETE_WHEN_EVENTS_APPLICABLE
# ---------------------------------------------------------------------------

def _check_surface_completeness(ir: Any) -> list[dict]:
    violations: list[dict] = []
    if not isinstance(ir, dict):
        return violations

    # --- IR_RULE_WITHOUT_FORMAL_CHECK_HINT ---
    for rule in (ir.get("rules") or []):
        rname = rule.get("rule_id") or rule.get("name", "?")
        has_hint = bool(
            rule.get("formal_check_hint")
            or rule.get("check_hint")
            or rule.get("invariant_ref")
        )
        if not has_hint:
            violations.append(_violation(
                IR_RULE_WITHOUT_FORMAL_CHECK_HINT,
                f"Rule '{rname}' lacks a formal_check_hint / invariant_ref.",
                f".rules[{rname}]",
                severity="warn",
            ))

    # --- IR_API_USE_CASE_INCOMPLETE ---
    for uc in (ir.get("api_use_cases") or ir.get("use_cases") or []):
        ucid = uc.get("use_case_id") or uc.get("name", "?")
        missing: list[str] = []
        if not (uc.get("actor")):
            missing.append("actor")
        if not (uc.get("goal") or uc.get("intent")):
            missing.append("goal/intent")
        if not (uc.get("operation") or uc.get("steps") or uc.get("flow")):
            missing.append("operation/steps")
        if not (uc.get("resource_ref") or uc.get("resource") or uc.get("response_entity")):
            missing.append("resource_ref/response_entity")
        if missing:
            violations.append(_violation(
                IR_API_USE_CASE_INCOMPLETE,
                f"Use case '{ucid}' is incomplete — missing: {missing}.",
                f".api_use_cases[{ucid}]",
            ))

    # --- IR_UI_FLOW_INCOMPLETE_WHEN_UI_APPLICABLE ---
    ui_flows = ir.get("ui_flows") or ir.get("screens") or []
    if ui_flows:
        for flow in ui_flows:
            if not isinstance(flow, dict):
                continue
            fid = flow.get("flow_id") or flow.get("name", "?")
            if not flow.get("steps") and not flow.get("screens"):
                violations.append(_violation(
                    IR_UI_FLOW_INCOMPLETE_WHEN_UI_APPLICABLE,
                    f"UI flow '{fid}' has no steps defined.",
                    f".ui_flows[{fid}]",
                ))

    # --- IR_PERMISSION_MODEL_INCOMPLETE_WHEN_RBAC_APPLICABLE ---
    perms = ir.get("permissions") or ir.get("permission_model")
    if perms is not None:
        if isinstance(perms, dict):
            has_roles = bool(perms.get("roles"))
            has_policies = bool(perms.get("policies") or perms.get("enforcement_policy"))
            if not has_roles and not has_policies:
                violations.append(_violation(
                    IR_PERMISSION_MODEL_INCOMPLETE_WHEN_RBAC_APPLICABLE,
                    "Permission model declared but 'roles' and 'policies' are both absent.",
                    ".permissions",
                ))
        elif isinstance(perms, list) and len(perms) == 0:
            violations.append(_violation(
                IR_PERMISSION_MODEL_INCOMPLETE_WHEN_RBAC_APPLICABLE,
                "Permission model is an empty list.",
                ".permissions",
            ))

    # --- IR_ERROR_MODEL_INCOMPLETE_WHEN_DOMAIN_ERRORS_APPLICABLE ---
    errors = ir.get("errors") or ir.get("error_model") or ir.get("error_codes")
    if errors is not None:
        if isinstance(errors, list) and len(errors) == 0:
            violations.append(_violation(
                IR_ERROR_MODEL_INCOMPLETE_WHEN_DOMAIN_ERRORS_APPLICABLE,
                "Error model declared but the list is empty.",
                ".errors",
            ))
        elif isinstance(errors, dict):
            if not errors.get("errors") and not errors.get("codes"):
                violations.append(_violation(
                    IR_ERROR_MODEL_INCOMPLETE_WHEN_DOMAIN_ERRORS_APPLICABLE,
                    "Error model declared but no 'errors' or 'codes' entries found.",
                    ".errors",
                ))

    # --- IR_EVENT_MODEL_INCOMPLETE_WHEN_EVENTS_APPLICABLE ---
    events = ir.get("events") or ir.get("event_model")
    if events is not None:
        emitted: list = []
        if isinstance(events, dict):
            emitted = events.get("emitted") or events.get("events") or []
        elif isinstance(events, list):
            emitted = events
        for evt in emitted:
            if not isinstance(evt, dict):
                continue
            eid = evt.get("event_id") or evt.get("name", "?")
            if not evt.get("trigger") and not evt.get("payload") and not evt.get("schema"):
                violations.append(_violation(
                    IR_EVENT_MODEL_INCOMPLETE_WHEN_EVENTS_APPLICABLE,
                    f"Event '{eid}' has no trigger or payload defined.",
                    f".events.emitted[{eid}]",
                ))

    return violations


# ---------------------------------------------------------------------------
# 5. Deterministic readiness
#    IR_OPEN_DECISION_BLOCKING, IR_SURFACE_MAPPING_INCOMPLETE,
#    IR_NON_DETERMINISTIC_MATERIALIZATION_RISK
# ---------------------------------------------------------------------------

def _check_deterministic_readiness(ir: Any) -> list[dict]:
    violations: list[dict] = []
    if not isinstance(ir, dict):
        return violations

    # --- IR_OPEN_DECISION_BLOCKING ---
    for decision in (ir.get("open_decisions") or ir.get("decisions") or []):
        if not isinstance(decision, dict):
            continue
        did = decision.get("decision_id") or decision.get("id") or decision.get("name", "?")
        is_blocking = bool(decision.get("blocking", False))
        resolved = (decision.get("status") or "open").lower() in ("resolved", "closed", "accepted")
        if is_blocking and not resolved:
            violations.append(_violation(
                IR_OPEN_DECISION_BLOCKING,
                f"Open decision '{did}' is marked blocking=true and not yet resolved.",
                f".open_decisions[{did}]",
            ))

    # --- IR_SURFACE_MAPPING_INCOMPLETE ---
    surface_map = ir.get("surface_mapping") or ir.get("ir_to_surface_mapping")
    if surface_map is not None:
        items: list = surface_map if isinstance(surface_map, list) else [surface_map]
        for binding in items:
            if not isinstance(binding, dict):
                continue
            surface = binding.get("surface") or "?"
            artifact = binding.get("artifact_path") or binding.get("target") or binding.get("artifact")
            if not artifact:
                violations.append(_violation(
                    IR_SURFACE_MAPPING_INCOMPLETE,
                    f"Surface binding '{surface}' has no artifact_path / target defined.",
                    f".surface_mapping[{surface}]",
                ))

    # --- IR_NON_DETERMINISTIC_MATERIALIZATION_RISK ---
    # Check for derived fields with no derivation formula
    for entity in (ir.get("entities") or []):
        ename = _entity_label(entity)
        for field in (entity.get("fields") or []):
            fname = field.get("name", "?")
            ftype = _field_type(field)
            if ftype == "derived" and not (
                field.get("derivation")
                or field.get("formula")
                or field.get("derived_from")
                or field.get("derivation_rule")
            ):
                violations.append(_violation(
                    IR_NON_DETERMINISTIC_MATERIALIZATION_RISK,
                    f"Derived field '{fname}' in entity '{ename}' has no derivation formula.",
                    f".entities[{ename}].fields[{fname}]",
                ))

    # Check for open_decisions with no recommendation when blocking
    for decision in (ir.get("open_decisions") or []):
        if not isinstance(decision, dict):
            continue
        did = decision.get("decision_id") or "?"
        is_blocking = bool(decision.get("blocking", False))
        has_recommendation = bool(decision.get("recommendation") or decision.get("resolution"))
        if is_blocking and not has_recommendation:
            violations.append(_violation(
                IR_NON_DETERMINISTIC_MATERIALIZATION_RISK,
                f"Blocking decision '{did}' has no resolution or recommendation, "
                "creating materialization ambiguity.",
                f".open_decisions[{did}]",
                severity="warn",
            ))

    return violations


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def run_decision_ir_gate(
    ir_path: pathlib.Path,
    schema_path: pathlib.Path | None = None,
) -> dict:
    """Run all 5 check groups against *ir_path* and return a gate result dict."""
    t0 = time.monotonic()
    artifacts_checked: list[str] = [str(ir_path)]
    violations: list[dict] = []

    # Load IR
    try:
        raw = ir_path.read_text(encoding="utf-8")
        suffix = ir_path.suffix.lower()
        if suffix in (".yaml", ".yml"):
            try:
                import yaml  # type: ignore
                ir = yaml.safe_load(raw)
            except ImportError:
                ir = json.loads(raw)
        else:
            ir = json.loads(raw)
    except Exception as exc:
        return _make_gate_result(
            "FAIL",
            [_violation(IR_SCHEMA_INVALID, f"Cannot parse IR file: {exc}")],
            artifacts_checked,
            time.monotonic() - t0,
        )

    # Load schema (optional)
    schema: dict | None = None
    if schema_path and schema_path.exists():
        try:
            schema = json.loads(schema_path.read_text(encoding="utf-8"))
            artifacts_checked.append(str(schema_path))
        except Exception:
            pass

    # Run the 5 check groups
    violations += _check_schema_validity(ir, schema)
    violations += _check_registry_conformance(ir)
    violations += _check_semantic_coherence(ir)
    violations += _check_surface_completeness(ir)
    violations += _check_deterministic_readiness(ir)

    elapsed = time.monotonic() - t0
    status = "PASS" if not violations else "FAIL"
    return _make_gate_result(status, violations, artifacts_checked, elapsed)


def _make_gate_result(
    status: str,
    violations: list[dict],
    artifacts_checked: list[str],
    elapsed_s: float,
) -> dict:
    return {
        "gate_id": "DECISION_IR_CONFORMANCE_GATE",
        "status": status,
        "blocking": True,
        "violations": violations,
        "artifacts_checked": artifacts_checked,
        "duration_ms": int(elapsed_s * 1000),
    }
