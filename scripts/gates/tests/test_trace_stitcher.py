"""
tests/test_trace_stitcher.py
Unit tests para scripts/gates/trace_stitcher.py  (DOC-GATE-021)

Cobertura: extração de campos por AR, validação de arquivos, exit codes.
"""
from __future__ import annotations

import sys
import textwrap
from pathlib import Path

import pytest

GATES_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(GATES_DIR))

from trace_stitcher import (  # noqa: E402
    EXIT_BLOCKED_INPUT,
    EXIT_PASS,
    _check_ar,
    _extract_ar_block,
    _extract_ar_ids,
    _extract_file_paths,
    _has_field_declared,
    _is_suppressed,
    _parse_field,
    _validate_trace_files,
    main,
)

# ---------------------------------------------------------------------------
# Fixtures de handoff
# ---------------------------------------------------------------------------

_BASE = textwrap.dedent("""\
    # ARQUITETO.md
    Protocolo: 1.3.0
    AR IDs: [232]
    ## PRE-FLIGHT
    - git diff --name-only
    ## STOP CONDITIONS
    - BLOCKED_INPUT exit 4
""")

HANDOFF_FULL = (
    _BASE
    + textwrap.dedent("""\

    ## Escopo da AR_232

    PROOF (AR_232): tests/training/test_wellness.py::test_focus_total
    TRACE (AR_232): docs/hbtrack/modulos/treinos/TEST_MATRIX_TRAINING.md §9
""")
)

HANDOFF_NO_PROOF = (
    _BASE
    + textwrap.dedent("""\

    ## Escopo da AR_232

    TRACE (AR_232): docs/hbtrack/modulos/treinos/TEST_MATRIX_TRAINING.md §9
""")
)

HANDOFF_NO_TRACE = (
    _BASE
    + textwrap.dedent("""\

    ## Escopo da AR_232

    PROOF (AR_232): tests/training/test_wellness.py::test_focus_total
""")
)

HANDOFF_SUPPRESSED = (
    _BASE
    + textwrap.dedent("""\

    ## Escopo da AR_232

    PROOF (AR_232): N/A (governance — sem mudança comportamental)
    TRACE (AR_232): N/A (governance)
""")
)

HANDOFF_NO_AR_IDS = textwrap.dedent("""\
    # ARQUITETO.md
    Protocolo: 1.3.0
    ## PRE-FLIGHT
    - git status
""")


# ---------------------------------------------------------------------------
# Testes: _parse_field
# ---------------------------------------------------------------------------

class TestParseField:
    def test_bold_field(self):
        block = "**PROOF (AR_232)**: tests/training/test_foo.py::test_bar"
        assert _parse_field(block, "PROOF") is not None

    def test_plain_field(self):
        block = "PROOF: tests/training/test_foo.py::test_bar"
        assert _parse_field(block, "PROOF") == "tests/training/test_foo.py::test_bar"

    def test_bullet_field(self):
        block = "* PROOF: tests/foo.py::test_bar"
        assert _parse_field(block, "PROOF") is not None

    def test_trace_field(self):
        block = "TRACE (AR_232): docs/path/file.md §9"
        val = _parse_field(block, "TRACE")
        assert val is not None
        assert "docs/" in val

    def test_field_absent(self):
        block = "Sem campos relevantes aqui."
        assert _parse_field(block, "PROOF") is None
        assert _parse_field(block, "TRACE") is None


# ---------------------------------------------------------------------------
# Testes: _is_suppressed
# ---------------------------------------------------------------------------

class TestIsSuppressed:
    def test_na_suppressed(self):
        assert _is_suppressed("N/A (governance)")

    def test_na_short(self):
        assert _is_suppressed("N/A")

    def test_governance_word(self):
        assert _is_suppressed("governance — sem mudança")

    def test_not_suppressed(self):
        assert not _is_suppressed("tests/training/test_foo.py::test_bar")

    def test_none_not_suppressed(self):
        assert not _is_suppressed(None)


# ---------------------------------------------------------------------------
# Testes: _extract_file_paths
# ---------------------------------------------------------------------------

class TestExtractFilePaths:
    def test_backtick_path(self):
        text = "docs alinha `docs/hbtrack/modulos/treinos/TEST_MATRIX_TRAINING.md` §9"
        paths = _extract_file_paths(text)
        assert "docs/hbtrack/modulos/treinos/TEST_MATRIX_TRAINING.md" in paths

    def test_bare_path(self):
        paths = _extract_file_paths("docs/path/to/file.md updated")
        assert "docs/path/to/file.md" in paths

    def test_no_paths(self):
        paths = _extract_file_paths("§9 §0 §10 PASS sem arquivo")
        assert paths == []

    def test_invalid_extension_ignored(self):
        paths = _extract_file_paths("docs/path/to/file §9")
        assert paths == []


# ---------------------------------------------------------------------------
# Testes: _validate_trace_files
# ---------------------------------------------------------------------------

class TestValidateTraceFiles:
    def test_existing_file(self, tmp_path: Path):
        (tmp_path / "docs").mkdir()
        (tmp_path / "docs" / "file.md").write_text("ok")
        existing, missing = _validate_trace_files("`docs/file.md` §0", tmp_path)
        assert "docs/file.md" in existing
        assert missing == []

    def test_missing_file(self, tmp_path: Path):
        existing, missing = _validate_trace_files("`docs/nonexistent.md`", tmp_path)
        assert "docs/nonexistent.md" in missing
        assert existing == []


# ---------------------------------------------------------------------------
# Testes: _check_ar
# ---------------------------------------------------------------------------

class TestCheckAr:
    def test_both_fields_present_no_warnings(self, tmp_path: Path):
        block = textwrap.dedent("""\
            PROOF (AR_232): tests/training/test_foo.py::test_bar
            TRACE (AR_232): N/A (governance)
        """)
        result = _check_ar("232", block, tmp_path)
        assert result.warns == []

    def test_missing_proof_generates_warn(self, tmp_path: Path):
        block = textwrap.dedent("""\
            TRACE (AR_232): N/A (governance)
        """)
        result = _check_ar("232", block, tmp_path)
        assert any("PROOF" in w for w in result.warns)

    def test_missing_trace_generates_warn(self, tmp_path: Path):
        block = "PROOF (AR_232): tests/foo.py::test_bar"
        result = _check_ar("232", block, tmp_path)
        assert any("TRACE" in w for w in result.warns)

    def test_trace_file_missing_on_disk(self, tmp_path: Path):
        block = textwrap.dedent("""\
            PROOF (AR_232): tests/foo.py::test_bar
            TRACE (AR_232): `docs/missing_file.md` §9
        """)
        result = _check_ar("232", block, tmp_path)
        assert any("inexistente" in w or "missing_file" in w for w in result.warns)

    def test_trace_file_exists_no_warn(self, tmp_path: Path):
        (tmp_path / "docs").mkdir()
        (tmp_path / "docs" / "real_file.md").write_text("content")
        block = textwrap.dedent("""\
            PROOF (AR_232): tests/foo.py::test_bar
            TRACE (AR_232): `docs/real_file.md` §9
        """)
        result = _check_ar("232", block, tmp_path)
        assert result.warns == []


# ---------------------------------------------------------------------------
# Testes: main() — exit codes e saída
# ---------------------------------------------------------------------------

def test_main_pass_full_handoff(tmp_path: Path):
    """Handoff com PROOF+TRACE explícitos → EXIT_PASS"""
    handoff = tmp_path / "ARQUITETO.md"
    handoff.write_text(HANDOFF_FULL, encoding="utf-8")
    assert main(["-", str(handoff), str(tmp_path)]) == EXIT_PASS


def test_main_pass_suppressed(tmp_path: Path):
    """Supressão N/A em ambos → EXIT_PASS, sem WARN relevante"""
    handoff = tmp_path / "ARQUITETO.md"
    handoff.write_text(HANDOFF_SUPPRESSED, encoding="utf-8")
    assert main(["-", str(handoff), str(tmp_path)]) == EXIT_PASS


def test_main_pass_even_with_warns(tmp_path: Path):
    """WARNs não mudam exit code — ainda EXIT_PASS."""
    handoff = tmp_path / "ARQUITETO.md"
    handoff.write_text(HANDOFF_NO_PROOF, encoding="utf-8")
    assert main(["-", str(handoff), str(tmp_path)]) == EXIT_PASS


def test_main_blocked_input_nonexistent(tmp_path: Path):
    """Handoff inexistente → EXIT_BLOCKED_INPUT."""
    assert main(["-", str(tmp_path / "NENHUM.md"), str(tmp_path)]) == EXIT_BLOCKED_INPUT


def test_main_warns_when_proof_absent(tmp_path: Path, capsys):
    """Handoff sem PROOF → saída contém ⚠️  WARN com AR_ID."""
    handoff = tmp_path / "ARQUITETO.md"
    handoff.write_text(HANDOFF_NO_PROOF, encoding="utf-8")
    main(["-", str(handoff), str(tmp_path)])
    captured = capsys.readouterr()
    assert "WARN" in captured.out
    assert "AR_232" in captured.out


def test_main_warns_when_trace_absent(tmp_path: Path, capsys):
    """Handoff sem TRACE → saída contém ⚠️  WARN com AR_ID."""
    handoff = tmp_path / "ARQUITETO.md"
    handoff.write_text(HANDOFF_NO_TRACE, encoding="utf-8")
    main(["-", str(handoff), str(tmp_path)])
    captured = capsys.readouterr()
    assert "WARN" in captured.out
    assert "AR_232" in captured.out


def test_main_no_warn_when_all_ok(tmp_path: Path, capsys):
    """Handoff completo sem arquivos TRACE para validar → sem WARN."""
    handoff = tmp_path / "ARQUITETO.md"
    handoff.write_text(HANDOFF_SUPPRESSED, encoding="utf-8")
    main(["-", str(handoff), str(tmp_path)])
    captured = capsys.readouterr()
    assert "WARN" not in captured.out
