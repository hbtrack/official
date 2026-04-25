from __future__ import annotations

from pathlib import Path

import yaml

from scripts.contracts.validate import validate_contracts as gates


ROOT = Path(__file__).resolve().parents[2]


def _write_registry(root: Path, status: str = "implemented") -> None:
    canon = root / "docs" / "_canon"
    canon.mkdir(parents=True, exist_ok=True)
    payload = {
        "version": "1.0.0",
        "policy": {
            "status_order": [
                "scaffold",
                "draft_contract",
                "validated_contract",
                "implementation_ready",
                "implemented",
                "staging_validated",
                "released",
            ]
        },
        "modules": {
            "demo": {
                "status": status,
                "owner": "platform-core",
            }
        },
    }
    (canon / "MODULE_REGISTRY.yaml").write_text(
        yaml.safe_dump(payload, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )


def _write_urls(root: Path, *, wired: bool = True) -> None:
    config = root / "config"
    config.mkdir(parents=True, exist_ok=True)
    if wired:
        text = "from demo.api import router as demo_router\napi = object()\n"
    else:
        text = "api = object()\n"
    (config / "urls.py").write_text(text, encoding="utf-8")


def _write_real_module(root: Path) -> None:
    module_dir = root / "src" / "demo"
    (module_dir / "tests" / "unit").mkdir(parents=True, exist_ok=True)
    (module_dir / "api.py").write_text("router = object()\n", encoding="utf-8")
    (module_dir / "tests" / "unit" / "test_demo.py").write_text(
        "def test_demo_behavior():\n    assert 1 + 1 == 2\n",
        encoding="utf-8",
    )


def test_module_behavioral_readiness_gate_passes_on_real_repo():
    result = gates._g_module_behavioral_readiness(ROOT)

    assert result["status"] == "PASS", result


def test_module_behavioral_readiness_gate_fails_for_placeholder_only_tests(tmp_path):
    _write_registry(tmp_path)
    _write_urls(tmp_path, wired=True)
    module_dir = tmp_path / "src" / "demo"
    (module_dir / "tests" / "integration").mkdir(parents=True, exist_ok=True)
    (module_dir / "api.py").write_text("router = object()\n", encoding="utf-8")
    (module_dir / "tests" / "integration" / "test_demo_api.py").write_text(
        "def test_demo_endpoint():\n    pass\n",
        encoding="utf-8",
    )

    result = gates._g_module_behavioral_readiness(tmp_path)

    assert result["status"] == "FAIL"
    assert any("não possui teste executável não-placeholder" in item["message"] for item in result["violations"])


def test_module_behavioral_readiness_gate_fails_for_generated_stub_only(tmp_path):
    _write_registry(tmp_path)
    _write_urls(tmp_path, wired=False)
    module_dir = tmp_path / "src" / "demo" / "generated"
    module_dir.mkdir(parents=True, exist_ok=True)
    (module_dir / "api.py").write_text(
        "raise NotImplementedError('stub')\n",
        encoding="utf-8",
    )

    result = gates._g_module_behavioral_readiness(tmp_path)

    assert result["status"] == "FAIL"
    assert any("stub gerado" in item["message"] for item in result["violations"])


def test_module_behavioral_readiness_gate_passes_with_real_surface_and_tests(tmp_path):
    _write_registry(tmp_path)
    _write_urls(tmp_path, wired=True)
    _write_real_module(tmp_path)

    result = gates._g_module_behavioral_readiness(tmp_path)

    assert result["status"] == "PASS", result
