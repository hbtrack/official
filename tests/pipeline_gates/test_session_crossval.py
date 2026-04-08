"""
Tests for cross-validation gate: session_start.json ↔ SESSION_HANDOFF.md
"""
import json
import pytest
from pathlib import Path

# Import the module under test
import importlib.util
GATE_PATH = Path(__file__).resolve().parent.parent.parent / "scripts" / "gates" / "check_session_crossval.py"
spec = importlib.util.spec_from_file_location("check_session_crossval", GATE_PATH)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class TestParseHandoffFrontmatter:
    def test_valid_frontmatter(self):
        text = """---
data_ultima_sessao: 2026-04-06
branch_ativo: main
modo_operacao: CDD
boot_profile_id: contract_execution
task_type: new_contract
modulo_foco: users
fase_roadmap: 5
---
# Body
"""
        result = mod.parse_handoff_frontmatter(text)
        assert result["branch_ativo"] == "main"
        assert result["modo_operacao"] == "CDD"
        assert result["boot_profile_id"] == "contract_execution"
        assert result["modulo_foco"] == "users"
        assert result["fase_roadmap"] == 5

    def test_no_frontmatter(self):
        result = mod.parse_handoff_frontmatter("# Just a heading\nNo frontmatter here")
        assert result == {}

    def test_empty_frontmatter(self):
        result = mod.parse_handoff_frontmatter("---\n---\n# Body")
        assert result == {}


class TestCrossValidate:
    def test_no_divergence(self):
        start = {
            "branch": "main",
            "boot_profile_id": "contract_execution",
            "task_type": "new_contract",
            "module": "users",
            "operation_mode": "CDD",
        }
        handoff = {
            "branch_ativo": "main",
            "boot_profile_id": "contract_execution",
            "task_type": "new_contract",
            "modulo_foco": "users",
            "modo_operacao": "CDD",
        }
        assert mod.cross_validate(start, handoff) == []

    def test_branch_divergence(self):
        start = {"branch": "feat/x"}
        handoff = {"branch_ativo": "main"}
        divs = mod.cross_validate(start, handoff)
        assert len(divs) == 1
        assert divs[0]["field"] == "Branch ativo"

    def test_mode_divergence(self):
        start = {"operation_mode": "CDD"}
        handoff = {"modo_operacao": "ROADMAP"}
        divs = mod.cross_validate(start, handoff)
        assert len(divs) == 1
        assert divs[0]["severity"] == "critical"

    def test_module_divergence(self):
        start = {"module": "users"}
        handoff = {"modulo_foco": "teams"}
        divs = mod.cross_validate(start, handoff)
        assert len(divs) == 1
        assert divs[0]["field"] == "Módulo foco"

    def test_multiple_divergences(self):
        start = {
            "branch": "feat/a",
            "task_type": "new_contract",
            "operation_mode": "CDD",
        }
        handoff = {
            "branch_ativo": "main",
            "task_type": "generate_code",
            "modo_operacao": "ROADMAP",
        }
        divs = mod.cross_validate(start, handoff)
        assert len(divs) == 3

    def test_missing_fields_no_divergence(self):
        """Fields missing from either side should not produce divergence."""
        start = {"branch": "main"}
        handoff = {"modo_operacao": "CDD"}
        assert mod.cross_validate(start, handoff) == []
