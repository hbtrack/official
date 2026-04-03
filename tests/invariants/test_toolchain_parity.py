"""Invariant tests: drift detection between toolchain.json and CI workflow files."""
import json
import pathlib
import pytest

ROOT = pathlib.Path(__file__).parent.parent.parent


def _tc():
    return json.loads((ROOT / "toolchain.json").read_text())


class TestNodeVersion:
    def test_nvmrc_matches_toolchain(self):
        tc = _tc()
        nvmrc = (ROOT / ".nvmrc").read_text().strip()
        assert nvmrc == tc["runtimes"]["node"], (
            f".nvmrc={nvmrc!r} != toolchain node={tc['runtimes']['node']!r}"
        )

    def test_ci_workflow_matches_toolchain(self):
        tc = _tc()
        ci = (ROOT / ".github/workflows/ci.yml").read_text()
        expected = f'node-version: "{tc["runtimes"]["node"]}"'
        assert expected in ci, f"ci.yml missing {expected!r}"


class TestPythonVersion:
    def test_contract_gates_matches_toolchain(self):
        tc = _tc()
        wf = (ROOT / ".github/workflows/contract-gates.yml").read_text()
        expected = f'python-version: "{tc["runtimes"]["python"]}"'
        assert expected in wf, f"contract-gates.yml missing {expected!r}"

    def test_ci_workflow_matches_toolchain(self):
        tc = _tc()
        ci = (ROOT / ".github/workflows/ci.yml").read_text()
        expected = f'python-version: "{tc["runtimes"]["python"]}"'
        assert expected in ci, f"ci.yml missing {expected!r}"


class TestPostgresVersion:
    def test_docker_compose_matches_toolchain(self):
        tc = _tc()
        dc = (ROOT / "infra/docker-compose.yml").read_text()
        pg_image = tc["services"]["postgres"]["image"]
        assert pg_image in dc, f"docker-compose.yml missing postgres image {pg_image!r}"


class TestOasdiffVersion:
    def test_contract_gates_references_version(self):
        tc = _tc()
        wf = (ROOT / ".github/workflows/contract-gates.yml").read_text()
        ver = tc["tools"]["oasdiff"]
        assert ver in wf, f"contract-gates.yml missing oasdiff version {ver!r}"
