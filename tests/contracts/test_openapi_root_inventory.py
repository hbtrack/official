from __future__ import annotations

import pathlib

from scripts.generate.gen_openapi_root_inventory import render_openapi_root, sync_openapi_root


def _make_repo(tmp_path: pathlib.Path) -> pathlib.Path:
    (tmp_path / "docs" / "_canon").mkdir(parents=True, exist_ok=True)
    (tmp_path / "contracts" / "openapi" / "paths").mkdir(parents=True, exist_ok=True)

    (tmp_path / "docs" / "_canon" / "MODULE_REGISTRY.yaml").write_text(
        """
version: "1.0.0"
artifact: "MODULE_REGISTRY"
modules:
  exercises:
    status: "validated_contract"
    owner: "performance-tech"
    expected_surfaces: ["openapi_sync"]
  users:
    status: "draft_contract"
    owner: "platform-core"
    expected_surfaces: ["openapi_sync"]
""".lstrip(),
        encoding="utf-8",
    )
    (tmp_path / "contracts" / "openapi" / "openapi.yaml").write_text(
        """
openapi: "3.1.0"
info:
  title: Test
  version: "0.1.0"
paths:
  /stale:
    $ref: ./paths/stale.yaml#/~1stale
components:
  schemas: {}
""".lstrip(),
        encoding="utf-8",
    )
    (tmp_path / "contracts" / "openapi" / "paths" / "exercises.yaml").write_text(
        """
/exercises:
  get:
    operationId: listExercises
/exercises/{id}:
  get:
    operationId: getExercise
""".lstrip(),
        encoding="utf-8",
    )
    (tmp_path / "contracts" / "openapi" / "paths" / "users.yaml").write_text(
        """
# scaffold only
""".lstrip(),
        encoding="utf-8",
    )
    return tmp_path


def test_render_openapi_root_uses_only_real_module_paths(tmp_path: pathlib.Path):
    root = _make_repo(tmp_path)

    rendered = render_openapi_root(root)

    assert "/exercises:" in rendered
    assert "/exercises/{id}:" in rendered
    assert "./paths/exercises.yaml#/~1exercises" in rendered
    assert "./paths/exercises.yaml#/~1exercises~1{id}" in rendered
    assert "./paths/users.yaml" not in rendered
    assert "/stale:" not in rendered


def test_sync_openapi_root_detects_and_fixes_drift(tmp_path: pathlib.Path):
    root = _make_repo(tmp_path)

    check = sync_openapi_root(root, check_only=True)
    assert check.changed is True
    assert check.reason == "openapi_root_inventory_out_of_sync"

    write = sync_openapi_root(root, check_only=False)
    assert write.changed is True

    recheck = sync_openapi_root(root, check_only=True)
    assert recheck.changed is False
