import importlib.util
from importlib.machinery import SourceFileLoader
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
_LOADER = SourceFileLoader("hb_cli_preflight_scope", str(ROOT / "scripts" / "hb"))
_SPEC = importlib.util.spec_from_loader(_LOADER.name, _LOADER)
_HB_MODULE = importlib.util.module_from_spec(_SPEC)
_LOADER.exec_module(_HB_MODULE)


def _write_handoff(workspace: Path, modulo_foco: str) -> None:
    (workspace / "SESSION_HANDOFF.md").write_text(
        f"---\nmodulo_foco: {modulo_foco}\n---\n",
        encoding="utf-8",
    )


def _build_cli(workspace: Path):
    cli = _HB_MODULE.HBCLIv2.__new__(_HB_MODULE.HBCLIv2)
    cli.root = workspace
    cli.module_registry = {
        "modules": {
            "training": {},
            "notifications": {},
            "video": {},
        }
    }
    return cli


def test_diff_outside_handoff_scope_ignores_noncanonical_area_focus(tmp_path):
    _write_handoff(tmp_path, "architecture")
    cli = _build_cli(tmp_path)

    changed_files = [
        "src/training/api/sessions.py",
        "src/notifications/tasks.py",
        "src/shared/middleware.py",
    ]

    assert cli._detect_diff_outside_handoff_scope(changed_files) is False


def test_diff_outside_handoff_scope_blocks_other_module_for_canonical_focus(tmp_path):
    _write_handoff(tmp_path, "training")
    cli = _build_cli(tmp_path)

    changed_files = [
        "src/training/api/sessions.py",
        "src/notifications/tasks.py",
    ]

    assert cli._detect_diff_outside_handoff_scope(changed_files) is True