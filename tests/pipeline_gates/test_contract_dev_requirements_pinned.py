from pathlib import Path


def test_contract_dev_requirements_exists():
    assert Path("scripts/bootstrap/requirements-contract-dev.txt").exists()


def test_contract_dev_requirements_references_pinned_manifests():
    content = Path("scripts/bootstrap/requirements-contract-dev.txt").read_text(encoding="utf-8")
    assert "-r ../../requirements.txt" in content
    assert "-r ../../requirements-dev.txt" in content
    assert "-r ../_policy/requirements.txt" in content


def test_requirements_dev_contains_pinned_core_tools():
    content = Path("requirements-dev.txt").read_text(encoding="utf-8")
    for requirement in [
        "pytest==",
        "pytest-django==",
        "schemathesis==",
        "PyYAML==",
    ]:
        assert requirement in content, f"requirements-dev.txt sem pin explícito para {requirement}"
