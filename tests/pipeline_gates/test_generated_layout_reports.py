from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_reports_generated_layout_exists():
    expected = {
        REPO_ROOT / "src" / "reports" / "generated" / "__init__.py",
        REPO_ROOT / "src" / "reports" / "generated" / "domain" / "__init__.py",
        REPO_ROOT / "src" / "reports" / "generated" / "application" / "__init__.py",
        REPO_ROOT / "src" / "reports" / "generated" / "infrastructure" / "__init__.py",
        REPO_ROOT / "src" / "reports" / "generated" / "tests" / "__init__.py",
    }

    for path in expected:
        assert path.is_file(), f"layout generated ausente: {path.relative_to(REPO_ROOT)}"


def test_code_architecture_documents_generated_zone_as_derived():
    source = (REPO_ROOT / "docs" / "_canon" / "CODE_ARCHITECTURE.md").read_text(encoding="utf-8")

    assert "src/<module>/generated/" in source
    assert "piloto `reports`" in source
    assert "nunca fonte de verdade" in source
    assert "codigo estrutural derivado do source graph" in source
