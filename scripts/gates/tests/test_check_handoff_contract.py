"""
tests/test_check_handoff_contract.py
Unit tests para scripts/gates/check_handoff_contract.py

Cobertura mínima: PASS e FAIL determinísticos.
Previne regressão quando o template de ARQUITETO.md for alterado.
"""
from __future__ import annotations

import sys
import textwrap
from pathlib import Path

import pytest

# Adicionar scripts/gates ao path para importação direta
GATES_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(GATES_DIR))

from check_handoff_contract import (  # noqa: E402
    EXIT_FAIL_ACTIONABLE,
    EXIT_PASS,
    _check_handoff,
    _extract_ar_ids,
    main,
)

# ---------------------------------------------------------------------------
# Fixtures de texto
# ---------------------------------------------------------------------------

HANDOFF_VALID = textwrap.dedent("""\
    # ARQUITETO.md — HB Track

    <!-- ARQUITETO_REPORT -->

    Protocolo: 1.3.0
    AR IDs: [233, 234, 235]

    ## PRE-FLIGHT
    - git diff --name-only (workspace clean)

    ## STOP CONDITIONS
    - BLOCKED_INPUT (exit 4) se AR não encontrada
    - FAIL_ACTIONABLE (exit 2) se validation_command falhar
""")

HANDOFF_MISSING_AR_IDS = textwrap.dedent("""\
    # ARQUITETO.md — HB Track

    **Protocolo**: 1.3.0

    ## PRE-FLIGHT
    - git status

    ## STOP CONDITIONS
    - exit 4 se falhar
""")

HANDOFF_EMPTY = ""

HANDOFF_MISSING_STOP_CONDITIONS = textwrap.dedent("""\
    # ARQUITETO.md — HB Track

    **Protocolo**: 1.3.0
    AR_233

    ## PRE-FLIGHT
    - workspace clean
""")


# ---------------------------------------------------------------------------
# Testes: _extract_ar_ids
# ---------------------------------------------------------------------------


def test_extract_ar_ids_bracket_notation():
    text = "AR IDs: [233, 234, 235]"
    assert _extract_ar_ids(text) == ["233", "234", "235"]


def test_extract_ar_ids_inline():
    text = "Executar AR_233 e AR_234"
    assert _extract_ar_ids(text) == ["233", "234"]


def test_extract_ar_ids_none():
    assert _extract_ar_ids("Sem ARs aqui") == []


# ---------------------------------------------------------------------------
# Testes: _check_handoff (lógica interna)
# ---------------------------------------------------------------------------


def test_check_handoff_pass_valid():
    failures: list[str] = []
    ar_ids = _check_handoff(HANDOFF_VALID, failures)
    assert failures == [], f"Esperado sem falhas, mas obteve: {failures}"
    assert "233" in ar_ids


def test_check_handoff_fail_no_ar_ids():
    failures: list[str] = []
    _check_handoff(HANDOFF_MISSING_AR_IDS, failures)
    assert any("AR IDs" in f for f in failures), failures


def test_check_handoff_fail_no_stop_conditions():
    failures: list[str] = []
    _check_handoff(HANDOFF_MISSING_STOP_CONDITIONS, failures)
    assert any("STOP" in f.upper() or "BLOCKED" in f.upper() for f in failures), failures


def test_check_handoff_fail_empty():
    failures: list[str] = []
    _check_handoff(HANDOFF_EMPTY, failures)
    assert len(failures) >= 3, f"Esperado ≥ 3 falhas num handoff vazio, obteve: {failures}"


# ---------------------------------------------------------------------------
# Testes: main() (integração de exit code)
# ---------------------------------------------------------------------------


def test_main_pass(tmp_path: Path):
    handoff = tmp_path / "ARQUITETO.md"
    handoff.write_text(HANDOFF_VALID, encoding="utf-8")
    assert main(["-", str(handoff)]) == EXIT_PASS


def test_main_fail_missing_ar_ids(tmp_path: Path):
    handoff = tmp_path / "ARQUITETO.md"
    handoff.write_text(HANDOFF_MISSING_AR_IDS, encoding="utf-8")
    assert main(["-", str(handoff)]) == EXIT_FAIL_ACTIONABLE


def test_main_blocked_input_file_not_found(tmp_path: Path):
    nonexistent = tmp_path / "NENHUM.md"
    from check_handoff_contract import EXIT_BLOCKED_INPUT
    assert main(["-", str(nonexistent)]) == EXIT_BLOCKED_INPUT
