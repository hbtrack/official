import importlib.machinery
import importlib.util
from pathlib import Path


HB_SCRIPT = Path("scripts/hb")


def _load_hb_module():
    spec = importlib.util.spec_from_loader(
        "hb_cli_bootstrap_guard",
        importlib.machinery.SourceFileLoader("hb_cli_bootstrap_guard", str(HB_SCRIPT)),
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_hb_contains_bootstrap_block_code():
    content = HB_SCRIPT.read_text(encoding="utf-8")
    assert "BLOCKED_LOCAL_TOOLCHAIN_MISSING" in content
    assert "scripts/bootstrap/dev_contract_env.sh" in content
    assert '"st", "schemathesis"' in content


def test_hb_exposes_local_contract_env_helpers():
    module = _load_hb_module()
    cls = module.HBCLIv2
    for attr in [
        "_build_tool_env",
        "_missing_cli_groups",
        "_ensure_local_contract_env",
        "_resolve_python_with_modules",
        "_missing_cli_tools",
    ]:
        assert hasattr(cls, attr), f"HBCLIv2 sem helper {attr}"


def test_hb_uses_bootstrap_guard_in_survival_suite_and_stage3():
    content = HB_SCRIPT.read_text(encoding="utf-8")
    assert "hb survival-suite" in content
    assert "hb stage3" in content
    assert content.count("_ensure_local_contract_env(") >= 2
