from __future__ import annotations

import dataclasses
import pathlib
import re
from typing import Any

from contracts.validate.api.policy_compiler import (  # noqa: PLC0415
    CompilerViolation,
    PolicyCompilerError,
    _canonical_type_registry_path,
    _load_canonical_types,
    _load_yaml_bytes,
    _rel,
    compile_expected,
)


@dataclasses.dataclass(frozen=True)
class YamlDocWithMarks:
    data: Any
    marks: dict[str, dict[str, int]]  # json_path -> {"line": int, "column": int}


_IDENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def _json_path_for_key(base: str, key: str) -> str:
    if _IDENT.match(key):
        return f"{base}.{key}"
    esc = key.replace("\\", "\\\\").replace("'", "\\'")
    return f"{base}['{esc}']"


def _json_path_for_index(base: str, idx: int) -> str:
    return f"{base}[{idx}]"


def _load_yaml_with_marks(path: pathlib.Path) -> YamlDocWithMarks:
    try:
        import yaml  # type: ignore
    except ImportError as e:  # pragma: no cover
        raise PolicyCompilerError("PyYAML não instalado (necessário para compiler de intent).") from e

    text = path.read_text(encoding="utf-8")
    node = yaml.compose(text)
    data = yaml.safe_load(text)

    marks: dict[str, dict[str, int]] = {}

    def _mark(n: Any) -> dict[str, int] | None:
        m = getattr(n, "start_mark", None)
        if m is None:
            return None
        # PyYAML is 0-based internally
        return {"line": int(m.line) + 1, "column": int(m.column) + 1}

    def _walk(n: Any, jp: str) -> None:
        mk = _mark(n)
        if mk is not None:
            marks.setdefault(jp, mk)

        kind = type(n).__name__
        if kind == "MappingNode":
            # value: list[tuple[keyNode, valueNode]]
            for k_node, v_node in getattr(n, "value", []) or []:
                k = getattr(k_node, "value", None)
                if not isinstance(k, str):
                    continue
                child = _json_path_for_key(jp, k)
                _walk(v_node, child)
                # também registrar a localização do próprio key, útil para erros de chave
                km = _mark(k_node)
                if km is not None:
                    marks.setdefault(f"{child}.__key__", km)
        elif kind == "SequenceNode":
            for i, it in enumerate(getattr(n, "value", []) or []):
                _walk(it, _json_path_for_index(jp, i))

    if node is not None:
        _walk(node, "$")
    return YamlDocWithMarks(data=data, marks=marks)


def _nearest_location(marks: dict[str, dict[str, int]], json_path: str) -> dict[str, int] | None:
    if json_path in marks:
        return marks[json_path]
    # fallback: tentar key mark
    if f"{json_path}.__key__" in marks:
        return marks[f"{json_path}.__key__"]

    # subir na árvore até encontrar algo
    cur = json_path
    for _ in range(50):
        if cur in marks:
            return marks[cur]
        if cur == "$":
            break
        if cur.endswith("]"):
            cur = cur.rsplit("[", 1)[0]
            continue
        if "['" in cur:
            cur = cur.rsplit("[", 1)[0]
            continue
        if "." in cur:
            cur = cur.rsplit(".", 1)[0]
            continue
        break
    return marks.get("$")


def _global_semantic_ids(root: pathlib.Path) -> set[str]:
    canon = _load_canonical_types(root)
    derived = canon.get("derived_types") or {}
    out: set[str] = set()
    if isinstance(derived, dict):
        for _, spec in derived.items():
            if isinstance(spec, dict) and isinstance(spec.get("semantic_id"), str):
                out.add(spec["semantic_id"])
    return out


def _intent_path(root: pathlib.Path, module: str) -> pathlib.Path:
    base = root / "contracts" / "openapi" / "intents"
    for suf in (".intent.yaml", ".intent.yml"):
        p = base / f"{module}{suf}"
        if p.exists():
            return p
    return base / f"{module}.intent.yaml"


def _render_openapi_paths_yaml(
    *,
    module: str,
    intent_relpath: str,
    endpoints: list[dict[str, Any]],
) -> bytes:
    path_map: dict[str, Any] = {}

    method_order = ["get", "post", "put", "patch", "delete", "options", "head", "trace"]
    method_rank = {m: i for i, m in enumerate(method_order)}

    for ep in endpoints:
        path = ep["path"]
        method = ep["method"]
        op: dict[str, Any] = {
            "tags": ep.get("tags") or [module],
            "summary": ep.get("summary") or "",
            "description": ep.get("description") or "",
            "operationId": ep["operationId"],
            "responses": ep.get("responses") or {"200": {"description": "OK"}},
        }
        if "parameters" in ep:
            op["parameters"] = ep["parameters"]
        if "requestBody" in ep:
            op["requestBody"] = ep["requestBody"]

        path_map.setdefault(path, {})
        path_map[path][method] = op

    # ordenação determinística
    ordered_paths: dict[str, Any] = {}
    for p in sorted(path_map.keys()):
        ops: dict[str, Any] = path_map[p]
        ordered_ops: dict[str, Any] = {}
        for m in sorted(ops.keys(), key=lambda x: method_rank.get(x, 999)):
            ordered_ops[m] = ops[m]
        ordered_paths[p] = ordered_ops

    try:
        import yaml  # type: ignore
    except ImportError as e:  # pragma: no cover
        raise PolicyCompilerError("PyYAML não instalado (necessário para render OpenAPI).") from e

    header = (
        f"# Path items for module: {module}\n"
        f"# Source of truth: contracts/openapi/openapi.yaml\n"
        f"# Generated by: scripts/contracts/validate/api/compile_api_intent.py\n"
        f"# Intent: {intent_relpath}\n"
        "#\n"
        "# Do not edit this file manually when using the intent compiler.\n"
    )

    body_obj: Any = ordered_paths
    if not ordered_paths:
        body_obj = {}

    body_text = yaml.safe_dump(
        body_obj,
        sort_keys=True,
        allow_unicode=True,
        width=120,
        default_flow_style=False,
    )
    if not body_text.endswith("\n"):
        body_text += "\n"
    return (header + "\n" + body_text).encode("utf-8")


@dataclasses.dataclass(frozen=True)
class IntentCompileResult:
    module: str
    intent_relpath: str
    openapi_paths_relpath: str
    openapi_paths_bytes: bytes
    extra_semantic_ids: set[str]
    expected: list[Any]


def compile_intent(
    root: pathlib.Path,
    *,
    module: str,
    surface: str = "sync",
    intent_path: pathlib.Path | None = None,
) -> IntentCompileResult:
    """
    Compila `.intent.yaml` -> `contracts/openapi/paths/<module>.yaml` (virtual) e
    roda o policy compiler em memória (fail-closed). Não escreve nada em disco.
    """
    ipath = intent_path or _intent_path(root, module)
    if not ipath.is_absolute():
        ipath = (root / ipath).resolve()
    if not ipath.exists():
        raise PolicyCompilerError(
            status="FAIL_ACTIONABLE",
            blocking_code="BLOCKED_MISSING_INTENT",
            summary=f"Intent não encontrada para módulo `{module}`: {ipath}",
            violations=[
                CompilerViolation(
                    gate_id="GATE-001-intent_presence",
                    rule_id="HB-INTENT-001",
                    code="BLOCKED_MISSING_INTENT",
                    severity="error",
                    artifact=_rel(root, ipath),
                    json_path="$",
                    location=None,
                    message="Arquivo .intent.yaml é obrigatório para o fluxo de intenção.",
                    ssot_refs=[{"path": "docs/hbtrack/planos/HB_TRACK_API_EXECUTION_CONTRACT.md", "pointer": "$.intent_flow"}],
                    hint="Crie `contracts/openapi/intents/<module>.intent.yaml`.",
                )
            ],
        )

    intent_rel = _rel(root, ipath)
    doc = _load_yaml_with_marks(ipath)
    data = doc.data
    marks = doc.marks

    root_key = "hbtrack_api_intent"
    base_jp = f"$.{root_key}"
    if not isinstance(data, dict) or root_key not in data or not isinstance(data.get(root_key), dict):
        raise PolicyCompilerError(
            status="FAIL_ACTIONABLE",
            blocking_code="FAIL_INTENT_SCHEMA",
            summary="Intent inválida: esperado mapping com raiz `hbtrack_api_intent`.",
            violations=[
                CompilerViolation(
                    gate_id="GATE-001-intent_schema",
                    rule_id="HB-INTENT-002",
                    code="FAIL_INTENT_SCHEMA",
                    severity="error",
                    artifact=intent_rel,
                    json_path="$",
                    location=_nearest_location(marks, "$"),
                    message="Documento YAML deve conter `hbtrack_api_intent: {...}`.",
                    ssot_refs=[{"path": "docs/hbtrack/planos/HB_TRACK_API_EXECUTION_CONTRACT.md", "pointer": "$.intent_schema"}],
                    hint="Crie a raiz `hbtrack_api_intent` e mova os campos para dentro dela.",
                )
            ],
        )

    intent = data[root_key]

    violations: list[CompilerViolation] = []

    mod_jp = _json_path_for_key(base_jp, "module")
    mod = intent.get("module")
    if mod != module:
        violations.append(
            CompilerViolation(
                gate_id="GATE-001-intent_schema",
                rule_id="HB-INTENT-003",
                code="FAIL_INTENT_MODULE_MISMATCH",
                severity="error",
                artifact=intent_rel,
                json_path=mod_jp,
                location=_nearest_location(marks, mod_jp),
                message=f"Campo module deve ser {module!r} (encontrado {mod!r}).",
                ssot_refs=[{"path": intent_rel, "pointer": mod_jp}],
                hint="Alinhe `hbtrack_api_intent.module` com o nome do arquivo/módulo.",
            )
        )

    # semantic types (locals)
    extra_semantic_ids: set[str] = set()
    locals_jp = _json_path_for_key(base_jp, "local_semantic_types")
    local_types = intent.get("local_semantic_types") or []
    if local_types and not isinstance(local_types, list):
        violations.append(
            CompilerViolation(
                gate_id="GATE-002-local_semantic_types",
                rule_id="HB-INTENT-010",
                code="FAIL_INTENT_LOCAL_TYPES_SCHEMA",
                severity="error",
                artifact=intent_rel,
                json_path=locals_jp,
                location=_nearest_location(marks, locals_jp),
                message="local_semantic_types deve ser uma lista.",
                ssot_refs=[{"path": intent_rel, "pointer": locals_jp}],
            )
        )
        local_types = []

    global_sem = _global_semantic_ids(root)
    for i, lt in enumerate(local_types):
        item_jp = _json_path_for_index(locals_jp, i)
        if not isinstance(lt, dict):
            violations.append(
                CompilerViolation(
                    gate_id="GATE-002-local_semantic_types",
                    rule_id="HB-INTENT-011",
                    code="FAIL_INTENT_LOCAL_TYPES_SCHEMA",
                    severity="error",
                    artifact=intent_rel,
                    json_path=item_jp,
                    location=_nearest_location(marks, item_jp),
                    message="Cada item de local_semantic_types deve ser um mapping.",
                    ssot_refs=[{"path": intent_rel, "pointer": item_jp}],
                )
            )
            continue
        sid_jp = _json_path_for_key(item_jp, "semantic_id")
        sid = lt.get("semantic_id")
        if not isinstance(sid, str) or not sid:
            violations.append(
                CompilerViolation(
                    gate_id="GATE-002-local_semantic_types",
                    rule_id="HB-INTENT-012",
                    code="FAIL_INTENT_LOCAL_TYPES_SCHEMA",
                    severity="error",
                    artifact=intent_rel,
                    json_path=sid_jp,
                    location=_nearest_location(marks, sid_jp),
                    message="local_semantic_types[].semantic_id é obrigatório.",
                    ssot_refs=[{"path": intent_rel, "pointer": sid_jp}],
                )
            )
            continue
        if sid in global_sem:
            violations.append(
                CompilerViolation(
                    gate_id="GATE-002-local_semantic_types",
                    rule_id="HB-INTENT-020",
                    code="FAIL_INTENT_LOCAL_SEMANTIC_ID_COLLISION",
                    severity="error",
                    artifact=intent_rel,
                    json_path=sid_jp,
                    location=_nearest_location(marks, sid_jp),
                    message=f"semantic_id local {sid!r} já existe no CANONICAL_TYPE_REGISTRY (proibido redeclarar).",
                    ssot_refs=[
                        {"path": _rel(root, _canonical_type_registry_path(root)), "pointer": "$.derived_types"},
                        {"path": intent_rel, "pointer": sid_jp},
                    ],
                    hint="Remova este tipo local ou use o semantic_id global existente.",
                )
            )
            continue
        extra_semantic_ids.add(sid)

    # endpoints
    endpoints_jp = _json_path_for_key(base_jp, "endpoints")
    endpoints_raw = intent.get("endpoints") or []
    endpoints: list[dict[str, Any]] = []
    if endpoints_raw and not isinstance(endpoints_raw, list):
        violations.append(
            CompilerViolation(
                gate_id="GATE-003-endpoints",
                rule_id="HB-INTENT-030",
                code="FAIL_INTENT_ENDPOINTS_SCHEMA",
                severity="error",
                artifact=intent_rel,
                json_path=endpoints_jp,
                location=_nearest_location(marks, endpoints_jp),
                message="endpoints deve ser uma lista.",
                ssot_refs=[{"path": intent_rel, "pointer": endpoints_jp}],
            )
        )
        endpoints_raw = []

    allowed_methods = {"get", "post", "put", "patch", "delete", "options", "head", "trace"}
    for i, ep in enumerate(endpoints_raw):
        item_jp = _json_path_for_index(endpoints_jp, i)
        if not isinstance(ep, dict):
            violations.append(
                CompilerViolation(
                    gate_id="GATE-003-endpoints",
                    rule_id="HB-INTENT-031",
                    code="FAIL_INTENT_ENDPOINTS_SCHEMA",
                    severity="error",
                    artifact=intent_rel,
                    json_path=item_jp,
                    location=_nearest_location(marks, item_jp),
                    message="Cada endpoint deve ser um mapping.",
                    ssot_refs=[{"path": intent_rel, "pointer": item_jp}],
                )
            )
            continue
        p = ep.get("path")
        m = ep.get("method")
        opid = ep.get("operationId")
        if not isinstance(p, str) or not p.startswith("/"):
            violations.append(
                CompilerViolation(
                    gate_id="GATE-003-endpoints",
                    rule_id="HB-INTENT-032",
                    code="FAIL_INTENT_ENDPOINTS_SCHEMA",
                    severity="error",
                    artifact=intent_rel,
                    json_path=_json_path_for_key(item_jp, "path"),
                    location=_nearest_location(marks, _json_path_for_key(item_jp, "path")),
                    message="endpoint.path deve começar com '/'.",
                    ssot_refs=[{"path": intent_rel, "pointer": item_jp}],
                )
            )
            continue
        if not isinstance(m, str) or m.lower() not in allowed_methods:
            violations.append(
                CompilerViolation(
                    gate_id="GATE-003-endpoints",
                    rule_id="HB-INTENT-033",
                    code="FAIL_INTENT_ENDPOINTS_SCHEMA",
                    severity="error",
                    artifact=intent_rel,
                    json_path=_json_path_for_key(item_jp, "method"),
                    location=_nearest_location(marks, _json_path_for_key(item_jp, "method")),
                    message=f"endpoint.method inválido: {m!r}.",
                    ssot_refs=[{"path": intent_rel, "pointer": item_jp}],
                )
            )
            continue
        if not isinstance(opid, str) or not opid:
            violations.append(
                CompilerViolation(
                    gate_id="GATE-003-endpoints",
                    rule_id="HB-INTENT-034",
                    code="FAIL_INTENT_ENDPOINTS_SCHEMA",
                    severity="error",
                    artifact=intent_rel,
                    json_path=_json_path_for_key(item_jp, "operationId"),
                    location=_nearest_location(marks, _json_path_for_key(item_jp, "operationId")),
                    message="endpoint.operationId é obrigatório.",
                    ssot_refs=[{"path": intent_rel, "pointer": item_jp}],
                )
            )
            continue
        endpoints.append({"path": p, "method": m.lower(), "operationId": opid, **ep})

    if violations:
        raise PolicyCompilerError(
            status="FAIL_ACTIONABLE",
            blocking_code="FAIL_INTENT_VALIDATION",
            summary="Intent inválida (falhas de schema/semântica) — geração vetada.",
            violations=violations[:50],
            actions=[
                f"Corrigir `{intent_rel}` e reexecutar o intent compiler.",
            ],
            details={"intent": {"path": intent_rel}},
        )

    # Render openapi/paths/<module>.yaml as bytes (virtual)
    openapi_rel = f"contracts/openapi/paths/{module}.yaml"
    openapi_bytes = _render_openapi_paths_yaml(module=module, intent_relpath=intent_rel, endpoints=endpoints)

    # Run the policy compiler fail-closed against virtual source bytes.
    try:
        expected = compile_expected(
            root,
            module=module,
            surface=surface,
            source_overrides={openapi_rel: openapi_bytes},
            extra_semantic_ids=extra_semantic_ids,
        )
    except PolicyCompilerError as e:
        # Re-map to intent context when possible (agent can edit the intent, not the rendered OpenAPI).
        if e.blocking_code == "FAIL_COMPATIBILITY_SAT":
            raise PolicyCompilerError(
                status=e.status,
                blocking_code=e.blocking_code,
                summary=e.summary,
                violations=[
                    CompilerViolation(
                        gate_id=v.gate_id,
                        rule_id=v.rule_id,
                        code=v.code,
                        severity=v.severity,
                        artifact=intent_rel,
                        json_path=base_jp,
                        location=_nearest_location(marks, base_jp),
                        message=v.message,
                        ssot_refs=v.ssot_refs,
                        hint="Ajuste o intent/profile para satisfazer a matriz (ver details.compatibility.unsat_core).",
                    )
                    for v in (e.violations or [])
                ],
                actions=[f"Corrigir `{intent_rel}` (ou perfis/matriz) e reexecutar."],
                details=e.details,
            ) from e
        raise

    # Validate that the rendered YAML is parseable (defensive).
    _load_yaml_bytes(openapi_bytes, context=openapi_rel)

    return IntentCompileResult(
        module=module,
        intent_relpath=intent_rel,
        openapi_paths_relpath=openapi_rel,
        openapi_paths_bytes=openapi_bytes,
        extra_semantic_ids=extra_semantic_ids,
        expected=expected,
    )
