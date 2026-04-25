from __future__ import annotations

import json
from pathlib import Path

from scripts.contracts.validate import validate_contracts as gates


ROOT = Path(__file__).resolve().parents[2]


def test_hook_effectiveness_gate_passes_on_real_repo():
    result = gates._g_hook_effectiveness(ROOT)

    assert result["status"] == "PASS", result


def test_hook_effectiveness_gate_fails_for_noop_pretool_hook(tmp_path):
    hooks_dir = tmp_path / ".claude"
    hooks_dir.mkdir(parents=True)
    (hooks_dir / "settings.local.json").write_text(
        json.dumps(
            {
                "hooks": {
                    "PreToolUse": [
                        {
                            "hooks": [
                                {
                                    "type": "command",
                                    "command": "python3 scripts/hooks/check_backend_gate.py",
                                    "timeout": 10,
                                }
                            ]
                        }
                    ]
                }
            }
        ),
        encoding="utf-8",
    )
    scripts_dir = tmp_path / "scripts" / "hooks"
    scripts_dir.mkdir(parents=True)
    (scripts_dir / "check_backend_gate.py").write_text(
        "import sys\nsys.exit(0)\n",
        encoding="utf-8",
    )

    result = gates._g_hook_effectiveness(tmp_path)

    assert result["status"] == "FAIL"
    assert any("allow-all incondicional" in item["message"] for item in result["violations"])


def test_hook_effectiveness_gate_fails_for_mislabeled_stop_hook(tmp_path):
    hooks_dir = tmp_path / ".github" / "hooks"
    hooks_dir.mkdir(parents=True)
    (hooks_dir / "hb-contract-guards.json").write_text(
        json.dumps(
            {
                "hooks": {
                    "Stop": [
                        {
                            "type": "command",
                            "command": "python3 scripts/hooks/advisory_session_commit.py",
                            "timeout": 10,
                        }
                    ]
                }
            }
        ),
        encoding="utf-8",
    )
    scripts_dir = tmp_path / "scripts" / "hooks"
    scripts_dir.mkdir(parents=True)
    (scripts_dir / "advisory_session_commit.py").write_text(
        '"""Stop Hook — Guard advisory"""\nimport sys\nsys.exit(0)\n',
        encoding="utf-8",
    )

    result = gates._g_hook_effectiveness(tmp_path)

    assert result["status"] == "FAIL"
    assert any("guard/gate bloqueante" in item["message"] for item in result["violations"])


def test_hook_effectiveness_gate_allows_explicitly_negated_guard_language(tmp_path):
    hooks_dir = tmp_path / ".github" / "hooks"
    hooks_dir.mkdir(parents=True)
    (hooks_dir / "hb-contract-guards.json").write_text(
        json.dumps(
            {
                "hooks": {
                    "Stop": [
                        {
                            "type": "command",
                            "command": "python3 scripts/hooks/advisory_session_commit.py",
                            "timeout": 10,
                        }
                    ]
                }
            }
        ),
        encoding="utf-8",
    )
    scripts_dir = tmp_path / "scripts" / "hooks"
    scripts_dir.mkdir(parents=True)
    (scripts_dir / "advisory_session_commit.py").write_text(
        '"""Stop Hook — advisory\\nNão é um guard. Não bloqueia.\\n"""\\nimport sys\\nsys.exit(0)\\n',
        encoding="utf-8",
    )

    result = gates._g_hook_effectiveness(tmp_path)

    assert result["status"] == "PASS", result
