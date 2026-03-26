from __future__ import annotations

import json
import pathlib
import sys


def _repo_root() -> pathlib.Path:
    here = pathlib.Path(__file__).resolve()
    for parent in here.parents:
        if (parent / ".git").exists():
            return parent
        if (parent / "contracts").exists() and (parent / ".contract_driven").exists():
            return parent
    return here.parents[3]


def main() -> int:
    root = _repo_root()
    scripts_dir = root / "scripts"
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
    from contracts.validate.validate_contracts import _g2j_pre_contract_evidence  # type: ignore

    result = _g2j_pre_contract_evidence(root)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result.get("status") in {"PASS", "SKIP_NOT_APPLICABLE", "DEGRADED"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
