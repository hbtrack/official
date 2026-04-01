from __future__ import annotations

import pathlib
import textwrap

from scripts.contracts.validate.doc_usage_gate import evaluate_doc_usage


def _write(path: pathlib.Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(content).lstrip(), encoding="utf-8")


def _base_repo(tmp_path: pathlib.Path) -> pathlib.Path:
    _write(tmp_path / "docs" / "_canon" / "README.md", "# canon\n")
    _write(tmp_path / "docs" / "hbtrack" / "modulos" / "README.md", "# modules\n")
    _write(tmp_path / "docs" / "hbtrack" / "modulos" / "training" / "README.md", "# training\n")
    _write(
        tmp_path / "docs" / "hbtrack" / "modulos" / "training" / "DOMAIN_RULES_TRAINING.md",
        "# domain\n",
    )
    _write(tmp_path / ".contract_driven" / "BOOT_PROFILES.yaml", "profiles: {}\n")
    _write(
        tmp_path / ".contract_driven" / "templates" / "modulos" / "README.md",
        "# template\n",
    )
    _write(
        tmp_path / ".contract_driven" / "templates" / "modulos" / "DOMAIN_RULES_{{MODULE_NAME_UPPER}}.md",
        "# domain template\n",
    )
    _write(
        tmp_path / "scripts" / "contracts" / "validate" / "validate_contracts.py",
        "print('validator')\n",
    )
    return tmp_path


def test_doc_usage_gate_passes_with_full_coverage(tmp_path: pathlib.Path):
    root = _base_repo(tmp_path)
    _write(
        root / "docs" / "_canon" / "DOC_USAGE_MANIFEST.yaml",
        """
        version: "1.0.0"
        scope:
          include:
            - "docs/_canon/**/*.md"
            - "docs/_canon/**/*.yaml"
            - "docs/hbtrack/modulos/**/*.md"
          exclude: []
        entries:
          - rule_id: canon
            class: canon
            paths:
              - "docs/_canon/README.md"
              - "docs/_canon/DOC_USAGE_MANIFEST.yaml"
            owner_source: "self"
            consumers:
              - "scripts/contracts/validate/validate_contracts.py"
            freshness_mode: registry_guarded
            update_triggers:
              - "docs/_canon/"
          - rule_id: hbtrack-root-readme
            class: module_readme
            paths:
              - "docs/hbtrack/modulos/README.md"
            owner_source: ".contract_driven/templates/modulos/README.md"
            consumers:
              - ".contract_driven/BOOT_PROFILES.yaml"
            freshness_mode: template_parity
            update_triggers:
              - ".contract_driven/templates/modulos/README.md"
          - rule_id: hbtrack-readmes
            class: module_readme
            path_globs:
              - "docs/hbtrack/modulos/*/README.md"
            owner_source: ".contract_driven/templates/modulos/README.md"
            consumers:
              - ".contract_driven/BOOT_PROFILES.yaml"
            freshness_mode: template_parity
            update_triggers:
              - ".contract_driven/templates/modulos/README.md"
          - rule_id: hbtrack-domain
            class: module_doc
            path_globs:
              - "docs/hbtrack/modulos/*/DOMAIN_RULES_*.md"
            owner_source: ".contract_driven/templates/modulos/DOMAIN_RULES_{{MODULE_NAME_UPPER}}.md"
            consumers:
              - "scripts/contracts/validate/validate_contracts.py"
            freshness_mode: template_parity
            update_triggers:
              - ".contract_driven/templates/modulos/DOMAIN_RULES_{{MODULE_NAME_UPPER}}.md"
        """,
    )

    result = evaluate_doc_usage(root)

    assert result["status"] == "PASS"
    assert result["violations"] == []


def test_doc_usage_gate_fails_for_orphan_doc(tmp_path: pathlib.Path):
    root = _base_repo(tmp_path)
    _write(
        root / "docs" / "_canon" / "DOC_USAGE_MANIFEST.yaml",
        """
        version: "1.0.0"
        scope:
          include:
            - "docs/_canon/**/*.md"
            - "docs/_canon/**/*.yaml"
            - "docs/hbtrack/modulos/**/*.md"
          exclude: []
        entries:
          - rule_id: canon
            class: canon
            paths:
              - "docs/_canon/README.md"
              - "docs/_canon/DOC_USAGE_MANIFEST.yaml"
            owner_source: "self"
            consumers:
              - "scripts/contracts/validate/validate_contracts.py"
            freshness_mode: registry_guarded
            update_triggers:
              - "docs/_canon/"
        """,
    )

    result = evaluate_doc_usage(root)

    assert result["status"] == "FAIL"
    assert any("fora do manifesto" in violation["message"] for violation in result["violations"])


def test_doc_usage_gate_fails_when_consumer_missing(tmp_path: pathlib.Path):
    root = _base_repo(tmp_path)
    _write(
        root / "docs" / "_canon" / "DOC_USAGE_MANIFEST.yaml",
        """
        version: "1.0.0"
        scope:
          include:
            - "docs/_canon/**/*.md"
            - "docs/_canon/**/*.yaml"
          exclude: []
        entries:
          - rule_id: canon
            class: canon
            paths:
              - "docs/_canon/README.md"
              - "docs/_canon/DOC_USAGE_MANIFEST.yaml"
            owner_source: "self"
            consumers:
              - "scripts/does/not/exist.py"
            freshness_mode: registry_guarded
            update_triggers:
              - "docs/_canon/"
        """,
    )

    result = evaluate_doc_usage(root)

    assert result["status"] == "FAIL"
    assert any("Consumer não resolve" in violation["message"] for violation in result["violations"])


def test_doc_usage_gate_fails_for_ambiguous_mapping(tmp_path: pathlib.Path):
    root = _base_repo(tmp_path)
    _write(
        root / "docs" / "_canon" / "DOC_USAGE_MANIFEST.yaml",
        """
        version: "1.0.0"
        scope:
          include:
            - "docs/_canon/**/*.md"
            - "docs/_canon/**/*.yaml"
          exclude: []
        entries:
          - rule_id: canon-a
            class: canon
            paths:
              - "docs/_canon/README.md"
              - "docs/_canon/DOC_USAGE_MANIFEST.yaml"
            owner_source: "self"
            consumers:
              - "scripts/contracts/validate/validate_contracts.py"
            freshness_mode: registry_guarded
            update_triggers:
              - "docs/_canon/"
          - rule_id: canon-b
            class: canon
            path_globs:
              - "docs/_canon/*.md"
            owner_source: "self"
            consumers:
              - "scripts/contracts/validate/validate_contracts.py"
            freshness_mode: registry_guarded
            update_triggers:
              - "docs/_canon/"
        """,
    )

    result = evaluate_doc_usage(root)

    assert result["status"] == "FAIL"
    assert any("múltiplas regras" in violation["message"] for violation in result["violations"])
