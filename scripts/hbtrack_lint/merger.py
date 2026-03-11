"""merger.py -- strict merge ENGINE_CONSTITUTION + module_rules -> runtime_ruleset."""
from __future__ import annotations

import copy
from typing import Any

SOVEREIGN_FIELDS = frozenset([
    "execution_phases",
    "exit_codes",
    "skip_policy",
    "aggregation_policy",
    "merge_policy",
    "global_type_system",
    "rule_sets",
])


class MergeConflictError(Exception):
    """Raised when module attempts to redefine a sovereign field."""


def strict_merge(constitution: dict, module_rules: dict) -> dict:
    """Produz runtime_ruleset. Nunca permite override de campos soberanos."""
    for field in SOVEREIGN_FIELDS:
        if field in module_rules:
            raise MergeConflictError(
                f"Module '{module_rules.get('module_id', '?')}' "
                f"cannot redefine sovereign field '{field}'"
            )
    _eff_waiver = _merge_waiver(
        constitution.get("waiver_policy", {}),
        module_rules.get("module_waiver_policy", {}),
    )
    return {
        "global_meta": copy.deepcopy(constitution.get("meta", {})),
        "module_meta": copy.deepcopy(module_rules.get("meta", {})),
        "effective_execution_phases": copy.deepcopy(
            constitution.get("execution_phases", [])
        ),
        "effective_waiver_policy": _eff_waiver,
        # campo explícito para acesso direto sem subfiltro de dict (Ajuste 3)
        "effective_cannot_waive": _eff_waiver["cannot_waive"],
        "effective_type_system": copy.deepcopy(
            constitution.get("global_type_system", {})
        ),
        # effective_rule_sets contém as 89 regras migradas (Opção A, fixada em B1)
        "effective_rule_sets": copy.deepcopy(constitution.get("rule_sets", {})),
    }


def _merge_waiver(global_waiver: dict, module_waiver: dict) -> dict:
    base = list(global_waiver.get("cannot_waive", []))
    extra = list(module_waiver.get("additional_cannot_waive", []))
    # dict.fromkeys preserva ordem e deduplica
    return {"cannot_waive": list(dict.fromkeys(base + extra))}
