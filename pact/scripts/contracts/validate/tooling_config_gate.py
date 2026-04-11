from __future__ import annotations

import argparse
import json
import pathlib
import re
from typing import Any


SUPPORTED_PACKAGE_MAJORS: dict[str, set[int]] = {
    "@redocly/cli": {1},
    "@stoplight/spectral-cli": {6},
    "@asyncapi/cli": {6},
}


def _repo_root() -> pathlib.Path:
    here = pathlib.Path(__file__).resolve()
    for parent in here.parents:
        if (parent / ".git").exists():
            return parent
        if (parent / "contracts").exists() and (parent / ".contract_driven").exists():
            return parent
    return here.parents[3]


def _load_json(path: pathlib.Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_yaml(path: pathlib.Path) -> dict[str, Any]:
    import yaml

    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def _parse_major(value: str | None) -> int | None:
    if not isinstance(value, str):
        return None
    match = re.search(r"(\d+)(?:\.\d+){0,2}", value)
    if not match:
        return None
    return int(match.group(1))


def _resolve_redocly_roots(config: dict[str, Any]) -> list[str]:
    apis = config.get("apis")
    if not isinstance(apis, dict):
        return []
    roots: list[str] = []
    for entry in apis.values():
        if not isinstance(entry, dict):
            continue
        root = entry.get("root")
        if isinstance(root, str) and root.strip():
            roots.append(root.strip())
    return roots


def evaluate_tooling_config(
    root: pathlib.Path,
    *,
    tool_versions: dict[str, str | None] | None = None,
    is_ci: bool = False,
) -> dict[str, Any]:
    package_path = root / "package.json"
    redocly_path = root / "redocly.yaml"
    health_policy_path = root / "docs" / "_canon" / "TOOLCHAIN_HEALTH_POLICY.md"
    checked = [str(package_path), str(redocly_path), str(health_policy_path)]
    violations: list[dict[str, Any]] = []
    degraded: list[dict[str, Any]] = []

    if not package_path.exists():
        violations.append({
            "blocking_code": "TOOLING_CONFIG_INVALID",
            "artifact": "package.json",
            "message": "package.json ausente — não é possível validar a matrix de tooling.",
            "severity": "error",
        })
        return {"status": "FAIL", "checked": checked, "violations": violations}

    if not redocly_path.exists():
        violations.append({
            "blocking_code": "TOOLING_CONFIG_INVALID",
            "artifact": "redocly.yaml",
            "message": "redocly.yaml ausente.",
            "severity": "error",
        })
        return {"status": "FAIL", "checked": checked, "violations": violations}

    try:
        package = _load_json(package_path)
    except Exception as exc:
        violations.append({
            "blocking_code": "TOOLING_CONFIG_INVALID",
            "artifact": "package.json",
            "message": f"package.json inválido: {exc}",
            "severity": "error",
        })
        return {"status": "FAIL", "checked": checked, "violations": violations}

    try:
        redocly = _load_yaml(redocly_path)
    except Exception as exc:
        violations.append({
            "blocking_code": "TOOLING_CONFIG_INVALID",
            "artifact": "redocly.yaml",
            "message": f"redocly.yaml inválido: {exc}",
            "severity": "error",
        })
        return {"status": "FAIL", "checked": checked, "violations": violations}

    package_tools = {
        **(package.get("dependencies") or {}),
        **(package.get("devDependencies") or {}),
    }

    for package_name, supported_majors in SUPPORTED_PACKAGE_MAJORS.items():
        raw = package_tools.get(package_name)
        major = _parse_major(raw)
        if raw is None:
            violations.append({
                "blocking_code": "TOOLING_CONFIG_INVALID",
                "artifact": "package.json",
                "message": f"{package_name} ausente em dependencies/devDependencies.",
                "severity": "error",
            })
            continue
        if major not in supported_majors:
            violations.append({
                "blocking_code": "TOOLING_CONFIG_INVALID",
                "artifact": "package.json",
                "message": f"{package_name} usa major {major!r}; suportado: {sorted(supported_majors)}.",
                "severity": "error",
            })

    roots = _resolve_redocly_roots(redocly)
    if not roots:
        violations.append({
            "blocking_code": "TOOLING_CONFIG_INVALID",
            "artifact": "redocly.yaml",
            "message": "redocly.yaml não declara `apis.*.root`.",
            "severity": "error",
        })
    for rel_root in roots:
        openapi_root = root / rel_root
        checked.append(str(openapi_root))
        if not openapi_root.exists():
            violations.append({
                "blocking_code": "TOOLING_CONFIG_INVALID",
                "artifact": "redocly.yaml",
                "message": f"Redocly referencia root inexistente: {rel_root}",
                "severity": "error",
            })

    versions = tool_versions or {}

    def _check_installed(tool_name: str, package_name: str | None, *, allow_local_degraded: bool, compare_major: bool = True) -> None:
        package_major = _parse_major(package_tools.get(package_name)) if package_name else None
        installed_version = versions.get(tool_name)
        installed_major = _parse_major(installed_version)
        if installed_version is None:
            payload = {
                "blocking_code": "ERROR_INFRA",
                "artifact": tool_name,
                "message": f"{tool_name} não disponível no ambiente.",
                "severity": "error" if is_ci or not allow_local_degraded else "warn",
            }
            if is_ci or not allow_local_degraded:
                violations.append(payload)
            else:
                degraded.append(payload)
            return
        if compare_major and package_major is not None and installed_major is not None and package_major != installed_major:
            violations.append({
                "blocking_code": "TOOLING_CONFIG_INVALID",
                "artifact": tool_name,
                "message": f"{tool_name} instalado em major {installed_major}, mas package.json declara major {package_major}.",
                "severity": "error",
            })

    _check_installed("redocly", "@redocly/cli", allow_local_degraded=False)
    _check_installed("spectral", "@stoplight/spectral-cli", allow_local_degraded=False)
    _check_installed("asyncapi", "@asyncapi/cli", allow_local_degraded=False)
    _check_installed("oasdiff", None, allow_local_degraded=True, compare_major=False)
    _check_installed("schemathesis", None, allow_local_degraded=True, compare_major=False)

    if violations:
        return {"status": "FAIL", "checked": checked, "violations": violations + degraded}
    if degraded:
        return {"status": "DEGRADED", "checked": checked, "violations": degraded}
    return {"status": "PASS", "checked": checked, "violations": []}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Valida compatibilidade de tooling/config antes dos gates semânticos.")
    parser.add_argument("--json", action="store_true", help="Imprime saída machine-readable.")
    parser.add_argument("--ci", action="store_true", help="Força modo CI.")
    args = parser.parse_args(argv)

    root = _repo_root()
    result = evaluate_tooling_config(root, is_ci=args.ci)
    if args.json:
        print(json.dumps(result, ensure_ascii=False))
    else:
        print(f"STATUS={result['status']}")
        for violation in result.get("violations") or []:
            print(f"- {violation['artifact']}: {violation['message']}")

    return 0 if result["status"] in {"PASS", "DEGRADED"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
