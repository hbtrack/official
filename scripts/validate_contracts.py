from __future__ import annotations

import pathlib
import runpy


def main() -> int:
    target = pathlib.Path(__file__).resolve().parent / "contracts" / "validate" / "validate_contracts.py"
    runpy.run_path(str(target), run_name="__main__")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

