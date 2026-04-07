from __future__ import annotations

import hashlib
import json
import py_compile
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
PYTHON = Path(sys.executable)
GENERATOR = REPO_ROOT / "scripts" / "generate" / "backend_codegen.py"
EXPECTED_FILES = [
    REPO_ROOT / "src" / "reports" / "generated" / "schemas.py",
    REPO_ROOT / "src" / "reports" / "generated" / "api.py",
    REPO_ROOT / "src" / "reports" / "generated" / "domain" / "entities.py",
    REPO_ROOT / "src" / "reports" / "generated" / "application" / "use_cases.py",
    REPO_ROOT / "src" / "reports" / "generated" / "infrastructure" / "repository.py",
    REPO_ROOT / "src" / "reports" / "generated" / "tests" / "test_codegen_contract.py",
]


def _run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(PYTHON), *args],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )


def _file_hashes() -> dict[str, str]:
    return {
        path.relative_to(REPO_ROOT).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in EXPECTED_FILES
    }


def test_backend_codegen_reports_is_deterministic_and_compiles():
    first = _run(str(GENERATOR), "--module", "reports", "--format", "json")
    first_payload = json.loads(first.stdout)
    first_hashes = _file_hashes()

    second = _run(str(GENERATOR), "--module", "reports", "--format", "json")
    second_payload = json.loads(second.stdout)
    second_hashes = _file_hashes()

    assert first_payload["status"] == "PASS"
    assert second_payload["status"] == "PASS"
    assert first_payload["combined_sha256"] == second_payload["combined_sha256"]
    assert first_hashes == second_hashes

    check_payload = json.loads(
        _run(str(GENERATOR), "--module", "reports", "--check", "--format", "json").stdout
    )
    assert check_payload["status"] == "PASS"
    assert check_payload["drifts"] == []

    for path in EXPECTED_FILES:
        assert path.is_file(), f"artefato gerado ausente: {path.relative_to(REPO_ROOT)}"
        py_compile.compile(str(path), doraise=True)


def test_generated_reports_contract_smoke_test_passes():
    result = subprocess.run(
        [
            str(PYTHON),
            "-m",
            "pytest",
            "src/reports/generated/tests/test_codegen_contract.py",
            "-q",
        ],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert "3 passed" in result.stdout


def test_backend_codegen_reports_rejects_unsupported_modules():
    result = subprocess.run(
        [str(PYTHON), str(GENERATOR), "--module", "nonexistent_module", "--format", "json"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["status"] == "FAIL"
    assert "Suportados nesta fase" in payload["summary"]
