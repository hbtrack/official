from __future__ import annotations

import shutil
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "audit"))

from check_architecture_docs import check_runtime_current_state_generated
from scripts.generate.docs.gen_runtime_current_state import generate_runtime_current_state


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _build_runtime_repo(tmp_path: Path) -> Path:
    registry = {
        "modules": {
            "training": {"status": "implemented", "expected_surfaces": []},
            "identity_access": {"status": "implemented", "expected_surfaces": []},
        }
    }
    _write(tmp_path / "docs" / "_canon" / "MODULE_REGISTRY.yaml", yaml.dump(registry, allow_unicode=True))
    _write(tmp_path / "manage.py", "# manage\n")
    _write(tmp_path / "config" / "settings.py", "DATABASES = {}\nCHANNEL_LAYERS = {}\n")
    _write(
        tmp_path / "config" / "urls.py",
        "from django.urls import path\n"
        "api = object()\n"
        "api.add_router('/training', object())\n"
        "api.add_router('/auth', object())\n"
        "urlpatterns = [path('health', object())]\n",
    )
    _write(
        tmp_path / "infra" / "docker-compose.yml",
        "services:\n  postgres:\n    image: postgres:12\n  redis:\n    image: redis:7-alpine\n",
    )
    _write(tmp_path / "config" / "celery.py", "app = None\n")
    _write(tmp_path / "src" / "training" / "api.py", "router = None\n")
    _write(tmp_path / "src" / "training" / "tasks.py", "app = None\n")
    _write(tmp_path / "src" / "training" / "consumers.py", "consumer = None\n")
    _write(tmp_path / "src" / "training" / "migrations" / "__init__.py", "")
    _write(tmp_path / "src" / "training" / "tests" / "__init__.py", "")
    _write(tmp_path / "src" / "training" / "tests" / "unit" / "__init__.py", "")
    _write(tmp_path / "src" / "training" / "tests" / "integration" / "__init__.py", "")
    _write(tmp_path / "src" / "identity_access" / "api.py", "router = None\n")
    _write(tmp_path / "src" / "identity_access" / "migrations" / "__init__.py", "")
    _write(tmp_path / "src" / "identity_access" / "tests" / "__init__.py", "")
    _write(tmp_path / "src" / "identity_access" / "tests" / "unit" / "__init__.py", "")
    _write(tmp_path / "src" / "identity_access" / "tests" / "integration" / "__init__.py", "")
    _write(tmp_path / "contracts" / "openapi" / "paths" / "training.yaml", "openapi: 3.1.0\n")
    _write(tmp_path / "contracts" / "openapi" / "paths" / "identity_access.yaml", "openapi: 3.1.0\n")
    _write(tmp_path / "contracts" / "schemas" / "training" / "training.schema.json", "{}\n")
    _write(tmp_path / "contracts" / "schemas" / "identity_access" / "identity_access.schema.json", "{}\n")
    _write(tmp_path / "contracts" / "schemas" / "shared" / "shared.schema.json", "{}\n")
    _write(tmp_path / "contracts" / "asyncapi" / "channels" / "training_created.yaml", "channel: x\n")
    _write(tmp_path / "contracts" / "workflows" / "training" / "flow.arazzo.yaml", "arazzo: 1.0.0\n")
    _write(tmp_path / "docs" / "hbtrack" / "modulos" / "training" / "STATE_MODEL_TRAINING.md", "# state\n")
    _write(tmp_path / "docs" / "hbtrack" / "modulos" / "training" / "UI_CONTRACT_TRAINING.md", "# ui\n")
    _write(tmp_path / "frontend" / "package.json", "{}\n")
    _write(tmp_path / "frontend" / "src" / "index.tsx", "export {}\n")
    _write(tmp_path / "frontend" / "src" / "schema.d.ts", "export {}\n")
    _write(tmp_path / "Dockerfile", "FROM python:3.12-slim\n")
    _write(tmp_path / "infra" / "docker-compose.prod.yml", "services: {}\n")
    _write(tmp_path / "infra" / "nginx" / "nginx.conf", "events {}\n")
    _write(tmp_path / "infra" / "scripts" / "rollback.sh", "#!/usr/bin/env bash\n")
    _write(tmp_path / "tests" / "pipeline_gates" / "test_sample.py", "def test_ok(): assert True\n")
    return tmp_path


def _install_generator(tmp_path: Path) -> None:
    src = ROOT / "scripts" / "generate" / "docs" / "gen_runtime_current_state.py"
    dst = tmp_path / "scripts" / "generate" / "docs" / "gen_runtime_current_state.py"
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)


def test_runtime_current_state_generator_renders_current_repo_facts(tmp_path):
    root = _build_runtime_repo(tmp_path)

    rendered = generate_runtime_current_state(root)

    assert "postgres:12" in rendered
    assert "GET /health" in rendered
    assert "frontend/" in rendered
    assert "materializado" in rendered


def test_runtime_current_state_generator_checker_detects_drift(tmp_path):
    root = _build_runtime_repo(tmp_path)
    _install_generator(root)
    _write(root / "docs" / "_canon" / "RUNTIME_CURRENT_STATE.md", "# stale\n")

    result = check_runtime_current_state_generated(root)

    assert result.status == "FAIL"
    assert "gen_runtime_current_state.py --write" in result.details[0]


def test_runtime_current_state_generator_checker_passes_when_doc_matches_generator(tmp_path):
    root = _build_runtime_repo(tmp_path)
    _install_generator(root)
    rendered = generate_runtime_current_state(root)
    _write(root / "docs" / "_canon" / "RUNTIME_CURRENT_STATE.md", rendered)

    result = check_runtime_current_state_generated(root)

    assert result.status == "PASS"


def test_runtime_current_state_generator_real_repo_is_in_sync():
    rendered = generate_runtime_current_state(ROOT)
    current = (ROOT / "docs" / "_canon" / "RUNTIME_CURRENT_STATE.md").read_text(encoding="utf-8")

    assert rendered.strip() == current.strip()


def test_runtime_current_state_generator_is_wired_into_validator():
    validator = (ROOT / "scripts" / "contracts" / "validate" / "validate_contracts.py").read_text(
        encoding="utf-8"
    )

    assert "gen_runtime_current_state.py" in validator
    assert "RUNTIME_CURRENT_STATE.md diverge do gerador canônico" in validator
