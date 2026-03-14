from __future__ import annotations

import dataclasses
import hashlib
import pathlib
import re
import json
from typing import Any


@dataclasses.dataclass(frozen=True)
class CompilerViolation:
    gate_id: str
    rule_id: str
    code: str
    severity: str
    artifact: str
    json_path: str
    message: str
    ssot_refs: list[dict[str, str]]
    location: dict[str, int] | None = None  # {"line": 1-based, "column": 1-based}
    hint: str | None = None

    def to_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {
            "gate_id": self.gate_id,
            "rule_id": self.rule_id,
            "code": self.code,
            "severity": self.severity,
            "artifact": self.artifact,
            "json_path": self.json_path,
            "location": self.location,
            "message": self.message,
            "ssot_refs": self.ssot_refs,
        }
        if self.hint:
            out["hint"] = self.hint
        return out


class PolicyCompilerError(RuntimeError):
    def __init__(
        self,
        *args: object,
        status: str | None = None,
        blocking_code: str | None = None,
        summary: str | None = None,
        violations: list[CompilerViolation] | None = None,
        actions: list[str] | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        # Compat: permite raise PolicyCompilerError("mensagem") em chamadas legadas.
        if summary is None and args:
            summary = str(args[0])
        if summary is None:
            summary = "Erro no compiler de policy."
        if status is None:
            status = "FAIL_CLOSED"
        if blocking_code is None:
            blocking_code = "FAIL_INTERNAL"

        super().__init__(summary)
        self.status = status  # FAIL_ACTIONABLE | BLOCKED_INPUT | FAIL_CLOSED
        self.blocking_code = blocking_code
        self.summary = summary
        self.violations = violations or []
        self.actions = actions or []
        self.details = details or {}

    def to_report(self) -> dict[str, Any]:
        return {
            "artifact_id": "HBTRACK_API_POLICY_COMPILER_ERROR",
            "status": self.status,
            "blocking_code": self.blocking_code,
            "summary": self.summary,
            "violations": [v.to_dict() for v in self.violations],
            "actions": self.actions,
            "details": self.details,
        }


@dataclasses.dataclass(frozen=True)
class ExpectedFile:
    relpath: str
    content: bytes


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _read_bytes(path: pathlib.Path) -> bytes:
    try:
        return path.read_bytes()
    except FileNotFoundError as e:
        raise PolicyCompilerError(f"Arquivo não encontrado: {path}") from e


def _load_yaml(path: pathlib.Path) -> Any:
    try:
        import yaml  # type: ignore
    except ImportError as e:  # pragma: no cover
        raise PolicyCompilerError("PyYAML não instalado (necessário para compiler de policy).") from e
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as e:
        raise PolicyCompilerError(f"YAML inválido: {path}: {e}") from e


def _load_yaml_bytes(data: bytes, *, context: str) -> Any:
    try:
        import yaml  # type: ignore
    except ImportError as e:  # pragma: no cover
        raise PolicyCompilerError("PyYAML não instalado (necessário para compiler de policy).") from e
    try:
        return yaml.safe_load(data.decode("utf-8"))
    except Exception as e:
        raise PolicyCompilerError(f"YAML inválido ({context}): {e}") from e


def _dump_yaml(obj: Any) -> bytes:
    try:
        import yaml  # type: ignore
    except ImportError as e:  # pragma: no cover
        raise PolicyCompilerError("PyYAML não instalado (necessário para compiler de policy).") from e
    text = yaml.safe_dump(
        obj,
        sort_keys=True,
        allow_unicode=True,
        width=120,
        default_flow_style=False,
    )
    if not text.endswith("\n"):
        text += "\n"
    return text.encode("utf-8")


def _rel(root: pathlib.Path, path: pathlib.Path) -> str:
    return path.relative_to(root).as_posix()


def _ssot_api_rules_path(root: pathlib.Path) -> pathlib.Path:
    p = root / ".contract_driven" / "templates" / "api" / "api_rules.yaml"
    if p.exists():
        return p
    raise PolicyCompilerError("SSOT de api_rules.yaml não encontrada (esperado: .contract_driven/templates/api/api_rules.yaml).")


def _architecture_matrix_path(root: pathlib.Path) -> pathlib.Path:
    return root / ".contract_driven" / "templates" / "api" / "ARCHITECTURE_MATRIX.yaml"


def _module_profile_registry_path(root: pathlib.Path) -> pathlib.Path:
    return root / ".contract_driven" / "templates" / "api" / "MODULE_PROFILE_REGISTRY.yaml"


def _canonical_type_registry_path(root: pathlib.Path) -> pathlib.Path:
    return root / ".contract_driven" / "templates" / "api" / "CANONICAL_TYPE_REGISTRY.yaml"


def _load_architecture_matrix(root: pathlib.Path) -> dict:
    path = _architecture_matrix_path(root)
    data = _load_yaml(path)
    if not isinstance(data, dict) or "modules" not in data or not isinstance(data.get("modules"), dict):
        raise PolicyCompilerError(f"ARCHITECTURE_MATRIX inválido: esperado mapping com 'modules': {path}")
    return data


def _load_module_profiles(root: pathlib.Path) -> dict:
    path = _module_profile_registry_path(root)
    data = _load_yaml(path)
    if not isinstance(data, dict) or "modules" not in data or not isinstance(data.get("modules"), dict):
        raise PolicyCompilerError(f"MODULE_PROFILE_REGISTRY inválido: esperado mapping com 'modules': {path}")
    return data


def _load_api_rules(root: pathlib.Path) -> dict:
    path = _ssot_api_rules_path(root)
    data = _load_yaml(path)
    if not isinstance(data, dict) or "hbtrack_api_rules" not in data:
        raise PolicyCompilerError(f"api_rules inválido: esperado raiz 'hbtrack_api_rules': {path}")
    return data["hbtrack_api_rules"]


def _load_canonical_types(root: pathlib.Path) -> dict:
    path = _canonical_type_registry_path(root)
    data = _load_yaml(path)
    if not isinstance(data, dict) or "base_types" not in data or "derived_types" not in data:
        raise PolicyCompilerError(f"CANONICAL_TYPE_REGISTRY inválido: esperado 'base_types' e 'derived_types': {path}")
    return data


def _load_domain_axioms_formats(root: pathlib.Path) -> dict[str, str]:
    path = root / ".contract_driven" / "DOMAIN_AXIOMS.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    fmts = (data.get("domain_axioms") or {}).get("global_formats") or {}
    out: dict[str, str] = {}
    for k, v in fmts.items():
        if isinstance(v, dict) and isinstance(v.get("pattern"), str) and v.get("pattern"):
            out[k] = v["pattern"]
    return out


def _iter_schema_properties(node: Any, *, base_path: str = "$") -> list[tuple[str, dict, str]]:
    """
    Extrai propriedades de nós do tipo JSON Schema/OpenAPI schema:
    qualquer mapping com `properties: { ... }`.
    """
    found: list[tuple[str, dict, str]] = []
    if isinstance(node, dict):
        props = node.get("properties")
        if isinstance(props, dict):
            for k, v in props.items():
                if isinstance(v, dict):
                    found.append((str(k), v, f"{base_path}.properties.{k}"))
        for k, v in node.items():
            found.extend(_iter_schema_properties(v, base_path=f"{base_path}.{k}"))
    elif isinstance(node, list):
        for i, v in enumerate(node):
            found.extend(_iter_schema_properties(v, base_path=f"{base_path}[{i}]"))
    return found


def _validate_style_veto_and_semantics(
    *,
    artifact_relpath: str,
    doc: Any,
    api_rules: dict,
    canonical_types: dict,
    domain_formats: dict[str, str],
    extra_semantic_ids: set[str] | None = None,
) -> None:
    """
    Enforcements (fail-closed):
    - json_fields em camelCase (style_veto mínimo)
    - uuid-v4 fields: proibir sufixo `Uuid` e exigir sufixo `Id`
    - field_bindings: exigir `x-semantic-id` e validar contra registry
    """
    naming = (api_rules.get("canonical_conventions") or {}).get("naming") or {}
    json_style = ((naming.get("json_fields") or {}) if isinstance(naming.get("json_fields"), dict) else {}).get("style")
    enforce_camel = (json_style == "camelCase")

    camel_re = re.compile(r"^[a-z][A-Za-z0-9]*$")
    uuid_v4_pat = domain_formats.get("uuid_v4")
    uuid_v4_pat_norm = uuid_v4_pat.strip() if isinstance(uuid_v4_pat, str) else None

    derived = canonical_types.get("derived_types") or {}
    semantic_ids: set[str] = set()
    if isinstance(derived, dict):
        for _, spec in derived.items():
            if isinstance(spec, dict) and isinstance(spec.get("semantic_id"), str):
                semantic_ids.add(spec["semantic_id"])
    if extra_semantic_ids:
        semantic_ids.update(extra_semantic_ids)

    bindings = canonical_types.get("field_bindings") or []
    binding_map: dict[str, str] = {}
    if isinstance(bindings, list):
        for b in bindings:
            if isinstance(b, dict) and isinstance(b.get("field_name"), str) and isinstance(b.get("canonical_type_ref"), str):
                binding_map[b["field_name"]] = b["canonical_type_ref"]

    violations: list[str] = []
    structured: list[CompilerViolation] = []
    for prop_name, prop_schema, prop_path in _iter_schema_properties(doc):
        if enforce_camel and not camel_re.match(prop_name):
            structured.append(
                CompilerViolation(
                    gate_id="GATE-005-style_veto_enforcement",
                    rule_id="HB-STYLE-VETO-001",
                    code="BLOCKED_STYLE_VETO_FIELD_CASING",
                    severity="error",
                    artifact=artifact_relpath,
                    json_path=prop_path,
                    message=f"Field não é camelCase: {prop_name!r}.",
                    ssot_refs=[
                        {"path": ".contract_driven/templates/api/api_rules.yaml", "pointer": "$.hbtrack_api_rules.canonical_conventions.naming.json_fields.style"},
                        {"path": ".contract_driven/DOMAIN_AXIOMS.json", "pointer": "$.domain_axioms.normalization_policy"},
                    ],
                    hint="Renomeie o campo para camelCase (ex.: trainingSessionId).",
                )
            )

        # semantic binding enforcement
        if prop_name in binding_map:
            expected = binding_map[prop_name]
            got = prop_schema.get("x-semantic-id")
            if got != expected:
                structured.append(
                    CompilerViolation(
                        gate_id="GATE-006-semantic_binding",
                        rule_id="HB-SEMANTIC-BIND-001",
                        code="BLOCKED_MISSING_OR_WRONG_SEMANTIC_ID",
                        severity="error",
                        artifact=artifact_relpath,
                        json_path=prop_path,
                        message=f"x-semantic-id obrigatório: esperado {expected!r}, encontrado {got!r}.",
                        ssot_refs=[
                            {"path": ".contract_driven/templates/api/CANONICAL_TYPE_REGISTRY.yaml", "pointer": "$.field_bindings"},
                        ],
                        hint=f"Adicione `x-semantic-id: {expected}` no schema do campo.",
                    )
                )
            if expected not in semantic_ids:
                structured.append(
                    CompilerViolation(
                        gate_id="GATE-006-semantic_binding",
                        rule_id="HB-SEMANTIC-BIND-002",
                        code="BLOCKED_UNKNOWN_SEMANTIC_ID",
                        severity="error",
                        artifact=artifact_relpath,
                        json_path=prop_path,
                        message=f"semantic_id {expected!r} não existe no CANONICAL_TYPE_REGISTRY.",
                        ssot_refs=[
                            {"path": ".contract_driven/templates/api/CANONICAL_TYPE_REGISTRY.yaml", "pointer": "$.derived_types"},
                        ],
                        hint="Promova este semantic_id para o registry (global) ou declare como tipo local no manifesto de intenção (quando aplicável).",
                    )
                )
        if "x-semantic-id" in prop_schema:
            got = prop_schema.get("x-semantic-id")
            if isinstance(got, str) and got and got not in semantic_ids:
                structured.append(
                    CompilerViolation(
                        gate_id="GATE-006-semantic_binding",
                        rule_id="HB-SEMANTIC-BIND-002",
                        code="BLOCKED_UNKNOWN_SEMANTIC_ID",
                        severity="error",
                        artifact=artifact_relpath,
                        json_path=prop_path,
                        message=f"x-semantic-id {got!r} não existe no CANONICAL_TYPE_REGISTRY.",
                        ssot_refs=[
                            {"path": ".contract_driven/templates/api/CANONICAL_TYPE_REGISTRY.yaml", "pointer": "$.derived_types"},
                        ],
                        hint="Use um semantic_id existente ou registre um novo tipo semântico.",
                    )
                )

        # uuid naming enforcement
        schema_type = prop_schema.get("type")
        schema_format = prop_schema.get("format")
        schema_pattern = prop_schema.get("pattern")
        schema_pattern_norm = None
        if isinstance(schema_pattern, str):
            schema_pattern_norm = schema_pattern.strip()

        is_uuid_v4 = (
            schema_type == "string"
            and (
                schema_format == "uuid"
                or (uuid_v4_pat_norm is not None and schema_pattern_norm == uuid_v4_pat_norm)
            )
        )
        if is_uuid_v4:
            if prop_name.lower().endswith("uuid"):
                structured.append(
                    CompilerViolation(
                        gate_id="GATE-005-style_veto_enforcement",
                        rule_id="HB-STYLE-VETO-002",
                        code="BLOCKED_STYLE_VETO_UUID_SUFFIX",
                        severity="error",
                        artifact=artifact_relpath,
                        json_path=prop_path,
                        message="Sufixo proibido `Uuid` para UUID v4 (use `...Id`).",
                        ssot_refs=[
                            {"path": ".contract_driven/templates/api/api_rules.yaml", "pointer": "$.hbtrack_api_rules.canonical_conventions.identifiers"},
                            {"path": ".contract_driven/DOMAIN_AXIOMS.json", "pointer": "$.domain_axioms.global_formats.uuid_v4"},
                        ],
                        hint="Renomeie para `...Id` (ex.: userId, athleteId).",
                    )
                )
            if not prop_name.endswith("Id"):
                structured.append(
                    CompilerViolation(
                        gate_id="GATE-005-style_veto_enforcement",
                        rule_id="HB-STYLE-VETO-003",
                        code="BLOCKED_STYLE_VETO_ID_SUFFIX_REQUIRED",
                        severity="error",
                        artifact=artifact_relpath,
                        json_path=prop_path,
                        message="UUID v4 deve terminar com sufixo canônico `Id` (ex.: athleteId).",
                        ssot_refs=[
                            {"path": ".contract_driven/templates/api/api_rules.yaml", "pointer": "$.hbtrack_api_rules.canonical_conventions.identifiers"},
                        ],
                        hint="Use o sufixo `Id` para identificadores públicos (uuid v4).",
                    )
                )

    if structured:
        raise PolicyCompilerError(
            status="FAIL_ACTIONABLE",
            blocking_code="FAIL_COMPILER_ENFORCEMENT",
            summary="Violação de style veto / semantic binding — compiler recusou-se a assinar manifesto/hash.",
            violations=structured[:50],
            actions=[
                "Corrigir o contrato fonte (ou o manifesto de intenção, quando aplicável).",
                "Reexecutar: python3 scripts/contracts/validate/api/compile_api_policy.py --all",
            ],
            details={
                "artifact": artifact_relpath,
                "enforcement": "pre-signature (fail-closed before manifest/hash)",
            },
        )


def _validate_matrix_vs_profile(matrix: dict, profiles: dict) -> None:
    mmods = matrix.get("modules", {})
    pmods = profiles.get("modules", {})
    for module, prof in pmods.items():
        if module not in mmods:
            raise PolicyCompilerError(f"Módulo `{module}` não existe na ARCHITECTURE_MATRIX.")
        mm = mmods[module]
        allowed_classes = set(mm.get("allowed_module_classes") or [])
        allowed_surfaces = set(mm.get("allowed_surfaces") or [])
        module_class = prof.get("module_class")
        if module_class not in allowed_classes:
            raise PolicyCompilerError(
                f"PROFILE `{module}` declara module_class `{module_class}` fora do permitido: {sorted(allowed_classes)}"
            )
        for surf in prof.get("enabled_surfaces") or []:
            if surf not in allowed_surfaces:
                raise PolicyCompilerError(
                    f"PROFILE `{module}` habilita surface `{surf}` fora do permitido: {sorted(allowed_surfaces)}"
                )


def _cond_ok(ctx: dict[str, Any], cond: dict[str, Any]) -> bool:
    var = cond.get("var")
    if not isinstance(var, str) or not var:
        return False
    if "equals" in cond:
        return ctx.get(var) == cond.get("equals")
    if "in" in cond:
        vals = cond.get("in")
        if not isinstance(vals, list):
            return False
        return ctx.get(var) in vals
    if "contains" in cond:
        v = ctx.get(var)
        if not isinstance(v, list):
            return False
        return cond.get("contains") in v
    return False


def _conds_all(ctx: dict[str, Any], conds: Any) -> bool:
    if not isinstance(conds, list):
        return False
    return all(isinstance(c, dict) and _cond_ok(ctx, c) for c in conds)


def _validate_compatibility_matrix(*, api_rules: dict, ctx: dict[str, Any]) -> None:
    """
    GATE-004 — Cross-set compatibility sat (determinístico).

    Para evitar explosão combinatória, cada entrada deve declarar `rules_involved`.
    """
    matrix = api_rules.get("compatibility_matrix") or []
    if not matrix:
        return
    if not isinstance(matrix, list):
        raise PolicyCompilerError(
            status="BLOCKED_INPUT",
            blocking_code="BLOCKED_INVALID_COMPATIBILITY_MATRIX",
            summary="compatibility_matrix inválida (esperado lista).",
            violations=[
                CompilerViolation(
                    gate_id="GATE-004-cross_set_compatibility_sat",
                    rule_id="HB-COMPAT-MATRIX-STRUCT",
                    code="BLOCKED_INVALID_COMPATIBILITY_MATRIX",
                    severity="error",
                    artifact=".contract_driven/templates/api/api_rules.yaml",
                    json_path="$.hbtrack_api_rules.compatibility_matrix",
                    message="compatibility_matrix deve ser lista.",
                    ssot_refs=[{"path": ".contract_driven/templates/api/api_rules.yaml", "pointer": "$.hbtrack_api_rules.compatibility_matrix"}],
                )
            ],
        )

    conflicts: list[dict[str, Any]] = []
    unsat: set[str] = set()

    for entry in matrix:
        if not isinstance(entry, dict):
            continue
        cid = entry.get("id")
        set_a = entry.get("set_a")
        set_b = entry.get("set_b")
        rules_involved = entry.get("rules_involved") or []
        rule = entry.get("rule") or {}

        if not isinstance(cid, str) or not cid:
            continue
        if not isinstance(set_a, str) or not isinstance(set_b, str):
            continue
        if not isinstance(rules_involved, list) or not all(isinstance(r, str) and r for r in rules_involved):
            continue
        if not isinstance(rule, dict):
            continue

        # Optional `when` gate
        when = entry.get("when")
        if when is not None:
            if isinstance(when, dict) and "all" in when:
                if not _conds_all(ctx, when.get("all")):
                    continue
            else:
                continue

        ok = True
        if "if" in rule and isinstance(rule.get("if"), dict) and isinstance(rule.get("then"), dict):
            iff = rule["if"]
            then = rule["then"]
            if isinstance(iff, dict) and "all" in iff and _conds_all(ctx, iff.get("all")):
                req = then.get("require")
                if req is not None and not _conds_all(ctx, req):
                    ok = False
        else:
            # rule sem if/then: não suportado (fail-closed de input)
            raise PolicyCompilerError(
                status="BLOCKED_INPUT",
                blocking_code="BLOCKED_INVALID_COMPATIBILITY_RULE",
                summary=f"compatibility_matrix.{cid} inválida (esperado rule.if + rule.then).",
                violations=[
                    CompilerViolation(
                        gate_id="GATE-004-cross_set_compatibility_sat",
                        rule_id=cid,
                        code="BLOCKED_INVALID_COMPATIBILITY_RULE",
                        severity="error",
                        artifact=".contract_driven/templates/api/api_rules.yaml",
                        json_path=f"$.hbtrack_api_rules.compatibility_matrix[{cid}]",
                        message="Rule deve declarar `if: {all:[...]}` e `then: {require:[...]}`.",
                        ssot_refs=[{"path": ".contract_driven/templates/api/api_rules.yaml", "pointer": "$.hbtrack_api_rules.compatibility_matrix"}],
                    )
                ],
            )

        if not ok:
            conflicts.append(
                {
                    "compatibility_id": cid,
                    "set_a": set_a,
                    "set_b": set_b,
                    "rules_involved": list(rules_involved),
                }
            )
            unsat.update(rules_involved)

    if not conflicts:
        return

    violations = [
        CompilerViolation(
            gate_id="GATE-004-cross_set_compatibility_sat",
            rule_id=c["compatibility_id"],
            code="FAIL_COMPATIBILITY_SAT",
            severity="error",
            artifact=".contract_driven/templates/api/api_rules.yaml",
            json_path="$.hbtrack_api_rules.compatibility_matrix",
            message=(
                f"Combinação insatisfatível entre sets {c['set_a']!r} e {c['set_b']!r} "
                f"(compatibility_id={c['compatibility_id']})."
            ),
            ssot_refs=[{"path": ".contract_driven/templates/api/api_rules.yaml", "pointer": "$.hbtrack_api_rules.compatibility_matrix"}],
            hint="Ajuste profile/overlays/política para satisfazer a matriz. Use details.compatibility.unsat_core.",
        )
        for c in conflicts
    ]

    raise PolicyCompilerError(
        status="FAIL_ACTIONABLE",
        blocking_code="FAIL_COMPATIBILITY_SAT",
        summary="Matriz de compatibilidade insatisfatível (GATE-004) — fail-closed.",
        violations=violations,
        actions=[
            "Corrigir o input (api_rules.yaml / ARCHITECTURE_MATRIX / MODULE_PROFILE_REGISTRY / intent).",
            "Reexecutar: python3 scripts/contracts/validate/api/compile_api_policy.py --all",
        ],
        details={
            "compatibility": {
                "unsat_core": sorted(unsat),
                "conflicts": conflicts,
            }
        },
    )


def _openapi_sync_sources(root: pathlib.Path, module: str, *, virtual_relpaths: set[str] | None = None) -> list[pathlib.Path]:
    path_file = root / "contracts" / "openapi" / "paths" / f"{module}.yaml"
    if not path_file.exists():
        rel = _rel(root, path_file)
        if virtual_relpaths and rel in virtual_relpaths:
            return [path_file]
        raise PolicyCompilerError(f"Contrato OpenAPI do módulo não encontrado: {path_file}")
    return [path_file]


def _asyncapi_event_sources(root: pathlib.Path, module: str) -> list[pathlib.Path]:
    base = root / "contracts" / "asyncapi"
    if not base.exists():
        raise PolicyCompilerError("contracts/asyncapi/ ausente (surface event não disponível).")
    candidates: list[pathlib.Path] = []
    for rel in (
        pathlib.Path("channels"),
        pathlib.Path("messages"),
        pathlib.Path("components") / "schemas",
        pathlib.Path("operations"),
    ):
        d = base / rel
        if not d.exists():
            continue
        candidates.extend(sorted(d.glob(f"{module}_*.yaml")))
        candidates.extend(sorted(d.glob(f"{module}_*.yml")))
    if not candidates:
        raise PolicyCompilerError(f"Nenhum artefato AsyncAPI encontrado para o módulo `{module}`.")
    # também amarrar no entrypoint
    root_file = base / "asyncapi.yaml"
    if root_file.exists():
        return [root_file] + candidates
    return candidates


def compile_expected(
    root: pathlib.Path,
    *,
    module: str,
    surface: str,
    source_overrides: dict[str, bytes] | None = None,
    extra_semantic_ids: set[str] | None = None,
) -> list[ExpectedFile]:
    """
    Compila policy resolvida + artefatos derivados + manifesto (tudo determinístico).

    - `surface=sync` => target=openapi (paths/<module>.yaml)
    - `surface=event` => target=asyncapi (subset por prefixo `<module>_*.yaml`)
    """
    overrides = source_overrides or {}

    matrix = _load_architecture_matrix(root)
    profiles = _load_module_profiles(root)
    _validate_matrix_vs_profile(matrix, profiles)

    pmods = profiles["modules"]
    if module not in pmods:
        raise PolicyCompilerError(f"Módulo `{module}` não existe no MODULE_PROFILE_REGISTRY.")
    prof = pmods[module]
    enabled = prof.get("enabled_surfaces") or []
    if surface not in enabled:
        raise PolicyCompilerError(f"Módulo `{module}` não habilita surface `{surface}` (enabled_surfaces={enabled}).")
    targets = prof.get("contract_targets") or {}
    target = targets.get(surface)
    if target not in ("openapi", "asyncapi"):
        raise PolicyCompilerError(f"contract_targets.{surface} inválido para `{module}`: {target!r}")

    api_rules = _load_api_rules(root)
    canon_types = _load_canonical_types(root)
    domain_formats = _load_domain_axioms_formats(root)

    mmods = matrix.get("modules") or {}
    arch_mod = mmods.get(module) if isinstance(mmods, dict) else None
    arch_sensitive = bool(arch_mod.get("sensitive")) if isinstance(arch_mod, dict) else False

    ctx = {
        "module": module,
        "surface": surface,
        "target": target,
        "module_class": prof.get("module_class"),
        "overlays": prof.get("overlays") or [],
        "sensitive_overlay_active": "sensitive_overlay" in (prof.get("overlays") or []),
        "arch_sensitive": arch_sensitive,
    }
    _validate_compatibility_matrix(api_rules=api_rules, ctx=ctx)

    if surface == "sync" and target == "openapi":
        source_contracts = _openapi_sync_sources(root, module, virtual_relpaths=set(overrides.keys()))
    elif surface == "event" and target == "asyncapi":
        source_contracts = _asyncapi_event_sources(root, module)
    else:
        raise PolicyCompilerError(f"Combinação surface/target não suportada: surface={surface} target={target}")

    # Enforce: compiler NÃO gera manifesto/hash para contrato que viola o style_veto/semantic bindings.
    for src in source_contracts:
        if src.suffix.lower() not in (".yaml", ".yml"):
            continue
        rel_src = _rel(root, src)
        if rel_src in overrides:
            doc = _load_yaml_bytes(overrides[rel_src], context=rel_src)
        else:
            doc = _load_yaml(src)
        _validate_style_veto_and_semantics(
            artifact_relpath=rel_src,
            doc=doc,
            api_rules=api_rules,
            canonical_types=canon_types,
            domain_formats=domain_formats,
            extra_semantic_ids=extra_semantic_ids,
        )

    policy_rel = f"generated/resolved_policy/{module}.{surface}.resolved.yaml"
    policy_obj = {
        "meta": {
            "artifact_id": "HBTRACK_RESOLVED_API_POLICY",
            "compiler": "hbtrack_api_policy_compiler",
            "compiler_version": "0.1.0",
            "module": module,
            "surface": surface,
            "target": target,
        },
        "inputs": {
            "architecture_matrix": ".contract_driven/templates/api/ARCHITECTURE_MATRIX.yaml",
            "module_profile_registry": ".contract_driven/templates/api/MODULE_PROFILE_REGISTRY.yaml",
            "api_rules": _rel(root, _ssot_api_rules_path(root)),
            "canonical_type_registry": ".contract_driven/templates/api/CANONICAL_TYPE_REGISTRY.yaml",
            "domain_axioms": ".contract_driven/DOMAIN_AXIOMS.json",
        },
        "module_profile": {
            "module_class": prof.get("module_class"),
            "enabled_surfaces": enabled,
            "overlays": prof.get("overlays") or [],
        },
        "style_veto": {
            "naming": (api_rules.get("canonical_conventions") or {}).get("naming") or {},
            "identifiers": (api_rules.get("canonical_conventions") or {}).get("identifiers") or {},
        },
        "canonical_types": {
            "base_types": canon_types.get("base_types") or {},
            "derived_types": canon_types.get("derived_types") or {},
            "field_bindings": canon_types.get("field_bindings") or [],
        },
        "contract_sources": [_rel(root, p) for p in source_contracts],
    }
    policy_bytes = _dump_yaml(policy_obj)

    derived: list[ExpectedFile] = [ExpectedFile(policy_rel, policy_bytes)]

    generated_contract_entries: list[dict[str, str]] = []
    source_contract_entries: list[dict[str, str]] = []

    if target == "openapi":
        # espelhar a árvore canônica sob generated/contracts/openapi/paths/
        src = source_contracts[0]
        rel_src = _rel(root, src)
        try:
            rel_under_contracts = src.relative_to(root / "contracts").as_posix()
        except Exception as e:  # pragma: no cover
            raise PolicyCompilerError(f"Falha ao relativizar contrato sob contracts/: {src}: {e}") from e
        dst_rel = f"generated/contracts/{rel_under_contracts}"
        if rel_src in overrides:
            src_bytes = overrides[rel_src]
        else:
            src_bytes = _read_bytes(src)
        derived.append(ExpectedFile(dst_rel, src_bytes))
        source_contract_entries.append({"path": rel_src, "sha256": _sha256_bytes(src_bytes)})
        generated_contract_entries.append({"path": dst_rel, "sha256": _sha256_bytes(src_bytes)})
    else:
        for src in source_contracts:
            rel_src = _rel(root, src)
            try:
                rel_under_contracts = src.relative_to(root / "contracts").as_posix()
            except Exception as e:  # pragma: no cover
                raise PolicyCompilerError(f"Falha ao relativizar contrato sob contracts/: {src}: {e}") from e
            dst_rel = f"generated/contracts/{rel_under_contracts}"
            if rel_src in overrides:
                src_bytes = overrides[rel_src]
            else:
                src_bytes = _read_bytes(src)
            derived.append(ExpectedFile(dst_rel, src_bytes))
            source_contract_entries.append({"path": rel_src, "sha256": _sha256_bytes(src_bytes)})
            generated_contract_entries.append({"path": dst_rel, "sha256": _sha256_bytes(src_bytes)})

    # hashes de inputs
    input_paths = [
        _architecture_matrix_path(root),
        _module_profile_registry_path(root),
        _ssot_api_rules_path(root),
        _canonical_type_registry_path(root),
        root / ".contract_driven" / "DOMAIN_AXIOMS.json",
    ]
    source_inputs = [{"path": _rel(root, p), "sha256": _sha256_bytes(_read_bytes(p))} for p in input_paths]

    def _tree_hash(entries: list[dict[str, str]]) -> str:
        h = hashlib.sha256()
        for e in sorted(entries, key=lambda x: x["path"]):
            h.update(e["path"].encode("utf-8"))
            h.update(b"\0")
            h.update(e["sha256"].encode("utf-8"))
            h.update(b"\n")
        return h.hexdigest()

    manifest_rel = f"generated/manifests/{module}.{surface}.traceability.yaml"
    manifest_obj = {
        "traceability_manifest": {
            "artifact_id": f"{module}.{surface}.{target}",
            "compiler": "hbtrack_api_policy_compiler",
            "compiler_version": "0.1.0",
            "policy_path": policy_rel,
            "policy_sha256": _sha256_bytes(policy_bytes),
            "source_inputs": source_inputs,
            "source_contracts": source_contract_entries,
            "generated_artifacts": generated_contract_entries,
            "source_tree_sha256": _tree_hash(source_contract_entries),
            "generated_tree_sha256": _tree_hash(generated_contract_entries),
        }
    }
    derived.append(ExpectedFile(manifest_rel, _dump_yaml(manifest_obj)))
    return derived


def write_expected(root: pathlib.Path, expected: list[ExpectedFile]) -> list[str]:
    written: list[str] = []
    for ef in expected:
        out = root / pathlib.Path(ef.relpath)
        out.parent.mkdir(parents=True, exist_ok=True)
        if out.exists() and out.read_bytes() == ef.content:
            continue
        out.write_bytes(ef.content)
        written.append(ef.relpath)
    return written


@dataclasses.dataclass(frozen=True)
class Drift:
    relpath: str
    reason: str


def check_expected(root: pathlib.Path, expected: list[ExpectedFile]) -> list[Drift]:
    drifts: list[Drift] = []
    for ef in expected:
        p = root / pathlib.Path(ef.relpath)
        if not p.exists():
            drifts.append(Drift(ef.relpath, "missing"))
            continue
        try:
            got = p.read_bytes()
        except Exception as e:  # pragma: no cover
            drifts.append(Drift(ef.relpath, f"unreadable: {e}"))
            continue

        def _semantic_equal(relpath: str, a: bytes, b: bytes) -> bool:
            suf = pathlib.Path(relpath).suffix.lower()
            if suf in (".yaml", ".yml"):
                try:
                    import yaml  # type: ignore
                    ao = yaml.safe_load(a.decode("utf-8"))
                    bo = yaml.safe_load(b.decode("utf-8"))
                    return ao == bo
                except Exception:
                    return a == b
            if suf == ".json":
                try:
                    return json.loads(a.decode("utf-8")) == json.loads(b.decode("utf-8"))
                except Exception:
                    return a == b
            return a == b

        if not _semantic_equal(ef.relpath, got, ef.content):
            drifts.append(Drift(ef.relpath, "semantic_mismatch"))
    return drifts


def compile_all_expected(root: pathlib.Path, *, only_modules: list[str] | None = None) -> list[ExpectedFile]:
    profiles = _load_module_profiles(root)
    pmods: dict[str, Any] = profiles["modules"]
    modules = sorted(pmods.keys())
    if only_modules is not None:
        missing = [m for m in only_modules if m not in pmods]
        if missing:
            raise PolicyCompilerError(f"Módulos não encontrados no registry: {missing}")
        modules = only_modules
    all_expected: list[ExpectedFile] = []
    for module in modules:
        enabled = pmods[module].get("enabled_surfaces") or []
        for surface in enabled:
            all_expected.extend(compile_expected(root, module=module, surface=surface))
    return all_expected
