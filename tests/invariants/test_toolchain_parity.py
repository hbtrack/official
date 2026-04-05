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

    def test_ci_workflow_delegates_to_reusable(self):
        """ci.yml deve ser caller fino que delega para _reusable-ci.yml."""
        ci = (ROOT / ".github/workflows/ci.yml").read_text()
        assert "_reusable-ci.yml" in ci, "ci.yml não referencia _reusable-ci.yml"

    def test_reusable_reads_node_version_from_toolchain(self):
        """_reusable-ci.yml deve ler node version de toolchain.json via jq."""
        reusable = (ROOT / ".github/workflows/_reusable-ci.yml").read_text()
        assert "jq -r .runtimes.node toolchain.json" in reusable, (
            "_reusable-ci.yml não lê node version de toolchain.json via jq"
        )


class TestPythonVersion:
    def test_contract_gates_reads_python_from_toolchain(self):
        """contract-gates.yml deve ler python version de toolchain.json via jq."""
        wf = (ROOT / ".github/workflows/contract-gates.yml").read_text()
        assert "jq -r .runtimes.python toolchain.json" in wf, (
            "contract-gates.yml não lê python version de toolchain.json via jq"
        )

    def test_reusable_reads_python_version_from_toolchain(self):
        """_reusable-ci.yml deve ler python version de toolchain.json via jq."""
        reusable = (ROOT / ".github/workflows/_reusable-ci.yml").read_text()
        assert "jq -r .runtimes.python toolchain.json" in reusable, (
            "_reusable-ci.yml não lê python version de toolchain.json via jq"
        )


class TestPostgresVersion:
    def test_docker_compose_matches_toolchain(self):
        tc = _tc()
        dc = (ROOT / "infra/docker-compose.yml").read_text()
        pg_image = tc["services"]["postgres"]["image"]
        assert pg_image in dc, f"docker-compose.yml missing postgres image {pg_image!r}"


class TestOasdiffVersion:
    def test_contract_gates_reads_oasdiff_from_toolchain(self):
        """contract-gates.yml deve ler oasdiff version de toolchain.json via jq."""
        wf = (ROOT / ".github/workflows/contract-gates.yml").read_text()
        assert "jq -r .tools.oasdiff toolchain.json" in wf, (
            "contract-gates.yml não lê oasdiff version de toolchain.json via jq"
        )
