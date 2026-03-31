"""
Enforcement de Clean Architecture — layer dependency rules.

Valida que a separação de camadas documentada em CODE_ARCHITECTURE.md
é enforçada no código:

  1. domain/ NÃO pode importar de infrastructure/, application/, django.*, celery
  2. application/ NÃO pode importar de django.db, django.http (só domain + infra)
  3. api.py NÃO pode instanciar *Model diretamente (deve usar use_cases/repository)

GAP-B da conformance_analysis.md.
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path
from typing import NamedTuple

import pytest

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"

# Módulos canônicos (exclui shared — utilitário transversal)
CANONICAL_MODULES = [
    d.name for d in sorted(SRC.iterdir())
    if d.is_dir() and (d / "domain").is_dir() and d.name != "shared"
]

# ── Extrator de imports via AST ───────────────────────────────────────────────


class ImportInfo(NamedTuple):
    module: str       # ex: "django.db.models"
    lineno: int


def _extract_imports(filepath: Path) -> list[ImportInfo]:
    """Extrai todos os módulos importados de um arquivo Python via AST."""
    try:
        tree = ast.parse(filepath.read_text(encoding="utf-8"), filename=str(filepath))
    except SyntaxError:
        return []

    imports: list[ImportInfo] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(ImportInfo(alias.name, node.lineno))
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(ImportInfo(node.module, node.lineno))
    return imports


# ── REGRA 1: domain/ não pode importar de infra, app, django, celery ─────────

# Prefixos proibidos para a camada domain
_DOMAIN_FORBIDDEN = (
    "django.",
    "celery",
    "channels",
    "rest_framework",
    ".infrastructure",
    ".application",
)


def _is_domain_forbidden(module: str) -> bool:
    """Verifica se o import é proibido na camada domain."""
    for prefix in _DOMAIN_FORBIDDEN:
        if module.startswith(prefix) or module == prefix.rstrip("."):
            return True
    # Imports relativos para infrastructure/application
    if "infrastructure" in module or "application" in module:
        return True
    return False


class TestDomainLayerIsolation:
    """domain/ deve conter apenas lógica pura — sem dependências de framework."""

    @pytest.mark.parametrize("mod", CANONICAL_MODULES, ids=lambda m: m)
    def test_domain_has_no_infra_imports(self, mod: str):
        domain_dir = SRC / mod / "domain"
        if not domain_dir.exists():
            pytest.skip(f"{mod} não tem domain/")

        violations: list[str] = []
        for py_file in domain_dir.rglob("*.py"):
            if py_file.name == "__init__.py":
                continue
            for imp in _extract_imports(py_file):
                if _is_domain_forbidden(imp.module):
                    rel = py_file.relative_to(ROOT)
                    violations.append(
                        f"  {rel}:{imp.lineno} → import {imp.module}"
                    )

        assert not violations, (
            f"[{mod}] domain/ importa de camada proibida:\n"
            + "\n".join(violations)
        )


# ── REGRA 2: application/ não pode importar de django.db, django.http ────────

_APPLICATION_FORBIDDEN = (
    "django.db",
    "django.http",
    "django.views",
    "django.urls",
    "ninja",          # Django Ninja é camada de interface
    "channels",
)


def _is_application_forbidden(module: str) -> bool:
    for prefix in _APPLICATION_FORBIDDEN:
        if module.startswith(prefix) or module == prefix:
            return True
    return False


class TestApplicationLayerBoundary:
    """application/ orquestra domain + infra — sem acesso direto a HTTP ou ORM."""

    @pytest.mark.parametrize("mod", CANONICAL_MODULES, ids=lambda m: m)
    def test_application_no_django_http_or_orm(self, mod: str):
        app_dir = SRC / mod / "application"
        if not app_dir.exists():
            pytest.skip(f"{mod} não tem application/")

        violations: list[str] = []
        for py_file in app_dir.rglob("*.py"):
            if py_file.name == "__init__.py":
                continue
            for imp in _extract_imports(py_file):
                if _is_application_forbidden(imp.module):
                    rel = py_file.relative_to(ROOT)
                    violations.append(
                        f"  {rel}:{imp.lineno} → import {imp.module}"
                    )

        assert not violations, (
            f"[{mod}] application/ importa de camada proibida:\n"
            + "\n".join(violations)
        )


# ── REGRA 3: api.py não deve instanciar *Model diretamente ───────────────────


def _find_model_instantiations(filepath: Path) -> list[str]:
    """Detecta chamadas a *Model(...) em api.py — indica bypass de use_cases."""
    try:
        tree = ast.parse(filepath.read_text(encoding="utf-8"), filename=str(filepath))
    except SyntaxError:
        return []

    violations: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func_name = ""
            if isinstance(node.func, ast.Name):
                func_name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                func_name = node.func.attr

            # Heurística: nomes que terminam em "Model" são ORM models
            if func_name.endswith("Model") and func_name[0].isupper():
                violations.append(
                    f"  L{node.lineno}: {func_name}(...) — instanciação direta de ORM model"
                )
    return violations


class TestApiLayerNoDirectORM:
    """api.py deve delegar para use_cases, nunca instanciar ORM models."""

    @pytest.mark.parametrize("mod", CANONICAL_MODULES, ids=lambda m: m)
    def test_api_no_model_instantiation(self, mod: str):
        api_file = SRC / mod / "api.py"
        if not api_file.exists():
            pytest.skip(f"{mod} não tem api.py")

        violations = _find_model_instantiations(api_file)
        assert not violations, (
            f"[{mod}] api.py instancia ORM Models diretamente:\n"
            + "\n".join(violations)
        )


# ── Teste de sanidade: todos os módulos canônicos têm as 4 camadas ───────────

class TestModuleStructureCompleteness:
    """Cada módulo canônico deve ter domain/, application/, infrastructure/, api.py."""

    REQUIRED = ["domain", "application", "infrastructure"]

    @pytest.mark.parametrize("mod", CANONICAL_MODULES, ids=lambda m: m)
    def test_module_has_all_layers(self, mod: str):
        mod_dir = SRC / mod
        missing = []
        for layer in self.REQUIRED:
            if not (mod_dir / layer).is_dir():
                missing.append(layer)
        if not (mod_dir / "api.py").is_file():
            missing.append("api.py")

        assert not missing, (
            f"[{mod}] camadas ausentes: {', '.join(missing)}"
        )
