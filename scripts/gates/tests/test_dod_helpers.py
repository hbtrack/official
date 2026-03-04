"""
tests/test_dod_helpers.py
Unit tests para _parse_gate_warns_for_ar, _print_dod_table e _collect_dod_status
(funções adicionadas em scripts/run/hb_cli.py — DoD "última milha")
"""
from __future__ import annotations

import io
import sys
from pathlib import Path
from typing import List
from unittest.mock import patch

import pytest

# Adiciona scripts/run/ ao path para importar hb_cli diretamente
RUN_DIR = Path(__file__).parent.parent.parent / "run"
sys.path.insert(0, str(RUN_DIR))

from hb_cli import (  # noqa: E402
    _parse_gate_warns_for_ar,
    _print_dod_table,
    _collect_dod_status,
    _run_gate_output,
)


# ---------------------------------------------------------------------------
# _parse_gate_warns_for_ar
# ---------------------------------------------------------------------------

class TestParseGateWarnsForAr:
    def test_extracts_warn_for_matching_ar(self):
        output = (
            "PASS: check_handoff_contract\n"
            "  AR IDs detectados: 232\n"
            "  ⚠️  WARN: AR_232: PROOF não declarado — adicione 'PROOF: ...'\n"
        )
        warns = _parse_gate_warns_for_ar(output, "232")
        assert len(warns) == 1
        assert "PROOF" in warns[0]

    def test_ignores_warn_for_different_ar(self):
        output = "  ⚠️  WARN: AR_233: TRACE não declarado — ...\n"
        warns = _parse_gate_warns_for_ar(output, "232")
        assert warns == []

    def test_empty_output_returns_empty(self):
        assert _parse_gate_warns_for_ar("", "232") == []

    def test_ok_output_no_warns(self):
        output = (
            "PASS: trace_stitcher\n"
            "  AR IDs avaliados: 232\n"
            "  PROOF+TRACE declarados e arquivos presentes em 1 AR(s)\n"
        )
        assert _parse_gate_warns_for_ar(output, "232") == []

    def test_multiple_warns_same_ar(self):
        output = (
            "  ⚠️  WARN: AR_232: PROOF não declarado\n"
            "  ⚠️  WARN: AR_232: TRACE não declarado\n"
        )
        warns = _parse_gate_warns_for_ar(output, "232")
        assert len(warns) == 2

    def test_warn_case_insensitive_detection(self):
        output = "  [warn] AR_232: stitch issue\n"
        warns = _parse_gate_warns_for_ar(output, "232")
        assert len(warns) == 1

    def test_leading_trailing_whitespace_stripped(self):
        output = "   ⚠️  WARN: AR_232: PROOF não declarado   \n"
        warns = _parse_gate_warns_for_ar(output, "232")
        assert warns[0] == warns[0].strip()


# ---------------------------------------------------------------------------
# _print_dod_table
# ---------------------------------------------------------------------------

class TestPrintDodTable:
    def _capture(self, ar_id: str, dod: dict) -> str:
        buf = io.StringIO()
        with patch("sys.stdout", buf):
            _print_dod_table(ar_id, dod)
        return buf.getvalue()

    def test_all_ok_shows_checkmark(self):
        dod = {"proof": "OK", "trace": "OK", "stitch": "OK", "matrix": "N/A",
               "warns": [], "gate_errors": []}
        out = self._capture("232", dod)
        assert "# DOD-TABLE/V1 AR_232" in out   # marker parseável
        assert "✓" in out
        assert "⚠" not in out

    def test_warn_shows_warning_icon(self):
        dod = {"proof": "WARN", "trace": "OK", "stitch": "OK", "matrix": "N/A",
               "warns": ["⚠️  WARN: AR_232: PROOF não declarado"], "gate_errors": []}
        out = self._capture("232", dod)
        assert "WARN" in out
        assert "⚠" in out

    def test_matrix_na_always_shown(self):
        dod = {"proof": "OK", "trace": "OK", "stitch": "OK", "matrix": "N/A",
               "warns": [], "gate_errors": []}
        out = self._capture("232", dod)
        assert "N/A" in out
        assert "gen_test_matrix" in out

    def test_gate_error_shown(self):
        dod = {"proof": "OK", "trace": "OK", "stitch": "OK", "matrix": "N/A",
               "warns": [], "gate_errors": ["DOC-GATE-021: BLOCKED_INPUT"]}
        out = self._capture("232", dod)
        assert "BLOCKED_INPUT" in out
        assert "GATE-ERROR:" in out            # prefix fixo para parse

    def test_dod_table_marker_includes_ar_id(self):
        """Marker '# DOD-TABLE/V1 AR_NNN' deve conter o AR_ID correto."""
        dod = {"proof": "OK", "trace": "OK", "stitch": "OK", "matrix": "N/A",
               "warns": [], "gate_errors": []}
        out99 = self._capture("99", dod)
        out232 = self._capture("232", dod)
        assert "# DOD-TABLE/V1 AR_99" in out99
        assert "# DOD-TABLE/V1 AR_232" in out232
        assert "# DOD-TABLE/V1 AR_99" not in out232

    def test_dimension_lines_stable_identifiers(self):
        """Cada dimensão deve aparecer exatamente com seu identificador canônico."""
        import re
        dod = {"proof": "OK", "trace": "WARN", "stitch": "WARN", "matrix": "N/A",
               "warns": [], "gate_errors": []}
        out = self._capture("232", dod)
        for dim in ("PROOF", "TRACE", "STITCH", "MATRIX"):
            assert re.search(rf"  {dim}\s+\[.", out), f"Dimensão {dim} ausente no formato esperado"

    def test_empty_warns_no_warn_section(self):
        dod = {"proof": "OK", "trace": "OK", "stitch": "OK", "matrix": "N/A",
               "warns": [], "gate_errors": []}
        out = self._capture("232", dod)
        assert "PROOF" in out  # dimensão exibida
        assert "PROOF não declarado" not in out  # sem mensagem de warn

    def test_separator_present(self):
        dod = {"proof": "OK", "trace": "OK", "stitch": "OK", "matrix": "N/A",
               "warns": [], "gate_errors": []}
        out = self._capture("232", dod)
        assert "─" in out


# ---------------------------------------------------------------------------
# _collect_dod_status (com mock de _run_gate_output)
# ---------------------------------------------------------------------------

class TestCollectDodStatus:
    def _make_ok_output(self, ar_id: str, gate_name: str) -> str:
        return (
            f"PASS: {gate_name}\n"
            f"  AR IDs avaliados: {ar_id}\n"
            f"  PROOF+TRACE declarados e arquivos presentes em 1 AR(s)\n"
        )

    def _make_warn_output(self, ar_id: str, field: str) -> str:
        return (
            "PASS: check_gate\n"
            f"  ⚠️  WARN: AR_{ar_id}: {field} não declarado — adicione ...\n"
        )

    def test_all_gates_pass_returns_all_ok(self, tmp_path):
        # Cria ARQUITETO.md dummy
        (tmp_path / "_reports").mkdir()
        (tmp_path / "_reports" / "ARQUITETO.md").write_text("**AR IDs**: [232]")
        ar_id = "232"

        with patch("hb_cli._run_gate_output", return_value=(0, self._make_ok_output(ar_id, "check_handoff"))):
            result = _collect_dod_status(ar_id, tmp_path)

        assert result["proof"]  == "OK"
        assert result["trace"]  == "OK"
        assert result["stitch"] == "OK"
        assert result["matrix"] == "N/A"
        assert result["warns"]  == []

    def test_proof_warn_detected(self, tmp_path):
        (tmp_path / "_reports").mkdir()
        (tmp_path / "_reports" / "ARQUITETO.md").write_text("**AR IDs**: [232]")

        proof_out  = self._make_warn_output("232", "PROOF")
        ok_out     = self._make_ok_output("232", "ok_gate")

        def fake_gate(script_rel, extra_args, repo_root):
            if "check_handoff" in script_rel:
                return 0, proof_out
            return 0, ok_out

        with patch("hb_cli._run_gate_output", side_effect=fake_gate):
            result = _collect_dod_status("232", tmp_path)

        assert result["proof"]  == "WARN"
        assert result["trace"]  == "OK"
        assert result["stitch"] == "OK"
        assert len(result["warns"]) >= 1

    def test_blocked_input_recorded_in_gate_errors(self, tmp_path):
        (tmp_path / "_reports").mkdir()
        (tmp_path / "_reports" / "ARQUITETO.md").write_text("**AR IDs**: [232]")

        with patch("hb_cli._run_gate_output", return_value=(4, "BLOCKED_INPUT: ...")):
            result = _collect_dod_status("232", tmp_path)

        assert len(result["gate_errors"]) == 3  # todos os 3 gates falharam

    def test_no_duplicate_warns(self, tmp_path):
        """STITCH e PROOF gate reportam a mesma WARN → deduplicar."""
        (tmp_path / "_reports").mkdir()
        (tmp_path / "_reports" / "ARQUITETO.md").write_text("**AR IDs**: [232]")
        dup_warn = "  ⚠️  WARN: AR_232: PROOF não declarado"

        with patch("hb_cli._run_gate_output", return_value=(0, dup_warn)):
            result = _collect_dod_status("232", tmp_path)

        # Mesmo warn vindo de 3 gates → apenas 1 entrada na lista
        assert len(result["warns"]) == 1


# ---------------------------------------------------------------------------
# _run_gate_output: script ausente
# ---------------------------------------------------------------------------

class TestRunGateOutput:
    def test_missing_script_returns_exit4(self, tmp_path):
        ec, out = _run_gate_output("scripts/gates/nao_existe.py", [], tmp_path)
        assert ec == 4
        assert "SCRIPT_NOT_FOUND" in out
