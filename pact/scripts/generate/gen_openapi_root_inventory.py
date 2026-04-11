from __future__ import annotations

import argparse
import pathlib
import re
import sys
from dataclasses import dataclass

import yaml


_PATHS_BLOCK_RE = re.compile(r"(?ms)^paths:\n.*?\n(?=components:\n)")


@dataclass(frozen=True)
class OpenApiRootSyncResult:
    relpath: str
    changed: bool
    reason: str | None = None


def _repo_root() -> pathlib.Path:
    here = pathlib.Path(__file__).resolve()
    for parent in here.parents:
        if (parent / ".git").exists():
            return parent
        if (parent / "contracts").exists() and (parent / ".contract_driven").exists():
            return parent
    return here.parents[2]


def _load_module_order(root: pathlib.Path) -> list[str]:
    registry_path = root / "docs" / "_canon" / "MODULE_REGISTRY.yaml"
    if registry_path.exists():
        data = yaml.safe_load(registry_path.read_text(encoding="utf-8")) or {}
        modules = data.get("modules")
        if isinstance(modules, dict):
            return list(modules.keys())

    paths_dir = root / "contracts" / "openapi" / "paths"
    return sorted(p.stem for p in paths_dir.glob("*.yaml"))


def _load_module_paths(path_file: pathlib.Path) -> list[str]:
    try:
        data = yaml.safe_load(path_file.read_text(encoding="utf-8"))
    except Exception:
        return []
    if not isinstance(data, dict):
        return []
    return [key for key in data.keys() if isinstance(key, str) and key.startswith("/")]


def _json_pointer(path_value: str) -> str:
    return path_value.replace("~", "~0").replace("/", "~1")


def render_paths_block(root: pathlib.Path) -> str:
    modules = _load_module_order(root)
    lines: list[str] = ["paths:"]
    lines.append("  # GENERATED PATH INVENTORY — do not edit manually.")
    lines.append("  # Source: scripts/generate/gen_openapi_root_inventory.py")

    emitted_modules = 0
    for module in modules:
        path_file = root / "contracts" / "openapi" / "paths" / f"{module}.yaml"
        if not path_file.exists():
            continue
        real_paths = _load_module_paths(path_file)
        if not real_paths:
            continue
        emitted_modules += 1
        lines.append(f"  # {module} module - path items defined in ./paths/{module}.yaml")
        for path_value in real_paths:
            lines.append(f"  {path_value}:")
            lines.append(f"    $ref: ./paths/{module}.yaml#/{_json_pointer(path_value)}")

    if emitted_modules == 0:
        lines.append("  {}")

    return "\n".join(lines) + "\n"


def render_openapi_root(root: pathlib.Path) -> str:
    openapi_root = root / "contracts" / "openapi" / "openapi.yaml"
    original = openapi_root.read_text(encoding="utf-8")
    rendered_paths = render_paths_block(root)
    if not _PATHS_BLOCK_RE.search(original):
        raise RuntimeError("Não foi possível localizar o bloco `paths:` → `components:` em contracts/openapi/openapi.yaml.")
    return _PATHS_BLOCK_RE.sub(rendered_paths, original, count=1)


def sync_openapi_root(root: pathlib.Path, *, check_only: bool) -> OpenApiRootSyncResult:
    relpath = "contracts/openapi/openapi.yaml"
    openapi_root = root / relpath
    rendered = render_openapi_root(root)
    current = openapi_root.read_text(encoding="utf-8")
    changed = current != rendered
    if check_only:
        return OpenApiRootSyncResult(
            relpath=relpath,
            changed=changed,
            reason="openapi_root_inventory_out_of_sync" if changed else None,
        )
    if changed:
        openapi_root.write_text(rendered, encoding="utf-8")
    return OpenApiRootSyncResult(relpath=relpath, changed=changed)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compõe o inventory de paths do OpenAPI root a partir dos path files modulares.")
    parser.add_argument("--check", action="store_true", help="Falha com exit 2 quando o root OpenAPI estiver fora de sincronia.")
    args = parser.parse_args(argv)

    root = _repo_root()
    result = sync_openapi_root(root, check_only=args.check)
    if args.check:
        if result.changed:
            print(f"DRIFT: {result.relpath} ({result.reason})")
            return 2
        print("OK: openapi root inventory alinhado aos módulos.")
        return 0

    if result.changed:
        print(f"OK: atualizado {result.relpath}.")
    else:
        print("OK: openapi root inventory já estava alinhado.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
