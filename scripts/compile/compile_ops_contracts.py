from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


COMPILER_NAME = "hbtrack_ops_contract_compiler"
COMPILER_VERSION = "0.1.0"
OPS_FILENAMES = (
    "environment_catalog.yaml",
    "secrets_catalog.yaml",
    "service_topology.yaml",
    "deploy_contract.yaml",
    "runtime_endpoints.yaml",
    "github_actions_catalog.yaml",
)
OUTPUTS = (
    "infra/env/.env.staging.template",
    "infra/env/.env.production.template",
    "compiled_ops/deploy/staging.env.fragment",
    "compiled_ops/deploy/production.env.fragment",
    "compiled_ops/deploy/secrets_catalog.json",
    "compiled_ops/deploy/runtime_topology.json",
    "compiled_ops/deploy/impact_report.json",
)


@dataclass(frozen=True)
class ExpectedFile:
    relpath: str
    content: str


@dataclass(frozen=True)
class Drift:
    relpath: str
    reason: str


class OpsContractsCompilerError(RuntimeError):
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
        raise OpsContractsCompilerError(f"Arquivo YAML ausente: {path}")
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(payload, dict):
        raise OpsContractsCompilerError(f"YAML inválido (esperado objeto): {path}")
    return payload


def _dump_json(data: dict[str, Any]) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def _ops_root(root: Path) -> Path:
    return root / "docs" / "_canon" / "graph" / "ops"


def _section_header(title: str) -> str:
    base = f"# ── {title} "
    return (base + ("─" * max(1, 78 - len(base)))).rstrip()


def _collect_input_paths(root: Path) -> list[Path]:
    ops_root = _ops_root(root)
    return [ops_root / filename for filename in OPS_FILENAMES]


def _required_template_variable_names(environment_catalog: dict[str, Any], env_name: str, output_path: str) -> set[str]:
    names: set[str] = set()
    for entry in environment_catalog["variables"]:
        required_in = set(entry.get("required_in", []))
        if env_name not in required_in:
            continue
        if output_path not in entry.get("sources", []):
            continue
        if entry.get("ci_only"):
            continue
        names.add(entry["name"])
    return names


def _render_env_template(template_doc: dict[str, Any]) -> str:
    lines = [
        "# ============================================================================",
        f"# {template_doc['title']}",
        f"# {template_doc['copy_instruction']}",
        "#",
        f"# {template_doc['warning_instruction']}",
        "# ============================================================================",
        "",
    ]
    for index, section in enumerate(template_doc["sections"]):
        lines.append(_section_header(section["title"]))
        for comment in section.get("comment_lines", []):
            lines.append(f"# {comment}")
        for entry in section["entries"]:
            lines.append(f"{entry['name']}={entry['value']}")
        if index != len(template_doc["sections"]) - 1:
            lines.append("")
    return "\n".join(lines) + "\n"


def _render_env_fragment(env_name: str, template_doc: dict[str, Any], source_relpath: str, catalog_version: str = "") -> str:
    version_line = f" | catalog_version: {catalog_version}" if catalog_version else ""
    lines = [
        f"# Generated from {source_relpath} [{env_name}]{version_line}",
        "# Do not edit manually.",
    ]
    for section in template_doc["sections"]:
        lines.extend(f"{entry['name']}={entry['value']}" for entry in section["entries"])
    return "\n".join(lines) + "\n"


def _compute_template_parity_hints(environment_catalog: dict[str, Any]) -> list[dict[str, Any]]:
    hints: list[dict[str, Any]] = []
    template_contracts = environment_catalog["template_contracts"]
    for env_name in ("staging", "production"):
        env_contract = environment_catalog["environments"][env_name]
        template_doc = template_contracts[env_name]
        values = {
            entry["name"]: entry["value"]
            for section in template_doc["sections"]
            for entry in section["entries"]
        }
        expected_hosts = set(env_contract.get("hostnames", []))
        allowed_hosts = {
            item.strip()
            for item in values.get("ALLOWED_HOSTS", "").split(",")
            if item.strip()
        }
        if expected_hosts != allowed_hosts:
            hints.append(
                {
                    "type": "allowed_hosts_mismatch",
                    "environment": env_name,
                    "expected_hosts": sorted(expected_hosts),
                    "template_hosts": sorted(allowed_hosts),
                }
            )

        cors_origins = {
            item.strip()
            for item in values.get("CORS_ALLOWED_ORIGINS", "").split(",")
            if item.strip()
        }
        expected_origin = env_contract["urls"]["docs"].rsplit("/api/docs", 1)[0]
        if expected_origin and expected_origin not in cors_origins:
            hints.append(
                {
                    "type": "cors_origin_mismatch",
                    "environment": env_name,
                    "expected_origin": expected_origin,
                    "template_origins": sorted(cors_origins),
                }
            )
    return hints


def _validate_payloads(
    *,
    root: Path,
    environment_catalog: dict[str, Any],
    secrets_catalog: dict[str, Any],
    service_topology: dict[str, Any],
    deploy_contract: dict[str, Any],
    runtime_endpoints: dict[str, Any],
    github_actions_catalog: dict[str, Any],
) -> None:
    expected_artifacts = {
        "environment_catalog.yaml": "OPS_ENVIRONMENT_CATALOG",
        "secrets_catalog.yaml": "OPS_SECRETS_CATALOG",
        "service_topology.yaml": "OPS_SERVICE_TOPOLOGY",
        "deploy_contract.yaml": "OPS_DEPLOY_CONTRACT",
        "runtime_endpoints.yaml": "OPS_RUNTIME_ENDPOINTS",
        "github_actions_catalog.yaml": "OPS_GITHUB_ACTIONS_CATALOG",
    }
    ops_root = _ops_root(root)
    for filename, artifact in expected_artifacts.items():
        payload = _load_yaml(ops_root / filename)
        if payload.get("artifact") != artifact:
            raise OpsContractsCompilerError(f"{filename} deve declarar artifact={artifact}.")
        if payload.get("status") != "active":
            raise OpsContractsCompilerError(f"{filename} deve estar com status=active.")

    environments = environment_catalog.get("environments", {})
    if set(environments.keys()) != {"development", "staging", "production"}:
        raise OpsContractsCompilerError("environment_catalog precisa cobrir development/staging/production.")

    template_contracts = environment_catalog.get("template_contracts")
    if not isinstance(template_contracts, dict):
        raise OpsContractsCompilerError("environment_catalog precisa declarar template_contracts.")

    variable_map = {entry["name"]: entry for entry in environment_catalog.get("variables", [])}
    if not variable_map:
        raise OpsContractsCompilerError("environment_catalog precisa declarar variables não vazias.")

    def _require_rotation_metadata(entry: dict[str, Any], *, artifact_label: str, name: str) -> None:
        if not isinstance(entry.get("rotation_ref"), str) or not entry["rotation_ref"].strip():
            raise OpsContractsCompilerError(f"{artifact_label} `{name}` precisa declarar rotation_ref.")
        if not isinstance(entry.get("rotation_command_ref"), str) or not entry["rotation_command_ref"].strip():
            raise OpsContractsCompilerError(f"{artifact_label} `{name}` precisa declarar rotation_command_ref.")
        command_ref = root / str(entry["rotation_command_ref"])
        if not command_ref.exists():
            raise OpsContractsCompilerError(
                f"{artifact_label} `{name}` aponta para rotation_command_ref inexistente: {entry['rotation_command_ref']}."
            )
        period = entry.get("rotation_period_days")
        if not isinstance(period, int) or period <= 0:
            raise OpsContractsCompilerError(f"{artifact_label} `{name}` precisa declarar rotation_period_days > 0.")
        actor = entry.get("rotation_actor")
        if not isinstance(actor, str) or not actor.strip():
            raise OpsContractsCompilerError(f"{artifact_label} `{name}` precisa declarar rotation_actor.")
        rotate_on = entry.get("rotate_on")
        if not isinstance(rotate_on, list) or not rotate_on or not all(isinstance(item, str) and item.strip() for item in rotate_on):
            raise OpsContractsCompilerError(f"{artifact_label} `{name}` precisa declarar rotate_on não vazio.")

    for env_name in ("staging", "production"):
        env_contract = environments[env_name]
        template_doc = template_contracts.get(env_name)
        if not isinstance(template_doc, dict):
            raise OpsContractsCompilerError(f"template_contracts.{env_name} ausente.")

        output_path = template_doc.get("output_path")
        if output_path not in env_contract.get("env_templates", []):
            raise OpsContractsCompilerError(
                f"template_contracts.{env_name}.output_path deve constar em environments.{env_name}.env_templates."
            )

        seen_names: list[str] = []
        sections = template_doc.get("sections")
        if not isinstance(sections, list) or not sections:
            raise OpsContractsCompilerError(f"template_contracts.{env_name}.sections deve ser lista não vazia.")

        for section in sections:
            entries = section.get("entries")
            if not isinstance(entries, list) or not entries:
                raise OpsContractsCompilerError(f"template_contracts.{env_name} contém seção sem entries.")
            for entry in entries:
                name = entry.get("name")
                value = entry.get("value")
                if name not in variable_map:
                    raise OpsContractsCompilerError(
                        f"template_contracts.{env_name} referencia variável não catalogada: {name}."
                    )
                if not isinstance(value, str) or not value:
                    raise OpsContractsCompilerError(
                        f"template_contracts.{env_name}.{name} precisa de value string não vazia."
                    )
                seen_names.append(name)

        if len(seen_names) != len(set(seen_names)):
            raise OpsContractsCompilerError(f"template_contracts.{env_name} contém variáveis duplicadas.")

        required_names = _required_template_variable_names(environment_catalog, env_name, output_path)
        seen_name_set = set(seen_names)
        if required_names != seen_name_set:
            missing = sorted(required_names - seen_name_set)
            extras = sorted(seen_name_set - required_names)
            raise OpsContractsCompilerError(
                f"template_contracts.{env_name} diverge das variáveis obrigatórias. missing={missing} extras={extras}"
            )

        nginx_entry = next(
            (entry["value"]
            for section in sections
            for entry in section["entries"]
            if entry["name"] == "NGINX_CONF"),
            None,
        )
        if nginx_entry is None:
            raise OpsContractsCompilerError(
                f"template_contracts.{env_name} não contém entrada NGINX_CONF em nenhuma seção."
            )
        expected_nginx_name = Path(env_contract["nginx_conf"]).name
        if nginx_entry != expected_nginx_name:
            raise OpsContractsCompilerError(
                f"template_contracts.{env_name}.NGINX_CONF deve ser {expected_nginx_name}."
            )

    if "runtime_secrets" not in secrets_catalog or not secrets_catalog["runtime_secrets"]:
        raise OpsContractsCompilerError("secrets_catalog precisa declarar runtime_secrets.")
    github_secrets = ((secrets_catalog.get("github_actions") or {}).get("secrets") or [])
    if not isinstance(github_secrets, list) or not github_secrets:
        raise OpsContractsCompilerError("secrets_catalog.github_actions.secrets precisa ser lista não vazia.")
    for item in github_secrets:
        if not isinstance(item, dict):
            raise OpsContractsCompilerError("secrets_catalog.github_actions.secrets deve conter mappings.")
        name = item.get("name")
        kind = item.get("kind")
        if not isinstance(name, str) or not name.strip():
            raise OpsContractsCompilerError("Todo github_actions secret precisa declarar name.")
        if kind in {"ssh_credential", "ssh_private_key", "runtime_environment_secret", "contract_broker_credential"}:
            _require_rotation_metadata(item, artifact_label="github_actions secret", name=name)
    for item in secrets_catalog["runtime_secrets"]:
        if not isinstance(item, dict):
            raise OpsContractsCompilerError("secrets_catalog.runtime_secrets deve conter mappings.")
        name = item.get("name")
        if not isinstance(name, str) or not name.strip():
            raise OpsContractsCompilerError("Todo runtime_secret precisa declarar name.")
        _require_rotation_metadata(item, artifact_label="runtime_secret", name=name)
    if "services" not in service_topology or not service_topology["services"]:
        raise OpsContractsCompilerError("service_topology precisa declarar services.")
    if (
        "promotion_flow" not in deploy_contract
        or "health_checks" not in deploy_contract
        or "env_rendering" not in deploy_contract
    ):
        raise OpsContractsCompilerError(
            "deploy_contract precisa declarar promotion_flow, health_checks e env_rendering."
        )
    env_rendering = deploy_contract["env_rendering"]
    if not isinstance(env_rendering, dict):
        raise OpsContractsCompilerError("deploy_contract.env_rendering precisa ser mapping.")
    for key in ("renderer_ref", "injector_ref", "generated_targets"):
        if key not in env_rendering:
            raise OpsContractsCompilerError(f"deploy_contract.env_rendering precisa declarar {key}.")
    if "endpoints" not in runtime_endpoints or not runtime_endpoints["endpoints"]:
        raise OpsContractsCompilerError("runtime_endpoints precisa declarar endpoints.")
    deploy_pipeline = github_actions_catalog.get("workflows", {}).get("deploy_pipeline")
    if not deploy_pipeline:
        raise OpsContractsCompilerError("github_actions_catalog precisa declarar workflows.deploy_pipeline.")


def _build_secrets_catalog(
    *,
    root: Path,
    secrets_catalog: dict[str, Any],
    environment_catalog: dict[str, Any],
    github_actions_catalog: dict[str, Any],
) -> dict[str, Any]:
    return {
        "artifact_id": "HBTRACK_OPS_SECRETS_DERIVED",
        "compiler": COMPILER_NAME,
        "compiler_version": COMPILER_VERSION,
        "source_ref": _rel(root, _ops_root(root) / "secrets_catalog.yaml"),
        "github_actions_workflow_ref": github_actions_catalog["workflows"]["deploy_pipeline"]["workflow_ref"],
        "github_actions": secrets_catalog["github_actions"],
        "runtime_secrets": secrets_catalog["runtime_secrets"],
        "runtime_env_templates": {
            env_name: environment_catalog["template_contracts"][env_name]["output_path"]
            for env_name in ("staging", "production")
        },
    }


def _build_runtime_topology(
    *,
    root: Path,
    environment_catalog: dict[str, Any],
    service_topology: dict[str, Any],
    deploy_contract: dict[str, Any],
    runtime_endpoints: dict[str, Any],
) -> dict[str, Any]:
    return {
        "artifact_id": "HBTRACK_OPS_RUNTIME_TOPOLOGY",
        "compiler": COMPILER_NAME,
        "compiler_version": COMPILER_VERSION,
        "source_refs": [
            _rel(root, _ops_root(root) / "environment_catalog.yaml"),
            _rel(root, _ops_root(root) / "service_topology.yaml"),
            _rel(root, _ops_root(root) / "deploy_contract.yaml"),
            _rel(root, _ops_root(root) / "runtime_endpoints.yaml"),
        ],
        "environments": environment_catalog["environments"],
        "services": service_topology["services"],
        "runtime_endpoints": runtime_endpoints["endpoints"],
        "deploy_contract": {
            "pre_checks": deploy_contract["pre_checks"],
            "health_checks": deploy_contract["health_checks"],
            "promotion_flow": deploy_contract["promotion_flow"],
            "rollback": deploy_contract["rollback"],
            "env_rendering": deploy_contract["env_rendering"],
        },
    }


def _build_impact_report(
    *,
    root: Path,
    environment_catalog: dict[str, Any],
    deploy_contract: dict[str, Any],
    outputs: list[str],
) -> dict[str, Any]:
    input_refs = [
        {
            "relpath": _rel(root, path),
            "sha256": _sha256_bytes(path.read_bytes()),
        }
        for path in _collect_input_paths(root)
    ]
    input_map = {item["relpath"]: item["sha256"] for item in input_refs}
    sync_manifest = _load_yaml(root / "docs" / "_canon" / "SYNC_MANIFEST.yaml")
    ops_sync_rule = next(rule for rule in sync_manifest["rules"] if rule["rule_id"] == "OPS_SOURCE_GRAPH_SYNC")
    template_parity_hints = _compute_template_parity_hints(environment_catalog)

    return {
        "artifact_id": "HBTRACK_OPS_IMPACT_REPORT",
        "compiler": COMPILER_NAME,
        "compiler_version": COMPILER_VERSION,
        "scope": "operations",
        "blocked_partial_update": True,
        "source_fingerprint": _sha256_text(json.dumps(input_map, sort_keys=True)),
        "inputs": input_refs,
        "upstream_operational_inputs": ops_sync_rule["source_inputs"],
        "outputs": outputs,
        "impacted_modules": [],
        "impacted_domains": ["operations"],
        "regenerated_contracts": [
            "infra/env/.env.staging.template",
            "infra/env/.env.production.template",
            "compiled_ops/deploy/secrets_catalog.json",
            "compiled_ops/deploy/runtime_topology.json",
        ],
        "regenerated_agent_bundles": [],
        "required_tests": [
            "python3 scripts/compile/compile_ops_contracts.py --check",
            "python3 -m pytest tests/pipeline_gates/test_ops_contract_compiler.py -q",
            "python3 scripts/validate_contracts.py --profile ci",
        ],
        "obsolete_artifacts": [],
        "known_deviations": deploy_contract.get("known_deviations", []),
        "template_parity_hints": template_parity_hints,
    }


def compile_expected(root: Path) -> list[ExpectedFile]:
    ops_root = _ops_root(root)
    if not ops_root.exists():
        raise OpsContractsCompilerError(f"Ops graph ausente: {ops_root}")

    environment_catalog = _load_yaml(ops_root / "environment_catalog.yaml")
    secrets_catalog = _load_yaml(ops_root / "secrets_catalog.yaml")
    service_topology = _load_yaml(ops_root / "service_topology.yaml")
    deploy_contract = _load_yaml(ops_root / "deploy_contract.yaml")
    runtime_endpoints = _load_yaml(ops_root / "runtime_endpoints.yaml")
    github_actions_catalog = _load_yaml(ops_root / "github_actions_catalog.yaml")

    _validate_payloads(
        root=root,
        environment_catalog=environment_catalog,
        secrets_catalog=secrets_catalog,
        service_topology=service_topology,
        deploy_contract=deploy_contract,
        runtime_endpoints=runtime_endpoints,
        github_actions_catalog=github_actions_catalog,
    )

    staging_template = _render_env_template(environment_catalog["template_contracts"]["staging"])
    production_template = _render_env_template(environment_catalog["template_contracts"]["production"])
    staging_fragment = _render_env_fragment(
        "staging",
        environment_catalog["template_contracts"]["staging"],
        "docs/_canon/graph/ops/environment_catalog.yaml",
        catalog_version=environment_catalog.get("version", ""),
    )
    production_fragment = _render_env_fragment(
        "production",
        environment_catalog["template_contracts"]["production"],
        "docs/_canon/graph/ops/environment_catalog.yaml",
        catalog_version=environment_catalog.get("version", ""),
    )

    secrets_catalog_payload = _build_secrets_catalog(
        root=root,
        secrets_catalog=secrets_catalog,
        environment_catalog=environment_catalog,
        github_actions_catalog=github_actions_catalog,
    )
    runtime_topology_payload = _build_runtime_topology(
        root=root,
        environment_catalog=environment_catalog,
        service_topology=service_topology,
        deploy_contract=deploy_contract,
        runtime_endpoints=runtime_endpoints,
    )
    impact_report = _build_impact_report(
        root=root,
        environment_catalog=environment_catalog,
        deploy_contract=deploy_contract,
        outputs=list(OUTPUTS),
    )

    return [
        ExpectedFile(OUTPUTS[0], staging_template),
        ExpectedFile(OUTPUTS[1], production_template),
        ExpectedFile(OUTPUTS[2], staging_fragment),
        ExpectedFile(OUTPUTS[3], production_fragment),
        ExpectedFile(OUTPUTS[4], _dump_json(secrets_catalog_payload)),
        ExpectedFile(OUTPUTS[5], _dump_json(runtime_topology_payload)),
        ExpectedFile(OUTPUTS[6], _dump_json(impact_report)),
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

    compiled_dir = root / "compiled_ops" / "deploy"
    if compiled_dir.exists():
        expected_paths = {item.relpath for item in expected if item.relpath.startswith("compiled_ops/deploy/")}
        for extra in sorted(path for path in compiled_dir.glob("*") if path.is_file()):
            relpath = _rel(root, extra)
            if relpath not in expected_paths:
                drifts.append(Drift(relpath, "unexpected_extra_file"))

    return drifts


def _format_payload(status: str, mode: str, *, written: list[str] | None = None, drifts: list[Drift] | None = None) -> dict[str, Any]:
    return {
        "artifact_id": "HBTRACK_OPS_COMPILER_RESULT",
        "compiler": COMPILER_NAME,
        "compiler_version": COMPILER_VERSION,
        "scope": "operations",
        "status": status,
        "mode": mode,
        "written": written or [],
        "drifts": [{"relpath": item.relpath, "reason": item.reason} for item in (drifts or [])],
    }


def main(argv: list[str] | None = None) -> int:
    root = _repo_root()
    ap = argparse.ArgumentParser(description="Compila contratos operacionais e gera derivados determinísticos em infra/env/ e compiled_ops/.")
    ap.add_argument("--check", action="store_true", help="Não escreve; apenas verifica drift.")
    ap.add_argument("--format", choices=("text", "json"), default="text", help="Formato de saída.")
    args = ap.parse_args(argv)

    try:
        expected = compile_expected(root)
        if args.check:
            drifts = check_expected(root, expected)
            if drifts:
                payload = _format_payload("FAIL", "check", drifts=drifts)
                if args.format == "json":
                    print(_dump_json(payload), end="")
                else:
                    for drift in drifts:
                        print(f"DRIFT: {drift.relpath} ({drift.reason})")
                    print(f"FAIL: {len(drifts)} drift(s) detectado(s) nos contratos operacionais derivados.")
                return 2

            payload = _format_payload("PASS", "check")
            if args.format == "json":
                print(_dump_json(payload), end="")
            else:
                print("OK: contratos operacionais alinhados ao compiler determinístico.")
            return 0

        written = write_expected(root, expected)
        payload = _format_payload("PASS", "write", written=written)
        if args.format == "json":
            print(_dump_json(payload), end="")
        else:
            if written:
                print("OK: artefatos operacionais gerados/atualizados:")
                for relpath in written:
                    print(f"  - {relpath}")
            else:
                print("OK: nada a atualizar (artefatos operacionais já estão alinhados).")
        return 0
    except OpsContractsCompilerError as exc:
        payload = {
            "artifact_id": "HBTRACK_OPS_COMPILER_RESULT",
            "compiler": COMPILER_NAME,
            "compiler_version": COMPILER_VERSION,
            "scope": "operations",
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
