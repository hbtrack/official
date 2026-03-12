"""
GAP-C7 — testes do strict_merge (merger.py)

5 casos obrigatórios por especificação do plano operacional:
  1. merge básico         -> effective_execution_phases == constitution phases
  2. waiver merge         -> cannot_waive = global + extra, deduplicado
  3. sovereign block      -> MergeConflictError para cada campo soberano
  4. dedup waiver         -> entrada duplicada entre global e module -> apenas 1
  5. module vazio         -> merge ok sem module_waiver_policy.additional_cannot_waive
"""
import pytest

from hbtrack_lint.merger import strict_merge, MergeConflictError, SOVEREIGN_FIELDS


# ── fixtures ────────────────────────────────────────────────────────────────

def _make_constitution(extra_cannot_waive=None):
    return {
        "meta": {"version": "2.0.0", "authority": "sovereign"},
        "execution_phases": ["PRE_PLAN", "POST_PLAN", "POST_EXECUTION"],
        "exit_codes": {"0": "PASS", "1": "FAIL"},
        "skip_policy": {"missing_checker_impl": "SKIP"},
        "aggregation_policy": {"fail_closed": True},
        "merge_policy": {"sovereign_fields": list(SOVEREIGN_FIELDS)},
        "global_type_system": {"canonical_scalar_mappings": []},
        "rule_sets": {"cross_rules": [{"rule_id": "X-001"}]},
        "waiver_policy": {
            "cannot_waive": extra_cannot_waive if extra_cannot_waive is not None
            else ["X-001", "X-002", "X-003"],
        },
    }


def _make_module(additional_cannot_waive=None, **extra_fields):
    m = {
        "meta": {"module_id": "ATLETAS", "version": "1.0.0"},
        "module_id": "ATLETAS",
        "module_waiver_policy": {
            "additional_cannot_waive": additional_cannot_waive
            if additional_cannot_waive is not None
            else [],
        },
    }
    m.update(extra_fields)
    return m


# ── caso 1: merge básico ─────────────────────────────────────────────────────

def test_basic_merge():
    constitution = _make_constitution()
    module = _make_module()

    ruleset = strict_merge(constitution, module)

    assert ruleset["effective_execution_phases"] == ["PRE_PLAN", "POST_PLAN", "POST_EXECUTION"]
    assert ruleset["global_meta"]["authority"] == "sovereign"
    assert ruleset["module_meta"]["module_id"] == "ATLETAS"
    assert ruleset["effective_rule_sets"] == {"cross_rules": [{"rule_id": "X-001"}]}
    # effective_cannot_waive deve ser cópia independente (não alias)
    assert ruleset["effective_cannot_waive"] == ruleset["effective_waiver_policy"]["cannot_waive"]


# ── caso 2: waiver merge ─────────────────────────────────────────────────────

def test_waiver_merge():
    constitution = _make_constitution(extra_cannot_waive=["X-001", "X-002"])
    module = _make_module(additional_cannot_waive=["X-003", "X-004"])

    ruleset = strict_merge(constitution, module)

    eff = ruleset["effective_cannot_waive"]
    assert "X-001" in eff
    assert "X-002" in eff
    assert "X-003" in eff
    assert "X-004" in eff
    assert len(eff) == 4  # sem duplicatas


# ── caso 3: sovereign block ──────────────────────────────────────────────────

@pytest.mark.parametrize("field", list(SOVEREIGN_FIELDS))
def test_sovereign_block(field):
    constitution = _make_constitution()
    module = _make_module(**{field: []})

    with pytest.raises(MergeConflictError) as exc_info:
        strict_merge(constitution, module)

    assert field in str(exc_info.value)


# ── caso 4: dedup waiver ─────────────────────────────────────────────────────

def test_waiver_dedup():
    constitution = _make_constitution(extra_cannot_waive=["X-001", "X-002"])
    # X-001 já está no global; adicionar de novo no módulo deve resultar em apenas 1
    module = _make_module(additional_cannot_waive=["X-001", "X-005"])

    ruleset = strict_merge(constitution, module)

    eff = ruleset["effective_cannot_waive"]
    assert eff.count("X-001") == 1
    assert "X-002" in eff
    assert "X-005" in eff
    assert len(eff) == 3


# ── caso 5: module vazio ─────────────────────────────────────────────────────

def test_empty_module():
    """Merge funciona mesmo sem module_waiver_policy (campo ausente no módulo)."""
    constitution = _make_constitution(extra_cannot_waive=["X-001"])
    # módulo sem module_waiver_policy
    module = {
        "meta": {"module_id": "EMPTY"},
        "module_id": "EMPTY",
    }

    ruleset = strict_merge(constitution, module)

    assert ruleset["effective_cannot_waive"] == ["X-001"]
    assert ruleset["module_meta"]["module_id"] == "EMPTY"
