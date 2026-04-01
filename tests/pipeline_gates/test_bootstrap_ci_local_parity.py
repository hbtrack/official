from pathlib import Path


CONTRACT_GATES = Path(".github/workflows/contract-gates.yml")
CI_WORKFLOW = Path(".github/workflows/ci.yml")
BOOTSTRAP_SH = Path("scripts/bootstrap/dev_contract_env.sh")
REQ_FILE = Path("scripts/bootstrap/requirements-contract-dev.txt")


def test_bootstrap_requirements_manifest_exists():
    assert REQ_FILE.exists()


def test_bootstrap_shell_references_same_core_tooling_as_ci():
    content = BOOTSTRAP_SH.read_text(encoding="utf-8")
    for fragment in [
        "npm ci",
        "requirements-contract-dev.txt",
        "schemathesis",
        "oasdiff",
        "redocly",
        "spectral",
        "asyncapi",
    ]:
        assert fragment in content, f"Bootstrap local não cobre {fragment}"


def test_contract_gates_mentions_bootstrap_parity():
    content = CONTRACT_GATES.read_text(encoding="utf-8")
    assert "dev_contract_env.sh" in content
    assert "scripts/_policy/requirements.txt" in content
    assert "npm ci" in content
    assert "schemathesis==4.12.1" in content


def test_ci_mentions_bootstrap_parity():
    content = CI_WORKFLOW.read_text(encoding="utf-8")
    assert "dev_contract_env.sh" in content
    assert "requirements-dev.txt" in content
    assert "scripts/_policy/requirements.txt" in content
    assert "npm ci" in content
