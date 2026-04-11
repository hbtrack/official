from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.compile.compile_source_graph import (
    check_expected as check_source_graph_expected,
    compile_expected as compile_source_graph_expected,
    SourceGraphCompilerError,
)


COMPILER_NAME = "hbtrack_context_bundle_compiler"
COMPILER_VERSION = "0.1.0"


@dataclass(frozen=True)
class ExpectedFile:
    relpath: str
    content: str


@dataclass(frozen=True)
class Drift:
    relpath: str
    reason: str


class ContextBundleCompilerError(RuntimeError):
    def __init__(self, summary: str):
        super().__init__(summary)
        self.summary = summary


def _repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / ".git").exists():
            return parent
        if (parent / "docs").exists() and (parent / ".contract_driven").exists():
            return parent
    return here.parents[2]


def _discover_source_graph_modules(root: Path) -> list[str]:
    base = root / "docs" / "hbtrack" / "modulos"
    if not base.exists():
        return []
    modules: list[str] = []
    for manifest in sorted(base.glob("*/graph/module_manifest.yaml")):
        modules.append(manifest.parent.parent.name)
    return modules


def _rel(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_text(text: str) -> str:
    return _sha256_bytes(text.encode("utf-8"))


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise ContextBundleCompilerError(f"Arquivo YAML ausente: {path}")
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(payload, dict):
        raise ContextBundleCompilerError(f"YAML inválido (esperado objeto): {path}")
    return payload


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise ContextBundleCompilerError(f"Arquivo JSON ausente: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ContextBundleCompilerError(f"JSON inválido (esperado objeto): {path}")
    return payload


def _dump_json(data: dict[str, Any]) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def _feature_registry(root: Path) -> dict[str, Any]:
    return _load_yaml(root / "docs" / "_canon" / "FEATURE_REGISTRY.yaml")


def _module_registry(root: Path) -> dict[str, Any]:
    return _load_yaml(root / "docs" / "_canon" / "MODULE_REGISTRY.yaml")


def _source_authority_graph(root: Path) -> dict[str, Any]:
    return _load_yaml(root / "docs" / "_canon" / "SOURCE_AUTHORITY_GRAPH.yaml")


def _sync_manifest(root: Path) -> dict[str, Any]:
    return _load_yaml(root / "docs" / "_canon" / "SYNC_MANIFEST.yaml")


def _source_graph_dir(root: Path, module: str) -> Path:
    return root / "generated" / "source_graph" / module


def _source_graph_paths(root: Path, module: str) -> dict[str, Path]:
    source_graph_dir = _source_graph_dir(root, module)
    return {
        "bundle": source_graph_dir / f"{module}.bundle.yaml",
        "schema_view": source_graph_dir / f"{module}.schema_contract_view.yaml",
        "openapi_view": source_graph_dir / f"{module}.openapi_contract_view.yaml",
        "impact": source_graph_dir / "impact_report.json",
    }


def _reports_sync_rule(sync_manifest: dict[str, Any], module: str) -> dict[str, Any]:
    source_master = f"docs/hbtrack/modulos/{module}/graph/module_manifest.yaml"
    for rule in sync_manifest.get("rules", []):
        if rule.get("source_master") == source_master:
            return rule
    raise ContextBundleCompilerError(f"SYNC_MANIFEST sem regra para source graph do módulo `{module}`.")


def _features_for_module(feature_registry: dict[str, Any], module: str) -> list[dict[str, Any]]:
    features = [
        feature
        for feature in feature_registry.get("features", [])
        if feature.get("module") == module
    ]
    if not features:
        raise ContextBundleCompilerError(f"FEATURE_REGISTRY sem feature para o módulo `{module}`.")
    return sorted(features, key=lambda item: str(item.get("id", "")))


def _input_paths(root: Path, module: str) -> list[Path]:
    paths = [
        root / "docs" / "_canon" / "FEATURE_REGISTRY.yaml",
        root / "docs" / "_canon" / "MODULE_REGISTRY.yaml",
        root / "docs" / "_canon" / "SOURCE_AUTHORITY_GRAPH.yaml",
        root / "docs" / "_canon" / "SYNC_MANIFEST.yaml",
    ]
    paths.extend(_source_graph_paths(root, module).values())
    return paths


def _ensure_source_graph_is_fresh(root: Path, module: str) -> None:
    expected = compile_source_graph_expected(root, module)
    drifts = check_source_graph_expected(root, expected)
    if drifts:
        lines = ", ".join(f"{item.relpath} ({item.reason})" for item in drifts)
        raise ContextBundleCompilerError(
            "Source graph derivado está stale; regenere antes de compilar context bundle: "
            + lines
        )


def _endpoint_key(method: str, path: str) -> str:
    return f"{method.upper()} {path}"


def _slugify(value: str) -> str:
    collapsed = "".join(char.lower() if char.isalnum() else "-" for char in value)
    collapsed = "-".join(part for part in collapsed.split("-") if part)
    return collapsed or "feature"


def _resolve_module_registry_entry(module_registry: dict[str, Any], module: str) -> dict[str, Any]:
    modules = module_registry.get("modules") or {}
    entry = modules.get(module)
    if not isinstance(entry, dict):
        raise ContextBundleCompilerError(f"MODULE_REGISTRY sem entrada para `{module}`.")
    return entry


def _load_source_graph_payloads(root: Path, module: str) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    paths = _source_graph_paths(root, module)
    bundle = _load_yaml(paths["bundle"])
    schema_view = _load_yaml(paths["schema_view"])
    openapi_view = _load_yaml(paths["openapi_view"])
    impact_report = _load_json(paths["impact"])
    if bundle.get("module") != module:
        raise ContextBundleCompilerError(f"Bundle do source graph diverge do módulo `{module}`.")
    if impact_report.get("module") != module:
        raise ContextBundleCompilerError(f"Impact report do source graph diverge do módulo `{module}`.")
    return bundle, schema_view, openapi_view, impact_report


def _feature_operations(bundle: dict[str, Any], feature: dict[str, Any]) -> list[dict[str, Any]]:
    operation_map = {
        _endpoint_key(entry["method"], entry["path"]): entry
        for entry in bundle.get("endpoints", [])
    }
    resolved: list[dict[str, Any]] = []
    for endpoint in feature.get("endpoints", []):
        entry = operation_map.get(endpoint)
        if entry is None:
            raise ContextBundleCompilerError(
                f"Feature `{feature['id']}` referencia endpoint inexistente no source graph: {endpoint}"
            )
        resolved.append(entry)
    return resolved


def _feature_errors(bundle: dict[str, Any], operations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    operation_ids = {entry["operation_id"] for entry in operations}
    errors: list[dict[str, Any]] = []
    for error in bundle.get("errors", []):
        if operation_ids & set(error.get("operations", [])):
            errors.append(error)
    return errors


def _bundle_targets(sync_rule: dict[str, Any], module: str) -> dict[str, list[str]]:
    prefix = f"src/{module}/"
    generated_prefix = f"src/{module}/generated/"
    bundle_prefix = f"compiled_context/{module}/"
    consumers = sorted(set(sync_rule.get("required_consumers", [])))
    return {
        "generated_runtime": [path for path in consumers if path.startswith(generated_prefix)],
        "canonical_runtime": [path for path in consumers if path.startswith(prefix) and not path.startswith(generated_prefix)],
        "contracts": [path for path in consumers if path.startswith("contracts/") and f"/{module}" in path],
        "module_docs": [path for path in consumers if path.startswith(f"docs/hbtrack/modulos/{module}/")],
        "derived_context": [path for path in consumers if path.startswith(bundle_prefix)],
        "tests": [path for path in consumers if path.startswith("tests/") and module in path],
    }


def _bundle_inputs(root: Path, module: str) -> list[dict[str, str]]:
    return [
        {
            "relpath": _rel(root, path),
            "sha256": _sha256_bytes(path.read_bytes()),
        }
        for path in _input_paths(root, module)
    ]


def _build_context_bundle(
    *,
    root: Path,
    module: str,
    module_entry: dict[str, Any],
    feature: dict[str, Any],
    bundle: dict[str, Any],
    schema_view: dict[str, Any],
    openapi_view: dict[str, Any],
    impact_report: dict[str, Any],
    source_authority_graph: dict[str, Any],
    sync_rule: dict[str, Any],
) -> dict[str, Any]:
    operations = _feature_operations(bundle, feature)
    errors = _feature_errors(bundle, operations)
    inputs = _bundle_inputs(root, module)
    input_map = {item["relpath"]: item["sha256"] for item in inputs}
    output_relpath = f"compiled_context/{module}/{feature['id']}.json"

    return {
        "artifact_id": "HBTRACK_MODULE_FEATURE_CONTEXT_BUNDLE",
        "compiler": COMPILER_NAME,
        "compiler_version": COMPILER_VERSION,
        "module": module,
        "module_state": {
            "status": module_entry["status"],
            "owner": module_entry["owner"],
            "expected_surfaces": module_entry.get("expected_surfaces", []),
        },
        "feature": {
            "id": feature["id"],
            "slug": _slugify(str(feature.get("name", ""))),
            "name": feature["name"],
            "status": feature["status"],
            "description": feature["description"].strip(),
            "endpoints": feature.get("endpoints", []),
            "contracts": feature.get("contracts", []),
        },
        "source_fingerprint": _sha256_text(json.dumps(input_map, sort_keys=True)),
        "inputs": inputs,
        "authority": {
            "source_authority_graph_ref": "docs/_canon/SOURCE_AUTHORITY_GRAPH.yaml",
            "sync_manifest_ref": "docs/_canon/SYNC_MANIFEST.yaml",
            "sync_rule_id": sync_rule["rule_id"],
            "source_graph_bundle_ref": f"generated/source_graph/{module}/{module}.bundle.yaml",
            "schema_contract_view_ref": f"generated/source_graph/{module}/{module}.schema_contract_view.yaml",
            "openapi_contract_view_ref": f"generated/source_graph/{module}/{module}.openapi_contract_view.yaml",
            "source_graph_impact_ref": f"generated/source_graph/{module}/impact_report.json",
            "precedence_order": source_authority_graph["policy"]["conflict_resolution"]["precedence_order"],
            "partial_update_policy": source_authority_graph["policy"]["conflict_resolution"]["partial_update_policy"],
        },
        "module_docs": {
            key: _rel(root, (root / "docs" / "hbtrack" / "modulos" / module / "graph" / ref).resolve())
            for key, ref in bundle["module_manifest"]["module_docs"].items()
        },
        "contract_surfaces": {
            key: _rel(root, (root / "docs" / "hbtrack" / "modulos" / module / "graph" / ref).resolve())
            for key, ref in bundle["module_manifest"]["contract_surfaces"].items()
        },
        "runtime_surfaces": {
            key: _rel(root, (root / "docs" / "hbtrack" / "modulos" / module / "graph" / ref).resolve())
            for key, ref in bundle["module_manifest"]["runtime_surfaces"].items()
        },
        "source_graph": {
            "entities": bundle.get("entities", {}),
            "operations": operations,
            "errors": errors,
            "test_obligations": bundle.get("test_obligations", []),
            "schema_contract_view": schema_view,
            "openapi_contract_view": openapi_view,
            "impact_report": {
                "blocked_partial_update": impact_report["blocked_partial_update"],
                "source_fingerprint": impact_report["source_fingerprint"],
                "impacted_docs": impact_report["impacted_docs"],
                "impacted_contracts": impact_report["impacted_contracts"],
                "impacted_runtime": impact_report["impacted_runtime"],
                "known_gaps": impact_report.get("known_gaps", []),
            },
        },
        "implementation_targets": _bundle_targets(sync_rule, module),
        "validation": {
            "required_commands": [
                "python3 scripts/compile/compile_source_graph.py --module reports --check --format json"
                if module == "reports"
                else f"python3 scripts/compile/compile_source_graph.py --module {module} --check --format json",
                "python3 scripts/compile/compile_context_bundle.py --module reports --check --format json"
                if module == "reports"
                else f"python3 scripts/compile/compile_context_bundle.py --module {module} --check --format json",
                *sync_rule.get("validation_commands", []),
            ],
            "blocking_consumers": sync_rule.get("blocking_consumers", []),
            "expected_output": output_relpath,
        },
    }


def compile_expected(root: Path, module: str) -> list[ExpectedFile]:
    _ensure_source_graph_is_fresh(root, module)
    feature_registry = _feature_registry(root)
    module_registry = _module_registry(root)
    source_authority_graph = _source_authority_graph(root)
    sync_manifest = _sync_manifest(root)
    module_entry = _resolve_module_registry_entry(module_registry, module)
    bundle, schema_view, openapi_view, impact_report = _load_source_graph_payloads(root, module)
    sync_rule = _reports_sync_rule(sync_manifest, module)

    expected: list[ExpectedFile] = []
    for feature in _features_for_module(feature_registry, module):
        payload = _build_context_bundle(
            root=root,
            module=module,
            module_entry=module_entry,
            feature=feature,
            bundle=bundle,
            schema_view=schema_view,
            openapi_view=openapi_view,
            impact_report=impact_report,
            source_authority_graph=source_authority_graph,
            sync_rule=sync_rule,
        )
        output_relpath = f"compiled_context/{module}/{feature['id']}.json"
        expected.append(ExpectedFile(output_relpath, _dump_json(payload)))
    return expected


def write_expected(root: Path, expected: list[ExpectedFile]) -> list[str]:
    written: list[str] = []
    for item in expected:
        path = root / item.relpath
        path.parent.mkdir(parents=True, exist_ok=True)
        current = path.read_text(encoding="utf-8") if path.exists() else None
        if current != item.content:
            path.write_text(item.content, encoding="utf-8")
            written.append(item.relpath)
    return written


def check_expected(root: Path, expected: list[ExpectedFile]) -> list[Drift]:
    drifts: list[Drift] = []
    expected_map = {item.relpath: item.content for item in expected}

    for relpath, expected_content in expected_map.items():
        target = root / relpath
        if not target.exists():
            drifts.append(Drift(relpath, "missing"))
            continue
        current = target.read_text(encoding="utf-8")
        if current != expected_content:
            drifts.append(Drift(relpath, "content_mismatch"))

    if expected:
        parent = (root / expected[0].relpath).parent
        if parent.exists():
            expected_paths = set(expected_map)
            for extra in sorted(path for path in parent.glob("*") if path.is_file()):
                relpath = _rel(root, extra)
                if relpath not in expected_paths:
                    drifts.append(Drift(relpath, "unexpected_extra_file"))

    return drifts


def _format_payload(
    status: str,
    mode: str,
    module: str,
    *,
    expected: list[ExpectedFile],
    written: list[str] | None = None,
    drifts: list[Drift] | None = None,
) -> dict[str, Any]:
    return {
        "artifact_id": "HBTRACK_CONTEXT_BUNDLE_COMPILER_RESULT",
        "compiler": COMPILER_NAME,
        "compiler_version": COMPILER_VERSION,
        "module": module,
        "features": [Path(item.relpath).stem for item in expected],
        "status": status,
        "mode": mode,
        "written": written or [],
        "drifts": [{"relpath": item.relpath, "reason": item.reason} for item in (drifts or [])],
    }


def _format_multi_payload(status: str, mode: str, modules: list[str], results: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "artifact_id": "HBTRACK_CONTEXT_BUNDLE_COMPILER_BATCH_RESULT",
        "compiler": COMPILER_NAME,
        "compiler_version": COMPILER_VERSION,
        "modules": modules,
        "status": status,
        "mode": mode,
        "results": results,
    }


def main(argv: list[str] | None = None) -> int:
    root = _repo_root()
    ap = argparse.ArgumentParser(description="Compila bundles determinísticos por módulo/feature em compiled_context/.")
    scope = ap.add_mutually_exclusive_group(required=True)
    scope.add_argument("--module", help="Módulo com source graph ativo.")
    scope.add_argument("--all", action="store_true", help="Executa para todos os módulos com source graph ativo.")
    ap.add_argument("--check", action="store_true", help="Não escreve; apenas verifica drift.")
    ap.add_argument("--format", choices=("text", "json"), default="text", help="Formato de saída.")
    args = ap.parse_args(argv)

    modules = [args.module] if args.module else _discover_source_graph_modules(root)
    if not modules:
        message = "Nenhum módulo com source graph ativo foi encontrado."
        if args.format == "json":
            print(
                _dump_json(
                    {
                        "artifact_id": "HBTRACK_CONTEXT_BUNDLE_COMPILER_BATCH_RESULT",
                        "compiler": COMPILER_NAME,
                        "compiler_version": COMPILER_VERSION,
                        "modules": [],
                        "status": "FAIL",
                        "mode": "check" if args.check else "write",
                        "error": message,
                    }
                ),
                end="",
            )
        else:
            print(f"ERROR: {message}")
        return 2

    results: list[dict[str, Any]] = []
    overall_exit = 0
    mode = "check" if args.check else "write"

    for module in modules:
        try:
            expected = compile_expected(root, module)
            if args.check:
                drifts = check_expected(root, expected)
                if drifts:
                    payload = _format_payload("FAIL", mode, module, expected=expected, drifts=drifts)
                    overall_exit = max(overall_exit, 2)
                else:
                    payload = _format_payload("PASS", mode, module, expected=expected)
            else:
                written = write_expected(root, expected)
                payload = _format_payload("PASS", mode, module, expected=expected, written=written)
            results.append(payload)
        except (ContextBundleCompilerError, SourceGraphCompilerError) as exc:
            results.append(
                {
                    "artifact_id": "HBTRACK_CONTEXT_BUNDLE_COMPILER_RESULT",
                    "compiler": COMPILER_NAME,
                    "compiler_version": COMPILER_VERSION,
                    "module": module,
                    "status": "FAIL",
                    "mode": mode,
                    "error": exc.summary if hasattr(exc, 'summary') else str(exc),
                }
            )
            overall_exit = max(overall_exit, 2)

    if len(results) == 1:
        payload = results[0]
        if args.format == "json":
            print(_dump_json(payload), end="")
        else:
            if payload["status"] == "FAIL":
                if payload.get("drifts"):
                    for drift in payload["drifts"]:
                        print(f"DRIFT: {drift['relpath']} ({drift['reason']})")
                    print(f"FAIL: {len(payload['drifts'])} drift(s) detectado(s) nos context bundles.")
                else:
                    print(f"ERROR: {payload['error']}")
            elif args.check:
                print(f"OK: context bundles de `{payload['module']}` alinhados ao compiler determinístico.")
            else:
                if payload["written"]:
                    print("UPDATED:")
                    for relpath in payload["written"]:
                        print(f"- {relpath}")
                else:
                    print("OK: nenhum arquivo precisou ser atualizado.")
        return overall_exit

    batch_payload = _format_multi_payload(
        "PASS" if overall_exit == 0 else "FAIL",
        mode,
        modules,
        results,
    )
    if args.format == "json":
        print(_dump_json(batch_payload), end="")
    else:
        for payload in results:
            summary = payload.get("error")
            if payload["status"] == "FAIL" and payload.get("drifts"):
                summary = f"{len(payload['drifts'])} drift(s)"
            elif payload["status"] == "PASS" and not args.check:
                summary = f"{len(payload.get('written', []))} arquivo(s) atualizado(s)"
            elif payload["status"] == "PASS":
                summary = "alinhado"
            print(f"[{payload['status']}] {payload['module']}: {summary}")
    return overall_exit


if __name__ == "__main__":
    raise SystemExit(main())
