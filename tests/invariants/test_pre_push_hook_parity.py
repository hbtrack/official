"""Invariant tests for the declared pre-push hook in merge-readiness.json."""

from __future__ import annotations

import json
import pathlib


ROOT = pathlib.Path(__file__).parent.parent.parent


def test_declared_pre_push_hook_exists():
    manifest = json.loads((ROOT / "merge-readiness.json").read_text())
    hook_path = manifest.get("local_executor", {}).get("pre_push_hook")
    assert hook_path, "local_executor.pre_push_hook ausente em merge-readiness.json"
    assert (ROOT / hook_path).exists(), (
        f"pre_push_hook declarado não existe no repo: {hook_path!r}"
    )
