from pathlib import Path


def test_dev_contract_env_sh_exists():
    path = Path("scripts/bootstrap/dev_contract_env.sh")
    assert path.exists(), "scripts/bootstrap/dev_contract_env.sh não existe"


def test_dev_contract_env_sh_contains_expected_steps():
    content = Path("scripts/bootstrap/dev_contract_env.sh").read_text(encoding="utf-8")
    for fragment in [
        ".venv-contract",
        "virtualenv",
        "pip --version",
        "linux_amd64.tar.gz",
        "requirements-contract-dev.txt",
        "npm ci",
        "pytest",
        "schemathesis",
        "redocly",
        "spectral",
        "asyncapi",
        "oasdiff",
    ]:
        assert fragment in content, f"Bootstrap shell não cobre '{fragment}'"
