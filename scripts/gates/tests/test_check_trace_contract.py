"""
tests/test_check_trace_contract.py
Unit tests para scripts/gates/check_trace_contract.py  (DOC-GATE-020)

Cobertura: heurística AR-centric (2 níveis), supressão explícita, exit codes.
"""
from __future__ import annotations

import sys
import textwrap
from pathlib import Path

import pytest

# Adicionar scripts/gates ao path para importação direta
GATES_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(GATES_DIR))

from check_trace_contract import (  # noqa: E402
    EXIT_BLOCKED_INPUT,
    EXIT_PASS,
    _check_trace_warns,
    _has_behavioral_signals,
    _has_trace_link,
    _has_trace_suppression,
    main,
)

# ---------------------------------------------------------------------------
# Fixtures de texto
# ---------------------------------------------------------------------------

_BASE = textwrap.dedent("""\
    # ARQUITETO.md — HB Track
    Protocolo: 1.3.0
    AR IDs: [232]
    ## PRE-FLIGHT
    - git diff --name-only
    ## STOP CONDITIONS
    - BLOCKED_INPUT exit 4
""")

HANDOFF_BEHAVIORAL_NO_TRACE = _BASE + "\npython scripts/run/hb_cli.py report 232\npytest tests/training/\n"

HANDOFF_BEHAVIORAL_WITH_TRACE = (
    _BASE
    + "\npytest tests/training/\n"
    + "**TRACE:** `docs/hbtrack/modulos/treinos/TEST_MATRIX_TRAINING.md` §9\n"
)

HANDOFF_BEHAVIORAL_TRACE_NA = (
    _BASE
    + "\nendpoint /training/sessions\n"
    + "**TRACE:** N/A (governance — sem mudança comportamental)\n"
)

HANDOFF_NO_AR_IDS = textwrap.dedent("""\
    # ARQUITETO.md — sem AR IDs
    pytest tests/
    schema.sql alterado
""")

HANDOFF_NO_BEHAVIORAL = textwrap.dedent("""\
    # ARQUITETO.md
    Protocolo: 1.3.0
    AR IDs: [232]
    ## Bump de versão
    Atualizar comentário no cabeçalho do ROADMAP.md.
""")

HANDOFF_SCHEMA_NO_TRACE = _BASE + "\nAlteração no schema.sql do banco.\n"

HANDOFF_GOVERNANCE_CLASS = (
    _BASE
    + "\nschema.sql atualizado\n"
    + "CLASS: GOVERNANCE_ONLY\n"
)

HANDOFF_TEST_MATRIX_LINK = _BASE + "\npytest\nTEST_MATRIX_TRAINING.md atualizado em §9\n"

HANDOFF_CONTRACT_MD_LINK = _BASE + "\ncontract alterado\nDocs em TRAINING_FRONT_BACK_CONTRACT.md\n"


# ---------------------------------------------------------------------------
# Testes: helpers internos
# ---------------------------------------------------------------------------

def test_has_behavioral_signals_pytest():
    assert _has_behavioral_signals("pytest tests/training/")


def test_has_behavioral_signals_schema():
    assert _has_behavioral_signals("Alterar schema.sql")


def test_has_behavioral_signals_endpoint():
    assert _has_behavioral_signals("endpoint /training/sessions")


def test_has_behavioral_signals_false_governance():
    assert not _has_behavioral_signals("Bump de versão no ROADMAP.md.")


def test_has_trace_suppression_na():
    assert _has_trace_suppression("TRACE: N/A (governance)")


def test_has_trace_suppression_governance_class():
    assert _has_trace_suppression("CLASS: GOVERNANCE_ONLY")


def test_has_trace_suppression_false():
    assert not _has_trace_suppression("pytest tests/")


def test_has_trace_link_test_matrix():
    assert _has_trace_link("TEST_MATRIX_TRAINING.md §9")


def test_has_trace_link_trace_field():
    assert _has_trace_link("TRACE: docs/hbtrack/modulos/treinos/TEST_MATRIX_TRAINING.md")


def test_has_trace_link_contract_md():
    assert _has_trace_link("ver TRAINING_FRONT_BACK_CONTRACT.md")


def test_has_trace_link_false():
    assert not _has_trace_link("pytest tests/training/")


# ---------------------------------------------------------------------------
# Testes: _check_trace_warns (heurística completa)
# ---------------------------------------------------------------------------

def test_warn_behavioral_no_trace():
    """AR com pytest e sem TRACE link → WARN emitido."""
    warns = _check_trace_warns(HANDOFF_BEHAVIORAL_NO_TRACE)
    assert len(warns) == 1
    assert "TRACE ausente" in warns[0]


def test_no_warn_trace_field_present():
    """AR com pytest + TRACE: preenchido → sem WARN."""
    warns = _check_trace_warns(HANDOFF_BEHAVIORAL_WITH_TRACE)
    assert warns == []


def test_no_warn_suppression_na():
    """Supressão explícita TRACE: N/A → sem WARN."""
    warns = _check_trace_warns(HANDOFF_BEHAVIORAL_TRACE_NA)
    assert warns == []


def test_no_warn_suppression_governance_class():
    """CLASS: GOVERNANCE_ONLY suprime o gate."""
    warns = _check_trace_warns(HANDOFF_GOVERNANCE_CLASS)
    assert warns == []


def test_no_warn_no_ar_ids():
    """Sem AR IDs → não avaliável → sem WARN."""
    warns = _check_trace_warns(HANDOFF_NO_AR_IDS)
    assert warns == []


def test_no_warn_no_behavioral_signals():
    """AR puramente documental (sem sinais comportamentais) → sem WARN."""
    warns = _check_trace_warns(HANDOFF_NO_BEHAVIORAL)
    assert warns == []


def test_warn_schema_signal():
    """schema.sql sem TRACE link → WARN."""
    warns = _check_trace_warns(HANDOFF_SCHEMA_NO_TRACE)
    assert len(warns) == 1
    assert "TRACE ausente" in warns[0]


def test_no_warn_test_matrix_link():
    """TEST_MATRIX no texto satisfaz trace link."""
    warns = _check_trace_warns(HANDOFF_TEST_MATRIX_LINK)
    assert warns == []


def test_no_warn_contract_md_link():
    """Referência a _CONTRACT.md satisfaz trace link."""
    warns = _check_trace_wants = _check_trace_warns(HANDOFF_CONTRACT_MD_LINK)
    assert warns == []


def test_warn_message_contains_ar_id():
    """WARN deve mencionar o AR ID detectado."""
    warns = _check_trace_warns(HANDOFF_BEHAVIORAL_NO_TRACE)
    assert "AR_232" in warns[0]


# ---------------------------------------------------------------------------
# Testes: main() — exit codes
# ---------------------------------------------------------------------------

def test_exit_pass_with_warn(tmp_path: Path):
    """WARN não muda exit code — deve retornar EXIT_PASS."""
    handoff = tmp_path / "ARQUITETO.md"
    handoff.write_text(HANDOFF_BEHAVIORAL_NO_TRACE, encoding="utf-8")
    assert main(["-", str(handoff)]) == EXIT_PASS


def test_exit_pass_no_warn(tmp_path: Path):
    """Handoff completo com TRACE → EXIT_PASS sem WARN."""
    handoff = tmp_path / "ARQUITETO.md"
    handoff.write_text(HANDOFF_BEHAVIORAL_WITH_TRACE, encoding="utf-8")
    assert main(["-", str(handoff)]) == EXIT_PASS


def test_exit_blocked_input_file_not_found(tmp_path: Path):
    """Handoff inexistente → EXIT_BLOCKED_INPUT (exit 4)."""
    nonexistent = tmp_path / "NENHUM.md"
    assert main(["-", str(nonexistent)]) == EXIT_BLOCKED_INPUT


def test_exit_pass_suppression_na(tmp_path: Path):
    """Supressão explícita + sinais comportamentais → EXIT_PASS, sem WARN."""
    handoff = tmp_path / "ARQUITETO.md"
    handoff.write_text(HANDOFF_BEHAVIORAL_TRACE_NA, encoding="utf-8")
    assert main(["-", str(handoff)]) == EXIT_PASS


# ---------------------------------------------------------------------------
# Testes: per-AR TRACE check (D-07)
# ---------------------------------------------------------------------------

_TWO_ARS_ONE_WITH_TRACE = textwrap.dedent("""\
    # ARQUITETO.md
    Protocolo: 1.3.0
    AR IDs: [232, 233]
    ## PRE-FLIGHT
    - git diff --name-only
    ## STOP CONDITIONS
    - BLOCKED_INPUT exit 4

    ## Escopo da AR_232

    pytest tests/training/
    TRACE (AR_232): docs/hbtrack/modulos/treinos/TEST_MATRIX_TRAINING.md §9

    ## Escopo da AR_233

    endpoint /cors/settings alterado — schema.sql não tocado
""")

_TWO_ARS_PER_AR_SUPPRESSION = textwrap.dedent("""\
    # ARQUITETO.md
    Protocolo: 1.3.0
    AR IDs: [232, 233]
    ## PRE-FLIGHT
    - git diff --name-only
    ## STOP CONDITIONS
    - BLOCKED_INPUT exit 4

    ## Escopo da AR_232

    endpoint /cors/settings — TRACE: N/A (governance — sem spec nova)

    ## Escopo da AR_233

    endpoint /teams/wellness — TRACE: N/A (governance)
""")


def test_warn_trace_per_ar_only_missing():
    """AR_232 tem TRACE → sem WARN; AR_233 tem sinais comportamentais e sem trace → WARN para AR_233."""
    warns = _check_trace_warns(_TWO_ARS_ONE_WITH_TRACE)
    assert len(warns) == 1, f"Esperado 1 WARN, obteve {len(warns)}: {warns}"
    assert "AR_233" in warns[0]
    assert "AR_232" not in warns[0]


def test_no_warn_trace_per_ar_suppressed_in_block():
    """Supressão TRACE: N/A por bloco de AR → sem WARN mesmo com endpoint."""
    warns = _check_trace_warns(_TWO_ARS_PER_AR_SUPPRESSION)
    assert warns == [], f"WARN inesperado: {warns}"


def test_warn_trace_per_ar_fallback_when_no_heading():
    """Sem heading, usa handoff inteiro como fallback.
    pytest + TEST_MATRIX no handoff → trace link presente → sem WARN."""
    text = textwrap.dedent("""\
        Protocolo: 1.3.0
        AR IDs: [500]
        endpoint /test
        TEST_MATRIX_TRAINING.md §9 atualizado
    """)
    warns = _check_trace_warns(text)
    assert warns == [], f"WARN inesperado: {warns}"
