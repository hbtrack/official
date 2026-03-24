from __future__ import annotations

import pathlib
import shutil
import textwrap

from scripts.contracts.validate.validate_contracts import _g1_path_canonicality, _g2a_module_doc_crossrefs
from scripts.generate.gen_module_doc_templates import sync_module_doc_templates


def _copy(repo_root: pathlib.Path, tmp_root: pathlib.Path, relpath: str) -> None:
    src = repo_root / relpath
    dst = tmp_root / relpath
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)


def _write(path: pathlib.Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(content).lstrip(), encoding="utf-8")


def _make_layout(tmp_root: pathlib.Path, modules: list[str]) -> None:
    module_lines = "\n".join(f"- {module}" for module in modules)
    _write(
        tmp_root / ".contract_driven" / "CONTRACT_SYSTEM_LAYOUT.md",
        f"""
        ### 2.1 Functional modules
        {module_lines}
        ### 2.2 Cross-cutting modules
        ### 2.3 End
        """,
    )


def _make_module_doc_set(tmp_root: pathlib.Path, module: str, *, include_permissions: bool, broken_permissions: bool = False) -> None:
    upper = module.upper()
    base = tmp_root / "docs" / "hbtrack" / "modulos" / module
    _write(
        base / "README.md",
        f"""
        ---
        module: "{module}"
        system_scope_ref: "../../../_canon/SYSTEM_SCOPE.md"
        handball_rules_ref: "../../../_canon/HANDBALL_RULES_DOMAIN.md"
        handball_semantic_applicability: false
        module_scope_ref: "./MODULE_SCOPE_{upper}.md"
        domain_rules_ref: "./DOMAIN_RULES_{upper}.md"
        invariants_ref: "./INVARIANTS_{upper}.md"
        test_matrix_ref: "./TEST_MATRIX_{upper}.md"
        contract_path_ref: "../../../../contracts/openapi/paths/{module}.yaml"
        schemas_ref: "../../../../contracts/schemas/{module}/"
        ---
        # README
        """,
    )
    _write(
        base / f"MODULE_SCOPE_{upper}.md",
        f"""
        ---
        module: "{module}"
        system_scope_ref: "../../../_canon/SYSTEM_SCOPE.md"
        handball_rules_ref: "../../../_canon/HANDBALL_RULES_DOMAIN.md"
        handball_semantic_applicability: false
        contract_path_ref: "../../../../contracts/openapi/paths/{module}.yaml"
        schemas_ref: "../../../../contracts/schemas/{module}/"
        ---
        # MODULE_SCOPE
        """,
    )
    for name, doc_type in [("DOMAIN_RULES", "domain-rules"), ("INVARIANTS", "invariants"), ("TEST_MATRIX", "test-matrix")]:
        doc_type_line = f'type: "{doc_type}"'
        _write(
            base / f"{name}_{upper}.md",
            f"""
            ---
            module: "{module}"
            system_scope_ref: "../../../_canon/SYSTEM_SCOPE.md"
            handball_rules_ref: "../../../_canon/HANDBALL_RULES_DOMAIN.md"
            handball_semantic_applicability: false
            {doc_type_line}
            contract_path_ref: "../../../../contracts/openapi/paths/{module}.yaml"
            schemas_ref: "../../../../contracts/schemas/{module}/"
            ---
            # {name}
            """,
        )
    if include_permissions:
        invariants_line = "" if broken_permissions else f'invariants_ref: "./INVARIANTS_{upper}.md"\n'
        _write(
            base / f"PERMISSIONS_{upper}.md",
            f"""
            ---
            module: "{module}"
            system_scope_ref: "../../../_canon/SYSTEM_SCOPE.md"
            handball_rules_ref: "../../../_canon/HANDBALL_RULES_DOMAIN.md"
            handball_semantic_applicability: false
            type: "permissions"
            domain_rules_ref: "./DOMAIN_RULES_{upper}.md"
            {invariants_line}---
            # PERMISSIONS
            """,
        )


def _make_minimal_contract_repo(tmp_path: pathlib.Path) -> pathlib.Path:
    repo_root = pathlib.Path(__file__).resolve().parents[2]
    _copy(repo_root, tmp_path, ".contract_driven/templates/modulos/MODULE_DOC_HEADER_POLICY.yaml")
    _write(tmp_path / "docs" / "_canon" / "SYSTEM_SCOPE.md", "# SYSTEM_SCOPE\n")
    _write(tmp_path / "docs" / "_canon" / "HANDBALL_RULES_DOMAIN.md", "# HANDBALL\n")
    _make_layout(tmp_path, ["users"])
    # MODULE_REGISTRY.yaml é a SSOT de módulos canônicos (requer exatamente 17 módulos)
    _copy(repo_root, tmp_path, "docs/_canon/MODULE_REGISTRY.yaml")
    _write(tmp_path / "contracts" / "openapi" / "openapi.yaml", 'openapi: "3.1.0"\ninfo:\n  title: X\n  version: "0.1.0"\npaths:\n  {}\ncomponents:\n  schemas: {}\n')
    _write(tmp_path / "contracts" / "openapi" / "paths" / "users.yaml", "# scaffold\n")
    _write(tmp_path / "contracts" / "schemas" / "users" / "user.schema.json", "{}\n")
    _write(tmp_path / "contracts" / "workflows" / "users" / ".gitkeep", "")
    _write(tmp_path / "contracts" / "openapi" / "components" / "schemas" / "users" / ".gitkeep", "")
    _write(tmp_path / "contracts" / "asyncapi" / "asyncapi.yaml", "asyncapi: 3.0.0\n")
    return tmp_path


def test_module_doc_crossrefs_accepts_legacy_minimum_docs_without_type(tmp_path: pathlib.Path):
    root = _make_minimal_contract_repo(tmp_path)
    _make_module_doc_set(root, "users", include_permissions=False)

    result = _g2a_module_doc_crossrefs(root)

    assert result["status"] == "PASS"


def test_module_doc_crossrefs_flags_conditional_doc_missing_required_ref(tmp_path: pathlib.Path):
    root = _make_minimal_contract_repo(tmp_path)
    _make_module_doc_set(root, "users", include_permissions=True, broken_permissions=True)

    result = _g2a_module_doc_crossrefs(root)

    assert result["status"] == "FAIL"
    messages = [violation["message"] for violation in result["violations"]]
    assert any("invariants_ref" in message for message in messages)


def test_path_canonicality_blocks_reports_outside_root(tmp_path: pathlib.Path):
    root = _make_minimal_contract_repo(tmp_path)
    _make_module_doc_set(root, "users", include_permissions=False)
    _write(root / "scripts" / "contracts" / "_reports" / "contract_gates" / "latest.json", "{}\n")

    result = _g1_path_canonicality(root)

    assert result["status"] == "FAIL"
    assert any("_reports" in violation["artifact"] for violation in result["violations"])


def test_module_doc_templates_sync_from_policy(tmp_path: pathlib.Path):
    repo_root = pathlib.Path(__file__).resolve().parents[2]
    _copy(repo_root, tmp_path, ".contract_driven/templates/modulos/MODULE_DOC_HEADER_POLICY.yaml")
    _write(
        tmp_path / ".contract_driven" / "templates" / "modulos" / "README.md",
        """
        ---
        module: "{{MODULE_NAME}}"
        ---
        # README
        """,
    )

    changed = sync_module_doc_templates(tmp_path, check_only=False)

    content = (tmp_path / ".contract_driven" / "templates" / "modulos" / "README.md").read_text(encoding="utf-8")
    assert ".contract_driven/templates/modulos/README.md" in changed
    assert 'type: "readme"' in content
    assert 'contract_path_ref: "../../../../contracts/openapi/paths/{{MODULE_NAME}}.yaml"' in content
