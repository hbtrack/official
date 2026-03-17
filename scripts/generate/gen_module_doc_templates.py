from __future__ import annotations

import argparse
import json
import pathlib
import re
from collections import OrderedDict

import yaml


_FRONT_MATTER_RE = re.compile(r"(?ms)^---\n.*?\n---\n")


def _repo_root() -> pathlib.Path:
    here = pathlib.Path(__file__).resolve()
    for parent in here.parents:
        if (parent / ".git").exists():
            return parent
        if (parent / ".contract_driven").exists() and (parent / "scripts").exists():
            return parent
    return here.parents[2]


def _policy_path(root: pathlib.Path) -> pathlib.Path:
    return root / ".contract_driven" / "templates" / "modulos" / "MODULE_DOC_HEADER_POLICY.yaml"


def _load_policy(root: pathlib.Path) -> dict:
    return yaml.safe_load(_policy_path(root).read_text(encoding="utf-8")) or {}


def _type_by_template_name(name: str, policy: dict) -> str | None:
    for doc_type, cfg in (policy.get("types") or {}).items():
        for pattern in cfg.get("filenames") or []:
            candidate = pattern.replace("{module_upper}", "{{MODULE_NAME_UPPER}}")
            if candidate == name:
                return doc_type
    return None


def _scalar(value: str | bool) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if value == "{{HANDBALL_SEMANTIC_APPLICABILITY}}":
        return value
    return json.dumps(value, ensure_ascii=False)


def _render_header(doc_type: str, template_name: str) -> str:
    common = OrderedDict([
        ("module", "{{MODULE_NAME}}"),
        ("system_scope_ref", "../../../_canon/SYSTEM_SCOPE.md"),
        ("handball_rules_ref", "../../../_canon/HANDBALL_RULES_DOMAIN.md"),
        ("handball_semantic_applicability", "{{HANDBALL_SEMANTIC_APPLICABILITY}}"),
        ("type", doc_type),
    ])

    per_type: dict[str, OrderedDict[str, str | bool]] = {
        "readme": OrderedDict([
            ("module_scope_ref", "./MODULE_SCOPE_{{MODULE_NAME_UPPER}}.md"),
            ("domain_rules_ref", "./DOMAIN_RULES_{{MODULE_NAME_UPPER}}.md"),
            ("invariants_ref", "./INVARIANTS_{{MODULE_NAME_UPPER}}.md"),
            ("test_matrix_ref", "./TEST_MATRIX_{{MODULE_NAME_UPPER}}.md"),
            ("contract_path_ref", "../../../../contracts/openapi/paths/{{MODULE_NAME}}.yaml"),
            ("schemas_ref", "../../../../contracts/schemas/{{MODULE_NAME}}/"),
        ]),
        "module-scope": OrderedDict([
            ("contract_path_ref", "../../../../contracts/openapi/paths/{{MODULE_NAME}}.yaml"),
            ("schemas_ref", "../../../../contracts/schemas/{{MODULE_NAME}}/"),
        ]),
        "domain-rules": OrderedDict([
            ("contract_path_ref", "../../../../contracts/openapi/paths/{{MODULE_NAME}}.yaml"),
            ("schemas_ref", "../../../../contracts/schemas/{{MODULE_NAME}}/"),
        ]),
        "invariants": OrderedDict([
            ("contract_path_ref", "../../../../contracts/openapi/paths/{{MODULE_NAME}}.yaml"),
            ("schemas_ref", "../../../../contracts/schemas/{{MODULE_NAME}}/"),
        ]),
        "test-matrix": OrderedDict([
            ("contract_path_ref", "../../../../contracts/openapi/paths/{{MODULE_NAME}}.yaml"),
            ("schemas_ref", "../../../../contracts/schemas/{{MODULE_NAME}}/"),
        ]),
        "state-model": OrderedDict([
            ("contract_path_ref", "../../../../contracts/openapi/paths/{{MODULE_NAME}}.yaml"),
            ("schemas_ref", "../../../../contracts/schemas/{{MODULE_NAME}}/"),
            ("diagram_format", "mermaid"),
            ("adr_ref", "../../../../docs/_canon/decisions/ADR-017-training-session-state-machine.md"),
        ]),
        "permissions": OrderedDict([
            ("domain_rules_ref", "./DOMAIN_RULES_{{MODULE_NAME_UPPER}}.md"),
            ("invariants_ref", "./INVARIANTS_{{MODULE_NAME_UPPER}}.md"),
        ]),
        "errors": OrderedDict([
            ("error_model_ref", "../../../../docs/_canon/ERROR_MODEL.md"),
            ("problem_schema_ref", "../../../../contracts/openapi/components/schemas/shared/problem.yaml"),
        ]),
        "sport-science-rules": OrderedDict([
            ("contract_path_ref", "../../../../contracts/openapi/paths/{{MODULE_NAME}}.yaml"),
            ("schemas_ref", "../../../../contracts/schemas/{{MODULE_NAME}}/"),
        ]),
        "ui-contract": OrderedDict([
            ("contract_path_ref", "../../../../contracts/openapi/paths/{{MODULE_NAME}}.yaml"),
            ("schemas_ref", "../../../../contracts/schemas/{{MODULE_NAME}}/"),
            ("module_scope_ref", "./MODULE_SCOPE_{{MODULE_NAME_UPPER}}.md"),
        ]),
        "screen-map": OrderedDict([
            ("module_scope_ref", "./MODULE_SCOPE_{{MODULE_NAME_UPPER}}.md"),
            ("ui_contract_ref", "./UI_CONTRACT_{{MODULE_NAME_UPPER}}.md"),
            ("diagram_format", "mermaid"),
        ]),
    }
    if doc_type not in per_type:
        raise KeyError(f"Tipo de doc não suportado pelo generator: {doc_type}")

    lines = [
        "---",
        "# TEMPLATE: module-doc-template",
        f"# DEST: docs/hbtrack/modulos/<module>/{template_name}",
        f"# SOURCE: .contract_driven/templates/modulos/{template_name}",
    ]
    for key, value in common.items():
        lines.append(f"{key}: {_scalar(value)}")
    for key, value in per_type[doc_type].items():
        lines.append(f"{key}: {_scalar(value)}")
    lines.append("---")
    return "\n".join(lines) + "\n"


def _update_template(path: pathlib.Path, policy: dict, *, check_only: bool) -> bool:
    doc_type = _type_by_template_name(path.name, policy)
    if not doc_type:
        return False

    original = path.read_text(encoding="utf-8")
    new_header = _render_header(doc_type, path.name)
    if _FRONT_MATTER_RE.match(original):
        body = _FRONT_MATTER_RE.sub("", original, count=1)
    else:
        body = original
    rendered = new_header + body.lstrip("\n")
    changed = rendered != original
    if changed and not check_only:
        path.write_text(rendered, encoding="utf-8")
    return changed


def sync_module_doc_templates(root: pathlib.Path, *, check_only: bool) -> list[str]:
    policy = _load_policy(root)
    templates_dir = root / ".contract_driven" / "templates" / "modulos"
    changed: list[str] = []
    for path in sorted(templates_dir.glob("*.md")):
        if _update_template(path, policy, check_only=check_only):
            changed.append(str(path.relative_to(root)))
    return changed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Regenera os headers dos templates de docs de módulo a partir do policy file.")
    parser.add_argument("--check", action="store_true", help="Falha com exit 2 quando houver drift nos templates.")
    args = parser.parse_args(argv)

    root = _repo_root()
    changed = sync_module_doc_templates(root, check_only=args.check)
    if args.check:
        if changed:
            for rel in changed:
                print(f"DRIFT: {rel} (module_doc_header_policy_out_of_sync)")
            return 2
        print("OK: templates de docs de módulo alinhados ao policy file.")
        return 0

    if changed:
        print("OK: templates atualizados:")
        for rel in changed:
            print(f"  - {rel}")
    else:
        print("OK: templates já estavam alinhados.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
