"""
Testes do DECISION_MATERIALIZATION_GATE (ordem 2O).

Cobertura:
- SKIP quando diretório de matrizes ausente
- SKIP quando nenhuma matriz encontrada
- PASS quando todas as decisões são materialized (modo full_scan)
- DEGRADED quando há decisões not_materialized com blocks_feature_work=true (modo full_scan)
- FAIL quando source_decision_ir aponta para caminho não soberano
- FAIL quando campo obrigatório raiz ausente
- FAIL quando campo obrigatório por decisão ausente
- FAIL quando blocks_feature_work=true e not_materialized e PR toca módulo (modo PR diff)
- PASS quando waiver inline válido está presente para decisão bloqueante
- Relatório gravado em _reports/decision_materialization/<module>.json
"""
from __future__ import annotations

import json
import os
import pathlib

import pytest
import yaml

from scripts.contracts.validate import validate_contracts as gates


# ---------------------------------------------------------------------------
# Helpers de fixture
# ---------------------------------------------------------------------------

def _write_matrix(tmp_path: pathlib.Path, module: str, decisions: list[dict], **extra) -> pathlib.Path:
    """Grava uma matriz DECISION_MATERIALIZATION_<MODULE>.yaml minimal em tmp_path."""
    mat_dir = tmp_path / ".contract_driven" / "decisions" / "materialization"
    mat_dir.mkdir(parents=True, exist_ok=True)
    data = {
        "module": module,
        "source_decision_ir": f".contract_driven/decisions/DECISION_IR_{module.upper()}.yaml",
        "source_adr": [f"docs/_canon/decisions/ADR-001-{module}.md"],
        "freshness": {"main_ref": None, "generated_at_utc": None},
        "decisions": decisions,
    }
    data.update(extra)
    mat_file = mat_dir / f"DECISION_MATERIALIZATION_{module.upper()}.yaml"
    mat_file.write_text(yaml.dump(data), encoding="utf-8")
    return mat_file


def _minimal_decision(
    decision_id: str = "DEC-001",
    status: str = "materialized",
    blocks: bool = False,
    waiver=None,
    **extra,
) -> dict:
    d = {
        "decision_id": decision_id,
        "decision_policy_criticality": "obrigatoria",
        "execution_priority": "P0",
        "canonical_source": "docs/_canon/decisions/ADR-001.md#dec-001",
        "materialization_status": status,
        "blocks_feature_work": blocks,
        "waiver": waiver,
    }
    d.update(extra)
    return d


# ---------------------------------------------------------------------------
# Testes: SKIP
# ---------------------------------------------------------------------------

def test_skip_when_mat_dir_absent(tmp_path: pathlib.Path) -> None:
    result = gates._g2O_decision_materialization(tmp_path)
    assert result["status"] == "SKIP_NOT_APPLICABLE"
    assert result["exit_code"] == 0


def test_skip_when_no_matrix_files(tmp_path: pathlib.Path) -> None:
    mat_dir = tmp_path / ".contract_driven" / "decisions" / "materialization"
    mat_dir.mkdir(parents=True)
    result = gates._g2O_decision_materialization(tmp_path)
    assert result["status"] == "SKIP_NOT_APPLICABLE"
    assert result["exit_code"] == 0


# ---------------------------------------------------------------------------
# Testes: PASS
# ---------------------------------------------------------------------------

def test_pass_all_materialized(tmp_path: pathlib.Path) -> None:
    _write_matrix(tmp_path, "training", [
        _minimal_decision("DEC-001", status="materialized", blocks=True),
        _minimal_decision("DEC-002", status="materialized", blocks=False),
    ])
    result = gates._g2O_decision_materialization(tmp_path)
    assert result["status"] == "PASS"
    assert result["exit_code"] == 0
    assert len([v for v in result["violations"] if v.get("severity") == "error"]) == 0


def test_pass_deferred_with_reason_not_blocking(tmp_path: pathlib.Path) -> None:
    """deferred_with_reason com blocks_feature_work=false não deve bloquear."""
    _write_matrix(tmp_path, "training", [
        _minimal_decision("DEC-001", status="deferred_with_reason", blocks=False),
    ])
    result = gates._g2O_decision_materialization(tmp_path)
    assert result["status"] == "PASS"
    assert result["exit_code"] == 0


# ---------------------------------------------------------------------------
# Testes: DEGRADED (full_scan local — sem GITHUB_ACTIONS)
# ---------------------------------------------------------------------------

def test_degraded_not_materialized_full_scan(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Em full_scan (sem GITHUB_ACTIONS), decisão not_materialized + blocks=True → DEGRADED, não FAIL."""
    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
    _write_matrix(tmp_path, "training", [
        _minimal_decision("DEC-001", status="not_materialized", blocks=True),
    ])
    result = gates._g2O_decision_materialization(tmp_path)
    assert result["status"] == "DEGRADED"
    assert result["exit_code"] == 0  # não bloqueia CI local
    violations = result["violations"]
    assert len(violations) == 1
    assert violations[0]["severity"] == "warn"
    assert violations[0]["blocking_code"] == "FAIL_DECISION_MATERIALIZATION"


def test_degraded_partially_materialized_full_scan(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
    _write_matrix(tmp_path, "training", [
        _minimal_decision("DEC-001", status="partially_materialized", blocks=True),
    ])
    result = gates._g2O_decision_materialization(tmp_path)
    assert result["status"] == "DEGRADED"
    assert result["exit_code"] == 0


def test_blocked_by_contract_conflict_always_warn(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """blocked_by_contract_conflict → sempre warn, nunca FAIL."""
    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
    _write_matrix(tmp_path, "training", [
        _minimal_decision("DEC-020", status="blocked_by_contract_conflict", blocks=True),
    ])
    result = gates._g2O_decision_materialization(tmp_path)
    assert result["status"] == "DEGRADED"
    assert result["exit_code"] == 0
    assert all(v["severity"] == "warn" for v in result["violations"])


# ---------------------------------------------------------------------------
# Testes: FAIL — violações estruturais
# ---------------------------------------------------------------------------

def test_fail_non_sovereign_source(tmp_path: pathlib.Path) -> None:
    """source_decision_ir apontando para docs/hbtrack/ → NON_SOVEREIGN_DECISION_IR_SOURCE."""
    _write_matrix(
        tmp_path, "training",
        [_minimal_decision("DEC-001", status="materialized", blocks=False)],
        source_decision_ir="docs/hbtrack/modulos/training/DECISION_IR_TRAINING.yaml",
    )
    result = gates._g2O_decision_materialization(tmp_path)
    assert result["status"] == "FAIL"
    assert result["exit_code"] == 2
    codes = [v["blocking_code"] for v in result["violations"]]
    assert "NON_SOVEREIGN_DECISION_IR_SOURCE" in codes


def test_fail_missing_required_root_field(tmp_path: pathlib.Path) -> None:
    """Campo obrigatório `decisions` ausente → CANON_REGISTRATION_INCOMPLETE."""
    mat_dir = tmp_path / ".contract_driven" / "decisions" / "materialization"
    mat_dir.mkdir(parents=True)
    # Escreve matriz sem o campo `decisions`
    data = {
        "module": "training",
        "source_decision_ir": ".contract_driven/decisions/DECISION_IR_TRAINING.yaml",
        "source_adr": ["docs/_canon/decisions/ADR-001.md"],
        # `decisions` ausente propositalmente
    }
    (mat_dir / "DECISION_MATERIALIZATION_TRAINING.yaml").write_text(yaml.dump(data), encoding="utf-8")
    result = gates._g2O_decision_materialization(tmp_path)
    assert result["status"] == "FAIL"
    codes = [v["blocking_code"] for v in result["violations"]]
    assert "CANON_REGISTRATION_INCOMPLETE" in codes


def test_fail_missing_required_decision_field(tmp_path: pathlib.Path) -> None:
    """Campo `materialization_status` ausente por decisão → CANON_REGISTRATION_INCOMPLETE."""
    dec = {
        "decision_id": "DEC-001",
        "decision_policy_criticality": "obrigatoria",
        "execution_priority": "P0",
        "canonical_source": "docs/_canon/decisions/ADR-001.md#dec-001",
        "blocks_feature_work": False,
        # `materialization_status` ausente
    }
    _write_matrix(tmp_path, "training", [dec])
    result = gates._g2O_decision_materialization(tmp_path)
    assert result["status"] == "FAIL"
    codes = [v["blocking_code"] for v in result["violations"]]
    assert "CANON_REGISTRATION_INCOMPLETE" in codes


def test_fail_invalid_yaml(tmp_path: pathlib.Path) -> None:
    """YAML inválido na matriz → FAIL com FAIL_DECISION_MATERIALIZATION."""
    mat_dir = tmp_path / ".contract_driven" / "decisions" / "materialization"
    mat_dir.mkdir(parents=True)
    (mat_dir / "DECISION_MATERIALIZATION_TRAINING.yaml").write_text(
        "---\ninvalid: yaml: [\nbroken", encoding="utf-8"
    )
    result = gates._g2O_decision_materialization(tmp_path)
    assert result["status"] == "FAIL"
    assert result["exit_code"] == 2


# ---------------------------------------------------------------------------
# Testes: FAIL — PR toca módulo em CI (modo pr_diff)
# ---------------------------------------------------------------------------

def test_fail_when_pr_touches_module_in_ci(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Em CI com GITHUB_ACTIONS, se PR toca src/<module>/ e decisão não materializada → FAIL."""
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    monkeypatch.setenv("GITHUB_BASE_SHA", "")
    _write_matrix(tmp_path, "training", [
        _minimal_decision("DEC-001", status="not_materialized", blocks=True),
    ])
    # Simula git diff retornando arquivo do módulo
    import unittest.mock as mock
    fake_diff = mock.MagicMock()
    fake_diff.returncode = 0
    fake_diff.stdout = "src/training/domain/session.py\n"
    fake_rev = mock.MagicMock()
    fake_rev.returncode = 0
    fake_rev.stdout = "abc123\n"
    with mock.patch("subprocess.run", side_effect=[fake_rev, fake_diff]):
        result = gates._g2O_decision_materialization(tmp_path)
    assert result["status"] == "FAIL"
    assert result["exit_code"] == 2
    errors = [v for v in result["violations"] if v.get("severity") == "error"]
    assert len(errors) >= 1
    assert errors[0]["blocking_code"] == "FAIL_DECISION_MATERIALIZATION"


def test_pass_when_pr_does_not_touch_module_in_ci(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Em CI com GITHUB_ACTIONS, se PR NÃO toca src/<module>/ → PASS mesmo com not_materialized."""
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    monkeypatch.setenv("GITHUB_BASE_SHA", "")
    _write_matrix(tmp_path, "training", [
        _minimal_decision("DEC-001", status="not_materialized", blocks=True),
    ])
    import unittest.mock as mock
    fake_diff = mock.MagicMock()
    fake_diff.returncode = 0
    fake_diff.stdout = "docs/_canon/OTHER_MODULE_FILE.md\n"
    fake_rev = mock.MagicMock()
    fake_rev.returncode = 0
    fake_rev.stdout = "abc123\n"
    with mock.patch("subprocess.run", side_effect=[fake_rev, fake_diff]):
        result = gates._g2O_decision_materialization(tmp_path)
    assert result["status"] == "PASS"
    assert result["exit_code"] == 0


# ---------------------------------------------------------------------------
# Testes: Waivers
# ---------------------------------------------------------------------------

def test_pass_with_valid_inline_waiver(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Waiver inline válido com campos obrigatórios → sem violação."""
    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
    waiver = {
        "waiver_id": "DECISION_MATERIALIZATION_GATE-training-DEC-001-2026-04-30",
        "approved_by": "davis",
        "expires_at_utc": "2026-12-31T23:59:59Z",
        "scope": ["src/training/"],
    }
    _write_matrix(tmp_path, "training", [
        _minimal_decision("DEC-001", status="not_materialized", blocks=True, waiver=waiver),
    ])
    result = gates._g2O_decision_materialization(tmp_path)
    # Com waiver válido, a decisão não gera violação; demais ok → PASS
    assert result["status"] == "PASS"
    assert result["exit_code"] == 0


def test_pass_with_valid_file_waiver(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Waiver em arquivo contracts/_waivers/... → sem violação."""
    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
    _write_matrix(tmp_path, "training", [
        _minimal_decision("DEC-001", status="not_materialized", blocks=True, waiver=None),
    ])
    waiver_dir = tmp_path / "contracts" / "_waivers" / "DECISION_MATERIALIZATION_GATE" / "training"
    waiver_dir.mkdir(parents=True)
    waiver_data = {
        "waiver_id": "DECISION_MATERIALIZATION_GATE-training-DEC-001-2026-04-30",
        "approved_by": "davis",
        "expires_at_utc": "2026-12-31T23:59:59Z",
        "scope": ["src/training/"],
        "reason": "Bootstrap — materialização ocorre no PR 4.",
    }
    (waiver_dir / "DEC-001.yaml").write_text(yaml.dump(waiver_data), encoding="utf-8")
    result = gates._g2O_decision_materialization(tmp_path)
    assert result["status"] == "PASS"
    assert result["exit_code"] == 0


def test_degraded_with_invalid_inline_waiver(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Waiver inline com campos faltando → tratado como sem waiver → DEGRADED."""
    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
    invalid_waiver = {"waiver_id": "DECISION_MATERIALIZATION_GATE-training-DEC-001"}  # falta approved_by, expires_at_utc, scope
    _write_matrix(tmp_path, "training", [
        _minimal_decision("DEC-001", status="not_materialized", blocks=True, waiver=invalid_waiver),
    ])
    result = gates._g2O_decision_materialization(tmp_path)
    assert result["status"] == "DEGRADED"
    assert any(v["blocking_code"] == "FAIL_DECISION_MATERIALIZATION" for v in result["violations"])


# ---------------------------------------------------------------------------
# Testes: Relatório
# ---------------------------------------------------------------------------

def test_report_written_on_pass(tmp_path: pathlib.Path) -> None:
    """Gate deve gravar relatório em _reports/decision_materialization/<module>.json ao passar."""
    _write_matrix(tmp_path, "training", [
        _minimal_decision("DEC-001", status="materialized", blocks=False),
    ])
    gates._g2O_decision_materialization(tmp_path)
    report_path = tmp_path / "_reports" / "decision_materialization" / "training.json"
    assert report_path.exists(), "Relatório training.json deve existir após execução do gate"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["module"] == "training"
    assert "decisions_total" in report
    assert "summary" in report


def test_report_includes_blocking_decisions(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Relatório deve listar decisões com blocks_feature_work=true e status bloqueante."""
    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
    _write_matrix(tmp_path, "training", [
        _minimal_decision("DEC-001", status="not_materialized", blocks=True),
        _minimal_decision("DEC-002", status="materialized", blocks=True),
    ])
    gates._g2O_decision_materialization(tmp_path)
    report = json.loads(
        (tmp_path / "_reports" / "decision_materialization" / "training.json").read_text(encoding="utf-8")
    )
    assert "DEC-001" in report["blocking_decisions"]
    assert "DEC-002" not in report["blocking_decisions"]


# ---------------------------------------------------------------------------
# Testes: Múltiplos módulos
# ---------------------------------------------------------------------------

def test_multiple_modules_all_pass(tmp_path: pathlib.Path) -> None:
    """Gate deve verificar todos os módulos com matriz e retornar PASS se todos ok."""
    for module in ("training", "analytics"):
        _write_matrix(tmp_path, module, [
            _minimal_decision("DEC-001", status="materialized", blocks=False),
        ])
    result = gates._g2O_decision_materialization(tmp_path)
    assert result["status"] == "PASS"
    assert result["exit_code"] == 0


# ---------------------------------------------------------------------------
# Testes adicionais: fixes das revisões do Codex
# ---------------------------------------------------------------------------

def test_fail_arbitrary_non_canonical_source(tmp_path: pathlib.Path) -> None:
    """Qualquer path não canônico em source_decision_ir → NON_SOVEREIGN_DECISION_IR_SOURCE.

    Fix P2 Codex: validação positiva — não só rejeitar docs/hbtrack/, mas
    exigir .contract_driven/decisions/DECISION_IR_<MODULE>.yaml.
    """
    _write_matrix(
        tmp_path, "training",
        [_minimal_decision("DEC-001", status="materialized", blocks=False)],
        source_decision_ir=".dev/training/DECISION_IR_TRAINING.yaml",  # path arbitrário não canônico
    )
    result = gates._g2O_decision_materialization(tmp_path)
    assert result["status"] == "FAIL"
    codes = [v["blocking_code"] for v in result["violations"]]
    assert "NON_SOVEREIGN_DECISION_IR_SOURCE" in codes


def test_degraded_with_expired_inline_waiver(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Waiver com expires_at_utc no passado → inválido → decisão ainda bloqueante.

    Fix P2 Codex: waiver expirado não deve suprimir bloqueio.
    """
    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
    expired_waiver = {
        "waiver_id": "DECISION_MATERIALIZATION_GATE-training-DEC-001-2025-01-01",
        "approved_by": "davis",
        "expires_at_utc": "2025-01-01T00:00:00Z",  # data no passado
        "scope": ["src/training/"],
    }
    _write_matrix(tmp_path, "training", [
        _minimal_decision("DEC-001", status="not_materialized", blocks=True, waiver=expired_waiver),
    ])
    result = gates._g2O_decision_materialization(tmp_path)
    assert result["status"] == "DEGRADED"  # full_scan: warn, não error
    assert any(v["blocking_code"] == "FAIL_DECISION_MATERIALIZATION" for v in result["violations"])


def test_diff_uses_triple_dot_syntax(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """_dm_detect_changed_files deve usar triple-dot diff (base_sha...HEAD) não dois pontos.

    Fix P1 Codex: dois pontos incluem mudanças do base branch não relacionadas ao PR.
    """
    import unittest.mock as mock
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    monkeypatch.setenv("GITHUB_BASE_SHA", "abc123")

    captured_args = []

    def fake_run(args, **kwargs):
        captured_args.append(args)
        m = mock.MagicMock()
        m.returncode = 0
        m.stdout = ""
        return m

    with mock.patch("subprocess.run", side_effect=fake_run):
        gates._dm_detect_changed_files(tmp_path)

    # Deve ter chamado git diff com triple-dot (base_sha...HEAD)
    diff_calls = [a for a in captured_args if "diff" in a]
    assert diff_calls, "git diff deve ter sido chamado"
    diff_args = diff_calls[0]
    assert any("abc123...HEAD" in str(arg) for arg in diff_args), (
        f"Esperado triple-dot diff 'abc123...HEAD', mas argumentos foram: {diff_args}"
    )
