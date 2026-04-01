from __future__ import annotations

import re
from pathlib import Path


GUIAS_ROOT = Path("docs/guias")

_REQUIRED_BANNER = "não canônico e não soberano"
_FORBIDDEN_TOP_PATTERNS = (
    re.compile(r"doc_type:\s*canon", re.IGNORECASE),
    re.compile(r"refer[êe]ncia can[oô]nica", re.IGNORECASE),
    re.compile(r"fonte [úu]nica de verdade", re.IGNORECASE),
    re.compile(r"fonte soberana", re.IGNORECASE),
    re.compile(r"fonte prim[aá]ria", re.IGNORECASE),
)


def _guide_markdown_files() -> list[Path]:
    return sorted(path for path in GUIAS_ROOT.rglob("*.md"))


def _top_excerpt(path: Path, *, lines: int = 20) -> str:
    return "\n".join(path.read_text(encoding="utf-8").splitlines()[:lines])


def test_docs_guias_markdown_files_have_non_sovereign_banner():
    missing_banner: list[str] = []

    for path in _guide_markdown_files():
        if path.name == "README.md":
            continue
        top = _top_excerpt(path)
        if _REQUIRED_BANNER not in top:
            missing_banner.append(str(path))

    assert not missing_banner, (
        "Todos os markdowns em docs/guias devem declarar explicitamente que sao "
        "nao canonicos e nao soberanos no topo.\n"
        + "\n".join(missing_banner)
    )


def test_docs_guias_top_section_does_not_claim_sovereign_authority():
    violations: list[str] = []

    for path in _guide_markdown_files():
        if path.name == "README.md":
            continue
        top = _top_excerpt(path)
        for pattern in _FORBIDDEN_TOP_PATTERNS:
            if pattern.search(top):
                violations.append(f"{path}: {pattern.pattern}")
                break

    assert not violations, (
        "Nenhum arquivo em docs/guias pode se apresentar como fonte soberana no topo.\n"
        + "\n".join(violations)
    )


def test_docs_guias_readme_declares_non_sovereign_contract():
    readme = (GUIAS_ROOT / "README.md").read_text(encoding="utf-8")

    assert "não é canon" in readme
    assert "não é SSOT" in readme
    assert "não substitui" in readme
    assert "Documento de apoio humano, não canônico e não soberano." in readme
