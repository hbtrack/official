from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


COMPILER_NAME = "hbtrack_source_graph_compiler"
COMPILER_VERSION = "0.1.0"
GRAPH_FILENAMES = (
    "module_manifest.yaml",
    "entities.yaml",
    "endpoints.yaml",
    "errors.yaml",
    "test_obligations.yaml",
)


@dataclass(frozen=True)
class ExpectedFile:
    relpath: str
    content: str


@dataclass(frozen=True)
class Drift:
    relpath: str
    reason: str


class SourceGraphCompilerError(RuntimeError):
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


def _rel(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_text(text: str) -> str:
    return _sha256_bytes(text.encode("utf-8"))


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise SourceGraphCompilerError(f"Arquivo YAML ausente: {path}")
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(payload, dict):
        raise SourceGraphCompilerError(f"YAML inválido (esperado objeto): {path}")
    return payload


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise SourceGraphCompilerError(f"Arquivo JSON ausente: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise SourceGraphCompilerError(f"JSON inválido (esperado objeto): {path}")
    return payload


def _dump_yaml(data: dict[str, Any]) -> str:
    return yaml.safe_dump(data, allow_unicode=False, sort_keys=False)


def _dump_json(data: dict[str, Any]) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def _graph_root(root: Path, module: str) -> Path:
    return root / "docs" / "hbtrack" / "modulos" / module / "graph"


def _resolve_ref(root: Path, base_dir: Path, ref: str) -> Path:
    target = (base_dir / ref).resolve()
    if not target.exists():
        raise SourceGraphCompilerError(f"Referência ausente no source graph: {ref}")
    if root not in target.parents and target != root:
        raise SourceGraphCompilerError(f"Referência fora do repositório: {ref}")
    return target


def _expand_resolved_path(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    if path.is_dir():
        return sorted(candidate for candidate in path.rglob("*") if candidate.is_file())
    raise SourceGraphCompilerError(f"Referência inválida (nem arquivo nem diretório): {path}")


def _read_source_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _operation_ids_from_openapi(path_doc: dict[str, Any]) -> list[str]:
    operation_ids: list[str] = []
    for path_item in path_doc.values():
        if not isinstance(path_item, dict):
            continue
        for method_doc in path_item.values():
            if isinstance(method_doc, dict) and "operationId" in method_doc:
                operation_ids.append(str(method_doc["operationId"]))
    return sorted(operation_ids)


def _validate_graph_payload(
    *,
    root: Path,
    module: str,
    manifest: dict[str, Any],
    entities: dict[str, Any],
    endpoints: dict[str, Any],
    errors: dict[str, Any],
    test_obligations: dict[str, Any],
) -> dict[str, Any]:
    graph_root = _graph_root(root, module)

    if manifest.get("module") != module:
        raise SourceGraphCompilerError("module_manifest.yaml não corresponde ao módulo alvo.")
    if manifest.get("status") != "active":
        raise SourceGraphCompilerError("module_manifest.yaml deve estar com status=active.")

    for filename in GRAPH_FILENAMES:
        payload = _load_yaml(graph_root / filename)
        if payload.get("module") != module:
            raise SourceGraphCompilerError(f"{filename} declara módulo diferente de `{module}`.")
        if payload.get("status") != "active":
            raise SourceGraphCompilerError(f"{filename} deve estar com status=active.")

    for section in ("global_refs", "module_docs", "contract_surfaces", "runtime_surfaces", "structured_ir"):
        values = manifest.get(section)
        if not isinstance(values, dict) or not values:
            raise SourceGraphCompilerError(f"module_manifest.yaml precisa de `{section}` não vazio.")
        for ref in values.values():
            if not isinstance(ref, str) or not ref.strip():
                raise SourceGraphCompilerError(f"Referência inválida em module_manifest.{section}.")
            _resolve_ref(root, graph_root, ref)

    report_job = entities.get("entities", {}).get("ReportJob")
    if not isinstance(report_job, dict):
        raise SourceGraphCompilerError("entities.yaml precisa declarar a entidade ReportJob.")

    primary_schema = _resolve_ref(root, graph_root, report_job["schema_ref"])
    schema = _load_json(primary_schema)
    sovereign_fields = report_job.get("sovereign_fields")
    if not isinstance(sovereign_fields, list) or not sovereign_fields:
        raise SourceGraphCompilerError("ReportJob.sovereign_fields deve ser lista não vazia.")
    sovereign_names = [field["name"] for field in sovereign_fields]
    schema_names = list((schema.get("properties") or {}).keys())
    if sovereign_names != schema_names:
        raise SourceGraphCompilerError("entities.yaml diverge da ordem/campos do schema soberano de reports.")

    required_from_graph = sorted(field["name"] for field in sovereign_fields if field.get("required"))
    required_from_schema = sorted(schema.get("required") or [])
    if required_from_graph != required_from_schema:
        raise SourceGraphCompilerError("entities.yaml diverge do conjunto de required do schema soberano.")

    entity_source = _read_source_text(_resolve_ref(root, graph_root, report_job["runtime_entity_ref"].split("#", 1)[0]))
    for field in sovereign_fields:
        runtime_name = field.get("runtime_name")
        if runtime_name not in entity_source:
            raise SourceGraphCompilerError(f"Campo runtime `{runtime_name}` não encontrado em entities.py.")
    for field in report_job.get("runtime_extension_fields", []):
        runtime_name = field.get("runtime_name")
        if runtime_name not in entity_source:
            raise SourceGraphCompilerError(f"Extensão runtime `{runtime_name}` não encontrada em entities.py.")

    openapi_paths = _load_yaml(_resolve_ref(root, graph_root, manifest["contract_surfaces"]["openapi_paths"]))
    operation_ids = _operation_ids_from_openapi(openapi_paths)
    endpoint_entries = endpoints.get("endpoints")
    if not isinstance(endpoint_entries, list) or not endpoint_entries:
        raise SourceGraphCompilerError("endpoints.yaml precisa declarar endpoints não vazios.")
    endpoint_ids = sorted(entry["operation_id"] for entry in endpoint_entries)
    if endpoint_ids != operation_ids:
        raise SourceGraphCompilerError("endpoints.yaml diverge dos operationIds de contracts/openapi/paths/reports.yaml.")

    api_source = _read_source_text(_resolve_ref(root, graph_root, manifest["runtime_surfaces"]["api_router"]))
    use_case_source = _read_source_text(_resolve_ref(root, graph_root, manifest["runtime_surfaces"]["use_cases"]))
    for entry in endpoint_entries:
        if not isinstance(entry.get("response_codes"), list) or not entry["response_codes"]:
            raise SourceGraphCompilerError(f"Endpoint `{entry['operation_id']}` sem response_codes.")
        handler_symbol = entry["runtime_handler_ref"].split("#", 1)[1]
        use_case_symbol = entry["use_case_ref"].split("#", 1)[1]
        if f"def {handler_symbol}" not in api_source:
            raise SourceGraphCompilerError(f"Handler `{handler_symbol}` ausente em src/reports/api.py.")
        if f"class {use_case_symbol}" not in use_case_source:
            raise SourceGraphCompilerError(f"Use case `{use_case_symbol}` ausente em src/reports/application/use_cases.py.")

    error_entries = errors.get("errors")
    if not isinstance(error_entries, list) or not error_entries:
        raise SourceGraphCompilerError("errors.yaml precisa declarar errors não vazios.")
    operation_id_set = set(operation_ids)
    rules_source = _read_source_text(_resolve_ref(root, graph_root, manifest["runtime_surfaces"]["domain_rules"]))
    for error in error_entries:
        if not set(error.get("operations", [])) <= operation_id_set:
            raise SourceGraphCompilerError(f"Erro `{error.get('id')}` referencia operationId inexistente.")
        exception_ref = error.get("exception_ref")
        if exception_ref:
            exception_symbol = exception_ref.split("#", 1)[1]
            if f"class {exception_symbol}" not in rules_source:
                raise SourceGraphCompilerError(f"Exceção `{exception_symbol}` ausente em src/reports/domain/rules.py.")

    obligations = test_obligations.get("obligations")
    if not isinstance(obligations, list) or not obligations:
        raise SourceGraphCompilerError("test_obligations.yaml precisa declarar obligations não vazias.")
    for obligation in obligations:
        _resolve_ref(root, graph_root, obligation["artifact_ref"])
        for evidence_ref in obligation.get("evidence_refs", []):
            _resolve_ref(root, graph_root, evidence_ref)

    return {
        "schema": schema,
        "operation_ids": operation_ids,
    }


def _collect_input_paths(root: Path, module: str, manifest: dict[str, Any]) -> list[Path]:
    graph_root = _graph_root(root, module)
    input_paths: dict[str, Path] = {}

    for filename in GRAPH_FILENAMES:
        path = graph_root / filename
        input_paths[_rel(root, path)] = path

    for section in ("global_refs", "module_docs", "contract_surfaces", "runtime_surfaces", "structured_ir"):
        for ref in manifest[section].values():
            target = _resolve_ref(root, graph_root, ref)
            for expanded in _expand_resolved_path(target):
                input_paths[_rel(root, expanded)] = expanded

    return [input_paths[key] for key in sorted(input_paths)]


def _build_bundle(
    *,
    root: Path,
    module: str,
    manifest: dict[str, Any],
    entities: dict[str, Any],
    endpoints: dict[str, Any],
    errors: dict[str, Any],
    test_obligations: dict[str, Any],
    input_paths: list[Path],
) -> dict[str, Any]:
    return {
        "artifact_id": "HBTRACK_SOURCE_GRAPH_BUNDLE",
        "compiler": COMPILER_NAME,
        "compiler_version": COMPILER_VERSION,
        "module": module,
        "graph_root": _rel(root, _graph_root(root, module)),
        "inputs": [
            {
                "relpath": _rel(root, path),
                "sha256": _sha256_bytes(path.read_bytes()),
            }
            for path in input_paths
        ],
        "module_manifest": manifest,
        "entities": entities["entities"],
        "endpoints": endpoints["endpoints"],
        "errors": errors["errors"],
        "test_obligations": test_obligations["obligations"],
    }


def _build_schema_contract_view(
    *,
    root: Path,
    module: str,
    manifest: dict[str, Any],
    entities: dict[str, Any],
    schema: dict[str, Any],
) -> dict[str, Any]:
    report_job = entities["entities"]["ReportJob"]
    return {
        "artifact_id": "HBTRACK_SOURCE_GRAPH_SCHEMA_CONTRACT_VIEW",
        "compiler": COMPILER_NAME,
        "compiler_version": COMPILER_VERSION,
        "module": module,
        "entity": "ReportJob",
        "primary_schema_ref": _rel(root, _resolve_ref(root, _graph_root(root, module), manifest["contract_surfaces"]["primary_schema"])),
        "openapi_projection_ref": _rel(root, _resolve_ref(root, _graph_root(root, module), manifest["contract_surfaces"]["openapi_projection"])),
        "required": schema.get("required", []),
        "sovereign_fields": report_job["sovereign_fields"],
        "runtime_extension_fields": report_job.get("runtime_extension_fields", []),
    }


def _build_openapi_contract_view(
    *,
    root: Path,
    module: str,
    manifest: dict[str, Any],
    endpoints: dict[str, Any],
    errors: dict[str, Any],
) -> dict[str, Any]:
    return {
        "artifact_id": "HBTRACK_SOURCE_GRAPH_OPENAPI_CONTRACT_VIEW",
        "compiler": COMPILER_NAME,
        "compiler_version": COMPILER_VERSION,
        "module": module,
        "openapi_paths_ref": _rel(root, _resolve_ref(root, _graph_root(root, module), manifest["contract_surfaces"]["openapi_paths"])),
        "operations": endpoints["endpoints"],
        "errors": errors["errors"],
    }


def _build_impact_report(
    *,
    root: Path,
    module: str,
    manifest: dict[str, Any],
    bundle: dict[str, Any],
    outputs: list[str],
) -> dict[str, Any]:
    input_map = {item["relpath"]: item["sha256"] for item in bundle["inputs"]}
    fingerprint = _sha256_text(json.dumps(input_map, sort_keys=True))
    impacted_contracts = [
        _rel(root, _resolve_ref(root, _graph_root(root, module), manifest["contract_surfaces"]["openapi_paths"])),
        _rel(root, _resolve_ref(root, _graph_root(root, module), manifest["contract_surfaces"]["primary_schema"])),
        _rel(root, _resolve_ref(root, _graph_root(root, module), manifest["contract_surfaces"]["openapi_projection"])),
    ]
    impacted_runtime = [
        _rel(root, _resolve_ref(root, _graph_root(root, module), ref))
        for ref in manifest["runtime_surfaces"].values()
    ]
    impacted_docs = [
        _rel(root, _resolve_ref(root, _graph_root(root, module), ref))
        for ref in manifest["module_docs"].values()
    ]
    return {
        "artifact_id": "HBTRACK_SOURCE_GRAPH_IMPACT_REPORT",
        "compiler": COMPILER_NAME,
        "compiler_version": COMPILER_VERSION,
        "module": module,
        "blocked_partial_update": True,
        "source_fingerprint": fingerprint,
        "inputs": bundle["inputs"],
        "outputs": outputs,
        "impacted_docs": impacted_docs,
        "impacted_contracts": impacted_contracts,
        "impacted_runtime": impacted_runtime,
        "known_gaps": manifest.get("known_gaps", []),
        "next_stage_targets": [
            "B3-001",
            "B3-002",
        ],
    }


def compile_expected(root: Path, module: str) -> list[ExpectedFile]:
    graph_root = _graph_root(root, module)
    if not graph_root.exists():
        raise SourceGraphCompilerError(f"Source graph ausente para módulo `{module}`: {graph_root}")

    manifest = _load_yaml(graph_root / "module_manifest.yaml")
    entities = _load_yaml(graph_root / "entities.yaml")
    endpoints = _load_yaml(graph_root / "endpoints.yaml")
    errors = _load_yaml(graph_root / "errors.yaml")
    test_obligations = _load_yaml(graph_root / "test_obligations.yaml")

    validated = _validate_graph_payload(
        root=root,
        module=module,
        manifest=manifest,
        entities=entities,
        endpoints=endpoints,
        errors=errors,
        test_obligations=test_obligations,
    )

    input_paths = _collect_input_paths(root, module, manifest)
    bundle = _build_bundle(
        root=root,
        module=module,
        manifest=manifest,
        entities=entities,
        endpoints=endpoints,
        errors=errors,
        test_obligations=test_obligations,
        input_paths=input_paths,
    )
    schema_view = _build_schema_contract_view(
        root=root,
        module=module,
        manifest=manifest,
        entities=entities,
        schema=validated["schema"],
    )
    openapi_view = _build_openapi_contract_view(
        root=root,
        module=module,
        manifest=manifest,
        endpoints=endpoints,
        errors=errors,
    )

    output_root = Path("generated") / "source_graph" / module
    outputs = [
        (output_root / f"{module}.bundle.yaml").as_posix(),
        (output_root / f"{module}.schema_contract_view.yaml").as_posix(),
        (output_root / f"{module}.openapi_contract_view.yaml").as_posix(),
        (output_root / "impact_report.json").as_posix(),
    ]
    impact_report = _build_impact_report(
        root=root,
        module=module,
        manifest=manifest,
        bundle=bundle,
        outputs=outputs,
    )

    return [
        ExpectedFile(outputs[0], _dump_yaml(bundle)),
        ExpectedFile(outputs[1], _dump_yaml(schema_view)),
        ExpectedFile(outputs[2], _dump_yaml(openapi_view)),
        ExpectedFile(outputs[3], _dump_json(impact_report)),
    ]


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


def _format_payload(status: str, mode: str, module: str, *, written: list[str] | None = None, drifts: list[Drift] | None = None) -> dict[str, Any]:
    return {
        "artifact_id": "HBTRACK_SOURCE_GRAPH_COMPILER_RESULT",
        "compiler": COMPILER_NAME,
        "compiler_version": COMPILER_VERSION,
        "module": module,
        "status": status,
        "mode": mode,
        "written": written or [],
        "drifts": [{"relpath": item.relpath, "reason": item.reason} for item in (drifts or [])],
    }


def main(argv: list[str] | None = None) -> int:
    root = _repo_root()
    ap = argparse.ArgumentParser(description="Compila source graph de módulo e gera derivados determinísticos em generated/source_graph/.")
    ap.add_argument("--module", required=True, help="Módulo com source graph ativo.")
    ap.add_argument("--check", action="store_true", help="Não escreve; apenas verifica drift.")
    ap.add_argument("--format", choices=("text", "json"), default="text", help="Formato de saída.")
    args = ap.parse_args(argv)

    try:
        expected = compile_expected(root, args.module)
        if args.check:
            drifts = check_expected(root, expected)
            if drifts:
                payload = _format_payload("FAIL", "check", args.module, drifts=drifts)
                if args.format == "json":
                    print(_dump_json(payload), end="")
                else:
                    for drift in drifts:
                        print(f"DRIFT: {drift.relpath} ({drift.reason})")
                    print(f"FAIL: {len(drifts)} drift(s) detectado(s) no source graph derivado.")
                return 2
            payload = _format_payload("PASS", "check", args.module)
            if args.format == "json":
                print(_dump_json(payload), end="")
            else:
                print(f"OK: source graph `{args.module}` alinhado ao compiler determinístico.")
            return 0

        written = write_expected(root, expected)
        payload = _format_payload("PASS", "write", args.module, written=written)
        if args.format == "json":
            print(_dump_json(payload), end="")
        else:
            if written:
                print("OK: artefatos gerados/atualizados:")
                for relpath in written:
                    print(f"  - {relpath}")
            else:
                print("OK: nada a atualizar (generated/source_graph já está alinhado).")
        return 0
    except SourceGraphCompilerError as exc:
        payload = {
            "artifact_id": "HBTRACK_SOURCE_GRAPH_COMPILER_RESULT",
            "compiler": COMPILER_NAME,
            "compiler_version": COMPILER_VERSION,
            "module": args.module,
            "status": "FAIL",
            "mode": "check" if args.check else "write",
            "summary": exc.summary,
        }
        if args.format == "json":
            print(_dump_json(payload), end="")
        else:
            print(f"FAIL: {exc.summary}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
