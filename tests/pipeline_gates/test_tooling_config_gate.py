from __future__ import annotations

import pathlib
import textwrap

from scripts.contracts.validate.tooling_config_gate import evaluate_tooling_config


def _write(path: pathlib.Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(content).lstrip(), encoding="utf-8")


def _make_repo(tmp_path: pathlib.Path) -> pathlib.Path:
    _write(
        tmp_path / "package.json",
        """
        {
          "devDependencies": {
            "@redocly/cli": "^1.29.5",
            "@stoplight/spectral-cli": "^6.15.0",
            "@asyncapi/cli": "6.0.0"
          }
        }
        """,
    )
    _write(
        tmp_path / "redocly.yaml",
        """
        apis:
          main@v0.1.0:
            root: contracts/openapi/openapi.yaml
        rules:
          no-unresolved-refs: error
        """,
    )
    _write(tmp_path / "docs" / "_canon" / "TOOLCHAIN_HEALTH_POLICY.md", "# policy\n")
    _write(
        tmp_path / "contracts" / "openapi" / "openapi.yaml",
        """
        openapi: "3.1.0"
        info:
          title: Test
          version: "0.1.0"
        paths: {}
        components:
          schemas: {}
        """,
    )
    return tmp_path


def test_tooling_config_gate_passes_with_supported_toolchain(tmp_path: pathlib.Path):
    root = _make_repo(tmp_path)

    result = evaluate_tooling_config(
        root,
        tool_versions={
            "redocly": "1.29.5",
            "spectral": "6.15.0",
            "asyncapi": "6.0.0",
            "oasdiff": "2.7.0",
            "schemathesis": "4.5.0",
        },
        is_ci=False,
    )

    assert result["status"] == "PASS"


def test_tooling_config_gate_degrades_locally_without_oasdiff_and_schemathesis(tmp_path: pathlib.Path):
    root = _make_repo(tmp_path)

    result = evaluate_tooling_config(
        root,
        tool_versions={
            "redocly": "1.29.5",
            "spectral": "6.15.0",
            "asyncapi": "6.0.0",
            "oasdiff": None,
            "schemathesis": None,
        },
        is_ci=False,
    )

    assert result["status"] == "DEGRADED"
    assert {violation["artifact"] for violation in result["violations"]} == {"oasdiff", "schemathesis"}


def test_tooling_config_gate_fails_in_ci_when_critical_tool_is_missing(tmp_path: pathlib.Path):
    root = _make_repo(tmp_path)

    result = evaluate_tooling_config(
        root,
        tool_versions={
            "redocly": "1.29.5",
            "spectral": "6.15.0",
            "asyncapi": "6.0.0",
            "oasdiff": None,
            "schemathesis": "4.5.0",
        },
        is_ci=True,
    )

    assert result["status"] == "FAIL"
    assert any(violation["artifact"] == "oasdiff" for violation in result["violations"])
