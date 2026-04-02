from __future__ import annotations

# B8-002 — PACT_BROKER_BASE_URL e PACT_BROKER_TOKEN são variáveis CI-only.
# Elas NÃO fazem parte do .env da aplicação Django e NÃO são renderizadas por este script.
# São injetadas como GitHub Actions vars/secrets diretamente no job `contract-conformance`
# do deploy.yml (ADR-025). Qualquer alteração na política de acesso ao Pact Broker
# deve refletir em docs/_canon/graph/ops/environment_catalog.yaml.
# JWT_PRIVATE_KEY e JWT_PUBLIC_KEY, por outro lado, são runtime-secrets obrigatórios;
# se o par ativo for corrigido manualmente no VPS, ele deve ser espelhado nos GitHub
# secrets antes do próximo deploy para evitar regressão no renderer.

import argparse
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path


ASSIGNMENT_RE = re.compile(r"^([A-Z][A-Z0-9_]*)=(.*)$")
PLACEHOLDER_PREFIX = "CHANGE_ME_"


@dataclass(frozen=True)
class TemplateContext:
    template_path: Path
    fragment_path: Path
    template_lines: list[str]
    names_in_order: list[str]
    template_values: dict[str, str]
    fragment_values: dict[str, str]


def _repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "docs").exists() and (parent / ".contract_driven").exists():
            return parent
    return here.parents[2]


def _env_paths(root: Path, env_name: str) -> tuple[Path, Path]:
    return (
        root / "infra" / "env" / f".env.{env_name}.template",
        root / "compiled_ops" / "deploy" / f"{env_name}.env.fragment",
    )


def _parse_env_assignments(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for lineno, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        match = ASSIGNMENT_RE.match(raw_line)
        if not match:
            raise RuntimeError(f"{path}: linha {lineno} inválida; esperado VAR=valor.")
        values[match.group(1)] = match.group(2)
    return values


def _parse_template(path: Path) -> tuple[list[str], list[str], dict[str, str]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    names: list[str] = []
    values: dict[str, str] = {}
    for lineno, line in enumerate(lines, start=1):
        match = ASSIGNMENT_RE.match(line)
        if not match:
            continue
        name, value = match.groups()
        if name in values:
            raise RuntimeError(f"{path}: variável duplicada `{name}` na linha {lineno}.")
        names.append(name)
        values[name] = value
    if not names:
        raise RuntimeError(f"{path}: template não contém assignments.")
    return lines, names, values


def _load_context(root: Path, env_name: str) -> TemplateContext:
    template_path, fragment_path = _env_paths(root, env_name)
    if not template_path.exists():
        raise RuntimeError(f"Template ausente: {template_path}")
    if not fragment_path.exists():
        raise RuntimeError(f"Fragment ausente: {fragment_path}")

    template_lines, names_in_order, template_values = _parse_template(template_path)
    fragment_values = _parse_env_assignments(fragment_path)

    if names_in_order != list(fragment_values.keys()):
        raise RuntimeError(
            f"{template_path} e {fragment_path} divergem na ordem/lista de variáveis."
        )
    for name in names_in_order:
        if template_values[name] != fragment_values[name]:
            raise RuntimeError(
                f"{template_path} e {fragment_path} divergem no valor base de `{name}`."
            )

    return TemplateContext(
        template_path=template_path,
        fragment_path=fragment_path,
        template_lines=template_lines,
        names_in_order=names_in_order,
        template_values=template_values,
        fragment_values=fragment_values,
    )


def _is_unresolved(value: str | None) -> bool:
    return value is None or value == "" or value.startswith(PLACEHOLDER_PREFIX)


def _collect_overrides(
    names: list[str],
    process_env: dict[str, str] | None = None,
    cli_sets: list[str] | None = None,
) -> dict[str, str]:
    process_env = process_env or dict(os.environ)
    cli_sets = cli_sets or []

    overrides: dict[str, str] = {}
    for item in cli_sets:
        if "=" not in item:
            raise RuntimeError(f"--set inválido: {item!r}. Use NAME=VALUE.")
        name, value = item.split("=", 1)
        name = name.strip()
        if name not in names:
            raise RuntimeError(f"--set referencia variável fora do contrato: {name}")
        if value != "":
            overrides[name] = value

    for name in names:
        env_name = f"HB_ENV_{name}"
        value = process_env.get(env_name)
        if value:
            overrides[name] = value

    return overrides


def _apply_derivations(values: dict[str, str]) -> None:
    if _is_unresolved(values.get("POSTGRES_PASSWORD")) and not _is_unresolved(values.get("DB_PASSWORD")):
        values["POSTGRES_PASSWORD"] = values["DB_PASSWORD"]

    if _is_unresolved(values.get("CLOUDINARY_URL")):
        key = values.get("CLOUDINARY_API_KEY")
        secret = values.get("CLOUDINARY_API_SECRET")
        cloud = values.get("CLOUDINARY_CLOUD_NAME")
        if not _is_unresolved(key) and not _is_unresolved(secret) and not _is_unresolved(cloud):
            values["CLOUDINARY_URL"] = f"cloudinary://{key}:{secret}@{cloud}"


def resolve_env(
    *,
    root: Path,
    env_name: str,
    process_env: dict[str, str] | None = None,
    cli_sets: list[str] | None = None,
) -> tuple[TemplateContext, dict[str, str], list[str]]:
    context = _load_context(root, env_name)
    values = dict(context.fragment_values)
    values.update(_collect_overrides(context.names_in_order, process_env=process_env, cli_sets=cli_sets))
    _apply_derivations(values)
    unresolved = [name for name in context.names_in_order if _is_unresolved(values.get(name))]
    return context, values, unresolved


def render_env_content(
    *,
    root: Path,
    env_name: str,
    process_env: dict[str, str] | None = None,
    cli_sets: list[str] | None = None,
) -> str:
    context, values, unresolved = resolve_env(
        root=root,
        env_name=env_name,
        process_env=process_env,
        cli_sets=cli_sets,
    )
    if unresolved:
        raise RuntimeError(
            "Valores obrigatórios ausentes para "
            f"{env_name}: {', '.join(unresolved)}. "
            "Forneça `HB_ENV_<VAR>` ou `--set VAR=VALUE`."
        )

    rendered_lines: list[str] = []
    for line in context.template_lines:
        match = ASSIGNMENT_RE.match(line)
        if not match:
            rendered_lines.append(line)
            continue
        name = match.group(1)
        rendered_lines.append(f"{name}={values[name]}")
    return "\n".join(rendered_lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    root = _repo_root()
    parser = argparse.ArgumentParser(
        description=(
            "Renderiza .env resolvido a partir do template/fragment compilados do "
            "source graph operacional e dos valores reais fornecidos pelo ambiente."
        )
    )
    parser.add_argument("--env", required=True, choices=("staging", "production"))
    parser.add_argument("--output", required=True)
    parser.add_argument("--set", action="append", default=[])
    args = parser.parse_args(argv)

    try:
        rendered = render_env_content(
            root=root,
            env_name=args.env,
            process_env=dict(os.environ),
            cli_sets=args.set,
        )
    except RuntimeError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 2

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(rendered, encoding="utf-8")
    print(f"OK: .env renderizado em {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
