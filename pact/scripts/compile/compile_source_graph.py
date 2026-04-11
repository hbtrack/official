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
    "entity_graph.yaml",
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


def _discover_graph_modules(root: Path) -> list[str]:
    base = root / "docs" / "hbtrack" / "modulos"
    if not base.exists():
        return []
    modules: list[str] = []
    for manifest in sorted(base.glob("*/graph/module_manifest.yaml")):
        modules.append(manifest.parent.parent.name)
    return modules


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


def _resolve_symbol_ref(root: Path, base_dir: Path, ref: str) -> tuple[Path, str]:
    if "#" not in ref:
        raise SourceGraphCompilerError(f"Referência simbólica inválida: {ref}")
    path_ref, symbol = ref.split("#", 1)
    if not symbol.strip():
        raise SourceGraphCompilerError(f"Referência simbólica sem símbolo: {ref}")
    return _resolve_ref(root, base_dir, path_ref), symbol


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

    entity_entries = entities.get("entities")
    if not isinstance(entity_entries, dict) or not entity_entries:
        raise SourceGraphCompilerError("entity_graph.yaml precisa declarar entities não vazias.")

    validated_entities: dict[str, Any] = {}
    for entity_name, entity_entry in entity_entries.items():
        if not isinstance(entity_entry, dict):
            raise SourceGraphCompilerError(f"entities.{entity_name} deve ser objeto.")
        schema_path = _resolve_ref(root, graph_root, entity_entry["schema_ref"])
        schema = _load_json(schema_path)
        schema_properties = schema.get("properties")
        if not isinstance(schema_properties, dict) or not schema_properties:
            raise SourceGraphCompilerError(f"{entity_name}.schema_ref precisa apontar para schema com properties.")
        runtime_entity_path, runtime_entity_symbol = _resolve_symbol_ref(
            root,
            graph_root,
            entity_entry["runtime_entity_ref"],
        )
        entity_source = _read_source_text(runtime_entity_path)
        if f"class {runtime_entity_symbol}" not in entity_source:
            raise SourceGraphCompilerError(
                f"Entidade runtime `{runtime_entity_symbol}` não encontrada em {runtime_entity_path}."
            )

        docs_refs = entity_entry.get("docs_refs") or []
        if not isinstance(docs_refs, list) or not docs_refs:
            raise SourceGraphCompilerError(f"{entity_name}.docs_refs deve ser lista não vazia.")
        for ref in docs_refs:
            _resolve_ref(root, graph_root, ref)

        sovereign_fields = entity_entry.get("sovereign_fields")
        if not isinstance(sovereign_fields, list) or not sovereign_fields:
            raise SourceGraphCompilerError(f"{entity_name}.sovereign_fields deve ser lista não vazia.")
        sovereign_names = [field["name"] for field in sovereign_fields]
        schema_names = list(schema_properties.keys())
        if sovereign_names != schema_names:
            raise SourceGraphCompilerError(
                f"{entity_name}.sovereign_fields diverge da ordem/campos do schema soberano."
            )

        required_from_graph = sorted(field["name"] for field in sovereign_fields if field.get("required"))
        required_from_schema = sorted(schema.get("required") or [])
        if required_from_graph != required_from_schema:
            raise SourceGraphCompilerError(
                f"{entity_name}.sovereign_fields diverge do conjunto de required do schema soberano."
            )

        for field in sovereign_fields:
            runtime_name = field.get("runtime_name")
            if not runtime_name or runtime_name not in entity_source:
                raise SourceGraphCompilerError(
                    f"Campo runtime `{runtime_name}` não encontrado em {runtime_entity_path}."
                )
        for field in entity_entry.get("runtime_extension_fields", []):
            runtime_name = field.get("runtime_name")
            if not runtime_name or runtime_name not in entity_source:
                raise SourceGraphCompilerError(
                    f"Extensão runtime `{runtime_name}` não encontrada em {runtime_entity_path}."
                )

        validated_entities[entity_name] = {
            "entry": entity_entry,
            "schema": schema,
            "schema_path": schema_path,
            "runtime_entity_path": runtime_entity_path,
        }

    primary_schema = _resolve_ref(root, graph_root, manifest["contract_surfaces"]["primary_schema"])
    primary_entity_names = [
        entity_name
        for entity_name, payload in validated_entities.items()
        if payload["schema_path"] == primary_schema
    ]
    if len(primary_entity_names) != 1:
        raise SourceGraphCompilerError(
            "contract_surfaces.primary_schema deve corresponder exatamente a uma entidade em entity_graph.yaml."
        )
    primary_entity = primary_entity_names[0]

    openapi_paths = _load_yaml(_resolve_ref(root, graph_root, manifest["contract_surfaces"]["openapi_paths"]))
    operation_ids = _operation_ids_from_openapi(openapi_paths)
    endpoint_entries = endpoints.get("endpoints")
    if not isinstance(endpoint_entries, list) or not endpoint_entries:
        raise SourceGraphCompilerError("endpoints.yaml precisa declarar endpoints não vazios.")
    endpoint_ids = sorted(entry["operation_id"] for entry in endpoint_entries)
    if endpoint_ids != operation_ids:
        raise SourceGraphCompilerError(
            "endpoints.yaml diverge dos operationIds expostos por contract_surfaces.openapi_paths."
        )

    for entry in endpoint_entries:
        if not isinstance(entry.get("response_codes"), list) or not entry["response_codes"]:
            raise SourceGraphCompilerError(f"Endpoint `{entry['operation_id']}` sem response_codes.")
        _resolve_ref(root, graph_root, entry["openapi_ref"].split("#", 1)[0])

        handler_path, handler_symbol = _resolve_symbol_ref(root, graph_root, entry["runtime_handler_ref"])
        handler_source = _read_source_text(handler_path)
        if f"def {handler_symbol}" not in handler_source:
            raise SourceGraphCompilerError(f"Handler `{handler_symbol}` ausente em {handler_path}.")

        use_case_path, use_case_symbol = _resolve_symbol_ref(root, graph_root, entry["use_case_ref"])
        use_case_source = _read_source_text(use_case_path)
        if f"class {use_case_symbol}" not in use_case_source:
            raise SourceGraphCompilerError(f"Use case `{use_case_symbol}` ausente em {use_case_path}.")

    error_entries = errors.get("errors")
    if not isinstance(error_entries, list) or not error_entries:
        raise SourceGraphCompilerError("errors.yaml precisa declarar errors não vazios.")
    operation_id_set = set(operation_ids)
    for error in error_entries:
        if not set(error.get("operations", [])) <= operation_id_set:
            raise SourceGraphCompilerError(f"Erro `{error.get('id')}` referencia operationId inexistente.")
        exception_ref = error.get("exception_ref")
        if exception_ref:
            exception_path, exception_symbol = _resolve_symbol_ref(root, graph_root, exception_ref)
            exception_source = _read_source_text(exception_path)
            if f"class {exception_symbol}" not in exception_source:
                raise SourceGraphCompilerError(f"Exceção `{exception_symbol}` ausente em {exception_path}.")
        source_ref = error.get("source_ref")
        if source_ref:
            source_path, source_symbol = _resolve_symbol_ref(root, graph_root, source_ref)
            source = _read_source_text(source_path)
            if source_symbol not in source:
                raise SourceGraphCompilerError(f"Source ref `{source_symbol}` ausente em {source_path}.")

    obligations = test_obligations.get("obligations")
    if not isinstance(obligations, list) or not obligations:
        raise SourceGraphCompilerError("test_obligations.yaml precisa declarar obligations não vazias.")
    for obligation in obligations:
        _resolve_ref(root, graph_root, obligation["artifact_ref"])
        for evidence_ref in obligation.get("evidence_refs", []):
            _resolve_ref(root, graph_root, evidence_ref)

    return {
        "entities": validated_entities,
        "primary_entity": primary_entity,
        "primary_schema": validated_entities[primary_entity]["schema"],
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
    validated: dict[str, Any],
) -> dict[str, Any]:
    primary_entity_name = validated["primary_entity"]
    primary_entity = entities["entities"][primary_entity_name]
    primary_schema = validated["primary_schema"]
    entity_views = {}
    for entity_name, payload in validated["entities"].items():
        entity_entry = payload["entry"]
        entity_views[entity_name] = {
            "schema_ref": _rel(root, payload["schema_path"]),
            "required": payload["schema"].get("required", []),
            "sovereign_fields": entity_entry["sovereign_fields"],
            "runtime_extension_fields": entity_entry.get("runtime_extension_fields", []),
        }
    return {
        "artifact_id": "HBTRACK_SOURCE_GRAPH_SCHEMA_CONTRACT_VIEW",
        "compiler": COMPILER_NAME,
        "compiler_version": COMPILER_VERSION,
        "module": module,
        "entity": primary_entity_name,
        "primary_entity": primary_entity_name,
        "primary_schema_ref": _rel(root, _resolve_ref(root, _graph_root(root, module), manifest["contract_surfaces"]["primary_schema"])),
        "openapi_projection_ref": _rel(root, _resolve_ref(root, _graph_root(root, module), manifest["contract_surfaces"]["openapi_projection"])),
        "required": primary_schema.get("required", []),
        "sovereign_fields": primary_entity["sovereign_fields"],
        "runtime_extension_fields": primary_entity.get("runtime_extension_fields", []),
        "entities": entity_views,
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
    entities = _load_yaml(graph_root / "entity_graph.yaml")
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
        validated=validated,
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


def _format_multi_payload(status: str, mode: str, modules: list[str], results: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "artifact_id": "HBTRACK_SOURCE_GRAPH_COMPILER_BATCH_RESULT",
        "compiler": COMPILER_NAME,
        "compiler_version": COMPILER_VERSION,
        "modules": modules,
        "status": status,
        "mode": mode,
        "results": results,
    }


def main(argv: list[str] | None = None) -> int:
    root = _repo_root()
    ap = argparse.ArgumentParser(description="Compila source graph de módulo e gera derivados determinísticos em generated/source_graph/.")
    scope = ap.add_mutually_exclusive_group(required=True)
    scope.add_argument("--module", help="Módulo com source graph ativo.")
    scope.add_argument("--all", action="store_true", help="Executa para todos os módulos com source graph ativo.")
    ap.add_argument("--check", action="store_true", help="Não escreve; apenas verifica drift.")
    ap.add_argument("--format", choices=("text", "json"), default="text", help="Formato de saída.")
    args = ap.parse_args(argv)

    modules = [args.module] if args.module else _discover_graph_modules(root)
    if not modules:
        message = "Nenhum módulo com source graph ativo foi encontrado."
        if args.format == "json":
            print(
                _dump_json(
                    {
                        "artifact_id": "HBTRACK_SOURCE_GRAPH_COMPILER_BATCH_RESULT",
                        "compiler": COMPILER_NAME,
                        "compiler_version": COMPILER_VERSION,
                        "modules": [],
                        "status": "FAIL",
                        "mode": "check" if args.check else "write",
                        "summary": message,
                    }
                ),
                end="",
            )
        else:
            print(f"FAIL: {message}")
        return 1

    results: list[dict[str, Any]] = []
    overall_exit = 0
    mode = "check" if args.check else "write"

    for module in modules:
        try:
            expected = compile_expected(root, module)
            if args.check:
                drifts = check_expected(root, expected)
                if drifts:
                    payload = _format_payload("FAIL", mode, module, drifts=drifts)
                    overall_exit = max(overall_exit, 2)
                else:
                    payload = _format_payload("PASS", mode, module)
            else:
                written = write_expected(root, expected)
                payload = _format_payload("PASS", mode, module, written=written)
            results.append(payload)
        except SourceGraphCompilerError as exc:
            results.append(
                {
                    "artifact_id": "HBTRACK_SOURCE_GRAPH_COMPILER_RESULT",
                    "compiler": COMPILER_NAME,
                    "compiler_version": COMPILER_VERSION,
                    "module": module,
                    "status": "FAIL",
                    "mode": mode,
                    "summary": exc.summary,
                }
            )
            overall_exit = max(overall_exit, 1)

    if len(results) == 1:
        payload = results[0]
        if args.format == "json":
            print(_dump_json(payload), end="")
        else:
            if payload["status"] == "FAIL":
                if payload.get("drifts"):
                    for drift in payload["drifts"]:
                        print(f"DRIFT: {drift['relpath']} ({drift['reason']})")
                    print(f"FAIL: {len(payload['drifts'])} drift(s) detectado(s) no source graph derivado.")
                else:
                    print(f"FAIL: {payload['summary']}")
            elif args.check:
                print(f"OK: source graph `{payload['module']}` alinhado ao compiler determinístico.")
            else:
                if payload["written"]:
                    print("OK: artefatos gerados/atualizados:")
                    for relpath in payload["written"]:
                        print(f"  - {relpath}")
                else:
                    print("OK: nada a atualizar (generated/source_graph já está alinhado).")
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
            summary = payload.get("summary")
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
