from pathlib import Path


def test_dev_contract_env_ps1_exists():
    path = Path("scripts/bootstrap/dev_contract_env.ps1")
    assert path.exists(), "scripts/bootstrap/dev_contract_env.ps1 não existe"


def test_dev_contract_env_ps1_contains_expected_steps():
    content = Path("scripts/bootstrap/dev_contract_env.ps1").read_text(encoding="utf-8")
    for fragment in [
        ".venv-contract",
        "node_modules\\.bin",
        "virtualenv",
        "pip --version",
        "requirements-contract-dev.txt",
        "npm ci",
        "pytest",
        "schemathesis",
        "redocly",
        "spectral",
        "asyncapi",
        "oasdiff",
    ]:
        assert fragment in content, f"Bootstrap PowerShell não cobre '{fragment}'"
