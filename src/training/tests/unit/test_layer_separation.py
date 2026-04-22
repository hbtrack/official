"""
TM-044 — Layer separation (Clean Architecture).
Fonte: DOMAIN_RULES_TRAINING.md (DR-TRAIN-032..035).
Verifica que imports entre camadas respeitam a dependência.
"""
import ast
import importlib
import inspect

import pytest


class TestDomainLayerPurity:
    """DR-TRAIN-032: domain layer não importa infra/api/Django."""

    def test_entities_no_django_imports(self):
        source = inspect.getsource(
            importlib.import_module("training.domain.entities")
        )
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert not alias.name.startswith("django"), (
                        f"domain.entities importa {alias.name} — viola Clean Architecture"
                    )
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    assert not node.module.startswith("django"), (
                        f"domain.entities importa de {node.module} — viola Clean Architecture"
                    )

    def test_rules_no_django_imports(self):
        source = inspect.getsource(
            importlib.import_module("training.domain.rules")
        )
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert not alias.name.startswith("django"), (
                        f"domain.rules importa {alias.name} — viola Clean Architecture"
                    )
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    assert not node.module.startswith("django"), (
                        f"domain.rules importa de {node.module} — viola Clean Architecture"
                    )

    def test_domain_no_infrastructure_imports(self):
        """domain layer não importa de infrastructure ou api."""
        for mod_name in ("training.domain.entities", "training.domain.rules"):
            source = inspect.getsource(importlib.import_module(mod_name))
            tree = ast.parse(source)
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom) and node.module:
                    assert "infrastructure" not in node.module, (
                        f"{mod_name} importa de {node.module}"
                    )
                    assert ".api" not in node.module, (
                        f"{mod_name} importa de {node.module}"
                    )


class TestApplicationLayerPurity:
    """Addendum 2.2: application/common/ não importa framework."""

    def test_paging_no_django_imports(self):
        """paging.py é framework-agnostic: nunca importa django.conf."""
        from pathlib import Path

        paging_path = (
            Path(__file__).parent.parent.parent / "application" / "common" / "paging.py"
        )
        tree = ast.parse(paging_path.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert not alias.name.startswith("django"), (
                        f"application/common/paging.py importa '{alias.name}' "
                        "— viola Clean Architecture (deve ser framework-agnostic)"
                    )
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    assert not node.module.startswith("django"), (
                        f"application/common/paging.py importa de '{node.module}' "
                        "— viola Clean Architecture (deve ser framework-agnostic)"
                    )
